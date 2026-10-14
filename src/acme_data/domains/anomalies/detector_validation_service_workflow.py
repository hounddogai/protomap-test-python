"""Application workflow for Detector Validation."""

from __future__ import annotations

from collections.abc import Awaitable
from collections.abc import Callable
from functools import partial
from typing import Any
from typing import cast
import asyncio
import logging

from google.protobuf.any_pb2 import Any as AnyMessage
from google.protobuf.json_format import MessageToDict
from google.protobuf.json_format import MessageToJson
from google.protobuf.json_format import Parse
from google.protobuf.json_format import ParseDict

from acme.anomalies.v1 import anomalies_pb2 as anomalies_v1_anomalies_pb2
from acme.anomalies.v1 import (
    anomaly_feedback_calculation_service_pb2 as anomalies_v1_anomaly_feedback_calculation_service_pb2,
)
from acme.anomalies.v1 import (
    anomaly_feedback_calculation_service_pb2_grpc as anomalies_v1_anomaly_feedback_calculation_service_pb2_grpc,
)
from acme.anomalies.v1 import anomaly_validation_service_pb2 as anomalies_v1_anomaly_validation_service_pb2
from acme.anomalies.v1 import detector_validation_service_pb2 as anomalies_v1_detector_validation_service_pb2
from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.datasets.v1 import refs_pb2 as datasets_v1_refs_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.lineage.v1 import lineage_edge_validation_service_pb2 as lineage_v1_lineage_edge_validation_service_pb2
from acme.lineage.v1 import lineage_node_service_pb2 as lineage_v1_lineage_node_service_pb2
from acme.lineage.v1 import lineage_node_validation_service_pb2 as lineage_v1_lineage_node_validation_service_pb2
from acme.metrics.v1 import metric_alert_history_service_pb2 as metrics_v1_metric_alert_history_service_pb2
from acme.metrics.v1 import metrics_pb2 as metrics_v1_metrics_pb2

from acme_data.domains.anomalies import hooks
from acme_data.domains.anomalies.adapters import DetectorValidationValidateDetector3Adapter
from acme_data.domains.anomalies.adapters import DetectorValidationValidateDetector3Port
from acme_data.domains.anomalies.dependencies import Dependencies
from acme_data.platform.rpc import async_messages
from acme_data.platform.tenancy import tenant_id
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class DetectorValidationServicerWorkflow:
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    async def handle_check_detector_eligibility(
        self,
        request: anomalies_v1_detector_validation_service_pb2.CheckDetectorEligibilityRequest
    ) -> anomalies_v1_detector_validation_service_pb2.CheckDetectorEligibilityResponse:
        """Checks a detector."""
        deps = self.deps
        response = anomalies_v1_detector_validation_service_pb2.CheckDetectorEligibilityResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CheckDetectorEligibility', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'CheckDetectorEligibility',
                {'reason': request.reason}
            )
            await deps.repository.save_detector(request.context.tenant_id, request.detector)
            response_0 = metrics_v1_metric_alert_history_service_pb2.RevertMetricAlertResponse()
            response_1 = lineage_v1_lineage_node_validation_service_pb2.ValidateLineageNodeResponse()
            async for item_0 in async_messages(request.detector.conditions):
                outgoing_0 = metrics_v1_metric_alert_history_service_pb2.RevertMetricAlertRequest(
                    context=request.context,
                    metric_alert=metrics_v1_metrics_pb2.MetricAlert(
                        conditions=[
                            metrics_v1_metrics_pb2.MetricAlertCondition(
                                attribute=item_0.attribute,
                                negate=item_0.negate,
                                operator=item_0.operator,
                                value=item_0.value
                            )
                        ]
                    )
                )
                response_0 = await deps.clients.metrics_metric_alert_history.RevertMetricAlert(
                    outgoing_0,
                    timeout=deps.settings.timeout
                )
            fields_1: dict[str, Any] = {
                'context': request.context,
                'lineage_node': {
                    'children': [
                        {
                            'children': [
                                {
                                    'manager': {
                                        'display_name': response_0.metric_alert.owner.display_name,
                                        'email': request.detector.owner.email,
                                        'user_id': request.detector.owner.user_id
                                    }
                                }
                            ]
                        }
                    ]
                }
            }
            outgoing_1 = lineage_v1_lineage_node_validation_service_pb2.ValidateLineageNodeRequest(**fields_1)
            response_1 = await deps.clients.lineage_lineage_node_validation.ValidateLineageNode(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_1_0 = response_1.result.correlation_id
            if returned_1_0:
                response.result.correlation_id = returned_1_0
            returned_1_1 = response_1.result.message
            if returned_1_1:
                response.result.message = returned_1_1
            echoed_0 = request.detector_id
            response.detector.detector_id = echoed_0
            echoed_1 = request.detector.effective
            response.detector.effective.CopyFrom(echoed_1)
            return response

    async def handle_explain_detector_decision(
        self,
        request: anomalies_v1_detector_validation_service_pb2.ExplainDetectorDecisionRequest
    ) -> anomalies_v1_detector_validation_service_pb2.ExplainDetectorDecisionResponse:
        """Explains a detector."""
        deps = self.deps
        response = anomalies_v1_detector_validation_service_pb2.ExplainDetectorDecisionResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ExplainDetectorDecision', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ExplainDetectorDecision',
                {'reason': request.reason}
            )
            await deps.repository.save_detector(request.context.tenant_id, request.detector)
            response_0 = anomalies_v1_anomaly_validation_service_pb2.ExplainAnomalyDecisionResponse()
            outgoing_0 = anomalies_v1_anomaly_validation_service_pb2.ExplainAnomalyDecisionRequest(
                anomaly=anomalies_v1_anomalies_pb2.Anomaly(
                    assignee=identity_v1_refs_pb2.UserRef(display_name=request.detector.owner.display_name),
                    audit=common_v1_audit_pb2.AuditInfo(etag=request.detector.audit.etag),
                    comments=[anomalies_v1_anomalies_pb2.AnomalyComment(created_at=request.detector.audit.created_at)],
                    requester=common_v1_contact_pb2.ContactInfo(phone=request.details.contact.phone)
                ),
                context=request.context
            )
            document_0 = MessageToDict(outgoing_0, preserving_proto_field_name=True)
            outgoing_0 = ParseDict(
                document_0,
                anomalies_v1_anomaly_validation_service_pb2.ExplainAnomalyDecisionRequest()
            )
            response_0 = await deps.clients.anomalies_anomaly_validation.ExplainAnomalyDecision(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.anomaly.customer.version
            if returned_0_0:
                response.detector.version = returned_0_0
            returned_0_1 = response_0.result.correlation_id
            if returned_0_1:
                response.result.correlation_id = returned_0_1
            echoed_0 = request.detector_id
            response.detector.detector_id = echoed_0
            echoed_1 = request.detector.description
            response.detector.description = echoed_1
            return response

    async def handle_lint_detectors(
        self,
        request: anomalies_v1_detector_validation_service_pb2.LintDetectorsRequest
    ) -> anomalies_v1_detector_validation_service_pb2.LintDetectorsResponse:
        """Lints a detector."""
        deps = self.deps
        response = anomalies_v1_detector_validation_service_pb2.LintDetectorsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('LintDetectors', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'LintDetectors', {'reason': request.reason})
            await deps.repository.save_detector(request.context.tenant_id, request.detector)
            response_0 = anomalies_v1_anomaly_validation_service_pb2.PreviewAnomalyResponse()
            response_1 = lineage_v1_lineage_edge_validation_service_pb2.ExplainLineageEdgeDecisionResponse()
            outgoing_0 = anomalies_v1_anomaly_validation_service_pb2.PreviewAnomalyRequest(
                anomaly=anomalies_v1_anomalies_pb2.Anomaly(
                    audit=common_v1_audit_pb2.AuditInfo(updated_at=request.detector.audit.updated_at)
                ),
                context=request.context,
                details=anomalies_v1_anomaly_validation_service_pb2.PreviewAnomalyRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(
                        preferred_channel=request.details.contact.preferred_channel
                    )
                )
            )
            document_0 = MessageToJson(outgoing_0, preserving_proto_field_name=True)
            outgoing_0 = Parse(document_0, anomalies_v1_anomaly_validation_service_pb2.PreviewAnomalyRequest())
            response_0 = await deps.clients.anomalies_anomaly_validation.PreviewAnomaly(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = lineage_v1_lineage_edge_validation_service_pb2.ExplainLineageEdgeDecisionRequest()
            outgoing_1.context.CopyFrom(request.context)
            outgoing_1.details.contact.name.CopyFrom(response_0.anomaly.requester.name)
            outgoing_1.details.contact.email = request.details.contact.email
            outgoing_1.lineage_edge.subject.priority = request.detector.priority
            merged_1 = lineage_v1_lineage_edge_validation_service_pb2.ExplainLineageEdgeDecisionRequest()
            merged_1.MergeFrom(outgoing_1)
            outgoing_1.CopyFrom(merged_1)
            response_1 = await deps.clients.lineage_lineage_edge_validation.ExplainLineageEdgeDecision(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.correlation_id
            if returned_0_0:
                response.result.correlation_id = returned_0_0
            returned_1_0 = response_1.result.status
            if returned_1_0:
                response.result.status = returned_1_0
            echoed_0 = request.detector_id
            response.detector.detector_id = echoed_0
            echoed_1 = request.detector.parameters
            response.detector.parameters.update(echoed_1)
            return response

    async def handle_normalize_detector(
        self,
        request: anomalies_v1_detector_validation_service_pb2.NormalizeDetectorRequest
    ) -> anomalies_v1_detector_validation_service_pb2.NormalizeDetectorResponse:
        """Normalizes a detector."""
        deps = self.deps
        response = anomalies_v1_detector_validation_service_pb2.NormalizeDetectorResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('NormalizeDetector', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'NormalizeDetector', {'reason': request.reason})
            await deps.repository.save_detector(request.context.tenant_id, request.detector)
            response_0 = anomalies_v1_anomaly_feedback_calculation_service_pb2.RecalculateAnomalyFeedbacksResponse()
            outgoing_0 = anomalies_v1_anomaly_feedback_calculation_service_pb2.RecalculateAnomalyFeedbacksRequest(
                anomaly_feedback=anomalies_v1_anomalies_pb2.AnomalyFeedback(
                    subject=datasets_v1_refs_pb2.DatasetRef(display_name=request.detector.owner.display_name)
                ),
                context=request.context
            )
            envelope_0 = AnyMessage()
            envelope_0.Pack(outgoing_0)
            outgoing_0 = anomalies_v1_anomaly_feedback_calculation_service_pb2.RecalculateAnomalyFeedbacksRequest()
            if not envelope_0.Unpack(outgoing_0):
                raise ValueError("partner envelope contains the wrong request type")
            response_0 = await deps.clients.anomalies_anomaly_feedback_calculation.RecalculateAnomalyFeedbacks(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.status
            if returned_0_0:
                response.outcome.status = returned_0_0
            returned_0_1 = response_0.result.details
            response.result.details.update(returned_0_1)
            echoed_0 = request.detector_id
            response.detector.detector_id = echoed_0
            echoed_1 = request.detector.description
            response.detector.description = echoed_1
            return response

    async def handle_preview_detector(
        self,
        request: anomalies_v1_detector_validation_service_pb2.PreviewDetectorRequest
    ) -> anomalies_v1_detector_validation_service_pb2.PreviewDetectorResponse:
        """Previews a detector."""
        deps = self.deps
        response = anomalies_v1_detector_validation_service_pb2.PreviewDetectorResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('PreviewDetector', extra={'fields': {'locale': request.details.locale}})
            await deps.repository.audit(
                request.context.tenant_id,
                'PreviewDetector',
                {'locale': request.details.locale}
            )
            await deps.repository.save_detector(request.context.tenant_id, request.detector)
            response_0 = anomalies_v1_anomaly_feedback_calculation_service_pb2.EstimateAnomalyFeedbackResponse()
            outgoing_0 = anomalies_v1_anomaly_feedback_calculation_service_pb2.EstimateAnomalyFeedbackRequest(
                annotations=dict(request.annotations),
                anomaly_feedback=anomalies_v1_anomalies_pb2.AnomalyFeedback(
                    subject=datasets_v1_refs_pb2.DatasetRef(display_name=request.detector.owner.display_name)
                ),
                context=request.context,
                reason=request.reason
            )
            registered_0 = cast(
                anomalies_v1_anomaly_feedback_calculation_service_pb2_grpc.AnomalyFeedbackCalculationServiceStub,
                deps.clients.registry['acme.anomalies.v1.AnomalyFeedbackCalculationService']
            )
            response_0 = await registered_0.EstimateAnomalyFeedback(outgoing_0, timeout=deps.settings.timeout)
            returned_0_0 = response_0.result.correlation_id
            if returned_0_0:
                response.result.correlation_id = returned_0_0
            echoed_0 = request.detector_id
            response.detector.detector_id = echoed_0
            echoed_1 = request.detector.version
            response.detector.version = echoed_1
            return response

    async def handle_score_detector(
        self,
        request: anomalies_v1_detector_validation_service_pb2.ScoreDetectorRequest
    ) -> anomalies_v1_detector_validation_service_pb2.ScoreDetectorResponse:
        """Scores a detector."""
        deps = self.deps
        response = anomalies_v1_detector_validation_service_pb2.ScoreDetectorResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ScoreDetector', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'ScoreDetector', {'reason': request.reason})
            await deps.repository.save_detector(request.context.tenant_id, request.detector)
            response_0 = anomalies_v1_anomaly_feedback_calculation_service_pb2.EstimateAnomalyFeedbackResponse()
            response_1 = anomalies_v1_anomaly_feedback_calculation_service_pb2.QuoteAnomalyFeedbackResponse()
            outgoing_0 = anomalies_v1_anomaly_feedback_calculation_service_pb2.EstimateAnomalyFeedbackRequest(
                context=request.context,
                details=anomalies_v1_anomaly_feedback_calculation_service_pb2.EstimateAnomalyFeedbackRequest.Details(
                    destination=common_v1_address_pb2.PostalAddress(
                        country_code=request.details.destination.country_code,
                        lines=list(request.details.destination.lines)
                    )
                )
            )
            outgoing_1 = anomalies_v1_anomaly_feedback_calculation_service_pb2.QuoteAnomalyFeedbackRequest(
                context=request.context,
                details=anomalies_v1_anomaly_feedback_calculation_service_pb2.QuoteAnomalyFeedbackRequest.Details(
                    destination=common_v1_address_pb2.PostalAddress(lines=list(request.details.destination.lines))
                )
            )
            response_0, response_1 = await asyncio.gather(
                deps.clients.anomalies_anomaly_feedback_calculation.EstimateAnomalyFeedback(
                    outgoing_0,
                    timeout=deps.settings.timeout
                ),
                deps.clients.anomalies_anomaly_feedback_calculation.QuoteAnomalyFeedback(
                    outgoing_1,
                    timeout=deps.settings.timeout
                ),
            )
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.result.message = returned_0_0
            returned_0_1 = response_0.breakdown.total
            if returned_0_1.ListFields():
                response.breakdown.total.MergeFrom(returned_0_1)
            returned_1_0 = response_1.result.message
            if returned_1_0:
                response.result.message = returned_1_0
            returned_1_1 = response_1.result.reference_ids
            response.result.reference_ids.extend(returned_1_1)
            echoed_0 = request.detector_id
            response.detector.detector_id = echoed_0
            echoed_1 = request.detector.priority
            response.detector.priority = echoed_1
            return response

    async def handle_validate_detector(
        self,
        request: anomalies_v1_detector_validation_service_pb2.ValidateDetectorRequest
    ) -> anomalies_v1_detector_validation_service_pb2.ValidateDetectorResponse:
        """Validates a detector."""
        deps = self.deps
        response = anomalies_v1_detector_validation_service_pb2.ValidateDetectorResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ValidateDetector', extra={'fields': {'locale': request.details.locale}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ValidateDetector',
                {'locale': request.details.locale}
            )
            await deps.repository.save_detector(request.context.tenant_id, request.detector)
            response_0 = anomalies_v1_anomaly_feedback_calculation_service_pb2.EstimateAnomalyFeedbackResponse()
            response_1 = lineage_v1_lineage_node_service_pb2.ListLineageNodesResponse()
            response_2 = lineage_v1_lineage_node_service_pb2.SearchLineageNodesResponse()
            response_3 = anomalies_v1_anomaly_feedback_calculation_service_pb2.CompareAnomalyFeedbackOptionsResponse()
            outgoing_0 = anomalies_v1_anomaly_feedback_calculation_service_pb2.EstimateAnomalyFeedbackRequest(
                anomaly_feedback=anomalies_v1_anomalies_pb2.AnomalyFeedback(
                    subject=datasets_v1_refs_pb2.DatasetRef(display_name=request.detector.owner.display_name)
                ),
                context=request.context,
                reason=request.reason
            )
            send_0 = partial(
                deps.clients.anomalies_anomaly_feedback_calculation.EstimateAnomalyFeedback,
                timeout=deps.settings.timeout
            )
            response_0 = await send_0(outgoing_0)
            outgoing_1 = lineage_v1_lineage_node_service_pb2.ListLineageNodesRequest(
                context=request.context,
                filter=lineage_v1_lineage_node_service_pb2.ListLineageNodesRequest.Filter(
                    created_after=request.detector.audit.created_at,
                    labels=dict(request.detector.parameters),
                    owner_id=request.detector.detector_id
                )
            )
            response_1 = await hooks.detector_validation_validate_detector1(
                deps.clients.lineage_lineage_node,
                outgoing_1,
                deps.settings.timeout
            )
            outgoing_2 = lineage_v1_lineage_node_service_pb2.SearchLineageNodesRequest()
            outgoing_2.context.CopyFrom(request.context)
            outgoing_2.filter.labels.update(dict(request.detector.parameters))
            outgoing_2.filter.owner_id = request.detector.owner.user_id
            outgoing_2.context.tenant_id = tenant_id.get()
            response_2 = await deps.clients.lineage_lineage_node.SearchLineageNodes(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            outgoing_3 = anomalies_v1_anomaly_feedback_calculation_service_pb2.CompareAnomalyFeedbackOptionsRequest(
                anomaly_feedback=anomalies_v1_anomalies_pb2.AnomalyFeedback(
                    anomaly_feedback_id=response_0.anomaly_feedback.anomaly_feedback_id,
                    kind=response_0.anomaly_feedback.kind,
                    subject=datasets_v1_refs_pb2.DatasetRef(
                        dataset_id=response_0.anomaly_feedback.subject.dataset_id,
                        display_name=response_0.anomaly_feedback.subject.display_name
                    )
                ),
                context=request.context
            )
            port_3: DetectorValidationValidateDetector3Port = DetectorValidationValidateDetector3Adapter(
                deps.clients.anomalies_anomaly_feedback_calculation,
                deps.settings.timeout
            )
            response_3 = await port_3.execute(outgoing_3)
            returned_0_0 = response_0.anomaly_feedback.subject.display_name
            if returned_0_0:
                response.detector.owner.display_name = returned_0_0
            returned_1_0 = response_1.result.message
            if returned_1_0:
                response.outcome.message = returned_1_0
            returned_1_1 = response_1.result.correlation_id
            if returned_1_1:
                response.result.correlation_id = returned_1_1
            returned_2_0 = response_2.result.correlation_id
            if returned_2_0:
                response.result.correlation_id = returned_2_0
            returned_3_0 = response_3.result.message
            if returned_3_0:
                response.result.message = returned_3_0
            echoed_0 = request.detector_id
            response.detector.detector_id = echoed_0
            echoed_1 = request.detector.description
            response.detector.description = echoed_1
            return response
