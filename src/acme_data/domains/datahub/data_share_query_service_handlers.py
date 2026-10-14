"""Reusable transport mixin for DataShareQueryService."""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import cast
import logging

from google.protobuf.json_format import MessageToDict
from google.protobuf.json_format import ParseDict
import grpc

from acme.anomalies.v1 import (
    anomaly_feedback_approval_service_pb2 as anomalies_v1_anomaly_feedback_approval_service_pb2,
)
from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.common.v1 import paging_pb2 as common_v1_paging_pb2
from acme.customers.v1 import (
    customer_segment_reporting_service_pb2 as customers_v1_customer_segment_reporting_service_pb2,
)
from acme.customers.v1 import customer_workflow_service_pb2 as customers_v1_customer_workflow_service_pb2
from acme.customers.v1 import customers_pb2 as customers_v1_customers_pb2
from acme.customers.v1 import preference_sync_service_pb2 as customers_v1_preference_sync_service_pb2
from acme.datahub.v1 import data_share_query_service_pb2 as datahub_v1_data_share_query_service_pb2
from acme.datahub.v1 import notebook_approval_service_pb2 as datahub_v1_notebook_approval_service_pb2
from acme.datahub.v1 import notebook_notification_service_pb2 as datahub_v1_notebook_notification_service_pb2
from acme.datahub.v1 import notebook_notification_service_pb2_grpc as datahub_v1_notebook_notification_service_pb2_grpc
from acme.datahub.v1 import notebook_workflow_service_pb2 as datahub_v1_notebook_workflow_service_pb2
from acme.datahub.v1 import workspace_integration_service_pb2 as datahub_v1_workspace_integration_service_pb2
from acme.datahub.v1 import workspace_reporting_service_pb2 as datahub_v1_workspace_reporting_service_pb2
from acme.fanportal.v1 import fan_session_query_service_pb2 as fanportal_v1_fan_session_query_service_pb2
from acme.featureflags.v1 import feature_flag_query_service_pb2 as featureflags_v1_feature_flag_query_service_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.metrics.v1 import dashboard_history_service_pb2 as metrics_v1_dashboard_history_service_pb2
from acme.metrics.v1 import metrics_pb2 as metrics_v1_metrics_pb2
from acme.notifications.v1 import notification_query_service_pb2 as notifications_v1_notification_query_service_pb2

from acme_data.domains.datahub.adapters import DataShareQueryExportDataShares0Adapter
from acme_data.domains.datahub.dependencies import Dependencies
from acme_data.domains.datahub.models import DataShareQuerySummarizeDataShares0Command
from acme_data.domains.datahub.models import DataShareQuerySummarizeDataShares1Command
from acme_data.domains.datahub.models import to_data_share_query_summarize_data_shares0_command
from acme_data.domains.datahub.models import to_data_share_query_summarize_data_shares1_command
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class DataShareQueryServicerHandlers:
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    @retry_transient
    async def BrowseDataShares(
        self, request: datahub_v1_data_share_query_service_pb2.BrowseDataSharesRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_data_share_query_service_pb2.BrowseDataSharesResponse:
        """Lists data shares a page at a time."""
        return await self.handle_browse_data_shares(request)

    @rpc_errors
    @retry_transient
    async def CountDataShares(
        self, request: datahub_v1_data_share_query_service_pb2.CountDataSharesRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_data_share_query_service_pb2.CountDataSharesResponse:
        """Counts data shares by status."""
        return await self.handle_count_data_shares(request)

    @stream_errors
    async def ExportDataShares(
        self, request: datahub_v1_data_share_query_service_pb2.ExportDataSharesRequest, context: grpc.aio.ServicerContext,
    ) -> AsyncIterator[datahub_v1_data_share_query_service_pb2.ExportDataSharesResponse]:
        """Streams every matching data share."""
        response = await self.handle_export_data_shares(request)
        for item in messages((response,)):
            yield item

    @rpc_errors
    @retry_transient
    async def FindDataShares(
        self, request: datahub_v1_data_share_query_service_pb2.FindDataSharesRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_data_share_query_service_pb2.FindDataSharesResponse:
        """Lists data shares a page at a time."""
        return await self.handle_find_data_shares(request)

    @rpc_errors
    @retry_transient
    async def LookupDataShare(
        self, request: datahub_v1_data_share_query_service_pb2.LookupDataShareRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_data_share_query_service_pb2.LookupDataShareResponse:
        """Returns a data share."""
        return await self.handle_lookup_data_share(request)

    @rpc_errors
    @retry_transient
    async def PeekDataShare(
        self, request: datahub_v1_data_share_query_service_pb2.PeekDataShareRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_data_share_query_service_pb2.PeekDataShareResponse:
        """Returns a data share."""
        return await self.handle_peek_data_share(request)

    @rpc_errors
    @retry_transient
    async def ResolveDataShares(
        self, request: datahub_v1_data_share_query_service_pb2.ResolveDataSharesRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_data_share_query_service_pb2.ResolveDataSharesResponse:
        """Returns several data shares at once."""
        return await self.handle_resolve_data_shares(request)

    @rpc_errors
    @retry_transient
    async def SuggestDataShares(
        self, request: datahub_v1_data_share_query_service_pb2.SuggestDataSharesRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_data_share_query_service_pb2.SuggestDataSharesResponse:
        """Lists data shares a page at a time."""
        return await self.handle_suggest_data_shares(request)

    @rpc_errors
    async def SummarizeDataShares(
        self, request: datahub_v1_data_share_query_service_pb2.SummarizeDataSharesRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_data_share_query_service_pb2.SummarizeDataSharesResponse:
        """Summarizes a data share."""
        return await self.handle_summarize_data_shares(request)

    async def handle_browse_data_shares(
        self,
        request: datahub_v1_data_share_query_service_pb2.BrowseDataSharesRequest
    ) -> datahub_v1_data_share_query_service_pb2.BrowseDataSharesResponse:
        """Lists data shares a page at a time."""
        deps = self.deps
        response = datahub_v1_data_share_query_service_pb2.BrowseDataSharesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('BrowseDataShares', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(request.context.tenant_id, 'BrowseDataShares', {'order_by': request.order_by})
            return response

    async def handle_count_data_shares(
        self,
        request: datahub_v1_data_share_query_service_pb2.CountDataSharesRequest
    ) -> datahub_v1_data_share_query_service_pb2.CountDataSharesResponse:
        """Counts data shares by status."""
        deps = self.deps
        response = datahub_v1_data_share_query_service_pb2.CountDataSharesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CountDataShares', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(request.context.tenant_id, 'CountDataShares', {'order_by': request.order_by})
            response_0 = metrics_v1_dashboard_history_service_pb2.RevertDashboardResponse()
            response_1 = customers_v1_customer_segment_reporting_service_pb2.StreamCustomerSegmentMetricsResponse()
            outgoing_0 = metrics_v1_dashboard_history_service_pb2.RevertDashboardRequest(
                context=request.context,
                dashboard=metrics_v1_metrics_pb2.Dashboard(
                    billing_address=common_v1_address_pb2.PostalAddress(region=request.filter.region),
                    issued_at=request.filter.created_after
                )
            )
            response_0 = await deps.clients.metrics_dashboard_history.RevertDashboard(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = customers_v1_customer_segment_reporting_service_pb2.StreamCustomerSegmentMetricsRequest(
                context=request.context,
                filter=customers_v1_customer_segment_reporting_service_pb2.StreamCustomerSegmentMetricsRequest.Filter(
                    created_after=request.filter.created_after,
                    labels=dict(request.filter.labels),
                    query=request.filter.query,
                    region=response_0.dashboard.billing_address.region
                )
            )
            async for chunk_1 in deps.clients.customers_customer_segment_reporting.StreamCustomerSegmentMetrics(
                outgoing_1,
                timeout=deps.settings.timeout
            ):
                response_1 = chunk_1
            returned_0_0 = response_0.result.correlation_id
            if returned_0_0:
                response.result.correlation_id = returned_0_0
            return response

    async def handle_export_data_shares(
        self,
        request: datahub_v1_data_share_query_service_pb2.ExportDataSharesRequest
    ) -> datahub_v1_data_share_query_service_pb2.ExportDataSharesResponse:
        """Streams every matching data share."""
        deps = self.deps
        response = datahub_v1_data_share_query_service_pb2.ExportDataSharesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ExportDataShares', extra={'fields': {'destination_uri': request.destination_uri}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ExportDataShares',
                {'destination_uri': request.destination_uri}
            )
            response_0 = customers_v1_customer_workflow_service_pb2.StartCustomerWorkflowResponse()
            response_1 = datahub_v1_workspace_integration_service_pb2.ConnectWorkspaceSourceResponse()
            response_2 = datahub_v1_workspace_integration_service_pb2.ReplayWorkspaceEventsResponse()
            outgoing_0 = customers_v1_customer_workflow_service_pb2.StartCustomerWorkflowRequest(
                context=request.context,
                customer=customers_v1_customers_pb2.Customer(
                    passport=customers_v1_customers_pb2.CustomerPassport(expires_at=request.filter.created_after),
                    primary_address=common_v1_address_pb2.PostalAddress(region=request.filter.region),
                    relationship_manager=identity_v1_refs_pb2.UserRef(
                        email=request.context.actor.email,
                        user_id=request.context.actor.user_id
                    )
                )
            )
            response_0 = await DataShareQueryExportDataShares0Adapter(
                deps.clients.customers_customer_workflow,
                deps.settings.timeout
            )(outgoing_0)
            outgoing_1 = datahub_v1_workspace_integration_service_pb2.ConnectWorkspaceSourceRequest(
                context=request.context,
                details=datahub_v1_workspace_integration_service_pb2.ConnectWorkspaceSourceRequest.Details(
                    message_id=response_0.outcome.message,
                    received_at=request.filter.created_after
                )
            )
            response_1 = cast(datahub_v1_workspace_integration_service_pb2.ConnectWorkspaceSourceResponse, await deps.bus.request(
                'acme.datahub.v1.DataShareQueryService/ExportDataShares/1', outgoing_1, deps.settings.timeout,
            ))
            outgoing_2 = datahub_v1_workspace_integration_service_pb2.ReplayWorkspaceEventsRequest(
                context=request.context,
                details=datahub_v1_workspace_integration_service_pb2.ReplayWorkspaceEventsRequest.Details(
                    message_id=response_1.result.message
                ),
                workspace_id=response_1.workspace.workspace_id
            )
            response_2 = await deps.clients.datahub_workspace_integration.ReplayWorkspaceEvents(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.customer.relationship_manager.display_name
            if returned_0_0:
                response.data_share.counterparty.display_name = returned_0_0
            returned_0_1 = response_0.customer.primary_address.lines
            response.data_share.billing_address.lines.extend(returned_0_1)
            returned_1_0 = response_1.outcome.status
            if returned_1_0:
                response.result.status = returned_1_0
            returned_1_1 = response_1.result.message
            if returned_1_1:
                response.result.message = returned_1_1
            returned_2_0 = response_2.workspace.assignee.display_name
            if returned_2_0:
                response.data_share.counterparty.display_name = returned_2_0
            echoed_0 = request.filter.region
            response.data_share.billing_address.region = echoed_0
            return response

    async def handle_find_data_shares(
        self,
        request: datahub_v1_data_share_query_service_pb2.FindDataSharesRequest
    ) -> datahub_v1_data_share_query_service_pb2.FindDataSharesResponse:
        """Lists data shares a page at a time."""
        deps = self.deps
        response = datahub_v1_data_share_query_service_pb2.FindDataSharesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('FindDataShares', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(request.context.tenant_id, 'FindDataShares', {'order_by': request.order_by})
            response_0 = notifications_v1_notification_query_service_pb2.BrowseNotificationsResponse()
            outgoing_0 = notifications_v1_notification_query_service_pb2.BrowseNotificationsRequest(
                context=request.context,
                filter=notifications_v1_notification_query_service_pb2.BrowseNotificationsRequest.Filter(
                    created_after=request.filter.created_after,
                    labels=dict(request.filter.labels)
                ),
                page=common_v1_paging_pb2.PageRequest(page_token=request.page.page_token)
            )
            response_0 = await deps.clients.notifications_notification_query.BrowseNotifications(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.details
            response.result.details.update(returned_0_0)
            return response

    async def handle_lookup_data_share(
        self,
        request: datahub_v1_data_share_query_service_pb2.LookupDataShareRequest
    ) -> datahub_v1_data_share_query_service_pb2.LookupDataShareResponse:
        """Returns a data share."""
        deps = self.deps
        response = datahub_v1_data_share_query_service_pb2.LookupDataShareResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('LookupDataShare', extra={'fields': {'locale': request.context.locale}})
            await deps.repository.audit(
                request.context.tenant_id,
                'LookupDataShare',
                {'locale': request.context.locale}
            )
            echoed_0 = request.data_share_id
            response.data_share.data_share_id = echoed_0
            return response

    async def handle_peek_data_share(
        self,
        request: datahub_v1_data_share_query_service_pb2.PeekDataShareRequest
    ) -> datahub_v1_data_share_query_service_pb2.PeekDataShareResponse:
        """Returns a data share."""
        deps = self.deps
        response = datahub_v1_data_share_query_service_pb2.PeekDataShareResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('PeekDataShare', extra={'fields': {'domain': 'datahub'}})
            await deps.repository.audit(request.context.tenant_id, 'PeekDataShare', {})
            response_0 = fanportal_v1_fan_session_query_service_pb2.CountFanSessionsResponse()
            response_1 = datahub_v1_workspace_reporting_service_pb2.ListWorkspaceReportsResponse()
            outgoing_0 = fanportal_v1_fan_session_query_service_pb2.CountFanSessionsRequest(
                context=request.context,
                filter=fanportal_v1_fan_session_query_service_pb2.CountFanSessionsRequest.Filter(
                    owner_id=request.data_share_id
                )
            )
            response_0 = await deps.clients.fanportal_fan_session_query.CountFanSessions(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = datahub_v1_workspace_reporting_service_pb2.ListWorkspaceReportsRequest(
                context=request.context,
                filter=datahub_v1_workspace_reporting_service_pb2.ListWorkspaceReportsRequest.Filter(
                    labels=dict(response_0.result.details),
                    owner_id=response_0.result.correlation_id
                )
            )
            document_1 = MessageToDict(outgoing_1, preserving_proto_field_name=True)
            outgoing_1 = ParseDict(document_1, datahub_v1_workspace_reporting_service_pb2.ListWorkspaceReportsRequest())
            response_1 = await deps.clients.datahub_workspace_reporting.ListWorkspaceReports(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.result.message = returned_0_0
            returned_0_1 = response_0.result.status
            if returned_0_1:
                response.result.status = returned_0_1
            returned_1_0 = response_1.result.reference_ids
            response.result.reference_ids.extend(returned_1_0)
            returned_1_1 = response_1.result.status
            if returned_1_1:
                response.result.status = returned_1_1
            echoed_0 = request.data_share_id
            response.data_share.data_share_id = echoed_0
            return response

    async def handle_resolve_data_shares(
        self,
        request: datahub_v1_data_share_query_service_pb2.ResolveDataSharesRequest
    ) -> datahub_v1_data_share_query_service_pb2.ResolveDataSharesResponse:
        """Returns several data shares at once."""
        deps = self.deps
        response = datahub_v1_data_share_query_service_pb2.ResolveDataSharesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ResolveDataShares', extra={'fields': {'domain': 'datahub'}})
            await deps.repository.audit(request.context.tenant_id, 'ResolveDataShares', {})
            response_0 = datahub_v1_workspace_integration_service_pb2.AcknowledgeWorkspaceEventResponse()
            response_1 = datahub_v1_notebook_approval_service_pb2.RecallNotebookResponse()
            outgoing_0 = datahub_v1_workspace_integration_service_pb2.AcknowledgeWorkspaceEventRequest(
                context=request.context,
                details=datahub_v1_workspace_integration_service_pb2.AcknowledgeWorkspaceEventRequest.Details(
                    message_id=request.context.trace_id,
                    received_at=request.context.deadline
                )
            )
            response_0 = await deps.clients.datahub_workspace_integration.AcknowledgeWorkspaceEvent(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = datahub_v1_notebook_approval_service_pb2.RecallNotebookRequest()
            outgoing_1.context.CopyFrom(request.context)
            outgoing_1.details.approver.display_name = response_0.workspace.assignee.display_name
            outgoing_1.details.approver.email = response_0.workspace.assignee.email
            merged_1 = datahub_v1_notebook_approval_service_pb2.RecallNotebookRequest()
            merged_1.MergeFrom(outgoing_1)
            outgoing_1.CopyFrom(merged_1)
            response_1 = await deps.clients.datahub_notebook_approval.RecallNotebook(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_0)
            returned_0_1 = response_0.workspace.audit.updated_at
            returned_0_1_part_0 = response.data_shares.add()
            if returned_0_1.ListFields():
                returned_0_1_part_0.audit.updated_at.MergeFrom(returned_0_1)
            returned_1_0 = response_1.notebook.audit.etag
            returned_1_0_part_0 = response.data_shares.add()
            if returned_1_0:
                returned_1_0_part_0.audit.etag = returned_1_0
            returned_1_1 = response_1.notebook.issued_at
            returned_1_1_part_0 = response.data_shares.add()
            if returned_1_1.ListFields():
                returned_1_1_part_0.issued_at.MergeFrom(returned_1_1)
            return response

    async def handle_suggest_data_shares(
        self,
        request: datahub_v1_data_share_query_service_pb2.SuggestDataSharesRequest
    ) -> datahub_v1_data_share_query_service_pb2.SuggestDataSharesResponse:
        """Lists data shares a page at a time."""
        deps = self.deps
        response = datahub_v1_data_share_query_service_pb2.SuggestDataSharesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SuggestDataShares', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(request.context.tenant_id, 'SuggestDataShares', {'order_by': request.order_by})
            response_0 = featureflags_v1_feature_flag_query_service_pb2.SummarizeFeatureFlagsResponse()
            response_1 = datahub_v1_notebook_notification_service_pb2.SubscribeNotebookUpdatesResponse()
            outgoing_0 = featureflags_v1_feature_flag_query_service_pb2.SummarizeFeatureFlagsRequest(
                annotations=dict(request.context.baggage),
                context=request.context,
                details=featureflags_v1_feature_flag_query_service_pb2.SummarizeFeatureFlagsRequest.Details(
                    filters=dict(request.filter.labels)
                )
            )
            response_0 = await deps.clients.featureflags_feature_flag_query.SummarizeFeatureFlags(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = datahub_v1_notebook_notification_service_pb2.SubscribeNotebookUpdatesRequest(
                context=request.context,
                details=datahub_v1_notebook_notification_service_pb2.SubscribeNotebookUpdatesRequest.Details(
                    recipient=common_v1_contact_pb2.ContactInfo(email=request.context.actor.email),
                    variables=dict(response_0.summary)
                )
            )
            registered_1 = cast(
                datahub_v1_notebook_notification_service_pb2_grpc.NotebookNotificationServiceStub,
                deps.clients.registry['acme.datahub.v1.NotebookNotificationService']
            )
            response_1 = await registered_1.SubscribeNotebookUpdates(outgoing_1, timeout=deps.settings.timeout)
            returned_0_0 = response_0.result.details
            response.result.details.update(returned_0_0)
            returned_1_0 = response_1.notebook.billing_address.country_code
            returned_1_0_part_0 = response.data_shares.add()
            if returned_1_0:
                returned_1_0_part_0.billing_address.country_code = returned_1_0
            return response

    async def handle_summarize_data_shares(
        self,
        request: datahub_v1_data_share_query_service_pb2.SummarizeDataSharesRequest
    ) -> datahub_v1_data_share_query_service_pb2.SummarizeDataSharesResponse:
        """Summarizes a data share."""
        deps = self.deps
        response = datahub_v1_data_share_query_service_pb2.SummarizeDataSharesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SummarizeDataShares', extra={'fields': {'data_share_id': request.data_share_id}})
            await deps.repository.audit(
                request.context.tenant_id,
                'SummarizeDataShares',
                {'data_share_id': request.data_share_id}
            )
            response_0 = anomalies_v1_anomaly_feedback_approval_service_pb2.RecallAnomalyFeedbackResponse()
            response_1 = customers_v1_preference_sync_service_pb2.ReconcilePreferencesResponse()
            response_2 = datahub_v1_notebook_workflow_service_pb2.AdvanceNotebookWorkflowResponse()
            command_0 = DataShareQuerySummarizeDataShares0Command(context=request.context, reason=request.reason)
            outgoing_0 = to_data_share_query_summarize_data_shares0_command(command_0)
            response_0 = await deps.clients.anomalies_anomaly_feedback_approval.RecallAnomalyFeedback(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            command_1 = DataShareQuerySummarizeDataShares1Command.model_validate(
                {
                    'context': request.context,
                    'preference_owner_display_name': response_0.anomaly_feedback.subject.display_name,
                    'preference_block_reason': request.reason,
                    'annotations': dict(request.annotations),
                    'preference_block_notify_email': request.context.actor.email
                }
            )
            outgoing_1 = to_data_share_query_summarize_data_shares1_command(command_1)
            response_1 = await deps.clients.customers_preference_sync.ReconcilePreferences(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = datahub_v1_notebook_workflow_service_pb2.AdvanceNotebookWorkflowRequest()
            outgoing_2.context.CopyFrom(request.context)
            if response_1.preference.WhichOneof('action') == 'discount':
                field_2_1_part_1 = outgoing_2.notebook.lines.add()
                field_2_1_part_1.tax.amount.CopyFrom(response_1.preference.discount.amount)
            outgoing_2.notebook.audit.created_by = response_1.preference.audit.created_by
            outgoing_2.notebook.audit.updated_at.CopyFrom(response_1.preference.audit.updated_at)
            response_2 = await deps.clients.datahub_notebook_workflow.AdvanceNotebookWorkflow(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.correlation_id
            if returned_0_0:
                response.result.correlation_id = returned_0_0
            returned_0_1 = response_0.outcome.status
            if returned_0_1:
                response.result.status = returned_0_1
            returned_1_0 = response_1.outcome.status
            if returned_1_0:
                response.result.status = returned_1_0
            returned_1_1 = response_1.result.message
            if returned_1_1:
                response.result.message = returned_1_1
            returned_2_0 = response_2.result.message
            if returned_2_0:
                response.result.message = returned_2_0
            echoed_0 = request.details.period
            response.period.CopyFrom(echoed_0)
            return response
