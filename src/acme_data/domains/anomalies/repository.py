"""Transactional storage of anomalies records and audit entries."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker

from acme.anomalies.v1 import anomalies_pb2 as anomalies_v1_anomalies_pb2

from acme_data.platform.persistence import Repository


class DomainRepository(Repository):
    def __init__(self, sessions: async_sessionmaker[AsyncSession]) -> None:
        super().__init__('anomalies', sessions)

    async def save_anomaly(self, tenant: str, record: anomalies_v1_anomalies_pb2.Anomaly) -> None:
        await self.save(tenant, 'Anomaly', record.anomaly_id,
                        record.SerializeToString(deterministic=True))

    async def save_anomaly_feedback(self, tenant: str, record: anomalies_v1_anomalies_pb2.AnomalyFeedback) -> None:
        await self.save(tenant, 'AnomalyFeedback', record.anomaly_feedback_id,
                        record.SerializeToString(deterministic=True))

    async def save_detector(self, tenant: str, record: anomalies_v1_anomalies_pb2.Detector) -> None:
        await self.save(tenant, 'Detector', record.detector_id,
                        record.SerializeToString(deterministic=True))
