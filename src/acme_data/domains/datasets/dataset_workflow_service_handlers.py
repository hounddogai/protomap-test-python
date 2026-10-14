"""Reusable transport mixin for DatasetWorkflowService."""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any
from typing import cast
import asyncio
import logging

from google.protobuf.any_pb2 import Any as AnyMessage
from google.protobuf.json_format import MessageToDict
from google.protobuf.json_format import MessageToJson
from google.protobuf.json_format import Parse
from google.protobuf.json_format import ParseDict
import grpc

from acme.boxoffice.v1 import (
    box_office_sale_calculation_service_pb2 as boxoffice_v1_box_office_sale_calculation_service_pb2,
)
from acme.boxoffice.v1 import (
    box_office_sale_calculation_service_pb2_grpc as boxoffice_v1_box_office_sale_calculation_service_pb2_grpc,
)
from acme.boxoffice.v1 import boxoffice_pb2 as boxoffice_v1_boxoffice_pb2
from acme.collections.v1 import collection_case_service_pb2 as collections_v1_collection_case_service_pb2
from acme.collections.v1 import collections_pb2 as collections_v1_collections_pb2
from acme.collections.v1 import refs_pb2 as collections_v1_refs_pb2
from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.customers.v1 import customer_service_pb2 as customers_v1_customer_service_pb2
from acme.customers.v1 import customer_validation_service_pb2 as customers_v1_customer_validation_service_pb2
from acme.customers.v1 import customers_pb2 as customers_v1_customers_pb2
from acme.customers.v1 import household_query_service_pb2 as customers_v1_household_query_service_pb2
from acme.customers.v1 import refs_pb2 as customers_v1_refs_pb2
from acme.datasets.v1 import data_schema_calculation_service_pb2 as datasets_v1_data_schema_calculation_service_pb2
from acme.datasets.v1 import data_schema_validation_service_pb2 as datasets_v1_data_schema_validation_service_pb2
from acme.datasets.v1 import dataset_approval_service_pb2 as datasets_v1_dataset_approval_service_pb2
from acme.datasets.v1 import dataset_service_pb2 as datasets_v1_dataset_service_pb2
from acme.datasets.v1 import (
    dataset_version_validation_service_pb2 as datasets_v1_dataset_version_validation_service_pb2,
)
from acme.datasets.v1 import dataset_workflow_service_pb2 as datasets_v1_dataset_workflow_service_pb2
from acme.datasets.v1 import datasets_pb2 as datasets_v1_datasets_pb2
from acme.featurestore.v1 import feature_value_sync_service_pb2 as featurestore_v1_feature_value_sync_service_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.ledger.v1 import ledger_account_service_pb2 as ledger_v1_ledger_account_service_pb2
from acme.lineage.v1 import lineage_edge_import_service_pb2 as lineage_v1_lineage_edge_import_service_pb2
from acme.lineage.v1 import lineage_pb2 as lineage_v1_lineage_pb2
from acme.metrics.v1 import metric_alert_export_service_pb2 as metrics_v1_metric_alert_export_service_pb2
from acme.modelregistry.v1 import (
    model_version_workflow_service_pb2 as modelregistry_v1_model_version_workflow_service_pb2,
)
from acme.modelregistry.v1 import modelregistry_pb2 as modelregistry_v1_modelregistry_pb2
from acme.modelregistry.v1 import (
    registered_model_sync_service_pb2 as modelregistry_v1_registered_model_sync_service_pb2,
)
from acme.reviews.v1 import product_review_service_pb2 as reviews_v1_product_review_service_pb2
from acme.search.v1 import search_index_query_service_pb2 as search_v1_search_index_query_service_pb2

from acme_data.domains.datasets.adapters import DatasetWorkflowResumeDatasetWorkflow1Adapter
from acme_data.domains.datasets.dependencies import Dependencies
from acme_data.domains.datasets.models import DatasetWorkflowCancelDatasetWorkflow3Command
from acme_data.domains.datasets.models import to_dataset_workflow_cancel_dataset_workflow3_command
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class DatasetWorkflowServicerHandlers:
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    async def AdvanceDatasetWorkflow(
        self, request: datasets_v1_dataset_workflow_service_pb2.AdvanceDatasetWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> datasets_v1_dataset_workflow_service_pb2.AdvanceDatasetWorkflowResponse:
        """Advances a dataset."""
        return await self.handle_advance_dataset_workflow(request)

    @rpc_errors
    async def CancelDatasetWorkflow(
        self, request: datasets_v1_dataset_workflow_service_pb2.CancelDatasetWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> datasets_v1_dataset_workflow_service_pb2.CancelDatasetWorkflowResponse:
        """Cancels a dataset."""
        return await self.handle_cancel_dataset_workflow(request)

    @rpc_errors
    @retry_transient
    async def InspectDatasetWorkflow(
        self, request: datasets_v1_dataset_workflow_service_pb2.InspectDatasetWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> datasets_v1_dataset_workflow_service_pb2.InspectDatasetWorkflowResponse:
        """Returns a dataset."""
        return await self.handle_inspect_dataset_workflow(request)

    @rpc_errors
    @retry_transient
    async def ListDatasetWorkflows(
        self, request: datasets_v1_dataset_workflow_service_pb2.ListDatasetWorkflowsRequest, context: grpc.aio.ServicerContext,
    ) -> datasets_v1_dataset_workflow_service_pb2.ListDatasetWorkflowsResponse:
        """Lists datasets a page at a time."""
        return await self.handle_list_dataset_workflows(request)

    @rpc_errors
    async def PauseDatasetWorkflow(
        self, request: datasets_v1_dataset_workflow_service_pb2.PauseDatasetWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> datasets_v1_dataset_workflow_service_pb2.PauseDatasetWorkflowResponse:
        """Pauses a dataset."""
        return await self.handle_pause_dataset_workflow(request)

    @rpc_errors
    async def ResumeDatasetWorkflow(
        self, request: datasets_v1_dataset_workflow_service_pb2.ResumeDatasetWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> datasets_v1_dataset_workflow_service_pb2.ResumeDatasetWorkflowResponse:
        """Resumes a dataset."""
        return await self.handle_resume_dataset_workflow(request)

    @rpc_errors
    async def SignalDatasetWorkflow(
        self, request: datasets_v1_dataset_workflow_service_pb2.SignalDatasetWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> datasets_v1_dataset_workflow_service_pb2.SignalDatasetWorkflowResponse:
        """Signals a dataset."""
        return await self.handle_signal_dataset_workflow(request)

    @rpc_errors
    async def StartDatasetWorkflow(
        self, request: datasets_v1_dataset_workflow_service_pb2.StartDatasetWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> datasets_v1_dataset_workflow_service_pb2.StartDatasetWorkflowResponse:
        """Starts a dataset."""
        return await self.handle_start_dataset_workflow(request)

    async def handle_advance_dataset_workflow(
        self,
        request: datasets_v1_dataset_workflow_service_pb2.AdvanceDatasetWorkflowRequest
    ) -> datasets_v1_dataset_workflow_service_pb2.AdvanceDatasetWorkflowResponse:
        """Advances a dataset."""
        deps = self.deps
        response = datasets_v1_dataset_workflow_service_pb2.AdvanceDatasetWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('AdvanceDatasetWorkflow', extra={'fields': {'capacity': request.dataset.capacity}})
            await deps.repository.audit(
                request.context.tenant_id,
                'AdvanceDatasetWorkflow',
                {'capacity': request.dataset.capacity}
            )
            await deps.repository.save_dataset(request.context.tenant_id, request.dataset)
            response_0 = datasets_v1_dataset_service_pb2.DeleteDatasetResponse()
            response_1 = modelregistry_v1_registered_model_sync_service_pb2.ResolveRegisteredModelConflictResponse()
            outgoing_0 = datasets_v1_dataset_service_pb2.DeleteDatasetRequest(
                context=request.context,
                dataset_id=request.dataset.dataset_id,
                etag=request.dataset.audit.etag,
                reason=request.reason
            )
            document_0 = MessageToDict(outgoing_0, preserving_proto_field_name=True)
            outgoing_0 = ParseDict(document_0, datasets_v1_dataset_service_pb2.DeleteDatasetRequest())
            response_0 = await deps.clients.datasets_dataset.DeleteDataset(outgoing_0, timeout=deps.settings.timeout)
            outgoing_1 = modelregistry_v1_registered_model_sync_service_pb2.ResolveRegisteredModelConflictRequest()
            outgoing_1.context.CopyFrom(request.context)
            if request.dataset.WhichOneof('locator') == 'address':
                outgoing_1.registered_model.address.lines.extend(list(request.dataset.address.lines))
            outgoing_1.registered_model.audit.etag = request.dataset.audit.etag
            response_1 = await deps.clients.modelregistry_registered_model_sync.ResolveRegisteredModelConflict(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_0)
            returned_0_1 = response_0.result.status
            if returned_0_1:
                response.outcome.status = returned_0_1
            returned_1_0 = response_1.result.status
            if returned_1_0:
                response.outcome.status = returned_1_0
            returned_1_1 = response_1.outcome.reference_id
            if returned_1_1:
                response.outcome.reference_id = returned_1_1
            echoed_0 = request.dataset_id
            response.dataset.dataset_id = echoed_0
            echoed_1 = request.dataset.status
            response.dataset.status = echoed_1
            return response

    async def handle_cancel_dataset_workflow(
        self,
        request: datasets_v1_dataset_workflow_service_pb2.CancelDatasetWorkflowRequest
    ) -> datasets_v1_dataset_workflow_service_pb2.CancelDatasetWorkflowResponse:
        """Cancels a dataset."""
        deps = self.deps
        response = datasets_v1_dataset_workflow_service_pb2.CancelDatasetWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CancelDatasetWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'CancelDatasetWorkflow', {'reason': request.reason})
            await deps.repository.save_dataset(request.context.tenant_id, request.dataset)
            response_0 = customers_v1_household_query_service_pb2.ResolveHouseholdsResponse()
            response_1 = datasets_v1_data_schema_validation_service_pb2.ValidateDataSchemaResponse()
            response_2 = ledger_v1_ledger_account_service_pb2.SearchLedgerAccountsResponse()
            response_3 = datasets_v1_dataset_approval_service_pb2.SubmitDatasetResponse()
            outgoing_0 = customers_v1_household_query_service_pb2.ResolveHouseholdsRequest(context=request.context)
            outgoing_1 = datasets_v1_data_schema_validation_service_pb2.ValidateDataSchemaRequest(
                context=request.context,
                data_schema=datasets_v1_datasets_pb2.DataSchema(
                    children=[
                        datasets_v1_datasets_pb2.DataSchema(
                            children=[
                                datasets_v1_datasets_pb2.DataSchema(
                                    audit=common_v1_audit_pb2.AuditInfo(created_at=request.dataset.audit.created_at),
                                    location=common_v1_address_pb2.PostalAddress(
                                        postal_code=request.dataset.address.postal_code
                                    )
                                )
                            ]
                        )
                    ]
                )
            )
            response_0, response_1 = await asyncio.gather(
                deps.clients.customers_household_query.ResolveHouseholds(outgoing_0, timeout=deps.settings.timeout),
                deps.clients.datasets_data_schema_validation.ValidateDataSchema(
                    outgoing_1,
                    timeout=deps.settings.timeout
                ),
            )
            outgoing_2 = ledger_v1_ledger_account_service_pb2.SearchLedgerAccountsRequest()
            outgoing_2.context.CopyFrom(request.context)
            if request.dataset.WhichOneof('locator') == 'address':
                outgoing_2.filter.region = request.dataset.address.region
            outgoing_2.filter.created_after.CopyFrom(response_1.data_schema.audit.created_at)
            response_2 = await deps.clients.ledger_ledger_account.SearchLedgerAccounts(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            command_3 = DatasetWorkflowCancelDatasetWorkflow3Command(
                context=request.context,
                dataset_owner_email=request.details.notify.email,
                dataset_dimensions_height=request.dataset.dimensions.height,
                dataset_audit_created_at=response_1.data_schema.audit.created_at,
                dataset_audit_updated_by=response_1.data_schema.audit.updated_by
            )
            outgoing_3 = to_dataset_workflow_cancel_dataset_workflow3_command(command_3)
            response_3 = await deps.clients.datasets_dataset_approval.SubmitDataset(
                outgoing_3,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.result.message = returned_0_0
            returned_1_0 = response_1.outcome.effective_at
            if returned_1_0.ListFields():
                response.outcome.effective_at.MergeFrom(returned_1_0)
            returned_1_1 = response_1.data_schema.audit.etag
            if returned_1_1:
                response.dataset.audit.etag = returned_1_1
            returned_2_0 = response_2.result.status
            if returned_2_0:
                response.outcome.status = returned_2_0
            returned_2_1 = response_2.result.details
            response.result.details.update(returned_2_1)
            returned_3_0 = response_3.dataset.dimensions.length
            if returned_3_0:
                response.dataset.dimensions.length = returned_3_0
            echoed_0 = request.dataset_id
            response.dataset.dataset_id = echoed_0
            echoed_1 = request.dataset.status
            response.dataset.status = echoed_1
            return response

    async def handle_inspect_dataset_workflow(
        self,
        request: datasets_v1_dataset_workflow_service_pb2.InspectDatasetWorkflowRequest
    ) -> datasets_v1_dataset_workflow_service_pb2.InspectDatasetWorkflowResponse:
        """Returns a dataset."""
        deps = self.deps
        response = datasets_v1_dataset_workflow_service_pb2.InspectDatasetWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('InspectDatasetWorkflow', extra={'fields': {'domain': 'datasets'}})
            await deps.repository.audit(request.context.tenant_id, 'InspectDatasetWorkflow', {})
            response_0 = lineage_v1_lineage_edge_import_service_pb2.RetryLineageEdgeImportResponse()
            outgoing_0 = lineage_v1_lineage_edge_import_service_pb2.RetryLineageEdgeImportRequest(
                context=request.context,
                details=lineage_v1_lineage_edge_import_service_pb2.RetryLineageEdgeImportRequest.Details(
                    notify=common_v1_contact_pb2.ContactInfo(email=request.context.actor.email)
                ),
                lineage_edge=lineage_v1_lineage_pb2.LineageEdge(correlation_id=request.dataset_id)
            )
            response_0 = await deps.clients.lineage_lineage_edge_import.RetryLineageEdgeImport(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.details
            response.result.details.update(returned_0_0)
            returned_0_1 = response_0.result.status
            if returned_0_1:
                response.result.status = returned_0_1
            echoed_0 = request.dataset_id
            response.dataset.dataset_id = echoed_0
            return response

    async def handle_list_dataset_workflows(
        self,
        request: datasets_v1_dataset_workflow_service_pb2.ListDatasetWorkflowsRequest
    ) -> datasets_v1_dataset_workflow_service_pb2.ListDatasetWorkflowsResponse:
        """Lists datasets a page at a time."""
        deps = self.deps
        response = datasets_v1_dataset_workflow_service_pb2.ListDatasetWorkflowsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ListDatasetWorkflows', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ListDatasetWorkflows',
                {'order_by': request.order_by}
            )
            response_0 = datasets_v1_data_schema_calculation_service_pb2.QuoteDataSchemaResponse()
            outgoing_0 = datasets_v1_data_schema_calculation_service_pb2.QuoteDataSchemaRequest(
                context=request.context,
                data_schema=datasets_v1_datasets_pb2.DataSchema(
                    children=[
                        datasets_v1_datasets_pb2.DataSchema(
                            location=common_v1_address_pb2.PostalAddress(region=request.filter.region),
                            manager=identity_v1_refs_pb2.UserRef(
                                email=request.context.actor.email,
                                user_id=request.context.actor.user_id
                            )
                        )
                    ]
                )
            )
            response_0 = await deps.clients.datasets_data_schema_calculation.QuoteDataSchema(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.correlation_id
            if returned_0_0:
                response.result.correlation_id = returned_0_0
            returned_0_1 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_1)
            return response

    async def handle_pause_dataset_workflow(
        self,
        request: datasets_v1_dataset_workflow_service_pb2.PauseDatasetWorkflowRequest
    ) -> datasets_v1_dataset_workflow_service_pb2.PauseDatasetWorkflowResponse:
        """Pauses a dataset."""
        deps = self.deps
        response = datasets_v1_dataset_workflow_service_pb2.PauseDatasetWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('PauseDatasetWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'PauseDatasetWorkflow', {'reason': request.reason})
            await deps.repository.save_dataset(request.context.tenant_id, request.dataset)
            response_0 = datasets_v1_dataset_approval_service_pb2.SubmitDatasetResponse()
            response_1 = modelregistry_v1_model_version_workflow_service_pb2.RetryModelVersionWorkflowResponse()
            response_2 = datasets_v1_data_schema_calculation_service_pb2.CalculateDataSchemaResponse()
            outgoing_0 = datasets_v1_dataset_approval_service_pb2.SubmitDatasetRequest(
                context=request.context,
                dataset=datasets_v1_datasets_pb2.Dataset(
                    components={
                        'primary': datasets_v1_datasets_pb2.DatasetComponent(
                            quantity=request.dataset.components.get(
                                'primary',
                                datasets_v1_datasets_pb2.DatasetComponent()
                            ).quantity
                        )
                    }
                ),
                details=datasets_v1_dataset_approval_service_pb2.SubmitDatasetRequest.Details(
                    approver=identity_v1_refs_pb2.UserRef(
                        email=request.dataset.owner.email,
                        user_id=request.dataset.owner.user_id
                    )
                )
            )
            outgoing_1 = modelregistry_v1_model_version_workflow_service_pb2.RetryModelVersionWorkflowRequest(
                context=request.context,
                details=modelregistry_v1_model_version_workflow_service_pb2.RetryModelVersionWorkflowRequest.Details(
                    notify=common_v1_contact_pb2.ContactInfo(
                        preferred_channel=request.details.notify.preferred_channel
                    ),
                    parameters=dict(request.details.parameters)
                ),
                model_version=modelregistry_v1_modelregistry_pb2.ModelVersion(
                    subject=customers_v1_refs_pb2.CustomerRef(display_name=request.dataset.owner.display_name)
                )
            )
            response_0, response_1 = await asyncio.gather(
                deps.clients.datasets_dataset_approval.SubmitDataset(outgoing_0, timeout=deps.settings.timeout),
                deps.clients.modelregistry_model_version_workflow.RetryModelVersionWorkflow(
                    outgoing_1,
                    timeout=deps.settings.timeout
                ),
            )
            outgoing_2 = datasets_v1_data_schema_calculation_service_pb2.CalculateDataSchemaRequest()
            outgoing_2.context.CopyFrom(request.context)
            if response_0.dataset.WhichOneof('locator') == 'address':
                field_2_1_part_1 = outgoing_2.data_schema.children.add()
                field_2_1_part_2 = field_2_1_part_1.children.add()
                field_2_1_part_2.location.lines.extend(list(response_0.dataset.address.lines))
            response_2 = await deps.clients.datasets_data_schema_calculation.CalculateDataSchema(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.dataset.components.get(
                'primary',
                datasets_v1_datasets_pb2.DatasetComponent()
            ).quantity
            if returned_0_0:
                response.dataset.components['primary'].quantity = returned_0_0
            returned_0_1 = response_0.result.details
            response.result.details.update(returned_0_1)
            returned_1_0 = response_1.result.details
            response.result.details.update(returned_1_0)
            returned_2_0 = response_2.data_schema.audit.updated_at
            if returned_2_0.ListFields():
                response.dataset.audit.updated_at.MergeFrom(returned_2_0)
            echoed_0 = request.dataset_id
            response.dataset.dataset_id = echoed_0
            echoed_1 = request.dataset.capacity
            response.dataset.capacity = echoed_1
            return response

    async def handle_resume_dataset_workflow(
        self,
        request: datasets_v1_dataset_workflow_service_pb2.ResumeDatasetWorkflowRequest
    ) -> datasets_v1_dataset_workflow_service_pb2.ResumeDatasetWorkflowResponse:
        """Resumes a dataset."""
        deps = self.deps
        response = datasets_v1_dataset_workflow_service_pb2.ResumeDatasetWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ResumeDatasetWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'ResumeDatasetWorkflow', {'reason': request.reason})
            await deps.repository.save_dataset(request.context.tenant_id, request.dataset)
            response_0 = metrics_v1_metric_alert_export_service_pb2.StreamMetricAlertExportResponse()
            response_1 = search_v1_search_index_query_service_pb2.BrowseSearchIndexesResponse()
            response_2 = datasets_v1_dataset_version_validation_service_pb2.ScoreDatasetVersionResponse()
            response_3 = collections_v1_collection_case_service_pb2.CloneCollectionCaseResponse()
            outgoing_0 = metrics_v1_metric_alert_export_service_pb2.StreamMetricAlertExportRequest(
                context=request.context,
                filter=metrics_v1_metric_alert_export_service_pb2.StreamMetricAlertExportRequest.Filter(
                    created_after=request.dataset.audit.updated_at,
                    owner_id=request.dataset.owner.user_id,
                    region=request.dataset.address.region
                )
            )
            async for chunk_0 in deps.clients.metrics_metric_alert_export.StreamMetricAlertExport(
                outgoing_0,
                timeout=deps.settings.timeout
            ):
                response_0 = chunk_0
            outgoing_1 = search_v1_search_index_query_service_pb2.BrowseSearchIndexesRequest(
                context=request.context,
                filter=search_v1_search_index_query_service_pb2.BrowseSearchIndexesRequest.Filter(
                    created_after=request.dataset.audit.created_at,
                    labels=dict(request.dataset.specs),
                    owner_id=request.dataset.components.get(
                        'primary',
                        datasets_v1_datasets_pb2.DatasetComponent()
                    ).component_id,
                    region=request.dataset.address.region
                )
            )
            response_1 = await DatasetWorkflowResumeDatasetWorkflow1Adapter(
                deps.clients.search_search_index_query,
                deps.settings.timeout
            )(outgoing_1)
            outgoing_2 = datasets_v1_dataset_version_validation_service_pb2.ScoreDatasetVersionRequest()
            outgoing_2.context.CopyFrom(request.context)
            outgoing_2.dataset_version.subject.display_name = request.dataset.owner.display_name
            if request.dataset.WhichOneof('locator') == 'address':
                outgoing_2.details.destination.country_code = request.dataset.address.country_code
            if request.dataset.WhichOneof('locator') == 'address':
                outgoing_2.details.destination.recipient = request.dataset.address.recipient
            outgoing_2.dataset_version.subject.email = request.details.notify.email
            response_2 = await deps.clients.datasets_dataset_version_validation.ScoreDatasetVersion(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            outgoing_3 = collections_v1_collection_case_service_pb2.CloneCollectionCaseRequest(
                collection_case=collections_v1_collections_pb2.CollectionCase(
                    audit=common_v1_audit_pb2.AuditInfo(
                        created_by=request.dataset.audit.created_by,
                        updated_by=request.dataset.audit.updated_by
                    ),
                    customer=collections_v1_refs_pb2.PaymentPromiseRef(
                        display_name=response_2.dataset_version.subject.display_name
                    ),
                    requester=common_v1_contact_pb2.ContactInfo(email=request.dataset.owner.email)
                ),
                context=request.context
            )
            response_3 = await deps.clients.collections_collection_case.CloneCollectionCase(
                outgoing_3,
                timeout=deps.settings.timeout
            )
            returned_1_0 = response_1.result.reference_ids
            response.result.reference_ids.extend(returned_1_0)
            returned_2_0 = response_2.result.message
            if returned_2_0:
                response.outcome.message = returned_2_0
            returned_3_0 = response_3.result.details
            response.result.details.update(returned_3_0)
            echoed_0 = request.dataset_id
            response.dataset.dataset_id = echoed_0
            echoed_1 = request.dataset.code
            response.dataset.code = echoed_1
            return response

    async def handle_signal_dataset_workflow(
        self,
        request: datasets_v1_dataset_workflow_service_pb2.SignalDatasetWorkflowRequest
    ) -> datasets_v1_dataset_workflow_service_pb2.SignalDatasetWorkflowResponse:
        """Signals a dataset."""
        deps = self.deps
        response = datasets_v1_dataset_workflow_service_pb2.SignalDatasetWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SignalDatasetWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'SignalDatasetWorkflow', {'reason': request.reason})
            await deps.repository.save_dataset(request.context.tenant_id, request.dataset)
            response_0 = customers_v1_customer_validation_service_pb2.ExplainCustomerDecisionResponse()
            response_1 = featurestore_v1_feature_value_sync_service_pb2.ResolveFeatureValueConflictResponse()
            response_2 = customers_v1_customer_service_pb2.ListCustomersResponse()
            outgoing_0 = customers_v1_customer_validation_service_pb2.ExplainCustomerDecisionRequest(
                context=request.context,
                customer=customers_v1_customers_pb2.Customer(
                    audit=common_v1_audit_pb2.AuditInfo(created_at=request.dataset.audit.created_at),
                    contact=common_v1_contact_pb2.ContactInfo(email=request.dataset.owner.email),
                    primary_address=common_v1_address_pb2.PostalAddress(
                        country_code=request.dataset.address.country_code,
                        locality=request.dataset.address.locality
                    )
                )
            )
            method_name_0 = 'ExplainCustomerDecision'
            response_0 = await getattr(
                deps.clients.customers_customer_validation,
                method_name_0
            )(outgoing_0, timeout=deps.settings.timeout)
            fields_1: dict[str, Any] = {
                'context': request.context,
                'feature_value': {
                    'measurements': [{'unit': request.dataset.dimensions.unit}],
                    'subject': {'dataset_id': request.dataset_id}
                }
            }
            outgoing_1 = featurestore_v1_feature_value_sync_service_pb2.ResolveFeatureValueConflictRequest(**fields_1)
            response_1 = await deps.clients.featurestore_feature_value_sync.ResolveFeatureValueConflict(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = customers_v1_customer_service_pb2.ListCustomersRequest(
                context=request.context,
                filter=customers_v1_customer_service_pb2.ListCustomersRequest.Filter(
                    created_after=request.dataset.audit.updated_at,
                    owner_id=response_0.customer.relationship_manager.user_id,
                    region=request.dataset.address.region
                )
            )
            document_2 = MessageToDict(outgoing_2, preserving_proto_field_name=True)
            outgoing_2 = ParseDict(document_2, customers_v1_customer_service_pb2.ListCustomersRequest())
            response_2 = await deps.clients.customers_customer.ListCustomers(outgoing_2, timeout=deps.settings.timeout)
            returned_0_0 = response_0.customer.audit.etag
            if returned_0_0:
                response.dataset.audit.etag = returned_0_0
            returned_1_0 = response_1.outcome.next_steps
            response.outcome.next_steps.extend(returned_1_0)
            returned_2_0 = response_2.result.message
            if returned_2_0:
                response.result.message = returned_2_0
            returned_2_1 = response_2.result.message
            if returned_2_1:
                response.outcome.message = returned_2_1
            echoed_0 = request.dataset_id
            response.dataset.dataset_id = echoed_0
            echoed_1 = request.dataset.specs
            response.dataset.specs.update(echoed_1)
            return response

    async def handle_start_dataset_workflow(
        self,
        request: datasets_v1_dataset_workflow_service_pb2.StartDatasetWorkflowRequest
    ) -> datasets_v1_dataset_workflow_service_pb2.StartDatasetWorkflowResponse:
        """Starts a dataset."""
        deps = self.deps
        response = datasets_v1_dataset_workflow_service_pb2.StartDatasetWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('StartDatasetWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'StartDatasetWorkflow', {'reason': request.reason})
            await deps.repository.save_dataset(request.context.tenant_id, request.dataset)
            response_0 = customers_v1_customer_validation_service_pb2.ValidateCustomerResponse()
            response_1 = reviews_v1_product_review_service_pb2.CloneProductReviewResponse()
            response_2 = datasets_v1_data_schema_validation_service_pb2.PreviewDataSchemaResponse()
            response_3 = boxoffice_v1_box_office_sale_calculation_service_pb2.CompareBoxOfficeSaleOptionsResponse()
            outgoing_0 = customers_v1_customer_validation_service_pb2.ValidateCustomerRequest(
                context=request.context,
                customer=customers_v1_customers_pb2.Customer(
                    contact=common_v1_contact_pb2.ContactInfo(email=request.details.notify.email)
                )
            )
            document_0 = MessageToJson(outgoing_0, preserving_proto_field_name=True)
            outgoing_0 = Parse(document_0, customers_v1_customer_validation_service_pb2.ValidateCustomerRequest())
            response_0 = await deps.clients.customers_customer_validation.ValidateCustomer(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = reviews_v1_product_review_service_pb2.CloneProductReviewRequest()
            outgoing_1.context.CopyFrom(request.context)
            outgoing_1.product_review.audit.created_at.CopyFrom(request.dataset.audit.created_at)
            outgoing_1.product_review.audit.created_by = request.dataset.audit.created_by
            outgoing_1.product_review.billing_address.locality = response_0.customer.primary_address.locality
            merged_1 = reviews_v1_product_review_service_pb2.CloneProductReviewRequest()
            merged_1.MergeFrom(outgoing_1)
            outgoing_1.CopyFrom(merged_1)
            response_1 = await deps.clients.reviews_product_review.CloneProductReview(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = datasets_v1_data_schema_validation_service_pb2.PreviewDataSchemaRequest(
                context=request.context,
                data_schema=datasets_v1_datasets_pb2.DataSchema(
                    children=[
                        datasets_v1_datasets_pb2.DataSchema(
                            children=[
                                datasets_v1_datasets_pb2.DataSchema(
                                    audit=common_v1_audit_pb2.AuditInfo(etag=response_0.customer.audit.etag),
                                    manager=identity_v1_refs_pb2.UserRef(
                                        email=response_0.customer.relationship_manager.email
                                    )
                                )
                            ]
                        )
                    ]
                )
            )
            envelope_2 = AnyMessage()
            envelope_2.Pack(outgoing_2)
            outgoing_2 = datasets_v1_data_schema_validation_service_pb2.PreviewDataSchemaRequest()
            if not envelope_2.Unpack(outgoing_2):
                raise ValueError("partner envelope contains the wrong request type")
            response_2 = await deps.clients.datasets_data_schema_validation.PreviewDataSchema(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            outgoing_3 = boxoffice_v1_box_office_sale_calculation_service_pb2.CompareBoxOfficeSaleOptionsRequest(
                box_office_sale=boxoffice_v1_boxoffice_pb2.BoxOfficeSale(
                    audit=common_v1_audit_pb2.AuditInfo(
                        etag=response_1.product_review.audit.etag,
                        updated_at=response_1.product_review.audit.updated_at
                    ),
                    billing_address=common_v1_address_pb2.PostalAddress(
                        lines=list(request.dataset.address.lines),
                        locality=response_2.data_schema.location.locality
                    )
                ),
                context=request.context
            )
            registered_3 = cast(
                boxoffice_v1_box_office_sale_calculation_service_pb2_grpc.BoxOfficeSaleCalculationServiceStub,
                deps.clients.registry['acme.boxoffice.v1.BoxOfficeSaleCalculationService']
            )
            response_3 = await registered_3.CompareBoxOfficeSaleOptions(outgoing_3, timeout=deps.settings.timeout)
            returned_0_0 = response_0.outcome.effective_at
            if returned_0_0.ListFields():
                response.outcome.effective_at.MergeFrom(returned_0_0)
            returned_1_0 = response_1.product_review.audit.updated_by
            if returned_1_0:
                response.dataset.audit.updated_by = returned_1_0
            returned_1_1 = response_1.result.correlation_id
            if returned_1_1:
                response.result.correlation_id = returned_1_1
            returned_2_0 = response_2.data_schema.audit.created_by
            if returned_2_0:
                response.dataset.audit.created_by = returned_2_0
            returned_3_0 = response_3.result.message
            if returned_3_0:
                response.result.message = returned_3_0
            echoed_0 = request.dataset_id
            response.dataset.dataset_id = echoed_0
            echoed_1 = request.dataset.code
            response.dataset.code = echoed_1
            return response
