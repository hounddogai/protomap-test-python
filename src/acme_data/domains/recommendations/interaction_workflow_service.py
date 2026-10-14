"""Runs the long-lived workflow that takes an interaction from start to finish."""

from __future__ import annotations

from collections.abc import AsyncIterator
from collections.abc import Awaitable
from collections.abc import Callable
from dataclasses import dataclass
from functools import partial
from typing import cast
import asyncio
import logging

from google.protobuf.any_pb2 import Any as AnyMessage
from google.protobuf.json_format import MessageToJson
from google.protobuf.json_format import Parse
import grpc

from acme.campaigns.v1 import marketing_campaign_query_service_pb2 as campaigns_v1_marketing_campaign_query_service_pb2
from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.corporateevents.v1 import corporate_event_service_pb2 as corporateevents_v1_corporate_event_service_pb2
from acme.customers.v1 import (
    customer_segment_calculation_service_pb2 as customers_v1_customer_segment_calculation_service_pb2,
)
from acme.customers.v1 import customer_service_pb2 as customers_v1_customer_service_pb2
from acme.customers.v1 import customers_pb2 as customers_v1_customers_pb2
from acme.customers.v1 import household_query_service_pb2 as customers_v1_household_query_service_pb2
from acme.customers.v1 import refs_pb2 as customers_v1_refs_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.labeling.v1 import label_set_lifecycle_service_pb2 as labeling_v1_label_set_lifecycle_service_pb2
from acme.labeling.v1 import labeling_pb2 as labeling_v1_labeling_pb2
from acme.metrics.v1 import metric_alert_query_service_pb2 as metrics_v1_metric_alert_query_service_pb2
from acme.performers.v1 import performer_service_pb2 as performers_v1_performer_service_pb2
from acme.recommendations.v1 import (
    interaction_calculation_service_pb2 as recommendations_v1_interaction_calculation_service_pb2,
)
from acme.recommendations.v1 import (
    interaction_lifecycle_service_pb2 as recommendations_v1_interaction_lifecycle_service_pb2,
)
from acme.recommendations.v1 import (
    interaction_lifecycle_service_pb2_grpc as recommendations_v1_interaction_lifecycle_service_pb2_grpc,
)
from acme.recommendations.v1 import (
    interaction_workflow_service_pb2 as recommendations_v1_interaction_workflow_service_pb2,
)
from acme.recommendations.v1 import (
    interaction_workflow_service_pb2_grpc as recommendations_v1_interaction_workflow_service_pb2_grpc,
)
from acme.recommendations.v1 import (
    recommendation_model_calculation_service_pb2 as recommendations_v1_recommendation_model_calculation_service_pb2,
)
from acme.recommendations.v1 import (
    recommendation_model_workflow_service_pb2 as recommendations_v1_recommendation_model_workflow_service_pb2,
)
from acme.recommendations.v1 import (
    recommendation_set_approval_service_pb2 as recommendations_v1_recommendation_set_approval_service_pb2,
)
from acme.recommendations.v1 import recommendation_set_service_pb2 as recommendations_v1_recommendation_set_service_pb2
from acme.recommendations.v1 import recommendations_pb2 as recommendations_v1_recommendations_pb2
from acme.venues.v1 import venue_service_pb2 as venues_v1_venue_service_pb2
from acme.venues.v1 import venues_pb2 as venues_v1_venues_pb2

from acme_data.domains.recommendations.adapters import InteractionWorkflowResumeInteractionWorkflow2Adapter
from acme_data.domains.recommendations.adapters import InteractionWorkflowResumeInteractionWorkflow2Port
from acme_data.domains.recommendations.adapters import InteractionWorkflowSignalInteractionWorkflow1Adapter
from acme_data.domains.recommendations.dependencies import Dependencies
from acme_data.domains.recommendations.models import InteractionWorkflowListInteractionWorkflows1Command
from acme_data.domains.recommendations.models import to_interaction_workflow_list_interaction_workflows1_command
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import run_steps
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_id
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


@dataclass(slots=True)
class InteractionWorkflowServicer(
    recommendations_v1_interaction_workflow_service_pb2_grpc.InteractionWorkflowServiceServicer
):
    deps: Dependencies

    @rpc_errors
    async def AdvanceInteractionWorkflow(
        self, request: recommendations_v1_interaction_workflow_service_pb2.AdvanceInteractionWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> recommendations_v1_interaction_workflow_service_pb2.AdvanceInteractionWorkflowResponse:
        """Advances an interaction."""
        return await self.handle_advance_interaction_workflow(request)

    @rpc_errors
    @retry_transient
    async def InspectInteractionWorkflow(
        self, request: recommendations_v1_interaction_workflow_service_pb2.InspectInteractionWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> recommendations_v1_interaction_workflow_service_pb2.InspectInteractionWorkflowResponse:
        """Returns an interaction."""
        return await self.handle_inspect_interaction_workflow(request)

    @rpc_errors
    @retry_transient
    async def ListInteractionWorkflows(
        self, request: recommendations_v1_interaction_workflow_service_pb2.ListInteractionWorkflowsRequest, context: grpc.aio.ServicerContext,
    ) -> recommendations_v1_interaction_workflow_service_pb2.ListInteractionWorkflowsResponse:
        """Lists interactions a page at a time."""
        return await self.handle_list_interaction_workflows(request)

    @rpc_errors
    async def PauseInteractionWorkflow(
        self, request: recommendations_v1_interaction_workflow_service_pb2.PauseInteractionWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> recommendations_v1_interaction_workflow_service_pb2.PauseInteractionWorkflowResponse:
        """Pauses an interaction."""
        return await self.handle_pause_interaction_workflow(request)

    @rpc_errors
    async def ResumeInteractionWorkflow(
        self, request: recommendations_v1_interaction_workflow_service_pb2.ResumeInteractionWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> recommendations_v1_interaction_workflow_service_pb2.ResumeInteractionWorkflowResponse:
        """Resumes an interaction."""
        return await self.handle_resume_interaction_workflow(request)

    @rpc_errors
    async def SignalInteractionWorkflow(
        self, request: recommendations_v1_interaction_workflow_service_pb2.SignalInteractionWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> recommendations_v1_interaction_workflow_service_pb2.SignalInteractionWorkflowResponse:
        """Signals an interaction."""
        return await self.handle_signal_interaction_workflow(request)

    @rpc_errors
    async def StartInteractionWorkflow(
        self, request: recommendations_v1_interaction_workflow_service_pb2.StartInteractionWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> recommendations_v1_interaction_workflow_service_pb2.StartInteractionWorkflowResponse:
        """Starts an interaction."""
        return await self.handle_start_interaction_workflow(request)

    async def handle_advance_interaction_workflow(
        self,
        request: recommendations_v1_interaction_workflow_service_pb2.AdvanceInteractionWorkflowRequest
    ) -> recommendations_v1_interaction_workflow_service_pb2.AdvanceInteractionWorkflowResponse:
        """Advances an interaction."""
        deps = self.deps
        response = recommendations_v1_interaction_workflow_service_pb2.AdvanceInteractionWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('AdvanceInteractionWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'AdvanceInteractionWorkflow',
                {'reason': request.reason}
            )
            await deps.repository.save_interaction(request.context.tenant_id, request.interaction)
            response_0 = recommendations_v1_recommendation_model_calculation_service_pb2.SimulateRecommendationModelResponse()
            response_1 = recommendations_v1_interaction_calculation_service_pb2.CompareInteractionOptionsResponse()
            response_2 = recommendations_v1_recommendation_set_service_pb2.UpdateRecommendationSetResponse()
            response_3 = recommendations_v1_interaction_lifecycle_service_pb2.RenewInteractionResponse()
            outgoing_0 = recommendations_v1_recommendation_model_calculation_service_pb2.SimulateRecommendationModelRequest(
                context=request.context,
                recommendation_model=recommendations_v1_recommendations_pb2.RecommendationModel(
                    owner=identity_v1_refs_pb2.UserRef(
                        display_name=request.interaction.subject.display_name,
                        email=request.interaction.subject.email,
                        user_id=request.context.actor.user_id
                    )
                )
            )
            document_0 = MessageToJson(outgoing_0, preserving_proto_field_name=True)
            outgoing_0 = Parse(
                document_0,
                recommendations_v1_recommendation_model_calculation_service_pb2.SimulateRecommendationModelRequest()
            )
            response_0 = await deps.clients.recommendations_recommendation_model_calculation.SimulateRecommendationModel(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = recommendations_v1_interaction_calculation_service_pb2.CompareInteractionOptionsRequest()
            outgoing_1.context.CopyFrom(request.context)
            outgoing_1.details.destination.country_code = response_0.recommendation_model.address.country_code
            outgoing_1.interaction.subject.email = request.details.notify.email
            merged_1 = recommendations_v1_interaction_calculation_service_pb2.CompareInteractionOptionsRequest()
            merged_1.MergeFrom(outgoing_1)
            outgoing_1.CopyFrom(merged_1)
            response_1 = await deps.clients.recommendations_interaction_calculation.CompareInteractionOptions(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = recommendations_v1_recommendation_set_service_pb2.UpdateRecommendationSetRequest(
                context=request.context,
                recommendation_set=recommendations_v1_recommendations_pb2.RecommendationSet(
                    counterparty=customers_v1_refs_pb2.CustomerRef(
                        display_name=response_1.interaction.subject.display_name,
                        email=request.details.notify.email
                    )
                )
            )
            envelope_2 = AnyMessage()
            envelope_2.Pack(outgoing_2)
            outgoing_2 = recommendations_v1_recommendation_set_service_pb2.UpdateRecommendationSetRequest()
            if not envelope_2.Unpack(outgoing_2):
                raise ValueError("partner envelope contains the wrong request type")
            response_2 = await deps.clients.recommendations_recommendation_set.UpdateRecommendationSet(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            outgoing_3 = recommendations_v1_interaction_lifecycle_service_pb2.RenewInteractionRequest(
                context=request.context,
                details=recommendations_v1_interaction_lifecycle_service_pb2.RenewInteractionRequest.Details(
                    new_owner=identity_v1_refs_pb2.UserRef(
                        display_name=response_1.interaction.subject.display_name,
                        email=response_1.interaction.subject.email
                    ),
                    notify_contact=common_v1_contact_pb2.ContactInfo(
                        phone=request.details.notify.phone,
                        preferred_channel=request.details.notify.preferred_channel
                    )
                ),
                interaction_id=request.interaction.interaction_id
            )
            registered_3 = cast(
                recommendations_v1_interaction_lifecycle_service_pb2_grpc.InteractionLifecycleServiceStub,
                deps.clients.registry['acme.recommendations.v1.InteractionLifecycleService']
            )
            response_3 = await registered_3.RenewInteraction(outgoing_3, timeout=deps.settings.timeout)
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.result.message = returned_0_0
            returned_1_0 = response_1.interaction.subject.email
            if returned_1_0:
                response.interaction.subject.email = returned_1_0
            returned_1_1 = response_1.result.correlation_id
            if returned_1_1:
                response.interaction.correlation_id = returned_1_1
            returned_2_0 = response_2.recommendation_set.counterparty.customer_id
            if returned_2_0:
                response.interaction.subject.customer_id = returned_2_0
            returned_2_1 = response_2.result.details
            response.result.details.update(returned_2_1)
            returned_3_0 = response_3.result.correlation_id
            if returned_3_0:
                response.interaction.correlation_id = returned_3_0
            echoed_0 = request.interaction_id
            response.interaction.interaction_id = echoed_0
            echoed_1 = request.interaction.correlation_id
            response.result.correlation_id = echoed_1
            return response

    async def handle_inspect_interaction_workflow(
        self,
        request: recommendations_v1_interaction_workflow_service_pb2.InspectInteractionWorkflowRequest
    ) -> recommendations_v1_interaction_workflow_service_pb2.InspectInteractionWorkflowResponse:
        """Returns an interaction."""
        deps = self.deps
        response = recommendations_v1_interaction_workflow_service_pb2.InspectInteractionWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('InspectInteractionWorkflow', extra={'fields': {'locale': request.context.locale}})
            await deps.repository.audit(
                request.context.tenant_id,
                'InspectInteractionWorkflow',
                {'locale': request.context.locale}
            )
            echoed_0 = request.interaction_id
            response.interaction.interaction_id = echoed_0
            return response

    async def handle_list_interaction_workflows(
        self,
        request: recommendations_v1_interaction_workflow_service_pb2.ListInteractionWorkflowsRequest
    ) -> recommendations_v1_interaction_workflow_service_pb2.ListInteractionWorkflowsResponse:
        """Lists interactions a page at a time."""
        deps = self.deps
        response = recommendations_v1_interaction_workflow_service_pb2.ListInteractionWorkflowsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ListInteractionWorkflows', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ListInteractionWorkflows',
                {'order_by': request.order_by}
            )
            response_0 = performers_v1_performer_service_pb2.ListPerformersResponse()
            response_1 = campaigns_v1_marketing_campaign_query_service_pb2.ResolveMarketingCampaignsResponse()
            outgoing_0 = performers_v1_performer_service_pb2.ListPerformersRequest(
                context=request.context,
                filter=performers_v1_performer_service_pb2.ListPerformersRequest.Filter(
                    query=request.filter.query,
                    region=request.filter.region
                )
            )
            response_0 = await deps.clients.performers_performer.ListPerformers(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            command_1 = InteractionWorkflowListInteractionWorkflows1Command.model_validate({'context': request.context})
            outgoing_1 = to_interaction_workflow_list_interaction_workflows1_command(command_1)
            response_1 = await deps.clients.campaigns_marketing_campaign_query.ResolveMarketingCampaigns(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_0)
            returned_1_0 = response_1.page_info.total_size
            if returned_1_0:
                response.page_info.total_size = returned_1_0
            return response

    async def handle_pause_interaction_workflow(
        self,
        request: recommendations_v1_interaction_workflow_service_pb2.PauseInteractionWorkflowRequest
    ) -> recommendations_v1_interaction_workflow_service_pb2.PauseInteractionWorkflowResponse:
        """Pauses an interaction."""
        deps = self.deps
        response = recommendations_v1_interaction_workflow_service_pb2.PauseInteractionWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('PauseInteractionWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'PauseInteractionWorkflow',
                {'reason': request.reason}
            )
            await deps.repository.save_interaction(request.context.tenant_id, request.interaction)
            response_0 = customers_v1_household_query_service_pb2.ResolveHouseholdsResponse()
            outgoing_0 = customers_v1_household_query_service_pb2.ResolveHouseholdsRequest(context=request.context)
            send_0 = partial(deps.clients.customers_household_query.ResolveHouseholds, timeout=deps.settings.timeout)
            response_0 = await send_0(outgoing_0)
            returned_0_0 = response_0.result.status
            if returned_0_0:
                response.result.status = returned_0_0
            echoed_0 = request.interaction_id
            response.interaction.interaction_id = echoed_0
            echoed_1 = request.interaction.correlation_id
            response.interaction.correlation_id = echoed_1
            return response

    async def handle_resume_interaction_workflow(
        self,
        request: recommendations_v1_interaction_workflow_service_pb2.ResumeInteractionWorkflowRequest
    ) -> recommendations_v1_interaction_workflow_service_pb2.ResumeInteractionWorkflowResponse:
        """Resumes an interaction."""
        deps = self.deps
        response = recommendations_v1_interaction_workflow_service_pb2.ResumeInteractionWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ResumeInteractionWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ResumeInteractionWorkflow',
                {'reason': request.reason}
            )
            await deps.repository.save_interaction(request.context.tenant_id, request.interaction)
            response_0 = recommendations_v1_recommendation_set_approval_service_pb2.RecallRecommendationSetResponse()
            response_1 = corporateevents_v1_corporate_event_service_pb2.CreateCorporateEventResponse()
            response_2 = recommendations_v1_recommendation_model_workflow_service_pb2.AdvanceRecommendationModelWorkflowResponse()
            for item_0 in request.interaction.measurements:
                outgoing_0 = recommendations_v1_recommendation_set_approval_service_pb2.RecallRecommendationSetRequest(
                    context=request.context,
                    details=recommendations_v1_recommendation_set_approval_service_pb2.RecallRecommendationSetRequest.Details(
                        approver=identity_v1_refs_pb2.UserRef(email=request.interaction.subject.email)
                    ),
                    recommendation_set=recommendations_v1_recommendations_pb2.RecommendationSet(
                        audit=common_v1_audit_pb2.AuditInfo(updated_at=item_0.observed_at),
                        counterparty=customers_v1_refs_pb2.CustomerRef(
                            display_name=request.interaction.subject.display_name,
                            email=request.details.notify.email
                        )
                    )
                )
                response_0 = await deps.clients.recommendations_recommendation_set_approval.RecallRecommendationSet(
                    outgoing_0,
                    timeout=deps.settings.timeout
                )
            outgoing_1 = corporateevents_v1_corporate_event_service_pb2.CreateCorporateEventRequest()
            outgoing_1.context.CopyFrom(request.context)
            field_1_1_part_1 = outgoing_1.corporate_event.participants.add()
            field_1_1_part_1.contact.phone = request.details.notify.phone
            field_1_2_part_1 = outgoing_1.corporate_event.participants.add()
            field_1_2_part_1.contact.name.CopyFrom(request.details.notify.name)
            outgoing_1.corporate_event.location.postal_code = response_0.recommendation_set.billing_address.postal_code
            outgoing_1.corporate_event.audit.created_by = response_0.recommendation_set.audit.created_by
            outgoing_1.context.tenant_id = tenant_id.get()
            response_1 = await deps.clients.corporateevents_corporate_event.CreateCorporateEvent(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = recommendations_v1_recommendation_model_workflow_service_pb2.AdvanceRecommendationModelWorkflowRequest(
                context=request.context,
                recommendation_model=recommendations_v1_recommendations_pb2.RecommendationModel(
                    address=common_v1_address_pb2.PostalAddress(
                        country_code=response_1.corporate_event.location.country_code,
                        postal_code=response_0.recommendation_set.billing_address.postal_code
                    ),
                    audit=common_v1_audit_pb2.AuditInfo(created_at=response_0.recommendation_set.audit.created_at)
                )
            )
            port_2: InteractionWorkflowResumeInteractionWorkflow2Port = InteractionWorkflowResumeInteractionWorkflow2Adapter(
                deps.clients.recommendations_recommendation_model_workflow,
                deps.settings.timeout
            )
            response_2 = await port_2.execute(outgoing_2)
            returned_1_0 = response_1.result.status
            if returned_1_0:
                response.result.status = returned_1_0
            returned_2_0 = response_2.result.status
            if returned_2_0:
                response.outcome.status = returned_2_0
            returned_2_1 = response_2.result.correlation_id
            if returned_2_1:
                response.result.correlation_id = returned_2_1
            echoed_0 = request.interaction_id
            response.interaction.interaction_id = echoed_0
            echoed_1 = request.interaction.correlation_id
            response.interaction.correlation_id = echoed_1
            return response

    async def handle_signal_interaction_workflow(
        self,
        request: recommendations_v1_interaction_workflow_service_pb2.SignalInteractionWorkflowRequest
    ) -> recommendations_v1_interaction_workflow_service_pb2.SignalInteractionWorkflowResponse:
        """Signals an interaction."""
        deps = self.deps
        response = recommendations_v1_interaction_workflow_service_pb2.SignalInteractionWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SignalInteractionWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'SignalInteractionWorkflow',
                {'reason': request.reason}
            )
            await deps.repository.save_interaction(request.context.tenant_id, request.interaction)
            response_0 = metrics_v1_metric_alert_query_service_pb2.CountMetricAlertsResponse()
            response_1 = labeling_v1_label_set_lifecycle_service_pb2.ScheduleLabelSetExpiryResponse()
            response_2 = customers_v1_customer_segment_calculation_service_pb2.SimulateCustomerSegmentResponse()
            response_3 = recommendations_v1_recommendation_model_workflow_service_pb2.CancelRecommendationModelWorkflowResponse()
            outgoing_0 = metrics_v1_metric_alert_query_service_pb2.CountMetricAlertsRequest(
                context=request.context,
                filter=metrics_v1_metric_alert_query_service_pb2.CountMetricAlertsRequest.Filter(
                    created_after=request.interaction.occurred_at,
                    labels=dict(request.annotations),
                    owner_id=request.interaction.subject.customer_id
                )
            )
            steps_0 = [
                partial(
                    deps.clients.metrics_metric_alert_query.CountMetricAlerts,
                    outgoing_0,
                    timeout=deps.settings.timeout
                )
            ]
            results_0 = await run_steps(steps_0)
            response_0 = results_0[-1]
            outgoing_1 = labeling_v1_label_set_lifecycle_service_pb2.ScheduleLabelSetExpiryRequest(
                context=request.context,
                label_set=labeling_v1_labeling_pb2.LabelSet(
                    manager=identity_v1_refs_pb2.UserRef(email=request.details.notify.email)
                )
            )
            response_1 = await InteractionWorkflowSignalInteractionWorkflow1Adapter(
                deps.clients.labeling_label_set_lifecycle,
                deps.settings.timeout
            )(outgoing_1)
            outgoing_2 = customers_v1_customer_segment_calculation_service_pb2.SimulateCustomerSegmentRequest(
                context=request.context,
                customer_segment=customers_v1_customers_pb2.CustomerSegment(
                    owner=identity_v1_refs_pb2.UserRef(
                        display_name=response_1.label_set.manager.display_name,
                        email=response_1.label_set.manager.email
                    )
                ),
                details=customers_v1_customer_segment_calculation_service_pb2.SimulateCustomerSegmentRequest.Details(
                    destination=common_v1_address_pb2.PostalAddress(region=response_1.label_set.location.region)
                )
            )
            response_2 = cast(customers_v1_customer_segment_calculation_service_pb2.SimulateCustomerSegmentResponse, await deps.bus.request(
                'acme.recommendations.v1.InteractionWorkflowService/SignalInteractionWorkflow/2', outgoing_2, deps.settings.timeout,
            ))
            requests_3: list[
                recommendations_v1_recommendation_model_workflow_service_pb2.CancelRecommendationModelWorkflowRequest
            ] = []
            for item_3 in request.interaction.measurements:
                outgoing_3 = recommendations_v1_recommendation_model_workflow_service_pb2.CancelRecommendationModelWorkflowRequest(
                    context=request.context,
                    details=recommendations_v1_recommendation_model_workflow_service_pb2.CancelRecommendationModelWorkflowRequest.Details(
                        notify=common_v1_contact_pb2.ContactInfo(
                            preferred_channel=request.details.notify.preferred_channel
                        )
                    ),
                    recommendation_model=recommendations_v1_recommendations_pb2.RecommendationModel(
                        dimensions=recommendations_v1_recommendations_pb2.RecommendationModelDimensions(
                            unit=item_3.unit
                        )
                    )
                )
                requests_3.append(outgoing_3)
            replies_3 = await asyncio.gather(*(
                deps.clients.recommendations_recommendation_model_workflow.CancelRecommendationModelWorkflow(
                    entry,
                    timeout=deps.settings.timeout
                ) for entry in requests_3
            ))
            if replies_3:
                response_3 = replies_3[-1]
            returned_0_0 = response_0.result.details
            response.result.details.update(returned_0_0)
            returned_1_0 = response_1.outcome.status
            if returned_1_0:
                response.result.status = returned_1_0
            returned_1_1 = response_1.outcome.message
            if returned_1_1:
                response.outcome.message = returned_1_1
            returned_2_0 = response_2.result.correlation_id
            if returned_2_0:
                response.result.correlation_id = returned_2_0
            echoed_0 = request.interaction_id
            response.interaction.interaction_id = echoed_0
            echoed_1 = request.interaction.sequence
            response.interaction.sequence = echoed_1
            return response

    async def handle_start_interaction_workflow(
        self,
        request: recommendations_v1_interaction_workflow_service_pb2.StartInteractionWorkflowRequest
    ) -> recommendations_v1_interaction_workflow_service_pb2.StartInteractionWorkflowResponse:
        """Starts an interaction."""
        deps = self.deps
        response = recommendations_v1_interaction_workflow_service_pb2.StartInteractionWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('StartInteractionWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'StartInteractionWorkflow',
                {'reason': request.reason}
            )
            await deps.repository.save_interaction(request.context.tenant_id, request.interaction)
            response_0 = venues_v1_venue_service_pb2.CreateVenueResponse()
            response_1 = customers_v1_customer_service_pb2.ListCustomersResponse()
            outgoing_0 = venues_v1_venue_service_pb2.CreateVenueRequest(
                context=request.context,
                venue=venues_v1_venues_pb2.Venue(
                    owner=identity_v1_refs_pb2.UserRef(
                        display_name=request.interaction.subject.display_name,
                        email=request.details.notify.email,
                        user_id=request.context.actor.user_id
                    )
                )
            )
            method_name_0 = 'CreateVenue'
            response_0 = await getattr(deps.clients.venues_venue, method_name_0)(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            callbacks_1: list[Callable[[], Awaitable[customers_v1_customer_service_pb2.ListCustomersResponse]]] = []
            for item_1 in request.interaction.measurements:
                outgoing_1 = customers_v1_customer_service_pb2.ListCustomersRequest(
                    context=request.context,
                    filter=customers_v1_customer_service_pb2.ListCustomersRequest.Filter(
                        created_after=item_1.observed_at,
                        owner_id=response_0.venue.components.get(
                            'primary',
                            venues_v1_venues_pb2.VenueComponent()
                        ).component_id,
                        region=response_0.venue.address.region
                    )
                )
                async def send_1(
                    payload: customers_v1_customer_service_pb2.ListCustomersRequest = outgoing_1
                ) -> customers_v1_customer_service_pb2.ListCustomersResponse:
                    return await deps.clients.customers_customer.ListCustomers(payload, timeout=deps.settings.timeout)
                callbacks_1.append(send_1)
            for callback_1 in callbacks_1:
                response_1 = await callback_1()
            returned_0_0 = response_0.result.details
            response.result.details.update(returned_0_0)
            returned_0_1 = response_0.venue.owner.display_name
            if returned_0_1:
                response.interaction.subject.display_name = returned_0_1
            echoed_0 = request.interaction_id
            response.interaction.interaction_id = echoed_0
            echoed_1 = request.interaction.sequence
            response.interaction.sequence = echoed_1
            return response
