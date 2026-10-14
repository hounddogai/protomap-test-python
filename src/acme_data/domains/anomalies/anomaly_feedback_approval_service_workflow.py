"""Application workflow for AnomalyFeedback Approval."""

from __future__ import annotations

from collections.abc import Awaitable
from collections.abc import Callable
from functools import partial
from typing import Any
from typing import cast
import asyncio
import logging

from google.protobuf.json_format import MessageToDict
from google.protobuf.json_format import MessageToJson
from google.protobuf.json_format import Parse
from google.protobuf.json_format import ParseDict

from acme.anomalies.v1 import anomalies_pb2 as anomalies_v1_anomalies_pb2
from acme.anomalies.v1 import (
    anomaly_feedback_approval_service_pb2 as anomalies_v1_anomaly_feedback_approval_service_pb2,
)
from acme.anomalies.v1 import anomaly_service_pb2 as anomalies_v1_anomaly_service_pb2
from acme.anomalies.v1 import anomaly_validation_service_pb2 as anomalies_v1_anomaly_validation_service_pb2
from acme.anomalies.v1 import detector_approval_service_pb2 as anomalies_v1_detector_approval_service_pb2
from acme.anomalies.v1 import refs_pb2 as anomalies_v1_refs_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.customers.v1 import refs_pb2 as customers_v1_refs_pb2
from acme.datasets.v1 import data_schema_calculation_service_pb2 as datasets_v1_data_schema_calculation_service_pb2
from acme.datasets.v1 import dataset_query_service_pb2 as datasets_v1_dataset_query_service_pb2
from acme.datasets.v1 import (
    dataset_version_calculation_service_pb2 as datasets_v1_dataset_version_calculation_service_pb2,
)
from acme.datasets.v1 import dataset_version_query_service_pb2 as datasets_v1_dataset_version_query_service_pb2
from acme.datasets.v1 import datasets_pb2 as datasets_v1_datasets_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.lineage.v1 import impact_lifecycle_service_pb2 as lineage_v1_impact_lifecycle_service_pb2
from acme.lineage.v1 import impact_workflow_service_pb2 as lineage_v1_impact_workflow_service_pb2
from acme.lineage.v1 import lineage_edge_approval_service_pb2 as lineage_v1_lineage_edge_approval_service_pb2
from acme.lineage.v1 import lineage_edge_import_service_pb2 as lineage_v1_lineage_edge_import_service_pb2
from acme.lineage.v1 import lineage_edge_reporting_service_pb2 as lineage_v1_lineage_edge_reporting_service_pb2
from acme.lineage.v1 import lineage_pb2 as lineage_v1_lineage_pb2
from acme.metrics.v1 import metric_alert_notification_service_pb2 as metrics_v1_metric_alert_notification_service_pb2
from acme.promotions.v1 import promotion_calculation_service_pb2 as promotions_v1_promotion_calculation_service_pb2
from acme.promotions.v1 import promotions_pb2 as promotions_v1_promotions_pb2
from acme.search.v1 import search_index_service_pb2 as search_v1_search_index_service_pb2
from acme.search.v1 import search_index_validation_service_pb2 as search_v1_search_index_validation_service_pb2
from acme.search.v1 import search_pb2 as search_v1_search_pb2

from acme_data.domains.anomalies import hooks
from acme_data.domains.anomalies.adapters import AnomalyFeedbackApprovalApproveAnomalyFeedback2Adapter
from acme_data.domains.anomalies.adapters import AnomalyFeedbackApprovalSubmitAnomalyFeedback1Adapter
from acme_data.domains.anomalies.adapters import AnomalyFeedbackApprovalSubmitAnomalyFeedback1Port
from acme_data.domains.anomalies.adapters import AnomalyFeedbackApprovalSubmitAnomalyFeedback3Adapter
from acme_data.domains.anomalies.dependencies import Dependencies
from acme_data.domains.anomalies.models import AnomalyFeedbackApprovalRecallAnomalyFeedback2Command
from acme_data.domains.anomalies.models import to_anomaly_feedback_approval_recall_anomaly_feedback2_command
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import run_steps
from acme_data.platform.tenancy import tenant_id
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class AnomalyFeedbackApprovalServicerWorkflow:
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    async def handle_approve_anomaly_feedback(
        self,
        request: anomalies_v1_anomaly_feedback_approval_service_pb2.ApproveAnomalyFeedbackRequest
    ) -> anomalies_v1_anomaly_feedback_approval_service_pb2.ApproveAnomalyFeedbackResponse:
        """Approves an anomaly feedback."""
        deps = self.deps
        response = anomalies_v1_anomaly_feedback_approval_service_pb2.ApproveAnomalyFeedbackResponse()
        with tenant_scope(request.context.tenant_id):
            log.info(
                'ApproveAnomalyFeedback',
                extra={'fields': {'anomaly_feedback_id': request.anomaly_feedback.anomaly_feedback_id}}
            )
            await deps.repository.audit(
                request.context.tenant_id,
                'ApproveAnomalyFeedback',
                {'anomaly_feedback_id': request.anomaly_feedback.anomaly_feedback_id}
            )
            await deps.repository.save_anomaly_feedback(request.context.tenant_id, request.anomaly_feedback)
            response_0 = datasets_v1_dataset_version_calculation_service_pb2.EstimateDatasetVersionResponse()
            response_1 = lineage_v1_lineage_edge_reporting_service_pb2.GenerateLineageEdgeReportResponse()
            response_2 = search_v1_search_index_validation_service_pb2.NormalizeSearchIndexResponse()
            response_3 = anomalies_v1_anomaly_service_pb2.UpdateAnomalyResponse()
            async for item_0 in async_messages(request.anomaly_feedback.measurements):
                outgoing_0 = datasets_v1_dataset_version_calculation_service_pb2.EstimateDatasetVersionRequest(
                    context=request.context,
                    dataset_version=datasets_v1_datasets_pb2.DatasetVersion(
                        measurements=[
                            datasets_v1_datasets_pb2.DatasetVersionMeasurement(observed_at=item_0.observed_at)
                        ]
                    )
                )
                response_0 = await deps.clients.datasets_dataset_version_calculation.EstimateDatasetVersion(
                    outgoing_0,
                    timeout=deps.settings.timeout
                )
            outgoing_1 = lineage_v1_lineage_edge_reporting_service_pb2.GenerateLineageEdgeReportRequest(
                annotations=dict(request.annotations),
                context=request.context,
                reason=request.reason
            )
            steps_1 = [
                partial(
                    deps.clients.lineage_lineage_edge_reporting.GenerateLineageEdgeReport,
                    outgoing_1,
                    timeout=deps.settings.timeout
                )
            ]
            results_1 = await run_steps(steps_1)
            response_1 = results_1[-1]
            outgoing_2 = search_v1_search_index_validation_service_pb2.NormalizeSearchIndexRequest(
                context=request.context,
                search_index=search_v1_search_pb2.SearchIndex(
                    owner=identity_v1_refs_pb2.UserRef(
                        display_name=response_0.dataset_version.subject.display_name,
                        email=request.details.approver.email
                    )
                )
            )
            response_2 = await AnomalyFeedbackApprovalApproveAnomalyFeedback2Adapter(
                deps.clients.search_search_index_validation,
                deps.settings.timeout
            )(outgoing_2)
            outgoing_3 = anomalies_v1_anomaly_service_pb2.UpdateAnomalyRequest(
                anomaly=anomalies_v1_anomalies_pb2.Anomaly(
                    assignee=identity_v1_refs_pb2.UserRef(email=response_2.search_index.owner.email),
                    audit=common_v1_audit_pb2.AuditInfo(etag=response_2.search_index.audit.etag),
                    requester=common_v1_contact_pb2.ContactInfo(email=request.details.approver.email)
                ),
                context=request.context
            )
            response_3 = cast(anomalies_v1_anomaly_service_pb2.UpdateAnomalyResponse, await deps.bus.request(
                'acme.anomalies.v1.AnomalyFeedbackApprovalService/ApproveAnomalyFeedback/3', outgoing_3, deps.settings.timeout,
            ))
            returned_1_0 = response_1.result.details
            response.result.details.update(returned_1_0)
            returned_2_0 = response_2.result.correlation_id
            if returned_2_0:
                response.anomaly_feedback.correlation_id = returned_2_0
            returned_2_1 = response_2.result.correlation_id
            if returned_2_1:
                response.result.correlation_id = returned_2_1
            returned_3_0 = response_3.result.reference_ids
            response.result.reference_ids.extend(returned_3_0)
            echoed_0 = request.anomaly_feedback_id
            response.anomaly_feedback.anomaly_feedback_id = echoed_0
            echoed_1 = request.anomaly_feedback.sequence
            response.anomaly_feedback.sequence = echoed_1
            return response

    async def handle_comment_anomaly_feedback_approval(
        self,
        request: anomalies_v1_anomaly_feedback_approval_service_pb2.CommentAnomalyFeedbackApprovalRequest
    ) -> anomalies_v1_anomaly_feedback_approval_service_pb2.CommentAnomalyFeedbackApprovalResponse:
        """Comments an anomaly feedback."""
        deps = self.deps
        response = anomalies_v1_anomaly_feedback_approval_service_pb2.CommentAnomalyFeedbackApprovalResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CommentAnomalyFeedbackApproval', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'CommentAnomalyFeedbackApproval',
                {'reason': request.reason}
            )
            await deps.repository.save_anomaly_feedback(request.context.tenant_id, request.anomaly_feedback)
            response_0 = lineage_v1_impact_lifecycle_service_pb2.ScheduleImpactExpiryResponse()
            outgoing_0 = lineage_v1_impact_lifecycle_service_pb2.ScheduleImpactExpiryRequest(
                context=request.context,
                impact=lineage_v1_lineage_pb2.Impact(
                    assignee=identity_v1_refs_pb2.UserRef(display_name=request.details.approver.display_name),
                    requester=common_v1_contact_pb2.ContactInfo(email=request.details.approver.email)
                )
            )
            response_0 = await deps.clients.lineage_impact_lifecycle.ScheduleImpactExpiry(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.impact.assignee.display_name
            if returned_0_0:
                response.anomaly_feedback.subject.display_name = returned_0_0
            returned_0_1 = response_0.result.correlation_id
            if returned_0_1:
                response.anomaly_feedback.correlation_id = returned_0_1
            echoed_0 = request.anomaly_feedback_id
            response.anomaly_feedback.anomaly_feedback_id = echoed_0
            echoed_1 = request.anomaly_feedback.source
            response.anomaly_feedback.source = echoed_1
            return response

    async def handle_delegate_anomaly_feedback_approval(
        self,
        request: anomalies_v1_anomaly_feedback_approval_service_pb2.DelegateAnomalyFeedbackApprovalRequest
    ) -> anomalies_v1_anomaly_feedback_approval_service_pb2.DelegateAnomalyFeedbackApprovalResponse:
        """Delegates an anomaly feedback."""
        deps = self.deps
        response = anomalies_v1_anomaly_feedback_approval_service_pb2.DelegateAnomalyFeedbackApprovalResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('DelegateAnomalyFeedbackApproval', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'DelegateAnomalyFeedbackApproval',
                {'reason': request.reason}
            )
            await deps.repository.save_anomaly_feedback(request.context.tenant_id, request.anomaly_feedback)
            response_0 = anomalies_v1_anomaly_validation_service_pb2.NormalizeAnomalyResponse()
            response_1 = datasets_v1_dataset_query_service_pb2.PeekDatasetResponse()
            response_2 = metrics_v1_metric_alert_notification_service_pb2.NotifyMetricAlertWatchersResponse()
            outgoing_0 = anomalies_v1_anomaly_validation_service_pb2.NormalizeAnomalyRequest(
                anomaly=anomalies_v1_anomalies_pb2.Anomaly(
                    assignee=identity_v1_refs_pb2.UserRef(
                        display_name=request.anomaly_feedback.subject.display_name,
                        user_id=request.details.approver.user_id
                    ),
                    customer=anomalies_v1_refs_pb2.DetectorRef(display_name=request.details.approver.display_name),
                    requester=common_v1_contact_pb2.ContactInfo(email=request.details.approver.email)
                ),
                context=request.context
            )
            method_name_0 = 'NormalizeAnomaly'
            response_0 = await getattr(
                deps.clients.anomalies_anomaly_validation,
                method_name_0
            )(outgoing_0, timeout=deps.settings.timeout)
            fields_1: dict[str, Any] = {
                'context': request.context,
                'dataset_id': request.anomaly_feedback.subject.dataset_id
            }
            outgoing_1 = datasets_v1_dataset_query_service_pb2.PeekDatasetRequest(**fields_1)
            response_1 = await deps.clients.datasets_dataset_query.PeekDataset(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = metrics_v1_metric_alert_notification_service_pb2.NotifyMetricAlertWatchersRequest(
                context=request.context,
                details=metrics_v1_metric_alert_notification_service_pb2.NotifyMetricAlertWatchersRequest.Details(
                    recipient=common_v1_contact_pb2.ContactInfo(
                        email=response_0.anomaly.requester.email,
                        phone=response_0.anomaly.requester.phone,
                        preferred_channel=response_0.anomaly.requester.preferred_channel
                    )
                )
            )
            document_2 = MessageToDict(outgoing_2, preserving_proto_field_name=True)
            outgoing_2 = ParseDict(
                document_2,
                metrics_v1_metric_alert_notification_service_pb2.NotifyMetricAlertWatchersRequest()
            )
            response_2 = await deps.clients.metrics_metric_alert_notification.NotifyMetricAlertWatchers(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.status
            if returned_0_0:
                response.outcome.status = returned_0_0
            returned_0_1 = response_0.result.correlation_id
            if returned_0_1:
                response.result.correlation_id = returned_0_1
            returned_1_0 = response_1.dataset.dataset_id
            if returned_1_0:
                response.anomaly_feedback.subject.dataset_id = returned_1_0
            returned_2_0 = response_2.result.reference_ids
            response.result.reference_ids.extend(returned_2_0)
            echoed_0 = request.anomaly_feedback_id
            response.anomaly_feedback.anomaly_feedback_id = echoed_0
            echoed_1 = request.details.effective_at
            response.outcome.effective_at.CopyFrom(echoed_1)
            return response

    async def handle_escalate_anomaly_feedback(
        self,
        request: anomalies_v1_anomaly_feedback_approval_service_pb2.EscalateAnomalyFeedbackRequest
    ) -> anomalies_v1_anomaly_feedback_approval_service_pb2.EscalateAnomalyFeedbackResponse:
        """Escalates an anomaly feedback."""
        deps = self.deps
        response = anomalies_v1_anomaly_feedback_approval_service_pb2.EscalateAnomalyFeedbackResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('EscalateAnomalyFeedback', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'EscalateAnomalyFeedback',
                {'reason': request.reason}
            )
            await deps.repository.save_anomaly_feedback(request.context.tenant_id, request.anomaly_feedback)
            response_0 = promotions_v1_promotion_calculation_service_pb2.RecalculatePromotionsResponse()
            response_1 = anomalies_v1_anomaly_validation_service_pb2.ExplainAnomalyDecisionResponse()
            outgoing_0 = promotions_v1_promotion_calculation_service_pb2.RecalculatePromotionsRequest(
                context=request.context,
                promotion=promotions_v1_promotions_pb2.Promotion(
                    owner=identity_v1_refs_pb2.UserRef(display_name=request.anomaly_feedback.subject.display_name)
                )
            )
            document_0 = MessageToJson(outgoing_0, preserving_proto_field_name=True)
            outgoing_0 = Parse(
                document_0,
                promotions_v1_promotion_calculation_service_pb2.RecalculatePromotionsRequest()
            )
            response_0 = await deps.clients.promotions_promotion_calculation.RecalculatePromotions(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = anomalies_v1_anomaly_validation_service_pb2.ExplainAnomalyDecisionRequest()
            outgoing_1.context.CopyFrom(request.context)
            outgoing_1.details.contact.email = response_0.promotion.owner.email
            outgoing_1.anomaly.audit.created_at.CopyFrom(response_0.promotion.audit.created_at)
            outgoing_1.anomaly.assignee.user_id = response_0.promotion.owner.user_id
            merged_1 = anomalies_v1_anomaly_validation_service_pb2.ExplainAnomalyDecisionRequest()
            merged_1.MergeFrom(outgoing_1)
            outgoing_1.CopyFrom(merged_1)
            response_1 = await deps.clients.anomalies_anomaly_validation.ExplainAnomalyDecision(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.status
            if returned_0_0:
                response.result.status = returned_0_0
            returned_0_1 = response_0.result.correlation_id
            if returned_0_1:
                response.anomaly_feedback.correlation_id = returned_0_1
            returned_1_0 = response_1.outcome.next_steps
            response.outcome.next_steps.extend(returned_1_0)
            returned_1_1 = response_1.anomaly.assignee.display_name
            if returned_1_1:
                response.anomaly_feedback.subject.display_name = returned_1_1
            echoed_0 = request.anomaly_feedback_id
            response.anomaly_feedback.anomaly_feedback_id = echoed_0
            echoed_1 = request.anomaly_feedback.kind
            response.anomaly_feedback.kind = echoed_1
            return response

    async def handle_get_anomaly_feedback_approval_status(
        self,
        request: anomalies_v1_anomaly_feedback_approval_service_pb2.GetAnomalyFeedbackApprovalStatusRequest
    ) -> anomalies_v1_anomaly_feedback_approval_service_pb2.GetAnomalyFeedbackApprovalStatusResponse:
        """Returns an anomaly feedback."""
        deps = self.deps
        response = anomalies_v1_anomaly_feedback_approval_service_pb2.GetAnomalyFeedbackApprovalStatusResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('GetAnomalyFeedbackApprovalStatus', extra={'fields': {'locale': request.context.locale}})
            await deps.repository.audit(
                request.context.tenant_id,
                'GetAnomalyFeedbackApprovalStatus',
                {'locale': request.context.locale}
            )
            echoed_0 = request.anomaly_feedback_id
            response.anomaly_feedback.anomaly_feedback_id = echoed_0
            return response

    async def handle_list_pending_anomaly_feedbacks(
        self,
        request: anomalies_v1_anomaly_feedback_approval_service_pb2.ListPendingAnomalyFeedbacksRequest
    ) -> anomalies_v1_anomaly_feedback_approval_service_pb2.ListPendingAnomalyFeedbacksResponse:
        """Lists anomaly feedbacks a page at a time."""
        deps = self.deps
        response = anomalies_v1_anomaly_feedback_approval_service_pb2.ListPendingAnomalyFeedbacksResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ListPendingAnomalyFeedbacks', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ListPendingAnomalyFeedbacks',
                {'order_by': request.order_by}
            )
            response_0 = datasets_v1_dataset_version_query_service_pb2.SummarizeDatasetVersionsResponse()
            outgoing_0 = datasets_v1_dataset_version_query_service_pb2.SummarizeDatasetVersionsRequest(
                annotations=dict(request.context.baggage),
                context=request.context,
                details=datasets_v1_dataset_version_query_service_pb2.SummarizeDatasetVersionsRequest.Details(
                    filters=dict(request.filter.labels)
                )
            )
            response_0 = await deps.clients.datasets_dataset_version_query.SummarizeDatasetVersions(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.result.message = returned_0_0
            return response

    async def handle_recall_anomaly_feedback(
        self,
        request: anomalies_v1_anomaly_feedback_approval_service_pb2.RecallAnomalyFeedbackRequest
    ) -> anomalies_v1_anomaly_feedback_approval_service_pb2.RecallAnomalyFeedbackResponse:
        """Recalls an anomaly feedback."""
        deps = self.deps
        response = anomalies_v1_anomaly_feedback_approval_service_pb2.RecallAnomalyFeedbackResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('RecallAnomalyFeedback', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'RecallAnomalyFeedback', {'reason': request.reason})
            await deps.repository.save_anomaly_feedback(request.context.tenant_id, request.anomaly_feedback)
            response_0 = datasets_v1_dataset_version_query_service_pb2.BrowseDatasetVersionsResponse()
            response_1 = anomalies_v1_anomaly_service_pb2.SearchAnomaliesResponse()
            response_2 = anomalies_v1_anomaly_validation_service_pb2.ScoreAnomalyResponse()
            for item_0 in request.anomaly_feedback.measurements:
                outgoing_0 = datasets_v1_dataset_version_query_service_pb2.BrowseDatasetVersionsRequest(
                    context=request.context,
                    filter=datasets_v1_dataset_version_query_service_pb2.BrowseDatasetVersionsRequest.Filter(
                        created_after=item_0.observed_at,
                        labels=dict(request.anomaly_feedback.attributes),
                        owner_id=request.anomaly_feedback.subject.dataset_id
                    )
                )
                response_0 = await deps.clients.datasets_dataset_version_query.BrowseDatasetVersions(
                    outgoing_0,
                    timeout=deps.settings.timeout
                )
            requests_1: list[anomalies_v1_anomaly_service_pb2.SearchAnomaliesRequest] = []
            for item_1 in request.anomaly_feedback.measurements:
                outgoing_1 = anomalies_v1_anomaly_service_pb2.SearchAnomaliesRequest(
                    context=request.context,
                    filter=anomalies_v1_anomaly_service_pb2.SearchAnomaliesRequest.Filter(
                        created_after=item_1.observed_at
                    )
                )
                requests_1.append(outgoing_1)
            replies_1 = await asyncio.gather(*(
                deps.clients.anomalies_anomaly.SearchAnomalies(
                    entry,
                    timeout=deps.settings.timeout
                ) for entry in requests_1
            ))
            if replies_1:
                response_1 = replies_1[-1]
            command_2 = AnomalyFeedbackApprovalRecallAnomalyFeedback2Command.model_validate(
                {
                    'context': request.context,
                    'anomaly_customer_display_name': request.details.approver.display_name,
                    'anomaly_requester_email': request.details.approver.email,
                    'anomaly_assignee_user_id': request.details.approver.user_id,
                    'anomaly_assignee_display_name': request.anomaly_feedback.subject.display_name
                }
            )
            outgoing_2 = to_anomaly_feedback_approval_recall_anomaly_feedback2_command(command_2)
            response_2 = await deps.clients.anomalies_anomaly_validation.ScoreAnomaly(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            returned_2_0 = response_2.result.correlation_id
            if returned_2_0:
                response.anomaly_feedback.correlation_id = returned_2_0
            returned_2_1 = response_2.result.correlation_id
            if returned_2_1:
                response.result.correlation_id = returned_2_1
            echoed_0 = request.anomaly_feedback_id
            response.anomaly_feedback.anomaly_feedback_id = echoed_0
            echoed_1 = request.anomaly_feedback.source
            response.anomaly_feedback.source = echoed_1
            return response

    async def handle_reject_anomaly_feedback(
        self,
        request: anomalies_v1_anomaly_feedback_approval_service_pb2.RejectAnomalyFeedbackRequest
    ) -> anomalies_v1_anomaly_feedback_approval_service_pb2.RejectAnomalyFeedbackResponse:
        """Rejects an anomaly feedback."""
        deps = self.deps
        response = anomalies_v1_anomaly_feedback_approval_service_pb2.RejectAnomalyFeedbackResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('RejectAnomalyFeedback', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'RejectAnomalyFeedback', {'reason': request.reason})
            await deps.repository.save_anomaly_feedback(request.context.tenant_id, request.anomaly_feedback)
            response_0 = lineage_v1_lineage_edge_approval_service_pb2.SubmitLineageEdgeResponse()
            response_1 = search_v1_search_index_service_pb2.BatchGetSearchIndexesResponse()
            callbacks_0: list[
                Callable[[], Awaitable[lineage_v1_lineage_edge_approval_service_pb2.SubmitLineageEdgeResponse]]
            ] = []
            for item_0 in request.anomaly_feedback.measurements:
                outgoing_0 = lineage_v1_lineage_edge_approval_service_pb2.SubmitLineageEdgeRequest(
                    context=request.context,
                    lineage_edge=lineage_v1_lineage_pb2.LineageEdge(
                        measurements=[
                            lineage_v1_lineage_pb2.LineageEdgeMeasurement(metric=item_0.metric, unit=item_0.unit)
                        ]
                    )
                )
                async def send_0(
                    payload: lineage_v1_lineage_edge_approval_service_pb2.SubmitLineageEdgeRequest = outgoing_0
                ) -> lineage_v1_lineage_edge_approval_service_pb2.SubmitLineageEdgeResponse:
                    return await deps.clients.lineage_lineage_edge_approval.SubmitLineageEdge(
                        payload,
                        timeout=deps.settings.timeout
                    )
                callbacks_0.append(send_0)
            for callback_0 in callbacks_0:
                response_0 = await callback_0()
            outgoing_1 = search_v1_search_index_service_pb2.BatchGetSearchIndexesRequest(context=request.context)
            response_1 = await hooks.anomaly_feedback_approval_reject_anomaly_feedback1(
                deps.clients.search_search_index,
                outgoing_1,
                deps.settings.timeout
            )
            returned_1_0 = response_1.result.message
            if returned_1_0:
                response.result.message = returned_1_0
            echoed_0 = request.anomaly_feedback_id
            response.anomaly_feedback.anomaly_feedback_id = echoed_0
            echoed_1 = request.anomaly_feedback.occurred_at
            response.anomaly_feedback.occurred_at.CopyFrom(echoed_1)
            return response

    async def handle_submit_anomaly_feedback(
        self,
        request: anomalies_v1_anomaly_feedback_approval_service_pb2.SubmitAnomalyFeedbackRequest
    ) -> anomalies_v1_anomaly_feedback_approval_service_pb2.SubmitAnomalyFeedbackResponse:
        """Submits an anomaly feedback."""
        deps = self.deps
        response = anomalies_v1_anomaly_feedback_approval_service_pb2.SubmitAnomalyFeedbackResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SubmitAnomalyFeedback', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'SubmitAnomalyFeedback', {'reason': request.reason})
            await deps.repository.save_anomaly_feedback(request.context.tenant_id, request.anomaly_feedback)
            response_0 = lineage_v1_lineage_edge_import_service_pb2.MapLineageEdgeImportColumnsResponse()
            response_1 = anomalies_v1_detector_approval_service_pb2.ApproveDetectorResponse()
            response_2 = datasets_v1_data_schema_calculation_service_pb2.CompareDataSchemaOptionsResponse()
            response_3 = lineage_v1_impact_workflow_service_pb2.RetryImpactWorkflowResponse()
            outgoing_0 = lineage_v1_lineage_edge_import_service_pb2.MapLineageEdgeImportColumnsRequest()
            outgoing_0.context.CopyFrom(request.context)
            outgoing_0.lineage_edge.subject.display_name = request.anomaly_feedback.subject.display_name
            outgoing_0.details.contact.email = request.details.approver.email
            outgoing_0.context.tenant_id = tenant_id.get()
            response_0 = await deps.clients.lineage_lineage_edge_import.MapLineageEdgeImportColumns(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = anomalies_v1_detector_approval_service_pb2.ApproveDetectorRequest(
                context=request.context,
                detector=anomalies_v1_anomalies_pb2.Detector(
                    owner=identity_v1_refs_pb2.UserRef(display_name=response_0.lineage_edge.subject.display_name)
                )
            )
            port_1: AnomalyFeedbackApprovalSubmitAnomalyFeedback1Port = AnomalyFeedbackApprovalSubmitAnomalyFeedback1Adapter(
                deps.clients.anomalies_detector_approval,
                deps.settings.timeout
            )
            response_1 = await port_1.execute(outgoing_1)
            outgoing_2 = datasets_v1_data_schema_calculation_service_pb2.CompareDataSchemaOptionsRequest(
                context=request.context,
                data_schema=datasets_v1_datasets_pb2.DataSchema(
                    children=[
                        datasets_v1_datasets_pb2.DataSchema(
                            children=[
                                datasets_v1_datasets_pb2.DataSchema(
                                    manager=identity_v1_refs_pb2.UserRef(user_id=response_1.detector.owner.user_id)
                                )
                            ]
                        )
                    ]
                )
            )
            steps_2 = [
                partial(
                    deps.clients.datasets_data_schema_calculation.CompareDataSchemaOptions,
                    outgoing_2,
                    timeout=deps.settings.timeout
                )
            ]
            results_2 = await run_steps(steps_2)
            response_2 = results_2[-1]
            outgoing_3 = lineage_v1_impact_workflow_service_pb2.RetryImpactWorkflowRequest(
                context=request.context,
                impact=lineage_v1_lineage_pb2.Impact(
                    audit=common_v1_audit_pb2.AuditInfo(updated_at=response_1.detector.audit.updated_at),
                    customer=customers_v1_refs_pb2.CustomerRef(
                        display_name=request.anomaly_feedback.subject.display_name,
                        email=request.details.approver.email
                    )
                )
            )
            response_3 = await AnomalyFeedbackApprovalSubmitAnomalyFeedback3Adapter(
                deps.clients.lineage_impact_workflow,
                deps.settings.timeout
            )(outgoing_3)
            returned_0_0 = response_0.result.correlation_id
            if returned_0_0:
                response.anomaly_feedback.correlation_id = returned_0_0
            returned_1_0 = response_1.result.status
            if returned_1_0:
                response.result.status = returned_1_0
            returned_2_0 = response_2.result.reference_ids
            response.result.reference_ids.extend(returned_2_0)
            returned_2_1 = response_2.result.details
            response.result.details.update(returned_2_1)
            returned_3_0 = response_3.result.reference_ids
            response.result.reference_ids.extend(returned_3_0)
            echoed_0 = request.anomaly_feedback_id
            response.anomaly_feedback.anomaly_feedback_id = echoed_0
            echoed_1 = request.anomaly_feedback.subject
            response.anomaly_feedback.subject.CopyFrom(echoed_1)
            return response
