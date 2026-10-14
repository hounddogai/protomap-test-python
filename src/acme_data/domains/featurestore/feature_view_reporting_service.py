"""Builds and schedules reports about feature views."""

from __future__ import annotations

from collections.abc import AsyncIterator

import grpc

from acme.featurestore.v1 import (
    feature_view_reporting_service_pb2 as featurestore_v1_feature_view_reporting_service_pb2,
)
from acme.featurestore.v1 import (
    feature_view_reporting_service_pb2_grpc as featurestore_v1_feature_view_reporting_service_pb2_grpc,
)

from acme_data.domains.featurestore.dependencies import Dependencies
from acme_data.domains.featurestore.feature_view_reporting_service_workflow import FeatureViewReportingServicerWorkflow
from acme_data.platform.rpc import messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors


class FeatureViewReportingServicer(
    featurestore_v1_feature_view_reporting_service_pb2_grpc.FeatureViewReportingServiceServicer
):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps
        self.workflow = FeatureViewReportingServicerWorkflow(deps)

    @rpc_errors
    @retry_transient
    async def CountFeatureViewTotals(
        self, request: featurestore_v1_feature_view_reporting_service_pb2.CountFeatureViewTotalsRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_feature_view_reporting_service_pb2.CountFeatureViewTotalsResponse:
        """Counts feature views by status."""
        return await self.workflow.handle_count_feature_view_totals(request)

    @rpc_errors
    async def DeleteFeatureViewReport(
        self, request: featurestore_v1_feature_view_reporting_service_pb2.DeleteFeatureViewReportRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_feature_view_reporting_service_pb2.DeleteFeatureViewReportResponse:
        """Deletes a feature view."""
        return await self.workflow.handle_delete_feature_view_report(request)

    @rpc_errors
    @retry_transient
    async def FetchFeatureViewReport(
        self, request: featurestore_v1_feature_view_reporting_service_pb2.FetchFeatureViewReportRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_feature_view_reporting_service_pb2.FetchFeatureViewReportResponse:
        """Returns a feature view."""
        return await self.workflow.handle_fetch_feature_view_report(request)

    @rpc_errors
    async def GenerateFeatureViewReport(
        self, request: featurestore_v1_feature_view_reporting_service_pb2.GenerateFeatureViewReportRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_feature_view_reporting_service_pb2.GenerateFeatureViewReportResponse:
        """Generates a feature view."""
        return await self.workflow.handle_generate_feature_view_report(request)

    @rpc_errors
    @retry_transient
    async def ListFeatureViewReports(
        self, request: featurestore_v1_feature_view_reporting_service_pb2.ListFeatureViewReportsRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_feature_view_reporting_service_pb2.ListFeatureViewReportsResponse:
        """Lists feature views a page at a time."""
        return await self.workflow.handle_list_feature_view_reports(request)

    @rpc_errors
    async def ScheduleFeatureViewReport(
        self, request: featurestore_v1_feature_view_reporting_service_pb2.ScheduleFeatureViewReportRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_feature_view_reporting_service_pb2.ScheduleFeatureViewReportResponse:
        """Schedules a feature view."""
        return await self.workflow.handle_schedule_feature_view_report(request)

    @rpc_errors
    async def ShareFeatureViewReport(
        self, request: featurestore_v1_feature_view_reporting_service_pb2.ShareFeatureViewReportRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_feature_view_reporting_service_pb2.ShareFeatureViewReportResponse:
        """Shares a feature view."""
        return await self.workflow.handle_share_feature_view_report(request)

    @stream_errors
    async def StreamFeatureViewMetrics(
        self, request: featurestore_v1_feature_view_reporting_service_pb2.StreamFeatureViewMetricsRequest, context: grpc.aio.ServicerContext,
    ) -> AsyncIterator[featurestore_v1_feature_view_reporting_service_pb2.StreamFeatureViewMetricsResponse]:
        """Streams the changes of feature views as they happen."""
        response = await self.workflow.handle_stream_feature_view_metrics(request)
        for item in messages((response,)):
            yield item
