"""Exports metric alerts to files and other systems."""

from __future__ import annotations

from collections.abc import AsyncIterator

import grpc

from acme.metrics.v1 import metric_alert_export_service_pb2 as metrics_v1_metric_alert_export_service_pb2
from acme.metrics.v1 import metric_alert_export_service_pb2_grpc as metrics_v1_metric_alert_export_service_pb2_grpc

from acme_data.domains.metrics.dependencies import Dependencies
from acme_data.domains.metrics.metric_alert_export_service_operations import handle_get_metric_alert_export
from acme_data.domains.metrics.metric_alert_export_service_operations import handle_list_metric_alert_exports
from acme_data.domains.metrics.metric_alert_export_service_operations import handle_retry_metric_alert_export
from acme_data.domains.metrics.metric_alert_export_service_operations import handle_schedule_metric_alert_export
from acme_data.domains.metrics.metric_alert_export_service_operations import handle_share_metric_alert_export
from acme_data.domains.metrics.metric_alert_export_service_operations import handle_stream_metric_alert_export
from acme_data.platform.rpc import messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors


class MetricAlertExportServicer(metrics_v1_metric_alert_export_service_pb2_grpc.MetricAlertExportServiceServicer):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    @retry_transient
    async def GetMetricAlertExport(
        self, request: metrics_v1_metric_alert_export_service_pb2.GetMetricAlertExportRequest, context: grpc.aio.ServicerContext,
    ) -> metrics_v1_metric_alert_export_service_pb2.GetMetricAlertExportResponse:
        """Returns a metric alert."""
        return await handle_get_metric_alert_export(self.deps, request)

    @rpc_errors
    @retry_transient
    async def ListMetricAlertExports(
        self, request: metrics_v1_metric_alert_export_service_pb2.ListMetricAlertExportsRequest, context: grpc.aio.ServicerContext,
    ) -> metrics_v1_metric_alert_export_service_pb2.ListMetricAlertExportsResponse:
        """Lists metric alerts a page at a time."""
        return await handle_list_metric_alert_exports(self.deps, request)

    @rpc_errors
    async def RetryMetricAlertExport(
        self, request: metrics_v1_metric_alert_export_service_pb2.RetryMetricAlertExportRequest, context: grpc.aio.ServicerContext,
    ) -> metrics_v1_metric_alert_export_service_pb2.RetryMetricAlertExportResponse:
        """Retrys a metric alert."""
        return await handle_retry_metric_alert_export(self.deps, request)

    @rpc_errors
    async def ScheduleMetricAlertExport(
        self, request: metrics_v1_metric_alert_export_service_pb2.ScheduleMetricAlertExportRequest, context: grpc.aio.ServicerContext,
    ) -> metrics_v1_metric_alert_export_service_pb2.ScheduleMetricAlertExportResponse:
        """Schedules a metric alert."""
        return await handle_schedule_metric_alert_export(self.deps, request)

    @rpc_errors
    async def ShareMetricAlertExport(
        self, request: metrics_v1_metric_alert_export_service_pb2.ShareMetricAlertExportRequest, context: grpc.aio.ServicerContext,
    ) -> metrics_v1_metric_alert_export_service_pb2.ShareMetricAlertExportResponse:
        """Shares a metric alert."""
        return await handle_share_metric_alert_export(self.deps, request)

    @stream_errors
    async def StreamMetricAlertExport(
        self, request: metrics_v1_metric_alert_export_service_pb2.StreamMetricAlertExportRequest, context: grpc.aio.ServicerContext,
    ) -> AsyncIterator[metrics_v1_metric_alert_export_service_pb2.StreamMetricAlertExportResponse]:
        """Streams every matching metric alert."""
        response = await handle_stream_metric_alert_export(self.deps, request)
        for item in messages((response,)):
            yield item
