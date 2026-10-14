"""Functional operations behind PipelineStepExportService."""

from __future__ import annotations

from collections.abc import Awaitable
from collections.abc import Callable
from functools import partial
from typing import Any
from typing import cast
import asyncio
import logging

from google.protobuf.any_pb2 import Any as AnyMessage

from acme.anomalies.v1 import anomalies_pb2 as anomalies_v1_anomalies_pb2
from acme.anomalies.v1 import detector_approval_service_pb2 as anomalies_v1_detector_approval_service_pb2
from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.featureflags.v1 import (
    feature_flag_validation_service_pb2 as featureflags_v1_feature_flag_validation_service_pb2,
)
from acme.featureflags.v1 import featureflags_pb2 as featureflags_v1_featureflags_pb2
from acme.featurestore.v1 import entity_sync_service_pb2 as featurestore_v1_entity_sync_service_pb2
from acme.featurestore.v1 import featurestore_pb2 as featurestore_v1_featurestore_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.identity.v1 import user_service_pb2 as identity_v1_user_service_pb2
from acme.pipelines.v1 import pipeline_calculation_service_pb2 as pipelines_v1_pipeline_calculation_service_pb2
from acme.pipelines.v1 import pipeline_query_service_pb2 as pipelines_v1_pipeline_query_service_pb2
from acme.pipelines.v1 import pipeline_run_validation_service_pb2 as pipelines_v1_pipeline_run_validation_service_pb2
from acme.pipelines.v1 import pipeline_service_pb2 as pipelines_v1_pipeline_service_pb2
from acme.pipelines.v1 import (
    pipeline_step_calculation_service_pb2 as pipelines_v1_pipeline_step_calculation_service_pb2,
)
from acme.pipelines.v1 import pipeline_step_export_service_pb2 as pipelines_v1_pipeline_step_export_service_pb2
from acme.pipelines.v1 import pipeline_step_validation_service_pb2 as pipelines_v1_pipeline_step_validation_service_pb2
from acme.pipelines.v1 import pipeline_validation_service_pb2 as pipelines_v1_pipeline_validation_service_pb2
from acme.pipelines.v1 import pipelines_pb2 as pipelines_v1_pipelines_pb2
from acme.venues.v1 import venue_query_service_pb2 as venues_v1_venue_query_service_pb2

from acme_data.domains.pipelines.adapters import PipelineStepExportStreamPipelineStepExport2Adapter
from acme_data.domains.pipelines.dependencies import Dependencies
from acme_data.domains.pipelines.models import PipelineStepExportSchedulePipelineStepExport1Command
from acme_data.domains.pipelines.models import PipelineStepExportSchedulePipelineStepExport2Command
from acme_data.domains.pipelines.models import to_pipeline_step_export_schedule_pipeline_step_export1_command
from acme_data.domains.pipelines.models import to_pipeline_step_export_schedule_pipeline_step_export2_command
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import run_steps
from acme_data.platform.tenancy import tenant_id
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


async def handle_cancel_pipeline_step_export(
    deps: Dependencies,
    request: pipelines_v1_pipeline_step_export_service_pb2.CancelPipelineStepExportRequest
) -> pipelines_v1_pipeline_step_export_service_pb2.CancelPipelineStepExportResponse:
    """Cancels a pipeline step."""
    response = pipelines_v1_pipeline_step_export_service_pb2.CancelPipelineStepExportResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('CancelPipelineStepExport', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'CancelPipelineStepExport', {'reason': request.reason})
        response_0 = anomalies_v1_detector_approval_service_pb2.CommentDetectorApprovalResponse()
        response_1 = pipelines_v1_pipeline_query_service_pb2.BrowsePipelinesResponse()
        response_2 = pipelines_v1_pipeline_service_pb2.ClonePipelineResponse()
        outgoing_0 = anomalies_v1_detector_approval_service_pb2.CommentDetectorApprovalRequest(
            context=request.context,
            details=anomalies_v1_detector_approval_service_pb2.CommentDetectorApprovalRequest.Details(
                approver=identity_v1_refs_pb2.UserRef(user_id=request.details.new_owner.user_id)
            ),
            detector=anomalies_v1_anomalies_pb2.Detector(
                owner=identity_v1_refs_pb2.UserRef(
                    display_name=request.details.new_owner.display_name,
                    email=request.details.new_owner.email
                )
            )
        )
        response_0 = await deps.clients.anomalies_detector_approval.CommentDetectorApproval(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = pipelines_v1_pipeline_query_service_pb2.BrowsePipelinesRequest(
            context=request.context,
            filter=pipelines_v1_pipeline_query_service_pb2.BrowsePipelinesRequest.Filter(
                created_after=request.details.effective_at,
                owner_id=request.details.new_owner.user_id
            )
        )
        response_1 = cast(pipelines_v1_pipeline_query_service_pb2.BrowsePipelinesResponse, await deps.bus.request(
            'acme.pipelines.v1.PipelineStepExportService/CancelPipelineStepExport/1', outgoing_1, deps.settings.timeout,
        ))
        outgoing_2 = pipelines_v1_pipeline_service_pb2.ClonePipelineRequest(
            context=request.context,
            pipeline=pipelines_v1_pipelines_pb2.Pipeline(
                participants=[
                    pipelines_v1_pipelines_pb2.PipelineParticipant(
                        contact=common_v1_contact_pb2.ContactInfo(
                            email=response_0.detector.owner.email,
                            preferred_channel=request.details.notify_contact.preferred_channel
                        )
                    )
                ]
            )
        )
        response_2 = await deps.clients.pipelines_pipeline.ClonePipeline(outgoing_2, timeout=deps.settings.timeout)
        returned_0_0 = response_0.detector.audit.updated_at
        if returned_0_0.ListFields():
            response.pipeline_step.audit.updated_at.MergeFrom(returned_0_0)
        returned_1_0 = response_1.result.correlation_id
        if returned_1_0:
            response.result.correlation_id = returned_1_0
        returned_1_1 = response_1.result.message
        if returned_1_1:
            response.outcome.message = returned_1_1
        returned_2_0 = response_2.result.reference_ids
        response.result.reference_ids.extend(returned_2_0)
        echoed_0 = request.pipeline_step_id
        response.pipeline_step.pipeline_step_id = echoed_0
        echoed_1 = request.details.effective_at
        response.outcome.effective_at.CopyFrom(echoed_1)
        return response


async def handle_get_pipeline_step_export(
    deps: Dependencies,
    request: pipelines_v1_pipeline_step_export_service_pb2.GetPipelineStepExportRequest
) -> pipelines_v1_pipeline_step_export_service_pb2.GetPipelineStepExportResponse:
    """Returns a pipeline step."""
    response = pipelines_v1_pipeline_step_export_service_pb2.GetPipelineStepExportResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('GetPipelineStepExport', extra={'fields': {'domain': 'pipelines'}})
        await deps.repository.audit(request.context.tenant_id, 'GetPipelineStepExport', {})
        response_0 = featureflags_v1_feature_flag_validation_service_pb2.PreviewFeatureFlagResponse()
        response_1 = pipelines_v1_pipeline_validation_service_pb2.ScorePipelineResponse()
        outgoing_0 = featureflags_v1_feature_flag_validation_service_pb2.PreviewFeatureFlagRequest(
            context=request.context,
            feature_flag=featureflags_v1_featureflags_pb2.FeatureFlag(
                owner=identity_v1_refs_pb2.UserRef(
                    email=request.context.actor.email,
                    user_id=request.context.actor.user_id
                )
            )
        )
        response_0 = await deps.clients.featureflags_feature_flag_validation.PreviewFeatureFlag(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        fields_1: dict[str, Any] = {
            'context': request.context,
            'pipeline': {
                'audit': {'created_at': response_0.feature_flag.audit.created_at},
                'organizer': {
                    'display_name': response_0.feature_flag.owner.display_name,
                    'email': response_0.feature_flag.owner.email
                }
            }
        }
        outgoing_1 = pipelines_v1_pipeline_validation_service_pb2.ScorePipelineRequest(**fields_1)
        response_1 = await deps.clients.pipelines_pipeline_validation.ScorePipeline(
            outgoing_1,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.feature_flag.priority
        if returned_0_0:
            response.pipeline_step.priority = returned_0_0
        returned_1_0 = response_1.pipeline.organizer.user_id
        if returned_1_0:
            response.pipeline_step.owner.user_id = returned_1_0
        echoed_0 = request.pipeline_step_id
        response.pipeline_step.pipeline_step_id = echoed_0
        return response


async def handle_list_pipeline_step_exports(
    deps: Dependencies,
    request: pipelines_v1_pipeline_step_export_service_pb2.ListPipelineStepExportsRequest
) -> pipelines_v1_pipeline_step_export_service_pb2.ListPipelineStepExportsResponse:
    """Lists pipeline steps a page at a time."""
    response = pipelines_v1_pipeline_step_export_service_pb2.ListPipelineStepExportsResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('ListPipelineStepExports', extra={'fields': {'order_by': request.order_by}})
        await deps.repository.audit(
            request.context.tenant_id,
            'ListPipelineStepExports',
            {'order_by': request.order_by}
        )
        response_0 = featurestore_v1_entity_sync_service_pb2.ReconcileEntitiesResponse()
        outgoing_0 = featurestore_v1_entity_sync_service_pb2.ReconcileEntitiesRequest(
            context=request.context,
            entity=featurestore_v1_featurestore_pb2.Entity(
                primary_address=common_v1_address_pb2.PostalAddress(region=request.filter.region)
            )
        )
        response_0 = await deps.clients.featurestore_entity_sync.ReconcileEntities(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.entity.audit.updated_at
        returned_0_0_part_0 = response.pipeline_steps.add()
        if returned_0_0.ListFields():
            returned_0_0_part_0.audit.updated_at.MergeFrom(returned_0_0)
        returned_0_1 = response_0.entity.relationship_manager.display_name
        returned_0_1_part_0 = response.pipeline_steps.add()
        if returned_0_1:
            returned_0_1_part_0.owner.display_name = returned_0_1
        return response


async def handle_retry_pipeline_step_export(
    deps: Dependencies,
    request: pipelines_v1_pipeline_step_export_service_pb2.RetryPipelineStepExportRequest
) -> pipelines_v1_pipeline_step_export_service_pb2.RetryPipelineStepExportResponse:
    """Retrys a pipeline step."""
    response = pipelines_v1_pipeline_step_export_service_pb2.RetryPipelineStepExportResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('RetryPipelineStepExport', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'RetryPipelineStepExport', {'reason': request.reason})
        await deps.repository.save_pipeline_step(request.context.tenant_id, request.pipeline_step)
        response_0 = pipelines_v1_pipeline_step_validation_service_pb2.ScorePipelineStepResponse()
        response_1 = pipelines_v1_pipeline_step_calculation_service_pb2.SimulatePipelineStepResponse()
        response_2 = pipelines_v1_pipeline_step_validation_service_pb2.ValidatePipelineStepResponse()
        outgoing_0 = pipelines_v1_pipeline_step_validation_service_pb2.ScorePipelineStepRequest(
            context=request.context,
            pipeline_step=pipelines_v1_pipelines_pb2.PipelineStep(
                audit=common_v1_audit_pb2.AuditInfo(updated_at=request.pipeline_step.audit.updated_at),
                block=pipelines_v1_pipelines_pb2.PipelineStepBlockAction(
                    notify_email=request.pipeline_step.block.notify_email,
                    reason=request.pipeline_step.block.reason
                ),
                owner=identity_v1_refs_pb2.UserRef(email=request.details.notify.email)
            )
        )
        response_0 = await deps.clients.pipelines_pipeline_step_validation.ScorePipelineStep(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        async for item_1 in async_messages(request.pipeline_step.conditions):
            outgoing_1 = pipelines_v1_pipeline_step_calculation_service_pb2.SimulatePipelineStepRequest(
                context=request.context,
                pipeline_step=pipelines_v1_pipelines_pb2.PipelineStep(
                    conditions=[
                        pipelines_v1_pipelines_pb2.PipelineStepCondition(
                            attribute=item_1.attribute,
                            operator=item_1.operator
                        )
                    ]
                )
            )
            response_1 = await deps.clients.pipelines_pipeline_step_calculation.SimulatePipelineStep(
                outgoing_1,
                timeout=deps.settings.timeout
            )
        outgoing_2 = pipelines_v1_pipeline_step_validation_service_pb2.ValidatePipelineStepRequest(
            context=request.context,
            pipeline_step=pipelines_v1_pipelines_pb2.PipelineStep(
                audit=common_v1_audit_pb2.AuditInfo(updated_by=response_1.pipeline_step.audit.updated_by)
            )
        )
        envelope_2 = AnyMessage()
        envelope_2.Pack(outgoing_2)
        outgoing_2 = pipelines_v1_pipeline_step_validation_service_pb2.ValidatePipelineStepRequest()
        if not envelope_2.Unpack(outgoing_2):
            raise ValueError("partner envelope contains the wrong request type")
        response_2 = await deps.clients.pipelines_pipeline_step_validation.ValidatePipelineStep(
            outgoing_2,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.result.status
        if returned_0_0:
            response.result.status = returned_0_0
        returned_2_0 = response_2.result.message
        if returned_2_0:
            response.result.message = returned_2_0
        returned_2_1 = response_2.pipeline_step.priority
        if returned_2_1:
            response.pipeline_step.priority = returned_2_1
        echoed_0 = request.pipeline_step_id
        response.pipeline_step.pipeline_step_id = echoed_0
        echoed_1 = request.pipeline_step.owner
        response.pipeline_step.owner.CopyFrom(echoed_1)
        return response


async def handle_schedule_pipeline_step_export(
    deps: Dependencies,
    request: pipelines_v1_pipeline_step_export_service_pb2.SchedulePipelineStepExportRequest
) -> pipelines_v1_pipeline_step_export_service_pb2.SchedulePipelineStepExportResponse:
    """Schedules a pipeline step."""
    response = pipelines_v1_pipeline_step_export_service_pb2.SchedulePipelineStepExportResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('SchedulePipelineStepExport', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'SchedulePipelineStepExport', {'reason': request.reason})
        response_0 = pipelines_v1_pipeline_query_service_pb2.SuggestPipelinesResponse()
        response_1 = identity_v1_user_service_pb2.CloneUserResponse()
        response_2 = pipelines_v1_pipeline_calculation_service_pb2.RecalculatePipelinesResponse()
        response_3 = venues_v1_venue_query_service_pb2.SuggestVenuesResponse()
        outgoing_0 = pipelines_v1_pipeline_query_service_pb2.SuggestPipelinesRequest(
            context=request.context,
            filter=pipelines_v1_pipeline_query_service_pb2.SuggestPipelinesRequest.Filter(
                labels=dict(request.details.filters),
                owner_id=request.pipeline_step_id
            )
        )
        response_0 = await deps.clients.pipelines_pipeline_query.SuggestPipelines(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        command_1 = PipelineStepExportSchedulePipelineStepExport1Command(
            context=request.context,
            user_relationship_manager_user_id=request.context.actor.user_id,
            user_relationship_manager_email=request.context.actor.email,
            user_preferences_quiet_hours=request.details.period
        )
        outgoing_1 = to_pipeline_step_export_schedule_pipeline_step_export1_command(command_1)
        response_1 = await deps.clients.identity_user.CloneUser(outgoing_1, timeout=deps.settings.timeout)
        command_2 = PipelineStepExportSchedulePipelineStepExport2Command.model_validate(
            {
                'context': request.context,
                'pipeline_participants_contact_name': response_1.user.contact.name,
                'details_destination_country_code': response_1.user.primary_address.country_code,
                'details_destination_recipient': response_1.user.primary_address.recipient,
                'pipeline_participants_contact_phone': response_1.user.contact.phone
            }
        )
        outgoing_2 = to_pipeline_step_export_schedule_pipeline_step_export2_command(command_2)
        response_2 = await deps.clients.pipelines_pipeline_calculation.RecalculatePipelines(
            outgoing_2,
            timeout=deps.settings.timeout
        )
        outgoing_3 = venues_v1_venue_query_service_pb2.SuggestVenuesRequest(
            context=request.context,
            filter=venues_v1_venue_query_service_pb2.SuggestVenuesRequest.Filter(
                created_after=response_1.user.audit.updated_at,
                labels=dict(request.details.filters),
                owner_id=response_2.result.correlation_id,
                region=response_1.user.primary_address.region
            )
        )
        send_3 = partial(deps.clients.venues_venue_query.SuggestVenues, timeout=deps.settings.timeout)
        response_3 = await send_3(outgoing_3)
        returned_0_0 = response_0.result.correlation_id
        if returned_0_0:
            response.result.correlation_id = returned_0_0
        returned_1_0 = response_1.result.reference_ids
        response.result.reference_ids.extend(returned_1_0)
        returned_2_0 = response_2.result.message
        if returned_2_0:
            response.result.message = returned_2_0
        returned_2_1 = response_2.result.reference_ids
        response.result.reference_ids.extend(returned_2_1)
        returned_3_0 = response_3.result.details
        response.result.details.update(returned_3_0)
        returned_3_1 = response_3.result.reference_ids
        response.result.reference_ids.extend(returned_3_1)
        echoed_0 = request.details.period
        response.period.CopyFrom(echoed_0)
        return response


async def handle_share_pipeline_step_export(
    deps: Dependencies,
    request: pipelines_v1_pipeline_step_export_service_pb2.SharePipelineStepExportRequest
) -> pipelines_v1_pipeline_step_export_service_pb2.SharePipelineStepExportResponse:
    """Shares a pipeline step."""
    response = pipelines_v1_pipeline_step_export_service_pb2.SharePipelineStepExportResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('SharePipelineStepExport', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'SharePipelineStepExport', {'reason': request.reason})
        response_0 = pipelines_v1_pipeline_run_validation_service_pb2.CheckPipelineRunEligibilityResponse()
        response_1 = pipelines_v1_pipeline_validation_service_pb2.NormalizePipelineResponse()
        outgoing_0 = pipelines_v1_pipeline_run_validation_service_pb2.CheckPipelineRunEligibilityRequest(
            context=request.context,
            details=pipelines_v1_pipeline_run_validation_service_pb2.CheckPipelineRunEligibilityRequest.Details(
                contact=common_v1_contact_pb2.ContactInfo(preferred_channel=request.details.recipient.preferred_channel)
            ),
            pipeline_run=pipelines_v1_pipelines_pb2.PipelineRun(
                requester=common_v1_contact_pb2.ContactInfo(
                    email=request.details.recipient.email,
                    phone=request.details.recipient.phone
                )
            )
        )
        response_0 = await deps.clients.pipelines_pipeline_run_validation.CheckPipelineRunEligibility(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = pipelines_v1_pipeline_validation_service_pb2.NormalizePipelineRequest()
        outgoing_1.context.CopyFrom(request.context)
        field_1_1_part_1 = outgoing_1.pipeline.participants.add()
        field_1_1_part_1.contact.preferred_channel = request.details.recipient.preferred_channel
        outgoing_1.details.contact.preferred_channel = response_0.pipeline_run.requester.preferred_channel
        outgoing_1.details.contact.name.CopyFrom(request.details.recipient.name)
        outgoing_1.pipeline.audit.updated_at.CopyFrom(response_0.pipeline_run.audit.updated_at)
        outgoing_1.context.tenant_id = tenant_id.get()
        response_1 = await deps.clients.pipelines_pipeline_validation.NormalizePipeline(
            outgoing_1,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.outcome.status
        if returned_0_0:
            response.outcome.status = returned_0_0
        returned_1_0 = response_1.pipeline.audit.updated_at
        if returned_1_0.ListFields():
            response.pipeline_step.audit.updated_at.MergeFrom(returned_1_0)
        returned_1_1 = response_1.outcome.next_steps
        response.outcome.next_steps.extend(returned_1_1)
        echoed_0 = request.pipeline_step_id
        response.pipeline_step.pipeline_step_id = echoed_0
        echoed_1 = request.details.recipient.email
        response.pipeline_step.owner.email = echoed_1
        return response


async def handle_stream_pipeline_step_export(
    deps: Dependencies,
    request: pipelines_v1_pipeline_step_export_service_pb2.StreamPipelineStepExportRequest
) -> pipelines_v1_pipeline_step_export_service_pb2.StreamPipelineStepExportResponse:
    """Streams every matching pipeline step."""
    response = pipelines_v1_pipeline_step_export_service_pb2.StreamPipelineStepExportResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('StreamPipelineStepExport', extra={'fields': {'destination_uri': request.destination_uri}})
        await deps.repository.audit(
            request.context.tenant_id,
            'StreamPipelineStepExport',
            {'destination_uri': request.destination_uri}
        )
        response_0 = pipelines_v1_pipeline_step_validation_service_pb2.LintPipelineStepsResponse()
        response_1 = featureflags_v1_feature_flag_validation_service_pb2.LintFeatureFlagsResponse()
        response_2 = pipelines_v1_pipeline_calculation_service_pb2.CalculatePipelineResponse()
        response_3 = featureflags_v1_feature_flag_validation_service_pb2.PreviewFeatureFlagResponse()
        outgoing_0 = pipelines_v1_pipeline_step_validation_service_pb2.LintPipelineStepsRequest(
            context=request.context,
            pipeline_step=pipelines_v1_pipelines_pb2.PipelineStep(
                owner=identity_v1_refs_pb2.UserRef(
                    email=request.context.actor.email,
                    user_id=request.context.actor.user_id
                )
            )
        )
        response_0 = await deps.clients.pipelines_pipeline_step_validation.LintPipelineSteps(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = featureflags_v1_feature_flag_validation_service_pb2.LintFeatureFlagsRequest(
            context=request.context,
            feature_flag=featureflags_v1_featureflags_pb2.FeatureFlag(
                block=featureflags_v1_featureflags_pb2.FeatureFlagBlockAction(
                    reason=response_0.pipeline_step.block.reason
                ),
                owner=identity_v1_refs_pb2.UserRef(email=response_0.pipeline_step.owner.email)
            )
        )
        steps_1 = [
            partial(
                deps.clients.featureflags_feature_flag_validation.LintFeatureFlags,
                outgoing_1,
                timeout=deps.settings.timeout
            )
        ]
        results_1 = await run_steps(steps_1)
        response_1 = results_1[-1]
        outgoing_2 = pipelines_v1_pipeline_calculation_service_pb2.CalculatePipelineRequest(
            context=request.context,
            pipeline=pipelines_v1_pipelines_pb2.Pipeline(
                audit=common_v1_audit_pb2.AuditInfo(created_at=response_1.feature_flag.audit.created_at),
                organizer=identity_v1_refs_pb2.UserRef(
                    email=response_1.feature_flag.owner.email,
                    user_id=response_1.feature_flag.owner.user_id
                )
            )
        )
        response_2 = await PipelineStepExportStreamPipelineStepExport2Adapter(
            deps.clients.pipelines_pipeline_calculation,
            deps.settings.timeout
        )(outgoing_2)
        outgoing_3 = featureflags_v1_feature_flag_validation_service_pb2.PreviewFeatureFlagRequest(
            context=request.context,
            details=featureflags_v1_feature_flag_validation_service_pb2.PreviewFeatureFlagRequest.Details(
                contact=common_v1_contact_pb2.ContactInfo(email=response_2.pipeline.organizer.email)
            ),
            feature_flag=featureflags_v1_featureflags_pb2.FeatureFlag(
                audit=common_v1_audit_pb2.AuditInfo(etag=response_2.pipeline.audit.etag)
            )
        )
        response_3 = cast(featureflags_v1_feature_flag_validation_service_pb2.PreviewFeatureFlagResponse, await deps.bus.request(
            'acme.pipelines.v1.PipelineStepExportService/StreamPipelineStepExport/3', outgoing_3, deps.settings.timeout,
        ))
        returned_0_0 = response_0.pipeline_step.owner
        if returned_0_0.ListFields():
            response.pipeline_step.owner.MergeFrom(returned_0_0)
        returned_1_0 = response_1.feature_flag.effective
        if returned_1_0.ListFields():
            response.pipeline_step.effective.MergeFrom(returned_1_0)
        returned_2_0 = response_2.pipeline.audit.created_by
        if returned_2_0:
            response.pipeline_step.audit.created_by = returned_2_0
        returned_3_0 = response_3.outcome.status
        if returned_3_0:
            response.result.status = returned_3_0
        returned_3_1 = response_3.feature_flag.audit.updated_at
        if returned_3_1.ListFields():
            response.pipeline_step.audit.updated_at.MergeFrom(returned_3_1)
        return response
