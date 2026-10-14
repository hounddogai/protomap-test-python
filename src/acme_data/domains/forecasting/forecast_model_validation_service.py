"""Checks forecast models against the rules before anything acts on them."""

from __future__ import annotations

from collections.abc import AsyncIterator

import grpc

from acme.forecasting.v1 import (
    forecast_model_validation_service_pb2 as forecasting_v1_forecast_model_validation_service_pb2,
)
from acme.forecasting.v1 import (
    forecast_model_validation_service_pb2_grpc as forecasting_v1_forecast_model_validation_service_pb2_grpc,
)

from acme_data.domains.forecasting.dependencies import Dependencies
from acme_data.domains.forecasting.forecast_model_validation_service_operations import (
    handle_check_forecast_model_eligibility,
)
from acme_data.domains.forecasting.forecast_model_validation_service_operations import handle_get_forecast_model_rules
from acme_data.domains.forecasting.forecast_model_validation_service_operations import handle_lint_forecast_models
from acme_data.domains.forecasting.forecast_model_validation_service_operations import handle_normalize_forecast_model
from acme_data.domains.forecasting.forecast_model_validation_service_operations import handle_preview_forecast_model
from acme_data.domains.forecasting.forecast_model_validation_service_operations import handle_score_forecast_model
from acme_data.domains.forecasting.forecast_model_validation_service_operations import handle_validate_forecast_model
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors


class ForecastModelValidationServicer(
    forecasting_v1_forecast_model_validation_service_pb2_grpc.ForecastModelValidationServiceServicer
):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    async def CheckForecastModelEligibility(
        self, request: forecasting_v1_forecast_model_validation_service_pb2.CheckForecastModelEligibilityRequest, context: grpc.aio.ServicerContext,
    ) -> forecasting_v1_forecast_model_validation_service_pb2.CheckForecastModelEligibilityResponse:
        """Checks a forecast model."""
        return await handle_check_forecast_model_eligibility(self.deps, request)

    @rpc_errors
    @retry_transient
    async def GetForecastModelRules(
        self, request: forecasting_v1_forecast_model_validation_service_pb2.GetForecastModelRulesRequest, context: grpc.aio.ServicerContext,
    ) -> forecasting_v1_forecast_model_validation_service_pb2.GetForecastModelRulesResponse:
        """Returns a forecast model."""
        return await handle_get_forecast_model_rules(self.deps, request)

    @rpc_errors
    async def LintForecastModels(
        self, request: forecasting_v1_forecast_model_validation_service_pb2.LintForecastModelsRequest, context: grpc.aio.ServicerContext,
    ) -> forecasting_v1_forecast_model_validation_service_pb2.LintForecastModelsResponse:
        """Lints a forecast model."""
        return await handle_lint_forecast_models(self.deps, request)

    @rpc_errors
    async def NormalizeForecastModel(
        self, request: forecasting_v1_forecast_model_validation_service_pb2.NormalizeForecastModelRequest, context: grpc.aio.ServicerContext,
    ) -> forecasting_v1_forecast_model_validation_service_pb2.NormalizeForecastModelResponse:
        """Normalizes a forecast model."""
        return await handle_normalize_forecast_model(self.deps, request)

    @rpc_errors
    async def PreviewForecastModel(
        self, request: forecasting_v1_forecast_model_validation_service_pb2.PreviewForecastModelRequest, context: grpc.aio.ServicerContext,
    ) -> forecasting_v1_forecast_model_validation_service_pb2.PreviewForecastModelResponse:
        """Previews a forecast model."""
        return await handle_preview_forecast_model(self.deps, request)

    @rpc_errors
    async def ScoreForecastModel(
        self, request: forecasting_v1_forecast_model_validation_service_pb2.ScoreForecastModelRequest, context: grpc.aio.ServicerContext,
    ) -> forecasting_v1_forecast_model_validation_service_pb2.ScoreForecastModelResponse:
        """Scores a forecast model."""
        return await handle_score_forecast_model(self.deps, request)

    @rpc_errors
    async def ValidateForecastModel(
        self, request: forecasting_v1_forecast_model_validation_service_pb2.ValidateForecastModelRequest, context: grpc.aio.ServicerContext,
    ) -> forecasting_v1_forecast_model_validation_service_pb2.ValidateForecastModelResponse:
        """Validates a forecast model."""
        return await handle_validate_forecast_model(self.deps, request)
