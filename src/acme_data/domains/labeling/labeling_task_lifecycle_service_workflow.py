"""Application workflow for LabelingTask Lifecycle."""

from __future__ import annotations

from functools import partial
import asyncio
import logging

from google.protobuf.any_pb2 import Any as AnyMessage

from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.labeling.v1 import annotation_calculation_service_pb2 as labeling_v1_annotation_calculation_service_pb2
from acme.labeling.v1 import label_set_sync_service_pb2 as labeling_v1_label_set_sync_service_pb2
from acme.labeling.v1 import label_set_validation_service_pb2 as labeling_v1_label_set_validation_service_pb2
from acme.labeling.v1 import labeling_pb2 as labeling_v1_labeling_pb2
from acme.labeling.v1 import labeling_task_calculation_service_pb2 as labeling_v1_labeling_task_calculation_service_pb2
from acme.labeling.v1 import labeling_task_lifecycle_service_pb2 as labeling_v1_labeling_task_lifecycle_service_pb2
from acme.labeling.v1 import labeling_task_query_service_pb2 as labeling_v1_labeling_task_query_service_pb2
from acme.labeling.v1 import labeling_task_service_pb2 as labeling_v1_labeling_task_service_pb2
from acme.labeling.v1 import refs_pb2 as labeling_v1_refs_pb2
from acme.lineage.v1 import lineage_edge_approval_service_pb2 as lineage_v1_lineage_edge_approval_service_pb2
from acme.lineage.v1 import lineage_pb2 as lineage_v1_lineage_pb2
from acme.lineage.v1 import refs_pb2 as lineage_v1_refs_pb2
from acme.metrics.v1 import dashboard_export_service_pb2 as metrics_v1_dashboard_export_service_pb2
from acme.metrics.v1 import dashboard_notification_service_pb2 as metrics_v1_dashboard_notification_service_pb2

from acme_data.domains.labeling.adapters import LabelingTaskLifecycleTerminateLabelingTask0Adapter
from acme_data.domains.labeling.adapters import LabelingTaskLifecycleTerminateLabelingTask0Port
from acme_data.domains.labeling.adapters import LabelingTaskLifecycleTerminateLabelingTask2Adapter
from acme_data.domains.labeling.dependencies import Dependencies
from acme_data.domains.labeling.models import LabelingTaskLifecycleReinstateLabelingTask0Command
from acme_data.domains.labeling.models import LabelingTaskLifecycleReinstateLabelingTask1Command
from acme_data.domains.labeling.models import to_labeling_task_lifecycle_reinstate_labeling_task0_command
from acme_data.domains.labeling.models import to_labeling_task_lifecycle_reinstate_labeling_task1_command
from acme_data.platform.rpc import run_steps
from acme_data.platform.tenancy import tenant_id
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class LabelingTaskLifecycleServicerWorkflow:
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    async def handle_activate_labeling_task(
        self,
        request: labeling_v1_labeling_task_lifecycle_service_pb2.ActivateLabelingTaskRequest
    ) -> labeling_v1_labeling_task_lifecycle_service_pb2.ActivateLabelingTaskResponse:
        """Activates a labeling task."""
        deps = self.deps
        response = labeling_v1_labeling_task_lifecycle_service_pb2.ActivateLabelingTaskResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ActivateLabelingTask', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'ActivateLabelingTask', {'reason': request.reason})
            response_0 = labeling_v1_label_set_sync_service_pb2.PushLabelSetResponse()
            outgoing_0 = labeling_v1_label_set_sync_service_pb2.PushLabelSetRequest()
            outgoing_0.context.CopyFrom(request.context)
            field_0_1_part_1 = outgoing_0.label_set.children.add()
            field_0_1_part_2 = field_0_1_part_1.children.add()
            field_0_1_part_2.manager.email = request.details.notify_contact.email
            field_0_2_part_1 = outgoing_0.label_set.children.add()
            field_0_2_part_2 = field_0_2_part_1.children.add()
            field_0_2_part_2.manager.user_id = request.details.new_owner.user_id
            merged_0 = labeling_v1_label_set_sync_service_pb2.PushLabelSetRequest()
            merged_0.MergeFrom(outgoing_0)
            outgoing_0.CopyFrom(merged_0)
            response_0 = await deps.clients.labeling_label_set_sync.PushLabelSet(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.label_set.audit.created_at
            returned_0_0_part_1 = response.labeling_task.comments.add()
            if returned_0_0.ListFields():
                returned_0_0_part_1.created_at.MergeFrom(returned_0_0)
            returned_0_1 = response_0.label_set.manager.display_name
            if returned_0_1:
                response.labeling_task.assignee.display_name = returned_0_1
            echoed_0 = request.labeling_task_id
            response.labeling_task.labeling_task_id = echoed_0
            echoed_1 = request.details.effective_at
            response.outcome.effective_at.CopyFrom(echoed_1)
            return response

    async def handle_expire_labeling_task(
        self,
        request: labeling_v1_labeling_task_lifecycle_service_pb2.ExpireLabelingTaskRequest
    ) -> labeling_v1_labeling_task_lifecycle_service_pb2.ExpireLabelingTaskResponse:
        """Expires a labeling task."""
        deps = self.deps
        response = labeling_v1_labeling_task_lifecycle_service_pb2.ExpireLabelingTaskResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ExpireLabelingTask', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'ExpireLabelingTask', {'reason': request.reason})
            response_0 = labeling_v1_labeling_task_query_service_pb2.BrowseLabelingTasksResponse()
            outgoing_0 = labeling_v1_labeling_task_query_service_pb2.BrowseLabelingTasksRequest(
                context=request.context,
                filter=labeling_v1_labeling_task_query_service_pb2.BrowseLabelingTasksRequest.Filter(
                    created_after=request.details.effective_at,
                    labels=dict(request.annotations),
                    owner_id=request.details.new_owner.user_id
                )
            )
            envelope_0 = AnyMessage()
            envelope_0.Pack(outgoing_0)
            outgoing_0 = labeling_v1_labeling_task_query_service_pb2.BrowseLabelingTasksRequest()
            if not envelope_0.Unpack(outgoing_0):
                raise ValueError("partner envelope contains the wrong request type")
            response_0 = await deps.clients.labeling_labeling_task_query.BrowseLabelingTasks(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.result.message = returned_0_0
            returned_0_1 = response_0.result.message
            if returned_0_1:
                response.outcome.message = returned_0_1
            echoed_0 = request.labeling_task_id
            response.labeling_task.labeling_task_id = echoed_0
            echoed_1 = request.details.effective_at
            response.outcome.effective_at.CopyFrom(echoed_1)
            return response

    async def handle_get_labeling_task_lifecycle(
        self,
        request: labeling_v1_labeling_task_lifecycle_service_pb2.GetLabelingTaskLifecycleRequest
    ) -> labeling_v1_labeling_task_lifecycle_service_pb2.GetLabelingTaskLifecycleResponse:
        """Returns a labeling task."""
        deps = self.deps
        response = labeling_v1_labeling_task_lifecycle_service_pb2.GetLabelingTaskLifecycleResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('GetLabelingTaskLifecycle', extra={'fields': {'domain': 'labeling'}})
            await deps.repository.audit(request.context.tenant_id, 'GetLabelingTaskLifecycle', {})
            response_0 = labeling_v1_annotation_calculation_service_pb2.RecalculateAnnotationsResponse()
            outgoing_0 = labeling_v1_annotation_calculation_service_pb2.RecalculateAnnotationsRequest(
                annotation=labeling_v1_labeling_pb2.Annotation(
                    measurements=[labeling_v1_labeling_pb2.AnnotationMeasurement(observed_at=request.context.deadline)],
                    source=request.context.actor.user_id,
                    subject=labeling_v1_refs_pb2.LabelingTaskRef(labeling_task_id=request.labeling_task_id)
                ),
                context=request.context
            )
            response_0 = await deps.clients.labeling_annotation_calculation.RecalculateAnnotations(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.correlation_id
            if returned_0_0:
                response.result.correlation_id = returned_0_0
            echoed_0 = request.labeling_task_id
            response.labeling_task.labeling_task_id = echoed_0
            return response

    async def handle_reinstate_labeling_task(
        self,
        request: labeling_v1_labeling_task_lifecycle_service_pb2.ReinstateLabelingTaskRequest
    ) -> labeling_v1_labeling_task_lifecycle_service_pb2.ReinstateLabelingTaskResponse:
        """Reinstates a labeling task."""
        deps = self.deps
        response = labeling_v1_labeling_task_lifecycle_service_pb2.ReinstateLabelingTaskResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ReinstateLabelingTask', extra={'fields': {'reason_code': request.details.reason_code}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ReinstateLabelingTask',
                {'reason_code': request.details.reason_code}
            )
            response_0 = metrics_v1_dashboard_notification_service_pb2.UnsubscribeDashboardUpdatesResponse()
            response_1 = metrics_v1_dashboard_export_service_pb2.ScheduleDashboardExportResponse()
            command_0 = LabelingTaskLifecycleReinstateLabelingTask0Command(
                context=request.context,
                details_recipient_phone=request.details.notify_contact.phone,
                details_recipient_name=request.details.notify_contact.name
            )
            outgoing_0 = to_labeling_task_lifecycle_reinstate_labeling_task0_command(command_0)
            response_0 = await deps.clients.metrics_dashboard_notification.UnsubscribeDashboardUpdates(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            command_1 = LabelingTaskLifecycleReinstateLabelingTask1Command.model_validate(
                {
                    'context': request.context,
                    'dashboard_id': response_0.dashboard.dashboard_id,
                    'annotations': dict(request.annotations),
                    'reason': request.reason,
                    'details_filters': dict(response_0.result.details)
                }
            )
            outgoing_1 = to_labeling_task_lifecycle_reinstate_labeling_task1_command(command_1)
            response_1 = await deps.clients.metrics_dashboard_export.ScheduleDashboardExport(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.dashboard.audit.created_by
            if returned_0_0:
                response.labeling_task.audit.created_by = returned_0_0
            returned_1_0 = response_1.result.message
            if returned_1_0:
                response.outcome.message = returned_1_0
            echoed_0 = request.labeling_task_id
            response.labeling_task.labeling_task_id = echoed_0
            echoed_1 = request.details.effective_at
            response.outcome.effective_at.CopyFrom(echoed_1)
            return response

    async def handle_renew_labeling_task(
        self,
        request: labeling_v1_labeling_task_lifecycle_service_pb2.RenewLabelingTaskRequest
    ) -> labeling_v1_labeling_task_lifecycle_service_pb2.RenewLabelingTaskResponse:
        """Renews a labeling task."""
        deps = self.deps
        response = labeling_v1_labeling_task_lifecycle_service_pb2.RenewLabelingTaskResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('RenewLabelingTask', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'RenewLabelingTask', {'reason': request.reason})
            response_0 = labeling_v1_labeling_task_service_pb2.CloneLabelingTaskResponse()
            response_1 = labeling_v1_label_set_sync_service_pb2.PushLabelSetResponse()
            outgoing_0 = labeling_v1_labeling_task_service_pb2.CloneLabelingTaskRequest(
                context=request.context,
                labeling_task=labeling_v1_labeling_pb2.LabelingTask(
                    assignee=identity_v1_refs_pb2.UserRef(email=request.details.notify_contact.email),
                    customer=labeling_v1_refs_pb2.LabelSetRef(display_name=request.details.new_owner.display_name),
                    requester=common_v1_contact_pb2.ContactInfo(
                        email=request.details.new_owner.email,
                        phone=request.details.notify_contact.phone
                    )
                )
            )
            outgoing_1 = labeling_v1_label_set_sync_service_pb2.PushLabelSetRequest(
                context=request.context,
                label_set=labeling_v1_labeling_pb2.LabelSet(
                    children=[
                        labeling_v1_labeling_pb2.LabelSet(
                            children=[
                                labeling_v1_labeling_pb2.LabelSet(
                                    manager=identity_v1_refs_pb2.UserRef(email=request.details.notify_contact.email)
                                )
                            ]
                        )
                    ]
                )
            )
            response_0, response_1 = await asyncio.gather(
                deps.clients.labeling_labeling_task.CloneLabelingTask(outgoing_0, timeout=deps.settings.timeout),
                deps.clients.labeling_label_set_sync.PushLabelSet(outgoing_1, timeout=deps.settings.timeout),
            )
            returned_0_0 = response_0.labeling_task.requester.email
            if returned_0_0:
                response.labeling_task.assignee.email = returned_0_0
            returned_1_0 = response_1.result.status
            if returned_1_0:
                response.outcome.status = returned_1_0
            returned_1_1 = response_1.result.reference_ids
            response.result.reference_ids.extend(returned_1_1)
            echoed_0 = request.labeling_task_id
            response.labeling_task.labeling_task_id = echoed_0
            echoed_1 = request.details.effective_at
            response.outcome.effective_at.CopyFrom(echoed_1)
            return response

    async def handle_suspend_labeling_task(
        self,
        request: labeling_v1_labeling_task_lifecycle_service_pb2.SuspendLabelingTaskRequest
    ) -> labeling_v1_labeling_task_lifecycle_service_pb2.SuspendLabelingTaskResponse:
        """Suspends a labeling task."""
        deps = self.deps
        response = labeling_v1_labeling_task_lifecycle_service_pb2.SuspendLabelingTaskResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SuspendLabelingTask', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'SuspendLabelingTask', {'reason': request.reason})
            response_0 = labeling_v1_label_set_validation_service_pb2.LintLabelSetsResponse()
            outgoing_0 = labeling_v1_label_set_validation_service_pb2.LintLabelSetsRequest()
            outgoing_0.context.CopyFrom(request.context)
            field_0_1_part_1 = outgoing_0.label_set.children.add()
            field_0_1_part_1.manager.email = request.details.notify_contact.email
            field_0_2_part_1 = outgoing_0.label_set.children.add()
            field_0_2_part_1.manager.user_id = request.details.new_owner.user_id
            field_0_3_part_1 = outgoing_0.label_set.children.add()
            field_0_3_part_2 = field_0_3_part_1.children.add()
            field_0_3_part_2.manager.display_name = request.details.new_owner.display_name
            outgoing_0.label_set.manager.email = request.details.new_owner.email
            outgoing_0.context.tenant_id = tenant_id.get()
            response_0 = await deps.clients.labeling_label_set_validation.LintLabelSets(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.result.message = returned_0_0
            echoed_0 = request.labeling_task_id
            response.labeling_task.labeling_task_id = echoed_0
            echoed_1 = request.details.effective_at
            response.outcome.effective_at.CopyFrom(echoed_1)
            return response

    async def handle_terminate_labeling_task(
        self,
        request: labeling_v1_labeling_task_lifecycle_service_pb2.TerminateLabelingTaskRequest
    ) -> labeling_v1_labeling_task_lifecycle_service_pb2.TerminateLabelingTaskResponse:
        """Terminates a labeling task."""
        deps = self.deps
        response = labeling_v1_labeling_task_lifecycle_service_pb2.TerminateLabelingTaskResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('TerminateLabelingTask', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'TerminateLabelingTask', {'reason': request.reason})
            response_0 = labeling_v1_labeling_task_calculation_service_pb2.CalculateLabelingTaskResponse()
            response_1 = labeling_v1_label_set_validation_service_pb2.ValidateLabelSetResponse()
            response_2 = lineage_v1_lineage_edge_approval_service_pb2.ApproveLineageEdgeResponse()
            outgoing_0 = labeling_v1_labeling_task_calculation_service_pb2.CalculateLabelingTaskRequest(
                context=request.context,
                labeling_task=labeling_v1_labeling_pb2.LabelingTask(
                    assignee=identity_v1_refs_pb2.UserRef(display_name=request.details.new_owner.display_name)
                )
            )
            port_0: LabelingTaskLifecycleTerminateLabelingTask0Port = LabelingTaskLifecycleTerminateLabelingTask0Adapter(
                deps.clients.labeling_labeling_task_calculation,
                deps.settings.timeout
            )
            response_0 = await port_0.execute(outgoing_0)
            outgoing_1 = labeling_v1_label_set_validation_service_pb2.ValidateLabelSetRequest(
                context=request.context,
                label_set=labeling_v1_labeling_pb2.LabelSet(
                    children=[
                        labeling_v1_labeling_pb2.LabelSet(
                            children=[
                                labeling_v1_labeling_pb2.LabelSet(
                                    audit=common_v1_audit_pb2.AuditInfo(
                                        etag=response_0.labeling_task.audit.etag,
                                        updated_at=response_0.labeling_task.audit.updated_at
                                    ),
                                    manager=identity_v1_refs_pb2.UserRef(
                                        display_name=response_0.labeling_task.assignee.display_name
                                    )
                                )
                            ],
                            manager=identity_v1_refs_pb2.UserRef(user_id=response_0.labeling_task.assignee.user_id)
                        )
                    ]
                )
            )
            steps_1 = [
                partial(
                    deps.clients.labeling_label_set_validation.ValidateLabelSet,
                    outgoing_1,
                    timeout=deps.settings.timeout
                )
            ]
            results_1 = await run_steps(steps_1)
            response_1 = results_1[-1]
            outgoing_2 = lineage_v1_lineage_edge_approval_service_pb2.ApproveLineageEdgeRequest(
                context=request.context,
                details=lineage_v1_lineage_edge_approval_service_pb2.ApproveLineageEdgeRequest.Details(
                    approver=identity_v1_refs_pb2.UserRef(email=response_1.label_set.manager.email)
                ),
                lineage_edge=lineage_v1_lineage_pb2.LineageEdge(
                    subject=lineage_v1_refs_pb2.ImpactRef(display_name=response_0.labeling_task.customer.display_name)
                )
            )
            response_2 = await LabelingTaskLifecycleTerminateLabelingTask2Adapter(
                deps.clients.lineage_lineage_edge_approval,
                deps.settings.timeout
            )(outgoing_2)
            returned_0_0 = response_0.labeling_task.custom_fields
            response.labeling_task.custom_fields.update(returned_0_0)
            returned_0_1 = response_0.labeling_task.subject
            if returned_0_1:
                response.labeling_task.subject = returned_0_1
            returned_1_0 = response_1.label_set.manager.email
            if returned_1_0:
                response.labeling_task.requester.email = returned_1_0
            returned_2_0 = response_2.outcome.message
            if returned_2_0:
                response.outcome.message = returned_2_0
            echoed_0 = request.labeling_task_id
            response.labeling_task.labeling_task_id = echoed_0
            echoed_1 = request.details.effective_at
            response.outcome.effective_at.CopyFrom(echoed_1)
            return response
