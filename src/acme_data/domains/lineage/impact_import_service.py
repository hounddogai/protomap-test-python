"""Takes impacts in bulk from partners and legacy systems."""

from __future__ import annotations

from collections.abc import AsyncIterator

import grpc

from acme.lineage.v1 import impact_import_service_pb2 as lineage_v1_impact_import_service_pb2
from acme.lineage.v1 import impact_import_service_pb2_grpc as lineage_v1_impact_import_service_pb2_grpc

from acme_data.domains.lineage.dependencies import Dependencies
from acme_data.domains.lineage.impact_import_service_operations import handle_cancel_impact_import
from acme_data.domains.lineage.impact_import_service_operations import handle_get_impact_import_status
from acme_data.domains.lineage.impact_import_service_operations import handle_import_impacts
from acme_data.domains.lineage.impact_import_service_operations import handle_list_impact_imports
from acme_data.domains.lineage.impact_import_service_operations import handle_map_impact_import_columns
from acme_data.domains.lineage.impact_import_service_operations import handle_validate_impact_import
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors


class ImpactImportServicer(lineage_v1_impact_import_service_pb2_grpc.ImpactImportServiceServicer):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    async def CancelImpactImport(
        self, request: lineage_v1_impact_import_service_pb2.CancelImpactImportRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_impact_import_service_pb2.CancelImpactImportResponse:
        """Cancels an impact."""
        return await handle_cancel_impact_import(self.deps, request)

    @rpc_errors
    @retry_transient
    async def GetImpactImportStatus(
        self, request: lineage_v1_impact_import_service_pb2.GetImpactImportStatusRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_impact_import_service_pb2.GetImpactImportStatusResponse:
        """Returns an impact."""
        return await handle_get_impact_import_status(self.deps, request)

    @rpc_errors
    async def ImportImpacts(
        self, requests: AsyncIterator[
            lineage_v1_impact_import_service_pb2.ImportImpactsRequest
        ], context: grpc.aio.ServicerContext,
    ) -> lineage_v1_impact_import_service_pb2.ImportImpactsResponse:
        """Takes a stream of impacts and answers once at the end."""
        response = lineage_v1_impact_import_service_pb2.ImportImpactsResponse()
        async for request in requests:
            response.MergeFrom(await handle_import_impacts(self.deps, request))
        return response

    @rpc_errors
    @retry_transient
    async def ListImpactImports(
        self, request: lineage_v1_impact_import_service_pb2.ListImpactImportsRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_impact_import_service_pb2.ListImpactImportsResponse:
        """Lists impacts a page at a time."""
        return await handle_list_impact_imports(self.deps, request)

    @rpc_errors
    async def MapImpactImportColumns(
        self, request: lineage_v1_impact_import_service_pb2.MapImpactImportColumnsRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_impact_import_service_pb2.MapImpactImportColumnsResponse:
        """Maps an impact."""
        return await handle_map_impact_import_columns(self.deps, request)

    @rpc_errors
    async def ValidateImpactImport(
        self, request: lineage_v1_impact_import_service_pb2.ValidateImpactImportRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_impact_import_service_pb2.ValidateImpactImportResponse:
        """Validates an impact."""
        return await handle_validate_impact_import(self.deps, request)
