"""Checks detectors against the rules before anything acts on them."""

from __future__ import annotations

from collections.abc import AsyncIterator

import grpc

from acme.anomalies.v1 import detector_validation_service_pb2 as anomalies_v1_detector_validation_service_pb2
from acme.anomalies.v1 import detector_validation_service_pb2_grpc as anomalies_v1_detector_validation_service_pb2_grpc

from acme_data.domains.anomalies.dependencies import Dependencies
from acme_data.domains.anomalies.detector_validation_service_workflow import DetectorValidationServicerWorkflow
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors


class DetectorValidationServicer(anomalies_v1_detector_validation_service_pb2_grpc.DetectorValidationServiceServicer):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps
        self.workflow = DetectorValidationServicerWorkflow(deps)

    @rpc_errors
    async def CheckDetectorEligibility(
        self, request: anomalies_v1_detector_validation_service_pb2.CheckDetectorEligibilityRequest, context: grpc.aio.ServicerContext,
    ) -> anomalies_v1_detector_validation_service_pb2.CheckDetectorEligibilityResponse:
        """Checks a detector."""
        return await self.workflow.handle_check_detector_eligibility(request)

    @rpc_errors
    async def ExplainDetectorDecision(
        self, request: anomalies_v1_detector_validation_service_pb2.ExplainDetectorDecisionRequest, context: grpc.aio.ServicerContext,
    ) -> anomalies_v1_detector_validation_service_pb2.ExplainDetectorDecisionResponse:
        """Explains a detector."""
        return await self.workflow.handle_explain_detector_decision(request)

    @rpc_errors
    async def LintDetectors(
        self, request: anomalies_v1_detector_validation_service_pb2.LintDetectorsRequest, context: grpc.aio.ServicerContext,
    ) -> anomalies_v1_detector_validation_service_pb2.LintDetectorsResponse:
        """Lints a detector."""
        return await self.workflow.handle_lint_detectors(request)

    @rpc_errors
    async def NormalizeDetector(
        self, request: anomalies_v1_detector_validation_service_pb2.NormalizeDetectorRequest, context: grpc.aio.ServicerContext,
    ) -> anomalies_v1_detector_validation_service_pb2.NormalizeDetectorResponse:
        """Normalizes a detector."""
        return await self.workflow.handle_normalize_detector(request)

    @rpc_errors
    async def PreviewDetector(
        self, request: anomalies_v1_detector_validation_service_pb2.PreviewDetectorRequest, context: grpc.aio.ServicerContext,
    ) -> anomalies_v1_detector_validation_service_pb2.PreviewDetectorResponse:
        """Previews a detector."""
        return await self.workflow.handle_preview_detector(request)

    @rpc_errors
    async def ScoreDetector(
        self, request: anomalies_v1_detector_validation_service_pb2.ScoreDetectorRequest, context: grpc.aio.ServicerContext,
    ) -> anomalies_v1_detector_validation_service_pb2.ScoreDetectorResponse:
        """Scores a detector."""
        return await self.workflow.handle_score_detector(request)

    @rpc_errors
    async def ValidateDetector(
        self, request: anomalies_v1_detector_validation_service_pb2.ValidateDetectorRequest, context: grpc.aio.ServicerContext,
    ) -> anomalies_v1_detector_validation_service_pb2.ValidateDetectorResponse:
        """Validates a detector."""
        return await self.workflow.handle_validate_detector(request)
