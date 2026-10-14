"""Answers read-only questions about feature values, for screens and reports."""

from __future__ import annotations

from collections.abc import AsyncIterator

import grpc

from acme.featurestore.v1 import feature_value_query_service_pb2 as featurestore_v1_feature_value_query_service_pb2
from acme.featurestore.v1 import (
    feature_value_query_service_pb2_grpc as featurestore_v1_feature_value_query_service_pb2_grpc,
)

from acme_data.domains.featurestore.dependencies import Dependencies
from acme_data.domains.featurestore.feature_value_query_service_operations import handle_browse_feature_values
from acme_data.domains.featurestore.feature_value_query_service_operations import handle_count_feature_values
from acme_data.domains.featurestore.feature_value_query_service_operations import handle_export_feature_values
from acme_data.domains.featurestore.feature_value_query_service_operations import handle_find_feature_values
from acme_data.domains.featurestore.feature_value_query_service_operations import handle_lookup_feature_value
from acme_data.domains.featurestore.feature_value_query_service_operations import handle_peek_feature_value
from acme_data.domains.featurestore.feature_value_query_service_operations import handle_resolve_feature_values
from acme_data.domains.featurestore.feature_value_query_service_operations import handle_suggest_feature_values
from acme_data.domains.featurestore.feature_value_query_service_operations import handle_summarize_feature_values
from acme_data.platform.rpc import messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors


class FeatureValueQueryServicer(featurestore_v1_feature_value_query_service_pb2_grpc.FeatureValueQueryServiceServicer):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    @retry_transient
    async def BrowseFeatureValues(
        self, request: featurestore_v1_feature_value_query_service_pb2.BrowseFeatureValuesRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_feature_value_query_service_pb2.BrowseFeatureValuesResponse:
        """Lists feature values a page at a time."""
        return await handle_browse_feature_values(self.deps, request)

    @rpc_errors
    @retry_transient
    async def CountFeatureValues(
        self, request: featurestore_v1_feature_value_query_service_pb2.CountFeatureValuesRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_feature_value_query_service_pb2.CountFeatureValuesResponse:
        """Counts feature values by status."""
        return await handle_count_feature_values(self.deps, request)

    @stream_errors
    async def ExportFeatureValues(
        self, request: featurestore_v1_feature_value_query_service_pb2.ExportFeatureValuesRequest, context: grpc.aio.ServicerContext,
    ) -> AsyncIterator[featurestore_v1_feature_value_query_service_pb2.ExportFeatureValuesResponse]:
        """Streams every matching feature value."""
        response = await handle_export_feature_values(self.deps, request)
        for item in messages((response,)):
            yield item

    @rpc_errors
    @retry_transient
    async def FindFeatureValues(
        self, request: featurestore_v1_feature_value_query_service_pb2.FindFeatureValuesRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_feature_value_query_service_pb2.FindFeatureValuesResponse:
        """Lists feature values a page at a time."""
        return await handle_find_feature_values(self.deps, request)

    @rpc_errors
    @retry_transient
    async def LookupFeatureValue(
        self, request: featurestore_v1_feature_value_query_service_pb2.LookupFeatureValueRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_feature_value_query_service_pb2.LookupFeatureValueResponse:
        """Returns a feature value."""
        return await handle_lookup_feature_value(self.deps, request)

    @rpc_errors
    @retry_transient
    async def PeekFeatureValue(
        self, request: featurestore_v1_feature_value_query_service_pb2.PeekFeatureValueRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_feature_value_query_service_pb2.PeekFeatureValueResponse:
        """Returns a feature value."""
        return await handle_peek_feature_value(self.deps, request)

    @rpc_errors
    @retry_transient
    async def ResolveFeatureValues(
        self, request: featurestore_v1_feature_value_query_service_pb2.ResolveFeatureValuesRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_feature_value_query_service_pb2.ResolveFeatureValuesResponse:
        """Returns several feature values at once."""
        return await handle_resolve_feature_values(self.deps, request)

    @rpc_errors
    @retry_transient
    async def SuggestFeatureValues(
        self, request: featurestore_v1_feature_value_query_service_pb2.SuggestFeatureValuesRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_feature_value_query_service_pb2.SuggestFeatureValuesResponse:
        """Lists feature values a page at a time."""
        return await handle_suggest_feature_values(self.deps, request)

    @rpc_errors
    async def SummarizeFeatureValues(
        self, request: featurestore_v1_feature_value_query_service_pb2.SummarizeFeatureValuesRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_feature_value_query_service_pb2.SummarizeFeatureValuesResponse:
        """Summarizes a feature value."""
        return await handle_summarize_feature_values(self.deps, request)
