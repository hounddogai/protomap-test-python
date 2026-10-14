"""Answers read-only questions about notebooks, for screens and reports."""

from __future__ import annotations

from collections.abc import AsyncIterator
from functools import partial
from typing import cast
import logging

from google.protobuf.any_pb2 import Any as AnyMessage
import grpc

from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.customers.v1 import household_workflow_service_pb2 as customers_v1_household_workflow_service_pb2
from acme.customers.v1 import preference_sync_service_pb2 as customers_v1_preference_sync_service_pb2
from acme.datahub.v1 import datahub_pb2 as datahub_v1_datahub_pb2
from acme.datahub.v1 import notebook_approval_service_pb2 as datahub_v1_notebook_approval_service_pb2
from acme.datahub.v1 import notebook_query_service_pb2 as datahub_v1_notebook_query_service_pb2
from acme.datahub.v1 import notebook_query_service_pb2_grpc as datahub_v1_notebook_query_service_pb2_grpc
from acme.featurestore.v1 import entity_reporting_service_pb2 as featurestore_v1_entity_reporting_service_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.lineage.v1 import lineage_edge_workflow_service_pb2 as lineage_v1_lineage_edge_workflow_service_pb2
from acme.lineage.v1 import lineage_pb2 as lineage_v1_lineage_pb2
from acme.metrics.v1 import dashboard_sync_service_pb2 as metrics_v1_dashboard_sync_service_pb2
from acme.metrics.v1 import dashboard_validation_service_pb2 as metrics_v1_dashboard_validation_service_pb2
from acme.metrics.v1 import metric_series_export_service_pb2 as metrics_v1_metric_series_export_service_pb2
from acme.metrics.v1 import metrics_pb2 as metrics_v1_metrics_pb2
from acme.search.v1 import search_index_validation_service_pb2 as search_v1_search_index_validation_service_pb2
from acme.search.v1 import (
    search_index_validation_service_pb2_grpc as search_v1_search_index_validation_service_pb2_grpc,
)
from acme.search.v1 import search_pb2 as search_v1_search_pb2

from acme_data.domains.datahub.dependencies import Dependencies
from acme_data.domains.datahub.models import NotebookQueryExportNotebooks2Command
from acme_data.domains.datahub.models import to_notebook_query_export_notebooks2_command
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class NotebookQueryServicer(datahub_v1_notebook_query_service_pb2_grpc.NotebookQueryServiceServicer):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    @retry_transient
    async def BrowseNotebooks(
        self, request: datahub_v1_notebook_query_service_pb2.BrowseNotebooksRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_notebook_query_service_pb2.BrowseNotebooksResponse:
        """Lists notebooks a page at a time."""
        return await self.handle_browse_notebooks(request)

    @rpc_errors
    @retry_transient
    async def CountNotebooks(
        self, request: datahub_v1_notebook_query_service_pb2.CountNotebooksRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_notebook_query_service_pb2.CountNotebooksResponse:
        """Counts notebooks by status."""
        return await self.handle_count_notebooks(request)

    @stream_errors
    async def ExportNotebooks(
        self, request: datahub_v1_notebook_query_service_pb2.ExportNotebooksRequest, context: grpc.aio.ServicerContext,
    ) -> AsyncIterator[datahub_v1_notebook_query_service_pb2.ExportNotebooksResponse]:
        """Streams every matching notebook."""
        response = await self.handle_export_notebooks(request)
        for item in messages((response,)):
            yield item

    @rpc_errors
    @retry_transient
    async def FindNotebooks(
        self, request: datahub_v1_notebook_query_service_pb2.FindNotebooksRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_notebook_query_service_pb2.FindNotebooksResponse:
        """Lists notebooks a page at a time."""
        return await self.handle_find_notebooks(request)

    @rpc_errors
    @retry_transient
    async def LookupNotebook(
        self, request: datahub_v1_notebook_query_service_pb2.LookupNotebookRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_notebook_query_service_pb2.LookupNotebookResponse:
        """Returns a notebook."""
        return await self.handle_lookup_notebook(request)

    @rpc_errors
    @retry_transient
    async def PeekNotebook(
        self, request: datahub_v1_notebook_query_service_pb2.PeekNotebookRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_notebook_query_service_pb2.PeekNotebookResponse:
        """Returns a notebook."""
        return await self.handle_peek_notebook(request)

    @rpc_errors
    @retry_transient
    async def ResolveNotebooks(
        self, request: datahub_v1_notebook_query_service_pb2.ResolveNotebooksRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_notebook_query_service_pb2.ResolveNotebooksResponse:
        """Returns several notebooks at once."""
        return await self.handle_resolve_notebooks(request)

    @rpc_errors
    @retry_transient
    async def SuggestNotebooks(
        self, request: datahub_v1_notebook_query_service_pb2.SuggestNotebooksRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_notebook_query_service_pb2.SuggestNotebooksResponse:
        """Lists notebooks a page at a time."""
        return await self.handle_suggest_notebooks(request)

    async def handle_browse_notebooks(
        self,
        request: datahub_v1_notebook_query_service_pb2.BrowseNotebooksRequest
    ) -> datahub_v1_notebook_query_service_pb2.BrowseNotebooksResponse:
        """Lists notebooks a page at a time."""
        deps = self.deps
        response = datahub_v1_notebook_query_service_pb2.BrowseNotebooksResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('BrowseNotebooks', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(request.context.tenant_id, 'BrowseNotebooks', {'order_by': request.order_by})
            response_0 = datahub_v1_notebook_approval_service_pb2.DelegateNotebookApprovalResponse()
            outgoing_0 = datahub_v1_notebook_approval_service_pb2.DelegateNotebookApprovalRequest(
                context=request.context,
                details=datahub_v1_notebook_approval_service_pb2.DelegateNotebookApprovalRequest.Details(
                    approver=identity_v1_refs_pb2.UserRef(
                        email=request.context.actor.email,
                        user_id=request.context.actor.user_id
                    )
                ),
                notebook=datahub_v1_datahub_pb2.Notebook(
                    billing_address=common_v1_address_pb2.PostalAddress(region=request.filter.region)
                )
            )
            response_0 = await deps.clients.datahub_notebook_approval.DelegateNotebookApproval(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.notebook.audit.updated_at
            returned_0_0_part_0 = response.notebooks.add()
            if returned_0_0.ListFields():
                returned_0_0_part_0.audit.updated_at.MergeFrom(returned_0_0)
            returned_0_1 = response_0.outcome.status
            if returned_0_1:
                response.result.status = returned_0_1
            return response

    async def handle_count_notebooks(
        self,
        request: datahub_v1_notebook_query_service_pb2.CountNotebooksRequest
    ) -> datahub_v1_notebook_query_service_pb2.CountNotebooksResponse:
        """Counts notebooks by status."""
        deps = self.deps
        response = datahub_v1_notebook_query_service_pb2.CountNotebooksResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CountNotebooks', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(request.context.tenant_id, 'CountNotebooks', {'order_by': request.order_by})
            response_0 = featurestore_v1_entity_reporting_service_pb2.CountEntityTotalsResponse()
            response_1 = lineage_v1_lineage_edge_workflow_service_pb2.StartLineageEdgeWorkflowResponse()
            outgoing_0 = featurestore_v1_entity_reporting_service_pb2.CountEntityTotalsRequest(
                context=request.context,
                filter=featurestore_v1_entity_reporting_service_pb2.CountEntityTotalsRequest.Filter(
                    owner_id=request.filter.owner_id
                )
            )
            response_0 = await deps.clients.featurestore_entity_reporting.CountEntityTotals(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = lineage_v1_lineage_edge_workflow_service_pb2.StartLineageEdgeWorkflowRequest(
                context=request.context,
                lineage_edge=lineage_v1_lineage_pb2.LineageEdge(correlation_id=response_0.result.correlation_id)
            )
            envelope_1 = AnyMessage()
            envelope_1.Pack(outgoing_1)
            outgoing_1 = lineage_v1_lineage_edge_workflow_service_pb2.StartLineageEdgeWorkflowRequest()
            if not envelope_1.Unpack(outgoing_1):
                raise ValueError("partner envelope contains the wrong request type")
            response_1 = await deps.clients.lineage_lineage_edge_workflow.StartLineageEdgeWorkflow(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.result.message = returned_0_0
            returned_1_0 = response_1.result.details
            response.result.details.update(returned_1_0)
            returned_1_1 = response_1.result.status
            if returned_1_1:
                response.result.status = returned_1_1
            return response

    async def handle_export_notebooks(
        self,
        request: datahub_v1_notebook_query_service_pb2.ExportNotebooksRequest
    ) -> datahub_v1_notebook_query_service_pb2.ExportNotebooksResponse:
        """Streams every matching notebook."""
        deps = self.deps
        response = datahub_v1_notebook_query_service_pb2.ExportNotebooksResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ExportNotebooks', extra={'fields': {'destination_uri': request.destination_uri}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ExportNotebooks',
                {'destination_uri': request.destination_uri}
            )
            response_0 = search_v1_search_index_validation_service_pb2.CheckSearchIndexEligibilityResponse()
            response_1 = customers_v1_household_workflow_service_pb2.ResumeHouseholdWorkflowResponse()
            response_2 = customers_v1_preference_sync_service_pb2.PushPreferenceResponse()
            response_3 = metrics_v1_dashboard_sync_service_pb2.SyncDashboardsResponse()
            outgoing_0 = search_v1_search_index_validation_service_pb2.CheckSearchIndexEligibilityRequest(
                context=request.context,
                search_index=search_v1_search_pb2.SearchIndex(
                    address=common_v1_address_pb2.PostalAddress(region=request.filter.region)
                )
            )
            registered_0 = cast(
                search_v1_search_index_validation_service_pb2_grpc.SearchIndexValidationServiceStub,
                deps.clients.registry['acme.search.v1.SearchIndexValidationService']
            )
            response_0 = await registered_0.CheckSearchIndexEligibility(outgoing_0, timeout=deps.settings.timeout)
            outgoing_1 = customers_v1_household_workflow_service_pb2.ResumeHouseholdWorkflowRequest()
            outgoing_1.context.CopyFrom(request.context)
            field_1_1_part_1 = outgoing_1.household.children.add()
            field_1_1_part_2 = field_1_1_part_1.children.add()
            field_1_1_part_2.audit.created_by = response_0.search_index.audit.created_by
            if response_0.search_index.WhichOneof('locator') == 'address':
                field_1_2_part_1 = outgoing_1.household.children.add()
                field_1_2_part_2 = field_1_2_part_1.children.add()
                field_1_2_part_2.location.postal_code = response_0.search_index.address.postal_code
            field_1_3_part_1 = outgoing_1.household.children.add()
            field_1_3_part_1.audit.etag = response_0.search_index.audit.etag
            if response_0.search_index.WhichOneof('locator') == 'address':
                field_1_4_part_1 = outgoing_1.household.children.add()
                field_1_4_part_1.location.region = response_0.search_index.address.region
            response_1 = await deps.clients.customers_household_workflow.ResumeHouseholdWorkflow(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            command_2 = NotebookQueryExportNotebooks2Command.model_validate(
                {
                    'context': request.context,
                    'preference_audit_updated_by': response_1.household.audit.updated_by,
                    'preference_audit_created_at': response_1.household.audit.created_at,
                    'preference_description': response_0.search_index.components.get(
                        'primary',
                        search_v1_search_pb2.SearchIndexComponent()
                    ).description
                }
            )
            outgoing_2 = to_notebook_query_export_notebooks2_command(command_2)
            response_2 = await deps.clients.customers_preference_sync.PushPreference(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            outgoing_3 = metrics_v1_dashboard_sync_service_pb2.SyncDashboardsRequest(
                context=request.context,
                dashboard=metrics_v1_metrics_pb2.Dashboard(
                    audit=common_v1_audit_pb2.AuditInfo(created_by=response_2.preference.audit.created_by),
                    billing_address=common_v1_address_pb2.PostalAddress(
                        country_code=response_0.search_index.address.country_code,
                        lines=list(response_1.household.location.lines),
                        postal_code=response_1.household.location.postal_code
                    )
                )
            )
            send_3 = partial(deps.clients.metrics_dashboard_sync.SyncDashboards, timeout=deps.settings.timeout)
            response_3 = await send_3(outgoing_3)
            returned_0_0 = response_0.search_index.audit.updated_by
            if returned_0_0:
                response.notebook.audit.updated_by = returned_0_0
            returned_1_0 = response_1.household.location.postal_code
            if returned_1_0:
                response.notebook.billing_address.postal_code = returned_1_0
            returned_1_1 = response_1.result.status
            if returned_1_1:
                response.result.status = returned_1_1
            returned_2_0 = response_2.result.message
            if returned_2_0:
                response.result.message = returned_2_0
            returned_3_0 = response_3.result.message
            if returned_3_0:
                response.result.message = returned_3_0
            returned_3_1 = response_3.dashboard.notes
            if returned_3_1:
                response.notebook.notes = returned_3_1
            echoed_0 = request.filter.region
            response.notebook.billing_address.region = echoed_0
            return response

    async def handle_find_notebooks(
        self,
        request: datahub_v1_notebook_query_service_pb2.FindNotebooksRequest
    ) -> datahub_v1_notebook_query_service_pb2.FindNotebooksResponse:
        """Lists notebooks a page at a time."""
        deps = self.deps
        response = datahub_v1_notebook_query_service_pb2.FindNotebooksResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('FindNotebooks', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(request.context.tenant_id, 'FindNotebooks', {'order_by': request.order_by})
            response_0 = metrics_v1_metric_series_export_service_pb2.StreamMetricSeriesExportResponse()
            outgoing_0 = metrics_v1_metric_series_export_service_pb2.StreamMetricSeriesExportRequest(
                context=request.context,
                filter=metrics_v1_metric_series_export_service_pb2.StreamMetricSeriesExportRequest.Filter(
                    created_after=request.filter.created_after,
                    labels=dict(request.filter.labels),
                    query=request.filter.query,
                    region=request.filter.region
                )
            )
            async for chunk_0 in deps.clients.metrics_metric_series_export.StreamMetricSeriesExport(
                outgoing_0,
                timeout=deps.settings.timeout
            ):
                response_0 = chunk_0
            return response

    async def handle_lookup_notebook(
        self,
        request: datahub_v1_notebook_query_service_pb2.LookupNotebookRequest
    ) -> datahub_v1_notebook_query_service_pb2.LookupNotebookResponse:
        """Returns a notebook."""
        deps = self.deps
        response = datahub_v1_notebook_query_service_pb2.LookupNotebookResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('LookupNotebook', extra={'fields': {'locale': request.context.locale}})
            await deps.repository.audit(request.context.tenant_id, 'LookupNotebook', {'locale': request.context.locale})
            echoed_0 = request.notebook_id
            response.notebook.notebook_id = echoed_0
            return response

    async def handle_peek_notebook(
        self,
        request: datahub_v1_notebook_query_service_pb2.PeekNotebookRequest
    ) -> datahub_v1_notebook_query_service_pb2.PeekNotebookResponse:
        """Returns a notebook."""
        deps = self.deps
        response = datahub_v1_notebook_query_service_pb2.PeekNotebookResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('PeekNotebook', extra={'fields': {'domain': 'datahub'}})
            await deps.repository.audit(request.context.tenant_id, 'PeekNotebook', {})
            response_0 = metrics_v1_dashboard_validation_service_pb2.ExplainDashboardDecisionResponse()
            outgoing_0 = metrics_v1_dashboard_validation_service_pb2.ExplainDashboardDecisionRequest(
                context=request.context,
                dashboard=metrics_v1_metrics_pb2.Dashboard(
                    audit=common_v1_audit_pb2.AuditInfo(updated_at=request.context.deadline),
                    lines=[metrics_v1_metrics_pb2.DashboardLine(attributes=dict(request.context.baggage))]
                ),
                details=metrics_v1_dashboard_validation_service_pb2.ExplainDashboardDecisionRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(email=request.context.actor.email),
                    locale=request.context.locale
                )
            )
            response_0 = await deps.clients.metrics_dashboard_validation.ExplainDashboardDecision(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.dashboard.due_at
            if returned_0_0.ListFields():
                response.notebook.due_at.MergeFrom(returned_0_0)
            echoed_0 = request.notebook_id
            response.notebook.notebook_id = echoed_0
            return response

    async def handle_resolve_notebooks(
        self,
        request: datahub_v1_notebook_query_service_pb2.ResolveNotebooksRequest
    ) -> datahub_v1_notebook_query_service_pb2.ResolveNotebooksResponse:
        """Returns several notebooks at once."""
        deps = self.deps
        response = datahub_v1_notebook_query_service_pb2.ResolveNotebooksResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ResolveNotebooks', extra={'fields': {'locale': request.context.locale}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ResolveNotebooks',
                {'locale': request.context.locale}
            )
            return response

    async def handle_suggest_notebooks(
        self,
        request: datahub_v1_notebook_query_service_pb2.SuggestNotebooksRequest
    ) -> datahub_v1_notebook_query_service_pb2.SuggestNotebooksResponse:
        """Lists notebooks a page at a time."""
        deps = self.deps
        response = datahub_v1_notebook_query_service_pb2.SuggestNotebooksResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SuggestNotebooks', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(request.context.tenant_id, 'SuggestNotebooks', {'order_by': request.order_by})
            response_0 = search_v1_search_index_validation_service_pb2.ExplainSearchIndexDecisionResponse()
            outgoing_0 = search_v1_search_index_validation_service_pb2.ExplainSearchIndexDecisionRequest(
                context=request.context,
                search_index=search_v1_search_pb2.SearchIndex(
                    address=common_v1_address_pb2.PostalAddress(region=request.filter.region)
                )
            )
            response_0 = await deps.clients.search_search_index_validation.ExplainSearchIndexDecision(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.search_index.address.locality
            returned_0_0_part_0 = response.notebooks.add()
            if returned_0_0:
                returned_0_0_part_0.billing_address.locality = returned_0_0
            return response
