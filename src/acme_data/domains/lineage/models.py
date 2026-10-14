"""Typed commands crossing the lineage application boundary."""

from __future__ import annotations

from dataclasses import dataclass

from google.protobuf import timestamp_pb2 as timestamp_pb2

from acme.anomalies.v1 import (
    anomaly_feedback_validation_service_pb2 as anomalies_v1_anomaly_feedback_validation_service_pb2,
)
from acme.authorization.v1 import access_policy_query_service_pb2 as authorization_v1_access_policy_query_service_pb2
from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.common.v1 import context_pb2 as common_v1_context_pb2
from acme.customers.v1 import (
    consent_record_validation_service_pb2 as customers_v1_consent_record_validation_service_pb2,
)
from acme.customers.v1 import customers_pb2 as customers_v1_customers_pb2
from acme.customers.v1 import preference_validation_service_pb2 as customers_v1_preference_validation_service_pb2
from acme.customers.v1 import refs_pb2 as customers_v1_refs_pb2
from acme.documents.v1 import document_query_service_pb2 as documents_v1_document_query_service_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.ledger.v1 import ledger_account_validation_service_pb2 as ledger_v1_ledger_account_validation_service_pb2
from acme.ledger.v1 import ledger_pb2 as ledger_v1_ledger_pb2
from acme.lineage.v1 import impact_calculation_service_pb2 as lineage_v1_impact_calculation_service_pb2
from acme.lineage.v1 import lineage_edge_calculation_service_pb2 as lineage_v1_lineage_edge_calculation_service_pb2
from acme.lineage.v1 import lineage_edge_query_service_pb2 as lineage_v1_lineage_edge_query_service_pb2
from acme.lineage.v1 import lineage_edge_sync_service_pb2 as lineage_v1_lineage_edge_sync_service_pb2
from acme.lineage.v1 import lineage_edge_workflow_service_pb2 as lineage_v1_lineage_edge_workflow_service_pb2
from acme.lineage.v1 import lineage_node_calculation_service_pb2 as lineage_v1_lineage_node_calculation_service_pb2
from acme.lineage.v1 import lineage_node_reporting_service_pb2 as lineage_v1_lineage_node_reporting_service_pb2
from acme.lineage.v1 import lineage_pb2 as lineage_v1_lineage_pb2
from acme.lineage.v1 import refs_pb2 as lineage_v1_refs_pb2
from acme.metrics.v1 import metric_alert_history_service_pb2 as metrics_v1_metric_alert_history_service_pb2
from acme.metrics.v1 import metrics_pb2 as metrics_v1_metrics_pb2
from acme.modelregistry.v1 import (
    registered_model_query_service_pb2 as modelregistry_v1_registered_model_query_service_pb2,
)
from acme.notifications.v1 import notification_query_service_pb2 as notifications_v1_notification_query_service_pb2
from acme.notifications.v1 import notification_service_pb2 as notifications_v1_notification_service_pb2
from acme.notifications.v1 import notifications_pb2 as notifications_v1_notifications_pb2
from acme.pipelines.v1 import (
    pipeline_step_calculation_service_pb2 as pipelines_v1_pipeline_step_calculation_service_pb2,
)
from acme.pipelines.v1 import pipelines_pb2 as pipelines_v1_pipelines_pb2
from acme.recruiting.v1 import job_opening_query_service_pb2 as recruiting_v1_job_opening_query_service_pb2
from acme.reviews.v1 import product_review_service_pb2 as reviews_v1_product_review_service_pb2

from acme_data.platform.models import ValidatedModel


@dataclass(frozen=True, slots=True)
class ImpactCalculationRecalculateImpacts0Command:
    """Inputs required to browse access policies."""
    context: common_v1_context_pb2.RequestContext
    filter_region: str
    filter_created_after: timestamp_pb2.Timestamp
    filter_owner_id: str


def to_impact_calculation_recalculate_impacts0_command(
    command: ImpactCalculationRecalculateImpacts0Command
) -> authorization_v1_access_policy_query_service_pb2.BrowseAccessPoliciesRequest:
    return authorization_v1_access_policy_query_service_pb2.BrowseAccessPoliciesRequest(
        context=command.context,
        filter=authorization_v1_access_policy_query_service_pb2.BrowseAccessPoliciesRequest.Filter(
            created_after=command.filter_created_after,
            owner_id=command.filter_owner_id,
            region=command.filter_region
        )
    )


@dataclass(frozen=True, slots=True)
class ImpactCalculationRecalculateImpacts1Command(ValidatedModel):
    """Inputs required to estimate lineage edge."""
    context: common_v1_context_pb2.RequestContext
    details_destination_recipient: str
    details_destination_region: str
    details_destination_country_code: str


def to_impact_calculation_recalculate_impacts1_command(
    command: ImpactCalculationRecalculateImpacts1Command
) -> lineage_v1_lineage_edge_calculation_service_pb2.EstimateLineageEdgeRequest:
    return lineage_v1_lineage_edge_calculation_service_pb2.EstimateLineageEdgeRequest(
        context=command.context,
        details=lineage_v1_lineage_edge_calculation_service_pb2.EstimateLineageEdgeRequest.Details(
            destination=common_v1_address_pb2.PostalAddress(
                country_code=command.details_destination_country_code,
                recipient=command.details_destination_recipient,
                region=command.details_destination_region
            )
        )
    )


@dataclass(frozen=True, slots=True)
class ImpactLifecycleExpireImpact1Command:
    """Inputs required to resolve lineage edge conflict."""
    context: common_v1_context_pb2.RequestContext
    lineage_edge_subject_display_name: str


def to_impact_lifecycle_expire_impact1_command(
    command: ImpactLifecycleExpireImpact1Command
) -> lineage_v1_lineage_edge_sync_service_pb2.ResolveLineageEdgeConflictRequest:
    return lineage_v1_lineage_edge_sync_service_pb2.ResolveLineageEdgeConflictRequest(
        context=command.context,
        lineage_edge=lineage_v1_lineage_pb2.LineageEdge(
            subject=lineage_v1_refs_pb2.ImpactRef(display_name=command.lineage_edge_subject_display_name)
        )
    )


@dataclass(frozen=True, slots=True)
class ImpactReportingScheduleImpactReport1Command:
    """Inputs required to estimate pipeline step."""
    context: common_v1_context_pb2.RequestContext
    details_destination_country_code: str
    pipeline_step_owner_display_name: str
    details_destination_region: str
    details_destination_recipient: str


def to_impact_reporting_schedule_impact_report1_command(
    command: ImpactReportingScheduleImpactReport1Command
) -> pipelines_v1_pipeline_step_calculation_service_pb2.EstimatePipelineStepRequest:
    return pipelines_v1_pipeline_step_calculation_service_pb2.EstimatePipelineStepRequest(
        context=command.context,
        details=pipelines_v1_pipeline_step_calculation_service_pb2.EstimatePipelineStepRequest.Details(
            destination=common_v1_address_pb2.PostalAddress(
                country_code=command.details_destination_country_code,
                recipient=command.details_destination_recipient,
                region=command.details_destination_region
            )
        ),
        pipeline_step=pipelines_v1_pipelines_pb2.PipelineStep(
            owner=identity_v1_refs_pb2.UserRef(display_name=command.pipeline_step_owner_display_name)
        )
    )


@dataclass(frozen=True, slots=True)
class ImpactReportingScheduleImpactReport2Command(ValidatedModel):
    """Inputs required to list product reviews."""
    context: common_v1_context_pb2.RequestContext
    filter_region: str
    filter_created_after: timestamp_pb2.Timestamp
    filter_owner_id: str
    filter_labels: dict[str, str]


def to_impact_reporting_schedule_impact_report2_command(
    command: ImpactReportingScheduleImpactReport2Command
) -> reviews_v1_product_review_service_pb2.ListProductReviewsRequest:
    return reviews_v1_product_review_service_pb2.ListProductReviewsRequest(
        context=command.context,
        filter=reviews_v1_product_review_service_pb2.ListProductReviewsRequest.Filter(
            created_after=command.filter_created_after,
            labels=command.filter_labels,
            owner_id=command.filter_owner_id,
            region=command.filter_region
        )
    )


@dataclass(frozen=True, slots=True)
class ImpactSyncResolveImpactConflict3Command(ValidatedModel):
    """Inputs required to resolve lineage edge conflict."""
    context: common_v1_context_pb2.RequestContext
    lineage_edge_subject_display_name: str
    lineage_edge_measurements_unit: str
    lineage_edge_correlation_id: str


def to_impact_sync_resolve_impact_conflict3_command(
    command: ImpactSyncResolveImpactConflict3Command
) -> lineage_v1_lineage_edge_sync_service_pb2.ResolveLineageEdgeConflictRequest:
    return lineage_v1_lineage_edge_sync_service_pb2.ResolveLineageEdgeConflictRequest(
        context=command.context,
        lineage_edge=lineage_v1_lineage_pb2.LineageEdge(
            correlation_id=command.lineage_edge_correlation_id,
            measurements=[lineage_v1_lineage_pb2.LineageEdgeMeasurement(unit=command.lineage_edge_measurements_unit)],
            subject=lineage_v1_refs_pb2.ImpactRef(display_name=command.lineage_edge_subject_display_name)
        )
    )


@dataclass(frozen=True, slots=True)
class ImpactValidationExplainImpactDecision3Command:
    """Inputs required to get impact rates."""
    context: common_v1_context_pb2.RequestContext
    impact_id: str


def to_impact_validation_explain_impact_decision3_command(
    command: ImpactValidationExplainImpactDecision3Command
) -> lineage_v1_impact_calculation_service_pb2.GetImpactRatesRequest:
    return lineage_v1_impact_calculation_service_pb2.GetImpactRatesRequest(
        context=command.context,
        impact_id=command.impact_id
    )


@dataclass(frozen=True, slots=True)
class ImpactWorkflowInspectImpactWorkflow1Command(ValidatedModel):
    """Inputs required to pause lineage edge workflow."""
    context: common_v1_context_pb2.RequestContext
    lineage_edge_subject_display_name: str
    details_notify_email: str
    lineage_edge_attributes: dict[str, str]


def to_impact_workflow_inspect_impact_workflow1_command(
    command: ImpactWorkflowInspectImpactWorkflow1Command
) -> lineage_v1_lineage_edge_workflow_service_pb2.PauseLineageEdgeWorkflowRequest:
    return lineage_v1_lineage_edge_workflow_service_pb2.PauseLineageEdgeWorkflowRequest(
        context=command.context,
        details=lineage_v1_lineage_edge_workflow_service_pb2.PauseLineageEdgeWorkflowRequest.Details(
            notify=common_v1_contact_pb2.ContactInfo(email=command.details_notify_email)
        ),
        lineage_edge=lineage_v1_lineage_pb2.LineageEdge(
            attributes=command.lineage_edge_attributes,
            subject=lineage_v1_refs_pb2.ImpactRef(display_name=command.lineage_edge_subject_display_name)
        )
    )


@dataclass(frozen=True, slots=True)
class LineageEdgeApprovalDelegateLineageEdgeApproval3Command:
    """Inputs required to validate preference."""
    context: common_v1_context_pb2.RequestContext
    preference_block_notify_email: str
    preference_audit_updated_by: str
    preference_owner_email: str


def to_lineage_edge_approval_delegate_lineage_edge_approval3_command(
    command: LineageEdgeApprovalDelegateLineageEdgeApproval3Command
) -> customers_v1_preference_validation_service_pb2.ValidatePreferenceRequest:
    return customers_v1_preference_validation_service_pb2.ValidatePreferenceRequest(
        context=command.context,
        preference=customers_v1_customers_pb2.Preference(
            audit=common_v1_audit_pb2.AuditInfo(updated_by=command.preference_audit_updated_by),
            block=customers_v1_customers_pb2.PreferenceBlockAction(notify_email=command.preference_block_notify_email),
            owner=identity_v1_refs_pb2.UserRef(email=command.preference_owner_email)
        )
    )


@dataclass(frozen=True, slots=True)
class LineageEdgeCalculationCalculateLineageEdge1Command:
    """Inputs required to recalculate lineage nodes."""
    context: common_v1_context_pb2.RequestContext
    lineage_node_children_children_audit_updated_at: timestamp_pb2.Timestamp
    lineage_node_children_children_location_recipient: str
    lineage_node_children_children_location_locality: str


def to_lineage_edge_calculation_calculate_lineage_edge1_command(
    command: LineageEdgeCalculationCalculateLineageEdge1Command
) -> lineage_v1_lineage_node_calculation_service_pb2.RecalculateLineageNodesRequest:
    return lineage_v1_lineage_node_calculation_service_pb2.RecalculateLineageNodesRequest(
        context=command.context,
        lineage_node=lineage_v1_lineage_pb2.LineageNode(
            children=[
                lineage_v1_lineage_pb2.LineageNode(
                    children=[
                        lineage_v1_lineage_pb2.LineageNode(
                            audit=common_v1_audit_pb2.AuditInfo(
                                updated_at=command.lineage_node_children_children_audit_updated_at
                            ),
                            location=common_v1_address_pb2.PostalAddress(
                                locality=command.lineage_node_children_children_location_locality,
                                recipient=command.lineage_node_children_children_location_recipient
                            )
                        )
                    ]
                )
            ]
        )
    )


@dataclass(frozen=True, slots=True)
class LineageEdgeCalculationCompareLineageEdgeOptions0Command(ValidatedModel):
    """Inputs required to explain lineage node calculation."""
    context: common_v1_context_pb2.RequestContext
    lineage_node_children_children_location_lines: list[str]
    lineage_node_children_children_location_region: str


def to_lineage_edge_calculation_compare_lineage_edge_options0_command(
    command: LineageEdgeCalculationCompareLineageEdgeOptions0Command
) -> lineage_v1_lineage_node_calculation_service_pb2.ExplainLineageNodeCalculationRequest:
    return lineage_v1_lineage_node_calculation_service_pb2.ExplainLineageNodeCalculationRequest(
        context=command.context,
        lineage_node=lineage_v1_lineage_pb2.LineageNode(
            children=[
                lineage_v1_lineage_pb2.LineageNode(
                    children=[
                        lineage_v1_lineage_pb2.LineageNode(
                            location=common_v1_address_pb2.PostalAddress(
                                lines=command.lineage_node_children_children_location_lines,
                                region=command.lineage_node_children_children_location_region
                            )
                        )
                    ]
                )
            ]
        )
    )


@dataclass(frozen=True, slots=True)
class LineageEdgeImportCancelLineageEdgeImport1Command:
    """Inputs required to resolve lineage edges."""
    context: common_v1_context_pb2.RequestContext


def to_lineage_edge_import_cancel_lineage_edge_import1_command(
    command: LineageEdgeImportCancelLineageEdgeImport1Command
) -> lineage_v1_lineage_edge_query_service_pb2.ResolveLineageEdgesRequest:
    return lineage_v1_lineage_edge_query_service_pb2.ResolveLineageEdgesRequest(context=command.context)


@dataclass(frozen=True, slots=True)
class LineageEdgeLifecycleExpireLineageEdge1Command:
    """Inputs required to list lineage node reports."""
    context: common_v1_context_pb2.RequestContext
    filter_created_after: timestamp_pb2.Timestamp
    filter_owner_id: str
    filter_labels: dict[str, str]


def to_lineage_edge_lifecycle_expire_lineage_edge1_command(
    command: LineageEdgeLifecycleExpireLineageEdge1Command
) -> lineage_v1_lineage_node_reporting_service_pb2.ListLineageNodeReportsRequest:
    return lineage_v1_lineage_node_reporting_service_pb2.ListLineageNodeReportsRequest(
        context=command.context,
        filter=lineage_v1_lineage_node_reporting_service_pb2.ListLineageNodeReportsRequest.Filter(
            created_after=command.filter_created_after,
            labels=command.filter_labels,
            owner_id=command.filter_owner_id
        )
    )


@dataclass(frozen=True, slots=True)
class LineageEdgeReportingScheduleLineageEdgeReport0Command:
    """Inputs required to browse job openings."""
    context: common_v1_context_pb2.RequestContext
    filter_labels: dict[str, str]
    filter_owner_id: str


def to_lineage_edge_reporting_schedule_lineage_edge_report0_command(
    command: LineageEdgeReportingScheduleLineageEdgeReport0Command
) -> recruiting_v1_job_opening_query_service_pb2.BrowseJobOpeningsRequest:
    return recruiting_v1_job_opening_query_service_pb2.BrowseJobOpeningsRequest(
        context=command.context,
        filter=recruiting_v1_job_opening_query_service_pb2.BrowseJobOpeningsRequest.Filter(
            labels=command.filter_labels,
            owner_id=command.filter_owner_id
        )
    )


@dataclass(frozen=True, slots=True)
class LineageEdgeReportingShareLineageEdgeReport0Command(ValidatedModel):
    """Inputs required to validate ledger account."""
    context: common_v1_context_pb2.RequestContext
    ledger_account_contact_email: str
    details_contact_phone: str
    ledger_account_contact_name: common_v1_contact_pb2.PersonName


def to_lineage_edge_reporting_share_lineage_edge_report0_command(
    command: LineageEdgeReportingShareLineageEdgeReport0Command
) -> ledger_v1_ledger_account_validation_service_pb2.ValidateLedgerAccountRequest:
    return ledger_v1_ledger_account_validation_service_pb2.ValidateLedgerAccountRequest(
        context=command.context,
        details=ledger_v1_ledger_account_validation_service_pb2.ValidateLedgerAccountRequest.Details(
            contact=common_v1_contact_pb2.ContactInfo(phone=command.details_contact_phone)
        ),
        ledger_account=ledger_v1_ledger_pb2.LedgerAccount(
            contact=common_v1_contact_pb2.ContactInfo(
                email=command.ledger_account_contact_email,
                name=command.ledger_account_contact_name
            )
        )
    )


@dataclass(frozen=True, slots=True)
class LineageEdgeValidationCheckLineageEdgeEligibility1Command:
    """Inputs required to revert metric alert."""
    context: common_v1_context_pb2.RequestContext
    metric_alert_owner_user_id: str
    metric_alert_audit_etag: str


def to_lineage_edge_validation_check_lineage_edge_eligibility1_command(
    command: LineageEdgeValidationCheckLineageEdgeEligibility1Command
) -> metrics_v1_metric_alert_history_service_pb2.RevertMetricAlertRequest:
    return metrics_v1_metric_alert_history_service_pb2.RevertMetricAlertRequest(
        context=command.context,
        metric_alert=metrics_v1_metrics_pb2.MetricAlert(
            audit=common_v1_audit_pb2.AuditInfo(etag=command.metric_alert_audit_etag),
            owner=identity_v1_refs_pb2.UserRef(user_id=command.metric_alert_owner_user_id)
        )
    )


@dataclass(frozen=True, slots=True)
class LineageEdgeValidationExplainLineageEdgeDecision0Command(ValidatedModel):
    """Inputs required to estimate impact."""
    context: common_v1_context_pb2.RequestContext
    impact_requester_email: str
    impact_customer_display_name: str
    impact_requester_phone: str


def to_lineage_edge_validation_explain_lineage_edge_decision0_command(
    command: LineageEdgeValidationExplainLineageEdgeDecision0Command
) -> lineage_v1_impact_calculation_service_pb2.EstimateImpactRequest:
    return lineage_v1_impact_calculation_service_pb2.EstimateImpactRequest(
        context=command.context,
        impact=lineage_v1_lineage_pb2.Impact(
            customer=customers_v1_refs_pb2.CustomerRef(display_name=command.impact_customer_display_name),
            requester=common_v1_contact_pb2.ContactInfo(
                email=command.impact_requester_email,
                phone=command.impact_requester_phone
            )
        )
    )


@dataclass(frozen=True, slots=True)
class LineageEdgeWorkflowAdvanceLineageEdgeWorkflow2Command:
    """Inputs required to summarize access policies."""
    context: common_v1_context_pb2.RequestContext
    annotations: dict[str, str]
    reason: str


def to_lineage_edge_workflow_advance_lineage_edge_workflow2_command(
    command: LineageEdgeWorkflowAdvanceLineageEdgeWorkflow2Command
) -> authorization_v1_access_policy_query_service_pb2.SummarizeAccessPoliciesRequest:
    return authorization_v1_access_policy_query_service_pb2.SummarizeAccessPoliciesRequest(
        annotations=command.annotations,
        context=command.context,
        reason=command.reason
    )


@dataclass(frozen=True, slots=True)
class LineageNodeApprovalRejectLineageNode2Command:
    """Inputs required to preview anomaly feedback."""
    context: common_v1_context_pb2.RequestContext
    details_contact_email: str


def to_lineage_node_approval_reject_lineage_node2_command(
    command: LineageNodeApprovalRejectLineageNode2Command
) -> anomalies_v1_anomaly_feedback_validation_service_pb2.PreviewAnomalyFeedbackRequest:
    return anomalies_v1_anomaly_feedback_validation_service_pb2.PreviewAnomalyFeedbackRequest(
        context=command.context,
        details=anomalies_v1_anomaly_feedback_validation_service_pb2.PreviewAnomalyFeedbackRequest.Details(
            contact=common_v1_contact_pb2.ContactInfo(email=command.details_contact_email)
        )
    )


@dataclass(frozen=True, slots=True)
class LineageNodeCalculationSimulateLineageNode0Command:
    """Inputs required to summarize documents."""
    context: common_v1_context_pb2.RequestContext
    annotations: dict[str, str]
    reason: str
    details_filters: dict[str, str]


def to_lineage_node_calculation_simulate_lineage_node0_command(
    command: LineageNodeCalculationSimulateLineageNode0Command
) -> documents_v1_document_query_service_pb2.SummarizeDocumentsRequest:
    return documents_v1_document_query_service_pb2.SummarizeDocumentsRequest(
        annotations=command.annotations,
        context=command.context,
        details=documents_v1_document_query_service_pb2.SummarizeDocumentsRequest.Details(
            filters=command.details_filters
        ),
        reason=command.reason
    )


@dataclass(frozen=True, slots=True)
class LineageNodeCalculationSimulateLineageNode1Command(ValidatedModel):
    """Inputs required to summarize notifications."""
    context: common_v1_context_pb2.RequestContext
    details_period: common_v1_audit_pb2.TimeWindow
    reason: str
    annotations: dict[str, str]


def to_lineage_node_calculation_simulate_lineage_node1_command(
    command: LineageNodeCalculationSimulateLineageNode1Command
) -> notifications_v1_notification_query_service_pb2.SummarizeNotificationsRequest:
    return notifications_v1_notification_query_service_pb2.SummarizeNotificationsRequest(
        annotations=command.annotations,
        context=command.context,
        details=notifications_v1_notification_query_service_pb2.SummarizeNotificationsRequest.Details(
            period=command.details_period
        ),
        reason=command.reason
    )


@dataclass(frozen=True, slots=True)
class LineageNodeQueryExportLineageNodes0Command(ValidatedModel):
    """Inputs required to calculate lineage edge."""
    context: common_v1_context_pb2.RequestContext
    details_destination_region: str
    lineage_edge_occurred_at: timestamp_pb2.Timestamp


def to_lineage_node_query_export_lineage_nodes0_command(
    command: LineageNodeQueryExportLineageNodes0Command
) -> lineage_v1_lineage_edge_calculation_service_pb2.CalculateLineageEdgeRequest:
    return lineage_v1_lineage_edge_calculation_service_pb2.CalculateLineageEdgeRequest(
        context=command.context,
        details=lineage_v1_lineage_edge_calculation_service_pb2.CalculateLineageEdgeRequest.Details(
            destination=common_v1_address_pb2.PostalAddress(region=command.details_destination_region)
        ),
        lineage_edge=lineage_v1_lineage_pb2.LineageEdge(occurred_at=command.lineage_edge_occurred_at)
    )


@dataclass(frozen=True, slots=True)
class LineageNodeReportingGenerateLineageNodeReport2Command:
    """Inputs required to clone notification."""
    context: common_v1_context_pb2.RequestContext
    notification_requester_email: str
    notification_requester_preferred_channel: str
    notification_audit_updated_at: timestamp_pb2.Timestamp


def to_lineage_node_reporting_generate_lineage_node_report2_command(
    command: LineageNodeReportingGenerateLineageNodeReport2Command
) -> notifications_v1_notification_service_pb2.CloneNotificationRequest:
    return notifications_v1_notification_service_pb2.CloneNotificationRequest(
        context=command.context,
        notification=notifications_v1_notifications_pb2.Notification(
            audit=common_v1_audit_pb2.AuditInfo(updated_at=command.notification_audit_updated_at),
            requester=common_v1_contact_pb2.ContactInfo(
                email=command.notification_requester_email,
                preferred_channel=command.notification_requester_preferred_channel
            )
        )
    )


@dataclass(frozen=True, slots=True)
class LineageNodeReportingScheduleLineageNodeReport0Command(ValidatedModel):
    """Inputs required to score consent record."""
    context: common_v1_context_pb2.RequestContext
    annotations: dict[str, str]
    reason: str
    consent_record_attributes: dict[str, str]


def to_lineage_node_reporting_schedule_lineage_node_report0_command(
    command: LineageNodeReportingScheduleLineageNodeReport0Command
) -> customers_v1_consent_record_validation_service_pb2.ScoreConsentRecordRequest:
    return customers_v1_consent_record_validation_service_pb2.ScoreConsentRecordRequest(
        annotations=command.annotations,
        consent_record=customers_v1_customers_pb2.ConsentRecord(attributes=command.consent_record_attributes),
        context=command.context,
        reason=command.reason
    )


@dataclass(frozen=True, slots=True)
class LineageNodeSyncResolveLineageNodeConflict1Command:
    """Inputs required to browse registered models."""
    context: common_v1_context_pb2.RequestContext
    filter_region: str
    filter_created_after: timestamp_pb2.Timestamp
    filter_labels: dict[str, str]


def to_lineage_node_sync_resolve_lineage_node_conflict1_command(
    command: LineageNodeSyncResolveLineageNodeConflict1Command
) -> modelregistry_v1_registered_model_query_service_pb2.BrowseRegisteredModelsRequest:
    return modelregistry_v1_registered_model_query_service_pb2.BrowseRegisteredModelsRequest(
        context=command.context,
        filter=modelregistry_v1_registered_model_query_service_pb2.BrowseRegisteredModelsRequest.Filter(
            created_after=command.filter_created_after,
            labels=command.filter_labels,
            region=command.filter_region
        )
    )


@dataclass(frozen=True, slots=True)
class LineageNodeValidationPreviewLineageNode3Command:
    """Inputs required to compare lineage edge options."""
    context: common_v1_context_pb2.RequestContext
    lineage_edge_subject_display_name: str
    details_destination_region: str


def to_lineage_node_validation_preview_lineage_node3_command(
    command: LineageNodeValidationPreviewLineageNode3Command
) -> lineage_v1_lineage_edge_calculation_service_pb2.CompareLineageEdgeOptionsRequest:
    return lineage_v1_lineage_edge_calculation_service_pb2.CompareLineageEdgeOptionsRequest(
        context=command.context,
        details=lineage_v1_lineage_edge_calculation_service_pb2.CompareLineageEdgeOptionsRequest.Details(
            destination=common_v1_address_pb2.PostalAddress(region=command.details_destination_region)
        ),
        lineage_edge=lineage_v1_lineage_pb2.LineageEdge(
            subject=lineage_v1_refs_pb2.ImpactRef(display_name=command.lineage_edge_subject_display_name)
        )
    )


@dataclass(frozen=True, slots=True)
class LineageNodeValidationValidateLineageNode0Command(ValidatedModel):
    """Inputs required to recalculate lineage nodes."""
    context: common_v1_context_pb2.RequestContext
    lineage_node_children_children_audit_created_by: str
    lineage_node_children_location_country_code: str


def to_lineage_node_validation_validate_lineage_node0_command(
    command: LineageNodeValidationValidateLineageNode0Command
) -> lineage_v1_lineage_node_calculation_service_pb2.RecalculateLineageNodesRequest:
    return lineage_v1_lineage_node_calculation_service_pb2.RecalculateLineageNodesRequest(
        context=command.context,
        lineage_node=lineage_v1_lineage_pb2.LineageNode(
            children=[
                lineage_v1_lineage_pb2.LineageNode(
                    children=[
                        lineage_v1_lineage_pb2.LineageNode(
                            audit=common_v1_audit_pb2.AuditInfo(
                                created_by=command.lineage_node_children_children_audit_created_by
                            )
                        )
                    ],
                    location=common_v1_address_pb2.PostalAddress(
                        country_code=command.lineage_node_children_location_country_code
                    )
                )
            ]
        )
    )
