"""Register and compose every service of the datahub domain."""

from __future__ import annotations

import grpc

from acme.analytics.v1 import (
    analytics_event_approval_service_pb2_grpc as analytics_v1_analytics_event_approval_service_pb2_grpc,
)
from acme.analytics.v1 import (
    analytics_report_approval_service_pb2_grpc as analytics_v1_analytics_report_approval_service_pb2_grpc,
)
from acme.analytics.v1 import (
    analytics_report_lifecycle_service_pb2_grpc as analytics_v1_analytics_report_lifecycle_service_pb2_grpc,
)
from acme.analytics.v1 import cohort_workflow_service_pb2_grpc as analytics_v1_cohort_workflow_service_pb2_grpc
from acme.analytics.v1 import funnel_approval_service_pb2_grpc as analytics_v1_funnel_approval_service_pb2_grpc
from acme.analytics.v1 import funnel_workflow_service_pb2_grpc as analytics_v1_funnel_workflow_service_pb2_grpc
from acme.anomalies.v1 import anomaly_approval_service_pb2_grpc as anomalies_v1_anomaly_approval_service_pb2_grpc
from acme.anomalies.v1 import (
    anomaly_feedback_approval_service_pb2_grpc as anomalies_v1_anomaly_feedback_approval_service_pb2_grpc,
)
from acme.anomalies.v1 import anomaly_workflow_service_pb2_grpc as anomalies_v1_anomaly_workflow_service_pb2_grpc
from acme.anomalies.v1 import detector_workflow_service_pb2_grpc as anomalies_v1_detector_workflow_service_pb2_grpc
from acme.audit.v1 import audit_event_query_service_pb2_grpc as audit_v1_audit_event_query_service_pb2_grpc
from acme.audit.v1 import audit_event_validation_service_pb2_grpc as audit_v1_audit_event_validation_service_pb2_grpc
from acme.authorization.v1 import access_policy_service_pb2_grpc as authorization_v1_access_policy_service_pb2_grpc
from acme.authorization.v1 import (
    access_policy_validation_service_pb2_grpc as authorization_v1_access_policy_validation_service_pb2_grpc,
)
from acme.billing.v1 import billing_account_query_service_pb2_grpc as billing_v1_billing_account_query_service_pb2_grpc
from acme.customers.v1 import (
    consent_record_approval_service_pb2_grpc as customers_v1_consent_record_approval_service_pb2_grpc,
)
from acme.customers.v1 import (
    consent_record_lifecycle_service_pb2_grpc as customers_v1_consent_record_lifecycle_service_pb2_grpc,
)
from acme.customers.v1 import (
    consent_record_reporting_service_pb2_grpc as customers_v1_consent_record_reporting_service_pb2_grpc,
)
from acme.customers.v1 import consent_record_sync_service_pb2_grpc as customers_v1_consent_record_sync_service_pb2_grpc
from acme.customers.v1 import (
    consent_record_workflow_service_pb2_grpc as customers_v1_consent_record_workflow_service_pb2_grpc,
)
from acme.customers.v1 import customer_approval_service_pb2_grpc as customers_v1_customer_approval_service_pb2_grpc
from acme.customers.v1 import (
    customer_segment_approval_service_pb2_grpc as customers_v1_customer_segment_approval_service_pb2_grpc,
)
from acme.customers.v1 import (
    customer_segment_import_service_pb2_grpc as customers_v1_customer_segment_import_service_pb2_grpc,
)
from acme.customers.v1 import (
    customer_segment_reporting_service_pb2_grpc as customers_v1_customer_segment_reporting_service_pb2_grpc,
)
from acme.customers.v1 import (
    customer_segment_sync_service_pb2_grpc as customers_v1_customer_segment_sync_service_pb2_grpc,
)
from acme.customers.v1 import customer_workflow_service_pb2_grpc as customers_v1_customer_workflow_service_pb2_grpc
from acme.customers.v1 import household_approval_service_pb2_grpc as customers_v1_household_approval_service_pb2_grpc
from acme.customers.v1 import household_reporting_service_pb2_grpc as customers_v1_household_reporting_service_pb2_grpc
from acme.customers.v1 import household_workflow_service_pb2_grpc as customers_v1_household_workflow_service_pb2_grpc
from acme.customers.v1 import (
    preference_calculation_service_pb2_grpc as customers_v1_preference_calculation_service_pb2_grpc,
)
from acme.customers.v1 import preference_import_service_pb2_grpc as customers_v1_preference_import_service_pb2_grpc
from acme.customers.v1 import (
    preference_lifecycle_service_pb2_grpc as customers_v1_preference_lifecycle_service_pb2_grpc,
)
from acme.customers.v1 import (
    preference_reporting_service_pb2_grpc as customers_v1_preference_reporting_service_pb2_grpc,
)
from acme.customers.v1 import preference_sync_service_pb2_grpc as customers_v1_preference_sync_service_pb2_grpc
from acme.datahub.v1 import data_share_approval_service_pb2_grpc as datahub_v1_data_share_approval_service_pb2_grpc
from acme.datahub.v1 import (
    data_share_integration_service_pb2_grpc as datahub_v1_data_share_integration_service_pb2_grpc,
)
from acme.datahub.v1 import (
    data_share_notification_service_pb2_grpc as datahub_v1_data_share_notification_service_pb2_grpc,
)
from acme.datahub.v1 import data_share_query_service_pb2_grpc as datahub_v1_data_share_query_service_pb2_grpc
from acme.datahub.v1 import data_share_reporting_service_pb2_grpc as datahub_v1_data_share_reporting_service_pb2_grpc
from acme.datahub.v1 import data_share_validation_service_pb2_grpc as datahub_v1_data_share_validation_service_pb2_grpc
from acme.datahub.v1 import data_share_workflow_service_pb2_grpc as datahub_v1_data_share_workflow_service_pb2_grpc
from acme.datahub.v1 import notebook_approval_service_pb2_grpc as datahub_v1_notebook_approval_service_pb2_grpc
from acme.datahub.v1 import notebook_integration_service_pb2_grpc as datahub_v1_notebook_integration_service_pb2_grpc
from acme.datahub.v1 import notebook_notification_service_pb2_grpc as datahub_v1_notebook_notification_service_pb2_grpc
from acme.datahub.v1 import notebook_query_service_pb2_grpc as datahub_v1_notebook_query_service_pb2_grpc
from acme.datahub.v1 import notebook_reporting_service_pb2_grpc as datahub_v1_notebook_reporting_service_pb2_grpc
from acme.datahub.v1 import notebook_service_pb2_grpc as datahub_v1_notebook_service_pb2_grpc
from acme.datahub.v1 import notebook_workflow_service_pb2_grpc as datahub_v1_notebook_workflow_service_pb2_grpc
from acme.datahub.v1 import workspace_approval_service_pb2_grpc as datahub_v1_workspace_approval_service_pb2_grpc
from acme.datahub.v1 import workspace_gateway_service_pb2_grpc as datahub_v1_workspace_gateway_service_pb2_grpc
from acme.datahub.v1 import workspace_integration_service_pb2_grpc as datahub_v1_workspace_integration_service_pb2_grpc
from acme.datahub.v1 import (
    workspace_notification_service_pb2_grpc as datahub_v1_workspace_notification_service_pb2_grpc,
)
from acme.datahub.v1 import workspace_query_service_pb2_grpc as datahub_v1_workspace_query_service_pb2_grpc
from acme.datahub.v1 import workspace_reporting_service_pb2_grpc as datahub_v1_workspace_reporting_service_pb2_grpc
from acme.datahub.v1 import workspace_service_pb2_grpc as datahub_v1_workspace_service_pb2_grpc
from acme.datahub.v1 import workspace_workflow_service_pb2_grpc as datahub_v1_workspace_workflow_service_pb2_grpc
from acme.datasets.v1 import data_schema_approval_service_pb2_grpc as datasets_v1_data_schema_approval_service_pb2_grpc
from acme.datasets.v1 import dataset_approval_service_pb2_grpc as datasets_v1_dataset_approval_service_pb2_grpc
from acme.datasets.v1 import dataset_workflow_service_pb2_grpc as datasets_v1_dataset_workflow_service_pb2_grpc
from acme.documents.v1 import document_query_service_pb2_grpc as documents_v1_document_query_service_pb2_grpc
from acme.documents.v1 import document_service_pb2_grpc as documents_v1_document_service_pb2_grpc
from acme.documents.v1 import document_validation_service_pb2_grpc as documents_v1_document_validation_service_pb2_grpc
from acme.driverapp.v1 import driver_home_query_service_pb2_grpc as driverapp_v1_driver_home_query_service_pb2_grpc
from acme.driverapp.v1 import driver_home_service_pb2_grpc as driverapp_v1_driver_home_service_pb2_grpc
from acme.edgegateway.v1 import (
    route_binding_query_service_pb2_grpc as edgegateway_v1_route_binding_query_service_pb2_grpc,
)
from acme.edgegateway.v1 import route_binding_service_pb2_grpc as edgegateway_v1_route_binding_service_pb2_grpc
from acme.fanportal.v1 import fan_session_query_service_pb2_grpc as fanportal_v1_fan_session_query_service_pb2_grpc
from acme.fanportal.v1 import fan_session_service_pb2_grpc as fanportal_v1_fan_session_service_pb2_grpc
from acme.featureflags.v1 import (
    feature_flag_query_service_pb2_grpc as featureflags_v1_feature_flag_query_service_pb2_grpc,
)
from acme.featureflags.v1 import feature_flag_service_pb2_grpc as featureflags_v1_feature_flag_service_pb2_grpc
from acme.featureflags.v1 import (
    feature_flag_validation_service_pb2_grpc as featureflags_v1_feature_flag_validation_service_pb2_grpc,
)
from acme.featurestore.v1 import entity_import_service_pb2_grpc as featurestore_v1_entity_import_service_pb2_grpc
from acme.featurestore.v1 import entity_reporting_service_pb2_grpc as featurestore_v1_entity_reporting_service_pb2_grpc
from acme.featurestore.v1 import (
    feature_value_reporting_service_pb2_grpc as featurestore_v1_feature_value_reporting_service_pb2_grpc,
)
from acme.featurestore.v1 import (
    feature_value_workflow_service_pb2_grpc as featurestore_v1_feature_value_workflow_service_pb2_grpc,
)
from acme.featurestore.v1 import (
    feature_view_sync_service_pb2_grpc as featurestore_v1_feature_view_sync_service_pb2_grpc,
)
from acme.featurestore.v1 import (
    feature_view_workflow_service_pb2_grpc as featurestore_v1_feature_view_workflow_service_pb2_grpc,
)
from acme.forecasting.v1 import (
    demand_forecast_approval_service_pb2_grpc as forecasting_v1_demand_forecast_approval_service_pb2_grpc,
)
from acme.forecasting.v1 import (
    demand_forecast_workflow_service_pb2_grpc as forecasting_v1_demand_forecast_workflow_service_pb2_grpc,
)
from acme.forecasting.v1 import scenario_workflow_service_pb2_grpc as forecasting_v1_scenario_workflow_service_pb2_grpc
from acme.identity.v1 import user_query_service_pb2_grpc as identity_v1_user_query_service_pb2_grpc
from acme.identity.v1 import user_validation_service_pb2_grpc as identity_v1_user_validation_service_pb2_grpc
from acme.itsm.v1 import incident_service_pb2_grpc as itsm_v1_incident_service_pb2_grpc
from acme.labeling.v1 import annotation_approval_service_pb2_grpc as labeling_v1_annotation_approval_service_pb2_grpc
from acme.labeling.v1 import label_set_approval_service_pb2_grpc as labeling_v1_label_set_approval_service_pb2_grpc
from acme.labeling.v1 import label_set_reporting_service_pb2_grpc as labeling_v1_label_set_reporting_service_pb2_grpc
from acme.labeling.v1 import (
    labeling_task_approval_service_pb2_grpc as labeling_v1_labeling_task_approval_service_pb2_grpc,
)
from acme.labeling.v1 import (
    labeling_task_workflow_service_pb2_grpc as labeling_v1_labeling_task_workflow_service_pb2_grpc,
)
from acme.learning.v1 import course_query_service_pb2_grpc as learning_v1_course_query_service_pb2_grpc
from acme.ledger.v1 import ledger_account_query_service_pb2_grpc as ledger_v1_ledger_account_query_service_pb2_grpc
from acme.ledger.v1 import ledger_account_service_pb2_grpc as ledger_v1_ledger_account_service_pb2_grpc
from acme.lineage.v1 import impact_approval_service_pb2_grpc as lineage_v1_impact_approval_service_pb2_grpc
from acme.lineage.v1 import impact_workflow_service_pb2_grpc as lineage_v1_impact_workflow_service_pb2_grpc
from acme.lineage.v1 import lineage_edge_workflow_service_pb2_grpc as lineage_v1_lineage_edge_workflow_service_pb2_grpc
from acme.lineage.v1 import lineage_node_workflow_service_pb2_grpc as lineage_v1_lineage_node_workflow_service_pb2_grpc
from acme.metrics.v1 import dashboard_history_service_pb2_grpc as metrics_v1_dashboard_history_service_pb2_grpc
from acme.metrics.v1 import (
    dashboard_notification_service_pb2_grpc as metrics_v1_dashboard_notification_service_pb2_grpc,
)
from acme.metrics.v1 import dashboard_sync_service_pb2_grpc as metrics_v1_dashboard_sync_service_pb2_grpc
from acme.metrics.v1 import dashboard_validation_service_pb2_grpc as metrics_v1_dashboard_validation_service_pb2_grpc
from acme.metrics.v1 import metric_alert_history_service_pb2_grpc as metrics_v1_metric_alert_history_service_pb2_grpc
from acme.metrics.v1 import (
    metric_alert_notification_service_pb2_grpc as metrics_v1_metric_alert_notification_service_pb2_grpc,
)
from acme.metrics.v1 import (
    metric_alert_validation_service_pb2_grpc as metrics_v1_metric_alert_validation_service_pb2_grpc,
)
from acme.metrics.v1 import metric_series_admin_service_pb2_grpc as metrics_v1_metric_series_admin_service_pb2_grpc
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
    deployment_approval_service_pb2_grpc as modelregistry_v1_deployment_approval_service_pb2_grpc,
)
from acme.modelregistry.v1 import (
    deployment_import_service_pb2_grpc as modelregistry_v1_deployment_import_service_pb2_grpc,
)
from acme.modelregistry.v1 import deployment_sync_service_pb2_grpc as modelregistry_v1_deployment_sync_service_pb2_grpc
from acme.modelregistry.v1 import (
    model_version_approval_service_pb2_grpc as modelregistry_v1_model_version_approval_service_pb2_grpc,
)
from acme.modelregistry.v1 import (
    model_version_reporting_service_pb2_grpc as modelregistry_v1_model_version_reporting_service_pb2_grpc,
)
from acme.modelregistry.v1 import (
    registered_model_lifecycle_service_pb2_grpc as modelregistry_v1_registered_model_lifecycle_service_pb2_grpc,
)
from acme.modelregistry.v1 import (
    registered_model_reporting_service_pb2_grpc as modelregistry_v1_registered_model_reporting_service_pb2_grpc,
)
from acme.notifications.v1 import (
    notification_query_service_pb2_grpc as notifications_v1_notification_query_service_pb2_grpc,
)
from acme.notifications.v1 import notification_service_pb2_grpc as notifications_v1_notification_service_pb2_grpc
from acme.notifications.v1 import (
    notification_validation_service_pb2_grpc as notifications_v1_notification_validation_service_pb2_grpc,
)
from acme.patientapp.v1 import patient_home_query_service_pb2_grpc as patientapp_v1_patient_home_query_service_pb2_grpc
from acme.patientapp.v1 import patient_home_service_pb2_grpc as patientapp_v1_patient_home_service_pb2_grpc
from acme.pipelines.v1 import pipeline_approval_service_pb2_grpc as pipelines_v1_pipeline_approval_service_pb2_grpc
from acme.pipelines.v1 import (
    pipeline_run_reporting_service_pb2_grpc as pipelines_v1_pipeline_run_reporting_service_pb2_grpc,
)
from acme.pipelines.v1 import (
    pipeline_run_workflow_service_pb2_grpc as pipelines_v1_pipeline_run_workflow_service_pb2_grpc,
)
from acme.pipelines.v1 import (
    pipeline_step_export_service_pb2_grpc as pipelines_v1_pipeline_step_export_service_pb2_grpc,
)
from acme.pipelines.v1 import (
    pipeline_step_reporting_service_pb2_grpc as pipelines_v1_pipeline_step_reporting_service_pb2_grpc,
)
from acme.pipelines.v1 import pipeline_step_sync_service_pb2_grpc as pipelines_v1_pipeline_step_sync_service_pb2_grpc
from acme.pipelines.v1 import pipeline_workflow_service_pb2_grpc as pipelines_v1_pipeline_workflow_service_pb2_grpc
from acme.pricing.v1 import price_list_query_service_pb2_grpc as pricing_v1_price_list_query_service_pb2_grpc
from acme.recommendations.v1 import (
    interaction_approval_service_pb2_grpc as recommendations_v1_interaction_approval_service_pb2_grpc,
)
from acme.recommendations.v1 import (
    interaction_workflow_service_pb2_grpc as recommendations_v1_interaction_workflow_service_pb2_grpc,
)
from acme.recommendations.v1 import (
    recommendation_model_workflow_service_pb2_grpc as recommendations_v1_recommendation_model_workflow_service_pb2_grpc,
)
from acme.search.v1 import search_index_service_pb2_grpc as search_v1_search_index_service_pb2_grpc
from acme.search.v1 import (
    search_index_validation_service_pb2_grpc as search_v1_search_index_validation_service_pb2_grpc,
)
from acme.telehealth.v1 import (
    video_visit_calculation_service_pb2_grpc as telehealth_v1_video_visit_calculation_service_pb2_grpc,
)
from acme.venues.v1 import venue_service_pb2_grpc as venues_v1_venue_service_pb2_grpc
from acme.venues.v1 import venue_validation_service_pb2_grpc as venues_v1_venue_validation_service_pb2_grpc

from acme_data.domains.datahub.data_share_approval_service import DataShareApprovalServicer
from acme_data.domains.datahub.data_share_integration_service import DataShareIntegrationServicer
from acme_data.domains.datahub.data_share_notification_service import DataShareNotificationServicer
from acme_data.domains.datahub.data_share_query_service import DataShareQueryServicer
from acme_data.domains.datahub.data_share_reporting_service import DataShareReportingServicer
from acme_data.domains.datahub.data_share_validation_service import DataShareValidationServicer
from acme_data.domains.datahub.data_share_workflow_service import DataShareWorkflowServicer
from acme_data.domains.datahub.dependencies import Clients
from acme_data.domains.datahub.dependencies import Dependencies
from acme_data.domains.datahub.events import subscribe
from acme_data.domains.datahub.notebook_approval_service import NotebookApprovalServicer
from acme_data.domains.datahub.notebook_integration_service import NotebookIntegrationServicer
from acme_data.domains.datahub.notebook_notification_service import NotebookNotificationServicer
from acme_data.domains.datahub.notebook_query_service import NotebookQueryServicer
from acme_data.domains.datahub.notebook_reporting_service import NotebookReportingServicer
from acme_data.domains.datahub.notebook_service import NotebookServicer
from acme_data.domains.datahub.notebook_workflow_service import NotebookWorkflowServicer
from acme_data.domains.datahub.repository import DomainRepository
from acme_data.domains.datahub.workspace_approval_service import WorkspaceApprovalServicer
from acme_data.domains.datahub.workspace_gateway_service import WorkspaceGatewayServicer
from acme_data.domains.datahub.workspace_integration_service import WorkspaceIntegrationServicer
from acme_data.domains.datahub.workspace_notification_service import WorkspaceNotificationServicer
from acme_data.domains.datahub.workspace_query_service import WorkspaceQueryServicer
from acme_data.domains.datahub.workspace_reporting_service import WorkspaceReportingServicer
from acme_data.domains.datahub.workspace_service import WorkspaceServicer
from acme_data.domains.datahub.workspace_workflow_service import WorkspaceWorkflowServicer
from acme_data.platform.container import Container
from acme_data.platform.container import Factory


def dependencies(container: Container) -> Dependencies:
    analytics_analytics_event_approval = container.singleton(
        analytics_v1_analytics_event_approval_service_pb2_grpc.AnalyticsEventApprovalServiceStub,
        lambda: analytics_v1_analytics_event_approval_service_pb2_grpc.AnalyticsEventApprovalServiceStub(
            container.channel
        )
    )
    analytics_analytics_report_approval = container.singleton(
        analytics_v1_analytics_report_approval_service_pb2_grpc.AnalyticsReportApprovalServiceStub,
        lambda: analytics_v1_analytics_report_approval_service_pb2_grpc.AnalyticsReportApprovalServiceStub(
            container.channel
        )
    )
    analytics_analytics_report_lifecycle = container.singleton(
        analytics_v1_analytics_report_lifecycle_service_pb2_grpc.AnalyticsReportLifecycleServiceStub,
        lambda: analytics_v1_analytics_report_lifecycle_service_pb2_grpc.AnalyticsReportLifecycleServiceStub(
            container.channel
        )
    )
    analytics_cohort_workflow = container.singleton(
        analytics_v1_cohort_workflow_service_pb2_grpc.CohortWorkflowServiceStub,
        lambda: analytics_v1_cohort_workflow_service_pb2_grpc.CohortWorkflowServiceStub(container.channel)
    )
    analytics_funnel_approval = container.singleton(
        analytics_v1_funnel_approval_service_pb2_grpc.FunnelApprovalServiceStub,
        lambda: analytics_v1_funnel_approval_service_pb2_grpc.FunnelApprovalServiceStub(container.channel)
    )
    analytics_funnel_workflow = container.singleton(
        analytics_v1_funnel_workflow_service_pb2_grpc.FunnelWorkflowServiceStub,
        lambda: analytics_v1_funnel_workflow_service_pb2_grpc.FunnelWorkflowServiceStub(container.channel)
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
    anomalies_anomaly_workflow = container.singleton(
        anomalies_v1_anomaly_workflow_service_pb2_grpc.AnomalyWorkflowServiceStub,
        lambda: anomalies_v1_anomaly_workflow_service_pb2_grpc.AnomalyWorkflowServiceStub(container.channel)
    )
    anomalies_detector_workflow = container.singleton(
        anomalies_v1_detector_workflow_service_pb2_grpc.DetectorWorkflowServiceStub,
        lambda: anomalies_v1_detector_workflow_service_pb2_grpc.DetectorWorkflowServiceStub(container.channel)
    )
    audit_audit_event_query = container.singleton(
        audit_v1_audit_event_query_service_pb2_grpc.AuditEventQueryServiceStub,
        lambda: audit_v1_audit_event_query_service_pb2_grpc.AuditEventQueryServiceStub(container.channel)
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
    customers_consent_record_approval = container.singleton(
        customers_v1_consent_record_approval_service_pb2_grpc.ConsentRecordApprovalServiceStub,
        lambda: customers_v1_consent_record_approval_service_pb2_grpc.ConsentRecordApprovalServiceStub(
            container.channel
        )
    )
    customers_consent_record_lifecycle = container.singleton(
        customers_v1_consent_record_lifecycle_service_pb2_grpc.ConsentRecordLifecycleServiceStub,
        lambda: customers_v1_consent_record_lifecycle_service_pb2_grpc.ConsentRecordLifecycleServiceStub(
            container.channel
        )
    )
    customers_consent_record_reporting = container.singleton(
        customers_v1_consent_record_reporting_service_pb2_grpc.ConsentRecordReportingServiceStub,
        lambda: customers_v1_consent_record_reporting_service_pb2_grpc.ConsentRecordReportingServiceStub(
            container.channel
        )
    )
    customers_consent_record_sync = container.singleton(
        customers_v1_consent_record_sync_service_pb2_grpc.ConsentRecordSyncServiceStub,
        lambda: customers_v1_consent_record_sync_service_pb2_grpc.ConsentRecordSyncServiceStub(container.channel)
    )
    customers_consent_record_workflow = container.singleton(
        customers_v1_consent_record_workflow_service_pb2_grpc.ConsentRecordWorkflowServiceStub,
        lambda: customers_v1_consent_record_workflow_service_pb2_grpc.ConsentRecordWorkflowServiceStub(
            container.channel
        )
    )
    customers_customer_approval = container.singleton(
        customers_v1_customer_approval_service_pb2_grpc.CustomerApprovalServiceStub,
        lambda: customers_v1_customer_approval_service_pb2_grpc.CustomerApprovalServiceStub(container.channel)
    )
    customers_customer_segment_approval = container.singleton(
        customers_v1_customer_segment_approval_service_pb2_grpc.CustomerSegmentApprovalServiceStub,
        lambda: customers_v1_customer_segment_approval_service_pb2_grpc.CustomerSegmentApprovalServiceStub(
            container.channel
        )
    )
    customers_customer_segment_import = container.singleton(
        customers_v1_customer_segment_import_service_pb2_grpc.CustomerSegmentImportServiceStub,
        lambda: customers_v1_customer_segment_import_service_pb2_grpc.CustomerSegmentImportServiceStub(
            container.channel
        )
    )
    customers_customer_segment_reporting = container.singleton(
        customers_v1_customer_segment_reporting_service_pb2_grpc.CustomerSegmentReportingServiceStub,
        lambda: customers_v1_customer_segment_reporting_service_pb2_grpc.CustomerSegmentReportingServiceStub(
            container.channel
        )
    )
    customers_customer_segment_sync = container.singleton(
        customers_v1_customer_segment_sync_service_pb2_grpc.CustomerSegmentSyncServiceStub,
        lambda: customers_v1_customer_segment_sync_service_pb2_grpc.CustomerSegmentSyncServiceStub(container.channel)
    )
    customers_customer_workflow = container.singleton(
        customers_v1_customer_workflow_service_pb2_grpc.CustomerWorkflowServiceStub,
        lambda: customers_v1_customer_workflow_service_pb2_grpc.CustomerWorkflowServiceStub(container.channel)
    )
    customers_household_approval = container.singleton(
        customers_v1_household_approval_service_pb2_grpc.HouseholdApprovalServiceStub,
        lambda: customers_v1_household_approval_service_pb2_grpc.HouseholdApprovalServiceStub(container.channel)
    )
    customers_household_reporting = container.singleton(
        customers_v1_household_reporting_service_pb2_grpc.HouseholdReportingServiceStub,
        lambda: customers_v1_household_reporting_service_pb2_grpc.HouseholdReportingServiceStub(container.channel)
    )
    customers_household_workflow = container.singleton(
        customers_v1_household_workflow_service_pb2_grpc.HouseholdWorkflowServiceStub,
        lambda: customers_v1_household_workflow_service_pb2_grpc.HouseholdWorkflowServiceStub(container.channel)
    )
    customers_preference_calculation = container.singleton(
        customers_v1_preference_calculation_service_pb2_grpc.PreferenceCalculationServiceStub,
        lambda: customers_v1_preference_calculation_service_pb2_grpc.PreferenceCalculationServiceStub(container.channel)
    )
    customers_preference_import = container.singleton(
        customers_v1_preference_import_service_pb2_grpc.PreferenceImportServiceStub,
        lambda: customers_v1_preference_import_service_pb2_grpc.PreferenceImportServiceStub(container.channel)
    )
    customers_preference_lifecycle = container.singleton(
        customers_v1_preference_lifecycle_service_pb2_grpc.PreferenceLifecycleServiceStub,
        lambda: customers_v1_preference_lifecycle_service_pb2_grpc.PreferenceLifecycleServiceStub(container.channel)
    )
    customers_preference_reporting = container.singleton(
        customers_v1_preference_reporting_service_pb2_grpc.PreferenceReportingServiceStub,
        lambda: customers_v1_preference_reporting_service_pb2_grpc.PreferenceReportingServiceStub(container.channel)
    )
    customers_preference_sync = container.singleton(
        customers_v1_preference_sync_service_pb2_grpc.PreferenceSyncServiceStub,
        lambda: customers_v1_preference_sync_service_pb2_grpc.PreferenceSyncServiceStub(container.channel)
    )
    datahub_data_share_approval = container.singleton(
        datahub_v1_data_share_approval_service_pb2_grpc.DataShareApprovalServiceStub,
        lambda: datahub_v1_data_share_approval_service_pb2_grpc.DataShareApprovalServiceStub(container.channel)
    )
    datahub_data_share_query = container.singleton(
        datahub_v1_data_share_query_service_pb2_grpc.DataShareQueryServiceStub,
        lambda: datahub_v1_data_share_query_service_pb2_grpc.DataShareQueryServiceStub(container.channel)
    )
    datahub_data_share_reporting = container.singleton(
        datahub_v1_data_share_reporting_service_pb2_grpc.DataShareReportingServiceStub,
        lambda: datahub_v1_data_share_reporting_service_pb2_grpc.DataShareReportingServiceStub(container.channel)
    )
    datahub_data_share_validation = container.singleton(
        datahub_v1_data_share_validation_service_pb2_grpc.DataShareValidationServiceStub,
        lambda: datahub_v1_data_share_validation_service_pb2_grpc.DataShareValidationServiceStub(container.channel)
    )
    datahub_data_share_workflow = container.singleton(
        datahub_v1_data_share_workflow_service_pb2_grpc.DataShareWorkflowServiceStub,
        lambda: datahub_v1_data_share_workflow_service_pb2_grpc.DataShareWorkflowServiceStub(container.channel)
    )
    datahub_notebook_approval = container.singleton(
        datahub_v1_notebook_approval_service_pb2_grpc.NotebookApprovalServiceStub,
        lambda: datahub_v1_notebook_approval_service_pb2_grpc.NotebookApprovalServiceStub(container.channel)
    )
    datahub_notebook_integration = container.singleton(
        datahub_v1_notebook_integration_service_pb2_grpc.NotebookIntegrationServiceStub,
        lambda: datahub_v1_notebook_integration_service_pb2_grpc.NotebookIntegrationServiceStub(container.channel)
    )
    datahub_notebook_notification = container.singleton(
        datahub_v1_notebook_notification_service_pb2_grpc.NotebookNotificationServiceStub,
        lambda: datahub_v1_notebook_notification_service_pb2_grpc.NotebookNotificationServiceStub(container.channel)
    )
    datahub_notebook_reporting = container.singleton(
        datahub_v1_notebook_reporting_service_pb2_grpc.NotebookReportingServiceStub,
        lambda: datahub_v1_notebook_reporting_service_pb2_grpc.NotebookReportingServiceStub(container.channel)
    )
    datahub_notebook_workflow = container.singleton(
        datahub_v1_notebook_workflow_service_pb2_grpc.NotebookWorkflowServiceStub,
        lambda: datahub_v1_notebook_workflow_service_pb2_grpc.NotebookWorkflowServiceStub(container.channel)
    )
    datahub_workspace_approval = container.singleton(
        datahub_v1_workspace_approval_service_pb2_grpc.WorkspaceApprovalServiceStub,
        lambda: datahub_v1_workspace_approval_service_pb2_grpc.WorkspaceApprovalServiceStub(container.channel)
    )
    datahub_workspace_integration = container.singleton(
        datahub_v1_workspace_integration_service_pb2_grpc.WorkspaceIntegrationServiceStub,
        lambda: datahub_v1_workspace_integration_service_pb2_grpc.WorkspaceIntegrationServiceStub(container.channel)
    )
    datahub_workspace_notification = container.singleton(
        datahub_v1_workspace_notification_service_pb2_grpc.WorkspaceNotificationServiceStub,
        lambda: datahub_v1_workspace_notification_service_pb2_grpc.WorkspaceNotificationServiceStub(container.channel)
    )
    datahub_workspace_reporting = container.singleton(
        datahub_v1_workspace_reporting_service_pb2_grpc.WorkspaceReportingServiceStub,
        lambda: datahub_v1_workspace_reporting_service_pb2_grpc.WorkspaceReportingServiceStub(container.channel)
    )
    datahub_workspace_workflow = container.singleton(
        datahub_v1_workspace_workflow_service_pb2_grpc.WorkspaceWorkflowServiceStub,
        lambda: datahub_v1_workspace_workflow_service_pb2_grpc.WorkspaceWorkflowServiceStub(container.channel)
    )
    datasets_data_schema_approval = container.singleton(
        datasets_v1_data_schema_approval_service_pb2_grpc.DataSchemaApprovalServiceStub,
        lambda: datasets_v1_data_schema_approval_service_pb2_grpc.DataSchemaApprovalServiceStub(container.channel)
    )
    datasets_dataset_approval = container.singleton(
        datasets_v1_dataset_approval_service_pb2_grpc.DatasetApprovalServiceStub,
        lambda: datasets_v1_dataset_approval_service_pb2_grpc.DatasetApprovalServiceStub(container.channel)
    )
    datasets_dataset_workflow = container.singleton(
        datasets_v1_dataset_workflow_service_pb2_grpc.DatasetWorkflowServiceStub,
        lambda: datasets_v1_dataset_workflow_service_pb2_grpc.DatasetWorkflowServiceStub(container.channel)
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
    driverapp_driver_home_query = container.singleton(
        driverapp_v1_driver_home_query_service_pb2_grpc.DriverHomeQueryServiceStub,
        lambda: driverapp_v1_driver_home_query_service_pb2_grpc.DriverHomeQueryServiceStub(container.channel)
    )
    driverapp_driver_home = container.singleton(
        driverapp_v1_driver_home_service_pb2_grpc.DriverHomeServiceStub,
        lambda: driverapp_v1_driver_home_service_pb2_grpc.DriverHomeServiceStub(container.channel)
    )
    edgegateway_route_binding_query = container.singleton(
        edgegateway_v1_route_binding_query_service_pb2_grpc.RouteBindingQueryServiceStub,
        lambda: edgegateway_v1_route_binding_query_service_pb2_grpc.RouteBindingQueryServiceStub(container.channel)
    )
    edgegateway_route_binding = container.singleton(
        edgegateway_v1_route_binding_service_pb2_grpc.RouteBindingServiceStub,
        lambda: edgegateway_v1_route_binding_service_pb2_grpc.RouteBindingServiceStub(container.channel)
    )
    fanportal_fan_session_query = container.singleton(
        fanportal_v1_fan_session_query_service_pb2_grpc.FanSessionQueryServiceStub,
        lambda: fanportal_v1_fan_session_query_service_pb2_grpc.FanSessionQueryServiceStub(container.channel)
    )
    fanportal_fan_session = container.singleton(
        fanportal_v1_fan_session_service_pb2_grpc.FanSessionServiceStub,
        lambda: fanportal_v1_fan_session_service_pb2_grpc.FanSessionServiceStub(container.channel)
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
    featurestore_entity_import = container.singleton(
        featurestore_v1_entity_import_service_pb2_grpc.EntityImportServiceStub,
        lambda: featurestore_v1_entity_import_service_pb2_grpc.EntityImportServiceStub(container.channel)
    )
    featurestore_entity_reporting = container.singleton(
        featurestore_v1_entity_reporting_service_pb2_grpc.EntityReportingServiceStub,
        lambda: featurestore_v1_entity_reporting_service_pb2_grpc.EntityReportingServiceStub(container.channel)
    )
    featurestore_feature_value_reporting = container.singleton(
        featurestore_v1_feature_value_reporting_service_pb2_grpc.FeatureValueReportingServiceStub,
        lambda: featurestore_v1_feature_value_reporting_service_pb2_grpc.FeatureValueReportingServiceStub(
            container.channel
        )
    )
    featurestore_feature_value_workflow = container.singleton(
        featurestore_v1_feature_value_workflow_service_pb2_grpc.FeatureValueWorkflowServiceStub,
        lambda: featurestore_v1_feature_value_workflow_service_pb2_grpc.FeatureValueWorkflowServiceStub(
            container.channel
        )
    )
    featurestore_feature_view_sync = container.singleton(
        featurestore_v1_feature_view_sync_service_pb2_grpc.FeatureViewSyncServiceStub,
        lambda: featurestore_v1_feature_view_sync_service_pb2_grpc.FeatureViewSyncServiceStub(container.channel)
    )
    featurestore_feature_view_workflow = container.singleton(
        featurestore_v1_feature_view_workflow_service_pb2_grpc.FeatureViewWorkflowServiceStub,
        lambda: featurestore_v1_feature_view_workflow_service_pb2_grpc.FeatureViewWorkflowServiceStub(container.channel)
    )
    forecasting_demand_forecast_approval = container.singleton(
        forecasting_v1_demand_forecast_approval_service_pb2_grpc.DemandForecastApprovalServiceStub,
        lambda: forecasting_v1_demand_forecast_approval_service_pb2_grpc.DemandForecastApprovalServiceStub(
            container.channel
        )
    )
    forecasting_demand_forecast_workflow = container.singleton(
        forecasting_v1_demand_forecast_workflow_service_pb2_grpc.DemandForecastWorkflowServiceStub,
        lambda: forecasting_v1_demand_forecast_workflow_service_pb2_grpc.DemandForecastWorkflowServiceStub(
            container.channel
        )
    )
    forecasting_scenario_workflow = container.singleton(
        forecasting_v1_scenario_workflow_service_pb2_grpc.ScenarioWorkflowServiceStub,
        lambda: forecasting_v1_scenario_workflow_service_pb2_grpc.ScenarioWorkflowServiceStub(container.channel)
    )
    identity_user_query = container.singleton(
        identity_v1_user_query_service_pb2_grpc.UserQueryServiceStub,
        lambda: identity_v1_user_query_service_pb2_grpc.UserQueryServiceStub(container.channel)
    )
    identity_user_validation = container.singleton(
        identity_v1_user_validation_service_pb2_grpc.UserValidationServiceStub,
        lambda: identity_v1_user_validation_service_pb2_grpc.UserValidationServiceStub(container.channel)
    )
    itsm_incident = container.singleton(
        itsm_v1_incident_service_pb2_grpc.IncidentServiceStub,
        lambda: itsm_v1_incident_service_pb2_grpc.IncidentServiceStub(container.channel)
    )
    labeling_annotation_approval = container.singleton(
        labeling_v1_annotation_approval_service_pb2_grpc.AnnotationApprovalServiceStub,
        lambda: labeling_v1_annotation_approval_service_pb2_grpc.AnnotationApprovalServiceStub(container.channel)
    )
    labeling_label_set_approval = container.singleton(
        labeling_v1_label_set_approval_service_pb2_grpc.LabelSetApprovalServiceStub,
        lambda: labeling_v1_label_set_approval_service_pb2_grpc.LabelSetApprovalServiceStub(container.channel)
    )
    labeling_label_set_reporting = container.singleton(
        labeling_v1_label_set_reporting_service_pb2_grpc.LabelSetReportingServiceStub,
        lambda: labeling_v1_label_set_reporting_service_pb2_grpc.LabelSetReportingServiceStub(container.channel)
    )
    labeling_labeling_task_approval = container.singleton(
        labeling_v1_labeling_task_approval_service_pb2_grpc.LabelingTaskApprovalServiceStub,
        lambda: labeling_v1_labeling_task_approval_service_pb2_grpc.LabelingTaskApprovalServiceStub(container.channel)
    )
    labeling_labeling_task_workflow = container.singleton(
        labeling_v1_labeling_task_workflow_service_pb2_grpc.LabelingTaskWorkflowServiceStub,
        lambda: labeling_v1_labeling_task_workflow_service_pb2_grpc.LabelingTaskWorkflowServiceStub(container.channel)
    )
    learning_course_query = container.singleton(
        learning_v1_course_query_service_pb2_grpc.CourseQueryServiceStub,
        lambda: learning_v1_course_query_service_pb2_grpc.CourseQueryServiceStub(container.channel)
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
    lineage_impact_workflow = container.singleton(
        lineage_v1_impact_workflow_service_pb2_grpc.ImpactWorkflowServiceStub,
        lambda: lineage_v1_impact_workflow_service_pb2_grpc.ImpactWorkflowServiceStub(container.channel)
    )
    lineage_lineage_edge_workflow = container.singleton(
        lineage_v1_lineage_edge_workflow_service_pb2_grpc.LineageEdgeWorkflowServiceStub,
        lambda: lineage_v1_lineage_edge_workflow_service_pb2_grpc.LineageEdgeWorkflowServiceStub(container.channel)
    )
    lineage_lineage_node_workflow = container.singleton(
        lineage_v1_lineage_node_workflow_service_pb2_grpc.LineageNodeWorkflowServiceStub,
        lambda: lineage_v1_lineage_node_workflow_service_pb2_grpc.LineageNodeWorkflowServiceStub(container.channel)
    )
    metrics_dashboard_history = container.singleton(
        metrics_v1_dashboard_history_service_pb2_grpc.DashboardHistoryServiceStub,
        lambda: metrics_v1_dashboard_history_service_pb2_grpc.DashboardHistoryServiceStub(container.channel)
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
    modelregistry_deployment_approval = container.singleton(
        modelregistry_v1_deployment_approval_service_pb2_grpc.DeploymentApprovalServiceStub,
        lambda: modelregistry_v1_deployment_approval_service_pb2_grpc.DeploymentApprovalServiceStub(container.channel)
    )
    modelregistry_deployment_import = container.singleton(
        modelregistry_v1_deployment_import_service_pb2_grpc.DeploymentImportServiceStub,
        lambda: modelregistry_v1_deployment_import_service_pb2_grpc.DeploymentImportServiceStub(container.channel)
    )
    modelregistry_deployment_sync = container.singleton(
        modelregistry_v1_deployment_sync_service_pb2_grpc.DeploymentSyncServiceStub,
        lambda: modelregistry_v1_deployment_sync_service_pb2_grpc.DeploymentSyncServiceStub(container.channel)
    )
    modelregistry_model_version_approval = container.singleton(
        modelregistry_v1_model_version_approval_service_pb2_grpc.ModelVersionApprovalServiceStub,
        lambda: modelregistry_v1_model_version_approval_service_pb2_grpc.ModelVersionApprovalServiceStub(
            container.channel
        )
    )
    modelregistry_model_version_reporting = container.singleton(
        modelregistry_v1_model_version_reporting_service_pb2_grpc.ModelVersionReportingServiceStub,
        lambda: modelregistry_v1_model_version_reporting_service_pb2_grpc.ModelVersionReportingServiceStub(
            container.channel
        )
    )
    modelregistry_registered_model_lifecycle = container.singleton(
        modelregistry_v1_registered_model_lifecycle_service_pb2_grpc.RegisteredModelLifecycleServiceStub,
        lambda: modelregistry_v1_registered_model_lifecycle_service_pb2_grpc.RegisteredModelLifecycleServiceStub(
            container.channel
        )
    )
    modelregistry_registered_model_reporting = container.singleton(
        modelregistry_v1_registered_model_reporting_service_pb2_grpc.RegisteredModelReportingServiceStub,
        lambda: modelregistry_v1_registered_model_reporting_service_pb2_grpc.RegisteredModelReportingServiceStub(
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
    patientapp_patient_home_query = container.singleton(
        patientapp_v1_patient_home_query_service_pb2_grpc.PatientHomeQueryServiceStub,
        lambda: patientapp_v1_patient_home_query_service_pb2_grpc.PatientHomeQueryServiceStub(container.channel)
    )
    patientapp_patient_home = container.singleton(
        patientapp_v1_patient_home_service_pb2_grpc.PatientHomeServiceStub,
        lambda: patientapp_v1_patient_home_service_pb2_grpc.PatientHomeServiceStub(container.channel)
    )
    pipelines_pipeline_approval = container.singleton(
        pipelines_v1_pipeline_approval_service_pb2_grpc.PipelineApprovalServiceStub,
        lambda: pipelines_v1_pipeline_approval_service_pb2_grpc.PipelineApprovalServiceStub(container.channel)
    )
    pipelines_pipeline_run_reporting = container.singleton(
        pipelines_v1_pipeline_run_reporting_service_pb2_grpc.PipelineRunReportingServiceStub,
        lambda: pipelines_v1_pipeline_run_reporting_service_pb2_grpc.PipelineRunReportingServiceStub(container.channel)
    )
    pipelines_pipeline_run_workflow = container.singleton(
        pipelines_v1_pipeline_run_workflow_service_pb2_grpc.PipelineRunWorkflowServiceStub,
        lambda: pipelines_v1_pipeline_run_workflow_service_pb2_grpc.PipelineRunWorkflowServiceStub(container.channel)
    )
    pipelines_pipeline_step_export = container.singleton(
        pipelines_v1_pipeline_step_export_service_pb2_grpc.PipelineStepExportServiceStub,
        lambda: pipelines_v1_pipeline_step_export_service_pb2_grpc.PipelineStepExportServiceStub(container.channel)
    )
    pipelines_pipeline_step_reporting = container.singleton(
        pipelines_v1_pipeline_step_reporting_service_pb2_grpc.PipelineStepReportingServiceStub,
        lambda: pipelines_v1_pipeline_step_reporting_service_pb2_grpc.PipelineStepReportingServiceStub(
            container.channel
        )
    )
    pipelines_pipeline_step_sync = container.singleton(
        pipelines_v1_pipeline_step_sync_service_pb2_grpc.PipelineStepSyncServiceStub,
        lambda: pipelines_v1_pipeline_step_sync_service_pb2_grpc.PipelineStepSyncServiceStub(container.channel)
    )
    pipelines_pipeline_workflow = container.singleton(
        pipelines_v1_pipeline_workflow_service_pb2_grpc.PipelineWorkflowServiceStub,
        lambda: pipelines_v1_pipeline_workflow_service_pb2_grpc.PipelineWorkflowServiceStub(container.channel)
    )
    pricing_price_list_query = container.singleton(
        pricing_v1_price_list_query_service_pb2_grpc.PriceListQueryServiceStub,
        lambda: pricing_v1_price_list_query_service_pb2_grpc.PriceListQueryServiceStub(container.channel)
    )
    recommendations_interaction_approval = container.singleton(
        recommendations_v1_interaction_approval_service_pb2_grpc.InteractionApprovalServiceStub,
        lambda: recommendations_v1_interaction_approval_service_pb2_grpc.InteractionApprovalServiceStub(
            container.channel
        )
    )
    recommendations_interaction_workflow = container.singleton(
        recommendations_v1_interaction_workflow_service_pb2_grpc.InteractionWorkflowServiceStub,
        lambda: recommendations_v1_interaction_workflow_service_pb2_grpc.InteractionWorkflowServiceStub(
            container.channel
        )
    )
    recommendations_recommendation_model_workflow = container.singleton(
        recommendations_v1_recommendation_model_workflow_service_pb2_grpc.RecommendationModelWorkflowServiceStub,
        lambda: recommendations_v1_recommendation_model_workflow_service_pb2_grpc.RecommendationModelWorkflowServiceStub(
            container.channel
        )
    )
    search_search_index = container.singleton(
        search_v1_search_index_service_pb2_grpc.SearchIndexServiceStub,
        lambda: search_v1_search_index_service_pb2_grpc.SearchIndexServiceStub(container.channel)
    )
    search_search_index_validation = container.singleton(
        search_v1_search_index_validation_service_pb2_grpc.SearchIndexValidationServiceStub,
        lambda: search_v1_search_index_validation_service_pb2_grpc.SearchIndexValidationServiceStub(container.channel)
    )
    telehealth_video_visit_calculation = container.singleton(
        telehealth_v1_video_visit_calculation_service_pb2_grpc.VideoVisitCalculationServiceStub,
        lambda: telehealth_v1_video_visit_calculation_service_pb2_grpc.VideoVisitCalculationServiceStub(
            container.channel
        )
    )
    venues_venue = container.singleton(
        venues_v1_venue_service_pb2_grpc.VenueServiceStub,
        lambda: venues_v1_venue_service_pb2_grpc.VenueServiceStub(container.channel)
    )
    venues_venue_validation = container.singleton(
        venues_v1_venue_validation_service_pb2_grpc.VenueValidationServiceStub,
        lambda: venues_v1_venue_validation_service_pb2_grpc.VenueValidationServiceStub(container.channel)
    )
    clients = Clients(
        analytics_analytics_event_approval=analytics_analytics_event_approval,
        analytics_analytics_report_approval=analytics_analytics_report_approval,
        analytics_analytics_report_lifecycle=analytics_analytics_report_lifecycle,
        analytics_cohort_workflow=analytics_cohort_workflow,
        analytics_funnel_approval=analytics_funnel_approval,
        analytics_funnel_workflow=analytics_funnel_workflow,
        anomalies_anomaly_approval=anomalies_anomaly_approval,
        anomalies_anomaly_feedback_approval=anomalies_anomaly_feedback_approval,
        anomalies_anomaly_workflow=anomalies_anomaly_workflow,
        anomalies_detector_workflow=anomalies_detector_workflow,
        audit_audit_event_query=audit_audit_event_query,
        audit_audit_event_validation=audit_audit_event_validation,
        authorization_access_policy=authorization_access_policy,
        authorization_access_policy_validation=authorization_access_policy_validation,
        billing_billing_account_query=billing_billing_account_query,
        customers_consent_record_approval=customers_consent_record_approval,
        customers_consent_record_lifecycle=customers_consent_record_lifecycle,
        customers_consent_record_reporting=customers_consent_record_reporting,
        customers_consent_record_sync=customers_consent_record_sync,
        customers_consent_record_workflow=customers_consent_record_workflow,
        customers_customer_approval=customers_customer_approval,
        customers_customer_segment_approval=customers_customer_segment_approval,
        customers_customer_segment_import=customers_customer_segment_import,
        customers_customer_segment_reporting=customers_customer_segment_reporting,
        customers_customer_segment_sync=customers_customer_segment_sync,
        customers_customer_workflow=customers_customer_workflow,
        customers_household_approval=customers_household_approval,
        customers_household_reporting=customers_household_reporting,
        customers_household_workflow=customers_household_workflow,
        customers_preference_calculation=customers_preference_calculation,
        customers_preference_import=customers_preference_import,
        customers_preference_lifecycle=customers_preference_lifecycle,
        customers_preference_reporting=customers_preference_reporting,
        customers_preference_sync=customers_preference_sync,
        datahub_data_share_approval=datahub_data_share_approval,
        datahub_data_share_query=datahub_data_share_query,
        datahub_data_share_reporting=datahub_data_share_reporting,
        datahub_data_share_validation=datahub_data_share_validation,
        datahub_data_share_workflow=datahub_data_share_workflow,
        datahub_notebook_approval=datahub_notebook_approval,
        datahub_notebook_integration=datahub_notebook_integration,
        datahub_notebook_notification=datahub_notebook_notification,
        datahub_notebook_reporting=datahub_notebook_reporting,
        datahub_notebook_workflow=datahub_notebook_workflow,
        datahub_workspace_approval=datahub_workspace_approval,
        datahub_workspace_integration=datahub_workspace_integration,
        datahub_workspace_notification=datahub_workspace_notification,
        datahub_workspace_reporting=datahub_workspace_reporting,
        datahub_workspace_workflow=datahub_workspace_workflow,
        datasets_data_schema_approval=datasets_data_schema_approval,
        datasets_dataset_approval=datasets_dataset_approval,
        datasets_dataset_workflow=datasets_dataset_workflow,
        documents_document_query=documents_document_query,
        documents_document=documents_document,
        documents_document_validation=documents_document_validation,
        driverapp_driver_home_query=driverapp_driver_home_query,
        driverapp_driver_home=driverapp_driver_home,
        edgegateway_route_binding_query=edgegateway_route_binding_query,
        edgegateway_route_binding=edgegateway_route_binding,
        fanportal_fan_session_query=fanportal_fan_session_query,
        fanportal_fan_session=fanportal_fan_session,
        featureflags_feature_flag_query=featureflags_feature_flag_query,
        featureflags_feature_flag=featureflags_feature_flag,
        featureflags_feature_flag_validation=featureflags_feature_flag_validation,
        featurestore_entity_import=featurestore_entity_import,
        featurestore_entity_reporting=featurestore_entity_reporting,
        featurestore_feature_value_reporting=featurestore_feature_value_reporting,
        featurestore_feature_value_workflow=featurestore_feature_value_workflow,
        featurestore_feature_view_sync=featurestore_feature_view_sync,
        featurestore_feature_view_workflow=featurestore_feature_view_workflow,
        forecasting_demand_forecast_approval=forecasting_demand_forecast_approval,
        forecasting_demand_forecast_workflow=forecasting_demand_forecast_workflow,
        forecasting_scenario_workflow=forecasting_scenario_workflow,
        identity_user_query=identity_user_query,
        identity_user_validation=identity_user_validation,
        itsm_incident=itsm_incident,
        labeling_annotation_approval=labeling_annotation_approval,
        labeling_label_set_approval=labeling_label_set_approval,
        labeling_label_set_reporting=labeling_label_set_reporting,
        labeling_labeling_task_approval=labeling_labeling_task_approval,
        labeling_labeling_task_workflow=labeling_labeling_task_workflow,
        learning_course_query=learning_course_query,
        ledger_ledger_account_query=ledger_ledger_account_query,
        ledger_ledger_account=ledger_ledger_account,
        lineage_impact_approval=lineage_impact_approval,
        lineage_impact_workflow=lineage_impact_workflow,
        lineage_lineage_edge_workflow=lineage_lineage_edge_workflow,
        lineage_lineage_node_workflow=lineage_lineage_node_workflow,
        metrics_dashboard_history=metrics_dashboard_history,
        metrics_dashboard_notification=metrics_dashboard_notification,
        metrics_dashboard_sync=metrics_dashboard_sync,
        metrics_dashboard_validation=metrics_dashboard_validation,
        metrics_metric_alert_history=metrics_metric_alert_history,
        metrics_metric_alert_notification=metrics_metric_alert_notification,
        metrics_metric_alert_validation=metrics_metric_alert_validation,
        metrics_metric_series_admin=metrics_metric_series_admin,
        metrics_metric_series_export=metrics_metric_series_export,
        metrics_metric_series_history=metrics_metric_series_history,
        metrics_metric_series_notification=metrics_metric_series_notification,
        metrics_metric_series_query=metrics_metric_series_query,
        metrics_metric_series=metrics_metric_series,
        metrics_metric_series_validation=metrics_metric_series_validation,
        modelregistry_deployment_approval=modelregistry_deployment_approval,
        modelregistry_deployment_import=modelregistry_deployment_import,
        modelregistry_deployment_sync=modelregistry_deployment_sync,
        modelregistry_model_version_approval=modelregistry_model_version_approval,
        modelregistry_model_version_reporting=modelregistry_model_version_reporting,
        modelregistry_registered_model_lifecycle=modelregistry_registered_model_lifecycle,
        modelregistry_registered_model_reporting=modelregistry_registered_model_reporting,
        notifications_notification_query=notifications_notification_query,
        notifications_notification=notifications_notification,
        notifications_notification_validation=notifications_notification_validation,
        patientapp_patient_home_query=patientapp_patient_home_query,
        patientapp_patient_home=patientapp_patient_home,
        pipelines_pipeline_approval=pipelines_pipeline_approval,
        pipelines_pipeline_run_reporting=pipelines_pipeline_run_reporting,
        pipelines_pipeline_run_workflow=pipelines_pipeline_run_workflow,
        pipelines_pipeline_step_export=pipelines_pipeline_step_export,
        pipelines_pipeline_step_reporting=pipelines_pipeline_step_reporting,
        pipelines_pipeline_step_sync=pipelines_pipeline_step_sync,
        pipelines_pipeline_workflow=pipelines_pipeline_workflow,
        pricing_price_list_query=pricing_price_list_query,
        recommendations_interaction_approval=recommendations_interaction_approval,
        recommendations_interaction_workflow=recommendations_interaction_workflow,
        recommendations_recommendation_model_workflow=recommendations_recommendation_model_workflow,
        search_search_index=search_search_index,
        search_search_index_validation=search_search_index_validation,
        telehealth_video_visit_calculation=telehealth_video_visit_calculation,
        venues_venue=venues_venue,
        venues_venue_validation=venues_venue_validation,
        registry={
            'acme.analytics.v1.AnalyticsEventApprovalService': analytics_analytics_event_approval,
            'acme.analytics.v1.AnalyticsReportApprovalService': analytics_analytics_report_approval,
            'acme.analytics.v1.AnalyticsReportLifecycleService': analytics_analytics_report_lifecycle,
            'acme.analytics.v1.CohortWorkflowService': analytics_cohort_workflow,
            'acme.analytics.v1.FunnelApprovalService': analytics_funnel_approval,
            'acme.analytics.v1.FunnelWorkflowService': analytics_funnel_workflow,
            'acme.anomalies.v1.AnomalyApprovalService': anomalies_anomaly_approval,
            'acme.anomalies.v1.AnomalyFeedbackApprovalService': anomalies_anomaly_feedback_approval,
            'acme.anomalies.v1.AnomalyWorkflowService': anomalies_anomaly_workflow,
            'acme.anomalies.v1.DetectorWorkflowService': anomalies_detector_workflow,
            'acme.audit.v1.AuditEventQueryService': audit_audit_event_query,
            'acme.audit.v1.AuditEventValidationService': audit_audit_event_validation,
            'acme.authorization.v1.AccessPolicyService': authorization_access_policy,
            'acme.authorization.v1.AccessPolicyValidationService': authorization_access_policy_validation,
            'acme.billing.v1.BillingAccountQueryService': billing_billing_account_query,
            'acme.customers.v1.ConsentRecordApprovalService': customers_consent_record_approval,
            'acme.customers.v1.ConsentRecordLifecycleService': customers_consent_record_lifecycle,
            'acme.customers.v1.ConsentRecordReportingService': customers_consent_record_reporting,
            'acme.customers.v1.ConsentRecordSyncService': customers_consent_record_sync,
            'acme.customers.v1.ConsentRecordWorkflowService': customers_consent_record_workflow,
            'acme.customers.v1.CustomerApprovalService': customers_customer_approval,
            'acme.customers.v1.CustomerSegmentApprovalService': customers_customer_segment_approval,
            'acme.customers.v1.CustomerSegmentImportService': customers_customer_segment_import,
            'acme.customers.v1.CustomerSegmentReportingService': customers_customer_segment_reporting,
            'acme.customers.v1.CustomerSegmentSyncService': customers_customer_segment_sync,
            'acme.customers.v1.CustomerWorkflowService': customers_customer_workflow,
            'acme.customers.v1.HouseholdApprovalService': customers_household_approval,
            'acme.customers.v1.HouseholdReportingService': customers_household_reporting,
            'acme.customers.v1.HouseholdWorkflowService': customers_household_workflow,
            'acme.customers.v1.PreferenceCalculationService': customers_preference_calculation,
            'acme.customers.v1.PreferenceImportService': customers_preference_import,
            'acme.customers.v1.PreferenceLifecycleService': customers_preference_lifecycle,
            'acme.customers.v1.PreferenceReportingService': customers_preference_reporting,
            'acme.customers.v1.PreferenceSyncService': customers_preference_sync,
            'acme.datahub.v1.DataShareApprovalService': datahub_data_share_approval,
            'acme.datahub.v1.DataShareQueryService': datahub_data_share_query,
            'acme.datahub.v1.DataShareReportingService': datahub_data_share_reporting,
            'acme.datahub.v1.DataShareValidationService': datahub_data_share_validation,
            'acme.datahub.v1.DataShareWorkflowService': datahub_data_share_workflow,
            'acme.datahub.v1.NotebookApprovalService': datahub_notebook_approval,
            'acme.datahub.v1.NotebookIntegrationService': datahub_notebook_integration,
            'acme.datahub.v1.NotebookNotificationService': datahub_notebook_notification,
            'acme.datahub.v1.NotebookReportingService': datahub_notebook_reporting,
            'acme.datahub.v1.NotebookWorkflowService': datahub_notebook_workflow,
            'acme.datahub.v1.WorkspaceApprovalService': datahub_workspace_approval,
            'acme.datahub.v1.WorkspaceIntegrationService': datahub_workspace_integration,
            'acme.datahub.v1.WorkspaceNotificationService': datahub_workspace_notification,
            'acme.datahub.v1.WorkspaceReportingService': datahub_workspace_reporting,
            'acme.datahub.v1.WorkspaceWorkflowService': datahub_workspace_workflow,
            'acme.datasets.v1.DataSchemaApprovalService': datasets_data_schema_approval,
            'acme.datasets.v1.DatasetApprovalService': datasets_dataset_approval,
            'acme.datasets.v1.DatasetWorkflowService': datasets_dataset_workflow,
            'acme.documents.v1.DocumentQueryService': documents_document_query,
            'acme.documents.v1.DocumentService': documents_document,
            'acme.documents.v1.DocumentValidationService': documents_document_validation,
            'acme.driverapp.v1.DriverHomeQueryService': driverapp_driver_home_query,
            'acme.driverapp.v1.DriverHomeService': driverapp_driver_home,
            'acme.edgegateway.v1.RouteBindingQueryService': edgegateway_route_binding_query,
            'acme.edgegateway.v1.RouteBindingService': edgegateway_route_binding,
            'acme.fanportal.v1.FanSessionQueryService': fanportal_fan_session_query,
            'acme.fanportal.v1.FanSessionService': fanportal_fan_session,
            'acme.featureflags.v1.FeatureFlagQueryService': featureflags_feature_flag_query,
            'acme.featureflags.v1.FeatureFlagService': featureflags_feature_flag,
            'acme.featureflags.v1.FeatureFlagValidationService': featureflags_feature_flag_validation,
            'acme.featurestore.v1.EntityImportService': featurestore_entity_import,
            'acme.featurestore.v1.EntityReportingService': featurestore_entity_reporting,
            'acme.featurestore.v1.FeatureValueReportingService': featurestore_feature_value_reporting,
            'acme.featurestore.v1.FeatureValueWorkflowService': featurestore_feature_value_workflow,
            'acme.featurestore.v1.FeatureViewSyncService': featurestore_feature_view_sync,
            'acme.featurestore.v1.FeatureViewWorkflowService': featurestore_feature_view_workflow,
            'acme.forecasting.v1.DemandForecastApprovalService': forecasting_demand_forecast_approval,
            'acme.forecasting.v1.DemandForecastWorkflowService': forecasting_demand_forecast_workflow,
            'acme.forecasting.v1.ScenarioWorkflowService': forecasting_scenario_workflow,
            'acme.identity.v1.UserQueryService': identity_user_query,
            'acme.identity.v1.UserValidationService': identity_user_validation,
            'acme.itsm.v1.IncidentService': itsm_incident,
            'acme.labeling.v1.AnnotationApprovalService': labeling_annotation_approval,
            'acme.labeling.v1.LabelSetApprovalService': labeling_label_set_approval,
            'acme.labeling.v1.LabelSetReportingService': labeling_label_set_reporting,
            'acme.labeling.v1.LabelingTaskApprovalService': labeling_labeling_task_approval,
            'acme.labeling.v1.LabelingTaskWorkflowService': labeling_labeling_task_workflow,
            'acme.learning.v1.CourseQueryService': learning_course_query,
            'acme.ledger.v1.LedgerAccountQueryService': ledger_ledger_account_query,
            'acme.ledger.v1.LedgerAccountService': ledger_ledger_account,
            'acme.lineage.v1.ImpactApprovalService': lineage_impact_approval,
            'acme.lineage.v1.ImpactWorkflowService': lineage_impact_workflow,
            'acme.lineage.v1.LineageEdgeWorkflowService': lineage_lineage_edge_workflow,
            'acme.lineage.v1.LineageNodeWorkflowService': lineage_lineage_node_workflow,
            'acme.metrics.v1.DashboardHistoryService': metrics_dashboard_history,
            'acme.metrics.v1.DashboardNotificationService': metrics_dashboard_notification,
            'acme.metrics.v1.DashboardSyncService': metrics_dashboard_sync,
            'acme.metrics.v1.DashboardValidationService': metrics_dashboard_validation,
            'acme.metrics.v1.MetricAlertHistoryService': metrics_metric_alert_history,
            'acme.metrics.v1.MetricAlertNotificationService': metrics_metric_alert_notification,
            'acme.metrics.v1.MetricAlertValidationService': metrics_metric_alert_validation,
            'acme.metrics.v1.MetricSeriesAdminService': metrics_metric_series_admin,
            'acme.metrics.v1.MetricSeriesExportService': metrics_metric_series_export,
            'acme.metrics.v1.MetricSeriesHistoryService': metrics_metric_series_history,
            'acme.metrics.v1.MetricSeriesNotificationService': metrics_metric_series_notification,
            'acme.metrics.v1.MetricSeriesQueryService': metrics_metric_series_query,
            'acme.metrics.v1.MetricSeriesService': metrics_metric_series,
            'acme.metrics.v1.MetricSeriesValidationService': metrics_metric_series_validation,
            'acme.modelregistry.v1.DeploymentApprovalService': modelregistry_deployment_approval,
            'acme.modelregistry.v1.DeploymentImportService': modelregistry_deployment_import,
            'acme.modelregistry.v1.DeploymentSyncService': modelregistry_deployment_sync,
            'acme.modelregistry.v1.ModelVersionApprovalService': modelregistry_model_version_approval,
            'acme.modelregistry.v1.ModelVersionReportingService': modelregistry_model_version_reporting,
            'acme.modelregistry.v1.RegisteredModelLifecycleService': modelregistry_registered_model_lifecycle,
            'acme.modelregistry.v1.RegisteredModelReportingService': modelregistry_registered_model_reporting,
            'acme.notifications.v1.NotificationQueryService': notifications_notification_query,
            'acme.notifications.v1.NotificationService': notifications_notification,
            'acme.notifications.v1.NotificationValidationService': notifications_notification_validation,
            'acme.patientapp.v1.PatientHomeQueryService': patientapp_patient_home_query,
            'acme.patientapp.v1.PatientHomeService': patientapp_patient_home,
            'acme.pipelines.v1.PipelineApprovalService': pipelines_pipeline_approval,
            'acme.pipelines.v1.PipelineRunReportingService': pipelines_pipeline_run_reporting,
            'acme.pipelines.v1.PipelineRunWorkflowService': pipelines_pipeline_run_workflow,
            'acme.pipelines.v1.PipelineStepExportService': pipelines_pipeline_step_export,
            'acme.pipelines.v1.PipelineStepReportingService': pipelines_pipeline_step_reporting,
            'acme.pipelines.v1.PipelineStepSyncService': pipelines_pipeline_step_sync,
            'acme.pipelines.v1.PipelineWorkflowService': pipelines_pipeline_workflow,
            'acme.pricing.v1.PriceListQueryService': pricing_price_list_query,
            'acme.recommendations.v1.InteractionApprovalService': recommendations_interaction_approval,
            'acme.recommendations.v1.InteractionWorkflowService': recommendations_interaction_workflow,
            'acme.recommendations.v1.RecommendationModelWorkflowService': recommendations_recommendation_model_workflow,
            'acme.search.v1.SearchIndexService': search_search_index,
            'acme.search.v1.SearchIndexValidationService': search_search_index_validation,
            'acme.telehealth.v1.VideoVisitCalculationService': telehealth_video_visit_calculation,
            'acme.venues.v1.VenueService': venues_venue,
            'acme.venues.v1.VenueValidationService': venues_venue_validation,
        },
    )
    return Dependencies(clients, DomainRepository(container.sessions),
                        container.settings, container.bus)


def register(server: grpc.aio.Server, container: Container) -> dict[str, object]:
    deps = dependencies(container)
    registered: dict[str, object] = {}
    data_share_approval_servicer = Factory(lambda: DataShareApprovalServicer(deps))()
    datahub_v1_data_share_approval_service_pb2_grpc.add_DataShareApprovalServiceServicer_to_server(
        data_share_approval_servicer,
        server
    )
    registered['acme.datahub.v1.DataShareApprovalService'] = data_share_approval_servicer
    data_share_integration_servicer = Factory(lambda: DataShareIntegrationServicer(deps))()
    datahub_v1_data_share_integration_service_pb2_grpc.add_DataShareIntegrationServiceServicer_to_server(
        data_share_integration_servicer,
        server
    )
    registered['acme.datahub.v1.DataShareIntegrationService'] = data_share_integration_servicer
    data_share_notification_servicer = Factory(lambda: DataShareNotificationServicer(deps))()
    datahub_v1_data_share_notification_service_pb2_grpc.add_DataShareNotificationServiceServicer_to_server(
        data_share_notification_servicer,
        server
    )
    registered['acme.datahub.v1.DataShareNotificationService'] = data_share_notification_servicer
    data_share_query_servicer = Factory(lambda: DataShareQueryServicer(deps))()
    datahub_v1_data_share_query_service_pb2_grpc.add_DataShareQueryServiceServicer_to_server(
        data_share_query_servicer,
        server
    )
    registered['acme.datahub.v1.DataShareQueryService'] = data_share_query_servicer
    data_share_reporting_servicer = Factory(lambda: DataShareReportingServicer(deps))()
    datahub_v1_data_share_reporting_service_pb2_grpc.add_DataShareReportingServiceServicer_to_server(
        data_share_reporting_servicer,
        server
    )
    registered['acme.datahub.v1.DataShareReportingService'] = data_share_reporting_servicer
    data_share_validation_servicer = Factory(lambda: DataShareValidationServicer(deps))()
    datahub_v1_data_share_validation_service_pb2_grpc.add_DataShareValidationServiceServicer_to_server(
        data_share_validation_servicer,
        server
    )
    registered['acme.datahub.v1.DataShareValidationService'] = data_share_validation_servicer
    data_share_workflow_servicer = Factory(lambda: DataShareWorkflowServicer(deps))()
    datahub_v1_data_share_workflow_service_pb2_grpc.add_DataShareWorkflowServiceServicer_to_server(
        data_share_workflow_servicer,
        server
    )
    registered['acme.datahub.v1.DataShareWorkflowService'] = data_share_workflow_servicer
    notebook_approval_servicer = Factory(lambda: NotebookApprovalServicer(deps))()
    datahub_v1_notebook_approval_service_pb2_grpc.add_NotebookApprovalServiceServicer_to_server(
        notebook_approval_servicer,
        server
    )
    registered['acme.datahub.v1.NotebookApprovalService'] = notebook_approval_servicer
    notebook_integration_servicer = Factory(lambda: NotebookIntegrationServicer(deps))()
    datahub_v1_notebook_integration_service_pb2_grpc.add_NotebookIntegrationServiceServicer_to_server(
        notebook_integration_servicer,
        server
    )
    registered['acme.datahub.v1.NotebookIntegrationService'] = notebook_integration_servicer
    notebook_notification_servicer = Factory(lambda: NotebookNotificationServicer(deps))()
    datahub_v1_notebook_notification_service_pb2_grpc.add_NotebookNotificationServiceServicer_to_server(
        notebook_notification_servicer,
        server
    )
    registered['acme.datahub.v1.NotebookNotificationService'] = notebook_notification_servicer
    notebook_query_servicer = Factory(lambda: NotebookQueryServicer(deps))()
    datahub_v1_notebook_query_service_pb2_grpc.add_NotebookQueryServiceServicer_to_server(
        notebook_query_servicer,
        server
    )
    registered['acme.datahub.v1.NotebookQueryService'] = notebook_query_servicer
    notebook_reporting_servicer = Factory(lambda: NotebookReportingServicer(deps))()
    datahub_v1_notebook_reporting_service_pb2_grpc.add_NotebookReportingServiceServicer_to_server(
        notebook_reporting_servicer,
        server
    )
    registered['acme.datahub.v1.NotebookReportingService'] = notebook_reporting_servicer
    notebook_servicer = Factory(lambda: NotebookServicer(deps))()
    datahub_v1_notebook_service_pb2_grpc.add_NotebookServiceServicer_to_server(notebook_servicer, server)
    registered['acme.datahub.v1.NotebookService'] = notebook_servicer
    notebook_workflow_servicer = Factory(lambda: NotebookWorkflowServicer(deps))()
    datahub_v1_notebook_workflow_service_pb2_grpc.add_NotebookWorkflowServiceServicer_to_server(
        notebook_workflow_servicer,
        server
    )
    registered['acme.datahub.v1.NotebookWorkflowService'] = notebook_workflow_servicer
    workspace_approval_servicer = Factory(lambda: WorkspaceApprovalServicer(deps))()
    datahub_v1_workspace_approval_service_pb2_grpc.add_WorkspaceApprovalServiceServicer_to_server(
        workspace_approval_servicer,
        server
    )
    registered['acme.datahub.v1.WorkspaceApprovalService'] = workspace_approval_servicer
    workspace_gateway_servicer = Factory(lambda: WorkspaceGatewayServicer(deps))()
    datahub_v1_workspace_gateway_service_pb2_grpc.add_WorkspaceGatewayServiceServicer_to_server(
        workspace_gateway_servicer,
        server
    )
    registered['acme.datahub.v1.WorkspaceGatewayService'] = workspace_gateway_servicer
    workspace_integration_servicer = Factory(lambda: WorkspaceIntegrationServicer(deps))()
    datahub_v1_workspace_integration_service_pb2_grpc.add_WorkspaceIntegrationServiceServicer_to_server(
        workspace_integration_servicer,
        server
    )
    registered['acme.datahub.v1.WorkspaceIntegrationService'] = workspace_integration_servicer
    workspace_notification_servicer = Factory(lambda: WorkspaceNotificationServicer(deps))()
    datahub_v1_workspace_notification_service_pb2_grpc.add_WorkspaceNotificationServiceServicer_to_server(
        workspace_notification_servicer,
        server
    )
    registered['acme.datahub.v1.WorkspaceNotificationService'] = workspace_notification_servicer
    workspace_query_servicer = Factory(lambda: WorkspaceQueryServicer(deps))()
    datahub_v1_workspace_query_service_pb2_grpc.add_WorkspaceQueryServiceServicer_to_server(
        workspace_query_servicer,
        server
    )
    registered['acme.datahub.v1.WorkspaceQueryService'] = workspace_query_servicer
    workspace_reporting_servicer = Factory(lambda: WorkspaceReportingServicer(deps))()
    datahub_v1_workspace_reporting_service_pb2_grpc.add_WorkspaceReportingServiceServicer_to_server(
        workspace_reporting_servicer,
        server
    )
    registered['acme.datahub.v1.WorkspaceReportingService'] = workspace_reporting_servicer
    workspace_servicer = Factory(lambda: WorkspaceServicer(deps))()
    datahub_v1_workspace_service_pb2_grpc.add_WorkspaceServiceServicer_to_server(workspace_servicer, server)
    registered['acme.datahub.v1.WorkspaceService'] = workspace_servicer
    workspace_workflow_servicer = Factory(lambda: WorkspaceWorkflowServicer(deps))()
    datahub_v1_workspace_workflow_service_pb2_grpc.add_WorkspaceWorkflowServiceServicer_to_server(
        workspace_workflow_servicer,
        server
    )
    registered['acme.datahub.v1.WorkspaceWorkflowService'] = workspace_workflow_servicer
    subscribe(deps)
    return registered
