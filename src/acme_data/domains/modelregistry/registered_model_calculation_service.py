"""Computes the figures of a registered model, such as totals, taxes, and estimates."""

from __future__ import annotations

from collections.abc import AsyncIterator

import grpc

from acme.modelregistry.v1 import (
    registered_model_calculation_service_pb2 as modelregistry_v1_registered_model_calculation_service_pb2,
)
from acme.modelregistry.v1 import (
    registered_model_calculation_service_pb2_grpc as modelregistry_v1_registered_model_calculation_service_pb2_grpc,
)

from acme_data.domains.modelregistry.dependencies import Dependencies
from acme_data.domains.modelregistry.registered_model_calculation_service_operations import (
    handle_calculate_registered_model,
)
from acme_data.domains.modelregistry.registered_model_calculation_service_operations import (
    handle_estimate_registered_model,
)
from acme_data.domains.modelregistry.registered_model_calculation_service_operations import (
    handle_explain_registered_model_calculation,
)
from acme_data.domains.modelregistry.registered_model_calculation_service_operations import (
    handle_get_registered_model_rates,
)
from acme_data.domains.modelregistry.registered_model_calculation_service_operations import (
    handle_quote_registered_model,
)
from acme_data.domains.modelregistry.registered_model_calculation_service_operations import (
    handle_recalculate_registered_models,
)
from acme_data.domains.modelregistry.registered_model_calculation_service_operations import (
    handle_simulate_registered_model,
)
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors


class RegisteredModelCalculationServicer(
    modelregistry_v1_registered_model_calculation_service_pb2_grpc.RegisteredModelCalculationServiceServicer
):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    async def CalculateRegisteredModel(
        self, request: modelregistry_v1_registered_model_calculation_service_pb2.CalculateRegisteredModelRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_registered_model_calculation_service_pb2.CalculateRegisteredModelResponse:
        """Calculates a registered model."""
        return await handle_calculate_registered_model(self.deps, request)

    @rpc_errors
    async def EstimateRegisteredModel(
        self, request: modelregistry_v1_registered_model_calculation_service_pb2.EstimateRegisteredModelRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_registered_model_calculation_service_pb2.EstimateRegisteredModelResponse:
        """Estimates a registered model."""
        return await handle_estimate_registered_model(self.deps, request)

    @rpc_errors
    async def ExplainRegisteredModelCalculation(
        self, request: modelregistry_v1_registered_model_calculation_service_pb2.ExplainRegisteredModelCalculationRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_registered_model_calculation_service_pb2.ExplainRegisteredModelCalculationResponse:
        """Explains a registered model."""
        return await handle_explain_registered_model_calculation(self.deps, request)

    @rpc_errors
    @retry_transient
    async def GetRegisteredModelRates(
        self, request: modelregistry_v1_registered_model_calculation_service_pb2.GetRegisteredModelRatesRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_registered_model_calculation_service_pb2.GetRegisteredModelRatesResponse:
        """Returns a registered model."""
        return await handle_get_registered_model_rates(self.deps, request)

    @rpc_errors
    async def QuoteRegisteredModel(
        self, request: modelregistry_v1_registered_model_calculation_service_pb2.QuoteRegisteredModelRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_registered_model_calculation_service_pb2.QuoteRegisteredModelResponse:
        """Quotes a registered model."""
        return await handle_quote_registered_model(self.deps, request)

    @rpc_errors
    async def RecalculateRegisteredModels(
        self, request: modelregistry_v1_registered_model_calculation_service_pb2.RecalculateRegisteredModelsRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_registered_model_calculation_service_pb2.RecalculateRegisteredModelsResponse:
        """Recalculates a registered model."""
        return await handle_recalculate_registered_models(self.deps, request)

    @rpc_errors
    async def SimulateRegisteredModel(
        self, request: modelregistry_v1_registered_model_calculation_service_pb2.SimulateRegisteredModelRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_registered_model_calculation_service_pb2.SimulateRegisteredModelResponse:
        """Simulates a registered model."""
        return await handle_simulate_registered_model(self.deps, request)
