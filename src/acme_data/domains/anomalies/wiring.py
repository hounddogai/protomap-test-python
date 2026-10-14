"""Register and compose every service of the anomalies domain."""

from __future__ import annotations

import grpc

from acme.admissions.v1 import (
    admission_calculation_service_pb2_grpc as admissions_v1_admission_calculation_service_pb2_grpc,
)
from acme.analytics.v1 import funnel_query_service_pb2_grpc as analytics_v1_funnel_query_service_pb2_grpc
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
from acme.anomalies.v1 import anomaly_validation_service_pb2_grpc as anomalies_v1_anomaly_validation_service_pb2_grpc
from acme.anomalies.v1 import anomaly_workflow_service_pb2_grpc as anomalies_v1_anomaly_workflow_service_pb2_grpc
from acme.anomalies.v1 import detector_approval_service_pb2_grpc as anomalies_v1_detector_approval_service_pb2_grpc
from acme.anomalies.v1 import detector_query_service_pb2_grpc as anomalies_v1_detector_query_service_pb2_grpc
from acme.anomalies.v1 import detector_validation_service_pb2_grpc as anomalies_v1_detector_validation_service_pb2_grpc
from acme.anomalies.v1 import detector_workflow_service_pb2_grpc as anomalies_v1_detector_workflow_service_pb2_grpc
from acme.audit.v1 import audit_event_query_service_pb2_grpc as audit_v1_audit_event_query_service_pb2_grpc
from acme.audit.v1 import audit_event_service_pb2_grpc as audit_v1_audit_event_service_pb2_grpc
from acme.authorization.v1 import access_policy_service_pb2_grpc as authorization_v1_access_policy_service_pb2_grpc
from acme.authorization.v1 import (
    access_policy_validation_service_pb2_grpc as authorization_v1_access_policy_validation_service_pb2_grpc,
)
from acme.boxoffice.v1 import (
    box_office_sale_query_service_pb2_grpc as boxoffice_v1_box_office_sale_query_service_pb2_grpc,
)
from acme.careplans.v1 import care_plan_query_service_pb2_grpc as careplans_v1_care_plan_query_service_pb2_grpc
from acme.catalog.v1 import product_query_service_pb2_grpc as catalog_v1_product_query_service_pb2_grpc
from acme.customers.v1 import customer_query_service_pb2_grpc as customers_v1_customer_query_service_pb2_grpc
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
from acme.featureflags.v1 import feature_flag_service_pb2_grpc as featureflags_v1_feature_flag_service_pb2_grpc
from acme.identity.v1 import user_query_service_pb2_grpc as identity_v1_user_query_service_pb2_grpc
from acme.learning.v1 import course_service_pb2_grpc as learning_v1_course_service_pb2_grpc
from acme.ledger.v1 import ledger_account_query_service_pb2_grpc as ledger_v1_ledger_account_query_service_pb2_grpc
from acme.ledger.v1 import (
    ledger_account_validation_service_pb2_grpc as ledger_v1_ledger_account_validation_service_pb2_grpc,
)
from acme.lineage.v1 import impact_calculation_service_pb2_grpc as lineage_v1_impact_calculation_service_pb2_grpc
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
from acme.lineage.v1 import lineage_node_approval_service_pb2_grpc as lineage_v1_lineage_node_approval_service_pb2_grpc
from acme.lineage.v1 import (
    lineage_node_calculation_service_pb2_grpc as lineage_v1_lineage_node_calculation_service_pb2_grpc,
)
from acme.lineage.v1 import lineage_node_query_service_pb2_grpc as lineage_v1_lineage_node_query_service_pb2_grpc
from acme.lineage.v1 import lineage_node_service_pb2_grpc as lineage_v1_lineage_node_service_pb2_grpc
from acme.lineage.v1 import lineage_node_sync_service_pb2_grpc as lineage_v1_lineage_node_sync_service_pb2_grpc
from acme.lineage.v1 import (
    lineage_node_validation_service_pb2_grpc as lineage_v1_lineage_node_validation_service_pb2_grpc,
)
from acme.lineage.v1 import lineage_node_workflow_service_pb2_grpc as lineage_v1_lineage_node_workflow_service_pb2_grpc
from acme.metrics.v1 import dashboard_export_service_pb2_grpc as metrics_v1_dashboard_export_service_pb2_grpc
from acme.metrics.v1 import (
    dashboard_notification_service_pb2_grpc as metrics_v1_dashboard_notification_service_pb2_grpc,
)
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
from acme.metrics.v1 import (
    metric_series_notification_service_pb2_grpc as metrics_v1_metric_series_notification_service_pb2_grpc,
)
from acme.metrics.v1 import metric_series_query_service_pb2_grpc as metrics_v1_metric_series_query_service_pb2_grpc
from acme.metrics.v1 import metric_series_service_pb2_grpc as metrics_v1_metric_series_service_pb2_grpc
from acme.notifications.v1 import (
    notification_query_service_pb2_grpc as notifications_v1_notification_query_service_pb2_grpc,
)
from acme.notifications.v1 import (
    notification_validation_service_pb2_grpc as notifications_v1_notification_validation_service_pb2_grpc,
)
from acme.patients.v1 import patient_query_service_pb2_grpc as patients_v1_patient_query_service_pb2_grpc
from acme.payroll.v1 import pay_run_calculation_service_pb2_grpc as payroll_v1_pay_run_calculation_service_pb2_grpc
from acme.pipelines.v1 import pipeline_service_pb2_grpc as pipelines_v1_pipeline_service_pb2_grpc
from acme.promotions.v1 import (
    promotion_calculation_service_pb2_grpc as promotions_v1_promotion_calculation_service_pb2_grpc,
)
from acme.search.v1 import search_index_service_pb2_grpc as search_v1_search_index_service_pb2_grpc
from acme.search.v1 import (
    search_index_validation_service_pb2_grpc as search_v1_search_index_validation_service_pb2_grpc,
)
from acme.surveys.v1 import survey_service_pb2_grpc as surveys_v1_survey_service_pb2_grpc
from acme.telehealth.v1 import video_visit_service_pb2_grpc as telehealth_v1_video_visit_service_pb2_grpc
from acme.telematics.v1 import telemetry_reading_service_pb2_grpc as telematics_v1_telemetry_reading_service_pb2_grpc
from acme.venues.v1 import venue_service_pb2_grpc as venues_v1_venue_service_pb2_grpc

from acme_data.domains.anomalies.anomaly_approval_service import AnomalyApprovalServicer
from acme_data.domains.anomalies.anomaly_feedback_approval_service import AnomalyFeedbackApprovalServicer
from acme_data.domains.anomalies.anomaly_feedback_calculation_service import AnomalyFeedbackCalculationServicer
from acme_data.domains.anomalies.anomaly_feedback_validation_service import AnomalyFeedbackValidationServicer
from acme_data.domains.anomalies.anomaly_feedback_workflow_service import AnomalyFeedbackWorkflowServicer
from acme_data.domains.anomalies.anomaly_query_service import AnomalyQueryServicer
from acme_data.domains.anomalies.anomaly_service import AnomalyServicer
from acme_data.domains.anomalies.anomaly_validation_service import AnomalyValidationServicer
from acme_data.domains.anomalies.anomaly_workflow_service import AnomalyWorkflowServicer
from acme_data.domains.anomalies.dependencies import Clients
from acme_data.domains.anomalies.dependencies import Dependencies
from acme_data.domains.anomalies.detector_approval_service import DetectorApprovalServicer
from acme_data.domains.anomalies.detector_query_service import DetectorQueryServicer
from acme_data.domains.anomalies.detector_validation_service import DetectorValidationServicer
from acme_data.domains.anomalies.detector_workflow_service import DetectorWorkflowServicer
from acme_data.domains.anomalies.events import subscribe
from acme_data.domains.anomalies.repository import DomainRepository
from acme_data.platform.container import Container
from acme_data.platform.container import Factory


def dependencies(container: Container) -> Dependencies:
    admissions_admission_calculation = container.singleton(
        admissions_v1_admission_calculation_service_pb2_grpc.AdmissionCalculationServiceStub,
        lambda: admissions_v1_admission_calculation_service_pb2_grpc.AdmissionCalculationServiceStub(container.channel)
    )
    analytics_funnel_query = container.singleton(
        analytics_v1_funnel_query_service_pb2_grpc.FunnelQueryServiceStub,
        lambda: analytics_v1_funnel_query_service_pb2_grpc.FunnelQueryServiceStub(container.channel)
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
    anomalies_anomaly_query = container.singleton(
        anomalies_v1_anomaly_query_service_pb2_grpc.AnomalyQueryServiceStub,
        lambda: anomalies_v1_anomaly_query_service_pb2_grpc.AnomalyQueryServiceStub(container.channel)
    )
    anomalies_anomaly = container.singleton(
        anomalies_v1_anomaly_service_pb2_grpc.AnomalyServiceStub,
        lambda: anomalies_v1_anomaly_service_pb2_grpc.AnomalyServiceStub(container.channel)
    )
    anomalies_anomaly_validation = container.singleton(
        anomalies_v1_anomaly_validation_service_pb2_grpc.AnomalyValidationServiceStub,
        lambda: anomalies_v1_anomaly_validation_service_pb2_grpc.AnomalyValidationServiceStub(container.channel)
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
    audit_audit_event_query = container.singleton(
        audit_v1_audit_event_query_service_pb2_grpc.AuditEventQueryServiceStub,
        lambda: audit_v1_audit_event_query_service_pb2_grpc.AuditEventQueryServiceStub(container.channel)
    )
    audit_audit_event = container.singleton(
        audit_v1_audit_event_service_pb2_grpc.AuditEventServiceStub,
        lambda: audit_v1_audit_event_service_pb2_grpc.AuditEventServiceStub(container.channel)
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
    boxoffice_box_office_sale_query = container.singleton(
        boxoffice_v1_box_office_sale_query_service_pb2_grpc.BoxOfficeSaleQueryServiceStub,
        lambda: boxoffice_v1_box_office_sale_query_service_pb2_grpc.BoxOfficeSaleQueryServiceStub(container.channel)
    )
    careplans_care_plan_query = container.singleton(
        careplans_v1_care_plan_query_service_pb2_grpc.CarePlanQueryServiceStub,
        lambda: careplans_v1_care_plan_query_service_pb2_grpc.CarePlanQueryServiceStub(container.channel)
    )
    catalog_product_query = container.singleton(
        catalog_v1_product_query_service_pb2_grpc.ProductQueryServiceStub,
        lambda: catalog_v1_product_query_service_pb2_grpc.ProductQueryServiceStub(container.channel)
    )
    customers_customer_query = container.singleton(
        customers_v1_customer_query_service_pb2_grpc.CustomerQueryServiceStub,
        lambda: customers_v1_customer_query_service_pb2_grpc.CustomerQueryServiceStub(container.channel)
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
    featureflags_feature_flag = container.singleton(
        featureflags_v1_feature_flag_service_pb2_grpc.FeatureFlagServiceStub,
        lambda: featureflags_v1_feature_flag_service_pb2_grpc.FeatureFlagServiceStub(container.channel)
    )
    identity_user_query = container.singleton(
        identity_v1_user_query_service_pb2_grpc.UserQueryServiceStub,
        lambda: identity_v1_user_query_service_pb2_grpc.UserQueryServiceStub(container.channel)
    )
    learning_course = container.singleton(
        learning_v1_course_service_pb2_grpc.CourseServiceStub,
        lambda: learning_v1_course_service_pb2_grpc.CourseServiceStub(container.channel)
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
    metrics_dashboard_export = container.singleton(
        metrics_v1_dashboard_export_service_pb2_grpc.DashboardExportServiceStub,
        lambda: metrics_v1_dashboard_export_service_pb2_grpc.DashboardExportServiceStub(container.channel)
    )
    metrics_dashboard_notification = container.singleton(
        metrics_v1_dashboard_notification_service_pb2_grpc.DashboardNotificationServiceStub,
        lambda: metrics_v1_dashboard_notification_service_pb2_grpc.DashboardNotificationServiceStub(container.channel)
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
    patients_patient_query = container.singleton(
        patients_v1_patient_query_service_pb2_grpc.PatientQueryServiceStub,
        lambda: patients_v1_patient_query_service_pb2_grpc.PatientQueryServiceStub(container.channel)
    )
    payroll_pay_run_calculation = container.singleton(
        payroll_v1_pay_run_calculation_service_pb2_grpc.PayRunCalculationServiceStub,
        lambda: payroll_v1_pay_run_calculation_service_pb2_grpc.PayRunCalculationServiceStub(container.channel)
    )
    pipelines_pipeline = container.singleton(
        pipelines_v1_pipeline_service_pb2_grpc.PipelineServiceStub,
        lambda: pipelines_v1_pipeline_service_pb2_grpc.PipelineServiceStub(container.channel)
    )
    promotions_promotion_calculation = container.singleton(
        promotions_v1_promotion_calculation_service_pb2_grpc.PromotionCalculationServiceStub,
        lambda: promotions_v1_promotion_calculation_service_pb2_grpc.PromotionCalculationServiceStub(container.channel)
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
    telematics_telemetry_reading = container.singleton(
        telematics_v1_telemetry_reading_service_pb2_grpc.TelemetryReadingServiceStub,
        lambda: telematics_v1_telemetry_reading_service_pb2_grpc.TelemetryReadingServiceStub(container.channel)
    )
    venues_venue = container.singleton(
        venues_v1_venue_service_pb2_grpc.VenueServiceStub,
        lambda: venues_v1_venue_service_pb2_grpc.VenueServiceStub(container.channel)
    )
    clients = Clients(
        admissions_admission_calculation=admissions_admission_calculation,
        analytics_funnel_query=analytics_funnel_query,
        anomalies_anomaly_approval=anomalies_anomaly_approval,
        anomalies_anomaly_feedback_approval=anomalies_anomaly_feedback_approval,
        anomalies_anomaly_feedback_calculation=anomalies_anomaly_feedback_calculation,
        anomalies_anomaly_feedback_validation=anomalies_anomaly_feedback_validation,
        anomalies_anomaly_query=anomalies_anomaly_query,
        anomalies_anomaly=anomalies_anomaly,
        anomalies_anomaly_validation=anomalies_anomaly_validation,
        anomalies_anomaly_workflow=anomalies_anomaly_workflow,
        anomalies_detector_approval=anomalies_detector_approval,
        anomalies_detector_query=anomalies_detector_query,
        anomalies_detector_validation=anomalies_detector_validation,
        audit_audit_event_query=audit_audit_event_query,
        audit_audit_event=audit_audit_event,
        authorization_access_policy=authorization_access_policy,
        authorization_access_policy_validation=authorization_access_policy_validation,
        boxoffice_box_office_sale_query=boxoffice_box_office_sale_query,
        careplans_care_plan_query=careplans_care_plan_query,
        catalog_product_query=catalog_product_query,
        customers_customer_query=customers_customer_query,
        datasets_data_schema_calculation=datasets_data_schema_calculation,
        datasets_data_schema_validation=datasets_data_schema_validation,
        datasets_dataset_query=datasets_dataset_query,
        datasets_dataset=datasets_dataset,
        datasets_dataset_validation=datasets_dataset_validation,
        datasets_dataset_version_calculation=datasets_dataset_version_calculation,
        datasets_dataset_version_query=datasets_dataset_version_query,
        datasets_dataset_version_validation=datasets_dataset_version_validation,
        featureflags_feature_flag=featureflags_feature_flag,
        identity_user_query=identity_user_query,
        learning_course=learning_course,
        ledger_ledger_account_query=ledger_ledger_account_query,
        ledger_ledger_account_validation=ledger_ledger_account_validation,
        lineage_impact_calculation=lineage_impact_calculation,
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
        lineage_lineage_node_approval=lineage_lineage_node_approval,
        lineage_lineage_node_calculation=lineage_lineage_node_calculation,
        lineage_lineage_node_query=lineage_lineage_node_query,
        lineage_lineage_node=lineage_lineage_node,
        lineage_lineage_node_sync=lineage_lineage_node_sync,
        lineage_lineage_node_validation=lineage_lineage_node_validation,
        lineage_lineage_node_workflow=lineage_lineage_node_workflow,
        metrics_dashboard_export=metrics_dashboard_export,
        metrics_dashboard_notification=metrics_dashboard_notification,
        metrics_dashboard_validation=metrics_dashboard_validation,
        metrics_metric_alert_export=metrics_metric_alert_export,
        metrics_metric_alert_history=metrics_metric_alert_history,
        metrics_metric_alert_notification=metrics_metric_alert_notification,
        metrics_metric_alert_query=metrics_metric_alert_query,
        metrics_metric_alert_validation=metrics_metric_alert_validation,
        metrics_metric_series_notification=metrics_metric_series_notification,
        metrics_metric_series_query=metrics_metric_series_query,
        metrics_metric_series=metrics_metric_series,
        notifications_notification_query=notifications_notification_query,
        notifications_notification_validation=notifications_notification_validation,
        patients_patient_query=patients_patient_query,
        payroll_pay_run_calculation=payroll_pay_run_calculation,
        pipelines_pipeline=pipelines_pipeline,
        promotions_promotion_calculation=promotions_promotion_calculation,
        search_search_index=search_search_index,
        search_search_index_validation=search_search_index_validation,
        surveys_survey=surveys_survey,
        telehealth_video_visit=telehealth_video_visit,
        telematics_telemetry_reading=telematics_telemetry_reading,
        venues_venue=venues_venue,
        registry={
            'acme.admissions.v1.AdmissionCalculationService': admissions_admission_calculation,
            'acme.analytics.v1.FunnelQueryService': analytics_funnel_query,
            'acme.anomalies.v1.AnomalyApprovalService': anomalies_anomaly_approval,
            'acme.anomalies.v1.AnomalyFeedbackApprovalService': anomalies_anomaly_feedback_approval,
            'acme.anomalies.v1.AnomalyFeedbackCalculationService': anomalies_anomaly_feedback_calculation,
            'acme.anomalies.v1.AnomalyFeedbackValidationService': anomalies_anomaly_feedback_validation,
            'acme.anomalies.v1.AnomalyQueryService': anomalies_anomaly_query,
            'acme.anomalies.v1.AnomalyService': anomalies_anomaly,
            'acme.anomalies.v1.AnomalyValidationService': anomalies_anomaly_validation,
            'acme.anomalies.v1.AnomalyWorkflowService': anomalies_anomaly_workflow,
            'acme.anomalies.v1.DetectorApprovalService': anomalies_detector_approval,
            'acme.anomalies.v1.DetectorQueryService': anomalies_detector_query,
            'acme.anomalies.v1.DetectorValidationService': anomalies_detector_validation,
            'acme.audit.v1.AuditEventQueryService': audit_audit_event_query,
            'acme.audit.v1.AuditEventService': audit_audit_event,
            'acme.authorization.v1.AccessPolicyService': authorization_access_policy,
            'acme.authorization.v1.AccessPolicyValidationService': authorization_access_policy_validation,
            'acme.boxoffice.v1.BoxOfficeSaleQueryService': boxoffice_box_office_sale_query,
            'acme.careplans.v1.CarePlanQueryService': careplans_care_plan_query,
            'acme.catalog.v1.ProductQueryService': catalog_product_query,
            'acme.customers.v1.CustomerQueryService': customers_customer_query,
            'acme.datasets.v1.DataSchemaCalculationService': datasets_data_schema_calculation,
            'acme.datasets.v1.DataSchemaValidationService': datasets_data_schema_validation,
            'acme.datasets.v1.DatasetQueryService': datasets_dataset_query,
            'acme.datasets.v1.DatasetService': datasets_dataset,
            'acme.datasets.v1.DatasetValidationService': datasets_dataset_validation,
            'acme.datasets.v1.DatasetVersionCalculationService': datasets_dataset_version_calculation,
            'acme.datasets.v1.DatasetVersionQueryService': datasets_dataset_version_query,
            'acme.datasets.v1.DatasetVersionValidationService': datasets_dataset_version_validation,
            'acme.featureflags.v1.FeatureFlagService': featureflags_feature_flag,
            'acme.identity.v1.UserQueryService': identity_user_query,
            'acme.learning.v1.CourseService': learning_course,
            'acme.ledger.v1.LedgerAccountQueryService': ledger_ledger_account_query,
            'acme.ledger.v1.LedgerAccountValidationService': ledger_ledger_account_validation,
            'acme.lineage.v1.ImpactCalculationService': lineage_impact_calculation,
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
            'acme.lineage.v1.LineageNodeApprovalService': lineage_lineage_node_approval,
            'acme.lineage.v1.LineageNodeCalculationService': lineage_lineage_node_calculation,
            'acme.lineage.v1.LineageNodeQueryService': lineage_lineage_node_query,
            'acme.lineage.v1.LineageNodeService': lineage_lineage_node,
            'acme.lineage.v1.LineageNodeSyncService': lineage_lineage_node_sync,
            'acme.lineage.v1.LineageNodeValidationService': lineage_lineage_node_validation,
            'acme.lineage.v1.LineageNodeWorkflowService': lineage_lineage_node_workflow,
            'acme.metrics.v1.DashboardExportService': metrics_dashboard_export,
            'acme.metrics.v1.DashboardNotificationService': metrics_dashboard_notification,
            'acme.metrics.v1.DashboardValidationService': metrics_dashboard_validation,
            'acme.metrics.v1.MetricAlertExportService': metrics_metric_alert_export,
            'acme.metrics.v1.MetricAlertHistoryService': metrics_metric_alert_history,
            'acme.metrics.v1.MetricAlertNotificationService': metrics_metric_alert_notification,
            'acme.metrics.v1.MetricAlertQueryService': metrics_metric_alert_query,
            'acme.metrics.v1.MetricAlertValidationService': metrics_metric_alert_validation,
            'acme.metrics.v1.MetricSeriesNotificationService': metrics_metric_series_notification,
            'acme.metrics.v1.MetricSeriesQueryService': metrics_metric_series_query,
            'acme.metrics.v1.MetricSeriesService': metrics_metric_series,
            'acme.notifications.v1.NotificationQueryService': notifications_notification_query,
            'acme.notifications.v1.NotificationValidationService': notifications_notification_validation,
            'acme.patients.v1.PatientQueryService': patients_patient_query,
            'acme.payroll.v1.PayRunCalculationService': payroll_pay_run_calculation,
            'acme.pipelines.v1.PipelineService': pipelines_pipeline,
            'acme.promotions.v1.PromotionCalculationService': promotions_promotion_calculation,
            'acme.search.v1.SearchIndexService': search_search_index,
            'acme.search.v1.SearchIndexValidationService': search_search_index_validation,
            'acme.surveys.v1.SurveyService': surveys_survey,
            'acme.telehealth.v1.VideoVisitService': telehealth_video_visit,
            'acme.telematics.v1.TelemetryReadingService': telematics_telemetry_reading,
            'acme.venues.v1.VenueService': venues_venue,
        },
    )
    return Dependencies(clients, DomainRepository(container.sessions),
                        container.settings, container.bus)


def register(server: grpc.aio.Server, container: Container) -> dict[str, object]:
    deps = dependencies(container)
    registered: dict[str, object] = {}
    anomaly_approval_servicer = Factory(lambda: AnomalyApprovalServicer(deps))()
    anomalies_v1_anomaly_approval_service_pb2_grpc.add_AnomalyApprovalServiceServicer_to_server(
        anomaly_approval_servicer,
        server
    )
    registered['acme.anomalies.v1.AnomalyApprovalService'] = anomaly_approval_servicer
    anomaly_feedback_approval_servicer = Factory(lambda: AnomalyFeedbackApprovalServicer(deps))()
    anomalies_v1_anomaly_feedback_approval_service_pb2_grpc.add_AnomalyFeedbackApprovalServiceServicer_to_server(
        anomaly_feedback_approval_servicer,
        server
    )
    registered['acme.anomalies.v1.AnomalyFeedbackApprovalService'] = anomaly_feedback_approval_servicer
    anomaly_feedback_calculation_servicer = Factory(lambda: AnomalyFeedbackCalculationServicer(deps))()
    anomalies_v1_anomaly_feedback_calculation_service_pb2_grpc.add_AnomalyFeedbackCalculationServiceServicer_to_server(
        anomaly_feedback_calculation_servicer,
        server
    )
    registered['acme.anomalies.v1.AnomalyFeedbackCalculationService'] = anomaly_feedback_calculation_servicer
    anomaly_feedback_validation_servicer = Factory(lambda: AnomalyFeedbackValidationServicer(deps))()
    anomalies_v1_anomaly_feedback_validation_service_pb2_grpc.add_AnomalyFeedbackValidationServiceServicer_to_server(
        anomaly_feedback_validation_servicer,
        server
    )
    registered['acme.anomalies.v1.AnomalyFeedbackValidationService'] = anomaly_feedback_validation_servicer
    anomaly_feedback_workflow_servicer = Factory(lambda: AnomalyFeedbackWorkflowServicer(deps))()
    anomalies_v1_anomaly_feedback_workflow_service_pb2_grpc.add_AnomalyFeedbackWorkflowServiceServicer_to_server(
        anomaly_feedback_workflow_servicer,
        server
    )
    registered['acme.anomalies.v1.AnomalyFeedbackWorkflowService'] = anomaly_feedback_workflow_servicer
    anomaly_query_servicer = Factory(lambda: AnomalyQueryServicer(deps))()
    anomalies_v1_anomaly_query_service_pb2_grpc.add_AnomalyQueryServiceServicer_to_server(
        anomaly_query_servicer,
        server
    )
    registered['acme.anomalies.v1.AnomalyQueryService'] = anomaly_query_servicer
    anomaly_servicer = Factory(lambda: AnomalyServicer(deps))()
    anomalies_v1_anomaly_service_pb2_grpc.add_AnomalyServiceServicer_to_server(anomaly_servicer, server)
    registered['acme.anomalies.v1.AnomalyService'] = anomaly_servicer
    anomaly_validation_servicer = Factory(lambda: AnomalyValidationServicer(deps))()
    anomalies_v1_anomaly_validation_service_pb2_grpc.add_AnomalyValidationServiceServicer_to_server(
        anomaly_validation_servicer,
        server
    )
    registered['acme.anomalies.v1.AnomalyValidationService'] = anomaly_validation_servicer
    anomaly_workflow_servicer = Factory(lambda: AnomalyWorkflowServicer(deps))()
    anomalies_v1_anomaly_workflow_service_pb2_grpc.add_AnomalyWorkflowServiceServicer_to_server(
        anomaly_workflow_servicer,
        server
    )
    registered['acme.anomalies.v1.AnomalyWorkflowService'] = anomaly_workflow_servicer
    detector_approval_servicer = Factory(lambda: DetectorApprovalServicer(deps))()
    anomalies_v1_detector_approval_service_pb2_grpc.add_DetectorApprovalServiceServicer_to_server(
        detector_approval_servicer,
        server
    )
    registered['acme.anomalies.v1.DetectorApprovalService'] = detector_approval_servicer
    detector_query_servicer = Factory(lambda: DetectorQueryServicer(deps))()
    anomalies_v1_detector_query_service_pb2_grpc.add_DetectorQueryServiceServicer_to_server(
        detector_query_servicer,
        server
    )
    registered['acme.anomalies.v1.DetectorQueryService'] = detector_query_servicer
    detector_validation_servicer = Factory(lambda: DetectorValidationServicer(deps))()
    anomalies_v1_detector_validation_service_pb2_grpc.add_DetectorValidationServiceServicer_to_server(
        detector_validation_servicer,
        server
    )
    registered['acme.anomalies.v1.DetectorValidationService'] = detector_validation_servicer
    detector_workflow_servicer = Factory(lambda: DetectorWorkflowServicer(deps))()
    anomalies_v1_detector_workflow_service_pb2_grpc.add_DetectorWorkflowServiceServicer_to_server(
        detector_workflow_servicer,
        server
    )
    registered['acme.anomalies.v1.DetectorWorkflowService'] = detector_workflow_servicer
    subscribe(deps)
    return registered
