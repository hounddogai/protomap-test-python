"""Keeps every version of a dashboard and restores earlier ones."""

from __future__ import annotations

from collections.abc import AsyncIterator

import grpc

from acme.metrics.v1 import dashboard_history_service_pb2 as metrics_v1_dashboard_history_service_pb2
from acme.metrics.v1 import dashboard_history_service_pb2_grpc as metrics_v1_dashboard_history_service_pb2_grpc

from acme_data.domains.metrics.dashboard_history_service_operations import handle_annotate_dashboard_version
from acme_data.domains.metrics.dashboard_history_service_operations import handle_compare_dashboard_versions
from acme_data.domains.metrics.dashboard_history_service_operations import handle_get_dashboard_version
from acme_data.domains.metrics.dashboard_history_service_operations import handle_list_dashboard_versions
from acme_data.domains.metrics.dashboard_history_service_operations import handle_prune_dashboard_versions
from acme_data.domains.metrics.dashboard_history_service_operations import handle_record_dashboard_version
from acme_data.domains.metrics.dashboard_history_service_operations import handle_revert_dashboard
from acme_data.domains.metrics.dependencies import Dependencies
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors


class DashboardHistoryServicer(metrics_v1_dashboard_history_service_pb2_grpc.DashboardHistoryServiceServicer):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    async def AnnotateDashboardVersion(
        self, request: metrics_v1_dashboard_history_service_pb2.AnnotateDashboardVersionRequest, context: grpc.aio.ServicerContext,
    ) -> metrics_v1_dashboard_history_service_pb2.AnnotateDashboardVersionResponse:
        """Annotates a dashboard."""
        return await handle_annotate_dashboard_version(self.deps, request)

    @rpc_errors
    async def CompareDashboardVersions(
        self, request: metrics_v1_dashboard_history_service_pb2.CompareDashboardVersionsRequest, context: grpc.aio.ServicerContext,
    ) -> metrics_v1_dashboard_history_service_pb2.CompareDashboardVersionsResponse:
        """Compares a dashboard."""
        return await handle_compare_dashboard_versions(self.deps, request)

    @rpc_errors
    @retry_transient
    async def GetDashboardVersion(
        self, request: metrics_v1_dashboard_history_service_pb2.GetDashboardVersionRequest, context: grpc.aio.ServicerContext,
    ) -> metrics_v1_dashboard_history_service_pb2.GetDashboardVersionResponse:
        """Returns a dashboard."""
        return await handle_get_dashboard_version(self.deps, request)

    @rpc_errors
    @retry_transient
    async def ListDashboardVersions(
        self, request: metrics_v1_dashboard_history_service_pb2.ListDashboardVersionsRequest, context: grpc.aio.ServicerContext,
    ) -> metrics_v1_dashboard_history_service_pb2.ListDashboardVersionsResponse:
        """Lists dashboards a page at a time."""
        return await handle_list_dashboard_versions(self.deps, request)

    @rpc_errors
    async def PruneDashboardVersions(
        self, request: metrics_v1_dashboard_history_service_pb2.PruneDashboardVersionsRequest, context: grpc.aio.ServicerContext,
    ) -> metrics_v1_dashboard_history_service_pb2.PruneDashboardVersionsResponse:
        """Deletes a dashboard."""
        return await handle_prune_dashboard_versions(self.deps, request)

    @rpc_errors
    async def RecordDashboardVersion(
        self, request: metrics_v1_dashboard_history_service_pb2.RecordDashboardVersionRequest, context: grpc.aio.ServicerContext,
    ) -> metrics_v1_dashboard_history_service_pb2.RecordDashboardVersionResponse:
        """Records a dashboard."""
        return await handle_record_dashboard_version(self.deps, request)

    @rpc_errors
    async def RevertDashboard(
        self, request: metrics_v1_dashboard_history_service_pb2.RevertDashboardRequest, context: grpc.aio.ServicerContext,
    ) -> metrics_v1_dashboard_history_service_pb2.RevertDashboardResponse:
        """Reverts a dashboard."""
        return await handle_revert_dashboard(self.deps, request)
