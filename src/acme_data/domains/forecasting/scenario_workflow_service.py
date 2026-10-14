"""Runs the long-lived workflow that takes a scenario from start to finish."""

from __future__ import annotations

from collections.abc import AsyncIterator

import grpc

from acme.forecasting.v1 import scenario_workflow_service_pb2 as forecasting_v1_scenario_workflow_service_pb2
from acme.forecasting.v1 import scenario_workflow_service_pb2_grpc as forecasting_v1_scenario_workflow_service_pb2_grpc

from acme_data.domains.forecasting.dependencies import Dependencies
from acme_data.domains.forecasting.scenario_workflow_service_operations import handle_advance_scenario_workflow
from acme_data.domains.forecasting.scenario_workflow_service_operations import handle_cancel_scenario_workflow
from acme_data.domains.forecasting.scenario_workflow_service_operations import handle_pause_scenario_workflow
from acme_data.domains.forecasting.scenario_workflow_service_operations import handle_resume_scenario_workflow
from acme_data.domains.forecasting.scenario_workflow_service_operations import handle_retry_scenario_workflow
from acme_data.domains.forecasting.scenario_workflow_service_operations import handle_signal_scenario_workflow
from acme_data.domains.forecasting.scenario_workflow_service_operations import handle_start_scenario_workflow
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors


class ScenarioWorkflowServicer(forecasting_v1_scenario_workflow_service_pb2_grpc.ScenarioWorkflowServiceServicer):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    async def AdvanceScenarioWorkflow(
        self, request: forecasting_v1_scenario_workflow_service_pb2.AdvanceScenarioWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> forecasting_v1_scenario_workflow_service_pb2.AdvanceScenarioWorkflowResponse:
        """Advances a scenario."""
        return await handle_advance_scenario_workflow(self.deps, request)

    @rpc_errors
    async def CancelScenarioWorkflow(
        self, request: forecasting_v1_scenario_workflow_service_pb2.CancelScenarioWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> forecasting_v1_scenario_workflow_service_pb2.CancelScenarioWorkflowResponse:
        """Cancels a scenario."""
        return await handle_cancel_scenario_workflow(self.deps, request)

    @rpc_errors
    async def PauseScenarioWorkflow(
        self, request: forecasting_v1_scenario_workflow_service_pb2.PauseScenarioWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> forecasting_v1_scenario_workflow_service_pb2.PauseScenarioWorkflowResponse:
        """Pauses a scenario."""
        return await handle_pause_scenario_workflow(self.deps, request)

    @rpc_errors
    async def ResumeScenarioWorkflow(
        self, request: forecasting_v1_scenario_workflow_service_pb2.ResumeScenarioWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> forecasting_v1_scenario_workflow_service_pb2.ResumeScenarioWorkflowResponse:
        """Resumes a scenario."""
        return await handle_resume_scenario_workflow(self.deps, request)

    @rpc_errors
    async def RetryScenarioWorkflow(
        self, request: forecasting_v1_scenario_workflow_service_pb2.RetryScenarioWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> forecasting_v1_scenario_workflow_service_pb2.RetryScenarioWorkflowResponse:
        """Retrys a scenario."""
        return await handle_retry_scenario_workflow(self.deps, request)

    @rpc_errors
    async def SignalScenarioWorkflow(
        self, request: forecasting_v1_scenario_workflow_service_pb2.SignalScenarioWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> forecasting_v1_scenario_workflow_service_pb2.SignalScenarioWorkflowResponse:
        """Signals a scenario."""
        return await handle_signal_scenario_workflow(self.deps, request)

    @rpc_errors
    async def StartScenarioWorkflow(
        self, request: forecasting_v1_scenario_workflow_service_pb2.StartScenarioWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> forecasting_v1_scenario_workflow_service_pb2.StartScenarioWorkflowResponse:
        """Starts a scenario."""
        return await handle_start_scenario_workflow(self.deps, request)
