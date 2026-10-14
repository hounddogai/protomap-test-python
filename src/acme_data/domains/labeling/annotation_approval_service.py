"""Routes annotations through approval, with escalation and delegation."""

from __future__ import annotations

from collections.abc import AsyncIterator
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
import grpc

from acme.anomalies.v1 import anomalies_pb2 as anomalies_v1_anomalies_pb2
from acme.anomalies.v1 import (
    anomaly_feedback_approval_service_pb2 as anomalies_v1_anomaly_feedback_approval_service_pb2,
)
from acme.anomalies.v1 import detector_workflow_service_pb2 as anomalies_v1_detector_workflow_service_pb2
from acme.anomalies.v1 import detector_workflow_service_pb2_grpc as anomalies_v1_detector_workflow_service_pb2_grpc
from acme.authorization.v1 import (
    access_policy_validation_service_pb2 as authorization_v1_access_policy_validation_service_pb2,
)
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.datasets.v1 import refs_pb2 as datasets_v1_refs_pb2
from acme.employees.v1 import refs_pb2 as employees_v1_refs_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.labeling.v1 import annotation_approval_service_pb2 as labeling_v1_annotation_approval_service_pb2
from acme.labeling.v1 import annotation_approval_service_pb2_grpc as labeling_v1_annotation_approval_service_pb2_grpc
from acme.labeling.v1 import annotation_validation_service_pb2 as labeling_v1_annotation_validation_service_pb2
from acme.labeling.v1 import label_set_calculation_service_pb2 as labeling_v1_label_set_calculation_service_pb2
from acme.labeling.v1 import label_set_reporting_service_pb2 as labeling_v1_label_set_reporting_service_pb2
from acme.labeling.v1 import labeling_pb2 as labeling_v1_labeling_pb2
from acme.labeling.v1 import labeling_task_approval_service_pb2 as labeling_v1_labeling_task_approval_service_pb2
from acme.labeling.v1 import labeling_task_lifecycle_service_pb2 as labeling_v1_labeling_task_lifecycle_service_pb2
from acme.labeling.v1 import labeling_task_validation_service_pb2 as labeling_v1_labeling_task_validation_service_pb2
from acme.labeling.v1 import refs_pb2 as labeling_v1_refs_pb2
from acme.lineage.v1 import impact_reporting_service_pb2 as lineage_v1_impact_reporting_service_pb2
from acme.lineage.v1 import lineage_edge_approval_service_pb2 as lineage_v1_lineage_edge_approval_service_pb2
from acme.metrics.v1 import metric_series_export_service_pb2 as metrics_v1_metric_series_export_service_pb2
from acme.modelregistry.v1 import deployment_sync_service_pb2 as modelregistry_v1_deployment_sync_service_pb2
from acme.modelregistry.v1 import deployment_workflow_service_pb2 as modelregistry_v1_deployment_workflow_service_pb2
from acme.scheduling.v1 import scheduling_pb2 as scheduling_v1_scheduling_pb2
from acme.scheduling.v1 import shift_service_pb2 as scheduling_v1_shift_service_pb2
from acme.search.v1 import search_index_service_pb2 as search_v1_search_index_service_pb2
from acme.ticketing.v1 import ticket_service_pb2 as ticketing_v1_ticket_service_pb2
from acme.timekeeping.v1 import timekeeping_pb2 as timekeeping_v1_timekeeping_pb2
from acme.timekeeping.v1 import timesheet_service_pb2 as timekeeping_v1_timesheet_service_pb2

from acme_data.domains.labeling.adapters import AnnotationApprovalRecallAnnotation2Adapter
from acme_data.domains.labeling.adapters import AnnotationApprovalRecallAnnotation2Port
from acme_data.domains.labeling.adapters import AnnotationApprovalRejectAnnotation0Adapter
from acme_data.domains.labeling.dependencies import Dependencies
from acme_data.domains.labeling.models import AnnotationApprovalEscalateAnnotation2Command
from acme_data.domains.labeling.models import to_annotation_approval_escalate_annotation2_command
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import run_steps
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class AnnotationApprovalServicer(labeling_v1_annotation_approval_service_pb2_grpc.AnnotationApprovalServiceServicer):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    async def ApproveAnnotation(
        self, request: labeling_v1_annotation_approval_service_pb2.ApproveAnnotationRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_annotation_approval_service_pb2.ApproveAnnotationResponse:
        """Approves an annotation."""
        return await self.handle_approve_annotation(request)

    @rpc_errors
    async def CommentAnnotationApproval(
        self, request: labeling_v1_annotation_approval_service_pb2.CommentAnnotationApprovalRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_annotation_approval_service_pb2.CommentAnnotationApprovalResponse:
        """Comments an annotation."""
        return await self.handle_comment_annotation_approval(request)

    @rpc_errors
    async def EscalateAnnotation(
        self, request: labeling_v1_annotation_approval_service_pb2.EscalateAnnotationRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_annotation_approval_service_pb2.EscalateAnnotationResponse:
        """Escalates an annotation."""
        return await self.handle_escalate_annotation(request)

    @rpc_errors
    @retry_transient
    async def GetAnnotationApprovalStatus(
        self, request: labeling_v1_annotation_approval_service_pb2.GetAnnotationApprovalStatusRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_annotation_approval_service_pb2.GetAnnotationApprovalStatusResponse:
        """Returns an annotation."""
        return await self.handle_get_annotation_approval_status(request)

    @rpc_errors
    @retry_transient
    async def ListPendingAnnotations(
        self, request: labeling_v1_annotation_approval_service_pb2.ListPendingAnnotationsRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_annotation_approval_service_pb2.ListPendingAnnotationsResponse:
        """Lists annotations a page at a time."""
        return await self.handle_list_pending_annotations(request)

    @rpc_errors
    async def RecallAnnotation(
        self, request: labeling_v1_annotation_approval_service_pb2.RecallAnnotationRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_annotation_approval_service_pb2.RecallAnnotationResponse:
        """Recalls an annotation."""
        return await self.handle_recall_annotation(request)

    @rpc_errors
    async def RejectAnnotation(
        self, request: labeling_v1_annotation_approval_service_pb2.RejectAnnotationRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_annotation_approval_service_pb2.RejectAnnotationResponse:
        """Rejects an annotation."""
        return await self.handle_reject_annotation(request)

    @rpc_errors
    async def SubmitAnnotation(
        self, request: labeling_v1_annotation_approval_service_pb2.SubmitAnnotationRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_annotation_approval_service_pb2.SubmitAnnotationResponse:
        """Submits an annotation."""
        return await self.handle_submit_annotation(request)

    async def handle_approve_annotation(
        self,
        request: labeling_v1_annotation_approval_service_pb2.ApproveAnnotationRequest
    ) -> labeling_v1_annotation_approval_service_pb2.ApproveAnnotationResponse:
        """Approves an annotation."""
        deps = self.deps
        response = labeling_v1_annotation_approval_service_pb2.ApproveAnnotationResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ApproveAnnotation', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'ApproveAnnotation', {'reason': request.reason})
            await deps.repository.save_annotation(request.context.tenant_id, request.annotation)
            response_0 = modelregistry_v1_deployment_workflow_service_pb2.StartDeploymentWorkflowResponse()
            response_1 = lineage_v1_lineage_edge_approval_service_pb2.ApproveLineageEdgeResponse()
            fields_0: dict[str, Any] = {
                'context': request.context,
                'deployment': {
                    'organizer': {
                        'display_name': request.details.approver.display_name,
                        'user_id': request.details.approver.user_id
                    },
                    'participants': [{'contact': {'email': request.details.approver.email}}]
                },
                'details': {'notify': {'email': request.details.approver_email}}
            }
            outgoing_0 = modelregistry_v1_deployment_workflow_service_pb2.StartDeploymentWorkflowRequest(**fields_0)
            response_0 = await deps.clients.modelregistry_deployment_workflow.StartDeploymentWorkflow(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = lineage_v1_lineage_edge_approval_service_pb2.ApproveLineageEdgeRequest(
                context=request.context,
                details=lineage_v1_lineage_edge_approval_service_pb2.ApproveLineageEdgeRequest.Details(
                    approver=identity_v1_refs_pb2.UserRef(email=response_0.deployment.organizer.email)
                )
            )
            document_1 = MessageToDict(outgoing_1, preserving_proto_field_name=True)
            outgoing_1 = ParseDict(document_1, lineage_v1_lineage_edge_approval_service_pb2.ApproveLineageEdgeRequest())
            response_1 = await deps.clients.lineage_lineage_edge_approval.ApproveLineageEdge(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.outcome.reference_id
            if returned_0_0:
                response.outcome.reference_id = returned_0_0
            returned_1_0 = response_1.result.details
            response.result.details.update(returned_1_0)
            returned_1_1 = response_1.lineage_edge.source
            if returned_1_1:
                response.annotation.source = returned_1_1
            echoed_0 = request.annotation_id
            response.annotation.annotation_id = echoed_0
            echoed_1 = request.annotation.subject
            response.annotation.subject.CopyFrom(echoed_1)
            return response

    async def handle_comment_annotation_approval(
        self,
        request: labeling_v1_annotation_approval_service_pb2.CommentAnnotationApprovalRequest
    ) -> labeling_v1_annotation_approval_service_pb2.CommentAnnotationApprovalResponse:
        """Comments an annotation."""
        deps = self.deps
        response = labeling_v1_annotation_approval_service_pb2.CommentAnnotationApprovalResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CommentAnnotationApproval', extra={'fields': {'annotation_id': request.annotation.annotation_id}})
            await deps.repository.audit(
                request.context.tenant_id,
                'CommentAnnotationApproval',
                {'annotation_id': request.annotation.annotation_id}
            )
            await deps.repository.save_annotation(request.context.tenant_id, request.annotation)
            response_0 = labeling_v1_labeling_task_lifecycle_service_pb2.ReinstateLabelingTaskResponse()
            response_1 = labeling_v1_label_set_reporting_service_pb2.GenerateLabelSetReportResponse()
            response_2 = labeling_v1_label_set_calculation_service_pb2.RecalculateLabelSetsResponse()
            outgoing_0 = labeling_v1_labeling_task_lifecycle_service_pb2.ReinstateLabelingTaskRequest(
                context=request.context,
                details=labeling_v1_labeling_task_lifecycle_service_pb2.ReinstateLabelingTaskRequest.Details(
                    new_owner=identity_v1_refs_pb2.UserRef(
                        display_name=request.details.approver.display_name,
                        email=request.details.approver.email
                    ),
                    notify_contact=common_v1_contact_pb2.ContactInfo(email=request.details.approver_email)
                ),
                labeling_task_id=request.annotation.subject.labeling_task_id
            )
            document_0 = MessageToJson(outgoing_0, preserving_proto_field_name=True)
            outgoing_0 = Parse(
                document_0,
                labeling_v1_labeling_task_lifecycle_service_pb2.ReinstateLabelingTaskRequest()
            )
            response_0 = await deps.clients.labeling_labeling_task_lifecycle.ReinstateLabelingTask(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = labeling_v1_label_set_reporting_service_pb2.GenerateLabelSetReportRequest()
            outgoing_1.context.CopyFrom(request.context)
            outgoing_1.label_set_id = response_0.labeling_task.customer.label_set_id
            outgoing_1.annotations.update(dict(request.annotations))
            outgoing_1.reason = request.reason
            outgoing_1.details.filters.update(dict(response_0.labeling_task.custom_fields))
            merged_1 = labeling_v1_label_set_reporting_service_pb2.GenerateLabelSetReportRequest()
            merged_1.MergeFrom(outgoing_1)
            outgoing_1.CopyFrom(merged_1)
            response_1 = await deps.clients.labeling_label_set_reporting.GenerateLabelSetReport(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = labeling_v1_label_set_calculation_service_pb2.RecalculateLabelSetsRequest(
                context=request.context,
                label_set=labeling_v1_labeling_pb2.LabelSet(
                    children=[
                        labeling_v1_labeling_pb2.LabelSet(
                            children=[
                                labeling_v1_labeling_pb2.LabelSet(
                                    audit=common_v1_audit_pb2.AuditInfo(etag=response_0.labeling_task.audit.etag),
                                    manager=identity_v1_refs_pb2.UserRef(
                                        display_name=response_0.labeling_task.assignee.display_name,
                                        user_id=request.details.approver.user_id
                                    )
                                )
                            ],
                            manager=identity_v1_refs_pb2.UserRef(email=request.details.approver.email)
                        )
                    ]
                )
            )
            envelope_2 = AnyMessage()
            envelope_2.Pack(outgoing_2)
            outgoing_2 = labeling_v1_label_set_calculation_service_pb2.RecalculateLabelSetsRequest()
            if not envelope_2.Unpack(outgoing_2):
                raise ValueError("partner envelope contains the wrong request type")
            response_2 = await deps.clients.labeling_label_set_calculation.RecalculateLabelSets(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.correlation_id
            if returned_0_0:
                response.result.correlation_id = returned_0_0
            returned_0_1 = response_0.outcome.status
            if returned_0_1:
                response.outcome.status = returned_0_1
            returned_1_0 = response_1.result.correlation_id
            if returned_1_0:
                response.annotation.correlation_id = returned_1_0
            returned_2_0 = response_2.label_set.attributes
            response.annotation.attributes.update(returned_2_0)
            returned_2_1 = response_2.result.message
            if returned_2_1:
                response.result.message = returned_2_1
            echoed_0 = request.annotation_id
            response.annotation.annotation_id = echoed_0
            echoed_1 = request.annotation.occurred_at
            response.annotation.occurred_at.CopyFrom(echoed_1)
            return response

    async def handle_escalate_annotation(
        self,
        request: labeling_v1_annotation_approval_service_pb2.EscalateAnnotationRequest
    ) -> labeling_v1_annotation_approval_service_pb2.EscalateAnnotationResponse:
        """Escalates an annotation."""
        deps = self.deps
        response = labeling_v1_annotation_approval_service_pb2.EscalateAnnotationResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('EscalateAnnotation', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'EscalateAnnotation', {'reason': request.reason})
            await deps.repository.save_annotation(request.context.tenant_id, request.annotation)
            response_0 = anomalies_v1_detector_workflow_service_pb2.AdvanceDetectorWorkflowResponse()
            response_1 = scheduling_v1_shift_service_pb2.UpdateShiftResponse()
            response_2 = metrics_v1_metric_series_export_service_pb2.ShareMetricSeriesExportResponse()
            outgoing_0 = anomalies_v1_detector_workflow_service_pb2.AdvanceDetectorWorkflowRequest(
                context=request.context,
                detector=anomalies_v1_anomalies_pb2.Detector(
                    owner=identity_v1_refs_pb2.UserRef(
                        display_name=request.annotation.subject.display_name,
                        email=request.details.approver.email,
                        user_id=request.details.approver.user_id
                    ),
                    priority=request.annotation.subject.priority
                )
            )
            registered_0 = cast(
                anomalies_v1_detector_workflow_service_pb2_grpc.DetectorWorkflowServiceStub,
                deps.clients.registry['acme.anomalies.v1.DetectorWorkflowService']
            )
            response_0 = await registered_0.AdvanceDetectorWorkflow(outgoing_0, timeout=deps.settings.timeout)
            async for item_1 in async_messages(request.annotation.measurements):
                outgoing_1 = scheduling_v1_shift_service_pb2.UpdateShiftRequest(
                    context=request.context,
                    shift=scheduling_v1_scheduling_pb2.Shift(
                        audit=common_v1_audit_pb2.AuditInfo(
                            created_at=response_0.detector.audit.created_at,
                            updated_at=item_1.observed_at
                        ),
                        organizer=identity_v1_refs_pb2.UserRef(
                            display_name=request.details.approver.display_name,
                            user_id=request.details.approver.user_id
                        )
                    )
                )
                response_1 = await deps.clients.scheduling_shift.UpdateShift(outgoing_1, timeout=deps.settings.timeout)
            command_2 = AnnotationApprovalEscalateAnnotation2Command.model_validate(
                {
                    'context': request.context,
                    'details_recipient_email': response_1.shift.organizer.email,
                    'annotations': dict(request.annotations),
                    'reason': response_0.detector.block.reason
                }
            )
            outgoing_2 = to_annotation_approval_escalate_annotation2_command(command_2)
            response_2 = await deps.clients.metrics_metric_series_export.ShareMetricSeriesExport(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_0)
            returned_2_0 = response_2.result.correlation_id
            if returned_2_0:
                response.annotation.correlation_id = returned_2_0
            returned_2_1 = response_2.metric_series.dimensions.unit
            returned_2_1_part_1 = response.annotation.measurements.add()
            if returned_2_1:
                returned_2_1_part_1.unit = returned_2_1
            echoed_0 = request.annotation_id
            response.annotation.annotation_id = echoed_0
            echoed_1 = request.annotation.subject
            response.annotation.subject.CopyFrom(echoed_1)
            return response

    async def handle_get_annotation_approval_status(
        self,
        request: labeling_v1_annotation_approval_service_pb2.GetAnnotationApprovalStatusRequest
    ) -> labeling_v1_annotation_approval_service_pb2.GetAnnotationApprovalStatusResponse:
        """Returns an annotation."""
        deps = self.deps
        response = labeling_v1_annotation_approval_service_pb2.GetAnnotationApprovalStatusResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('GetAnnotationApprovalStatus', extra={'fields': {'domain': 'labeling'}})
            await deps.repository.audit(request.context.tenant_id, 'GetAnnotationApprovalStatus', {})
            response_0 = ticketing_v1_ticket_service_pb2.ListTicketsResponse()
            outgoing_0 = ticketing_v1_ticket_service_pb2.ListTicketsRequest(
                context=request.context,
                filter=ticketing_v1_ticket_service_pb2.ListTicketsRequest.Filter(
                    labels=dict(request.context.baggage),
                    owner_id=request.annotation_id
                )
            )
            response_0 = await deps.clients.ticketing_ticket.ListTickets(outgoing_0, timeout=deps.settings.timeout)
            returned_0_0 = response_0.result.correlation_id
            if returned_0_0:
                response.annotation.correlation_id = returned_0_0
            returned_0_1 = response_0.result.details
            response.result.details.update(returned_0_1)
            echoed_0 = request.annotation_id
            response.annotation.annotation_id = echoed_0
            return response

    async def handle_list_pending_annotations(
        self,
        request: labeling_v1_annotation_approval_service_pb2.ListPendingAnnotationsRequest
    ) -> labeling_v1_annotation_approval_service_pb2.ListPendingAnnotationsResponse:
        """Lists annotations a page at a time."""
        deps = self.deps
        response = labeling_v1_annotation_approval_service_pb2.ListPendingAnnotationsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ListPendingAnnotations', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ListPendingAnnotations',
                {'order_by': request.order_by}
            )
            return response

    async def handle_recall_annotation(
        self,
        request: labeling_v1_annotation_approval_service_pb2.RecallAnnotationRequest
    ) -> labeling_v1_annotation_approval_service_pb2.RecallAnnotationResponse:
        """Recalls an annotation."""
        deps = self.deps
        response = labeling_v1_annotation_approval_service_pb2.RecallAnnotationResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('RecallAnnotation', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'RecallAnnotation', {'reason': request.reason})
            await deps.repository.save_annotation(request.context.tenant_id, request.annotation)
            response_0 = timekeeping_v1_timesheet_service_pb2.CreateTimesheetResponse()
            response_1 = search_v1_search_index_service_pb2.BatchGetSearchIndexesResponse()
            response_2 = labeling_v1_labeling_task_validation_service_pb2.ValidateLabelingTaskResponse()
            response_3 = labeling_v1_labeling_task_lifecycle_service_pb2.ActivateLabelingTaskResponse()
            outgoing_0 = timekeeping_v1_timesheet_service_pb2.CreateTimesheetRequest(
                context=request.context,
                timesheet=timekeeping_v1_timekeeping_pb2.Timesheet(
                    audit=common_v1_audit_pb2.AuditInfo(updated_at=request.details.effective_at),
                    counterparty=employees_v1_refs_pb2.EmployeeRef(
                        display_name=request.annotation.subject.display_name,
                        email=request.details.approver.email
                    ),
                    lines=[timekeeping_v1_timekeeping_pb2.TimesheetLine(attributes=dict(request.annotation.attributes))]
                )
            )
            outgoing_1 = search_v1_search_index_service_pb2.BatchGetSearchIndexesRequest(context=request.context)
            response_0, response_1 = await asyncio.gather(
                deps.clients.timekeeping_timesheet.CreateTimesheet(outgoing_0, timeout=deps.settings.timeout),
                deps.clients.search_search_index.BatchGetSearchIndexes(outgoing_1, timeout=deps.settings.timeout),
            )
            outgoing_2 = labeling_v1_labeling_task_validation_service_pb2.ValidateLabelingTaskRequest(
                context=request.context,
                labeling_task=labeling_v1_labeling_pb2.LabelingTask(
                    assignee=identity_v1_refs_pb2.UserRef(display_name=request.details.approver.display_name),
                    audit=common_v1_audit_pb2.AuditInfo(etag=response_0.timesheet.audit.etag)
                )
            )
            port_2: AnnotationApprovalRecallAnnotation2Port = AnnotationApprovalRecallAnnotation2Adapter(
                deps.clients.labeling_labeling_task_validation,
                deps.settings.timeout
            )
            response_2 = await port_2.execute(outgoing_2)
            outgoing_3 = labeling_v1_labeling_task_lifecycle_service_pb2.ActivateLabelingTaskRequest(
                context=request.context,
                details=labeling_v1_labeling_task_lifecycle_service_pb2.ActivateLabelingTaskRequest.Details(
                    new_owner=identity_v1_refs_pb2.UserRef(display_name=response_0.timesheet.counterparty.display_name),
                    notify_contact=common_v1_contact_pb2.ContactInfo(
                        name=response_2.labeling_task.requester.name,
                        preferred_channel=response_2.labeling_task.requester.preferred_channel
                    )
                ),
                labeling_task_id=request.annotation.subject.labeling_task_id
            )
            steps_3 = [
                partial(
                    deps.clients.labeling_labeling_task_lifecycle.ActivateLabelingTask,
                    outgoing_3,
                    timeout=deps.settings.timeout
                )
            ]
            results_3 = await run_steps(steps_3)
            response_3 = results_3[-1]
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.result.message = returned_0_0
            returned_0_1 = response_0.result.details
            response.result.details.update(returned_0_1)
            returned_1_0 = response_1.result.details
            response.result.details.update(returned_1_0)
            returned_1_1 = response_1.result.message
            if returned_1_1:
                response.outcome.message = returned_1_1
            returned_2_0 = response_2.outcome.status
            if returned_2_0:
                response.outcome.status = returned_2_0
            returned_3_0 = response_3.result.status
            if returned_3_0:
                response.result.status = returned_3_0
            returned_3_1 = response_3.result.message
            if returned_3_1:
                response.outcome.message = returned_3_1
            echoed_0 = request.annotation_id
            response.annotation.annotation_id = echoed_0
            echoed_1 = request.annotation.source
            response.annotation.source = echoed_1
            return response

    async def handle_reject_annotation(
        self,
        request: labeling_v1_annotation_approval_service_pb2.RejectAnnotationRequest
    ) -> labeling_v1_annotation_approval_service_pb2.RejectAnnotationResponse:
        """Rejects an annotation."""
        deps = self.deps
        response = labeling_v1_annotation_approval_service_pb2.RejectAnnotationResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('RejectAnnotation', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'RejectAnnotation', {'reason': request.reason})
            await deps.repository.save_annotation(request.context.tenant_id, request.annotation)
            response_0 = lineage_v1_impact_reporting_service_pb2.ListImpactReportsResponse()
            response_1 = anomalies_v1_anomaly_feedback_approval_service_pb2.SubmitAnomalyFeedbackResponse()
            outgoing_0 = lineage_v1_impact_reporting_service_pb2.ListImpactReportsRequest(
                context=request.context,
                filter=lineage_v1_impact_reporting_service_pb2.ListImpactReportsRequest.Filter(
                    created_after=request.details.effective_at,
                    labels=dict(request.annotations),
                    owner_id=request.annotation.annotation_id
                )
            )
            response_0 = await AnnotationApprovalRejectAnnotation0Adapter(
                deps.clients.lineage_impact_reporting,
                deps.settings.timeout
            )(outgoing_0)
            outgoing_1 = anomalies_v1_anomaly_feedback_approval_service_pb2.SubmitAnomalyFeedbackRequest(
                anomaly_feedback=anomalies_v1_anomalies_pb2.AnomalyFeedback(
                    subject=datasets_v1_refs_pb2.DatasetRef(display_name=request.details.approver.display_name)
                ),
                context=request.context,
                details=anomalies_v1_anomaly_feedback_approval_service_pb2.SubmitAnomalyFeedbackRequest.Details(
                    approver=identity_v1_refs_pb2.UserRef(user_id=request.details.approver.user_id)
                )
            )
            response_1 = cast(anomalies_v1_anomaly_feedback_approval_service_pb2.SubmitAnomalyFeedbackResponse, await deps.bus.request(
                'acme.labeling.v1.AnnotationApprovalService/RejectAnnotation/1', outgoing_1, deps.settings.timeout,
            ))
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.outcome.message = returned_0_0
            returned_1_0 = response_1.outcome.reference_id
            if returned_1_0:
                response.outcome.reference_id = returned_1_0
            echoed_0 = request.annotation_id
            response.annotation.annotation_id = echoed_0
            echoed_1 = request.annotation.correlation_id
            response.result.correlation_id = echoed_1
            return response

    async def handle_submit_annotation(
        self,
        request: labeling_v1_annotation_approval_service_pb2.SubmitAnnotationRequest
    ) -> labeling_v1_annotation_approval_service_pb2.SubmitAnnotationResponse:
        """Submits an annotation."""
        deps = self.deps
        response = labeling_v1_annotation_approval_service_pb2.SubmitAnnotationResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SubmitAnnotation', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'SubmitAnnotation', {'reason': request.reason})
            await deps.repository.save_annotation(request.context.tenant_id, request.annotation)
            response_0 = labeling_v1_labeling_task_approval_service_pb2.EscalateLabelingTaskResponse()
            response_1 = modelregistry_v1_deployment_sync_service_pb2.ListDeploymentConflictsResponse()
            response_2 = authorization_v1_access_policy_validation_service_pb2.ValidateAccessPolicyResponse()
            response_3 = labeling_v1_annotation_validation_service_pb2.NormalizeAnnotationResponse()
            outgoing_0 = labeling_v1_labeling_task_approval_service_pb2.EscalateLabelingTaskRequest(
                context=request.context,
                labeling_task=labeling_v1_labeling_pb2.LabelingTask(
                    assignee=identity_v1_refs_pb2.UserRef(display_name=request.details.approver.display_name),
                    requester=common_v1_contact_pb2.ContactInfo(email=request.details.approver.email)
                )
            )
            response_0 = await deps.clients.labeling_labeling_task_approval.EscalateLabelingTask(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = modelregistry_v1_deployment_sync_service_pb2.ListDeploymentConflictsRequest(
                context=request.context,
                filter=modelregistry_v1_deployment_sync_service_pb2.ListDeploymentConflictsRequest.Filter(
                    created_after=response_0.labeling_task.audit.updated_at,
                    labels=dict(response_0.labeling_task.custom_fields),
                    owner_id=response_0.labeling_task.sla.policy_id
                )
            )
            method_name_1 = 'ListDeploymentConflicts'
            response_1 = await getattr(
                deps.clients.modelregistry_deployment_sync,
                method_name_1
            )(outgoing_1, timeout=deps.settings.timeout)
            fields_2: dict[str, Any] = {
                'access_policy': {
                    'audit': {'created_at': response_0.labeling_task.audit.created_at},
                    'owner': {'display_name': request.annotation.subject.display_name}
                },
                'context': request.context
            }
            outgoing_2 = authorization_v1_access_policy_validation_service_pb2.ValidateAccessPolicyRequest(**fields_2)
            response_2 = await deps.clients.authorization_access_policy_validation.ValidateAccessPolicy(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            outgoing_3 = labeling_v1_annotation_validation_service_pb2.NormalizeAnnotationRequest(
                annotation=labeling_v1_labeling_pb2.Annotation(
                    subject=labeling_v1_refs_pb2.LabelingTaskRef(
                        display_name=request.annotation.subject.display_name,
                        labeling_task_id=request.annotation.subject.labeling_task_id
                    )
                ),
                context=request.context,
                details=labeling_v1_annotation_validation_service_pb2.NormalizeAnnotationRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(email=request.details.approver.email)
                )
            )
            document_3 = MessageToDict(outgoing_3, preserving_proto_field_name=True)
            outgoing_3 = ParseDict(
                document_3,
                labeling_v1_annotation_validation_service_pb2.NormalizeAnnotationRequest()
            )
            response_3 = await deps.clients.labeling_annotation_validation.NormalizeAnnotation(
                outgoing_3,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_0)
            returned_0_1 = response_0.result.correlation_id
            if returned_0_1:
                response.result.correlation_id = returned_0_1
            returned_1_0 = response_1.result.correlation_id
            if returned_1_0:
                response.result.correlation_id = returned_1_0
            returned_2_0 = response_2.outcome.message
            if returned_2_0:
                response.result.message = returned_2_0
            returned_2_1 = response_2.outcome.message
            if returned_2_1:
                response.outcome.message = returned_2_1
            returned_3_0 = response_3.annotation.subject
            if returned_3_0.ListFields():
                response.annotation.subject.MergeFrom(returned_3_0)
            returned_3_1 = response_3.outcome.status
            if returned_3_1:
                response.outcome.status = returned_3_1
            echoed_0 = request.annotation_id
            response.annotation.annotation_id = echoed_0
            echoed_1 = request.annotation.source
            response.annotation.source = echoed_1
            return response
