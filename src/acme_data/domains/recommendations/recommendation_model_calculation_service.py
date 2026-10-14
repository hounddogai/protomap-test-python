"""Computes the figures of a recommendation model, such as totals, taxes, and estimates."""

from __future__ import annotations

from collections.abc import AsyncIterator

import grpc

from acme.recommendations.v1 import (
    recommendation_model_calculation_service_pb2 as recommendations_v1_recommendation_model_calculation_service_pb2,
)
from acme.recommendations.v1 import (
    recommendation_model_calculation_service_pb2_grpc as recommendations_v1_recommendation_model_calculation_service_pb2_grpc,
)

from acme_data.domains.recommendations.dependencies import Dependencies
from acme_data.domains.recommendations.recommendation_model_calculation_service_workflow import (
    RecommendationModelCalculationServicerWorkflow,
)
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors


class RecommendationModelCalculationServicer(
    recommendations_v1_recommendation_model_calculation_service_pb2_grpc.RecommendationModelCalculationServiceServicer
):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps
        self.workflow = RecommendationModelCalculationServicerWorkflow(deps)

    @rpc_errors
    async def CalculateRecommendationModel(
        self, request: recommendations_v1_recommendation_model_calculation_service_pb2.CalculateRecommendationModelRequest, context: grpc.aio.ServicerContext,
    ) -> recommendations_v1_recommendation_model_calculation_service_pb2.CalculateRecommendationModelResponse:
        """Calculates a recommendation model."""
        return await self.workflow.handle_calculate_recommendation_model(request)

    @rpc_errors
    async def CompareRecommendationModelOptions(
        self, request: recommendations_v1_recommendation_model_calculation_service_pb2.CompareRecommendationModelOptionsRequest, context: grpc.aio.ServicerContext,
    ) -> recommendations_v1_recommendation_model_calculation_service_pb2.CompareRecommendationModelOptionsResponse:
        """Compares a recommendation model."""
        return await self.workflow.handle_compare_recommendation_model_options(request)

    @rpc_errors
    async def EstimateRecommendationModel(
        self, request: recommendations_v1_recommendation_model_calculation_service_pb2.EstimateRecommendationModelRequest, context: grpc.aio.ServicerContext,
    ) -> recommendations_v1_recommendation_model_calculation_service_pb2.EstimateRecommendationModelResponse:
        """Estimates a recommendation model."""
        return await self.workflow.handle_estimate_recommendation_model(request)

    @rpc_errors
    async def QuoteRecommendationModel(
        self, request: recommendations_v1_recommendation_model_calculation_service_pb2.QuoteRecommendationModelRequest, context: grpc.aio.ServicerContext,
    ) -> recommendations_v1_recommendation_model_calculation_service_pb2.QuoteRecommendationModelResponse:
        """Quotes a recommendation model."""
        return await self.workflow.handle_quote_recommendation_model(request)

    @rpc_errors
    async def RecalculateRecommendationModels(
        self, request: recommendations_v1_recommendation_model_calculation_service_pb2.RecalculateRecommendationModelsRequest, context: grpc.aio.ServicerContext,
    ) -> recommendations_v1_recommendation_model_calculation_service_pb2.RecalculateRecommendationModelsResponse:
        """Recalculates a recommendation model."""
        return await self.workflow.handle_recalculate_recommendation_models(request)

    @rpc_errors
    async def SimulateRecommendationModel(
        self, request: recommendations_v1_recommendation_model_calculation_service_pb2.SimulateRecommendationModelRequest, context: grpc.aio.ServicerContext,
    ) -> recommendations_v1_recommendation_model_calculation_service_pb2.SimulateRecommendationModelResponse:
        """Simulates a recommendation model."""
        return await self.workflow.handle_simulate_recommendation_model(request)
