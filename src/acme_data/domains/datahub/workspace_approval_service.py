"""Routes workspaces through approval, with escalation and delegation."""

from __future__ import annotations

from collections.abc import AsyncIterator
from collections.abc import Awaitable
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any
from typing import cast
import asyncio
import logging

from google.protobuf.any_pb2 import Any as AnyMessage
from google.protobuf.json_format import MessageToDict
from google.protobuf.json_format import ParseDict
import grpc

from acme.analytics.v1 import (
    analytics_report_approval_service_pb2 as analytics_v1_analytics_report_approval_service_pb2,
)
from acme.anomalies.v1 import anomalies_pb2 as anomalies_v1_anomalies_pb2
from acme.anomalies.v1 import detector_workflow_service_pb2 as anomalies_v1_detector_workflow_service_pb2
from acme.authorization.v1 import access_policy_service_pb2 as authorization_v1_access_policy_service_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.customers.v1 import consent_record_approval_service_pb2 as customers_v1_consent_record_approval_service_pb2
from acme.customers.v1 import (
    customer_segment_approval_service_pb2 as customers_v1_customer_segment_approval_service_pb2,
)
from acme.customers.v1 import customers_pb2 as customers_v1_customers_pb2
from acme.customers.v1 import preference_calculation_service_pb2 as customers_v1_preference_calculation_service_pb2
from acme.customers.v1 import refs_pb2 as customers_v1_refs_pb2
from acme.datahub.v1 import workspace_approval_service_pb2 as datahub_v1_workspace_approval_service_pb2
from acme.datahub.v1 import workspace_approval_service_pb2_grpc as datahub_v1_workspace_approval_service_pb2_grpc
from acme.edgegateway.v1 import route_binding_service_pb2 as edgegateway_v1_route_binding_service_pb2
from acme.fanportal.v1 import fan_session_query_service_pb2 as fanportal_v1_fan_session_query_service_pb2
from acme.fanportal.v1 import fan_session_service_pb2 as fanportal_v1_fan_session_service_pb2
from acme.featureflags.v1 import feature_flag_service_pb2 as featureflags_v1_feature_flag_service_pb2
from acme.featureflags.v1 import featureflags_pb2 as featureflags_v1_featureflags_pb2
from acme.identity.v1 import identity_pb2 as identity_v1_identity_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.identity.v1 import user_validation_service_pb2 as identity_v1_user_validation_service_pb2
from acme.labeling.v1 import labeling_pb2 as labeling_v1_labeling_pb2
from acme.labeling.v1 import labeling_task_approval_service_pb2 as labeling_v1_labeling_task_approval_service_pb2
from acme.metrics.v1 import metric_alert_validation_service_pb2 as metrics_v1_metric_alert_validation_service_pb2
from acme.metrics.v1 import metrics_pb2 as metrics_v1_metrics_pb2
from acme.pipelines.v1 import pipeline_run_reporting_service_pb2 as pipelines_v1_pipeline_run_reporting_service_pb2

from acme_data.domains.datahub import hooks
from acme_data.domains.datahub.adapters import WorkspaceApprovalCommentWorkspaceApproval2Adapter
from acme_data.domains.datahub.adapters import WorkspaceApprovalCommentWorkspaceApproval2Port
from acme_data.domains.datahub.adapters import WorkspaceApprovalDelegateWorkspaceApproval1Adapter
from acme_data.domains.datahub.dependencies import Dependencies
from acme_data.domains.datahub.models import WorkspaceApprovalSubmitWorkspace2Command
from acme_data.domains.datahub.models import to_workspace_approval_submit_workspace2_command
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


@dataclass(slots=True)
class WorkspaceApprovalServicer(datahub_v1_workspace_approval_service_pb2_grpc.WorkspaceApprovalServiceServicer):
    deps: Dependencies

    @rpc_errors
    async def ApproveWorkspace(
        self, request: datahub_v1_workspace_approval_service_pb2.ApproveWorkspaceRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_workspace_approval_service_pb2.ApproveWorkspaceResponse:
        """Approves a workspace."""
        return await self.handle_approve_workspace(request)

    @rpc_errors
    async def CommentWorkspaceApproval(
        self, request: datahub_v1_workspace_approval_service_pb2.CommentWorkspaceApprovalRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_workspace_approval_service_pb2.CommentWorkspaceApprovalResponse:
        """Comments a workspace."""
        return await self.handle_comment_workspace_approval(request)

    @rpc_errors
    async def DelegateWorkspaceApproval(
        self, request: datahub_v1_workspace_approval_service_pb2.DelegateWorkspaceApprovalRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_workspace_approval_service_pb2.DelegateWorkspaceApprovalResponse:
        """Delegates a workspace."""
        return await self.handle_delegate_workspace_approval(request)

    @rpc_errors
    async def EscalateWorkspace(
        self, request: datahub_v1_workspace_approval_service_pb2.EscalateWorkspaceRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_workspace_approval_service_pb2.EscalateWorkspaceResponse:
        """Escalates a workspace."""
        return await self.handle_escalate_workspace(request)

    @rpc_errors
    async def RecallWorkspace(
        self, request: datahub_v1_workspace_approval_service_pb2.RecallWorkspaceRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_workspace_approval_service_pb2.RecallWorkspaceResponse:
        """Recalls a workspace."""
        return await self.handle_recall_workspace(request)

    @rpc_errors
    async def SubmitWorkspace(
        self, request: datahub_v1_workspace_approval_service_pb2.SubmitWorkspaceRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_workspace_approval_service_pb2.SubmitWorkspaceResponse:
        """Submits a workspace."""
        return await self.handle_submit_workspace(request)

    async def handle_approve_workspace(
        self,
        request: datahub_v1_workspace_approval_service_pb2.ApproveWorkspaceRequest
    ) -> datahub_v1_workspace_approval_service_pb2.ApproveWorkspaceResponse:
        """Approves a workspace."""
        deps = self.deps
        response = datahub_v1_workspace_approval_service_pb2.ApproveWorkspaceResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ApproveWorkspace', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'ApproveWorkspace', {'reason': request.reason})
            await deps.repository.save_workspace(request.context.tenant_id, request.workspace)
            response_0 = customers_v1_consent_record_approval_service_pb2.ListPendingConsentRecordsResponse()
            response_1 = fanportal_v1_fan_session_query_service_pb2.FindFanSessionsResponse()
            outgoing_0 = customers_v1_consent_record_approval_service_pb2.ListPendingConsentRecordsRequest(
                context=request.context,
                filter=customers_v1_consent_record_approval_service_pb2.ListPendingConsentRecordsRequest.Filter(
                    created_after=request.workspace.sla.due_at,
                    labels=dict(request.annotations),
                    owner_id=request.workspace.customer.customer_id
                )
            )
            outgoing_1 = fanportal_v1_fan_session_query_service_pb2.FindFanSessionsRequest(
                context=request.context,
                filter=fanportal_v1_fan_session_query_service_pb2.FindFanSessionsRequest.Filter(
                    created_after=request.workspace.audit.updated_at,
                    labels=dict(request.workspace.custom_fields),
                    owner_id=request.workspace.customer.customer_id
                )
            )
            response_0, response_1 = await asyncio.gather(
                deps.clients.customers_consent_record_approval.ListPendingConsentRecords(
                    outgoing_0,
                    timeout=deps.settings.timeout
                ),
                deps.clients.fanportal_fan_session_query.FindFanSessions(outgoing_1, timeout=deps.settings.timeout),
            )
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.outcome.message = returned_0_0
            returned_1_0 = response_1.result.reference_ids
            response.result.reference_ids.extend(returned_1_0)
            echoed_0 = request.workspace_id
            response.workspace.workspace_id = echoed_0
            echoed_1 = request.workspace.subject
            response.workspace.subject = echoed_1
            return response

    async def handle_comment_workspace_approval(
        self,
        request: datahub_v1_workspace_approval_service_pb2.CommentWorkspaceApprovalRequest
    ) -> datahub_v1_workspace_approval_service_pb2.CommentWorkspaceApprovalResponse:
        """Comments a workspace."""
        deps = self.deps
        response = datahub_v1_workspace_approval_service_pb2.CommentWorkspaceApprovalResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CommentWorkspaceApproval', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'CommentWorkspaceApproval',
                {'reason': request.reason}
            )
            await deps.repository.save_workspace(request.context.tenant_id, request.workspace)
            response_0 = customers_v1_consent_record_approval_service_pb2.RecallConsentRecordResponse()
            response_1 = customers_v1_customer_segment_approval_service_pb2.EscalateCustomerSegmentResponse()
            response_2 = analytics_v1_analytics_report_approval_service_pb2.CommentAnalyticsReportApprovalResponse()
            outgoing_0 = customers_v1_consent_record_approval_service_pb2.RecallConsentRecordRequest(
                consent_record=customers_v1_customers_pb2.ConsentRecord(
                    subject=customers_v1_refs_pb2.HouseholdRef(display_name=request.details.approver.display_name)
                ),
                context=request.context,
                details=customers_v1_consent_record_approval_service_pb2.RecallConsentRecordRequest.Details(
                    approver=identity_v1_refs_pb2.UserRef(email=request.workspace.assignee.email)
                )
            )
            response_0 = await hooks.workspace_approval_comment_workspace_approval0(
                deps.clients.customers_consent_record_approval,
                outgoing_0,
                deps.settings.timeout
            )
            for item_1 in request.workspace.history:
                outgoing_1 = customers_v1_customer_segment_approval_service_pb2.EscalateCustomerSegmentRequest(
                    context=request.context,
                    customer_segment=customers_v1_customers_pb2.CustomerSegment(
                        audit=common_v1_audit_pb2.AuditInfo(
                            created_at=item_1.changed_at,
                            updated_by=request.workspace.audit.updated_by
                        ),
                        owner=identity_v1_refs_pb2.UserRef(email=request.workspace.requester.email)
                    )
                )
                response_1 = await deps.clients.customers_customer_segment_approval.EscalateCustomerSegment(
                    outgoing_1,
                    timeout=deps.settings.timeout
                )
            outgoing_2 = analytics_v1_analytics_report_approval_service_pb2.CommentAnalyticsReportApprovalRequest(
                context=request.context,
                details=analytics_v1_analytics_report_approval_service_pb2.CommentAnalyticsReportApprovalRequest.Details(
                    approver=identity_v1_refs_pb2.UserRef(email=request.details.approver.email)
                )
            )
            port_2: WorkspaceApprovalCommentWorkspaceApproval2Port = WorkspaceApprovalCommentWorkspaceApproval2Adapter(
                deps.clients.analytics_analytics_report_approval,
                deps.settings.timeout
            )
            response_2 = await port_2.execute(outgoing_2)
            returned_0_0 = response_0.consent_record.subject.display_name
            if returned_0_0:
                response.workspace.assignee.display_name = returned_0_0
            returned_2_0 = response_2.result.message
            if returned_2_0:
                response.result.message = returned_2_0
            echoed_0 = request.workspace_id
            response.workspace.workspace_id = echoed_0
            echoed_1 = request.workspace.status
            response.workspace.status = echoed_1
            return response

    async def handle_delegate_workspace_approval(
        self,
        request: datahub_v1_workspace_approval_service_pb2.DelegateWorkspaceApprovalRequest
    ) -> datahub_v1_workspace_approval_service_pb2.DelegateWorkspaceApprovalResponse:
        """Delegates a workspace."""
        deps = self.deps
        response = datahub_v1_workspace_approval_service_pb2.DelegateWorkspaceApprovalResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('DelegateWorkspaceApproval', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'DelegateWorkspaceApproval',
                {'reason': request.reason}
            )
            await deps.repository.save_workspace(request.context.tenant_id, request.workspace)
            response_0 = labeling_v1_labeling_task_approval_service_pb2.ApproveLabelingTaskResponse()
            response_1 = featureflags_v1_feature_flag_service_pb2.CreateFeatureFlagResponse()
            response_2 = customers_v1_consent_record_approval_service_pb2.CommentConsentRecordApprovalResponse()
            requests_0: list[labeling_v1_labeling_task_approval_service_pb2.ApproveLabelingTaskRequest] = []
            for item_0 in request.workspace.comments:
                outgoing_0 = labeling_v1_labeling_task_approval_service_pb2.ApproveLabelingTaskRequest(
                    context=request.context,
                    labeling_task=labeling_v1_labeling_pb2.LabelingTask(
                        comments=[labeling_v1_labeling_pb2.LabelingTaskComment(author_email=item_0.author_email)]
                    )
                )
                requests_0.append(outgoing_0)
            replies_0 = await asyncio.gather(*(
                deps.clients.labeling_labeling_task_approval.ApproveLabelingTask(
                    entry,
                    timeout=deps.settings.timeout
                ) for entry in requests_0
            ))
            if replies_0:
                response_0 = replies_0[-1]
            outgoing_1 = featureflags_v1_feature_flag_service_pb2.CreateFeatureFlagRequest(
                context=request.context,
                feature_flag=featureflags_v1_featureflags_pb2.FeatureFlag(
                    audit=common_v1_audit_pb2.AuditInfo(
                        created_by=response_0.labeling_task.audit.created_by,
                        updated_at=request.workspace.audit.updated_at
                    ),
                    owner=identity_v1_refs_pb2.UserRef(display_name=request.workspace.assignee.display_name)
                )
            )
            response_1 = await WorkspaceApprovalDelegateWorkspaceApproval1Adapter(
                deps.clients.featureflags_feature_flag,
                deps.settings.timeout
            )(outgoing_1)
            outgoing_2 = customers_v1_consent_record_approval_service_pb2.CommentConsentRecordApprovalRequest(
                consent_record=customers_v1_customers_pb2.ConsentRecord(
                    subject=customers_v1_refs_pb2.HouseholdRef(display_name=request.workspace.customer.display_name)
                ),
                context=request.context,
                details=customers_v1_consent_record_approval_service_pb2.CommentConsentRecordApprovalRequest.Details(
                    approver=identity_v1_refs_pb2.UserRef(
                        display_name=response_1.feature_flag.owner.display_name,
                        email=request.workspace.requester.email
                    ),
                    comment=request.details.comment
                )
            )
            response_2 = cast(customers_v1_consent_record_approval_service_pb2.CommentConsentRecordApprovalResponse, await deps.bus.request(
                'acme.datahub.v1.WorkspaceApprovalService/DelegateWorkspaceApproval/2', outgoing_2, deps.settings.timeout,
            ))
            returned_1_0 = response_1.result.message
            if returned_1_0:
                response.result.message = returned_1_0
            returned_2_0 = response_2.result.status
            if returned_2_0:
                response.outcome.status = returned_2_0
            echoed_0 = request.workspace_id
            response.workspace.workspace_id = echoed_0
            echoed_1 = request.workspace.requester
            response.workspace.requester.CopyFrom(echoed_1)
            return response

    async def handle_escalate_workspace(
        self,
        request: datahub_v1_workspace_approval_service_pb2.EscalateWorkspaceRequest
    ) -> datahub_v1_workspace_approval_service_pb2.EscalateWorkspaceResponse:
        """Escalates a workspace."""
        deps = self.deps
        response = datahub_v1_workspace_approval_service_pb2.EscalateWorkspaceResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('EscalateWorkspace', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'EscalateWorkspace', {'reason': request.reason})
            await deps.repository.save_workspace(request.context.tenant_id, request.workspace)
            response_0 = pipelines_v1_pipeline_run_reporting_service_pb2.CountPipelineRunTotalsResponse()
            response_1 = metrics_v1_metric_alert_validation_service_pb2.ScoreMetricAlertResponse()
            response_2 = pipelines_v1_pipeline_run_reporting_service_pb2.SharePipelineRunReportResponse()
            outgoing_0 = pipelines_v1_pipeline_run_reporting_service_pb2.CountPipelineRunTotalsRequest(
                context=request.context,
                filter=pipelines_v1_pipeline_run_reporting_service_pb2.CountPipelineRunTotalsRequest.Filter(
                    created_after=request.workspace.audit.created_at,
                    owner_id=request.workspace.assignee.user_id
                )
            )
            outgoing_1 = metrics_v1_metric_alert_validation_service_pb2.ScoreMetricAlertRequest(
                context=request.context,
                metric_alert=metrics_v1_metrics_pb2.MetricAlert(
                    audit=common_v1_audit_pb2.AuditInfo(updated_by=request.workspace.audit.updated_by),
                    owner=identity_v1_refs_pb2.UserRef(
                        display_name=request.details.approver.display_name,
                        email=request.workspace.assignee.email,
                        user_id=request.workspace.assignee.user_id
                    )
                )
            )
            response_0, response_1 = await asyncio.gather(
                deps.clients.pipelines_pipeline_run_reporting.CountPipelineRunTotals(
                    outgoing_0,
                    timeout=deps.settings.timeout
                ),
                deps.clients.metrics_metric_alert_validation.ScoreMetricAlert(
                    outgoing_1,
                    timeout=deps.settings.timeout
                ),
            )
            fields_2: dict[str, Any] = {
                'context': request.context,
                'details': {
                    'channel': request.workspace.channel.channel,
                    'recipient': {
                        'email': response_1.metric_alert.owner.email,
                        'preferred_channel': request.workspace.requester.preferred_channel
                    }
                },
                'reason': response_1.metric_alert.block.reason
            }
            outgoing_2 = pipelines_v1_pipeline_run_reporting_service_pb2.SharePipelineRunReportRequest(**fields_2)
            response_2 = await deps.clients.pipelines_pipeline_run_reporting.SharePipelineRunReport(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_0)
            returned_1_0 = response_1.result.status
            if returned_1_0:
                response.outcome.status = returned_1_0
            returned_2_0 = response_2.pipeline_run.audit.created_at
            if returned_2_0.ListFields():
                response.workspace.audit.created_at.MergeFrom(returned_2_0)
            echoed_0 = request.workspace_id
            response.workspace.workspace_id = echoed_0
            echoed_1 = request.workspace.subject
            response.workspace.subject = echoed_1
            return response

    async def handle_recall_workspace(
        self,
        request: datahub_v1_workspace_approval_service_pb2.RecallWorkspaceRequest
    ) -> datahub_v1_workspace_approval_service_pb2.RecallWorkspaceResponse:
        """Recalls a workspace."""
        deps = self.deps
        response = datahub_v1_workspace_approval_service_pb2.RecallWorkspaceResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('RecallWorkspace', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'RecallWorkspace', {'reason': request.reason})
            await deps.repository.save_workspace(request.context.tenant_id, request.workspace)
            response_0 = edgegateway_v1_route_binding_service_pb2.BatchGetRouteBindingsResponse()
            response_1 = labeling_v1_labeling_task_approval_service_pb2.EscalateLabelingTaskResponse()
            response_2 = authorization_v1_access_policy_service_pb2.WatchAccessPoliciesResponse()
            response_3 = featureflags_v1_feature_flag_service_pb2.ListFeatureFlagsResponse()
            outgoing_0 = edgegateway_v1_route_binding_service_pb2.BatchGetRouteBindingsRequest(context=request.context)
            document_0 = MessageToDict(outgoing_0, preserving_proto_field_name=True)
            outgoing_0 = ParseDict(document_0, edgegateway_v1_route_binding_service_pb2.BatchGetRouteBindingsRequest())
            response_0 = await deps.clients.edgegateway_route_binding.BatchGetRouteBindings(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            callbacks_1: list[
                Callable[[], Awaitable[labeling_v1_labeling_task_approval_service_pb2.EscalateLabelingTaskResponse]]
            ] = []
            for item_1 in request.workspace.history:
                outgoing_1 = labeling_v1_labeling_task_approval_service_pb2.EscalateLabelingTaskRequest(
                    context=request.context,
                    labeling_task=labeling_v1_labeling_pb2.LabelingTask(
                        history=[
                            labeling_v1_labeling_pb2.LabelingTaskStatusChange(
                                changed_at=item_1.changed_at,
                                from_status=item_1.from_status,
                                to_status=item_1.to_status
                            )
                        ]
                    )
                )
                async def send_1(
                    payload: labeling_v1_labeling_task_approval_service_pb2.EscalateLabelingTaskRequest = outgoing_1
                ) -> labeling_v1_labeling_task_approval_service_pb2.EscalateLabelingTaskResponse:
                    return await deps.clients.labeling_labeling_task_approval.EscalateLabelingTask(
                        payload,
                        timeout=deps.settings.timeout
                    )
                callbacks_1.append(send_1)
            for callback_1 in callbacks_1:
                response_1 = await callback_1()
            outgoing_2 = authorization_v1_access_policy_service_pb2.WatchAccessPoliciesRequest(
                context=request.context,
                subscriber=common_v1_contact_pb2.ContactInfo(
                    email=response_1.labeling_task.assignee.email,
                    name=request.workspace.requester.name,
                    preferred_channel=response_1.labeling_task.requester.preferred_channel
                )
            )
            async for chunk_2 in deps.clients.authorization_access_policy.WatchAccessPolicies(
                outgoing_2,
                timeout=deps.settings.timeout
            ):
                response_2 = chunk_2
            outgoing_3 = featureflags_v1_feature_flag_service_pb2.ListFeatureFlagsRequest(
                context=request.context,
                filter=featureflags_v1_feature_flag_service_pb2.ListFeatureFlagsRequest.Filter(
                    created_after=response_1.labeling_task.sla.due_at,
                    labels=dict(response_0.result.details),
                    owner_id=request.details.approver.user_id
                )
            )
            envelope_3 = AnyMessage()
            envelope_3.Pack(outgoing_3)
            outgoing_3 = featureflags_v1_feature_flag_service_pb2.ListFeatureFlagsRequest()
            if not envelope_3.Unpack(outgoing_3):
                raise ValueError("partner envelope contains the wrong request type")
            response_3 = await deps.clients.featureflags_feature_flag.ListFeatureFlags(
                outgoing_3,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.status
            if returned_0_0:
                response.outcome.status = returned_0_0
            returned_0_1 = response_0.result.details
            response.result.details.update(returned_0_1)
            returned_3_0 = response_3.result.details
            response.result.details.update(returned_3_0)
            echoed_0 = request.workspace_id
            response.workspace.workspace_id = echoed_0
            echoed_1 = request.workspace.subject
            response.workspace.subject = echoed_1
            return response

    async def handle_submit_workspace(
        self,
        request: datahub_v1_workspace_approval_service_pb2.SubmitWorkspaceRequest
    ) -> datahub_v1_workspace_approval_service_pb2.SubmitWorkspaceResponse:
        """Submits a workspace."""
        deps = self.deps
        response = datahub_v1_workspace_approval_service_pb2.SubmitWorkspaceResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SubmitWorkspace', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'SubmitWorkspace', {'reason': request.reason})
            await deps.repository.save_workspace(request.context.tenant_id, request.workspace)
            response_0 = fanportal_v1_fan_session_service_pb2.WatchFanSessionsResponse()
            response_1 = anomalies_v1_detector_workflow_service_pb2.StartDetectorWorkflowResponse()
            response_2 = customers_v1_preference_calculation_service_pb2.EstimatePreferenceResponse()
            response_3 = identity_v1_user_validation_service_pb2.LintUsersResponse()
            outgoing_0 = fanportal_v1_fan_session_service_pb2.WatchFanSessionsRequest(
                context=request.context,
                subscriber=common_v1_contact_pb2.ContactInfo(
                    email=request.details.approver.email,
                    name=request.workspace.requester.name,
                    phone=request.workspace.requester.phone
                )
            )
            async for chunk_0 in deps.clients.fanportal_fan_session.WatchFanSessions(
                outgoing_0,
                timeout=deps.settings.timeout
            ):
                response_0 = chunk_0
            async for item_1 in async_messages(request.workspace.comments):
                outgoing_1 = anomalies_v1_detector_workflow_service_pb2.StartDetectorWorkflowRequest(
                    context=request.context,
                    detector=anomalies_v1_anomalies_pb2.Detector(
                        audit=common_v1_audit_pb2.AuditInfo(created_at=item_1.created_at),
                        owner=identity_v1_refs_pb2.UserRef(
                            email=item_1.author_email,
                            user_id=request.details.approver.user_id
                        )
                    )
                )
                response_1 = await deps.clients.anomalies_detector_workflow.StartDetectorWorkflow(
                    outgoing_1,
                    timeout=deps.settings.timeout
                )
            command_2 = WorkspaceApprovalSubmitWorkspace2Command.model_validate(
                {
                    'context': request.context,
                    'preference_owner_display_name': response_1.detector.owner.display_name,
                    'preference_audit_updated_at': response_1.detector.audit.updated_at,
                    'preference_audit_created_by': response_1.detector.audit.created_by,
                    'preference_audit_updated_by': response_1.detector.audit.updated_by
                }
            )
            outgoing_2 = to_workspace_approval_submit_workspace2_command(command_2)
            response_2 = await deps.clients.customers_preference_calculation.EstimatePreference(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            for item_3 in request.workspace.comments:
                outgoing_3 = identity_v1_user_validation_service_pb2.LintUsersRequest(
                    context=request.context,
                    user=identity_v1_identity_pb2.User(
                        audit=common_v1_audit_pb2.AuditInfo(created_at=item_3.created_at),
                        contact=common_v1_contact_pb2.ContactInfo(email=item_3.author_email),
                        relationship_manager=identity_v1_refs_pb2.UserRef(
                            display_name=response_2.preference.owner.display_name
                        )
                    )
                )
                response_3 = await deps.clients.identity_user_validation.LintUsers(
                    outgoing_3,
                    timeout=deps.settings.timeout
                )
            returned_2_0 = response_2.result.message
            if returned_2_0:
                response.outcome.message = returned_2_0
            echoed_0 = request.workspace_id
            response.workspace.workspace_id = echoed_0
            echoed_1 = request.workspace.assignee
            response.workspace.assignee.CopyFrom(echoed_1)
            return response
