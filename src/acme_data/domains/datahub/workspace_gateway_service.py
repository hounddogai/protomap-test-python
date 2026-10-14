"""The edge API that apps call for workspaces."""

from __future__ import annotations

from collections.abc import AsyncIterator
from collections.abc import Awaitable
from collections.abc import Callable
from functools import partial
from typing import Any
import asyncio
import logging

from google.protobuf.any_pb2 import Any as AnyMessage
from google.protobuf.json_format import MessageToDict
from google.protobuf.json_format import MessageToJson
from google.protobuf.json_format import Parse
from google.protobuf.json_format import ParseDict
import grpc

from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.customers.v1 import consent_record_lifecycle_service_pb2 as customers_v1_consent_record_lifecycle_service_pb2
from acme.customers.v1 import refs_pb2 as customers_v1_refs_pb2
from acme.datahub.v1 import data_share_approval_service_pb2 as datahub_v1_data_share_approval_service_pb2
from acme.datahub.v1 import data_share_query_service_pb2 as datahub_v1_data_share_query_service_pb2
from acme.datahub.v1 import data_share_workflow_service_pb2 as datahub_v1_data_share_workflow_service_pb2
from acme.datahub.v1 import datahub_pb2 as datahub_v1_datahub_pb2
from acme.datahub.v1 import notebook_integration_service_pb2 as datahub_v1_notebook_integration_service_pb2
from acme.datahub.v1 import notebook_notification_service_pb2 as datahub_v1_notebook_notification_service_pb2
from acme.datahub.v1 import notebook_reporting_service_pb2 as datahub_v1_notebook_reporting_service_pb2
from acme.datahub.v1 import workspace_gateway_service_pb2 as datahub_v1_workspace_gateway_service_pb2
from acme.datahub.v1 import workspace_gateway_service_pb2_grpc as datahub_v1_workspace_gateway_service_pb2_grpc
from acme.datahub.v1 import workspace_integration_service_pb2 as datahub_v1_workspace_integration_service_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.lineage.v1 import impact_workflow_service_pb2 as lineage_v1_impact_workflow_service_pb2
from acme.lineage.v1 import lineage_pb2 as lineage_v1_lineage_pb2
from acme.metrics.v1 import dashboard_sync_service_pb2 as metrics_v1_dashboard_sync_service_pb2
from acme.metrics.v1 import metric_alert_history_service_pb2 as metrics_v1_metric_alert_history_service_pb2
from acme.metrics.v1 import metric_alert_notification_service_pb2 as metrics_v1_metric_alert_notification_service_pb2
from acme.metrics.v1 import metric_series_notification_service_pb2 as metrics_v1_metric_series_notification_service_pb2
from acme.modelregistry.v1 import (
    model_version_approval_service_pb2 as modelregistry_v1_model_version_approval_service_pb2,
)
from acme.modelregistry.v1 import (
    model_version_reporting_service_pb2 as modelregistry_v1_model_version_reporting_service_pb2,
)
from acme.modelregistry.v1 import modelregistry_pb2 as modelregistry_v1_modelregistry_pb2
from acme.patientapp.v1 import patient_home_query_service_pb2 as patientapp_v1_patient_home_query_service_pb2
from acme.recommendations.v1 import (
    recommendation_model_workflow_service_pb2 as recommendations_v1_recommendation_model_workflow_service_pb2,
)

from acme_data.domains.datahub.adapters import WorkspaceGatewayComposeWorkspacePage2Adapter
from acme_data.domains.datahub.adapters import WorkspaceGatewayComposeWorkspacePage2Port
from acme_data.domains.datahub.adapters import WorkspaceGatewayUploadWorkspaceAttachments0Adapter
from acme_data.domains.datahub.adapters import WorkspaceGatewayUploadWorkspaceAttachments0Port
from acme_data.domains.datahub.dependencies import Dependencies
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import run_steps
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_id
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class WorkspaceGatewayServicer(datahub_v1_workspace_gateway_service_pb2_grpc.WorkspaceGatewayServiceServicer):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    async def ComposeWorkspacePage(
        self, request: datahub_v1_workspace_gateway_service_pb2.ComposeWorkspacePageRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_workspace_gateway_service_pb2.ComposeWorkspacePageResponse:
        """Composes a workspace."""
        return await self.handle_compose_workspace_page(request)

    @rpc_errors
    async def FetchWorkspaceView(
        self, request: datahub_v1_workspace_gateway_service_pb2.FetchWorkspaceViewRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_workspace_gateway_service_pb2.FetchWorkspaceViewResponse:
        """Fetchs a workspace."""
        return await self.handle_fetch_workspace_view(request)

    @rpc_errors
    @retry_transient
    async def GetWorkspaceSummary(
        self, request: datahub_v1_workspace_gateway_service_pb2.GetWorkspaceSummaryRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_workspace_gateway_service_pb2.GetWorkspaceSummaryResponse:
        """Returns a workspace."""
        return await self.handle_get_workspace_summary(request)

    @rpc_errors
    @retry_transient
    async def SearchWorkspaceCatalog(
        self, request: datahub_v1_workspace_gateway_service_pb2.SearchWorkspaceCatalogRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_workspace_gateway_service_pb2.SearchWorkspaceCatalogResponse:
        """Lists workspaces a page at a time."""
        return await self.handle_search_workspace_catalog(request)

    @stream_errors
    async def StreamWorkspaceUpdates(
        self, request: datahub_v1_workspace_gateway_service_pb2.StreamWorkspaceUpdatesRequest, context: grpc.aio.ServicerContext,
    ) -> AsyncIterator[datahub_v1_workspace_gateway_service_pb2.StreamWorkspaceUpdatesResponse]:
        """Streams the changes of workspaces as they happen."""
        response = await self.handle_stream_workspace_updates(request)
        for item in messages((response,)):
            yield item

    @rpc_errors
    async def SubmitWorkspaceForm(
        self, request: datahub_v1_workspace_gateway_service_pb2.SubmitWorkspaceFormRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_workspace_gateway_service_pb2.SubmitWorkspaceFormResponse:
        """Submits a workspace."""
        return await self.handle_submit_workspace_form(request)

    @rpc_errors
    async def TrackWorkspace(
        self, request: datahub_v1_workspace_gateway_service_pb2.TrackWorkspaceRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_workspace_gateway_service_pb2.TrackWorkspaceResponse:
        """Tracks a workspace."""
        return await self.handle_track_workspace(request)

    @rpc_errors
    async def UploadWorkspaceAttachments(
        self, requests: AsyncIterator[
            datahub_v1_workspace_gateway_service_pb2.UploadWorkspaceAttachmentsRequest
        ], context: grpc.aio.ServicerContext,
    ) -> datahub_v1_workspace_gateway_service_pb2.UploadWorkspaceAttachmentsResponse:
        """Takes a stream of workspaces and answers once at the end."""
        response = datahub_v1_workspace_gateway_service_pb2.UploadWorkspaceAttachmentsResponse()
        async for request in requests:
            response.MergeFrom(await self.handle_upload_workspace_attachments(request))
        return response

    async def handle_compose_workspace_page(
        self,
        request: datahub_v1_workspace_gateway_service_pb2.ComposeWorkspacePageRequest
    ) -> datahub_v1_workspace_gateway_service_pb2.ComposeWorkspacePageResponse:
        """Composes a workspace."""
        deps = self.deps
        response = datahub_v1_workspace_gateway_service_pb2.ComposeWorkspacePageResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ComposeWorkspacePage', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'ComposeWorkspacePage', {'reason': request.reason})
            await deps.repository.save_workspace(request.context.tenant_id, request.workspace)
            response_0 = recommendations_v1_recommendation_model_workflow_service_pb2.ListRecommendationModelWorkflowsResponse()
            response_1 = datahub_v1_notebook_notification_service_pb2.SendNotebookTestNoticeResponse()
            response_2 = datahub_v1_notebook_integration_service_pb2.ConnectNotebookSourceResponse()
            requests_0: list[
                recommendations_v1_recommendation_model_workflow_service_pb2.ListRecommendationModelWorkflowsRequest
            ] = []
            for item_0 in request.workspace.comments:
                outgoing_0 = recommendations_v1_recommendation_model_workflow_service_pb2.ListRecommendationModelWorkflowsRequest(
                    context=request.context,
                    filter=recommendations_v1_recommendation_model_workflow_service_pb2.ListRecommendationModelWorkflowsRequest.Filter(
                        created_after=item_0.created_at,
                        labels=dict(request.workspace.custom_fields),
                        owner_id=item_0.comment_id
                    )
                )
                requests_0.append(outgoing_0)
            replies_0 = await asyncio.gather(*(
                deps.clients.recommendations_recommendation_model_workflow.ListRecommendationModelWorkflows(
                    entry,
                    timeout=deps.settings.timeout
                ) for entry in requests_0
            ))
            if replies_0:
                response_0 = replies_0[-1]
            outgoing_1 = datahub_v1_notebook_notification_service_pb2.SendNotebookTestNoticeRequest()
            outgoing_1.context.CopyFrom(request.context)
            outgoing_1.details.recipient.email = request.workspace.customer.email
            outgoing_1.details.recipient.preferred_channel = request.workspace.requester.preferred_channel
            outgoing_1.details.recipient.name.CopyFrom(request.workspace.requester.name)
            outgoing_1.context.tenant_id = tenant_id.get()
            response_1 = await deps.clients.datahub_notebook_notification.SendNotebookTestNotice(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = datahub_v1_notebook_integration_service_pb2.ConnectNotebookSourceRequest(
                context=request.context,
                details=datahub_v1_notebook_integration_service_pb2.ConnectNotebookSourceRequest.Details(
                    message_id=response_1.outcome.message
                ),
                notebook_id=response_1.notebook.notebook_id
            )
            port_2: WorkspaceGatewayComposeWorkspacePage2Port = WorkspaceGatewayComposeWorkspacePage2Adapter(
                deps.clients.datahub_notebook_integration,
                deps.settings.timeout
            )
            response_2 = await port_2.execute(outgoing_2)
            returned_1_0 = response_1.notebook.due_at
            if returned_1_0.ListFields():
                response.workspace.sla.due_at.MergeFrom(returned_1_0)
            returned_1_1 = response_1.notebook.counterparty.priority
            if returned_1_1:
                response.workspace.priority = returned_1_1
            returned_2_0 = response_2.notebook.counterparty.display_name
            if returned_2_0:
                response.workspace.assignee.display_name = returned_2_0
            returned_2_1 = response_2.outcome.status
            if returned_2_1:
                response.result.status = returned_2_1
            echoed_0 = request.workspace_id
            response.workspace.workspace_id = echoed_0
            echoed_1 = request.workspace.custom_fields
            response.workspace.custom_fields.update(echoed_1)
            return response

    async def handle_fetch_workspace_view(
        self,
        request: datahub_v1_workspace_gateway_service_pb2.FetchWorkspaceViewRequest
    ) -> datahub_v1_workspace_gateway_service_pb2.FetchWorkspaceViewResponse:
        """Fetchs a workspace."""
        deps = self.deps
        response = datahub_v1_workspace_gateway_service_pb2.FetchWorkspaceViewResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('FetchWorkspaceView', extra={'fields': {'device': request.details.device}})
            await deps.repository.audit(
                request.context.tenant_id,
                'FetchWorkspaceView',
                {'device': request.details.device}
            )
            await deps.repository.save_workspace(request.context.tenant_id, request.workspace)
            response_0 = datahub_v1_notebook_reporting_service_pb2.GenerateNotebookReportResponse()
            response_1 = metrics_v1_metric_alert_history_service_pb2.ListMetricAlertVersionsResponse()
            response_2 = datahub_v1_notebook_notification_service_pb2.StreamNotebookNoticesResponse()
            outgoing_0 = datahub_v1_notebook_reporting_service_pb2.GenerateNotebookReportRequest(
                annotations=dict(request.annotations),
                context=request.context,
                reason=request.reason
            )
            steps_0 = [
                partial(
                    deps.clients.datahub_notebook_reporting.GenerateNotebookReport,
                    outgoing_0,
                    timeout=deps.settings.timeout
                )
            ]
            results_0 = await run_steps(steps_0)
            response_0 = results_0[-1]
            callbacks_1: list[
                Callable[[], Awaitable[metrics_v1_metric_alert_history_service_pb2.ListMetricAlertVersionsResponse]]
            ] = []
            for item_1 in request.workspace.comments:
                outgoing_1 = metrics_v1_metric_alert_history_service_pb2.ListMetricAlertVersionsRequest(
                    context=request.context,
                    filter=metrics_v1_metric_alert_history_service_pb2.ListMetricAlertVersionsRequest.Filter(
                        created_after=item_1.created_at,
                        owner_id=item_1.comment_id
                    )
                )
                async def send_1(
                    payload: metrics_v1_metric_alert_history_service_pb2.ListMetricAlertVersionsRequest = outgoing_1
                ) -> metrics_v1_metric_alert_history_service_pb2.ListMetricAlertVersionsResponse:
                    return await deps.clients.metrics_metric_alert_history.ListMetricAlertVersions(
                        payload,
                        timeout=deps.settings.timeout
                    )
                callbacks_1.append(send_1)
            for callback_1 in callbacks_1:
                response_1 = await callback_1()
            outgoing_2 = datahub_v1_notebook_notification_service_pb2.StreamNotebookNoticesRequest(
                context=request.context,
                subscriber=common_v1_contact_pb2.ContactInfo(
                    name=request.workspace.requester.name,
                    preferred_channel=request.workspace.requester.preferred_channel
                )
            )
            async for chunk_2 in deps.clients.datahub_notebook_notification.StreamNotebookNotices(
                outgoing_2,
                timeout=deps.settings.timeout
            ):
                response_2 = chunk_2
            returned_0_0 = response_0.result.correlation_id
            if returned_0_0:
                response.result.correlation_id = returned_0_0
            returned_0_1 = response_0.result.message
            if returned_0_1:
                response.result.message = returned_0_1
            echoed_0 = request.workspace_id
            response.workspace.workspace_id = echoed_0
            echoed_1 = request.workspace.subject
            response.workspace.subject = echoed_1
            return response

    async def handle_get_workspace_summary(
        self,
        request: datahub_v1_workspace_gateway_service_pb2.GetWorkspaceSummaryRequest
    ) -> datahub_v1_workspace_gateway_service_pb2.GetWorkspaceSummaryResponse:
        """Returns a workspace."""
        deps = self.deps
        response = datahub_v1_workspace_gateway_service_pb2.GetWorkspaceSummaryResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('GetWorkspaceSummary', extra={'fields': {'locale': request.context.locale}})
            await deps.repository.audit(
                request.context.tenant_id,
                'GetWorkspaceSummary',
                {'locale': request.context.locale}
            )
            echoed_0 = request.workspace_id
            response.workspace.workspace_id = echoed_0
            return response

    async def handle_search_workspace_catalog(
        self,
        request: datahub_v1_workspace_gateway_service_pb2.SearchWorkspaceCatalogRequest
    ) -> datahub_v1_workspace_gateway_service_pb2.SearchWorkspaceCatalogResponse:
        """Lists workspaces a page at a time."""
        deps = self.deps
        response = datahub_v1_workspace_gateway_service_pb2.SearchWorkspaceCatalogResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SearchWorkspaceCatalog', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'SearchWorkspaceCatalog',
                {'order_by': request.order_by}
            )
            response_0 = datahub_v1_data_share_query_service_pb2.ResolveDataSharesResponse()
            response_1 = datahub_v1_workspace_integration_service_pb2.ConnectWorkspaceSourceResponse()
            outgoing_0 = datahub_v1_data_share_query_service_pb2.ResolveDataSharesRequest(context=request.context)
            response_0 = await deps.clients.datahub_data_share_query.ResolveDataShares(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = datahub_v1_workspace_integration_service_pb2.ConnectWorkspaceSourceRequest(
                annotations=dict(request.filter.labels),
                context=request.context,
                details=datahub_v1_workspace_integration_service_pb2.ConnectWorkspaceSourceRequest.Details(
                    message_id=response_0.result.message,
                    received_at=request.filter.created_after
                )
            )
            method_name_1 = 'ConnectWorkspaceSource'
            response_1 = await getattr(
                deps.clients.datahub_workspace_integration,
                method_name_1
            )(outgoing_1, timeout=deps.settings.timeout)
            returned_0_0 = response_0.page_info.total_size
            if returned_0_0:
                response.page_info.total_size = returned_0_0
            returned_1_0 = response_1.workspace.requester.phone
            returned_1_0_part_0 = response.workspaces.add()
            if returned_1_0:
                returned_1_0_part_0.requester.phone = returned_1_0
            returned_1_1 = response_1.workspace.requester.email
            returned_1_1_part_0 = response.workspaces.add()
            if returned_1_1:
                returned_1_1_part_0.assignee.email = returned_1_1
            return response

    async def handle_stream_workspace_updates(
        self,
        request: datahub_v1_workspace_gateway_service_pb2.StreamWorkspaceUpdatesRequest
    ) -> datahub_v1_workspace_gateway_service_pb2.StreamWorkspaceUpdatesResponse:
        """Streams the changes of workspaces as they happen."""
        deps = self.deps
        response = datahub_v1_workspace_gateway_service_pb2.StreamWorkspaceUpdatesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('StreamWorkspaceUpdates', extra={'fields': {'max_events': request.max_events}})
            await deps.repository.audit(
                request.context.tenant_id,
                'StreamWorkspaceUpdates',
                {'max_events': request.max_events}
            )
            response_0 = patientapp_v1_patient_home_query_service_pb2.CountPatientHomesResponse()
            response_1 = modelregistry_v1_model_version_approval_service_pb2.RecallModelVersionResponse()
            response_2 = lineage_v1_impact_workflow_service_pb2.SignalImpactWorkflowResponse()
            fields_0: dict[str, Any] = {
                'context': request.context,
                'filter': {
                    'created_after': request.filter.created_after,
                    'labels': dict(request.filter.labels),
                    'query': request.filter.query,
                    'region': request.filter.region
                }
            }
            outgoing_0 = patientapp_v1_patient_home_query_service_pb2.CountPatientHomesRequest(**fields_0)
            response_0 = await deps.clients.patientapp_patient_home_query.CountPatientHomes(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = modelregistry_v1_model_version_approval_service_pb2.RecallModelVersionRequest(
                context=request.context,
                details=modelregistry_v1_model_version_approval_service_pb2.RecallModelVersionRequest.Details(
                    approver=identity_v1_refs_pb2.UserRef(email=request.subscriber.email)
                ),
                model_version=modelregistry_v1_modelregistry_pb2.ModelVersion(
                    correlation_id=response_0.result.correlation_id
                )
            )
            document_1 = MessageToDict(outgoing_1, preserving_proto_field_name=True)
            outgoing_1 = ParseDict(
                document_1,
                modelregistry_v1_model_version_approval_service_pb2.RecallModelVersionRequest()
            )
            response_1 = await deps.clients.modelregistry_model_version_approval.RecallModelVersion(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = lineage_v1_impact_workflow_service_pb2.SignalImpactWorkflowRequest(
                context=request.context,
                details=lineage_v1_impact_workflow_service_pb2.SignalImpactWorkflowRequest.Details(
                    notify=common_v1_contact_pb2.ContactInfo(
                        email=response_1.model_version.subject.email,
                        preferred_channel=request.subscriber.preferred_channel
                    )
                ),
                impact=lineage_v1_lineage_pb2.Impact(
                    assignee=identity_v1_refs_pb2.UserRef(display_name=response_1.model_version.subject.display_name),
                    customer=customers_v1_refs_pb2.CustomerRef(customer_id=response_1.model_version.subject.customer_id)
                )
            )
            document_2 = MessageToJson(outgoing_2, preserving_proto_field_name=True)
            outgoing_2 = Parse(document_2, lineage_v1_impact_workflow_service_pb2.SignalImpactWorkflowRequest())
            response_2 = await deps.clients.lineage_impact_workflow.SignalImpactWorkflow(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.details
            response.result.details.update(returned_0_0)
            returned_1_0 = response_1.outcome.message
            if returned_1_0:
                response.result.message = returned_1_0
            returned_2_0 = response_2.result.details
            response.result.details.update(returned_2_0)
            returned_2_1 = response_2.impact.subject
            if returned_2_1:
                response.workspace.subject = returned_2_1
            echoed_0 = request.subscriber.email
            response.workspace.requester.email = echoed_0
            echoed_1 = request.subscriber.phone
            response.workspace.requester.phone = echoed_1
            return response

    async def handle_submit_workspace_form(
        self,
        request: datahub_v1_workspace_gateway_service_pb2.SubmitWorkspaceFormRequest
    ) -> datahub_v1_workspace_gateway_service_pb2.SubmitWorkspaceFormResponse:
        """Submits a workspace."""
        deps = self.deps
        response = datahub_v1_workspace_gateway_service_pb2.SubmitWorkspaceFormResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SubmitWorkspaceForm', extra={'fields': {'device': request.details.device}})
            await deps.repository.audit(
                request.context.tenant_id,
                'SubmitWorkspaceForm',
                {'device': request.details.device}
            )
            await deps.repository.save_workspace(request.context.tenant_id, request.workspace)
            response_0 = customers_v1_consent_record_lifecycle_service_pb2.ScheduleConsentRecordExpiryResponse()
            response_1 = datahub_v1_notebook_reporting_service_pb2.ScheduleNotebookReportResponse()
            response_2 = datahub_v1_data_share_approval_service_pb2.RejectDataShareResponse()
            response_3 = metrics_v1_dashboard_sync_service_pb2.PullDashboardsResponse()
            outgoing_0 = customers_v1_consent_record_lifecycle_service_pb2.ScheduleConsentRecordExpiryRequest()
            outgoing_0.context.CopyFrom(request.context)
            outgoing_0.details.notify.phone = request.workspace.requester.phone
            if request.workspace.WhichOneof('origin') == 'customer':
                outgoing_0.details.notify.email = request.workspace.customer.email
            response_0 = await deps.clients.customers_consent_record_lifecycle.ScheduleConsentRecordExpiry(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = datahub_v1_notebook_reporting_service_pb2.ScheduleNotebookReportRequest(
                annotations=dict(request.annotations),
                context=request.context,
                details=datahub_v1_notebook_reporting_service_pb2.ScheduleNotebookReportRequest.Details(
                    filters=dict(response_0.consent_record.attributes)
                ),
                reason=request.reason
            )
            envelope_1 = AnyMessage()
            envelope_1.Pack(outgoing_1)
            outgoing_1 = datahub_v1_notebook_reporting_service_pb2.ScheduleNotebookReportRequest()
            if not envelope_1.Unpack(outgoing_1):
                raise ValueError("partner envelope contains the wrong request type")
            response_1 = await deps.clients.datahub_notebook_reporting.ScheduleNotebookReport(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            async for item_2 in async_messages(request.workspace.comments):
                outgoing_2 = datahub_v1_data_share_approval_service_pb2.RejectDataShareRequest(
                    context=request.context,
                    data_share=datahub_v1_datahub_pb2.DataShare(
                        audit=common_v1_audit_pb2.AuditInfo(created_at=item_2.created_at)
                    ),
                    details=datahub_v1_data_share_approval_service_pb2.RejectDataShareRequest.Details(
                        approver=identity_v1_refs_pb2.UserRef(
                            display_name=request.workspace.customer.display_name,
                            email=item_2.author_email
                        ),
                        comment=item_2.comment_id
                    )
                )
                response_2 = await deps.clients.datahub_data_share_approval.RejectDataShare(
                    outgoing_2,
                    timeout=deps.settings.timeout
                )
            outgoing_3 = metrics_v1_dashboard_sync_service_pb2.PullDashboardsRequest()
            outgoing_3.context.CopyFrom(request.context)
            if response_2.data_share.WhichOneof('settlement') == 'bank':
                outgoing_3.dashboard.bank.bic = response_2.data_share.bank.bic
            outgoing_3.dashboard.audit.updated_by = request.workspace.audit.updated_by
            outgoing_3.dashboard.billing_address.recipient = response_2.data_share.billing_address.recipient
            response_3 = await deps.clients.metrics_dashboard_sync.PullDashboards(
                outgoing_3,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.outcome.message
            if returned_0_0:
                response.result.message = returned_0_0
            returned_1_0 = response_1.result.status
            if returned_1_0:
                response.result.status = returned_1_0
            returned_1_1 = response_1.result.reference_ids
            response.result.reference_ids.extend(returned_1_1)
            returned_3_0 = response_3.outcome.message
            if returned_3_0:
                response.result.message = returned_3_0
            returned_3_1 = response_3.result.reference_ids
            response.result.reference_ids.extend(returned_3_1)
            echoed_0 = request.workspace_id
            response.workspace.workspace_id = echoed_0
            echoed_1 = request.workspace.subject
            response.workspace.subject = echoed_1
            return response

    async def handle_track_workspace(
        self,
        request: datahub_v1_workspace_gateway_service_pb2.TrackWorkspaceRequest
    ) -> datahub_v1_workspace_gateway_service_pb2.TrackWorkspaceResponse:
        """Tracks a workspace."""
        deps = self.deps
        response = datahub_v1_workspace_gateway_service_pb2.TrackWorkspaceResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('TrackWorkspace', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'TrackWorkspace', {'reason': request.reason})
            await deps.repository.save_workspace(request.context.tenant_id, request.workspace)
            response_0 = metrics_v1_metric_alert_notification_service_pb2.SubscribeMetricAlertUpdatesResponse()
            response_1 = metrics_v1_metric_series_notification_service_pb2.NotifyMetricSeriesWatchersResponse()
            response_2 = modelregistry_v1_model_version_reporting_service_pb2.StreamModelVersionMetricsResponse()
            response_3 = datahub_v1_workspace_integration_service_pb2.TestWorkspaceConnectionResponse()
            for item_0 in request.workspace.comments:
                outgoing_0 = metrics_v1_metric_alert_notification_service_pb2.SubscribeMetricAlertUpdatesRequest(
                    context=request.context,
                    details=metrics_v1_metric_alert_notification_service_pb2.SubscribeMetricAlertUpdatesRequest.Details(
                        recipient=common_v1_contact_pb2.ContactInfo(
                            email=item_0.author_email,
                            preferred_channel=request.workspace.requester.preferred_channel
                        )
                    )
                )
                response_0 = await deps.clients.metrics_metric_alert_notification.SubscribeMetricAlertUpdates(
                    outgoing_0,
                    timeout=deps.settings.timeout
                )
            requests_1: list[metrics_v1_metric_series_notification_service_pb2.NotifyMetricSeriesWatchersRequest] = []
            for item_1 in request.workspace.comments:
                outgoing_1 = metrics_v1_metric_series_notification_service_pb2.NotifyMetricSeriesWatchersRequest(
                    context=request.context,
                    details=metrics_v1_metric_series_notification_service_pb2.NotifyMetricSeriesWatchersRequest.Details(
                        recipient=common_v1_contact_pb2.ContactInfo(email=item_1.author_email)
                    )
                )
                requests_1.append(outgoing_1)
            replies_1 = await asyncio.gather(*(
                deps.clients.metrics_metric_series_notification.NotifyMetricSeriesWatchers(
                    entry,
                    timeout=deps.settings.timeout
                ) for entry in requests_1
            ))
            if replies_1:
                response_1 = replies_1[-1]
            outgoing_2 = modelregistry_v1_model_version_reporting_service_pb2.StreamModelVersionMetricsRequest(
                context=request.context,
                filter=modelregistry_v1_model_version_reporting_service_pb2.StreamModelVersionMetricsRequest.Filter(
                    region=response_1.metric_series.address.region
                ),
                subscriber=common_v1_contact_pb2.ContactInfo(
                    email=request.workspace.requester.email,
                    preferred_channel=request.workspace.requester.preferred_channel
                )
            )
            async for chunk_2 in deps.clients.modelregistry_model_version_reporting.StreamModelVersionMetrics(
                outgoing_2,
                timeout=deps.settings.timeout
            ):
                response_2 = chunk_2
            callbacks_3: list[
                Callable[[], Awaitable[datahub_v1_workspace_integration_service_pb2.TestWorkspaceConnectionResponse]]
            ] = []
            for item_3 in request.workspace.history:
                outgoing_3 = datahub_v1_workspace_integration_service_pb2.TestWorkspaceConnectionRequest(
                    annotations=dict(request.annotations),
                    context=request.context,
                    details=datahub_v1_workspace_integration_service_pb2.TestWorkspaceConnectionRequest.Details(
                        received_at=item_3.changed_at
                    ),
                    reason=response_0.metric_alert.block.reason,
                    workspace_id=request.workspace.workspace_id
                )
                async def send_3(
                    payload: datahub_v1_workspace_integration_service_pb2.TestWorkspaceConnectionRequest = outgoing_3
                ) -> datahub_v1_workspace_integration_service_pb2.TestWorkspaceConnectionResponse:
                    return await deps.clients.datahub_workspace_integration.TestWorkspaceConnection(
                        payload,
                        timeout=deps.settings.timeout
                    )
                callbacks_3.append(send_3)
            for callback_3 in callbacks_3:
                response_3 = await callback_3()
            echoed_0 = request.workspace_id
            response.workspace.workspace_id = echoed_0
            echoed_1 = request.workspace.requester
            response.workspace.requester.CopyFrom(echoed_1)
            return response

    async def handle_upload_workspace_attachments(
        self,
        request: datahub_v1_workspace_gateway_service_pb2.UploadWorkspaceAttachmentsRequest
    ) -> datahub_v1_workspace_gateway_service_pb2.UploadWorkspaceAttachmentsResponse:
        """Takes a stream of workspaces and answers once at the end."""
        deps = self.deps
        response = datahub_v1_workspace_gateway_service_pb2.UploadWorkspaceAttachmentsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('UploadWorkspaceAttachments', extra={'fields': {'sequence': request.sequence}})
            await deps.repository.audit(
                request.context.tenant_id,
                'UploadWorkspaceAttachments',
                {'sequence': request.sequence}
            )
            if request.WhichOneof('chunk') == 'record':
                await deps.repository.save_workspace(request.context.tenant_id, request.record)
            response_0 = datahub_v1_data_share_workflow_service_pb2.CancelDataShareWorkflowResponse()
            response_1 = datahub_v1_data_share_workflow_service_pb2.StartDataShareWorkflowResponse()
            outgoing_0 = datahub_v1_data_share_workflow_service_pb2.CancelDataShareWorkflowRequest(
                context=request.context,
                details=datahub_v1_data_share_workflow_service_pb2.CancelDataShareWorkflowRequest.Details(
                    notify=common_v1_contact_pb2.ContactInfo(name=request.record.requester.name)
                )
            )
            port_0: WorkspaceGatewayUploadWorkspaceAttachments0Port = WorkspaceGatewayUploadWorkspaceAttachments0Adapter(
                deps.clients.datahub_data_share_workflow,
                deps.settings.timeout
            )
            response_0 = await port_0.execute(outgoing_0)
            outgoing_1 = datahub_v1_data_share_workflow_service_pb2.StartDataShareWorkflowRequest()
            outgoing_1.context.CopyFrom(request.context)
            if response_0.data_share.WhichOneof('settlement') == 'bank':
                outgoing_1.data_share.bank.iban = response_0.data_share.bank.iban
            outgoing_1.data_share.audit.updated_by = response_0.data_share.audit.updated_by
            response_1 = await deps.clients.datahub_data_share_workflow.StartDataShareWorkflow(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.status
            if returned_0_0:
                response.result.status = returned_0_0
            returned_1_0 = response_1.result.message
            if returned_1_0:
                response.result.message = returned_1_0
            returned_1_1 = response_1.result.correlation_id
            if returned_1_1:
                response.result.correlation_id = returned_1_1
            return response
