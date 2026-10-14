"""Background event handlers owned by the datahub team."""

from __future__ import annotations

from functools import partial
from typing import cast

from google.protobuf.message import Message

from acme.anomalies.v1 import anomaly_approval_service_pb2 as anomalies_v1_anomaly_approval_service_pb2
from acme.authorization.v1 import (
    access_policy_validation_service_pb2 as authorization_v1_access_policy_validation_service_pb2,
)
from acme.customers.v1 import consent_record_approval_service_pb2 as customers_v1_consent_record_approval_service_pb2
from acme.customers.v1 import consent_record_sync_service_pb2 as customers_v1_consent_record_sync_service_pb2
from acme.customers.v1 import consent_record_workflow_service_pb2 as customers_v1_consent_record_workflow_service_pb2
from acme.customers.v1 import (
    customer_segment_approval_service_pb2 as customers_v1_customer_segment_approval_service_pb2,
)
from acme.customers.v1 import customer_segment_import_service_pb2 as customers_v1_customer_segment_import_service_pb2
from acme.customers.v1 import customer_segment_sync_service_pb2 as customers_v1_customer_segment_sync_service_pb2
from acme.datahub.v1 import data_share_validation_service_pb2 as datahub_v1_data_share_validation_service_pb2
from acme.datahub.v1 import data_share_workflow_service_pb2 as datahub_v1_data_share_workflow_service_pb2
from acme.datahub.v1 import notebook_workflow_service_pb2 as datahub_v1_notebook_workflow_service_pb2
from acme.datahub.v1 import workspace_approval_service_pb2 as datahub_v1_workspace_approval_service_pb2
from acme.datahub.v1 import workspace_integration_service_pb2 as datahub_v1_workspace_integration_service_pb2
from acme.featurestore.v1 import (
    feature_value_workflow_service_pb2 as featurestore_v1_feature_value_workflow_service_pb2,
)
from acme.metrics.v1 import metric_series_query_service_pb2 as metrics_v1_metric_series_query_service_pb2
from acme.modelregistry.v1 import deployment_approval_service_pb2 as modelregistry_v1_deployment_approval_service_pb2
from acme.notifications.v1 import (
    notification_validation_service_pb2 as notifications_v1_notification_validation_service_pb2,
)

from acme_data.domains.datahub.dependencies import Dependencies


async def on_data_share_approval_service_delegate_data_share_approval_0(
    deps: Dependencies,
    payload: Message
) -> Message:
    request = cast(customers_v1_customer_segment_sync_service_pb2.ReconcileCustomerSegmentsRequest, payload)
    return await deps.clients.customers_customer_segment_sync.ReconcileCustomerSegments(
        request,
        timeout=deps.settings.timeout
    )


async def on_data_share_integration_service_replay_data_share_events_0(deps: Dependencies, payload: Message) -> Message:
    request = cast(customers_v1_customer_segment_approval_service_pb2.RejectCustomerSegmentRequest, payload)
    return await deps.clients.customers_customer_segment_approval.RejectCustomerSegment(
        request,
        timeout=deps.settings.timeout
    )


async def on_data_share_query_service_export_data_shares_1(deps: Dependencies, payload: Message) -> Message:
    request = cast(datahub_v1_workspace_integration_service_pb2.ConnectWorkspaceSourceRequest, payload)
    return await deps.clients.datahub_workspace_integration.ConnectWorkspaceSource(
        request,
        timeout=deps.settings.timeout
    )


async def on_data_share_reporting_service_generate_data_share_report_0(deps: Dependencies, payload: Message) -> Message:
    request = cast(customers_v1_consent_record_workflow_service_pb2.ResumeConsentRecordWorkflowRequest, payload)
    return await deps.clients.customers_consent_record_workflow.ResumeConsentRecordWorkflow(
        request,
        timeout=deps.settings.timeout
    )


async def on_data_share_validation_service_explain_data_share_decision_2(
    deps: Dependencies,
    payload: Message
) -> Message:
    request = cast(modelregistry_v1_deployment_approval_service_pb2.CommentDeploymentApprovalRequest, payload)
    return await deps.clients.modelregistry_deployment_approval.CommentDeploymentApproval(
        request,
        timeout=deps.settings.timeout
    )


async def on_data_share_workflow_service_advance_data_share_workflow_2(deps: Dependencies, payload: Message) -> Message:
    request = cast(datahub_v1_workspace_approval_service_pb2.EscalateWorkspaceRequest, payload)
    return await deps.clients.datahub_workspace_approval.EscalateWorkspace(request, timeout=deps.settings.timeout)


async def on_data_share_workflow_service_start_data_share_workflow_0(deps: Dependencies, payload: Message) -> Message:
    request = cast(datahub_v1_notebook_workflow_service_pb2.ResumeNotebookWorkflowRequest, payload)
    return await deps.clients.datahub_notebook_workflow.ResumeNotebookWorkflow(request, timeout=deps.settings.timeout)


async def on_notebook_approval_service_recall_notebook_1(deps: Dependencies, payload: Message) -> Message:
    request = cast(authorization_v1_access_policy_validation_service_pb2.ExplainAccessPolicyDecisionRequest, payload)
    return await deps.clients.authorization_access_policy_validation.ExplainAccessPolicyDecision(
        request,
        timeout=deps.settings.timeout
    )


async def on_notebook_integration_service_disconnect_notebook_source_2(deps: Dependencies, payload: Message) -> Message:
    request = cast(featurestore_v1_feature_value_workflow_service_pb2.ResumeFeatureValueWorkflowRequest, payload)
    return await deps.clients.featurestore_feature_value_workflow.ResumeFeatureValueWorkflow(
        request,
        timeout=deps.settings.timeout
    )


async def on_notebook_notification_service_subscribe_notebook_updates_0(
    deps: Dependencies,
    payload: Message
) -> Message:
    request = cast(datahub_v1_data_share_workflow_service_pb2.RetryDataShareWorkflowRequest, payload)
    return await deps.clients.datahub_data_share_workflow.RetryDataShareWorkflow(request, timeout=deps.settings.timeout)


async def on_notebook_reporting_service_delete_notebook_report_2(deps: Dependencies, payload: Message) -> Message:
    request = cast(notifications_v1_notification_validation_service_pb2.LintNotificationsRequest, payload)
    return await deps.clients.notifications_notification_validation.LintNotifications(
        request,
        timeout=deps.settings.timeout
    )


async def on_notebook_workflow_service_retry_notebook_workflow_0(deps: Dependencies, payload: Message) -> Message:
    request = cast(customers_v1_customer_segment_import_service_pb2.RetryCustomerSegmentImportRequest, payload)
    return await deps.clients.customers_customer_segment_import.RetryCustomerSegmentImport(
        request,
        timeout=deps.settings.timeout
    )


async def on_workspace_approval_service_delegate_workspace_approval_2(deps: Dependencies, payload: Message) -> Message:
    request = cast(customers_v1_consent_record_approval_service_pb2.CommentConsentRecordApprovalRequest, payload)
    return await deps.clients.customers_consent_record_approval.CommentConsentRecordApproval(
        request,
        timeout=deps.settings.timeout
    )


async def on_workspace_integration_service_acknowledge_workspace_event_1(
    deps: Dependencies,
    payload: Message
) -> Message:
    request = cast(anomalies_v1_anomaly_approval_service_pb2.RejectAnomalyRequest, payload)
    return await deps.clients.anomalies_anomaly_approval.RejectAnomaly(request, timeout=deps.settings.timeout)


async def on_workspace_reporting_service_fetch_workspace_report_1(deps: Dependencies, payload: Message) -> Message:
    request = cast(metrics_v1_metric_series_query_service_pb2.SuggestMetricSeriesesRequest, payload)
    return await deps.clients.metrics_metric_series_query.SuggestMetricSerieses(request, timeout=deps.settings.timeout)


async def on_workspace_service_clone_workspace_0(deps: Dependencies, payload: Message) -> Message:
    request = cast(datahub_v1_data_share_validation_service_pb2.LintDataSharesRequest, payload)
    return await deps.clients.datahub_data_share_validation.LintDataShares(request, timeout=deps.settings.timeout)


async def on_workspace_workflow_service_retry_workspace_workflow_1(deps: Dependencies, payload: Message) -> Message:
    request = cast(customers_v1_consent_record_sync_service_pb2.PushConsentRecordRequest, payload)
    return await deps.clients.customers_consent_record_sync.PushConsentRecord(request, timeout=deps.settings.timeout)


def subscribe(deps: Dependencies) -> None:
    deps.bus.subscribe(
        'acme.datahub.v1.DataShareApprovalService/DelegateDataShareApproval/0',
        partial(on_data_share_approval_service_delegate_data_share_approval_0, deps)
    )
    deps.bus.subscribe(
        'acme.datahub.v1.DataShareIntegrationService/ReplayDataShareEvents/0',
        partial(on_data_share_integration_service_replay_data_share_events_0, deps)
    )
    deps.bus.subscribe(
        'acme.datahub.v1.DataShareQueryService/ExportDataShares/1',
        partial(on_data_share_query_service_export_data_shares_1, deps)
    )
    deps.bus.subscribe(
        'acme.datahub.v1.DataShareReportingService/GenerateDataShareReport/0',
        partial(on_data_share_reporting_service_generate_data_share_report_0, deps)
    )
    deps.bus.subscribe(
        'acme.datahub.v1.DataShareValidationService/ExplainDataShareDecision/2',
        partial(on_data_share_validation_service_explain_data_share_decision_2, deps)
    )
    deps.bus.subscribe(
        'acme.datahub.v1.DataShareWorkflowService/AdvanceDataShareWorkflow/2',
        partial(on_data_share_workflow_service_advance_data_share_workflow_2, deps)
    )
    deps.bus.subscribe(
        'acme.datahub.v1.DataShareWorkflowService/StartDataShareWorkflow/0',
        partial(on_data_share_workflow_service_start_data_share_workflow_0, deps)
    )
    deps.bus.subscribe(
        'acme.datahub.v1.NotebookApprovalService/RecallNotebook/1',
        partial(on_notebook_approval_service_recall_notebook_1, deps)
    )
    deps.bus.subscribe(
        'acme.datahub.v1.NotebookIntegrationService/DisconnectNotebookSource/2',
        partial(on_notebook_integration_service_disconnect_notebook_source_2, deps)
    )
    deps.bus.subscribe(
        'acme.datahub.v1.NotebookNotificationService/SubscribeNotebookUpdates/0',
        partial(on_notebook_notification_service_subscribe_notebook_updates_0, deps)
    )
    deps.bus.subscribe(
        'acme.datahub.v1.NotebookReportingService/DeleteNotebookReport/2',
        partial(on_notebook_reporting_service_delete_notebook_report_2, deps)
    )
    deps.bus.subscribe(
        'acme.datahub.v1.NotebookWorkflowService/RetryNotebookWorkflow/0',
        partial(on_notebook_workflow_service_retry_notebook_workflow_0, deps)
    )
    deps.bus.subscribe(
        'acme.datahub.v1.WorkspaceApprovalService/DelegateWorkspaceApproval/2',
        partial(on_workspace_approval_service_delegate_workspace_approval_2, deps)
    )
    deps.bus.subscribe(
        'acme.datahub.v1.WorkspaceIntegrationService/AcknowledgeWorkspaceEvent/1',
        partial(on_workspace_integration_service_acknowledge_workspace_event_1, deps)
    )
    deps.bus.subscribe(
        'acme.datahub.v1.WorkspaceReportingService/FetchWorkspaceReport/1',
        partial(on_workspace_reporting_service_fetch_workspace_report_1, deps)
    )
    deps.bus.subscribe(
        'acme.datahub.v1.WorkspaceService/CloneWorkspace/0',
        partial(on_workspace_service_clone_workspace_0, deps)
    )
    deps.bus.subscribe(
        'acme.datahub.v1.WorkspaceWorkflowService/RetryWorkspaceWorkflow/1',
        partial(on_workspace_workflow_service_retry_workspace_workflow_1, deps)
    )
