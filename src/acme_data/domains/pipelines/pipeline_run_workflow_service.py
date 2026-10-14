"""Runs the long-lived workflow that takes a pipeline run from start to finish."""

from __future__ import annotations

from collections.abc import AsyncIterator

import grpc

from acme.pipelines.v1 import (
    pipeline_run_workflow_service_pb2_grpc as pipelines_v1_pipeline_run_workflow_service_pb2_grpc,
)

from acme_data.domains.pipelines.dependencies import Dependencies
from acme_data.domains.pipelines.pipeline_run_workflow_service_handlers import PipelineRunWorkflowServicerHandlers
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors


class PipelineRunWorkflowServicer(
    PipelineRunWorkflowServicerHandlers,
    pipelines_v1_pipeline_run_workflow_service_pb2_grpc.PipelineRunWorkflowServiceServicer
):
    """Runs the long-lived workflow that takes a pipeline run from start to finish."""
