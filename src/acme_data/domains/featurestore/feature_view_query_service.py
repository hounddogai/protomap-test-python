"""Answers read-only questions about feature views, for screens and reports."""

from __future__ import annotations

from collections.abc import AsyncIterator
import logging

from google.protobuf.json_format import MessageToJson
from google.protobuf.json_format import Parse
import grpc

from acme.audit.v1 import audit_event_service_pb2 as audit_v1_audit_event_service_pb2
from acme.audit.v1 import audit_event_validation_service_pb2 as audit_v1_audit_event_validation_service_pb2
from acme.audit.v1 import audit_pb2 as audit_v1_audit_pb2
from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.featurestore.v1 import entity_calculation_service_pb2 as featurestore_v1_entity_calculation_service_pb2
from acme.featurestore.v1 import (
    feature_value_calculation_service_pb2 as featurestore_v1_feature_value_calculation_service_pb2,
)
from acme.featurestore.v1 import (
    feature_value_validation_service_pb2 as featurestore_v1_feature_value_validation_service_pb2,
)
from acme.featurestore.v1 import feature_view_query_service_pb2 as featurestore_v1_feature_view_query_service_pb2
from acme.featurestore.v1 import (
    feature_view_query_service_pb2_grpc as featurestore_v1_feature_view_query_service_pb2_grpc,
)
from acme.featurestore.v1 import featurestore_pb2 as featurestore_v1_featurestore_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.ledger.v1 import ledger_account_query_service_pb2 as ledger_v1_ledger_account_query_service_pb2
from acme.metrics.v1 import metric_series_notification_service_pb2 as metrics_v1_metric_series_notification_service_pb2

from acme_data.domains.featurestore.adapters import FeatureViewQueryBrowseFeatureViews1Adapter
from acme_data.domains.featurestore.dependencies import Dependencies
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class FeatureViewQueryServicer(featurestore_v1_feature_view_query_service_pb2_grpc.FeatureViewQueryServiceServicer):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    @retry_transient
    async def BrowseFeatureViews(
        self, request: featurestore_v1_feature_view_query_service_pb2.BrowseFeatureViewsRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_feature_view_query_service_pb2.BrowseFeatureViewsResponse:
        """Lists feature views a page at a time."""
        return await self.handle_browse_feature_views(request)

    @rpc_errors
    @retry_transient
    async def CountFeatureViews(
        self, request: featurestore_v1_feature_view_query_service_pb2.CountFeatureViewsRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_feature_view_query_service_pb2.CountFeatureViewsResponse:
        """Counts feature views by status."""
        return await self.handle_count_feature_views(request)

    @rpc_errors
    @retry_transient
    async def LookupFeatureView(
        self, request: featurestore_v1_feature_view_query_service_pb2.LookupFeatureViewRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_feature_view_query_service_pb2.LookupFeatureViewResponse:
        """Returns a feature view."""
        return await self.handle_lookup_feature_view(request)

    @rpc_errors
    @retry_transient
    async def PeekFeatureView(
        self, request: featurestore_v1_feature_view_query_service_pb2.PeekFeatureViewRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_feature_view_query_service_pb2.PeekFeatureViewResponse:
        """Returns a feature view."""
        return await self.handle_peek_feature_view(request)

    @rpc_errors
    @retry_transient
    async def ResolveFeatureViews(
        self, request: featurestore_v1_feature_view_query_service_pb2.ResolveFeatureViewsRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_feature_view_query_service_pb2.ResolveFeatureViewsResponse:
        """Returns several feature views at once."""
        return await self.handle_resolve_feature_views(request)

    @rpc_errors
    @retry_transient
    async def SuggestFeatureViews(
        self, request: featurestore_v1_feature_view_query_service_pb2.SuggestFeatureViewsRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_feature_view_query_service_pb2.SuggestFeatureViewsResponse:
        """Lists feature views a page at a time."""
        return await self.handle_suggest_feature_views(request)

    @rpc_errors
    async def SummarizeFeatureViews(
        self, request: featurestore_v1_feature_view_query_service_pb2.SummarizeFeatureViewsRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_feature_view_query_service_pb2.SummarizeFeatureViewsResponse:
        """Summarizes a feature view."""
        return await self.handle_summarize_feature_views(request)

    async def handle_browse_feature_views(
        self,
        request: featurestore_v1_feature_view_query_service_pb2.BrowseFeatureViewsRequest
    ) -> featurestore_v1_feature_view_query_service_pb2.BrowseFeatureViewsResponse:
        """Lists feature views a page at a time."""
        deps = self.deps
        response = featurestore_v1_feature_view_query_service_pb2.BrowseFeatureViewsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('BrowseFeatureViews', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(request.context.tenant_id, 'BrowseFeatureViews', {'order_by': request.order_by})
            response_0 = featurestore_v1_feature_value_validation_service_pb2.NormalizeFeatureValueResponse()
            response_1 = featurestore_v1_entity_calculation_service_pb2.ExplainEntityCalculationResponse()
            outgoing_0 = featurestore_v1_feature_value_validation_service_pb2.NormalizeFeatureValueRequest(
                context=request.context,
                details=featurestore_v1_feature_value_validation_service_pb2.NormalizeFeatureValueRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(email=request.context.actor.email)
                )
            )
            response_0 = await deps.clients.featurestore_feature_value_validation.NormalizeFeatureValue(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = featurestore_v1_entity_calculation_service_pb2.ExplainEntityCalculationRequest(
                context=request.context,
                entity=featurestore_v1_featurestore_pb2.Entity(
                    attributes=dict(response_0.feature_value.attributes),
                    relationship_manager=identity_v1_refs_pb2.UserRef(
                        display_name=response_0.feature_value.subject.display_name
                    )
                )
            )
            response_1 = await FeatureViewQueryBrowseFeatureViews1Adapter(
                deps.clients.featurestore_entity_calculation,
                deps.settings.timeout
            )(outgoing_1)
            returned_0_0 = response_0.result.details
            response.result.details.update(returned_0_0)
            returned_1_0 = response_1.entity.audit.updated_by
            returned_1_0_part_0 = response.feature_views.add()
            if returned_1_0:
                returned_1_0_part_0.audit.updated_by = returned_1_0
            return response

    async def handle_count_feature_views(
        self,
        request: featurestore_v1_feature_view_query_service_pb2.CountFeatureViewsRequest
    ) -> featurestore_v1_feature_view_query_service_pb2.CountFeatureViewsResponse:
        """Counts feature views by status."""
        deps = self.deps
        response = featurestore_v1_feature_view_query_service_pb2.CountFeatureViewsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CountFeatureViews', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(request.context.tenant_id, 'CountFeatureViews', {'order_by': request.order_by})
            response_0 = metrics_v1_metric_series_notification_service_pb2.StreamMetricSeriesNoticesResponse()
            response_1 = featurestore_v1_feature_value_calculation_service_pb2.EstimateFeatureValueResponse()
            outgoing_0 = metrics_v1_metric_series_notification_service_pb2.StreamMetricSeriesNoticesRequest(
                context=request.context,
                filter=metrics_v1_metric_series_notification_service_pb2.StreamMetricSeriesNoticesRequest.Filter(
                    created_after=request.filter.created_after,
                    labels=dict(request.filter.labels),
                    owner_id=request.filter.owner_id,
                    region=request.filter.region
                )
            )
            async for chunk_0 in deps.clients.metrics_metric_series_notification.StreamMetricSeriesNotices(
                outgoing_0,
                timeout=deps.settings.timeout
            ):
                response_0 = chunk_0
            outgoing_1 = featurestore_v1_feature_value_calculation_service_pb2.EstimateFeatureValueRequest(
                context=request.context,
                details=featurestore_v1_feature_value_calculation_service_pb2.EstimateFeatureValueRequest.Details(
                    destination=common_v1_address_pb2.PostalAddress(region=request.filter.region)
                ),
                feature_value=featurestore_v1_featurestore_pb2.FeatureValue(
                    measurements=[
                        featurestore_v1_featurestore_pb2.FeatureValueMeasurement(
                            observed_at=request.filter.created_after
                        )
                    ]
                )
            )
            response_1 = await deps.clients.featurestore_feature_value_calculation.EstimateFeatureValue(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_1_0 = response_1.result.reference_ids
            response.result.reference_ids.extend(returned_1_0)
            returned_1_1 = response_1.result.message
            if returned_1_1:
                response.result.message = returned_1_1
            return response

    async def handle_lookup_feature_view(
        self,
        request: featurestore_v1_feature_view_query_service_pb2.LookupFeatureViewRequest
    ) -> featurestore_v1_feature_view_query_service_pb2.LookupFeatureViewResponse:
        """Returns a feature view."""
        deps = self.deps
        response = featurestore_v1_feature_view_query_service_pb2.LookupFeatureViewResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('LookupFeatureView', extra={'fields': {'locale': request.context.locale}})
            await deps.repository.audit(
                request.context.tenant_id,
                'LookupFeatureView',
                {'locale': request.context.locale}
            )
            echoed_0 = request.feature_view_id
            response.feature_view.feature_view_id = echoed_0
            return response

    async def handle_peek_feature_view(
        self,
        request: featurestore_v1_feature_view_query_service_pb2.PeekFeatureViewRequest
    ) -> featurestore_v1_feature_view_query_service_pb2.PeekFeatureViewResponse:
        """Returns a feature view."""
        deps = self.deps
        response = featurestore_v1_feature_view_query_service_pb2.PeekFeatureViewResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('PeekFeatureView', extra={'fields': {'domain': 'featurestore'}})
            await deps.repository.audit(request.context.tenant_id, 'PeekFeatureView', {})
            response_0 = ledger_v1_ledger_account_query_service_pb2.SummarizeLedgerAccountsResponse()
            outgoing_0 = ledger_v1_ledger_account_query_service_pb2.SummarizeLedgerAccountsRequest(
                annotations=dict(request.context.baggage),
                context=request.context
            )
            response_0 = await deps.clients.ledger_ledger_account_query.SummarizeLedgerAccounts(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.result.message = returned_0_0
            returned_0_1 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_1)
            echoed_0 = request.feature_view_id
            response.feature_view.feature_view_id = echoed_0
            return response

    async def handle_resolve_feature_views(
        self,
        request: featurestore_v1_feature_view_query_service_pb2.ResolveFeatureViewsRequest
    ) -> featurestore_v1_feature_view_query_service_pb2.ResolveFeatureViewsResponse:
        """Returns several feature views at once."""
        deps = self.deps
        response = featurestore_v1_feature_view_query_service_pb2.ResolveFeatureViewsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ResolveFeatureViews', extra={'fields': {'domain': 'featurestore'}})
            await deps.repository.audit(request.context.tenant_id, 'ResolveFeatureViews', {})
            response_0 = audit_v1_audit_event_validation_service_pb2.CheckAuditEventEligibilityResponse()
            outgoing_0 = audit_v1_audit_event_validation_service_pb2.CheckAuditEventEligibilityRequest(
                audit_event=audit_v1_audit_pb2.AuditEvent(
                    occurred_at=request.context.deadline,
                    source=request.context.trace_id
                ),
                context=request.context,
                details=audit_v1_audit_event_validation_service_pb2.CheckAuditEventEligibilityRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(email=request.context.actor.email),
                    locale=request.context.locale
                )
            )
            response_0 = await deps.clients.audit_audit_event_validation.CheckAuditEventEligibility(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.audit_event.correlation_id
            if returned_0_0:
                response.result.correlation_id = returned_0_0
            returned_0_1 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_1)
            return response

    async def handle_suggest_feature_views(
        self,
        request: featurestore_v1_feature_view_query_service_pb2.SuggestFeatureViewsRequest
    ) -> featurestore_v1_feature_view_query_service_pb2.SuggestFeatureViewsResponse:
        """Lists feature views a page at a time."""
        deps = self.deps
        response = featurestore_v1_feature_view_query_service_pb2.SuggestFeatureViewsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SuggestFeatureViews', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'SuggestFeatureViews',
                {'order_by': request.order_by}
            )
            response_0 = featurestore_v1_feature_value_calculation_service_pb2.SimulateFeatureValueResponse()
            outgoing_0 = featurestore_v1_feature_value_calculation_service_pb2.SimulateFeatureValueRequest(
                context=request.context,
                details=featurestore_v1_feature_value_calculation_service_pb2.SimulateFeatureValueRequest.Details(
                    destination=common_v1_address_pb2.PostalAddress(region=request.filter.region)
                ),
                feature_value=featurestore_v1_featurestore_pb2.FeatureValue(occurred_at=request.filter.created_after)
            )
            response_0 = await deps.clients.featurestore_feature_value_calculation.SimulateFeatureValue(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.feature_value.subject.code
            returned_0_0_part_0 = response.feature_views.add()
            if returned_0_0:
                returned_0_0_part_0.code = returned_0_0
            returned_0_1 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_1)
            return response

    async def handle_summarize_feature_views(
        self,
        request: featurestore_v1_feature_view_query_service_pb2.SummarizeFeatureViewsRequest
    ) -> featurestore_v1_feature_view_query_service_pb2.SummarizeFeatureViewsResponse:
        """Summarizes a feature view."""
        deps = self.deps
        response = featurestore_v1_feature_view_query_service_pb2.SummarizeFeatureViewsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SummarizeFeatureViews', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'SummarizeFeatureViews', {'reason': request.reason})
            response_0 = audit_v1_audit_event_service_pb2.CreateAuditEventResponse()
            response_1 = featurestore_v1_feature_value_validation_service_pb2.LintFeatureValuesResponse()
            outgoing_0 = audit_v1_audit_event_service_pb2.CreateAuditEventRequest(
                audit_event=audit_v1_audit_pb2.AuditEvent(
                    attributes=dict(request.details.filters),
                    correlation_id=request.feature_view_id,
                    source=request.context.tenant_id
                ),
                context=request.context
            )
            document_0 = MessageToJson(outgoing_0, preserving_proto_field_name=True)
            outgoing_0 = Parse(document_0, audit_v1_audit_event_service_pb2.CreateAuditEventRequest())
            response_0 = await deps.clients.audit_audit_event.CreateAuditEvent(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = featurestore_v1_feature_value_validation_service_pb2.LintFeatureValuesRequest()
            outgoing_1.context.CopyFrom(request.context)
            outgoing_1.feature_value.sequence = response_0.audit_event.sequence
            merged_1 = featurestore_v1_feature_value_validation_service_pb2.LintFeatureValuesRequest()
            merged_1.MergeFrom(outgoing_1)
            outgoing_1.CopyFrom(merged_1)
            response_1 = await deps.clients.featurestore_feature_value_validation.LintFeatureValues(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.correlation_id
            if returned_0_0:
                response.result.correlation_id = returned_0_0
            returned_0_1 = response_0.result.message
            if returned_0_1:
                response.result.message = returned_0_1
            returned_1_0 = response_1.feature_value.correlation_id
            if returned_1_0:
                response.result.correlation_id = returned_1_0
            returned_1_1 = response_1.outcome.status
            if returned_1_1:
                response.result.status = returned_1_1
            echoed_0 = request.details.period
            response.period.CopyFrom(echoed_0)
            return response
