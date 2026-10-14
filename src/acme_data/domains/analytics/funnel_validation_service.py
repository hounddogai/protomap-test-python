"""Checks funnels against the rules before anything acts on them."""

from __future__ import annotations

from collections.abc import AsyncIterator

import grpc

from acme.analytics.v1 import funnel_validation_service_pb2 as analytics_v1_funnel_validation_service_pb2
from acme.analytics.v1 import funnel_validation_service_pb2_grpc as analytics_v1_funnel_validation_service_pb2_grpc

from acme_data.domains.analytics.dependencies import Dependencies
from acme_data.domains.analytics.funnel_validation_service_operations import handle_check_funnel_eligibility
from acme_data.domains.analytics.funnel_validation_service_operations import handle_get_funnel_rules
from acme_data.domains.analytics.funnel_validation_service_operations import handle_normalize_funnel
from acme_data.domains.analytics.funnel_validation_service_operations import handle_preview_funnel
from acme_data.domains.analytics.funnel_validation_service_operations import handle_score_funnel
from acme_data.domains.analytics.funnel_validation_service_operations import handle_validate_funnel
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors


class FunnelValidationServicer(analytics_v1_funnel_validation_service_pb2_grpc.FunnelValidationServiceServicer):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    async def CheckFunnelEligibility(
        self, request: analytics_v1_funnel_validation_service_pb2.CheckFunnelEligibilityRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_funnel_validation_service_pb2.CheckFunnelEligibilityResponse:
        """Checks a funnel."""
        return await handle_check_funnel_eligibility(self.deps, request)

    @rpc_errors
    @retry_transient
    async def GetFunnelRules(
        self, request: analytics_v1_funnel_validation_service_pb2.GetFunnelRulesRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_funnel_validation_service_pb2.GetFunnelRulesResponse:
        """Returns a funnel."""
        return await handle_get_funnel_rules(self.deps, request)

    @rpc_errors
    async def NormalizeFunnel(
        self, request: analytics_v1_funnel_validation_service_pb2.NormalizeFunnelRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_funnel_validation_service_pb2.NormalizeFunnelResponse:
        """Normalizes a funnel."""
        return await handle_normalize_funnel(self.deps, request)

    @rpc_errors
    async def PreviewFunnel(
        self, request: analytics_v1_funnel_validation_service_pb2.PreviewFunnelRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_funnel_validation_service_pb2.PreviewFunnelResponse:
        """Previews a funnel."""
        return await handle_preview_funnel(self.deps, request)

    @rpc_errors
    async def ScoreFunnel(
        self, request: analytics_v1_funnel_validation_service_pb2.ScoreFunnelRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_funnel_validation_service_pb2.ScoreFunnelResponse:
        """Scores a funnel."""
        return await handle_score_funnel(self.deps, request)

    @rpc_errors
    async def ValidateFunnel(
        self, request: analytics_v1_funnel_validation_service_pb2.ValidateFunnelRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_funnel_validation_service_pb2.ValidateFunnelResponse:
        """Validates a funnel."""
        return await handle_validate_funnel(self.deps, request)
