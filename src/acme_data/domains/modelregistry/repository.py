"""Transactional storage of modelregistry records and audit entries."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker

from acme.modelregistry.v1 import modelregistry_pb2 as modelregistry_v1_modelregistry_pb2

from acme_data.platform.persistence import Repository


class DomainRepository(Repository):
    def __init__(self, sessions: async_sessionmaker[AsyncSession]) -> None:
        super().__init__('modelregistry', sessions)

    async def save_deployment(self, tenant: str, record: modelregistry_v1_modelregistry_pb2.Deployment) -> None:
        await self.save(tenant, 'Deployment', record.deployment_id,
                        record.SerializeToString(deterministic=True))

    async def save_model_version(self, tenant: str, record: modelregistry_v1_modelregistry_pb2.ModelVersion) -> None:
        await self.save(tenant, 'ModelVersion', record.model_version_id,
                        record.SerializeToString(deterministic=True))

    async def save_registered_model(
        self,
        tenant: str,
        record: modelregistry_v1_modelregistry_pb2.RegisteredModel
    ) -> None:
        await self.save(tenant, 'RegisteredModel', record.registered_model_id,
                        record.SerializeToString(deterministic=True))
