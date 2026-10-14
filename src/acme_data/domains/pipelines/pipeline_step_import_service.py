"""Takes pipeline steps in bulk from partners and legacy systems."""

from __future__ import annotations

from collections.abc import AsyncIterator

import grpc

from acme.pipelines.v1 import (
    pipeline_step_import_service_pb2_grpc as pipelines_v1_pipeline_step_import_service_pb2_grpc,
)

from acme_data.domains.pipelines.dependencies import Dependencies
from acme_data.domains.pipelines.pipeline_step_import_service_handlers import PipelineStepImportServicerHandlers
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors


class PipelineStepImportServicer(
    PipelineStepImportServicerHandlers,
    pipelines_v1_pipeline_step_import_service_pb2_grpc.PipelineStepImportServiceServicer
):
    """Takes pipeline steps in bulk from partners and legacy systems."""
