"""Register and compose every service of the forecasting domain."""

from __future__ import annotations

import grpc

from acme.anomalies.v1 import (
    anomaly_feedback_calculation_service_pb2_grpc as anomalies_v1_anomaly_feedback_calculation_service_pb2_grpc,
)
from acme.anomalies.v1 import anomaly_query_service_pb2_grpc as anomalies_v1_anomaly_query_service_pb2_grpc
from acme.appointments.v1 import (
    appointment_query_service_pb2_grpc as appointments_v1_appointment_query_service_pb2_grpc,
)
from acme.audit.v1 import audit_event_validation_service_pb2_grpc as audit_v1_audit_event_validation_service_pb2_grpc
from acme.authorization.v1 import access_policy_service_pb2_grpc as authorization_v1_access_policy_service_pb2_grpc
from acme.authorization.v1 import (
    access_policy_validation_service_pb2_grpc as authorization_v1_access_policy_validation_service_pb2_grpc,
)
from acme.careplans.v1 import care_plan_query_service_pb2_grpc as careplans_v1_care_plan_query_service_pb2_grpc
from acme.certificates.v1 import (
    certificate_calculation_service_pb2_grpc as certificates_v1_certificate_calculation_service_pb2_grpc,
)
from acme.datasets.v1 import dataset_service_pb2_grpc as datasets_v1_dataset_service_pb2_grpc
from acme.datasets.v1 import (
    dataset_version_validation_service_pb2_grpc as datasets_v1_dataset_version_validation_service_pb2_grpc,
)
from acme.documents.v1 import document_query_service_pb2_grpc as documents_v1_document_query_service_pb2_grpc
from acme.documents.v1 import document_service_pb2_grpc as documents_v1_document_service_pb2_grpc
from acme.documents.v1 import document_validation_service_pb2_grpc as documents_v1_document_validation_service_pb2_grpc
from acme.featureflags.v1 import (
    feature_flag_query_service_pb2_grpc as featureflags_v1_feature_flag_query_service_pb2_grpc,
)
from acme.featureflags.v1 import feature_flag_service_pb2_grpc as featureflags_v1_feature_flag_service_pb2_grpc
from acme.featurestore.v1 import entity_approval_service_pb2_grpc as featurestore_v1_entity_approval_service_pb2_grpc
from acme.featurestore.v1 import (
    entity_validation_service_pb2_grpc as featurestore_v1_entity_validation_service_pb2_grpc,
)
from acme.featurestore.v1 import entity_workflow_service_pb2_grpc as featurestore_v1_entity_workflow_service_pb2_grpc
from acme.featurestore.v1 import (
    feature_value_validation_service_pb2_grpc as featurestore_v1_feature_value_validation_service_pb2_grpc,
)
from acme.featurestore.v1 import (
    feature_view_query_service_pb2_grpc as featurestore_v1_feature_view_query_service_pb2_grpc,
)
from acme.featurestore.v1 import (
    feature_view_reporting_service_pb2_grpc as featurestore_v1_feature_view_reporting_service_pb2_grpc,
)
from acme.forecasting.v1 import (
    demand_forecast_approval_service_pb2_grpc as forecasting_v1_demand_forecast_approval_service_pb2_grpc,
)
from acme.forecasting.v1 import (
    demand_forecast_query_service_pb2_grpc as forecasting_v1_demand_forecast_query_service_pb2_grpc,
)
from acme.forecasting.v1 import demand_forecast_service_pb2_grpc as forecasting_v1_demand_forecast_service_pb2_grpc
from acme.forecasting.v1 import (
    demand_forecast_validation_service_pb2_grpc as forecasting_v1_demand_forecast_validation_service_pb2_grpc,
)
from acme.forecasting.v1 import (
    demand_forecast_workflow_service_pb2_grpc as forecasting_v1_demand_forecast_workflow_service_pb2_grpc,
)
from acme.forecasting.v1 import (
    forecast_model_approval_service_pb2_grpc as forecasting_v1_forecast_model_approval_service_pb2_grpc,
)
from acme.forecasting.v1 import (
    forecast_model_query_service_pb2_grpc as forecasting_v1_forecast_model_query_service_pb2_grpc,
)
from acme.forecasting.v1 import (
    forecast_model_validation_service_pb2_grpc as forecasting_v1_forecast_model_validation_service_pb2_grpc,
)
from acme.forecasting.v1 import (
    forecast_model_workflow_service_pb2_grpc as forecasting_v1_forecast_model_workflow_service_pb2_grpc,
)
from acme.forecasting.v1 import scenario_approval_service_pb2_grpc as forecasting_v1_scenario_approval_service_pb2_grpc
from acme.forecasting.v1 import (
    scenario_calculation_service_pb2_grpc as forecasting_v1_scenario_calculation_service_pb2_grpc,
)
from acme.forecasting.v1 import (
    scenario_validation_service_pb2_grpc as forecasting_v1_scenario_validation_service_pb2_grpc,
)
from acme.forecasting.v1 import scenario_workflow_service_pb2_grpc as forecasting_v1_scenario_workflow_service_pb2_grpc
from acme.identity.v1 import user_query_service_pb2_grpc as identity_v1_user_query_service_pb2_grpc
from acme.identity.v1 import user_service_pb2_grpc as identity_v1_user_service_pb2_grpc
from acme.identity.v1 import user_validation_service_pb2_grpc as identity_v1_user_validation_service_pb2_grpc
from acme.labeling.v1 import (
    annotation_validation_service_pb2_grpc as labeling_v1_annotation_validation_service_pb2_grpc,
)
from acme.labeling.v1 import annotation_workflow_service_pb2_grpc as labeling_v1_annotation_workflow_service_pb2_grpc
from acme.labeling.v1 import label_set_validation_service_pb2_grpc as labeling_v1_label_set_validation_service_pb2_grpc
from acme.labeling.v1 import (
    labeling_task_calculation_service_pb2_grpc as labeling_v1_labeling_task_calculation_service_pb2_grpc,
)
from acme.labeling.v1 import labeling_task_query_service_pb2_grpc as labeling_v1_labeling_task_query_service_pb2_grpc
from acme.labeling.v1 import (
    labeling_task_validation_service_pb2_grpc as labeling_v1_labeling_task_validation_service_pb2_grpc,
)
from acme.labeling.v1 import (
    labeling_task_workflow_service_pb2_grpc as labeling_v1_labeling_task_workflow_service_pb2_grpc,
)
from acme.ledger.v1 import ledger_account_query_service_pb2_grpc as ledger_v1_ledger_account_query_service_pb2_grpc
from acme.ledger.v1 import (
    ledger_account_validation_service_pb2_grpc as ledger_v1_ledger_account_validation_service_pb2_grpc,
)
from acme.lineage.v1 import impact_calculation_service_pb2_grpc as lineage_v1_impact_calculation_service_pb2_grpc
from acme.lineage.v1 import impact_workflow_service_pb2_grpc as lineage_v1_impact_workflow_service_pb2_grpc
from acme.lineage.v1 import lineage_node_service_pb2_grpc as lineage_v1_lineage_node_service_pb2_grpc
from acme.lineage.v1 import lineage_node_sync_service_pb2_grpc as lineage_v1_lineage_node_sync_service_pb2_grpc
from acme.metrics.v1 import (
    dashboard_notification_service_pb2_grpc as metrics_v1_dashboard_notification_service_pb2_grpc,
)
from acme.metrics.v1 import dashboard_sync_service_pb2_grpc as metrics_v1_dashboard_sync_service_pb2_grpc
from acme.metrics.v1 import dashboard_validation_service_pb2_grpc as metrics_v1_dashboard_validation_service_pb2_grpc
from acme.metrics.v1 import metric_alert_export_service_pb2_grpc as metrics_v1_metric_alert_export_service_pb2_grpc
from acme.metrics.v1 import metric_alert_history_service_pb2_grpc as metrics_v1_metric_alert_history_service_pb2_grpc
from acme.metrics.v1 import metric_alert_query_service_pb2_grpc as metrics_v1_metric_alert_query_service_pb2_grpc
from acme.metrics.v1 import metric_series_export_service_pb2_grpc as metrics_v1_metric_series_export_service_pb2_grpc
from acme.metrics.v1 import metric_series_history_service_pb2_grpc as metrics_v1_metric_series_history_service_pb2_grpc
from acme.metrics.v1 import (
    metric_series_notification_service_pb2_grpc as metrics_v1_metric_series_notification_service_pb2_grpc,
)
from acme.metrics.v1 import metric_series_query_service_pb2_grpc as metrics_v1_metric_series_query_service_pb2_grpc
from acme.metrics.v1 import (
    metric_series_validation_service_pb2_grpc as metrics_v1_metric_series_validation_service_pb2_grpc,
)
from acme.modelregistry.v1 import (
    deployment_approval_service_pb2_grpc as modelregistry_v1_deployment_approval_service_pb2_grpc,
)
from acme.modelregistry.v1 import deployment_sync_service_pb2_grpc as modelregistry_v1_deployment_sync_service_pb2_grpc
from acme.modelregistry.v1 import (
    deployment_validation_service_pb2_grpc as modelregistry_v1_deployment_validation_service_pb2_grpc,
)
from acme.modelregistry.v1 import (
    model_version_lifecycle_service_pb2_grpc as modelregistry_v1_model_version_lifecycle_service_pb2_grpc,
)
from acme.modelregistry.v1 import (
    model_version_validation_service_pb2_grpc as modelregistry_v1_model_version_validation_service_pb2_grpc,
)
from acme.modelregistry.v1 import (
    registered_model_query_service_pb2_grpc as modelregistry_v1_registered_model_query_service_pb2_grpc,
)
from acme.modelregistry.v1 import (
    registered_model_workflow_service_pb2_grpc as modelregistry_v1_registered_model_workflow_service_pb2_grpc,
)
from acme.notifications.v1 import (
    notification_query_service_pb2_grpc as notifications_v1_notification_query_service_pb2_grpc,
)
from acme.notifications.v1 import notification_service_pb2_grpc as notifications_v1_notification_service_pb2_grpc
from acme.notifications.v1 import (
    notification_validation_service_pb2_grpc as notifications_v1_notification_validation_service_pb2_grpc,
)
from acme.patients.v1 import patient_query_service_pb2_grpc as patients_v1_patient_query_service_pb2_grpc
from acme.pipelines.v1 import pipeline_reporting_service_pb2_grpc as pipelines_v1_pipeline_reporting_service_pb2_grpc
from acme.pipelines.v1 import (
    pipeline_run_calculation_service_pb2_grpc as pipelines_v1_pipeline_run_calculation_service_pb2_grpc,
)
from acme.pipelines.v1 import (
    pipeline_run_validation_service_pb2_grpc as pipelines_v1_pipeline_run_validation_service_pb2_grpc,
)
from acme.pipelines.v1 import (
    pipeline_step_calculation_service_pb2_grpc as pipelines_v1_pipeline_step_calculation_service_pb2_grpc,
)
from acme.pipelines.v1 import (
    pipeline_step_export_service_pb2_grpc as pipelines_v1_pipeline_step_export_service_pb2_grpc,
)
from acme.pipelines.v1 import (
    pipeline_step_import_service_pb2_grpc as pipelines_v1_pipeline_step_import_service_pb2_grpc,
)
from acme.pipelines.v1 import (
    pipeline_step_validation_service_pb2_grpc as pipelines_v1_pipeline_step_validation_service_pb2_grpc,
)
from acme.pipelines.v1 import pipeline_workflow_service_pb2_grpc as pipelines_v1_pipeline_workflow_service_pb2_grpc
from acme.ratelimiting.v1 import rate_limit_query_service_pb2_grpc as ratelimiting_v1_rate_limit_query_service_pb2_grpc
from acme.recommendations.v1 import (
    interaction_approval_service_pb2_grpc as recommendations_v1_interaction_approval_service_pb2_grpc,
)
from acme.recommendations.v1 import (
    recommendation_model_calculation_service_pb2_grpc as recommendations_v1_recommendation_model_calculation_service_pb2_grpc,
)
from acme.recommendations.v1 import (
    recommendation_model_workflow_service_pb2_grpc as recommendations_v1_recommendation_model_workflow_service_pb2_grpc,
)
from acme.recommendations.v1 import (
    recommendation_set_query_service_pb2_grpc as recommendations_v1_recommendation_set_query_service_pb2_grpc,
)
from acme.routing.v1 import route_service_pb2_grpc as routing_v1_route_service_pb2_grpc
from acme.search.v1 import search_index_service_pb2_grpc as search_v1_search_index_service_pb2_grpc
from acme.search.v1 import (
    search_index_validation_service_pb2_grpc as search_v1_search_index_validation_service_pb2_grpc,
)
from acme.shows.v1 import show_calculation_service_pb2_grpc as shows_v1_show_calculation_service_pb2_grpc
from acme.shows.v1 import show_query_service_pb2_grpc as shows_v1_show_query_service_pb2_grpc
from acme.suppliers.v1 import supplier_service_pb2_grpc as suppliers_v1_supplier_service_pb2_grpc
from acme.tours.v1 import tour_query_service_pb2_grpc as tours_v1_tour_query_service_pb2_grpc
from acme.venues.v1 import venue_query_service_pb2_grpc as venues_v1_venue_query_service_pb2_grpc
from acme.venues.v1 import venue_service_pb2_grpc as venues_v1_venue_service_pb2_grpc
from acme.venues.v1 import venue_validation_service_pb2_grpc as venues_v1_venue_validation_service_pb2_grpc
from acme.webhooks.v1 import webhook_endpoint_service_pb2_grpc as webhooks_v1_webhook_endpoint_service_pb2_grpc

from acme_data.domains.forecasting.demand_forecast_approval_service import DemandForecastApprovalServicer
from acme_data.domains.forecasting.demand_forecast_query_service import DemandForecastQueryServicer
from acme_data.domains.forecasting.demand_forecast_service import DemandForecastServicer
from acme_data.domains.forecasting.demand_forecast_validation_service import DemandForecastValidationServicer
from acme_data.domains.forecasting.demand_forecast_workflow_service import DemandForecastWorkflowServicer
from acme_data.domains.forecasting.dependencies import Clients
from acme_data.domains.forecasting.dependencies import Dependencies
from acme_data.domains.forecasting.events import subscribe
from acme_data.domains.forecasting.forecast_model_approval_service import ForecastModelApprovalServicer
from acme_data.domains.forecasting.forecast_model_query_service import ForecastModelQueryServicer
from acme_data.domains.forecasting.forecast_model_validation_service import ForecastModelValidationServicer
from acme_data.domains.forecasting.forecast_model_workflow_service import ForecastModelWorkflowServicer
from acme_data.domains.forecasting.repository import DomainRepository
from acme_data.domains.forecasting.scenario_approval_service import ScenarioApprovalServicer
from acme_data.domains.forecasting.scenario_calculation_service import ScenarioCalculationServicer
from acme_data.domains.forecasting.scenario_validation_service import ScenarioValidationServicer
from acme_data.domains.forecasting.scenario_workflow_service import ScenarioWorkflowServicer
from acme_data.platform.container import Container
from acme_data.platform.container import Factory


def dependencies(container: Container) -> Dependencies:
    anomalies_anomaly_feedback_calculation = container.singleton(
        anomalies_v1_anomaly_feedback_calculation_service_pb2_grpc.AnomalyFeedbackCalculationServiceStub,
        lambda: anomalies_v1_anomaly_feedback_calculation_service_pb2_grpc.AnomalyFeedbackCalculationServiceStub(
            container.channel
        )
    )
    anomalies_anomaly_query = container.singleton(
        anomalies_v1_anomaly_query_service_pb2_grpc.AnomalyQueryServiceStub,
        lambda: anomalies_v1_anomaly_query_service_pb2_grpc.AnomalyQueryServiceStub(container.channel)
    )
    appointments_appointment_query = container.singleton(
        appointments_v1_appointment_query_service_pb2_grpc.AppointmentQueryServiceStub,
        lambda: appointments_v1_appointment_query_service_pb2_grpc.AppointmentQueryServiceStub(container.channel)
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
    careplans_care_plan_query = container.singleton(
        careplans_v1_care_plan_query_service_pb2_grpc.CarePlanQueryServiceStub,
        lambda: careplans_v1_care_plan_query_service_pb2_grpc.CarePlanQueryServiceStub(container.channel)
    )
    certificates_certificate_calculation = container.singleton(
        certificates_v1_certificate_calculation_service_pb2_grpc.CertificateCalculationServiceStub,
        lambda: certificates_v1_certificate_calculation_service_pb2_grpc.CertificateCalculationServiceStub(
            container.channel
        )
    )
    datasets_dataset = container.singleton(
        datasets_v1_dataset_service_pb2_grpc.DatasetServiceStub,
        lambda: datasets_v1_dataset_service_pb2_grpc.DatasetServiceStub(container.channel)
    )
    datasets_dataset_version_validation = container.singleton(
        datasets_v1_dataset_version_validation_service_pb2_grpc.DatasetVersionValidationServiceStub,
        lambda: datasets_v1_dataset_version_validation_service_pb2_grpc.DatasetVersionValidationServiceStub(
            container.channel
        )
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
    featureflags_feature_flag_query = container.singleton(
        featureflags_v1_feature_flag_query_service_pb2_grpc.FeatureFlagQueryServiceStub,
        lambda: featureflags_v1_feature_flag_query_service_pb2_grpc.FeatureFlagQueryServiceStub(container.channel)
    )
    featureflags_feature_flag = container.singleton(
        featureflags_v1_feature_flag_service_pb2_grpc.FeatureFlagServiceStub,
        lambda: featureflags_v1_feature_flag_service_pb2_grpc.FeatureFlagServiceStub(container.channel)
    )
    featurestore_entity_approval = container.singleton(
        featurestore_v1_entity_approval_service_pb2_grpc.EntityApprovalServiceStub,
        lambda: featurestore_v1_entity_approval_service_pb2_grpc.EntityApprovalServiceStub(container.channel)
    )
    featurestore_entity_validation = container.singleton(
        featurestore_v1_entity_validation_service_pb2_grpc.EntityValidationServiceStub,
        lambda: featurestore_v1_entity_validation_service_pb2_grpc.EntityValidationServiceStub(container.channel)
    )
    featurestore_entity_workflow = container.singleton(
        featurestore_v1_entity_workflow_service_pb2_grpc.EntityWorkflowServiceStub,
        lambda: featurestore_v1_entity_workflow_service_pb2_grpc.EntityWorkflowServiceStub(container.channel)
    )
    featurestore_feature_value_validation = container.singleton(
        featurestore_v1_feature_value_validation_service_pb2_grpc.FeatureValueValidationServiceStub,
        lambda: featurestore_v1_feature_value_validation_service_pb2_grpc.FeatureValueValidationServiceStub(
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
    forecasting_demand_forecast_approval = container.singleton(
        forecasting_v1_demand_forecast_approval_service_pb2_grpc.DemandForecastApprovalServiceStub,
        lambda: forecasting_v1_demand_forecast_approval_service_pb2_grpc.DemandForecastApprovalServiceStub(
            container.channel
        )
    )
    forecasting_demand_forecast_query = container.singleton(
        forecasting_v1_demand_forecast_query_service_pb2_grpc.DemandForecastQueryServiceStub,
        lambda: forecasting_v1_demand_forecast_query_service_pb2_grpc.DemandForecastQueryServiceStub(container.channel)
    )
    forecasting_demand_forecast = container.singleton(
        forecasting_v1_demand_forecast_service_pb2_grpc.DemandForecastServiceStub,
        lambda: forecasting_v1_demand_forecast_service_pb2_grpc.DemandForecastServiceStub(container.channel)
    )
    forecasting_demand_forecast_validation = container.singleton(
        forecasting_v1_demand_forecast_validation_service_pb2_grpc.DemandForecastValidationServiceStub,
        lambda: forecasting_v1_demand_forecast_validation_service_pb2_grpc.DemandForecastValidationServiceStub(
            container.channel
        )
    )
    forecasting_demand_forecast_workflow = container.singleton(
        forecasting_v1_demand_forecast_workflow_service_pb2_grpc.DemandForecastWorkflowServiceStub,
        lambda: forecasting_v1_demand_forecast_workflow_service_pb2_grpc.DemandForecastWorkflowServiceStub(
            container.channel
        )
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
    forecasting_forecast_model_validation = container.singleton(
        forecasting_v1_forecast_model_validation_service_pb2_grpc.ForecastModelValidationServiceStub,
        lambda: forecasting_v1_forecast_model_validation_service_pb2_grpc.ForecastModelValidationServiceStub(
            container.channel
        )
    )
    forecasting_scenario_approval = container.singleton(
        forecasting_v1_scenario_approval_service_pb2_grpc.ScenarioApprovalServiceStub,
        lambda: forecasting_v1_scenario_approval_service_pb2_grpc.ScenarioApprovalServiceStub(container.channel)
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
    identity_user = container.singleton(
        identity_v1_user_service_pb2_grpc.UserServiceStub,
        lambda: identity_v1_user_service_pb2_grpc.UserServiceStub(container.channel)
    )
    identity_user_validation = container.singleton(
        identity_v1_user_validation_service_pb2_grpc.UserValidationServiceStub,
        lambda: identity_v1_user_validation_service_pb2_grpc.UserValidationServiceStub(container.channel)
    )
    labeling_annotation_validation = container.singleton(
        labeling_v1_annotation_validation_service_pb2_grpc.AnnotationValidationServiceStub,
        lambda: labeling_v1_annotation_validation_service_pb2_grpc.AnnotationValidationServiceStub(container.channel)
    )
    labeling_annotation_workflow = container.singleton(
        labeling_v1_annotation_workflow_service_pb2_grpc.AnnotationWorkflowServiceStub,
        lambda: labeling_v1_annotation_workflow_service_pb2_grpc.AnnotationWorkflowServiceStub(container.channel)
    )
    labeling_label_set_validation = container.singleton(
        labeling_v1_label_set_validation_service_pb2_grpc.LabelSetValidationServiceStub,
        lambda: labeling_v1_label_set_validation_service_pb2_grpc.LabelSetValidationServiceStub(container.channel)
    )
    labeling_labeling_task_calculation = container.singleton(
        labeling_v1_labeling_task_calculation_service_pb2_grpc.LabelingTaskCalculationServiceStub,
        lambda: labeling_v1_labeling_task_calculation_service_pb2_grpc.LabelingTaskCalculationServiceStub(
            container.channel
        )
    )
    labeling_labeling_task_query = container.singleton(
        labeling_v1_labeling_task_query_service_pb2_grpc.LabelingTaskQueryServiceStub,
        lambda: labeling_v1_labeling_task_query_service_pb2_grpc.LabelingTaskQueryServiceStub(container.channel)
    )
    labeling_labeling_task_validation = container.singleton(
        labeling_v1_labeling_task_validation_service_pb2_grpc.LabelingTaskValidationServiceStub,
        lambda: labeling_v1_labeling_task_validation_service_pb2_grpc.LabelingTaskValidationServiceStub(
            container.channel
        )
    )
    labeling_labeling_task_workflow = container.singleton(
        labeling_v1_labeling_task_workflow_service_pb2_grpc.LabelingTaskWorkflowServiceStub,
        lambda: labeling_v1_labeling_task_workflow_service_pb2_grpc.LabelingTaskWorkflowServiceStub(container.channel)
    )
    ledger_ledger_account_query = container.singleton(
        ledger_v1_ledger_account_query_service_pb2_grpc.LedgerAccountQueryServiceStub,
        lambda: ledger_v1_ledger_account_query_service_pb2_grpc.LedgerAccountQueryServiceStub(container.channel)
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
    lineage_impact_workflow = container.singleton(
        lineage_v1_impact_workflow_service_pb2_grpc.ImpactWorkflowServiceStub,
        lambda: lineage_v1_impact_workflow_service_pb2_grpc.ImpactWorkflowServiceStub(container.channel)
    )
    lineage_lineage_node = container.singleton(
        lineage_v1_lineage_node_service_pb2_grpc.LineageNodeServiceStub,
        lambda: lineage_v1_lineage_node_service_pb2_grpc.LineageNodeServiceStub(container.channel)
    )
    lineage_lineage_node_sync = container.singleton(
        lineage_v1_lineage_node_sync_service_pb2_grpc.LineageNodeSyncServiceStub,
        lambda: lineage_v1_lineage_node_sync_service_pb2_grpc.LineageNodeSyncServiceStub(container.channel)
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
    metrics_metric_alert_query = container.singleton(
        metrics_v1_metric_alert_query_service_pb2_grpc.MetricAlertQueryServiceStub,
        lambda: metrics_v1_metric_alert_query_service_pb2_grpc.MetricAlertQueryServiceStub(container.channel)
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
    modelregistry_model_version_lifecycle = container.singleton(
        modelregistry_v1_model_version_lifecycle_service_pb2_grpc.ModelVersionLifecycleServiceStub,
        lambda: modelregistry_v1_model_version_lifecycle_service_pb2_grpc.ModelVersionLifecycleServiceStub(
            container.channel
        )
    )
    modelregistry_model_version_validation = container.singleton(
        modelregistry_v1_model_version_validation_service_pb2_grpc.ModelVersionValidationServiceStub,
        lambda: modelregistry_v1_model_version_validation_service_pb2_grpc.ModelVersionValidationServiceStub(
            container.channel
        )
    )
    modelregistry_registered_model_query = container.singleton(
        modelregistry_v1_registered_model_query_service_pb2_grpc.RegisteredModelQueryServiceStub,
        lambda: modelregistry_v1_registered_model_query_service_pb2_grpc.RegisteredModelQueryServiceStub(
            container.channel
        )
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
    patients_patient_query = container.singleton(
        patients_v1_patient_query_service_pb2_grpc.PatientQueryServiceStub,
        lambda: patients_v1_patient_query_service_pb2_grpc.PatientQueryServiceStub(container.channel)
    )
    pipelines_pipeline_reporting = container.singleton(
        pipelines_v1_pipeline_reporting_service_pb2_grpc.PipelineReportingServiceStub,
        lambda: pipelines_v1_pipeline_reporting_service_pb2_grpc.PipelineReportingServiceStub(container.channel)
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
    pipelines_pipeline_step_calculation = container.singleton(
        pipelines_v1_pipeline_step_calculation_service_pb2_grpc.PipelineStepCalculationServiceStub,
        lambda: pipelines_v1_pipeline_step_calculation_service_pb2_grpc.PipelineStepCalculationServiceStub(
            container.channel
        )
    )
    pipelines_pipeline_step_export = container.singleton(
        pipelines_v1_pipeline_step_export_service_pb2_grpc.PipelineStepExportServiceStub,
        lambda: pipelines_v1_pipeline_step_export_service_pb2_grpc.PipelineStepExportServiceStub(container.channel)
    )
    pipelines_pipeline_step_import = container.singleton(
        pipelines_v1_pipeline_step_import_service_pb2_grpc.PipelineStepImportServiceStub,
        lambda: pipelines_v1_pipeline_step_import_service_pb2_grpc.PipelineStepImportServiceStub(container.channel)
    )
    pipelines_pipeline_step_validation = container.singleton(
        pipelines_v1_pipeline_step_validation_service_pb2_grpc.PipelineStepValidationServiceStub,
        lambda: pipelines_v1_pipeline_step_validation_service_pb2_grpc.PipelineStepValidationServiceStub(
            container.channel
        )
    )
    pipelines_pipeline_workflow = container.singleton(
        pipelines_v1_pipeline_workflow_service_pb2_grpc.PipelineWorkflowServiceStub,
        lambda: pipelines_v1_pipeline_workflow_service_pb2_grpc.PipelineWorkflowServiceStub(container.channel)
    )
    ratelimiting_rate_limit_query = container.singleton(
        ratelimiting_v1_rate_limit_query_service_pb2_grpc.RateLimitQueryServiceStub,
        lambda: ratelimiting_v1_rate_limit_query_service_pb2_grpc.RateLimitQueryServiceStub(container.channel)
    )
    recommendations_interaction_approval = container.singleton(
        recommendations_v1_interaction_approval_service_pb2_grpc.InteractionApprovalServiceStub,
        lambda: recommendations_v1_interaction_approval_service_pb2_grpc.InteractionApprovalServiceStub(
            container.channel
        )
    )
    recommendations_recommendation_model_calculation = container.singleton(
        recommendations_v1_recommendation_model_calculation_service_pb2_grpc.RecommendationModelCalculationServiceStub,
        lambda: recommendations_v1_recommendation_model_calculation_service_pb2_grpc.RecommendationModelCalculationServiceStub(
            container.channel
        )
    )
    recommendations_recommendation_model_workflow = container.singleton(
        recommendations_v1_recommendation_model_workflow_service_pb2_grpc.RecommendationModelWorkflowServiceStub,
        lambda: recommendations_v1_recommendation_model_workflow_service_pb2_grpc.RecommendationModelWorkflowServiceStub(
            container.channel
        )
    )
    recommendations_recommendation_set_query = container.singleton(
        recommendations_v1_recommendation_set_query_service_pb2_grpc.RecommendationSetQueryServiceStub,
        lambda: recommendations_v1_recommendation_set_query_service_pb2_grpc.RecommendationSetQueryServiceStub(
            container.channel
        )
    )
    routing_route = container.singleton(
        routing_v1_route_service_pb2_grpc.RouteServiceStub,
        lambda: routing_v1_route_service_pb2_grpc.RouteServiceStub(container.channel)
    )
    search_search_index = container.singleton(
        search_v1_search_index_service_pb2_grpc.SearchIndexServiceStub,
        lambda: search_v1_search_index_service_pb2_grpc.SearchIndexServiceStub(container.channel)
    )
    search_search_index_validation = container.singleton(
        search_v1_search_index_validation_service_pb2_grpc.SearchIndexValidationServiceStub,
        lambda: search_v1_search_index_validation_service_pb2_grpc.SearchIndexValidationServiceStub(container.channel)
    )
    shows_show_calculation = container.singleton(
        shows_v1_show_calculation_service_pb2_grpc.ShowCalculationServiceStub,
        lambda: shows_v1_show_calculation_service_pb2_grpc.ShowCalculationServiceStub(container.channel)
    )
    shows_show_query = container.singleton(
        shows_v1_show_query_service_pb2_grpc.ShowQueryServiceStub,
        lambda: shows_v1_show_query_service_pb2_grpc.ShowQueryServiceStub(container.channel)
    )
    suppliers_supplier = container.singleton(
        suppliers_v1_supplier_service_pb2_grpc.SupplierServiceStub,
        lambda: suppliers_v1_supplier_service_pb2_grpc.SupplierServiceStub(container.channel)
    )
    tours_tour_query = container.singleton(
        tours_v1_tour_query_service_pb2_grpc.TourQueryServiceStub,
        lambda: tours_v1_tour_query_service_pb2_grpc.TourQueryServiceStub(container.channel)
    )
    venues_venue_query = container.singleton(
        venues_v1_venue_query_service_pb2_grpc.VenueQueryServiceStub,
        lambda: venues_v1_venue_query_service_pb2_grpc.VenueQueryServiceStub(container.channel)
    )
    venues_venue = container.singleton(
        venues_v1_venue_service_pb2_grpc.VenueServiceStub,
        lambda: venues_v1_venue_service_pb2_grpc.VenueServiceStub(container.channel)
    )
    venues_venue_validation = container.singleton(
        venues_v1_venue_validation_service_pb2_grpc.VenueValidationServiceStub,
        lambda: venues_v1_venue_validation_service_pb2_grpc.VenueValidationServiceStub(container.channel)
    )
    webhooks_webhook_endpoint = container.singleton(
        webhooks_v1_webhook_endpoint_service_pb2_grpc.WebhookEndpointServiceStub,
        lambda: webhooks_v1_webhook_endpoint_service_pb2_grpc.WebhookEndpointServiceStub(container.channel)
    )
    clients = Clients(
        anomalies_anomaly_feedback_calculation=anomalies_anomaly_feedback_calculation,
        anomalies_anomaly_query=anomalies_anomaly_query,
        appointments_appointment_query=appointments_appointment_query,
        audit_audit_event_validation=audit_audit_event_validation,
        authorization_access_policy=authorization_access_policy,
        authorization_access_policy_validation=authorization_access_policy_validation,
        careplans_care_plan_query=careplans_care_plan_query,
        certificates_certificate_calculation=certificates_certificate_calculation,
        datasets_dataset=datasets_dataset,
        datasets_dataset_version_validation=datasets_dataset_version_validation,
        documents_document_query=documents_document_query,
        documents_document=documents_document,
        documents_document_validation=documents_document_validation,
        featureflags_feature_flag_query=featureflags_feature_flag_query,
        featureflags_feature_flag=featureflags_feature_flag,
        featurestore_entity_approval=featurestore_entity_approval,
        featurestore_entity_validation=featurestore_entity_validation,
        featurestore_entity_workflow=featurestore_entity_workflow,
        featurestore_feature_value_validation=featurestore_feature_value_validation,
        featurestore_feature_view_query=featurestore_feature_view_query,
        featurestore_feature_view_reporting=featurestore_feature_view_reporting,
        forecasting_demand_forecast_approval=forecasting_demand_forecast_approval,
        forecasting_demand_forecast_query=forecasting_demand_forecast_query,
        forecasting_demand_forecast=forecasting_demand_forecast,
        forecasting_demand_forecast_validation=forecasting_demand_forecast_validation,
        forecasting_demand_forecast_workflow=forecasting_demand_forecast_workflow,
        forecasting_forecast_model_approval=forecasting_forecast_model_approval,
        forecasting_forecast_model_query=forecasting_forecast_model_query,
        forecasting_forecast_model_validation=forecasting_forecast_model_validation,
        forecasting_scenario_approval=forecasting_scenario_approval,
        forecasting_scenario_calculation=forecasting_scenario_calculation,
        forecasting_scenario_validation=forecasting_scenario_validation,
        identity_user_query=identity_user_query,
        identity_user=identity_user,
        identity_user_validation=identity_user_validation,
        labeling_annotation_validation=labeling_annotation_validation,
        labeling_annotation_workflow=labeling_annotation_workflow,
        labeling_label_set_validation=labeling_label_set_validation,
        labeling_labeling_task_calculation=labeling_labeling_task_calculation,
        labeling_labeling_task_query=labeling_labeling_task_query,
        labeling_labeling_task_validation=labeling_labeling_task_validation,
        labeling_labeling_task_workflow=labeling_labeling_task_workflow,
        ledger_ledger_account_query=ledger_ledger_account_query,
        ledger_ledger_account_validation=ledger_ledger_account_validation,
        lineage_impact_calculation=lineage_impact_calculation,
        lineage_impact_workflow=lineage_impact_workflow,
        lineage_lineage_node=lineage_lineage_node,
        lineage_lineage_node_sync=lineage_lineage_node_sync,
        metrics_dashboard_notification=metrics_dashboard_notification,
        metrics_dashboard_sync=metrics_dashboard_sync,
        metrics_dashboard_validation=metrics_dashboard_validation,
        metrics_metric_alert_export=metrics_metric_alert_export,
        metrics_metric_alert_history=metrics_metric_alert_history,
        metrics_metric_alert_query=metrics_metric_alert_query,
        metrics_metric_series_export=metrics_metric_series_export,
        metrics_metric_series_history=metrics_metric_series_history,
        metrics_metric_series_notification=metrics_metric_series_notification,
        metrics_metric_series_query=metrics_metric_series_query,
        metrics_metric_series_validation=metrics_metric_series_validation,
        modelregistry_deployment_approval=modelregistry_deployment_approval,
        modelregistry_deployment_sync=modelregistry_deployment_sync,
        modelregistry_deployment_validation=modelregistry_deployment_validation,
        modelregistry_model_version_lifecycle=modelregistry_model_version_lifecycle,
        modelregistry_model_version_validation=modelregistry_model_version_validation,
        modelregistry_registered_model_query=modelregistry_registered_model_query,
        modelregistry_registered_model_workflow=modelregistry_registered_model_workflow,
        notifications_notification_query=notifications_notification_query,
        notifications_notification=notifications_notification,
        notifications_notification_validation=notifications_notification_validation,
        patients_patient_query=patients_patient_query,
        pipelines_pipeline_reporting=pipelines_pipeline_reporting,
        pipelines_pipeline_run_calculation=pipelines_pipeline_run_calculation,
        pipelines_pipeline_run_validation=pipelines_pipeline_run_validation,
        pipelines_pipeline_step_calculation=pipelines_pipeline_step_calculation,
        pipelines_pipeline_step_export=pipelines_pipeline_step_export,
        pipelines_pipeline_step_import=pipelines_pipeline_step_import,
        pipelines_pipeline_step_validation=pipelines_pipeline_step_validation,
        pipelines_pipeline_workflow=pipelines_pipeline_workflow,
        ratelimiting_rate_limit_query=ratelimiting_rate_limit_query,
        recommendations_interaction_approval=recommendations_interaction_approval,
        recommendations_recommendation_model_calculation=recommendations_recommendation_model_calculation,
        recommendations_recommendation_model_workflow=recommendations_recommendation_model_workflow,
        recommendations_recommendation_set_query=recommendations_recommendation_set_query,
        routing_route=routing_route,
        search_search_index=search_search_index,
        search_search_index_validation=search_search_index_validation,
        shows_show_calculation=shows_show_calculation,
        shows_show_query=shows_show_query,
        suppliers_supplier=suppliers_supplier,
        tours_tour_query=tours_tour_query,
        venues_venue_query=venues_venue_query,
        venues_venue=venues_venue,
        venues_venue_validation=venues_venue_validation,
        webhooks_webhook_endpoint=webhooks_webhook_endpoint,
        registry={
            'acme.anomalies.v1.AnomalyFeedbackCalculationService': anomalies_anomaly_feedback_calculation,
            'acme.anomalies.v1.AnomalyQueryService': anomalies_anomaly_query,
            'acme.appointments.v1.AppointmentQueryService': appointments_appointment_query,
            'acme.audit.v1.AuditEventValidationService': audit_audit_event_validation,
            'acme.authorization.v1.AccessPolicyService': authorization_access_policy,
            'acme.authorization.v1.AccessPolicyValidationService': authorization_access_policy_validation,
            'acme.careplans.v1.CarePlanQueryService': careplans_care_plan_query,
            'acme.certificates.v1.CertificateCalculationService': certificates_certificate_calculation,
            'acme.datasets.v1.DatasetService': datasets_dataset,
            'acme.datasets.v1.DatasetVersionValidationService': datasets_dataset_version_validation,
            'acme.documents.v1.DocumentQueryService': documents_document_query,
            'acme.documents.v1.DocumentService': documents_document,
            'acme.documents.v1.DocumentValidationService': documents_document_validation,
            'acme.featureflags.v1.FeatureFlagQueryService': featureflags_feature_flag_query,
            'acme.featureflags.v1.FeatureFlagService': featureflags_feature_flag,
            'acme.featurestore.v1.EntityApprovalService': featurestore_entity_approval,
            'acme.featurestore.v1.EntityValidationService': featurestore_entity_validation,
            'acme.featurestore.v1.EntityWorkflowService': featurestore_entity_workflow,
            'acme.featurestore.v1.FeatureValueValidationService': featurestore_feature_value_validation,
            'acme.featurestore.v1.FeatureViewQueryService': featurestore_feature_view_query,
            'acme.featurestore.v1.FeatureViewReportingService': featurestore_feature_view_reporting,
            'acme.forecasting.v1.DemandForecastApprovalService': forecasting_demand_forecast_approval,
            'acme.forecasting.v1.DemandForecastQueryService': forecasting_demand_forecast_query,
            'acme.forecasting.v1.DemandForecastService': forecasting_demand_forecast,
            'acme.forecasting.v1.DemandForecastValidationService': forecasting_demand_forecast_validation,
            'acme.forecasting.v1.DemandForecastWorkflowService': forecasting_demand_forecast_workflow,
            'acme.forecasting.v1.ForecastModelApprovalService': forecasting_forecast_model_approval,
            'acme.forecasting.v1.ForecastModelQueryService': forecasting_forecast_model_query,
            'acme.forecasting.v1.ForecastModelValidationService': forecasting_forecast_model_validation,
            'acme.forecasting.v1.ScenarioApprovalService': forecasting_scenario_approval,
            'acme.forecasting.v1.ScenarioCalculationService': forecasting_scenario_calculation,
            'acme.forecasting.v1.ScenarioValidationService': forecasting_scenario_validation,
            'acme.identity.v1.UserQueryService': identity_user_query,
            'acme.identity.v1.UserService': identity_user,
            'acme.identity.v1.UserValidationService': identity_user_validation,
            'acme.labeling.v1.AnnotationValidationService': labeling_annotation_validation,
            'acme.labeling.v1.AnnotationWorkflowService': labeling_annotation_workflow,
            'acme.labeling.v1.LabelSetValidationService': labeling_label_set_validation,
            'acme.labeling.v1.LabelingTaskCalculationService': labeling_labeling_task_calculation,
            'acme.labeling.v1.LabelingTaskQueryService': labeling_labeling_task_query,
            'acme.labeling.v1.LabelingTaskValidationService': labeling_labeling_task_validation,
            'acme.labeling.v1.LabelingTaskWorkflowService': labeling_labeling_task_workflow,
            'acme.ledger.v1.LedgerAccountQueryService': ledger_ledger_account_query,
            'acme.ledger.v1.LedgerAccountValidationService': ledger_ledger_account_validation,
            'acme.lineage.v1.ImpactCalculationService': lineage_impact_calculation,
            'acme.lineage.v1.ImpactWorkflowService': lineage_impact_workflow,
            'acme.lineage.v1.LineageNodeService': lineage_lineage_node,
            'acme.lineage.v1.LineageNodeSyncService': lineage_lineage_node_sync,
            'acme.metrics.v1.DashboardNotificationService': metrics_dashboard_notification,
            'acme.metrics.v1.DashboardSyncService': metrics_dashboard_sync,
            'acme.metrics.v1.DashboardValidationService': metrics_dashboard_validation,
            'acme.metrics.v1.MetricAlertExportService': metrics_metric_alert_export,
            'acme.metrics.v1.MetricAlertHistoryService': metrics_metric_alert_history,
            'acme.metrics.v1.MetricAlertQueryService': metrics_metric_alert_query,
            'acme.metrics.v1.MetricSeriesExportService': metrics_metric_series_export,
            'acme.metrics.v1.MetricSeriesHistoryService': metrics_metric_series_history,
            'acme.metrics.v1.MetricSeriesNotificationService': metrics_metric_series_notification,
            'acme.metrics.v1.MetricSeriesQueryService': metrics_metric_series_query,
            'acme.metrics.v1.MetricSeriesValidationService': metrics_metric_series_validation,
            'acme.modelregistry.v1.DeploymentApprovalService': modelregistry_deployment_approval,
            'acme.modelregistry.v1.DeploymentSyncService': modelregistry_deployment_sync,
            'acme.modelregistry.v1.DeploymentValidationService': modelregistry_deployment_validation,
            'acme.modelregistry.v1.ModelVersionLifecycleService': modelregistry_model_version_lifecycle,
            'acme.modelregistry.v1.ModelVersionValidationService': modelregistry_model_version_validation,
            'acme.modelregistry.v1.RegisteredModelQueryService': modelregistry_registered_model_query,
            'acme.modelregistry.v1.RegisteredModelWorkflowService': modelregistry_registered_model_workflow,
            'acme.notifications.v1.NotificationQueryService': notifications_notification_query,
            'acme.notifications.v1.NotificationService': notifications_notification,
            'acme.notifications.v1.NotificationValidationService': notifications_notification_validation,
            'acme.patients.v1.PatientQueryService': patients_patient_query,
            'acme.pipelines.v1.PipelineReportingService': pipelines_pipeline_reporting,
            'acme.pipelines.v1.PipelineRunCalculationService': pipelines_pipeline_run_calculation,
            'acme.pipelines.v1.PipelineRunValidationService': pipelines_pipeline_run_validation,
            'acme.pipelines.v1.PipelineStepCalculationService': pipelines_pipeline_step_calculation,
            'acme.pipelines.v1.PipelineStepExportService': pipelines_pipeline_step_export,
            'acme.pipelines.v1.PipelineStepImportService': pipelines_pipeline_step_import,
            'acme.pipelines.v1.PipelineStepValidationService': pipelines_pipeline_step_validation,
            'acme.pipelines.v1.PipelineWorkflowService': pipelines_pipeline_workflow,
            'acme.ratelimiting.v1.RateLimitQueryService': ratelimiting_rate_limit_query,
            'acme.recommendations.v1.InteractionApprovalService': recommendations_interaction_approval,
            'acme.recommendations.v1.RecommendationModelCalculationService': recommendations_recommendation_model_calculation,
            'acme.recommendations.v1.RecommendationModelWorkflowService': recommendations_recommendation_model_workflow,
            'acme.recommendations.v1.RecommendationSetQueryService': recommendations_recommendation_set_query,
            'acme.routing.v1.RouteService': routing_route,
            'acme.search.v1.SearchIndexService': search_search_index,
            'acme.search.v1.SearchIndexValidationService': search_search_index_validation,
            'acme.shows.v1.ShowCalculationService': shows_show_calculation,
            'acme.shows.v1.ShowQueryService': shows_show_query,
            'acme.suppliers.v1.SupplierService': suppliers_supplier,
            'acme.tours.v1.TourQueryService': tours_tour_query,
            'acme.venues.v1.VenueQueryService': venues_venue_query,
            'acme.venues.v1.VenueService': venues_venue,
            'acme.venues.v1.VenueValidationService': venues_venue_validation,
            'acme.webhooks.v1.WebhookEndpointService': webhooks_webhook_endpoint,
        },
    )
    return Dependencies(clients, DomainRepository(container.sessions),
                        container.settings, container.bus)


def register(server: grpc.aio.Server, container: Container) -> dict[str, object]:
    deps = dependencies(container)
    registered: dict[str, object] = {}
    demand_forecast_approval_servicer = Factory(lambda: DemandForecastApprovalServicer(deps))()
    forecasting_v1_demand_forecast_approval_service_pb2_grpc.add_DemandForecastApprovalServiceServicer_to_server(
        demand_forecast_approval_servicer,
        server
    )
    registered['acme.forecasting.v1.DemandForecastApprovalService'] = demand_forecast_approval_servicer
    demand_forecast_query_servicer = Factory(lambda: DemandForecastQueryServicer(deps))()
    forecasting_v1_demand_forecast_query_service_pb2_grpc.add_DemandForecastQueryServiceServicer_to_server(
        demand_forecast_query_servicer,
        server
    )
    registered['acme.forecasting.v1.DemandForecastQueryService'] = demand_forecast_query_servicer
    demand_forecast_servicer = Factory(lambda: DemandForecastServicer(deps))()
    forecasting_v1_demand_forecast_service_pb2_grpc.add_DemandForecastServiceServicer_to_server(
        demand_forecast_servicer,
        server
    )
    registered['acme.forecasting.v1.DemandForecastService'] = demand_forecast_servicer
    demand_forecast_validation_servicer = Factory(lambda: DemandForecastValidationServicer(deps))()
    forecasting_v1_demand_forecast_validation_service_pb2_grpc.add_DemandForecastValidationServiceServicer_to_server(
        demand_forecast_validation_servicer,
        server
    )
    registered['acme.forecasting.v1.DemandForecastValidationService'] = demand_forecast_validation_servicer
    demand_forecast_workflow_servicer = Factory(lambda: DemandForecastWorkflowServicer(deps))()
    forecasting_v1_demand_forecast_workflow_service_pb2_grpc.add_DemandForecastWorkflowServiceServicer_to_server(
        demand_forecast_workflow_servicer,
        server
    )
    registered['acme.forecasting.v1.DemandForecastWorkflowService'] = demand_forecast_workflow_servicer
    forecast_model_approval_servicer = Factory(lambda: ForecastModelApprovalServicer(deps))()
    forecasting_v1_forecast_model_approval_service_pb2_grpc.add_ForecastModelApprovalServiceServicer_to_server(
        forecast_model_approval_servicer,
        server
    )
    registered['acme.forecasting.v1.ForecastModelApprovalService'] = forecast_model_approval_servicer
    forecast_model_query_servicer = Factory(lambda: ForecastModelQueryServicer(deps))()
    forecasting_v1_forecast_model_query_service_pb2_grpc.add_ForecastModelQueryServiceServicer_to_server(
        forecast_model_query_servicer,
        server
    )
    registered['acme.forecasting.v1.ForecastModelQueryService'] = forecast_model_query_servicer
    forecast_model_validation_servicer = Factory(lambda: ForecastModelValidationServicer(deps))()
    forecasting_v1_forecast_model_validation_service_pb2_grpc.add_ForecastModelValidationServiceServicer_to_server(
        forecast_model_validation_servicer,
        server
    )
    registered['acme.forecasting.v1.ForecastModelValidationService'] = forecast_model_validation_servicer
    forecast_model_workflow_servicer = Factory(lambda: ForecastModelWorkflowServicer(deps))()
    forecasting_v1_forecast_model_workflow_service_pb2_grpc.add_ForecastModelWorkflowServiceServicer_to_server(
        forecast_model_workflow_servicer,
        server
    )
    registered['acme.forecasting.v1.ForecastModelWorkflowService'] = forecast_model_workflow_servicer
    scenario_approval_servicer = Factory(lambda: ScenarioApprovalServicer(deps))()
    forecasting_v1_scenario_approval_service_pb2_grpc.add_ScenarioApprovalServiceServicer_to_server(
        scenario_approval_servicer,
        server
    )
    registered['acme.forecasting.v1.ScenarioApprovalService'] = scenario_approval_servicer
    scenario_calculation_servicer = Factory(lambda: ScenarioCalculationServicer(deps))()
    forecasting_v1_scenario_calculation_service_pb2_grpc.add_ScenarioCalculationServiceServicer_to_server(
        scenario_calculation_servicer,
        server
    )
    registered['acme.forecasting.v1.ScenarioCalculationService'] = scenario_calculation_servicer
    scenario_validation_servicer = Factory(lambda: ScenarioValidationServicer(deps))()
    forecasting_v1_scenario_validation_service_pb2_grpc.add_ScenarioValidationServiceServicer_to_server(
        scenario_validation_servicer,
        server
    )
    registered['acme.forecasting.v1.ScenarioValidationService'] = scenario_validation_servicer
    scenario_workflow_servicer = Factory(lambda: ScenarioWorkflowServicer(deps))()
    forecasting_v1_scenario_workflow_service_pb2_grpc.add_ScenarioWorkflowServiceServicer_to_server(
        scenario_workflow_servicer,
        server
    )
    registered['acme.forecasting.v1.ScenarioWorkflowService'] = scenario_workflow_servicer
    subscribe(deps)
    return registered
