"""Manages analytics events: creates, reads, changes, and lists them."""

from __future__ import annotations

from collections.abc import AsyncIterator

import grpc

from acme.analytics.v1 import analytics_event_service_pb2 as analytics_v1_analytics_event_service_pb2
from acme.analytics.v1 import analytics_event_service_pb2_grpc as analytics_v1_analytics_event_service_pb2_grpc

from acme_data.domains.analytics.analytics_event_service_operations import handle_batch_create_analytics_events
from acme_data.domains.analytics.analytics_event_service_operations import handle_create_analytics_event
from acme_data.domains.analytics.analytics_event_service_operations import handle_delete_analytics_event
from acme_data.domains.analytics.analytics_event_service_operations import handle_get_analytics_event
from acme_data.domains.analytics.analytics_event_service_operations import handle_list_analytics_events
from acme_data.domains.analytics.analytics_event_service_operations import handle_search_analytics_events
from acme_data.domains.analytics.analytics_event_service_operations import handle_update_analytics_event
from acme_data.domains.analytics.analytics_event_service_operations import handle_watch_analytics_events
from acme_data.domains.analytics.dependencies import Dependencies
from acme_data.platform.rpc import messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors


class AnalyticsEventServicer(analytics_v1_analytics_event_service_pb2_grpc.AnalyticsEventServiceServicer):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    async def BatchCreateAnalyticsEvents(
        self, requests: AsyncIterator[
            analytics_v1_analytics_event_service_pb2.BatchCreateAnalyticsEventsRequest
        ], context: grpc.aio.ServicerContext,
    ) -> analytics_v1_analytics_event_service_pb2.BatchCreateAnalyticsEventsResponse:
        """Takes a stream of analytics events and answers once at the end."""
        response = analytics_v1_analytics_event_service_pb2.BatchCreateAnalyticsEventsResponse()
        async for request in requests:
            response.MergeFrom(await handle_batch_create_analytics_events(self.deps, request))
        return response

    @rpc_errors
    async def CreateAnalyticsEvent(
        self, request: analytics_v1_analytics_event_service_pb2.CreateAnalyticsEventRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_analytics_event_service_pb2.CreateAnalyticsEventResponse:
        """Creates an analytics event."""
        return await handle_create_analytics_event(self.deps, request)

    @rpc_errors
    async def DeleteAnalyticsEvent(
        self, request: analytics_v1_analytics_event_service_pb2.DeleteAnalyticsEventRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_analytics_event_service_pb2.DeleteAnalyticsEventResponse:
        """Deletes an analytics event."""
        return await handle_delete_analytics_event(self.deps, request)

    @rpc_errors
    @retry_transient
    async def GetAnalyticsEvent(
        self, request: analytics_v1_analytics_event_service_pb2.GetAnalyticsEventRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_analytics_event_service_pb2.GetAnalyticsEventResponse:
        """Returns an analytics event."""
        return await handle_get_analytics_event(self.deps, request)

    @rpc_errors
    @retry_transient
    async def ListAnalyticsEvents(
        self, request: analytics_v1_analytics_event_service_pb2.ListAnalyticsEventsRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_analytics_event_service_pb2.ListAnalyticsEventsResponse:
        """Lists analytics events a page at a time."""
        return await handle_list_analytics_events(self.deps, request)

    @rpc_errors
    @retry_transient
    async def SearchAnalyticsEvents(
        self, request: analytics_v1_analytics_event_service_pb2.SearchAnalyticsEventsRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_analytics_event_service_pb2.SearchAnalyticsEventsResponse:
        """Lists analytics events a page at a time."""
        return await handle_search_analytics_events(self.deps, request)

    @rpc_errors
    async def UpdateAnalyticsEvent(
        self, request: analytics_v1_analytics_event_service_pb2.UpdateAnalyticsEventRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_analytics_event_service_pb2.UpdateAnalyticsEventResponse:
        """Changes an analytics event."""
        return await handle_update_analytics_event(self.deps, request)

    @stream_errors
    async def WatchAnalyticsEvents(
        self, request: analytics_v1_analytics_event_service_pb2.WatchAnalyticsEventsRequest, context: grpc.aio.ServicerContext,
    ) -> AsyncIterator[analytics_v1_analytics_event_service_pb2.WatchAnalyticsEventsResponse]:
        """Streams the changes of analytics events as they happen."""
        response = await handle_watch_analytics_events(self.deps, request)
        for item in messages((response,)):
            yield item
