"""Exports pipeline steps to files and other systems."""

from __future__ import annotations

from collections.abc import AsyncIterator

import grpc

from acme.pipelines.v1 import pipeline_step_export_service_pb2 as pipelines_v1_pipeline_step_export_service_pb2
from acme.pipelines.v1 import (
    pipeline_step_export_service_pb2_grpc as pipelines_v1_pipeline_step_export_service_pb2_grpc,
)

from acme_data.domains.pipelines.dependencies import Dependencies
from acme_data.domains.pipelines.pipeline_step_export_service_operations import handle_cancel_pipeline_step_export
from acme_data.domains.pipelines.pipeline_step_export_service_operations import handle_get_pipeline_step_export
from acme_data.domains.pipelines.pipeline_step_export_service_operations import handle_list_pipeline_step_exports
from acme_data.domains.pipelines.pipeline_step_export_service_operations import handle_retry_pipeline_step_export
from acme_data.domains.pipelines.pipeline_step_export_service_operations import handle_schedule_pipeline_step_export
from acme_data.domains.pipelines.pipeline_step_export_service_operations import handle_share_pipeline_step_export
from acme_data.domains.pipelines.pipeline_step_export_service_operations import handle_stream_pipeline_step_export
from acme_data.platform.rpc import messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors


class PipelineStepExportServicer(pipelines_v1_pipeline_step_export_service_pb2_grpc.PipelineStepExportServiceServicer):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    async def CancelPipelineStepExport(
        self, request: pipelines_v1_pipeline_step_export_service_pb2.CancelPipelineStepExportRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_step_export_service_pb2.CancelPipelineStepExportResponse:
        """Cancels a pipeline step."""
        return await handle_cancel_pipeline_step_export(self.deps, request)

    @rpc_errors
    @retry_transient
    async def GetPipelineStepExport(
        self, request: pipelines_v1_pipeline_step_export_service_pb2.GetPipelineStepExportRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_step_export_service_pb2.GetPipelineStepExportResponse:
        """Returns a pipeline step."""
        return await handle_get_pipeline_step_export(self.deps, request)

    @rpc_errors
    @retry_transient
    async def ListPipelineStepExports(
        self, request: pipelines_v1_pipeline_step_export_service_pb2.ListPipelineStepExportsRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_step_export_service_pb2.ListPipelineStepExportsResponse:
        """Lists pipeline steps a page at a time."""
        return await handle_list_pipeline_step_exports(self.deps, request)

    @rpc_errors
    async def RetryPipelineStepExport(
        self, request: pipelines_v1_pipeline_step_export_service_pb2.RetryPipelineStepExportRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_step_export_service_pb2.RetryPipelineStepExportResponse:
        """Retrys a pipeline step."""
        return await handle_retry_pipeline_step_export(self.deps, request)

    @rpc_errors
    async def SchedulePipelineStepExport(
        self, request: pipelines_v1_pipeline_step_export_service_pb2.SchedulePipelineStepExportRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_step_export_service_pb2.SchedulePipelineStepExportResponse:
        """Schedules a pipeline step."""
        return await handle_schedule_pipeline_step_export(self.deps, request)

    @rpc_errors
    async def SharePipelineStepExport(
        self, request: pipelines_v1_pipeline_step_export_service_pb2.SharePipelineStepExportRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_step_export_service_pb2.SharePipelineStepExportResponse:
        """Shares a pipeline step."""
        return await handle_share_pipeline_step_export(self.deps, request)

    @stream_errors
    async def StreamPipelineStepExport(
        self, request: pipelines_v1_pipeline_step_export_service_pb2.StreamPipelineStepExportRequest, context: grpc.aio.ServicerContext,
    ) -> AsyncIterator[pipelines_v1_pipeline_step_export_service_pb2.StreamPipelineStepExportResponse]:
        """Streams every matching pipeline step."""
        response = await handle_stream_pipeline_step_export(self.deps, request)
        for item in messages((response,)):
            yield item
