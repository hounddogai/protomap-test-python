"""Reusable transport mixin for InteractionValidationService."""

from __future__ import annotations

from collections.abc import AsyncIterator
from collections.abc import Awaitable
from collections.abc import Callable
from functools import partial
from typing import cast
import asyncio
import logging

from google.protobuf.json_format import MessageToDict
from google.protobuf.json_format import ParseDict
import grpc

from acme.appointments.v1 import appointment_query_service_pb2 as appointments_v1_appointment_query_service_pb2
from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.concessions.v1 import concession_stand_query_service_pb2 as concessions_v1_concession_stand_query_service_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.identity.v1 import user_query_service_pb2 as identity_v1_user_query_service_pb2
from acme.ledger.v1 import ledger_account_validation_service_pb2 as ledger_v1_ledger_account_validation_service_pb2
from acme.ledger.v1 import ledger_pb2 as ledger_v1_ledger_pb2
from acme.ledger.v1 import refs_pb2 as ledger_v1_refs_pb2
from acme.lineage.v1 import lineage_node_validation_service_pb2 as lineage_v1_lineage_node_validation_service_pb2
from acme.lineage.v1 import lineage_pb2 as lineage_v1_lineage_pb2
from acme.maintenance.v1 import work_order_query_service_pb2 as maintenance_v1_work_order_query_service_pb2
from acme.metrics.v1 import dashboard_validation_service_pb2 as metrics_v1_dashboard_validation_service_pb2
from acme.performers.v1 import performer_service_pb2 as performers_v1_performer_service_pb2
from acme.recommendations.v1 import (
    interaction_validation_service_pb2 as recommendations_v1_interaction_validation_service_pb2,
)
from acme.recommendations.v1 import (
    recommendation_model_calculation_service_pb2 as recommendations_v1_recommendation_model_calculation_service_pb2,
)
from acme.recommendations.v1 import (
    recommendation_set_validation_service_pb2 as recommendations_v1_recommendation_set_validation_service_pb2,
)
from acme.recommendations.v1 import recommendations_pb2 as recommendations_v1_recommendations_pb2
from acme.venues.v1 import venue_validation_service_pb2 as venues_v1_venue_validation_service_pb2

from acme_data.domains.recommendations import hooks
from acme_data.domains.recommendations.adapters import InteractionValidationNormalizeInteraction1Adapter
from acme_data.domains.recommendations.adapters import InteractionValidationNormalizeInteraction1Port
from acme_data.domains.recommendations.dependencies import Dependencies
from acme_data.domains.recommendations.models import InteractionValidationCheckInteractionEligibility0Command
from acme_data.domains.recommendations.models import to_interaction_validation_check_interaction_eligibility0_command
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class InteractionValidationServicerHandlers:
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    async def CheckInteractionEligibility(
        self, request: recommendations_v1_interaction_validation_service_pb2.CheckInteractionEligibilityRequest, context: grpc.aio.ServicerContext,
    ) -> recommendations_v1_interaction_validation_service_pb2.CheckInteractionEligibilityResponse:
        """Checks an interaction."""
        return await self.handle_check_interaction_eligibility(request)

    @rpc_errors
    async def ExplainInteractionDecision(
        self, request: recommendations_v1_interaction_validation_service_pb2.ExplainInteractionDecisionRequest, context: grpc.aio.ServicerContext,
    ) -> recommendations_v1_interaction_validation_service_pb2.ExplainInteractionDecisionResponse:
        """Explains an interaction."""
        return await self.handle_explain_interaction_decision(request)

    @rpc_errors
    @retry_transient
    async def GetInteractionRules(
        self, request: recommendations_v1_interaction_validation_service_pb2.GetInteractionRulesRequest, context: grpc.aio.ServicerContext,
    ) -> recommendations_v1_interaction_validation_service_pb2.GetInteractionRulesResponse:
        """Returns an interaction."""
        return await self.handle_get_interaction_rules(request)

    @rpc_errors
    async def LintInteractions(
        self, request: recommendations_v1_interaction_validation_service_pb2.LintInteractionsRequest, context: grpc.aio.ServicerContext,
    ) -> recommendations_v1_interaction_validation_service_pb2.LintInteractionsResponse:
        """Lints an interaction."""
        return await self.handle_lint_interactions(request)

    @rpc_errors
    async def NormalizeInteraction(
        self, request: recommendations_v1_interaction_validation_service_pb2.NormalizeInteractionRequest, context: grpc.aio.ServicerContext,
    ) -> recommendations_v1_interaction_validation_service_pb2.NormalizeInteractionResponse:
        """Normalizes an interaction."""
        return await self.handle_normalize_interaction(request)

    @rpc_errors
    async def PreviewInteraction(
        self, request: recommendations_v1_interaction_validation_service_pb2.PreviewInteractionRequest, context: grpc.aio.ServicerContext,
    ) -> recommendations_v1_interaction_validation_service_pb2.PreviewInteractionResponse:
        """Previews an interaction."""
        return await self.handle_preview_interaction(request)

    @rpc_errors
    async def ScoreInteraction(
        self, request: recommendations_v1_interaction_validation_service_pb2.ScoreInteractionRequest, context: grpc.aio.ServicerContext,
    ) -> recommendations_v1_interaction_validation_service_pb2.ScoreInteractionResponse:
        """Scores an interaction."""
        return await self.handle_score_interaction(request)

    @rpc_errors
    async def ValidateInteraction(
        self, request: recommendations_v1_interaction_validation_service_pb2.ValidateInteractionRequest, context: grpc.aio.ServicerContext,
    ) -> recommendations_v1_interaction_validation_service_pb2.ValidateInteractionResponse:
        """Validates an interaction."""
        return await self.handle_validate_interaction(request)

    async def handle_check_interaction_eligibility(
        self,
        request: recommendations_v1_interaction_validation_service_pb2.CheckInteractionEligibilityRequest
    ) -> recommendations_v1_interaction_validation_service_pb2.CheckInteractionEligibilityResponse:
        """Checks an interaction."""
        deps = self.deps
        response = recommendations_v1_interaction_validation_service_pb2.CheckInteractionEligibilityResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CheckInteractionEligibility', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'CheckInteractionEligibility',
                {'reason': request.reason}
            )
            await deps.repository.save_interaction(request.context.tenant_id, request.interaction)
            response_0 = concessions_v1_concession_stand_query_service_pb2.SummarizeConcessionStandsResponse()
            command_0 = InteractionValidationCheckInteractionEligibility0Command.model_validate(
                {'context': request.context, 'annotations': dict(request.annotations)}
            )
            outgoing_0 = to_interaction_validation_check_interaction_eligibility0_command(command_0)
            response_0 = await deps.clients.concessions_concession_stand_query.SummarizeConcessionStands(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.outcome.message = returned_0_0
            returned_0_1 = response_0.result.correlation_id
            if returned_0_1:
                response.interaction.correlation_id = returned_0_1
            echoed_0 = request.interaction_id
            response.interaction.interaction_id = echoed_0
            echoed_1 = request.interaction.correlation_id
            response.result.correlation_id = echoed_1
            return response

    async def handle_explain_interaction_decision(
        self,
        request: recommendations_v1_interaction_validation_service_pb2.ExplainInteractionDecisionRequest
    ) -> recommendations_v1_interaction_validation_service_pb2.ExplainInteractionDecisionResponse:
        """Explains an interaction."""
        deps = self.deps
        response = recommendations_v1_interaction_validation_service_pb2.ExplainInteractionDecisionResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ExplainInteractionDecision', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ExplainInteractionDecision',
                {'reason': request.reason}
            )
            await deps.repository.save_interaction(request.context.tenant_id, request.interaction)
            response_0 = venues_v1_venue_validation_service_pb2.ValidateVenueResponse()
            outgoing_0 = venues_v1_venue_validation_service_pb2.ValidateVenueRequest(
                context=request.context,
                details=venues_v1_venue_validation_service_pb2.ValidateVenueRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(
                        name=request.details.contact.name,
                        preferred_channel=request.details.contact.preferred_channel
                    )
                )
            )
            send_0 = partial(deps.clients.venues_venue_validation.ValidateVenue, timeout=deps.settings.timeout)
            response_0 = await send_0(outgoing_0)
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.result.message = returned_0_0
            echoed_0 = request.interaction_id
            response.interaction.interaction_id = echoed_0
            echoed_1 = request.interaction.source
            response.interaction.source = echoed_1
            return response

    async def handle_get_interaction_rules(
        self,
        request: recommendations_v1_interaction_validation_service_pb2.GetInteractionRulesRequest
    ) -> recommendations_v1_interaction_validation_service_pb2.GetInteractionRulesResponse:
        """Returns an interaction."""
        deps = self.deps
        response = recommendations_v1_interaction_validation_service_pb2.GetInteractionRulesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('GetInteractionRules', extra={'fields': {'locale': request.context.locale}})
            await deps.repository.audit(
                request.context.tenant_id,
                'GetInteractionRules',
                {'locale': request.context.locale}
            )
            echoed_0 = request.interaction_id
            response.interaction.interaction_id = echoed_0
            return response

    async def handle_lint_interactions(
        self,
        request: recommendations_v1_interaction_validation_service_pb2.LintInteractionsRequest
    ) -> recommendations_v1_interaction_validation_service_pb2.LintInteractionsResponse:
        """Lints an interaction."""
        deps = self.deps
        response = recommendations_v1_interaction_validation_service_pb2.LintInteractionsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('LintInteractions', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'LintInteractions', {'reason': request.reason})
            await deps.repository.save_interaction(request.context.tenant_id, request.interaction)
            response_0 = performers_v1_performer_service_pb2.BatchGetPerformersResponse()
            outgoing_0 = performers_v1_performer_service_pb2.BatchGetPerformersRequest(context=request.context)
            response_0 = await hooks.interaction_validation_lint_interactions0(
                deps.clients.performers_performer,
                outgoing_0,
                deps.settings.timeout
            )
            returned_0_0 = response_0.result.status
            if returned_0_0:
                response.result.status = returned_0_0
            echoed_0 = request.interaction_id
            response.interaction.interaction_id = echoed_0
            echoed_1 = request.interaction.correlation_id
            response.interaction.correlation_id = echoed_1
            return response

    async def handle_normalize_interaction(
        self,
        request: recommendations_v1_interaction_validation_service_pb2.NormalizeInteractionRequest
    ) -> recommendations_v1_interaction_validation_service_pb2.NormalizeInteractionResponse:
        """Normalizes an interaction."""
        deps = self.deps
        response = recommendations_v1_interaction_validation_service_pb2.NormalizeInteractionResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('NormalizeInteraction', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'NormalizeInteraction', {'reason': request.reason})
            await deps.repository.save_interaction(request.context.tenant_id, request.interaction)
            response_0 = maintenance_v1_work_order_query_service_pb2.ExportWorkOrdersResponse()
            response_1 = identity_v1_user_query_service_pb2.BrowseUsersResponse()
            for item_0 in request.interaction.measurements:
                outgoing_0 = maintenance_v1_work_order_query_service_pb2.ExportWorkOrdersRequest(
                    context=request.context,
                    filter=maintenance_v1_work_order_query_service_pb2.ExportWorkOrdersRequest.Filter(
                        created_after=item_0.observed_at
                    )
                )
                async for result_0 in deps.clients.maintenance_work_order_query.ExportWorkOrders(
                    outgoing_0,
                    timeout=deps.settings.timeout
                ):
                    response_0 = result_0
            outgoing_1 = identity_v1_user_query_service_pb2.BrowseUsersRequest(
                context=request.context,
                filter=identity_v1_user_query_service_pb2.BrowseUsersRequest.Filter(
                    created_after=request.interaction.occurred_at,
                    owner_id=request.interaction.interaction_id
                )
            )
            port_1: InteractionValidationNormalizeInteraction1Port = InteractionValidationNormalizeInteraction1Adapter(
                deps.clients.identity_user_query,
                deps.settings.timeout
            )
            response_1 = await port_1.execute(outgoing_1)
            returned_1_0 = response_1.result.status
            if returned_1_0:
                response.result.status = returned_1_0
            returned_1_1 = response_1.result.reference_ids
            response.result.reference_ids.extend(returned_1_1)
            echoed_0 = request.interaction_id
            response.interaction.interaction_id = echoed_0
            echoed_1 = request.interaction.correlation_id
            response.interaction.correlation_id = echoed_1
            return response

    async def handle_preview_interaction(
        self,
        request: recommendations_v1_interaction_validation_service_pb2.PreviewInteractionRequest
    ) -> recommendations_v1_interaction_validation_service_pb2.PreviewInteractionResponse:
        """Previews an interaction."""
        deps = self.deps
        response = recommendations_v1_interaction_validation_service_pb2.PreviewInteractionResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('PreviewInteraction', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'PreviewInteraction', {'reason': request.reason})
            await deps.repository.save_interaction(request.context.tenant_id, request.interaction)
            response_0 = metrics_v1_dashboard_validation_service_pb2.NormalizeDashboardResponse()
            response_1 = performers_v1_performer_service_pb2.BatchGetPerformersResponse()
            response_2 = appointments_v1_appointment_query_service_pb2.SuggestAppointmentsResponse()
            response_3 = ledger_v1_ledger_account_validation_service_pb2.ScoreLedgerAccountResponse()
            outgoing_0 = metrics_v1_dashboard_validation_service_pb2.NormalizeDashboardRequest(
                context=request.context,
                details=metrics_v1_dashboard_validation_service_pb2.NormalizeDashboardRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(
                        email=request.details.contact.email,
                        phone=request.details.contact.phone
                    )
                )
            )
            outgoing_1 = performers_v1_performer_service_pb2.BatchGetPerformersRequest(context=request.context)
            response_0, response_1 = await asyncio.gather(
                deps.clients.metrics_dashboard_validation.NormalizeDashboard(outgoing_0, timeout=deps.settings.timeout),
                deps.clients.performers_performer.BatchGetPerformers(outgoing_1, timeout=deps.settings.timeout),
            )
            outgoing_2 = appointments_v1_appointment_query_service_pb2.SuggestAppointmentsRequest(
                context=request.context,
                filter=appointments_v1_appointment_query_service_pb2.SuggestAppointmentsRequest.Filter(
                    created_after=response_0.dashboard.issued_at,
                    labels=dict(response_0.result.details),
                    owner_id=response_1.result.correlation_id,
                    region=response_0.dashboard.billing_address.region
                )
            )
            response_2 = cast(appointments_v1_appointment_query_service_pb2.SuggestAppointmentsResponse, await deps.bus.request(
                'acme.recommendations.v1.InteractionValidationService/PreviewInteraction/2', outgoing_2, deps.settings.timeout,
            ))
            outgoing_3 = ledger_v1_ledger_account_validation_service_pb2.ScoreLedgerAccountRequest(
                context=request.context,
                details=ledger_v1_ledger_account_validation_service_pb2.ScoreLedgerAccountRequest.Details(
                    destination=common_v1_address_pb2.PostalAddress(
                        locality=response_0.dashboard.billing_address.locality
                    )
                ),
                ledger_account=ledger_v1_ledger_pb2.LedgerAccount(
                    holder=ledger_v1_refs_pb2.PostingBatchRef(
                        display_name=response_0.dashboard.counterparty.display_name
                    )
                )
            )
            response_3 = await deps.clients.ledger_ledger_account_validation.ScoreLedgerAccount(
                outgoing_3,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_0)
            returned_1_0 = response_1.result.correlation_id
            if returned_1_0:
                response.interaction.correlation_id = returned_1_0
            returned_1_1 = response_1.result.details
            response.result.details.update(returned_1_1)
            returned_2_0 = response_2.result.correlation_id
            if returned_2_0:
                response.result.correlation_id = returned_2_0
            returned_2_1 = response_2.result.status
            if returned_2_1:
                response.result.status = returned_2_1
            returned_3_0 = response_3.result.correlation_id
            if returned_3_0:
                response.result.correlation_id = returned_3_0
            echoed_0 = request.interaction_id
            response.interaction.interaction_id = echoed_0
            echoed_1 = request.interaction.source
            response.interaction.source = echoed_1
            return response

    async def handle_score_interaction(
        self,
        request: recommendations_v1_interaction_validation_service_pb2.ScoreInteractionRequest
    ) -> recommendations_v1_interaction_validation_service_pb2.ScoreInteractionResponse:
        """Scores an interaction."""
        deps = self.deps
        response = recommendations_v1_interaction_validation_service_pb2.ScoreInteractionResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ScoreInteraction', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'ScoreInteraction', {'reason': request.reason})
            await deps.repository.save_interaction(request.context.tenant_id, request.interaction)
            response_0 = recommendations_v1_recommendation_model_calculation_service_pb2.CompareRecommendationModelOptionsResponse()
            response_1 = recommendations_v1_recommendation_set_validation_service_pb2.PreviewRecommendationSetResponse()
            callbacks_0: list[
                Callable[
                    [],
                    Awaitable[
                        recommendations_v1_recommendation_model_calculation_service_pb2.CompareRecommendationModelOptionsResponse
                    ]
                ]
            ] = []
            for item_0 in request.interaction.measurements:
                outgoing_0 = recommendations_v1_recommendation_model_calculation_service_pb2.CompareRecommendationModelOptionsRequest(
                    context=request.context,
                    recommendation_model=recommendations_v1_recommendations_pb2.RecommendationModel(
                        dimensions=recommendations_v1_recommendations_pb2.RecommendationModelDimensions(
                            unit=item_0.unit
                        )
                    )
                )
                async def send_0(
                    payload: recommendations_v1_recommendation_model_calculation_service_pb2.CompareRecommendationModelOptionsRequest = outgoing_0
                ) -> recommendations_v1_recommendation_model_calculation_service_pb2.CompareRecommendationModelOptionsResponse:
                    return await deps.clients.recommendations_recommendation_model_calculation.CompareRecommendationModelOptions(
                        payload,
                        timeout=deps.settings.timeout
                    )
                callbacks_0.append(send_0)
            for callback_0 in callbacks_0:
                response_0 = await callback_0()
            async for item_1 in async_messages(request.interaction.measurements):
                outgoing_1 = recommendations_v1_recommendation_set_validation_service_pb2.PreviewRecommendationSetRequest(
                    context=request.context,
                    recommendation_set=recommendations_v1_recommendations_pb2.RecommendationSet(
                        audit=common_v1_audit_pb2.AuditInfo(
                            created_by=response_0.recommendation_model.audit.created_by,
                            updated_at=item_1.observed_at
                        ),
                        billing_address=common_v1_address_pb2.PostalAddress(
                            region=response_0.recommendation_model.address.region
                        )
                    )
                )
                response_1 = await deps.clients.recommendations_recommendation_set_validation.PreviewRecommendationSet(
                    outgoing_1,
                    timeout=deps.settings.timeout
                )
            echoed_0 = request.interaction_id
            response.interaction.interaction_id = echoed_0
            echoed_1 = request.interaction.attributes
            response.interaction.attributes.update(echoed_1)
            return response

    async def handle_validate_interaction(
        self,
        request: recommendations_v1_interaction_validation_service_pb2.ValidateInteractionRequest
    ) -> recommendations_v1_interaction_validation_service_pb2.ValidateInteractionResponse:
        """Validates an interaction."""
        deps = self.deps
        response = recommendations_v1_interaction_validation_service_pb2.ValidateInteractionResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ValidateInteraction', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'ValidateInteraction', {'reason': request.reason})
            await deps.repository.save_interaction(request.context.tenant_id, request.interaction)
            response_0 = lineage_v1_lineage_node_validation_service_pb2.NormalizeLineageNodeResponse()
            outgoing_0 = lineage_v1_lineage_node_validation_service_pb2.NormalizeLineageNodeRequest(
                context=request.context,
                lineage_node=lineage_v1_lineage_pb2.LineageNode(
                    children=[
                        lineage_v1_lineage_pb2.LineageNode(
                            children=[
                                lineage_v1_lineage_pb2.LineageNode(
                                    manager=identity_v1_refs_pb2.UserRef(email=request.details.contact.email)
                                )
                            ]
                        )
                    ]
                )
            )
            document_0 = MessageToDict(outgoing_0, preserving_proto_field_name=True)
            outgoing_0 = ParseDict(
                document_0,
                lineage_v1_lineage_node_validation_service_pb2.NormalizeLineageNodeRequest()
            )
            response_0 = await deps.clients.lineage_lineage_node_validation.NormalizeLineageNode(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.correlation_id
            if returned_0_0:
                response.result.correlation_id = returned_0_0
            returned_0_1 = response_0.outcome.status
            if returned_0_1:
                response.result.status = returned_0_1
            echoed_0 = request.interaction_id
            response.interaction.interaction_id = echoed_0
            echoed_1 = request.interaction.correlation_id
            response.interaction.correlation_id = echoed_1
            return response
