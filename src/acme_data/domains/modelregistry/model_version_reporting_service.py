"""Builds and schedules reports about model versions."""

from __future__ import annotations

from collections.abc import AsyncIterator

import grpc

from acme.modelregistry.v1 import (
    model_version_reporting_service_pb2 as modelregistry_v1_model_version_reporting_service_pb2,
)
from acme.modelregistry.v1 import (
    model_version_reporting_service_pb2_grpc as modelregistry_v1_model_version_reporting_service_pb2_grpc,
)

from acme_data.domains.modelregistry.dependencies import Dependencies
from acme_data.domains.modelregistry.model_version_reporting_service_operations import handle_count_model_version_totals
from acme_data.domains.modelregistry.model_version_reporting_service_operations import handle_fetch_model_version_report
from acme_data.domains.modelregistry.model_version_reporting_service_operations import (
    handle_generate_model_version_report,
)
from acme_data.domains.modelregistry.model_version_reporting_service_operations import handle_list_model_version_reports
from acme_data.domains.modelregistry.model_version_reporting_service_operations import (
    handle_schedule_model_version_report,
)
from acme_data.domains.modelregistry.model_version_reporting_service_operations import handle_share_model_version_report
from acme_data.domains.modelregistry.model_version_reporting_service_operations import (
    handle_stream_model_version_metrics,
)
from acme_data.platform.rpc import messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors


class ModelVersionReportingServicer(
    modelregistry_v1_model_version_reporting_service_pb2_grpc.ModelVersionReportingServiceServicer
):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    @retry_transient
    async def CountModelVersionTotals(
        self, request: modelregistry_v1_model_version_reporting_service_pb2.CountModelVersionTotalsRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_model_version_reporting_service_pb2.CountModelVersionTotalsResponse:
        """Counts model versions by status."""
        return await handle_count_model_version_totals(self.deps, request)

    @rpc_errors
    @retry_transient
    async def FetchModelVersionReport(
        self, request: modelregistry_v1_model_version_reporting_service_pb2.FetchModelVersionReportRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_model_version_reporting_service_pb2.FetchModelVersionReportResponse:
        """Returns a model version."""
        return await handle_fetch_model_version_report(self.deps, request)

    @rpc_errors
    async def GenerateModelVersionReport(
        self, request: modelregistry_v1_model_version_reporting_service_pb2.GenerateModelVersionReportRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_model_version_reporting_service_pb2.GenerateModelVersionReportResponse:
        """Generates a model version."""
        return await handle_generate_model_version_report(self.deps, request)

    @rpc_errors
    @retry_transient
    async def ListModelVersionReports(
        self, request: modelregistry_v1_model_version_reporting_service_pb2.ListModelVersionReportsRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_model_version_reporting_service_pb2.ListModelVersionReportsResponse:
        """Lists model versions a page at a time."""
        return await handle_list_model_version_reports(self.deps, request)

    @rpc_errors
    async def ScheduleModelVersionReport(
        self, request: modelregistry_v1_model_version_reporting_service_pb2.ScheduleModelVersionReportRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_model_version_reporting_service_pb2.ScheduleModelVersionReportResponse:
        """Schedules a model version."""
        return await handle_schedule_model_version_report(self.deps, request)

    @rpc_errors
    async def ShareModelVersionReport(
        self, request: modelregistry_v1_model_version_reporting_service_pb2.ShareModelVersionReportRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_model_version_reporting_service_pb2.ShareModelVersionReportResponse:
        """Shares a model version."""
        return await handle_share_model_version_report(self.deps, request)

    @stream_errors
    async def StreamModelVersionMetrics(
        self, request: modelregistry_v1_model_version_reporting_service_pb2.StreamModelVersionMetricsRequest, context: grpc.aio.ServicerContext,
    ) -> AsyncIterator[modelregistry_v1_model_version_reporting_service_pb2.StreamModelVersionMetricsResponse]:
        """Streams the changes of model versions as they happen."""
        response = await handle_stream_model_version_metrics(self.deps, request)
        for item in messages((response,)):
            yield item
