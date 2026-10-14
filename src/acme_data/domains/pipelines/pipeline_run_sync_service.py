"""Keeps pipeline runs in step with the systems of record in other regions."""

from __future__ import annotations

from collections.abc import AsyncIterator

import grpc

from acme.pipelines.v1 import pipeline_run_sync_service_pb2 as pipelines_v1_pipeline_run_sync_service_pb2
from acme.pipelines.v1 import pipeline_run_sync_service_pb2_grpc as pipelines_v1_pipeline_run_sync_service_pb2_grpc

from acme_data.domains.pipelines.dependencies import Dependencies
from acme_data.domains.pipelines.pipeline_run_sync_service_workflow import PipelineRunSyncServicerWorkflow
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors


class PipelineRunSyncServicer(pipelines_v1_pipeline_run_sync_service_pb2_grpc.PipelineRunSyncServiceServicer):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps
        self.workflow = PipelineRunSyncServicerWorkflow(deps)

    @rpc_errors
    @retry_transient
    async def GetPipelineRunSyncState(
        self, request: pipelines_v1_pipeline_run_sync_service_pb2.GetPipelineRunSyncStateRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_run_sync_service_pb2.GetPipelineRunSyncStateResponse:
        """Returns a pipeline run."""
        return await self.workflow.handle_get_pipeline_run_sync_state(request)

    @rpc_errors
    @retry_transient
    async def ListPipelineRunConflicts(
        self, request: pipelines_v1_pipeline_run_sync_service_pb2.ListPipelineRunConflictsRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_run_sync_service_pb2.ListPipelineRunConflictsResponse:
        """Lists pipeline runs a page at a time."""
        return await self.workflow.handle_list_pipeline_run_conflicts(request)

    @rpc_errors
    async def PushPipelineRun(
        self, request: pipelines_v1_pipeline_run_sync_service_pb2.PushPipelineRunRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_run_sync_service_pb2.PushPipelineRunResponse:
        """Pushs a pipeline run."""
        return await self.workflow.handle_push_pipeline_run(request)

    @rpc_errors
    async def ReconcilePipelineRuns(
        self, request: pipelines_v1_pipeline_run_sync_service_pb2.ReconcilePipelineRunsRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_run_sync_service_pb2.ReconcilePipelineRunsResponse:
        """Reconciles a pipeline run."""
        return await self.workflow.handle_reconcile_pipeline_runs(request)

    @rpc_errors
    async def ResolvePipelineRunConflict(
        self, request: pipelines_v1_pipeline_run_sync_service_pb2.ResolvePipelineRunConflictRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_run_sync_service_pb2.ResolvePipelineRunConflictResponse:
        """Resolves a pipeline run."""
        return await self.workflow.handle_resolve_pipeline_run_conflict(request)

    @stream_errors
    async def StreamPipelineRunChanges(
        self, requests: AsyncIterator[
            pipelines_v1_pipeline_run_sync_service_pb2.StreamPipelineRunChangesRequest
        ], context: grpc.aio.ServicerContext,
    ) -> AsyncIterator[pipelines_v1_pipeline_run_sync_service_pb2.StreamPipelineRunChangesResponse]:
        """Exchanges changes of pipeline runs with a peer."""
        async for request in requests:
            yield await self.workflow.handle_stream_pipeline_run_changes(request)

    @rpc_errors
    async def SyncPipelineRuns(
        self, request: pipelines_v1_pipeline_run_sync_service_pb2.SyncPipelineRunsRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_run_sync_service_pb2.SyncPipelineRunsResponse:
        """Syncs a pipeline run."""
        return await self.workflow.handle_sync_pipeline_runs(request)
