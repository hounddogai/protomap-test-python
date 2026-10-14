"""Checks metric serieses against the rules before anything acts on them."""

from __future__ import annotations

from collections.abc import AsyncIterator

import grpc

from acme.metrics.v1 import (
    metric_series_validation_service_pb2_grpc as metrics_v1_metric_series_validation_service_pb2_grpc,
)

from acme_data.domains.metrics.dependencies import Dependencies
from acme_data.domains.metrics.metric_series_validation_service_handlers import MetricSeriesValidationServicerHandlers
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors


class MetricSeriesValidationServicer(
    MetricSeriesValidationServicerHandlers,
    metrics_v1_metric_series_validation_service_pb2_grpc.MetricSeriesValidationServiceServicer
):
    """Checks metric serieses against the rules before anything acts on them."""
