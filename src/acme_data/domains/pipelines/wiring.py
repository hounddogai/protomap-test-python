"""Register and compose every service of the pipelines domain."""

from __future__ import annotations

import grpc

from acme.admissions.v1 import admission_query_service_pb2_grpc as admissions_v1_admission_query_service_pb2_grpc
from acme.anomalies.v1 import anomaly_approval_service_pb2_grpc as anomalies_v1_anomaly_approval_service_pb2_grpc
from acme.anomalies.v1 import (
    anomaly_feedback_calculation_service_pb2_grpc as anomalies_v1_anomaly_feedback_calculation_service_pb2_grpc,
)
from acme.anomalies.v1 import anomaly_query_service_pb2_grpc as anomalies_v1_anomaly_query_service_pb2_grpc
from acme.anomalies.v1 import anomaly_workflow_service_pb2_grpc as anomalies_v1_anomaly_workflow_service_pb2_grpc
from acme.anomalies.v1 import detector_approval_service_pb2_grpc as anomalies_v1_detector_approval_service_pb2_grpc
from acme.anomalies.v1 import detector_query_service_pb2_grpc as anomalies_v1_detector_query_service_pb2_grpc
from acme.appointments.v1 import appointment_service_pb2_grpc as appointments_v1_appointment_service_pb2_grpc
from acme.assets.v1 import fixed_asset_query_service_pb2_grpc as assets_v1_fixed_asset_query_service_pb2_grpc
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
from acme.broadcasts.v1 import broadcast_service_pb2_grpc as broadcasts_v1_broadcast_service_pb2_grpc
from acme.careplans.v1 import (
    care_plan_calculation_service_pb2_grpc as careplans_v1_care_plan_calculation_service_pb2_grpc,
)
from acme.careplans.v1 import care_plan_query_service_pb2_grpc as careplans_v1_care_plan_query_service_pb2_grpc
from acme.careplans.v1 import care_plan_service_pb2_grpc as careplans_v1_care_plan_service_pb2_grpc
from acme.cart.v1 import cart_query_service_pb2_grpc as cart_v1_cart_query_service_pb2_grpc
from acme.chat.v1 import chat_room_service_pb2_grpc as chat_v1_chat_room_service_pb2_grpc
from acme.community.v1 import forum_query_service_pb2_grpc as community_v1_forum_query_service_pb2_grpc
from acme.compliance.v1 import (
    compliance_case_query_service_pb2_grpc as compliance_v1_compliance_case_query_service_pb2_grpc,
)
from acme.concessions.v1 import concession_stand_service_pb2_grpc as concessions_v1_concession_stand_service_pb2_grpc
from acme.dispatch.v1 import dispatch_order_query_service_pb2_grpc as dispatch_v1_dispatch_order_query_service_pb2_grpc
from acme.documents.v1 import document_query_service_pb2_grpc as documents_v1_document_query_service_pb2_grpc
from acme.documents.v1 import document_service_pb2_grpc as documents_v1_document_service_pb2_grpc
from acme.documents.v1 import document_validation_service_pb2_grpc as documents_v1_document_validation_service_pb2_grpc
from acme.drivers.v1 import driver_calculation_service_pb2_grpc as drivers_v1_driver_calculation_service_pb2_grpc
from acme.drivers.v1 import driver_query_service_pb2_grpc as drivers_v1_driver_query_service_pb2_grpc
from acme.expenses.v1 import expense_report_query_service_pb2_grpc as expenses_v1_expense_report_query_service_pb2_grpc
from acme.featureflags.v1 import (
    feature_flag_validation_service_pb2_grpc as featureflags_v1_feature_flag_validation_service_pb2_grpc,
)
from acme.featurestore.v1 import entity_approval_service_pb2_grpc as featurestore_v1_entity_approval_service_pb2_grpc
from acme.featurestore.v1 import entity_import_service_pb2_grpc as featurestore_v1_entity_import_service_pb2_grpc
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
    feature_value_import_service_pb2_grpc as featurestore_v1_feature_value_import_service_pb2_grpc,
)
from acme.featurestore.v1 import (
    feature_value_query_service_pb2_grpc as featurestore_v1_feature_value_query_service_pb2_grpc,
)
from acme.featurestore.v1 import (
    feature_value_reporting_service_pb2_grpc as featurestore_v1_feature_value_reporting_service_pb2_grpc,
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
    feature_view_query_service_pb2_grpc as featurestore_v1_feature_view_query_service_pb2_grpc,
)
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
from acme.forms.v1 import form_query_service_pb2_grpc as forms_v1_form_query_service_pb2_grpc
from acme.fulfillment.v1 import fulfillment_query_service_pb2_grpc as fulfillment_v1_fulfillment_query_service_pb2_grpc
from acme.helpdesk.v1 import ticket_service_pb2_grpc as helpdesk_v1_ticket_service_pb2_grpc
from acme.identity.v1 import user_query_service_pb2_grpc as identity_v1_user_query_service_pb2_grpc
from acme.identity.v1 import user_service_pb2_grpc as identity_v1_user_service_pb2_grpc
from acme.identity.v1 import user_validation_service_pb2_grpc as identity_v1_user_validation_service_pb2_grpc
from acme.itsm.v1 import incident_service_pb2_grpc as itsm_v1_incident_service_pb2_grpc
from acme.keymanagement.v1 import crypto_key_service_pb2_grpc as keymanagement_v1_crypto_key_service_pb2_grpc
from acme.labeling.v1 import annotation_approval_service_pb2_grpc as labeling_v1_annotation_approval_service_pb2_grpc
from acme.labeling.v1 import (
    annotation_validation_service_pb2_grpc as labeling_v1_annotation_validation_service_pb2_grpc,
)
from acme.labeling.v1 import label_set_approval_service_pb2_grpc as labeling_v1_label_set_approval_service_pb2_grpc
from acme.labeling.v1 import (
    label_set_calculation_service_pb2_grpc as labeling_v1_label_set_calculation_service_pb2_grpc,
)
from acme.labeling.v1 import label_set_sync_service_pb2_grpc as labeling_v1_label_set_sync_service_pb2_grpc
from acme.labeling.v1 import label_set_validation_service_pb2_grpc as labeling_v1_label_set_validation_service_pb2_grpc
from acme.labeling.v1 import labeling_task_query_service_pb2_grpc as labeling_v1_labeling_task_query_service_pb2_grpc
from acme.labeling.v1 import labeling_task_service_pb2_grpc as labeling_v1_labeling_task_service_pb2_grpc
from acme.labeling.v1 import (
    labeling_task_workflow_service_pb2_grpc as labeling_v1_labeling_task_workflow_service_pb2_grpc,
)
from acme.ledger.v1 import ledger_account_query_service_pb2_grpc as ledger_v1_ledger_account_query_service_pb2_grpc
from acme.ledger.v1 import ledger_account_service_pb2_grpc as ledger_v1_ledger_account_service_pb2_grpc
from acme.ledger.v1 import (
    ledger_account_validation_service_pb2_grpc as ledger_v1_ledger_account_validation_service_pb2_grpc,
)
from acme.lending.v1 import (
    loan_application_query_service_pb2_grpc as lending_v1_loan_application_query_service_pb2_grpc,
)
from acme.lineage.v1 import impact_approval_service_pb2_grpc as lineage_v1_impact_approval_service_pb2_grpc
from acme.lineage.v1 import impact_lifecycle_service_pb2_grpc as lineage_v1_impact_lifecycle_service_pb2_grpc
from acme.lineage.v1 import impact_reporting_service_pb2_grpc as lineage_v1_impact_reporting_service_pb2_grpc
from acme.lineage.v1 import impact_sync_service_pb2_grpc as lineage_v1_impact_sync_service_pb2_grpc
from acme.lineage.v1 import impact_validation_service_pb2_grpc as lineage_v1_impact_validation_service_pb2_grpc
from acme.lineage.v1 import lineage_edge_approval_service_pb2_grpc as lineage_v1_lineage_edge_approval_service_pb2_grpc
from acme.lineage.v1 import (
    lineage_edge_calculation_service_pb2_grpc as lineage_v1_lineage_edge_calculation_service_pb2_grpc,
)
from acme.lineage.v1 import lineage_edge_import_service_pb2_grpc as lineage_v1_lineage_edge_import_service_pb2_grpc
from acme.lineage.v1 import lineage_edge_sync_service_pb2_grpc as lineage_v1_lineage_edge_sync_service_pb2_grpc
from acme.lineage.v1 import lineage_node_approval_service_pb2_grpc as lineage_v1_lineage_node_approval_service_pb2_grpc
from acme.lineage.v1 import lineage_node_service_pb2_grpc as lineage_v1_lineage_node_service_pb2_grpc
from acme.maintenance.v1 import (
    work_order_calculation_service_pb2_grpc as maintenance_v1_work_order_calculation_service_pb2_grpc,
)
from acme.metrics.v1 import dashboard_admin_service_pb2_grpc as metrics_v1_dashboard_admin_service_pb2_grpc
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
    deployment_approval_service_pb2_grpc as modelregistry_v1_deployment_approval_service_pb2_grpc,
)
from acme.modelregistry.v1 import (
    deployment_import_service_pb2_grpc as modelregistry_v1_deployment_import_service_pb2_grpc,
)
from acme.modelregistry.v1 import deployment_sync_service_pb2_grpc as modelregistry_v1_deployment_sync_service_pb2_grpc
from acme.modelregistry.v1 import (
    deployment_validation_service_pb2_grpc as modelregistry_v1_deployment_validation_service_pb2_grpc,
)
from acme.modelregistry.v1 import (
    model_version_lifecycle_service_pb2_grpc as modelregistry_v1_model_version_lifecycle_service_pb2_grpc,
)
from acme.modelregistry.v1 import (
    model_version_reporting_service_pb2_grpc as modelregistry_v1_model_version_reporting_service_pb2_grpc,
)
from acme.modelregistry.v1 import (
    model_version_validation_service_pb2_grpc as modelregistry_v1_model_version_validation_service_pb2_grpc,
)
from acme.modelregistry.v1 import (
    registered_model_approval_service_pb2_grpc as modelregistry_v1_registered_model_approval_service_pb2_grpc,
)
from acme.modelregistry.v1 import (
    registered_model_query_service_pb2_grpc as modelregistry_v1_registered_model_query_service_pb2_grpc,
)
from acme.modelregistry.v1 import (
    registered_model_reporting_service_pb2_grpc as modelregistry_v1_registered_model_reporting_service_pb2_grpc,
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
from acme.notifications.v1 import notification_service_pb2_grpc as notifications_v1_notification_service_pb2_grpc
from acme.patients.v1 import patient_calculation_service_pb2_grpc as patients_v1_patient_calculation_service_pb2_grpc
from acme.pipelines.v1 import pipeline_approval_service_pb2_grpc as pipelines_v1_pipeline_approval_service_pb2_grpc
from acme.pipelines.v1 import (
    pipeline_calculation_service_pb2_grpc as pipelines_v1_pipeline_calculation_service_pb2_grpc,
)
from acme.pipelines.v1 import pipeline_lifecycle_service_pb2_grpc as pipelines_v1_pipeline_lifecycle_service_pb2_grpc
from acme.pipelines.v1 import pipeline_query_service_pb2_grpc as pipelines_v1_pipeline_query_service_pb2_grpc
from acme.pipelines.v1 import pipeline_reporting_service_pb2_grpc as pipelines_v1_pipeline_reporting_service_pb2_grpc
from acme.pipelines.v1 import (
    pipeline_run_approval_service_pb2_grpc as pipelines_v1_pipeline_run_approval_service_pb2_grpc,
)
from acme.pipelines.v1 import (
    pipeline_run_calculation_service_pb2_grpc as pipelines_v1_pipeline_run_calculation_service_pb2_grpc,
)
from acme.pipelines.v1 import pipeline_run_import_service_pb2_grpc as pipelines_v1_pipeline_run_import_service_pb2_grpc
from acme.pipelines.v1 import (
    pipeline_run_lifecycle_service_pb2_grpc as pipelines_v1_pipeline_run_lifecycle_service_pb2_grpc,
)
from acme.pipelines.v1 import pipeline_run_query_service_pb2_grpc as pipelines_v1_pipeline_run_query_service_pb2_grpc
from acme.pipelines.v1 import (
    pipeline_run_reporting_service_pb2_grpc as pipelines_v1_pipeline_run_reporting_service_pb2_grpc,
)
from acme.pipelines.v1 import pipeline_run_sync_service_pb2_grpc as pipelines_v1_pipeline_run_sync_service_pb2_grpc
from acme.pipelines.v1 import (
    pipeline_run_validation_service_pb2_grpc as pipelines_v1_pipeline_run_validation_service_pb2_grpc,
)
from acme.pipelines.v1 import (
    pipeline_run_workflow_service_pb2_grpc as pipelines_v1_pipeline_run_workflow_service_pb2_grpc,
)
from acme.pipelines.v1 import pipeline_service_pb2_grpc as pipelines_v1_pipeline_service_pb2_grpc
from acme.pipelines.v1 import (
    pipeline_step_approval_service_pb2_grpc as pipelines_v1_pipeline_step_approval_service_pb2_grpc,
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
    pipeline_step_lifecycle_service_pb2_grpc as pipelines_v1_pipeline_step_lifecycle_service_pb2_grpc,
)
from acme.pipelines.v1 import (
    pipeline_step_reporting_service_pb2_grpc as pipelines_v1_pipeline_step_reporting_service_pb2_grpc,
)
from acme.pipelines.v1 import pipeline_step_sync_service_pb2_grpc as pipelines_v1_pipeline_step_sync_service_pb2_grpc
from acme.pipelines.v1 import (
    pipeline_step_validation_service_pb2_grpc as pipelines_v1_pipeline_step_validation_service_pb2_grpc,
)
from acme.pipelines.v1 import (
    pipeline_step_workflow_service_pb2_grpc as pipelines_v1_pipeline_step_workflow_service_pb2_grpc,
)
from acme.pipelines.v1 import pipeline_sync_service_pb2_grpc as pipelines_v1_pipeline_sync_service_pb2_grpc
from acme.pipelines.v1 import pipeline_validation_service_pb2_grpc as pipelines_v1_pipeline_validation_service_pb2_grpc
from acme.pipelines.v1 import pipeline_workflow_service_pb2_grpc as pipelines_v1_pipeline_workflow_service_pb2_grpc
from acme.prescriptions.v1 import (
    prescription_query_service_pb2_grpc as prescriptions_v1_prescription_query_service_pb2_grpc,
)
from acme.pricing.v1 import price_list_service_pb2_grpc as pricing_v1_price_list_service_pb2_grpc
from acme.promotions.v1 import promotion_query_service_pb2_grpc as promotions_v1_promotion_query_service_pb2_grpc
from acme.ratelimiting.v1 import rate_limit_query_service_pb2_grpc as ratelimiting_v1_rate_limit_query_service_pb2_grpc
from acme.recruiting.v1 import job_opening_service_pb2_grpc as recruiting_v1_job_opening_service_pb2_grpc
from acme.routing.v1 import route_service_pb2_grpc as routing_v1_route_service_pb2_grpc
from acme.search.v1 import search_index_query_service_pb2_grpc as search_v1_search_index_query_service_pb2_grpc
from acme.search.v1 import search_index_service_pb2_grpc as search_v1_search_index_service_pb2_grpc
from acme.search.v1 import (
    search_index_validation_service_pb2_grpc as search_v1_search_index_validation_service_pb2_grpc,
)
from acme.seating.v1 import seat_map_service_pb2_grpc as seating_v1_seat_map_service_pb2_grpc
from acme.telematics.v1 import (
    telemetry_reading_query_service_pb2_grpc as telematics_v1_telemetry_reading_query_service_pb2_grpc,
)
from acme.ticketing.v1 import ticket_query_service_pb2_grpc as ticketing_v1_ticket_query_service_pb2_grpc
from acme.timekeeping.v1 import timesheet_service_pb2_grpc as timekeeping_v1_timesheet_service_pb2_grpc
from acme.treasury.v1 import cash_position_query_service_pb2_grpc as treasury_v1_cash_position_query_service_pb2_grpc
from acme.venues.v1 import venue_query_service_pb2_grpc as venues_v1_venue_query_service_pb2_grpc
from acme.venues.v1 import venue_service_pb2_grpc as venues_v1_venue_service_pb2_grpc
from acme.venues.v1 import venue_validation_service_pb2_grpc as venues_v1_venue_validation_service_pb2_grpc
from acme.yards.v1 import yard_calculation_service_pb2_grpc as yards_v1_yard_calculation_service_pb2_grpc
from acme.yards.v1 import yard_query_service_pb2_grpc as yards_v1_yard_query_service_pb2_grpc

from acme_data.domains.pipelines.dependencies import Clients
from acme_data.domains.pipelines.dependencies import Dependencies
from acme_data.domains.pipelines.events import subscribe
from acme_data.domains.pipelines.pipeline_approval_service import PipelineApprovalServicer
from acme_data.domains.pipelines.pipeline_calculation_service import PipelineCalculationServicer
from acme_data.domains.pipelines.pipeline_lifecycle_service import PipelineLifecycleServicer
from acme_data.domains.pipelines.pipeline_query_service import PipelineQueryServicer
from acme_data.domains.pipelines.pipeline_reporting_service import PipelineReportingServicer
from acme_data.domains.pipelines.pipeline_run_approval_service import PipelineRunApprovalServicer
from acme_data.domains.pipelines.pipeline_run_calculation_service import PipelineRunCalculationServicer
from acme_data.domains.pipelines.pipeline_run_import_service import PipelineRunImportServicer
from acme_data.domains.pipelines.pipeline_run_lifecycle_service import PipelineRunLifecycleServicer
from acme_data.domains.pipelines.pipeline_run_query_service import PipelineRunQueryServicer
from acme_data.domains.pipelines.pipeline_run_reporting_service import PipelineRunReportingServicer
from acme_data.domains.pipelines.pipeline_run_sync_service import PipelineRunSyncServicer
from acme_data.domains.pipelines.pipeline_run_validation_service import PipelineRunValidationServicer
from acme_data.domains.pipelines.pipeline_run_workflow_service import PipelineRunWorkflowServicer
from acme_data.domains.pipelines.pipeline_service import PipelineServicer
from acme_data.domains.pipelines.pipeline_step_approval_service import PipelineStepApprovalServicer
from acme_data.domains.pipelines.pipeline_step_calculation_service import PipelineStepCalculationServicer
from acme_data.domains.pipelines.pipeline_step_export_service import PipelineStepExportServicer
from acme_data.domains.pipelines.pipeline_step_import_service import PipelineStepImportServicer
from acme_data.domains.pipelines.pipeline_step_lifecycle_service import PipelineStepLifecycleServicer
from acme_data.domains.pipelines.pipeline_step_reporting_service import PipelineStepReportingServicer
from acme_data.domains.pipelines.pipeline_step_sync_service import PipelineStepSyncServicer
from acme_data.domains.pipelines.pipeline_step_validation_service import PipelineStepValidationServicer
from acme_data.domains.pipelines.pipeline_step_workflow_service import PipelineStepWorkflowServicer
from acme_data.domains.pipelines.pipeline_sync_service import PipelineSyncServicer
from acme_data.domains.pipelines.pipeline_validation_service import PipelineValidationServicer
from acme_data.domains.pipelines.pipeline_workflow_service import PipelineWorkflowServicer
from acme_data.domains.pipelines.repository import DomainRepository
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
    appointments_appointment = container.singleton(
        appointments_v1_appointment_service_pb2_grpc.AppointmentServiceStub,
        lambda: appointments_v1_appointment_service_pb2_grpc.AppointmentServiceStub(container.channel)
    )
    assets_fixed_asset_query = container.singleton(
        assets_v1_fixed_asset_query_service_pb2_grpc.FixedAssetQueryServiceStub,
        lambda: assets_v1_fixed_asset_query_service_pb2_grpc.FixedAssetQueryServiceStub(container.channel)
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
    broadcasts_broadcast = container.singleton(
        broadcasts_v1_broadcast_service_pb2_grpc.BroadcastServiceStub,
        lambda: broadcasts_v1_broadcast_service_pb2_grpc.BroadcastServiceStub(container.channel)
    )
    careplans_care_plan_calculation = container.singleton(
        careplans_v1_care_plan_calculation_service_pb2_grpc.CarePlanCalculationServiceStub,
        lambda: careplans_v1_care_plan_calculation_service_pb2_grpc.CarePlanCalculationServiceStub(container.channel)
    )
    careplans_care_plan_query = container.singleton(
        careplans_v1_care_plan_query_service_pb2_grpc.CarePlanQueryServiceStub,
        lambda: careplans_v1_care_plan_query_service_pb2_grpc.CarePlanQueryServiceStub(container.channel)
    )
    careplans_care_plan = container.singleton(
        careplans_v1_care_plan_service_pb2_grpc.CarePlanServiceStub,
        lambda: careplans_v1_care_plan_service_pb2_grpc.CarePlanServiceStub(container.channel)
    )
    cart_cart_query = container.singleton(
        cart_v1_cart_query_service_pb2_grpc.CartQueryServiceStub,
        lambda: cart_v1_cart_query_service_pb2_grpc.CartQueryServiceStub(container.channel)
    )
    chat_chat_room = container.singleton(
        chat_v1_chat_room_service_pb2_grpc.ChatRoomServiceStub,
        lambda: chat_v1_chat_room_service_pb2_grpc.ChatRoomServiceStub(container.channel)
    )
    community_forum_query = container.singleton(
        community_v1_forum_query_service_pb2_grpc.ForumQueryServiceStub,
        lambda: community_v1_forum_query_service_pb2_grpc.ForumQueryServiceStub(container.channel)
    )
    compliance_compliance_case_query = container.singleton(
        compliance_v1_compliance_case_query_service_pb2_grpc.ComplianceCaseQueryServiceStub,
        lambda: compliance_v1_compliance_case_query_service_pb2_grpc.ComplianceCaseQueryServiceStub(container.channel)
    )
    concessions_concession_stand = container.singleton(
        concessions_v1_concession_stand_service_pb2_grpc.ConcessionStandServiceStub,
        lambda: concessions_v1_concession_stand_service_pb2_grpc.ConcessionStandServiceStub(container.channel)
    )
    dispatch_dispatch_order_query = container.singleton(
        dispatch_v1_dispatch_order_query_service_pb2_grpc.DispatchOrderQueryServiceStub,
        lambda: dispatch_v1_dispatch_order_query_service_pb2_grpc.DispatchOrderQueryServiceStub(container.channel)
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
    drivers_driver_calculation = container.singleton(
        drivers_v1_driver_calculation_service_pb2_grpc.DriverCalculationServiceStub,
        lambda: drivers_v1_driver_calculation_service_pb2_grpc.DriverCalculationServiceStub(container.channel)
    )
    drivers_driver_query = container.singleton(
        drivers_v1_driver_query_service_pb2_grpc.DriverQueryServiceStub,
        lambda: drivers_v1_driver_query_service_pb2_grpc.DriverQueryServiceStub(container.channel)
    )
    expenses_expense_report_query = container.singleton(
        expenses_v1_expense_report_query_service_pb2_grpc.ExpenseReportQueryServiceStub,
        lambda: expenses_v1_expense_report_query_service_pb2_grpc.ExpenseReportQueryServiceStub(container.channel)
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
    featurestore_entity_import = container.singleton(
        featurestore_v1_entity_import_service_pb2_grpc.EntityImportServiceStub,
        lambda: featurestore_v1_entity_import_service_pb2_grpc.EntityImportServiceStub(container.channel)
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
    featurestore_entity_workflow = container.singleton(
        featurestore_v1_entity_workflow_service_pb2_grpc.EntityWorkflowServiceStub,
        lambda: featurestore_v1_entity_workflow_service_pb2_grpc.EntityWorkflowServiceStub(container.channel)
    )
    featurestore_feature_value_approval = container.singleton(
        featurestore_v1_feature_value_approval_service_pb2_grpc.FeatureValueApprovalServiceStub,
        lambda: featurestore_v1_feature_value_approval_service_pb2_grpc.FeatureValueApprovalServiceStub(
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
    fleet_vehicle = container.singleton(
        fleet_v1_vehicle_service_pb2_grpc.VehicleServiceStub,
        lambda: fleet_v1_vehicle_service_pb2_grpc.VehicleServiceStub(container.channel)
    )
    forms_form_query = container.singleton(
        forms_v1_form_query_service_pb2_grpc.FormQueryServiceStub,
        lambda: forms_v1_form_query_service_pb2_grpc.FormQueryServiceStub(container.channel)
    )
    fulfillment_fulfillment_query = container.singleton(
        fulfillment_v1_fulfillment_query_service_pb2_grpc.FulfillmentQueryServiceStub,
        lambda: fulfillment_v1_fulfillment_query_service_pb2_grpc.FulfillmentQueryServiceStub(container.channel)
    )
    helpdesk_ticket = container.singleton(
        helpdesk_v1_ticket_service_pb2_grpc.TicketServiceStub,
        lambda: helpdesk_v1_ticket_service_pb2_grpc.TicketServiceStub(container.channel)
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
    itsm_incident = container.singleton(
        itsm_v1_incident_service_pb2_grpc.IncidentServiceStub,
        lambda: itsm_v1_incident_service_pb2_grpc.IncidentServiceStub(container.channel)
    )
    keymanagement_crypto_key = container.singleton(
        keymanagement_v1_crypto_key_service_pb2_grpc.CryptoKeyServiceStub,
        lambda: keymanagement_v1_crypto_key_service_pb2_grpc.CryptoKeyServiceStub(container.channel)
    )
    labeling_annotation_approval = container.singleton(
        labeling_v1_annotation_approval_service_pb2_grpc.AnnotationApprovalServiceStub,
        lambda: labeling_v1_annotation_approval_service_pb2_grpc.AnnotationApprovalServiceStub(container.channel)
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
    labeling_label_set_sync = container.singleton(
        labeling_v1_label_set_sync_service_pb2_grpc.LabelSetSyncServiceStub,
        lambda: labeling_v1_label_set_sync_service_pb2_grpc.LabelSetSyncServiceStub(container.channel)
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
    labeling_labeling_task_workflow = container.singleton(
        labeling_v1_labeling_task_workflow_service_pb2_grpc.LabelingTaskWorkflowServiceStub,
        lambda: labeling_v1_labeling_task_workflow_service_pb2_grpc.LabelingTaskWorkflowServiceStub(container.channel)
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
    lending_loan_application_query = container.singleton(
        lending_v1_loan_application_query_service_pb2_grpc.LoanApplicationQueryServiceStub,
        lambda: lending_v1_loan_application_query_service_pb2_grpc.LoanApplicationQueryServiceStub(container.channel)
    )
    lineage_impact_approval = container.singleton(
        lineage_v1_impact_approval_service_pb2_grpc.ImpactApprovalServiceStub,
        lambda: lineage_v1_impact_approval_service_pb2_grpc.ImpactApprovalServiceStub(container.channel)
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
    lineage_lineage_edge_sync = container.singleton(
        lineage_v1_lineage_edge_sync_service_pb2_grpc.LineageEdgeSyncServiceStub,
        lambda: lineage_v1_lineage_edge_sync_service_pb2_grpc.LineageEdgeSyncServiceStub(container.channel)
    )
    lineage_lineage_node_approval = container.singleton(
        lineage_v1_lineage_node_approval_service_pb2_grpc.LineageNodeApprovalServiceStub,
        lambda: lineage_v1_lineage_node_approval_service_pb2_grpc.LineageNodeApprovalServiceStub(container.channel)
    )
    lineage_lineage_node = container.singleton(
        lineage_v1_lineage_node_service_pb2_grpc.LineageNodeServiceStub,
        lambda: lineage_v1_lineage_node_service_pb2_grpc.LineageNodeServiceStub(container.channel)
    )
    maintenance_work_order_calculation = container.singleton(
        maintenance_v1_work_order_calculation_service_pb2_grpc.WorkOrderCalculationServiceStub,
        lambda: maintenance_v1_work_order_calculation_service_pb2_grpc.WorkOrderCalculationServiceStub(
            container.channel
        )
    )
    metrics_dashboard_admin = container.singleton(
        metrics_v1_dashboard_admin_service_pb2_grpc.DashboardAdminServiceStub,
        lambda: metrics_v1_dashboard_admin_service_pb2_grpc.DashboardAdminServiceStub(container.channel)
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
    modelregistry_model_version_reporting = container.singleton(
        modelregistry_v1_model_version_reporting_service_pb2_grpc.ModelVersionReportingServiceStub,
        lambda: modelregistry_v1_model_version_reporting_service_pb2_grpc.ModelVersionReportingServiceStub(
            container.channel
        )
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
    modelregistry_registered_model_workflow = container.singleton(
        modelregistry_v1_registered_model_workflow_service_pb2_grpc.RegisteredModelWorkflowServiceStub,
        lambda: modelregistry_v1_registered_model_workflow_service_pb2_grpc.RegisteredModelWorkflowServiceStub(
            container.channel
        )
    )
    notifications_notification = container.singleton(
        notifications_v1_notification_service_pb2_grpc.NotificationServiceStub,
        lambda: notifications_v1_notification_service_pb2_grpc.NotificationServiceStub(container.channel)
    )
    patients_patient_calculation = container.singleton(
        patients_v1_patient_calculation_service_pb2_grpc.PatientCalculationServiceStub,
        lambda: patients_v1_patient_calculation_service_pb2_grpc.PatientCalculationServiceStub(container.channel)
    )
    pipelines_pipeline_approval = container.singleton(
        pipelines_v1_pipeline_approval_service_pb2_grpc.PipelineApprovalServiceStub,
        lambda: pipelines_v1_pipeline_approval_service_pb2_grpc.PipelineApprovalServiceStub(container.channel)
    )
    pipelines_pipeline_calculation = container.singleton(
        pipelines_v1_pipeline_calculation_service_pb2_grpc.PipelineCalculationServiceStub,
        lambda: pipelines_v1_pipeline_calculation_service_pb2_grpc.PipelineCalculationServiceStub(container.channel)
    )
    pipelines_pipeline_lifecycle = container.singleton(
        pipelines_v1_pipeline_lifecycle_service_pb2_grpc.PipelineLifecycleServiceStub,
        lambda: pipelines_v1_pipeline_lifecycle_service_pb2_grpc.PipelineLifecycleServiceStub(container.channel)
    )
    pipelines_pipeline_query = container.singleton(
        pipelines_v1_pipeline_query_service_pb2_grpc.PipelineQueryServiceStub,
        lambda: pipelines_v1_pipeline_query_service_pb2_grpc.PipelineQueryServiceStub(container.channel)
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
    pipelines_pipeline_run_import = container.singleton(
        pipelines_v1_pipeline_run_import_service_pb2_grpc.PipelineRunImportServiceStub,
        lambda: pipelines_v1_pipeline_run_import_service_pb2_grpc.PipelineRunImportServiceStub(container.channel)
    )
    pipelines_pipeline_run_lifecycle = container.singleton(
        pipelines_v1_pipeline_run_lifecycle_service_pb2_grpc.PipelineRunLifecycleServiceStub,
        lambda: pipelines_v1_pipeline_run_lifecycle_service_pb2_grpc.PipelineRunLifecycleServiceStub(container.channel)
    )
    pipelines_pipeline_run_query = container.singleton(
        pipelines_v1_pipeline_run_query_service_pb2_grpc.PipelineRunQueryServiceStub,
        lambda: pipelines_v1_pipeline_run_query_service_pb2_grpc.PipelineRunQueryServiceStub(container.channel)
    )
    pipelines_pipeline_run_reporting = container.singleton(
        pipelines_v1_pipeline_run_reporting_service_pb2_grpc.PipelineRunReportingServiceStub,
        lambda: pipelines_v1_pipeline_run_reporting_service_pb2_grpc.PipelineRunReportingServiceStub(container.channel)
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
    pipelines_pipeline = container.singleton(
        pipelines_v1_pipeline_service_pb2_grpc.PipelineServiceStub,
        lambda: pipelines_v1_pipeline_service_pb2_grpc.PipelineServiceStub(container.channel)
    )
    pipelines_pipeline_step_approval = container.singleton(
        pipelines_v1_pipeline_step_approval_service_pb2_grpc.PipelineStepApprovalServiceStub,
        lambda: pipelines_v1_pipeline_step_approval_service_pb2_grpc.PipelineStepApprovalServiceStub(container.channel)
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
    pipelines_pipeline_step_lifecycle = container.singleton(
        pipelines_v1_pipeline_step_lifecycle_service_pb2_grpc.PipelineStepLifecycleServiceStub,
        lambda: pipelines_v1_pipeline_step_lifecycle_service_pb2_grpc.PipelineStepLifecycleServiceStub(
            container.channel
        )
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
    pipelines_pipeline_step_validation = container.singleton(
        pipelines_v1_pipeline_step_validation_service_pb2_grpc.PipelineStepValidationServiceStub,
        lambda: pipelines_v1_pipeline_step_validation_service_pb2_grpc.PipelineStepValidationServiceStub(
            container.channel
        )
    )
    pipelines_pipeline_sync = container.singleton(
        pipelines_v1_pipeline_sync_service_pb2_grpc.PipelineSyncServiceStub,
        lambda: pipelines_v1_pipeline_sync_service_pb2_grpc.PipelineSyncServiceStub(container.channel)
    )
    pipelines_pipeline_validation = container.singleton(
        pipelines_v1_pipeline_validation_service_pb2_grpc.PipelineValidationServiceStub,
        lambda: pipelines_v1_pipeline_validation_service_pb2_grpc.PipelineValidationServiceStub(container.channel)
    )
    prescriptions_prescription_query = container.singleton(
        prescriptions_v1_prescription_query_service_pb2_grpc.PrescriptionQueryServiceStub,
        lambda: prescriptions_v1_prescription_query_service_pb2_grpc.PrescriptionQueryServiceStub(container.channel)
    )
    pricing_price_list = container.singleton(
        pricing_v1_price_list_service_pb2_grpc.PriceListServiceStub,
        lambda: pricing_v1_price_list_service_pb2_grpc.PriceListServiceStub(container.channel)
    )
    promotions_promotion_query = container.singleton(
        promotions_v1_promotion_query_service_pb2_grpc.PromotionQueryServiceStub,
        lambda: promotions_v1_promotion_query_service_pb2_grpc.PromotionQueryServiceStub(container.channel)
    )
    ratelimiting_rate_limit_query = container.singleton(
        ratelimiting_v1_rate_limit_query_service_pb2_grpc.RateLimitQueryServiceStub,
        lambda: ratelimiting_v1_rate_limit_query_service_pb2_grpc.RateLimitQueryServiceStub(container.channel)
    )
    recruiting_job_opening = container.singleton(
        recruiting_v1_job_opening_service_pb2_grpc.JobOpeningServiceStub,
        lambda: recruiting_v1_job_opening_service_pb2_grpc.JobOpeningServiceStub(container.channel)
    )
    routing_route = container.singleton(
        routing_v1_route_service_pb2_grpc.RouteServiceStub,
        lambda: routing_v1_route_service_pb2_grpc.RouteServiceStub(container.channel)
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
    telematics_telemetry_reading_query = container.singleton(
        telematics_v1_telemetry_reading_query_service_pb2_grpc.TelemetryReadingQueryServiceStub,
        lambda: telematics_v1_telemetry_reading_query_service_pb2_grpc.TelemetryReadingQueryServiceStub(
            container.channel
        )
    )
    ticketing_ticket_query = container.singleton(
        ticketing_v1_ticket_query_service_pb2_grpc.TicketQueryServiceStub,
        lambda: ticketing_v1_ticket_query_service_pb2_grpc.TicketQueryServiceStub(container.channel)
    )
    timekeeping_timesheet = container.singleton(
        timekeeping_v1_timesheet_service_pb2_grpc.TimesheetServiceStub,
        lambda: timekeeping_v1_timesheet_service_pb2_grpc.TimesheetServiceStub(container.channel)
    )
    treasury_cash_position_query = container.singleton(
        treasury_v1_cash_position_query_service_pb2_grpc.CashPositionQueryServiceStub,
        lambda: treasury_v1_cash_position_query_service_pb2_grpc.CashPositionQueryServiceStub(container.channel)
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
    yards_yard_calculation = container.singleton(
        yards_v1_yard_calculation_service_pb2_grpc.YardCalculationServiceStub,
        lambda: yards_v1_yard_calculation_service_pb2_grpc.YardCalculationServiceStub(container.channel)
    )
    yards_yard_query = container.singleton(
        yards_v1_yard_query_service_pb2_grpc.YardQueryServiceStub,
        lambda: yards_v1_yard_query_service_pb2_grpc.YardQueryServiceStub(container.channel)
    )
    clients = Clients(
        admissions_admission_query=admissions_admission_query,
        anomalies_anomaly_approval=anomalies_anomaly_approval,
        anomalies_anomaly_feedback_calculation=anomalies_anomaly_feedback_calculation,
        anomalies_anomaly_query=anomalies_anomaly_query,
        anomalies_anomaly_workflow=anomalies_anomaly_workflow,
        anomalies_detector_approval=anomalies_detector_approval,
        anomalies_detector_query=anomalies_detector_query,
        appointments_appointment=appointments_appointment,
        assets_fixed_asset_query=assets_fixed_asset_query,
        audit_audit_event_query=audit_audit_event_query,
        audit_audit_event=audit_audit_event,
        audit_audit_event_validation=audit_audit_event_validation,
        authorization_access_policy_query=authorization_access_policy_query,
        authorization_access_policy=authorization_access_policy,
        authorization_access_policy_validation=authorization_access_policy_validation,
        broadcasts_broadcast=broadcasts_broadcast,
        careplans_care_plan_calculation=careplans_care_plan_calculation,
        careplans_care_plan_query=careplans_care_plan_query,
        careplans_care_plan=careplans_care_plan,
        cart_cart_query=cart_cart_query,
        chat_chat_room=chat_chat_room,
        community_forum_query=community_forum_query,
        compliance_compliance_case_query=compliance_compliance_case_query,
        concessions_concession_stand=concessions_concession_stand,
        dispatch_dispatch_order_query=dispatch_dispatch_order_query,
        documents_document_query=documents_document_query,
        documents_document=documents_document,
        documents_document_validation=documents_document_validation,
        drivers_driver_calculation=drivers_driver_calculation,
        drivers_driver_query=drivers_driver_query,
        expenses_expense_report_query=expenses_expense_report_query,
        featureflags_feature_flag_validation=featureflags_feature_flag_validation,
        featurestore_entity_approval=featurestore_entity_approval,
        featurestore_entity_import=featurestore_entity_import,
        featurestore_entity_reporting=featurestore_entity_reporting,
        featurestore_entity_sync=featurestore_entity_sync,
        featurestore_entity_validation=featurestore_entity_validation,
        featurestore_entity_workflow=featurestore_entity_workflow,
        featurestore_feature_value_approval=featurestore_feature_value_approval,
        featurestore_feature_value_import=featurestore_feature_value_import,
        featurestore_feature_value_query=featurestore_feature_value_query,
        featurestore_feature_value_reporting=featurestore_feature_value_reporting,
        featurestore_feature_value_workflow=featurestore_feature_value_workflow,
        featurestore_feature_view_approval=featurestore_feature_view_approval,
        featurestore_feature_view_calculation=featurestore_feature_view_calculation,
        featurestore_feature_view_query=featurestore_feature_view_query,
        featurestore_feature_view_sync=featurestore_feature_view_sync,
        featurestore_feature_view_validation=featurestore_feature_view_validation,
        featurestore_feature_view_workflow=featurestore_feature_view_workflow,
        fleet_vehicle=fleet_vehicle,
        forms_form_query=forms_form_query,
        fulfillment_fulfillment_query=fulfillment_fulfillment_query,
        helpdesk_ticket=helpdesk_ticket,
        identity_user_query=identity_user_query,
        identity_user=identity_user,
        identity_user_validation=identity_user_validation,
        itsm_incident=itsm_incident,
        keymanagement_crypto_key=keymanagement_crypto_key,
        labeling_annotation_approval=labeling_annotation_approval,
        labeling_annotation_validation=labeling_annotation_validation,
        labeling_label_set_approval=labeling_label_set_approval,
        labeling_label_set_calculation=labeling_label_set_calculation,
        labeling_label_set_sync=labeling_label_set_sync,
        labeling_label_set_validation=labeling_label_set_validation,
        labeling_labeling_task_query=labeling_labeling_task_query,
        labeling_labeling_task=labeling_labeling_task,
        labeling_labeling_task_workflow=labeling_labeling_task_workflow,
        ledger_ledger_account_query=ledger_ledger_account_query,
        ledger_ledger_account=ledger_ledger_account,
        ledger_ledger_account_validation=ledger_ledger_account_validation,
        lending_loan_application_query=lending_loan_application_query,
        lineage_impact_approval=lineage_impact_approval,
        lineage_impact_lifecycle=lineage_impact_lifecycle,
        lineage_impact_reporting=lineage_impact_reporting,
        lineage_impact_sync=lineage_impact_sync,
        lineage_impact_validation=lineage_impact_validation,
        lineage_lineage_edge_approval=lineage_lineage_edge_approval,
        lineage_lineage_edge_calculation=lineage_lineage_edge_calculation,
        lineage_lineage_edge_import=lineage_lineage_edge_import,
        lineage_lineage_edge_sync=lineage_lineage_edge_sync,
        lineage_lineage_node_approval=lineage_lineage_node_approval,
        lineage_lineage_node=lineage_lineage_node,
        maintenance_work_order_calculation=maintenance_work_order_calculation,
        metrics_dashboard_admin=metrics_dashboard_admin,
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
        modelregistry_deployment_approval=modelregistry_deployment_approval,
        modelregistry_deployment_import=modelregistry_deployment_import,
        modelregistry_deployment_sync=modelregistry_deployment_sync,
        modelregistry_deployment_validation=modelregistry_deployment_validation,
        modelregistry_model_version_lifecycle=modelregistry_model_version_lifecycle,
        modelregistry_model_version_reporting=modelregistry_model_version_reporting,
        modelregistry_model_version_validation=modelregistry_model_version_validation,
        modelregistry_registered_model_approval=modelregistry_registered_model_approval,
        modelregistry_registered_model_query=modelregistry_registered_model_query,
        modelregistry_registered_model_reporting=modelregistry_registered_model_reporting,
        modelregistry_registered_model_sync=modelregistry_registered_model_sync,
        modelregistry_registered_model_validation=modelregistry_registered_model_validation,
        modelregistry_registered_model_workflow=modelregistry_registered_model_workflow,
        notifications_notification=notifications_notification,
        patients_patient_calculation=patients_patient_calculation,
        pipelines_pipeline_approval=pipelines_pipeline_approval,
        pipelines_pipeline_calculation=pipelines_pipeline_calculation,
        pipelines_pipeline_lifecycle=pipelines_pipeline_lifecycle,
        pipelines_pipeline_query=pipelines_pipeline_query,
        pipelines_pipeline_reporting=pipelines_pipeline_reporting,
        pipelines_pipeline_run_calculation=pipelines_pipeline_run_calculation,
        pipelines_pipeline_run_import=pipelines_pipeline_run_import,
        pipelines_pipeline_run_lifecycle=pipelines_pipeline_run_lifecycle,
        pipelines_pipeline_run_query=pipelines_pipeline_run_query,
        pipelines_pipeline_run_reporting=pipelines_pipeline_run_reporting,
        pipelines_pipeline_run_sync=pipelines_pipeline_run_sync,
        pipelines_pipeline_run_validation=pipelines_pipeline_run_validation,
        pipelines_pipeline=pipelines_pipeline,
        pipelines_pipeline_step_approval=pipelines_pipeline_step_approval,
        pipelines_pipeline_step_calculation=pipelines_pipeline_step_calculation,
        pipelines_pipeline_step_export=pipelines_pipeline_step_export,
        pipelines_pipeline_step_import=pipelines_pipeline_step_import,
        pipelines_pipeline_step_lifecycle=pipelines_pipeline_step_lifecycle,
        pipelines_pipeline_step_reporting=pipelines_pipeline_step_reporting,
        pipelines_pipeline_step_sync=pipelines_pipeline_step_sync,
        pipelines_pipeline_step_validation=pipelines_pipeline_step_validation,
        pipelines_pipeline_sync=pipelines_pipeline_sync,
        pipelines_pipeline_validation=pipelines_pipeline_validation,
        prescriptions_prescription_query=prescriptions_prescription_query,
        pricing_price_list=pricing_price_list,
        promotions_promotion_query=promotions_promotion_query,
        ratelimiting_rate_limit_query=ratelimiting_rate_limit_query,
        recruiting_job_opening=recruiting_job_opening,
        routing_route=routing_route,
        search_search_index_query=search_search_index_query,
        search_search_index=search_search_index,
        search_search_index_validation=search_search_index_validation,
        seating_seat_map=seating_seat_map,
        telematics_telemetry_reading_query=telematics_telemetry_reading_query,
        ticketing_ticket_query=ticketing_ticket_query,
        timekeeping_timesheet=timekeeping_timesheet,
        treasury_cash_position_query=treasury_cash_position_query,
        venues_venue_query=venues_venue_query,
        venues_venue=venues_venue,
        venues_venue_validation=venues_venue_validation,
        yards_yard_calculation=yards_yard_calculation,
        yards_yard_query=yards_yard_query,
        registry={
            'acme.admissions.v1.AdmissionQueryService': admissions_admission_query,
            'acme.anomalies.v1.AnomalyApprovalService': anomalies_anomaly_approval,
            'acme.anomalies.v1.AnomalyFeedbackCalculationService': anomalies_anomaly_feedback_calculation,
            'acme.anomalies.v1.AnomalyQueryService': anomalies_anomaly_query,
            'acme.anomalies.v1.AnomalyWorkflowService': anomalies_anomaly_workflow,
            'acme.anomalies.v1.DetectorApprovalService': anomalies_detector_approval,
            'acme.anomalies.v1.DetectorQueryService': anomalies_detector_query,
            'acme.appointments.v1.AppointmentService': appointments_appointment,
            'acme.assets.v1.FixedAssetQueryService': assets_fixed_asset_query,
            'acme.audit.v1.AuditEventQueryService': audit_audit_event_query,
            'acme.audit.v1.AuditEventService': audit_audit_event,
            'acme.audit.v1.AuditEventValidationService': audit_audit_event_validation,
            'acme.authorization.v1.AccessPolicyQueryService': authorization_access_policy_query,
            'acme.authorization.v1.AccessPolicyService': authorization_access_policy,
            'acme.authorization.v1.AccessPolicyValidationService': authorization_access_policy_validation,
            'acme.broadcasts.v1.BroadcastService': broadcasts_broadcast,
            'acme.careplans.v1.CarePlanCalculationService': careplans_care_plan_calculation,
            'acme.careplans.v1.CarePlanQueryService': careplans_care_plan_query,
            'acme.careplans.v1.CarePlanService': careplans_care_plan,
            'acme.cart.v1.CartQueryService': cart_cart_query,
            'acme.chat.v1.ChatRoomService': chat_chat_room,
            'acme.community.v1.ForumQueryService': community_forum_query,
            'acme.compliance.v1.ComplianceCaseQueryService': compliance_compliance_case_query,
            'acme.concessions.v1.ConcessionStandService': concessions_concession_stand,
            'acme.dispatch.v1.DispatchOrderQueryService': dispatch_dispatch_order_query,
            'acme.documents.v1.DocumentQueryService': documents_document_query,
            'acme.documents.v1.DocumentService': documents_document,
            'acme.documents.v1.DocumentValidationService': documents_document_validation,
            'acme.drivers.v1.DriverCalculationService': drivers_driver_calculation,
            'acme.drivers.v1.DriverQueryService': drivers_driver_query,
            'acme.expenses.v1.ExpenseReportQueryService': expenses_expense_report_query,
            'acme.featureflags.v1.FeatureFlagValidationService': featureflags_feature_flag_validation,
            'acme.featurestore.v1.EntityApprovalService': featurestore_entity_approval,
            'acme.featurestore.v1.EntityImportService': featurestore_entity_import,
            'acme.featurestore.v1.EntityReportingService': featurestore_entity_reporting,
            'acme.featurestore.v1.EntitySyncService': featurestore_entity_sync,
            'acme.featurestore.v1.EntityValidationService': featurestore_entity_validation,
            'acme.featurestore.v1.EntityWorkflowService': featurestore_entity_workflow,
            'acme.featurestore.v1.FeatureValueApprovalService': featurestore_feature_value_approval,
            'acme.featurestore.v1.FeatureValueImportService': featurestore_feature_value_import,
            'acme.featurestore.v1.FeatureValueQueryService': featurestore_feature_value_query,
            'acme.featurestore.v1.FeatureValueReportingService': featurestore_feature_value_reporting,
            'acme.featurestore.v1.FeatureValueWorkflowService': featurestore_feature_value_workflow,
            'acme.featurestore.v1.FeatureViewApprovalService': featurestore_feature_view_approval,
            'acme.featurestore.v1.FeatureViewCalculationService': featurestore_feature_view_calculation,
            'acme.featurestore.v1.FeatureViewQueryService': featurestore_feature_view_query,
            'acme.featurestore.v1.FeatureViewSyncService': featurestore_feature_view_sync,
            'acme.featurestore.v1.FeatureViewValidationService': featurestore_feature_view_validation,
            'acme.featurestore.v1.FeatureViewWorkflowService': featurestore_feature_view_workflow,
            'acme.fleet.v1.VehicleService': fleet_vehicle,
            'acme.forms.v1.FormQueryService': forms_form_query,
            'acme.fulfillment.v1.FulfillmentQueryService': fulfillment_fulfillment_query,
            'acme.helpdesk.v1.TicketService': helpdesk_ticket,
            'acme.identity.v1.UserQueryService': identity_user_query,
            'acme.identity.v1.UserService': identity_user,
            'acme.identity.v1.UserValidationService': identity_user_validation,
            'acme.itsm.v1.IncidentService': itsm_incident,
            'acme.keymanagement.v1.CryptoKeyService': keymanagement_crypto_key,
            'acme.labeling.v1.AnnotationApprovalService': labeling_annotation_approval,
            'acme.labeling.v1.AnnotationValidationService': labeling_annotation_validation,
            'acme.labeling.v1.LabelSetApprovalService': labeling_label_set_approval,
            'acme.labeling.v1.LabelSetCalculationService': labeling_label_set_calculation,
            'acme.labeling.v1.LabelSetSyncService': labeling_label_set_sync,
            'acme.labeling.v1.LabelSetValidationService': labeling_label_set_validation,
            'acme.labeling.v1.LabelingTaskQueryService': labeling_labeling_task_query,
            'acme.labeling.v1.LabelingTaskService': labeling_labeling_task,
            'acme.labeling.v1.LabelingTaskWorkflowService': labeling_labeling_task_workflow,
            'acme.ledger.v1.LedgerAccountQueryService': ledger_ledger_account_query,
            'acme.ledger.v1.LedgerAccountService': ledger_ledger_account,
            'acme.ledger.v1.LedgerAccountValidationService': ledger_ledger_account_validation,
            'acme.lending.v1.LoanApplicationQueryService': lending_loan_application_query,
            'acme.lineage.v1.ImpactApprovalService': lineage_impact_approval,
            'acme.lineage.v1.ImpactLifecycleService': lineage_impact_lifecycle,
            'acme.lineage.v1.ImpactReportingService': lineage_impact_reporting,
            'acme.lineage.v1.ImpactSyncService': lineage_impact_sync,
            'acme.lineage.v1.ImpactValidationService': lineage_impact_validation,
            'acme.lineage.v1.LineageEdgeApprovalService': lineage_lineage_edge_approval,
            'acme.lineage.v1.LineageEdgeCalculationService': lineage_lineage_edge_calculation,
            'acme.lineage.v1.LineageEdgeImportService': lineage_lineage_edge_import,
            'acme.lineage.v1.LineageEdgeSyncService': lineage_lineage_edge_sync,
            'acme.lineage.v1.LineageNodeApprovalService': lineage_lineage_node_approval,
            'acme.lineage.v1.LineageNodeService': lineage_lineage_node,
            'acme.maintenance.v1.WorkOrderCalculationService': maintenance_work_order_calculation,
            'acme.metrics.v1.DashboardAdminService': metrics_dashboard_admin,
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
            'acme.modelregistry.v1.DeploymentApprovalService': modelregistry_deployment_approval,
            'acme.modelregistry.v1.DeploymentImportService': modelregistry_deployment_import,
            'acme.modelregistry.v1.DeploymentSyncService': modelregistry_deployment_sync,
            'acme.modelregistry.v1.DeploymentValidationService': modelregistry_deployment_validation,
            'acme.modelregistry.v1.ModelVersionLifecycleService': modelregistry_model_version_lifecycle,
            'acme.modelregistry.v1.ModelVersionReportingService': modelregistry_model_version_reporting,
            'acme.modelregistry.v1.ModelVersionValidationService': modelregistry_model_version_validation,
            'acme.modelregistry.v1.RegisteredModelApprovalService': modelregistry_registered_model_approval,
            'acme.modelregistry.v1.RegisteredModelQueryService': modelregistry_registered_model_query,
            'acme.modelregistry.v1.RegisteredModelReportingService': modelregistry_registered_model_reporting,
            'acme.modelregistry.v1.RegisteredModelSyncService': modelregistry_registered_model_sync,
            'acme.modelregistry.v1.RegisteredModelValidationService': modelregistry_registered_model_validation,
            'acme.modelregistry.v1.RegisteredModelWorkflowService': modelregistry_registered_model_workflow,
            'acme.notifications.v1.NotificationService': notifications_notification,
            'acme.patients.v1.PatientCalculationService': patients_patient_calculation,
            'acme.pipelines.v1.PipelineApprovalService': pipelines_pipeline_approval,
            'acme.pipelines.v1.PipelineCalculationService': pipelines_pipeline_calculation,
            'acme.pipelines.v1.PipelineLifecycleService': pipelines_pipeline_lifecycle,
            'acme.pipelines.v1.PipelineQueryService': pipelines_pipeline_query,
            'acme.pipelines.v1.PipelineReportingService': pipelines_pipeline_reporting,
            'acme.pipelines.v1.PipelineRunCalculationService': pipelines_pipeline_run_calculation,
            'acme.pipelines.v1.PipelineRunImportService': pipelines_pipeline_run_import,
            'acme.pipelines.v1.PipelineRunLifecycleService': pipelines_pipeline_run_lifecycle,
            'acme.pipelines.v1.PipelineRunQueryService': pipelines_pipeline_run_query,
            'acme.pipelines.v1.PipelineRunReportingService': pipelines_pipeline_run_reporting,
            'acme.pipelines.v1.PipelineRunSyncService': pipelines_pipeline_run_sync,
            'acme.pipelines.v1.PipelineRunValidationService': pipelines_pipeline_run_validation,
            'acme.pipelines.v1.PipelineService': pipelines_pipeline,
            'acme.pipelines.v1.PipelineStepApprovalService': pipelines_pipeline_step_approval,
            'acme.pipelines.v1.PipelineStepCalculationService': pipelines_pipeline_step_calculation,
            'acme.pipelines.v1.PipelineStepExportService': pipelines_pipeline_step_export,
            'acme.pipelines.v1.PipelineStepImportService': pipelines_pipeline_step_import,
            'acme.pipelines.v1.PipelineStepLifecycleService': pipelines_pipeline_step_lifecycle,
            'acme.pipelines.v1.PipelineStepReportingService': pipelines_pipeline_step_reporting,
            'acme.pipelines.v1.PipelineStepSyncService': pipelines_pipeline_step_sync,
            'acme.pipelines.v1.PipelineStepValidationService': pipelines_pipeline_step_validation,
            'acme.pipelines.v1.PipelineSyncService': pipelines_pipeline_sync,
            'acme.pipelines.v1.PipelineValidationService': pipelines_pipeline_validation,
            'acme.prescriptions.v1.PrescriptionQueryService': prescriptions_prescription_query,
            'acme.pricing.v1.PriceListService': pricing_price_list,
            'acme.promotions.v1.PromotionQueryService': promotions_promotion_query,
            'acme.ratelimiting.v1.RateLimitQueryService': ratelimiting_rate_limit_query,
            'acme.recruiting.v1.JobOpeningService': recruiting_job_opening,
            'acme.routing.v1.RouteService': routing_route,
            'acme.search.v1.SearchIndexQueryService': search_search_index_query,
            'acme.search.v1.SearchIndexService': search_search_index,
            'acme.search.v1.SearchIndexValidationService': search_search_index_validation,
            'acme.seating.v1.SeatMapService': seating_seat_map,
            'acme.telematics.v1.TelemetryReadingQueryService': telematics_telemetry_reading_query,
            'acme.ticketing.v1.TicketQueryService': ticketing_ticket_query,
            'acme.timekeeping.v1.TimesheetService': timekeeping_timesheet,
            'acme.treasury.v1.CashPositionQueryService': treasury_cash_position_query,
            'acme.venues.v1.VenueQueryService': venues_venue_query,
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
    pipeline_approval_servicer = Factory(lambda: PipelineApprovalServicer(deps))()
    pipelines_v1_pipeline_approval_service_pb2_grpc.add_PipelineApprovalServiceServicer_to_server(
        pipeline_approval_servicer,
        server
    )
    registered['acme.pipelines.v1.PipelineApprovalService'] = pipeline_approval_servicer
    pipeline_calculation_servicer = Factory(lambda: PipelineCalculationServicer(deps))()
    pipelines_v1_pipeline_calculation_service_pb2_grpc.add_PipelineCalculationServiceServicer_to_server(
        pipeline_calculation_servicer,
        server
    )
    registered['acme.pipelines.v1.PipelineCalculationService'] = pipeline_calculation_servicer
    pipeline_lifecycle_servicer = Factory(lambda: PipelineLifecycleServicer(deps))()
    pipelines_v1_pipeline_lifecycle_service_pb2_grpc.add_PipelineLifecycleServiceServicer_to_server(
        pipeline_lifecycle_servicer,
        server
    )
    registered['acme.pipelines.v1.PipelineLifecycleService'] = pipeline_lifecycle_servicer
    pipeline_query_servicer = Factory(lambda: PipelineQueryServicer(deps))()
    pipelines_v1_pipeline_query_service_pb2_grpc.add_PipelineQueryServiceServicer_to_server(
        pipeline_query_servicer,
        server
    )
    registered['acme.pipelines.v1.PipelineQueryService'] = pipeline_query_servicer
    pipeline_reporting_servicer = Factory(lambda: PipelineReportingServicer(deps))()
    pipelines_v1_pipeline_reporting_service_pb2_grpc.add_PipelineReportingServiceServicer_to_server(
        pipeline_reporting_servicer,
        server
    )
    registered['acme.pipelines.v1.PipelineReportingService'] = pipeline_reporting_servicer
    pipeline_run_approval_servicer = Factory(lambda: PipelineRunApprovalServicer(deps))()
    pipelines_v1_pipeline_run_approval_service_pb2_grpc.add_PipelineRunApprovalServiceServicer_to_server(
        pipeline_run_approval_servicer,
        server
    )
    registered['acme.pipelines.v1.PipelineRunApprovalService'] = pipeline_run_approval_servicer
    pipeline_run_calculation_servicer = Factory(lambda: PipelineRunCalculationServicer(deps))()
    pipelines_v1_pipeline_run_calculation_service_pb2_grpc.add_PipelineRunCalculationServiceServicer_to_server(
        pipeline_run_calculation_servicer,
        server
    )
    registered['acme.pipelines.v1.PipelineRunCalculationService'] = pipeline_run_calculation_servicer
    pipeline_run_import_servicer = Factory(lambda: PipelineRunImportServicer(deps))()
    pipelines_v1_pipeline_run_import_service_pb2_grpc.add_PipelineRunImportServiceServicer_to_server(
        pipeline_run_import_servicer,
        server
    )
    registered['acme.pipelines.v1.PipelineRunImportService'] = pipeline_run_import_servicer
    pipeline_run_lifecycle_servicer = Factory(lambda: PipelineRunLifecycleServicer(deps))()
    pipelines_v1_pipeline_run_lifecycle_service_pb2_grpc.add_PipelineRunLifecycleServiceServicer_to_server(
        pipeline_run_lifecycle_servicer,
        server
    )
    registered['acme.pipelines.v1.PipelineRunLifecycleService'] = pipeline_run_lifecycle_servicer
    pipeline_run_query_servicer = Factory(lambda: PipelineRunQueryServicer(deps))()
    pipelines_v1_pipeline_run_query_service_pb2_grpc.add_PipelineRunQueryServiceServicer_to_server(
        pipeline_run_query_servicer,
        server
    )
    registered['acme.pipelines.v1.PipelineRunQueryService'] = pipeline_run_query_servicer
    pipeline_run_reporting_servicer = Factory(lambda: PipelineRunReportingServicer(deps))()
    pipelines_v1_pipeline_run_reporting_service_pb2_grpc.add_PipelineRunReportingServiceServicer_to_server(
        pipeline_run_reporting_servicer,
        server
    )
    registered['acme.pipelines.v1.PipelineRunReportingService'] = pipeline_run_reporting_servicer
    pipeline_run_sync_servicer = Factory(lambda: PipelineRunSyncServicer(deps))()
    pipelines_v1_pipeline_run_sync_service_pb2_grpc.add_PipelineRunSyncServiceServicer_to_server(
        pipeline_run_sync_servicer,
        server
    )
    registered['acme.pipelines.v1.PipelineRunSyncService'] = pipeline_run_sync_servicer
    pipeline_run_validation_servicer = Factory(lambda: PipelineRunValidationServicer(deps))()
    pipelines_v1_pipeline_run_validation_service_pb2_grpc.add_PipelineRunValidationServiceServicer_to_server(
        pipeline_run_validation_servicer,
        server
    )
    registered['acme.pipelines.v1.PipelineRunValidationService'] = pipeline_run_validation_servicer
    pipeline_run_workflow_servicer = Factory(lambda: PipelineRunWorkflowServicer(deps))()
    pipelines_v1_pipeline_run_workflow_service_pb2_grpc.add_PipelineRunWorkflowServiceServicer_to_server(
        pipeline_run_workflow_servicer,
        server
    )
    registered['acme.pipelines.v1.PipelineRunWorkflowService'] = pipeline_run_workflow_servicer
    pipeline_servicer = Factory(lambda: PipelineServicer(deps))()
    pipelines_v1_pipeline_service_pb2_grpc.add_PipelineServiceServicer_to_server(pipeline_servicer, server)
    registered['acme.pipelines.v1.PipelineService'] = pipeline_servicer
    pipeline_step_approval_servicer = Factory(lambda: PipelineStepApprovalServicer(deps))()
    pipelines_v1_pipeline_step_approval_service_pb2_grpc.add_PipelineStepApprovalServiceServicer_to_server(
        pipeline_step_approval_servicer,
        server
    )
    registered['acme.pipelines.v1.PipelineStepApprovalService'] = pipeline_step_approval_servicer
    pipeline_step_calculation_servicer = Factory(lambda: PipelineStepCalculationServicer(deps))()
    pipelines_v1_pipeline_step_calculation_service_pb2_grpc.add_PipelineStepCalculationServiceServicer_to_server(
        pipeline_step_calculation_servicer,
        server
    )
    registered['acme.pipelines.v1.PipelineStepCalculationService'] = pipeline_step_calculation_servicer
    pipeline_step_export_servicer = Factory(lambda: PipelineStepExportServicer(deps))()
    pipelines_v1_pipeline_step_export_service_pb2_grpc.add_PipelineStepExportServiceServicer_to_server(
        pipeline_step_export_servicer,
        server
    )
    registered['acme.pipelines.v1.PipelineStepExportService'] = pipeline_step_export_servicer
    pipeline_step_import_servicer = Factory(lambda: PipelineStepImportServicer(deps))()
    pipelines_v1_pipeline_step_import_service_pb2_grpc.add_PipelineStepImportServiceServicer_to_server(
        pipeline_step_import_servicer,
        server
    )
    registered['acme.pipelines.v1.PipelineStepImportService'] = pipeline_step_import_servicer
    pipeline_step_lifecycle_servicer = Factory(lambda: PipelineStepLifecycleServicer(deps))()
    pipelines_v1_pipeline_step_lifecycle_service_pb2_grpc.add_PipelineStepLifecycleServiceServicer_to_server(
        pipeline_step_lifecycle_servicer,
        server
    )
    registered['acme.pipelines.v1.PipelineStepLifecycleService'] = pipeline_step_lifecycle_servicer
    pipeline_step_reporting_servicer = Factory(lambda: PipelineStepReportingServicer(deps))()
    pipelines_v1_pipeline_step_reporting_service_pb2_grpc.add_PipelineStepReportingServiceServicer_to_server(
        pipeline_step_reporting_servicer,
        server
    )
    registered['acme.pipelines.v1.PipelineStepReportingService'] = pipeline_step_reporting_servicer
    pipeline_step_sync_servicer = Factory(lambda: PipelineStepSyncServicer(deps))()
    pipelines_v1_pipeline_step_sync_service_pb2_grpc.add_PipelineStepSyncServiceServicer_to_server(
        pipeline_step_sync_servicer,
        server
    )
    registered['acme.pipelines.v1.PipelineStepSyncService'] = pipeline_step_sync_servicer
    pipeline_step_validation_servicer = Factory(lambda: PipelineStepValidationServicer(deps))()
    pipelines_v1_pipeline_step_validation_service_pb2_grpc.add_PipelineStepValidationServiceServicer_to_server(
        pipeline_step_validation_servicer,
        server
    )
    registered['acme.pipelines.v1.PipelineStepValidationService'] = pipeline_step_validation_servicer
    pipeline_step_workflow_servicer = Factory(lambda: PipelineStepWorkflowServicer(deps))()
    pipelines_v1_pipeline_step_workflow_service_pb2_grpc.add_PipelineStepWorkflowServiceServicer_to_server(
        pipeline_step_workflow_servicer,
        server
    )
    registered['acme.pipelines.v1.PipelineStepWorkflowService'] = pipeline_step_workflow_servicer
    pipeline_sync_servicer = Factory(lambda: PipelineSyncServicer(deps))()
    pipelines_v1_pipeline_sync_service_pb2_grpc.add_PipelineSyncServiceServicer_to_server(
        pipeline_sync_servicer,
        server
    )
    registered['acme.pipelines.v1.PipelineSyncService'] = pipeline_sync_servicer
    pipeline_validation_servicer = Factory(lambda: PipelineValidationServicer(deps))()
    pipelines_v1_pipeline_validation_service_pb2_grpc.add_PipelineValidationServiceServicer_to_server(
        pipeline_validation_servicer,
        server
    )
    registered['acme.pipelines.v1.PipelineValidationService'] = pipeline_validation_servicer
    pipeline_workflow_servicer = Factory(lambda: PipelineWorkflowServicer(deps))()
    pipelines_v1_pipeline_workflow_service_pb2_grpc.add_PipelineWorkflowServiceServicer_to_server(
        pipeline_workflow_servicer,
        server
    )
    registered['acme.pipelines.v1.PipelineWorkflowService'] = pipeline_workflow_servicer
    subscribe(deps)
    return registered
