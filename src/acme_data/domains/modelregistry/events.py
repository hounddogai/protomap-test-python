"""Background event handlers owned by the modelregistry team."""

from __future__ import annotations

from functools import partial
from typing import cast

from google.protobuf.message import Message

from acme.customers.v1 import customer_calculation_service_pb2 as customers_v1_customer_calculation_service_pb2
from acme.customers.v1 import (
    customer_segment_validation_service_pb2 as customers_v1_customer_segment_validation_service_pb2,
)
from acme.customers.v1 import preference_validation_service_pb2 as customers_v1_preference_validation_service_pb2
from acme.featurestore.v1 import entity_sync_service_pb2 as featurestore_v1_entity_sync_service_pb2
from acme.ledger.v1 import ledger_account_service_pb2 as ledger_v1_ledger_account_service_pb2
from acme.metrics.v1 import dashboard_validation_service_pb2 as metrics_v1_dashboard_validation_service_pb2
from acme.metrics.v1 import metric_series_validation_service_pb2 as metrics_v1_metric_series_validation_service_pb2
from acme.modelregistry.v1 import deployment_approval_service_pb2 as modelregistry_v1_deployment_approval_service_pb2
from acme.modelregistry.v1 import (
    deployment_calculation_service_pb2 as modelregistry_v1_deployment_calculation_service_pb2,
)
from acme.modelregistry.v1 import deployment_import_service_pb2 as modelregistry_v1_deployment_import_service_pb2
from acme.modelregistry.v1 import deployment_sync_service_pb2 as modelregistry_v1_deployment_sync_service_pb2
from acme.modelregistry.v1 import (
    model_version_calculation_service_pb2 as modelregistry_v1_model_version_calculation_service_pb2,
)
from acme.modelregistry.v1 import (
    registered_model_calculation_service_pb2 as modelregistry_v1_registered_model_calculation_service_pb2,
)
from acme.modelregistry.v1 import (
    registered_model_query_service_pb2 as modelregistry_v1_registered_model_query_service_pb2,
)
from acme.modelregistry.v1 import (
    registered_model_reporting_service_pb2 as modelregistry_v1_registered_model_reporting_service_pb2,
)
from acme.modelregistry.v1 import (
    registered_model_sync_service_pb2 as modelregistry_v1_registered_model_sync_service_pb2,
)
from acme.notifications.v1 import notification_service_pb2 as notifications_v1_notification_service_pb2

from acme_data.domains.modelregistry.dependencies import Dependencies


async def on_deployment_approval_service_delegate_deployment_approval_1(
    deps: Dependencies,
    payload: Message
) -> Message:
    request = cast(customers_v1_customer_segment_validation_service_pb2.ExplainCustomerSegmentDecisionRequest, payload)
    return await deps.clients.customers_customer_segment_validation.ExplainCustomerSegmentDecision(
        request,
        timeout=deps.settings.timeout
    )


async def on_deployment_calculation_service_quote_deployment_2(deps: Dependencies, payload: Message) -> Message:
    request = cast(
        modelregistry_v1_registered_model_calculation_service_pb2.RecalculateRegisteredModelsRequest,
        payload
    )
    return await deps.clients.modelregistry_registered_model_calculation.RecalculateRegisteredModels(
        request,
        timeout=deps.settings.timeout
    )


async def on_deployment_lifecycle_service_suspend_deployment_0(deps: Dependencies, payload: Message) -> Message:
    request = cast(modelregistry_v1_deployment_import_service_pb2.RetryDeploymentImportRequest, payload)
    return await deps.clients.modelregistry_deployment_import.RetryDeploymentImport(
        request,
        timeout=deps.settings.timeout
    )


async def on_deployment_reporting_service_share_deployment_report_0(deps: Dependencies, payload: Message) -> Message:
    request = cast(metrics_v1_metric_series_validation_service_pb2.CheckMetricSeriesEligibilityRequest, payload)
    return await deps.clients.metrics_metric_series_validation.CheckMetricSeriesEligibility(
        request,
        timeout=deps.settings.timeout
    )


async def on_deployment_sync_service_stream_deployment_changes_2(deps: Dependencies, payload: Message) -> Message:
    request = cast(modelregistry_v1_registered_model_query_service_pb2.CountRegisteredModelsRequest, payload)
    return await deps.clients.modelregistry_registered_model_query.CountRegisteredModels(
        request,
        timeout=deps.settings.timeout
    )


async def on_deployment_validation_service_score_deployment_1(deps: Dependencies, payload: Message) -> Message:
    request = cast(ledger_v1_ledger_account_service_pb2.SearchLedgerAccountsRequest, payload)
    return await deps.clients.ledger_ledger_account.SearchLedgerAccounts(request, timeout=deps.settings.timeout)


async def on_model_version_approval_service_approve_model_version_0(deps: Dependencies, payload: Message) -> Message:
    request = cast(modelregistry_v1_registered_model_reporting_service_pb2.ListRegisteredModelReportsRequest, payload)
    return await deps.clients.modelregistry_registered_model_reporting.ListRegisteredModelReports(
        request,
        timeout=deps.settings.timeout
    )


async def on_model_version_lifecycle_service_renew_model_version_1(deps: Dependencies, payload: Message) -> Message:
    request = cast(customers_v1_customer_calculation_service_pb2.ExplainCustomerCalculationRequest, payload)
    return await deps.clients.customers_customer_calculation.ExplainCustomerCalculation(
        request,
        timeout=deps.settings.timeout
    )


async def on_model_version_sync_service_pull_model_versions_1(deps: Dependencies, payload: Message) -> Message:
    request = cast(featurestore_v1_entity_sync_service_pb2.PushEntityRequest, payload)
    return await deps.clients.featurestore_entity_sync.PushEntity(request, timeout=deps.settings.timeout)


async def on_model_version_validation_service_check_model_version_eligibility_1(
    deps: Dependencies,
    payload: Message
) -> Message:
    request = cast(modelregistry_v1_deployment_calculation_service_pb2.RecalculateDeploymentsRequest, payload)
    return await deps.clients.modelregistry_deployment_calculation.RecalculateDeployments(
        request,
        timeout=deps.settings.timeout
    )


async def on_model_version_validation_service_score_model_version_2(deps: Dependencies, payload: Message) -> Message:
    request = cast(
        modelregistry_v1_model_version_calculation_service_pb2.ExplainModelVersionCalculationRequest,
        payload
    )
    return await deps.clients.modelregistry_model_version_calculation.ExplainModelVersionCalculation(
        request,
        timeout=deps.settings.timeout
    )


async def on_model_version_workflow_service_retry_model_version_workflow_0(
    deps: Dependencies,
    payload: Message
) -> Message:
    request = cast(modelregistry_v1_deployment_approval_service_pb2.SubmitDeploymentRequest, payload)
    return await deps.clients.modelregistry_deployment_approval.SubmitDeployment(request, timeout=deps.settings.timeout)


async def on_registered_model_approval_service_reject_registered_model_1(
    deps: Dependencies,
    payload: Message
) -> Message:
    request = cast(notifications_v1_notification_service_pb2.CloneNotificationRequest, payload)
    return await deps.clients.notifications_notification.CloneNotification(request, timeout=deps.settings.timeout)


async def on_registered_model_lifecycle_service_activate_registered_model_0(
    deps: Dependencies,
    payload: Message
) -> Message:
    request = cast(modelregistry_v1_deployment_sync_service_pb2.PullDeploymentsRequest, payload)
    return await deps.clients.modelregistry_deployment_sync.PullDeployments(request, timeout=deps.settings.timeout)


async def on_registered_model_lifecycle_service_terminate_registered_model_3(
    deps: Dependencies,
    payload: Message
) -> Message:
    request = cast(customers_v1_preference_validation_service_pb2.CheckPreferenceEligibilityRequest, payload)
    return await deps.clients.customers_preference_validation.CheckPreferenceEligibility(
        request,
        timeout=deps.settings.timeout
    )


async def on_registered_model_reporting_service_schedule_registered_model_report_0(
    deps: Dependencies,
    payload: Message
) -> Message:
    request = cast(modelregistry_v1_registered_model_sync_service_pb2.SyncRegisteredModelsRequest, payload)
    return await deps.clients.modelregistry_registered_model_sync.SyncRegisteredModels(
        request,
        timeout=deps.settings.timeout
    )


async def on_registered_model_service_update_registered_model_1(deps: Dependencies, payload: Message) -> Message:
    request = cast(modelregistry_v1_deployment_calculation_service_pb2.CalculateDeploymentRequest, payload)
    return await deps.clients.modelregistry_deployment_calculation.CalculateDeployment(
        request,
        timeout=deps.settings.timeout
    )


async def on_registered_model_validation_service_explain_registered_model_decision_0(
    deps: Dependencies,
    payload: Message
) -> Message:
    request = cast(modelregistry_v1_registered_model_calculation_service_pb2.CalculateRegisteredModelRequest, payload)
    return await deps.clients.modelregistry_registered_model_calculation.CalculateRegisteredModel(
        request,
        timeout=deps.settings.timeout
    )


async def on_registered_model_workflow_service_cancel_registered_model_workflow_0(
    deps: Dependencies,
    payload: Message
) -> Message:
    request = cast(metrics_v1_dashboard_validation_service_pb2.PreviewDashboardRequest, payload)
    return await deps.clients.metrics_dashboard_validation.PreviewDashboard(request, timeout=deps.settings.timeout)


def subscribe(deps: Dependencies) -> None:
    deps.bus.subscribe(
        'acme.modelregistry.v1.DeploymentApprovalService/DelegateDeploymentApproval/1',
        partial(on_deployment_approval_service_delegate_deployment_approval_1, deps)
    )
    deps.bus.subscribe(
        'acme.modelregistry.v1.DeploymentCalculationService/QuoteDeployment/2',
        partial(on_deployment_calculation_service_quote_deployment_2, deps)
    )
    deps.bus.subscribe(
        'acme.modelregistry.v1.DeploymentLifecycleService/SuspendDeployment/0',
        partial(on_deployment_lifecycle_service_suspend_deployment_0, deps)
    )
    deps.bus.subscribe(
        'acme.modelregistry.v1.DeploymentReportingService/ShareDeploymentReport/0',
        partial(on_deployment_reporting_service_share_deployment_report_0, deps)
    )
    deps.bus.subscribe(
        'acme.modelregistry.v1.DeploymentSyncService/StreamDeploymentChanges/2',
        partial(on_deployment_sync_service_stream_deployment_changes_2, deps)
    )
    deps.bus.subscribe(
        'acme.modelregistry.v1.DeploymentValidationService/ScoreDeployment/1',
        partial(on_deployment_validation_service_score_deployment_1, deps)
    )
    deps.bus.subscribe(
        'acme.modelregistry.v1.ModelVersionApprovalService/ApproveModelVersion/0',
        partial(on_model_version_approval_service_approve_model_version_0, deps)
    )
    deps.bus.subscribe(
        'acme.modelregistry.v1.ModelVersionLifecycleService/RenewModelVersion/1',
        partial(on_model_version_lifecycle_service_renew_model_version_1, deps)
    )
    deps.bus.subscribe(
        'acme.modelregistry.v1.ModelVersionSyncService/PullModelVersions/1',
        partial(on_model_version_sync_service_pull_model_versions_1, deps)
    )
    deps.bus.subscribe(
        'acme.modelregistry.v1.ModelVersionValidationService/CheckModelVersionEligibility/1',
        partial(on_model_version_validation_service_check_model_version_eligibility_1, deps)
    )
    deps.bus.subscribe(
        'acme.modelregistry.v1.ModelVersionValidationService/ScoreModelVersion/2',
        partial(on_model_version_validation_service_score_model_version_2, deps)
    )
    deps.bus.subscribe(
        'acme.modelregistry.v1.ModelVersionWorkflowService/RetryModelVersionWorkflow/0',
        partial(on_model_version_workflow_service_retry_model_version_workflow_0, deps)
    )
    deps.bus.subscribe(
        'acme.modelregistry.v1.RegisteredModelApprovalService/RejectRegisteredModel/1',
        partial(on_registered_model_approval_service_reject_registered_model_1, deps)
    )
    deps.bus.subscribe(
        'acme.modelregistry.v1.RegisteredModelLifecycleService/ActivateRegisteredModel/0',
        partial(on_registered_model_lifecycle_service_activate_registered_model_0, deps)
    )
    deps.bus.subscribe(
        'acme.modelregistry.v1.RegisteredModelLifecycleService/TerminateRegisteredModel/3',
        partial(on_registered_model_lifecycle_service_terminate_registered_model_3, deps)
    )
    deps.bus.subscribe(
        'acme.modelregistry.v1.RegisteredModelReportingService/ScheduleRegisteredModelReport/0',
        partial(on_registered_model_reporting_service_schedule_registered_model_report_0, deps)
    )
    deps.bus.subscribe(
        'acme.modelregistry.v1.RegisteredModelService/UpdateRegisteredModel/1',
        partial(on_registered_model_service_update_registered_model_1, deps)
    )
    deps.bus.subscribe(
        'acme.modelregistry.v1.RegisteredModelValidationService/ExplainRegisteredModelDecision/0',
        partial(on_registered_model_validation_service_explain_registered_model_decision_0, deps)
    )
    deps.bus.subscribe(
        'acme.modelregistry.v1.RegisteredModelWorkflowService/CancelRegisteredModelWorkflow/0',
        partial(on_registered_model_workflow_service_cancel_registered_model_workflow_0, deps)
    )
