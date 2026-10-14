"""Takes entities in bulk from partners and legacy systems."""

from __future__ import annotations

from collections.abc import AsyncIterator

import grpc

from acme.featurestore.v1 import entity_import_service_pb2 as featurestore_v1_entity_import_service_pb2
from acme.featurestore.v1 import entity_import_service_pb2_grpc as featurestore_v1_entity_import_service_pb2_grpc

from acme_data.domains.featurestore.dependencies import Dependencies
from acme_data.domains.featurestore.entity_import_service_operations import handle_cancel_entity_import
from acme_data.domains.featurestore.entity_import_service_operations import handle_get_entity_import_status
from acme_data.domains.featurestore.entity_import_service_operations import handle_import_entities
from acme_data.domains.featurestore.entity_import_service_operations import handle_list_entity_imports
from acme_data.domains.featurestore.entity_import_service_operations import handle_map_entity_import_columns
from acme_data.domains.featurestore.entity_import_service_operations import handle_retry_entity_import
from acme_data.domains.featurestore.entity_import_service_operations import handle_validate_entity_import
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors


class EntityImportServicer(featurestore_v1_entity_import_service_pb2_grpc.EntityImportServiceServicer):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    async def CancelEntityImport(
        self, request: featurestore_v1_entity_import_service_pb2.CancelEntityImportRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_entity_import_service_pb2.CancelEntityImportResponse:
        """Cancels an entity."""
        return await handle_cancel_entity_import(self.deps, request)

    @rpc_errors
    @retry_transient
    async def GetEntityImportStatus(
        self, request: featurestore_v1_entity_import_service_pb2.GetEntityImportStatusRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_entity_import_service_pb2.GetEntityImportStatusResponse:
        """Returns an entity."""
        return await handle_get_entity_import_status(self.deps, request)

    @rpc_errors
    async def ImportEntities(
        self, requests: AsyncIterator[
            featurestore_v1_entity_import_service_pb2.ImportEntitiesRequest
        ], context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_entity_import_service_pb2.ImportEntitiesResponse:
        """Takes a stream of entities and answers once at the end."""
        response = featurestore_v1_entity_import_service_pb2.ImportEntitiesResponse()
        async for request in requests:
            response.MergeFrom(await handle_import_entities(self.deps, request))
        return response

    @rpc_errors
    @retry_transient
    async def ListEntityImports(
        self, request: featurestore_v1_entity_import_service_pb2.ListEntityImportsRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_entity_import_service_pb2.ListEntityImportsResponse:
        """Lists entities a page at a time."""
        return await handle_list_entity_imports(self.deps, request)

    @rpc_errors
    async def MapEntityImportColumns(
        self, request: featurestore_v1_entity_import_service_pb2.MapEntityImportColumnsRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_entity_import_service_pb2.MapEntityImportColumnsResponse:
        """Maps an entity."""
        return await handle_map_entity_import_columns(self.deps, request)

    @rpc_errors
    async def RetryEntityImport(
        self, request: featurestore_v1_entity_import_service_pb2.RetryEntityImportRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_entity_import_service_pb2.RetryEntityImportResponse:
        """Retrys an entity."""
        return await handle_retry_entity_import(self.deps, request)

    @rpc_errors
    async def ValidateEntityImport(
        self, request: featurestore_v1_entity_import_service_pb2.ValidateEntityImportRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_entity_import_service_pb2.ValidateEntityImportResponse:
        """Validates an entity."""
        return await handle_validate_entity_import(self.deps, request)
