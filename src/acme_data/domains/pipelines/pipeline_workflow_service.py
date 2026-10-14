"""Runs the long-lived workflow that takes a pipeline from start to finish."""

from __future__ import annotations

from collections.abc import AsyncIterator

import grpc

from acme.pipelines.v1 import pipeline_workflow_service_pb2 as pipelines_v1_pipeline_workflow_service_pb2
from acme.pipelines.v1 import pipeline_workflow_service_pb2_grpc as pipelines_v1_pipeline_workflow_service_pb2_grpc

from acme_data.domains.pipelines.dependencies import Dependencies
from acme_data.domains.pipelines.pipeline_workflow_service_workflow import PipelineWorkflowServicerWorkflow
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors


class PipelineWorkflowServicer(pipelines_v1_pipeline_workflow_service_pb2_grpc.PipelineWorkflowServiceServicer):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps
        self.workflow = PipelineWorkflowServicerWorkflow(deps)

    @rpc_errors
    async def AdvancePipelineWorkflow(
        self, request: pipelines_v1_pipeline_workflow_service_pb2.AdvancePipelineWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_workflow_service_pb2.AdvancePipelineWorkflowResponse:
        """Advances a pipeline."""
        return await self.workflow.handle_advance_pipeline_workflow(request)

    @rpc_errors
    async def CancelPipelineWorkflow(
        self, request: pipelines_v1_pipeline_workflow_service_pb2.CancelPipelineWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_workflow_service_pb2.CancelPipelineWorkflowResponse:
        """Cancels a pipeline."""
        return await self.workflow.handle_cancel_pipeline_workflow(request)

    @rpc_errors
    @retry_transient
    async def InspectPipelineWorkflow(
        self, request: pipelines_v1_pipeline_workflow_service_pb2.InspectPipelineWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_workflow_service_pb2.InspectPipelineWorkflowResponse:
        """Returns a pipeline."""
        return await self.workflow.handle_inspect_pipeline_workflow(request)

    @rpc_errors
    @retry_transient
    async def ListPipelineWorkflows(
        self, request: pipelines_v1_pipeline_workflow_service_pb2.ListPipelineWorkflowsRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_workflow_service_pb2.ListPipelineWorkflowsResponse:
        """Lists pipelines a page at a time."""
        return await self.workflow.handle_list_pipeline_workflows(request)

    @rpc_errors
    async def PausePipelineWorkflow(
        self, request: pipelines_v1_pipeline_workflow_service_pb2.PausePipelineWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_workflow_service_pb2.PausePipelineWorkflowResponse:
        """Pauses a pipeline."""
        return await self.workflow.handle_pause_pipeline_workflow(request)

    @rpc_errors
    async def ResumePipelineWorkflow(
        self, request: pipelines_v1_pipeline_workflow_service_pb2.ResumePipelineWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_workflow_service_pb2.ResumePipelineWorkflowResponse:
        """Resumes a pipeline."""
        return await self.workflow.handle_resume_pipeline_workflow(request)

    @rpc_errors
    async def RetryPipelineWorkflow(
        self, request: pipelines_v1_pipeline_workflow_service_pb2.RetryPipelineWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_workflow_service_pb2.RetryPipelineWorkflowResponse:
        """Retrys a pipeline."""
        return await self.workflow.handle_retry_pipeline_workflow(request)

    @rpc_errors
    async def SignalPipelineWorkflow(
        self, request: pipelines_v1_pipeline_workflow_service_pb2.SignalPipelineWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_workflow_service_pb2.SignalPipelineWorkflowResponse:
        """Signals a pipeline."""
        return await self.workflow.handle_signal_pipeline_workflow(request)

    @rpc_errors
    async def StartPipelineWorkflow(
        self, request: pipelines_v1_pipeline_workflow_service_pb2.StartPipelineWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_workflow_service_pb2.StartPipelineWorkflowResponse:
        """Starts a pipeline."""
        return await self.workflow.handle_start_pipeline_workflow(request)
