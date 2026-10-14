"""Deadlines, retry policy, streaming adapters, and status translation for async handlers."""

from __future__ import annotations

import asyncio
import logging
from collections.abc import AsyncIterator, Awaitable, Callable, Iterable, Iterator
from functools import wraps
from typing import Any, ParamSpec, TypeVar, cast

import grpc
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

P = ParamSpec("P")
T = TypeVar("T")
log = logging.getLogger(__name__)


def retry_transient(function: Callable[P, Awaitable[T]]) -> Callable[P, Awaitable[T]]:
    """Retry idempotent read handlers only; a stream cannot restart after yielding a response."""
    @wraps(function)
    async def wrapped(*args: P.args, **kwargs: P.kwargs) -> T:
        for attempt in range(3):
            try:
                return await function(*args, **kwargs)
            except grpc.aio.AioRpcError as error:
                if attempt == 2 or error.code() not in (grpc.StatusCode.UNAVAILABLE, grpc.StatusCode.ABORTED):
                    raise
                await asyncio.sleep(0.01 * (2 ** attempt))
        raise RuntimeError("retry budget exhausted")
    return wrapped


async def abort_error(context: Any, error: Exception) -> None:
    if isinstance(error, ValueError):
        await context.abort(grpc.StatusCode.INVALID_ARGUMENT, str(error))
    elif isinstance(error, IntegrityError):
        await context.abort(grpc.StatusCode.ALREADY_EXISTS, "record already exists")
    elif isinstance(error, grpc.aio.AioRpcError):
        await context.abort(error.code(), error.details() or "downstream RPC failed")
    elif isinstance(error, SQLAlchemyError):
        log.exception("repository operation failed")
        await context.abort(grpc.StatusCode.INTERNAL, "repository operation failed")
    else:
        log.exception("handler failed")
        await context.abort(grpc.StatusCode.INTERNAL, "internal error")


def rpc_errors(function: Callable[P, Awaitable[T]]) -> Callable[P, Awaitable[T]]:
    @wraps(function)
    async def wrapped(*args: P.args, **kwargs: P.kwargs) -> T:
        try:
            return await function(*args, **kwargs)
        except Exception as error:
            await abort_error(args[-1], error)
            raise
    return wrapped


def stream_errors(function: Callable[P, AsyncIterator[T]]) -> Callable[P, AsyncIterator[T]]:
    @wraps(function)
    async def wrapped(*args: P.args, **kwargs: P.kwargs) -> AsyncIterator[T]:
        try:
            async for response in function(*args, **kwargs):
                yield response
        except Exception as error:
            await abort_error(args[-1], error)
            raise
    return wrapped


def messages(values: Iterable[T]) -> Iterator[T]:
    yield from values


async def async_messages(values: Iterable[T]) -> AsyncIterator[T]:
    for value in values:
        await asyncio.sleep(0)
        yield value


async def run_steps(steps: Iterable[Callable[[], Awaitable[T]]]) -> list[T]:
    results = []
    for step in steps:
        results.append(await step())
    return results


def typed_callback(value: object) -> Callable[..., Awaitable[Any]]:
    if not callable(value):
        raise TypeError("registered callback is not callable")
    return cast(Callable[..., Awaitable[Any]], value)
