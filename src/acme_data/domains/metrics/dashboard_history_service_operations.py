"""Functional operations behind DashboardHistoryService."""

from __future__ import annotations

import logging

from acme.metrics.v1 import dashboard_history_service_pb2 as metrics_v1_dashboard_history_service_pb2

from acme_data.domains.metrics.dependencies import Dependencies
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


async def handle_annotate_dashboard_version(
    deps: Dependencies,
    request: metrics_v1_dashboard_history_service_pb2.AnnotateDashboardVersionRequest
) -> metrics_v1_dashboard_history_service_pb2.AnnotateDashboardVersionResponse:
    """Annotates a dashboard."""
    response = metrics_v1_dashboard_history_service_pb2.AnnotateDashboardVersionResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('AnnotateDashboardVersion', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'AnnotateDashboardVersion', {'reason': request.reason})
        await deps.repository.save_dashboard(request.context.tenant_id, request.dashboard)
        echoed_0 = request.dashboard_id
        response.dashboard.dashboard_id = echoed_0
        echoed_1 = request.dashboard.notes
        response.dashboard.notes = echoed_1
        return response


async def handle_compare_dashboard_versions(
    deps: Dependencies,
    request: metrics_v1_dashboard_history_service_pb2.CompareDashboardVersionsRequest
) -> metrics_v1_dashboard_history_service_pb2.CompareDashboardVersionsResponse:
    """Compares a dashboard."""
    response = metrics_v1_dashboard_history_service_pb2.CompareDashboardVersionsResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('CompareDashboardVersions', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'CompareDashboardVersions', {'reason': request.reason})
        await deps.repository.save_dashboard(request.context.tenant_id, request.dashboard)
        echoed_0 = request.dashboard_id
        response.dashboard.dashboard_id = echoed_0
        echoed_1 = request.dashboard.due_at
        response.dashboard.due_at.CopyFrom(echoed_1)
        return response


async def handle_get_dashboard_version(
    deps: Dependencies,
    request: metrics_v1_dashboard_history_service_pb2.GetDashboardVersionRequest
) -> metrics_v1_dashboard_history_service_pb2.GetDashboardVersionResponse:
    """Returns a dashboard."""
    response = metrics_v1_dashboard_history_service_pb2.GetDashboardVersionResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('GetDashboardVersion', extra={'fields': {'locale': request.context.locale}})
        await deps.repository.audit(
            request.context.tenant_id,
            'GetDashboardVersion',
            {'locale': request.context.locale}
        )
        echoed_0 = request.dashboard_id
        response.dashboard.dashboard_id = echoed_0
        return response


async def handle_list_dashboard_versions(
    deps: Dependencies,
    request: metrics_v1_dashboard_history_service_pb2.ListDashboardVersionsRequest
) -> metrics_v1_dashboard_history_service_pb2.ListDashboardVersionsResponse:
    """Lists dashboards a page at a time."""
    response = metrics_v1_dashboard_history_service_pb2.ListDashboardVersionsResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('ListDashboardVersions', extra={'fields': {'order_by': request.order_by}})
        await deps.repository.audit(request.context.tenant_id, 'ListDashboardVersions', {'order_by': request.order_by})
        return response


async def handle_prune_dashboard_versions(
    deps: Dependencies,
    request: metrics_v1_dashboard_history_service_pb2.PruneDashboardVersionsRequest
) -> metrics_v1_dashboard_history_service_pb2.PruneDashboardVersionsResponse:
    """Deletes a dashboard."""
    response = metrics_v1_dashboard_history_service_pb2.PruneDashboardVersionsResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('PruneDashboardVersions', extra={'fields': {'dashboard_id': request.dashboard_id}})
        await deps.repository.audit(
            request.context.tenant_id,
            'PruneDashboardVersions',
            {'dashboard_id': request.dashboard_id}
        )
        return response


async def handle_record_dashboard_version(
    deps: Dependencies,
    request: metrics_v1_dashboard_history_service_pb2.RecordDashboardVersionRequest
) -> metrics_v1_dashboard_history_service_pb2.RecordDashboardVersionResponse:
    """Records a dashboard."""
    response = metrics_v1_dashboard_history_service_pb2.RecordDashboardVersionResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('RecordDashboardVersion', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'RecordDashboardVersion', {'reason': request.reason})
        await deps.repository.save_dashboard(request.context.tenant_id, request.dashboard)
        echoed_0 = request.dashboard_id
        response.dashboard.dashboard_id = echoed_0
        echoed_1 = request.dashboard.total
        response.dashboard.total.CopyFrom(echoed_1)
        return response


async def handle_revert_dashboard(
    deps: Dependencies,
    request: metrics_v1_dashboard_history_service_pb2.RevertDashboardRequest
) -> metrics_v1_dashboard_history_service_pb2.RevertDashboardResponse:
    """Reverts a dashboard."""
    response = metrics_v1_dashboard_history_service_pb2.RevertDashboardResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('RevertDashboard', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'RevertDashboard', {'reason': request.reason})
        await deps.repository.save_dashboard(request.context.tenant_id, request.dashboard)
        echoed_0 = request.dashboard_id
        response.dashboard.dashboard_id = echoed_0
        echoed_1 = request.dashboard.metadata
        response.dashboard.metadata.update(echoed_1)
        return response
