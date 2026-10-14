"""Application workflow for MetricSeries Query."""

from __future__ import annotations

import logging

from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.metrics.v1 import dashboard_history_service_pb2 as metrics_v1_dashboard_history_service_pb2
from acme.metrics.v1 import metric_series_query_service_pb2 as metrics_v1_metric_series_query_service_pb2
from acme.venues.v1 import venue_service_pb2 as venues_v1_venue_service_pb2
from acme.venues.v1 import venue_validation_service_pb2 as venues_v1_venue_validation_service_pb2
from acme.venues.v1 import venues_pb2 as venues_v1_venues_pb2

from acme_data.domains.metrics.dependencies import Dependencies
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class MetricSeriesQueryServicerWorkflow:
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    async def handle_browse_metric_serieses(
        self,
        request: metrics_v1_metric_series_query_service_pb2.BrowseMetricSeriesesRequest
    ) -> metrics_v1_metric_series_query_service_pb2.BrowseMetricSeriesesResponse:
        """Lists metric serieses a page at a time."""
        deps = self.deps
        response = metrics_v1_metric_series_query_service_pb2.BrowseMetricSeriesesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('BrowseMetricSerieses', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'BrowseMetricSerieses',
                {'order_by': request.order_by}
            )
            return response

    async def handle_count_metric_serieses(
        self,
        request: metrics_v1_metric_series_query_service_pb2.CountMetricSeriesesRequest
    ) -> metrics_v1_metric_series_query_service_pb2.CountMetricSeriesesResponse:
        """Counts metric serieses by status."""
        deps = self.deps
        response = metrics_v1_metric_series_query_service_pb2.CountMetricSeriesesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CountMetricSerieses', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'CountMetricSerieses',
                {'order_by': request.order_by}
            )
            response_0 = metrics_v1_dashboard_history_service_pb2.ListDashboardVersionsResponse()
            outgoing_0 = metrics_v1_dashboard_history_service_pb2.ListDashboardVersionsRequest(
                context=request.context,
                filter=metrics_v1_dashboard_history_service_pb2.ListDashboardVersionsRequest.Filter(
                    created_after=request.filter.created_after
                )
            )
            response_0 = await deps.clients.metrics_dashboard_history.ListDashboardVersions(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.result.message = returned_0_0
            return response

    async def handle_lookup_metric_series(
        self,
        request: metrics_v1_metric_series_query_service_pb2.LookupMetricSeriesRequest
    ) -> metrics_v1_metric_series_query_service_pb2.LookupMetricSeriesResponse:
        """Returns a metric series."""
        deps = self.deps
        response = metrics_v1_metric_series_query_service_pb2.LookupMetricSeriesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('LookupMetricSeries', extra={'fields': {'locale': request.context.locale}})
            await deps.repository.audit(
                request.context.tenant_id,
                'LookupMetricSeries',
                {'locale': request.context.locale}
            )
            echoed_0 = request.metric_series_id
            response.metric_series.metric_series_id = echoed_0
            return response

    async def handle_peek_metric_series(
        self,
        request: metrics_v1_metric_series_query_service_pb2.PeekMetricSeriesRequest
    ) -> metrics_v1_metric_series_query_service_pb2.PeekMetricSeriesResponse:
        """Returns a metric series."""
        deps = self.deps
        response = metrics_v1_metric_series_query_service_pb2.PeekMetricSeriesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('PeekMetricSeries', extra={'fields': {'domain': 'metrics'}})
            await deps.repository.audit(request.context.tenant_id, 'PeekMetricSeries', {})
            response_0 = venues_v1_venue_service_pb2.CloneVenueResponse()
            outgoing_0 = venues_v1_venue_service_pb2.CloneVenueRequest(
                context=request.context,
                venue=venues_v1_venues_pb2.Venue(
                    owner=identity_v1_refs_pb2.UserRef(
                        email=request.context.actor.email,
                        user_id=request.context.actor.user_id
                    )
                )
            )
            response_0 = await deps.clients.venues_venue.CloneVenue(outgoing_0, timeout=deps.settings.timeout)
            returned_0_0 = response_0.venue.components.get('primary', venues_v1_venues_pb2.VenueComponent()).description
            if returned_0_0:
                response.metric_series.components['primary'].description = returned_0_0
            echoed_0 = request.metric_series_id
            response.metric_series.metric_series_id = echoed_0
            return response

    async def handle_suggest_metric_serieses(
        self,
        request: metrics_v1_metric_series_query_service_pb2.SuggestMetricSeriesesRequest
    ) -> metrics_v1_metric_series_query_service_pb2.SuggestMetricSeriesesResponse:
        """Lists metric serieses a page at a time."""
        deps = self.deps
        response = metrics_v1_metric_series_query_service_pb2.SuggestMetricSeriesesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SuggestMetricSerieses', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'SuggestMetricSerieses',
                {'order_by': request.order_by}
            )
            response_0 = venues_v1_venue_validation_service_pb2.CheckVenueEligibilityResponse()
            outgoing_0 = venues_v1_venue_validation_service_pb2.CheckVenueEligibilityRequest(
                context=request.context,
                details=venues_v1_venue_validation_service_pb2.CheckVenueEligibilityRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(email=request.context.actor.email)
                )
            )
            response_0 = await deps.clients.venues_venue_validation.CheckVenueEligibility(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.venue.owner.display_name
            returned_0_0_part_0 = response.metric_serieses.add()
            if returned_0_0:
                returned_0_0_part_0.owner.display_name = returned_0_0
            return response

    async def handle_summarize_metric_serieses(
        self,
        request: metrics_v1_metric_series_query_service_pb2.SummarizeMetricSeriesesRequest
    ) -> metrics_v1_metric_series_query_service_pb2.SummarizeMetricSeriesesResponse:
        """Summarizes a metric series."""
        deps = self.deps
        response = metrics_v1_metric_series_query_service_pb2.SummarizeMetricSeriesesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SummarizeMetricSerieses', extra={'fields': {'metric_series_id': request.metric_series_id}})
            await deps.repository.audit(
                request.context.tenant_id,
                'SummarizeMetricSerieses',
                {'metric_series_id': request.metric_series_id}
            )
            response_0 = venues_v1_venue_validation_service_pb2.LintVenuesResponse()
            outgoing_0 = venues_v1_venue_validation_service_pb2.LintVenuesRequest()
            outgoing_0.context.CopyFrom(request.context)
            outgoing_0.annotations.update(dict(request.annotations))
            merged_0 = venues_v1_venue_validation_service_pb2.LintVenuesRequest()
            merged_0.MergeFrom(outgoing_0)
            outgoing_0.CopyFrom(merged_0)
            response_0 = await deps.clients.venues_venue_validation.LintVenues(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_0)
            echoed_0 = request.details.period
            response.period.CopyFrom(echoed_0)
            return response
