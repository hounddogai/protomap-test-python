"""Transactional storage of datahub records and audit entries."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker

from acme.datahub.v1 import datahub_pb2 as datahub_v1_datahub_pb2

from acme_data.platform.persistence import Repository


class DomainRepository(Repository):
    def __init__(self, sessions: async_sessionmaker[AsyncSession]) -> None:
        super().__init__('datahub', sessions)

    async def save_data_share(self, tenant: str, record: datahub_v1_datahub_pb2.DataShare) -> None:
        await self.save(tenant, 'DataShare', record.data_share_id,
                        record.SerializeToString(deterministic=True))

    async def save_notebook(self, tenant: str, record: datahub_v1_datahub_pb2.Notebook) -> None:
        await self.save(tenant, 'Notebook', record.notebook_id,
                        record.SerializeToString(deterministic=True))

    async def save_workspace(self, tenant: str, record: datahub_v1_datahub_pb2.Workspace) -> None:
        await self.save(tenant, 'Workspace', record.workspace_id,
                        record.SerializeToString(deterministic=True))
