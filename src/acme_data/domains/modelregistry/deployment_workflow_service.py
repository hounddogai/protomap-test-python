"""Runs the long-lived workflow that takes a deployment from start to finish."""

from __future__ import annotations

from collections.abc import AsyncIterator

import grpc

from acme.modelregistry.v1 import deployment_workflow_service_pb2 as modelregistry_v1_deployment_workflow_service_pb2
from acme.modelregistry.v1 import (
    deployment_workflow_service_pb2_grpc as modelregistry_v1_deployment_workflow_service_pb2_grpc,
)

from acme_data.domains.modelregistry.dependencies import Dependencies
from acme_data.domains.modelregistry.deployment_workflow_service_operations import handle_advance_deployment_workflow
from acme_data.domains.modelregistry.deployment_workflow_service_operations import handle_cancel_deployment_workflow
from acme_data.domains.modelregistry.deployment_workflow_service_operations import handle_list_deployment_workflows
from acme_data.domains.modelregistry.deployment_workflow_service_operations import handle_pause_deployment_workflow
from acme_data.domains.modelregistry.deployment_workflow_service_operations import handle_signal_deployment_workflow
from acme_data.domains.modelregistry.deployment_workflow_service_operations import handle_start_deployment_workflow
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors


class DeploymentWorkflowServicer(
    modelregistry_v1_deployment_workflow_service_pb2_grpc.DeploymentWorkflowServiceServicer
):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    async def AdvanceDeploymentWorkflow(
        self, request: modelregistry_v1_deployment_workflow_service_pb2.AdvanceDeploymentWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_deployment_workflow_service_pb2.AdvanceDeploymentWorkflowResponse:
        """Advances a deployment."""
        return await handle_advance_deployment_workflow(self.deps, request)

    @rpc_errors
    async def CancelDeploymentWorkflow(
        self, request: modelregistry_v1_deployment_workflow_service_pb2.CancelDeploymentWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_deployment_workflow_service_pb2.CancelDeploymentWorkflowResponse:
        """Cancels a deployment."""
        return await handle_cancel_deployment_workflow(self.deps, request)

    @rpc_errors
    @retry_transient
    async def ListDeploymentWorkflows(
        self, request: modelregistry_v1_deployment_workflow_service_pb2.ListDeploymentWorkflowsRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_deployment_workflow_service_pb2.ListDeploymentWorkflowsResponse:
        """Lists deployments a page at a time."""
        return await handle_list_deployment_workflows(self.deps, request)

    @rpc_errors
    async def PauseDeploymentWorkflow(
        self, request: modelregistry_v1_deployment_workflow_service_pb2.PauseDeploymentWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_deployment_workflow_service_pb2.PauseDeploymentWorkflowResponse:
        """Pauses a deployment."""
        return await handle_pause_deployment_workflow(self.deps, request)

    @rpc_errors
    async def SignalDeploymentWorkflow(
        self, request: modelregistry_v1_deployment_workflow_service_pb2.SignalDeploymentWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_deployment_workflow_service_pb2.SignalDeploymentWorkflowResponse:
        """Signals a deployment."""
        return await handle_signal_deployment_workflow(self.deps, request)

    @rpc_errors
    async def StartDeploymentWorkflow(
        self, request: modelregistry_v1_deployment_workflow_service_pb2.StartDeploymentWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_deployment_workflow_service_pb2.StartDeploymentWorkflowResponse:
        """Starts a deployment."""
        return await handle_start_deployment_workflow(self.deps, request)
