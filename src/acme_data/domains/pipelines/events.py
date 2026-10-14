"""Background event handlers owned by the pipelines team."""

from __future__ import annotations

from functools import partial
from typing import cast

from google.protobuf.message import Message

from acme.authorization.v1 import access_policy_service_pb2 as authorization_v1_access_policy_service_pb2
from acme.featureflags.v1 import (
    feature_flag_validation_service_pb2 as featureflags_v1_feature_flag_validation_service_pb2,
)
from acme.helpdesk.v1 import ticket_service_pb2 as helpdesk_v1_ticket_service_pb2
from acme.labeling.v1 import label_set_sync_service_pb2 as labeling_v1_label_set_sync_service_pb2
from acme.metrics.v1 import metric_series_service_pb2 as metrics_v1_metric_series_service_pb2
from acme.pipelines.v1 import pipeline_approval_service_pb2 as pipelines_v1_pipeline_approval_service_pb2
from acme.pipelines.v1 import pipeline_calculation_service_pb2 as pipelines_v1_pipeline_calculation_service_pb2
from acme.pipelines.v1 import pipeline_query_service_pb2 as pipelines_v1_pipeline_query_service_pb2
from acme.pipelines.v1 import pipeline_reporting_service_pb2 as pipelines_v1_pipeline_reporting_service_pb2
from acme.pipelines.v1 import pipeline_run_calculation_service_pb2 as pipelines_v1_pipeline_run_calculation_service_pb2
from acme.pipelines.v1 import pipeline_run_import_service_pb2 as pipelines_v1_pipeline_run_import_service_pb2
from acme.pipelines.v1 import pipeline_run_lifecycle_service_pb2 as pipelines_v1_pipeline_run_lifecycle_service_pb2
from acme.pipelines.v1 import pipeline_step_import_service_pb2 as pipelines_v1_pipeline_step_import_service_pb2
from acme.pipelines.v1 import pipeline_step_validation_service_pb2 as pipelines_v1_pipeline_step_validation_service_pb2
from acme.pipelines.v1 import pipeline_validation_service_pb2 as pipelines_v1_pipeline_validation_service_pb2
from acme.venues.v1 import venue_service_pb2 as venues_v1_venue_service_pb2

from acme_data.domains.pipelines.dependencies import Dependencies


async def on_pipeline_approval_service_delegate_pipeline_approval_3(deps: Dependencies, payload: Message) -> Message:
    request = cast(pipelines_v1_pipeline_run_import_service_pb2.ValidatePipelineRunImportRequest, payload)
    return await deps.clients.pipelines_pipeline_run_import.ValidatePipelineRunImport(
        request,
        timeout=deps.settings.timeout
    )


async def on_pipeline_calculation_service_compare_pipeline_options_1(deps: Dependencies, payload: Message) -> Message:
    request = cast(metrics_v1_metric_series_service_pb2.CloneMetricSeriesRequest, payload)
    return await deps.clients.metrics_metric_series.CloneMetricSeries(request, timeout=deps.settings.timeout)


async def on_pipeline_query_service_find_pipelines_1(deps: Dependencies, payload: Message) -> Message:
    request = cast(pipelines_v1_pipeline_validation_service_pb2.ValidatePipelineRequest, payload)
    return await deps.clients.pipelines_pipeline_validation.ValidatePipeline(request, timeout=deps.settings.timeout)


async def on_pipeline_reporting_service_share_pipeline_report_1(deps: Dependencies, payload: Message) -> Message:
    request = cast(pipelines_v1_pipeline_step_validation_service_pb2.ExplainPipelineStepDecisionRequest, payload)
    return await deps.clients.pipelines_pipeline_step_validation.ExplainPipelineStepDecision(
        request,
        timeout=deps.settings.timeout
    )


async def on_pipeline_run_calculation_service_explain_pipeline_run_calculation_1(
    deps: Dependencies,
    payload: Message
) -> Message:
    request = cast(pipelines_v1_pipeline_calculation_service_pb2.ComparePipelineOptionsRequest, payload)
    return await deps.clients.pipelines_pipeline_calculation.ComparePipelineOptions(
        request,
        timeout=deps.settings.timeout
    )


async def on_pipeline_run_lifecycle_service_activate_pipeline_run_0(deps: Dependencies, payload: Message) -> Message:
    request = cast(pipelines_v1_pipeline_step_import_service_pb2.ValidatePipelineStepImportRequest, payload)
    return await deps.clients.pipelines_pipeline_step_import.ValidatePipelineStepImport(
        request,
        timeout=deps.settings.timeout
    )


async def on_pipeline_run_lifecycle_service_terminate_pipeline_run_2(deps: Dependencies, payload: Message) -> Message:
    request = cast(venues_v1_venue_service_pb2.SearchVenuesRequest, payload)
    return await deps.clients.venues_venue.SearchVenues(request, timeout=deps.settings.timeout)


async def on_pipeline_run_reporting_service_stream_pipeline_run_metrics_0(
    deps: Dependencies,
    payload: Message
) -> Message:
    request = cast(labeling_v1_label_set_sync_service_pb2.ListLabelSetConflictsRequest, payload)
    return await deps.clients.labeling_label_set_sync.ListLabelSetConflicts(request, timeout=deps.settings.timeout)


async def on_pipeline_run_validation_service_check_pipeline_run_eligibility_1(
    deps: Dependencies,
    payload: Message
) -> Message:
    request = cast(pipelines_v1_pipeline_run_calculation_service_pb2.ComparePipelineRunOptionsRequest, payload)
    return await deps.clients.pipelines_pipeline_run_calculation.ComparePipelineRunOptions(
        request,
        timeout=deps.settings.timeout
    )


async def on_pipeline_run_workflow_service_advance_pipeline_run_workflow_1(
    deps: Dependencies,
    payload: Message
) -> Message:
    request = cast(pipelines_v1_pipeline_approval_service_pb2.EscalatePipelineRequest, payload)
    return await deps.clients.pipelines_pipeline_approval.EscalatePipeline(request, timeout=deps.settings.timeout)


async def on_pipeline_step_calculation_service_compare_pipeline_step_options_0(
    deps: Dependencies,
    payload: Message
) -> Message:
    request = cast(pipelines_v1_pipeline_calculation_service_pb2.ComparePipelineOptionsRequest, payload)
    return await deps.clients.pipelines_pipeline_calculation.ComparePipelineOptions(
        request,
        timeout=deps.settings.timeout
    )


async def on_pipeline_step_export_service_cancel_pipeline_step_export_1(
    deps: Dependencies,
    payload: Message
) -> Message:
    request = cast(pipelines_v1_pipeline_query_service_pb2.BrowsePipelinesRequest, payload)
    return await deps.clients.pipelines_pipeline_query.BrowsePipelines(request, timeout=deps.settings.timeout)


async def on_pipeline_step_export_service_stream_pipeline_step_export_3(
    deps: Dependencies,
    payload: Message
) -> Message:
    request = cast(featureflags_v1_feature_flag_validation_service_pb2.PreviewFeatureFlagRequest, payload)
    return await deps.clients.featureflags_feature_flag_validation.PreviewFeatureFlag(
        request,
        timeout=deps.settings.timeout
    )


async def on_pipeline_step_lifecycle_service_terminate_pipeline_step_0(deps: Dependencies, payload: Message) -> Message:
    request = cast(helpdesk_v1_ticket_service_pb2.CreateTicketRequest, payload)
    return await deps.clients.helpdesk_ticket.CreateTicket(request, timeout=deps.settings.timeout)


async def on_pipeline_step_sync_service_pull_pipeline_steps_1(deps: Dependencies, payload: Message) -> Message:
    request = cast(pipelines_v1_pipeline_reporting_service_pb2.SchedulePipelineReportRequest, payload)
    return await deps.clients.pipelines_pipeline_reporting.SchedulePipelineReport(
        request,
        timeout=deps.settings.timeout
    )


async def on_pipeline_step_workflow_service_signal_pipeline_step_workflow_0(
    deps: Dependencies,
    payload: Message
) -> Message:
    request = cast(pipelines_v1_pipeline_run_lifecycle_service_pb2.SchedulePipelineRunExpiryRequest, payload)
    return await deps.clients.pipelines_pipeline_run_lifecycle.SchedulePipelineRunExpiry(
        request,
        timeout=deps.settings.timeout
    )


async def on_pipeline_sync_service_stream_pipeline_changes_0(deps: Dependencies, payload: Message) -> Message:
    request = cast(pipelines_v1_pipeline_query_service_pb2.ResolvePipelinesRequest, payload)
    return await deps.clients.pipelines_pipeline_query.ResolvePipelines(request, timeout=deps.settings.timeout)


async def on_pipeline_workflow_service_retry_pipeline_workflow_1(deps: Dependencies, payload: Message) -> Message:
    request = cast(authorization_v1_access_policy_service_pb2.CreateAccessPolicyRequest, payload)
    return await deps.clients.authorization_access_policy.CreateAccessPolicy(request, timeout=deps.settings.timeout)


def subscribe(deps: Dependencies) -> None:
    deps.bus.subscribe(
        'acme.pipelines.v1.PipelineApprovalService/DelegatePipelineApproval/3',
        partial(on_pipeline_approval_service_delegate_pipeline_approval_3, deps)
    )
    deps.bus.subscribe(
        'acme.pipelines.v1.PipelineCalculationService/ComparePipelineOptions/1',
        partial(on_pipeline_calculation_service_compare_pipeline_options_1, deps)
    )
    deps.bus.subscribe(
        'acme.pipelines.v1.PipelineQueryService/FindPipelines/1',
        partial(on_pipeline_query_service_find_pipelines_1, deps)
    )
    deps.bus.subscribe(
        'acme.pipelines.v1.PipelineReportingService/SharePipelineReport/1',
        partial(on_pipeline_reporting_service_share_pipeline_report_1, deps)
    )
    deps.bus.subscribe(
        'acme.pipelines.v1.PipelineRunCalculationService/ExplainPipelineRunCalculation/1',
        partial(on_pipeline_run_calculation_service_explain_pipeline_run_calculation_1, deps)
    )
    deps.bus.subscribe(
        'acme.pipelines.v1.PipelineRunLifecycleService/ActivatePipelineRun/0',
        partial(on_pipeline_run_lifecycle_service_activate_pipeline_run_0, deps)
    )
    deps.bus.subscribe(
        'acme.pipelines.v1.PipelineRunLifecycleService/TerminatePipelineRun/2',
        partial(on_pipeline_run_lifecycle_service_terminate_pipeline_run_2, deps)
    )
    deps.bus.subscribe(
        'acme.pipelines.v1.PipelineRunReportingService/StreamPipelineRunMetrics/0',
        partial(on_pipeline_run_reporting_service_stream_pipeline_run_metrics_0, deps)
    )
    deps.bus.subscribe(
        'acme.pipelines.v1.PipelineRunValidationService/CheckPipelineRunEligibility/1',
        partial(on_pipeline_run_validation_service_check_pipeline_run_eligibility_1, deps)
    )
    deps.bus.subscribe(
        'acme.pipelines.v1.PipelineRunWorkflowService/AdvancePipelineRunWorkflow/1',
        partial(on_pipeline_run_workflow_service_advance_pipeline_run_workflow_1, deps)
    )
    deps.bus.subscribe(
        'acme.pipelines.v1.PipelineStepCalculationService/ComparePipelineStepOptions/0',
        partial(on_pipeline_step_calculation_service_compare_pipeline_step_options_0, deps)
    )
    deps.bus.subscribe(
        'acme.pipelines.v1.PipelineStepExportService/CancelPipelineStepExport/1',
        partial(on_pipeline_step_export_service_cancel_pipeline_step_export_1, deps)
    )
    deps.bus.subscribe(
        'acme.pipelines.v1.PipelineStepExportService/StreamPipelineStepExport/3',
        partial(on_pipeline_step_export_service_stream_pipeline_step_export_3, deps)
    )
    deps.bus.subscribe(
        'acme.pipelines.v1.PipelineStepLifecycleService/TerminatePipelineStep/0',
        partial(on_pipeline_step_lifecycle_service_terminate_pipeline_step_0, deps)
    )
    deps.bus.subscribe(
        'acme.pipelines.v1.PipelineStepSyncService/PullPipelineSteps/1',
        partial(on_pipeline_step_sync_service_pull_pipeline_steps_1, deps)
    )
    deps.bus.subscribe(
        'acme.pipelines.v1.PipelineStepWorkflowService/SignalPipelineStepWorkflow/0',
        partial(on_pipeline_step_workflow_service_signal_pipeline_step_workflow_0, deps)
    )
    deps.bus.subscribe(
        'acme.pipelines.v1.PipelineSyncService/StreamPipelineChanges/0',
        partial(on_pipeline_sync_service_stream_pipeline_changes_0, deps)
    )
    deps.bus.subscribe(
        'acme.pipelines.v1.PipelineWorkflowService/RetryPipelineWorkflow/1',
        partial(on_pipeline_workflow_service_retry_pipeline_workflow_1, deps)
    )
