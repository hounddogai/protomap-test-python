"""Tells the people who follow a metric series what changed."""

from __future__ import annotations

from collections.abc import AsyncIterator
import logging

import grpc

from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.metrics.v1 import dashboard_export_service_pb2 as metrics_v1_dashboard_export_service_pb2
from acme.metrics.v1 import metric_series_notification_service_pb2 as metrics_v1_metric_series_notification_service_pb2
from acme.metrics.v1 import (
    metric_series_notification_service_pb2_grpc as metrics_v1_metric_series_notification_service_pb2_grpc,
)

from acme_data.domains.metrics.dependencies import Dependencies
from acme_data.platform.rpc import messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class MetricSeriesNotificationServicer(
    metrics_v1_metric_series_notification_service_pb2_grpc.MetricSeriesNotificationServiceServicer
):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    @retry_transient
    async def GetMetricSeriesPreferences(
        self, request: metrics_v1_metric_series_notification_service_pb2.GetMetricSeriesPreferencesRequest, context: grpc.aio.ServicerContext,
    ) -> metrics_v1_metric_series_notification_service_pb2.GetMetricSeriesPreferencesResponse:
        """Returns a metric series."""
        return await self.handle_get_metric_series_preferences(request)

    @rpc_errors
    async def NotifyMetricSeriesWatchers(
        self, request: metrics_v1_metric_series_notification_service_pb2.NotifyMetricSeriesWatchersRequest, context: grpc.aio.ServicerContext,
    ) -> metrics_v1_metric_series_notification_service_pb2.NotifyMetricSeriesWatchersResponse:
        """Notifys a metric series."""
        return await self.handle_notify_metric_series_watchers(request)

    @rpc_errors
    async def SendMetricSeriesTestNotice(
        self, request: metrics_v1_metric_series_notification_service_pb2.SendMetricSeriesTestNoticeRequest, context: grpc.aio.ServicerContext,
    ) -> metrics_v1_metric_series_notification_service_pb2.SendMetricSeriesTestNoticeResponse:
        """Sends a metric series."""
        return await self.handle_send_metric_series_test_notice(request)

    @stream_errors
    async def StreamMetricSeriesNotices(
        self, request: metrics_v1_metric_series_notification_service_pb2.StreamMetricSeriesNoticesRequest, context: grpc.aio.ServicerContext,
    ) -> AsyncIterator[metrics_v1_metric_series_notification_service_pb2.StreamMetricSeriesNoticesResponse]:
        """Streams the changes of metric serieses as they happen."""
        response = await self.handle_stream_metric_series_notices(request)
        for item in messages((response,)):
            yield item

    @rpc_errors
    async def SubscribeMetricSeriesUpdates(
        self, request: metrics_v1_metric_series_notification_service_pb2.SubscribeMetricSeriesUpdatesRequest, context: grpc.aio.ServicerContext,
    ) -> metrics_v1_metric_series_notification_service_pb2.SubscribeMetricSeriesUpdatesResponse:
        """Subscribes a metric series."""
        return await self.handle_subscribe_metric_series_updates(request)

    @rpc_errors
    async def UnsubscribeMetricSeriesUpdates(
        self, request: metrics_v1_metric_series_notification_service_pb2.UnsubscribeMetricSeriesUpdatesRequest, context: grpc.aio.ServicerContext,
    ) -> metrics_v1_metric_series_notification_service_pb2.UnsubscribeMetricSeriesUpdatesResponse:
        """Unsubscribes a metric series."""
        return await self.handle_unsubscribe_metric_series_updates(request)

    async def handle_get_metric_series_preferences(
        self,
        request: metrics_v1_metric_series_notification_service_pb2.GetMetricSeriesPreferencesRequest
    ) -> metrics_v1_metric_series_notification_service_pb2.GetMetricSeriesPreferencesResponse:
        """Returns a metric series."""
        deps = self.deps
        response = metrics_v1_metric_series_notification_service_pb2.GetMetricSeriesPreferencesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('GetMetricSeriesPreferences', extra={'fields': {'locale': request.context.locale}})
            await deps.repository.audit(
                request.context.tenant_id,
                'GetMetricSeriesPreferences',
                {'locale': request.context.locale}
            )
            echoed_0 = request.metric_series_id
            response.metric_series.metric_series_id = echoed_0
            return response

    async def handle_notify_metric_series_watchers(
        self,
        request: metrics_v1_metric_series_notification_service_pb2.NotifyMetricSeriesWatchersRequest
    ) -> metrics_v1_metric_series_notification_service_pb2.NotifyMetricSeriesWatchersResponse:
        """Notifys a metric series."""
        deps = self.deps
        response = metrics_v1_metric_series_notification_service_pb2.NotifyMetricSeriesWatchersResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('NotifyMetricSeriesWatchers', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'NotifyMetricSeriesWatchers',
                {'reason': request.reason}
            )
            echoed_0 = request.metric_series_id
            response.metric_series.metric_series_id = echoed_0
            echoed_1 = request.details.recipient.email
            response.metric_series.owner.email = echoed_1
            return response

    async def handle_send_metric_series_test_notice(
        self,
        request: metrics_v1_metric_series_notification_service_pb2.SendMetricSeriesTestNoticeRequest
    ) -> metrics_v1_metric_series_notification_service_pb2.SendMetricSeriesTestNoticeResponse:
        """Sends a metric series."""
        deps = self.deps
        response = metrics_v1_metric_series_notification_service_pb2.SendMetricSeriesTestNoticeResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SendMetricSeriesTestNotice', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'SendMetricSeriesTestNotice',
                {'reason': request.reason}
            )
            echoed_0 = request.metric_series_id
            response.metric_series.metric_series_id = echoed_0
            echoed_1 = request.details.recipient.email
            response.metric_series.owner.email = echoed_1
            return response

    async def handle_stream_metric_series_notices(
        self,
        request: metrics_v1_metric_series_notification_service_pb2.StreamMetricSeriesNoticesRequest
    ) -> metrics_v1_metric_series_notification_service_pb2.StreamMetricSeriesNoticesResponse:
        """Streams the changes of metric serieses as they happen."""
        deps = self.deps
        response = metrics_v1_metric_series_notification_service_pb2.StreamMetricSeriesNoticesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('StreamMetricSeriesNotices', extra={'fields': {'max_events': request.max_events}})
            await deps.repository.audit(
                request.context.tenant_id,
                'StreamMetricSeriesNotices',
                {'max_events': request.max_events}
            )
            response_0 = metrics_v1_dashboard_export_service_pb2.ScheduleDashboardExportResponse()
            outgoing_0 = metrics_v1_dashboard_export_service_pb2.ScheduleDashboardExportRequest(
                annotations=dict(request.context.baggage),
                context=request.context,
                details=metrics_v1_dashboard_export_service_pb2.ScheduleDashboardExportRequest.Details(
                    filters=dict(request.filter.labels)
                )
            )
            response_0 = await deps.clients.metrics_dashboard_export.ScheduleDashboardExport(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_0)
            echoed_0 = request.subscriber.email
            response.metric_series.owner.email = echoed_0
            return response

    async def handle_subscribe_metric_series_updates(
        self,
        request: metrics_v1_metric_series_notification_service_pb2.SubscribeMetricSeriesUpdatesRequest
    ) -> metrics_v1_metric_series_notification_service_pb2.SubscribeMetricSeriesUpdatesResponse:
        """Subscribes a metric series."""
        deps = self.deps
        response = metrics_v1_metric_series_notification_service_pb2.SubscribeMetricSeriesUpdatesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SubscribeMetricSeriesUpdates', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'SubscribeMetricSeriesUpdates',
                {'reason': request.reason}
            )
            response_0 = metrics_v1_dashboard_export_service_pb2.ShareDashboardExportResponse()
            outgoing_0 = metrics_v1_dashboard_export_service_pb2.ShareDashboardExportRequest(
                context=request.context,
                details=metrics_v1_dashboard_export_service_pb2.ShareDashboardExportRequest.Details(
                    recipient=common_v1_contact_pb2.ContactInfo(phone=request.details.recipient.phone)
                )
            )
            method_name_0 = 'ShareDashboardExport'
            response_0 = await getattr(
                deps.clients.metrics_dashboard_export,
                method_name_0
            )(outgoing_0, timeout=deps.settings.timeout)
            returned_0_0 = response_0.outcome.status
            if returned_0_0:
                response.outcome.status = returned_0_0
            echoed_0 = request.metric_series_id
            response.metric_series.metric_series_id = echoed_0
            echoed_1 = request.details.recipient.email
            response.metric_series.owner.email = echoed_1
            return response

    async def handle_unsubscribe_metric_series_updates(
        self,
        request: metrics_v1_metric_series_notification_service_pb2.UnsubscribeMetricSeriesUpdatesRequest
    ) -> metrics_v1_metric_series_notification_service_pb2.UnsubscribeMetricSeriesUpdatesResponse:
        """Unsubscribes a metric series."""
        deps = self.deps
        response = metrics_v1_metric_series_notification_service_pb2.UnsubscribeMetricSeriesUpdatesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('UnsubscribeMetricSeriesUpdates', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'UnsubscribeMetricSeriesUpdates',
                {'reason': request.reason}
            )
            echoed_0 = request.metric_series_id
            response.metric_series.metric_series_id = echoed_0
            echoed_1 = request.details.recipient.email
            response.metric_series.owner.email = echoed_1
            return response
