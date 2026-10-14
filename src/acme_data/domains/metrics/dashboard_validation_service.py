"""Checks dashboards against the rules before anything acts on them."""

from __future__ import annotations

from collections.abc import AsyncIterator
import logging

import grpc

from acme.metrics.v1 import dashboard_validation_service_pb2 as metrics_v1_dashboard_validation_service_pb2
from acme.metrics.v1 import dashboard_validation_service_pb2_grpc as metrics_v1_dashboard_validation_service_pb2_grpc
from acme.metrics.v1 import metric_alert_export_service_pb2 as metrics_v1_metric_alert_export_service_pb2

from acme_data.domains.metrics.dependencies import Dependencies
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class DashboardValidationServicer(metrics_v1_dashboard_validation_service_pb2_grpc.DashboardValidationServiceServicer):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    async def CheckDashboardEligibility(
        self, request: metrics_v1_dashboard_validation_service_pb2.CheckDashboardEligibilityRequest, context: grpc.aio.ServicerContext,
    ) -> metrics_v1_dashboard_validation_service_pb2.CheckDashboardEligibilityResponse:
        """Checks a dashboard."""
        return await self.handle_check_dashboard_eligibility(request)

    @rpc_errors
    async def ExplainDashboardDecision(
        self, request: metrics_v1_dashboard_validation_service_pb2.ExplainDashboardDecisionRequest, context: grpc.aio.ServicerContext,
    ) -> metrics_v1_dashboard_validation_service_pb2.ExplainDashboardDecisionResponse:
        """Explains a dashboard."""
        return await self.handle_explain_dashboard_decision(request)

    @rpc_errors
    @retry_transient
    async def GetDashboardRules(
        self, request: metrics_v1_dashboard_validation_service_pb2.GetDashboardRulesRequest, context: grpc.aio.ServicerContext,
    ) -> metrics_v1_dashboard_validation_service_pb2.GetDashboardRulesResponse:
        """Returns a dashboard."""
        return await self.handle_get_dashboard_rules(request)

    @rpc_errors
    async def LintDashboards(
        self, request: metrics_v1_dashboard_validation_service_pb2.LintDashboardsRequest, context: grpc.aio.ServicerContext,
    ) -> metrics_v1_dashboard_validation_service_pb2.LintDashboardsResponse:
        """Lints a dashboard."""
        return await self.handle_lint_dashboards(request)

    @rpc_errors
    async def NormalizeDashboard(
        self, request: metrics_v1_dashboard_validation_service_pb2.NormalizeDashboardRequest, context: grpc.aio.ServicerContext,
    ) -> metrics_v1_dashboard_validation_service_pb2.NormalizeDashboardResponse:
        """Normalizes a dashboard."""
        return await self.handle_normalize_dashboard(request)

    @rpc_errors
    async def PreviewDashboard(
        self, request: metrics_v1_dashboard_validation_service_pb2.PreviewDashboardRequest, context: grpc.aio.ServicerContext,
    ) -> metrics_v1_dashboard_validation_service_pb2.PreviewDashboardResponse:
        """Previews a dashboard."""
        return await self.handle_preview_dashboard(request)

    @rpc_errors
    async def ScoreDashboard(
        self, request: metrics_v1_dashboard_validation_service_pb2.ScoreDashboardRequest, context: grpc.aio.ServicerContext,
    ) -> metrics_v1_dashboard_validation_service_pb2.ScoreDashboardResponse:
        """Scores a dashboard."""
        return await self.handle_score_dashboard(request)

    @rpc_errors
    async def ValidateDashboard(
        self, request: metrics_v1_dashboard_validation_service_pb2.ValidateDashboardRequest, context: grpc.aio.ServicerContext,
    ) -> metrics_v1_dashboard_validation_service_pb2.ValidateDashboardResponse:
        """Validates a dashboard."""
        return await self.handle_validate_dashboard(request)

    async def handle_check_dashboard_eligibility(
        self,
        request: metrics_v1_dashboard_validation_service_pb2.CheckDashboardEligibilityRequest
    ) -> metrics_v1_dashboard_validation_service_pb2.CheckDashboardEligibilityResponse:
        """Checks a dashboard."""
        deps = self.deps
        response = metrics_v1_dashboard_validation_service_pb2.CheckDashboardEligibilityResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CheckDashboardEligibility', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'CheckDashboardEligibility',
                {'reason': request.reason}
            )
            await deps.repository.save_dashboard(request.context.tenant_id, request.dashboard)
            response_0 = metrics_v1_metric_alert_export_service_pb2.StreamMetricAlertExportResponse()
            outgoing_0 = metrics_v1_metric_alert_export_service_pb2.StreamMetricAlertExportRequest(
                context=request.context,
                filter=metrics_v1_metric_alert_export_service_pb2.StreamMetricAlertExportRequest.Filter(
                    created_after=request.dashboard.audit.updated_at,
                    labels=dict(request.annotations),
                    owner_id=request.dashboard.counterparty.metric_alert_id,
                    region=request.dashboard.billing_address.region
                )
            )
            async for chunk_0 in deps.clients.metrics_metric_alert_export.StreamMetricAlertExport(
                outgoing_0,
                timeout=deps.settings.timeout
            ):
                response_0 = chunk_0
            echoed_0 = request.dashboard_id
            response.dashboard.dashboard_id = echoed_0
            echoed_1 = request.dashboard.status
            response.dashboard.status = echoed_1
            return response

    async def handle_explain_dashboard_decision(
        self,
        request: metrics_v1_dashboard_validation_service_pb2.ExplainDashboardDecisionRequest
    ) -> metrics_v1_dashboard_validation_service_pb2.ExplainDashboardDecisionResponse:
        """Explains a dashboard."""
        deps = self.deps
        response = metrics_v1_dashboard_validation_service_pb2.ExplainDashboardDecisionResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ExplainDashboardDecision', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ExplainDashboardDecision',
                {'reason': request.reason}
            )
            await deps.repository.save_dashboard(request.context.tenant_id, request.dashboard)
            echoed_0 = request.dashboard_id
            response.dashboard.dashboard_id = echoed_0
            echoed_1 = request.dashboard.counterparty
            response.dashboard.counterparty.CopyFrom(echoed_1)
            return response

    async def handle_get_dashboard_rules(
        self,
        request: metrics_v1_dashboard_validation_service_pb2.GetDashboardRulesRequest
    ) -> metrics_v1_dashboard_validation_service_pb2.GetDashboardRulesResponse:
        """Returns a dashboard."""
        deps = self.deps
        response = metrics_v1_dashboard_validation_service_pb2.GetDashboardRulesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('GetDashboardRules', extra={'fields': {'locale': request.context.locale}})
            await deps.repository.audit(
                request.context.tenant_id,
                'GetDashboardRules',
                {'locale': request.context.locale}
            )
            echoed_0 = request.dashboard_id
            response.dashboard.dashboard_id = echoed_0
            return response

    async def handle_lint_dashboards(
        self,
        request: metrics_v1_dashboard_validation_service_pb2.LintDashboardsRequest
    ) -> metrics_v1_dashboard_validation_service_pb2.LintDashboardsResponse:
        """Lints a dashboard."""
        deps = self.deps
        response = metrics_v1_dashboard_validation_service_pb2.LintDashboardsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('LintDashboards', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'LintDashboards', {'reason': request.reason})
            await deps.repository.save_dashboard(request.context.tenant_id, request.dashboard)
            echoed_0 = request.dashboard_id
            response.dashboard.dashboard_id = echoed_0
            echoed_1 = request.dashboard.notes
            response.dashboard.notes = echoed_1
            return response

    async def handle_normalize_dashboard(
        self,
        request: metrics_v1_dashboard_validation_service_pb2.NormalizeDashboardRequest
    ) -> metrics_v1_dashboard_validation_service_pb2.NormalizeDashboardResponse:
        """Normalizes a dashboard."""
        deps = self.deps
        response = metrics_v1_dashboard_validation_service_pb2.NormalizeDashboardResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('NormalizeDashboard', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'NormalizeDashboard', {'reason': request.reason})
            await deps.repository.save_dashboard(request.context.tenant_id, request.dashboard)
            echoed_0 = request.dashboard_id
            response.dashboard.dashboard_id = echoed_0
            echoed_1 = request.dashboard.notes
            response.dashboard.notes = echoed_1
            return response

    async def handle_preview_dashboard(
        self,
        request: metrics_v1_dashboard_validation_service_pb2.PreviewDashboardRequest
    ) -> metrics_v1_dashboard_validation_service_pb2.PreviewDashboardResponse:
        """Previews a dashboard."""
        deps = self.deps
        response = metrics_v1_dashboard_validation_service_pb2.PreviewDashboardResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('PreviewDashboard', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'PreviewDashboard', {'reason': request.reason})
            await deps.repository.save_dashboard(request.context.tenant_id, request.dashboard)
            echoed_0 = request.dashboard_id
            response.dashboard.dashboard_id = echoed_0
            echoed_1 = request.dashboard.total
            response.dashboard.total.CopyFrom(echoed_1)
            return response

    async def handle_score_dashboard(
        self,
        request: metrics_v1_dashboard_validation_service_pb2.ScoreDashboardRequest
    ) -> metrics_v1_dashboard_validation_service_pb2.ScoreDashboardResponse:
        """Scores a dashboard."""
        deps = self.deps
        response = metrics_v1_dashboard_validation_service_pb2.ScoreDashboardResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ScoreDashboard', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'ScoreDashboard', {'reason': request.reason})
            await deps.repository.save_dashboard(request.context.tenant_id, request.dashboard)
            echoed_0 = request.dashboard_id
            response.dashboard.dashboard_id = echoed_0
            echoed_1 = request.details.currency_code
            response.breakdown.currency_code = echoed_1
            return response

    async def handle_validate_dashboard(
        self,
        request: metrics_v1_dashboard_validation_service_pb2.ValidateDashboardRequest
    ) -> metrics_v1_dashboard_validation_service_pb2.ValidateDashboardResponse:
        """Validates a dashboard."""
        deps = self.deps
        response = metrics_v1_dashboard_validation_service_pb2.ValidateDashboardResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ValidateDashboard', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'ValidateDashboard', {'reason': request.reason})
            await deps.repository.save_dashboard(request.context.tenant_id, request.dashboard)
            echoed_0 = request.dashboard_id
            response.dashboard.dashboard_id = echoed_0
            echoed_1 = request.dashboard.number
            response.dashboard.number = echoed_1
            return response
