"""Functional operations behind MetricAlertExportService."""

from __future__ import annotations

import logging

from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.metrics.v1 import metric_alert_export_service_pb2 as metrics_v1_metric_alert_export_service_pb2
from acme.metrics.v1 import metric_series_export_service_pb2 as metrics_v1_metric_series_export_service_pb2
from acme.venues.v1 import venue_service_pb2 as venues_v1_venue_service_pb2
from acme.venues.v1 import venues_pb2 as venues_v1_venues_pb2

from acme_data.domains.metrics.dependencies import Dependencies
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


async def handle_get_metric_alert_export(
    deps: Dependencies,
    request: metrics_v1_metric_alert_export_service_pb2.GetMetricAlertExportRequest
) -> metrics_v1_metric_alert_export_service_pb2.GetMetricAlertExportResponse:
    """Returns a metric alert."""
    response = metrics_v1_metric_alert_export_service_pb2.GetMetricAlertExportResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('GetMetricAlertExport', extra={'fields': {'locale': request.context.locale}})
        await deps.repository.audit(
            request.context.tenant_id,
            'GetMetricAlertExport',
            {'locale': request.context.locale}
        )
        echoed_0 = request.metric_alert_id
        response.metric_alert.metric_alert_id = echoed_0
        return response


async def handle_list_metric_alert_exports(
    deps: Dependencies,
    request: metrics_v1_metric_alert_export_service_pb2.ListMetricAlertExportsRequest
) -> metrics_v1_metric_alert_export_service_pb2.ListMetricAlertExportsResponse:
    """Lists metric alerts a page at a time."""
    response = metrics_v1_metric_alert_export_service_pb2.ListMetricAlertExportsResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('ListMetricAlertExports', extra={'fields': {'order_by': request.order_by}})
        await deps.repository.audit(request.context.tenant_id, 'ListMetricAlertExports', {'order_by': request.order_by})
        return response


async def handle_retry_metric_alert_export(
    deps: Dependencies,
    request: metrics_v1_metric_alert_export_service_pb2.RetryMetricAlertExportRequest
) -> metrics_v1_metric_alert_export_service_pb2.RetryMetricAlertExportResponse:
    """Retrys a metric alert."""
    response = metrics_v1_metric_alert_export_service_pb2.RetryMetricAlertExportResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('RetryMetricAlertExport', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'RetryMetricAlertExport', {'reason': request.reason})
        await deps.repository.save_metric_alert(request.context.tenant_id, request.metric_alert)
        echoed_0 = request.metric_alert_id
        response.metric_alert.metric_alert_id = echoed_0
        echoed_1 = request.metric_alert.owner
        response.metric_alert.owner.CopyFrom(echoed_1)
        return response


async def handle_schedule_metric_alert_export(
    deps: Dependencies,
    request: metrics_v1_metric_alert_export_service_pb2.ScheduleMetricAlertExportRequest
) -> metrics_v1_metric_alert_export_service_pb2.ScheduleMetricAlertExportResponse:
    """Schedules a metric alert."""
    response = metrics_v1_metric_alert_export_service_pb2.ScheduleMetricAlertExportResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('ScheduleMetricAlertExport', extra={'fields': {'metric_alert_id': request.metric_alert_id}})
        await deps.repository.audit(
            request.context.tenant_id,
            'ScheduleMetricAlertExport',
            {'metric_alert_id': request.metric_alert_id}
        )
        echoed_0 = request.details.period
        response.period.CopyFrom(echoed_0)
        return response


async def handle_share_metric_alert_export(
    deps: Dependencies,
    request: metrics_v1_metric_alert_export_service_pb2.ShareMetricAlertExportRequest
) -> metrics_v1_metric_alert_export_service_pb2.ShareMetricAlertExportResponse:
    """Shares a metric alert."""
    response = metrics_v1_metric_alert_export_service_pb2.ShareMetricAlertExportResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('ShareMetricAlertExport', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'ShareMetricAlertExport', {'reason': request.reason})
        response_0 = metrics_v1_metric_series_export_service_pb2.RetryMetricSeriesExportResponse()
        outgoing_0 = metrics_v1_metric_series_export_service_pb2.RetryMetricSeriesExportRequest(
            context=request.context,
            details=metrics_v1_metric_series_export_service_pb2.RetryMetricSeriesExportRequest.Details(
                notify=common_v1_contact_pb2.ContactInfo(email=request.details.recipient.email)
            )
        )
        response_0 = await deps.clients.metrics_metric_series_export.RetryMetricSeriesExport(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.metric_series.owner
        if returned_0_0.ListFields():
            response.metric_alert.owner.MergeFrom(returned_0_0)
        echoed_0 = request.metric_alert_id
        response.metric_alert.metric_alert_id = echoed_0
        return response


async def handle_stream_metric_alert_export(
    deps: Dependencies,
    request: metrics_v1_metric_alert_export_service_pb2.StreamMetricAlertExportRequest
) -> metrics_v1_metric_alert_export_service_pb2.StreamMetricAlertExportResponse:
    """Streams every matching metric alert."""
    response = metrics_v1_metric_alert_export_service_pb2.StreamMetricAlertExportResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('StreamMetricAlertExport', extra={'fields': {'destination_uri': request.destination_uri}})
        await deps.repository.audit(
            request.context.tenant_id,
            'StreamMetricAlertExport',
            {'destination_uri': request.destination_uri}
        )
        response_0 = venues_v1_venue_service_pb2.CreateVenueResponse()
        outgoing_0 = venues_v1_venue_service_pb2.CreateVenueRequest(
            context=request.context,
            venue=venues_v1_venues_pb2.Venue(
                address=common_v1_address_pb2.PostalAddress(region=request.filter.region),
                audit=common_v1_audit_pb2.AuditInfo(updated_at=request.filter.created_after),
                owner=identity_v1_refs_pb2.UserRef(
                    email=request.context.actor.email,
                    user_id=request.context.actor.user_id
                )
            )
        )
        response_0 = await deps.clients.venues_venue.CreateVenue(outgoing_0, timeout=deps.settings.timeout)
        returned_0_0 = response_0.venue.audit.updated_by
        if returned_0_0:
            response.metric_alert.audit.updated_by = returned_0_0
        return response
