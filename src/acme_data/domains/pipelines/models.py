"""Typed commands crossing the pipelines application boundary."""

from __future__ import annotations

from dataclasses import dataclass

from google.protobuf import timestamp_pb2 as timestamp_pb2

from acme.anomalies.v1 import (
    anomaly_feedback_calculation_service_pb2 as anomalies_v1_anomaly_feedback_calculation_service_pb2,
)
from acme.appointments.v1 import appointment_service_pb2 as appointments_v1_appointment_service_pb2
from acme.careplans.v1 import care_plan_query_service_pb2 as careplans_v1_care_plan_query_service_pb2
from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.common.v1 import context_pb2 as common_v1_context_pb2
from acme.compliance.v1 import compliance_case_query_service_pb2 as compliance_v1_compliance_case_query_service_pb2
from acme.featurestore.v1 import entity_sync_service_pb2 as featurestore_v1_entity_sync_service_pb2
from acme.identity.v1 import identity_pb2 as identity_v1_identity_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.identity.v1 import user_service_pb2 as identity_v1_user_service_pb2
from acme.ledger.v1 import ledger_account_query_service_pb2 as ledger_v1_ledger_account_query_service_pb2
from acme.metrics.v1 import dashboard_sync_service_pb2 as metrics_v1_dashboard_sync_service_pb2
from acme.metrics.v1 import metric_alert_query_service_pb2 as metrics_v1_metric_alert_query_service_pb2
from acme.metrics.v1 import metrics_pb2 as metrics_v1_metrics_pb2
from acme.metrics.v1 import refs_pb2 as metrics_v1_refs_pb2
from acme.modelregistry.v1 import (
    model_version_lifecycle_service_pb2 as modelregistry_v1_model_version_lifecycle_service_pb2,
)
from acme.modelregistry.v1 import modelregistry_pb2 as modelregistry_v1_modelregistry_pb2
from acme.modelregistry.v1 import (
    registered_model_validation_service_pb2 as modelregistry_v1_registered_model_validation_service_pb2,
)
from acme.patients.v1 import patient_calculation_service_pb2 as patients_v1_patient_calculation_service_pb2
from acme.patients.v1 import patients_pb2 as patients_v1_patients_pb2
from acme.pipelines.v1 import pipeline_calculation_service_pb2 as pipelines_v1_pipeline_calculation_service_pb2
from acme.pipelines.v1 import pipeline_run_calculation_service_pb2 as pipelines_v1_pipeline_run_calculation_service_pb2
from acme.pipelines.v1 import pipeline_run_import_service_pb2 as pipelines_v1_pipeline_run_import_service_pb2
from acme.pipelines.v1 import pipeline_run_validation_service_pb2 as pipelines_v1_pipeline_run_validation_service_pb2
from acme.pipelines.v1 import pipeline_service_pb2 as pipelines_v1_pipeline_service_pb2
from acme.pipelines.v1 import pipeline_step_approval_service_pb2 as pipelines_v1_pipeline_step_approval_service_pb2
from acme.pipelines.v1 import pipeline_step_export_service_pb2 as pipelines_v1_pipeline_step_export_service_pb2
from acme.pipelines.v1 import pipeline_step_import_service_pb2 as pipelines_v1_pipeline_step_import_service_pb2
from acme.pipelines.v1 import pipeline_step_validation_service_pb2 as pipelines_v1_pipeline_step_validation_service_pb2
from acme.pipelines.v1 import pipeline_validation_service_pb2 as pipelines_v1_pipeline_validation_service_pb2
from acme.pipelines.v1 import pipelines_pb2 as pipelines_v1_pipelines_pb2
from acme.venues.v1 import venue_validation_service_pb2 as venues_v1_venue_validation_service_pb2
from acme.venues.v1 import venues_pb2 as venues_v1_venues_pb2

from acme_data.platform.models import ValidatedModel


@dataclass(frozen=True, slots=True)
class PipelineCalculationSimulatePipeline0Command:
    """Inputs required to preview venue."""
    context: common_v1_context_pb2.RequestContext
    venue_owner_email: str


def to_pipeline_calculation_simulate_pipeline0_command(
    command: PipelineCalculationSimulatePipeline0Command
) -> venues_v1_venue_validation_service_pb2.PreviewVenueRequest:
    return venues_v1_venue_validation_service_pb2.PreviewVenueRequest(
        context=command.context,
        venue=venues_v1_venues_pb2.Venue(owner=identity_v1_refs_pb2.UserRef(email=command.venue_owner_email))
    )


@dataclass(frozen=True, slots=True)
class PipelineCalculationSimulatePipeline1Command(ValidatedModel):
    """Inputs required to batch get appointments."""
    context: common_v1_context_pb2.RequestContext


def to_pipeline_calculation_simulate_pipeline1_command(
    command: PipelineCalculationSimulatePipeline1Command
) -> appointments_v1_appointment_service_pb2.BatchGetAppointmentsRequest:
    return appointments_v1_appointment_service_pb2.BatchGetAppointmentsRequest(context=command.context)


@dataclass(frozen=True, slots=True)
class PipelineLifecycleTerminatePipeline1Command:
    """Inputs required to sync dashboards."""
    context: common_v1_context_pb2.RequestContext
    dashboard_counterparty_display_name: str
    reason: str
    annotations: dict[str, str]


def to_pipeline_lifecycle_terminate_pipeline1_command(
    command: PipelineLifecycleTerminatePipeline1Command
) -> metrics_v1_dashboard_sync_service_pb2.SyncDashboardsRequest:
    return metrics_v1_dashboard_sync_service_pb2.SyncDashboardsRequest(
        annotations=command.annotations,
        context=command.context,
        dashboard=metrics_v1_metrics_pb2.Dashboard(
            counterparty=metrics_v1_refs_pb2.MetricAlertRef(display_name=command.dashboard_counterparty_display_name)
        ),
        reason=command.reason
    )


@dataclass(frozen=True, slots=True)
class PipelineLifecycleTerminatePipeline2Command(ValidatedModel):
    """Inputs required to check pipeline run eligibility."""
    context: common_v1_context_pb2.RequestContext
    pipeline_run_comments_created_at: timestamp_pb2.Timestamp
    details_contact_preferred_channel: str
    details_contact_email: str


def to_pipeline_lifecycle_terminate_pipeline2_command(
    command: PipelineLifecycleTerminatePipeline2Command
) -> pipelines_v1_pipeline_run_validation_service_pb2.CheckPipelineRunEligibilityRequest:
    return pipelines_v1_pipeline_run_validation_service_pb2.CheckPipelineRunEligibilityRequest(
        context=command.context,
        details=pipelines_v1_pipeline_run_validation_service_pb2.CheckPipelineRunEligibilityRequest.Details(
            contact=common_v1_contact_pb2.ContactInfo(
                email=command.details_contact_email,
                preferred_channel=command.details_contact_preferred_channel
            )
        ),
        pipeline_run=pipelines_v1_pipelines_pb2.PipelineRun(
            comments=[
                pipelines_v1_pipelines_pb2.PipelineRunComment(created_at=command.pipeline_run_comments_created_at)
            ]
        )
    )


@dataclass(frozen=True, slots=True)
class PipelineReportingDeletePipelineReport2Command(ValidatedModel):
    """Inputs required to count ledger accounts."""
    context: common_v1_context_pb2.RequestContext
    filter_region: str
    filter_created_after: timestamp_pb2.Timestamp


def to_pipeline_reporting_delete_pipeline_report2_command(
    command: PipelineReportingDeletePipelineReport2Command
) -> ledger_v1_ledger_account_query_service_pb2.CountLedgerAccountsRequest:
    return ledger_v1_ledger_account_query_service_pb2.CountLedgerAccountsRequest(
        context=command.context,
        filter=ledger_v1_ledger_account_query_service_pb2.CountLedgerAccountsRequest.Filter(
            created_after=command.filter_created_after,
            region=command.filter_region
        )
    )


@dataclass(frozen=True, slots=True)
class PipelineRunCalculationComparePipelineRunOptions0Command:
    """Inputs required to calculate pipeline."""
    context: common_v1_context_pb2.RequestContext
    pipeline_participants_contact_preferred_channel: str


def to_pipeline_run_calculation_compare_pipeline_run_options0_command(
    command: PipelineRunCalculationComparePipelineRunOptions0Command
) -> pipelines_v1_pipeline_calculation_service_pb2.CalculatePipelineRequest:
    return pipelines_v1_pipeline_calculation_service_pb2.CalculatePipelineRequest(
        context=command.context,
        pipeline=pipelines_v1_pipelines_pb2.Pipeline(
            participants=[
                pipelines_v1_pipelines_pb2.PipelineParticipant(
                    contact=common_v1_contact_pb2.ContactInfo(
                        preferred_channel=command.pipeline_participants_contact_preferred_channel
                    )
                )
            ]
        )
    )


@dataclass(frozen=True, slots=True)
class PipelineRunCalculationComparePipelineRunOptions1Command(ValidatedModel):
    """Inputs required to explain pipeline calculation."""
    context: common_v1_context_pb2.RequestContext
    pipeline_location_locality: str
    pipeline_organizer_user_id: str
    pipeline_participants_contact_phone: str
    details_contact_name: common_v1_contact_pb2.PersonName


def to_pipeline_run_calculation_compare_pipeline_run_options1_command(
    command: PipelineRunCalculationComparePipelineRunOptions1Command
) -> pipelines_v1_pipeline_calculation_service_pb2.ExplainPipelineCalculationRequest:
    return pipelines_v1_pipeline_calculation_service_pb2.ExplainPipelineCalculationRequest(
        context=command.context,
        details=pipelines_v1_pipeline_calculation_service_pb2.ExplainPipelineCalculationRequest.Details(
            contact=common_v1_contact_pb2.ContactInfo(name=command.details_contact_name)
        ),
        pipeline=pipelines_v1_pipelines_pb2.Pipeline(
            location=common_v1_address_pb2.PostalAddress(locality=command.pipeline_location_locality),
            organizer=identity_v1_refs_pb2.UserRef(user_id=command.pipeline_organizer_user_id),
            participants=[
                pipelines_v1_pipelines_pb2.PipelineParticipant(
                    contact=common_v1_contact_pb2.ContactInfo(phone=command.pipeline_participants_contact_phone)
                )
            ]
        )
    )


@dataclass(frozen=True, slots=True)
class PipelineRunLifecycleRenewPipelineRun1Command:
    """Inputs required to calculate patient."""
    context: common_v1_context_pb2.RequestContext
    patient_relationship_manager_user_id: str
    patient_contact_preferred_channel: str
    patient_relationship_manager_display_name: str
    patient_relationship_manager_email: str


def to_pipeline_run_lifecycle_renew_pipeline_run1_command(
    command: PipelineRunLifecycleRenewPipelineRun1Command
) -> patients_v1_patient_calculation_service_pb2.CalculatePatientRequest:
    return patients_v1_patient_calculation_service_pb2.CalculatePatientRequest(
        context=command.context,
        patient=patients_v1_patients_pb2.Patient(
            contact=common_v1_contact_pb2.ContactInfo(preferred_channel=command.patient_contact_preferred_channel),
            relationship_manager=identity_v1_refs_pb2.UserRef(
                display_name=command.patient_relationship_manager_display_name,
                email=command.patient_relationship_manager_email,
                user_id=command.patient_relationship_manager_user_id
            )
        )
    )


@dataclass(frozen=True, slots=True)
class PipelineRunLifecycleRenewPipelineRun2Command(ValidatedModel):
    """Inputs required to list pipeline step imports."""
    context: common_v1_context_pb2.RequestContext
    filter_region: str
    filter_created_after: timestamp_pb2.Timestamp
    filter_owner_id: str


def to_pipeline_run_lifecycle_renew_pipeline_run2_command(
    command: PipelineRunLifecycleRenewPipelineRun2Command
) -> pipelines_v1_pipeline_step_import_service_pb2.ListPipelineStepImportsRequest:
    return pipelines_v1_pipeline_step_import_service_pb2.ListPipelineStepImportsRequest(
        context=command.context,
        filter=pipelines_v1_pipeline_step_import_service_pb2.ListPipelineStepImportsRequest.Filter(
            created_after=command.filter_created_after,
            owner_id=command.filter_owner_id,
            region=command.filter_region
        )
    )


@dataclass(frozen=True, slots=True)
class PipelineRunReportingDeletePipelineRunReport0Command(ValidatedModel):
    """Inputs required to schedule model version expiry."""
    context: common_v1_context_pb2.RequestContext
    reason: str


def to_pipeline_run_reporting_delete_pipeline_run_report0_command(
    command: PipelineRunReportingDeletePipelineRunReport0Command
) -> modelregistry_v1_model_version_lifecycle_service_pb2.ScheduleModelVersionExpiryRequest:
    return modelregistry_v1_model_version_lifecycle_service_pb2.ScheduleModelVersionExpiryRequest(
        context=command.context,
        reason=command.reason
    )


@dataclass(frozen=True, slots=True)
class PipelineRunSyncResolvePipelineRunConflict0Command:
    """Inputs required to map pipeline step import columns."""
    context: common_v1_context_pb2.RequestContext
    details_contact_phone: str
    pipeline_step_owner_display_name: str
    details_contact_name: common_v1_contact_pb2.PersonName


def to_pipeline_run_sync_resolve_pipeline_run_conflict0_command(
    command: PipelineRunSyncResolvePipelineRunConflict0Command
) -> pipelines_v1_pipeline_step_import_service_pb2.MapPipelineStepImportColumnsRequest:
    return pipelines_v1_pipeline_step_import_service_pb2.MapPipelineStepImportColumnsRequest(
        context=command.context,
        details=pipelines_v1_pipeline_step_import_service_pb2.MapPipelineStepImportColumnsRequest.Details(
            contact=common_v1_contact_pb2.ContactInfo(
                name=command.details_contact_name,
                phone=command.details_contact_phone
            )
        ),
        pipeline_step=pipelines_v1_pipelines_pb2.PipelineStep(
            owner=identity_v1_refs_pb2.UserRef(display_name=command.pipeline_step_owner_display_name)
        )
    )


@dataclass(frozen=True, slots=True)
class PipelineRunSyncResolvePipelineRunConflict1Command(ValidatedModel):
    """Inputs required to list pipelines."""
    context: common_v1_context_pb2.RequestContext
    filter_created_after: timestamp_pb2.Timestamp


def to_pipeline_run_sync_resolve_pipeline_run_conflict1_command(
    command: PipelineRunSyncResolvePipelineRunConflict1Command
) -> pipelines_v1_pipeline_service_pb2.ListPipelinesRequest:
    return pipelines_v1_pipeline_service_pb2.ListPipelinesRequest(
        context=command.context,
        filter=pipelines_v1_pipeline_service_pb2.ListPipelinesRequest.Filter(created_after=command.filter_created_after)
    )


@dataclass(frozen=True, slots=True)
class PipelineRunValidationPreviewPipelineRun1Command(ValidatedModel):
    """Inputs required to count care plans."""
    context: common_v1_context_pb2.RequestContext
    filter_created_after: timestamp_pb2.Timestamp
    filter_owner_id: str


def to_pipeline_run_validation_preview_pipeline_run1_command(
    command: PipelineRunValidationPreviewPipelineRun1Command
) -> careplans_v1_care_plan_query_service_pb2.CountCarePlansRequest:
    return careplans_v1_care_plan_query_service_pb2.CountCarePlansRequest(
        context=command.context,
        filter=careplans_v1_care_plan_query_service_pb2.CountCarePlansRequest.Filter(
            created_after=command.filter_created_after,
            owner_id=command.filter_owner_id
        )
    )


@dataclass(frozen=True, slots=True)
class PipelineRunWorkflowSignalPipelineRunWorkflow0Command:
    """Inputs required to normalize pipeline."""
    context: common_v1_context_pb2.RequestContext
    pipeline_participants_contact_name: common_v1_contact_pb2.PersonName
    pipeline_participants_contact_email: str
    pipeline_organizer_user_id: str


def to_pipeline_run_workflow_signal_pipeline_run_workflow0_command(
    command: PipelineRunWorkflowSignalPipelineRunWorkflow0Command
) -> pipelines_v1_pipeline_validation_service_pb2.NormalizePipelineRequest:
    return pipelines_v1_pipeline_validation_service_pb2.NormalizePipelineRequest(
        context=command.context,
        pipeline=pipelines_v1_pipelines_pb2.Pipeline(
            organizer=identity_v1_refs_pb2.UserRef(user_id=command.pipeline_organizer_user_id),
            participants=[
                pipelines_v1_pipelines_pb2.PipelineParticipant(
                    contact=common_v1_contact_pb2.ContactInfo(
                        email=command.pipeline_participants_contact_email,
                        name=command.pipeline_participants_contact_name
                    )
                )
            ]
        )
    )


@dataclass(frozen=True, slots=True)
class PipelineRunWorkflowSignalPipelineRunWorkflow1Command(ValidatedModel):
    """Inputs required to reject pipeline step."""
    context: common_v1_context_pb2.RequestContext
    pipeline_step_owner_display_name: str
    pipeline_step_owner_user_id: str
    pipeline_step_owner_email: str


def to_pipeline_run_workflow_signal_pipeline_run_workflow1_command(
    command: PipelineRunWorkflowSignalPipelineRunWorkflow1Command
) -> pipelines_v1_pipeline_step_approval_service_pb2.RejectPipelineStepRequest:
    return pipelines_v1_pipeline_step_approval_service_pb2.RejectPipelineStepRequest(
        context=command.context,
        pipeline_step=pipelines_v1_pipelines_pb2.PipelineStep(
            owner=identity_v1_refs_pb2.UserRef(
                display_name=command.pipeline_step_owner_display_name,
                email=command.pipeline_step_owner_email,
                user_id=command.pipeline_step_owner_user_id
            )
        )
    )


@dataclass(frozen=True, slots=True)
class PipelineStepApprovalEscalatePipelineStep2Command:
    """Inputs required to retry pipeline run import."""
    context: common_v1_context_pb2.RequestContext
    pipeline_run_sla_breached: bool


def to_pipeline_step_approval_escalate_pipeline_step2_command(
    command: PipelineStepApprovalEscalatePipelineStep2Command
) -> pipelines_v1_pipeline_run_import_service_pb2.RetryPipelineRunImportRequest:
    return pipelines_v1_pipeline_run_import_service_pb2.RetryPipelineRunImportRequest(
        context=command.context,
        pipeline_run=pipelines_v1_pipelines_pb2.PipelineRun(
            sla=pipelines_v1_pipelines_pb2.PipelineRunSla(breached=command.pipeline_run_sla_breached)
        )
    )


@dataclass(frozen=True, slots=True)
class PipelineStepApprovalEscalatePipelineStep3Command(ValidatedModel):
    """Inputs required to list entity conflicts."""
    context: common_v1_context_pb2.RequestContext
    filter_created_after: timestamp_pb2.Timestamp
    filter_owner_id: str
    filter_labels: dict[str, str]


def to_pipeline_step_approval_escalate_pipeline_step3_command(
    command: PipelineStepApprovalEscalatePipelineStep3Command
) -> featurestore_v1_entity_sync_service_pb2.ListEntityConflictsRequest:
    return featurestore_v1_entity_sync_service_pb2.ListEntityConflictsRequest(
        context=command.context,
        filter=featurestore_v1_entity_sync_service_pb2.ListEntityConflictsRequest.Filter(
            created_after=command.filter_created_after,
            labels=command.filter_labels,
            owner_id=command.filter_owner_id
        )
    )


@dataclass(frozen=True, slots=True)
class PipelineStepCalculationQuotePipelineStep0Command:
    """Inputs required to score registered model."""
    context: common_v1_context_pb2.RequestContext
    registered_model_address_region: str
    registered_model_audit_updated_at: timestamp_pb2.Timestamp
    registered_model_owner_email: str


def to_pipeline_step_calculation_quote_pipeline_step0_command(
    command: PipelineStepCalculationQuotePipelineStep0Command
) -> modelregistry_v1_registered_model_validation_service_pb2.ScoreRegisteredModelRequest:
    return modelregistry_v1_registered_model_validation_service_pb2.ScoreRegisteredModelRequest(
        context=command.context,
        registered_model=modelregistry_v1_modelregistry_pb2.RegisteredModel(
            address=common_v1_address_pb2.PostalAddress(region=command.registered_model_address_region),
            audit=common_v1_audit_pb2.AuditInfo(updated_at=command.registered_model_audit_updated_at),
            owner=identity_v1_refs_pb2.UserRef(email=command.registered_model_owner_email)
        )
    )


@dataclass(frozen=True, slots=True)
class PipelineStepCalculationQuotePipelineStep1Command(ValidatedModel):
    """Inputs required to recalculate anomaly feedbacks."""
    context: common_v1_context_pb2.RequestContext
    details_destination_postal_code: str


def to_pipeline_step_calculation_quote_pipeline_step1_command(
    command: PipelineStepCalculationQuotePipelineStep1Command
) -> anomalies_v1_anomaly_feedback_calculation_service_pb2.RecalculateAnomalyFeedbacksRequest:
    return anomalies_v1_anomaly_feedback_calculation_service_pb2.RecalculateAnomalyFeedbacksRequest(
        context=command.context,
        details=anomalies_v1_anomaly_feedback_calculation_service_pb2.RecalculateAnomalyFeedbacksRequest.Details(
            destination=common_v1_address_pb2.PostalAddress(postal_code=command.details_destination_postal_code)
        )
    )


@dataclass(frozen=True, slots=True)
class PipelineStepExportSchedulePipelineStepExport1Command:
    """Inputs required to clone user."""
    context: common_v1_context_pb2.RequestContext
    user_relationship_manager_user_id: str
    user_relationship_manager_email: str
    user_preferences_quiet_hours: common_v1_audit_pb2.TimeWindow


def to_pipeline_step_export_schedule_pipeline_step_export1_command(
    command: PipelineStepExportSchedulePipelineStepExport1Command
) -> identity_v1_user_service_pb2.CloneUserRequest:
    return identity_v1_user_service_pb2.CloneUserRequest(
        context=command.context,
        user=identity_v1_identity_pb2.User(
            preferences=identity_v1_identity_pb2.UserPreferences(quiet_hours=command.user_preferences_quiet_hours),
            relationship_manager=identity_v1_refs_pb2.UserRef(
                email=command.user_relationship_manager_email,
                user_id=command.user_relationship_manager_user_id
            )
        )
    )


@dataclass(frozen=True, slots=True)
class PipelineStepExportSchedulePipelineStepExport2Command(ValidatedModel):
    """Inputs required to recalculate pipelines."""
    context: common_v1_context_pb2.RequestContext
    pipeline_participants_contact_name: common_v1_contact_pb2.PersonName
    details_destination_country_code: str
    details_destination_recipient: str
    pipeline_participants_contact_phone: str


def to_pipeline_step_export_schedule_pipeline_step_export2_command(
    command: PipelineStepExportSchedulePipelineStepExport2Command
) -> pipelines_v1_pipeline_calculation_service_pb2.RecalculatePipelinesRequest:
    return pipelines_v1_pipeline_calculation_service_pb2.RecalculatePipelinesRequest(
        context=command.context,
        details=pipelines_v1_pipeline_calculation_service_pb2.RecalculatePipelinesRequest.Details(
            destination=common_v1_address_pb2.PostalAddress(
                country_code=command.details_destination_country_code,
                recipient=command.details_destination_recipient
            )
        ),
        pipeline=pipelines_v1_pipelines_pb2.Pipeline(
            participants=[
                pipelines_v1_pipelines_pb2.PipelineParticipant(
                    contact=common_v1_contact_pb2.ContactInfo(
                        name=command.pipeline_participants_contact_name,
                        phone=command.pipeline_participants_contact_phone
                    )
                )
            ]
        )
    )


@dataclass(frozen=True, slots=True)
class PipelineStepImportMapPipelineStepImportColumns0Command:
    """Inputs required to schedule pipeline step export."""
    context: common_v1_context_pb2.RequestContext
    pipeline_step_id: str
    reason: str
    annotations: dict[str, str]


def to_pipeline_step_import_map_pipeline_step_import_columns0_command(
    command: PipelineStepImportMapPipelineStepImportColumns0Command
) -> pipelines_v1_pipeline_step_export_service_pb2.SchedulePipelineStepExportRequest:
    return pipelines_v1_pipeline_step_export_service_pb2.SchedulePipelineStepExportRequest(
        annotations=command.annotations,
        context=command.context,
        pipeline_step_id=command.pipeline_step_id,
        reason=command.reason
    )


@dataclass(frozen=True, slots=True)
class PipelineStepImportMapPipelineStepImportColumns1Command(ValidatedModel):
    """Inputs required to check pipeline run eligibility."""
    context: common_v1_context_pb2.RequestContext
    pipeline_run_requester_phone: str
    details_contact_email: str
    pipeline_run_requester_name: common_v1_contact_pb2.PersonName


def to_pipeline_step_import_map_pipeline_step_import_columns1_command(
    command: PipelineStepImportMapPipelineStepImportColumns1Command
) -> pipelines_v1_pipeline_run_validation_service_pb2.CheckPipelineRunEligibilityRequest:
    return pipelines_v1_pipeline_run_validation_service_pb2.CheckPipelineRunEligibilityRequest(
        context=command.context,
        details=pipelines_v1_pipeline_run_validation_service_pb2.CheckPipelineRunEligibilityRequest.Details(
            contact=common_v1_contact_pb2.ContactInfo(email=command.details_contact_email)
        ),
        pipeline_run=pipelines_v1_pipelines_pb2.PipelineRun(
            requester=common_v1_contact_pb2.ContactInfo(
                name=command.pipeline_run_requester_name,
                phone=command.pipeline_run_requester_phone
            )
        )
    )


@dataclass(frozen=True, slots=True)
class PipelineStepLifecycleSchedulePipelineStepExpiry0Command(ValidatedModel):
    """Inputs required to find compliance cases."""
    context: common_v1_context_pb2.RequestContext
    filter_created_after: timestamp_pb2.Timestamp


def to_pipeline_step_lifecycle_schedule_pipeline_step_expiry0_command(
    command: PipelineStepLifecycleSchedulePipelineStepExpiry0Command
) -> compliance_v1_compliance_case_query_service_pb2.FindComplianceCasesRequest:
    return compliance_v1_compliance_case_query_service_pb2.FindComplianceCasesRequest(
        context=command.context,
        filter=compliance_v1_compliance_case_query_service_pb2.FindComplianceCasesRequest.Filter(
            created_after=command.filter_created_after
        )
    )


@dataclass(frozen=True, slots=True)
class PipelineStepReportingGeneratePipelineStepReport0Command(ValidatedModel):
    """Inputs required to count metric alerts."""
    context: common_v1_context_pb2.RequestContext
    filter_labels: dict[str, str]
    filter_owner_id: str
    filter_created_after: timestamp_pb2.Timestamp


def to_pipeline_step_reporting_generate_pipeline_step_report0_command(
    command: PipelineStepReportingGeneratePipelineStepReport0Command
) -> metrics_v1_metric_alert_query_service_pb2.CountMetricAlertsRequest:
    return metrics_v1_metric_alert_query_service_pb2.CountMetricAlertsRequest(
        context=command.context,
        filter=metrics_v1_metric_alert_query_service_pb2.CountMetricAlertsRequest.Filter(
            created_after=command.filter_created_after,
            labels=command.filter_labels,
            owner_id=command.filter_owner_id
        )
    )


@dataclass(frozen=True, slots=True)
class PipelineSyncPullPipelines3Command(ValidatedModel):
    """Inputs required to score pipeline step."""
    context: common_v1_context_pb2.RequestContext
    pipeline_step_audit_updated_at: timestamp_pb2.Timestamp
    details_destination_recipient: str
    pipeline_step_owner_user_id: str


def to_pipeline_sync_pull_pipelines3_command(
    command: PipelineSyncPullPipelines3Command
) -> pipelines_v1_pipeline_step_validation_service_pb2.ScorePipelineStepRequest:
    return pipelines_v1_pipeline_step_validation_service_pb2.ScorePipelineStepRequest(
        context=command.context,
        details=pipelines_v1_pipeline_step_validation_service_pb2.ScorePipelineStepRequest.Details(
            destination=common_v1_address_pb2.PostalAddress(recipient=command.details_destination_recipient)
        ),
        pipeline_step=pipelines_v1_pipelines_pb2.PipelineStep(
            audit=common_v1_audit_pb2.AuditInfo(updated_at=command.pipeline_step_audit_updated_at),
            owner=identity_v1_refs_pb2.UserRef(user_id=command.pipeline_step_owner_user_id)
        )
    )


@dataclass(frozen=True, slots=True)
class PipelineValidationNormalizePipeline0Command:
    """Inputs required to estimate pipeline run."""
    context: common_v1_context_pb2.RequestContext
    pipeline_run_assignee_email: str


def to_pipeline_validation_normalize_pipeline0_command(
    command: PipelineValidationNormalizePipeline0Command
) -> pipelines_v1_pipeline_run_calculation_service_pb2.EstimatePipelineRunRequest:
    return pipelines_v1_pipeline_run_calculation_service_pb2.EstimatePipelineRunRequest(
        context=command.context,
        pipeline_run=pipelines_v1_pipelines_pb2.PipelineRun(
            assignee=identity_v1_refs_pb2.UserRef(email=command.pipeline_run_assignee_email)
        )
    )
