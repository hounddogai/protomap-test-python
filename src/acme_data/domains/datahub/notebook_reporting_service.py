"""Builds and schedules reports about notebooks."""

from __future__ import annotations

from collections.abc import AsyncIterator

import grpc

from acme.datahub.v1 import notebook_reporting_service_pb2 as datahub_v1_notebook_reporting_service_pb2
from acme.datahub.v1 import notebook_reporting_service_pb2_grpc as datahub_v1_notebook_reporting_service_pb2_grpc

from acme_data.domains.datahub.dependencies import Dependencies
from acme_data.domains.datahub.notebook_reporting_service_workflow import NotebookReportingServicerWorkflow
from acme_data.platform.rpc import messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors


class NotebookReportingServicer(datahub_v1_notebook_reporting_service_pb2_grpc.NotebookReportingServiceServicer):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps
        self.workflow = NotebookReportingServicerWorkflow(deps)

    @rpc_errors
    @retry_transient
    async def CountNotebookTotals(
        self, request: datahub_v1_notebook_reporting_service_pb2.CountNotebookTotalsRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_notebook_reporting_service_pb2.CountNotebookTotalsResponse:
        """Counts notebooks by status."""
        return await self.workflow.handle_count_notebook_totals(request)

    @rpc_errors
    async def DeleteNotebookReport(
        self, request: datahub_v1_notebook_reporting_service_pb2.DeleteNotebookReportRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_notebook_reporting_service_pb2.DeleteNotebookReportResponse:
        """Deletes a notebook."""
        return await self.workflow.handle_delete_notebook_report(request)

    @rpc_errors
    @retry_transient
    async def FetchNotebookReport(
        self, request: datahub_v1_notebook_reporting_service_pb2.FetchNotebookReportRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_notebook_reporting_service_pb2.FetchNotebookReportResponse:
        """Returns a notebook."""
        return await self.workflow.handle_fetch_notebook_report(request)

    @rpc_errors
    async def GenerateNotebookReport(
        self, request: datahub_v1_notebook_reporting_service_pb2.GenerateNotebookReportRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_notebook_reporting_service_pb2.GenerateNotebookReportResponse:
        """Generates a notebook."""
        return await self.workflow.handle_generate_notebook_report(request)

    @rpc_errors
    @retry_transient
    async def ListNotebookReports(
        self, request: datahub_v1_notebook_reporting_service_pb2.ListNotebookReportsRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_notebook_reporting_service_pb2.ListNotebookReportsResponse:
        """Lists notebooks a page at a time."""
        return await self.workflow.handle_list_notebook_reports(request)

    @rpc_errors
    async def ScheduleNotebookReport(
        self, request: datahub_v1_notebook_reporting_service_pb2.ScheduleNotebookReportRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_notebook_reporting_service_pb2.ScheduleNotebookReportResponse:
        """Schedules a notebook."""
        return await self.workflow.handle_schedule_notebook_report(request)

    @rpc_errors
    async def ShareNotebookReport(
        self, request: datahub_v1_notebook_reporting_service_pb2.ShareNotebookReportRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_notebook_reporting_service_pb2.ShareNotebookReportResponse:
        """Shares a notebook."""
        return await self.workflow.handle_share_notebook_report(request)

    @stream_errors
    async def StreamNotebookMetrics(
        self, request: datahub_v1_notebook_reporting_service_pb2.StreamNotebookMetricsRequest, context: grpc.aio.ServicerContext,
    ) -> AsyncIterator[datahub_v1_notebook_reporting_service_pb2.StreamNotebookMetricsResponse]:
        """Streams the changes of notebooks as they happen."""
        response = await self.workflow.handle_stream_notebook_metrics(request)
        for item in messages((response,)):
            yield item
