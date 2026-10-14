"""Typed commands crossing the modelregistry application boundary."""

from __future__ import annotations

from dataclasses import dataclass

from google.protobuf import timestamp_pb2 as timestamp_pb2

from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.common.v1 import context_pb2 as common_v1_context_pb2
from acme.customers.v1 import customer_validation_service_pb2 as customers_v1_customer_validation_service_pb2
from acme.customers.v1 import customers_pb2 as customers_v1_customers_pb2
from acme.customers.v1 import refs_pb2 as customers_v1_refs_pb2
from acme.documents.v1 import document_validation_service_pb2 as documents_v1_document_validation_service_pb2
from acme.documents.v1 import documents_pb2 as documents_v1_documents_pb2
from acme.documents.v1 import refs_pb2 as documents_v1_refs_pb2
from acme.featurestore.v1 import entity_sync_service_pb2 as featurestore_v1_entity_sync_service_pb2
from acme.featurestore.v1 import entity_validation_service_pb2 as featurestore_v1_entity_validation_service_pb2
from acme.featurestore.v1 import (
    feature_value_calculation_service_pb2 as featurestore_v1_feature_value_calculation_service_pb2,
)
from acme.featurestore.v1 import (
    feature_view_calculation_service_pb2 as featurestore_v1_feature_view_calculation_service_pb2,
)
from acme.featurestore.v1 import feature_view_query_service_pb2 as featurestore_v1_feature_view_query_service_pb2
from acme.featurestore.v1 import featurestore_pb2 as featurestore_v1_featurestore_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.identity.v1 import user_query_service_pb2 as identity_v1_user_query_service_pb2
from acme.lineage.v1 import lineage_node_approval_service_pb2 as lineage_v1_lineage_node_approval_service_pb2
from acme.lineage.v1 import lineage_pb2 as lineage_v1_lineage_pb2
from acme.metrics.v1 import metric_alert_notification_service_pb2 as metrics_v1_metric_alert_notification_service_pb2
from acme.modelregistry.v1 import (
    deployment_calculation_service_pb2 as modelregistry_v1_deployment_calculation_service_pb2,
)
from acme.modelregistry.v1 import deployment_import_service_pb2 as modelregistry_v1_deployment_import_service_pb2
from acme.modelregistry.v1 import deployment_sync_service_pb2 as modelregistry_v1_deployment_sync_service_pb2
from acme.modelregistry.v1 import (
    model_version_approval_service_pb2 as modelregistry_v1_model_version_approval_service_pb2,
)
from acme.modelregistry.v1 import (
    model_version_calculation_service_pb2 as modelregistry_v1_model_version_calculation_service_pb2,
)
from acme.modelregistry.v1 import modelregistry_pb2 as modelregistry_v1_modelregistry_pb2
from acme.modelregistry.v1 import (
    registered_model_calculation_service_pb2 as modelregistry_v1_registered_model_calculation_service_pb2,
)
from acme.modelregistry.v1 import (
    registered_model_query_service_pb2 as modelregistry_v1_registered_model_query_service_pb2,
)
from acme.modelregistry.v1 import (
    registered_model_sync_service_pb2 as modelregistry_v1_registered_model_sync_service_pb2,
)
from acme.modelregistry.v1 import (
    registered_model_validation_service_pb2 as modelregistry_v1_registered_model_validation_service_pb2,
)
from acme.venues.v1 import venue_validation_service_pb2 as venues_v1_venue_validation_service_pb2
from acme.venues.v1 import venues_pb2 as venues_v1_venues_pb2

from acme_data.platform.models import ValidatedModel


@dataclass(frozen=True, slots=True)
class DeploymentCalculationCalculateDeployment0Command:
    """Inputs required to browse feature views."""
    context: common_v1_context_pb2.RequestContext
    filter_region: str
    filter_created_after: timestamp_pb2.Timestamp
    filter_labels: dict[str, str]
    filter_owner_id: str


def to_deployment_calculation_calculate_deployment0_command(
    command: DeploymentCalculationCalculateDeployment0Command
) -> featurestore_v1_feature_view_query_service_pb2.BrowseFeatureViewsRequest:
    return featurestore_v1_feature_view_query_service_pb2.BrowseFeatureViewsRequest(
        context=command.context,
        filter=featurestore_v1_feature_view_query_service_pb2.BrowseFeatureViewsRequest.Filter(
            created_after=command.filter_created_after,
            labels=command.filter_labels,
            owner_id=command.filter_owner_id,
            region=command.filter_region
        )
    )


@dataclass(frozen=True, slots=True)
class DeploymentCalculationCompareDeploymentOptions0Command(ValidatedModel):
    """Inputs required to quote registered model."""
    context: common_v1_context_pb2.RequestContext
    registered_model_address_region: str
    details_destination_locality: str


def to_deployment_calculation_compare_deployment_options0_command(
    command: DeploymentCalculationCompareDeploymentOptions0Command
) -> modelregistry_v1_registered_model_calculation_service_pb2.QuoteRegisteredModelRequest:
    return modelregistry_v1_registered_model_calculation_service_pb2.QuoteRegisteredModelRequest(
        context=command.context,
        details=modelregistry_v1_registered_model_calculation_service_pb2.QuoteRegisteredModelRequest.Details(
            destination=common_v1_address_pb2.PostalAddress(locality=command.details_destination_locality)
        ),
        registered_model=modelregistry_v1_modelregistry_pb2.RegisteredModel(
            address=common_v1_address_pb2.PostalAddress(region=command.registered_model_address_region)
        )
    )


@dataclass(frozen=True, slots=True)
class DeploymentImportImportDeployments3Command:
    """Inputs required to count registered models."""
    context: common_v1_context_pb2.RequestContext
    filter_region: str
    filter_owner_id: str
    filter_created_after: timestamp_pb2.Timestamp
    filter_labels: dict[str, str]


def to_deployment_import_import_deployments3_command(
    command: DeploymentImportImportDeployments3Command
) -> modelregistry_v1_registered_model_query_service_pb2.CountRegisteredModelsRequest:
    return modelregistry_v1_registered_model_query_service_pb2.CountRegisteredModelsRequest(
        context=command.context,
        filter=modelregistry_v1_registered_model_query_service_pb2.CountRegisteredModelsRequest.Filter(
            created_after=command.filter_created_after,
            labels=command.filter_labels,
            owner_id=command.filter_owner_id,
            region=command.filter_region
        )
    )


@dataclass(frozen=True, slots=True)
class DeploymentLifecycleExpireDeployment3Command:
    """Inputs required to push registered model."""
    context: common_v1_context_pb2.RequestContext
    registered_model_audit_updated_by: str
    registered_model_address_locality: str


def to_deployment_lifecycle_expire_deployment3_command(
    command: DeploymentLifecycleExpireDeployment3Command
) -> modelregistry_v1_registered_model_sync_service_pb2.PushRegisteredModelRequest:
    return modelregistry_v1_registered_model_sync_service_pb2.PushRegisteredModelRequest(
        context=command.context,
        registered_model=modelregistry_v1_modelregistry_pb2.RegisteredModel(
            address=common_v1_address_pb2.PostalAddress(locality=command.registered_model_address_locality),
            audit=common_v1_audit_pb2.AuditInfo(updated_by=command.registered_model_audit_updated_by)
        )
    )


@dataclass(frozen=True, slots=True)
class DeploymentLifecycleReinstateDeployment0Command(ValidatedModel):
    """Inputs required to delegate lineage node approval."""
    context: common_v1_context_pb2.RequestContext
    lineage_node_children_children_manager_email: str
    details_approver_display_name: str
    lineage_node_children_manager_user_id: str
    details_approver_email: str


def to_deployment_lifecycle_reinstate_deployment0_command(
    command: DeploymentLifecycleReinstateDeployment0Command
) -> lineage_v1_lineage_node_approval_service_pb2.DelegateLineageNodeApprovalRequest:
    return lineage_v1_lineage_node_approval_service_pb2.DelegateLineageNodeApprovalRequest(
        context=command.context,
        details=lineage_v1_lineage_node_approval_service_pb2.DelegateLineageNodeApprovalRequest.Details(
            approver=identity_v1_refs_pb2.UserRef(
                display_name=command.details_approver_display_name,
                email=command.details_approver_email
            )
        ),
        lineage_node=lineage_v1_lineage_pb2.LineageNode(
            children=[
                lineage_v1_lineage_pb2.LineageNode(
                    children=[
                        lineage_v1_lineage_pb2.LineageNode(
                            manager=identity_v1_refs_pb2.UserRef(
                                email=command.lineage_node_children_children_manager_email
                            )
                        )
                    ],
                    manager=identity_v1_refs_pb2.UserRef(user_id=command.lineage_node_children_manager_user_id)
                )
            ]
        )
    )


@dataclass(frozen=True, slots=True)
class DeploymentReportingGenerateDeploymentReport0Command:
    """Inputs required to sync deployments."""
    context: common_v1_context_pb2.RequestContext
    deployment_participants_contact_email: str


def to_deployment_reporting_generate_deployment_report0_command(
    command: DeploymentReportingGenerateDeploymentReport0Command
) -> modelregistry_v1_deployment_sync_service_pb2.SyncDeploymentsRequest:
    return modelregistry_v1_deployment_sync_service_pb2.SyncDeploymentsRequest(
        context=command.context,
        deployment=modelregistry_v1_modelregistry_pb2.Deployment(
            participants=[
                modelregistry_v1_modelregistry_pb2.DeploymentParticipant(
                    contact=common_v1_contact_pb2.ContactInfo(email=command.deployment_participants_contact_email)
                )
            ]
        )
    )


@dataclass(frozen=True, slots=True)
class DeploymentReportingGenerateDeploymentReport1Command(ValidatedModel):
    """Inputs required to preview customer."""
    context: common_v1_context_pb2.RequestContext
    customer_audit_etag: str
    customer_relationship_manager_display_name: str
    customer_audit_updated_by: str


def to_deployment_reporting_generate_deployment_report1_command(
    command: DeploymentReportingGenerateDeploymentReport1Command
) -> customers_v1_customer_validation_service_pb2.PreviewCustomerRequest:
    return customers_v1_customer_validation_service_pb2.PreviewCustomerRequest(
        context=command.context,
        customer=customers_v1_customers_pb2.Customer(
            audit=common_v1_audit_pb2.AuditInfo(
                etag=command.customer_audit_etag,
                updated_by=command.customer_audit_updated_by
            ),
            relationship_manager=identity_v1_refs_pb2.UserRef(
                display_name=command.customer_relationship_manager_display_name
            )
        )
    )


@dataclass(frozen=True, slots=True)
class DeploymentSyncPushDeployment1Command(ValidatedModel):
    """Inputs required to sync registered models."""
    context: common_v1_context_pb2.RequestContext
    registered_model_audit_etag: str
    registered_model_audit_updated_by: str
    registered_model_address_country_code: str


def to_deployment_sync_push_deployment1_command(
    command: DeploymentSyncPushDeployment1Command
) -> modelregistry_v1_registered_model_sync_service_pb2.SyncRegisteredModelsRequest:
    return modelregistry_v1_registered_model_sync_service_pb2.SyncRegisteredModelsRequest(
        context=command.context,
        registered_model=modelregistry_v1_modelregistry_pb2.RegisteredModel(
            address=common_v1_address_pb2.PostalAddress(country_code=command.registered_model_address_country_code),
            audit=common_v1_audit_pb2.AuditInfo(
                etag=command.registered_model_audit_etag,
                updated_by=command.registered_model_audit_updated_by
            )
        )
    )


@dataclass(frozen=True, slots=True)
class DeploymentValidationExplainDeploymentDecision1Command:
    """Inputs required to lint venues."""
    context: common_v1_context_pb2.RequestContext
    details_contact_email: str
    venue_address_locality: str


def to_deployment_validation_explain_deployment_decision1_command(
    command: DeploymentValidationExplainDeploymentDecision1Command
) -> venues_v1_venue_validation_service_pb2.LintVenuesRequest:
    return venues_v1_venue_validation_service_pb2.LintVenuesRequest(
        context=command.context,
        details=venues_v1_venue_validation_service_pb2.LintVenuesRequest.Details(
            contact=common_v1_contact_pb2.ContactInfo(email=command.details_contact_email)
        ),
        venue=venues_v1_venues_pb2.Venue(
            address=common_v1_address_pb2.PostalAddress(locality=command.venue_address_locality)
        )
    )


@dataclass(frozen=True, slots=True)
class DeploymentWorkflowPauseDeploymentWorkflow3Command(ValidatedModel):
    """Inputs required to reconcile registered models."""
    context: common_v1_context_pb2.RequestContext
    registered_model_address_region: str
    registered_model_owner_display_name: str
    registered_model_owner_user_id: str
    registered_model_audit_updated_at: timestamp_pb2.Timestamp


def to_deployment_workflow_pause_deployment_workflow3_command(
    command: DeploymentWorkflowPauseDeploymentWorkflow3Command
) -> modelregistry_v1_registered_model_sync_service_pb2.ReconcileRegisteredModelsRequest:
    return modelregistry_v1_registered_model_sync_service_pb2.ReconcileRegisteredModelsRequest(
        context=command.context,
        registered_model=modelregistry_v1_modelregistry_pb2.RegisteredModel(
            address=common_v1_address_pb2.PostalAddress(region=command.registered_model_address_region),
            audit=common_v1_audit_pb2.AuditInfo(updated_at=command.registered_model_audit_updated_at),
            owner=identity_v1_refs_pb2.UserRef(
                display_name=command.registered_model_owner_display_name,
                user_id=command.registered_model_owner_user_id
            )
        )
    )


@dataclass(frozen=True, slots=True)
class ModelVersionLifecycleActivateModelVersion3Command:
    """Inputs required to validate deployment import."""
    context: common_v1_context_pb2.RequestContext
    deployment_participants_contact_phone: str


def to_model_version_lifecycle_activate_model_version3_command(
    command: ModelVersionLifecycleActivateModelVersion3Command
) -> modelregistry_v1_deployment_import_service_pb2.ValidateDeploymentImportRequest:
    return modelregistry_v1_deployment_import_service_pb2.ValidateDeploymentImportRequest(
        context=command.context,
        deployment=modelregistry_v1_modelregistry_pb2.Deployment(
            participants=[
                modelregistry_v1_modelregistry_pb2.DeploymentParticipant(
                    contact=common_v1_contact_pb2.ContactInfo(phone=command.deployment_participants_contact_phone)
                )
            ]
        )
    )


@dataclass(frozen=True, slots=True)
class ModelVersionReportingShareModelVersionReport2Command:
    """Inputs required to validate registered model."""
    context: common_v1_context_pb2.RequestContext
    registered_model_address_postal_code: str
    registered_model_audit_created_at: timestamp_pb2.Timestamp
    details_contact_name: common_v1_contact_pb2.PersonName
    registered_model_audit_updated_at: timestamp_pb2.Timestamp


def to_model_version_reporting_share_model_version_report2_command(
    command: ModelVersionReportingShareModelVersionReport2Command
) -> modelregistry_v1_registered_model_validation_service_pb2.ValidateRegisteredModelRequest:
    return modelregistry_v1_registered_model_validation_service_pb2.ValidateRegisteredModelRequest(
        context=command.context,
        details=modelregistry_v1_registered_model_validation_service_pb2.ValidateRegisteredModelRequest.Details(
            contact=common_v1_contact_pb2.ContactInfo(name=command.details_contact_name)
        ),
        registered_model=modelregistry_v1_modelregistry_pb2.RegisteredModel(
            address=common_v1_address_pb2.PostalAddress(postal_code=command.registered_model_address_postal_code),
            audit=common_v1_audit_pb2.AuditInfo(
                created_at=command.registered_model_audit_created_at,
                updated_at=command.registered_model_audit_updated_at
            )
        )
    )


@dataclass(frozen=True, slots=True)
class ModelVersionSyncStreamModelVersionChanges1Command:
    """Inputs required to push entity."""
    context: common_v1_context_pb2.RequestContext
    entity_primary_address_recipient: str


def to_model_version_sync_stream_model_version_changes1_command(
    command: ModelVersionSyncStreamModelVersionChanges1Command
) -> featurestore_v1_entity_sync_service_pb2.PushEntityRequest:
    return featurestore_v1_entity_sync_service_pb2.PushEntityRequest(
        context=command.context,
        entity=featurestore_v1_featurestore_pb2.Entity(
            primary_address=common_v1_address_pb2.PostalAddress(recipient=command.entity_primary_address_recipient)
        )
    )


@dataclass(frozen=True, slots=True)
class ModelVersionSyncStreamModelVersionChanges2Command(ValidatedModel):
    """Inputs required to count registered models."""
    context: common_v1_context_pb2.RequestContext
    filter_region: str


def to_model_version_sync_stream_model_version_changes2_command(
    command: ModelVersionSyncStreamModelVersionChanges2Command
) -> modelregistry_v1_registered_model_query_service_pb2.CountRegisteredModelsRequest:
    return modelregistry_v1_registered_model_query_service_pb2.CountRegisteredModelsRequest(
        context=command.context,
        filter=modelregistry_v1_registered_model_query_service_pb2.CountRegisteredModelsRequest.Filter(
            region=command.filter_region
        )
    )


@dataclass(frozen=True, slots=True)
class RegisteredModelApprovalCommentRegisteredModelApproval1Command:
    """Inputs required to unsubscribe metric alert updates."""
    context: common_v1_context_pb2.RequestContext
    details_recipient_email: str


def to_registered_model_approval_comment_registered_model_approval1_command(
    command: RegisteredModelApprovalCommentRegisteredModelApproval1Command
) -> metrics_v1_metric_alert_notification_service_pb2.UnsubscribeMetricAlertUpdatesRequest:
    return metrics_v1_metric_alert_notification_service_pb2.UnsubscribeMetricAlertUpdatesRequest(
        context=command.context,
        details=metrics_v1_metric_alert_notification_service_pb2.UnsubscribeMetricAlertUpdatesRequest.Details(
            recipient=common_v1_contact_pb2.ContactInfo(email=command.details_recipient_email)
        )
    )


@dataclass(frozen=True, slots=True)
class RegisteredModelApprovalCommentRegisteredModelApproval2Command(ValidatedModel):
    """Inputs required to normalize document."""
    context: common_v1_context_pb2.RequestContext
    document_billing_address_recipient: str
    document_counterparty_display_name: str


def to_registered_model_approval_comment_registered_model_approval2_command(
    command: RegisteredModelApprovalCommentRegisteredModelApproval2Command
) -> documents_v1_document_validation_service_pb2.NormalizeDocumentRequest:
    return documents_v1_document_validation_service_pb2.NormalizeDocumentRequest(
        context=command.context,
        document=documents_v1_documents_pb2.Document(
            billing_address=common_v1_address_pb2.PostalAddress(recipient=command.document_billing_address_recipient),
            counterparty=documents_v1_refs_pb2.DocumentFolderRef(
                display_name=command.document_counterparty_display_name
            )
        )
    )


@dataclass(frozen=True, slots=True)
class RegisteredModelCalculationExplainRegisteredModelCalculation3Command:
    """Inputs required to simulate feature value."""
    context: common_v1_context_pb2.RequestContext
    details_destination_recipient: str
    feature_value_measurements_unit: str


def to_registered_model_calculation_explain_registered_model_calculation3_command(
    command: RegisteredModelCalculationExplainRegisteredModelCalculation3Command
) -> featurestore_v1_feature_value_calculation_service_pb2.SimulateFeatureValueRequest:
    return featurestore_v1_feature_value_calculation_service_pb2.SimulateFeatureValueRequest(
        context=command.context,
        details=featurestore_v1_feature_value_calculation_service_pb2.SimulateFeatureValueRequest.Details(
            destination=common_v1_address_pb2.PostalAddress(recipient=command.details_destination_recipient)
        ),
        feature_value=featurestore_v1_featurestore_pb2.FeatureValue(
            measurements=[
                featurestore_v1_featurestore_pb2.FeatureValueMeasurement(unit=command.feature_value_measurements_unit)
            ]
        )
    )


@dataclass(frozen=True, slots=True)
class RegisteredModelLifecycleRenewRegisteredModel1Command:
    """Inputs required to resolve users."""
    context: common_v1_context_pb2.RequestContext


def to_registered_model_lifecycle_renew_registered_model1_command(
    command: RegisteredModelLifecycleRenewRegisteredModel1Command
) -> identity_v1_user_query_service_pb2.ResolveUsersRequest:
    return identity_v1_user_query_service_pb2.ResolveUsersRequest(context=command.context)


@dataclass(frozen=True, slots=True)
class RegisteredModelCloneRegisteredModel1Command:
    """Inputs required to estimate feature view."""
    context: common_v1_context_pb2.RequestContext
    feature_view_dimensions_unit: str
    feature_view_audit_created_by: str


def to_registered_model_clone_registered_model1_command(
    command: RegisteredModelCloneRegisteredModel1Command
) -> featurestore_v1_feature_view_calculation_service_pb2.EstimateFeatureViewRequest:
    return featurestore_v1_feature_view_calculation_service_pb2.EstimateFeatureViewRequest(
        context=command.context,
        feature_view=featurestore_v1_featurestore_pb2.FeatureView(
            audit=common_v1_audit_pb2.AuditInfo(created_by=command.feature_view_audit_created_by),
            dimensions=featurestore_v1_featurestore_pb2.FeatureViewDimensions(unit=command.feature_view_dimensions_unit)
        )
    )


@dataclass(frozen=True, slots=True)
class RegisteredModelSyncReconcileRegisteredModels1Command:
    """Inputs required to calculate deployment."""
    context: common_v1_context_pb2.RequestContext
    deployment_participants_contact_email: str
    deployment_audit_created_at: timestamp_pb2.Timestamp


def to_registered_model_sync_reconcile_registered_models1_command(
    command: RegisteredModelSyncReconcileRegisteredModels1Command
) -> modelregistry_v1_deployment_calculation_service_pb2.CalculateDeploymentRequest:
    return modelregistry_v1_deployment_calculation_service_pb2.CalculateDeploymentRequest(
        context=command.context,
        deployment=modelregistry_v1_modelregistry_pb2.Deployment(
            audit=common_v1_audit_pb2.AuditInfo(created_at=command.deployment_audit_created_at),
            participants=[
                modelregistry_v1_modelregistry_pb2.DeploymentParticipant(
                    contact=common_v1_contact_pb2.ContactInfo(email=command.deployment_participants_contact_email)
                )
            ]
        )
    )


@dataclass(frozen=True, slots=True)
class RegisteredModelValidationPreviewRegisteredModel1Command:
    """Inputs required to simulate model version."""
    context: common_v1_context_pb2.RequestContext
    model_version_subject_display_name: str
    model_version_subject_email: str
    details_destination_locality: str
    model_version_measurements_unit: str


def to_registered_model_validation_preview_registered_model1_command(
    command: RegisteredModelValidationPreviewRegisteredModel1Command
) -> modelregistry_v1_model_version_calculation_service_pb2.SimulateModelVersionRequest:
    return modelregistry_v1_model_version_calculation_service_pb2.SimulateModelVersionRequest(
        context=command.context,
        details=modelregistry_v1_model_version_calculation_service_pb2.SimulateModelVersionRequest.Details(
            destination=common_v1_address_pb2.PostalAddress(locality=command.details_destination_locality)
        ),
        model_version=modelregistry_v1_modelregistry_pb2.ModelVersion(
            measurements=[
                modelregistry_v1_modelregistry_pb2.ModelVersionMeasurement(unit=command.model_version_measurements_unit)
            ],
            subject=customers_v1_refs_pb2.CustomerRef(
                display_name=command.model_version_subject_display_name,
                email=command.model_version_subject_email
            )
        )
    )


@dataclass(frozen=True, slots=True)
class RegisteredModelValidationScoreRegisteredModel0Command(ValidatedModel):
    """Inputs required to preview entity."""
    context: common_v1_context_pb2.RequestContext
    entity_primary_address_country_code: str
    entity_primary_address_region: str


def to_registered_model_validation_score_registered_model0_command(
    command: RegisteredModelValidationScoreRegisteredModel0Command
) -> featurestore_v1_entity_validation_service_pb2.PreviewEntityRequest:
    return featurestore_v1_entity_validation_service_pb2.PreviewEntityRequest(
        context=command.context,
        entity=featurestore_v1_featurestore_pb2.Entity(
            primary_address=common_v1_address_pb2.PostalAddress(
                country_code=command.entity_primary_address_country_code,
                region=command.entity_primary_address_region
            )
        )
    )


@dataclass(frozen=True, slots=True)
class RegisteredModelWorkflowSignalRegisteredModelWorkflow3Command(ValidatedModel):
    """Inputs required to recall model version."""
    context: common_v1_context_pb2.RequestContext
    model_version_subject_display_name: str


def to_registered_model_workflow_signal_registered_model_workflow3_command(
    command: RegisteredModelWorkflowSignalRegisteredModelWorkflow3Command
) -> modelregistry_v1_model_version_approval_service_pb2.RecallModelVersionRequest:
    return modelregistry_v1_model_version_approval_service_pb2.RecallModelVersionRequest(
        context=command.context,
        model_version=modelregistry_v1_modelregistry_pb2.ModelVersion(
            subject=customers_v1_refs_pb2.CustomerRef(display_name=command.model_version_subject_display_name)
        )
    )
