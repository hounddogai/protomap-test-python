"""Checks deployments against the rules before anything acts on them."""

from __future__ import annotations

from collections.abc import AsyncIterator

import grpc

from acme.modelregistry.v1 import (
    deployment_validation_service_pb2 as modelregistry_v1_deployment_validation_service_pb2,
)
from acme.modelregistry.v1 import (
    deployment_validation_service_pb2_grpc as modelregistry_v1_deployment_validation_service_pb2_grpc,
)

from acme_data.domains.modelregistry.dependencies import Dependencies
from acme_data.domains.modelregistry.deployment_validation_service_workflow import DeploymentValidationServicerWorkflow
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors


class DeploymentValidationServicer(
    modelregistry_v1_deployment_validation_service_pb2_grpc.DeploymentValidationServiceServicer
):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps
        self.workflow = DeploymentValidationServicerWorkflow(deps)

    @rpc_errors
    async def CheckDeploymentEligibility(
        self, request: modelregistry_v1_deployment_validation_service_pb2.CheckDeploymentEligibilityRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_deployment_validation_service_pb2.CheckDeploymentEligibilityResponse:
        """Checks a deployment."""
        return await self.workflow.handle_check_deployment_eligibility(request)

    @rpc_errors
    async def ExplainDeploymentDecision(
        self, request: modelregistry_v1_deployment_validation_service_pb2.ExplainDeploymentDecisionRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_deployment_validation_service_pb2.ExplainDeploymentDecisionResponse:
        """Explains a deployment."""
        return await self.workflow.handle_explain_deployment_decision(request)

    @rpc_errors
    @retry_transient
    async def GetDeploymentRules(
        self, request: modelregistry_v1_deployment_validation_service_pb2.GetDeploymentRulesRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_deployment_validation_service_pb2.GetDeploymentRulesResponse:
        """Returns a deployment."""
        return await self.workflow.handle_get_deployment_rules(request)

    @rpc_errors
    async def LintDeployments(
        self, request: modelregistry_v1_deployment_validation_service_pb2.LintDeploymentsRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_deployment_validation_service_pb2.LintDeploymentsResponse:
        """Lints a deployment."""
        return await self.workflow.handle_lint_deployments(request)

    @rpc_errors
    async def NormalizeDeployment(
        self, request: modelregistry_v1_deployment_validation_service_pb2.NormalizeDeploymentRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_deployment_validation_service_pb2.NormalizeDeploymentResponse:
        """Normalizes a deployment."""
        return await self.workflow.handle_normalize_deployment(request)

    @rpc_errors
    async def PreviewDeployment(
        self, request: modelregistry_v1_deployment_validation_service_pb2.PreviewDeploymentRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_deployment_validation_service_pb2.PreviewDeploymentResponse:
        """Previews a deployment."""
        return await self.workflow.handle_preview_deployment(request)

    @rpc_errors
    async def ScoreDeployment(
        self, request: modelregistry_v1_deployment_validation_service_pb2.ScoreDeploymentRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_deployment_validation_service_pb2.ScoreDeploymentResponse:
        """Scores a deployment."""
        return await self.workflow.handle_score_deployment(request)

    @rpc_errors
    async def ValidateDeployment(
        self, request: modelregistry_v1_deployment_validation_service_pb2.ValidateDeploymentRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_deployment_validation_service_pb2.ValidateDeploymentResponse:
        """Validates a deployment."""
        return await self.workflow.handle_validate_deployment(request)
