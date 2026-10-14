"""Transactional storage of pipelines records and audit entries."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker

from acme.pipelines.v1 import pipelines_pb2 as pipelines_v1_pipelines_pb2

from acme_data.platform.persistence import Repository


class DomainRepository(Repository):
    def __init__(self, sessions: async_sessionmaker[AsyncSession]) -> None:
        super().__init__('pipelines', sessions)

    async def save_pipeline(self, tenant: str, record: pipelines_v1_pipelines_pb2.Pipeline) -> None:
        await self.save(tenant, 'Pipeline', record.pipeline_id,
                        record.SerializeToString(deterministic=True))

    async def save_pipeline_run(self, tenant: str, record: pipelines_v1_pipelines_pb2.PipelineRun) -> None:
        await self.save(tenant, 'PipelineRun', record.pipeline_run_id,
                        record.SerializeToString(deterministic=True))

    async def save_pipeline_step(self, tenant: str, record: pipelines_v1_pipelines_pb2.PipelineStep) -> None:
        await self.save(tenant, 'PipelineStep', record.pipeline_step_id,
                        record.SerializeToString(deterministic=True))
