"""Keeps every version of a metric alert and restores earlier ones."""

from __future__ import annotations

from collections.abc import AsyncIterator

import grpc

from acme.metrics.v1 import metric_alert_history_service_pb2_grpc as metrics_v1_metric_alert_history_service_pb2_grpc

from acme_data.domains.metrics.dependencies import Dependencies
from acme_data.domains.metrics.metric_alert_history_service_handlers import MetricAlertHistoryServicerHandlers
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors


class MetricAlertHistoryServicer(
    MetricAlertHistoryServicerHandlers,
    metrics_v1_metric_alert_history_service_pb2_grpc.MetricAlertHistoryServiceServicer
):
    """Keeps every version of a metric alert and restores earlier ones."""
