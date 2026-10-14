"""Checks anomaly feedbacks against the rules before anything acts on them."""

from __future__ import annotations

from collections.abc import AsyncIterator

import grpc

from acme.anomalies.v1 import (
    anomaly_feedback_validation_service_pb2_grpc as anomalies_v1_anomaly_feedback_validation_service_pb2_grpc,
)

from acme_data.domains.anomalies.anomaly_feedback_validation_service_handlers import (
    AnomalyFeedbackValidationServicerHandlers,
)
from acme_data.domains.anomalies.dependencies import Dependencies
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors


class AnomalyFeedbackValidationServicer(
    AnomalyFeedbackValidationServicerHandlers,
    anomalies_v1_anomaly_feedback_validation_service_pb2_grpc.AnomalyFeedbackValidationServiceServicer
):
    """Checks anomaly feedbacks against the rules before anything acts on them."""
