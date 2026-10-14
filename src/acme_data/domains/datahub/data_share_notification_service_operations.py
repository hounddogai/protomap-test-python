"""Functional operations behind DataShareNotificationService."""

from __future__ import annotations

import logging

from google.protobuf.any_pb2 import Any as AnyMessage
from google.protobuf.json_format import MessageToJson
from google.protobuf.json_format import Parse

from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.datahub.v1 import data_share_notification_service_pb2 as datahub_v1_data_share_notification_service_pb2
from acme.datahub.v1 import data_share_reporting_service_pb2 as datahub_v1_data_share_reporting_service_pb2
from acme.datahub.v1 import datahub_pb2 as datahub_v1_datahub_pb2
from acme.datahub.v1 import notebook_approval_service_pb2 as datahub_v1_notebook_approval_service_pb2
from acme.datahub.v1 import notebook_reporting_service_pb2 as datahub_v1_notebook_reporting_service_pb2
from acme.datahub.v1 import workspace_notification_service_pb2 as datahub_v1_workspace_notification_service_pb2
from acme.datahub.v1 import workspace_workflow_service_pb2 as datahub_v1_workspace_workflow_service_pb2
from acme.fanportal.v1 import fan_session_service_pb2 as fanportal_v1_fan_session_service_pb2
from acme.fanportal.v1 import fanportal_pb2 as fanportal_v1_fanportal_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.labeling.v1 import label_set_reporting_service_pb2 as labeling_v1_label_set_reporting_service_pb2
from acme.pipelines.v1 import pipeline_run_workflow_service_pb2 as pipelines_v1_pipeline_run_workflow_service_pb2
from acme.search.v1 import search_index_validation_service_pb2 as search_v1_search_index_validation_service_pb2
from acme.search.v1 import search_pb2 as search_v1_search_pb2

from acme_data.domains.datahub import hooks
from acme_data.domains.datahub.dependencies import Dependencies
from acme_data.domains.datahub.models import DataShareNotificationSubscribeDataShareUpdates2Command
from acme_data.domains.datahub.models import to_data_share_notification_subscribe_data_share_updates2_command
from acme_data.platform.rpc import async_messages
from acme_data.platform.tenancy import tenant_id
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


async def handle_get_data_share_preferences(
    deps: Dependencies,
    request: datahub_v1_data_share_notification_service_pb2.GetDataSharePreferencesRequest
) -> datahub_v1_data_share_notification_service_pb2.GetDataSharePreferencesResponse:
    """Returns a data share."""
    response = datahub_v1_data_share_notification_service_pb2.GetDataSharePreferencesResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('GetDataSharePreferences', extra={'fields': {'locale': request.context.locale}})
        await deps.repository.audit(
            request.context.tenant_id,
            'GetDataSharePreferences',
            {'locale': request.context.locale}
        )
        echoed_0 = request.data_share_id
        response.data_share.data_share_id = echoed_0
        return response


async def handle_list_data_share_subscriptions(
    deps: Dependencies,
    request: datahub_v1_data_share_notification_service_pb2.ListDataShareSubscriptionsRequest
) -> datahub_v1_data_share_notification_service_pb2.ListDataShareSubscriptionsResponse:
    """Lists data shares a page at a time."""
    response = datahub_v1_data_share_notification_service_pb2.ListDataShareSubscriptionsResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('ListDataShareSubscriptions', extra={'fields': {'order_by': request.order_by}})
        await deps.repository.audit(
            request.context.tenant_id,
            'ListDataShareSubscriptions',
            {'order_by': request.order_by}
        )
        response_0 = datahub_v1_workspace_workflow_service_pb2.AdvanceWorkspaceWorkflowResponse()
        outgoing_0 = datahub_v1_workspace_workflow_service_pb2.AdvanceWorkspaceWorkflowRequest(
            context=request.context,
            details=datahub_v1_workspace_workflow_service_pb2.AdvanceWorkspaceWorkflowRequest.Details(
                notify=common_v1_contact_pb2.ContactInfo(email=request.context.actor.email)
            ),
            workspace=datahub_v1_datahub_pb2.Workspace(
                assignee=identity_v1_refs_pb2.UserRef(user_id=request.context.actor.user_id)
            )
        )
        response_0 = await deps.clients.datahub_workspace_workflow.AdvanceWorkspaceWorkflow(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.result.correlation_id
        if returned_0_0:
            response.result.correlation_id = returned_0_0
        returned_0_1 = response_0.outcome.message
        if returned_0_1:
            response.result.message = returned_0_1
        return response


async def handle_notify_data_share_watchers(
    deps: Dependencies,
    request: datahub_v1_data_share_notification_service_pb2.NotifyDataShareWatchersRequest
) -> datahub_v1_data_share_notification_service_pb2.NotifyDataShareWatchersResponse:
    """Notifys a data share."""
    response = datahub_v1_data_share_notification_service_pb2.NotifyDataShareWatchersResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('NotifyDataShareWatchers', extra={'fields': {'channel': request.details.channel}})
        await deps.repository.audit(
            request.context.tenant_id,
            'NotifyDataShareWatchers',
            {'channel': request.details.channel}
        )
        response_0 = datahub_v1_notebook_approval_service_pb2.DelegateNotebookApprovalResponse()
        response_1 = labeling_v1_label_set_reporting_service_pb2.StreamLabelSetMetricsResponse()
        response_2 = datahub_v1_workspace_workflow_service_pb2.StartWorkspaceWorkflowResponse()
        outgoing_0 = datahub_v1_notebook_approval_service_pb2.DelegateNotebookApprovalRequest(
            annotations=dict(request.annotations),
            context=request.context,
            details=datahub_v1_notebook_approval_service_pb2.DelegateNotebookApprovalRequest.Details(
                approver=identity_v1_refs_pb2.UserRef(
                    email=request.details.recipient.email,
                    user_id=request.context.actor.user_id
                )
            ),
            reason=request.reason
        )
        response_0 = await deps.clients.datahub_notebook_approval.DelegateNotebookApproval(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = labeling_v1_label_set_reporting_service_pb2.StreamLabelSetMetricsRequest(
            context=request.context,
            subscriber=common_v1_contact_pb2.ContactInfo(
                email=request.details.recipient.email,
                phone=request.details.recipient.phone,
                preferred_channel=request.details.recipient.preferred_channel
            )
        )
        async for chunk_1 in deps.clients.labeling_label_set_reporting.StreamLabelSetMetrics(
            outgoing_1,
            timeout=deps.settings.timeout
        ):
            response_1 = chunk_1
        outgoing_2 = datahub_v1_workspace_workflow_service_pb2.StartWorkspaceWorkflowRequest(
            context=request.context,
            details=datahub_v1_workspace_workflow_service_pb2.StartWorkspaceWorkflowRequest.Details(
                notify=common_v1_contact_pb2.ContactInfo(
                    email=request.details.recipient.email,
                    phone=request.details.recipient.phone
                )
            ),
            workspace=datahub_v1_datahub_pb2.Workspace(
                audit=common_v1_audit_pb2.AuditInfo(
                    created_by=response_0.notebook.audit.created_by,
                    etag=response_0.notebook.audit.etag
                )
            )
        )
        document_2 = MessageToJson(outgoing_2, preserving_proto_field_name=True)
        outgoing_2 = Parse(document_2, datahub_v1_workspace_workflow_service_pb2.StartWorkspaceWorkflowRequest())
        response_2 = await deps.clients.datahub_workspace_workflow.StartWorkspaceWorkflow(
            outgoing_2,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.notebook.number
        if returned_0_0:
            response.data_share.number = returned_0_0
        returned_0_1 = response_0.notebook.billing_address.recipient
        if returned_0_1:
            response.data_share.billing_address.recipient = returned_0_1
        returned_2_0 = response_2.outcome.reference_id
        if returned_2_0:
            response.outcome.reference_id = returned_2_0
        echoed_0 = request.data_share_id
        response.data_share.data_share_id = echoed_0
        return response


async def handle_send_data_share_test_notice(
    deps: Dependencies,
    request: datahub_v1_data_share_notification_service_pb2.SendDataShareTestNoticeRequest
) -> datahub_v1_data_share_notification_service_pb2.SendDataShareTestNoticeResponse:
    """Sends a data share."""
    response = datahub_v1_data_share_notification_service_pb2.SendDataShareTestNoticeResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('SendDataShareTestNotice', extra={'fields': {'channel': request.details.channel}})
        await deps.repository.audit(
            request.context.tenant_id,
            'SendDataShareTestNotice',
            {'channel': request.details.channel}
        )
        response_0 = datahub_v1_data_share_reporting_service_pb2.CountDataShareTotalsResponse()
        response_1 = datahub_v1_data_share_reporting_service_pb2.ScheduleDataShareReportResponse()
        outgoing_0 = datahub_v1_data_share_reporting_service_pb2.CountDataShareTotalsRequest(
            context=request.context,
            filter=datahub_v1_data_share_reporting_service_pb2.CountDataShareTotalsRequest.Filter(
                created_after=request.context.deadline,
                owner_id=request.details.template_id
            )
        )
        response_0 = await deps.clients.datahub_data_share_reporting.CountDataShareTotals(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = datahub_v1_data_share_reporting_service_pb2.ScheduleDataShareReportRequest(
            annotations=dict(request.annotations),
            context=request.context,
            data_share_id=request.data_share_id,
            reason=request.reason
        )
        envelope_1 = AnyMessage()
        envelope_1.Pack(outgoing_1)
        outgoing_1 = datahub_v1_data_share_reporting_service_pb2.ScheduleDataShareReportRequest()
        if not envelope_1.Unpack(outgoing_1):
            raise ValueError("partner envelope contains the wrong request type")
        response_1 = await deps.clients.datahub_data_share_reporting.ScheduleDataShareReport(
            outgoing_1,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.result.status
        if returned_0_0:
            response.outcome.status = returned_0_0
        returned_1_0 = response_1.result.reference_ids
        response.result.reference_ids.extend(returned_1_0)
        returned_1_1 = response_1.result.status
        if returned_1_1:
            response.result.status = returned_1_1
        echoed_0 = request.data_share_id
        response.data_share.data_share_id = echoed_0
        return response


async def handle_subscribe_data_share_updates(
    deps: Dependencies,
    request: datahub_v1_data_share_notification_service_pb2.SubscribeDataShareUpdatesRequest
) -> datahub_v1_data_share_notification_service_pb2.SubscribeDataShareUpdatesResponse:
    """Subscribes a data share."""
    response = datahub_v1_data_share_notification_service_pb2.SubscribeDataShareUpdatesResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('SubscribeDataShareUpdates', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'SubscribeDataShareUpdates', {'reason': request.reason})
        response_0 = fanportal_v1_fan_session_service_pb2.CreateFanSessionResponse()
        response_1 = datahub_v1_notebook_reporting_service_pb2.StreamNotebookMetricsResponse()
        response_2 = pipelines_v1_pipeline_run_workflow_service_pb2.SignalPipelineRunWorkflowResponse()
        outgoing_0 = fanportal_v1_fan_session_service_pb2.CreateFanSessionRequest(
            context=request.context,
            fan_session=fanportal_v1_fanportal_pb2.FanSession(
                requester=common_v1_contact_pb2.ContactInfo(
                    email=request.details.recipient.email,
                    name=request.details.recipient.name,
                    phone=request.details.recipient.phone,
                    preferred_channel=request.details.recipient.preferred_channel
                )
            )
        )
        response_0 = await deps.clients.fanportal_fan_session.CreateFanSession(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = datahub_v1_notebook_reporting_service_pb2.StreamNotebookMetricsRequest(
            context=request.context,
            subscriber=common_v1_contact_pb2.ContactInfo(name=response_0.fan_session.requester.name)
        )
        async for chunk_1 in deps.clients.datahub_notebook_reporting.StreamNotebookMetrics(
            outgoing_1,
            timeout=deps.settings.timeout
        ):
            response_1 = chunk_1
        command_2 = DataShareNotificationSubscribeDataShareUpdates2Command.model_validate(
            {'context': request.context, 'pipeline_run_assignee_email': request.details.recipient.email}
        )
        outgoing_2 = to_data_share_notification_subscribe_data_share_updates2_command(command_2)
        response_2 = await deps.clients.pipelines_pipeline_run_workflow.SignalPipelineRunWorkflow(
            outgoing_2,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.result.status
        if returned_0_0:
            response.outcome.status = returned_0_0
        returned_0_1 = response_0.fan_session.assignee.display_name
        if returned_0_1:
            response.data_share.counterparty.display_name = returned_0_1
        returned_2_0 = response_2.pipeline_run.audit.etag
        if returned_2_0:
            response.data_share.audit.etag = returned_2_0
        returned_2_1 = response_2.result.reference_ids
        response.result.reference_ids.extend(returned_2_1)
        echoed_0 = request.data_share_id
        response.data_share.data_share_id = echoed_0
        return response


async def handle_unsubscribe_data_share_updates(
    deps: Dependencies,
    request: datahub_v1_data_share_notification_service_pb2.UnsubscribeDataShareUpdatesRequest
) -> datahub_v1_data_share_notification_service_pb2.UnsubscribeDataShareUpdatesResponse:
    """Unsubscribes a data share."""
    response = datahub_v1_data_share_notification_service_pb2.UnsubscribeDataShareUpdatesResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('UnsubscribeDataShareUpdates', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(
            request.context.tenant_id,
            'UnsubscribeDataShareUpdates',
            {'reason': request.reason}
        )
        response_0 = datahub_v1_workspace_notification_service_pb2.NotifyWorkspaceWatchersResponse()
        response_1 = search_v1_search_index_validation_service_pb2.LintSearchIndexesResponse()
        response_2 = datahub_v1_workspace_workflow_service_pb2.AdvanceWorkspaceWorkflowResponse()
        outgoing_0 = datahub_v1_workspace_notification_service_pb2.NotifyWorkspaceWatchersRequest(
            context=request.context,
            details=datahub_v1_workspace_notification_service_pb2.NotifyWorkspaceWatchersRequest.Details(
                recipient=common_v1_contact_pb2.ContactInfo(
                    email=request.details.recipient.email,
                    preferred_channel=request.details.recipient.preferred_channel
                )
            )
        )
        response_0 = await deps.clients.datahub_workspace_notification.NotifyWorkspaceWatchers(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = search_v1_search_index_validation_service_pb2.LintSearchIndexesRequest(
            context=request.context,
            details=search_v1_search_index_validation_service_pb2.LintSearchIndexesRequest.Details(
                contact=common_v1_contact_pb2.ContactInfo(name=request.details.recipient.name)
            ),
            search_index=search_v1_search_pb2.SearchIndex(
                audit=common_v1_audit_pb2.AuditInfo(
                    created_at=response_0.workspace.audit.created_at,
                    updated_by=response_0.workspace.audit.updated_by
                ),
                owner=identity_v1_refs_pb2.UserRef(user_id=response_0.workspace.assignee.user_id)
            )
        )
        response_1 = await hooks.data_share_notification_unsubscribe_data_share_updates1(
            deps.clients.search_search_index_validation,
            outgoing_1,
            deps.settings.timeout
        )
        outgoing_2 = datahub_v1_workspace_workflow_service_pb2.AdvanceWorkspaceWorkflowRequest()
        outgoing_2.context.CopyFrom(request.context)
        outgoing_2.workspace.customer.email = request.details.recipient.email
        outgoing_2.context.tenant_id = tenant_id.get()
        response_2 = await deps.clients.datahub_workspace_workflow.AdvanceWorkspaceWorkflow(
            outgoing_2,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.result.reference_ids
        response.result.reference_ids.extend(returned_0_0)
        returned_1_0 = response_1.search_index.owner.display_name
        if returned_1_0:
            response.data_share.counterparty.display_name = returned_1_0
        returned_2_0 = response_2.workspace.audit.created_at
        if returned_2_0.ListFields():
            response.data_share.audit.created_at.MergeFrom(returned_2_0)
        returned_2_1 = response_2.result.details
        response.result.details.update(returned_2_1)
        echoed_0 = request.data_share_id
        response.data_share.data_share_id = echoed_0
        return response
