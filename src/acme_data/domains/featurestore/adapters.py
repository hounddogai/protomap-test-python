"""Transport adapters used by featurestore workflows."""

from __future__ import annotations

from typing import Protocol

from acme.anomalies.v1 import (
    anomaly_feedback_calculation_service_pb2 as anomalies_v1_anomaly_feedback_calculation_service_pb2,
)
from acme.anomalies.v1 import (
    anomaly_feedback_calculation_service_pb2_grpc as anomalies_v1_anomaly_feedback_calculation_service_pb2_grpc,
)
from acme.anomalies.v1 import anomaly_workflow_service_pb2 as anomalies_v1_anomaly_workflow_service_pb2
from acme.anomalies.v1 import anomaly_workflow_service_pb2_grpc as anomalies_v1_anomaly_workflow_service_pb2_grpc
from acme.authorization.v1 import (
    access_policy_validation_service_pb2 as authorization_v1_access_policy_validation_service_pb2,
)
from acme.authorization.v1 import (
    access_policy_validation_service_pb2_grpc as authorization_v1_access_policy_validation_service_pb2_grpc,
)
from acme.certificates.v1 import (
    certificate_calculation_service_pb2 as certificates_v1_certificate_calculation_service_pb2,
)
from acme.certificates.v1 import (
    certificate_calculation_service_pb2_grpc as certificates_v1_certificate_calculation_service_pb2_grpc,
)
from acme.datasets.v1 import data_schema_validation_service_pb2 as datasets_v1_data_schema_validation_service_pb2
from acme.datasets.v1 import (
    data_schema_validation_service_pb2_grpc as datasets_v1_data_schema_validation_service_pb2_grpc,
)
from acme.datasets.v1 import dataset_query_service_pb2 as datasets_v1_dataset_query_service_pb2
from acme.datasets.v1 import dataset_query_service_pb2_grpc as datasets_v1_dataset_query_service_pb2_grpc
from acme.datasets.v1 import dataset_service_pb2 as datasets_v1_dataset_service_pb2
from acme.datasets.v1 import dataset_service_pb2_grpc as datasets_v1_dataset_service_pb2_grpc
from acme.datasets.v1 import dataset_version_query_service_pb2 as datasets_v1_dataset_version_query_service_pb2
from acme.datasets.v1 import (
    dataset_version_query_service_pb2_grpc as datasets_v1_dataset_version_query_service_pb2_grpc,
)
from acme.documents.v1 import document_service_pb2 as documents_v1_document_service_pb2
from acme.documents.v1 import document_service_pb2_grpc as documents_v1_document_service_pb2_grpc
from acme.documents.v1 import document_validation_service_pb2 as documents_v1_document_validation_service_pb2
from acme.documents.v1 import document_validation_service_pb2_grpc as documents_v1_document_validation_service_pb2_grpc
from acme.featureflags.v1 import feature_flag_service_pb2 as featureflags_v1_feature_flag_service_pb2
from acme.featureflags.v1 import feature_flag_service_pb2_grpc as featureflags_v1_feature_flag_service_pb2_grpc
from acme.featurestore.v1 import entity_calculation_service_pb2 as featurestore_v1_entity_calculation_service_pb2
from acme.featurestore.v1 import (
    entity_calculation_service_pb2_grpc as featurestore_v1_entity_calculation_service_pb2_grpc,
)
from acme.featurestore.v1 import entity_import_service_pb2 as featurestore_v1_entity_import_service_pb2
from acme.featurestore.v1 import entity_import_service_pb2_grpc as featurestore_v1_entity_import_service_pb2_grpc
from acme.featurestore.v1 import entity_sync_service_pb2 as featurestore_v1_entity_sync_service_pb2
from acme.featurestore.v1 import entity_sync_service_pb2_grpc as featurestore_v1_entity_sync_service_pb2_grpc
from acme.featurestore.v1 import entity_validation_service_pb2 as featurestore_v1_entity_validation_service_pb2
from acme.featurestore.v1 import (
    entity_validation_service_pb2_grpc as featurestore_v1_entity_validation_service_pb2_grpc,
)
from acme.featurestore.v1 import (
    feature_value_approval_service_pb2 as featurestore_v1_feature_value_approval_service_pb2,
)
from acme.featurestore.v1 import (
    feature_value_approval_service_pb2_grpc as featurestore_v1_feature_value_approval_service_pb2_grpc,
)
from acme.featurestore.v1 import (
    feature_value_calculation_service_pb2 as featurestore_v1_feature_value_calculation_service_pb2,
)
from acme.featurestore.v1 import (
    feature_value_calculation_service_pb2_grpc as featurestore_v1_feature_value_calculation_service_pb2_grpc,
)
from acme.featurestore.v1 import feature_value_import_service_pb2 as featurestore_v1_feature_value_import_service_pb2
from acme.featurestore.v1 import (
    feature_value_import_service_pb2_grpc as featurestore_v1_feature_value_import_service_pb2_grpc,
)
from acme.featurestore.v1 import feature_value_sync_service_pb2 as featurestore_v1_feature_value_sync_service_pb2
from acme.featurestore.v1 import (
    feature_value_sync_service_pb2_grpc as featurestore_v1_feature_value_sync_service_pb2_grpc,
)
from acme.featurestore.v1 import (
    feature_view_calculation_service_pb2 as featurestore_v1_feature_view_calculation_service_pb2,
)
from acme.featurestore.v1 import (
    feature_view_calculation_service_pb2_grpc as featurestore_v1_feature_view_calculation_service_pb2_grpc,
)
from acme.featurestore.v1 import feature_view_query_service_pb2 as featurestore_v1_feature_view_query_service_pb2
from acme.featurestore.v1 import (
    feature_view_query_service_pb2_grpc as featurestore_v1_feature_view_query_service_pb2_grpc,
)
from acme.featurestore.v1 import (
    feature_view_reporting_service_pb2 as featurestore_v1_feature_view_reporting_service_pb2,
)
from acme.featurestore.v1 import (
    feature_view_reporting_service_pb2_grpc as featurestore_v1_feature_view_reporting_service_pb2_grpc,
)
from acme.featurestore.v1 import feature_view_service_pb2 as featurestore_v1_feature_view_service_pb2
from acme.featurestore.v1 import feature_view_service_pb2_grpc as featurestore_v1_feature_view_service_pb2_grpc
from acme.featurestore.v1 import feature_view_sync_service_pb2 as featurestore_v1_feature_view_sync_service_pb2
from acme.featurestore.v1 import (
    feature_view_sync_service_pb2_grpc as featurestore_v1_feature_view_sync_service_pb2_grpc,
)
from acme.featurestore.v1 import (
    feature_view_validation_service_pb2 as featurestore_v1_feature_view_validation_service_pb2,
)
from acme.featurestore.v1 import (
    feature_view_validation_service_pb2_grpc as featurestore_v1_feature_view_validation_service_pb2_grpc,
)
from acme.identity.v1 import user_validation_service_pb2 as identity_v1_user_validation_service_pb2
from acme.identity.v1 import user_validation_service_pb2_grpc as identity_v1_user_validation_service_pb2_grpc
from acme.lineage.v1 import impact_validation_service_pb2 as lineage_v1_impact_validation_service_pb2
from acme.lineage.v1 import impact_validation_service_pb2_grpc as lineage_v1_impact_validation_service_pb2_grpc
from acme.lineage.v1 import lineage_edge_import_service_pb2 as lineage_v1_lineage_edge_import_service_pb2
from acme.lineage.v1 import lineage_edge_import_service_pb2_grpc as lineage_v1_lineage_edge_import_service_pb2_grpc
from acme.lineage.v1 import lineage_edge_sync_service_pb2 as lineage_v1_lineage_edge_sync_service_pb2
from acme.lineage.v1 import lineage_edge_sync_service_pb2_grpc as lineage_v1_lineage_edge_sync_service_pb2_grpc
from acme.metrics.v1 import metric_series_export_service_pb2 as metrics_v1_metric_series_export_service_pb2
from acme.metrics.v1 import metric_series_export_service_pb2_grpc as metrics_v1_metric_series_export_service_pb2_grpc
from acme.metrics.v1 import metric_series_history_service_pb2 as metrics_v1_metric_series_history_service_pb2
from acme.metrics.v1 import metric_series_history_service_pb2_grpc as metrics_v1_metric_series_history_service_pb2_grpc
from acme.notifications.v1 import (
    notification_validation_service_pb2 as notifications_v1_notification_validation_service_pb2,
)
from acme.notifications.v1 import (
    notification_validation_service_pb2_grpc as notifications_v1_notification_validation_service_pb2_grpc,
)


async def entity_approval_comment_entity_approval2(
    client: featurestore_v1_feature_value_sync_service_pb2_grpc.FeatureValueSyncServiceStub,
    request: featurestore_v1_feature_value_sync_service_pb2.ListFeatureValueConflictsRequest,
    timeout: float
) -> featurestore_v1_feature_value_sync_service_pb2.ListFeatureValueConflictsResponse:
    return await client.ListFeatureValueConflicts(request, timeout=timeout)


class EntityApprovalRecallEntity0Port(Protocol):
    async def execute(
        self,
        request: featurestore_v1_entity_import_service_pb2.ListEntityImportsRequest
    ) -> featurestore_v1_entity_import_service_pb2.ListEntityImportsResponse: ...


class EntityApprovalRecallEntity0Adapter:
    def __init__(
        self,
        client: featurestore_v1_entity_import_service_pb2_grpc.EntityImportServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def execute(
        self,
        request: featurestore_v1_entity_import_service_pb2.ListEntityImportsRequest
    ) -> featurestore_v1_entity_import_service_pb2.ListEntityImportsResponse:
        return await self.client.ListEntityImports(request, timeout=self.timeout)


class EntityApprovalRecallEntity2Adapter:
    def __init__(
        self,
        client: anomalies_v1_anomaly_workflow_service_pb2_grpc.AnomalyWorkflowServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def __call__(
        self,
        request: anomalies_v1_anomaly_workflow_service_pb2.AdvanceAnomalyWorkflowRequest
    ) -> anomalies_v1_anomaly_workflow_service_pb2.AdvanceAnomalyWorkflowResponse:
        return await self.client.AdvanceAnomalyWorkflow(request, timeout=self.timeout)


class EntityCalculationExplainEntityCalculation2Port(Protocol):
    async def execute(
        self,
        request: featurestore_v1_feature_view_validation_service_pb2.ScoreFeatureViewRequest
    ) -> featurestore_v1_feature_view_validation_service_pb2.ScoreFeatureViewResponse: ...


class EntityCalculationExplainEntityCalculation2Adapter:
    def __init__(
        self,
        client: featurestore_v1_feature_view_validation_service_pb2_grpc.FeatureViewValidationServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def execute(
        self,
        request: featurestore_v1_feature_view_validation_service_pb2.ScoreFeatureViewRequest
    ) -> featurestore_v1_feature_view_validation_service_pb2.ScoreFeatureViewResponse:
        return await self.client.ScoreFeatureView(request, timeout=self.timeout)


async def entity_import_validate_entity_import1(
    client: notifications_v1_notification_validation_service_pb2_grpc.NotificationValidationServiceStub,
    request: notifications_v1_notification_validation_service_pb2.ScoreNotificationRequest,
    timeout: float
) -> notifications_v1_notification_validation_service_pb2.ScoreNotificationResponse:
    return await client.ScoreNotification(request, timeout=timeout)


class EntityLifecycleExpireEntity0Adapter:
    def __init__(
        self,
        client: featurestore_v1_feature_value_sync_service_pb2_grpc.FeatureValueSyncServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def __call__(
        self,
        request: featurestore_v1_feature_value_sync_service_pb2.ListFeatureValueConflictsRequest
    ) -> featurestore_v1_feature_value_sync_service_pb2.ListFeatureValueConflictsResponse:
        return await self.client.ListFeatureValueConflicts(request, timeout=self.timeout)


async def entity_reporting_delete_entity_report0(
    client: datasets_v1_dataset_service_pb2_grpc.DatasetServiceStub,
    request: datasets_v1_dataset_service_pb2.SearchDatasetsRequest,
    timeout: float
) -> datasets_v1_dataset_service_pb2.SearchDatasetsResponse:
    return await client.SearchDatasets(request, timeout=timeout)


class EntityReportingDeleteEntityReport2Port(Protocol):
    async def execute(
        self,
        request: featurestore_v1_feature_view_sync_service_pb2.ReconcileFeatureViewsRequest
    ) -> featurestore_v1_feature_view_sync_service_pb2.ReconcileFeatureViewsResponse: ...


class EntityReportingDeleteEntityReport2Adapter:
    def __init__(
        self,
        client: featurestore_v1_feature_view_sync_service_pb2_grpc.FeatureViewSyncServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def execute(
        self,
        request: featurestore_v1_feature_view_sync_service_pb2.ReconcileFeatureViewsRequest
    ) -> featurestore_v1_feature_view_sync_service_pb2.ReconcileFeatureViewsResponse:
        return await self.client.ReconcileFeatureViews(request, timeout=self.timeout)


async def entity_sync_push_entity0(
    client: datasets_v1_dataset_service_pb2_grpc.DatasetServiceStub,
    request: datasets_v1_dataset_service_pb2.UpdateDatasetRequest,
    timeout: float
) -> datasets_v1_dataset_service_pb2.UpdateDatasetResponse:
    return await client.UpdateDataset(request, timeout=timeout)


class EntitySyncReconcileEntities0Port(Protocol):
    async def execute(
        self,
        request: featurestore_v1_feature_view_reporting_service_pb2.ListFeatureViewReportsRequest
    ) -> featurestore_v1_feature_view_reporting_service_pb2.ListFeatureViewReportsResponse: ...


class EntitySyncReconcileEntities0Adapter:
    def __init__(
        self,
        client: featurestore_v1_feature_view_reporting_service_pb2_grpc.FeatureViewReportingServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def execute(
        self,
        request: featurestore_v1_feature_view_reporting_service_pb2.ListFeatureViewReportsRequest
    ) -> featurestore_v1_feature_view_reporting_service_pb2.ListFeatureViewReportsResponse:
        return await self.client.ListFeatureViewReports(request, timeout=self.timeout)


class EntitySyncStreamEntityChanges0Adapter:
    def __init__(
        self,
        client: featureflags_v1_feature_flag_service_pb2_grpc.FeatureFlagServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def __call__(
        self,
        request: featureflags_v1_feature_flag_service_pb2.BatchGetFeatureFlagsRequest
    ) -> featureflags_v1_feature_flag_service_pb2.BatchGetFeatureFlagsResponse:
        return await self.client.BatchGetFeatureFlags(request, timeout=self.timeout)


class EntityValidationNormalizeEntity0Port(Protocol):
    async def execute(
        self,
        request: metrics_v1_metric_series_export_service_pb2.RetryMetricSeriesExportRequest
    ) -> metrics_v1_metric_series_export_service_pb2.RetryMetricSeriesExportResponse: ...


class EntityValidationNormalizeEntity0Adapter:
    def __init__(
        self,
        client: metrics_v1_metric_series_export_service_pb2_grpc.MetricSeriesExportServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def execute(
        self,
        request: metrics_v1_metric_series_export_service_pb2.RetryMetricSeriesExportRequest
    ) -> metrics_v1_metric_series_export_service_pb2.RetryMetricSeriesExportResponse:
        return await self.client.RetryMetricSeriesExport(request, timeout=self.timeout)


class EntityValidationNormalizeEntity2Adapter:
    def __init__(
        self,
        client: metrics_v1_metric_series_history_service_pb2_grpc.MetricSeriesHistoryServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def __call__(
        self,
        request: metrics_v1_metric_series_history_service_pb2.RecordMetricSeriesVersionRequest
    ) -> metrics_v1_metric_series_history_service_pb2.RecordMetricSeriesVersionResponse:
        return await self.client.RecordMetricSeriesVersion(request, timeout=self.timeout)


class EntityWorkflowResumeEntityWorkflow1Port(Protocol):
    async def execute(
        self,
        request: featurestore_v1_feature_view_sync_service_pb2.ListFeatureViewConflictsRequest
    ) -> featurestore_v1_feature_view_sync_service_pb2.ListFeatureViewConflictsResponse: ...


class EntityWorkflowResumeEntityWorkflow1Adapter:
    def __init__(
        self,
        client: featurestore_v1_feature_view_sync_service_pb2_grpc.FeatureViewSyncServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def execute(
        self,
        request: featurestore_v1_feature_view_sync_service_pb2.ListFeatureViewConflictsRequest
    ) -> featurestore_v1_feature_view_sync_service_pb2.ListFeatureViewConflictsResponse:
        return await self.client.ListFeatureViewConflicts(request, timeout=self.timeout)


class EntityWorkflowResumeEntityWorkflow3Adapter:
    def __init__(
        self,
        client: featurestore_v1_feature_value_approval_service_pb2_grpc.FeatureValueApprovalServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def __call__(
        self,
        request: featurestore_v1_feature_value_approval_service_pb2.DelegateFeatureValueApprovalRequest
    ) -> featurestore_v1_feature_value_approval_service_pb2.DelegateFeatureValueApprovalResponse:
        return await self.client.DelegateFeatureValueApproval(request, timeout=self.timeout)


async def feature_value_approval_escalate_feature_value0(
    client: featurestore_v1_feature_view_sync_service_pb2_grpc.FeatureViewSyncServiceStub,
    request: featurestore_v1_feature_view_sync_service_pb2.ReconcileFeatureViewsRequest,
    timeout: float
) -> featurestore_v1_feature_view_sync_service_pb2.ReconcileFeatureViewsResponse:
    return await client.ReconcileFeatureViews(request, timeout=timeout)


class FeatureValueApprovalEscalateFeatureValue2Port(Protocol):
    async def execute(
        self,
        request: authorization_v1_access_policy_validation_service_pb2.ExplainAccessPolicyDecisionRequest
    ) -> authorization_v1_access_policy_validation_service_pb2.ExplainAccessPolicyDecisionResponse: ...


class FeatureValueApprovalEscalateFeatureValue2Adapter:
    def __init__(
        self,
        client: authorization_v1_access_policy_validation_service_pb2_grpc.AccessPolicyValidationServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def execute(
        self,
        request: authorization_v1_access_policy_validation_service_pb2.ExplainAccessPolicyDecisionRequest
    ) -> authorization_v1_access_policy_validation_service_pb2.ExplainAccessPolicyDecisionResponse:
        return await self.client.ExplainAccessPolicyDecision(request, timeout=self.timeout)


async def feature_value_calculation_estimate_feature_value1(
    client: metrics_v1_metric_series_history_service_pb2_grpc.MetricSeriesHistoryServiceStub,
    request: metrics_v1_metric_series_history_service_pb2.ListMetricSeriesVersionsRequest,
    timeout: float
) -> metrics_v1_metric_series_history_service_pb2.ListMetricSeriesVersionsResponse:
    return await client.ListMetricSeriesVersions(request, timeout=timeout)


class FeatureValueCalculationQuoteFeatureValue0Adapter:
    def __init__(
        self,
        client: featurestore_v1_feature_view_calculation_service_pb2_grpc.FeatureViewCalculationServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def __call__(
        self,
        request: featurestore_v1_feature_view_calculation_service_pb2.EstimateFeatureViewRequest
    ) -> featurestore_v1_feature_view_calculation_service_pb2.EstimateFeatureViewResponse:
        return await self.client.EstimateFeatureView(request, timeout=self.timeout)


async def feature_value_import_map_feature_value_import_columns1(
    client: datasets_v1_data_schema_validation_service_pb2_grpc.DataSchemaValidationServiceStub,
    request: datasets_v1_data_schema_validation_service_pb2.ValidateDataSchemaRequest,
    timeout: float
) -> datasets_v1_data_schema_validation_service_pb2.ValidateDataSchemaResponse:
    return await client.ValidateDataSchema(request, timeout=timeout)


class FeatureValueImportMapFeatureValueImportColumns3Port(Protocol):
    async def execute(
        self,
        request: datasets_v1_dataset_service_pb2.GetDatasetRequest
    ) -> datasets_v1_dataset_service_pb2.GetDatasetResponse: ...


class FeatureValueImportMapFeatureValueImportColumns3Adapter:
    def __init__(self, client: datasets_v1_dataset_service_pb2_grpc.DatasetServiceStub, timeout: float) -> None:
        self.client = client
        self.timeout = timeout

    async def execute(
        self,
        request: datasets_v1_dataset_service_pb2.GetDatasetRequest
    ) -> datasets_v1_dataset_service_pb2.GetDatasetResponse:
        return await self.client.GetDataset(request, timeout=self.timeout)


class FeatureValueImportRetryFeatureValueImport1Adapter:
    def __init__(
        self,
        client: anomalies_v1_anomaly_workflow_service_pb2_grpc.AnomalyWorkflowServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def __call__(
        self,
        request: anomalies_v1_anomaly_workflow_service_pb2.AdvanceAnomalyWorkflowRequest
    ) -> anomalies_v1_anomaly_workflow_service_pb2.AdvanceAnomalyWorkflowResponse:
        return await self.client.AdvanceAnomalyWorkflow(request, timeout=self.timeout)


async def feature_value_lifecycle_renew_feature_value1(
    client: lineage_v1_lineage_edge_sync_service_pb2_grpc.LineageEdgeSyncServiceStub,
    request: lineage_v1_lineage_edge_sync_service_pb2.ResolveLineageEdgeConflictRequest,
    timeout: float
) -> lineage_v1_lineage_edge_sync_service_pb2.ResolveLineageEdgeConflictResponse:
    return await client.ResolveLineageEdgeConflict(request, timeout=timeout)


async def feature_value_query_summarize_feature_values1(
    client: lineage_v1_impact_validation_service_pb2_grpc.ImpactValidationServiceStub,
    request: lineage_v1_impact_validation_service_pb2.ExplainImpactDecisionRequest,
    timeout: float
) -> lineage_v1_impact_validation_service_pb2.ExplainImpactDecisionResponse:
    return await client.ExplainImpactDecision(request, timeout=timeout)


class FeatureValueReportingGenerateFeatureValueReport1Adapter:
    def __init__(
        self,
        client: featurestore_v1_feature_view_query_service_pb2_grpc.FeatureViewQueryServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def __call__(
        self,
        request: featurestore_v1_feature_view_query_service_pb2.SummarizeFeatureViewsRequest
    ) -> featurestore_v1_feature_view_query_service_pb2.SummarizeFeatureViewsResponse:
        return await self.client.SummarizeFeatureViews(request, timeout=self.timeout)


async def feature_value_sync_push_feature_value0(
    client: datasets_v1_dataset_query_service_pb2_grpc.DatasetQueryServiceStub,
    request: datasets_v1_dataset_query_service_pb2.PeekDatasetRequest,
    timeout: float
) -> datasets_v1_dataset_query_service_pb2.PeekDatasetResponse:
    return await client.PeekDataset(request, timeout=timeout)


class FeatureValueSyncPushFeatureValue2Port(Protocol):
    async def execute(
        self,
        request: featurestore_v1_entity_calculation_service_pb2.QuoteEntityRequest
    ) -> featurestore_v1_entity_calculation_service_pb2.QuoteEntityResponse: ...


class FeatureValueSyncPushFeatureValue2Adapter:
    def __init__(
        self,
        client: featurestore_v1_entity_calculation_service_pb2_grpc.EntityCalculationServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def execute(
        self,
        request: featurestore_v1_entity_calculation_service_pb2.QuoteEntityRequest
    ) -> featurestore_v1_entity_calculation_service_pb2.QuoteEntityResponse:
        return await self.client.QuoteEntity(request, timeout=self.timeout)


class FeatureValueSyncReconcileFeatureValues0Adapter:
    def __init__(self, client: documents_v1_document_service_pb2_grpc.DocumentServiceStub, timeout: float) -> None:
        self.client = client
        self.timeout = timeout

    async def __call__(
        self,
        request: documents_v1_document_service_pb2.ListDocumentsRequest
    ) -> documents_v1_document_service_pb2.ListDocumentsResponse:
        return await self.client.ListDocuments(request, timeout=self.timeout)


class FeatureValueValidationNormalizeFeatureValue1Adapter:
    def __init__(
        self,
        client: anomalies_v1_anomaly_feedback_calculation_service_pb2_grpc.AnomalyFeedbackCalculationServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def __call__(
        self,
        request: anomalies_v1_anomaly_feedback_calculation_service_pb2.QuoteAnomalyFeedbackRequest
    ) -> anomalies_v1_anomaly_feedback_calculation_service_pb2.QuoteAnomalyFeedbackResponse:
        return await self.client.QuoteAnomalyFeedback(request, timeout=self.timeout)


async def feature_value_workflow_cancel_feature_value_workflow0(
    client: lineage_v1_lineage_edge_import_service_pb2_grpc.LineageEdgeImportServiceStub,
    request: lineage_v1_lineage_edge_import_service_pb2.MapLineageEdgeImportColumnsRequest,
    timeout: float
) -> lineage_v1_lineage_edge_import_service_pb2.MapLineageEdgeImportColumnsResponse:
    return await client.MapLineageEdgeImportColumns(request, timeout=timeout)


async def feature_view_approval_approve_feature_view1(
    client: datasets_v1_dataset_version_query_service_pb2_grpc.DatasetVersionQueryServiceStub,
    request: datasets_v1_dataset_version_query_service_pb2.SummarizeDatasetVersionsRequest,
    timeout: float
) -> datasets_v1_dataset_version_query_service_pb2.SummarizeDatasetVersionsResponse:
    return await client.SummarizeDatasetVersions(request, timeout=timeout)


class FeatureViewApprovalCommentFeatureViewApproval1Port(Protocol):
    async def execute(
        self,
        request: identity_v1_user_validation_service_pb2.NormalizeUserRequest
    ) -> identity_v1_user_validation_service_pb2.NormalizeUserResponse: ...


class FeatureViewApprovalCommentFeatureViewApproval1Adapter:
    def __init__(
        self,
        client: identity_v1_user_validation_service_pb2_grpc.UserValidationServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def execute(
        self,
        request: identity_v1_user_validation_service_pb2.NormalizeUserRequest
    ) -> identity_v1_user_validation_service_pb2.NormalizeUserResponse:
        return await self.client.NormalizeUser(request, timeout=self.timeout)


class FeatureViewCalculationCalculateFeatureView0Port(Protocol):
    async def execute(
        self,
        request: certificates_v1_certificate_calculation_service_pb2.CompareCertificateOptionsRequest
    ) -> certificates_v1_certificate_calculation_service_pb2.CompareCertificateOptionsResponse: ...


class FeatureViewCalculationCalculateFeatureView0Adapter:
    def __init__(
        self,
        client: certificates_v1_certificate_calculation_service_pb2_grpc.CertificateCalculationServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def execute(
        self,
        request: certificates_v1_certificate_calculation_service_pb2.CompareCertificateOptionsRequest
    ) -> certificates_v1_certificate_calculation_service_pb2.CompareCertificateOptionsResponse:
        return await self.client.CompareCertificateOptions(request, timeout=self.timeout)


async def feature_view_calculation_simulate_feature_view0(
    client: identity_v1_user_validation_service_pb2_grpc.UserValidationServiceStub,
    request: identity_v1_user_validation_service_pb2.GetUserRulesRequest,
    timeout: float
) -> identity_v1_user_validation_service_pb2.GetUserRulesResponse:
    return await client.GetUserRules(request, timeout=timeout)


class FeatureViewLifecycleActivateFeatureView0Port(Protocol):
    async def execute(
        self,
        request: featurestore_v1_feature_view_service_pb2.GetFeatureViewRequest
    ) -> featurestore_v1_feature_view_service_pb2.GetFeatureViewResponse: ...


class FeatureViewLifecycleActivateFeatureView0Adapter:
    def __init__(
        self,
        client: featurestore_v1_feature_view_service_pb2_grpc.FeatureViewServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def execute(
        self,
        request: featurestore_v1_feature_view_service_pb2.GetFeatureViewRequest
    ) -> featurestore_v1_feature_view_service_pb2.GetFeatureViewResponse:
        return await self.client.GetFeatureView(request, timeout=self.timeout)


class FeatureViewLifecycleExpireFeatureView0Adapter:
    def __init__(
        self,
        client: featurestore_v1_feature_view_service_pb2_grpc.FeatureViewServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def __call__(
        self,
        request: featurestore_v1_feature_view_service_pb2.BatchGetFeatureViewsRequest
    ) -> featurestore_v1_feature_view_service_pb2.BatchGetFeatureViewsResponse:
        return await self.client.BatchGetFeatureViews(request, timeout=self.timeout)


async def feature_view_lifecycle_suspend_feature_view0(
    client: featurestore_v1_feature_value_import_service_pb2_grpc.FeatureValueImportServiceStub,
    request: featurestore_v1_feature_value_import_service_pb2.ValidateFeatureValueImportRequest,
    timeout: float
) -> featurestore_v1_feature_value_import_service_pb2.ValidateFeatureValueImportResponse:
    return await client.ValidateFeatureValueImport(request, timeout=timeout)


class FeatureViewLifecycleTerminateFeatureView1Port(Protocol):
    async def execute(
        self,
        request: datasets_v1_data_schema_validation_service_pb2.CheckDataSchemaEligibilityRequest
    ) -> datasets_v1_data_schema_validation_service_pb2.CheckDataSchemaEligibilityResponse: ...


class FeatureViewLifecycleTerminateFeatureView1Adapter:
    def __init__(
        self,
        client: datasets_v1_data_schema_validation_service_pb2_grpc.DataSchemaValidationServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def execute(
        self,
        request: datasets_v1_data_schema_validation_service_pb2.CheckDataSchemaEligibilityRequest
    ) -> datasets_v1_data_schema_validation_service_pb2.CheckDataSchemaEligibilityResponse:
        return await self.client.CheckDataSchemaEligibility(request, timeout=self.timeout)


class FeatureViewQueryBrowseFeatureViews1Adapter:
    def __init__(
        self,
        client: featurestore_v1_entity_calculation_service_pb2_grpc.EntityCalculationServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def __call__(
        self,
        request: featurestore_v1_entity_calculation_service_pb2.ExplainEntityCalculationRequest
    ) -> featurestore_v1_entity_calculation_service_pb2.ExplainEntityCalculationResponse:
        return await self.client.ExplainEntityCalculation(request, timeout=self.timeout)


class FeatureViewReportingScheduleFeatureViewReport1Port(Protocol):
    async def execute(
        self,
        request: featurestore_v1_feature_view_validation_service_pb2.ScoreFeatureViewRequest
    ) -> featurestore_v1_feature_view_validation_service_pb2.ScoreFeatureViewResponse: ...


class FeatureViewReportingScheduleFeatureViewReport1Adapter:
    def __init__(
        self,
        client: featurestore_v1_feature_view_validation_service_pb2_grpc.FeatureViewValidationServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def execute(
        self,
        request: featurestore_v1_feature_view_validation_service_pb2.ScoreFeatureViewRequest
    ) -> featurestore_v1_feature_view_validation_service_pb2.ScoreFeatureViewResponse:
        return await self.client.ScoreFeatureView(request, timeout=self.timeout)


async def feature_view_create_feature_view1(
    client: featurestore_v1_feature_view_query_service_pb2_grpc.FeatureViewQueryServiceStub,
    request: featurestore_v1_feature_view_query_service_pb2.BrowseFeatureViewsRequest,
    timeout: float
) -> featurestore_v1_feature_view_query_service_pb2.BrowseFeatureViewsResponse:
    return await client.BrowseFeatureViews(request, timeout=timeout)


class FeatureViewDeleteFeatureView1Port(Protocol):
    async def execute(
        self,
        request: documents_v1_document_service_pb2.ListDocumentsRequest
    ) -> documents_v1_document_service_pb2.ListDocumentsResponse: ...


class FeatureViewDeleteFeatureView1Adapter:
    def __init__(self, client: documents_v1_document_service_pb2_grpc.DocumentServiceStub, timeout: float) -> None:
        self.client = client
        self.timeout = timeout

    async def execute(
        self,
        request: documents_v1_document_service_pb2.ListDocumentsRequest
    ) -> documents_v1_document_service_pb2.ListDocumentsResponse:
        return await self.client.ListDocuments(request, timeout=self.timeout)


async def feature_view_sync_push_feature_view2(
    client: datasets_v1_dataset_service_pb2_grpc.DatasetServiceStub,
    request: datasets_v1_dataset_service_pb2.BatchGetDatasetsRequest,
    timeout: float
) -> datasets_v1_dataset_service_pb2.BatchGetDatasetsResponse:
    return await client.BatchGetDatasets(request, timeout=timeout)


class FeatureViewSyncSyncFeatureViews0Adapter:
    def __init__(
        self,
        client: featurestore_v1_entity_validation_service_pb2_grpc.EntityValidationServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def __call__(
        self,
        request: featurestore_v1_entity_validation_service_pb2.ExplainEntityDecisionRequest
    ) -> featurestore_v1_entity_validation_service_pb2.ExplainEntityDecisionResponse:
        return await self.client.ExplainEntityDecision(request, timeout=self.timeout)


async def feature_view_validation_validate_feature_view0(
    client: featurestore_v1_feature_value_calculation_service_pb2_grpc.FeatureValueCalculationServiceStub,
    request: featurestore_v1_feature_value_calculation_service_pb2.QuoteFeatureValueRequest,
    timeout: float
) -> featurestore_v1_feature_value_calculation_service_pb2.QuoteFeatureValueResponse:
    return await client.QuoteFeatureValue(request, timeout=timeout)


class FeatureViewValidationValidateFeatureView2Port(Protocol):
    async def execute(
        self,
        request: documents_v1_document_validation_service_pb2.ValidateDocumentRequest
    ) -> documents_v1_document_validation_service_pb2.ValidateDocumentResponse: ...


class FeatureViewValidationValidateFeatureView2Adapter:
    def __init__(
        self,
        client: documents_v1_document_validation_service_pb2_grpc.DocumentValidationServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def execute(
        self,
        request: documents_v1_document_validation_service_pb2.ValidateDocumentRequest
    ) -> documents_v1_document_validation_service_pb2.ValidateDocumentResponse:
        return await self.client.ValidateDocument(request, timeout=self.timeout)


class FeatureViewWorkflowStartFeatureViewWorkflow1Port(Protocol):
    async def execute(
        self,
        request: featurestore_v1_feature_value_approval_service_pb2.RejectFeatureValueRequest
    ) -> featurestore_v1_feature_value_approval_service_pb2.RejectFeatureValueResponse: ...


class FeatureViewWorkflowStartFeatureViewWorkflow1Adapter:
    def __init__(
        self,
        client: featurestore_v1_feature_value_approval_service_pb2_grpc.FeatureValueApprovalServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def execute(
        self,
        request: featurestore_v1_feature_value_approval_service_pb2.RejectFeatureValueRequest
    ) -> featurestore_v1_feature_value_approval_service_pb2.RejectFeatureValueResponse:
        return await self.client.RejectFeatureValue(request, timeout=self.timeout)


class FeatureViewWorkflowStartFeatureViewWorkflow3Adapter:
    def __init__(
        self,
        client: featurestore_v1_entity_sync_service_pb2_grpc.EntitySyncServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def __call__(
        self,
        request: featurestore_v1_entity_sync_service_pb2.PushEntityRequest
    ) -> featurestore_v1_entity_sync_service_pb2.PushEntityResponse:
        return await self.client.PushEntity(request, timeout=self.timeout)
