"""Tells the people who follow a data share what changed."""

from __future__ import annotations

from collections.abc import AsyncIterator

import grpc

from acme.datahub.v1 import data_share_notification_service_pb2 as datahub_v1_data_share_notification_service_pb2
from acme.datahub.v1 import (
    data_share_notification_service_pb2_grpc as datahub_v1_data_share_notification_service_pb2_grpc,
)

from acme_data.domains.datahub.data_share_notification_service_operations import handle_get_data_share_preferences
from acme_data.domains.datahub.data_share_notification_service_operations import handle_list_data_share_subscriptions
from acme_data.domains.datahub.data_share_notification_service_operations import handle_notify_data_share_watchers
from acme_data.domains.datahub.data_share_notification_service_operations import handle_send_data_share_test_notice
from acme_data.domains.datahub.data_share_notification_service_operations import handle_subscribe_data_share_updates
from acme_data.domains.datahub.data_share_notification_service_operations import handle_unsubscribe_data_share_updates
from acme_data.domains.datahub.dependencies import Dependencies
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors


class DataShareNotificationServicer(
    datahub_v1_data_share_notification_service_pb2_grpc.DataShareNotificationServiceServicer
):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    @retry_transient
    async def GetDataSharePreferences(
        self, request: datahub_v1_data_share_notification_service_pb2.GetDataSharePreferencesRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_data_share_notification_service_pb2.GetDataSharePreferencesResponse:
        """Returns a data share."""
        return await handle_get_data_share_preferences(self.deps, request)

    @rpc_errors
    @retry_transient
    async def ListDataShareSubscriptions(
        self, request: datahub_v1_data_share_notification_service_pb2.ListDataShareSubscriptionsRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_data_share_notification_service_pb2.ListDataShareSubscriptionsResponse:
        """Lists data shares a page at a time."""
        return await handle_list_data_share_subscriptions(self.deps, request)

    @rpc_errors
    async def NotifyDataShareWatchers(
        self, request: datahub_v1_data_share_notification_service_pb2.NotifyDataShareWatchersRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_data_share_notification_service_pb2.NotifyDataShareWatchersResponse:
        """Notifys a data share."""
        return await handle_notify_data_share_watchers(self.deps, request)

    @rpc_errors
    async def SendDataShareTestNotice(
        self, request: datahub_v1_data_share_notification_service_pb2.SendDataShareTestNoticeRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_data_share_notification_service_pb2.SendDataShareTestNoticeResponse:
        """Sends a data share."""
        return await handle_send_data_share_test_notice(self.deps, request)

    @rpc_errors
    async def SubscribeDataShareUpdates(
        self, request: datahub_v1_data_share_notification_service_pb2.SubscribeDataShareUpdatesRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_data_share_notification_service_pb2.SubscribeDataShareUpdatesResponse:
        """Subscribes a data share."""
        return await handle_subscribe_data_share_updates(self.deps, request)

    @rpc_errors
    async def UnsubscribeDataShareUpdates(
        self, request: datahub_v1_data_share_notification_service_pb2.UnsubscribeDataShareUpdatesRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_data_share_notification_service_pb2.UnsubscribeDataShareUpdatesResponse:
        """Unsubscribes a data share."""
        return await handle_unsubscribe_data_share_updates(self.deps, request)
