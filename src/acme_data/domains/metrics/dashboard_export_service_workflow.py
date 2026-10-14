"""Application workflow for Dashboard Export."""

from __future__ import annotations

import logging

from acme.metrics.v1 import dashboard_export_service_pb2 as metrics_v1_dashboard_export_service_pb2
from acme.metrics.v1 import metric_alert_export_service_pb2 as metrics_v1_metric_alert_export_service_pb2

from acme_data.domains.metrics.dependencies import Dependencies
from acme_data.platform.rpc import async_messages
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class DashboardExportServicerWorkflow:
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    async def handle_cancel_dashboard_export(
        self,
        request: metrics_v1_dashboard_export_service_pb2.CancelDashboardExportRequest
    ) -> metrics_v1_dashboard_export_service_pb2.CancelDashboardExportResponse:
        """Cancels a dashboard."""
        deps = self.deps
        response = metrics_v1_dashboard_export_service_pb2.CancelDashboardExportResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CancelDashboardExport', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'CancelDashboardExport', {'reason': request.reason})
            echoed_0 = request.dashboard_id
            response.dashboard.dashboard_id = echoed_0
            echoed_1 = request.details.effective_at
            response.outcome.effective_at.CopyFrom(echoed_1)
            return response

    async def handle_get_dashboard_export(
        self,
        request: metrics_v1_dashboard_export_service_pb2.GetDashboardExportRequest
    ) -> metrics_v1_dashboard_export_service_pb2.GetDashboardExportResponse:
        """Returns a dashboard."""
        deps = self.deps
        response = metrics_v1_dashboard_export_service_pb2.GetDashboardExportResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('GetDashboardExport', extra={'fields': {'locale': request.context.locale}})
            await deps.repository.audit(
                request.context.tenant_id,
                'GetDashboardExport',
                {'locale': request.context.locale}
            )
            echoed_0 = request.dashboard_id
            response.dashboard.dashboard_id = echoed_0
            return response

    async def handle_retry_dashboard_export(
        self,
        request: metrics_v1_dashboard_export_service_pb2.RetryDashboardExportRequest
    ) -> metrics_v1_dashboard_export_service_pb2.RetryDashboardExportResponse:
        """Retrys a dashboard."""
        deps = self.deps
        response = metrics_v1_dashboard_export_service_pb2.RetryDashboardExportResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('RetryDashboardExport', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'RetryDashboardExport', {'reason': request.reason})
            await deps.repository.save_dashboard(request.context.tenant_id, request.dashboard)
            echoed_0 = request.dashboard_id
            response.dashboard.dashboard_id = echoed_0
            echoed_1 = request.dashboard.total
            response.dashboard.total.CopyFrom(echoed_1)
            return response

    async def handle_schedule_dashboard_export(
        self,
        request: metrics_v1_dashboard_export_service_pb2.ScheduleDashboardExportRequest
    ) -> metrics_v1_dashboard_export_service_pb2.ScheduleDashboardExportResponse:
        """Schedules a dashboard."""
        deps = self.deps
        response = metrics_v1_dashboard_export_service_pb2.ScheduleDashboardExportResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ScheduleDashboardExport', extra={'fields': {'dashboard_id': request.dashboard_id}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ScheduleDashboardExport',
                {'dashboard_id': request.dashboard_id}
            )
            echoed_0 = request.details.period
            response.period.CopyFrom(echoed_0)
            return response

    async def handle_share_dashboard_export(
        self,
        request: metrics_v1_dashboard_export_service_pb2.ShareDashboardExportRequest
    ) -> metrics_v1_dashboard_export_service_pb2.ShareDashboardExportResponse:
        """Shares a dashboard."""
        deps = self.deps
        response = metrics_v1_dashboard_export_service_pb2.ShareDashboardExportResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ShareDashboardExport', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'ShareDashboardExport', {'reason': request.reason})
            echoed_0 = request.dashboard_id
            response.dashboard.dashboard_id = echoed_0
            return response

    async def handle_stream_dashboard_export(
        self,
        request: metrics_v1_dashboard_export_service_pb2.StreamDashboardExportRequest
    ) -> metrics_v1_dashboard_export_service_pb2.StreamDashboardExportResponse:
        """Streams every matching dashboard."""
        deps = self.deps
        response = metrics_v1_dashboard_export_service_pb2.StreamDashboardExportResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('StreamDashboardExport', extra={'fields': {'destination_uri': request.destination_uri}})
            await deps.repository.audit(
                request.context.tenant_id,
                'StreamDashboardExport',
                {'destination_uri': request.destination_uri}
            )
            response_0 = metrics_v1_metric_alert_export_service_pb2.StreamMetricAlertExportResponse()
            outgoing_0 = metrics_v1_metric_alert_export_service_pb2.StreamMetricAlertExportRequest(
                context=request.context,
                filter=metrics_v1_metric_alert_export_service_pb2.StreamMetricAlertExportRequest.Filter(
                    created_after=request.filter.created_after,
                    owner_id=request.filter.owner_id,
                    query=request.filter.query,
                    region=request.filter.region
                )
            )
            async for chunk_0 in deps.clients.metrics_metric_alert_export.StreamMetricAlertExport(
                outgoing_0,
                timeout=deps.settings.timeout
            ):
                response_0 = chunk_0
            echoed_0 = request.filter.region
            response.dashboard.billing_address.region = echoed_0
            return response
