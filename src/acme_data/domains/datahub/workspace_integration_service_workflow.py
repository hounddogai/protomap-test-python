"""Application workflow for Workspace Integration."""

from __future__ import annotations

from functools import partial
from typing import cast
import asyncio
import logging

from google.protobuf.any_pb2 import Any as AnyMessage
from google.protobuf.json_format import MessageToJson
from google.protobuf.json_format import Parse

from acme.analytics.v1 import analytics_pb2 as analytics_v1_analytics_pb2
from acme.analytics.v1 import (
    analytics_report_lifecycle_service_pb2 as analytics_v1_analytics_report_lifecycle_service_pb2,
)
from acme.anomalies.v1 import anomalies_pb2 as anomalies_v1_anomalies_pb2
from acme.anomalies.v1 import anomaly_approval_service_pb2 as anomalies_v1_anomaly_approval_service_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.customers.v1 import customers_pb2 as customers_v1_customers_pb2
from acme.customers.v1 import household_workflow_service_pb2 as customers_v1_household_workflow_service_pb2
from acme.customers.v1 import preference_sync_service_pb2 as customers_v1_preference_sync_service_pb2
from acme.datahub.v1 import data_share_approval_service_pb2 as datahub_v1_data_share_approval_service_pb2
from acme.datahub.v1 import datahub_pb2 as datahub_v1_datahub_pb2
from acme.datahub.v1 import notebook_approval_service_pb2 as datahub_v1_notebook_approval_service_pb2
from acme.datahub.v1 import notebook_approval_service_pb2_grpc as datahub_v1_notebook_approval_service_pb2_grpc
from acme.datahub.v1 import notebook_reporting_service_pb2 as datahub_v1_notebook_reporting_service_pb2
from acme.datahub.v1 import notebook_workflow_service_pb2 as datahub_v1_notebook_workflow_service_pb2
from acme.datahub.v1 import refs_pb2 as datahub_v1_refs_pb2
from acme.datahub.v1 import workspace_integration_service_pb2 as datahub_v1_workspace_integration_service_pb2
from acme.datahub.v1 import workspace_reporting_service_pb2 as datahub_v1_workspace_reporting_service_pb2
from acme.datahub.v1 import workspace_workflow_service_pb2 as datahub_v1_workspace_workflow_service_pb2
from acme.edgegateway.v1 import route_binding_service_pb2 as edgegateway_v1_route_binding_service_pb2
from acme.featureflags.v1 import feature_flag_service_pb2 as featureflags_v1_feature_flag_service_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.metrics.v1 import metric_series_admin_service_pb2 as metrics_v1_metric_series_admin_service_pb2
from acme.modelregistry.v1 import (
    registered_model_reporting_service_pb2 as modelregistry_v1_registered_model_reporting_service_pb2,
)
from acme.recommendations.v1 import (
    recommendation_model_workflow_service_pb2 as recommendations_v1_recommendation_model_workflow_service_pb2,
)

from acme_data.domains.datahub import hooks
from acme_data.domains.datahub.adapters import WorkspaceIntegrationAcknowledgeWorkspaceEvent0Adapter
from acme_data.domains.datahub.adapters import WorkspaceIntegrationTestWorkspaceConnection0Adapter
from acme_data.domains.datahub.adapters import WorkspaceIntegrationTestWorkspaceConnection0Port
from acme_data.domains.datahub.adapters import WorkspaceIntegrationTestWorkspaceConnection2Adapter
from acme_data.domains.datahub.dependencies import Dependencies
from acme_data.domains.datahub.models import WorkspaceIntegrationRelayWorkspaceMessages0Command
from acme_data.domains.datahub.models import to_workspace_integration_relay_workspace_messages0_command
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import run_steps
from acme_data.platform.tenancy import tenant_id
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class WorkspaceIntegrationServicerWorkflow:
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    async def handle_acknowledge_workspace_event(
        self,
        request: datahub_v1_workspace_integration_service_pb2.AcknowledgeWorkspaceEventRequest
    ) -> datahub_v1_workspace_integration_service_pb2.AcknowledgeWorkspaceEventResponse:
        """Acknowledges a workspace."""
        deps = self.deps
        response = datahub_v1_workspace_integration_service_pb2.AcknowledgeWorkspaceEventResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('AcknowledgeWorkspaceEvent', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'AcknowledgeWorkspaceEvent',
                {'reason': request.reason}
            )
            response_0 = datahub_v1_workspace_reporting_service_pb2.FetchWorkspaceReportResponse()
            response_1 = anomalies_v1_anomaly_approval_service_pb2.RejectAnomalyResponse()
            response_2 = datahub_v1_notebook_approval_service_pb2.CommentNotebookApprovalResponse()
            outgoing_0 = datahub_v1_workspace_reporting_service_pb2.FetchWorkspaceReportRequest(
                context=request.context,
                workspace_id=request.workspace_id
            )
            response_0 = await WorkspaceIntegrationAcknowledgeWorkspaceEvent0Adapter(
                deps.clients.datahub_workspace_reporting,
                deps.settings.timeout
            )(outgoing_0)
            outgoing_1 = anomalies_v1_anomaly_approval_service_pb2.RejectAnomalyRequest(
                anomaly=anomalies_v1_anomalies_pb2.Anomaly(
                    audit=common_v1_audit_pb2.AuditInfo(etag=response_0.workspace.audit.etag),
                    requester=common_v1_contact_pb2.ContactInfo(email=response_0.workspace.requester.email)
                ),
                context=request.context,
                details=anomalies_v1_anomaly_approval_service_pb2.RejectAnomalyRequest.Details(
                    approver=identity_v1_refs_pb2.UserRef(display_name=response_0.workspace.customer.display_name)
                )
            )
            response_1 = cast(anomalies_v1_anomaly_approval_service_pb2.RejectAnomalyResponse, await deps.bus.request(
                'acme.datahub.v1.WorkspaceIntegrationService/AcknowledgeWorkspaceEvent/1', outgoing_1, deps.settings.timeout,
            ))
            outgoing_2 = datahub_v1_notebook_approval_service_pb2.CommentNotebookApprovalRequest(
                context=request.context,
                details=datahub_v1_notebook_approval_service_pb2.CommentNotebookApprovalRequest.Details(
                    approver=identity_v1_refs_pb2.UserRef(
                        email=response_1.anomaly.requester.email,
                        user_id=response_1.anomaly.assignee.user_id
                    )
                ),
                notebook=datahub_v1_datahub_pb2.Notebook(
                    audit=common_v1_audit_pb2.AuditInfo(
                        etag=response_1.anomaly.audit.etag,
                        updated_by=response_1.anomaly.audit.updated_by
                    )
                )
            )
            response_2 = await deps.clients.datahub_notebook_approval.CommentNotebookApproval(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.workspace.sla.breached
            if returned_0_0:
                response.workspace.sla.breached = returned_0_0
            returned_1_0 = response_1.anomaly.audit.created_at
            returned_1_0_part_1 = response.workspace.comments.add()
            if returned_1_0.ListFields():
                returned_1_0_part_1.created_at.MergeFrom(returned_1_0)
            returned_1_1 = response_1.anomaly.requester.email
            if returned_1_1:
                response.workspace.requester.email = returned_1_1
            returned_2_0 = response_2.notebook.audit.etag
            if returned_2_0:
                response.workspace.audit.etag = returned_2_0
            returned_2_1 = response_2.result.message
            if returned_2_1:
                response.outcome.message = returned_2_1
            echoed_0 = request.workspace_id
            response.workspace.workspace_id = echoed_0
            return response

    async def handle_connect_workspace_source(
        self,
        request: datahub_v1_workspace_integration_service_pb2.ConnectWorkspaceSourceRequest
    ) -> datahub_v1_workspace_integration_service_pb2.ConnectWorkspaceSourceResponse:
        """Connects a workspace."""
        deps = self.deps
        response = datahub_v1_workspace_integration_service_pb2.ConnectWorkspaceSourceResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ConnectWorkspaceSource', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'ConnectWorkspaceSource', {'reason': request.reason})
            response_0 = featureflags_v1_feature_flag_service_pb2.BatchGetFeatureFlagsResponse()
            response_1 = customers_v1_household_workflow_service_pb2.StartHouseholdWorkflowResponse()
            response_2 = datahub_v1_workspace_reporting_service_pb2.StreamWorkspaceMetricsResponse()
            response_3 = edgegateway_v1_route_binding_service_pb2.SearchRouteBindingsResponse()
            outgoing_0 = featureflags_v1_feature_flag_service_pb2.BatchGetFeatureFlagsRequest(context=request.context)
            outgoing_1 = customers_v1_household_workflow_service_pb2.StartHouseholdWorkflowRequest(
                context=request.context,
                details=customers_v1_household_workflow_service_pb2.StartHouseholdWorkflowRequest.Details(
                    notify=common_v1_contact_pb2.ContactInfo(email=request.context.actor.email)
                ),
                household=customers_v1_customers_pb2.Household(
                    children=[
                        customers_v1_customers_pb2.Household(
                            manager=identity_v1_refs_pb2.UserRef(user_id=request.context.actor.user_id)
                        )
                    ]
                )
            )
            response_0, response_1 = await asyncio.gather(
                deps.clients.featureflags_feature_flag.BatchGetFeatureFlags(outgoing_0, timeout=deps.settings.timeout),
                deps.clients.customers_household_workflow.StartHouseholdWorkflow(
                    outgoing_1,
                    timeout=deps.settings.timeout
                ),
            )
            outgoing_2 = datahub_v1_workspace_reporting_service_pb2.StreamWorkspaceMetricsRequest(
                context=request.context,
                subscriber=common_v1_contact_pb2.ContactInfo(email=response_1.household.manager.email)
            )
            async for chunk_2 in deps.clients.datahub_workspace_reporting.StreamWorkspaceMetrics(
                outgoing_2,
                timeout=deps.settings.timeout
            ):
                response_2 = chunk_2
            outgoing_3 = edgegateway_v1_route_binding_service_pb2.SearchRouteBindingsRequest(
                context=request.context,
                filter=edgegateway_v1_route_binding_service_pb2.SearchRouteBindingsRequest.Filter(
                    region=response_1.household.location.region
                )
            )
            document_3 = MessageToJson(outgoing_3, preserving_proto_field_name=True)
            outgoing_3 = Parse(document_3, edgegateway_v1_route_binding_service_pb2.SearchRouteBindingsRequest())
            response_3 = await deps.clients.edgegateway_route_binding.SearchRouteBindings(
                outgoing_3,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.details
            response.result.details.update(returned_0_0)
            returned_0_1 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_1)
            returned_1_0 = response_1.result.correlation_id
            if returned_1_0:
                response.result.correlation_id = returned_1_0
            returned_3_0 = response_3.result.correlation_id
            if returned_3_0:
                response.result.correlation_id = returned_3_0
            returned_3_1 = response_3.result.status
            if returned_3_1:
                response.result.status = returned_3_1
            echoed_0 = request.workspace_id
            response.workspace.workspace_id = echoed_0
            return response

    async def handle_disconnect_workspace_source(
        self,
        request: datahub_v1_workspace_integration_service_pb2.DisconnectWorkspaceSourceRequest
    ) -> datahub_v1_workspace_integration_service_pb2.DisconnectWorkspaceSourceResponse:
        """Disconnects a workspace."""
        deps = self.deps
        response = datahub_v1_workspace_integration_service_pb2.DisconnectWorkspaceSourceResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('DisconnectWorkspaceSource', extra={'fields': {'endpoint': request.details.endpoint}})
            await deps.repository.audit(
                request.context.tenant_id,
                'DisconnectWorkspaceSource',
                {'endpoint': request.details.endpoint}
            )
            response_0 = datahub_v1_notebook_reporting_service_pb2.GenerateNotebookReportResponse()
            response_1 = datahub_v1_notebook_reporting_service_pb2.CountNotebookTotalsResponse()
            response_2 = datahub_v1_notebook_approval_service_pb2.RejectNotebookResponse()
            outgoing_0 = datahub_v1_notebook_reporting_service_pb2.GenerateNotebookReportRequest()
            outgoing_0.context.CopyFrom(request.context)
            outgoing_0.reason = request.reason
            merged_0 = datahub_v1_notebook_reporting_service_pb2.GenerateNotebookReportRequest()
            merged_0.MergeFrom(outgoing_0)
            outgoing_0.CopyFrom(merged_0)
            response_0 = await deps.clients.datahub_notebook_reporting.GenerateNotebookReport(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = datahub_v1_notebook_reporting_service_pb2.CountNotebookTotalsRequest(
                context=request.context,
                filter=datahub_v1_notebook_reporting_service_pb2.CountNotebookTotalsRequest.Filter(
                    created_after=request.details.received_at,
                    owner_id=request.workspace_id
                )
            )
            envelope_1 = AnyMessage()
            envelope_1.Pack(outgoing_1)
            outgoing_1 = datahub_v1_notebook_reporting_service_pb2.CountNotebookTotalsRequest()
            if not envelope_1.Unpack(outgoing_1):
                raise ValueError("partner envelope contains the wrong request type")
            response_1 = await deps.clients.datahub_notebook_reporting.CountNotebookTotals(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = datahub_v1_notebook_approval_service_pb2.RejectNotebookRequest(
                annotations=dict(request.annotations),
                context=request.context,
                details=datahub_v1_notebook_approval_service_pb2.RejectNotebookRequest.Details(
                    approver=identity_v1_refs_pb2.UserRef(user_id=request.context.actor.user_id)
                ),
                notebook=datahub_v1_datahub_pb2.Notebook(
                    counterparty=datahub_v1_refs_pb2.WorkspaceRef(workspace_id=request.workspace_id)
                ),
                reason=request.reason
            )
            registered_2 = cast(
                datahub_v1_notebook_approval_service_pb2_grpc.NotebookApprovalServiceStub,
                deps.clients.registry['acme.datahub.v1.NotebookApprovalService']
            )
            response_2 = await registered_2.RejectNotebook(outgoing_2, timeout=deps.settings.timeout)
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.outcome.message = returned_0_0
            returned_1_0 = response_1.result.status
            if returned_1_0:
                response.outcome.status = returned_1_0
            returned_1_1 = response_1.result.details
            response.result.details.update(returned_1_1)
            returned_2_0 = response_2.notebook.counterparty.display_name
            if returned_2_0:
                response.workspace.assignee.display_name = returned_2_0
            echoed_0 = request.workspace_id
            response.workspace.workspace_id = echoed_0
            return response

    async def handle_relay_workspace_messages(
        self,
        request: datahub_v1_workspace_integration_service_pb2.RelayWorkspaceMessagesRequest
    ) -> datahub_v1_workspace_integration_service_pb2.RelayWorkspaceMessagesResponse:
        """Exchanges changes of workspaces with a peer."""
        deps = self.deps
        response = datahub_v1_workspace_integration_service_pb2.RelayWorkspaceMessagesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('RelayWorkspaceMessages', extra={'fields': {'cursor': request.cursor}})
            await deps.repository.audit(request.context.tenant_id, 'RelayWorkspaceMessages', {'cursor': request.cursor})
            if request.WhichOneof('frame') == 'change':
                await deps.repository.save_workspace(request.context.tenant_id, request.change)
            response_0 = datahub_v1_notebook_workflow_service_pb2.StartNotebookWorkflowResponse()
            response_1 = customers_v1_preference_sync_service_pb2.PullPreferencesResponse()
            response_2 = analytics_v1_analytics_report_lifecycle_service_pb2.ScheduleAnalyticsReportExpiryResponse()
            command_0 = WorkspaceIntegrationRelayWorkspaceMessages0Command(
                context=request.context,
                notebook_audit_etag=request.change.audit.etag,
                notebook_audit_created_by=request.change.audit.created_by,
                details_notify_name=request.change.requester.name
            )
            outgoing_0 = to_workspace_integration_relay_workspace_messages0_command(command_0)
            response_0 = await deps.clients.datahub_notebook_workflow.StartNotebookWorkflow(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = customers_v1_preference_sync_service_pb2.PullPreferencesRequest()
            outgoing_1.context.CopyFrom(request.context)
            outgoing_1.preference.audit.created_at.CopyFrom(response_0.notebook.audit.created_at)
            if request.WhichOneof('frame') == 'change':
                outgoing_1.preference.audit.etag = request.change.audit.etag
            outgoing_1.preference.audit.updated_at.CopyFrom(response_0.notebook.audit.updated_at)
            response_1 = await deps.clients.customers_preference_sync.PullPreferences(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = analytics_v1_analytics_report_lifecycle_service_pb2.ScheduleAnalyticsReportExpiryRequest(
                analytics_report=analytics_v1_analytics_pb2.AnalyticsReport(
                    audit=common_v1_audit_pb2.AuditInfo(created_by=response_1.preference.audit.created_by)
                ),
                context=request.context
            )
            send_2 = partial(
                deps.clients.analytics_analytics_report_lifecycle.ScheduleAnalyticsReportExpiry,
                timeout=deps.settings.timeout
            )
            response_2 = await send_2(outgoing_2)
            returned_0_0 = response_0.outcome.message
            if returned_0_0:
                response.result.message = returned_0_0
            returned_0_1 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_1)
            returned_1_0 = response_1.preference.owner.user_id
            if returned_1_0:
                response.workspace.assignee.user_id = returned_1_0
            returned_1_1 = response_1.preference.priority
            if returned_1_1:
                response.workspace.priority = returned_1_1
            returned_2_0 = response_2.analytics_report.counterparty.email
            if returned_2_0:
                response.workspace.assignee.email = returned_2_0
            returned_2_1 = response_2.analytics_report.audit.updated_by
            if returned_2_1:
                response.workspace.audit.updated_by = returned_2_1
            echoed_0 = request.change.subject
            response.workspace.subject = echoed_0
            echoed_1 = request.ack.sequence
            response.sequence = echoed_1
            return response

    async def handle_replay_workspace_events(
        self,
        request: datahub_v1_workspace_integration_service_pb2.ReplayWorkspaceEventsRequest
    ) -> datahub_v1_workspace_integration_service_pb2.ReplayWorkspaceEventsResponse:
        """Replays a workspace."""
        deps = self.deps
        response = datahub_v1_workspace_integration_service_pb2.ReplayWorkspaceEventsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ReplayWorkspaceEvents', extra={'fields': {'endpoint': request.details.endpoint}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ReplayWorkspaceEvents',
                {'endpoint': request.details.endpoint}
            )
            response_0 = datahub_v1_data_share_approval_service_pb2.ApproveDataShareResponse()
            response_1 = recommendations_v1_recommendation_model_workflow_service_pb2.AdvanceRecommendationModelWorkflowResponse()
            outgoing_0 = datahub_v1_data_share_approval_service_pb2.ApproveDataShareRequest(
                annotations=dict(request.annotations),
                context=request.context,
                details=datahub_v1_data_share_approval_service_pb2.ApproveDataShareRequest.Details(
                    approver=identity_v1_refs_pb2.UserRef(email=request.context.actor.email)
                ),
                reason=request.reason
            )
            response_0 = await hooks.workspace_integration_replay_workspace_events0(
                deps.clients.datahub_data_share_approval,
                outgoing_0,
                deps.settings.timeout
            )
            outgoing_1 = recommendations_v1_recommendation_model_workflow_service_pb2.AdvanceRecommendationModelWorkflowRequest()
            outgoing_1.context.CopyFrom(request.context)
            outgoing_1.recommendation_model.address.postal_code = response_0.data_share.billing_address.postal_code
            outgoing_1.recommendation_model.address.recipient = response_0.data_share.billing_address.recipient
            outgoing_1.context.tenant_id = tenant_id.get()
            response_1 = await deps.clients.recommendations_recommendation_model_workflow.AdvanceRecommendationModelWorkflow(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.outcome.message
            if returned_0_0:
                response.outcome.message = returned_0_0
            returned_0_1 = response_0.result.message
            if returned_0_1:
                response.result.message = returned_0_1
            returned_1_0 = response_1.recommendation_model.audit.updated_at
            if returned_1_0.ListFields():
                response.workspace.audit.updated_at.MergeFrom(returned_1_0)
            returned_1_1 = response_1.result.status
            if returned_1_1:
                response.outcome.status = returned_1_1
            echoed_0 = request.workspace_id
            response.workspace.workspace_id = echoed_0
            return response

    async def handle_test_workspace_connection(
        self,
        request: datahub_v1_workspace_integration_service_pb2.TestWorkspaceConnectionRequest
    ) -> datahub_v1_workspace_integration_service_pb2.TestWorkspaceConnectionResponse:
        """Tests a workspace."""
        deps = self.deps
        response = datahub_v1_workspace_integration_service_pb2.TestWorkspaceConnectionResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('TestWorkspaceConnection', extra={'fields': {'endpoint': request.details.endpoint}})
            await deps.repository.audit(
                request.context.tenant_id,
                'TestWorkspaceConnection',
                {'endpoint': request.details.endpoint}
            )
            response_0 = metrics_v1_metric_series_admin_service_pb2.RepairMetricSeriesResponse()
            response_1 = modelregistry_v1_registered_model_reporting_service_pb2.ScheduleRegisteredModelReportResponse()
            response_2 = datahub_v1_workspace_workflow_service_pb2.AdvanceWorkspaceWorkflowResponse()
            outgoing_0 = metrics_v1_metric_series_admin_service_pb2.RepairMetricSeriesRequest(
                annotations=dict(request.annotations),
                context=request.context
            )
            port_0: WorkspaceIntegrationTestWorkspaceConnection0Port = WorkspaceIntegrationTestWorkspaceConnection0Adapter(
                deps.clients.metrics_metric_series_admin,
                deps.settings.timeout
            )
            response_0 = await port_0.execute(outgoing_0)
            outgoing_1 = modelregistry_v1_registered_model_reporting_service_pb2.ScheduleRegisteredModelReportRequest(
                annotations=dict(request.annotations),
                context=request.context,
                reason=request.reason
            )
            steps_1 = [
                partial(
                    deps.clients.modelregistry_registered_model_reporting.ScheduleRegisteredModelReport,
                    outgoing_1,
                    timeout=deps.settings.timeout
                )
            ]
            results_1 = await run_steps(steps_1)
            response_1 = results_1[-1]
            outgoing_2 = datahub_v1_workspace_workflow_service_pb2.AdvanceWorkspaceWorkflowRequest(
                context=request.context,
                details=datahub_v1_workspace_workflow_service_pb2.AdvanceWorkspaceWorkflowRequest.Details(
                    notify=common_v1_contact_pb2.ContactInfo(email=response_0.metric_series.owner.email)
                ),
                workspace=datahub_v1_datahub_pb2.Workspace(
                    audit=common_v1_audit_pb2.AuditInfo(updated_by=response_0.metric_series.audit.updated_by)
                )
            )
            response_2 = await WorkspaceIntegrationTestWorkspaceConnection2Adapter(
                deps.clients.datahub_workspace_workflow,
                deps.settings.timeout
            )(outgoing_2)
            returned_0_0 = response_0.metric_series.tags
            response.workspace.tags.extend(returned_0_0)
            returned_0_1 = response_0.outcome.message
            if returned_0_1:
                response.outcome.message = returned_0_1
            returned_1_0 = response_1.result.correlation_id
            if returned_1_0:
                response.result.correlation_id = returned_1_0
            returned_1_1 = response_1.result.status
            if returned_1_1:
                response.outcome.status = returned_1_1
            returned_2_0 = response_2.result.message
            if returned_2_0:
                response.outcome.message = returned_2_0
            returned_2_1 = response_2.result.details
            response.result.details.update(returned_2_1)
            echoed_0 = request.workspace_id
            response.workspace.workspace_id = echoed_0
            return response
