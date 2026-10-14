"""Register and compose every service of the modelregistry domain."""

from __future__ import annotations

import grpc

from acme.admissions.v1 import admission_query_service_pb2_grpc as admissions_v1_admission_query_service_pb2_grpc
from acme.anomalies.v1 import anomaly_approval_service_pb2_grpc as anomalies_v1_anomaly_approval_service_pb2_grpc
from acme.anomalies.v1 import (
    anomaly_feedback_approval_service_pb2_grpc as anomalies_v1_anomaly_feedback_approval_service_pb2_grpc,
)
from acme.anomalies.v1 import (
    anomaly_feedback_calculation_service_pb2_grpc as anomalies_v1_anomaly_feedback_calculation_service_pb2_grpc,
)
from acme.anomalies.v1 import (
    anomaly_feedback_workflow_service_pb2_grpc as anomalies_v1_anomaly_feedback_workflow_service_pb2_grpc,
)
from acme.anomalies.v1 import anomaly_validation_service_pb2_grpc as anomalies_v1_anomaly_validation_service_pb2_grpc
from acme.anomalies.v1 import anomaly_workflow_service_pb2_grpc as anomalies_v1_anomaly_workflow_service_pb2_grpc
from acme.anomalies.v1 import detector_query_service_pb2_grpc as anomalies_v1_detector_query_service_pb2_grpc
from acme.audit.v1 import audit_event_query_service_pb2_grpc as audit_v1_audit_event_query_service_pb2_grpc
from acme.audit.v1 import audit_event_service_pb2_grpc as audit_v1_audit_event_service_pb2_grpc
from acme.audit.v1 import audit_event_validation_service_pb2_grpc as audit_v1_audit_event_validation_service_pb2_grpc
from acme.authorization.v1 import access_policy_service_pb2_grpc as authorization_v1_access_policy_service_pb2_grpc
from acme.authorization.v1 import (
    access_policy_validation_service_pb2_grpc as authorization_v1_access_policy_validation_service_pb2_grpc,
)
from acme.banking.v1 import bank_account_query_service_pb2_grpc as banking_v1_bank_account_query_service_pb2_grpc
from acme.budgeting.v1 import budget_query_service_pb2_grpc as budgeting_v1_budget_query_service_pb2_grpc
from acme.cart.v1 import cart_query_service_pb2_grpc as cart_v1_cart_query_service_pb2_grpc
from acme.certificates.v1 import (
    certificate_calculation_service_pb2_grpc as certificates_v1_certificate_calculation_service_pb2_grpc,
)
from acme.community.v1 import forum_query_service_pb2_grpc as community_v1_forum_query_service_pb2_grpc
from acme.concessions.v1 import concession_stand_service_pb2_grpc as concessions_v1_concession_stand_service_pb2_grpc
from acme.customers.v1 import (
    consent_record_calculation_service_pb2_grpc as customers_v1_consent_record_calculation_service_pb2_grpc,
)
from acme.customers.v1 import (
    consent_record_validation_service_pb2_grpc as customers_v1_consent_record_validation_service_pb2_grpc,
)
from acme.customers.v1 import (
    customer_calculation_service_pb2_grpc as customers_v1_customer_calculation_service_pb2_grpc,
)
from acme.customers.v1 import customer_query_service_pb2_grpc as customers_v1_customer_query_service_pb2_grpc
from acme.customers.v1 import (
    customer_segment_calculation_service_pb2_grpc as customers_v1_customer_segment_calculation_service_pb2_grpc,
)
from acme.customers.v1 import (
    customer_segment_validation_service_pb2_grpc as customers_v1_customer_segment_validation_service_pb2_grpc,
)
from acme.customers.v1 import customer_service_pb2_grpc as customers_v1_customer_service_pb2_grpc
from acme.customers.v1 import customer_validation_service_pb2_grpc as customers_v1_customer_validation_service_pb2_grpc
from acme.customers.v1 import (
    household_calculation_service_pb2_grpc as customers_v1_household_calculation_service_pb2_grpc,
)
from acme.customers.v1 import household_query_service_pb2_grpc as customers_v1_household_query_service_pb2_grpc
from acme.customers.v1 import (
    household_validation_service_pb2_grpc as customers_v1_household_validation_service_pb2_grpc,
)
from acme.customers.v1 import (
    preference_calculation_service_pb2_grpc as customers_v1_preference_calculation_service_pb2_grpc,
)
from acme.customers.v1 import (
    preference_validation_service_pb2_grpc as customers_v1_preference_validation_service_pb2_grpc,
)
from acme.documents.v1 import document_service_pb2_grpc as documents_v1_document_service_pb2_grpc
from acme.documents.v1 import document_validation_service_pb2_grpc as documents_v1_document_validation_service_pb2_grpc
from acme.featureflags.v1 import feature_flag_service_pb2_grpc as featureflags_v1_feature_flag_service_pb2_grpc
from acme.featureflags.v1 import (
    feature_flag_validation_service_pb2_grpc as featureflags_v1_feature_flag_validation_service_pb2_grpc,
)
from acme.featurestore.v1 import entity_approval_service_pb2_grpc as featurestore_v1_entity_approval_service_pb2_grpc
from acme.featurestore.v1 import (
    entity_calculation_service_pb2_grpc as featurestore_v1_entity_calculation_service_pb2_grpc,
)
from acme.featurestore.v1 import entity_lifecycle_service_pb2_grpc as featurestore_v1_entity_lifecycle_service_pb2_grpc
from acme.featurestore.v1 import entity_reporting_service_pb2_grpc as featurestore_v1_entity_reporting_service_pb2_grpc
from acme.featurestore.v1 import entity_sync_service_pb2_grpc as featurestore_v1_entity_sync_service_pb2_grpc
from acme.featurestore.v1 import (
    entity_validation_service_pb2_grpc as featurestore_v1_entity_validation_service_pb2_grpc,
)
from acme.featurestore.v1 import (
    feature_value_approval_service_pb2_grpc as featurestore_v1_feature_value_approval_service_pb2_grpc,
)
from acme.featurestore.v1 import (
    feature_value_calculation_service_pb2_grpc as featurestore_v1_feature_value_calculation_service_pb2_grpc,
)
from acme.featurestore.v1 import (
    feature_value_import_service_pb2_grpc as featurestore_v1_feature_value_import_service_pb2_grpc,
)
from acme.featurestore.v1 import (
    feature_value_query_service_pb2_grpc as featurestore_v1_feature_value_query_service_pb2_grpc,
)
from acme.featurestore.v1 import (
    feature_value_sync_service_pb2_grpc as featurestore_v1_feature_value_sync_service_pb2_grpc,
)
from acme.featurestore.v1 import (
    feature_value_validation_service_pb2_grpc as featurestore_v1_feature_value_validation_service_pb2_grpc,
)
from acme.featurestore.v1 import (
    feature_view_approval_service_pb2_grpc as featurestore_v1_feature_view_approval_service_pb2_grpc,
)
from acme.featurestore.v1 import (
    feature_view_calculation_service_pb2_grpc as featurestore_v1_feature_view_calculation_service_pb2_grpc,
)
from acme.featurestore.v1 import (
    feature_view_query_service_pb2_grpc as featurestore_v1_feature_view_query_service_pb2_grpc,
)
from acme.featurestore.v1 import feature_view_service_pb2_grpc as featurestore_v1_feature_view_service_pb2_grpc
from acme.featurestore.v1 import (
    feature_view_sync_service_pb2_grpc as featurestore_v1_feature_view_sync_service_pb2_grpc,
)
from acme.featurestore.v1 import (
    feature_view_validation_service_pb2_grpc as featurestore_v1_feature_view_validation_service_pb2_grpc,
)
from acme.featurestore.v1 import (
    feature_view_workflow_service_pb2_grpc as featurestore_v1_feature_view_workflow_service_pb2_grpc,
)
from acme.identity.v1 import user_query_service_pb2_grpc as identity_v1_user_query_service_pb2_grpc
from acme.identity.v1 import user_service_pb2_grpc as identity_v1_user_service_pb2_grpc
from acme.identity.v1 import user_validation_service_pb2_grpc as identity_v1_user_validation_service_pb2_grpc
from acme.ledger.v1 import ledger_account_query_service_pb2_grpc as ledger_v1_ledger_account_query_service_pb2_grpc
from acme.ledger.v1 import ledger_account_service_pb2_grpc as ledger_v1_ledger_account_service_pb2_grpc
from acme.lineage.v1 import impact_approval_service_pb2_grpc as lineage_v1_impact_approval_service_pb2_grpc
from acme.lineage.v1 import impact_sync_service_pb2_grpc as lineage_v1_impact_sync_service_pb2_grpc
from acme.lineage.v1 import impact_workflow_service_pb2_grpc as lineage_v1_impact_workflow_service_pb2_grpc
from acme.lineage.v1 import lineage_edge_approval_service_pb2_grpc as lineage_v1_lineage_edge_approval_service_pb2_grpc
from acme.lineage.v1 import lineage_edge_import_service_pb2_grpc as lineage_v1_lineage_edge_import_service_pb2_grpc
from acme.lineage.v1 import lineage_edge_sync_service_pb2_grpc as lineage_v1_lineage_edge_sync_service_pb2_grpc
from acme.lineage.v1 import lineage_edge_workflow_service_pb2_grpc as lineage_v1_lineage_edge_workflow_service_pb2_grpc
from acme.lineage.v1 import lineage_node_approval_service_pb2_grpc as lineage_v1_lineage_node_approval_service_pb2_grpc
from acme.lineage.v1 import (
    lineage_node_calculation_service_pb2_grpc as lineage_v1_lineage_node_calculation_service_pb2_grpc,
)
from acme.lineage.v1 import lineage_node_query_service_pb2_grpc as lineage_v1_lineage_node_query_service_pb2_grpc
from acme.lineage.v1 import (
    lineage_node_reporting_service_pb2_grpc as lineage_v1_lineage_node_reporting_service_pb2_grpc,
)
from acme.lineage.v1 import lineage_node_sync_service_pb2_grpc as lineage_v1_lineage_node_sync_service_pb2_grpc
from acme.lineage.v1 import lineage_node_workflow_service_pb2_grpc as lineage_v1_lineage_node_workflow_service_pb2_grpc
from acme.maintenance.v1 import work_order_query_service_pb2_grpc as maintenance_v1_work_order_query_service_pb2_grpc
from acme.metrics.v1 import dashboard_export_service_pb2_grpc as metrics_v1_dashboard_export_service_pb2_grpc
from acme.metrics.v1 import dashboard_history_service_pb2_grpc as metrics_v1_dashboard_history_service_pb2_grpc
from acme.metrics.v1 import dashboard_sync_service_pb2_grpc as metrics_v1_dashboard_sync_service_pb2_grpc
from acme.metrics.v1 import dashboard_validation_service_pb2_grpc as metrics_v1_dashboard_validation_service_pb2_grpc
from acme.metrics.v1 import metric_alert_admin_service_pb2_grpc as metrics_v1_metric_alert_admin_service_pb2_grpc
from acme.metrics.v1 import (
    metric_alert_notification_service_pb2_grpc as metrics_v1_metric_alert_notification_service_pb2_grpc,
)
from acme.metrics.v1 import metric_alert_query_service_pb2_grpc as metrics_v1_metric_alert_query_service_pb2_grpc
from acme.metrics.v1 import (
    metric_alert_validation_service_pb2_grpc as metrics_v1_metric_alert_validation_service_pb2_grpc,
)
from acme.metrics.v1 import metric_series_admin_service_pb2_grpc as metrics_v1_metric_series_admin_service_pb2_grpc
from acme.metrics.v1 import metric_series_export_service_pb2_grpc as metrics_v1_metric_series_export_service_pb2_grpc
from acme.metrics.v1 import metric_series_history_service_pb2_grpc as metrics_v1_metric_series_history_service_pb2_grpc
from acme.metrics.v1 import metric_series_query_service_pb2_grpc as metrics_v1_metric_series_query_service_pb2_grpc
from acme.metrics.v1 import (
    metric_series_validation_service_pb2_grpc as metrics_v1_metric_series_validation_service_pb2_grpc,
)
from acme.modelregistry.v1 import (
    deployment_approval_service_pb2_grpc as modelregistry_v1_deployment_approval_service_pb2_grpc,
)
from acme.modelregistry.v1 import (
    deployment_calculation_service_pb2_grpc as modelregistry_v1_deployment_calculation_service_pb2_grpc,
)
from acme.modelregistry.v1 import (
    deployment_import_service_pb2_grpc as modelregistry_v1_deployment_import_service_pb2_grpc,
)
from acme.modelregistry.v1 import (
    deployment_lifecycle_service_pb2_grpc as modelregistry_v1_deployment_lifecycle_service_pb2_grpc,
)
from acme.modelregistry.v1 import (
    deployment_reporting_service_pb2_grpc as modelregistry_v1_deployment_reporting_service_pb2_grpc,
)
from acme.modelregistry.v1 import deployment_sync_service_pb2_grpc as modelregistry_v1_deployment_sync_service_pb2_grpc
from acme.modelregistry.v1 import (
    deployment_validation_service_pb2_grpc as modelregistry_v1_deployment_validation_service_pb2_grpc,
)
from acme.modelregistry.v1 import (
    deployment_workflow_service_pb2_grpc as modelregistry_v1_deployment_workflow_service_pb2_grpc,
)
from acme.modelregistry.v1 import (
    model_version_approval_service_pb2_grpc as modelregistry_v1_model_version_approval_service_pb2_grpc,
)
from acme.modelregistry.v1 import (
    model_version_calculation_service_pb2_grpc as modelregistry_v1_model_version_calculation_service_pb2_grpc,
)
from acme.modelregistry.v1 import (
    model_version_lifecycle_service_pb2_grpc as modelregistry_v1_model_version_lifecycle_service_pb2_grpc,
)
from acme.modelregistry.v1 import (
    model_version_query_service_pb2_grpc as modelregistry_v1_model_version_query_service_pb2_grpc,
)
from acme.modelregistry.v1 import (
    model_version_reporting_service_pb2_grpc as modelregistry_v1_model_version_reporting_service_pb2_grpc,
)
from acme.modelregistry.v1 import (
    model_version_sync_service_pb2_grpc as modelregistry_v1_model_version_sync_service_pb2_grpc,
)
from acme.modelregistry.v1 import (
    model_version_validation_service_pb2_grpc as modelregistry_v1_model_version_validation_service_pb2_grpc,
)
from acme.modelregistry.v1 import (
    model_version_workflow_service_pb2_grpc as modelregistry_v1_model_version_workflow_service_pb2_grpc,
)
from acme.modelregistry.v1 import (
    registered_model_approval_service_pb2_grpc as modelregistry_v1_registered_model_approval_service_pb2_grpc,
)
from acme.modelregistry.v1 import (
    registered_model_calculation_service_pb2_grpc as modelregistry_v1_registered_model_calculation_service_pb2_grpc,
)
from acme.modelregistry.v1 import (
    registered_model_lifecycle_service_pb2_grpc as modelregistry_v1_registered_model_lifecycle_service_pb2_grpc,
)
from acme.modelregistry.v1 import (
    registered_model_query_service_pb2_grpc as modelregistry_v1_registered_model_query_service_pb2_grpc,
)
from acme.modelregistry.v1 import (
    registered_model_reporting_service_pb2_grpc as modelregistry_v1_registered_model_reporting_service_pb2_grpc,
)
from acme.modelregistry.v1 import (
    registered_model_service_pb2_grpc as modelregistry_v1_registered_model_service_pb2_grpc,
)
from acme.modelregistry.v1 import (
    registered_model_sync_service_pb2_grpc as modelregistry_v1_registered_model_sync_service_pb2_grpc,
)
from acme.modelregistry.v1 import (
    registered_model_validation_service_pb2_grpc as modelregistry_v1_registered_model_validation_service_pb2_grpc,
)
from acme.modelregistry.v1 import (
    registered_model_workflow_service_pb2_grpc as modelregistry_v1_registered_model_workflow_service_pb2_grpc,
)
from acme.notifications.v1 import (
    notification_query_service_pb2_grpc as notifications_v1_notification_query_service_pb2_grpc,
)
from acme.notifications.v1 import notification_service_pb2_grpc as notifications_v1_notification_service_pb2_grpc
from acme.patients.v1 import patient_service_pb2_grpc as patients_v1_patient_service_pb2_grpc
from acme.search.v1 import search_index_service_pb2_grpc as search_v1_search_index_service_pb2_grpc
from acme.search.v1 import (
    search_index_validation_service_pb2_grpc as search_v1_search_index_validation_service_pb2_grpc,
)
from acme.seating.v1 import seat_map_service_pb2_grpc as seating_v1_seat_map_service_pb2_grpc
from acme.secrets.v1 import secret_query_service_pb2_grpc as secrets_v1_secret_query_service_pb2_grpc
from acme.sponsorships.v1 import sponsor_query_service_pb2_grpc as sponsorships_v1_sponsor_query_service_pb2_grpc
from acme.ticketing.v1 import ticket_service_pb2_grpc as ticketing_v1_ticket_service_pb2_grpc
from acme.venues.v1 import venue_validation_service_pb2_grpc as venues_v1_venue_validation_service_pb2_grpc

from acme_data.domains.modelregistry.dependencies import Clients
from acme_data.domains.modelregistry.dependencies import Dependencies
from acme_data.domains.modelregistry.deployment_approval_service import DeploymentApprovalServicer
from acme_data.domains.modelregistry.deployment_calculation_service import DeploymentCalculationServicer
from acme_data.domains.modelregistry.deployment_import_service import DeploymentImportServicer
from acme_data.domains.modelregistry.deployment_lifecycle_service import DeploymentLifecycleServicer
from acme_data.domains.modelregistry.deployment_reporting_service import DeploymentReportingServicer
from acme_data.domains.modelregistry.deployment_sync_service import DeploymentSyncServicer
from acme_data.domains.modelregistry.deployment_validation_service import DeploymentValidationServicer
from acme_data.domains.modelregistry.deployment_workflow_service import DeploymentWorkflowServicer
from acme_data.domains.modelregistry.events import subscribe
from acme_data.domains.modelregistry.model_version_approval_service import ModelVersionApprovalServicer
from acme_data.domains.modelregistry.model_version_calculation_service import ModelVersionCalculationServicer
from acme_data.domains.modelregistry.model_version_lifecycle_service import ModelVersionLifecycleServicer
from acme_data.domains.modelregistry.model_version_query_service import ModelVersionQueryServicer
from acme_data.domains.modelregistry.model_version_reporting_service import ModelVersionReportingServicer
from acme_data.domains.modelregistry.model_version_sync_service import ModelVersionSyncServicer
from acme_data.domains.modelregistry.model_version_validation_service import ModelVersionValidationServicer
from acme_data.domains.modelregistry.model_version_workflow_service import ModelVersionWorkflowServicer
from acme_data.domains.modelregistry.registered_model_approval_service import RegisteredModelApprovalServicer
from acme_data.domains.modelregistry.registered_model_calculation_service import RegisteredModelCalculationServicer
from acme_data.domains.modelregistry.registered_model_lifecycle_service import RegisteredModelLifecycleServicer
from acme_data.domains.modelregistry.registered_model_query_service import RegisteredModelQueryServicer
from acme_data.domains.modelregistry.registered_model_reporting_service import RegisteredModelReportingServicer
from acme_data.domains.modelregistry.registered_model_service import RegisteredModelServicer
from acme_data.domains.modelregistry.registered_model_sync_service import RegisteredModelSyncServicer
from acme_data.domains.modelregistry.registered_model_validation_service import RegisteredModelValidationServicer
from acme_data.domains.modelregistry.registered_model_workflow_service import RegisteredModelWorkflowServicer
from acme_data.domains.modelregistry.repository import DomainRepository
from acme_data.platform.container import Container
from acme_data.platform.container import Factory


def dependencies(container: Container) -> Dependencies:
    admissions_admission_query = container.singleton(
        admissions_v1_admission_query_service_pb2_grpc.AdmissionQueryServiceStub,
        lambda: admissions_v1_admission_query_service_pb2_grpc.AdmissionQueryServiceStub(container.channel)
    )
    anomalies_anomaly_approval = container.singleton(
        anomalies_v1_anomaly_approval_service_pb2_grpc.AnomalyApprovalServiceStub,
        lambda: anomalies_v1_anomaly_approval_service_pb2_grpc.AnomalyApprovalServiceStub(container.channel)
    )
    anomalies_anomaly_feedback_approval = container.singleton(
        anomalies_v1_anomaly_feedback_approval_service_pb2_grpc.AnomalyFeedbackApprovalServiceStub,
        lambda: anomalies_v1_anomaly_feedback_approval_service_pb2_grpc.AnomalyFeedbackApprovalServiceStub(
            container.channel
        )
    )
    anomalies_anomaly_feedback_calculation = container.singleton(
        anomalies_v1_anomaly_feedback_calculation_service_pb2_grpc.AnomalyFeedbackCalculationServiceStub,
        lambda: anomalies_v1_anomaly_feedback_calculation_service_pb2_grpc.AnomalyFeedbackCalculationServiceStub(
            container.channel
        )
    )
    anomalies_anomaly_feedback_workflow = container.singleton(
        anomalies_v1_anomaly_feedback_workflow_service_pb2_grpc.AnomalyFeedbackWorkflowServiceStub,
        lambda: anomalies_v1_anomaly_feedback_workflow_service_pb2_grpc.AnomalyFeedbackWorkflowServiceStub(
            container.channel
        )
    )
    anomalies_anomaly_validation = container.singleton(
        anomalies_v1_anomaly_validation_service_pb2_grpc.AnomalyValidationServiceStub,
        lambda: anomalies_v1_anomaly_validation_service_pb2_grpc.AnomalyValidationServiceStub(container.channel)
    )
    anomalies_anomaly_workflow = container.singleton(
        anomalies_v1_anomaly_workflow_service_pb2_grpc.AnomalyWorkflowServiceStub,
        lambda: anomalies_v1_anomaly_workflow_service_pb2_grpc.AnomalyWorkflowServiceStub(container.channel)
    )
    anomalies_detector_query = container.singleton(
        anomalies_v1_detector_query_service_pb2_grpc.DetectorQueryServiceStub,
        lambda: anomalies_v1_detector_query_service_pb2_grpc.DetectorQueryServiceStub(container.channel)
    )
    audit_audit_event_query = container.singleton(
        audit_v1_audit_event_query_service_pb2_grpc.AuditEventQueryServiceStub,
        lambda: audit_v1_audit_event_query_service_pb2_grpc.AuditEventQueryServiceStub(container.channel)
    )
    audit_audit_event = container.singleton(
        audit_v1_audit_event_service_pb2_grpc.AuditEventServiceStub,
        lambda: audit_v1_audit_event_service_pb2_grpc.AuditEventServiceStub(container.channel)
    )
    audit_audit_event_validation = container.singleton(
        audit_v1_audit_event_validation_service_pb2_grpc.AuditEventValidationServiceStub,
        lambda: audit_v1_audit_event_validation_service_pb2_grpc.AuditEventValidationServiceStub(container.channel)
    )
    authorization_access_policy = container.singleton(
        authorization_v1_access_policy_service_pb2_grpc.AccessPolicyServiceStub,
        lambda: authorization_v1_access_policy_service_pb2_grpc.AccessPolicyServiceStub(container.channel)
    )
    authorization_access_policy_validation = container.singleton(
        authorization_v1_access_policy_validation_service_pb2_grpc.AccessPolicyValidationServiceStub,
        lambda: authorization_v1_access_policy_validation_service_pb2_grpc.AccessPolicyValidationServiceStub(
            container.channel
        )
    )
    banking_bank_account_query = container.singleton(
        banking_v1_bank_account_query_service_pb2_grpc.BankAccountQueryServiceStub,
        lambda: banking_v1_bank_account_query_service_pb2_grpc.BankAccountQueryServiceStub(container.channel)
    )
    budgeting_budget_query = container.singleton(
        budgeting_v1_budget_query_service_pb2_grpc.BudgetQueryServiceStub,
        lambda: budgeting_v1_budget_query_service_pb2_grpc.BudgetQueryServiceStub(container.channel)
    )
    cart_cart_query = container.singleton(
        cart_v1_cart_query_service_pb2_grpc.CartQueryServiceStub,
        lambda: cart_v1_cart_query_service_pb2_grpc.CartQueryServiceStub(container.channel)
    )
    certificates_certificate_calculation = container.singleton(
        certificates_v1_certificate_calculation_service_pb2_grpc.CertificateCalculationServiceStub,
        lambda: certificates_v1_certificate_calculation_service_pb2_grpc.CertificateCalculationServiceStub(
            container.channel
        )
    )
    community_forum_query = container.singleton(
        community_v1_forum_query_service_pb2_grpc.ForumQueryServiceStub,
        lambda: community_v1_forum_query_service_pb2_grpc.ForumQueryServiceStub(container.channel)
    )
    concessions_concession_stand = container.singleton(
        concessions_v1_concession_stand_service_pb2_grpc.ConcessionStandServiceStub,
        lambda: concessions_v1_concession_stand_service_pb2_grpc.ConcessionStandServiceStub(container.channel)
    )
    customers_consent_record_calculation = container.singleton(
        customers_v1_consent_record_calculation_service_pb2_grpc.ConsentRecordCalculationServiceStub,
        lambda: customers_v1_consent_record_calculation_service_pb2_grpc.ConsentRecordCalculationServiceStub(
            container.channel
        )
    )
    customers_consent_record_validation = container.singleton(
        customers_v1_consent_record_validation_service_pb2_grpc.ConsentRecordValidationServiceStub,
        lambda: customers_v1_consent_record_validation_service_pb2_grpc.ConsentRecordValidationServiceStub(
            container.channel
        )
    )
    customers_customer_calculation = container.singleton(
        customers_v1_customer_calculation_service_pb2_grpc.CustomerCalculationServiceStub,
        lambda: customers_v1_customer_calculation_service_pb2_grpc.CustomerCalculationServiceStub(container.channel)
    )
    customers_customer_query = container.singleton(
        customers_v1_customer_query_service_pb2_grpc.CustomerQueryServiceStub,
        lambda: customers_v1_customer_query_service_pb2_grpc.CustomerQueryServiceStub(container.channel)
    )
    customers_customer_segment_calculation = container.singleton(
        customers_v1_customer_segment_calculation_service_pb2_grpc.CustomerSegmentCalculationServiceStub,
        lambda: customers_v1_customer_segment_calculation_service_pb2_grpc.CustomerSegmentCalculationServiceStub(
            container.channel
        )
    )
    customers_customer_segment_validation = container.singleton(
        customers_v1_customer_segment_validation_service_pb2_grpc.CustomerSegmentValidationServiceStub,
        lambda: customers_v1_customer_segment_validation_service_pb2_grpc.CustomerSegmentValidationServiceStub(
            container.channel
        )
    )
    customers_customer = container.singleton(
        customers_v1_customer_service_pb2_grpc.CustomerServiceStub,
        lambda: customers_v1_customer_service_pb2_grpc.CustomerServiceStub(container.channel)
    )
    customers_customer_validation = container.singleton(
        customers_v1_customer_validation_service_pb2_grpc.CustomerValidationServiceStub,
        lambda: customers_v1_customer_validation_service_pb2_grpc.CustomerValidationServiceStub(container.channel)
    )
    customers_household_calculation = container.singleton(
        customers_v1_household_calculation_service_pb2_grpc.HouseholdCalculationServiceStub,
        lambda: customers_v1_household_calculation_service_pb2_grpc.HouseholdCalculationServiceStub(container.channel)
    )
    customers_household_query = container.singleton(
        customers_v1_household_query_service_pb2_grpc.HouseholdQueryServiceStub,
        lambda: customers_v1_household_query_service_pb2_grpc.HouseholdQueryServiceStub(container.channel)
    )
    customers_household_validation = container.singleton(
        customers_v1_household_validation_service_pb2_grpc.HouseholdValidationServiceStub,
        lambda: customers_v1_household_validation_service_pb2_grpc.HouseholdValidationServiceStub(container.channel)
    )
    customers_preference_calculation = container.singleton(
        customers_v1_preference_calculation_service_pb2_grpc.PreferenceCalculationServiceStub,
        lambda: customers_v1_preference_calculation_service_pb2_grpc.PreferenceCalculationServiceStub(container.channel)
    )
    customers_preference_validation = container.singleton(
        customers_v1_preference_validation_service_pb2_grpc.PreferenceValidationServiceStub,
        lambda: customers_v1_preference_validation_service_pb2_grpc.PreferenceValidationServiceStub(container.channel)
    )
    documents_document = container.singleton(
        documents_v1_document_service_pb2_grpc.DocumentServiceStub,
        lambda: documents_v1_document_service_pb2_grpc.DocumentServiceStub(container.channel)
    )
    documents_document_validation = container.singleton(
        documents_v1_document_validation_service_pb2_grpc.DocumentValidationServiceStub,
        lambda: documents_v1_document_validation_service_pb2_grpc.DocumentValidationServiceStub(container.channel)
    )
    featureflags_feature_flag = container.singleton(
        featureflags_v1_feature_flag_service_pb2_grpc.FeatureFlagServiceStub,
        lambda: featureflags_v1_feature_flag_service_pb2_grpc.FeatureFlagServiceStub(container.channel)
    )
    featureflags_feature_flag_validation = container.singleton(
        featureflags_v1_feature_flag_validation_service_pb2_grpc.FeatureFlagValidationServiceStub,
        lambda: featureflags_v1_feature_flag_validation_service_pb2_grpc.FeatureFlagValidationServiceStub(
            container.channel
        )
    )
    featurestore_entity_approval = container.singleton(
        featurestore_v1_entity_approval_service_pb2_grpc.EntityApprovalServiceStub,
        lambda: featurestore_v1_entity_approval_service_pb2_grpc.EntityApprovalServiceStub(container.channel)
    )
    featurestore_entity_calculation = container.singleton(
        featurestore_v1_entity_calculation_service_pb2_grpc.EntityCalculationServiceStub,
        lambda: featurestore_v1_entity_calculation_service_pb2_grpc.EntityCalculationServiceStub(container.channel)
    )
    featurestore_entity_lifecycle = container.singleton(
        featurestore_v1_entity_lifecycle_service_pb2_grpc.EntityLifecycleServiceStub,
        lambda: featurestore_v1_entity_lifecycle_service_pb2_grpc.EntityLifecycleServiceStub(container.channel)
    )
    featurestore_entity_reporting = container.singleton(
        featurestore_v1_entity_reporting_service_pb2_grpc.EntityReportingServiceStub,
        lambda: featurestore_v1_entity_reporting_service_pb2_grpc.EntityReportingServiceStub(container.channel)
    )
    featurestore_entity_sync = container.singleton(
        featurestore_v1_entity_sync_service_pb2_grpc.EntitySyncServiceStub,
        lambda: featurestore_v1_entity_sync_service_pb2_grpc.EntitySyncServiceStub(container.channel)
    )
    featurestore_entity_validation = container.singleton(
        featurestore_v1_entity_validation_service_pb2_grpc.EntityValidationServiceStub,
        lambda: featurestore_v1_entity_validation_service_pb2_grpc.EntityValidationServiceStub(container.channel)
    )
    featurestore_feature_value_approval = container.singleton(
        featurestore_v1_feature_value_approval_service_pb2_grpc.FeatureValueApprovalServiceStub,
        lambda: featurestore_v1_feature_value_approval_service_pb2_grpc.FeatureValueApprovalServiceStub(
            container.channel
        )
    )
    featurestore_feature_value_calculation = container.singleton(
        featurestore_v1_feature_value_calculation_service_pb2_grpc.FeatureValueCalculationServiceStub,
        lambda: featurestore_v1_feature_value_calculation_service_pb2_grpc.FeatureValueCalculationServiceStub(
            container.channel
        )
    )
    featurestore_feature_value_import = container.singleton(
        featurestore_v1_feature_value_import_service_pb2_grpc.FeatureValueImportServiceStub,
        lambda: featurestore_v1_feature_value_import_service_pb2_grpc.FeatureValueImportServiceStub(container.channel)
    )
    featurestore_feature_value_query = container.singleton(
        featurestore_v1_feature_value_query_service_pb2_grpc.FeatureValueQueryServiceStub,
        lambda: featurestore_v1_feature_value_query_service_pb2_grpc.FeatureValueQueryServiceStub(container.channel)
    )
    featurestore_feature_value_sync = container.singleton(
        featurestore_v1_feature_value_sync_service_pb2_grpc.FeatureValueSyncServiceStub,
        lambda: featurestore_v1_feature_value_sync_service_pb2_grpc.FeatureValueSyncServiceStub(container.channel)
    )
    featurestore_feature_value_validation = container.singleton(
        featurestore_v1_feature_value_validation_service_pb2_grpc.FeatureValueValidationServiceStub,
        lambda: featurestore_v1_feature_value_validation_service_pb2_grpc.FeatureValueValidationServiceStub(
            container.channel
        )
    )
    featurestore_feature_view_approval = container.singleton(
        featurestore_v1_feature_view_approval_service_pb2_grpc.FeatureViewApprovalServiceStub,
        lambda: featurestore_v1_feature_view_approval_service_pb2_grpc.FeatureViewApprovalServiceStub(container.channel)
    )
    featurestore_feature_view_calculation = container.singleton(
        featurestore_v1_feature_view_calculation_service_pb2_grpc.FeatureViewCalculationServiceStub,
        lambda: featurestore_v1_feature_view_calculation_service_pb2_grpc.FeatureViewCalculationServiceStub(
            container.channel
        )
    )
    featurestore_feature_view_query = container.singleton(
        featurestore_v1_feature_view_query_service_pb2_grpc.FeatureViewQueryServiceStub,
        lambda: featurestore_v1_feature_view_query_service_pb2_grpc.FeatureViewQueryServiceStub(container.channel)
    )
    featurestore_feature_view = container.singleton(
        featurestore_v1_feature_view_service_pb2_grpc.FeatureViewServiceStub,
        lambda: featurestore_v1_feature_view_service_pb2_grpc.FeatureViewServiceStub(container.channel)
    )
    featurestore_feature_view_sync = container.singleton(
        featurestore_v1_feature_view_sync_service_pb2_grpc.FeatureViewSyncServiceStub,
        lambda: featurestore_v1_feature_view_sync_service_pb2_grpc.FeatureViewSyncServiceStub(container.channel)
    )
    featurestore_feature_view_validation = container.singleton(
        featurestore_v1_feature_view_validation_service_pb2_grpc.FeatureViewValidationServiceStub,
        lambda: featurestore_v1_feature_view_validation_service_pb2_grpc.FeatureViewValidationServiceStub(
            container.channel
        )
    )
    featurestore_feature_view_workflow = container.singleton(
        featurestore_v1_feature_view_workflow_service_pb2_grpc.FeatureViewWorkflowServiceStub,
        lambda: featurestore_v1_feature_view_workflow_service_pb2_grpc.FeatureViewWorkflowServiceStub(container.channel)
    )
    identity_user_query = container.singleton(
        identity_v1_user_query_service_pb2_grpc.UserQueryServiceStub,
        lambda: identity_v1_user_query_service_pb2_grpc.UserQueryServiceStub(container.channel)
    )
    identity_user = container.singleton(
        identity_v1_user_service_pb2_grpc.UserServiceStub,
        lambda: identity_v1_user_service_pb2_grpc.UserServiceStub(container.channel)
    )
    identity_user_validation = container.singleton(
        identity_v1_user_validation_service_pb2_grpc.UserValidationServiceStub,
        lambda: identity_v1_user_validation_service_pb2_grpc.UserValidationServiceStub(container.channel)
    )
    ledger_ledger_account_query = container.singleton(
        ledger_v1_ledger_account_query_service_pb2_grpc.LedgerAccountQueryServiceStub,
        lambda: ledger_v1_ledger_account_query_service_pb2_grpc.LedgerAccountQueryServiceStub(container.channel)
    )
    ledger_ledger_account = container.singleton(
        ledger_v1_ledger_account_service_pb2_grpc.LedgerAccountServiceStub,
        lambda: ledger_v1_ledger_account_service_pb2_grpc.LedgerAccountServiceStub(container.channel)
    )
    lineage_impact_approval = container.singleton(
        lineage_v1_impact_approval_service_pb2_grpc.ImpactApprovalServiceStub,
        lambda: lineage_v1_impact_approval_service_pb2_grpc.ImpactApprovalServiceStub(container.channel)
    )
    lineage_impact_sync = container.singleton(
        lineage_v1_impact_sync_service_pb2_grpc.ImpactSyncServiceStub,
        lambda: lineage_v1_impact_sync_service_pb2_grpc.ImpactSyncServiceStub(container.channel)
    )
    lineage_impact_workflow = container.singleton(
        lineage_v1_impact_workflow_service_pb2_grpc.ImpactWorkflowServiceStub,
        lambda: lineage_v1_impact_workflow_service_pb2_grpc.ImpactWorkflowServiceStub(container.channel)
    )
    lineage_lineage_edge_approval = container.singleton(
        lineage_v1_lineage_edge_approval_service_pb2_grpc.LineageEdgeApprovalServiceStub,
        lambda: lineage_v1_lineage_edge_approval_service_pb2_grpc.LineageEdgeApprovalServiceStub(container.channel)
    )
    lineage_lineage_edge_import = container.singleton(
        lineage_v1_lineage_edge_import_service_pb2_grpc.LineageEdgeImportServiceStub,
        lambda: lineage_v1_lineage_edge_import_service_pb2_grpc.LineageEdgeImportServiceStub(container.channel)
    )
    lineage_lineage_edge_sync = container.singleton(
        lineage_v1_lineage_edge_sync_service_pb2_grpc.LineageEdgeSyncServiceStub,
        lambda: lineage_v1_lineage_edge_sync_service_pb2_grpc.LineageEdgeSyncServiceStub(container.channel)
    )
    lineage_lineage_edge_workflow = container.singleton(
        lineage_v1_lineage_edge_workflow_service_pb2_grpc.LineageEdgeWorkflowServiceStub,
        lambda: lineage_v1_lineage_edge_workflow_service_pb2_grpc.LineageEdgeWorkflowServiceStub(container.channel)
    )
    lineage_lineage_node_approval = container.singleton(
        lineage_v1_lineage_node_approval_service_pb2_grpc.LineageNodeApprovalServiceStub,
        lambda: lineage_v1_lineage_node_approval_service_pb2_grpc.LineageNodeApprovalServiceStub(container.channel)
    )
    lineage_lineage_node_calculation = container.singleton(
        lineage_v1_lineage_node_calculation_service_pb2_grpc.LineageNodeCalculationServiceStub,
        lambda: lineage_v1_lineage_node_calculation_service_pb2_grpc.LineageNodeCalculationServiceStub(
            container.channel
        )
    )
    lineage_lineage_node_query = container.singleton(
        lineage_v1_lineage_node_query_service_pb2_grpc.LineageNodeQueryServiceStub,
        lambda: lineage_v1_lineage_node_query_service_pb2_grpc.LineageNodeQueryServiceStub(container.channel)
    )
    lineage_lineage_node_reporting = container.singleton(
        lineage_v1_lineage_node_reporting_service_pb2_grpc.LineageNodeReportingServiceStub,
        lambda: lineage_v1_lineage_node_reporting_service_pb2_grpc.LineageNodeReportingServiceStub(container.channel)
    )
    lineage_lineage_node_sync = container.singleton(
        lineage_v1_lineage_node_sync_service_pb2_grpc.LineageNodeSyncServiceStub,
        lambda: lineage_v1_lineage_node_sync_service_pb2_grpc.LineageNodeSyncServiceStub(container.channel)
    )
    lineage_lineage_node_workflow = container.singleton(
        lineage_v1_lineage_node_workflow_service_pb2_grpc.LineageNodeWorkflowServiceStub,
        lambda: lineage_v1_lineage_node_workflow_service_pb2_grpc.LineageNodeWorkflowServiceStub(container.channel)
    )
    maintenance_work_order_query = container.singleton(
        maintenance_v1_work_order_query_service_pb2_grpc.WorkOrderQueryServiceStub,
        lambda: maintenance_v1_work_order_query_service_pb2_grpc.WorkOrderQueryServiceStub(container.channel)
    )
    metrics_dashboard_export = container.singleton(
        metrics_v1_dashboard_export_service_pb2_grpc.DashboardExportServiceStub,
        lambda: metrics_v1_dashboard_export_service_pb2_grpc.DashboardExportServiceStub(container.channel)
    )
    metrics_dashboard_history = container.singleton(
        metrics_v1_dashboard_history_service_pb2_grpc.DashboardHistoryServiceStub,
        lambda: metrics_v1_dashboard_history_service_pb2_grpc.DashboardHistoryServiceStub(container.channel)
    )
    metrics_dashboard_sync = container.singleton(
        metrics_v1_dashboard_sync_service_pb2_grpc.DashboardSyncServiceStub,
        lambda: metrics_v1_dashboard_sync_service_pb2_grpc.DashboardSyncServiceStub(container.channel)
    )
    metrics_dashboard_validation = container.singleton(
        metrics_v1_dashboard_validation_service_pb2_grpc.DashboardValidationServiceStub,
        lambda: metrics_v1_dashboard_validation_service_pb2_grpc.DashboardValidationServiceStub(container.channel)
    )
    metrics_metric_alert_admin = container.singleton(
        metrics_v1_metric_alert_admin_service_pb2_grpc.MetricAlertAdminServiceStub,
        lambda: metrics_v1_metric_alert_admin_service_pb2_grpc.MetricAlertAdminServiceStub(container.channel)
    )
    metrics_metric_alert_notification = container.singleton(
        metrics_v1_metric_alert_notification_service_pb2_grpc.MetricAlertNotificationServiceStub,
        lambda: metrics_v1_metric_alert_notification_service_pb2_grpc.MetricAlertNotificationServiceStub(
            container.channel
        )
    )
    metrics_metric_alert_query = container.singleton(
        metrics_v1_metric_alert_query_service_pb2_grpc.MetricAlertQueryServiceStub,
        lambda: metrics_v1_metric_alert_query_service_pb2_grpc.MetricAlertQueryServiceStub(container.channel)
    )
    metrics_metric_alert_validation = container.singleton(
        metrics_v1_metric_alert_validation_service_pb2_grpc.MetricAlertValidationServiceStub,
        lambda: metrics_v1_metric_alert_validation_service_pb2_grpc.MetricAlertValidationServiceStub(container.channel)
    )
    metrics_metric_series_admin = container.singleton(
        metrics_v1_metric_series_admin_service_pb2_grpc.MetricSeriesAdminServiceStub,
        lambda: metrics_v1_metric_series_admin_service_pb2_grpc.MetricSeriesAdminServiceStub(container.channel)
    )
    metrics_metric_series_export = container.singleton(
        metrics_v1_metric_series_export_service_pb2_grpc.MetricSeriesExportServiceStub,
        lambda: metrics_v1_metric_series_export_service_pb2_grpc.MetricSeriesExportServiceStub(container.channel)
    )
    metrics_metric_series_history = container.singleton(
        metrics_v1_metric_series_history_service_pb2_grpc.MetricSeriesHistoryServiceStub,
        lambda: metrics_v1_metric_series_history_service_pb2_grpc.MetricSeriesHistoryServiceStub(container.channel)
    )
    metrics_metric_series_query = container.singleton(
        metrics_v1_metric_series_query_service_pb2_grpc.MetricSeriesQueryServiceStub,
        lambda: metrics_v1_metric_series_query_service_pb2_grpc.MetricSeriesQueryServiceStub(container.channel)
    )
    metrics_metric_series_validation = container.singleton(
        metrics_v1_metric_series_validation_service_pb2_grpc.MetricSeriesValidationServiceStub,
        lambda: metrics_v1_metric_series_validation_service_pb2_grpc.MetricSeriesValidationServiceStub(
            container.channel
        )
    )
    modelregistry_deployment_approval = container.singleton(
        modelregistry_v1_deployment_approval_service_pb2_grpc.DeploymentApprovalServiceStub,
        lambda: modelregistry_v1_deployment_approval_service_pb2_grpc.DeploymentApprovalServiceStub(container.channel)
    )
    modelregistry_deployment_calculation = container.singleton(
        modelregistry_v1_deployment_calculation_service_pb2_grpc.DeploymentCalculationServiceStub,
        lambda: modelregistry_v1_deployment_calculation_service_pb2_grpc.DeploymentCalculationServiceStub(
            container.channel
        )
    )
    modelregistry_deployment_import = container.singleton(
        modelregistry_v1_deployment_import_service_pb2_grpc.DeploymentImportServiceStub,
        lambda: modelregistry_v1_deployment_import_service_pb2_grpc.DeploymentImportServiceStub(container.channel)
    )
    modelregistry_deployment_lifecycle = container.singleton(
        modelregistry_v1_deployment_lifecycle_service_pb2_grpc.DeploymentLifecycleServiceStub,
        lambda: modelregistry_v1_deployment_lifecycle_service_pb2_grpc.DeploymentLifecycleServiceStub(container.channel)
    )
    modelregistry_deployment_reporting = container.singleton(
        modelregistry_v1_deployment_reporting_service_pb2_grpc.DeploymentReportingServiceStub,
        lambda: modelregistry_v1_deployment_reporting_service_pb2_grpc.DeploymentReportingServiceStub(container.channel)
    )
    modelregistry_deployment_sync = container.singleton(
        modelregistry_v1_deployment_sync_service_pb2_grpc.DeploymentSyncServiceStub,
        lambda: modelregistry_v1_deployment_sync_service_pb2_grpc.DeploymentSyncServiceStub(container.channel)
    )
    modelregistry_deployment_validation = container.singleton(
        modelregistry_v1_deployment_validation_service_pb2_grpc.DeploymentValidationServiceStub,
        lambda: modelregistry_v1_deployment_validation_service_pb2_grpc.DeploymentValidationServiceStub(
            container.channel
        )
    )
    modelregistry_model_version_approval = container.singleton(
        modelregistry_v1_model_version_approval_service_pb2_grpc.ModelVersionApprovalServiceStub,
        lambda: modelregistry_v1_model_version_approval_service_pb2_grpc.ModelVersionApprovalServiceStub(
            container.channel
        )
    )
    modelregistry_model_version_calculation = container.singleton(
        modelregistry_v1_model_version_calculation_service_pb2_grpc.ModelVersionCalculationServiceStub,
        lambda: modelregistry_v1_model_version_calculation_service_pb2_grpc.ModelVersionCalculationServiceStub(
            container.channel
        )
    )
    modelregistry_model_version_lifecycle = container.singleton(
        modelregistry_v1_model_version_lifecycle_service_pb2_grpc.ModelVersionLifecycleServiceStub,
        lambda: modelregistry_v1_model_version_lifecycle_service_pb2_grpc.ModelVersionLifecycleServiceStub(
            container.channel
        )
    )
    modelregistry_model_version_query = container.singleton(
        modelregistry_v1_model_version_query_service_pb2_grpc.ModelVersionQueryServiceStub,
        lambda: modelregistry_v1_model_version_query_service_pb2_grpc.ModelVersionQueryServiceStub(container.channel)
    )
    modelregistry_model_version_reporting = container.singleton(
        modelregistry_v1_model_version_reporting_service_pb2_grpc.ModelVersionReportingServiceStub,
        lambda: modelregistry_v1_model_version_reporting_service_pb2_grpc.ModelVersionReportingServiceStub(
            container.channel
        )
    )
    modelregistry_model_version_sync = container.singleton(
        modelregistry_v1_model_version_sync_service_pb2_grpc.ModelVersionSyncServiceStub,
        lambda: modelregistry_v1_model_version_sync_service_pb2_grpc.ModelVersionSyncServiceStub(container.channel)
    )
    modelregistry_model_version_validation = container.singleton(
        modelregistry_v1_model_version_validation_service_pb2_grpc.ModelVersionValidationServiceStub,
        lambda: modelregistry_v1_model_version_validation_service_pb2_grpc.ModelVersionValidationServiceStub(
            container.channel
        )
    )
    modelregistry_registered_model_approval = container.singleton(
        modelregistry_v1_registered_model_approval_service_pb2_grpc.RegisteredModelApprovalServiceStub,
        lambda: modelregistry_v1_registered_model_approval_service_pb2_grpc.RegisteredModelApprovalServiceStub(
            container.channel
        )
    )
    modelregistry_registered_model_calculation = container.singleton(
        modelregistry_v1_registered_model_calculation_service_pb2_grpc.RegisteredModelCalculationServiceStub,
        lambda: modelregistry_v1_registered_model_calculation_service_pb2_grpc.RegisteredModelCalculationServiceStub(
            container.channel
        )
    )
    modelregistry_registered_model_lifecycle = container.singleton(
        modelregistry_v1_registered_model_lifecycle_service_pb2_grpc.RegisteredModelLifecycleServiceStub,
        lambda: modelregistry_v1_registered_model_lifecycle_service_pb2_grpc.RegisteredModelLifecycleServiceStub(
            container.channel
        )
    )
    modelregistry_registered_model_query = container.singleton(
        modelregistry_v1_registered_model_query_service_pb2_grpc.RegisteredModelQueryServiceStub,
        lambda: modelregistry_v1_registered_model_query_service_pb2_grpc.RegisteredModelQueryServiceStub(
            container.channel
        )
    )
    modelregistry_registered_model_reporting = container.singleton(
        modelregistry_v1_registered_model_reporting_service_pb2_grpc.RegisteredModelReportingServiceStub,
        lambda: modelregistry_v1_registered_model_reporting_service_pb2_grpc.RegisteredModelReportingServiceStub(
            container.channel
        )
    )
    modelregistry_registered_model = container.singleton(
        modelregistry_v1_registered_model_service_pb2_grpc.RegisteredModelServiceStub,
        lambda: modelregistry_v1_registered_model_service_pb2_grpc.RegisteredModelServiceStub(container.channel)
    )
    modelregistry_registered_model_sync = container.singleton(
        modelregistry_v1_registered_model_sync_service_pb2_grpc.RegisteredModelSyncServiceStub,
        lambda: modelregistry_v1_registered_model_sync_service_pb2_grpc.RegisteredModelSyncServiceStub(
            container.channel
        )
    )
    modelregistry_registered_model_validation = container.singleton(
        modelregistry_v1_registered_model_validation_service_pb2_grpc.RegisteredModelValidationServiceStub,
        lambda: modelregistry_v1_registered_model_validation_service_pb2_grpc.RegisteredModelValidationServiceStub(
            container.channel
        )
    )
    notifications_notification_query = container.singleton(
        notifications_v1_notification_query_service_pb2_grpc.NotificationQueryServiceStub,
        lambda: notifications_v1_notification_query_service_pb2_grpc.NotificationQueryServiceStub(container.channel)
    )
    notifications_notification = container.singleton(
        notifications_v1_notification_service_pb2_grpc.NotificationServiceStub,
        lambda: notifications_v1_notification_service_pb2_grpc.NotificationServiceStub(container.channel)
    )
    patients_patient = container.singleton(
        patients_v1_patient_service_pb2_grpc.PatientServiceStub,
        lambda: patients_v1_patient_service_pb2_grpc.PatientServiceStub(container.channel)
    )
    search_search_index = container.singleton(
        search_v1_search_index_service_pb2_grpc.SearchIndexServiceStub,
        lambda: search_v1_search_index_service_pb2_grpc.SearchIndexServiceStub(container.channel)
    )
    search_search_index_validation = container.singleton(
        search_v1_search_index_validation_service_pb2_grpc.SearchIndexValidationServiceStub,
        lambda: search_v1_search_index_validation_service_pb2_grpc.SearchIndexValidationServiceStub(container.channel)
    )
    seating_seat_map = container.singleton(
        seating_v1_seat_map_service_pb2_grpc.SeatMapServiceStub,
        lambda: seating_v1_seat_map_service_pb2_grpc.SeatMapServiceStub(container.channel)
    )
    secrets_secret_query = container.singleton(
        secrets_v1_secret_query_service_pb2_grpc.SecretQueryServiceStub,
        lambda: secrets_v1_secret_query_service_pb2_grpc.SecretQueryServiceStub(container.channel)
    )
    sponsorships_sponsor_query = container.singleton(
        sponsorships_v1_sponsor_query_service_pb2_grpc.SponsorQueryServiceStub,
        lambda: sponsorships_v1_sponsor_query_service_pb2_grpc.SponsorQueryServiceStub(container.channel)
    )
    ticketing_ticket = container.singleton(
        ticketing_v1_ticket_service_pb2_grpc.TicketServiceStub,
        lambda: ticketing_v1_ticket_service_pb2_grpc.TicketServiceStub(container.channel)
    )
    venues_venue_validation = container.singleton(
        venues_v1_venue_validation_service_pb2_grpc.VenueValidationServiceStub,
        lambda: venues_v1_venue_validation_service_pb2_grpc.VenueValidationServiceStub(container.channel)
    )
    clients = Clients(
        admissions_admission_query=admissions_admission_query,
        anomalies_anomaly_approval=anomalies_anomaly_approval,
        anomalies_anomaly_feedback_approval=anomalies_anomaly_feedback_approval,
        anomalies_anomaly_feedback_calculation=anomalies_anomaly_feedback_calculation,
        anomalies_anomaly_feedback_workflow=anomalies_anomaly_feedback_workflow,
        anomalies_anomaly_validation=anomalies_anomaly_validation,
        anomalies_anomaly_workflow=anomalies_anomaly_workflow,
        anomalies_detector_query=anomalies_detector_query,
        audit_audit_event_query=audit_audit_event_query,
        audit_audit_event=audit_audit_event,
        audit_audit_event_validation=audit_audit_event_validation,
        authorization_access_policy=authorization_access_policy,
        authorization_access_policy_validation=authorization_access_policy_validation,
        banking_bank_account_query=banking_bank_account_query,
        budgeting_budget_query=budgeting_budget_query,
        cart_cart_query=cart_cart_query,
        certificates_certificate_calculation=certificates_certificate_calculation,
        community_forum_query=community_forum_query,
        concessions_concession_stand=concessions_concession_stand,
        customers_consent_record_calculation=customers_consent_record_calculation,
        customers_consent_record_validation=customers_consent_record_validation,
        customers_customer_calculation=customers_customer_calculation,
        customers_customer_query=customers_customer_query,
        customers_customer_segment_calculation=customers_customer_segment_calculation,
        customers_customer_segment_validation=customers_customer_segment_validation,
        customers_customer=customers_customer,
        customers_customer_validation=customers_customer_validation,
        customers_household_calculation=customers_household_calculation,
        customers_household_query=customers_household_query,
        customers_household_validation=customers_household_validation,
        customers_preference_calculation=customers_preference_calculation,
        customers_preference_validation=customers_preference_validation,
        documents_document=documents_document,
        documents_document_validation=documents_document_validation,
        featureflags_feature_flag=featureflags_feature_flag,
        featureflags_feature_flag_validation=featureflags_feature_flag_validation,
        featurestore_entity_approval=featurestore_entity_approval,
        featurestore_entity_calculation=featurestore_entity_calculation,
        featurestore_entity_lifecycle=featurestore_entity_lifecycle,
        featurestore_entity_reporting=featurestore_entity_reporting,
        featurestore_entity_sync=featurestore_entity_sync,
        featurestore_entity_validation=featurestore_entity_validation,
        featurestore_feature_value_approval=featurestore_feature_value_approval,
        featurestore_feature_value_calculation=featurestore_feature_value_calculation,
        featurestore_feature_value_import=featurestore_feature_value_import,
        featurestore_feature_value_query=featurestore_feature_value_query,
        featurestore_feature_value_sync=featurestore_feature_value_sync,
        featurestore_feature_value_validation=featurestore_feature_value_validation,
        featurestore_feature_view_approval=featurestore_feature_view_approval,
        featurestore_feature_view_calculation=featurestore_feature_view_calculation,
        featurestore_feature_view_query=featurestore_feature_view_query,
        featurestore_feature_view=featurestore_feature_view,
        featurestore_feature_view_sync=featurestore_feature_view_sync,
        featurestore_feature_view_validation=featurestore_feature_view_validation,
        featurestore_feature_view_workflow=featurestore_feature_view_workflow,
        identity_user_query=identity_user_query,
        identity_user=identity_user,
        identity_user_validation=identity_user_validation,
        ledger_ledger_account_query=ledger_ledger_account_query,
        ledger_ledger_account=ledger_ledger_account,
        lineage_impact_approval=lineage_impact_approval,
        lineage_impact_sync=lineage_impact_sync,
        lineage_impact_workflow=lineage_impact_workflow,
        lineage_lineage_edge_approval=lineage_lineage_edge_approval,
        lineage_lineage_edge_import=lineage_lineage_edge_import,
        lineage_lineage_edge_sync=lineage_lineage_edge_sync,
        lineage_lineage_edge_workflow=lineage_lineage_edge_workflow,
        lineage_lineage_node_approval=lineage_lineage_node_approval,
        lineage_lineage_node_calculation=lineage_lineage_node_calculation,
        lineage_lineage_node_query=lineage_lineage_node_query,
        lineage_lineage_node_reporting=lineage_lineage_node_reporting,
        lineage_lineage_node_sync=lineage_lineage_node_sync,
        lineage_lineage_node_workflow=lineage_lineage_node_workflow,
        maintenance_work_order_query=maintenance_work_order_query,
        metrics_dashboard_export=metrics_dashboard_export,
        metrics_dashboard_history=metrics_dashboard_history,
        metrics_dashboard_sync=metrics_dashboard_sync,
        metrics_dashboard_validation=metrics_dashboard_validation,
        metrics_metric_alert_admin=metrics_metric_alert_admin,
        metrics_metric_alert_notification=metrics_metric_alert_notification,
        metrics_metric_alert_query=metrics_metric_alert_query,
        metrics_metric_alert_validation=metrics_metric_alert_validation,
        metrics_metric_series_admin=metrics_metric_series_admin,
        metrics_metric_series_export=metrics_metric_series_export,
        metrics_metric_series_history=metrics_metric_series_history,
        metrics_metric_series_query=metrics_metric_series_query,
        metrics_metric_series_validation=metrics_metric_series_validation,
        modelregistry_deployment_approval=modelregistry_deployment_approval,
        modelregistry_deployment_calculation=modelregistry_deployment_calculation,
        modelregistry_deployment_import=modelregistry_deployment_import,
        modelregistry_deployment_lifecycle=modelregistry_deployment_lifecycle,
        modelregistry_deployment_reporting=modelregistry_deployment_reporting,
        modelregistry_deployment_sync=modelregistry_deployment_sync,
        modelregistry_deployment_validation=modelregistry_deployment_validation,
        modelregistry_model_version_approval=modelregistry_model_version_approval,
        modelregistry_model_version_calculation=modelregistry_model_version_calculation,
        modelregistry_model_version_lifecycle=modelregistry_model_version_lifecycle,
        modelregistry_model_version_query=modelregistry_model_version_query,
        modelregistry_model_version_reporting=modelregistry_model_version_reporting,
        modelregistry_model_version_sync=modelregistry_model_version_sync,
        modelregistry_model_version_validation=modelregistry_model_version_validation,
        modelregistry_registered_model_approval=modelregistry_registered_model_approval,
        modelregistry_registered_model_calculation=modelregistry_registered_model_calculation,
        modelregistry_registered_model_lifecycle=modelregistry_registered_model_lifecycle,
        modelregistry_registered_model_query=modelregistry_registered_model_query,
        modelregistry_registered_model_reporting=modelregistry_registered_model_reporting,
        modelregistry_registered_model=modelregistry_registered_model,
        modelregistry_registered_model_sync=modelregistry_registered_model_sync,
        modelregistry_registered_model_validation=modelregistry_registered_model_validation,
        notifications_notification_query=notifications_notification_query,
        notifications_notification=notifications_notification,
        patients_patient=patients_patient,
        search_search_index=search_search_index,
        search_search_index_validation=search_search_index_validation,
        seating_seat_map=seating_seat_map,
        secrets_secret_query=secrets_secret_query,
        sponsorships_sponsor_query=sponsorships_sponsor_query,
        ticketing_ticket=ticketing_ticket,
        venues_venue_validation=venues_venue_validation,
        registry={
            'acme.admissions.v1.AdmissionQueryService': admissions_admission_query,
            'acme.anomalies.v1.AnomalyApprovalService': anomalies_anomaly_approval,
            'acme.anomalies.v1.AnomalyFeedbackApprovalService': anomalies_anomaly_feedback_approval,
            'acme.anomalies.v1.AnomalyFeedbackCalculationService': anomalies_anomaly_feedback_calculation,
            'acme.anomalies.v1.AnomalyFeedbackWorkflowService': anomalies_anomaly_feedback_workflow,
            'acme.anomalies.v1.AnomalyValidationService': anomalies_anomaly_validation,
            'acme.anomalies.v1.AnomalyWorkflowService': anomalies_anomaly_workflow,
            'acme.anomalies.v1.DetectorQueryService': anomalies_detector_query,
            'acme.audit.v1.AuditEventQueryService': audit_audit_event_query,
            'acme.audit.v1.AuditEventService': audit_audit_event,
            'acme.audit.v1.AuditEventValidationService': audit_audit_event_validation,
            'acme.authorization.v1.AccessPolicyService': authorization_access_policy,
            'acme.authorization.v1.AccessPolicyValidationService': authorization_access_policy_validation,
            'acme.banking.v1.BankAccountQueryService': banking_bank_account_query,
            'acme.budgeting.v1.BudgetQueryService': budgeting_budget_query,
            'acme.cart.v1.CartQueryService': cart_cart_query,
            'acme.certificates.v1.CertificateCalculationService': certificates_certificate_calculation,
            'acme.community.v1.ForumQueryService': community_forum_query,
            'acme.concessions.v1.ConcessionStandService': concessions_concession_stand,
            'acme.customers.v1.ConsentRecordCalculationService': customers_consent_record_calculation,
            'acme.customers.v1.ConsentRecordValidationService': customers_consent_record_validation,
            'acme.customers.v1.CustomerCalculationService': customers_customer_calculation,
            'acme.customers.v1.CustomerQueryService': customers_customer_query,
            'acme.customers.v1.CustomerSegmentCalculationService': customers_customer_segment_calculation,
            'acme.customers.v1.CustomerSegmentValidationService': customers_customer_segment_validation,
            'acme.customers.v1.CustomerService': customers_customer,
            'acme.customers.v1.CustomerValidationService': customers_customer_validation,
            'acme.customers.v1.HouseholdCalculationService': customers_household_calculation,
            'acme.customers.v1.HouseholdQueryService': customers_household_query,
            'acme.customers.v1.HouseholdValidationService': customers_household_validation,
            'acme.customers.v1.PreferenceCalculationService': customers_preference_calculation,
            'acme.customers.v1.PreferenceValidationService': customers_preference_validation,
            'acme.documents.v1.DocumentService': documents_document,
            'acme.documents.v1.DocumentValidationService': documents_document_validation,
            'acme.featureflags.v1.FeatureFlagService': featureflags_feature_flag,
            'acme.featureflags.v1.FeatureFlagValidationService': featureflags_feature_flag_validation,
            'acme.featurestore.v1.EntityApprovalService': featurestore_entity_approval,
            'acme.featurestore.v1.EntityCalculationService': featurestore_entity_calculation,
            'acme.featurestore.v1.EntityLifecycleService': featurestore_entity_lifecycle,
            'acme.featurestore.v1.EntityReportingService': featurestore_entity_reporting,
            'acme.featurestore.v1.EntitySyncService': featurestore_entity_sync,
            'acme.featurestore.v1.EntityValidationService': featurestore_entity_validation,
            'acme.featurestore.v1.FeatureValueApprovalService': featurestore_feature_value_approval,
            'acme.featurestore.v1.FeatureValueCalculationService': featurestore_feature_value_calculation,
            'acme.featurestore.v1.FeatureValueImportService': featurestore_feature_value_import,
            'acme.featurestore.v1.FeatureValueQueryService': featurestore_feature_value_query,
            'acme.featurestore.v1.FeatureValueSyncService': featurestore_feature_value_sync,
            'acme.featurestore.v1.FeatureValueValidationService': featurestore_feature_value_validation,
            'acme.featurestore.v1.FeatureViewApprovalService': featurestore_feature_view_approval,
            'acme.featurestore.v1.FeatureViewCalculationService': featurestore_feature_view_calculation,
            'acme.featurestore.v1.FeatureViewQueryService': featurestore_feature_view_query,
            'acme.featurestore.v1.FeatureViewService': featurestore_feature_view,
            'acme.featurestore.v1.FeatureViewSyncService': featurestore_feature_view_sync,
            'acme.featurestore.v1.FeatureViewValidationService': featurestore_feature_view_validation,
            'acme.featurestore.v1.FeatureViewWorkflowService': featurestore_feature_view_workflow,
            'acme.identity.v1.UserQueryService': identity_user_query,
            'acme.identity.v1.UserService': identity_user,
            'acme.identity.v1.UserValidationService': identity_user_validation,
            'acme.ledger.v1.LedgerAccountQueryService': ledger_ledger_account_query,
            'acme.ledger.v1.LedgerAccountService': ledger_ledger_account,
            'acme.lineage.v1.ImpactApprovalService': lineage_impact_approval,
            'acme.lineage.v1.ImpactSyncService': lineage_impact_sync,
            'acme.lineage.v1.ImpactWorkflowService': lineage_impact_workflow,
            'acme.lineage.v1.LineageEdgeApprovalService': lineage_lineage_edge_approval,
            'acme.lineage.v1.LineageEdgeImportService': lineage_lineage_edge_import,
            'acme.lineage.v1.LineageEdgeSyncService': lineage_lineage_edge_sync,
            'acme.lineage.v1.LineageEdgeWorkflowService': lineage_lineage_edge_workflow,
            'acme.lineage.v1.LineageNodeApprovalService': lineage_lineage_node_approval,
            'acme.lineage.v1.LineageNodeCalculationService': lineage_lineage_node_calculation,
            'acme.lineage.v1.LineageNodeQueryService': lineage_lineage_node_query,
            'acme.lineage.v1.LineageNodeReportingService': lineage_lineage_node_reporting,
            'acme.lineage.v1.LineageNodeSyncService': lineage_lineage_node_sync,
            'acme.lineage.v1.LineageNodeWorkflowService': lineage_lineage_node_workflow,
            'acme.maintenance.v1.WorkOrderQueryService': maintenance_work_order_query,
            'acme.metrics.v1.DashboardExportService': metrics_dashboard_export,
            'acme.metrics.v1.DashboardHistoryService': metrics_dashboard_history,
            'acme.metrics.v1.DashboardSyncService': metrics_dashboard_sync,
            'acme.metrics.v1.DashboardValidationService': metrics_dashboard_validation,
            'acme.metrics.v1.MetricAlertAdminService': metrics_metric_alert_admin,
            'acme.metrics.v1.MetricAlertNotificationService': metrics_metric_alert_notification,
            'acme.metrics.v1.MetricAlertQueryService': metrics_metric_alert_query,
            'acme.metrics.v1.MetricAlertValidationService': metrics_metric_alert_validation,
            'acme.metrics.v1.MetricSeriesAdminService': metrics_metric_series_admin,
            'acme.metrics.v1.MetricSeriesExportService': metrics_metric_series_export,
            'acme.metrics.v1.MetricSeriesHistoryService': metrics_metric_series_history,
            'acme.metrics.v1.MetricSeriesQueryService': metrics_metric_series_query,
            'acme.metrics.v1.MetricSeriesValidationService': metrics_metric_series_validation,
            'acme.modelregistry.v1.DeploymentApprovalService': modelregistry_deployment_approval,
            'acme.modelregistry.v1.DeploymentCalculationService': modelregistry_deployment_calculation,
            'acme.modelregistry.v1.DeploymentImportService': modelregistry_deployment_import,
            'acme.modelregistry.v1.DeploymentLifecycleService': modelregistry_deployment_lifecycle,
            'acme.modelregistry.v1.DeploymentReportingService': modelregistry_deployment_reporting,
            'acme.modelregistry.v1.DeploymentSyncService': modelregistry_deployment_sync,
            'acme.modelregistry.v1.DeploymentValidationService': modelregistry_deployment_validation,
            'acme.modelregistry.v1.ModelVersionApprovalService': modelregistry_model_version_approval,
            'acme.modelregistry.v1.ModelVersionCalculationService': modelregistry_model_version_calculation,
            'acme.modelregistry.v1.ModelVersionLifecycleService': modelregistry_model_version_lifecycle,
            'acme.modelregistry.v1.ModelVersionQueryService': modelregistry_model_version_query,
            'acme.modelregistry.v1.ModelVersionReportingService': modelregistry_model_version_reporting,
            'acme.modelregistry.v1.ModelVersionSyncService': modelregistry_model_version_sync,
            'acme.modelregistry.v1.ModelVersionValidationService': modelregistry_model_version_validation,
            'acme.modelregistry.v1.RegisteredModelApprovalService': modelregistry_registered_model_approval,
            'acme.modelregistry.v1.RegisteredModelCalculationService': modelregistry_registered_model_calculation,
            'acme.modelregistry.v1.RegisteredModelLifecycleService': modelregistry_registered_model_lifecycle,
            'acme.modelregistry.v1.RegisteredModelQueryService': modelregistry_registered_model_query,
            'acme.modelregistry.v1.RegisteredModelReportingService': modelregistry_registered_model_reporting,
            'acme.modelregistry.v1.RegisteredModelService': modelregistry_registered_model,
            'acme.modelregistry.v1.RegisteredModelSyncService': modelregistry_registered_model_sync,
            'acme.modelregistry.v1.RegisteredModelValidationService': modelregistry_registered_model_validation,
            'acme.notifications.v1.NotificationQueryService': notifications_notification_query,
            'acme.notifications.v1.NotificationService': notifications_notification,
            'acme.patients.v1.PatientService': patients_patient,
            'acme.search.v1.SearchIndexService': search_search_index,
            'acme.search.v1.SearchIndexValidationService': search_search_index_validation,
            'acme.seating.v1.SeatMapService': seating_seat_map,
            'acme.secrets.v1.SecretQueryService': secrets_secret_query,
            'acme.sponsorships.v1.SponsorQueryService': sponsorships_sponsor_query,
            'acme.ticketing.v1.TicketService': ticketing_ticket,
            'acme.venues.v1.VenueValidationService': venues_venue_validation,
        },
    )
    return Dependencies(clients, DomainRepository(container.sessions),
                        container.settings, container.bus)


def register(server: grpc.aio.Server, container: Container) -> dict[str, object]:
    deps = dependencies(container)
    registered: dict[str, object] = {}
    deployment_approval_servicer = Factory(lambda: DeploymentApprovalServicer(deps))()
    modelregistry_v1_deployment_approval_service_pb2_grpc.add_DeploymentApprovalServiceServicer_to_server(
        deployment_approval_servicer,
        server
    )
    registered['acme.modelregistry.v1.DeploymentApprovalService'] = deployment_approval_servicer
    deployment_calculation_servicer = Factory(lambda: DeploymentCalculationServicer(deps))()
    modelregistry_v1_deployment_calculation_service_pb2_grpc.add_DeploymentCalculationServiceServicer_to_server(
        deployment_calculation_servicer,
        server
    )
    registered['acme.modelregistry.v1.DeploymentCalculationService'] = deployment_calculation_servicer
    deployment_import_servicer = Factory(lambda: DeploymentImportServicer(deps))()
    modelregistry_v1_deployment_import_service_pb2_grpc.add_DeploymentImportServiceServicer_to_server(
        deployment_import_servicer,
        server
    )
    registered['acme.modelregistry.v1.DeploymentImportService'] = deployment_import_servicer
    deployment_lifecycle_servicer = Factory(lambda: DeploymentLifecycleServicer(deps))()
    modelregistry_v1_deployment_lifecycle_service_pb2_grpc.add_DeploymentLifecycleServiceServicer_to_server(
        deployment_lifecycle_servicer,
        server
    )
    registered['acme.modelregistry.v1.DeploymentLifecycleService'] = deployment_lifecycle_servicer
    deployment_reporting_servicer = Factory(lambda: DeploymentReportingServicer(deps))()
    modelregistry_v1_deployment_reporting_service_pb2_grpc.add_DeploymentReportingServiceServicer_to_server(
        deployment_reporting_servicer,
        server
    )
    registered['acme.modelregistry.v1.DeploymentReportingService'] = deployment_reporting_servicer
    deployment_sync_servicer = Factory(lambda: DeploymentSyncServicer(deps))()
    modelregistry_v1_deployment_sync_service_pb2_grpc.add_DeploymentSyncServiceServicer_to_server(
        deployment_sync_servicer,
        server
    )
    registered['acme.modelregistry.v1.DeploymentSyncService'] = deployment_sync_servicer
    deployment_validation_servicer = Factory(lambda: DeploymentValidationServicer(deps))()
    modelregistry_v1_deployment_validation_service_pb2_grpc.add_DeploymentValidationServiceServicer_to_server(
        deployment_validation_servicer,
        server
    )
    registered['acme.modelregistry.v1.DeploymentValidationService'] = deployment_validation_servicer
    deployment_workflow_servicer = Factory(lambda: DeploymentWorkflowServicer(deps))()
    modelregistry_v1_deployment_workflow_service_pb2_grpc.add_DeploymentWorkflowServiceServicer_to_server(
        deployment_workflow_servicer,
        server
    )
    registered['acme.modelregistry.v1.DeploymentWorkflowService'] = deployment_workflow_servicer
    model_version_approval_servicer = Factory(lambda: ModelVersionApprovalServicer(deps))()
    modelregistry_v1_model_version_approval_service_pb2_grpc.add_ModelVersionApprovalServiceServicer_to_server(
        model_version_approval_servicer,
        server
    )
    registered['acme.modelregistry.v1.ModelVersionApprovalService'] = model_version_approval_servicer
    model_version_calculation_servicer = Factory(lambda: ModelVersionCalculationServicer(deps))()
    modelregistry_v1_model_version_calculation_service_pb2_grpc.add_ModelVersionCalculationServiceServicer_to_server(
        model_version_calculation_servicer,
        server
    )
    registered['acme.modelregistry.v1.ModelVersionCalculationService'] = model_version_calculation_servicer
    model_version_lifecycle_servicer = Factory(lambda: ModelVersionLifecycleServicer(deps))()
    modelregistry_v1_model_version_lifecycle_service_pb2_grpc.add_ModelVersionLifecycleServiceServicer_to_server(
        model_version_lifecycle_servicer,
        server
    )
    registered['acme.modelregistry.v1.ModelVersionLifecycleService'] = model_version_lifecycle_servicer
    model_version_query_servicer = Factory(lambda: ModelVersionQueryServicer(deps))()
    modelregistry_v1_model_version_query_service_pb2_grpc.add_ModelVersionQueryServiceServicer_to_server(
        model_version_query_servicer,
        server
    )
    registered['acme.modelregistry.v1.ModelVersionQueryService'] = model_version_query_servicer
    model_version_reporting_servicer = Factory(lambda: ModelVersionReportingServicer(deps))()
    modelregistry_v1_model_version_reporting_service_pb2_grpc.add_ModelVersionReportingServiceServicer_to_server(
        model_version_reporting_servicer,
        server
    )
    registered['acme.modelregistry.v1.ModelVersionReportingService'] = model_version_reporting_servicer
    model_version_sync_servicer = Factory(lambda: ModelVersionSyncServicer(deps))()
    modelregistry_v1_model_version_sync_service_pb2_grpc.add_ModelVersionSyncServiceServicer_to_server(
        model_version_sync_servicer,
        server
    )
    registered['acme.modelregistry.v1.ModelVersionSyncService'] = model_version_sync_servicer
    model_version_validation_servicer = Factory(lambda: ModelVersionValidationServicer(deps))()
    modelregistry_v1_model_version_validation_service_pb2_grpc.add_ModelVersionValidationServiceServicer_to_server(
        model_version_validation_servicer,
        server
    )
    registered['acme.modelregistry.v1.ModelVersionValidationService'] = model_version_validation_servicer
    model_version_workflow_servicer = Factory(lambda: ModelVersionWorkflowServicer(deps))()
    modelregistry_v1_model_version_workflow_service_pb2_grpc.add_ModelVersionWorkflowServiceServicer_to_server(
        model_version_workflow_servicer,
        server
    )
    registered['acme.modelregistry.v1.ModelVersionWorkflowService'] = model_version_workflow_servicer
    registered_model_approval_servicer = Factory(lambda: RegisteredModelApprovalServicer(deps))()
    modelregistry_v1_registered_model_approval_service_pb2_grpc.add_RegisteredModelApprovalServiceServicer_to_server(
        registered_model_approval_servicer,
        server
    )
    registered['acme.modelregistry.v1.RegisteredModelApprovalService'] = registered_model_approval_servicer
    registered_model_calculation_servicer = Factory(lambda: RegisteredModelCalculationServicer(deps))()
    modelregistry_v1_registered_model_calculation_service_pb2_grpc.add_RegisteredModelCalculationServiceServicer_to_server(
        registered_model_calculation_servicer,
        server
    )
    registered['acme.modelregistry.v1.RegisteredModelCalculationService'] = registered_model_calculation_servicer
    registered_model_lifecycle_servicer = Factory(lambda: RegisteredModelLifecycleServicer(deps))()
    modelregistry_v1_registered_model_lifecycle_service_pb2_grpc.add_RegisteredModelLifecycleServiceServicer_to_server(
        registered_model_lifecycle_servicer,
        server
    )
    registered['acme.modelregistry.v1.RegisteredModelLifecycleService'] = registered_model_lifecycle_servicer
    registered_model_query_servicer = Factory(lambda: RegisteredModelQueryServicer(deps))()
    modelregistry_v1_registered_model_query_service_pb2_grpc.add_RegisteredModelQueryServiceServicer_to_server(
        registered_model_query_servicer,
        server
    )
    registered['acme.modelregistry.v1.RegisteredModelQueryService'] = registered_model_query_servicer
    registered_model_reporting_servicer = Factory(lambda: RegisteredModelReportingServicer(deps))()
    modelregistry_v1_registered_model_reporting_service_pb2_grpc.add_RegisteredModelReportingServiceServicer_to_server(
        registered_model_reporting_servicer,
        server
    )
    registered['acme.modelregistry.v1.RegisteredModelReportingService'] = registered_model_reporting_servicer
    registered_model_servicer = Factory(lambda: RegisteredModelServicer(deps))()
    modelregistry_v1_registered_model_service_pb2_grpc.add_RegisteredModelServiceServicer_to_server(
        registered_model_servicer,
        server
    )
    registered['acme.modelregistry.v1.RegisteredModelService'] = registered_model_servicer
    registered_model_sync_servicer = Factory(lambda: RegisteredModelSyncServicer(deps))()
    modelregistry_v1_registered_model_sync_service_pb2_grpc.add_RegisteredModelSyncServiceServicer_to_server(
        registered_model_sync_servicer,
        server
    )
    registered['acme.modelregistry.v1.RegisteredModelSyncService'] = registered_model_sync_servicer
    registered_model_validation_servicer = Factory(lambda: RegisteredModelValidationServicer(deps))()
    modelregistry_v1_registered_model_validation_service_pb2_grpc.add_RegisteredModelValidationServiceServicer_to_server(
        registered_model_validation_servicer,
        server
    )
    registered['acme.modelregistry.v1.RegisteredModelValidationService'] = registered_model_validation_servicer
    registered_model_workflow_servicer = Factory(lambda: RegisteredModelWorkflowServicer(deps))()
    modelregistry_v1_registered_model_workflow_service_pb2_grpc.add_RegisteredModelWorkflowServiceServicer_to_server(
        registered_model_workflow_servicer,
        server
    )
    registered['acme.modelregistry.v1.RegisteredModelWorkflowService'] = registered_model_workflow_servicer
    subscribe(deps)
    return registered
