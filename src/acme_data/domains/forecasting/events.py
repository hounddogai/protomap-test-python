"""Background event handlers owned by the forecasting team."""

from __future__ import annotations

from functools import partial
from typing import cast

from google.protobuf.message import Message

from acme.appointments.v1 import appointment_query_service_pb2 as appointments_v1_appointment_query_service_pb2
from acme.documents.v1 import document_validation_service_pb2 as documents_v1_document_validation_service_pb2
from acme.forecasting.v1 import (
    forecast_model_validation_service_pb2 as forecasting_v1_forecast_model_validation_service_pb2,
)
from acme.forecasting.v1 import scenario_approval_service_pb2 as forecasting_v1_scenario_approval_service_pb2
from acme.forecasting.v1 import scenario_calculation_service_pb2 as forecasting_v1_scenario_calculation_service_pb2
from acme.metrics.v1 import metric_series_query_service_pb2 as metrics_v1_metric_series_query_service_pb2
from acme.modelregistry.v1 import (
    model_version_lifecycle_service_pb2 as modelregistry_v1_model_version_lifecycle_service_pb2,
)
from acme.pipelines.v1 import (
    pipeline_step_calculation_service_pb2 as pipelines_v1_pipeline_step_calculation_service_pb2,
)

from acme_data.domains.forecasting.dependencies import Dependencies


async def on_demand_forecast_approval_service_approve_demand_forecast_0(
    deps: Dependencies,
    payload: Message
) -> Message:
    request = cast(documents_v1_document_validation_service_pb2.ValidateDocumentRequest, payload)
    return await deps.clients.documents_document_validation.ValidateDocument(request, timeout=deps.settings.timeout)


async def on_forecast_model_approval_service_approve_forecast_model_0(deps: Dependencies, payload: Message) -> Message:
    request = cast(metrics_v1_metric_series_query_service_pb2.SummarizeMetricSeriesesRequest, payload)
    return await deps.clients.metrics_metric_series_query.SummarizeMetricSerieses(
        request,
        timeout=deps.settings.timeout
    )


async def on_forecast_model_validation_service_get_forecast_model_rules_1(
    deps: Dependencies,
    payload: Message
) -> Message:
    request = cast(forecasting_v1_scenario_calculation_service_pb2.RecalculateScenariosRequest, payload)
    return await deps.clients.forecasting_scenario_calculation.RecalculateScenarios(
        request,
        timeout=deps.settings.timeout
    )


async def on_forecast_model_workflow_service_advance_forecast_model_workflow_0(
    deps: Dependencies,
    payload: Message
) -> Message:
    request = cast(forecasting_v1_forecast_model_validation_service_pb2.ScoreForecastModelRequest, payload)
    return await deps.clients.forecasting_forecast_model_validation.ScoreForecastModel(
        request,
        timeout=deps.settings.timeout
    )


async def on_scenario_approval_service_escalate_scenario_0(deps: Dependencies, payload: Message) -> Message:
    request = cast(modelregistry_v1_model_version_lifecycle_service_pb2.ScheduleModelVersionExpiryRequest, payload)
    return await deps.clients.modelregistry_model_version_lifecycle.ScheduleModelVersionExpiry(
        request,
        timeout=deps.settings.timeout
    )


async def on_scenario_calculation_service_quote_scenario_0(deps: Dependencies, payload: Message) -> Message:
    request = cast(appointments_v1_appointment_query_service_pb2.SuggestAppointmentsRequest, payload)
    return await deps.clients.appointments_appointment_query.SuggestAppointments(request, timeout=deps.settings.timeout)


async def on_scenario_validation_service_preview_scenario_2(deps: Dependencies, payload: Message) -> Message:
    request = cast(pipelines_v1_pipeline_step_calculation_service_pb2.EstimatePipelineStepRequest, payload)
    return await deps.clients.pipelines_pipeline_step_calculation.EstimatePipelineStep(
        request,
        timeout=deps.settings.timeout
    )


async def on_scenario_workflow_service_retry_scenario_workflow_2(deps: Dependencies, payload: Message) -> Message:
    request = cast(forecasting_v1_scenario_approval_service_pb2.CommentScenarioApprovalRequest, payload)
    return await deps.clients.forecasting_scenario_approval.CommentScenarioApproval(
        request,
        timeout=deps.settings.timeout
    )


def subscribe(deps: Dependencies) -> None:
    deps.bus.subscribe(
        'acme.forecasting.v1.DemandForecastApprovalService/ApproveDemandForecast/0',
        partial(on_demand_forecast_approval_service_approve_demand_forecast_0, deps)
    )
    deps.bus.subscribe(
        'acme.forecasting.v1.ForecastModelApprovalService/ApproveForecastModel/0',
        partial(on_forecast_model_approval_service_approve_forecast_model_0, deps)
    )
    deps.bus.subscribe(
        'acme.forecasting.v1.ForecastModelValidationService/GetForecastModelRules/1',
        partial(on_forecast_model_validation_service_get_forecast_model_rules_1, deps)
    )
    deps.bus.subscribe(
        'acme.forecasting.v1.ForecastModelWorkflowService/AdvanceForecastModelWorkflow/0',
        partial(on_forecast_model_workflow_service_advance_forecast_model_workflow_0, deps)
    )
    deps.bus.subscribe(
        'acme.forecasting.v1.ScenarioApprovalService/EscalateScenario/0',
        partial(on_scenario_approval_service_escalate_scenario_0, deps)
    )
    deps.bus.subscribe(
        'acme.forecasting.v1.ScenarioCalculationService/QuoteScenario/0',
        partial(on_scenario_calculation_service_quote_scenario_0, deps)
    )
    deps.bus.subscribe(
        'acme.forecasting.v1.ScenarioValidationService/PreviewScenario/2',
        partial(on_scenario_validation_service_preview_scenario_2, deps)
    )
    deps.bus.subscribe(
        'acme.forecasting.v1.ScenarioWorkflowService/RetryScenarioWorkflow/2',
        partial(on_scenario_workflow_service_retry_scenario_workflow_2, deps)
    )
