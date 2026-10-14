"""SQLAlchemy transaction boundaries for audit records and domain snapshots."""

from __future__ import annotations

import json

from sqlalchemy import Integer, LargeBinary, String, Text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class AuditRecord(Base):
    __tablename__ = "rpc_audit"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    domain: Mapped[str] = mapped_column(String(80), index=True)
    tenant: Mapped[str] = mapped_column(String(120), index=True)
    operation: Mapped[str] = mapped_column(String(200))
    details: Mapped[str] = mapped_column(Text)


class Snapshot(Base):
    __tablename__ = "domain_snapshot"
    domain: Mapped[str] = mapped_column(String(80), primary_key=True)
    tenant: Mapped[str] = mapped_column(String(120), primary_key=True)
    entity: Mapped[str] = mapped_column(String(160), primary_key=True)
    record_id: Mapped[str] = mapped_column(String(200), primary_key=True)
    payload: Mapped[bytes] = mapped_column(LargeBinary)


class Repository:
    def __init__(self, domain: str, sessions: async_sessionmaker[AsyncSession]) -> None:
        self.domain = domain
        self.sessions = sessions

    async def audit(self, tenant: str, operation: str, details: dict[str, object]) -> None:
        async with self.sessions.begin() as session:
            session.add(AuditRecord(domain=self.domain, tenant=tenant, operation=operation,
                                    details=json.dumps(details, sort_keys=True, default=str)))

    async def save(self, tenant: str, entity: str, record_id: str, payload: bytes) -> None:
        async with self.sessions.begin() as session:
            await session.merge(Snapshot(domain=self.domain, tenant=tenant, entity=entity,
                                         record_id=record_id, payload=payload))
