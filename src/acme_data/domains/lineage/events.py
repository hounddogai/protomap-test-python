"""Background event handlers owned by the lineage team."""

from __future__ import annotations

from functools import partial
from typing import cast

from google.protobuf.message import Message

from acme.customers.v1 import (
    customer_segment_validation_service_pb2 as customers_v1_customer_segment_validation_service_pb2,
)
from acme.featureflags.v1 import (
    feature_flag_validation_service_pb2 as featureflags_v1_feature_flag_validation_service_pb2,
)
from acme.featurestore.v1 import (
    feature_value_calculation_service_pb2 as featurestore_v1_feature_value_calculation_service_pb2,
)
from acme.labeling.v1 import labeling_task_validation_service_pb2 as labeling_v1_labeling_task_validation_service_pb2
from acme.lineage.v1 import impact_reporting_service_pb2 as lineage_v1_impact_reporting_service_pb2
from acme.lineage.v1 import impact_validation_service_pb2 as lineage_v1_impact_validation_service_pb2
from acme.lineage.v1 import lineage_edge_calculation_service_pb2 as lineage_v1_lineage_edge_calculation_service_pb2
from acme.lineage.v1 import lineage_edge_validation_service_pb2 as lineage_v1_lineage_edge_validation_service_pb2
from acme.lineage.v1 import lineage_node_approval_service_pb2 as lineage_v1_lineage_node_approval_service_pb2
from acme.lineage.v1 import lineage_node_calculation_service_pb2 as lineage_v1_lineage_node_calculation_service_pb2
from acme.lineage.v1 import lineage_node_reporting_service_pb2 as lineage_v1_lineage_node_reporting_service_pb2
from acme.metrics.v1 import metric_alert_history_service_pb2 as metrics_v1_metric_alert_history_service_pb2
from acme.search.v1 import search_index_query_service_pb2 as search_v1_search_index_query_service_pb2

from acme_data.domains.lineage.dependencies import Dependencies


async def on_impact_calculation_service_compare_impact_options_2(deps: Dependencies, payload: Message) -> Message:
    request = cast(search_v1_search_index_query_service_pb2.BrowseSearchIndexesRequest, payload)
    return await deps.clients.search_search_index_query.BrowseSearchIndexes(request, timeout=deps.settings.timeout)


async def on_impact_import_service_get_impact_import_status_1(deps: Dependencies, payload: Message) -> Message:
    request = cast(lineage_v1_impact_validation_service_pb2.LintImpactsRequest, payload)
    return await deps.clients.lineage_impact_validation.LintImpacts(request, timeout=deps.settings.timeout)


async def on_impact_sync_service_pull_impacts_0(deps: Dependencies, payload: Message) -> Message:
    request = cast(lineage_v1_lineage_node_reporting_service_pb2.ScheduleLineageNodeReportRequest, payload)
    return await deps.clients.lineage_lineage_node_reporting.ScheduleLineageNodeReport(
        request,
        timeout=deps.settings.timeout
    )


async def on_impact_sync_service_sync_impacts_2(deps: Dependencies, payload: Message) -> Message:
    request = cast(lineage_v1_lineage_edge_validation_service_pb2.ValidateLineageEdgeRequest, payload)
    return await deps.clients.lineage_lineage_edge_validation.ValidateLineageEdge(
        request,
        timeout=deps.settings.timeout
    )


async def on_impact_validation_service_preview_impact_1(deps: Dependencies, payload: Message) -> Message:
    request = cast(lineage_v1_lineage_node_calculation_service_pb2.CalculateLineageNodeRequest, payload)
    return await deps.clients.lineage_lineage_node_calculation.CalculateLineageNode(
        request,
        timeout=deps.settings.timeout
    )


async def on_lineage_edge_approval_service_recall_lineage_edge_0(deps: Dependencies, payload: Message) -> Message:
    request = cast(lineage_v1_impact_reporting_service_pb2.ListImpactReportsRequest, payload)
    return await deps.clients.lineage_impact_reporting.ListImpactReports(request, timeout=deps.settings.timeout)


async def on_lineage_edge_calculation_service_explain_lineage_edge_calculation_1(
    deps: Dependencies,
    payload: Message
) -> Message:
    request = cast(lineage_v1_lineage_node_calculation_service_pb2.SimulateLineageNodeRequest, payload)
    return await deps.clients.lineage_lineage_node_calculation.SimulateLineageNode(
        request,
        timeout=deps.settings.timeout
    )


async def on_lineage_edge_import_service_retry_lineage_edge_import_0(deps: Dependencies, payload: Message) -> Message:
    request = cast(featurestore_v1_feature_value_calculation_service_pb2.RecalculateFeatureValuesRequest, payload)
    return await deps.clients.featurestore_feature_value_calculation.RecalculateFeatureValues(
        request,
        timeout=deps.settings.timeout
    )


async def on_lineage_edge_query_service_summarize_lineage_edges_3(deps: Dependencies, payload: Message) -> Message:
    request = cast(metrics_v1_metric_alert_history_service_pb2.RevertMetricAlertRequest, payload)
    return await deps.clients.metrics_metric_alert_history.RevertMetricAlert(request, timeout=deps.settings.timeout)


async def on_lineage_edge_sync_service_reconcile_lineage_edges_0(deps: Dependencies, payload: Message) -> Message:
    request = cast(featureflags_v1_feature_flag_validation_service_pb2.PreviewFeatureFlagRequest, payload)
    return await deps.clients.featureflags_feature_flag_validation.PreviewFeatureFlag(
        request,
        timeout=deps.settings.timeout
    )


async def on_lineage_edge_workflow_service_resume_lineage_edge_workflow_1(
    deps: Dependencies,
    payload: Message
) -> Message:
    request = cast(customers_v1_customer_segment_validation_service_pb2.ExplainCustomerSegmentDecisionRequest, payload)
    return await deps.clients.customers_customer_segment_validation.ExplainCustomerSegmentDecision(
        request,
        timeout=deps.settings.timeout
    )


async def on_lineage_node_lifecycle_service_reinstate_lineage_node_0(deps: Dependencies, payload: Message) -> Message:
    request = cast(labeling_v1_labeling_task_validation_service_pb2.ValidateLabelingTaskRequest, payload)
    return await deps.clients.labeling_labeling_task_validation.ValidateLabelingTask(
        request,
        timeout=deps.settings.timeout
    )


async def on_lineage_node_sync_service_pull_lineage_nodes_0(deps: Dependencies, payload: Message) -> Message:
    request = cast(customers_v1_customer_segment_validation_service_pb2.CheckCustomerSegmentEligibilityRequest, payload)
    return await deps.clients.customers_customer_segment_validation.CheckCustomerSegmentEligibility(
        request,
        timeout=deps.settings.timeout
    )


async def on_lineage_node_validation_service_explain_lineage_node_decision_0(
    deps: Dependencies,
    payload: Message
) -> Message:
    request = cast(lineage_v1_lineage_edge_calculation_service_pb2.SimulateLineageEdgeRequest, payload)
    return await deps.clients.lineage_lineage_edge_calculation.SimulateLineageEdge(
        request,
        timeout=deps.settings.timeout
    )


async def on_lineage_node_workflow_service_pause_lineage_node_workflow_2(
    deps: Dependencies,
    payload: Message
) -> Message:
    request = cast(lineage_v1_lineage_node_approval_service_pb2.EscalateLineageNodeRequest, payload)
    return await deps.clients.lineage_lineage_node_approval.EscalateLineageNode(request, timeout=deps.settings.timeout)


def subscribe(deps: Dependencies) -> None:
    deps.bus.subscribe(
        'acme.lineage.v1.ImpactCalculationService/CompareImpactOptions/2',
        partial(on_impact_calculation_service_compare_impact_options_2, deps)
    )
    deps.bus.subscribe(
        'acme.lineage.v1.ImpactImportService/GetImpactImportStatus/1',
        partial(on_impact_import_service_get_impact_import_status_1, deps)
    )
    deps.bus.subscribe(
        'acme.lineage.v1.ImpactSyncService/PullImpacts/0',
        partial(on_impact_sync_service_pull_impacts_0, deps)
    )
    deps.bus.subscribe(
        'acme.lineage.v1.ImpactSyncService/SyncImpacts/2',
        partial(on_impact_sync_service_sync_impacts_2, deps)
    )
    deps.bus.subscribe(
        'acme.lineage.v1.ImpactValidationService/PreviewImpact/1',
        partial(on_impact_validation_service_preview_impact_1, deps)
    )
    deps.bus.subscribe(
        'acme.lineage.v1.LineageEdgeApprovalService/RecallLineageEdge/0',
        partial(on_lineage_edge_approval_service_recall_lineage_edge_0, deps)
    )
    deps.bus.subscribe(
        'acme.lineage.v1.LineageEdgeCalculationService/ExplainLineageEdgeCalculation/1',
        partial(on_lineage_edge_calculation_service_explain_lineage_edge_calculation_1, deps)
    )
    deps.bus.subscribe(
        'acme.lineage.v1.LineageEdgeImportService/RetryLineageEdgeImport/0',
        partial(on_lineage_edge_import_service_retry_lineage_edge_import_0, deps)
    )
    deps.bus.subscribe(
        'acme.lineage.v1.LineageEdgeQueryService/SummarizeLineageEdges/3',
        partial(on_lineage_edge_query_service_summarize_lineage_edges_3, deps)
    )
    deps.bus.subscribe(
        'acme.lineage.v1.LineageEdgeSyncService/ReconcileLineageEdges/0',
        partial(on_lineage_edge_sync_service_reconcile_lineage_edges_0, deps)
    )
    deps.bus.subscribe(
        'acme.lineage.v1.LineageEdgeWorkflowService/ResumeLineageEdgeWorkflow/1',
        partial(on_lineage_edge_workflow_service_resume_lineage_edge_workflow_1, deps)
    )
    deps.bus.subscribe(
        'acme.lineage.v1.LineageNodeLifecycleService/ReinstateLineageNode/0',
        partial(on_lineage_node_lifecycle_service_reinstate_lineage_node_0, deps)
    )
    deps.bus.subscribe(
        'acme.lineage.v1.LineageNodeSyncService/PullLineageNodes/0',
        partial(on_lineage_node_sync_service_pull_lineage_nodes_0, deps)
    )
    deps.bus.subscribe(
        'acme.lineage.v1.LineageNodeValidationService/ExplainLineageNodeDecision/0',
        partial(on_lineage_node_validation_service_explain_lineage_node_decision_0, deps)
    )
    deps.bus.subscribe(
        'acme.lineage.v1.LineageNodeWorkflowService/PauseLineageNodeWorkflow/2',
        partial(on_lineage_node_workflow_service_pause_lineage_node_workflow_2, deps)
    )
