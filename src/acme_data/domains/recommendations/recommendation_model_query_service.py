"""Answers read-only questions about recommendation models, for screens and reports."""

from __future__ import annotations

from collections.abc import AsyncIterator

import grpc

from acme.recommendations.v1 import (
    recommendation_model_query_service_pb2 as recommendations_v1_recommendation_model_query_service_pb2,
)
from acme.recommendations.v1 import (
    recommendation_model_query_service_pb2_grpc as recommendations_v1_recommendation_model_query_service_pb2_grpc,
)

from acme_data.domains.recommendations.dependencies import Dependencies
from acme_data.domains.recommendations.recommendation_model_query_service_operations import (
    handle_browse_recommendation_models,
)
from acme_data.domains.recommendations.recommendation_model_query_service_operations import (
    handle_count_recommendation_models,
)
from acme_data.domains.recommendations.recommendation_model_query_service_operations import (
    handle_export_recommendation_models,
)
from acme_data.domains.recommendations.recommendation_model_query_service_operations import (
    handle_find_recommendation_models,
)
from acme_data.domains.recommendations.recommendation_model_query_service_operations import (
    handle_lookup_recommendation_model,
)
from acme_data.domains.recommendations.recommendation_model_query_service_operations import (
    handle_peek_recommendation_model,
)
from acme_data.domains.recommendations.recommendation_model_query_service_operations import (
    handle_suggest_recommendation_models,
)
from acme_data.platform.rpc import messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors


class RecommendationModelQueryServicer(
    recommendations_v1_recommendation_model_query_service_pb2_grpc.RecommendationModelQueryServiceServicer
):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    @retry_transient
    async def BrowseRecommendationModels(
        self, request: recommendations_v1_recommendation_model_query_service_pb2.BrowseRecommendationModelsRequest, context: grpc.aio.ServicerContext,
    ) -> recommendations_v1_recommendation_model_query_service_pb2.BrowseRecommendationModelsResponse:
        """Lists recommendation models a page at a time."""
        return await handle_browse_recommendation_models(self.deps, request)

    @rpc_errors
    @retry_transient
    async def CountRecommendationModels(
        self, request: recommendations_v1_recommendation_model_query_service_pb2.CountRecommendationModelsRequest, context: grpc.aio.ServicerContext,
    ) -> recommendations_v1_recommendation_model_query_service_pb2.CountRecommendationModelsResponse:
        """Counts recommendation models by status."""
        return await handle_count_recommendation_models(self.deps, request)

    @stream_errors
    async def ExportRecommendationModels(
        self, request: recommendations_v1_recommendation_model_query_service_pb2.ExportRecommendationModelsRequest, context: grpc.aio.ServicerContext,
    ) -> AsyncIterator[recommendations_v1_recommendation_model_query_service_pb2.ExportRecommendationModelsResponse]:
        """Streams every matching recommendation model."""
        response = await handle_export_recommendation_models(self.deps, request)
        for item in messages((response,)):
            yield item

    @rpc_errors
    @retry_transient
    async def FindRecommendationModels(
        self, request: recommendations_v1_recommendation_model_query_service_pb2.FindRecommendationModelsRequest, context: grpc.aio.ServicerContext,
    ) -> recommendations_v1_recommendation_model_query_service_pb2.FindRecommendationModelsResponse:
        """Lists recommendation models a page at a time."""
        return await handle_find_recommendation_models(self.deps, request)

    @rpc_errors
    @retry_transient
    async def LookupRecommendationModel(
        self, request: recommendations_v1_recommendation_model_query_service_pb2.LookupRecommendationModelRequest, context: grpc.aio.ServicerContext,
    ) -> recommendations_v1_recommendation_model_query_service_pb2.LookupRecommendationModelResponse:
        """Returns a recommendation model."""
        return await handle_lookup_recommendation_model(self.deps, request)

    @rpc_errors
    @retry_transient
    async def PeekRecommendationModel(
        self, request: recommendations_v1_recommendation_model_query_service_pb2.PeekRecommendationModelRequest, context: grpc.aio.ServicerContext,
    ) -> recommendations_v1_recommendation_model_query_service_pb2.PeekRecommendationModelResponse:
        """Returns a recommendation model."""
        return await handle_peek_recommendation_model(self.deps, request)

    @rpc_errors
    @retry_transient
    async def SuggestRecommendationModels(
        self, request: recommendations_v1_recommendation_model_query_service_pb2.SuggestRecommendationModelsRequest, context: grpc.aio.ServicerContext,
    ) -> recommendations_v1_recommendation_model_query_service_pb2.SuggestRecommendationModelsResponse:
        """Lists recommendation models a page at a time."""
        return await handle_suggest_recommendation_models(self.deps, request)
