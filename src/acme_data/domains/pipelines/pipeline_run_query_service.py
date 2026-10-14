"""Answers read-only questions about pipeline runs, for screens and reports."""

from __future__ import annotations

from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import cast
import logging

from google.protobuf.any_pb2 import Any as AnyMessage
import grpc

from acme.careplans.v1 import care_plan_calculation_service_pb2 as careplans_v1_care_plan_calculation_service_pb2
from acme.careplans.v1 import careplans_pb2 as careplans_v1_careplans_pb2
from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.dispatch.v1 import dispatch_order_query_service_pb2 as dispatch_v1_dispatch_order_query_service_pb2
from acme.documents.v1 import document_query_service_pb2 as documents_v1_document_query_service_pb2
from acme.featurestore.v1 import feature_value_query_service_pb2 as featurestore_v1_feature_value_query_service_pb2
from acme.featurestore.v1 import (
    feature_value_query_service_pb2_grpc as featurestore_v1_feature_value_query_service_pb2_grpc,
)
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.keymanagement.v1 import crypto_key_service_pb2 as keymanagement_v1_crypto_key_service_pb2
from acme.ledger.v1 import ledger_account_service_pb2 as ledger_v1_ledger_account_service_pb2
from acme.metrics.v1 import dashboard_admin_service_pb2 as metrics_v1_dashboard_admin_service_pb2
from acme.metrics.v1 import metrics_pb2 as metrics_v1_metrics_pb2
from acme.pipelines.v1 import pipeline_run_query_service_pb2 as pipelines_v1_pipeline_run_query_service_pb2
from acme.pipelines.v1 import pipeline_run_query_service_pb2_grpc as pipelines_v1_pipeline_run_query_service_pb2_grpc
from acme.pipelines.v1 import pipeline_step_validation_service_pb2 as pipelines_v1_pipeline_step_validation_service_pb2
from acme.pipelines.v1 import pipelines_pb2 as pipelines_v1_pipelines_pb2

from acme_data.domains.pipelines.dependencies import Dependencies
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


@dataclass(slots=True)
class PipelineRunQueryServicer(pipelines_v1_pipeline_run_query_service_pb2_grpc.PipelineRunQueryServiceServicer):
    deps: Dependencies

    @rpc_errors
    @retry_transient
    async def BrowsePipelineRuns(
        self, request: pipelines_v1_pipeline_run_query_service_pb2.BrowsePipelineRunsRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_run_query_service_pb2.BrowsePipelineRunsResponse:
        """Lists pipeline runs a page at a time."""
        return await self.handle_browse_pipeline_runs(request)

    @stream_errors
    async def ExportPipelineRuns(
        self, request: pipelines_v1_pipeline_run_query_service_pb2.ExportPipelineRunsRequest, context: grpc.aio.ServicerContext,
    ) -> AsyncIterator[pipelines_v1_pipeline_run_query_service_pb2.ExportPipelineRunsResponse]:
        """Streams every matching pipeline run."""
        response = await self.handle_export_pipeline_runs(request)
        for item in messages((response,)):
            yield item

    @rpc_errors
    @retry_transient
    async def FindPipelineRuns(
        self, request: pipelines_v1_pipeline_run_query_service_pb2.FindPipelineRunsRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_run_query_service_pb2.FindPipelineRunsResponse:
        """Lists pipeline runs a page at a time."""
        return await self.handle_find_pipeline_runs(request)

    @rpc_errors
    @retry_transient
    async def LookupPipelineRun(
        self, request: pipelines_v1_pipeline_run_query_service_pb2.LookupPipelineRunRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_run_query_service_pb2.LookupPipelineRunResponse:
        """Returns a pipeline run."""
        return await self.handle_lookup_pipeline_run(request)

    @rpc_errors
    @retry_transient
    async def SuggestPipelineRuns(
        self, request: pipelines_v1_pipeline_run_query_service_pb2.SuggestPipelineRunsRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_run_query_service_pb2.SuggestPipelineRunsResponse:
        """Lists pipeline runs a page at a time."""
        return await self.handle_suggest_pipeline_runs(request)

    @rpc_errors
    async def SummarizePipelineRuns(
        self, request: pipelines_v1_pipeline_run_query_service_pb2.SummarizePipelineRunsRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_run_query_service_pb2.SummarizePipelineRunsResponse:
        """Summarizes a pipeline run."""
        return await self.handle_summarize_pipeline_runs(request)

    async def handle_browse_pipeline_runs(
        self,
        request: pipelines_v1_pipeline_run_query_service_pb2.BrowsePipelineRunsRequest
    ) -> pipelines_v1_pipeline_run_query_service_pb2.BrowsePipelineRunsResponse:
        """Lists pipeline runs a page at a time."""
        deps = self.deps
        response = pipelines_v1_pipeline_run_query_service_pb2.BrowsePipelineRunsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('BrowsePipelineRuns', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(request.context.tenant_id, 'BrowsePipelineRuns', {'order_by': request.order_by})
            response_0 = metrics_v1_dashboard_admin_service_pb2.RepairDashboardResponse()
            outgoing_0 = metrics_v1_dashboard_admin_service_pb2.RepairDashboardRequest(
                context=request.context,
                dashboard=metrics_v1_metrics_pb2.Dashboard(
                    audit=common_v1_audit_pb2.AuditInfo(updated_at=request.filter.created_after),
                    billing_address=common_v1_address_pb2.PostalAddress(region=request.filter.region)
                )
            )
            response_0 = await deps.clients.metrics_dashboard_admin.RepairDashboard(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.dashboard.counterparty.display_name
            returned_0_0_part_0 = response.pipeline_runs.add()
            if returned_0_0:
                returned_0_0_part_0.assignee.display_name = returned_0_0
            returned_0_1 = response_0.result.correlation_id
            if returned_0_1:
                response.result.correlation_id = returned_0_1
            return response

    async def handle_export_pipeline_runs(
        self,
        request: pipelines_v1_pipeline_run_query_service_pb2.ExportPipelineRunsRequest
    ) -> pipelines_v1_pipeline_run_query_service_pb2.ExportPipelineRunsResponse:
        """Streams every matching pipeline run."""
        deps = self.deps
        response = pipelines_v1_pipeline_run_query_service_pb2.ExportPipelineRunsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ExportPipelineRuns', extra={'fields': {'destination_uri': request.destination_uri}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ExportPipelineRuns',
                {'destination_uri': request.destination_uri}
            )
            response_0 = keymanagement_v1_crypto_key_service_pb2.SearchCryptoKeysResponse()
            outgoing_0 = keymanagement_v1_crypto_key_service_pb2.SearchCryptoKeysRequest(
                context=request.context,
                filter=keymanagement_v1_crypto_key_service_pb2.SearchCryptoKeysRequest.Filter(
                    created_after=request.filter.created_after,
                    labels=dict(request.filter.labels),
                    query=request.filter.query,
                    region=request.filter.region
                )
            )
            method_name_0 = 'SearchCryptoKeys'
            response_0 = await getattr(
                deps.clients.keymanagement_crypto_key,
                method_name_0
            )(outgoing_0, timeout=deps.settings.timeout)
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.result.message = returned_0_0
            returned_0_1 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_1)
            return response

    async def handle_find_pipeline_runs(
        self,
        request: pipelines_v1_pipeline_run_query_service_pb2.FindPipelineRunsRequest
    ) -> pipelines_v1_pipeline_run_query_service_pb2.FindPipelineRunsResponse:
        """Lists pipeline runs a page at a time."""
        deps = self.deps
        response = pipelines_v1_pipeline_run_query_service_pb2.FindPipelineRunsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('FindPipelineRuns', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(request.context.tenant_id, 'FindPipelineRuns', {'order_by': request.order_by})
            response_0 = ledger_v1_ledger_account_service_pb2.SearchLedgerAccountsResponse()
            outgoing_0 = ledger_v1_ledger_account_service_pb2.SearchLedgerAccountsRequest(
                context=request.context,
                filter=ledger_v1_ledger_account_service_pb2.SearchLedgerAccountsRequest.Filter(
                    owner_id=request.filter.owner_id
                )
            )
            response_0 = await deps.clients.ledger_ledger_account.SearchLedgerAccounts(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.page_info.next_page_token
            if returned_0_0:
                response.page_info.next_page_token = returned_0_0
            return response

    async def handle_lookup_pipeline_run(
        self,
        request: pipelines_v1_pipeline_run_query_service_pb2.LookupPipelineRunRequest
    ) -> pipelines_v1_pipeline_run_query_service_pb2.LookupPipelineRunResponse:
        """Returns a pipeline run."""
        deps = self.deps
        response = pipelines_v1_pipeline_run_query_service_pb2.LookupPipelineRunResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('LookupPipelineRun', extra={'fields': {'domain': 'pipelines'}})
            await deps.repository.audit(request.context.tenant_id, 'LookupPipelineRun', {})
            response_0 = dispatch_v1_dispatch_order_query_service_pb2.ExportDispatchOrdersResponse()
            outgoing_0 = dispatch_v1_dispatch_order_query_service_pb2.ExportDispatchOrdersRequest(
                context=request.context,
                filter=dispatch_v1_dispatch_order_query_service_pb2.ExportDispatchOrdersRequest.Filter(
                    owner_id=request.pipeline_run_id
                )
            )
            async for chunk_0 in deps.clients.dispatch_dispatch_order_query.ExportDispatchOrders(
                outgoing_0,
                timeout=deps.settings.timeout
            ):
                response_0 = chunk_0
            echoed_0 = request.pipeline_run_id
            response.pipeline_run.pipeline_run_id = echoed_0
            return response

    async def handle_suggest_pipeline_runs(
        self,
        request: pipelines_v1_pipeline_run_query_service_pb2.SuggestPipelineRunsRequest
    ) -> pipelines_v1_pipeline_run_query_service_pb2.SuggestPipelineRunsResponse:
        """Lists pipeline runs a page at a time."""
        deps = self.deps
        response = pipelines_v1_pipeline_run_query_service_pb2.SuggestPipelineRunsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SuggestPipelineRuns', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'SuggestPipelineRuns',
                {'order_by': request.order_by}
            )
            response_0 = pipelines_v1_pipeline_step_validation_service_pb2.PreviewPipelineStepResponse()
            response_1 = documents_v1_document_query_service_pb2.CountDocumentsResponse()
            outgoing_0 = pipelines_v1_pipeline_step_validation_service_pb2.PreviewPipelineStepRequest(
                context=request.context,
                details=pipelines_v1_pipeline_step_validation_service_pb2.PreviewPipelineStepRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(email=request.context.actor.email),
                    locale=request.context.locale
                ),
                pipeline_step=pipelines_v1_pipelines_pb2.PipelineStep(
                    audit=common_v1_audit_pb2.AuditInfo(created_at=request.filter.created_after),
                    owner=identity_v1_refs_pb2.UserRef(user_id=request.context.actor.user_id)
                )
            )
            response_0 = await deps.clients.pipelines_pipeline_step_validation.PreviewPipelineStep(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = documents_v1_document_query_service_pb2.CountDocumentsRequest()
            outgoing_1.context.CopyFrom(request.context)
            outgoing_1.filter.labels.update(dict(request.filter.labels))
            outgoing_1.filter.query = request.filter.query
            outgoing_1.page.page_size = request.page.page_size
            outgoing_1.page.page_token = request.page.page_token
            merged_1 = documents_v1_document_query_service_pb2.CountDocumentsRequest()
            merged_1.MergeFrom(outgoing_1)
            outgoing_1.CopyFrom(merged_1)
            response_1 = await deps.clients.documents_document_query.CountDocuments(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_0)
            returned_1_0 = response_1.result.status
            if returned_1_0:
                response.result.status = returned_1_0
            return response

    async def handle_summarize_pipeline_runs(
        self,
        request: pipelines_v1_pipeline_run_query_service_pb2.SummarizePipelineRunsRequest
    ) -> pipelines_v1_pipeline_run_query_service_pb2.SummarizePipelineRunsResponse:
        """Summarizes a pipeline run."""
        deps = self.deps
        response = pipelines_v1_pipeline_run_query_service_pb2.SummarizePipelineRunsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SummarizePipelineRuns', extra={'fields': {'pipeline_run_id': request.pipeline_run_id}})
            await deps.repository.audit(
                request.context.tenant_id,
                'SummarizePipelineRuns',
                {'pipeline_run_id': request.pipeline_run_id}
            )
            response_0 = careplans_v1_care_plan_calculation_service_pb2.RecalculateCarePlansResponse()
            response_1 = featurestore_v1_feature_value_query_service_pb2.BrowseFeatureValuesResponse()
            outgoing_0 = careplans_v1_care_plan_calculation_service_pb2.RecalculateCarePlansRequest(
                annotations=dict(request.annotations),
                care_plan=careplans_v1_careplans_pb2.CarePlan(
                    audit=common_v1_audit_pb2.AuditInfo(created_at=request.context.deadline),
                    metadata=dict(request.details.filters)
                ),
                context=request.context,
                reason=request.reason
            )
            envelope_0 = AnyMessage()
            envelope_0.Pack(outgoing_0)
            outgoing_0 = careplans_v1_care_plan_calculation_service_pb2.RecalculateCarePlansRequest()
            if not envelope_0.Unpack(outgoing_0):
                raise ValueError("partner envelope contains the wrong request type")
            response_0 = await deps.clients.careplans_care_plan_calculation.RecalculateCarePlans(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = featurestore_v1_feature_value_query_service_pb2.BrowseFeatureValuesRequest(
                context=request.context,
                filter=featurestore_v1_feature_value_query_service_pb2.BrowseFeatureValuesRequest.Filter(
                    created_after=response_0.care_plan.audit.created_at,
                    labels=dict(request.details.filters),
                    region=response_0.care_plan.billing_address.region
                )
            )
            registered_1 = cast(
                featurestore_v1_feature_value_query_service_pb2_grpc.FeatureValueQueryServiceStub,
                deps.clients.registry['acme.featurestore.v1.FeatureValueQueryService']
            )
            response_1 = await registered_1.BrowseFeatureValues(outgoing_1, timeout=deps.settings.timeout)
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.result.message = returned_0_0
            returned_1_0 = response_1.result.reference_ids
            response.result.reference_ids.extend(returned_1_0)
            returned_1_1 = response_1.result.details
            response.result.details.update(returned_1_1)
            echoed_0 = request.details.period
            response.period.CopyFrom(echoed_0)
            return response
