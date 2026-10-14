"""Runs the long-lived workflow that takes a detector from start to finish."""

from __future__ import annotations

from collections.abc import AsyncIterator

import grpc

from acme.anomalies.v1 import detector_workflow_service_pb2 as anomalies_v1_detector_workflow_service_pb2
from acme.anomalies.v1 import detector_workflow_service_pb2_grpc as anomalies_v1_detector_workflow_service_pb2_grpc

from acme_data.domains.anomalies.dependencies import Dependencies
from acme_data.domains.anomalies.detector_workflow_service_operations import handle_advance_detector_workflow
from acme_data.domains.anomalies.detector_workflow_service_operations import handle_cancel_detector_workflow
from acme_data.domains.anomalies.detector_workflow_service_operations import handle_inspect_detector_workflow
from acme_data.domains.anomalies.detector_workflow_service_operations import handle_list_detector_workflows
from acme_data.domains.anomalies.detector_workflow_service_operations import handle_retry_detector_workflow
from acme_data.domains.anomalies.detector_workflow_service_operations import handle_signal_detector_workflow
from acme_data.domains.anomalies.detector_workflow_service_operations import handle_start_detector_workflow
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors


class DetectorWorkflowServicer(anomalies_v1_detector_workflow_service_pb2_grpc.DetectorWorkflowServiceServicer):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    async def AdvanceDetectorWorkflow(
        self, request: anomalies_v1_detector_workflow_service_pb2.AdvanceDetectorWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> anomalies_v1_detector_workflow_service_pb2.AdvanceDetectorWorkflowResponse:
        """Advances a detector."""
        return await handle_advance_detector_workflow(self.deps, request)

    @rpc_errors
    async def CancelDetectorWorkflow(
        self, request: anomalies_v1_detector_workflow_service_pb2.CancelDetectorWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> anomalies_v1_detector_workflow_service_pb2.CancelDetectorWorkflowResponse:
        """Cancels a detector."""
        return await handle_cancel_detector_workflow(self.deps, request)

    @rpc_errors
    @retry_transient
    async def InspectDetectorWorkflow(
        self, request: anomalies_v1_detector_workflow_service_pb2.InspectDetectorWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> anomalies_v1_detector_workflow_service_pb2.InspectDetectorWorkflowResponse:
        """Returns a detector."""
        return await handle_inspect_detector_workflow(self.deps, request)

    @rpc_errors
    @retry_transient
    async def ListDetectorWorkflows(
        self, request: anomalies_v1_detector_workflow_service_pb2.ListDetectorWorkflowsRequest, context: grpc.aio.ServicerContext,
    ) -> anomalies_v1_detector_workflow_service_pb2.ListDetectorWorkflowsResponse:
        """Lists detectors a page at a time."""
        return await handle_list_detector_workflows(self.deps, request)

    @rpc_errors
    async def RetryDetectorWorkflow(
        self, request: anomalies_v1_detector_workflow_service_pb2.RetryDetectorWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> anomalies_v1_detector_workflow_service_pb2.RetryDetectorWorkflowResponse:
        """Retrys a detector."""
        return await handle_retry_detector_workflow(self.deps, request)

    @rpc_errors
    async def SignalDetectorWorkflow(
        self, request: anomalies_v1_detector_workflow_service_pb2.SignalDetectorWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> anomalies_v1_detector_workflow_service_pb2.SignalDetectorWorkflowResponse:
        """Signals a detector."""
        return await handle_signal_detector_workflow(self.deps, request)

    @rpc_errors
    async def StartDetectorWorkflow(
        self, request: anomalies_v1_detector_workflow_service_pb2.StartDetectorWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> anomalies_v1_detector_workflow_service_pb2.StartDetectorWorkflowResponse:
        """Starts a detector."""
        return await handle_start_detector_workflow(self.deps, request)
