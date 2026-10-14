"""Manages metric serieses: creates, reads, changes, and lists them."""

from __future__ import annotations

from collections.abc import AsyncIterator

import grpc

from acme.metrics.v1 import metric_series_service_pb2 as metrics_v1_metric_series_service_pb2
from acme.metrics.v1 import metric_series_service_pb2_grpc as metrics_v1_metric_series_service_pb2_grpc

from acme_data.domains.metrics.dependencies import Dependencies
from acme_data.domains.metrics.metric_series_service_operations import handle_batch_create_metric_serieses
from acme_data.domains.metrics.metric_series_service_operations import handle_clone_metric_series
from acme_data.domains.metrics.metric_series_service_operations import handle_create_metric_series
from acme_data.domains.metrics.metric_series_service_operations import handle_delete_metric_series
from acme_data.domains.metrics.metric_series_service_operations import handle_get_metric_series
from acme_data.domains.metrics.metric_series_service_operations import handle_list_metric_serieses
from acme_data.domains.metrics.metric_series_service_operations import handle_search_metric_serieses
from acme_data.domains.metrics.metric_series_service_operations import handle_update_metric_series
from acme_data.domains.metrics.metric_series_service_operations import handle_watch_metric_serieses
from acme_data.platform.rpc import messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors


class MetricSeriesServicer(metrics_v1_metric_series_service_pb2_grpc.MetricSeriesServiceServicer):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    async def BatchCreateMetricSerieses(
        self, requests: AsyncIterator[
            metrics_v1_metric_series_service_pb2.BatchCreateMetricSeriesesRequest
        ], context: grpc.aio.ServicerContext,
    ) -> metrics_v1_metric_series_service_pb2.BatchCreateMetricSeriesesResponse:
        """Takes a stream of metric serieses and answers once at the end."""
        response = metrics_v1_metric_series_service_pb2.BatchCreateMetricSeriesesResponse()
        async for request in requests:
            response.MergeFrom(await handle_batch_create_metric_serieses(self.deps, request))
        return response

    @rpc_errors
    async def CloneMetricSeries(
        self, request: metrics_v1_metric_series_service_pb2.CloneMetricSeriesRequest, context: grpc.aio.ServicerContext,
    ) -> metrics_v1_metric_series_service_pb2.CloneMetricSeriesResponse:
        """Creates a metric series."""
        return await handle_clone_metric_series(self.deps, request)

    @rpc_errors
    async def CreateMetricSeries(
        self, request: metrics_v1_metric_series_service_pb2.CreateMetricSeriesRequest, context: grpc.aio.ServicerContext,
    ) -> metrics_v1_metric_series_service_pb2.CreateMetricSeriesResponse:
        """Creates a metric series."""
        return await handle_create_metric_series(self.deps, request)

    @rpc_errors
    async def DeleteMetricSeries(
        self, request: metrics_v1_metric_series_service_pb2.DeleteMetricSeriesRequest, context: grpc.aio.ServicerContext,
    ) -> metrics_v1_metric_series_service_pb2.DeleteMetricSeriesResponse:
        """Deletes a metric series."""
        return await handle_delete_metric_series(self.deps, request)

    @rpc_errors
    @retry_transient
    async def GetMetricSeries(
        self, request: metrics_v1_metric_series_service_pb2.GetMetricSeriesRequest, context: grpc.aio.ServicerContext,
    ) -> metrics_v1_metric_series_service_pb2.GetMetricSeriesResponse:
        """Returns a metric series."""
        return await handle_get_metric_series(self.deps, request)

    @rpc_errors
    @retry_transient
    async def ListMetricSerieses(
        self, request: metrics_v1_metric_series_service_pb2.ListMetricSeriesesRequest, context: grpc.aio.ServicerContext,
    ) -> metrics_v1_metric_series_service_pb2.ListMetricSeriesesResponse:
        """Lists metric serieses a page at a time."""
        return await handle_list_metric_serieses(self.deps, request)

    @rpc_errors
    @retry_transient
    async def SearchMetricSerieses(
        self, request: metrics_v1_metric_series_service_pb2.SearchMetricSeriesesRequest, context: grpc.aio.ServicerContext,
    ) -> metrics_v1_metric_series_service_pb2.SearchMetricSeriesesResponse:
        """Lists metric serieses a page at a time."""
        return await handle_search_metric_serieses(self.deps, request)

    @rpc_errors
    async def UpdateMetricSeries(
        self, request: metrics_v1_metric_series_service_pb2.UpdateMetricSeriesRequest, context: grpc.aio.ServicerContext,
    ) -> metrics_v1_metric_series_service_pb2.UpdateMetricSeriesResponse:
        """Changes a metric series."""
        return await handle_update_metric_series(self.deps, request)

    @stream_errors
    async def WatchMetricSerieses(
        self, request: metrics_v1_metric_series_service_pb2.WatchMetricSeriesesRequest, context: grpc.aio.ServicerContext,
    ) -> AsyncIterator[metrics_v1_metric_series_service_pb2.WatchMetricSeriesesResponse]:
        """Streams the changes of metric serieses as they happen."""
        response = await handle_watch_metric_serieses(self.deps, request)
        for item in messages((response,)):
            yield item
