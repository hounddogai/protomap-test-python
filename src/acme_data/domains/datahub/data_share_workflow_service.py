"""Runs the long-lived workflow that takes a data share from start to finish."""

from __future__ import annotations

from collections.abc import AsyncIterator

import grpc

from acme.datahub.v1 import data_share_workflow_service_pb2 as datahub_v1_data_share_workflow_service_pb2
from acme.datahub.v1 import data_share_workflow_service_pb2_grpc as datahub_v1_data_share_workflow_service_pb2_grpc

from acme_data.domains.datahub.data_share_workflow_service_workflow import DataShareWorkflowServicerWorkflow
from acme_data.domains.datahub.dependencies import Dependencies
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors


class DataShareWorkflowServicer(datahub_v1_data_share_workflow_service_pb2_grpc.DataShareWorkflowServiceServicer):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps
        self.workflow = DataShareWorkflowServicerWorkflow(deps)

    @rpc_errors
    async def AdvanceDataShareWorkflow(
        self, request: datahub_v1_data_share_workflow_service_pb2.AdvanceDataShareWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_data_share_workflow_service_pb2.AdvanceDataShareWorkflowResponse:
        """Advances a data share."""
        return await self.workflow.handle_advance_data_share_workflow(request)

    @rpc_errors
    async def CancelDataShareWorkflow(
        self, request: datahub_v1_data_share_workflow_service_pb2.CancelDataShareWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_data_share_workflow_service_pb2.CancelDataShareWorkflowResponse:
        """Cancels a data share."""
        return await self.workflow.handle_cancel_data_share_workflow(request)

    @rpc_errors
    @retry_transient
    async def InspectDataShareWorkflow(
        self, request: datahub_v1_data_share_workflow_service_pb2.InspectDataShareWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_data_share_workflow_service_pb2.InspectDataShareWorkflowResponse:
        """Returns a data share."""
        return await self.workflow.handle_inspect_data_share_workflow(request)

    @rpc_errors
    @retry_transient
    async def ListDataShareWorkflows(
        self, request: datahub_v1_data_share_workflow_service_pb2.ListDataShareWorkflowsRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_data_share_workflow_service_pb2.ListDataShareWorkflowsResponse:
        """Lists data shares a page at a time."""
        return await self.workflow.handle_list_data_share_workflows(request)

    @rpc_errors
    async def PauseDataShareWorkflow(
        self, request: datahub_v1_data_share_workflow_service_pb2.PauseDataShareWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_data_share_workflow_service_pb2.PauseDataShareWorkflowResponse:
        """Pauses a data share."""
        return await self.workflow.handle_pause_data_share_workflow(request)

    @rpc_errors
    async def ResumeDataShareWorkflow(
        self, request: datahub_v1_data_share_workflow_service_pb2.ResumeDataShareWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_data_share_workflow_service_pb2.ResumeDataShareWorkflowResponse:
        """Resumes a data share."""
        return await self.workflow.handle_resume_data_share_workflow(request)

    @rpc_errors
    async def RetryDataShareWorkflow(
        self, request: datahub_v1_data_share_workflow_service_pb2.RetryDataShareWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_data_share_workflow_service_pb2.RetryDataShareWorkflowResponse:
        """Retrys a data share."""
        return await self.workflow.handle_retry_data_share_workflow(request)

    @rpc_errors
    async def SignalDataShareWorkflow(
        self, request: datahub_v1_data_share_workflow_service_pb2.SignalDataShareWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_data_share_workflow_service_pb2.SignalDataShareWorkflowResponse:
        """Signals a data share."""
        return await self.workflow.handle_signal_data_share_workflow(request)

    @rpc_errors
    async def StartDataShareWorkflow(
        self, request: datahub_v1_data_share_workflow_service_pb2.StartDataShareWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_data_share_workflow_service_pb2.StartDataShareWorkflowResponse:
        """Starts a data share."""
        return await self.workflow.handle_start_data_share_workflow(request)
