"""Computes the figures of a pipeline run, such as totals, taxes, and estimates."""

from __future__ import annotations

from collections.abc import AsyncIterator

import grpc

from acme.pipelines.v1 import pipeline_run_calculation_service_pb2 as pipelines_v1_pipeline_run_calculation_service_pb2
from acme.pipelines.v1 import (
    pipeline_run_calculation_service_pb2_grpc as pipelines_v1_pipeline_run_calculation_service_pb2_grpc,
)

from acme_data.domains.pipelines.dependencies import Dependencies
from acme_data.domains.pipelines.pipeline_run_calculation_service_workflow import PipelineRunCalculationServicerWorkflow
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors


class PipelineRunCalculationServicer(
    pipelines_v1_pipeline_run_calculation_service_pb2_grpc.PipelineRunCalculationServiceServicer
):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps
        self.workflow = PipelineRunCalculationServicerWorkflow(deps)

    @rpc_errors
    async def CalculatePipelineRun(
        self, request: pipelines_v1_pipeline_run_calculation_service_pb2.CalculatePipelineRunRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_run_calculation_service_pb2.CalculatePipelineRunResponse:
        """Calculates a pipeline run."""
        return await self.workflow.handle_calculate_pipeline_run(request)

    @rpc_errors
    async def ComparePipelineRunOptions(
        self, request: pipelines_v1_pipeline_run_calculation_service_pb2.ComparePipelineRunOptionsRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_run_calculation_service_pb2.ComparePipelineRunOptionsResponse:
        """Compares a pipeline run."""
        return await self.workflow.handle_compare_pipeline_run_options(request)

    @rpc_errors
    async def EstimatePipelineRun(
        self, request: pipelines_v1_pipeline_run_calculation_service_pb2.EstimatePipelineRunRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_run_calculation_service_pb2.EstimatePipelineRunResponse:
        """Estimates a pipeline run."""
        return await self.workflow.handle_estimate_pipeline_run(request)

    @rpc_errors
    async def ExplainPipelineRunCalculation(
        self, request: pipelines_v1_pipeline_run_calculation_service_pb2.ExplainPipelineRunCalculationRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_run_calculation_service_pb2.ExplainPipelineRunCalculationResponse:
        """Explains a pipeline run."""
        return await self.workflow.handle_explain_pipeline_run_calculation(request)

    @rpc_errors
    @retry_transient
    async def GetPipelineRunRates(
        self, request: pipelines_v1_pipeline_run_calculation_service_pb2.GetPipelineRunRatesRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_run_calculation_service_pb2.GetPipelineRunRatesResponse:
        """Returns a pipeline run."""
        return await self.workflow.handle_get_pipeline_run_rates(request)

    @rpc_errors
    async def QuotePipelineRun(
        self, request: pipelines_v1_pipeline_run_calculation_service_pb2.QuotePipelineRunRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_run_calculation_service_pb2.QuotePipelineRunResponse:
        """Quotes a pipeline run."""
        return await self.workflow.handle_quote_pipeline_run(request)

    @rpc_errors
    async def RecalculatePipelineRuns(
        self, request: pipelines_v1_pipeline_run_calculation_service_pb2.RecalculatePipelineRunsRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_run_calculation_service_pb2.RecalculatePipelineRunsResponse:
        """Recalculates a pipeline run."""
        return await self.workflow.handle_recalculate_pipeline_runs(request)
