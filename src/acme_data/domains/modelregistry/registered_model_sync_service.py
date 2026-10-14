"""Keeps registered models in step with the systems of record in other regions."""

from __future__ import annotations

from collections.abc import AsyncIterator

import grpc

from acme.modelregistry.v1 import (
    registered_model_sync_service_pb2 as modelregistry_v1_registered_model_sync_service_pb2,
)
from acme.modelregistry.v1 import (
    registered_model_sync_service_pb2_grpc as modelregistry_v1_registered_model_sync_service_pb2_grpc,
)

from acme_data.domains.modelregistry.dependencies import Dependencies
from acme_data.domains.modelregistry.registered_model_sync_service_operations import (
    handle_list_registered_model_conflicts,
)
from acme_data.domains.modelregistry.registered_model_sync_service_operations import handle_pull_registered_models
from acme_data.domains.modelregistry.registered_model_sync_service_operations import handle_push_registered_model
from acme_data.domains.modelregistry.registered_model_sync_service_operations import handle_reconcile_registered_models
from acme_data.domains.modelregistry.registered_model_sync_service_operations import (
    handle_resolve_registered_model_conflict,
)
from acme_data.domains.modelregistry.registered_model_sync_service_operations import (
    handle_stream_registered_model_changes,
)
from acme_data.domains.modelregistry.registered_model_sync_service_operations import handle_sync_registered_models
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors


class RegisteredModelSyncServicer(
    modelregistry_v1_registered_model_sync_service_pb2_grpc.RegisteredModelSyncServiceServicer
):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    @retry_transient
    async def ListRegisteredModelConflicts(
        self, request: modelregistry_v1_registered_model_sync_service_pb2.ListRegisteredModelConflictsRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_registered_model_sync_service_pb2.ListRegisteredModelConflictsResponse:
        """Lists registered models a page at a time."""
        return await handle_list_registered_model_conflicts(self.deps, request)

    @rpc_errors
    async def PullRegisteredModels(
        self, request: modelregistry_v1_registered_model_sync_service_pb2.PullRegisteredModelsRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_registered_model_sync_service_pb2.PullRegisteredModelsResponse:
        """Pulls a registered model."""
        return await handle_pull_registered_models(self.deps, request)

    @rpc_errors
    async def PushRegisteredModel(
        self, request: modelregistry_v1_registered_model_sync_service_pb2.PushRegisteredModelRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_registered_model_sync_service_pb2.PushRegisteredModelResponse:
        """Pushs a registered model."""
        return await handle_push_registered_model(self.deps, request)

    @rpc_errors
    async def ReconcileRegisteredModels(
        self, request: modelregistry_v1_registered_model_sync_service_pb2.ReconcileRegisteredModelsRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_registered_model_sync_service_pb2.ReconcileRegisteredModelsResponse:
        """Reconciles a registered model."""
        return await handle_reconcile_registered_models(self.deps, request)

    @rpc_errors
    async def ResolveRegisteredModelConflict(
        self, request: modelregistry_v1_registered_model_sync_service_pb2.ResolveRegisteredModelConflictRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_registered_model_sync_service_pb2.ResolveRegisteredModelConflictResponse:
        """Resolves a registered model."""
        return await handle_resolve_registered_model_conflict(self.deps, request)

    @stream_errors
    async def StreamRegisteredModelChanges(
        self, requests: AsyncIterator[
            modelregistry_v1_registered_model_sync_service_pb2.StreamRegisteredModelChangesRequest
        ], context: grpc.aio.ServicerContext,
    ) -> AsyncIterator[modelregistry_v1_registered_model_sync_service_pb2.StreamRegisteredModelChangesResponse]:
        """Exchanges changes of registered models with a peer."""
        async for request in requests:
            yield await handle_stream_registered_model_changes(self.deps, request)

    @rpc_errors
    async def SyncRegisteredModels(
        self, request: modelregistry_v1_registered_model_sync_service_pb2.SyncRegisteredModelsRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_registered_model_sync_service_pb2.SyncRegisteredModelsResponse:
        """Syncs a registered model."""
        return await handle_sync_registered_models(self.deps, request)
