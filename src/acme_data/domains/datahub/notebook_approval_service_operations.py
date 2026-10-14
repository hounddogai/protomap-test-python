"""Functional operations behind NotebookApprovalService."""

from __future__ import annotations

from collections.abc import Awaitable
from collections.abc import Callable
from typing import Any
from typing import cast
import asyncio
import logging

from google.protobuf.any_pb2 import Any as AnyMessage
from google.protobuf.json_format import MessageToDict
from google.protobuf.json_format import MessageToJson
from google.protobuf.json_format import Parse
from google.protobuf.json_format import ParseDict

from acme.authorization.v1 import (
    access_policy_validation_service_pb2 as authorization_v1_access_policy_validation_service_pb2,
)
from acme.authorization.v1 import authorization_pb2 as authorization_v1_authorization_pb2
from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.customers.v1 import customers_pb2 as customers_v1_customers_pb2
from acme.customers.v1 import preference_import_service_pb2 as customers_v1_preference_import_service_pb2
from acme.customers.v1 import refs_pb2 as customers_v1_refs_pb2
from acme.datahub.v1 import data_share_validation_service_pb2 as datahub_v1_data_share_validation_service_pb2
from acme.datahub.v1 import datahub_pb2 as datahub_v1_datahub_pb2
from acme.datahub.v1 import notebook_approval_service_pb2 as datahub_v1_notebook_approval_service_pb2
from acme.datahub.v1 import refs_pb2 as datahub_v1_refs_pb2
from acme.datahub.v1 import workspace_approval_service_pb2 as datahub_v1_workspace_approval_service_pb2
from acme.datahub.v1 import workspace_approval_service_pb2_grpc as datahub_v1_workspace_approval_service_pb2_grpc
from acme.featurestore.v1 import entity_import_service_pb2 as featurestore_v1_entity_import_service_pb2
from acme.featurestore.v1 import feature_view_sync_service_pb2 as featurestore_v1_feature_view_sync_service_pb2
from acme.featurestore.v1 import featurestore_pb2 as featurestore_v1_featurestore_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.metrics.v1 import metric_alert_notification_service_pb2 as metrics_v1_metric_alert_notification_service_pb2
from acme.notifications.v1 import (
    notification_validation_service_pb2 as notifications_v1_notification_validation_service_pb2,
)
from acme.pipelines.v1 import pipeline_workflow_service_pb2 as pipelines_v1_pipeline_workflow_service_pb2
from acme.pipelines.v1 import pipelines_pb2 as pipelines_v1_pipelines_pb2
from acme.recommendations.v1 import (
    interaction_workflow_service_pb2 as recommendations_v1_interaction_workflow_service_pb2,
)
from acme.search.v1 import search_index_service_pb2 as search_v1_search_index_service_pb2
from acme.search.v1 import search_pb2 as search_v1_search_pb2
from acme.venues.v1 import venue_validation_service_pb2 as venues_v1_venue_validation_service_pb2

from acme_data.domains.datahub.dependencies import Dependencies
from acme_data.domains.datahub.models import NotebookApprovalDelegateNotebookApproval1Command
from acme_data.domains.datahub.models import to_notebook_approval_delegate_notebook_approval1_command
from acme_data.platform.rpc import async_messages
from acme_data.platform.tenancy import tenant_id
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


async def handle_approve_notebook(
    deps: Dependencies,
    request: datahub_v1_notebook_approval_service_pb2.ApproveNotebookRequest
) -> datahub_v1_notebook_approval_service_pb2.ApproveNotebookResponse:
    """Approves a notebook."""
    response = datahub_v1_notebook_approval_service_pb2.ApproveNotebookResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('ApproveNotebook', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'ApproveNotebook', {'reason': request.reason})
        await deps.repository.save_notebook(request.context.tenant_id, request.notebook)
        response_0 = pipelines_v1_pipeline_workflow_service_pb2.StartPipelineWorkflowResponse()
        response_1 = datahub_v1_workspace_approval_service_pb2.EscalateWorkspaceResponse()
        response_2 = featurestore_v1_feature_view_sync_service_pb2.PushFeatureViewResponse()
        outgoing_0 = pipelines_v1_pipeline_workflow_service_pb2.StartPipelineWorkflowRequest(
            context=request.context,
            pipeline=pipelines_v1_pipelines_pb2.Pipeline(
                location=common_v1_address_pb2.PostalAddress(postal_code=request.notebook.billing_address.postal_code),
                participants=[
                    pipelines_v1_pipelines_pb2.PipelineParticipant(
                        contact=common_v1_contact_pb2.ContactInfo(email=request.details.approver.email)
                    )
                ]
            )
        )
        response_0 = await deps.clients.pipelines_pipeline_workflow.StartPipelineWorkflow(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = datahub_v1_workspace_approval_service_pb2.EscalateWorkspaceRequest(
            context=request.context,
            workspace=datahub_v1_datahub_pb2.Workspace(
                audit=common_v1_audit_pb2.AuditInfo(etag=request.notebook.audit.etag),
                customer=customers_v1_refs_pb2.CustomerRef(email=request.details.approver.email)
            )
        )
        document_1 = MessageToDict(outgoing_1, preserving_proto_field_name=True)
        outgoing_1 = ParseDict(document_1, datahub_v1_workspace_approval_service_pb2.EscalateWorkspaceRequest())
        response_1 = await deps.clients.datahub_workspace_approval.EscalateWorkspace(
            outgoing_1,
            timeout=deps.settings.timeout
        )
        outgoing_2 = featurestore_v1_feature_view_sync_service_pb2.PushFeatureViewRequest(
            context=request.context,
            feature_view=featurestore_v1_featurestore_pb2.FeatureView(
                address=common_v1_address_pb2.PostalAddress(lines=list(response_0.pipeline.location.lines)),
                audit=common_v1_audit_pb2.AuditInfo(updated_by=response_0.pipeline.audit.updated_by),
                owner=identity_v1_refs_pb2.UserRef(display_name=response_1.workspace.assignee.display_name)
            )
        )
        document_2 = MessageToJson(outgoing_2, preserving_proto_field_name=True)
        outgoing_2 = Parse(document_2, featurestore_v1_feature_view_sync_service_pb2.PushFeatureViewRequest())
        response_2 = await deps.clients.featurestore_feature_view_sync.PushFeatureView(
            outgoing_2,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.pipeline.audit.created_at
        if returned_0_0.ListFields():
            response.notebook.audit.created_at.MergeFrom(returned_0_0)
        returned_0_1 = response_0.pipeline.location.country_code
        if returned_0_1:
            response.notebook.billing_address.country_code = returned_0_1
        returned_1_0 = response_1.workspace.audit.etag
        if returned_1_0:
            response.notebook.audit.etag = returned_1_0
        returned_2_0 = response_2.feature_view.audit.etag
        if returned_2_0:
            response.notebook.audit.etag = returned_2_0
        echoed_0 = request.notebook_id
        response.notebook.notebook_id = echoed_0
        echoed_1 = request.notebook.notes
        response.notebook.notes = echoed_1
        return response


async def handle_comment_notebook_approval(
    deps: Dependencies,
    request: datahub_v1_notebook_approval_service_pb2.CommentNotebookApprovalRequest
) -> datahub_v1_notebook_approval_service_pb2.CommentNotebookApprovalResponse:
    """Comments a notebook."""
    response = datahub_v1_notebook_approval_service_pb2.CommentNotebookApprovalResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('CommentNotebookApproval', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'CommentNotebookApproval', {'reason': request.reason})
        await deps.repository.save_notebook(request.context.tenant_id, request.notebook)
        response_0 = customers_v1_preference_import_service_pb2.MapPreferenceImportColumnsResponse()
        response_1 = datahub_v1_data_share_validation_service_pb2.LintDataSharesResponse()
        response_2 = datahub_v1_workspace_approval_service_pb2.EscalateWorkspaceResponse()
        callbacks_0: list[
            Callable[[], Awaitable[customers_v1_preference_import_service_pb2.MapPreferenceImportColumnsResponse]]
        ] = []
        for item_0 in request.notebook.lines:
            outgoing_0 = customers_v1_preference_import_service_pb2.MapPreferenceImportColumnsRequest(
                context=request.context,
                preference=customers_v1_customers_pb2.Preference(
                    description=item_0.description,
                    discount=customers_v1_customers_pb2.PreferenceDiscountAction(amount=item_0.tax.amount)
                )
            )
            async def send_0(
                payload: customers_v1_preference_import_service_pb2.MapPreferenceImportColumnsRequest = outgoing_0
            ) -> customers_v1_preference_import_service_pb2.MapPreferenceImportColumnsResponse:
                return await deps.clients.customers_preference_import.MapPreferenceImportColumns(
                    payload,
                    timeout=deps.settings.timeout
                )
            callbacks_0.append(send_0)
        for callback_0 in callbacks_0:
            response_0 = await callback_0()
        outgoing_1 = datahub_v1_data_share_validation_service_pb2.LintDataSharesRequest(
            context=request.context,
            data_share=datahub_v1_datahub_pb2.DataShare(
                audit=common_v1_audit_pb2.AuditInfo(
                    created_at=response_0.preference.audit.created_at,
                    updated_at=response_0.preference.audit.updated_at
                ),
                bank=datahub_v1_datahub_pb2.DataShareBankSettlement(iban=request.notebook.bank.iban),
                lines=[
                    datahub_v1_datahub_pb2.DataShareLine(
                        tax=datahub_v1_datahub_pb2.DataShareLineTax(amount=response_0.preference.discount.amount)
                    )
                ]
            )
        )
        envelope_1 = AnyMessage()
        envelope_1.Pack(outgoing_1)
        outgoing_1 = datahub_v1_data_share_validation_service_pb2.LintDataSharesRequest()
        if not envelope_1.Unpack(outgoing_1):
            raise ValueError("partner envelope contains the wrong request type")
        response_1 = await deps.clients.datahub_data_share_validation.LintDataShares(
            outgoing_1,
            timeout=deps.settings.timeout
        )
        outgoing_2 = datahub_v1_workspace_approval_service_pb2.EscalateWorkspaceRequest(
            context=request.context,
            workspace=datahub_v1_datahub_pb2.Workspace(
                audit=common_v1_audit_pb2.AuditInfo(
                    created_by=request.notebook.audit.created_by,
                    updated_at=request.notebook.audit.updated_at
                )
            )
        )
        registered_2 = cast(
            datahub_v1_workspace_approval_service_pb2_grpc.WorkspaceApprovalServiceStub,
            deps.clients.registry['acme.datahub.v1.WorkspaceApprovalService']
        )
        response_2 = await registered_2.EscalateWorkspace(outgoing_2, timeout=deps.settings.timeout)
        returned_1_0 = response_1.data_share.billing_address.country_code
        if returned_1_0:
            response.notebook.billing_address.country_code = returned_1_0
        returned_2_0 = response_2.result.message
        if returned_2_0:
            response.result.message = returned_2_0
        echoed_0 = request.notebook_id
        response.notebook.notebook_id = echoed_0
        echoed_1 = request.notebook.counterparty
        response.notebook.counterparty.CopyFrom(echoed_1)
        return response


async def handle_delegate_notebook_approval(
    deps: Dependencies,
    request: datahub_v1_notebook_approval_service_pb2.DelegateNotebookApprovalRequest
) -> datahub_v1_notebook_approval_service_pb2.DelegateNotebookApprovalResponse:
    """Delegates a notebook."""
    response = datahub_v1_notebook_approval_service_pb2.DelegateNotebookApprovalResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('DelegateNotebookApproval', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'DelegateNotebookApproval', {'reason': request.reason})
        await deps.repository.save_notebook(request.context.tenant_id, request.notebook)
        response_0 = datahub_v1_data_share_validation_service_pb2.ScoreDataShareResponse()
        response_1 = featurestore_v1_entity_import_service_pb2.ValidateEntityImportResponse()
        outgoing_0 = datahub_v1_data_share_validation_service_pb2.ScoreDataShareRequest(
            context=request.context,
            data_share=datahub_v1_datahub_pb2.DataShare(
                billing_address=common_v1_address_pb2.PostalAddress(lines=list(request.notebook.billing_address.lines))
            ),
            details=datahub_v1_data_share_validation_service_pb2.ScoreDataShareRequest.Details(
                destination=common_v1_address_pb2.PostalAddress(recipient=request.notebook.billing_address.recipient)
            )
        )
        response_0 = await deps.clients.datahub_data_share_validation.ScoreDataShare(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        command_1 = NotebookApprovalDelegateNotebookApproval1Command.model_validate(
            {
                'context': request.context,
                'entity_audit_created_at': response_0.data_share.audit.created_at,
                'entity_primary_address_postal_code': request.notebook.billing_address.postal_code,
                'entity_audit_created_by': request.notebook.audit.created_by
            }
        )
        outgoing_1 = to_notebook_approval_delegate_notebook_approval1_command(command_1)
        response_1 = await deps.clients.featurestore_entity_import.ValidateEntityImport(
            outgoing_1,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.data_share.notes
        if returned_0_0:
            response.notebook.notes = returned_0_0
        returned_1_0 = response_1.entity.audit.etag
        if returned_1_0:
            response.notebook.audit.etag = returned_1_0
        echoed_0 = request.notebook_id
        response.notebook.notebook_id = echoed_0
        echoed_1 = request.notebook.issued_at
        response.notebook.issued_at.CopyFrom(echoed_1)
        return response


async def handle_escalate_notebook(
    deps: Dependencies,
    request: datahub_v1_notebook_approval_service_pb2.EscalateNotebookRequest
) -> datahub_v1_notebook_approval_service_pb2.EscalateNotebookResponse:
    """Escalates a notebook."""
    response = datahub_v1_notebook_approval_service_pb2.EscalateNotebookResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('EscalateNotebook', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'EscalateNotebook', {'reason': request.reason})
        await deps.repository.save_notebook(request.context.tenant_id, request.notebook)
        response_0 = datahub_v1_workspace_approval_service_pb2.EscalateWorkspaceResponse()
        response_1 = notifications_v1_notification_validation_service_pb2.LintNotificationsResponse()
        response_2 = recommendations_v1_interaction_workflow_service_pb2.SignalInteractionWorkflowResponse()
        outgoing_0 = datahub_v1_workspace_approval_service_pb2.EscalateWorkspaceRequest(
            context=request.context,
            workspace=datahub_v1_datahub_pb2.Workspace(
                assignee=identity_v1_refs_pb2.UserRef(display_name=request.notebook.counterparty.display_name),
                audit=common_v1_audit_pb2.AuditInfo(created_by=request.notebook.audit.created_by)
            )
        )
        response_0 = await deps.clients.datahub_workspace_approval.EscalateWorkspace(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = notifications_v1_notification_validation_service_pb2.LintNotificationsRequest()
        outgoing_1.context.CopyFrom(request.context)
        outgoing_1.notification.audit.etag = response_0.workspace.audit.etag
        if response_0.workspace.WhichOneof('origin') == 'customer':
            outgoing_1.notification.requester.email = response_0.workspace.customer.email
        response_1 = await deps.clients.notifications_notification_validation.LintNotifications(
            outgoing_1,
            timeout=deps.settings.timeout
        )
        outgoing_2 = recommendations_v1_interaction_workflow_service_pb2.SignalInteractionWorkflowRequest()
        outgoing_2.context.CopyFrom(request.context)
        outgoing_2.details.notify.name.CopyFrom(response_1.notification.requester.name)
        outgoing_2.details.notify.email = response_0.workspace.assignee.email
        outgoing_2.interaction.subject.display_name = request.notebook.counterparty.display_name
        outgoing_2.context.tenant_id = tenant_id.get()
        response_2 = await deps.clients.recommendations_interaction_workflow.SignalInteractionWorkflow(
            outgoing_2,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.workspace.audit.updated_at
        if returned_0_0.ListFields():
            response.notebook.audit.updated_at.MergeFrom(returned_0_0)
        returned_0_1 = response_0.result.message
        if returned_0_1:
            response.outcome.message = returned_0_1
        returned_1_0 = response_1.notification.customer.display_name
        if returned_1_0:
            response.notebook.counterparty.display_name = returned_1_0
        returned_2_0 = response_2.interaction.correlation_id
        if returned_2_0:
            response.result.correlation_id = returned_2_0
        returned_2_1 = response_2.result.status
        if returned_2_1:
            response.outcome.status = returned_2_1
        echoed_0 = request.notebook_id
        response.notebook.notebook_id = echoed_0
        echoed_1 = request.details.effective_at
        response.outcome.effective_at.CopyFrom(echoed_1)
        return response


async def handle_get_notebook_approval_status(
    deps: Dependencies,
    request: datahub_v1_notebook_approval_service_pb2.GetNotebookApprovalStatusRequest
) -> datahub_v1_notebook_approval_service_pb2.GetNotebookApprovalStatusResponse:
    """Returns a notebook."""
    response = datahub_v1_notebook_approval_service_pb2.GetNotebookApprovalStatusResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('GetNotebookApprovalStatus', extra={'fields': {'domain': 'datahub'}})
        await deps.repository.audit(request.context.tenant_id, 'GetNotebookApprovalStatus', {})
        response_0 = datahub_v1_data_share_validation_service_pb2.ScoreDataShareResponse()
        outgoing_0 = datahub_v1_data_share_validation_service_pb2.ScoreDataShareRequest(
            context=request.context,
            data_share=datahub_v1_datahub_pb2.DataShare(
                audit=common_v1_audit_pb2.AuditInfo(created_at=request.context.deadline),
                counterparty=datahub_v1_refs_pb2.NotebookRef(notebook_id=request.notebook_id)
            )
        )
        response_0 = await deps.clients.datahub_data_share_validation.ScoreDataShare(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.result.status
        if returned_0_0:
            response.result.status = returned_0_0
        returned_0_1 = response_0.data_share.audit.created_at
        if returned_0_1.ListFields():
            response.notebook.audit.created_at.MergeFrom(returned_0_1)
        echoed_0 = request.notebook_id
        response.notebook.notebook_id = echoed_0
        return response


async def handle_list_pending_notebooks(
    deps: Dependencies,
    request: datahub_v1_notebook_approval_service_pb2.ListPendingNotebooksRequest
) -> datahub_v1_notebook_approval_service_pb2.ListPendingNotebooksResponse:
    """Lists notebooks a page at a time."""
    response = datahub_v1_notebook_approval_service_pb2.ListPendingNotebooksResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('ListPendingNotebooks', extra={'fields': {'order_by': request.order_by}})
        await deps.repository.audit(request.context.tenant_id, 'ListPendingNotebooks', {'order_by': request.order_by})
        response_0 = authorization_v1_access_policy_validation_service_pb2.LintAccessPoliciesResponse()
        outgoing_0 = authorization_v1_access_policy_validation_service_pb2.LintAccessPoliciesRequest(
            access_policy=authorization_v1_authorization_pb2.AccessPolicy(
                audit=common_v1_audit_pb2.AuditInfo(created_at=request.filter.created_after),
                owner=identity_v1_refs_pb2.UserRef(
                    email=request.context.actor.email,
                    user_id=request.context.actor.user_id
                )
            ),
            context=request.context,
            details=authorization_v1_access_policy_validation_service_pb2.LintAccessPoliciesRequest.Details(
                locale=request.context.locale
            )
        )
        response_0 = await deps.clients.authorization_access_policy_validation.LintAccessPolicies(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.result.correlation_id
        if returned_0_0:
            response.result.correlation_id = returned_0_0
        returned_0_1 = response_0.access_policy.audit.updated_at
        returned_0_1_part_0 = response.notebooks.add()
        if returned_0_1.ListFields():
            returned_0_1_part_0.audit.updated_at.MergeFrom(returned_0_1)
        return response


async def handle_recall_notebook(
    deps: Dependencies,
    request: datahub_v1_notebook_approval_service_pb2.RecallNotebookRequest
) -> datahub_v1_notebook_approval_service_pb2.RecallNotebookResponse:
    """Recalls a notebook."""
    response = datahub_v1_notebook_approval_service_pb2.RecallNotebookResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('RecallNotebook', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'RecallNotebook', {'reason': request.reason})
        await deps.repository.save_notebook(request.context.tenant_id, request.notebook)
        response_0 = datahub_v1_workspace_approval_service_pb2.DelegateWorkspaceApprovalResponse()
        response_1 = authorization_v1_access_policy_validation_service_pb2.ExplainAccessPolicyDecisionResponse()
        response_2 = datahub_v1_workspace_approval_service_pb2.SubmitWorkspaceResponse()
        outgoing_0 = datahub_v1_workspace_approval_service_pb2.DelegateWorkspaceApprovalRequest(
            context=request.context,
            workspace=datahub_v1_datahub_pb2.Workspace(
                audit=common_v1_audit_pb2.AuditInfo(created_at=request.notebook.audit.created_at),
                workspace_id=request.notebook.counterparty.workspace_id
            )
        )
        response_0 = await deps.clients.datahub_workspace_approval.DelegateWorkspaceApproval(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = authorization_v1_access_policy_validation_service_pb2.ExplainAccessPolicyDecisionRequest(
            access_policy=authorization_v1_authorization_pb2.AccessPolicy(
                owner=identity_v1_refs_pb2.UserRef(
                    display_name=request.notebook.counterparty.display_name,
                    email=response_0.workspace.assignee.email
                )
            ),
            context=request.context,
            details=authorization_v1_access_policy_validation_service_pb2.ExplainAccessPolicyDecisionRequest.Details(
                contact=common_v1_contact_pb2.ContactInfo(email=response_0.workspace.requester.email)
            )
        )
        response_1 = cast(authorization_v1_access_policy_validation_service_pb2.ExplainAccessPolicyDecisionResponse, await deps.bus.request(
            'acme.datahub.v1.NotebookApprovalService/RecallNotebook/1', outgoing_1, deps.settings.timeout,
        ))
        outgoing_2 = datahub_v1_workspace_approval_service_pb2.SubmitWorkspaceRequest(
            context=request.context,
            workspace=datahub_v1_datahub_pb2.Workspace(
                audit=common_v1_audit_pb2.AuditInfo(created_at=request.notebook.audit.created_at)
            )
        )
        response_2 = await deps.clients.datahub_workspace_approval.SubmitWorkspace(
            outgoing_2,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.workspace.audit.updated_by
        if returned_0_0:
            response.notebook.audit.updated_by = returned_0_0
        returned_1_0 = response_1.access_policy.discount.amount
        returned_1_0_part_1 = response.notebook.lines.add()
        if returned_1_0.ListFields():
            returned_1_0_part_1.amount.MergeFrom(returned_1_0)
        returned_2_0 = response_2.result.status
        if returned_2_0:
            response.result.status = returned_2_0
        returned_2_1 = response_2.result.correlation_id
        if returned_2_1:
            response.result.correlation_id = returned_2_1
        echoed_0 = request.notebook_id
        response.notebook.notebook_id = echoed_0
        echoed_1 = request.details.effective_at
        response.outcome.effective_at.CopyFrom(echoed_1)
        return response


async def handle_reject_notebook(
    deps: Dependencies,
    request: datahub_v1_notebook_approval_service_pb2.RejectNotebookRequest
) -> datahub_v1_notebook_approval_service_pb2.RejectNotebookResponse:
    """Rejects a notebook."""
    response = datahub_v1_notebook_approval_service_pb2.RejectNotebookResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('RejectNotebook', extra={'fields': {'approver_email': request.details.approver_email}})
        await deps.repository.audit(
            request.context.tenant_id,
            'RejectNotebook',
            {'approver_email': request.details.approver_email}
        )
        await deps.repository.save_notebook(request.context.tenant_id, request.notebook)
        response_0 = search_v1_search_index_service_pb2.UpdateSearchIndexResponse()
        response_1 = metrics_v1_metric_alert_notification_service_pb2.UnsubscribeMetricAlertUpdatesResponse()
        outgoing_0 = search_v1_search_index_service_pb2.UpdateSearchIndexRequest(
            context=request.context,
            search_index=search_v1_search_pb2.SearchIndex(
                address=common_v1_address_pb2.PostalAddress(country_code=request.notebook.billing_address.country_code),
                owner=identity_v1_refs_pb2.UserRef(email=request.details.approver.email)
            )
        )
        response_0 = await deps.clients.search_search_index.UpdateSearchIndex(outgoing_0, timeout=deps.settings.timeout)
        fields_1: dict[str, Any] = {
            'annotations': dict(request.annotations),
            'context': request.context,
            'details': {
                'recipient': {'email': request.details.approver.email},
                'variables': dict(response_0.result.details)
            },
            'reason': request.reason
        }
        outgoing_1 = metrics_v1_metric_alert_notification_service_pb2.UnsubscribeMetricAlertUpdatesRequest(**fields_1)
        response_1 = await deps.clients.metrics_metric_alert_notification.UnsubscribeMetricAlertUpdates(
            outgoing_1,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.result.status
        if returned_0_0:
            response.result.status = returned_0_0
        returned_0_1 = response_0.result.status
        if returned_0_1:
            response.outcome.status = returned_0_1
        returned_1_0 = response_1.metric_alert.audit.etag
        if returned_1_0:
            response.notebook.audit.etag = returned_1_0
        returned_1_1 = response_1.result.details
        response.result.details.update(returned_1_1)
        echoed_0 = request.notebook_id
        response.notebook.notebook_id = echoed_0
        echoed_1 = request.notebook.status
        response.notebook.status = echoed_1
        return response


async def handle_submit_notebook(
    deps: Dependencies,
    request: datahub_v1_notebook_approval_service_pb2.SubmitNotebookRequest
) -> datahub_v1_notebook_approval_service_pb2.SubmitNotebookResponse:
    """Submits a notebook."""
    response = datahub_v1_notebook_approval_service_pb2.SubmitNotebookResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('SubmitNotebook', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'SubmitNotebook', {'reason': request.reason})
        await deps.repository.save_notebook(request.context.tenant_id, request.notebook)
        response_0 = customers_v1_preference_import_service_pb2.RetryPreferenceImportResponse()
        response_1 = datahub_v1_data_share_validation_service_pb2.ValidateDataShareResponse()
        response_2 = venues_v1_venue_validation_service_pb2.NormalizeVenueResponse()
        response_3 = datahub_v1_data_share_validation_service_pb2.NormalizeDataShareResponse()
        async for item_0 in async_messages(request.notebook.lines):
            outgoing_0 = customers_v1_preference_import_service_pb2.RetryPreferenceImportRequest(
                context=request.context,
                preference=customers_v1_customers_pb2.Preference(
                    audit=common_v1_audit_pb2.AuditInfo(created_by=request.notebook.audit.created_by),
                    description=item_0.description,
                    discount=customers_v1_customers_pb2.PreferenceDiscountAction(amount=item_0.amount)
                )
            )
            response_0 = await deps.clients.customers_preference_import.RetryPreferenceImport(
                outgoing_0,
                timeout=deps.settings.timeout
            )
        outgoing_1 = datahub_v1_data_share_validation_service_pb2.ValidateDataShareRequest(
            context=request.context,
            data_share=datahub_v1_datahub_pb2.DataShare(
                bank=datahub_v1_datahub_pb2.DataShareBankSettlement(bic=request.notebook.bank.bic),
                billing_address=common_v1_address_pb2.PostalAddress(
                    recipient=request.notebook.billing_address.recipient,
                    region=request.notebook.billing_address.region
                ),
                lines=[
                    datahub_v1_datahub_pb2.DataShareLine(
                        tax=datahub_v1_datahub_pb2.DataShareLineTax(amount=response_0.preference.discount.amount)
                    )
                ]
            )
        )
        document_1 = MessageToJson(outgoing_1, preserving_proto_field_name=True)
        outgoing_1 = Parse(document_1, datahub_v1_data_share_validation_service_pb2.ValidateDataShareRequest())
        response_1 = await deps.clients.datahub_data_share_validation.ValidateDataShare(
            outgoing_1,
            timeout=deps.settings.timeout
        )
        outgoing_2 = venues_v1_venue_validation_service_pb2.NormalizeVenueRequest()
        outgoing_2.context.CopyFrom(request.context)
        outgoing_2.venue.owner.display_name = request.details.approver.display_name
        outgoing_2.venue.audit.created_by = response_0.preference.audit.created_by
        outgoing_2.venue.audit.updated_at.CopyFrom(response_1.data_share.audit.updated_at)
        outgoing_2.venue.address.region = response_1.data_share.billing_address.region
        merged_2 = venues_v1_venue_validation_service_pb2.NormalizeVenueRequest()
        merged_2.MergeFrom(outgoing_2)
        outgoing_2.CopyFrom(merged_2)
        response_2 = await deps.clients.venues_venue_validation.NormalizeVenue(
            outgoing_2,
            timeout=deps.settings.timeout
        )
        outgoing_3 = datahub_v1_data_share_validation_service_pb2.NormalizeDataShareRequest(
            context=request.context,
            data_share=datahub_v1_datahub_pb2.DataShare(
                audit=common_v1_audit_pb2.AuditInfo(updated_at=response_0.preference.audit.updated_at),
                billing_address=common_v1_address_pb2.PostalAddress(
                    postal_code=response_1.data_share.billing_address.postal_code,
                    region=response_1.data_share.billing_address.region
                )
            )
        )
        envelope_3 = AnyMessage()
        envelope_3.Pack(outgoing_3)
        outgoing_3 = datahub_v1_data_share_validation_service_pb2.NormalizeDataShareRequest()
        if not envelope_3.Unpack(outgoing_3):
            raise ValueError("partner envelope contains the wrong request type")
        response_3 = await deps.clients.datahub_data_share_validation.NormalizeDataShare(
            outgoing_3,
            timeout=deps.settings.timeout
        )
        returned_1_0 = response_1.data_share.audit.created_at
        if returned_1_0.ListFields():
            response.notebook.audit.created_at.MergeFrom(returned_1_0)
        returned_2_0 = response_2.venue.address.country_code
        if returned_2_0:
            response.notebook.billing_address.country_code = returned_2_0
        returned_2_1 = response_2.result.details
        response.result.details.update(returned_2_1)
        returned_3_0 = response_3.result.correlation_id
        if returned_3_0:
            response.result.correlation_id = returned_3_0
        returned_3_1 = response_3.outcome.effective_at
        if returned_3_1.ListFields():
            response.outcome.effective_at.MergeFrom(returned_3_1)
        echoed_0 = request.notebook_id
        response.notebook.notebook_id = echoed_0
        echoed_1 = request.notebook.number
        response.notebook.number = echoed_1
        return response
