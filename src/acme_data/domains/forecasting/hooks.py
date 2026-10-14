"""Replaceable partner hooks of the forecasting domain."""

from __future__ import annotations

from acme.careplans.v1 import care_plan_query_service_pb2 as careplans_v1_care_plan_query_service_pb2
from acme.careplans.v1 import care_plan_query_service_pb2_grpc as careplans_v1_care_plan_query_service_pb2_grpc
from acme.forecasting.v1 import (
    forecast_model_validation_service_pb2 as forecasting_v1_forecast_model_validation_service_pb2,
)
from acme.forecasting.v1 import (
    forecast_model_validation_service_pb2_grpc as forecasting_v1_forecast_model_validation_service_pb2_grpc,
)
from acme.labeling.v1 import annotation_workflow_service_pb2 as labeling_v1_annotation_workflow_service_pb2
from acme.labeling.v1 import annotation_workflow_service_pb2_grpc as labeling_v1_annotation_workflow_service_pb2_grpc
from acme.labeling.v1 import labeling_task_validation_service_pb2 as labeling_v1_labeling_task_validation_service_pb2
from acme.labeling.v1 import (
    labeling_task_validation_service_pb2_grpc as labeling_v1_labeling_task_validation_service_pb2_grpc,
)
from acme.ledger.v1 import ledger_account_validation_service_pb2 as ledger_v1_ledger_account_validation_service_pb2
from acme.ledger.v1 import (
    ledger_account_validation_service_pb2_grpc as ledger_v1_ledger_account_validation_service_pb2_grpc,
)
from acme.venues.v1 import venue_query_service_pb2 as venues_v1_venue_query_service_pb2
from acme.venues.v1 import venue_query_service_pb2_grpc as venues_v1_venue_query_service_pb2_grpc
from acme.venues.v1 import venue_validation_service_pb2 as venues_v1_venue_validation_service_pb2
from acme.venues.v1 import venue_validation_service_pb2_grpc as venues_v1_venue_validation_service_pb2_grpc


async def demand_forecast_query_export_demand_forecasts0(
    client: labeling_v1_labeling_task_validation_service_pb2_grpc.LabelingTaskValidationServiceStub,
    request: labeling_v1_labeling_task_validation_service_pb2.ExplainLabelingTaskDecisionRequest,
    timeout: float
) -> labeling_v1_labeling_task_validation_service_pb2.ExplainLabelingTaskDecisionResponse:
    raise RuntimeError("domain hook was not installed")


async def demand_forecast_create_demand_forecast1(
    client: forecasting_v1_forecast_model_validation_service_pb2_grpc.ForecastModelValidationServiceStub,
    request: forecasting_v1_forecast_model_validation_service_pb2.NormalizeForecastModelRequest,
    timeout: float
) -> forecasting_v1_forecast_model_validation_service_pb2.NormalizeForecastModelResponse:
    raise RuntimeError("domain hook was not installed")


async def forecast_model_approval_escalate_forecast_model2(
    client: ledger_v1_ledger_account_validation_service_pb2_grpc.LedgerAccountValidationServiceStub,
    request: ledger_v1_ledger_account_validation_service_pb2.ScoreLedgerAccountRequest,
    timeout: float
) -> ledger_v1_ledger_account_validation_service_pb2.ScoreLedgerAccountResponse:
    raise RuntimeError("domain hook was not installed")


async def forecast_model_query_summarize_forecast_models0(
    client: forecasting_v1_forecast_model_validation_service_pb2_grpc.ForecastModelValidationServiceStub,
    request: forecasting_v1_forecast_model_validation_service_pb2.CheckForecastModelEligibilityRequest,
    timeout: float
) -> forecasting_v1_forecast_model_validation_service_pb2.CheckForecastModelEligibilityResponse:
    raise RuntimeError("domain hook was not installed")


async def scenario_approval_comment_scenario_approval2(
    client: labeling_v1_annotation_workflow_service_pb2_grpc.AnnotationWorkflowServiceStub,
    request: labeling_v1_annotation_workflow_service_pb2.SignalAnnotationWorkflowRequest,
    timeout: float
) -> labeling_v1_annotation_workflow_service_pb2.SignalAnnotationWorkflowResponse:
    raise RuntimeError("domain hook was not installed")


async def scenario_calculation_estimate_scenario0(
    client: venues_v1_venue_query_service_pb2_grpc.VenueQueryServiceStub,
    request: venues_v1_venue_query_service_pb2.SummarizeVenuesRequest,
    timeout: float
) -> venues_v1_venue_query_service_pb2.SummarizeVenuesResponse:
    raise RuntimeError("domain hook was not installed")


async def scenario_validation_normalize_scenario0(
    client: venues_v1_venue_validation_service_pb2_grpc.VenueValidationServiceStub,
    request: venues_v1_venue_validation_service_pb2.LintVenuesRequest,
    timeout: float
) -> venues_v1_venue_validation_service_pb2.LintVenuesResponse:
    raise RuntimeError("domain hook was not installed")


async def scenario_workflow_pause_scenario_workflow1(
    client: careplans_v1_care_plan_query_service_pb2_grpc.CarePlanQueryServiceStub,
    request: careplans_v1_care_plan_query_service_pb2.ResolveCarePlansRequest,
    timeout: float
) -> careplans_v1_care_plan_query_service_pb2.ResolveCarePlansResponse:
    raise RuntimeError("domain hook was not installed")
