"""Functional operations behind MetricSeriesService."""

from __future__ import annotations

import logging

from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.metrics.v1 import dashboard_admin_service_pb2 as metrics_v1_dashboard_admin_service_pb2
from acme.metrics.v1 import metric_alert_export_service_pb2 as metrics_v1_metric_alert_export_service_pb2
from acme.metrics.v1 import metric_series_export_service_pb2 as metrics_v1_metric_series_export_service_pb2
from acme.metrics.v1 import metric_series_service_pb2 as metrics_v1_metric_series_service_pb2
from acme.metrics.v1 import metrics_pb2 as metrics_v1_metrics_pb2
from acme.venues.v1 import venue_validation_service_pb2 as venues_v1_venue_validation_service_pb2

from acme_data.domains.metrics.dependencies import Dependencies
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


async def handle_batch_create_metric_serieses(
    deps: Dependencies,
    request: metrics_v1_metric_series_service_pb2.BatchCreateMetricSeriesesRequest
) -> metrics_v1_metric_series_service_pb2.BatchCreateMetricSeriesesResponse:
    """Takes a stream of metric serieses and answers once at the end."""
    response = metrics_v1_metric_series_service_pb2.BatchCreateMetricSeriesesResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('BatchCreateMetricSerieses', extra={'fields': {'sequence': request.sequence}})
        await deps.repository.audit(
            request.context.tenant_id,
            'BatchCreateMetricSerieses',
            {'sequence': request.sequence}
        )
        if request.WhichOneof('chunk') == 'record':
            await deps.repository.save_metric_series(request.context.tenant_id, request.record)
        response_0 = metrics_v1_dashboard_admin_service_pb2.RepairDashboardResponse()
        outgoing_0 = metrics_v1_dashboard_admin_service_pb2.RepairDashboardRequest(
            context=request.context,
            dashboard=metrics_v1_metrics_pb2.Dashboard(
                audit=common_v1_audit_pb2.AuditInfo(etag=request.record.audit.etag),
                billing_address=common_v1_address_pb2.PostalAddress(
                    lines=list(request.record.address.lines),
                    recipient=request.record.address.recipient
                )
            )
        )
        response_0 = await deps.clients.metrics_dashboard_admin.RepairDashboard(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.result.correlation_id
        if returned_0_0:
            response.result.correlation_id = returned_0_0
        return response


async def handle_clone_metric_series(
    deps: Dependencies,
    request: metrics_v1_metric_series_service_pb2.CloneMetricSeriesRequest
) -> metrics_v1_metric_series_service_pb2.CloneMetricSeriesResponse:
    """Creates a metric series."""
    response = metrics_v1_metric_series_service_pb2.CloneMetricSeriesResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('CloneMetricSeries', extra={'fields': {'request_id': request.request_id}})
        await deps.repository.audit(request.context.tenant_id, 'CloneMetricSeries', {'request_id': request.request_id})
        await deps.repository.save_metric_series(request.context.tenant_id, request.metric_series)
        response_0 = venues_v1_venue_validation_service_pb2.NormalizeVenueResponse()
        outgoing_0 = venues_v1_venue_validation_service_pb2.NormalizeVenueRequest()
        outgoing_0.context.CopyFrom(request.context)
        if request.metric_series.WhichOneof('locator') == 'address':
            outgoing_0.venue.address.region = request.metric_series.address.region
        outgoing_0.venue.dimensions.weight = request.metric_series.dimensions.weight
        if request.metric_series.WhichOneof('locator') == 'address':
            outgoing_0.venue.address.locality = request.metric_series.address.locality
        response_0 = await deps.clients.venues_venue_validation.NormalizeVenue(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.venue.dimensions.length
        if returned_0_0:
            response.metric_series.dimensions.length = returned_0_0
        returned_0_1 = response_0.venue.category_path
        response.metric_series.category_path.extend(returned_0_1)
        echoed_0 = request.metric_series.status
        response.metric_series.status = echoed_0
        echoed_1 = request.metric_series.name
        response.metric_series.name = echoed_1
        return response


async def handle_create_metric_series(
    deps: Dependencies,
    request: metrics_v1_metric_series_service_pb2.CreateMetricSeriesRequest
) -> metrics_v1_metric_series_service_pb2.CreateMetricSeriesResponse:
    """Creates a metric series."""
    response = metrics_v1_metric_series_service_pb2.CreateMetricSeriesResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('CreateMetricSeries', extra={'fields': {'request_id': request.request_id}})
        await deps.repository.audit(request.context.tenant_id, 'CreateMetricSeries', {'request_id': request.request_id})
        await deps.repository.save_metric_series(request.context.tenant_id, request.metric_series)
        echoed_0 = request.metric_series.code
        response.metric_series.code = echoed_0
        echoed_1 = request.metric_series.owner
        response.metric_series.owner.CopyFrom(echoed_1)
        return response


async def handle_delete_metric_series(
    deps: Dependencies,
    request: metrics_v1_metric_series_service_pb2.DeleteMetricSeriesRequest
) -> metrics_v1_metric_series_service_pb2.DeleteMetricSeriesResponse:
    """Deletes a metric series."""
    response = metrics_v1_metric_series_service_pb2.DeleteMetricSeriesResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('DeleteMetricSeries', extra={'fields': {'etag': request.etag}})
        await deps.repository.audit(request.context.tenant_id, 'DeleteMetricSeries', {'etag': request.etag})
        return response


async def handle_get_metric_series(
    deps: Dependencies,
    request: metrics_v1_metric_series_service_pb2.GetMetricSeriesRequest
) -> metrics_v1_metric_series_service_pb2.GetMetricSeriesResponse:
    """Returns a metric series."""
    response = metrics_v1_metric_series_service_pb2.GetMetricSeriesResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('GetMetricSeries', extra={'fields': {'domain': 'metrics'}})
        await deps.repository.audit(request.context.tenant_id, 'GetMetricSeries', {})
        response_0 = metrics_v1_metric_alert_export_service_pb2.ShareMetricAlertExportResponse()
        outgoing_0 = metrics_v1_metric_alert_export_service_pb2.ShareMetricAlertExportRequest(
            context=request.context,
            details=metrics_v1_metric_alert_export_service_pb2.ShareMetricAlertExportRequest.Details(
                recipient=common_v1_contact_pb2.ContactInfo(email=request.context.actor.email),
                variables=dict(request.context.baggage)
            )
        )
        response_0 = await deps.clients.metrics_metric_alert_export.ShareMetricAlertExport(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.metric_alert.audit.created_by
        if returned_0_0:
            response.metric_series.audit.created_by = returned_0_0
        echoed_0 = request.metric_series_id
        response.metric_series.metric_series_id = echoed_0
        return response


async def handle_list_metric_serieses(
    deps: Dependencies,
    request: metrics_v1_metric_series_service_pb2.ListMetricSeriesesRequest
) -> metrics_v1_metric_series_service_pb2.ListMetricSeriesesResponse:
    """Lists metric serieses a page at a time."""
    response = metrics_v1_metric_series_service_pb2.ListMetricSeriesesResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('ListMetricSerieses', extra={'fields': {'order_by': request.order_by}})
        await deps.repository.audit(request.context.tenant_id, 'ListMetricSerieses', {'order_by': request.order_by})
        return response


async def handle_search_metric_serieses(
    deps: Dependencies,
    request: metrics_v1_metric_series_service_pb2.SearchMetricSeriesesRequest
) -> metrics_v1_metric_series_service_pb2.SearchMetricSeriesesResponse:
    """Lists metric serieses a page at a time."""
    response = metrics_v1_metric_series_service_pb2.SearchMetricSeriesesResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('SearchMetricSerieses', extra={'fields': {'order_by': request.order_by}})
        await deps.repository.audit(request.context.tenant_id, 'SearchMetricSerieses', {'order_by': request.order_by})
        response_0 = metrics_v1_metric_series_export_service_pb2.RetryMetricSeriesExportResponse()
        outgoing_0 = metrics_v1_metric_series_export_service_pb2.RetryMetricSeriesExportRequest(
            context=request.context,
            details=metrics_v1_metric_series_export_service_pb2.RetryMetricSeriesExportRequest.Details(
                notify=common_v1_contact_pb2.ContactInfo(email=request.context.actor.email)
            ),
            metric_series=metrics_v1_metrics_pb2.MetricSeries(
                address=common_v1_address_pb2.PostalAddress(region=request.filter.region),
                owner=identity_v1_refs_pb2.UserRef(user_id=request.context.actor.user_id)
            )
        )
        response_0 = await deps.clients.metrics_metric_series_export.RetryMetricSeriesExport(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.metric_series.dimensions.unit
        returned_0_0_part_0 = response.metric_serieses.add()
        if returned_0_0:
            returned_0_0_part_0.dimensions.unit = returned_0_0
        returned_0_1 = response_0.metric_series.dimensions.width
        returned_0_1_part_0 = response.metric_serieses.add()
        if returned_0_1:
            returned_0_1_part_0.dimensions.width = returned_0_1
        return response


async def handle_update_metric_series(
    deps: Dependencies,
    request: metrics_v1_metric_series_service_pb2.UpdateMetricSeriesRequest
) -> metrics_v1_metric_series_service_pb2.UpdateMetricSeriesResponse:
    """Changes a metric series."""
    response = metrics_v1_metric_series_service_pb2.UpdateMetricSeriesResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('UpdateMetricSeries', extra={'fields': {'allow_missing': request.allow_missing}})
        await deps.repository.audit(
            request.context.tenant_id,
            'UpdateMetricSeries',
            {'allow_missing': request.allow_missing}
        )
        await deps.repository.save_metric_series(request.context.tenant_id, request.metric_series)
        echoed_0 = request.metric_series.capacity
        response.metric_series.capacity = echoed_0
        echoed_1 = request.metric_series.status
        response.metric_series.status = echoed_1
        return response


async def handle_watch_metric_serieses(
    deps: Dependencies,
    request: metrics_v1_metric_series_service_pb2.WatchMetricSeriesesRequest
) -> metrics_v1_metric_series_service_pb2.WatchMetricSeriesesResponse:
    """Streams the changes of metric serieses as they happen."""
    response = metrics_v1_metric_series_service_pb2.WatchMetricSeriesesResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('WatchMetricSerieses', extra={'fields': {'max_events': request.max_events}})
        await deps.repository.audit(
            request.context.tenant_id,
            'WatchMetricSerieses',
            {'max_events': request.max_events}
        )
        echoed_0 = request.subscriber.email
        response.metric_series.owner.email = echoed_0
        return response
