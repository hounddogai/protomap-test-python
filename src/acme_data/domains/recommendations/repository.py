"""Transactional storage of recommendations records and audit entries."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker

from acme.recommendations.v1 import recommendations_pb2 as recommendations_v1_recommendations_pb2

from acme_data.platform.persistence import Repository


class DomainRepository(Repository):
    def __init__(self, sessions: async_sessionmaker[AsyncSession]) -> None:
        super().__init__('recommendations', sessions)

    async def save_interaction(self, tenant: str, record: recommendations_v1_recommendations_pb2.Interaction) -> None:
        await self.save(tenant, 'Interaction', record.interaction_id,
                        record.SerializeToString(deterministic=True))

    async def save_recommendation_model(
        self,
        tenant: str,
        record: recommendations_v1_recommendations_pb2.RecommendationModel
    ) -> None:
        await self.save(tenant, 'RecommendationModel', record.recommendation_model_id,
                        record.SerializeToString(deterministic=True))

    async def save_recommendation_set(
        self,
        tenant: str,
        record: recommendations_v1_recommendations_pb2.RecommendationSet
    ) -> None:
        await self.save(tenant, 'RecommendationSet', record.recommendation_set_id,
                        record.SerializeToString(deterministic=True))
