"""Exports dashboards to files and other systems."""

from __future__ import annotations

from collections.abc import AsyncIterator

import grpc

from acme.metrics.v1 import dashboard_export_service_pb2 as metrics_v1_dashboard_export_service_pb2
from acme.metrics.v1 import dashboard_export_service_pb2_grpc as metrics_v1_dashboard_export_service_pb2_grpc

from acme_data.domains.metrics.dashboard_export_service_workflow import DashboardExportServicerWorkflow
from acme_data.domains.metrics.dependencies import Dependencies
from acme_data.platform.rpc import messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors


class DashboardExportServicer(metrics_v1_dashboard_export_service_pb2_grpc.DashboardExportServiceServicer):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps
        self.workflow = DashboardExportServicerWorkflow(deps)

    @rpc_errors
    async def CancelDashboardExport(
        self, request: metrics_v1_dashboard_export_service_pb2.CancelDashboardExportRequest, context: grpc.aio.ServicerContext,
    ) -> metrics_v1_dashboard_export_service_pb2.CancelDashboardExportResponse:
        """Cancels a dashboard."""
        return await self.workflow.handle_cancel_dashboard_export(request)

    @rpc_errors
    @retry_transient
    async def GetDashboardExport(
        self, request: metrics_v1_dashboard_export_service_pb2.GetDashboardExportRequest, context: grpc.aio.ServicerContext,
    ) -> metrics_v1_dashboard_export_service_pb2.GetDashboardExportResponse:
        """Returns a dashboard."""
        return await self.workflow.handle_get_dashboard_export(request)

    @rpc_errors
    async def RetryDashboardExport(
        self, request: metrics_v1_dashboard_export_service_pb2.RetryDashboardExportRequest, context: grpc.aio.ServicerContext,
    ) -> metrics_v1_dashboard_export_service_pb2.RetryDashboardExportResponse:
        """Retrys a dashboard."""
        return await self.workflow.handle_retry_dashboard_export(request)

    @rpc_errors
    async def ScheduleDashboardExport(
        self, request: metrics_v1_dashboard_export_service_pb2.ScheduleDashboardExportRequest, context: grpc.aio.ServicerContext,
    ) -> metrics_v1_dashboard_export_service_pb2.ScheduleDashboardExportResponse:
        """Schedules a dashboard."""
        return await self.workflow.handle_schedule_dashboard_export(request)

    @rpc_errors
    async def ShareDashboardExport(
        self, request: metrics_v1_dashboard_export_service_pb2.ShareDashboardExportRequest, context: grpc.aio.ServicerContext,
    ) -> metrics_v1_dashboard_export_service_pb2.ShareDashboardExportResponse:
        """Shares a dashboard."""
        return await self.workflow.handle_share_dashboard_export(request)

    @stream_errors
    async def StreamDashboardExport(
        self, request: metrics_v1_dashboard_export_service_pb2.StreamDashboardExportRequest, context: grpc.aio.ServicerContext,
    ) -> AsyncIterator[metrics_v1_dashboard_export_service_pb2.StreamDashboardExportResponse]:
        """Streams every matching dashboard."""
        response = await self.workflow.handle_stream_dashboard_export(request)
        for item in messages((response,)):
            yield item
