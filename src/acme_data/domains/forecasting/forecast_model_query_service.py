"""Answers read-only questions about forecast models, for screens and reports."""

from __future__ import annotations

from collections.abc import AsyncIterator

import grpc

from acme.forecasting.v1 import forecast_model_query_service_pb2 as forecasting_v1_forecast_model_query_service_pb2
from acme.forecasting.v1 import (
    forecast_model_query_service_pb2_grpc as forecasting_v1_forecast_model_query_service_pb2_grpc,
)

from acme_data.domains.forecasting.dependencies import Dependencies
from acme_data.domains.forecasting.forecast_model_query_service_workflow import ForecastModelQueryServicerWorkflow
from acme_data.platform.rpc import messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors


class ForecastModelQueryServicer(
    forecasting_v1_forecast_model_query_service_pb2_grpc.ForecastModelQueryServiceServicer
):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps
        self.workflow = ForecastModelQueryServicerWorkflow(deps)

    @rpc_errors
    @retry_transient
    async def BrowseForecastModels(
        self, request: forecasting_v1_forecast_model_query_service_pb2.BrowseForecastModelsRequest, context: grpc.aio.ServicerContext,
    ) -> forecasting_v1_forecast_model_query_service_pb2.BrowseForecastModelsResponse:
        """Lists forecast models a page at a time."""
        return await self.workflow.handle_browse_forecast_models(request)

    @rpc_errors
    @retry_transient
    async def CountForecastModels(
        self, request: forecasting_v1_forecast_model_query_service_pb2.CountForecastModelsRequest, context: grpc.aio.ServicerContext,
    ) -> forecasting_v1_forecast_model_query_service_pb2.CountForecastModelsResponse:
        """Counts forecast models by status."""
        return await self.workflow.handle_count_forecast_models(request)

    @stream_errors
    async def ExportForecastModels(
        self, request: forecasting_v1_forecast_model_query_service_pb2.ExportForecastModelsRequest, context: grpc.aio.ServicerContext,
    ) -> AsyncIterator[forecasting_v1_forecast_model_query_service_pb2.ExportForecastModelsResponse]:
        """Streams every matching forecast model."""
        response = await self.workflow.handle_export_forecast_models(request)
        for item in messages((response,)):
            yield item

    @rpc_errors
    @retry_transient
    async def FindForecastModels(
        self, request: forecasting_v1_forecast_model_query_service_pb2.FindForecastModelsRequest, context: grpc.aio.ServicerContext,
    ) -> forecasting_v1_forecast_model_query_service_pb2.FindForecastModelsResponse:
        """Lists forecast models a page at a time."""
        return await self.workflow.handle_find_forecast_models(request)

    @rpc_errors
    @retry_transient
    async def LookupForecastModel(
        self, request: forecasting_v1_forecast_model_query_service_pb2.LookupForecastModelRequest, context: grpc.aio.ServicerContext,
    ) -> forecasting_v1_forecast_model_query_service_pb2.LookupForecastModelResponse:
        """Returns a forecast model."""
        return await self.workflow.handle_lookup_forecast_model(request)

    @rpc_errors
    @retry_transient
    async def PeekForecastModel(
        self, request: forecasting_v1_forecast_model_query_service_pb2.PeekForecastModelRequest, context: grpc.aio.ServicerContext,
    ) -> forecasting_v1_forecast_model_query_service_pb2.PeekForecastModelResponse:
        """Returns a forecast model."""
        return await self.workflow.handle_peek_forecast_model(request)

    @rpc_errors
    @retry_transient
    async def ResolveForecastModels(
        self, request: forecasting_v1_forecast_model_query_service_pb2.ResolveForecastModelsRequest, context: grpc.aio.ServicerContext,
    ) -> forecasting_v1_forecast_model_query_service_pb2.ResolveForecastModelsResponse:
        """Returns several forecast models at once."""
        return await self.workflow.handle_resolve_forecast_models(request)

    @rpc_errors
    @retry_transient
    async def SuggestForecastModels(
        self, request: forecasting_v1_forecast_model_query_service_pb2.SuggestForecastModelsRequest, context: grpc.aio.ServicerContext,
    ) -> forecasting_v1_forecast_model_query_service_pb2.SuggestForecastModelsResponse:
        """Lists forecast models a page at a time."""
        return await self.workflow.handle_suggest_forecast_models(request)

    @rpc_errors
    async def SummarizeForecastModels(
        self, request: forecasting_v1_forecast_model_query_service_pb2.SummarizeForecastModelsRequest, context: grpc.aio.ServicerContext,
    ) -> forecasting_v1_forecast_model_query_service_pb2.SummarizeForecastModelsResponse:
        """Summarizes a forecast model."""
        return await self.workflow.handle_summarize_forecast_models(request)
