"""Manages demand forecasts: creates, reads, changes, and lists them."""

from __future__ import annotations

from collections.abc import AsyncIterator

import grpc

from acme.forecasting.v1 import demand_forecast_service_pb2 as forecasting_v1_demand_forecast_service_pb2
from acme.forecasting.v1 import demand_forecast_service_pb2_grpc as forecasting_v1_demand_forecast_service_pb2_grpc

from acme_data.domains.forecasting.demand_forecast_service_operations import handle_batch_create_demand_forecasts
from acme_data.domains.forecasting.demand_forecast_service_operations import handle_batch_get_demand_forecasts
from acme_data.domains.forecasting.demand_forecast_service_operations import handle_clone_demand_forecast
from acme_data.domains.forecasting.demand_forecast_service_operations import handle_create_demand_forecast
from acme_data.domains.forecasting.demand_forecast_service_operations import handle_delete_demand_forecast
from acme_data.domains.forecasting.demand_forecast_service_operations import handle_get_demand_forecast
from acme_data.domains.forecasting.demand_forecast_service_operations import handle_list_demand_forecasts
from acme_data.domains.forecasting.demand_forecast_service_operations import handle_search_demand_forecasts
from acme_data.domains.forecasting.demand_forecast_service_operations import handle_update_demand_forecast
from acme_data.domains.forecasting.dependencies import Dependencies
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors


class DemandForecastServicer(forecasting_v1_demand_forecast_service_pb2_grpc.DemandForecastServiceServicer):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    async def BatchCreateDemandForecasts(
        self, requests: AsyncIterator[
            forecasting_v1_demand_forecast_service_pb2.BatchCreateDemandForecastsRequest
        ], context: grpc.aio.ServicerContext,
    ) -> forecasting_v1_demand_forecast_service_pb2.BatchCreateDemandForecastsResponse:
        """Takes a stream of demand forecasts and answers once at the end."""
        response = forecasting_v1_demand_forecast_service_pb2.BatchCreateDemandForecastsResponse()
        async for request in requests:
            response.MergeFrom(await handle_batch_create_demand_forecasts(self.deps, request))
        return response

    @rpc_errors
    @retry_transient
    async def BatchGetDemandForecasts(
        self, request: forecasting_v1_demand_forecast_service_pb2.BatchGetDemandForecastsRequest, context: grpc.aio.ServicerContext,
    ) -> forecasting_v1_demand_forecast_service_pb2.BatchGetDemandForecastsResponse:
        """Returns several demand forecasts at once."""
        return await handle_batch_get_demand_forecasts(self.deps, request)

    @rpc_errors
    async def CloneDemandForecast(
        self, request: forecasting_v1_demand_forecast_service_pb2.CloneDemandForecastRequest, context: grpc.aio.ServicerContext,
    ) -> forecasting_v1_demand_forecast_service_pb2.CloneDemandForecastResponse:
        """Creates a demand forecast."""
        return await handle_clone_demand_forecast(self.deps, request)

    @rpc_errors
    async def CreateDemandForecast(
        self, request: forecasting_v1_demand_forecast_service_pb2.CreateDemandForecastRequest, context: grpc.aio.ServicerContext,
    ) -> forecasting_v1_demand_forecast_service_pb2.CreateDemandForecastResponse:
        """Creates a demand forecast."""
        return await handle_create_demand_forecast(self.deps, request)

    @rpc_errors
    async def DeleteDemandForecast(
        self, request: forecasting_v1_demand_forecast_service_pb2.DeleteDemandForecastRequest, context: grpc.aio.ServicerContext,
    ) -> forecasting_v1_demand_forecast_service_pb2.DeleteDemandForecastResponse:
        """Deletes a demand forecast."""
        return await handle_delete_demand_forecast(self.deps, request)

    @rpc_errors
    @retry_transient
    async def GetDemandForecast(
        self, request: forecasting_v1_demand_forecast_service_pb2.GetDemandForecastRequest, context: grpc.aio.ServicerContext,
    ) -> forecasting_v1_demand_forecast_service_pb2.GetDemandForecastResponse:
        """Returns a demand forecast."""
        return await handle_get_demand_forecast(self.deps, request)

    @rpc_errors
    @retry_transient
    async def ListDemandForecasts(
        self, request: forecasting_v1_demand_forecast_service_pb2.ListDemandForecastsRequest, context: grpc.aio.ServicerContext,
    ) -> forecasting_v1_demand_forecast_service_pb2.ListDemandForecastsResponse:
        """Lists demand forecasts a page at a time."""
        return await handle_list_demand_forecasts(self.deps, request)

    @rpc_errors
    @retry_transient
    async def SearchDemandForecasts(
        self, request: forecasting_v1_demand_forecast_service_pb2.SearchDemandForecastsRequest, context: grpc.aio.ServicerContext,
    ) -> forecasting_v1_demand_forecast_service_pb2.SearchDemandForecastsResponse:
        """Lists demand forecasts a page at a time."""
        return await handle_search_demand_forecasts(self.deps, request)

    @rpc_errors
    async def UpdateDemandForecast(
        self, request: forecasting_v1_demand_forecast_service_pb2.UpdateDemandForecastRequest, context: grpc.aio.ServicerContext,
    ) -> forecasting_v1_demand_forecast_service_pb2.UpdateDemandForecastResponse:
        """Changes a demand forecast."""
        return await handle_update_demand_forecast(self.deps, request)
