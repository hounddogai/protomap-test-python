"""Providers own resource lifetimes; domain modules receive explicit constructor dependencies."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Generic, TypeVar, cast

import grpc
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from acme_data.platform.config import Settings
from acme_data.platform.events import EventBus
from acme_data.platform.persistence import Base

T = TypeVar("T")


@dataclass(slots=True)
class Factory(Generic[T]):
    build: Callable[[], T]

    def __call__(self) -> T:
        return self.build()


class Container:
    def __init__(self, settings: Settings, channel: grpc.aio.Channel) -> None:
        self.settings = settings
        self.channel = channel
        self.engine = create_async_engine(settings.database_url)
        self.sessions = async_sessionmaker(self.engine, expire_on_commit=False)
        self.bus = EventBus(settings.event_capacity)
        self.singletons: dict[type[object], object] = {}

    def singleton(self, kind: type[T], factory: Callable[[], T]) -> T:
        if kind not in self.singletons:
            self.singletons[kind] = factory()
        return cast(T, self.singletons[kind])

    async def initialize(self) -> None:
        async with self.engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)

    async def close(self) -> None:
        await self.engine.dispose()
