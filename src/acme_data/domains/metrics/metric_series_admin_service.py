"""Operator actions on metric serieses that support staff run by hand."""

from __future__ import annotations

from collections.abc import AsyncIterator

import grpc

from acme.metrics.v1 import metric_series_admin_service_pb2 as metrics_v1_metric_series_admin_service_pb2
from acme.metrics.v1 import metric_series_admin_service_pb2_grpc as metrics_v1_metric_series_admin_service_pb2_grpc

from acme_data.domains.metrics.dependencies import Dependencies
from acme_data.domains.metrics.metric_series_admin_service_operations import handle_archive_metric_series
from acme_data.domains.metrics.metric_series_admin_service_operations import handle_inspect_metric_series
from acme_data.domains.metrics.metric_series_admin_service_operations import handle_lock_metric_series
from acme_data.domains.metrics.metric_series_admin_service_operations import handle_purge_metric_series
from acme_data.domains.metrics.metric_series_admin_service_operations import handle_reassign_metric_series
from acme_data.domains.metrics.metric_series_admin_service_operations import handle_repair_metric_series
from acme_data.domains.metrics.metric_series_admin_service_operations import handle_restore_metric_series
from acme_data.domains.metrics.metric_series_admin_service_operations import handle_unlock_metric_series
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors


class MetricSeriesAdminServicer(metrics_v1_metric_series_admin_service_pb2_grpc.MetricSeriesAdminServiceServicer):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    async def ArchiveMetricSeries(
        self, request: metrics_v1_metric_series_admin_service_pb2.ArchiveMetricSeriesRequest, context: grpc.aio.ServicerContext,
    ) -> metrics_v1_metric_series_admin_service_pb2.ArchiveMetricSeriesResponse:
        """Archives a metric series."""
        return await handle_archive_metric_series(self.deps, request)

    @rpc_errors
    @retry_transient
    async def InspectMetricSeries(
        self, request: metrics_v1_metric_series_admin_service_pb2.InspectMetricSeriesRequest, context: grpc.aio.ServicerContext,
    ) -> metrics_v1_metric_series_admin_service_pb2.InspectMetricSeriesResponse:
        """Returns a metric series."""
        return await handle_inspect_metric_series(self.deps, request)

    @rpc_errors
    async def LockMetricSeries(
        self, request: metrics_v1_metric_series_admin_service_pb2.LockMetricSeriesRequest, context: grpc.aio.ServicerContext,
    ) -> metrics_v1_metric_series_admin_service_pb2.LockMetricSeriesResponse:
        """Locks a metric series."""
        return await handle_lock_metric_series(self.deps, request)

    @rpc_errors
    async def PurgeMetricSeries(
        self, request: metrics_v1_metric_series_admin_service_pb2.PurgeMetricSeriesRequest, context: grpc.aio.ServicerContext,
    ) -> metrics_v1_metric_series_admin_service_pb2.PurgeMetricSeriesResponse:
        """Deletes a metric series."""
        return await handle_purge_metric_series(self.deps, request)

    @rpc_errors
    async def ReassignMetricSeries(
        self, request: metrics_v1_metric_series_admin_service_pb2.ReassignMetricSeriesRequest, context: grpc.aio.ServicerContext,
    ) -> metrics_v1_metric_series_admin_service_pb2.ReassignMetricSeriesResponse:
        """Reassigns a metric series."""
        return await handle_reassign_metric_series(self.deps, request)

    @rpc_errors
    async def RepairMetricSeries(
        self, request: metrics_v1_metric_series_admin_service_pb2.RepairMetricSeriesRequest, context: grpc.aio.ServicerContext,
    ) -> metrics_v1_metric_series_admin_service_pb2.RepairMetricSeriesResponse:
        """Repairs a metric series."""
        return await handle_repair_metric_series(self.deps, request)

    @rpc_errors
    async def RestoreMetricSeries(
        self, request: metrics_v1_metric_series_admin_service_pb2.RestoreMetricSeriesRequest, context: grpc.aio.ServicerContext,
    ) -> metrics_v1_metric_series_admin_service_pb2.RestoreMetricSeriesResponse:
        """Restores a metric series."""
        return await handle_restore_metric_series(self.deps, request)

    @rpc_errors
    async def UnlockMetricSeries(
        self, request: metrics_v1_metric_series_admin_service_pb2.UnlockMetricSeriesRequest, context: grpc.aio.ServicerContext,
    ) -> metrics_v1_metric_series_admin_service_pb2.UnlockMetricSeriesResponse:
        """Unlocks a metric series."""
        return await handle_unlock_metric_series(self.deps, request)
