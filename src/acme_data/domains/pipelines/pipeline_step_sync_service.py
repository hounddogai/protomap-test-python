"""Keeps pipeline steps in step with the systems of record in other regions."""

from __future__ import annotations

from collections.abc import AsyncIterator

import grpc

from acme.pipelines.v1 import pipeline_step_sync_service_pb2 as pipelines_v1_pipeline_step_sync_service_pb2
from acme.pipelines.v1 import pipeline_step_sync_service_pb2_grpc as pipelines_v1_pipeline_step_sync_service_pb2_grpc

from acme_data.domains.pipelines.dependencies import Dependencies
from acme_data.domains.pipelines.pipeline_step_sync_service_workflow import PipelineStepSyncServicerWorkflow
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors


class PipelineStepSyncServicer(pipelines_v1_pipeline_step_sync_service_pb2_grpc.PipelineStepSyncServiceServicer):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps
        self.workflow = PipelineStepSyncServicerWorkflow(deps)

    @rpc_errors
    @retry_transient
    async def GetPipelineStepSyncState(
        self, request: pipelines_v1_pipeline_step_sync_service_pb2.GetPipelineStepSyncStateRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_step_sync_service_pb2.GetPipelineStepSyncStateResponse:
        """Returns a pipeline step."""
        return await self.workflow.handle_get_pipeline_step_sync_state(request)

    @rpc_errors
    async def PullPipelineSteps(
        self, request: pipelines_v1_pipeline_step_sync_service_pb2.PullPipelineStepsRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_step_sync_service_pb2.PullPipelineStepsResponse:
        """Pulls a pipeline step."""
        return await self.workflow.handle_pull_pipeline_steps(request)

    @rpc_errors
    async def PushPipelineStep(
        self, request: pipelines_v1_pipeline_step_sync_service_pb2.PushPipelineStepRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_step_sync_service_pb2.PushPipelineStepResponse:
        """Pushs a pipeline step."""
        return await self.workflow.handle_push_pipeline_step(request)

    @rpc_errors
    async def ReconcilePipelineSteps(
        self, request: pipelines_v1_pipeline_step_sync_service_pb2.ReconcilePipelineStepsRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_step_sync_service_pb2.ReconcilePipelineStepsResponse:
        """Reconciles a pipeline step."""
        return await self.workflow.handle_reconcile_pipeline_steps(request)

    @rpc_errors
    async def ResolvePipelineStepConflict(
        self, request: pipelines_v1_pipeline_step_sync_service_pb2.ResolvePipelineStepConflictRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_step_sync_service_pb2.ResolvePipelineStepConflictResponse:
        """Resolves a pipeline step."""
        return await self.workflow.handle_resolve_pipeline_step_conflict(request)

    @stream_errors
    async def StreamPipelineStepChanges(
        self, requests: AsyncIterator[
            pipelines_v1_pipeline_step_sync_service_pb2.StreamPipelineStepChangesRequest
        ], context: grpc.aio.ServicerContext,
    ) -> AsyncIterator[pipelines_v1_pipeline_step_sync_service_pb2.StreamPipelineStepChangesResponse]:
        """Exchanges changes of pipeline steps with a peer."""
        async for request in requests:
            yield await self.workflow.handle_stream_pipeline_step_changes(request)

    @rpc_errors
    async def SyncPipelineSteps(
        self, request: pipelines_v1_pipeline_step_sync_service_pb2.SyncPipelineStepsRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_step_sync_service_pb2.SyncPipelineStepsResponse:
        """Syncs a pipeline step."""
        return await self.workflow.handle_sync_pipeline_steps(request)
