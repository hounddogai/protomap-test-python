"""Answers read-only questions about dataset versions, for screens and reports."""

from __future__ import annotations

from collections.abc import AsyncIterator
import logging

from google.protobuf.json_format import MessageToDict
from google.protobuf.json_format import ParseDict
import grpc

from acme.broadcasts.v1 import broadcast_query_service_pb2 as broadcasts_v1_broadcast_query_service_pb2
from acme.careplans.v1 import care_plan_service_pb2 as careplans_v1_care_plan_service_pb2
from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.customers.v1 import refs_pb2 as customers_v1_refs_pb2
from acme.datasets.v1 import data_schema_calculation_service_pb2 as datasets_v1_data_schema_calculation_service_pb2
from acme.datasets.v1 import (
    dataset_version_calculation_service_pb2 as datasets_v1_dataset_version_calculation_service_pb2,
)
from acme.datasets.v1 import dataset_version_query_service_pb2 as datasets_v1_dataset_version_query_service_pb2
from acme.datasets.v1 import (
    dataset_version_query_service_pb2_grpc as datasets_v1_dataset_version_query_service_pb2_grpc,
)
from acme.datasets.v1 import datasets_pb2 as datasets_v1_datasets_pb2
from acme.featurestore.v1 import (
    feature_value_calculation_service_pb2 as featurestore_v1_feature_value_calculation_service_pb2,
)
from acme.featurestore.v1 import featurestore_pb2 as featurestore_v1_featurestore_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.metrics.v1 import dashboard_history_service_pb2 as metrics_v1_dashboard_history_service_pb2
from acme.metrics.v1 import metric_alert_validation_service_pb2 as metrics_v1_metric_alert_validation_service_pb2
from acme.metrics.v1 import metrics_pb2 as metrics_v1_metrics_pb2
from acme.search.v1 import search_index_validation_service_pb2 as search_v1_search_index_validation_service_pb2
from acme.search.v1 import search_pb2 as search_v1_search_pb2

from acme_data.domains.datasets.adapters import DatasetVersionQueryBrowseDatasetVersions1Adapter
from acme_data.domains.datasets.adapters import DatasetVersionQueryBrowseDatasetVersions1Port
from acme_data.domains.datasets.adapters import DatasetVersionQueryCountDatasetVersions1Adapter
from acme_data.domains.datasets.dependencies import Dependencies
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class DatasetVersionQueryServicer(
    datasets_v1_dataset_version_query_service_pb2_grpc.DatasetVersionQueryServiceServicer
):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    @retry_transient
    async def BrowseDatasetVersions(
        self, request: datasets_v1_dataset_version_query_service_pb2.BrowseDatasetVersionsRequest, context: grpc.aio.ServicerContext,
    ) -> datasets_v1_dataset_version_query_service_pb2.BrowseDatasetVersionsResponse:
        """Lists dataset versions a page at a time."""
        return await self.handle_browse_dataset_versions(request)

    @rpc_errors
    @retry_transient
    async def CountDatasetVersions(
        self, request: datasets_v1_dataset_version_query_service_pb2.CountDatasetVersionsRequest, context: grpc.aio.ServicerContext,
    ) -> datasets_v1_dataset_version_query_service_pb2.CountDatasetVersionsResponse:
        """Counts dataset versions by status."""
        return await self.handle_count_dataset_versions(request)

    @rpc_errors
    @retry_transient
    async def FindDatasetVersions(
        self, request: datasets_v1_dataset_version_query_service_pb2.FindDatasetVersionsRequest, context: grpc.aio.ServicerContext,
    ) -> datasets_v1_dataset_version_query_service_pb2.FindDatasetVersionsResponse:
        """Lists dataset versions a page at a time."""
        return await self.handle_find_dataset_versions(request)

    @rpc_errors
    @retry_transient
    async def LookupDatasetVersion(
        self, request: datasets_v1_dataset_version_query_service_pb2.LookupDatasetVersionRequest, context: grpc.aio.ServicerContext,
    ) -> datasets_v1_dataset_version_query_service_pb2.LookupDatasetVersionResponse:
        """Returns a dataset version."""
        return await self.handle_lookup_dataset_version(request)

    @rpc_errors
    @retry_transient
    async def PeekDatasetVersion(
        self, request: datasets_v1_dataset_version_query_service_pb2.PeekDatasetVersionRequest, context: grpc.aio.ServicerContext,
    ) -> datasets_v1_dataset_version_query_service_pb2.PeekDatasetVersionResponse:
        """Returns a dataset version."""
        return await self.handle_peek_dataset_version(request)

    @rpc_errors
    @retry_transient
    async def ResolveDatasetVersions(
        self, request: datasets_v1_dataset_version_query_service_pb2.ResolveDatasetVersionsRequest, context: grpc.aio.ServicerContext,
    ) -> datasets_v1_dataset_version_query_service_pb2.ResolveDatasetVersionsResponse:
        """Returns several dataset versions at once."""
        return await self.handle_resolve_dataset_versions(request)

    @rpc_errors
    @retry_transient
    async def SuggestDatasetVersions(
        self, request: datasets_v1_dataset_version_query_service_pb2.SuggestDatasetVersionsRequest, context: grpc.aio.ServicerContext,
    ) -> datasets_v1_dataset_version_query_service_pb2.SuggestDatasetVersionsResponse:
        """Lists dataset versions a page at a time."""
        return await self.handle_suggest_dataset_versions(request)

    @rpc_errors
    async def SummarizeDatasetVersions(
        self, request: datasets_v1_dataset_version_query_service_pb2.SummarizeDatasetVersionsRequest, context: grpc.aio.ServicerContext,
    ) -> datasets_v1_dataset_version_query_service_pb2.SummarizeDatasetVersionsResponse:
        """Summarizes a dataset version."""
        return await self.handle_summarize_dataset_versions(request)

    async def handle_browse_dataset_versions(
        self,
        request: datasets_v1_dataset_version_query_service_pb2.BrowseDatasetVersionsRequest
    ) -> datasets_v1_dataset_version_query_service_pb2.BrowseDatasetVersionsResponse:
        """Lists dataset versions a page at a time."""
        deps = self.deps
        response = datasets_v1_dataset_version_query_service_pb2.BrowseDatasetVersionsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('BrowseDatasetVersions', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'BrowseDatasetVersions',
                {'order_by': request.order_by}
            )
            response_0 = metrics_v1_metric_alert_validation_service_pb2.PreviewMetricAlertResponse()
            response_1 = datasets_v1_data_schema_calculation_service_pb2.CalculateDataSchemaResponse()
            outgoing_0 = metrics_v1_metric_alert_validation_service_pb2.PreviewMetricAlertRequest(
                context=request.context,
                details=metrics_v1_metric_alert_validation_service_pb2.PreviewMetricAlertRequest.Details(
                    locale=request.context.locale
                ),
                metric_alert=metrics_v1_metrics_pb2.MetricAlert(
                    owner=identity_v1_refs_pb2.UserRef(
                        email=request.context.actor.email,
                        user_id=request.context.actor.user_id
                    )
                )
            )
            response_0 = await deps.clients.metrics_metric_alert_validation.PreviewMetricAlert(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = datasets_v1_data_schema_calculation_service_pb2.CalculateDataSchemaRequest(
                context=request.context,
                data_schema=datasets_v1_datasets_pb2.DataSchema(
                    children=[
                        datasets_v1_datasets_pb2.DataSchema(
                            children=[
                                datasets_v1_datasets_pb2.DataSchema(
                                    audit=common_v1_audit_pb2.AuditInfo(etag=response_0.metric_alert.audit.etag),
                                    children=[datasets_v1_datasets_pb2.DataSchema(name=response_0.metric_alert.name)],
                                    manager=identity_v1_refs_pb2.UserRef(
                                        display_name=response_0.metric_alert.owner.display_name,
                                        user_id=response_0.metric_alert.owner.user_id
                                    )
                                )
                            ]
                        )
                    ]
                )
            )
            port_1: DatasetVersionQueryBrowseDatasetVersions1Port = DatasetVersionQueryBrowseDatasetVersions1Adapter(
                deps.clients.datasets_data_schema_calculation,
                deps.settings.timeout
            )
            response_1 = await port_1.execute(outgoing_1)
            returned_0_0 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_0)
            returned_0_1 = response_0.result.status
            if returned_0_1:
                response.result.status = returned_0_1
            returned_1_0 = response_1.data_schema.attributes
            returned_1_0_part_0 = response.dataset_versions.add()
            returned_1_0_part_0.attributes.update(returned_1_0)
            returned_1_1 = response_1.result.reference_ids
            response.result.reference_ids.extend(returned_1_1)
            return response

    async def handle_count_dataset_versions(
        self,
        request: datasets_v1_dataset_version_query_service_pb2.CountDatasetVersionsRequest
    ) -> datasets_v1_dataset_version_query_service_pb2.CountDatasetVersionsResponse:
        """Counts dataset versions by status."""
        deps = self.deps
        response = datasets_v1_dataset_version_query_service_pb2.CountDatasetVersionsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CountDatasetVersions', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'CountDatasetVersions',
                {'order_by': request.order_by}
            )
            response_0 = broadcasts_v1_broadcast_query_service_pb2.CountBroadcastsResponse()
            response_1 = featurestore_v1_feature_value_calculation_service_pb2.RecalculateFeatureValuesResponse()
            outgoing_0 = broadcasts_v1_broadcast_query_service_pb2.CountBroadcastsRequest(
                context=request.context,
                filter=broadcasts_v1_broadcast_query_service_pb2.CountBroadcastsRequest.Filter(
                    created_after=request.filter.created_after
                )
            )
            response_0 = await deps.clients.broadcasts_broadcast_query.CountBroadcasts(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = featurestore_v1_feature_value_calculation_service_pb2.RecalculateFeatureValuesRequest(
                context=request.context,
                details=featurestore_v1_feature_value_calculation_service_pb2.RecalculateFeatureValuesRequest.Details(
                    destination=common_v1_address_pb2.PostalAddress(region=request.filter.region)
                ),
                feature_value=featurestore_v1_featurestore_pb2.FeatureValue(
                    correlation_id=response_0.result.correlation_id,
                    measurements=[
                        featurestore_v1_featurestore_pb2.FeatureValueMeasurement(
                            observed_at=request.filter.created_after
                        )
                    ]
                )
            )
            response_1 = await DatasetVersionQueryCountDatasetVersions1Adapter(
                deps.clients.featurestore_feature_value_calculation,
                deps.settings.timeout
            )(outgoing_1)
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.result.message = returned_0_0
            returned_0_1 = response_0.result.status
            if returned_0_1:
                response.result.status = returned_0_1
            returned_1_0 = response_1.result.correlation_id
            if returned_1_0:
                response.result.correlation_id = returned_1_0
            returned_1_1 = response_1.result.details
            response.result.details.update(returned_1_1)
            return response

    async def handle_find_dataset_versions(
        self,
        request: datasets_v1_dataset_version_query_service_pb2.FindDatasetVersionsRequest
    ) -> datasets_v1_dataset_version_query_service_pb2.FindDatasetVersionsResponse:
        """Lists dataset versions a page at a time."""
        deps = self.deps
        response = datasets_v1_dataset_version_query_service_pb2.FindDatasetVersionsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('FindDatasetVersions', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'FindDatasetVersions',
                {'order_by': request.order_by}
            )
            response_0 = datasets_v1_dataset_version_calculation_service_pb2.CalculateDatasetVersionResponse()
            outgoing_0 = datasets_v1_dataset_version_calculation_service_pb2.CalculateDatasetVersionRequest(
                context=request.context,
                dataset_version=datasets_v1_datasets_pb2.DatasetVersion(
                    measurements=[
                        datasets_v1_datasets_pb2.DatasetVersionMeasurement(observed_at=request.filter.created_after)
                    ],
                    subject=customers_v1_refs_pb2.CustomerRef(email=request.context.actor.email)
                ),
                details=datasets_v1_dataset_version_calculation_service_pb2.CalculateDatasetVersionRequest.Details(
                    destination=common_v1_address_pb2.PostalAddress(region=request.filter.region)
                )
            )
            response_0 = await deps.clients.datasets_dataset_version_calculation.CalculateDatasetVersion(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.correlation_id
            returned_0_0_part_0 = response.dataset_versions.add()
            if returned_0_0:
                returned_0_0_part_0.correlation_id = returned_0_0
            return response

    async def handle_lookup_dataset_version(
        self,
        request: datasets_v1_dataset_version_query_service_pb2.LookupDatasetVersionRequest
    ) -> datasets_v1_dataset_version_query_service_pb2.LookupDatasetVersionResponse:
        """Returns a dataset version."""
        deps = self.deps
        response = datasets_v1_dataset_version_query_service_pb2.LookupDatasetVersionResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('LookupDatasetVersion', extra={'fields': {'locale': request.context.locale}})
            await deps.repository.audit(
                request.context.tenant_id,
                'LookupDatasetVersion',
                {'locale': request.context.locale}
            )
            echoed_0 = request.dataset_version_id
            response.dataset_version.dataset_version_id = echoed_0
            return response

    async def handle_peek_dataset_version(
        self,
        request: datasets_v1_dataset_version_query_service_pb2.PeekDatasetVersionRequest
    ) -> datasets_v1_dataset_version_query_service_pb2.PeekDatasetVersionResponse:
        """Returns a dataset version."""
        deps = self.deps
        response = datasets_v1_dataset_version_query_service_pb2.PeekDatasetVersionResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('PeekDatasetVersion', extra={'fields': {'locale': request.context.locale}})
            await deps.repository.audit(
                request.context.tenant_id,
                'PeekDatasetVersion',
                {'locale': request.context.locale}
            )
            echoed_0 = request.dataset_version_id
            response.dataset_version.dataset_version_id = echoed_0
            return response

    async def handle_resolve_dataset_versions(
        self,
        request: datasets_v1_dataset_version_query_service_pb2.ResolveDatasetVersionsRequest
    ) -> datasets_v1_dataset_version_query_service_pb2.ResolveDatasetVersionsResponse:
        """Returns several dataset versions at once."""
        deps = self.deps
        response = datasets_v1_dataset_version_query_service_pb2.ResolveDatasetVersionsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ResolveDatasetVersions', extra={'fields': {'locale': request.context.locale}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ResolveDatasetVersions',
                {'locale': request.context.locale}
            )
            return response

    async def handle_suggest_dataset_versions(
        self,
        request: datasets_v1_dataset_version_query_service_pb2.SuggestDatasetVersionsRequest
    ) -> datasets_v1_dataset_version_query_service_pb2.SuggestDatasetVersionsResponse:
        """Lists dataset versions a page at a time."""
        deps = self.deps
        response = datasets_v1_dataset_version_query_service_pb2.SuggestDatasetVersionsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SuggestDatasetVersions', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'SuggestDatasetVersions',
                {'order_by': request.order_by}
            )
            response_0 = metrics_v1_dashboard_history_service_pb2.RecordDashboardVersionResponse()
            outgoing_0 = metrics_v1_dashboard_history_service_pb2.RecordDashboardVersionRequest(
                context=request.context,
                dashboard=metrics_v1_metrics_pb2.Dashboard(
                    audit=common_v1_audit_pb2.AuditInfo(updated_at=request.filter.created_after),
                    billing_address=common_v1_address_pb2.PostalAddress(region=request.filter.region)
                ),
                details=metrics_v1_dashboard_history_service_pb2.RecordDashboardVersionRequest.Details(
                    author_email=request.context.actor.email
                )
            )
            response_0 = await deps.clients.metrics_dashboard_history.RecordDashboardVersion(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.result.message = returned_0_0
            returned_0_1 = response_0.outcome.status
            if returned_0_1:
                response.result.status = returned_0_1
            return response

    async def handle_summarize_dataset_versions(
        self,
        request: datasets_v1_dataset_version_query_service_pb2.SummarizeDatasetVersionsRequest
    ) -> datasets_v1_dataset_version_query_service_pb2.SummarizeDatasetVersionsResponse:
        """Summarizes a dataset version."""
        deps = self.deps
        response = datasets_v1_dataset_version_query_service_pb2.SummarizeDatasetVersionsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SummarizeDatasetVersions', extra={'fields': {'dataset_version_id': request.dataset_version_id}})
            await deps.repository.audit(
                request.context.tenant_id,
                'SummarizeDatasetVersions',
                {'dataset_version_id': request.dataset_version_id}
            )
            response_0 = metrics_v1_dashboard_history_service_pb2.RecordDashboardVersionResponse()
            response_1 = careplans_v1_care_plan_service_pb2.CreateCarePlanResponse()
            response_2 = search_v1_search_index_validation_service_pb2.LintSearchIndexesResponse()
            outgoing_0 = metrics_v1_dashboard_history_service_pb2.RecordDashboardVersionRequest(
                annotations=dict(request.annotations),
                context=request.context,
                dashboard=metrics_v1_metrics_pb2.Dashboard(
                    lines=[metrics_v1_metrics_pb2.DashboardLine(attributes=dict(request.details.filters))]
                ),
                details=metrics_v1_dashboard_history_service_pb2.RecordDashboardVersionRequest.Details(
                    author_email=request.context.actor.email
                ),
                reason=request.reason
            )
            method_name_0 = 'RecordDashboardVersion'
            response_0 = await getattr(
                deps.clients.metrics_dashboard_history,
                method_name_0
            )(outgoing_0, timeout=deps.settings.timeout)
            outgoing_1 = careplans_v1_care_plan_service_pb2.CreateCarePlanRequest()
            outgoing_1.context.CopyFrom(request.context)
            if response_0.dashboard.WhichOneof('settlement') == 'card':
                outgoing_1.care_plan.card.holder_name = response_0.dashboard.card.holder_name
            if response_0.dashboard.WhichOneof('settlement') == 'card':
                outgoing_1.care_plan.card.last4 = response_0.dashboard.card.last4
            outgoing_1.care_plan.counterparty.display_name = response_0.dashboard.counterparty.display_name
            response_1 = await deps.clients.careplans_care_plan.CreateCarePlan(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = search_v1_search_index_validation_service_pb2.LintSearchIndexesRequest(
                context=request.context,
                search_index=search_v1_search_pb2.SearchIndex(
                    address=common_v1_address_pb2.PostalAddress(
                        locality=response_0.dashboard.billing_address.locality,
                        region=response_1.care_plan.billing_address.region
                    ),
                    audit=common_v1_audit_pb2.AuditInfo(etag=response_0.dashboard.audit.etag),
                    owner=identity_v1_refs_pb2.UserRef(display_name=response_0.dashboard.counterparty.display_name)
                )
            )
            document_2 = MessageToDict(outgoing_2, preserving_proto_field_name=True)
            outgoing_2 = ParseDict(document_2, search_v1_search_index_validation_service_pb2.LintSearchIndexesRequest())
            response_2 = await deps.clients.search_search_index_validation.LintSearchIndexes(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.outcome.message
            if returned_0_0:
                response.result.message = returned_0_0
            returned_0_1 = response_0.result.status
            if returned_0_1:
                response.result.status = returned_0_1
            returned_1_0 = response_1.result.status
            if returned_1_0:
                response.result.status = returned_1_0
            returned_1_1 = response_1.result.reference_ids
            response.result.reference_ids.extend(returned_1_1)
            returned_2_0 = response_2.result.status
            if returned_2_0:
                response.result.status = returned_2_0
            echoed_0 = request.details.period
            response.period.CopyFrom(echoed_0)
            return response
