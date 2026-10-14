"""Transactional storage of lineage records and audit entries."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker

from acme.lineage.v1 import lineage_pb2 as lineage_v1_lineage_pb2

from acme_data.platform.persistence import Repository


class DomainRepository(Repository):
    def __init__(self, sessions: async_sessionmaker[AsyncSession]) -> None:
        super().__init__('lineage', sessions)

    async def save_impact(self, tenant: str, record: lineage_v1_lineage_pb2.Impact) -> None:
        await self.save(tenant, 'Impact', record.impact_id,
                        record.SerializeToString(deterministic=True))

    async def save_lineage_edge(self, tenant: str, record: lineage_v1_lineage_pb2.LineageEdge) -> None:
        await self.save(tenant, 'LineageEdge', record.lineage_edge_id,
                        record.SerializeToString(deterministic=True))

    async def save_lineage_node(self, tenant: str, record: lineage_v1_lineage_pb2.LineageNode) -> None:
        await self.save(tenant, 'LineageNode', record.lineage_node_id,
                        record.SerializeToString(deterministic=True))
