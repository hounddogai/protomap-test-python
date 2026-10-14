"""Register and compose every service of the labeling domain."""

from __future__ import annotations

import grpc

from acme.admissions.v1 import (
    admission_calculation_service_pb2_grpc as admissions_v1_admission_calculation_service_pb2_grpc,
)
from acme.admissions.v1 import admission_service_pb2_grpc as admissions_v1_admission_service_pb2_grpc
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
from acme.anomalies.v1 import anomaly_validation_service_pb2_grpc as anomalies_v1_anomaly_validation_service_pb2_grpc
from acme.anomalies.v1 import anomaly_workflow_service_pb2_grpc as anomalies_v1_anomaly_workflow_service_pb2_grpc
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
from acme.billing.v1 import billing_account_service_pb2_grpc as billing_v1_billing_account_service_pb2_grpc
from acme.broadcasts.v1 import broadcast_query_service_pb2_grpc as broadcasts_v1_broadcast_query_service_pb2_grpc
from acme.careplans.v1 import (
    care_plan_calculation_service_pb2_grpc as careplans_v1_care_plan_calculation_service_pb2_grpc,
)
from acme.concessions.v1 import concession_stand_service_pb2_grpc as concessions_v1_concession_stand_service_pb2_grpc
from acme.configuration.v1 import (
    config_set_query_service_pb2_grpc as configuration_v1_config_set_query_service_pb2_grpc,
)
from acme.customers.v1 import (
    customer_calculation_service_pb2_grpc as customers_v1_customer_calculation_service_pb2_grpc,
)
from acme.customers.v1 import customer_service_pb2_grpc as customers_v1_customer_service_pb2_grpc
from acme.documents.v1 import document_query_service_pb2_grpc as documents_v1_document_query_service_pb2_grpc
from acme.documents.v1 import document_service_pb2_grpc as documents_v1_document_service_pb2_grpc
from acme.documents.v1 import document_validation_service_pb2_grpc as documents_v1_document_validation_service_pb2_grpc
from acme.experiments.v1 import experiment_query_service_pb2_grpc as experiments_v1_experiment_query_service_pb2_grpc
from acme.featureflags.v1 import (
    feature_flag_query_service_pb2_grpc as featureflags_v1_feature_flag_query_service_pb2_grpc,
)
from acme.featurestore.v1 import (
    feature_value_calculation_service_pb2_grpc as featurestore_v1_feature_value_calculation_service_pb2_grpc,
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
    feature_view_approval_service_pb2_grpc as featurestore_v1_feature_view_approval_service_pb2_grpc,
)
from acme.featurestore.v1 import (
    feature_view_calculation_service_pb2_grpc as featurestore_v1_feature_view_calculation_service_pb2_grpc,
)
from acme.featurestore.v1 import (
    feature_view_query_service_pb2_grpc as featurestore_v1_feature_view_query_service_pb2_grpc,
)
from acme.featurestore.v1 import (
    feature_view_reporting_service_pb2_grpc as featurestore_v1_feature_view_reporting_service_pb2_grpc,
)
from acme.featurestore.v1 import feature_view_service_pb2_grpc as featurestore_v1_feature_view_service_pb2_grpc
from acme.featurestore.v1 import (
    feature_view_validation_service_pb2_grpc as featurestore_v1_feature_view_validation_service_pb2_grpc,
)
from acme.identity.v1 import user_query_service_pb2_grpc as identity_v1_user_query_service_pb2_grpc
from acme.identity.v1 import user_service_pb2_grpc as identity_v1_user_service_pb2_grpc
from acme.identity.v1 import user_validation_service_pb2_grpc as identity_v1_user_validation_service_pb2_grpc
from acme.invoicing.v1 import invoice_batch_service_pb2_grpc as invoicing_v1_invoice_batch_service_pb2_grpc
from acme.keymanagement.v1 import (
    crypto_key_calculation_service_pb2_grpc as keymanagement_v1_crypto_key_calculation_service_pb2_grpc,
)
from acme.labeling.v1 import annotation_approval_service_pb2_grpc as labeling_v1_annotation_approval_service_pb2_grpc
from acme.labeling.v1 import (
    annotation_calculation_service_pb2_grpc as labeling_v1_annotation_calculation_service_pb2_grpc,
)
from acme.labeling.v1 import annotation_lifecycle_service_pb2_grpc as labeling_v1_annotation_lifecycle_service_pb2_grpc
from acme.labeling.v1 import annotation_query_service_pb2_grpc as labeling_v1_annotation_query_service_pb2_grpc
from acme.labeling.v1 import annotation_reporting_service_pb2_grpc as labeling_v1_annotation_reporting_service_pb2_grpc
from acme.labeling.v1 import (
    annotation_validation_service_pb2_grpc as labeling_v1_annotation_validation_service_pb2_grpc,
)
from acme.labeling.v1 import annotation_workflow_service_pb2_grpc as labeling_v1_annotation_workflow_service_pb2_grpc
from acme.labeling.v1 import label_set_approval_service_pb2_grpc as labeling_v1_label_set_approval_service_pb2_grpc
from acme.labeling.v1 import (
    label_set_calculation_service_pb2_grpc as labeling_v1_label_set_calculation_service_pb2_grpc,
)
from acme.labeling.v1 import label_set_lifecycle_service_pb2_grpc as labeling_v1_label_set_lifecycle_service_pb2_grpc
from acme.labeling.v1 import label_set_reporting_service_pb2_grpc as labeling_v1_label_set_reporting_service_pb2_grpc
from acme.labeling.v1 import label_set_sync_service_pb2_grpc as labeling_v1_label_set_sync_service_pb2_grpc
from acme.labeling.v1 import label_set_validation_service_pb2_grpc as labeling_v1_label_set_validation_service_pb2_grpc
from acme.labeling.v1 import label_set_workflow_service_pb2_grpc as labeling_v1_label_set_workflow_service_pb2_grpc
from acme.labeling.v1 import (
    labeling_task_approval_service_pb2_grpc as labeling_v1_labeling_task_approval_service_pb2_grpc,
)
from acme.labeling.v1 import (
    labeling_task_calculation_service_pb2_grpc as labeling_v1_labeling_task_calculation_service_pb2_grpc,
)
from acme.labeling.v1 import (
    labeling_task_lifecycle_service_pb2_grpc as labeling_v1_labeling_task_lifecycle_service_pb2_grpc,
)
from acme.labeling.v1 import labeling_task_query_service_pb2_grpc as labeling_v1_labeling_task_query_service_pb2_grpc
from acme.labeling.v1 import labeling_task_service_pb2_grpc as labeling_v1_labeling_task_service_pb2_grpc
from acme.labeling.v1 import (
    labeling_task_validation_service_pb2_grpc as labeling_v1_labeling_task_validation_service_pb2_grpc,
)
from acme.labeling.v1 import (
    labeling_task_workflow_service_pb2_grpc as labeling_v1_labeling_task_workflow_service_pb2_grpc,
)
from acme.ledger.v1 import ledger_account_query_service_pb2_grpc as ledger_v1_ledger_account_query_service_pb2_grpc
from acme.ledger.v1 import ledger_account_service_pb2_grpc as ledger_v1_ledger_account_service_pb2_grpc
from acme.ledger.v1 import (
    ledger_account_validation_service_pb2_grpc as ledger_v1_ledger_account_validation_service_pb2_grpc,
)
from acme.lineage.v1 import impact_approval_service_pb2_grpc as lineage_v1_impact_approval_service_pb2_grpc
from acme.lineage.v1 import impact_calculation_service_pb2_grpc as lineage_v1_impact_calculation_service_pb2_grpc
from acme.lineage.v1 import impact_reporting_service_pb2_grpc as lineage_v1_impact_reporting_service_pb2_grpc
from acme.lineage.v1 import impact_sync_service_pb2_grpc as lineage_v1_impact_sync_service_pb2_grpc
from acme.lineage.v1 import impact_validation_service_pb2_grpc as lineage_v1_impact_validation_service_pb2_grpc
from acme.lineage.v1 import impact_workflow_service_pb2_grpc as lineage_v1_impact_workflow_service_pb2_grpc
from acme.lineage.v1 import lineage_edge_approval_service_pb2_grpc as lineage_v1_lineage_edge_approval_service_pb2_grpc
from acme.lineage.v1 import (
    lineage_edge_calculation_service_pb2_grpc as lineage_v1_lineage_edge_calculation_service_pb2_grpc,
)
from acme.lineage.v1 import lineage_edge_query_service_pb2_grpc as lineage_v1_lineage_edge_query_service_pb2_grpc
from acme.lineage.v1 import lineage_edge_workflow_service_pb2_grpc as lineage_v1_lineage_edge_workflow_service_pb2_grpc
from acme.lineage.v1 import lineage_node_approval_service_pb2_grpc as lineage_v1_lineage_node_approval_service_pb2_grpc
from acme.lineage.v1 import (
    lineage_node_reporting_service_pb2_grpc as lineage_v1_lineage_node_reporting_service_pb2_grpc,
)
from acme.maintenance.v1 import (
    work_order_calculation_service_pb2_grpc as maintenance_v1_work_order_calculation_service_pb2_grpc,
)
from acme.messaging.v1 import conversation_query_service_pb2_grpc as messaging_v1_conversation_query_service_pb2_grpc
from acme.metrics.v1 import dashboard_export_service_pb2_grpc as metrics_v1_dashboard_export_service_pb2_grpc
from acme.metrics.v1 import dashboard_history_service_pb2_grpc as metrics_v1_dashboard_history_service_pb2_grpc
from acme.metrics.v1 import (
    dashboard_notification_service_pb2_grpc as metrics_v1_dashboard_notification_service_pb2_grpc,
)
from acme.metrics.v1 import dashboard_sync_service_pb2_grpc as metrics_v1_dashboard_sync_service_pb2_grpc
from acme.metrics.v1 import dashboard_validation_service_pb2_grpc as metrics_v1_dashboard_validation_service_pb2_grpc
from acme.metrics.v1 import metric_alert_admin_service_pb2_grpc as metrics_v1_metric_alert_admin_service_pb2_grpc
from acme.metrics.v1 import metric_alert_export_service_pb2_grpc as metrics_v1_metric_alert_export_service_pb2_grpc
from acme.metrics.v1 import metric_alert_history_service_pb2_grpc as metrics_v1_metric_alert_history_service_pb2_grpc
from acme.metrics.v1 import (
    metric_alert_notification_service_pb2_grpc as metrics_v1_metric_alert_notification_service_pb2_grpc,
)
from acme.metrics.v1 import (
    metric_alert_validation_service_pb2_grpc as metrics_v1_metric_alert_validation_service_pb2_grpc,
)
from acme.metrics.v1 import metric_series_export_service_pb2_grpc as metrics_v1_metric_series_export_service_pb2_grpc
from acme.metrics.v1 import metric_series_history_service_pb2_grpc as metrics_v1_metric_series_history_service_pb2_grpc
from acme.metrics.v1 import (
    metric_series_notification_service_pb2_grpc as metrics_v1_metric_series_notification_service_pb2_grpc,
)
from acme.metrics.v1 import metric_series_query_service_pb2_grpc as metrics_v1_metric_series_query_service_pb2_grpc
from acme.modelregistry.v1 import (
    deployment_calculation_service_pb2_grpc as modelregistry_v1_deployment_calculation_service_pb2_grpc,
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
    model_version_query_service_pb2_grpc as modelregistry_v1_model_version_query_service_pb2_grpc,
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
    registered_model_service_pb2_grpc as modelregistry_v1_registered_model_service_pb2_grpc,
)
from acme.modelregistry.v1 import (
    registered_model_sync_service_pb2_grpc as modelregistry_v1_registered_model_sync_service_pb2_grpc,
)
from acme.modelregistry.v1 import (
    registered_model_validation_service_pb2_grpc as modelregistry_v1_registered_model_validation_service_pb2_grpc,
)
from acme.notifications.v1 import (
    notification_query_service_pb2_grpc as notifications_v1_notification_query_service_pb2_grpc,
)
from acme.notifications.v1 import notification_service_pb2_grpc as notifications_v1_notification_service_pb2_grpc
from acme.notifications.v1 import (
    notification_validation_service_pb2_grpc as notifications_v1_notification_validation_service_pb2_grpc,
)
from acme.patients.v1 import patient_service_pb2_grpc as patients_v1_patient_service_pb2_grpc
from acme.performers.v1 import performer_query_service_pb2_grpc as performers_v1_performer_query_service_pb2_grpc
from acme.prescriptions.v1 import (
    prescription_query_service_pb2_grpc as prescriptions_v1_prescription_query_service_pb2_grpc,
)
from acme.pricing.v1 import price_list_query_service_pb2_grpc as pricing_v1_price_list_query_service_pb2_grpc
from acme.ratelimiting.v1 import rate_limit_service_pb2_grpc as ratelimiting_v1_rate_limit_service_pb2_grpc
from acme.scheduling.v1 import shift_service_pb2_grpc as scheduling_v1_shift_service_pb2_grpc
from acme.search.v1 import search_index_query_service_pb2_grpc as search_v1_search_index_query_service_pb2_grpc
from acme.search.v1 import search_index_service_pb2_grpc as search_v1_search_index_service_pb2_grpc
from acme.search.v1 import (
    search_index_validation_service_pb2_grpc as search_v1_search_index_validation_service_pb2_grpc,
)
from acme.secrets.v1 import secret_service_pb2_grpc as secrets_v1_secret_service_pb2_grpc
from acme.sponsorships.v1 import sponsor_query_service_pb2_grpc as sponsorships_v1_sponsor_query_service_pb2_grpc
from acme.sponsorships.v1 import sponsor_service_pb2_grpc as sponsorships_v1_sponsor_service_pb2_grpc
from acme.telehealth.v1 import video_visit_service_pb2_grpc as telehealth_v1_video_visit_service_pb2_grpc
from acme.ticketing.v1 import ticket_service_pb2_grpc as ticketing_v1_ticket_service_pb2_grpc
from acme.timekeeping.v1 import timesheet_service_pb2_grpc as timekeeping_v1_timesheet_service_pb2_grpc
from acme.tours.v1 import tour_query_service_pb2_grpc as tours_v1_tour_query_service_pb2_grpc
from acme.venues.v1 import venue_validation_service_pb2_grpc as venues_v1_venue_validation_service_pb2_grpc
from acme.yards.v1 import yard_calculation_service_pb2_grpc as yards_v1_yard_calculation_service_pb2_grpc
from acme.yards.v1 import yard_service_pb2_grpc as yards_v1_yard_service_pb2_grpc

from acme_data.domains.labeling.annotation_approval_service import AnnotationApprovalServicer
from acme_data.domains.labeling.annotation_calculation_service import AnnotationCalculationServicer
from acme_data.domains.labeling.annotation_lifecycle_service import AnnotationLifecycleServicer
from acme_data.domains.labeling.annotation_query_service import AnnotationQueryServicer
from acme_data.domains.labeling.annotation_reporting_service import AnnotationReportingServicer
from acme_data.domains.labeling.annotation_validation_service import AnnotationValidationServicer
from acme_data.domains.labeling.annotation_workflow_service import AnnotationWorkflowServicer
from acme_data.domains.labeling.dependencies import Clients
from acme_data.domains.labeling.dependencies import Dependencies
from acme_data.domains.labeling.events import subscribe
from acme_data.domains.labeling.label_set_approval_service import LabelSetApprovalServicer
from acme_data.domains.labeling.label_set_calculation_service import LabelSetCalculationServicer
from acme_data.domains.labeling.label_set_lifecycle_service import LabelSetLifecycleServicer
from acme_data.domains.labeling.label_set_reporting_service import LabelSetReportingServicer
from acme_data.domains.labeling.label_set_sync_service import LabelSetSyncServicer
from acme_data.domains.labeling.label_set_validation_service import LabelSetValidationServicer
from acme_data.domains.labeling.label_set_workflow_service import LabelSetWorkflowServicer
from acme_data.domains.labeling.labeling_task_approval_service import LabelingTaskApprovalServicer
from acme_data.domains.labeling.labeling_task_calculation_service import LabelingTaskCalculationServicer
from acme_data.domains.labeling.labeling_task_lifecycle_service import LabelingTaskLifecycleServicer
from acme_data.domains.labeling.labeling_task_query_service import LabelingTaskQueryServicer
from acme_data.domains.labeling.labeling_task_service import LabelingTaskServicer
from acme_data.domains.labeling.labeling_task_validation_service import LabelingTaskValidationServicer
from acme_data.domains.labeling.labeling_task_workflow_service import LabelingTaskWorkflowServicer
from acme_data.domains.labeling.repository import DomainRepository
from acme_data.platform.container import Container
from acme_data.platform.container import Factory


def dependencies(container: Container) -> Dependencies:
    admissions_admission_calculation = container.singleton(
        admissions_v1_admission_calculation_service_pb2_grpc.AdmissionCalculationServiceStub,
        lambda: admissions_v1_admission_calculation_service_pb2_grpc.AdmissionCalculationServiceStub(container.channel)
    )
    admissions_admission = container.singleton(
        admissions_v1_admission_service_pb2_grpc.AdmissionServiceStub,
        lambda: admissions_v1_admission_service_pb2_grpc.AdmissionServiceStub(container.channel)
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
    anomalies_anomaly_feedback_validation = container.singleton(
        anomalies_v1_anomaly_feedback_validation_service_pb2_grpc.AnomalyFeedbackValidationServiceStub,
        lambda: anomalies_v1_anomaly_feedback_validation_service_pb2_grpc.AnomalyFeedbackValidationServiceStub(
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
    billing_billing_account = container.singleton(
        billing_v1_billing_account_service_pb2_grpc.BillingAccountServiceStub,
        lambda: billing_v1_billing_account_service_pb2_grpc.BillingAccountServiceStub(container.channel)
    )
    broadcasts_broadcast_query = container.singleton(
        broadcasts_v1_broadcast_query_service_pb2_grpc.BroadcastQueryServiceStub,
        lambda: broadcasts_v1_broadcast_query_service_pb2_grpc.BroadcastQueryServiceStub(container.channel)
    )
    careplans_care_plan_calculation = container.singleton(
        careplans_v1_care_plan_calculation_service_pb2_grpc.CarePlanCalculationServiceStub,
        lambda: careplans_v1_care_plan_calculation_service_pb2_grpc.CarePlanCalculationServiceStub(container.channel)
    )
    concessions_concession_stand = container.singleton(
        concessions_v1_concession_stand_service_pb2_grpc.ConcessionStandServiceStub,
        lambda: concessions_v1_concession_stand_service_pb2_grpc.ConcessionStandServiceStub(container.channel)
    )
    configuration_config_set_query = container.singleton(
        configuration_v1_config_set_query_service_pb2_grpc.ConfigSetQueryServiceStub,
        lambda: configuration_v1_config_set_query_service_pb2_grpc.ConfigSetQueryServiceStub(container.channel)
    )
    customers_customer_calculation = container.singleton(
        customers_v1_customer_calculation_service_pb2_grpc.CustomerCalculationServiceStub,
        lambda: customers_v1_customer_calculation_service_pb2_grpc.CustomerCalculationServiceStub(container.channel)
    )
    customers_customer = container.singleton(
        customers_v1_customer_service_pb2_grpc.CustomerServiceStub,
        lambda: customers_v1_customer_service_pb2_grpc.CustomerServiceStub(container.channel)
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
    experiments_experiment_query = container.singleton(
        experiments_v1_experiment_query_service_pb2_grpc.ExperimentQueryServiceStub,
        lambda: experiments_v1_experiment_query_service_pb2_grpc.ExperimentQueryServiceStub(container.channel)
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
    featurestore_feature_view_validation = container.singleton(
        featurestore_v1_feature_view_validation_service_pb2_grpc.FeatureViewValidationServiceStub,
        lambda: featurestore_v1_feature_view_validation_service_pb2_grpc.FeatureViewValidationServiceStub(
            container.channel
        )
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
    invoicing_invoice_batch = container.singleton(
        invoicing_v1_invoice_batch_service_pb2_grpc.InvoiceBatchServiceStub,
        lambda: invoicing_v1_invoice_batch_service_pb2_grpc.InvoiceBatchServiceStub(container.channel)
    )
    keymanagement_crypto_key_calculation = container.singleton(
        keymanagement_v1_crypto_key_calculation_service_pb2_grpc.CryptoKeyCalculationServiceStub,
        lambda: keymanagement_v1_crypto_key_calculation_service_pb2_grpc.CryptoKeyCalculationServiceStub(
            container.channel
        )
    )
    labeling_annotation_approval = container.singleton(
        labeling_v1_annotation_approval_service_pb2_grpc.AnnotationApprovalServiceStub,
        lambda: labeling_v1_annotation_approval_service_pb2_grpc.AnnotationApprovalServiceStub(container.channel)
    )
    labeling_annotation_calculation = container.singleton(
        labeling_v1_annotation_calculation_service_pb2_grpc.AnnotationCalculationServiceStub,
        lambda: labeling_v1_annotation_calculation_service_pb2_grpc.AnnotationCalculationServiceStub(container.channel)
    )
    labeling_annotation_lifecycle = container.singleton(
        labeling_v1_annotation_lifecycle_service_pb2_grpc.AnnotationLifecycleServiceStub,
        lambda: labeling_v1_annotation_lifecycle_service_pb2_grpc.AnnotationLifecycleServiceStub(container.channel)
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
    labeling_annotation_workflow = container.singleton(
        labeling_v1_annotation_workflow_service_pb2_grpc.AnnotationWorkflowServiceStub,
        lambda: labeling_v1_annotation_workflow_service_pb2_grpc.AnnotationWorkflowServiceStub(container.channel)
    )
    labeling_label_set_approval = container.singleton(
        labeling_v1_label_set_approval_service_pb2_grpc.LabelSetApprovalServiceStub,
        lambda: labeling_v1_label_set_approval_service_pb2_grpc.LabelSetApprovalServiceStub(container.channel)
    )
    labeling_label_set_calculation = container.singleton(
        labeling_v1_label_set_calculation_service_pb2_grpc.LabelSetCalculationServiceStub,
        lambda: labeling_v1_label_set_calculation_service_pb2_grpc.LabelSetCalculationServiceStub(container.channel)
    )
    labeling_label_set_lifecycle = container.singleton(
        labeling_v1_label_set_lifecycle_service_pb2_grpc.LabelSetLifecycleServiceStub,
        lambda: labeling_v1_label_set_lifecycle_service_pb2_grpc.LabelSetLifecycleServiceStub(container.channel)
    )
    labeling_label_set_reporting = container.singleton(
        labeling_v1_label_set_reporting_service_pb2_grpc.LabelSetReportingServiceStub,
        lambda: labeling_v1_label_set_reporting_service_pb2_grpc.LabelSetReportingServiceStub(container.channel)
    )
    labeling_label_set_sync = container.singleton(
        labeling_v1_label_set_sync_service_pb2_grpc.LabelSetSyncServiceStub,
        lambda: labeling_v1_label_set_sync_service_pb2_grpc.LabelSetSyncServiceStub(container.channel)
    )
    labeling_label_set_validation = container.singleton(
        labeling_v1_label_set_validation_service_pb2_grpc.LabelSetValidationServiceStub,
        lambda: labeling_v1_label_set_validation_service_pb2_grpc.LabelSetValidationServiceStub(container.channel)
    )
    labeling_labeling_task_approval = container.singleton(
        labeling_v1_labeling_task_approval_service_pb2_grpc.LabelingTaskApprovalServiceStub,
        lambda: labeling_v1_labeling_task_approval_service_pb2_grpc.LabelingTaskApprovalServiceStub(container.channel)
    )
    labeling_labeling_task_calculation = container.singleton(
        labeling_v1_labeling_task_calculation_service_pb2_grpc.LabelingTaskCalculationServiceStub,
        lambda: labeling_v1_labeling_task_calculation_service_pb2_grpc.LabelingTaskCalculationServiceStub(
            container.channel
        )
    )
    labeling_labeling_task_lifecycle = container.singleton(
        labeling_v1_labeling_task_lifecycle_service_pb2_grpc.LabelingTaskLifecycleServiceStub,
        lambda: labeling_v1_labeling_task_lifecycle_service_pb2_grpc.LabelingTaskLifecycleServiceStub(container.channel)
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
    lineage_impact_approval = container.singleton(
        lineage_v1_impact_approval_service_pb2_grpc.ImpactApprovalServiceStub,
        lambda: lineage_v1_impact_approval_service_pb2_grpc.ImpactApprovalServiceStub(container.channel)
    )
    lineage_impact_calculation = container.singleton(
        lineage_v1_impact_calculation_service_pb2_grpc.ImpactCalculationServiceStub,
        lambda: lineage_v1_impact_calculation_service_pb2_grpc.ImpactCalculationServiceStub(container.channel)
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
    lineage_lineage_edge_query = container.singleton(
        lineage_v1_lineage_edge_query_service_pb2_grpc.LineageEdgeQueryServiceStub,
        lambda: lineage_v1_lineage_edge_query_service_pb2_grpc.LineageEdgeQueryServiceStub(container.channel)
    )
    lineage_lineage_edge_workflow = container.singleton(
        lineage_v1_lineage_edge_workflow_service_pb2_grpc.LineageEdgeWorkflowServiceStub,
        lambda: lineage_v1_lineage_edge_workflow_service_pb2_grpc.LineageEdgeWorkflowServiceStub(container.channel)
    )
    lineage_lineage_node_approval = container.singleton(
        lineage_v1_lineage_node_approval_service_pb2_grpc.LineageNodeApprovalServiceStub,
        lambda: lineage_v1_lineage_node_approval_service_pb2_grpc.LineageNodeApprovalServiceStub(container.channel)
    )
    lineage_lineage_node_reporting = container.singleton(
        lineage_v1_lineage_node_reporting_service_pb2_grpc.LineageNodeReportingServiceStub,
        lambda: lineage_v1_lineage_node_reporting_service_pb2_grpc.LineageNodeReportingServiceStub(container.channel)
    )
    maintenance_work_order_calculation = container.singleton(
        maintenance_v1_work_order_calculation_service_pb2_grpc.WorkOrderCalculationServiceStub,
        lambda: maintenance_v1_work_order_calculation_service_pb2_grpc.WorkOrderCalculationServiceStub(
            container.channel
        )
    )
    messaging_conversation_query = container.singleton(
        messaging_v1_conversation_query_service_pb2_grpc.ConversationQueryServiceStub,
        lambda: messaging_v1_conversation_query_service_pb2_grpc.ConversationQueryServiceStub(container.channel)
    )
    metrics_dashboard_export = container.singleton(
        metrics_v1_dashboard_export_service_pb2_grpc.DashboardExportServiceStub,
        lambda: metrics_v1_dashboard_export_service_pb2_grpc.DashboardExportServiceStub(container.channel)
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
    metrics_metric_alert_admin = container.singleton(
        metrics_v1_metric_alert_admin_service_pb2_grpc.MetricAlertAdminServiceStub,
        lambda: metrics_v1_metric_alert_admin_service_pb2_grpc.MetricAlertAdminServiceStub(container.channel)
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
    modelregistry_deployment_calculation = container.singleton(
        modelregistry_v1_deployment_calculation_service_pb2_grpc.DeploymentCalculationServiceStub,
        lambda: modelregistry_v1_deployment_calculation_service_pb2_grpc.DeploymentCalculationServiceStub(
            container.channel
        )
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
    modelregistry_deployment_workflow = container.singleton(
        modelregistry_v1_deployment_workflow_service_pb2_grpc.DeploymentWorkflowServiceStub,
        lambda: modelregistry_v1_deployment_workflow_service_pb2_grpc.DeploymentWorkflowServiceStub(container.channel)
    )
    modelregistry_model_version_query = container.singleton(
        modelregistry_v1_model_version_query_service_pb2_grpc.ModelVersionQueryServiceStub,
        lambda: modelregistry_v1_model_version_query_service_pb2_grpc.ModelVersionQueryServiceStub(container.channel)
    )
    modelregistry_model_version_workflow = container.singleton(
        modelregistry_v1_model_version_workflow_service_pb2_grpc.ModelVersionWorkflowServiceStub,
        lambda: modelregistry_v1_model_version_workflow_service_pb2_grpc.ModelVersionWorkflowServiceStub(
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
    notifications_notification_validation = container.singleton(
        notifications_v1_notification_validation_service_pb2_grpc.NotificationValidationServiceStub,
        lambda: notifications_v1_notification_validation_service_pb2_grpc.NotificationValidationServiceStub(
            container.channel
        )
    )
    patients_patient = container.singleton(
        patients_v1_patient_service_pb2_grpc.PatientServiceStub,
        lambda: patients_v1_patient_service_pb2_grpc.PatientServiceStub(container.channel)
    )
    performers_performer_query = container.singleton(
        performers_v1_performer_query_service_pb2_grpc.PerformerQueryServiceStub,
        lambda: performers_v1_performer_query_service_pb2_grpc.PerformerQueryServiceStub(container.channel)
    )
    prescriptions_prescription_query = container.singleton(
        prescriptions_v1_prescription_query_service_pb2_grpc.PrescriptionQueryServiceStub,
        lambda: prescriptions_v1_prescription_query_service_pb2_grpc.PrescriptionQueryServiceStub(container.channel)
    )
    pricing_price_list_query = container.singleton(
        pricing_v1_price_list_query_service_pb2_grpc.PriceListQueryServiceStub,
        lambda: pricing_v1_price_list_query_service_pb2_grpc.PriceListQueryServiceStub(container.channel)
    )
    ratelimiting_rate_limit = container.singleton(
        ratelimiting_v1_rate_limit_service_pb2_grpc.RateLimitServiceStub,
        lambda: ratelimiting_v1_rate_limit_service_pb2_grpc.RateLimitServiceStub(container.channel)
    )
    scheduling_shift = container.singleton(
        scheduling_v1_shift_service_pb2_grpc.ShiftServiceStub,
        lambda: scheduling_v1_shift_service_pb2_grpc.ShiftServiceStub(container.channel)
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
    secrets_secret = container.singleton(
        secrets_v1_secret_service_pb2_grpc.SecretServiceStub,
        lambda: secrets_v1_secret_service_pb2_grpc.SecretServiceStub(container.channel)
    )
    sponsorships_sponsor_query = container.singleton(
        sponsorships_v1_sponsor_query_service_pb2_grpc.SponsorQueryServiceStub,
        lambda: sponsorships_v1_sponsor_query_service_pb2_grpc.SponsorQueryServiceStub(container.channel)
    )
    sponsorships_sponsor = container.singleton(
        sponsorships_v1_sponsor_service_pb2_grpc.SponsorServiceStub,
        lambda: sponsorships_v1_sponsor_service_pb2_grpc.SponsorServiceStub(container.channel)
    )
    telehealth_video_visit = container.singleton(
        telehealth_v1_video_visit_service_pb2_grpc.VideoVisitServiceStub,
        lambda: telehealth_v1_video_visit_service_pb2_grpc.VideoVisitServiceStub(container.channel)
    )
    ticketing_ticket = container.singleton(
        ticketing_v1_ticket_service_pb2_grpc.TicketServiceStub,
        lambda: ticketing_v1_ticket_service_pb2_grpc.TicketServiceStub(container.channel)
    )
    timekeeping_timesheet = container.singleton(
        timekeeping_v1_timesheet_service_pb2_grpc.TimesheetServiceStub,
        lambda: timekeeping_v1_timesheet_service_pb2_grpc.TimesheetServiceStub(container.channel)
    )
    tours_tour_query = container.singleton(
        tours_v1_tour_query_service_pb2_grpc.TourQueryServiceStub,
        lambda: tours_v1_tour_query_service_pb2_grpc.TourQueryServiceStub(container.channel)
    )
    venues_venue_validation = container.singleton(
        venues_v1_venue_validation_service_pb2_grpc.VenueValidationServiceStub,
        lambda: venues_v1_venue_validation_service_pb2_grpc.VenueValidationServiceStub(container.channel)
    )
    yards_yard_calculation = container.singleton(
        yards_v1_yard_calculation_service_pb2_grpc.YardCalculationServiceStub,
        lambda: yards_v1_yard_calculation_service_pb2_grpc.YardCalculationServiceStub(container.channel)
    )
    yards_yard = container.singleton(
        yards_v1_yard_service_pb2_grpc.YardServiceStub,
        lambda: yards_v1_yard_service_pb2_grpc.YardServiceStub(container.channel)
    )
    clients = Clients(
        admissions_admission_calculation=admissions_admission_calculation,
        admissions_admission=admissions_admission,
        anomalies_anomaly_approval=anomalies_anomaly_approval,
        anomalies_anomaly_feedback_approval=anomalies_anomaly_feedback_approval,
        anomalies_anomaly_feedback_calculation=anomalies_anomaly_feedback_calculation,
        anomalies_anomaly_feedback_validation=anomalies_anomaly_feedback_validation,
        anomalies_anomaly_validation=anomalies_anomaly_validation,
        anomalies_anomaly_workflow=anomalies_anomaly_workflow,
        anomalies_detector_validation=anomalies_detector_validation,
        anomalies_detector_workflow=anomalies_detector_workflow,
        audit_audit_event_query=audit_audit_event_query,
        audit_audit_event=audit_audit_event,
        audit_audit_event_validation=audit_audit_event_validation,
        authorization_access_policy_query=authorization_access_policy_query,
        authorization_access_policy=authorization_access_policy,
        authorization_access_policy_validation=authorization_access_policy_validation,
        billing_billing_account=billing_billing_account,
        broadcasts_broadcast_query=broadcasts_broadcast_query,
        careplans_care_plan_calculation=careplans_care_plan_calculation,
        concessions_concession_stand=concessions_concession_stand,
        configuration_config_set_query=configuration_config_set_query,
        customers_customer_calculation=customers_customer_calculation,
        customers_customer=customers_customer,
        documents_document_query=documents_document_query,
        documents_document=documents_document,
        documents_document_validation=documents_document_validation,
        experiments_experiment_query=experiments_experiment_query,
        featureflags_feature_flag_query=featureflags_feature_flag_query,
        featurestore_feature_value_calculation=featurestore_feature_value_calculation,
        featurestore_feature_value_query=featurestore_feature_value_query,
        featurestore_feature_value_reporting=featurestore_feature_value_reporting,
        featurestore_feature_value_sync=featurestore_feature_value_sync,
        featurestore_feature_value_validation=featurestore_feature_value_validation,
        featurestore_feature_view_approval=featurestore_feature_view_approval,
        featurestore_feature_view_calculation=featurestore_feature_view_calculation,
        featurestore_feature_view_query=featurestore_feature_view_query,
        featurestore_feature_view_reporting=featurestore_feature_view_reporting,
        featurestore_feature_view=featurestore_feature_view,
        featurestore_feature_view_validation=featurestore_feature_view_validation,
        identity_user_query=identity_user_query,
        identity_user=identity_user,
        identity_user_validation=identity_user_validation,
        invoicing_invoice_batch=invoicing_invoice_batch,
        keymanagement_crypto_key_calculation=keymanagement_crypto_key_calculation,
        labeling_annotation_approval=labeling_annotation_approval,
        labeling_annotation_calculation=labeling_annotation_calculation,
        labeling_annotation_lifecycle=labeling_annotation_lifecycle,
        labeling_annotation_query=labeling_annotation_query,
        labeling_annotation_reporting=labeling_annotation_reporting,
        labeling_annotation_validation=labeling_annotation_validation,
        labeling_annotation_workflow=labeling_annotation_workflow,
        labeling_label_set_approval=labeling_label_set_approval,
        labeling_label_set_calculation=labeling_label_set_calculation,
        labeling_label_set_lifecycle=labeling_label_set_lifecycle,
        labeling_label_set_reporting=labeling_label_set_reporting,
        labeling_label_set_sync=labeling_label_set_sync,
        labeling_label_set_validation=labeling_label_set_validation,
        labeling_labeling_task_approval=labeling_labeling_task_approval,
        labeling_labeling_task_calculation=labeling_labeling_task_calculation,
        labeling_labeling_task_lifecycle=labeling_labeling_task_lifecycle,
        labeling_labeling_task_query=labeling_labeling_task_query,
        labeling_labeling_task=labeling_labeling_task,
        labeling_labeling_task_validation=labeling_labeling_task_validation,
        labeling_labeling_task_workflow=labeling_labeling_task_workflow,
        ledger_ledger_account_query=ledger_ledger_account_query,
        ledger_ledger_account=ledger_ledger_account,
        ledger_ledger_account_validation=ledger_ledger_account_validation,
        lineage_impact_approval=lineage_impact_approval,
        lineage_impact_calculation=lineage_impact_calculation,
        lineage_impact_reporting=lineage_impact_reporting,
        lineage_impact_sync=lineage_impact_sync,
        lineage_impact_validation=lineage_impact_validation,
        lineage_impact_workflow=lineage_impact_workflow,
        lineage_lineage_edge_approval=lineage_lineage_edge_approval,
        lineage_lineage_edge_calculation=lineage_lineage_edge_calculation,
        lineage_lineage_edge_query=lineage_lineage_edge_query,
        lineage_lineage_edge_workflow=lineage_lineage_edge_workflow,
        lineage_lineage_node_approval=lineage_lineage_node_approval,
        lineage_lineage_node_reporting=lineage_lineage_node_reporting,
        maintenance_work_order_calculation=maintenance_work_order_calculation,
        messaging_conversation_query=messaging_conversation_query,
        metrics_dashboard_export=metrics_dashboard_export,
        metrics_dashboard_history=metrics_dashboard_history,
        metrics_dashboard_notification=metrics_dashboard_notification,
        metrics_dashboard_sync=metrics_dashboard_sync,
        metrics_dashboard_validation=metrics_dashboard_validation,
        metrics_metric_alert_admin=metrics_metric_alert_admin,
        metrics_metric_alert_export=metrics_metric_alert_export,
        metrics_metric_alert_history=metrics_metric_alert_history,
        metrics_metric_alert_notification=metrics_metric_alert_notification,
        metrics_metric_alert_validation=metrics_metric_alert_validation,
        metrics_metric_series_export=metrics_metric_series_export,
        metrics_metric_series_history=metrics_metric_series_history,
        metrics_metric_series_notification=metrics_metric_series_notification,
        metrics_metric_series_query=metrics_metric_series_query,
        modelregistry_deployment_calculation=modelregistry_deployment_calculation,
        modelregistry_deployment_reporting=modelregistry_deployment_reporting,
        modelregistry_deployment_sync=modelregistry_deployment_sync,
        modelregistry_deployment_validation=modelregistry_deployment_validation,
        modelregistry_deployment_workflow=modelregistry_deployment_workflow,
        modelregistry_model_version_query=modelregistry_model_version_query,
        modelregistry_model_version_workflow=modelregistry_model_version_workflow,
        modelregistry_registered_model_approval=modelregistry_registered_model_approval,
        modelregistry_registered_model_calculation=modelregistry_registered_model_calculation,
        modelregistry_registered_model=modelregistry_registered_model,
        modelregistry_registered_model_sync=modelregistry_registered_model_sync,
        modelregistry_registered_model_validation=modelregistry_registered_model_validation,
        notifications_notification_query=notifications_notification_query,
        notifications_notification=notifications_notification,
        notifications_notification_validation=notifications_notification_validation,
        patients_patient=patients_patient,
        performers_performer_query=performers_performer_query,
        prescriptions_prescription_query=prescriptions_prescription_query,
        pricing_price_list_query=pricing_price_list_query,
        ratelimiting_rate_limit=ratelimiting_rate_limit,
        scheduling_shift=scheduling_shift,
        search_search_index_query=search_search_index_query,
        search_search_index=search_search_index,
        search_search_index_validation=search_search_index_validation,
        secrets_secret=secrets_secret,
        sponsorships_sponsor_query=sponsorships_sponsor_query,
        sponsorships_sponsor=sponsorships_sponsor,
        telehealth_video_visit=telehealth_video_visit,
        ticketing_ticket=ticketing_ticket,
        timekeeping_timesheet=timekeeping_timesheet,
        tours_tour_query=tours_tour_query,
        venues_venue_validation=venues_venue_validation,
        yards_yard_calculation=yards_yard_calculation,
        yards_yard=yards_yard,
        registry={
            'acme.admissions.v1.AdmissionCalculationService': admissions_admission_calculation,
            'acme.admissions.v1.AdmissionService': admissions_admission,
            'acme.anomalies.v1.AnomalyApprovalService': anomalies_anomaly_approval,
            'acme.anomalies.v1.AnomalyFeedbackApprovalService': anomalies_anomaly_feedback_approval,
            'acme.anomalies.v1.AnomalyFeedbackCalculationService': anomalies_anomaly_feedback_calculation,
            'acme.anomalies.v1.AnomalyFeedbackValidationService': anomalies_anomaly_feedback_validation,
            'acme.anomalies.v1.AnomalyValidationService': anomalies_anomaly_validation,
            'acme.anomalies.v1.AnomalyWorkflowService': anomalies_anomaly_workflow,
            'acme.anomalies.v1.DetectorValidationService': anomalies_detector_validation,
            'acme.anomalies.v1.DetectorWorkflowService': anomalies_detector_workflow,
            'acme.audit.v1.AuditEventQueryService': audit_audit_event_query,
            'acme.audit.v1.AuditEventService': audit_audit_event,
            'acme.audit.v1.AuditEventValidationService': audit_audit_event_validation,
            'acme.authorization.v1.AccessPolicyQueryService': authorization_access_policy_query,
            'acme.authorization.v1.AccessPolicyService': authorization_access_policy,
            'acme.authorization.v1.AccessPolicyValidationService': authorization_access_policy_validation,
            'acme.billing.v1.BillingAccountService': billing_billing_account,
            'acme.broadcasts.v1.BroadcastQueryService': broadcasts_broadcast_query,
            'acme.careplans.v1.CarePlanCalculationService': careplans_care_plan_calculation,
            'acme.concessions.v1.ConcessionStandService': concessions_concession_stand,
            'acme.configuration.v1.ConfigSetQueryService': configuration_config_set_query,
            'acme.customers.v1.CustomerCalculationService': customers_customer_calculation,
            'acme.customers.v1.CustomerService': customers_customer,
            'acme.documents.v1.DocumentQueryService': documents_document_query,
            'acme.documents.v1.DocumentService': documents_document,
            'acme.documents.v1.DocumentValidationService': documents_document_validation,
            'acme.experiments.v1.ExperimentQueryService': experiments_experiment_query,
            'acme.featureflags.v1.FeatureFlagQueryService': featureflags_feature_flag_query,
            'acme.featurestore.v1.FeatureValueCalculationService': featurestore_feature_value_calculation,
            'acme.featurestore.v1.FeatureValueQueryService': featurestore_feature_value_query,
            'acme.featurestore.v1.FeatureValueReportingService': featurestore_feature_value_reporting,
            'acme.featurestore.v1.FeatureValueSyncService': featurestore_feature_value_sync,
            'acme.featurestore.v1.FeatureValueValidationService': featurestore_feature_value_validation,
            'acme.featurestore.v1.FeatureViewApprovalService': featurestore_feature_view_approval,
            'acme.featurestore.v1.FeatureViewCalculationService': featurestore_feature_view_calculation,
            'acme.featurestore.v1.FeatureViewQueryService': featurestore_feature_view_query,
            'acme.featurestore.v1.FeatureViewReportingService': featurestore_feature_view_reporting,
            'acme.featurestore.v1.FeatureViewService': featurestore_feature_view,
            'acme.featurestore.v1.FeatureViewValidationService': featurestore_feature_view_validation,
            'acme.identity.v1.UserQueryService': identity_user_query,
            'acme.identity.v1.UserService': identity_user,
            'acme.identity.v1.UserValidationService': identity_user_validation,
            'acme.invoicing.v1.InvoiceBatchService': invoicing_invoice_batch,
            'acme.keymanagement.v1.CryptoKeyCalculationService': keymanagement_crypto_key_calculation,
            'acme.labeling.v1.AnnotationApprovalService': labeling_annotation_approval,
            'acme.labeling.v1.AnnotationCalculationService': labeling_annotation_calculation,
            'acme.labeling.v1.AnnotationLifecycleService': labeling_annotation_lifecycle,
            'acme.labeling.v1.AnnotationQueryService': labeling_annotation_query,
            'acme.labeling.v1.AnnotationReportingService': labeling_annotation_reporting,
            'acme.labeling.v1.AnnotationValidationService': labeling_annotation_validation,
            'acme.labeling.v1.AnnotationWorkflowService': labeling_annotation_workflow,
            'acme.labeling.v1.LabelSetApprovalService': labeling_label_set_approval,
            'acme.labeling.v1.LabelSetCalculationService': labeling_label_set_calculation,
            'acme.labeling.v1.LabelSetLifecycleService': labeling_label_set_lifecycle,
            'acme.labeling.v1.LabelSetReportingService': labeling_label_set_reporting,
            'acme.labeling.v1.LabelSetSyncService': labeling_label_set_sync,
            'acme.labeling.v1.LabelSetValidationService': labeling_label_set_validation,
            'acme.labeling.v1.LabelingTaskApprovalService': labeling_labeling_task_approval,
            'acme.labeling.v1.LabelingTaskCalculationService': labeling_labeling_task_calculation,
            'acme.labeling.v1.LabelingTaskLifecycleService': labeling_labeling_task_lifecycle,
            'acme.labeling.v1.LabelingTaskQueryService': labeling_labeling_task_query,
            'acme.labeling.v1.LabelingTaskService': labeling_labeling_task,
            'acme.labeling.v1.LabelingTaskValidationService': labeling_labeling_task_validation,
            'acme.labeling.v1.LabelingTaskWorkflowService': labeling_labeling_task_workflow,
            'acme.ledger.v1.LedgerAccountQueryService': ledger_ledger_account_query,
            'acme.ledger.v1.LedgerAccountService': ledger_ledger_account,
            'acme.ledger.v1.LedgerAccountValidationService': ledger_ledger_account_validation,
            'acme.lineage.v1.ImpactApprovalService': lineage_impact_approval,
            'acme.lineage.v1.ImpactCalculationService': lineage_impact_calculation,
            'acme.lineage.v1.ImpactReportingService': lineage_impact_reporting,
            'acme.lineage.v1.ImpactSyncService': lineage_impact_sync,
            'acme.lineage.v1.ImpactValidationService': lineage_impact_validation,
            'acme.lineage.v1.ImpactWorkflowService': lineage_impact_workflow,
            'acme.lineage.v1.LineageEdgeApprovalService': lineage_lineage_edge_approval,
            'acme.lineage.v1.LineageEdgeCalculationService': lineage_lineage_edge_calculation,
            'acme.lineage.v1.LineageEdgeQueryService': lineage_lineage_edge_query,
            'acme.lineage.v1.LineageEdgeWorkflowService': lineage_lineage_edge_workflow,
            'acme.lineage.v1.LineageNodeApprovalService': lineage_lineage_node_approval,
            'acme.lineage.v1.LineageNodeReportingService': lineage_lineage_node_reporting,
            'acme.maintenance.v1.WorkOrderCalculationService': maintenance_work_order_calculation,
            'acme.messaging.v1.ConversationQueryService': messaging_conversation_query,
            'acme.metrics.v1.DashboardExportService': metrics_dashboard_export,
            'acme.metrics.v1.DashboardHistoryService': metrics_dashboard_history,
            'acme.metrics.v1.DashboardNotificationService': metrics_dashboard_notification,
            'acme.metrics.v1.DashboardSyncService': metrics_dashboard_sync,
            'acme.metrics.v1.DashboardValidationService': metrics_dashboard_validation,
            'acme.metrics.v1.MetricAlertAdminService': metrics_metric_alert_admin,
            'acme.metrics.v1.MetricAlertExportService': metrics_metric_alert_export,
            'acme.metrics.v1.MetricAlertHistoryService': metrics_metric_alert_history,
            'acme.metrics.v1.MetricAlertNotificationService': metrics_metric_alert_notification,
            'acme.metrics.v1.MetricAlertValidationService': metrics_metric_alert_validation,
            'acme.metrics.v1.MetricSeriesExportService': metrics_metric_series_export,
            'acme.metrics.v1.MetricSeriesHistoryService': metrics_metric_series_history,
            'acme.metrics.v1.MetricSeriesNotificationService': metrics_metric_series_notification,
            'acme.metrics.v1.MetricSeriesQueryService': metrics_metric_series_query,
            'acme.modelregistry.v1.DeploymentCalculationService': modelregistry_deployment_calculation,
            'acme.modelregistry.v1.DeploymentReportingService': modelregistry_deployment_reporting,
            'acme.modelregistry.v1.DeploymentSyncService': modelregistry_deployment_sync,
            'acme.modelregistry.v1.DeploymentValidationService': modelregistry_deployment_validation,
            'acme.modelregistry.v1.DeploymentWorkflowService': modelregistry_deployment_workflow,
            'acme.modelregistry.v1.ModelVersionQueryService': modelregistry_model_version_query,
            'acme.modelregistry.v1.ModelVersionWorkflowService': modelregistry_model_version_workflow,
            'acme.modelregistry.v1.RegisteredModelApprovalService': modelregistry_registered_model_approval,
            'acme.modelregistry.v1.RegisteredModelCalculationService': modelregistry_registered_model_calculation,
            'acme.modelregistry.v1.RegisteredModelService': modelregistry_registered_model,
            'acme.modelregistry.v1.RegisteredModelSyncService': modelregistry_registered_model_sync,
            'acme.modelregistry.v1.RegisteredModelValidationService': modelregistry_registered_model_validation,
            'acme.notifications.v1.NotificationQueryService': notifications_notification_query,
            'acme.notifications.v1.NotificationService': notifications_notification,
            'acme.notifications.v1.NotificationValidationService': notifications_notification_validation,
            'acme.patients.v1.PatientService': patients_patient,
            'acme.performers.v1.PerformerQueryService': performers_performer_query,
            'acme.prescriptions.v1.PrescriptionQueryService': prescriptions_prescription_query,
            'acme.pricing.v1.PriceListQueryService': pricing_price_list_query,
            'acme.ratelimiting.v1.RateLimitService': ratelimiting_rate_limit,
            'acme.scheduling.v1.ShiftService': scheduling_shift,
            'acme.search.v1.SearchIndexQueryService': search_search_index_query,
            'acme.search.v1.SearchIndexService': search_search_index,
            'acme.search.v1.SearchIndexValidationService': search_search_index_validation,
            'acme.secrets.v1.SecretService': secrets_secret,
            'acme.sponsorships.v1.SponsorQueryService': sponsorships_sponsor_query,
            'acme.sponsorships.v1.SponsorService': sponsorships_sponsor,
            'acme.telehealth.v1.VideoVisitService': telehealth_video_visit,
            'acme.ticketing.v1.TicketService': ticketing_ticket,
            'acme.timekeeping.v1.TimesheetService': timekeeping_timesheet,
            'acme.tours.v1.TourQueryService': tours_tour_query,
            'acme.venues.v1.VenueValidationService': venues_venue_validation,
            'acme.yards.v1.YardCalculationService': yards_yard_calculation,
            'acme.yards.v1.YardService': yards_yard,
        },
    )
    return Dependencies(clients, DomainRepository(container.sessions),
                        container.settings, container.bus)


def register(server: grpc.aio.Server, container: Container) -> dict[str, object]:
    deps = dependencies(container)
    registered: dict[str, object] = {}
    annotation_approval_servicer = Factory(lambda: AnnotationApprovalServicer(deps))()
    labeling_v1_annotation_approval_service_pb2_grpc.add_AnnotationApprovalServiceServicer_to_server(
        annotation_approval_servicer,
        server
    )
    registered['acme.labeling.v1.AnnotationApprovalService'] = annotation_approval_servicer
    annotation_calculation_servicer = Factory(lambda: AnnotationCalculationServicer(deps))()
    labeling_v1_annotation_calculation_service_pb2_grpc.add_AnnotationCalculationServiceServicer_to_server(
        annotation_calculation_servicer,
        server
    )
    registered['acme.labeling.v1.AnnotationCalculationService'] = annotation_calculation_servicer
    annotation_lifecycle_servicer = Factory(lambda: AnnotationLifecycleServicer(deps))()
    labeling_v1_annotation_lifecycle_service_pb2_grpc.add_AnnotationLifecycleServiceServicer_to_server(
        annotation_lifecycle_servicer,
        server
    )
    registered['acme.labeling.v1.AnnotationLifecycleService'] = annotation_lifecycle_servicer
    annotation_query_servicer = Factory(lambda: AnnotationQueryServicer(deps))()
    labeling_v1_annotation_query_service_pb2_grpc.add_AnnotationQueryServiceServicer_to_server(
        annotation_query_servicer,
        server
    )
    registered['acme.labeling.v1.AnnotationQueryService'] = annotation_query_servicer
    annotation_reporting_servicer = Factory(lambda: AnnotationReportingServicer(deps))()
    labeling_v1_annotation_reporting_service_pb2_grpc.add_AnnotationReportingServiceServicer_to_server(
        annotation_reporting_servicer,
        server
    )
    registered['acme.labeling.v1.AnnotationReportingService'] = annotation_reporting_servicer
    annotation_validation_servicer = Factory(lambda: AnnotationValidationServicer(deps))()
    labeling_v1_annotation_validation_service_pb2_grpc.add_AnnotationValidationServiceServicer_to_server(
        annotation_validation_servicer,
        server
    )
    registered['acme.labeling.v1.AnnotationValidationService'] = annotation_validation_servicer
    annotation_workflow_servicer = Factory(lambda: AnnotationWorkflowServicer(deps))()
    labeling_v1_annotation_workflow_service_pb2_grpc.add_AnnotationWorkflowServiceServicer_to_server(
        annotation_workflow_servicer,
        server
    )
    registered['acme.labeling.v1.AnnotationWorkflowService'] = annotation_workflow_servicer
    label_set_approval_servicer = Factory(lambda: LabelSetApprovalServicer(deps))()
    labeling_v1_label_set_approval_service_pb2_grpc.add_LabelSetApprovalServiceServicer_to_server(
        label_set_approval_servicer,
        server
    )
    registered['acme.labeling.v1.LabelSetApprovalService'] = label_set_approval_servicer
    label_set_calculation_servicer = Factory(lambda: LabelSetCalculationServicer(deps))()
    labeling_v1_label_set_calculation_service_pb2_grpc.add_LabelSetCalculationServiceServicer_to_server(
        label_set_calculation_servicer,
        server
    )
    registered['acme.labeling.v1.LabelSetCalculationService'] = label_set_calculation_servicer
    label_set_lifecycle_servicer = Factory(lambda: LabelSetLifecycleServicer(deps))()
    labeling_v1_label_set_lifecycle_service_pb2_grpc.add_LabelSetLifecycleServiceServicer_to_server(
        label_set_lifecycle_servicer,
        server
    )
    registered['acme.labeling.v1.LabelSetLifecycleService'] = label_set_lifecycle_servicer
    label_set_reporting_servicer = Factory(lambda: LabelSetReportingServicer(deps))()
    labeling_v1_label_set_reporting_service_pb2_grpc.add_LabelSetReportingServiceServicer_to_server(
        label_set_reporting_servicer,
        server
    )
    registered['acme.labeling.v1.LabelSetReportingService'] = label_set_reporting_servicer
    label_set_sync_servicer = Factory(lambda: LabelSetSyncServicer(deps))()
    labeling_v1_label_set_sync_service_pb2_grpc.add_LabelSetSyncServiceServicer_to_server(
        label_set_sync_servicer,
        server
    )
    registered['acme.labeling.v1.LabelSetSyncService'] = label_set_sync_servicer
    label_set_validation_servicer = Factory(lambda: LabelSetValidationServicer(deps))()
    labeling_v1_label_set_validation_service_pb2_grpc.add_LabelSetValidationServiceServicer_to_server(
        label_set_validation_servicer,
        server
    )
    registered['acme.labeling.v1.LabelSetValidationService'] = label_set_validation_servicer
    label_set_workflow_servicer = Factory(lambda: LabelSetWorkflowServicer(deps))()
    labeling_v1_label_set_workflow_service_pb2_grpc.add_LabelSetWorkflowServiceServicer_to_server(
        label_set_workflow_servicer,
        server
    )
    registered['acme.labeling.v1.LabelSetWorkflowService'] = label_set_workflow_servicer
    labeling_task_approval_servicer = Factory(lambda: LabelingTaskApprovalServicer(deps))()
    labeling_v1_labeling_task_approval_service_pb2_grpc.add_LabelingTaskApprovalServiceServicer_to_server(
        labeling_task_approval_servicer,
        server
    )
    registered['acme.labeling.v1.LabelingTaskApprovalService'] = labeling_task_approval_servicer
    labeling_task_calculation_servicer = Factory(lambda: LabelingTaskCalculationServicer(deps))()
    labeling_v1_labeling_task_calculation_service_pb2_grpc.add_LabelingTaskCalculationServiceServicer_to_server(
        labeling_task_calculation_servicer,
        server
    )
    registered['acme.labeling.v1.LabelingTaskCalculationService'] = labeling_task_calculation_servicer
    labeling_task_lifecycle_servicer = Factory(lambda: LabelingTaskLifecycleServicer(deps))()
    labeling_v1_labeling_task_lifecycle_service_pb2_grpc.add_LabelingTaskLifecycleServiceServicer_to_server(
        labeling_task_lifecycle_servicer,
        server
    )
    registered['acme.labeling.v1.LabelingTaskLifecycleService'] = labeling_task_lifecycle_servicer
    labeling_task_query_servicer = Factory(lambda: LabelingTaskQueryServicer(deps))()
    labeling_v1_labeling_task_query_service_pb2_grpc.add_LabelingTaskQueryServiceServicer_to_server(
        labeling_task_query_servicer,
        server
    )
    registered['acme.labeling.v1.LabelingTaskQueryService'] = labeling_task_query_servicer
    labeling_task_servicer = Factory(lambda: LabelingTaskServicer(deps))()
    labeling_v1_labeling_task_service_pb2_grpc.add_LabelingTaskServiceServicer_to_server(labeling_task_servicer, server)
    registered['acme.labeling.v1.LabelingTaskService'] = labeling_task_servicer
    labeling_task_validation_servicer = Factory(lambda: LabelingTaskValidationServicer(deps))()
    labeling_v1_labeling_task_validation_service_pb2_grpc.add_LabelingTaskValidationServiceServicer_to_server(
        labeling_task_validation_servicer,
        server
    )
    registered['acme.labeling.v1.LabelingTaskValidationService'] = labeling_task_validation_servicer
    labeling_task_workflow_servicer = Factory(lambda: LabelingTaskWorkflowServicer(deps))()
    labeling_v1_labeling_task_workflow_service_pb2_grpc.add_LabelingTaskWorkflowServiceServicer_to_server(
        labeling_task_workflow_servicer,
        server
    )
    registered['acme.labeling.v1.LabelingTaskWorkflowService'] = labeling_task_workflow_servicer
    subscribe(deps)
    return registered
