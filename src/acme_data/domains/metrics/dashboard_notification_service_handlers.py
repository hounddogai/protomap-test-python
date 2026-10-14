"""Reusable transport mixin for DashboardNotificationService."""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import cast
import logging

import grpc

from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.metrics.v1 import dashboard_admin_service_pb2 as metrics_v1_dashboard_admin_service_pb2
from acme.metrics.v1 import dashboard_export_service_pb2 as metrics_v1_dashboard_export_service_pb2
from acme.metrics.v1 import dashboard_notification_service_pb2 as metrics_v1_dashboard_notification_service_pb2

from acme_data.domains.metrics.dependencies import Dependencies
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class DashboardNotificationServicerHandlers:
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    @retry_transient
    async def GetDashboardPreferences(
        self, request: metrics_v1_dashboard_notification_service_pb2.GetDashboardPreferencesRequest, context: grpc.aio.ServicerContext,
    ) -> metrics_v1_dashboard_notification_service_pb2.GetDashboardPreferencesResponse:
        """Returns a dashboard."""
        return await self.handle_get_dashboard_preferences(request)

    @rpc_errors
    @retry_transient
    async def ListDashboardSubscriptions(
        self, request: metrics_v1_dashboard_notification_service_pb2.ListDashboardSubscriptionsRequest, context: grpc.aio.ServicerContext,
    ) -> metrics_v1_dashboard_notification_service_pb2.ListDashboardSubscriptionsResponse:
        """Lists dashboards a page at a time."""
        return await self.handle_list_dashboard_subscriptions(request)

    @rpc_errors
    async def NotifyDashboardWatchers(
        self, request: metrics_v1_dashboard_notification_service_pb2.NotifyDashboardWatchersRequest, context: grpc.aio.ServicerContext,
    ) -> metrics_v1_dashboard_notification_service_pb2.NotifyDashboardWatchersResponse:
        """Notifys a dashboard."""
        return await self.handle_notify_dashboard_watchers(request)

    @rpc_errors
    async def SendDashboardTestNotice(
        self, request: metrics_v1_dashboard_notification_service_pb2.SendDashboardTestNoticeRequest, context: grpc.aio.ServicerContext,
    ) -> metrics_v1_dashboard_notification_service_pb2.SendDashboardTestNoticeResponse:
        """Sends a dashboard."""
        return await self.handle_send_dashboard_test_notice(request)

    @stream_errors
    async def StreamDashboardNotices(
        self, request: metrics_v1_dashboard_notification_service_pb2.StreamDashboardNoticesRequest, context: grpc.aio.ServicerContext,
    ) -> AsyncIterator[metrics_v1_dashboard_notification_service_pb2.StreamDashboardNoticesResponse]:
        """Streams the changes of dashboards as they happen."""
        response = await self.handle_stream_dashboard_notices(request)
        for item in messages((response,)):
            yield item

    @rpc_errors
    async def SubscribeDashboardUpdates(
        self, request: metrics_v1_dashboard_notification_service_pb2.SubscribeDashboardUpdatesRequest, context: grpc.aio.ServicerContext,
    ) -> metrics_v1_dashboard_notification_service_pb2.SubscribeDashboardUpdatesResponse:
        """Subscribes a dashboard."""
        return await self.handle_subscribe_dashboard_updates(request)

    @rpc_errors
    async def UnsubscribeDashboardUpdates(
        self, request: metrics_v1_dashboard_notification_service_pb2.UnsubscribeDashboardUpdatesRequest, context: grpc.aio.ServicerContext,
    ) -> metrics_v1_dashboard_notification_service_pb2.UnsubscribeDashboardUpdatesResponse:
        """Unsubscribes a dashboard."""
        return await self.handle_unsubscribe_dashboard_updates(request)

    async def handle_get_dashboard_preferences(
        self,
        request: metrics_v1_dashboard_notification_service_pb2.GetDashboardPreferencesRequest
    ) -> metrics_v1_dashboard_notification_service_pb2.GetDashboardPreferencesResponse:
        """Returns a dashboard."""
        deps = self.deps
        response = metrics_v1_dashboard_notification_service_pb2.GetDashboardPreferencesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('GetDashboardPreferences', extra={'fields': {'domain': 'metrics'}})
            await deps.repository.audit(request.context.tenant_id, 'GetDashboardPreferences', {})
            response_0 = metrics_v1_dashboard_export_service_pb2.StreamDashboardExportResponse()
            outgoing_0 = metrics_v1_dashboard_export_service_pb2.StreamDashboardExportRequest(
                context=request.context,
                filter=metrics_v1_dashboard_export_service_pb2.StreamDashboardExportRequest.Filter(
                    created_after=request.context.deadline,
                    labels=dict(request.context.baggage),
                    owner_id=request.dashboard_id
                )
            )
            async for chunk_0 in deps.clients.metrics_dashboard_export.StreamDashboardExport(
                outgoing_0,
                timeout=deps.settings.timeout
            ):
                response_0 = chunk_0
            echoed_0 = request.dashboard_id
            response.dashboard.dashboard_id = echoed_0
            return response

    async def handle_list_dashboard_subscriptions(
        self,
        request: metrics_v1_dashboard_notification_service_pb2.ListDashboardSubscriptionsRequest
    ) -> metrics_v1_dashboard_notification_service_pb2.ListDashboardSubscriptionsResponse:
        """Lists dashboards a page at a time."""
        deps = self.deps
        response = metrics_v1_dashboard_notification_service_pb2.ListDashboardSubscriptionsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ListDashboardSubscriptions', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ListDashboardSubscriptions',
                {'order_by': request.order_by}
            )
            return response

    async def handle_notify_dashboard_watchers(
        self,
        request: metrics_v1_dashboard_notification_service_pb2.NotifyDashboardWatchersRequest
    ) -> metrics_v1_dashboard_notification_service_pb2.NotifyDashboardWatchersResponse:
        """Notifys a dashboard."""
        deps = self.deps
        response = metrics_v1_dashboard_notification_service_pb2.NotifyDashboardWatchersResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('NotifyDashboardWatchers', extra={'fields': {'channel': request.details.channel}})
            await deps.repository.audit(
                request.context.tenant_id,
                'NotifyDashboardWatchers',
                {'channel': request.details.channel}
            )
            response_0 = metrics_v1_dashboard_admin_service_pb2.ReassignDashboardResponse()
            outgoing_0 = metrics_v1_dashboard_admin_service_pb2.ReassignDashboardRequest(
                context=request.context,
                dashboard_id=request.dashboard_id,
                details=metrics_v1_dashboard_admin_service_pb2.ReassignDashboardRequest.Details(
                    assignee=identity_v1_refs_pb2.UserRef(
                        email=request.details.recipient.email,
                        user_id=request.context.actor.user_id
                    )
                ),
                reason=request.reason
            )
            response_0 = cast(metrics_v1_dashboard_admin_service_pb2.ReassignDashboardResponse, await deps.bus.request(
                'acme.metrics.v1.DashboardNotificationService/NotifyDashboardWatchers/0', outgoing_0, deps.settings.timeout,
            ))
            returned_0_0 = response_0.dashboard.audit.updated_by
            if returned_0_0:
                response.dashboard.audit.updated_by = returned_0_0
            returned_0_1 = response_0.outcome.reference_id
            if returned_0_1:
                response.outcome.reference_id = returned_0_1
            echoed_0 = request.dashboard_id
            response.dashboard.dashboard_id = echoed_0
            return response

    async def handle_send_dashboard_test_notice(
        self,
        request: metrics_v1_dashboard_notification_service_pb2.SendDashboardTestNoticeRequest
    ) -> metrics_v1_dashboard_notification_service_pb2.SendDashboardTestNoticeResponse:
        """Sends a dashboard."""
        deps = self.deps
        response = metrics_v1_dashboard_notification_service_pb2.SendDashboardTestNoticeResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SendDashboardTestNotice', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'SendDashboardTestNotice',
                {'reason': request.reason}
            )
            echoed_0 = request.dashboard_id
            response.dashboard.dashboard_id = echoed_0
            return response

    async def handle_stream_dashboard_notices(
        self,
        request: metrics_v1_dashboard_notification_service_pb2.StreamDashboardNoticesRequest
    ) -> metrics_v1_dashboard_notification_service_pb2.StreamDashboardNoticesResponse:
        """Streams the changes of dashboards as they happen."""
        deps = self.deps
        response = metrics_v1_dashboard_notification_service_pb2.StreamDashboardNoticesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('StreamDashboardNotices', extra={'fields': {'max_events': request.max_events}})
            await deps.repository.audit(
                request.context.tenant_id,
                'StreamDashboardNotices',
                {'max_events': request.max_events}
            )
            echoed_0 = request.filter.region
            response.dashboard.billing_address.region = echoed_0
            return response

    async def handle_subscribe_dashboard_updates(
        self,
        request: metrics_v1_dashboard_notification_service_pb2.SubscribeDashboardUpdatesRequest
    ) -> metrics_v1_dashboard_notification_service_pb2.SubscribeDashboardUpdatesResponse:
        """Subscribes a dashboard."""
        deps = self.deps
        response = metrics_v1_dashboard_notification_service_pb2.SubscribeDashboardUpdatesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SubscribeDashboardUpdates', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'SubscribeDashboardUpdates',
                {'reason': request.reason}
            )
            echoed_0 = request.dashboard_id
            response.dashboard.dashboard_id = echoed_0
            return response

    async def handle_unsubscribe_dashboard_updates(
        self,
        request: metrics_v1_dashboard_notification_service_pb2.UnsubscribeDashboardUpdatesRequest
    ) -> metrics_v1_dashboard_notification_service_pb2.UnsubscribeDashboardUpdatesResponse:
        """Unsubscribes a dashboard."""
        deps = self.deps
        response = metrics_v1_dashboard_notification_service_pb2.UnsubscribeDashboardUpdatesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('UnsubscribeDashboardUpdates', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'UnsubscribeDashboardUpdates',
                {'reason': request.reason}
            )
            response_0 = metrics_v1_dashboard_admin_service_pb2.ArchiveDashboardResponse()
            outgoing_0 = metrics_v1_dashboard_admin_service_pb2.ArchiveDashboardRequest(
                context=request.context,
                dashboard_id=request.dashboard_id,
                details=metrics_v1_dashboard_admin_service_pb2.ArchiveDashboardRequest.Details(
                    new_owner=identity_v1_refs_pb2.UserRef(email=request.details.recipient.email)
                )
            )
            response_0 = await deps.clients.metrics_dashboard_admin.ArchiveDashboard(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.dashboard.status
            if returned_0_0:
                response.dashboard.status = returned_0_0
            returned_0_1 = response_0.dashboard.counterparty.version
            if returned_0_1:
                response.dashboard.counterparty.version = returned_0_1
            echoed_0 = request.dashboard_id
            response.dashboard.dashboard_id = echoed_0
            return response
