"""Runs the long-lived workflow that takes a workspace from start to finish."""

from __future__ import annotations

from collections.abc import AsyncIterator

import grpc

from acme.datahub.v1 import workspace_workflow_service_pb2 as datahub_v1_workspace_workflow_service_pb2
from acme.datahub.v1 import workspace_workflow_service_pb2_grpc as datahub_v1_workspace_workflow_service_pb2_grpc

from acme_data.domains.datahub.dependencies import Dependencies
from acme_data.domains.datahub.workspace_workflow_service_workflow import WorkspaceWorkflowServicerWorkflow
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors


class WorkspaceWorkflowServicer(datahub_v1_workspace_workflow_service_pb2_grpc.WorkspaceWorkflowServiceServicer):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps
        self.workflow = WorkspaceWorkflowServicerWorkflow(deps)

    @rpc_errors
    async def AdvanceWorkspaceWorkflow(
        self, request: datahub_v1_workspace_workflow_service_pb2.AdvanceWorkspaceWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_workspace_workflow_service_pb2.AdvanceWorkspaceWorkflowResponse:
        """Advances a workspace."""
        return await self.workflow.handle_advance_workspace_workflow(request)

    @rpc_errors
    async def CancelWorkspaceWorkflow(
        self, request: datahub_v1_workspace_workflow_service_pb2.CancelWorkspaceWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_workspace_workflow_service_pb2.CancelWorkspaceWorkflowResponse:
        """Cancels a workspace."""
        return await self.workflow.handle_cancel_workspace_workflow(request)

    @rpc_errors
    @retry_transient
    async def InspectWorkspaceWorkflow(
        self, request: datahub_v1_workspace_workflow_service_pb2.InspectWorkspaceWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_workspace_workflow_service_pb2.InspectWorkspaceWorkflowResponse:
        """Returns a workspace."""
        return await self.workflow.handle_inspect_workspace_workflow(request)

    @rpc_errors
    @retry_transient
    async def ListWorkspaceWorkflows(
        self, request: datahub_v1_workspace_workflow_service_pb2.ListWorkspaceWorkflowsRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_workspace_workflow_service_pb2.ListWorkspaceWorkflowsResponse:
        """Lists workspaces a page at a time."""
        return await self.workflow.handle_list_workspace_workflows(request)

    @rpc_errors
    async def PauseWorkspaceWorkflow(
        self, request: datahub_v1_workspace_workflow_service_pb2.PauseWorkspaceWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_workspace_workflow_service_pb2.PauseWorkspaceWorkflowResponse:
        """Pauses a workspace."""
        return await self.workflow.handle_pause_workspace_workflow(request)

    @rpc_errors
    async def ResumeWorkspaceWorkflow(
        self, request: datahub_v1_workspace_workflow_service_pb2.ResumeWorkspaceWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_workspace_workflow_service_pb2.ResumeWorkspaceWorkflowResponse:
        """Resumes a workspace."""
        return await self.workflow.handle_resume_workspace_workflow(request)

    @rpc_errors
    async def RetryWorkspaceWorkflow(
        self, request: datahub_v1_workspace_workflow_service_pb2.RetryWorkspaceWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_workspace_workflow_service_pb2.RetryWorkspaceWorkflowResponse:
        """Retrys a workspace."""
        return await self.workflow.handle_retry_workspace_workflow(request)

    @rpc_errors
    async def SignalWorkspaceWorkflow(
        self, request: datahub_v1_workspace_workflow_service_pb2.SignalWorkspaceWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_workspace_workflow_service_pb2.SignalWorkspaceWorkflowResponse:
        """Signals a workspace."""
        return await self.workflow.handle_signal_workspace_workflow(request)

    @rpc_errors
    async def StartWorkspaceWorkflow(
        self, request: datahub_v1_workspace_workflow_service_pb2.StartWorkspaceWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_workspace_workflow_service_pb2.StartWorkspaceWorkflowResponse:
        """Starts a workspace."""
        return await self.workflow.handle_start_workspace_workflow(request)
