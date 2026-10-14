"""Functional operations behind PipelineRunValidationService."""

from __future__ import annotations

from collections.abc import Awaitable
from collections.abc import Callable
from functools import partial
from typing import cast
import asyncio
import logging

from google.protobuf.any_pb2 import Any as AnyMessage
from google.protobuf.json_format import MessageToDict
from google.protobuf.json_format import ParseDict

from acme.anomalies.v1 import (
    anomaly_feedback_calculation_service_pb2 as anomalies_v1_anomaly_feedback_calculation_service_pb2,
)
from acme.audit.v1 import audit_event_validation_service_pb2 as audit_v1_audit_event_validation_service_pb2
from acme.careplans.v1 import care_plan_query_service_pb2 as careplans_v1_care_plan_query_service_pb2
from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.ledger.v1 import ledger_account_validation_service_pb2 as ledger_v1_ledger_account_validation_service_pb2
from acme.metrics.v1 import metric_series_export_service_pb2 as metrics_v1_metric_series_export_service_pb2
from acme.pipelines.v1 import pipeline_calculation_service_pb2 as pipelines_v1_pipeline_calculation_service_pb2
from acme.pipelines.v1 import pipeline_run_calculation_service_pb2 as pipelines_v1_pipeline_run_calculation_service_pb2
from acme.pipelines.v1 import pipeline_run_validation_service_pb2 as pipelines_v1_pipeline_run_validation_service_pb2
from acme.pipelines.v1 import (
    pipeline_step_calculation_service_pb2 as pipelines_v1_pipeline_step_calculation_service_pb2,
)
from acme.pipelines.v1 import pipeline_validation_service_pb2 as pipelines_v1_pipeline_validation_service_pb2
from acme.pipelines.v1 import pipelines_pb2 as pipelines_v1_pipelines_pb2

from acme_data.domains.pipelines import hooks
from acme_data.domains.pipelines.dependencies import Dependencies
from acme_data.domains.pipelines.models import PipelineRunValidationPreviewPipelineRun1Command
from acme_data.domains.pipelines.models import to_pipeline_run_validation_preview_pipeline_run1_command
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import run_steps
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


async def handle_check_pipeline_run_eligibility(
    deps: Dependencies,
    request: pipelines_v1_pipeline_run_validation_service_pb2.CheckPipelineRunEligibilityRequest
) -> pipelines_v1_pipeline_run_validation_service_pb2.CheckPipelineRunEligibilityResponse:
    """Checks a pipeline run."""
    response = pipelines_v1_pipeline_run_validation_service_pb2.CheckPipelineRunEligibilityResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('CheckPipelineRunEligibility', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(
            request.context.tenant_id,
            'CheckPipelineRunEligibility',
            {'reason': request.reason}
        )
        await deps.repository.save_pipeline_run(request.context.tenant_id, request.pipeline_run)
        response_0 = ledger_v1_ledger_account_validation_service_pb2.CheckLedgerAccountEligibilityResponse()
        response_1 = pipelines_v1_pipeline_run_calculation_service_pb2.ComparePipelineRunOptionsResponse()
        outgoing_0 = ledger_v1_ledger_account_validation_service_pb2.CheckLedgerAccountEligibilityRequest(
            context=request.context,
            details=ledger_v1_ledger_account_validation_service_pb2.CheckLedgerAccountEligibilityRequest.Details(
                contact=common_v1_contact_pb2.ContactInfo(
                    email=request.pipeline_run.requester.email,
                    phone=request.pipeline_run.requester.phone
                )
            )
        )
        response_0 = await deps.clients.ledger_ledger_account_validation.CheckLedgerAccountEligibility(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = pipelines_v1_pipeline_run_calculation_service_pb2.ComparePipelineRunOptionsRequest(
            context=request.context,
            pipeline_run=pipelines_v1_pipelines_pb2.PipelineRun(
                audit=common_v1_audit_pb2.AuditInfo(updated_at=request.pipeline_run.audit.updated_at),
                channel=pipelines_v1_pipelines_pb2.PipelineRunChannelOrigin(
                    address=request.pipeline_run.channel.address
                ),
                requester=common_v1_contact_pb2.ContactInfo(preferred_channel=request.details.contact.preferred_channel)
            )
        )
        response_1 = cast(pipelines_v1_pipeline_run_calculation_service_pb2.ComparePipelineRunOptionsResponse, await deps.bus.request(
            'acme.pipelines.v1.PipelineRunValidationService/CheckPipelineRunEligibility/1', outgoing_1, deps.settings.timeout,
        ))
        returned_0_0 = response_0.ledger_account.contact.preferred_channel
        if returned_0_0:
            response.pipeline_run.requester.preferred_channel = returned_0_0
        returned_0_1 = response_0.ledger_account.holder.display_name
        if returned_0_1:
            response.pipeline_run.assignee.display_name = returned_0_1
        returned_1_0 = response_1.pipeline_run.assignee
        if returned_1_0.ListFields():
            response.pipeline_run.assignee.MergeFrom(returned_1_0)
        echoed_0 = request.pipeline_run_id
        response.pipeline_run.pipeline_run_id = echoed_0
        echoed_1 = request.pipeline_run.custom_fields
        response.pipeline_run.custom_fields.update(echoed_1)
        return response


async def handle_explain_pipeline_run_decision(
    deps: Dependencies,
    request: pipelines_v1_pipeline_run_validation_service_pb2.ExplainPipelineRunDecisionRequest
) -> pipelines_v1_pipeline_run_validation_service_pb2.ExplainPipelineRunDecisionResponse:
    """Explains a pipeline run."""
    response = pipelines_v1_pipeline_run_validation_service_pb2.ExplainPipelineRunDecisionResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('ExplainPipelineRunDecision', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'ExplainPipelineRunDecision', {'reason': request.reason})
        await deps.repository.save_pipeline_run(request.context.tenant_id, request.pipeline_run)
        response_0 = pipelines_v1_pipeline_step_calculation_service_pb2.QuotePipelineStepResponse()
        response_1 = pipelines_v1_pipeline_calculation_service_pb2.ComparePipelineOptionsResponse()
        outgoing_0 = pipelines_v1_pipeline_step_calculation_service_pb2.QuotePipelineStepRequest(
            context=request.context,
            pipeline_step=pipelines_v1_pipelines_pb2.PipelineStep(
                audit=common_v1_audit_pb2.AuditInfo(created_by=request.pipeline_run.audit.created_by),
                owner=identity_v1_refs_pb2.UserRef(
                    display_name=request.pipeline_run.assignee.display_name,
                    email=request.pipeline_run.requester.email,
                    user_id=request.pipeline_run.assignee.user_id
                )
            )
        )
        response_0 = await deps.clients.pipelines_pipeline_step_calculation.QuotePipelineStep(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        for item_1 in request.pipeline_run.comments:
            outgoing_1 = pipelines_v1_pipeline_calculation_service_pb2.ComparePipelineOptionsRequest(
                context=request.context,
                pipeline=pipelines_v1_pipelines_pb2.Pipeline(
                    audit=common_v1_audit_pb2.AuditInfo(created_at=item_1.created_at),
                    participants=[
                        pipelines_v1_pipelines_pb2.PipelineParticipant(
                            contact=common_v1_contact_pb2.ContactInfo(
                                email=item_1.author_email,
                                preferred_channel=request.details.contact.preferred_channel
                            )
                        )
                    ]
                )
            )
            response_1 = await deps.clients.pipelines_pipeline_calculation.ComparePipelineOptions(
                outgoing_1,
                timeout=deps.settings.timeout
            )
        returned_0_0 = response_0.pipeline_step.audit.updated_at
        if returned_0_0.ListFields():
            response.pipeline_run.audit.updated_at.MergeFrom(returned_0_0)
        returned_0_1 = response_0.result.message
        if returned_0_1:
            response.outcome.message = returned_0_1
        echoed_0 = request.pipeline_run_id
        response.pipeline_run.pipeline_run_id = echoed_0
        echoed_1 = request.pipeline_run.status
        response.pipeline_run.status = echoed_1
        return response


async def handle_get_pipeline_run_rules(
    deps: Dependencies,
    request: pipelines_v1_pipeline_run_validation_service_pb2.GetPipelineRunRulesRequest
) -> pipelines_v1_pipeline_run_validation_service_pb2.GetPipelineRunRulesResponse:
    """Returns a pipeline run."""
    response = pipelines_v1_pipeline_run_validation_service_pb2.GetPipelineRunRulesResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('GetPipelineRunRules', extra={'fields': {'domain': 'pipelines'}})
        await deps.repository.audit(request.context.tenant_id, 'GetPipelineRunRules', {})
        response_0 = pipelines_v1_pipeline_calculation_service_pb2.RecalculatePipelinesResponse()
        response_1 = pipelines_v1_pipeline_step_calculation_service_pb2.QuotePipelineStepResponse()
        outgoing_0 = pipelines_v1_pipeline_calculation_service_pb2.RecalculatePipelinesRequest(
            context=request.context,
            pipeline=pipelines_v1_pipelines_pb2.Pipeline(
                organizer=identity_v1_refs_pb2.UserRef(user_id=request.context.actor.user_id)
            )
        )
        response_0 = await deps.clients.pipelines_pipeline_calculation.RecalculatePipelines(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = pipelines_v1_pipeline_step_calculation_service_pb2.QuotePipelineStepRequest(
            context=request.context,
            details=pipelines_v1_pipeline_step_calculation_service_pb2.QuotePipelineStepRequest.Details(
                destination=common_v1_address_pb2.PostalAddress(region=response_0.pipeline.location.region)
            )
        )
        document_1 = MessageToDict(outgoing_1, preserving_proto_field_name=True)
        outgoing_1 = ParseDict(
            document_1,
            pipelines_v1_pipeline_step_calculation_service_pb2.QuotePipelineStepRequest()
        )
        response_1 = await deps.clients.pipelines_pipeline_step_calculation.QuotePipelineStep(
            outgoing_1,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.result.message
        if returned_0_0:
            response.result.message = returned_0_0
        returned_0_1 = response_0.pipeline.organizer.email
        if returned_0_1:
            response.pipeline_run.requester.email = returned_0_1
        returned_1_0 = response_1.result.details
        response.result.details.update(returned_1_0)
        echoed_0 = request.pipeline_run_id
        response.pipeline_run.pipeline_run_id = echoed_0
        return response


async def handle_lint_pipeline_runs(
    deps: Dependencies,
    request: pipelines_v1_pipeline_run_validation_service_pb2.LintPipelineRunsRequest
) -> pipelines_v1_pipeline_run_validation_service_pb2.LintPipelineRunsResponse:
    """Lints a pipeline run."""
    response = pipelines_v1_pipeline_run_validation_service_pb2.LintPipelineRunsResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('LintPipelineRuns', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'LintPipelineRuns', {'reason': request.reason})
        await deps.repository.save_pipeline_run(request.context.tenant_id, request.pipeline_run)
        response_0 = pipelines_v1_pipeline_run_calculation_service_pb2.GetPipelineRunRatesResponse()
        response_1 = metrics_v1_metric_series_export_service_pb2.ScheduleMetricSeriesExportResponse()
        response_2 = pipelines_v1_pipeline_step_calculation_service_pb2.SimulatePipelineStepResponse()
        outgoing_0 = pipelines_v1_pipeline_run_calculation_service_pb2.GetPipelineRunRatesRequest(
            context=request.context,
            pipeline_run_id=request.pipeline_run.pipeline_run_id
        )
        response_0 = await deps.clients.pipelines_pipeline_run_calculation.GetPipelineRunRates(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = metrics_v1_metric_series_export_service_pb2.ScheduleMetricSeriesExportRequest()
        outgoing_1.context.CopyFrom(request.context)
        outgoing_1.annotations.update(dict(request.annotations))
        merged_1 = metrics_v1_metric_series_export_service_pb2.ScheduleMetricSeriesExportRequest()
        merged_1.MergeFrom(outgoing_1)
        outgoing_1.CopyFrom(merged_1)
        response_1 = await deps.clients.metrics_metric_series_export.ScheduleMetricSeriesExport(
            outgoing_1,
            timeout=deps.settings.timeout
        )
        outgoing_2 = pipelines_v1_pipeline_step_calculation_service_pb2.SimulatePipelineStepRequest(
            context=request.context,
            pipeline_step=pipelines_v1_pipelines_pb2.PipelineStep(
                audit=common_v1_audit_pb2.AuditInfo(
                    created_at=response_0.pipeline_run.audit.created_at,
                    updated_by=response_0.pipeline_run.audit.updated_by
                ),
                owner=identity_v1_refs_pb2.UserRef(
                    display_name=request.pipeline_run.customer.display_name,
                    email=request.pipeline_run.requester.email
                )
            )
        )
        envelope_2 = AnyMessage()
        envelope_2.Pack(outgoing_2)
        outgoing_2 = pipelines_v1_pipeline_step_calculation_service_pb2.SimulatePipelineStepRequest()
        if not envelope_2.Unpack(outgoing_2):
            raise ValueError("partner envelope contains the wrong request type")
        response_2 = await deps.clients.pipelines_pipeline_step_calculation.SimulatePipelineStep(
            outgoing_2,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.pipeline_run.assignee
        if returned_0_0.ListFields():
            response.pipeline_run.assignee.MergeFrom(returned_0_0)
        returned_1_0 = response_1.result.status
        if returned_1_0:
            response.outcome.status = returned_1_0
        returned_2_0 = response_2.pipeline_step.audit.updated_at
        if returned_2_0.ListFields():
            response.pipeline_run.audit.updated_at.MergeFrom(returned_2_0)
        echoed_0 = request.pipeline_run_id
        response.pipeline_run.pipeline_run_id = echoed_0
        echoed_1 = request.pipeline_run.custom_fields
        response.pipeline_run.custom_fields.update(echoed_1)
        return response


async def handle_normalize_pipeline_run(
    deps: Dependencies,
    request: pipelines_v1_pipeline_run_validation_service_pb2.NormalizePipelineRunRequest
) -> pipelines_v1_pipeline_run_validation_service_pb2.NormalizePipelineRunResponse:
    """Normalizes a pipeline run."""
    response = pipelines_v1_pipeline_run_validation_service_pb2.NormalizePipelineRunResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('NormalizePipelineRun', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'NormalizePipelineRun', {'reason': request.reason})
        await deps.repository.save_pipeline_run(request.context.tenant_id, request.pipeline_run)
        response_0 = audit_v1_audit_event_validation_service_pb2.LintAuditEventsResponse()
        outgoing_0 = audit_v1_audit_event_validation_service_pb2.LintAuditEventsRequest(
            context=request.context,
            details=audit_v1_audit_event_validation_service_pb2.LintAuditEventsRequest.Details(
                contact=common_v1_contact_pb2.ContactInfo(
                    email=request.details.contact.email,
                    phone=request.details.contact.phone
                )
            )
        )
        response_0 = await deps.clients.audit_audit_event_validation.LintAuditEvents(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.outcome.message
        if returned_0_0:
            response.result.message = returned_0_0
        echoed_0 = request.pipeline_run_id
        response.pipeline_run.pipeline_run_id = echoed_0
        echoed_1 = request.pipeline_run.custom_fields
        response.pipeline_run.custom_fields.update(echoed_1)
        return response


async def handle_preview_pipeline_run(
    deps: Dependencies,
    request: pipelines_v1_pipeline_run_validation_service_pb2.PreviewPipelineRunRequest
) -> pipelines_v1_pipeline_run_validation_service_pb2.PreviewPipelineRunResponse:
    """Previews a pipeline run."""
    response = pipelines_v1_pipeline_run_validation_service_pb2.PreviewPipelineRunResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('PreviewPipelineRun', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'PreviewPipelineRun', {'reason': request.reason})
        await deps.repository.save_pipeline_run(request.context.tenant_id, request.pipeline_run)
        response_0 = pipelines_v1_pipeline_step_calculation_service_pb2.ComparePipelineStepOptionsResponse()
        response_1 = careplans_v1_care_plan_query_service_pb2.CountCarePlansResponse()
        outgoing_0 = pipelines_v1_pipeline_step_calculation_service_pb2.ComparePipelineStepOptionsRequest(
            context=request.context,
            pipeline_step=pipelines_v1_pipelines_pb2.PipelineStep(
                owner=identity_v1_refs_pb2.UserRef(email=request.details.contact.email)
            )
        )
        response_0 = await deps.clients.pipelines_pipeline_step_calculation.ComparePipelineStepOptions(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        command_1 = PipelineRunValidationPreviewPipelineRun1Command.model_validate(
            {
                'context': request.context,
                'filter_created_after': request.pipeline_run.audit.updated_at,
                'filter_owner_id': response_0.pipeline_step.owner.user_id
            }
        )
        outgoing_1 = to_pipeline_run_validation_preview_pipeline_run1_command(command_1)
        response_1 = await deps.clients.careplans_care_plan_query.CountCarePlans(
            outgoing_1,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.result.message
        if returned_0_0:
            response.outcome.message = returned_0_0
        returned_1_0 = response_1.result.reference_ids
        response.result.reference_ids.extend(returned_1_0)
        echoed_0 = request.pipeline_run_id
        response.pipeline_run.pipeline_run_id = echoed_0
        echoed_1 = request.pipeline_run.assignee
        response.pipeline_run.assignee.CopyFrom(echoed_1)
        return response


async def handle_score_pipeline_run(
    deps: Dependencies,
    request: pipelines_v1_pipeline_run_validation_service_pb2.ScorePipelineRunRequest
) -> pipelines_v1_pipeline_run_validation_service_pb2.ScorePipelineRunResponse:
    """Scores a pipeline run."""
    response = pipelines_v1_pipeline_run_validation_service_pb2.ScorePipelineRunResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('ScorePipelineRun', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'ScorePipelineRun', {'reason': request.reason})
        await deps.repository.save_pipeline_run(request.context.tenant_id, request.pipeline_run)
        response_0 = anomalies_v1_anomaly_feedback_calculation_service_pb2.CompareAnomalyFeedbackOptionsResponse()
        response_1 = pipelines_v1_pipeline_step_calculation_service_pb2.EstimatePipelineStepResponse()
        outgoing_0 = anomalies_v1_anomaly_feedback_calculation_service_pb2.CompareAnomalyFeedbackOptionsRequest(
            context=request.context,
            details=anomalies_v1_anomaly_feedback_calculation_service_pb2.CompareAnomalyFeedbackOptionsRequest.Details(
                destination=common_v1_address_pb2.PostalAddress(
                    locality=request.details.destination.locality,
                    region=request.details.destination.region
                )
            )
        )
        response_0 = await deps.clients.anomalies_anomaly_feedback_calculation.CompareAnomalyFeedbackOptions(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = pipelines_v1_pipeline_step_calculation_service_pb2.EstimatePipelineStepRequest(
            context=request.context,
            pipeline_step=pipelines_v1_pipelines_pb2.PipelineStep(
                audit=common_v1_audit_pb2.AuditInfo(etag=request.pipeline_run.audit.etag)
            )
        )
        response_1 = await hooks.pipeline_run_validation_score_pipeline_run1(
            deps.clients.pipelines_pipeline_step_calculation,
            outgoing_1,
            deps.settings.timeout
        )
        returned_0_0 = response_0.anomaly_feedback.subject.display_name
        if returned_0_0:
            response.pipeline_run.assignee.display_name = returned_0_0
        returned_1_0 = response_1.pipeline_step.audit.updated_at
        if returned_1_0.ListFields():
            response.pipeline_run.audit.updated_at.MergeFrom(returned_1_0)
        echoed_0 = request.pipeline_run_id
        response.pipeline_run.pipeline_run_id = echoed_0
        echoed_1 = request.pipeline_run.subject
        response.pipeline_run.subject = echoed_1
        return response


async def handle_validate_pipeline_run(
    deps: Dependencies,
    request: pipelines_v1_pipeline_run_validation_service_pb2.ValidatePipelineRunRequest
) -> pipelines_v1_pipeline_run_validation_service_pb2.ValidatePipelineRunResponse:
    """Validates a pipeline run."""
    response = pipelines_v1_pipeline_run_validation_service_pb2.ValidatePipelineRunResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('ValidatePipelineRun', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'ValidatePipelineRun', {'reason': request.reason})
        await deps.repository.save_pipeline_run(request.context.tenant_id, request.pipeline_run)
        response_0 = pipelines_v1_pipeline_step_calculation_service_pb2.EstimatePipelineStepResponse()
        response_1 = pipelines_v1_pipeline_step_calculation_service_pb2.QuotePipelineStepResponse()
        response_2 = pipelines_v1_pipeline_validation_service_pb2.ScorePipelineResponse()
        requests_0: list[pipelines_v1_pipeline_step_calculation_service_pb2.EstimatePipelineStepRequest] = []
        for item_0 in request.pipeline_run.comments:
            outgoing_0 = pipelines_v1_pipeline_step_calculation_service_pb2.EstimatePipelineStepRequest(
                context=request.context,
                pipeline_step=pipelines_v1_pipelines_pb2.PipelineStep(
                    block=pipelines_v1_pipelines_pb2.PipelineStepBlockAction(notify_email=item_0.author_email)
                )
            )
            requests_0.append(outgoing_0)
        replies_0 = await asyncio.gather(*(
            deps.clients.pipelines_pipeline_step_calculation.EstimatePipelineStep(
                entry,
                timeout=deps.settings.timeout
            ) for entry in requests_0
        ))
        if replies_0:
            response_0 = replies_0[-1]
        callbacks_1: list[
            Callable[[], Awaitable[pipelines_v1_pipeline_step_calculation_service_pb2.QuotePipelineStepResponse]]
        ] = []
        for item_1 in request.pipeline_run.comments:
            outgoing_1 = pipelines_v1_pipeline_step_calculation_service_pb2.QuotePipelineStepRequest(
                context=request.context,
                pipeline_step=pipelines_v1_pipelines_pb2.PipelineStep(
                    audit=common_v1_audit_pb2.AuditInfo(created_at=item_1.created_at),
                    block=pipelines_v1_pipelines_pb2.PipelineStepBlockAction(
                        notify_email=response_0.pipeline_step.block.notify_email
                    ),
                    owner=identity_v1_refs_pb2.UserRef(email=item_1.author_email)
                )
            )
            async def send_1(
                payload: pipelines_v1_pipeline_step_calculation_service_pb2.QuotePipelineStepRequest = outgoing_1
            ) -> pipelines_v1_pipeline_step_calculation_service_pb2.QuotePipelineStepResponse:
                return await deps.clients.pipelines_pipeline_step_calculation.QuotePipelineStep(
                    payload,
                    timeout=deps.settings.timeout
                )
            callbacks_1.append(send_1)
        for callback_1 in callbacks_1:
            response_1 = await callback_1()
        outgoing_2 = pipelines_v1_pipeline_validation_service_pb2.ScorePipelineRequest(
            context=request.context,
            pipeline=pipelines_v1_pipelines_pb2.Pipeline(
                participants=[
                    pipelines_v1_pipelines_pb2.PipelineParticipant(
                        contact=common_v1_contact_pb2.ContactInfo(
                            email=response_1.pipeline_step.owner.email,
                            name=request.details.contact.name,
                            phone=request.details.contact.phone,
                            preferred_channel=request.details.contact.preferred_channel
                        )
                    )
                ]
            )
        )
        steps_2 = [
            partial(deps.clients.pipelines_pipeline_validation.ScorePipeline, outgoing_2, timeout=deps.settings.timeout)
        ]
        results_2 = await run_steps(steps_2)
        response_2 = results_2[-1]
        returned_2_0 = response_2.pipeline.audit.updated_at
        if returned_2_0.ListFields():
            response.pipeline_run.audit.updated_at.MergeFrom(returned_2_0)
        echoed_0 = request.pipeline_run_id
        response.pipeline_run.pipeline_run_id = echoed_0
        echoed_1 = request.pipeline_run.subject
        response.pipeline_run.subject = echoed_1
        return response
