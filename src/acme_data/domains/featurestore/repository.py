"""Transactional storage of featurestore records and audit entries."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker

from acme.featurestore.v1 import featurestore_pb2 as featurestore_v1_featurestore_pb2

from acme_data.platform.persistence import Repository


class DomainRepository(Repository):
    def __init__(self, sessions: async_sessionmaker[AsyncSession]) -> None:
        super().__init__('featurestore', sessions)

    async def save_entity(self, tenant: str, record: featurestore_v1_featurestore_pb2.Entity) -> None:
        await self.save(tenant, 'Entity', record.entity_id,
                        record.SerializeToString(deterministic=True))

    async def save_feature_value(self, tenant: str, record: featurestore_v1_featurestore_pb2.FeatureValue) -> None:
        await self.save(tenant, 'FeatureValue', record.feature_value_id,
                        record.SerializeToString(deterministic=True))

    async def save_feature_view(self, tenant: str, record: featurestore_v1_featurestore_pb2.FeatureView) -> None:
        await self.save(tenant, 'FeatureView', record.feature_view_id,
                        record.SerializeToString(deterministic=True))
