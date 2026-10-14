"""Computes the figures of an entity, such as totals, taxes, and estimates."""

from __future__ import annotations

from collections.abc import AsyncIterator

import grpc

from acme.featurestore.v1 import entity_calculation_service_pb2 as featurestore_v1_entity_calculation_service_pb2
from acme.featurestore.v1 import (
    entity_calculation_service_pb2_grpc as featurestore_v1_entity_calculation_service_pb2_grpc,
)

from acme_data.domains.featurestore.dependencies import Dependencies
from acme_data.domains.featurestore.entity_calculation_service_workflow import EntityCalculationServicerWorkflow
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors


class EntityCalculationServicer(featurestore_v1_entity_calculation_service_pb2_grpc.EntityCalculationServiceServicer):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps
        self.workflow = EntityCalculationServicerWorkflow(deps)

    @rpc_errors
    async def CalculateEntity(
        self, request: featurestore_v1_entity_calculation_service_pb2.CalculateEntityRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_entity_calculation_service_pb2.CalculateEntityResponse:
        """Calculates an entity."""
        return await self.workflow.handle_calculate_entity(request)

    @rpc_errors
    async def CompareEntityOptions(
        self, request: featurestore_v1_entity_calculation_service_pb2.CompareEntityOptionsRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_entity_calculation_service_pb2.CompareEntityOptionsResponse:
        """Compares an entity."""
        return await self.workflow.handle_compare_entity_options(request)

    @rpc_errors
    async def EstimateEntity(
        self, request: featurestore_v1_entity_calculation_service_pb2.EstimateEntityRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_entity_calculation_service_pb2.EstimateEntityResponse:
        """Estimates an entity."""
        return await self.workflow.handle_estimate_entity(request)

    @rpc_errors
    async def ExplainEntityCalculation(
        self, request: featurestore_v1_entity_calculation_service_pb2.ExplainEntityCalculationRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_entity_calculation_service_pb2.ExplainEntityCalculationResponse:
        """Explains an entity."""
        return await self.workflow.handle_explain_entity_calculation(request)

    @rpc_errors
    @retry_transient
    async def GetEntityRates(
        self, request: featurestore_v1_entity_calculation_service_pb2.GetEntityRatesRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_entity_calculation_service_pb2.GetEntityRatesResponse:
        """Returns an entity."""
        return await self.workflow.handle_get_entity_rates(request)

    @rpc_errors
    async def QuoteEntity(
        self, request: featurestore_v1_entity_calculation_service_pb2.QuoteEntityRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_entity_calculation_service_pb2.QuoteEntityResponse:
        """Quotes an entity."""
        return await self.workflow.handle_quote_entity(request)
