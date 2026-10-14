"""Checks datasets against the rules before anything acts on them."""

from __future__ import annotations

from collections.abc import AsyncIterator

import grpc

from acme.datasets.v1 import dataset_validation_service_pb2 as datasets_v1_dataset_validation_service_pb2
from acme.datasets.v1 import dataset_validation_service_pb2_grpc as datasets_v1_dataset_validation_service_pb2_grpc

from acme_data.domains.datasets.dataset_validation_service_operations import handle_check_dataset_eligibility
from acme_data.domains.datasets.dataset_validation_service_operations import handle_explain_dataset_decision
from acme_data.domains.datasets.dataset_validation_service_operations import handle_get_dataset_rules
from acme_data.domains.datasets.dataset_validation_service_operations import handle_lint_datasets
from acme_data.domains.datasets.dataset_validation_service_operations import handle_normalize_dataset
from acme_data.domains.datasets.dataset_validation_service_operations import handle_preview_dataset
from acme_data.domains.datasets.dataset_validation_service_operations import handle_score_dataset
from acme_data.domains.datasets.dataset_validation_service_operations import handle_validate_dataset
from acme_data.domains.datasets.dependencies import Dependencies
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors


class DatasetValidationServicer(datasets_v1_dataset_validation_service_pb2_grpc.DatasetValidationServiceServicer):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    async def CheckDatasetEligibility(
        self, request: datasets_v1_dataset_validation_service_pb2.CheckDatasetEligibilityRequest, context: grpc.aio.ServicerContext,
    ) -> datasets_v1_dataset_validation_service_pb2.CheckDatasetEligibilityResponse:
        """Checks a dataset."""
        return await handle_check_dataset_eligibility(self.deps, request)

    @rpc_errors
    async def ExplainDatasetDecision(
        self, request: datasets_v1_dataset_validation_service_pb2.ExplainDatasetDecisionRequest, context: grpc.aio.ServicerContext,
    ) -> datasets_v1_dataset_validation_service_pb2.ExplainDatasetDecisionResponse:
        """Explains a dataset."""
        return await handle_explain_dataset_decision(self.deps, request)

    @rpc_errors
    @retry_transient
    async def GetDatasetRules(
        self, request: datasets_v1_dataset_validation_service_pb2.GetDatasetRulesRequest, context: grpc.aio.ServicerContext,
    ) -> datasets_v1_dataset_validation_service_pb2.GetDatasetRulesResponse:
        """Returns a dataset."""
        return await handle_get_dataset_rules(self.deps, request)

    @rpc_errors
    async def LintDatasets(
        self, request: datasets_v1_dataset_validation_service_pb2.LintDatasetsRequest, context: grpc.aio.ServicerContext,
    ) -> datasets_v1_dataset_validation_service_pb2.LintDatasetsResponse:
        """Lints a dataset."""
        return await handle_lint_datasets(self.deps, request)

    @rpc_errors
    async def NormalizeDataset(
        self, request: datasets_v1_dataset_validation_service_pb2.NormalizeDatasetRequest, context: grpc.aio.ServicerContext,
    ) -> datasets_v1_dataset_validation_service_pb2.NormalizeDatasetResponse:
        """Normalizes a dataset."""
        return await handle_normalize_dataset(self.deps, request)

    @rpc_errors
    async def PreviewDataset(
        self, request: datasets_v1_dataset_validation_service_pb2.PreviewDatasetRequest, context: grpc.aio.ServicerContext,
    ) -> datasets_v1_dataset_validation_service_pb2.PreviewDatasetResponse:
        """Previews a dataset."""
        return await handle_preview_dataset(self.deps, request)

    @rpc_errors
    async def ScoreDataset(
        self, request: datasets_v1_dataset_validation_service_pb2.ScoreDatasetRequest, context: grpc.aio.ServicerContext,
    ) -> datasets_v1_dataset_validation_service_pb2.ScoreDatasetResponse:
        """Scores a dataset."""
        return await handle_score_dataset(self.deps, request)

    @rpc_errors
    async def ValidateDataset(
        self, request: datasets_v1_dataset_validation_service_pb2.ValidateDatasetRequest, context: grpc.aio.ServicerContext,
    ) -> datasets_v1_dataset_validation_service_pb2.ValidateDatasetResponse:
        """Validates a dataset."""
        return await handle_validate_dataset(self.deps, request)
