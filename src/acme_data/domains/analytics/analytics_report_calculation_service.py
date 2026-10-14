"""Computes the figures of an analytics report, such as totals, taxes, and estimates."""

from __future__ import annotations

from collections.abc import AsyncIterator

import grpc

from acme.analytics.v1 import (
    analytics_report_calculation_service_pb2 as analytics_v1_analytics_report_calculation_service_pb2,
)
from acme.analytics.v1 import (
    analytics_report_calculation_service_pb2_grpc as analytics_v1_analytics_report_calculation_service_pb2_grpc,
)

from acme_data.domains.analytics.analytics_report_calculation_service_workflow import (
    AnalyticsReportCalculationServicerWorkflow,
)
from acme_data.domains.analytics.dependencies import Dependencies
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors


class AnalyticsReportCalculationServicer(
    analytics_v1_analytics_report_calculation_service_pb2_grpc.AnalyticsReportCalculationServiceServicer
):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps
        self.workflow = AnalyticsReportCalculationServicerWorkflow(deps)

    @rpc_errors
    async def CalculateAnalyticsReport(
        self, request: analytics_v1_analytics_report_calculation_service_pb2.CalculateAnalyticsReportRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_analytics_report_calculation_service_pb2.CalculateAnalyticsReportResponse:
        """Calculates an analytics report."""
        return await self.workflow.handle_calculate_analytics_report(request)

    @rpc_errors
    async def CompareAnalyticsReportOptions(
        self, request: analytics_v1_analytics_report_calculation_service_pb2.CompareAnalyticsReportOptionsRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_analytics_report_calculation_service_pb2.CompareAnalyticsReportOptionsResponse:
        """Compares an analytics report."""
        return await self.workflow.handle_compare_analytics_report_options(request)

    @rpc_errors
    async def EstimateAnalyticsReport(
        self, request: analytics_v1_analytics_report_calculation_service_pb2.EstimateAnalyticsReportRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_analytics_report_calculation_service_pb2.EstimateAnalyticsReportResponse:
        """Estimates an analytics report."""
        return await self.workflow.handle_estimate_analytics_report(request)

    @rpc_errors
    async def ExplainAnalyticsReportCalculation(
        self, request: analytics_v1_analytics_report_calculation_service_pb2.ExplainAnalyticsReportCalculationRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_analytics_report_calculation_service_pb2.ExplainAnalyticsReportCalculationResponse:
        """Explains an analytics report."""
        return await self.workflow.handle_explain_analytics_report_calculation(request)

    @rpc_errors
    async def QuoteAnalyticsReport(
        self, request: analytics_v1_analytics_report_calculation_service_pb2.QuoteAnalyticsReportRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_analytics_report_calculation_service_pb2.QuoteAnalyticsReportResponse:
        """Quotes an analytics report."""
        return await self.workflow.handle_quote_analytics_report(request)

    @rpc_errors
    async def RecalculateAnalyticsReports(
        self, request: analytics_v1_analytics_report_calculation_service_pb2.RecalculateAnalyticsReportsRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_analytics_report_calculation_service_pb2.RecalculateAnalyticsReportsResponse:
        """Recalculates an analytics report."""
        return await self.workflow.handle_recalculate_analytics_reports(request)

    @rpc_errors
    async def SimulateAnalyticsReport(
        self, request: analytics_v1_analytics_report_calculation_service_pb2.SimulateAnalyticsReportRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_analytics_report_calculation_service_pb2.SimulateAnalyticsReportResponse:
        """Simulates an analytics report."""
        return await self.workflow.handle_simulate_analytics_report(request)
