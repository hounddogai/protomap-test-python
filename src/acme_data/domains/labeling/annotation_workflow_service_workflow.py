"""Application workflow for Annotation Workflow."""

from __future__ import annotations

from collections.abc import Awaitable
from collections.abc import Callable
from functools import partial
from typing import cast
import asyncio
import logging

from google.protobuf.any_pb2 import Any as AnyMessage
from google.protobuf.json_format import MessageToDict
from google.protobuf.json_format import MessageToJson
from google.protobuf.json_format import Parse
from google.protobuf.json_format import ParseDict

from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.concessions.v1 import concession_stand_service_pb2 as concessions_v1_concession_stand_service_pb2
from acme.featurestore.v1 import (
    feature_value_reporting_service_pb2 as featurestore_v1_feature_value_reporting_service_pb2,
)
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.identity.v1 import user_validation_service_pb2 as identity_v1_user_validation_service_pb2
from acme.labeling.v1 import annotation_approval_service_pb2 as labeling_v1_annotation_approval_service_pb2
from acme.labeling.v1 import annotation_lifecycle_service_pb2 as labeling_v1_annotation_lifecycle_service_pb2
from acme.labeling.v1 import annotation_lifecycle_service_pb2_grpc as labeling_v1_annotation_lifecycle_service_pb2_grpc
from acme.labeling.v1 import annotation_reporting_service_pb2 as labeling_v1_annotation_reporting_service_pb2
from acme.labeling.v1 import annotation_workflow_service_pb2 as labeling_v1_annotation_workflow_service_pb2
from acme.labeling.v1 import label_set_calculation_service_pb2 as labeling_v1_label_set_calculation_service_pb2
from acme.labeling.v1 import label_set_reporting_service_pb2 as labeling_v1_label_set_reporting_service_pb2
from acme.labeling.v1 import label_set_validation_service_pb2 as labeling_v1_label_set_validation_service_pb2
from acme.labeling.v1 import labeling_pb2 as labeling_v1_labeling_pb2
from acme.labeling.v1 import labeling_task_approval_service_pb2 as labeling_v1_labeling_task_approval_service_pb2
from acme.labeling.v1 import labeling_task_lifecycle_service_pb2 as labeling_v1_labeling_task_lifecycle_service_pb2
from acme.labeling.v1 import labeling_task_query_service_pb2 as labeling_v1_labeling_task_query_service_pb2
from acme.labeling.v1 import labeling_task_workflow_service_pb2 as labeling_v1_labeling_task_workflow_service_pb2
from acme.labeling.v1 import refs_pb2 as labeling_v1_refs_pb2
from acme.messaging.v1 import conversation_query_service_pb2 as messaging_v1_conversation_query_service_pb2
from acme.metrics.v1 import metric_alert_export_service_pb2 as metrics_v1_metric_alert_export_service_pb2
from acme.notifications.v1 import (
    notification_validation_service_pb2 as notifications_v1_notification_validation_service_pb2,
)
from acme.notifications.v1 import (
    notification_validation_service_pb2_grpc as notifications_v1_notification_validation_service_pb2_grpc,
)
from acme.notifications.v1 import notifications_pb2 as notifications_v1_notifications_pb2

from acme_data.domains.labeling.adapters import AnnotationWorkflowCancelAnnotationWorkflow3Adapter
from acme_data.domains.labeling.adapters import AnnotationWorkflowCancelAnnotationWorkflow3Port
from acme_data.domains.labeling.dependencies import Dependencies
from acme_data.domains.labeling.models import AnnotationWorkflowAdvanceAnnotationWorkflow2Command
from acme_data.domains.labeling.models import AnnotationWorkflowAdvanceAnnotationWorkflow3Command
from acme_data.domains.labeling.models import to_annotation_workflow_advance_annotation_workflow2_command
from acme_data.domains.labeling.models import to_annotation_workflow_advance_annotation_workflow3_command
from acme_data.platform.rpc import async_messages
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class AnnotationWorkflowServicerWorkflow:
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    async def handle_advance_annotation_workflow(
        self,
        request: labeling_v1_annotation_workflow_service_pb2.AdvanceAnnotationWorkflowRequest
    ) -> labeling_v1_annotation_workflow_service_pb2.AdvanceAnnotationWorkflowResponse:
        """Advances an annotation."""
        deps = self.deps
        response = labeling_v1_annotation_workflow_service_pb2.AdvanceAnnotationWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('AdvanceAnnotationWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'AdvanceAnnotationWorkflow',
                {'reason': request.reason}
            )
            await deps.repository.save_annotation(request.context.tenant_id, request.annotation)
            response_0 = labeling_v1_label_set_calculation_service_pb2.CalculateLabelSetResponse()
            response_1 = notifications_v1_notification_validation_service_pb2.ValidateNotificationResponse()
            response_2 = labeling_v1_label_set_validation_service_pb2.PreviewLabelSetResponse()
            response_3 = labeling_v1_annotation_approval_service_pb2.RecallAnnotationResponse()
            outgoing_0 = labeling_v1_label_set_calculation_service_pb2.CalculateLabelSetRequest(
                context=request.context,
                label_set=labeling_v1_labeling_pb2.LabelSet(
                    children=[
                        labeling_v1_labeling_pb2.LabelSet(
                            children=[
                                labeling_v1_labeling_pb2.LabelSet(
                                    children=[
                                        labeling_v1_labeling_pb2.LabelSet(
                                            attributes=dict(request.annotation.attributes)
                                        )
                                    ],
                                    manager=identity_v1_refs_pb2.UserRef(email=request.details.notify.email)
                                )
                            ]
                        )
                    ]
                )
            )
            envelope_0 = AnyMessage()
            envelope_0.Pack(outgoing_0)
            outgoing_0 = labeling_v1_label_set_calculation_service_pb2.CalculateLabelSetRequest()
            if not envelope_0.Unpack(outgoing_0):
                raise ValueError("partner envelope contains the wrong request type")
            response_0 = await deps.clients.labeling_label_set_calculation.CalculateLabelSet(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = notifications_v1_notification_validation_service_pb2.ValidateNotificationRequest(
                context=request.context,
                details=notifications_v1_notification_validation_service_pb2.ValidateNotificationRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(email=request.details.notify.email)
                ),
                notification=notifications_v1_notifications_pb2.Notification(
                    assignee=identity_v1_refs_pb2.UserRef(
                        display_name=request.annotation.subject.display_name,
                        user_id=response_0.label_set.manager.user_id
                    )
                )
            )
            registered_1 = cast(
                notifications_v1_notification_validation_service_pb2_grpc.NotificationValidationServiceStub,
                deps.clients.registry['acme.notifications.v1.NotificationValidationService']
            )
            response_1 = await registered_1.ValidateNotification(outgoing_1, timeout=deps.settings.timeout)
            command_2 = AnnotationWorkflowAdvanceAnnotationWorkflow2Command(
                context=request.context,
                label_set_children_children_audit_created_at=response_1.notification.audit.created_at,
                label_set_children_children_audit_created_by=response_0.label_set.audit.created_by,
                label_set_children_children_audit_updated_by=response_0.label_set.audit.updated_by
            )
            outgoing_2 = to_annotation_workflow_advance_annotation_workflow2_command(command_2)
            response_2 = await deps.clients.labeling_label_set_validation.PreviewLabelSet(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            command_3 = AnnotationWorkflowAdvanceAnnotationWorkflow3Command.model_validate(
                {'context': request.context, 'details_approver_email': response_0.label_set.manager.email}
            )
            outgoing_3 = to_annotation_workflow_advance_annotation_workflow3_command(command_3)
            response_3 = await deps.clients.labeling_annotation_approval.RecallAnnotation(
                outgoing_3,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.label_set.manager.display_name
            if returned_0_0:
                response.annotation.subject.display_name = returned_0_0
            returned_0_1 = response_0.result.message
            if returned_0_1:
                response.outcome.message = returned_0_1
            returned_1_0 = response_1.result.correlation_id
            if returned_1_0:
                response.result.correlation_id = returned_1_0
            returned_1_1 = response_1.notification.assignee.display_name
            if returned_1_1:
                response.annotation.subject.display_name = returned_1_1
            returned_2_0 = response_2.outcome.message
            if returned_2_0:
                response.result.message = returned_2_0
            returned_2_1 = response_2.outcome.next_steps
            response.outcome.next_steps.extend(returned_2_1)
            returned_3_0 = response_3.outcome.status
            if returned_3_0:
                response.result.status = returned_3_0
            returned_3_1 = response_3.result.status
            if returned_3_1:
                response.outcome.status = returned_3_1
            echoed_0 = request.annotation_id
            response.annotation.annotation_id = echoed_0
            echoed_1 = request.annotation.attributes
            response.annotation.attributes.update(echoed_1)
            return response

    async def handle_cancel_annotation_workflow(
        self,
        request: labeling_v1_annotation_workflow_service_pb2.CancelAnnotationWorkflowRequest
    ) -> labeling_v1_annotation_workflow_service_pb2.CancelAnnotationWorkflowResponse:
        """Cancels an annotation."""
        deps = self.deps
        response = labeling_v1_annotation_workflow_service_pb2.CancelAnnotationWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CancelAnnotationWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'CancelAnnotationWorkflow',
                {'reason': request.reason}
            )
            await deps.repository.save_annotation(request.context.tenant_id, request.annotation)
            response_0 = labeling_v1_labeling_task_query_service_pb2.CountLabelingTasksResponse()
            response_1 = labeling_v1_annotation_reporting_service_pb2.FetchAnnotationReportResponse()
            response_2 = labeling_v1_labeling_task_query_service_pb2.LookupLabelingTaskResponse()
            response_3 = labeling_v1_annotation_approval_service_pb2.CommentAnnotationApprovalResponse()
            outgoing_0 = labeling_v1_labeling_task_query_service_pb2.CountLabelingTasksRequest(
                context=request.context,
                filter=labeling_v1_labeling_task_query_service_pb2.CountLabelingTasksRequest.Filter(
                    created_after=request.annotation.occurred_at,
                    labels=dict(request.details.parameters)
                )
            )
            outgoing_1 = labeling_v1_annotation_reporting_service_pb2.FetchAnnotationReportRequest(
                annotation_id=request.annotation_id,
                context=request.context
            )
            outgoing_2 = labeling_v1_labeling_task_query_service_pb2.LookupLabelingTaskRequest(
                context=request.context,
                labeling_task_id=request.annotation.subject.labeling_task_id
            )
            response_0, response_1, response_2 = await asyncio.gather(
                deps.clients.labeling_labeling_task_query.CountLabelingTasks(outgoing_0, timeout=deps.settings.timeout),
                deps.clients.labeling_annotation_reporting.FetchAnnotationReport(
                    outgoing_1,
                    timeout=deps.settings.timeout
                ),
                deps.clients.labeling_labeling_task_query.LookupLabelingTask(outgoing_2, timeout=deps.settings.timeout),
            )
            outgoing_3 = labeling_v1_annotation_approval_service_pb2.CommentAnnotationApprovalRequest(
                context=request.context,
                details=labeling_v1_annotation_approval_service_pb2.CommentAnnotationApprovalRequest.Details(
                    approver=identity_v1_refs_pb2.UserRef(display_name=response_1.annotation.subject.display_name)
                )
            )
            port_3: AnnotationWorkflowCancelAnnotationWorkflow3Port = AnnotationWorkflowCancelAnnotationWorkflow3Adapter(
                deps.clients.labeling_annotation_approval,
                deps.settings.timeout
            )
            response_3 = await port_3.execute(outgoing_3)
            returned_0_0 = response_0.result.status
            if returned_0_0:
                response.outcome.status = returned_0_0
            returned_1_0 = response_1.annotation.source
            if returned_1_0:
                response.annotation.source = returned_1_0
            returned_1_1 = response_1.result.status
            if returned_1_1:
                response.result.status = returned_1_1
            returned_2_0 = response_2.labeling_task.priority
            if returned_2_0:
                response.annotation.subject.priority = returned_2_0
            returned_2_1 = response_2.result.status
            if returned_2_1:
                response.outcome.status = returned_2_1
            returned_3_0 = response_3.annotation.occurred_at
            if returned_3_0.ListFields():
                response.annotation.occurred_at.MergeFrom(returned_3_0)
            returned_3_1 = response_3.annotation.subject.display_name
            if returned_3_1:
                response.annotation.subject.display_name = returned_3_1
            echoed_0 = request.annotation_id
            response.annotation.annotation_id = echoed_0
            echoed_1 = request.annotation.sequence
            response.annotation.sequence = echoed_1
            return response

    async def handle_inspect_annotation_workflow(
        self,
        request: labeling_v1_annotation_workflow_service_pb2.InspectAnnotationWorkflowRequest
    ) -> labeling_v1_annotation_workflow_service_pb2.InspectAnnotationWorkflowResponse:
        """Returns an annotation."""
        deps = self.deps
        response = labeling_v1_annotation_workflow_service_pb2.InspectAnnotationWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('InspectAnnotationWorkflow', extra={'fields': {'domain': 'labeling'}})
            await deps.repository.audit(request.context.tenant_id, 'InspectAnnotationWorkflow', {})
            response_0 = identity_v1_user_validation_service_pb2.GetUserRulesResponse()
            outgoing_0 = identity_v1_user_validation_service_pb2.GetUserRulesRequest(
                context=request.context,
                user_id=request.context.actor.user_id
            )
            response_0 = await deps.clients.identity_user_validation.GetUserRules(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.correlation_id
            if returned_0_0:
                response.result.correlation_id = returned_0_0
            echoed_0 = request.annotation_id
            response.annotation.annotation_id = echoed_0
            return response

    async def handle_list_annotation_workflows(
        self,
        request: labeling_v1_annotation_workflow_service_pb2.ListAnnotationWorkflowsRequest
    ) -> labeling_v1_annotation_workflow_service_pb2.ListAnnotationWorkflowsResponse:
        """Lists annotations a page at a time."""
        deps = self.deps
        response = labeling_v1_annotation_workflow_service_pb2.ListAnnotationWorkflowsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ListAnnotationWorkflows', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ListAnnotationWorkflows',
                {'order_by': request.order_by}
            )
            response_0 = labeling_v1_annotation_approval_service_pb2.ListPendingAnnotationsResponse()
            outgoing_0 = labeling_v1_annotation_approval_service_pb2.ListPendingAnnotationsRequest(
                context=request.context,
                filter=labeling_v1_annotation_approval_service_pb2.ListPendingAnnotationsRequest.Filter(
                    statuses=list(request.filter.statuses)
                )
            )
            response_0 = await deps.clients.labeling_annotation_approval.ListPendingAnnotations(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.correlation_id
            returned_0_0_part_0 = response.annotations.add()
            if returned_0_0:
                returned_0_0_part_0.correlation_id = returned_0_0
            return response

    async def handle_pause_annotation_workflow(
        self,
        request: labeling_v1_annotation_workflow_service_pb2.PauseAnnotationWorkflowRequest
    ) -> labeling_v1_annotation_workflow_service_pb2.PauseAnnotationWorkflowResponse:
        """Pauses an annotation."""
        deps = self.deps
        response = labeling_v1_annotation_workflow_service_pb2.PauseAnnotationWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('PauseAnnotationWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'PauseAnnotationWorkflow',
                {'reason': request.reason}
            )
            await deps.repository.save_annotation(request.context.tenant_id, request.annotation)
            response_0 = notifications_v1_notification_validation_service_pb2.ValidateNotificationResponse()
            response_1 = messaging_v1_conversation_query_service_pb2.ExportConversationsResponse()
            response_2 = labeling_v1_labeling_task_workflow_service_pb2.ListLabelingTaskWorkflowsResponse()
            outgoing_0 = notifications_v1_notification_validation_service_pb2.ValidateNotificationRequest(
                context=request.context,
                details=notifications_v1_notification_validation_service_pb2.ValidateNotificationRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(email=request.details.notify.email)
                ),
                notification=notifications_v1_notifications_pb2.Notification(
                    assignee=identity_v1_refs_pb2.UserRef(display_name=request.annotation.subject.display_name)
                )
            )
            response_0 = cast(notifications_v1_notification_validation_service_pb2.ValidateNotificationResponse, await deps.bus.request(
                'acme.labeling.v1.AnnotationWorkflowService/PauseAnnotationWorkflow/0', outgoing_0, deps.settings.timeout,
            ))
            outgoing_1 = messaging_v1_conversation_query_service_pb2.ExportConversationsRequest(
                context=request.context,
                filter=messaging_v1_conversation_query_service_pb2.ExportConversationsRequest.Filter(
                    created_after=response_0.notification.audit.created_at,
                    labels=dict(request.annotation.attributes),
                    owner_id=request.annotation.subject.labeling_task_id
                )
            )
            async for chunk_1 in deps.clients.messaging_conversation_query.ExportConversations(
                outgoing_1,
                timeout=deps.settings.timeout
            ):
                response_1 = chunk_1
            callbacks_2: list[
                Callable[
                    [],
                    Awaitable[labeling_v1_labeling_task_workflow_service_pb2.ListLabelingTaskWorkflowsResponse]
                ]
            ] = []
            for item_2 in request.annotation.measurements:
                outgoing_2 = labeling_v1_labeling_task_workflow_service_pb2.ListLabelingTaskWorkflowsRequest(
                    context=request.context,
                    filter=labeling_v1_labeling_task_workflow_service_pb2.ListLabelingTaskWorkflowsRequest.Filter(
                        created_after=item_2.observed_at,
                        labels=dict(response_0.result.details),
                        owner_id=response_0.notification.customer.notification_template_id
                    )
                )
                async def send_2(
                    payload: labeling_v1_labeling_task_workflow_service_pb2.ListLabelingTaskWorkflowsRequest = outgoing_2
                ) -> labeling_v1_labeling_task_workflow_service_pb2.ListLabelingTaskWorkflowsResponse:
                    return await deps.clients.labeling_labeling_task_workflow.ListLabelingTaskWorkflows(
                        payload,
                        timeout=deps.settings.timeout
                    )
                callbacks_2.append(send_2)
            for callback_2 in callbacks_2:
                response_2 = await callback_2()
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.outcome.message = returned_0_0
            echoed_0 = request.annotation_id
            response.annotation.annotation_id = echoed_0
            echoed_1 = request.annotation.correlation_id
            response.result.correlation_id = echoed_1
            return response

    async def handle_resume_annotation_workflow(
        self,
        request: labeling_v1_annotation_workflow_service_pb2.ResumeAnnotationWorkflowRequest
    ) -> labeling_v1_annotation_workflow_service_pb2.ResumeAnnotationWorkflowResponse:
        """Resumes an annotation."""
        deps = self.deps
        response = labeling_v1_annotation_workflow_service_pb2.ResumeAnnotationWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ResumeAnnotationWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ResumeAnnotationWorkflow',
                {'reason': request.reason}
            )
            await deps.repository.save_annotation(request.context.tenant_id, request.annotation)
            response_0 = featurestore_v1_feature_value_reporting_service_pb2.ListFeatureValueReportsResponse()
            response_1 = labeling_v1_label_set_reporting_service_pb2.ListLabelSetReportsResponse()
            response_2 = labeling_v1_labeling_task_lifecycle_service_pb2.RenewLabelingTaskResponse()
            async for item_0 in async_messages(request.annotation.measurements):
                outgoing_0 = featurestore_v1_feature_value_reporting_service_pb2.ListFeatureValueReportsRequest(
                    context=request.context,
                    filter=featurestore_v1_feature_value_reporting_service_pb2.ListFeatureValueReportsRequest.Filter(
                        created_after=item_0.observed_at,
                        owner_id=request.annotation.subject.labeling_task_id
                    )
                )
                response_0 = await deps.clients.featurestore_feature_value_reporting.ListFeatureValueReports(
                    outgoing_0,
                    timeout=deps.settings.timeout
                )
            outgoing_1 = labeling_v1_label_set_reporting_service_pb2.ListLabelSetReportsRequest(
                context=request.context,
                filter=labeling_v1_label_set_reporting_service_pb2.ListLabelSetReportsRequest.Filter(
                    created_after=request.annotation.occurred_at,
                    labels=dict(request.details.parameters),
                    owner_id=request.annotation.annotation_id
                )
            )
            document_1 = MessageToDict(outgoing_1, preserving_proto_field_name=True)
            outgoing_1 = ParseDict(document_1, labeling_v1_label_set_reporting_service_pb2.ListLabelSetReportsRequest())
            response_1 = await deps.clients.labeling_label_set_reporting.ListLabelSetReports(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = labeling_v1_labeling_task_lifecycle_service_pb2.RenewLabelingTaskRequest(
                context=request.context,
                details=labeling_v1_labeling_task_lifecycle_service_pb2.RenewLabelingTaskRequest.Details(
                    new_owner=identity_v1_refs_pb2.UserRef(display_name=request.annotation.subject.display_name)
                ),
                labeling_task_id=request.annotation.subject.labeling_task_id
            )
            document_2 = MessageToJson(outgoing_2, preserving_proto_field_name=True)
            outgoing_2 = Parse(document_2, labeling_v1_labeling_task_lifecycle_service_pb2.RenewLabelingTaskRequest())
            response_2 = await deps.clients.labeling_labeling_task_lifecycle.RenewLabelingTask(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            returned_1_0 = response_1.result.correlation_id
            if returned_1_0:
                response.result.correlation_id = returned_1_0
            returned_1_1 = response_1.result.status
            if returned_1_1:
                response.result.status = returned_1_1
            returned_2_0 = response_2.result.message
            if returned_2_0:
                response.outcome.message = returned_2_0
            echoed_0 = request.annotation_id
            response.annotation.annotation_id = echoed_0
            echoed_1 = request.annotation.subject
            response.annotation.subject.CopyFrom(echoed_1)
            return response

    async def handle_retry_annotation_workflow(
        self,
        request: labeling_v1_annotation_workflow_service_pb2.RetryAnnotationWorkflowRequest
    ) -> labeling_v1_annotation_workflow_service_pb2.RetryAnnotationWorkflowResponse:
        """Retrys an annotation."""
        deps = self.deps
        response = labeling_v1_annotation_workflow_service_pb2.RetryAnnotationWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('RetryAnnotationWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'RetryAnnotationWorkflow',
                {'reason': request.reason}
            )
            await deps.repository.save_annotation(request.context.tenant_id, request.annotation)
            response_0 = concessions_v1_concession_stand_service_pb2.SearchConcessionStandsResponse()
            response_1 = metrics_v1_metric_alert_export_service_pb2.StreamMetricAlertExportResponse()
            response_2 = labeling_v1_annotation_lifecycle_service_pb2.GetAnnotationLifecycleResponse()
            outgoing_0 = concessions_v1_concession_stand_service_pb2.SearchConcessionStandsRequest()
            outgoing_0.context.CopyFrom(request.context)
            outgoing_0.filter.created_after.CopyFrom(request.annotation.occurred_at)
            outgoing_0.filter.owner_id = request.annotation.subject.labeling_task_id
            merged_0 = concessions_v1_concession_stand_service_pb2.SearchConcessionStandsRequest()
            merged_0.MergeFrom(outgoing_0)
            outgoing_0.CopyFrom(merged_0)
            response_0 = await deps.clients.concessions_concession_stand.SearchConcessionStands(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = metrics_v1_metric_alert_export_service_pb2.StreamMetricAlertExportRequest(
                context=request.context,
                filter=metrics_v1_metric_alert_export_service_pb2.StreamMetricAlertExportRequest.Filter(
                    created_after=request.annotation.occurred_at,
                    labels=dict(response_0.result.details),
                    owner_id=request.annotation.subject.labeling_task_id
                )
            )
            async for chunk_1 in deps.clients.metrics_metric_alert_export.StreamMetricAlertExport(
                outgoing_1,
                timeout=deps.settings.timeout
            ):
                response_1 = chunk_1
            outgoing_2 = labeling_v1_annotation_lifecycle_service_pb2.GetAnnotationLifecycleRequest(
                annotation_id=request.annotation.annotation_id,
                context=request.context
            )
            registered_2 = cast(
                labeling_v1_annotation_lifecycle_service_pb2_grpc.AnnotationLifecycleServiceStub,
                deps.clients.registry['acme.labeling.v1.AnnotationLifecycleService']
            )
            response_2 = await registered_2.GetAnnotationLifecycle(outgoing_2, timeout=deps.settings.timeout)
            returned_0_0 = response_0.result.status
            if returned_0_0:
                response.outcome.status = returned_0_0
            returned_2_0 = response_2.result.correlation_id
            if returned_2_0:
                response.annotation.correlation_id = returned_2_0
            returned_2_1 = response_2.result.status
            if returned_2_1:
                response.outcome.status = returned_2_1
            echoed_0 = request.annotation_id
            response.annotation.annotation_id = echoed_0
            echoed_1 = request.annotation.occurred_at
            response.annotation.occurred_at.CopyFrom(echoed_1)
            return response

    async def handle_signal_annotation_workflow(
        self,
        request: labeling_v1_annotation_workflow_service_pb2.SignalAnnotationWorkflowRequest
    ) -> labeling_v1_annotation_workflow_service_pb2.SignalAnnotationWorkflowResponse:
        """Signals an annotation."""
        deps = self.deps
        response = labeling_v1_annotation_workflow_service_pb2.SignalAnnotationWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SignalAnnotationWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'SignalAnnotationWorkflow',
                {'reason': request.reason}
            )
            await deps.repository.save_annotation(request.context.tenant_id, request.annotation)
            response_0 = labeling_v1_labeling_task_query_service_pb2.SuggestLabelingTasksResponse()
            response_1 = notifications_v1_notification_validation_service_pb2.ValidateNotificationResponse()
            outgoing_0 = labeling_v1_labeling_task_query_service_pb2.SuggestLabelingTasksRequest(
                context=request.context,
                filter=labeling_v1_labeling_task_query_service_pb2.SuggestLabelingTasksRequest.Filter(
                    created_after=request.annotation.occurred_at,
                    owner_id=request.annotation.subject.labeling_task_id
                )
            )
            outgoing_1 = notifications_v1_notification_validation_service_pb2.ValidateNotificationRequest(
                context=request.context,
                details=notifications_v1_notification_validation_service_pb2.ValidateNotificationRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(phone=request.details.notify.phone)
                ),
                notification=notifications_v1_notifications_pb2.Notification(
                    priority=request.annotation.subject.priority,
                    requester=common_v1_contact_pb2.ContactInfo(email=request.details.notify.email)
                )
            )
            response_0, response_1 = await asyncio.gather(
                deps.clients.labeling_labeling_task_query.SuggestLabelingTasks(
                    outgoing_0,
                    timeout=deps.settings.timeout
                ),
                deps.clients.notifications_notification_validation.ValidateNotification(
                    outgoing_1,
                    timeout=deps.settings.timeout
                ),
            )
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.result.message = returned_0_0
            returned_0_1 = response_0.result.status
            if returned_0_1:
                response.outcome.status = returned_0_1
            returned_1_0 = response_1.outcome.reference_id
            if returned_1_0:
                response.outcome.reference_id = returned_1_0
            returned_1_1 = response_1.outcome.status
            if returned_1_1:
                response.result.status = returned_1_1
            echoed_0 = request.annotation_id
            response.annotation.annotation_id = echoed_0
            echoed_1 = request.annotation.correlation_id
            response.result.correlation_id = echoed_1
            return response

    async def handle_start_annotation_workflow(
        self,
        request: labeling_v1_annotation_workflow_service_pb2.StartAnnotationWorkflowRequest
    ) -> labeling_v1_annotation_workflow_service_pb2.StartAnnotationWorkflowResponse:
        """Starts an annotation."""
        deps = self.deps
        response = labeling_v1_annotation_workflow_service_pb2.StartAnnotationWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('StartAnnotationWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'StartAnnotationWorkflow',
                {'reason': request.reason}
            )
            await deps.repository.save_annotation(request.context.tenant_id, request.annotation)
            response_0 = labeling_v1_labeling_task_approval_service_pb2.EscalateLabelingTaskResponse()
            outgoing_0 = labeling_v1_labeling_task_approval_service_pb2.EscalateLabelingTaskRequest(
                context=request.context,
                labeling_task=labeling_v1_labeling_pb2.LabelingTask(
                    assignee=identity_v1_refs_pb2.UserRef(email=request.details.notify.email),
                    customer=labeling_v1_refs_pb2.LabelSetRef(display_name=request.annotation.subject.display_name)
                )
            )
            send_0 = partial(
                deps.clients.labeling_labeling_task_approval.EscalateLabelingTask,
                timeout=deps.settings.timeout
            )
            response_0 = await send_0(outgoing_0)
            returned_0_0 = response_0.result.correlation_id
            if returned_0_0:
                response.annotation.correlation_id = returned_0_0
            echoed_0 = request.annotation_id
            response.annotation.annotation_id = echoed_0
            echoed_1 = request.annotation.source
            response.annotation.source = echoed_1
            return response
