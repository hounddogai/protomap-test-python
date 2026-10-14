"""Connects external systems that send data share events."""

from __future__ import annotations

from collections.abc import AsyncIterator

import grpc

from acme.datahub.v1 import data_share_integration_service_pb2 as datahub_v1_data_share_integration_service_pb2
from acme.datahub.v1 import (
    data_share_integration_service_pb2_grpc as datahub_v1_data_share_integration_service_pb2_grpc,
)

from acme_data.domains.datahub.data_share_integration_service_workflow import DataShareIntegrationServicerWorkflow
from acme_data.domains.datahub.dependencies import Dependencies
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors


class DataShareIntegrationServicer(
    datahub_v1_data_share_integration_service_pb2_grpc.DataShareIntegrationServiceServicer
):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps
        self.workflow = DataShareIntegrationServicerWorkflow(deps)

    @rpc_errors
    async def AcknowledgeDataShareEvent(
        self, request: datahub_v1_data_share_integration_service_pb2.AcknowledgeDataShareEventRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_data_share_integration_service_pb2.AcknowledgeDataShareEventResponse:
        """Acknowledges a data share."""
        return await self.workflow.handle_acknowledge_data_share_event(request)

    @rpc_errors
    async def ConnectDataShareSource(
        self, request: datahub_v1_data_share_integration_service_pb2.ConnectDataShareSourceRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_data_share_integration_service_pb2.ConnectDataShareSourceResponse:
        """Connects a data share."""
        return await self.workflow.handle_connect_data_share_source(request)

    @rpc_errors
    async def DisconnectDataShareSource(
        self, request: datahub_v1_data_share_integration_service_pb2.DisconnectDataShareSourceRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_data_share_integration_service_pb2.DisconnectDataShareSourceResponse:
        """Disconnects a data share."""
        return await self.workflow.handle_disconnect_data_share_source(request)

    @rpc_errors
    async def IngestDataShareEvents(
        self, requests: AsyncIterator[
            datahub_v1_data_share_integration_service_pb2.IngestDataShareEventsRequest
        ], context: grpc.aio.ServicerContext,
    ) -> datahub_v1_data_share_integration_service_pb2.IngestDataShareEventsResponse:
        """Takes a stream of data shares and answers once at the end."""
        response = datahub_v1_data_share_integration_service_pb2.IngestDataShareEventsResponse()
        async for request in requests:
            response.MergeFrom(await self.workflow.handle_ingest_data_share_events(request))
        return response

    @rpc_errors
    @retry_transient
    async def ListDataShareSources(
        self, request: datahub_v1_data_share_integration_service_pb2.ListDataShareSourcesRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_data_share_integration_service_pb2.ListDataShareSourcesResponse:
        """Lists data shares a page at a time."""
        return await self.workflow.handle_list_data_share_sources(request)

    @stream_errors
    async def RelayDataShareMessages(
        self, requests: AsyncIterator[
            datahub_v1_data_share_integration_service_pb2.RelayDataShareMessagesRequest
        ], context: grpc.aio.ServicerContext,
    ) -> AsyncIterator[datahub_v1_data_share_integration_service_pb2.RelayDataShareMessagesResponse]:
        """Exchanges changes of data shares with a peer."""
        async for request in requests:
            yield await self.workflow.handle_relay_data_share_messages(request)

    @rpc_errors
    async def ReplayDataShareEvents(
        self, request: datahub_v1_data_share_integration_service_pb2.ReplayDataShareEventsRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_data_share_integration_service_pb2.ReplayDataShareEventsResponse:
        """Replays a data share."""
        return await self.workflow.handle_replay_data_share_events(request)
