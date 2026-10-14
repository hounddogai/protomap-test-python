"""Reusable transport mixin for NotebookIntegrationService."""

from __future__ import annotations

from collections.abc import AsyncIterator
from functools import partial
from typing import Any
from typing import cast
import logging

from google.protobuf.any_pb2 import Any as AnyMessage
from google.protobuf.json_format import MessageToDict
from google.protobuf.json_format import ParseDict
import grpc

from acme.analytics.v1 import analytics_event_approval_service_pb2 as analytics_v1_analytics_event_approval_service_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.customers.v1 import customer_segment_sync_service_pb2 as customers_v1_customer_segment_sync_service_pb2
from acme.customers.v1 import (
    customer_segment_sync_service_pb2_grpc as customers_v1_customer_segment_sync_service_pb2_grpc,
)
from acme.customers.v1 import customers_pb2 as customers_v1_customers_pb2
from acme.customers.v1 import refs_pb2 as customers_v1_refs_pb2
from acme.datahub.v1 import data_share_reporting_service_pb2 as datahub_v1_data_share_reporting_service_pb2
from acme.datahub.v1 import data_share_validation_service_pb2 as datahub_v1_data_share_validation_service_pb2
from acme.datahub.v1 import datahub_pb2 as datahub_v1_datahub_pb2
from acme.datahub.v1 import notebook_approval_service_pb2 as datahub_v1_notebook_approval_service_pb2
from acme.datahub.v1 import notebook_integration_service_pb2 as datahub_v1_notebook_integration_service_pb2
from acme.datahub.v1 import notebook_reporting_service_pb2 as datahub_v1_notebook_reporting_service_pb2
from acme.datahub.v1 import workspace_approval_service_pb2 as datahub_v1_workspace_approval_service_pb2
from acme.datahub.v1 import workspace_approval_service_pb2_grpc as datahub_v1_workspace_approval_service_pb2_grpc
from acme.datahub.v1 import workspace_integration_service_pb2 as datahub_v1_workspace_integration_service_pb2
from acme.datahub.v1 import workspace_workflow_service_pb2 as datahub_v1_workspace_workflow_service_pb2
from acme.edgegateway.v1 import route_binding_query_service_pb2 as edgegateway_v1_route_binding_query_service_pb2
from acme.featurestore.v1 import (
    feature_value_workflow_service_pb2 as featurestore_v1_feature_value_workflow_service_pb2,
)
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.metrics.v1 import dashboard_sync_service_pb2 as metrics_v1_dashboard_sync_service_pb2
from acme.metrics.v1 import metric_series_validation_service_pb2 as metrics_v1_metric_series_validation_service_pb2

from acme_data.domains.datahub import hooks
from acme_data.domains.datahub.adapters import NotebookIntegrationConnectNotebookSource2Adapter
from acme_data.domains.datahub.adapters import NotebookIntegrationConnectNotebookSource2Port
from acme_data.domains.datahub.adapters import NotebookIntegrationDisconnectNotebookSource1Adapter
from acme_data.domains.datahub.dependencies import Dependencies
from acme_data.domains.datahub.models import NotebookIntegrationAcknowledgeNotebookEvent1Command
from acme_data.domains.datahub.models import NotebookIntegrationAcknowledgeNotebookEvent2Command
from acme_data.domains.datahub.models import to_notebook_integration_acknowledge_notebook_event1_command
from acme_data.domains.datahub.models import to_notebook_integration_acknowledge_notebook_event2_command
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import run_steps
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_id
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class NotebookIntegrationServicerHandlers:
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    async def AcknowledgeNotebookEvent(
        self, request: datahub_v1_notebook_integration_service_pb2.AcknowledgeNotebookEventRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_notebook_integration_service_pb2.AcknowledgeNotebookEventResponse:
        """Acknowledges a notebook."""
        return await self.handle_acknowledge_notebook_event(request)

    @rpc_errors
    async def ConnectNotebookSource(
        self, request: datahub_v1_notebook_integration_service_pb2.ConnectNotebookSourceRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_notebook_integration_service_pb2.ConnectNotebookSourceResponse:
        """Connects a notebook."""
        return await self.handle_connect_notebook_source(request)

    @rpc_errors
    async def DisconnectNotebookSource(
        self, request: datahub_v1_notebook_integration_service_pb2.DisconnectNotebookSourceRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_notebook_integration_service_pb2.DisconnectNotebookSourceResponse:
        """Disconnects a notebook."""
        return await self.handle_disconnect_notebook_source(request)

    @rpc_errors
    async def IngestNotebookEvents(
        self, requests: AsyncIterator[
            datahub_v1_notebook_integration_service_pb2.IngestNotebookEventsRequest
        ], context: grpc.aio.ServicerContext,
    ) -> datahub_v1_notebook_integration_service_pb2.IngestNotebookEventsResponse:
        """Takes a stream of notebooks and answers once at the end."""
        response = datahub_v1_notebook_integration_service_pb2.IngestNotebookEventsResponse()
        async for request in requests:
            response.MergeFrom(await self.handle_ingest_notebook_events(request))
        return response

    @stream_errors
    async def RelayNotebookMessages(
        self, requests: AsyncIterator[
            datahub_v1_notebook_integration_service_pb2.RelayNotebookMessagesRequest
        ], context: grpc.aio.ServicerContext,
    ) -> AsyncIterator[datahub_v1_notebook_integration_service_pb2.RelayNotebookMessagesResponse]:
        """Exchanges changes of notebooks with a peer."""
        async for request in requests:
            yield await self.handle_relay_notebook_messages(request)

    @rpc_errors
    async def ReplayNotebookEvents(
        self, request: datahub_v1_notebook_integration_service_pb2.ReplayNotebookEventsRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_notebook_integration_service_pb2.ReplayNotebookEventsResponse:
        """Replays a notebook."""
        return await self.handle_replay_notebook_events(request)

    async def handle_acknowledge_notebook_event(
        self,
        request: datahub_v1_notebook_integration_service_pb2.AcknowledgeNotebookEventRequest
    ) -> datahub_v1_notebook_integration_service_pb2.AcknowledgeNotebookEventResponse:
        """Acknowledges a notebook."""
        deps = self.deps
        response = datahub_v1_notebook_integration_service_pb2.AcknowledgeNotebookEventResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('AcknowledgeNotebookEvent', extra={'fields': {'endpoint': request.details.endpoint}})
            await deps.repository.audit(
                request.context.tenant_id,
                'AcknowledgeNotebookEvent',
                {'endpoint': request.details.endpoint}
            )
            response_0 = datahub_v1_workspace_approval_service_pb2.CommentWorkspaceApprovalResponse()
            response_1 = metrics_v1_metric_series_validation_service_pb2.CheckMetricSeriesEligibilityResponse()
            response_2 = datahub_v1_data_share_reporting_service_pb2.GenerateDataShareReportResponse()
            response_3 = datahub_v1_notebook_approval_service_pb2.EscalateNotebookResponse()
            outgoing_0 = datahub_v1_workspace_approval_service_pb2.CommentWorkspaceApprovalRequest(
                annotations=dict(request.annotations),
                context=request.context,
                details=datahub_v1_workspace_approval_service_pb2.CommentWorkspaceApprovalRequest.Details(
                    approver=identity_v1_refs_pb2.UserRef(user_id=request.context.actor.user_id)
                ),
                reason=request.reason,
                workspace=datahub_v1_datahub_pb2.Workspace(
                    assignee=identity_v1_refs_pb2.UserRef(email=request.context.actor.email)
                )
            )
            registered_0 = cast(
                datahub_v1_workspace_approval_service_pb2_grpc.WorkspaceApprovalServiceStub,
                deps.clients.registry['acme.datahub.v1.WorkspaceApprovalService']
            )
            response_0 = await registered_0.CommentWorkspaceApproval(outgoing_0, timeout=deps.settings.timeout)
            command_1 = NotebookIntegrationAcknowledgeNotebookEvent1Command(
                context=request.context,
                metric_series_owner_email=response_0.workspace.requester.email
            )
            outgoing_1 = to_notebook_integration_acknowledge_notebook_event1_command(command_1)
            response_1 = await deps.clients.metrics_metric_series_validation.CheckMetricSeriesEligibility(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            command_2 = NotebookIntegrationAcknowledgeNotebookEvent2Command.model_validate(
                {
                    'context': request.context,
                    'annotations': dict(request.annotations),
                    'reason': request.reason,
                    'details_filters': dict(response_1.metric_series.specs)
                }
            )
            outgoing_2 = to_notebook_integration_acknowledge_notebook_event2_command(command_2)
            response_2 = await deps.clients.datahub_data_share_reporting.GenerateDataShareReport(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            outgoing_3 = datahub_v1_notebook_approval_service_pb2.EscalateNotebookRequest(
                context=request.context,
                details=datahub_v1_notebook_approval_service_pb2.EscalateNotebookRequest.Details(
                    approver=identity_v1_refs_pb2.UserRef(email=response_0.workspace.customer.email)
                ),
                notebook=datahub_v1_datahub_pb2.Notebook(
                    audit=common_v1_audit_pb2.AuditInfo(updated_at=response_1.metric_series.audit.updated_at)
                )
            )
            send_3 = partial(deps.clients.datahub_notebook_approval.EscalateNotebook, timeout=deps.settings.timeout)
            response_3 = await send_3(outgoing_3)
            returned_0_0 = response_0.result.status
            if returned_0_0:
                response.outcome.status = returned_0_0
            returned_1_0 = response_1.outcome.reference_id
            if returned_1_0:
                response.outcome.reference_id = returned_1_0
            returned_1_1 = response_1.metric_series.owner.display_name
            if returned_1_1:
                response.notebook.counterparty.display_name = returned_1_1
            returned_2_0 = response_2.result.status
            if returned_2_0:
                response.result.status = returned_2_0
            returned_3_0 = response_3.notebook.counterparty
            if returned_3_0.ListFields():
                response.notebook.counterparty.MergeFrom(returned_3_0)
            echoed_0 = request.notebook_id
            response.notebook.notebook_id = echoed_0
            return response

    async def handle_connect_notebook_source(
        self,
        request: datahub_v1_notebook_integration_service_pb2.ConnectNotebookSourceRequest
    ) -> datahub_v1_notebook_integration_service_pb2.ConnectNotebookSourceResponse:
        """Connects a notebook."""
        deps = self.deps
        response = datahub_v1_notebook_integration_service_pb2.ConnectNotebookSourceResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ConnectNotebookSource', extra={'fields': {'endpoint': request.details.endpoint}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ConnectNotebookSource',
                {'endpoint': request.details.endpoint}
            )
            response_0 = analytics_v1_analytics_event_approval_service_pb2.EscalateAnalyticsEventResponse()
            response_1 = datahub_v1_data_share_validation_service_pb2.NormalizeDataShareResponse()
            response_2 = datahub_v1_workspace_integration_service_pb2.AcknowledgeWorkspaceEventResponse()
            outgoing_0 = analytics_v1_analytics_event_approval_service_pb2.EscalateAnalyticsEventRequest(
                annotations=dict(request.annotations),
                context=request.context,
                details=analytics_v1_analytics_event_approval_service_pb2.EscalateAnalyticsEventRequest.Details(
                    approver=identity_v1_refs_pb2.UserRef(email=request.context.actor.email)
                ),
                reason=request.reason
            )
            response_0 = await hooks.notebook_integration_connect_notebook_source0(
                deps.clients.analytics_analytics_event_approval,
                outgoing_0,
                deps.settings.timeout
            )
            outgoing_1 = datahub_v1_data_share_validation_service_pb2.NormalizeDataShareRequest()
            outgoing_1.context.CopyFrom(request.context)
            field_1_1_part_1 = outgoing_1.data_share.lines.add()
            field_1_1_part_1.attributes.update(dict(response_0.analytics_event.attributes))
            outgoing_1.annotations.update(dict(request.annotations))
            outgoing_1.reason = request.reason
            outgoing_1.data_share.counterparty.display_name = response_0.analytics_event.subject.display_name
            outgoing_1.context.tenant_id = tenant_id.get()
            response_1 = await deps.clients.datahub_data_share_validation.NormalizeDataShare(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = datahub_v1_workspace_integration_service_pb2.AcknowledgeWorkspaceEventRequest(
                context=request.context,
                details=datahub_v1_workspace_integration_service_pb2.AcknowledgeWorkspaceEventRequest.Details(
                    message_id=request.details.message_id
                )
            )
            port_2: NotebookIntegrationConnectNotebookSource2Port = NotebookIntegrationConnectNotebookSource2Adapter(
                deps.clients.datahub_workspace_integration,
                deps.settings.timeout
            )
            response_2 = await port_2.execute(outgoing_2)
            returned_0_0 = response_0.analytics_event.attributes
            returned_0_0_part_1 = response.notebook.lines.add()
            returned_0_0_part_1.attributes.update(returned_0_0)
            returned_0_1 = response_0.outcome.next_steps
            response.outcome.next_steps.extend(returned_0_1)
            returned_1_0 = response_1.data_share.due_at
            if returned_1_0.ListFields():
                response.notebook.due_at.MergeFrom(returned_1_0)
            returned_2_0 = response_2.outcome.reference_id
            if returned_2_0:
                response.outcome.reference_id = returned_2_0
            echoed_0 = request.notebook_id
            response.notebook.notebook_id = echoed_0
            return response

    async def handle_disconnect_notebook_source(
        self,
        request: datahub_v1_notebook_integration_service_pb2.DisconnectNotebookSourceRequest
    ) -> datahub_v1_notebook_integration_service_pb2.DisconnectNotebookSourceResponse:
        """Disconnects a notebook."""
        deps = self.deps
        response = datahub_v1_notebook_integration_service_pb2.DisconnectNotebookSourceResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('DisconnectNotebookSource', extra={'fields': {'endpoint': request.details.endpoint}})
            await deps.repository.audit(
                request.context.tenant_id,
                'DisconnectNotebookSource',
                {'endpoint': request.details.endpoint}
            )
            response_0 = customers_v1_customer_segment_sync_service_pb2.SyncCustomerSegmentsResponse()
            response_1 = datahub_v1_workspace_workflow_service_pb2.StartWorkspaceWorkflowResponse()
            response_2 = featurestore_v1_feature_value_workflow_service_pb2.ResumeFeatureValueWorkflowResponse()
            response_3 = edgegateway_v1_route_binding_query_service_pb2.SummarizeRouteBindingsResponse()
            outgoing_0 = customers_v1_customer_segment_sync_service_pb2.SyncCustomerSegmentsRequest(
                annotations=dict(request.annotations),
                context=request.context,
                customer_segment=customers_v1_customers_pb2.CustomerSegment(
                    block=customers_v1_customers_pb2.CustomerSegmentBlockAction(reason=request.reason),
                    owner=identity_v1_refs_pb2.UserRef(email=request.context.actor.email)
                )
            )
            steps_0 = [
                partial(
                    deps.clients.customers_customer_segment_sync.SyncCustomerSegments,
                    outgoing_0,
                    timeout=deps.settings.timeout
                )
            ]
            results_0 = await run_steps(steps_0)
            response_0 = results_0[-1]
            outgoing_1 = datahub_v1_workspace_workflow_service_pb2.StartWorkspaceWorkflowRequest(
                context=request.context,
                workspace=datahub_v1_datahub_pb2.Workspace(
                    audit=common_v1_audit_pb2.AuditInfo(
                        created_at=response_0.customer_segment.audit.created_at,
                        created_by=response_0.customer_segment.audit.created_by,
                        updated_by=response_0.customer_segment.audit.updated_by
                    ),
                    customer=customers_v1_refs_pb2.CustomerRef(
                        display_name=response_0.customer_segment.owner.display_name
                    )
                )
            )
            response_1 = await NotebookIntegrationDisconnectNotebookSource1Adapter(
                deps.clients.datahub_workspace_workflow,
                deps.settings.timeout
            )(outgoing_1)
            outgoing_2 = featurestore_v1_feature_value_workflow_service_pb2.ResumeFeatureValueWorkflowRequest(
                context=request.context,
                details=featurestore_v1_feature_value_workflow_service_pb2.ResumeFeatureValueWorkflowRequest.Details(
                    notify=common_v1_contact_pb2.ContactInfo(
                        email=response_1.workspace.customer.email,
                        phone=response_1.workspace.requester.phone
                    )
                )
            )
            response_2 = cast(featurestore_v1_feature_value_workflow_service_pb2.ResumeFeatureValueWorkflowResponse, await deps.bus.request(
                'acme.datahub.v1.NotebookIntegrationService/DisconnectNotebookSource/2', outgoing_2, deps.settings.timeout,
            ))
            outgoing_3 = edgegateway_v1_route_binding_query_service_pb2.SummarizeRouteBindingsRequest(
                context=request.context,
                reason=response_0.customer_segment.block.reason
            )
            response_3 = await deps.clients.edgegateway_route_binding_query.SummarizeRouteBindings(
                outgoing_3,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.details
            response.result.details.update(returned_0_0)
            returned_1_0 = response_1.workspace.assignee.display_name
            if returned_1_0:
                response.notebook.counterparty.display_name = returned_1_0
            returned_1_1 = response_1.outcome.reference_id
            if returned_1_1:
                response.outcome.reference_id = returned_1_1
            returned_2_0 = response_2.outcome.effective_at
            if returned_2_0.ListFields():
                response.outcome.effective_at.MergeFrom(returned_2_0)
            returned_3_0 = response_3.result.message
            if returned_3_0:
                response.outcome.message = returned_3_0
            returned_3_1 = response_3.result.correlation_id
            if returned_3_1:
                response.result.correlation_id = returned_3_1
            echoed_0 = request.notebook_id
            response.notebook.notebook_id = echoed_0
            return response

    async def handle_ingest_notebook_events(
        self,
        request: datahub_v1_notebook_integration_service_pb2.IngestNotebookEventsRequest
    ) -> datahub_v1_notebook_integration_service_pb2.IngestNotebookEventsResponse:
        """Takes a stream of notebooks and answers once at the end."""
        deps = self.deps
        response = datahub_v1_notebook_integration_service_pb2.IngestNotebookEventsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('IngestNotebookEvents', extra={'fields': {'sequence': request.sequence}})
            await deps.repository.audit(
                request.context.tenant_id,
                'IngestNotebookEvents',
                {'sequence': request.sequence}
            )
            if request.WhichOneof('chunk') == 'record':
                await deps.repository.save_notebook(request.context.tenant_id, request.record)
            response_0 = datahub_v1_notebook_reporting_service_pb2.ShareNotebookReportResponse()
            response_1 = metrics_v1_dashboard_sync_service_pb2.PushDashboardResponse()
            outgoing_0 = datahub_v1_notebook_reporting_service_pb2.ShareNotebookReportRequest()
            outgoing_0.context.CopyFrom(request.context)
            if request.WhichOneof('chunk') == 'header':
                outgoing_0.details.recipient.phone = request.header.submitted_by.phone
            if request.WhichOneof('chunk') == 'header':
                outgoing_0.details.recipient.email = request.header.submitted_by.email
            if request.WhichOneof('chunk') == 'header':
                outgoing_0.details.recipient.preferred_channel = request.header.submitted_by.preferred_channel
            response_0 = await deps.clients.datahub_notebook_reporting.ShareNotebookReport(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            fields_1: dict[str, Any] = {
                'context': request.context,
                'dashboard': {
                    'audit': {
                        'created_at': request.record.audit.created_at,
                        'created_by': response_0.notebook.audit.created_by
                    },
                    'billing_address': {'recipient': response_0.notebook.billing_address.recipient}
                }
            }
            outgoing_1 = metrics_v1_dashboard_sync_service_pb2.PushDashboardRequest(**fields_1)
            response_1 = await deps.clients.metrics_dashboard_sync.PushDashboard(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.result.message = returned_0_0
            returned_1_0 = response_1.result.correlation_id
            if returned_1_0:
                response.result.correlation_id = returned_1_0
            return response

    async def handle_relay_notebook_messages(
        self,
        request: datahub_v1_notebook_integration_service_pb2.RelayNotebookMessagesRequest
    ) -> datahub_v1_notebook_integration_service_pb2.RelayNotebookMessagesResponse:
        """Exchanges changes of notebooks with a peer."""
        deps = self.deps
        response = datahub_v1_notebook_integration_service_pb2.RelayNotebookMessagesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('RelayNotebookMessages', extra={'fields': {'cursor': request.cursor}})
            await deps.repository.audit(request.context.tenant_id, 'RelayNotebookMessages', {'cursor': request.cursor})
            if request.WhichOneof('frame') == 'change':
                await deps.repository.save_notebook(request.context.tenant_id, request.change)
            response_0 = analytics_v1_analytics_event_approval_service_pb2.ListPendingAnalyticsEventsResponse()
            response_1 = datahub_v1_workspace_workflow_service_pb2.RetryWorkspaceWorkflowResponse()
            response_2 = datahub_v1_workspace_integration_service_pb2.AcknowledgeWorkspaceEventResponse()
            outgoing_0 = analytics_v1_analytics_event_approval_service_pb2.ListPendingAnalyticsEventsRequest(
                context=request.context,
                filter=analytics_v1_analytics_event_approval_service_pb2.ListPendingAnalyticsEventsRequest.Filter(
                    region=request.change.billing_address.region
                )
            )
            document_0 = MessageToDict(outgoing_0, preserving_proto_field_name=True)
            outgoing_0 = ParseDict(
                document_0,
                analytics_v1_analytics_event_approval_service_pb2.ListPendingAnalyticsEventsRequest()
            )
            response_0 = await deps.clients.analytics_analytics_event_approval.ListPendingAnalyticsEvents(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = datahub_v1_workspace_workflow_service_pb2.RetryWorkspaceWorkflowRequest()
            outgoing_1.context.CopyFrom(request.context)
            if request.WhichOneof('frame') == 'change':
                outgoing_1.workspace.audit.created_at.CopyFrom(request.change.audit.created_at)
            if request.WhichOneof('frame') == 'change':
                outgoing_1.workspace.audit.created_by = request.change.audit.created_by
            if request.WhichOneof('frame') == 'change':
                outgoing_1.workspace.customer.display_name = request.change.counterparty.display_name
            response_1 = await deps.clients.datahub_workspace_workflow.RetryWorkspaceWorkflow(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = datahub_v1_workspace_integration_service_pb2.AcknowledgeWorkspaceEventRequest()
            outgoing_2.context.CopyFrom(request.context)
            outgoing_2.workspace_id = response_1.workspace.workspace_id
            merged_2 = datahub_v1_workspace_integration_service_pb2.AcknowledgeWorkspaceEventRequest()
            merged_2.MergeFrom(outgoing_2)
            outgoing_2.CopyFrom(merged_2)
            response_2 = await deps.clients.datahub_workspace_integration.AcknowledgeWorkspaceEvent(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_0)
            returned_1_0 = response_1.workspace.workspace_id
            if returned_1_0:
                response.notebook.counterparty.workspace_id = returned_1_0
            returned_1_1 = response_1.workspace.assignee.display_name
            if returned_1_1:
                response.notebook.counterparty.display_name = returned_1_1
            returned_2_0 = response_2.result.reference_ids
            response.result.reference_ids.extend(returned_2_0)
            returned_2_1 = response_2.workspace.audit.created_at
            if returned_2_1.ListFields():
                response.notebook.audit.created_at.MergeFrom(returned_2_1)
            echoed_0 = request.change.notebook_id
            response.notebook.notebook_id = echoed_0
            echoed_1 = request.change.notes
            response.notebook.notes = echoed_1
            return response

    async def handle_replay_notebook_events(
        self,
        request: datahub_v1_notebook_integration_service_pb2.ReplayNotebookEventsRequest
    ) -> datahub_v1_notebook_integration_service_pb2.ReplayNotebookEventsResponse:
        """Replays a notebook."""
        deps = self.deps
        response = datahub_v1_notebook_integration_service_pb2.ReplayNotebookEventsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ReplayNotebookEvents', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'ReplayNotebookEvents', {'reason': request.reason})
            response_0 = datahub_v1_workspace_approval_service_pb2.DelegateWorkspaceApprovalResponse()
            response_1 = customers_v1_customer_segment_sync_service_pb2.ListCustomerSegmentConflictsResponse()
            outgoing_0 = datahub_v1_workspace_approval_service_pb2.DelegateWorkspaceApprovalRequest(
                annotations=dict(request.annotations),
                context=request.context,
                workspace=datahub_v1_datahub_pb2.Workspace(
                    assignee=identity_v1_refs_pb2.UserRef(
                        email=request.context.actor.email,
                        user_id=request.context.actor.user_id
                    )
                )
            )
            envelope_0 = AnyMessage()
            envelope_0.Pack(outgoing_0)
            outgoing_0 = datahub_v1_workspace_approval_service_pb2.DelegateWorkspaceApprovalRequest()
            if not envelope_0.Unpack(outgoing_0):
                raise ValueError("partner envelope contains the wrong request type")
            response_0 = await deps.clients.datahub_workspace_approval.DelegateWorkspaceApproval(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = customers_v1_customer_segment_sync_service_pb2.ListCustomerSegmentConflictsRequest(
                context=request.context,
                filter=customers_v1_customer_segment_sync_service_pb2.ListCustomerSegmentConflictsRequest.Filter(
                    created_after=response_0.workspace.audit.updated_at,
                    owner_id=response_0.result.correlation_id
                )
            )
            registered_1 = cast(
                customers_v1_customer_segment_sync_service_pb2_grpc.CustomerSegmentSyncServiceStub,
                deps.clients.registry['acme.customers.v1.CustomerSegmentSyncService']
            )
            response_1 = await registered_1.ListCustomerSegmentConflicts(outgoing_1, timeout=deps.settings.timeout)
            returned_0_0 = response_0.result.details
            response.result.details.update(returned_0_0)
            returned_0_1 = response_0.workspace.assignee.display_name
            if returned_0_1:
                response.notebook.counterparty.display_name = returned_0_1
            returned_1_0 = response_1.result.status
            if returned_1_0:
                response.outcome.status = returned_1_0
            returned_1_1 = response_1.result.details
            response.result.details.update(returned_1_1)
            echoed_0 = request.notebook_id
            response.notebook.notebook_id = echoed_0
            return response
