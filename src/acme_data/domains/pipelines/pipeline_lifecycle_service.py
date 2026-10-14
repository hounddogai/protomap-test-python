"""Moves a pipeline between the states of its lifecycle."""

from __future__ import annotations

from collections.abc import AsyncIterator

import grpc

from acme.pipelines.v1 import pipeline_lifecycle_service_pb2 as pipelines_v1_pipeline_lifecycle_service_pb2
from acme.pipelines.v1 import pipeline_lifecycle_service_pb2_grpc as pipelines_v1_pipeline_lifecycle_service_pb2_grpc

from acme_data.domains.pipelines.dependencies import Dependencies
from acme_data.domains.pipelines.pipeline_lifecycle_service_operations import handle_activate_pipeline
from acme_data.domains.pipelines.pipeline_lifecycle_service_operations import handle_expire_pipeline
from acme_data.domains.pipelines.pipeline_lifecycle_service_operations import handle_get_pipeline_lifecycle
from acme_data.domains.pipelines.pipeline_lifecycle_service_operations import handle_renew_pipeline
from acme_data.domains.pipelines.pipeline_lifecycle_service_operations import handle_schedule_pipeline_expiry
from acme_data.domains.pipelines.pipeline_lifecycle_service_operations import handle_suspend_pipeline
from acme_data.domains.pipelines.pipeline_lifecycle_service_operations import handle_terminate_pipeline
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors


class PipelineLifecycleServicer(pipelines_v1_pipeline_lifecycle_service_pb2_grpc.PipelineLifecycleServiceServicer):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    async def ActivatePipeline(
        self, request: pipelines_v1_pipeline_lifecycle_service_pb2.ActivatePipelineRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_lifecycle_service_pb2.ActivatePipelineResponse:
        """Activates a pipeline."""
        return await handle_activate_pipeline(self.deps, request)

    @rpc_errors
    async def ExpirePipeline(
        self, request: pipelines_v1_pipeline_lifecycle_service_pb2.ExpirePipelineRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_lifecycle_service_pb2.ExpirePipelineResponse:
        """Expires a pipeline."""
        return await handle_expire_pipeline(self.deps, request)

    @rpc_errors
    @retry_transient
    async def GetPipelineLifecycle(
        self, request: pipelines_v1_pipeline_lifecycle_service_pb2.GetPipelineLifecycleRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_lifecycle_service_pb2.GetPipelineLifecycleResponse:
        """Returns a pipeline."""
        return await handle_get_pipeline_lifecycle(self.deps, request)

    @rpc_errors
    async def RenewPipeline(
        self, request: pipelines_v1_pipeline_lifecycle_service_pb2.RenewPipelineRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_lifecycle_service_pb2.RenewPipelineResponse:
        """Renews a pipeline."""
        return await handle_renew_pipeline(self.deps, request)

    @rpc_errors
    async def SchedulePipelineExpiry(
        self, request: pipelines_v1_pipeline_lifecycle_service_pb2.SchedulePipelineExpiryRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_lifecycle_service_pb2.SchedulePipelineExpiryResponse:
        """Schedules a pipeline."""
        return await handle_schedule_pipeline_expiry(self.deps, request)

    @rpc_errors
    async def SuspendPipeline(
        self, request: pipelines_v1_pipeline_lifecycle_service_pb2.SuspendPipelineRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_lifecycle_service_pb2.SuspendPipelineResponse:
        """Suspends a pipeline."""
        return await handle_suspend_pipeline(self.deps, request)

    @rpc_errors
    async def TerminatePipeline(
        self, request: pipelines_v1_pipeline_lifecycle_service_pb2.TerminatePipelineRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_lifecycle_service_pb2.TerminatePipelineResponse:
        """Terminates a pipeline."""
        return await handle_terminate_pipeline(self.deps, request)
