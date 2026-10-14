"""Routes detectors through approval, with escalation and delegation."""

from __future__ import annotations

from collections.abc import AsyncIterator
from dataclasses import dataclass
from functools import partial
from typing import Any
from typing import cast
import logging

from google.protobuf.any_pb2 import Any as AnyMessage
from google.protobuf.json_format import MessageToDict
from google.protobuf.json_format import MessageToJson
from google.protobuf.json_format import Parse
from google.protobuf.json_format import ParseDict
import grpc

from acme.analytics.v1 import funnel_query_service_pb2 as analytics_v1_funnel_query_service_pb2
from acme.anomalies.v1 import anomalies_pb2 as anomalies_v1_anomalies_pb2
from acme.anomalies.v1 import anomaly_approval_service_pb2 as anomalies_v1_anomaly_approval_service_pb2
from acme.anomalies.v1 import (
    anomaly_feedback_calculation_service_pb2 as anomalies_v1_anomaly_feedback_calculation_service_pb2,
)
from acme.anomalies.v1 import anomaly_query_service_pb2 as anomalies_v1_anomaly_query_service_pb2
from acme.anomalies.v1 import anomaly_validation_service_pb2 as anomalies_v1_anomaly_validation_service_pb2
from acme.anomalies.v1 import detector_approval_service_pb2 as anomalies_v1_detector_approval_service_pb2
from acme.anomalies.v1 import detector_approval_service_pb2_grpc as anomalies_v1_detector_approval_service_pb2_grpc
from acme.anomalies.v1 import detector_query_service_pb2 as anomalies_v1_detector_query_service_pb2
from acme.catalog.v1 import product_query_service_pb2 as catalog_v1_product_query_service_pb2
from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.customers.v1 import refs_pb2 as customers_v1_refs_pb2
from acme.datasets.v1 import dataset_query_service_pb2 as datasets_v1_dataset_query_service_pb2
from acme.datasets.v1 import (
    dataset_version_calculation_service_pb2 as datasets_v1_dataset_version_calculation_service_pb2,
)
from acme.datasets.v1 import dataset_version_query_service_pb2 as datasets_v1_dataset_version_query_service_pb2
from acme.datasets.v1 import datasets_pb2 as datasets_v1_datasets_pb2
from acme.datasets.v1 import refs_pb2 as datasets_v1_refs_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.lineage.v1 import lineage_node_sync_service_pb2 as lineage_v1_lineage_node_sync_service_pb2
from acme.metrics.v1 import metric_series_query_service_pb2 as metrics_v1_metric_series_query_service_pb2
from acme.venues.v1 import venue_service_pb2 as venues_v1_venue_service_pb2
from acme.venues.v1 import venue_service_pb2_grpc as venues_v1_venue_service_pb2_grpc
from acme.venues.v1 import venues_pb2 as venues_v1_venues_pb2

from acme_data.domains.anomalies import hooks
from acme_data.domains.anomalies.adapters import DetectorApprovalCommentDetectorApproval1Adapter
from acme_data.domains.anomalies.adapters import DetectorApprovalCommentDetectorApproval1Port
from acme_data.domains.anomalies.dependencies import Dependencies
from acme_data.domains.anomalies.models import DetectorApprovalApproveDetector0Command
from acme_data.domains.anomalies.models import DetectorApprovalRejectDetector2Command
from acme_data.domains.anomalies.models import DetectorApprovalSubmitDetector0Command
from acme_data.domains.anomalies.models import to_detector_approval_approve_detector0_command
from acme_data.domains.anomalies.models import to_detector_approval_reject_detector2_command
from acme_data.domains.anomalies.models import to_detector_approval_submit_detector0_command
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import run_steps
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_id
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


@dataclass(slots=True)
class DetectorApprovalServicer(anomalies_v1_detector_approval_service_pb2_grpc.DetectorApprovalServiceServicer):
    deps: Dependencies

    @rpc_errors
    async def ApproveDetector(
        self, request: anomalies_v1_detector_approval_service_pb2.ApproveDetectorRequest, context: grpc.aio.ServicerContext,
    ) -> anomalies_v1_detector_approval_service_pb2.ApproveDetectorResponse:
        """Approves a detector."""
        return await self.handle_approve_detector(request)

    @rpc_errors
    async def CommentDetectorApproval(
        self, request: anomalies_v1_detector_approval_service_pb2.CommentDetectorApprovalRequest, context: grpc.aio.ServicerContext,
    ) -> anomalies_v1_detector_approval_service_pb2.CommentDetectorApprovalResponse:
        """Comments a detector."""
        return await self.handle_comment_detector_approval(request)

    @rpc_errors
    async def DelegateDetectorApproval(
        self, request: anomalies_v1_detector_approval_service_pb2.DelegateDetectorApprovalRequest, context: grpc.aio.ServicerContext,
    ) -> anomalies_v1_detector_approval_service_pb2.DelegateDetectorApprovalResponse:
        """Delegates a detector."""
        return await self.handle_delegate_detector_approval(request)

    @rpc_errors
    async def EscalateDetector(
        self, request: anomalies_v1_detector_approval_service_pb2.EscalateDetectorRequest, context: grpc.aio.ServicerContext,
    ) -> anomalies_v1_detector_approval_service_pb2.EscalateDetectorResponse:
        """Escalates a detector."""
        return await self.handle_escalate_detector(request)

    @rpc_errors
    @retry_transient
    async def GetDetectorApprovalStatus(
        self, request: anomalies_v1_detector_approval_service_pb2.GetDetectorApprovalStatusRequest, context: grpc.aio.ServicerContext,
    ) -> anomalies_v1_detector_approval_service_pb2.GetDetectorApprovalStatusResponse:
        """Returns a detector."""
        return await self.handle_get_detector_approval_status(request)

    @rpc_errors
    @retry_transient
    async def ListPendingDetectors(
        self, request: anomalies_v1_detector_approval_service_pb2.ListPendingDetectorsRequest, context: grpc.aio.ServicerContext,
    ) -> anomalies_v1_detector_approval_service_pb2.ListPendingDetectorsResponse:
        """Lists detectors a page at a time."""
        return await self.handle_list_pending_detectors(request)

    @rpc_errors
    async def RecallDetector(
        self, request: anomalies_v1_detector_approval_service_pb2.RecallDetectorRequest, context: grpc.aio.ServicerContext,
    ) -> anomalies_v1_detector_approval_service_pb2.RecallDetectorResponse:
        """Recalls a detector."""
        return await self.handle_recall_detector(request)

    @rpc_errors
    async def RejectDetector(
        self, request: anomalies_v1_detector_approval_service_pb2.RejectDetectorRequest, context: grpc.aio.ServicerContext,
    ) -> anomalies_v1_detector_approval_service_pb2.RejectDetectorResponse:
        """Rejects a detector."""
        return await self.handle_reject_detector(request)

    @rpc_errors
    async def SubmitDetector(
        self, request: anomalies_v1_detector_approval_service_pb2.SubmitDetectorRequest, context: grpc.aio.ServicerContext,
    ) -> anomalies_v1_detector_approval_service_pb2.SubmitDetectorResponse:
        """Submits a detector."""
        return await self.handle_submit_detector(request)

    async def handle_approve_detector(
        self,
        request: anomalies_v1_detector_approval_service_pb2.ApproveDetectorRequest
    ) -> anomalies_v1_detector_approval_service_pb2.ApproveDetectorResponse:
        """Approves a detector."""
        deps = self.deps
        response = anomalies_v1_detector_approval_service_pb2.ApproveDetectorResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ApproveDetector', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'ApproveDetector', {'reason': request.reason})
            await deps.repository.save_detector(request.context.tenant_id, request.detector)
            response_0 = anomalies_v1_anomaly_approval_service_pb2.SubmitAnomalyResponse()
            response_1 = anomalies_v1_anomaly_query_service_pb2.SummarizeAnomaliesResponse()
            response_2 = catalog_v1_product_query_service_pb2.BrowseProductsResponse()
            response_3 = anomalies_v1_anomaly_feedback_calculation_service_pb2.EstimateAnomalyFeedbackResponse()
            command_0 = DetectorApprovalApproveDetector0Command(
                context=request.context,
                details_approver_email=request.detector.owner.email,
                anomaly_audit_created_by=request.detector.audit.created_by
            )
            outgoing_0 = to_detector_approval_approve_detector0_command(command_0)
            response_0 = await deps.clients.anomalies_anomaly_approval.SubmitAnomaly(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = anomalies_v1_anomaly_query_service_pb2.SummarizeAnomaliesRequest()
            outgoing_1.context.CopyFrom(request.context)
            if request.detector.WhichOneof('action') == 'block':
                outgoing_1.reason = request.detector.block.reason
            outgoing_1.anomaly_id = response_0.anomaly.anomaly_id
            response_1 = await deps.clients.anomalies_anomaly_query.SummarizeAnomalies(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = catalog_v1_product_query_service_pb2.BrowseProductsRequest(
                context=request.context,
                filter=catalog_v1_product_query_service_pb2.BrowseProductsRequest.Filter(
                    created_after=response_0.anomaly.audit.updated_at,
                    labels=dict(response_0.anomaly.custom_fields),
                    owner_id=response_0.anomaly.anomaly_id
                )
            )
            send_2 = partial(deps.clients.catalog_product_query.BrowseProducts, timeout=deps.settings.timeout)
            response_2 = await send_2(outgoing_2)
            outgoing_3 = anomalies_v1_anomaly_feedback_calculation_service_pb2.EstimateAnomalyFeedbackRequest(
                annotations=dict(request.annotations),
                anomaly_feedback=anomalies_v1_anomalies_pb2.AnomalyFeedback(
                    correlation_id=response_2.result.correlation_id,
                    subject=datasets_v1_refs_pb2.DatasetRef(display_name=request.details.approver.display_name)
                ),
                context=request.context,
                reason=request.detector.block.reason
            )
            response_3 = await hooks.detector_approval_approve_detector3(
                deps.clients.anomalies_anomaly_feedback_calculation,
                outgoing_3,
                deps.settings.timeout
            )
            returned_0_0 = response_0.anomaly.assignee.email
            if returned_0_0:
                response.detector.owner.email = returned_0_0
            returned_0_1 = response_0.anomaly.priority
            if returned_0_1:
                response.detector.priority = returned_0_1
            returned_1_0 = response_1.result.message
            if returned_1_0:
                response.outcome.message = returned_1_0
            returned_2_0 = response_2.result.details
            response.result.details.update(returned_2_0)
            returned_2_1 = response_2.result.status
            if returned_2_1:
                response.result.status = returned_2_1
            returned_3_0 = response_3.result.status
            if returned_3_0:
                response.outcome.status = returned_3_0
            returned_3_1 = response_3.result.reference_ids
            response.result.reference_ids.extend(returned_3_1)
            echoed_0 = request.detector_id
            response.detector.detector_id = echoed_0
            echoed_1 = request.detector.status
            response.detector.status = echoed_1
            return response

    async def handle_comment_detector_approval(
        self,
        request: anomalies_v1_detector_approval_service_pb2.CommentDetectorApprovalRequest
    ) -> anomalies_v1_detector_approval_service_pb2.CommentDetectorApprovalResponse:
        """Comments a detector."""
        deps = self.deps
        response = anomalies_v1_detector_approval_service_pb2.CommentDetectorApprovalResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CommentDetectorApproval', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'CommentDetectorApproval',
                {'reason': request.reason}
            )
            await deps.repository.save_detector(request.context.tenant_id, request.detector)
            response_0 = anomalies_v1_detector_query_service_pb2.PeekDetectorResponse()
            response_1 = analytics_v1_funnel_query_service_pb2.SuggestFunnelsResponse()
            outgoing_0 = anomalies_v1_detector_query_service_pb2.PeekDetectorRequest()
            outgoing_0.context.CopyFrom(request.context)
            outgoing_0.detector_id = request.detector.detector_id
            outgoing_0.context.tenant_id = tenant_id.get()
            response_0 = await deps.clients.anomalies_detector_query.PeekDetector(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = analytics_v1_funnel_query_service_pb2.SuggestFunnelsRequest(
                context=request.context,
                filter=analytics_v1_funnel_query_service_pb2.SuggestFunnelsRequest.Filter(
                    created_after=response_0.detector.audit.updated_at,
                    labels=dict(response_0.result.details),
                    owner_id=request.detector.owner.user_id
                )
            )
            port_1: DetectorApprovalCommentDetectorApproval1Port = DetectorApprovalCommentDetectorApproval1Adapter(
                deps.clients.analytics_funnel_query,
                deps.settings.timeout
            )
            response_1 = await port_1.execute(outgoing_1)
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.result.message = returned_0_0
            returned_1_0 = response_1.result.message
            if returned_1_0:
                response.result.message = returned_1_0
            echoed_0 = request.detector_id
            response.detector.detector_id = echoed_0
            echoed_1 = request.detector.name
            response.detector.name = echoed_1
            return response

    async def handle_delegate_detector_approval(
        self,
        request: anomalies_v1_detector_approval_service_pb2.DelegateDetectorApprovalRequest
    ) -> anomalies_v1_detector_approval_service_pb2.DelegateDetectorApprovalResponse:
        """Delegates a detector."""
        deps = self.deps
        response = anomalies_v1_detector_approval_service_pb2.DelegateDetectorApprovalResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('DelegateDetectorApproval', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'DelegateDetectorApproval',
                {'reason': request.reason}
            )
            await deps.repository.save_detector(request.context.tenant_id, request.detector)
            response_0 = anomalies_v1_anomaly_feedback_calculation_service_pb2.ExplainAnomalyFeedbackCalculationResponse()
            outgoing_0 = anomalies_v1_anomaly_feedback_calculation_service_pb2.ExplainAnomalyFeedbackCalculationRequest(
                anomaly_feedback=anomalies_v1_anomalies_pb2.AnomalyFeedback(
                    subject=datasets_v1_refs_pb2.DatasetRef(display_name=request.details.approver.display_name)
                ),
                context=request.context,
                details=anomalies_v1_anomaly_feedback_calculation_service_pb2.ExplainAnomalyFeedbackCalculationRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(email=request.details.approver.email)
                )
            )
            steps_0 = [
                partial(
                    deps.clients.anomalies_anomaly_feedback_calculation.ExplainAnomalyFeedbackCalculation,
                    outgoing_0,
                    timeout=deps.settings.timeout
                )
            ]
            results_0 = await run_steps(steps_0)
            response_0 = results_0[-1]
            returned_0_0 = response_0.anomaly_feedback.subject.display_name
            if returned_0_0:
                response.detector.owner.display_name = returned_0_0
            echoed_0 = request.detector_id
            response.detector.detector_id = echoed_0
            echoed_1 = request.detector.effective
            response.detector.effective.CopyFrom(echoed_1)
            return response

    async def handle_escalate_detector(
        self,
        request: anomalies_v1_detector_approval_service_pb2.EscalateDetectorRequest
    ) -> anomalies_v1_detector_approval_service_pb2.EscalateDetectorResponse:
        """Escalates a detector."""
        deps = self.deps
        response = anomalies_v1_detector_approval_service_pb2.EscalateDetectorResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('EscalateDetector', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'EscalateDetector', {'reason': request.reason})
            await deps.repository.save_detector(request.context.tenant_id, request.detector)
            response_0 = datasets_v1_dataset_query_service_pb2.ExportDatasetsResponse()
            response_1 = anomalies_v1_anomaly_validation_service_pb2.ScoreAnomalyResponse()
            outgoing_0 = datasets_v1_dataset_query_service_pb2.ExportDatasetsRequest(
                context=request.context,
                filter=datasets_v1_dataset_query_service_pb2.ExportDatasetsRequest.Filter(
                    created_after=request.detector.audit.updated_at,
                    owner_id=request.detector.detector_id
                )
            )
            async for chunk_0 in deps.clients.datasets_dataset_query.ExportDatasets(
                outgoing_0,
                timeout=deps.settings.timeout
            ):
                response_0 = chunk_0
            outgoing_1 = anomalies_v1_anomaly_validation_service_pb2.ScoreAnomalyRequest(
                anomaly=anomalies_v1_anomalies_pb2.Anomaly(
                    assignee=identity_v1_refs_pb2.UserRef(user_id=request.details.approver.user_id)
                ),
                context=request.context
            )
            response_1 = cast(anomalies_v1_anomaly_validation_service_pb2.ScoreAnomalyResponse, await deps.bus.request(
                'acme.anomalies.v1.DetectorApprovalService/EscalateDetector/1', outgoing_1, deps.settings.timeout,
            ))
            returned_1_0 = response_1.anomaly.assignee.display_name
            if returned_1_0:
                response.detector.owner.display_name = returned_1_0
            echoed_0 = request.detector_id
            response.detector.detector_id = echoed_0
            echoed_1 = request.detector.description
            response.detector.description = echoed_1
            return response

    async def handle_get_detector_approval_status(
        self,
        request: anomalies_v1_detector_approval_service_pb2.GetDetectorApprovalStatusRequest
    ) -> anomalies_v1_detector_approval_service_pb2.GetDetectorApprovalStatusResponse:
        """Returns a detector."""
        deps = self.deps
        response = anomalies_v1_detector_approval_service_pb2.GetDetectorApprovalStatusResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('GetDetectorApprovalStatus', extra={'fields': {'domain': 'anomalies'}})
            await deps.repository.audit(request.context.tenant_id, 'GetDetectorApprovalStatus', {})
            response_0 = anomalies_v1_detector_query_service_pb2.BrowseDetectorsResponse()
            outgoing_0 = anomalies_v1_detector_query_service_pb2.BrowseDetectorsRequest(
                context=request.context,
                filter=anomalies_v1_detector_query_service_pb2.BrowseDetectorsRequest.Filter(
                    created_after=request.context.deadline,
                    labels=dict(request.context.baggage),
                    owner_id=request.context.trace_id
                )
            )
            response_0 = await deps.clients.anomalies_detector_query.BrowseDetectors(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.correlation_id
            if returned_0_0:
                response.result.correlation_id = returned_0_0
            echoed_0 = request.detector_id
            response.detector.detector_id = echoed_0
            return response

    async def handle_list_pending_detectors(
        self,
        request: anomalies_v1_detector_approval_service_pb2.ListPendingDetectorsRequest
    ) -> anomalies_v1_detector_approval_service_pb2.ListPendingDetectorsResponse:
        """Lists detectors a page at a time."""
        deps = self.deps
        response = anomalies_v1_detector_approval_service_pb2.ListPendingDetectorsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ListPendingDetectors', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ListPendingDetectors',
                {'order_by': request.order_by}
            )
            response_0 = datasets_v1_dataset_version_calculation_service_pb2.CompareDatasetVersionOptionsResponse()
            response_1 = datasets_v1_dataset_version_query_service_pb2.FindDatasetVersionsResponse()
            outgoing_0 = datasets_v1_dataset_version_calculation_service_pb2.CompareDatasetVersionOptionsRequest(
                context=request.context,
                dataset_version=datasets_v1_datasets_pb2.DatasetVersion(
                    measurements=[
                        datasets_v1_datasets_pb2.DatasetVersionMeasurement(observed_at=request.filter.created_after)
                    ],
                    subject=customers_v1_refs_pb2.CustomerRef(email=request.context.actor.email)
                ),
                details=datasets_v1_dataset_version_calculation_service_pb2.CompareDatasetVersionOptionsRequest.Details(
                    destination=common_v1_address_pb2.PostalAddress(region=request.filter.region)
                )
            )
            response_0 = await deps.clients.datasets_dataset_version_calculation.CompareDatasetVersionOptions(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            fields_1: dict[str, Any] = {
                'context': request.context,
                'filter': {
                    'created_after': request.filter.created_after,
                    'owner_id': request.filter.owner_id,
                    'query': request.filter.query
                },
                'page': {'page_size': request.page.page_size}
            }
            outgoing_1 = datasets_v1_dataset_version_query_service_pb2.FindDatasetVersionsRequest(**fields_1)
            response_1 = await deps.clients.datasets_dataset_version_query.FindDatasetVersions(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.correlation_id
            if returned_0_0:
                response.result.correlation_id = returned_0_0
            returned_0_1 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_1)
            returned_1_0 = response_1.result.status
            if returned_1_0:
                response.result.status = returned_1_0
            returned_1_1 = response_1.page_info.next_page_token
            if returned_1_1:
                response.page_info.next_page_token = returned_1_1
            return response

    async def handle_recall_detector(
        self,
        request: anomalies_v1_detector_approval_service_pb2.RecallDetectorRequest
    ) -> anomalies_v1_detector_approval_service_pb2.RecallDetectorResponse:
        """Recalls a detector."""
        deps = self.deps
        response = anomalies_v1_detector_approval_service_pb2.RecallDetectorResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('RecallDetector', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'RecallDetector', {'reason': request.reason})
            await deps.repository.save_detector(request.context.tenant_id, request.detector)
            response_0 = anomalies_v1_detector_query_service_pb2.LookupDetectorResponse()
            response_1 = anomalies_v1_anomaly_approval_service_pb2.CommentAnomalyApprovalResponse()
            response_2 = anomalies_v1_anomaly_approval_service_pb2.DelegateAnomalyApprovalResponse()
            outgoing_0 = anomalies_v1_detector_query_service_pb2.LookupDetectorRequest(
                context=request.context,
                detector_id=request.detector.detector_id
            )
            document_0 = MessageToDict(outgoing_0, preserving_proto_field_name=True)
            outgoing_0 = ParseDict(document_0, anomalies_v1_detector_query_service_pb2.LookupDetectorRequest())
            response_0 = await deps.clients.anomalies_detector_query.LookupDetector(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = anomalies_v1_anomaly_approval_service_pb2.CommentAnomalyApprovalRequest(
                anomaly=anomalies_v1_anomalies_pb2.Anomaly(
                    audit=common_v1_audit_pb2.AuditInfo(updated_by=response_0.detector.audit.updated_by),
                    requester=common_v1_contact_pb2.ContactInfo(email=response_0.detector.owner.email)
                ),
                context=request.context
            )
            document_1 = MessageToJson(outgoing_1, preserving_proto_field_name=True)
            outgoing_1 = Parse(document_1, anomalies_v1_anomaly_approval_service_pb2.CommentAnomalyApprovalRequest())
            response_1 = await deps.clients.anomalies_anomaly_approval.CommentAnomalyApproval(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = anomalies_v1_anomaly_approval_service_pb2.DelegateAnomalyApprovalRequest()
            outgoing_2.context.CopyFrom(request.context)
            outgoing_2.anomaly.customer.version = response_1.anomaly.customer.version
            outgoing_2.anomaly.audit.created_by = response_1.anomaly.audit.created_by
            outgoing_2.anomaly.sla.breached = response_1.anomaly.sla.breached
            outgoing_2.anomaly.assignee.email = response_0.detector.owner.email
            merged_2 = anomalies_v1_anomaly_approval_service_pb2.DelegateAnomalyApprovalRequest()
            merged_2.MergeFrom(outgoing_2)
            outgoing_2.CopyFrom(merged_2)
            response_2 = await deps.clients.anomalies_anomaly_approval.DelegateAnomalyApproval(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.detector.owner.display_name
            if returned_0_0:
                response.detector.owner.display_name = returned_0_0
            returned_0_1 = response_0.detector.audit.updated_at
            if returned_0_1.ListFields():
                response.detector.audit.updated_at.MergeFrom(returned_0_1)
            returned_1_0 = response_1.result.message
            if returned_1_0:
                response.outcome.message = returned_1_0
            returned_1_1 = response_1.anomaly.assignee.user_id
            if returned_1_1:
                response.detector.owner.user_id = returned_1_1
            returned_2_0 = response_2.outcome.message
            if returned_2_0:
                response.outcome.message = returned_2_0
            returned_2_1 = response_2.anomaly.customer.display_name
            if returned_2_1:
                response.detector.owner.display_name = returned_2_1
            echoed_0 = request.detector_id
            response.detector.detector_id = echoed_0
            echoed_1 = request.detector.parameters
            response.detector.parameters.update(echoed_1)
            return response

    async def handle_reject_detector(
        self,
        request: anomalies_v1_detector_approval_service_pb2.RejectDetectorRequest
    ) -> anomalies_v1_detector_approval_service_pb2.RejectDetectorResponse:
        """Rejects a detector."""
        deps = self.deps
        response = anomalies_v1_detector_approval_service_pb2.RejectDetectorResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('RejectDetector', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'RejectDetector', {'reason': request.reason})
            await deps.repository.save_detector(request.context.tenant_id, request.detector)
            response_0 = anomalies_v1_anomaly_feedback_calculation_service_pb2.CalculateAnomalyFeedbackResponse()
            response_1 = venues_v1_venue_service_pb2.UpdateVenueResponse()
            response_2 = anomalies_v1_anomaly_query_service_pb2.ResolveAnomaliesResponse()
            outgoing_0 = anomalies_v1_anomaly_feedback_calculation_service_pb2.CalculateAnomalyFeedbackRequest(
                annotations=dict(request.annotations),
                anomaly_feedback=anomalies_v1_anomalies_pb2.AnomalyFeedback(
                    measurements=[
                        anomalies_v1_anomalies_pb2.AnomalyFeedbackMeasurement(observed_at=request.details.effective_at)
                    ],
                    subject=datasets_v1_refs_pb2.DatasetRef(display_name=request.details.approver.display_name)
                ),
                context=request.context,
                reason=request.detector.block.reason
            )
            envelope_0 = AnyMessage()
            envelope_0.Pack(outgoing_0)
            outgoing_0 = anomalies_v1_anomaly_feedback_calculation_service_pb2.CalculateAnomalyFeedbackRequest()
            if not envelope_0.Unpack(outgoing_0):
                raise ValueError("partner envelope contains the wrong request type")
            response_0 = await deps.clients.anomalies_anomaly_feedback_calculation.CalculateAnomalyFeedback(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = venues_v1_venue_service_pb2.UpdateVenueRequest(
                context=request.context,
                venue=venues_v1_venues_pb2.Venue(
                    audit=common_v1_audit_pb2.AuditInfo(
                        created_at=request.detector.audit.created_at,
                        updated_at=request.detector.audit.updated_at
                    ),
                    owner=identity_v1_refs_pb2.UserRef(
                        display_name=request.detector.owner.display_name,
                        user_id=request.detector.owner.user_id
                    )
                )
            )
            registered_1 = cast(
                venues_v1_venue_service_pb2_grpc.VenueServiceStub,
                deps.clients.registry['acme.venues.v1.VenueService']
            )
            response_1 = await registered_1.UpdateVenue(outgoing_1, timeout=deps.settings.timeout)
            command_2 = DetectorApprovalRejectDetector2Command(context=request.context)
            outgoing_2 = to_detector_approval_reject_detector2_command(command_2)
            response_2 = await deps.clients.anomalies_anomaly_query.ResolveAnomalies(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.correlation_id
            if returned_0_0:
                response.result.correlation_id = returned_0_0
            returned_1_0 = response_1.result.status
            if returned_1_0:
                response.result.status = returned_1_0
            returned_1_1 = response_1.venue.audit.created_by
            if returned_1_1:
                response.detector.audit.created_by = returned_1_1
            returned_2_0 = response_2.result.status
            if returned_2_0:
                response.result.status = returned_2_0
            returned_2_1 = response_2.result.correlation_id
            if returned_2_1:
                response.result.correlation_id = returned_2_1
            echoed_0 = request.detector_id
            response.detector.detector_id = echoed_0
            echoed_1 = request.detector.owner
            response.detector.owner.CopyFrom(echoed_1)
            return response

    async def handle_submit_detector(
        self,
        request: anomalies_v1_detector_approval_service_pb2.SubmitDetectorRequest
    ) -> anomalies_v1_detector_approval_service_pb2.SubmitDetectorResponse:
        """Submits a detector."""
        deps = self.deps
        response = anomalies_v1_detector_approval_service_pb2.SubmitDetectorResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SubmitDetector', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'SubmitDetector', {'reason': request.reason})
            await deps.repository.save_detector(request.context.tenant_id, request.detector)
            response_0 = lineage_v1_lineage_node_sync_service_pb2.PullLineageNodesResponse()
            response_1 = datasets_v1_dataset_version_calculation_service_pb2.EstimateDatasetVersionResponse()
            response_2 = metrics_v1_metric_series_query_service_pb2.SuggestMetricSeriesesResponse()
            command_0 = DetectorApprovalSubmitDetector0Command.model_validate(
                {
                    'context': request.context,
                    'lineage_node_children_children_audit_updated_at': request.detector.audit.updated_at,
                    'lineage_node_children_children_audit_etag': request.detector.audit.etag,
                    'lineage_node_children_children_manager_display_name': request.detector.owner.display_name,
                    'lineage_node_children_children_manager_email': request.detector.owner.email
                }
            )
            outgoing_0 = to_detector_approval_submit_detector0_command(command_0)
            response_0 = await deps.clients.lineage_lineage_node_sync.PullLineageNodes(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = datasets_v1_dataset_version_calculation_service_pb2.EstimateDatasetVersionRequest(
                context=request.context,
                dataset_version=datasets_v1_datasets_pb2.DatasetVersion(
                    subject=customers_v1_refs_pb2.CustomerRef(display_name=response_0.lineage_node.manager.display_name)
                ),
                details=datasets_v1_dataset_version_calculation_service_pb2.EstimateDatasetVersionRequest.Details(
                    destination=common_v1_address_pb2.PostalAddress(
                        lines=list(response_0.lineage_node.location.lines),
                        region=response_0.lineage_node.location.region
                    )
                )
            )
            send_1 = partial(
                deps.clients.datasets_dataset_version_calculation.EstimateDatasetVersion,
                timeout=deps.settings.timeout
            )
            response_1 = await send_1(outgoing_1)
            outgoing_2 = metrics_v1_metric_series_query_service_pb2.SuggestMetricSeriesesRequest(
                context=request.context,
                filter=metrics_v1_metric_series_query_service_pb2.SuggestMetricSeriesesRequest.Filter(
                    created_after=request.detector.audit.updated_at,
                    region=response_0.lineage_node.location.region
                )
            )
            response_2 = await hooks.detector_approval_submit_detector2(
                deps.clients.metrics_metric_series_query,
                outgoing_2,
                deps.settings.timeout
            )
            returned_0_0 = response_0.outcome.next_steps
            response.outcome.next_steps.extend(returned_0_0)
            returned_1_0 = response_1.dataset_version.correlation_id
            if returned_1_0:
                response.result.correlation_id = returned_1_0
            returned_1_1 = response_1.dataset_version.subject.display_name
            if returned_1_1:
                response.detector.owner.display_name = returned_1_1
            returned_2_0 = response_2.result.status
            if returned_2_0:
                response.result.status = returned_2_0
            returned_2_1 = response_2.result.message
            if returned_2_1:
                response.result.message = returned_2_1
            echoed_0 = request.detector_id
            response.detector.detector_id = echoed_0
            echoed_1 = request.detector.parameters
            response.detector.parameters.update(echoed_1)
            return response
