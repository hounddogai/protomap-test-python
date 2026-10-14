"""Checks scenarios against the rules before anything acts on them."""

from __future__ import annotations

from collections.abc import AsyncIterator

import grpc

from acme.forecasting.v1 import scenario_validation_service_pb2 as forecasting_v1_scenario_validation_service_pb2
from acme.forecasting.v1 import (
    scenario_validation_service_pb2_grpc as forecasting_v1_scenario_validation_service_pb2_grpc,
)

from acme_data.domains.forecasting.dependencies import Dependencies
from acme_data.domains.forecasting.scenario_validation_service_workflow import ScenarioValidationServicerWorkflow
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors


class ScenarioValidationServicer(forecasting_v1_scenario_validation_service_pb2_grpc.ScenarioValidationServiceServicer):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps
        self.workflow = ScenarioValidationServicerWorkflow(deps)

    @rpc_errors
    async def CheckScenarioEligibility(
        self, request: forecasting_v1_scenario_validation_service_pb2.CheckScenarioEligibilityRequest, context: grpc.aio.ServicerContext,
    ) -> forecasting_v1_scenario_validation_service_pb2.CheckScenarioEligibilityResponse:
        """Checks a scenario."""
        return await self.workflow.handle_check_scenario_eligibility(request)

    @rpc_errors
    async def ExplainScenarioDecision(
        self, request: forecasting_v1_scenario_validation_service_pb2.ExplainScenarioDecisionRequest, context: grpc.aio.ServicerContext,
    ) -> forecasting_v1_scenario_validation_service_pb2.ExplainScenarioDecisionResponse:
        """Explains a scenario."""
        return await self.workflow.handle_explain_scenario_decision(request)

    @rpc_errors
    @retry_transient
    async def GetScenarioRules(
        self, request: forecasting_v1_scenario_validation_service_pb2.GetScenarioRulesRequest, context: grpc.aio.ServicerContext,
    ) -> forecasting_v1_scenario_validation_service_pb2.GetScenarioRulesResponse:
        """Returns a scenario."""
        return await self.workflow.handle_get_scenario_rules(request)

    @rpc_errors
    async def LintScenarios(
        self, request: forecasting_v1_scenario_validation_service_pb2.LintScenariosRequest, context: grpc.aio.ServicerContext,
    ) -> forecasting_v1_scenario_validation_service_pb2.LintScenariosResponse:
        """Lints a scenario."""
        return await self.workflow.handle_lint_scenarios(request)

    @rpc_errors
    async def NormalizeScenario(
        self, request: forecasting_v1_scenario_validation_service_pb2.NormalizeScenarioRequest, context: grpc.aio.ServicerContext,
    ) -> forecasting_v1_scenario_validation_service_pb2.NormalizeScenarioResponse:
        """Normalizes a scenario."""
        return await self.workflow.handle_normalize_scenario(request)

    @rpc_errors
    async def PreviewScenario(
        self, request: forecasting_v1_scenario_validation_service_pb2.PreviewScenarioRequest, context: grpc.aio.ServicerContext,
    ) -> forecasting_v1_scenario_validation_service_pb2.PreviewScenarioResponse:
        """Previews a scenario."""
        return await self.workflow.handle_preview_scenario(request)

    @rpc_errors
    async def ScoreScenario(
        self, request: forecasting_v1_scenario_validation_service_pb2.ScoreScenarioRequest, context: grpc.aio.ServicerContext,
    ) -> forecasting_v1_scenario_validation_service_pb2.ScoreScenarioResponse:
        """Scores a scenario."""
        return await self.workflow.handle_score_scenario(request)

    @rpc_errors
    async def ValidateScenario(
        self, request: forecasting_v1_scenario_validation_service_pb2.ValidateScenarioRequest, context: grpc.aio.ServicerContext,
    ) -> forecasting_v1_scenario_validation_service_pb2.ValidateScenarioResponse:
        """Validates a scenario."""
        return await self.workflow.handle_validate_scenario(request)
