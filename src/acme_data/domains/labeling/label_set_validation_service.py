"""Checks label sets against the rules before anything acts on them."""

from __future__ import annotations

from collections.abc import AsyncIterator

import grpc

from acme.labeling.v1 import label_set_validation_service_pb2 as labeling_v1_label_set_validation_service_pb2
from acme.labeling.v1 import label_set_validation_service_pb2_grpc as labeling_v1_label_set_validation_service_pb2_grpc

from acme_data.domains.labeling.dependencies import Dependencies
from acme_data.domains.labeling.label_set_validation_service_operations import handle_check_label_set_eligibility
from acme_data.domains.labeling.label_set_validation_service_operations import handle_explain_label_set_decision
from acme_data.domains.labeling.label_set_validation_service_operations import handle_get_label_set_rules
from acme_data.domains.labeling.label_set_validation_service_operations import handle_lint_label_sets
from acme_data.domains.labeling.label_set_validation_service_operations import handle_normalize_label_set
from acme_data.domains.labeling.label_set_validation_service_operations import handle_preview_label_set
from acme_data.domains.labeling.label_set_validation_service_operations import handle_score_label_set
from acme_data.domains.labeling.label_set_validation_service_operations import handle_validate_label_set
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors


class LabelSetValidationServicer(labeling_v1_label_set_validation_service_pb2_grpc.LabelSetValidationServiceServicer):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    async def CheckLabelSetEligibility(
        self, request: labeling_v1_label_set_validation_service_pb2.CheckLabelSetEligibilityRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_label_set_validation_service_pb2.CheckLabelSetEligibilityResponse:
        """Checks a label set."""
        return await handle_check_label_set_eligibility(self.deps, request)

    @rpc_errors
    async def ExplainLabelSetDecision(
        self, request: labeling_v1_label_set_validation_service_pb2.ExplainLabelSetDecisionRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_label_set_validation_service_pb2.ExplainLabelSetDecisionResponse:
        """Explains a label set."""
        return await handle_explain_label_set_decision(self.deps, request)

    @rpc_errors
    @retry_transient
    async def GetLabelSetRules(
        self, request: labeling_v1_label_set_validation_service_pb2.GetLabelSetRulesRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_label_set_validation_service_pb2.GetLabelSetRulesResponse:
        """Returns a label set."""
        return await handle_get_label_set_rules(self.deps, request)

    @rpc_errors
    async def LintLabelSets(
        self, request: labeling_v1_label_set_validation_service_pb2.LintLabelSetsRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_label_set_validation_service_pb2.LintLabelSetsResponse:
        """Lints a label set."""
        return await handle_lint_label_sets(self.deps, request)

    @rpc_errors
    async def NormalizeLabelSet(
        self, request: labeling_v1_label_set_validation_service_pb2.NormalizeLabelSetRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_label_set_validation_service_pb2.NormalizeLabelSetResponse:
        """Normalizes a label set."""
        return await handle_normalize_label_set(self.deps, request)

    @rpc_errors
    async def PreviewLabelSet(
        self, request: labeling_v1_label_set_validation_service_pb2.PreviewLabelSetRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_label_set_validation_service_pb2.PreviewLabelSetResponse:
        """Previews a label set."""
        return await handle_preview_label_set(self.deps, request)

    @rpc_errors
    async def ScoreLabelSet(
        self, request: labeling_v1_label_set_validation_service_pb2.ScoreLabelSetRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_label_set_validation_service_pb2.ScoreLabelSetResponse:
        """Scores a label set."""
        return await handle_score_label_set(self.deps, request)

    @rpc_errors
    async def ValidateLabelSet(
        self, request: labeling_v1_label_set_validation_service_pb2.ValidateLabelSetRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_label_set_validation_service_pb2.ValidateLabelSetResponse:
        """Validates a label set."""
        return await handle_validate_label_set(self.deps, request)
