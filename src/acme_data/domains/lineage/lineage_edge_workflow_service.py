"""Runs the long-lived workflow that takes a lineage edge from start to finish."""

from __future__ import annotations

from collections.abc import AsyncIterator

import grpc

from acme.lineage.v1 import lineage_edge_workflow_service_pb2 as lineage_v1_lineage_edge_workflow_service_pb2
from acme.lineage.v1 import lineage_edge_workflow_service_pb2_grpc as lineage_v1_lineage_edge_workflow_service_pb2_grpc

from acme_data.domains.lineage.dependencies import Dependencies
from acme_data.domains.lineage.lineage_edge_workflow_service_workflow import LineageEdgeWorkflowServicerWorkflow
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors


class LineageEdgeWorkflowServicer(lineage_v1_lineage_edge_workflow_service_pb2_grpc.LineageEdgeWorkflowServiceServicer):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps
        self.workflow = LineageEdgeWorkflowServicerWorkflow(deps)

    @rpc_errors
    async def AdvanceLineageEdgeWorkflow(
        self, request: lineage_v1_lineage_edge_workflow_service_pb2.AdvanceLineageEdgeWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_lineage_edge_workflow_service_pb2.AdvanceLineageEdgeWorkflowResponse:
        """Advances a lineage edge."""
        return await self.workflow.handle_advance_lineage_edge_workflow(request)

    @rpc_errors
    async def CancelLineageEdgeWorkflow(
        self, request: lineage_v1_lineage_edge_workflow_service_pb2.CancelLineageEdgeWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_lineage_edge_workflow_service_pb2.CancelLineageEdgeWorkflowResponse:
        """Cancels a lineage edge."""
        return await self.workflow.handle_cancel_lineage_edge_workflow(request)

    @rpc_errors
    @retry_transient
    async def InspectLineageEdgeWorkflow(
        self, request: lineage_v1_lineage_edge_workflow_service_pb2.InspectLineageEdgeWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_lineage_edge_workflow_service_pb2.InspectLineageEdgeWorkflowResponse:
        """Returns a lineage edge."""
        return await self.workflow.handle_inspect_lineage_edge_workflow(request)

    @rpc_errors
    @retry_transient
    async def ListLineageEdgeWorkflows(
        self, request: lineage_v1_lineage_edge_workflow_service_pb2.ListLineageEdgeWorkflowsRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_lineage_edge_workflow_service_pb2.ListLineageEdgeWorkflowsResponse:
        """Lists lineage edges a page at a time."""
        return await self.workflow.handle_list_lineage_edge_workflows(request)

    @rpc_errors
    async def PauseLineageEdgeWorkflow(
        self, request: lineage_v1_lineage_edge_workflow_service_pb2.PauseLineageEdgeWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_lineage_edge_workflow_service_pb2.PauseLineageEdgeWorkflowResponse:
        """Pauses a lineage edge."""
        return await self.workflow.handle_pause_lineage_edge_workflow(request)

    @rpc_errors
    async def ResumeLineageEdgeWorkflow(
        self, request: lineage_v1_lineage_edge_workflow_service_pb2.ResumeLineageEdgeWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_lineage_edge_workflow_service_pb2.ResumeLineageEdgeWorkflowResponse:
        """Resumes a lineage edge."""
        return await self.workflow.handle_resume_lineage_edge_workflow(request)

    @rpc_errors
    async def RetryLineageEdgeWorkflow(
        self, request: lineage_v1_lineage_edge_workflow_service_pb2.RetryLineageEdgeWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_lineage_edge_workflow_service_pb2.RetryLineageEdgeWorkflowResponse:
        """Retrys a lineage edge."""
        return await self.workflow.handle_retry_lineage_edge_workflow(request)

    @rpc_errors
    async def SignalLineageEdgeWorkflow(
        self, request: lineage_v1_lineage_edge_workflow_service_pb2.SignalLineageEdgeWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_lineage_edge_workflow_service_pb2.SignalLineageEdgeWorkflowResponse:
        """Signals a lineage edge."""
        return await self.workflow.handle_signal_lineage_edge_workflow(request)

    @rpc_errors
    async def StartLineageEdgeWorkflow(
        self, request: lineage_v1_lineage_edge_workflow_service_pb2.StartLineageEdgeWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_lineage_edge_workflow_service_pb2.StartLineageEdgeWorkflowResponse:
        """Starts a lineage edge."""
        return await self.workflow.handle_start_lineage_edge_workflow(request)
