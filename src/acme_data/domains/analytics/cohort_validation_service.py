"""Checks cohorts against the rules before anything acts on them."""

from __future__ import annotations

from collections.abc import AsyncIterator

import grpc

from acme.analytics.v1 import cohort_validation_service_pb2 as analytics_v1_cohort_validation_service_pb2
from acme.analytics.v1 import cohort_validation_service_pb2_grpc as analytics_v1_cohort_validation_service_pb2_grpc

from acme_data.domains.analytics.cohort_validation_service_operations import handle_check_cohort_eligibility
from acme_data.domains.analytics.cohort_validation_service_operations import handle_get_cohort_rules
from acme_data.domains.analytics.cohort_validation_service_operations import handle_normalize_cohort
from acme_data.domains.analytics.cohort_validation_service_operations import handle_preview_cohort
from acme_data.domains.analytics.cohort_validation_service_operations import handle_score_cohort
from acme_data.domains.analytics.cohort_validation_service_operations import handle_validate_cohort
from acme_data.domains.analytics.dependencies import Dependencies
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors


class CohortValidationServicer(analytics_v1_cohort_validation_service_pb2_grpc.CohortValidationServiceServicer):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    async def CheckCohortEligibility(
        self, request: analytics_v1_cohort_validation_service_pb2.CheckCohortEligibilityRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_cohort_validation_service_pb2.CheckCohortEligibilityResponse:
        """Checks a cohort."""
        return await handle_check_cohort_eligibility(self.deps, request)

    @rpc_errors
    @retry_transient
    async def GetCohortRules(
        self, request: analytics_v1_cohort_validation_service_pb2.GetCohortRulesRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_cohort_validation_service_pb2.GetCohortRulesResponse:
        """Returns a cohort."""
        return await handle_get_cohort_rules(self.deps, request)

    @rpc_errors
    async def NormalizeCohort(
        self, request: analytics_v1_cohort_validation_service_pb2.NormalizeCohortRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_cohort_validation_service_pb2.NormalizeCohortResponse:
        """Normalizes a cohort."""
        return await handle_normalize_cohort(self.deps, request)

    @rpc_errors
    async def PreviewCohort(
        self, request: analytics_v1_cohort_validation_service_pb2.PreviewCohortRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_cohort_validation_service_pb2.PreviewCohortResponse:
        """Previews a cohort."""
        return await handle_preview_cohort(self.deps, request)

    @rpc_errors
    async def ScoreCohort(
        self, request: analytics_v1_cohort_validation_service_pb2.ScoreCohortRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_cohort_validation_service_pb2.ScoreCohortResponse:
        """Scores a cohort."""
        return await handle_score_cohort(self.deps, request)

    @rpc_errors
    async def ValidateCohort(
        self, request: analytics_v1_cohort_validation_service_pb2.ValidateCohortRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_cohort_validation_service_pb2.ValidateCohortResponse:
        """Validates a cohort."""
        return await handle_validate_cohort(self.deps, request)
