"""Takes pipeline runs in bulk from partners and legacy systems."""

from __future__ import annotations

from collections.abc import AsyncIterator

import grpc

from acme.pipelines.v1 import pipeline_run_import_service_pb2 as pipelines_v1_pipeline_run_import_service_pb2
from acme.pipelines.v1 import pipeline_run_import_service_pb2_grpc as pipelines_v1_pipeline_run_import_service_pb2_grpc

from acme_data.domains.pipelines.dependencies import Dependencies
from acme_data.domains.pipelines.pipeline_run_import_service_operations import handle_cancel_pipeline_run_import
from acme_data.domains.pipelines.pipeline_run_import_service_operations import handle_get_pipeline_run_import_status
from acme_data.domains.pipelines.pipeline_run_import_service_operations import handle_import_pipeline_runs
from acme_data.domains.pipelines.pipeline_run_import_service_operations import handle_list_pipeline_run_imports
from acme_data.domains.pipelines.pipeline_run_import_service_operations import handle_map_pipeline_run_import_columns
from acme_data.domains.pipelines.pipeline_run_import_service_operations import handle_retry_pipeline_run_import
from acme_data.domains.pipelines.pipeline_run_import_service_operations import handle_validate_pipeline_run_import
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors


class PipelineRunImportServicer(pipelines_v1_pipeline_run_import_service_pb2_grpc.PipelineRunImportServiceServicer):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    async def CancelPipelineRunImport(
        self, request: pipelines_v1_pipeline_run_import_service_pb2.CancelPipelineRunImportRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_run_import_service_pb2.CancelPipelineRunImportResponse:
        """Cancels a pipeline run."""
        return await handle_cancel_pipeline_run_import(self.deps, request)

    @rpc_errors
    @retry_transient
    async def GetPipelineRunImportStatus(
        self, request: pipelines_v1_pipeline_run_import_service_pb2.GetPipelineRunImportStatusRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_run_import_service_pb2.GetPipelineRunImportStatusResponse:
        """Returns a pipeline run."""
        return await handle_get_pipeline_run_import_status(self.deps, request)

    @rpc_errors
    async def ImportPipelineRuns(
        self, requests: AsyncIterator[
            pipelines_v1_pipeline_run_import_service_pb2.ImportPipelineRunsRequest
        ], context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_run_import_service_pb2.ImportPipelineRunsResponse:
        """Takes a stream of pipeline runs and answers once at the end."""
        response = pipelines_v1_pipeline_run_import_service_pb2.ImportPipelineRunsResponse()
        async for request in requests:
            response.MergeFrom(await handle_import_pipeline_runs(self.deps, request))
        return response

    @rpc_errors
    @retry_transient
    async def ListPipelineRunImports(
        self, request: pipelines_v1_pipeline_run_import_service_pb2.ListPipelineRunImportsRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_run_import_service_pb2.ListPipelineRunImportsResponse:
        """Lists pipeline runs a page at a time."""
        return await handle_list_pipeline_run_imports(self.deps, request)

    @rpc_errors
    async def MapPipelineRunImportColumns(
        self, request: pipelines_v1_pipeline_run_import_service_pb2.MapPipelineRunImportColumnsRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_run_import_service_pb2.MapPipelineRunImportColumnsResponse:
        """Maps a pipeline run."""
        return await handle_map_pipeline_run_import_columns(self.deps, request)

    @rpc_errors
    async def RetryPipelineRunImport(
        self, request: pipelines_v1_pipeline_run_import_service_pb2.RetryPipelineRunImportRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_run_import_service_pb2.RetryPipelineRunImportResponse:
        """Retrys a pipeline run."""
        return await handle_retry_pipeline_run_import(self.deps, request)

    @rpc_errors
    async def ValidatePipelineRunImport(
        self, request: pipelines_v1_pipeline_run_import_service_pb2.ValidatePipelineRunImportRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_run_import_service_pb2.ValidatePipelineRunImportResponse:
        """Validates a pipeline run."""
        return await handle_validate_pipeline_run_import(self.deps, request)
