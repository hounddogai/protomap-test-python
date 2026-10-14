"""Checks demand forecasts against the rules before anything acts on them."""

from __future__ import annotations

from collections.abc import AsyncIterator

import grpc

from acme.forecasting.v1 import (
    demand_forecast_validation_service_pb2_grpc as forecasting_v1_demand_forecast_validation_service_pb2_grpc,
)

from acme_data.domains.forecasting.demand_forecast_validation_service_handlers import (
    DemandForecastValidationServicerHandlers,
)
from acme_data.domains.forecasting.dependencies import Dependencies
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors


class DemandForecastValidationServicer(
    DemandForecastValidationServicerHandlers,
    forecasting_v1_demand_forecast_validation_service_pb2_grpc.DemandForecastValidationServiceServicer
):
    """Checks demand forecasts against the rules before anything acts on them."""
