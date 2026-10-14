"""Checks dataset versions against the rules before anything acts on them."""

from __future__ import annotations

from collections.abc import AsyncIterator

import grpc

from acme.datasets.v1 import (
    dataset_version_validation_service_pb2 as datasets_v1_dataset_version_validation_service_pb2,
)
from acme.datasets.v1 import (
    dataset_version_validation_service_pb2_grpc as datasets_v1_dataset_version_validation_service_pb2_grpc,
)

from acme_data.domains.datasets.dataset_version_validation_service_workflow import (
    DatasetVersionValidationServicerWorkflow,
)
from acme_data.domains.datasets.dependencies import Dependencies
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors


class DatasetVersionValidationServicer(
    datasets_v1_dataset_version_validation_service_pb2_grpc.DatasetVersionValidationServiceServicer
):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps
        self.workflow = DatasetVersionValidationServicerWorkflow(deps)

    @rpc_errors
    async def CheckDatasetVersionEligibility(
        self, request: datasets_v1_dataset_version_validation_service_pb2.CheckDatasetVersionEligibilityRequest, context: grpc.aio.ServicerContext,
    ) -> datasets_v1_dataset_version_validation_service_pb2.CheckDatasetVersionEligibilityResponse:
        """Checks a dataset version."""
        return await self.workflow.handle_check_dataset_version_eligibility(request)

    @rpc_errors
    async def ExplainDatasetVersionDecision(
        self, request: datasets_v1_dataset_version_validation_service_pb2.ExplainDatasetVersionDecisionRequest, context: grpc.aio.ServicerContext,
    ) -> datasets_v1_dataset_version_validation_service_pb2.ExplainDatasetVersionDecisionResponse:
        """Explains a dataset version."""
        return await self.workflow.handle_explain_dataset_version_decision(request)

    @rpc_errors
    @retry_transient
    async def GetDatasetVersionRules(
        self, request: datasets_v1_dataset_version_validation_service_pb2.GetDatasetVersionRulesRequest, context: grpc.aio.ServicerContext,
    ) -> datasets_v1_dataset_version_validation_service_pb2.GetDatasetVersionRulesResponse:
        """Returns a dataset version."""
        return await self.workflow.handle_get_dataset_version_rules(request)

    @rpc_errors
    async def LintDatasetVersions(
        self, request: datasets_v1_dataset_version_validation_service_pb2.LintDatasetVersionsRequest, context: grpc.aio.ServicerContext,
    ) -> datasets_v1_dataset_version_validation_service_pb2.LintDatasetVersionsResponse:
        """Lints a dataset version."""
        return await self.workflow.handle_lint_dataset_versions(request)

    @rpc_errors
    async def NormalizeDatasetVersion(
        self, request: datasets_v1_dataset_version_validation_service_pb2.NormalizeDatasetVersionRequest, context: grpc.aio.ServicerContext,
    ) -> datasets_v1_dataset_version_validation_service_pb2.NormalizeDatasetVersionResponse:
        """Normalizes a dataset version."""
        return await self.workflow.handle_normalize_dataset_version(request)

    @rpc_errors
    async def PreviewDatasetVersion(
        self, request: datasets_v1_dataset_version_validation_service_pb2.PreviewDatasetVersionRequest, context: grpc.aio.ServicerContext,
    ) -> datasets_v1_dataset_version_validation_service_pb2.PreviewDatasetVersionResponse:
        """Previews a dataset version."""
        return await self.workflow.handle_preview_dataset_version(request)

    @rpc_errors
    async def ScoreDatasetVersion(
        self, request: datasets_v1_dataset_version_validation_service_pb2.ScoreDatasetVersionRequest, context: grpc.aio.ServicerContext,
    ) -> datasets_v1_dataset_version_validation_service_pb2.ScoreDatasetVersionResponse:
        """Scores a dataset version."""
        return await self.workflow.handle_score_dataset_version(request)

    @rpc_errors
    async def ValidateDatasetVersion(
        self, request: datasets_v1_dataset_version_validation_service_pb2.ValidateDatasetVersionRequest, context: grpc.aio.ServicerContext,
    ) -> datasets_v1_dataset_version_validation_service_pb2.ValidateDatasetVersionResponse:
        """Validates a dataset version."""
        return await self.workflow.handle_validate_dataset_version(request)
