"""Routes datasets through approval, with escalation and delegation."""

from __future__ import annotations

from collections.abc import AsyncIterator
from dataclasses import dataclass
from functools import partial
from typing import cast
import asyncio
import logging

from google.protobuf.json_format import MessageToDict
from google.protobuf.json_format import MessageToJson
from google.protobuf.json_format import Parse
from google.protobuf.json_format import ParseDict
import grpc

from acme.boxoffice.v1 import box_office_sale_service_pb2 as boxoffice_v1_box_office_sale_service_pb2
from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.compliance.v1 import (
    compliance_case_calculation_service_pb2 as compliance_v1_compliance_case_calculation_service_pb2,
)
from acme.compliance.v1 import compliance_pb2 as compliance_v1_compliance_pb2
from acme.customers.v1 import (
    consent_record_calculation_service_pb2 as customers_v1_consent_record_calculation_service_pb2,
)
from acme.customers.v1 import customer_calculation_service_pb2 as customers_v1_customer_calculation_service_pb2
from acme.customers.v1 import customer_query_service_pb2 as customers_v1_customer_query_service_pb2
from acme.customers.v1 import customer_validation_service_pb2 as customers_v1_customer_validation_service_pb2
from acme.customers.v1 import customers_pb2 as customers_v1_customers_pb2
from acme.customers.v1 import refs_pb2 as customers_v1_refs_pb2
from acme.datasets.v1 import data_schema_calculation_service_pb2 as datasets_v1_data_schema_calculation_service_pb2
from acme.datasets.v1 import data_schema_validation_service_pb2 as datasets_v1_data_schema_validation_service_pb2
from acme.datasets.v1 import dataset_approval_service_pb2 as datasets_v1_dataset_approval_service_pb2
from acme.datasets.v1 import dataset_approval_service_pb2_grpc as datasets_v1_dataset_approval_service_pb2_grpc
from acme.datasets.v1 import dataset_query_service_pb2 as datasets_v1_dataset_query_service_pb2
from acme.datasets.v1 import dataset_service_pb2 as datasets_v1_dataset_service_pb2
from acme.datasets.v1 import (
    dataset_version_calculation_service_pb2 as datasets_v1_dataset_version_calculation_service_pb2,
)
from acme.datasets.v1 import datasets_pb2 as datasets_v1_datasets_pb2
from acme.datasets.v1 import refs_pb2 as datasets_v1_refs_pb2
from acme.featurestore.v1 import feature_value_sync_service_pb2 as featurestore_v1_feature_value_sync_service_pb2
from acme.featurestore.v1 import featurestore_pb2 as featurestore_v1_featurestore_pb2
from acme.forms.v1 import form_service_pb2 as forms_v1_form_service_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.identity.v1 import user_query_service_pb2 as identity_v1_user_query_service_pb2
from acme.labeling.v1 import annotation_approval_service_pb2 as labeling_v1_annotation_approval_service_pb2
from acme.ledger.v1 import ledger_account_query_service_pb2 as ledger_v1_ledger_account_query_service_pb2
from acme.pipelines.v1 import pipeline_approval_service_pb2 as pipelines_v1_pipeline_approval_service_pb2
from acme.pipelines.v1 import pipelines_pb2 as pipelines_v1_pipelines_pb2

from acme_data.domains.datasets import hooks
from acme_data.domains.datasets.adapters import DatasetApprovalRejectDataset3Adapter
from acme_data.domains.datasets.adapters import DatasetApprovalRejectDataset3Port
from acme_data.domains.datasets.dependencies import Dependencies
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import run_steps
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_id
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


@dataclass(slots=True)
class DatasetApprovalServicer(datasets_v1_dataset_approval_service_pb2_grpc.DatasetApprovalServiceServicer):
    deps: Dependencies

    @rpc_errors
    async def ApproveDataset(
        self, request: datasets_v1_dataset_approval_service_pb2.ApproveDatasetRequest, context: grpc.aio.ServicerContext,
    ) -> datasets_v1_dataset_approval_service_pb2.ApproveDatasetResponse:
        """Approves a dataset."""
        return await self.handle_approve_dataset(request)

    @rpc_errors
    async def CommentDatasetApproval(
        self, request: datasets_v1_dataset_approval_service_pb2.CommentDatasetApprovalRequest, context: grpc.aio.ServicerContext,
    ) -> datasets_v1_dataset_approval_service_pb2.CommentDatasetApprovalResponse:
        """Comments a dataset."""
        return await self.handle_comment_dataset_approval(request)

    @rpc_errors
    async def DelegateDatasetApproval(
        self, request: datasets_v1_dataset_approval_service_pb2.DelegateDatasetApprovalRequest, context: grpc.aio.ServicerContext,
    ) -> datasets_v1_dataset_approval_service_pb2.DelegateDatasetApprovalResponse:
        """Delegates a dataset."""
        return await self.handle_delegate_dataset_approval(request)

    @rpc_errors
    async def EscalateDataset(
        self, request: datasets_v1_dataset_approval_service_pb2.EscalateDatasetRequest, context: grpc.aio.ServicerContext,
    ) -> datasets_v1_dataset_approval_service_pb2.EscalateDatasetResponse:
        """Escalates a dataset."""
        return await self.handle_escalate_dataset(request)

    @rpc_errors
    @retry_transient
    async def GetDatasetApprovalStatus(
        self, request: datasets_v1_dataset_approval_service_pb2.GetDatasetApprovalStatusRequest, context: grpc.aio.ServicerContext,
    ) -> datasets_v1_dataset_approval_service_pb2.GetDatasetApprovalStatusResponse:
        """Returns a dataset."""
        return await self.handle_get_dataset_approval_status(request)

    @rpc_errors
    @retry_transient
    async def ListPendingDatasets(
        self, request: datasets_v1_dataset_approval_service_pb2.ListPendingDatasetsRequest, context: grpc.aio.ServicerContext,
    ) -> datasets_v1_dataset_approval_service_pb2.ListPendingDatasetsResponse:
        """Lists datasets a page at a time."""
        return await self.handle_list_pending_datasets(request)

    @rpc_errors
    async def RecallDataset(
        self, request: datasets_v1_dataset_approval_service_pb2.RecallDatasetRequest, context: grpc.aio.ServicerContext,
    ) -> datasets_v1_dataset_approval_service_pb2.RecallDatasetResponse:
        """Recalls a dataset."""
        return await self.handle_recall_dataset(request)

    @rpc_errors
    async def RejectDataset(
        self, request: datasets_v1_dataset_approval_service_pb2.RejectDatasetRequest, context: grpc.aio.ServicerContext,
    ) -> datasets_v1_dataset_approval_service_pb2.RejectDatasetResponse:
        """Rejects a dataset."""
        return await self.handle_reject_dataset(request)

    @rpc_errors
    async def SubmitDataset(
        self, request: datasets_v1_dataset_approval_service_pb2.SubmitDatasetRequest, context: grpc.aio.ServicerContext,
    ) -> datasets_v1_dataset_approval_service_pb2.SubmitDatasetResponse:
        """Submits a dataset."""
        return await self.handle_submit_dataset(request)

    async def handle_approve_dataset(
        self,
        request: datasets_v1_dataset_approval_service_pb2.ApproveDatasetRequest
    ) -> datasets_v1_dataset_approval_service_pb2.ApproveDatasetResponse:
        """Approves a dataset."""
        deps = self.deps
        response = datasets_v1_dataset_approval_service_pb2.ApproveDatasetResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ApproveDataset', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'ApproveDataset', {'reason': request.reason})
            await deps.repository.save_dataset(request.context.tenant_id, request.dataset)
            response_0 = datasets_v1_dataset_service_pb2.SearchDatasetsResponse()
            response_1 = datasets_v1_dataset_query_service_pb2.FindDatasetsResponse()
            outgoing_0 = datasets_v1_dataset_service_pb2.SearchDatasetsRequest(
                context=request.context,
                filter=datasets_v1_dataset_service_pb2.SearchDatasetsRequest.Filter(
                    created_after=request.details.effective_at,
                    owner_id=request.dataset.components.get(
                        'primary',
                        datasets_v1_datasets_pb2.DatasetComponent()
                    ).component_id,
                    region=request.dataset.address.region
                )
            )
            outgoing_1 = datasets_v1_dataset_query_service_pb2.FindDatasetsRequest(
                context=request.context,
                filter=datasets_v1_dataset_query_service_pb2.FindDatasetsRequest.Filter(
                    created_after=request.dataset.audit.updated_at,
                    region=request.dataset.address.region
                )
            )
            response_0, response_1 = await asyncio.gather(
                deps.clients.datasets_dataset.SearchDatasets(outgoing_0, timeout=deps.settings.timeout),
                deps.clients.datasets_dataset_query.FindDatasets(outgoing_1, timeout=deps.settings.timeout),
            )
            returned_0_0 = response_0.result.correlation_id
            if returned_0_0:
                response.result.correlation_id = returned_0_0
            returned_1_0 = response_1.result.message
            if returned_1_0:
                response.result.message = returned_1_0
            echoed_0 = request.dataset_id
            response.dataset.dataset_id = echoed_0
            echoed_1 = request.dataset.name
            response.dataset.name = echoed_1
            return response

    async def handle_comment_dataset_approval(
        self,
        request: datasets_v1_dataset_approval_service_pb2.CommentDatasetApprovalRequest
    ) -> datasets_v1_dataset_approval_service_pb2.CommentDatasetApprovalResponse:
        """Comments a dataset."""
        deps = self.deps
        response = datasets_v1_dataset_approval_service_pb2.CommentDatasetApprovalResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CommentDatasetApproval', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'CommentDatasetApproval', {'reason': request.reason})
            await deps.repository.save_dataset(request.context.tenant_id, request.dataset)
            response_0 = compliance_v1_compliance_case_calculation_service_pb2.RecalculateComplianceCasesResponse()
            response_1 = ledger_v1_ledger_account_query_service_pb2.ResolveLedgerAccountsResponse()
            response_2 = datasets_v1_dataset_query_service_pb2.BrowseDatasetsResponse()
            response_3 = identity_v1_user_query_service_pb2.SuggestUsersResponse()
            outgoing_0 = compliance_v1_compliance_case_calculation_service_pb2.RecalculateComplianceCasesRequest(
                compliance_case=compliance_v1_compliance_pb2.ComplianceCase(
                    requester=common_v1_contact_pb2.ContactInfo(email=request.details.approver.email)
                ),
                context=request.context
            )
            response_0 = cast(compliance_v1_compliance_case_calculation_service_pb2.RecalculateComplianceCasesResponse, await deps.bus.request(
                'acme.datasets.v1.DatasetApprovalService/CommentDatasetApproval/0', outgoing_0, deps.settings.timeout,
            ))
            outgoing_1 = ledger_v1_ledger_account_query_service_pb2.ResolveLedgerAccountsRequest(
                context=request.context
            )
            response_1 = await deps.clients.ledger_ledger_account_query.ResolveLedgerAccounts(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = datasets_v1_dataset_query_service_pb2.BrowseDatasetsRequest(
                context=request.context,
                filter=datasets_v1_dataset_query_service_pb2.BrowseDatasetsRequest.Filter(
                    region=request.dataset.address.region
                )
            )
            method_name_2 = 'BrowseDatasets'
            response_2 = await getattr(
                deps.clients.datasets_dataset_query,
                method_name_2
            )(outgoing_2, timeout=deps.settings.timeout)
            outgoing_3 = identity_v1_user_query_service_pb2.SuggestUsersRequest()
            outgoing_3.context.CopyFrom(request.context)
            if request.dataset.WhichOneof('locator') == 'address':
                outgoing_3.filter.region = request.dataset.address.region
            outgoing_3.filter.created_after.CopyFrom(response_0.compliance_case.audit.updated_at)
            response_3 = await deps.clients.identity_user_query.SuggestUsers(outgoing_3, timeout=deps.settings.timeout)
            returned_0_0 = response_0.result.status
            if returned_0_0:
                response.result.status = returned_0_0
            returned_0_1 = response_0.compliance_case.audit.created_at
            if returned_0_1.ListFields():
                response.dataset.audit.created_at.MergeFrom(returned_0_1)
            returned_1_0 = response_1.result.details
            response.result.details.update(returned_1_0)
            returned_2_0 = response_2.result.correlation_id
            if returned_2_0:
                response.result.correlation_id = returned_2_0
            returned_2_1 = response_2.result.message
            if returned_2_1:
                response.result.message = returned_2_1
            returned_3_0 = response_3.result.message
            if returned_3_0:
                response.result.message = returned_3_0
            echoed_0 = request.dataset_id
            response.dataset.dataset_id = echoed_0
            echoed_1 = request.dataset.owner
            response.dataset.owner.CopyFrom(echoed_1)
            return response

    async def handle_delegate_dataset_approval(
        self,
        request: datasets_v1_dataset_approval_service_pb2.DelegateDatasetApprovalRequest
    ) -> datasets_v1_dataset_approval_service_pb2.DelegateDatasetApprovalResponse:
        """Delegates a dataset."""
        deps = self.deps
        response = datasets_v1_dataset_approval_service_pb2.DelegateDatasetApprovalResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('DelegateDatasetApproval', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'DelegateDatasetApproval',
                {'reason': request.reason}
            )
            await deps.repository.save_dataset(request.context.tenant_id, request.dataset)
            response_0 = datasets_v1_dataset_version_calculation_service_pb2.SimulateDatasetVersionResponse()
            response_1 = pipelines_v1_pipeline_approval_service_pb2.EscalatePipelineResponse()
            outgoing_0 = datasets_v1_dataset_version_calculation_service_pb2.SimulateDatasetVersionRequest(
                context=request.context,
                dataset_version=datasets_v1_datasets_pb2.DatasetVersion(
                    subject=customers_v1_refs_pb2.CustomerRef(email=request.details.approver.email)
                )
            )
            document_0 = MessageToDict(outgoing_0, preserving_proto_field_name=True)
            outgoing_0 = ParseDict(
                document_0,
                datasets_v1_dataset_version_calculation_service_pb2.SimulateDatasetVersionRequest()
            )
            response_0 = await deps.clients.datasets_dataset_version_calculation.SimulateDatasetVersion(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = pipelines_v1_pipeline_approval_service_pb2.EscalatePipelineRequest(
                context=request.context,
                pipeline=pipelines_v1_pipelines_pb2.Pipeline(
                    audit=common_v1_audit_pb2.AuditInfo(created_at=request.dataset.audit.created_at),
                    location=common_v1_address_pb2.PostalAddress(postal_code=request.dataset.address.postal_code),
                    participants=[
                        pipelines_v1_pipelines_pb2.PipelineParticipant(
                            contact=common_v1_contact_pb2.ContactInfo(email=request.dataset.owner.email)
                        )
                    ]
                )
            )
            document_1 = MessageToJson(outgoing_1, preserving_proto_field_name=True)
            outgoing_1 = Parse(document_1, pipelines_v1_pipeline_approval_service_pb2.EscalatePipelineRequest())
            response_1 = await deps.clients.pipelines_pipeline_approval.EscalatePipeline(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.outcome.message = returned_0_0
            returned_1_0 = response_1.result.message
            if returned_1_0:
                response.result.message = returned_1_0
            returned_1_1 = response_1.outcome.next_steps
            response.outcome.next_steps.extend(returned_1_1)
            echoed_0 = request.dataset_id
            response.dataset.dataset_id = echoed_0
            echoed_1 = request.dataset.name
            response.dataset.name = echoed_1
            return response

    async def handle_escalate_dataset(
        self,
        request: datasets_v1_dataset_approval_service_pb2.EscalateDatasetRequest
    ) -> datasets_v1_dataset_approval_service_pb2.EscalateDatasetResponse:
        """Escalates a dataset."""
        deps = self.deps
        response = datasets_v1_dataset_approval_service_pb2.EscalateDatasetResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('EscalateDataset', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'EscalateDataset', {'reason': request.reason})
            await deps.repository.save_dataset(request.context.tenant_id, request.dataset)
            response_0 = boxoffice_v1_box_office_sale_service_pb2.CloneBoxOfficeSaleResponse()
            outgoing_0 = boxoffice_v1_box_office_sale_service_pb2.CloneBoxOfficeSaleRequest()
            outgoing_0.context.CopyFrom(request.context)
            outgoing_0.box_office_sale.counterparty.display_name = request.details.approver.display_name
            merged_0 = boxoffice_v1_box_office_sale_service_pb2.CloneBoxOfficeSaleRequest()
            merged_0.MergeFrom(outgoing_0)
            outgoing_0.CopyFrom(merged_0)
            response_0 = await deps.clients.boxoffice_box_office_sale.CloneBoxOfficeSale(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.box_office_sale.audit.etag
            if returned_0_0:
                response.dataset.audit.etag = returned_0_0
            returned_0_1 = response_0.result.details
            response.result.details.update(returned_0_1)
            echoed_0 = request.dataset_id
            response.dataset.dataset_id = echoed_0
            echoed_1 = request.details.effective_at
            response.outcome.effective_at.CopyFrom(echoed_1)
            return response

    async def handle_get_dataset_approval_status(
        self,
        request: datasets_v1_dataset_approval_service_pb2.GetDatasetApprovalStatusRequest
    ) -> datasets_v1_dataset_approval_service_pb2.GetDatasetApprovalStatusResponse:
        """Returns a dataset."""
        deps = self.deps
        response = datasets_v1_dataset_approval_service_pb2.GetDatasetApprovalStatusResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('GetDatasetApprovalStatus', extra={'fields': {'domain': 'datasets'}})
            await deps.repository.audit(request.context.tenant_id, 'GetDatasetApprovalStatus', {})
            response_0 = customers_v1_consent_record_calculation_service_pb2.RecalculateConsentRecordsResponse()
            outgoing_0 = customers_v1_consent_record_calculation_service_pb2.RecalculateConsentRecordsRequest(
                consent_record=customers_v1_customers_pb2.ConsentRecord(
                    measurements=[
                        customers_v1_customers_pb2.ConsentRecordMeasurement(observed_at=request.context.deadline)
                    ],
                    source=request.dataset_id
                ),
                context=request.context
            )
            response_0 = await deps.clients.customers_consent_record_calculation.RecalculateConsentRecords(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_0)
            echoed_0 = request.dataset_id
            response.dataset.dataset_id = echoed_0
            return response

    async def handle_list_pending_datasets(
        self,
        request: datasets_v1_dataset_approval_service_pb2.ListPendingDatasetsRequest
    ) -> datasets_v1_dataset_approval_service_pb2.ListPendingDatasetsResponse:
        """Lists datasets a page at a time."""
        deps = self.deps
        response = datasets_v1_dataset_approval_service_pb2.ListPendingDatasetsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ListPendingDatasets', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ListPendingDatasets',
                {'order_by': request.order_by}
            )
            response_0 = customers_v1_customer_calculation_service_pb2.ExplainCustomerCalculationResponse()
            outgoing_0 = customers_v1_customer_calculation_service_pb2.ExplainCustomerCalculationRequest(
                context=request.context,
                customer=customers_v1_customers_pb2.Customer(
                    primary_address=common_v1_address_pb2.PostalAddress(region=request.filter.region),
                    relationship_manager=identity_v1_refs_pb2.UserRef(email=request.context.actor.email)
                )
            )
            response_0 = await deps.clients.customers_customer_calculation.ExplainCustomerCalculation(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.customer.audit.etag
            returned_0_0_part_0 = response.datasets.add()
            if returned_0_0:
                returned_0_0_part_0.audit.etag = returned_0_0
            returned_0_1 = response_0.customer.relationship_manager.display_name
            returned_0_1_part_0 = response.datasets.add()
            if returned_0_1:
                returned_0_1_part_0.owner.display_name = returned_0_1
            return response

    async def handle_recall_dataset(
        self,
        request: datasets_v1_dataset_approval_service_pb2.RecallDatasetRequest
    ) -> datasets_v1_dataset_approval_service_pb2.RecallDatasetResponse:
        """Recalls a dataset."""
        deps = self.deps
        response = datasets_v1_dataset_approval_service_pb2.RecallDatasetResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('RecallDataset', extra={'fields': {'capacity': request.dataset.capacity}})
            await deps.repository.audit(
                request.context.tenant_id,
                'RecallDataset',
                {'capacity': request.dataset.capacity}
            )
            await deps.repository.save_dataset(request.context.tenant_id, request.dataset)
            response_0 = customers_v1_customer_query_service_pb2.SummarizeCustomersResponse()
            response_1 = datasets_v1_data_schema_validation_service_pb2.ScoreDataSchemaResponse()
            outgoing_0 = customers_v1_customer_query_service_pb2.SummarizeCustomersRequest(
                annotations=dict(request.annotations),
                context=request.context,
                details=customers_v1_customer_query_service_pb2.SummarizeCustomersRequest.Details(
                    filters=dict(request.dataset.specs)
                ),
                reason=request.reason
            )
            outgoing_1 = datasets_v1_data_schema_validation_service_pb2.ScoreDataSchemaRequest(
                context=request.context,
                data_schema=datasets_v1_datasets_pb2.DataSchema(
                    children=[
                        datasets_v1_datasets_pb2.DataSchema(
                            children=[
                                datasets_v1_datasets_pb2.DataSchema(
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
                deps.clients.customers_customer_query.SummarizeCustomers(outgoing_0, timeout=deps.settings.timeout),
                deps.clients.datasets_data_schema_validation.ScoreDataSchema(outgoing_1, timeout=deps.settings.timeout),
            )
            returned_0_0 = response_0.result.correlation_id
            if returned_0_0:
                response.result.correlation_id = returned_0_0
            returned_0_1 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_1)
            returned_1_0 = response_1.data_schema.manager.user_id
            if returned_1_0:
                response.dataset.owner.user_id = returned_1_0
            echoed_0 = request.dataset_id
            response.dataset.dataset_id = echoed_0
            echoed_1 = request.details.effective_at
            response.outcome.effective_at.CopyFrom(echoed_1)
            return response

    async def handle_reject_dataset(
        self,
        request: datasets_v1_dataset_approval_service_pb2.RejectDatasetRequest
    ) -> datasets_v1_dataset_approval_service_pb2.RejectDatasetResponse:
        """Rejects a dataset."""
        deps = self.deps
        response = datasets_v1_dataset_approval_service_pb2.RejectDatasetResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('RejectDataset', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'RejectDataset', {'reason': request.reason})
            await deps.repository.save_dataset(request.context.tenant_id, request.dataset)
            response_0 = forms_v1_form_service_pb2.ListFormsResponse()
            response_1 = featurestore_v1_feature_value_sync_service_pb2.PushFeatureValueResponse()
            response_2 = customers_v1_customer_validation_service_pb2.CheckCustomerEligibilityResponse()
            response_3 = datasets_v1_data_schema_calculation_service_pb2.CompareDataSchemaOptionsResponse()
            outgoing_0 = forms_v1_form_service_pb2.ListFormsRequest(
                context=request.context,
                filter=forms_v1_form_service_pb2.ListFormsRequest.Filter(
                    created_after=request.dataset.audit.created_at,
                    labels=dict(request.dataset.specs),
                    owner_id=request.dataset.components.get(
                        'primary',
                        datasets_v1_datasets_pb2.DatasetComponent()
                    ).component_id,
                    region=request.dataset.address.region
                )
            )
            send_0 = partial(deps.clients.forms_form.ListForms, timeout=deps.settings.timeout)
            response_0 = await send_0(outgoing_0)
            outgoing_1 = featurestore_v1_feature_value_sync_service_pb2.PushFeatureValueRequest(
                context=request.context,
                feature_value=featurestore_v1_featurestore_pb2.FeatureValue(
                    subject=datasets_v1_refs_pb2.DatasetRef(display_name=request.dataset.owner.display_name)
                )
            )
            response_1 = await hooks.dataset_approval_reject_dataset1(
                deps.clients.featurestore_feature_value_sync,
                outgoing_1,
                deps.settings.timeout
            )
            outgoing_2 = customers_v1_customer_validation_service_pb2.CheckCustomerEligibilityRequest()
            outgoing_2.context.CopyFrom(request.context)
            outgoing_2.customer.primary_address.lines.extend(list(request.dataset.address.lines))
            outgoing_2.details.contact.email = request.details.approver.email
            outgoing_2.customer.relationship_manager.user_id = request.details.approver.user_id
            outgoing_2.context.tenant_id = tenant_id.get()
            response_2 = await deps.clients.customers_customer_validation.CheckCustomerEligibility(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            outgoing_3 = datasets_v1_data_schema_calculation_service_pb2.CompareDataSchemaOptionsRequest(
                context=request.context,
                data_schema=datasets_v1_datasets_pb2.DataSchema(
                    children=[
                        datasets_v1_datasets_pb2.DataSchema(
                            children=[
                                datasets_v1_datasets_pb2.DataSchema(
                                    location=common_v1_address_pb2.PostalAddress(
                                        country_code=response_2.customer.primary_address.country_code,
                                        lines=list(request.dataset.address.lines)
                                    )
                                )
                            ]
                        )
                    ]
                )
            )
            port_3: DatasetApprovalRejectDataset3Port = DatasetApprovalRejectDataset3Adapter(
                deps.clients.datasets_data_schema_calculation,
                deps.settings.timeout
            )
            response_3 = await port_3.execute(outgoing_3)
            returned_0_0 = response_0.result.correlation_id
            if returned_0_0:
                response.result.correlation_id = returned_0_0
            returned_1_0 = response_1.result.status
            if returned_1_0:
                response.outcome.status = returned_1_0
            returned_2_0 = response_2.outcome.reference_id
            if returned_2_0:
                response.outcome.reference_id = returned_2_0
            returned_3_0 = response_3.result.status
            if returned_3_0:
                response.outcome.status = returned_3_0
            returned_3_1 = response_3.data_schema.manager.email
            if returned_3_1:
                response.dataset.owner.email = returned_3_1
            echoed_0 = request.dataset_id
            response.dataset.dataset_id = echoed_0
            echoed_1 = request.dataset.status
            response.dataset.status = echoed_1
            return response

    async def handle_submit_dataset(
        self,
        request: datasets_v1_dataset_approval_service_pb2.SubmitDatasetRequest
    ) -> datasets_v1_dataset_approval_service_pb2.SubmitDatasetResponse:
        """Submits a dataset."""
        deps = self.deps
        response = datasets_v1_dataset_approval_service_pb2.SubmitDatasetResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SubmitDataset', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'SubmitDataset', {'reason': request.reason})
            await deps.repository.save_dataset(request.context.tenant_id, request.dataset)
            response_0 = labeling_v1_annotation_approval_service_pb2.CommentAnnotationApprovalResponse()
            outgoing_0 = labeling_v1_annotation_approval_service_pb2.CommentAnnotationApprovalRequest(
                context=request.context,
                details=labeling_v1_annotation_approval_service_pb2.CommentAnnotationApprovalRequest.Details(
                    approver=identity_v1_refs_pb2.UserRef(user_id=request.details.approver.user_id)
                )
            )
            steps_0 = [
                partial(
                    deps.clients.labeling_annotation_approval.CommentAnnotationApproval,
                    outgoing_0,
                    timeout=deps.settings.timeout
                )
            ]
            results_0 = await run_steps(steps_0)
            response_0 = results_0[-1]
            returned_0_0 = response_0.outcome.status
            if returned_0_0:
                response.outcome.status = returned_0_0
            echoed_0 = request.dataset_id
            response.dataset.dataset_id = echoed_0
            echoed_1 = request.dataset.name
            response.dataset.name = echoed_1
            return response
