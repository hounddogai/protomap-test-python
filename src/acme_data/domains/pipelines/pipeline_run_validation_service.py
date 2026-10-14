"""Checks pipeline runs against the rules before anything acts on them."""

from __future__ import annotations

from collections.abc import AsyncIterator

import grpc

from acme.pipelines.v1 import pipeline_run_validation_service_pb2 as pipelines_v1_pipeline_run_validation_service_pb2
from acme.pipelines.v1 import (
    pipeline_run_validation_service_pb2_grpc as pipelines_v1_pipeline_run_validation_service_pb2_grpc,
)

from acme_data.domains.pipelines.dependencies import Dependencies
from acme_data.domains.pipelines.pipeline_run_validation_service_operations import handle_check_pipeline_run_eligibility
from acme_data.domains.pipelines.pipeline_run_validation_service_operations import handle_explain_pipeline_run_decision
from acme_data.domains.pipelines.pipeline_run_validation_service_operations import handle_get_pipeline_run_rules
from acme_data.domains.pipelines.pipeline_run_validation_service_operations import handle_lint_pipeline_runs
from acme_data.domains.pipelines.pipeline_run_validation_service_operations import handle_normalize_pipeline_run
from acme_data.domains.pipelines.pipeline_run_validation_service_operations import handle_preview_pipeline_run
from acme_data.domains.pipelines.pipeline_run_validation_service_operations import handle_score_pipeline_run
from acme_data.domains.pipelines.pipeline_run_validation_service_operations import handle_validate_pipeline_run
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors


class PipelineRunValidationServicer(
    pipelines_v1_pipeline_run_validation_service_pb2_grpc.PipelineRunValidationServiceServicer
):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    async def CheckPipelineRunEligibility(
        self, request: pipelines_v1_pipeline_run_validation_service_pb2.CheckPipelineRunEligibilityRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_run_validation_service_pb2.CheckPipelineRunEligibilityResponse:
        """Checks a pipeline run."""
        return await handle_check_pipeline_run_eligibility(self.deps, request)

    @rpc_errors
    async def ExplainPipelineRunDecision(
        self, request: pipelines_v1_pipeline_run_validation_service_pb2.ExplainPipelineRunDecisionRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_run_validation_service_pb2.ExplainPipelineRunDecisionResponse:
        """Explains a pipeline run."""
        return await handle_explain_pipeline_run_decision(self.deps, request)

    @rpc_errors
    @retry_transient
    async def GetPipelineRunRules(
        self, request: pipelines_v1_pipeline_run_validation_service_pb2.GetPipelineRunRulesRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_run_validation_service_pb2.GetPipelineRunRulesResponse:
        """Returns a pipeline run."""
        return await handle_get_pipeline_run_rules(self.deps, request)

    @rpc_errors
    async def LintPipelineRuns(
        self, request: pipelines_v1_pipeline_run_validation_service_pb2.LintPipelineRunsRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_run_validation_service_pb2.LintPipelineRunsResponse:
        """Lints a pipeline run."""
        return await handle_lint_pipeline_runs(self.deps, request)

    @rpc_errors
    async def NormalizePipelineRun(
        self, request: pipelines_v1_pipeline_run_validation_service_pb2.NormalizePipelineRunRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_run_validation_service_pb2.NormalizePipelineRunResponse:
        """Normalizes a pipeline run."""
        return await handle_normalize_pipeline_run(self.deps, request)

    @rpc_errors
    async def PreviewPipelineRun(
        self, request: pipelines_v1_pipeline_run_validation_service_pb2.PreviewPipelineRunRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_run_validation_service_pb2.PreviewPipelineRunResponse:
        """Previews a pipeline run."""
        return await handle_preview_pipeline_run(self.deps, request)

    @rpc_errors
    async def ScorePipelineRun(
        self, request: pipelines_v1_pipeline_run_validation_service_pb2.ScorePipelineRunRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_run_validation_service_pb2.ScorePipelineRunResponse:
        """Scores a pipeline run."""
        return await handle_score_pipeline_run(self.deps, request)

    @rpc_errors
    async def ValidatePipelineRun(
        self, request: pipelines_v1_pipeline_run_validation_service_pb2.ValidatePipelineRunRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_run_validation_service_pb2.ValidatePipelineRunResponse:
        """Validates a pipeline run."""
        return await handle_validate_pipeline_run(self.deps, request)
