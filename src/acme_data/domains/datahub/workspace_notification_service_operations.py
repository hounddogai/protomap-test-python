"""Functional operations behind WorkspaceNotificationService."""

from __future__ import annotations

from functools import partial
from typing import Any
import logging

from google.protobuf.any_pb2 import Any as AnyMessage

from acme.analytics.v1 import analytics_pb2 as analytics_v1_analytics_pb2
from acme.analytics.v1 import (
    analytics_report_approval_service_pb2 as analytics_v1_analytics_report_approval_service_pb2,
)
from acme.audit.v1 import audit_event_validation_service_pb2 as audit_v1_audit_event_validation_service_pb2
from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.customers.v1 import customers_pb2 as customers_v1_customers_pb2
from acme.customers.v1 import household_workflow_service_pb2 as customers_v1_household_workflow_service_pb2
from acme.customers.v1 import preference_reporting_service_pb2 as customers_v1_preference_reporting_service_pb2
from acme.customers.v1 import refs_pb2 as customers_v1_refs_pb2
from acme.datahub.v1 import data_share_validation_service_pb2 as datahub_v1_data_share_validation_service_pb2
from acme.datahub.v1 import datahub_pb2 as datahub_v1_datahub_pb2
from acme.datahub.v1 import notebook_approval_service_pb2 as datahub_v1_notebook_approval_service_pb2
from acme.datahub.v1 import notebook_integration_service_pb2 as datahub_v1_notebook_integration_service_pb2
from acme.datahub.v1 import notebook_reporting_service_pb2 as datahub_v1_notebook_reporting_service_pb2
from acme.datahub.v1 import notebook_workflow_service_pb2 as datahub_v1_notebook_workflow_service_pb2
from acme.datahub.v1 import refs_pb2 as datahub_v1_refs_pb2
from acme.datahub.v1 import workspace_integration_service_pb2 as datahub_v1_workspace_integration_service_pb2
from acme.datahub.v1 import workspace_notification_service_pb2 as datahub_v1_workspace_notification_service_pb2
from acme.fanportal.v1 import fan_session_query_service_pb2 as fanportal_v1_fan_session_query_service_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.metrics.v1 import dashboard_sync_service_pb2 as metrics_v1_dashboard_sync_service_pb2
from acme.metrics.v1 import metric_series_validation_service_pb2 as metrics_v1_metric_series_validation_service_pb2
from acme.patientapp.v1 import patient_home_query_service_pb2 as patientapp_v1_patient_home_query_service_pb2

from acme_data.domains.datahub import hooks
from acme_data.domains.datahub.adapters import WorkspaceNotificationUnsubscribeWorkspaceUpdates2Adapter
from acme_data.domains.datahub.dependencies import Dependencies
from acme_data.domains.datahub.models import WorkspaceNotificationStreamWorkspaceNotices1Command
from acme_data.domains.datahub.models import WorkspaceNotificationStreamWorkspaceNotices2Command
from acme_data.domains.datahub.models import to_workspace_notification_stream_workspace_notices1_command
from acme_data.domains.datahub.models import to_workspace_notification_stream_workspace_notices2_command
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import run_steps
from acme_data.platform.tenancy import tenant_id
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


async def handle_get_workspace_preferences(
    deps: Dependencies,
    request: datahub_v1_workspace_notification_service_pb2.GetWorkspacePreferencesRequest
) -> datahub_v1_workspace_notification_service_pb2.GetWorkspacePreferencesResponse:
    """Returns a workspace."""
    response = datahub_v1_workspace_notification_service_pb2.GetWorkspacePreferencesResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('GetWorkspacePreferences', extra={'fields': {'domain': 'datahub'}})
        await deps.repository.audit(request.context.tenant_id, 'GetWorkspacePreferences', {})
        response_0 = datahub_v1_notebook_approval_service_pb2.DelegateNotebookApprovalResponse()
        outgoing_0 = datahub_v1_notebook_approval_service_pb2.DelegateNotebookApprovalRequest(
            context=request.context,
            notebook=datahub_v1_datahub_pb2.Notebook(
                counterparty=datahub_v1_refs_pb2.WorkspaceRef(workspace_id=request.workspace_id)
            )
        )
        response_0 = await deps.clients.datahub_notebook_approval.DelegateNotebookApproval(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.notebook.audit.updated_by
        if returned_0_0:
            response.workspace.audit.updated_by = returned_0_0
        echoed_0 = request.workspace_id
        response.workspace.workspace_id = echoed_0
        return response


async def handle_list_workspace_subscriptions(
    deps: Dependencies,
    request: datahub_v1_workspace_notification_service_pb2.ListWorkspaceSubscriptionsRequest
) -> datahub_v1_workspace_notification_service_pb2.ListWorkspaceSubscriptionsResponse:
    """Lists workspaces a page at a time."""
    response = datahub_v1_workspace_notification_service_pb2.ListWorkspaceSubscriptionsResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('ListWorkspaceSubscriptions', extra={'fields': {'order_by': request.order_by}})
        await deps.repository.audit(
            request.context.tenant_id,
            'ListWorkspaceSubscriptions',
            {'order_by': request.order_by}
        )
        return response


async def handle_notify_workspace_watchers(
    deps: Dependencies,
    request: datahub_v1_workspace_notification_service_pb2.NotifyWorkspaceWatchersRequest
) -> datahub_v1_workspace_notification_service_pb2.NotifyWorkspaceWatchersResponse:
    """Notifys a workspace."""
    response = datahub_v1_workspace_notification_service_pb2.NotifyWorkspaceWatchersResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('NotifyWorkspaceWatchers', extra={'fields': {'channel': request.details.channel}})
        await deps.repository.audit(
            request.context.tenant_id,
            'NotifyWorkspaceWatchers',
            {'channel': request.details.channel}
        )
        response_0 = patientapp_v1_patient_home_query_service_pb2.BrowsePatientHomesResponse()
        response_1 = metrics_v1_metric_series_validation_service_pb2.PreviewMetricSeriesResponse()
        response_2 = datahub_v1_workspace_integration_service_pb2.ReplayWorkspaceEventsResponse()
        outgoing_0 = patientapp_v1_patient_home_query_service_pb2.BrowsePatientHomesRequest(
            context=request.context,
            filter=patientapp_v1_patient_home_query_service_pb2.BrowsePatientHomesRequest.Filter(
                created_after=request.context.deadline,
                labels=dict(request.details.variables),
                owner_id=request.workspace_id
            )
        )
        response_0 = await deps.clients.patientapp_patient_home_query.BrowsePatientHomes(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = metrics_v1_metric_series_validation_service_pb2.PreviewMetricSeriesRequest(
            context=request.context,
            details=metrics_v1_metric_series_validation_service_pb2.PreviewMetricSeriesRequest.Details(
                contact=common_v1_contact_pb2.ContactInfo(name=request.details.recipient.name)
            )
        )
        method_name_1 = 'PreviewMetricSeries'
        response_1 = await getattr(
            deps.clients.metrics_metric_series_validation,
            method_name_1
        )(outgoing_1, timeout=deps.settings.timeout)
        fields_2: dict[str, Any] = {
            'context': request.context,
            'details': {'message_id': response_0.result.message},
            'reason': request.reason,
            'workspace_id': request.workspace_id
        }
        outgoing_2 = datahub_v1_workspace_integration_service_pb2.ReplayWorkspaceEventsRequest(**fields_2)
        response_2 = await deps.clients.datahub_workspace_integration.ReplayWorkspaceEvents(
            outgoing_2,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.result.status
        if returned_0_0:
            response.result.status = returned_0_0
        returned_1_0 = response_1.outcome.status
        if returned_1_0:
            response.result.status = returned_1_0
        returned_2_0 = response_2.workspace.customer.email
        if returned_2_0:
            response.workspace.assignee.email = returned_2_0
        returned_2_1 = response_2.workspace.audit.etag
        if returned_2_1:
            response.workspace.audit.etag = returned_2_1
        echoed_0 = request.workspace_id
        response.workspace.workspace_id = echoed_0
        echoed_1 = request.details.recipient.preferred_channel
        response.workspace.requester.preferred_channel = echoed_1
        return response


async def handle_send_workspace_test_notice(
    deps: Dependencies,
    request: datahub_v1_workspace_notification_service_pb2.SendWorkspaceTestNoticeRequest
) -> datahub_v1_workspace_notification_service_pb2.SendWorkspaceTestNoticeResponse:
    """Sends a workspace."""
    response = datahub_v1_workspace_notification_service_pb2.SendWorkspaceTestNoticeResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('SendWorkspaceTestNotice', extra={'fields': {'channel': request.details.channel}})
        await deps.repository.audit(
            request.context.tenant_id,
            'SendWorkspaceTestNotice',
            {'channel': request.details.channel}
        )
        response_0 = metrics_v1_metric_series_validation_service_pb2.NormalizeMetricSeriesResponse()
        response_1 = customers_v1_preference_reporting_service_pb2.StreamPreferenceMetricsResponse()
        response_2 = datahub_v1_notebook_reporting_service_pb2.GenerateNotebookReportResponse()
        response_3 = datahub_v1_notebook_integration_service_pb2.ConnectNotebookSourceResponse()
        outgoing_0 = metrics_v1_metric_series_validation_service_pb2.NormalizeMetricSeriesRequest(
            context=request.context,
            details=metrics_v1_metric_series_validation_service_pb2.NormalizeMetricSeriesRequest.Details(
                contact=common_v1_contact_pb2.ContactInfo(
                    email=request.details.recipient.email,
                    name=request.details.recipient.name,
                    phone=request.details.recipient.phone,
                    preferred_channel=request.details.recipient.preferred_channel
                )
            )
        )
        response_0 = await deps.clients.metrics_metric_series_validation.NormalizeMetricSeries(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = customers_v1_preference_reporting_service_pb2.StreamPreferenceMetricsRequest(
            context=request.context,
            subscriber=common_v1_contact_pb2.ContactInfo(preferred_channel=request.details.recipient.preferred_channel)
        )
        async for chunk_1 in deps.clients.customers_preference_reporting.StreamPreferenceMetrics(
            outgoing_1,
            timeout=deps.settings.timeout
        ):
            response_1 = chunk_1
        outgoing_2 = datahub_v1_notebook_reporting_service_pb2.GenerateNotebookReportRequest()
        outgoing_2.context.CopyFrom(request.context)
        outgoing_2.reason = request.reason
        outgoing_2.annotations.update(dict(request.annotations))
        outgoing_2.details.filters.update(dict(response_0.metric_series.specs))
        merged_2 = datahub_v1_notebook_reporting_service_pb2.GenerateNotebookReportRequest()
        merged_2.MergeFrom(outgoing_2)
        outgoing_2.CopyFrom(merged_2)
        response_2 = await deps.clients.datahub_notebook_reporting.GenerateNotebookReport(
            outgoing_2,
            timeout=deps.settings.timeout
        )
        outgoing_3 = datahub_v1_notebook_integration_service_pb2.ConnectNotebookSourceRequest(
            annotations=dict(request.annotations),
            context=request.context,
            details=datahub_v1_notebook_integration_service_pb2.ConnectNotebookSourceRequest.Details(
                message_id=response_2.result.message
            ),
            reason=request.reason
        )
        envelope_3 = AnyMessage()
        envelope_3.Pack(outgoing_3)
        outgoing_3 = datahub_v1_notebook_integration_service_pb2.ConnectNotebookSourceRequest()
        if not envelope_3.Unpack(outgoing_3):
            raise ValueError("partner envelope contains the wrong request type")
        response_3 = await deps.clients.datahub_notebook_integration.ConnectNotebookSource(
            outgoing_3,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.result.status
        if returned_0_0:
            response.outcome.status = returned_0_0
        returned_2_0 = response_2.result.message
        if returned_2_0:
            response.outcome.message = returned_2_0
        returned_3_0 = response_3.outcome.reference_id
        if returned_3_0:
            response.outcome.reference_id = returned_3_0
        returned_3_1 = response_3.notebook.counterparty.display_name
        if returned_3_1:
            response.workspace.assignee.display_name = returned_3_1
        echoed_0 = request.workspace_id
        response.workspace.workspace_id = echoed_0
        echoed_1 = request.details.recipient.phone
        response.workspace.requester.phone = echoed_1
        return response


async def handle_stream_workspace_notices(
    deps: Dependencies,
    request: datahub_v1_workspace_notification_service_pb2.StreamWorkspaceNoticesRequest
) -> datahub_v1_workspace_notification_service_pb2.StreamWorkspaceNoticesResponse:
    """Streams the changes of workspaces as they happen."""
    response = datahub_v1_workspace_notification_service_pb2.StreamWorkspaceNoticesResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('StreamWorkspaceNotices', extra={'fields': {'max_events': request.max_events}})
        await deps.repository.audit(
            request.context.tenant_id,
            'StreamWorkspaceNotices',
            {'max_events': request.max_events}
        )
        response_0 = datahub_v1_notebook_workflow_service_pb2.CancelNotebookWorkflowResponse()
        response_1 = metrics_v1_dashboard_sync_service_pb2.PullDashboardsResponse()
        response_2 = metrics_v1_metric_series_validation_service_pb2.ScoreMetricSeriesResponse()
        outgoing_0 = datahub_v1_notebook_workflow_service_pb2.CancelNotebookWorkflowRequest(
            context=request.context,
            details=datahub_v1_notebook_workflow_service_pb2.CancelNotebookWorkflowRequest.Details(
                notify=common_v1_contact_pb2.ContactInfo(
                    email=request.subscriber.email,
                    name=request.subscriber.name,
                    preferred_channel=request.subscriber.preferred_channel
                )
            ),
            notebook=datahub_v1_datahub_pb2.Notebook(
                billing_address=common_v1_address_pb2.PostalAddress(region=request.filter.region)
            )
        )
        response_0 = await deps.clients.datahub_notebook_workflow.CancelNotebookWorkflow(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        command_1 = WorkspaceNotificationStreamWorkspaceNotices1Command(
            context=request.context,
            dashboard_audit_etag=response_0.notebook.audit.etag,
            dashboard_audit_created_by=response_0.notebook.audit.created_by,
            dashboard_card_network=response_0.notebook.card.network,
            dashboard_counterparty_display_name=response_0.notebook.counterparty.display_name
        )
        outgoing_1 = to_workspace_notification_stream_workspace_notices1_command(command_1)
        response_1 = await deps.clients.metrics_dashboard_sync.PullDashboards(outgoing_1, timeout=deps.settings.timeout)
        command_2 = WorkspaceNotificationStreamWorkspaceNotices2Command.model_validate(
            {'context': request.context, 'metric_series_audit_etag': response_1.dashboard.audit.etag}
        )
        outgoing_2 = to_workspace_notification_stream_workspace_notices2_command(command_2)
        response_2 = await deps.clients.metrics_metric_series_validation.ScoreMetricSeries(
            outgoing_2,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.notebook.audit.updated_by
        if returned_0_0:
            response.workspace.audit.updated_by = returned_0_0
        returned_0_1 = response_0.notebook.audit.updated_at
        if returned_0_1.ListFields():
            response.workspace.audit.updated_at.MergeFrom(returned_0_1)
        returned_1_0 = response_1.dashboard.audit.updated_by
        if returned_1_0:
            response.workspace.audit.updated_by = returned_1_0
        returned_1_1 = response_1.dashboard.audit.created_at
        if returned_1_1.ListFields():
            response.workspace.audit.created_at.MergeFrom(returned_1_1)
        returned_2_0 = response_2.result.message
        if returned_2_0:
            response.result.message = returned_2_0
        echoed_0 = request.subscriber.email
        response.workspace.requester.email = echoed_0
        echoed_1 = request.subscriber.phone
        response.workspace.requester.phone = echoed_1
        return response


async def handle_subscribe_workspace_updates(
    deps: Dependencies,
    request: datahub_v1_workspace_notification_service_pb2.SubscribeWorkspaceUpdatesRequest
) -> datahub_v1_workspace_notification_service_pb2.SubscribeWorkspaceUpdatesResponse:
    """Subscribes a workspace."""
    response = datahub_v1_workspace_notification_service_pb2.SubscribeWorkspaceUpdatesResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('SubscribeWorkspaceUpdates', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'SubscribeWorkspaceUpdates', {'reason': request.reason})
        response_0 = datahub_v1_workspace_integration_service_pb2.ReplayWorkspaceEventsResponse()
        response_1 = fanportal_v1_fan_session_query_service_pb2.CountFanSessionsResponse()
        response_2 = datahub_v1_data_share_validation_service_pb2.ExplainDataShareDecisionResponse()
        outgoing_0 = datahub_v1_workspace_integration_service_pb2.ReplayWorkspaceEventsRequest(
            annotations=dict(request.annotations),
            context=request.context
        )
        response_0 = await deps.clients.datahub_workspace_integration.ReplayWorkspaceEvents(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = fanportal_v1_fan_session_query_service_pb2.CountFanSessionsRequest(
            context=request.context,
            filter=fanportal_v1_fan_session_query_service_pb2.CountFanSessionsRequest.Filter(
                created_after=response_0.workspace.sla.due_at
            )
        )
        response_1 = await hooks.workspace_notification_subscribe_workspace_updates1(
            deps.clients.fanportal_fan_session_query,
            outgoing_1,
            deps.settings.timeout
        )
        outgoing_2 = datahub_v1_data_share_validation_service_pb2.ExplainDataShareDecisionRequest()
        outgoing_2.context.CopyFrom(request.context)
        outgoing_2.details.contact.preferred_channel = request.details.recipient.preferred_channel
        outgoing_2.data_share.audit.updated_at.CopyFrom(response_0.workspace.audit.updated_at)
        outgoing_2.data_share.audit.created_at.CopyFrom(response_0.workspace.audit.created_at)
        outgoing_2.context.tenant_id = tenant_id.get()
        response_2 = await deps.clients.datahub_data_share_validation.ExplainDataShareDecision(
            outgoing_2,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.workspace.sla.breached
        if returned_0_0:
            response.workspace.sla.breached = returned_0_0
        returned_1_0 = response_1.result.message
        if returned_1_0:
            response.outcome.message = returned_1_0
        returned_2_0 = response_2.data_share.audit.etag
        if returned_2_0:
            response.workspace.audit.etag = returned_2_0
        returned_2_1 = response_2.result.status
        if returned_2_1:
            response.outcome.status = returned_2_1
        echoed_0 = request.workspace_id
        response.workspace.workspace_id = echoed_0
        echoed_1 = request.details.recipient.email
        response.workspace.requester.email = echoed_1
        return response


async def handle_unsubscribe_workspace_updates(
    deps: Dependencies,
    request: datahub_v1_workspace_notification_service_pb2.UnsubscribeWorkspaceUpdatesRequest
) -> datahub_v1_workspace_notification_service_pb2.UnsubscribeWorkspaceUpdatesResponse:
    """Unsubscribes a workspace."""
    response = datahub_v1_workspace_notification_service_pb2.UnsubscribeWorkspaceUpdatesResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('UnsubscribeWorkspaceUpdates', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(
            request.context.tenant_id,
            'UnsubscribeWorkspaceUpdates',
            {'reason': request.reason}
        )
        response_0 = audit_v1_audit_event_validation_service_pb2.ValidateAuditEventResponse()
        response_1 = analytics_v1_analytics_report_approval_service_pb2.RecallAnalyticsReportResponse()
        response_2 = customers_v1_household_workflow_service_pb2.ResumeHouseholdWorkflowResponse()
        outgoing_0 = audit_v1_audit_event_validation_service_pb2.ValidateAuditEventRequest(
            context=request.context,
            details=audit_v1_audit_event_validation_service_pb2.ValidateAuditEventRequest.Details(
                contact=common_v1_contact_pb2.ContactInfo(
                    email=request.details.recipient.email,
                    name=request.details.recipient.name,
                    phone=request.details.recipient.phone,
                    preferred_channel=request.details.recipient.preferred_channel
                )
            )
        )
        response_0 = await deps.clients.audit_audit_event_validation.ValidateAuditEvent(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = analytics_v1_analytics_report_approval_service_pb2.RecallAnalyticsReportRequest(
            analytics_report=analytics_v1_analytics_pb2.AnalyticsReport(
                counterparty=customers_v1_refs_pb2.CustomerRef(email=request.details.recipient.email)
            ),
            context=request.context,
            details=analytics_v1_analytics_report_approval_service_pb2.RecallAnalyticsReportRequest.Details(
                approver=identity_v1_refs_pb2.UserRef(display_name=response_0.audit_event.subject.display_name),
                effective_at=response_0.outcome.effective_at
            )
        )
        steps_1 = [
            partial(
                deps.clients.analytics_analytics_report_approval.RecallAnalyticsReport,
                outgoing_1,
                timeout=deps.settings.timeout
            )
        ]
        results_1 = await run_steps(steps_1)
        response_1 = results_1[-1]
        outgoing_2 = customers_v1_household_workflow_service_pb2.ResumeHouseholdWorkflowRequest(
            context=request.context,
            household=customers_v1_customers_pb2.Household(
                children=[
                    customers_v1_customers_pb2.Household(
                        children=[
                            customers_v1_customers_pb2.Household(
                                audit=common_v1_audit_pb2.AuditInfo(etag=response_1.analytics_report.audit.etag),
                                location=common_v1_address_pb2.PostalAddress(
                                    locality=response_1.analytics_report.billing_address.locality,
                                    postal_code=response_1.analytics_report.billing_address.postal_code
                                )
                            )
                        ]
                    )
                ]
            )
        )
        response_2 = await WorkspaceNotificationUnsubscribeWorkspaceUpdates2Adapter(
            deps.clients.customers_household_workflow,
            deps.settings.timeout
        )(outgoing_2)
        returned_0_0 = response_0.result.correlation_id
        if returned_0_0:
            response.result.correlation_id = returned_0_0
        returned_1_0 = response_1.analytics_report.audit.created_at
        if returned_1_0.ListFields():
            response.workspace.audit.created_at.MergeFrom(returned_1_0)
        returned_1_1 = response_1.result.reference_ids
        response.result.reference_ids.extend(returned_1_1)
        returned_2_0 = response_2.result.details
        response.result.details.update(returned_2_0)
        echoed_0 = request.workspace_id
        response.workspace.workspace_id = echoed_0
        echoed_1 = request.details.recipient.email
        response.workspace.requester.email = echoed_1
        return response
