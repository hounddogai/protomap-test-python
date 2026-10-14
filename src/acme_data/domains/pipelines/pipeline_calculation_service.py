"""Computes the figures of a pipeline, such as totals, taxes, and estimates."""

from __future__ import annotations

from collections.abc import AsyncIterator

import grpc

from acme.pipelines.v1 import pipeline_calculation_service_pb2 as pipelines_v1_pipeline_calculation_service_pb2
from acme.pipelines.v1 import (
    pipeline_calculation_service_pb2_grpc as pipelines_v1_pipeline_calculation_service_pb2_grpc,
)

from acme_data.domains.pipelines.dependencies import Dependencies
from acme_data.domains.pipelines.pipeline_calculation_service_workflow import PipelineCalculationServicerWorkflow
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors


class PipelineCalculationServicer(
    pipelines_v1_pipeline_calculation_service_pb2_grpc.PipelineCalculationServiceServicer
):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps
        self.workflow = PipelineCalculationServicerWorkflow(deps)

    @rpc_errors
    async def CalculatePipeline(
        self, request: pipelines_v1_pipeline_calculation_service_pb2.CalculatePipelineRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_calculation_service_pb2.CalculatePipelineResponse:
        """Calculates a pipeline."""
        return await self.workflow.handle_calculate_pipeline(request)

    @rpc_errors
    async def ComparePipelineOptions(
        self, request: pipelines_v1_pipeline_calculation_service_pb2.ComparePipelineOptionsRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_calculation_service_pb2.ComparePipelineOptionsResponse:
        """Compares a pipeline."""
        return await self.workflow.handle_compare_pipeline_options(request)

    @rpc_errors
    async def EstimatePipeline(
        self, request: pipelines_v1_pipeline_calculation_service_pb2.EstimatePipelineRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_calculation_service_pb2.EstimatePipelineResponse:
        """Estimates a pipeline."""
        return await self.workflow.handle_estimate_pipeline(request)

    @rpc_errors
    async def ExplainPipelineCalculation(
        self, request: pipelines_v1_pipeline_calculation_service_pb2.ExplainPipelineCalculationRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_calculation_service_pb2.ExplainPipelineCalculationResponse:
        """Explains a pipeline."""
        return await self.workflow.handle_explain_pipeline_calculation(request)

    @rpc_errors
    @retry_transient
    async def GetPipelineRates(
        self, request: pipelines_v1_pipeline_calculation_service_pb2.GetPipelineRatesRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_calculation_service_pb2.GetPipelineRatesResponse:
        """Returns a pipeline."""
        return await self.workflow.handle_get_pipeline_rates(request)

    @rpc_errors
    async def RecalculatePipelines(
        self, request: pipelines_v1_pipeline_calculation_service_pb2.RecalculatePipelinesRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_calculation_service_pb2.RecalculatePipelinesResponse:
        """Recalculates a pipeline."""
        return await self.workflow.handle_recalculate_pipelines(request)

    @rpc_errors
    async def SimulatePipeline(
        self, request: pipelines_v1_pipeline_calculation_service_pb2.SimulatePipelineRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_calculation_service_pb2.SimulatePipelineResponse:
        """Simulates a pipeline."""
        return await self.workflow.handle_simulate_pipeline(request)
