"""Routes registered models through approval, with escalation and delegation."""

from __future__ import annotations

from collections.abc import AsyncIterator

import grpc

from acme.modelregistry.v1 import (
    registered_model_approval_service_pb2 as modelregistry_v1_registered_model_approval_service_pb2,
)
from acme.modelregistry.v1 import (
    registered_model_approval_service_pb2_grpc as modelregistry_v1_registered_model_approval_service_pb2_grpc,
)

from acme_data.domains.modelregistry.dependencies import Dependencies
from acme_data.domains.modelregistry.registered_model_approval_service_workflow import (
    RegisteredModelApprovalServicerWorkflow,
)
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors


class RegisteredModelApprovalServicer(
    modelregistry_v1_registered_model_approval_service_pb2_grpc.RegisteredModelApprovalServiceServicer
):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps
        self.workflow = RegisteredModelApprovalServicerWorkflow(deps)

    @rpc_errors
    async def ApproveRegisteredModel(
        self, request: modelregistry_v1_registered_model_approval_service_pb2.ApproveRegisteredModelRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_registered_model_approval_service_pb2.ApproveRegisteredModelResponse:
        """Approves a registered model."""
        return await self.workflow.handle_approve_registered_model(request)

    @rpc_errors
    async def CommentRegisteredModelApproval(
        self, request: modelregistry_v1_registered_model_approval_service_pb2.CommentRegisteredModelApprovalRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_registered_model_approval_service_pb2.CommentRegisteredModelApprovalResponse:
        """Comments a registered model."""
        return await self.workflow.handle_comment_registered_model_approval(request)

    @rpc_errors
    @retry_transient
    async def GetRegisteredModelApprovalStatus(
        self, request: modelregistry_v1_registered_model_approval_service_pb2.GetRegisteredModelApprovalStatusRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_registered_model_approval_service_pb2.GetRegisteredModelApprovalStatusResponse:
        """Returns a registered model."""
        return await self.workflow.handle_get_registered_model_approval_status(request)

    @rpc_errors
    @retry_transient
    async def ListPendingRegisteredModels(
        self, request: modelregistry_v1_registered_model_approval_service_pb2.ListPendingRegisteredModelsRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_registered_model_approval_service_pb2.ListPendingRegisteredModelsResponse:
        """Lists registered models a page at a time."""
        return await self.workflow.handle_list_pending_registered_models(request)

    @rpc_errors
    async def RecallRegisteredModel(
        self, request: modelregistry_v1_registered_model_approval_service_pb2.RecallRegisteredModelRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_registered_model_approval_service_pb2.RecallRegisteredModelResponse:
        """Recalls a registered model."""
        return await self.workflow.handle_recall_registered_model(request)

    @rpc_errors
    async def RejectRegisteredModel(
        self, request: modelregistry_v1_registered_model_approval_service_pb2.RejectRegisteredModelRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_registered_model_approval_service_pb2.RejectRegisteredModelResponse:
        """Rejects a registered model."""
        return await self.workflow.handle_reject_registered_model(request)

    @rpc_errors
    async def SubmitRegisteredModel(
        self, request: modelregistry_v1_registered_model_approval_service_pb2.SubmitRegisteredModelRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_registered_model_approval_service_pb2.SubmitRegisteredModelResponse:
        """Submits a registered model."""
        return await self.workflow.handle_submit_registered_model(request)
