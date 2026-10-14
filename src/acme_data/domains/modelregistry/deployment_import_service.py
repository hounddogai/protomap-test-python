"""Takes deployments in bulk from partners and legacy systems."""

from __future__ import annotations

from collections.abc import AsyncIterator

import grpc

from acme.modelregistry.v1 import deployment_import_service_pb2 as modelregistry_v1_deployment_import_service_pb2
from acme.modelregistry.v1 import (
    deployment_import_service_pb2_grpc as modelregistry_v1_deployment_import_service_pb2_grpc,
)

from acme_data.domains.modelregistry.dependencies import Dependencies
from acme_data.domains.modelregistry.deployment_import_service_operations import handle_cancel_deployment_import
from acme_data.domains.modelregistry.deployment_import_service_operations import handle_get_deployment_import_status
from acme_data.domains.modelregistry.deployment_import_service_operations import handle_import_deployments
from acme_data.domains.modelregistry.deployment_import_service_operations import handle_list_deployment_imports
from acme_data.domains.modelregistry.deployment_import_service_operations import handle_map_deployment_import_columns
from acme_data.domains.modelregistry.deployment_import_service_operations import handle_retry_deployment_import
from acme_data.domains.modelregistry.deployment_import_service_operations import handle_validate_deployment_import
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors


class DeploymentImportServicer(modelregistry_v1_deployment_import_service_pb2_grpc.DeploymentImportServiceServicer):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    async def CancelDeploymentImport(
        self, request: modelregistry_v1_deployment_import_service_pb2.CancelDeploymentImportRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_deployment_import_service_pb2.CancelDeploymentImportResponse:
        """Cancels a deployment."""
        return await handle_cancel_deployment_import(self.deps, request)

    @rpc_errors
    @retry_transient
    async def GetDeploymentImportStatus(
        self, request: modelregistry_v1_deployment_import_service_pb2.GetDeploymentImportStatusRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_deployment_import_service_pb2.GetDeploymentImportStatusResponse:
        """Returns a deployment."""
        return await handle_get_deployment_import_status(self.deps, request)

    @rpc_errors
    async def ImportDeployments(
        self, requests: AsyncIterator[
            modelregistry_v1_deployment_import_service_pb2.ImportDeploymentsRequest
        ], context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_deployment_import_service_pb2.ImportDeploymentsResponse:
        """Takes a stream of deployments and answers once at the end."""
        response = modelregistry_v1_deployment_import_service_pb2.ImportDeploymentsResponse()
        async for request in requests:
            response.MergeFrom(await handle_import_deployments(self.deps, request))
        return response

    @rpc_errors
    @retry_transient
    async def ListDeploymentImports(
        self, request: modelregistry_v1_deployment_import_service_pb2.ListDeploymentImportsRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_deployment_import_service_pb2.ListDeploymentImportsResponse:
        """Lists deployments a page at a time."""
        return await handle_list_deployment_imports(self.deps, request)

    @rpc_errors
    async def MapDeploymentImportColumns(
        self, request: modelregistry_v1_deployment_import_service_pb2.MapDeploymentImportColumnsRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_deployment_import_service_pb2.MapDeploymentImportColumnsResponse:
        """Maps a deployment."""
        return await handle_map_deployment_import_columns(self.deps, request)

    @rpc_errors
    async def RetryDeploymentImport(
        self, request: modelregistry_v1_deployment_import_service_pb2.RetryDeploymentImportRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_deployment_import_service_pb2.RetryDeploymentImportResponse:
        """Retrys a deployment."""
        return await handle_retry_deployment_import(self.deps, request)

    @rpc_errors
    async def ValidateDeploymentImport(
        self, request: modelregistry_v1_deployment_import_service_pb2.ValidateDeploymentImportRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_deployment_import_service_pb2.ValidateDeploymentImportResponse:
        """Validates a deployment."""
        return await handle_validate_deployment_import(self.deps, request)
