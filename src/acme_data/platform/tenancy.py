"""Task-local tenant context, including child tasks started by asyncio.gather."""

from collections.abc import Iterator
from contextlib import contextmanager
from contextvars import ContextVar

tenant_id: ContextVar[str] = ContextVar("tenant_id", default="")


@contextmanager
def tenant_scope(value: str) -> Iterator[None]:
    if not value.strip():
        raise ValueError("context.tenant_id is required")
    token = tenant_id.set(value)
    try:
        yield
    finally:
        tenant_id.reset(token)
