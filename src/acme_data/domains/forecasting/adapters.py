"""Transport adapters used by forecasting workflows."""

from __future__ import annotations

from typing import Protocol

from acme.authorization.v1 import (
    access_policy_validation_service_pb2 as authorization_v1_access_policy_validation_service_pb2,
)
from acme.authorization.v1 import (
    access_policy_validation_service_pb2_grpc as authorization_v1_access_policy_validation_service_pb2_grpc,
)
from acme.careplans.v1 import care_plan_query_service_pb2 as careplans_v1_care_plan_query_service_pb2
from acme.careplans.v1 import care_plan_query_service_pb2_grpc as careplans_v1_care_plan_query_service_pb2_grpc
from acme.documents.v1 import document_validation_service_pb2 as documents_v1_document_validation_service_pb2
from acme.documents.v1 import document_validation_service_pb2_grpc as documents_v1_document_validation_service_pb2_grpc
from acme.featureflags.v1 import feature_flag_service_pb2 as featureflags_v1_feature_flag_service_pb2
from acme.featureflags.v1 import feature_flag_service_pb2_grpc as featureflags_v1_feature_flag_service_pb2_grpc
from acme.featurestore.v1 import entity_approval_service_pb2 as featurestore_v1_entity_approval_service_pb2
from acme.featurestore.v1 import entity_approval_service_pb2_grpc as featurestore_v1_entity_approval_service_pb2_grpc
from acme.forecasting.v1 import (
    demand_forecast_approval_service_pb2 as forecasting_v1_demand_forecast_approval_service_pb2,
)
from acme.forecasting.v1 import (
    demand_forecast_approval_service_pb2_grpc as forecasting_v1_demand_forecast_approval_service_pb2_grpc,
)
from acme.forecasting.v1 import (
    demand_forecast_validation_service_pb2 as forecasting_v1_demand_forecast_validation_service_pb2,
)
from acme.forecasting.v1 import (
    demand_forecast_validation_service_pb2_grpc as forecasting_v1_demand_forecast_validation_service_pb2_grpc,
)
from acme.forecasting.v1 import forecast_model_query_service_pb2 as forecasting_v1_forecast_model_query_service_pb2
from acme.forecasting.v1 import (
    forecast_model_query_service_pb2_grpc as forecasting_v1_forecast_model_query_service_pb2_grpc,
)
from acme.forecasting.v1 import (
    forecast_model_validation_service_pb2 as forecasting_v1_forecast_model_validation_service_pb2,
)
from acme.forecasting.v1 import (
    forecast_model_validation_service_pb2_grpc as forecasting_v1_forecast_model_validation_service_pb2_grpc,
)
from acme.labeling.v1 import annotation_workflow_service_pb2 as labeling_v1_annotation_workflow_service_pb2
from acme.labeling.v1 import annotation_workflow_service_pb2_grpc as labeling_v1_annotation_workflow_service_pb2_grpc
from acme.labeling.v1 import labeling_task_query_service_pb2 as labeling_v1_labeling_task_query_service_pb2
from acme.labeling.v1 import labeling_task_query_service_pb2_grpc as labeling_v1_labeling_task_query_service_pb2_grpc
from acme.labeling.v1 import labeling_task_validation_service_pb2 as labeling_v1_labeling_task_validation_service_pb2
from acme.labeling.v1 import (
    labeling_task_validation_service_pb2_grpc as labeling_v1_labeling_task_validation_service_pb2_grpc,
)
from acme.ledger.v1 import ledger_account_validation_service_pb2 as ledger_v1_ledger_account_validation_service_pb2
from acme.ledger.v1 import (
    ledger_account_validation_service_pb2_grpc as ledger_v1_ledger_account_validation_service_pb2_grpc,
)
from acme.metrics.v1 import dashboard_validation_service_pb2 as metrics_v1_dashboard_validation_service_pb2
from acme.metrics.v1 import dashboard_validation_service_pb2_grpc as metrics_v1_dashboard_validation_service_pb2_grpc
from acme.patients.v1 import patient_query_service_pb2 as patients_v1_patient_query_service_pb2
from acme.patients.v1 import patient_query_service_pb2_grpc as patients_v1_patient_query_service_pb2_grpc
from acme.pipelines.v1 import pipeline_run_validation_service_pb2 as pipelines_v1_pipeline_run_validation_service_pb2
from acme.pipelines.v1 import (
    pipeline_run_validation_service_pb2_grpc as pipelines_v1_pipeline_run_validation_service_pb2_grpc,
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
    return await client.ExplainLabelingTaskDecision(request, timeout=timeout)


async def demand_forecast_create_demand_forecast1(
    client: forecasting_v1_forecast_model_validation_service_pb2_grpc.ForecastModelValidationServiceStub,
    request: forecasting_v1_forecast_model_validation_service_pb2.NormalizeForecastModelRequest,
    timeout: float
) -> forecasting_v1_forecast_model_validation_service_pb2.NormalizeForecastModelResponse:
    return await client.NormalizeForecastModel(request, timeout=timeout)


class DemandForecastValidationPreviewDemandForecast0Port(Protocol):
    async def execute(
        self,
        request: labeling_v1_labeling_task_query_service_pb2.FindLabelingTasksRequest
    ) -> labeling_v1_labeling_task_query_service_pb2.FindLabelingTasksResponse: ...


class DemandForecastValidationPreviewDemandForecast0Adapter:
    def __init__(
        self,
        client: labeling_v1_labeling_task_query_service_pb2_grpc.LabelingTaskQueryServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def execute(
        self,
        request: labeling_v1_labeling_task_query_service_pb2.FindLabelingTasksRequest
    ) -> labeling_v1_labeling_task_query_service_pb2.FindLabelingTasksResponse:
        return await self.client.FindLabelingTasks(request, timeout=self.timeout)


class DemandForecastValidationValidateDemandForecast0Adapter:
    def __init__(
        self,
        client: pipelines_v1_pipeline_run_validation_service_pb2_grpc.PipelineRunValidationServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def __call__(
        self,
        request: pipelines_v1_pipeline_run_validation_service_pb2.LintPipelineRunsRequest
    ) -> pipelines_v1_pipeline_run_validation_service_pb2.LintPipelineRunsResponse:
        return await self.client.LintPipelineRuns(request, timeout=self.timeout)


class DemandForecastWorkflowSignalDemandForecastWorkflow0Port(Protocol):
    async def execute(
        self,
        request: forecasting_v1_forecast_model_query_service_pb2.SummarizeForecastModelsRequest
    ) -> forecasting_v1_forecast_model_query_service_pb2.SummarizeForecastModelsResponse: ...


class DemandForecastWorkflowSignalDemandForecastWorkflow0Adapter:
    def __init__(
        self,
        client: forecasting_v1_forecast_model_query_service_pb2_grpc.ForecastModelQueryServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def execute(
        self,
        request: forecasting_v1_forecast_model_query_service_pb2.SummarizeForecastModelsRequest
    ) -> forecasting_v1_forecast_model_query_service_pb2.SummarizeForecastModelsResponse:
        return await self.client.SummarizeForecastModels(request, timeout=self.timeout)


class DemandForecastWorkflowStartDemandForecastWorkflow0Adapter:
    def __init__(
        self,
        client: forecasting_v1_demand_forecast_approval_service_pb2_grpc.DemandForecastApprovalServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def __call__(
        self,
        request: forecasting_v1_demand_forecast_approval_service_pb2.SubmitDemandForecastRequest
    ) -> forecasting_v1_demand_forecast_approval_service_pb2.SubmitDemandForecastResponse:
        return await self.client.SubmitDemandForecast(request, timeout=self.timeout)


async def forecast_model_approval_escalate_forecast_model2(
    client: ledger_v1_ledger_account_validation_service_pb2_grpc.LedgerAccountValidationServiceStub,
    request: ledger_v1_ledger_account_validation_service_pb2.ScoreLedgerAccountRequest,
    timeout: float
) -> ledger_v1_ledger_account_validation_service_pb2.ScoreLedgerAccountResponse:
    return await client.ScoreLedgerAccount(request, timeout=timeout)


class ForecastModelApprovalRejectForecastModel0Adapter:
    def __init__(
        self,
        client: documents_v1_document_validation_service_pb2_grpc.DocumentValidationServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def __call__(
        self,
        request: documents_v1_document_validation_service_pb2.CheckDocumentEligibilityRequest
    ) -> documents_v1_document_validation_service_pb2.CheckDocumentEligibilityResponse:
        return await self.client.CheckDocumentEligibility(request, timeout=self.timeout)


async def forecast_model_query_summarize_forecast_models0(
    client: forecasting_v1_forecast_model_validation_service_pb2_grpc.ForecastModelValidationServiceStub,
    request: forecasting_v1_forecast_model_validation_service_pb2.CheckForecastModelEligibilityRequest,
    timeout: float
) -> forecasting_v1_forecast_model_validation_service_pb2.CheckForecastModelEligibilityResponse:
    return await client.CheckForecastModelEligibility(request, timeout=timeout)


class ForecastModelValidationScoreForecastModel1Port(Protocol):
    async def execute(
        self,
        request: patients_v1_patient_query_service_pb2.SummarizePatientsRequest
    ) -> patients_v1_patient_query_service_pb2.SummarizePatientsResponse: ...


class ForecastModelValidationScoreForecastModel1Adapter:
    def __init__(
        self,
        client: patients_v1_patient_query_service_pb2_grpc.PatientQueryServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def execute(
        self,
        request: patients_v1_patient_query_service_pb2.SummarizePatientsRequest
    ) -> patients_v1_patient_query_service_pb2.SummarizePatientsResponse:
        return await self.client.SummarizePatients(request, timeout=self.timeout)


class ForecastModelValidationValidateForecastModel1Adapter:
    def __init__(
        self,
        client: forecasting_v1_demand_forecast_validation_service_pb2_grpc.DemandForecastValidationServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def __call__(
        self,
        request: forecasting_v1_demand_forecast_validation_service_pb2.NormalizeDemandForecastRequest
    ) -> forecasting_v1_demand_forecast_validation_service_pb2.NormalizeDemandForecastResponse:
        return await self.client.NormalizeDemandForecast(request, timeout=self.timeout)


async def scenario_approval_comment_scenario_approval2(
    client: labeling_v1_annotation_workflow_service_pb2_grpc.AnnotationWorkflowServiceStub,
    request: labeling_v1_annotation_workflow_service_pb2.SignalAnnotationWorkflowRequest,
    timeout: float
) -> labeling_v1_annotation_workflow_service_pb2.SignalAnnotationWorkflowResponse:
    return await client.SignalAnnotationWorkflow(request, timeout=timeout)


class ScenarioApprovalDelegateScenarioApproval1Port(Protocol):
    async def execute(
        self,
        request: featureflags_v1_feature_flag_service_pb2.ListFeatureFlagsRequest
    ) -> featureflags_v1_feature_flag_service_pb2.ListFeatureFlagsResponse: ...


class ScenarioApprovalDelegateScenarioApproval1Adapter:
    def __init__(
        self,
        client: featureflags_v1_feature_flag_service_pb2_grpc.FeatureFlagServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def execute(
        self,
        request: featureflags_v1_feature_flag_service_pb2.ListFeatureFlagsRequest
    ) -> featureflags_v1_feature_flag_service_pb2.ListFeatureFlagsResponse:
        return await self.client.ListFeatureFlags(request, timeout=self.timeout)


class ScenarioApprovalDelegateScenarioApproval3Adapter:
    def __init__(
        self,
        client: featurestore_v1_entity_approval_service_pb2_grpc.EntityApprovalServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def __call__(
        self,
        request: featurestore_v1_entity_approval_service_pb2.ListPendingEntitiesRequest
    ) -> featurestore_v1_entity_approval_service_pb2.ListPendingEntitiesResponse:
        return await self.client.ListPendingEntities(request, timeout=self.timeout)


async def scenario_calculation_estimate_scenario0(
    client: venues_v1_venue_query_service_pb2_grpc.VenueQueryServiceStub,
    request: venues_v1_venue_query_service_pb2.SummarizeVenuesRequest,
    timeout: float
) -> venues_v1_venue_query_service_pb2.SummarizeVenuesResponse:
    return await client.SummarizeVenues(request, timeout=timeout)


class ScenarioCalculationEstimateScenario2Port(Protocol):
    async def execute(
        self,
        request: forecasting_v1_demand_forecast_validation_service_pb2.NormalizeDemandForecastRequest
    ) -> forecasting_v1_demand_forecast_validation_service_pb2.NormalizeDemandForecastResponse: ...


class ScenarioCalculationEstimateScenario2Adapter:
    def __init__(
        self,
        client: forecasting_v1_demand_forecast_validation_service_pb2_grpc.DemandForecastValidationServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def execute(
        self,
        request: forecasting_v1_demand_forecast_validation_service_pb2.NormalizeDemandForecastRequest
    ) -> forecasting_v1_demand_forecast_validation_service_pb2.NormalizeDemandForecastResponse:
        return await self.client.NormalizeDemandForecast(request, timeout=self.timeout)


async def scenario_validation_normalize_scenario0(
    client: venues_v1_venue_validation_service_pb2_grpc.VenueValidationServiceStub,
    request: venues_v1_venue_validation_service_pb2.LintVenuesRequest,
    timeout: float
) -> venues_v1_venue_validation_service_pb2.LintVenuesResponse:
    return await client.LintVenues(request, timeout=timeout)


class ScenarioValidationNormalizeScenario2Port(Protocol):
    async def execute(
        self,
        request: metrics_v1_dashboard_validation_service_pb2.ValidateDashboardRequest
    ) -> metrics_v1_dashboard_validation_service_pb2.ValidateDashboardResponse: ...


class ScenarioValidationNormalizeScenario2Adapter:
    def __init__(
        self,
        client: metrics_v1_dashboard_validation_service_pb2_grpc.DashboardValidationServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def execute(
        self,
        request: metrics_v1_dashboard_validation_service_pb2.ValidateDashboardRequest
    ) -> metrics_v1_dashboard_validation_service_pb2.ValidateDashboardResponse:
        return await self.client.ValidateDashboard(request, timeout=self.timeout)


async def scenario_workflow_pause_scenario_workflow1(
    client: careplans_v1_care_plan_query_service_pb2_grpc.CarePlanQueryServiceStub,
    request: careplans_v1_care_plan_query_service_pb2.ResolveCarePlansRequest,
    timeout: float
) -> careplans_v1_care_plan_query_service_pb2.ResolveCarePlansResponse:
    return await client.ResolveCarePlans(request, timeout=timeout)


class ScenarioWorkflowResumeScenarioWorkflow1Port(Protocol):
    async def execute(
        self,
        request: authorization_v1_access_policy_validation_service_pb2.CheckAccessPolicyEligibilityRequest
    ) -> authorization_v1_access_policy_validation_service_pb2.CheckAccessPolicyEligibilityResponse: ...


class ScenarioWorkflowResumeScenarioWorkflow1Adapter:
    def __init__(
        self,
        client: authorization_v1_access_policy_validation_service_pb2_grpc.AccessPolicyValidationServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def execute(
        self,
        request: authorization_v1_access_policy_validation_service_pb2.CheckAccessPolicyEligibilityRequest
    ) -> authorization_v1_access_policy_validation_service_pb2.CheckAccessPolicyEligibilityResponse:
        return await self.client.CheckAccessPolicyEligibility(request, timeout=self.timeout)


class ScenarioWorkflowRetryScenarioWorkflow1Adapter:
    def __init__(
        self,
        client: forecasting_v1_forecast_model_validation_service_pb2_grpc.ForecastModelValidationServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def __call__(
        self,
        request: forecasting_v1_forecast_model_validation_service_pb2.CheckForecastModelEligibilityRequest
    ) -> forecasting_v1_forecast_model_validation_service_pb2.CheckForecastModelEligibilityResponse:
        return await self.client.CheckForecastModelEligibility(request, timeout=self.timeout)
