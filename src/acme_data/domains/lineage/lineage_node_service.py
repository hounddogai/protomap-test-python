"""Manages lineage nodes: creates, reads, changes, and lists them."""

from __future__ import annotations

from collections.abc import AsyncIterator

import grpc

from acme.lineage.v1 import lineage_node_service_pb2 as lineage_v1_lineage_node_service_pb2
from acme.lineage.v1 import lineage_node_service_pb2_grpc as lineage_v1_lineage_node_service_pb2_grpc

from acme_data.domains.lineage.dependencies import Dependencies
from acme_data.domains.lineage.lineage_node_service_operations import handle_batch_create_lineage_nodes
from acme_data.domains.lineage.lineage_node_service_operations import handle_batch_get_lineage_nodes
from acme_data.domains.lineage.lineage_node_service_operations import handle_clone_lineage_node
from acme_data.domains.lineage.lineage_node_service_operations import handle_create_lineage_node
from acme_data.domains.lineage.lineage_node_service_operations import handle_delete_lineage_node
from acme_data.domains.lineage.lineage_node_service_operations import handle_get_lineage_node
from acme_data.domains.lineage.lineage_node_service_operations import handle_list_lineage_nodes
from acme_data.domains.lineage.lineage_node_service_operations import handle_search_lineage_nodes
from acme_data.domains.lineage.lineage_node_service_operations import handle_update_lineage_node
from acme_data.domains.lineage.lineage_node_service_operations import handle_watch_lineage_nodes
from acme_data.platform.rpc import messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors


class LineageNodeServicer(lineage_v1_lineage_node_service_pb2_grpc.LineageNodeServiceServicer):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    async def BatchCreateLineageNodes(
        self, requests: AsyncIterator[
            lineage_v1_lineage_node_service_pb2.BatchCreateLineageNodesRequest
        ], context: grpc.aio.ServicerContext,
    ) -> lineage_v1_lineage_node_service_pb2.BatchCreateLineageNodesResponse:
        """Takes a stream of lineage nodes and answers once at the end."""
        response = lineage_v1_lineage_node_service_pb2.BatchCreateLineageNodesResponse()
        async for request in requests:
            response.MergeFrom(await handle_batch_create_lineage_nodes(self.deps, request))
        return response

    @rpc_errors
    @retry_transient
    async def BatchGetLineageNodes(
        self, request: lineage_v1_lineage_node_service_pb2.BatchGetLineageNodesRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_lineage_node_service_pb2.BatchGetLineageNodesResponse:
        """Returns several lineage nodes at once."""
        return await handle_batch_get_lineage_nodes(self.deps, request)

    @rpc_errors
    async def CloneLineageNode(
        self, request: lineage_v1_lineage_node_service_pb2.CloneLineageNodeRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_lineage_node_service_pb2.CloneLineageNodeResponse:
        """Creates a lineage node."""
        return await handle_clone_lineage_node(self.deps, request)

    @rpc_errors
    async def CreateLineageNode(
        self, request: lineage_v1_lineage_node_service_pb2.CreateLineageNodeRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_lineage_node_service_pb2.CreateLineageNodeResponse:
        """Creates a lineage node."""
        return await handle_create_lineage_node(self.deps, request)

    @rpc_errors
    async def DeleteLineageNode(
        self, request: lineage_v1_lineage_node_service_pb2.DeleteLineageNodeRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_lineage_node_service_pb2.DeleteLineageNodeResponse:
        """Deletes a lineage node."""
        return await handle_delete_lineage_node(self.deps, request)

    @rpc_errors
    @retry_transient
    async def GetLineageNode(
        self, request: lineage_v1_lineage_node_service_pb2.GetLineageNodeRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_lineage_node_service_pb2.GetLineageNodeResponse:
        """Returns a lineage node."""
        return await handle_get_lineage_node(self.deps, request)

    @rpc_errors
    @retry_transient
    async def ListLineageNodes(
        self, request: lineage_v1_lineage_node_service_pb2.ListLineageNodesRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_lineage_node_service_pb2.ListLineageNodesResponse:
        """Lists lineage nodes a page at a time."""
        return await handle_list_lineage_nodes(self.deps, request)

    @rpc_errors
    @retry_transient
    async def SearchLineageNodes(
        self, request: lineage_v1_lineage_node_service_pb2.SearchLineageNodesRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_lineage_node_service_pb2.SearchLineageNodesResponse:
        """Lists lineage nodes a page at a time."""
        return await handle_search_lineage_nodes(self.deps, request)

    @rpc_errors
    async def UpdateLineageNode(
        self, request: lineage_v1_lineage_node_service_pb2.UpdateLineageNodeRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_lineage_node_service_pb2.UpdateLineageNodeResponse:
        """Changes a lineage node."""
        return await handle_update_lineage_node(self.deps, request)

    @stream_errors
    async def WatchLineageNodes(
        self, request: lineage_v1_lineage_node_service_pb2.WatchLineageNodesRequest, context: grpc.aio.ServicerContext,
    ) -> AsyncIterator[lineage_v1_lineage_node_service_pb2.WatchLineageNodesResponse]:
        """Streams the changes of lineage nodes as they happen."""
        response = await handle_watch_lineage_nodes(self.deps, request)
        for item in messages((response,)):
            yield item
