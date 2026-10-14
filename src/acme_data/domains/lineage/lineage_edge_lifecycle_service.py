"""Moves a lineage edge between the states of its lifecycle."""

from __future__ import annotations

from collections.abc import AsyncIterator

import grpc

from acme.lineage.v1 import lineage_edge_lifecycle_service_pb2 as lineage_v1_lineage_edge_lifecycle_service_pb2
from acme.lineage.v1 import (
    lineage_edge_lifecycle_service_pb2_grpc as lineage_v1_lineage_edge_lifecycle_service_pb2_grpc,
)

from acme_data.domains.lineage.dependencies import Dependencies
from acme_data.domains.lineage.lineage_edge_lifecycle_service_workflow import LineageEdgeLifecycleServicerWorkflow
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors


class LineageEdgeLifecycleServicer(
    lineage_v1_lineage_edge_lifecycle_service_pb2_grpc.LineageEdgeLifecycleServiceServicer
):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps
        self.workflow = LineageEdgeLifecycleServicerWorkflow(deps)

    @rpc_errors
    async def ActivateLineageEdge(
        self, request: lineage_v1_lineage_edge_lifecycle_service_pb2.ActivateLineageEdgeRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_lineage_edge_lifecycle_service_pb2.ActivateLineageEdgeResponse:
        """Activates a lineage edge."""
        return await self.workflow.handle_activate_lineage_edge(request)

    @rpc_errors
    async def ExpireLineageEdge(
        self, request: lineage_v1_lineage_edge_lifecycle_service_pb2.ExpireLineageEdgeRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_lineage_edge_lifecycle_service_pb2.ExpireLineageEdgeResponse:
        """Expires a lineage edge."""
        return await self.workflow.handle_expire_lineage_edge(request)

    @rpc_errors
    @retry_transient
    async def GetLineageEdgeLifecycle(
        self, request: lineage_v1_lineage_edge_lifecycle_service_pb2.GetLineageEdgeLifecycleRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_lineage_edge_lifecycle_service_pb2.GetLineageEdgeLifecycleResponse:
        """Returns a lineage edge."""
        return await self.workflow.handle_get_lineage_edge_lifecycle(request)

    @rpc_errors
    async def ReinstateLineageEdge(
        self, request: lineage_v1_lineage_edge_lifecycle_service_pb2.ReinstateLineageEdgeRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_lineage_edge_lifecycle_service_pb2.ReinstateLineageEdgeResponse:
        """Reinstates a lineage edge."""
        return await self.workflow.handle_reinstate_lineage_edge(request)

    @rpc_errors
    async def RenewLineageEdge(
        self, request: lineage_v1_lineage_edge_lifecycle_service_pb2.RenewLineageEdgeRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_lineage_edge_lifecycle_service_pb2.RenewLineageEdgeResponse:
        """Renews a lineage edge."""
        return await self.workflow.handle_renew_lineage_edge(request)

    @rpc_errors
    async def ScheduleLineageEdgeExpiry(
        self, request: lineage_v1_lineage_edge_lifecycle_service_pb2.ScheduleLineageEdgeExpiryRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_lineage_edge_lifecycle_service_pb2.ScheduleLineageEdgeExpiryResponse:
        """Schedules a lineage edge."""
        return await self.workflow.handle_schedule_lineage_edge_expiry(request)

    @rpc_errors
    async def SuspendLineageEdge(
        self, request: lineage_v1_lineage_edge_lifecycle_service_pb2.SuspendLineageEdgeRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_lineage_edge_lifecycle_service_pb2.SuspendLineageEdgeResponse:
        """Suspends a lineage edge."""
        return await self.workflow.handle_suspend_lineage_edge(request)
