"""Application workflow for Notebook Reporting."""

from __future__ import annotations

from functools import partial
from typing import Any
from typing import cast
import logging

from google.protobuf.json_format import MessageToJson
from google.protobuf.json_format import Parse

from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.datahub.v1 import data_share_approval_service_pb2 as datahub_v1_data_share_approval_service_pb2
from acme.datahub.v1 import data_share_validation_service_pb2 as datahub_v1_data_share_validation_service_pb2
from acme.datahub.v1 import datahub_pb2 as datahub_v1_datahub_pb2
from acme.datahub.v1 import notebook_approval_service_pb2 as datahub_v1_notebook_approval_service_pb2
from acme.datahub.v1 import notebook_reporting_service_pb2 as datahub_v1_notebook_reporting_service_pb2
from acme.datahub.v1 import refs_pb2 as datahub_v1_refs_pb2
from acme.datahub.v1 import workspace_approval_service_pb2 as datahub_v1_workspace_approval_service_pb2
from acme.datahub.v1 import workspace_reporting_service_pb2 as datahub_v1_workspace_reporting_service_pb2
from acme.documents.v1 import document_query_service_pb2 as documents_v1_document_query_service_pb2
from acme.documents.v1 import document_query_service_pb2_grpc as documents_v1_document_query_service_pb2_grpc
from acme.featureflags.v1 import feature_flag_query_service_pb2 as featureflags_v1_feature_flag_query_service_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.identity.v1 import user_query_service_pb2 as identity_v1_user_query_service_pb2
from acme.metrics.v1 import metric_alert_validation_service_pb2 as metrics_v1_metric_alert_validation_service_pb2
from acme.notifications.v1 import (
    notification_validation_service_pb2 as notifications_v1_notification_validation_service_pb2,
)
from acme.notifications.v1 import notifications_pb2 as notifications_v1_notifications_pb2
from acme.notifications.v1 import refs_pb2 as notifications_v1_refs_pb2
from acme.recommendations.v1 import (
    recommendation_model_workflow_service_pb2 as recommendations_v1_recommendation_model_workflow_service_pb2,
)
from acme.recommendations.v1 import recommendations_pb2 as recommendations_v1_recommendations_pb2

from acme_data.domains.datahub import hooks
from acme_data.domains.datahub.adapters import NotebookReportingDeleteNotebookReport1Adapter
from acme_data.domains.datahub.adapters import NotebookReportingStreamNotebookMetrics0Adapter
from acme_data.domains.datahub.adapters import NotebookReportingStreamNotebookMetrics0Port
from acme_data.domains.datahub.dependencies import Dependencies
from acme_data.domains.datahub.models import NotebookReportingScheduleNotebookReport1Command
from acme_data.domains.datahub.models import to_notebook_reporting_schedule_notebook_report1_command
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import run_steps
from acme_data.platform.tenancy import tenant_id
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class NotebookReportingServicerWorkflow:
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    async def handle_count_notebook_totals(
        self,
        request: datahub_v1_notebook_reporting_service_pb2.CountNotebookTotalsRequest
    ) -> datahub_v1_notebook_reporting_service_pb2.CountNotebookTotalsResponse:
        """Counts notebooks by status."""
        deps = self.deps
        response = datahub_v1_notebook_reporting_service_pb2.CountNotebookTotalsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CountNotebookTotals', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'CountNotebookTotals',
                {'order_by': request.order_by}
            )
            return response

    async def handle_delete_notebook_report(
        self,
        request: datahub_v1_notebook_reporting_service_pb2.DeleteNotebookReportRequest
    ) -> datahub_v1_notebook_reporting_service_pb2.DeleteNotebookReportResponse:
        """Deletes a notebook."""
        deps = self.deps
        response = datahub_v1_notebook_reporting_service_pb2.DeleteNotebookReportResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('DeleteNotebookReport', extra={'fields': {'etag': request.etag}})
            await deps.repository.audit(request.context.tenant_id, 'DeleteNotebookReport', {'etag': request.etag})
            response_0 = notifications_v1_notification_validation_service_pb2.ScoreNotificationResponse()
            response_1 = datahub_v1_notebook_approval_service_pb2.EscalateNotebookResponse()
            response_2 = notifications_v1_notification_validation_service_pb2.LintNotificationsResponse()
            outgoing_0 = notifications_v1_notification_validation_service_pb2.ScoreNotificationRequest(
                context=request.context,
                notification=notifications_v1_notifications_pb2.Notification(
                    requester=common_v1_contact_pb2.ContactInfo(email=request.context.actor.email)
                ),
                reason=request.reason
            )
            steps_0 = [
                partial(
                    deps.clients.notifications_notification_validation.ScoreNotification,
                    outgoing_0,
                    timeout=deps.settings.timeout
                )
            ]
            results_0 = await run_steps(steps_0)
            response_0 = results_0[-1]
            outgoing_1 = datahub_v1_notebook_approval_service_pb2.EscalateNotebookRequest(
                context=request.context,
                details=datahub_v1_notebook_approval_service_pb2.EscalateNotebookRequest.Details(
                    approver=identity_v1_refs_pb2.UserRef(display_name=response_0.notification.customer.display_name)
                ),
                notebook=datahub_v1_datahub_pb2.Notebook(
                    audit=common_v1_audit_pb2.AuditInfo(updated_by=response_0.notification.audit.updated_by)
                )
            )
            response_1 = await NotebookReportingDeleteNotebookReport1Adapter(
                deps.clients.datahub_notebook_approval,
                deps.settings.timeout
            )(outgoing_1)
            outgoing_2 = notifications_v1_notification_validation_service_pb2.LintNotificationsRequest(
                context=request.context,
                notification=notifications_v1_notifications_pb2.Notification(
                    customer=notifications_v1_refs_pb2.NotificationTemplateRef(
                        display_name=response_0.notification.customer.display_name
                    )
                )
            )
            response_2 = cast(notifications_v1_notification_validation_service_pb2.LintNotificationsResponse, await deps.bus.request(
                'acme.datahub.v1.NotebookReportingService/DeleteNotebookReport/2', outgoing_2, deps.settings.timeout,
            ))
            returned_0_0 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_0)
            returned_1_0 = response_1.outcome.message
            if returned_1_0:
                response.result.message = returned_1_0
            returned_1_1 = response_1.result.correlation_id
            if returned_1_1:
                response.result.correlation_id = returned_1_1
            returned_2_0 = response_2.outcome.effective_at
            if returned_2_0.ListFields():
                response.effective_at.MergeFrom(returned_2_0)
            return response

    async def handle_fetch_notebook_report(
        self,
        request: datahub_v1_notebook_reporting_service_pb2.FetchNotebookReportRequest
    ) -> datahub_v1_notebook_reporting_service_pb2.FetchNotebookReportResponse:
        """Returns a notebook."""
        deps = self.deps
        response = datahub_v1_notebook_reporting_service_pb2.FetchNotebookReportResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('FetchNotebookReport', extra={'fields': {'domain': 'datahub'}})
            await deps.repository.audit(request.context.tenant_id, 'FetchNotebookReport', {})
            response_0 = datahub_v1_notebook_approval_service_pb2.RejectNotebookResponse()
            response_1 = featureflags_v1_feature_flag_query_service_pb2.CountFeatureFlagsResponse()
            outgoing_0 = datahub_v1_notebook_approval_service_pb2.RejectNotebookRequest(
                context=request.context,
                notebook_id=request.notebook_id
            )
            response_0 = await deps.clients.datahub_notebook_approval.RejectNotebook(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = featureflags_v1_feature_flag_query_service_pb2.CountFeatureFlagsRequest(
                context=request.context,
                filter=featureflags_v1_feature_flag_query_service_pb2.CountFeatureFlagsRequest.Filter(
                    created_after=response_0.notebook.issued_at,
                    labels=dict(response_0.notebook.metadata),
                    owner_id=response_0.notebook.notebook_id,
                    region=response_0.notebook.billing_address.region
                )
            )
            method_name_1 = 'CountFeatureFlags'
            response_1 = await getattr(
                deps.clients.featureflags_feature_flag_query,
                method_name_1
            )(outgoing_1, timeout=deps.settings.timeout)
            returned_0_0 = response_0.result.status
            if returned_0_0:
                response.result.status = returned_0_0
            returned_1_0 = response_1.result.details
            response.result.details.update(returned_1_0)
            echoed_0 = request.notebook_id
            response.notebook.notebook_id = echoed_0
            return response

    async def handle_generate_notebook_report(
        self,
        request: datahub_v1_notebook_reporting_service_pb2.GenerateNotebookReportRequest
    ) -> datahub_v1_notebook_reporting_service_pb2.GenerateNotebookReportResponse:
        """Generates a notebook."""
        deps = self.deps
        response = datahub_v1_notebook_reporting_service_pb2.GenerateNotebookReportResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('GenerateNotebookReport', extra={'fields': {'notebook_id': request.notebook_id}})
            await deps.repository.audit(
                request.context.tenant_id,
                'GenerateNotebookReport',
                {'notebook_id': request.notebook_id}
            )
            response_0 = datahub_v1_workspace_approval_service_pb2.ApproveWorkspaceResponse()
            response_1 = datahub_v1_notebook_approval_service_pb2.RejectNotebookResponse()
            response_2 = datahub_v1_notebook_approval_service_pb2.DelegateNotebookApprovalResponse()
            response_3 = datahub_v1_notebook_approval_service_pb2.SubmitNotebookResponse()
            fields_0: dict[str, Any] = {
                'context': request.context,
                'details': {'approver': {'user_id': request.context.actor.user_id}},
                'reason': request.reason,
                'workspace': {'assignee': {'email': request.context.actor.email}}
            }
            outgoing_0 = datahub_v1_workspace_approval_service_pb2.ApproveWorkspaceRequest(**fields_0)
            response_0 = await deps.clients.datahub_workspace_approval.ApproveWorkspace(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = datahub_v1_notebook_approval_service_pb2.RejectNotebookRequest()
            outgoing_1.context.CopyFrom(request.context)
            outgoing_1.notebook.audit.created_by = response_0.workspace.audit.created_by
            if response_0.workspace.WhichOneof('origin') == 'customer':
                outgoing_1.details.approver.email = response_0.workspace.customer.email
            response_1 = await deps.clients.datahub_notebook_approval.RejectNotebook(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = datahub_v1_notebook_approval_service_pb2.DelegateNotebookApprovalRequest(
                context=request.context,
                notebook=datahub_v1_datahub_pb2.Notebook(
                    billing_address=common_v1_address_pb2.PostalAddress(
                        lines=list(response_1.notebook.billing_address.lines)
                    ),
                    card=datahub_v1_datahub_pb2.NotebookCardSettlement(
                        holder_name=response_1.notebook.card.holder_name
                    ),
                    counterparty=datahub_v1_refs_pb2.WorkspaceRef(
                        display_name=response_0.workspace.assignee.display_name
                    )
                )
            )
            document_2 = MessageToJson(outgoing_2, preserving_proto_field_name=True)
            outgoing_2 = Parse(document_2, datahub_v1_notebook_approval_service_pb2.DelegateNotebookApprovalRequest())
            response_2 = await deps.clients.datahub_notebook_approval.DelegateNotebookApproval(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            outgoing_3 = datahub_v1_notebook_approval_service_pb2.SubmitNotebookRequest()
            outgoing_3.context.CopyFrom(request.context)
            outgoing_3.notebook.audit.created_by = response_2.notebook.audit.created_by
            merged_3 = datahub_v1_notebook_approval_service_pb2.SubmitNotebookRequest()
            merged_3.MergeFrom(outgoing_3)
            outgoing_3.CopyFrom(merged_3)
            response_3 = await deps.clients.datahub_notebook_approval.SubmitNotebook(
                outgoing_3,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.outcome.message
            if returned_0_0:
                response.result.message = returned_0_0
            returned_1_0 = response_1.result.details
            response.result.details.update(returned_1_0)
            returned_2_0 = response_2.result.reference_ids
            response.result.reference_ids.extend(returned_2_0)
            returned_3_0 = response_3.result.details
            response.result.details.update(returned_3_0)
            echoed_0 = request.details.period
            response.period.CopyFrom(echoed_0)
            return response

    async def handle_list_notebook_reports(
        self,
        request: datahub_v1_notebook_reporting_service_pb2.ListNotebookReportsRequest
    ) -> datahub_v1_notebook_reporting_service_pb2.ListNotebookReportsResponse:
        """Lists notebooks a page at a time."""
        deps = self.deps
        response = datahub_v1_notebook_reporting_service_pb2.ListNotebookReportsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ListNotebookReports', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ListNotebookReports',
                {'order_by': request.order_by}
            )
            response_0 = datahub_v1_data_share_approval_service_pb2.ApproveDataShareResponse()
            outgoing_0 = datahub_v1_data_share_approval_service_pb2.ApproveDataShareRequest(
                context=request.context,
                data_share=datahub_v1_datahub_pb2.DataShare(
                    billing_address=common_v1_address_pb2.PostalAddress(region=request.filter.region)
                )
            )
            response_0 = await deps.clients.datahub_data_share_approval.ApproveDataShare(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.outcome.message
            if returned_0_0:
                response.result.message = returned_0_0
            return response

    async def handle_schedule_notebook_report(
        self,
        request: datahub_v1_notebook_reporting_service_pb2.ScheduleNotebookReportRequest
    ) -> datahub_v1_notebook_reporting_service_pb2.ScheduleNotebookReportResponse:
        """Schedules a notebook."""
        deps = self.deps
        response = datahub_v1_notebook_reporting_service_pb2.ScheduleNotebookReportResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ScheduleNotebookReport', extra={'fields': {'cron': request.details.cron}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ScheduleNotebookReport',
                {'cron': request.details.cron}
            )
            response_0 = documents_v1_document_query_service_pb2.SummarizeDocumentsResponse()
            response_1 = datahub_v1_notebook_approval_service_pb2.ApproveNotebookResponse()
            response_2 = datahub_v1_data_share_validation_service_pb2.ScoreDataShareResponse()
            outgoing_0 = documents_v1_document_query_service_pb2.SummarizeDocumentsRequest(
                context=request.context,
                details=documents_v1_document_query_service_pb2.SummarizeDocumentsRequest.Details(
                    format=request.details.format,
                    period=request.details.period
                )
            )
            registered_0 = cast(
                documents_v1_document_query_service_pb2_grpc.DocumentQueryServiceStub,
                deps.clients.registry['acme.documents.v1.DocumentQueryService']
            )
            response_0 = await registered_0.SummarizeDocuments(outgoing_0, timeout=deps.settings.timeout)
            command_1 = NotebookReportingScheduleNotebookReport1Command(
                context=request.context,
                annotations=dict(request.annotations),
                reason=request.reason,
                notebook_notebook_id=request.notebook_id,
                details_approver_email=request.context.actor.email
            )
            outgoing_1 = to_notebook_reporting_schedule_notebook_report1_command(command_1)
            response_1 = await deps.clients.datahub_notebook_approval.ApproveNotebook(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = datahub_v1_data_share_validation_service_pb2.ScoreDataShareRequest()
            outgoing_2.context.CopyFrom(request.context)
            outgoing_2.data_share.audit.etag = response_1.notebook.audit.etag
            if response_1.notebook.WhichOneof('settlement') == 'card':
                outgoing_2.data_share.card.network = response_1.notebook.card.network
            response_2 = await deps.clients.datahub_data_share_validation.ScoreDataShare(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_0)
            returned_1_0 = response_1.result.status
            if returned_1_0:
                response.result.status = returned_1_0
            returned_1_1 = response_1.result.reference_ids
            response.result.reference_ids.extend(returned_1_1)
            returned_2_0 = response_2.result.reference_ids
            response.result.reference_ids.extend(returned_2_0)
            returned_2_1 = response_2.result.message
            if returned_2_1:
                response.result.message = returned_2_1
            echoed_0 = request.details.period
            response.period.CopyFrom(echoed_0)
            return response

    async def handle_share_notebook_report(
        self,
        request: datahub_v1_notebook_reporting_service_pb2.ShareNotebookReportRequest
    ) -> datahub_v1_notebook_reporting_service_pb2.ShareNotebookReportResponse:
        """Shares a notebook."""
        deps = self.deps
        response = datahub_v1_notebook_reporting_service_pb2.ShareNotebookReportResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ShareNotebookReport', extra={'fields': {'channel': request.details.channel}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ShareNotebookReport',
                {'channel': request.details.channel}
            )
            response_0 = datahub_v1_notebook_approval_service_pb2.CommentNotebookApprovalResponse()
            response_1 = identity_v1_user_query_service_pb2.FindUsersResponse()
            response_2 = metrics_v1_metric_alert_validation_service_pb2.ScoreMetricAlertResponse()
            outgoing_0 = datahub_v1_notebook_approval_service_pb2.CommentNotebookApprovalRequest(
                annotations=dict(request.annotations),
                context=request.context,
                details=datahub_v1_notebook_approval_service_pb2.CommentNotebookApprovalRequest.Details(
                    approver=identity_v1_refs_pb2.UserRef(email=request.details.recipient.email)
                ),
                notebook=datahub_v1_datahub_pb2.Notebook(notebook_id=request.notebook_id),
                reason=request.reason
            )
            send_0 = partial(
                deps.clients.datahub_notebook_approval.CommentNotebookApproval,
                timeout=deps.settings.timeout
            )
            response_0 = await send_0(outgoing_0)
            outgoing_1 = identity_v1_user_query_service_pb2.FindUsersRequest(
                context=request.context,
                filter=identity_v1_user_query_service_pb2.FindUsersRequest.Filter(
                    region=response_0.notebook.billing_address.region
                )
            )
            response_1 = await hooks.notebook_reporting_share_notebook_report1(
                deps.clients.identity_user_query,
                outgoing_1,
                deps.settings.timeout
            )
            outgoing_2 = metrics_v1_metric_alert_validation_service_pb2.ScoreMetricAlertRequest()
            outgoing_2.context.CopyFrom(request.context)
            outgoing_2.metric_alert.audit.updated_at.CopyFrom(response_0.notebook.audit.updated_at)
            outgoing_2.context.tenant_id = tenant_id.get()
            response_2 = await deps.clients.metrics_metric_alert_validation.ScoreMetricAlert(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.notebook.total
            if returned_0_0.ListFields():
                response.notebook.total.MergeFrom(returned_0_0)
            returned_0_1 = response_0.result.message
            if returned_0_1:
                response.result.message = returned_0_1
            returned_1_0 = response_1.result.message
            if returned_1_0:
                response.result.message = returned_1_0
            returned_2_0 = response_2.result.status
            if returned_2_0:
                response.result.status = returned_2_0
            returned_2_1 = response_2.metric_alert.discount.amount
            returned_2_1_part_1 = response.notebook.lines.add()
            if returned_2_1.ListFields():
                returned_2_1_part_1.amount.MergeFrom(returned_2_1)
            echoed_0 = request.notebook_id
            response.notebook.notebook_id = echoed_0
            return response

    async def handle_stream_notebook_metrics(
        self,
        request: datahub_v1_notebook_reporting_service_pb2.StreamNotebookMetricsRequest
    ) -> datahub_v1_notebook_reporting_service_pb2.StreamNotebookMetricsResponse:
        """Streams the changes of notebooks as they happen."""
        deps = self.deps
        response = datahub_v1_notebook_reporting_service_pb2.StreamNotebookMetricsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('StreamNotebookMetrics', extra={'fields': {'max_events': request.max_events}})
            await deps.repository.audit(
                request.context.tenant_id,
                'StreamNotebookMetrics',
                {'max_events': request.max_events}
            )
            response_0 = datahub_v1_workspace_reporting_service_pb2.ShareWorkspaceReportResponse()
            response_1 = recommendations_v1_recommendation_model_workflow_service_pb2.CancelRecommendationModelWorkflowResponse()
            response_2 = featureflags_v1_feature_flag_query_service_pb2.ExportFeatureFlagsResponse()
            outgoing_0 = datahub_v1_workspace_reporting_service_pb2.ShareWorkspaceReportRequest(
                context=request.context,
                details=datahub_v1_workspace_reporting_service_pb2.ShareWorkspaceReportRequest.Details(
                    recipient=common_v1_contact_pb2.ContactInfo(
                        email=request.subscriber.email,
                        name=request.subscriber.name,
                        phone=request.subscriber.phone
                    )
                )
            )
            port_0: NotebookReportingStreamNotebookMetrics0Port = NotebookReportingStreamNotebookMetrics0Adapter(
                deps.clients.datahub_workspace_reporting,
                deps.settings.timeout
            )
            response_0 = await port_0.execute(outgoing_0)
            outgoing_1 = recommendations_v1_recommendation_model_workflow_service_pb2.CancelRecommendationModelWorkflowRequest(
                context=request.context,
                recommendation_model=recommendations_v1_recommendations_pb2.RecommendationModel(
                    audit=common_v1_audit_pb2.AuditInfo(created_at=response_0.workspace.audit.created_at),
                    owner=identity_v1_refs_pb2.UserRef(email=response_0.workspace.requester.email)
                )
            )
            steps_1 = [
                partial(
                    deps.clients.recommendations_recommendation_model_workflow.CancelRecommendationModelWorkflow,
                    outgoing_1,
                    timeout=deps.settings.timeout
                )
            ]
            results_1 = await run_steps(steps_1)
            response_1 = results_1[-1]
            outgoing_2 = featureflags_v1_feature_flag_query_service_pb2.ExportFeatureFlagsRequest(
                context=request.context,
                filter=featureflags_v1_feature_flag_query_service_pb2.ExportFeatureFlagsRequest.Filter(
                    region=response_1.recommendation_model.address.region
                )
            )
            async for chunk_2 in deps.clients.featureflags_feature_flag_query.ExportFeatureFlags(
                outgoing_2,
                timeout=deps.settings.timeout
            ):
                response_2 = chunk_2
            returned_0_0 = response_0.workspace.assignee.display_name
            if returned_0_0:
                response.notebook.counterparty.display_name = returned_0_0
            returned_1_0 = response_1.recommendation_model.audit.created_at
            if returned_1_0.ListFields():
                response.notebook.audit.created_at.MergeFrom(returned_1_0)
            echoed_0 = request.filter.region
            response.notebook.billing_address.region = echoed_0
            return response
