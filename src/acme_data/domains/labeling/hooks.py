"""Replaceable partner hooks of the labeling domain."""

from __future__ import annotations

from acme.audit.v1 import audit_event_query_service_pb2 as audit_v1_audit_event_query_service_pb2
from acme.audit.v1 import audit_event_query_service_pb2_grpc as audit_v1_audit_event_query_service_pb2_grpc
from acme.audit.v1 import audit_event_validation_service_pb2 as audit_v1_audit_event_validation_service_pb2
from acme.audit.v1 import audit_event_validation_service_pb2_grpc as audit_v1_audit_event_validation_service_pb2_grpc
from acme.featurestore.v1 import (
    feature_view_reporting_service_pb2 as featurestore_v1_feature_view_reporting_service_pb2,
)
from acme.featurestore.v1 import (
    feature_view_reporting_service_pb2_grpc as featurestore_v1_feature_view_reporting_service_pb2_grpc,
)
from acme.labeling.v1 import label_set_calculation_service_pb2 as labeling_v1_label_set_calculation_service_pb2
from acme.labeling.v1 import (
    label_set_calculation_service_pb2_grpc as labeling_v1_label_set_calculation_service_pb2_grpc,
)
from acme.labeling.v1 import label_set_lifecycle_service_pb2 as labeling_v1_label_set_lifecycle_service_pb2
from acme.labeling.v1 import label_set_lifecycle_service_pb2_grpc as labeling_v1_label_set_lifecycle_service_pb2_grpc
from acme.labeling.v1 import label_set_sync_service_pb2 as labeling_v1_label_set_sync_service_pb2
from acme.labeling.v1 import label_set_sync_service_pb2_grpc as labeling_v1_label_set_sync_service_pb2_grpc
from acme.labeling.v1 import labeling_task_calculation_service_pb2 as labeling_v1_labeling_task_calculation_service_pb2
from acme.labeling.v1 import (
    labeling_task_calculation_service_pb2_grpc as labeling_v1_labeling_task_calculation_service_pb2_grpc,
)
from acme.metrics.v1 import dashboard_notification_service_pb2 as metrics_v1_dashboard_notification_service_pb2
from acme.metrics.v1 import (
    dashboard_notification_service_pb2_grpc as metrics_v1_dashboard_notification_service_pb2_grpc,
)
from acme.metrics.v1 import dashboard_sync_service_pb2 as metrics_v1_dashboard_sync_service_pb2
from acme.metrics.v1 import dashboard_sync_service_pb2_grpc as metrics_v1_dashboard_sync_service_pb2_grpc
from acme.metrics.v1 import metric_alert_notification_service_pb2 as metrics_v1_metric_alert_notification_service_pb2
from acme.metrics.v1 import (
    metric_alert_notification_service_pb2_grpc as metrics_v1_metric_alert_notification_service_pb2_grpc,
)


async def annotation_validation_lint_annotations0(
    client: labeling_v1_labeling_task_calculation_service_pb2_grpc.LabelingTaskCalculationServiceStub,
    request: labeling_v1_labeling_task_calculation_service_pb2.ExplainLabelingTaskCalculationRequest,
    timeout: float
) -> labeling_v1_labeling_task_calculation_service_pb2.ExplainLabelingTaskCalculationResponse:
    raise RuntimeError("domain hook was not installed")


async def label_set_approval_submit_label_set1(
    client: labeling_v1_label_set_lifecycle_service_pb2_grpc.LabelSetLifecycleServiceStub,
    request: labeling_v1_label_set_lifecycle_service_pb2.ScheduleLabelSetExpiryRequest,
    timeout: float
) -> labeling_v1_label_set_lifecycle_service_pb2.ScheduleLabelSetExpiryResponse:
    raise RuntimeError("domain hook was not installed")


async def label_set_calculation_quote_label_set3(
    client: audit_v1_audit_event_validation_service_pb2_grpc.AuditEventValidationServiceStub,
    request: audit_v1_audit_event_validation_service_pb2.ExplainAuditEventDecisionRequest,
    timeout: float
) -> audit_v1_audit_event_validation_service_pb2.ExplainAuditEventDecisionResponse:
    raise RuntimeError("domain hook was not installed")


async def label_set_lifecycle_suspend_label_set1(
    client: labeling_v1_label_set_calculation_service_pb2_grpc.LabelSetCalculationServiceStub,
    request: labeling_v1_label_set_calculation_service_pb2.ExplainLabelSetCalculationRequest,
    timeout: float
) -> labeling_v1_label_set_calculation_service_pb2.ExplainLabelSetCalculationResponse:
    raise RuntimeError("domain hook was not installed")


async def label_set_validation_normalize_label_set1(
    client: metrics_v1_metric_alert_notification_service_pb2_grpc.MetricAlertNotificationServiceStub,
    request: metrics_v1_metric_alert_notification_service_pb2.ListMetricAlertSubscriptionsRequest,
    timeout: float
) -> metrics_v1_metric_alert_notification_service_pb2.ListMetricAlertSubscriptionsResponse:
    raise RuntimeError("domain hook was not installed")


async def label_set_workflow_pause_label_set_workflow1(
    client: featurestore_v1_feature_view_reporting_service_pb2_grpc.FeatureViewReportingServiceStub,
    request: featurestore_v1_feature_view_reporting_service_pb2.ScheduleFeatureViewReportRequest,
    timeout: float
) -> featurestore_v1_feature_view_reporting_service_pb2.ScheduleFeatureViewReportResponse:
    raise RuntimeError("domain hook was not installed")


async def labeling_task_approval_delegate_labeling_task_approval0(
    client: metrics_v1_dashboard_notification_service_pb2_grpc.DashboardNotificationServiceStub,
    request: metrics_v1_dashboard_notification_service_pb2.SubscribeDashboardUpdatesRequest,
    timeout: float
) -> metrics_v1_dashboard_notification_service_pb2.SubscribeDashboardUpdatesResponse:
    raise RuntimeError("domain hook was not installed")


async def labeling_task_calculation_explain_labeling_task_calculation0(
    client: metrics_v1_dashboard_sync_service_pb2_grpc.DashboardSyncServiceStub,
    request: metrics_v1_dashboard_sync_service_pb2.ResolveDashboardConflictRequest,
    timeout: float
) -> metrics_v1_dashboard_sync_service_pb2.ResolveDashboardConflictResponse:
    raise RuntimeError("domain hook was not installed")


async def labeling_task_validation_check_labeling_task_eligibility2(
    client: audit_v1_audit_event_query_service_pb2_grpc.AuditEventQueryServiceStub,
    request: audit_v1_audit_event_query_service_pb2.ResolveAuditEventsRequest,
    timeout: float
) -> audit_v1_audit_event_query_service_pb2.ResolveAuditEventsResponse:
    raise RuntimeError("domain hook was not installed")


async def labeling_task_workflow_cancel_labeling_task_workflow2(
    client: labeling_v1_label_set_sync_service_pb2_grpc.LabelSetSyncServiceStub,
    request: labeling_v1_label_set_sync_service_pb2.PushLabelSetRequest,
    timeout: float
) -> labeling_v1_label_set_sync_service_pb2.PushLabelSetResponse:
    raise RuntimeError("domain hook was not installed")
