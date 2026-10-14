"""Runs the long-lived workflow that takes an anomaly from start to finish."""

from __future__ import annotations

from collections.abc import AsyncIterator

import grpc

from acme.anomalies.v1 import anomaly_workflow_service_pb2_grpc as anomalies_v1_anomaly_workflow_service_pb2_grpc

from acme_data.domains.anomalies.anomaly_workflow_service_handlers import AnomalyWorkflowServicerHandlers
from acme_data.domains.anomalies.dependencies import Dependencies
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors


class AnomalyWorkflowServicer(
    AnomalyWorkflowServicerHandlers,
    anomalies_v1_anomaly_workflow_service_pb2_grpc.AnomalyWorkflowServiceServicer
):
    """Runs the long-lived workflow that takes an anomaly from start to finish."""
