"""Takes feature values in bulk from partners and legacy systems."""

from __future__ import annotations

from collections.abc import AsyncIterator
from collections.abc import Awaitable
from collections.abc import Callable
from functools import partial
from typing import cast
import asyncio
import logging

import grpc

from acme.anomalies.v1 import anomalies_pb2 as anomalies_v1_anomalies_pb2
from acme.anomalies.v1 import anomaly_workflow_service_pb2 as anomalies_v1_anomaly_workflow_service_pb2
from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.datasets.v1 import data_schema_validation_service_pb2 as datasets_v1_data_schema_validation_service_pb2
from acme.datasets.v1 import dataset_service_pb2 as datasets_v1_dataset_service_pb2
from acme.datasets.v1 import (
    dataset_version_validation_service_pb2 as datasets_v1_dataset_version_validation_service_pb2,
)
from acme.datasets.v1 import datasets_pb2 as datasets_v1_datasets_pb2
from acme.documents.v1 import document_validation_service_pb2 as documents_v1_document_validation_service_pb2
from acme.documents.v1 import documents_pb2 as documents_v1_documents_pb2
from acme.documents.v1 import refs_pb2 as documents_v1_refs_pb2
from acme.featurestore.v1 import entity_calculation_service_pb2 as featurestore_v1_entity_calculation_service_pb2
from acme.featurestore.v1 import feature_value_import_service_pb2 as featurestore_v1_feature_value_import_service_pb2
from acme.featurestore.v1 import (
    feature_value_import_service_pb2_grpc as featurestore_v1_feature_value_import_service_pb2_grpc,
)
from acme.featurestore.v1 import feature_value_query_service_pb2 as featurestore_v1_feature_value_query_service_pb2
from acme.featurestore.v1 import feature_view_query_service_pb2 as featurestore_v1_feature_view_query_service_pb2
from acme.featurestore.v1 import featurestore_pb2 as featurestore_v1_featurestore_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.lineage.v1 import lineage_node_reporting_service_pb2 as lineage_v1_lineage_node_reporting_service_pb2
from acme.lineage.v1 import lineage_node_sync_service_pb2 as lineage_v1_lineage_node_sync_service_pb2
from acme.metrics.v1 import metric_series_export_service_pb2 as metrics_v1_metric_series_export_service_pb2

from acme_data.domains.featurestore import hooks
from acme_data.domains.featurestore.adapters import FeatureValueImportMapFeatureValueImportColumns3Adapter
from acme_data.domains.featurestore.adapters import FeatureValueImportMapFeatureValueImportColumns3Port
from acme_data.domains.featurestore.adapters import FeatureValueImportRetryFeatureValueImport1Adapter
from acme_data.domains.featurestore.dependencies import Dependencies
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import run_steps
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class FeatureValueImportServicer(
    featurestore_v1_feature_value_import_service_pb2_grpc.FeatureValueImportServiceServicer
):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    async def CancelFeatureValueImport(
        self, request: featurestore_v1_feature_value_import_service_pb2.CancelFeatureValueImportRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_feature_value_import_service_pb2.CancelFeatureValueImportResponse:
        """Cancels a feature value."""
        return await self.handle_cancel_feature_value_import(request)

    @rpc_errors
    @retry_transient
    async def GetFeatureValueImportStatus(
        self, request: featurestore_v1_feature_value_import_service_pb2.GetFeatureValueImportStatusRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_feature_value_import_service_pb2.GetFeatureValueImportStatusResponse:
        """Returns a feature value."""
        return await self.handle_get_feature_value_import_status(request)

    @rpc_errors
    async def ImportFeatureValues(
        self, requests: AsyncIterator[
            featurestore_v1_feature_value_import_service_pb2.ImportFeatureValuesRequest
        ], context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_feature_value_import_service_pb2.ImportFeatureValuesResponse:
        """Takes a stream of feature values and answers once at the end."""
        response = featurestore_v1_feature_value_import_service_pb2.ImportFeatureValuesResponse()
        async for request in requests:
            response.MergeFrom(await self.handle_import_feature_values(request))
        return response

    @rpc_errors
    @retry_transient
    async def ListFeatureValueImports(
        self, request: featurestore_v1_feature_value_import_service_pb2.ListFeatureValueImportsRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_feature_value_import_service_pb2.ListFeatureValueImportsResponse:
        """Lists feature values a page at a time."""
        return await self.handle_list_feature_value_imports(request)

    @rpc_errors
    async def MapFeatureValueImportColumns(
        self, request: featurestore_v1_feature_value_import_service_pb2.MapFeatureValueImportColumnsRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_feature_value_import_service_pb2.MapFeatureValueImportColumnsResponse:
        """Maps a feature value."""
        return await self.handle_map_feature_value_import_columns(request)

    @rpc_errors
    async def RetryFeatureValueImport(
        self, request: featurestore_v1_feature_value_import_service_pb2.RetryFeatureValueImportRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_feature_value_import_service_pb2.RetryFeatureValueImportResponse:
        """Retrys a feature value."""
        return await self.handle_retry_feature_value_import(request)

    @rpc_errors
    async def ValidateFeatureValueImport(
        self, request: featurestore_v1_feature_value_import_service_pb2.ValidateFeatureValueImportRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_feature_value_import_service_pb2.ValidateFeatureValueImportResponse:
        """Validates a feature value."""
        return await self.handle_validate_feature_value_import(request)

    async def handle_cancel_feature_value_import(
        self,
        request: featurestore_v1_feature_value_import_service_pb2.CancelFeatureValueImportRequest
    ) -> featurestore_v1_feature_value_import_service_pb2.CancelFeatureValueImportResponse:
        """Cancels a feature value."""
        deps = self.deps
        response = featurestore_v1_feature_value_import_service_pb2.CancelFeatureValueImportResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CancelFeatureValueImport', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'CancelFeatureValueImport',
                {'reason': request.reason}
            )
            response_0 = lineage_v1_lineage_node_reporting_service_pb2.CountLineageNodeTotalsResponse()
            response_1 = featurestore_v1_feature_view_query_service_pb2.ResolveFeatureViewsResponse()
            outgoing_0 = lineage_v1_lineage_node_reporting_service_pb2.CountLineageNodeTotalsRequest(
                context=request.context,
                filter=lineage_v1_lineage_node_reporting_service_pb2.CountLineageNodeTotalsRequest.Filter(
                    created_after=request.details.effective_at,
                    owner_id=request.details.new_owner.user_id
                )
            )
            outgoing_1 = featurestore_v1_feature_view_query_service_pb2.ResolveFeatureViewsRequest(
                context=request.context
            )
            response_0, response_1 = await asyncio.gather(
                deps.clients.lineage_lineage_node_reporting.CountLineageNodeTotals(
                    outgoing_0,
                    timeout=deps.settings.timeout
                ),
                deps.clients.featurestore_feature_view_query.ResolveFeatureViews(
                    outgoing_1,
                    timeout=deps.settings.timeout
                ),
            )
            returned_0_0 = response_0.result.correlation_id
            if returned_0_0:
                response.result.correlation_id = returned_0_0
            returned_0_1 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_1)
            returned_1_0 = response_1.result.correlation_id
            if returned_1_0:
                response.result.correlation_id = returned_1_0
            returned_1_1 = response_1.result.message
            if returned_1_1:
                response.outcome.message = returned_1_1
            echoed_0 = request.feature_value_id
            response.feature_value.feature_value_id = echoed_0
            echoed_1 = request.details.effective_at
            response.outcome.effective_at.CopyFrom(echoed_1)
            return response

    async def handle_get_feature_value_import_status(
        self,
        request: featurestore_v1_feature_value_import_service_pb2.GetFeatureValueImportStatusRequest
    ) -> featurestore_v1_feature_value_import_service_pb2.GetFeatureValueImportStatusResponse:
        """Returns a feature value."""
        deps = self.deps
        response = featurestore_v1_feature_value_import_service_pb2.GetFeatureValueImportStatusResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('GetFeatureValueImportStatus', extra={'fields': {'locale': request.context.locale}})
            await deps.repository.audit(
                request.context.tenant_id,
                'GetFeatureValueImportStatus',
                {'locale': request.context.locale}
            )
            echoed_0 = request.feature_value_id
            response.feature_value.feature_value_id = echoed_0
            return response

    async def handle_import_feature_values(
        self,
        request: featurestore_v1_feature_value_import_service_pb2.ImportFeatureValuesRequest
    ) -> featurestore_v1_feature_value_import_service_pb2.ImportFeatureValuesResponse:
        """Takes a stream of feature values and answers once at the end."""
        deps = self.deps
        response = featurestore_v1_feature_value_import_service_pb2.ImportFeatureValuesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ImportFeatureValues', extra={'fields': {'sequence': request.sequence}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ImportFeatureValues',
                {'sequence': request.sequence}
            )
            if request.WhichOneof('chunk') == 'record':
                await deps.repository.save_feature_value(request.context.tenant_id, request.record)
            response_0 = lineage_v1_lineage_node_sync_service_pb2.PushLineageNodeResponse()
            outgoing_0 = lineage_v1_lineage_node_sync_service_pb2.PushLineageNodeRequest()
            outgoing_0.context.CopyFrom(request.context)
            if request.WhichOneof('chunk') == 'header':
                field_0_1_part_1 = outgoing_0.lineage_node.children.add()
                field_0_1_part_2 = field_0_1_part_1.children.add()
                field_0_1_part_2.manager.email = request.header.submitted_by.email
            response_0 = await deps.clients.lineage_lineage_node_sync.PushLineageNode(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_0)
            echoed_0 = request.record.correlation_id
            response.result.correlation_id = echoed_0
            return response

    async def handle_list_feature_value_imports(
        self,
        request: featurestore_v1_feature_value_import_service_pb2.ListFeatureValueImportsRequest
    ) -> featurestore_v1_feature_value_import_service_pb2.ListFeatureValueImportsResponse:
        """Lists feature values a page at a time."""
        deps = self.deps
        response = featurestore_v1_feature_value_import_service_pb2.ListFeatureValueImportsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ListFeatureValueImports', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ListFeatureValueImports',
                {'order_by': request.order_by}
            )
            response_0 = featurestore_v1_entity_calculation_service_pb2.CompareEntityOptionsResponse()
            outgoing_0 = featurestore_v1_entity_calculation_service_pb2.CompareEntityOptionsRequest(
                context=request.context,
                entity=featurestore_v1_featurestore_pb2.Entity(
                    contact=common_v1_contact_pb2.ContactInfo(email=request.context.actor.email),
                    primary_address=common_v1_address_pb2.PostalAddress(region=request.filter.region),
                    relationship_manager=identity_v1_refs_pb2.UserRef(user_id=request.context.actor.user_id)
                )
            )
            response_0 = await deps.clients.featurestore_entity_calculation.CompareEntityOptions(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.details
            response.result.details.update(returned_0_0)
            returned_0_1 = response_0.result.correlation_id
            returned_0_1_part_0 = response.feature_values.add()
            if returned_0_1:
                returned_0_1_part_0.correlation_id = returned_0_1
            return response

    async def handle_map_feature_value_import_columns(
        self,
        request: featurestore_v1_feature_value_import_service_pb2.MapFeatureValueImportColumnsRequest
    ) -> featurestore_v1_feature_value_import_service_pb2.MapFeatureValueImportColumnsResponse:
        """Maps a feature value."""
        deps = self.deps
        response = featurestore_v1_feature_value_import_service_pb2.MapFeatureValueImportColumnsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('MapFeatureValueImportColumns', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'MapFeatureValueImportColumns',
                {'reason': request.reason}
            )
            await deps.repository.save_feature_value(request.context.tenant_id, request.feature_value)
            response_0 = featurestore_v1_entity_calculation_service_pb2.CalculateEntityResponse()
            response_1 = datasets_v1_data_schema_validation_service_pb2.ValidateDataSchemaResponse()
            response_2 = featurestore_v1_feature_value_query_service_pb2.ExportFeatureValuesResponse()
            response_3 = datasets_v1_dataset_service_pb2.GetDatasetResponse()
            callbacks_0: list[
                Callable[[], Awaitable[featurestore_v1_entity_calculation_service_pb2.CalculateEntityResponse]]
            ] = []
            for item_0 in request.feature_value.measurements:
                outgoing_0 = featurestore_v1_entity_calculation_service_pb2.CalculateEntityRequest(
                    context=request.context,
                    entity=featurestore_v1_featurestore_pb2.Entity(
                        audit=common_v1_audit_pb2.AuditInfo(created_at=item_0.observed_at),
                        contact=common_v1_contact_pb2.ContactInfo(
                            email=request.details.contact.email,
                            name=request.details.contact.name,
                            phone=request.details.contact.phone
                        )
                    )
                )
                async def send_0(
                    payload: featurestore_v1_entity_calculation_service_pb2.CalculateEntityRequest = outgoing_0
                ) -> featurestore_v1_entity_calculation_service_pb2.CalculateEntityResponse:
                    return await deps.clients.featurestore_entity_calculation.CalculateEntity(
                        payload,
                        timeout=deps.settings.timeout
                    )
                callbacks_0.append(send_0)
            for callback_0 in callbacks_0:
                response_0 = await callback_0()
            outgoing_1 = datasets_v1_data_schema_validation_service_pb2.ValidateDataSchemaRequest(
                context=request.context,
                data_schema=datasets_v1_datasets_pb2.DataSchema(
                    children=[
                        datasets_v1_datasets_pb2.DataSchema(
                            children=[
                                datasets_v1_datasets_pb2.DataSchema(
                                    audit=common_v1_audit_pb2.AuditInfo(etag=response_0.entity.audit.etag),
                                    location=common_v1_address_pb2.PostalAddress(
                                        postal_code=response_0.entity.primary_address.postal_code
                                    )
                                )
                            ]
                        )
                    ]
                )
            )
            response_1 = await hooks.feature_value_import_map_feature_value_import_columns1(
                deps.clients.datasets_data_schema_validation,
                outgoing_1,
                deps.settings.timeout
            )
            for item_2 in request.feature_value.measurements:
                outgoing_2 = featurestore_v1_feature_value_query_service_pb2.ExportFeatureValuesRequest(
                    context=request.context,
                    filter=featurestore_v1_feature_value_query_service_pb2.ExportFeatureValuesRequest.Filter(
                        created_after=item_2.observed_at,
                        region=response_0.entity.primary_address.region
                    )
                )
                async for result_2 in deps.clients.featurestore_feature_value_query.ExportFeatureValues(
                    outgoing_2,
                    timeout=deps.settings.timeout
                ):
                    response_2 = result_2
            outgoing_3 = datasets_v1_dataset_service_pb2.GetDatasetRequest(
                context=request.context,
                dataset_id=request.feature_value.subject.dataset_id
            )
            port_3: FeatureValueImportMapFeatureValueImportColumns3Port = FeatureValueImportMapFeatureValueImportColumns3Adapter(
                deps.clients.datasets_dataset,
                deps.settings.timeout
            )
            response_3 = await port_3.execute(outgoing_3)
            returned_1_0 = response_1.result.message
            if returned_1_0:
                response.result.message = returned_1_0
            returned_3_0 = response_3.dataset.code
            if returned_3_0:
                response.feature_value.subject.code = returned_3_0
            returned_3_1 = response_3.dataset.dimensions.unit
            returned_3_1_part_1 = response.feature_value.measurements.add()
            if returned_3_1:
                returned_3_1_part_1.unit = returned_3_1
            echoed_0 = request.feature_value_id
            response.feature_value.feature_value_id = echoed_0
            echoed_1 = request.feature_value.source
            response.feature_value.source = echoed_1
            return response

    async def handle_retry_feature_value_import(
        self,
        request: featurestore_v1_feature_value_import_service_pb2.RetryFeatureValueImportRequest
    ) -> featurestore_v1_feature_value_import_service_pb2.RetryFeatureValueImportResponse:
        """Retrys a feature value."""
        deps = self.deps
        response = featurestore_v1_feature_value_import_service_pb2.RetryFeatureValueImportResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('RetryFeatureValueImport', extra={'fields': {'initiated_by': request.details.initiated_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'RetryFeatureValueImport',
                {'initiated_by': request.details.initiated_by}
            )
            await deps.repository.save_feature_value(request.context.tenant_id, request.feature_value)
            response_0 = metrics_v1_metric_series_export_service_pb2.ScheduleMetricSeriesExportResponse()
            response_1 = anomalies_v1_anomaly_workflow_service_pb2.AdvanceAnomalyWorkflowResponse()
            response_2 = documents_v1_document_validation_service_pb2.NormalizeDocumentResponse()
            outgoing_0 = metrics_v1_metric_series_export_service_pb2.ScheduleMetricSeriesExportRequest(
                annotations=dict(request.annotations),
                context=request.context,
                details=metrics_v1_metric_series_export_service_pb2.ScheduleMetricSeriesExportRequest.Details(
                    filters=dict(request.feature_value.attributes)
                ),
                reason=request.reason
            )
            steps_0 = [
                partial(
                    deps.clients.metrics_metric_series_export.ScheduleMetricSeriesExport,
                    outgoing_0,
                    timeout=deps.settings.timeout
                )
            ]
            results_0 = await run_steps(steps_0)
            response_0 = results_0[-1]
            outgoing_1 = anomalies_v1_anomaly_workflow_service_pb2.AdvanceAnomalyWorkflowRequest(
                anomaly=anomalies_v1_anomalies_pb2.Anomaly(
                    assignee=identity_v1_refs_pb2.UserRef(email=request.details.notify.email),
                    requester=common_v1_contact_pb2.ContactInfo(name=request.details.notify.name)
                ),
                context=request.context,
                details=anomalies_v1_anomaly_workflow_service_pb2.AdvanceAnomalyWorkflowRequest.Details(
                    notify=common_v1_contact_pb2.ContactInfo(
                        phone=request.details.notify.phone,
                        preferred_channel=request.details.notify.preferred_channel
                    )
                )
            )
            response_1 = await FeatureValueImportRetryFeatureValueImport1Adapter(
                deps.clients.anomalies_anomaly_workflow,
                deps.settings.timeout
            )(outgoing_1)
            outgoing_2 = documents_v1_document_validation_service_pb2.NormalizeDocumentRequest(
                context=request.context,
                details=documents_v1_document_validation_service_pb2.NormalizeDocumentRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(email=response_1.anomaly.requester.email)
                ),
                document=documents_v1_documents_pb2.Document(
                    audit=common_v1_audit_pb2.AuditInfo(etag=response_1.anomaly.audit.etag),
                    counterparty=documents_v1_refs_pb2.DocumentFolderRef(
                        display_name=response_1.anomaly.assignee.display_name
                    ),
                    lines=[documents_v1_documents_pb2.DocumentLine(attributes=dict(request.feature_value.attributes))]
                )
            )
            response_2 = cast(documents_v1_document_validation_service_pb2.NormalizeDocumentResponse, await deps.bus.request(
                'acme.featurestore.v1.FeatureValueImportService/RetryFeatureValueImport/2', outgoing_2, deps.settings.timeout,
            ))
            returned_0_0 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_0)
            returned_1_0 = response_1.result.status
            if returned_1_0:
                response.result.status = returned_1_0
            returned_1_1 = response_1.outcome.status
            if returned_1_1:
                response.outcome.status = returned_1_1
            returned_2_0 = response_2.outcome.status
            if returned_2_0:
                response.outcome.status = returned_2_0
            echoed_0 = request.feature_value_id
            response.feature_value.feature_value_id = echoed_0
            echoed_1 = request.feature_value.source
            response.feature_value.source = echoed_1
            return response

    async def handle_validate_feature_value_import(
        self,
        request: featurestore_v1_feature_value_import_service_pb2.ValidateFeatureValueImportRequest
    ) -> featurestore_v1_feature_value_import_service_pb2.ValidateFeatureValueImportResponse:
        """Validates a feature value."""
        deps = self.deps
        response = featurestore_v1_feature_value_import_service_pb2.ValidateFeatureValueImportResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ValidateFeatureValueImport', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ValidateFeatureValueImport',
                {'reason': request.reason}
            )
            await deps.repository.save_feature_value(request.context.tenant_id, request.feature_value)
            response_0 = featurestore_v1_feature_value_query_service_pb2.ResolveFeatureValuesResponse()
            response_1 = documents_v1_document_validation_service_pb2.PreviewDocumentResponse()
            response_2 = datasets_v1_dataset_version_validation_service_pb2.ExplainDatasetVersionDecisionResponse()
            outgoing_0 = featurestore_v1_feature_value_query_service_pb2.ResolveFeatureValuesRequest(
                context=request.context
            )
            outgoing_1 = documents_v1_document_validation_service_pb2.PreviewDocumentRequest(
                context=request.context,
                details=documents_v1_document_validation_service_pb2.PreviewDocumentRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(phone=request.details.contact.phone)
                )
            )
            response_0, response_1 = await asyncio.gather(
                deps.clients.featurestore_feature_value_query.ResolveFeatureValues(
                    outgoing_0,
                    timeout=deps.settings.timeout
                ),
                deps.clients.documents_document_validation.PreviewDocument(outgoing_1, timeout=deps.settings.timeout),
            )
            async for item_2 in async_messages(request.feature_value.measurements):
                outgoing_2 = datasets_v1_dataset_version_validation_service_pb2.ExplainDatasetVersionDecisionRequest(
                    context=request.context,
                    dataset_version=datasets_v1_datasets_pb2.DatasetVersion(
                        measurements=[
                            datasets_v1_datasets_pb2.DatasetVersionMeasurement(
                                metric=item_2.metric,
                                observed_at=item_2.observed_at,
                                unit=item_2.unit,
                                value=item_2.value
                            )
                        ]
                    )
                )
                response_2 = await deps.clients.datasets_dataset_version_validation.ExplainDatasetVersionDecision(
                    outgoing_2,
                    timeout=deps.settings.timeout
                )
            returned_0_0 = response_0.result.status
            if returned_0_0:
                response.result.status = returned_0_0
            returned_0_1 = response_0.result.message
            if returned_0_1:
                response.result.message = returned_0_1
            returned_1_0 = response_1.result.correlation_id
            if returned_1_0:
                response.result.correlation_id = returned_1_0
            echoed_0 = request.feature_value_id
            response.feature_value.feature_value_id = echoed_0
            echoed_1 = request.feature_value.occurred_at
            response.feature_value.occurred_at.CopyFrom(echoed_1)
            return response
