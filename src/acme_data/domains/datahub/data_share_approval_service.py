"""Routes data shares through approval, with escalation and delegation."""

from __future__ import annotations

from collections.abc import AsyncIterator
from collections.abc import Awaitable
from collections.abc import Callable
from functools import partial
from typing import cast
import asyncio
import logging

from google.protobuf.any_pb2 import Any as AnyMessage
import grpc

from acme.analytics.v1 import (
    analytics_report_approval_service_pb2 as analytics_v1_analytics_report_approval_service_pb2,
)
from acme.analytics.v1 import funnel_approval_service_pb2 as analytics_v1_funnel_approval_service_pb2
from acme.authorization.v1 import (
    access_policy_validation_service_pb2 as authorization_v1_access_policy_validation_service_pb2,
)
from acme.authorization.v1 import authorization_pb2 as authorization_v1_authorization_pb2
from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.customers.v1 import customer_approval_service_pb2 as customers_v1_customer_approval_service_pb2
from acme.customers.v1 import customer_segment_import_service_pb2 as customers_v1_customer_segment_import_service_pb2
from acme.customers.v1 import customer_segment_sync_service_pb2 as customers_v1_customer_segment_sync_service_pb2
from acme.customers.v1 import customers_pb2 as customers_v1_customers_pb2
from acme.customers.v1 import household_reporting_service_pb2 as customers_v1_household_reporting_service_pb2
from acme.customers.v1 import preference_sync_service_pb2 as customers_v1_preference_sync_service_pb2
from acme.customers.v1 import refs_pb2 as customers_v1_refs_pb2
from acme.datahub.v1 import data_share_approval_service_pb2 as datahub_v1_data_share_approval_service_pb2
from acme.datahub.v1 import data_share_approval_service_pb2_grpc as datahub_v1_data_share_approval_service_pb2_grpc
from acme.datahub.v1 import data_share_validation_service_pb2 as datahub_v1_data_share_validation_service_pb2
from acme.datahub.v1 import datahub_pb2 as datahub_v1_datahub_pb2
from acme.datahub.v1 import notebook_approval_service_pb2 as datahub_v1_notebook_approval_service_pb2
from acme.datahub.v1 import refs_pb2 as datahub_v1_refs_pb2
from acme.datahub.v1 import workspace_approval_service_pb2 as datahub_v1_workspace_approval_service_pb2
from acme.datahub.v1 import workspace_approval_service_pb2_grpc as datahub_v1_workspace_approval_service_pb2_grpc
from acme.datasets.v1 import dataset_approval_service_pb2 as datasets_v1_dataset_approval_service_pb2
from acme.datasets.v1 import datasets_pb2 as datasets_v1_datasets_pb2
from acme.documents.v1 import document_service_pb2 as documents_v1_document_service_pb2
from acme.documents.v1 import documents_pb2 as documents_v1_documents_pb2
from acme.documents.v1 import refs_pb2 as documents_v1_refs_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.labeling.v1 import labeling_pb2 as labeling_v1_labeling_pb2
from acme.labeling.v1 import labeling_task_workflow_service_pb2 as labeling_v1_labeling_task_workflow_service_pb2
from acme.metrics.v1 import metric_series_history_service_pb2 as metrics_v1_metric_series_history_service_pb2

from acme_data.domains.datahub import hooks
from acme_data.domains.datahub.adapters import DataShareApprovalApproveDataShare2Adapter
from acme_data.domains.datahub.adapters import DataShareApprovalApproveDataShare2Port
from acme_data.domains.datahub.adapters import DataShareApprovalCommentDataShareApproval1Adapter
from acme_data.domains.datahub.adapters import DataShareApprovalSubmitDataShare1Adapter
from acme_data.domains.datahub.adapters import DataShareApprovalSubmitDataShare1Port
from acme_data.domains.datahub.dependencies import Dependencies
from acme_data.domains.datahub.models import DataShareApprovalRejectDataShare0Command
from acme_data.domains.datahub.models import DataShareApprovalRejectDataShare1Command
from acme_data.domains.datahub.models import to_data_share_approval_reject_data_share0_command
from acme_data.domains.datahub.models import to_data_share_approval_reject_data_share1_command
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_id
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class DataShareApprovalServicer(datahub_v1_data_share_approval_service_pb2_grpc.DataShareApprovalServiceServicer):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    async def ApproveDataShare(
        self, request: datahub_v1_data_share_approval_service_pb2.ApproveDataShareRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_data_share_approval_service_pb2.ApproveDataShareResponse:
        """Approves a data share."""
        return await self.handle_approve_data_share(request)

    @rpc_errors
    async def CommentDataShareApproval(
        self, request: datahub_v1_data_share_approval_service_pb2.CommentDataShareApprovalRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_data_share_approval_service_pb2.CommentDataShareApprovalResponse:
        """Comments a data share."""
        return await self.handle_comment_data_share_approval(request)

    @rpc_errors
    async def DelegateDataShareApproval(
        self, request: datahub_v1_data_share_approval_service_pb2.DelegateDataShareApprovalRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_data_share_approval_service_pb2.DelegateDataShareApprovalResponse:
        """Delegates a data share."""
        return await self.handle_delegate_data_share_approval(request)

    @rpc_errors
    async def EscalateDataShare(
        self, request: datahub_v1_data_share_approval_service_pb2.EscalateDataShareRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_data_share_approval_service_pb2.EscalateDataShareResponse:
        """Escalates a data share."""
        return await self.handle_escalate_data_share(request)

    @rpc_errors
    @retry_transient
    async def ListPendingDataShares(
        self, request: datahub_v1_data_share_approval_service_pb2.ListPendingDataSharesRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_data_share_approval_service_pb2.ListPendingDataSharesResponse:
        """Lists data shares a page at a time."""
        return await self.handle_list_pending_data_shares(request)

    @rpc_errors
    async def RecallDataShare(
        self, request: datahub_v1_data_share_approval_service_pb2.RecallDataShareRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_data_share_approval_service_pb2.RecallDataShareResponse:
        """Recalls a data share."""
        return await self.handle_recall_data_share(request)

    @rpc_errors
    async def RejectDataShare(
        self, request: datahub_v1_data_share_approval_service_pb2.RejectDataShareRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_data_share_approval_service_pb2.RejectDataShareResponse:
        """Rejects a data share."""
        return await self.handle_reject_data_share(request)

    @rpc_errors
    async def SubmitDataShare(
        self, request: datahub_v1_data_share_approval_service_pb2.SubmitDataShareRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_data_share_approval_service_pb2.SubmitDataShareResponse:
        """Submits a data share."""
        return await self.handle_submit_data_share(request)

    async def handle_approve_data_share(
        self,
        request: datahub_v1_data_share_approval_service_pb2.ApproveDataShareRequest
    ) -> datahub_v1_data_share_approval_service_pb2.ApproveDataShareResponse:
        """Approves a data share."""
        deps = self.deps
        response = datahub_v1_data_share_approval_service_pb2.ApproveDataShareResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ApproveDataShare', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'ApproveDataShare', {'reason': request.reason})
            await deps.repository.save_data_share(request.context.tenant_id, request.data_share)
            response_0 = datahub_v1_data_share_validation_service_pb2.ScoreDataShareResponse()
            response_1 = documents_v1_document_service_pb2.BatchCreateDocumentsResponse()
            response_2 = analytics_v1_analytics_report_approval_service_pb2.ListPendingAnalyticsReportsResponse()
            outgoing_0 = datahub_v1_data_share_validation_service_pb2.ScoreDataShareRequest(
                context=request.context,
                data_share=datahub_v1_datahub_pb2.DataShare(
                    billing_address=common_v1_address_pb2.PostalAddress(
                        lines=list(request.data_share.billing_address.lines)
                    ),
                    card=datahub_v1_datahub_pb2.DataShareCardSettlement(token=request.data_share.card.token),
                    counterparty=datahub_v1_refs_pb2.NotebookRef(
                        display_name=request.data_share.counterparty.display_name
                    )
                )
            )
            response_0 = await hooks.data_share_approval_approve_data_share0(
                deps.clients.datahub_data_share_validation,
                outgoing_0,
                deps.settings.timeout
            )
            outgoing_1 = documents_v1_document_service_pb2.BatchCreateDocumentsRequest(
                context=request.context,
                record=documents_v1_documents_pb2.Document(
                    audit=common_v1_audit_pb2.AuditInfo(updated_at=request.data_share.audit.updated_at),
                    billing_address=common_v1_address_pb2.PostalAddress(
                        postal_code=request.data_share.billing_address.postal_code
                    ),
                    counterparty=documents_v1_refs_pb2.DocumentFolderRef(
                        display_name=response_0.data_share.counterparty.display_name
                    )
                )
            )
            response_1 = await deps.clients.documents_document.BatchCreateDocuments(
                async_messages((outgoing_1,)),
                timeout=deps.settings.timeout
            )
            outgoing_2 = analytics_v1_analytics_report_approval_service_pb2.ListPendingAnalyticsReportsRequest(
                context=request.context,
                filter=analytics_v1_analytics_report_approval_service_pb2.ListPendingAnalyticsReportsRequest.Filter(
                    created_after=response_0.data_share.audit.created_at,
                    owner_id=response_0.data_share.data_share_id,
                    region=response_0.data_share.billing_address.region
                )
            )
            port_2: DataShareApprovalApproveDataShare2Port = DataShareApprovalApproveDataShare2Adapter(
                deps.clients.analytics_analytics_report_approval,
                deps.settings.timeout
            )
            response_2 = await port_2.execute(outgoing_2)
            returned_0_0 = response_0.data_share.total
            if returned_0_0.ListFields():
                response.data_share.total.MergeFrom(returned_0_0)
            returned_0_1 = response_0.result.details
            response.result.details.update(returned_0_1)
            returned_2_0 = response_2.result.status
            if returned_2_0:
                response.outcome.status = returned_2_0
            echoed_0 = request.data_share_id
            response.data_share.data_share_id = echoed_0
            echoed_1 = request.data_share.issued_at
            response.data_share.issued_at.CopyFrom(echoed_1)
            return response

    async def handle_comment_data_share_approval(
        self,
        request: datahub_v1_data_share_approval_service_pb2.CommentDataShareApprovalRequest
    ) -> datahub_v1_data_share_approval_service_pb2.CommentDataShareApprovalResponse:
        """Comments a data share."""
        deps = self.deps
        response = datahub_v1_data_share_approval_service_pb2.CommentDataShareApprovalResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CommentDataShareApproval', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'CommentDataShareApproval',
                {'reason': request.reason}
            )
            await deps.repository.save_data_share(request.context.tenant_id, request.data_share)
            response_0 = customers_v1_preference_sync_service_pb2.PullPreferencesResponse()
            response_1 = datahub_v1_notebook_approval_service_pb2.DelegateNotebookApprovalResponse()
            for item_0 in request.data_share.lines:
                outgoing_0 = customers_v1_preference_sync_service_pb2.PullPreferencesRequest(
                    context=request.context,
                    preference=customers_v1_customers_pb2.Preference(
                        description=item_0.description,
                        discount=customers_v1_customers_pb2.PreferenceDiscountAction(amount=item_0.tax.amount),
                        owner=identity_v1_refs_pb2.UserRef(email=request.details.approver.email)
                    )
                )
                response_0 = await deps.clients.customers_preference_sync.PullPreferences(
                    outgoing_0,
                    timeout=deps.settings.timeout
                )
            outgoing_1 = datahub_v1_notebook_approval_service_pb2.DelegateNotebookApprovalRequest(
                context=request.context,
                details=datahub_v1_notebook_approval_service_pb2.DelegateNotebookApprovalRequest.Details(
                    approver=identity_v1_refs_pb2.UserRef(display_name=request.data_share.counterparty.display_name)
                ),
                notebook=datahub_v1_datahub_pb2.Notebook(
                    counterparty=datahub_v1_refs_pb2.WorkspaceRef(display_name=response_0.preference.owner.display_name)
                )
            )
            response_1 = await DataShareApprovalCommentDataShareApproval1Adapter(
                deps.clients.datahub_notebook_approval,
                deps.settings.timeout
            )(outgoing_1)
            returned_1_0 = response_1.notebook.audit.updated_at
            if returned_1_0.ListFields():
                response.data_share.audit.updated_at.MergeFrom(returned_1_0)
            echoed_0 = request.data_share_id
            response.data_share.data_share_id = echoed_0
            echoed_1 = request.data_share.billing_address
            response.data_share.billing_address.CopyFrom(echoed_1)
            return response

    async def handle_delegate_data_share_approval(
        self,
        request: datahub_v1_data_share_approval_service_pb2.DelegateDataShareApprovalRequest
    ) -> datahub_v1_data_share_approval_service_pb2.DelegateDataShareApprovalResponse:
        """Delegates a data share."""
        deps = self.deps
        response = datahub_v1_data_share_approval_service_pb2.DelegateDataShareApprovalResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('DelegateDataShareApproval', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'DelegateDataShareApproval',
                {'reason': request.reason}
            )
            await deps.repository.save_data_share(request.context.tenant_id, request.data_share)
            response_0 = customers_v1_customer_segment_sync_service_pb2.ReconcileCustomerSegmentsResponse()
            response_1 = customers_v1_customer_segment_import_service_pb2.ImportCustomerSegmentsResponse()
            response_2 = analytics_v1_funnel_approval_service_pb2.CommentFunnelApprovalResponse()
            outgoing_0 = customers_v1_customer_segment_sync_service_pb2.ReconcileCustomerSegmentsRequest(
                context=request.context,
                customer_segment=customers_v1_customers_pb2.CustomerSegment(
                    audit=common_v1_audit_pb2.AuditInfo(etag=request.data_share.audit.etag)
                )
            )
            response_0 = cast(customers_v1_customer_segment_sync_service_pb2.ReconcileCustomerSegmentsResponse, await deps.bus.request(
                'acme.datahub.v1.DataShareApprovalService/DelegateDataShareApproval/0', outgoing_0, deps.settings.timeout,
            ))
            outgoing_1 = customers_v1_customer_segment_import_service_pb2.ImportCustomerSegmentsRequest(
                context=request.context,
                record=customers_v1_customers_pb2.CustomerSegment(
                    audit=common_v1_audit_pb2.AuditInfo(created_by=request.data_share.audit.created_by),
                    owner=identity_v1_refs_pb2.UserRef(user_id=response_0.customer_segment.owner.user_id)
                )
            )
            response_1 = await deps.clients.customers_customer_segment_import.ImportCustomerSegments(
                async_messages((outgoing_1,)),
                timeout=deps.settings.timeout
            )
            outgoing_2 = analytics_v1_funnel_approval_service_pb2.CommentFunnelApprovalRequest()
            outgoing_2.context.CopyFrom(request.context)
            outgoing_2.details.approver.email = request.details.approver.email
            outgoing_2.funnel.owner.display_name = response_0.customer_segment.owner.display_name
            if response_0.customer_segment.WhichOneof('action') == 'block':
                outgoing_2.funnel.block.reason = response_0.customer_segment.block.reason
            response_2 = await deps.clients.analytics_funnel_approval.CommentFunnelApproval(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.customer_segment.audit.created_at
            if returned_0_0.ListFields():
                response.data_share.audit.created_at.MergeFrom(returned_0_0)
            returned_2_0 = response_2.outcome.message
            if returned_2_0:
                response.result.message = returned_2_0
            echoed_0 = request.data_share_id
            response.data_share.data_share_id = echoed_0
            echoed_1 = request.data_share.issued_at
            response.data_share.issued_at.CopyFrom(echoed_1)
            return response

    async def handle_escalate_data_share(
        self,
        request: datahub_v1_data_share_approval_service_pb2.EscalateDataShareRequest
    ) -> datahub_v1_data_share_approval_service_pb2.EscalateDataShareResponse:
        """Escalates a data share."""
        deps = self.deps
        response = datahub_v1_data_share_approval_service_pb2.EscalateDataShareResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('EscalateDataShare', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'EscalateDataShare', {'reason': request.reason})
            await deps.repository.save_data_share(request.context.tenant_id, request.data_share)
            response_0 = customers_v1_customer_approval_service_pb2.RejectCustomerResponse()
            response_1 = datahub_v1_notebook_approval_service_pb2.ApproveNotebookResponse()
            outgoing_0 = customers_v1_customer_approval_service_pb2.RejectCustomerRequest(
                context=request.context,
                customer=customers_v1_customers_pb2.Customer(
                    passport=customers_v1_customers_pb2.CustomerPassport(number=request.data_share.counterparty.number),
                    primary_address=common_v1_address_pb2.PostalAddress(
                        recipient=request.data_share.billing_address.recipient
                    ),
                    relationship_manager=identity_v1_refs_pb2.UserRef(
                        display_name=request.details.approver.display_name
                    )
                ),
                details=customers_v1_customer_approval_service_pb2.RejectCustomerRequest.Details(
                    approver=identity_v1_refs_pb2.UserRef(email=request.details.approver.email)
                )
            )
            outgoing_1 = datahub_v1_notebook_approval_service_pb2.ApproveNotebookRequest(
                context=request.context,
                notebook=datahub_v1_datahub_pb2.Notebook(
                    card=datahub_v1_datahub_pb2.NotebookCardSettlement(network=request.data_share.card.network)
                )
            )
            response_0, response_1 = await asyncio.gather(
                deps.clients.customers_customer_approval.RejectCustomer(outgoing_0, timeout=deps.settings.timeout),
                deps.clients.datahub_notebook_approval.ApproveNotebook(outgoing_1, timeout=deps.settings.timeout),
            )
            returned_0_0 = response_0.result.correlation_id
            if returned_0_0:
                response.result.correlation_id = returned_0_0
            returned_0_1 = response_0.result.message
            if returned_0_1:
                response.result.message = returned_0_1
            returned_1_0 = response_1.notebook.audit.created_by
            if returned_1_0:
                response.data_share.audit.created_by = returned_1_0
            echoed_0 = request.data_share_id
            response.data_share.data_share_id = echoed_0
            echoed_1 = request.data_share.total
            response.data_share.total.CopyFrom(echoed_1)
            return response

    async def handle_list_pending_data_shares(
        self,
        request: datahub_v1_data_share_approval_service_pb2.ListPendingDataSharesRequest
    ) -> datahub_v1_data_share_approval_service_pb2.ListPendingDataSharesResponse:
        """Lists data shares a page at a time."""
        deps = self.deps
        response = datahub_v1_data_share_approval_service_pb2.ListPendingDataSharesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ListPendingDataShares', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ListPendingDataShares',
                {'order_by': request.order_by}
            )
            response_0 = labeling_v1_labeling_task_workflow_service_pb2.AdvanceLabelingTaskWorkflowResponse()
            outgoing_0 = labeling_v1_labeling_task_workflow_service_pb2.AdvanceLabelingTaskWorkflowRequest(
                context=request.context,
                labeling_task=labeling_v1_labeling_pb2.LabelingTask(
                    audit=common_v1_audit_pb2.AuditInfo(updated_at=request.filter.created_after),
                    requester=common_v1_contact_pb2.ContactInfo(email=request.context.actor.email)
                )
            )
            response_0 = await deps.clients.labeling_labeling_task_workflow.AdvanceLabelingTaskWorkflow(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.labeling_task.audit.updated_at
            returned_0_0_part_0 = response.data_shares.add()
            if returned_0_0.ListFields():
                returned_0_0_part_0.audit.updated_at.MergeFrom(returned_0_0)
            return response

    async def handle_recall_data_share(
        self,
        request: datahub_v1_data_share_approval_service_pb2.RecallDataShareRequest
    ) -> datahub_v1_data_share_approval_service_pb2.RecallDataShareResponse:
        """Recalls a data share."""
        deps = self.deps
        response = datahub_v1_data_share_approval_service_pb2.RecallDataShareResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('RecallDataShare', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'RecallDataShare', {'reason': request.reason})
            await deps.repository.save_data_share(request.context.tenant_id, request.data_share)
            response_0 = datahub_v1_workspace_approval_service_pb2.ApproveWorkspaceResponse()
            response_1 = authorization_v1_access_policy_validation_service_pb2.LintAccessPoliciesResponse()
            response_2 = datahub_v1_workspace_approval_service_pb2.SubmitWorkspaceResponse()
            outgoing_0 = datahub_v1_workspace_approval_service_pb2.ApproveWorkspaceRequest()
            outgoing_0.context.CopyFrom(request.context)
            outgoing_0.details.approver.display_name = request.data_share.counterparty.display_name
            outgoing_0.details.approver.user_id = request.details.approver.user_id
            outgoing_0.workspace.audit.etag = request.data_share.audit.etag
            outgoing_0.workspace.assignee.display_name = request.details.approver.display_name
            merged_0 = datahub_v1_workspace_approval_service_pb2.ApproveWorkspaceRequest()
            merged_0.MergeFrom(outgoing_0)
            outgoing_0.CopyFrom(merged_0)
            response_0 = await deps.clients.datahub_workspace_approval.ApproveWorkspace(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = authorization_v1_access_policy_validation_service_pb2.LintAccessPoliciesRequest(
                access_policy=authorization_v1_authorization_pb2.AccessPolicy(
                    audit=common_v1_audit_pb2.AuditInfo(created_by=request.data_share.audit.created_by)
                ),
                context=request.context
            )
            envelope_1 = AnyMessage()
            envelope_1.Pack(outgoing_1)
            outgoing_1 = authorization_v1_access_policy_validation_service_pb2.LintAccessPoliciesRequest()
            if not envelope_1.Unpack(outgoing_1):
                raise ValueError("partner envelope contains the wrong request type")
            response_1 = await deps.clients.authorization_access_policy_validation.LintAccessPolicies(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = datahub_v1_workspace_approval_service_pb2.SubmitWorkspaceRequest(
                context=request.context,
                workspace=datahub_v1_datahub_pb2.Workspace(
                    assignee=identity_v1_refs_pb2.UserRef(user_id=response_1.access_policy.owner.user_id),
                    customer=customers_v1_refs_pb2.CustomerRef(display_name=request.details.approver.display_name)
                )
            )
            registered_2 = cast(
                datahub_v1_workspace_approval_service_pb2_grpc.WorkspaceApprovalServiceStub,
                deps.clients.registry['acme.datahub.v1.WorkspaceApprovalService']
            )
            response_2 = await registered_2.SubmitWorkspace(outgoing_2, timeout=deps.settings.timeout)
            returned_0_0 = response_0.workspace.audit.etag
            if returned_0_0:
                response.data_share.audit.etag = returned_0_0
            returned_0_1 = response_0.outcome.message
            if returned_0_1:
                response.outcome.message = returned_0_1
            returned_1_0 = response_1.outcome.status
            if returned_1_0:
                response.result.status = returned_1_0
            returned_2_0 = response_2.workspace.assignee.display_name
            if returned_2_0:
                response.data_share.counterparty.display_name = returned_2_0
            returned_2_1 = response_2.workspace.audit.created_at
            if returned_2_1.ListFields():
                response.data_share.audit.created_at.MergeFrom(returned_2_1)
            echoed_0 = request.data_share_id
            response.data_share.data_share_id = echoed_0
            echoed_1 = request.data_share.number
            response.data_share.counterparty.number = echoed_1
            return response

    async def handle_reject_data_share(
        self,
        request: datahub_v1_data_share_approval_service_pb2.RejectDataShareRequest
    ) -> datahub_v1_data_share_approval_service_pb2.RejectDataShareResponse:
        """Rejects a data share."""
        deps = self.deps
        response = datahub_v1_data_share_approval_service_pb2.RejectDataShareResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('RejectDataShare', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'RejectDataShare', {'reason': request.reason})
            await deps.repository.save_data_share(request.context.tenant_id, request.data_share)
            response_0 = metrics_v1_metric_series_history_service_pb2.AnnotateMetricSeriesVersionResponse()
            response_1 = datasets_v1_dataset_approval_service_pb2.RecallDatasetResponse()
            response_2 = datahub_v1_workspace_approval_service_pb2.RecallWorkspaceResponse()
            response_3 = customers_v1_household_reporting_service_pb2.ListHouseholdReportsResponse()
            command_0 = DataShareApprovalRejectDataShare0Command(
                context=request.context,
                metric_series_owner_email=request.details.approver.email
            )
            outgoing_0 = to_data_share_approval_reject_data_share0_command(command_0)
            response_0 = await deps.clients.metrics_metric_series_history.AnnotateMetricSeriesVersion(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            command_1 = DataShareApprovalRejectDataShare1Command.model_validate(
                {
                    'context': request.context,
                    'dataset_owner_display_name': request.details.approver.display_name,
                    'dataset_address_recipient': response_0.metric_series.address.recipient
                }
            )
            outgoing_1 = to_data_share_approval_reject_data_share1_command(command_1)
            response_1 = await deps.clients.datasets_dataset_approval.RecallDataset(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = datahub_v1_workspace_approval_service_pb2.RecallWorkspaceRequest(
                context=request.context,
                details=datahub_v1_workspace_approval_service_pb2.RecallWorkspaceRequest.Details(
                    approver=identity_v1_refs_pb2.UserRef(email=request.details.approver.email)
                ),
                workspace=datahub_v1_datahub_pb2.Workspace(
                    assignee=identity_v1_refs_pb2.UserRef(user_id=request.details.approver.user_id),
                    requester=common_v1_contact_pb2.ContactInfo(email=response_1.dataset.owner.email)
                )
            )
            send_2 = partial(deps.clients.datahub_workspace_approval.RecallWorkspace, timeout=deps.settings.timeout)
            response_2 = await send_2(outgoing_2)
            outgoing_3 = customers_v1_household_reporting_service_pb2.ListHouseholdReportsRequest(
                context=request.context,
                filter=customers_v1_household_reporting_service_pb2.ListHouseholdReportsRequest.Filter(
                    created_after=response_2.workspace.audit.updated_at,
                    labels=dict(response_0.metric_series.specs),
                    owner_id=request.details.approver.user_id,
                    region=response_0.metric_series.address.region
                )
            )
            response_3 = await hooks.data_share_approval_reject_data_share3(
                deps.clients.customers_household_reporting,
                outgoing_3,
                deps.settings.timeout
            )
            returned_0_0 = response_0.metric_series.audit.etag
            if returned_0_0:
                response.data_share.audit.etag = returned_0_0
            returned_1_0 = response_1.dataset.components.get(
                'primary',
                datasets_v1_datasets_pb2.DatasetComponent()
            ).description
            returned_1_0_part_1 = response.data_share.lines.add()
            if returned_1_0:
                returned_1_0_part_1.description = returned_1_0
            returned_1_1 = response_1.outcome.next_steps
            response.outcome.next_steps.extend(returned_1_1)
            returned_2_0 = response_2.workspace.customer.display_name
            if returned_2_0:
                response.data_share.counterparty.display_name = returned_2_0
            returned_3_0 = response_3.result.details
            response.result.details.update(returned_3_0)
            returned_3_1 = response_3.result.message
            if returned_3_1:
                response.outcome.message = returned_3_1
            echoed_0 = request.data_share_id
            response.data_share.data_share_id = echoed_0
            echoed_1 = request.data_share.billing_address
            response.data_share.billing_address.CopyFrom(echoed_1)
            return response

    async def handle_submit_data_share(
        self,
        request: datahub_v1_data_share_approval_service_pb2.SubmitDataShareRequest
    ) -> datahub_v1_data_share_approval_service_pb2.SubmitDataShareResponse:
        """Submits a data share."""
        deps = self.deps
        response = datahub_v1_data_share_approval_service_pb2.SubmitDataShareResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SubmitDataShare', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'SubmitDataShare', {'reason': request.reason})
            await deps.repository.save_data_share(request.context.tenant_id, request.data_share)
            response_0 = datahub_v1_data_share_validation_service_pb2.ValidateDataShareResponse()
            response_1 = datahub_v1_workspace_approval_service_pb2.EscalateWorkspaceResponse()
            response_2 = documents_v1_document_service_pb2.BatchCreateDocumentsResponse()
            outgoing_0 = datahub_v1_data_share_validation_service_pb2.ValidateDataShareRequest()
            outgoing_0.context.CopyFrom(request.context)
            outgoing_0.data_share.card.network = request.data_share.card.network
            outgoing_0.data_share.card.last4 = request.data_share.card.last4
            outgoing_0.data_share.card.holder_name = request.data_share.card.holder_name
            outgoing_0.context.tenant_id = tenant_id.get()
            response_0 = await deps.clients.datahub_data_share_validation.ValidateDataShare(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = datahub_v1_workspace_approval_service_pb2.EscalateWorkspaceRequest(
                context=request.context,
                details=datahub_v1_workspace_approval_service_pb2.EscalateWorkspaceRequest.Details(
                    approver=identity_v1_refs_pb2.UserRef(display_name=request.data_share.counterparty.display_name)
                ),
                workspace=datahub_v1_datahub_pb2.Workspace(
                    audit=common_v1_audit_pb2.AuditInfo(
                        created_at=request.data_share.audit.created_at,
                        updated_by=request.data_share.audit.updated_by
                    ),
                    customer=customers_v1_refs_pb2.CustomerRef(email=request.details.approver.email)
                )
            )
            port_1: DataShareApprovalSubmitDataShare1Port = DataShareApprovalSubmitDataShare1Adapter(
                deps.clients.datahub_workspace_approval,
                deps.settings.timeout
            )
            response_1 = await port_1.execute(outgoing_1)
            outgoing_2 = documents_v1_document_service_pb2.BatchCreateDocumentsRequest(
                context=request.context,
                record=documents_v1_documents_pb2.Document(
                    audit=common_v1_audit_pb2.AuditInfo(created_at=request.data_share.audit.created_at),
                    billing_address=common_v1_address_pb2.PostalAddress(
                        country_code=request.data_share.billing_address.country_code
                    ),
                    counterparty=documents_v1_refs_pb2.DocumentFolderRef(
                        display_name=response_1.workspace.assignee.display_name
                    )
                )
            )
            response_2 = await deps.clients.documents_document.BatchCreateDocuments(
                async_messages((outgoing_2,)),
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.result.message = returned_0_0
            returned_0_1 = response_0.data_share.counterparty
            if returned_0_1.ListFields():
                response.data_share.counterparty.MergeFrom(returned_0_1)
            returned_1_0 = response_1.outcome.status
            if returned_1_0:
                response.outcome.status = returned_1_0
            returned_1_1 = response_1.result.reference_ids
            response.result.reference_ids.extend(returned_1_1)
            echoed_0 = request.data_share_id
            response.data_share.data_share_id = echoed_0
            echoed_1 = request.data_share.issued_at
            response.data_share.issued_at.CopyFrom(echoed_1)
            return response
