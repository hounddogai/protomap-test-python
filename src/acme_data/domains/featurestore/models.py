"""Typed commands crossing the featurestore application boundary."""

from __future__ import annotations

from dataclasses import dataclass

from google.protobuf import timestamp_pb2 as timestamp_pb2

from acme.anomalies.v1 import anomalies_pb2 as anomalies_v1_anomalies_pb2
from acme.anomalies.v1 import (
    anomaly_feedback_approval_service_pb2 as anomalies_v1_anomaly_feedback_approval_service_pb2,
)
from acme.anomalies.v1 import (
    anomaly_feedback_workflow_service_pb2 as anomalies_v1_anomaly_feedback_workflow_service_pb2,
)
from acme.anomalies.v1 import detector_approval_service_pb2 as anomalies_v1_detector_approval_service_pb2
from acme.anomalies.v1 import detector_query_service_pb2 as anomalies_v1_detector_query_service_pb2
from acme.catalog.v1 import product_query_service_pb2 as catalog_v1_product_query_service_pb2
from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.common.v1 import context_pb2 as common_v1_context_pb2
from acme.customers.v1 import refs_pb2 as customers_v1_refs_pb2
from acme.datasets.v1 import dataset_query_service_pb2 as datasets_v1_dataset_query_service_pb2
from acme.datasets.v1 import (
    dataset_version_validation_service_pb2 as datasets_v1_dataset_version_validation_service_pb2,
)
from acme.datasets.v1 import datasets_pb2 as datasets_v1_datasets_pb2
from acme.datasets.v1 import refs_pb2 as datasets_v1_refs_pb2
from acme.featurestore.v1 import entity_calculation_service_pb2 as featurestore_v1_entity_calculation_service_pb2
from acme.featurestore.v1 import (
    feature_value_calculation_service_pb2 as featurestore_v1_feature_value_calculation_service_pb2,
)
from acme.featurestore.v1 import feature_value_import_service_pb2 as featurestore_v1_feature_value_import_service_pb2
from acme.featurestore.v1 import (
    feature_value_lifecycle_service_pb2 as featurestore_v1_feature_value_lifecycle_service_pb2,
)
from acme.featurestore.v1 import (
    feature_value_reporting_service_pb2 as featurestore_v1_feature_value_reporting_service_pb2,
)
from acme.featurestore.v1 import (
    feature_view_lifecycle_service_pb2 as featurestore_v1_feature_view_lifecycle_service_pb2,
)
from acme.featurestore.v1 import feature_view_sync_service_pb2 as featurestore_v1_feature_view_sync_service_pb2
from acme.featurestore.v1 import (
    feature_view_validation_service_pb2 as featurestore_v1_feature_view_validation_service_pb2,
)
from acme.featurestore.v1 import featurestore_pb2 as featurestore_v1_featurestore_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.ledger.v1 import ledger_account_validation_service_pb2 as ledger_v1_ledger_account_validation_service_pb2
from acme.ledger.v1 import ledger_pb2 as ledger_v1_ledger_pb2
from acme.metrics.v1 import metric_series_history_service_pb2 as metrics_v1_metric_series_history_service_pb2
from acme.metrics.v1 import metrics_pb2 as metrics_v1_metrics_pb2
from acme.notifications.v1 import notification_query_service_pb2 as notifications_v1_notification_query_service_pb2
from acme.notifications.v1 import notification_service_pb2 as notifications_v1_notification_service_pb2
from acme.search.v1 import search_index_validation_service_pb2 as search_v1_search_index_validation_service_pb2
from acme.search.v1 import search_pb2 as search_v1_search_pb2
from acme.telehealth.v1 import video_visit_service_pb2 as telehealth_v1_video_visit_service_pb2

from acme_data.platform.models import ValidatedModel


@dataclass(frozen=True, slots=True)
class EntityApprovalApproveEntity0Command:
    """Inputs required to preview search index."""
    context: common_v1_context_pb2.RequestContext
    details_contact_email: str
    details_contact_preferred_channel: str
    search_index_owner_email: str


def to_entity_approval_approve_entity0_command(
    command: EntityApprovalApproveEntity0Command
) -> search_v1_search_index_validation_service_pb2.PreviewSearchIndexRequest:
    return search_v1_search_index_validation_service_pb2.PreviewSearchIndexRequest(
        context=command.context,
        details=search_v1_search_index_validation_service_pb2.PreviewSearchIndexRequest.Details(
            contact=common_v1_contact_pb2.ContactInfo(
                email=command.details_contact_email,
                preferred_channel=command.details_contact_preferred_channel
            )
        ),
        search_index=search_v1_search_pb2.SearchIndex(
            owner=identity_v1_refs_pb2.UserRef(email=command.search_index_owner_email)
        )
    )


@dataclass(frozen=True, slots=True)
class EntityCalculationCompareEntityOptions1Command:
    """Inputs required to score feature view."""
    context: common_v1_context_pb2.RequestContext
    details_destination_lines: list[str]
    feature_view_owner_email: str


def to_entity_calculation_compare_entity_options1_command(
    command: EntityCalculationCompareEntityOptions1Command
) -> featurestore_v1_feature_view_validation_service_pb2.ScoreFeatureViewRequest:
    return featurestore_v1_feature_view_validation_service_pb2.ScoreFeatureViewRequest(
        context=command.context,
        details=featurestore_v1_feature_view_validation_service_pb2.ScoreFeatureViewRequest.Details(
            destination=common_v1_address_pb2.PostalAddress(lines=command.details_destination_lines)
        ),
        feature_view=featurestore_v1_featurestore_pb2.FeatureView(
            owner=identity_v1_refs_pb2.UserRef(email=command.feature_view_owner_email)
        )
    )


@dataclass(frozen=True, slots=True)
class EntityCalculationEstimateEntity0Command(ValidatedModel):
    """Inputs required to score feature view."""
    context: common_v1_context_pb2.RequestContext
    feature_view_audit_updated_by: str
    feature_view_address_locality: str


def to_entity_calculation_estimate_entity0_command(
    command: EntityCalculationEstimateEntity0Command
) -> featurestore_v1_feature_view_validation_service_pb2.ScoreFeatureViewRequest:
    return featurestore_v1_feature_view_validation_service_pb2.ScoreFeatureViewRequest(
        context=command.context,
        feature_view=featurestore_v1_featurestore_pb2.FeatureView(
            address=common_v1_address_pb2.PostalAddress(locality=command.feature_view_address_locality),
            audit=common_v1_audit_pb2.AuditInfo(updated_by=command.feature_view_audit_updated_by)
        )
    )


@dataclass(frozen=True, slots=True)
class EntityImportRetryEntityImport1Command(ValidatedModel):
    """Inputs required to count products."""
    context: common_v1_context_pb2.RequestContext
    filter_region: str


def to_entity_import_retry_entity_import1_command(
    command: EntityImportRetryEntityImport1Command
) -> catalog_v1_product_query_service_pb2.CountProductsRequest:
    return catalog_v1_product_query_service_pb2.CountProductsRequest(
        context=command.context,
        filter=catalog_v1_product_query_service_pb2.CountProductsRequest.Filter(region=command.filter_region)
    )


@dataclass(frozen=True, slots=True)
class EntityLifecycleSuspendEntity3Command:
    """Inputs required to summarize datasets."""
    context: common_v1_context_pb2.RequestContext
    annotations: dict[str, str]
    details_period: common_v1_audit_pb2.TimeWindow


def to_entity_lifecycle_suspend_entity3_command(
    command: EntityLifecycleSuspendEntity3Command
) -> datasets_v1_dataset_query_service_pb2.SummarizeDatasetsRequest:
    return datasets_v1_dataset_query_service_pb2.SummarizeDatasetsRequest(
        annotations=command.annotations,
        context=command.context,
        details=datasets_v1_dataset_query_service_pb2.SummarizeDatasetsRequest.Details(period=command.details_period)
    )


@dataclass(frozen=True, slots=True)
class EntityReportingStreamEntityMetrics1Command:
    """Inputs required to push feature view."""
    context: common_v1_context_pb2.RequestContext
    feature_view_components_component_id: str
    feature_view_address_region: str
    feature_view_owner_email: str
    feature_view_dimensions_width: float


def to_entity_reporting_stream_entity_metrics1_command(
    command: EntityReportingStreamEntityMetrics1Command
) -> featurestore_v1_feature_view_sync_service_pb2.PushFeatureViewRequest:
    return featurestore_v1_feature_view_sync_service_pb2.PushFeatureViewRequest(
        context=command.context,
        feature_view=featurestore_v1_featurestore_pb2.FeatureView(
            address=common_v1_address_pb2.PostalAddress(region=command.feature_view_address_region),
            components={
                'primary': featurestore_v1_featurestore_pb2.FeatureViewComponent(
                    component_id=command.feature_view_components_component_id
                )
            },
            dimensions=featurestore_v1_featurestore_pb2.FeatureViewDimensions(
                width=command.feature_view_dimensions_width
            ),
            owner=identity_v1_refs_pb2.UserRef(email=command.feature_view_owner_email)
        )
    )


@dataclass(frozen=True, slots=True)
class EntityValidationExplainEntityDecision0Command:
    """Inputs required to recalculate feature values."""
    context: common_v1_context_pb2.RequestContext
    details_destination_recipient: str
    details_destination_country_code: str
    details_destination_lines: list[str]


def to_entity_validation_explain_entity_decision0_command(
    command: EntityValidationExplainEntityDecision0Command
) -> featurestore_v1_feature_value_calculation_service_pb2.RecalculateFeatureValuesRequest:
    return featurestore_v1_feature_value_calculation_service_pb2.RecalculateFeatureValuesRequest(
        context=command.context,
        details=featurestore_v1_feature_value_calculation_service_pb2.RecalculateFeatureValuesRequest.Details(
            destination=common_v1_address_pb2.PostalAddress(
                country_code=command.details_destination_country_code,
                lines=command.details_destination_lines,
                recipient=command.details_destination_recipient
            )
        )
    )


@dataclass(frozen=True, slots=True)
class EntityValidationExplainEntityDecision1Command(ValidatedModel):
    """Inputs required to quote entity."""
    context: common_v1_context_pb2.RequestContext
    entity_primary_address_region: str


def to_entity_validation_explain_entity_decision1_command(
    command: EntityValidationExplainEntityDecision1Command
) -> featurestore_v1_entity_calculation_service_pb2.QuoteEntityRequest:
    return featurestore_v1_entity_calculation_service_pb2.QuoteEntityRequest(
        context=command.context,
        entity=featurestore_v1_featurestore_pb2.Entity(
            primary_address=common_v1_address_pb2.PostalAddress(region=command.entity_primary_address_region)
        )
    )


@dataclass(frozen=True, slots=True)
class EntityWorkflowAdvanceEntityWorkflow2Command(ValidatedModel):
    """Inputs required to list feature value reports."""
    context: common_v1_context_pb2.RequestContext
    filter_region: str
    filter_labels: dict[str, str]
    filter_created_after: timestamp_pb2.Timestamp
    filter_owner_id: str


def to_entity_workflow_advance_entity_workflow2_command(
    command: EntityWorkflowAdvanceEntityWorkflow2Command
) -> featurestore_v1_feature_value_reporting_service_pb2.ListFeatureValueReportsRequest:
    return featurestore_v1_feature_value_reporting_service_pb2.ListFeatureValueReportsRequest(
        context=command.context,
        filter=featurestore_v1_feature_value_reporting_service_pb2.ListFeatureValueReportsRequest.Filter(
            created_after=command.filter_created_after,
            labels=command.filter_labels,
            owner_id=command.filter_owner_id,
            region=command.filter_region
        )
    )


@dataclass(frozen=True, slots=True)
class FeatureValueApprovalCommentFeatureValueApproval2Command:
    """Inputs required to retry feature value import."""
    context: common_v1_context_pb2.RequestContext
    feature_value_subject_dataset_id: str
    feature_value_subject_display_name: str
    feature_value_subject_code: str


def to_feature_value_approval_comment_feature_value_approval2_command(
    command: FeatureValueApprovalCommentFeatureValueApproval2Command
) -> featurestore_v1_feature_value_import_service_pb2.RetryFeatureValueImportRequest:
    return featurestore_v1_feature_value_import_service_pb2.RetryFeatureValueImportRequest(
        context=command.context,
        feature_value=featurestore_v1_featurestore_pb2.FeatureValue(
            subject=datasets_v1_refs_pb2.DatasetRef(
                code=command.feature_value_subject_code,
                dataset_id=command.feature_value_subject_dataset_id,
                display_name=command.feature_value_subject_display_name
            )
        )
    )


@dataclass(frozen=True, slots=True)
class FeatureValueApprovalDelegateFeatureValueApproval0Command(ValidatedModel):
    """Inputs required to sync feature views."""
    context: common_v1_context_pb2.RequestContext
    feature_view_owner_email: str


def to_feature_value_approval_delegate_feature_value_approval0_command(
    command: FeatureValueApprovalDelegateFeatureValueApproval0Command
) -> featurestore_v1_feature_view_sync_service_pb2.SyncFeatureViewsRequest:
    return featurestore_v1_feature_view_sync_service_pb2.SyncFeatureViewsRequest(
        context=command.context,
        feature_view=featurestore_v1_featurestore_pb2.FeatureView(
            owner=identity_v1_refs_pb2.UserRef(email=command.feature_view_owner_email)
        )
    )


@dataclass(frozen=True, slots=True)
class FeatureValueApprovalSubmitFeatureValue2Command:
    """Inputs required to schedule feature value expiry."""
    context: common_v1_context_pb2.RequestContext
    feature_value_subject_display_name: str


def to_feature_value_approval_submit_feature_value2_command(
    command: FeatureValueApprovalSubmitFeatureValue2Command
) -> featurestore_v1_feature_value_lifecycle_service_pb2.ScheduleFeatureValueExpiryRequest:
    return featurestore_v1_feature_value_lifecycle_service_pb2.ScheduleFeatureValueExpiryRequest(
        context=command.context,
        feature_value=featurestore_v1_featurestore_pb2.FeatureValue(
            subject=datasets_v1_refs_pb2.DatasetRef(display_name=command.feature_value_subject_display_name)
        )
    )


@dataclass(frozen=True, slots=True)
class FeatureValueCalculationCalculateFeatureValue0Command(ValidatedModel):
    """Inputs required to compare metric series versions."""
    context: common_v1_context_pb2.RequestContext
    metric_series_address_locality: str


def to_feature_value_calculation_calculate_feature_value0_command(
    command: FeatureValueCalculationCalculateFeatureValue0Command
) -> metrics_v1_metric_series_history_service_pb2.CompareMetricSeriesVersionsRequest:
    return metrics_v1_metric_series_history_service_pb2.CompareMetricSeriesVersionsRequest(
        context=command.context,
        metric_series=metrics_v1_metrics_pb2.MetricSeries(
            address=common_v1_address_pb2.PostalAddress(locality=command.metric_series_address_locality)
        )
    )


@dataclass(frozen=True, slots=True)
class FeatureValueLifecycleReinstateFeatureValue0Command:
    """Inputs required to list feature value imports."""
    context: common_v1_context_pb2.RequestContext
    filter_created_after: timestamp_pb2.Timestamp
    filter_owner_id: str
    filter_labels: dict[str, str]


def to_feature_value_lifecycle_reinstate_feature_value0_command(
    command: FeatureValueLifecycleReinstateFeatureValue0Command
) -> featurestore_v1_feature_value_import_service_pb2.ListFeatureValueImportsRequest:
    return featurestore_v1_feature_value_import_service_pb2.ListFeatureValueImportsRequest(
        context=command.context,
        filter=featurestore_v1_feature_value_import_service_pb2.ListFeatureValueImportsRequest.Filter(
            created_after=command.filter_created_after,
            labels=command.filter_labels,
            owner_id=command.filter_owner_id
        )
    )


@dataclass(frozen=True, slots=True)
class FeatureValueReportingStreamFeatureValueMetrics2Command:
    """Inputs required to lint dataset versions."""
    context: common_v1_context_pb2.RequestContext
    dataset_version_subject_email: str
    dataset_version_subject_display_name: str
    details_contact_name: common_v1_contact_pb2.PersonName


def to_feature_value_reporting_stream_feature_value_metrics2_command(
    command: FeatureValueReportingStreamFeatureValueMetrics2Command
) -> datasets_v1_dataset_version_validation_service_pb2.LintDatasetVersionsRequest:
    return datasets_v1_dataset_version_validation_service_pb2.LintDatasetVersionsRequest(
        context=command.context,
        dataset_version=datasets_v1_datasets_pb2.DatasetVersion(
            subject=customers_v1_refs_pb2.CustomerRef(
                display_name=command.dataset_version_subject_display_name,
                email=command.dataset_version_subject_email
            )
        ),
        details=datasets_v1_dataset_version_validation_service_pb2.LintDatasetVersionsRequest.Details(
            contact=common_v1_contact_pb2.ContactInfo(name=command.details_contact_name)
        )
    )


@dataclass(frozen=True, slots=True)
class FeatureValueValidationValidateFeatureValue3Command:
    """Inputs required to browse detectors."""
    context: common_v1_context_pb2.RequestContext
    filter_region: str
    filter_created_after: timestamp_pb2.Timestamp
    filter_owner_id: str
    filter_labels: dict[str, str]


def to_feature_value_validation_validate_feature_value3_command(
    command: FeatureValueValidationValidateFeatureValue3Command
) -> anomalies_v1_detector_query_service_pb2.BrowseDetectorsRequest:
    return anomalies_v1_detector_query_service_pb2.BrowseDetectorsRequest(
        context=command.context,
        filter=anomalies_v1_detector_query_service_pb2.BrowseDetectorsRequest.Filter(
            created_after=command.filter_created_after,
            labels=command.filter_labels,
            owner_id=command.filter_owner_id,
            region=command.filter_region
        )
    )


@dataclass(frozen=True, slots=True)
class FeatureValueWorkflowAdvanceFeatureValueWorkflow0Command(ValidatedModel):
    """Inputs required to recall detector."""
    context: common_v1_context_pb2.RequestContext
    detector_owner_email: str


def to_feature_value_workflow_advance_feature_value_workflow0_command(
    command: FeatureValueWorkflowAdvanceFeatureValueWorkflow0Command
) -> anomalies_v1_detector_approval_service_pb2.RecallDetectorRequest:
    return anomalies_v1_detector_approval_service_pb2.RecallDetectorRequest(
        context=command.context,
        detector=anomalies_v1_anomalies_pb2.Detector(
            owner=identity_v1_refs_pb2.UserRef(email=command.detector_owner_email)
        )
    )


@dataclass(frozen=True, slots=True)
class FeatureValueWorkflowStartFeatureValueWorkflow1Command:
    """Inputs required to submit anomaly feedback."""
    context: common_v1_context_pb2.RequestContext
    anomaly_feedback_subject_code: str
    details_effective_at: timestamp_pb2.Timestamp


def to_feature_value_workflow_start_feature_value_workflow1_command(
    command: FeatureValueWorkflowStartFeatureValueWorkflow1Command
) -> anomalies_v1_anomaly_feedback_approval_service_pb2.SubmitAnomalyFeedbackRequest:
    return anomalies_v1_anomaly_feedback_approval_service_pb2.SubmitAnomalyFeedbackRequest(
        anomaly_feedback=anomalies_v1_anomalies_pb2.AnomalyFeedback(
            subject=datasets_v1_refs_pb2.DatasetRef(code=command.anomaly_feedback_subject_code)
        ),
        context=command.context,
        details=anomalies_v1_anomaly_feedback_approval_service_pb2.SubmitAnomalyFeedbackRequest.Details(
            effective_at=command.details_effective_at
        )
    )


@dataclass(frozen=True, slots=True)
class FeatureViewApprovalRejectFeatureView3Command:
    """Inputs required to submit anomaly feedback."""
    context: common_v1_context_pb2.RequestContext
    details_approver_user_id: str
    anomaly_feedback_subject_display_name: str
    details_approver_display_name: str
    anomaly_feedback_kind: str


def to_feature_view_approval_reject_feature_view3_command(
    command: FeatureViewApprovalRejectFeatureView3Command
) -> anomalies_v1_anomaly_feedback_approval_service_pb2.SubmitAnomalyFeedbackRequest:
    return anomalies_v1_anomaly_feedback_approval_service_pb2.SubmitAnomalyFeedbackRequest(
        anomaly_feedback=anomalies_v1_anomalies_pb2.AnomalyFeedback(
            kind=command.anomaly_feedback_kind,
            subject=datasets_v1_refs_pb2.DatasetRef(display_name=command.anomaly_feedback_subject_display_name)
        ),
        context=command.context,
        details=anomalies_v1_anomaly_feedback_approval_service_pb2.SubmitAnomalyFeedbackRequest.Details(
            approver=identity_v1_refs_pb2.UserRef(
                display_name=command.details_approver_display_name,
                user_id=command.details_approver_user_id
            )
        )
    )


@dataclass(frozen=True, slots=True)
class FeatureViewLifecycleScheduleFeatureViewExpiry2Command(ValidatedModel):
    """Inputs required to summarize notifications."""
    context: common_v1_context_pb2.RequestContext
    annotations: dict[str, str]
    reason: str
    details_filters: dict[str, str]


def to_feature_view_lifecycle_schedule_feature_view_expiry2_command(
    command: FeatureViewLifecycleScheduleFeatureViewExpiry2Command
) -> notifications_v1_notification_query_service_pb2.SummarizeNotificationsRequest:
    return notifications_v1_notification_query_service_pb2.SummarizeNotificationsRequest(
        annotations=command.annotations,
        context=command.context,
        details=notifications_v1_notification_query_service_pb2.SummarizeNotificationsRequest.Details(
            filters=command.details_filters
        ),
        reason=command.reason
    )


@dataclass(frozen=True, slots=True)
class FeatureViewReportingFetchFeatureViewReport1Command(ValidatedModel):
    """Inputs required to estimate entity."""
    context: common_v1_context_pb2.RequestContext
    entity_contact_email: str


def to_feature_view_reporting_fetch_feature_view_report1_command(
    command: FeatureViewReportingFetchFeatureViewReport1Command
) -> featurestore_v1_entity_calculation_service_pb2.EstimateEntityRequest:
    return featurestore_v1_entity_calculation_service_pb2.EstimateEntityRequest(
        context=command.context,
        entity=featurestore_v1_featurestore_pb2.Entity(
            contact=common_v1_contact_pb2.ContactInfo(email=command.entity_contact_email)
        )
    )


@dataclass(frozen=True, slots=True)
class FeatureViewCloneFeatureView1Command:
    """Inputs required to explain ledger account decision."""
    context: common_v1_context_pb2.RequestContext
    ledger_account_audit_updated_by: str
    ledger_account_audit_created_at: timestamp_pb2.Timestamp


def to_feature_view_clone_feature_view1_command(
    command: FeatureViewCloneFeatureView1Command
) -> ledger_v1_ledger_account_validation_service_pb2.ExplainLedgerAccountDecisionRequest:
    return ledger_v1_ledger_account_validation_service_pb2.ExplainLedgerAccountDecisionRequest(
        context=command.context,
        ledger_account=ledger_v1_ledger_pb2.LedgerAccount(
            audit=common_v1_audit_pb2.AuditInfo(
                created_at=command.ledger_account_audit_created_at,
                updated_by=command.ledger_account_audit_updated_by
            )
        )
    )


@dataclass(frozen=True, slots=True)
class FeatureViewCloneFeatureView2Command(ValidatedModel):
    """Inputs required to search video visits."""
    context: common_v1_context_pb2.RequestContext
    filter_labels: dict[str, str]
    filter_region: str


def to_feature_view_clone_feature_view2_command(
    command: FeatureViewCloneFeatureView2Command
) -> telehealth_v1_video_visit_service_pb2.SearchVideoVisitsRequest:
    return telehealth_v1_video_visit_service_pb2.SearchVideoVisitsRequest(
        context=command.context,
        filter=telehealth_v1_video_visit_service_pb2.SearchVideoVisitsRequest.Filter(
            labels=command.filter_labels,
            region=command.filter_region
        )
    )


@dataclass(frozen=True, slots=True)
class FeatureViewSyncPushFeatureView0Command(ValidatedModel):
    """Inputs required to resume anomaly feedback workflow."""
    context: common_v1_context_pb2.RequestContext
    anomaly_feedback_subject_display_name: str
    details_notify_email: str
    anomaly_feedback_measurements_unit: str


def to_feature_view_sync_push_feature_view0_command(
    command: FeatureViewSyncPushFeatureView0Command
) -> anomalies_v1_anomaly_feedback_workflow_service_pb2.ResumeAnomalyFeedbackWorkflowRequest:
    return anomalies_v1_anomaly_feedback_workflow_service_pb2.ResumeAnomalyFeedbackWorkflowRequest(
        anomaly_feedback=anomalies_v1_anomalies_pb2.AnomalyFeedback(
            measurements=[
                anomalies_v1_anomalies_pb2.AnomalyFeedbackMeasurement(unit=command.anomaly_feedback_measurements_unit)
            ],
            subject=datasets_v1_refs_pb2.DatasetRef(display_name=command.anomaly_feedback_subject_display_name)
        ),
        context=command.context,
        details=anomalies_v1_anomaly_feedback_workflow_service_pb2.ResumeAnomalyFeedbackWorkflowRequest.Details(
            notify=common_v1_contact_pb2.ContactInfo(email=command.details_notify_email)
        )
    )


@dataclass(frozen=True, slots=True)
class FeatureViewValidationScoreFeatureView1Command:
    """Inputs required to search notifications."""
    context: common_v1_context_pb2.RequestContext
    filter_region: str


def to_feature_view_validation_score_feature_view1_command(
    command: FeatureViewValidationScoreFeatureView1Command
) -> notifications_v1_notification_service_pb2.SearchNotificationsRequest:
    return notifications_v1_notification_service_pb2.SearchNotificationsRequest(
        context=command.context,
        filter=notifications_v1_notification_service_pb2.SearchNotificationsRequest.Filter(region=command.filter_region)
    )


@dataclass(frozen=True, slots=True)
class FeatureViewValidationScoreFeatureView2Command(ValidatedModel):
    """Inputs required to list notifications."""
    context: common_v1_context_pb2.RequestContext
    filter_region: str


def to_feature_view_validation_score_feature_view2_command(
    command: FeatureViewValidationScoreFeatureView2Command
) -> notifications_v1_notification_service_pb2.ListNotificationsRequest:
    return notifications_v1_notification_service_pb2.ListNotificationsRequest(
        context=command.context,
        filter=notifications_v1_notification_service_pb2.ListNotificationsRequest.Filter(region=command.filter_region)
    )


@dataclass(frozen=True, slots=True)
class FeatureViewWorkflowRetryFeatureViewWorkflow0Command:
    """Inputs required to get feature view lifecycle."""
    context: common_v1_context_pb2.RequestContext
    feature_view_id: str


def to_feature_view_workflow_retry_feature_view_workflow0_command(
    command: FeatureViewWorkflowRetryFeatureViewWorkflow0Command
) -> featurestore_v1_feature_view_lifecycle_service_pb2.GetFeatureViewLifecycleRequest:
    return featurestore_v1_feature_view_lifecycle_service_pb2.GetFeatureViewLifecycleRequest(
        context=command.context,
        feature_view_id=command.feature_view_id
    )


@dataclass(frozen=True, slots=True)
class FeatureViewWorkflowRetryFeatureViewWorkflow1Command(ValidatedModel):
    """Inputs required to count feature value totals."""
    context: common_v1_context_pb2.RequestContext
    filter_region: str
    filter_created_after: timestamp_pb2.Timestamp
    filter_owner_id: str


def to_feature_view_workflow_retry_feature_view_workflow1_command(
    command: FeatureViewWorkflowRetryFeatureViewWorkflow1Command
) -> featurestore_v1_feature_value_reporting_service_pb2.CountFeatureValueTotalsRequest:
    return featurestore_v1_feature_value_reporting_service_pb2.CountFeatureValueTotalsRequest(
        context=command.context,
        filter=featurestore_v1_feature_value_reporting_service_pb2.CountFeatureValueTotalsRequest.Filter(
            created_after=command.filter_created_after,
            owner_id=command.filter_owner_id,
            region=command.filter_region
        )
    )
