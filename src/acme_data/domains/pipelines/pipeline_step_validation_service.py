"""Checks pipeline steps against the rules before anything acts on them."""

from __future__ import annotations

from collections.abc import AsyncIterator

import grpc

from acme.pipelines.v1 import pipeline_step_validation_service_pb2 as pipelines_v1_pipeline_step_validation_service_pb2
from acme.pipelines.v1 import (
    pipeline_step_validation_service_pb2_grpc as pipelines_v1_pipeline_step_validation_service_pb2_grpc,
)

from acme_data.domains.pipelines.dependencies import Dependencies
from acme_data.domains.pipelines.pipeline_step_validation_service_operations import (
    handle_check_pipeline_step_eligibility,
)
from acme_data.domains.pipelines.pipeline_step_validation_service_operations import (
    handle_explain_pipeline_step_decision,
)
from acme_data.domains.pipelines.pipeline_step_validation_service_operations import handle_get_pipeline_step_rules
from acme_data.domains.pipelines.pipeline_step_validation_service_operations import handle_lint_pipeline_steps
from acme_data.domains.pipelines.pipeline_step_validation_service_operations import handle_normalize_pipeline_step
from acme_data.domains.pipelines.pipeline_step_validation_service_operations import handle_preview_pipeline_step
from acme_data.domains.pipelines.pipeline_step_validation_service_operations import handle_score_pipeline_step
from acme_data.domains.pipelines.pipeline_step_validation_service_operations import handle_validate_pipeline_step
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors


class PipelineStepValidationServicer(
    pipelines_v1_pipeline_step_validation_service_pb2_grpc.PipelineStepValidationServiceServicer
):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    async def CheckPipelineStepEligibility(
        self, request: pipelines_v1_pipeline_step_validation_service_pb2.CheckPipelineStepEligibilityRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_step_validation_service_pb2.CheckPipelineStepEligibilityResponse:
        """Checks a pipeline step."""
        return await handle_check_pipeline_step_eligibility(self.deps, request)

    @rpc_errors
    async def ExplainPipelineStepDecision(
        self, request: pipelines_v1_pipeline_step_validation_service_pb2.ExplainPipelineStepDecisionRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_step_validation_service_pb2.ExplainPipelineStepDecisionResponse:
        """Explains a pipeline step."""
        return await handle_explain_pipeline_step_decision(self.deps, request)

    @rpc_errors
    @retry_transient
    async def GetPipelineStepRules(
        self, request: pipelines_v1_pipeline_step_validation_service_pb2.GetPipelineStepRulesRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_step_validation_service_pb2.GetPipelineStepRulesResponse:
        """Returns a pipeline step."""
        return await handle_get_pipeline_step_rules(self.deps, request)

    @rpc_errors
    async def LintPipelineSteps(
        self, request: pipelines_v1_pipeline_step_validation_service_pb2.LintPipelineStepsRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_step_validation_service_pb2.LintPipelineStepsResponse:
        """Lints a pipeline step."""
        return await handle_lint_pipeline_steps(self.deps, request)

    @rpc_errors
    async def NormalizePipelineStep(
        self, request: pipelines_v1_pipeline_step_validation_service_pb2.NormalizePipelineStepRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_step_validation_service_pb2.NormalizePipelineStepResponse:
        """Normalizes a pipeline step."""
        return await handle_normalize_pipeline_step(self.deps, request)

    @rpc_errors
    async def PreviewPipelineStep(
        self, request: pipelines_v1_pipeline_step_validation_service_pb2.PreviewPipelineStepRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_step_validation_service_pb2.PreviewPipelineStepResponse:
        """Previews a pipeline step."""
        return await handle_preview_pipeline_step(self.deps, request)

    @rpc_errors
    async def ScorePipelineStep(
        self, request: pipelines_v1_pipeline_step_validation_service_pb2.ScorePipelineStepRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_step_validation_service_pb2.ScorePipelineStepResponse:
        """Scores a pipeline step."""
        return await handle_score_pipeline_step(self.deps, request)

    @rpc_errors
    async def ValidatePipelineStep(
        self, request: pipelines_v1_pipeline_step_validation_service_pb2.ValidatePipelineStepRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_step_validation_service_pb2.ValidatePipelineStepResponse:
        """Validates a pipeline step."""
        return await handle_validate_pipeline_step(self.deps, request)
