"""Answers read-only questions about funnels, for screens and reports."""

from __future__ import annotations

from collections.abc import AsyncIterator

import grpc

from acme.analytics.v1 import funnel_query_service_pb2 as analytics_v1_funnel_query_service_pb2
from acme.analytics.v1 import funnel_query_service_pb2_grpc as analytics_v1_funnel_query_service_pb2_grpc

from acme_data.domains.analytics.dependencies import Dependencies
from acme_data.domains.analytics.funnel_query_service_workflow import FunnelQueryServicerWorkflow
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors


class FunnelQueryServicer(analytics_v1_funnel_query_service_pb2_grpc.FunnelQueryServiceServicer):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps
        self.workflow = FunnelQueryServicerWorkflow(deps)

    @rpc_errors
    @retry_transient
    async def BrowseFunnels(
        self, request: analytics_v1_funnel_query_service_pb2.BrowseFunnelsRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_funnel_query_service_pb2.BrowseFunnelsResponse:
        """Lists funnels a page at a time."""
        return await self.workflow.handle_browse_funnels(request)

    @rpc_errors
    @retry_transient
    async def CountFunnels(
        self, request: analytics_v1_funnel_query_service_pb2.CountFunnelsRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_funnel_query_service_pb2.CountFunnelsResponse:
        """Counts funnels by status."""
        return await self.workflow.handle_count_funnels(request)

    @rpc_errors
    @retry_transient
    async def FindFunnels(
        self, request: analytics_v1_funnel_query_service_pb2.FindFunnelsRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_funnel_query_service_pb2.FindFunnelsResponse:
        """Lists funnels a page at a time."""
        return await self.workflow.handle_find_funnels(request)

    @rpc_errors
    @retry_transient
    async def LookupFunnel(
        self, request: analytics_v1_funnel_query_service_pb2.LookupFunnelRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_funnel_query_service_pb2.LookupFunnelResponse:
        """Returns a funnel."""
        return await self.workflow.handle_lookup_funnel(request)

    @rpc_errors
    @retry_transient
    async def PeekFunnel(
        self, request: analytics_v1_funnel_query_service_pb2.PeekFunnelRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_funnel_query_service_pb2.PeekFunnelResponse:
        """Returns a funnel."""
        return await self.workflow.handle_peek_funnel(request)

    @rpc_errors
    @retry_transient
    async def ResolveFunnels(
        self, request: analytics_v1_funnel_query_service_pb2.ResolveFunnelsRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_funnel_query_service_pb2.ResolveFunnelsResponse:
        """Returns several funnels at once."""
        return await self.workflow.handle_resolve_funnels(request)

    @rpc_errors
    @retry_transient
    async def SuggestFunnels(
        self, request: analytics_v1_funnel_query_service_pb2.SuggestFunnelsRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_funnel_query_service_pb2.SuggestFunnelsResponse:
        """Lists funnels a page at a time."""
        return await self.workflow.handle_suggest_funnels(request)

    @rpc_errors
    async def SummarizeFunnels(
        self, request: analytics_v1_funnel_query_service_pb2.SummarizeFunnelsRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_funnel_query_service_pb2.SummarizeFunnelsResponse:
        """Summarizes a funnel."""
        return await self.workflow.handle_summarize_funnels(request)
