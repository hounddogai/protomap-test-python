"""Reusable transport mixin for DatasetVersionApprovalService."""

from __future__ import annotations

from collections.abc import AsyncIterator
from collections.abc import Awaitable
from collections.abc import Callable
from functools import partial
from typing import cast
import asyncio
import logging

from google.protobuf.any_pb2 import Any as AnyMessage
from google.protobuf.json_format import MessageToDict
from google.protobuf.json_format import ParseDict
import grpc

from acme.billing.v1 import billing_account_query_service_pb2 as billing_v1_billing_account_query_service_pb2
from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.customers.v1 import (
    consent_record_calculation_service_pb2 as customers_v1_consent_record_calculation_service_pb2,
)
from acme.customers.v1 import customer_service_pb2 as customers_v1_customer_service_pb2
from acme.customers.v1 import customer_validation_service_pb2 as customers_v1_customer_validation_service_pb2
from acme.customers.v1 import customers_pb2 as customers_v1_customers_pb2
from acme.customers.v1 import household_validation_service_pb2 as customers_v1_household_validation_service_pb2
from acme.customers.v1 import preference_validation_service_pb2 as customers_v1_preference_validation_service_pb2
from acme.customers.v1 import refs_pb2 as customers_v1_refs_pb2
from acme.datasets.v1 import data_schema_calculation_service_pb2 as datasets_v1_data_schema_calculation_service_pb2
from acme.datasets.v1 import dataset_approval_service_pb2 as datasets_v1_dataset_approval_service_pb2
from acme.datasets.v1 import dataset_validation_service_pb2 as datasets_v1_dataset_validation_service_pb2
from acme.datasets.v1 import dataset_version_approval_service_pb2 as datasets_v1_dataset_version_approval_service_pb2
from acme.datasets.v1 import (
    dataset_version_calculation_service_pb2 as datasets_v1_dataset_version_calculation_service_pb2,
)
from acme.datasets.v1 import dataset_version_query_service_pb2 as datasets_v1_dataset_version_query_service_pb2
from acme.datasets.v1 import datasets_pb2 as datasets_v1_datasets_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.labeling.v1 import label_set_sync_service_pb2 as labeling_v1_label_set_sync_service_pb2
from acme.labeling.v1 import labeling_pb2 as labeling_v1_labeling_pb2

from acme_data.domains.datasets.adapters import DatasetVersionApprovalApproveDatasetVersion1Adapter
from acme_data.domains.datasets.adapters import DatasetVersionApprovalApproveDatasetVersion1Port
from acme_data.domains.datasets.adapters import DatasetVersionApprovalCommentDatasetVersionApproval1Adapter
from acme_data.domains.datasets.dependencies import Dependencies
from acme_data.domains.datasets.models import DatasetVersionApprovalSubmitDatasetVersion0Command
from acme_data.domains.datasets.models import to_dataset_version_approval_submit_dataset_version0_command
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import run_steps
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class DatasetVersionApprovalServicerHandlers:
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    async def ApproveDatasetVersion(
        self, request: datasets_v1_dataset_version_approval_service_pb2.ApproveDatasetVersionRequest, context: grpc.aio.ServicerContext,
    ) -> datasets_v1_dataset_version_approval_service_pb2.ApproveDatasetVersionResponse:
        """Approves a dataset version."""
        return await self.handle_approve_dataset_version(request)

    @rpc_errors
    async def CommentDatasetVersionApproval(
        self, request: datasets_v1_dataset_version_approval_service_pb2.CommentDatasetVersionApprovalRequest, context: grpc.aio.ServicerContext,
    ) -> datasets_v1_dataset_version_approval_service_pb2.CommentDatasetVersionApprovalResponse:
        """Comments a dataset version."""
        return await self.handle_comment_dataset_version_approval(request)

    @rpc_errors
    async def DelegateDatasetVersionApproval(
        self, request: datasets_v1_dataset_version_approval_service_pb2.DelegateDatasetVersionApprovalRequest, context: grpc.aio.ServicerContext,
    ) -> datasets_v1_dataset_version_approval_service_pb2.DelegateDatasetVersionApprovalResponse:
        """Delegates a dataset version."""
        return await self.handle_delegate_dataset_version_approval(request)

    @rpc_errors
    async def EscalateDatasetVersion(
        self, request: datasets_v1_dataset_version_approval_service_pb2.EscalateDatasetVersionRequest, context: grpc.aio.ServicerContext,
    ) -> datasets_v1_dataset_version_approval_service_pb2.EscalateDatasetVersionResponse:
        """Escalates a dataset version."""
        return await self.handle_escalate_dataset_version(request)

    @rpc_errors
    @retry_transient
    async def GetDatasetVersionApprovalStatus(
        self, request: datasets_v1_dataset_version_approval_service_pb2.GetDatasetVersionApprovalStatusRequest, context: grpc.aio.ServicerContext,
    ) -> datasets_v1_dataset_version_approval_service_pb2.GetDatasetVersionApprovalStatusResponse:
        """Returns a dataset version."""
        return await self.handle_get_dataset_version_approval_status(request)

    @rpc_errors
    @retry_transient
    async def ListPendingDatasetVersions(
        self, request: datasets_v1_dataset_version_approval_service_pb2.ListPendingDatasetVersionsRequest, context: grpc.aio.ServicerContext,
    ) -> datasets_v1_dataset_version_approval_service_pb2.ListPendingDatasetVersionsResponse:
        """Lists dataset versions a page at a time."""
        return await self.handle_list_pending_dataset_versions(request)

    @rpc_errors
    async def RecallDatasetVersion(
        self, request: datasets_v1_dataset_version_approval_service_pb2.RecallDatasetVersionRequest, context: grpc.aio.ServicerContext,
    ) -> datasets_v1_dataset_version_approval_service_pb2.RecallDatasetVersionResponse:
        """Recalls a dataset version."""
        return await self.handle_recall_dataset_version(request)

    @rpc_errors
    async def SubmitDatasetVersion(
        self, request: datasets_v1_dataset_version_approval_service_pb2.SubmitDatasetVersionRequest, context: grpc.aio.ServicerContext,
    ) -> datasets_v1_dataset_version_approval_service_pb2.SubmitDatasetVersionResponse:
        """Submits a dataset version."""
        return await self.handle_submit_dataset_version(request)

    async def handle_approve_dataset_version(
        self,
        request: datasets_v1_dataset_version_approval_service_pb2.ApproveDatasetVersionRequest
    ) -> datasets_v1_dataset_version_approval_service_pb2.ApproveDatasetVersionResponse:
        """Approves a dataset version."""
        deps = self.deps
        response = datasets_v1_dataset_version_approval_service_pb2.ApproveDatasetVersionResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ApproveDatasetVersion', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'ApproveDatasetVersion', {'reason': request.reason})
            await deps.repository.save_dataset_version(request.context.tenant_id, request.dataset_version)
            response_0 = customers_v1_household_validation_service_pb2.ValidateHouseholdResponse()
            response_1 = billing_v1_billing_account_query_service_pb2.ResolveBillingAccountsResponse()
            requests_0: list[customers_v1_household_validation_service_pb2.ValidateHouseholdRequest] = []
            for item_0 in request.dataset_version.measurements:
                outgoing_0 = customers_v1_household_validation_service_pb2.ValidateHouseholdRequest(
                    context=request.context,
                    household=customers_v1_customers_pb2.Household(
                        children=[
                            customers_v1_customers_pb2.Household(
                                children=[
                                    customers_v1_customers_pb2.Household(
                                        audit=common_v1_audit_pb2.AuditInfo(created_at=item_0.observed_at),
                                        manager=identity_v1_refs_pb2.UserRef(
                                            display_name=request.details.approver.display_name
                                        )
                                    )
                                ]
                            )
                        ]
                    )
                )
                requests_0.append(outgoing_0)
            replies_0 = await asyncio.gather(*(
                deps.clients.customers_household_validation.ValidateHousehold(
                    entry,
                    timeout=deps.settings.timeout
                ) for entry in requests_0
            ))
            if replies_0:
                response_0 = replies_0[-1]
            outgoing_1 = billing_v1_billing_account_query_service_pb2.ResolveBillingAccountsRequest(
                context=request.context
            )
            port_1: DatasetVersionApprovalApproveDatasetVersion1Port = DatasetVersionApprovalApproveDatasetVersion1Adapter(
                deps.clients.billing_billing_account_query,
                deps.settings.timeout
            )
            response_1 = await port_1.execute(outgoing_1)
            returned_1_0 = response_1.result.correlation_id
            if returned_1_0:
                response.dataset_version.correlation_id = returned_1_0
            echoed_0 = request.dataset_version_id
            response.dataset_version.dataset_version_id = echoed_0
            echoed_1 = request.dataset_version.sequence
            response.dataset_version.sequence = echoed_1
            return response

    async def handle_comment_dataset_version_approval(
        self,
        request: datasets_v1_dataset_version_approval_service_pb2.CommentDatasetVersionApprovalRequest
    ) -> datasets_v1_dataset_version_approval_service_pb2.CommentDatasetVersionApprovalResponse:
        """Comments a dataset version."""
        deps = self.deps
        response = datasets_v1_dataset_version_approval_service_pb2.CommentDatasetVersionApprovalResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CommentDatasetVersionApproval', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'CommentDatasetVersionApproval',
                {'reason': request.reason}
            )
            await deps.repository.save_dataset_version(request.context.tenant_id, request.dataset_version)
            response_0 = customers_v1_preference_validation_service_pb2.CheckPreferenceEligibilityResponse()
            response_1 = datasets_v1_dataset_validation_service_pb2.ScoreDatasetResponse()
            outgoing_0 = customers_v1_preference_validation_service_pb2.CheckPreferenceEligibilityRequest(
                context=request.context,
                details=customers_v1_preference_validation_service_pb2.CheckPreferenceEligibilityRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(email=request.dataset_version.subject.email)
                )
            )
            steps_0 = [
                partial(
                    deps.clients.customers_preference_validation.CheckPreferenceEligibility,
                    outgoing_0,
                    timeout=deps.settings.timeout
                )
            ]
            results_0 = await run_steps(steps_0)
            response_0 = results_0[-1]
            outgoing_1 = datasets_v1_dataset_validation_service_pb2.ScoreDatasetRequest(
                context=request.context,
                dataset=datasets_v1_datasets_pb2.Dataset(
                    audit=common_v1_audit_pb2.AuditInfo(created_by=response_0.preference.audit.created_by),
                    owner=identity_v1_refs_pb2.UserRef(display_name=response_0.preference.owner.display_name)
                )
            )
            response_1 = await DatasetVersionApprovalCommentDatasetVersionApproval1Adapter(
                deps.clients.datasets_dataset_validation,
                deps.settings.timeout
            )(outgoing_1)
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.result.message = returned_0_0
            returned_0_1 = response_0.result.message
            if returned_0_1:
                response.outcome.message = returned_0_1
            returned_1_0 = response_1.dataset.owner.email
            if returned_1_0:
                response.dataset_version.subject.email = returned_1_0
            echoed_0 = request.dataset_version_id
            response.dataset_version.dataset_version_id = echoed_0
            echoed_1 = request.dataset_version.sequence
            response.dataset_version.sequence = echoed_1
            return response

    async def handle_delegate_dataset_version_approval(
        self,
        request: datasets_v1_dataset_version_approval_service_pb2.DelegateDatasetVersionApprovalRequest
    ) -> datasets_v1_dataset_version_approval_service_pb2.DelegateDatasetVersionApprovalResponse:
        """Delegates a dataset version."""
        deps = self.deps
        response = datasets_v1_dataset_version_approval_service_pb2.DelegateDatasetVersionApprovalResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('DelegateDatasetVersionApproval', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'DelegateDatasetVersionApproval',
                {'reason': request.reason}
            )
            await deps.repository.save_dataset_version(request.context.tenant_id, request.dataset_version)
            response_0 = customers_v1_household_validation_service_pb2.ValidateHouseholdResponse()
            outgoing_0 = customers_v1_household_validation_service_pb2.ValidateHouseholdRequest(
                context=request.context,
                household=customers_v1_customers_pb2.Household(
                    children=[
                        customers_v1_customers_pb2.Household(
                            children=[
                                customers_v1_customers_pb2.Household(
                                    manager=identity_v1_refs_pb2.UserRef(
                                        display_name=request.details.approver.display_name
                                    )
                                )
                            ],
                            manager=identity_v1_refs_pb2.UserRef(email=request.details.approver.email)
                        )
                    ]
                )
            )
            response_0 = cast(customers_v1_household_validation_service_pb2.ValidateHouseholdResponse, await deps.bus.request(
                'acme.datasets.v1.DatasetVersionApprovalService/DelegateDatasetVersionApproval/0', outgoing_0, deps.settings.timeout,
            ))
            returned_0_0 = response_0.result.correlation_id
            if returned_0_0:
                response.result.correlation_id = returned_0_0
            echoed_0 = request.dataset_version_id
            response.dataset_version.dataset_version_id = echoed_0
            echoed_1 = request.dataset_version.attributes
            response.dataset_version.attributes.update(echoed_1)
            return response

    async def handle_escalate_dataset_version(
        self,
        request: datasets_v1_dataset_version_approval_service_pb2.EscalateDatasetVersionRequest
    ) -> datasets_v1_dataset_version_approval_service_pb2.EscalateDatasetVersionResponse:
        """Escalates a dataset version."""
        deps = self.deps
        response = datasets_v1_dataset_version_approval_service_pb2.EscalateDatasetVersionResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('EscalateDatasetVersion', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'EscalateDatasetVersion', {'reason': request.reason})
            await deps.repository.save_dataset_version(request.context.tenant_id, request.dataset_version)
            response_0 = datasets_v1_dataset_approval_service_pb2.ListPendingDatasetsResponse()
            response_1 = datasets_v1_dataset_version_calculation_service_pb2.ExplainDatasetVersionCalculationResponse()
            response_2 = customers_v1_customer_validation_service_pb2.GetCustomerRulesResponse()
            response_3 = datasets_v1_dataset_version_query_service_pb2.SuggestDatasetVersionsResponse()
            outgoing_0 = datasets_v1_dataset_approval_service_pb2.ListPendingDatasetsRequest(
                context=request.context,
                filter=datasets_v1_dataset_approval_service_pb2.ListPendingDatasetsRequest.Filter(
                    created_after=request.dataset_version.occurred_at
                )
            )
            outgoing_1 = datasets_v1_dataset_version_calculation_service_pb2.ExplainDatasetVersionCalculationRequest(
                context=request.context,
                dataset_version=datasets_v1_datasets_pb2.DatasetVersion(
                    subject=customers_v1_refs_pb2.CustomerRef(
                        display_name=request.dataset_version.subject.display_name,
                        email=request.details.approver.email
                    )
                ),
                details=datasets_v1_dataset_version_calculation_service_pb2.ExplainDatasetVersionCalculationRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(email=request.dataset_version.subject.email)
                )
            )
            outgoing_2 = customers_v1_customer_validation_service_pb2.GetCustomerRulesRequest(
                context=request.context,
                customer_id=request.dataset_version.subject.customer_id
            )
            response_0, response_1, response_2 = await asyncio.gather(
                deps.clients.datasets_dataset_approval.ListPendingDatasets(outgoing_0, timeout=deps.settings.timeout),
                deps.clients.datasets_dataset_version_calculation.ExplainDatasetVersionCalculation(
                    outgoing_1,
                    timeout=deps.settings.timeout
                ),
                deps.clients.customers_customer_validation.GetCustomerRules(outgoing_2, timeout=deps.settings.timeout),
            )
            outgoing_3 = datasets_v1_dataset_version_query_service_pb2.SuggestDatasetVersionsRequest(
                context=request.context,
                filter=datasets_v1_dataset_version_query_service_pb2.SuggestDatasetVersionsRequest.Filter(
                    created_after=response_2.customer.audit.updated_at,
                    labels=dict(request.dataset_version.attributes),
                    owner_id=request.details.approver.user_id,
                    region=response_2.customer.primary_address.region
                )
            )
            document_3 = MessageToDict(outgoing_3, preserving_proto_field_name=True)
            outgoing_3 = ParseDict(
                document_3,
                datasets_v1_dataset_version_query_service_pb2.SuggestDatasetVersionsRequest()
            )
            response_3 = await deps.clients.datasets_dataset_version_query.SuggestDatasetVersions(
                outgoing_3,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.status
            if returned_0_0:
                response.outcome.status = returned_0_0
            returned_0_1 = response_0.result.correlation_id
            if returned_0_1:
                response.result.correlation_id = returned_0_1
            returned_1_0 = response_1.dataset_version.correlation_id
            if returned_1_0:
                response.dataset_version.correlation_id = returned_1_0
            returned_1_1 = response_1.outcome.status
            if returned_1_1:
                response.result.status = returned_1_1
            returned_2_0 = response_2.result.message
            if returned_2_0:
                response.outcome.message = returned_2_0
            returned_2_1 = response_2.customer.contact.email
            if returned_2_1:
                response.dataset_version.subject.email = returned_2_1
            returned_3_0 = response_3.result.details
            response.result.details.update(returned_3_0)
            returned_3_1 = response_3.result.correlation_id
            if returned_3_1:
                response.dataset_version.correlation_id = returned_3_1
            echoed_0 = request.dataset_version_id
            response.dataset_version.dataset_version_id = echoed_0
            echoed_1 = request.dataset_version.attributes
            response.dataset_version.attributes.update(echoed_1)
            return response

    async def handle_get_dataset_version_approval_status(
        self,
        request: datasets_v1_dataset_version_approval_service_pb2.GetDatasetVersionApprovalStatusRequest
    ) -> datasets_v1_dataset_version_approval_service_pb2.GetDatasetVersionApprovalStatusResponse:
        """Returns a dataset version."""
        deps = self.deps
        response = datasets_v1_dataset_version_approval_service_pb2.GetDatasetVersionApprovalStatusResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('GetDatasetVersionApprovalStatus', extra={'fields': {'locale': request.context.locale}})
            await deps.repository.audit(
                request.context.tenant_id,
                'GetDatasetVersionApprovalStatus',
                {'locale': request.context.locale}
            )
            echoed_0 = request.dataset_version_id
            response.dataset_version.dataset_version_id = echoed_0
            return response

    async def handle_list_pending_dataset_versions(
        self,
        request: datasets_v1_dataset_version_approval_service_pb2.ListPendingDatasetVersionsRequest
    ) -> datasets_v1_dataset_version_approval_service_pb2.ListPendingDatasetVersionsResponse:
        """Lists dataset versions a page at a time."""
        deps = self.deps
        response = datasets_v1_dataset_version_approval_service_pb2.ListPendingDatasetVersionsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ListPendingDatasetVersions', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ListPendingDatasetVersions',
                {'order_by': request.order_by}
            )
            response_0 = datasets_v1_dataset_version_calculation_service_pb2.SimulateDatasetVersionResponse()
            outgoing_0 = datasets_v1_dataset_version_calculation_service_pb2.SimulateDatasetVersionRequest(
                context=request.context,
                dataset_version=datasets_v1_datasets_pb2.DatasetVersion(
                    correlation_id=request.filter.owner_id,
                    occurred_at=request.filter.created_after,
                    subject=customers_v1_refs_pb2.CustomerRef(email=request.context.actor.email)
                ),
                details=datasets_v1_dataset_version_calculation_service_pb2.SimulateDatasetVersionRequest.Details(
                    destination=common_v1_address_pb2.PostalAddress(region=request.filter.region)
                )
            )
            response_0 = await deps.clients.datasets_dataset_version_calculation.SimulateDatasetVersion(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.dataset_version.subject.display_name
            returned_0_0_part_0 = response.dataset_versions.add()
            if returned_0_0:
                returned_0_0_part_0.subject.display_name = returned_0_0
            returned_0_1 = response_0.result.correlation_id
            returned_0_1_part_0 = response.dataset_versions.add()
            if returned_0_1:
                returned_0_1_part_0.correlation_id = returned_0_1
            return response

    async def handle_recall_dataset_version(
        self,
        request: datasets_v1_dataset_version_approval_service_pb2.RecallDatasetVersionRequest
    ) -> datasets_v1_dataset_version_approval_service_pb2.RecallDatasetVersionResponse:
        """Recalls a dataset version."""
        deps = self.deps
        response = datasets_v1_dataset_version_approval_service_pb2.RecallDatasetVersionResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('RecallDatasetVersion', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'RecallDatasetVersion', {'reason': request.reason})
            await deps.repository.save_dataset_version(request.context.tenant_id, request.dataset_version)
            response_0 = customers_v1_consent_record_calculation_service_pb2.QuoteConsentRecordResponse()
            response_1 = labeling_v1_label_set_sync_service_pb2.SyncLabelSetsResponse()
            response_2 = datasets_v1_dataset_version_calculation_service_pb2.CalculateDatasetVersionResponse()
            outgoing_0 = customers_v1_consent_record_calculation_service_pb2.QuoteConsentRecordRequest()
            outgoing_0.context.CopyFrom(request.context)
            outgoing_0.consent_record.subject.display_name = request.details.approver.display_name
            outgoing_0.consent_record.correlation_id = request.dataset_version.correlation_id
            outgoing_0.consent_record.source = request.dataset_version.source
            outgoing_0.consent_record.attributes.update(dict(request.dataset_version.attributes))
            merged_0 = customers_v1_consent_record_calculation_service_pb2.QuoteConsentRecordRequest()
            merged_0.MergeFrom(outgoing_0)
            outgoing_0.CopyFrom(merged_0)
            response_0 = await deps.clients.customers_consent_record_calculation.QuoteConsentRecord(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = labeling_v1_label_set_sync_service_pb2.SyncLabelSetsRequest(
                context=request.context,
                label_set=labeling_v1_labeling_pb2.LabelSet(
                    children=[
                        labeling_v1_labeling_pb2.LabelSet(
                            children=[
                                labeling_v1_labeling_pb2.LabelSet(
                                    children=[
                                        labeling_v1_labeling_pb2.LabelSet(
                                            attributes=dict(response_0.consent_record.attributes)
                                        )
                                    ],
                                    manager=identity_v1_refs_pb2.UserRef(
                                        display_name=request.details.approver.display_name
                                    )
                                )
                            ]
                        )
                    ]
                )
            )
            envelope_1 = AnyMessage()
            envelope_1.Pack(outgoing_1)
            outgoing_1 = labeling_v1_label_set_sync_service_pb2.SyncLabelSetsRequest()
            if not envelope_1.Unpack(outgoing_1):
                raise ValueError("partner envelope contains the wrong request type")
            response_1 = await deps.clients.labeling_label_set_sync.SyncLabelSets(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            callbacks_2: list[
                Callable[
                    [],
                    Awaitable[datasets_v1_dataset_version_calculation_service_pb2.CalculateDatasetVersionResponse]
                ]
            ] = []
            for item_2 in request.dataset_version.measurements:
                outgoing_2 = datasets_v1_dataset_version_calculation_service_pb2.CalculateDatasetVersionRequest(
                    context=request.context,
                    dataset_version=datasets_v1_datasets_pb2.DatasetVersion(
                        measurements=[
                            datasets_v1_datasets_pb2.DatasetVersionMeasurement(
                                metric=item_2.metric,
                                observed_at=item_2.observed_at
                            )
                        ]
                    )
                )
                async def send_2(
                    payload: datasets_v1_dataset_version_calculation_service_pb2.CalculateDatasetVersionRequest = outgoing_2
                ) -> datasets_v1_dataset_version_calculation_service_pb2.CalculateDatasetVersionResponse:
                    return await deps.clients.datasets_dataset_version_calculation.CalculateDatasetVersion(
                        payload,
                        timeout=deps.settings.timeout
                    )
                callbacks_2.append(send_2)
            for callback_2 in callbacks_2:
                response_2 = await callback_2()
            returned_0_0 = response_0.result.status
            if returned_0_0:
                response.result.status = returned_0_0
            returned_0_1 = response_0.consent_record.sequence
            if returned_0_1:
                response.dataset_version.sequence = returned_0_1
            returned_1_0 = response_1.result.details
            response.result.details.update(returned_1_0)
            returned_1_1 = response_1.outcome.status
            if returned_1_1:
                response.result.status = returned_1_1
            echoed_0 = request.dataset_version_id
            response.dataset_version.dataset_version_id = echoed_0
            echoed_1 = request.dataset_version.occurred_at
            response.dataset_version.occurred_at.CopyFrom(echoed_1)
            return response

    async def handle_submit_dataset_version(
        self,
        request: datasets_v1_dataset_version_approval_service_pb2.SubmitDatasetVersionRequest
    ) -> datasets_v1_dataset_version_approval_service_pb2.SubmitDatasetVersionResponse:
        """Submits a dataset version."""
        deps = self.deps
        response = datasets_v1_dataset_version_approval_service_pb2.SubmitDatasetVersionResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SubmitDatasetVersion', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'SubmitDatasetVersion', {'reason': request.reason})
            await deps.repository.save_dataset_version(request.context.tenant_id, request.dataset_version)
            response_0 = datasets_v1_dataset_validation_service_pb2.NormalizeDatasetResponse()
            response_1 = customers_v1_customer_service_pb2.UpdateCustomerResponse()
            response_2 = datasets_v1_data_schema_calculation_service_pb2.EstimateDataSchemaResponse()
            response_3 = datasets_v1_dataset_approval_service_pb2.RejectDatasetResponse()
            command_0 = DatasetVersionApprovalSubmitDatasetVersion0Command(
                context=request.context,
                dataset_owner_email=request.details.approver.email,
                details_contact_email=request.dataset_version.subject.email,
                dataset_owner_display_name=request.dataset_version.subject.display_name,
                annotations=dict(request.annotations)
            )
            outgoing_0 = to_dataset_version_approval_submit_dataset_version0_command(command_0)
            response_0 = await deps.clients.datasets_dataset_validation.NormalizeDataset(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = customers_v1_customer_service_pb2.UpdateCustomerRequest()
            outgoing_1.context.CopyFrom(request.context)
            if response_0.dataset.WhichOneof('locator') == 'address':
                outgoing_1.customer.primary_address.postal_code = response_0.dataset.address.postal_code
            outgoing_1.customer.contact.email = request.dataset_version.subject.email
            response_1 = await deps.clients.customers_customer.UpdateCustomer(outgoing_1, timeout=deps.settings.timeout)
            outgoing_2 = datasets_v1_data_schema_calculation_service_pb2.EstimateDataSchemaRequest(
                context=request.context,
                data_schema=datasets_v1_datasets_pb2.DataSchema(
                    children=[
                        datasets_v1_datasets_pb2.DataSchema(
                            children=[
                                datasets_v1_datasets_pb2.DataSchema(
                                    location=common_v1_address_pb2.PostalAddress(
                                        locality=response_0.dataset.address.locality
                                    ),
                                    manager=identity_v1_refs_pb2.UserRef(
                                        display_name=response_0.dataset.owner.display_name
                                    )
                                )
                            ]
                        )
                    ]
                )
            )
            send_2 = partial(
                deps.clients.datasets_data_schema_calculation.EstimateDataSchema,
                timeout=deps.settings.timeout
            )
            response_2 = await send_2(outgoing_2)
            async for item_3 in async_messages(request.dataset_version.measurements):
                outgoing_3 = datasets_v1_dataset_approval_service_pb2.RejectDatasetRequest(
                    context=request.context,
                    dataset=datasets_v1_datasets_pb2.Dataset(
                        audit=common_v1_audit_pb2.AuditInfo(created_at=response_2.data_schema.audit.created_at),
                        components={
                            'primary': datasets_v1_datasets_pb2.DatasetComponent(
                                description=response_0.dataset.components.get(
                                    'primary',
                                    datasets_v1_datasets_pb2.DatasetComponent()
                                ).description,
                                quantity=response_0.dataset.components.get(
                                    'primary',
                                    datasets_v1_datasets_pb2.DatasetComponent()
                                ).quantity
                            )
                        },
                        dimensions=datasets_v1_datasets_pb2.DatasetDimensions(unit=item_3.unit)
                    )
                )
                response_3 = await deps.clients.datasets_dataset_approval.RejectDataset(
                    outgoing_3,
                    timeout=deps.settings.timeout
                )
            returned_0_0 = response_0.result.correlation_id
            if returned_0_0:
                response.dataset_version.correlation_id = returned_0_0
            returned_0_1 = response_0.outcome.status
            if returned_0_1:
                response.result.status = returned_0_1
            returned_1_0 = response_1.result.details
            response.result.details.update(returned_1_0)
            returned_1_1 = response_1.result.status
            if returned_1_1:
                response.outcome.status = returned_1_1
            returned_2_0 = response_2.data_schema.manager.email
            if returned_2_0:
                response.dataset_version.subject.email = returned_2_0
            returned_2_1 = response_2.result.correlation_id
            if returned_2_1:
                response.result.correlation_id = returned_2_1
            echoed_0 = request.dataset_version_id
            response.dataset_version.dataset_version_id = echoed_0
            echoed_1 = request.dataset_version.kind
            response.dataset_version.kind = echoed_1
            return response
