"""Routes data schemas through approval, with escalation and delegation."""

from __future__ import annotations

from collections.abc import AsyncIterator
from functools import partial
from typing import Any
from typing import cast
import asyncio
import logging

from google.protobuf.any_pb2 import Any as AnyMessage
from google.protobuf.json_format import MessageToDict
from google.protobuf.json_format import ParseDict
import grpc

from acme.authorization.v1 import access_policy_service_pb2 as authorization_v1_access_policy_service_pb2
from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.customers.v1 import (
    consent_record_calculation_service_pb2 as customers_v1_consent_record_calculation_service_pb2,
)
from acme.customers.v1 import customer_query_service_pb2 as customers_v1_customer_query_service_pb2
from acme.customers.v1 import customers_pb2 as customers_v1_customers_pb2
from acme.customers.v1 import household_calculation_service_pb2 as customers_v1_household_calculation_service_pb2
from acme.customers.v1 import household_query_service_pb2 as customers_v1_household_query_service_pb2
from acme.customers.v1 import preference_calculation_service_pb2 as customers_v1_preference_calculation_service_pb2
from acme.customers.v1 import preference_validation_service_pb2 as customers_v1_preference_validation_service_pb2
from acme.customers.v1 import refs_pb2 as customers_v1_refs_pb2
from acme.datasets.v1 import data_schema_approval_service_pb2 as datasets_v1_data_schema_approval_service_pb2
from acme.datasets.v1 import data_schema_approval_service_pb2_grpc as datasets_v1_data_schema_approval_service_pb2_grpc
from acme.datasets.v1 import data_schema_calculation_service_pb2 as datasets_v1_data_schema_calculation_service_pb2
from acme.datasets.v1 import dataset_approval_service_pb2 as datasets_v1_dataset_approval_service_pb2
from acme.datasets.v1 import dataset_query_service_pb2 as datasets_v1_dataset_query_service_pb2
from acme.datasets.v1 import dataset_service_pb2 as datasets_v1_dataset_service_pb2
from acme.datasets.v1 import dataset_service_pb2_grpc as datasets_v1_dataset_service_pb2_grpc
from acme.datasets.v1 import dataset_validation_service_pb2 as datasets_v1_dataset_validation_service_pb2
from acme.datasets.v1 import dataset_version_approval_service_pb2 as datasets_v1_dataset_version_approval_service_pb2
from acme.datasets.v1 import (
    dataset_version_validation_service_pb2 as datasets_v1_dataset_version_validation_service_pb2,
)
from acme.datasets.v1 import (
    dataset_version_validation_service_pb2_grpc as datasets_v1_dataset_version_validation_service_pb2_grpc,
)
from acme.datasets.v1 import dataset_workflow_service_pb2 as datasets_v1_dataset_workflow_service_pb2
from acme.datasets.v1 import datasets_pb2 as datasets_v1_datasets_pb2
from acme.documents.v1 import document_query_service_pb2 as documents_v1_document_query_service_pb2
from acme.featurestore.v1 import feature_value_import_service_pb2 as featurestore_v1_feature_value_import_service_pb2
from acme.featurestore.v1 import featurestore_pb2 as featurestore_v1_featurestore_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.identity.v1 import user_service_pb2 as identity_v1_user_service_pb2
from acme.labeling.v1 import label_set_sync_service_pb2 as labeling_v1_label_set_sync_service_pb2
from acme.labeling.v1 import labeling_pb2 as labeling_v1_labeling_pb2
from acme.lineage.v1 import lineage_edge_reporting_service_pb2 as lineage_v1_lineage_edge_reporting_service_pb2
from acme.metrics.v1 import dashboard_validation_service_pb2 as metrics_v1_dashboard_validation_service_pb2
from acme.metrics.v1 import metrics_pb2 as metrics_v1_metrics_pb2
from acme.modelregistry.v1 import deployment_workflow_service_pb2 as modelregistry_v1_deployment_workflow_service_pb2
from acme.modelregistry.v1 import modelregistry_pb2 as modelregistry_v1_modelregistry_pb2
from acme.venues.v1 import venue_query_service_pb2 as venues_v1_venue_query_service_pb2

from acme_data.domains.datasets.adapters import DataSchemaApprovalDelegateDataSchemaApproval0Adapter
from acme_data.domains.datasets.adapters import DataSchemaApprovalDelegateDataSchemaApproval0Port
from acme_data.domains.datasets.adapters import DataSchemaApprovalDelegateDataSchemaApproval2Adapter
from acme_data.domains.datasets.adapters import DataSchemaApprovalRejectDataSchema3Adapter
from acme_data.domains.datasets.adapters import DataSchemaApprovalRejectDataSchema3Port
from acme_data.domains.datasets.adapters import DataSchemaApprovalSubmitDataSchema1Adapter
from acme_data.domains.datasets.dependencies import Dependencies
from acme_data.domains.datasets.models import DataSchemaApprovalApproveDataSchema3Command
from acme_data.domains.datasets.models import DataSchemaApprovalRecallDataSchema1Command
from acme_data.domains.datasets.models import DataSchemaApprovalRecallDataSchema2Command
from acme_data.domains.datasets.models import to_data_schema_approval_approve_data_schema3_command
from acme_data.domains.datasets.models import to_data_schema_approval_recall_data_schema1_command
from acme_data.domains.datasets.models import to_data_schema_approval_recall_data_schema2_command
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import run_steps
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class DataSchemaApprovalServicer(datasets_v1_data_schema_approval_service_pb2_grpc.DataSchemaApprovalServiceServicer):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    async def ApproveDataSchema(
        self, request: datasets_v1_data_schema_approval_service_pb2.ApproveDataSchemaRequest, context: grpc.aio.ServicerContext,
    ) -> datasets_v1_data_schema_approval_service_pb2.ApproveDataSchemaResponse:
        """Approves a data schema."""
        return await self.handle_approve_data_schema(request)

    @rpc_errors
    async def CommentDataSchemaApproval(
        self, request: datasets_v1_data_schema_approval_service_pb2.CommentDataSchemaApprovalRequest, context: grpc.aio.ServicerContext,
    ) -> datasets_v1_data_schema_approval_service_pb2.CommentDataSchemaApprovalResponse:
        """Comments a data schema."""
        return await self.handle_comment_data_schema_approval(request)

    @rpc_errors
    async def DelegateDataSchemaApproval(
        self, request: datasets_v1_data_schema_approval_service_pb2.DelegateDataSchemaApprovalRequest, context: grpc.aio.ServicerContext,
    ) -> datasets_v1_data_schema_approval_service_pb2.DelegateDataSchemaApprovalResponse:
        """Delegates a data schema."""
        return await self.handle_delegate_data_schema_approval(request)

    @rpc_errors
    async def EscalateDataSchema(
        self, request: datasets_v1_data_schema_approval_service_pb2.EscalateDataSchemaRequest, context: grpc.aio.ServicerContext,
    ) -> datasets_v1_data_schema_approval_service_pb2.EscalateDataSchemaResponse:
        """Escalates a data schema."""
        return await self.handle_escalate_data_schema(request)

    @rpc_errors
    @retry_transient
    async def GetDataSchemaApprovalStatus(
        self, request: datasets_v1_data_schema_approval_service_pb2.GetDataSchemaApprovalStatusRequest, context: grpc.aio.ServicerContext,
    ) -> datasets_v1_data_schema_approval_service_pb2.GetDataSchemaApprovalStatusResponse:
        """Returns a data schema."""
        return await self.handle_get_data_schema_approval_status(request)

    @rpc_errors
    @retry_transient
    async def ListPendingDataSchemas(
        self, request: datasets_v1_data_schema_approval_service_pb2.ListPendingDataSchemasRequest, context: grpc.aio.ServicerContext,
    ) -> datasets_v1_data_schema_approval_service_pb2.ListPendingDataSchemasResponse:
        """Lists data schemas a page at a time."""
        return await self.handle_list_pending_data_schemas(request)

    @rpc_errors
    async def RecallDataSchema(
        self, request: datasets_v1_data_schema_approval_service_pb2.RecallDataSchemaRequest, context: grpc.aio.ServicerContext,
    ) -> datasets_v1_data_schema_approval_service_pb2.RecallDataSchemaResponse:
        """Recalls a data schema."""
        return await self.handle_recall_data_schema(request)

    @rpc_errors
    async def RejectDataSchema(
        self, request: datasets_v1_data_schema_approval_service_pb2.RejectDataSchemaRequest, context: grpc.aio.ServicerContext,
    ) -> datasets_v1_data_schema_approval_service_pb2.RejectDataSchemaResponse:
        """Rejects a data schema."""
        return await self.handle_reject_data_schema(request)

    @rpc_errors
    async def SubmitDataSchema(
        self, request: datasets_v1_data_schema_approval_service_pb2.SubmitDataSchemaRequest, context: grpc.aio.ServicerContext,
    ) -> datasets_v1_data_schema_approval_service_pb2.SubmitDataSchemaResponse:
        """Submits a data schema."""
        return await self.handle_submit_data_schema(request)

    async def handle_approve_data_schema(
        self,
        request: datasets_v1_data_schema_approval_service_pb2.ApproveDataSchemaRequest
    ) -> datasets_v1_data_schema_approval_service_pb2.ApproveDataSchemaResponse:
        """Approves a data schema."""
        deps = self.deps
        response = datasets_v1_data_schema_approval_service_pb2.ApproveDataSchemaResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ApproveDataSchema', extra={'fields': {'name': request.data_schema.name}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ApproveDataSchema',
                {'name': request.data_schema.name}
            )
            await deps.repository.save_data_schema(request.context.tenant_id, request.data_schema)
            response_0 = datasets_v1_dataset_version_approval_service_pb2.ListPendingDatasetVersionsResponse()
            response_1 = datasets_v1_data_schema_calculation_service_pb2.GetDataSchemaRatesResponse()
            response_2 = datasets_v1_dataset_version_validation_service_pb2.ExplainDatasetVersionDecisionResponse()
            response_3 = venues_v1_venue_query_service_pb2.SummarizeVenuesResponse()
            outgoing_0 = datasets_v1_dataset_version_approval_service_pb2.ListPendingDatasetVersionsRequest()
            outgoing_0.context.CopyFrom(request.context)
            outgoing_0.filter.region = request.data_schema.location.region
            merged_0 = datasets_v1_dataset_version_approval_service_pb2.ListPendingDatasetVersionsRequest()
            merged_0.MergeFrom(outgoing_0)
            outgoing_0.CopyFrom(merged_0)
            response_0 = await deps.clients.datasets_dataset_version_approval.ListPendingDatasetVersions(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = datasets_v1_data_schema_calculation_service_pb2.GetDataSchemaRatesRequest(
                context=request.context,
                data_schema_id=request.data_schema.data_schema_id
            )
            envelope_1 = AnyMessage()
            envelope_1.Pack(outgoing_1)
            outgoing_1 = datasets_v1_data_schema_calculation_service_pb2.GetDataSchemaRatesRequest()
            if not envelope_1.Unpack(outgoing_1):
                raise ValueError("partner envelope contains the wrong request type")
            response_1 = await deps.clients.datasets_data_schema_calculation.GetDataSchemaRates(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = datasets_v1_dataset_version_validation_service_pb2.ExplainDatasetVersionDecisionRequest(
                context=request.context,
                dataset_version=datasets_v1_datasets_pb2.DatasetVersion(
                    subject=customers_v1_refs_pb2.CustomerRef(
                        display_name=request.details.approver.display_name,
                        email=response_1.data_schema.manager.email
                    )
                ),
                details=datasets_v1_dataset_version_validation_service_pb2.ExplainDatasetVersionDecisionRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(email=request.data_schema.manager.email)
                )
            )
            registered_2 = cast(
                datasets_v1_dataset_version_validation_service_pb2_grpc.DatasetVersionValidationServiceStub,
                deps.clients.registry['acme.datasets.v1.DatasetVersionValidationService']
            )
            response_2 = await registered_2.ExplainDatasetVersionDecision(outgoing_2, timeout=deps.settings.timeout)
            command_3 = DataSchemaApprovalApproveDataSchema3Command(
                context=request.context,
                reason=request.reason,
                annotations=dict(request.annotations)
            )
            outgoing_3 = to_data_schema_approval_approve_data_schema3_command(command_3)
            response_3 = await deps.clients.venues_venue_query.SummarizeVenues(
                outgoing_3,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_0)
            returned_1_0 = response_1.data_schema.manager
            returned_1_0_part_1 = response.data_schema.children.add()
            returned_1_0_part_2 = returned_1_0_part_1.children.add()
            returned_1_0_part_3 = returned_1_0_part_2.children.add()
            if returned_1_0.ListFields():
                returned_1_0_part_3.manager.MergeFrom(returned_1_0)
            returned_1_1 = response_1.data_schema.manager.display_name
            returned_1_1_part_1 = response.data_schema.children.add()
            if returned_1_1:
                returned_1_1_part_1.manager.display_name = returned_1_1
            returned_2_0 = response_2.dataset_version.subject.display_name
            returned_2_0_part_1 = response.data_schema.children.add()
            if returned_2_0:
                returned_2_0_part_1.manager.display_name = returned_2_0
            returned_3_0 = response_3.result.message
            if returned_3_0:
                response.result.message = returned_3_0
            returned_3_1 = response_3.result.details
            response.result.details.update(returned_3_1)
            echoed_0 = request.data_schema_id
            response.data_schema.data_schema_id = echoed_0
            echoed_1 = request.data_schema.depth
            response.data_schema.depth = echoed_1
            return response

    async def handle_comment_data_schema_approval(
        self,
        request: datasets_v1_data_schema_approval_service_pb2.CommentDataSchemaApprovalRequest
    ) -> datasets_v1_data_schema_approval_service_pb2.CommentDataSchemaApprovalResponse:
        """Comments a data schema."""
        deps = self.deps
        response = datasets_v1_data_schema_approval_service_pb2.CommentDataSchemaApprovalResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CommentDataSchemaApproval', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'CommentDataSchemaApproval',
                {'reason': request.reason}
            )
            await deps.repository.save_data_schema(request.context.tenant_id, request.data_schema)
            response_0 = documents_v1_document_query_service_pb2.CountDocumentsResponse()
            response_1 = documents_v1_document_query_service_pb2.SuggestDocumentsResponse()
            response_2 = datasets_v1_dataset_version_validation_service_pb2.ScoreDatasetVersionResponse()
            response_3 = customers_v1_household_calculation_service_pb2.SimulateHouseholdResponse()
            outgoing_0 = documents_v1_document_query_service_pb2.CountDocumentsRequest(
                context=request.context,
                filter=documents_v1_document_query_service_pb2.CountDocumentsRequest.Filter(
                    created_after=request.data_schema.audit.updated_at,
                    region=request.data_schema.location.region
                )
            )
            outgoing_1 = documents_v1_document_query_service_pb2.SuggestDocumentsRequest(
                context=request.context,
                filter=documents_v1_document_query_service_pb2.SuggestDocumentsRequest.Filter(
                    created_after=request.details.effective_at,
                    owner_id=request.data_schema.parent_id,
                    region=request.data_schema.location.region
                )
            )
            outgoing_2 = datasets_v1_dataset_version_validation_service_pb2.ScoreDatasetVersionRequest(
                context=request.context,
                dataset_version=datasets_v1_datasets_pb2.DatasetVersion(
                    subject=customers_v1_refs_pb2.CustomerRef(email=request.data_schema.manager.email)
                ),
                details=datasets_v1_dataset_version_validation_service_pb2.ScoreDatasetVersionRequest.Details(
                    destination=common_v1_address_pb2.PostalAddress(
                        country_code=request.data_schema.location.country_code,
                        locality=request.data_schema.location.locality,
                        region=request.data_schema.location.region
                    )
                )
            )
            outgoing_3 = customers_v1_household_calculation_service_pb2.SimulateHouseholdRequest(
                context=request.context,
                household=customers_v1_customers_pb2.Household(
                    children=[
                        customers_v1_customers_pb2.Household(
                            children=[
                                customers_v1_customers_pb2.Household(
                                    location=common_v1_address_pb2.PostalAddress(
                                        recipient=request.data_schema.location.recipient,
                                        region=request.data_schema.location.region
                                    ),
                                    manager=identity_v1_refs_pb2.UserRef(email=request.data_schema.manager.email)
                                )
                            ]
                        )
                    ]
                )
            )
            response_0, response_1, response_2, response_3 = await asyncio.gather(
                deps.clients.documents_document_query.CountDocuments(outgoing_0, timeout=deps.settings.timeout),
                deps.clients.documents_document_query.SuggestDocuments(outgoing_1, timeout=deps.settings.timeout),
                deps.clients.datasets_dataset_version_validation.ScoreDatasetVersion(
                    outgoing_2,
                    timeout=deps.settings.timeout
                ),
                deps.clients.customers_household_calculation.SimulateHousehold(
                    outgoing_3,
                    timeout=deps.settings.timeout
                ),
            )
            returned_0_0 = response_0.result.status
            if returned_0_0:
                response.result.status = returned_0_0
            returned_1_0 = response_1.result.correlation_id
            if returned_1_0:
                response.result.correlation_id = returned_1_0
            returned_1_1 = response_1.result.message
            if returned_1_1:
                response.result.message = returned_1_1
            returned_2_0 = response_2.result.correlation_id
            if returned_2_0:
                response.result.correlation_id = returned_2_0
            returned_2_1 = response_2.dataset_version.attributes
            returned_2_1_part_1 = response.data_schema.children.add()
            returned_2_1_part_1.attributes.update(returned_2_1)
            returned_3_0 = response_3.household.manager.display_name
            returned_3_0_part_1 = response.data_schema.children.add()
            returned_3_0_part_2 = returned_3_0_part_1.children.add()
            if returned_3_0:
                returned_3_0_part_2.manager.display_name = returned_3_0
            echoed_0 = request.data_schema_id
            response.data_schema.data_schema_id = echoed_0
            echoed_1 = request.data_schema.parent_id
            response.data_schema.parent_id = echoed_1
            return response

    async def handle_delegate_data_schema_approval(
        self,
        request: datasets_v1_data_schema_approval_service_pb2.DelegateDataSchemaApprovalRequest
    ) -> datasets_v1_data_schema_approval_service_pb2.DelegateDataSchemaApprovalResponse:
        """Delegates a data schema."""
        deps = self.deps
        response = datasets_v1_data_schema_approval_service_pb2.DelegateDataSchemaApprovalResponse()
        with tenant_scope(request.context.tenant_id):
            log.info(
                'DelegateDataSchemaApproval',
                extra={'fields': {'data_schema_id': request.data_schema.data_schema_id}}
            )
            await deps.repository.audit(
                request.context.tenant_id,
                'DelegateDataSchemaApproval',
                {'data_schema_id': request.data_schema.data_schema_id}
            )
            await deps.repository.save_data_schema(request.context.tenant_id, request.data_schema)
            response_0 = datasets_v1_dataset_query_service_pb2.SummarizeDatasetsResponse()
            response_1 = customers_v1_consent_record_calculation_service_pb2.EstimateConsentRecordResponse()
            response_2 = labeling_v1_label_set_sync_service_pb2.SyncLabelSetsResponse()
            response_3 = datasets_v1_dataset_validation_service_pb2.CheckDatasetEligibilityResponse()
            outgoing_0 = datasets_v1_dataset_query_service_pb2.SummarizeDatasetsRequest(
                annotations=dict(request.annotations),
                context=request.context,
                reason=request.reason
            )
            port_0: DataSchemaApprovalDelegateDataSchemaApproval0Port = DataSchemaApprovalDelegateDataSchemaApproval0Adapter(
                deps.clients.datasets_dataset_query,
                deps.settings.timeout
            )
            response_0 = await port_0.execute(outgoing_0)
            outgoing_1 = customers_v1_consent_record_calculation_service_pb2.EstimateConsentRecordRequest(
                context=request.context,
                details=customers_v1_consent_record_calculation_service_pb2.EstimateConsentRecordRequest.Details(
                    destination=common_v1_address_pb2.PostalAddress(
                        locality=request.data_schema.location.locality,
                        recipient=request.data_schema.location.recipient
                    )
                )
            )
            steps_1 = [
                partial(
                    deps.clients.customers_consent_record_calculation.EstimateConsentRecord,
                    outgoing_1,
                    timeout=deps.settings.timeout
                )
            ]
            results_1 = await run_steps(steps_1)
            response_1 = results_1[-1]
            outgoing_2 = labeling_v1_label_set_sync_service_pb2.SyncLabelSetsRequest(
                context=request.context,
                label_set=labeling_v1_labeling_pb2.LabelSet(
                    children=[
                        labeling_v1_labeling_pb2.LabelSet(
                            children=[
                                labeling_v1_labeling_pb2.LabelSet(
                                    audit=common_v1_audit_pb2.AuditInfo(
                                        updated_at=request.data_schema.audit.updated_at
                                    ),
                                    children=[
                                        labeling_v1_labeling_pb2.LabelSet(
                                            attributes=dict(request.data_schema.attributes)
                                        )
                                    ],
                                    location=common_v1_address_pb2.PostalAddress(
                                        country_code=request.data_schema.location.country_code
                                    ),
                                    manager=identity_v1_refs_pb2.UserRef(
                                        display_name=request.data_schema.manager.display_name
                                    )
                                )
                            ]
                        )
                    ]
                )
            )
            response_2 = await DataSchemaApprovalDelegateDataSchemaApproval2Adapter(
                deps.clients.labeling_label_set_sync,
                deps.settings.timeout
            )(outgoing_2)
            outgoing_3 = datasets_v1_dataset_validation_service_pb2.CheckDatasetEligibilityRequest(
                context=request.context,
                dataset=datasets_v1_datasets_pb2.Dataset(
                    owner=identity_v1_refs_pb2.UserRef(display_name=response_1.consent_record.subject.display_name)
                ),
                details=datasets_v1_dataset_validation_service_pb2.CheckDatasetEligibilityRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(email=request.details.approver.email)
                )
            )
            response_3 = cast(datasets_v1_dataset_validation_service_pb2.CheckDatasetEligibilityResponse, await deps.bus.request(
                'acme.datasets.v1.DataSchemaApprovalService/DelegateDataSchemaApproval/3', outgoing_3, deps.settings.timeout,
            ))
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.result.message = returned_0_0
            returned_0_1 = response_0.result.details
            response.result.details.update(returned_0_1)
            returned_1_0 = response_1.result.message
            if returned_1_0:
                response.result.message = returned_1_0
            returned_2_0 = response_2.label_set.name
            returned_2_0_part_1 = response.data_schema.children.add()
            returned_2_0_part_2 = returned_2_0_part_1.children.add()
            returned_2_0_part_3 = returned_2_0_part_2.children.add()
            if returned_2_0:
                returned_2_0_part_3.name = returned_2_0
            returned_2_1 = response_2.label_set.manager
            returned_2_1_part_1 = response.data_schema.children.add()
            returned_2_1_part_2 = returned_2_1_part_1.children.add()
            returned_2_1_part_3 = returned_2_1_part_2.children.add()
            if returned_2_1.ListFields():
                returned_2_1_part_3.manager.MergeFrom(returned_2_1)
            returned_3_0 = response_3.dataset.address.postal_code
            returned_3_0_part_1 = response.data_schema.children.add()
            if returned_3_0:
                returned_3_0_part_1.location.postal_code = returned_3_0
            echoed_0 = request.data_schema_id
            response.data_schema.data_schema_id = echoed_0
            echoed_1 = request.data_schema.status
            response.data_schema.status = echoed_1
            return response

    async def handle_escalate_data_schema(
        self,
        request: datasets_v1_data_schema_approval_service_pb2.EscalateDataSchemaRequest
    ) -> datasets_v1_data_schema_approval_service_pb2.EscalateDataSchemaResponse:
        """Escalates a data schema."""
        deps = self.deps
        response = datasets_v1_data_schema_approval_service_pb2.EscalateDataSchemaResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('EscalateDataSchema', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'EscalateDataSchema', {'reason': request.reason})
            await deps.repository.save_data_schema(request.context.tenant_id, request.data_schema)
            response_0 = identity_v1_user_service_pb2.GetUserResponse()
            response_1 = customers_v1_preference_validation_service_pb2.CheckPreferenceEligibilityResponse()
            response_2 = authorization_v1_access_policy_service_pb2.UpdateAccessPolicyResponse()
            response_3 = modelregistry_v1_deployment_workflow_service_pb2.CancelDeploymentWorkflowResponse()
            outgoing_0 = identity_v1_user_service_pb2.GetUserRequest(
                context=request.context,
                user_id=request.data_schema.manager.user_id
            )
            response_0 = await deps.clients.identity_user.GetUser(outgoing_0, timeout=deps.settings.timeout)
            outgoing_1 = customers_v1_preference_validation_service_pb2.CheckPreferenceEligibilityRequest(
                context=request.context,
                details=customers_v1_preference_validation_service_pb2.CheckPreferenceEligibilityRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(email=response_0.user.relationship_manager.email)
                ),
                preference=customers_v1_customers_pb2.Preference(
                    audit=common_v1_audit_pb2.AuditInfo(updated_by=request.data_schema.audit.updated_by),
                    owner=identity_v1_refs_pb2.UserRef(user_id=request.details.approver.user_id)
                )
            )
            method_name_1 = 'CheckPreferenceEligibility'
            response_1 = await getattr(
                deps.clients.customers_preference_validation,
                method_name_1
            )(outgoing_1, timeout=deps.settings.timeout)
            fields_2: dict[str, Any] = {
                'access_policy': {
                    'audit': {
                        'created_at': request.data_schema.audit.created_at,
                        'updated_at': response_0.user.audit.updated_at
                    },
                    'owner': {
                        'display_name': response_1.preference.owner.display_name,
                        'email': request.data_schema.manager.email
                    }
                },
                'context': request.context
            }
            outgoing_2 = authorization_v1_access_policy_service_pb2.UpdateAccessPolicyRequest(**fields_2)
            response_2 = await deps.clients.authorization_access_policy.UpdateAccessPolicy(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            outgoing_3 = modelregistry_v1_deployment_workflow_service_pb2.CancelDeploymentWorkflowRequest(
                context=request.context,
                deployment=modelregistry_v1_modelregistry_pb2.Deployment(
                    participants=[
                        modelregistry_v1_modelregistry_pb2.DeploymentParticipant(
                            contact=common_v1_contact_pb2.ContactInfo(
                                preferred_channel=response_0.user.contact.preferred_channel
                            )
                        )
                    ]
                )
            )
            document_3 = MessageToDict(outgoing_3, preserving_proto_field_name=True)
            outgoing_3 = ParseDict(
                document_3,
                modelregistry_v1_deployment_workflow_service_pb2.CancelDeploymentWorkflowRequest()
            )
            response_3 = await deps.clients.modelregistry_deployment_workflow.CancelDeploymentWorkflow(
                outgoing_3,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.user.contact.email
            if returned_0_0:
                response.data_schema.manager.email = returned_0_0
            returned_1_0 = response_1.preference.audit.created_by
            returned_1_0_part_1 = response.data_schema.children.add()
            returned_1_0_part_2 = returned_1_0_part_1.children.add()
            if returned_1_0:
                returned_1_0_part_2.audit.created_by = returned_1_0
            returned_1_1 = response_1.preference.owner.display_name
            returned_1_1_part_1 = response.data_schema.children.add()
            returned_1_1_part_2 = returned_1_1_part_1.children.add()
            if returned_1_1:
                returned_1_1_part_2.manager.display_name = returned_1_1
            returned_2_0 = response_2.access_policy.owner.display_name
            returned_2_0_part_1 = response.data_schema.children.add()
            returned_2_0_part_2 = returned_2_0_part_1.children.add()
            if returned_2_0:
                returned_2_0_part_2.manager.display_name = returned_2_0
            returned_3_0 = response_3.deployment.location.region
            if returned_3_0:
                response.data_schema.location.region = returned_3_0
            returned_3_1 = response_3.deployment.audit.created_at
            if returned_3_1.ListFields():
                response.data_schema.audit.created_at.MergeFrom(returned_3_1)
            echoed_0 = request.data_schema_id
            response.data_schema.data_schema_id = echoed_0
            echoed_1 = request.data_schema.name
            response.data_schema.name = echoed_1
            return response

    async def handle_get_data_schema_approval_status(
        self,
        request: datasets_v1_data_schema_approval_service_pb2.GetDataSchemaApprovalStatusRequest
    ) -> datasets_v1_data_schema_approval_service_pb2.GetDataSchemaApprovalStatusResponse:
        """Returns a data schema."""
        deps = self.deps
        response = datasets_v1_data_schema_approval_service_pb2.GetDataSchemaApprovalStatusResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('GetDataSchemaApprovalStatus', extra={'fields': {'domain': 'datasets'}})
            await deps.repository.audit(request.context.tenant_id, 'GetDataSchemaApprovalStatus', {})
            response_0 = featurestore_v1_feature_value_import_service_pb2.ValidateFeatureValueImportResponse()
            response_1 = lineage_v1_lineage_edge_reporting_service_pb2.ShareLineageEdgeReportResponse()
            outgoing_0 = featurestore_v1_feature_value_import_service_pb2.ValidateFeatureValueImportRequest(
                context=request.context,
                details=featurestore_v1_feature_value_import_service_pb2.ValidateFeatureValueImportRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(email=request.context.actor.email),
                    locale=request.context.locale
                ),
                feature_value=featurestore_v1_featurestore_pb2.FeatureValue(
                    correlation_id=request.data_schema_id,
                    occurred_at=request.context.deadline
                )
            )
            response_0 = await deps.clients.featurestore_feature_value_import.ValidateFeatureValueImport(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = lineage_v1_lineage_edge_reporting_service_pb2.ShareLineageEdgeReportRequest()
            outgoing_1.context.CopyFrom(request.context)
            outgoing_1.details.recipient.email = request.context.actor.email
            merged_1 = lineage_v1_lineage_edge_reporting_service_pb2.ShareLineageEdgeReportRequest()
            merged_1.MergeFrom(outgoing_1)
            outgoing_1.CopyFrom(merged_1)
            response_1 = await deps.clients.lineage_lineage_edge_reporting.ShareLineageEdgeReport(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.feature_value.subject.display_name
            returned_0_0_part_1 = response.data_schema.children.add()
            if returned_0_0:
                returned_0_0_part_1.manager.display_name = returned_0_0
            returned_1_0 = response_1.lineage_edge.correlation_id
            if returned_1_0:
                response.result.correlation_id = returned_1_0
            returned_1_1 = response_1.lineage_edge.attributes
            returned_1_1_part_1 = response.data_schema.children.add()
            returned_1_1_part_2 = returned_1_1_part_1.children.add()
            returned_1_1_part_2.attributes.update(returned_1_1)
            echoed_0 = request.data_schema_id
            response.data_schema.data_schema_id = echoed_0
            return response

    async def handle_list_pending_data_schemas(
        self,
        request: datasets_v1_data_schema_approval_service_pb2.ListPendingDataSchemasRequest
    ) -> datasets_v1_data_schema_approval_service_pb2.ListPendingDataSchemasResponse:
        """Lists data schemas a page at a time."""
        deps = self.deps
        response = datasets_v1_data_schema_approval_service_pb2.ListPendingDataSchemasResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ListPendingDataSchemas', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ListPendingDataSchemas',
                {'order_by': request.order_by}
            )
            response_0 = datasets_v1_dataset_validation_service_pb2.PreviewDatasetResponse()
            outgoing_0 = datasets_v1_dataset_validation_service_pb2.PreviewDatasetRequest(
                context=request.context,
                dataset=datasets_v1_datasets_pb2.Dataset(
                    address=common_v1_address_pb2.PostalAddress(region=request.filter.region)
                )
            )
            response_0 = await deps.clients.datasets_dataset_validation.PreviewDataset(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.outcome.message
            if returned_0_0:
                response.result.message = returned_0_0
            returned_0_1 = response_0.dataset.owner.user_id
            returned_0_1_part_0 = response.data_schemas.add()
            returned_0_1_part_1 = returned_0_1_part_0.children.add()
            returned_0_1_part_2 = returned_0_1_part_1.children.add()
            if returned_0_1:
                returned_0_1_part_2.manager.user_id = returned_0_1
            return response

    async def handle_recall_data_schema(
        self,
        request: datasets_v1_data_schema_approval_service_pb2.RecallDataSchemaRequest
    ) -> datasets_v1_data_schema_approval_service_pb2.RecallDataSchemaResponse:
        """Recalls a data schema."""
        deps = self.deps
        response = datasets_v1_data_schema_approval_service_pb2.RecallDataSchemaResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('RecallDataSchema', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'RecallDataSchema', {'reason': request.reason})
            await deps.repository.save_data_schema(request.context.tenant_id, request.data_schema)
            response_0 = datasets_v1_dataset_service_pb2.CreateDatasetResponse()
            response_1 = customers_v1_customer_query_service_pb2.ResolveCustomersResponse()
            response_2 = documents_v1_document_query_service_pb2.BrowseDocumentsResponse()
            outgoing_0 = datasets_v1_dataset_service_pb2.CreateDatasetRequest(
                context=request.context,
                dataset=datasets_v1_datasets_pb2.Dataset(
                    address=common_v1_address_pb2.PostalAddress(
                        recipient=request.data_schema.location.recipient,
                        region=request.data_schema.location.region
                    )
                )
            )
            registered_0 = cast(
                datasets_v1_dataset_service_pb2_grpc.DatasetServiceStub,
                deps.clients.registry['acme.datasets.v1.DatasetService']
            )
            response_0 = await registered_0.CreateDataset(outgoing_0, timeout=deps.settings.timeout)
            command_1 = DataSchemaApprovalRecallDataSchema1Command(context=request.context)
            outgoing_1 = to_data_schema_approval_recall_data_schema1_command(command_1)
            response_1 = await deps.clients.customers_customer_query.ResolveCustomers(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            command_2 = DataSchemaApprovalRecallDataSchema2Command.model_validate(
                {
                    'context': request.context,
                    'filter_region': response_0.dataset.address.region,
                    'filter_created_after': request.details.effective_at,
                    'filter_labels': dict(response_1.result.details),
                    'filter_owner_id': response_1.result.correlation_id
                }
            )
            outgoing_2 = to_data_schema_approval_recall_data_schema2_command(command_2)
            response_2 = await deps.clients.documents_document_query.BrowseDocuments(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.dataset.owner.display_name
            if returned_0_0:
                response.data_schema.manager.display_name = returned_0_0
            returned_1_0 = response_1.result.reference_ids
            response.result.reference_ids.extend(returned_1_0)
            returned_2_0 = response_2.result.status
            if returned_2_0:
                response.outcome.status = returned_2_0
            echoed_0 = request.data_schema_id
            response.data_schema.data_schema_id = echoed_0
            echoed_1 = request.data_schema.name
            response.data_schema.name = echoed_1
            return response

    async def handle_reject_data_schema(
        self,
        request: datasets_v1_data_schema_approval_service_pb2.RejectDataSchemaRequest
    ) -> datasets_v1_data_schema_approval_service_pb2.RejectDataSchemaResponse:
        """Rejects a data schema."""
        deps = self.deps
        response = datasets_v1_data_schema_approval_service_pb2.RejectDataSchemaResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('RejectDataSchema', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'RejectDataSchema', {'reason': request.reason})
            await deps.repository.save_data_schema(request.context.tenant_id, request.data_schema)
            response_0 = datasets_v1_dataset_workflow_service_pb2.StartDatasetWorkflowResponse()
            response_1 = customers_v1_household_query_service_pb2.CountHouseholdsResponse()
            response_2 = metrics_v1_dashboard_validation_service_pb2.ScoreDashboardResponse()
            response_3 = datasets_v1_dataset_approval_service_pb2.CommentDatasetApprovalResponse()
            outgoing_0 = datasets_v1_dataset_workflow_service_pb2.StartDatasetWorkflowRequest(
                context=request.context,
                dataset=datasets_v1_datasets_pb2.Dataset(
                    owner=identity_v1_refs_pb2.UserRef(email=request.data_schema.manager.email)
                )
            )
            outgoing_1 = customers_v1_household_query_service_pb2.CountHouseholdsRequest(
                context=request.context,
                filter=customers_v1_household_query_service_pb2.CountHouseholdsRequest.Filter(
                    created_after=request.data_schema.audit.created_at,
                    region=request.data_schema.location.region
                )
            )
            outgoing_2 = metrics_v1_dashboard_validation_service_pb2.ScoreDashboardRequest(
                context=request.context,
                dashboard=metrics_v1_metrics_pb2.Dashboard(
                    billing_address=common_v1_address_pb2.PostalAddress(lines=list(request.data_schema.location.lines))
                ),
                details=metrics_v1_dashboard_validation_service_pb2.ScoreDashboardRequest.Details(
                    destination=common_v1_address_pb2.PostalAddress(
                        postal_code=request.data_schema.location.postal_code
                    )
                )
            )
            response_0, response_1, response_2 = await asyncio.gather(
                deps.clients.datasets_dataset_workflow.StartDatasetWorkflow(outgoing_0, timeout=deps.settings.timeout),
                deps.clients.customers_household_query.CountHouseholds(outgoing_1, timeout=deps.settings.timeout),
                deps.clients.metrics_dashboard_validation.ScoreDashboard(outgoing_2, timeout=deps.settings.timeout),
            )
            outgoing_3 = datasets_v1_dataset_approval_service_pb2.CommentDatasetApprovalRequest(
                context=request.context,
                dataset=datasets_v1_datasets_pb2.Dataset(
                    audit=common_v1_audit_pb2.AuditInfo(etag=request.data_schema.audit.etag)
                ),
                details=datasets_v1_dataset_approval_service_pb2.CommentDatasetApprovalRequest.Details(
                    approver=identity_v1_refs_pb2.UserRef(
                        display_name=response_2.dashboard.counterparty.display_name,
                        email=request.data_schema.manager.email
                    )
                )
            )
            port_3: DataSchemaApprovalRejectDataSchema3Port = DataSchemaApprovalRejectDataSchema3Adapter(
                deps.clients.datasets_dataset_approval,
                deps.settings.timeout
            )
            response_3 = await port_3.execute(outgoing_3)
            returned_0_0 = response_0.outcome.status
            if returned_0_0:
                response.outcome.status = returned_0_0
            returned_0_1 = response_0.dataset.owner.email
            returned_0_1_part_1 = response.data_schema.children.add()
            returned_0_1_part_2 = returned_0_1_part_1.children.add()
            if returned_0_1:
                returned_0_1_part_2.manager.email = returned_0_1
            returned_1_0 = response_1.result.status
            if returned_1_0:
                response.result.status = returned_1_0
            returned_2_0 = response_2.result.message
            if returned_2_0:
                response.outcome.message = returned_2_0
            returned_2_1 = response_2.dashboard.billing_address.recipient
            if returned_2_1:
                response.data_schema.location.recipient = returned_2_1
            returned_3_0 = response_3.dataset.name
            returned_3_0_part_1 = response.data_schema.children.add()
            if returned_3_0:
                returned_3_0_part_1.name = returned_3_0
            returned_3_1 = response_3.dataset.address.region
            if returned_3_1:
                response.data_schema.location.region = returned_3_1
            echoed_0 = request.data_schema_id
            response.data_schema.data_schema_id = echoed_0
            echoed_1 = request.data_schema.parent_id
            response.data_schema.parent_id = echoed_1
            return response

    async def handle_submit_data_schema(
        self,
        request: datasets_v1_data_schema_approval_service_pb2.SubmitDataSchemaRequest
    ) -> datasets_v1_data_schema_approval_service_pb2.SubmitDataSchemaResponse:
        """Submits a data schema."""
        deps = self.deps
        response = datasets_v1_data_schema_approval_service_pb2.SubmitDataSchemaResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SubmitDataSchema', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'SubmitDataSchema', {'reason': request.reason})
            await deps.repository.save_data_schema(request.context.tenant_id, request.data_schema)
            response_0 = authorization_v1_access_policy_service_pb2.WatchAccessPoliciesResponse()
            response_1 = customers_v1_preference_calculation_service_pb2.EstimatePreferenceResponse()
            outgoing_0 = authorization_v1_access_policy_service_pb2.WatchAccessPoliciesRequest(
                context=request.context,
                subscriber=common_v1_contact_pb2.ContactInfo(email=request.data_schema.manager.email)
            )
            async for chunk_0 in deps.clients.authorization_access_policy.WatchAccessPolicies(
                outgoing_0,
                timeout=deps.settings.timeout
            ):
                response_0 = chunk_0
            outgoing_1 = customers_v1_preference_calculation_service_pb2.EstimatePreferenceRequest(
                context=request.context,
                preference=customers_v1_customers_pb2.Preference(
                    audit=common_v1_audit_pb2.AuditInfo(
                        created_by=request.data_schema.audit.created_by,
                        etag=request.data_schema.audit.etag
                    ),
                    owner=identity_v1_refs_pb2.UserRef(
                        display_name=request.details.approver.display_name,
                        user_id=request.details.approver.user_id
                    )
                )
            )
            response_1 = await DataSchemaApprovalSubmitDataSchema1Adapter(
                deps.clients.customers_preference_calculation,
                deps.settings.timeout
            )(outgoing_1)
            returned_1_0 = response_1.preference.owner.user_id
            if returned_1_0:
                response.data_schema.manager.user_id = returned_1_0
            echoed_0 = request.data_schema_id
            response.data_schema.data_schema_id = echoed_0
            echoed_1 = request.details.effective_at
            response.outcome.effective_at.CopyFrom(echoed_1)
            return response
