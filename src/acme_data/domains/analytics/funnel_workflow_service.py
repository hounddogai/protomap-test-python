"""Runs the long-lived workflow that takes a funnel from start to finish."""

from __future__ import annotations

from collections.abc import AsyncIterator

import grpc

from acme.analytics.v1 import funnel_workflow_service_pb2_grpc as analytics_v1_funnel_workflow_service_pb2_grpc

from acme_data.domains.analytics.dependencies import Dependencies
from acme_data.domains.analytics.funnel_workflow_service_handlers import FunnelWorkflowServicerHandlers
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors


class FunnelWorkflowServicer(
    FunnelWorkflowServicerHandlers,
    analytics_v1_funnel_workflow_service_pb2_grpc.FunnelWorkflowServiceServicer
):
    """Runs the long-lived workflow that takes a funnel from start to finish."""
