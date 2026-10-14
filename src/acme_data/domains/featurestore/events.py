"""Background event handlers owned by the featurestore team."""

from __future__ import annotations

from functools import partial
from typing import cast

from google.protobuf.message import Message

from acme.anomalies.v1 import detector_workflow_service_pb2 as anomalies_v1_detector_workflow_service_pb2
from acme.datasets.v1 import data_schema_calculation_service_pb2 as datasets_v1_data_schema_calculation_service_pb2
from acme.datasets.v1 import dataset_service_pb2 as datasets_v1_dataset_service_pb2
from acme.documents.v1 import document_service_pb2 as documents_v1_document_service_pb2
from acme.documents.v1 import document_validation_service_pb2 as documents_v1_document_validation_service_pb2
from acme.featurestore.v1 import entity_sync_service_pb2 as featurestore_v1_entity_sync_service_pb2
from acme.featurestore.v1 import (
    feature_value_calculation_service_pb2 as featurestore_v1_feature_value_calculation_service_pb2,
)
from acme.featurestore.v1 import feature_value_import_service_pb2 as featurestore_v1_feature_value_import_service_pb2
from acme.featurestore.v1 import feature_view_sync_service_pb2 as featurestore_v1_feature_view_sync_service_pb2
from acme.featurestore.v1 import (
    feature_view_validation_service_pb2 as featurestore_v1_feature_view_validation_service_pb2,
)
from acme.lineage.v1 import lineage_edge_workflow_service_pb2 as lineage_v1_lineage_edge_workflow_service_pb2
from acme.lineage.v1 import lineage_node_query_service_pb2 as lineage_v1_lineage_node_query_service_pb2
from acme.merchandising.v1 import collection_query_service_pb2 as merchandising_v1_collection_query_service_pb2
from acme.metrics.v1 import dashboard_validation_service_pb2 as metrics_v1_dashboard_validation_service_pb2

from acme_data.domains.featurestore.dependencies import Dependencies


async def on_entity_approval_service_reject_entity_0(deps: Dependencies, payload: Message) -> Message:
    request = cast(datasets_v1_dataset_service_pb2.BatchGetDatasetsRequest, payload)
    return await deps.clients.datasets_dataset.BatchGetDatasets(request, timeout=deps.settings.timeout)


async def on_entity_calculation_service_quote_entity_0(deps: Dependencies, payload: Message) -> Message:
    request = cast(featurestore_v1_feature_view_validation_service_pb2.ValidateFeatureViewRequest, payload)
    return await deps.clients.featurestore_feature_view_validation.ValidateFeatureView(
        request,
        timeout=deps.settings.timeout
    )


async def on_entity_reporting_service_generate_entity_report_0(deps: Dependencies, payload: Message) -> Message:
    request = cast(datasets_v1_data_schema_calculation_service_pb2.RecalculateDataSchemasRequest, payload)
    return await deps.clients.datasets_data_schema_calculation.RecalculateDataSchemas(
        request,
        timeout=deps.settings.timeout
    )


async def on_entity_sync_service_stream_entity_changes_1(deps: Dependencies, payload: Message) -> Message:
    request = cast(documents_v1_document_service_pb2.ListDocumentsRequest, payload)
    return await deps.clients.documents_document.ListDocuments(request, timeout=deps.settings.timeout)


async def on_entity_validation_service_preview_entity_0(deps: Dependencies, payload: Message) -> Message:
    request = cast(featurestore_v1_feature_view_validation_service_pb2.ValidateFeatureViewRequest, payload)
    return await deps.clients.featurestore_feature_view_validation.ValidateFeatureView(
        request,
        timeout=deps.settings.timeout
    )


async def on_feature_value_approval_service_get_feature_value_approval_status_1(
    deps: Dependencies,
    payload: Message
) -> Message:
    request = cast(anomalies_v1_detector_workflow_service_pb2.ListDetectorWorkflowsRequest, payload)
    return await deps.clients.anomalies_detector_workflow.ListDetectorWorkflows(request, timeout=deps.settings.timeout)


async def on_feature_value_import_service_retry_feature_value_import_2(deps: Dependencies, payload: Message) -> Message:
    request = cast(documents_v1_document_validation_service_pb2.NormalizeDocumentRequest, payload)
    return await deps.clients.documents_document_validation.NormalizeDocument(request, timeout=deps.settings.timeout)


async def on_feature_value_lifecycle_service_terminate_feature_value_1(deps: Dependencies, payload: Message) -> Message:
    request = cast(lineage_v1_lineage_edge_workflow_service_pb2.StartLineageEdgeWorkflowRequest, payload)
    return await deps.clients.lineage_lineage_edge_workflow.StartLineageEdgeWorkflow(
        request,
        timeout=deps.settings.timeout
    )


async def on_feature_value_reporting_service_generate_feature_value_report_2(
    deps: Dependencies,
    payload: Message
) -> Message:
    request = cast(featurestore_v1_entity_sync_service_pb2.ReconcileEntitiesRequest, payload)
    return await deps.clients.featurestore_entity_sync.ReconcileEntities(request, timeout=deps.settings.timeout)


async def on_feature_value_sync_service_reconcile_feature_values_1(deps: Dependencies, payload: Message) -> Message:
    request = cast(merchandising_v1_collection_query_service_pb2.BrowseCollectionsRequest, payload)
    return await deps.clients.merchandising_collection_query.BrowseCollections(request, timeout=deps.settings.timeout)


async def on_feature_value_validation_service_normalize_feature_value_2(
    deps: Dependencies,
    payload: Message
) -> Message:
    request = cast(featurestore_v1_feature_value_calculation_service_pb2.SimulateFeatureValueRequest, payload)
    return await deps.clients.featurestore_feature_value_calculation.SimulateFeatureValue(
        request,
        timeout=deps.settings.timeout
    )


async def on_feature_view_approval_service_delegate_feature_view_approval_1(
    deps: Dependencies,
    payload: Message
) -> Message:
    request = cast(featurestore_v1_feature_view_sync_service_pb2.GetFeatureViewSyncStateRequest, payload)
    return await deps.clients.featurestore_feature_view_sync.GetFeatureViewSyncState(
        request,
        timeout=deps.settings.timeout
    )


async def on_feature_view_calculation_service_compare_feature_view_options_0(
    deps: Dependencies,
    payload: Message
) -> Message:
    request = cast(lineage_v1_lineage_node_query_service_pb2.CountLineageNodesRequest, payload)
    return await deps.clients.lineage_lineage_node_query.CountLineageNodes(request, timeout=deps.settings.timeout)


async def on_feature_view_lifecycle_service_expire_feature_view_1(deps: Dependencies, payload: Message) -> Message:
    request = cast(featurestore_v1_feature_view_sync_service_pb2.GetFeatureViewSyncStateRequest, payload)
    return await deps.clients.featurestore_feature_view_sync.GetFeatureViewSyncState(
        request,
        timeout=deps.settings.timeout
    )


async def on_feature_view_reporting_service_share_feature_view_report_0(
    deps: Dependencies,
    payload: Message
) -> Message:
    request = cast(featurestore_v1_feature_view_sync_service_pb2.ReconcileFeatureViewsRequest, payload)
    return await deps.clients.featurestore_feature_view_sync.ReconcileFeatureViews(
        request,
        timeout=deps.settings.timeout
    )


async def on_feature_view_sync_service_sync_feature_views_1(deps: Dependencies, payload: Message) -> Message:
    request = cast(featurestore_v1_feature_value_import_service_pb2.RetryFeatureValueImportRequest, payload)
    return await deps.clients.featurestore_feature_value_import.RetryFeatureValueImport(
        request,
        timeout=deps.settings.timeout
    )


async def on_feature_view_workflow_service_cancel_feature_view_workflow_0(
    deps: Dependencies,
    payload: Message
) -> Message:
    request = cast(metrics_v1_dashboard_validation_service_pb2.ScoreDashboardRequest, payload)
    return await deps.clients.metrics_dashboard_validation.ScoreDashboard(request, timeout=deps.settings.timeout)


def subscribe(deps: Dependencies) -> None:
    deps.bus.subscribe(
        'acme.featurestore.v1.EntityApprovalService/RejectEntity/0',
        partial(on_entity_approval_service_reject_entity_0, deps)
    )
    deps.bus.subscribe(
        'acme.featurestore.v1.EntityCalculationService/QuoteEntity/0',
        partial(on_entity_calculation_service_quote_entity_0, deps)
    )
    deps.bus.subscribe(
        'acme.featurestore.v1.EntityReportingService/GenerateEntityReport/0',
        partial(on_entity_reporting_service_generate_entity_report_0, deps)
    )
    deps.bus.subscribe(
        'acme.featurestore.v1.EntitySyncService/StreamEntityChanges/1',
        partial(on_entity_sync_service_stream_entity_changes_1, deps)
    )
    deps.bus.subscribe(
        'acme.featurestore.v1.EntityValidationService/PreviewEntity/0',
        partial(on_entity_validation_service_preview_entity_0, deps)
    )
    deps.bus.subscribe(
        'acme.featurestore.v1.FeatureValueApprovalService/GetFeatureValueApprovalStatus/1',
        partial(on_feature_value_approval_service_get_feature_value_approval_status_1, deps)
    )
    deps.bus.subscribe(
        'acme.featurestore.v1.FeatureValueImportService/RetryFeatureValueImport/2',
        partial(on_feature_value_import_service_retry_feature_value_import_2, deps)
    )
    deps.bus.subscribe(
        'acme.featurestore.v1.FeatureValueLifecycleService/TerminateFeatureValue/1',
        partial(on_feature_value_lifecycle_service_terminate_feature_value_1, deps)
    )
    deps.bus.subscribe(
        'acme.featurestore.v1.FeatureValueReportingService/GenerateFeatureValueReport/2',
        partial(on_feature_value_reporting_service_generate_feature_value_report_2, deps)
    )
    deps.bus.subscribe(
        'acme.featurestore.v1.FeatureValueSyncService/ReconcileFeatureValues/1',
        partial(on_feature_value_sync_service_reconcile_feature_values_1, deps)
    )
    deps.bus.subscribe(
        'acme.featurestore.v1.FeatureValueValidationService/NormalizeFeatureValue/2',
        partial(on_feature_value_validation_service_normalize_feature_value_2, deps)
    )
    deps.bus.subscribe(
        'acme.featurestore.v1.FeatureViewApprovalService/DelegateFeatureViewApproval/1',
        partial(on_feature_view_approval_service_delegate_feature_view_approval_1, deps)
    )
    deps.bus.subscribe(
        'acme.featurestore.v1.FeatureViewCalculationService/CompareFeatureViewOptions/0',
        partial(on_feature_view_calculation_service_compare_feature_view_options_0, deps)
    )
    deps.bus.subscribe(
        'acme.featurestore.v1.FeatureViewLifecycleService/ExpireFeatureView/1',
        partial(on_feature_view_lifecycle_service_expire_feature_view_1, deps)
    )
    deps.bus.subscribe(
        'acme.featurestore.v1.FeatureViewReportingService/ShareFeatureViewReport/0',
        partial(on_feature_view_reporting_service_share_feature_view_report_0, deps)
    )
    deps.bus.subscribe(
        'acme.featurestore.v1.FeatureViewSyncService/SyncFeatureViews/1',
        partial(on_feature_view_sync_service_sync_feature_views_1, deps)
    )
    deps.bus.subscribe(
        'acme.featurestore.v1.FeatureViewWorkflowService/CancelFeatureViewWorkflow/0',
        partial(on_feature_view_workflow_service_cancel_feature_view_workflow_0, deps)
    )
