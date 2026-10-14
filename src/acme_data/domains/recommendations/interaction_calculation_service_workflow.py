"""Application workflow for Interaction Calculation."""

from __future__ import annotations

from collections.abc import Awaitable
from collections.abc import Callable
from functools import partial
from typing import Any
from typing import cast
import asyncio
import logging

from google.protobuf.any_pb2 import Any as AnyMessage
from google.protobuf.json_format import MessageToJson
from google.protobuf.json_format import Parse

from acme.anomalies.v1 import anomalies_pb2 as anomalies_v1_anomalies_pb2
from acme.anomalies.v1 import anomaly_service_pb2 as anomalies_v1_anomaly_service_pb2
from acme.anomalies.v1 import detector_validation_service_pb2 as anomalies_v1_detector_validation_service_pb2
from acme.audit.v1 import audit_event_query_service_pb2 as audit_v1_audit_event_query_service_pb2
from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.customers.v1 import refs_pb2 as customers_v1_refs_pb2
from acme.featurestore.v1 import (
    feature_value_calculation_service_pb2 as featurestore_v1_feature_value_calculation_service_pb2,
)
from acme.featurestore.v1 import featurestore_pb2 as featurestore_v1_featurestore_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.lineage.v1 import impact_validation_service_pb2 as lineage_v1_impact_validation_service_pb2
from acme.lineage.v1 import lineage_edge_query_service_pb2 as lineage_v1_lineage_edge_query_service_pb2
from acme.lineage.v1 import lineage_pb2 as lineage_v1_lineage_pb2
from acme.metrics.v1 import dashboard_notification_service_pb2 as metrics_v1_dashboard_notification_service_pb2
from acme.recommendations.v1 import (
    interaction_calculation_service_pb2 as recommendations_v1_interaction_calculation_service_pb2,
)
from acme.recommendations.v1 import (
    recommendation_model_calculation_service_pb2 as recommendations_v1_recommendation_model_calculation_service_pb2,
)
from acme.recommendations.v1 import (
    recommendation_set_validation_service_pb2 as recommendations_v1_recommendation_set_validation_service_pb2,
)
from acme.recommendations.v1 import recommendations_pb2 as recommendations_v1_recommendations_pb2

from acme_data.domains.recommendations import hooks
from acme_data.domains.recommendations.dependencies import Dependencies
from acme_data.domains.recommendations.models import InteractionCalculationExplainInteractionCalculation1Command
from acme_data.domains.recommendations.models import to_interaction_calculation_explain_interaction_calculation1_command
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import run_steps
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class InteractionCalculationServicerWorkflow:
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    async def handle_calculate_interaction(
        self,
        request: recommendations_v1_interaction_calculation_service_pb2.CalculateInteractionRequest
    ) -> recommendations_v1_interaction_calculation_service_pb2.CalculateInteractionResponse:
        """Calculates an interaction."""
        deps = self.deps
        response = recommendations_v1_interaction_calculation_service_pb2.CalculateInteractionResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CalculateInteraction', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'CalculateInteraction', {'reason': request.reason})
            await deps.repository.save_interaction(request.context.tenant_id, request.interaction)
            response_0 = lineage_v1_lineage_edge_query_service_pb2.SuggestLineageEdgesResponse()
            response_1 = recommendations_v1_recommendation_model_calculation_service_pb2.SimulateRecommendationModelResponse()
            outgoing_0 = lineage_v1_lineage_edge_query_service_pb2.SuggestLineageEdgesRequest(
                context=request.context,
                filter=lineage_v1_lineage_edge_query_service_pb2.SuggestLineageEdgesRequest.Filter(
                    created_after=request.interaction.occurred_at,
                    labels=dict(request.interaction.attributes),
                    owner_id=request.interaction.subject.customer_id,
                    region=request.details.destination.region
                )
            )
            outgoing_1 = recommendations_v1_recommendation_model_calculation_service_pb2.SimulateRecommendationModelRequest(
                context=request.context,
                details=recommendations_v1_recommendation_model_calculation_service_pb2.SimulateRecommendationModelRequest.Details(
                    destination=common_v1_address_pb2.PostalAddress(
                        country_code=request.details.destination.country_code,
                        lines=list(request.details.destination.lines),
                        locality=request.details.destination.locality
                    )
                ),
                recommendation_model=recommendations_v1_recommendations_pb2.RecommendationModel(
                    owner=identity_v1_refs_pb2.UserRef(email=request.interaction.subject.email)
                )
            )
            response_0, response_1 = await asyncio.gather(
                deps.clients.lineage_lineage_edge_query.SuggestLineageEdges(outgoing_0, timeout=deps.settings.timeout),
                deps.clients.recommendations_recommendation_model_calculation.SimulateRecommendationModel(
                    outgoing_1,
                    timeout=deps.settings.timeout
                ),
            )
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.result.message = returned_0_0
            returned_0_1 = response_0.result.status
            if returned_0_1:
                response.result.status = returned_0_1
            returned_1_0 = response_1.breakdown.currency_code
            if returned_1_0:
                response.breakdown.currency_code = returned_1_0
            returned_1_1 = response_1.result.correlation_id
            if returned_1_1:
                response.result.correlation_id = returned_1_1
            echoed_0 = request.interaction_id
            response.interaction.interaction_id = echoed_0
            echoed_1 = request.interaction.correlation_id
            response.interaction.correlation_id = echoed_1
            return response

    async def handle_compare_interaction_options(
        self,
        request: recommendations_v1_interaction_calculation_service_pb2.CompareInteractionOptionsRequest
    ) -> recommendations_v1_interaction_calculation_service_pb2.CompareInteractionOptionsResponse:
        """Compares an interaction."""
        deps = self.deps
        response = recommendations_v1_interaction_calculation_service_pb2.CompareInteractionOptionsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info(
                'CompareInteractionOptions',
                extra={'fields': {'include_breakdown': request.details.include_breakdown}}
            )
            await deps.repository.audit(
                request.context.tenant_id,
                'CompareInteractionOptions',
                {'include_breakdown': request.details.include_breakdown}
            )
            await deps.repository.save_interaction(request.context.tenant_id, request.interaction)
            response_0 = anomalies_v1_detector_validation_service_pb2.NormalizeDetectorResponse()
            outgoing_0 = anomalies_v1_detector_validation_service_pb2.NormalizeDetectorRequest(
                context=request.context,
                details=anomalies_v1_detector_validation_service_pb2.NormalizeDetectorRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(email=request.interaction.subject.email)
                ),
                detector=anomalies_v1_anomalies_pb2.Detector(
                    owner=identity_v1_refs_pb2.UserRef(display_name=request.interaction.subject.display_name)
                ),
                reason=request.reason
            )
            document_0 = MessageToJson(outgoing_0, preserving_proto_field_name=True)
            outgoing_0 = Parse(document_0, anomalies_v1_detector_validation_service_pb2.NormalizeDetectorRequest())
            response_0 = await deps.clients.anomalies_detector_validation.NormalizeDetector(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.detector.discount.amount
            returned_0_0_part_1 = response.breakdown.lines.add()
            if returned_0_0.ListFields():
                returned_0_0_part_1.amount.MergeFrom(returned_0_0)
            returned_0_1 = response_0.result.correlation_id
            if returned_0_1:
                response.result.correlation_id = returned_0_1
            echoed_0 = request.interaction_id
            response.interaction.interaction_id = echoed_0
            echoed_1 = request.details.currency_code
            response.breakdown.currency_code = echoed_1
            return response

    async def handle_estimate_interaction(
        self,
        request: recommendations_v1_interaction_calculation_service_pb2.EstimateInteractionRequest
    ) -> recommendations_v1_interaction_calculation_service_pb2.EstimateInteractionResponse:
        """Estimates an interaction."""
        deps = self.deps
        response = recommendations_v1_interaction_calculation_service_pb2.EstimateInteractionResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('EstimateInteraction', extra={'fields': {'currency_code': request.details.currency_code}})
            await deps.repository.audit(
                request.context.tenant_id,
                'EstimateInteraction',
                {'currency_code': request.details.currency_code}
            )
            await deps.repository.save_interaction(request.context.tenant_id, request.interaction)
            response_0 = metrics_v1_dashboard_notification_service_pb2.NotifyDashboardWatchersResponse()
            response_1 = recommendations_v1_recommendation_model_calculation_service_pb2.SimulateRecommendationModelResponse()
            outgoing_0 = metrics_v1_dashboard_notification_service_pb2.NotifyDashboardWatchersRequest()
            outgoing_0.context.CopyFrom(request.context)
            outgoing_0.details.recipient.email = request.interaction.subject.email
            outgoing_0.reason = request.reason
            outgoing_0.annotations.update(dict(request.annotations))
            outgoing_0.details.variables.update(dict(request.interaction.attributes))
            merged_0 = metrics_v1_dashboard_notification_service_pb2.NotifyDashboardWatchersRequest()
            merged_0.MergeFrom(outgoing_0)
            outgoing_0.CopyFrom(merged_0)
            response_0 = await deps.clients.metrics_dashboard_notification.NotifyDashboardWatchers(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = recommendations_v1_recommendation_model_calculation_service_pb2.SimulateRecommendationModelRequest(
                context=request.context,
                recommendation_model=recommendations_v1_recommendations_pb2.RecommendationModel(
                    address=common_v1_address_pb2.PostalAddress(
                        locality=request.details.destination.locality,
                        recipient=response_0.dashboard.billing_address.recipient
                    )
                )
            )
            envelope_1 = AnyMessage()
            envelope_1.Pack(outgoing_1)
            outgoing_1 = recommendations_v1_recommendation_model_calculation_service_pb2.SimulateRecommendationModelRequest()
            if not envelope_1.Unpack(outgoing_1):
                raise ValueError("partner envelope contains the wrong request type")
            response_1 = await deps.clients.recommendations_recommendation_model_calculation.SimulateRecommendationModel(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.correlation_id
            if returned_0_0:
                response.result.correlation_id = returned_0_0
            returned_1_0 = response_1.recommendation_model.owner.email
            if returned_1_0:
                response.interaction.subject.email = returned_1_0
            returned_1_1 = response_1.result.details
            response.result.details.update(returned_1_1)
            echoed_0 = request.interaction_id
            response.interaction.interaction_id = echoed_0
            echoed_1 = request.interaction.source
            response.interaction.source = echoed_1
            return response

    async def handle_explain_interaction_calculation(
        self,
        request: recommendations_v1_interaction_calculation_service_pb2.ExplainInteractionCalculationRequest
    ) -> recommendations_v1_interaction_calculation_service_pb2.ExplainInteractionCalculationResponse:
        """Explains an interaction."""
        deps = self.deps
        response = recommendations_v1_interaction_calculation_service_pb2.ExplainInteractionCalculationResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ExplainInteractionCalculation', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ExplainInteractionCalculation',
                {'reason': request.reason}
            )
            await deps.repository.save_interaction(request.context.tenant_id, request.interaction)
            response_0 = recommendations_v1_recommendation_model_calculation_service_pb2.QuoteRecommendationModelResponse()
            response_1 = recommendations_v1_recommendation_set_validation_service_pb2.ValidateRecommendationSetResponse()
            for item_0 in request.interaction.measurements:
                outgoing_0 = recommendations_v1_recommendation_model_calculation_service_pb2.QuoteRecommendationModelRequest(
                    context=request.context,
                    recommendation_model=recommendations_v1_recommendations_pb2.RecommendationModel(
                        dimensions=recommendations_v1_recommendations_pb2.RecommendationModelDimensions(
                            unit=item_0.unit
                        ),
                        owner=identity_v1_refs_pb2.UserRef(display_name=request.interaction.subject.display_name)
                    )
                )
                response_0 = await deps.clients.recommendations_recommendation_model_calculation.QuoteRecommendationModel(
                    outgoing_0,
                    timeout=deps.settings.timeout
                )
            command_1 = InteractionCalculationExplainInteractionCalculation1Command(
                context=request.context,
                details_contact_email=response_0.recommendation_model.owner.email
            )
            outgoing_1 = to_interaction_calculation_explain_interaction_calculation1_command(command_1)
            response_1 = await deps.clients.recommendations_recommendation_set_validation.ValidateRecommendationSet(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_1_0 = response_1.result.status
            if returned_1_0:
                response.outcome.status = returned_1_0
            echoed_0 = request.interaction_id
            response.interaction.interaction_id = echoed_0
            echoed_1 = request.interaction.subject
            response.interaction.subject.CopyFrom(echoed_1)
            return response

    async def handle_get_interaction_rates(
        self,
        request: recommendations_v1_interaction_calculation_service_pb2.GetInteractionRatesRequest
    ) -> recommendations_v1_interaction_calculation_service_pb2.GetInteractionRatesResponse:
        """Returns an interaction."""
        deps = self.deps
        response = recommendations_v1_interaction_calculation_service_pb2.GetInteractionRatesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('GetInteractionRates', extra={'fields': {'domain': 'recommendations'}})
            await deps.repository.audit(request.context.tenant_id, 'GetInteractionRates', {})
            response_0 = recommendations_v1_recommendation_model_calculation_service_pb2.EstimateRecommendationModelResponse()
            outgoing_0 = recommendations_v1_recommendation_model_calculation_service_pb2.EstimateRecommendationModelRequest(
                context=request.context,
                recommendation_model=recommendations_v1_recommendations_pb2.RecommendationModel(
                    owner=identity_v1_refs_pb2.UserRef(email=request.context.actor.email)
                )
            )
            response_0 = await deps.clients.recommendations_recommendation_model_calculation.EstimateRecommendationModel(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.details
            response.result.details.update(returned_0_0)
            returned_0_1 = response_0.recommendation_model.owner.display_name
            if returned_0_1:
                response.interaction.subject.display_name = returned_0_1
            echoed_0 = request.interaction_id
            response.interaction.interaction_id = echoed_0
            return response

    async def handle_quote_interaction(
        self,
        request: recommendations_v1_interaction_calculation_service_pb2.QuoteInteractionRequest
    ) -> recommendations_v1_interaction_calculation_service_pb2.QuoteInteractionResponse:
        """Quotes an interaction."""
        deps = self.deps
        response = recommendations_v1_interaction_calculation_service_pb2.QuoteInteractionResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('QuoteInteraction', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'QuoteInteraction', {'reason': request.reason})
            await deps.repository.save_interaction(request.context.tenant_id, request.interaction)
            response_0 = recommendations_v1_recommendation_model_calculation_service_pb2.SimulateRecommendationModelResponse()
            response_1 = recommendations_v1_recommendation_model_calculation_service_pb2.RecalculateRecommendationModelsResponse()
            response_2 = recommendations_v1_recommendation_model_calculation_service_pb2.CalculateRecommendationModelResponse()
            response_3 = recommendations_v1_recommendation_model_calculation_service_pb2.QuoteRecommendationModelResponse()
            outgoing_0 = recommendations_v1_recommendation_model_calculation_service_pb2.SimulateRecommendationModelRequest(
                context=request.context,
                details=recommendations_v1_recommendation_model_calculation_service_pb2.SimulateRecommendationModelRequest.Details(
                    destination=common_v1_address_pb2.PostalAddress(region=request.details.destination.region)
                ),
                recommendation_model=recommendations_v1_recommendations_pb2.RecommendationModel(
                    owner=identity_v1_refs_pb2.UserRef(email=request.interaction.subject.email)
                )
            )
            send_0 = partial(
                deps.clients.recommendations_recommendation_model_calculation.SimulateRecommendationModel,
                timeout=deps.settings.timeout
            )
            response_0 = await send_0(outgoing_0)
            outgoing_1 = recommendations_v1_recommendation_model_calculation_service_pb2.RecalculateRecommendationModelsRequest(
                context=request.context,
                recommendation_model=recommendations_v1_recommendations_pb2.RecommendationModel(
                    address=common_v1_address_pb2.PostalAddress(region=request.details.destination.region),
                    audit=common_v1_audit_pb2.AuditInfo(
                        updated_at=response_0.recommendation_model.audit.updated_at,
                        updated_by=response_0.recommendation_model.audit.updated_by
                    )
                )
            )
            response_1 = await hooks.interaction_calculation_quote_interaction1(
                deps.clients.recommendations_recommendation_model_calculation,
                outgoing_1,
                deps.settings.timeout
            )
            requests_2: list[
                recommendations_v1_recommendation_model_calculation_service_pb2.CalculateRecommendationModelRequest
            ] = []
            for item_2 in request.interaction.measurements:
                outgoing_2 = recommendations_v1_recommendation_model_calculation_service_pb2.CalculateRecommendationModelRequest(
                    context=request.context,
                    details=recommendations_v1_recommendation_model_calculation_service_pb2.CalculateRecommendationModelRequest.Details(
                        destination=common_v1_address_pb2.PostalAddress(
                            region=response_0.recommendation_model.address.region
                        )
                    ),
                    recommendation_model=recommendations_v1_recommendations_pb2.RecommendationModel(
                        dimensions=recommendations_v1_recommendations_pb2.RecommendationModelDimensions(
                            unit=item_2.unit
                        )
                    )
                )
                requests_2.append(outgoing_2)
            replies_2 = await asyncio.gather(*(
                deps.clients.recommendations_recommendation_model_calculation.CalculateRecommendationModel(
                    entry,
                    timeout=deps.settings.timeout
                ) for entry in requests_2
            ))
            if replies_2:
                response_2 = replies_2[-1]
            outgoing_3 = recommendations_v1_recommendation_model_calculation_service_pb2.QuoteRecommendationModelRequest()
            outgoing_3.context.CopyFrom(request.context)
            if response_1.recommendation_model.WhichOneof('locator') == 'address':
                outgoing_3.details.destination.postal_code = response_1.recommendation_model.address.postal_code
            if response_0.recommendation_model.WhichOneof('locator') == 'address':
                outgoing_3.recommendation_model.address.postal_code = response_0.recommendation_model.address.postal_code
            response_3 = await deps.clients.recommendations_recommendation_model_calculation.QuoteRecommendationModel(
                outgoing_3,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.recommendation_model.dimensions.unit
            returned_0_0_part_1 = response.interaction.measurements.add()
            if returned_0_0:
                returned_0_0_part_1.unit = returned_0_0
            returned_1_0 = response_1.result.status
            if returned_1_0:
                response.result.status = returned_1_0
            returned_3_0 = response_3.result.details
            response.result.details.update(returned_3_0)
            echoed_0 = request.interaction_id
            response.interaction.interaction_id = echoed_0
            echoed_1 = request.interaction.attributes
            response.interaction.attributes.update(echoed_1)
            return response

    async def handle_recalculate_interactions(
        self,
        request: recommendations_v1_interaction_calculation_service_pb2.RecalculateInteractionsRequest
    ) -> recommendations_v1_interaction_calculation_service_pb2.RecalculateInteractionsResponse:
        """Recalculates an interaction."""
        deps = self.deps
        response = recommendations_v1_interaction_calculation_service_pb2.RecalculateInteractionsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('RecalculateInteractions', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'RecalculateInteractions',
                {'reason': request.reason}
            )
            await deps.repository.save_interaction(request.context.tenant_id, request.interaction)
            response_0 = lineage_v1_impact_validation_service_pb2.PreviewImpactResponse()
            response_1 = recommendations_v1_recommendation_model_calculation_service_pb2.CompareRecommendationModelOptionsResponse()
            response_2 = recommendations_v1_recommendation_model_calculation_service_pb2.CalculateRecommendationModelResponse()
            response_3 = recommendations_v1_recommendation_set_validation_service_pb2.LintRecommendationSetsResponse()
            outgoing_0 = lineage_v1_impact_validation_service_pb2.PreviewImpactRequest(
                context=request.context,
                impact=lineage_v1_lineage_pb2.Impact(
                    assignee=identity_v1_refs_pb2.UserRef(email=request.interaction.subject.email),
                    customer=customers_v1_refs_pb2.CustomerRef(
                        customer_id=request.interaction.subject.customer_id,
                        display_name=request.interaction.subject.display_name
                    )
                )
            )
            steps_0 = [
                partial(deps.clients.lineage_impact_validation.PreviewImpact, outgoing_0, timeout=deps.settings.timeout)
            ]
            results_0 = await run_steps(steps_0)
            response_0 = results_0[-1]
            callbacks_1: list[
                Callable[
                    [],
                    Awaitable[
                        recommendations_v1_recommendation_model_calculation_service_pb2.CompareRecommendationModelOptionsResponse
                    ]
                ]
            ] = []
            for item_1 in request.interaction.measurements:
                outgoing_1 = recommendations_v1_recommendation_model_calculation_service_pb2.CompareRecommendationModelOptionsRequest(
                    context=request.context,
                    recommendation_model=recommendations_v1_recommendations_pb2.RecommendationModel(
                        dimensions=recommendations_v1_recommendations_pb2.RecommendationModelDimensions(
                            unit=item_1.unit
                        )
                    )
                )
                async def send_1(
                    payload: recommendations_v1_recommendation_model_calculation_service_pb2.CompareRecommendationModelOptionsRequest = outgoing_1
                ) -> recommendations_v1_recommendation_model_calculation_service_pb2.CompareRecommendationModelOptionsResponse:
                    return await deps.clients.recommendations_recommendation_model_calculation.CompareRecommendationModelOptions(
                        payload,
                        timeout=deps.settings.timeout
                    )
                callbacks_1.append(send_1)
            for callback_1 in callbacks_1:
                response_1 = await callback_1()
            outgoing_2 = recommendations_v1_recommendation_model_calculation_service_pb2.CalculateRecommendationModelRequest(
                context=request.context,
                recommendation_model=recommendations_v1_recommendations_pb2.RecommendationModel(
                    audit=common_v1_audit_pb2.AuditInfo(created_by=response_1.recommendation_model.audit.created_by),
                    components={
                        'primary': recommendations_v1_recommendations_pb2.RecommendationModelComponent(
                            quantity=response_1.recommendation_model.components.get(
                                'primary',
                                recommendations_v1_recommendations_pb2.RecommendationModelComponent()
                            ).quantity
                        )
                    }
                )
            )
            response_2 = cast(recommendations_v1_recommendation_model_calculation_service_pb2.CalculateRecommendationModelResponse, await deps.bus.request(
                'acme.recommendations.v1.InteractionCalculationService/RecalculateInteractions/2', outgoing_2, deps.settings.timeout,
            ))
            outgoing_3 = recommendations_v1_recommendation_set_validation_service_pb2.LintRecommendationSetsRequest(
                context=request.context,
                details=recommendations_v1_recommendation_set_validation_service_pb2.LintRecommendationSetsRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(email=response_0.impact.requester.email)
                ),
                recommendation_set=recommendations_v1_recommendations_pb2.RecommendationSet(
                    counterparty=customers_v1_refs_pb2.CustomerRef(
                        customer_id=response_0.impact.customer.customer_id,
                        email=response_1.recommendation_model.owner.email
                    )
                )
            )
            response_3 = await deps.clients.recommendations_recommendation_set_validation.LintRecommendationSets(
                outgoing_3,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.impact.assignee.email
            if returned_0_0:
                response.interaction.subject.email = returned_0_0
            returned_2_0 = response_2.result.details
            response.result.details.update(returned_2_0)
            returned_2_1 = response_2.recommendation_model.owner.email
            if returned_2_1:
                response.interaction.subject.email = returned_2_1
            returned_3_0 = response_3.recommendation_set.counterparty.email
            if returned_3_0:
                response.interaction.subject.email = returned_3_0
            returned_3_1 = response_3.result.details
            response.result.details.update(returned_3_1)
            echoed_0 = request.interaction_id
            response.interaction.interaction_id = echoed_0
            echoed_1 = request.interaction.correlation_id
            response.result.correlation_id = echoed_1
            return response

    async def handle_simulate_interaction(
        self,
        request: recommendations_v1_interaction_calculation_service_pb2.SimulateInteractionRequest
    ) -> recommendations_v1_interaction_calculation_service_pb2.SimulateInteractionResponse:
        """Simulates an interaction."""
        deps = self.deps
        response = recommendations_v1_interaction_calculation_service_pb2.SimulateInteractionResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SimulateInteraction', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'SimulateInteraction', {'reason': request.reason})
            await deps.repository.save_interaction(request.context.tenant_id, request.interaction)
            response_0 = recommendations_v1_recommendation_model_calculation_service_pb2.CalculateRecommendationModelResponse()
            response_1 = anomalies_v1_anomaly_service_pb2.BatchGetAnomaliesResponse()
            response_2 = audit_v1_audit_event_query_service_pb2.FindAuditEventsResponse()
            response_3 = featurestore_v1_feature_value_calculation_service_pb2.QuoteFeatureValueResponse()
            outgoing_0 = recommendations_v1_recommendation_model_calculation_service_pb2.CalculateRecommendationModelRequest(
                context=request.context,
                details=recommendations_v1_recommendation_model_calculation_service_pb2.CalculateRecommendationModelRequest.Details(
                    destination=common_v1_address_pb2.PostalAddress(postal_code=request.details.destination.postal_code)
                ),
                recommendation_model=recommendations_v1_recommendations_pb2.RecommendationModel(
                    address=common_v1_address_pb2.PostalAddress(
                        lines=list(request.details.destination.lines),
                        locality=request.details.destination.locality
                    )
                )
            )
            method_name_0 = 'CalculateRecommendationModel'
            response_0 = await getattr(
                deps.clients.recommendations_recommendation_model_calculation,
                method_name_0
            )(outgoing_0, timeout=deps.settings.timeout)
            fields_1: dict[str, Any] = {'context': request.context}
            outgoing_1 = anomalies_v1_anomaly_service_pb2.BatchGetAnomaliesRequest(**fields_1)
            response_1 = await deps.clients.anomalies_anomaly.BatchGetAnomalies(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            async for item_2 in async_messages(request.interaction.measurements):
                outgoing_2 = audit_v1_audit_event_query_service_pb2.FindAuditEventsRequest(
                    context=request.context,
                    filter=audit_v1_audit_event_query_service_pb2.FindAuditEventsRequest.Filter(
                        created_after=item_2.observed_at,
                        owner_id=request.interaction.interaction_id,
                        region=request.details.destination.region
                    )
                )
                response_2 = await deps.clients.audit_audit_event_query.FindAuditEvents(
                    outgoing_2,
                    timeout=deps.settings.timeout
                )
            for item_3 in request.interaction.measurements:
                outgoing_3 = featurestore_v1_feature_value_calculation_service_pb2.QuoteFeatureValueRequest(
                    context=request.context,
                    feature_value=featurestore_v1_featurestore_pb2.FeatureValue(
                        measurements=[featurestore_v1_featurestore_pb2.FeatureValueMeasurement(metric=item_3.metric)]
                    )
                )
                response_3 = await deps.clients.featurestore_feature_value_calculation.QuoteFeatureValue(
                    outgoing_3,
                    timeout=deps.settings.timeout
                )
            returned_0_0 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_0)
            returned_0_1 = response_0.recommendation_model.owner.display_name
            if returned_0_1:
                response.interaction.subject.display_name = returned_0_1
            returned_1_0 = response_1.result.status
            if returned_1_0:
                response.result.status = returned_1_0
            echoed_0 = request.interaction_id
            response.interaction.interaction_id = echoed_0
            echoed_1 = request.interaction.correlation_id
            response.result.correlation_id = echoed_1
            return response
