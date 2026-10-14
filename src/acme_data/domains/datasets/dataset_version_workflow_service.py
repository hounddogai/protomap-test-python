"""Runs the long-lived workflow that takes a dataset version from start to finish."""

from __future__ import annotations

from collections.abc import AsyncIterator

import grpc

from acme.datasets.v1 import dataset_version_workflow_service_pb2 as datasets_v1_dataset_version_workflow_service_pb2
from acme.datasets.v1 import (
    dataset_version_workflow_service_pb2_grpc as datasets_v1_dataset_version_workflow_service_pb2_grpc,
)

from acme_data.domains.datasets.dataset_version_workflow_service_operations import (
    handle_advance_dataset_version_workflow,
)
from acme_data.domains.datasets.dataset_version_workflow_service_operations import (
    handle_cancel_dataset_version_workflow,
)
from acme_data.domains.datasets.dataset_version_workflow_service_operations import (
    handle_inspect_dataset_version_workflow,
)
from acme_data.domains.datasets.dataset_version_workflow_service_operations import handle_pause_dataset_version_workflow
from acme_data.domains.datasets.dataset_version_workflow_service_operations import (
    handle_resume_dataset_version_workflow,
)
from acme_data.domains.datasets.dataset_version_workflow_service_operations import handle_retry_dataset_version_workflow
from acme_data.domains.datasets.dataset_version_workflow_service_operations import handle_start_dataset_version_workflow
from acme_data.domains.datasets.dependencies import Dependencies
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors


class DatasetVersionWorkflowServicer(
    datasets_v1_dataset_version_workflow_service_pb2_grpc.DatasetVersionWorkflowServiceServicer
):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    async def AdvanceDatasetVersionWorkflow(
        self, request: datasets_v1_dataset_version_workflow_service_pb2.AdvanceDatasetVersionWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> datasets_v1_dataset_version_workflow_service_pb2.AdvanceDatasetVersionWorkflowResponse:
        """Advances a dataset version."""
        return await handle_advance_dataset_version_workflow(self.deps, request)

    @rpc_errors
    async def CancelDatasetVersionWorkflow(
        self, request: datasets_v1_dataset_version_workflow_service_pb2.CancelDatasetVersionWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> datasets_v1_dataset_version_workflow_service_pb2.CancelDatasetVersionWorkflowResponse:
        """Cancels a dataset version."""
        return await handle_cancel_dataset_version_workflow(self.deps, request)

    @rpc_errors
    @retry_transient
    async def InspectDatasetVersionWorkflow(
        self, request: datasets_v1_dataset_version_workflow_service_pb2.InspectDatasetVersionWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> datasets_v1_dataset_version_workflow_service_pb2.InspectDatasetVersionWorkflowResponse:
        """Returns a dataset version."""
        return await handle_inspect_dataset_version_workflow(self.deps, request)

    @rpc_errors
    async def PauseDatasetVersionWorkflow(
        self, request: datasets_v1_dataset_version_workflow_service_pb2.PauseDatasetVersionWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> datasets_v1_dataset_version_workflow_service_pb2.PauseDatasetVersionWorkflowResponse:
        """Pauses a dataset version."""
        return await handle_pause_dataset_version_workflow(self.deps, request)

    @rpc_errors
    async def ResumeDatasetVersionWorkflow(
        self, request: datasets_v1_dataset_version_workflow_service_pb2.ResumeDatasetVersionWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> datasets_v1_dataset_version_workflow_service_pb2.ResumeDatasetVersionWorkflowResponse:
        """Resumes a dataset version."""
        return await handle_resume_dataset_version_workflow(self.deps, request)

    @rpc_errors
    async def RetryDatasetVersionWorkflow(
        self, request: datasets_v1_dataset_version_workflow_service_pb2.RetryDatasetVersionWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> datasets_v1_dataset_version_workflow_service_pb2.RetryDatasetVersionWorkflowResponse:
        """Retrys a dataset version."""
        return await handle_retry_dataset_version_workflow(self.deps, request)

    @rpc_errors
    async def StartDatasetVersionWorkflow(
        self, request: datasets_v1_dataset_version_workflow_service_pb2.StartDatasetVersionWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> datasets_v1_dataset_version_workflow_service_pb2.StartDatasetVersionWorkflowResponse:
        """Starts a dataset version."""
        return await handle_start_dataset_version_workflow(self.deps, request)
