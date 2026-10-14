"""Functional operations behind MetricSeriesAdminService."""

from __future__ import annotations

import logging

from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.metrics.v1 import metric_alert_export_service_pb2 as metrics_v1_metric_alert_export_service_pb2
from acme.metrics.v1 import metric_series_admin_service_pb2 as metrics_v1_metric_series_admin_service_pb2
from acme.metrics.v1 import metrics_pb2 as metrics_v1_metrics_pb2
from acme.venues.v1 import venue_query_service_pb2 as venues_v1_venue_query_service_pb2

from acme_data.domains.metrics.dependencies import Dependencies
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


async def handle_archive_metric_series(
    deps: Dependencies,
    request: metrics_v1_metric_series_admin_service_pb2.ArchiveMetricSeriesRequest
) -> metrics_v1_metric_series_admin_service_pb2.ArchiveMetricSeriesResponse:
    """Archives a metric series."""
    response = metrics_v1_metric_series_admin_service_pb2.ArchiveMetricSeriesResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('ArchiveMetricSeries', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'ArchiveMetricSeries', {'reason': request.reason})
        response_0 = venues_v1_venue_query_service_pb2.SuggestVenuesResponse()
        outgoing_0 = venues_v1_venue_query_service_pb2.SuggestVenuesRequest(
            context=request.context,
            filter=venues_v1_venue_query_service_pb2.SuggestVenuesRequest.Filter(
                created_after=request.details.effective_at,
                labels=dict(request.annotations),
                owner_id=request.details.new_owner.user_id
            )
        )
        response_0 = await deps.clients.venues_venue_query.SuggestVenues(outgoing_0, timeout=deps.settings.timeout)
        returned_0_0 = response_0.result.status
        if returned_0_0:
            response.outcome.status = returned_0_0
        echoed_0 = request.metric_series_id
        response.metric_series.metric_series_id = echoed_0
        echoed_1 = request.details.effective_at
        response.outcome.effective_at.CopyFrom(echoed_1)
        return response


async def handle_inspect_metric_series(
    deps: Dependencies,
    request: metrics_v1_metric_series_admin_service_pb2.InspectMetricSeriesRequest
) -> metrics_v1_metric_series_admin_service_pb2.InspectMetricSeriesResponse:
    """Returns a metric series."""
    response = metrics_v1_metric_series_admin_service_pb2.InspectMetricSeriesResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('InspectMetricSeries', extra={'fields': {'locale': request.context.locale}})
        await deps.repository.audit(
            request.context.tenant_id,
            'InspectMetricSeries',
            {'locale': request.context.locale}
        )
        echoed_0 = request.metric_series_id
        response.metric_series.metric_series_id = echoed_0
        return response


async def handle_lock_metric_series(
    deps: Dependencies,
    request: metrics_v1_metric_series_admin_service_pb2.LockMetricSeriesRequest
) -> metrics_v1_metric_series_admin_service_pb2.LockMetricSeriesResponse:
    """Locks a metric series."""
    response = metrics_v1_metric_series_admin_service_pb2.LockMetricSeriesResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('LockMetricSeries', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'LockMetricSeries', {'reason': request.reason})
        echoed_0 = request.metric_series_id
        response.metric_series.metric_series_id = echoed_0
        echoed_1 = request.details.effective_at
        response.outcome.effective_at.CopyFrom(echoed_1)
        return response


async def handle_purge_metric_series(
    deps: Dependencies,
    request: metrics_v1_metric_series_admin_service_pb2.PurgeMetricSeriesRequest
) -> metrics_v1_metric_series_admin_service_pb2.PurgeMetricSeriesResponse:
    """Deletes a metric series."""
    response = metrics_v1_metric_series_admin_service_pb2.PurgeMetricSeriesResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('PurgeMetricSeries', extra={'fields': {'etag': request.etag}})
        await deps.repository.audit(request.context.tenant_id, 'PurgeMetricSeries', {'etag': request.etag})
        return response


async def handle_reassign_metric_series(
    deps: Dependencies,
    request: metrics_v1_metric_series_admin_service_pb2.ReassignMetricSeriesRequest
) -> metrics_v1_metric_series_admin_service_pb2.ReassignMetricSeriesResponse:
    """Reassigns a metric series."""
    response = metrics_v1_metric_series_admin_service_pb2.ReassignMetricSeriesResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('ReassignMetricSeries', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'ReassignMetricSeries', {'reason': request.reason})
        echoed_0 = request.metric_series_id
        response.metric_series.metric_series_id = echoed_0
        echoed_1 = request.details.capacity
        response.metric_series.capacity = echoed_1
        return response


async def handle_repair_metric_series(
    deps: Dependencies,
    request: metrics_v1_metric_series_admin_service_pb2.RepairMetricSeriesRequest
) -> metrics_v1_metric_series_admin_service_pb2.RepairMetricSeriesResponse:
    """Repairs a metric series."""
    response = metrics_v1_metric_series_admin_service_pb2.RepairMetricSeriesResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('RepairMetricSeries', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'RepairMetricSeries', {'reason': request.reason})
        await deps.repository.save_metric_series(request.context.tenant_id, request.metric_series)
        response_0 = metrics_v1_metric_alert_export_service_pb2.RetryMetricAlertExportResponse()
        outgoing_0 = metrics_v1_metric_alert_export_service_pb2.RetryMetricAlertExportRequest(
            context=request.context,
            metric_alert=metrics_v1_metrics_pb2.MetricAlert(
                audit=common_v1_audit_pb2.AuditInfo(updated_at=request.metric_series.audit.updated_at)
            )
        )
        response_0 = await deps.clients.metrics_metric_alert_export.RetryMetricAlertExport(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.outcome.next_steps
        response.outcome.next_steps.extend(returned_0_0)
        echoed_0 = request.metric_series_id
        response.metric_series.metric_series_id = echoed_0
        echoed_1 = request.metric_series.status
        response.metric_series.status = echoed_1
        return response


async def handle_restore_metric_series(
    deps: Dependencies,
    request: metrics_v1_metric_series_admin_service_pb2.RestoreMetricSeriesRequest
) -> metrics_v1_metric_series_admin_service_pb2.RestoreMetricSeriesResponse:
    """Restores a metric series."""
    response = metrics_v1_metric_series_admin_service_pb2.RestoreMetricSeriesResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('RestoreMetricSeries', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'RestoreMetricSeries', {'reason': request.reason})
        echoed_0 = request.metric_series_id
        response.metric_series.metric_series_id = echoed_0
        echoed_1 = request.details.effective_at
        response.outcome.effective_at.CopyFrom(echoed_1)
        return response


async def handle_unlock_metric_series(
    deps: Dependencies,
    request: metrics_v1_metric_series_admin_service_pb2.UnlockMetricSeriesRequest
) -> metrics_v1_metric_series_admin_service_pb2.UnlockMetricSeriesResponse:
    """Unlocks a metric series."""
    response = metrics_v1_metric_series_admin_service_pb2.UnlockMetricSeriesResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('UnlockMetricSeries', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'UnlockMetricSeries', {'reason': request.reason})
        echoed_0 = request.metric_series_id
        response.metric_series.metric_series_id = echoed_0
        echoed_1 = request.details.effective_at
        response.outcome.effective_at.CopyFrom(echoed_1)
        return response
