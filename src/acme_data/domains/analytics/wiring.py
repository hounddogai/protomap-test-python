"""Register and compose every service of the analytics domain."""

from __future__ import annotations

import grpc

from acme.admissions.v1 import (
    admission_calculation_service_pb2_grpc as admissions_v1_admission_calculation_service_pb2_grpc,
)
from acme.analytics.v1 import (
    analytics_event_approval_service_pb2_grpc as analytics_v1_analytics_event_approval_service_pb2_grpc,
)
from acme.analytics.v1 import (
    analytics_event_query_service_pb2_grpc as analytics_v1_analytics_event_query_service_pb2_grpc,
)
from acme.analytics.v1 import analytics_event_service_pb2_grpc as analytics_v1_analytics_event_service_pb2_grpc
from acme.analytics.v1 import (
    analytics_event_validation_service_pb2_grpc as analytics_v1_analytics_event_validation_service_pb2_grpc,
)
from acme.analytics.v1 import (
    analytics_event_workflow_service_pb2_grpc as analytics_v1_analytics_event_workflow_service_pb2_grpc,
)
from acme.analytics.v1 import (
    analytics_report_approval_service_pb2_grpc as analytics_v1_analytics_report_approval_service_pb2_grpc,
)
from acme.analytics.v1 import (
    analytics_report_calculation_service_pb2_grpc as analytics_v1_analytics_report_calculation_service_pb2_grpc,
)
from acme.analytics.v1 import (
    analytics_report_lifecycle_service_pb2_grpc as analytics_v1_analytics_report_lifecycle_service_pb2_grpc,
)
from acme.analytics.v1 import (
    analytics_report_validation_service_pb2_grpc as analytics_v1_analytics_report_validation_service_pb2_grpc,
)
from acme.analytics.v1 import cohort_approval_service_pb2_grpc as analytics_v1_cohort_approval_service_pb2_grpc
from acme.analytics.v1 import cohort_calculation_service_pb2_grpc as analytics_v1_cohort_calculation_service_pb2_grpc
from acme.analytics.v1 import cohort_lifecycle_service_pb2_grpc as analytics_v1_cohort_lifecycle_service_pb2_grpc
from acme.analytics.v1 import cohort_validation_service_pb2_grpc as analytics_v1_cohort_validation_service_pb2_grpc
from acme.analytics.v1 import cohort_workflow_service_pb2_grpc as analytics_v1_cohort_workflow_service_pb2_grpc
from acme.analytics.v1 import funnel_approval_service_pb2_grpc as analytics_v1_funnel_approval_service_pb2_grpc
from acme.analytics.v1 import funnel_calculation_service_pb2_grpc as analytics_v1_funnel_calculation_service_pb2_grpc
from acme.analytics.v1 import funnel_query_service_pb2_grpc as analytics_v1_funnel_query_service_pb2_grpc
from acme.analytics.v1 import funnel_validation_service_pb2_grpc as analytics_v1_funnel_validation_service_pb2_grpc
from acme.analytics.v1 import funnel_workflow_service_pb2_grpc as analytics_v1_funnel_workflow_service_pb2_grpc
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
from acme.anomalies.v1 import anomaly_validation_service_pb2_grpc as anomalies_v1_anomaly_validation_service_pb2_grpc
from acme.anomalies.v1 import detector_query_service_pb2_grpc as anomalies_v1_detector_query_service_pb2_grpc
from acme.anomalies.v1 import detector_validation_service_pb2_grpc as anomalies_v1_detector_validation_service_pb2_grpc
from acme.appointments.v1 import (
    appointment_query_service_pb2_grpc as appointments_v1_appointment_query_service_pb2_grpc,
)
from acme.appointments.v1 import appointment_service_pb2_grpc as appointments_v1_appointment_service_pb2_grpc
from acme.audit.v1 import audit_event_query_service_pb2_grpc as audit_v1_audit_event_query_service_pb2_grpc
from acme.audit.v1 import audit_event_service_pb2_grpc as audit_v1_audit_event_service_pb2_grpc
from acme.audit.v1 import audit_event_validation_service_pb2_grpc as audit_v1_audit_event_validation_service_pb2_grpc
from acme.authorization.v1 import (
    access_policy_query_service_pb2_grpc as authorization_v1_access_policy_query_service_pb2_grpc,
)
from acme.authorization.v1 import access_policy_service_pb2_grpc as authorization_v1_access_policy_service_pb2_grpc
from acme.billing.v1 import billing_account_query_service_pb2_grpc as billing_v1_billing_account_query_service_pb2_grpc
from acme.checkout.v1 import (
    checkout_session_query_service_pb2_grpc as checkout_v1_checkout_session_query_service_pb2_grpc,
)
from acme.concessions.v1 import (
    concession_stand_query_service_pb2_grpc as concessions_v1_concession_stand_query_service_pb2_grpc,
)
from acme.configuration.v1 import (
    config_set_calculation_service_pb2_grpc as configuration_v1_config_set_calculation_service_pb2_grpc,
)
from acme.configuration.v1 import config_set_service_pb2_grpc as configuration_v1_config_set_service_pb2_grpc
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
    data_schema_calculation_service_pb2_grpc as datasets_v1_data_schema_calculation_service_pb2_grpc,
)
from acme.datasets.v1 import dataset_approval_service_pb2_grpc as datasets_v1_dataset_approval_service_pb2_grpc
from acme.datasets.v1 import (
    dataset_version_workflow_service_pb2_grpc as datasets_v1_dataset_version_workflow_service_pb2_grpc,
)
from acme.deliveries.v1 import delivery_query_service_pb2_grpc as deliveries_v1_delivery_query_service_pb2_grpc
from acme.documents.v1 import document_query_service_pb2_grpc as documents_v1_document_query_service_pb2_grpc
from acme.featureflags.v1 import feature_flag_service_pb2_grpc as featureflags_v1_feature_flag_service_pb2_grpc
from acme.featureflags.v1 import (
    feature_flag_validation_service_pb2_grpc as featureflags_v1_feature_flag_validation_service_pb2_grpc,
)
from acme.featurestore.v1 import entity_reporting_service_pb2_grpc as featurestore_v1_entity_reporting_service_pb2_grpc
from acme.featurestore.v1 import (
    feature_value_query_service_pb2_grpc as featurestore_v1_feature_value_query_service_pb2_grpc,
)
from acme.featurestore.v1 import (
    feature_view_lifecycle_service_pb2_grpc as featurestore_v1_feature_view_lifecycle_service_pb2_grpc,
)
from acme.featurestore.v1 import (
    feature_view_validation_service_pb2_grpc as featurestore_v1_feature_view_validation_service_pb2_grpc,
)
from acme.featurestore.v1 import (
    feature_view_workflow_service_pb2_grpc as featurestore_v1_feature_view_workflow_service_pb2_grpc,
)
from acme.forecasting.v1 import (
    forecast_model_approval_service_pb2_grpc as forecasting_v1_forecast_model_approval_service_pb2_grpc,
)
from acme.forecasting.v1 import (
    forecast_model_query_service_pb2_grpc as forecasting_v1_forecast_model_query_service_pb2_grpc,
)
from acme.forecasting.v1 import (
    forecast_model_workflow_service_pb2_grpc as forecasting_v1_forecast_model_workflow_service_pb2_grpc,
)
from acme.forecasting.v1 import (
    scenario_calculation_service_pb2_grpc as forecasting_v1_scenario_calculation_service_pb2_grpc,
)
from acme.forecasting.v1 import (
    scenario_validation_service_pb2_grpc as forecasting_v1_scenario_validation_service_pb2_grpc,
)
from acme.identity.v1 import user_query_service_pb2_grpc as identity_v1_user_query_service_pb2_grpc
from acme.identity.v1 import user_validation_service_pb2_grpc as identity_v1_user_validation_service_pb2_grpc
from acme.labeling.v1 import annotation_query_service_pb2_grpc as labeling_v1_annotation_query_service_pb2_grpc
from acme.labeling.v1 import annotation_reporting_service_pb2_grpc as labeling_v1_annotation_reporting_service_pb2_grpc
from acme.labeling.v1 import (
    annotation_validation_service_pb2_grpc as labeling_v1_annotation_validation_service_pb2_grpc,
)
from acme.labeling.v1 import label_set_approval_service_pb2_grpc as labeling_v1_label_set_approval_service_pb2_grpc
from acme.labeling.v1 import (
    label_set_calculation_service_pb2_grpc as labeling_v1_label_set_calculation_service_pb2_grpc,
)
from acme.ledger.v1 import ledger_account_query_service_pb2_grpc as ledger_v1_ledger_account_query_service_pb2_grpc
from acme.ledger.v1 import ledger_account_service_pb2_grpc as ledger_v1_ledger_account_service_pb2_grpc
from acme.ledger.v1 import (
    ledger_account_validation_service_pb2_grpc as ledger_v1_ledger_account_validation_service_pb2_grpc,
)
from acme.lineage.v1 import impact_lifecycle_service_pb2_grpc as lineage_v1_impact_lifecycle_service_pb2_grpc
from acme.lineage.v1 import impact_reporting_service_pb2_grpc as lineage_v1_impact_reporting_service_pb2_grpc
from acme.lineage.v1 import impact_sync_service_pb2_grpc as lineage_v1_impact_sync_service_pb2_grpc
from acme.lineage.v1 import impact_workflow_service_pb2_grpc as lineage_v1_impact_workflow_service_pb2_grpc
from acme.lineage.v1 import (
    lineage_edge_lifecycle_service_pb2_grpc as lineage_v1_lineage_edge_lifecycle_service_pb2_grpc,
)
from acme.lineage.v1 import lineage_edge_workflow_service_pb2_grpc as lineage_v1_lineage_edge_workflow_service_pb2_grpc
from acme.lineage.v1 import lineage_node_approval_service_pb2_grpc as lineage_v1_lineage_node_approval_service_pb2_grpc
from acme.lineage.v1 import lineage_node_workflow_service_pb2_grpc as lineage_v1_lineage_node_workflow_service_pb2_grpc
from acme.maintenance.v1 import (
    work_order_calculation_service_pb2_grpc as maintenance_v1_work_order_calculation_service_pb2_grpc,
)
from acme.metrics.v1 import dashboard_history_service_pb2_grpc as metrics_v1_dashboard_history_service_pb2_grpc
from acme.metrics.v1 import dashboard_sync_service_pb2_grpc as metrics_v1_dashboard_sync_service_pb2_grpc
from acme.metrics.v1 import dashboard_validation_service_pb2_grpc as metrics_v1_dashboard_validation_service_pb2_grpc
from acme.metrics.v1 import (
    metric_alert_notification_service_pb2_grpc as metrics_v1_metric_alert_notification_service_pb2_grpc,
)
from acme.metrics.v1 import metric_alert_query_service_pb2_grpc as metrics_v1_metric_alert_query_service_pb2_grpc
from acme.metrics.v1 import (
    metric_alert_validation_service_pb2_grpc as metrics_v1_metric_alert_validation_service_pb2_grpc,
)
from acme.metrics.v1 import metric_series_export_service_pb2_grpc as metrics_v1_metric_series_export_service_pb2_grpc
from acme.metrics.v1 import (
    metric_series_notification_service_pb2_grpc as metrics_v1_metric_series_notification_service_pb2_grpc,
)
from acme.metrics.v1 import metric_series_query_service_pb2_grpc as metrics_v1_metric_series_query_service_pb2_grpc
from acme.metrics.v1 import metric_series_service_pb2_grpc as metrics_v1_metric_series_service_pb2_grpc
from acme.metrics.v1 import (
    metric_series_validation_service_pb2_grpc as metrics_v1_metric_series_validation_service_pb2_grpc,
)
from acme.modelregistry.v1 import (
    model_version_sync_service_pb2_grpc as modelregistry_v1_model_version_sync_service_pb2_grpc,
)
from acme.modelregistry.v1 import (
    registered_model_calculation_service_pb2_grpc as modelregistry_v1_registered_model_calculation_service_pb2_grpc,
)
from acme.modelregistry.v1 import (
    registered_model_reporting_service_pb2_grpc as modelregistry_v1_registered_model_reporting_service_pb2_grpc,
)
from acme.modelregistry.v1 import (
    registered_model_service_pb2_grpc as modelregistry_v1_registered_model_service_pb2_grpc,
)
from acme.modelregistry.v1 import (
    registered_model_workflow_service_pb2_grpc as modelregistry_v1_registered_model_workflow_service_pb2_grpc,
)
from acme.notifications.v1 import (
    notification_query_service_pb2_grpc as notifications_v1_notification_query_service_pb2_grpc,
)
from acme.notifications.v1 import (
    notification_validation_service_pb2_grpc as notifications_v1_notification_validation_service_pb2_grpc,
)
from acme.onboarding.v1 import (
    onboarding_plan_calculation_service_pb2_grpc as onboarding_v1_onboarding_plan_calculation_service_pb2_grpc,
)
from acme.patients.v1 import patient_calculation_service_pb2_grpc as patients_v1_patient_calculation_service_pb2_grpc
from acme.performers.v1 import performer_query_service_pb2_grpc as performers_v1_performer_query_service_pb2_grpc
from acme.pipelines.v1 import pipeline_reporting_service_pb2_grpc as pipelines_v1_pipeline_reporting_service_pb2_grpc
from acme.pipelines.v1 import pipeline_run_query_service_pb2_grpc as pipelines_v1_pipeline_run_query_service_pb2_grpc
from acme.pipelines.v1 import pipeline_run_sync_service_pb2_grpc as pipelines_v1_pipeline_run_sync_service_pb2_grpc
from acme.pipelines.v1 import (
    pipeline_run_validation_service_pb2_grpc as pipelines_v1_pipeline_run_validation_service_pb2_grpc,
)
from acme.pipelines.v1 import (
    pipeline_run_workflow_service_pb2_grpc as pipelines_v1_pipeline_run_workflow_service_pb2_grpc,
)
from acme.pipelines.v1 import (
    pipeline_step_approval_service_pb2_grpc as pipelines_v1_pipeline_step_approval_service_pb2_grpc,
)
from acme.pipelines.v1 import pipeline_sync_service_pb2_grpc as pipelines_v1_pipeline_sync_service_pb2_grpc
from acme.prescriptions.v1 import prescription_service_pb2_grpc as prescriptions_v1_prescription_service_pb2_grpc
from acme.ratelimiting.v1 import rate_limit_query_service_pb2_grpc as ratelimiting_v1_rate_limit_query_service_pb2_grpc
from acme.ratelimiting.v1 import rate_limit_service_pb2_grpc as ratelimiting_v1_rate_limit_service_pb2_grpc
from acme.recommendations.v1 import (
    interaction_calculation_service_pb2_grpc as recommendations_v1_interaction_calculation_service_pb2_grpc,
)
from acme.recommendations.v1 import (
    recommendation_model_calculation_service_pb2_grpc as recommendations_v1_recommendation_model_calculation_service_pb2_grpc,
)
from acme.risk.v1 import risk_register_query_service_pb2_grpc as risk_v1_risk_register_query_service_pb2_grpc
from acme.search.v1 import search_index_query_service_pb2_grpc as search_v1_search_index_query_service_pb2_grpc
from acme.secrets.v1 import secret_query_service_pb2_grpc as secrets_v1_secret_query_service_pb2_grpc
from acme.ticketing.v1 import ticket_query_service_pb2_grpc as ticketing_v1_ticket_query_service_pb2_grpc
from acme.travel.v1 import trip_calculation_service_pb2_grpc as travel_v1_trip_calculation_service_pb2_grpc
from acme.treasury.v1 import cash_position_service_pb2_grpc as treasury_v1_cash_position_service_pb2_grpc
from acme.venues.v1 import venue_service_pb2_grpc as venues_v1_venue_service_pb2_grpc
from acme.venues.v1 import venue_validation_service_pb2_grpc as venues_v1_venue_validation_service_pb2_grpc
from acme.yards.v1 import yard_calculation_service_pb2_grpc as yards_v1_yard_calculation_service_pb2_grpc
from acme.yards.v1 import yard_query_service_pb2_grpc as yards_v1_yard_query_service_pb2_grpc

from acme_data.domains.analytics.analytics_event_approval_service import AnalyticsEventApprovalServicer
from acme_data.domains.analytics.analytics_event_query_service import AnalyticsEventQueryServicer
from acme_data.domains.analytics.analytics_event_service import AnalyticsEventServicer
from acme_data.domains.analytics.analytics_event_validation_service import AnalyticsEventValidationServicer
from acme_data.domains.analytics.analytics_event_workflow_service import AnalyticsEventWorkflowServicer
from acme_data.domains.analytics.analytics_report_approval_service import AnalyticsReportApprovalServicer
from acme_data.domains.analytics.analytics_report_calculation_service import AnalyticsReportCalculationServicer
from acme_data.domains.analytics.analytics_report_lifecycle_service import AnalyticsReportLifecycleServicer
from acme_data.domains.analytics.analytics_report_validation_service import AnalyticsReportValidationServicer
from acme_data.domains.analytics.cohort_approval_service import CohortApprovalServicer
from acme_data.domains.analytics.cohort_calculation_service import CohortCalculationServicer
from acme_data.domains.analytics.cohort_lifecycle_service import CohortLifecycleServicer
from acme_data.domains.analytics.cohort_validation_service import CohortValidationServicer
from acme_data.domains.analytics.cohort_workflow_service import CohortWorkflowServicer
from acme_data.domains.analytics.dependencies import Clients
from acme_data.domains.analytics.dependencies import Dependencies
from acme_data.domains.analytics.events import subscribe
from acme_data.domains.analytics.funnel_approval_service import FunnelApprovalServicer
from acme_data.domains.analytics.funnel_calculation_service import FunnelCalculationServicer
from acme_data.domains.analytics.funnel_query_service import FunnelQueryServicer
from acme_data.domains.analytics.funnel_validation_service import FunnelValidationServicer
from acme_data.domains.analytics.funnel_workflow_service import FunnelWorkflowServicer
from acme_data.domains.analytics.repository import DomainRepository
from acme_data.platform.container import Container
from acme_data.platform.container import Factory


def dependencies(container: Container) -> Dependencies:
    admissions_admission_calculation = container.singleton(
        admissions_v1_admission_calculation_service_pb2_grpc.AdmissionCalculationServiceStub,
        lambda: admissions_v1_admission_calculation_service_pb2_grpc.AdmissionCalculationServiceStub(container.channel)
    )
    analytics_analytics_event_approval = container.singleton(
        analytics_v1_analytics_event_approval_service_pb2_grpc.AnalyticsEventApprovalServiceStub,
        lambda: analytics_v1_analytics_event_approval_service_pb2_grpc.AnalyticsEventApprovalServiceStub(
            container.channel
        )
    )
    analytics_analytics_event_query = container.singleton(
        analytics_v1_analytics_event_query_service_pb2_grpc.AnalyticsEventQueryServiceStub,
        lambda: analytics_v1_analytics_event_query_service_pb2_grpc.AnalyticsEventQueryServiceStub(container.channel)
    )
    analytics_analytics_event_validation = container.singleton(
        analytics_v1_analytics_event_validation_service_pb2_grpc.AnalyticsEventValidationServiceStub,
        lambda: analytics_v1_analytics_event_validation_service_pb2_grpc.AnalyticsEventValidationServiceStub(
            container.channel
        )
    )
    analytics_analytics_event_workflow = container.singleton(
        analytics_v1_analytics_event_workflow_service_pb2_grpc.AnalyticsEventWorkflowServiceStub,
        lambda: analytics_v1_analytics_event_workflow_service_pb2_grpc.AnalyticsEventWorkflowServiceStub(
            container.channel
        )
    )
    analytics_analytics_report_approval = container.singleton(
        analytics_v1_analytics_report_approval_service_pb2_grpc.AnalyticsReportApprovalServiceStub,
        lambda: analytics_v1_analytics_report_approval_service_pb2_grpc.AnalyticsReportApprovalServiceStub(
            container.channel
        )
    )
    analytics_analytics_report_calculation = container.singleton(
        analytics_v1_analytics_report_calculation_service_pb2_grpc.AnalyticsReportCalculationServiceStub,
        lambda: analytics_v1_analytics_report_calculation_service_pb2_grpc.AnalyticsReportCalculationServiceStub(
            container.channel
        )
    )
    analytics_analytics_report_lifecycle = container.singleton(
        analytics_v1_analytics_report_lifecycle_service_pb2_grpc.AnalyticsReportLifecycleServiceStub,
        lambda: analytics_v1_analytics_report_lifecycle_service_pb2_grpc.AnalyticsReportLifecycleServiceStub(
            container.channel
        )
    )
    analytics_analytics_report_validation = container.singleton(
        analytics_v1_analytics_report_validation_service_pb2_grpc.AnalyticsReportValidationServiceStub,
        lambda: analytics_v1_analytics_report_validation_service_pb2_grpc.AnalyticsReportValidationServiceStub(
            container.channel
        )
    )
    analytics_cohort_calculation = container.singleton(
        analytics_v1_cohort_calculation_service_pb2_grpc.CohortCalculationServiceStub,
        lambda: analytics_v1_cohort_calculation_service_pb2_grpc.CohortCalculationServiceStub(container.channel)
    )
    analytics_cohort_lifecycle = container.singleton(
        analytics_v1_cohort_lifecycle_service_pb2_grpc.CohortLifecycleServiceStub,
        lambda: analytics_v1_cohort_lifecycle_service_pb2_grpc.CohortLifecycleServiceStub(container.channel)
    )
    analytics_cohort_validation = container.singleton(
        analytics_v1_cohort_validation_service_pb2_grpc.CohortValidationServiceStub,
        lambda: analytics_v1_cohort_validation_service_pb2_grpc.CohortValidationServiceStub(container.channel)
    )
    analytics_funnel_approval = container.singleton(
        analytics_v1_funnel_approval_service_pb2_grpc.FunnelApprovalServiceStub,
        lambda: analytics_v1_funnel_approval_service_pb2_grpc.FunnelApprovalServiceStub(container.channel)
    )
    analytics_funnel_calculation = container.singleton(
        analytics_v1_funnel_calculation_service_pb2_grpc.FunnelCalculationServiceStub,
        lambda: analytics_v1_funnel_calculation_service_pb2_grpc.FunnelCalculationServiceStub(container.channel)
    )
    analytics_funnel_query = container.singleton(
        analytics_v1_funnel_query_service_pb2_grpc.FunnelQueryServiceStub,
        lambda: analytics_v1_funnel_query_service_pb2_grpc.FunnelQueryServiceStub(container.channel)
    )
    analytics_funnel_validation = container.singleton(
        analytics_v1_funnel_validation_service_pb2_grpc.FunnelValidationServiceStub,
        lambda: analytics_v1_funnel_validation_service_pb2_grpc.FunnelValidationServiceStub(container.channel)
    )
    analytics_funnel_workflow = container.singleton(
        analytics_v1_funnel_workflow_service_pb2_grpc.FunnelWorkflowServiceStub,
        lambda: analytics_v1_funnel_workflow_service_pb2_grpc.FunnelWorkflowServiceStub(container.channel)
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
    anomalies_anomaly_validation = container.singleton(
        anomalies_v1_anomaly_validation_service_pb2_grpc.AnomalyValidationServiceStub,
        lambda: anomalies_v1_anomaly_validation_service_pb2_grpc.AnomalyValidationServiceStub(container.channel)
    )
    anomalies_detector_query = container.singleton(
        anomalies_v1_detector_query_service_pb2_grpc.DetectorQueryServiceStub,
        lambda: anomalies_v1_detector_query_service_pb2_grpc.DetectorQueryServiceStub(container.channel)
    )
    anomalies_detector_validation = container.singleton(
        anomalies_v1_detector_validation_service_pb2_grpc.DetectorValidationServiceStub,
        lambda: anomalies_v1_detector_validation_service_pb2_grpc.DetectorValidationServiceStub(container.channel)
    )
    appointments_appointment_query = container.singleton(
        appointments_v1_appointment_query_service_pb2_grpc.AppointmentQueryServiceStub,
        lambda: appointments_v1_appointment_query_service_pb2_grpc.AppointmentQueryServiceStub(container.channel)
    )
    appointments_appointment = container.singleton(
        appointments_v1_appointment_service_pb2_grpc.AppointmentServiceStub,
        lambda: appointments_v1_appointment_service_pb2_grpc.AppointmentServiceStub(container.channel)
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
    billing_billing_account_query = container.singleton(
        billing_v1_billing_account_query_service_pb2_grpc.BillingAccountQueryServiceStub,
        lambda: billing_v1_billing_account_query_service_pb2_grpc.BillingAccountQueryServiceStub(container.channel)
    )
    checkout_checkout_session_query = container.singleton(
        checkout_v1_checkout_session_query_service_pb2_grpc.CheckoutSessionQueryServiceStub,
        lambda: checkout_v1_checkout_session_query_service_pb2_grpc.CheckoutSessionQueryServiceStub(container.channel)
    )
    concessions_concession_stand_query = container.singleton(
        concessions_v1_concession_stand_query_service_pb2_grpc.ConcessionStandQueryServiceStub,
        lambda: concessions_v1_concession_stand_query_service_pb2_grpc.ConcessionStandQueryServiceStub(
            container.channel
        )
    )
    configuration_config_set_calculation = container.singleton(
        configuration_v1_config_set_calculation_service_pb2_grpc.ConfigSetCalculationServiceStub,
        lambda: configuration_v1_config_set_calculation_service_pb2_grpc.ConfigSetCalculationServiceStub(
            container.channel
        )
    )
    configuration_config_set = container.singleton(
        configuration_v1_config_set_service_pb2_grpc.ConfigSetServiceStub,
        lambda: configuration_v1_config_set_service_pb2_grpc.ConfigSetServiceStub(container.channel)
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
    datasets_data_schema_calculation = container.singleton(
        datasets_v1_data_schema_calculation_service_pb2_grpc.DataSchemaCalculationServiceStub,
        lambda: datasets_v1_data_schema_calculation_service_pb2_grpc.DataSchemaCalculationServiceStub(container.channel)
    )
    datasets_dataset_approval = container.singleton(
        datasets_v1_dataset_approval_service_pb2_grpc.DatasetApprovalServiceStub,
        lambda: datasets_v1_dataset_approval_service_pb2_grpc.DatasetApprovalServiceStub(container.channel)
    )
    datasets_dataset_version_workflow = container.singleton(
        datasets_v1_dataset_version_workflow_service_pb2_grpc.DatasetVersionWorkflowServiceStub,
        lambda: datasets_v1_dataset_version_workflow_service_pb2_grpc.DatasetVersionWorkflowServiceStub(
            container.channel
        )
    )
    deliveries_delivery_query = container.singleton(
        deliveries_v1_delivery_query_service_pb2_grpc.DeliveryQueryServiceStub,
        lambda: deliveries_v1_delivery_query_service_pb2_grpc.DeliveryQueryServiceStub(container.channel)
    )
    documents_document_query = container.singleton(
        documents_v1_document_query_service_pb2_grpc.DocumentQueryServiceStub,
        lambda: documents_v1_document_query_service_pb2_grpc.DocumentQueryServiceStub(container.channel)
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
    featurestore_entity_reporting = container.singleton(
        featurestore_v1_entity_reporting_service_pb2_grpc.EntityReportingServiceStub,
        lambda: featurestore_v1_entity_reporting_service_pb2_grpc.EntityReportingServiceStub(container.channel)
    )
    featurestore_feature_value_query = container.singleton(
        featurestore_v1_feature_value_query_service_pb2_grpc.FeatureValueQueryServiceStub,
        lambda: featurestore_v1_feature_value_query_service_pb2_grpc.FeatureValueQueryServiceStub(container.channel)
    )
    featurestore_feature_view_lifecycle = container.singleton(
        featurestore_v1_feature_view_lifecycle_service_pb2_grpc.FeatureViewLifecycleServiceStub,
        lambda: featurestore_v1_feature_view_lifecycle_service_pb2_grpc.FeatureViewLifecycleServiceStub(
            container.channel
        )
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
    forecasting_forecast_model_approval = container.singleton(
        forecasting_v1_forecast_model_approval_service_pb2_grpc.ForecastModelApprovalServiceStub,
        lambda: forecasting_v1_forecast_model_approval_service_pb2_grpc.ForecastModelApprovalServiceStub(
            container.channel
        )
    )
    forecasting_forecast_model_query = container.singleton(
        forecasting_v1_forecast_model_query_service_pb2_grpc.ForecastModelQueryServiceStub,
        lambda: forecasting_v1_forecast_model_query_service_pb2_grpc.ForecastModelQueryServiceStub(container.channel)
    )
    forecasting_forecast_model_workflow = container.singleton(
        forecasting_v1_forecast_model_workflow_service_pb2_grpc.ForecastModelWorkflowServiceStub,
        lambda: forecasting_v1_forecast_model_workflow_service_pb2_grpc.ForecastModelWorkflowServiceStub(
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
    identity_user_query = container.singleton(
        identity_v1_user_query_service_pb2_grpc.UserQueryServiceStub,
        lambda: identity_v1_user_query_service_pb2_grpc.UserQueryServiceStub(container.channel)
    )
    identity_user_validation = container.singleton(
        identity_v1_user_validation_service_pb2_grpc.UserValidationServiceStub,
        lambda: identity_v1_user_validation_service_pb2_grpc.UserValidationServiceStub(container.channel)
    )
    labeling_annotation_query = container.singleton(
        labeling_v1_annotation_query_service_pb2_grpc.AnnotationQueryServiceStub,
        lambda: labeling_v1_annotation_query_service_pb2_grpc.AnnotationQueryServiceStub(container.channel)
    )
    labeling_annotation_reporting = container.singleton(
        labeling_v1_annotation_reporting_service_pb2_grpc.AnnotationReportingServiceStub,
        lambda: labeling_v1_annotation_reporting_service_pb2_grpc.AnnotationReportingServiceStub(container.channel)
    )
    labeling_annotation_validation = container.singleton(
        labeling_v1_annotation_validation_service_pb2_grpc.AnnotationValidationServiceStub,
        lambda: labeling_v1_annotation_validation_service_pb2_grpc.AnnotationValidationServiceStub(container.channel)
    )
    labeling_label_set_approval = container.singleton(
        labeling_v1_label_set_approval_service_pb2_grpc.LabelSetApprovalServiceStub,
        lambda: labeling_v1_label_set_approval_service_pb2_grpc.LabelSetApprovalServiceStub(container.channel)
    )
    labeling_label_set_calculation = container.singleton(
        labeling_v1_label_set_calculation_service_pb2_grpc.LabelSetCalculationServiceStub,
        lambda: labeling_v1_label_set_calculation_service_pb2_grpc.LabelSetCalculationServiceStub(container.channel)
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
    lineage_impact_workflow = container.singleton(
        lineage_v1_impact_workflow_service_pb2_grpc.ImpactWorkflowServiceStub,
        lambda: lineage_v1_impact_workflow_service_pb2_grpc.ImpactWorkflowServiceStub(container.channel)
    )
    lineage_lineage_edge_lifecycle = container.singleton(
        lineage_v1_lineage_edge_lifecycle_service_pb2_grpc.LineageEdgeLifecycleServiceStub,
        lambda: lineage_v1_lineage_edge_lifecycle_service_pb2_grpc.LineageEdgeLifecycleServiceStub(container.channel)
    )
    lineage_lineage_edge_workflow = container.singleton(
        lineage_v1_lineage_edge_workflow_service_pb2_grpc.LineageEdgeWorkflowServiceStub,
        lambda: lineage_v1_lineage_edge_workflow_service_pb2_grpc.LineageEdgeWorkflowServiceStub(container.channel)
    )
    lineage_lineage_node_approval = container.singleton(
        lineage_v1_lineage_node_approval_service_pb2_grpc.LineageNodeApprovalServiceStub,
        lambda: lineage_v1_lineage_node_approval_service_pb2_grpc.LineageNodeApprovalServiceStub(container.channel)
    )
    lineage_lineage_node_workflow = container.singleton(
        lineage_v1_lineage_node_workflow_service_pb2_grpc.LineageNodeWorkflowServiceStub,
        lambda: lineage_v1_lineage_node_workflow_service_pb2_grpc.LineageNodeWorkflowServiceStub(container.channel)
    )
    maintenance_work_order_calculation = container.singleton(
        maintenance_v1_work_order_calculation_service_pb2_grpc.WorkOrderCalculationServiceStub,
        lambda: maintenance_v1_work_order_calculation_service_pb2_grpc.WorkOrderCalculationServiceStub(
            container.channel
        )
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
    modelregistry_model_version_sync = container.singleton(
        modelregistry_v1_model_version_sync_service_pb2_grpc.ModelVersionSyncServiceStub,
        lambda: modelregistry_v1_model_version_sync_service_pb2_grpc.ModelVersionSyncServiceStub(container.channel)
    )
    modelregistry_registered_model_calculation = container.singleton(
        modelregistry_v1_registered_model_calculation_service_pb2_grpc.RegisteredModelCalculationServiceStub,
        lambda: modelregistry_v1_registered_model_calculation_service_pb2_grpc.RegisteredModelCalculationServiceStub(
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
    modelregistry_registered_model_workflow = container.singleton(
        modelregistry_v1_registered_model_workflow_service_pb2_grpc.RegisteredModelWorkflowServiceStub,
        lambda: modelregistry_v1_registered_model_workflow_service_pb2_grpc.RegisteredModelWorkflowServiceStub(
            container.channel
        )
    )
    notifications_notification_query = container.singleton(
        notifications_v1_notification_query_service_pb2_grpc.NotificationQueryServiceStub,
        lambda: notifications_v1_notification_query_service_pb2_grpc.NotificationQueryServiceStub(container.channel)
    )
    notifications_notification_validation = container.singleton(
        notifications_v1_notification_validation_service_pb2_grpc.NotificationValidationServiceStub,
        lambda: notifications_v1_notification_validation_service_pb2_grpc.NotificationValidationServiceStub(
            container.channel
        )
    )
    onboarding_onboarding_plan_calculation = container.singleton(
        onboarding_v1_onboarding_plan_calculation_service_pb2_grpc.OnboardingPlanCalculationServiceStub,
        lambda: onboarding_v1_onboarding_plan_calculation_service_pb2_grpc.OnboardingPlanCalculationServiceStub(
            container.channel
        )
    )
    patients_patient_calculation = container.singleton(
        patients_v1_patient_calculation_service_pb2_grpc.PatientCalculationServiceStub,
        lambda: patients_v1_patient_calculation_service_pb2_grpc.PatientCalculationServiceStub(container.channel)
    )
    performers_performer_query = container.singleton(
        performers_v1_performer_query_service_pb2_grpc.PerformerQueryServiceStub,
        lambda: performers_v1_performer_query_service_pb2_grpc.PerformerQueryServiceStub(container.channel)
    )
    pipelines_pipeline_reporting = container.singleton(
        pipelines_v1_pipeline_reporting_service_pb2_grpc.PipelineReportingServiceStub,
        lambda: pipelines_v1_pipeline_reporting_service_pb2_grpc.PipelineReportingServiceStub(container.channel)
    )
    pipelines_pipeline_run_query = container.singleton(
        pipelines_v1_pipeline_run_query_service_pb2_grpc.PipelineRunQueryServiceStub,
        lambda: pipelines_v1_pipeline_run_query_service_pb2_grpc.PipelineRunQueryServiceStub(container.channel)
    )
    pipelines_pipeline_run_sync = container.singleton(
        pipelines_v1_pipeline_run_sync_service_pb2_grpc.PipelineRunSyncServiceStub,
        lambda: pipelines_v1_pipeline_run_sync_service_pb2_grpc.PipelineRunSyncServiceStub(container.channel)
    )
    pipelines_pipeline_run_validation = container.singleton(
        pipelines_v1_pipeline_run_validation_service_pb2_grpc.PipelineRunValidationServiceStub,
        lambda: pipelines_v1_pipeline_run_validation_service_pb2_grpc.PipelineRunValidationServiceStub(
            container.channel
        )
    )
    pipelines_pipeline_run_workflow = container.singleton(
        pipelines_v1_pipeline_run_workflow_service_pb2_grpc.PipelineRunWorkflowServiceStub,
        lambda: pipelines_v1_pipeline_run_workflow_service_pb2_grpc.PipelineRunWorkflowServiceStub(container.channel)
    )
    pipelines_pipeline_step_approval = container.singleton(
        pipelines_v1_pipeline_step_approval_service_pb2_grpc.PipelineStepApprovalServiceStub,
        lambda: pipelines_v1_pipeline_step_approval_service_pb2_grpc.PipelineStepApprovalServiceStub(container.channel)
    )
    pipelines_pipeline_sync = container.singleton(
        pipelines_v1_pipeline_sync_service_pb2_grpc.PipelineSyncServiceStub,
        lambda: pipelines_v1_pipeline_sync_service_pb2_grpc.PipelineSyncServiceStub(container.channel)
    )
    prescriptions_prescription = container.singleton(
        prescriptions_v1_prescription_service_pb2_grpc.PrescriptionServiceStub,
        lambda: prescriptions_v1_prescription_service_pb2_grpc.PrescriptionServiceStub(container.channel)
    )
    ratelimiting_rate_limit_query = container.singleton(
        ratelimiting_v1_rate_limit_query_service_pb2_grpc.RateLimitQueryServiceStub,
        lambda: ratelimiting_v1_rate_limit_query_service_pb2_grpc.RateLimitQueryServiceStub(container.channel)
    )
    ratelimiting_rate_limit = container.singleton(
        ratelimiting_v1_rate_limit_service_pb2_grpc.RateLimitServiceStub,
        lambda: ratelimiting_v1_rate_limit_service_pb2_grpc.RateLimitServiceStub(container.channel)
    )
    recommendations_interaction_calculation = container.singleton(
        recommendations_v1_interaction_calculation_service_pb2_grpc.InteractionCalculationServiceStub,
        lambda: recommendations_v1_interaction_calculation_service_pb2_grpc.InteractionCalculationServiceStub(
            container.channel
        )
    )
    recommendations_recommendation_model_calculation = container.singleton(
        recommendations_v1_recommendation_model_calculation_service_pb2_grpc.RecommendationModelCalculationServiceStub,
        lambda: recommendations_v1_recommendation_model_calculation_service_pb2_grpc.RecommendationModelCalculationServiceStub(
            container.channel
        )
    )
    risk_risk_register_query = container.singleton(
        risk_v1_risk_register_query_service_pb2_grpc.RiskRegisterQueryServiceStub,
        lambda: risk_v1_risk_register_query_service_pb2_grpc.RiskRegisterQueryServiceStub(container.channel)
    )
    search_search_index_query = container.singleton(
        search_v1_search_index_query_service_pb2_grpc.SearchIndexQueryServiceStub,
        lambda: search_v1_search_index_query_service_pb2_grpc.SearchIndexQueryServiceStub(container.channel)
    )
    secrets_secret_query = container.singleton(
        secrets_v1_secret_query_service_pb2_grpc.SecretQueryServiceStub,
        lambda: secrets_v1_secret_query_service_pb2_grpc.SecretQueryServiceStub(container.channel)
    )
    ticketing_ticket_query = container.singleton(
        ticketing_v1_ticket_query_service_pb2_grpc.TicketQueryServiceStub,
        lambda: ticketing_v1_ticket_query_service_pb2_grpc.TicketQueryServiceStub(container.channel)
    )
    travel_trip_calculation = container.singleton(
        travel_v1_trip_calculation_service_pb2_grpc.TripCalculationServiceStub,
        lambda: travel_v1_trip_calculation_service_pb2_grpc.TripCalculationServiceStub(container.channel)
    )
    treasury_cash_position = container.singleton(
        treasury_v1_cash_position_service_pb2_grpc.CashPositionServiceStub,
        lambda: treasury_v1_cash_position_service_pb2_grpc.CashPositionServiceStub(container.channel)
    )
    venues_venue = container.singleton(
        venues_v1_venue_service_pb2_grpc.VenueServiceStub,
        lambda: venues_v1_venue_service_pb2_grpc.VenueServiceStub(container.channel)
    )
    venues_venue_validation = container.singleton(
        venues_v1_venue_validation_service_pb2_grpc.VenueValidationServiceStub,
        lambda: venues_v1_venue_validation_service_pb2_grpc.VenueValidationServiceStub(container.channel)
    )
    yards_yard_calculation = container.singleton(
        yards_v1_yard_calculation_service_pb2_grpc.YardCalculationServiceStub,
        lambda: yards_v1_yard_calculation_service_pb2_grpc.YardCalculationServiceStub(container.channel)
    )
    yards_yard_query = container.singleton(
        yards_v1_yard_query_service_pb2_grpc.YardQueryServiceStub,
        lambda: yards_v1_yard_query_service_pb2_grpc.YardQueryServiceStub(container.channel)
    )
    clients = Clients(
        admissions_admission_calculation=admissions_admission_calculation,
        analytics_analytics_event_approval=analytics_analytics_event_approval,
        analytics_analytics_event_query=analytics_analytics_event_query,
        analytics_analytics_event_validation=analytics_analytics_event_validation,
        analytics_analytics_event_workflow=analytics_analytics_event_workflow,
        analytics_analytics_report_approval=analytics_analytics_report_approval,
        analytics_analytics_report_calculation=analytics_analytics_report_calculation,
        analytics_analytics_report_lifecycle=analytics_analytics_report_lifecycle,
        analytics_analytics_report_validation=analytics_analytics_report_validation,
        analytics_cohort_calculation=analytics_cohort_calculation,
        analytics_cohort_lifecycle=analytics_cohort_lifecycle,
        analytics_cohort_validation=analytics_cohort_validation,
        analytics_funnel_approval=analytics_funnel_approval,
        analytics_funnel_calculation=analytics_funnel_calculation,
        analytics_funnel_query=analytics_funnel_query,
        analytics_funnel_validation=analytics_funnel_validation,
        analytics_funnel_workflow=analytics_funnel_workflow,
        anomalies_anomaly_feedback_approval=anomalies_anomaly_feedback_approval,
        anomalies_anomaly_feedback_calculation=anomalies_anomaly_feedback_calculation,
        anomalies_anomaly_feedback_validation=anomalies_anomaly_feedback_validation,
        anomalies_anomaly_feedback_workflow=anomalies_anomaly_feedback_workflow,
        anomalies_anomaly_query=anomalies_anomaly_query,
        anomalies_anomaly_validation=anomalies_anomaly_validation,
        anomalies_detector_query=anomalies_detector_query,
        anomalies_detector_validation=anomalies_detector_validation,
        appointments_appointment_query=appointments_appointment_query,
        appointments_appointment=appointments_appointment,
        audit_audit_event_query=audit_audit_event_query,
        audit_audit_event=audit_audit_event,
        audit_audit_event_validation=audit_audit_event_validation,
        authorization_access_policy_query=authorization_access_policy_query,
        authorization_access_policy=authorization_access_policy,
        billing_billing_account_query=billing_billing_account_query,
        checkout_checkout_session_query=checkout_checkout_session_query,
        concessions_concession_stand_query=concessions_concession_stand_query,
        configuration_config_set_calculation=configuration_config_set_calculation,
        configuration_config_set=configuration_config_set,
        customers_consent_record_calculation=customers_consent_record_calculation,
        customers_consent_record_validation=customers_consent_record_validation,
        customers_customer_calculation=customers_customer_calculation,
        customers_customer_query=customers_customer_query,
        customers_customer_segment_calculation=customers_customer_segment_calculation,
        customers_customer_segment_validation=customers_customer_segment_validation,
        customers_customer=customers_customer,
        customers_customer_validation=customers_customer_validation,
        customers_household_calculation=customers_household_calculation,
        customers_household_validation=customers_household_validation,
        customers_preference_calculation=customers_preference_calculation,
        customers_preference_validation=customers_preference_validation,
        datasets_data_schema_calculation=datasets_data_schema_calculation,
        datasets_dataset_approval=datasets_dataset_approval,
        datasets_dataset_version_workflow=datasets_dataset_version_workflow,
        deliveries_delivery_query=deliveries_delivery_query,
        documents_document_query=documents_document_query,
        featureflags_feature_flag=featureflags_feature_flag,
        featureflags_feature_flag_validation=featureflags_feature_flag_validation,
        featurestore_entity_reporting=featurestore_entity_reporting,
        featurestore_feature_value_query=featurestore_feature_value_query,
        featurestore_feature_view_lifecycle=featurestore_feature_view_lifecycle,
        featurestore_feature_view_validation=featurestore_feature_view_validation,
        featurestore_feature_view_workflow=featurestore_feature_view_workflow,
        forecasting_forecast_model_approval=forecasting_forecast_model_approval,
        forecasting_forecast_model_query=forecasting_forecast_model_query,
        forecasting_forecast_model_workflow=forecasting_forecast_model_workflow,
        forecasting_scenario_calculation=forecasting_scenario_calculation,
        forecasting_scenario_validation=forecasting_scenario_validation,
        identity_user_query=identity_user_query,
        identity_user_validation=identity_user_validation,
        labeling_annotation_query=labeling_annotation_query,
        labeling_annotation_reporting=labeling_annotation_reporting,
        labeling_annotation_validation=labeling_annotation_validation,
        labeling_label_set_approval=labeling_label_set_approval,
        labeling_label_set_calculation=labeling_label_set_calculation,
        ledger_ledger_account_query=ledger_ledger_account_query,
        ledger_ledger_account=ledger_ledger_account,
        ledger_ledger_account_validation=ledger_ledger_account_validation,
        lineage_impact_lifecycle=lineage_impact_lifecycle,
        lineage_impact_reporting=lineage_impact_reporting,
        lineage_impact_sync=lineage_impact_sync,
        lineage_impact_workflow=lineage_impact_workflow,
        lineage_lineage_edge_lifecycle=lineage_lineage_edge_lifecycle,
        lineage_lineage_edge_workflow=lineage_lineage_edge_workflow,
        lineage_lineage_node_approval=lineage_lineage_node_approval,
        lineage_lineage_node_workflow=lineage_lineage_node_workflow,
        maintenance_work_order_calculation=maintenance_work_order_calculation,
        metrics_dashboard_history=metrics_dashboard_history,
        metrics_dashboard_sync=metrics_dashboard_sync,
        metrics_dashboard_validation=metrics_dashboard_validation,
        metrics_metric_alert_notification=metrics_metric_alert_notification,
        metrics_metric_alert_query=metrics_metric_alert_query,
        metrics_metric_alert_validation=metrics_metric_alert_validation,
        metrics_metric_series_export=metrics_metric_series_export,
        metrics_metric_series_notification=metrics_metric_series_notification,
        metrics_metric_series_query=metrics_metric_series_query,
        metrics_metric_series=metrics_metric_series,
        metrics_metric_series_validation=metrics_metric_series_validation,
        modelregistry_model_version_sync=modelregistry_model_version_sync,
        modelregistry_registered_model_calculation=modelregistry_registered_model_calculation,
        modelregistry_registered_model_reporting=modelregistry_registered_model_reporting,
        modelregistry_registered_model=modelregistry_registered_model,
        modelregistry_registered_model_workflow=modelregistry_registered_model_workflow,
        notifications_notification_query=notifications_notification_query,
        notifications_notification_validation=notifications_notification_validation,
        onboarding_onboarding_plan_calculation=onboarding_onboarding_plan_calculation,
        patients_patient_calculation=patients_patient_calculation,
        performers_performer_query=performers_performer_query,
        pipelines_pipeline_reporting=pipelines_pipeline_reporting,
        pipelines_pipeline_run_query=pipelines_pipeline_run_query,
        pipelines_pipeline_run_sync=pipelines_pipeline_run_sync,
        pipelines_pipeline_run_validation=pipelines_pipeline_run_validation,
        pipelines_pipeline_run_workflow=pipelines_pipeline_run_workflow,
        pipelines_pipeline_step_approval=pipelines_pipeline_step_approval,
        pipelines_pipeline_sync=pipelines_pipeline_sync,
        prescriptions_prescription=prescriptions_prescription,
        ratelimiting_rate_limit_query=ratelimiting_rate_limit_query,
        ratelimiting_rate_limit=ratelimiting_rate_limit,
        recommendations_interaction_calculation=recommendations_interaction_calculation,
        recommendations_recommendation_model_calculation=recommendations_recommendation_model_calculation,
        risk_risk_register_query=risk_risk_register_query,
        search_search_index_query=search_search_index_query,
        secrets_secret_query=secrets_secret_query,
        ticketing_ticket_query=ticketing_ticket_query,
        travel_trip_calculation=travel_trip_calculation,
        treasury_cash_position=treasury_cash_position,
        venues_venue=venues_venue,
        venues_venue_validation=venues_venue_validation,
        yards_yard_calculation=yards_yard_calculation,
        yards_yard_query=yards_yard_query,
        registry={
            'acme.admissions.v1.AdmissionCalculationService': admissions_admission_calculation,
            'acme.analytics.v1.AnalyticsEventApprovalService': analytics_analytics_event_approval,
            'acme.analytics.v1.AnalyticsEventQueryService': analytics_analytics_event_query,
            'acme.analytics.v1.AnalyticsEventValidationService': analytics_analytics_event_validation,
            'acme.analytics.v1.AnalyticsEventWorkflowService': analytics_analytics_event_workflow,
            'acme.analytics.v1.AnalyticsReportApprovalService': analytics_analytics_report_approval,
            'acme.analytics.v1.AnalyticsReportCalculationService': analytics_analytics_report_calculation,
            'acme.analytics.v1.AnalyticsReportLifecycleService': analytics_analytics_report_lifecycle,
            'acme.analytics.v1.AnalyticsReportValidationService': analytics_analytics_report_validation,
            'acme.analytics.v1.CohortCalculationService': analytics_cohort_calculation,
            'acme.analytics.v1.CohortLifecycleService': analytics_cohort_lifecycle,
            'acme.analytics.v1.CohortValidationService': analytics_cohort_validation,
            'acme.analytics.v1.FunnelApprovalService': analytics_funnel_approval,
            'acme.analytics.v1.FunnelCalculationService': analytics_funnel_calculation,
            'acme.analytics.v1.FunnelQueryService': analytics_funnel_query,
            'acme.analytics.v1.FunnelValidationService': analytics_funnel_validation,
            'acme.analytics.v1.FunnelWorkflowService': analytics_funnel_workflow,
            'acme.anomalies.v1.AnomalyFeedbackApprovalService': anomalies_anomaly_feedback_approval,
            'acme.anomalies.v1.AnomalyFeedbackCalculationService': anomalies_anomaly_feedback_calculation,
            'acme.anomalies.v1.AnomalyFeedbackValidationService': anomalies_anomaly_feedback_validation,
            'acme.anomalies.v1.AnomalyFeedbackWorkflowService': anomalies_anomaly_feedback_workflow,
            'acme.anomalies.v1.AnomalyQueryService': anomalies_anomaly_query,
            'acme.anomalies.v1.AnomalyValidationService': anomalies_anomaly_validation,
            'acme.anomalies.v1.DetectorQueryService': anomalies_detector_query,
            'acme.anomalies.v1.DetectorValidationService': anomalies_detector_validation,
            'acme.appointments.v1.AppointmentQueryService': appointments_appointment_query,
            'acme.appointments.v1.AppointmentService': appointments_appointment,
            'acme.audit.v1.AuditEventQueryService': audit_audit_event_query,
            'acme.audit.v1.AuditEventService': audit_audit_event,
            'acme.audit.v1.AuditEventValidationService': audit_audit_event_validation,
            'acme.authorization.v1.AccessPolicyQueryService': authorization_access_policy_query,
            'acme.authorization.v1.AccessPolicyService': authorization_access_policy,
            'acme.billing.v1.BillingAccountQueryService': billing_billing_account_query,
            'acme.checkout.v1.CheckoutSessionQueryService': checkout_checkout_session_query,
            'acme.concessions.v1.ConcessionStandQueryService': concessions_concession_stand_query,
            'acme.configuration.v1.ConfigSetCalculationService': configuration_config_set_calculation,
            'acme.configuration.v1.ConfigSetService': configuration_config_set,
            'acme.customers.v1.ConsentRecordCalculationService': customers_consent_record_calculation,
            'acme.customers.v1.ConsentRecordValidationService': customers_consent_record_validation,
            'acme.customers.v1.CustomerCalculationService': customers_customer_calculation,
            'acme.customers.v1.CustomerQueryService': customers_customer_query,
            'acme.customers.v1.CustomerSegmentCalculationService': customers_customer_segment_calculation,
            'acme.customers.v1.CustomerSegmentValidationService': customers_customer_segment_validation,
            'acme.customers.v1.CustomerService': customers_customer,
            'acme.customers.v1.CustomerValidationService': customers_customer_validation,
            'acme.customers.v1.HouseholdCalculationService': customers_household_calculation,
            'acme.customers.v1.HouseholdValidationService': customers_household_validation,
            'acme.customers.v1.PreferenceCalculationService': customers_preference_calculation,
            'acme.customers.v1.PreferenceValidationService': customers_preference_validation,
            'acme.datasets.v1.DataSchemaCalculationService': datasets_data_schema_calculation,
            'acme.datasets.v1.DatasetApprovalService': datasets_dataset_approval,
            'acme.datasets.v1.DatasetVersionWorkflowService': datasets_dataset_version_workflow,
            'acme.deliveries.v1.DeliveryQueryService': deliveries_delivery_query,
            'acme.documents.v1.DocumentQueryService': documents_document_query,
            'acme.featureflags.v1.FeatureFlagService': featureflags_feature_flag,
            'acme.featureflags.v1.FeatureFlagValidationService': featureflags_feature_flag_validation,
            'acme.featurestore.v1.EntityReportingService': featurestore_entity_reporting,
            'acme.featurestore.v1.FeatureValueQueryService': featurestore_feature_value_query,
            'acme.featurestore.v1.FeatureViewLifecycleService': featurestore_feature_view_lifecycle,
            'acme.featurestore.v1.FeatureViewValidationService': featurestore_feature_view_validation,
            'acme.featurestore.v1.FeatureViewWorkflowService': featurestore_feature_view_workflow,
            'acme.forecasting.v1.ForecastModelApprovalService': forecasting_forecast_model_approval,
            'acme.forecasting.v1.ForecastModelQueryService': forecasting_forecast_model_query,
            'acme.forecasting.v1.ForecastModelWorkflowService': forecasting_forecast_model_workflow,
            'acme.forecasting.v1.ScenarioCalculationService': forecasting_scenario_calculation,
            'acme.forecasting.v1.ScenarioValidationService': forecasting_scenario_validation,
            'acme.identity.v1.UserQueryService': identity_user_query,
            'acme.identity.v1.UserValidationService': identity_user_validation,
            'acme.labeling.v1.AnnotationQueryService': labeling_annotation_query,
            'acme.labeling.v1.AnnotationReportingService': labeling_annotation_reporting,
            'acme.labeling.v1.AnnotationValidationService': labeling_annotation_validation,
            'acme.labeling.v1.LabelSetApprovalService': labeling_label_set_approval,
            'acme.labeling.v1.LabelSetCalculationService': labeling_label_set_calculation,
            'acme.ledger.v1.LedgerAccountQueryService': ledger_ledger_account_query,
            'acme.ledger.v1.LedgerAccountService': ledger_ledger_account,
            'acme.ledger.v1.LedgerAccountValidationService': ledger_ledger_account_validation,
            'acme.lineage.v1.ImpactLifecycleService': lineage_impact_lifecycle,
            'acme.lineage.v1.ImpactReportingService': lineage_impact_reporting,
            'acme.lineage.v1.ImpactSyncService': lineage_impact_sync,
            'acme.lineage.v1.ImpactWorkflowService': lineage_impact_workflow,
            'acme.lineage.v1.LineageEdgeLifecycleService': lineage_lineage_edge_lifecycle,
            'acme.lineage.v1.LineageEdgeWorkflowService': lineage_lineage_edge_workflow,
            'acme.lineage.v1.LineageNodeApprovalService': lineage_lineage_node_approval,
            'acme.lineage.v1.LineageNodeWorkflowService': lineage_lineage_node_workflow,
            'acme.maintenance.v1.WorkOrderCalculationService': maintenance_work_order_calculation,
            'acme.metrics.v1.DashboardHistoryService': metrics_dashboard_history,
            'acme.metrics.v1.DashboardSyncService': metrics_dashboard_sync,
            'acme.metrics.v1.DashboardValidationService': metrics_dashboard_validation,
            'acme.metrics.v1.MetricAlertNotificationService': metrics_metric_alert_notification,
            'acme.metrics.v1.MetricAlertQueryService': metrics_metric_alert_query,
            'acme.metrics.v1.MetricAlertValidationService': metrics_metric_alert_validation,
            'acme.metrics.v1.MetricSeriesExportService': metrics_metric_series_export,
            'acme.metrics.v1.MetricSeriesNotificationService': metrics_metric_series_notification,
            'acme.metrics.v1.MetricSeriesQueryService': metrics_metric_series_query,
            'acme.metrics.v1.MetricSeriesService': metrics_metric_series,
            'acme.metrics.v1.MetricSeriesValidationService': metrics_metric_series_validation,
            'acme.modelregistry.v1.ModelVersionSyncService': modelregistry_model_version_sync,
            'acme.modelregistry.v1.RegisteredModelCalculationService': modelregistry_registered_model_calculation,
            'acme.modelregistry.v1.RegisteredModelReportingService': modelregistry_registered_model_reporting,
            'acme.modelregistry.v1.RegisteredModelService': modelregistry_registered_model,
            'acme.modelregistry.v1.RegisteredModelWorkflowService': modelregistry_registered_model_workflow,
            'acme.notifications.v1.NotificationQueryService': notifications_notification_query,
            'acme.notifications.v1.NotificationValidationService': notifications_notification_validation,
            'acme.onboarding.v1.OnboardingPlanCalculationService': onboarding_onboarding_plan_calculation,
            'acme.patients.v1.PatientCalculationService': patients_patient_calculation,
            'acme.performers.v1.PerformerQueryService': performers_performer_query,
            'acme.pipelines.v1.PipelineReportingService': pipelines_pipeline_reporting,
            'acme.pipelines.v1.PipelineRunQueryService': pipelines_pipeline_run_query,
            'acme.pipelines.v1.PipelineRunSyncService': pipelines_pipeline_run_sync,
            'acme.pipelines.v1.PipelineRunValidationService': pipelines_pipeline_run_validation,
            'acme.pipelines.v1.PipelineRunWorkflowService': pipelines_pipeline_run_workflow,
            'acme.pipelines.v1.PipelineStepApprovalService': pipelines_pipeline_step_approval,
            'acme.pipelines.v1.PipelineSyncService': pipelines_pipeline_sync,
            'acme.prescriptions.v1.PrescriptionService': prescriptions_prescription,
            'acme.ratelimiting.v1.RateLimitQueryService': ratelimiting_rate_limit_query,
            'acme.ratelimiting.v1.RateLimitService': ratelimiting_rate_limit,
            'acme.recommendations.v1.InteractionCalculationService': recommendations_interaction_calculation,
            'acme.recommendations.v1.RecommendationModelCalculationService': recommendations_recommendation_model_calculation,
            'acme.risk.v1.RiskRegisterQueryService': risk_risk_register_query,
            'acme.search.v1.SearchIndexQueryService': search_search_index_query,
            'acme.secrets.v1.SecretQueryService': secrets_secret_query,
            'acme.ticketing.v1.TicketQueryService': ticketing_ticket_query,
            'acme.travel.v1.TripCalculationService': travel_trip_calculation,
            'acme.treasury.v1.CashPositionService': treasury_cash_position,
            'acme.venues.v1.VenueService': venues_venue,
            'acme.venues.v1.VenueValidationService': venues_venue_validation,
            'acme.yards.v1.YardCalculationService': yards_yard_calculation,
            'acme.yards.v1.YardQueryService': yards_yard_query,
        },
    )
    return Dependencies(clients, DomainRepository(container.sessions),
                        container.settings, container.bus)


def register(server: grpc.aio.Server, container: Container) -> dict[str, object]:
    deps = dependencies(container)
    registered: dict[str, object] = {}
    analytics_event_approval_servicer = Factory(lambda: AnalyticsEventApprovalServicer(deps))()
    analytics_v1_analytics_event_approval_service_pb2_grpc.add_AnalyticsEventApprovalServiceServicer_to_server(
        analytics_event_approval_servicer,
        server
    )
    registered['acme.analytics.v1.AnalyticsEventApprovalService'] = analytics_event_approval_servicer
    analytics_event_query_servicer = Factory(lambda: AnalyticsEventQueryServicer(deps))()
    analytics_v1_analytics_event_query_service_pb2_grpc.add_AnalyticsEventQueryServiceServicer_to_server(
        analytics_event_query_servicer,
        server
    )
    registered['acme.analytics.v1.AnalyticsEventQueryService'] = analytics_event_query_servicer
    analytics_event_servicer = Factory(lambda: AnalyticsEventServicer(deps))()
    analytics_v1_analytics_event_service_pb2_grpc.add_AnalyticsEventServiceServicer_to_server(
        analytics_event_servicer,
        server
    )
    registered['acme.analytics.v1.AnalyticsEventService'] = analytics_event_servicer
    analytics_event_validation_servicer = Factory(lambda: AnalyticsEventValidationServicer(deps))()
    analytics_v1_analytics_event_validation_service_pb2_grpc.add_AnalyticsEventValidationServiceServicer_to_server(
        analytics_event_validation_servicer,
        server
    )
    registered['acme.analytics.v1.AnalyticsEventValidationService'] = analytics_event_validation_servicer
    analytics_event_workflow_servicer = Factory(lambda: AnalyticsEventWorkflowServicer(deps))()
    analytics_v1_analytics_event_workflow_service_pb2_grpc.add_AnalyticsEventWorkflowServiceServicer_to_server(
        analytics_event_workflow_servicer,
        server
    )
    registered['acme.analytics.v1.AnalyticsEventWorkflowService'] = analytics_event_workflow_servicer
    analytics_report_approval_servicer = Factory(lambda: AnalyticsReportApprovalServicer(deps))()
    analytics_v1_analytics_report_approval_service_pb2_grpc.add_AnalyticsReportApprovalServiceServicer_to_server(
        analytics_report_approval_servicer,
        server
    )
    registered['acme.analytics.v1.AnalyticsReportApprovalService'] = analytics_report_approval_servicer
    analytics_report_calculation_servicer = Factory(lambda: AnalyticsReportCalculationServicer(deps))()
    analytics_v1_analytics_report_calculation_service_pb2_grpc.add_AnalyticsReportCalculationServiceServicer_to_server(
        analytics_report_calculation_servicer,
        server
    )
    registered['acme.analytics.v1.AnalyticsReportCalculationService'] = analytics_report_calculation_servicer
    analytics_report_lifecycle_servicer = Factory(lambda: AnalyticsReportLifecycleServicer(deps))()
    analytics_v1_analytics_report_lifecycle_service_pb2_grpc.add_AnalyticsReportLifecycleServiceServicer_to_server(
        analytics_report_lifecycle_servicer,
        server
    )
    registered['acme.analytics.v1.AnalyticsReportLifecycleService'] = analytics_report_lifecycle_servicer
    analytics_report_validation_servicer = Factory(lambda: AnalyticsReportValidationServicer(deps))()
    analytics_v1_analytics_report_validation_service_pb2_grpc.add_AnalyticsReportValidationServiceServicer_to_server(
        analytics_report_validation_servicer,
        server
    )
    registered['acme.analytics.v1.AnalyticsReportValidationService'] = analytics_report_validation_servicer
    cohort_approval_servicer = Factory(lambda: CohortApprovalServicer(deps))()
    analytics_v1_cohort_approval_service_pb2_grpc.add_CohortApprovalServiceServicer_to_server(
        cohort_approval_servicer,
        server
    )
    registered['acme.analytics.v1.CohortApprovalService'] = cohort_approval_servicer
    cohort_calculation_servicer = Factory(lambda: CohortCalculationServicer(deps))()
    analytics_v1_cohort_calculation_service_pb2_grpc.add_CohortCalculationServiceServicer_to_server(
        cohort_calculation_servicer,
        server
    )
    registered['acme.analytics.v1.CohortCalculationService'] = cohort_calculation_servicer
    cohort_lifecycle_servicer = Factory(lambda: CohortLifecycleServicer(deps))()
    analytics_v1_cohort_lifecycle_service_pb2_grpc.add_CohortLifecycleServiceServicer_to_server(
        cohort_lifecycle_servicer,
        server
    )
    registered['acme.analytics.v1.CohortLifecycleService'] = cohort_lifecycle_servicer
    cohort_validation_servicer = Factory(lambda: CohortValidationServicer(deps))()
    analytics_v1_cohort_validation_service_pb2_grpc.add_CohortValidationServiceServicer_to_server(
        cohort_validation_servicer,
        server
    )
    registered['acme.analytics.v1.CohortValidationService'] = cohort_validation_servicer
    cohort_workflow_servicer = Factory(lambda: CohortWorkflowServicer(deps))()
    analytics_v1_cohort_workflow_service_pb2_grpc.add_CohortWorkflowServiceServicer_to_server(
        cohort_workflow_servicer,
        server
    )
    registered['acme.analytics.v1.CohortWorkflowService'] = cohort_workflow_servicer
    funnel_approval_servicer = Factory(lambda: FunnelApprovalServicer(deps))()
    analytics_v1_funnel_approval_service_pb2_grpc.add_FunnelApprovalServiceServicer_to_server(
        funnel_approval_servicer,
        server
    )
    registered['acme.analytics.v1.FunnelApprovalService'] = funnel_approval_servicer
    funnel_calculation_servicer = Factory(lambda: FunnelCalculationServicer(deps))()
    analytics_v1_funnel_calculation_service_pb2_grpc.add_FunnelCalculationServiceServicer_to_server(
        funnel_calculation_servicer,
        server
    )
    registered['acme.analytics.v1.FunnelCalculationService'] = funnel_calculation_servicer
    funnel_query_servicer = Factory(lambda: FunnelQueryServicer(deps))()
    analytics_v1_funnel_query_service_pb2_grpc.add_FunnelQueryServiceServicer_to_server(funnel_query_servicer, server)
    registered['acme.analytics.v1.FunnelQueryService'] = funnel_query_servicer
    funnel_validation_servicer = Factory(lambda: FunnelValidationServicer(deps))()
    analytics_v1_funnel_validation_service_pb2_grpc.add_FunnelValidationServiceServicer_to_server(
        funnel_validation_servicer,
        server
    )
    registered['acme.analytics.v1.FunnelValidationService'] = funnel_validation_servicer
    funnel_workflow_servicer = Factory(lambda: FunnelWorkflowServicer(deps))()
    analytics_v1_funnel_workflow_service_pb2_grpc.add_FunnelWorkflowServiceServicer_to_server(
        funnel_workflow_servicer,
        server
    )
    registered['acme.analytics.v1.FunnelWorkflowService'] = funnel_workflow_servicer
    subscribe(deps)
    return registered
