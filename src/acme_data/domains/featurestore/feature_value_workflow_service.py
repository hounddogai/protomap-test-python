"""Runs the long-lived workflow that takes a feature value from start to finish."""

from __future__ import annotations

from collections.abc import AsyncIterator

import grpc

from acme.featurestore.v1 import (
    feature_value_workflow_service_pb2 as featurestore_v1_feature_value_workflow_service_pb2,
)
from acme.featurestore.v1 import (
    feature_value_workflow_service_pb2_grpc as featurestore_v1_feature_value_workflow_service_pb2_grpc,
)

from acme_data.domains.featurestore.dependencies import Dependencies
from acme_data.domains.featurestore.feature_value_workflow_service_workflow import FeatureValueWorkflowServicerWorkflow
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors


class FeatureValueWorkflowServicer(
    featurestore_v1_feature_value_workflow_service_pb2_grpc.FeatureValueWorkflowServiceServicer
):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps
        self.workflow = FeatureValueWorkflowServicerWorkflow(deps)

    @rpc_errors
    async def AdvanceFeatureValueWorkflow(
        self, request: featurestore_v1_feature_value_workflow_service_pb2.AdvanceFeatureValueWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_feature_value_workflow_service_pb2.AdvanceFeatureValueWorkflowResponse:
        """Advances a feature value."""
        return await self.workflow.handle_advance_feature_value_workflow(request)

    @rpc_errors
    async def CancelFeatureValueWorkflow(
        self, request: featurestore_v1_feature_value_workflow_service_pb2.CancelFeatureValueWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_feature_value_workflow_service_pb2.CancelFeatureValueWorkflowResponse:
        """Cancels a feature value."""
        return await self.workflow.handle_cancel_feature_value_workflow(request)

    @rpc_errors
    @retry_transient
    async def InspectFeatureValueWorkflow(
        self, request: featurestore_v1_feature_value_workflow_service_pb2.InspectFeatureValueWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_feature_value_workflow_service_pb2.InspectFeatureValueWorkflowResponse:
        """Returns a feature value."""
        return await self.workflow.handle_inspect_feature_value_workflow(request)

    @rpc_errors
    @retry_transient
    async def ListFeatureValueWorkflows(
        self, request: featurestore_v1_feature_value_workflow_service_pb2.ListFeatureValueWorkflowsRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_feature_value_workflow_service_pb2.ListFeatureValueWorkflowsResponse:
        """Lists feature values a page at a time."""
        return await self.workflow.handle_list_feature_value_workflows(request)

    @rpc_errors
    async def ResumeFeatureValueWorkflow(
        self, request: featurestore_v1_feature_value_workflow_service_pb2.ResumeFeatureValueWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_feature_value_workflow_service_pb2.ResumeFeatureValueWorkflowResponse:
        """Resumes a feature value."""
        return await self.workflow.handle_resume_feature_value_workflow(request)

    @rpc_errors
    async def RetryFeatureValueWorkflow(
        self, request: featurestore_v1_feature_value_workflow_service_pb2.RetryFeatureValueWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_feature_value_workflow_service_pb2.RetryFeatureValueWorkflowResponse:
        """Retrys a feature value."""
        return await self.workflow.handle_retry_feature_value_workflow(request)

    @rpc_errors
    async def SignalFeatureValueWorkflow(
        self, request: featurestore_v1_feature_value_workflow_service_pb2.SignalFeatureValueWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_feature_value_workflow_service_pb2.SignalFeatureValueWorkflowResponse:
        """Signals a feature value."""
        return await self.workflow.handle_signal_feature_value_workflow(request)

    @rpc_errors
    async def StartFeatureValueWorkflow(
        self, request: featurestore_v1_feature_value_workflow_service_pb2.StartFeatureValueWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_feature_value_workflow_service_pb2.StartFeatureValueWorkflowResponse:
        """Starts a feature value."""
        return await self.workflow.handle_start_feature_value_workflow(request)
