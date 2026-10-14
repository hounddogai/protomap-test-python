"""Runs the long-lived workflow that takes an impact from start to finish."""

from __future__ import annotations

from collections.abc import AsyncIterator

import grpc

from acme.lineage.v1 import impact_workflow_service_pb2 as lineage_v1_impact_workflow_service_pb2
from acme.lineage.v1 import impact_workflow_service_pb2_grpc as lineage_v1_impact_workflow_service_pb2_grpc

from acme_data.domains.lineage.dependencies import Dependencies
from acme_data.domains.lineage.impact_workflow_service_operations import handle_advance_impact_workflow
from acme_data.domains.lineage.impact_workflow_service_operations import handle_cancel_impact_workflow
from acme_data.domains.lineage.impact_workflow_service_operations import handle_inspect_impact_workflow
from acme_data.domains.lineage.impact_workflow_service_operations import handle_list_impact_workflows
from acme_data.domains.lineage.impact_workflow_service_operations import handle_pause_impact_workflow
from acme_data.domains.lineage.impact_workflow_service_operations import handle_retry_impact_workflow
from acme_data.domains.lineage.impact_workflow_service_operations import handle_signal_impact_workflow
from acme_data.domains.lineage.impact_workflow_service_operations import handle_start_impact_workflow
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors


class ImpactWorkflowServicer(lineage_v1_impact_workflow_service_pb2_grpc.ImpactWorkflowServiceServicer):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    async def AdvanceImpactWorkflow(
        self, request: lineage_v1_impact_workflow_service_pb2.AdvanceImpactWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_impact_workflow_service_pb2.AdvanceImpactWorkflowResponse:
        """Advances an impact."""
        return await handle_advance_impact_workflow(self.deps, request)

    @rpc_errors
    async def CancelImpactWorkflow(
        self, request: lineage_v1_impact_workflow_service_pb2.CancelImpactWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_impact_workflow_service_pb2.CancelImpactWorkflowResponse:
        """Cancels an impact."""
        return await handle_cancel_impact_workflow(self.deps, request)

    @rpc_errors
    @retry_transient
    async def InspectImpactWorkflow(
        self, request: lineage_v1_impact_workflow_service_pb2.InspectImpactWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_impact_workflow_service_pb2.InspectImpactWorkflowResponse:
        """Returns an impact."""
        return await handle_inspect_impact_workflow(self.deps, request)

    @rpc_errors
    @retry_transient
    async def ListImpactWorkflows(
        self, request: lineage_v1_impact_workflow_service_pb2.ListImpactWorkflowsRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_impact_workflow_service_pb2.ListImpactWorkflowsResponse:
        """Lists impacts a page at a time."""
        return await handle_list_impact_workflows(self.deps, request)

    @rpc_errors
    async def PauseImpactWorkflow(
        self, request: lineage_v1_impact_workflow_service_pb2.PauseImpactWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_impact_workflow_service_pb2.PauseImpactWorkflowResponse:
        """Pauses an impact."""
        return await handle_pause_impact_workflow(self.deps, request)

    @rpc_errors
    async def RetryImpactWorkflow(
        self, request: lineage_v1_impact_workflow_service_pb2.RetryImpactWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_impact_workflow_service_pb2.RetryImpactWorkflowResponse:
        """Retrys an impact."""
        return await handle_retry_impact_workflow(self.deps, request)

    @rpc_errors
    async def SignalImpactWorkflow(
        self, request: lineage_v1_impact_workflow_service_pb2.SignalImpactWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_impact_workflow_service_pb2.SignalImpactWorkflowResponse:
        """Signals an impact."""
        return await handle_signal_impact_workflow(self.deps, request)

    @rpc_errors
    async def StartImpactWorkflow(
        self, request: lineage_v1_impact_workflow_service_pb2.StartImpactWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_impact_workflow_service_pb2.StartImpactWorkflowResponse:
        """Starts an impact."""
        return await handle_start_impact_workflow(self.deps, request)
