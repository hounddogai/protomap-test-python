"""Answers read-only questions about model versions, for screens and reports."""

from __future__ import annotations

from collections.abc import AsyncIterator

import grpc

from acme.modelregistry.v1 import model_version_query_service_pb2 as modelregistry_v1_model_version_query_service_pb2
from acme.modelregistry.v1 import (
    model_version_query_service_pb2_grpc as modelregistry_v1_model_version_query_service_pb2_grpc,
)

from acme_data.domains.modelregistry.dependencies import Dependencies
from acme_data.domains.modelregistry.model_version_query_service_workflow import ModelVersionQueryServicerWorkflow
from acme_data.platform.rpc import messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors


class ModelVersionQueryServicer(modelregistry_v1_model_version_query_service_pb2_grpc.ModelVersionQueryServiceServicer):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps
        self.workflow = ModelVersionQueryServicerWorkflow(deps)

    @rpc_errors
    @retry_transient
    async def BrowseModelVersions(
        self, request: modelregistry_v1_model_version_query_service_pb2.BrowseModelVersionsRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_model_version_query_service_pb2.BrowseModelVersionsResponse:
        """Lists model versions a page at a time."""
        return await self.workflow.handle_browse_model_versions(request)

    @rpc_errors
    @retry_transient
    async def CountModelVersions(
        self, request: modelregistry_v1_model_version_query_service_pb2.CountModelVersionsRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_model_version_query_service_pb2.CountModelVersionsResponse:
        """Counts model versions by status."""
        return await self.workflow.handle_count_model_versions(request)

    @stream_errors
    async def ExportModelVersions(
        self, request: modelregistry_v1_model_version_query_service_pb2.ExportModelVersionsRequest, context: grpc.aio.ServicerContext,
    ) -> AsyncIterator[modelregistry_v1_model_version_query_service_pb2.ExportModelVersionsResponse]:
        """Streams every matching model version."""
        response = await self.workflow.handle_export_model_versions(request)
        for item in messages((response,)):
            yield item

    @rpc_errors
    @retry_transient
    async def LookupModelVersion(
        self, request: modelregistry_v1_model_version_query_service_pb2.LookupModelVersionRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_model_version_query_service_pb2.LookupModelVersionResponse:
        """Returns a model version."""
        return await self.workflow.handle_lookup_model_version(request)

    @rpc_errors
    @retry_transient
    async def PeekModelVersion(
        self, request: modelregistry_v1_model_version_query_service_pb2.PeekModelVersionRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_model_version_query_service_pb2.PeekModelVersionResponse:
        """Returns a model version."""
        return await self.workflow.handle_peek_model_version(request)

    @rpc_errors
    @retry_transient
    async def SuggestModelVersions(
        self, request: modelregistry_v1_model_version_query_service_pb2.SuggestModelVersionsRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_model_version_query_service_pb2.SuggestModelVersionsResponse:
        """Lists model versions a page at a time."""
        return await self.workflow.handle_suggest_model_versions(request)

    @rpc_errors
    async def SummarizeModelVersions(
        self, request: modelregistry_v1_model_version_query_service_pb2.SummarizeModelVersionsRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_model_version_query_service_pb2.SummarizeModelVersionsResponse:
        """Summarizes a model version."""
        return await self.workflow.handle_summarize_model_versions(request)
