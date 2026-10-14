"""Builds and schedules reports about workspaces."""

from __future__ import annotations

from collections.abc import AsyncIterator
from dataclasses import dataclass
from functools import partial
from typing import Any
from typing import cast
import asyncio
import logging

from google.protobuf.any_pb2 import Any as AnyMessage
from google.protobuf.json_format import MessageToJson
from google.protobuf.json_format import Parse
import grpc

from acme.audit.v1 import audit_event_query_service_pb2 as audit_v1_audit_event_query_service_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.customers.v1 import (
    customer_segment_approval_service_pb2 as customers_v1_customer_segment_approval_service_pb2,
)
from acme.customers.v1 import refs_pb2 as customers_v1_refs_pb2
from acme.datahub.v1 import data_share_validation_service_pb2 as datahub_v1_data_share_validation_service_pb2
from acme.datahub.v1 import datahub_pb2 as datahub_v1_datahub_pb2
from acme.datahub.v1 import notebook_approval_service_pb2 as datahub_v1_notebook_approval_service_pb2
from acme.datahub.v1 import workspace_approval_service_pb2 as datahub_v1_workspace_approval_service_pb2
from acme.datahub.v1 import workspace_reporting_service_pb2 as datahub_v1_workspace_reporting_service_pb2
from acme.datahub.v1 import workspace_reporting_service_pb2_grpc as datahub_v1_workspace_reporting_service_pb2_grpc
from acme.edgegateway.v1 import route_binding_service_pb2 as edgegateway_v1_route_binding_service_pb2
from acme.forecasting.v1 import (
    demand_forecast_approval_service_pb2 as forecasting_v1_demand_forecast_approval_service_pb2,
)
from acme.forecasting.v1 import forecasting_pb2 as forecasting_v1_forecasting_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.ledger.v1 import ledger_account_query_service_pb2 as ledger_v1_ledger_account_query_service_pb2
from acme.metrics.v1 import metric_series_query_service_pb2 as metrics_v1_metric_series_query_service_pb2
from acme.notifications.v1 import notification_service_pb2 as notifications_v1_notification_service_pb2
from acme.patientapp.v1 import patient_home_service_pb2 as patientapp_v1_patient_home_service_pb2
from acme.pipelines.v1 import pipeline_step_sync_service_pb2 as pipelines_v1_pipeline_step_sync_service_pb2
from acme.pipelines.v1 import pipelines_pb2 as pipelines_v1_pipelines_pb2

from acme_data.domains.datahub import hooks
from acme_data.domains.datahub.adapters import WorkspaceReportingDeleteWorkspaceReport1Adapter
from acme_data.domains.datahub.adapters import WorkspaceReportingDeleteWorkspaceReport1Port
from acme_data.domains.datahub.dependencies import Dependencies
from acme_data.domains.datahub.models import WorkspaceReportingStreamWorkspaceMetrics2Command
from acme_data.domains.datahub.models import to_workspace_reporting_stream_workspace_metrics2_command
from acme_data.platform.rpc import messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import run_steps
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_id
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


@dataclass(slots=True)
class WorkspaceReportingServicer(datahub_v1_workspace_reporting_service_pb2_grpc.WorkspaceReportingServiceServicer):
    deps: Dependencies

    @rpc_errors
    @retry_transient
    async def CountWorkspaceTotals(
        self, request: datahub_v1_workspace_reporting_service_pb2.CountWorkspaceTotalsRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_workspace_reporting_service_pb2.CountWorkspaceTotalsResponse:
        """Counts workspaces by status."""
        return await self.handle_count_workspace_totals(request)

    @rpc_errors
    async def DeleteWorkspaceReport(
        self, request: datahub_v1_workspace_reporting_service_pb2.DeleteWorkspaceReportRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_workspace_reporting_service_pb2.DeleteWorkspaceReportResponse:
        """Deletes a workspace."""
        return await self.handle_delete_workspace_report(request)

    @rpc_errors
    @retry_transient
    async def FetchWorkspaceReport(
        self, request: datahub_v1_workspace_reporting_service_pb2.FetchWorkspaceReportRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_workspace_reporting_service_pb2.FetchWorkspaceReportResponse:
        """Returns a workspace."""
        return await self.handle_fetch_workspace_report(request)

    @rpc_errors
    async def GenerateWorkspaceReport(
        self, request: datahub_v1_workspace_reporting_service_pb2.GenerateWorkspaceReportRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_workspace_reporting_service_pb2.GenerateWorkspaceReportResponse:
        """Generates a workspace."""
        return await self.handle_generate_workspace_report(request)

    @rpc_errors
    @retry_transient
    async def ListWorkspaceReports(
        self, request: datahub_v1_workspace_reporting_service_pb2.ListWorkspaceReportsRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_workspace_reporting_service_pb2.ListWorkspaceReportsResponse:
        """Lists workspaces a page at a time."""
        return await self.handle_list_workspace_reports(request)

    @rpc_errors
    async def ShareWorkspaceReport(
        self, request: datahub_v1_workspace_reporting_service_pb2.ShareWorkspaceReportRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_workspace_reporting_service_pb2.ShareWorkspaceReportResponse:
        """Shares a workspace."""
        return await self.handle_share_workspace_report(request)

    @stream_errors
    async def StreamWorkspaceMetrics(
        self, request: datahub_v1_workspace_reporting_service_pb2.StreamWorkspaceMetricsRequest, context: grpc.aio.ServicerContext,
    ) -> AsyncIterator[datahub_v1_workspace_reporting_service_pb2.StreamWorkspaceMetricsResponse]:
        """Streams the changes of workspaces as they happen."""
        response = await self.handle_stream_workspace_metrics(request)
        for item in messages((response,)):
            yield item

    async def handle_count_workspace_totals(
        self,
        request: datahub_v1_workspace_reporting_service_pb2.CountWorkspaceTotalsRequest
    ) -> datahub_v1_workspace_reporting_service_pb2.CountWorkspaceTotalsResponse:
        """Counts workspaces by status."""
        deps = self.deps
        response = datahub_v1_workspace_reporting_service_pb2.CountWorkspaceTotalsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CountWorkspaceTotals', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'CountWorkspaceTotals',
                {'order_by': request.order_by}
            )
            response_0 = ledger_v1_ledger_account_query_service_pb2.ResolveLedgerAccountsResponse()
            response_1 = datahub_v1_workspace_approval_service_pb2.RecallWorkspaceResponse()
            outgoing_0 = ledger_v1_ledger_account_query_service_pb2.ResolveLedgerAccountsRequest(
                context=request.context
            )
            response_0 = await deps.clients.ledger_ledger_account_query.ResolveLedgerAccounts(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = datahub_v1_workspace_approval_service_pb2.RecallWorkspaceRequest(
                context=request.context,
                workspace=datahub_v1_datahub_pb2.Workspace(
                    assignee=identity_v1_refs_pb2.UserRef(
                        email=request.context.actor.email,
                        user_id=request.context.actor.user_id
                    ),
                    history=[datahub_v1_datahub_pb2.WorkspaceStatusChange(changed_at=request.filter.created_after)]
                )
            )
            response_1 = await hooks.workspace_reporting_count_workspace_totals1(
                deps.clients.datahub_workspace_approval,
                outgoing_1,
                deps.settings.timeout
            )
            returned_0_0 = response_0.result.details
            response.result.details.update(returned_0_0)
            returned_0_1 = response_0.result.correlation_id
            if returned_0_1:
                response.result.correlation_id = returned_0_1
            returned_1_0 = response_1.outcome.status
            if returned_1_0:
                response.result.status = returned_1_0
            return response

    async def handle_delete_workspace_report(
        self,
        request: datahub_v1_workspace_reporting_service_pb2.DeleteWorkspaceReportRequest
    ) -> datahub_v1_workspace_reporting_service_pb2.DeleteWorkspaceReportResponse:
        """Deletes a workspace."""
        deps = self.deps
        response = datahub_v1_workspace_reporting_service_pb2.DeleteWorkspaceReportResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('DeleteWorkspaceReport', extra={'fields': {'force': request.force}})
            await deps.repository.audit(request.context.tenant_id, 'DeleteWorkspaceReport', {'force': request.force})
            response_0 = customers_v1_customer_segment_approval_service_pb2.SubmitCustomerSegmentResponse()
            response_1 = forecasting_v1_demand_forecast_approval_service_pb2.EscalateDemandForecastResponse()
            response_2 = datahub_v1_workspace_approval_service_pb2.DelegateWorkspaceApprovalResponse()
            outgoing_0 = customers_v1_customer_segment_approval_service_pb2.SubmitCustomerSegmentRequest()
            outgoing_0.context.CopyFrom(request.context)
            outgoing_0.reason = request.reason
            outgoing_0.customer_segment.audit.etag = request.etag
            outgoing_0.context.tenant_id = tenant_id.get()
            response_0 = await deps.clients.customers_customer_segment_approval.SubmitCustomerSegment(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = forecasting_v1_demand_forecast_approval_service_pb2.EscalateDemandForecastRequest(
                context=request.context,
                demand_forecast=forecasting_v1_forecasting_pb2.DemandForecast(
                    audit=common_v1_audit_pb2.AuditInfo(updated_at=response_0.customer_segment.audit.updated_at)
                )
            )
            port_1: WorkspaceReportingDeleteWorkspaceReport1Port = WorkspaceReportingDeleteWorkspaceReport1Adapter(
                deps.clients.forecasting_demand_forecast_approval,
                deps.settings.timeout
            )
            response_1 = await port_1.execute(outgoing_1)
            outgoing_2 = datahub_v1_workspace_approval_service_pb2.DelegateWorkspaceApprovalRequest(
                context=request.context,
                details=datahub_v1_workspace_approval_service_pb2.DelegateWorkspaceApprovalRequest.Details(
                    approver=identity_v1_refs_pb2.UserRef(email=response_0.customer_segment.owner.email)
                ),
                workspace=datahub_v1_datahub_pb2.Workspace(
                    audit=common_v1_audit_pb2.AuditInfo(updated_by=response_1.demand_forecast.audit.updated_by),
                    customer=customers_v1_refs_pb2.CustomerRef(
                        display_name=response_0.customer_segment.owner.display_name
                    )
                )
            )
            steps_2 = [
                partial(
                    deps.clients.datahub_workspace_approval.DelegateWorkspaceApproval,
                    outgoing_2,
                    timeout=deps.settings.timeout
                )
            ]
            results_2 = await run_steps(steps_2)
            response_2 = results_2[-1]
            returned_0_0 = response_0.result.details
            response.result.details.update(returned_0_0)
            returned_0_1 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_1)
            returned_1_0 = response_1.outcome.effective_at
            if returned_1_0.ListFields():
                response.effective_at.MergeFrom(returned_1_0)
            returned_1_1 = response_1.result.message
            if returned_1_1:
                response.result.message = returned_1_1
            returned_2_0 = response_2.result.message
            if returned_2_0:
                response.result.message = returned_2_0
            return response

    async def handle_fetch_workspace_report(
        self,
        request: datahub_v1_workspace_reporting_service_pb2.FetchWorkspaceReportRequest
    ) -> datahub_v1_workspace_reporting_service_pb2.FetchWorkspaceReportResponse:
        """Returns a workspace."""
        deps = self.deps
        response = datahub_v1_workspace_reporting_service_pb2.FetchWorkspaceReportResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('FetchWorkspaceReport', extra={'fields': {'domain': 'datahub'}})
            await deps.repository.audit(request.context.tenant_id, 'FetchWorkspaceReport', {})
            response_0 = pipelines_v1_pipeline_step_sync_service_pb2.ResolvePipelineStepConflictResponse()
            response_1 = metrics_v1_metric_series_query_service_pb2.SuggestMetricSeriesesResponse()
            outgoing_0 = pipelines_v1_pipeline_step_sync_service_pb2.ResolvePipelineStepConflictRequest(
                context=request.context,
                pipeline_step=pipelines_v1_pipelines_pb2.PipelineStep(
                    owner=identity_v1_refs_pb2.UserRef(
                        email=request.context.actor.email,
                        user_id=request.context.actor.user_id
                    )
                )
            )
            response_0 = await deps.clients.pipelines_pipeline_step_sync.ResolvePipelineStepConflict(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = metrics_v1_metric_series_query_service_pb2.SuggestMetricSeriesesRequest(
                context=request.context,
                filter=metrics_v1_metric_series_query_service_pb2.SuggestMetricSeriesesRequest.Filter(
                    created_after=response_0.pipeline_step.audit.updated_at,
                    labels=dict(response_0.result.details),
                    owner_id=request.workspace_id
                )
            )
            response_1 = cast(metrics_v1_metric_series_query_service_pb2.SuggestMetricSeriesesResponse, await deps.bus.request(
                'acme.datahub.v1.WorkspaceReportingService/FetchWorkspaceReport/1', outgoing_1, deps.settings.timeout,
            ))
            returned_0_0 = response_0.pipeline_step.owner.display_name
            if returned_0_0:
                response.workspace.assignee.display_name = returned_0_0
            returned_0_1 = response_0.pipeline_step.audit.etag
            if returned_0_1:
                response.workspace.audit.etag = returned_0_1
            returned_1_0 = response_1.result.message
            if returned_1_0:
                response.result.message = returned_1_0
            returned_1_1 = response_1.result.correlation_id
            if returned_1_1:
                response.result.correlation_id = returned_1_1
            echoed_0 = request.workspace_id
            response.workspace.workspace_id = echoed_0
            return response

    async def handle_generate_workspace_report(
        self,
        request: datahub_v1_workspace_reporting_service_pb2.GenerateWorkspaceReportRequest
    ) -> datahub_v1_workspace_reporting_service_pb2.GenerateWorkspaceReportResponse:
        """Generates a workspace."""
        deps = self.deps
        response = datahub_v1_workspace_reporting_service_pb2.GenerateWorkspaceReportResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('GenerateWorkspaceReport', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'GenerateWorkspaceReport',
                {'reason': request.reason}
            )
            response_0 = notifications_v1_notification_service_pb2.ListNotificationsResponse()
            response_1 = datahub_v1_workspace_approval_service_pb2.CommentWorkspaceApprovalResponse()
            response_2 = datahub_v1_workspace_approval_service_pb2.SubmitWorkspaceResponse()
            outgoing_0 = notifications_v1_notification_service_pb2.ListNotificationsRequest(
                context=request.context,
                filter=notifications_v1_notification_service_pb2.ListNotificationsRequest.Filter(
                    owner_id=request.workspace_id
                )
            )
            outgoing_1 = datahub_v1_workspace_approval_service_pb2.CommentWorkspaceApprovalRequest(
                context=request.context,
                details=datahub_v1_workspace_approval_service_pb2.CommentWorkspaceApprovalRequest.Details(
                    approver=identity_v1_refs_pb2.UserRef(user_id=request.context.actor.user_id)
                )
            )
            response_0, response_1 = await asyncio.gather(
                deps.clients.notifications_notification.ListNotifications(outgoing_0, timeout=deps.settings.timeout),
                deps.clients.datahub_workspace_approval.CommentWorkspaceApproval(
                    outgoing_1,
                    timeout=deps.settings.timeout
                ),
            )
            fields_2: dict[str, Any] = {
                'context': request.context,
                'workspace': {'requester': {'email': response_1.workspace.assignee.email}}
            }
            outgoing_2 = datahub_v1_workspace_approval_service_pb2.SubmitWorkspaceRequest(**fields_2)
            response_2 = await deps.clients.datahub_workspace_approval.SubmitWorkspace(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_0)
            returned_1_0 = response_1.outcome.message
            if returned_1_0:
                response.result.message = returned_1_0
            returned_1_1 = response_1.result.reference_ids
            response.result.reference_ids.extend(returned_1_1)
            returned_2_0 = response_2.result.status
            if returned_2_0:
                response.result.status = returned_2_0
            returned_2_1 = response_2.result.message
            if returned_2_1:
                response.result.message = returned_2_1
            echoed_0 = request.details.period
            response.period.CopyFrom(echoed_0)
            return response

    async def handle_list_workspace_reports(
        self,
        request: datahub_v1_workspace_reporting_service_pb2.ListWorkspaceReportsRequest
    ) -> datahub_v1_workspace_reporting_service_pb2.ListWorkspaceReportsResponse:
        """Lists workspaces a page at a time."""
        deps = self.deps
        response = datahub_v1_workspace_reporting_service_pb2.ListWorkspaceReportsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ListWorkspaceReports', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ListWorkspaceReports',
                {'order_by': request.order_by}
            )
            response_0 = datahub_v1_workspace_approval_service_pb2.RecallWorkspaceResponse()
            outgoing_0 = datahub_v1_workspace_approval_service_pb2.RecallWorkspaceRequest(
                context=request.context,
                workspace=datahub_v1_datahub_pb2.Workspace(
                    assignee=identity_v1_refs_pb2.UserRef(user_id=request.context.actor.user_id),
                    customer=customers_v1_refs_pb2.CustomerRef(email=request.context.actor.email),
                    sla=datahub_v1_datahub_pb2.WorkspaceSla(due_at=request.filter.created_after)
                )
            )
            response_0 = await deps.clients.datahub_workspace_approval.RecallWorkspace(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.workspace.audit.etag
            returned_0_0_part_0 = response.workspaces.add()
            if returned_0_0:
                returned_0_0_part_0.audit.etag = returned_0_0
            returned_0_1 = response_0.workspace.customer.display_name
            returned_0_1_part_0 = response.workspaces.add()
            if returned_0_1:
                returned_0_1_part_0.assignee.display_name = returned_0_1
            return response

    async def handle_share_workspace_report(
        self,
        request: datahub_v1_workspace_reporting_service_pb2.ShareWorkspaceReportRequest
    ) -> datahub_v1_workspace_reporting_service_pb2.ShareWorkspaceReportResponse:
        """Shares a workspace."""
        deps = self.deps
        response = datahub_v1_workspace_reporting_service_pb2.ShareWorkspaceReportResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ShareWorkspaceReport', extra={'fields': {'channel': request.details.channel}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ShareWorkspaceReport',
                {'channel': request.details.channel}
            )
            response_0 = datahub_v1_data_share_validation_service_pb2.ScoreDataShareResponse()
            response_1 = patientapp_v1_patient_home_service_pb2.CreatePatientHomeResponse()
            response_2 = audit_v1_audit_event_query_service_pb2.BrowseAuditEventsResponse()
            outgoing_0 = datahub_v1_data_share_validation_service_pb2.ScoreDataShareRequest(
                annotations=dict(request.annotations),
                context=request.context,
                data_share=datahub_v1_datahub_pb2.DataShare(
                    lines=[datahub_v1_datahub_pb2.DataShareLine(attributes=dict(request.details.variables))]
                ),
                reason=request.reason
            )
            document_0 = MessageToJson(outgoing_0, preserving_proto_field_name=True)
            outgoing_0 = Parse(document_0, datahub_v1_data_share_validation_service_pb2.ScoreDataShareRequest())
            response_0 = await deps.clients.datahub_data_share_validation.ScoreDataShare(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = patientapp_v1_patient_home_service_pb2.CreatePatientHomeRequest()
            outgoing_1.context.CopyFrom(request.context)
            outgoing_1.patient_home.requester.preferred_channel = request.details.recipient.preferred_channel
            merged_1 = patientapp_v1_patient_home_service_pb2.CreatePatientHomeRequest()
            merged_1.MergeFrom(outgoing_1)
            outgoing_1.CopyFrom(merged_1)
            response_1 = await deps.clients.patientapp_patient_home.CreatePatientHome(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = audit_v1_audit_event_query_service_pb2.BrowseAuditEventsRequest(
                context=request.context,
                filter=audit_v1_audit_event_query_service_pb2.BrowseAuditEventsRequest.Filter(
                    created_after=response_0.data_share.audit.created_at,
                    labels=dict(response_1.result.details),
                    region=response_0.data_share.billing_address.region
                )
            )
            envelope_2 = AnyMessage()
            envelope_2.Pack(outgoing_2)
            outgoing_2 = audit_v1_audit_event_query_service_pb2.BrowseAuditEventsRequest()
            if not envelope_2.Unpack(outgoing_2):
                raise ValueError("partner envelope contains the wrong request type")
            response_2 = await deps.clients.audit_audit_event_query.BrowseAuditEvents(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.details
            response.result.details.update(returned_0_0)
            returned_1_0 = response_1.patient_home.custom_fields
            response.workspace.custom_fields.update(returned_1_0)
            returned_1_1 = response_1.patient_home.requester.preferred_channel
            if returned_1_1:
                response.workspace.requester.preferred_channel = returned_1_1
            returned_2_0 = response_2.result.reference_ids
            response.result.reference_ids.extend(returned_2_0)
            returned_2_1 = response_2.result.status
            if returned_2_1:
                response.result.status = returned_2_1
            echoed_0 = request.workspace_id
            response.workspace.workspace_id = echoed_0
            echoed_1 = request.details.recipient.name
            response.workspace.requester.name.CopyFrom(echoed_1)
            return response

    async def handle_stream_workspace_metrics(
        self,
        request: datahub_v1_workspace_reporting_service_pb2.StreamWorkspaceMetricsRequest
    ) -> datahub_v1_workspace_reporting_service_pb2.StreamWorkspaceMetricsResponse:
        """Streams the changes of workspaces as they happen."""
        deps = self.deps
        response = datahub_v1_workspace_reporting_service_pb2.StreamWorkspaceMetricsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('StreamWorkspaceMetrics', extra={'fields': {'max_events': request.max_events}})
            await deps.repository.audit(
                request.context.tenant_id,
                'StreamWorkspaceMetrics',
                {'max_events': request.max_events}
            )
            response_0 = datahub_v1_workspace_approval_service_pb2.DelegateWorkspaceApprovalResponse()
            response_1 = edgegateway_v1_route_binding_service_pb2.SearchRouteBindingsResponse()
            response_2 = datahub_v1_workspace_approval_service_pb2.ApproveWorkspaceResponse()
            response_3 = datahub_v1_notebook_approval_service_pb2.ListPendingNotebooksResponse()
            outgoing_0 = datahub_v1_workspace_approval_service_pb2.DelegateWorkspaceApprovalRequest(
                context=request.context,
                workspace=datahub_v1_datahub_pb2.Workspace(
                    customer=customers_v1_refs_pb2.CustomerRef(email=request.subscriber.email)
                )
            )
            outgoing_1 = edgegateway_v1_route_binding_service_pb2.SearchRouteBindingsRequest(
                context=request.context,
                filter=edgegateway_v1_route_binding_service_pb2.SearchRouteBindingsRequest.Filter(
                    created_after=request.filter.created_after,
                    labels=dict(request.filter.labels)
                )
            )
            outgoing_3 = datahub_v1_notebook_approval_service_pb2.ListPendingNotebooksRequest(
                context=request.context,
                filter=datahub_v1_notebook_approval_service_pb2.ListPendingNotebooksRequest.Filter(
                    owner_id=request.filter.owner_id,
                    query=request.filter.query,
                    region=request.filter.region
                )
            )
            response_0, response_1, response_3 = await asyncio.gather(
                deps.clients.datahub_workspace_approval.DelegateWorkspaceApproval(
                    outgoing_0,
                    timeout=deps.settings.timeout
                ),
                deps.clients.edgegateway_route_binding.SearchRouteBindings(outgoing_1, timeout=deps.settings.timeout),
                deps.clients.datahub_notebook_approval.ListPendingNotebooks(outgoing_3, timeout=deps.settings.timeout),
            )
            command_2 = WorkspaceReportingStreamWorkspaceMetrics2Command.model_validate(
                {'context': request.context, 'workspace_sla_policy_id': response_0.workspace.sla.policy_id}
            )
            outgoing_2 = to_workspace_reporting_stream_workspace_metrics2_command(command_2)
            response_2 = await deps.clients.datahub_workspace_approval.ApproveWorkspace(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.workspace.requester.email
            if returned_0_0:
                response.workspace.requester.email = returned_0_0
            returned_0_1 = response_0.workspace.requester.preferred_channel
            if returned_0_1:
                response.workspace.requester.preferred_channel = returned_0_1
            returned_1_0 = response_1.result.status
            if returned_1_0:
                response.result.status = returned_1_0
            returned_1_1 = response_1.result.message
            if returned_1_1:
                response.result.message = returned_1_1
            returned_2_0 = response_2.workspace.status
            if returned_2_0:
                response.workspace.status = returned_2_0
            returned_2_1 = response_2.workspace.audit.created_by
            if returned_2_1:
                response.workspace.audit.created_by = returned_2_1
            returned_3_0 = response_3.result.reference_ids
            response.result.reference_ids.extend(returned_3_0)
            returned_3_1 = response_3.result.message
            if returned_3_1:
                response.result.message = returned_3_1
            echoed_0 = request.subscriber.email
            response.workspace.assignee.email = echoed_0
            echoed_1 = request.subscriber.phone
            response.workspace.requester.phone = echoed_1
            return response
