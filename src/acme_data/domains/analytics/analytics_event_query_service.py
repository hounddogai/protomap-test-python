"""Answers read-only questions about analytics events, for screens and reports."""

from __future__ import annotations

from collections.abc import AsyncIterator

import grpc

from acme.analytics.v1 import analytics_event_query_service_pb2 as analytics_v1_analytics_event_query_service_pb2
from acme.analytics.v1 import (
    analytics_event_query_service_pb2_grpc as analytics_v1_analytics_event_query_service_pb2_grpc,
)

from acme_data.domains.analytics.analytics_event_query_service_workflow import AnalyticsEventQueryServicerWorkflow
from acme_data.domains.analytics.dependencies import Dependencies
from acme_data.platform.rpc import messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors


class AnalyticsEventQueryServicer(
    analytics_v1_analytics_event_query_service_pb2_grpc.AnalyticsEventQueryServiceServicer
):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps
        self.workflow = AnalyticsEventQueryServicerWorkflow(deps)

    @rpc_errors
    @retry_transient
    async def BrowseAnalyticsEvents(
        self, request: analytics_v1_analytics_event_query_service_pb2.BrowseAnalyticsEventsRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_analytics_event_query_service_pb2.BrowseAnalyticsEventsResponse:
        """Lists analytics events a page at a time."""
        return await self.workflow.handle_browse_analytics_events(request)

    @rpc_errors
    @retry_transient
    async def CountAnalyticsEvents(
        self, request: analytics_v1_analytics_event_query_service_pb2.CountAnalyticsEventsRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_analytics_event_query_service_pb2.CountAnalyticsEventsResponse:
        """Counts analytics events by status."""
        return await self.workflow.handle_count_analytics_events(request)

    @stream_errors
    async def ExportAnalyticsEvents(
        self, request: analytics_v1_analytics_event_query_service_pb2.ExportAnalyticsEventsRequest, context: grpc.aio.ServicerContext,
    ) -> AsyncIterator[analytics_v1_analytics_event_query_service_pb2.ExportAnalyticsEventsResponse]:
        """Streams every matching analytics event."""
        response = await self.workflow.handle_export_analytics_events(request)
        for item in messages((response,)):
            yield item

    @rpc_errors
    @retry_transient
    async def FindAnalyticsEvents(
        self, request: analytics_v1_analytics_event_query_service_pb2.FindAnalyticsEventsRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_analytics_event_query_service_pb2.FindAnalyticsEventsResponse:
        """Lists analytics events a page at a time."""
        return await self.workflow.handle_find_analytics_events(request)

    @rpc_errors
    @retry_transient
    async def LookupAnalyticsEvent(
        self, request: analytics_v1_analytics_event_query_service_pb2.LookupAnalyticsEventRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_analytics_event_query_service_pb2.LookupAnalyticsEventResponse:
        """Returns an analytics event."""
        return await self.workflow.handle_lookup_analytics_event(request)

    @rpc_errors
    @retry_transient
    async def PeekAnalyticsEvent(
        self, request: analytics_v1_analytics_event_query_service_pb2.PeekAnalyticsEventRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_analytics_event_query_service_pb2.PeekAnalyticsEventResponse:
        """Returns an analytics event."""
        return await self.workflow.handle_peek_analytics_event(request)

    @rpc_errors
    @retry_transient
    async def ResolveAnalyticsEvents(
        self, request: analytics_v1_analytics_event_query_service_pb2.ResolveAnalyticsEventsRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_analytics_event_query_service_pb2.ResolveAnalyticsEventsResponse:
        """Returns several analytics events at once."""
        return await self.workflow.handle_resolve_analytics_events(request)

    @rpc_errors
    @retry_transient
    async def SuggestAnalyticsEvents(
        self, request: analytics_v1_analytics_event_query_service_pb2.SuggestAnalyticsEventsRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_analytics_event_query_service_pb2.SuggestAnalyticsEventsResponse:
        """Lists analytics events a page at a time."""
        return await self.workflow.handle_suggest_analytics_events(request)

    @rpc_errors
    async def SummarizeAnalyticsEvents(
        self, request: analytics_v1_analytics_event_query_service_pb2.SummarizeAnalyticsEventsRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_analytics_event_query_service_pb2.SummarizeAnalyticsEventsResponse:
        """Summarizes an analytics event."""
        return await self.workflow.handle_summarize_analytics_events(request)
