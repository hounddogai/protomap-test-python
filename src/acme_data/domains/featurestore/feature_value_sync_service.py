"""Keeps feature values in step with the systems of record in other regions."""

from __future__ import annotations

from collections.abc import AsyncIterator
from collections.abc import Awaitable
from collections.abc import Callable
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

from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.common.v1 import paging_pb2 as common_v1_paging_pb2
from acme.customers.v1 import customer_calculation_service_pb2 as customers_v1_customer_calculation_service_pb2
from acme.customers.v1 import refs_pb2 as customers_v1_refs_pb2
from acme.datasets.v1 import data_schema_validation_service_pb2 as datasets_v1_data_schema_validation_service_pb2
from acme.datasets.v1 import dataset_query_service_pb2 as datasets_v1_dataset_query_service_pb2
from acme.datasets.v1 import (
    dataset_version_calculation_service_pb2 as datasets_v1_dataset_version_calculation_service_pb2,
)
from acme.datasets.v1 import dataset_version_query_service_pb2 as datasets_v1_dataset_version_query_service_pb2
from acme.datasets.v1 import datasets_pb2 as datasets_v1_datasets_pb2
from acme.documents.v1 import document_service_pb2 as documents_v1_document_service_pb2
from acme.experiments.v1 import experiment_query_service_pb2 as experiments_v1_experiment_query_service_pb2
from acme.featurestore.v1 import entity_calculation_service_pb2 as featurestore_v1_entity_calculation_service_pb2
from acme.featurestore.v1 import entity_import_service_pb2 as featurestore_v1_entity_import_service_pb2
from acme.featurestore.v1 import feature_value_import_service_pb2 as featurestore_v1_feature_value_import_service_pb2
from acme.featurestore.v1 import feature_value_sync_service_pb2 as featurestore_v1_feature_value_sync_service_pb2
from acme.featurestore.v1 import (
    feature_value_sync_service_pb2_grpc as featurestore_v1_feature_value_sync_service_pb2_grpc,
)
from acme.featurestore.v1 import (
    feature_value_validation_service_pb2 as featurestore_v1_feature_value_validation_service_pb2,
)
from acme.featurestore.v1 import feature_view_sync_service_pb2 as featurestore_v1_feature_view_sync_service_pb2
from acme.featurestore.v1 import featurestore_pb2 as featurestore_v1_featurestore_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.lineage.v1 import impact_sync_service_pb2 as lineage_v1_impact_sync_service_pb2
from acme.lineage.v1 import lineage_pb2 as lineage_v1_lineage_pb2
from acme.merchandising.v1 import collection_query_service_pb2 as merchandising_v1_collection_query_service_pb2
from acme.metrics.v1 import metric_series_validation_service_pb2 as metrics_v1_metric_series_validation_service_pb2
from acme.metrics.v1 import (
    metric_series_validation_service_pb2_grpc as metrics_v1_metric_series_validation_service_pb2_grpc,
)

from acme_data.domains.featurestore import hooks
from acme_data.domains.featurestore.adapters import FeatureValueSyncPushFeatureValue2Adapter
from acme_data.domains.featurestore.adapters import FeatureValueSyncPushFeatureValue2Port
from acme_data.domains.featurestore.adapters import FeatureValueSyncReconcileFeatureValues0Adapter
from acme_data.domains.featurestore.dependencies import Dependencies
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_id
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


@dataclass(slots=True)
class FeatureValueSyncServicer(featurestore_v1_feature_value_sync_service_pb2_grpc.FeatureValueSyncServiceServicer):
    deps: Dependencies

    @rpc_errors
    @retry_transient
    async def GetFeatureValueSyncState(
        self, request: featurestore_v1_feature_value_sync_service_pb2.GetFeatureValueSyncStateRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_feature_value_sync_service_pb2.GetFeatureValueSyncStateResponse:
        """Returns a feature value."""
        return await self.handle_get_feature_value_sync_state(request)

    @rpc_errors
    @retry_transient
    async def ListFeatureValueConflicts(
        self, request: featurestore_v1_feature_value_sync_service_pb2.ListFeatureValueConflictsRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_feature_value_sync_service_pb2.ListFeatureValueConflictsResponse:
        """Lists feature values a page at a time."""
        return await self.handle_list_feature_value_conflicts(request)

    @rpc_errors
    async def PullFeatureValues(
        self, request: featurestore_v1_feature_value_sync_service_pb2.PullFeatureValuesRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_feature_value_sync_service_pb2.PullFeatureValuesResponse:
        """Pulls a feature value."""
        return await self.handle_pull_feature_values(request)

    @rpc_errors
    async def PushFeatureValue(
        self, request: featurestore_v1_feature_value_sync_service_pb2.PushFeatureValueRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_feature_value_sync_service_pb2.PushFeatureValueResponse:
        """Pushs a feature value."""
        return await self.handle_push_feature_value(request)

    @rpc_errors
    async def ReconcileFeatureValues(
        self, request: featurestore_v1_feature_value_sync_service_pb2.ReconcileFeatureValuesRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_feature_value_sync_service_pb2.ReconcileFeatureValuesResponse:
        """Reconciles a feature value."""
        return await self.handle_reconcile_feature_values(request)

    @rpc_errors
    async def ResolveFeatureValueConflict(
        self, request: featurestore_v1_feature_value_sync_service_pb2.ResolveFeatureValueConflictRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_feature_value_sync_service_pb2.ResolveFeatureValueConflictResponse:
        """Resolves a feature value."""
        return await self.handle_resolve_feature_value_conflict(request)

    @stream_errors
    async def StreamFeatureValueChanges(
        self, requests: AsyncIterator[
            featurestore_v1_feature_value_sync_service_pb2.StreamFeatureValueChangesRequest
        ], context: grpc.aio.ServicerContext,
    ) -> AsyncIterator[featurestore_v1_feature_value_sync_service_pb2.StreamFeatureValueChangesResponse]:
        """Exchanges changes of feature values with a peer."""
        async for request in requests:
            yield await self.handle_stream_feature_value_changes(request)

    @rpc_errors
    async def SyncFeatureValues(
        self, request: featurestore_v1_feature_value_sync_service_pb2.SyncFeatureValuesRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_feature_value_sync_service_pb2.SyncFeatureValuesResponse:
        """Syncs a feature value."""
        return await self.handle_sync_feature_values(request)

    async def handle_get_feature_value_sync_state(
        self,
        request: featurestore_v1_feature_value_sync_service_pb2.GetFeatureValueSyncStateRequest
    ) -> featurestore_v1_feature_value_sync_service_pb2.GetFeatureValueSyncStateResponse:
        """Returns a feature value."""
        deps = self.deps
        response = featurestore_v1_feature_value_sync_service_pb2.GetFeatureValueSyncStateResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('GetFeatureValueSyncState', extra={'fields': {'locale': request.context.locale}})
            await deps.repository.audit(
                request.context.tenant_id,
                'GetFeatureValueSyncState',
                {'locale': request.context.locale}
            )
            echoed_0 = request.feature_value_id
            response.feature_value.feature_value_id = echoed_0
            return response

    async def handle_list_feature_value_conflicts(
        self,
        request: featurestore_v1_feature_value_sync_service_pb2.ListFeatureValueConflictsRequest
    ) -> featurestore_v1_feature_value_sync_service_pb2.ListFeatureValueConflictsResponse:
        """Lists feature values a page at a time."""
        deps = self.deps
        response = featurestore_v1_feature_value_sync_service_pb2.ListFeatureValueConflictsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ListFeatureValueConflicts', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ListFeatureValueConflicts',
                {'order_by': request.order_by}
            )
            response_0 = datasets_v1_dataset_version_query_service_pb2.BrowseDatasetVersionsResponse()
            outgoing_0 = datasets_v1_dataset_version_query_service_pb2.BrowseDatasetVersionsRequest(
                context=request.context,
                filter=datasets_v1_dataset_version_query_service_pb2.BrowseDatasetVersionsRequest.Filter(
                    owner_id=request.filter.owner_id,
                    region=request.filter.region
                ),
                page=common_v1_paging_pb2.PageRequest(page_size=request.page.page_size)
            )
            response_0 = await deps.clients.datasets_dataset_version_query.BrowseDatasetVersions(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.status
            if returned_0_0:
                response.result.status = returned_0_0
            return response

    async def handle_pull_feature_values(
        self,
        request: featurestore_v1_feature_value_sync_service_pb2.PullFeatureValuesRequest
    ) -> featurestore_v1_feature_value_sync_service_pb2.PullFeatureValuesResponse:
        """Pulls a feature value."""
        deps = self.deps
        response = featurestore_v1_feature_value_sync_service_pb2.PullFeatureValuesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('PullFeatureValues', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'PullFeatureValues', {'reason': request.reason})
            await deps.repository.save_feature_value(request.context.tenant_id, request.feature_value)
            response_0 = featurestore_v1_entity_import_service_pb2.ListEntityImportsResponse()
            outgoing_0 = featurestore_v1_entity_import_service_pb2.ListEntityImportsRequest(
                context=request.context,
                filter=featurestore_v1_entity_import_service_pb2.ListEntityImportsRequest.Filter(
                    created_after=request.feature_value.occurred_at,
                    labels=dict(request.feature_value.attributes),
                    owner_id=request.feature_value_id
                )
            )
            send_0 = partial(deps.clients.featurestore_entity_import.ListEntityImports, timeout=deps.settings.timeout)
            response_0 = await send_0(outgoing_0)
            returned_0_0 = response_0.result.status
            if returned_0_0:
                response.result.status = returned_0_0
            returned_0_1 = response_0.result.message
            if returned_0_1:
                response.result.message = returned_0_1
            echoed_0 = request.feature_value_id
            response.feature_value.feature_value_id = echoed_0
            echoed_1 = request.feature_value.correlation_id
            response.feature_value.correlation_id = echoed_1
            return response

    async def handle_push_feature_value(
        self,
        request: featurestore_v1_feature_value_sync_service_pb2.PushFeatureValueRequest
    ) -> featurestore_v1_feature_value_sync_service_pb2.PushFeatureValueResponse:
        """Pushs a feature value."""
        deps = self.deps
        response = featurestore_v1_feature_value_sync_service_pb2.PushFeatureValueResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('PushFeatureValue', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'PushFeatureValue', {'reason': request.reason})
            await deps.repository.save_feature_value(request.context.tenant_id, request.feature_value)
            response_0 = datasets_v1_dataset_query_service_pb2.PeekDatasetResponse()
            response_1 = featurestore_v1_feature_view_sync_service_pb2.PushFeatureViewResponse()
            response_2 = featurestore_v1_entity_calculation_service_pb2.QuoteEntityResponse()
            response_3 = featurestore_v1_feature_value_import_service_pb2.ListFeatureValueImportsResponse()
            outgoing_0 = datasets_v1_dataset_query_service_pb2.PeekDatasetRequest(
                context=request.context,
                dataset_id=request.feature_value.subject.dataset_id
            )
            response_0 = await hooks.feature_value_sync_push_feature_value0(
                deps.clients.datasets_dataset_query,
                outgoing_0,
                deps.settings.timeout
            )
            outgoing_1 = featurestore_v1_feature_view_sync_service_pb2.PushFeatureViewRequest()
            outgoing_1.context.CopyFrom(request.context)
            outgoing_1.feature_view.audit.updated_by = response_0.dataset.audit.updated_by
            outgoing_1.feature_view.dimensions.weight = response_0.dataset.dimensions.weight
            outgoing_1.context.tenant_id = tenant_id.get()
            response_1 = await deps.clients.featurestore_feature_view_sync.PushFeatureView(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = featurestore_v1_entity_calculation_service_pb2.QuoteEntityRequest(
                context=request.context,
                details=featurestore_v1_entity_calculation_service_pb2.QuoteEntityRequest.Details(
                    destination=common_v1_address_pb2.PostalAddress(
                        postal_code=response_1.feature_view.address.postal_code
                    )
                ),
                entity=featurestore_v1_featurestore_pb2.Entity(
                    audit=common_v1_audit_pb2.AuditInfo(updated_at=response_0.dataset.audit.updated_at)
                )
            )
            port_2: FeatureValueSyncPushFeatureValue2Port = FeatureValueSyncPushFeatureValue2Adapter(
                deps.clients.featurestore_entity_calculation,
                deps.settings.timeout
            )
            response_2 = await port_2.execute(outgoing_2)
            outgoing_3 = featurestore_v1_feature_value_import_service_pb2.ListFeatureValueImportsRequest()
            outgoing_3.context.CopyFrom(request.context)
            if response_0.dataset.WhichOneof('locator') == 'address':
                outgoing_3.filter.region = response_0.dataset.address.region
            outgoing_3.filter.created_after.CopyFrom(response_0.dataset.audit.created_at)
            outgoing_3.filter.owner_id = response_0.dataset.components.get(
                'primary',
                datasets_v1_datasets_pb2.DatasetComponent()
            ).component_id
            response_3 = await deps.clients.featurestore_feature_value_import.ListFeatureValueImports(
                outgoing_3,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.dataset.owner.display_name
            if returned_0_0:
                response.feature_value.subject.display_name = returned_0_0
            returned_1_0 = response_1.result.message
            if returned_1_0:
                response.outcome.message = returned_1_0
            returned_1_1 = response_1.result.message
            if returned_1_1:
                response.result.message = returned_1_1
            returned_2_0 = response_2.result.reference_ids
            response.result.reference_ids.extend(returned_2_0)
            returned_3_0 = response_3.result.reference_ids
            response.result.reference_ids.extend(returned_3_0)
            returned_3_1 = response_3.result.status
            if returned_3_1:
                response.result.status = returned_3_1
            echoed_0 = request.feature_value_id
            response.feature_value.feature_value_id = echoed_0
            echoed_1 = request.feature_value.occurred_at
            response.feature_value.occurred_at.CopyFrom(echoed_1)
            return response

    async def handle_reconcile_feature_values(
        self,
        request: featurestore_v1_feature_value_sync_service_pb2.ReconcileFeatureValuesRequest
    ) -> featurestore_v1_feature_value_sync_service_pb2.ReconcileFeatureValuesResponse:
        """Reconciles a feature value."""
        deps = self.deps
        response = featurestore_v1_feature_value_sync_service_pb2.ReconcileFeatureValuesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ReconcileFeatureValues', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'ReconcileFeatureValues', {'reason': request.reason})
            await deps.repository.save_feature_value(request.context.tenant_id, request.feature_value)
            response_0 = documents_v1_document_service_pb2.ListDocumentsResponse()
            response_1 = merchandising_v1_collection_query_service_pb2.BrowseCollectionsResponse()
            response_2 = experiments_v1_experiment_query_service_pb2.ExportExperimentsResponse()
            response_3 = datasets_v1_dataset_version_calculation_service_pb2.CalculateDatasetVersionResponse()
            outgoing_0 = documents_v1_document_service_pb2.ListDocumentsRequest(
                context=request.context,
                filter=documents_v1_document_service_pb2.ListDocumentsRequest.Filter(
                    created_after=request.feature_value.occurred_at,
                    labels=dict(request.feature_value.attributes),
                    owner_id=request.feature_value_id
                )
            )
            response_0 = await FeatureValueSyncReconcileFeatureValues0Adapter(
                deps.clients.documents_document,
                deps.settings.timeout
            )(outgoing_0)
            outgoing_1 = merchandising_v1_collection_query_service_pb2.BrowseCollectionsRequest(
                context=request.context,
                filter=merchandising_v1_collection_query_service_pb2.BrowseCollectionsRequest.Filter(
                    created_after=request.feature_value.occurred_at,
                    labels=dict(response_0.result.details),
                    owner_id=request.feature_value.feature_value_id
                )
            )
            response_1 = cast(merchandising_v1_collection_query_service_pb2.BrowseCollectionsResponse, await deps.bus.request(
                'acme.featurestore.v1.FeatureValueSyncService/ReconcileFeatureValues/1', outgoing_1, deps.settings.timeout,
            ))
            for item_2 in request.feature_value.measurements:
                outgoing_2 = experiments_v1_experiment_query_service_pb2.ExportExperimentsRequest(
                    context=request.context,
                    filter=experiments_v1_experiment_query_service_pb2.ExportExperimentsRequest.Filter(
                        created_after=item_2.observed_at
                    )
                )
                async for result_2 in deps.clients.experiments_experiment_query.ExportExperiments(
                    outgoing_2,
                    timeout=deps.settings.timeout
                ):
                    response_2 = result_2
            outgoing_3 = datasets_v1_dataset_version_calculation_service_pb2.CalculateDatasetVersionRequest(
                context=request.context,
                dataset_version=datasets_v1_datasets_pb2.DatasetVersion(
                    correlation_id=request.feature_value.correlation_id,
                    kind=request.feature_value.kind,
                    occurred_at=request.feature_value.occurred_at,
                    subject=customers_v1_refs_pb2.CustomerRef(display_name=request.feature_value.subject.display_name)
                )
            )
            method_name_3 = 'CalculateDatasetVersion'
            response_3 = await getattr(
                deps.clients.datasets_dataset_version_calculation,
                method_name_3
            )(outgoing_3, timeout=deps.settings.timeout)
            returned_0_0 = response_0.result.correlation_id
            if returned_0_0:
                response.result.correlation_id = returned_0_0
            returned_1_0 = response_1.result.details
            response.result.details.update(returned_1_0)
            returned_1_1 = response_1.result.message
            if returned_1_1:
                response.outcome.message = returned_1_1
            returned_3_0 = response_3.dataset_version.source
            if returned_3_0:
                response.feature_value.source = returned_3_0
            returned_3_1 = response_3.result.correlation_id
            if returned_3_1:
                response.result.correlation_id = returned_3_1
            echoed_0 = request.feature_value_id
            response.feature_value.feature_value_id = echoed_0
            echoed_1 = request.feature_value.correlation_id
            response.feature_value.correlation_id = echoed_1
            return response

    async def handle_resolve_feature_value_conflict(
        self,
        request: featurestore_v1_feature_value_sync_service_pb2.ResolveFeatureValueConflictRequest
    ) -> featurestore_v1_feature_value_sync_service_pb2.ResolveFeatureValueConflictResponse:
        """Resolves a feature value."""
        deps = self.deps
        response = featurestore_v1_feature_value_sync_service_pb2.ResolveFeatureValueConflictResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ResolveFeatureValueConflict', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ResolveFeatureValueConflict',
                {'reason': request.reason}
            )
            await deps.repository.save_feature_value(request.context.tenant_id, request.feature_value)
            response_0 = datasets_v1_data_schema_validation_service_pb2.ValidateDataSchemaResponse()
            fields_0: dict[str, Any] = {
                'context': request.context,
                'data_schema': {'children': [{'manager': {'display_name': request.feature_value.subject.display_name}}]}
            }
            outgoing_0 = datasets_v1_data_schema_validation_service_pb2.ValidateDataSchemaRequest(**fields_0)
            response_0 = await deps.clients.datasets_data_schema_validation.ValidateDataSchema(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.details
            response.result.details.update(returned_0_0)
            returned_0_1 = response_0.outcome.next_steps
            response.outcome.next_steps.extend(returned_0_1)
            echoed_0 = request.feature_value_id
            response.feature_value.feature_value_id = echoed_0
            echoed_1 = request.feature_value.sequence
            response.feature_value.sequence = echoed_1
            return response

    async def handle_stream_feature_value_changes(
        self,
        request: featurestore_v1_feature_value_sync_service_pb2.StreamFeatureValueChangesRequest
    ) -> featurestore_v1_feature_value_sync_service_pb2.StreamFeatureValueChangesResponse:
        """Exchanges changes of feature values with a peer."""
        deps = self.deps
        response = featurestore_v1_feature_value_sync_service_pb2.StreamFeatureValueChangesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('StreamFeatureValueChanges', extra={'fields': {'cursor': request.cursor}})
            await deps.repository.audit(
                request.context.tenant_id,
                'StreamFeatureValueChanges',
                {'cursor': request.cursor}
            )
            if request.WhichOneof('frame') == 'change':
                await deps.repository.save_feature_value(request.context.tenant_id, request.change)
            response_0 = featurestore_v1_feature_value_validation_service_pb2.LintFeatureValuesResponse()
            response_1 = datasets_v1_dataset_version_calculation_service_pb2.QuoteDatasetVersionResponse()
            requests_0: list[featurestore_v1_feature_value_validation_service_pb2.LintFeatureValuesRequest] = []
            for item_0 in request.change.measurements:
                outgoing_0 = featurestore_v1_feature_value_validation_service_pb2.LintFeatureValuesRequest(
                    context=request.context,
                    feature_value=featurestore_v1_featurestore_pb2.FeatureValue(
                        measurements=[
                            featurestore_v1_featurestore_pb2.FeatureValueMeasurement(
                                metric=item_0.metric,
                                observed_at=item_0.observed_at,
                                value=item_0.value
                            )
                        ]
                    )
                )
                requests_0.append(outgoing_0)
            replies_0 = await asyncio.gather(*(
                deps.clients.featurestore_feature_value_validation.LintFeatureValues(
                    entry,
                    timeout=deps.settings.timeout
                ) for entry in requests_0
            ))
            if replies_0:
                response_0 = replies_0[-1]
            outgoing_1 = datasets_v1_dataset_version_calculation_service_pb2.QuoteDatasetVersionRequest(
                context=request.context,
                dataset_version=datasets_v1_datasets_pb2.DatasetVersion(
                    attributes=dict(response_0.feature_value.attributes),
                    occurred_at=response_0.feature_value.occurred_at,
                    subject=customers_v1_refs_pb2.CustomerRef(display_name=request.change.subject.display_name)
                )
            )
            document_1 = MessageToJson(outgoing_1, preserving_proto_field_name=True)
            outgoing_1 = Parse(
                document_1,
                datasets_v1_dataset_version_calculation_service_pb2.QuoteDatasetVersionRequest()
            )
            response_1 = await deps.clients.datasets_dataset_version_calculation.QuoteDatasetVersion(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_1_0 = response_1.result.details
            response.result.details.update(returned_1_0)
            echoed_0 = request.change.feature_value_id
            response.feature_value.feature_value_id = echoed_0
            echoed_1 = request.ack.status
            response.result.status = echoed_1
            return response

    async def handle_sync_feature_values(
        self,
        request: featurestore_v1_feature_value_sync_service_pb2.SyncFeatureValuesRequest
    ) -> featurestore_v1_feature_value_sync_service_pb2.SyncFeatureValuesResponse:
        """Syncs a feature value."""
        deps = self.deps
        response = featurestore_v1_feature_value_sync_service_pb2.SyncFeatureValuesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SyncFeatureValues', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'SyncFeatureValues', {'reason': request.reason})
            await deps.repository.save_feature_value(request.context.tenant_id, request.feature_value)
            response_0 = customers_v1_customer_calculation_service_pb2.CalculateCustomerResponse()
            response_1 = lineage_v1_impact_sync_service_pb2.ResolveImpactConflictResponse()
            response_2 = metrics_v1_metric_series_validation_service_pb2.ValidateMetricSeriesResponse()
            outgoing_0 = customers_v1_customer_calculation_service_pb2.CalculateCustomerRequest()
            outgoing_0.context.CopyFrom(request.context)
            outgoing_0.customer.relationship_manager.display_name = request.feature_value.subject.display_name
            outgoing_0.annotations.update(dict(request.annotations))
            merged_0 = customers_v1_customer_calculation_service_pb2.CalculateCustomerRequest()
            merged_0.MergeFrom(outgoing_0)
            outgoing_0.CopyFrom(merged_0)
            response_0 = await deps.clients.customers_customer_calculation.CalculateCustomer(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = lineage_v1_impact_sync_service_pb2.ResolveImpactConflictRequest(
                context=request.context,
                impact=lineage_v1_lineage_pb2.Impact(
                    assignee=identity_v1_refs_pb2.UserRef(email=response_0.customer.relationship_manager.email),
                    audit=common_v1_audit_pb2.AuditInfo(created_at=response_0.customer.audit.created_at)
                )
            )
            envelope_1 = AnyMessage()
            envelope_1.Pack(outgoing_1)
            outgoing_1 = lineage_v1_impact_sync_service_pb2.ResolveImpactConflictRequest()
            if not envelope_1.Unpack(outgoing_1):
                raise ValueError("partner envelope contains the wrong request type")
            response_1 = await deps.clients.lineage_impact_sync.ResolveImpactConflict(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = metrics_v1_metric_series_validation_service_pb2.ValidateMetricSeriesRequest(
                context=request.context,
                details=metrics_v1_metric_series_validation_service_pb2.ValidateMetricSeriesRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(email=response_0.customer.contact.email)
                )
            )
            registered_2 = cast(
                metrics_v1_metric_series_validation_service_pb2_grpc.MetricSeriesValidationServiceStub,
                deps.clients.registry['acme.metrics.v1.MetricSeriesValidationService']
            )
            response_2 = await registered_2.ValidateMetricSeries(outgoing_2, timeout=deps.settings.timeout)
            returned_0_0 = response_0.result.correlation_id
            if returned_0_0:
                response.result.correlation_id = returned_0_0
            returned_1_0 = response_1.result.message
            if returned_1_0:
                response.result.message = returned_1_0
            returned_1_1 = response_1.outcome.message
            if returned_1_1:
                response.outcome.message = returned_1_1
            returned_2_0 = response_2.result.status
            if returned_2_0:
                response.result.status = returned_2_0
            echoed_0 = request.feature_value_id
            response.feature_value.feature_value_id = echoed_0
            echoed_1 = request.feature_value.subject
            response.feature_value.subject.CopyFrom(echoed_1)
            return response
