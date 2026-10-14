"""Answers read-only questions about datasets, for screens and reports."""

from __future__ import annotations

from collections.abc import AsyncIterator
import logging

from google.protobuf.any_pb2 import Any as AnyMessage
from google.protobuf.json_format import MessageToJson
from google.protobuf.json_format import Parse
import grpc

from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.customers.v1 import refs_pb2 as customers_v1_refs_pb2
from acme.datasets.v1 import dataset_query_service_pb2 as datasets_v1_dataset_query_service_pb2
from acme.datasets.v1 import dataset_query_service_pb2_grpc as datasets_v1_dataset_query_service_pb2_grpc
from acme.datasets.v1 import (
    dataset_version_calculation_service_pb2 as datasets_v1_dataset_version_calculation_service_pb2,
)
from acme.datasets.v1 import (
    dataset_version_validation_service_pb2 as datasets_v1_dataset_version_validation_service_pb2,
)
from acme.datasets.v1 import datasets_pb2 as datasets_v1_datasets_pb2
from acme.deliveries.v1 import delivery_query_service_pb2 as deliveries_v1_delivery_query_service_pb2
from acme.featurestore.v1 import (
    feature_value_validation_service_pb2 as featurestore_v1_feature_value_validation_service_pb2,
)
from acme.featurestore.v1 import feature_view_query_service_pb2 as featurestore_v1_feature_view_query_service_pb2
from acme.featurestore.v1 import featurestore_pb2 as featurestore_v1_featurestore_pb2
from acme.pipelines.v1 import pipeline_run_calculation_service_pb2 as pipelines_v1_pipeline_run_calculation_service_pb2
from acme.pipelines.v1 import pipelines_pb2 as pipelines_v1_pipelines_pb2
from acme.prescriptions.v1 import prescription_query_service_pb2 as prescriptions_v1_prescription_query_service_pb2

from acme_data.domains.datasets.dependencies import Dependencies
from acme_data.platform.rpc import messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class DatasetQueryServicer(datasets_v1_dataset_query_service_pb2_grpc.DatasetQueryServiceServicer):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    @retry_transient
    async def BrowseDatasets(
        self, request: datasets_v1_dataset_query_service_pb2.BrowseDatasetsRequest, context: grpc.aio.ServicerContext,
    ) -> datasets_v1_dataset_query_service_pb2.BrowseDatasetsResponse:
        """Lists datasets a page at a time."""
        return await self.handle_browse_datasets(request)

    @rpc_errors
    @retry_transient
    async def CountDatasets(
        self, request: datasets_v1_dataset_query_service_pb2.CountDatasetsRequest, context: grpc.aio.ServicerContext,
    ) -> datasets_v1_dataset_query_service_pb2.CountDatasetsResponse:
        """Counts datasets by status."""
        return await self.handle_count_datasets(request)

    @stream_errors
    async def ExportDatasets(
        self, request: datasets_v1_dataset_query_service_pb2.ExportDatasetsRequest, context: grpc.aio.ServicerContext,
    ) -> AsyncIterator[datasets_v1_dataset_query_service_pb2.ExportDatasetsResponse]:
        """Streams every matching dataset."""
        response = await self.handle_export_datasets(request)
        for item in messages((response,)):
            yield item

    @rpc_errors
    @retry_transient
    async def FindDatasets(
        self, request: datasets_v1_dataset_query_service_pb2.FindDatasetsRequest, context: grpc.aio.ServicerContext,
    ) -> datasets_v1_dataset_query_service_pb2.FindDatasetsResponse:
        """Lists datasets a page at a time."""
        return await self.handle_find_datasets(request)

    @rpc_errors
    @retry_transient
    async def LookupDataset(
        self, request: datasets_v1_dataset_query_service_pb2.LookupDatasetRequest, context: grpc.aio.ServicerContext,
    ) -> datasets_v1_dataset_query_service_pb2.LookupDatasetResponse:
        """Returns a dataset."""
        return await self.handle_lookup_dataset(request)

    @rpc_errors
    @retry_transient
    async def PeekDataset(
        self, request: datasets_v1_dataset_query_service_pb2.PeekDatasetRequest, context: grpc.aio.ServicerContext,
    ) -> datasets_v1_dataset_query_service_pb2.PeekDatasetResponse:
        """Returns a dataset."""
        return await self.handle_peek_dataset(request)

    @rpc_errors
    @retry_transient
    async def ResolveDatasets(
        self, request: datasets_v1_dataset_query_service_pb2.ResolveDatasetsRequest, context: grpc.aio.ServicerContext,
    ) -> datasets_v1_dataset_query_service_pb2.ResolveDatasetsResponse:
        """Returns several datasets at once."""
        return await self.handle_resolve_datasets(request)

    @rpc_errors
    @retry_transient
    async def SuggestDatasets(
        self, request: datasets_v1_dataset_query_service_pb2.SuggestDatasetsRequest, context: grpc.aio.ServicerContext,
    ) -> datasets_v1_dataset_query_service_pb2.SuggestDatasetsResponse:
        """Lists datasets a page at a time."""
        return await self.handle_suggest_datasets(request)

    @rpc_errors
    async def SummarizeDatasets(
        self, request: datasets_v1_dataset_query_service_pb2.SummarizeDatasetsRequest, context: grpc.aio.ServicerContext,
    ) -> datasets_v1_dataset_query_service_pb2.SummarizeDatasetsResponse:
        """Summarizes a dataset."""
        return await self.handle_summarize_datasets(request)

    async def handle_browse_datasets(
        self,
        request: datasets_v1_dataset_query_service_pb2.BrowseDatasetsRequest
    ) -> datasets_v1_dataset_query_service_pb2.BrowseDatasetsResponse:
        """Lists datasets a page at a time."""
        deps = self.deps
        response = datasets_v1_dataset_query_service_pb2.BrowseDatasetsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('BrowseDatasets', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(request.context.tenant_id, 'BrowseDatasets', {'order_by': request.order_by})
            response_0 = datasets_v1_dataset_version_validation_service_pb2.PreviewDatasetVersionResponse()
            outgoing_0 = datasets_v1_dataset_version_validation_service_pb2.PreviewDatasetVersionRequest(
                context=request.context,
                dataset_version=datasets_v1_datasets_pb2.DatasetVersion(
                    attributes=dict(request.filter.labels),
                    occurred_at=request.filter.created_after,
                    subject=customers_v1_refs_pb2.CustomerRef(email=request.context.actor.email)
                ),
                details=datasets_v1_dataset_version_validation_service_pb2.PreviewDatasetVersionRequest.Details(
                    locale=request.context.locale
                )
            )
            response_0 = await deps.clients.datasets_dataset_version_validation.PreviewDatasetVersion(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.details
            response.result.details.update(returned_0_0)
            returned_0_1 = response_0.result.status
            if returned_0_1:
                response.result.status = returned_0_1
            return response

    async def handle_count_datasets(
        self,
        request: datasets_v1_dataset_query_service_pb2.CountDatasetsRequest
    ) -> datasets_v1_dataset_query_service_pb2.CountDatasetsResponse:
        """Counts datasets by status."""
        deps = self.deps
        response = datasets_v1_dataset_query_service_pb2.CountDatasetsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CountDatasets', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(request.context.tenant_id, 'CountDatasets', {'order_by': request.order_by})
            response_0 = featurestore_v1_feature_value_validation_service_pb2.LintFeatureValuesResponse()
            outgoing_0 = featurestore_v1_feature_value_validation_service_pb2.LintFeatureValuesRequest(
                context=request.context,
                details=featurestore_v1_feature_value_validation_service_pb2.LintFeatureValuesRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(email=request.context.actor.email),
                    locale=request.context.locale
                ),
                feature_value=featurestore_v1_featurestore_pb2.FeatureValue(
                    measurements=[
                        featurestore_v1_featurestore_pb2.FeatureValueMeasurement(
                            observed_at=request.filter.created_after
                        )
                    ]
                )
            )
            response_0 = await deps.clients.featurestore_feature_value_validation.LintFeatureValues(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.correlation_id
            if returned_0_0:
                response.result.correlation_id = returned_0_0
            return response

    async def handle_export_datasets(
        self,
        request: datasets_v1_dataset_query_service_pb2.ExportDatasetsRequest
    ) -> datasets_v1_dataset_query_service_pb2.ExportDatasetsResponse:
        """Streams every matching dataset."""
        deps = self.deps
        response = datasets_v1_dataset_query_service_pb2.ExportDatasetsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ExportDatasets', extra={'fields': {'destination_uri': request.destination_uri}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ExportDatasets',
                {'destination_uri': request.destination_uri}
            )
            response_0 = datasets_v1_dataset_version_calculation_service_pb2.SimulateDatasetVersionResponse()
            response_1 = datasets_v1_dataset_version_validation_service_pb2.LintDatasetVersionsResponse()
            outgoing_0 = datasets_v1_dataset_version_calculation_service_pb2.SimulateDatasetVersionRequest(
                context=request.context,
                details=datasets_v1_dataset_version_calculation_service_pb2.SimulateDatasetVersionRequest.Details(
                    destination=common_v1_address_pb2.PostalAddress(region=request.filter.region)
                )
            )
            response_0 = await deps.clients.datasets_dataset_version_calculation.SimulateDatasetVersion(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = datasets_v1_dataset_version_validation_service_pb2.LintDatasetVersionsRequest(
                context=request.context,
                dataset_version=datasets_v1_datasets_pb2.DatasetVersion(
                    subject=customers_v1_refs_pb2.CustomerRef(
                        customer_id=response_0.dataset_version.subject.customer_id
                    )
                ),
                details=datasets_v1_dataset_version_validation_service_pb2.LintDatasetVersionsRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(email=response_0.dataset_version.subject.email)
                )
            )
            method_name_1 = 'LintDatasetVersions'
            response_1 = await getattr(
                deps.clients.datasets_dataset_version_validation,
                method_name_1
            )(outgoing_1, timeout=deps.settings.timeout)
            returned_0_0 = response_0.dataset_version.subject.display_name
            if returned_0_0:
                response.dataset.owner.display_name = returned_0_0
            returned_0_1 = response_0.dataset_version.sequence
            if returned_0_1:
                response.sequence = returned_0_1
            returned_1_0 = response_1.dataset_version.correlation_id
            if returned_1_0:
                response.result.correlation_id = returned_1_0
            return response

    async def handle_find_datasets(
        self,
        request: datasets_v1_dataset_query_service_pb2.FindDatasetsRequest
    ) -> datasets_v1_dataset_query_service_pb2.FindDatasetsResponse:
        """Lists datasets a page at a time."""
        deps = self.deps
        response = datasets_v1_dataset_query_service_pb2.FindDatasetsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('FindDatasets', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(request.context.tenant_id, 'FindDatasets', {'order_by': request.order_by})
            response_0 = pipelines_v1_pipeline_run_calculation_service_pb2.RecalculatePipelineRunsResponse()
            outgoing_0 = pipelines_v1_pipeline_run_calculation_service_pb2.RecalculatePipelineRunsRequest(
                context=request.context,
                details=pipelines_v1_pipeline_run_calculation_service_pb2.RecalculatePipelineRunsRequest.Details(
                    destination=common_v1_address_pb2.PostalAddress(region=request.filter.region)
                ),
                pipeline_run=pipelines_v1_pipelines_pb2.PipelineRun(
                    requester=common_v1_contact_pb2.ContactInfo(email=request.context.actor.email)
                )
            )
            response_0 = await deps.clients.pipelines_pipeline_run_calculation.RecalculatePipelineRuns(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.pipeline_run.assignee.display_name
            returned_0_0_part_0 = response.datasets.add()
            if returned_0_0:
                returned_0_0_part_0.owner.display_name = returned_0_0
            returned_0_1 = response_0.result.correlation_id
            if returned_0_1:
                response.result.correlation_id = returned_0_1
            return response

    async def handle_lookup_dataset(
        self,
        request: datasets_v1_dataset_query_service_pb2.LookupDatasetRequest
    ) -> datasets_v1_dataset_query_service_pb2.LookupDatasetResponse:
        """Returns a dataset."""
        deps = self.deps
        response = datasets_v1_dataset_query_service_pb2.LookupDatasetResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('LookupDataset', extra={'fields': {'domain': 'datasets'}})
            await deps.repository.audit(request.context.tenant_id, 'LookupDataset', {})
            response_0 = prescriptions_v1_prescription_query_service_pb2.SuggestPrescriptionsResponse()
            response_1 = featurestore_v1_feature_view_query_service_pb2.CountFeatureViewsResponse()
            outgoing_0 = prescriptions_v1_prescription_query_service_pb2.SuggestPrescriptionsRequest(
                context=request.context,
                filter=prescriptions_v1_prescription_query_service_pb2.SuggestPrescriptionsRequest.Filter(
                    created_after=request.context.deadline,
                    labels=dict(request.context.baggage),
                    owner_id=request.dataset_id
                )
            )
            response_0 = await deps.clients.prescriptions_prescription_query.SuggestPrescriptions(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = featurestore_v1_feature_view_query_service_pb2.CountFeatureViewsRequest(
                context=request.context,
                filter=featurestore_v1_feature_view_query_service_pb2.CountFeatureViewsRequest.Filter(
                    created_after=request.context.deadline,
                    labels=dict(response_0.result.details),
                    owner_id=response_0.result.correlation_id
                )
            )
            document_1 = MessageToJson(outgoing_1, preserving_proto_field_name=True)
            outgoing_1 = Parse(document_1, featurestore_v1_feature_view_query_service_pb2.CountFeatureViewsRequest())
            response_1 = await deps.clients.featurestore_feature_view_query.CountFeatureViews(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.status
            if returned_0_0:
                response.result.status = returned_0_0
            returned_0_1 = response_0.result.details
            response.result.details.update(returned_0_1)
            returned_1_0 = response_1.result.details
            response.result.details.update(returned_1_0)
            returned_1_1 = response_1.result.correlation_id
            if returned_1_1:
                response.result.correlation_id = returned_1_1
            echoed_0 = request.dataset_id
            response.dataset.dataset_id = echoed_0
            return response

    async def handle_peek_dataset(
        self,
        request: datasets_v1_dataset_query_service_pb2.PeekDatasetRequest
    ) -> datasets_v1_dataset_query_service_pb2.PeekDatasetResponse:
        """Returns a dataset."""
        deps = self.deps
        response = datasets_v1_dataset_query_service_pb2.PeekDatasetResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('PeekDataset', extra={'fields': {'locale': request.context.locale}})
            await deps.repository.audit(request.context.tenant_id, 'PeekDataset', {'locale': request.context.locale})
            echoed_0 = request.dataset_id
            response.dataset.dataset_id = echoed_0
            return response

    async def handle_resolve_datasets(
        self,
        request: datasets_v1_dataset_query_service_pb2.ResolveDatasetsRequest
    ) -> datasets_v1_dataset_query_service_pb2.ResolveDatasetsResponse:
        """Returns several datasets at once."""
        deps = self.deps
        response = datasets_v1_dataset_query_service_pb2.ResolveDatasetsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ResolveDatasets', extra={'fields': {'locale': request.context.locale}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ResolveDatasets',
                {'locale': request.context.locale}
            )
            return response

    async def handle_suggest_datasets(
        self,
        request: datasets_v1_dataset_query_service_pb2.SuggestDatasetsRequest
    ) -> datasets_v1_dataset_query_service_pb2.SuggestDatasetsResponse:
        """Lists datasets a page at a time."""
        deps = self.deps
        response = datasets_v1_dataset_query_service_pb2.SuggestDatasetsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SuggestDatasets', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(request.context.tenant_id, 'SuggestDatasets', {'order_by': request.order_by})
            response_0 = datasets_v1_dataset_version_calculation_service_pb2.QuoteDatasetVersionResponse()
            outgoing_0 = datasets_v1_dataset_version_calculation_service_pb2.QuoteDatasetVersionRequest(
                context=request.context,
                dataset_version=datasets_v1_datasets_pb2.DatasetVersion(
                    correlation_id=request.filter.owner_id,
                    occurred_at=request.filter.created_after,
                    subject=customers_v1_refs_pb2.CustomerRef(email=request.context.actor.email)
                ),
                details=datasets_v1_dataset_version_calculation_service_pb2.QuoteDatasetVersionRequest.Details(
                    destination=common_v1_address_pb2.PostalAddress(region=request.filter.region)
                )
            )
            response_0 = await deps.clients.datasets_dataset_version_calculation.QuoteDatasetVersion(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.status
            if returned_0_0:
                response.result.status = returned_0_0
            return response

    async def handle_summarize_datasets(
        self,
        request: datasets_v1_dataset_query_service_pb2.SummarizeDatasetsRequest
    ) -> datasets_v1_dataset_query_service_pb2.SummarizeDatasetsResponse:
        """Summarizes a dataset."""
        deps = self.deps
        response = datasets_v1_dataset_query_service_pb2.SummarizeDatasetsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SummarizeDatasets', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'SummarizeDatasets', {'reason': request.reason})
            response_0 = deliveries_v1_delivery_query_service_pb2.FindDeliveriesResponse()
            outgoing_0 = deliveries_v1_delivery_query_service_pb2.FindDeliveriesRequest(
                context=request.context,
                filter=deliveries_v1_delivery_query_service_pb2.FindDeliveriesRequest.Filter(
                    created_after=request.context.deadline,
                    labels=dict(request.details.filters),
                    owner_id=request.dataset_id
                )
            )
            envelope_0 = AnyMessage()
            envelope_0.Pack(outgoing_0)
            outgoing_0 = deliveries_v1_delivery_query_service_pb2.FindDeliveriesRequest()
            if not envelope_0.Unpack(outgoing_0):
                raise ValueError("partner envelope contains the wrong request type")
            response_0 = await deps.clients.deliveries_delivery_query.FindDeliveries(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.status
            if returned_0_0:
                response.result.status = returned_0_0
            returned_0_1 = response_0.result.correlation_id
            if returned_0_1:
                response.result.correlation_id = returned_0_1
            echoed_0 = request.details.period
            response.period.CopyFrom(echoed_0)
            return response
