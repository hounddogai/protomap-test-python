"""Moves a labeling task between the states of its lifecycle."""

from __future__ import annotations

from collections.abc import AsyncIterator

import grpc

from acme.labeling.v1 import labeling_task_lifecycle_service_pb2 as labeling_v1_labeling_task_lifecycle_service_pb2
from acme.labeling.v1 import (
    labeling_task_lifecycle_service_pb2_grpc as labeling_v1_labeling_task_lifecycle_service_pb2_grpc,
)

from acme_data.domains.labeling.dependencies import Dependencies
from acme_data.domains.labeling.labeling_task_lifecycle_service_workflow import LabelingTaskLifecycleServicerWorkflow
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors


class LabelingTaskLifecycleServicer(
    labeling_v1_labeling_task_lifecycle_service_pb2_grpc.LabelingTaskLifecycleServiceServicer
):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps
        self.workflow = LabelingTaskLifecycleServicerWorkflow(deps)

    @rpc_errors
    async def ActivateLabelingTask(
        self, request: labeling_v1_labeling_task_lifecycle_service_pb2.ActivateLabelingTaskRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_labeling_task_lifecycle_service_pb2.ActivateLabelingTaskResponse:
        """Activates a labeling task."""
        return await self.workflow.handle_activate_labeling_task(request)

    @rpc_errors
    async def ExpireLabelingTask(
        self, request: labeling_v1_labeling_task_lifecycle_service_pb2.ExpireLabelingTaskRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_labeling_task_lifecycle_service_pb2.ExpireLabelingTaskResponse:
        """Expires a labeling task."""
        return await self.workflow.handle_expire_labeling_task(request)

    @rpc_errors
    @retry_transient
    async def GetLabelingTaskLifecycle(
        self, request: labeling_v1_labeling_task_lifecycle_service_pb2.GetLabelingTaskLifecycleRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_labeling_task_lifecycle_service_pb2.GetLabelingTaskLifecycleResponse:
        """Returns a labeling task."""
        return await self.workflow.handle_get_labeling_task_lifecycle(request)

    @rpc_errors
    async def ReinstateLabelingTask(
        self, request: labeling_v1_labeling_task_lifecycle_service_pb2.ReinstateLabelingTaskRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_labeling_task_lifecycle_service_pb2.ReinstateLabelingTaskResponse:
        """Reinstates a labeling task."""
        return await self.workflow.handle_reinstate_labeling_task(request)

    @rpc_errors
    async def RenewLabelingTask(
        self, request: labeling_v1_labeling_task_lifecycle_service_pb2.RenewLabelingTaskRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_labeling_task_lifecycle_service_pb2.RenewLabelingTaskResponse:
        """Renews a labeling task."""
        return await self.workflow.handle_renew_labeling_task(request)

    @rpc_errors
    async def SuspendLabelingTask(
        self, request: labeling_v1_labeling_task_lifecycle_service_pb2.SuspendLabelingTaskRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_labeling_task_lifecycle_service_pb2.SuspendLabelingTaskResponse:
        """Suspends a labeling task."""
        return await self.workflow.handle_suspend_labeling_task(request)

    @rpc_errors
    async def TerminateLabelingTask(
        self, request: labeling_v1_labeling_task_lifecycle_service_pb2.TerminateLabelingTaskRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_labeling_task_lifecycle_service_pb2.TerminateLabelingTaskResponse:
        """Terminates a labeling task."""
        return await self.workflow.handle_terminate_labeling_task(request)
