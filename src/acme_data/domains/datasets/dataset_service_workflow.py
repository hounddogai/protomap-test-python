"""Application workflow for Dataset ."""

from __future__ import annotations

from functools import partial
from typing import cast
import asyncio
import logging

from google.protobuf.any_pb2 import Any as AnyMessage
from google.protobuf.json_format import MessageToDict
from google.protobuf.json_format import ParseDict

from acme.anomalies.v1 import anomaly_query_service_pb2 as anomalies_v1_anomaly_query_service_pb2
from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.customers.v1 import refs_pb2 as customers_v1_refs_pb2
from acme.datasets.v1 import data_schema_calculation_service_pb2 as datasets_v1_data_schema_calculation_service_pb2
from acme.datasets.v1 import data_schema_validation_service_pb2 as datasets_v1_data_schema_validation_service_pb2
from acme.datasets.v1 import dataset_query_service_pb2 as datasets_v1_dataset_query_service_pb2
from acme.datasets.v1 import dataset_service_pb2 as datasets_v1_dataset_service_pb2
from acme.datasets.v1 import dataset_validation_service_pb2 as datasets_v1_dataset_validation_service_pb2
from acme.datasets.v1 import dataset_validation_service_pb2_grpc as datasets_v1_dataset_validation_service_pb2_grpc
from acme.datasets.v1 import (
    dataset_version_validation_service_pb2 as datasets_v1_dataset_version_validation_service_pb2,
)
from acme.datasets.v1 import datasets_pb2 as datasets_v1_datasets_pb2
from acme.featurestore.v1 import (
    feature_value_calculation_service_pb2 as featurestore_v1_feature_value_calculation_service_pb2,
)
from acme.featurestore.v1 import (
    feature_value_validation_service_pb2 as featurestore_v1_feature_value_validation_service_pb2,
)
from acme.featurestore.v1 import feature_view_query_service_pb2 as featurestore_v1_feature_view_query_service_pb2
from acme.featurestore.v1 import featurestore_pb2 as featurestore_v1_featurestore_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.metrics.v1 import metric_alert_history_service_pb2 as metrics_v1_metric_alert_history_service_pb2
from acme.metrics.v1 import metrics_pb2 as metrics_v1_metrics_pb2
from acme.ticketing.v1 import ticket_query_service_pb2 as ticketing_v1_ticket_query_service_pb2

from acme_data.domains.datasets import hooks
from acme_data.domains.datasets.adapters import DatasetCloneDataset1Adapter
from acme_data.domains.datasets.adapters import DatasetCloneDataset1Port
from acme_data.domains.datasets.adapters import DatasetCreateDataset1Adapter
from acme_data.domains.datasets.dependencies import Dependencies
from acme_data.domains.datasets.models import DatasetBatchCreateDatasets1Command
from acme_data.domains.datasets.models import to_dataset_batch_create_datasets1_command
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import run_steps
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class DatasetServicerWorkflow:
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    async def handle_batch_create_datasets(
        self,
        request: datasets_v1_dataset_service_pb2.BatchCreateDatasetsRequest
    ) -> datasets_v1_dataset_service_pb2.BatchCreateDatasetsResponse:
        """Takes a stream of datasets and answers once at the end."""
        deps = self.deps
        response = datasets_v1_dataset_service_pb2.BatchCreateDatasetsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('BatchCreateDatasets', extra={'fields': {'sequence': request.sequence}})
            await deps.repository.audit(
                request.context.tenant_id,
                'BatchCreateDatasets',
                {'sequence': request.sequence}
            )
            if request.WhichOneof('chunk') == 'record':
                await deps.repository.save_dataset(request.context.tenant_id, request.record)
            response_0 = datasets_v1_dataset_validation_service_pb2.CheckDatasetEligibilityResponse()
            response_1 = datasets_v1_dataset_validation_service_pb2.PreviewDatasetResponse()
            response_2 = ticketing_v1_ticket_query_service_pb2.ExportTicketsResponse()
            outgoing_0 = datasets_v1_dataset_validation_service_pb2.CheckDatasetEligibilityRequest(
                context=request.context,
                dataset=datasets_v1_datasets_pb2.Dataset(
                    owner=identity_v1_refs_pb2.UserRef(
                        email=request.record.owner.email,
                        user_id=request.record.owner.user_id
                    )
                )
            )
            registered_0 = cast(
                datasets_v1_dataset_validation_service_pb2_grpc.DatasetValidationServiceStub,
                deps.clients.registry['acme.datasets.v1.DatasetValidationService']
            )
            response_0 = await registered_0.CheckDatasetEligibility(outgoing_0, timeout=deps.settings.timeout)
            command_1 = DatasetBatchCreateDatasets1Command(
                context=request.context,
                dataset_address_recipient=response_0.dataset.address.recipient,
                dataset_audit_created_by=response_0.dataset.audit.created_by,
                dataset_audit_updated_at=response_0.dataset.audit.updated_at,
                dataset_address_region=request.record.address.region
            )
            outgoing_1 = to_dataset_batch_create_datasets1_command(command_1)
            response_1 = await deps.clients.datasets_dataset_validation.PreviewDataset(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = ticketing_v1_ticket_query_service_pb2.ExportTicketsRequest(
                context=request.context,
                filter=ticketing_v1_ticket_query_service_pb2.ExportTicketsRequest.Filter(
                    created_after=response_0.dataset.audit.updated_at,
                    region=response_1.dataset.address.region
                ),
                format=request.header.format
            )
            async for chunk_2 in deps.clients.ticketing_ticket_query.ExportTickets(
                outgoing_2,
                timeout=deps.settings.timeout
            ):
                response_2 = chunk_2
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.result.message = returned_0_0
            returned_0_1 = response_0.result.details
            response.result.details.update(returned_0_1)
            returned_1_0 = response_1.result.details
            response.result.details.update(returned_1_0)
            return response

    async def handle_batch_get_datasets(
        self,
        request: datasets_v1_dataset_service_pb2.BatchGetDatasetsRequest
    ) -> datasets_v1_dataset_service_pb2.BatchGetDatasetsResponse:
        """Returns several datasets at once."""
        deps = self.deps
        response = datasets_v1_dataset_service_pb2.BatchGetDatasetsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('BatchGetDatasets', extra={'fields': {'domain': 'datasets'}})
            await deps.repository.audit(request.context.tenant_id, 'BatchGetDatasets', {})
            response_0 = featurestore_v1_feature_view_query_service_pb2.ResolveFeatureViewsResponse()
            response_1 = featurestore_v1_feature_value_validation_service_pb2.PreviewFeatureValueResponse()
            outgoing_0 = featurestore_v1_feature_view_query_service_pb2.ResolveFeatureViewsRequest(
                context=request.context
            )
            response_0 = await deps.clients.featurestore_feature_view_query.ResolveFeatureViews(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = featurestore_v1_feature_value_validation_service_pb2.PreviewFeatureValueRequest(
                context=request.context,
                feature_value=featurestore_v1_featurestore_pb2.FeatureValue(
                    correlation_id=response_0.result.correlation_id
                )
            )
            response_1 = await hooks.dataset_batch_get_datasets1(
                deps.clients.featurestore_feature_value_validation,
                outgoing_1,
                deps.settings.timeout
            )
            returned_0_0 = response_0.result.correlation_id
            if returned_0_0:
                response.result.correlation_id = returned_0_0
            returned_0_1 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_1)
            returned_1_0 = response_1.feature_value.subject.display_name
            returned_1_0_part_0 = response.datasets.add()
            if returned_1_0:
                returned_1_0_part_0.owner.display_name = returned_1_0
            returned_1_1 = response_1.feature_value.correlation_id
            if returned_1_1:
                response.result.correlation_id = returned_1_1
            return response

    async def handle_clone_dataset(
        self,
        request: datasets_v1_dataset_service_pb2.CloneDatasetRequest
    ) -> datasets_v1_dataset_service_pb2.CloneDatasetResponse:
        """Creates a dataset."""
        deps = self.deps
        response = datasets_v1_dataset_service_pb2.CloneDatasetResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CloneDataset', extra={'fields': {'request_id': request.request_id}})
            await deps.repository.audit(request.context.tenant_id, 'CloneDataset', {'request_id': request.request_id})
            await deps.repository.save_dataset(request.context.tenant_id, request.dataset)
            response_0 = datasets_v1_dataset_validation_service_pb2.LintDatasetsResponse()
            response_1 = metrics_v1_metric_alert_history_service_pb2.CompareMetricAlertVersionsResponse()
            outgoing_0 = datasets_v1_dataset_validation_service_pb2.LintDatasetsRequest()
            outgoing_0.context.CopyFrom(request.context)
            if request.dataset.WhichOneof('locator') == 'address':
                outgoing_0.dataset.address.recipient = request.dataset.address.recipient
            response_0 = await deps.clients.datasets_dataset_validation.LintDatasets(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = metrics_v1_metric_alert_history_service_pb2.CompareMetricAlertVersionsRequest(
                context=request.context,
                metric_alert=metrics_v1_metrics_pb2.MetricAlert(
                    audit=common_v1_audit_pb2.AuditInfo(etag=request.dataset.audit.etag)
                )
            )
            port_1: DatasetCloneDataset1Port = DatasetCloneDataset1Adapter(
                deps.clients.metrics_metric_alert_history,
                deps.settings.timeout
            )
            response_1 = await port_1.execute(outgoing_1)
            returned_0_0 = response_0.dataset.dimensions.height
            if returned_0_0:
                response.dataset.dimensions.height = returned_0_0
            returned_0_1 = response_0.dataset.audit.created_at
            if returned_0_1.ListFields():
                response.dataset.audit.created_at.MergeFrom(returned_0_1)
            returned_1_0 = response_1.outcome.message
            if returned_1_0:
                response.result.message = returned_1_0
            returned_1_1 = response_1.metric_alert.audit.created_at
            if returned_1_1.ListFields():
                response.dataset.audit.created_at.MergeFrom(returned_1_1)
            echoed_0 = request.dataset.specs
            response.dataset.specs.update(echoed_0)
            echoed_1 = request.dataset.status
            response.dataset.status = echoed_1
            return response

    async def handle_create_dataset(
        self,
        request: datasets_v1_dataset_service_pb2.CreateDatasetRequest
    ) -> datasets_v1_dataset_service_pb2.CreateDatasetResponse:
        """Creates a dataset."""
        deps = self.deps
        response = datasets_v1_dataset_service_pb2.CreateDatasetResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CreateDataset', extra={'fields': {'request_id': request.request_id}})
            await deps.repository.audit(request.context.tenant_id, 'CreateDataset', {'request_id': request.request_id})
            await deps.repository.save_dataset(request.context.tenant_id, request.dataset)
            response_0 = featurestore_v1_feature_value_calculation_service_pb2.RecalculateFeatureValuesResponse()
            response_1 = ticketing_v1_ticket_query_service_pb2.SummarizeTicketsResponse()
            outgoing_0 = featurestore_v1_feature_value_calculation_service_pb2.RecalculateFeatureValuesRequest(
                context=request.context,
                details=featurestore_v1_feature_value_calculation_service_pb2.RecalculateFeatureValuesRequest.Details(
                    destination=common_v1_address_pb2.PostalAddress(locality=request.dataset.address.locality)
                )
            )
            steps_0 = [
                partial(
                    deps.clients.featurestore_feature_value_calculation.RecalculateFeatureValues,
                    outgoing_0,
                    timeout=deps.settings.timeout
                )
            ]
            results_0 = await run_steps(steps_0)
            response_0 = results_0[-1]
            outgoing_1 = ticketing_v1_ticket_query_service_pb2.SummarizeTicketsRequest(
                annotations=dict(request.dataset.specs),
                context=request.context,
                details=ticketing_v1_ticket_query_service_pb2.SummarizeTicketsRequest.Details(
                    filters=dict(response_0.feature_value.attributes)
                )
            )
            response_1 = await DatasetCreateDataset1Adapter(
                deps.clients.ticketing_ticket_query,
                deps.settings.timeout
            )(outgoing_1)
            returned_0_0 = response_0.feature_value.subject.dataset_id
            if returned_0_0:
                response.dataset.dataset_id = returned_0_0
            returned_0_1 = response_0.feature_value.subject.code
            if returned_0_1:
                response.dataset.code = returned_0_1
            returned_1_0 = response_1.result.message
            if returned_1_0:
                response.result.message = returned_1_0
            returned_1_1 = response_1.result.status
            if returned_1_1:
                response.result.status = returned_1_1
            echoed_0 = request.dataset.status
            response.dataset.status = echoed_0
            echoed_1 = request.dataset.owner
            response.dataset.owner.CopyFrom(echoed_1)
            return response

    async def handle_delete_dataset(
        self,
        request: datasets_v1_dataset_service_pb2.DeleteDatasetRequest
    ) -> datasets_v1_dataset_service_pb2.DeleteDatasetResponse:
        """Deletes a dataset."""
        deps = self.deps
        response = datasets_v1_dataset_service_pb2.DeleteDatasetResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('DeleteDataset', extra={'fields': {'dataset_id': request.dataset_id}})
            await deps.repository.audit(request.context.tenant_id, 'DeleteDataset', {'dataset_id': request.dataset_id})
            response_0 = datasets_v1_data_schema_validation_service_pb2.CheckDataSchemaEligibilityResponse()
            response_1 = datasets_v1_dataset_query_service_pb2.SummarizeDatasetsResponse()
            response_2 = datasets_v1_data_schema_validation_service_pb2.ValidateDataSchemaResponse()
            outgoing_0 = datasets_v1_data_schema_validation_service_pb2.CheckDataSchemaEligibilityRequest(
                context=request.context,
                data_schema=datasets_v1_datasets_pb2.DataSchema(
                    children=[
                        datasets_v1_datasets_pb2.DataSchema(
                            children=[
                                datasets_v1_datasets_pb2.DataSchema(
                                    audit=common_v1_audit_pb2.AuditInfo(etag=request.etag)
                                )
                            ]
                        )
                    ]
                )
            )
            response_0 = cast(datasets_v1_data_schema_validation_service_pb2.CheckDataSchemaEligibilityResponse, await deps.bus.request(
                'acme.datasets.v1.DatasetService/DeleteDataset/0', outgoing_0, deps.settings.timeout,
            ))
            outgoing_1 = datasets_v1_dataset_query_service_pb2.SummarizeDatasetsRequest(
                context=request.context,
                reason=request.reason
            )
            response_1 = await deps.clients.datasets_dataset_query.SummarizeDatasets(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = datasets_v1_data_schema_validation_service_pb2.ValidateDataSchemaRequest(
                context=request.context,
                data_schema=datasets_v1_datasets_pb2.DataSchema(
                    children=[
                        datasets_v1_datasets_pb2.DataSchema(
                            children=[
                                datasets_v1_datasets_pb2.DataSchema(
                                    audit=common_v1_audit_pb2.AuditInfo(
                                        created_by=response_0.data_schema.audit.created_by,
                                        updated_by=response_0.data_schema.audit.updated_by
                                    ),
                                    location=common_v1_address_pb2.PostalAddress(
                                        recipient=response_0.data_schema.location.recipient
                                    )
                                )
                            ]
                        )
                    ]
                )
            )
            method_name_2 = 'ValidateDataSchema'
            response_2 = await getattr(
                deps.clients.datasets_data_schema_validation,
                method_name_2
            )(outgoing_2, timeout=deps.settings.timeout)
            returned_0_0 = response_0.result.status
            if returned_0_0:
                response.result.status = returned_0_0
            returned_0_1 = response_0.result.details
            response.result.details.update(returned_0_1)
            returned_1_0 = response_1.result.correlation_id
            if returned_1_0:
                response.result.correlation_id = returned_1_0
            returned_1_1 = response_1.result.status
            if returned_1_1:
                response.result.status = returned_1_1
            returned_2_0 = response_2.result.correlation_id
            if returned_2_0:
                response.result.correlation_id = returned_2_0
            returned_2_1 = response_2.outcome.message
            if returned_2_1:
                response.result.message = returned_2_1
            return response

    async def handle_get_dataset(
        self,
        request: datasets_v1_dataset_service_pb2.GetDatasetRequest
    ) -> datasets_v1_dataset_service_pb2.GetDatasetResponse:
        """Returns a dataset."""
        deps = self.deps
        response = datasets_v1_dataset_service_pb2.GetDatasetResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('GetDataset', extra={'fields': {'locale': request.context.locale}})
            await deps.repository.audit(request.context.tenant_id, 'GetDataset', {'locale': request.context.locale})
            echoed_0 = request.dataset_id
            response.dataset.dataset_id = echoed_0
            return response

    async def handle_list_datasets(
        self,
        request: datasets_v1_dataset_service_pb2.ListDatasetsRequest
    ) -> datasets_v1_dataset_service_pb2.ListDatasetsResponse:
        """Lists datasets a page at a time."""
        deps = self.deps
        response = datasets_v1_dataset_service_pb2.ListDatasetsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ListDatasets', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(request.context.tenant_id, 'ListDatasets', {'order_by': request.order_by})
            response_0 = datasets_v1_dataset_version_validation_service_pb2.NormalizeDatasetVersionResponse()
            outgoing_0 = datasets_v1_dataset_version_validation_service_pb2.NormalizeDatasetVersionRequest(
                context=request.context,
                dataset_version=datasets_v1_datasets_pb2.DatasetVersion(
                    subject=customers_v1_refs_pb2.CustomerRef(email=request.context.actor.email)
                )
            )
            response_0 = await deps.clients.datasets_dataset_version_validation.NormalizeDatasetVersion(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.dataset_version.subject.display_name
            returned_0_0_part_0 = response.datasets.add()
            if returned_0_0:
                returned_0_0_part_0.owner.display_name = returned_0_0
            returned_0_1 = response_0.result.details
            response.result.details.update(returned_0_1)
            return response

    async def handle_search_datasets(
        self,
        request: datasets_v1_dataset_service_pb2.SearchDatasetsRequest
    ) -> datasets_v1_dataset_service_pb2.SearchDatasetsResponse:
        """Lists datasets a page at a time."""
        deps = self.deps
        response = datasets_v1_dataset_service_pb2.SearchDatasetsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SearchDatasets', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(request.context.tenant_id, 'SearchDatasets', {'order_by': request.order_by})
            return response

    async def handle_update_dataset(
        self,
        request: datasets_v1_dataset_service_pb2.UpdateDatasetRequest
    ) -> datasets_v1_dataset_service_pb2.UpdateDatasetResponse:
        """Changes a dataset."""
        deps = self.deps
        response = datasets_v1_dataset_service_pb2.UpdateDatasetResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('UpdateDataset', extra={'fields': {'allow_missing': request.allow_missing}})
            await deps.repository.audit(
                request.context.tenant_id,
                'UpdateDataset',
                {'allow_missing': request.allow_missing}
            )
            await deps.repository.save_dataset(request.context.tenant_id, request.dataset)
            response_0 = datasets_v1_dataset_query_service_pb2.CountDatasetsResponse()
            outgoing_0 = datasets_v1_dataset_query_service_pb2.CountDatasetsRequest(
                context=request.context,
                filter=datasets_v1_dataset_query_service_pb2.CountDatasetsRequest.Filter(
                    region=request.dataset.address.region
                )
            )
            document_0 = MessageToDict(outgoing_0, preserving_proto_field_name=True)
            outgoing_0 = ParseDict(document_0, datasets_v1_dataset_query_service_pb2.CountDatasetsRequest())
            response_0 = await deps.clients.datasets_dataset_query.CountDatasets(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_0)
            echoed_0 = request.dataset.status
            response.dataset.status = echoed_0
            echoed_1 = request.dataset.name
            response.dataset.name = echoed_1
            return response

    async def handle_watch_datasets(
        self,
        request: datasets_v1_dataset_service_pb2.WatchDatasetsRequest
    ) -> datasets_v1_dataset_service_pb2.WatchDatasetsResponse:
        """Streams the changes of datasets as they happen."""
        deps = self.deps
        response = datasets_v1_dataset_service_pb2.WatchDatasetsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('WatchDatasets', extra={'fields': {'max_events': request.max_events}})
            await deps.repository.audit(request.context.tenant_id, 'WatchDatasets', {'max_events': request.max_events})
            response_0 = anomalies_v1_anomaly_query_service_pb2.BrowseAnomaliesResponse()
            response_1 = datasets_v1_data_schema_calculation_service_pb2.CompareDataSchemaOptionsResponse()
            response_2 = metrics_v1_metric_alert_history_service_pb2.RecordMetricAlertVersionResponse()
            response_3 = datasets_v1_dataset_validation_service_pb2.LintDatasetsResponse()
            outgoing_0 = anomalies_v1_anomaly_query_service_pb2.BrowseAnomaliesRequest(
                context=request.context,
                filter=anomalies_v1_anomaly_query_service_pb2.BrowseAnomaliesRequest.Filter(
                    created_after=request.filter.created_after,
                    labels=dict(request.filter.labels),
                    query=request.filter.query
                )
            )
            outgoing_1 = datasets_v1_data_schema_calculation_service_pb2.CompareDataSchemaOptionsRequest(
                context=request.context,
                data_schema=datasets_v1_datasets_pb2.DataSchema(
                    children=[
                        datasets_v1_datasets_pb2.DataSchema(
                            children=[
                                datasets_v1_datasets_pb2.DataSchema(
                                    manager=identity_v1_refs_pb2.UserRef(email=request.subscriber.email)
                                )
                            ],
                            location=common_v1_address_pb2.PostalAddress(region=request.filter.region),
                            manager=identity_v1_refs_pb2.UserRef(
                                email=request.context.actor.email,
                                user_id=request.context.actor.user_id
                            )
                        )
                    ]
                )
            )
            response_0, response_1 = await asyncio.gather(
                deps.clients.anomalies_anomaly_query.BrowseAnomalies(outgoing_0, timeout=deps.settings.timeout),
                deps.clients.datasets_data_schema_calculation.CompareDataSchemaOptions(
                    outgoing_1,
                    timeout=deps.settings.timeout
                ),
            )
            outgoing_2 = metrics_v1_metric_alert_history_service_pb2.RecordMetricAlertVersionRequest(
                context=request.context,
                metric_alert=metrics_v1_metrics_pb2.MetricAlert(
                    audit=common_v1_audit_pb2.AuditInfo(
                        created_by=response_1.data_schema.audit.created_by,
                        etag=response_1.data_schema.audit.etag
                    ),
                    block=metrics_v1_metrics_pb2.MetricAlertBlockAction(
                        notify_email=response_1.data_schema.manager.email
                    ),
                    owner=identity_v1_refs_pb2.UserRef(email=request.subscriber.email)
                )
            )
            envelope_2 = AnyMessage()
            envelope_2.Pack(outgoing_2)
            outgoing_2 = metrics_v1_metric_alert_history_service_pb2.RecordMetricAlertVersionRequest()
            if not envelope_2.Unpack(outgoing_2):
                raise ValueError("partner envelope contains the wrong request type")
            response_2 = await deps.clients.metrics_metric_alert_history.RecordMetricAlertVersion(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            outgoing_3 = datasets_v1_dataset_validation_service_pb2.LintDatasetsRequest(
                context=request.context,
                dataset=datasets_v1_datasets_pb2.Dataset(
                    owner=identity_v1_refs_pb2.UserRef(user_id=response_2.metric_alert.owner.user_id)
                ),
                details=datasets_v1_dataset_validation_service_pb2.LintDatasetsRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(name=request.subscriber.name)
                )
            )
            registered_3 = cast(
                datasets_v1_dataset_validation_service_pb2_grpc.DatasetValidationServiceStub,
                deps.clients.registry['acme.datasets.v1.DatasetValidationService']
            )
            response_3 = await registered_3.LintDatasets(outgoing_3, timeout=deps.settings.timeout)
            returned_0_0 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_0)
            returned_0_1 = response_0.result.correlation_id
            if returned_0_1:
                response.result.correlation_id = returned_0_1
            returned_1_0 = response_1.data_schema.audit.created_by
            if returned_1_0:
                response.dataset.audit.created_by = returned_1_0
            returned_2_0 = response_2.metric_alert.name
            if returned_2_0:
                response.dataset.name = returned_2_0
            returned_2_1 = response_2.metric_alert.audit.created_by
            if returned_2_1:
                response.dataset.audit.created_by = returned_2_1
            returned_3_0 = response_3.dataset.dimensions.weight
            if returned_3_0:
                response.dataset.dimensions.weight = returned_3_0
            returned_3_1 = response_3.result.correlation_id
            if returned_3_1:
                response.result.correlation_id = returned_3_1
            echoed_0 = request.subscriber.email
            response.dataset.owner.email = echoed_0
            return response
