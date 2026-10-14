"""An in-process request/reply bus whose consumer owns the downstream RPC of each delivery."""

from __future__ import annotations

import asyncio
import contextvars
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field

from google.protobuf.message import Message


@dataclass(slots=True)
class Delivery:
    topic: str
    payload: Message
    reply: asyncio.Future[Message]
    # The context of the request, whose credentials the delivery's downstream RPC carries.
    context: contextvars.Context = field(default_factory=contextvars.copy_context)


class EventBus:
    def __init__(self, capacity: int) -> None:
        self.queue: asyncio.Queue[Delivery] = asyncio.Queue(maxsize=capacity)
        self.handlers: dict[str, Callable[[Message], Awaitable[Message]]] = {}
        self.running: set[asyncio.Task[None]] = set()

    def subscribe(self, topic: str, handler: Callable[[Message], Awaitable[Message]]) -> None:
        if topic in self.handlers:
            raise ValueError(f"duplicate event subscription: {topic}")
        self.handlers[topic] = handler

    async def request(self, topic: str, payload: Message, timeout: float) -> Message:
        snapshot = type(payload)()
        snapshot.CopyFrom(payload)
        reply: asyncio.Future[Message] = asyncio.get_running_loop().create_future()
        try:
            async with asyncio.timeout(timeout):
                await self.queue.put(Delivery(topic, snapshot, reply))
                return await reply
        finally:
            if not reply.done():
                reply.cancel()

    async def consume(self) -> None:
        # Each delivery runs on a task of its own: a delivery's RPC may reach a handler that makes a request of the
        # bus in turn, which would otherwise wait behind the delivery that waits for it.
        try:
            while True:
                delivery = await self.queue.get()
                task = asyncio.create_task(self.deliver(delivery), context=delivery.context)
                self.running.add(task)
                task.add_done_callback(self.running.discard)
        finally:
            running = list(self.running)
            for task in running:
                task.cancel()
            await asyncio.gather(*running, return_exceptions=True)

    async def deliver(self, delivery: Delivery) -> None:
        try:
            if delivery.reply.cancelled():
                return
            response = await self.handlers[delivery.topic](delivery.payload)
            if not delivery.reply.done():
                delivery.reply.set_result(response)
        except asyncio.CancelledError:
            if not delivery.reply.done():
                delivery.reply.cancel()
            raise
        except Exception as error:
            if not delivery.reply.done():
                delivery.reply.set_exception(error)
        finally:
            self.queue.task_done()
