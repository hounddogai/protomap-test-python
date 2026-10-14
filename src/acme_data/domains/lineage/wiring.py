"""Register and compose every service of the lineage domain."""

from __future__ import annotations

import grpc

from acme.analytics.v1 import (
    analytics_event_query_service_pb2_grpc as analytics_v1_analytics_event_query_service_pb2_grpc,
)
from acme.analytics.v1 import analytics_event_service_pb2_grpc as analytics_v1_analytics_event_service_pb2_grpc
from acme.analytics.v1 import funnel_validation_service_pb2_grpc as analytics_v1_funnel_validation_service_pb2_grpc
from acme.anomalies.v1 import (
    anomaly_feedback_validation_service_pb2_grpc as anomalies_v1_anomaly_feedback_validation_service_pb2_grpc,
)
from acme.anomalies.v1 import detector_query_service_pb2_grpc as anomalies_v1_detector_query_service_pb2_grpc
from acme.appointments.v1 import appointment_service_pb2_grpc as appointments_v1_appointment_service_pb2_grpc
from acme.assets.v1 import fixed_asset_service_pb2_grpc as assets_v1_fixed_asset_service_pb2_grpc
from acme.audit.v1 import audit_event_query_service_pb2_grpc as audit_v1_audit_event_query_service_pb2_grpc
from acme.audit.v1 import audit_event_service_pb2_grpc as audit_v1_audit_event_service_pb2_grpc
from acme.authorization.v1 import (
    access_policy_query_service_pb2_grpc as authorization_v1_access_policy_query_service_pb2_grpc,
)
from acme.authorization.v1 import access_policy_service_pb2_grpc as authorization_v1_access_policy_service_pb2_grpc
from acme.authorization.v1 import (
    access_policy_validation_service_pb2_grpc as authorization_v1_access_policy_validation_service_pb2_grpc,
)
from acme.careplans.v1 import (
    care_plan_calculation_service_pb2_grpc as careplans_v1_care_plan_calculation_service_pb2_grpc,
)
from acme.catalog.v1 import product_query_service_pb2_grpc as catalog_v1_product_query_service_pb2_grpc
from acme.certificates.v1 import (
    certificate_calculation_service_pb2_grpc as certificates_v1_certificate_calculation_service_pb2_grpc,
)
from acme.checkout.v1 import checkout_session_service_pb2_grpc as checkout_v1_checkout_session_service_pb2_grpc
from acme.concessions.v1 import (
    concession_stand_calculation_service_pb2_grpc as concessions_v1_concession_stand_calculation_service_pb2_grpc,
)
from acme.configuration.v1 import (
    config_set_calculation_service_pb2_grpc as configuration_v1_config_set_calculation_service_pb2_grpc,
)
from acme.configuration.v1 import (
    config_set_query_service_pb2_grpc as configuration_v1_config_set_query_service_pb2_grpc,
)
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
from acme.datasets.v1 import (
    dataset_version_validation_service_pb2_grpc as datasets_v1_dataset_version_validation_service_pb2_grpc,
)
from acme.deliveries.v1 import delivery_service_pb2_grpc as deliveries_v1_delivery_service_pb2_grpc
from acme.dispatch.v1 import dispatch_order_query_service_pb2_grpc as dispatch_v1_dispatch_order_query_service_pb2_grpc
from acme.documents.v1 import document_query_service_pb2_grpc as documents_v1_document_query_service_pb2_grpc
from acme.documents.v1 import document_validation_service_pb2_grpc as documents_v1_document_validation_service_pb2_grpc
from acme.featureflags.v1 import (
    feature_flag_query_service_pb2_grpc as featureflags_v1_feature_flag_query_service_pb2_grpc,
)
from acme.featureflags.v1 import feature_flag_service_pb2_grpc as featureflags_v1_feature_flag_service_pb2_grpc
from acme.featureflags.v1 import (
    feature_flag_validation_service_pb2_grpc as featureflags_v1_feature_flag_validation_service_pb2_grpc,
)
from acme.featurestore.v1 import (
    feature_value_calculation_service_pb2_grpc as featurestore_v1_feature_value_calculation_service_pb2_grpc,
)
from acme.featurestore.v1 import feature_view_service_pb2_grpc as featurestore_v1_feature_view_service_pb2_grpc
from acme.featurestore.v1 import (
    feature_view_validation_service_pb2_grpc as featurestore_v1_feature_view_validation_service_pb2_grpc,
)
from acme.fleet.v1 import vehicle_service_pb2_grpc as fleet_v1_vehicle_service_pb2_grpc
from acme.forecasting.v1 import (
    demand_forecast_validation_service_pb2_grpc as forecasting_v1_demand_forecast_validation_service_pb2_grpc,
)
from acme.forecasting.v1 import (
    forecast_model_query_service_pb2_grpc as forecasting_v1_forecast_model_query_service_pb2_grpc,
)
from acme.forecasting.v1 import (
    forecast_model_validation_service_pb2_grpc as forecasting_v1_forecast_model_validation_service_pb2_grpc,
)
from acme.forecasting.v1 import (
    scenario_calculation_service_pb2_grpc as forecasting_v1_scenario_calculation_service_pb2_grpc,
)
from acme.forecasting.v1 import (
    scenario_validation_service_pb2_grpc as forecasting_v1_scenario_validation_service_pb2_grpc,
)
from acme.forms.v1 import form_query_service_pb2_grpc as forms_v1_form_query_service_pb2_grpc
from acme.fulfillment.v1 import fulfillment_query_service_pb2_grpc as fulfillment_v1_fulfillment_query_service_pb2_grpc
from acme.identity.v1 import user_query_service_pb2_grpc as identity_v1_user_query_service_pb2_grpc
from acme.identity.v1 import user_service_pb2_grpc as identity_v1_user_service_pb2_grpc
from acme.keymanagement.v1 import (
    crypto_key_query_service_pb2_grpc as keymanagement_v1_crypto_key_query_service_pb2_grpc,
)
from acme.keymanagement.v1 import crypto_key_service_pb2_grpc as keymanagement_v1_crypto_key_service_pb2_grpc
from acme.labeling.v1 import (
    annotation_calculation_service_pb2_grpc as labeling_v1_annotation_calculation_service_pb2_grpc,
)
from acme.labeling.v1 import label_set_validation_service_pb2_grpc as labeling_v1_label_set_validation_service_pb2_grpc
from acme.labeling.v1 import labeling_task_query_service_pb2_grpc as labeling_v1_labeling_task_query_service_pb2_grpc
from acme.labeling.v1 import labeling_task_service_pb2_grpc as labeling_v1_labeling_task_service_pb2_grpc
from acme.labeling.v1 import (
    labeling_task_validation_service_pb2_grpc as labeling_v1_labeling_task_validation_service_pb2_grpc,
)
from acme.ledger.v1 import ledger_account_service_pb2_grpc as ledger_v1_ledger_account_service_pb2_grpc
from acme.ledger.v1 import (
    ledger_account_validation_service_pb2_grpc as ledger_v1_ledger_account_validation_service_pb2_grpc,
)
from acme.lending.v1 import loan_application_service_pb2_grpc as lending_v1_loan_application_service_pb2_grpc
from acme.lineage.v1 import impact_approval_service_pb2_grpc as lineage_v1_impact_approval_service_pb2_grpc
from acme.lineage.v1 import impact_calculation_service_pb2_grpc as lineage_v1_impact_calculation_service_pb2_grpc
from acme.lineage.v1 import impact_import_service_pb2_grpc as lineage_v1_impact_import_service_pb2_grpc
from acme.lineage.v1 import impact_lifecycle_service_pb2_grpc as lineage_v1_impact_lifecycle_service_pb2_grpc
from acme.lineage.v1 import impact_reporting_service_pb2_grpc as lineage_v1_impact_reporting_service_pb2_grpc
from acme.lineage.v1 import impact_sync_service_pb2_grpc as lineage_v1_impact_sync_service_pb2_grpc
from acme.lineage.v1 import impact_validation_service_pb2_grpc as lineage_v1_impact_validation_service_pb2_grpc
from acme.lineage.v1 import impact_workflow_service_pb2_grpc as lineage_v1_impact_workflow_service_pb2_grpc
from acme.lineage.v1 import lineage_edge_approval_service_pb2_grpc as lineage_v1_lineage_edge_approval_service_pb2_grpc
from acme.lineage.v1 import (
    lineage_edge_calculation_service_pb2_grpc as lineage_v1_lineage_edge_calculation_service_pb2_grpc,
)
from acme.lineage.v1 import lineage_edge_import_service_pb2_grpc as lineage_v1_lineage_edge_import_service_pb2_grpc
from acme.lineage.v1 import (
    lineage_edge_lifecycle_service_pb2_grpc as lineage_v1_lineage_edge_lifecycle_service_pb2_grpc,
)
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
from acme.lineage.v1 import (
    lineage_node_lifecycle_service_pb2_grpc as lineage_v1_lineage_node_lifecycle_service_pb2_grpc,
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
from acme.messaging.v1 import (
    conversation_calculation_service_pb2_grpc as messaging_v1_conversation_calculation_service_pb2_grpc,
)
from acme.metrics.v1 import dashboard_export_service_pb2_grpc as metrics_v1_dashboard_export_service_pb2_grpc
from acme.metrics.v1 import dashboard_history_service_pb2_grpc as metrics_v1_dashboard_history_service_pb2_grpc
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
from acme.metrics.v1 import metric_series_query_service_pb2_grpc as metrics_v1_metric_series_query_service_pb2_grpc
from acme.metrics.v1 import metric_series_service_pb2_grpc as metrics_v1_metric_series_service_pb2_grpc
from acme.metrics.v1 import (
    metric_series_validation_service_pb2_grpc as metrics_v1_metric_series_validation_service_pb2_grpc,
)
from acme.modelregistry.v1 import (
    model_version_calculation_service_pb2_grpc as modelregistry_v1_model_version_calculation_service_pb2_grpc,
)
from acme.modelregistry.v1 import (
    registered_model_query_service_pb2_grpc as modelregistry_v1_registered_model_query_service_pb2_grpc,
)
from acme.notifications.v1 import (
    notification_query_service_pb2_grpc as notifications_v1_notification_query_service_pb2_grpc,
)
from acme.notifications.v1 import notification_service_pb2_grpc as notifications_v1_notification_service_pb2_grpc
from acme.notifications.v1 import (
    notification_validation_service_pb2_grpc as notifications_v1_notification_validation_service_pb2_grpc,
)
from acme.performers.v1 import performer_query_service_pb2_grpc as performers_v1_performer_query_service_pb2_grpc
from acme.pipelines.v1 import pipeline_query_service_pb2_grpc as pipelines_v1_pipeline_query_service_pb2_grpc
from acme.pipelines.v1 import (
    pipeline_run_calculation_service_pb2_grpc as pipelines_v1_pipeline_run_calculation_service_pb2_grpc,
)
from acme.pipelines.v1 import (
    pipeline_run_validation_service_pb2_grpc as pipelines_v1_pipeline_run_validation_service_pb2_grpc,
)
from acme.pipelines.v1 import pipeline_service_pb2_grpc as pipelines_v1_pipeline_service_pb2_grpc
from acme.pipelines.v1 import (
    pipeline_step_calculation_service_pb2_grpc as pipelines_v1_pipeline_step_calculation_service_pb2_grpc,
)
from acme.pipelines.v1 import pipeline_validation_service_pb2_grpc as pipelines_v1_pipeline_validation_service_pb2_grpc
from acme.prescriptions.v1 import (
    prescription_calculation_service_pb2_grpc as prescriptions_v1_prescription_calculation_service_pb2_grpc,
)
from acme.promotions.v1 import promotion_query_service_pb2_grpc as promotions_v1_promotion_query_service_pb2_grpc
from acme.recommendations.v1 import (
    interaction_validation_service_pb2_grpc as recommendations_v1_interaction_validation_service_pb2_grpc,
)
from acme.recommendations.v1 import (
    recommendation_model_calculation_service_pb2_grpc as recommendations_v1_recommendation_model_calculation_service_pb2_grpc,
)
from acme.recommendations.v1 import (
    recommendation_model_validation_service_pb2_grpc as recommendations_v1_recommendation_model_validation_service_pb2_grpc,
)
from acme.recommendations.v1 import (
    recommendation_set_service_pb2_grpc as recommendations_v1_recommendation_set_service_pb2_grpc,
)
from acme.recruiting.v1 import job_opening_query_service_pb2_grpc as recruiting_v1_job_opening_query_service_pb2_grpc
from acme.returns.v1 import return_request_query_service_pb2_grpc as returns_v1_return_request_query_service_pb2_grpc
from acme.reviews.v1 import product_review_service_pb2_grpc as reviews_v1_product_review_service_pb2_grpc
from acme.search.v1 import search_index_query_service_pb2_grpc as search_v1_search_index_query_service_pb2_grpc
from acme.search.v1 import search_index_service_pb2_grpc as search_v1_search_index_service_pb2_grpc
from acme.search.v1 import (
    search_index_validation_service_pb2_grpc as search_v1_search_index_validation_service_pb2_grpc,
)
from acme.seating.v1 import seat_map_service_pb2_grpc as seating_v1_seat_map_service_pb2_grpc
from acme.shipping.v1 import shipment_query_service_pb2_grpc as shipping_v1_shipment_query_service_pb2_grpc
from acme.travel.v1 import trip_query_service_pb2_grpc as travel_v1_trip_query_service_pb2_grpc
from acme.venues.v1 import venue_query_service_pb2_grpc as venues_v1_venue_query_service_pb2_grpc
from acme.venues.v1 import venue_validation_service_pb2_grpc as venues_v1_venue_validation_service_pb2_grpc

from acme_data.domains.lineage.dependencies import Clients
from acme_data.domains.lineage.dependencies import Dependencies
from acme_data.domains.lineage.events import subscribe
from acme_data.domains.lineage.impact_approval_service import ImpactApprovalServicer
from acme_data.domains.lineage.impact_calculation_service import ImpactCalculationServicer
from acme_data.domains.lineage.impact_import_service import ImpactImportServicer
from acme_data.domains.lineage.impact_lifecycle_service import ImpactLifecycleServicer
from acme_data.domains.lineage.impact_reporting_service import ImpactReportingServicer
from acme_data.domains.lineage.impact_sync_service import ImpactSyncServicer
from acme_data.domains.lineage.impact_validation_service import ImpactValidationServicer
from acme_data.domains.lineage.impact_workflow_service import ImpactWorkflowServicer
from acme_data.domains.lineage.lineage_edge_approval_service import LineageEdgeApprovalServicer
from acme_data.domains.lineage.lineage_edge_calculation_service import LineageEdgeCalculationServicer
from acme_data.domains.lineage.lineage_edge_import_service import LineageEdgeImportServicer
from acme_data.domains.lineage.lineage_edge_lifecycle_service import LineageEdgeLifecycleServicer
from acme_data.domains.lineage.lineage_edge_query_service import LineageEdgeQueryServicer
from acme_data.domains.lineage.lineage_edge_reporting_service import LineageEdgeReportingServicer
from acme_data.domains.lineage.lineage_edge_sync_service import LineageEdgeSyncServicer
from acme_data.domains.lineage.lineage_edge_validation_service import LineageEdgeValidationServicer
from acme_data.domains.lineage.lineage_edge_workflow_service import LineageEdgeWorkflowServicer
from acme_data.domains.lineage.lineage_node_approval_service import LineageNodeApprovalServicer
from acme_data.domains.lineage.lineage_node_calculation_service import LineageNodeCalculationServicer
from acme_data.domains.lineage.lineage_node_lifecycle_service import LineageNodeLifecycleServicer
from acme_data.domains.lineage.lineage_node_query_service import LineageNodeQueryServicer
from acme_data.domains.lineage.lineage_node_reporting_service import LineageNodeReportingServicer
from acme_data.domains.lineage.lineage_node_service import LineageNodeServicer
from acme_data.domains.lineage.lineage_node_sync_service import LineageNodeSyncServicer
from acme_data.domains.lineage.lineage_node_validation_service import LineageNodeValidationServicer
from acme_data.domains.lineage.lineage_node_workflow_service import LineageNodeWorkflowServicer
from acme_data.domains.lineage.repository import DomainRepository
from acme_data.platform.container import Container
from acme_data.platform.container import Factory


def dependencies(container: Container) -> Dependencies:
    analytics_analytics_event_query = container.singleton(
        analytics_v1_analytics_event_query_service_pb2_grpc.AnalyticsEventQueryServiceStub,
        lambda: analytics_v1_analytics_event_query_service_pb2_grpc.AnalyticsEventQueryServiceStub(container.channel)
    )
    analytics_analytics_event = container.singleton(
        analytics_v1_analytics_event_service_pb2_grpc.AnalyticsEventServiceStub,
        lambda: analytics_v1_analytics_event_service_pb2_grpc.AnalyticsEventServiceStub(container.channel)
    )
    analytics_funnel_validation = container.singleton(
        analytics_v1_funnel_validation_service_pb2_grpc.FunnelValidationServiceStub,
        lambda: analytics_v1_funnel_validation_service_pb2_grpc.FunnelValidationServiceStub(container.channel)
    )
    anomalies_anomaly_feedback_validation = container.singleton(
        anomalies_v1_anomaly_feedback_validation_service_pb2_grpc.AnomalyFeedbackValidationServiceStub,
        lambda: anomalies_v1_anomaly_feedback_validation_service_pb2_grpc.AnomalyFeedbackValidationServiceStub(
            container.channel
        )
    )
    anomalies_detector_query = container.singleton(
        anomalies_v1_detector_query_service_pb2_grpc.DetectorQueryServiceStub,
        lambda: anomalies_v1_detector_query_service_pb2_grpc.DetectorQueryServiceStub(container.channel)
    )
    appointments_appointment = container.singleton(
        appointments_v1_appointment_service_pb2_grpc.AppointmentServiceStub,
        lambda: appointments_v1_appointment_service_pb2_grpc.AppointmentServiceStub(container.channel)
    )
    assets_fixed_asset = container.singleton(
        assets_v1_fixed_asset_service_pb2_grpc.FixedAssetServiceStub,
        lambda: assets_v1_fixed_asset_service_pb2_grpc.FixedAssetServiceStub(container.channel)
    )
    audit_audit_event_query = container.singleton(
        audit_v1_audit_event_query_service_pb2_grpc.AuditEventQueryServiceStub,
        lambda: audit_v1_audit_event_query_service_pb2_grpc.AuditEventQueryServiceStub(container.channel)
    )
    audit_audit_event = container.singleton(
        audit_v1_audit_event_service_pb2_grpc.AuditEventServiceStub,
        lambda: audit_v1_audit_event_service_pb2_grpc.AuditEventServiceStub(container.channel)
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
    careplans_care_plan_calculation = container.singleton(
        careplans_v1_care_plan_calculation_service_pb2_grpc.CarePlanCalculationServiceStub,
        lambda: careplans_v1_care_plan_calculation_service_pb2_grpc.CarePlanCalculationServiceStub(container.channel)
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
    checkout_checkout_session = container.singleton(
        checkout_v1_checkout_session_service_pb2_grpc.CheckoutSessionServiceStub,
        lambda: checkout_v1_checkout_session_service_pb2_grpc.CheckoutSessionServiceStub(container.channel)
    )
    concessions_concession_stand_calculation = container.singleton(
        concessions_v1_concession_stand_calculation_service_pb2_grpc.ConcessionStandCalculationServiceStub,
        lambda: concessions_v1_concession_stand_calculation_service_pb2_grpc.ConcessionStandCalculationServiceStub(
            container.channel
        )
    )
    configuration_config_set_calculation = container.singleton(
        configuration_v1_config_set_calculation_service_pb2_grpc.ConfigSetCalculationServiceStub,
        lambda: configuration_v1_config_set_calculation_service_pb2_grpc.ConfigSetCalculationServiceStub(
            container.channel
        )
    )
    configuration_config_set_query = container.singleton(
        configuration_v1_config_set_query_service_pb2_grpc.ConfigSetQueryServiceStub,
        lambda: configuration_v1_config_set_query_service_pb2_grpc.ConfigSetQueryServiceStub(container.channel)
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
    datasets_dataset_version_validation = container.singleton(
        datasets_v1_dataset_version_validation_service_pb2_grpc.DatasetVersionValidationServiceStub,
        lambda: datasets_v1_dataset_version_validation_service_pb2_grpc.DatasetVersionValidationServiceStub(
            container.channel
        )
    )
    deliveries_delivery = container.singleton(
        deliveries_v1_delivery_service_pb2_grpc.DeliveryServiceStub,
        lambda: deliveries_v1_delivery_service_pb2_grpc.DeliveryServiceStub(container.channel)
    )
    dispatch_dispatch_order_query = container.singleton(
        dispatch_v1_dispatch_order_query_service_pb2_grpc.DispatchOrderQueryServiceStub,
        lambda: dispatch_v1_dispatch_order_query_service_pb2_grpc.DispatchOrderQueryServiceStub(container.channel)
    )
    documents_document_query = container.singleton(
        documents_v1_document_query_service_pb2_grpc.DocumentQueryServiceStub,
        lambda: documents_v1_document_query_service_pb2_grpc.DocumentQueryServiceStub(container.channel)
    )
    documents_document_validation = container.singleton(
        documents_v1_document_validation_service_pb2_grpc.DocumentValidationServiceStub,
        lambda: documents_v1_document_validation_service_pb2_grpc.DocumentValidationServiceStub(container.channel)
    )
    featureflags_feature_flag_query = container.singleton(
        featureflags_v1_feature_flag_query_service_pb2_grpc.FeatureFlagQueryServiceStub,
        lambda: featureflags_v1_feature_flag_query_service_pb2_grpc.FeatureFlagQueryServiceStub(container.channel)
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
    featurestore_feature_value_calculation = container.singleton(
        featurestore_v1_feature_value_calculation_service_pb2_grpc.FeatureValueCalculationServiceStub,
        lambda: featurestore_v1_feature_value_calculation_service_pb2_grpc.FeatureValueCalculationServiceStub(
            container.channel
        )
    )
    featurestore_feature_view = container.singleton(
        featurestore_v1_feature_view_service_pb2_grpc.FeatureViewServiceStub,
        lambda: featurestore_v1_feature_view_service_pb2_grpc.FeatureViewServiceStub(container.channel)
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
    forecasting_demand_forecast_validation = container.singleton(
        forecasting_v1_demand_forecast_validation_service_pb2_grpc.DemandForecastValidationServiceStub,
        lambda: forecasting_v1_demand_forecast_validation_service_pb2_grpc.DemandForecastValidationServiceStub(
            container.channel
        )
    )
    forecasting_forecast_model_query = container.singleton(
        forecasting_v1_forecast_model_query_service_pb2_grpc.ForecastModelQueryServiceStub,
        lambda: forecasting_v1_forecast_model_query_service_pb2_grpc.ForecastModelQueryServiceStub(container.channel)
    )
    forecasting_forecast_model_validation = container.singleton(
        forecasting_v1_forecast_model_validation_service_pb2_grpc.ForecastModelValidationServiceStub,
        lambda: forecasting_v1_forecast_model_validation_service_pb2_grpc.ForecastModelValidationServiceStub(
            container.channel
        )
    )
    forecasting_scenario_calculation = container.singleton(
        forecasting_v1_scenario_calculation_service_pb2_grpc.ScenarioCalculationServiceStub,
        lambda: forecasting_v1_scenario_calculation_service_pb2_grpc.ScenarioCalculationServiceStub(container.channel)
    )
    forecasting_scenario_validation = container.singleton(
        forecasting_v1_scenario_validation_service_pb2_grpc.ScenarioValidationServiceStub,
        lambda: forecasting_v1_scenario_validation_service_pb2_grpc.ScenarioValidationServiceStub(container.channel)
    )
    forms_form_query = container.singleton(
        forms_v1_form_query_service_pb2_grpc.FormQueryServiceStub,
        lambda: forms_v1_form_query_service_pb2_grpc.FormQueryServiceStub(container.channel)
    )
    fulfillment_fulfillment_query = container.singleton(
        fulfillment_v1_fulfillment_query_service_pb2_grpc.FulfillmentQueryServiceStub,
        lambda: fulfillment_v1_fulfillment_query_service_pb2_grpc.FulfillmentQueryServiceStub(container.channel)
    )
    identity_user_query = container.singleton(
        identity_v1_user_query_service_pb2_grpc.UserQueryServiceStub,
        lambda: identity_v1_user_query_service_pb2_grpc.UserQueryServiceStub(container.channel)
    )
    identity_user = container.singleton(
        identity_v1_user_service_pb2_grpc.UserServiceStub,
        lambda: identity_v1_user_service_pb2_grpc.UserServiceStub(container.channel)
    )
    keymanagement_crypto_key_query = container.singleton(
        keymanagement_v1_crypto_key_query_service_pb2_grpc.CryptoKeyQueryServiceStub,
        lambda: keymanagement_v1_crypto_key_query_service_pb2_grpc.CryptoKeyQueryServiceStub(container.channel)
    )
    keymanagement_crypto_key = container.singleton(
        keymanagement_v1_crypto_key_service_pb2_grpc.CryptoKeyServiceStub,
        lambda: keymanagement_v1_crypto_key_service_pb2_grpc.CryptoKeyServiceStub(container.channel)
    )
    labeling_annotation_calculation = container.singleton(
        labeling_v1_annotation_calculation_service_pb2_grpc.AnnotationCalculationServiceStub,
        lambda: labeling_v1_annotation_calculation_service_pb2_grpc.AnnotationCalculationServiceStub(container.channel)
    )
    labeling_label_set_validation = container.singleton(
        labeling_v1_label_set_validation_service_pb2_grpc.LabelSetValidationServiceStub,
        lambda: labeling_v1_label_set_validation_service_pb2_grpc.LabelSetValidationServiceStub(container.channel)
    )
    labeling_labeling_task_query = container.singleton(
        labeling_v1_labeling_task_query_service_pb2_grpc.LabelingTaskQueryServiceStub,
        lambda: labeling_v1_labeling_task_query_service_pb2_grpc.LabelingTaskQueryServiceStub(container.channel)
    )
    labeling_labeling_task = container.singleton(
        labeling_v1_labeling_task_service_pb2_grpc.LabelingTaskServiceStub,
        lambda: labeling_v1_labeling_task_service_pb2_grpc.LabelingTaskServiceStub(container.channel)
    )
    labeling_labeling_task_validation = container.singleton(
        labeling_v1_labeling_task_validation_service_pb2_grpc.LabelingTaskValidationServiceStub,
        lambda: labeling_v1_labeling_task_validation_service_pb2_grpc.LabelingTaskValidationServiceStub(
            container.channel
        )
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
    lending_loan_application = container.singleton(
        lending_v1_loan_application_service_pb2_grpc.LoanApplicationServiceStub,
        lambda: lending_v1_loan_application_service_pb2_grpc.LoanApplicationServiceStub(container.channel)
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
    lineage_impact_reporting = container.singleton(
        lineage_v1_impact_reporting_service_pb2_grpc.ImpactReportingServiceStub,
        lambda: lineage_v1_impact_reporting_service_pb2_grpc.ImpactReportingServiceStub(container.channel)
    )
    lineage_impact_sync = container.singleton(
        lineage_v1_impact_sync_service_pb2_grpc.ImpactSyncServiceStub,
        lambda: lineage_v1_impact_sync_service_pb2_grpc.ImpactSyncServiceStub(container.channel)
    )
    lineage_impact_validation = container.singleton(
        lineage_v1_impact_validation_service_pb2_grpc.ImpactValidationServiceStub,
        lambda: lineage_v1_impact_validation_service_pb2_grpc.ImpactValidationServiceStub(container.channel)
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
    lineage_lineage_edge_lifecycle = container.singleton(
        lineage_v1_lineage_edge_lifecycle_service_pb2_grpc.LineageEdgeLifecycleServiceStub,
        lambda: lineage_v1_lineage_edge_lifecycle_service_pb2_grpc.LineageEdgeLifecycleServiceStub(container.channel)
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
    lineage_lineage_node_lifecycle = container.singleton(
        lineage_v1_lineage_node_lifecycle_service_pb2_grpc.LineageNodeLifecycleServiceStub,
        lambda: lineage_v1_lineage_node_lifecycle_service_pb2_grpc.LineageNodeLifecycleServiceStub(container.channel)
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
    messaging_conversation_calculation = container.singleton(
        messaging_v1_conversation_calculation_service_pb2_grpc.ConversationCalculationServiceStub,
        lambda: messaging_v1_conversation_calculation_service_pb2_grpc.ConversationCalculationServiceStub(
            container.channel
        )
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
    metrics_metric_series_query = container.singleton(
        metrics_v1_metric_series_query_service_pb2_grpc.MetricSeriesQueryServiceStub,
        lambda: metrics_v1_metric_series_query_service_pb2_grpc.MetricSeriesQueryServiceStub(container.channel)
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
    modelregistry_model_version_calculation = container.singleton(
        modelregistry_v1_model_version_calculation_service_pb2_grpc.ModelVersionCalculationServiceStub,
        lambda: modelregistry_v1_model_version_calculation_service_pb2_grpc.ModelVersionCalculationServiceStub(
            container.channel
        )
    )
    modelregistry_registered_model_query = container.singleton(
        modelregistry_v1_registered_model_query_service_pb2_grpc.RegisteredModelQueryServiceStub,
        lambda: modelregistry_v1_registered_model_query_service_pb2_grpc.RegisteredModelQueryServiceStub(
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
    performers_performer_query = container.singleton(
        performers_v1_performer_query_service_pb2_grpc.PerformerQueryServiceStub,
        lambda: performers_v1_performer_query_service_pb2_grpc.PerformerQueryServiceStub(container.channel)
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
    pipelines_pipeline_run_validation = container.singleton(
        pipelines_v1_pipeline_run_validation_service_pb2_grpc.PipelineRunValidationServiceStub,
        lambda: pipelines_v1_pipeline_run_validation_service_pb2_grpc.PipelineRunValidationServiceStub(
            container.channel
        )
    )
    pipelines_pipeline = container.singleton(
        pipelines_v1_pipeline_service_pb2_grpc.PipelineServiceStub,
        lambda: pipelines_v1_pipeline_service_pb2_grpc.PipelineServiceStub(container.channel)
    )
    pipelines_pipeline_step_calculation = container.singleton(
        pipelines_v1_pipeline_step_calculation_service_pb2_grpc.PipelineStepCalculationServiceStub,
        lambda: pipelines_v1_pipeline_step_calculation_service_pb2_grpc.PipelineStepCalculationServiceStub(
            container.channel
        )
    )
    pipelines_pipeline_validation = container.singleton(
        pipelines_v1_pipeline_validation_service_pb2_grpc.PipelineValidationServiceStub,
        lambda: pipelines_v1_pipeline_validation_service_pb2_grpc.PipelineValidationServiceStub(container.channel)
    )
    prescriptions_prescription_calculation = container.singleton(
        prescriptions_v1_prescription_calculation_service_pb2_grpc.PrescriptionCalculationServiceStub,
        lambda: prescriptions_v1_prescription_calculation_service_pb2_grpc.PrescriptionCalculationServiceStub(
            container.channel
        )
    )
    promotions_promotion_query = container.singleton(
        promotions_v1_promotion_query_service_pb2_grpc.PromotionQueryServiceStub,
        lambda: promotions_v1_promotion_query_service_pb2_grpc.PromotionQueryServiceStub(container.channel)
    )
    recommendations_interaction_validation = container.singleton(
        recommendations_v1_interaction_validation_service_pb2_grpc.InteractionValidationServiceStub,
        lambda: recommendations_v1_interaction_validation_service_pb2_grpc.InteractionValidationServiceStub(
            container.channel
        )
    )
    recommendations_recommendation_model_calculation = container.singleton(
        recommendations_v1_recommendation_model_calculation_service_pb2_grpc.RecommendationModelCalculationServiceStub,
        lambda: recommendations_v1_recommendation_model_calculation_service_pb2_grpc.RecommendationModelCalculationServiceStub(
            container.channel
        )
    )
    recommendations_recommendation_model_validation = container.singleton(
        recommendations_v1_recommendation_model_validation_service_pb2_grpc.RecommendationModelValidationServiceStub,
        lambda: recommendations_v1_recommendation_model_validation_service_pb2_grpc.RecommendationModelValidationServiceStub(
            container.channel
        )
    )
    recommendations_recommendation_set = container.singleton(
        recommendations_v1_recommendation_set_service_pb2_grpc.RecommendationSetServiceStub,
        lambda: recommendations_v1_recommendation_set_service_pb2_grpc.RecommendationSetServiceStub(container.channel)
    )
    recruiting_job_opening_query = container.singleton(
        recruiting_v1_job_opening_query_service_pb2_grpc.JobOpeningQueryServiceStub,
        lambda: recruiting_v1_job_opening_query_service_pb2_grpc.JobOpeningQueryServiceStub(container.channel)
    )
    returns_return_request_query = container.singleton(
        returns_v1_return_request_query_service_pb2_grpc.ReturnRequestQueryServiceStub,
        lambda: returns_v1_return_request_query_service_pb2_grpc.ReturnRequestQueryServiceStub(container.channel)
    )
    reviews_product_review = container.singleton(
        reviews_v1_product_review_service_pb2_grpc.ProductReviewServiceStub,
        lambda: reviews_v1_product_review_service_pb2_grpc.ProductReviewServiceStub(container.channel)
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
    seating_seat_map = container.singleton(
        seating_v1_seat_map_service_pb2_grpc.SeatMapServiceStub,
        lambda: seating_v1_seat_map_service_pb2_grpc.SeatMapServiceStub(container.channel)
    )
    shipping_shipment_query = container.singleton(
        shipping_v1_shipment_query_service_pb2_grpc.ShipmentQueryServiceStub,
        lambda: shipping_v1_shipment_query_service_pb2_grpc.ShipmentQueryServiceStub(container.channel)
    )
    travel_trip_query = container.singleton(
        travel_v1_trip_query_service_pb2_grpc.TripQueryServiceStub,
        lambda: travel_v1_trip_query_service_pb2_grpc.TripQueryServiceStub(container.channel)
    )
    venues_venue_query = container.singleton(
        venues_v1_venue_query_service_pb2_grpc.VenueQueryServiceStub,
        lambda: venues_v1_venue_query_service_pb2_grpc.VenueQueryServiceStub(container.channel)
    )
    venues_venue_validation = container.singleton(
        venues_v1_venue_validation_service_pb2_grpc.VenueValidationServiceStub,
        lambda: venues_v1_venue_validation_service_pb2_grpc.VenueValidationServiceStub(container.channel)
    )
    clients = Clients(
        analytics_analytics_event_query=analytics_analytics_event_query,
        analytics_analytics_event=analytics_analytics_event,
        analytics_funnel_validation=analytics_funnel_validation,
        anomalies_anomaly_feedback_validation=anomalies_anomaly_feedback_validation,
        anomalies_detector_query=anomalies_detector_query,
        appointments_appointment=appointments_appointment,
        assets_fixed_asset=assets_fixed_asset,
        audit_audit_event_query=audit_audit_event_query,
        audit_audit_event=audit_audit_event,
        authorization_access_policy_query=authorization_access_policy_query,
        authorization_access_policy=authorization_access_policy,
        authorization_access_policy_validation=authorization_access_policy_validation,
        careplans_care_plan_calculation=careplans_care_plan_calculation,
        catalog_product_query=catalog_product_query,
        certificates_certificate_calculation=certificates_certificate_calculation,
        checkout_checkout_session=checkout_checkout_session,
        concessions_concession_stand_calculation=concessions_concession_stand_calculation,
        configuration_config_set_calculation=configuration_config_set_calculation,
        configuration_config_set_query=configuration_config_set_query,
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
        datasets_dataset_version_validation=datasets_dataset_version_validation,
        deliveries_delivery=deliveries_delivery,
        dispatch_dispatch_order_query=dispatch_dispatch_order_query,
        documents_document_query=documents_document_query,
        documents_document_validation=documents_document_validation,
        featureflags_feature_flag_query=featureflags_feature_flag_query,
        featureflags_feature_flag=featureflags_feature_flag,
        featureflags_feature_flag_validation=featureflags_feature_flag_validation,
        featurestore_feature_value_calculation=featurestore_feature_value_calculation,
        featurestore_feature_view=featurestore_feature_view,
        featurestore_feature_view_validation=featurestore_feature_view_validation,
        fleet_vehicle=fleet_vehicle,
        forecasting_demand_forecast_validation=forecasting_demand_forecast_validation,
        forecasting_forecast_model_query=forecasting_forecast_model_query,
        forecasting_forecast_model_validation=forecasting_forecast_model_validation,
        forecasting_scenario_calculation=forecasting_scenario_calculation,
        forecasting_scenario_validation=forecasting_scenario_validation,
        forms_form_query=forms_form_query,
        fulfillment_fulfillment_query=fulfillment_fulfillment_query,
        identity_user_query=identity_user_query,
        identity_user=identity_user,
        keymanagement_crypto_key_query=keymanagement_crypto_key_query,
        keymanagement_crypto_key=keymanagement_crypto_key,
        labeling_annotation_calculation=labeling_annotation_calculation,
        labeling_label_set_validation=labeling_label_set_validation,
        labeling_labeling_task_query=labeling_labeling_task_query,
        labeling_labeling_task=labeling_labeling_task,
        labeling_labeling_task_validation=labeling_labeling_task_validation,
        ledger_ledger_account=ledger_ledger_account,
        ledger_ledger_account_validation=ledger_ledger_account_validation,
        lending_loan_application=lending_loan_application,
        lineage_impact_calculation=lineage_impact_calculation,
        lineage_impact_import=lineage_impact_import,
        lineage_impact_lifecycle=lineage_impact_lifecycle,
        lineage_impact_reporting=lineage_impact_reporting,
        lineage_impact_sync=lineage_impact_sync,
        lineage_impact_validation=lineage_impact_validation,
        lineage_lineage_edge_approval=lineage_lineage_edge_approval,
        lineage_lineage_edge_calculation=lineage_lineage_edge_calculation,
        lineage_lineage_edge_import=lineage_lineage_edge_import,
        lineage_lineage_edge_lifecycle=lineage_lineage_edge_lifecycle,
        lineage_lineage_edge_query=lineage_lineage_edge_query,
        lineage_lineage_edge_reporting=lineage_lineage_edge_reporting,
        lineage_lineage_edge_sync=lineage_lineage_edge_sync,
        lineage_lineage_edge_validation=lineage_lineage_edge_validation,
        lineage_lineage_edge_workflow=lineage_lineage_edge_workflow,
        lineage_lineage_node_approval=lineage_lineage_node_approval,
        lineage_lineage_node_calculation=lineage_lineage_node_calculation,
        lineage_lineage_node_lifecycle=lineage_lineage_node_lifecycle,
        lineage_lineage_node_query=lineage_lineage_node_query,
        lineage_lineage_node_reporting=lineage_lineage_node_reporting,
        lineage_lineage_node=lineage_lineage_node,
        lineage_lineage_node_sync=lineage_lineage_node_sync,
        lineage_lineage_node_validation=lineage_lineage_node_validation,
        lineage_lineage_node_workflow=lineage_lineage_node_workflow,
        messaging_conversation_calculation=messaging_conversation_calculation,
        metrics_dashboard_export=metrics_dashboard_export,
        metrics_dashboard_history=metrics_dashboard_history,
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
        metrics_metric_series_query=metrics_metric_series_query,
        metrics_metric_series=metrics_metric_series,
        metrics_metric_series_validation=metrics_metric_series_validation,
        modelregistry_model_version_calculation=modelregistry_model_version_calculation,
        modelregistry_registered_model_query=modelregistry_registered_model_query,
        notifications_notification_query=notifications_notification_query,
        notifications_notification=notifications_notification,
        notifications_notification_validation=notifications_notification_validation,
        performers_performer_query=performers_performer_query,
        pipelines_pipeline_query=pipelines_pipeline_query,
        pipelines_pipeline_run_calculation=pipelines_pipeline_run_calculation,
        pipelines_pipeline_run_validation=pipelines_pipeline_run_validation,
        pipelines_pipeline=pipelines_pipeline,
        pipelines_pipeline_step_calculation=pipelines_pipeline_step_calculation,
        pipelines_pipeline_validation=pipelines_pipeline_validation,
        prescriptions_prescription_calculation=prescriptions_prescription_calculation,
        promotions_promotion_query=promotions_promotion_query,
        recommendations_interaction_validation=recommendations_interaction_validation,
        recommendations_recommendation_model_calculation=recommendations_recommendation_model_calculation,
        recommendations_recommendation_model_validation=recommendations_recommendation_model_validation,
        recommendations_recommendation_set=recommendations_recommendation_set,
        recruiting_job_opening_query=recruiting_job_opening_query,
        returns_return_request_query=returns_return_request_query,
        reviews_product_review=reviews_product_review,
        search_search_index_query=search_search_index_query,
        search_search_index=search_search_index,
        search_search_index_validation=search_search_index_validation,
        seating_seat_map=seating_seat_map,
        shipping_shipment_query=shipping_shipment_query,
        travel_trip_query=travel_trip_query,
        venues_venue_query=venues_venue_query,
        venues_venue_validation=venues_venue_validation,
        registry={
            'acme.analytics.v1.AnalyticsEventQueryService': analytics_analytics_event_query,
            'acme.analytics.v1.AnalyticsEventService': analytics_analytics_event,
            'acme.analytics.v1.FunnelValidationService': analytics_funnel_validation,
            'acme.anomalies.v1.AnomalyFeedbackValidationService': anomalies_anomaly_feedback_validation,
            'acme.anomalies.v1.DetectorQueryService': anomalies_detector_query,
            'acme.appointments.v1.AppointmentService': appointments_appointment,
            'acme.assets.v1.FixedAssetService': assets_fixed_asset,
            'acme.audit.v1.AuditEventQueryService': audit_audit_event_query,
            'acme.audit.v1.AuditEventService': audit_audit_event,
            'acme.authorization.v1.AccessPolicyQueryService': authorization_access_policy_query,
            'acme.authorization.v1.AccessPolicyService': authorization_access_policy,
            'acme.authorization.v1.AccessPolicyValidationService': authorization_access_policy_validation,
            'acme.careplans.v1.CarePlanCalculationService': careplans_care_plan_calculation,
            'acme.catalog.v1.ProductQueryService': catalog_product_query,
            'acme.certificates.v1.CertificateCalculationService': certificates_certificate_calculation,
            'acme.checkout.v1.CheckoutSessionService': checkout_checkout_session,
            'acme.concessions.v1.ConcessionStandCalculationService': concessions_concession_stand_calculation,
            'acme.configuration.v1.ConfigSetCalculationService': configuration_config_set_calculation,
            'acme.configuration.v1.ConfigSetQueryService': configuration_config_set_query,
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
            'acme.datasets.v1.DatasetVersionValidationService': datasets_dataset_version_validation,
            'acme.deliveries.v1.DeliveryService': deliveries_delivery,
            'acme.dispatch.v1.DispatchOrderQueryService': dispatch_dispatch_order_query,
            'acme.documents.v1.DocumentQueryService': documents_document_query,
            'acme.documents.v1.DocumentValidationService': documents_document_validation,
            'acme.featureflags.v1.FeatureFlagQueryService': featureflags_feature_flag_query,
            'acme.featureflags.v1.FeatureFlagService': featureflags_feature_flag,
            'acme.featureflags.v1.FeatureFlagValidationService': featureflags_feature_flag_validation,
            'acme.featurestore.v1.FeatureValueCalculationService': featurestore_feature_value_calculation,
            'acme.featurestore.v1.FeatureViewService': featurestore_feature_view,
            'acme.featurestore.v1.FeatureViewValidationService': featurestore_feature_view_validation,
            'acme.fleet.v1.VehicleService': fleet_vehicle,
            'acme.forecasting.v1.DemandForecastValidationService': forecasting_demand_forecast_validation,
            'acme.forecasting.v1.ForecastModelQueryService': forecasting_forecast_model_query,
            'acme.forecasting.v1.ForecastModelValidationService': forecasting_forecast_model_validation,
            'acme.forecasting.v1.ScenarioCalculationService': forecasting_scenario_calculation,
            'acme.forecasting.v1.ScenarioValidationService': forecasting_scenario_validation,
            'acme.forms.v1.FormQueryService': forms_form_query,
            'acme.fulfillment.v1.FulfillmentQueryService': fulfillment_fulfillment_query,
            'acme.identity.v1.UserQueryService': identity_user_query,
            'acme.identity.v1.UserService': identity_user,
            'acme.keymanagement.v1.CryptoKeyQueryService': keymanagement_crypto_key_query,
            'acme.keymanagement.v1.CryptoKeyService': keymanagement_crypto_key,
            'acme.labeling.v1.AnnotationCalculationService': labeling_annotation_calculation,
            'acme.labeling.v1.LabelSetValidationService': labeling_label_set_validation,
            'acme.labeling.v1.LabelingTaskQueryService': labeling_labeling_task_query,
            'acme.labeling.v1.LabelingTaskService': labeling_labeling_task,
            'acme.labeling.v1.LabelingTaskValidationService': labeling_labeling_task_validation,
            'acme.ledger.v1.LedgerAccountService': ledger_ledger_account,
            'acme.ledger.v1.LedgerAccountValidationService': ledger_ledger_account_validation,
            'acme.lending.v1.LoanApplicationService': lending_loan_application,
            'acme.lineage.v1.ImpactCalculationService': lineage_impact_calculation,
            'acme.lineage.v1.ImpactImportService': lineage_impact_import,
            'acme.lineage.v1.ImpactLifecycleService': lineage_impact_lifecycle,
            'acme.lineage.v1.ImpactReportingService': lineage_impact_reporting,
            'acme.lineage.v1.ImpactSyncService': lineage_impact_sync,
            'acme.lineage.v1.ImpactValidationService': lineage_impact_validation,
            'acme.lineage.v1.LineageEdgeApprovalService': lineage_lineage_edge_approval,
            'acme.lineage.v1.LineageEdgeCalculationService': lineage_lineage_edge_calculation,
            'acme.lineage.v1.LineageEdgeImportService': lineage_lineage_edge_import,
            'acme.lineage.v1.LineageEdgeLifecycleService': lineage_lineage_edge_lifecycle,
            'acme.lineage.v1.LineageEdgeQueryService': lineage_lineage_edge_query,
            'acme.lineage.v1.LineageEdgeReportingService': lineage_lineage_edge_reporting,
            'acme.lineage.v1.LineageEdgeSyncService': lineage_lineage_edge_sync,
            'acme.lineage.v1.LineageEdgeValidationService': lineage_lineage_edge_validation,
            'acme.lineage.v1.LineageEdgeWorkflowService': lineage_lineage_edge_workflow,
            'acme.lineage.v1.LineageNodeApprovalService': lineage_lineage_node_approval,
            'acme.lineage.v1.LineageNodeCalculationService': lineage_lineage_node_calculation,
            'acme.lineage.v1.LineageNodeLifecycleService': lineage_lineage_node_lifecycle,
            'acme.lineage.v1.LineageNodeQueryService': lineage_lineage_node_query,
            'acme.lineage.v1.LineageNodeReportingService': lineage_lineage_node_reporting,
            'acme.lineage.v1.LineageNodeService': lineage_lineage_node,
            'acme.lineage.v1.LineageNodeSyncService': lineage_lineage_node_sync,
            'acme.lineage.v1.LineageNodeValidationService': lineage_lineage_node_validation,
            'acme.lineage.v1.LineageNodeWorkflowService': lineage_lineage_node_workflow,
            'acme.messaging.v1.ConversationCalculationService': messaging_conversation_calculation,
            'acme.metrics.v1.DashboardExportService': metrics_dashboard_export,
            'acme.metrics.v1.DashboardHistoryService': metrics_dashboard_history,
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
            'acme.metrics.v1.MetricSeriesQueryService': metrics_metric_series_query,
            'acme.metrics.v1.MetricSeriesService': metrics_metric_series,
            'acme.metrics.v1.MetricSeriesValidationService': metrics_metric_series_validation,
            'acme.modelregistry.v1.ModelVersionCalculationService': modelregistry_model_version_calculation,
            'acme.modelregistry.v1.RegisteredModelQueryService': modelregistry_registered_model_query,
            'acme.notifications.v1.NotificationQueryService': notifications_notification_query,
            'acme.notifications.v1.NotificationService': notifications_notification,
            'acme.notifications.v1.NotificationValidationService': notifications_notification_validation,
            'acme.performers.v1.PerformerQueryService': performers_performer_query,
            'acme.pipelines.v1.PipelineQueryService': pipelines_pipeline_query,
            'acme.pipelines.v1.PipelineRunCalculationService': pipelines_pipeline_run_calculation,
            'acme.pipelines.v1.PipelineRunValidationService': pipelines_pipeline_run_validation,
            'acme.pipelines.v1.PipelineService': pipelines_pipeline,
            'acme.pipelines.v1.PipelineStepCalculationService': pipelines_pipeline_step_calculation,
            'acme.pipelines.v1.PipelineValidationService': pipelines_pipeline_validation,
            'acme.prescriptions.v1.PrescriptionCalculationService': prescriptions_prescription_calculation,
            'acme.promotions.v1.PromotionQueryService': promotions_promotion_query,
            'acme.recommendations.v1.InteractionValidationService': recommendations_interaction_validation,
            'acme.recommendations.v1.RecommendationModelCalculationService': recommendations_recommendation_model_calculation,
            'acme.recommendations.v1.RecommendationModelValidationService': recommendations_recommendation_model_validation,
            'acme.recommendations.v1.RecommendationSetService': recommendations_recommendation_set,
            'acme.recruiting.v1.JobOpeningQueryService': recruiting_job_opening_query,
            'acme.returns.v1.ReturnRequestQueryService': returns_return_request_query,
            'acme.reviews.v1.ProductReviewService': reviews_product_review,
            'acme.search.v1.SearchIndexQueryService': search_search_index_query,
            'acme.search.v1.SearchIndexService': search_search_index,
            'acme.search.v1.SearchIndexValidationService': search_search_index_validation,
            'acme.seating.v1.SeatMapService': seating_seat_map,
            'acme.shipping.v1.ShipmentQueryService': shipping_shipment_query,
            'acme.travel.v1.TripQueryService': travel_trip_query,
            'acme.venues.v1.VenueQueryService': venues_venue_query,
            'acme.venues.v1.VenueValidationService': venues_venue_validation,
        },
    )
    return Dependencies(clients, DomainRepository(container.sessions),
                        container.settings, container.bus)


def register(server: grpc.aio.Server, container: Container) -> dict[str, object]:
    deps = dependencies(container)
    registered: dict[str, object] = {}
    impact_approval_servicer = Factory(lambda: ImpactApprovalServicer(deps))()
    lineage_v1_impact_approval_service_pb2_grpc.add_ImpactApprovalServiceServicer_to_server(
        impact_approval_servicer,
        server
    )
    registered['acme.lineage.v1.ImpactApprovalService'] = impact_approval_servicer
    impact_calculation_servicer = Factory(lambda: ImpactCalculationServicer(deps))()
    lineage_v1_impact_calculation_service_pb2_grpc.add_ImpactCalculationServiceServicer_to_server(
        impact_calculation_servicer,
        server
    )
    registered['acme.lineage.v1.ImpactCalculationService'] = impact_calculation_servicer
    impact_import_servicer = Factory(lambda: ImpactImportServicer(deps))()
    lineage_v1_impact_import_service_pb2_grpc.add_ImpactImportServiceServicer_to_server(impact_import_servicer, server)
    registered['acme.lineage.v1.ImpactImportService'] = impact_import_servicer
    impact_lifecycle_servicer = Factory(lambda: ImpactLifecycleServicer(deps))()
    lineage_v1_impact_lifecycle_service_pb2_grpc.add_ImpactLifecycleServiceServicer_to_server(
        impact_lifecycle_servicer,
        server
    )
    registered['acme.lineage.v1.ImpactLifecycleService'] = impact_lifecycle_servicer
    impact_reporting_servicer = Factory(lambda: ImpactReportingServicer(deps))()
    lineage_v1_impact_reporting_service_pb2_grpc.add_ImpactReportingServiceServicer_to_server(
        impact_reporting_servicer,
        server
    )
    registered['acme.lineage.v1.ImpactReportingService'] = impact_reporting_servicer
    impact_sync_servicer = Factory(lambda: ImpactSyncServicer(deps))()
    lineage_v1_impact_sync_service_pb2_grpc.add_ImpactSyncServiceServicer_to_server(impact_sync_servicer, server)
    registered['acme.lineage.v1.ImpactSyncService'] = impact_sync_servicer
    impact_validation_servicer = Factory(lambda: ImpactValidationServicer(deps))()
    lineage_v1_impact_validation_service_pb2_grpc.add_ImpactValidationServiceServicer_to_server(
        impact_validation_servicer,
        server
    )
    registered['acme.lineage.v1.ImpactValidationService'] = impact_validation_servicer
    impact_workflow_servicer = Factory(lambda: ImpactWorkflowServicer(deps))()
    lineage_v1_impact_workflow_service_pb2_grpc.add_ImpactWorkflowServiceServicer_to_server(
        impact_workflow_servicer,
        server
    )
    registered['acme.lineage.v1.ImpactWorkflowService'] = impact_workflow_servicer
    lineage_edge_approval_servicer = Factory(lambda: LineageEdgeApprovalServicer(deps))()
    lineage_v1_lineage_edge_approval_service_pb2_grpc.add_LineageEdgeApprovalServiceServicer_to_server(
        lineage_edge_approval_servicer,
        server
    )
    registered['acme.lineage.v1.LineageEdgeApprovalService'] = lineage_edge_approval_servicer
    lineage_edge_calculation_servicer = Factory(lambda: LineageEdgeCalculationServicer(deps))()
    lineage_v1_lineage_edge_calculation_service_pb2_grpc.add_LineageEdgeCalculationServiceServicer_to_server(
        lineage_edge_calculation_servicer,
        server
    )
    registered['acme.lineage.v1.LineageEdgeCalculationService'] = lineage_edge_calculation_servicer
    lineage_edge_import_servicer = Factory(lambda: LineageEdgeImportServicer(deps))()
    lineage_v1_lineage_edge_import_service_pb2_grpc.add_LineageEdgeImportServiceServicer_to_server(
        lineage_edge_import_servicer,
        server
    )
    registered['acme.lineage.v1.LineageEdgeImportService'] = lineage_edge_import_servicer
    lineage_edge_lifecycle_servicer = Factory(lambda: LineageEdgeLifecycleServicer(deps))()
    lineage_v1_lineage_edge_lifecycle_service_pb2_grpc.add_LineageEdgeLifecycleServiceServicer_to_server(
        lineage_edge_lifecycle_servicer,
        server
    )
    registered['acme.lineage.v1.LineageEdgeLifecycleService'] = lineage_edge_lifecycle_servicer
    lineage_edge_query_servicer = Factory(lambda: LineageEdgeQueryServicer(deps))()
    lineage_v1_lineage_edge_query_service_pb2_grpc.add_LineageEdgeQueryServiceServicer_to_server(
        lineage_edge_query_servicer,
        server
    )
    registered['acme.lineage.v1.LineageEdgeQueryService'] = lineage_edge_query_servicer
    lineage_edge_reporting_servicer = Factory(lambda: LineageEdgeReportingServicer(deps))()
    lineage_v1_lineage_edge_reporting_service_pb2_grpc.add_LineageEdgeReportingServiceServicer_to_server(
        lineage_edge_reporting_servicer,
        server
    )
    registered['acme.lineage.v1.LineageEdgeReportingService'] = lineage_edge_reporting_servicer
    lineage_edge_sync_servicer = Factory(lambda: LineageEdgeSyncServicer(deps))()
    lineage_v1_lineage_edge_sync_service_pb2_grpc.add_LineageEdgeSyncServiceServicer_to_server(
        lineage_edge_sync_servicer,
        server
    )
    registered['acme.lineage.v1.LineageEdgeSyncService'] = lineage_edge_sync_servicer
    lineage_edge_validation_servicer = Factory(lambda: LineageEdgeValidationServicer(deps))()
    lineage_v1_lineage_edge_validation_service_pb2_grpc.add_LineageEdgeValidationServiceServicer_to_server(
        lineage_edge_validation_servicer,
        server
    )
    registered['acme.lineage.v1.LineageEdgeValidationService'] = lineage_edge_validation_servicer
    lineage_edge_workflow_servicer = Factory(lambda: LineageEdgeWorkflowServicer(deps))()
    lineage_v1_lineage_edge_workflow_service_pb2_grpc.add_LineageEdgeWorkflowServiceServicer_to_server(
        lineage_edge_workflow_servicer,
        server
    )
    registered['acme.lineage.v1.LineageEdgeWorkflowService'] = lineage_edge_workflow_servicer
    lineage_node_approval_servicer = Factory(lambda: LineageNodeApprovalServicer(deps))()
    lineage_v1_lineage_node_approval_service_pb2_grpc.add_LineageNodeApprovalServiceServicer_to_server(
        lineage_node_approval_servicer,
        server
    )
    registered['acme.lineage.v1.LineageNodeApprovalService'] = lineage_node_approval_servicer
    lineage_node_calculation_servicer = Factory(lambda: LineageNodeCalculationServicer(deps))()
    lineage_v1_lineage_node_calculation_service_pb2_grpc.add_LineageNodeCalculationServiceServicer_to_server(
        lineage_node_calculation_servicer,
        server
    )
    registered['acme.lineage.v1.LineageNodeCalculationService'] = lineage_node_calculation_servicer
    lineage_node_lifecycle_servicer = Factory(lambda: LineageNodeLifecycleServicer(deps))()
    lineage_v1_lineage_node_lifecycle_service_pb2_grpc.add_LineageNodeLifecycleServiceServicer_to_server(
        lineage_node_lifecycle_servicer,
        server
    )
    registered['acme.lineage.v1.LineageNodeLifecycleService'] = lineage_node_lifecycle_servicer
    lineage_node_query_servicer = Factory(lambda: LineageNodeQueryServicer(deps))()
    lineage_v1_lineage_node_query_service_pb2_grpc.add_LineageNodeQueryServiceServicer_to_server(
        lineage_node_query_servicer,
        server
    )
    registered['acme.lineage.v1.LineageNodeQueryService'] = lineage_node_query_servicer
    lineage_node_reporting_servicer = Factory(lambda: LineageNodeReportingServicer(deps))()
    lineage_v1_lineage_node_reporting_service_pb2_grpc.add_LineageNodeReportingServiceServicer_to_server(
        lineage_node_reporting_servicer,
        server
    )
    registered['acme.lineage.v1.LineageNodeReportingService'] = lineage_node_reporting_servicer
    lineage_node_servicer = Factory(lambda: LineageNodeServicer(deps))()
    lineage_v1_lineage_node_service_pb2_grpc.add_LineageNodeServiceServicer_to_server(lineage_node_servicer, server)
    registered['acme.lineage.v1.LineageNodeService'] = lineage_node_servicer
    lineage_node_sync_servicer = Factory(lambda: LineageNodeSyncServicer(deps))()
    lineage_v1_lineage_node_sync_service_pb2_grpc.add_LineageNodeSyncServiceServicer_to_server(
        lineage_node_sync_servicer,
        server
    )
    registered['acme.lineage.v1.LineageNodeSyncService'] = lineage_node_sync_servicer
    lineage_node_validation_servicer = Factory(lambda: LineageNodeValidationServicer(deps))()
    lineage_v1_lineage_node_validation_service_pb2_grpc.add_LineageNodeValidationServiceServicer_to_server(
        lineage_node_validation_servicer,
        server
    )
    registered['acme.lineage.v1.LineageNodeValidationService'] = lineage_node_validation_servicer
    lineage_node_workflow_servicer = Factory(lambda: LineageNodeWorkflowServicer(deps))()
    lineage_v1_lineage_node_workflow_service_pb2_grpc.add_LineageNodeWorkflowServiceServicer_to_server(
        lineage_node_workflow_servicer,
        server
    )
    registered['acme.lineage.v1.LineageNodeWorkflowService'] = lineage_node_workflow_servicer
    subscribe(deps)
    return registered
