"""Functional operations behind PipelineStepValidationService."""

from __future__ import annotations

from collections.abc import Awaitable
from collections.abc import Callable
from typing import Any
import asyncio
import logging

from google.protobuf.any_pb2 import Any as AnyMessage
from google.protobuf.json_format import MessageToDict
from google.protobuf.json_format import ParseDict

from acme.audit.v1 import audit_event_validation_service_pb2 as audit_v1_audit_event_validation_service_pb2
from acme.audit.v1 import audit_pb2 as audit_v1_audit_pb2
from acme.audit.v1 import refs_pb2 as audit_v1_refs_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.documents.v1 import document_query_service_pb2 as documents_v1_document_query_service_pb2
from acme.documents.v1 import document_service_pb2 as documents_v1_document_service_pb2
from acme.fleet.v1 import vehicle_service_pb2 as fleet_v1_vehicle_service_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.ledger.v1 import ledger_account_query_service_pb2 as ledger_v1_ledger_account_query_service_pb2
from acme.pipelines.v1 import pipeline_run_validation_service_pb2 as pipelines_v1_pipeline_run_validation_service_pb2
from acme.pipelines.v1 import (
    pipeline_step_calculation_service_pb2 as pipelines_v1_pipeline_step_calculation_service_pb2,
)
from acme.pipelines.v1 import pipeline_step_validation_service_pb2 as pipelines_v1_pipeline_step_validation_service_pb2
from acme.pipelines.v1 import pipeline_validation_service_pb2 as pipelines_v1_pipeline_validation_service_pb2
from acme.pipelines.v1 import pipelines_pb2 as pipelines_v1_pipelines_pb2
from acme.prescriptions.v1 import prescription_query_service_pb2 as prescriptions_v1_prescription_query_service_pb2
from acme.routing.v1 import route_service_pb2 as routing_v1_route_service_pb2
from acme.yards.v1 import yard_query_service_pb2 as yards_v1_yard_query_service_pb2

from acme_data.domains.pipelines import hooks
from acme_data.domains.pipelines.adapters import PipelineStepValidationLintPipelineSteps1Adapter
from acme_data.domains.pipelines.dependencies import Dependencies
from acme_data.platform.rpc import async_messages
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


async def handle_check_pipeline_step_eligibility(
    deps: Dependencies,
    request: pipelines_v1_pipeline_step_validation_service_pb2.CheckPipelineStepEligibilityRequest
) -> pipelines_v1_pipeline_step_validation_service_pb2.CheckPipelineStepEligibilityResponse:
    """Checks a pipeline step."""
    response = pipelines_v1_pipeline_step_validation_service_pb2.CheckPipelineStepEligibilityResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('CheckPipelineStepEligibility', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(
            request.context.tenant_id,
            'CheckPipelineStepEligibility',
            {'reason': request.reason}
        )
        await deps.repository.save_pipeline_step(request.context.tenant_id, request.pipeline_step)
        response_0 = pipelines_v1_pipeline_step_calculation_service_pb2.SimulatePipelineStepResponse()
        response_1 = documents_v1_document_service_pb2.WatchDocumentsResponse()
        response_2 = prescriptions_v1_prescription_query_service_pb2.BrowsePrescriptionsResponse()
        outgoing_0 = pipelines_v1_pipeline_step_calculation_service_pb2.SimulatePipelineStepRequest(
            context=request.context,
            pipeline_step=pipelines_v1_pipelines_pb2.PipelineStep(
                audit=common_v1_audit_pb2.AuditInfo(updated_by=request.pipeline_step.audit.updated_by),
                owner=identity_v1_refs_pb2.UserRef(
                    email=request.details.contact.email,
                    user_id=request.pipeline_step.owner.user_id
                ),
                route=pipelines_v1_pipelines_pb2.PipelineStepRouteAction(target=request.pipeline_step.route.target)
            )
        )
        response_0 = await deps.clients.pipelines_pipeline_step_calculation.SimulatePipelineStep(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = documents_v1_document_service_pb2.WatchDocumentsRequest(
            context=request.context,
            subscriber=common_v1_contact_pb2.ContactInfo(phone=request.details.contact.phone)
        )
        async for chunk_1 in deps.clients.documents_document.WatchDocuments(outgoing_1, timeout=deps.settings.timeout):
            response_1 = chunk_1
        outgoing_2 = prescriptions_v1_prescription_query_service_pb2.BrowsePrescriptionsRequest(
            context=request.context,
            filter=prescriptions_v1_prescription_query_service_pb2.BrowsePrescriptionsRequest.Filter(
                created_after=response_0.pipeline_step.audit.created_at
            )
        )
        response_2 = await hooks.pipeline_step_validation_check_pipeline_step_eligibility2(
            deps.clients.prescriptions_prescription_query,
            outgoing_2,
            deps.settings.timeout
        )
        returned_0_0 = response_0.result.status
        if returned_0_0:
            response.outcome.status = returned_0_0
        returned_2_0 = response_2.result.message
        if returned_2_0:
            response.outcome.message = returned_2_0
        returned_2_1 = response_2.result.correlation_id
        if returned_2_1:
            response.result.correlation_id = returned_2_1
        echoed_0 = request.pipeline_step_id
        response.pipeline_step.pipeline_step_id = echoed_0
        echoed_1 = request.pipeline_step.owner
        response.pipeline_step.owner.CopyFrom(echoed_1)
        return response


async def handle_explain_pipeline_step_decision(
    deps: Dependencies,
    request: pipelines_v1_pipeline_step_validation_service_pb2.ExplainPipelineStepDecisionRequest
) -> pipelines_v1_pipeline_step_validation_service_pb2.ExplainPipelineStepDecisionResponse:
    """Explains a pipeline step."""
    response = pipelines_v1_pipeline_step_validation_service_pb2.ExplainPipelineStepDecisionResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('ExplainPipelineStepDecision', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(
            request.context.tenant_id,
            'ExplainPipelineStepDecision',
            {'reason': request.reason}
        )
        await deps.repository.save_pipeline_step(request.context.tenant_id, request.pipeline_step)
        response_0 = pipelines_v1_pipeline_step_calculation_service_pb2.QuotePipelineStepResponse()
        outgoing_0 = pipelines_v1_pipeline_step_calculation_service_pb2.QuotePipelineStepRequest(
            context=request.context,
            pipeline_step=pipelines_v1_pipelines_pb2.PipelineStep(
                audit=common_v1_audit_pb2.AuditInfo(created_by=request.pipeline_step.audit.created_by),
                owner=identity_v1_refs_pb2.UserRef(display_name=request.pipeline_step.owner.display_name)
            )
        )
        response_0 = await deps.clients.pipelines_pipeline_step_calculation.QuotePipelineStep(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.result.correlation_id
        if returned_0_0:
            response.result.correlation_id = returned_0_0
        echoed_0 = request.pipeline_step_id
        response.pipeline_step.pipeline_step_id = echoed_0
        echoed_1 = request.pipeline_step.version
        response.pipeline_step.version = echoed_1
        return response


async def handle_get_pipeline_step_rules(
    deps: Dependencies,
    request: pipelines_v1_pipeline_step_validation_service_pb2.GetPipelineStepRulesRequest
) -> pipelines_v1_pipeline_step_validation_service_pb2.GetPipelineStepRulesResponse:
    """Returns a pipeline step."""
    response = pipelines_v1_pipeline_step_validation_service_pb2.GetPipelineStepRulesResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('GetPipelineStepRules', extra={'fields': {'domain': 'pipelines'}})
        await deps.repository.audit(request.context.tenant_id, 'GetPipelineStepRules', {})
        response_0 = ledger_v1_ledger_account_query_service_pb2.ResolveLedgerAccountsResponse()
        outgoing_0 = ledger_v1_ledger_account_query_service_pb2.ResolveLedgerAccountsRequest(context=request.context)
        response_0 = await deps.clients.ledger_ledger_account_query.ResolveLedgerAccounts(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.result.status
        if returned_0_0:
            response.result.status = returned_0_0
        returned_0_1 = response_0.result.reference_ids
        response.result.reference_ids.extend(returned_0_1)
        echoed_0 = request.pipeline_step_id
        response.pipeline_step.pipeline_step_id = echoed_0
        return response


async def handle_lint_pipeline_steps(
    deps: Dependencies,
    request: pipelines_v1_pipeline_step_validation_service_pb2.LintPipelineStepsRequest
) -> pipelines_v1_pipeline_step_validation_service_pb2.LintPipelineStepsResponse:
    """Lints a pipeline step."""
    response = pipelines_v1_pipeline_step_validation_service_pb2.LintPipelineStepsResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('LintPipelineSteps', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'LintPipelineSteps', {'reason': request.reason})
        await deps.repository.save_pipeline_step(request.context.tenant_id, request.pipeline_step)
        response_0 = pipelines_v1_pipeline_run_validation_service_pb2.CheckPipelineRunEligibilityResponse()
        response_1 = yards_v1_yard_query_service_pb2.BrowseYardsResponse()
        response_2 = documents_v1_document_query_service_pb2.ExportDocumentsResponse()
        response_3 = pipelines_v1_pipeline_validation_service_pb2.ScorePipelineResponse()
        outgoing_0 = pipelines_v1_pipeline_run_validation_service_pb2.CheckPipelineRunEligibilityRequest(
            context=request.context,
            details=pipelines_v1_pipeline_run_validation_service_pb2.CheckPipelineRunEligibilityRequest.Details(
                contact=common_v1_contact_pb2.ContactInfo(name=request.details.contact.name)
            )
        )
        response_0 = await deps.clients.pipelines_pipeline_run_validation.CheckPipelineRunEligibility(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = yards_v1_yard_query_service_pb2.BrowseYardsRequest(
            context=request.context,
            filter=yards_v1_yard_query_service_pb2.BrowseYardsRequest.Filter(
                created_after=request.pipeline_step.audit.updated_at
            )
        )
        response_1 = await PipelineStepValidationLintPipelineSteps1Adapter(
            deps.clients.yards_yard_query,
            deps.settings.timeout
        )(outgoing_1)
        outgoing_2 = documents_v1_document_query_service_pb2.ExportDocumentsRequest(
            context=request.context,
            filter=documents_v1_document_query_service_pb2.ExportDocumentsRequest.Filter(
                created_after=response_0.pipeline_run.sla.due_at
            )
        )
        async for chunk_2 in deps.clients.documents_document_query.ExportDocuments(
            outgoing_2,
            timeout=deps.settings.timeout
        ):
            response_2 = chunk_2
        outgoing_3 = pipelines_v1_pipeline_validation_service_pb2.ScorePipelineRequest(
            context=request.context,
            pipeline=pipelines_v1_pipelines_pb2.Pipeline(
                organizer=identity_v1_refs_pb2.UserRef(
                    email=response_0.pipeline_run.assignee.email,
                    user_id=request.pipeline_step.owner.user_id
                ),
                participants=[
                    pipelines_v1_pipelines_pb2.PipelineParticipant(
                        contact=common_v1_contact_pb2.ContactInfo(phone=response_0.pipeline_run.requester.phone)
                    )
                ]
            )
        )
        response_3 = await deps.clients.pipelines_pipeline_validation.ScorePipeline(
            outgoing_3,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.outcome.status
        if returned_0_0:
            response.outcome.status = returned_0_0
        returned_1_0 = response_1.result.status
        if returned_1_0:
            response.outcome.status = returned_1_0
        returned_1_1 = response_1.result.message
        if returned_1_1:
            response.result.message = returned_1_1
        returned_3_0 = response_3.pipeline.organizer.email
        if returned_3_0:
            response.pipeline_step.owner.email = returned_3_0
        returned_3_1 = response_3.result.status
        if returned_3_1:
            response.result.status = returned_3_1
        echoed_0 = request.pipeline_step_id
        response.pipeline_step.pipeline_step_id = echoed_0
        echoed_1 = request.pipeline_step.name
        response.pipeline_step.name = echoed_1
        return response


async def handle_normalize_pipeline_step(
    deps: Dependencies,
    request: pipelines_v1_pipeline_step_validation_service_pb2.NormalizePipelineStepRequest
) -> pipelines_v1_pipeline_step_validation_service_pb2.NormalizePipelineStepResponse:
    """Normalizes a pipeline step."""
    response = pipelines_v1_pipeline_step_validation_service_pb2.NormalizePipelineStepResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('NormalizePipelineStep', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'NormalizePipelineStep', {'reason': request.reason})
        await deps.repository.save_pipeline_step(request.context.tenant_id, request.pipeline_step)
        response_0 = pipelines_v1_pipeline_step_calculation_service_pb2.QuotePipelineStepResponse()
        response_1 = pipelines_v1_pipeline_validation_service_pb2.NormalizePipelineResponse()
        response_2 = pipelines_v1_pipeline_step_calculation_service_pb2.ComparePipelineStepOptionsResponse()
        response_3 = pipelines_v1_pipeline_step_calculation_service_pb2.SimulatePipelineStepResponse()
        outgoing_0 = pipelines_v1_pipeline_step_calculation_service_pb2.QuotePipelineStepRequest(
            context=request.context,
            pipeline_step=pipelines_v1_pipelines_pb2.PipelineStep(
                discount=pipelines_v1_pipelines_pb2.PipelineStepDiscountAction(
                    percent=request.pipeline_step.discount.percent
                ),
                owner=identity_v1_refs_pb2.UserRef(display_name=request.pipeline_step.owner.display_name)
            )
        )
        response_0 = await deps.clients.pipelines_pipeline_step_calculation.QuotePipelineStep(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        fields_1: dict[str, Any] = {
            'context': request.context,
            'pipeline': {'participants': [{'contact': {'email': response_0.pipeline_step.owner.email}}]}
        }
        outgoing_1 = pipelines_v1_pipeline_validation_service_pb2.NormalizePipelineRequest(**fields_1)
        response_1 = await deps.clients.pipelines_pipeline_validation.NormalizePipeline(
            outgoing_1,
            timeout=deps.settings.timeout
        )
        outgoing_2 = pipelines_v1_pipeline_step_calculation_service_pb2.ComparePipelineStepOptionsRequest(
            context=request.context,
            pipeline_step=pipelines_v1_pipelines_pb2.PipelineStep(
                audit=common_v1_audit_pb2.AuditInfo(
                    created_at=response_0.pipeline_step.audit.created_at,
                    created_by=request.pipeline_step.audit.created_by
                ),
                discount=pipelines_v1_pipelines_pb2.PipelineStepDiscountAction(
                    percent=request.pipeline_step.discount.percent
                ),
                owner=identity_v1_refs_pb2.UserRef(display_name=response_1.pipeline.organizer.display_name)
            )
        )
        document_2 = MessageToDict(outgoing_2, preserving_proto_field_name=True)
        outgoing_2 = ParseDict(
            document_2,
            pipelines_v1_pipeline_step_calculation_service_pb2.ComparePipelineStepOptionsRequest()
        )
        response_2 = await deps.clients.pipelines_pipeline_step_calculation.ComparePipelineStepOptions(
            outgoing_2,
            timeout=deps.settings.timeout
        )
        requests_3: list[pipelines_v1_pipeline_step_calculation_service_pb2.SimulatePipelineStepRequest] = []
        for item_3 in request.pipeline_step.conditions:
            outgoing_3 = pipelines_v1_pipeline_step_calculation_service_pb2.SimulatePipelineStepRequest(
                context=request.context,
                pipeline_step=pipelines_v1_pipelines_pb2.PipelineStep(
                    conditions=[
                        pipelines_v1_pipelines_pb2.PipelineStepCondition(
                            attribute=item_3.attribute,
                            negate=item_3.negate,
                            operator=item_3.operator,
                            value=item_3.value
                        )
                    ]
                )
            )
            requests_3.append(outgoing_3)
        replies_3 = await asyncio.gather(*(
            deps.clients.pipelines_pipeline_step_calculation.SimulatePipelineStep(
                entry,
                timeout=deps.settings.timeout
            ) for entry in requests_3
        ))
        if replies_3:
            response_3 = replies_3[-1]
        returned_0_0 = response_0.result.status
        if returned_0_0:
            response.result.status = returned_0_0
        returned_1_0 = response_1.outcome.message
        if returned_1_0:
            response.outcome.message = returned_1_0
        returned_2_0 = response_2.result.reference_ids
        response.result.reference_ids.extend(returned_2_0)
        echoed_0 = request.pipeline_step_id
        response.pipeline_step.pipeline_step_id = echoed_0
        echoed_1 = request.pipeline_step.name
        response.pipeline_step.name = echoed_1
        return response


async def handle_preview_pipeline_step(
    deps: Dependencies,
    request: pipelines_v1_pipeline_step_validation_service_pb2.PreviewPipelineStepRequest
) -> pipelines_v1_pipeline_step_validation_service_pb2.PreviewPipelineStepResponse:
    """Previews a pipeline step."""
    response = pipelines_v1_pipeline_step_validation_service_pb2.PreviewPipelineStepResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('PreviewPipelineStep', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'PreviewPipelineStep', {'reason': request.reason})
        await deps.repository.save_pipeline_step(request.context.tenant_id, request.pipeline_step)
        response_0 = fleet_v1_vehicle_service_pb2.WatchVehiclesResponse()
        response_1 = pipelines_v1_pipeline_step_calculation_service_pb2.ComparePipelineStepOptionsResponse()
        outgoing_0 = fleet_v1_vehicle_service_pb2.WatchVehiclesRequest(
            context=request.context,
            subscriber=common_v1_contact_pb2.ContactInfo(phone=request.details.contact.phone)
        )
        async for chunk_0 in deps.clients.fleet_vehicle.WatchVehicles(outgoing_0, timeout=deps.settings.timeout):
            response_0 = chunk_0
        outgoing_1 = pipelines_v1_pipeline_step_calculation_service_pb2.ComparePipelineStepOptionsRequest(
            context=request.context,
            pipeline_step=pipelines_v1_pipelines_pb2.PipelineStep(
                audit=common_v1_audit_pb2.AuditInfo(
                    created_by=request.pipeline_step.audit.created_by,
                    updated_at=request.pipeline_step.audit.updated_at
                )
            )
        )
        envelope_1 = AnyMessage()
        envelope_1.Pack(outgoing_1)
        outgoing_1 = pipelines_v1_pipeline_step_calculation_service_pb2.ComparePipelineStepOptionsRequest()
        if not envelope_1.Unpack(outgoing_1):
            raise ValueError("partner envelope contains the wrong request type")
        response_1 = await deps.clients.pipelines_pipeline_step_calculation.ComparePipelineStepOptions(
            outgoing_1,
            timeout=deps.settings.timeout
        )
        returned_1_0 = response_1.pipeline_step.owner.email
        if returned_1_0:
            response.pipeline_step.owner.email = returned_1_0
        returned_1_1 = response_1.pipeline_step.owner.user_id
        if returned_1_1:
            response.pipeline_step.owner.user_id = returned_1_1
        echoed_0 = request.pipeline_step_id
        response.pipeline_step.pipeline_step_id = echoed_0
        echoed_1 = request.pipeline_step.status
        response.pipeline_step.status = echoed_1
        return response


async def handle_score_pipeline_step(
    deps: Dependencies,
    request: pipelines_v1_pipeline_step_validation_service_pb2.ScorePipelineStepRequest
) -> pipelines_v1_pipeline_step_validation_service_pb2.ScorePipelineStepResponse:
    """Scores a pipeline step."""
    response = pipelines_v1_pipeline_step_validation_service_pb2.ScorePipelineStepResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('ScorePipelineStep', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'ScorePipelineStep', {'reason': request.reason})
        await deps.repository.save_pipeline_step(request.context.tenant_id, request.pipeline_step)
        response_0 = audit_v1_audit_event_validation_service_pb2.ValidateAuditEventResponse()
        outgoing_0 = audit_v1_audit_event_validation_service_pb2.ValidateAuditEventRequest(
            audit_event=audit_v1_audit_pb2.AuditEvent(
                subject=audit_v1_refs_pb2.AuditTrailRef(display_name=request.pipeline_step.owner.display_name)
            ),
            context=request.context,
            reason=request.pipeline_step.block.reason
        )
        response_0 = await deps.clients.audit_audit_event_validation.ValidateAuditEvent(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.result.message
        if returned_0_0:
            response.result.message = returned_0_0
        returned_0_1 = response_0.result.correlation_id
        if returned_0_1:
            response.result.correlation_id = returned_0_1
        echoed_0 = request.pipeline_step_id
        response.pipeline_step.pipeline_step_id = echoed_0
        echoed_1 = request.pipeline_step.description
        response.pipeline_step.description = echoed_1
        return response


async def handle_validate_pipeline_step(
    deps: Dependencies,
    request: pipelines_v1_pipeline_step_validation_service_pb2.ValidatePipelineStepRequest
) -> pipelines_v1_pipeline_step_validation_service_pb2.ValidatePipelineStepResponse:
    """Validates a pipeline step."""
    response = pipelines_v1_pipeline_step_validation_service_pb2.ValidatePipelineStepResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('ValidatePipelineStep', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'ValidatePipelineStep', {'reason': request.reason})
        await deps.repository.save_pipeline_step(request.context.tenant_id, request.pipeline_step)
        response_0 = routing_v1_route_service_pb2.SearchRoutesResponse()
        outgoing_0 = routing_v1_route_service_pb2.SearchRoutesRequest(
            context=request.context,
            filter=routing_v1_route_service_pb2.SearchRoutesRequest.Filter(
                created_after=request.pipeline_step.audit.created_at,
                labels=dict(request.pipeline_step.parameters),
                owner_id=request.pipeline_step.owner.user_id
            )
        )
        response_0 = await deps.clients.routing_route.SearchRoutes(outgoing_0, timeout=deps.settings.timeout)
        returned_0_0 = response_0.result.details
        response.result.details.update(returned_0_0)
        returned_0_1 = response_0.result.reference_ids
        response.result.reference_ids.extend(returned_0_1)
        echoed_0 = request.pipeline_step_id
        response.pipeline_step.pipeline_step_id = echoed_0
        echoed_1 = request.pipeline_step.priority
        response.pipeline_step.priority = echoed_1
        return response
