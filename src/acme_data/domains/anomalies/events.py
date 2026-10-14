"""Background event handlers owned by the anomalies team."""

from __future__ import annotations

from functools import partial
from typing import cast

from google.protobuf.message import Message

from acme.anomalies.v1 import anomaly_query_service_pb2 as anomalies_v1_anomaly_query_service_pb2
from acme.anomalies.v1 import anomaly_service_pb2 as anomalies_v1_anomaly_service_pb2
from acme.anomalies.v1 import anomaly_validation_service_pb2 as anomalies_v1_anomaly_validation_service_pb2
from acme.lineage.v1 import impact_validation_service_pb2 as lineage_v1_impact_validation_service_pb2
from acme.lineage.v1 import lineage_node_validation_service_pb2 as lineage_v1_lineage_node_validation_service_pb2
from acme.notifications.v1 import notification_query_service_pb2 as notifications_v1_notification_query_service_pb2

from acme_data.domains.anomalies.dependencies import Dependencies


async def on_anomaly_approval_service_comment_anomaly_approval_1(deps: Dependencies, payload: Message) -> Message:
    request = cast(anomalies_v1_anomaly_service_pb2.GetAnomalyRequest, payload)
    return await deps.clients.anomalies_anomaly.GetAnomaly(request, timeout=deps.settings.timeout)


async def on_anomaly_feedback_approval_service_approve_anomaly_feedback_3(
    deps: Dependencies,
    payload: Message
) -> Message:
    request = cast(anomalies_v1_anomaly_service_pb2.UpdateAnomalyRequest, payload)
    return await deps.clients.anomalies_anomaly.UpdateAnomaly(request, timeout=deps.settings.timeout)


async def on_anomaly_feedback_validation_service_check_anomaly_feedback_eligibility_1(
    deps: Dependencies,
    payload: Message
) -> Message:
    request = cast(lineage_v1_impact_validation_service_pb2.ExplainImpactDecisionRequest, payload)
    return await deps.clients.lineage_impact_validation.ExplainImpactDecision(request, timeout=deps.settings.timeout)


async def on_anomaly_feedback_workflow_service_signal_anomaly_feedback_workflow_2(
    deps: Dependencies,
    payload: Message
) -> Message:
    request = cast(notifications_v1_notification_query_service_pb2.ResolveNotificationsRequest, payload)
    return await deps.clients.notifications_notification_query.ResolveNotifications(
        request,
        timeout=deps.settings.timeout
    )


async def on_anomaly_validation_service_normalize_anomaly_1(deps: Dependencies, payload: Message) -> Message:
    request = cast(lineage_v1_lineage_node_validation_service_pb2.LintLineageNodesRequest, payload)
    return await deps.clients.lineage_lineage_node_validation.LintLineageNodes(request, timeout=deps.settings.timeout)


async def on_anomaly_workflow_service_resume_anomaly_workflow_0(deps: Dependencies, payload: Message) -> Message:
    request = cast(anomalies_v1_anomaly_query_service_pb2.PeekAnomalyRequest, payload)
    return await deps.clients.anomalies_anomaly_query.PeekAnomaly(request, timeout=deps.settings.timeout)


async def on_detector_approval_service_escalate_detector_1(deps: Dependencies, payload: Message) -> Message:
    request = cast(anomalies_v1_anomaly_validation_service_pb2.ScoreAnomalyRequest, payload)
    return await deps.clients.anomalies_anomaly_validation.ScoreAnomaly(request, timeout=deps.settings.timeout)


async def on_detector_query_service_suggest_detectors_1(deps: Dependencies, payload: Message) -> Message:
    request = cast(anomalies_v1_anomaly_query_service_pb2.FindAnomaliesRequest, payload)
    return await deps.clients.anomalies_anomaly_query.FindAnomalies(request, timeout=deps.settings.timeout)


def subscribe(deps: Dependencies) -> None:
    deps.bus.subscribe(
        'acme.anomalies.v1.AnomalyApprovalService/CommentAnomalyApproval/1',
        partial(on_anomaly_approval_service_comment_anomaly_approval_1, deps)
    )
    deps.bus.subscribe(
        'acme.anomalies.v1.AnomalyFeedbackApprovalService/ApproveAnomalyFeedback/3',
        partial(on_anomaly_feedback_approval_service_approve_anomaly_feedback_3, deps)
    )
    deps.bus.subscribe(
        'acme.anomalies.v1.AnomalyFeedbackValidationService/CheckAnomalyFeedbackEligibility/1',
        partial(on_anomaly_feedback_validation_service_check_anomaly_feedback_eligibility_1, deps)
    )
    deps.bus.subscribe(
        'acme.anomalies.v1.AnomalyFeedbackWorkflowService/SignalAnomalyFeedbackWorkflow/2',
        partial(on_anomaly_feedback_workflow_service_signal_anomaly_feedback_workflow_2, deps)
    )
    deps.bus.subscribe(
        'acme.anomalies.v1.AnomalyValidationService/NormalizeAnomaly/1',
        partial(on_anomaly_validation_service_normalize_anomaly_1, deps)
    )
    deps.bus.subscribe(
        'acme.anomalies.v1.AnomalyWorkflowService/ResumeAnomalyWorkflow/0',
        partial(on_anomaly_workflow_service_resume_anomaly_workflow_0, deps)
    )
    deps.bus.subscribe(
        'acme.anomalies.v1.DetectorApprovalService/EscalateDetector/1',
        partial(on_detector_approval_service_escalate_detector_1, deps)
    )
    deps.bus.subscribe(
        'acme.anomalies.v1.DetectorQueryService/SuggestDetectors/1',
        partial(on_detector_query_service_suggest_detectors_1, deps)
    )
