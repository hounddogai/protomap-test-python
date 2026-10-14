"""Runs the long-lived workflow that takes an entity from start to finish."""

from __future__ import annotations

from collections.abc import AsyncIterator

import grpc

from acme.featurestore.v1 import entity_workflow_service_pb2 as featurestore_v1_entity_workflow_service_pb2
from acme.featurestore.v1 import entity_workflow_service_pb2_grpc as featurestore_v1_entity_workflow_service_pb2_grpc

from acme_data.domains.featurestore.dependencies import Dependencies
from acme_data.domains.featurestore.entity_workflow_service_operations import handle_advance_entity_workflow
from acme_data.domains.featurestore.entity_workflow_service_operations import handle_inspect_entity_workflow
from acme_data.domains.featurestore.entity_workflow_service_operations import handle_pause_entity_workflow
from acme_data.domains.featurestore.entity_workflow_service_operations import handle_resume_entity_workflow
from acme_data.domains.featurestore.entity_workflow_service_operations import handle_retry_entity_workflow
from acme_data.domains.featurestore.entity_workflow_service_operations import handle_start_entity_workflow
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors


class EntityWorkflowServicer(featurestore_v1_entity_workflow_service_pb2_grpc.EntityWorkflowServiceServicer):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    async def AdvanceEntityWorkflow(
        self, request: featurestore_v1_entity_workflow_service_pb2.AdvanceEntityWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_entity_workflow_service_pb2.AdvanceEntityWorkflowResponse:
        """Advances an entity."""
        return await handle_advance_entity_workflow(self.deps, request)

    @rpc_errors
    @retry_transient
    async def InspectEntityWorkflow(
        self, request: featurestore_v1_entity_workflow_service_pb2.InspectEntityWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_entity_workflow_service_pb2.InspectEntityWorkflowResponse:
        """Returns an entity."""
        return await handle_inspect_entity_workflow(self.deps, request)

    @rpc_errors
    async def PauseEntityWorkflow(
        self, request: featurestore_v1_entity_workflow_service_pb2.PauseEntityWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_entity_workflow_service_pb2.PauseEntityWorkflowResponse:
        """Pauses an entity."""
        return await handle_pause_entity_workflow(self.deps, request)

    @rpc_errors
    async def ResumeEntityWorkflow(
        self, request: featurestore_v1_entity_workflow_service_pb2.ResumeEntityWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_entity_workflow_service_pb2.ResumeEntityWorkflowResponse:
        """Resumes an entity."""
        return await handle_resume_entity_workflow(self.deps, request)

    @rpc_errors
    async def RetryEntityWorkflow(
        self, request: featurestore_v1_entity_workflow_service_pb2.RetryEntityWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_entity_workflow_service_pb2.RetryEntityWorkflowResponse:
        """Retrys an entity."""
        return await handle_retry_entity_workflow(self.deps, request)

    @rpc_errors
    async def StartEntityWorkflow(
        self, request: featurestore_v1_entity_workflow_service_pb2.StartEntityWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_entity_workflow_service_pb2.StartEntityWorkflowResponse:
        """Starts an entity."""
        return await handle_start_entity_workflow(self.deps, request)
