"""Answers read-only questions about metric serieses, for screens and reports."""

from __future__ import annotations

from collections.abc import AsyncIterator

import grpc

from acme.metrics.v1 import metric_series_query_service_pb2 as metrics_v1_metric_series_query_service_pb2
from acme.metrics.v1 import metric_series_query_service_pb2_grpc as metrics_v1_metric_series_query_service_pb2_grpc

from acme_data.domains.metrics.dependencies import Dependencies
from acme_data.domains.metrics.metric_series_query_service_workflow import MetricSeriesQueryServicerWorkflow
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors


class MetricSeriesQueryServicer(metrics_v1_metric_series_query_service_pb2_grpc.MetricSeriesQueryServiceServicer):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps
        self.workflow = MetricSeriesQueryServicerWorkflow(deps)

    @rpc_errors
    @retry_transient
    async def BrowseMetricSerieses(
        self, request: metrics_v1_metric_series_query_service_pb2.BrowseMetricSeriesesRequest, context: grpc.aio.ServicerContext,
    ) -> metrics_v1_metric_series_query_service_pb2.BrowseMetricSeriesesResponse:
        """Lists metric serieses a page at a time."""
        return await self.workflow.handle_browse_metric_serieses(request)

    @rpc_errors
    @retry_transient
    async def CountMetricSerieses(
        self, request: metrics_v1_metric_series_query_service_pb2.CountMetricSeriesesRequest, context: grpc.aio.ServicerContext,
    ) -> metrics_v1_metric_series_query_service_pb2.CountMetricSeriesesResponse:
        """Counts metric serieses by status."""
        return await self.workflow.handle_count_metric_serieses(request)

    @rpc_errors
    @retry_transient
    async def LookupMetricSeries(
        self, request: metrics_v1_metric_series_query_service_pb2.LookupMetricSeriesRequest, context: grpc.aio.ServicerContext,
    ) -> metrics_v1_metric_series_query_service_pb2.LookupMetricSeriesResponse:
        """Returns a metric series."""
        return await self.workflow.handle_lookup_metric_series(request)

    @rpc_errors
    @retry_transient
    async def PeekMetricSeries(
        self, request: metrics_v1_metric_series_query_service_pb2.PeekMetricSeriesRequest, context: grpc.aio.ServicerContext,
    ) -> metrics_v1_metric_series_query_service_pb2.PeekMetricSeriesResponse:
        """Returns a metric series."""
        return await self.workflow.handle_peek_metric_series(request)

    @rpc_errors
    @retry_transient
    async def SuggestMetricSerieses(
        self, request: metrics_v1_metric_series_query_service_pb2.SuggestMetricSeriesesRequest, context: grpc.aio.ServicerContext,
    ) -> metrics_v1_metric_series_query_service_pb2.SuggestMetricSeriesesResponse:
        """Lists metric serieses a page at a time."""
        return await self.workflow.handle_suggest_metric_serieses(request)

    @rpc_errors
    async def SummarizeMetricSerieses(
        self, request: metrics_v1_metric_series_query_service_pb2.SummarizeMetricSeriesesRequest, context: grpc.aio.ServicerContext,
    ) -> metrics_v1_metric_series_query_service_pb2.SummarizeMetricSeriesesResponse:
        """Summarizes a metric series."""
        return await self.workflow.handle_summarize_metric_serieses(request)
