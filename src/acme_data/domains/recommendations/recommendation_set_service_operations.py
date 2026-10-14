"""Functional operations behind RecommendationSetService."""

from __future__ import annotations

from collections.abc import Awaitable
from collections.abc import Callable
from functools import partial
import asyncio
import logging

from acme.authorization.v1 import access_policy_service_pb2 as authorization_v1_access_policy_service_pb2
from acme.authorization.v1 import authorization_pb2 as authorization_v1_authorization_pb2
from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.customers.v1 import refs_pb2 as customers_v1_refs_pb2
from acme.documents.v1 import document_validation_service_pb2 as documents_v1_document_validation_service_pb2
from acme.featurestore.v1 import (
    feature_view_calculation_service_pb2 as featurestore_v1_feature_view_calculation_service_pb2,
)
from acme.featurestore.v1 import featurestore_pb2 as featurestore_v1_featurestore_pb2
from acme.fuel.v1 import fuel_card_service_pb2 as fuel_v1_fuel_card_service_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.metrics.v1 import metric_alert_export_service_pb2 as metrics_v1_metric_alert_export_service_pb2
from acme.modelregistry.v1 import modelregistry_pb2 as modelregistry_v1_modelregistry_pb2
from acme.modelregistry.v1 import (
    registered_model_validation_service_pb2 as modelregistry_v1_registered_model_validation_service_pb2,
)
from acme.notifications.v1 import (
    notification_validation_service_pb2 as notifications_v1_notification_validation_service_pb2,
)
from acme.notifications.v1 import notifications_pb2 as notifications_v1_notifications_pb2
from acme.recommendations.v1 import (
    interaction_validation_service_pb2 as recommendations_v1_interaction_validation_service_pb2,
)
from acme.recommendations.v1 import (
    recommendation_model_calculation_service_pb2 as recommendations_v1_recommendation_model_calculation_service_pb2,
)
from acme.recommendations.v1 import (
    recommendation_model_query_service_pb2 as recommendations_v1_recommendation_model_query_service_pb2,
)
from acme.recommendations.v1 import (
    recommendation_model_validation_service_pb2 as recommendations_v1_recommendation_model_validation_service_pb2,
)
from acme.recommendations.v1 import (
    recommendation_set_query_service_pb2 as recommendations_v1_recommendation_set_query_service_pb2,
)
from acme.recommendations.v1 import recommendation_set_service_pb2 as recommendations_v1_recommendation_set_service_pb2
from acme.recommendations.v1 import recommendations_pb2 as recommendations_v1_recommendations_pb2
from acme.venues.v1 import venue_query_service_pb2 as venues_v1_venue_query_service_pb2

from acme_data.domains.recommendations.adapters import RecommendationSetDeleteRecommendationSet1Adapter
from acme_data.domains.recommendations.adapters import RecommendationSetDeleteRecommendationSet1Port
from acme_data.domains.recommendations.adapters import RecommendationSetDeleteRecommendationSet3Adapter
from acme_data.domains.recommendations.dependencies import Dependencies
from acme_data.domains.recommendations.models import RecommendationSetCreateRecommendationSet1Command
from acme_data.domains.recommendations.models import to_recommendation_set_create_recommendation_set1_command
from acme_data.platform.rpc import async_messages
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


async def handle_batch_get_recommendation_sets(
    deps: Dependencies,
    request: recommendations_v1_recommendation_set_service_pb2.BatchGetRecommendationSetsRequest
) -> recommendations_v1_recommendation_set_service_pb2.BatchGetRecommendationSetsResponse:
    """Returns several recommendation sets at once."""
    response = recommendations_v1_recommendation_set_service_pb2.BatchGetRecommendationSetsResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('BatchGetRecommendationSets', extra={'fields': {'domain': 'recommendations'}})
        await deps.repository.audit(request.context.tenant_id, 'BatchGetRecommendationSets', {})
        response_0 = modelregistry_v1_registered_model_validation_service_pb2.ScoreRegisteredModelResponse()
        outgoing_0 = modelregistry_v1_registered_model_validation_service_pb2.ScoreRegisteredModelRequest(
            context=request.context,
            registered_model=modelregistry_v1_modelregistry_pb2.RegisteredModel(
                audit=common_v1_audit_pb2.AuditInfo(updated_at=request.context.deadline),
                owner=identity_v1_refs_pb2.UserRef(
                    email=request.context.actor.email,
                    user_id=request.context.actor.user_id
                )
            )
        )
        response_0 = await deps.clients.modelregistry_registered_model_validation.ScoreRegisteredModel(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.registered_model.owner.display_name
        returned_0_0_part_0 = response.recommendation_sets.add()
        if returned_0_0:
            returned_0_0_part_0.counterparty.display_name = returned_0_0
        return response


async def handle_clone_recommendation_set(
    deps: Dependencies,
    request: recommendations_v1_recommendation_set_service_pb2.CloneRecommendationSetRequest
) -> recommendations_v1_recommendation_set_service_pb2.CloneRecommendationSetResponse:
    """Creates a recommendation set."""
    response = recommendations_v1_recommendation_set_service_pb2.CloneRecommendationSetResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('CloneRecommendationSet', extra={'fields': {'request_id': request.request_id}})
        await deps.repository.audit(
            request.context.tenant_id,
            'CloneRecommendationSet',
            {'request_id': request.request_id}
        )
        await deps.repository.save_recommendation_set(request.context.tenant_id, request.recommendation_set)
        response_0 = fuel_v1_fuel_card_service_pb2.WatchFuelCardsResponse()
        outgoing_0 = fuel_v1_fuel_card_service_pb2.WatchFuelCardsRequest(
            context=request.context,
            filter=fuel_v1_fuel_card_service_pb2.WatchFuelCardsRequest.Filter(
                created_after=request.recommendation_set.audit.created_at,
                region=request.recommendation_set.billing_address.region
            ),
            subscriber=common_v1_contact_pb2.ContactInfo(email=request.recommendation_set.counterparty.email)
        )
        async for chunk_0 in deps.clients.fuel_fuel_card.WatchFuelCards(outgoing_0, timeout=deps.settings.timeout):
            response_0 = chunk_0
        echoed_0 = request.recommendation_set.issued_at
        response.recommendation_set.issued_at.CopyFrom(echoed_0)
        echoed_1 = request.recommendation_set.billing_address
        response.recommendation_set.billing_address.CopyFrom(echoed_1)
        return response


async def handle_create_recommendation_set(
    deps: Dependencies,
    request: recommendations_v1_recommendation_set_service_pb2.CreateRecommendationSetRequest
) -> recommendations_v1_recommendation_set_service_pb2.CreateRecommendationSetResponse:
    """Creates a recommendation set."""
    response = recommendations_v1_recommendation_set_service_pb2.CreateRecommendationSetResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('CreateRecommendationSet', extra={'fields': {'request_id': request.request_id}})
        await deps.repository.audit(
            request.context.tenant_id,
            'CreateRecommendationSet',
            {'request_id': request.request_id}
        )
        await deps.repository.save_recommendation_set(request.context.tenant_id, request.recommendation_set)
        response_0 = recommendations_v1_interaction_validation_service_pb2.ExplainInteractionDecisionResponse()
        response_1 = venues_v1_venue_query_service_pb2.BrowseVenuesResponse()
        response_2 = recommendations_v1_recommendation_model_calculation_service_pb2.SimulateRecommendationModelResponse()
        response_3 = metrics_v1_metric_alert_export_service_pb2.ListMetricAlertExportsResponse()
        outgoing_0 = recommendations_v1_interaction_validation_service_pb2.ExplainInteractionDecisionRequest(
            context=request.context,
            interaction=recommendations_v1_recommendations_pb2.Interaction(
                subject=customers_v1_refs_pb2.CustomerRef(
                    customer_id=request.recommendation_set.counterparty.customer_id
                )
            )
        )
        response_0 = await deps.clients.recommendations_interaction_validation.ExplainInteractionDecision(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        command_1 = RecommendationSetCreateRecommendationSet1Command.model_validate(
            {
                'context': request.context,
                'filter_region': request.recommendation_set.billing_address.region,
                'filter_created_after': response_0.outcome.effective_at
            }
        )
        outgoing_1 = to_recommendation_set_create_recommendation_set1_command(command_1)
        response_1 = await deps.clients.venues_venue_query.BrowseVenues(outgoing_1, timeout=deps.settings.timeout)
        outgoing_2 = recommendations_v1_recommendation_model_calculation_service_pb2.SimulateRecommendationModelRequest(
            context=request.context,
            details=recommendations_v1_recommendation_model_calculation_service_pb2.SimulateRecommendationModelRequest.Details(
                destination=common_v1_address_pb2.PostalAddress(
                    region=request.recommendation_set.billing_address.region
                )
            ),
            recommendation_model=recommendations_v1_recommendations_pb2.RecommendationModel(
                address=common_v1_address_pb2.PostalAddress(
                    recipient=request.recommendation_set.billing_address.recipient
                ),
                owner=identity_v1_refs_pb2.UserRef(display_name=request.recommendation_set.counterparty.display_name)
            )
        )
        send_2 = partial(
            deps.clients.recommendations_recommendation_model_calculation.SimulateRecommendationModel,
            timeout=deps.settings.timeout
        )
        response_2 = await send_2(outgoing_2)
        for item_3 in request.recommendation_set.lines:
            outgoing_3 = metrics_v1_metric_alert_export_service_pb2.ListMetricAlertExportsRequest(
                context=request.context,
                filter=metrics_v1_metric_alert_export_service_pb2.ListMetricAlertExportsRequest.Filter(
                    created_after=request.recommendation_set.due_at,
                    labels=dict(item_3.attributes),
                    owner_id=item_3.line_id,
                    region=response_2.recommendation_model.address.region
                )
            )
            response_3 = await deps.clients.metrics_metric_alert_export.ListMetricAlertExports(
                outgoing_3,
                timeout=deps.settings.timeout
            )
        returned_0_0 = response_0.outcome.status
        if returned_0_0:
            response.result.status = returned_0_0
        returned_1_0 = response_1.result.reference_ids
        response.result.reference_ids.extend(returned_1_0)
        returned_2_0 = response_2.recommendation_model.owner.display_name
        if returned_2_0:
            response.recommendation_set.counterparty.display_name = returned_2_0
        returned_2_1 = response_2.result.message
        if returned_2_1:
            response.result.message = returned_2_1
        echoed_0 = request.recommendation_set.billing_address
        response.recommendation_set.billing_address.CopyFrom(echoed_0)
        echoed_1 = request.recommendation_set.notes
        response.recommendation_set.notes = echoed_1
        return response


async def handle_delete_recommendation_set(
    deps: Dependencies,
    request: recommendations_v1_recommendation_set_service_pb2.DeleteRecommendationSetRequest
) -> recommendations_v1_recommendation_set_service_pb2.DeleteRecommendationSetResponse:
    """Deletes a recommendation set."""
    response = recommendations_v1_recommendation_set_service_pb2.DeleteRecommendationSetResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('DeleteRecommendationSet', extra={'fields': {'force': request.force}})
        await deps.repository.audit(request.context.tenant_id, 'DeleteRecommendationSet', {'force': request.force})
        response_0 = recommendations_v1_recommendation_model_validation_service_pb2.ScoreRecommendationModelResponse()
        response_1 = recommendations_v1_recommendation_model_query_service_pb2.FindRecommendationModelsResponse()
        response_2 = recommendations_v1_recommendation_set_query_service_pb2.ExportRecommendationSetsResponse()
        response_3 = featurestore_v1_feature_view_calculation_service_pb2.CalculateFeatureViewResponse()
        outgoing_0 = recommendations_v1_recommendation_model_validation_service_pb2.ScoreRecommendationModelRequest(
            context=request.context,
            reason=request.reason,
            recommendation_model=recommendations_v1_recommendations_pb2.RecommendationModel(
                audit=common_v1_audit_pb2.AuditInfo(etag=request.etag),
                owner=identity_v1_refs_pb2.UserRef(
                    email=request.context.actor.email,
                    user_id=request.context.actor.user_id
                )
            )
        )
        response_0 = await deps.clients.recommendations_recommendation_model_validation.ScoreRecommendationModel(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = recommendations_v1_recommendation_model_query_service_pb2.FindRecommendationModelsRequest(
            context=request.context,
            filter=recommendations_v1_recommendation_model_query_service_pb2.FindRecommendationModelsRequest.Filter(
                created_after=response_0.recommendation_model.audit.created_at,
                owner_id=response_0.recommendation_model.recommendation_model_id,
                region=response_0.recommendation_model.address.region
            )
        )
        port_1: RecommendationSetDeleteRecommendationSet1Port = RecommendationSetDeleteRecommendationSet1Adapter(
            deps.clients.recommendations_recommendation_model_query,
            deps.settings.timeout
        )
        response_1 = await port_1.execute(outgoing_1)
        outgoing_2 = recommendations_v1_recommendation_set_query_service_pb2.ExportRecommendationSetsRequest(
            context=request.context,
            filter=recommendations_v1_recommendation_set_query_service_pb2.ExportRecommendationSetsRequest.Filter(
                created_after=response_0.recommendation_model.audit.updated_at,
                labels=dict(response_0.recommendation_model.specs),
                owner_id=response_0.recommendation_model.components.get(
                    'primary',
                    recommendations_v1_recommendations_pb2.RecommendationModelComponent()
                ).component_id,
                region=response_0.recommendation_model.address.region
            )
        )
        async for chunk_2 in deps.clients.recommendations_recommendation_set_query.ExportRecommendationSets(
            outgoing_2,
            timeout=deps.settings.timeout
        ):
            response_2 = chunk_2
        outgoing_3 = featurestore_v1_feature_view_calculation_service_pb2.CalculateFeatureViewRequest(
            context=request.context,
            feature_view=featurestore_v1_featurestore_pb2.FeatureView(
                address=common_v1_address_pb2.PostalAddress(recipient=response_0.recommendation_model.address.recipient)
            )
        )
        response_3 = await RecommendationSetDeleteRecommendationSet3Adapter(
            deps.clients.featurestore_feature_view_calculation,
            deps.settings.timeout
        )(outgoing_3)
        returned_0_0 = response_0.result.status
        if returned_0_0:
            response.result.status = returned_0_0
        returned_1_0 = response_1.result.status
        if returned_1_0:
            response.result.status = returned_1_0
        returned_1_1 = response_1.result.reference_ids
        response.result.reference_ids.extend(returned_1_1)
        returned_3_0 = response_3.result.message
        if returned_3_0:
            response.result.message = returned_3_0
        returned_3_1 = response_3.result.correlation_id
        if returned_3_1:
            response.result.correlation_id = returned_3_1
        return response


async def handle_get_recommendation_set(
    deps: Dependencies,
    request: recommendations_v1_recommendation_set_service_pb2.GetRecommendationSetRequest
) -> recommendations_v1_recommendation_set_service_pb2.GetRecommendationSetResponse:
    """Returns a recommendation set."""
    response = recommendations_v1_recommendation_set_service_pb2.GetRecommendationSetResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('GetRecommendationSet', extra={'fields': {'domain': 'recommendations'}})
        await deps.repository.audit(request.context.tenant_id, 'GetRecommendationSet', {})
        response_0 = documents_v1_document_validation_service_pb2.CheckDocumentEligibilityResponse()
        outgoing_0 = documents_v1_document_validation_service_pb2.CheckDocumentEligibilityRequest(
            context=request.context,
            details=documents_v1_document_validation_service_pb2.CheckDocumentEligibilityRequest.Details(
                contact=common_v1_contact_pb2.ContactInfo(email=request.context.actor.email),
                locale=request.context.locale
            )
        )
        response_0 = await deps.clients.documents_document_validation.CheckDocumentEligibility(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.document.audit.updated_by
        if returned_0_0:
            response.recommendation_set.audit.updated_by = returned_0_0
        echoed_0 = request.recommendation_set_id
        response.recommendation_set.recommendation_set_id = echoed_0
        return response


async def handle_list_recommendation_sets(
    deps: Dependencies,
    request: recommendations_v1_recommendation_set_service_pb2.ListRecommendationSetsRequest
) -> recommendations_v1_recommendation_set_service_pb2.ListRecommendationSetsResponse:
    """Lists recommendation sets a page at a time."""
    response = recommendations_v1_recommendation_set_service_pb2.ListRecommendationSetsResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('ListRecommendationSets', extra={'fields': {'order_by': request.order_by}})
        await deps.repository.audit(request.context.tenant_id, 'ListRecommendationSets', {'order_by': request.order_by})
        response_0 = notifications_v1_notification_validation_service_pb2.ExplainNotificationDecisionResponse()
        response_1 = authorization_v1_access_policy_service_pb2.CreateAccessPolicyResponse()
        outgoing_0 = notifications_v1_notification_validation_service_pb2.ExplainNotificationDecisionRequest(
            context=request.context,
            notification=notifications_v1_notifications_pb2.Notification(
                assignee=identity_v1_refs_pb2.UserRef(user_id=request.context.actor.user_id),
                requester=common_v1_contact_pb2.ContactInfo(email=request.context.actor.email)
            )
        )
        response_0 = await deps.clients.notifications_notification_validation.ExplainNotificationDecision(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = authorization_v1_access_policy_service_pb2.CreateAccessPolicyRequest(
            access_policy=authorization_v1_authorization_pb2.AccessPolicy(
                audit=common_v1_audit_pb2.AuditInfo(etag=response_0.notification.audit.etag)
            ),
            context=request.context
        )
        method_name_1 = 'CreateAccessPolicy'
        response_1 = await getattr(
            deps.clients.authorization_access_policy,
            method_name_1
        )(outgoing_1, timeout=deps.settings.timeout)
        returned_0_0 = response_0.result.details
        response.result.details.update(returned_0_0)
        returned_0_1 = response_0.notification.sla.due_at
        returned_0_1_part_0 = response.recommendation_sets.add()
        if returned_0_1.ListFields():
            returned_0_1_part_0.due_at.MergeFrom(returned_0_1)
        returned_1_0 = response_1.access_policy.audit.created_by
        returned_1_0_part_0 = response.recommendation_sets.add()
        if returned_1_0:
            returned_1_0_part_0.audit.created_by = returned_1_0
        returned_1_1 = response_1.access_policy.audit.etag
        returned_1_1_part_0 = response.recommendation_sets.add()
        if returned_1_1:
            returned_1_1_part_0.audit.etag = returned_1_1
        return response


async def handle_search_recommendation_sets(
    deps: Dependencies,
    request: recommendations_v1_recommendation_set_service_pb2.SearchRecommendationSetsRequest
) -> recommendations_v1_recommendation_set_service_pb2.SearchRecommendationSetsResponse:
    """Lists recommendation sets a page at a time."""
    response = recommendations_v1_recommendation_set_service_pb2.SearchRecommendationSetsResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('SearchRecommendationSets', extra={'fields': {'order_by': request.order_by}})
        await deps.repository.audit(
            request.context.tenant_id,
            'SearchRecommendationSets',
            {'order_by': request.order_by}
        )
        return response


async def handle_update_recommendation_set(
    deps: Dependencies,
    request: recommendations_v1_recommendation_set_service_pb2.UpdateRecommendationSetRequest
) -> recommendations_v1_recommendation_set_service_pb2.UpdateRecommendationSetResponse:
    """Changes a recommendation set."""
    response = recommendations_v1_recommendation_set_service_pb2.UpdateRecommendationSetResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('UpdateRecommendationSet', extra={'fields': {'allow_missing': request.allow_missing}})
        await deps.repository.audit(
            request.context.tenant_id,
            'UpdateRecommendationSet',
            {'allow_missing': request.allow_missing}
        )
        await deps.repository.save_recommendation_set(request.context.tenant_id, request.recommendation_set)
        response_0 = featurestore_v1_feature_view_calculation_service_pb2.SimulateFeatureViewResponse()
        outgoing_0 = featurestore_v1_feature_view_calculation_service_pb2.SimulateFeatureViewRequest(
            context=request.context,
            feature_view=featurestore_v1_featurestore_pb2.FeatureView(
                audit=common_v1_audit_pb2.AuditInfo(
                    created_at=request.recommendation_set.audit.created_at,
                    created_by=request.recommendation_set.audit.created_by
                ),
                owner=identity_v1_refs_pb2.UserRef(display_name=request.recommendation_set.counterparty.display_name)
            )
        )
        response_0 = await deps.clients.featurestore_feature_view_calculation.SimulateFeatureView(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.feature_view.address.lines
        response.recommendation_set.billing_address.lines.extend(returned_0_0)
        echoed_0 = request.recommendation_set.metadata
        response.recommendation_set.metadata.update(echoed_0)
        echoed_1 = request.recommendation_set.status
        response.recommendation_set.status = echoed_1
        return response
