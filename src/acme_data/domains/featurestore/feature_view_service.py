"""Manages feature views: creates, reads, changes, and lists them."""

from __future__ import annotations

from collections.abc import AsyncIterator

import grpc

from acme.featurestore.v1 import feature_view_service_pb2 as featurestore_v1_feature_view_service_pb2
from acme.featurestore.v1 import feature_view_service_pb2_grpc as featurestore_v1_feature_view_service_pb2_grpc

from acme_data.domains.featurestore.dependencies import Dependencies
from acme_data.domains.featurestore.feature_view_service_operations import handle_batch_create_feature_views
from acme_data.domains.featurestore.feature_view_service_operations import handle_batch_get_feature_views
from acme_data.domains.featurestore.feature_view_service_operations import handle_clone_feature_view
from acme_data.domains.featurestore.feature_view_service_operations import handle_create_feature_view
from acme_data.domains.featurestore.feature_view_service_operations import handle_delete_feature_view
from acme_data.domains.featurestore.feature_view_service_operations import handle_get_feature_view
from acme_data.domains.featurestore.feature_view_service_operations import handle_list_feature_views
from acme_data.domains.featurestore.feature_view_service_operations import handle_search_feature_views
from acme_data.domains.featurestore.feature_view_service_operations import handle_update_feature_view
from acme_data.domains.featurestore.feature_view_service_operations import handle_watch_feature_views
from acme_data.platform.rpc import messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors


class FeatureViewServicer(featurestore_v1_feature_view_service_pb2_grpc.FeatureViewServiceServicer):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    async def BatchCreateFeatureViews(
        self, requests: AsyncIterator[
            featurestore_v1_feature_view_service_pb2.BatchCreateFeatureViewsRequest
        ], context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_feature_view_service_pb2.BatchCreateFeatureViewsResponse:
        """Takes a stream of feature views and answers once at the end."""
        response = featurestore_v1_feature_view_service_pb2.BatchCreateFeatureViewsResponse()
        async for request in requests:
            response.MergeFrom(await handle_batch_create_feature_views(self.deps, request))
        return response

    @rpc_errors
    @retry_transient
    async def BatchGetFeatureViews(
        self, request: featurestore_v1_feature_view_service_pb2.BatchGetFeatureViewsRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_feature_view_service_pb2.BatchGetFeatureViewsResponse:
        """Returns several feature views at once."""
        return await handle_batch_get_feature_views(self.deps, request)

    @rpc_errors
    async def CloneFeatureView(
        self, request: featurestore_v1_feature_view_service_pb2.CloneFeatureViewRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_feature_view_service_pb2.CloneFeatureViewResponse:
        """Creates a feature view."""
        return await handle_clone_feature_view(self.deps, request)

    @rpc_errors
    async def CreateFeatureView(
        self, request: featurestore_v1_feature_view_service_pb2.CreateFeatureViewRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_feature_view_service_pb2.CreateFeatureViewResponse:
        """Creates a feature view."""
        return await handle_create_feature_view(self.deps, request)

    @rpc_errors
    async def DeleteFeatureView(
        self, request: featurestore_v1_feature_view_service_pb2.DeleteFeatureViewRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_feature_view_service_pb2.DeleteFeatureViewResponse:
        """Deletes a feature view."""
        return await handle_delete_feature_view(self.deps, request)

    @rpc_errors
    @retry_transient
    async def GetFeatureView(
        self, request: featurestore_v1_feature_view_service_pb2.GetFeatureViewRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_feature_view_service_pb2.GetFeatureViewResponse:
        """Returns a feature view."""
        return await handle_get_feature_view(self.deps, request)

    @rpc_errors
    @retry_transient
    async def ListFeatureViews(
        self, request: featurestore_v1_feature_view_service_pb2.ListFeatureViewsRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_feature_view_service_pb2.ListFeatureViewsResponse:
        """Lists feature views a page at a time."""
        return await handle_list_feature_views(self.deps, request)

    @rpc_errors
    @retry_transient
    async def SearchFeatureViews(
        self, request: featurestore_v1_feature_view_service_pb2.SearchFeatureViewsRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_feature_view_service_pb2.SearchFeatureViewsResponse:
        """Lists feature views a page at a time."""
        return await handle_search_feature_views(self.deps, request)

    @rpc_errors
    async def UpdateFeatureView(
        self, request: featurestore_v1_feature_view_service_pb2.UpdateFeatureViewRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_feature_view_service_pb2.UpdateFeatureViewResponse:
        """Changes a feature view."""
        return await handle_update_feature_view(self.deps, request)

    @stream_errors
    async def WatchFeatureViews(
        self, request: featurestore_v1_feature_view_service_pb2.WatchFeatureViewsRequest, context: grpc.aio.ServicerContext,
    ) -> AsyncIterator[featurestore_v1_feature_view_service_pb2.WatchFeatureViewsResponse]:
        """Streams the changes of feature views as they happen."""
        response = await handle_watch_feature_views(self.deps, request)
        for item in messages((response,)):
            yield item
