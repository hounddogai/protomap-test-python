"""Answers read-only questions about metric alerts, for screens and reports."""

from __future__ import annotations

from collections.abc import AsyncIterator
import logging

import grpc

from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.metrics.v1 import dashboard_export_service_pb2 as metrics_v1_dashboard_export_service_pb2
from acme.metrics.v1 import metric_alert_query_service_pb2 as metrics_v1_metric_alert_query_service_pb2
from acme.metrics.v1 import metric_alert_query_service_pb2_grpc as metrics_v1_metric_alert_query_service_pb2_grpc
from acme.metrics.v1 import metrics_pb2 as metrics_v1_metrics_pb2
from acme.metrics.v1 import refs_pb2 as metrics_v1_refs_pb2

from acme_data.domains.metrics.dependencies import Dependencies
from acme_data.platform.rpc import messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class MetricAlertQueryServicer(metrics_v1_metric_alert_query_service_pb2_grpc.MetricAlertQueryServiceServicer):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    @retry_transient
    async def BrowseMetricAlerts(
        self, request: metrics_v1_metric_alert_query_service_pb2.BrowseMetricAlertsRequest, context: grpc.aio.ServicerContext,
    ) -> metrics_v1_metric_alert_query_service_pb2.BrowseMetricAlertsResponse:
        """Lists metric alerts a page at a time."""
        return await self.handle_browse_metric_alerts(request)

    @rpc_errors
    @retry_transient
    async def CountMetricAlerts(
        self, request: metrics_v1_metric_alert_query_service_pb2.CountMetricAlertsRequest, context: grpc.aio.ServicerContext,
    ) -> metrics_v1_metric_alert_query_service_pb2.CountMetricAlertsResponse:
        """Counts metric alerts by status."""
        return await self.handle_count_metric_alerts(request)

    @stream_errors
    async def ExportMetricAlerts(
        self, request: metrics_v1_metric_alert_query_service_pb2.ExportMetricAlertsRequest, context: grpc.aio.ServicerContext,
    ) -> AsyncIterator[metrics_v1_metric_alert_query_service_pb2.ExportMetricAlertsResponse]:
        """Streams every matching metric alert."""
        response = await self.handle_export_metric_alerts(request)
        for item in messages((response,)):
            yield item

    @rpc_errors
    @retry_transient
    async def FindMetricAlerts(
        self, request: metrics_v1_metric_alert_query_service_pb2.FindMetricAlertsRequest, context: grpc.aio.ServicerContext,
    ) -> metrics_v1_metric_alert_query_service_pb2.FindMetricAlertsResponse:
        """Lists metric alerts a page at a time."""
        return await self.handle_find_metric_alerts(request)

    @rpc_errors
    @retry_transient
    async def LookupMetricAlert(
        self, request: metrics_v1_metric_alert_query_service_pb2.LookupMetricAlertRequest, context: grpc.aio.ServicerContext,
    ) -> metrics_v1_metric_alert_query_service_pb2.LookupMetricAlertResponse:
        """Returns a metric alert."""
        return await self.handle_lookup_metric_alert(request)

    @rpc_errors
    @retry_transient
    async def PeekMetricAlert(
        self, request: metrics_v1_metric_alert_query_service_pb2.PeekMetricAlertRequest, context: grpc.aio.ServicerContext,
    ) -> metrics_v1_metric_alert_query_service_pb2.PeekMetricAlertResponse:
        """Returns a metric alert."""
        return await self.handle_peek_metric_alert(request)

    @rpc_errors
    @retry_transient
    async def ResolveMetricAlerts(
        self, request: metrics_v1_metric_alert_query_service_pb2.ResolveMetricAlertsRequest, context: grpc.aio.ServicerContext,
    ) -> metrics_v1_metric_alert_query_service_pb2.ResolveMetricAlertsResponse:
        """Returns several metric alerts at once."""
        return await self.handle_resolve_metric_alerts(request)

    @rpc_errors
    @retry_transient
    async def SuggestMetricAlerts(
        self, request: metrics_v1_metric_alert_query_service_pb2.SuggestMetricAlertsRequest, context: grpc.aio.ServicerContext,
    ) -> metrics_v1_metric_alert_query_service_pb2.SuggestMetricAlertsResponse:
        """Lists metric alerts a page at a time."""
        return await self.handle_suggest_metric_alerts(request)

    @rpc_errors
    async def SummarizeMetricAlerts(
        self, request: metrics_v1_metric_alert_query_service_pb2.SummarizeMetricAlertsRequest, context: grpc.aio.ServicerContext,
    ) -> metrics_v1_metric_alert_query_service_pb2.SummarizeMetricAlertsResponse:
        """Summarizes a metric alert."""
        return await self.handle_summarize_metric_alerts(request)

    async def handle_browse_metric_alerts(
        self,
        request: metrics_v1_metric_alert_query_service_pb2.BrowseMetricAlertsRequest
    ) -> metrics_v1_metric_alert_query_service_pb2.BrowseMetricAlertsResponse:
        """Lists metric alerts a page at a time."""
        deps = self.deps
        response = metrics_v1_metric_alert_query_service_pb2.BrowseMetricAlertsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('BrowseMetricAlerts', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(request.context.tenant_id, 'BrowseMetricAlerts', {'order_by': request.order_by})
            return response

    async def handle_count_metric_alerts(
        self,
        request: metrics_v1_metric_alert_query_service_pb2.CountMetricAlertsRequest
    ) -> metrics_v1_metric_alert_query_service_pb2.CountMetricAlertsResponse:
        """Counts metric alerts by status."""
        deps = self.deps
        response = metrics_v1_metric_alert_query_service_pb2.CountMetricAlertsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CountMetricAlerts', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(request.context.tenant_id, 'CountMetricAlerts', {'order_by': request.order_by})
            return response

    async def handle_export_metric_alerts(
        self,
        request: metrics_v1_metric_alert_query_service_pb2.ExportMetricAlertsRequest
    ) -> metrics_v1_metric_alert_query_service_pb2.ExportMetricAlertsResponse:
        """Streams every matching metric alert."""
        deps = self.deps
        response = metrics_v1_metric_alert_query_service_pb2.ExportMetricAlertsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ExportMetricAlerts', extra={'fields': {'destination_uri': request.destination_uri}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ExportMetricAlerts',
                {'destination_uri': request.destination_uri}
            )
            return response

    async def handle_find_metric_alerts(
        self,
        request: metrics_v1_metric_alert_query_service_pb2.FindMetricAlertsRequest
    ) -> metrics_v1_metric_alert_query_service_pb2.FindMetricAlertsResponse:
        """Lists metric alerts a page at a time."""
        deps = self.deps
        response = metrics_v1_metric_alert_query_service_pb2.FindMetricAlertsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('FindMetricAlerts', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(request.context.tenant_id, 'FindMetricAlerts', {'order_by': request.order_by})
            return response

    async def handle_lookup_metric_alert(
        self,
        request: metrics_v1_metric_alert_query_service_pb2.LookupMetricAlertRequest
    ) -> metrics_v1_metric_alert_query_service_pb2.LookupMetricAlertResponse:
        """Returns a metric alert."""
        deps = self.deps
        response = metrics_v1_metric_alert_query_service_pb2.LookupMetricAlertResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('LookupMetricAlert', extra={'fields': {'domain': 'metrics'}})
            await deps.repository.audit(request.context.tenant_id, 'LookupMetricAlert', {})
            response_0 = metrics_v1_dashboard_export_service_pb2.RetryDashboardExportResponse()
            outgoing_0 = metrics_v1_dashboard_export_service_pb2.RetryDashboardExportRequest(
                context=request.context,
                dashboard=metrics_v1_metrics_pb2.Dashboard(
                    audit=common_v1_audit_pb2.AuditInfo(created_at=request.context.deadline),
                    counterparty=metrics_v1_refs_pb2.MetricAlertRef(metric_alert_id=request.metric_alert_id),
                    lines=[metrics_v1_metrics_pb2.DashboardLine(attributes=dict(request.context.baggage))]
                ),
                details=metrics_v1_dashboard_export_service_pb2.RetryDashboardExportRequest.Details(
                    notify=common_v1_contact_pb2.ContactInfo(email=request.context.actor.email)
                )
            )
            response_0 = await deps.clients.metrics_dashboard_export.RetryDashboardExport(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.dashboard.counterparty.metric_alert_id
            if returned_0_0:
                response.metric_alert.metric_alert_id = returned_0_0
            returned_0_1 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_1)
            return response

    async def handle_peek_metric_alert(
        self,
        request: metrics_v1_metric_alert_query_service_pb2.PeekMetricAlertRequest
    ) -> metrics_v1_metric_alert_query_service_pb2.PeekMetricAlertResponse:
        """Returns a metric alert."""
        deps = self.deps
        response = metrics_v1_metric_alert_query_service_pb2.PeekMetricAlertResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('PeekMetricAlert', extra={'fields': {'domain': 'metrics'}})
            await deps.repository.audit(request.context.tenant_id, 'PeekMetricAlert', {})
            response_0 = metrics_v1_dashboard_export_service_pb2.ShareDashboardExportResponse()
            outgoing_0 = metrics_v1_dashboard_export_service_pb2.ShareDashboardExportRequest(
                context=request.context,
                details=metrics_v1_dashboard_export_service_pb2.ShareDashboardExportRequest.Details(
                    recipient=common_v1_contact_pb2.ContactInfo(email=request.context.actor.email),
                    variables=dict(request.context.baggage)
                )
            )
            response_0 = await deps.clients.metrics_dashboard_export.ShareDashboardExport(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_0)
            echoed_0 = request.metric_alert_id
            response.metric_alert.metric_alert_id = echoed_0
            return response

    async def handle_resolve_metric_alerts(
        self,
        request: metrics_v1_metric_alert_query_service_pb2.ResolveMetricAlertsRequest
    ) -> metrics_v1_metric_alert_query_service_pb2.ResolveMetricAlertsResponse:
        """Returns several metric alerts at once."""
        deps = self.deps
        response = metrics_v1_metric_alert_query_service_pb2.ResolveMetricAlertsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ResolveMetricAlerts', extra={'fields': {'locale': request.context.locale}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ResolveMetricAlerts',
                {'locale': request.context.locale}
            )
            return response

    async def handle_suggest_metric_alerts(
        self,
        request: metrics_v1_metric_alert_query_service_pb2.SuggestMetricAlertsRequest
    ) -> metrics_v1_metric_alert_query_service_pb2.SuggestMetricAlertsResponse:
        """Lists metric alerts a page at a time."""
        deps = self.deps
        response = metrics_v1_metric_alert_query_service_pb2.SuggestMetricAlertsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SuggestMetricAlerts', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'SuggestMetricAlerts',
                {'order_by': request.order_by}
            )
            return response

    async def handle_summarize_metric_alerts(
        self,
        request: metrics_v1_metric_alert_query_service_pb2.SummarizeMetricAlertsRequest
    ) -> metrics_v1_metric_alert_query_service_pb2.SummarizeMetricAlertsResponse:
        """Summarizes a metric alert."""
        deps = self.deps
        response = metrics_v1_metric_alert_query_service_pb2.SummarizeMetricAlertsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SummarizeMetricAlerts', extra={'fields': {'metric_alert_id': request.metric_alert_id}})
            await deps.repository.audit(
                request.context.tenant_id,
                'SummarizeMetricAlerts',
                {'metric_alert_id': request.metric_alert_id}
            )
            echoed_0 = request.details.period
            response.period.CopyFrom(echoed_0)
            return response
