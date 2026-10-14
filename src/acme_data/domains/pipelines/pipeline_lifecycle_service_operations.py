"""Functional operations behind PipelineLifecycleService."""

from __future__ import annotations

from collections.abc import Awaitable
from collections.abc import Callable
from typing import Any
import asyncio
import logging

from google.protobuf.json_format import MessageToDict
from google.protobuf.json_format import ParseDict

from acme.audit.v1 import audit_event_validation_service_pb2 as audit_v1_audit_event_validation_service_pb2
from acme.audit.v1 import audit_pb2 as audit_v1_audit_pb2
from acme.audit.v1 import refs_pb2 as audit_v1_refs_pb2
from acme.authorization.v1 import access_policy_query_service_pb2 as authorization_v1_access_policy_query_service_pb2
from acme.cart.v1 import cart_query_service_pb2 as cart_v1_cart_query_service_pb2
from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.metrics.v1 import dashboard_sync_service_pb2 as metrics_v1_dashboard_sync_service_pb2
from acme.metrics.v1 import metrics_pb2 as metrics_v1_metrics_pb2
from acme.metrics.v1 import refs_pb2 as metrics_v1_refs_pb2
from acme.pipelines.v1 import pipeline_calculation_service_pb2 as pipelines_v1_pipeline_calculation_service_pb2
from acme.pipelines.v1 import pipeline_lifecycle_service_pb2 as pipelines_v1_pipeline_lifecycle_service_pb2
from acme.pipelines.v1 import pipeline_query_service_pb2 as pipelines_v1_pipeline_query_service_pb2
from acme.pipelines.v1 import pipeline_run_sync_service_pb2 as pipelines_v1_pipeline_run_sync_service_pb2
from acme.pipelines.v1 import pipeline_run_validation_service_pb2 as pipelines_v1_pipeline_run_validation_service_pb2
from acme.pipelines.v1 import pipeline_step_sync_service_pb2 as pipelines_v1_pipeline_step_sync_service_pb2
from acme.pipelines.v1 import pipelines_pb2 as pipelines_v1_pipelines_pb2
from acme.pipelines.v1 import refs_pb2 as pipelines_v1_refs_pb2
from acme.seating.v1 import seat_map_service_pb2 as seating_v1_seat_map_service_pb2

from acme_data.domains.pipelines.adapters import PipelineLifecycleExpirePipeline1Adapter
from acme_data.domains.pipelines.dependencies import Dependencies
from acme_data.domains.pipelines.models import PipelineLifecycleTerminatePipeline1Command
from acme_data.domains.pipelines.models import PipelineLifecycleTerminatePipeline2Command
from acme_data.domains.pipelines.models import to_pipeline_lifecycle_terminate_pipeline1_command
from acme_data.domains.pipelines.models import to_pipeline_lifecycle_terminate_pipeline2_command
from acme_data.platform.rpc import async_messages
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


async def handle_activate_pipeline(
    deps: Dependencies,
    request: pipelines_v1_pipeline_lifecycle_service_pb2.ActivatePipelineRequest
) -> pipelines_v1_pipeline_lifecycle_service_pb2.ActivatePipelineResponse:
    """Activates a pipeline."""
    response = pipelines_v1_pipeline_lifecycle_service_pb2.ActivatePipelineResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('ActivatePipeline', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'ActivatePipeline', {'reason': request.reason})
        response_0 = authorization_v1_access_policy_query_service_pb2.CountAccessPoliciesResponse()
        response_1 = cart_v1_cart_query_service_pb2.ExportCartsResponse()
        outgoing_0 = authorization_v1_access_policy_query_service_pb2.CountAccessPoliciesRequest(
            context=request.context,
            filter=authorization_v1_access_policy_query_service_pb2.CountAccessPoliciesRequest.Filter(
                created_after=request.details.effective_at
            )
        )
        response_0 = await deps.clients.authorization_access_policy_query.CountAccessPolicies(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = cart_v1_cart_query_service_pb2.ExportCartsRequest(
            context=request.context,
            filter=cart_v1_cart_query_service_pb2.ExportCartsRequest.Filter(
                created_after=request.details.effective_at,
                owner_id=request.details.new_owner.user_id
            )
        )
        async for chunk_1 in deps.clients.cart_cart_query.ExportCarts(outgoing_1, timeout=deps.settings.timeout):
            response_1 = chunk_1
        returned_0_0 = response_0.result.message
        if returned_0_0:
            response.outcome.message = returned_0_0
        echoed_0 = request.pipeline_id
        response.pipeline.pipeline_id = echoed_0
        echoed_1 = request.details.effective_at
        response.outcome.effective_at.CopyFrom(echoed_1)
        return response


async def handle_expire_pipeline(
    deps: Dependencies,
    request: pipelines_v1_pipeline_lifecycle_service_pb2.ExpirePipelineRequest
) -> pipelines_v1_pipeline_lifecycle_service_pb2.ExpirePipelineResponse:
    """Expires a pipeline."""
    response = pipelines_v1_pipeline_lifecycle_service_pb2.ExpirePipelineResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('ExpirePipeline', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'ExpirePipeline', {'reason': request.reason})
        response_0 = pipelines_v1_pipeline_query_service_pb2.ResolvePipelinesResponse()
        response_1 = metrics_v1_dashboard_sync_service_pb2.ResolveDashboardConflictResponse()
        outgoing_0 = pipelines_v1_pipeline_query_service_pb2.ResolvePipelinesRequest(context=request.context)
        response_0 = await deps.clients.pipelines_pipeline_query.ResolvePipelines(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = metrics_v1_dashboard_sync_service_pb2.ResolveDashboardConflictRequest(
            context=request.context,
            dashboard=metrics_v1_metrics_pb2.Dashboard(
                counterparty=metrics_v1_refs_pb2.MetricAlertRef(display_name=request.details.new_owner.display_name)
            )
        )
        response_1 = await PipelineLifecycleExpirePipeline1Adapter(
            deps.clients.metrics_dashboard_sync,
            deps.settings.timeout
        )(outgoing_1)
        returned_0_0 = response_0.result.details
        response.result.details.update(returned_0_0)
        returned_1_0 = response_1.result.status
        if returned_1_0:
            response.result.status = returned_1_0
        echoed_0 = request.pipeline_id
        response.pipeline.pipeline_id = echoed_0
        echoed_1 = request.details.effective_at
        response.outcome.effective_at.CopyFrom(echoed_1)
        return response


async def handle_get_pipeline_lifecycle(
    deps: Dependencies,
    request: pipelines_v1_pipeline_lifecycle_service_pb2.GetPipelineLifecycleRequest
) -> pipelines_v1_pipeline_lifecycle_service_pb2.GetPipelineLifecycleResponse:
    """Returns a pipeline."""
    response = pipelines_v1_pipeline_lifecycle_service_pb2.GetPipelineLifecycleResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('GetPipelineLifecycle', extra={'fields': {'domain': 'pipelines'}})
        await deps.repository.audit(request.context.tenant_id, 'GetPipelineLifecycle', {})
        response_0 = pipelines_v1_pipeline_run_sync_service_pb2.SyncPipelineRunsResponse()
        response_1 = pipelines_v1_pipeline_step_sync_service_pb2.SyncPipelineStepsResponse()
        outgoing_0 = pipelines_v1_pipeline_run_sync_service_pb2.SyncPipelineRunsRequest(
            context=request.context,
            pipeline_run=pipelines_v1_pipelines_pb2.PipelineRun(
                assignee=identity_v1_refs_pb2.UserRef(user_id=request.context.actor.user_id),
                audit=common_v1_audit_pb2.AuditInfo(created_at=request.context.deadline),
                customer=pipelines_v1_refs_pb2.PipelineRef(pipeline_id=request.pipeline_id),
                requester=common_v1_contact_pb2.ContactInfo(email=request.context.actor.email)
            )
        )
        response_0 = await deps.clients.pipelines_pipeline_run_sync.SyncPipelineRuns(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = pipelines_v1_pipeline_step_sync_service_pb2.SyncPipelineStepsRequest(
            context=request.context,
            pipeline_step=pipelines_v1_pipelines_pb2.PipelineStep(
                audit=common_v1_audit_pb2.AuditInfo(
                    created_by=response_0.pipeline_run.audit.created_by,
                    etag=response_0.pipeline_run.audit.etag,
                    updated_at=response_0.pipeline_run.audit.updated_at
                ),
                owner=identity_v1_refs_pb2.UserRef(user_id=response_0.pipeline_run.assignee.user_id)
            )
        )
        response_1 = await deps.clients.pipelines_pipeline_step_sync.SyncPipelineSteps(
            outgoing_1,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.pipeline_run.customer.display_name
        if returned_0_0:
            response.pipeline.organizer.display_name = returned_0_0
        returned_0_1 = response_0.outcome.status
        if returned_0_1:
            response.result.status = returned_0_1
        returned_1_0 = response_1.pipeline_step.owner.email
        if returned_1_0:
            response.pipeline.organizer.email = returned_1_0
        returned_1_1 = response_1.result.correlation_id
        if returned_1_1:
            response.result.correlation_id = returned_1_1
        echoed_0 = request.pipeline_id
        response.pipeline.pipeline_id = echoed_0
        return response


async def handle_renew_pipeline(
    deps: Dependencies,
    request: pipelines_v1_pipeline_lifecycle_service_pb2.RenewPipelineRequest
) -> pipelines_v1_pipeline_lifecycle_service_pb2.RenewPipelineResponse:
    """Renews a pipeline."""
    response = pipelines_v1_pipeline_lifecycle_service_pb2.RenewPipelineResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('RenewPipeline', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'RenewPipeline', {'reason': request.reason})
        response_0 = seating_v1_seat_map_service_pb2.ListSeatMapsResponse()
        response_1 = pipelines_v1_pipeline_calculation_service_pb2.RecalculatePipelinesResponse()
        response_2 = audit_v1_audit_event_validation_service_pb2.NormalizeAuditEventResponse()
        outgoing_0 = seating_v1_seat_map_service_pb2.ListSeatMapsRequest(
            context=request.context,
            filter=seating_v1_seat_map_service_pb2.ListSeatMapsRequest.Filter(
                created_after=request.details.effective_at,
                labels=dict(request.annotations),
                owner_id=request.pipeline_id
            )
        )
        response_0 = await deps.clients.seating_seat_map.ListSeatMaps(outgoing_0, timeout=deps.settings.timeout)
        fields_1: dict[str, Any] = {
            'context': request.context,
            'pipeline': {'participants': [{'contact': {'email': request.details.notify_contact.email}}]}
        }
        outgoing_1 = pipelines_v1_pipeline_calculation_service_pb2.RecalculatePipelinesRequest(**fields_1)
        response_1 = await deps.clients.pipelines_pipeline_calculation.RecalculatePipelines(
            outgoing_1,
            timeout=deps.settings.timeout
        )
        outgoing_2 = audit_v1_audit_event_validation_service_pb2.NormalizeAuditEventRequest(
            audit_event=audit_v1_audit_pb2.AuditEvent(
                subject=audit_v1_refs_pb2.AuditTrailRef(display_name=response_1.pipeline.organizer.display_name)
            ),
            context=request.context,
            details=audit_v1_audit_event_validation_service_pb2.NormalizeAuditEventRequest.Details(
                contact=common_v1_contact_pb2.ContactInfo(
                    email=request.details.new_owner.email,
                    name=request.details.notify_contact.name,
                    phone=request.details.notify_contact.phone
                )
            )
        )
        document_2 = MessageToDict(outgoing_2, preserving_proto_field_name=True)
        outgoing_2 = ParseDict(document_2, audit_v1_audit_event_validation_service_pb2.NormalizeAuditEventRequest())
        response_2 = await deps.clients.audit_audit_event_validation.NormalizeAuditEvent(
            outgoing_2,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.result.message
        if returned_0_0:
            response.result.message = returned_0_0
        returned_0_1 = response_0.result.status
        if returned_0_1:
            response.result.status = returned_0_1
        returned_1_0 = response_1.result.correlation_id
        if returned_1_0:
            response.result.correlation_id = returned_1_0
        returned_2_0 = response_2.result.details
        response.result.details.update(returned_2_0)
        returned_2_1 = response_2.outcome.status
        if returned_2_1:
            response.outcome.status = returned_2_1
        echoed_0 = request.pipeline_id
        response.pipeline.pipeline_id = echoed_0
        echoed_1 = request.details.effective_at
        response.outcome.effective_at.CopyFrom(echoed_1)
        return response


async def handle_schedule_pipeline_expiry(
    deps: Dependencies,
    request: pipelines_v1_pipeline_lifecycle_service_pb2.SchedulePipelineExpiryRequest
) -> pipelines_v1_pipeline_lifecycle_service_pb2.SchedulePipelineExpiryResponse:
    """Schedules a pipeline."""
    response = pipelines_v1_pipeline_lifecycle_service_pb2.SchedulePipelineExpiryResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('SchedulePipelineExpiry', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'SchedulePipelineExpiry', {'reason': request.reason})
        await deps.repository.save_pipeline(request.context.tenant_id, request.pipeline)
        response_0 = metrics_v1_dashboard_sync_service_pb2.SyncDashboardsResponse()
        response_1 = pipelines_v1_pipeline_step_sync_service_pb2.SyncPipelineStepsResponse()
        outgoing_0 = metrics_v1_dashboard_sync_service_pb2.SyncDashboardsRequest(
            context=request.context,
            dashboard=metrics_v1_metrics_pb2.Dashboard(
                audit=common_v1_audit_pb2.AuditInfo(
                    created_at=request.pipeline.audit.created_at,
                    updated_by=request.pipeline.audit.updated_by
                ),
                billing_address=common_v1_address_pb2.PostalAddress(
                    locality=request.pipeline.location.locality,
                    region=request.pipeline.location.region
                )
            )
        )
        response_0 = await deps.clients.metrics_dashboard_sync.SyncDashboards(outgoing_0, timeout=deps.settings.timeout)
        callbacks_1: list[
            Callable[[], Awaitable[pipelines_v1_pipeline_step_sync_service_pb2.SyncPipelineStepsResponse]]
        ] = []
        for item_1 in request.pipeline.participants:
            outgoing_1 = pipelines_v1_pipeline_step_sync_service_pb2.SyncPipelineStepsRequest(
                context=request.context,
                pipeline_step=pipelines_v1_pipelines_pb2.PipelineStep(
                    audit=common_v1_audit_pb2.AuditInfo(
                        created_by=response_0.dashboard.audit.created_by,
                        updated_at=response_0.dashboard.audit.updated_at
                    ),
                    owner=identity_v1_refs_pb2.UserRef(
                        display_name=request.pipeline.organizer.display_name,
                        email=item_1.contact.email
                    )
                )
            )
            async def send_1(
                payload: pipelines_v1_pipeline_step_sync_service_pb2.SyncPipelineStepsRequest = outgoing_1
            ) -> pipelines_v1_pipeline_step_sync_service_pb2.SyncPipelineStepsResponse:
                return await deps.clients.pipelines_pipeline_step_sync.SyncPipelineSteps(
                    payload,
                    timeout=deps.settings.timeout
                )
            callbacks_1.append(send_1)
        for callback_1 in callbacks_1:
            response_1 = await callback_1()
        returned_0_0 = response_0.result.reference_ids
        response.result.reference_ids.extend(returned_0_0)
        returned_0_1 = response_0.dashboard.billing_address.region
        if returned_0_1:
            response.pipeline.location.region = returned_0_1
        echoed_0 = request.pipeline_id
        response.pipeline.pipeline_id = echoed_0
        echoed_1 = request.pipeline.window
        response.pipeline.window.CopyFrom(echoed_1)
        return response


async def handle_suspend_pipeline(
    deps: Dependencies,
    request: pipelines_v1_pipeline_lifecycle_service_pb2.SuspendPipelineRequest
) -> pipelines_v1_pipeline_lifecycle_service_pb2.SuspendPipelineResponse:
    """Suspends a pipeline."""
    response = pipelines_v1_pipeline_lifecycle_service_pb2.SuspendPipelineResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('SuspendPipeline', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'SuspendPipeline', {'reason': request.reason})
        response_0 = pipelines_v1_pipeline_calculation_service_pb2.ExplainPipelineCalculationResponse()
        outgoing_0 = pipelines_v1_pipeline_calculation_service_pb2.ExplainPipelineCalculationRequest(
            context=request.context,
            pipeline=pipelines_v1_pipelines_pb2.Pipeline(
                organizer=identity_v1_refs_pb2.UserRef(email=request.details.new_owner.email),
                participants=[
                    pipelines_v1_pipelines_pb2.PipelineParticipant(
                        contact=common_v1_contact_pb2.ContactInfo(
                            email=request.details.notify_contact.email,
                            name=request.details.notify_contact.name,
                            phone=request.details.notify_contact.phone
                        )
                    )
                ]
            )
        )
        response_0 = await deps.clients.pipelines_pipeline_calculation.ExplainPipelineCalculation(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.pipeline.location
        if returned_0_0.ListFields():
            response.pipeline.location.MergeFrom(returned_0_0)
        returned_0_1 = response_0.pipeline.organizer.email
        if returned_0_1:
            response.pipeline.organizer.email = returned_0_1
        echoed_0 = request.pipeline_id
        response.pipeline.pipeline_id = echoed_0
        echoed_1 = request.details.effective_at
        response.outcome.effective_at.CopyFrom(echoed_1)
        return response


async def handle_terminate_pipeline(
    deps: Dependencies,
    request: pipelines_v1_pipeline_lifecycle_service_pb2.TerminatePipelineRequest
) -> pipelines_v1_pipeline_lifecycle_service_pb2.TerminatePipelineResponse:
    """Terminates a pipeline."""
    response = pipelines_v1_pipeline_lifecycle_service_pb2.TerminatePipelineResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('TerminatePipeline', extra={'fields': {'reason_code': request.details.reason_code}})
        await deps.repository.audit(
            request.context.tenant_id,
            'TerminatePipeline',
            {'reason_code': request.details.reason_code}
        )
        response_0 = pipelines_v1_pipeline_query_service_pb2.CountPipelinesResponse()
        response_1 = metrics_v1_dashboard_sync_service_pb2.SyncDashboardsResponse()
        response_2 = pipelines_v1_pipeline_run_validation_service_pb2.CheckPipelineRunEligibilityResponse()
        outgoing_0 = pipelines_v1_pipeline_query_service_pb2.CountPipelinesRequest(
            context=request.context,
            filter=pipelines_v1_pipeline_query_service_pb2.CountPipelinesRequest.Filter(
                created_after=request.details.effective_at,
                labels=dict(request.annotations),
                owner_id=request.details.new_owner.user_id
            )
        )
        response_0 = await deps.clients.pipelines_pipeline_query.CountPipelines(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        command_1 = PipelineLifecycleTerminatePipeline1Command(
            context=request.context,
            dashboard_counterparty_display_name=request.details.new_owner.display_name,
            reason=request.reason,
            annotations=dict(request.annotations)
        )
        outgoing_1 = to_pipeline_lifecycle_terminate_pipeline1_command(command_1)
        response_1 = await deps.clients.metrics_dashboard_sync.SyncDashboards(outgoing_1, timeout=deps.settings.timeout)
        command_2 = PipelineLifecycleTerminatePipeline2Command.model_validate(
            {
                'context': request.context,
                'pipeline_run_comments_created_at': response_1.dashboard.audit.created_at,
                'details_contact_preferred_channel': request.details.notify_contact.preferred_channel,
                'details_contact_email': request.details.notify_contact.email
            }
        )
        outgoing_2 = to_pipeline_lifecycle_terminate_pipeline2_command(command_2)
        response_2 = await deps.clients.pipelines_pipeline_run_validation.CheckPipelineRunEligibility(
            outgoing_2,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.result.message
        if returned_0_0:
            response.result.message = returned_0_0
        returned_1_0 = response_1.dashboard.billing_address.lines
        response.pipeline.location.lines.extend(returned_1_0)
        returned_2_0 = response_2.pipeline_run.requester.email
        returned_2_0_part_1 = response.pipeline.participants.add()
        if returned_2_0:
            returned_2_0_part_1.contact.email = returned_2_0
        echoed_0 = request.pipeline_id
        response.pipeline.pipeline_id = echoed_0
        echoed_1 = request.details.effective_at
        response.outcome.effective_at.CopyFrom(echoed_1)
        return response
