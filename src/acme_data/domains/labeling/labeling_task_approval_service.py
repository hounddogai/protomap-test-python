"""Routes labeling tasks through approval, with escalation and delegation."""

from __future__ import annotations

from collections.abc import AsyncIterator
from collections.abc import Awaitable
from collections.abc import Callable
from dataclasses import dataclass
from functools import partial
from typing import Any
from typing import cast
import asyncio
import logging

import grpc

from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.documents.v1 import document_validation_service_pb2 as documents_v1_document_validation_service_pb2
from acme.documents.v1 import documents_pb2 as documents_v1_documents_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.labeling.v1 import annotation_validation_service_pb2 as labeling_v1_annotation_validation_service_pb2
from acme.labeling.v1 import label_set_calculation_service_pb2 as labeling_v1_label_set_calculation_service_pb2
from acme.labeling.v1 import label_set_lifecycle_service_pb2 as labeling_v1_label_set_lifecycle_service_pb2
from acme.labeling.v1 import label_set_reporting_service_pb2 as labeling_v1_label_set_reporting_service_pb2
from acme.labeling.v1 import labeling_pb2 as labeling_v1_labeling_pb2
from acme.labeling.v1 import labeling_task_approval_service_pb2 as labeling_v1_labeling_task_approval_service_pb2
from acme.labeling.v1 import (
    labeling_task_approval_service_pb2_grpc as labeling_v1_labeling_task_approval_service_pb2_grpc,
)
from acme.labeling.v1 import labeling_task_lifecycle_service_pb2 as labeling_v1_labeling_task_lifecycle_service_pb2
from acme.lineage.v1 import impact_approval_service_pb2 as lineage_v1_impact_approval_service_pb2
from acme.lineage.v1 import lineage_edge_workflow_service_pb2 as lineage_v1_lineage_edge_workflow_service_pb2
from acme.lineage.v1 import lineage_pb2 as lineage_v1_lineage_pb2
from acme.lineage.v1 import refs_pb2 as lineage_v1_refs_pb2
from acme.metrics.v1 import dashboard_notification_service_pb2 as metrics_v1_dashboard_notification_service_pb2
from acme.modelregistry.v1 import (
    model_version_workflow_service_pb2 as modelregistry_v1_model_version_workflow_service_pb2,
)
from acme.modelregistry.v1 import modelregistry_pb2 as modelregistry_v1_modelregistry_pb2
from acme.modelregistry.v1 import (
    registered_model_sync_service_pb2 as modelregistry_v1_registered_model_sync_service_pb2,
)
from acme.sponsorships.v1 import sponsor_query_service_pb2 as sponsorships_v1_sponsor_query_service_pb2

from acme_data.domains.labeling import hooks
from acme_data.domains.labeling.adapters import LabelingTaskApprovalRecallLabelingTask1Adapter
from acme_data.domains.labeling.dependencies import Dependencies
from acme_data.domains.labeling.models import LabelingTaskApprovalApproveLabelingTask2Command
from acme_data.domains.labeling.models import LabelingTaskApprovalCommentLabelingTaskApproval0Command
from acme_data.domains.labeling.models import to_labeling_task_approval_approve_labeling_task2_command
from acme_data.domains.labeling.models import to_labeling_task_approval_comment_labeling_task_approval0_command
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import run_steps
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_id
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


@dataclass(slots=True)
class LabelingTaskApprovalServicer(
    labeling_v1_labeling_task_approval_service_pb2_grpc.LabelingTaskApprovalServiceServicer
):
    deps: Dependencies

    @rpc_errors
    async def ApproveLabelingTask(
        self, request: labeling_v1_labeling_task_approval_service_pb2.ApproveLabelingTaskRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_labeling_task_approval_service_pb2.ApproveLabelingTaskResponse:
        """Approves a labeling task."""
        return await self.handle_approve_labeling_task(request)

    @rpc_errors
    async def CommentLabelingTaskApproval(
        self, request: labeling_v1_labeling_task_approval_service_pb2.CommentLabelingTaskApprovalRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_labeling_task_approval_service_pb2.CommentLabelingTaskApprovalResponse:
        """Comments a labeling task."""
        return await self.handle_comment_labeling_task_approval(request)

    @rpc_errors
    async def DelegateLabelingTaskApproval(
        self, request: labeling_v1_labeling_task_approval_service_pb2.DelegateLabelingTaskApprovalRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_labeling_task_approval_service_pb2.DelegateLabelingTaskApprovalResponse:
        """Delegates a labeling task."""
        return await self.handle_delegate_labeling_task_approval(request)

    @rpc_errors
    async def EscalateLabelingTask(
        self, request: labeling_v1_labeling_task_approval_service_pb2.EscalateLabelingTaskRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_labeling_task_approval_service_pb2.EscalateLabelingTaskResponse:
        """Escalates a labeling task."""
        return await self.handle_escalate_labeling_task(request)

    @rpc_errors
    @retry_transient
    async def GetLabelingTaskApprovalStatus(
        self, request: labeling_v1_labeling_task_approval_service_pb2.GetLabelingTaskApprovalStatusRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_labeling_task_approval_service_pb2.GetLabelingTaskApprovalStatusResponse:
        """Returns a labeling task."""
        return await self.handle_get_labeling_task_approval_status(request)

    @rpc_errors
    @retry_transient
    async def ListPendingLabelingTasks(
        self, request: labeling_v1_labeling_task_approval_service_pb2.ListPendingLabelingTasksRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_labeling_task_approval_service_pb2.ListPendingLabelingTasksResponse:
        """Lists labeling tasks a page at a time."""
        return await self.handle_list_pending_labeling_tasks(request)

    @rpc_errors
    async def RecallLabelingTask(
        self, request: labeling_v1_labeling_task_approval_service_pb2.RecallLabelingTaskRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_labeling_task_approval_service_pb2.RecallLabelingTaskResponse:
        """Recalls a labeling task."""
        return await self.handle_recall_labeling_task(request)

    @rpc_errors
    async def RejectLabelingTask(
        self, request: labeling_v1_labeling_task_approval_service_pb2.RejectLabelingTaskRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_labeling_task_approval_service_pb2.RejectLabelingTaskResponse:
        """Rejects a labeling task."""
        return await self.handle_reject_labeling_task(request)

    @rpc_errors
    async def SubmitLabelingTask(
        self, request: labeling_v1_labeling_task_approval_service_pb2.SubmitLabelingTaskRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_labeling_task_approval_service_pb2.SubmitLabelingTaskResponse:
        """Submits a labeling task."""
        return await self.handle_submit_labeling_task(request)

    async def handle_approve_labeling_task(
        self,
        request: labeling_v1_labeling_task_approval_service_pb2.ApproveLabelingTaskRequest
    ) -> labeling_v1_labeling_task_approval_service_pb2.ApproveLabelingTaskResponse:
        """Approves a labeling task."""
        deps = self.deps
        response = labeling_v1_labeling_task_approval_service_pb2.ApproveLabelingTaskResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ApproveLabelingTask', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'ApproveLabelingTask', {'reason': request.reason})
            await deps.repository.save_labeling_task(request.context.tenant_id, request.labeling_task)
            response_0 = labeling_v1_annotation_validation_service_pb2.ValidateAnnotationResponse()
            response_1 = lineage_v1_lineage_edge_workflow_service_pb2.CancelLineageEdgeWorkflowResponse()
            response_2 = labeling_v1_label_set_calculation_service_pb2.SimulateLabelSetResponse()
            outgoing_0 = labeling_v1_annotation_validation_service_pb2.ValidateAnnotationRequest(
                context=request.context,
                details=labeling_v1_annotation_validation_service_pb2.ValidateAnnotationRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(
                        phone=request.labeling_task.requester.phone,
                        preferred_channel=request.labeling_task.requester.preferred_channel
                    )
                )
            )
            outgoing_1 = lineage_v1_lineage_edge_workflow_service_pb2.CancelLineageEdgeWorkflowRequest(
                context=request.context,
                details=lineage_v1_lineage_edge_workflow_service_pb2.CancelLineageEdgeWorkflowRequest.Details(
                    notify=common_v1_contact_pb2.ContactInfo(email=request.labeling_task.assignee.email)
                ),
                lineage_edge=lineage_v1_lineage_pb2.LineageEdge(
                    subject=lineage_v1_refs_pb2.ImpactRef(
                        display_name=request.labeling_task.customer.display_name,
                        priority=request.labeling_task.priority
                    )
                )
            )
            response_0, response_1 = await asyncio.gather(
                deps.clients.labeling_annotation_validation.ValidateAnnotation(
                    outgoing_0,
                    timeout=deps.settings.timeout
                ),
                deps.clients.lineage_lineage_edge_workflow.CancelLineageEdgeWorkflow(
                    outgoing_1,
                    timeout=deps.settings.timeout
                ),
            )
            command_2 = LabelingTaskApprovalApproveLabelingTask2Command(
                context=request.context,
                label_set_children_children_audit_updated_by=request.labeling_task.audit.updated_by,
                label_set_children_children_manager_display_name=request.labeling_task.assignee.display_name,
                label_set_children_children_manager_email=request.labeling_task.assignee.email,
                label_set_children_manager_display_name=response_0.annotation.subject.display_name
            )
            outgoing_2 = to_labeling_task_approval_approve_labeling_task2_command(command_2)
            response_2 = await deps.clients.labeling_label_set_calculation.SimulateLabelSet(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_0)
            returned_1_0 = response_1.lineage_edge.subject.display_name
            if returned_1_0:
                response.labeling_task.assignee.display_name = returned_1_0
            returned_2_0 = response_2.result.reference_ids
            response.result.reference_ids.extend(returned_2_0)
            echoed_0 = request.labeling_task_id
            response.labeling_task.labeling_task_id = echoed_0
            echoed_1 = request.labeling_task.requester
            response.labeling_task.requester.CopyFrom(echoed_1)
            return response

    async def handle_comment_labeling_task_approval(
        self,
        request: labeling_v1_labeling_task_approval_service_pb2.CommentLabelingTaskApprovalRequest
    ) -> labeling_v1_labeling_task_approval_service_pb2.CommentLabelingTaskApprovalResponse:
        """Comments a labeling task."""
        deps = self.deps
        response = labeling_v1_labeling_task_approval_service_pb2.CommentLabelingTaskApprovalResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CommentLabelingTaskApproval', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'CommentLabelingTaskApproval',
                {'reason': request.reason}
            )
            await deps.repository.save_labeling_task(request.context.tenant_id, request.labeling_task)
            response_0 = modelregistry_v1_model_version_workflow_service_pb2.PauseModelVersionWorkflowResponse()
            response_1 = modelregistry_v1_registered_model_sync_service_pb2.ReconcileRegisteredModelsResponse()
            command_0 = LabelingTaskApprovalCommentLabelingTaskApproval0Command.model_validate(
                {'context': request.context, 'details_notify_email': request.details.approver.email}
            )
            outgoing_0 = to_labeling_task_approval_comment_labeling_task_approval0_command(command_0)
            response_0 = await deps.clients.modelregistry_model_version_workflow.PauseModelVersionWorkflow(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = modelregistry_v1_registered_model_sync_service_pb2.ReconcileRegisteredModelsRequest(
                context=request.context,
                registered_model=modelregistry_v1_modelregistry_pb2.RegisteredModel(
                    owner=identity_v1_refs_pb2.UserRef(email=request.labeling_task.requester.email)
                )
            )
            send_1 = partial(
                deps.clients.modelregistry_registered_model_sync.ReconcileRegisteredModels,
                timeout=deps.settings.timeout
            )
            response_1 = await send_1(outgoing_1)
            returned_0_0 = response_0.result.details
            response.result.details.update(returned_0_0)
            returned_1_0 = response_1.outcome.status
            if returned_1_0:
                response.outcome.status = returned_1_0
            echoed_0 = request.labeling_task_id
            response.labeling_task.labeling_task_id = echoed_0
            echoed_1 = request.labeling_task.subject
            response.labeling_task.subject = echoed_1
            return response

    async def handle_delegate_labeling_task_approval(
        self,
        request: labeling_v1_labeling_task_approval_service_pb2.DelegateLabelingTaskApprovalRequest
    ) -> labeling_v1_labeling_task_approval_service_pb2.DelegateLabelingTaskApprovalResponse:
        """Delegates a labeling task."""
        deps = self.deps
        response = labeling_v1_labeling_task_approval_service_pb2.DelegateLabelingTaskApprovalResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('DelegateLabelingTaskApproval', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'DelegateLabelingTaskApproval',
                {'reason': request.reason}
            )
            await deps.repository.save_labeling_task(request.context.tenant_id, request.labeling_task)
            response_0 = metrics_v1_dashboard_notification_service_pb2.SubscribeDashboardUpdatesResponse()
            outgoing_0 = metrics_v1_dashboard_notification_service_pb2.SubscribeDashboardUpdatesRequest(
                context=request.context,
                details=metrics_v1_dashboard_notification_service_pb2.SubscribeDashboardUpdatesRequest.Details(
                    recipient=common_v1_contact_pb2.ContactInfo(
                        email=request.labeling_task.requester.email,
                        name=request.labeling_task.requester.name,
                        phone=request.labeling_task.requester.phone,
                        preferred_channel=request.labeling_task.requester.preferred_channel
                    )
                )
            )
            response_0 = await hooks.labeling_task_approval_delegate_labeling_task_approval0(
                deps.clients.metrics_dashboard_notification,
                outgoing_0,
                deps.settings.timeout
            )
            returned_0_0 = response_0.outcome.reference_id
            if returned_0_0:
                response.outcome.reference_id = returned_0_0
            returned_0_1 = response_0.result.correlation_id
            if returned_0_1:
                response.result.correlation_id = returned_0_1
            echoed_0 = request.labeling_task_id
            response.labeling_task.labeling_task_id = echoed_0
            echoed_1 = request.labeling_task.subject
            response.labeling_task.subject = echoed_1
            return response

    async def handle_escalate_labeling_task(
        self,
        request: labeling_v1_labeling_task_approval_service_pb2.EscalateLabelingTaskRequest
    ) -> labeling_v1_labeling_task_approval_service_pb2.EscalateLabelingTaskResponse:
        """Escalates a labeling task."""
        deps = self.deps
        response = labeling_v1_labeling_task_approval_service_pb2.EscalateLabelingTaskResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('EscalateLabelingTask', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'EscalateLabelingTask', {'reason': request.reason})
            await deps.repository.save_labeling_task(request.context.tenant_id, request.labeling_task)
            response_0 = sponsorships_v1_sponsor_query_service_pb2.ResolveSponsorsResponse()
            outgoing_0 = sponsorships_v1_sponsor_query_service_pb2.ResolveSponsorsRequest()
            outgoing_0.context.CopyFrom(request.context)
            outgoing_0.context.tenant_id = tenant_id.get()
            response_0 = await deps.clients.sponsorships_sponsor_query.ResolveSponsors(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.result.message = returned_0_0
            echoed_0 = request.labeling_task_id
            response.labeling_task.labeling_task_id = echoed_0
            echoed_1 = request.labeling_task.custom_fields
            response.labeling_task.custom_fields.update(echoed_1)
            return response

    async def handle_get_labeling_task_approval_status(
        self,
        request: labeling_v1_labeling_task_approval_service_pb2.GetLabelingTaskApprovalStatusRequest
    ) -> labeling_v1_labeling_task_approval_service_pb2.GetLabelingTaskApprovalStatusResponse:
        """Returns a labeling task."""
        deps = self.deps
        response = labeling_v1_labeling_task_approval_service_pb2.GetLabelingTaskApprovalStatusResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('GetLabelingTaskApprovalStatus', extra={'fields': {'domain': 'labeling'}})
            await deps.repository.audit(request.context.tenant_id, 'GetLabelingTaskApprovalStatus', {})
            response_0 = labeling_v1_label_set_lifecycle_service_pb2.ScheduleLabelSetExpiryResponse()
            outgoing_0 = labeling_v1_label_set_lifecycle_service_pb2.ScheduleLabelSetExpiryRequest(
                context=request.context,
                label_set=labeling_v1_labeling_pb2.LabelSet(
                    children=[
                        labeling_v1_labeling_pb2.LabelSet(
                            children=[
                                labeling_v1_labeling_pb2.LabelSet(
                                    children=[labeling_v1_labeling_pb2.LabelSet(parent_id=request.labeling_task_id)],
                                    manager=identity_v1_refs_pb2.UserRef(
                                        email=request.context.actor.email,
                                        user_id=request.context.actor.user_id
                                    )
                                )
                            ]
                        )
                    ]
                )
            )
            response_0 = await deps.clients.labeling_label_set_lifecycle.ScheduleLabelSetExpiry(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.label_set.manager.email
            if returned_0_0:
                response.labeling_task.requester.email = returned_0_0
            returned_0_1 = response_0.label_set.audit.created_at
            if returned_0_1.ListFields():
                response.labeling_task.audit.created_at.MergeFrom(returned_0_1)
            echoed_0 = request.labeling_task_id
            response.labeling_task.labeling_task_id = echoed_0
            return response

    async def handle_list_pending_labeling_tasks(
        self,
        request: labeling_v1_labeling_task_approval_service_pb2.ListPendingLabelingTasksRequest
    ) -> labeling_v1_labeling_task_approval_service_pb2.ListPendingLabelingTasksResponse:
        """Lists labeling tasks a page at a time."""
        deps = self.deps
        response = labeling_v1_labeling_task_approval_service_pb2.ListPendingLabelingTasksResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ListPendingLabelingTasks', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ListPendingLabelingTasks',
                {'order_by': request.order_by}
            )
            return response

    async def handle_recall_labeling_task(
        self,
        request: labeling_v1_labeling_task_approval_service_pb2.RecallLabelingTaskRequest
    ) -> labeling_v1_labeling_task_approval_service_pb2.RecallLabelingTaskResponse:
        """Recalls a labeling task."""
        deps = self.deps
        response = labeling_v1_labeling_task_approval_service_pb2.RecallLabelingTaskResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('RecallLabelingTask', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'RecallLabelingTask', {'reason': request.reason})
            await deps.repository.save_labeling_task(request.context.tenant_id, request.labeling_task)
            response_0 = lineage_v1_impact_approval_service_pb2.RecallImpactResponse()
            response_1 = modelregistry_v1_registered_model_sync_service_pb2.ResolveRegisteredModelConflictResponse()
            outgoing_0 = lineage_v1_impact_approval_service_pb2.RecallImpactRequest(
                context=request.context,
                details=lineage_v1_impact_approval_service_pb2.RecallImpactRequest.Details(
                    approver=identity_v1_refs_pb2.UserRef(email=request.labeling_task.requester.email)
                ),
                impact=lineage_v1_lineage_pb2.Impact(
                    requester=common_v1_contact_pb2.ContactInfo(email=request.details.approver.email)
                )
            )
            steps_0 = [
                partial(deps.clients.lineage_impact_approval.RecallImpact, outgoing_0, timeout=deps.settings.timeout)
            ]
            results_0 = await run_steps(steps_0)
            response_0 = results_0[-1]
            outgoing_1 = modelregistry_v1_registered_model_sync_service_pb2.ResolveRegisteredModelConflictRequest(
                context=request.context,
                registered_model=modelregistry_v1_modelregistry_pb2.RegisteredModel(
                    audit=common_v1_audit_pb2.AuditInfo(
                        created_at=request.labeling_task.audit.created_at,
                        etag=response_0.impact.audit.etag
                    )
                )
            )
            response_1 = await LabelingTaskApprovalRecallLabelingTask1Adapter(
                deps.clients.modelregistry_registered_model_sync,
                deps.settings.timeout
            )(outgoing_1)
            returned_0_0 = response_0.impact.audit.etag
            if returned_0_0:
                response.labeling_task.audit.etag = returned_0_0
            returned_1_0 = response_1.outcome.reference_id
            if returned_1_0:
                response.outcome.reference_id = returned_1_0
            echoed_0 = request.labeling_task_id
            response.labeling_task.labeling_task_id = echoed_0
            echoed_1 = request.labeling_task.status
            response.labeling_task.status = echoed_1
            return response

    async def handle_reject_labeling_task(
        self,
        request: labeling_v1_labeling_task_approval_service_pb2.RejectLabelingTaskRequest
    ) -> labeling_v1_labeling_task_approval_service_pb2.RejectLabelingTaskResponse:
        """Rejects a labeling task."""
        deps = self.deps
        response = labeling_v1_labeling_task_approval_service_pb2.RejectLabelingTaskResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('RejectLabelingTask', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'RejectLabelingTask', {'reason': request.reason})
            await deps.repository.save_labeling_task(request.context.tenant_id, request.labeling_task)
            response_0 = lineage_v1_impact_approval_service_pb2.SubmitImpactResponse()
            outgoing_0 = lineage_v1_impact_approval_service_pb2.SubmitImpactRequest(
                context=request.context,
                impact=lineage_v1_lineage_pb2.Impact(
                    assignee=identity_v1_refs_pb2.UserRef(email=request.labeling_task.requester.email),
                    audit=common_v1_audit_pb2.AuditInfo(created_at=request.labeling_task.audit.created_at)
                )
            )
            response_0 = cast(lineage_v1_impact_approval_service_pb2.SubmitImpactResponse, await deps.bus.request(
                'acme.labeling.v1.LabelingTaskApprovalService/RejectLabelingTask/0', outgoing_0, deps.settings.timeout,
            ))
            returned_0_0 = response_0.impact.tags
            response.labeling_task.tags.extend(returned_0_0)
            returned_0_1 = response_0.impact.requester.preferred_channel
            if returned_0_1:
                response.labeling_task.requester.preferred_channel = returned_0_1
            echoed_0 = request.labeling_task_id
            response.labeling_task.labeling_task_id = echoed_0
            echoed_1 = request.labeling_task.subject
            response.labeling_task.subject = echoed_1
            return response

    async def handle_submit_labeling_task(
        self,
        request: labeling_v1_labeling_task_approval_service_pb2.SubmitLabelingTaskRequest
    ) -> labeling_v1_labeling_task_approval_service_pb2.SubmitLabelingTaskResponse:
        """Submits a labeling task."""
        deps = self.deps
        response = labeling_v1_labeling_task_approval_service_pb2.SubmitLabelingTaskResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SubmitLabelingTask', extra={'fields': {'approver_email': request.details.approver_email}})
            await deps.repository.audit(
                request.context.tenant_id,
                'SubmitLabelingTask',
                {'approver_email': request.details.approver_email}
            )
            await deps.repository.save_labeling_task(request.context.tenant_id, request.labeling_task)
            response_0 = labeling_v1_label_set_reporting_service_pb2.GenerateLabelSetReportResponse()
            response_1 = documents_v1_document_validation_service_pb2.ValidateDocumentResponse()
            response_2 = labeling_v1_labeling_task_lifecycle_service_pb2.TerminateLabelingTaskResponse()
            outgoing_0 = labeling_v1_label_set_reporting_service_pb2.GenerateLabelSetReportRequest()
            outgoing_0.context.CopyFrom(request.context)
            outgoing_0.reason = request.reason
            if request.labeling_task.WhichOneof('origin') == 'customer':
                outgoing_0.label_set_id = request.labeling_task.customer.label_set_id
            outgoing_0.annotations.update(dict(request.annotations))
            outgoing_0.details.filters.update(dict(request.labeling_task.custom_fields))
            response_0 = await deps.clients.labeling_label_set_reporting.GenerateLabelSetReport(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            for item_1 in request.labeling_task.history:
                outgoing_1 = documents_v1_document_validation_service_pb2.ValidateDocumentRequest(
                    context=request.context,
                    details=documents_v1_document_validation_service_pb2.ValidateDocumentRequest.Details(
                        contact=common_v1_contact_pb2.ContactInfo(email=request.details.approver.email)
                    ),
                    document=documents_v1_documents_pb2.Document(
                        audit=common_v1_audit_pb2.AuditInfo(
                            created_at=item_1.changed_at,
                            etag=request.labeling_task.audit.etag
                        )
                    )
                )
                response_1 = await deps.clients.documents_document_validation.ValidateDocument(
                    outgoing_1,
                    timeout=deps.settings.timeout
                )
            fields_2: dict[str, Any] = {
                'context': request.context,
                'details': {
                    'new_owner': {'display_name': request.labeling_task.assignee.display_name},
                    'notify_contact': {
                        'email': request.labeling_task.assignee.email,
                        'phone': request.labeling_task.requester.phone,
                        'preferred_channel': request.labeling_task.requester.preferred_channel
                    }
                },
                'labeling_task_id': request.labeling_task.labeling_task_id
            }
            outgoing_2 = labeling_v1_labeling_task_lifecycle_service_pb2.TerminateLabelingTaskRequest(**fields_2)
            response_2 = await deps.clients.labeling_labeling_task_lifecycle.TerminateLabelingTask(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.outcome.message = returned_0_0
            returned_2_0 = response_2.labeling_task.assignee.email
            if returned_2_0:
                response.labeling_task.assignee.email = returned_2_0
            echoed_0 = request.labeling_task_id
            response.labeling_task.labeling_task_id = echoed_0
            echoed_1 = request.labeling_task.custom_fields
            response.labeling_task.custom_fields.update(echoed_1)
            return response
