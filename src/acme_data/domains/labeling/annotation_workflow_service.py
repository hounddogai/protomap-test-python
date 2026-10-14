"""Runs the long-lived workflow that takes an annotation from start to finish."""

from __future__ import annotations

from collections.abc import AsyncIterator

import grpc

from acme.labeling.v1 import annotation_workflow_service_pb2 as labeling_v1_annotation_workflow_service_pb2
from acme.labeling.v1 import annotation_workflow_service_pb2_grpc as labeling_v1_annotation_workflow_service_pb2_grpc

from acme_data.domains.labeling.annotation_workflow_service_workflow import AnnotationWorkflowServicerWorkflow
from acme_data.domains.labeling.dependencies import Dependencies
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors


class AnnotationWorkflowServicer(labeling_v1_annotation_workflow_service_pb2_grpc.AnnotationWorkflowServiceServicer):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps
        self.workflow = AnnotationWorkflowServicerWorkflow(deps)

    @rpc_errors
    async def AdvanceAnnotationWorkflow(
        self, request: labeling_v1_annotation_workflow_service_pb2.AdvanceAnnotationWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_annotation_workflow_service_pb2.AdvanceAnnotationWorkflowResponse:
        """Advances an annotation."""
        return await self.workflow.handle_advance_annotation_workflow(request)

    @rpc_errors
    async def CancelAnnotationWorkflow(
        self, request: labeling_v1_annotation_workflow_service_pb2.CancelAnnotationWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_annotation_workflow_service_pb2.CancelAnnotationWorkflowResponse:
        """Cancels an annotation."""
        return await self.workflow.handle_cancel_annotation_workflow(request)

    @rpc_errors
    @retry_transient
    async def InspectAnnotationWorkflow(
        self, request: labeling_v1_annotation_workflow_service_pb2.InspectAnnotationWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_annotation_workflow_service_pb2.InspectAnnotationWorkflowResponse:
        """Returns an annotation."""
        return await self.workflow.handle_inspect_annotation_workflow(request)

    @rpc_errors
    @retry_transient
    async def ListAnnotationWorkflows(
        self, request: labeling_v1_annotation_workflow_service_pb2.ListAnnotationWorkflowsRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_annotation_workflow_service_pb2.ListAnnotationWorkflowsResponse:
        """Lists annotations a page at a time."""
        return await self.workflow.handle_list_annotation_workflows(request)

    @rpc_errors
    async def PauseAnnotationWorkflow(
        self, request: labeling_v1_annotation_workflow_service_pb2.PauseAnnotationWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_annotation_workflow_service_pb2.PauseAnnotationWorkflowResponse:
        """Pauses an annotation."""
        return await self.workflow.handle_pause_annotation_workflow(request)

    @rpc_errors
    async def ResumeAnnotationWorkflow(
        self, request: labeling_v1_annotation_workflow_service_pb2.ResumeAnnotationWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_annotation_workflow_service_pb2.ResumeAnnotationWorkflowResponse:
        """Resumes an annotation."""
        return await self.workflow.handle_resume_annotation_workflow(request)

    @rpc_errors
    async def RetryAnnotationWorkflow(
        self, request: labeling_v1_annotation_workflow_service_pb2.RetryAnnotationWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_annotation_workflow_service_pb2.RetryAnnotationWorkflowResponse:
        """Retrys an annotation."""
        return await self.workflow.handle_retry_annotation_workflow(request)

    @rpc_errors
    async def SignalAnnotationWorkflow(
        self, request: labeling_v1_annotation_workflow_service_pb2.SignalAnnotationWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_annotation_workflow_service_pb2.SignalAnnotationWorkflowResponse:
        """Signals an annotation."""
        return await self.workflow.handle_signal_annotation_workflow(request)

    @rpc_errors
    async def StartAnnotationWorkflow(
        self, request: labeling_v1_annotation_workflow_service_pb2.StartAnnotationWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_annotation_workflow_service_pb2.StartAnnotationWorkflowResponse:
        """Starts an annotation."""
        return await self.workflow.handle_start_annotation_workflow(request)
