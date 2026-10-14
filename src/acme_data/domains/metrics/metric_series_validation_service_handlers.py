"""Reusable transport mixin for MetricSeriesValidationService."""

from __future__ import annotations

from collections.abc import AsyncIterator
import logging

import grpc

from acme.metrics.v1 import metric_series_history_service_pb2 as metrics_v1_metric_series_history_service_pb2
from acme.metrics.v1 import metric_series_validation_service_pb2 as metrics_v1_metric_series_validation_service_pb2

from acme_data.domains.metrics.dependencies import Dependencies
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class MetricSeriesValidationServicerHandlers:
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    async def CheckMetricSeriesEligibility(
        self, request: metrics_v1_metric_series_validation_service_pb2.CheckMetricSeriesEligibilityRequest, context: grpc.aio.ServicerContext,
    ) -> metrics_v1_metric_series_validation_service_pb2.CheckMetricSeriesEligibilityResponse:
        """Checks a metric series."""
        return await self.handle_check_metric_series_eligibility(request)

    @rpc_errors
    async def ExplainMetricSeriesDecision(
        self, request: metrics_v1_metric_series_validation_service_pb2.ExplainMetricSeriesDecisionRequest, context: grpc.aio.ServicerContext,
    ) -> metrics_v1_metric_series_validation_service_pb2.ExplainMetricSeriesDecisionResponse:
        """Explains a metric series."""
        return await self.handle_explain_metric_series_decision(request)

    @rpc_errors
    @retry_transient
    async def GetMetricSeriesRules(
        self, request: metrics_v1_metric_series_validation_service_pb2.GetMetricSeriesRulesRequest, context: grpc.aio.ServicerContext,
    ) -> metrics_v1_metric_series_validation_service_pb2.GetMetricSeriesRulesResponse:
        """Returns a metric series."""
        return await self.handle_get_metric_series_rules(request)

    @rpc_errors
    async def LintMetricSerieses(
        self, request: metrics_v1_metric_series_validation_service_pb2.LintMetricSeriesesRequest, context: grpc.aio.ServicerContext,
    ) -> metrics_v1_metric_series_validation_service_pb2.LintMetricSeriesesResponse:
        """Lints a metric series."""
        return await self.handle_lint_metric_serieses(request)

    @rpc_errors
    async def NormalizeMetricSeries(
        self, request: metrics_v1_metric_series_validation_service_pb2.NormalizeMetricSeriesRequest, context: grpc.aio.ServicerContext,
    ) -> metrics_v1_metric_series_validation_service_pb2.NormalizeMetricSeriesResponse:
        """Normalizes a metric series."""
        return await self.handle_normalize_metric_series(request)

    @rpc_errors
    async def PreviewMetricSeries(
        self, request: metrics_v1_metric_series_validation_service_pb2.PreviewMetricSeriesRequest, context: grpc.aio.ServicerContext,
    ) -> metrics_v1_metric_series_validation_service_pb2.PreviewMetricSeriesResponse:
        """Previews a metric series."""
        return await self.handle_preview_metric_series(request)

    @rpc_errors
    async def ScoreMetricSeries(
        self, request: metrics_v1_metric_series_validation_service_pb2.ScoreMetricSeriesRequest, context: grpc.aio.ServicerContext,
    ) -> metrics_v1_metric_series_validation_service_pb2.ScoreMetricSeriesResponse:
        """Scores a metric series."""
        return await self.handle_score_metric_series(request)

    @rpc_errors
    async def ValidateMetricSeries(
        self, request: metrics_v1_metric_series_validation_service_pb2.ValidateMetricSeriesRequest, context: grpc.aio.ServicerContext,
    ) -> metrics_v1_metric_series_validation_service_pb2.ValidateMetricSeriesResponse:
        """Validates a metric series."""
        return await self.handle_validate_metric_series(request)

    async def handle_check_metric_series_eligibility(
        self,
        request: metrics_v1_metric_series_validation_service_pb2.CheckMetricSeriesEligibilityRequest
    ) -> metrics_v1_metric_series_validation_service_pb2.CheckMetricSeriesEligibilityResponse:
        """Checks a metric series."""
        deps = self.deps
        response = metrics_v1_metric_series_validation_service_pb2.CheckMetricSeriesEligibilityResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CheckMetricSeriesEligibility', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'CheckMetricSeriesEligibility',
                {'reason': request.reason}
            )
            await deps.repository.save_metric_series(request.context.tenant_id, request.metric_series)
            echoed_0 = request.metric_series_id
            response.metric_series.metric_series_id = echoed_0
            echoed_1 = request.metric_series.owner
            response.metric_series.owner.CopyFrom(echoed_1)
            return response

    async def handle_explain_metric_series_decision(
        self,
        request: metrics_v1_metric_series_validation_service_pb2.ExplainMetricSeriesDecisionRequest
    ) -> metrics_v1_metric_series_validation_service_pb2.ExplainMetricSeriesDecisionResponse:
        """Explains a metric series."""
        deps = self.deps
        response = metrics_v1_metric_series_validation_service_pb2.ExplainMetricSeriesDecisionResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ExplainMetricSeriesDecision', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ExplainMetricSeriesDecision',
                {'reason': request.reason}
            )
            await deps.repository.save_metric_series(request.context.tenant_id, request.metric_series)
            echoed_0 = request.metric_series_id
            response.metric_series.metric_series_id = echoed_0
            echoed_1 = request.metric_series.status
            response.metric_series.status = echoed_1
            return response

    async def handle_get_metric_series_rules(
        self,
        request: metrics_v1_metric_series_validation_service_pb2.GetMetricSeriesRulesRequest
    ) -> metrics_v1_metric_series_validation_service_pb2.GetMetricSeriesRulesResponse:
        """Returns a metric series."""
        deps = self.deps
        response = metrics_v1_metric_series_validation_service_pb2.GetMetricSeriesRulesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('GetMetricSeriesRules', extra={'fields': {'domain': 'metrics'}})
            await deps.repository.audit(request.context.tenant_id, 'GetMetricSeriesRules', {})
            response_0 = metrics_v1_metric_series_history_service_pb2.PruneMetricSeriesVersionsResponse()
            outgoing_0 = metrics_v1_metric_series_history_service_pb2.PruneMetricSeriesVersionsRequest(
                context=request.context,
                metric_series_id=request.metric_series_id
            )
            response_0 = await deps.clients.metrics_metric_series_history.PruneMetricSeriesVersions(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_0)
            echoed_0 = request.metric_series_id
            response.metric_series.metric_series_id = echoed_0
            return response

    async def handle_lint_metric_serieses(
        self,
        request: metrics_v1_metric_series_validation_service_pb2.LintMetricSeriesesRequest
    ) -> metrics_v1_metric_series_validation_service_pb2.LintMetricSeriesesResponse:
        """Lints a metric series."""
        deps = self.deps
        response = metrics_v1_metric_series_validation_service_pb2.LintMetricSeriesesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('LintMetricSerieses', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'LintMetricSerieses', {'reason': request.reason})
            await deps.repository.save_metric_series(request.context.tenant_id, request.metric_series)
            echoed_0 = request.metric_series_id
            response.metric_series.metric_series_id = echoed_0
            echoed_1 = request.metric_series.name
            response.metric_series.name = echoed_1
            return response

    async def handle_normalize_metric_series(
        self,
        request: metrics_v1_metric_series_validation_service_pb2.NormalizeMetricSeriesRequest
    ) -> metrics_v1_metric_series_validation_service_pb2.NormalizeMetricSeriesResponse:
        """Normalizes a metric series."""
        deps = self.deps
        response = metrics_v1_metric_series_validation_service_pb2.NormalizeMetricSeriesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('NormalizeMetricSeries', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'NormalizeMetricSeries', {'reason': request.reason})
            await deps.repository.save_metric_series(request.context.tenant_id, request.metric_series)
            echoed_0 = request.metric_series_id
            response.metric_series.metric_series_id = echoed_0
            echoed_1 = request.metric_series.name
            response.metric_series.name = echoed_1
            return response

    async def handle_preview_metric_series(
        self,
        request: metrics_v1_metric_series_validation_service_pb2.PreviewMetricSeriesRequest
    ) -> metrics_v1_metric_series_validation_service_pb2.PreviewMetricSeriesResponse:
        """Previews a metric series."""
        deps = self.deps
        response = metrics_v1_metric_series_validation_service_pb2.PreviewMetricSeriesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('PreviewMetricSeries', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'PreviewMetricSeries', {'reason': request.reason})
            await deps.repository.save_metric_series(request.context.tenant_id, request.metric_series)
            echoed_0 = request.metric_series_id
            response.metric_series.metric_series_id = echoed_0
            echoed_1 = request.metric_series.capacity
            response.metric_series.capacity = echoed_1
            return response

    async def handle_score_metric_series(
        self,
        request: metrics_v1_metric_series_validation_service_pb2.ScoreMetricSeriesRequest
    ) -> metrics_v1_metric_series_validation_service_pb2.ScoreMetricSeriesResponse:
        """Scores a metric series."""
        deps = self.deps
        response = metrics_v1_metric_series_validation_service_pb2.ScoreMetricSeriesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ScoreMetricSeries', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'ScoreMetricSeries', {'reason': request.reason})
            await deps.repository.save_metric_series(request.context.tenant_id, request.metric_series)
            echoed_0 = request.metric_series_id
            response.metric_series.metric_series_id = echoed_0
            echoed_1 = request.metric_series.capacity
            response.metric_series.capacity = echoed_1
            return response

    async def handle_validate_metric_series(
        self,
        request: metrics_v1_metric_series_validation_service_pb2.ValidateMetricSeriesRequest
    ) -> metrics_v1_metric_series_validation_service_pb2.ValidateMetricSeriesResponse:
        """Validates a metric series."""
        deps = self.deps
        response = metrics_v1_metric_series_validation_service_pb2.ValidateMetricSeriesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ValidateMetricSeries', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'ValidateMetricSeries', {'reason': request.reason})
            await deps.repository.save_metric_series(request.context.tenant_id, request.metric_series)
            echoed_0 = request.metric_series_id
            response.metric_series.metric_series_id = echoed_0
            echoed_1 = request.metric_series.capacity
            response.metric_series.capacity = echoed_1
            return response
