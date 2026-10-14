"""Typed commands crossing the anomalies application boundary."""

from __future__ import annotations

from dataclasses import dataclass

from google.protobuf import timestamp_pb2 as timestamp_pb2

from acme.anomalies.v1 import anomalies_pb2 as anomalies_v1_anomalies_pb2
from acme.anomalies.v1 import anomaly_approval_service_pb2 as anomalies_v1_anomaly_approval_service_pb2
from acme.anomalies.v1 import (
    anomaly_feedback_validation_service_pb2 as anomalies_v1_anomaly_feedback_validation_service_pb2,
)
from acme.anomalies.v1 import anomaly_query_service_pb2 as anomalies_v1_anomaly_query_service_pb2
from acme.anomalies.v1 import anomaly_service_pb2 as anomalies_v1_anomaly_service_pb2
from acme.anomalies.v1 import anomaly_validation_service_pb2 as anomalies_v1_anomaly_validation_service_pb2
from acme.anomalies.v1 import detector_validation_service_pb2 as anomalies_v1_detector_validation_service_pb2
from acme.anomalies.v1 import refs_pb2 as anomalies_v1_refs_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.common.v1 import context_pb2 as common_v1_context_pb2
from acme.customers.v1 import refs_pb2 as customers_v1_refs_pb2
from acme.datasets.v1 import data_schema_validation_service_pb2 as datasets_v1_data_schema_validation_service_pb2
from acme.datasets.v1 import dataset_query_service_pb2 as datasets_v1_dataset_query_service_pb2
from acme.datasets.v1 import datasets_pb2 as datasets_v1_datasets_pb2
from acme.datasets.v1 import refs_pb2 as datasets_v1_refs_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.lineage.v1 import impact_sync_service_pb2 as lineage_v1_impact_sync_service_pb2
from acme.lineage.v1 import lineage_node_sync_service_pb2 as lineage_v1_lineage_node_sync_service_pb2
from acme.lineage.v1 import lineage_pb2 as lineage_v1_lineage_pb2
from acme.pipelines.v1 import pipeline_service_pb2 as pipelines_v1_pipeline_service_pb2
from acme.pipelines.v1 import pipelines_pb2 as pipelines_v1_pipelines_pb2

from acme_data.platform.models import ValidatedModel


@dataclass(frozen=True, slots=True)
class AnomalyApprovalListPendingAnomalies1Command:
    """Inputs required to resolve impact conflict."""
    context: common_v1_context_pb2.RequestContext
    impact_customer_customer_id: str
    impact_customer_email: str


def to_anomaly_approval_list_pending_anomalies1_command(
    command: AnomalyApprovalListPendingAnomalies1Command
) -> lineage_v1_impact_sync_service_pb2.ResolveImpactConflictRequest:
    return lineage_v1_impact_sync_service_pb2.ResolveImpactConflictRequest(
        context=command.context,
        impact=lineage_v1_lineage_pb2.Impact(
            customer=customers_v1_refs_pb2.CustomerRef(
                customer_id=command.impact_customer_customer_id,
                email=command.impact_customer_email
            )
        )
    )


@dataclass(frozen=True, slots=True)
class AnomalyApprovalRecallAnomaly0Command(ValidatedModel):
    """Inputs required to update pipeline."""
    context: common_v1_context_pb2.RequestContext
    pipeline_participants_contact_email: str
    pipeline_participants_contact_preferred_channel: str
    pipeline_audit_created_by: str
    pipeline_organizer_display_name: str


def to_anomaly_approval_recall_anomaly0_command(
    command: AnomalyApprovalRecallAnomaly0Command
) -> pipelines_v1_pipeline_service_pb2.UpdatePipelineRequest:
    return pipelines_v1_pipeline_service_pb2.UpdatePipelineRequest(
        context=command.context,
        pipeline=pipelines_v1_pipelines_pb2.Pipeline(
            audit=common_v1_audit_pb2.AuditInfo(created_by=command.pipeline_audit_created_by),
            organizer=identity_v1_refs_pb2.UserRef(display_name=command.pipeline_organizer_display_name),
            participants=[
                pipelines_v1_pipelines_pb2.PipelineParticipant(
                    contact=common_v1_contact_pb2.ContactInfo(
                        email=command.pipeline_participants_contact_email,
                        preferred_channel=command.pipeline_participants_contact_preferred_channel
                    )
                )
            ]
        )
    )


@dataclass(frozen=True, slots=True)
class AnomalyFeedbackApprovalRecallAnomalyFeedback2Command(ValidatedModel):
    """Inputs required to score anomaly."""
    context: common_v1_context_pb2.RequestContext
    anomaly_customer_display_name: str
    anomaly_requester_email: str
    anomaly_assignee_user_id: str
    anomaly_assignee_display_name: str


def to_anomaly_feedback_approval_recall_anomaly_feedback2_command(
    command: AnomalyFeedbackApprovalRecallAnomalyFeedback2Command
) -> anomalies_v1_anomaly_validation_service_pb2.ScoreAnomalyRequest:
    return anomalies_v1_anomaly_validation_service_pb2.ScoreAnomalyRequest(
        anomaly=anomalies_v1_anomalies_pb2.Anomaly(
            assignee=identity_v1_refs_pb2.UserRef(
                display_name=command.anomaly_assignee_display_name,
                user_id=command.anomaly_assignee_user_id
            ),
            customer=anomalies_v1_refs_pb2.DetectorRef(display_name=command.anomaly_customer_display_name),
            requester=common_v1_contact_pb2.ContactInfo(email=command.anomaly_requester_email)
        ),
        context=command.context
    )


@dataclass(frozen=True, slots=True)
class AnomalyFeedbackCalculationQuoteAnomalyFeedback2Command(ValidatedModel):
    """Inputs required to check anomaly eligibility."""
    context: common_v1_context_pb2.RequestContext
    anomaly_comments_created_at: timestamp_pb2.Timestamp


def to_anomaly_feedback_calculation_quote_anomaly_feedback2_command(
    command: AnomalyFeedbackCalculationQuoteAnomalyFeedback2Command
) -> anomalies_v1_anomaly_validation_service_pb2.CheckAnomalyEligibilityRequest:
    return anomalies_v1_anomaly_validation_service_pb2.CheckAnomalyEligibilityRequest(
        anomaly=anomalies_v1_anomalies_pb2.Anomaly(
            comments=[anomalies_v1_anomalies_pb2.AnomalyComment(created_at=command.anomaly_comments_created_at)]
        ),
        context=command.context
    )


@dataclass(frozen=True, slots=True)
class AnomalyFeedbackValidationNormalizeAnomalyFeedback1Command(ValidatedModel):
    """Inputs required to validate detector."""
    context: common_v1_context_pb2.RequestContext
    detector_block_reason: str


def to_anomaly_feedback_validation_normalize_anomaly_feedback1_command(
    command: AnomalyFeedbackValidationNormalizeAnomalyFeedback1Command
) -> anomalies_v1_detector_validation_service_pb2.ValidateDetectorRequest:
    return anomalies_v1_detector_validation_service_pb2.ValidateDetectorRequest(
        context=command.context,
        detector=anomalies_v1_anomalies_pb2.Detector(
            block=anomalies_v1_anomalies_pb2.DetectorBlockAction(reason=command.detector_block_reason)
        )
    )


@dataclass(frozen=True, slots=True)
class AnomalyFeedbackWorkflowResumeAnomalyFeedbackWorkflow1Command(ValidatedModel):
    """Inputs required to preview data schema."""
    context: common_v1_context_pb2.RequestContext
    data_schema_children_children_audit_updated_at: timestamp_pb2.Timestamp


def to_anomaly_feedback_workflow_resume_anomaly_feedback_workflow1_command(
    command: AnomalyFeedbackWorkflowResumeAnomalyFeedbackWorkflow1Command
) -> datasets_v1_data_schema_validation_service_pb2.PreviewDataSchemaRequest:
    return datasets_v1_data_schema_validation_service_pb2.PreviewDataSchemaRequest(
        context=command.context,
        data_schema=datasets_v1_datasets_pb2.DataSchema(
            children=[
                datasets_v1_datasets_pb2.DataSchema(
                    children=[
                        datasets_v1_datasets_pb2.DataSchema(
                            audit=common_v1_audit_pb2.AuditInfo(
                                updated_at=command.data_schema_children_children_audit_updated_at
                            )
                        )
                    ]
                )
            ]
        )
    )


@dataclass(frozen=True, slots=True)
class AnomalyUpdateAnomaly1Command:
    """Inputs required to validate anomaly feedback."""
    context: common_v1_context_pb2.RequestContext
    anomaly_feedback_subject_display_name: str


def to_anomaly_update_anomaly1_command(
    command: AnomalyUpdateAnomaly1Command
) -> anomalies_v1_anomaly_feedback_validation_service_pb2.ValidateAnomalyFeedbackRequest:
    return anomalies_v1_anomaly_feedback_validation_service_pb2.ValidateAnomalyFeedbackRequest(
        anomaly_feedback=anomalies_v1_anomalies_pb2.AnomalyFeedback(
            subject=datasets_v1_refs_pb2.DatasetRef(display_name=command.anomaly_feedback_subject_display_name)
        ),
        context=command.context
    )


@dataclass(frozen=True, slots=True)
class AnomalyWorkflowAdvanceAnomalyWorkflow1Command:
    """Inputs required to get anomaly."""
    context: common_v1_context_pb2.RequestContext
    anomaly_id: str


def to_anomaly_workflow_advance_anomaly_workflow1_command(
    command: AnomalyWorkflowAdvanceAnomalyWorkflow1Command
) -> anomalies_v1_anomaly_service_pb2.GetAnomalyRequest:
    return anomalies_v1_anomaly_service_pb2.GetAnomalyRequest(anomaly_id=command.anomaly_id, context=command.context)


@dataclass(frozen=True, slots=True)
class AnomalyWorkflowCancelAnomalyWorkflow0Command(ValidatedModel):
    """Inputs required to resolve datasets."""
    context: common_v1_context_pb2.RequestContext


def to_anomaly_workflow_cancel_anomaly_workflow0_command(
    command: AnomalyWorkflowCancelAnomalyWorkflow0Command
) -> datasets_v1_dataset_query_service_pb2.ResolveDatasetsRequest:
    return datasets_v1_dataset_query_service_pb2.ResolveDatasetsRequest(context=command.context)


@dataclass(frozen=True, slots=True)
class DetectorApprovalApproveDetector0Command:
    """Inputs required to submit anomaly."""
    context: common_v1_context_pb2.RequestContext
    details_approver_email: str
    anomaly_audit_created_by: str


def to_detector_approval_approve_detector0_command(
    command: DetectorApprovalApproveDetector0Command
) -> anomalies_v1_anomaly_approval_service_pb2.SubmitAnomalyRequest:
    return anomalies_v1_anomaly_approval_service_pb2.SubmitAnomalyRequest(
        anomaly=anomalies_v1_anomalies_pb2.Anomaly(
            audit=common_v1_audit_pb2.AuditInfo(created_by=command.anomaly_audit_created_by)
        ),
        context=command.context,
        details=anomalies_v1_anomaly_approval_service_pb2.SubmitAnomalyRequest.Details(
            approver=identity_v1_refs_pb2.UserRef(email=command.details_approver_email)
        )
    )


@dataclass(frozen=True, slots=True)
class DetectorApprovalRejectDetector2Command:
    """Inputs required to resolve anomalies."""
    context: common_v1_context_pb2.RequestContext


def to_detector_approval_reject_detector2_command(
    command: DetectorApprovalRejectDetector2Command
) -> anomalies_v1_anomaly_query_service_pb2.ResolveAnomaliesRequest:
    return anomalies_v1_anomaly_query_service_pb2.ResolveAnomaliesRequest(context=command.context)


@dataclass(frozen=True, slots=True)
class DetectorApprovalSubmitDetector0Command(ValidatedModel):
    """Inputs required to pull lineage nodes."""
    context: common_v1_context_pb2.RequestContext
    lineage_node_children_children_audit_updated_at: timestamp_pb2.Timestamp
    lineage_node_children_children_audit_etag: str
    lineage_node_children_children_manager_display_name: str
    lineage_node_children_children_manager_email: str


def to_detector_approval_submit_detector0_command(
    command: DetectorApprovalSubmitDetector0Command
) -> lineage_v1_lineage_node_sync_service_pb2.PullLineageNodesRequest:
    return lineage_v1_lineage_node_sync_service_pb2.PullLineageNodesRequest(
        context=command.context,
        lineage_node=lineage_v1_lineage_pb2.LineageNode(
            children=[
                lineage_v1_lineage_pb2.LineageNode(
                    children=[
                        lineage_v1_lineage_pb2.LineageNode(
                            audit=common_v1_audit_pb2.AuditInfo(
                                etag=command.lineage_node_children_children_audit_etag,
                                updated_at=command.lineage_node_children_children_audit_updated_at
                            ),
                            manager=identity_v1_refs_pb2.UserRef(
                                display_name=command.lineage_node_children_children_manager_display_name,
                                email=command.lineage_node_children_children_manager_email
                            )
                        )
                    ]
                )
            ]
        )
    )
