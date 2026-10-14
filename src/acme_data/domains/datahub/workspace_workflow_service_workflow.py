"""Application workflow for Workspace Workflow."""

from __future__ import annotations

from collections.abc import Awaitable
from collections.abc import Callable
from typing import Any
from typing import cast
import asyncio
import logging

from google.protobuf.any_pb2 import Any as AnyMessage
from google.protobuf.json_format import MessageToJson
from google.protobuf.json_format import Parse

from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.customers.v1 import consent_record_sync_service_pb2 as customers_v1_consent_record_sync_service_pb2
from acme.customers.v1 import consent_record_workflow_service_pb2 as customers_v1_consent_record_workflow_service_pb2
from acme.customers.v1 import customers_pb2 as customers_v1_customers_pb2
from acme.customers.v1 import household_workflow_service_pb2 as customers_v1_household_workflow_service_pb2
from acme.customers.v1 import refs_pb2 as customers_v1_refs_pb2
from acme.datahub.v1 import data_share_approval_service_pb2 as datahub_v1_data_share_approval_service_pb2
from acme.datahub.v1 import data_share_validation_service_pb2 as datahub_v1_data_share_validation_service_pb2
from acme.datahub.v1 import datahub_pb2 as datahub_v1_datahub_pb2
from acme.datahub.v1 import notebook_reporting_service_pb2 as datahub_v1_notebook_reporting_service_pb2
from acme.datahub.v1 import workspace_approval_service_pb2 as datahub_v1_workspace_approval_service_pb2
from acme.datahub.v1 import workspace_workflow_service_pb2 as datahub_v1_workspace_workflow_service_pb2
from acme.edgegateway.v1 import route_binding_service_pb2 as edgegateway_v1_route_binding_service_pb2
from acme.featureflags.v1 import feature_flag_service_pb2 as featureflags_v1_feature_flag_service_pb2
from acme.featureflags.v1 import featureflags_pb2 as featureflags_v1_featureflags_pb2
from acme.featurestore.v1 import feature_view_workflow_service_pb2 as featurestore_v1_feature_view_workflow_service_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.ledger.v1 import ledger_account_query_service_pb2 as ledger_v1_ledger_account_query_service_pb2
from acme.ledger.v1 import ledger_account_service_pb2 as ledger_v1_ledger_account_service_pb2
from acme.modelregistry.v1 import deployment_import_service_pb2 as modelregistry_v1_deployment_import_service_pb2
from acme.pricing.v1 import price_list_query_service_pb2 as pricing_v1_price_list_query_service_pb2

from acme_data.domains.datahub.adapters import WorkspaceWorkflowResumeWorkspaceWorkflow2Adapter
from acme_data.domains.datahub.adapters import WorkspaceWorkflowResumeWorkspaceWorkflow2Port
from acme_data.domains.datahub.dependencies import Dependencies
from acme_data.platform.rpc import async_messages
from acme_data.platform.tenancy import tenant_id
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class WorkspaceWorkflowServicerWorkflow:
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    async def handle_advance_workspace_workflow(
        self,
        request: datahub_v1_workspace_workflow_service_pb2.AdvanceWorkspaceWorkflowRequest
    ) -> datahub_v1_workspace_workflow_service_pb2.AdvanceWorkspaceWorkflowResponse:
        """Advances a workspace."""
        deps = self.deps
        response = datahub_v1_workspace_workflow_service_pb2.AdvanceWorkspaceWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('AdvanceWorkspaceWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'AdvanceWorkspaceWorkflow',
                {'reason': request.reason}
            )
            await deps.repository.save_workspace(request.context.tenant_id, request.workspace)
            response_0 = datahub_v1_workspace_approval_service_pb2.EscalateWorkspaceResponse()
            response_1 = customers_v1_consent_record_workflow_service_pb2.ResumeConsentRecordWorkflowResponse()
            response_2 = ledger_v1_ledger_account_service_pb2.CloneLedgerAccountResponse()
            outgoing_0 = datahub_v1_workspace_approval_service_pb2.EscalateWorkspaceRequest(
                context=request.context,
                workspace=datahub_v1_datahub_pb2.Workspace(
                    audit=common_v1_audit_pb2.AuditInfo(etag=request.workspace.audit.etag),
                    customer=customers_v1_refs_pb2.CustomerRef(
                        display_name=request.workspace.assignee.display_name,
                        email=request.details.notify.email
                    ),
                    requester=common_v1_contact_pb2.ContactInfo(name=request.workspace.requester.name)
                )
            )
            response_0 = await deps.clients.datahub_workspace_approval.EscalateWorkspace(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = customers_v1_consent_record_workflow_service_pb2.ResumeConsentRecordWorkflowRequest(
                consent_record=customers_v1_customers_pb2.ConsentRecord(
                    subject=customers_v1_refs_pb2.HouseholdRef(display_name=response_0.workspace.customer.display_name)
                ),
                context=request.context,
                details=customers_v1_consent_record_workflow_service_pb2.ResumeConsentRecordWorkflowRequest.Details(
                    notify=common_v1_contact_pb2.ContactInfo(email=request.workspace.assignee.email)
                )
            )
            method_name_1 = 'ResumeConsentRecordWorkflow'
            response_1 = await getattr(
                deps.clients.customers_consent_record_workflow,
                method_name_1
            )(outgoing_1, timeout=deps.settings.timeout)
            outgoing_2 = ledger_v1_ledger_account_service_pb2.CloneLedgerAccountRequest()
            outgoing_2.context.CopyFrom(request.context)
            outgoing_2.ledger_account.contact.email = response_0.workspace.requester.email
            if request.workspace.WhichOneof('origin') == 'customer':
                outgoing_2.ledger_account.holder.display_name = request.workspace.customer.display_name
            response_2 = await deps.clients.ledger_ledger_account.CloneLedgerAccount(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.workspace.audit.etag
            if returned_0_0:
                response.workspace.audit.etag = returned_0_0
            returned_1_0 = response_1.consent_record.subject.display_name
            if returned_1_0:
                response.workspace.assignee.display_name = returned_1_0
            returned_2_0 = response_2.ledger_account.contact.email
            if returned_2_0:
                response.workspace.requester.email = returned_2_0
            echoed_0 = request.workspace_id
            response.workspace.workspace_id = echoed_0
            echoed_1 = request.workspace.subject
            response.workspace.subject = echoed_1
            return response

    async def handle_cancel_workspace_workflow(
        self,
        request: datahub_v1_workspace_workflow_service_pb2.CancelWorkspaceWorkflowRequest
    ) -> datahub_v1_workspace_workflow_service_pb2.CancelWorkspaceWorkflowResponse:
        """Cancels a workspace."""
        deps = self.deps
        response = datahub_v1_workspace_workflow_service_pb2.CancelWorkspaceWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CancelWorkspaceWorkflow', extra={'fields': {'initiated_by': request.details.initiated_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'CancelWorkspaceWorkflow',
                {'initiated_by': request.details.initiated_by}
            )
            await deps.repository.save_workspace(request.context.tenant_id, request.workspace)
            response_0 = ledger_v1_ledger_account_query_service_pb2.FindLedgerAccountsResponse()
            response_1 = modelregistry_v1_deployment_import_service_pb2.ListDeploymentImportsResponse()
            response_2 = datahub_v1_workspace_approval_service_pb2.DelegateWorkspaceApprovalResponse()
            response_3 = datahub_v1_notebook_reporting_service_pb2.ScheduleNotebookReportResponse()
            outgoing_0 = ledger_v1_ledger_account_query_service_pb2.FindLedgerAccountsRequest(
                context=request.context,
                filter=ledger_v1_ledger_account_query_service_pb2.FindLedgerAccountsRequest.Filter(
                    created_after=request.workspace.sla.due_at,
                    labels=dict(request.details.parameters),
                    owner_id=request.workspace.assignee.user_id
                )
            )
            outgoing_2 = datahub_v1_workspace_approval_service_pb2.DelegateWorkspaceApprovalRequest(
                context=request.context,
                details=datahub_v1_workspace_approval_service_pb2.DelegateWorkspaceApprovalRequest.Details(
                    approver=identity_v1_refs_pb2.UserRef(email=request.details.notify.email)
                ),
                workspace=datahub_v1_datahub_pb2.Workspace(
                    assignee=identity_v1_refs_pb2.UserRef(email=request.workspace.requester.email),
                    audit=common_v1_audit_pb2.AuditInfo(created_by=request.workspace.audit.created_by),
                    customer=customers_v1_refs_pb2.CustomerRef(email=request.workspace.customer.email)
                )
            )
            response_0, response_2 = await asyncio.gather(
                deps.clients.ledger_ledger_account_query.FindLedgerAccounts(outgoing_0, timeout=deps.settings.timeout),
                deps.clients.datahub_workspace_approval.DelegateWorkspaceApproval(
                    outgoing_2,
                    timeout=deps.settings.timeout
                ),
            )
            outgoing_1 = modelregistry_v1_deployment_import_service_pb2.ListDeploymentImportsRequest(
                context=request.context,
                filter=modelregistry_v1_deployment_import_service_pb2.ListDeploymentImportsRequest.Filter(
                    created_after=request.workspace.sla.due_at,
                    labels=dict(response_0.result.details),
                    owner_id=request.workspace.sla.policy_id
                )
            )
            document_1 = MessageToJson(outgoing_1, preserving_proto_field_name=True)
            outgoing_1 = Parse(
                document_1,
                modelregistry_v1_deployment_import_service_pb2.ListDeploymentImportsRequest()
            )
            response_1 = await deps.clients.modelregistry_deployment_import.ListDeploymentImports(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_3 = datahub_v1_notebook_reporting_service_pb2.ScheduleNotebookReportRequest(
                annotations=dict(request.annotations),
                context=request.context,
                details=datahub_v1_notebook_reporting_service_pb2.ScheduleNotebookReportRequest.Details(
                    filters=dict(response_2.result.details)
                ),
                reason=request.reason
            )
            envelope_3 = AnyMessage()
            envelope_3.Pack(outgoing_3)
            outgoing_3 = datahub_v1_notebook_reporting_service_pb2.ScheduleNotebookReportRequest()
            if not envelope_3.Unpack(outgoing_3):
                raise ValueError("partner envelope contains the wrong request type")
            response_3 = await deps.clients.datahub_notebook_reporting.ScheduleNotebookReport(
                outgoing_3,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_0)
            returned_0_1 = response_0.result.details
            response.result.details.update(returned_0_1)
            returned_1_0 = response_1.result.status
            if returned_1_0:
                response.outcome.status = returned_1_0
            returned_2_0 = response_2.workspace.audit.created_by
            if returned_2_0:
                response.workspace.audit.created_by = returned_2_0
            returned_3_0 = response_3.result.reference_ids
            response.result.reference_ids.extend(returned_3_0)
            echoed_0 = request.workspace_id
            response.workspace.workspace_id = echoed_0
            echoed_1 = request.workspace.subject
            response.workspace.subject = echoed_1
            return response

    async def handle_inspect_workspace_workflow(
        self,
        request: datahub_v1_workspace_workflow_service_pb2.InspectWorkspaceWorkflowRequest
    ) -> datahub_v1_workspace_workflow_service_pb2.InspectWorkspaceWorkflowResponse:
        """Returns a workspace."""
        deps = self.deps
        response = datahub_v1_workspace_workflow_service_pb2.InspectWorkspaceWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('InspectWorkspaceWorkflow', extra={'fields': {'locale': request.context.locale}})
            await deps.repository.audit(
                request.context.tenant_id,
                'InspectWorkspaceWorkflow',
                {'locale': request.context.locale}
            )
            echoed_0 = request.workspace_id
            response.workspace.workspace_id = echoed_0
            return response

    async def handle_list_workspace_workflows(
        self,
        request: datahub_v1_workspace_workflow_service_pb2.ListWorkspaceWorkflowsRequest
    ) -> datahub_v1_workspace_workflow_service_pb2.ListWorkspaceWorkflowsResponse:
        """Lists workspaces a page at a time."""
        deps = self.deps
        response = datahub_v1_workspace_workflow_service_pb2.ListWorkspaceWorkflowsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ListWorkspaceWorkflows', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ListWorkspaceWorkflows',
                {'order_by': request.order_by}
            )
            response_0 = datahub_v1_workspace_approval_service_pb2.DelegateWorkspaceApprovalResponse()
            outgoing_0 = datahub_v1_workspace_approval_service_pb2.DelegateWorkspaceApprovalRequest(
                context=request.context,
                details=datahub_v1_workspace_approval_service_pb2.DelegateWorkspaceApprovalRequest.Details(
                    approver=identity_v1_refs_pb2.UserRef(
                        email=request.context.actor.email,
                        user_id=request.context.actor.user_id
                    )
                ),
                workspace=datahub_v1_datahub_pb2.Workspace(
                    audit=common_v1_audit_pb2.AuditInfo(created_at=request.filter.created_after)
                )
            )
            response_0 = await deps.clients.datahub_workspace_approval.DelegateWorkspaceApproval(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.workspace.assignee.user_id
            returned_0_0_part_0 = response.workspaces.add()
            if returned_0_0:
                returned_0_0_part_0.assignee.user_id = returned_0_0
            returned_0_1 = response_0.result.message
            if returned_0_1:
                response.result.message = returned_0_1
            return response

    async def handle_pause_workspace_workflow(
        self,
        request: datahub_v1_workspace_workflow_service_pb2.PauseWorkspaceWorkflowRequest
    ) -> datahub_v1_workspace_workflow_service_pb2.PauseWorkspaceWorkflowResponse:
        """Pauses a workspace."""
        deps = self.deps
        response = datahub_v1_workspace_workflow_service_pb2.PauseWorkspaceWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('PauseWorkspaceWorkflow', extra={'fields': {'initiated_by': request.details.initiated_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'PauseWorkspaceWorkflow',
                {'initiated_by': request.details.initiated_by}
            )
            await deps.repository.save_workspace(request.context.tenant_id, request.workspace)
            response_0 = datahub_v1_notebook_reporting_service_pb2.ScheduleNotebookReportResponse()
            response_1 = datahub_v1_workspace_approval_service_pb2.ApproveWorkspaceResponse()
            response_2 = customers_v1_household_workflow_service_pb2.ResumeHouseholdWorkflowResponse()
            outgoing_0 = datahub_v1_notebook_reporting_service_pb2.ScheduleNotebookReportRequest(
                annotations=dict(request.annotations),
                context=request.context,
                details=datahub_v1_notebook_reporting_service_pb2.ScheduleNotebookReportRequest.Details(
                    filters=dict(request.details.parameters)
                ),
                reason=request.reason
            )
            outgoing_2 = customers_v1_household_workflow_service_pb2.ResumeHouseholdWorkflowRequest(
                context=request.context,
                household=customers_v1_customers_pb2.Household(
                    children=[
                        customers_v1_customers_pb2.Household(
                            children=[
                                customers_v1_customers_pb2.Household(
                                    audit=common_v1_audit_pb2.AuditInfo(updated_at=request.workspace.audit.updated_at)
                                )
                            ]
                        )
                    ]
                )
            )
            response_0, response_2 = await asyncio.gather(
                deps.clients.datahub_notebook_reporting.ScheduleNotebookReport(
                    outgoing_0,
                    timeout=deps.settings.timeout
                ),
                deps.clients.customers_household_workflow.ResumeHouseholdWorkflow(
                    outgoing_2,
                    timeout=deps.settings.timeout
                ),
            )
            callbacks_1: list[
                Callable[[], Awaitable[datahub_v1_workspace_approval_service_pb2.ApproveWorkspaceResponse]]
            ] = []
            for item_1 in request.workspace.history:
                outgoing_1 = datahub_v1_workspace_approval_service_pb2.ApproveWorkspaceRequest(
                    context=request.context,
                    workspace=datahub_v1_datahub_pb2.Workspace(
                        history=[
                            datahub_v1_datahub_pb2.WorkspaceStatusChange(
                                changed_at=item_1.changed_at,
                                changed_by=item_1.changed_by,
                                from_status=item_1.from_status,
                                to_status=item_1.to_status
                            )
                        ]
                    )
                )
                async def send_1(
                    payload: datahub_v1_workspace_approval_service_pb2.ApproveWorkspaceRequest = outgoing_1
                ) -> datahub_v1_workspace_approval_service_pb2.ApproveWorkspaceResponse:
                    return await deps.clients.datahub_workspace_approval.ApproveWorkspace(
                        payload,
                        timeout=deps.settings.timeout
                    )
                callbacks_1.append(send_1)
            for callback_1 in callbacks_1:
                response_1 = await callback_1()
            returned_0_0 = response_0.result.correlation_id
            if returned_0_0:
                response.result.correlation_id = returned_0_0
            returned_0_1 = response_0.result.status
            if returned_0_1:
                response.outcome.status = returned_0_1
            returned_2_0 = response_2.household.manager.display_name
            if returned_2_0:
                response.workspace.assignee.display_name = returned_2_0
            returned_2_1 = response_2.outcome.status
            if returned_2_1:
                response.result.status = returned_2_1
            echoed_0 = request.workspace_id
            response.workspace.workspace_id = echoed_0
            echoed_1 = request.workspace.priority
            response.workspace.priority = echoed_1
            return response

    async def handle_resume_workspace_workflow(
        self,
        request: datahub_v1_workspace_workflow_service_pb2.ResumeWorkspaceWorkflowRequest
    ) -> datahub_v1_workspace_workflow_service_pb2.ResumeWorkspaceWorkflowResponse:
        """Resumes a workspace."""
        deps = self.deps
        response = datahub_v1_workspace_workflow_service_pb2.ResumeWorkspaceWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ResumeWorkspaceWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ResumeWorkspaceWorkflow',
                {'reason': request.reason}
            )
            await deps.repository.save_workspace(request.context.tenant_id, request.workspace)
            response_0 = featureflags_v1_feature_flag_service_pb2.CloneFeatureFlagResponse()
            response_1 = pricing_v1_price_list_query_service_pb2.SuggestPriceListsResponse()
            response_2 = datahub_v1_data_share_approval_service_pb2.SubmitDataShareResponse()
            response_3 = datahub_v1_workspace_approval_service_pb2.EscalateWorkspaceResponse()
            async for item_0 in async_messages(request.workspace.comments):
                outgoing_0 = featureflags_v1_feature_flag_service_pb2.CloneFeatureFlagRequest(
                    context=request.context,
                    feature_flag=featureflags_v1_featureflags_pb2.FeatureFlag(
                        audit=common_v1_audit_pb2.AuditInfo(
                            created_at=item_0.created_at,
                            etag=request.workspace.audit.etag
                        ),
                        block=featureflags_v1_featureflags_pb2.FeatureFlagBlockAction(notify_email=item_0.author_email),
                        owner=identity_v1_refs_pb2.UserRef(email=request.workspace.requester.email)
                    )
                )
                response_0 = await deps.clients.featureflags_feature_flag.CloneFeatureFlag(
                    outgoing_0,
                    timeout=deps.settings.timeout
                )
            outgoing_1 = pricing_v1_price_list_query_service_pb2.SuggestPriceListsRequest()
            outgoing_1.context.CopyFrom(request.context)
            outgoing_1.filter.created_after.CopyFrom(response_0.feature_flag.audit.created_at)
            outgoing_1.context.tenant_id = tenant_id.get()
            response_1 = await deps.clients.pricing_price_list_query.SuggestPriceLists(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = datahub_v1_data_share_approval_service_pb2.SubmitDataShareRequest(
                context=request.context,
                data_share=datahub_v1_datahub_pb2.DataShare(
                    audit=common_v1_audit_pb2.AuditInfo(updated_by=request.workspace.audit.updated_by),
                    lines=[
                        datahub_v1_datahub_pb2.DataShareLine(
                            tax=datahub_v1_datahub_pb2.DataShareLineTax(amount=response_0.feature_flag.discount.amount)
                        )
                    ]
                ),
                details=datahub_v1_data_share_approval_service_pb2.SubmitDataShareRequest.Details(
                    approver=identity_v1_refs_pb2.UserRef(user_id=response_0.feature_flag.owner.user_id)
                )
            )
            port_2: WorkspaceWorkflowResumeWorkspaceWorkflow2Port = WorkspaceWorkflowResumeWorkspaceWorkflow2Adapter(
                deps.clients.datahub_data_share_approval,
                deps.settings.timeout
            )
            response_2 = await port_2.execute(outgoing_2)
            outgoing_3 = datahub_v1_workspace_approval_service_pb2.EscalateWorkspaceRequest()
            outgoing_3.context.CopyFrom(request.context)
            outgoing_3.details.approver.display_name = response_2.data_share.counterparty.display_name
            if request.workspace.WhichOneof('origin') == 'customer':
                outgoing_3.workspace.customer.email = request.workspace.customer.email
            outgoing_3.details.approver.user_id = request.workspace.assignee.user_id
            outgoing_3.details.approver.email = response_0.feature_flag.owner.email
            response_3 = await deps.clients.datahub_workspace_approval.EscalateWorkspace(
                outgoing_3,
                timeout=deps.settings.timeout
            )
            returned_1_0 = response_1.result.reference_ids
            response.result.reference_ids.extend(returned_1_0)
            returned_1_1 = response_1.result.correlation_id
            if returned_1_1:
                response.result.correlation_id = returned_1_1
            returned_2_0 = response_2.result.reference_ids
            response.result.reference_ids.extend(returned_2_0)
            returned_2_1 = response_2.data_share.audit.created_at
            returned_2_1_part_1 = response.workspace.comments.add()
            if returned_2_1.ListFields():
                returned_2_1_part_1.created_at.MergeFrom(returned_2_1)
            returned_3_0 = response_3.workspace.audit.updated_at
            if returned_3_0.ListFields():
                response.workspace.audit.updated_at.MergeFrom(returned_3_0)
            returned_3_1 = response_3.workspace.audit.created_by
            if returned_3_1:
                response.workspace.audit.created_by = returned_3_1
            echoed_0 = request.workspace_id
            response.workspace.workspace_id = echoed_0
            echoed_1 = request.workspace.priority
            response.workspace.priority = echoed_1
            return response

    async def handle_retry_workspace_workflow(
        self,
        request: datahub_v1_workspace_workflow_service_pb2.RetryWorkspaceWorkflowRequest
    ) -> datahub_v1_workspace_workflow_service_pb2.RetryWorkspaceWorkflowResponse:
        """Retrys a workspace."""
        deps = self.deps
        response = datahub_v1_workspace_workflow_service_pb2.RetryWorkspaceWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('RetryWorkspaceWorkflow', extra={'fields': {'initiated_by': request.details.initiated_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'RetryWorkspaceWorkflow',
                {'initiated_by': request.details.initiated_by}
            )
            await deps.repository.save_workspace(request.context.tenant_id, request.workspace)
            response_0 = datahub_v1_workspace_approval_service_pb2.ApproveWorkspaceResponse()
            response_1 = customers_v1_consent_record_sync_service_pb2.PushConsentRecordResponse()
            response_2 = ledger_v1_ledger_account_service_pb2.ListLedgerAccountsResponse()
            for item_0 in request.workspace.comments:
                outgoing_0 = datahub_v1_workspace_approval_service_pb2.ApproveWorkspaceRequest(
                    context=request.context,
                    workspace=datahub_v1_datahub_pb2.Workspace(
                        comments=[
                            datahub_v1_datahub_pb2.WorkspaceComment(author_email=item_0.author_email, body=item_0.body)
                        ]
                    )
                )
                response_0 = await deps.clients.datahub_workspace_approval.ApproveWorkspace(
                    outgoing_0,
                    timeout=deps.settings.timeout
                )
            outgoing_1 = customers_v1_consent_record_sync_service_pb2.PushConsentRecordRequest(
                consent_record=customers_v1_customers_pb2.ConsentRecord(
                    correlation_id=response_0.result.correlation_id,
                    measurements=[
                        customers_v1_customers_pb2.ConsentRecordMeasurement(
                            observed_at=response_0.workspace.audit.created_at
                        )
                    ],
                    subject=customers_v1_refs_pb2.HouseholdRef(display_name=response_0.workspace.assignee.display_name)
                ),
                context=request.context,
                reason=request.reason
            )
            response_1 = cast(customers_v1_consent_record_sync_service_pb2.PushConsentRecordResponse, await deps.bus.request(
                'acme.datahub.v1.WorkspaceWorkflowService/RetryWorkspaceWorkflow/1', outgoing_1, deps.settings.timeout,
            ))
            outgoing_2 = ledger_v1_ledger_account_service_pb2.ListLedgerAccountsRequest()
            outgoing_2.context.CopyFrom(request.context)
            outgoing_2.filter.created_after.CopyFrom(response_0.workspace.sla.due_at)
            if request.workspace.WhichOneof('origin') == 'customer':
                outgoing_2.filter.owner_id = request.workspace.customer.customer_id
            outgoing_2.filter.labels.update(dict(response_1.result.details))
            response_2 = await deps.clients.ledger_ledger_account.ListLedgerAccounts(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            returned_1_0 = response_1.consent_record.correlation_id
            if returned_1_0:
                response.result.correlation_id = returned_1_0
            returned_2_0 = response_2.result.reference_ids
            response.result.reference_ids.extend(returned_2_0)
            returned_2_1 = response_2.result.status
            if returned_2_1:
                response.outcome.status = returned_2_1
            echoed_0 = request.workspace_id
            response.workspace.workspace_id = echoed_0
            echoed_1 = request.workspace.subject
            response.workspace.subject = echoed_1
            return response

    async def handle_signal_workspace_workflow(
        self,
        request: datahub_v1_workspace_workflow_service_pb2.SignalWorkspaceWorkflowRequest
    ) -> datahub_v1_workspace_workflow_service_pb2.SignalWorkspaceWorkflowResponse:
        """Signals a workspace."""
        deps = self.deps
        response = datahub_v1_workspace_workflow_service_pb2.SignalWorkspaceWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SignalWorkspaceWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'SignalWorkspaceWorkflow',
                {'reason': request.reason}
            )
            await deps.repository.save_workspace(request.context.tenant_id, request.workspace)
            response_0 = datahub_v1_data_share_validation_service_pb2.CheckDataShareEligibilityResponse()
            response_1 = datahub_v1_workspace_approval_service_pb2.EscalateWorkspaceResponse()
            outgoing_0 = datahub_v1_data_share_validation_service_pb2.CheckDataShareEligibilityRequest(
                context=request.context,
                details=datahub_v1_data_share_validation_service_pb2.CheckDataShareEligibilityRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(
                        email=request.details.notify.email,
                        preferred_channel=request.details.notify.preferred_channel
                    )
                )
            )
            method_name_0 = 'CheckDataShareEligibility'
            response_0 = await getattr(
                deps.clients.datahub_data_share_validation,
                method_name_0
            )(outgoing_0, timeout=deps.settings.timeout)
            fields_1: dict[str, Any] = {
                'context': request.context,
                'workspace': {
                    'audit': {'updated_at': response_0.data_share.audit.updated_at},
                    'comments': [{'created_at': response_0.data_share.audit.created_at}],
                    'customer': {'customer_id': request.workspace.customer.customer_id},
                    'requester': {'email': request.workspace.customer.email}
                }
            }
            outgoing_1 = datahub_v1_workspace_approval_service_pb2.EscalateWorkspaceRequest(**fields_1)
            response_1 = await deps.clients.datahub_workspace_approval.EscalateWorkspace(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.data_share.audit.created_at
            if returned_0_0.ListFields():
                response.workspace.audit.created_at.MergeFrom(returned_0_0)
            returned_1_0 = response_1.outcome.next_steps
            response.outcome.next_steps.extend(returned_1_0)
            echoed_0 = request.workspace_id
            response.workspace.workspace_id = echoed_0
            echoed_1 = request.workspace.priority
            response.workspace.priority = echoed_1
            return response

    async def handle_start_workspace_workflow(
        self,
        request: datahub_v1_workspace_workflow_service_pb2.StartWorkspaceWorkflowRequest
    ) -> datahub_v1_workspace_workflow_service_pb2.StartWorkspaceWorkflowResponse:
        """Starts a workspace."""
        deps = self.deps
        response = datahub_v1_workspace_workflow_service_pb2.StartWorkspaceWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('StartWorkspaceWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'StartWorkspaceWorkflow', {'reason': request.reason})
            await deps.repository.save_workspace(request.context.tenant_id, request.workspace)
            response_0 = edgegateway_v1_route_binding_service_pb2.WatchRouteBindingsResponse()
            response_1 = featurestore_v1_feature_view_workflow_service_pb2.SignalFeatureViewWorkflowResponse()
            outgoing_0 = edgegateway_v1_route_binding_service_pb2.WatchRouteBindingsRequest(
                context=request.context,
                subscriber=common_v1_contact_pb2.ContactInfo(email=request.workspace.assignee.email)
            )
            async for chunk_0 in deps.clients.edgegateway_route_binding.WatchRouteBindings(
                outgoing_0,
                timeout=deps.settings.timeout
            ):
                response_0 = chunk_0
            outgoing_1 = featurestore_v1_feature_view_workflow_service_pb2.SignalFeatureViewWorkflowRequest(
                context=request.context,
                details=featurestore_v1_feature_view_workflow_service_pb2.SignalFeatureViewWorkflowRequest.Details(
                    notify=common_v1_contact_pb2.ContactInfo(phone=request.workspace.requester.phone)
                )
            )
            document_1 = MessageToJson(outgoing_1, preserving_proto_field_name=True)
            outgoing_1 = Parse(
                document_1,
                featurestore_v1_feature_view_workflow_service_pb2.SignalFeatureViewWorkflowRequest()
            )
            response_1 = await deps.clients.featurestore_feature_view_workflow.SignalFeatureViewWorkflow(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_1_0 = response_1.feature_view.audit.created_by
            if returned_1_0:
                response.workspace.audit.created_by = returned_1_0
            returned_1_1 = response_1.result.reference_ids
            response.result.reference_ids.extend(returned_1_1)
            echoed_0 = request.workspace_id
            response.workspace.workspace_id = echoed_0
            echoed_1 = request.workspace.subject
            response.workspace.subject = echoed_1
            return response
