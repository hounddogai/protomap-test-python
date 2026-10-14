"""Checks anomalies against the rules before anything acts on them."""

from __future__ import annotations

from collections.abc import AsyncIterator

import grpc

from acme.anomalies.v1 import anomaly_validation_service_pb2 as anomalies_v1_anomaly_validation_service_pb2
from acme.anomalies.v1 import anomaly_validation_service_pb2_grpc as anomalies_v1_anomaly_validation_service_pb2_grpc

from acme_data.domains.anomalies.anomaly_validation_service_operations import handle_check_anomaly_eligibility
from acme_data.domains.anomalies.anomaly_validation_service_operations import handle_explain_anomaly_decision
from acme_data.domains.anomalies.anomaly_validation_service_operations import handle_lint_anomalies
from acme_data.domains.anomalies.anomaly_validation_service_operations import handle_normalize_anomaly
from acme_data.domains.anomalies.anomaly_validation_service_operations import handle_preview_anomaly
from acme_data.domains.anomalies.anomaly_validation_service_operations import handle_score_anomaly
from acme_data.domains.anomalies.anomaly_validation_service_operations import handle_validate_anomaly
from acme_data.domains.anomalies.dependencies import Dependencies
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors


class AnomalyValidationServicer(anomalies_v1_anomaly_validation_service_pb2_grpc.AnomalyValidationServiceServicer):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    async def CheckAnomalyEligibility(
        self, request: anomalies_v1_anomaly_validation_service_pb2.CheckAnomalyEligibilityRequest, context: grpc.aio.ServicerContext,
    ) -> anomalies_v1_anomaly_validation_service_pb2.CheckAnomalyEligibilityResponse:
        """Checks an anomaly."""
        return await handle_check_anomaly_eligibility(self.deps, request)

    @rpc_errors
    async def ExplainAnomalyDecision(
        self, request: anomalies_v1_anomaly_validation_service_pb2.ExplainAnomalyDecisionRequest, context: grpc.aio.ServicerContext,
    ) -> anomalies_v1_anomaly_validation_service_pb2.ExplainAnomalyDecisionResponse:
        """Explains an anomaly."""
        return await handle_explain_anomaly_decision(self.deps, request)

    @rpc_errors
    async def LintAnomalies(
        self, request: anomalies_v1_anomaly_validation_service_pb2.LintAnomaliesRequest, context: grpc.aio.ServicerContext,
    ) -> anomalies_v1_anomaly_validation_service_pb2.LintAnomaliesResponse:
        """Lints an anomaly."""
        return await handle_lint_anomalies(self.deps, request)

    @rpc_errors
    async def NormalizeAnomaly(
        self, request: anomalies_v1_anomaly_validation_service_pb2.NormalizeAnomalyRequest, context: grpc.aio.ServicerContext,
    ) -> anomalies_v1_anomaly_validation_service_pb2.NormalizeAnomalyResponse:
        """Normalizes an anomaly."""
        return await handle_normalize_anomaly(self.deps, request)

    @rpc_errors
    async def PreviewAnomaly(
        self, request: anomalies_v1_anomaly_validation_service_pb2.PreviewAnomalyRequest, context: grpc.aio.ServicerContext,
    ) -> anomalies_v1_anomaly_validation_service_pb2.PreviewAnomalyResponse:
        """Previews an anomaly."""
        return await handle_preview_anomaly(self.deps, request)

    @rpc_errors
    async def ScoreAnomaly(
        self, request: anomalies_v1_anomaly_validation_service_pb2.ScoreAnomalyRequest, context: grpc.aio.ServicerContext,
    ) -> anomalies_v1_anomaly_validation_service_pb2.ScoreAnomalyResponse:
        """Scores an anomaly."""
        return await handle_score_anomaly(self.deps, request)

    @rpc_errors
    async def ValidateAnomaly(
        self, request: anomalies_v1_anomaly_validation_service_pb2.ValidateAnomalyRequest, context: grpc.aio.ServicerContext,
    ) -> anomalies_v1_anomaly_validation_service_pb2.ValidateAnomalyResponse:
        """Validates an anomaly."""
        return await handle_validate_anomaly(self.deps, request)
