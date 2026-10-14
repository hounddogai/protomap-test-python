"""Computes the figures of an interaction, such as totals, taxes, and estimates."""

from __future__ import annotations

from collections.abc import AsyncIterator

import grpc

from acme.recommendations.v1 import (
    interaction_calculation_service_pb2 as recommendations_v1_interaction_calculation_service_pb2,
)
from acme.recommendations.v1 import (
    interaction_calculation_service_pb2_grpc as recommendations_v1_interaction_calculation_service_pb2_grpc,
)

from acme_data.domains.recommendations.dependencies import Dependencies
from acme_data.domains.recommendations.interaction_calculation_service_workflow import (
    InteractionCalculationServicerWorkflow,
)
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors


class InteractionCalculationServicer(
    recommendations_v1_interaction_calculation_service_pb2_grpc.InteractionCalculationServiceServicer
):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps
        self.workflow = InteractionCalculationServicerWorkflow(deps)

    @rpc_errors
    async def CalculateInteraction(
        self, request: recommendations_v1_interaction_calculation_service_pb2.CalculateInteractionRequest, context: grpc.aio.ServicerContext,
    ) -> recommendations_v1_interaction_calculation_service_pb2.CalculateInteractionResponse:
        """Calculates an interaction."""
        return await self.workflow.handle_calculate_interaction(request)

    @rpc_errors
    async def CompareInteractionOptions(
        self, request: recommendations_v1_interaction_calculation_service_pb2.CompareInteractionOptionsRequest, context: grpc.aio.ServicerContext,
    ) -> recommendations_v1_interaction_calculation_service_pb2.CompareInteractionOptionsResponse:
        """Compares an interaction."""
        return await self.workflow.handle_compare_interaction_options(request)

    @rpc_errors
    async def EstimateInteraction(
        self, request: recommendations_v1_interaction_calculation_service_pb2.EstimateInteractionRequest, context: grpc.aio.ServicerContext,
    ) -> recommendations_v1_interaction_calculation_service_pb2.EstimateInteractionResponse:
        """Estimates an interaction."""
        return await self.workflow.handle_estimate_interaction(request)

    @rpc_errors
    async def ExplainInteractionCalculation(
        self, request: recommendations_v1_interaction_calculation_service_pb2.ExplainInteractionCalculationRequest, context: grpc.aio.ServicerContext,
    ) -> recommendations_v1_interaction_calculation_service_pb2.ExplainInteractionCalculationResponse:
        """Explains an interaction."""
        return await self.workflow.handle_explain_interaction_calculation(request)

    @rpc_errors
    @retry_transient
    async def GetInteractionRates(
        self, request: recommendations_v1_interaction_calculation_service_pb2.GetInteractionRatesRequest, context: grpc.aio.ServicerContext,
    ) -> recommendations_v1_interaction_calculation_service_pb2.GetInteractionRatesResponse:
        """Returns an interaction."""
        return await self.workflow.handle_get_interaction_rates(request)

    @rpc_errors
    async def QuoteInteraction(
        self, request: recommendations_v1_interaction_calculation_service_pb2.QuoteInteractionRequest, context: grpc.aio.ServicerContext,
    ) -> recommendations_v1_interaction_calculation_service_pb2.QuoteInteractionResponse:
        """Quotes an interaction."""
        return await self.workflow.handle_quote_interaction(request)

    @rpc_errors
    async def RecalculateInteractions(
        self, request: recommendations_v1_interaction_calculation_service_pb2.RecalculateInteractionsRequest, context: grpc.aio.ServicerContext,
    ) -> recommendations_v1_interaction_calculation_service_pb2.RecalculateInteractionsResponse:
        """Recalculates an interaction."""
        return await self.workflow.handle_recalculate_interactions(request)

    @rpc_errors
    async def SimulateInteraction(
        self, request: recommendations_v1_interaction_calculation_service_pb2.SimulateInteractionRequest, context: grpc.aio.ServicerContext,
    ) -> recommendations_v1_interaction_calculation_service_pb2.SimulateInteractionResponse:
        """Simulates an interaction."""
        return await self.workflow.handle_simulate_interaction(request)
