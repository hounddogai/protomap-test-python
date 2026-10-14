"""Answers read-only questions about pipelines, for screens and reports."""

from __future__ import annotations

from collections.abc import AsyncIterator

import grpc

from acme.pipelines.v1 import pipeline_query_service_pb2_grpc as pipelines_v1_pipeline_query_service_pb2_grpc

from acme_data.domains.pipelines.dependencies import Dependencies
from acme_data.domains.pipelines.pipeline_query_service_handlers import PipelineQueryServicerHandlers
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors


class PipelineQueryServicer(
    PipelineQueryServicerHandlers,
    pipelines_v1_pipeline_query_service_pb2_grpc.PipelineQueryServiceServicer
):
    """Answers read-only questions about pipelines, for screens and reports."""
