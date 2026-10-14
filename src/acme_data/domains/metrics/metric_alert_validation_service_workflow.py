"""Application workflow for MetricAlert Validation."""

from __future__ import annotations

import logging

from acme.metrics.v1 import dashboard_export_service_pb2 as metrics_v1_dashboard_export_service_pb2
from acme.metrics.v1 import metric_alert_validation_service_pb2 as metrics_v1_metric_alert_validation_service_pb2

from acme_data.domains.metrics.dependencies import Dependencies
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class MetricAlertValidationServicerWorkflow:
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    async def handle_explain_metric_alert_decision(
        self,
        request: metrics_v1_metric_alert_validation_service_pb2.ExplainMetricAlertDecisionRequest
    ) -> metrics_v1_metric_alert_validation_service_pb2.ExplainMetricAlertDecisionResponse:
        """Explains a metric alert."""
        deps = self.deps
        response = metrics_v1_metric_alert_validation_service_pb2.ExplainMetricAlertDecisionResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ExplainMetricAlertDecision', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ExplainMetricAlertDecision',
                {'reason': request.reason}
            )
            await deps.repository.save_metric_alert(request.context.tenant_id, request.metric_alert)
            echoed_0 = request.metric_alert_id
            response.metric_alert.metric_alert_id = echoed_0
            echoed_1 = request.metric_alert.version
            response.metric_alert.version = echoed_1
            return response

    async def handle_get_metric_alert_rules(
        self,
        request: metrics_v1_metric_alert_validation_service_pb2.GetMetricAlertRulesRequest
    ) -> metrics_v1_metric_alert_validation_service_pb2.GetMetricAlertRulesResponse:
        """Returns a metric alert."""
        deps = self.deps
        response = metrics_v1_metric_alert_validation_service_pb2.GetMetricAlertRulesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('GetMetricAlertRules', extra={'fields': {'domain': 'metrics'}})
            await deps.repository.audit(request.context.tenant_id, 'GetMetricAlertRules', {})
            response_0 = metrics_v1_dashboard_export_service_pb2.ScheduleDashboardExportResponse()
            outgoing_0 = metrics_v1_dashboard_export_service_pb2.ScheduleDashboardExportRequest(
                annotations=dict(request.context.baggage),
                context=request.context
            )
            response_0 = await deps.clients.metrics_dashboard_export.ScheduleDashboardExport(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.status
            if returned_0_0:
                response.result.status = returned_0_0
            echoed_0 = request.metric_alert_id
            response.metric_alert.metric_alert_id = echoed_0
            return response

    async def handle_lint_metric_alerts(
        self,
        request: metrics_v1_metric_alert_validation_service_pb2.LintMetricAlertsRequest
    ) -> metrics_v1_metric_alert_validation_service_pb2.LintMetricAlertsResponse:
        """Lints a metric alert."""
        deps = self.deps
        response = metrics_v1_metric_alert_validation_service_pb2.LintMetricAlertsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('LintMetricAlerts', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'LintMetricAlerts', {'reason': request.reason})
            await deps.repository.save_metric_alert(request.context.tenant_id, request.metric_alert)
            echoed_0 = request.metric_alert_id
            response.metric_alert.metric_alert_id = echoed_0
            echoed_1 = request.metric_alert.effective
            response.metric_alert.effective.CopyFrom(echoed_1)
            return response

    async def handle_normalize_metric_alert(
        self,
        request: metrics_v1_metric_alert_validation_service_pb2.NormalizeMetricAlertRequest
    ) -> metrics_v1_metric_alert_validation_service_pb2.NormalizeMetricAlertResponse:
        """Normalizes a metric alert."""
        deps = self.deps
        response = metrics_v1_metric_alert_validation_service_pb2.NormalizeMetricAlertResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('NormalizeMetricAlert', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'NormalizeMetricAlert', {'reason': request.reason})
            await deps.repository.save_metric_alert(request.context.tenant_id, request.metric_alert)
            echoed_0 = request.metric_alert_id
            response.metric_alert.metric_alert_id = echoed_0
            echoed_1 = request.metric_alert.version
            response.metric_alert.version = echoed_1
            return response

    async def handle_preview_metric_alert(
        self,
        request: metrics_v1_metric_alert_validation_service_pb2.PreviewMetricAlertRequest
    ) -> metrics_v1_metric_alert_validation_service_pb2.PreviewMetricAlertResponse:
        """Previews a metric alert."""
        deps = self.deps
        response = metrics_v1_metric_alert_validation_service_pb2.PreviewMetricAlertResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('PreviewMetricAlert', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'PreviewMetricAlert', {'reason': request.reason})
            await deps.repository.save_metric_alert(request.context.tenant_id, request.metric_alert)
            echoed_0 = request.metric_alert_id
            response.metric_alert.metric_alert_id = echoed_0
            echoed_1 = request.metric_alert.version
            response.metric_alert.version = echoed_1
            return response

    async def handle_score_metric_alert(
        self,
        request: metrics_v1_metric_alert_validation_service_pb2.ScoreMetricAlertRequest
    ) -> metrics_v1_metric_alert_validation_service_pb2.ScoreMetricAlertResponse:
        """Scores a metric alert."""
        deps = self.deps
        response = metrics_v1_metric_alert_validation_service_pb2.ScoreMetricAlertResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ScoreMetricAlert', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'ScoreMetricAlert', {'reason': request.reason})
            await deps.repository.save_metric_alert(request.context.tenant_id, request.metric_alert)
            echoed_0 = request.metric_alert_id
            response.metric_alert.metric_alert_id = echoed_0
            echoed_1 = request.metric_alert.status
            response.metric_alert.status = echoed_1
            return response

    async def handle_validate_metric_alert(
        self,
        request: metrics_v1_metric_alert_validation_service_pb2.ValidateMetricAlertRequest
    ) -> metrics_v1_metric_alert_validation_service_pb2.ValidateMetricAlertResponse:
        """Validates a metric alert."""
        deps = self.deps
        response = metrics_v1_metric_alert_validation_service_pb2.ValidateMetricAlertResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ValidateMetricAlert', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'ValidateMetricAlert', {'reason': request.reason})
            await deps.repository.save_metric_alert(request.context.tenant_id, request.metric_alert)
            echoed_0 = request.metric_alert_id
            response.metric_alert.metric_alert_id = echoed_0
            echoed_1 = request.metric_alert.description
            response.metric_alert.description = echoed_1
            return response
