"""Runs the long-lived workflow that takes a label set from start to finish."""

from __future__ import annotations

from collections.abc import AsyncIterator

import grpc

from acme.labeling.v1 import label_set_workflow_service_pb2_grpc as labeling_v1_label_set_workflow_service_pb2_grpc

from acme_data.domains.labeling.dependencies import Dependencies
from acme_data.domains.labeling.label_set_workflow_service_handlers import LabelSetWorkflowServicerHandlers
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors


class LabelSetWorkflowServicer(
    LabelSetWorkflowServicerHandlers,
    labeling_v1_label_set_workflow_service_pb2_grpc.LabelSetWorkflowServiceServicer
):
    """Runs the long-lived workflow that takes a label set from start to finish."""
