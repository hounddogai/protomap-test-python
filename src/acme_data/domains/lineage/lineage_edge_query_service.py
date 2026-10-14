"""Answers read-only questions about lineage edges, for screens and reports."""

from __future__ import annotations

from collections.abc import AsyncIterator

import grpc

from acme.lineage.v1 import lineage_edge_query_service_pb2 as lineage_v1_lineage_edge_query_service_pb2
from acme.lineage.v1 import lineage_edge_query_service_pb2_grpc as lineage_v1_lineage_edge_query_service_pb2_grpc

from acme_data.domains.lineage.dependencies import Dependencies
from acme_data.domains.lineage.lineage_edge_query_service_operations import handle_browse_lineage_edges
from acme_data.domains.lineage.lineage_edge_query_service_operations import handle_count_lineage_edges
from acme_data.domains.lineage.lineage_edge_query_service_operations import handle_find_lineage_edges
from acme_data.domains.lineage.lineage_edge_query_service_operations import handle_lookup_lineage_edge
from acme_data.domains.lineage.lineage_edge_query_service_operations import handle_peek_lineage_edge
from acme_data.domains.lineage.lineage_edge_query_service_operations import handle_resolve_lineage_edges
from acme_data.domains.lineage.lineage_edge_query_service_operations import handle_suggest_lineage_edges
from acme_data.domains.lineage.lineage_edge_query_service_operations import handle_summarize_lineage_edges
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors


class LineageEdgeQueryServicer(lineage_v1_lineage_edge_query_service_pb2_grpc.LineageEdgeQueryServiceServicer):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    @retry_transient
    async def BrowseLineageEdges(
        self, request: lineage_v1_lineage_edge_query_service_pb2.BrowseLineageEdgesRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_lineage_edge_query_service_pb2.BrowseLineageEdgesResponse:
        """Lists lineage edges a page at a time."""
        return await handle_browse_lineage_edges(self.deps, request)

    @rpc_errors
    @retry_transient
    async def CountLineageEdges(
        self, request: lineage_v1_lineage_edge_query_service_pb2.CountLineageEdgesRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_lineage_edge_query_service_pb2.CountLineageEdgesResponse:
        """Counts lineage edges by status."""
        return await handle_count_lineage_edges(self.deps, request)

    @rpc_errors
    @retry_transient
    async def FindLineageEdges(
        self, request: lineage_v1_lineage_edge_query_service_pb2.FindLineageEdgesRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_lineage_edge_query_service_pb2.FindLineageEdgesResponse:
        """Lists lineage edges a page at a time."""
        return await handle_find_lineage_edges(self.deps, request)

    @rpc_errors
    @retry_transient
    async def LookupLineageEdge(
        self, request: lineage_v1_lineage_edge_query_service_pb2.LookupLineageEdgeRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_lineage_edge_query_service_pb2.LookupLineageEdgeResponse:
        """Returns a lineage edge."""
        return await handle_lookup_lineage_edge(self.deps, request)

    @rpc_errors
    @retry_transient
    async def PeekLineageEdge(
        self, request: lineage_v1_lineage_edge_query_service_pb2.PeekLineageEdgeRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_lineage_edge_query_service_pb2.PeekLineageEdgeResponse:
        """Returns a lineage edge."""
        return await handle_peek_lineage_edge(self.deps, request)

    @rpc_errors
    @retry_transient
    async def ResolveLineageEdges(
        self, request: lineage_v1_lineage_edge_query_service_pb2.ResolveLineageEdgesRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_lineage_edge_query_service_pb2.ResolveLineageEdgesResponse:
        """Returns several lineage edges at once."""
        return await handle_resolve_lineage_edges(self.deps, request)

    @rpc_errors
    @retry_transient
    async def SuggestLineageEdges(
        self, request: lineage_v1_lineage_edge_query_service_pb2.SuggestLineageEdgesRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_lineage_edge_query_service_pb2.SuggestLineageEdgesResponse:
        """Lists lineage edges a page at a time."""
        return await handle_suggest_lineage_edges(self.deps, request)

    @rpc_errors
    async def SummarizeLineageEdges(
        self, request: lineage_v1_lineage_edge_query_service_pb2.SummarizeLineageEdgesRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_lineage_edge_query_service_pb2.SummarizeLineageEdgesResponse:
        """Summarizes a lineage edge."""
        return await handle_summarize_lineage_edges(self.deps, request)
