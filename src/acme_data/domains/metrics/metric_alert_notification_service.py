"""Tells the people who follow a metric alert what changed."""

from __future__ import annotations

from collections.abc import AsyncIterator
from dataclasses import dataclass
import logging

import grpc

from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.metrics.v1 import metric_alert_notification_service_pb2 as metrics_v1_metric_alert_notification_service_pb2
from acme.metrics.v1 import (
    metric_alert_notification_service_pb2_grpc as metrics_v1_metric_alert_notification_service_pb2_grpc,
)
from acme.metrics.v1 import metric_series_export_service_pb2 as metrics_v1_metric_series_export_service_pb2
from acme.metrics.v1 import metrics_pb2 as metrics_v1_metrics_pb2

from acme_data.domains.metrics.dependencies import Dependencies
from acme_data.platform.rpc import messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


@dataclass(slots=True)
class MetricAlertNotificationServicer(
    metrics_v1_metric_alert_notification_service_pb2_grpc.MetricAlertNotificationServiceServicer
):
    deps: Dependencies

    @rpc_errors
    @retry_transient
    async def GetMetricAlertPreferences(
        self, request: metrics_v1_metric_alert_notification_service_pb2.GetMetricAlertPreferencesRequest, context: grpc.aio.ServicerContext,
    ) -> metrics_v1_metric_alert_notification_service_pb2.GetMetricAlertPreferencesResponse:
        """Returns a metric alert."""
        return await self.handle_get_metric_alert_preferences(request)

    @rpc_errors
    @retry_transient
    async def ListMetricAlertSubscriptions(
        self, request: metrics_v1_metric_alert_notification_service_pb2.ListMetricAlertSubscriptionsRequest, context: grpc.aio.ServicerContext,
    ) -> metrics_v1_metric_alert_notification_service_pb2.ListMetricAlertSubscriptionsResponse:
        """Lists metric alerts a page at a time."""
        return await self.handle_list_metric_alert_subscriptions(request)

    @rpc_errors
    async def NotifyMetricAlertWatchers(
        self, request: metrics_v1_metric_alert_notification_service_pb2.NotifyMetricAlertWatchersRequest, context: grpc.aio.ServicerContext,
    ) -> metrics_v1_metric_alert_notification_service_pb2.NotifyMetricAlertWatchersResponse:
        """Notifys a metric alert."""
        return await self.handle_notify_metric_alert_watchers(request)

    @rpc_errors
    async def SendMetricAlertTestNotice(
        self, request: metrics_v1_metric_alert_notification_service_pb2.SendMetricAlertTestNoticeRequest, context: grpc.aio.ServicerContext,
    ) -> metrics_v1_metric_alert_notification_service_pb2.SendMetricAlertTestNoticeResponse:
        """Sends a metric alert."""
        return await self.handle_send_metric_alert_test_notice(request)

    @stream_errors
    async def StreamMetricAlertNotices(
        self, request: metrics_v1_metric_alert_notification_service_pb2.StreamMetricAlertNoticesRequest, context: grpc.aio.ServicerContext,
    ) -> AsyncIterator[metrics_v1_metric_alert_notification_service_pb2.StreamMetricAlertNoticesResponse]:
        """Streams the changes of metric alerts as they happen."""
        response = await self.handle_stream_metric_alert_notices(request)
        for item in messages((response,)):
            yield item

    @rpc_errors
    async def SubscribeMetricAlertUpdates(
        self, request: metrics_v1_metric_alert_notification_service_pb2.SubscribeMetricAlertUpdatesRequest, context: grpc.aio.ServicerContext,
    ) -> metrics_v1_metric_alert_notification_service_pb2.SubscribeMetricAlertUpdatesResponse:
        """Subscribes a metric alert."""
        return await self.handle_subscribe_metric_alert_updates(request)

    @rpc_errors
    async def UnsubscribeMetricAlertUpdates(
        self, request: metrics_v1_metric_alert_notification_service_pb2.UnsubscribeMetricAlertUpdatesRequest, context: grpc.aio.ServicerContext,
    ) -> metrics_v1_metric_alert_notification_service_pb2.UnsubscribeMetricAlertUpdatesResponse:
        """Unsubscribes a metric alert."""
        return await self.handle_unsubscribe_metric_alert_updates(request)

    async def handle_get_metric_alert_preferences(
        self,
        request: metrics_v1_metric_alert_notification_service_pb2.GetMetricAlertPreferencesRequest
    ) -> metrics_v1_metric_alert_notification_service_pb2.GetMetricAlertPreferencesResponse:
        """Returns a metric alert."""
        deps = self.deps
        response = metrics_v1_metric_alert_notification_service_pb2.GetMetricAlertPreferencesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('GetMetricAlertPreferences', extra={'fields': {'locale': request.context.locale}})
            await deps.repository.audit(
                request.context.tenant_id,
                'GetMetricAlertPreferences',
                {'locale': request.context.locale}
            )
            echoed_0 = request.metric_alert_id
            response.metric_alert.metric_alert_id = echoed_0
            return response

    async def handle_list_metric_alert_subscriptions(
        self,
        request: metrics_v1_metric_alert_notification_service_pb2.ListMetricAlertSubscriptionsRequest
    ) -> metrics_v1_metric_alert_notification_service_pb2.ListMetricAlertSubscriptionsResponse:
        """Lists metric alerts a page at a time."""
        deps = self.deps
        response = metrics_v1_metric_alert_notification_service_pb2.ListMetricAlertSubscriptionsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ListMetricAlertSubscriptions', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ListMetricAlertSubscriptions',
                {'order_by': request.order_by}
            )
            response_0 = metrics_v1_metric_series_export_service_pb2.RetryMetricSeriesExportResponse()
            outgoing_0 = metrics_v1_metric_series_export_service_pb2.RetryMetricSeriesExportRequest(
                context=request.context,
                metric_series=metrics_v1_metrics_pb2.MetricSeries(
                    address=common_v1_address_pb2.PostalAddress(region=request.filter.region)
                )
            )
            response_0 = await deps.clients.metrics_metric_series_export.RetryMetricSeriesExport(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.result.message = returned_0_0
            return response

    async def handle_notify_metric_alert_watchers(
        self,
        request: metrics_v1_metric_alert_notification_service_pb2.NotifyMetricAlertWatchersRequest
    ) -> metrics_v1_metric_alert_notification_service_pb2.NotifyMetricAlertWatchersResponse:
        """Notifys a metric alert."""
        deps = self.deps
        response = metrics_v1_metric_alert_notification_service_pb2.NotifyMetricAlertWatchersResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('NotifyMetricAlertWatchers', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'NotifyMetricAlertWatchers',
                {'reason': request.reason}
            )
            echoed_0 = request.metric_alert_id
            response.metric_alert.metric_alert_id = echoed_0
            echoed_1 = request.details.recipient.email
            response.metric_alert.owner.email = echoed_1
            return response

    async def handle_send_metric_alert_test_notice(
        self,
        request: metrics_v1_metric_alert_notification_service_pb2.SendMetricAlertTestNoticeRequest
    ) -> metrics_v1_metric_alert_notification_service_pb2.SendMetricAlertTestNoticeResponse:
        """Sends a metric alert."""
        deps = self.deps
        response = metrics_v1_metric_alert_notification_service_pb2.SendMetricAlertTestNoticeResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SendMetricAlertTestNotice', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'SendMetricAlertTestNotice',
                {'reason': request.reason}
            )
            echoed_0 = request.metric_alert_id
            response.metric_alert.metric_alert_id = echoed_0
            echoed_1 = request.details.recipient.email
            response.metric_alert.owner.email = echoed_1
            return response

    async def handle_stream_metric_alert_notices(
        self,
        request: metrics_v1_metric_alert_notification_service_pb2.StreamMetricAlertNoticesRequest
    ) -> metrics_v1_metric_alert_notification_service_pb2.StreamMetricAlertNoticesResponse:
        """Streams the changes of metric alerts as they happen."""
        deps = self.deps
        response = metrics_v1_metric_alert_notification_service_pb2.StreamMetricAlertNoticesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('StreamMetricAlertNotices', extra={'fields': {'max_events': request.max_events}})
            await deps.repository.audit(
                request.context.tenant_id,
                'StreamMetricAlertNotices',
                {'max_events': request.max_events}
            )
            echoed_0 = request.subscriber.email
            response.metric_alert.owner.email = echoed_0
            return response

    async def handle_subscribe_metric_alert_updates(
        self,
        request: metrics_v1_metric_alert_notification_service_pb2.SubscribeMetricAlertUpdatesRequest
    ) -> metrics_v1_metric_alert_notification_service_pb2.SubscribeMetricAlertUpdatesResponse:
        """Subscribes a metric alert."""
        deps = self.deps
        response = metrics_v1_metric_alert_notification_service_pb2.SubscribeMetricAlertUpdatesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SubscribeMetricAlertUpdates', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'SubscribeMetricAlertUpdates',
                {'reason': request.reason}
            )
            echoed_0 = request.metric_alert_id
            response.metric_alert.metric_alert_id = echoed_0
            echoed_1 = request.details.recipient.email
            response.metric_alert.owner.email = echoed_1
            return response

    async def handle_unsubscribe_metric_alert_updates(
        self,
        request: metrics_v1_metric_alert_notification_service_pb2.UnsubscribeMetricAlertUpdatesRequest
    ) -> metrics_v1_metric_alert_notification_service_pb2.UnsubscribeMetricAlertUpdatesResponse:
        """Unsubscribes a metric alert."""
        deps = self.deps
        response = metrics_v1_metric_alert_notification_service_pb2.UnsubscribeMetricAlertUpdatesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('UnsubscribeMetricAlertUpdates', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'UnsubscribeMetricAlertUpdates',
                {'reason': request.reason}
            )
            echoed_0 = request.metric_alert_id
            response.metric_alert.metric_alert_id = echoed_0
            echoed_1 = request.details.recipient.email
            response.metric_alert.owner.email = echoed_1
            return response
