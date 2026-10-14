"""Moves a pipeline run between the states of its lifecycle."""

from __future__ import annotations

from collections.abc import AsyncIterator

import grpc

from acme.pipelines.v1 import (
    pipeline_run_lifecycle_service_pb2_grpc as pipelines_v1_pipeline_run_lifecycle_service_pb2_grpc,
)

from acme_data.domains.pipelines.dependencies import Dependencies
from acme_data.domains.pipelines.pipeline_run_lifecycle_service_handlers import PipelineRunLifecycleServicerHandlers
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors


class PipelineRunLifecycleServicer(
    PipelineRunLifecycleServicerHandlers,
    pipelines_v1_pipeline_run_lifecycle_service_pb2_grpc.PipelineRunLifecycleServiceServicer
):
    """Moves a pipeline run between the states of its lifecycle."""
