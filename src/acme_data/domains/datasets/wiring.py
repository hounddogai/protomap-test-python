"""Register and compose every service of the datasets domain."""

from __future__ import annotations

import grpc

from acme.anomalies.v1 import (
    anomaly_feedback_workflow_service_pb2_grpc as anomalies_v1_anomaly_feedback_workflow_service_pb2_grpc,
)
from acme.anomalies.v1 import anomaly_query_service_pb2_grpc as anomalies_v1_anomaly_query_service_pb2_grpc
from acme.anomalies.v1 import anomaly_validation_service_pb2_grpc as anomalies_v1_anomaly_validation_service_pb2_grpc
from acme.anomalies.v1 import detector_validation_service_pb2_grpc as anomalies_v1_detector_validation_service_pb2_grpc
from acme.appointments.v1 import appointment_service_pb2_grpc as appointments_v1_appointment_service_pb2_grpc
from acme.audit.v1 import audit_event_validation_service_pb2_grpc as audit_v1_audit_event_validation_service_pb2_grpc
from acme.authorization.v1 import access_policy_service_pb2_grpc as authorization_v1_access_policy_service_pb2_grpc
from acme.authorization.v1 import (
    access_policy_validation_service_pb2_grpc as authorization_v1_access_policy_validation_service_pb2_grpc,
)
from acme.billing.v1 import billing_account_query_service_pb2_grpc as billing_v1_billing_account_query_service_pb2_grpc
from acme.boxoffice.v1 import (
    box_office_sale_calculation_service_pb2_grpc as boxoffice_v1_box_office_sale_calculation_service_pb2_grpc,
)
from acme.boxoffice.v1 import box_office_sale_service_pb2_grpc as boxoffice_v1_box_office_sale_service_pb2_grpc
from acme.broadcasts.v1 import broadcast_query_service_pb2_grpc as broadcasts_v1_broadcast_query_service_pb2_grpc
from acme.careplans.v1 import care_plan_service_pb2_grpc as careplans_v1_care_plan_service_pb2_grpc
from acme.collections.v1 import collection_case_service_pb2_grpc as collections_v1_collection_case_service_pb2_grpc
from acme.compliance.v1 import (
    compliance_case_calculation_service_pb2_grpc as compliance_v1_compliance_case_calculation_service_pb2_grpc,
)
from acme.customers.v1 import (
    consent_record_calculation_service_pb2_grpc as customers_v1_consent_record_calculation_service_pb2_grpc,
)
from acme.customers.v1 import (
    customer_calculation_service_pb2_grpc as customers_v1_customer_calculation_service_pb2_grpc,
)
from acme.customers.v1 import customer_query_service_pb2_grpc as customers_v1_customer_query_service_pb2_grpc
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
from acme.datasets.v1 import data_schema_approval_service_pb2_grpc as datasets_v1_data_schema_approval_service_pb2_grpc
from acme.datasets.v1 import (
    data_schema_calculation_service_pb2_grpc as datasets_v1_data_schema_calculation_service_pb2_grpc,
)
from acme.datasets.v1 import (
    data_schema_validation_service_pb2_grpc as datasets_v1_data_schema_validation_service_pb2_grpc,
)
from acme.datasets.v1 import data_schema_workflow_service_pb2_grpc as datasets_v1_data_schema_workflow_service_pb2_grpc
from acme.datasets.v1 import dataset_approval_service_pb2_grpc as datasets_v1_dataset_approval_service_pb2_grpc
from acme.datasets.v1 import dataset_query_service_pb2_grpc as datasets_v1_dataset_query_service_pb2_grpc
from acme.datasets.v1 import dataset_service_pb2_grpc as datasets_v1_dataset_service_pb2_grpc
from acme.datasets.v1 import dataset_validation_service_pb2_grpc as datasets_v1_dataset_validation_service_pb2_grpc
from acme.datasets.v1 import (
    dataset_version_approval_service_pb2_grpc as datasets_v1_dataset_version_approval_service_pb2_grpc,
)
from acme.datasets.v1 import (
    dataset_version_calculation_service_pb2_grpc as datasets_v1_dataset_version_calculation_service_pb2_grpc,
)
from acme.datasets.v1 import (
    dataset_version_query_service_pb2_grpc as datasets_v1_dataset_version_query_service_pb2_grpc,
)
from acme.datasets.v1 import (
    dataset_version_validation_service_pb2_grpc as datasets_v1_dataset_version_validation_service_pb2_grpc,
)
from acme.datasets.v1 import (
    dataset_version_workflow_service_pb2_grpc as datasets_v1_dataset_version_workflow_service_pb2_grpc,
)
from acme.datasets.v1 import dataset_workflow_service_pb2_grpc as datasets_v1_dataset_workflow_service_pb2_grpc
from acme.deliveries.v1 import delivery_query_service_pb2_grpc as deliveries_v1_delivery_query_service_pb2_grpc
from acme.documents.v1 import document_query_service_pb2_grpc as documents_v1_document_query_service_pb2_grpc
from acme.documents.v1 import document_service_pb2_grpc as documents_v1_document_service_pb2_grpc
from acme.drivers.v1 import driver_query_service_pb2_grpc as drivers_v1_driver_query_service_pb2_grpc
from acme.featureflags.v1 import (
    feature_flag_query_service_pb2_grpc as featureflags_v1_feature_flag_query_service_pb2_grpc,
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
    feature_value_sync_service_pb2_grpc as featurestore_v1_feature_value_sync_service_pb2_grpc,
)
from acme.featurestore.v1 import (
    feature_value_validation_service_pb2_grpc as featurestore_v1_feature_value_validation_service_pb2_grpc,
)
from acme.featurestore.v1 import (
    feature_view_calculation_service_pb2_grpc as featurestore_v1_feature_view_calculation_service_pb2_grpc,
)
from acme.featurestore.v1 import (
    feature_view_query_service_pb2_grpc as featurestore_v1_feature_view_query_service_pb2_grpc,
)
from acme.featurestore.v1 import (
    feature_view_validation_service_pb2_grpc as featurestore_v1_feature_view_validation_service_pb2_grpc,
)
from acme.forms.v1 import form_service_pb2_grpc as forms_v1_form_service_pb2_grpc
from acme.fuel.v1 import fuel_card_service_pb2_grpc as fuel_v1_fuel_card_service_pb2_grpc
from acme.identity.v1 import user_query_service_pb2_grpc as identity_v1_user_query_service_pb2_grpc
from acme.identity.v1 import user_service_pb2_grpc as identity_v1_user_service_pb2_grpc
from acme.identity.v1 import user_validation_service_pb2_grpc as identity_v1_user_validation_service_pb2_grpc
from acme.labeling.v1 import annotation_approval_service_pb2_grpc as labeling_v1_annotation_approval_service_pb2_grpc
from acme.labeling.v1 import (
    annotation_validation_service_pb2_grpc as labeling_v1_annotation_validation_service_pb2_grpc,
)
from acme.labeling.v1 import (
    label_set_calculation_service_pb2_grpc as labeling_v1_label_set_calculation_service_pb2_grpc,
)
from acme.labeling.v1 import label_set_sync_service_pb2_grpc as labeling_v1_label_set_sync_service_pb2_grpc
from acme.labeling.v1 import (
    labeling_task_validation_service_pb2_grpc as labeling_v1_labeling_task_validation_service_pb2_grpc,
)
from acme.ledger.v1 import ledger_account_query_service_pb2_grpc as ledger_v1_ledger_account_query_service_pb2_grpc
from acme.ledger.v1 import ledger_account_service_pb2_grpc as ledger_v1_ledger_account_service_pb2_grpc
from acme.lineage.v1 import impact_approval_service_pb2_grpc as lineage_v1_impact_approval_service_pb2_grpc
from acme.lineage.v1 import lineage_edge_approval_service_pb2_grpc as lineage_v1_lineage_edge_approval_service_pb2_grpc
from acme.lineage.v1 import (
    lineage_edge_calculation_service_pb2_grpc as lineage_v1_lineage_edge_calculation_service_pb2_grpc,
)
from acme.lineage.v1 import lineage_edge_import_service_pb2_grpc as lineage_v1_lineage_edge_import_service_pb2_grpc
from acme.lineage.v1 import (
    lineage_edge_reporting_service_pb2_grpc as lineage_v1_lineage_edge_reporting_service_pb2_grpc,
)
from acme.lineage.v1 import (
    lineage_node_calculation_service_pb2_grpc as lineage_v1_lineage_node_calculation_service_pb2_grpc,
)
from acme.lineage.v1 import (
    lineage_node_validation_service_pb2_grpc as lineage_v1_lineage_node_validation_service_pb2_grpc,
)
from acme.loyalty.v1 import loyalty_member_query_service_pb2_grpc as loyalty_v1_loyalty_member_query_service_pb2_grpc
from acme.metrics.v1 import dashboard_export_service_pb2_grpc as metrics_v1_dashboard_export_service_pb2_grpc
from acme.metrics.v1 import dashboard_history_service_pb2_grpc as metrics_v1_dashboard_history_service_pb2_grpc
from acme.metrics.v1 import dashboard_sync_service_pb2_grpc as metrics_v1_dashboard_sync_service_pb2_grpc
from acme.metrics.v1 import dashboard_validation_service_pb2_grpc as metrics_v1_dashboard_validation_service_pb2_grpc
from acme.metrics.v1 import metric_alert_export_service_pb2_grpc as metrics_v1_metric_alert_export_service_pb2_grpc
from acme.metrics.v1 import metric_alert_history_service_pb2_grpc as metrics_v1_metric_alert_history_service_pb2_grpc
from acme.metrics.v1 import metric_alert_query_service_pb2_grpc as metrics_v1_metric_alert_query_service_pb2_grpc
from acme.metrics.v1 import (
    metric_alert_validation_service_pb2_grpc as metrics_v1_metric_alert_validation_service_pb2_grpc,
)
from acme.metrics.v1 import metric_series_history_service_pb2_grpc as metrics_v1_metric_series_history_service_pb2_grpc
from acme.metrics.v1 import (
    metric_series_notification_service_pb2_grpc as metrics_v1_metric_series_notification_service_pb2_grpc,
)
from acme.metrics.v1 import (
    metric_series_validation_service_pb2_grpc as metrics_v1_metric_series_validation_service_pb2_grpc,
)
from acme.modelregistry.v1 import (
    deployment_workflow_service_pb2_grpc as modelregistry_v1_deployment_workflow_service_pb2_grpc,
)
from acme.modelregistry.v1 import (
    model_version_validation_service_pb2_grpc as modelregistry_v1_model_version_validation_service_pb2_grpc,
)
from acme.modelregistry.v1 import (
    model_version_workflow_service_pb2_grpc as modelregistry_v1_model_version_workflow_service_pb2_grpc,
)
from acme.modelregistry.v1 import (
    registered_model_calculation_service_pb2_grpc as modelregistry_v1_registered_model_calculation_service_pb2_grpc,
)
from acme.modelregistry.v1 import (
    registered_model_sync_service_pb2_grpc as modelregistry_v1_registered_model_sync_service_pb2_grpc,
)
from acme.notifications.v1 import (
    notification_query_service_pb2_grpc as notifications_v1_notification_query_service_pb2_grpc,
)
from acme.notifications.v1 import notification_service_pb2_grpc as notifications_v1_notification_service_pb2_grpc
from acme.notifications.v1 import (
    notification_validation_service_pb2_grpc as notifications_v1_notification_validation_service_pb2_grpc,
)
from acme.orders.v1 import order_calculation_service_pb2_grpc as orders_v1_order_calculation_service_pb2_grpc
from acme.pipelines.v1 import pipeline_approval_service_pb2_grpc as pipelines_v1_pipeline_approval_service_pb2_grpc
from acme.pipelines.v1 import pipeline_query_service_pb2_grpc as pipelines_v1_pipeline_query_service_pb2_grpc
from acme.pipelines.v1 import (
    pipeline_run_calculation_service_pb2_grpc as pipelines_v1_pipeline_run_calculation_service_pb2_grpc,
)
from acme.pipelines.v1 import pipeline_run_query_service_pb2_grpc as pipelines_v1_pipeline_run_query_service_pb2_grpc
from acme.pipelines.v1 import pipeline_service_pb2_grpc as pipelines_v1_pipeline_service_pb2_grpc
from acme.prescriptions.v1 import (
    prescription_query_service_pb2_grpc as prescriptions_v1_prescription_query_service_pb2_grpc,
)
from acme.reviews.v1 import product_review_service_pb2_grpc as reviews_v1_product_review_service_pb2_grpc
from acme.search.v1 import search_index_query_service_pb2_grpc as search_v1_search_index_query_service_pb2_grpc
from acme.search.v1 import (
    search_index_validation_service_pb2_grpc as search_v1_search_index_validation_service_pb2_grpc,
)
from acme.seating.v1 import seat_map_service_pb2_grpc as seating_v1_seat_map_service_pb2_grpc
from acme.shows.v1 import show_calculation_service_pb2_grpc as shows_v1_show_calculation_service_pb2_grpc
from acme.sponsorships.v1 import sponsor_service_pb2_grpc as sponsorships_v1_sponsor_service_pb2_grpc
from acme.ticketing.v1 import ticket_query_service_pb2_grpc as ticketing_v1_ticket_query_service_pb2_grpc
from acme.tours.v1 import tour_service_pb2_grpc as tours_v1_tour_service_pb2_grpc
from acme.venues.v1 import venue_query_service_pb2_grpc as venues_v1_venue_query_service_pb2_grpc

from acme_data.domains.datasets.data_schema_approval_service import DataSchemaApprovalServicer
from acme_data.domains.datasets.data_schema_calculation_service import DataSchemaCalculationServicer
from acme_data.domains.datasets.data_schema_validation_service import DataSchemaValidationServicer
from acme_data.domains.datasets.data_schema_workflow_service import DataSchemaWorkflowServicer
from acme_data.domains.datasets.dataset_approval_service import DatasetApprovalServicer
from acme_data.domains.datasets.dataset_query_service import DatasetQueryServicer
from acme_data.domains.datasets.dataset_service import DatasetServicer
from acme_data.domains.datasets.dataset_validation_service import DatasetValidationServicer
from acme_data.domains.datasets.dataset_version_approval_service import DatasetVersionApprovalServicer
from acme_data.domains.datasets.dataset_version_calculation_service import DatasetVersionCalculationServicer
from acme_data.domains.datasets.dataset_version_query_service import DatasetVersionQueryServicer
from acme_data.domains.datasets.dataset_version_validation_service import DatasetVersionValidationServicer
from acme_data.domains.datasets.dataset_version_workflow_service import DatasetVersionWorkflowServicer
from acme_data.domains.datasets.dataset_workflow_service import DatasetWorkflowServicer
from acme_data.domains.datasets.dependencies import Clients
from acme_data.domains.datasets.dependencies import Dependencies
from acme_data.domains.datasets.events import subscribe
from acme_data.domains.datasets.repository import DomainRepository
from acme_data.platform.container import Container
from acme_data.platform.container import Factory


def dependencies(container: Container) -> Dependencies:
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
    anomalies_anomaly_validation = container.singleton(
        anomalies_v1_anomaly_validation_service_pb2_grpc.AnomalyValidationServiceStub,
        lambda: anomalies_v1_anomaly_validation_service_pb2_grpc.AnomalyValidationServiceStub(container.channel)
    )
    anomalies_detector_validation = container.singleton(
        anomalies_v1_detector_validation_service_pb2_grpc.DetectorValidationServiceStub,
        lambda: anomalies_v1_detector_validation_service_pb2_grpc.DetectorValidationServiceStub(container.channel)
    )
    appointments_appointment = container.singleton(
        appointments_v1_appointment_service_pb2_grpc.AppointmentServiceStub,
        lambda: appointments_v1_appointment_service_pb2_grpc.AppointmentServiceStub(container.channel)
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
    billing_billing_account_query = container.singleton(
        billing_v1_billing_account_query_service_pb2_grpc.BillingAccountQueryServiceStub,
        lambda: billing_v1_billing_account_query_service_pb2_grpc.BillingAccountQueryServiceStub(container.channel)
    )
    boxoffice_box_office_sale_calculation = container.singleton(
        boxoffice_v1_box_office_sale_calculation_service_pb2_grpc.BoxOfficeSaleCalculationServiceStub,
        lambda: boxoffice_v1_box_office_sale_calculation_service_pb2_grpc.BoxOfficeSaleCalculationServiceStub(
            container.channel
        )
    )
    boxoffice_box_office_sale = container.singleton(
        boxoffice_v1_box_office_sale_service_pb2_grpc.BoxOfficeSaleServiceStub,
        lambda: boxoffice_v1_box_office_sale_service_pb2_grpc.BoxOfficeSaleServiceStub(container.channel)
    )
    broadcasts_broadcast_query = container.singleton(
        broadcasts_v1_broadcast_query_service_pb2_grpc.BroadcastQueryServiceStub,
        lambda: broadcasts_v1_broadcast_query_service_pb2_grpc.BroadcastQueryServiceStub(container.channel)
    )
    careplans_care_plan = container.singleton(
        careplans_v1_care_plan_service_pb2_grpc.CarePlanServiceStub,
        lambda: careplans_v1_care_plan_service_pb2_grpc.CarePlanServiceStub(container.channel)
    )
    collections_collection_case = container.singleton(
        collections_v1_collection_case_service_pb2_grpc.CollectionCaseServiceStub,
        lambda: collections_v1_collection_case_service_pb2_grpc.CollectionCaseServiceStub(container.channel)
    )
    compliance_compliance_case_calculation = container.singleton(
        compliance_v1_compliance_case_calculation_service_pb2_grpc.ComplianceCaseCalculationServiceStub,
        lambda: compliance_v1_compliance_case_calculation_service_pb2_grpc.ComplianceCaseCalculationServiceStub(
            container.channel
        )
    )
    customers_consent_record_calculation = container.singleton(
        customers_v1_consent_record_calculation_service_pb2_grpc.ConsentRecordCalculationServiceStub,
        lambda: customers_v1_consent_record_calculation_service_pb2_grpc.ConsentRecordCalculationServiceStub(
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
    datasets_data_schema_approval = container.singleton(
        datasets_v1_data_schema_approval_service_pb2_grpc.DataSchemaApprovalServiceStub,
        lambda: datasets_v1_data_schema_approval_service_pb2_grpc.DataSchemaApprovalServiceStub(container.channel)
    )
    datasets_data_schema_calculation = container.singleton(
        datasets_v1_data_schema_calculation_service_pb2_grpc.DataSchemaCalculationServiceStub,
        lambda: datasets_v1_data_schema_calculation_service_pb2_grpc.DataSchemaCalculationServiceStub(container.channel)
    )
    datasets_data_schema_validation = container.singleton(
        datasets_v1_data_schema_validation_service_pb2_grpc.DataSchemaValidationServiceStub,
        lambda: datasets_v1_data_schema_validation_service_pb2_grpc.DataSchemaValidationServiceStub(container.channel)
    )
    datasets_dataset_approval = container.singleton(
        datasets_v1_dataset_approval_service_pb2_grpc.DatasetApprovalServiceStub,
        lambda: datasets_v1_dataset_approval_service_pb2_grpc.DatasetApprovalServiceStub(container.channel)
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
    datasets_dataset_version_approval = container.singleton(
        datasets_v1_dataset_version_approval_service_pb2_grpc.DatasetVersionApprovalServiceStub,
        lambda: datasets_v1_dataset_version_approval_service_pb2_grpc.DatasetVersionApprovalServiceStub(
            container.channel
        )
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
    datasets_dataset_version_workflow = container.singleton(
        datasets_v1_dataset_version_workflow_service_pb2_grpc.DatasetVersionWorkflowServiceStub,
        lambda: datasets_v1_dataset_version_workflow_service_pb2_grpc.DatasetVersionWorkflowServiceStub(
            container.channel
        )
    )
    datasets_dataset_workflow = container.singleton(
        datasets_v1_dataset_workflow_service_pb2_grpc.DatasetWorkflowServiceStub,
        lambda: datasets_v1_dataset_workflow_service_pb2_grpc.DatasetWorkflowServiceStub(container.channel)
    )
    deliveries_delivery_query = container.singleton(
        deliveries_v1_delivery_query_service_pb2_grpc.DeliveryQueryServiceStub,
        lambda: deliveries_v1_delivery_query_service_pb2_grpc.DeliveryQueryServiceStub(container.channel)
    )
    documents_document_query = container.singleton(
        documents_v1_document_query_service_pb2_grpc.DocumentQueryServiceStub,
        lambda: documents_v1_document_query_service_pb2_grpc.DocumentQueryServiceStub(container.channel)
    )
    documents_document = container.singleton(
        documents_v1_document_service_pb2_grpc.DocumentServiceStub,
        lambda: documents_v1_document_service_pb2_grpc.DocumentServiceStub(container.channel)
    )
    drivers_driver_query = container.singleton(
        drivers_v1_driver_query_service_pb2_grpc.DriverQueryServiceStub,
        lambda: drivers_v1_driver_query_service_pb2_grpc.DriverQueryServiceStub(container.channel)
    )
    featureflags_feature_flag_query = container.singleton(
        featureflags_v1_feature_flag_query_service_pb2_grpc.FeatureFlagQueryServiceStub,
        lambda: featureflags_v1_feature_flag_query_service_pb2_grpc.FeatureFlagQueryServiceStub(container.channel)
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
    featurestore_feature_view_validation = container.singleton(
        featurestore_v1_feature_view_validation_service_pb2_grpc.FeatureViewValidationServiceStub,
        lambda: featurestore_v1_feature_view_validation_service_pb2_grpc.FeatureViewValidationServiceStub(
            container.channel
        )
    )
    forms_form = container.singleton(
        forms_v1_form_service_pb2_grpc.FormServiceStub,
        lambda: forms_v1_form_service_pb2_grpc.FormServiceStub(container.channel)
    )
    fuel_fuel_card = container.singleton(
        fuel_v1_fuel_card_service_pb2_grpc.FuelCardServiceStub,
        lambda: fuel_v1_fuel_card_service_pb2_grpc.FuelCardServiceStub(container.channel)
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
    labeling_annotation_approval = container.singleton(
        labeling_v1_annotation_approval_service_pb2_grpc.AnnotationApprovalServiceStub,
        lambda: labeling_v1_annotation_approval_service_pb2_grpc.AnnotationApprovalServiceStub(container.channel)
    )
    labeling_annotation_validation = container.singleton(
        labeling_v1_annotation_validation_service_pb2_grpc.AnnotationValidationServiceStub,
        lambda: labeling_v1_annotation_validation_service_pb2_grpc.AnnotationValidationServiceStub(container.channel)
    )
    labeling_label_set_calculation = container.singleton(
        labeling_v1_label_set_calculation_service_pb2_grpc.LabelSetCalculationServiceStub,
        lambda: labeling_v1_label_set_calculation_service_pb2_grpc.LabelSetCalculationServiceStub(container.channel)
    )
    labeling_label_set_sync = container.singleton(
        labeling_v1_label_set_sync_service_pb2_grpc.LabelSetSyncServiceStub,
        lambda: labeling_v1_label_set_sync_service_pb2_grpc.LabelSetSyncServiceStub(container.channel)
    )
    labeling_labeling_task_validation = container.singleton(
        labeling_v1_labeling_task_validation_service_pb2_grpc.LabelingTaskValidationServiceStub,
        lambda: labeling_v1_labeling_task_validation_service_pb2_grpc.LabelingTaskValidationServiceStub(
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
    lineage_impact_approval = container.singleton(
        lineage_v1_impact_approval_service_pb2_grpc.ImpactApprovalServiceStub,
        lambda: lineage_v1_impact_approval_service_pb2_grpc.ImpactApprovalServiceStub(container.channel)
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
    lineage_lineage_edge_reporting = container.singleton(
        lineage_v1_lineage_edge_reporting_service_pb2_grpc.LineageEdgeReportingServiceStub,
        lambda: lineage_v1_lineage_edge_reporting_service_pb2_grpc.LineageEdgeReportingServiceStub(container.channel)
    )
    lineage_lineage_node_calculation = container.singleton(
        lineage_v1_lineage_node_calculation_service_pb2_grpc.LineageNodeCalculationServiceStub,
        lambda: lineage_v1_lineage_node_calculation_service_pb2_grpc.LineageNodeCalculationServiceStub(
            container.channel
        )
    )
    lineage_lineage_node_validation = container.singleton(
        lineage_v1_lineage_node_validation_service_pb2_grpc.LineageNodeValidationServiceStub,
        lambda: lineage_v1_lineage_node_validation_service_pb2_grpc.LineageNodeValidationServiceStub(container.channel)
    )
    loyalty_loyalty_member_query = container.singleton(
        loyalty_v1_loyalty_member_query_service_pb2_grpc.LoyaltyMemberQueryServiceStub,
        lambda: loyalty_v1_loyalty_member_query_service_pb2_grpc.LoyaltyMemberQueryServiceStub(container.channel)
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
    metrics_metric_alert_export = container.singleton(
        metrics_v1_metric_alert_export_service_pb2_grpc.MetricAlertExportServiceStub,
        lambda: metrics_v1_metric_alert_export_service_pb2_grpc.MetricAlertExportServiceStub(container.channel)
    )
    metrics_metric_alert_history = container.singleton(
        metrics_v1_metric_alert_history_service_pb2_grpc.MetricAlertHistoryServiceStub,
        lambda: metrics_v1_metric_alert_history_service_pb2_grpc.MetricAlertHistoryServiceStub(container.channel)
    )
    metrics_metric_alert_query = container.singleton(
        metrics_v1_metric_alert_query_service_pb2_grpc.MetricAlertQueryServiceStub,
        lambda: metrics_v1_metric_alert_query_service_pb2_grpc.MetricAlertQueryServiceStub(container.channel)
    )
    metrics_metric_alert_validation = container.singleton(
        metrics_v1_metric_alert_validation_service_pb2_grpc.MetricAlertValidationServiceStub,
        lambda: metrics_v1_metric_alert_validation_service_pb2_grpc.MetricAlertValidationServiceStub(container.channel)
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
    metrics_metric_series_validation = container.singleton(
        metrics_v1_metric_series_validation_service_pb2_grpc.MetricSeriesValidationServiceStub,
        lambda: metrics_v1_metric_series_validation_service_pb2_grpc.MetricSeriesValidationServiceStub(
            container.channel
        )
    )
    modelregistry_deployment_workflow = container.singleton(
        modelregistry_v1_deployment_workflow_service_pb2_grpc.DeploymentWorkflowServiceStub,
        lambda: modelregistry_v1_deployment_workflow_service_pb2_grpc.DeploymentWorkflowServiceStub(container.channel)
    )
    modelregistry_model_version_validation = container.singleton(
        modelregistry_v1_model_version_validation_service_pb2_grpc.ModelVersionValidationServiceStub,
        lambda: modelregistry_v1_model_version_validation_service_pb2_grpc.ModelVersionValidationServiceStub(
            container.channel
        )
    )
    modelregistry_model_version_workflow = container.singleton(
        modelregistry_v1_model_version_workflow_service_pb2_grpc.ModelVersionWorkflowServiceStub,
        lambda: modelregistry_v1_model_version_workflow_service_pb2_grpc.ModelVersionWorkflowServiceStub(
            container.channel
        )
    )
    modelregistry_registered_model_calculation = container.singleton(
        modelregistry_v1_registered_model_calculation_service_pb2_grpc.RegisteredModelCalculationServiceStub,
        lambda: modelregistry_v1_registered_model_calculation_service_pb2_grpc.RegisteredModelCalculationServiceStub(
            container.channel
        )
    )
    modelregistry_registered_model_sync = container.singleton(
        modelregistry_v1_registered_model_sync_service_pb2_grpc.RegisteredModelSyncServiceStub,
        lambda: modelregistry_v1_registered_model_sync_service_pb2_grpc.RegisteredModelSyncServiceStub(
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
    orders_order_calculation = container.singleton(
        orders_v1_order_calculation_service_pb2_grpc.OrderCalculationServiceStub,
        lambda: orders_v1_order_calculation_service_pb2_grpc.OrderCalculationServiceStub(container.channel)
    )
    pipelines_pipeline_approval = container.singleton(
        pipelines_v1_pipeline_approval_service_pb2_grpc.PipelineApprovalServiceStub,
        lambda: pipelines_v1_pipeline_approval_service_pb2_grpc.PipelineApprovalServiceStub(container.channel)
    )
    pipelines_pipeline_query = container.singleton(
        pipelines_v1_pipeline_query_service_pb2_grpc.PipelineQueryServiceStub,
        lambda: pipelines_v1_pipeline_query_service_pb2_grpc.PipelineQueryServiceStub(container.channel)
    )
    pipelines_pipeline_run_calculation = container.singleton(
        pipelines_v1_pipeline_run_calculation_service_pb2_grpc.PipelineRunCalculationServiceStub,
        lambda: pipelines_v1_pipeline_run_calculation_service_pb2_grpc.PipelineRunCalculationServiceStub(
            container.channel
        )
    )
    pipelines_pipeline_run_query = container.singleton(
        pipelines_v1_pipeline_run_query_service_pb2_grpc.PipelineRunQueryServiceStub,
        lambda: pipelines_v1_pipeline_run_query_service_pb2_grpc.PipelineRunQueryServiceStub(container.channel)
    )
    pipelines_pipeline = container.singleton(
        pipelines_v1_pipeline_service_pb2_grpc.PipelineServiceStub,
        lambda: pipelines_v1_pipeline_service_pb2_grpc.PipelineServiceStub(container.channel)
    )
    prescriptions_prescription_query = container.singleton(
        prescriptions_v1_prescription_query_service_pb2_grpc.PrescriptionQueryServiceStub,
        lambda: prescriptions_v1_prescription_query_service_pb2_grpc.PrescriptionQueryServiceStub(container.channel)
    )
    reviews_product_review = container.singleton(
        reviews_v1_product_review_service_pb2_grpc.ProductReviewServiceStub,
        lambda: reviews_v1_product_review_service_pb2_grpc.ProductReviewServiceStub(container.channel)
    )
    search_search_index_query = container.singleton(
        search_v1_search_index_query_service_pb2_grpc.SearchIndexQueryServiceStub,
        lambda: search_v1_search_index_query_service_pb2_grpc.SearchIndexQueryServiceStub(container.channel)
    )
    search_search_index_validation = container.singleton(
        search_v1_search_index_validation_service_pb2_grpc.SearchIndexValidationServiceStub,
        lambda: search_v1_search_index_validation_service_pb2_grpc.SearchIndexValidationServiceStub(container.channel)
    )
    seating_seat_map = container.singleton(
        seating_v1_seat_map_service_pb2_grpc.SeatMapServiceStub,
        lambda: seating_v1_seat_map_service_pb2_grpc.SeatMapServiceStub(container.channel)
    )
    shows_show_calculation = container.singleton(
        shows_v1_show_calculation_service_pb2_grpc.ShowCalculationServiceStub,
        lambda: shows_v1_show_calculation_service_pb2_grpc.ShowCalculationServiceStub(container.channel)
    )
    sponsorships_sponsor = container.singleton(
        sponsorships_v1_sponsor_service_pb2_grpc.SponsorServiceStub,
        lambda: sponsorships_v1_sponsor_service_pb2_grpc.SponsorServiceStub(container.channel)
    )
    ticketing_ticket_query = container.singleton(
        ticketing_v1_ticket_query_service_pb2_grpc.TicketQueryServiceStub,
        lambda: ticketing_v1_ticket_query_service_pb2_grpc.TicketQueryServiceStub(container.channel)
    )
    tours_tour = container.singleton(
        tours_v1_tour_service_pb2_grpc.TourServiceStub,
        lambda: tours_v1_tour_service_pb2_grpc.TourServiceStub(container.channel)
    )
    venues_venue_query = container.singleton(
        venues_v1_venue_query_service_pb2_grpc.VenueQueryServiceStub,
        lambda: venues_v1_venue_query_service_pb2_grpc.VenueQueryServiceStub(container.channel)
    )
    clients = Clients(
        anomalies_anomaly_feedback_workflow=anomalies_anomaly_feedback_workflow,
        anomalies_anomaly_query=anomalies_anomaly_query,
        anomalies_anomaly_validation=anomalies_anomaly_validation,
        anomalies_detector_validation=anomalies_detector_validation,
        appointments_appointment=appointments_appointment,
        audit_audit_event_validation=audit_audit_event_validation,
        authorization_access_policy=authorization_access_policy,
        authorization_access_policy_validation=authorization_access_policy_validation,
        billing_billing_account_query=billing_billing_account_query,
        boxoffice_box_office_sale_calculation=boxoffice_box_office_sale_calculation,
        boxoffice_box_office_sale=boxoffice_box_office_sale,
        broadcasts_broadcast_query=broadcasts_broadcast_query,
        careplans_care_plan=careplans_care_plan,
        collections_collection_case=collections_collection_case,
        compliance_compliance_case_calculation=compliance_compliance_case_calculation,
        customers_consent_record_calculation=customers_consent_record_calculation,
        customers_customer_calculation=customers_customer_calculation,
        customers_customer_query=customers_customer_query,
        customers_customer=customers_customer,
        customers_customer_validation=customers_customer_validation,
        customers_household_calculation=customers_household_calculation,
        customers_household_query=customers_household_query,
        customers_household_validation=customers_household_validation,
        customers_preference_calculation=customers_preference_calculation,
        customers_preference_validation=customers_preference_validation,
        datasets_data_schema_approval=datasets_data_schema_approval,
        datasets_data_schema_calculation=datasets_data_schema_calculation,
        datasets_data_schema_validation=datasets_data_schema_validation,
        datasets_dataset_approval=datasets_dataset_approval,
        datasets_dataset_query=datasets_dataset_query,
        datasets_dataset=datasets_dataset,
        datasets_dataset_validation=datasets_dataset_validation,
        datasets_dataset_version_approval=datasets_dataset_version_approval,
        datasets_dataset_version_calculation=datasets_dataset_version_calculation,
        datasets_dataset_version_query=datasets_dataset_version_query,
        datasets_dataset_version_validation=datasets_dataset_version_validation,
        datasets_dataset_version_workflow=datasets_dataset_version_workflow,
        datasets_dataset_workflow=datasets_dataset_workflow,
        deliveries_delivery_query=deliveries_delivery_query,
        documents_document_query=documents_document_query,
        documents_document=documents_document,
        drivers_driver_query=drivers_driver_query,
        featureflags_feature_flag_query=featureflags_feature_flag_query,
        featurestore_feature_value_calculation=featurestore_feature_value_calculation,
        featurestore_feature_value_import=featurestore_feature_value_import,
        featurestore_feature_value_lifecycle=featurestore_feature_value_lifecycle,
        featurestore_feature_value_sync=featurestore_feature_value_sync,
        featurestore_feature_value_validation=featurestore_feature_value_validation,
        featurestore_feature_view_calculation=featurestore_feature_view_calculation,
        featurestore_feature_view_query=featurestore_feature_view_query,
        featurestore_feature_view_validation=featurestore_feature_view_validation,
        forms_form=forms_form,
        fuel_fuel_card=fuel_fuel_card,
        identity_user_query=identity_user_query,
        identity_user=identity_user,
        identity_user_validation=identity_user_validation,
        labeling_annotation_approval=labeling_annotation_approval,
        labeling_annotation_validation=labeling_annotation_validation,
        labeling_label_set_calculation=labeling_label_set_calculation,
        labeling_label_set_sync=labeling_label_set_sync,
        labeling_labeling_task_validation=labeling_labeling_task_validation,
        ledger_ledger_account_query=ledger_ledger_account_query,
        ledger_ledger_account=ledger_ledger_account,
        lineage_impact_approval=lineage_impact_approval,
        lineage_lineage_edge_approval=lineage_lineage_edge_approval,
        lineage_lineage_edge_calculation=lineage_lineage_edge_calculation,
        lineage_lineage_edge_import=lineage_lineage_edge_import,
        lineage_lineage_edge_reporting=lineage_lineage_edge_reporting,
        lineage_lineage_node_calculation=lineage_lineage_node_calculation,
        lineage_lineage_node_validation=lineage_lineage_node_validation,
        loyalty_loyalty_member_query=loyalty_loyalty_member_query,
        metrics_dashboard_export=metrics_dashboard_export,
        metrics_dashboard_history=metrics_dashboard_history,
        metrics_dashboard_sync=metrics_dashboard_sync,
        metrics_dashboard_validation=metrics_dashboard_validation,
        metrics_metric_alert_export=metrics_metric_alert_export,
        metrics_metric_alert_history=metrics_metric_alert_history,
        metrics_metric_alert_query=metrics_metric_alert_query,
        metrics_metric_alert_validation=metrics_metric_alert_validation,
        metrics_metric_series_history=metrics_metric_series_history,
        metrics_metric_series_notification=metrics_metric_series_notification,
        metrics_metric_series_validation=metrics_metric_series_validation,
        modelregistry_deployment_workflow=modelregistry_deployment_workflow,
        modelregistry_model_version_validation=modelregistry_model_version_validation,
        modelregistry_model_version_workflow=modelregistry_model_version_workflow,
        modelregistry_registered_model_calculation=modelregistry_registered_model_calculation,
        modelregistry_registered_model_sync=modelregistry_registered_model_sync,
        notifications_notification_query=notifications_notification_query,
        notifications_notification=notifications_notification,
        notifications_notification_validation=notifications_notification_validation,
        orders_order_calculation=orders_order_calculation,
        pipelines_pipeline_approval=pipelines_pipeline_approval,
        pipelines_pipeline_query=pipelines_pipeline_query,
        pipelines_pipeline_run_calculation=pipelines_pipeline_run_calculation,
        pipelines_pipeline_run_query=pipelines_pipeline_run_query,
        pipelines_pipeline=pipelines_pipeline,
        prescriptions_prescription_query=prescriptions_prescription_query,
        reviews_product_review=reviews_product_review,
        search_search_index_query=search_search_index_query,
        search_search_index_validation=search_search_index_validation,
        seating_seat_map=seating_seat_map,
        shows_show_calculation=shows_show_calculation,
        sponsorships_sponsor=sponsorships_sponsor,
        ticketing_ticket_query=ticketing_ticket_query,
        tours_tour=tours_tour,
        venues_venue_query=venues_venue_query,
        registry={
            'acme.anomalies.v1.AnomalyFeedbackWorkflowService': anomalies_anomaly_feedback_workflow,
            'acme.anomalies.v1.AnomalyQueryService': anomalies_anomaly_query,
            'acme.anomalies.v1.AnomalyValidationService': anomalies_anomaly_validation,
            'acme.anomalies.v1.DetectorValidationService': anomalies_detector_validation,
            'acme.appointments.v1.AppointmentService': appointments_appointment,
            'acme.audit.v1.AuditEventValidationService': audit_audit_event_validation,
            'acme.authorization.v1.AccessPolicyService': authorization_access_policy,
            'acme.authorization.v1.AccessPolicyValidationService': authorization_access_policy_validation,
            'acme.billing.v1.BillingAccountQueryService': billing_billing_account_query,
            'acme.boxoffice.v1.BoxOfficeSaleCalculationService': boxoffice_box_office_sale_calculation,
            'acme.boxoffice.v1.BoxOfficeSaleService': boxoffice_box_office_sale,
            'acme.broadcasts.v1.BroadcastQueryService': broadcasts_broadcast_query,
            'acme.careplans.v1.CarePlanService': careplans_care_plan,
            'acme.collections.v1.CollectionCaseService': collections_collection_case,
            'acme.compliance.v1.ComplianceCaseCalculationService': compliance_compliance_case_calculation,
            'acme.customers.v1.ConsentRecordCalculationService': customers_consent_record_calculation,
            'acme.customers.v1.CustomerCalculationService': customers_customer_calculation,
            'acme.customers.v1.CustomerQueryService': customers_customer_query,
            'acme.customers.v1.CustomerService': customers_customer,
            'acme.customers.v1.CustomerValidationService': customers_customer_validation,
            'acme.customers.v1.HouseholdCalculationService': customers_household_calculation,
            'acme.customers.v1.HouseholdQueryService': customers_household_query,
            'acme.customers.v1.HouseholdValidationService': customers_household_validation,
            'acme.customers.v1.PreferenceCalculationService': customers_preference_calculation,
            'acme.customers.v1.PreferenceValidationService': customers_preference_validation,
            'acme.datasets.v1.DataSchemaApprovalService': datasets_data_schema_approval,
            'acme.datasets.v1.DataSchemaCalculationService': datasets_data_schema_calculation,
            'acme.datasets.v1.DataSchemaValidationService': datasets_data_schema_validation,
            'acme.datasets.v1.DatasetApprovalService': datasets_dataset_approval,
            'acme.datasets.v1.DatasetQueryService': datasets_dataset_query,
            'acme.datasets.v1.DatasetService': datasets_dataset,
            'acme.datasets.v1.DatasetValidationService': datasets_dataset_validation,
            'acme.datasets.v1.DatasetVersionApprovalService': datasets_dataset_version_approval,
            'acme.datasets.v1.DatasetVersionCalculationService': datasets_dataset_version_calculation,
            'acme.datasets.v1.DatasetVersionQueryService': datasets_dataset_version_query,
            'acme.datasets.v1.DatasetVersionValidationService': datasets_dataset_version_validation,
            'acme.datasets.v1.DatasetVersionWorkflowService': datasets_dataset_version_workflow,
            'acme.datasets.v1.DatasetWorkflowService': datasets_dataset_workflow,
            'acme.deliveries.v1.DeliveryQueryService': deliveries_delivery_query,
            'acme.documents.v1.DocumentQueryService': documents_document_query,
            'acme.documents.v1.DocumentService': documents_document,
            'acme.drivers.v1.DriverQueryService': drivers_driver_query,
            'acme.featureflags.v1.FeatureFlagQueryService': featureflags_feature_flag_query,
            'acme.featurestore.v1.FeatureValueCalculationService': featurestore_feature_value_calculation,
            'acme.featurestore.v1.FeatureValueImportService': featurestore_feature_value_import,
            'acme.featurestore.v1.FeatureValueLifecycleService': featurestore_feature_value_lifecycle,
            'acme.featurestore.v1.FeatureValueSyncService': featurestore_feature_value_sync,
            'acme.featurestore.v1.FeatureValueValidationService': featurestore_feature_value_validation,
            'acme.featurestore.v1.FeatureViewCalculationService': featurestore_feature_view_calculation,
            'acme.featurestore.v1.FeatureViewQueryService': featurestore_feature_view_query,
            'acme.featurestore.v1.FeatureViewValidationService': featurestore_feature_view_validation,
            'acme.forms.v1.FormService': forms_form,
            'acme.fuel.v1.FuelCardService': fuel_fuel_card,
            'acme.identity.v1.UserQueryService': identity_user_query,
            'acme.identity.v1.UserService': identity_user,
            'acme.identity.v1.UserValidationService': identity_user_validation,
            'acme.labeling.v1.AnnotationApprovalService': labeling_annotation_approval,
            'acme.labeling.v1.AnnotationValidationService': labeling_annotation_validation,
            'acme.labeling.v1.LabelSetCalculationService': labeling_label_set_calculation,
            'acme.labeling.v1.LabelSetSyncService': labeling_label_set_sync,
            'acme.labeling.v1.LabelingTaskValidationService': labeling_labeling_task_validation,
            'acme.ledger.v1.LedgerAccountQueryService': ledger_ledger_account_query,
            'acme.ledger.v1.LedgerAccountService': ledger_ledger_account,
            'acme.lineage.v1.ImpactApprovalService': lineage_impact_approval,
            'acme.lineage.v1.LineageEdgeApprovalService': lineage_lineage_edge_approval,
            'acme.lineage.v1.LineageEdgeCalculationService': lineage_lineage_edge_calculation,
            'acme.lineage.v1.LineageEdgeImportService': lineage_lineage_edge_import,
            'acme.lineage.v1.LineageEdgeReportingService': lineage_lineage_edge_reporting,
            'acme.lineage.v1.LineageNodeCalculationService': lineage_lineage_node_calculation,
            'acme.lineage.v1.LineageNodeValidationService': lineage_lineage_node_validation,
            'acme.loyalty.v1.LoyaltyMemberQueryService': loyalty_loyalty_member_query,
            'acme.metrics.v1.DashboardExportService': metrics_dashboard_export,
            'acme.metrics.v1.DashboardHistoryService': metrics_dashboard_history,
            'acme.metrics.v1.DashboardSyncService': metrics_dashboard_sync,
            'acme.metrics.v1.DashboardValidationService': metrics_dashboard_validation,
            'acme.metrics.v1.MetricAlertExportService': metrics_metric_alert_export,
            'acme.metrics.v1.MetricAlertHistoryService': metrics_metric_alert_history,
            'acme.metrics.v1.MetricAlertQueryService': metrics_metric_alert_query,
            'acme.metrics.v1.MetricAlertValidationService': metrics_metric_alert_validation,
            'acme.metrics.v1.MetricSeriesHistoryService': metrics_metric_series_history,
            'acme.metrics.v1.MetricSeriesNotificationService': metrics_metric_series_notification,
            'acme.metrics.v1.MetricSeriesValidationService': metrics_metric_series_validation,
            'acme.modelregistry.v1.DeploymentWorkflowService': modelregistry_deployment_workflow,
            'acme.modelregistry.v1.ModelVersionValidationService': modelregistry_model_version_validation,
            'acme.modelregistry.v1.ModelVersionWorkflowService': modelregistry_model_version_workflow,
            'acme.modelregistry.v1.RegisteredModelCalculationService': modelregistry_registered_model_calculation,
            'acme.modelregistry.v1.RegisteredModelSyncService': modelregistry_registered_model_sync,
            'acme.notifications.v1.NotificationQueryService': notifications_notification_query,
            'acme.notifications.v1.NotificationService': notifications_notification,
            'acme.notifications.v1.NotificationValidationService': notifications_notification_validation,
            'acme.orders.v1.OrderCalculationService': orders_order_calculation,
            'acme.pipelines.v1.PipelineApprovalService': pipelines_pipeline_approval,
            'acme.pipelines.v1.PipelineQueryService': pipelines_pipeline_query,
            'acme.pipelines.v1.PipelineRunCalculationService': pipelines_pipeline_run_calculation,
            'acme.pipelines.v1.PipelineRunQueryService': pipelines_pipeline_run_query,
            'acme.pipelines.v1.PipelineService': pipelines_pipeline,
            'acme.prescriptions.v1.PrescriptionQueryService': prescriptions_prescription_query,
            'acme.reviews.v1.ProductReviewService': reviews_product_review,
            'acme.search.v1.SearchIndexQueryService': search_search_index_query,
            'acme.search.v1.SearchIndexValidationService': search_search_index_validation,
            'acme.seating.v1.SeatMapService': seating_seat_map,
            'acme.shows.v1.ShowCalculationService': shows_show_calculation,
            'acme.sponsorships.v1.SponsorService': sponsorships_sponsor,
            'acme.ticketing.v1.TicketQueryService': ticketing_ticket_query,
            'acme.tours.v1.TourService': tours_tour,
            'acme.venues.v1.VenueQueryService': venues_venue_query,
        },
    )
    return Dependencies(clients, DomainRepository(container.sessions),
                        container.settings, container.bus)


def register(server: grpc.aio.Server, container: Container) -> dict[str, object]:
    deps = dependencies(container)
    registered: dict[str, object] = {}
    data_schema_approval_servicer = Factory(lambda: DataSchemaApprovalServicer(deps))()
    datasets_v1_data_schema_approval_service_pb2_grpc.add_DataSchemaApprovalServiceServicer_to_server(
        data_schema_approval_servicer,
        server
    )
    registered['acme.datasets.v1.DataSchemaApprovalService'] = data_schema_approval_servicer
    data_schema_calculation_servicer = Factory(lambda: DataSchemaCalculationServicer(deps))()
    datasets_v1_data_schema_calculation_service_pb2_grpc.add_DataSchemaCalculationServiceServicer_to_server(
        data_schema_calculation_servicer,
        server
    )
    registered['acme.datasets.v1.DataSchemaCalculationService'] = data_schema_calculation_servicer
    data_schema_validation_servicer = Factory(lambda: DataSchemaValidationServicer(deps))()
    datasets_v1_data_schema_validation_service_pb2_grpc.add_DataSchemaValidationServiceServicer_to_server(
        data_schema_validation_servicer,
        server
    )
    registered['acme.datasets.v1.DataSchemaValidationService'] = data_schema_validation_servicer
    data_schema_workflow_servicer = Factory(lambda: DataSchemaWorkflowServicer(deps))()
    datasets_v1_data_schema_workflow_service_pb2_grpc.add_DataSchemaWorkflowServiceServicer_to_server(
        data_schema_workflow_servicer,
        server
    )
    registered['acme.datasets.v1.DataSchemaWorkflowService'] = data_schema_workflow_servicer
    dataset_approval_servicer = Factory(lambda: DatasetApprovalServicer(deps))()
    datasets_v1_dataset_approval_service_pb2_grpc.add_DatasetApprovalServiceServicer_to_server(
        dataset_approval_servicer,
        server
    )
    registered['acme.datasets.v1.DatasetApprovalService'] = dataset_approval_servicer
    dataset_query_servicer = Factory(lambda: DatasetQueryServicer(deps))()
    datasets_v1_dataset_query_service_pb2_grpc.add_DatasetQueryServiceServicer_to_server(dataset_query_servicer, server)
    registered['acme.datasets.v1.DatasetQueryService'] = dataset_query_servicer
    dataset_servicer = Factory(lambda: DatasetServicer(deps))()
    datasets_v1_dataset_service_pb2_grpc.add_DatasetServiceServicer_to_server(dataset_servicer, server)
    registered['acme.datasets.v1.DatasetService'] = dataset_servicer
    dataset_validation_servicer = Factory(lambda: DatasetValidationServicer(deps))()
    datasets_v1_dataset_validation_service_pb2_grpc.add_DatasetValidationServiceServicer_to_server(
        dataset_validation_servicer,
        server
    )
    registered['acme.datasets.v1.DatasetValidationService'] = dataset_validation_servicer
    dataset_version_approval_servicer = Factory(lambda: DatasetVersionApprovalServicer(deps))()
    datasets_v1_dataset_version_approval_service_pb2_grpc.add_DatasetVersionApprovalServiceServicer_to_server(
        dataset_version_approval_servicer,
        server
    )
    registered['acme.datasets.v1.DatasetVersionApprovalService'] = dataset_version_approval_servicer
    dataset_version_calculation_servicer = Factory(lambda: DatasetVersionCalculationServicer(deps))()
    datasets_v1_dataset_version_calculation_service_pb2_grpc.add_DatasetVersionCalculationServiceServicer_to_server(
        dataset_version_calculation_servicer,
        server
    )
    registered['acme.datasets.v1.DatasetVersionCalculationService'] = dataset_version_calculation_servicer
    dataset_version_query_servicer = Factory(lambda: DatasetVersionQueryServicer(deps))()
    datasets_v1_dataset_version_query_service_pb2_grpc.add_DatasetVersionQueryServiceServicer_to_server(
        dataset_version_query_servicer,
        server
    )
    registered['acme.datasets.v1.DatasetVersionQueryService'] = dataset_version_query_servicer
    dataset_version_validation_servicer = Factory(lambda: DatasetVersionValidationServicer(deps))()
    datasets_v1_dataset_version_validation_service_pb2_grpc.add_DatasetVersionValidationServiceServicer_to_server(
        dataset_version_validation_servicer,
        server
    )
    registered['acme.datasets.v1.DatasetVersionValidationService'] = dataset_version_validation_servicer
    dataset_version_workflow_servicer = Factory(lambda: DatasetVersionWorkflowServicer(deps))()
    datasets_v1_dataset_version_workflow_service_pb2_grpc.add_DatasetVersionWorkflowServiceServicer_to_server(
        dataset_version_workflow_servicer,
        server
    )
    registered['acme.datasets.v1.DatasetVersionWorkflowService'] = dataset_version_workflow_servicer
    dataset_workflow_servicer = Factory(lambda: DatasetWorkflowServicer(deps))()
    datasets_v1_dataset_workflow_service_pb2_grpc.add_DatasetWorkflowServiceServicer_to_server(
        dataset_workflow_servicer,
        server
    )
    registered['acme.datasets.v1.DatasetWorkflowService'] = dataset_workflow_servicer
    subscribe(deps)
    return registered
