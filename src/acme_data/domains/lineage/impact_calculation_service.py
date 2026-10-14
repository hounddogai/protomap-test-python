"""Computes the figures of an impact, such as totals, taxes, and estimates."""

from __future__ import annotations

from collections.abc import AsyncIterator

import grpc

from acme.lineage.v1 import impact_calculation_service_pb2 as lineage_v1_impact_calculation_service_pb2
from acme.lineage.v1 import impact_calculation_service_pb2_grpc as lineage_v1_impact_calculation_service_pb2_grpc

from acme_data.domains.lineage.dependencies import Dependencies
from acme_data.domains.lineage.impact_calculation_service_workflow import ImpactCalculationServicerWorkflow
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors


class ImpactCalculationServicer(lineage_v1_impact_calculation_service_pb2_grpc.ImpactCalculationServiceServicer):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps
        self.workflow = ImpactCalculationServicerWorkflow(deps)

    @rpc_errors
    async def CalculateImpact(
        self, request: lineage_v1_impact_calculation_service_pb2.CalculateImpactRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_impact_calculation_service_pb2.CalculateImpactResponse:
        """Calculates an impact."""
        return await self.workflow.handle_calculate_impact(request)

    @rpc_errors
    async def CompareImpactOptions(
        self, request: lineage_v1_impact_calculation_service_pb2.CompareImpactOptionsRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_impact_calculation_service_pb2.CompareImpactOptionsResponse:
        """Compares an impact."""
        return await self.workflow.handle_compare_impact_options(request)

    @rpc_errors
    async def EstimateImpact(
        self, request: lineage_v1_impact_calculation_service_pb2.EstimateImpactRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_impact_calculation_service_pb2.EstimateImpactResponse:
        """Estimates an impact."""
        return await self.workflow.handle_estimate_impact(request)

    @rpc_errors
    async def ExplainImpactCalculation(
        self, request: lineage_v1_impact_calculation_service_pb2.ExplainImpactCalculationRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_impact_calculation_service_pb2.ExplainImpactCalculationResponse:
        """Explains an impact."""
        return await self.workflow.handle_explain_impact_calculation(request)

    @rpc_errors
    @retry_transient
    async def GetImpactRates(
        self, request: lineage_v1_impact_calculation_service_pb2.GetImpactRatesRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_impact_calculation_service_pb2.GetImpactRatesResponse:
        """Returns an impact."""
        return await self.workflow.handle_get_impact_rates(request)

    @rpc_errors
    async def QuoteImpact(
        self, request: lineage_v1_impact_calculation_service_pb2.QuoteImpactRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_impact_calculation_service_pb2.QuoteImpactResponse:
        """Quotes an impact."""
        return await self.workflow.handle_quote_impact(request)

    @rpc_errors
    async def RecalculateImpacts(
        self, request: lineage_v1_impact_calculation_service_pb2.RecalculateImpactsRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_impact_calculation_service_pb2.RecalculateImpactsResponse:
        """Recalculates an impact."""
        return await self.workflow.handle_recalculate_impacts(request)

    @rpc_errors
    async def SimulateImpact(
        self, request: lineage_v1_impact_calculation_service_pb2.SimulateImpactRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_impact_calculation_service_pb2.SimulateImpactResponse:
        """Simulates an impact."""
        return await self.workflow.handle_simulate_impact(request)
