"""Runs the long-lived workflow that takes a forecast model from start to finish."""

from __future__ import annotations

from collections.abc import AsyncIterator

import grpc

from acme.forecasting.v1 import (
    forecast_model_workflow_service_pb2_grpc as forecasting_v1_forecast_model_workflow_service_pb2_grpc,
)

from acme_data.domains.forecasting.dependencies import Dependencies
from acme_data.domains.forecasting.forecast_model_workflow_service_handlers import ForecastModelWorkflowServicerHandlers
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors


class ForecastModelWorkflowServicer(
    ForecastModelWorkflowServicerHandlers,
    forecasting_v1_forecast_model_workflow_service_pb2_grpc.ForecastModelWorkflowServiceServicer
):
    """Runs the long-lived workflow that takes a forecast model from start to finish."""
