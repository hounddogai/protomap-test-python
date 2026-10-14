"""Application workflow for PipelineRun Calculation."""

from __future__ import annotations

from collections.abc import Awaitable
from collections.abc import Callable
from functools import partial
from typing import cast
import asyncio
import logging

from google.protobuf.any_pb2 import Any as AnyMessage
from google.protobuf.json_format import MessageToDict
from google.protobuf.json_format import MessageToJson
from google.protobuf.json_format import Parse
from google.protobuf.json_format import ParseDict

from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.lineage.v1 import lineage_node_service_pb2 as lineage_v1_lineage_node_service_pb2
from acme.lineage.v1 import lineage_pb2 as lineage_v1_lineage_pb2
from acme.metrics.v1 import metric_alert_validation_service_pb2 as metrics_v1_metric_alert_validation_service_pb2
from acme.modelregistry.v1 import (
    deployment_validation_service_pb2 as modelregistry_v1_deployment_validation_service_pb2,
)
from acme.pipelines.v1 import pipeline_calculation_service_pb2 as pipelines_v1_pipeline_calculation_service_pb2
from acme.pipelines.v1 import (
    pipeline_calculation_service_pb2_grpc as pipelines_v1_pipeline_calculation_service_pb2_grpc,
)
from acme.pipelines.v1 import pipeline_run_calculation_service_pb2 as pipelines_v1_pipeline_run_calculation_service_pb2
from acme.pipelines.v1 import pipelines_pb2 as pipelines_v1_pipelines_pb2
from acme.ratelimiting.v1 import rate_limit_query_service_pb2 as ratelimiting_v1_rate_limit_query_service_pb2
from acme.ticketing.v1 import ticket_query_service_pb2 as ticketing_v1_ticket_query_service_pb2
from acme.venues.v1 import venue_query_service_pb2 as venues_v1_venue_query_service_pb2
from acme.venues.v1 import venue_validation_service_pb2 as venues_v1_venue_validation_service_pb2
from acme.venues.v1 import venues_pb2 as venues_v1_venues_pb2

from acme_data.domains.pipelines.adapters import PipelineRunCalculationEstimatePipelineRun1Adapter
from acme_data.domains.pipelines.adapters import PipelineRunCalculationEstimatePipelineRun1Port
from acme_data.domains.pipelines.dependencies import Dependencies
from acme_data.domains.pipelines.models import PipelineRunCalculationComparePipelineRunOptions0Command
from acme_data.domains.pipelines.models import PipelineRunCalculationComparePipelineRunOptions1Command
from acme_data.domains.pipelines.models import to_pipeline_run_calculation_compare_pipeline_run_options0_command
from acme_data.domains.pipelines.models import to_pipeline_run_calculation_compare_pipeline_run_options1_command
from acme_data.platform.rpc import async_messages
from acme_data.platform.tenancy import tenant_id
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class PipelineRunCalculationServicerWorkflow:
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    async def handle_calculate_pipeline_run(
        self,
        request: pipelines_v1_pipeline_run_calculation_service_pb2.CalculatePipelineRunRequest
    ) -> pipelines_v1_pipeline_run_calculation_service_pb2.CalculatePipelineRunResponse:
        """Calculates a pipeline run."""
        deps = self.deps
        response = pipelines_v1_pipeline_run_calculation_service_pb2.CalculatePipelineRunResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CalculatePipelineRun', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'CalculatePipelineRun', {'reason': request.reason})
            await deps.repository.save_pipeline_run(request.context.tenant_id, request.pipeline_run)
            response_0 = lineage_v1_lineage_node_service_pb2.UpdateLineageNodeResponse()
            response_1 = modelregistry_v1_deployment_validation_service_pb2.PreviewDeploymentResponse()
            response_2 = pipelines_v1_pipeline_calculation_service_pb2.ExplainPipelineCalculationResponse()
            response_3 = pipelines_v1_pipeline_calculation_service_pb2.RecalculatePipelinesResponse()
            outgoing_0 = lineage_v1_lineage_node_service_pb2.UpdateLineageNodeRequest(
                context=request.context,
                lineage_node=lineage_v1_lineage_pb2.LineageNode(
                    children=[
                        lineage_v1_lineage_pb2.LineageNode(
                            children=[
                                lineage_v1_lineage_pb2.LineageNode(
                                    location=common_v1_address_pb2.PostalAddress(
                                        lines=list(request.details.destination.lines)
                                    )
                                )
                            ]
                        )
                    ]
                )
            )
            document_0 = MessageToJson(outgoing_0, preserving_proto_field_name=True)
            outgoing_0 = Parse(document_0, lineage_v1_lineage_node_service_pb2.UpdateLineageNodeRequest())
            response_0 = await deps.clients.lineage_lineage_node.UpdateLineageNode(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = modelregistry_v1_deployment_validation_service_pb2.PreviewDeploymentRequest()
            outgoing_1.context.CopyFrom(request.context)
            outgoing_1.deployment.audit.updated_by = request.pipeline_run.audit.updated_by
            outgoing_1.details.contact.email = response_0.lineage_node.manager.email
            merged_1 = modelregistry_v1_deployment_validation_service_pb2.PreviewDeploymentRequest()
            merged_1.MergeFrom(outgoing_1)
            outgoing_1.CopyFrom(merged_1)
            response_1 = await deps.clients.modelregistry_deployment_validation.PreviewDeployment(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = pipelines_v1_pipeline_calculation_service_pb2.ExplainPipelineCalculationRequest(
                context=request.context,
                pipeline=pipelines_v1_pipelines_pb2.Pipeline(
                    audit=common_v1_audit_pb2.AuditInfo(updated_by=request.pipeline_run.audit.updated_by),
                    participants=[
                        pipelines_v1_pipelines_pb2.PipelineParticipant(
                            contact=common_v1_contact_pb2.ContactInfo(
                                email=response_1.deployment.organizer.email,
                                phone=request.pipeline_run.requester.phone
                            )
                        )
                    ]
                )
            )
            envelope_2 = AnyMessage()
            envelope_2.Pack(outgoing_2)
            outgoing_2 = pipelines_v1_pipeline_calculation_service_pb2.ExplainPipelineCalculationRequest()
            if not envelope_2.Unpack(outgoing_2):
                raise ValueError("partner envelope contains the wrong request type")
            response_2 = await deps.clients.pipelines_pipeline_calculation.ExplainPipelineCalculation(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            outgoing_3 = pipelines_v1_pipeline_calculation_service_pb2.RecalculatePipelinesRequest(
                context=request.context,
                pipeline=pipelines_v1_pipelines_pb2.Pipeline(
                    location=common_v1_address_pb2.PostalAddress(postal_code=request.details.destination.postal_code),
                    participants=[
                        pipelines_v1_pipelines_pb2.PipelineParticipant(
                            contact=common_v1_contact_pb2.ContactInfo(email=response_1.deployment.organizer.email)
                        )
                    ]
                )
            )
            registered_3 = cast(
                pipelines_v1_pipeline_calculation_service_pb2_grpc.PipelineCalculationServiceStub,
                deps.clients.registry['acme.pipelines.v1.PipelineCalculationService']
            )
            response_3 = await registered_3.RecalculatePipelines(outgoing_3, timeout=deps.settings.timeout)
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.result.message = returned_0_0
            returned_0_1 = response_0.lineage_node.audit.created_at
            returned_0_1_part_1 = response.pipeline_run.comments.add()
            if returned_0_1.ListFields():
                returned_0_1_part_1.created_at.MergeFrom(returned_0_1)
            returned_1_0 = response_1.result.details
            response.result.details.update(returned_1_0)
            returned_2_0 = response_2.pipeline.audit.etag
            if returned_2_0:
                response.pipeline_run.audit.etag = returned_2_0
            returned_2_1 = response_2.result.reference_ids
            response.result.reference_ids.extend(returned_2_1)
            returned_3_0 = response_3.pipeline.audit.created_at
            returned_3_0_part_1 = response.pipeline_run.comments.add()
            if returned_3_0.ListFields():
                returned_3_0_part_1.created_at.MergeFrom(returned_3_0)
            returned_3_1 = response_3.result.status
            if returned_3_1:
                response.result.status = returned_3_1
            echoed_0 = request.pipeline_run_id
            response.pipeline_run.pipeline_run_id = echoed_0
            echoed_1 = request.pipeline_run.priority
            response.pipeline_run.priority = echoed_1
            return response

    async def handle_compare_pipeline_run_options(
        self,
        request: pipelines_v1_pipeline_run_calculation_service_pb2.ComparePipelineRunOptionsRequest
    ) -> pipelines_v1_pipeline_run_calculation_service_pb2.ComparePipelineRunOptionsResponse:
        """Compares a pipeline run."""
        deps = self.deps
        response = pipelines_v1_pipeline_run_calculation_service_pb2.ComparePipelineRunOptionsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ComparePipelineRunOptions', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ComparePipelineRunOptions',
                {'reason': request.reason}
            )
            await deps.repository.save_pipeline_run(request.context.tenant_id, request.pipeline_run)
            response_0 = pipelines_v1_pipeline_calculation_service_pb2.CalculatePipelineResponse()
            response_1 = pipelines_v1_pipeline_calculation_service_pb2.ExplainPipelineCalculationResponse()
            response_2 = venues_v1_venue_query_service_pb2.CountVenuesResponse()
            response_3 = pipelines_v1_pipeline_calculation_service_pb2.EstimatePipelineResponse()
            command_0 = PipelineRunCalculationComparePipelineRunOptions0Command(
                context=request.context,
                pipeline_participants_contact_preferred_channel=request.pipeline_run.requester.preferred_channel
            )
            outgoing_0 = to_pipeline_run_calculation_compare_pipeline_run_options0_command(command_0)
            response_0 = await deps.clients.pipelines_pipeline_calculation.CalculatePipeline(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            command_1 = PipelineRunCalculationComparePipelineRunOptions1Command.model_validate(
                {
                    'context': request.context,
                    'pipeline_location_locality': response_0.pipeline.location.locality,
                    'pipeline_organizer_user_id': request.pipeline_run.assignee.user_id,
                    'pipeline_participants_contact_phone': request.pipeline_run.requester.phone,
                    'details_contact_name': request.pipeline_run.requester.name
                }
            )
            outgoing_1 = to_pipeline_run_calculation_compare_pipeline_run_options1_command(command_1)
            response_1 = await deps.clients.pipelines_pipeline_calculation.ExplainPipelineCalculation(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = venues_v1_venue_query_service_pb2.CountVenuesRequest(
                context=request.context,
                filter=venues_v1_venue_query_service_pb2.CountVenuesRequest.Filter(
                    region=response_1.pipeline.location.region
                )
            )
            send_2 = partial(deps.clients.venues_venue_query.CountVenues, timeout=deps.settings.timeout)
            response_2 = await send_2(outgoing_2)
            outgoing_3 = pipelines_v1_pipeline_calculation_service_pb2.EstimatePipelineRequest()
            outgoing_3.context.CopyFrom(request.context)
            if response_1.pipeline.WhichOneof('recurrence') == 'weekly':
                outgoing_3.pipeline.weekly.days.extend(list(response_1.pipeline.weekly.days))
            outgoing_3.pipeline.location.locality = response_1.pipeline.location.locality
            outgoing_3.pipeline.organizer.display_name = response_0.pipeline.organizer.display_name
            response_3 = await deps.clients.pipelines_pipeline_calculation.EstimatePipeline(
                outgoing_3,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.result.message = returned_0_0
            returned_0_1 = response_0.pipeline.audit.created_by
            if returned_0_1:
                response.pipeline_run.audit.created_by = returned_0_1
            returned_1_0 = response_1.pipeline.organizer.user_id
            if returned_1_0:
                response.pipeline_run.assignee.user_id = returned_1_0
            returned_2_0 = response_2.result.reference_ids
            response.result.reference_ids.extend(returned_2_0)
            returned_3_0 = response_3.result.details
            response.result.details.update(returned_3_0)
            returned_3_1 = response_3.pipeline.organizer.display_name
            if returned_3_1:
                response.pipeline_run.assignee.display_name = returned_3_1
            echoed_0 = request.pipeline_run_id
            response.pipeline_run.pipeline_run_id = echoed_0
            echoed_1 = request.pipeline_run.priority
            response.pipeline_run.priority = echoed_1
            return response

    async def handle_estimate_pipeline_run(
        self,
        request: pipelines_v1_pipeline_run_calculation_service_pb2.EstimatePipelineRunRequest
    ) -> pipelines_v1_pipeline_run_calculation_service_pb2.EstimatePipelineRunResponse:
        """Estimates a pipeline run."""
        deps = self.deps
        response = pipelines_v1_pipeline_run_calculation_service_pb2.EstimatePipelineRunResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('EstimatePipelineRun', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'EstimatePipelineRun', {'reason': request.reason})
            await deps.repository.save_pipeline_run(request.context.tenant_id, request.pipeline_run)
            response_0 = pipelines_v1_pipeline_calculation_service_pb2.SimulatePipelineResponse()
            response_1 = pipelines_v1_pipeline_calculation_service_pb2.RecalculatePipelinesResponse()
            response_2 = pipelines_v1_pipeline_calculation_service_pb2.EstimatePipelineResponse()
            outgoing_0 = pipelines_v1_pipeline_calculation_service_pb2.SimulatePipelineRequest()
            outgoing_0.context.CopyFrom(request.context)
            field_0_1_part_1 = outgoing_0.pipeline.participants.add()
            field_0_1_part_1.contact.email = request.pipeline_run.requester.email
            outgoing_0.pipeline.organizer.user_id = request.pipeline_run.assignee.user_id
            outgoing_0.context.tenant_id = tenant_id.get()
            response_0 = await deps.clients.pipelines_pipeline_calculation.SimulatePipeline(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = pipelines_v1_pipeline_calculation_service_pb2.RecalculatePipelinesRequest(
                context=request.context,
                pipeline=pipelines_v1_pipelines_pb2.Pipeline(
                    participants=[
                        pipelines_v1_pipelines_pb2.PipelineParticipant(
                            contact=common_v1_contact_pb2.ContactInfo(
                                email=response_0.pipeline.organizer.email,
                                name=request.pipeline_run.requester.name
                            )
                        )
                    ]
                )
            )
            port_1: PipelineRunCalculationEstimatePipelineRun1Port = PipelineRunCalculationEstimatePipelineRun1Adapter(
                deps.clients.pipelines_pipeline_calculation,
                deps.settings.timeout
            )
            response_1 = await port_1.execute(outgoing_1)
            requests_2: list[pipelines_v1_pipeline_calculation_service_pb2.EstimatePipelineRequest] = []
            for item_2 in request.pipeline_run.comments:
                outgoing_2 = pipelines_v1_pipeline_calculation_service_pb2.EstimatePipelineRequest(
                    context=request.context,
                    pipeline=pipelines_v1_pipelines_pb2.Pipeline(
                        audit=common_v1_audit_pb2.AuditInfo(
                            created_at=item_2.created_at,
                            updated_at=request.pipeline_run.audit.updated_at
                        ),
                        participants=[
                            pipelines_v1_pipelines_pb2.PipelineParticipant(
                                contact=common_v1_contact_pb2.ContactInfo(email=item_2.author_email)
                            )
                        ]
                    )
                )
                requests_2.append(outgoing_2)
            replies_2 = await asyncio.gather(*(
                deps.clients.pipelines_pipeline_calculation.EstimatePipeline(
                    entry,
                    timeout=deps.settings.timeout
                ) for entry in requests_2
            ))
            if replies_2:
                response_2 = replies_2[-1]
            returned_0_0 = response_0.pipeline.organizer.email
            if returned_0_0:
                response.pipeline_run.requester.email = returned_0_0
            returned_0_1 = response_0.breakdown.total
            if returned_0_1.ListFields():
                response.breakdown.total.MergeFrom(returned_0_1)
            returned_1_0 = response_1.pipeline.organizer.email
            if returned_1_0:
                response.pipeline_run.requester.email = returned_1_0
            returned_1_1 = response_1.result.details
            response.result.details.update(returned_1_1)
            echoed_0 = request.pipeline_run_id
            response.pipeline_run.pipeline_run_id = echoed_0
            echoed_1 = request.pipeline_run.subject
            response.pipeline_run.subject = echoed_1
            return response

    async def handle_explain_pipeline_run_calculation(
        self,
        request: pipelines_v1_pipeline_run_calculation_service_pb2.ExplainPipelineRunCalculationRequest
    ) -> pipelines_v1_pipeline_run_calculation_service_pb2.ExplainPipelineRunCalculationResponse:
        """Explains a pipeline run."""
        deps = self.deps
        response = pipelines_v1_pipeline_run_calculation_service_pb2.ExplainPipelineRunCalculationResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ExplainPipelineRunCalculation', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ExplainPipelineRunCalculation',
                {'reason': request.reason}
            )
            await deps.repository.save_pipeline_run(request.context.tenant_id, request.pipeline_run)
            response_0 = ratelimiting_v1_rate_limit_query_service_pb2.ExportRateLimitsResponse()
            response_1 = pipelines_v1_pipeline_calculation_service_pb2.ComparePipelineOptionsResponse()
            response_2 = ticketing_v1_ticket_query_service_pb2.SuggestTicketsResponse()
            for item_0 in request.pipeline_run.comments:
                outgoing_0 = ratelimiting_v1_rate_limit_query_service_pb2.ExportRateLimitsRequest(
                    context=request.context,
                    filter=ratelimiting_v1_rate_limit_query_service_pb2.ExportRateLimitsRequest.Filter(
                        created_after=item_0.created_at,
                        labels=dict(request.annotations),
                        owner_id=item_0.comment_id
                    )
                )
                async for result_0 in deps.clients.ratelimiting_rate_limit_query.ExportRateLimits(
                    outgoing_0,
                    timeout=deps.settings.timeout
                ):
                    response_0 = result_0
            outgoing_1 = pipelines_v1_pipeline_calculation_service_pb2.ComparePipelineOptionsRequest(
                context=request.context,
                pipeline=pipelines_v1_pipelines_pb2.Pipeline(
                    audit=common_v1_audit_pb2.AuditInfo(updated_at=request.pipeline_run.audit.updated_at),
                    participants=[
                        pipelines_v1_pipelines_pb2.PipelineParticipant(
                            contact=common_v1_contact_pb2.ContactInfo(
                                phone=request.pipeline_run.requester.phone,
                                preferred_channel=request.pipeline_run.requester.preferred_channel
                            )
                        )
                    ]
                )
            )
            response_1 = cast(pipelines_v1_pipeline_calculation_service_pb2.ComparePipelineOptionsResponse, await deps.bus.request(
                'acme.pipelines.v1.PipelineRunCalculationService/ExplainPipelineRunCalculation/1', outgoing_1, deps.settings.timeout,
            ))
            outgoing_2 = ticketing_v1_ticket_query_service_pb2.SuggestTicketsRequest(
                context=request.context,
                filter=ticketing_v1_ticket_query_service_pb2.SuggestTicketsRequest.Filter(
                    created_after=response_1.pipeline.audit.created_at,
                    labels=dict(request.pipeline_run.custom_fields),
                    region=response_1.pipeline.location.region
                )
            )
            response_2 = await deps.clients.ticketing_ticket_query.SuggestTickets(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            returned_1_0 = response_1.result.details
            response.result.details.update(returned_1_0)
            returned_2_0 = response_2.result.status
            if returned_2_0:
                response.result.status = returned_2_0
            echoed_0 = request.pipeline_run_id
            response.pipeline_run.pipeline_run_id = echoed_0
            echoed_1 = request.pipeline_run.status
            response.pipeline_run.status = echoed_1
            return response

    async def handle_get_pipeline_run_rates(
        self,
        request: pipelines_v1_pipeline_run_calculation_service_pb2.GetPipelineRunRatesRequest
    ) -> pipelines_v1_pipeline_run_calculation_service_pb2.GetPipelineRunRatesResponse:
        """Returns a pipeline run."""
        deps = self.deps
        response = pipelines_v1_pipeline_run_calculation_service_pb2.GetPipelineRunRatesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('GetPipelineRunRates', extra={'fields': {'domain': 'pipelines'}})
            await deps.repository.audit(request.context.tenant_id, 'GetPipelineRunRates', {})
            response_0 = venues_v1_venue_validation_service_pb2.CheckVenueEligibilityResponse()
            outgoing_0 = venues_v1_venue_validation_service_pb2.CheckVenueEligibilityRequest(
                context=request.context,
                venue=venues_v1_venues_pb2.Venue(owner=identity_v1_refs_pb2.UserRef(email=request.context.actor.email))
            )
            response_0 = await deps.clients.venues_venue_validation.CheckVenueEligibility(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.venue.owner.email
            if returned_0_0:
                response.pipeline_run.requester.email = returned_0_0
            echoed_0 = request.pipeline_run_id
            response.pipeline_run.pipeline_run_id = echoed_0
            return response

    async def handle_quote_pipeline_run(
        self,
        request: pipelines_v1_pipeline_run_calculation_service_pb2.QuotePipelineRunRequest
    ) -> pipelines_v1_pipeline_run_calculation_service_pb2.QuotePipelineRunResponse:
        """Quotes a pipeline run."""
        deps = self.deps
        response = pipelines_v1_pipeline_run_calculation_service_pb2.QuotePipelineRunResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('QuotePipelineRun', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'QuotePipelineRun', {'reason': request.reason})
            await deps.repository.save_pipeline_run(request.context.tenant_id, request.pipeline_run)
            response_0 = pipelines_v1_pipeline_calculation_service_pb2.SimulatePipelineResponse()
            callbacks_0: list[
                Callable[[], Awaitable[pipelines_v1_pipeline_calculation_service_pb2.SimulatePipelineResponse]]
            ] = []
            for item_0 in request.pipeline_run.comments:
                outgoing_0 = pipelines_v1_pipeline_calculation_service_pb2.SimulatePipelineRequest(
                    context=request.context,
                    pipeline=pipelines_v1_pipelines_pb2.Pipeline(
                        audit=common_v1_audit_pb2.AuditInfo(created_at=item_0.created_at),
                        participants=[
                            pipelines_v1_pipelines_pb2.PipelineParticipant(
                                contact=common_v1_contact_pb2.ContactInfo(email=item_0.author_email)
                            )
                        ]
                    )
                )
                async def send_0(
                    payload: pipelines_v1_pipeline_calculation_service_pb2.SimulatePipelineRequest = outgoing_0
                ) -> pipelines_v1_pipeline_calculation_service_pb2.SimulatePipelineResponse:
                    return await deps.clients.pipelines_pipeline_calculation.SimulatePipeline(
                        payload,
                        timeout=deps.settings.timeout
                    )
                callbacks_0.append(send_0)
            for callback_0 in callbacks_0:
                response_0 = await callback_0()
            echoed_0 = request.pipeline_run_id
            response.pipeline_run.pipeline_run_id = echoed_0
            echoed_1 = request.details.currency_code
            response.breakdown.currency_code = echoed_1
            return response

    async def handle_recalculate_pipeline_runs(
        self,
        request: pipelines_v1_pipeline_run_calculation_service_pb2.RecalculatePipelineRunsRequest
    ) -> pipelines_v1_pipeline_run_calculation_service_pb2.RecalculatePipelineRunsResponse:
        """Recalculates a pipeline run."""
        deps = self.deps
        response = pipelines_v1_pipeline_run_calculation_service_pb2.RecalculatePipelineRunsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('RecalculatePipelineRuns', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'RecalculatePipelineRuns',
                {'reason': request.reason}
            )
            await deps.repository.save_pipeline_run(request.context.tenant_id, request.pipeline_run)
            response_0 = metrics_v1_metric_alert_validation_service_pb2.NormalizeMetricAlertResponse()
            outgoing_0 = metrics_v1_metric_alert_validation_service_pb2.NormalizeMetricAlertRequest(
                context=request.context,
                details=metrics_v1_metric_alert_validation_service_pb2.NormalizeMetricAlertRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(
                        name=request.pipeline_run.requester.name,
                        preferred_channel=request.pipeline_run.requester.preferred_channel
                    )
                )
            )
            document_0 = MessageToDict(outgoing_0, preserving_proto_field_name=True)
            outgoing_0 = ParseDict(
                document_0,
                metrics_v1_metric_alert_validation_service_pb2.NormalizeMetricAlertRequest()
            )
            response_0 = await deps.clients.metrics_metric_alert_validation.NormalizeMetricAlert(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.metric_alert.audit.updated_by
            if returned_0_0:
                response.pipeline_run.audit.updated_by = returned_0_0
            returned_0_1 = response_0.metric_alert.owner.email
            if returned_0_1:
                response.pipeline_run.requester.email = returned_0_1
            echoed_0 = request.pipeline_run_id
            response.pipeline_run.pipeline_run_id = echoed_0
            echoed_1 = request.pipeline_run.status
            response.pipeline_run.status = echoed_1
            return response
