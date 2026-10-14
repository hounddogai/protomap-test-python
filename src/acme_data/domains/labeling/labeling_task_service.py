"""Manages labeling tasks: creates, reads, changes, and lists them."""

from __future__ import annotations

from collections.abc import AsyncIterator

import grpc

from acme.labeling.v1 import labeling_task_service_pb2_grpc as labeling_v1_labeling_task_service_pb2_grpc

from acme_data.domains.labeling.dependencies import Dependencies
from acme_data.domains.labeling.labeling_task_service_handlers import LabelingTaskServicerHandlers
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors


class LabelingTaskServicer(
    LabelingTaskServicerHandlers,
    labeling_v1_labeling_task_service_pb2_grpc.LabelingTaskServiceServicer
):
    """Manages labeling tasks: creates, reads, changes, and lists them."""
