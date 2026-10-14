"""Transactional storage of metrics records and audit entries."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker

from acme.metrics.v1 import metrics_pb2 as metrics_v1_metrics_pb2

from acme_data.platform.persistence import Repository


class DomainRepository(Repository):
    def __init__(self, sessions: async_sessionmaker[AsyncSession]) -> None:
        super().__init__('metrics', sessions)

    async def save_dashboard(self, tenant: str, record: metrics_v1_metrics_pb2.Dashboard) -> None:
        await self.save(tenant, 'Dashboard', record.dashboard_id,
                        record.SerializeToString(deterministic=True))

    async def save_metric_alert(self, tenant: str, record: metrics_v1_metrics_pb2.MetricAlert) -> None:
        await self.save(tenant, 'MetricAlert', record.metric_alert_id,
                        record.SerializeToString(deterministic=True))

    async def save_metric_series(self, tenant: str, record: metrics_v1_metrics_pb2.MetricSeries) -> None:
        await self.save(tenant, 'MetricSeries', record.metric_series_id,
                        record.SerializeToString(deterministic=True))
