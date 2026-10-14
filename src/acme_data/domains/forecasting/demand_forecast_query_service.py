"""Answers read-only questions about demand forecasts, for screens and reports."""

from __future__ import annotations

from collections.abc import AsyncIterator

import grpc

from acme.forecasting.v1 import demand_forecast_query_service_pb2 as forecasting_v1_demand_forecast_query_service_pb2
from acme.forecasting.v1 import (
    demand_forecast_query_service_pb2_grpc as forecasting_v1_demand_forecast_query_service_pb2_grpc,
)

from acme_data.domains.forecasting.demand_forecast_query_service_workflow import DemandForecastQueryServicerWorkflow
from acme_data.domains.forecasting.dependencies import Dependencies
from acme_data.platform.rpc import messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors


class DemandForecastQueryServicer(
    forecasting_v1_demand_forecast_query_service_pb2_grpc.DemandForecastQueryServiceServicer
):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps
        self.workflow = DemandForecastQueryServicerWorkflow(deps)

    @rpc_errors
    @retry_transient
    async def BrowseDemandForecasts(
        self, request: forecasting_v1_demand_forecast_query_service_pb2.BrowseDemandForecastsRequest, context: grpc.aio.ServicerContext,
    ) -> forecasting_v1_demand_forecast_query_service_pb2.BrowseDemandForecastsResponse:
        """Lists demand forecasts a page at a time."""
        return await self.workflow.handle_browse_demand_forecasts(request)

    @rpc_errors
    @retry_transient
    async def CountDemandForecasts(
        self, request: forecasting_v1_demand_forecast_query_service_pb2.CountDemandForecastsRequest, context: grpc.aio.ServicerContext,
    ) -> forecasting_v1_demand_forecast_query_service_pb2.CountDemandForecastsResponse:
        """Counts demand forecasts by status."""
        return await self.workflow.handle_count_demand_forecasts(request)

    @stream_errors
    async def ExportDemandForecasts(
        self, request: forecasting_v1_demand_forecast_query_service_pb2.ExportDemandForecastsRequest, context: grpc.aio.ServicerContext,
    ) -> AsyncIterator[forecasting_v1_demand_forecast_query_service_pb2.ExportDemandForecastsResponse]:
        """Streams every matching demand forecast."""
        response = await self.workflow.handle_export_demand_forecasts(request)
        for item in messages((response,)):
            yield item

    @rpc_errors
    @retry_transient
    async def FindDemandForecasts(
        self, request: forecasting_v1_demand_forecast_query_service_pb2.FindDemandForecastsRequest, context: grpc.aio.ServicerContext,
    ) -> forecasting_v1_demand_forecast_query_service_pb2.FindDemandForecastsResponse:
        """Lists demand forecasts a page at a time."""
        return await self.workflow.handle_find_demand_forecasts(request)

    @rpc_errors
    @retry_transient
    async def LookupDemandForecast(
        self, request: forecasting_v1_demand_forecast_query_service_pb2.LookupDemandForecastRequest, context: grpc.aio.ServicerContext,
    ) -> forecasting_v1_demand_forecast_query_service_pb2.LookupDemandForecastResponse:
        """Returns a demand forecast."""
        return await self.workflow.handle_lookup_demand_forecast(request)

    @rpc_errors
    @retry_transient
    async def PeekDemandForecast(
        self, request: forecasting_v1_demand_forecast_query_service_pb2.PeekDemandForecastRequest, context: grpc.aio.ServicerContext,
    ) -> forecasting_v1_demand_forecast_query_service_pb2.PeekDemandForecastResponse:
        """Returns a demand forecast."""
        return await self.workflow.handle_peek_demand_forecast(request)

    @rpc_errors
    @retry_transient
    async def ResolveDemandForecasts(
        self, request: forecasting_v1_demand_forecast_query_service_pb2.ResolveDemandForecastsRequest, context: grpc.aio.ServicerContext,
    ) -> forecasting_v1_demand_forecast_query_service_pb2.ResolveDemandForecastsResponse:
        """Returns several demand forecasts at once."""
        return await self.workflow.handle_resolve_demand_forecasts(request)

    @rpc_errors
    @retry_transient
    async def SuggestDemandForecasts(
        self, request: forecasting_v1_demand_forecast_query_service_pb2.SuggestDemandForecastsRequest, context: grpc.aio.ServicerContext,
    ) -> forecasting_v1_demand_forecast_query_service_pb2.SuggestDemandForecastsResponse:
        """Lists demand forecasts a page at a time."""
        return await self.workflow.handle_suggest_demand_forecasts(request)

    @rpc_errors
    async def SummarizeDemandForecasts(
        self, request: forecasting_v1_demand_forecast_query_service_pb2.SummarizeDemandForecastsRequest, context: grpc.aio.ServicerContext,
    ) -> forecasting_v1_demand_forecast_query_service_pb2.SummarizeDemandForecastsResponse:
        """Summarizes a demand forecast."""
        return await self.workflow.handle_summarize_demand_forecasts(request)
