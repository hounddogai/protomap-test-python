"""Moves an analytics report between the states of its lifecycle."""

from __future__ import annotations

from collections.abc import AsyncIterator

import grpc

from acme.analytics.v1 import (
    analytics_report_lifecycle_service_pb2 as analytics_v1_analytics_report_lifecycle_service_pb2,
)
from acme.analytics.v1 import (
    analytics_report_lifecycle_service_pb2_grpc as analytics_v1_analytics_report_lifecycle_service_pb2_grpc,
)

from acme_data.domains.analytics.analytics_report_lifecycle_service_operations import handle_activate_analytics_report
from acme_data.domains.analytics.analytics_report_lifecycle_service_operations import handle_expire_analytics_report
from acme_data.domains.analytics.analytics_report_lifecycle_service_operations import (
    handle_get_analytics_report_lifecycle,
)
from acme_data.domains.analytics.analytics_report_lifecycle_service_operations import handle_reinstate_analytics_report
from acme_data.domains.analytics.analytics_report_lifecycle_service_operations import handle_renew_analytics_report
from acme_data.domains.analytics.analytics_report_lifecycle_service_operations import (
    handle_schedule_analytics_report_expiry,
)
from acme_data.domains.analytics.analytics_report_lifecycle_service_operations import handle_suspend_analytics_report
from acme_data.domains.analytics.analytics_report_lifecycle_service_operations import handle_terminate_analytics_report
from acme_data.domains.analytics.dependencies import Dependencies
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors


class AnalyticsReportLifecycleServicer(
    analytics_v1_analytics_report_lifecycle_service_pb2_grpc.AnalyticsReportLifecycleServiceServicer
):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    async def ActivateAnalyticsReport(
        self, request: analytics_v1_analytics_report_lifecycle_service_pb2.ActivateAnalyticsReportRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_analytics_report_lifecycle_service_pb2.ActivateAnalyticsReportResponse:
        """Activates an analytics report."""
        return await handle_activate_analytics_report(self.deps, request)

    @rpc_errors
    async def ExpireAnalyticsReport(
        self, request: analytics_v1_analytics_report_lifecycle_service_pb2.ExpireAnalyticsReportRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_analytics_report_lifecycle_service_pb2.ExpireAnalyticsReportResponse:
        """Expires an analytics report."""
        return await handle_expire_analytics_report(self.deps, request)

    @rpc_errors
    @retry_transient
    async def GetAnalyticsReportLifecycle(
        self, request: analytics_v1_analytics_report_lifecycle_service_pb2.GetAnalyticsReportLifecycleRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_analytics_report_lifecycle_service_pb2.GetAnalyticsReportLifecycleResponse:
        """Returns an analytics report."""
        return await handle_get_analytics_report_lifecycle(self.deps, request)

    @rpc_errors
    async def ReinstateAnalyticsReport(
        self, request: analytics_v1_analytics_report_lifecycle_service_pb2.ReinstateAnalyticsReportRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_analytics_report_lifecycle_service_pb2.ReinstateAnalyticsReportResponse:
        """Reinstates an analytics report."""
        return await handle_reinstate_analytics_report(self.deps, request)

    @rpc_errors
    async def RenewAnalyticsReport(
        self, request: analytics_v1_analytics_report_lifecycle_service_pb2.RenewAnalyticsReportRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_analytics_report_lifecycle_service_pb2.RenewAnalyticsReportResponse:
        """Renews an analytics report."""
        return await handle_renew_analytics_report(self.deps, request)

    @rpc_errors
    async def ScheduleAnalyticsReportExpiry(
        self, request: analytics_v1_analytics_report_lifecycle_service_pb2.ScheduleAnalyticsReportExpiryRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_analytics_report_lifecycle_service_pb2.ScheduleAnalyticsReportExpiryResponse:
        """Schedules an analytics report."""
        return await handle_schedule_analytics_report_expiry(self.deps, request)

    @rpc_errors
    async def SuspendAnalyticsReport(
        self, request: analytics_v1_analytics_report_lifecycle_service_pb2.SuspendAnalyticsReportRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_analytics_report_lifecycle_service_pb2.SuspendAnalyticsReportResponse:
        """Suspends an analytics report."""
        return await handle_suspend_analytics_report(self.deps, request)

    @rpc_errors
    async def TerminateAnalyticsReport(
        self, request: analytics_v1_analytics_report_lifecycle_service_pb2.TerminateAnalyticsReportRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_analytics_report_lifecycle_service_pb2.TerminateAnalyticsReportResponse:
        """Terminates an analytics report."""
        return await handle_terminate_analytics_report(self.deps, request)
