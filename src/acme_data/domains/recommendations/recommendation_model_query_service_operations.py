"""Functional operations behind RecommendationModelQueryService."""

from __future__ import annotations

import logging

from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.configuration.v1 import config_set_service_pb2 as configuration_v1_config_set_service_pb2
from acme.customers.v1 import refs_pb2 as customers_v1_refs_pb2
from acme.ledger.v1 import ledger_account_validation_service_pb2 as ledger_v1_ledger_account_validation_service_pb2
from acme.recommendations.v1 import (
    interaction_calculation_service_pb2 as recommendations_v1_interaction_calculation_service_pb2,
)
from acme.recommendations.v1 import (
    recommendation_model_query_service_pb2 as recommendations_v1_recommendation_model_query_service_pb2,
)
from acme.recommendations.v1 import recommendations_pb2 as recommendations_v1_recommendations_pb2
from acme.telematics.v1 import telematics_pb2 as telematics_v1_telematics_pb2
from acme.telematics.v1 import (
    telemetry_reading_calculation_service_pb2 as telematics_v1_telemetry_reading_calculation_service_pb2,
)

from acme_data.domains.recommendations.dependencies import Dependencies
from acme_data.domains.recommendations.models import RecommendationModelQueryExportRecommendationModels1Command
from acme_data.domains.recommendations.models import to_recommendation_model_query_export_recommendation_models1_command
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


async def handle_browse_recommendation_models(
    deps: Dependencies,
    request: recommendations_v1_recommendation_model_query_service_pb2.BrowseRecommendationModelsRequest
) -> recommendations_v1_recommendation_model_query_service_pb2.BrowseRecommendationModelsResponse:
    """Lists recommendation models a page at a time."""
    response = recommendations_v1_recommendation_model_query_service_pb2.BrowseRecommendationModelsResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('BrowseRecommendationModels', extra={'fields': {'order_by': request.order_by}})
        await deps.repository.audit(
            request.context.tenant_id,
            'BrowseRecommendationModels',
            {'order_by': request.order_by}
        )
        return response


async def handle_count_recommendation_models(
    deps: Dependencies,
    request: recommendations_v1_recommendation_model_query_service_pb2.CountRecommendationModelsRequest
) -> recommendations_v1_recommendation_model_query_service_pb2.CountRecommendationModelsResponse:
    """Counts recommendation models by status."""
    response = recommendations_v1_recommendation_model_query_service_pb2.CountRecommendationModelsResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('CountRecommendationModels', extra={'fields': {'order_by': request.order_by}})
        await deps.repository.audit(
            request.context.tenant_id,
            'CountRecommendationModels',
            {'order_by': request.order_by}
        )
        response_0 = recommendations_v1_interaction_calculation_service_pb2.SimulateInteractionResponse()
        outgoing_0 = recommendations_v1_interaction_calculation_service_pb2.SimulateInteractionRequest(
            context=request.context,
            details=recommendations_v1_interaction_calculation_service_pb2.SimulateInteractionRequest.Details(
                destination=common_v1_address_pb2.PostalAddress(region=request.filter.region)
            ),
            interaction=recommendations_v1_recommendations_pb2.Interaction(
                subject=customers_v1_refs_pb2.CustomerRef(email=request.context.actor.email)
            )
        )
        response_0 = await deps.clients.recommendations_interaction_calculation.SimulateInteraction(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.result.details
        response.result.details.update(returned_0_0)
        return response


async def handle_export_recommendation_models(
    deps: Dependencies,
    request: recommendations_v1_recommendation_model_query_service_pb2.ExportRecommendationModelsRequest
) -> recommendations_v1_recommendation_model_query_service_pb2.ExportRecommendationModelsResponse:
    """Streams every matching recommendation model."""
    response = recommendations_v1_recommendation_model_query_service_pb2.ExportRecommendationModelsResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('ExportRecommendationModels', extra={'fields': {'destination_uri': request.destination_uri}})
        await deps.repository.audit(
            request.context.tenant_id,
            'ExportRecommendationModels',
            {'destination_uri': request.destination_uri}
        )
        response_0 = ledger_v1_ledger_account_validation_service_pb2.LintLedgerAccountsResponse()
        response_1 = recommendations_v1_interaction_calculation_service_pb2.CalculateInteractionResponse()
        outgoing_0 = ledger_v1_ledger_account_validation_service_pb2.LintLedgerAccountsRequest(
            context=request.context,
            details=ledger_v1_ledger_account_validation_service_pb2.LintLedgerAccountsRequest.Details(
                contact=common_v1_contact_pb2.ContactInfo(email=request.context.actor.email)
            )
        )
        response_0 = await deps.clients.ledger_ledger_account_validation.LintLedgerAccounts(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        command_1 = RecommendationModelQueryExportRecommendationModels1Command(
            context=request.context,
            interaction_subject_display_name=response_0.ledger_account.holder.display_name,
            interaction_correlation_id=response_0.result.correlation_id,
            details_destination_region=request.filter.region,
            interaction_subject_email=response_0.ledger_account.contact.email
        )
        outgoing_1 = to_recommendation_model_query_export_recommendation_models1_command(command_1)
        response_1 = await deps.clients.recommendations_interaction_calculation.CalculateInteraction(
            outgoing_1,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.ledger_account.contact.email
        if returned_0_0:
            response.recommendation_model.owner.email = returned_0_0
        returned_1_0 = response_1.result.status
        if returned_1_0:
            response.result.status = returned_1_0
        returned_1_1 = response_1.result.details
        response.result.details.update(returned_1_1)
        return response


async def handle_find_recommendation_models(
    deps: Dependencies,
    request: recommendations_v1_recommendation_model_query_service_pb2.FindRecommendationModelsRequest
) -> recommendations_v1_recommendation_model_query_service_pb2.FindRecommendationModelsResponse:
    """Lists recommendation models a page at a time."""
    response = recommendations_v1_recommendation_model_query_service_pb2.FindRecommendationModelsResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('FindRecommendationModels', extra={'fields': {'order_by': request.order_by}})
        await deps.repository.audit(
            request.context.tenant_id,
            'FindRecommendationModels',
            {'order_by': request.order_by}
        )
        response_0 = recommendations_v1_interaction_calculation_service_pb2.SimulateInteractionResponse()
        outgoing_0 = recommendations_v1_interaction_calculation_service_pb2.SimulateInteractionRequest(
            context=request.context,
            details=recommendations_v1_interaction_calculation_service_pb2.SimulateInteractionRequest.Details(
                destination=common_v1_address_pb2.PostalAddress(region=request.filter.region)
            ),
            interaction=recommendations_v1_recommendations_pb2.Interaction(
                measurements=[
                    recommendations_v1_recommendations_pb2.InteractionMeasurement(
                        observed_at=request.filter.created_after
                    )
                ],
                subject=customers_v1_refs_pb2.CustomerRef(email=request.context.actor.email)
            )
        )
        response_0 = await deps.clients.recommendations_interaction_calculation.SimulateInteraction(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.result.status
        if returned_0_0:
            response.result.status = returned_0_0
        returned_0_1 = response_0.interaction.subject.display_name
        returned_0_1_part_0 = response.recommendation_models.add()
        if returned_0_1:
            returned_0_1_part_0.owner.display_name = returned_0_1
        return response


async def handle_lookup_recommendation_model(
    deps: Dependencies,
    request: recommendations_v1_recommendation_model_query_service_pb2.LookupRecommendationModelRequest
) -> recommendations_v1_recommendation_model_query_service_pb2.LookupRecommendationModelResponse:
    """Returns a recommendation model."""
    response = recommendations_v1_recommendation_model_query_service_pb2.LookupRecommendationModelResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('LookupRecommendationModel', extra={'fields': {'domain': 'recommendations'}})
        await deps.repository.audit(request.context.tenant_id, 'LookupRecommendationModel', {})
        response_0 = telematics_v1_telemetry_reading_calculation_service_pb2.CompareTelemetryReadingOptionsResponse()
        outgoing_0 = telematics_v1_telemetry_reading_calculation_service_pb2.CompareTelemetryReadingOptionsRequest(
            context=request.context,
            telemetry_reading=telematics_v1_telematics_pb2.TelemetryReading(
                correlation_id=request.recommendation_model_id,
                occurred_at=request.context.deadline
            )
        )
        response_0 = await deps.clients.telematics_telemetry_reading_calculation.CompareTelemetryReadingOptions(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.result.status
        if returned_0_0:
            response.result.status = returned_0_0
        returned_0_1 = response_0.result.message
        if returned_0_1:
            response.result.message = returned_0_1
        echoed_0 = request.recommendation_model_id
        response.recommendation_model.recommendation_model_id = echoed_0
        return response


async def handle_peek_recommendation_model(
    deps: Dependencies,
    request: recommendations_v1_recommendation_model_query_service_pb2.PeekRecommendationModelRequest
) -> recommendations_v1_recommendation_model_query_service_pb2.PeekRecommendationModelResponse:
    """Returns a recommendation model."""
    response = recommendations_v1_recommendation_model_query_service_pb2.PeekRecommendationModelResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('PeekRecommendationModel', extra={'fields': {'domain': 'recommendations'}})
        await deps.repository.audit(request.context.tenant_id, 'PeekRecommendationModel', {})
        response_0 = configuration_v1_config_set_service_pb2.SearchConfigSetsResponse()
        outgoing_0 = configuration_v1_config_set_service_pb2.SearchConfigSetsRequest(
            context=request.context,
            filter=configuration_v1_config_set_service_pb2.SearchConfigSetsRequest.Filter(
                created_after=request.context.deadline,
                owner_id=request.recommendation_model_id
            )
        )
        response_0 = await deps.clients.configuration_config_set.SearchConfigSets(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.result.reference_ids
        response.result.reference_ids.extend(returned_0_0)
        returned_0_1 = response_0.result.correlation_id
        if returned_0_1:
            response.result.correlation_id = returned_0_1
        echoed_0 = request.recommendation_model_id
        response.recommendation_model.recommendation_model_id = echoed_0
        return response


async def handle_suggest_recommendation_models(
    deps: Dependencies,
    request: recommendations_v1_recommendation_model_query_service_pb2.SuggestRecommendationModelsRequest
) -> recommendations_v1_recommendation_model_query_service_pb2.SuggestRecommendationModelsResponse:
    """Lists recommendation models a page at a time."""
    response = recommendations_v1_recommendation_model_query_service_pb2.SuggestRecommendationModelsResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('SuggestRecommendationModels', extra={'fields': {'order_by': request.order_by}})
        await deps.repository.audit(
            request.context.tenant_id,
            'SuggestRecommendationModels',
            {'order_by': request.order_by}
        )
        response_0 = recommendations_v1_interaction_calculation_service_pb2.RecalculateInteractionsResponse()
        outgoing_0 = recommendations_v1_interaction_calculation_service_pb2.RecalculateInteractionsRequest(
            context=request.context,
            details=recommendations_v1_interaction_calculation_service_pb2.RecalculateInteractionsRequest.Details(
                destination=common_v1_address_pb2.PostalAddress(region=request.filter.region)
            )
        )
        response_0 = await deps.clients.recommendations_interaction_calculation.RecalculateInteractions(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.result.message
        if returned_0_0:
            response.result.message = returned_0_0
        returned_0_1 = response_0.result.details
        response.result.details.update(returned_0_1)
        return response
