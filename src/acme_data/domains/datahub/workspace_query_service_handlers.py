"""Reusable transport mixin for WorkspaceQueryService."""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any
import logging

from google.protobuf.any_pb2 import Any as AnyMessage
import grpc

from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.customers.v1 import consent_record_reporting_service_pb2 as customers_v1_consent_record_reporting_service_pb2
from acme.customers.v1 import consent_record_sync_service_pb2 as customers_v1_consent_record_sync_service_pb2
from acme.datahub.v1 import data_share_approval_service_pb2 as datahub_v1_data_share_approval_service_pb2
from acme.datahub.v1 import data_share_validation_service_pb2 as datahub_v1_data_share_validation_service_pb2
from acme.datahub.v1 import datahub_pb2 as datahub_v1_datahub_pb2
from acme.datahub.v1 import notebook_workflow_service_pb2 as datahub_v1_notebook_workflow_service_pb2
from acme.datahub.v1 import refs_pb2 as datahub_v1_refs_pb2
from acme.datahub.v1 import workspace_approval_service_pb2 as datahub_v1_workspace_approval_service_pb2
from acme.datahub.v1 import workspace_notification_service_pb2 as datahub_v1_workspace_notification_service_pb2
from acme.datahub.v1 import workspace_query_service_pb2 as datahub_v1_workspace_query_service_pb2
from acme.datahub.v1 import workspace_reporting_service_pb2 as datahub_v1_workspace_reporting_service_pb2
from acme.documents.v1 import document_service_pb2 as documents_v1_document_service_pb2
from acme.featurestore.v1 import feature_view_workflow_service_pb2 as featurestore_v1_feature_view_workflow_service_pb2
from acme.featurestore.v1 import featurestore_pb2 as featurestore_v1_featurestore_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2

from acme_data.domains.datahub.dependencies import Dependencies
from acme_data.domains.datahub.models import WorkspaceQuerySummarizeWorkspaces0Command
from acme_data.domains.datahub.models import WorkspaceQuerySummarizeWorkspaces1Command
from acme_data.domains.datahub.models import to_workspace_query_summarize_workspaces0_command
from acme_data.domains.datahub.models import to_workspace_query_summarize_workspaces1_command
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class WorkspaceQueryServicerHandlers:
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    @retry_transient
    async def BrowseWorkspaces(
        self, request: datahub_v1_workspace_query_service_pb2.BrowseWorkspacesRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_workspace_query_service_pb2.BrowseWorkspacesResponse:
        """Lists workspaces a page at a time."""
        return await self.handle_browse_workspaces(request)

    @rpc_errors
    @retry_transient
    async def CountWorkspaces(
        self, request: datahub_v1_workspace_query_service_pb2.CountWorkspacesRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_workspace_query_service_pb2.CountWorkspacesResponse:
        """Counts workspaces by status."""
        return await self.handle_count_workspaces(request)

    @stream_errors
    async def ExportWorkspaces(
        self, request: datahub_v1_workspace_query_service_pb2.ExportWorkspacesRequest, context: grpc.aio.ServicerContext,
    ) -> AsyncIterator[datahub_v1_workspace_query_service_pb2.ExportWorkspacesResponse]:
        """Streams every matching workspace."""
        response = await self.handle_export_workspaces(request)
        for item in messages((response,)):
            yield item

    @rpc_errors
    @retry_transient
    async def FindWorkspaces(
        self, request: datahub_v1_workspace_query_service_pb2.FindWorkspacesRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_workspace_query_service_pb2.FindWorkspacesResponse:
        """Lists workspaces a page at a time."""
        return await self.handle_find_workspaces(request)

    @rpc_errors
    @retry_transient
    async def LookupWorkspace(
        self, request: datahub_v1_workspace_query_service_pb2.LookupWorkspaceRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_workspace_query_service_pb2.LookupWorkspaceResponse:
        """Returns a workspace."""
        return await self.handle_lookup_workspace(request)

    @rpc_errors
    @retry_transient
    async def PeekWorkspace(
        self, request: datahub_v1_workspace_query_service_pb2.PeekWorkspaceRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_workspace_query_service_pb2.PeekWorkspaceResponse:
        """Returns a workspace."""
        return await self.handle_peek_workspace(request)

    @rpc_errors
    @retry_transient
    async def ResolveWorkspaces(
        self, request: datahub_v1_workspace_query_service_pb2.ResolveWorkspacesRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_workspace_query_service_pb2.ResolveWorkspacesResponse:
        """Returns several workspaces at once."""
        return await self.handle_resolve_workspaces(request)

    @rpc_errors
    @retry_transient
    async def SuggestWorkspaces(
        self, request: datahub_v1_workspace_query_service_pb2.SuggestWorkspacesRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_workspace_query_service_pb2.SuggestWorkspacesResponse:
        """Lists workspaces a page at a time."""
        return await self.handle_suggest_workspaces(request)

    @rpc_errors
    async def SummarizeWorkspaces(
        self, request: datahub_v1_workspace_query_service_pb2.SummarizeWorkspacesRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_workspace_query_service_pb2.SummarizeWorkspacesResponse:
        """Summarizes a workspace."""
        return await self.handle_summarize_workspaces(request)

    async def handle_browse_workspaces(
        self,
        request: datahub_v1_workspace_query_service_pb2.BrowseWorkspacesRequest
    ) -> datahub_v1_workspace_query_service_pb2.BrowseWorkspacesResponse:
        """Lists workspaces a page at a time."""
        deps = self.deps
        response = datahub_v1_workspace_query_service_pb2.BrowseWorkspacesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('BrowseWorkspaces', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(request.context.tenant_id, 'BrowseWorkspaces', {'order_by': request.order_by})
            return response

    async def handle_count_workspaces(
        self,
        request: datahub_v1_workspace_query_service_pb2.CountWorkspacesRequest
    ) -> datahub_v1_workspace_query_service_pb2.CountWorkspacesResponse:
        """Counts workspaces by status."""
        deps = self.deps
        response = datahub_v1_workspace_query_service_pb2.CountWorkspacesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CountWorkspaces', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(request.context.tenant_id, 'CountWorkspaces', {'order_by': request.order_by})
            response_0 = documents_v1_document_service_pb2.WatchDocumentsResponse()
            outgoing_0 = documents_v1_document_service_pb2.WatchDocumentsRequest(
                context=request.context,
                filter=documents_v1_document_service_pb2.WatchDocumentsRequest.Filter(
                    labels=dict(request.filter.labels),
                    owner_id=request.filter.owner_id,
                    query=request.filter.query,
                    region=request.filter.region
                )
            )
            async for chunk_0 in deps.clients.documents_document.WatchDocuments(
                outgoing_0,
                timeout=deps.settings.timeout
            ):
                response_0 = chunk_0
            return response

    async def handle_export_workspaces(
        self,
        request: datahub_v1_workspace_query_service_pb2.ExportWorkspacesRequest
    ) -> datahub_v1_workspace_query_service_pb2.ExportWorkspacesResponse:
        """Streams every matching workspace."""
        deps = self.deps
        response = datahub_v1_workspace_query_service_pb2.ExportWorkspacesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ExportWorkspaces', extra={'fields': {'destination_uri': request.destination_uri}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ExportWorkspaces',
                {'destination_uri': request.destination_uri}
            )
            response_0 = datahub_v1_workspace_notification_service_pb2.SubscribeWorkspaceUpdatesResponse()
            response_1 = datahub_v1_workspace_reporting_service_pb2.CountWorkspaceTotalsResponse()
            response_2 = customers_v1_consent_record_reporting_service_pb2.ShareConsentRecordReportResponse()
            outgoing_0 = datahub_v1_workspace_notification_service_pb2.SubscribeWorkspaceUpdatesRequest(
                annotations=dict(request.filter.labels),
                context=request.context,
                details=datahub_v1_workspace_notification_service_pb2.SubscribeWorkspaceUpdatesRequest.Details(
                    recipient=common_v1_contact_pb2.ContactInfo(email=request.context.actor.email),
                    variables=dict(request.context.baggage)
                )
            )
            response_0 = await deps.clients.datahub_workspace_notification.SubscribeWorkspaceUpdates(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = datahub_v1_workspace_reporting_service_pb2.CountWorkspaceTotalsRequest(
                context=request.context,
                filter=datahub_v1_workspace_reporting_service_pb2.CountWorkspaceTotalsRequest.Filter(
                    labels=dict(request.filter.labels),
                    owner_id=request.filter.owner_id,
                    statuses=list(request.filter.statuses)
                )
            )
            method_name_1 = 'CountWorkspaceTotals'
            response_1 = await getattr(
                deps.clients.datahub_workspace_reporting,
                method_name_1
            )(outgoing_1, timeout=deps.settings.timeout)
            fields_2: dict[str, Any] = {
                'context': request.context,
                'details': {'recipient': {'email': response_0.workspace.assignee.email}}
            }
            outgoing_2 = customers_v1_consent_record_reporting_service_pb2.ShareConsentRecordReportRequest(**fields_2)
            response_2 = await deps.clients.customers_consent_record_reporting.ShareConsentRecordReport(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.workspace.assignee.display_name
            if returned_0_0:
                response.workspace.assignee.display_name = returned_0_0
            returned_0_1 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_1)
            returned_1_0 = response_1.result.status
            if returned_1_0:
                response.result.status = returned_1_0
            returned_1_1 = response_1.result.message
            if returned_1_1:
                response.result.message = returned_1_1
            returned_2_0 = response_2.outcome.message
            if returned_2_0:
                response.result.message = returned_2_0
            returned_2_1 = response_2.outcome.status
            if returned_2_1:
                response.result.status = returned_2_1
            return response

    async def handle_find_workspaces(
        self,
        request: datahub_v1_workspace_query_service_pb2.FindWorkspacesRequest
    ) -> datahub_v1_workspace_query_service_pb2.FindWorkspacesResponse:
        """Lists workspaces a page at a time."""
        deps = self.deps
        response = datahub_v1_workspace_query_service_pb2.FindWorkspacesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('FindWorkspaces', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(request.context.tenant_id, 'FindWorkspaces', {'order_by': request.order_by})
            response_0 = featurestore_v1_feature_view_workflow_service_pb2.AdvanceFeatureViewWorkflowResponse()
            outgoing_0 = featurestore_v1_feature_view_workflow_service_pb2.AdvanceFeatureViewWorkflowRequest(
                context=request.context,
                feature_view=featurestore_v1_featurestore_pb2.FeatureView(
                    address=common_v1_address_pb2.PostalAddress(region=request.filter.region),
                    audit=common_v1_audit_pb2.AuditInfo(created_at=request.filter.created_after),
                    owner=identity_v1_refs_pb2.UserRef(
                        email=request.context.actor.email,
                        user_id=request.context.actor.user_id
                    )
                )
            )
            response_0 = await deps.clients.featurestore_feature_view_workflow.AdvanceFeatureViewWorkflow(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.outcome.status
            if returned_0_0:
                response.result.status = returned_0_0
            return response

    async def handle_lookup_workspace(
        self,
        request: datahub_v1_workspace_query_service_pb2.LookupWorkspaceRequest
    ) -> datahub_v1_workspace_query_service_pb2.LookupWorkspaceResponse:
        """Returns a workspace."""
        deps = self.deps
        response = datahub_v1_workspace_query_service_pb2.LookupWorkspaceResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('LookupWorkspace', extra={'fields': {'domain': 'datahub'}})
            await deps.repository.audit(request.context.tenant_id, 'LookupWorkspace', {})
            response_0 = datahub_v1_workspace_approval_service_pb2.RecallWorkspaceResponse()
            outgoing_0 = datahub_v1_workspace_approval_service_pb2.RecallWorkspaceRequest(
                context=request.context,
                details=datahub_v1_workspace_approval_service_pb2.RecallWorkspaceRequest.Details(
                    approver=identity_v1_refs_pb2.UserRef(user_id=request.context.actor.user_id)
                ),
                workspace=datahub_v1_datahub_pb2.Workspace(
                    requester=common_v1_contact_pb2.ContactInfo(email=request.context.actor.email),
                    workspace_id=request.workspace_id
                )
            )
            response_0 = await deps.clients.datahub_workspace_approval.RecallWorkspace(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.workspace.audit.etag
            if returned_0_0:
                response.workspace.audit.etag = returned_0_0
            returned_0_1 = response_0.workspace.customer.display_name
            if returned_0_1:
                response.workspace.assignee.display_name = returned_0_1
            echoed_0 = request.workspace_id
            response.workspace.workspace_id = echoed_0
            return response

    async def handle_peek_workspace(
        self,
        request: datahub_v1_workspace_query_service_pb2.PeekWorkspaceRequest
    ) -> datahub_v1_workspace_query_service_pb2.PeekWorkspaceResponse:
        """Returns a workspace."""
        deps = self.deps
        response = datahub_v1_workspace_query_service_pb2.PeekWorkspaceResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('PeekWorkspace', extra={'fields': {'domain': 'datahub'}})
            await deps.repository.audit(request.context.tenant_id, 'PeekWorkspace', {})
            response_0 = datahub_v1_notebook_workflow_service_pb2.RetryNotebookWorkflowResponse()
            response_1 = datahub_v1_workspace_notification_service_pb2.GetWorkspacePreferencesResponse()
            outgoing_0 = datahub_v1_notebook_workflow_service_pb2.RetryNotebookWorkflowRequest(
                context=request.context,
                notebook=datahub_v1_datahub_pb2.Notebook(
                    counterparty=datahub_v1_refs_pb2.WorkspaceRef(workspace_id=request.workspace_id)
                )
            )
            response_0 = await deps.clients.datahub_notebook_workflow.RetryNotebookWorkflow(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = datahub_v1_workspace_notification_service_pb2.GetWorkspacePreferencesRequest(
                context=request.context,
                workspace_id=request.workspace_id
            )
            envelope_1 = AnyMessage()
            envelope_1.Pack(outgoing_1)
            outgoing_1 = datahub_v1_workspace_notification_service_pb2.GetWorkspacePreferencesRequest()
            if not envelope_1.Unpack(outgoing_1):
                raise ValueError("partner envelope contains the wrong request type")
            response_1 = await deps.clients.datahub_workspace_notification.GetWorkspacePreferences(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.notebook.counterparty.display_name
            if returned_0_0:
                response.workspace.assignee.display_name = returned_0_0
            returned_0_1 = response_0.outcome.message
            if returned_0_1:
                response.result.message = returned_0_1
            returned_1_0 = response_1.workspace.status
            if returned_1_0:
                response.workspace.status = returned_1_0
            echoed_0 = request.workspace_id
            response.workspace.workspace_id = echoed_0
            return response

    async def handle_resolve_workspaces(
        self,
        request: datahub_v1_workspace_query_service_pb2.ResolveWorkspacesRequest
    ) -> datahub_v1_workspace_query_service_pb2.ResolveWorkspacesResponse:
        """Returns several workspaces at once."""
        deps = self.deps
        response = datahub_v1_workspace_query_service_pb2.ResolveWorkspacesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ResolveWorkspaces', extra={'fields': {'locale': request.context.locale}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ResolveWorkspaces',
                {'locale': request.context.locale}
            )
            return response

    async def handle_suggest_workspaces(
        self,
        request: datahub_v1_workspace_query_service_pb2.SuggestWorkspacesRequest
    ) -> datahub_v1_workspace_query_service_pb2.SuggestWorkspacesResponse:
        """Lists workspaces a page at a time."""
        deps = self.deps
        response = datahub_v1_workspace_query_service_pb2.SuggestWorkspacesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SuggestWorkspaces', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(request.context.tenant_id, 'SuggestWorkspaces', {'order_by': request.order_by})
            response_0 = datahub_v1_data_share_validation_service_pb2.LintDataSharesResponse()
            outgoing_0 = datahub_v1_data_share_validation_service_pb2.LintDataSharesRequest(
                context=request.context,
                data_share=datahub_v1_datahub_pb2.DataShare(
                    audit=common_v1_audit_pb2.AuditInfo(created_at=request.filter.created_after),
                    billing_address=common_v1_address_pb2.PostalAddress(region=request.filter.region)
                ),
                details=datahub_v1_data_share_validation_service_pb2.LintDataSharesRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(email=request.context.actor.email),
                    locale=request.context.locale
                )
            )
            response_0 = await deps.clients.datahub_data_share_validation.LintDataShares(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.data_share.audit.created_by
            returned_0_0_part_0 = response.workspaces.add()
            if returned_0_0:
                returned_0_0_part_0.audit.created_by = returned_0_0
            returned_0_1 = response_0.result.message
            if returned_0_1:
                response.result.message = returned_0_1
            return response

    async def handle_summarize_workspaces(
        self,
        request: datahub_v1_workspace_query_service_pb2.SummarizeWorkspacesRequest
    ) -> datahub_v1_workspace_query_service_pb2.SummarizeWorkspacesResponse:
        """Summarizes a workspace."""
        deps = self.deps
        response = datahub_v1_workspace_query_service_pb2.SummarizeWorkspacesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SummarizeWorkspaces', extra={'fields': {'cron': request.details.cron}})
            await deps.repository.audit(
                request.context.tenant_id,
                'SummarizeWorkspaces',
                {'cron': request.details.cron}
            )
            response_0 = datahub_v1_data_share_approval_service_pb2.ListPendingDataSharesResponse()
            response_1 = customers_v1_consent_record_sync_service_pb2.PushConsentRecordResponse()
            command_0 = WorkspaceQuerySummarizeWorkspaces0Command(
                context=request.context,
                filter_labels=dict(request.details.filters),
                filter_owner_id=request.workspace_id
            )
            outgoing_0 = to_workspace_query_summarize_workspaces0_command(command_0)
            response_0 = await deps.clients.datahub_data_share_approval.ListPendingDataShares(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            command_1 = WorkspaceQuerySummarizeWorkspaces1Command.model_validate(
                {
                    'context': request.context,
                    'consent_record_correlation_id': response_0.result.correlation_id,
                    'reason': request.reason
                }
            )
            outgoing_1 = to_workspace_query_summarize_workspaces1_command(command_1)
            response_1 = await deps.clients.customers_consent_record_sync.PushConsentRecord(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.details
            response.result.details.update(returned_0_0)
            returned_0_1 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_1)
            returned_1_0 = response_1.result.status
            if returned_1_0:
                response.result.status = returned_1_0
            echoed_0 = request.details.period
            response.period.CopyFrom(echoed_0)
            return response
