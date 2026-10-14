"""Background event handlers owned by the labeling team."""

from __future__ import annotations

from functools import partial
from typing import cast

from google.protobuf.message import Message

from acme.anomalies.v1 import (
    anomaly_feedback_approval_service_pb2 as anomalies_v1_anomaly_feedback_approval_service_pb2,
)
from acme.authorization.v1 import access_policy_service_pb2 as authorization_v1_access_policy_service_pb2
from acme.experiments.v1 import experiment_query_service_pb2 as experiments_v1_experiment_query_service_pb2
from acme.featureflags.v1 import feature_flag_query_service_pb2 as featureflags_v1_feature_flag_query_service_pb2
from acme.labeling.v1 import annotation_calculation_service_pb2 as labeling_v1_annotation_calculation_service_pb2
from acme.labeling.v1 import annotation_validation_service_pb2 as labeling_v1_annotation_validation_service_pb2
from acme.labeling.v1 import label_set_sync_service_pb2 as labeling_v1_label_set_sync_service_pb2
from acme.labeling.v1 import labeling_task_calculation_service_pb2 as labeling_v1_labeling_task_calculation_service_pb2
from acme.labeling.v1 import labeling_task_service_pb2 as labeling_v1_labeling_task_service_pb2
from acme.ledger.v1 import ledger_account_validation_service_pb2 as ledger_v1_ledger_account_validation_service_pb2
from acme.lineage.v1 import impact_approval_service_pb2 as lineage_v1_impact_approval_service_pb2
from acme.lineage.v1 import impact_validation_service_pb2 as lineage_v1_impact_validation_service_pb2
from acme.lineage.v1 import lineage_node_reporting_service_pb2 as lineage_v1_lineage_node_reporting_service_pb2
from acme.notifications.v1 import (
    notification_validation_service_pb2 as notifications_v1_notification_validation_service_pb2,
)
from acme.yards.v1 import yard_calculation_service_pb2 as yards_v1_yard_calculation_service_pb2

from acme_data.domains.labeling.dependencies import Dependencies


async def on_annotation_approval_service_reject_annotation_1(deps: Dependencies, payload: Message) -> Message:
    request = cast(anomalies_v1_anomaly_feedback_approval_service_pb2.SubmitAnomalyFeedbackRequest, payload)
    return await deps.clients.anomalies_anomaly_feedback_approval.SubmitAnomalyFeedback(
        request,
        timeout=deps.settings.timeout
    )


async def on_annotation_calculation_service_recalculate_annotations_0(deps: Dependencies, payload: Message) -> Message:
    request = cast(labeling_v1_labeling_task_calculation_service_pb2.CompareLabelingTaskOptionsRequest, payload)
    return await deps.clients.labeling_labeling_task_calculation.CompareLabelingTaskOptions(
        request,
        timeout=deps.settings.timeout
    )


async def on_annotation_query_service_export_annotations_0(deps: Dependencies, payload: Message) -> Message:
    request = cast(labeling_v1_annotation_validation_service_pb2.LintAnnotationsRequest, payload)
    return await deps.clients.labeling_annotation_validation.LintAnnotations(request, timeout=deps.settings.timeout)


async def on_annotation_reporting_service_list_annotation_reports_1(deps: Dependencies, payload: Message) -> Message:
    request = cast(labeling_v1_labeling_task_service_pb2.SearchLabelingTasksRequest, payload)
    return await deps.clients.labeling_labeling_task.SearchLabelingTasks(request, timeout=deps.settings.timeout)


async def on_annotation_validation_service_preview_annotation_1(deps: Dependencies, payload: Message) -> Message:
    request = cast(yards_v1_yard_calculation_service_pb2.EstimateYardRequest, payload)
    return await deps.clients.yards_yard_calculation.EstimateYard(request, timeout=deps.settings.timeout)


async def on_annotation_workflow_service_pause_annotation_workflow_0(deps: Dependencies, payload: Message) -> Message:
    request = cast(notifications_v1_notification_validation_service_pb2.ValidateNotificationRequest, payload)
    return await deps.clients.notifications_notification_validation.ValidateNotification(
        request,
        timeout=deps.settings.timeout
    )


async def on_label_set_approval_service_delegate_label_set_approval_1(deps: Dependencies, payload: Message) -> Message:
    request = cast(labeling_v1_label_set_sync_service_pb2.ResolveLabelSetConflictRequest, payload)
    return await deps.clients.labeling_label_set_sync.ResolveLabelSetConflict(request, timeout=deps.settings.timeout)


async def on_label_set_calculation_service_compare_label_set_options_0(deps: Dependencies, payload: Message) -> Message:
    request = cast(labeling_v1_annotation_calculation_service_pb2.CompareAnnotationOptionsRequest, payload)
    return await deps.clients.labeling_annotation_calculation.CompareAnnotationOptions(
        request,
        timeout=deps.settings.timeout
    )


async def on_label_set_lifecycle_service_activate_label_set_1(deps: Dependencies, payload: Message) -> Message:
    request = cast(authorization_v1_access_policy_service_pb2.BatchGetAccessPoliciesRequest, payload)
    return await deps.clients.authorization_access_policy.BatchGetAccessPolicies(request, timeout=deps.settings.timeout)


async def on_label_set_reporting_service_count_label_set_totals_1(deps: Dependencies, payload: Message) -> Message:
    request = cast(experiments_v1_experiment_query_service_pb2.SummarizeExperimentsRequest, payload)
    return await deps.clients.experiments_experiment_query.SummarizeExperiments(request, timeout=deps.settings.timeout)


async def on_label_set_sync_service_resolve_label_set_conflict_0(deps: Dependencies, payload: Message) -> Message:
    request = cast(lineage_v1_lineage_node_reporting_service_pb2.CountLineageNodeTotalsRequest, payload)
    return await deps.clients.lineage_lineage_node_reporting.CountLineageNodeTotals(
        request,
        timeout=deps.settings.timeout
    )


async def on_label_set_validation_service_score_label_set_1(deps: Dependencies, payload: Message) -> Message:
    request = cast(ledger_v1_ledger_account_validation_service_pb2.LintLedgerAccountsRequest, payload)
    return await deps.clients.ledger_ledger_account_validation.LintLedgerAccounts(
        request,
        timeout=deps.settings.timeout
    )


async def on_label_set_workflow_service_retry_label_set_workflow_2(deps: Dependencies, payload: Message) -> Message:
    request = cast(labeling_v1_label_set_sync_service_pb2.ResolveLabelSetConflictRequest, payload)
    return await deps.clients.labeling_label_set_sync.ResolveLabelSetConflict(request, timeout=deps.settings.timeout)


async def on_labeling_task_approval_service_reject_labeling_task_0(deps: Dependencies, payload: Message) -> Message:
    request = cast(lineage_v1_impact_approval_service_pb2.SubmitImpactRequest, payload)
    return await deps.clients.lineage_impact_approval.SubmitImpact(request, timeout=deps.settings.timeout)


async def on_labeling_task_calculation_service_quote_labeling_task_1(deps: Dependencies, payload: Message) -> Message:
    request = cast(featureflags_v1_feature_flag_query_service_pb2.CountFeatureFlagsRequest, payload)
    return await deps.clients.featureflags_feature_flag_query.CountFeatureFlags(request, timeout=deps.settings.timeout)


async def on_labeling_task_validation_service_normalize_labeling_task_0(
    deps: Dependencies,
    payload: Message
) -> Message:
    request = cast(lineage_v1_impact_validation_service_pb2.NormalizeImpactRequest, payload)
    return await deps.clients.lineage_impact_validation.NormalizeImpact(request, timeout=deps.settings.timeout)


def subscribe(deps: Dependencies) -> None:
    deps.bus.subscribe(
        'acme.labeling.v1.AnnotationApprovalService/RejectAnnotation/1',
        partial(on_annotation_approval_service_reject_annotation_1, deps)
    )
    deps.bus.subscribe(
        'acme.labeling.v1.AnnotationCalculationService/RecalculateAnnotations/0',
        partial(on_annotation_calculation_service_recalculate_annotations_0, deps)
    )
    deps.bus.subscribe(
        'acme.labeling.v1.AnnotationQueryService/ExportAnnotations/0',
        partial(on_annotation_query_service_export_annotations_0, deps)
    )
    deps.bus.subscribe(
        'acme.labeling.v1.AnnotationReportingService/ListAnnotationReports/1',
        partial(on_annotation_reporting_service_list_annotation_reports_1, deps)
    )
    deps.bus.subscribe(
        'acme.labeling.v1.AnnotationValidationService/PreviewAnnotation/1',
        partial(on_annotation_validation_service_preview_annotation_1, deps)
    )
    deps.bus.subscribe(
        'acme.labeling.v1.AnnotationWorkflowService/PauseAnnotationWorkflow/0',
        partial(on_annotation_workflow_service_pause_annotation_workflow_0, deps)
    )
    deps.bus.subscribe(
        'acme.labeling.v1.LabelSetApprovalService/DelegateLabelSetApproval/1',
        partial(on_label_set_approval_service_delegate_label_set_approval_1, deps)
    )
    deps.bus.subscribe(
        'acme.labeling.v1.LabelSetCalculationService/CompareLabelSetOptions/0',
        partial(on_label_set_calculation_service_compare_label_set_options_0, deps)
    )
    deps.bus.subscribe(
        'acme.labeling.v1.LabelSetLifecycleService/ActivateLabelSet/1',
        partial(on_label_set_lifecycle_service_activate_label_set_1, deps)
    )
    deps.bus.subscribe(
        'acme.labeling.v1.LabelSetReportingService/CountLabelSetTotals/1',
        partial(on_label_set_reporting_service_count_label_set_totals_1, deps)
    )
    deps.bus.subscribe(
        'acme.labeling.v1.LabelSetSyncService/ResolveLabelSetConflict/0',
        partial(on_label_set_sync_service_resolve_label_set_conflict_0, deps)
    )
    deps.bus.subscribe(
        'acme.labeling.v1.LabelSetValidationService/ScoreLabelSet/1',
        partial(on_label_set_validation_service_score_label_set_1, deps)
    )
    deps.bus.subscribe(
        'acme.labeling.v1.LabelSetWorkflowService/RetryLabelSetWorkflow/2',
        partial(on_label_set_workflow_service_retry_label_set_workflow_2, deps)
    )
    deps.bus.subscribe(
        'acme.labeling.v1.LabelingTaskApprovalService/RejectLabelingTask/0',
        partial(on_labeling_task_approval_service_reject_labeling_task_0, deps)
    )
    deps.bus.subscribe(
        'acme.labeling.v1.LabelingTaskCalculationService/QuoteLabelingTask/1',
        partial(on_labeling_task_calculation_service_quote_labeling_task_1, deps)
    )
    deps.bus.subscribe(
        'acme.labeling.v1.LabelingTaskValidationService/NormalizeLabelingTask/0',
        partial(on_labeling_task_validation_service_normalize_labeling_task_0, deps)
    )
