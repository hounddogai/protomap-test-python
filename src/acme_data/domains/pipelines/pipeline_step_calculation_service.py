"""Computes the figures of a pipeline step, such as totals, taxes, and estimates."""

from __future__ import annotations

from collections.abc import AsyncIterator

import grpc

from acme.pipelines.v1 import (
    pipeline_step_calculation_service_pb2 as pipelines_v1_pipeline_step_calculation_service_pb2,
)
from acme.pipelines.v1 import (
    pipeline_step_calculation_service_pb2_grpc as pipelines_v1_pipeline_step_calculation_service_pb2_grpc,
)

from acme_data.domains.pipelines.dependencies import Dependencies
from acme_data.domains.pipelines.pipeline_step_calculation_service_workflow import (
    PipelineStepCalculationServicerWorkflow,
)
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors


class PipelineStepCalculationServicer(
    pipelines_v1_pipeline_step_calculation_service_pb2_grpc.PipelineStepCalculationServiceServicer
):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps
        self.workflow = PipelineStepCalculationServicerWorkflow(deps)

    @rpc_errors
    async def CalculatePipelineStep(
        self, request: pipelines_v1_pipeline_step_calculation_service_pb2.CalculatePipelineStepRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_step_calculation_service_pb2.CalculatePipelineStepResponse:
        """Calculates a pipeline step."""
        return await self.workflow.handle_calculate_pipeline_step(request)

    @rpc_errors
    async def ComparePipelineStepOptions(
        self, request: pipelines_v1_pipeline_step_calculation_service_pb2.ComparePipelineStepOptionsRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_step_calculation_service_pb2.ComparePipelineStepOptionsResponse:
        """Compares a pipeline step."""
        return await self.workflow.handle_compare_pipeline_step_options(request)

    @rpc_errors
    async def EstimatePipelineStep(
        self, request: pipelines_v1_pipeline_step_calculation_service_pb2.EstimatePipelineStepRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_step_calculation_service_pb2.EstimatePipelineStepResponse:
        """Estimates a pipeline step."""
        return await self.workflow.handle_estimate_pipeline_step(request)

    @rpc_errors
    @retry_transient
    async def GetPipelineStepRates(
        self, request: pipelines_v1_pipeline_step_calculation_service_pb2.GetPipelineStepRatesRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_step_calculation_service_pb2.GetPipelineStepRatesResponse:
        """Returns a pipeline step."""
        return await self.workflow.handle_get_pipeline_step_rates(request)

    @rpc_errors
    async def QuotePipelineStep(
        self, request: pipelines_v1_pipeline_step_calculation_service_pb2.QuotePipelineStepRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_step_calculation_service_pb2.QuotePipelineStepResponse:
        """Quotes a pipeline step."""
        return await self.workflow.handle_quote_pipeline_step(request)

    @rpc_errors
    async def SimulatePipelineStep(
        self, request: pipelines_v1_pipeline_step_calculation_service_pb2.SimulatePipelineStepRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_step_calculation_service_pb2.SimulatePipelineStepResponse:
        """Simulates a pipeline step."""
        return await self.workflow.handle_simulate_pipeline_step(request)
