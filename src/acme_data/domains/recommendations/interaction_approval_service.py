"""Routes interactions through approval, with escalation and delegation."""

from __future__ import annotations

from collections.abc import AsyncIterator
from collections.abc import Awaitable
from collections.abc import Callable
from functools import partial
from typing import cast
import asyncio
import logging

from google.protobuf.any_pb2 import Any as AnyMessage
from google.protobuf.json_format import MessageToJson
from google.protobuf.json_format import Parse
import grpc

from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.customers.v1 import (
    customer_segment_calculation_service_pb2 as customers_v1_customer_segment_calculation_service_pb2,
)
from acme.customers.v1 import customer_validation_service_pb2 as customers_v1_customer_validation_service_pb2
from acme.customers.v1 import customers_pb2 as customers_v1_customers_pb2
from acme.customers.v1 import household_query_service_pb2 as customers_v1_household_query_service_pb2
from acme.customers.v1 import preference_calculation_service_pb2 as customers_v1_preference_calculation_service_pb2
from acme.customers.v1 import refs_pb2 as customers_v1_refs_pb2
from acme.featureflags.v1 import (
    feature_flag_validation_service_pb2 as featureflags_v1_feature_flag_validation_service_pb2,
)
from acme.featureflags.v1 import (
    feature_flag_validation_service_pb2_grpc as featureflags_v1_feature_flag_validation_service_pb2_grpc,
)
from acme.featureflags.v1 import featureflags_pb2 as featureflags_v1_featureflags_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.lineage.v1 import impact_sync_service_pb2 as lineage_v1_impact_sync_service_pb2
from acme.lineage.v1 import lineage_pb2 as lineage_v1_lineage_pb2
from acme.pipelines.v1 import pipeline_lifecycle_service_pb2 as pipelines_v1_pipeline_lifecycle_service_pb2
from acme.pipelines.v1 import pipelines_pb2 as pipelines_v1_pipelines_pb2
from acme.recommendations.v1 import (
    interaction_approval_service_pb2 as recommendations_v1_interaction_approval_service_pb2,
)
from acme.recommendations.v1 import (
    interaction_approval_service_pb2_grpc as recommendations_v1_interaction_approval_service_pb2_grpc,
)
from acme.recommendations.v1 import (
    interaction_lifecycle_service_pb2 as recommendations_v1_interaction_lifecycle_service_pb2,
)
from acme.recommendations.v1 import (
    interaction_validation_service_pb2 as recommendations_v1_interaction_validation_service_pb2,
)
from acme.recommendations.v1 import (
    recommendation_model_validation_service_pb2 as recommendations_v1_recommendation_model_validation_service_pb2,
)
from acme.recommendations.v1 import (
    recommendation_set_approval_service_pb2 as recommendations_v1_recommendation_set_approval_service_pb2,
)
from acme.recommendations.v1 import (
    recommendation_set_validation_service_pb2 as recommendations_v1_recommendation_set_validation_service_pb2,
)
from acme.recommendations.v1 import recommendations_pb2 as recommendations_v1_recommendations_pb2

from acme_data.domains.recommendations import hooks
from acme_data.domains.recommendations.adapters import InteractionApprovalDelegateInteractionApproval1Adapter
from acme_data.domains.recommendations.adapters import InteractionApprovalDelegateInteractionApproval1Port
from acme_data.domains.recommendations.adapters import InteractionApprovalRecallInteraction0Adapter
from acme_data.domains.recommendations.dependencies import Dependencies
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_id
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class InteractionApprovalServicer(
    recommendations_v1_interaction_approval_service_pb2_grpc.InteractionApprovalServiceServicer
):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    async def ApproveInteraction(
        self, request: recommendations_v1_interaction_approval_service_pb2.ApproveInteractionRequest, context: grpc.aio.ServicerContext,
    ) -> recommendations_v1_interaction_approval_service_pb2.ApproveInteractionResponse:
        """Approves an interaction."""
        return await self.handle_approve_interaction(request)

    @rpc_errors
    async def CommentInteractionApproval(
        self, request: recommendations_v1_interaction_approval_service_pb2.CommentInteractionApprovalRequest, context: grpc.aio.ServicerContext,
    ) -> recommendations_v1_interaction_approval_service_pb2.CommentInteractionApprovalResponse:
        """Comments an interaction."""
        return await self.handle_comment_interaction_approval(request)

    @rpc_errors
    async def DelegateInteractionApproval(
        self, request: recommendations_v1_interaction_approval_service_pb2.DelegateInteractionApprovalRequest, context: grpc.aio.ServicerContext,
    ) -> recommendations_v1_interaction_approval_service_pb2.DelegateInteractionApprovalResponse:
        """Delegates an interaction."""
        return await self.handle_delegate_interaction_approval(request)

    @rpc_errors
    @retry_transient
    async def GetInteractionApprovalStatus(
        self, request: recommendations_v1_interaction_approval_service_pb2.GetInteractionApprovalStatusRequest, context: grpc.aio.ServicerContext,
    ) -> recommendations_v1_interaction_approval_service_pb2.GetInteractionApprovalStatusResponse:
        """Returns an interaction."""
        return await self.handle_get_interaction_approval_status(request)

    @rpc_errors
    @retry_transient
    async def ListPendingInteractions(
        self, request: recommendations_v1_interaction_approval_service_pb2.ListPendingInteractionsRequest, context: grpc.aio.ServicerContext,
    ) -> recommendations_v1_interaction_approval_service_pb2.ListPendingInteractionsResponse:
        """Lists interactions a page at a time."""
        return await self.handle_list_pending_interactions(request)

    @rpc_errors
    async def RecallInteraction(
        self, request: recommendations_v1_interaction_approval_service_pb2.RecallInteractionRequest, context: grpc.aio.ServicerContext,
    ) -> recommendations_v1_interaction_approval_service_pb2.RecallInteractionResponse:
        """Recalls an interaction."""
        return await self.handle_recall_interaction(request)

    @rpc_errors
    async def SubmitInteraction(
        self, request: recommendations_v1_interaction_approval_service_pb2.SubmitInteractionRequest, context: grpc.aio.ServicerContext,
    ) -> recommendations_v1_interaction_approval_service_pb2.SubmitInteractionResponse:
        """Submits an interaction."""
        return await self.handle_submit_interaction(request)

    async def handle_approve_interaction(
        self,
        request: recommendations_v1_interaction_approval_service_pb2.ApproveInteractionRequest
    ) -> recommendations_v1_interaction_approval_service_pb2.ApproveInteractionResponse:
        """Approves an interaction."""
        deps = self.deps
        response = recommendations_v1_interaction_approval_service_pb2.ApproveInteractionResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ApproveInteraction', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'ApproveInteraction', {'reason': request.reason})
            await deps.repository.save_interaction(request.context.tenant_id, request.interaction)
            response_0 = lineage_v1_impact_sync_service_pb2.PushImpactResponse()
            response_1 = recommendations_v1_interaction_validation_service_pb2.ScoreInteractionResponse()
            response_2 = customers_v1_preference_calculation_service_pb2.SimulatePreferenceResponse()
            response_3 = featureflags_v1_feature_flag_validation_service_pb2.ExplainFeatureFlagDecisionResponse()
            outgoing_0 = lineage_v1_impact_sync_service_pb2.PushImpactRequest(
                context=request.context,
                impact=lineage_v1_lineage_pb2.Impact(
                    customer=customers_v1_refs_pb2.CustomerRef(display_name=request.details.approver.display_name)
                )
            )
            document_0 = MessageToJson(outgoing_0, preserving_proto_field_name=True)
            outgoing_0 = Parse(document_0, lineage_v1_impact_sync_service_pb2.PushImpactRequest())
            response_0 = await deps.clients.lineage_impact_sync.PushImpact(outgoing_0, timeout=deps.settings.timeout)
            outgoing_1 = recommendations_v1_interaction_validation_service_pb2.ScoreInteractionRequest()
            outgoing_1.context.CopyFrom(request.context)
            outgoing_1.interaction.subject.email = response_0.impact.customer.email
            outgoing_1.interaction.subject.display_name = request.details.approver.display_name
            outgoing_1.interaction.occurred_at.CopyFrom(request.interaction.occurred_at)
            merged_1 = recommendations_v1_interaction_validation_service_pb2.ScoreInteractionRequest()
            merged_1.MergeFrom(outgoing_1)
            outgoing_1.CopyFrom(merged_1)
            response_1 = await deps.clients.recommendations_interaction_validation.ScoreInteraction(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = customers_v1_preference_calculation_service_pb2.SimulatePreferenceRequest(
                context=request.context,
                preference=customers_v1_customers_pb2.Preference(
                    audit=common_v1_audit_pb2.AuditInfo(etag=response_0.impact.audit.etag),
                    owner=identity_v1_refs_pb2.UserRef(email=response_0.impact.requester.email)
                )
            )
            envelope_2 = AnyMessage()
            envelope_2.Pack(outgoing_2)
            outgoing_2 = customers_v1_preference_calculation_service_pb2.SimulatePreferenceRequest()
            if not envelope_2.Unpack(outgoing_2):
                raise ValueError("partner envelope contains the wrong request type")
            response_2 = await deps.clients.customers_preference_calculation.SimulatePreference(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            outgoing_3 = featureflags_v1_feature_flag_validation_service_pb2.ExplainFeatureFlagDecisionRequest(
                context=request.context,
                feature_flag=featureflags_v1_featureflags_pb2.FeatureFlag(
                    audit=common_v1_audit_pb2.AuditInfo(updated_at=response_2.preference.audit.updated_at),
                    discount=featureflags_v1_featureflags_pb2.FeatureFlagDiscountAction(
                        percent=response_2.preference.discount.percent
                    )
                )
            )
            registered_3 = cast(
                featureflags_v1_feature_flag_validation_service_pb2_grpc.FeatureFlagValidationServiceStub,
                deps.clients.registry['acme.featureflags.v1.FeatureFlagValidationService']
            )
            response_3 = await registered_3.ExplainFeatureFlagDecision(outgoing_3, timeout=deps.settings.timeout)
            returned_0_0 = response_0.outcome.message
            if returned_0_0:
                response.result.message = returned_0_0
            returned_1_0 = response_1.interaction.correlation_id
            if returned_1_0:
                response.interaction.correlation_id = returned_1_0
            returned_2_0 = response_2.preference.owner.email
            if returned_2_0:
                response.interaction.subject.email = returned_2_0
            returned_2_1 = response_2.result.message
            if returned_2_1:
                response.outcome.message = returned_2_1
            returned_3_0 = response_3.result.message
            if returned_3_0:
                response.outcome.message = returned_3_0
            returned_3_1 = response_3.outcome.status
            if returned_3_1:
                response.result.status = returned_3_1
            echoed_0 = request.interaction_id
            response.interaction.interaction_id = echoed_0
            echoed_1 = request.details.effective_at
            response.outcome.effective_at.CopyFrom(echoed_1)
            return response

    async def handle_comment_interaction_approval(
        self,
        request: recommendations_v1_interaction_approval_service_pb2.CommentInteractionApprovalRequest
    ) -> recommendations_v1_interaction_approval_service_pb2.CommentInteractionApprovalResponse:
        """Comments an interaction."""
        deps = self.deps
        response = recommendations_v1_interaction_approval_service_pb2.CommentInteractionApprovalResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CommentInteractionApproval', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'CommentInteractionApproval',
                {'reason': request.reason}
            )
            await deps.repository.save_interaction(request.context.tenant_id, request.interaction)
            response_0 = recommendations_v1_recommendation_model_validation_service_pb2.ScoreRecommendationModelResponse()
            response_1 = recommendations_v1_recommendation_model_validation_service_pb2.ExplainRecommendationModelDecisionResponse()
            response_2 = recommendations_v1_interaction_lifecycle_service_pb2.RenewInteractionResponse()
            response_3 = pipelines_v1_pipeline_lifecycle_service_pb2.SchedulePipelineExpiryResponse()
            requests_0: list[
                recommendations_v1_recommendation_model_validation_service_pb2.ScoreRecommendationModelRequest
            ] = []
            for item_0 in request.interaction.measurements:
                outgoing_0 = recommendations_v1_recommendation_model_validation_service_pb2.ScoreRecommendationModelRequest(
                    context=request.context,
                    recommendation_model=recommendations_v1_recommendations_pb2.RecommendationModel(
                        dimensions=recommendations_v1_recommendations_pb2.RecommendationModelDimensions(
                            unit=item_0.unit
                        )
                    )
                )
                requests_0.append(outgoing_0)
            replies_0 = await asyncio.gather(*(
                deps.clients.recommendations_recommendation_model_validation.ScoreRecommendationModel(
                    entry,
                    timeout=deps.settings.timeout
                ) for entry in requests_0
            ))
            if replies_0:
                response_0 = replies_0[-1]
            callbacks_1: list[
                Callable[
                    [],
                    Awaitable[
                        recommendations_v1_recommendation_model_validation_service_pb2.ExplainRecommendationModelDecisionResponse
                    ]
                ]
            ] = []
            for item_1 in request.interaction.measurements:
                outgoing_1 = recommendations_v1_recommendation_model_validation_service_pb2.ExplainRecommendationModelDecisionRequest(
                    context=request.context,
                    recommendation_model=recommendations_v1_recommendations_pb2.RecommendationModel(
                        dimensions=recommendations_v1_recommendations_pb2.RecommendationModelDimensions(
                            unit=item_1.unit
                        ),
                        owner=identity_v1_refs_pb2.UserRef(
                            display_name=response_0.recommendation_model.owner.display_name
                        )
                    )
                )
                async def send_1(
                    payload: recommendations_v1_recommendation_model_validation_service_pb2.ExplainRecommendationModelDecisionRequest = outgoing_1
                ) -> recommendations_v1_recommendation_model_validation_service_pb2.ExplainRecommendationModelDecisionResponse:
                    return await deps.clients.recommendations_recommendation_model_validation.ExplainRecommendationModelDecision(
                        payload,
                        timeout=deps.settings.timeout
                    )
                callbacks_1.append(send_1)
            for callback_1 in callbacks_1:
                response_1 = await callback_1()
            outgoing_2 = recommendations_v1_interaction_lifecycle_service_pb2.RenewInteractionRequest(
                context=request.context,
                details=recommendations_v1_interaction_lifecycle_service_pb2.RenewInteractionRequest.Details(
                    new_owner=identity_v1_refs_pb2.UserRef(email=request.details.approver.email)
                ),
                interaction_id=request.interaction_id
            )
            send_2 = partial(
                deps.clients.recommendations_interaction_lifecycle.RenewInteraction,
                timeout=deps.settings.timeout
            )
            response_2 = await send_2(outgoing_2)
            outgoing_3 = pipelines_v1_pipeline_lifecycle_service_pb2.SchedulePipelineExpiryRequest(
                context=request.context,
                pipeline=pipelines_v1_pipelines_pb2.Pipeline(
                    audit=common_v1_audit_pb2.AuditInfo(etag=response_0.recommendation_model.audit.etag),
                    participants=[
                        pipelines_v1_pipelines_pb2.PipelineParticipant(
                            contact=common_v1_contact_pb2.ContactInfo(email=response_0.recommendation_model.owner.email)
                        )
                    ]
                )
            )
            response_3 = await hooks.interaction_approval_comment_interaction_approval3(
                deps.clients.pipelines_pipeline_lifecycle,
                outgoing_3,
                deps.settings.timeout
            )
            returned_2_0 = response_2.result.status
            if returned_2_0:
                response.result.status = returned_2_0
            returned_3_0 = response_3.pipeline.organizer.email
            if returned_3_0:
                response.interaction.subject.email = returned_3_0
            echoed_0 = request.interaction_id
            response.interaction.interaction_id = echoed_0
            echoed_1 = request.interaction.kind
            response.interaction.kind = echoed_1
            return response

    async def handle_delegate_interaction_approval(
        self,
        request: recommendations_v1_interaction_approval_service_pb2.DelegateInteractionApprovalRequest
    ) -> recommendations_v1_interaction_approval_service_pb2.DelegateInteractionApprovalResponse:
        """Delegates an interaction."""
        deps = self.deps
        response = recommendations_v1_interaction_approval_service_pb2.DelegateInteractionApprovalResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('DelegateInteractionApproval', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'DelegateInteractionApproval',
                {'reason': request.reason}
            )
            await deps.repository.save_interaction(request.context.tenant_id, request.interaction)
            response_0 = customers_v1_customer_validation_service_pb2.CheckCustomerEligibilityResponse()
            response_1 = recommendations_v1_recommendation_set_validation_service_pb2.NormalizeRecommendationSetResponse()
            outgoing_0 = customers_v1_customer_validation_service_pb2.CheckCustomerEligibilityRequest()
            outgoing_0.context.CopyFrom(request.context)
            outgoing_0.customer.relationship_manager.display_name = request.interaction.subject.display_name
            outgoing_0.context.tenant_id = tenant_id.get()
            response_0 = await deps.clients.customers_customer_validation.CheckCustomerEligibility(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = recommendations_v1_recommendation_set_validation_service_pb2.NormalizeRecommendationSetRequest(
                context=request.context,
                recommendation_set=recommendations_v1_recommendations_pb2.RecommendationSet(
                    audit=common_v1_audit_pb2.AuditInfo(updated_by=response_0.customer.audit.updated_by),
                    billing_address=common_v1_address_pb2.PostalAddress(
                        country_code=response_0.customer.primary_address.country_code
                    ),
                    counterparty=customers_v1_refs_pb2.CustomerRef(email=request.interaction.subject.email)
                )
            )
            port_1: InteractionApprovalDelegateInteractionApproval1Port = InteractionApprovalDelegateInteractionApproval1Adapter(
                deps.clients.recommendations_recommendation_set_validation,
                deps.settings.timeout
            )
            response_1 = await port_1.execute(outgoing_1)
            returned_0_0 = response_0.result.correlation_id
            if returned_0_0:
                response.interaction.correlation_id = returned_0_0
            returned_1_0 = response_1.outcome.message
            if returned_1_0:
                response.outcome.message = returned_1_0
            returned_1_1 = response_1.result.status
            if returned_1_1:
                response.result.status = returned_1_1
            echoed_0 = request.interaction_id
            response.interaction.interaction_id = echoed_0
            echoed_1 = request.interaction.correlation_id
            response.result.correlation_id = echoed_1
            return response

    async def handle_get_interaction_approval_status(
        self,
        request: recommendations_v1_interaction_approval_service_pb2.GetInteractionApprovalStatusRequest
    ) -> recommendations_v1_interaction_approval_service_pb2.GetInteractionApprovalStatusResponse:
        """Returns an interaction."""
        deps = self.deps
        response = recommendations_v1_interaction_approval_service_pb2.GetInteractionApprovalStatusResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('GetInteractionApprovalStatus', extra={'fields': {'locale': request.context.locale}})
            await deps.repository.audit(
                request.context.tenant_id,
                'GetInteractionApprovalStatus',
                {'locale': request.context.locale}
            )
            echoed_0 = request.interaction_id
            response.interaction.interaction_id = echoed_0
            return response

    async def handle_list_pending_interactions(
        self,
        request: recommendations_v1_interaction_approval_service_pb2.ListPendingInteractionsRequest
    ) -> recommendations_v1_interaction_approval_service_pb2.ListPendingInteractionsResponse:
        """Lists interactions a page at a time."""
        deps = self.deps
        response = recommendations_v1_interaction_approval_service_pb2.ListPendingInteractionsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ListPendingInteractions', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ListPendingInteractions',
                {'order_by': request.order_by}
            )
            response_0 = recommendations_v1_recommendation_set_approval_service_pb2.ApproveRecommendationSetResponse()
            outgoing_0 = recommendations_v1_recommendation_set_approval_service_pb2.ApproveRecommendationSetRequest(
                context=request.context,
                details=recommendations_v1_recommendation_set_approval_service_pb2.ApproveRecommendationSetRequest.Details(
                    approver=identity_v1_refs_pb2.UserRef(user_id=request.context.actor.user_id)
                ),
                recommendation_set=recommendations_v1_recommendations_pb2.RecommendationSet(
                    billing_address=common_v1_address_pb2.PostalAddress(region=request.filter.region),
                    counterparty=customers_v1_refs_pb2.CustomerRef(email=request.context.actor.email)
                )
            )
            response_0 = await deps.clients.recommendations_recommendation_set_approval.ApproveRecommendationSet(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.outcome.status
            if returned_0_0:
                response.result.status = returned_0_0
            returned_0_1 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_1)
            return response

    async def handle_recall_interaction(
        self,
        request: recommendations_v1_interaction_approval_service_pb2.RecallInteractionRequest
    ) -> recommendations_v1_interaction_approval_service_pb2.RecallInteractionResponse:
        """Recalls an interaction."""
        deps = self.deps
        response = recommendations_v1_interaction_approval_service_pb2.RecallInteractionResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('RecallInteraction', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'RecallInteraction', {'reason': request.reason})
            await deps.repository.save_interaction(request.context.tenant_id, request.interaction)
            response_0 = lineage_v1_impact_sync_service_pb2.ResolveImpactConflictResponse()
            response_1 = customers_v1_household_query_service_pb2.FindHouseholdsResponse()
            outgoing_0 = lineage_v1_impact_sync_service_pb2.ResolveImpactConflictRequest(
                context=request.context,
                impact=lineage_v1_lineage_pb2.Impact(
                    assignee=identity_v1_refs_pb2.UserRef(email=request.interaction.subject.email),
                    customer=customers_v1_refs_pb2.CustomerRef(
                        customer_id=request.interaction.subject.customer_id,
                        display_name=request.interaction.subject.display_name
                    )
                )
            )
            response_0 = await InteractionApprovalRecallInteraction0Adapter(
                deps.clients.lineage_impact_sync,
                deps.settings.timeout
            )(outgoing_0)
            async for item_1 in async_messages(request.interaction.measurements):
                outgoing_1 = customers_v1_household_query_service_pb2.FindHouseholdsRequest(
                    context=request.context,
                    filter=customers_v1_household_query_service_pb2.FindHouseholdsRequest.Filter(
                        created_after=item_1.observed_at
                    )
                )
                response_1 = await deps.clients.customers_household_query.FindHouseholds(
                    outgoing_1,
                    timeout=deps.settings.timeout
                )
            returned_0_0 = response_0.result.correlation_id
            if returned_0_0:
                response.result.correlation_id = returned_0_0
            echoed_0 = request.interaction_id
            response.interaction.interaction_id = echoed_0
            echoed_1 = request.interaction.correlation_id
            response.interaction.correlation_id = echoed_1
            return response

    async def handle_submit_interaction(
        self,
        request: recommendations_v1_interaction_approval_service_pb2.SubmitInteractionRequest
    ) -> recommendations_v1_interaction_approval_service_pb2.SubmitInteractionResponse:
        """Submits an interaction."""
        deps = self.deps
        response = recommendations_v1_interaction_approval_service_pb2.SubmitInteractionResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SubmitInteraction', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'SubmitInteraction', {'reason': request.reason})
            await deps.repository.save_interaction(request.context.tenant_id, request.interaction)
            response_0 = recommendations_v1_interaction_lifecycle_service_pb2.ScheduleInteractionExpiryResponse()
            response_1 = customers_v1_customer_segment_calculation_service_pb2.ExplainCustomerSegmentCalculationResponse()
            outgoing_0 = recommendations_v1_interaction_lifecycle_service_pb2.ScheduleInteractionExpiryRequest(
                context=request.context,
                details=recommendations_v1_interaction_lifecycle_service_pb2.ScheduleInteractionExpiryRequest.Details(
                    notify=common_v1_contact_pb2.ContactInfo(email=request.interaction.subject.email)
                ),
                interaction=recommendations_v1_recommendations_pb2.Interaction(
                    correlation_id=request.interaction.correlation_id,
                    subject=customers_v1_refs_pb2.CustomerRef(
                        display_name=request.interaction.subject.display_name,
                        email=request.details.approver.email
                    )
                )
            )
            response_0 = await deps.clients.recommendations_interaction_lifecycle.ScheduleInteractionExpiry(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = customers_v1_customer_segment_calculation_service_pb2.ExplainCustomerSegmentCalculationRequest(
                context=request.context,
                customer_segment=customers_v1_customers_pb2.CustomerSegment(
                    owner=identity_v1_refs_pb2.UserRef(display_name=response_0.interaction.subject.display_name)
                )
            )
            method_name_1 = 'ExplainCustomerSegmentCalculation'
            response_1 = await getattr(
                deps.clients.customers_customer_segment_calculation,
                method_name_1
            )(outgoing_1, timeout=deps.settings.timeout)
            returned_0_0 = response_0.outcome.message
            if returned_0_0:
                response.outcome.message = returned_0_0
            returned_0_1 = response_0.outcome.effective_at
            if returned_0_1.ListFields():
                response.outcome.effective_at.MergeFrom(returned_0_1)
            returned_1_0 = response_1.customer_segment.owner.email
            if returned_1_0:
                response.interaction.subject.email = returned_1_0
            returned_1_1 = response_1.result.correlation_id
            if returned_1_1:
                response.interaction.correlation_id = returned_1_1
            echoed_0 = request.interaction_id
            response.interaction.interaction_id = echoed_0
            echoed_1 = request.interaction.sequence
            response.interaction.sequence = echoed_1
            return response
