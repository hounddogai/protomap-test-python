"""Typed commands crossing the labeling application boundary."""

from __future__ import annotations

from dataclasses import dataclass

from google.protobuf import timestamp_pb2 as timestamp_pb2

from acme.authorization.v1 import access_policy_query_service_pb2 as authorization_v1_access_policy_query_service_pb2
from acme.authorization.v1 import access_policy_service_pb2 as authorization_v1_access_policy_service_pb2
from acme.authorization.v1 import authorization_pb2 as authorization_v1_authorization_pb2
from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.common.v1 import context_pb2 as common_v1_context_pb2
from acme.customers.v1 import customer_calculation_service_pb2 as customers_v1_customer_calculation_service_pb2
from acme.customers.v1 import customers_pb2 as customers_v1_customers_pb2
from acme.datasets.v1 import refs_pb2 as datasets_v1_refs_pb2
from acme.featurestore.v1 import feature_value_sync_service_pb2 as featurestore_v1_feature_value_sync_service_pb2
from acme.featurestore.v1 import (
    feature_view_calculation_service_pb2 as featurestore_v1_feature_view_calculation_service_pb2,
)
from acme.featurestore.v1 import featurestore_pb2 as featurestore_v1_featurestore_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.labeling.v1 import annotation_approval_service_pb2 as labeling_v1_annotation_approval_service_pb2
from acme.labeling.v1 import label_set_calculation_service_pb2 as labeling_v1_label_set_calculation_service_pb2
from acme.labeling.v1 import label_set_sync_service_pb2 as labeling_v1_label_set_sync_service_pb2
from acme.labeling.v1 import label_set_validation_service_pb2 as labeling_v1_label_set_validation_service_pb2
from acme.labeling.v1 import labeling_pb2 as labeling_v1_labeling_pb2
from acme.labeling.v1 import labeling_task_approval_service_pb2 as labeling_v1_labeling_task_approval_service_pb2
from acme.labeling.v1 import labeling_task_calculation_service_pb2 as labeling_v1_labeling_task_calculation_service_pb2
from acme.labeling.v1 import labeling_task_lifecycle_service_pb2 as labeling_v1_labeling_task_lifecycle_service_pb2
from acme.lineage.v1 import lineage_node_approval_service_pb2 as lineage_v1_lineage_node_approval_service_pb2
from acme.lineage.v1 import lineage_pb2 as lineage_v1_lineage_pb2
from acme.metrics.v1 import dashboard_export_service_pb2 as metrics_v1_dashboard_export_service_pb2
from acme.metrics.v1 import dashboard_notification_service_pb2 as metrics_v1_dashboard_notification_service_pb2
from acme.metrics.v1 import metric_series_export_service_pb2 as metrics_v1_metric_series_export_service_pb2
from acme.modelregistry.v1 import (
    model_version_workflow_service_pb2 as modelregistry_v1_model_version_workflow_service_pb2,
)
from acme.modelregistry.v1 import modelregistry_pb2 as modelregistry_v1_modelregistry_pb2
from acme.modelregistry.v1 import (
    registered_model_approval_service_pb2 as modelregistry_v1_registered_model_approval_service_pb2,
)
from acme.sponsorships.v1 import sponsor_service_pb2 as sponsorships_v1_sponsor_service_pb2
from acme.sponsorships.v1 import sponsorships_pb2 as sponsorships_v1_sponsorships_pb2

from acme_data.platform.models import ValidatedModel


@dataclass(frozen=True, slots=True)
class AnnotationApprovalEscalateAnnotation2Command(ValidatedModel):
    """Inputs required to share metric series export."""
    context: common_v1_context_pb2.RequestContext
    details_recipient_email: str
    annotations: dict[str, str]
    reason: str


def to_annotation_approval_escalate_annotation2_command(
    command: AnnotationApprovalEscalateAnnotation2Command
) -> metrics_v1_metric_series_export_service_pb2.ShareMetricSeriesExportRequest:
    return metrics_v1_metric_series_export_service_pb2.ShareMetricSeriesExportRequest(
        annotations=command.annotations,
        context=command.context,
        details=metrics_v1_metric_series_export_service_pb2.ShareMetricSeriesExportRequest.Details(
            recipient=common_v1_contact_pb2.ContactInfo(email=command.details_recipient_email)
        ),
        reason=command.reason
    )


@dataclass(frozen=True, slots=True)
class AnnotationCalculationCompareAnnotationOptions3Command(ValidatedModel):
    """Inputs required to clone sponsor."""
    context: common_v1_context_pb2.RequestContext
    sponsor_passport_issuing_country: str
    sponsor_contact_email: str
    sponsor_relationship_manager_user_id: str
    sponsor_audit_updated_at: timestamp_pb2.Timestamp


def to_annotation_calculation_compare_annotation_options3_command(
    command: AnnotationCalculationCompareAnnotationOptions3Command
) -> sponsorships_v1_sponsor_service_pb2.CloneSponsorRequest:
    return sponsorships_v1_sponsor_service_pb2.CloneSponsorRequest(
        context=command.context,
        sponsor=sponsorships_v1_sponsorships_pb2.Sponsor(
            audit=common_v1_audit_pb2.AuditInfo(updated_at=command.sponsor_audit_updated_at),
            contact=common_v1_contact_pb2.ContactInfo(email=command.sponsor_contact_email),
            passport=sponsorships_v1_sponsorships_pb2.SponsorPassport(
                issuing_country=command.sponsor_passport_issuing_country
            ),
            relationship_manager=identity_v1_refs_pb2.UserRef(user_id=command.sponsor_relationship_manager_user_id)
        )
    )


@dataclass(frozen=True, slots=True)
class AnnotationLifecycleReinstateAnnotation1Command:
    """Inputs required to simulate labeling task."""
    context: common_v1_context_pb2.RequestContext
    labeling_task_assignee_display_name: str
    labeling_task_assignee_email: str


def to_annotation_lifecycle_reinstate_annotation1_command(
    command: AnnotationLifecycleReinstateAnnotation1Command
) -> labeling_v1_labeling_task_calculation_service_pb2.SimulateLabelingTaskRequest:
    return labeling_v1_labeling_task_calculation_service_pb2.SimulateLabelingTaskRequest(
        context=command.context,
        labeling_task=labeling_v1_labeling_pb2.LabelingTask(
            assignee=identity_v1_refs_pb2.UserRef(
                display_name=command.labeling_task_assignee_display_name,
                email=command.labeling_task_assignee_email
            )
        )
    )


@dataclass(frozen=True, slots=True)
class AnnotationReportingDeleteAnnotationReport0Command:
    """Inputs required to pull label sets."""
    context: common_v1_context_pb2.RequestContext
    label_set_audit_etag: str
    label_set_children_children_manager_user_id: str
    label_set_manager_email: str
    reason: str


def to_annotation_reporting_delete_annotation_report0_command(
    command: AnnotationReportingDeleteAnnotationReport0Command
) -> labeling_v1_label_set_sync_service_pb2.PullLabelSetsRequest:
    return labeling_v1_label_set_sync_service_pb2.PullLabelSetsRequest(
        context=command.context,
        label_set=labeling_v1_labeling_pb2.LabelSet(
            audit=common_v1_audit_pb2.AuditInfo(etag=command.label_set_audit_etag),
            children=[
                labeling_v1_labeling_pb2.LabelSet(
                    children=[
                        labeling_v1_labeling_pb2.LabelSet(
                            manager=identity_v1_refs_pb2.UserRef(
                                user_id=command.label_set_children_children_manager_user_id
                            )
                        )
                    ]
                )
            ],
            manager=identity_v1_refs_pb2.UserRef(email=command.label_set_manager_email)
        ),
        reason=command.reason
    )


@dataclass(frozen=True, slots=True)
class AnnotationReportingDeleteAnnotationReport1Command(ValidatedModel):
    """Inputs required to summarize access policies."""
    context: common_v1_context_pb2.RequestContext
    reason: str
    annotations: dict[str, str]
    details_filters: dict[str, str]


def to_annotation_reporting_delete_annotation_report1_command(
    command: AnnotationReportingDeleteAnnotationReport1Command
) -> authorization_v1_access_policy_query_service_pb2.SummarizeAccessPoliciesRequest:
    return authorization_v1_access_policy_query_service_pb2.SummarizeAccessPoliciesRequest(
        annotations=command.annotations,
        context=command.context,
        details=authorization_v1_access_policy_query_service_pb2.SummarizeAccessPoliciesRequest.Details(
            filters=command.details_filters
        ),
        reason=command.reason
    )


@dataclass(frozen=True, slots=True)
class AnnotationValidationExplainAnnotationDecision1Command:
    """Inputs required to estimate labeling task."""
    context: common_v1_context_pb2.RequestContext
    labeling_task_requester_preferred_channel: str
    labeling_task_requester_email: str


def to_annotation_validation_explain_annotation_decision1_command(
    command: AnnotationValidationExplainAnnotationDecision1Command
) -> labeling_v1_labeling_task_calculation_service_pb2.EstimateLabelingTaskRequest:
    return labeling_v1_labeling_task_calculation_service_pb2.EstimateLabelingTaskRequest(
        context=command.context,
        labeling_task=labeling_v1_labeling_pb2.LabelingTask(
            requester=common_v1_contact_pb2.ContactInfo(
                email=command.labeling_task_requester_email,
                preferred_channel=command.labeling_task_requester_preferred_channel
            )
        )
    )


@dataclass(frozen=True, slots=True)
class AnnotationWorkflowAdvanceAnnotationWorkflow2Command:
    """Inputs required to preview label set."""
    context: common_v1_context_pb2.RequestContext
    label_set_children_children_audit_created_at: timestamp_pb2.Timestamp
    label_set_children_children_audit_created_by: str
    label_set_children_children_audit_updated_by: str


def to_annotation_workflow_advance_annotation_workflow2_command(
    command: AnnotationWorkflowAdvanceAnnotationWorkflow2Command
) -> labeling_v1_label_set_validation_service_pb2.PreviewLabelSetRequest:
    return labeling_v1_label_set_validation_service_pb2.PreviewLabelSetRequest(
        context=command.context,
        label_set=labeling_v1_labeling_pb2.LabelSet(
            children=[
                labeling_v1_labeling_pb2.LabelSet(
                    children=[
                        labeling_v1_labeling_pb2.LabelSet(
                            audit=common_v1_audit_pb2.AuditInfo(
                                created_at=command.label_set_children_children_audit_created_at,
                                created_by=command.label_set_children_children_audit_created_by,
                                updated_by=command.label_set_children_children_audit_updated_by
                            )
                        )
                    ]
                )
            ]
        )
    )


@dataclass(frozen=True, slots=True)
class AnnotationWorkflowAdvanceAnnotationWorkflow3Command(ValidatedModel):
    """Inputs required to recall annotation."""
    context: common_v1_context_pb2.RequestContext
    details_approver_email: str


def to_annotation_workflow_advance_annotation_workflow3_command(
    command: AnnotationWorkflowAdvanceAnnotationWorkflow3Command
) -> labeling_v1_annotation_approval_service_pb2.RecallAnnotationRequest:
    return labeling_v1_annotation_approval_service_pb2.RecallAnnotationRequest(
        context=command.context,
        details=labeling_v1_annotation_approval_service_pb2.RecallAnnotationRequest.Details(
            approver=identity_v1_refs_pb2.UserRef(email=command.details_approver_email)
        )
    )


@dataclass(frozen=True, slots=True)
class LabelSetApprovalRejectLabelSet1Command:
    """Inputs required to push feature value."""
    context: common_v1_context_pb2.RequestContext
    feature_value_subject_dataset_id: str
    feature_value_subject_display_name: str
    feature_value_kind: str


def to_label_set_approval_reject_label_set1_command(
    command: LabelSetApprovalRejectLabelSet1Command
) -> featurestore_v1_feature_value_sync_service_pb2.PushFeatureValueRequest:
    return featurestore_v1_feature_value_sync_service_pb2.PushFeatureValueRequest(
        context=command.context,
        feature_value=featurestore_v1_featurestore_pb2.FeatureValue(
            kind=command.feature_value_kind,
            subject=datasets_v1_refs_pb2.DatasetRef(
                dataset_id=command.feature_value_subject_dataset_id,
                display_name=command.feature_value_subject_display_name
            )
        )
    )


@dataclass(frozen=True, slots=True)
class LabelSetApprovalRejectLabelSet2Command(ValidatedModel):
    """Inputs required to recall registered model."""
    context: common_v1_context_pb2.RequestContext
    registered_model_audit_updated_by: str


def to_label_set_approval_reject_label_set2_command(
    command: LabelSetApprovalRejectLabelSet2Command
) -> modelregistry_v1_registered_model_approval_service_pb2.RecallRegisteredModelRequest:
    return modelregistry_v1_registered_model_approval_service_pb2.RecallRegisteredModelRequest(
        context=command.context,
        registered_model=modelregistry_v1_modelregistry_pb2.RegisteredModel(
            audit=common_v1_audit_pb2.AuditInfo(updated_by=command.registered_model_audit_updated_by)
        )
    )


@dataclass(frozen=True, slots=True)
class LabelSetLifecycleRenewLabelSet0Command:
    """Inputs required to update access policy."""
    context: common_v1_context_pb2.RequestContext
    access_policy_owner_email: str
    access_policy_owner_display_name: str
    access_policy_owner_user_id: str
    access_policy_block_reason: str


def to_label_set_lifecycle_renew_label_set0_command(
    command: LabelSetLifecycleRenewLabelSet0Command
) -> authorization_v1_access_policy_service_pb2.UpdateAccessPolicyRequest:
    return authorization_v1_access_policy_service_pb2.UpdateAccessPolicyRequest(
        access_policy=authorization_v1_authorization_pb2.AccessPolicy(
            block=authorization_v1_authorization_pb2.AccessPolicyBlockAction(reason=command.access_policy_block_reason),
            owner=identity_v1_refs_pb2.UserRef(
                display_name=command.access_policy_owner_display_name,
                email=command.access_policy_owner_email,
                user_id=command.access_policy_owner_user_id
            )
        ),
        context=command.context
    )


@dataclass(frozen=True, slots=True)
class LabelSetLifecycleScheduleLabelSetExpiry0Command(ValidatedModel):
    """Inputs required to explain customer calculation."""
    context: common_v1_context_pb2.RequestContext
    details_contact_name: common_v1_contact_pb2.PersonName
    customer_relationship_manager_display_name: str
    details_contact_preferred_channel: str


def to_label_set_lifecycle_schedule_label_set_expiry0_command(
    command: LabelSetLifecycleScheduleLabelSetExpiry0Command
) -> customers_v1_customer_calculation_service_pb2.ExplainCustomerCalculationRequest:
    return customers_v1_customer_calculation_service_pb2.ExplainCustomerCalculationRequest(
        context=command.context,
        customer=customers_v1_customers_pb2.Customer(
            relationship_manager=identity_v1_refs_pb2.UserRef(
                display_name=command.customer_relationship_manager_display_name
            )
        ),
        details=customers_v1_customer_calculation_service_pb2.ExplainCustomerCalculationRequest.Details(
            contact=common_v1_contact_pb2.ContactInfo(
                name=command.details_contact_name,
                preferred_channel=command.details_contact_preferred_channel
            )
        )
    )


@dataclass(frozen=True, slots=True)
class LabelSetReportingShareLabelSetReport0Command:
    """Inputs required to submit lineage node."""
    context: common_v1_context_pb2.RequestContext
    lineage_node_manager_email: str
    lineage_node_children_children_manager_email: str


def to_label_set_reporting_share_label_set_report0_command(
    command: LabelSetReportingShareLabelSetReport0Command
) -> lineage_v1_lineage_node_approval_service_pb2.SubmitLineageNodeRequest:
    return lineage_v1_lineage_node_approval_service_pb2.SubmitLineageNodeRequest(
        context=command.context,
        lineage_node=lineage_v1_lineage_pb2.LineageNode(
            children=[
                lineage_v1_lineage_pb2.LineageNode(
                    children=[
                        lineage_v1_lineage_pb2.LineageNode(
                            manager=identity_v1_refs_pb2.UserRef(
                                email=command.lineage_node_children_children_manager_email
                            )
                        )
                    ]
                )
            ],
            manager=identity_v1_refs_pb2.UserRef(email=command.lineage_node_manager_email)
        )
    )


@dataclass(frozen=True, slots=True)
class LabelSetValidationExplainLabelSetDecision1Command:
    """Inputs required to compare feature view options."""
    context: common_v1_context_pb2.RequestContext
    feature_view_audit_etag: str
    feature_view_address_postal_code: str
    details_destination_country_code: str
    details_destination_locality: str


def to_label_set_validation_explain_label_set_decision1_command(
    command: LabelSetValidationExplainLabelSetDecision1Command
) -> featurestore_v1_feature_view_calculation_service_pb2.CompareFeatureViewOptionsRequest:
    return featurestore_v1_feature_view_calculation_service_pb2.CompareFeatureViewOptionsRequest(
        context=command.context,
        details=featurestore_v1_feature_view_calculation_service_pb2.CompareFeatureViewOptionsRequest.Details(
            destination=common_v1_address_pb2.PostalAddress(
                country_code=command.details_destination_country_code,
                locality=command.details_destination_locality
            )
        ),
        feature_view=featurestore_v1_featurestore_pb2.FeatureView(
            address=common_v1_address_pb2.PostalAddress(postal_code=command.feature_view_address_postal_code),
            audit=common_v1_audit_pb2.AuditInfo(etag=command.feature_view_audit_etag)
        )
    )


@dataclass(frozen=True, slots=True)
class LabelingTaskApprovalApproveLabelingTask2Command:
    """Inputs required to simulate label set."""
    context: common_v1_context_pb2.RequestContext
    label_set_children_children_audit_updated_by: str
    label_set_children_children_manager_display_name: str
    label_set_children_children_manager_email: str
    label_set_children_manager_display_name: str


def to_labeling_task_approval_approve_labeling_task2_command(
    command: LabelingTaskApprovalApproveLabelingTask2Command
) -> labeling_v1_label_set_calculation_service_pb2.SimulateLabelSetRequest:
    return labeling_v1_label_set_calculation_service_pb2.SimulateLabelSetRequest(
        context=command.context,
        label_set=labeling_v1_labeling_pb2.LabelSet(
            children=[
                labeling_v1_labeling_pb2.LabelSet(
                    children=[
                        labeling_v1_labeling_pb2.LabelSet(
                            audit=common_v1_audit_pb2.AuditInfo(
                                updated_by=command.label_set_children_children_audit_updated_by
                            ),
                            manager=identity_v1_refs_pb2.UserRef(
                                display_name=command.label_set_children_children_manager_display_name,
                                email=command.label_set_children_children_manager_email
                            )
                        )
                    ],
                    manager=identity_v1_refs_pb2.UserRef(display_name=command.label_set_children_manager_display_name)
                )
            ]
        )
    )


@dataclass(frozen=True, slots=True)
class LabelingTaskApprovalCommentLabelingTaskApproval0Command(ValidatedModel):
    """Inputs required to pause model version workflow."""
    context: common_v1_context_pb2.RequestContext
    details_notify_email: str


def to_labeling_task_approval_comment_labeling_task_approval0_command(
    command: LabelingTaskApprovalCommentLabelingTaskApproval0Command
) -> modelregistry_v1_model_version_workflow_service_pb2.PauseModelVersionWorkflowRequest:
    return modelregistry_v1_model_version_workflow_service_pb2.PauseModelVersionWorkflowRequest(
        context=command.context,
        details=modelregistry_v1_model_version_workflow_service_pb2.PauseModelVersionWorkflowRequest.Details(
            notify=common_v1_contact_pb2.ContactInfo(email=command.details_notify_email)
        )
    )


@dataclass(frozen=True, slots=True)
class LabelingTaskLifecycleReinstateLabelingTask0Command:
    """Inputs required to unsubscribe dashboard updates."""
    context: common_v1_context_pb2.RequestContext
    details_recipient_phone: str
    details_recipient_name: common_v1_contact_pb2.PersonName


def to_labeling_task_lifecycle_reinstate_labeling_task0_command(
    command: LabelingTaskLifecycleReinstateLabelingTask0Command
) -> metrics_v1_dashboard_notification_service_pb2.UnsubscribeDashboardUpdatesRequest:
    return metrics_v1_dashboard_notification_service_pb2.UnsubscribeDashboardUpdatesRequest(
        context=command.context,
        details=metrics_v1_dashboard_notification_service_pb2.UnsubscribeDashboardUpdatesRequest.Details(
            recipient=common_v1_contact_pb2.ContactInfo(
                name=command.details_recipient_name,
                phone=command.details_recipient_phone
            )
        )
    )


@dataclass(frozen=True, slots=True)
class LabelingTaskLifecycleReinstateLabelingTask1Command(ValidatedModel):
    """Inputs required to schedule dashboard export."""
    context: common_v1_context_pb2.RequestContext
    dashboard_id: str
    annotations: dict[str, str]
    reason: str
    details_filters: dict[str, str]


def to_labeling_task_lifecycle_reinstate_labeling_task1_command(
    command: LabelingTaskLifecycleReinstateLabelingTask1Command
) -> metrics_v1_dashboard_export_service_pb2.ScheduleDashboardExportRequest:
    return metrics_v1_dashboard_export_service_pb2.ScheduleDashboardExportRequest(
        annotations=command.annotations,
        context=command.context,
        dashboard_id=command.dashboard_id,
        details=metrics_v1_dashboard_export_service_pb2.ScheduleDashboardExportRequest.Details(
            filters=command.details_filters
        ),
        reason=command.reason
    )


@dataclass(frozen=True, slots=True)
class LabelingTaskUpdateLabelingTask0Command:
    """Inputs required to recalculate label sets."""
    context: common_v1_context_pb2.RequestContext
    label_set_children_children_audit_created_by: str
    label_set_children_children_audit_updated_at: timestamp_pb2.Timestamp
    label_set_children_children_audit_etag: str


def to_labeling_task_update_labeling_task0_command(
    command: LabelingTaskUpdateLabelingTask0Command
) -> labeling_v1_label_set_calculation_service_pb2.RecalculateLabelSetsRequest:
    return labeling_v1_label_set_calculation_service_pb2.RecalculateLabelSetsRequest(
        context=command.context,
        label_set=labeling_v1_labeling_pb2.LabelSet(
            children=[
                labeling_v1_labeling_pb2.LabelSet(
                    children=[
                        labeling_v1_labeling_pb2.LabelSet(
                            audit=common_v1_audit_pb2.AuditInfo(
                                created_by=command.label_set_children_children_audit_created_by,
                                etag=command.label_set_children_children_audit_etag,
                                updated_at=command.label_set_children_children_audit_updated_at
                            )
                        )
                    ]
                )
            ]
        )
    )


@dataclass(frozen=True, slots=True)
class LabelingTaskWorkflowCancelLabelingTaskWorkflow0Command(ValidatedModel):
    """Inputs required to recall labeling task."""
    context: common_v1_context_pb2.RequestContext
    labeling_task_sla_breached: bool


def to_labeling_task_workflow_cancel_labeling_task_workflow0_command(
    command: LabelingTaskWorkflowCancelLabelingTaskWorkflow0Command
) -> labeling_v1_labeling_task_approval_service_pb2.RecallLabelingTaskRequest:
    return labeling_v1_labeling_task_approval_service_pb2.RecallLabelingTaskRequest(
        context=command.context,
        labeling_task=labeling_v1_labeling_pb2.LabelingTask(
            sla=labeling_v1_labeling_pb2.LabelingTaskSla(breached=command.labeling_task_sla_breached)
        )
    )


@dataclass(frozen=True, slots=True)
class LabelingTaskWorkflowSignalLabelingTaskWorkflow2Command:
    """Inputs required to terminate labeling task."""
    context: common_v1_context_pb2.RequestContext
    labeling_task_id: str
    details_notify_contact_phone: str
    details_new_owner_email: str
    details_notify_contact_email: str
    details_notify_contact_name: common_v1_contact_pb2.PersonName


def to_labeling_task_workflow_signal_labeling_task_workflow2_command(
    command: LabelingTaskWorkflowSignalLabelingTaskWorkflow2Command
) -> labeling_v1_labeling_task_lifecycle_service_pb2.TerminateLabelingTaskRequest:
    return labeling_v1_labeling_task_lifecycle_service_pb2.TerminateLabelingTaskRequest(
        context=command.context,
        details=labeling_v1_labeling_task_lifecycle_service_pb2.TerminateLabelingTaskRequest.Details(
            new_owner=identity_v1_refs_pb2.UserRef(email=command.details_new_owner_email),
            notify_contact=common_v1_contact_pb2.ContactInfo(
                email=command.details_notify_contact_email,
                name=command.details_notify_contact_name,
                phone=command.details_notify_contact_phone
            )
        ),
        labeling_task_id=command.labeling_task_id
    )
