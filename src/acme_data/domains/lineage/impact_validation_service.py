"""Checks impacts against the rules before anything acts on them."""

from __future__ import annotations

from collections.abc import AsyncIterator

import grpc

from acme.lineage.v1 import impact_validation_service_pb2 as lineage_v1_impact_validation_service_pb2
from acme.lineage.v1 import impact_validation_service_pb2_grpc as lineage_v1_impact_validation_service_pb2_grpc

from acme_data.domains.lineage.dependencies import Dependencies
from acme_data.domains.lineage.impact_validation_service_workflow import ImpactValidationServicerWorkflow
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors


class ImpactValidationServicer(lineage_v1_impact_validation_service_pb2_grpc.ImpactValidationServiceServicer):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps
        self.workflow = ImpactValidationServicerWorkflow(deps)

    @rpc_errors
    async def CheckImpactEligibility(
        self, request: lineage_v1_impact_validation_service_pb2.CheckImpactEligibilityRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_impact_validation_service_pb2.CheckImpactEligibilityResponse:
        """Checks an impact."""
        return await self.workflow.handle_check_impact_eligibility(request)

    @rpc_errors
    async def ExplainImpactDecision(
        self, request: lineage_v1_impact_validation_service_pb2.ExplainImpactDecisionRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_impact_validation_service_pb2.ExplainImpactDecisionResponse:
        """Explains an impact."""
        return await self.workflow.handle_explain_impact_decision(request)

    @rpc_errors
    @retry_transient
    async def GetImpactRules(
        self, request: lineage_v1_impact_validation_service_pb2.GetImpactRulesRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_impact_validation_service_pb2.GetImpactRulesResponse:
        """Returns an impact."""
        return await self.workflow.handle_get_impact_rules(request)

    @rpc_errors
    async def LintImpacts(
        self, request: lineage_v1_impact_validation_service_pb2.LintImpactsRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_impact_validation_service_pb2.LintImpactsResponse:
        """Lints an impact."""
        return await self.workflow.handle_lint_impacts(request)

    @rpc_errors
    async def NormalizeImpact(
        self, request: lineage_v1_impact_validation_service_pb2.NormalizeImpactRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_impact_validation_service_pb2.NormalizeImpactResponse:
        """Normalizes an impact."""
        return await self.workflow.handle_normalize_impact(request)

    @rpc_errors
    async def PreviewImpact(
        self, request: lineage_v1_impact_validation_service_pb2.PreviewImpactRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_impact_validation_service_pb2.PreviewImpactResponse:
        """Previews an impact."""
        return await self.workflow.handle_preview_impact(request)

    @rpc_errors
    async def ValidateImpact(
        self, request: lineage_v1_impact_validation_service_pb2.ValidateImpactRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_impact_validation_service_pb2.ValidateImpactResponse:
        """Validates an impact."""
        return await self.workflow.handle_validate_impact(request)
