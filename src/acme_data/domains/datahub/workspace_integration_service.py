"""Connects external systems that send workspace events."""

from __future__ import annotations

from collections.abc import AsyncIterator

import grpc

from acme.datahub.v1 import workspace_integration_service_pb2 as datahub_v1_workspace_integration_service_pb2
from acme.datahub.v1 import workspace_integration_service_pb2_grpc as datahub_v1_workspace_integration_service_pb2_grpc

from acme_data.domains.datahub.dependencies import Dependencies
from acme_data.domains.datahub.workspace_integration_service_workflow import WorkspaceIntegrationServicerWorkflow
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors


class WorkspaceIntegrationServicer(
    datahub_v1_workspace_integration_service_pb2_grpc.WorkspaceIntegrationServiceServicer
):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps
        self.workflow = WorkspaceIntegrationServicerWorkflow(deps)

    @rpc_errors
    async def AcknowledgeWorkspaceEvent(
        self, request: datahub_v1_workspace_integration_service_pb2.AcknowledgeWorkspaceEventRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_workspace_integration_service_pb2.AcknowledgeWorkspaceEventResponse:
        """Acknowledges a workspace."""
        return await self.workflow.handle_acknowledge_workspace_event(request)

    @rpc_errors
    async def ConnectWorkspaceSource(
        self, request: datahub_v1_workspace_integration_service_pb2.ConnectWorkspaceSourceRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_workspace_integration_service_pb2.ConnectWorkspaceSourceResponse:
        """Connects a workspace."""
        return await self.workflow.handle_connect_workspace_source(request)

    @rpc_errors
    async def DisconnectWorkspaceSource(
        self, request: datahub_v1_workspace_integration_service_pb2.DisconnectWorkspaceSourceRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_workspace_integration_service_pb2.DisconnectWorkspaceSourceResponse:
        """Disconnects a workspace."""
        return await self.workflow.handle_disconnect_workspace_source(request)

    @stream_errors
    async def RelayWorkspaceMessages(
        self, requests: AsyncIterator[
            datahub_v1_workspace_integration_service_pb2.RelayWorkspaceMessagesRequest
        ], context: grpc.aio.ServicerContext,
    ) -> AsyncIterator[datahub_v1_workspace_integration_service_pb2.RelayWorkspaceMessagesResponse]:
        """Exchanges changes of workspaces with a peer."""
        async for request in requests:
            yield await self.workflow.handle_relay_workspace_messages(request)

    @rpc_errors
    async def ReplayWorkspaceEvents(
        self, request: datahub_v1_workspace_integration_service_pb2.ReplayWorkspaceEventsRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_workspace_integration_service_pb2.ReplayWorkspaceEventsResponse:
        """Replays a workspace."""
        return await self.workflow.handle_replay_workspace_events(request)

    @rpc_errors
    async def TestWorkspaceConnection(
        self, request: datahub_v1_workspace_integration_service_pb2.TestWorkspaceConnectionRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_workspace_integration_service_pb2.TestWorkspaceConnectionResponse:
        """Tests a workspace."""
        return await self.workflow.handle_test_workspace_connection(request)
