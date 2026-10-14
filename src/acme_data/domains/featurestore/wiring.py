"""Register and compose every service of the featurestore domain."""

from __future__ import annotations

import grpc

from acme.anomalies.v1 import anomaly_approval_service_pb2_grpc as anomalies_v1_anomaly_approval_service_pb2_grpc
from acme.anomalies.v1 import (
    anomaly_feedback_approval_service_pb2_grpc as anomalies_v1_anomaly_feedback_approval_service_pb2_grpc,
)
from acme.anomalies.v1 import (
    anomaly_feedback_calculation_service_pb2_grpc as anomalies_v1_anomaly_feedback_calculation_service_pb2_grpc,
)
from acme.anomalies.v1 import (
    anomaly_feedback_validation_service_pb2_grpc as anomalies_v1_anomaly_feedback_validation_service_pb2_grpc,
)
from acme.anomalies.v1 import (
    anomaly_feedback_workflow_service_pb2_grpc as anomalies_v1_anomaly_feedback_workflow_service_pb2_grpc,
)
from acme.anomalies.v1 import anomaly_query_service_pb2_grpc as anomalies_v1_anomaly_query_service_pb2_grpc
from acme.anomalies.v1 import anomaly_service_pb2_grpc as anomalies_v1_anomaly_service_pb2_grpc
from acme.anomalies.v1 import anomaly_workflow_service_pb2_grpc as anomalies_v1_anomaly_workflow_service_pb2_grpc
from acme.anomalies.v1 import detector_approval_service_pb2_grpc as anomalies_v1_detector_approval_service_pb2_grpc
from acme.anomalies.v1 import detector_query_service_pb2_grpc as anomalies_v1_detector_query_service_pb2_grpc
from acme.anomalies.v1 import detector_validation_service_pb2_grpc as anomalies_v1_detector_validation_service_pb2_grpc
from acme.anomalies.v1 import detector_workflow_service_pb2_grpc as anomalies_v1_detector_workflow_service_pb2_grpc
from acme.audit.v1 import audit_event_query_service_pb2_grpc as audit_v1_audit_event_query_service_pb2_grpc
from acme.audit.v1 import audit_event_service_pb2_grpc as audit_v1_audit_event_service_pb2_grpc
from acme.audit.v1 import audit_event_validation_service_pb2_grpc as audit_v1_audit_event_validation_service_pb2_grpc
from acme.authorization.v1 import (
    access_policy_query_service_pb2_grpc as authorization_v1_access_policy_query_service_pb2_grpc,
)
from acme.authorization.v1 import access_policy_service_pb2_grpc as authorization_v1_access_policy_service_pb2_grpc
from acme.authorization.v1 import (
    access_policy_validation_service_pb2_grpc as authorization_v1_access_policy_validation_service_pb2_grpc,
)
from acme.banking.v1 import bank_account_query_service_pb2_grpc as banking_v1_bank_account_query_service_pb2_grpc
from acme.boxoffice.v1 import (
    box_office_sale_query_service_pb2_grpc as boxoffice_v1_box_office_sale_query_service_pb2_grpc,
)
from acme.boxoffice.v1 import box_office_sale_service_pb2_grpc as boxoffice_v1_box_office_sale_service_pb2_grpc
from acme.broadcasts.v1 import broadcast_service_pb2_grpc as broadcasts_v1_broadcast_service_pb2_grpc
from acme.campaigns.v1 import (
    marketing_campaign_query_service_pb2_grpc as campaigns_v1_marketing_campaign_query_service_pb2_grpc,
)
from acme.catalog.v1 import product_query_service_pb2_grpc as catalog_v1_product_query_service_pb2_grpc
from acme.certificates.v1 import (
    certificate_calculation_service_pb2_grpc as certificates_v1_certificate_calculation_service_pb2_grpc,
)
from acme.chat.v1 import chat_room_service_pb2_grpc as chat_v1_chat_room_service_pb2_grpc
from acme.concessions.v1 import (
    concession_stand_calculation_service_pb2_grpc as concessions_v1_concession_stand_calculation_service_pb2_grpc,
)
from acme.customers.v1 import (
    customer_calculation_service_pb2_grpc as customers_v1_customer_calculation_service_pb2_grpc,
)
from acme.datasets.v1 import (
    data_schema_calculation_service_pb2_grpc as datasets_v1_data_schema_calculation_service_pb2_grpc,
)
from acme.datasets.v1 import (
    data_schema_validation_service_pb2_grpc as datasets_v1_data_schema_validation_service_pb2_grpc,
)
from acme.datasets.v1 import dataset_query_service_pb2_grpc as datasets_v1_dataset_query_service_pb2_grpc
from acme.datasets.v1 import dataset_service_pb2_grpc as datasets_v1_dataset_service_pb2_grpc
from acme.datasets.v1 import dataset_validation_service_pb2_grpc as datasets_v1_dataset_validation_service_pb2_grpc
from acme.datasets.v1 import (
    dataset_version_calculation_service_pb2_grpc as datasets_v1_dataset_version_calculation_service_pb2_grpc,
)
from acme.datasets.v1 import (
    dataset_version_query_service_pb2_grpc as datasets_v1_dataset_version_query_service_pb2_grpc,
)
from acme.datasets.v1 import (
    dataset_version_validation_service_pb2_grpc as datasets_v1_dataset_version_validation_service_pb2_grpc,
)
from acme.dispatch.v1 import dispatch_order_service_pb2_grpc as dispatch_v1_dispatch_order_service_pb2_grpc
from acme.documents.v1 import document_query_service_pb2_grpc as documents_v1_document_query_service_pb2_grpc
from acme.documents.v1 import document_service_pb2_grpc as documents_v1_document_service_pb2_grpc
from acme.documents.v1 import document_validation_service_pb2_grpc as documents_v1_document_validation_service_pb2_grpc
from acme.drivers.v1 import driver_query_service_pb2_grpc as drivers_v1_driver_query_service_pb2_grpc
from acme.experiments.v1 import experiment_query_service_pb2_grpc as experiments_v1_experiment_query_service_pb2_grpc
from acme.featureflags.v1 import feature_flag_service_pb2_grpc as featureflags_v1_feature_flag_service_pb2_grpc
from acme.featureflags.v1 import (
    feature_flag_validation_service_pb2_grpc as featureflags_v1_feature_flag_validation_service_pb2_grpc,
)
from acme.featurestore.v1 import entity_approval_service_pb2_grpc as featurestore_v1_entity_approval_service_pb2_grpc
from acme.featurestore.v1 import (
    entity_calculation_service_pb2_grpc as featurestore_v1_entity_calculation_service_pb2_grpc,
)
from acme.featurestore.v1 import entity_import_service_pb2_grpc as featurestore_v1_entity_import_service_pb2_grpc
from acme.featurestore.v1 import entity_lifecycle_service_pb2_grpc as featurestore_v1_entity_lifecycle_service_pb2_grpc
from acme.featurestore.v1 import entity_reporting_service_pb2_grpc as featurestore_v1_entity_reporting_service_pb2_grpc
from acme.featurestore.v1 import entity_sync_service_pb2_grpc as featurestore_v1_entity_sync_service_pb2_grpc
from acme.featurestore.v1 import (
    entity_validation_service_pb2_grpc as featurestore_v1_entity_validation_service_pb2_grpc,
)
from acme.featurestore.v1 import entity_workflow_service_pb2_grpc as featurestore_v1_entity_workflow_service_pb2_grpc
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
    feature_value_lifecycle_service_pb2_grpc as featurestore_v1_feature_value_lifecycle_service_pb2_grpc,
)
from acme.featurestore.v1 import (
    feature_value_query_service_pb2_grpc as featurestore_v1_feature_value_query_service_pb2_grpc,
)
from acme.featurestore.v1 import (
    feature_value_reporting_service_pb2_grpc as featurestore_v1_feature_value_reporting_service_pb2_grpc,
)
from acme.featurestore.v1 import (
    feature_value_sync_service_pb2_grpc as featurestore_v1_feature_value_sync_service_pb2_grpc,
)
from acme.featurestore.v1 import (
    feature_value_validation_service_pb2_grpc as featurestore_v1_feature_value_validation_service_pb2_grpc,
)
from acme.featurestore.v1 import (
    feature_value_workflow_service_pb2_grpc as featurestore_v1_feature_value_workflow_service_pb2_grpc,
)
from acme.featurestore.v1 import (
    feature_view_approval_service_pb2_grpc as featurestore_v1_feature_view_approval_service_pb2_grpc,
)
from acme.featurestore.v1 import (
    feature_view_calculation_service_pb2_grpc as featurestore_v1_feature_view_calculation_service_pb2_grpc,
)
from acme.featurestore.v1 import (
    feature_view_lifecycle_service_pb2_grpc as featurestore_v1_feature_view_lifecycle_service_pb2_grpc,
)
from acme.featurestore.v1 import (
    feature_view_query_service_pb2_grpc as featurestore_v1_feature_view_query_service_pb2_grpc,
)
from acme.featurestore.v1 import (
    feature_view_reporting_service_pb2_grpc as featurestore_v1_feature_view_reporting_service_pb2_grpc,
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
from acme.fleet.v1 import vehicle_service_pb2_grpc as fleet_v1_vehicle_service_pb2_grpc
from acme.helpdesk.v1 import ticket_calculation_service_pb2_grpc as helpdesk_v1_ticket_calculation_service_pb2_grpc
from acme.identity.v1 import user_query_service_pb2_grpc as identity_v1_user_query_service_pb2_grpc
from acme.identity.v1 import user_service_pb2_grpc as identity_v1_user_service_pb2_grpc
from acme.identity.v1 import user_validation_service_pb2_grpc as identity_v1_user_validation_service_pb2_grpc
from acme.insurance.v1 import policy_query_service_pb2_grpc as insurance_v1_policy_query_service_pb2_grpc
from acme.keymanagement.v1 import (
    crypto_key_calculation_service_pb2_grpc as keymanagement_v1_crypto_key_calculation_service_pb2_grpc,
)
from acme.ledger.v1 import ledger_account_query_service_pb2_grpc as ledger_v1_ledger_account_query_service_pb2_grpc
from acme.ledger.v1 import ledger_account_service_pb2_grpc as ledger_v1_ledger_account_service_pb2_grpc
from acme.ledger.v1 import (
    ledger_account_validation_service_pb2_grpc as ledger_v1_ledger_account_validation_service_pb2_grpc,
)
from acme.lineage.v1 import impact_calculation_service_pb2_grpc as lineage_v1_impact_calculation_service_pb2_grpc
from acme.lineage.v1 import impact_import_service_pb2_grpc as lineage_v1_impact_import_service_pb2_grpc
from acme.lineage.v1 import impact_lifecycle_service_pb2_grpc as lineage_v1_impact_lifecycle_service_pb2_grpc
from acme.lineage.v1 import impact_sync_service_pb2_grpc as lineage_v1_impact_sync_service_pb2_grpc
from acme.lineage.v1 import impact_validation_service_pb2_grpc as lineage_v1_impact_validation_service_pb2_grpc
from acme.lineage.v1 import impact_workflow_service_pb2_grpc as lineage_v1_impact_workflow_service_pb2_grpc
from acme.lineage.v1 import lineage_edge_approval_service_pb2_grpc as lineage_v1_lineage_edge_approval_service_pb2_grpc
from acme.lineage.v1 import (
    lineage_edge_calculation_service_pb2_grpc as lineage_v1_lineage_edge_calculation_service_pb2_grpc,
)
from acme.lineage.v1 import lineage_edge_import_service_pb2_grpc as lineage_v1_lineage_edge_import_service_pb2_grpc
from acme.lineage.v1 import lineage_edge_query_service_pb2_grpc as lineage_v1_lineage_edge_query_service_pb2_grpc
from acme.lineage.v1 import (
    lineage_edge_reporting_service_pb2_grpc as lineage_v1_lineage_edge_reporting_service_pb2_grpc,
)
from acme.lineage.v1 import lineage_edge_sync_service_pb2_grpc as lineage_v1_lineage_edge_sync_service_pb2_grpc
from acme.lineage.v1 import (
    lineage_edge_validation_service_pb2_grpc as lineage_v1_lineage_edge_validation_service_pb2_grpc,
)
from acme.lineage.v1 import lineage_edge_workflow_service_pb2_grpc as lineage_v1_lineage_edge_workflow_service_pb2_grpc
from acme.lineage.v1 import lineage_node_approval_service_pb2_grpc as lineage_v1_lineage_node_approval_service_pb2_grpc
from acme.lineage.v1 import (
    lineage_node_calculation_service_pb2_grpc as lineage_v1_lineage_node_calculation_service_pb2_grpc,
)
from acme.lineage.v1 import lineage_node_query_service_pb2_grpc as lineage_v1_lineage_node_query_service_pb2_grpc
from acme.lineage.v1 import (
    lineage_node_reporting_service_pb2_grpc as lineage_v1_lineage_node_reporting_service_pb2_grpc,
)
from acme.lineage.v1 import lineage_node_service_pb2_grpc as lineage_v1_lineage_node_service_pb2_grpc
from acme.lineage.v1 import lineage_node_sync_service_pb2_grpc as lineage_v1_lineage_node_sync_service_pb2_grpc
from acme.lineage.v1 import (
    lineage_node_validation_service_pb2_grpc as lineage_v1_lineage_node_validation_service_pb2_grpc,
)
from acme.lineage.v1 import lineage_node_workflow_service_pb2_grpc as lineage_v1_lineage_node_workflow_service_pb2_grpc
from acme.maintenance.v1 import work_order_query_service_pb2_grpc as maintenance_v1_work_order_query_service_pb2_grpc
from acme.merchandising.v1 import (
    collection_query_service_pb2_grpc as merchandising_v1_collection_query_service_pb2_grpc,
)
from acme.metrics.v1 import dashboard_export_service_pb2_grpc as metrics_v1_dashboard_export_service_pb2_grpc
from acme.metrics.v1 import (
    dashboard_notification_service_pb2_grpc as metrics_v1_dashboard_notification_service_pb2_grpc,
)
from acme.metrics.v1 import dashboard_sync_service_pb2_grpc as metrics_v1_dashboard_sync_service_pb2_grpc
from acme.metrics.v1 import dashboard_validation_service_pb2_grpc as metrics_v1_dashboard_validation_service_pb2_grpc
from acme.metrics.v1 import metric_alert_export_service_pb2_grpc as metrics_v1_metric_alert_export_service_pb2_grpc
from acme.metrics.v1 import metric_alert_history_service_pb2_grpc as metrics_v1_metric_alert_history_service_pb2_grpc
from acme.metrics.v1 import (
    metric_alert_notification_service_pb2_grpc as metrics_v1_metric_alert_notification_service_pb2_grpc,
)
from acme.metrics.v1 import metric_alert_query_service_pb2_grpc as metrics_v1_metric_alert_query_service_pb2_grpc
from acme.metrics.v1 import (
    metric_alert_validation_service_pb2_grpc as metrics_v1_metric_alert_validation_service_pb2_grpc,
)
from acme.metrics.v1 import metric_series_export_service_pb2_grpc as metrics_v1_metric_series_export_service_pb2_grpc
from acme.metrics.v1 import metric_series_history_service_pb2_grpc as metrics_v1_metric_series_history_service_pb2_grpc
from acme.metrics.v1 import (
    metric_series_notification_service_pb2_grpc as metrics_v1_metric_series_notification_service_pb2_grpc,
)
from acme.metrics.v1 import metric_series_service_pb2_grpc as metrics_v1_metric_series_service_pb2_grpc
from acme.metrics.v1 import (
    metric_series_validation_service_pb2_grpc as metrics_v1_metric_series_validation_service_pb2_grpc,
)
from acme.notifications.v1 import (
    notification_query_service_pb2_grpc as notifications_v1_notification_query_service_pb2_grpc,
)
from acme.notifications.v1 import notification_service_pb2_grpc as notifications_v1_notification_service_pb2_grpc
from acme.notifications.v1 import (
    notification_validation_service_pb2_grpc as notifications_v1_notification_validation_service_pb2_grpc,
)
from acme.patients.v1 import patient_calculation_service_pb2_grpc as patients_v1_patient_calculation_service_pb2_grpc
from acme.prescriptions.v1 import prescription_service_pb2_grpc as prescriptions_v1_prescription_service_pb2_grpc
from acme.search.v1 import search_index_query_service_pb2_grpc as search_v1_search_index_query_service_pb2_grpc
from acme.search.v1 import search_index_service_pb2_grpc as search_v1_search_index_service_pb2_grpc
from acme.search.v1 import (
    search_index_validation_service_pb2_grpc as search_v1_search_index_validation_service_pb2_grpc,
)
from acme.surveys.v1 import survey_service_pb2_grpc as surveys_v1_survey_service_pb2_grpc
from acme.telehealth.v1 import video_visit_service_pb2_grpc as telehealth_v1_video_visit_service_pb2_grpc
from acme.treasury.v1 import cash_position_query_service_pb2_grpc as treasury_v1_cash_position_query_service_pb2_grpc
from acme.venues.v1 import venue_query_service_pb2_grpc as venues_v1_venue_query_service_pb2_grpc
from acme.venues.v1 import venue_validation_service_pb2_grpc as venues_v1_venue_validation_service_pb2_grpc
from acme.webhooks.v1 import (
    webhook_endpoint_query_service_pb2_grpc as webhooks_v1_webhook_endpoint_query_service_pb2_grpc,
)

from acme_data.domains.featurestore.dependencies import Clients
from acme_data.domains.featurestore.dependencies import Dependencies
from acme_data.domains.featurestore.entity_approval_service import EntityApprovalServicer
from acme_data.domains.featurestore.entity_calculation_service import EntityCalculationServicer
from acme_data.domains.featurestore.entity_import_service import EntityImportServicer
from acme_data.domains.featurestore.entity_lifecycle_service import EntityLifecycleServicer
from acme_data.domains.featurestore.entity_reporting_service import EntityReportingServicer
from acme_data.domains.featurestore.entity_sync_service import EntitySyncServicer
from acme_data.domains.featurestore.entity_validation_service import EntityValidationServicer
from acme_data.domains.featurestore.entity_workflow_service import EntityWorkflowServicer
from acme_data.domains.featurestore.events import subscribe
from acme_data.domains.featurestore.feature_value_approval_service import FeatureValueApprovalServicer
from acme_data.domains.featurestore.feature_value_calculation_service import FeatureValueCalculationServicer
from acme_data.domains.featurestore.feature_value_import_service import FeatureValueImportServicer
from acme_data.domains.featurestore.feature_value_lifecycle_service import FeatureValueLifecycleServicer
from acme_data.domains.featurestore.feature_value_query_service import FeatureValueQueryServicer
from acme_data.domains.featurestore.feature_value_reporting_service import FeatureValueReportingServicer
from acme_data.domains.featurestore.feature_value_sync_service import FeatureValueSyncServicer
from acme_data.domains.featurestore.feature_value_validation_service import FeatureValueValidationServicer
from acme_data.domains.featurestore.feature_value_workflow_service import FeatureValueWorkflowServicer
from acme_data.domains.featurestore.feature_view_approval_service import FeatureViewApprovalServicer
from acme_data.domains.featurestore.feature_view_calculation_service import FeatureViewCalculationServicer
from acme_data.domains.featurestore.feature_view_lifecycle_service import FeatureViewLifecycleServicer
from acme_data.domains.featurestore.feature_view_query_service import FeatureViewQueryServicer
from acme_data.domains.featurestore.feature_view_reporting_service import FeatureViewReportingServicer
from acme_data.domains.featurestore.feature_view_service import FeatureViewServicer
from acme_data.domains.featurestore.feature_view_sync_service import FeatureViewSyncServicer
from acme_data.domains.featurestore.feature_view_validation_service import FeatureViewValidationServicer
from acme_data.domains.featurestore.feature_view_workflow_service import FeatureViewWorkflowServicer
from acme_data.domains.featurestore.repository import DomainRepository
from acme_data.platform.container import Container
from acme_data.platform.container import Factory


def dependencies(container: Container) -> Dependencies:
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
    anomalies_anomaly_feedback_validation = container.singleton(
        anomalies_v1_anomaly_feedback_validation_service_pb2_grpc.AnomalyFeedbackValidationServiceStub,
        lambda: anomalies_v1_anomaly_feedback_validation_service_pb2_grpc.AnomalyFeedbackValidationServiceStub(
            container.channel
        )
    )
    anomalies_anomaly_feedback_workflow = container.singleton(
        anomalies_v1_anomaly_feedback_workflow_service_pb2_grpc.AnomalyFeedbackWorkflowServiceStub,
        lambda: anomalies_v1_anomaly_feedback_workflow_service_pb2_grpc.AnomalyFeedbackWorkflowServiceStub(
            container.channel
        )
    )
    anomalies_anomaly_query = container.singleton(
        anomalies_v1_anomaly_query_service_pb2_grpc.AnomalyQueryServiceStub,
        lambda: anomalies_v1_anomaly_query_service_pb2_grpc.AnomalyQueryServiceStub(container.channel)
    )
    anomalies_anomaly = container.singleton(
        anomalies_v1_anomaly_service_pb2_grpc.AnomalyServiceStub,
        lambda: anomalies_v1_anomaly_service_pb2_grpc.AnomalyServiceStub(container.channel)
    )
    anomalies_anomaly_workflow = container.singleton(
        anomalies_v1_anomaly_workflow_service_pb2_grpc.AnomalyWorkflowServiceStub,
        lambda: anomalies_v1_anomaly_workflow_service_pb2_grpc.AnomalyWorkflowServiceStub(container.channel)
    )
    anomalies_detector_approval = container.singleton(
        anomalies_v1_detector_approval_service_pb2_grpc.DetectorApprovalServiceStub,
        lambda: anomalies_v1_detector_approval_service_pb2_grpc.DetectorApprovalServiceStub(container.channel)
    )
    anomalies_detector_query = container.singleton(
        anomalies_v1_detector_query_service_pb2_grpc.DetectorQueryServiceStub,
        lambda: anomalies_v1_detector_query_service_pb2_grpc.DetectorQueryServiceStub(container.channel)
    )
    anomalies_detector_validation = container.singleton(
        anomalies_v1_detector_validation_service_pb2_grpc.DetectorValidationServiceStub,
        lambda: anomalies_v1_detector_validation_service_pb2_grpc.DetectorValidationServiceStub(container.channel)
    )
    anomalies_detector_workflow = container.singleton(
        anomalies_v1_detector_workflow_service_pb2_grpc.DetectorWorkflowServiceStub,
        lambda: anomalies_v1_detector_workflow_service_pb2_grpc.DetectorWorkflowServiceStub(container.channel)
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
    authorization_access_policy_query = container.singleton(
        authorization_v1_access_policy_query_service_pb2_grpc.AccessPolicyQueryServiceStub,
        lambda: authorization_v1_access_policy_query_service_pb2_grpc.AccessPolicyQueryServiceStub(container.channel)
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
    boxoffice_box_office_sale_query = container.singleton(
        boxoffice_v1_box_office_sale_query_service_pb2_grpc.BoxOfficeSaleQueryServiceStub,
        lambda: boxoffice_v1_box_office_sale_query_service_pb2_grpc.BoxOfficeSaleQueryServiceStub(container.channel)
    )
    boxoffice_box_office_sale = container.singleton(
        boxoffice_v1_box_office_sale_service_pb2_grpc.BoxOfficeSaleServiceStub,
        lambda: boxoffice_v1_box_office_sale_service_pb2_grpc.BoxOfficeSaleServiceStub(container.channel)
    )
    broadcasts_broadcast = container.singleton(
        broadcasts_v1_broadcast_service_pb2_grpc.BroadcastServiceStub,
        lambda: broadcasts_v1_broadcast_service_pb2_grpc.BroadcastServiceStub(container.channel)
    )
    campaigns_marketing_campaign_query = container.singleton(
        campaigns_v1_marketing_campaign_query_service_pb2_grpc.MarketingCampaignQueryServiceStub,
        lambda: campaigns_v1_marketing_campaign_query_service_pb2_grpc.MarketingCampaignQueryServiceStub(
            container.channel
        )
    )
    catalog_product_query = container.singleton(
        catalog_v1_product_query_service_pb2_grpc.ProductQueryServiceStub,
        lambda: catalog_v1_product_query_service_pb2_grpc.ProductQueryServiceStub(container.channel)
    )
    certificates_certificate_calculation = container.singleton(
        certificates_v1_certificate_calculation_service_pb2_grpc.CertificateCalculationServiceStub,
        lambda: certificates_v1_certificate_calculation_service_pb2_grpc.CertificateCalculationServiceStub(
            container.channel
        )
    )
    chat_chat_room = container.singleton(
        chat_v1_chat_room_service_pb2_grpc.ChatRoomServiceStub,
        lambda: chat_v1_chat_room_service_pb2_grpc.ChatRoomServiceStub(container.channel)
    )
    concessions_concession_stand_calculation = container.singleton(
        concessions_v1_concession_stand_calculation_service_pb2_grpc.ConcessionStandCalculationServiceStub,
        lambda: concessions_v1_concession_stand_calculation_service_pb2_grpc.ConcessionStandCalculationServiceStub(
            container.channel
        )
    )
    customers_customer_calculation = container.singleton(
        customers_v1_customer_calculation_service_pb2_grpc.CustomerCalculationServiceStub,
        lambda: customers_v1_customer_calculation_service_pb2_grpc.CustomerCalculationServiceStub(container.channel)
    )
    datasets_data_schema_calculation = container.singleton(
        datasets_v1_data_schema_calculation_service_pb2_grpc.DataSchemaCalculationServiceStub,
        lambda: datasets_v1_data_schema_calculation_service_pb2_grpc.DataSchemaCalculationServiceStub(container.channel)
    )
    datasets_data_schema_validation = container.singleton(
        datasets_v1_data_schema_validation_service_pb2_grpc.DataSchemaValidationServiceStub,
        lambda: datasets_v1_data_schema_validation_service_pb2_grpc.DataSchemaValidationServiceStub(container.channel)
    )
    datasets_dataset_query = container.singleton(
        datasets_v1_dataset_query_service_pb2_grpc.DatasetQueryServiceStub,
        lambda: datasets_v1_dataset_query_service_pb2_grpc.DatasetQueryServiceStub(container.channel)
    )
    datasets_dataset = container.singleton(
        datasets_v1_dataset_service_pb2_grpc.DatasetServiceStub,
        lambda: datasets_v1_dataset_service_pb2_grpc.DatasetServiceStub(container.channel)
    )
    datasets_dataset_validation = container.singleton(
        datasets_v1_dataset_validation_service_pb2_grpc.DatasetValidationServiceStub,
        lambda: datasets_v1_dataset_validation_service_pb2_grpc.DatasetValidationServiceStub(container.channel)
    )
    datasets_dataset_version_calculation = container.singleton(
        datasets_v1_dataset_version_calculation_service_pb2_grpc.DatasetVersionCalculationServiceStub,
        lambda: datasets_v1_dataset_version_calculation_service_pb2_grpc.DatasetVersionCalculationServiceStub(
            container.channel
        )
    )
    datasets_dataset_version_query = container.singleton(
        datasets_v1_dataset_version_query_service_pb2_grpc.DatasetVersionQueryServiceStub,
        lambda: datasets_v1_dataset_version_query_service_pb2_grpc.DatasetVersionQueryServiceStub(container.channel)
    )
    datasets_dataset_version_validation = container.singleton(
        datasets_v1_dataset_version_validation_service_pb2_grpc.DatasetVersionValidationServiceStub,
        lambda: datasets_v1_dataset_version_validation_service_pb2_grpc.DatasetVersionValidationServiceStub(
            container.channel
        )
    )
    dispatch_dispatch_order = container.singleton(
        dispatch_v1_dispatch_order_service_pb2_grpc.DispatchOrderServiceStub,
        lambda: dispatch_v1_dispatch_order_service_pb2_grpc.DispatchOrderServiceStub(container.channel)
    )
    documents_document_query = container.singleton(
        documents_v1_document_query_service_pb2_grpc.DocumentQueryServiceStub,
        lambda: documents_v1_document_query_service_pb2_grpc.DocumentQueryServiceStub(container.channel)
    )
    documents_document = container.singleton(
        documents_v1_document_service_pb2_grpc.DocumentServiceStub,
        lambda: documents_v1_document_service_pb2_grpc.DocumentServiceStub(container.channel)
    )
    documents_document_validation = container.singleton(
        documents_v1_document_validation_service_pb2_grpc.DocumentValidationServiceStub,
        lambda: documents_v1_document_validation_service_pb2_grpc.DocumentValidationServiceStub(container.channel)
    )
    drivers_driver_query = container.singleton(
        drivers_v1_driver_query_service_pb2_grpc.DriverQueryServiceStub,
        lambda: drivers_v1_driver_query_service_pb2_grpc.DriverQueryServiceStub(container.channel)
    )
    experiments_experiment_query = container.singleton(
        experiments_v1_experiment_query_service_pb2_grpc.ExperimentQueryServiceStub,
        lambda: experiments_v1_experiment_query_service_pb2_grpc.ExperimentQueryServiceStub(container.channel)
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
    featurestore_entity_import = container.singleton(
        featurestore_v1_entity_import_service_pb2_grpc.EntityImportServiceStub,
        lambda: featurestore_v1_entity_import_service_pb2_grpc.EntityImportServiceStub(container.channel)
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
    featurestore_feature_value_lifecycle = container.singleton(
        featurestore_v1_feature_value_lifecycle_service_pb2_grpc.FeatureValueLifecycleServiceStub,
        lambda: featurestore_v1_feature_value_lifecycle_service_pb2_grpc.FeatureValueLifecycleServiceStub(
            container.channel
        )
    )
    featurestore_feature_value_query = container.singleton(
        featurestore_v1_feature_value_query_service_pb2_grpc.FeatureValueQueryServiceStub,
        lambda: featurestore_v1_feature_value_query_service_pb2_grpc.FeatureValueQueryServiceStub(container.channel)
    )
    featurestore_feature_value_reporting = container.singleton(
        featurestore_v1_feature_value_reporting_service_pb2_grpc.FeatureValueReportingServiceStub,
        lambda: featurestore_v1_feature_value_reporting_service_pb2_grpc.FeatureValueReportingServiceStub(
            container.channel
        )
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
    featurestore_feature_view_lifecycle = container.singleton(
        featurestore_v1_feature_view_lifecycle_service_pb2_grpc.FeatureViewLifecycleServiceStub,
        lambda: featurestore_v1_feature_view_lifecycle_service_pb2_grpc.FeatureViewLifecycleServiceStub(
            container.channel
        )
    )
    featurestore_feature_view_query = container.singleton(
        featurestore_v1_feature_view_query_service_pb2_grpc.FeatureViewQueryServiceStub,
        lambda: featurestore_v1_feature_view_query_service_pb2_grpc.FeatureViewQueryServiceStub(container.channel)
    )
    featurestore_feature_view_reporting = container.singleton(
        featurestore_v1_feature_view_reporting_service_pb2_grpc.FeatureViewReportingServiceStub,
        lambda: featurestore_v1_feature_view_reporting_service_pb2_grpc.FeatureViewReportingServiceStub(
            container.channel
        )
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
    fleet_vehicle = container.singleton(
        fleet_v1_vehicle_service_pb2_grpc.VehicleServiceStub,
        lambda: fleet_v1_vehicle_service_pb2_grpc.VehicleServiceStub(container.channel)
    )
    helpdesk_ticket_calculation = container.singleton(
        helpdesk_v1_ticket_calculation_service_pb2_grpc.TicketCalculationServiceStub,
        lambda: helpdesk_v1_ticket_calculation_service_pb2_grpc.TicketCalculationServiceStub(container.channel)
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
    insurance_policy_query = container.singleton(
        insurance_v1_policy_query_service_pb2_grpc.PolicyQueryServiceStub,
        lambda: insurance_v1_policy_query_service_pb2_grpc.PolicyQueryServiceStub(container.channel)
    )
    keymanagement_crypto_key_calculation = container.singleton(
        keymanagement_v1_crypto_key_calculation_service_pb2_grpc.CryptoKeyCalculationServiceStub,
        lambda: keymanagement_v1_crypto_key_calculation_service_pb2_grpc.CryptoKeyCalculationServiceStub(
            container.channel
        )
    )
    ledger_ledger_account_query = container.singleton(
        ledger_v1_ledger_account_query_service_pb2_grpc.LedgerAccountQueryServiceStub,
        lambda: ledger_v1_ledger_account_query_service_pb2_grpc.LedgerAccountQueryServiceStub(container.channel)
    )
    ledger_ledger_account = container.singleton(
        ledger_v1_ledger_account_service_pb2_grpc.LedgerAccountServiceStub,
        lambda: ledger_v1_ledger_account_service_pb2_grpc.LedgerAccountServiceStub(container.channel)
    )
    ledger_ledger_account_validation = container.singleton(
        ledger_v1_ledger_account_validation_service_pb2_grpc.LedgerAccountValidationServiceStub,
        lambda: ledger_v1_ledger_account_validation_service_pb2_grpc.LedgerAccountValidationServiceStub(
            container.channel
        )
    )
    lineage_impact_calculation = container.singleton(
        lineage_v1_impact_calculation_service_pb2_grpc.ImpactCalculationServiceStub,
        lambda: lineage_v1_impact_calculation_service_pb2_grpc.ImpactCalculationServiceStub(container.channel)
    )
    lineage_impact_import = container.singleton(
        lineage_v1_impact_import_service_pb2_grpc.ImpactImportServiceStub,
        lambda: lineage_v1_impact_import_service_pb2_grpc.ImpactImportServiceStub(container.channel)
    )
    lineage_impact_lifecycle = container.singleton(
        lineage_v1_impact_lifecycle_service_pb2_grpc.ImpactLifecycleServiceStub,
        lambda: lineage_v1_impact_lifecycle_service_pb2_grpc.ImpactLifecycleServiceStub(container.channel)
    )
    lineage_impact_sync = container.singleton(
        lineage_v1_impact_sync_service_pb2_grpc.ImpactSyncServiceStub,
        lambda: lineage_v1_impact_sync_service_pb2_grpc.ImpactSyncServiceStub(container.channel)
    )
    lineage_impact_validation = container.singleton(
        lineage_v1_impact_validation_service_pb2_grpc.ImpactValidationServiceStub,
        lambda: lineage_v1_impact_validation_service_pb2_grpc.ImpactValidationServiceStub(container.channel)
    )
    lineage_impact_workflow = container.singleton(
        lineage_v1_impact_workflow_service_pb2_grpc.ImpactWorkflowServiceStub,
        lambda: lineage_v1_impact_workflow_service_pb2_grpc.ImpactWorkflowServiceStub(container.channel)
    )
    lineage_lineage_edge_approval = container.singleton(
        lineage_v1_lineage_edge_approval_service_pb2_grpc.LineageEdgeApprovalServiceStub,
        lambda: lineage_v1_lineage_edge_approval_service_pb2_grpc.LineageEdgeApprovalServiceStub(container.channel)
    )
    lineage_lineage_edge_calculation = container.singleton(
        lineage_v1_lineage_edge_calculation_service_pb2_grpc.LineageEdgeCalculationServiceStub,
        lambda: lineage_v1_lineage_edge_calculation_service_pb2_grpc.LineageEdgeCalculationServiceStub(
            container.channel
        )
    )
    lineage_lineage_edge_import = container.singleton(
        lineage_v1_lineage_edge_import_service_pb2_grpc.LineageEdgeImportServiceStub,
        lambda: lineage_v1_lineage_edge_import_service_pb2_grpc.LineageEdgeImportServiceStub(container.channel)
    )
    lineage_lineage_edge_query = container.singleton(
        lineage_v1_lineage_edge_query_service_pb2_grpc.LineageEdgeQueryServiceStub,
        lambda: lineage_v1_lineage_edge_query_service_pb2_grpc.LineageEdgeQueryServiceStub(container.channel)
    )
    lineage_lineage_edge_reporting = container.singleton(
        lineage_v1_lineage_edge_reporting_service_pb2_grpc.LineageEdgeReportingServiceStub,
        lambda: lineage_v1_lineage_edge_reporting_service_pb2_grpc.LineageEdgeReportingServiceStub(container.channel)
    )
    lineage_lineage_edge_sync = container.singleton(
        lineage_v1_lineage_edge_sync_service_pb2_grpc.LineageEdgeSyncServiceStub,
        lambda: lineage_v1_lineage_edge_sync_service_pb2_grpc.LineageEdgeSyncServiceStub(container.channel)
    )
    lineage_lineage_edge_validation = container.singleton(
        lineage_v1_lineage_edge_validation_service_pb2_grpc.LineageEdgeValidationServiceStub,
        lambda: lineage_v1_lineage_edge_validation_service_pb2_grpc.LineageEdgeValidationServiceStub(container.channel)
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
    lineage_lineage_node = container.singleton(
        lineage_v1_lineage_node_service_pb2_grpc.LineageNodeServiceStub,
        lambda: lineage_v1_lineage_node_service_pb2_grpc.LineageNodeServiceStub(container.channel)
    )
    lineage_lineage_node_sync = container.singleton(
        lineage_v1_lineage_node_sync_service_pb2_grpc.LineageNodeSyncServiceStub,
        lambda: lineage_v1_lineage_node_sync_service_pb2_grpc.LineageNodeSyncServiceStub(container.channel)
    )
    lineage_lineage_node_validation = container.singleton(
        lineage_v1_lineage_node_validation_service_pb2_grpc.LineageNodeValidationServiceStub,
        lambda: lineage_v1_lineage_node_validation_service_pb2_grpc.LineageNodeValidationServiceStub(container.channel)
    )
    lineage_lineage_node_workflow = container.singleton(
        lineage_v1_lineage_node_workflow_service_pb2_grpc.LineageNodeWorkflowServiceStub,
        lambda: lineage_v1_lineage_node_workflow_service_pb2_grpc.LineageNodeWorkflowServiceStub(container.channel)
    )
    maintenance_work_order_query = container.singleton(
        maintenance_v1_work_order_query_service_pb2_grpc.WorkOrderQueryServiceStub,
        lambda: maintenance_v1_work_order_query_service_pb2_grpc.WorkOrderQueryServiceStub(container.channel)
    )
    merchandising_collection_query = container.singleton(
        merchandising_v1_collection_query_service_pb2_grpc.CollectionQueryServiceStub,
        lambda: merchandising_v1_collection_query_service_pb2_grpc.CollectionQueryServiceStub(container.channel)
    )
    metrics_dashboard_export = container.singleton(
        metrics_v1_dashboard_export_service_pb2_grpc.DashboardExportServiceStub,
        lambda: metrics_v1_dashboard_export_service_pb2_grpc.DashboardExportServiceStub(container.channel)
    )
    metrics_dashboard_notification = container.singleton(
        metrics_v1_dashboard_notification_service_pb2_grpc.DashboardNotificationServiceStub,
        lambda: metrics_v1_dashboard_notification_service_pb2_grpc.DashboardNotificationServiceStub(container.channel)
    )
    metrics_dashboard_sync = container.singleton(
        metrics_v1_dashboard_sync_service_pb2_grpc.DashboardSyncServiceStub,
        lambda: metrics_v1_dashboard_sync_service_pb2_grpc.DashboardSyncServiceStub(container.channel)
    )
    metrics_dashboard_validation = container.singleton(
        metrics_v1_dashboard_validation_service_pb2_grpc.DashboardValidationServiceStub,
        lambda: metrics_v1_dashboard_validation_service_pb2_grpc.DashboardValidationServiceStub(container.channel)
    )
    metrics_metric_alert_export = container.singleton(
        metrics_v1_metric_alert_export_service_pb2_grpc.MetricAlertExportServiceStub,
        lambda: metrics_v1_metric_alert_export_service_pb2_grpc.MetricAlertExportServiceStub(container.channel)
    )
    metrics_metric_alert_history = container.singleton(
        metrics_v1_metric_alert_history_service_pb2_grpc.MetricAlertHistoryServiceStub,
        lambda: metrics_v1_metric_alert_history_service_pb2_grpc.MetricAlertHistoryServiceStub(container.channel)
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
    metrics_metric_series_export = container.singleton(
        metrics_v1_metric_series_export_service_pb2_grpc.MetricSeriesExportServiceStub,
        lambda: metrics_v1_metric_series_export_service_pb2_grpc.MetricSeriesExportServiceStub(container.channel)
    )
    metrics_metric_series_history = container.singleton(
        metrics_v1_metric_series_history_service_pb2_grpc.MetricSeriesHistoryServiceStub,
        lambda: metrics_v1_metric_series_history_service_pb2_grpc.MetricSeriesHistoryServiceStub(container.channel)
    )
    metrics_metric_series_notification = container.singleton(
        metrics_v1_metric_series_notification_service_pb2_grpc.MetricSeriesNotificationServiceStub,
        lambda: metrics_v1_metric_series_notification_service_pb2_grpc.MetricSeriesNotificationServiceStub(
            container.channel
        )
    )
    metrics_metric_series = container.singleton(
        metrics_v1_metric_series_service_pb2_grpc.MetricSeriesServiceStub,
        lambda: metrics_v1_metric_series_service_pb2_grpc.MetricSeriesServiceStub(container.channel)
    )
    metrics_metric_series_validation = container.singleton(
        metrics_v1_metric_series_validation_service_pb2_grpc.MetricSeriesValidationServiceStub,
        lambda: metrics_v1_metric_series_validation_service_pb2_grpc.MetricSeriesValidationServiceStub(
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
    notifications_notification_validation = container.singleton(
        notifications_v1_notification_validation_service_pb2_grpc.NotificationValidationServiceStub,
        lambda: notifications_v1_notification_validation_service_pb2_grpc.NotificationValidationServiceStub(
            container.channel
        )
    )
    patients_patient_calculation = container.singleton(
        patients_v1_patient_calculation_service_pb2_grpc.PatientCalculationServiceStub,
        lambda: patients_v1_patient_calculation_service_pb2_grpc.PatientCalculationServiceStub(container.channel)
    )
    prescriptions_prescription = container.singleton(
        prescriptions_v1_prescription_service_pb2_grpc.PrescriptionServiceStub,
        lambda: prescriptions_v1_prescription_service_pb2_grpc.PrescriptionServiceStub(container.channel)
    )
    search_search_index_query = container.singleton(
        search_v1_search_index_query_service_pb2_grpc.SearchIndexQueryServiceStub,
        lambda: search_v1_search_index_query_service_pb2_grpc.SearchIndexQueryServiceStub(container.channel)
    )
    search_search_index = container.singleton(
        search_v1_search_index_service_pb2_grpc.SearchIndexServiceStub,
        lambda: search_v1_search_index_service_pb2_grpc.SearchIndexServiceStub(container.channel)
    )
    search_search_index_validation = container.singleton(
        search_v1_search_index_validation_service_pb2_grpc.SearchIndexValidationServiceStub,
        lambda: search_v1_search_index_validation_service_pb2_grpc.SearchIndexValidationServiceStub(container.channel)
    )
    surveys_survey = container.singleton(
        surveys_v1_survey_service_pb2_grpc.SurveyServiceStub,
        lambda: surveys_v1_survey_service_pb2_grpc.SurveyServiceStub(container.channel)
    )
    telehealth_video_visit = container.singleton(
        telehealth_v1_video_visit_service_pb2_grpc.VideoVisitServiceStub,
        lambda: telehealth_v1_video_visit_service_pb2_grpc.VideoVisitServiceStub(container.channel)
    )
    treasury_cash_position_query = container.singleton(
        treasury_v1_cash_position_query_service_pb2_grpc.CashPositionQueryServiceStub,
        lambda: treasury_v1_cash_position_query_service_pb2_grpc.CashPositionQueryServiceStub(container.channel)
    )
    venues_venue_query = container.singleton(
        venues_v1_venue_query_service_pb2_grpc.VenueQueryServiceStub,
        lambda: venues_v1_venue_query_service_pb2_grpc.VenueQueryServiceStub(container.channel)
    )
    venues_venue_validation = container.singleton(
        venues_v1_venue_validation_service_pb2_grpc.VenueValidationServiceStub,
        lambda: venues_v1_venue_validation_service_pb2_grpc.VenueValidationServiceStub(container.channel)
    )
    webhooks_webhook_endpoint_query = container.singleton(
        webhooks_v1_webhook_endpoint_query_service_pb2_grpc.WebhookEndpointQueryServiceStub,
        lambda: webhooks_v1_webhook_endpoint_query_service_pb2_grpc.WebhookEndpointQueryServiceStub(container.channel)
    )
    clients = Clients(
        anomalies_anomaly_approval=anomalies_anomaly_approval,
        anomalies_anomaly_feedback_approval=anomalies_anomaly_feedback_approval,
        anomalies_anomaly_feedback_calculation=anomalies_anomaly_feedback_calculation,
        anomalies_anomaly_feedback_validation=anomalies_anomaly_feedback_validation,
        anomalies_anomaly_feedback_workflow=anomalies_anomaly_feedback_workflow,
        anomalies_anomaly_query=anomalies_anomaly_query,
        anomalies_anomaly=anomalies_anomaly,
        anomalies_anomaly_workflow=anomalies_anomaly_workflow,
        anomalies_detector_approval=anomalies_detector_approval,
        anomalies_detector_query=anomalies_detector_query,
        anomalies_detector_validation=anomalies_detector_validation,
        anomalies_detector_workflow=anomalies_detector_workflow,
        audit_audit_event_query=audit_audit_event_query,
        audit_audit_event=audit_audit_event,
        audit_audit_event_validation=audit_audit_event_validation,
        authorization_access_policy_query=authorization_access_policy_query,
        authorization_access_policy=authorization_access_policy,
        authorization_access_policy_validation=authorization_access_policy_validation,
        banking_bank_account_query=banking_bank_account_query,
        boxoffice_box_office_sale_query=boxoffice_box_office_sale_query,
        boxoffice_box_office_sale=boxoffice_box_office_sale,
        broadcasts_broadcast=broadcasts_broadcast,
        campaigns_marketing_campaign_query=campaigns_marketing_campaign_query,
        catalog_product_query=catalog_product_query,
        certificates_certificate_calculation=certificates_certificate_calculation,
        chat_chat_room=chat_chat_room,
        concessions_concession_stand_calculation=concessions_concession_stand_calculation,
        customers_customer_calculation=customers_customer_calculation,
        datasets_data_schema_calculation=datasets_data_schema_calculation,
        datasets_data_schema_validation=datasets_data_schema_validation,
        datasets_dataset_query=datasets_dataset_query,
        datasets_dataset=datasets_dataset,
        datasets_dataset_validation=datasets_dataset_validation,
        datasets_dataset_version_calculation=datasets_dataset_version_calculation,
        datasets_dataset_version_query=datasets_dataset_version_query,
        datasets_dataset_version_validation=datasets_dataset_version_validation,
        dispatch_dispatch_order=dispatch_dispatch_order,
        documents_document_query=documents_document_query,
        documents_document=documents_document,
        documents_document_validation=documents_document_validation,
        drivers_driver_query=drivers_driver_query,
        experiments_experiment_query=experiments_experiment_query,
        featureflags_feature_flag=featureflags_feature_flag,
        featureflags_feature_flag_validation=featureflags_feature_flag_validation,
        featurestore_entity_approval=featurestore_entity_approval,
        featurestore_entity_calculation=featurestore_entity_calculation,
        featurestore_entity_import=featurestore_entity_import,
        featurestore_entity_lifecycle=featurestore_entity_lifecycle,
        featurestore_entity_reporting=featurestore_entity_reporting,
        featurestore_entity_sync=featurestore_entity_sync,
        featurestore_entity_validation=featurestore_entity_validation,
        featurestore_feature_value_approval=featurestore_feature_value_approval,
        featurestore_feature_value_calculation=featurestore_feature_value_calculation,
        featurestore_feature_value_import=featurestore_feature_value_import,
        featurestore_feature_value_lifecycle=featurestore_feature_value_lifecycle,
        featurestore_feature_value_query=featurestore_feature_value_query,
        featurestore_feature_value_reporting=featurestore_feature_value_reporting,
        featurestore_feature_value_sync=featurestore_feature_value_sync,
        featurestore_feature_value_validation=featurestore_feature_value_validation,
        featurestore_feature_view_approval=featurestore_feature_view_approval,
        featurestore_feature_view_calculation=featurestore_feature_view_calculation,
        featurestore_feature_view_lifecycle=featurestore_feature_view_lifecycle,
        featurestore_feature_view_query=featurestore_feature_view_query,
        featurestore_feature_view_reporting=featurestore_feature_view_reporting,
        featurestore_feature_view=featurestore_feature_view,
        featurestore_feature_view_sync=featurestore_feature_view_sync,
        featurestore_feature_view_validation=featurestore_feature_view_validation,
        fleet_vehicle=fleet_vehicle,
        helpdesk_ticket_calculation=helpdesk_ticket_calculation,
        identity_user_query=identity_user_query,
        identity_user=identity_user,
        identity_user_validation=identity_user_validation,
        insurance_policy_query=insurance_policy_query,
        keymanagement_crypto_key_calculation=keymanagement_crypto_key_calculation,
        ledger_ledger_account_query=ledger_ledger_account_query,
        ledger_ledger_account=ledger_ledger_account,
        ledger_ledger_account_validation=ledger_ledger_account_validation,
        lineage_impact_calculation=lineage_impact_calculation,
        lineage_impact_import=lineage_impact_import,
        lineage_impact_lifecycle=lineage_impact_lifecycle,
        lineage_impact_sync=lineage_impact_sync,
        lineage_impact_validation=lineage_impact_validation,
        lineage_impact_workflow=lineage_impact_workflow,
        lineage_lineage_edge_approval=lineage_lineage_edge_approval,
        lineage_lineage_edge_calculation=lineage_lineage_edge_calculation,
        lineage_lineage_edge_import=lineage_lineage_edge_import,
        lineage_lineage_edge_query=lineage_lineage_edge_query,
        lineage_lineage_edge_reporting=lineage_lineage_edge_reporting,
        lineage_lineage_edge_sync=lineage_lineage_edge_sync,
        lineage_lineage_edge_validation=lineage_lineage_edge_validation,
        lineage_lineage_edge_workflow=lineage_lineage_edge_workflow,
        lineage_lineage_node_approval=lineage_lineage_node_approval,
        lineage_lineage_node_calculation=lineage_lineage_node_calculation,
        lineage_lineage_node_query=lineage_lineage_node_query,
        lineage_lineage_node_reporting=lineage_lineage_node_reporting,
        lineage_lineage_node=lineage_lineage_node,
        lineage_lineage_node_sync=lineage_lineage_node_sync,
        lineage_lineage_node_validation=lineage_lineage_node_validation,
        lineage_lineage_node_workflow=lineage_lineage_node_workflow,
        maintenance_work_order_query=maintenance_work_order_query,
        merchandising_collection_query=merchandising_collection_query,
        metrics_dashboard_export=metrics_dashboard_export,
        metrics_dashboard_notification=metrics_dashboard_notification,
        metrics_dashboard_sync=metrics_dashboard_sync,
        metrics_dashboard_validation=metrics_dashboard_validation,
        metrics_metric_alert_export=metrics_metric_alert_export,
        metrics_metric_alert_history=metrics_metric_alert_history,
        metrics_metric_alert_notification=metrics_metric_alert_notification,
        metrics_metric_alert_query=metrics_metric_alert_query,
        metrics_metric_alert_validation=metrics_metric_alert_validation,
        metrics_metric_series_export=metrics_metric_series_export,
        metrics_metric_series_history=metrics_metric_series_history,
        metrics_metric_series_notification=metrics_metric_series_notification,
        metrics_metric_series=metrics_metric_series,
        metrics_metric_series_validation=metrics_metric_series_validation,
        notifications_notification_query=notifications_notification_query,
        notifications_notification=notifications_notification,
        notifications_notification_validation=notifications_notification_validation,
        patients_patient_calculation=patients_patient_calculation,
        prescriptions_prescription=prescriptions_prescription,
        search_search_index_query=search_search_index_query,
        search_search_index=search_search_index,
        search_search_index_validation=search_search_index_validation,
        surveys_survey=surveys_survey,
        telehealth_video_visit=telehealth_video_visit,
        treasury_cash_position_query=treasury_cash_position_query,
        venues_venue_query=venues_venue_query,
        venues_venue_validation=venues_venue_validation,
        webhooks_webhook_endpoint_query=webhooks_webhook_endpoint_query,
        registry={
            'acme.anomalies.v1.AnomalyApprovalService': anomalies_anomaly_approval,
            'acme.anomalies.v1.AnomalyFeedbackApprovalService': anomalies_anomaly_feedback_approval,
            'acme.anomalies.v1.AnomalyFeedbackCalculationService': anomalies_anomaly_feedback_calculation,
            'acme.anomalies.v1.AnomalyFeedbackValidationService': anomalies_anomaly_feedback_validation,
            'acme.anomalies.v1.AnomalyFeedbackWorkflowService': anomalies_anomaly_feedback_workflow,
            'acme.anomalies.v1.AnomalyQueryService': anomalies_anomaly_query,
            'acme.anomalies.v1.AnomalyService': anomalies_anomaly,
            'acme.anomalies.v1.AnomalyWorkflowService': anomalies_anomaly_workflow,
            'acme.anomalies.v1.DetectorApprovalService': anomalies_detector_approval,
            'acme.anomalies.v1.DetectorQueryService': anomalies_detector_query,
            'acme.anomalies.v1.DetectorValidationService': anomalies_detector_validation,
            'acme.anomalies.v1.DetectorWorkflowService': anomalies_detector_workflow,
            'acme.audit.v1.AuditEventQueryService': audit_audit_event_query,
            'acme.audit.v1.AuditEventService': audit_audit_event,
            'acme.audit.v1.AuditEventValidationService': audit_audit_event_validation,
            'acme.authorization.v1.AccessPolicyQueryService': authorization_access_policy_query,
            'acme.authorization.v1.AccessPolicyService': authorization_access_policy,
            'acme.authorization.v1.AccessPolicyValidationService': authorization_access_policy_validation,
            'acme.banking.v1.BankAccountQueryService': banking_bank_account_query,
            'acme.boxoffice.v1.BoxOfficeSaleQueryService': boxoffice_box_office_sale_query,
            'acme.boxoffice.v1.BoxOfficeSaleService': boxoffice_box_office_sale,
            'acme.broadcasts.v1.BroadcastService': broadcasts_broadcast,
            'acme.campaigns.v1.MarketingCampaignQueryService': campaigns_marketing_campaign_query,
            'acme.catalog.v1.ProductQueryService': catalog_product_query,
            'acme.certificates.v1.CertificateCalculationService': certificates_certificate_calculation,
            'acme.chat.v1.ChatRoomService': chat_chat_room,
            'acme.concessions.v1.ConcessionStandCalculationService': concessions_concession_stand_calculation,
            'acme.customers.v1.CustomerCalculationService': customers_customer_calculation,
            'acme.datasets.v1.DataSchemaCalculationService': datasets_data_schema_calculation,
            'acme.datasets.v1.DataSchemaValidationService': datasets_data_schema_validation,
            'acme.datasets.v1.DatasetQueryService': datasets_dataset_query,
            'acme.datasets.v1.DatasetService': datasets_dataset,
            'acme.datasets.v1.DatasetValidationService': datasets_dataset_validation,
            'acme.datasets.v1.DatasetVersionCalculationService': datasets_dataset_version_calculation,
            'acme.datasets.v1.DatasetVersionQueryService': datasets_dataset_version_query,
            'acme.datasets.v1.DatasetVersionValidationService': datasets_dataset_version_validation,
            'acme.dispatch.v1.DispatchOrderService': dispatch_dispatch_order,
            'acme.documents.v1.DocumentQueryService': documents_document_query,
            'acme.documents.v1.DocumentService': documents_document,
            'acme.documents.v1.DocumentValidationService': documents_document_validation,
            'acme.drivers.v1.DriverQueryService': drivers_driver_query,
            'acme.experiments.v1.ExperimentQueryService': experiments_experiment_query,
            'acme.featureflags.v1.FeatureFlagService': featureflags_feature_flag,
            'acme.featureflags.v1.FeatureFlagValidationService': featureflags_feature_flag_validation,
            'acme.featurestore.v1.EntityApprovalService': featurestore_entity_approval,
            'acme.featurestore.v1.EntityCalculationService': featurestore_entity_calculation,
            'acme.featurestore.v1.EntityImportService': featurestore_entity_import,
            'acme.featurestore.v1.EntityLifecycleService': featurestore_entity_lifecycle,
            'acme.featurestore.v1.EntityReportingService': featurestore_entity_reporting,
            'acme.featurestore.v1.EntitySyncService': featurestore_entity_sync,
            'acme.featurestore.v1.EntityValidationService': featurestore_entity_validation,
            'acme.featurestore.v1.FeatureValueApprovalService': featurestore_feature_value_approval,
            'acme.featurestore.v1.FeatureValueCalculationService': featurestore_feature_value_calculation,
            'acme.featurestore.v1.FeatureValueImportService': featurestore_feature_value_import,
            'acme.featurestore.v1.FeatureValueLifecycleService': featurestore_feature_value_lifecycle,
            'acme.featurestore.v1.FeatureValueQueryService': featurestore_feature_value_query,
            'acme.featurestore.v1.FeatureValueReportingService': featurestore_feature_value_reporting,
            'acme.featurestore.v1.FeatureValueSyncService': featurestore_feature_value_sync,
            'acme.featurestore.v1.FeatureValueValidationService': featurestore_feature_value_validation,
            'acme.featurestore.v1.FeatureViewApprovalService': featurestore_feature_view_approval,
            'acme.featurestore.v1.FeatureViewCalculationService': featurestore_feature_view_calculation,
            'acme.featurestore.v1.FeatureViewLifecycleService': featurestore_feature_view_lifecycle,
            'acme.featurestore.v1.FeatureViewQueryService': featurestore_feature_view_query,
            'acme.featurestore.v1.FeatureViewReportingService': featurestore_feature_view_reporting,
            'acme.featurestore.v1.FeatureViewService': featurestore_feature_view,
            'acme.featurestore.v1.FeatureViewSyncService': featurestore_feature_view_sync,
            'acme.featurestore.v1.FeatureViewValidationService': featurestore_feature_view_validation,
            'acme.fleet.v1.VehicleService': fleet_vehicle,
            'acme.helpdesk.v1.TicketCalculationService': helpdesk_ticket_calculation,
            'acme.identity.v1.UserQueryService': identity_user_query,
            'acme.identity.v1.UserService': identity_user,
            'acme.identity.v1.UserValidationService': identity_user_validation,
            'acme.insurance.v1.PolicyQueryService': insurance_policy_query,
            'acme.keymanagement.v1.CryptoKeyCalculationService': keymanagement_crypto_key_calculation,
            'acme.ledger.v1.LedgerAccountQueryService': ledger_ledger_account_query,
            'acme.ledger.v1.LedgerAccountService': ledger_ledger_account,
            'acme.ledger.v1.LedgerAccountValidationService': ledger_ledger_account_validation,
            'acme.lineage.v1.ImpactCalculationService': lineage_impact_calculation,
            'acme.lineage.v1.ImpactImportService': lineage_impact_import,
            'acme.lineage.v1.ImpactLifecycleService': lineage_impact_lifecycle,
            'acme.lineage.v1.ImpactSyncService': lineage_impact_sync,
            'acme.lineage.v1.ImpactValidationService': lineage_impact_validation,
            'acme.lineage.v1.ImpactWorkflowService': lineage_impact_workflow,
            'acme.lineage.v1.LineageEdgeApprovalService': lineage_lineage_edge_approval,
            'acme.lineage.v1.LineageEdgeCalculationService': lineage_lineage_edge_calculation,
            'acme.lineage.v1.LineageEdgeImportService': lineage_lineage_edge_import,
            'acme.lineage.v1.LineageEdgeQueryService': lineage_lineage_edge_query,
            'acme.lineage.v1.LineageEdgeReportingService': lineage_lineage_edge_reporting,
            'acme.lineage.v1.LineageEdgeSyncService': lineage_lineage_edge_sync,
            'acme.lineage.v1.LineageEdgeValidationService': lineage_lineage_edge_validation,
            'acme.lineage.v1.LineageEdgeWorkflowService': lineage_lineage_edge_workflow,
            'acme.lineage.v1.LineageNodeApprovalService': lineage_lineage_node_approval,
            'acme.lineage.v1.LineageNodeCalculationService': lineage_lineage_node_calculation,
            'acme.lineage.v1.LineageNodeQueryService': lineage_lineage_node_query,
            'acme.lineage.v1.LineageNodeReportingService': lineage_lineage_node_reporting,
            'acme.lineage.v1.LineageNodeService': lineage_lineage_node,
            'acme.lineage.v1.LineageNodeSyncService': lineage_lineage_node_sync,
            'acme.lineage.v1.LineageNodeValidationService': lineage_lineage_node_validation,
            'acme.lineage.v1.LineageNodeWorkflowService': lineage_lineage_node_workflow,
            'acme.maintenance.v1.WorkOrderQueryService': maintenance_work_order_query,
            'acme.merchandising.v1.CollectionQueryService': merchandising_collection_query,
            'acme.metrics.v1.DashboardExportService': metrics_dashboard_export,
            'acme.metrics.v1.DashboardNotificationService': metrics_dashboard_notification,
            'acme.metrics.v1.DashboardSyncService': metrics_dashboard_sync,
            'acme.metrics.v1.DashboardValidationService': metrics_dashboard_validation,
            'acme.metrics.v1.MetricAlertExportService': metrics_metric_alert_export,
            'acme.metrics.v1.MetricAlertHistoryService': metrics_metric_alert_history,
            'acme.metrics.v1.MetricAlertNotificationService': metrics_metric_alert_notification,
            'acme.metrics.v1.MetricAlertQueryService': metrics_metric_alert_query,
            'acme.metrics.v1.MetricAlertValidationService': metrics_metric_alert_validation,
            'acme.metrics.v1.MetricSeriesExportService': metrics_metric_series_export,
            'acme.metrics.v1.MetricSeriesHistoryService': metrics_metric_series_history,
            'acme.metrics.v1.MetricSeriesNotificationService': metrics_metric_series_notification,
            'acme.metrics.v1.MetricSeriesService': metrics_metric_series,
            'acme.metrics.v1.MetricSeriesValidationService': metrics_metric_series_validation,
            'acme.notifications.v1.NotificationQueryService': notifications_notification_query,
            'acme.notifications.v1.NotificationService': notifications_notification,
            'acme.notifications.v1.NotificationValidationService': notifications_notification_validation,
            'acme.patients.v1.PatientCalculationService': patients_patient_calculation,
            'acme.prescriptions.v1.PrescriptionService': prescriptions_prescription,
            'acme.search.v1.SearchIndexQueryService': search_search_index_query,
            'acme.search.v1.SearchIndexService': search_search_index,
            'acme.search.v1.SearchIndexValidationService': search_search_index_validation,
            'acme.surveys.v1.SurveyService': surveys_survey,
            'acme.telehealth.v1.VideoVisitService': telehealth_video_visit,
            'acme.treasury.v1.CashPositionQueryService': treasury_cash_position_query,
            'acme.venues.v1.VenueQueryService': venues_venue_query,
            'acme.venues.v1.VenueValidationService': venues_venue_validation,
            'acme.webhooks.v1.WebhookEndpointQueryService': webhooks_webhook_endpoint_query,
        },
    )
    return Dependencies(clients, DomainRepository(container.sessions),
                        container.settings, container.bus)


def register(server: grpc.aio.Server, container: Container) -> dict[str, object]:
    deps = dependencies(container)
    registered: dict[str, object] = {}
    entity_approval_servicer = Factory(lambda: EntityApprovalServicer(deps))()
    featurestore_v1_entity_approval_service_pb2_grpc.add_EntityApprovalServiceServicer_to_server(
        entity_approval_servicer,
        server
    )
    registered['acme.featurestore.v1.EntityApprovalService'] = entity_approval_servicer
    entity_calculation_servicer = Factory(lambda: EntityCalculationServicer(deps))()
    featurestore_v1_entity_calculation_service_pb2_grpc.add_EntityCalculationServiceServicer_to_server(
        entity_calculation_servicer,
        server
    )
    registered['acme.featurestore.v1.EntityCalculationService'] = entity_calculation_servicer
    entity_import_servicer = Factory(lambda: EntityImportServicer(deps))()
    featurestore_v1_entity_import_service_pb2_grpc.add_EntityImportServiceServicer_to_server(
        entity_import_servicer,
        server
    )
    registered['acme.featurestore.v1.EntityImportService'] = entity_import_servicer
    entity_lifecycle_servicer = Factory(lambda: EntityLifecycleServicer(deps))()
    featurestore_v1_entity_lifecycle_service_pb2_grpc.add_EntityLifecycleServiceServicer_to_server(
        entity_lifecycle_servicer,
        server
    )
    registered['acme.featurestore.v1.EntityLifecycleService'] = entity_lifecycle_servicer
    entity_reporting_servicer = Factory(lambda: EntityReportingServicer(deps))()
    featurestore_v1_entity_reporting_service_pb2_grpc.add_EntityReportingServiceServicer_to_server(
        entity_reporting_servicer,
        server
    )
    registered['acme.featurestore.v1.EntityReportingService'] = entity_reporting_servicer
    entity_sync_servicer = Factory(lambda: EntitySyncServicer(deps))()
    featurestore_v1_entity_sync_service_pb2_grpc.add_EntitySyncServiceServicer_to_server(entity_sync_servicer, server)
    registered['acme.featurestore.v1.EntitySyncService'] = entity_sync_servicer
    entity_validation_servicer = Factory(lambda: EntityValidationServicer(deps))()
    featurestore_v1_entity_validation_service_pb2_grpc.add_EntityValidationServiceServicer_to_server(
        entity_validation_servicer,
        server
    )
    registered['acme.featurestore.v1.EntityValidationService'] = entity_validation_servicer
    entity_workflow_servicer = Factory(lambda: EntityWorkflowServicer(deps))()
    featurestore_v1_entity_workflow_service_pb2_grpc.add_EntityWorkflowServiceServicer_to_server(
        entity_workflow_servicer,
        server
    )
    registered['acme.featurestore.v1.EntityWorkflowService'] = entity_workflow_servicer
    feature_value_approval_servicer = Factory(lambda: FeatureValueApprovalServicer(deps))()
    featurestore_v1_feature_value_approval_service_pb2_grpc.add_FeatureValueApprovalServiceServicer_to_server(
        feature_value_approval_servicer,
        server
    )
    registered['acme.featurestore.v1.FeatureValueApprovalService'] = feature_value_approval_servicer
    feature_value_calculation_servicer = Factory(lambda: FeatureValueCalculationServicer(deps))()
    featurestore_v1_feature_value_calculation_service_pb2_grpc.add_FeatureValueCalculationServiceServicer_to_server(
        feature_value_calculation_servicer,
        server
    )
    registered['acme.featurestore.v1.FeatureValueCalculationService'] = feature_value_calculation_servicer
    feature_value_import_servicer = Factory(lambda: FeatureValueImportServicer(deps))()
    featurestore_v1_feature_value_import_service_pb2_grpc.add_FeatureValueImportServiceServicer_to_server(
        feature_value_import_servicer,
        server
    )
    registered['acme.featurestore.v1.FeatureValueImportService'] = feature_value_import_servicer
    feature_value_lifecycle_servicer = Factory(lambda: FeatureValueLifecycleServicer(deps))()
    featurestore_v1_feature_value_lifecycle_service_pb2_grpc.add_FeatureValueLifecycleServiceServicer_to_server(
        feature_value_lifecycle_servicer,
        server
    )
    registered['acme.featurestore.v1.FeatureValueLifecycleService'] = feature_value_lifecycle_servicer
    feature_value_query_servicer = Factory(lambda: FeatureValueQueryServicer(deps))()
    featurestore_v1_feature_value_query_service_pb2_grpc.add_FeatureValueQueryServiceServicer_to_server(
        feature_value_query_servicer,
        server
    )
    registered['acme.featurestore.v1.FeatureValueQueryService'] = feature_value_query_servicer
    feature_value_reporting_servicer = Factory(lambda: FeatureValueReportingServicer(deps))()
    featurestore_v1_feature_value_reporting_service_pb2_grpc.add_FeatureValueReportingServiceServicer_to_server(
        feature_value_reporting_servicer,
        server
    )
    registered['acme.featurestore.v1.FeatureValueReportingService'] = feature_value_reporting_servicer
    feature_value_sync_servicer = Factory(lambda: FeatureValueSyncServicer(deps))()
    featurestore_v1_feature_value_sync_service_pb2_grpc.add_FeatureValueSyncServiceServicer_to_server(
        feature_value_sync_servicer,
        server
    )
    registered['acme.featurestore.v1.FeatureValueSyncService'] = feature_value_sync_servicer
    feature_value_validation_servicer = Factory(lambda: FeatureValueValidationServicer(deps))()
    featurestore_v1_feature_value_validation_service_pb2_grpc.add_FeatureValueValidationServiceServicer_to_server(
        feature_value_validation_servicer,
        server
    )
    registered['acme.featurestore.v1.FeatureValueValidationService'] = feature_value_validation_servicer
    feature_value_workflow_servicer = Factory(lambda: FeatureValueWorkflowServicer(deps))()
    featurestore_v1_feature_value_workflow_service_pb2_grpc.add_FeatureValueWorkflowServiceServicer_to_server(
        feature_value_workflow_servicer,
        server
    )
    registered['acme.featurestore.v1.FeatureValueWorkflowService'] = feature_value_workflow_servicer
    feature_view_approval_servicer = Factory(lambda: FeatureViewApprovalServicer(deps))()
    featurestore_v1_feature_view_approval_service_pb2_grpc.add_FeatureViewApprovalServiceServicer_to_server(
        feature_view_approval_servicer,
        server
    )
    registered['acme.featurestore.v1.FeatureViewApprovalService'] = feature_view_approval_servicer
    feature_view_calculation_servicer = Factory(lambda: FeatureViewCalculationServicer(deps))()
    featurestore_v1_feature_view_calculation_service_pb2_grpc.add_FeatureViewCalculationServiceServicer_to_server(
        feature_view_calculation_servicer,
        server
    )
    registered['acme.featurestore.v1.FeatureViewCalculationService'] = feature_view_calculation_servicer
    feature_view_lifecycle_servicer = Factory(lambda: FeatureViewLifecycleServicer(deps))()
    featurestore_v1_feature_view_lifecycle_service_pb2_grpc.add_FeatureViewLifecycleServiceServicer_to_server(
        feature_view_lifecycle_servicer,
        server
    )
    registered['acme.featurestore.v1.FeatureViewLifecycleService'] = feature_view_lifecycle_servicer
    feature_view_query_servicer = Factory(lambda: FeatureViewQueryServicer(deps))()
    featurestore_v1_feature_view_query_service_pb2_grpc.add_FeatureViewQueryServiceServicer_to_server(
        feature_view_query_servicer,
        server
    )
    registered['acme.featurestore.v1.FeatureViewQueryService'] = feature_view_query_servicer
    feature_view_reporting_servicer = Factory(lambda: FeatureViewReportingServicer(deps))()
    featurestore_v1_feature_view_reporting_service_pb2_grpc.add_FeatureViewReportingServiceServicer_to_server(
        feature_view_reporting_servicer,
        server
    )
    registered['acme.featurestore.v1.FeatureViewReportingService'] = feature_view_reporting_servicer
    feature_view_servicer = Factory(lambda: FeatureViewServicer(deps))()
    featurestore_v1_feature_view_service_pb2_grpc.add_FeatureViewServiceServicer_to_server(
        feature_view_servicer,
        server
    )
    registered['acme.featurestore.v1.FeatureViewService'] = feature_view_servicer
    feature_view_sync_servicer = Factory(lambda: FeatureViewSyncServicer(deps))()
    featurestore_v1_feature_view_sync_service_pb2_grpc.add_FeatureViewSyncServiceServicer_to_server(
        feature_view_sync_servicer,
        server
    )
    registered['acme.featurestore.v1.FeatureViewSyncService'] = feature_view_sync_servicer
    feature_view_validation_servicer = Factory(lambda: FeatureViewValidationServicer(deps))()
    featurestore_v1_feature_view_validation_service_pb2_grpc.add_FeatureViewValidationServiceServicer_to_server(
        feature_view_validation_servicer,
        server
    )
    registered['acme.featurestore.v1.FeatureViewValidationService'] = feature_view_validation_servicer
    feature_view_workflow_servicer = Factory(lambda: FeatureViewWorkflowServicer(deps))()
    featurestore_v1_feature_view_workflow_service_pb2_grpc.add_FeatureViewWorkflowServiceServicer_to_server(
        feature_view_workflow_servicer,
        server
    )
    registered['acme.featurestore.v1.FeatureViewWorkflowService'] = feature_view_workflow_servicer
    subscribe(deps)
    return registered
