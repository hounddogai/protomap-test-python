"""Application workflow for DemandForecast Query."""

from __future__ import annotations

from functools import partial
from typing import Any
import logging

from google.protobuf.json_format import MessageToDict
from google.protobuf.json_format import ParseDict

from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.common.v1 import paging_pb2 as common_v1_paging_pb2
from acme.documents.v1 import document_query_service_pb2 as documents_v1_document_query_service_pb2
from acme.featurestore.v1 import (
    feature_value_validation_service_pb2 as featurestore_v1_feature_value_validation_service_pb2,
)
from acme.featurestore.v1 import featurestore_pb2 as featurestore_v1_featurestore_pb2
from acme.forecasting.v1 import demand_forecast_query_service_pb2 as forecasting_v1_demand_forecast_query_service_pb2
from acme.forecasting.v1 import (
    demand_forecast_validation_service_pb2 as forecasting_v1_demand_forecast_validation_service_pb2,
)
from acme.forecasting.v1 import forecasting_pb2 as forecasting_v1_forecasting_pb2
from acme.forecasting.v1 import scenario_validation_service_pb2 as forecasting_v1_scenario_validation_service_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.labeling.v1 import labeling_pb2 as labeling_v1_labeling_pb2
from acme.labeling.v1 import labeling_task_validation_service_pb2 as labeling_v1_labeling_task_validation_service_pb2
from acme.notifications.v1 import notification_query_service_pb2 as notifications_v1_notification_query_service_pb2
from acme.ratelimiting.v1 import rate_limit_query_service_pb2 as ratelimiting_v1_rate_limit_query_service_pb2
from acme.recommendations.v1 import (
    recommendation_set_query_service_pb2 as recommendations_v1_recommendation_set_query_service_pb2,
)
from acme.tours.v1 import tour_query_service_pb2 as tours_v1_tour_query_service_pb2
from acme.venues.v1 import venue_query_service_pb2 as venues_v1_venue_query_service_pb2

from acme_data.domains.forecasting import hooks
from acme_data.domains.forecasting.dependencies import Dependencies
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import run_steps
from acme_data.platform.tenancy import tenant_id
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class DemandForecastQueryServicerWorkflow:
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    async def handle_browse_demand_forecasts(
        self,
        request: forecasting_v1_demand_forecast_query_service_pb2.BrowseDemandForecastsRequest
    ) -> forecasting_v1_demand_forecast_query_service_pb2.BrowseDemandForecastsResponse:
        """Lists demand forecasts a page at a time."""
        deps = self.deps
        response = forecasting_v1_demand_forecast_query_service_pb2.BrowseDemandForecastsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('BrowseDemandForecasts', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'BrowseDemandForecasts',
                {'order_by': request.order_by}
            )
            response_0 = featurestore_v1_feature_value_validation_service_pb2.PreviewFeatureValueResponse()
            outgoing_0 = featurestore_v1_feature_value_validation_service_pb2.PreviewFeatureValueRequest(
                context=request.context,
                details=featurestore_v1_feature_value_validation_service_pb2.PreviewFeatureValueRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(email=request.context.actor.email),
                    locale=request.context.locale
                ),
                feature_value=featurestore_v1_featurestore_pb2.FeatureValue(occurred_at=request.filter.created_after)
            )
            response_0 = await deps.clients.featurestore_feature_value_validation.PreviewFeatureValue(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_0)
            return response

    async def handle_count_demand_forecasts(
        self,
        request: forecasting_v1_demand_forecast_query_service_pb2.CountDemandForecastsRequest
    ) -> forecasting_v1_demand_forecast_query_service_pb2.CountDemandForecastsResponse:
        """Counts demand forecasts by status."""
        deps = self.deps
        response = forecasting_v1_demand_forecast_query_service_pb2.CountDemandForecastsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CountDemandForecasts', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'CountDemandForecasts',
                {'order_by': request.order_by}
            )
            return response

    async def handle_export_demand_forecasts(
        self,
        request: forecasting_v1_demand_forecast_query_service_pb2.ExportDemandForecastsRequest
    ) -> forecasting_v1_demand_forecast_query_service_pb2.ExportDemandForecastsResponse:
        """Streams every matching demand forecast."""
        deps = self.deps
        response = forecasting_v1_demand_forecast_query_service_pb2.ExportDemandForecastsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ExportDemandForecasts', extra={'fields': {'destination_uri': request.destination_uri}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ExportDemandForecasts',
                {'destination_uri': request.destination_uri}
            )
            response_0 = labeling_v1_labeling_task_validation_service_pb2.ExplainLabelingTaskDecisionResponse()
            response_1 = venues_v1_venue_query_service_pb2.SuggestVenuesResponse()
            outgoing_0 = labeling_v1_labeling_task_validation_service_pb2.ExplainLabelingTaskDecisionRequest(
                context=request.context,
                labeling_task=labeling_v1_labeling_pb2.LabelingTask(
                    assignee=identity_v1_refs_pb2.UserRef(user_id=request.context.actor.user_id),
                    requester=common_v1_contact_pb2.ContactInfo(email=request.context.actor.email),
                    sla=labeling_v1_labeling_pb2.LabelingTaskSla(due_at=request.filter.created_after)
                )
            )
            response_0 = await hooks.demand_forecast_query_export_demand_forecasts0(
                deps.clients.labeling_labeling_task_validation,
                outgoing_0,
                deps.settings.timeout
            )
            outgoing_1 = venues_v1_venue_query_service_pb2.SuggestVenuesRequest()
            outgoing_1.context.CopyFrom(request.context)
            outgoing_1.filter.query = request.filter.query
            outgoing_1.filter.created_after.CopyFrom(request.filter.created_after)
            outgoing_1.filter.region = request.filter.region
            outgoing_1.filter.labels.update(dict(request.filter.labels))
            outgoing_1.context.tenant_id = tenant_id.get()
            response_1 = await deps.clients.venues_venue_query.SuggestVenues(outgoing_1, timeout=deps.settings.timeout)
            returned_0_0 = response_0.result.correlation_id
            if returned_0_0:
                response.result.correlation_id = returned_0_0
            returned_0_1 = response_0.labeling_task.audit.created_at
            if returned_0_1.ListFields():
                response.demand_forecast.audit.created_at.MergeFrom(returned_0_1)
            returned_1_0 = response_1.result.message
            if returned_1_0:
                response.result.message = returned_1_0
            returned_1_1 = response_1.result.correlation_id
            if returned_1_1:
                response.result.correlation_id = returned_1_1
            echoed_0 = request.filter.region
            response.demand_forecast.billing_address.region = echoed_0
            return response

    async def handle_find_demand_forecasts(
        self,
        request: forecasting_v1_demand_forecast_query_service_pb2.FindDemandForecastsRequest
    ) -> forecasting_v1_demand_forecast_query_service_pb2.FindDemandForecastsResponse:
        """Lists demand forecasts a page at a time."""
        deps = self.deps
        response = forecasting_v1_demand_forecast_query_service_pb2.FindDemandForecastsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('FindDemandForecasts', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'FindDemandForecasts',
                {'order_by': request.order_by}
            )
            response_0 = forecasting_v1_demand_forecast_validation_service_pb2.NormalizeDemandForecastResponse()
            response_1 = tours_v1_tour_query_service_pb2.BrowseToursResponse()
            outgoing_0 = forecasting_v1_demand_forecast_validation_service_pb2.NormalizeDemandForecastRequest(
                context=request.context,
                demand_forecast=forecasting_v1_forecasting_pb2.DemandForecast(
                    audit=common_v1_audit_pb2.AuditInfo(created_at=request.filter.created_after),
                    billing_address=common_v1_address_pb2.PostalAddress(region=request.filter.region)
                ),
                details=forecasting_v1_demand_forecast_validation_service_pb2.NormalizeDemandForecastRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(email=request.context.actor.email)
                )
            )
            response_0 = await deps.clients.forecasting_demand_forecast_validation.NormalizeDemandForecast(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = tours_v1_tour_query_service_pb2.BrowseToursRequest(
                context=request.context,
                filter=tours_v1_tour_query_service_pb2.BrowseToursRequest.Filter(
                    labels=dict(request.filter.labels),
                    owner_id=request.filter.owner_id
                ),
                page=common_v1_paging_pb2.PageRequest(page_token=request.page.page_token)
            )
            steps_1 = [partial(deps.clients.tours_tour_query.BrowseTours, outgoing_1, timeout=deps.settings.timeout)]
            results_1 = await run_steps(steps_1)
            response_1 = results_1[-1]
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.result.message = returned_0_0
            returned_1_0 = response_1.page_info.next_page_token
            if returned_1_0:
                response.page_info.next_page_token = returned_1_0
            return response

    async def handle_lookup_demand_forecast(
        self,
        request: forecasting_v1_demand_forecast_query_service_pb2.LookupDemandForecastRequest
    ) -> forecasting_v1_demand_forecast_query_service_pb2.LookupDemandForecastResponse:
        """Returns a demand forecast."""
        deps = self.deps
        response = forecasting_v1_demand_forecast_query_service_pb2.LookupDemandForecastResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('LookupDemandForecast', extra={'fields': {'domain': 'forecasting'}})
            await deps.repository.audit(request.context.tenant_id, 'LookupDemandForecast', {})
            response_0 = documents_v1_document_query_service_pb2.ExportDocumentsResponse()
            outgoing_0 = documents_v1_document_query_service_pb2.ExportDocumentsRequest(
                context=request.context,
                filter=documents_v1_document_query_service_pb2.ExportDocumentsRequest.Filter(
                    created_after=request.context.deadline,
                    owner_id=request.demand_forecast_id
                )
            )
            async for chunk_0 in deps.clients.documents_document_query.ExportDocuments(
                outgoing_0,
                timeout=deps.settings.timeout
            ):
                response_0 = chunk_0
            echoed_0 = request.demand_forecast_id
            response.demand_forecast.demand_forecast_id = echoed_0
            return response

    async def handle_peek_demand_forecast(
        self,
        request: forecasting_v1_demand_forecast_query_service_pb2.PeekDemandForecastRequest
    ) -> forecasting_v1_demand_forecast_query_service_pb2.PeekDemandForecastResponse:
        """Returns a demand forecast."""
        deps = self.deps
        response = forecasting_v1_demand_forecast_query_service_pb2.PeekDemandForecastResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('PeekDemandForecast', extra={'fields': {'locale': request.context.locale}})
            await deps.repository.audit(
                request.context.tenant_id,
                'PeekDemandForecast',
                {'locale': request.context.locale}
            )
            echoed_0 = request.demand_forecast_id
            response.demand_forecast.demand_forecast_id = echoed_0
            return response

    async def handle_resolve_demand_forecasts(
        self,
        request: forecasting_v1_demand_forecast_query_service_pb2.ResolveDemandForecastsRequest
    ) -> forecasting_v1_demand_forecast_query_service_pb2.ResolveDemandForecastsResponse:
        """Returns several demand forecasts at once."""
        deps = self.deps
        response = forecasting_v1_demand_forecast_query_service_pb2.ResolveDemandForecastsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ResolveDemandForecasts', extra={'fields': {'domain': 'forecasting'}})
            await deps.repository.audit(request.context.tenant_id, 'ResolveDemandForecasts', {})
            response_0 = recommendations_v1_recommendation_set_query_service_pb2.FindRecommendationSetsResponse()
            outgoing_0 = recommendations_v1_recommendation_set_query_service_pb2.FindRecommendationSetsRequest(
                context=request.context,
                filter=recommendations_v1_recommendation_set_query_service_pb2.FindRecommendationSetsRequest.Filter(
                    created_after=request.context.deadline,
                    labels=dict(request.context.baggage),
                    owner_id=request.context.trace_id
                )
            )
            response_0 = await deps.clients.recommendations_recommendation_set_query.FindRecommendationSets(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.status
            if returned_0_0:
                response.result.status = returned_0_0
            return response

    async def handle_suggest_demand_forecasts(
        self,
        request: forecasting_v1_demand_forecast_query_service_pb2.SuggestDemandForecastsRequest
    ) -> forecasting_v1_demand_forecast_query_service_pb2.SuggestDemandForecastsResponse:
        """Lists demand forecasts a page at a time."""
        deps = self.deps
        response = forecasting_v1_demand_forecast_query_service_pb2.SuggestDemandForecastsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SuggestDemandForecasts', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'SuggestDemandForecasts',
                {'order_by': request.order_by}
            )
            response_0 = forecasting_v1_scenario_validation_service_pb2.ScoreScenarioResponse()
            response_1 = recommendations_v1_recommendation_set_query_service_pb2.SummarizeRecommendationSetsResponse()
            outgoing_0 = forecasting_v1_scenario_validation_service_pb2.ScoreScenarioRequest(
                context=request.context,
                details=forecasting_v1_scenario_validation_service_pb2.ScoreScenarioRequest.Details(
                    destination=common_v1_address_pb2.PostalAddress(region=request.filter.region)
                ),
                scenario=forecasting_v1_forecasting_pb2.Scenario(
                    assignee=identity_v1_refs_pb2.UserRef(user_id=request.context.actor.user_id),
                    audit=common_v1_audit_pb2.AuditInfo(created_at=request.filter.created_after),
                    requester=common_v1_contact_pb2.ContactInfo(email=request.context.actor.email)
                )
            )
            response_0 = await deps.clients.forecasting_scenario_validation.ScoreScenario(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = recommendations_v1_recommendation_set_query_service_pb2.SummarizeRecommendationSetsRequest(
                annotations=dict(response_0.scenario.custom_fields),
                context=request.context,
                details=recommendations_v1_recommendation_set_query_service_pb2.SummarizeRecommendationSetsRequest.Details(
                    filters=dict(response_0.result.details)
                )
            )
            method_name_1 = 'SummarizeRecommendationSets'
            response_1 = await getattr(
                deps.clients.recommendations_recommendation_set_query,
                method_name_1
            )(outgoing_1, timeout=deps.settings.timeout)
            returned_0_0 = response_0.scenario.audit.created_by
            returned_0_0_part_0 = response.demand_forecasts.add()
            if returned_0_0:
                returned_0_0_part_0.audit.created_by = returned_0_0
            returned_1_0 = response_1.result.correlation_id
            if returned_1_0:
                response.result.correlation_id = returned_1_0
            returned_1_1 = response_1.result.reference_ids
            response.result.reference_ids.extend(returned_1_1)
            return response

    async def handle_summarize_demand_forecasts(
        self,
        request: forecasting_v1_demand_forecast_query_service_pb2.SummarizeDemandForecastsRequest
    ) -> forecasting_v1_demand_forecast_query_service_pb2.SummarizeDemandForecastsResponse:
        """Summarizes a demand forecast."""
        deps = self.deps
        response = forecasting_v1_demand_forecast_query_service_pb2.SummarizeDemandForecastsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SummarizeDemandForecasts', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'SummarizeDemandForecasts',
                {'reason': request.reason}
            )
            response_0 = notifications_v1_notification_query_service_pb2.FindNotificationsResponse()
            response_1 = ratelimiting_v1_rate_limit_query_service_pb2.SuggestRateLimitsResponse()
            fields_0: dict[str, Any] = {
                'context': request.context,
                'filter': {'labels': dict(request.details.filters), 'owner_id': request.demand_forecast_id}
            }
            outgoing_0 = notifications_v1_notification_query_service_pb2.FindNotificationsRequest(**fields_0)
            response_0 = await deps.clients.notifications_notification_query.FindNotifications(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = ratelimiting_v1_rate_limit_query_service_pb2.SuggestRateLimitsRequest(
                context=request.context,
                filter=ratelimiting_v1_rate_limit_query_service_pb2.SuggestRateLimitsRequest.Filter(
                    labels=dict(response_0.result.details)
                )
            )
            document_1 = MessageToDict(outgoing_1, preserving_proto_field_name=True)
            outgoing_1 = ParseDict(document_1, ratelimiting_v1_rate_limit_query_service_pb2.SuggestRateLimitsRequest())
            response_1 = await deps.clients.ratelimiting_rate_limit_query.SuggestRateLimits(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.result.message = returned_0_0
            returned_0_1 = response_0.result.status
            if returned_0_1:
                response.result.status = returned_0_1
            returned_1_0 = response_1.result.status
            if returned_1_0:
                response.result.status = returned_1_0
            returned_1_1 = response_1.result.message
            if returned_1_1:
                response.result.message = returned_1_1
            echoed_0 = request.details.period
            response.period.CopyFrom(echoed_0)
            return response
