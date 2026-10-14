"""Exports metric serieses to files and other systems."""

from __future__ import annotations

from collections.abc import AsyncIterator

import grpc

from acme.metrics.v1 import metric_series_export_service_pb2_grpc as metrics_v1_metric_series_export_service_pb2_grpc

from acme_data.domains.metrics.dependencies import Dependencies
from acme_data.domains.metrics.metric_series_export_service_handlers import MetricSeriesExportServicerHandlers
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors


class MetricSeriesExportServicer(
    MetricSeriesExportServicerHandlers,
    metrics_v1_metric_series_export_service_pb2_grpc.MetricSeriesExportServiceServicer
):
    """Exports metric serieses to files and other systems."""
