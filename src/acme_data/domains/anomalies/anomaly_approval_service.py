"""Routes anomalies through approval, with escalation and delegation."""

from __future__ import annotations

from collections.abc import AsyncIterator
from collections.abc import Awaitable
from collections.abc import Callable
from functools import partial
from typing import Any
from typing import cast
import asyncio
import logging

from google.protobuf.json_format import MessageToDict
from google.protobuf.json_format import ParseDict
import grpc

from acme.anomalies.v1 import anomalies_pb2 as anomalies_v1_anomalies_pb2
from acme.anomalies.v1 import anomaly_approval_service_pb2 as anomalies_v1_anomaly_approval_service_pb2
from acme.anomalies.v1 import anomaly_approval_service_pb2_grpc as anomalies_v1_anomaly_approval_service_pb2_grpc
from acme.anomalies.v1 import (
    anomaly_feedback_calculation_service_pb2 as anomalies_v1_anomaly_feedback_calculation_service_pb2,
)
from acme.anomalies.v1 import (
    anomaly_feedback_validation_service_pb2 as anomalies_v1_anomaly_feedback_validation_service_pb2,
)
from acme.anomalies.v1 import anomaly_query_service_pb2 as anomalies_v1_anomaly_query_service_pb2
from acme.anomalies.v1 import anomaly_service_pb2 as anomalies_v1_anomaly_service_pb2
from acme.anomalies.v1 import detector_query_service_pb2 as anomalies_v1_detector_query_service_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.customers.v1 import customer_query_service_pb2 as customers_v1_customer_query_service_pb2
from acme.customers.v1 import refs_pb2 as customers_v1_refs_pb2
from acme.datasets.v1 import dataset_query_service_pb2 as datasets_v1_dataset_query_service_pb2
from acme.datasets.v1 import dataset_validation_service_pb2 as datasets_v1_dataset_validation_service_pb2
from acme.datasets.v1 import (
    dataset_version_calculation_service_pb2 as datasets_v1_dataset_version_calculation_service_pb2,
)
from acme.datasets.v1 import (
    dataset_version_validation_service_pb2 as datasets_v1_dataset_version_validation_service_pb2,
)
from acme.datasets.v1 import datasets_pb2 as datasets_v1_datasets_pb2
from acme.datasets.v1 import refs_pb2 as datasets_v1_refs_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.lineage.v1 import impact_sync_service_pb2 as lineage_v1_impact_sync_service_pb2
from acme.lineage.v1 import lineage_node_approval_service_pb2 as lineage_v1_lineage_node_approval_service_pb2
from acme.lineage.v1 import lineage_pb2 as lineage_v1_lineage_pb2
from acme.payroll.v1 import pay_run_calculation_service_pb2 as payroll_v1_pay_run_calculation_service_pb2
from acme.payroll.v1 import payroll_pb2 as payroll_v1_payroll_pb2
from acme.payroll.v1 import refs_pb2 as payroll_v1_refs_pb2
from acme.pipelines.v1 import pipeline_service_pb2 as pipelines_v1_pipeline_service_pb2

from acme_data.domains.anomalies.adapters import AnomalyApprovalCommentAnomalyApproval0Adapter
from acme_data.domains.anomalies.dependencies import Dependencies
from acme_data.domains.anomalies.models import AnomalyApprovalListPendingAnomalies1Command
from acme_data.domains.anomalies.models import AnomalyApprovalRecallAnomaly0Command
from acme_data.domains.anomalies.models import to_anomaly_approval_list_pending_anomalies1_command
from acme_data.domains.anomalies.models import to_anomaly_approval_recall_anomaly0_command
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import run_steps
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_id
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class AnomalyApprovalServicer(anomalies_v1_anomaly_approval_service_pb2_grpc.AnomalyApprovalServiceServicer):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    async def ApproveAnomaly(
        self, request: anomalies_v1_anomaly_approval_service_pb2.ApproveAnomalyRequest, context: grpc.aio.ServicerContext,
    ) -> anomalies_v1_anomaly_approval_service_pb2.ApproveAnomalyResponse:
        """Approves an anomaly."""
        return await self.handle_approve_anomaly(request)

    @rpc_errors
    async def CommentAnomalyApproval(
        self, request: anomalies_v1_anomaly_approval_service_pb2.CommentAnomalyApprovalRequest, context: grpc.aio.ServicerContext,
    ) -> anomalies_v1_anomaly_approval_service_pb2.CommentAnomalyApprovalResponse:
        """Comments an anomaly."""
        return await self.handle_comment_anomaly_approval(request)

    @rpc_errors
    async def DelegateAnomalyApproval(
        self, request: anomalies_v1_anomaly_approval_service_pb2.DelegateAnomalyApprovalRequest, context: grpc.aio.ServicerContext,
    ) -> anomalies_v1_anomaly_approval_service_pb2.DelegateAnomalyApprovalResponse:
        """Delegates an anomaly."""
        return await self.handle_delegate_anomaly_approval(request)

    @rpc_errors
    async def EscalateAnomaly(
        self, request: anomalies_v1_anomaly_approval_service_pb2.EscalateAnomalyRequest, context: grpc.aio.ServicerContext,
    ) -> anomalies_v1_anomaly_approval_service_pb2.EscalateAnomalyResponse:
        """Escalates an anomaly."""
        return await self.handle_escalate_anomaly(request)

    @rpc_errors
    @retry_transient
    async def GetAnomalyApprovalStatus(
        self, request: anomalies_v1_anomaly_approval_service_pb2.GetAnomalyApprovalStatusRequest, context: grpc.aio.ServicerContext,
    ) -> anomalies_v1_anomaly_approval_service_pb2.GetAnomalyApprovalStatusResponse:
        """Returns an anomaly."""
        return await self.handle_get_anomaly_approval_status(request)

    @rpc_errors
    @retry_transient
    async def ListPendingAnomalies(
        self, request: anomalies_v1_anomaly_approval_service_pb2.ListPendingAnomaliesRequest, context: grpc.aio.ServicerContext,
    ) -> anomalies_v1_anomaly_approval_service_pb2.ListPendingAnomaliesResponse:
        """Lists anomalies a page at a time."""
        return await self.handle_list_pending_anomalies(request)

    @rpc_errors
    async def RecallAnomaly(
        self, request: anomalies_v1_anomaly_approval_service_pb2.RecallAnomalyRequest, context: grpc.aio.ServicerContext,
    ) -> anomalies_v1_anomaly_approval_service_pb2.RecallAnomalyResponse:
        """Recalls an anomaly."""
        return await self.handle_recall_anomaly(request)

    @rpc_errors
    async def RejectAnomaly(
        self, request: anomalies_v1_anomaly_approval_service_pb2.RejectAnomalyRequest, context: grpc.aio.ServicerContext,
    ) -> anomalies_v1_anomaly_approval_service_pb2.RejectAnomalyResponse:
        """Rejects an anomaly."""
        return await self.handle_reject_anomaly(request)

    @rpc_errors
    async def SubmitAnomaly(
        self, request: anomalies_v1_anomaly_approval_service_pb2.SubmitAnomalyRequest, context: grpc.aio.ServicerContext,
    ) -> anomalies_v1_anomaly_approval_service_pb2.SubmitAnomalyResponse:
        """Submits an anomaly."""
        return await self.handle_submit_anomaly(request)

    async def handle_approve_anomaly(
        self,
        request: anomalies_v1_anomaly_approval_service_pb2.ApproveAnomalyRequest
    ) -> anomalies_v1_anomaly_approval_service_pb2.ApproveAnomalyResponse:
        """Approves an anomaly."""
        deps = self.deps
        response = anomalies_v1_anomaly_approval_service_pb2.ApproveAnomalyResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ApproveAnomaly', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'ApproveAnomaly', {'reason': request.reason})
            await deps.repository.save_anomaly(request.context.tenant_id, request.anomaly)
            response_0 = lineage_v1_lineage_node_approval_service_pb2.CommentLineageNodeApprovalResponse()
            outgoing_0 = lineage_v1_lineage_node_approval_service_pb2.CommentLineageNodeApprovalRequest(
                context=request.context,
                lineage_node=lineage_v1_lineage_pb2.LineageNode(
                    children=[
                        lineage_v1_lineage_pb2.LineageNode(
                            children=[
                                lineage_v1_lineage_pb2.LineageNode(
                                    audit=common_v1_audit_pb2.AuditInfo(updated_by=request.anomaly.audit.updated_by),
                                    manager=identity_v1_refs_pb2.UserRef(email=request.details.approver.email)
                                )
                            ]
                        )
                    ]
                )
            )
            steps_0 = [
                partial(
                    deps.clients.lineage_lineage_node_approval.CommentLineageNodeApproval,
                    outgoing_0,
                    timeout=deps.settings.timeout
                )
            ]
            results_0 = await run_steps(steps_0)
            response_0 = results_0[-1]
            returned_0_0 = response_0.lineage_node.audit.created_at
            if returned_0_0.ListFields():
                response.anomaly.audit.created_at.MergeFrom(returned_0_0)
            echoed_0 = request.anomaly_id
            response.anomaly.anomaly_id = echoed_0
            echoed_1 = request.anomaly.assignee
            response.anomaly.assignee.CopyFrom(echoed_1)
            return response

    async def handle_comment_anomaly_approval(
        self,
        request: anomalies_v1_anomaly_approval_service_pb2.CommentAnomalyApprovalRequest
    ) -> anomalies_v1_anomaly_approval_service_pb2.CommentAnomalyApprovalResponse:
        """Comments an anomaly."""
        deps = self.deps
        response = anomalies_v1_anomaly_approval_service_pb2.CommentAnomalyApprovalResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CommentAnomalyApproval', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'CommentAnomalyApproval', {'reason': request.reason})
            await deps.repository.save_anomaly(request.context.tenant_id, request.anomaly)
            response_0 = datasets_v1_dataset_query_service_pb2.ResolveDatasetsResponse()
            response_1 = anomalies_v1_anomaly_service_pb2.GetAnomalyResponse()
            outgoing_0 = datasets_v1_dataset_query_service_pb2.ResolveDatasetsRequest(context=request.context)
            response_0 = await AnomalyApprovalCommentAnomalyApproval0Adapter(
                deps.clients.datasets_dataset_query,
                deps.settings.timeout
            )(outgoing_0)
            outgoing_1 = anomalies_v1_anomaly_service_pb2.GetAnomalyRequest(
                anomaly_id=request.anomaly.anomaly_id,
                context=request.context
            )
            response_1 = cast(anomalies_v1_anomaly_service_pb2.GetAnomalyResponse, await deps.bus.request(
                'acme.anomalies.v1.AnomalyApprovalService/CommentAnomalyApproval/1', outgoing_1, deps.settings.timeout,
            ))
            returned_0_0 = response_0.result.details
            response.result.details.update(returned_0_0)
            returned_0_1 = response_0.result.message
            if returned_0_1:
                response.result.message = returned_0_1
            returned_1_0 = response_1.result.reference_ids
            response.result.reference_ids.extend(returned_1_0)
            returned_1_1 = response_1.anomaly.sla.policy_id
            if returned_1_1:
                response.anomaly.sla.policy_id = returned_1_1
            echoed_0 = request.anomaly_id
            response.anomaly.anomaly_id = echoed_0
            echoed_1 = request.anomaly.priority
            response.anomaly.priority = echoed_1
            return response

    async def handle_delegate_anomaly_approval(
        self,
        request: anomalies_v1_anomaly_approval_service_pb2.DelegateAnomalyApprovalRequest
    ) -> anomalies_v1_anomaly_approval_service_pb2.DelegateAnomalyApprovalResponse:
        """Delegates an anomaly."""
        deps = self.deps
        response = anomalies_v1_anomaly_approval_service_pb2.DelegateAnomalyApprovalResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('DelegateAnomalyApproval', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'DelegateAnomalyApproval',
                {'reason': request.reason}
            )
            await deps.repository.save_anomaly(request.context.tenant_id, request.anomaly)
            response_0 = datasets_v1_dataset_version_calculation_service_pb2.CompareDatasetVersionOptionsResponse()
            response_1 = anomalies_v1_anomaly_feedback_calculation_service_pb2.RecalculateAnomalyFeedbacksResponse()
            response_2 = pipelines_v1_pipeline_service_pb2.UpdatePipelineResponse()
            response_3 = anomalies_v1_anomaly_feedback_validation_service_pb2.NormalizeAnomalyFeedbackResponse()
            requests_0: list[
                datasets_v1_dataset_version_calculation_service_pb2.CompareDatasetVersionOptionsRequest
            ] = []
            for item_0 in request.anomaly.comments:
                outgoing_0 = datasets_v1_dataset_version_calculation_service_pb2.CompareDatasetVersionOptionsRequest(
                    context=request.context,
                    dataset_version=datasets_v1_datasets_pb2.DatasetVersion(
                        source=item_0.comment_id,
                        subject=customers_v1_refs_pb2.CustomerRef(
                            display_name=request.anomaly.assignee.display_name,
                            email=item_0.author_email
                        )
                    )
                )
                requests_0.append(outgoing_0)
            replies_0 = await asyncio.gather(*(
                deps.clients.datasets_dataset_version_calculation.CompareDatasetVersionOptions(
                    entry,
                    timeout=deps.settings.timeout
                ) for entry in requests_0
            ))
            if replies_0:
                response_0 = replies_0[-1]
            outgoing_1 = anomalies_v1_anomaly_feedback_calculation_service_pb2.RecalculateAnomalyFeedbacksRequest(
                anomaly_feedback=anomalies_v1_anomalies_pb2.AnomalyFeedback(
                    subject=datasets_v1_refs_pb2.DatasetRef(display_name=request.details.approver.display_name)
                ),
                context=request.context,
                details=anomalies_v1_anomaly_feedback_calculation_service_pb2.RecalculateAnomalyFeedbacksRequest.Details(
                    currency_code=response_0.breakdown.currency_code
                )
            )
            method_name_1 = 'RecalculateAnomalyFeedbacks'
            response_1 = await getattr(
                deps.clients.anomalies_anomaly_feedback_calculation,
                method_name_1
            )(outgoing_1, timeout=deps.settings.timeout)
            fields_2: dict[str, Any] = {
                'context': request.context,
                'pipeline': {
                    'audit': {'created_at': request.anomaly.audit.created_at},
                    'organizer': {'email': response_0.dataset_version.subject.email},
                    'participants': [
                        {'contact': {'email': request.details.approver.email, 'phone': request.anomaly.requester.phone}}
                    ]
                }
            }
            outgoing_2 = pipelines_v1_pipeline_service_pb2.UpdatePipelineRequest(**fields_2)
            response_2 = await deps.clients.pipelines_pipeline.UpdatePipeline(outgoing_2, timeout=deps.settings.timeout)
            outgoing_3 = anomalies_v1_anomaly_feedback_validation_service_pb2.NormalizeAnomalyFeedbackRequest(
                anomaly_feedback=anomalies_v1_anomalies_pb2.AnomalyFeedback(
                    subject=datasets_v1_refs_pb2.DatasetRef(
                        dataset_id=response_1.anomaly_feedback.subject.dataset_id,
                        display_name=response_2.pipeline.organizer.display_name
                    )
                ),
                context=request.context,
                details=anomalies_v1_anomaly_feedback_validation_service_pb2.NormalizeAnomalyFeedbackRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(email=request.anomaly.requester.email)
                )
            )
            document_3 = MessageToDict(outgoing_3, preserving_proto_field_name=True)
            outgoing_3 = ParseDict(
                document_3,
                anomalies_v1_anomaly_feedback_validation_service_pb2.NormalizeAnomalyFeedbackRequest()
            )
            response_3 = await deps.clients.anomalies_anomaly_feedback_validation.NormalizeAnomalyFeedback(
                outgoing_3,
                timeout=deps.settings.timeout
            )
            returned_1_0 = response_1.result.message
            if returned_1_0:
                response.result.message = returned_1_0
            returned_2_0 = response_2.pipeline.audit.created_at
            if returned_2_0.ListFields():
                response.anomaly.audit.created_at.MergeFrom(returned_2_0)
            returned_2_1 = response_2.result.message
            if returned_2_1:
                response.outcome.message = returned_2_1
            returned_3_0 = response_3.result.message
            if returned_3_0:
                response.result.message = returned_3_0
            echoed_0 = request.anomaly_id
            response.anomaly.anomaly_id = echoed_0
            echoed_1 = request.anomaly.status
            response.anomaly.status = echoed_1
            return response

    async def handle_escalate_anomaly(
        self,
        request: anomalies_v1_anomaly_approval_service_pb2.EscalateAnomalyRequest
    ) -> anomalies_v1_anomaly_approval_service_pb2.EscalateAnomalyResponse:
        """Escalates an anomaly."""
        deps = self.deps
        response = anomalies_v1_anomaly_approval_service_pb2.EscalateAnomalyResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('EscalateAnomaly', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'EscalateAnomaly', {'reason': request.reason})
            await deps.repository.save_anomaly(request.context.tenant_id, request.anomaly)
            response_0 = anomalies_v1_detector_query_service_pb2.BrowseDetectorsResponse()
            response_1 = payroll_v1_pay_run_calculation_service_pb2.EstimatePayRunResponse()
            outgoing_0 = anomalies_v1_detector_query_service_pb2.BrowseDetectorsRequest(
                context=request.context,
                filter=anomalies_v1_detector_query_service_pb2.BrowseDetectorsRequest.Filter(
                    created_after=request.anomaly.audit.created_at,
                    labels=dict(request.annotations),
                    owner_id=request.anomaly.assignee.user_id
                )
            )
            outgoing_1 = payroll_v1_pay_run_calculation_service_pb2.EstimatePayRunRequest(
                context=request.context,
                pay_run=payroll_v1_payroll_pb2.PayRun(
                    audit=common_v1_audit_pb2.AuditInfo(updated_at=request.anomaly.audit.updated_at),
                    counterparty=payroll_v1_refs_pb2.DeductionRef(
                        display_name=request.details.approver.display_name,
                        version=request.anomaly.customer.version
                    )
                )
            )
            response_0, response_1 = await asyncio.gather(
                deps.clients.anomalies_detector_query.BrowseDetectors(outgoing_0, timeout=deps.settings.timeout),
                deps.clients.payroll_pay_run_calculation.EstimatePayRun(outgoing_1, timeout=deps.settings.timeout),
            )
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.result.message = returned_0_0
            returned_1_0 = response_1.pay_run.audit.updated_by
            if returned_1_0:
                response.anomaly.audit.updated_by = returned_1_0
            echoed_0 = request.anomaly_id
            response.anomaly.anomaly_id = echoed_0
            echoed_1 = request.anomaly.assignee
            response.anomaly.assignee.CopyFrom(echoed_1)
            return response

    async def handle_get_anomaly_approval_status(
        self,
        request: anomalies_v1_anomaly_approval_service_pb2.GetAnomalyApprovalStatusRequest
    ) -> anomalies_v1_anomaly_approval_service_pb2.GetAnomalyApprovalStatusResponse:
        """Returns an anomaly."""
        deps = self.deps
        response = anomalies_v1_anomaly_approval_service_pb2.GetAnomalyApprovalStatusResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('GetAnomalyApprovalStatus', extra={'fields': {'domain': 'anomalies'}})
            await deps.repository.audit(request.context.tenant_id, 'GetAnomalyApprovalStatus', {})
            response_0 = anomalies_v1_anomaly_query_service_pb2.PeekAnomalyResponse()
            outgoing_0 = anomalies_v1_anomaly_query_service_pb2.PeekAnomalyRequest(
                anomaly_id=request.anomaly_id,
                context=request.context
            )
            response_0 = await deps.clients.anomalies_anomaly_query.PeekAnomaly(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.anomaly.audit.updated_by
            if returned_0_0:
                response.anomaly.audit.updated_by = returned_0_0
            echoed_0 = request.anomaly_id
            response.anomaly.anomaly_id = echoed_0
            return response

    async def handle_list_pending_anomalies(
        self,
        request: anomalies_v1_anomaly_approval_service_pb2.ListPendingAnomaliesRequest
    ) -> anomalies_v1_anomaly_approval_service_pb2.ListPendingAnomaliesResponse:
        """Lists anomalies a page at a time."""
        deps = self.deps
        response = anomalies_v1_anomaly_approval_service_pb2.ListPendingAnomaliesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ListPendingAnomalies', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ListPendingAnomalies',
                {'order_by': request.order_by}
            )
            response_0 = datasets_v1_dataset_version_validation_service_pb2.ExplainDatasetVersionDecisionResponse()
            response_1 = lineage_v1_impact_sync_service_pb2.ResolveImpactConflictResponse()
            outgoing_0 = datasets_v1_dataset_version_validation_service_pb2.ExplainDatasetVersionDecisionRequest(
                context=request.context,
                dataset_version=datasets_v1_datasets_pb2.DatasetVersion(
                    subject=customers_v1_refs_pb2.CustomerRef(email=request.context.actor.email)
                )
            )
            response_0 = await deps.clients.datasets_dataset_version_validation.ExplainDatasetVersionDecision(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            command_1 = AnomalyApprovalListPendingAnomalies1Command(
                context=request.context,
                impact_customer_customer_id=response_0.dataset_version.subject.customer_id,
                impact_customer_email=response_0.dataset_version.subject.email
            )
            outgoing_1 = to_anomaly_approval_list_pending_anomalies1_command(command_1)
            response_1 = await deps.clients.lineage_impact_sync.ResolveImpactConflict(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.dataset_version.subject.email
            returned_0_0_part_0 = response.anomalies.add()
            if returned_0_0:
                returned_0_0_part_0.assignee.email = returned_0_0
            returned_1_0 = response_1.result.details
            response.result.details.update(returned_1_0)
            returned_1_1 = response_1.impact.customer.display_name
            returned_1_1_part_0 = response.anomalies.add()
            if returned_1_1:
                returned_1_1_part_0.assignee.display_name = returned_1_1
            return response

    async def handle_recall_anomaly(
        self,
        request: anomalies_v1_anomaly_approval_service_pb2.RecallAnomalyRequest
    ) -> anomalies_v1_anomaly_approval_service_pb2.RecallAnomalyResponse:
        """Recalls an anomaly."""
        deps = self.deps
        response = anomalies_v1_anomaly_approval_service_pb2.RecallAnomalyResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('RecallAnomaly', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'RecallAnomaly', {'reason': request.reason})
            await deps.repository.save_anomaly(request.context.tenant_id, request.anomaly)
            response_0 = pipelines_v1_pipeline_service_pb2.UpdatePipelineResponse()
            command_0 = AnomalyApprovalRecallAnomaly0Command.model_validate(
                {
                    'context': request.context,
                    'pipeline_participants_contact_email': request.anomaly.requester.email,
                    'pipeline_participants_contact_preferred_channel': request.anomaly.requester.preferred_channel,
                    'pipeline_audit_created_by': request.anomaly.audit.created_by,
                    'pipeline_organizer_display_name': request.anomaly.customer.display_name
                }
            )
            outgoing_0 = to_anomaly_approval_recall_anomaly0_command(command_0)
            response_0 = await deps.clients.pipelines_pipeline.UpdatePipeline(outgoing_0, timeout=deps.settings.timeout)
            returned_0_0 = response_0.result.status
            if returned_0_0:
                response.outcome.status = returned_0_0
            returned_0_1 = response_0.result.message
            if returned_0_1:
                response.outcome.message = returned_0_1
            echoed_0 = request.anomaly_id
            response.anomaly.anomaly_id = echoed_0
            echoed_1 = request.anomaly.custom_fields
            response.anomaly.custom_fields.update(echoed_1)
            return response

    async def handle_reject_anomaly(
        self,
        request: anomalies_v1_anomaly_approval_service_pb2.RejectAnomalyRequest
    ) -> anomalies_v1_anomaly_approval_service_pb2.RejectAnomalyResponse:
        """Rejects an anomaly."""
        deps = self.deps
        response = anomalies_v1_anomaly_approval_service_pb2.RejectAnomalyResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('RejectAnomaly', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'RejectAnomaly', {'reason': request.reason})
            await deps.repository.save_anomaly(request.context.tenant_id, request.anomaly)
            response_0 = customers_v1_customer_query_service_pb2.SuggestCustomersResponse()
            response_1 = datasets_v1_dataset_validation_service_pb2.ValidateDatasetResponse()
            outgoing_0 = customers_v1_customer_query_service_pb2.SuggestCustomersRequest(
                context=request.context,
                filter=customers_v1_customer_query_service_pb2.SuggestCustomersRequest.Filter(
                    created_after=request.anomaly.sla.due_at
                )
            )
            send_0 = partial(deps.clients.customers_customer_query.SuggestCustomers, timeout=deps.settings.timeout)
            response_0 = await send_0(outgoing_0)
            callbacks_1: list[
                Callable[[], Awaitable[datasets_v1_dataset_validation_service_pb2.ValidateDatasetResponse]]
            ] = []
            for item_1 in request.anomaly.comments:
                outgoing_1 = datasets_v1_dataset_validation_service_pb2.ValidateDatasetRequest(
                    context=request.context,
                    details=datasets_v1_dataset_validation_service_pb2.ValidateDatasetRequest.Details(
                        contact=common_v1_contact_pb2.ContactInfo(email=item_1.author_email)
                    )
                )
                async def send_1(
                    payload: datasets_v1_dataset_validation_service_pb2.ValidateDatasetRequest = outgoing_1
                ) -> datasets_v1_dataset_validation_service_pb2.ValidateDatasetResponse:
                    return await deps.clients.datasets_dataset_validation.ValidateDataset(
                        payload,
                        timeout=deps.settings.timeout
                    )
                callbacks_1.append(send_1)
            for callback_1 in callbacks_1:
                response_1 = await callback_1()
            returned_0_0 = response_0.result.status
            if returned_0_0:
                response.outcome.status = returned_0_0
            returned_0_1 = response_0.result.correlation_id
            if returned_0_1:
                response.result.correlation_id = returned_0_1
            echoed_0 = request.anomaly_id
            response.anomaly.anomaly_id = echoed_0
            echoed_1 = request.anomaly.subject
            response.anomaly.subject = echoed_1
            return response

    async def handle_submit_anomaly(
        self,
        request: anomalies_v1_anomaly_approval_service_pb2.SubmitAnomalyRequest
    ) -> anomalies_v1_anomaly_approval_service_pb2.SubmitAnomalyResponse:
        """Submits an anomaly."""
        deps = self.deps
        response = anomalies_v1_anomaly_approval_service_pb2.SubmitAnomalyResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SubmitAnomaly', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'SubmitAnomaly', {'reason': request.reason})
            await deps.repository.save_anomaly(request.context.tenant_id, request.anomaly)
            response_0 = datasets_v1_dataset_version_calculation_service_pb2.CompareDatasetVersionOptionsResponse()
            outgoing_0 = datasets_v1_dataset_version_calculation_service_pb2.CompareDatasetVersionOptionsRequest()
            outgoing_0.context.CopyFrom(request.context)
            outgoing_0.dataset_version.subject.display_name = request.anomaly.customer.display_name
            outgoing_0.context.tenant_id = tenant_id.get()
            response_0 = await deps.clients.datasets_dataset_version_calculation.CompareDatasetVersionOptions(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.status
            if returned_0_0:
                response.result.status = returned_0_0
            returned_0_1 = response_0.result.status
            if returned_0_1:
                response.outcome.status = returned_0_1
            echoed_0 = request.anomaly_id
            response.anomaly.anomaly_id = echoed_0
            echoed_1 = request.anomaly.priority
            response.anomaly.priority = echoed_1
            return response
