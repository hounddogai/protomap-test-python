"""Keeps dashboards in step with the systems of record in other regions."""

from __future__ import annotations

from collections.abc import AsyncIterator
from dataclasses import dataclass
import logging

import grpc

from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.metrics.v1 import dashboard_sync_service_pb2 as metrics_v1_dashboard_sync_service_pb2
from acme.metrics.v1 import dashboard_sync_service_pb2_grpc as metrics_v1_dashboard_sync_service_pb2_grpc
from acme.metrics.v1 import metric_series_export_service_pb2 as metrics_v1_metric_series_export_service_pb2
from acme.metrics.v1 import metrics_pb2 as metrics_v1_metrics_pb2

from acme_data.domains.metrics.dependencies import Dependencies
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


@dataclass(slots=True)
class DashboardSyncServicer(metrics_v1_dashboard_sync_service_pb2_grpc.DashboardSyncServiceServicer):
    deps: Dependencies

    @rpc_errors
    @retry_transient
    async def GetDashboardSyncState(
        self, request: metrics_v1_dashboard_sync_service_pb2.GetDashboardSyncStateRequest, context: grpc.aio.ServicerContext,
    ) -> metrics_v1_dashboard_sync_service_pb2.GetDashboardSyncStateResponse:
        """Returns a dashboard."""
        return await self.handle_get_dashboard_sync_state(request)

    @rpc_errors
    @retry_transient
    async def ListDashboardConflicts(
        self, request: metrics_v1_dashboard_sync_service_pb2.ListDashboardConflictsRequest, context: grpc.aio.ServicerContext,
    ) -> metrics_v1_dashboard_sync_service_pb2.ListDashboardConflictsResponse:
        """Lists dashboards a page at a time."""
        return await self.handle_list_dashboard_conflicts(request)

    @rpc_errors
    async def PullDashboards(
        self, request: metrics_v1_dashboard_sync_service_pb2.PullDashboardsRequest, context: grpc.aio.ServicerContext,
    ) -> metrics_v1_dashboard_sync_service_pb2.PullDashboardsResponse:
        """Pulls a dashboard."""
        return await self.handle_pull_dashboards(request)

    @rpc_errors
    async def PushDashboard(
        self, request: metrics_v1_dashboard_sync_service_pb2.PushDashboardRequest, context: grpc.aio.ServicerContext,
    ) -> metrics_v1_dashboard_sync_service_pb2.PushDashboardResponse:
        """Pushs a dashboard."""
        return await self.handle_push_dashboard(request)

    @rpc_errors
    async def ReconcileDashboards(
        self, request: metrics_v1_dashboard_sync_service_pb2.ReconcileDashboardsRequest, context: grpc.aio.ServicerContext,
    ) -> metrics_v1_dashboard_sync_service_pb2.ReconcileDashboardsResponse:
        """Reconciles a dashboard."""
        return await self.handle_reconcile_dashboards(request)

    @rpc_errors
    async def ResolveDashboardConflict(
        self, request: metrics_v1_dashboard_sync_service_pb2.ResolveDashboardConflictRequest, context: grpc.aio.ServicerContext,
    ) -> metrics_v1_dashboard_sync_service_pb2.ResolveDashboardConflictResponse:
        """Resolves a dashboard."""
        return await self.handle_resolve_dashboard_conflict(request)

    @stream_errors
    async def StreamDashboardChanges(
        self, requests: AsyncIterator[
            metrics_v1_dashboard_sync_service_pb2.StreamDashboardChangesRequest
        ], context: grpc.aio.ServicerContext,
    ) -> AsyncIterator[metrics_v1_dashboard_sync_service_pb2.StreamDashboardChangesResponse]:
        """Exchanges changes of dashboards with a peer."""
        async for request in requests:
            yield await self.handle_stream_dashboard_changes(request)

    @rpc_errors
    async def SyncDashboards(
        self, request: metrics_v1_dashboard_sync_service_pb2.SyncDashboardsRequest, context: grpc.aio.ServicerContext,
    ) -> metrics_v1_dashboard_sync_service_pb2.SyncDashboardsResponse:
        """Syncs a dashboard."""
        return await self.handle_sync_dashboards(request)

    async def handle_get_dashboard_sync_state(
        self,
        request: metrics_v1_dashboard_sync_service_pb2.GetDashboardSyncStateRequest
    ) -> metrics_v1_dashboard_sync_service_pb2.GetDashboardSyncStateResponse:
        """Returns a dashboard."""
        deps = self.deps
        response = metrics_v1_dashboard_sync_service_pb2.GetDashboardSyncStateResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('GetDashboardSyncState', extra={'fields': {'locale': request.context.locale}})
            await deps.repository.audit(
                request.context.tenant_id,
                'GetDashboardSyncState',
                {'locale': request.context.locale}
            )
            echoed_0 = request.dashboard_id
            response.dashboard.dashboard_id = echoed_0
            return response

    async def handle_list_dashboard_conflicts(
        self,
        request: metrics_v1_dashboard_sync_service_pb2.ListDashboardConflictsRequest
    ) -> metrics_v1_dashboard_sync_service_pb2.ListDashboardConflictsResponse:
        """Lists dashboards a page at a time."""
        deps = self.deps
        response = metrics_v1_dashboard_sync_service_pb2.ListDashboardConflictsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ListDashboardConflicts', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ListDashboardConflicts',
                {'order_by': request.order_by}
            )
            return response

    async def handle_pull_dashboards(
        self,
        request: metrics_v1_dashboard_sync_service_pb2.PullDashboardsRequest
    ) -> metrics_v1_dashboard_sync_service_pb2.PullDashboardsResponse:
        """Pulls a dashboard."""
        deps = self.deps
        response = metrics_v1_dashboard_sync_service_pb2.PullDashboardsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('PullDashboards', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'PullDashboards', {'reason': request.reason})
            await deps.repository.save_dashboard(request.context.tenant_id, request.dashboard)
            response_0 = metrics_v1_metric_series_export_service_pb2.RetryMetricSeriesExportResponse()
            outgoing_0 = metrics_v1_metric_series_export_service_pb2.RetryMetricSeriesExportRequest(
                context=request.context,
                metric_series=metrics_v1_metrics_pb2.MetricSeries(
                    address=common_v1_address_pb2.PostalAddress(lines=list(request.dashboard.billing_address.lines)),
                    audit=common_v1_audit_pb2.AuditInfo(
                        updated_at=request.dashboard.audit.updated_at,
                        updated_by=request.dashboard.audit.updated_by
                    ),
                    owner=identity_v1_refs_pb2.UserRef(display_name=request.dashboard.counterparty.display_name)
                )
            )
            method_name_0 = 'RetryMetricSeriesExport'
            response_0 = await getattr(
                deps.clients.metrics_metric_series_export,
                method_name_0
            )(outgoing_0, timeout=deps.settings.timeout)
            returned_0_0 = response_0.metric_series.address.postal_code
            if returned_0_0:
                response.dashboard.billing_address.postal_code = returned_0_0
            returned_0_1 = response_0.outcome.status
            if returned_0_1:
                response.outcome.status = returned_0_1
            echoed_0 = request.dashboard_id
            response.dashboard.dashboard_id = echoed_0
            echoed_1 = request.dashboard.notes
            response.dashboard.notes = echoed_1
            return response

    async def handle_push_dashboard(
        self,
        request: metrics_v1_dashboard_sync_service_pb2.PushDashboardRequest
    ) -> metrics_v1_dashboard_sync_service_pb2.PushDashboardResponse:
        """Pushs a dashboard."""
        deps = self.deps
        response = metrics_v1_dashboard_sync_service_pb2.PushDashboardResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('PushDashboard', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'PushDashboard', {'reason': request.reason})
            await deps.repository.save_dashboard(request.context.tenant_id, request.dashboard)
            echoed_0 = request.dashboard_id
            response.dashboard.dashboard_id = echoed_0
            echoed_1 = request.dashboard.billing_address
            response.dashboard.billing_address.CopyFrom(echoed_1)
            return response

    async def handle_reconcile_dashboards(
        self,
        request: metrics_v1_dashboard_sync_service_pb2.ReconcileDashboardsRequest
    ) -> metrics_v1_dashboard_sync_service_pb2.ReconcileDashboardsResponse:
        """Reconciles a dashboard."""
        deps = self.deps
        response = metrics_v1_dashboard_sync_service_pb2.ReconcileDashboardsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ReconcileDashboards', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'ReconcileDashboards', {'reason': request.reason})
            await deps.repository.save_dashboard(request.context.tenant_id, request.dashboard)
            echoed_0 = request.dashboard_id
            response.dashboard.dashboard_id = echoed_0
            echoed_1 = request.dashboard.metadata
            response.dashboard.metadata.update(echoed_1)
            return response

    async def handle_resolve_dashboard_conflict(
        self,
        request: metrics_v1_dashboard_sync_service_pb2.ResolveDashboardConflictRequest
    ) -> metrics_v1_dashboard_sync_service_pb2.ResolveDashboardConflictResponse:
        """Resolves a dashboard."""
        deps = self.deps
        response = metrics_v1_dashboard_sync_service_pb2.ResolveDashboardConflictResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ResolveDashboardConflict', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ResolveDashboardConflict',
                {'reason': request.reason}
            )
            await deps.repository.save_dashboard(request.context.tenant_id, request.dashboard)
            echoed_0 = request.dashboard_id
            response.dashboard.dashboard_id = echoed_0
            echoed_1 = request.dashboard.due_at
            response.dashboard.due_at.CopyFrom(echoed_1)
            return response

    async def handle_stream_dashboard_changes(
        self,
        request: metrics_v1_dashboard_sync_service_pb2.StreamDashboardChangesRequest
    ) -> metrics_v1_dashboard_sync_service_pb2.StreamDashboardChangesResponse:
        """Exchanges changes of dashboards with a peer."""
        deps = self.deps
        response = metrics_v1_dashboard_sync_service_pb2.StreamDashboardChangesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('StreamDashboardChanges', extra={'fields': {'cursor': request.cursor}})
            await deps.repository.audit(request.context.tenant_id, 'StreamDashboardChanges', {'cursor': request.cursor})
            if request.WhichOneof('frame') == 'change':
                await deps.repository.save_dashboard(request.context.tenant_id, request.change)
            echoed_0 = request.change.status
            response.dashboard.status = echoed_0
            echoed_1 = request.change.metadata
            response.dashboard.metadata.update(echoed_1)
            return response

    async def handle_sync_dashboards(
        self,
        request: metrics_v1_dashboard_sync_service_pb2.SyncDashboardsRequest
    ) -> metrics_v1_dashboard_sync_service_pb2.SyncDashboardsResponse:
        """Syncs a dashboard."""
        deps = self.deps
        response = metrics_v1_dashboard_sync_service_pb2.SyncDashboardsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SyncDashboards', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'SyncDashboards', {'reason': request.reason})
            await deps.repository.save_dashboard(request.context.tenant_id, request.dashboard)
            echoed_0 = request.dashboard_id
            response.dashboard.dashboard_id = echoed_0
            echoed_1 = request.dashboard.metadata
            response.dashboard.metadata.update(echoed_1)
            return response
