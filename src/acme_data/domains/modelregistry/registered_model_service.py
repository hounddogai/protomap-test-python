"""Manages registered models: creates, reads, changes, and lists them."""

from __future__ import annotations

from collections.abc import AsyncIterator

import grpc

from acme.modelregistry.v1 import registered_model_service_pb2 as modelregistry_v1_registered_model_service_pb2
from acme.modelregistry.v1 import (
    registered_model_service_pb2_grpc as modelregistry_v1_registered_model_service_pb2_grpc,
)

from acme_data.domains.modelregistry.dependencies import Dependencies
from acme_data.domains.modelregistry.registered_model_service_workflow import RegisteredModelServicerWorkflow
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors


class RegisteredModelServicer(modelregistry_v1_registered_model_service_pb2_grpc.RegisteredModelServiceServicer):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps
        self.workflow = RegisteredModelServicerWorkflow(deps)

    @rpc_errors
    async def BatchCreateRegisteredModels(
        self, requests: AsyncIterator[
            modelregistry_v1_registered_model_service_pb2.BatchCreateRegisteredModelsRequest
        ], context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_registered_model_service_pb2.BatchCreateRegisteredModelsResponse:
        """Takes a stream of registered models and answers once at the end."""
        response = modelregistry_v1_registered_model_service_pb2.BatchCreateRegisteredModelsResponse()
        async for request in requests:
            response.MergeFrom(await self.workflow.handle_batch_create_registered_models(request))
        return response

    @rpc_errors
    @retry_transient
    async def BatchGetRegisteredModels(
        self, request: modelregistry_v1_registered_model_service_pb2.BatchGetRegisteredModelsRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_registered_model_service_pb2.BatchGetRegisteredModelsResponse:
        """Returns several registered models at once."""
        return await self.workflow.handle_batch_get_registered_models(request)

    @rpc_errors
    async def CloneRegisteredModel(
        self, request: modelregistry_v1_registered_model_service_pb2.CloneRegisteredModelRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_registered_model_service_pb2.CloneRegisteredModelResponse:
        """Creates a registered model."""
        return await self.workflow.handle_clone_registered_model(request)

    @rpc_errors
    async def CreateRegisteredModel(
        self, request: modelregistry_v1_registered_model_service_pb2.CreateRegisteredModelRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_registered_model_service_pb2.CreateRegisteredModelResponse:
        """Creates a registered model."""
        return await self.workflow.handle_create_registered_model(request)

    @rpc_errors
    async def DeleteRegisteredModel(
        self, request: modelregistry_v1_registered_model_service_pb2.DeleteRegisteredModelRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_registered_model_service_pb2.DeleteRegisteredModelResponse:
        """Deletes a registered model."""
        return await self.workflow.handle_delete_registered_model(request)

    @rpc_errors
    @retry_transient
    async def GetRegisteredModel(
        self, request: modelregistry_v1_registered_model_service_pb2.GetRegisteredModelRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_registered_model_service_pb2.GetRegisteredModelResponse:
        """Returns a registered model."""
        return await self.workflow.handle_get_registered_model(request)

    @rpc_errors
    async def UpdateRegisteredModel(
        self, request: modelregistry_v1_registered_model_service_pb2.UpdateRegisteredModelRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_registered_model_service_pb2.UpdateRegisteredModelResponse:
        """Changes a registered model."""
        return await self.workflow.handle_update_registered_model(request)
