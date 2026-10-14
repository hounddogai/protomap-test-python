"""Checks metric alerts against the rules before anything acts on them."""

from __future__ import annotations

from collections.abc import AsyncIterator

import grpc

from acme.metrics.v1 import metric_alert_validation_service_pb2 as metrics_v1_metric_alert_validation_service_pb2
from acme.metrics.v1 import (
    metric_alert_validation_service_pb2_grpc as metrics_v1_metric_alert_validation_service_pb2_grpc,
)

from acme_data.domains.metrics.dependencies import Dependencies
from acme_data.domains.metrics.metric_alert_validation_service_workflow import MetricAlertValidationServicerWorkflow
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors


class MetricAlertValidationServicer(
    metrics_v1_metric_alert_validation_service_pb2_grpc.MetricAlertValidationServiceServicer
):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps
        self.workflow = MetricAlertValidationServicerWorkflow(deps)

    @rpc_errors
    async def ExplainMetricAlertDecision(
        self, request: metrics_v1_metric_alert_validation_service_pb2.ExplainMetricAlertDecisionRequest, context: grpc.aio.ServicerContext,
    ) -> metrics_v1_metric_alert_validation_service_pb2.ExplainMetricAlertDecisionResponse:
        """Explains a metric alert."""
        return await self.workflow.handle_explain_metric_alert_decision(request)

    @rpc_errors
    @retry_transient
    async def GetMetricAlertRules(
        self, request: metrics_v1_metric_alert_validation_service_pb2.GetMetricAlertRulesRequest, context: grpc.aio.ServicerContext,
    ) -> metrics_v1_metric_alert_validation_service_pb2.GetMetricAlertRulesResponse:
        """Returns a metric alert."""
        return await self.workflow.handle_get_metric_alert_rules(request)

    @rpc_errors
    async def LintMetricAlerts(
        self, request: metrics_v1_metric_alert_validation_service_pb2.LintMetricAlertsRequest, context: grpc.aio.ServicerContext,
    ) -> metrics_v1_metric_alert_validation_service_pb2.LintMetricAlertsResponse:
        """Lints a metric alert."""
        return await self.workflow.handle_lint_metric_alerts(request)

    @rpc_errors
    async def NormalizeMetricAlert(
        self, request: metrics_v1_metric_alert_validation_service_pb2.NormalizeMetricAlertRequest, context: grpc.aio.ServicerContext,
    ) -> metrics_v1_metric_alert_validation_service_pb2.NormalizeMetricAlertResponse:
        """Normalizes a metric alert."""
        return await self.workflow.handle_normalize_metric_alert(request)

    @rpc_errors
    async def PreviewMetricAlert(
        self, request: metrics_v1_metric_alert_validation_service_pb2.PreviewMetricAlertRequest, context: grpc.aio.ServicerContext,
    ) -> metrics_v1_metric_alert_validation_service_pb2.PreviewMetricAlertResponse:
        """Previews a metric alert."""
        return await self.workflow.handle_preview_metric_alert(request)

    @rpc_errors
    async def ScoreMetricAlert(
        self, request: metrics_v1_metric_alert_validation_service_pb2.ScoreMetricAlertRequest, context: grpc.aio.ServicerContext,
    ) -> metrics_v1_metric_alert_validation_service_pb2.ScoreMetricAlertResponse:
        """Scores a metric alert."""
        return await self.workflow.handle_score_metric_alert(request)

    @rpc_errors
    async def ValidateMetricAlert(
        self, request: metrics_v1_metric_alert_validation_service_pb2.ValidateMetricAlertRequest, context: grpc.aio.ServicerContext,
    ) -> metrics_v1_metric_alert_validation_service_pb2.ValidateMetricAlertResponse:
        """Validates a metric alert."""
        return await self.workflow.handle_validate_metric_alert(request)
