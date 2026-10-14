"""Transactional storage of datasets records and audit entries."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker

from acme.datasets.v1 import datasets_pb2 as datasets_v1_datasets_pb2

from acme_data.platform.persistence import Repository


class DomainRepository(Repository):
    def __init__(self, sessions: async_sessionmaker[AsyncSession]) -> None:
        super().__init__('datasets', sessions)

    async def save_data_schema(self, tenant: str, record: datasets_v1_datasets_pb2.DataSchema) -> None:
        await self.save(tenant, 'DataSchema', record.data_schema_id,
                        record.SerializeToString(deterministic=True))

    async def save_dataset(self, tenant: str, record: datasets_v1_datasets_pb2.Dataset) -> None:
        await self.save(tenant, 'Dataset', record.dataset_id,
                        record.SerializeToString(deterministic=True))

    async def save_dataset_version(self, tenant: str, record: datasets_v1_datasets_pb2.DatasetVersion) -> None:
        await self.save(tenant, 'DatasetVersion', record.dataset_version_id,
                        record.SerializeToString(deterministic=True))
