"""Transactional storage of analytics records and audit entries."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker

from acme.analytics.v1 import analytics_pb2 as analytics_v1_analytics_pb2

from acme_data.platform.persistence import Repository


class DomainRepository(Repository):
    def __init__(self, sessions: async_sessionmaker[AsyncSession]) -> None:
        super().__init__('analytics', sessions)

    async def save_analytics_event(self, tenant: str, record: analytics_v1_analytics_pb2.AnalyticsEvent) -> None:
        await self.save(tenant, 'AnalyticsEvent', record.analytics_event_id,
                        record.SerializeToString(deterministic=True))

    async def save_analytics_report(self, tenant: str, record: analytics_v1_analytics_pb2.AnalyticsReport) -> None:
        await self.save(tenant, 'AnalyticsReport', record.analytics_report_id,
                        record.SerializeToString(deterministic=True))

    async def save_cohort(self, tenant: str, record: analytics_v1_analytics_pb2.Cohort) -> None:
        await self.save(tenant, 'Cohort', record.cohort_id,
                        record.SerializeToString(deterministic=True))

    async def save_funnel(self, tenant: str, record: analytics_v1_analytics_pb2.Funnel) -> None:
        await self.save(tenant, 'Funnel', record.funnel_id,
                        record.SerializeToString(deterministic=True))
