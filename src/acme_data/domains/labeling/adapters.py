"""Transport adapters used by labeling workflows."""

from __future__ import annotations

from typing import Protocol

from acme.audit.v1 import audit_event_query_service_pb2 as audit_v1_audit_event_query_service_pb2
from acme.audit.v1 import audit_event_query_service_pb2_grpc as audit_v1_audit_event_query_service_pb2_grpc
from acme.audit.v1 import audit_event_validation_service_pb2 as audit_v1_audit_event_validation_service_pb2
from acme.audit.v1 import audit_event_validation_service_pb2_grpc as audit_v1_audit_event_validation_service_pb2_grpc
from acme.featurestore.v1 import feature_value_query_service_pb2 as featurestore_v1_feature_value_query_service_pb2
from acme.featurestore.v1 import (
    feature_value_query_service_pb2_grpc as featurestore_v1_feature_value_query_service_pb2_grpc,
)
from acme.featurestore.v1 import (
    feature_value_validation_service_pb2 as featurestore_v1_feature_value_validation_service_pb2,
)
from acme.featurestore.v1 import (
    feature_value_validation_service_pb2_grpc as featurestore_v1_feature_value_validation_service_pb2_grpc,
)
from acme.featurestore.v1 import (
    feature_view_reporting_service_pb2 as featurestore_v1_feature_view_reporting_service_pb2,
)
from acme.featurestore.v1 import (
    feature_view_reporting_service_pb2_grpc as featurestore_v1_feature_view_reporting_service_pb2_grpc,
)
from acme.featurestore.v1 import (
    feature_view_validation_service_pb2 as featurestore_v1_feature_view_validation_service_pb2,
)
from acme.featurestore.v1 import (
    feature_view_validation_service_pb2_grpc as featurestore_v1_feature_view_validation_service_pb2_grpc,
)
from acme.identity.v1 import user_query_service_pb2 as identity_v1_user_query_service_pb2
from acme.identity.v1 import user_query_service_pb2_grpc as identity_v1_user_query_service_pb2_grpc
from acme.labeling.v1 import annotation_approval_service_pb2 as labeling_v1_annotation_approval_service_pb2
from acme.labeling.v1 import annotation_approval_service_pb2_grpc as labeling_v1_annotation_approval_service_pb2_grpc
from acme.labeling.v1 import annotation_calculation_service_pb2 as labeling_v1_annotation_calculation_service_pb2
from acme.labeling.v1 import (
    annotation_calculation_service_pb2_grpc as labeling_v1_annotation_calculation_service_pb2_grpc,
)
from acme.labeling.v1 import label_set_calculation_service_pb2 as labeling_v1_label_set_calculation_service_pb2
from acme.labeling.v1 import (
    label_set_calculation_service_pb2_grpc as labeling_v1_label_set_calculation_service_pb2_grpc,
)
from acme.labeling.v1 import label_set_lifecycle_service_pb2 as labeling_v1_label_set_lifecycle_service_pb2
from acme.labeling.v1 import label_set_lifecycle_service_pb2_grpc as labeling_v1_label_set_lifecycle_service_pb2_grpc
from acme.labeling.v1 import label_set_sync_service_pb2 as labeling_v1_label_set_sync_service_pb2
from acme.labeling.v1 import label_set_sync_service_pb2_grpc as labeling_v1_label_set_sync_service_pb2_grpc
from acme.labeling.v1 import labeling_task_approval_service_pb2 as labeling_v1_labeling_task_approval_service_pb2
from acme.labeling.v1 import (
    labeling_task_approval_service_pb2_grpc as labeling_v1_labeling_task_approval_service_pb2_grpc,
)
from acme.labeling.v1 import labeling_task_calculation_service_pb2 as labeling_v1_labeling_task_calculation_service_pb2
from acme.labeling.v1 import (
    labeling_task_calculation_service_pb2_grpc as labeling_v1_labeling_task_calculation_service_pb2_grpc,
)
from acme.labeling.v1 import labeling_task_service_pb2 as labeling_v1_labeling_task_service_pb2
from acme.labeling.v1 import labeling_task_service_pb2_grpc as labeling_v1_labeling_task_service_pb2_grpc
from acme.labeling.v1 import labeling_task_validation_service_pb2 as labeling_v1_labeling_task_validation_service_pb2
from acme.labeling.v1 import (
    labeling_task_validation_service_pb2_grpc as labeling_v1_labeling_task_validation_service_pb2_grpc,
)
from acme.ledger.v1 import ledger_account_service_pb2 as ledger_v1_ledger_account_service_pb2
from acme.ledger.v1 import ledger_account_service_pb2_grpc as ledger_v1_ledger_account_service_pb2_grpc
from acme.lineage.v1 import impact_reporting_service_pb2 as lineage_v1_impact_reporting_service_pb2
from acme.lineage.v1 import impact_reporting_service_pb2_grpc as lineage_v1_impact_reporting_service_pb2_grpc
from acme.lineage.v1 import lineage_edge_approval_service_pb2 as lineage_v1_lineage_edge_approval_service_pb2
from acme.lineage.v1 import lineage_edge_approval_service_pb2_grpc as lineage_v1_lineage_edge_approval_service_pb2_grpc
from acme.metrics.v1 import dashboard_notification_service_pb2 as metrics_v1_dashboard_notification_service_pb2
from acme.metrics.v1 import (
    dashboard_notification_service_pb2_grpc as metrics_v1_dashboard_notification_service_pb2_grpc,
)
from acme.metrics.v1 import dashboard_sync_service_pb2 as metrics_v1_dashboard_sync_service_pb2
from acme.metrics.v1 import dashboard_sync_service_pb2_grpc as metrics_v1_dashboard_sync_service_pb2_grpc
from acme.metrics.v1 import metric_alert_admin_service_pb2 as metrics_v1_metric_alert_admin_service_pb2
from acme.metrics.v1 import metric_alert_admin_service_pb2_grpc as metrics_v1_metric_alert_admin_service_pb2_grpc
from acme.metrics.v1 import metric_alert_notification_service_pb2 as metrics_v1_metric_alert_notification_service_pb2
from acme.metrics.v1 import (
    metric_alert_notification_service_pb2_grpc as metrics_v1_metric_alert_notification_service_pb2_grpc,
)
from acme.modelregistry.v1 import (
    registered_model_sync_service_pb2 as modelregistry_v1_registered_model_sync_service_pb2,
)
from acme.modelregistry.v1 import (
    registered_model_sync_service_pb2_grpc as modelregistry_v1_registered_model_sync_service_pb2_grpc,
)


class AnnotationApprovalRecallAnnotation2Port(Protocol):
    async def execute(
        self,
        request: labeling_v1_labeling_task_validation_service_pb2.ValidateLabelingTaskRequest
    ) -> labeling_v1_labeling_task_validation_service_pb2.ValidateLabelingTaskResponse: ...


class AnnotationApprovalRecallAnnotation2Adapter:
    def __init__(
        self,
        client: labeling_v1_labeling_task_validation_service_pb2_grpc.LabelingTaskValidationServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def execute(
        self,
        request: labeling_v1_labeling_task_validation_service_pb2.ValidateLabelingTaskRequest
    ) -> labeling_v1_labeling_task_validation_service_pb2.ValidateLabelingTaskResponse:
        return await self.client.ValidateLabelingTask(request, timeout=self.timeout)


class AnnotationApprovalRejectAnnotation0Adapter:
    def __init__(
        self,
        client: lineage_v1_impact_reporting_service_pb2_grpc.ImpactReportingServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def __call__(
        self,
        request: lineage_v1_impact_reporting_service_pb2.ListImpactReportsRequest
    ) -> lineage_v1_impact_reporting_service_pb2.ListImpactReportsResponse:
        return await self.client.ListImpactReports(request, timeout=self.timeout)


class AnnotationCalculationExplainAnnotationCalculation0Port(Protocol):
    async def execute(
        self,
        request: labeling_v1_labeling_task_calculation_service_pb2.QuoteLabelingTaskRequest
    ) -> labeling_v1_labeling_task_calculation_service_pb2.QuoteLabelingTaskResponse: ...


class AnnotationCalculationExplainAnnotationCalculation0Adapter:
    def __init__(
        self,
        client: labeling_v1_labeling_task_calculation_service_pb2_grpc.LabelingTaskCalculationServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def execute(
        self,
        request: labeling_v1_labeling_task_calculation_service_pb2.QuoteLabelingTaskRequest
    ) -> labeling_v1_labeling_task_calculation_service_pb2.QuoteLabelingTaskResponse:
        return await self.client.QuoteLabelingTask(request, timeout=self.timeout)


class AnnotationCalculationExplainAnnotationCalculation2Adapter:
    def __init__(
        self,
        client: labeling_v1_labeling_task_calculation_service_pb2_grpc.LabelingTaskCalculationServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def __call__(
        self,
        request: labeling_v1_labeling_task_calculation_service_pb2.EstimateLabelingTaskRequest
    ) -> labeling_v1_labeling_task_calculation_service_pb2.EstimateLabelingTaskResponse:
        return await self.client.EstimateLabelingTask(request, timeout=self.timeout)


class AnnotationReportingGenerateAnnotationReport1Port(Protocol):
    async def execute(
        self,
        request: labeling_v1_labeling_task_calculation_service_pb2.CompareLabelingTaskOptionsRequest
    ) -> labeling_v1_labeling_task_calculation_service_pb2.CompareLabelingTaskOptionsResponse: ...


class AnnotationReportingGenerateAnnotationReport1Adapter:
    def __init__(
        self,
        client: labeling_v1_labeling_task_calculation_service_pb2_grpc.LabelingTaskCalculationServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def execute(
        self,
        request: labeling_v1_labeling_task_calculation_service_pb2.CompareLabelingTaskOptionsRequest
    ) -> labeling_v1_labeling_task_calculation_service_pb2.CompareLabelingTaskOptionsResponse:
        return await self.client.CompareLabelingTaskOptions(request, timeout=self.timeout)


async def annotation_validation_lint_annotations0(
    client: labeling_v1_labeling_task_calculation_service_pb2_grpc.LabelingTaskCalculationServiceStub,
    request: labeling_v1_labeling_task_calculation_service_pb2.ExplainLabelingTaskCalculationRequest,
    timeout: float
) -> labeling_v1_labeling_task_calculation_service_pb2.ExplainLabelingTaskCalculationResponse:
    return await client.ExplainLabelingTaskCalculation(request, timeout=timeout)


class AnnotationValidationNormalizeAnnotation0Port(Protocol):
    async def execute(
        self,
        request: ledger_v1_ledger_account_service_pb2.ListLedgerAccountsRequest
    ) -> ledger_v1_ledger_account_service_pb2.ListLedgerAccountsResponse: ...


class AnnotationValidationNormalizeAnnotation0Adapter:
    def __init__(
        self,
        client: ledger_v1_ledger_account_service_pb2_grpc.LedgerAccountServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def execute(
        self,
        request: ledger_v1_ledger_account_service_pb2.ListLedgerAccountsRequest
    ) -> ledger_v1_ledger_account_service_pb2.ListLedgerAccountsResponse:
        return await self.client.ListLedgerAccounts(request, timeout=self.timeout)


class AnnotationValidationPreviewAnnotation0Adapter:
    def __init__(
        self,
        client: featurestore_v1_feature_value_query_service_pb2_grpc.FeatureValueQueryServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def __call__(
        self,
        request: featurestore_v1_feature_value_query_service_pb2.CountFeatureValuesRequest
    ) -> featurestore_v1_feature_value_query_service_pb2.CountFeatureValuesResponse:
        return await self.client.CountFeatureValues(request, timeout=self.timeout)


class AnnotationWorkflowCancelAnnotationWorkflow3Port(Protocol):
    async def execute(
        self,
        request: labeling_v1_annotation_approval_service_pb2.CommentAnnotationApprovalRequest
    ) -> labeling_v1_annotation_approval_service_pb2.CommentAnnotationApprovalResponse: ...


class AnnotationWorkflowCancelAnnotationWorkflow3Adapter:
    def __init__(
        self,
        client: labeling_v1_annotation_approval_service_pb2_grpc.AnnotationApprovalServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def execute(
        self,
        request: labeling_v1_annotation_approval_service_pb2.CommentAnnotationApprovalRequest
    ) -> labeling_v1_annotation_approval_service_pb2.CommentAnnotationApprovalResponse:
        return await self.client.CommentAnnotationApproval(request, timeout=self.timeout)


async def label_set_approval_submit_label_set1(
    client: labeling_v1_label_set_lifecycle_service_pb2_grpc.LabelSetLifecycleServiceStub,
    request: labeling_v1_label_set_lifecycle_service_pb2.ScheduleLabelSetExpiryRequest,
    timeout: float
) -> labeling_v1_label_set_lifecycle_service_pb2.ScheduleLabelSetExpiryResponse:
    return await client.ScheduleLabelSetExpiry(request, timeout=timeout)


class LabelSetCalculationCalculateLabelSet1Port(Protocol):
    async def execute(
        self,
        request: labeling_v1_annotation_calculation_service_pb2.EstimateAnnotationRequest
    ) -> labeling_v1_annotation_calculation_service_pb2.EstimateAnnotationResponse: ...


class LabelSetCalculationCalculateLabelSet1Adapter:
    def __init__(
        self,
        client: labeling_v1_annotation_calculation_service_pb2_grpc.AnnotationCalculationServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def execute(
        self,
        request: labeling_v1_annotation_calculation_service_pb2.EstimateAnnotationRequest
    ) -> labeling_v1_annotation_calculation_service_pb2.EstimateAnnotationResponse:
        return await self.client.EstimateAnnotation(request, timeout=self.timeout)


class LabelSetCalculationCalculateLabelSet3Adapter:
    def __init__(
        self,
        client: featurestore_v1_feature_view_validation_service_pb2_grpc.FeatureViewValidationServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def __call__(
        self,
        request: featurestore_v1_feature_view_validation_service_pb2.PreviewFeatureViewRequest
    ) -> featurestore_v1_feature_view_validation_service_pb2.PreviewFeatureViewResponse:
        return await self.client.PreviewFeatureView(request, timeout=self.timeout)


async def label_set_calculation_quote_label_set3(
    client: audit_v1_audit_event_validation_service_pb2_grpc.AuditEventValidationServiceStub,
    request: audit_v1_audit_event_validation_service_pb2.ExplainAuditEventDecisionRequest,
    timeout: float
) -> audit_v1_audit_event_validation_service_pb2.ExplainAuditEventDecisionResponse:
    return await client.ExplainAuditEventDecision(request, timeout=timeout)


class LabelSetCalculationRecalculateLabelSets1Port(Protocol):
    async def execute(
        self,
        request: labeling_v1_annotation_calculation_service_pb2.EstimateAnnotationRequest
    ) -> labeling_v1_annotation_calculation_service_pb2.EstimateAnnotationResponse: ...


class LabelSetCalculationRecalculateLabelSets1Adapter:
    def __init__(
        self,
        client: labeling_v1_annotation_calculation_service_pb2_grpc.AnnotationCalculationServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def execute(
        self,
        request: labeling_v1_annotation_calculation_service_pb2.EstimateAnnotationRequest
    ) -> labeling_v1_annotation_calculation_service_pb2.EstimateAnnotationResponse:
        return await self.client.EstimateAnnotation(request, timeout=self.timeout)


class LabelSetLifecycleActivateLabelSet0Adapter:
    def __init__(
        self,
        client: lineage_v1_impact_reporting_service_pb2_grpc.ImpactReportingServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def __call__(
        self,
        request: lineage_v1_impact_reporting_service_pb2.ShareImpactReportRequest
    ) -> lineage_v1_impact_reporting_service_pb2.ShareImpactReportResponse:
        return await self.client.ShareImpactReport(request, timeout=self.timeout)


async def label_set_lifecycle_suspend_label_set1(
    client: labeling_v1_label_set_calculation_service_pb2_grpc.LabelSetCalculationServiceStub,
    request: labeling_v1_label_set_calculation_service_pb2.ExplainLabelSetCalculationRequest,
    timeout: float
) -> labeling_v1_label_set_calculation_service_pb2.ExplainLabelSetCalculationResponse:
    return await client.ExplainLabelSetCalculation(request, timeout=timeout)


class LabelSetLifecycleTerminateLabelSet0Port(Protocol):
    async def execute(
        self,
        request: identity_v1_user_query_service_pb2.BrowseUsersRequest
    ) -> identity_v1_user_query_service_pb2.BrowseUsersResponse: ...


class LabelSetLifecycleTerminateLabelSet0Adapter:
    def __init__(self, client: identity_v1_user_query_service_pb2_grpc.UserQueryServiceStub, timeout: float) -> None:
        self.client = client
        self.timeout = timeout

    async def execute(
        self,
        request: identity_v1_user_query_service_pb2.BrowseUsersRequest
    ) -> identity_v1_user_query_service_pb2.BrowseUsersResponse:
        return await self.client.BrowseUsers(request, timeout=self.timeout)


class LabelSetSyncPullLabelSets1Port(Protocol):
    async def execute(
        self,
        request: labeling_v1_labeling_task_service_pb2.BatchGetLabelingTasksRequest
    ) -> labeling_v1_labeling_task_service_pb2.BatchGetLabelingTasksResponse: ...


class LabelSetSyncPullLabelSets1Adapter:
    def __init__(
        self,
        client: labeling_v1_labeling_task_service_pb2_grpc.LabelingTaskServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def execute(
        self,
        request: labeling_v1_labeling_task_service_pb2.BatchGetLabelingTasksRequest
    ) -> labeling_v1_labeling_task_service_pb2.BatchGetLabelingTasksResponse:
        return await self.client.BatchGetLabelingTasks(request, timeout=self.timeout)


async def label_set_validation_normalize_label_set1(
    client: metrics_v1_metric_alert_notification_service_pb2_grpc.MetricAlertNotificationServiceStub,
    request: metrics_v1_metric_alert_notification_service_pb2.ListMetricAlertSubscriptionsRequest,
    timeout: float
) -> metrics_v1_metric_alert_notification_service_pb2.ListMetricAlertSubscriptionsResponse:
    return await client.ListMetricAlertSubscriptions(request, timeout=timeout)


async def label_set_workflow_pause_label_set_workflow1(
    client: featurestore_v1_feature_view_reporting_service_pb2_grpc.FeatureViewReportingServiceStub,
    request: featurestore_v1_feature_view_reporting_service_pb2.ScheduleFeatureViewReportRequest,
    timeout: float
) -> featurestore_v1_feature_view_reporting_service_pb2.ScheduleFeatureViewReportResponse:
    return await client.ScheduleFeatureViewReport(request, timeout=timeout)


class LabelSetWorkflowResumeLabelSetWorkflow1Port(Protocol):
    async def execute(
        self,
        request: featurestore_v1_feature_view_reporting_service_pb2.GenerateFeatureViewReportRequest
    ) -> featurestore_v1_feature_view_reporting_service_pb2.GenerateFeatureViewReportResponse: ...


class LabelSetWorkflowResumeLabelSetWorkflow1Adapter:
    def __init__(
        self,
        client: featurestore_v1_feature_view_reporting_service_pb2_grpc.FeatureViewReportingServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def execute(
        self,
        request: featurestore_v1_feature_view_reporting_service_pb2.GenerateFeatureViewReportRequest
    ) -> featurestore_v1_feature_view_reporting_service_pb2.GenerateFeatureViewReportResponse:
        return await self.client.GenerateFeatureViewReport(request, timeout=self.timeout)


class LabelSetWorkflowRetryLabelSetWorkflow1Adapter:
    def __init__(
        self,
        client: labeling_v1_labeling_task_approval_service_pb2_grpc.LabelingTaskApprovalServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def __call__(
        self,
        request: labeling_v1_labeling_task_approval_service_pb2.RejectLabelingTaskRequest
    ) -> labeling_v1_labeling_task_approval_service_pb2.RejectLabelingTaskResponse:
        return await self.client.RejectLabelingTask(request, timeout=self.timeout)


async def labeling_task_approval_delegate_labeling_task_approval0(
    client: metrics_v1_dashboard_notification_service_pb2_grpc.DashboardNotificationServiceStub,
    request: metrics_v1_dashboard_notification_service_pb2.SubscribeDashboardUpdatesRequest,
    timeout: float
) -> metrics_v1_dashboard_notification_service_pb2.SubscribeDashboardUpdatesResponse:
    return await client.SubscribeDashboardUpdates(request, timeout=timeout)


class LabelingTaskApprovalRecallLabelingTask1Adapter:
    def __init__(
        self,
        client: modelregistry_v1_registered_model_sync_service_pb2_grpc.RegisteredModelSyncServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def __call__(
        self,
        request: modelregistry_v1_registered_model_sync_service_pb2.ResolveRegisteredModelConflictRequest
    ) -> modelregistry_v1_registered_model_sync_service_pb2.ResolveRegisteredModelConflictResponse:
        return await self.client.ResolveRegisteredModelConflict(request, timeout=self.timeout)


async def labeling_task_calculation_explain_labeling_task_calculation0(
    client: metrics_v1_dashboard_sync_service_pb2_grpc.DashboardSyncServiceStub,
    request: metrics_v1_dashboard_sync_service_pb2.ResolveDashboardConflictRequest,
    timeout: float
) -> metrics_v1_dashboard_sync_service_pb2.ResolveDashboardConflictResponse:
    return await client.ResolveDashboardConflict(request, timeout=timeout)


class LabelingTaskLifecycleTerminateLabelingTask0Port(Protocol):
    async def execute(
        self,
        request: labeling_v1_labeling_task_calculation_service_pb2.CalculateLabelingTaskRequest
    ) -> labeling_v1_labeling_task_calculation_service_pb2.CalculateLabelingTaskResponse: ...


class LabelingTaskLifecycleTerminateLabelingTask0Adapter:
    def __init__(
        self,
        client: labeling_v1_labeling_task_calculation_service_pb2_grpc.LabelingTaskCalculationServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def execute(
        self,
        request: labeling_v1_labeling_task_calculation_service_pb2.CalculateLabelingTaskRequest
    ) -> labeling_v1_labeling_task_calculation_service_pb2.CalculateLabelingTaskResponse:
        return await self.client.CalculateLabelingTask(request, timeout=self.timeout)


class LabelingTaskLifecycleTerminateLabelingTask2Adapter:
    def __init__(
        self,
        client: lineage_v1_lineage_edge_approval_service_pb2_grpc.LineageEdgeApprovalServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def __call__(
        self,
        request: lineage_v1_lineage_edge_approval_service_pb2.ApproveLineageEdgeRequest
    ) -> lineage_v1_lineage_edge_approval_service_pb2.ApproveLineageEdgeResponse:
        return await self.client.ApproveLineageEdge(request, timeout=self.timeout)


class LabelingTaskCloneLabelingTask0Port(Protocol):
    async def execute(
        self,
        request: labeling_v1_labeling_task_validation_service_pb2.PreviewLabelingTaskRequest
    ) -> labeling_v1_labeling_task_validation_service_pb2.PreviewLabelingTaskResponse: ...


class LabelingTaskCloneLabelingTask0Adapter:
    def __init__(
        self,
        client: labeling_v1_labeling_task_validation_service_pb2_grpc.LabelingTaskValidationServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def execute(
        self,
        request: labeling_v1_labeling_task_validation_service_pb2.PreviewLabelingTaskRequest
    ) -> labeling_v1_labeling_task_validation_service_pb2.PreviewLabelingTaskResponse:
        return await self.client.PreviewLabelingTask(request, timeout=self.timeout)


class LabelingTaskCreateLabelingTask1Adapter:
    def __init__(
        self,
        client: featurestore_v1_feature_value_validation_service_pb2_grpc.FeatureValueValidationServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def __call__(
        self,
        request: featurestore_v1_feature_value_validation_service_pb2.ValidateFeatureValueRequest
    ) -> featurestore_v1_feature_value_validation_service_pb2.ValidateFeatureValueResponse:
        return await self.client.ValidateFeatureValue(request, timeout=self.timeout)


async def labeling_task_validation_check_labeling_task_eligibility2(
    client: audit_v1_audit_event_query_service_pb2_grpc.AuditEventQueryServiceStub,
    request: audit_v1_audit_event_query_service_pb2.ResolveAuditEventsRequest,
    timeout: float
) -> audit_v1_audit_event_query_service_pb2.ResolveAuditEventsResponse:
    return await client.ResolveAuditEvents(request, timeout=timeout)


class LabelingTaskValidationLintLabelingTasks0Adapter:
    def __init__(
        self,
        client: audit_v1_audit_event_query_service_pb2_grpc.AuditEventQueryServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def __call__(
        self,
        request: audit_v1_audit_event_query_service_pb2.SuggestAuditEventsRequest
    ) -> audit_v1_audit_event_query_service_pb2.SuggestAuditEventsResponse:
        return await self.client.SuggestAuditEvents(request, timeout=self.timeout)


async def labeling_task_workflow_cancel_labeling_task_workflow2(
    client: labeling_v1_label_set_sync_service_pb2_grpc.LabelSetSyncServiceStub,
    request: labeling_v1_label_set_sync_service_pb2.PushLabelSetRequest,
    timeout: float
) -> labeling_v1_label_set_sync_service_pb2.PushLabelSetResponse:
    return await client.PushLabelSet(request, timeout=timeout)


class LabelingTaskWorkflowResumeLabelingTaskWorkflow0Adapter:
    def __init__(
        self,
        client: metrics_v1_metric_alert_admin_service_pb2_grpc.MetricAlertAdminServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def __call__(
        self,
        request: metrics_v1_metric_alert_admin_service_pb2.RepairMetricAlertRequest
    ) -> metrics_v1_metric_alert_admin_service_pb2.RepairMetricAlertResponse:
        return await self.client.RepairMetricAlert(request, timeout=self.timeout)
