"""Typed commands crossing the forecasting application boundary."""

from __future__ import annotations

from dataclasses import dataclass

from google.protobuf import timestamp_pb2 as timestamp_pb2

from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.common.v1 import context_pb2 as common_v1_context_pb2
from acme.customers.v1 import refs_pb2 as customers_v1_refs_pb2
from acme.datasets.v1 import (
    dataset_version_validation_service_pb2 as datasets_v1_dataset_version_validation_service_pb2,
)
from acme.datasets.v1 import datasets_pb2 as datasets_v1_datasets_pb2
from acme.forecasting.v1 import (
    demand_forecast_approval_service_pb2 as forecasting_v1_demand_forecast_approval_service_pb2,
)
from acme.forecasting.v1 import demand_forecast_service_pb2 as forecasting_v1_demand_forecast_service_pb2
from acme.forecasting.v1 import (
    demand_forecast_validation_service_pb2 as forecasting_v1_demand_forecast_validation_service_pb2,
)
from acme.forecasting.v1 import (
    forecast_model_validation_service_pb2 as forecasting_v1_forecast_model_validation_service_pb2,
)
from acme.forecasting.v1 import forecasting_pb2 as forecasting_v1_forecasting_pb2
from acme.forecasting.v1 import refs_pb2 as forecasting_v1_refs_pb2
from acme.forecasting.v1 import scenario_calculation_service_pb2 as forecasting_v1_scenario_calculation_service_pb2
from acme.identity.v1 import identity_pb2 as identity_v1_identity_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.identity.v1 import user_validation_service_pb2 as identity_v1_user_validation_service_pb2
from acme.ledger.v1 import ledger_account_validation_service_pb2 as ledger_v1_ledger_account_validation_service_pb2
from acme.ledger.v1 import ledger_pb2 as ledger_v1_ledger_pb2
from acme.metrics.v1 import metric_series_export_service_pb2 as metrics_v1_metric_series_export_service_pb2
from acme.modelregistry.v1 import deployment_sync_service_pb2 as modelregistry_v1_deployment_sync_service_pb2
from acme.modelregistry.v1 import modelregistry_pb2 as modelregistry_v1_modelregistry_pb2
from acme.pipelines.v1 import pipeline_run_validation_service_pb2 as pipelines_v1_pipeline_run_validation_service_pb2
from acme.pipelines.v1 import pipelines_pb2 as pipelines_v1_pipelines_pb2
from acme.shows.v1 import show_calculation_service_pb2 as shows_v1_show_calculation_service_pb2
from acme.shows.v1 import shows_pb2 as shows_v1_shows_pb2

from acme_data.platform.models import ValidatedModel


@dataclass(frozen=True, slots=True)
class DemandForecastApprovalSubmitDemandForecast1Command:
    """Inputs required to estimate scenario."""
    context: common_v1_context_pb2.RequestContext
    details_destination_postal_code: str
    scenario_audit_updated_at: timestamp_pb2.Timestamp


def to_demand_forecast_approval_submit_demand_forecast1_command(
    command: DemandForecastApprovalSubmitDemandForecast1Command
) -> forecasting_v1_scenario_calculation_service_pb2.EstimateScenarioRequest:
    return forecasting_v1_scenario_calculation_service_pb2.EstimateScenarioRequest(
        context=command.context,
        details=forecasting_v1_scenario_calculation_service_pb2.EstimateScenarioRequest.Details(
            destination=common_v1_address_pb2.PostalAddress(postal_code=command.details_destination_postal_code)
        ),
        scenario=forecasting_v1_forecasting_pb2.Scenario(
            audit=common_v1_audit_pb2.AuditInfo(updated_at=command.scenario_audit_updated_at)
        )
    )


@dataclass(frozen=True, slots=True)
class DemandForecastApprovalSubmitDemandForecast2Command(ValidatedModel):
    """Inputs required to check forecast model eligibility."""
    context: common_v1_context_pb2.RequestContext
    details_contact_phone: str
    forecast_model_audit_created_by: str
    forecast_model_address_postal_code: str
    forecast_model_audit_updated_at: timestamp_pb2.Timestamp


def to_demand_forecast_approval_submit_demand_forecast2_command(
    command: DemandForecastApprovalSubmitDemandForecast2Command
) -> forecasting_v1_forecast_model_validation_service_pb2.CheckForecastModelEligibilityRequest:
    return forecasting_v1_forecast_model_validation_service_pb2.CheckForecastModelEligibilityRequest(
        context=command.context,
        details=forecasting_v1_forecast_model_validation_service_pb2.CheckForecastModelEligibilityRequest.Details(
            contact=common_v1_contact_pb2.ContactInfo(phone=command.details_contact_phone)
        ),
        forecast_model=forecasting_v1_forecasting_pb2.ForecastModel(
            address=common_v1_address_pb2.PostalAddress(postal_code=command.forecast_model_address_postal_code),
            audit=common_v1_audit_pb2.AuditInfo(
                created_by=command.forecast_model_audit_created_by,
                updated_at=command.forecast_model_audit_updated_at
            )
        )
    )


@dataclass(frozen=True, slots=True)
class DemandForecastCloneDemandForecast1Command(ValidatedModel):
    """Inputs required to simulate show."""
    context: common_v1_context_pb2.RequestContext
    show_location_locality: str
    show_organizer_display_name: str
    show_location_postal_code: str


def to_demand_forecast_clone_demand_forecast1_command(
    command: DemandForecastCloneDemandForecast1Command
) -> shows_v1_show_calculation_service_pb2.SimulateShowRequest:
    return shows_v1_show_calculation_service_pb2.SimulateShowRequest(
        context=command.context,
        show=shows_v1_shows_pb2.Show(
            location=common_v1_address_pb2.PostalAddress(
                locality=command.show_location_locality,
                postal_code=command.show_location_postal_code
            ),
            organizer=identity_v1_refs_pb2.UserRef(display_name=command.show_organizer_display_name)
        )
    )


@dataclass(frozen=True, slots=True)
class DemandForecastValidationLintDemandForecasts0Command:
    """Inputs required to validate pipeline run."""
    context: common_v1_context_pb2.RequestContext
    details_contact_name: common_v1_contact_pb2.PersonName
    pipeline_run_audit_updated_by: str


def to_demand_forecast_validation_lint_demand_forecasts0_command(
    command: DemandForecastValidationLintDemandForecasts0Command
) -> pipelines_v1_pipeline_run_validation_service_pb2.ValidatePipelineRunRequest:
    return pipelines_v1_pipeline_run_validation_service_pb2.ValidatePipelineRunRequest(
        context=command.context,
        details=pipelines_v1_pipeline_run_validation_service_pb2.ValidatePipelineRunRequest.Details(
            contact=common_v1_contact_pb2.ContactInfo(name=command.details_contact_name)
        ),
        pipeline_run=pipelines_v1_pipelines_pb2.PipelineRun(
            audit=common_v1_audit_pb2.AuditInfo(updated_by=command.pipeline_run_audit_updated_by)
        )
    )


@dataclass(frozen=True, slots=True)
class DemandForecastWorkflowResumeDemandForecastWorkflow0Command(ValidatedModel):
    """Inputs required to clone demand forecast."""
    context: common_v1_context_pb2.RequestContext
    demand_forecast_billing_address_country_code: str
    demand_forecast_billing_address_lines: list[str]
    demand_forecast_billing_address_postal_code: str


def to_demand_forecast_workflow_resume_demand_forecast_workflow0_command(
    command: DemandForecastWorkflowResumeDemandForecastWorkflow0Command
) -> forecasting_v1_demand_forecast_service_pb2.CloneDemandForecastRequest:
    return forecasting_v1_demand_forecast_service_pb2.CloneDemandForecastRequest(
        context=command.context,
        demand_forecast=forecasting_v1_forecasting_pb2.DemandForecast(
            billing_address=common_v1_address_pb2.PostalAddress(
                country_code=command.demand_forecast_billing_address_country_code,
                lines=command.demand_forecast_billing_address_lines,
                postal_code=command.demand_forecast_billing_address_postal_code
            )
        )
    )


@dataclass(frozen=True, slots=True)
class ForecastModelApprovalDelegateForecastModelApproval1Command:
    """Inputs required to pull deployments."""
    context: common_v1_context_pb2.RequestContext
    deployment_organizer_email: str
    deployment_weekly_interval: int
    deployment_participants_contact_email: str
    deployment_location_lines: list[str]


def to_forecast_model_approval_delegate_forecast_model_approval1_command(
    command: ForecastModelApprovalDelegateForecastModelApproval1Command
) -> modelregistry_v1_deployment_sync_service_pb2.PullDeploymentsRequest:
    return modelregistry_v1_deployment_sync_service_pb2.PullDeploymentsRequest(
        context=command.context,
        deployment=modelregistry_v1_modelregistry_pb2.Deployment(
            location=common_v1_address_pb2.PostalAddress(lines=command.deployment_location_lines),
            organizer=identity_v1_refs_pb2.UserRef(email=command.deployment_organizer_email),
            participants=[
                modelregistry_v1_modelregistry_pb2.DeploymentParticipant(
                    contact=common_v1_contact_pb2.ContactInfo(email=command.deployment_participants_contact_email)
                )
            ],
            weekly=modelregistry_v1_modelregistry_pb2.DeploymentWeeklyRule(interval=command.deployment_weekly_interval)
        )
    )


@dataclass(frozen=True, slots=True)
class ForecastModelApprovalEscalateForecastModel0Command(ValidatedModel):
    """Inputs required to normalize ledger account."""
    context: common_v1_context_pb2.RequestContext
    ledger_account_contact_email: str
    ledger_account_audit_updated_by: str
    ledger_account_audit_created_by: str
    ledger_account_audit_created_at: timestamp_pb2.Timestamp


def to_forecast_model_approval_escalate_forecast_model0_command(
    command: ForecastModelApprovalEscalateForecastModel0Command
) -> ledger_v1_ledger_account_validation_service_pb2.NormalizeLedgerAccountRequest:
    return ledger_v1_ledger_account_validation_service_pb2.NormalizeLedgerAccountRequest(
        context=command.context,
        ledger_account=ledger_v1_ledger_pb2.LedgerAccount(
            audit=common_v1_audit_pb2.AuditInfo(
                created_at=command.ledger_account_audit_created_at,
                created_by=command.ledger_account_audit_created_by,
                updated_by=command.ledger_account_audit_updated_by
            ),
            contact=common_v1_contact_pb2.ContactInfo(email=command.ledger_account_contact_email)
        )
    )


@dataclass(frozen=True, slots=True)
class ForecastModelValidationPreviewForecastModel1Command(ValidatedModel):
    """Inputs required to schedule metric series export."""
    context: common_v1_context_pb2.RequestContext
    reason: str


def to_forecast_model_validation_preview_forecast_model1_command(
    command: ForecastModelValidationPreviewForecastModel1Command
) -> metrics_v1_metric_series_export_service_pb2.ScheduleMetricSeriesExportRequest:
    return metrics_v1_metric_series_export_service_pb2.ScheduleMetricSeriesExportRequest(
        context=command.context,
        reason=command.reason
    )


@dataclass(frozen=True, slots=True)
class ScenarioApprovalApproveScenario1Command:
    """Inputs required to list demand forecasts."""
    context: common_v1_context_pb2.RequestContext
    filter_region: str
    filter_created_after: timestamp_pb2.Timestamp
    filter_owner_id: str


def to_scenario_approval_approve_scenario1_command(
    command: ScenarioApprovalApproveScenario1Command
) -> forecasting_v1_demand_forecast_service_pb2.ListDemandForecastsRequest:
    return forecasting_v1_demand_forecast_service_pb2.ListDemandForecastsRequest(
        context=command.context,
        filter=forecasting_v1_demand_forecast_service_pb2.ListDemandForecastsRequest.Filter(
            created_after=command.filter_created_after,
            owner_id=command.filter_owner_id,
            region=command.filter_region
        )
    )


@dataclass(frozen=True, slots=True)
class ScenarioApprovalCommentScenarioApproval0Command(ValidatedModel):
    """Inputs required to approve demand forecast."""
    context: common_v1_context_pb2.RequestContext
    details_approver_email: str
    demand_forecast_audit_created_by: str
    details_approver_display_name: str


def to_scenario_approval_comment_scenario_approval0_command(
    command: ScenarioApprovalCommentScenarioApproval0Command
) -> forecasting_v1_demand_forecast_approval_service_pb2.ApproveDemandForecastRequest:
    return forecasting_v1_demand_forecast_approval_service_pb2.ApproveDemandForecastRequest(
        context=command.context,
        demand_forecast=forecasting_v1_forecasting_pb2.DemandForecast(
            audit=common_v1_audit_pb2.AuditInfo(created_by=command.demand_forecast_audit_created_by)
        ),
        details=forecasting_v1_demand_forecast_approval_service_pb2.ApproveDemandForecastRequest.Details(
            approver=identity_v1_refs_pb2.UserRef(
                display_name=command.details_approver_display_name,
                email=command.details_approver_email
            )
        )
    )


@dataclass(frozen=True, slots=True)
class ScenarioCalculationCalculateScenario0Command:
    """Inputs required to score user."""
    context: common_v1_context_pb2.RequestContext
    user_relationship_manager_user_id: str
    user_audit_updated_by: str
    details_destination_recipient: str
    user_primary_address_locality: str


def to_scenario_calculation_calculate_scenario0_command(
    command: ScenarioCalculationCalculateScenario0Command
) -> identity_v1_user_validation_service_pb2.ScoreUserRequest:
    return identity_v1_user_validation_service_pb2.ScoreUserRequest(
        context=command.context,
        details=identity_v1_user_validation_service_pb2.ScoreUserRequest.Details(
            destination=common_v1_address_pb2.PostalAddress(recipient=command.details_destination_recipient)
        ),
        user=identity_v1_identity_pb2.User(
            audit=common_v1_audit_pb2.AuditInfo(updated_by=command.user_audit_updated_by),
            primary_address=common_v1_address_pb2.PostalAddress(locality=command.user_primary_address_locality),
            relationship_manager=identity_v1_refs_pb2.UserRef(user_id=command.user_relationship_manager_user_id)
        )
    )


@dataclass(frozen=True, slots=True)
class ScenarioCalculationCalculateScenario1Command(ValidatedModel):
    """Inputs required to score dataset version."""
    context: common_v1_context_pb2.RequestContext
    details_destination_locality: str
    details_destination_lines: list[str]
    dataset_version_subject_email: str
    details_destination_region: str


def to_scenario_calculation_calculate_scenario1_command(
    command: ScenarioCalculationCalculateScenario1Command
) -> datasets_v1_dataset_version_validation_service_pb2.ScoreDatasetVersionRequest:
    return datasets_v1_dataset_version_validation_service_pb2.ScoreDatasetVersionRequest(
        context=command.context,
        dataset_version=datasets_v1_datasets_pb2.DatasetVersion(
            subject=customers_v1_refs_pb2.CustomerRef(email=command.dataset_version_subject_email)
        ),
        details=datasets_v1_dataset_version_validation_service_pb2.ScoreDatasetVersionRequest.Details(
            destination=common_v1_address_pb2.PostalAddress(
                lines=command.details_destination_lines,
                locality=command.details_destination_locality,
                region=command.details_destination_region
            )
        )
    )


@dataclass(frozen=True, slots=True)
class ScenarioValidationExplainScenarioDecision1Command:
    """Inputs required to preview demand forecast."""
    context: common_v1_context_pb2.RequestContext
    details_contact_email: str
    demand_forecast_counterparty_display_name: str
    demand_forecast_lines_quantity: int


def to_scenario_validation_explain_scenario_decision1_command(
    command: ScenarioValidationExplainScenarioDecision1Command
) -> forecasting_v1_demand_forecast_validation_service_pb2.PreviewDemandForecastRequest:
    return forecasting_v1_demand_forecast_validation_service_pb2.PreviewDemandForecastRequest(
        context=command.context,
        demand_forecast=forecasting_v1_forecasting_pb2.DemandForecast(
            counterparty=forecasting_v1_refs_pb2.ScenarioRef(
                display_name=command.demand_forecast_counterparty_display_name
            ),
            lines=[forecasting_v1_forecasting_pb2.DemandForecastLine(quantity=command.demand_forecast_lines_quantity)]
        ),
        details=forecasting_v1_demand_forecast_validation_service_pb2.PreviewDemandForecastRequest.Details(
            contact=common_v1_contact_pb2.ContactInfo(email=command.details_contact_email)
        )
    )


@dataclass(frozen=True, slots=True)
class ScenarioWorkflowAdvanceScenarioWorkflow2Command:
    """Inputs required to list pending demand forecasts."""
    context: common_v1_context_pb2.RequestContext
    filter_region: str
    filter_created_after: timestamp_pb2.Timestamp


def to_scenario_workflow_advance_scenario_workflow2_command(
    command: ScenarioWorkflowAdvanceScenarioWorkflow2Command
) -> forecasting_v1_demand_forecast_approval_service_pb2.ListPendingDemandForecastsRequest:
    return forecasting_v1_demand_forecast_approval_service_pb2.ListPendingDemandForecastsRequest(
        context=command.context,
        filter=forecasting_v1_demand_forecast_approval_service_pb2.ListPendingDemandForecastsRequest.Filter(
            created_after=command.filter_created_after,
            region=command.filter_region
        )
    )
