"""Tells the people who follow a workspace what changed."""

from __future__ import annotations

from collections.abc import AsyncIterator

import grpc

from acme.datahub.v1 import workspace_notification_service_pb2 as datahub_v1_workspace_notification_service_pb2
from acme.datahub.v1 import (
    workspace_notification_service_pb2_grpc as datahub_v1_workspace_notification_service_pb2_grpc,
)

from acme_data.domains.datahub.dependencies import Dependencies
from acme_data.domains.datahub.workspace_notification_service_operations import handle_get_workspace_preferences
from acme_data.domains.datahub.workspace_notification_service_operations import handle_list_workspace_subscriptions
from acme_data.domains.datahub.workspace_notification_service_operations import handle_notify_workspace_watchers
from acme_data.domains.datahub.workspace_notification_service_operations import handle_send_workspace_test_notice
from acme_data.domains.datahub.workspace_notification_service_operations import handle_stream_workspace_notices
from acme_data.domains.datahub.workspace_notification_service_operations import handle_subscribe_workspace_updates
from acme_data.domains.datahub.workspace_notification_service_operations import handle_unsubscribe_workspace_updates
from acme_data.platform.rpc import messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors


class WorkspaceNotificationServicer(
    datahub_v1_workspace_notification_service_pb2_grpc.WorkspaceNotificationServiceServicer
):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    @retry_transient
    async def GetWorkspacePreferences(
        self, request: datahub_v1_workspace_notification_service_pb2.GetWorkspacePreferencesRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_workspace_notification_service_pb2.GetWorkspacePreferencesResponse:
        """Returns a workspace."""
        return await handle_get_workspace_preferences(self.deps, request)

    @rpc_errors
    @retry_transient
    async def ListWorkspaceSubscriptions(
        self, request: datahub_v1_workspace_notification_service_pb2.ListWorkspaceSubscriptionsRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_workspace_notification_service_pb2.ListWorkspaceSubscriptionsResponse:
        """Lists workspaces a page at a time."""
        return await handle_list_workspace_subscriptions(self.deps, request)

    @rpc_errors
    async def NotifyWorkspaceWatchers(
        self, request: datahub_v1_workspace_notification_service_pb2.NotifyWorkspaceWatchersRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_workspace_notification_service_pb2.NotifyWorkspaceWatchersResponse:
        """Notifys a workspace."""
        return await handle_notify_workspace_watchers(self.deps, request)

    @rpc_errors
    async def SendWorkspaceTestNotice(
        self, request: datahub_v1_workspace_notification_service_pb2.SendWorkspaceTestNoticeRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_workspace_notification_service_pb2.SendWorkspaceTestNoticeResponse:
        """Sends a workspace."""
        return await handle_send_workspace_test_notice(self.deps, request)

    @stream_errors
    async def StreamWorkspaceNotices(
        self, request: datahub_v1_workspace_notification_service_pb2.StreamWorkspaceNoticesRequest, context: grpc.aio.ServicerContext,
    ) -> AsyncIterator[datahub_v1_workspace_notification_service_pb2.StreamWorkspaceNoticesResponse]:
        """Streams the changes of workspaces as they happen."""
        response = await handle_stream_workspace_notices(self.deps, request)
        for item in messages((response,)):
            yield item

    @rpc_errors
    async def SubscribeWorkspaceUpdates(
        self, request: datahub_v1_workspace_notification_service_pb2.SubscribeWorkspaceUpdatesRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_workspace_notification_service_pb2.SubscribeWorkspaceUpdatesResponse:
        """Subscribes a workspace."""
        return await handle_subscribe_workspace_updates(self.deps, request)

    @rpc_errors
    async def UnsubscribeWorkspaceUpdates(
        self, request: datahub_v1_workspace_notification_service_pb2.UnsubscribeWorkspaceUpdatesRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_workspace_notification_service_pb2.UnsubscribeWorkspaceUpdatesResponse:
        """Unsubscribes a workspace."""
        return await handle_unsubscribe_workspace_updates(self.deps, request)
