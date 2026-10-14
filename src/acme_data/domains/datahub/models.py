"""Typed commands crossing the datahub application boundary."""

from __future__ import annotations

from dataclasses import dataclass

from google.protobuf import timestamp_pb2 as timestamp_pb2

from acme.anomalies.v1 import (
    anomaly_feedback_approval_service_pb2 as anomalies_v1_anomaly_feedback_approval_service_pb2,
)
from acme.authorization.v1 import (
    access_policy_validation_service_pb2 as authorization_v1_access_policy_validation_service_pb2,
)
from acme.authorization.v1 import authorization_pb2 as authorization_v1_authorization_pb2
from acme.billing.v1 import billing_account_query_service_pb2 as billing_v1_billing_account_query_service_pb2
from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.common.v1 import context_pb2 as common_v1_context_pb2
from acme.customers.v1 import consent_record_sync_service_pb2 as customers_v1_consent_record_sync_service_pb2
from acme.customers.v1 import customers_pb2 as customers_v1_customers_pb2
from acme.customers.v1 import preference_calculation_service_pb2 as customers_v1_preference_calculation_service_pb2
from acme.customers.v1 import preference_sync_service_pb2 as customers_v1_preference_sync_service_pb2
from acme.customers.v1 import refs_pb2 as customers_v1_refs_pb2
from acme.datahub.v1 import data_share_approval_service_pb2 as datahub_v1_data_share_approval_service_pb2
from acme.datahub.v1 import data_share_reporting_service_pb2 as datahub_v1_data_share_reporting_service_pb2
from acme.datahub.v1 import datahub_pb2 as datahub_v1_datahub_pb2
from acme.datahub.v1 import notebook_approval_service_pb2 as datahub_v1_notebook_approval_service_pb2
from acme.datahub.v1 import notebook_workflow_service_pb2 as datahub_v1_notebook_workflow_service_pb2
from acme.datahub.v1 import workspace_approval_service_pb2 as datahub_v1_workspace_approval_service_pb2
from acme.datasets.v1 import dataset_approval_service_pb2 as datasets_v1_dataset_approval_service_pb2
from acme.datasets.v1 import datasets_pb2 as datasets_v1_datasets_pb2
from acme.documents.v1 import document_service_pb2 as documents_v1_document_service_pb2
from acme.featureflags.v1 import (
    feature_flag_validation_service_pb2 as featureflags_v1_feature_flag_validation_service_pb2,
)
from acme.featureflags.v1 import featureflags_pb2 as featureflags_v1_featureflags_pb2
from acme.featurestore.v1 import entity_import_service_pb2 as featurestore_v1_entity_import_service_pb2
from acme.featurestore.v1 import featurestore_pb2 as featurestore_v1_featurestore_pb2
from acme.forecasting.v1 import (
    demand_forecast_workflow_service_pb2 as forecasting_v1_demand_forecast_workflow_service_pb2,
)
from acme.forecasting.v1 import forecasting_pb2 as forecasting_v1_forecasting_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.identity.v1 import user_query_service_pb2 as identity_v1_user_query_service_pb2
from acme.labeling.v1 import label_set_approval_service_pb2 as labeling_v1_label_set_approval_service_pb2
from acme.labeling.v1 import labeling_pb2 as labeling_v1_labeling_pb2
from acme.metrics.v1 import dashboard_sync_service_pb2 as metrics_v1_dashboard_sync_service_pb2
from acme.metrics.v1 import metric_series_history_service_pb2 as metrics_v1_metric_series_history_service_pb2
from acme.metrics.v1 import metric_series_validation_service_pb2 as metrics_v1_metric_series_validation_service_pb2
from acme.metrics.v1 import metrics_pb2 as metrics_v1_metrics_pb2
from acme.metrics.v1 import refs_pb2 as metrics_v1_refs_pb2
from acme.pipelines.v1 import pipeline_run_workflow_service_pb2 as pipelines_v1_pipeline_run_workflow_service_pb2
from acme.pipelines.v1 import pipelines_pb2 as pipelines_v1_pipelines_pb2

from acme_data.platform.models import ValidatedModel


@dataclass(frozen=True, slots=True)
class DataShareApprovalRejectDataShare0Command:
    """Inputs required to annotate metric series version."""
    context: common_v1_context_pb2.RequestContext
    metric_series_owner_email: str


def to_data_share_approval_reject_data_share0_command(
    command: DataShareApprovalRejectDataShare0Command
) -> metrics_v1_metric_series_history_service_pb2.AnnotateMetricSeriesVersionRequest:
    return metrics_v1_metric_series_history_service_pb2.AnnotateMetricSeriesVersionRequest(
        context=command.context,
        metric_series=metrics_v1_metrics_pb2.MetricSeries(
            owner=identity_v1_refs_pb2.UserRef(email=command.metric_series_owner_email)
        )
    )


@dataclass(frozen=True, slots=True)
class DataShareApprovalRejectDataShare1Command(ValidatedModel):
    """Inputs required to recall dataset."""
    context: common_v1_context_pb2.RequestContext
    dataset_owner_display_name: str
    dataset_address_recipient: str


def to_data_share_approval_reject_data_share1_command(
    command: DataShareApprovalRejectDataShare1Command
) -> datasets_v1_dataset_approval_service_pb2.RecallDatasetRequest:
    return datasets_v1_dataset_approval_service_pb2.RecallDatasetRequest(
        context=command.context,
        dataset=datasets_v1_datasets_pb2.Dataset(
            address=common_v1_address_pb2.PostalAddress(recipient=command.dataset_address_recipient),
            owner=identity_v1_refs_pb2.UserRef(display_name=command.dataset_owner_display_name)
        )
    )


@dataclass(frozen=True, slots=True)
class DataShareIntegrationIngestDataShareEvents1Command(ValidatedModel):
    """Inputs required to score access policy."""
    context: common_v1_context_pb2.RequestContext
    access_policy_audit_updated_by: str
    access_policy_audit_updated_at: timestamp_pb2.Timestamp
    details_destination_recipient: str


def to_data_share_integration_ingest_data_share_events1_command(
    command: DataShareIntegrationIngestDataShareEvents1Command
) -> authorization_v1_access_policy_validation_service_pb2.ScoreAccessPolicyRequest:
    return authorization_v1_access_policy_validation_service_pb2.ScoreAccessPolicyRequest(
        access_policy=authorization_v1_authorization_pb2.AccessPolicy(
            audit=common_v1_audit_pb2.AuditInfo(
                updated_at=command.access_policy_audit_updated_at,
                updated_by=command.access_policy_audit_updated_by
            )
        ),
        context=command.context,
        details=authorization_v1_access_policy_validation_service_pb2.ScoreAccessPolicyRequest.Details(
            destination=common_v1_address_pb2.PostalAddress(recipient=command.details_destination_recipient)
        )
    )


@dataclass(frozen=True, slots=True)
class DataShareNotificationSubscribeDataShareUpdates2Command(ValidatedModel):
    """Inputs required to signal pipeline run workflow."""
    context: common_v1_context_pb2.RequestContext
    pipeline_run_assignee_email: str


def to_data_share_notification_subscribe_data_share_updates2_command(
    command: DataShareNotificationSubscribeDataShareUpdates2Command
) -> pipelines_v1_pipeline_run_workflow_service_pb2.SignalPipelineRunWorkflowRequest:
    return pipelines_v1_pipeline_run_workflow_service_pb2.SignalPipelineRunWorkflowRequest(
        context=command.context,
        pipeline_run=pipelines_v1_pipelines_pb2.PipelineRun(
            assignee=identity_v1_refs_pb2.UserRef(email=command.pipeline_run_assignee_email)
        )
    )


@dataclass(frozen=True, slots=True)
class DataShareQuerySummarizeDataShares0Command:
    """Inputs required to recall anomaly feedback."""
    context: common_v1_context_pb2.RequestContext
    reason: str


def to_data_share_query_summarize_data_shares0_command(
    command: DataShareQuerySummarizeDataShares0Command
) -> anomalies_v1_anomaly_feedback_approval_service_pb2.RecallAnomalyFeedbackRequest:
    return anomalies_v1_anomaly_feedback_approval_service_pb2.RecallAnomalyFeedbackRequest(
        context=command.context,
        reason=command.reason
    )


@dataclass(frozen=True, slots=True)
class DataShareQuerySummarizeDataShares1Command(ValidatedModel):
    """Inputs required to reconcile preferences."""
    context: common_v1_context_pb2.RequestContext
    preference_owner_display_name: str
    preference_block_reason: str
    annotations: dict[str, str]
    preference_block_notify_email: str


def to_data_share_query_summarize_data_shares1_command(
    command: DataShareQuerySummarizeDataShares1Command
) -> customers_v1_preference_sync_service_pb2.ReconcilePreferencesRequest:
    return customers_v1_preference_sync_service_pb2.ReconcilePreferencesRequest(
        annotations=command.annotations,
        context=command.context,
        preference=customers_v1_customers_pb2.Preference(
            block=customers_v1_customers_pb2.PreferenceBlockAction(
                notify_email=command.preference_block_notify_email,
                reason=command.preference_block_reason
            ),
            owner=identity_v1_refs_pb2.UserRef(display_name=command.preference_owner_display_name)
        )
    )


@dataclass(frozen=True, slots=True)
class DataShareReportingStreamDataShareMetrics2Command(ValidatedModel):
    """Inputs required to delegate data share approval."""
    context: common_v1_context_pb2.RequestContext
    details_approver_email: str
    data_share_billing_address_region: str
    details_approver_user_id: str
    details_approver_email_value: str


def to_data_share_reporting_stream_data_share_metrics2_command(
    command: DataShareReportingStreamDataShareMetrics2Command
) -> datahub_v1_data_share_approval_service_pb2.DelegateDataShareApprovalRequest:
    return datahub_v1_data_share_approval_service_pb2.DelegateDataShareApprovalRequest(
        context=command.context,
        data_share=datahub_v1_datahub_pb2.DataShare(
            billing_address=common_v1_address_pb2.PostalAddress(region=command.data_share_billing_address_region)
        ),
        details=datahub_v1_data_share_approval_service_pb2.DelegateDataShareApprovalRequest.Details(
            approver=identity_v1_refs_pb2.UserRef(
                email=command.details_approver_email,
                user_id=command.details_approver_user_id
            ),
            approver_email=command.details_approver_email_value
        )
    )


@dataclass(frozen=True, slots=True)
class DataShareValidationPreviewDataShare2Command:
    """Inputs required to check feature flag eligibility."""
    context: common_v1_context_pb2.RequestContext
    feature_flag_audit_etag: str


def to_data_share_validation_preview_data_share2_command(
    command: DataShareValidationPreviewDataShare2Command
) -> featureflags_v1_feature_flag_validation_service_pb2.CheckFeatureFlagEligibilityRequest:
    return featureflags_v1_feature_flag_validation_service_pb2.CheckFeatureFlagEligibilityRequest(
        context=command.context,
        feature_flag=featureflags_v1_featureflags_pb2.FeatureFlag(
            audit=common_v1_audit_pb2.AuditInfo(etag=command.feature_flag_audit_etag)
        )
    )


@dataclass(frozen=True, slots=True)
class DataShareValidationScoreDataShare0Command(ValidatedModel):
    """Inputs required to approve workspace."""
    context: common_v1_context_pb2.RequestContext
    workspace_customer_display_name: str


def to_data_share_validation_score_data_share0_command(
    command: DataShareValidationScoreDataShare0Command
) -> datahub_v1_workspace_approval_service_pb2.ApproveWorkspaceRequest:
    return datahub_v1_workspace_approval_service_pb2.ApproveWorkspaceRequest(
        context=command.context,
        workspace=datahub_v1_datahub_pb2.Workspace(
            customer=customers_v1_refs_pb2.CustomerRef(display_name=command.workspace_customer_display_name)
        )
    )


@dataclass(frozen=True, slots=True)
class DataShareWorkflowResumeDataShareWorkflow1Command:
    """Inputs required to recall workspace."""
    context: common_v1_context_pb2.RequestContext
    workspace_requester_preferred_channel: str
    workspace_assignee_display_name: str
    workspace_audit_etag: str


def to_data_share_workflow_resume_data_share_workflow1_command(
    command: DataShareWorkflowResumeDataShareWorkflow1Command
) -> datahub_v1_workspace_approval_service_pb2.RecallWorkspaceRequest:
    return datahub_v1_workspace_approval_service_pb2.RecallWorkspaceRequest(
        context=command.context,
        workspace=datahub_v1_datahub_pb2.Workspace(
            assignee=identity_v1_refs_pb2.UserRef(display_name=command.workspace_assignee_display_name),
            audit=common_v1_audit_pb2.AuditInfo(etag=command.workspace_audit_etag),
            requester=common_v1_contact_pb2.ContactInfo(preferred_channel=command.workspace_requester_preferred_channel)
        )
    )


@dataclass(frozen=True, slots=True)
class NotebookApprovalDelegateNotebookApproval1Command(ValidatedModel):
    """Inputs required to validate entity import."""
    context: common_v1_context_pb2.RequestContext
    entity_audit_created_at: timestamp_pb2.Timestamp
    entity_primary_address_postal_code: str
    entity_audit_created_by: str


def to_notebook_approval_delegate_notebook_approval1_command(
    command: NotebookApprovalDelegateNotebookApproval1Command
) -> featurestore_v1_entity_import_service_pb2.ValidateEntityImportRequest:
    return featurestore_v1_entity_import_service_pb2.ValidateEntityImportRequest(
        context=command.context,
        entity=featurestore_v1_featurestore_pb2.Entity(
            audit=common_v1_audit_pb2.AuditInfo(
                created_at=command.entity_audit_created_at,
                created_by=command.entity_audit_created_by
            ),
            primary_address=common_v1_address_pb2.PostalAddress(postal_code=command.entity_primary_address_postal_code)
        )
    )


@dataclass(frozen=True, slots=True)
class NotebookIntegrationAcknowledgeNotebookEvent1Command:
    """Inputs required to check metric series eligibility."""
    context: common_v1_context_pb2.RequestContext
    metric_series_owner_email: str


def to_notebook_integration_acknowledge_notebook_event1_command(
    command: NotebookIntegrationAcknowledgeNotebookEvent1Command
) -> metrics_v1_metric_series_validation_service_pb2.CheckMetricSeriesEligibilityRequest:
    return metrics_v1_metric_series_validation_service_pb2.CheckMetricSeriesEligibilityRequest(
        context=command.context,
        metric_series=metrics_v1_metrics_pb2.MetricSeries(
            owner=identity_v1_refs_pb2.UserRef(email=command.metric_series_owner_email)
        )
    )


@dataclass(frozen=True, slots=True)
class NotebookIntegrationAcknowledgeNotebookEvent2Command(ValidatedModel):
    """Inputs required to generate data share report."""
    context: common_v1_context_pb2.RequestContext
    annotations: dict[str, str]
    reason: str
    details_filters: dict[str, str]


def to_notebook_integration_acknowledge_notebook_event2_command(
    command: NotebookIntegrationAcknowledgeNotebookEvent2Command
) -> datahub_v1_data_share_reporting_service_pb2.GenerateDataShareReportRequest:
    return datahub_v1_data_share_reporting_service_pb2.GenerateDataShareReportRequest(
        annotations=command.annotations,
        context=command.context,
        details=datahub_v1_data_share_reporting_service_pb2.GenerateDataShareReportRequest.Details(
            filters=command.details_filters
        ),
        reason=command.reason
    )


@dataclass(frozen=True, slots=True)
class NotebookNotificationNotifyNotebookWatchers0Command(ValidatedModel):
    """Inputs required to signal notebook workflow."""
    context: common_v1_context_pb2.RequestContext
    details_notify_name: common_v1_contact_pb2.PersonName
    details_notify_email: str
    details_notify_phone: str
    notebook_notebook_id: str


def to_notebook_notification_notify_notebook_watchers0_command(
    command: NotebookNotificationNotifyNotebookWatchers0Command
) -> datahub_v1_notebook_workflow_service_pb2.SignalNotebookWorkflowRequest:
    return datahub_v1_notebook_workflow_service_pb2.SignalNotebookWorkflowRequest(
        context=command.context,
        details=datahub_v1_notebook_workflow_service_pb2.SignalNotebookWorkflowRequest.Details(
            notify=common_v1_contact_pb2.ContactInfo(
                email=command.details_notify_email,
                name=command.details_notify_name,
                phone=command.details_notify_phone
            )
        ),
        notebook=datahub_v1_datahub_pb2.Notebook(notebook_id=command.notebook_notebook_id)
    )


@dataclass(frozen=True, slots=True)
class NotebookQueryExportNotebooks2Command(ValidatedModel):
    """Inputs required to push preference."""
    context: common_v1_context_pb2.RequestContext
    preference_audit_updated_by: str
    preference_audit_created_at: timestamp_pb2.Timestamp
    preference_description: str


def to_notebook_query_export_notebooks2_command(
    command: NotebookQueryExportNotebooks2Command
) -> customers_v1_preference_sync_service_pb2.PushPreferenceRequest:
    return customers_v1_preference_sync_service_pb2.PushPreferenceRequest(
        context=command.context,
        preference=customers_v1_customers_pb2.Preference(
            audit=common_v1_audit_pb2.AuditInfo(
                created_at=command.preference_audit_created_at,
                updated_by=command.preference_audit_updated_by
            ),
            description=command.preference_description
        )
    )


@dataclass(frozen=True, slots=True)
class NotebookReportingScheduleNotebookReport1Command:
    """Inputs required to approve notebook."""
    context: common_v1_context_pb2.RequestContext
    annotations: dict[str, str]
    reason: str
    notebook_notebook_id: str
    details_approver_email: str


def to_notebook_reporting_schedule_notebook_report1_command(
    command: NotebookReportingScheduleNotebookReport1Command
) -> datahub_v1_notebook_approval_service_pb2.ApproveNotebookRequest:
    return datahub_v1_notebook_approval_service_pb2.ApproveNotebookRequest(
        annotations=command.annotations,
        context=command.context,
        details=datahub_v1_notebook_approval_service_pb2.ApproveNotebookRequest.Details(
            approver=identity_v1_refs_pb2.UserRef(email=command.details_approver_email)
        ),
        notebook=datahub_v1_datahub_pb2.Notebook(notebook_id=command.notebook_notebook_id),
        reason=command.reason
    )


@dataclass(frozen=True, slots=True)
class NotebookDeleteNotebook1Command:
    """Inputs required to reject label set."""
    context: common_v1_context_pb2.RequestContext
    label_set_children_children_audit_etag: str


def to_notebook_delete_notebook1_command(
    command: NotebookDeleteNotebook1Command
) -> labeling_v1_label_set_approval_service_pb2.RejectLabelSetRequest:
    return labeling_v1_label_set_approval_service_pb2.RejectLabelSetRequest(
        context=command.context,
        label_set=labeling_v1_labeling_pb2.LabelSet(
            children=[
                labeling_v1_labeling_pb2.LabelSet(
                    children=[
                        labeling_v1_labeling_pb2.LabelSet(
                            audit=common_v1_audit_pb2.AuditInfo(etag=command.label_set_children_children_audit_etag)
                        )
                    ]
                )
            ]
        )
    )


@dataclass(frozen=True, slots=True)
class NotebookDeleteNotebook2Command(ValidatedModel):
    """Inputs required to cancel demand forecast workflow."""
    context: common_v1_context_pb2.RequestContext
    demand_forecast_billing_address_lines: list[str]
    demand_forecast_billing_address_recipient: str
    demand_forecast_audit_created_at: timestamp_pb2.Timestamp


def to_notebook_delete_notebook2_command(
    command: NotebookDeleteNotebook2Command
) -> forecasting_v1_demand_forecast_workflow_service_pb2.CancelDemandForecastWorkflowRequest:
    return forecasting_v1_demand_forecast_workflow_service_pb2.CancelDemandForecastWorkflowRequest(
        context=command.context,
        demand_forecast=forecasting_v1_forecasting_pb2.DemandForecast(
            audit=common_v1_audit_pb2.AuditInfo(created_at=command.demand_forecast_audit_created_at),
            billing_address=common_v1_address_pb2.PostalAddress(
                lines=command.demand_forecast_billing_address_lines,
                recipient=command.demand_forecast_billing_address_recipient
            )
        )
    )


@dataclass(frozen=True, slots=True)
class NotebookWorkflowPauseNotebookWorkflow0Command:
    """Inputs required to count users."""
    context: common_v1_context_pb2.RequestContext
    filter_region: str
    filter_created_after: timestamp_pb2.Timestamp


def to_notebook_workflow_pause_notebook_workflow0_command(
    command: NotebookWorkflowPauseNotebookWorkflow0Command
) -> identity_v1_user_query_service_pb2.CountUsersRequest:
    return identity_v1_user_query_service_pb2.CountUsersRequest(
        context=command.context,
        filter=identity_v1_user_query_service_pb2.CountUsersRequest.Filter(
            created_after=command.filter_created_after,
            region=command.filter_region
        )
    )


@dataclass(frozen=True, slots=True)
class NotebookWorkflowPauseNotebookWorkflow1Command(ValidatedModel):
    """Inputs required to resolve billing accounts."""
    context: common_v1_context_pb2.RequestContext


def to_notebook_workflow_pause_notebook_workflow1_command(
    command: NotebookWorkflowPauseNotebookWorkflow1Command
) -> billing_v1_billing_account_query_service_pb2.ResolveBillingAccountsRequest:
    return billing_v1_billing_account_query_service_pb2.ResolveBillingAccountsRequest(context=command.context)


@dataclass(frozen=True, slots=True)
class NotebookWorkflowStartNotebookWorkflow2Command:
    """Inputs required to batch get documents."""
    context: common_v1_context_pb2.RequestContext


def to_notebook_workflow_start_notebook_workflow2_command(
    command: NotebookWorkflowStartNotebookWorkflow2Command
) -> documents_v1_document_service_pb2.BatchGetDocumentsRequest:
    return documents_v1_document_service_pb2.BatchGetDocumentsRequest(context=command.context)


@dataclass(frozen=True, slots=True)
class WorkspaceApprovalSubmitWorkspace2Command(ValidatedModel):
    """Inputs required to estimate preference."""
    context: common_v1_context_pb2.RequestContext
    preference_owner_display_name: str
    preference_audit_updated_at: timestamp_pb2.Timestamp
    preference_audit_created_by: str
    preference_audit_updated_by: str


def to_workspace_approval_submit_workspace2_command(
    command: WorkspaceApprovalSubmitWorkspace2Command
) -> customers_v1_preference_calculation_service_pb2.EstimatePreferenceRequest:
    return customers_v1_preference_calculation_service_pb2.EstimatePreferenceRequest(
        context=command.context,
        preference=customers_v1_customers_pb2.Preference(
            audit=common_v1_audit_pb2.AuditInfo(
                created_by=command.preference_audit_created_by,
                updated_at=command.preference_audit_updated_at,
                updated_by=command.preference_audit_updated_by
            ),
            owner=identity_v1_refs_pb2.UserRef(display_name=command.preference_owner_display_name)
        )
    )


@dataclass(frozen=True, slots=True)
class WorkspaceIntegrationRelayWorkspaceMessages0Command:
    """Inputs required to start notebook workflow."""
    context: common_v1_context_pb2.RequestContext
    notebook_audit_etag: str
    notebook_audit_created_by: str
    details_notify_name: common_v1_contact_pb2.PersonName


def to_workspace_integration_relay_workspace_messages0_command(
    command: WorkspaceIntegrationRelayWorkspaceMessages0Command
) -> datahub_v1_notebook_workflow_service_pb2.StartNotebookWorkflowRequest:
    return datahub_v1_notebook_workflow_service_pb2.StartNotebookWorkflowRequest(
        context=command.context,
        details=datahub_v1_notebook_workflow_service_pb2.StartNotebookWorkflowRequest.Details(
            notify=common_v1_contact_pb2.ContactInfo(name=command.details_notify_name)
        ),
        notebook=datahub_v1_datahub_pb2.Notebook(
            audit=common_v1_audit_pb2.AuditInfo(
                created_by=command.notebook_audit_created_by,
                etag=command.notebook_audit_etag
            )
        )
    )


@dataclass(frozen=True, slots=True)
class WorkspaceNotificationStreamWorkspaceNotices1Command:
    """Inputs required to pull dashboards."""
    context: common_v1_context_pb2.RequestContext
    dashboard_audit_etag: str
    dashboard_audit_created_by: str
    dashboard_card_network: str
    dashboard_counterparty_display_name: str


def to_workspace_notification_stream_workspace_notices1_command(
    command: WorkspaceNotificationStreamWorkspaceNotices1Command
) -> metrics_v1_dashboard_sync_service_pb2.PullDashboardsRequest:
    return metrics_v1_dashboard_sync_service_pb2.PullDashboardsRequest(
        context=command.context,
        dashboard=metrics_v1_metrics_pb2.Dashboard(
            audit=common_v1_audit_pb2.AuditInfo(
                created_by=command.dashboard_audit_created_by,
                etag=command.dashboard_audit_etag
            ),
            card=metrics_v1_metrics_pb2.DashboardCardSettlement(network=command.dashboard_card_network),
            counterparty=metrics_v1_refs_pb2.MetricAlertRef(display_name=command.dashboard_counterparty_display_name)
        )
    )


@dataclass(frozen=True, slots=True)
class WorkspaceNotificationStreamWorkspaceNotices2Command(ValidatedModel):
    """Inputs required to score metric series."""
    context: common_v1_context_pb2.RequestContext
    metric_series_audit_etag: str


def to_workspace_notification_stream_workspace_notices2_command(
    command: WorkspaceNotificationStreamWorkspaceNotices2Command
) -> metrics_v1_metric_series_validation_service_pb2.ScoreMetricSeriesRequest:
    return metrics_v1_metric_series_validation_service_pb2.ScoreMetricSeriesRequest(
        context=command.context,
        metric_series=metrics_v1_metrics_pb2.MetricSeries(
            audit=common_v1_audit_pb2.AuditInfo(etag=command.metric_series_audit_etag)
        )
    )


@dataclass(frozen=True, slots=True)
class WorkspaceQuerySummarizeWorkspaces0Command:
    """Inputs required to list pending data shares."""
    context: common_v1_context_pb2.RequestContext
    filter_labels: dict[str, str]
    filter_owner_id: str


def to_workspace_query_summarize_workspaces0_command(
    command: WorkspaceQuerySummarizeWorkspaces0Command
) -> datahub_v1_data_share_approval_service_pb2.ListPendingDataSharesRequest:
    return datahub_v1_data_share_approval_service_pb2.ListPendingDataSharesRequest(
        context=command.context,
        filter=datahub_v1_data_share_approval_service_pb2.ListPendingDataSharesRequest.Filter(
            labels=command.filter_labels,
            owner_id=command.filter_owner_id
        )
    )


@dataclass(frozen=True, slots=True)
class WorkspaceQuerySummarizeWorkspaces1Command(ValidatedModel):
    """Inputs required to push consent record."""
    context: common_v1_context_pb2.RequestContext
    consent_record_correlation_id: str
    reason: str


def to_workspace_query_summarize_workspaces1_command(
    command: WorkspaceQuerySummarizeWorkspaces1Command
) -> customers_v1_consent_record_sync_service_pb2.PushConsentRecordRequest:
    return customers_v1_consent_record_sync_service_pb2.PushConsentRecordRequest(
        consent_record=customers_v1_customers_pb2.ConsentRecord(correlation_id=command.consent_record_correlation_id),
        context=command.context,
        reason=command.reason
    )


@dataclass(frozen=True, slots=True)
class WorkspaceReportingStreamWorkspaceMetrics2Command(ValidatedModel):
    """Inputs required to approve workspace."""
    context: common_v1_context_pb2.RequestContext
    workspace_sla_policy_id: str


def to_workspace_reporting_stream_workspace_metrics2_command(
    command: WorkspaceReportingStreamWorkspaceMetrics2Command
) -> datahub_v1_workspace_approval_service_pb2.ApproveWorkspaceRequest:
    return datahub_v1_workspace_approval_service_pb2.ApproveWorkspaceRequest(
        context=command.context,
        workspace=datahub_v1_datahub_pb2.Workspace(
            sla=datahub_v1_datahub_pb2.WorkspaceSla(policy_id=command.workspace_sla_policy_id)
        )
    )
