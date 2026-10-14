"""Reusable transport mixin for AnomalyFeedbackValidationService."""

from __future__ import annotations

from collections.abc import AsyncIterator
from collections.abc import Awaitable
from collections.abc import Callable
from functools import partial
from typing import cast
import asyncio
import logging

from google.protobuf.any_pb2 import Any as AnyMessage
from google.protobuf.json_format import MessageToJson
from google.protobuf.json_format import Parse
import grpc

from acme.anomalies.v1 import anomalies_pb2 as anomalies_v1_anomalies_pb2
from acme.anomalies.v1 import (
    anomaly_feedback_calculation_service_pb2 as anomalies_v1_anomaly_feedback_calculation_service_pb2,
)
from acme.anomalies.v1 import (
    anomaly_feedback_validation_service_pb2 as anomalies_v1_anomaly_feedback_validation_service_pb2,
)
from acme.anomalies.v1 import detector_validation_service_pb2 as anomalies_v1_detector_validation_service_pb2
from acme.audit.v1 import audit_event_query_service_pb2 as audit_v1_audit_event_query_service_pb2
from acme.boxoffice.v1 import box_office_sale_query_service_pb2 as boxoffice_v1_box_office_sale_query_service_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.datasets.v1 import refs_pb2 as datasets_v1_refs_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.lineage.v1 import impact_calculation_service_pb2 as lineage_v1_impact_calculation_service_pb2
from acme.lineage.v1 import impact_validation_service_pb2 as lineage_v1_impact_validation_service_pb2
from acme.lineage.v1 import lineage_edge_query_service_pb2 as lineage_v1_lineage_edge_query_service_pb2
from acme.lineage.v1 import lineage_node_query_service_pb2 as lineage_v1_lineage_node_query_service_pb2
from acme.lineage.v1 import lineage_pb2 as lineage_v1_lineage_pb2
from acme.metrics.v1 import dashboard_validation_service_pb2 as metrics_v1_dashboard_validation_service_pb2
from acme.metrics.v1 import dashboard_validation_service_pb2_grpc as metrics_v1_dashboard_validation_service_pb2_grpc
from acme.metrics.v1 import metric_series_notification_service_pb2 as metrics_v1_metric_series_notification_service_pb2
from acme.metrics.v1 import metrics_pb2 as metrics_v1_metrics_pb2
from acme.telematics.v1 import refs_pb2 as telematics_v1_refs_pb2
from acme.telematics.v1 import telematics_pb2 as telematics_v1_telematics_pb2
from acme.telematics.v1 import telemetry_reading_service_pb2 as telematics_v1_telemetry_reading_service_pb2

from acme_data.domains.anomalies import hooks
from acme_data.domains.anomalies.adapters import AnomalyFeedbackValidationCheckAnomalyFeedbackEligibility0Adapter
from acme_data.domains.anomalies.adapters import AnomalyFeedbackValidationScoreAnomalyFeedback0Adapter
from acme_data.domains.anomalies.adapters import AnomalyFeedbackValidationScoreAnomalyFeedback0Port
from acme_data.domains.anomalies.dependencies import Dependencies
from acme_data.domains.anomalies.models import AnomalyFeedbackValidationNormalizeAnomalyFeedback1Command
from acme_data.domains.anomalies.models import to_anomaly_feedback_validation_normalize_anomaly_feedback1_command
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_id
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class AnomalyFeedbackValidationServicerHandlers:
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    async def CheckAnomalyFeedbackEligibility(
        self, request: anomalies_v1_anomaly_feedback_validation_service_pb2.CheckAnomalyFeedbackEligibilityRequest, context: grpc.aio.ServicerContext,
    ) -> anomalies_v1_anomaly_feedback_validation_service_pb2.CheckAnomalyFeedbackEligibilityResponse:
        """Checks an anomaly feedback."""
        return await self.handle_check_anomaly_feedback_eligibility(request)

    @rpc_errors
    async def ExplainAnomalyFeedbackDecision(
        self, request: anomalies_v1_anomaly_feedback_validation_service_pb2.ExplainAnomalyFeedbackDecisionRequest, context: grpc.aio.ServicerContext,
    ) -> anomalies_v1_anomaly_feedback_validation_service_pb2.ExplainAnomalyFeedbackDecisionResponse:
        """Explains an anomaly feedback."""
        return await self.handle_explain_anomaly_feedback_decision(request)

    @rpc_errors
    @retry_transient
    async def GetAnomalyFeedbackRules(
        self, request: anomalies_v1_anomaly_feedback_validation_service_pb2.GetAnomalyFeedbackRulesRequest, context: grpc.aio.ServicerContext,
    ) -> anomalies_v1_anomaly_feedback_validation_service_pb2.GetAnomalyFeedbackRulesResponse:
        """Returns an anomaly feedback."""
        return await self.handle_get_anomaly_feedback_rules(request)

    @rpc_errors
    async def LintAnomalyFeedbacks(
        self, request: anomalies_v1_anomaly_feedback_validation_service_pb2.LintAnomalyFeedbacksRequest, context: grpc.aio.ServicerContext,
    ) -> anomalies_v1_anomaly_feedback_validation_service_pb2.LintAnomalyFeedbacksResponse:
        """Lints an anomaly feedback."""
        return await self.handle_lint_anomaly_feedbacks(request)

    @rpc_errors
    async def NormalizeAnomalyFeedback(
        self, request: anomalies_v1_anomaly_feedback_validation_service_pb2.NormalizeAnomalyFeedbackRequest, context: grpc.aio.ServicerContext,
    ) -> anomalies_v1_anomaly_feedback_validation_service_pb2.NormalizeAnomalyFeedbackResponse:
        """Normalizes an anomaly feedback."""
        return await self.handle_normalize_anomaly_feedback(request)

    @rpc_errors
    async def PreviewAnomalyFeedback(
        self, request: anomalies_v1_anomaly_feedback_validation_service_pb2.PreviewAnomalyFeedbackRequest, context: grpc.aio.ServicerContext,
    ) -> anomalies_v1_anomaly_feedback_validation_service_pb2.PreviewAnomalyFeedbackResponse:
        """Previews an anomaly feedback."""
        return await self.handle_preview_anomaly_feedback(request)

    @rpc_errors
    async def ScoreAnomalyFeedback(
        self, request: anomalies_v1_anomaly_feedback_validation_service_pb2.ScoreAnomalyFeedbackRequest, context: grpc.aio.ServicerContext,
    ) -> anomalies_v1_anomaly_feedback_validation_service_pb2.ScoreAnomalyFeedbackResponse:
        """Scores an anomaly feedback."""
        return await self.handle_score_anomaly_feedback(request)

    @rpc_errors
    async def ValidateAnomalyFeedback(
        self, request: anomalies_v1_anomaly_feedback_validation_service_pb2.ValidateAnomalyFeedbackRequest, context: grpc.aio.ServicerContext,
    ) -> anomalies_v1_anomaly_feedback_validation_service_pb2.ValidateAnomalyFeedbackResponse:
        """Validates an anomaly feedback."""
        return await self.handle_validate_anomaly_feedback(request)

    async def handle_check_anomaly_feedback_eligibility(
        self,
        request: anomalies_v1_anomaly_feedback_validation_service_pb2.CheckAnomalyFeedbackEligibilityRequest
    ) -> anomalies_v1_anomaly_feedback_validation_service_pb2.CheckAnomalyFeedbackEligibilityResponse:
        """Checks an anomaly feedback."""
        deps = self.deps
        response = anomalies_v1_anomaly_feedback_validation_service_pb2.CheckAnomalyFeedbackEligibilityResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CheckAnomalyFeedbackEligibility', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'CheckAnomalyFeedbackEligibility',
                {'reason': request.reason}
            )
            await deps.repository.save_anomaly_feedback(request.context.tenant_id, request.anomaly_feedback)
            response_0 = boxoffice_v1_box_office_sale_query_service_pb2.ResolveBoxOfficeSalesResponse()
            response_1 = lineage_v1_impact_validation_service_pb2.ExplainImpactDecisionResponse()
            response_2 = metrics_v1_metric_series_notification_service_pb2.NotifyMetricSeriesWatchersResponse()
            outgoing_0 = boxoffice_v1_box_office_sale_query_service_pb2.ResolveBoxOfficeSalesRequest(
                context=request.context
            )
            response_0 = await AnomalyFeedbackValidationCheckAnomalyFeedbackEligibility0Adapter(
                deps.clients.boxoffice_box_office_sale_query,
                deps.settings.timeout
            )(outgoing_0)
            outgoing_1 = lineage_v1_impact_validation_service_pb2.ExplainImpactDecisionRequest(
                context=request.context,
                impact=lineage_v1_lineage_pb2.Impact(
                    requester=common_v1_contact_pb2.ContactInfo(email=request.details.contact.email)
                )
            )
            response_1 = cast(lineage_v1_impact_validation_service_pb2.ExplainImpactDecisionResponse, await deps.bus.request(
                'acme.anomalies.v1.AnomalyFeedbackValidationService/CheckAnomalyFeedbackEligibility/1', outgoing_1, deps.settings.timeout,
            ))
            outgoing_2 = metrics_v1_metric_series_notification_service_pb2.NotifyMetricSeriesWatchersRequest(
                context=request.context,
                details=metrics_v1_metric_series_notification_service_pb2.NotifyMetricSeriesWatchersRequest.Details(
                    recipient=common_v1_contact_pb2.ContactInfo(
                        email=response_1.impact.assignee.email,
                        name=response_1.impact.requester.name,
                        phone=request.details.contact.phone,
                        preferred_channel=response_1.impact.requester.preferred_channel
                    )
                )
            )
            response_2 = await deps.clients.metrics_metric_series_notification.NotifyMetricSeriesWatchers(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.status
            if returned_0_0:
                response.outcome.status = returned_0_0
            returned_0_1 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_1)
            returned_1_0 = response_1.result.message
            if returned_1_0:
                response.result.message = returned_1_0
            returned_2_0 = response_2.outcome.effective_at
            if returned_2_0.ListFields():
                response.outcome.effective_at.MergeFrom(returned_2_0)
            returned_2_1 = response_2.outcome.reference_id
            if returned_2_1:
                response.outcome.reference_id = returned_2_1
            echoed_0 = request.anomaly_feedback_id
            response.anomaly_feedback.anomaly_feedback_id = echoed_0
            echoed_1 = request.anomaly_feedback.attributes
            response.anomaly_feedback.attributes.update(echoed_1)
            return response

    async def handle_explain_anomaly_feedback_decision(
        self,
        request: anomalies_v1_anomaly_feedback_validation_service_pb2.ExplainAnomalyFeedbackDecisionRequest
    ) -> anomalies_v1_anomaly_feedback_validation_service_pb2.ExplainAnomalyFeedbackDecisionResponse:
        """Explains an anomaly feedback."""
        deps = self.deps
        response = anomalies_v1_anomaly_feedback_validation_service_pb2.ExplainAnomalyFeedbackDecisionResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ExplainAnomalyFeedbackDecision', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ExplainAnomalyFeedbackDecision',
                {'reason': request.reason}
            )
            await deps.repository.save_anomaly_feedback(request.context.tenant_id, request.anomaly_feedback)
            response_0 = lineage_v1_lineage_edge_query_service_pb2.ResolveLineageEdgesResponse()
            response_1 = anomalies_v1_detector_validation_service_pb2.ScoreDetectorResponse()
            outgoing_0 = lineage_v1_lineage_edge_query_service_pb2.ResolveLineageEdgesRequest(context=request.context)
            outgoing_1 = anomalies_v1_detector_validation_service_pb2.ScoreDetectorRequest(
                context=request.context,
                detector=anomalies_v1_anomalies_pb2.Detector(
                    owner=identity_v1_refs_pb2.UserRef(email=request.details.contact.email)
                )
            )
            response_0, response_1 = await asyncio.gather(
                deps.clients.lineage_lineage_edge_query.ResolveLineageEdges(outgoing_0, timeout=deps.settings.timeout),
                deps.clients.anomalies_detector_validation.ScoreDetector(outgoing_1, timeout=deps.settings.timeout),
            )
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.outcome.message = returned_0_0
            returned_0_1 = response_0.result.correlation_id
            if returned_0_1:
                response.anomaly_feedback.correlation_id = returned_0_1
            returned_1_0 = response_1.result.message
            if returned_1_0:
                response.outcome.message = returned_1_0
            returned_1_1 = response_1.detector.owner.display_name
            if returned_1_1:
                response.anomaly_feedback.subject.display_name = returned_1_1
            echoed_0 = request.anomaly_feedback_id
            response.anomaly_feedback.anomaly_feedback_id = echoed_0
            echoed_1 = request.anomaly_feedback.attributes
            response.anomaly_feedback.attributes.update(echoed_1)
            return response

    async def handle_get_anomaly_feedback_rules(
        self,
        request: anomalies_v1_anomaly_feedback_validation_service_pb2.GetAnomalyFeedbackRulesRequest
    ) -> anomalies_v1_anomaly_feedback_validation_service_pb2.GetAnomalyFeedbackRulesResponse:
        """Returns an anomaly feedback."""
        deps = self.deps
        response = anomalies_v1_anomaly_feedback_validation_service_pb2.GetAnomalyFeedbackRulesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('GetAnomalyFeedbackRules', extra={'fields': {'domain': 'anomalies'}})
            await deps.repository.audit(request.context.tenant_id, 'GetAnomalyFeedbackRules', {})
            response_0 = anomalies_v1_detector_validation_service_pb2.ExplainDetectorDecisionResponse()
            outgoing_0 = anomalies_v1_detector_validation_service_pb2.ExplainDetectorDecisionRequest(
                context=request.context,
                detector=anomalies_v1_anomalies_pb2.Detector(
                    owner=identity_v1_refs_pb2.UserRef(
                        email=request.context.actor.email,
                        user_id=request.context.actor.user_id
                    )
                )
            )
            response_0 = await deps.clients.anomalies_detector_validation.ExplainDetectorDecision(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_0)
            returned_0_1 = response_0.result.message
            if returned_0_1:
                response.result.message = returned_0_1
            echoed_0 = request.anomaly_feedback_id
            response.anomaly_feedback.anomaly_feedback_id = echoed_0
            return response

    async def handle_lint_anomaly_feedbacks(
        self,
        request: anomalies_v1_anomaly_feedback_validation_service_pb2.LintAnomalyFeedbacksRequest
    ) -> anomalies_v1_anomaly_feedback_validation_service_pb2.LintAnomalyFeedbacksResponse:
        """Lints an anomaly feedback."""
        deps = self.deps
        response = anomalies_v1_anomaly_feedback_validation_service_pb2.LintAnomalyFeedbacksResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('LintAnomalyFeedbacks', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'LintAnomalyFeedbacks', {'reason': request.reason})
            await deps.repository.save_anomaly_feedback(request.context.tenant_id, request.anomaly_feedback)
            response_0 = anomalies_v1_anomaly_feedback_calculation_service_pb2.QuoteAnomalyFeedbackResponse()
            response_1 = anomalies_v1_anomaly_feedback_calculation_service_pb2.EstimateAnomalyFeedbackResponse()
            response_2 = audit_v1_audit_event_query_service_pb2.ResolveAuditEventsResponse()
            response_3 = metrics_v1_dashboard_validation_service_pb2.ValidateDashboardResponse()
            outgoing_0 = anomalies_v1_anomaly_feedback_calculation_service_pb2.QuoteAnomalyFeedbackRequest(
                anomaly_feedback=anomalies_v1_anomalies_pb2.AnomalyFeedback(
                    subject=datasets_v1_refs_pb2.DatasetRef(code=request.anomaly_feedback.subject.code)
                ),
                context=request.context
            )
            document_0 = MessageToJson(outgoing_0, preserving_proto_field_name=True)
            outgoing_0 = Parse(
                document_0,
                anomalies_v1_anomaly_feedback_calculation_service_pb2.QuoteAnomalyFeedbackRequest()
            )
            response_0 = await deps.clients.anomalies_anomaly_feedback_calculation.QuoteAnomalyFeedback(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            callbacks_1: list[
                Callable[
                    [],
                    Awaitable[anomalies_v1_anomaly_feedback_calculation_service_pb2.EstimateAnomalyFeedbackResponse]
                ]
            ] = []
            for item_1 in request.anomaly_feedback.measurements:
                outgoing_1 = anomalies_v1_anomaly_feedback_calculation_service_pb2.EstimateAnomalyFeedbackRequest(
                    anomaly_feedback=anomalies_v1_anomalies_pb2.AnomalyFeedback(
                        measurements=[
                            anomalies_v1_anomalies_pb2.AnomalyFeedbackMeasurement(unit=item_1.unit, value=item_1.value)
                        ]
                    ),
                    context=request.context
                )
                async def send_1(
                    payload: anomalies_v1_anomaly_feedback_calculation_service_pb2.EstimateAnomalyFeedbackRequest = outgoing_1
                ) -> anomalies_v1_anomaly_feedback_calculation_service_pb2.EstimateAnomalyFeedbackResponse:
                    return await deps.clients.anomalies_anomaly_feedback_calculation.EstimateAnomalyFeedback(
                        payload,
                        timeout=deps.settings.timeout
                    )
                callbacks_1.append(send_1)
            for callback_1 in callbacks_1:
                response_1 = await callback_1()
            outgoing_2 = audit_v1_audit_event_query_service_pb2.ResolveAuditEventsRequest(context=request.context)
            envelope_2 = AnyMessage()
            envelope_2.Pack(outgoing_2)
            outgoing_2 = audit_v1_audit_event_query_service_pb2.ResolveAuditEventsRequest()
            if not envelope_2.Unpack(outgoing_2):
                raise ValueError("partner envelope contains the wrong request type")
            response_2 = await deps.clients.audit_audit_event_query.ResolveAuditEvents(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            outgoing_3 = metrics_v1_dashboard_validation_service_pb2.ValidateDashboardRequest(
                context=request.context,
                dashboard=metrics_v1_metrics_pb2.Dashboard(
                    lines=[
                        metrics_v1_metrics_pb2.DashboardLine(attributes=dict(response_0.anomaly_feedback.attributes))
                    ],
                    total=response_0.breakdown.total
                ),
                details=metrics_v1_dashboard_validation_service_pb2.ValidateDashboardRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(
                        email=request.details.contact.email,
                        phone=request.details.contact.phone
                    )
                )
            )
            registered_3 = cast(
                metrics_v1_dashboard_validation_service_pb2_grpc.DashboardValidationServiceStub,
                deps.clients.registry['acme.metrics.v1.DashboardValidationService']
            )
            response_3 = await registered_3.ValidateDashboard(outgoing_3, timeout=deps.settings.timeout)
            returned_0_0 = response_0.anomaly_feedback.subject.display_name
            if returned_0_0:
                response.anomaly_feedback.subject.display_name = returned_0_0
            returned_2_0 = response_2.result.reference_ids
            response.result.reference_ids.extend(returned_2_0)
            returned_2_1 = response_2.result.status
            if returned_2_1:
                response.result.status = returned_2_1
            returned_3_0 = response_3.result.message
            if returned_3_0:
                response.outcome.message = returned_3_0
            echoed_0 = request.anomaly_feedback_id
            response.anomaly_feedback.anomaly_feedback_id = echoed_0
            echoed_1 = request.anomaly_feedback.correlation_id
            response.anomaly_feedback.correlation_id = echoed_1
            return response

    async def handle_normalize_anomaly_feedback(
        self,
        request: anomalies_v1_anomaly_feedback_validation_service_pb2.NormalizeAnomalyFeedbackRequest
    ) -> anomalies_v1_anomaly_feedback_validation_service_pb2.NormalizeAnomalyFeedbackResponse:
        """Normalizes an anomaly feedback."""
        deps = self.deps
        response = anomalies_v1_anomaly_feedback_validation_service_pb2.NormalizeAnomalyFeedbackResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('NormalizeAnomalyFeedback', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'NormalizeAnomalyFeedback',
                {'reason': request.reason}
            )
            await deps.repository.save_anomaly_feedback(request.context.tenant_id, request.anomaly_feedback)
            response_0 = anomalies_v1_detector_validation_service_pb2.LintDetectorsResponse()
            response_1 = anomalies_v1_detector_validation_service_pb2.ValidateDetectorResponse()
            async for item_0 in async_messages(request.anomaly_feedback.measurements):
                outgoing_0 = anomalies_v1_detector_validation_service_pb2.LintDetectorsRequest(
                    context=request.context,
                    detector=anomalies_v1_anomalies_pb2.Detector(
                        audit=common_v1_audit_pb2.AuditInfo(created_at=item_0.observed_at)
                    )
                )
                response_0 = await deps.clients.anomalies_detector_validation.LintDetectors(
                    outgoing_0,
                    timeout=deps.settings.timeout
                )
            command_1 = AnomalyFeedbackValidationNormalizeAnomalyFeedback1Command.model_validate(
                {'context': request.context, 'detector_block_reason': response_0.detector.block.reason}
            )
            outgoing_1 = to_anomaly_feedback_validation_normalize_anomaly_feedback1_command(command_1)
            response_1 = await deps.clients.anomalies_detector_validation.ValidateDetector(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_1_0 = response_1.outcome.status
            if returned_1_0:
                response.result.status = returned_1_0
            echoed_0 = request.anomaly_feedback_id
            response.anomaly_feedback.anomaly_feedback_id = echoed_0
            echoed_1 = request.anomaly_feedback.correlation_id
            response.anomaly_feedback.correlation_id = echoed_1
            return response

    async def handle_preview_anomaly_feedback(
        self,
        request: anomalies_v1_anomaly_feedback_validation_service_pb2.PreviewAnomalyFeedbackRequest
    ) -> anomalies_v1_anomaly_feedback_validation_service_pb2.PreviewAnomalyFeedbackResponse:
        """Previews an anomaly feedback."""
        deps = self.deps
        response = anomalies_v1_anomaly_feedback_validation_service_pb2.PreviewAnomalyFeedbackResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('PreviewAnomalyFeedback', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'PreviewAnomalyFeedback', {'reason': request.reason})
            await deps.repository.save_anomaly_feedback(request.context.tenant_id, request.anomaly_feedback)
            response_0 = anomalies_v1_detector_validation_service_pb2.PreviewDetectorResponse()
            response_1 = lineage_v1_impact_calculation_service_pb2.RecalculateImpactsResponse()
            response_2 = anomalies_v1_detector_validation_service_pb2.ScoreDetectorResponse()
            outgoing_0 = anomalies_v1_detector_validation_service_pb2.PreviewDetectorRequest(
                context=request.context,
                details=anomalies_v1_detector_validation_service_pb2.PreviewDetectorRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(
                        preferred_channel=request.details.contact.preferred_channel
                    )
                ),
                detector=anomalies_v1_anomalies_pb2.Detector(
                    owner=identity_v1_refs_pb2.UserRef(
                        display_name=request.anomaly_feedback.subject.display_name,
                        email=request.details.contact.email
                    )
                )
            )
            send_0 = partial(deps.clients.anomalies_detector_validation.PreviewDetector, timeout=deps.settings.timeout)
            response_0 = await send_0(outgoing_0)
            outgoing_1 = lineage_v1_impact_calculation_service_pb2.RecalculateImpactsRequest(
                context=request.context,
                impact=lineage_v1_lineage_pb2.Impact(
                    comments=[lineage_v1_lineage_pb2.ImpactComment(created_at=response_0.detector.audit.created_at)]
                )
            )
            response_1 = await hooks.anomaly_feedback_validation_preview_anomaly_feedback1(
                deps.clients.lineage_impact_calculation,
                outgoing_1,
                deps.settings.timeout
            )
            outgoing_2 = anomalies_v1_detector_validation_service_pb2.ScoreDetectorRequest()
            outgoing_2.context.CopyFrom(request.context)
            outgoing_2.detector.audit.created_by = response_0.detector.audit.created_by
            outgoing_2.detector.audit.updated_by = response_0.detector.audit.updated_by
            outgoing_2.detector.route.weight = response_0.detector.route.weight
            outgoing_2.detector.owner.display_name = response_1.impact.customer.display_name
            outgoing_2.context.tenant_id = tenant_id.get()
            response_2 = await deps.clients.anomalies_detector_validation.ScoreDetector(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.correlation_id
            if returned_0_0:
                response.result.correlation_id = returned_0_0
            returned_0_1 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_1)
            returned_1_0 = response_1.result.reference_ids
            response.result.reference_ids.extend(returned_1_0)
            returned_1_1 = response_1.impact.customer.display_name
            if returned_1_1:
                response.anomaly_feedback.subject.display_name = returned_1_1
            returned_2_0 = response_2.result.message
            if returned_2_0:
                response.result.message = returned_2_0
            returned_2_1 = response_2.result.status
            if returned_2_1:
                response.result.status = returned_2_1
            echoed_0 = request.anomaly_feedback_id
            response.anomaly_feedback.anomaly_feedback_id = echoed_0
            echoed_1 = request.anomaly_feedback.occurred_at
            response.anomaly_feedback.occurred_at.CopyFrom(echoed_1)
            return response

    async def handle_score_anomaly_feedback(
        self,
        request: anomalies_v1_anomaly_feedback_validation_service_pb2.ScoreAnomalyFeedbackRequest
    ) -> anomalies_v1_anomaly_feedback_validation_service_pb2.ScoreAnomalyFeedbackResponse:
        """Scores an anomaly feedback."""
        deps = self.deps
        response = anomalies_v1_anomaly_feedback_validation_service_pb2.ScoreAnomalyFeedbackResponse()
        with tenant_scope(request.context.tenant_id):
            log.info(
                'ScoreAnomalyFeedback',
                extra={'fields': {'anomaly_feedback_id': request.anomaly_feedback.anomaly_feedback_id}}
            )
            await deps.repository.audit(
                request.context.tenant_id,
                'ScoreAnomalyFeedback',
                {'anomaly_feedback_id': request.anomaly_feedback.anomaly_feedback_id}
            )
            await deps.repository.save_anomaly_feedback(request.context.tenant_id, request.anomaly_feedback)
            response_0 = anomalies_v1_detector_validation_service_pb2.NormalizeDetectorResponse()
            response_1 = lineage_v1_lineage_node_query_service_pb2.ExportLineageNodesResponse()
            outgoing_0 = anomalies_v1_detector_validation_service_pb2.NormalizeDetectorRequest(
                annotations=dict(request.annotations),
                context=request.context,
                detector=anomalies_v1_anomalies_pb2.Detector(
                    block=anomalies_v1_anomalies_pb2.DetectorBlockAction(reason=request.reason),
                    owner=identity_v1_refs_pb2.UserRef(
                        display_name=request.anomaly_feedback.subject.display_name,
                        user_id=request.context.actor.user_id
                    )
                )
            )
            port_0: AnomalyFeedbackValidationScoreAnomalyFeedback0Port = AnomalyFeedbackValidationScoreAnomalyFeedback0Adapter(
                deps.clients.anomalies_detector_validation,
                deps.settings.timeout
            )
            response_0 = await port_0.execute(outgoing_0)
            outgoing_1 = lineage_v1_lineage_node_query_service_pb2.ExportLineageNodesRequest(
                context=request.context,
                filter=lineage_v1_lineage_node_query_service_pb2.ExportLineageNodesRequest.Filter(
                    created_after=response_0.detector.audit.created_at,
                    region=request.details.destination.region
                )
            )
            async for chunk_1 in deps.clients.lineage_lineage_node_query.ExportLineageNodes(
                outgoing_1,
                timeout=deps.settings.timeout
            ):
                response_1 = chunk_1
            returned_0_0 = response_0.outcome.status
            if returned_0_0:
                response.result.status = returned_0_0
            returned_0_1 = response_0.result.correlation_id
            if returned_0_1:
                response.anomaly_feedback.correlation_id = returned_0_1
            echoed_0 = request.anomaly_feedback_id
            response.anomaly_feedback.anomaly_feedback_id = echoed_0
            echoed_1 = request.anomaly_feedback.source
            response.anomaly_feedback.source = echoed_1
            return response

    async def handle_validate_anomaly_feedback(
        self,
        request: anomalies_v1_anomaly_feedback_validation_service_pb2.ValidateAnomalyFeedbackRequest
    ) -> anomalies_v1_anomaly_feedback_validation_service_pb2.ValidateAnomalyFeedbackResponse:
        """Validates an anomaly feedback."""
        deps = self.deps
        response = anomalies_v1_anomaly_feedback_validation_service_pb2.ValidateAnomalyFeedbackResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ValidateAnomalyFeedback', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ValidateAnomalyFeedback',
                {'reason': request.reason}
            )
            await deps.repository.save_anomaly_feedback(request.context.tenant_id, request.anomaly_feedback)
            response_0 = telematics_v1_telemetry_reading_service_pb2.CloneTelemetryReadingResponse()
            response_1 = anomalies_v1_anomaly_feedback_calculation_service_pb2.ExplainAnomalyFeedbackCalculationResponse()
            response_2 = anomalies_v1_detector_validation_service_pb2.NormalizeDetectorResponse()
            outgoing_0 = telematics_v1_telemetry_reading_service_pb2.CloneTelemetryReadingRequest(
                context=request.context,
                telemetry_reading=telematics_v1_telematics_pb2.TelemetryReading(
                    subject=telematics_v1_refs_pb2.GeoFenceRef(
                        display_name=request.anomaly_feedback.subject.display_name
                    )
                )
            )
            outgoing_2 = anomalies_v1_detector_validation_service_pb2.NormalizeDetectorRequest(
                context=request.context,
                details=anomalies_v1_detector_validation_service_pb2.NormalizeDetectorRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(name=request.details.contact.name),
                    locale=request.details.locale
                ),
                detector=anomalies_v1_anomalies_pb2.Detector(
                    owner=identity_v1_refs_pb2.UserRef(
                        display_name=request.anomaly_feedback.subject.display_name,
                        email=request.details.contact.email
                    )
                )
            )
            response_0, response_2 = await asyncio.gather(
                deps.clients.telematics_telemetry_reading.CloneTelemetryReading(
                    outgoing_0,
                    timeout=deps.settings.timeout
                ),
                deps.clients.anomalies_detector_validation.NormalizeDetector(outgoing_2, timeout=deps.settings.timeout),
            )
            for item_1 in request.anomaly_feedback.measurements:
                outgoing_1 = anomalies_v1_anomaly_feedback_calculation_service_pb2.ExplainAnomalyFeedbackCalculationRequest(
                    anomaly_feedback=anomalies_v1_anomalies_pb2.AnomalyFeedback(
                        measurements=[
                            anomalies_v1_anomalies_pb2.AnomalyFeedbackMeasurement(
                                metric=item_1.metric,
                                observed_at=item_1.observed_at,
                                unit=item_1.unit
                            )
                        ]
                    ),
                    context=request.context
                )
                response_1 = await deps.clients.anomalies_anomaly_feedback_calculation.ExplainAnomalyFeedbackCalculation(
                    outgoing_1,
                    timeout=deps.settings.timeout
                )
            returned_0_0 = response_0.telemetry_reading.kind
            if returned_0_0:
                response.anomaly_feedback.kind = returned_0_0
            returned_2_0 = response_2.outcome.status
            if returned_2_0:
                response.outcome.status = returned_2_0
            echoed_0 = request.anomaly_feedback_id
            response.anomaly_feedback.anomaly_feedback_id = echoed_0
            echoed_1 = request.anomaly_feedback.occurred_at
            response.anomaly_feedback.occurred_at.CopyFrom(echoed_1)
            return response
