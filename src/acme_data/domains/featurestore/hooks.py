"""Replaceable partner hooks of the featurestore domain."""

from __future__ import annotations

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
from acme.featurestore.v1 import feature_view_query_service_pb2 as featurestore_v1_feature_view_query_service_pb2
from acme.featurestore.v1 import (
    feature_view_query_service_pb2_grpc as featurestore_v1_feature_view_query_service_pb2_grpc,
)
from acme.featurestore.v1 import feature_view_sync_service_pb2 as featurestore_v1_feature_view_sync_service_pb2
from acme.featurestore.v1 import (
    feature_view_sync_service_pb2_grpc as featurestore_v1_feature_view_sync_service_pb2_grpc,
)
from acme.identity.v1 import user_validation_service_pb2 as identity_v1_user_validation_service_pb2
from acme.identity.v1 import user_validation_service_pb2_grpc as identity_v1_user_validation_service_pb2_grpc
from acme.lineage.v1 import impact_validation_service_pb2 as lineage_v1_impact_validation_service_pb2
from acme.lineage.v1 import impact_validation_service_pb2_grpc as lineage_v1_impact_validation_service_pb2_grpc
from acme.lineage.v1 import lineage_edge_import_service_pb2 as lineage_v1_lineage_edge_import_service_pb2
from acme.lineage.v1 import lineage_edge_import_service_pb2_grpc as lineage_v1_lineage_edge_import_service_pb2_grpc
from acme.lineage.v1 import lineage_edge_sync_service_pb2 as lineage_v1_lineage_edge_sync_service_pb2
from acme.lineage.v1 import lineage_edge_sync_service_pb2_grpc as lineage_v1_lineage_edge_sync_service_pb2_grpc
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
    raise RuntimeError("domain hook was not installed")


async def entity_import_validate_entity_import1(
    client: notifications_v1_notification_validation_service_pb2_grpc.NotificationValidationServiceStub,
    request: notifications_v1_notification_validation_service_pb2.ScoreNotificationRequest,
    timeout: float
) -> notifications_v1_notification_validation_service_pb2.ScoreNotificationResponse:
    raise RuntimeError("domain hook was not installed")


async def entity_reporting_delete_entity_report0(
    client: datasets_v1_dataset_service_pb2_grpc.DatasetServiceStub,
    request: datasets_v1_dataset_service_pb2.SearchDatasetsRequest,
    timeout: float
) -> datasets_v1_dataset_service_pb2.SearchDatasetsResponse:
    raise RuntimeError("domain hook was not installed")


async def entity_sync_push_entity0(
    client: datasets_v1_dataset_service_pb2_grpc.DatasetServiceStub,
    request: datasets_v1_dataset_service_pb2.UpdateDatasetRequest,
    timeout: float
) -> datasets_v1_dataset_service_pb2.UpdateDatasetResponse:
    raise RuntimeError("domain hook was not installed")


async def feature_value_approval_escalate_feature_value0(
    client: featurestore_v1_feature_view_sync_service_pb2_grpc.FeatureViewSyncServiceStub,
    request: featurestore_v1_feature_view_sync_service_pb2.ReconcileFeatureViewsRequest,
    timeout: float
) -> featurestore_v1_feature_view_sync_service_pb2.ReconcileFeatureViewsResponse:
    raise RuntimeError("domain hook was not installed")


async def feature_value_calculation_estimate_feature_value1(
    client: metrics_v1_metric_series_history_service_pb2_grpc.MetricSeriesHistoryServiceStub,
    request: metrics_v1_metric_series_history_service_pb2.ListMetricSeriesVersionsRequest,
    timeout: float
) -> metrics_v1_metric_series_history_service_pb2.ListMetricSeriesVersionsResponse:
    raise RuntimeError("domain hook was not installed")


async def feature_value_import_map_feature_value_import_columns1(
    client: datasets_v1_data_schema_validation_service_pb2_grpc.DataSchemaValidationServiceStub,
    request: datasets_v1_data_schema_validation_service_pb2.ValidateDataSchemaRequest,
    timeout: float
) -> datasets_v1_data_schema_validation_service_pb2.ValidateDataSchemaResponse:
    raise RuntimeError("domain hook was not installed")


async def feature_value_lifecycle_renew_feature_value1(
    client: lineage_v1_lineage_edge_sync_service_pb2_grpc.LineageEdgeSyncServiceStub,
    request: lineage_v1_lineage_edge_sync_service_pb2.ResolveLineageEdgeConflictRequest,
    timeout: float
) -> lineage_v1_lineage_edge_sync_service_pb2.ResolveLineageEdgeConflictResponse:
    raise RuntimeError("domain hook was not installed")


async def feature_value_query_summarize_feature_values1(
    client: lineage_v1_impact_validation_service_pb2_grpc.ImpactValidationServiceStub,
    request: lineage_v1_impact_validation_service_pb2.ExplainImpactDecisionRequest,
    timeout: float
) -> lineage_v1_impact_validation_service_pb2.ExplainImpactDecisionResponse:
    raise RuntimeError("domain hook was not installed")


async def feature_value_sync_push_feature_value0(
    client: datasets_v1_dataset_query_service_pb2_grpc.DatasetQueryServiceStub,
    request: datasets_v1_dataset_query_service_pb2.PeekDatasetRequest,
    timeout: float
) -> datasets_v1_dataset_query_service_pb2.PeekDatasetResponse:
    raise RuntimeError("domain hook was not installed")


async def feature_value_workflow_cancel_feature_value_workflow0(
    client: lineage_v1_lineage_edge_import_service_pb2_grpc.LineageEdgeImportServiceStub,
    request: lineage_v1_lineage_edge_import_service_pb2.MapLineageEdgeImportColumnsRequest,
    timeout: float
) -> lineage_v1_lineage_edge_import_service_pb2.MapLineageEdgeImportColumnsResponse:
    raise RuntimeError("domain hook was not installed")


async def feature_view_approval_approve_feature_view1(
    client: datasets_v1_dataset_version_query_service_pb2_grpc.DatasetVersionQueryServiceStub,
    request: datasets_v1_dataset_version_query_service_pb2.SummarizeDatasetVersionsRequest,
    timeout: float
) -> datasets_v1_dataset_version_query_service_pb2.SummarizeDatasetVersionsResponse:
    raise RuntimeError("domain hook was not installed")


async def feature_view_calculation_simulate_feature_view0(
    client: identity_v1_user_validation_service_pb2_grpc.UserValidationServiceStub,
    request: identity_v1_user_validation_service_pb2.GetUserRulesRequest,
    timeout: float
) -> identity_v1_user_validation_service_pb2.GetUserRulesResponse:
    raise RuntimeError("domain hook was not installed")


async def feature_view_lifecycle_suspend_feature_view0(
    client: featurestore_v1_feature_value_import_service_pb2_grpc.FeatureValueImportServiceStub,
    request: featurestore_v1_feature_value_import_service_pb2.ValidateFeatureValueImportRequest,
    timeout: float
) -> featurestore_v1_feature_value_import_service_pb2.ValidateFeatureValueImportResponse:
    raise RuntimeError("domain hook was not installed")


async def feature_view_create_feature_view1(
    client: featurestore_v1_feature_view_query_service_pb2_grpc.FeatureViewQueryServiceStub,
    request: featurestore_v1_feature_view_query_service_pb2.BrowseFeatureViewsRequest,
    timeout: float
) -> featurestore_v1_feature_view_query_service_pb2.BrowseFeatureViewsResponse:
    raise RuntimeError("domain hook was not installed")


async def feature_view_sync_push_feature_view2(
    client: datasets_v1_dataset_service_pb2_grpc.DatasetServiceStub,
    request: datasets_v1_dataset_service_pb2.BatchGetDatasetsRequest,
    timeout: float
) -> datasets_v1_dataset_service_pb2.BatchGetDatasetsResponse:
    raise RuntimeError("domain hook was not installed")


async def feature_view_validation_validate_feature_view0(
    client: featurestore_v1_feature_value_calculation_service_pb2_grpc.FeatureValueCalculationServiceStub,
    request: featurestore_v1_feature_value_calculation_service_pb2.QuoteFeatureValueRequest,
    timeout: float
) -> featurestore_v1_feature_value_calculation_service_pb2.QuoteFeatureValueResponse:
    raise RuntimeError("domain hook was not installed")
