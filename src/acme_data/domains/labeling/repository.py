"""Transactional storage of labeling records and audit entries."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker

from acme.labeling.v1 import labeling_pb2 as labeling_v1_labeling_pb2

from acme_data.platform.persistence import Repository


class DomainRepository(Repository):
    def __init__(self, sessions: async_sessionmaker[AsyncSession]) -> None:
        super().__init__('labeling', sessions)

    async def save_annotation(self, tenant: str, record: labeling_v1_labeling_pb2.Annotation) -> None:
        await self.save(tenant, 'Annotation', record.annotation_id,
                        record.SerializeToString(deterministic=True))

    async def save_label_set(self, tenant: str, record: labeling_v1_labeling_pb2.LabelSet) -> None:
        await self.save(tenant, 'LabelSet', record.label_set_id,
                        record.SerializeToString(deterministic=True))

    async def save_labeling_task(self, tenant: str, record: labeling_v1_labeling_pb2.LabelingTask) -> None:
        await self.save(tenant, 'LabelingTask', record.labeling_task_id,
                        record.SerializeToString(deterministic=True))
