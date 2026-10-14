"""Environment configuration, loaded once at the composition root."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Settings:
    listen: str = "127.0.0.1:8040"
    mesh: str = "127.0.0.1:15001"
    database_url: str = "sqlite+aiosqlite:///db.sqlite3"
    timeout: float = 5.0
    event_capacity: int = 256
    # The workload credential this server makes its own calls with, such as its identity lookups.
    service_token: str = ""

    @classmethod
    def from_environment(cls) -> Settings:
        settings = cls(
            listen=os.environ.get("ACME_LISTEN", "127.0.0.1:8040"),
            mesh=os.environ.get("ACME_MESH", "127.0.0.1:15001"),
            database_url=os.environ.get("ACME_DATABASE_URL", "sqlite+aiosqlite:///db.sqlite3"),
            timeout=float(os.environ.get("ACME_RPC_TIMEOUT", "5")),
            event_capacity=int(os.environ.get("ACME_EVENT_CAPACITY", "256")),
            service_token=os.environ.get("ACME_SERVICE_TOKEN", ""),
        )
        if settings.timeout <= 0 or settings.event_capacity <= 0:
            raise ValueError("RPC timeout and event capacity must be positive")
        return settings
