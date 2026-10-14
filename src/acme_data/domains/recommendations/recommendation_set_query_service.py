"""Answers read-only questions about recommendation sets, for screens and reports."""

from __future__ import annotations

from collections.abc import AsyncIterator

import grpc

from acme.recommendations.v1 import (
    recommendation_set_query_service_pb2 as recommendations_v1_recommendation_set_query_service_pb2,
)
from acme.recommendations.v1 import (
    recommendation_set_query_service_pb2_grpc as recommendations_v1_recommendation_set_query_service_pb2_grpc,
)

from acme_data.domains.recommendations.dependencies import Dependencies
from acme_data.domains.recommendations.recommendation_set_query_service_workflow import (
    RecommendationSetQueryServicerWorkflow,
)
from acme_data.platform.rpc import messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors


class RecommendationSetQueryServicer(
    recommendations_v1_recommendation_set_query_service_pb2_grpc.RecommendationSetQueryServiceServicer
):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps
        self.workflow = RecommendationSetQueryServicerWorkflow(deps)

    @rpc_errors
    @retry_transient
    async def BrowseRecommendationSets(
        self, request: recommendations_v1_recommendation_set_query_service_pb2.BrowseRecommendationSetsRequest, context: grpc.aio.ServicerContext,
    ) -> recommendations_v1_recommendation_set_query_service_pb2.BrowseRecommendationSetsResponse:
        """Lists recommendation sets a page at a time."""
        return await self.workflow.handle_browse_recommendation_sets(request)

    @stream_errors
    async def ExportRecommendationSets(
        self, request: recommendations_v1_recommendation_set_query_service_pb2.ExportRecommendationSetsRequest, context: grpc.aio.ServicerContext,
    ) -> AsyncIterator[recommendations_v1_recommendation_set_query_service_pb2.ExportRecommendationSetsResponse]:
        """Streams every matching recommendation set."""
        response = await self.workflow.handle_export_recommendation_sets(request)
        for item in messages((response,)):
            yield item

    @rpc_errors
    @retry_transient
    async def FindRecommendationSets(
        self, request: recommendations_v1_recommendation_set_query_service_pb2.FindRecommendationSetsRequest, context: grpc.aio.ServicerContext,
    ) -> recommendations_v1_recommendation_set_query_service_pb2.FindRecommendationSetsResponse:
        """Lists recommendation sets a page at a time."""
        return await self.workflow.handle_find_recommendation_sets(request)

    @rpc_errors
    @retry_transient
    async def LookupRecommendationSet(
        self, request: recommendations_v1_recommendation_set_query_service_pb2.LookupRecommendationSetRequest, context: grpc.aio.ServicerContext,
    ) -> recommendations_v1_recommendation_set_query_service_pb2.LookupRecommendationSetResponse:
        """Returns a recommendation set."""
        return await self.workflow.handle_lookup_recommendation_set(request)

    @rpc_errors
    @retry_transient
    async def PeekRecommendationSet(
        self, request: recommendations_v1_recommendation_set_query_service_pb2.PeekRecommendationSetRequest, context: grpc.aio.ServicerContext,
    ) -> recommendations_v1_recommendation_set_query_service_pb2.PeekRecommendationSetResponse:
        """Returns a recommendation set."""
        return await self.workflow.handle_peek_recommendation_set(request)

    @rpc_errors
    @retry_transient
    async def SuggestRecommendationSets(
        self, request: recommendations_v1_recommendation_set_query_service_pb2.SuggestRecommendationSetsRequest, context: grpc.aio.ServicerContext,
    ) -> recommendations_v1_recommendation_set_query_service_pb2.SuggestRecommendationSetsResponse:
        """Lists recommendation sets a page at a time."""
        return await self.workflow.handle_suggest_recommendation_sets(request)

    @rpc_errors
    async def SummarizeRecommendationSets(
        self, request: recommendations_v1_recommendation_set_query_service_pb2.SummarizeRecommendationSetsRequest, context: grpc.aio.ServicerContext,
    ) -> recommendations_v1_recommendation_set_query_service_pb2.SummarizeRecommendationSetsResponse:
        """Summarizes a recommendation set."""
        return await self.workflow.handle_summarize_recommendation_sets(request)
