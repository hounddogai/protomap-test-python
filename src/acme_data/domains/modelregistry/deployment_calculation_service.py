"""Computes the figures of a deployment, such as totals, taxes, and estimates."""

from __future__ import annotations

from collections.abc import AsyncIterator

import grpc

from acme.modelregistry.v1 import (
    deployment_calculation_service_pb2 as modelregistry_v1_deployment_calculation_service_pb2,
)
from acme.modelregistry.v1 import (
    deployment_calculation_service_pb2_grpc as modelregistry_v1_deployment_calculation_service_pb2_grpc,
)

from acme_data.domains.modelregistry.dependencies import Dependencies
from acme_data.domains.modelregistry.deployment_calculation_service_workflow import (
    DeploymentCalculationServicerWorkflow,
)
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors


class DeploymentCalculationServicer(
    modelregistry_v1_deployment_calculation_service_pb2_grpc.DeploymentCalculationServiceServicer
):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps
        self.workflow = DeploymentCalculationServicerWorkflow(deps)

    @rpc_errors
    async def CalculateDeployment(
        self, request: modelregistry_v1_deployment_calculation_service_pb2.CalculateDeploymentRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_deployment_calculation_service_pb2.CalculateDeploymentResponse:
        """Calculates a deployment."""
        return await self.workflow.handle_calculate_deployment(request)

    @rpc_errors
    async def CompareDeploymentOptions(
        self, request: modelregistry_v1_deployment_calculation_service_pb2.CompareDeploymentOptionsRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_deployment_calculation_service_pb2.CompareDeploymentOptionsResponse:
        """Compares a deployment."""
        return await self.workflow.handle_compare_deployment_options(request)

    @rpc_errors
    async def EstimateDeployment(
        self, request: modelregistry_v1_deployment_calculation_service_pb2.EstimateDeploymentRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_deployment_calculation_service_pb2.EstimateDeploymentResponse:
        """Estimates a deployment."""
        return await self.workflow.handle_estimate_deployment(request)

    @rpc_errors
    @retry_transient
    async def GetDeploymentRates(
        self, request: modelregistry_v1_deployment_calculation_service_pb2.GetDeploymentRatesRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_deployment_calculation_service_pb2.GetDeploymentRatesResponse:
        """Returns a deployment."""
        return await self.workflow.handle_get_deployment_rates(request)

    @rpc_errors
    async def QuoteDeployment(
        self, request: modelregistry_v1_deployment_calculation_service_pb2.QuoteDeploymentRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_deployment_calculation_service_pb2.QuoteDeploymentResponse:
        """Quotes a deployment."""
        return await self.workflow.handle_quote_deployment(request)

    @rpc_errors
    async def RecalculateDeployments(
        self, request: modelregistry_v1_deployment_calculation_service_pb2.RecalculateDeploymentsRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_deployment_calculation_service_pb2.RecalculateDeploymentsResponse:
        """Recalculates a deployment."""
        return await self.workflow.handle_recalculate_deployments(request)
