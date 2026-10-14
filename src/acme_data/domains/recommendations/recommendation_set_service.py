"""Manages recommendation sets: creates, reads, changes, and lists them."""

from __future__ import annotations

from collections.abc import AsyncIterator

import grpc

from acme.recommendations.v1 import recommendation_set_service_pb2 as recommendations_v1_recommendation_set_service_pb2
from acme.recommendations.v1 import (
    recommendation_set_service_pb2_grpc as recommendations_v1_recommendation_set_service_pb2_grpc,
)

from acme_data.domains.recommendations.dependencies import Dependencies
from acme_data.domains.recommendations.recommendation_set_service_operations import handle_batch_get_recommendation_sets
from acme_data.domains.recommendations.recommendation_set_service_operations import handle_clone_recommendation_set
from acme_data.domains.recommendations.recommendation_set_service_operations import handle_create_recommendation_set
from acme_data.domains.recommendations.recommendation_set_service_operations import handle_delete_recommendation_set
from acme_data.domains.recommendations.recommendation_set_service_operations import handle_get_recommendation_set
from acme_data.domains.recommendations.recommendation_set_service_operations import handle_list_recommendation_sets
from acme_data.domains.recommendations.recommendation_set_service_operations import handle_search_recommendation_sets
from acme_data.domains.recommendations.recommendation_set_service_operations import handle_update_recommendation_set
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors


class RecommendationSetServicer(
    recommendations_v1_recommendation_set_service_pb2_grpc.RecommendationSetServiceServicer
):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    @retry_transient
    async def BatchGetRecommendationSets(
        self, request: recommendations_v1_recommendation_set_service_pb2.BatchGetRecommendationSetsRequest, context: grpc.aio.ServicerContext,
    ) -> recommendations_v1_recommendation_set_service_pb2.BatchGetRecommendationSetsResponse:
        """Returns several recommendation sets at once."""
        return await handle_batch_get_recommendation_sets(self.deps, request)

    @rpc_errors
    async def CloneRecommendationSet(
        self, request: recommendations_v1_recommendation_set_service_pb2.CloneRecommendationSetRequest, context: grpc.aio.ServicerContext,
    ) -> recommendations_v1_recommendation_set_service_pb2.CloneRecommendationSetResponse:
        """Creates a recommendation set."""
        return await handle_clone_recommendation_set(self.deps, request)

    @rpc_errors
    async def CreateRecommendationSet(
        self, request: recommendations_v1_recommendation_set_service_pb2.CreateRecommendationSetRequest, context: grpc.aio.ServicerContext,
    ) -> recommendations_v1_recommendation_set_service_pb2.CreateRecommendationSetResponse:
        """Creates a recommendation set."""
        return await handle_create_recommendation_set(self.deps, request)

    @rpc_errors
    async def DeleteRecommendationSet(
        self, request: recommendations_v1_recommendation_set_service_pb2.DeleteRecommendationSetRequest, context: grpc.aio.ServicerContext,
    ) -> recommendations_v1_recommendation_set_service_pb2.DeleteRecommendationSetResponse:
        """Deletes a recommendation set."""
        return await handle_delete_recommendation_set(self.deps, request)

    @rpc_errors
    @retry_transient
    async def GetRecommendationSet(
        self, request: recommendations_v1_recommendation_set_service_pb2.GetRecommendationSetRequest, context: grpc.aio.ServicerContext,
    ) -> recommendations_v1_recommendation_set_service_pb2.GetRecommendationSetResponse:
        """Returns a recommendation set."""
        return await handle_get_recommendation_set(self.deps, request)

    @rpc_errors
    @retry_transient
    async def ListRecommendationSets(
        self, request: recommendations_v1_recommendation_set_service_pb2.ListRecommendationSetsRequest, context: grpc.aio.ServicerContext,
    ) -> recommendations_v1_recommendation_set_service_pb2.ListRecommendationSetsResponse:
        """Lists recommendation sets a page at a time."""
        return await handle_list_recommendation_sets(self.deps, request)

    @rpc_errors
    @retry_transient
    async def SearchRecommendationSets(
        self, request: recommendations_v1_recommendation_set_service_pb2.SearchRecommendationSetsRequest, context: grpc.aio.ServicerContext,
    ) -> recommendations_v1_recommendation_set_service_pb2.SearchRecommendationSetsResponse:
        """Lists recommendation sets a page at a time."""
        return await handle_search_recommendation_sets(self.deps, request)

    @rpc_errors
    async def UpdateRecommendationSet(
        self, request: recommendations_v1_recommendation_set_service_pb2.UpdateRecommendationSetRequest, context: grpc.aio.ServicerContext,
    ) -> recommendations_v1_recommendation_set_service_pb2.UpdateRecommendationSetResponse:
        """Changes a recommendation set."""
        return await handle_update_recommendation_set(self.deps, request)
