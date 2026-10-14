"""Builds and schedules reports about data shares."""

from __future__ import annotations

from collections.abc import AsyncIterator
from dataclasses import dataclass
from functools import partial
from typing import cast
import asyncio
import logging

from google.protobuf.json_format import MessageToDict
from google.protobuf.json_format import MessageToJson
from google.protobuf.json_format import Parse
from google.protobuf.json_format import ParseDict
import grpc

from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.common.v1 import paging_pb2 as common_v1_paging_pb2
from acme.customers.v1 import consent_record_lifecycle_service_pb2 as customers_v1_consent_record_lifecycle_service_pb2
from acme.customers.v1 import consent_record_workflow_service_pb2 as customers_v1_consent_record_workflow_service_pb2
from acme.customers.v1 import preference_sync_service_pb2 as customers_v1_preference_sync_service_pb2
from acme.customers.v1 import refs_pb2 as customers_v1_refs_pb2
from acme.datahub.v1 import data_share_approval_service_pb2 as datahub_v1_data_share_approval_service_pb2
from acme.datahub.v1 import data_share_reporting_service_pb2 as datahub_v1_data_share_reporting_service_pb2
from acme.datahub.v1 import data_share_reporting_service_pb2_grpc as datahub_v1_data_share_reporting_service_pb2_grpc
from acme.datahub.v1 import datahub_pb2 as datahub_v1_datahub_pb2
from acme.datahub.v1 import notebook_reporting_service_pb2 as datahub_v1_notebook_reporting_service_pb2
from acme.datahub.v1 import workspace_approval_service_pb2 as datahub_v1_workspace_approval_service_pb2
from acme.datahub.v1 import workspace_reporting_service_pb2 as datahub_v1_workspace_reporting_service_pb2
from acme.datahub.v1 import workspace_reporting_service_pb2_grpc as datahub_v1_workspace_reporting_service_pb2_grpc
from acme.datahub.v1 import workspace_workflow_service_pb2 as datahub_v1_workspace_workflow_service_pb2
from acme.fanportal.v1 import fan_session_service_pb2 as fanportal_v1_fan_session_service_pb2
from acme.fanportal.v1 import fanportal_pb2 as fanportal_v1_fanportal_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.itsm.v1 import incident_service_pb2 as itsm_v1_incident_service_pb2
from acme.itsm.v1 import itsm_pb2 as itsm_v1_itsm_pb2
from acme.learning.v1 import course_query_service_pb2 as learning_v1_course_query_service_pb2
from acme.notifications.v1 import notification_service_pb2 as notifications_v1_notification_service_pb2

from acme_data.domains.datahub.adapters import DataShareReportingDeleteDataShareReport1Adapter
from acme_data.domains.datahub.adapters import DataShareReportingDeleteDataShareReport1Port
from acme_data.domains.datahub.dependencies import Dependencies
from acme_data.domains.datahub.models import DataShareReportingStreamDataShareMetrics2Command
from acme_data.domains.datahub.models import to_data_share_reporting_stream_data_share_metrics2_command
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import run_steps
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_id
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


@dataclass(slots=True)
class DataShareReportingServicer(datahub_v1_data_share_reporting_service_pb2_grpc.DataShareReportingServiceServicer):
    deps: Dependencies

    @rpc_errors
    @retry_transient
    async def CountDataShareTotals(
        self, request: datahub_v1_data_share_reporting_service_pb2.CountDataShareTotalsRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_data_share_reporting_service_pb2.CountDataShareTotalsResponse:
        """Counts data shares by status."""
        return await self.handle_count_data_share_totals(request)

    @rpc_errors
    async def DeleteDataShareReport(
        self, request: datahub_v1_data_share_reporting_service_pb2.DeleteDataShareReportRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_data_share_reporting_service_pb2.DeleteDataShareReportResponse:
        """Deletes a data share."""
        return await self.handle_delete_data_share_report(request)

    @rpc_errors
    @retry_transient
    async def FetchDataShareReport(
        self, request: datahub_v1_data_share_reporting_service_pb2.FetchDataShareReportRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_data_share_reporting_service_pb2.FetchDataShareReportResponse:
        """Returns a data share."""
        return await self.handle_fetch_data_share_report(request)

    @rpc_errors
    async def GenerateDataShareReport(
        self, request: datahub_v1_data_share_reporting_service_pb2.GenerateDataShareReportRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_data_share_reporting_service_pb2.GenerateDataShareReportResponse:
        """Generates a data share."""
        return await self.handle_generate_data_share_report(request)

    @rpc_errors
    @retry_transient
    async def ListDataShareReports(
        self, request: datahub_v1_data_share_reporting_service_pb2.ListDataShareReportsRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_data_share_reporting_service_pb2.ListDataShareReportsResponse:
        """Lists data shares a page at a time."""
        return await self.handle_list_data_share_reports(request)

    @rpc_errors
    async def ScheduleDataShareReport(
        self, request: datahub_v1_data_share_reporting_service_pb2.ScheduleDataShareReportRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_data_share_reporting_service_pb2.ScheduleDataShareReportResponse:
        """Schedules a data share."""
        return await self.handle_schedule_data_share_report(request)

    @rpc_errors
    async def ShareDataShareReport(
        self, request: datahub_v1_data_share_reporting_service_pb2.ShareDataShareReportRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_data_share_reporting_service_pb2.ShareDataShareReportResponse:
        """Shares a data share."""
        return await self.handle_share_data_share_report(request)

    @stream_errors
    async def StreamDataShareMetrics(
        self, request: datahub_v1_data_share_reporting_service_pb2.StreamDataShareMetricsRequest, context: grpc.aio.ServicerContext,
    ) -> AsyncIterator[datahub_v1_data_share_reporting_service_pb2.StreamDataShareMetricsResponse]:
        """Streams the changes of data shares as they happen."""
        response = await self.handle_stream_data_share_metrics(request)
        for item in messages((response,)):
            yield item

    async def handle_count_data_share_totals(
        self,
        request: datahub_v1_data_share_reporting_service_pb2.CountDataShareTotalsRequest
    ) -> datahub_v1_data_share_reporting_service_pb2.CountDataShareTotalsResponse:
        """Counts data shares by status."""
        deps = self.deps
        response = datahub_v1_data_share_reporting_service_pb2.CountDataShareTotalsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CountDataShareTotals', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'CountDataShareTotals',
                {'order_by': request.order_by}
            )
            response_0 = datahub_v1_workspace_reporting_service_pb2.GenerateWorkspaceReportResponse()
            outgoing_0 = datahub_v1_workspace_reporting_service_pb2.GenerateWorkspaceReportRequest(
                annotations=dict(request.context.baggage),
                context=request.context,
                details=datahub_v1_workspace_reporting_service_pb2.GenerateWorkspaceReportRequest.Details(
                    filters=dict(request.filter.labels)
                )
            )
            response_0 = await deps.clients.datahub_workspace_reporting.GenerateWorkspaceReport(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.correlation_id
            if returned_0_0:
                response.result.correlation_id = returned_0_0
            return response

    async def handle_delete_data_share_report(
        self,
        request: datahub_v1_data_share_reporting_service_pb2.DeleteDataShareReportRequest
    ) -> datahub_v1_data_share_reporting_service_pb2.DeleteDataShareReportResponse:
        """Deletes a data share."""
        deps = self.deps
        response = datahub_v1_data_share_reporting_service_pb2.DeleteDataShareReportResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('DeleteDataShareReport', extra={'fields': {'data_share_id': request.data_share_id}})
            await deps.repository.audit(
                request.context.tenant_id,
                'DeleteDataShareReport',
                {'data_share_id': request.data_share_id}
            )
            response_0 = customers_v1_preference_sync_service_pb2.PullPreferencesResponse()
            response_1 = fanportal_v1_fan_session_service_pb2.CreateFanSessionResponse()
            response_2 = customers_v1_consent_record_lifecycle_service_pb2.ScheduleConsentRecordExpiryResponse()
            outgoing_0 = customers_v1_preference_sync_service_pb2.PullPreferencesRequest()
            outgoing_0.context.CopyFrom(request.context)
            outgoing_0.preference.audit.etag = request.etag
            outgoing_0.preference.block.reason = request.reason
            outgoing_0.preference.owner.email = request.context.actor.email
            outgoing_0.context.tenant_id = tenant_id.get()
            response_0 = await deps.clients.customers_preference_sync.PullPreferences(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = fanportal_v1_fan_session_service_pb2.CreateFanSessionRequest(
                context=request.context,
                fan_session=fanportal_v1_fanportal_pb2.FanSession(
                    assignee=identity_v1_refs_pb2.UserRef(
                        display_name=response_0.preference.owner.display_name,
                        email=response_0.preference.owner.email
                    ),
                    audit=common_v1_audit_pb2.AuditInfo(updated_by=response_0.preference.audit.updated_by)
                )
            )
            port_1: DataShareReportingDeleteDataShareReport1Port = DataShareReportingDeleteDataShareReport1Adapter(
                deps.clients.fanportal_fan_session,
                deps.settings.timeout
            )
            response_1 = await port_1.execute(outgoing_1)
            outgoing_2 = customers_v1_consent_record_lifecycle_service_pb2.ScheduleConsentRecordExpiryRequest(
                context=request.context,
                details=customers_v1_consent_record_lifecycle_service_pb2.ScheduleConsentRecordExpiryRequest.Details(
                    notify=common_v1_contact_pb2.ContactInfo(
                        preferred_channel=response_1.fan_session.requester.preferred_channel
                    )
                )
            )
            steps_2 = [
                partial(
                    deps.clients.customers_consent_record_lifecycle.ScheduleConsentRecordExpiry,
                    outgoing_2,
                    timeout=deps.settings.timeout
                )
            ]
            results_2 = await run_steps(steps_2)
            response_2 = results_2[-1]
            returned_0_0 = response_0.outcome.effective_at
            if returned_0_0.ListFields():
                response.effective_at.MergeFrom(returned_0_0)
            returned_0_1 = response_0.result.details
            response.result.details.update(returned_0_1)
            returned_1_0 = response_1.result.correlation_id
            if returned_1_0:
                response.result.correlation_id = returned_1_0
            returned_2_0 = response_2.outcome.status
            if returned_2_0:
                response.result.status = returned_2_0
            returned_2_1 = response_2.result.message
            if returned_2_1:
                response.result.message = returned_2_1
            return response

    async def handle_fetch_data_share_report(
        self,
        request: datahub_v1_data_share_reporting_service_pb2.FetchDataShareReportRequest
    ) -> datahub_v1_data_share_reporting_service_pb2.FetchDataShareReportResponse:
        """Returns a data share."""
        deps = self.deps
        response = datahub_v1_data_share_reporting_service_pb2.FetchDataShareReportResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('FetchDataShareReport', extra={'fields': {'domain': 'datahub'}})
            await deps.repository.audit(request.context.tenant_id, 'FetchDataShareReport', {})
            response_0 = datahub_v1_notebook_reporting_service_pb2.StreamNotebookMetricsResponse()
            outgoing_0 = datahub_v1_notebook_reporting_service_pb2.StreamNotebookMetricsRequest(
                context=request.context,
                filter=datahub_v1_notebook_reporting_service_pb2.StreamNotebookMetricsRequest.Filter(
                    created_after=request.context.deadline,
                    labels=dict(request.context.baggage),
                    owner_id=request.context.actor.user_id
                ),
                subscriber=common_v1_contact_pb2.ContactInfo(email=request.context.actor.email)
            )
            async for chunk_0 in deps.clients.datahub_notebook_reporting.StreamNotebookMetrics(
                outgoing_0,
                timeout=deps.settings.timeout
            ):
                response_0 = chunk_0
            echoed_0 = request.data_share_id
            response.data_share.data_share_id = echoed_0
            return response

    async def handle_generate_data_share_report(
        self,
        request: datahub_v1_data_share_reporting_service_pb2.GenerateDataShareReportRequest
    ) -> datahub_v1_data_share_reporting_service_pb2.GenerateDataShareReportResponse:
        """Generates a data share."""
        deps = self.deps
        response = datahub_v1_data_share_reporting_service_pb2.GenerateDataShareReportResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('GenerateDataShareReport', extra={'fields': {'data_share_id': request.data_share_id}})
            await deps.repository.audit(
                request.context.tenant_id,
                'GenerateDataShareReport',
                {'data_share_id': request.data_share_id}
            )
            response_0 = customers_v1_consent_record_workflow_service_pb2.ResumeConsentRecordWorkflowResponse()
            response_1 = learning_v1_course_query_service_pb2.ExportCoursesResponse()
            response_2 = datahub_v1_workspace_workflow_service_pb2.ResumeWorkspaceWorkflowResponse()
            outgoing_0 = customers_v1_consent_record_workflow_service_pb2.ResumeConsentRecordWorkflowRequest(
                annotations=dict(request.annotations),
                context=request.context,
                details=customers_v1_consent_record_workflow_service_pb2.ResumeConsentRecordWorkflowRequest.Details(
                    notify=common_v1_contact_pb2.ContactInfo(email=request.context.actor.email)
                ),
                reason=request.reason
            )
            response_0 = cast(customers_v1_consent_record_workflow_service_pb2.ResumeConsentRecordWorkflowResponse, await deps.bus.request(
                'acme.datahub.v1.DataShareReportingService/GenerateDataShareReport/0', outgoing_0, deps.settings.timeout,
            ))
            outgoing_1 = learning_v1_course_query_service_pb2.ExportCoursesRequest(
                context=request.context,
                filter=learning_v1_course_query_service_pb2.ExportCoursesRequest.Filter(
                    created_after=response_0.outcome.effective_at,
                    labels=dict(request.details.filters)
                ),
                format=request.details.format
            )
            async for chunk_1 in deps.clients.learning_course_query.ExportCourses(
                outgoing_1,
                timeout=deps.settings.timeout
            ):
                response_1 = chunk_1
            outgoing_2 = datahub_v1_workspace_workflow_service_pb2.ResumeWorkspaceWorkflowRequest(
                context=request.context,
                workspace=datahub_v1_datahub_pb2.Workspace(
                    customer=customers_v1_refs_pb2.CustomerRef(
                        display_name=response_0.consent_record.subject.display_name
                    )
                )
            )
            method_name_2 = 'ResumeWorkspaceWorkflow'
            response_2 = await getattr(
                deps.clients.datahub_workspace_workflow,
                method_name_2
            )(outgoing_2, timeout=deps.settings.timeout)
            returned_0_0 = response_0.result.status
            if returned_0_0:
                response.result.status = returned_0_0
            returned_2_0 = response_2.result.reference_ids
            response.result.reference_ids.extend(returned_2_0)
            echoed_0 = request.details.period
            response.period.CopyFrom(echoed_0)
            return response

    async def handle_list_data_share_reports(
        self,
        request: datahub_v1_data_share_reporting_service_pb2.ListDataShareReportsRequest
    ) -> datahub_v1_data_share_reporting_service_pb2.ListDataShareReportsResponse:
        """Lists data shares a page at a time."""
        deps = self.deps
        response = datahub_v1_data_share_reporting_service_pb2.ListDataShareReportsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ListDataShareReports', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ListDataShareReports',
                {'order_by': request.order_by}
            )
            response_0 = datahub_v1_notebook_reporting_service_pb2.ListNotebookReportsResponse()
            outgoing_0 = datahub_v1_notebook_reporting_service_pb2.ListNotebookReportsRequest(
                context=request.context,
                filter=datahub_v1_notebook_reporting_service_pb2.ListNotebookReportsRequest.Filter(
                    labels=dict(request.filter.labels),
                    owner_id=request.filter.owner_id
                ),
                page=common_v1_paging_pb2.PageRequest(
                    page_size=request.page.page_size,
                    page_token=request.page.page_token
                )
            )
            response_0 = await deps.clients.datahub_notebook_reporting.ListNotebookReports(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_0)
            returned_0_1 = response_0.result.status
            if returned_0_1:
                response.result.status = returned_0_1
            return response

    async def handle_schedule_data_share_report(
        self,
        request: datahub_v1_data_share_reporting_service_pb2.ScheduleDataShareReportRequest
    ) -> datahub_v1_data_share_reporting_service_pb2.ScheduleDataShareReportResponse:
        """Schedules a data share."""
        deps = self.deps
        response = datahub_v1_data_share_reporting_service_pb2.ScheduleDataShareReportResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ScheduleDataShareReport', extra={'fields': {'data_share_id': request.data_share_id}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ScheduleDataShareReport',
                {'data_share_id': request.data_share_id}
            )
            response_0 = notifications_v1_notification_service_pb2.BatchGetNotificationsResponse()
            response_1 = datahub_v1_workspace_approval_service_pb2.CommentWorkspaceApprovalResponse()
            outgoing_0 = notifications_v1_notification_service_pb2.BatchGetNotificationsRequest(context=request.context)
            document_0 = MessageToDict(outgoing_0, preserving_proto_field_name=True)
            outgoing_0 = ParseDict(document_0, notifications_v1_notification_service_pb2.BatchGetNotificationsRequest())
            response_0 = await deps.clients.notifications_notification.BatchGetNotifications(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = datahub_v1_workspace_approval_service_pb2.CommentWorkspaceApprovalRequest(
                annotations=dict(request.annotations),
                context=request.context,
                workspace=datahub_v1_datahub_pb2.Workspace(
                    assignee=identity_v1_refs_pb2.UserRef(user_id=request.context.actor.user_id)
                )
            )
            document_1 = MessageToJson(outgoing_1, preserving_proto_field_name=True)
            outgoing_1 = Parse(document_1, datahub_v1_workspace_approval_service_pb2.CommentWorkspaceApprovalRequest())
            response_1 = await deps.clients.datahub_workspace_approval.CommentWorkspaceApproval(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.correlation_id
            if returned_0_0:
                response.result.correlation_id = returned_0_0
            returned_0_1 = response_0.result.details
            response.result.details.update(returned_0_1)
            returned_1_0 = response_1.result.status
            if returned_1_0:
                response.result.status = returned_1_0
            echoed_0 = request.details.period
            response.period.CopyFrom(echoed_0)
            return response

    async def handle_share_data_share_report(
        self,
        request: datahub_v1_data_share_reporting_service_pb2.ShareDataShareReportRequest
    ) -> datahub_v1_data_share_reporting_service_pb2.ShareDataShareReportResponse:
        """Shares a data share."""
        deps = self.deps
        response = datahub_v1_data_share_reporting_service_pb2.ShareDataShareReportResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ShareDataShareReport', extra={'fields': {'channel': request.details.channel}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ShareDataShareReport',
                {'channel': request.details.channel}
            )
            response_0 = datahub_v1_notebook_reporting_service_pb2.GenerateNotebookReportResponse()
            response_1 = itsm_v1_incident_service_pb2.CreateIncidentResponse()
            outgoing_0 = datahub_v1_notebook_reporting_service_pb2.GenerateNotebookReportRequest(
                annotations=dict(request.annotations),
                context=request.context,
                reason=request.reason
            )
            outgoing_1 = itsm_v1_incident_service_pb2.CreateIncidentRequest(
                context=request.context,
                incident=itsm_v1_itsm_pb2.Incident(
                    assignee=identity_v1_refs_pb2.UserRef(email=request.details.recipient.email),
                    requester=common_v1_contact_pb2.ContactInfo(
                        phone=request.details.recipient.phone,
                        preferred_channel=request.details.recipient.preferred_channel
                    )
                )
            )
            response_0, response_1 = await asyncio.gather(
                deps.clients.datahub_notebook_reporting.GenerateNotebookReport(
                    outgoing_0,
                    timeout=deps.settings.timeout
                ),
                deps.clients.itsm_incident.CreateIncident(outgoing_1, timeout=deps.settings.timeout),
            )
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.outcome.message = returned_0_0
            returned_1_0 = response_1.incident.audit.created_by
            if returned_1_0:
                response.data_share.audit.created_by = returned_1_0
            returned_1_1 = response_1.incident.audit.etag
            if returned_1_1:
                response.data_share.audit.etag = returned_1_1
            echoed_0 = request.data_share_id
            response.data_share.data_share_id = echoed_0
            return response

    async def handle_stream_data_share_metrics(
        self,
        request: datahub_v1_data_share_reporting_service_pb2.StreamDataShareMetricsRequest
    ) -> datahub_v1_data_share_reporting_service_pb2.StreamDataShareMetricsResponse:
        """Streams the changes of data shares as they happen."""
        deps = self.deps
        response = datahub_v1_data_share_reporting_service_pb2.StreamDataShareMetricsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('StreamDataShareMetrics', extra={'fields': {'max_events': request.max_events}})
            await deps.repository.audit(
                request.context.tenant_id,
                'StreamDataShareMetrics',
                {'max_events': request.max_events}
            )
            response_0 = datahub_v1_workspace_reporting_service_pb2.GenerateWorkspaceReportResponse()
            response_1 = datahub_v1_notebook_reporting_service_pb2.StreamNotebookMetricsResponse()
            response_2 = datahub_v1_data_share_approval_service_pb2.DelegateDataShareApprovalResponse()
            outgoing_0 = datahub_v1_workspace_reporting_service_pb2.GenerateWorkspaceReportRequest(
                annotations=dict(request.context.baggage),
                context=request.context,
                details=datahub_v1_workspace_reporting_service_pb2.GenerateWorkspaceReportRequest.Details(
                    filters=dict(request.filter.labels)
                )
            )
            registered_0 = cast(
                datahub_v1_workspace_reporting_service_pb2_grpc.WorkspaceReportingServiceStub,
                deps.clients.registry['acme.datahub.v1.WorkspaceReportingService']
            )
            response_0 = await registered_0.GenerateWorkspaceReport(outgoing_0, timeout=deps.settings.timeout)
            outgoing_1 = datahub_v1_notebook_reporting_service_pb2.StreamNotebookMetricsRequest(
                context=request.context,
                filter=datahub_v1_notebook_reporting_service_pb2.StreamNotebookMetricsRequest.Filter(
                    created_after=request.filter.created_after
                ),
                subscriber=common_v1_contact_pb2.ContactInfo(
                    email=request.subscriber.email,
                    name=request.subscriber.name,
                    preferred_channel=request.subscriber.preferred_channel
                )
            )
            async for chunk_1 in deps.clients.datahub_notebook_reporting.StreamNotebookMetrics(
                outgoing_1,
                timeout=deps.settings.timeout
            ):
                response_1 = chunk_1
            command_2 = DataShareReportingStreamDataShareMetrics2Command.model_validate(
                {
                    'context': request.context,
                    'details_approver_email': request.subscriber.email,
                    'data_share_billing_address_region': request.filter.region,
                    'details_approver_user_id': request.context.actor.user_id,
                    'details_approver_email_value': request.context.actor.email
                }
            )
            outgoing_2 = to_data_share_reporting_stream_data_share_metrics2_command(command_2)
            response_2 = await deps.clients.datahub_data_share_approval.DelegateDataShareApproval(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.details
            response.result.details.update(returned_0_0)
            returned_0_1 = response_0.result.correlation_id
            if returned_0_1:
                response.result.correlation_id = returned_0_1
            returned_2_0 = response_2.data_share.counterparty.notebook_id
            if returned_2_0:
                response.data_share.counterparty.notebook_id = returned_2_0
            returned_2_1 = response_2.data_share.status
            if returned_2_1:
                response.data_share.status = returned_2_1
            echoed_0 = request.filter.region
            response.data_share.billing_address.region = echoed_0
            return response
