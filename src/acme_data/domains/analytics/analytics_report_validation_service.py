"""Checks analytics reports against the rules before anything acts on them."""

from __future__ import annotations

from collections.abc import AsyncIterator

import grpc

from acme.analytics.v1 import (
    analytics_report_validation_service_pb2_grpc as analytics_v1_analytics_report_validation_service_pb2_grpc,
)

from acme_data.domains.analytics.analytics_report_validation_service_handlers import (
    AnalyticsReportValidationServicerHandlers,
)
from acme_data.domains.analytics.dependencies import Dependencies
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors


class AnalyticsReportValidationServicer(
    AnalyticsReportValidationServicerHandlers,
    analytics_v1_analytics_report_validation_service_pb2_grpc.AnalyticsReportValidationServiceServicer
):
    """Checks analytics reports against the rules before anything acts on them."""
