"""Tells the people who follow a dashboard what changed."""

from __future__ import annotations

from collections.abc import AsyncIterator

import grpc

from acme.metrics.v1 import (
    dashboard_notification_service_pb2_grpc as metrics_v1_dashboard_notification_service_pb2_grpc,
)

from acme_data.domains.metrics.dashboard_notification_service_handlers import DashboardNotificationServicerHandlers
from acme_data.domains.metrics.dependencies import Dependencies
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors


class DashboardNotificationServicer(
    DashboardNotificationServicerHandlers,
    metrics_v1_dashboard_notification_service_pb2_grpc.DashboardNotificationServiceServicer
):
    """Tells the people who follow a dashboard what changed."""
