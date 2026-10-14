"""Typed commands crossing the datasets application boundary."""

from __future__ import annotations

from dataclasses import dataclass

from google.protobuf import timestamp_pb2 as timestamp_pb2

from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.common.v1 import context_pb2 as common_v1_context_pb2
from acme.customers.v1 import customer_query_service_pb2 as customers_v1_customer_query_service_pb2
from acme.datasets.v1 import dataset_approval_service_pb2 as datasets_v1_dataset_approval_service_pb2
from acme.datasets.v1 import dataset_validation_service_pb2 as datasets_v1_dataset_validation_service_pb2
from acme.datasets.v1 import (
    dataset_version_calculation_service_pb2 as datasets_v1_dataset_version_calculation_service_pb2,
)
from acme.datasets.v1 import dataset_workflow_service_pb2 as datasets_v1_dataset_workflow_service_pb2
from acme.datasets.v1 import datasets_pb2 as datasets_v1_datasets_pb2
from acme.documents.v1 import document_query_service_pb2 as documents_v1_document_query_service_pb2
from acme.documents.v1 import document_service_pb2 as documents_v1_document_service_pb2
from acme.featureflags.v1 import feature_flag_query_service_pb2 as featureflags_v1_feature_flag_query_service_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.identity.v1 import user_query_service_pb2 as identity_v1_user_query_service_pb2
from acme.lineage.v1 import lineage_node_validation_service_pb2 as lineage_v1_lineage_node_validation_service_pb2
from acme.lineage.v1 import lineage_pb2 as lineage_v1_lineage_pb2
from acme.metrics.v1 import metric_alert_export_service_pb2 as metrics_v1_metric_alert_export_service_pb2
from acme.notifications.v1 import notification_query_service_pb2 as notifications_v1_notification_query_service_pb2
from acme.pipelines.v1 import pipeline_run_calculation_service_pb2 as pipelines_v1_pipeline_run_calculation_service_pb2
from acme.venues.v1 import venue_query_service_pb2 as venues_v1_venue_query_service_pb2

from acme_data.platform.models import ValidatedModel


@dataclass(frozen=True, slots=True)
class DataSchemaApprovalApproveDataSchema3Command:
    """Inputs required to summarize venues."""
    context: common_v1_context_pb2.RequestContext
    reason: str
    annotations: dict[str, str]


def to_data_schema_approval_approve_data_schema3_command(
    command: DataSchemaApprovalApproveDataSchema3Command
) -> venues_v1_venue_query_service_pb2.SummarizeVenuesRequest:
    return venues_v1_venue_query_service_pb2.SummarizeVenuesRequest(
        annotations=command.annotations,
        context=command.context,
        reason=command.reason
    )


@dataclass(frozen=True, slots=True)
class DataSchemaApprovalRecallDataSchema1Command:
    """Inputs required to resolve customers."""
    context: common_v1_context_pb2.RequestContext


def to_data_schema_approval_recall_data_schema1_command(
    command: DataSchemaApprovalRecallDataSchema1Command
) -> customers_v1_customer_query_service_pb2.ResolveCustomersRequest:
    return customers_v1_customer_query_service_pb2.ResolveCustomersRequest(context=command.context)


@dataclass(frozen=True, slots=True)
class DataSchemaApprovalRecallDataSchema2Command(ValidatedModel):
    """Inputs required to browse documents."""
    context: common_v1_context_pb2.RequestContext
    filter_region: str
    filter_created_after: timestamp_pb2.Timestamp
    filter_labels: dict[str, str]
    filter_owner_id: str


def to_data_schema_approval_recall_data_schema2_command(
    command: DataSchemaApprovalRecallDataSchema2Command
) -> documents_v1_document_query_service_pb2.BrowseDocumentsRequest:
    return documents_v1_document_query_service_pb2.BrowseDocumentsRequest(
        context=command.context,
        filter=documents_v1_document_query_service_pb2.BrowseDocumentsRequest.Filter(
            created_after=command.filter_created_after,
            labels=command.filter_labels,
            owner_id=command.filter_owner_id,
            region=command.filter_region
        )
    )


@dataclass(frozen=True, slots=True)
class DataSchemaCalculationExplainDataSchemaCalculation2Command:
    """Inputs required to validate lineage node."""
    context: common_v1_context_pb2.RequestContext
    lineage_node_children_children_manager_display_name: str
    lineage_node_children_children_location_postal_code: str


def to_data_schema_calculation_explain_data_schema_calculation2_command(
    command: DataSchemaCalculationExplainDataSchemaCalculation2Command
) -> lineage_v1_lineage_node_validation_service_pb2.ValidateLineageNodeRequest:
    return lineage_v1_lineage_node_validation_service_pb2.ValidateLineageNodeRequest(
        context=command.context,
        lineage_node=lineage_v1_lineage_pb2.LineageNode(
            children=[
                lineage_v1_lineage_pb2.LineageNode(
                    children=[
                        lineage_v1_lineage_pb2.LineageNode(
                            location=common_v1_address_pb2.PostalAddress(
                                postal_code=command.lineage_node_children_children_location_postal_code
                            ),
                            manager=identity_v1_refs_pb2.UserRef(
                                display_name=command.lineage_node_children_children_manager_display_name
                            )
                        )
                    ]
                )
            ]
        )
    )


@dataclass(frozen=True, slots=True)
class DataSchemaValidationPreviewDataSchema1Command:
    """Inputs required to count feature flags."""
    context: common_v1_context_pb2.RequestContext
    filter_region: str
    filter_created_after: timestamp_pb2.Timestamp
    filter_owner_id: str
    filter_labels: dict[str, str]


def to_data_schema_validation_preview_data_schema1_command(
    command: DataSchemaValidationPreviewDataSchema1Command
) -> featureflags_v1_feature_flag_query_service_pb2.CountFeatureFlagsRequest:
    return featureflags_v1_feature_flag_query_service_pb2.CountFeatureFlagsRequest(
        context=command.context,
        filter=featureflags_v1_feature_flag_query_service_pb2.CountFeatureFlagsRequest.Filter(
            created_after=command.filter_created_after,
            labels=command.filter_labels,
            owner_id=command.filter_owner_id,
            region=command.filter_region
        )
    )


@dataclass(frozen=True, slots=True)
class DataSchemaValidationPreviewDataSchema2Command(ValidatedModel):
    """Inputs required to calculate dataset version."""
    context: common_v1_context_pb2.RequestContext
    details_destination_lines: list[str]
    details_destination_locality: str
    details_destination_postal_code: str


def to_data_schema_validation_preview_data_schema2_command(
    command: DataSchemaValidationPreviewDataSchema2Command
) -> datasets_v1_dataset_version_calculation_service_pb2.CalculateDatasetVersionRequest:
    return datasets_v1_dataset_version_calculation_service_pb2.CalculateDatasetVersionRequest(
        context=command.context,
        details=datasets_v1_dataset_version_calculation_service_pb2.CalculateDatasetVersionRequest.Details(
            destination=common_v1_address_pb2.PostalAddress(
                lines=command.details_destination_lines,
                locality=command.details_destination_locality,
                postal_code=command.details_destination_postal_code
            )
        )
    )


@dataclass(frozen=True, slots=True)
class DataSchemaWorkflowRetryDataSchemaWorkflow0Command:
    """Inputs required to submit dataset."""
    context: common_v1_context_pb2.RequestContext
    details_approver_display_name: str
    dataset_audit_updated_by: str
    dataset_audit_created_at: timestamp_pb2.Timestamp
    dataset_owner_email: str


def to_data_schema_workflow_retry_data_schema_workflow0_command(
    command: DataSchemaWorkflowRetryDataSchemaWorkflow0Command
) -> datasets_v1_dataset_approval_service_pb2.SubmitDatasetRequest:
    return datasets_v1_dataset_approval_service_pb2.SubmitDatasetRequest(
        context=command.context,
        dataset=datasets_v1_datasets_pb2.Dataset(
            audit=common_v1_audit_pb2.AuditInfo(
                created_at=command.dataset_audit_created_at,
                updated_by=command.dataset_audit_updated_by
            ),
            owner=identity_v1_refs_pb2.UserRef(email=command.dataset_owner_email)
        ),
        details=datasets_v1_dataset_approval_service_pb2.SubmitDatasetRequest.Details(
            approver=identity_v1_refs_pb2.UserRef(display_name=command.details_approver_display_name)
        )
    )


@dataclass(frozen=True, slots=True)
class DataSchemaWorkflowRetryDataSchemaWorkflow1Command(ValidatedModel):
    """Inputs required to cancel dataset workflow."""
    context: common_v1_context_pb2.RequestContext
    dataset_audit_created_at: timestamp_pb2.Timestamp
    dataset_components_quantity: int
    dataset_audit_updated_at: timestamp_pb2.Timestamp


def to_data_schema_workflow_retry_data_schema_workflow1_command(
    command: DataSchemaWorkflowRetryDataSchemaWorkflow1Command
) -> datasets_v1_dataset_workflow_service_pb2.CancelDatasetWorkflowRequest:
    return datasets_v1_dataset_workflow_service_pb2.CancelDatasetWorkflowRequest(
        context=command.context,
        dataset=datasets_v1_datasets_pb2.Dataset(
            audit=common_v1_audit_pb2.AuditInfo(
                created_at=command.dataset_audit_created_at,
                updated_at=command.dataset_audit_updated_at
            ),
            components={
                'primary': datasets_v1_datasets_pb2.DatasetComponent(quantity=command.dataset_components_quantity)
            }
        )
    )


@dataclass(frozen=True, slots=True)
class DatasetBatchCreateDatasets1Command:
    """Inputs required to preview dataset."""
    context: common_v1_context_pb2.RequestContext
    dataset_address_recipient: str
    dataset_audit_created_by: str
    dataset_audit_updated_at: timestamp_pb2.Timestamp
    dataset_address_region: str


def to_dataset_batch_create_datasets1_command(
    command: DatasetBatchCreateDatasets1Command
) -> datasets_v1_dataset_validation_service_pb2.PreviewDatasetRequest:
    return datasets_v1_dataset_validation_service_pb2.PreviewDatasetRequest(
        context=command.context,
        dataset=datasets_v1_datasets_pb2.Dataset(
            address=common_v1_address_pb2.PostalAddress(
                recipient=command.dataset_address_recipient,
                region=command.dataset_address_region
            ),
            audit=common_v1_audit_pb2.AuditInfo(
                created_by=command.dataset_audit_created_by,
                updated_at=command.dataset_audit_updated_at
            )
        )
    )


@dataclass(frozen=True, slots=True)
class DatasetValidationCheckDatasetEligibility1Command(ValidatedModel):
    """Inputs required to list metric alert exports."""
    context: common_v1_context_pb2.RequestContext
    filter_region: str
    filter_created_after: timestamp_pb2.Timestamp


def to_dataset_validation_check_dataset_eligibility1_command(
    command: DatasetValidationCheckDatasetEligibility1Command
) -> metrics_v1_metric_alert_export_service_pb2.ListMetricAlertExportsRequest:
    return metrics_v1_metric_alert_export_service_pb2.ListMetricAlertExportsRequest(
        context=command.context,
        filter=metrics_v1_metric_alert_export_service_pb2.ListMetricAlertExportsRequest.Filter(
            created_after=command.filter_created_after,
            region=command.filter_region
        )
    )


@dataclass(frozen=True, slots=True)
class DatasetValidationScoreDataset2Command(ValidatedModel):
    """Inputs required to estimate pipeline run."""
    context: common_v1_context_pb2.RequestContext
    details_destination_country_code: str
    details_destination_recipient: str


def to_dataset_validation_score_dataset2_command(
    command: DatasetValidationScoreDataset2Command
) -> pipelines_v1_pipeline_run_calculation_service_pb2.EstimatePipelineRunRequest:
    return pipelines_v1_pipeline_run_calculation_service_pb2.EstimatePipelineRunRequest(
        context=command.context,
        details=pipelines_v1_pipeline_run_calculation_service_pb2.EstimatePipelineRunRequest.Details(
            destination=common_v1_address_pb2.PostalAddress(
                country_code=command.details_destination_country_code,
                recipient=command.details_destination_recipient
            )
        )
    )


@dataclass(frozen=True, slots=True)
class DatasetVersionApprovalSubmitDatasetVersion0Command:
    """Inputs required to normalize dataset."""
    context: common_v1_context_pb2.RequestContext
    dataset_owner_email: str
    details_contact_email: str
    dataset_owner_display_name: str
    annotations: dict[str, str]


def to_dataset_version_approval_submit_dataset_version0_command(
    command: DatasetVersionApprovalSubmitDatasetVersion0Command
) -> datasets_v1_dataset_validation_service_pb2.NormalizeDatasetRequest:
    return datasets_v1_dataset_validation_service_pb2.NormalizeDatasetRequest(
        annotations=command.annotations,
        context=command.context,
        dataset=datasets_v1_datasets_pb2.Dataset(
            owner=identity_v1_refs_pb2.UserRef(
                display_name=command.dataset_owner_display_name,
                email=command.dataset_owner_email
            )
        ),
        details=datasets_v1_dataset_validation_service_pb2.NormalizeDatasetRequest.Details(
            contact=common_v1_contact_pb2.ContactInfo(email=command.details_contact_email)
        )
    )


@dataclass(frozen=True, slots=True)
class DatasetVersionCalculationQuoteDatasetVersion2Command:
    """Inputs required to browse notifications."""
    context: common_v1_context_pb2.RequestContext
    filter_region: str
    filter_created_after: timestamp_pb2.Timestamp
    filter_owner_id: str
    filter_labels: dict[str, str]


def to_dataset_version_calculation_quote_dataset_version2_command(
    command: DatasetVersionCalculationQuoteDatasetVersion2Command
) -> notifications_v1_notification_query_service_pb2.BrowseNotificationsRequest:
    return notifications_v1_notification_query_service_pb2.BrowseNotificationsRequest(
        context=command.context,
        filter=notifications_v1_notification_query_service_pb2.BrowseNotificationsRequest.Filter(
            created_after=command.filter_created_after,
            labels=command.filter_labels,
            owner_id=command.filter_owner_id,
            region=command.filter_region
        )
    )


@dataclass(frozen=True, slots=True)
class DatasetVersionCalculationSimulateDatasetVersion0Command(ValidatedModel):
    """Inputs required to list documents."""
    context: common_v1_context_pb2.RequestContext
    filter_region: str
    filter_created_after: timestamp_pb2.Timestamp
    filter_owner_id: str


def to_dataset_version_calculation_simulate_dataset_version0_command(
    command: DatasetVersionCalculationSimulateDatasetVersion0Command
) -> documents_v1_document_service_pb2.ListDocumentsRequest:
    return documents_v1_document_service_pb2.ListDocumentsRequest(
        context=command.context,
        filter=documents_v1_document_service_pb2.ListDocumentsRequest.Filter(
            created_after=command.filter_created_after,
            owner_id=command.filter_owner_id,
            region=command.filter_region
        )
    )


@dataclass(frozen=True, slots=True)
class DatasetVersionValidationExplainDatasetVersionDecision2Command:
    """Inputs required to browse users."""
    context: common_v1_context_pb2.RequestContext
    filter_created_after: timestamp_pb2.Timestamp


def to_dataset_version_validation_explain_dataset_version_decision2_command(
    command: DatasetVersionValidationExplainDatasetVersionDecision2Command
) -> identity_v1_user_query_service_pb2.BrowseUsersRequest:
    return identity_v1_user_query_service_pb2.BrowseUsersRequest(
        context=command.context,
        filter=identity_v1_user_query_service_pb2.BrowseUsersRequest.Filter(created_after=command.filter_created_after)
    )


@dataclass(frozen=True, slots=True)
class DatasetWorkflowCancelDatasetWorkflow3Command:
    """Inputs required to submit dataset."""
    context: common_v1_context_pb2.RequestContext
    dataset_owner_email: str
    dataset_dimensions_height: float
    dataset_audit_created_at: timestamp_pb2.Timestamp
    dataset_audit_updated_by: str


def to_dataset_workflow_cancel_dataset_workflow3_command(
    command: DatasetWorkflowCancelDatasetWorkflow3Command
) -> datasets_v1_dataset_approval_service_pb2.SubmitDatasetRequest:
    return datasets_v1_dataset_approval_service_pb2.SubmitDatasetRequest(
        context=command.context,
        dataset=datasets_v1_datasets_pb2.Dataset(
            audit=common_v1_audit_pb2.AuditInfo(
                created_at=command.dataset_audit_created_at,
                updated_by=command.dataset_audit_updated_by
            ),
            dimensions=datasets_v1_datasets_pb2.DatasetDimensions(height=command.dataset_dimensions_height),
            owner=identity_v1_refs_pb2.UserRef(email=command.dataset_owner_email)
        )
    )
