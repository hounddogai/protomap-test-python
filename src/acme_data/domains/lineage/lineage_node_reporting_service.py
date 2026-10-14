"""Builds and schedules reports about lineage nodes."""

from __future__ import annotations

from collections.abc import AsyncIterator

import grpc

from acme.lineage.v1 import lineage_node_reporting_service_pb2 as lineage_v1_lineage_node_reporting_service_pb2
from acme.lineage.v1 import (
    lineage_node_reporting_service_pb2_grpc as lineage_v1_lineage_node_reporting_service_pb2_grpc,
)

from acme_data.domains.lineage.dependencies import Dependencies
from acme_data.domains.lineage.lineage_node_reporting_service_workflow import LineageNodeReportingServicerWorkflow
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors


class LineageNodeReportingServicer(
    lineage_v1_lineage_node_reporting_service_pb2_grpc.LineageNodeReportingServiceServicer
):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps
        self.workflow = LineageNodeReportingServicerWorkflow(deps)

    @rpc_errors
    @retry_transient
    async def CountLineageNodeTotals(
        self, request: lineage_v1_lineage_node_reporting_service_pb2.CountLineageNodeTotalsRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_lineage_node_reporting_service_pb2.CountLineageNodeTotalsResponse:
        """Counts lineage nodes by status."""
        return await self.workflow.handle_count_lineage_node_totals(request)

    @rpc_errors
    async def DeleteLineageNodeReport(
        self, request: lineage_v1_lineage_node_reporting_service_pb2.DeleteLineageNodeReportRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_lineage_node_reporting_service_pb2.DeleteLineageNodeReportResponse:
        """Deletes a lineage node."""
        return await self.workflow.handle_delete_lineage_node_report(request)

    @rpc_errors
    @retry_transient
    async def FetchLineageNodeReport(
        self, request: lineage_v1_lineage_node_reporting_service_pb2.FetchLineageNodeReportRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_lineage_node_reporting_service_pb2.FetchLineageNodeReportResponse:
        """Returns a lineage node."""
        return await self.workflow.handle_fetch_lineage_node_report(request)

    @rpc_errors
    async def GenerateLineageNodeReport(
        self, request: lineage_v1_lineage_node_reporting_service_pb2.GenerateLineageNodeReportRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_lineage_node_reporting_service_pb2.GenerateLineageNodeReportResponse:
        """Generates a lineage node."""
        return await self.workflow.handle_generate_lineage_node_report(request)

    @rpc_errors
    @retry_transient
    async def ListLineageNodeReports(
        self, request: lineage_v1_lineage_node_reporting_service_pb2.ListLineageNodeReportsRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_lineage_node_reporting_service_pb2.ListLineageNodeReportsResponse:
        """Lists lineage nodes a page at a time."""
        return await self.workflow.handle_list_lineage_node_reports(request)

    @rpc_errors
    async def ScheduleLineageNodeReport(
        self, request: lineage_v1_lineage_node_reporting_service_pb2.ScheduleLineageNodeReportRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_lineage_node_reporting_service_pb2.ScheduleLineageNodeReportResponse:
        """Schedules a lineage node."""
        return await self.workflow.handle_schedule_lineage_node_report(request)

    @rpc_errors
    async def ShareLineageNodeReport(
        self, request: lineage_v1_lineage_node_reporting_service_pb2.ShareLineageNodeReportRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_lineage_node_reporting_service_pb2.ShareLineageNodeReportResponse:
        """Shares a lineage node."""
        return await self.workflow.handle_share_lineage_node_report(request)
