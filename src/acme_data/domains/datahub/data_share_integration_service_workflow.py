"""Application workflow for DataShare Integration."""

from __future__ import annotations

from functools import partial
from typing import cast
import logging

from google.protobuf.any_pb2 import Any as AnyMessage
from google.protobuf.json_format import MessageToDict
from google.protobuf.json_format import MessageToJson
from google.protobuf.json_format import Parse
from google.protobuf.json_format import ParseDict

from acme.analytics.v1 import cohort_workflow_service_pb2 as analytics_v1_cohort_workflow_service_pb2
from acme.authorization.v1 import (
    access_policy_validation_service_pb2 as authorization_v1_access_policy_validation_service_pb2,
)
from acme.authorization.v1 import authorization_pb2 as authorization_v1_authorization_pb2
from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.customers.v1 import (
    customer_segment_approval_service_pb2 as customers_v1_customer_segment_approval_service_pb2,
)
from acme.customers.v1 import customers_pb2 as customers_v1_customers_pb2
from acme.customers.v1 import preference_import_service_pb2 as customers_v1_preference_import_service_pb2
from acme.customers.v1 import preference_lifecycle_service_pb2 as customers_v1_preference_lifecycle_service_pb2
from acme.customers.v1 import (
    preference_lifecycle_service_pb2_grpc as customers_v1_preference_lifecycle_service_pb2_grpc,
)
from acme.datahub.v1 import data_share_integration_service_pb2 as datahub_v1_data_share_integration_service_pb2
from acme.datahub.v1 import notebook_integration_service_pb2 as datahub_v1_notebook_integration_service_pb2
from acme.datahub.v1 import notebook_workflow_service_pb2 as datahub_v1_notebook_workflow_service_pb2
from acme.datahub.v1 import workspace_approval_service_pb2 as datahub_v1_workspace_approval_service_pb2
from acme.datahub.v1 import workspace_notification_service_pb2 as datahub_v1_workspace_notification_service_pb2
from acme.driverapp.v1 import driver_home_service_pb2 as driverapp_v1_driver_home_service_pb2
from acme.fanportal.v1 import fan_session_service_pb2 as fanportal_v1_fan_session_service_pb2
from acme.fanportal.v1 import fanportal_pb2 as fanportal_v1_fanportal_pb2
from acme.fanportal.v1 import refs_pb2 as fanportal_v1_refs_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.metrics.v1 import dashboard_sync_service_pb2 as metrics_v1_dashboard_sync_service_pb2
from acme.metrics.v1 import metric_series_service_pb2 as metrics_v1_metric_series_service_pb2
from acme.metrics.v1 import metrics_pb2 as metrics_v1_metrics_pb2
from acme.pipelines.v1 import pipeline_approval_service_pb2 as pipelines_v1_pipeline_approval_service_pb2

from acme_data.domains.datahub.adapters import DataShareIntegrationAcknowledgeDataShareEvent0Adapter
from acme_data.domains.datahub.adapters import DataShareIntegrationListDataShareSources1Adapter
from acme_data.domains.datahub.adapters import DataShareIntegrationListDataShareSources1Port
from acme_data.domains.datahub.adapters import DataShareIntegrationRelayDataShareMessages1Adapter
from acme_data.domains.datahub.dependencies import Dependencies
from acme_data.domains.datahub.models import DataShareIntegrationIngestDataShareEvents1Command
from acme_data.domains.datahub.models import to_data_share_integration_ingest_data_share_events1_command
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class DataShareIntegrationServicerWorkflow:
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    async def handle_acknowledge_data_share_event(
        self,
        request: datahub_v1_data_share_integration_service_pb2.AcknowledgeDataShareEventRequest
    ) -> datahub_v1_data_share_integration_service_pb2.AcknowledgeDataShareEventResponse:
        """Acknowledges a data share."""
        deps = self.deps
        response = datahub_v1_data_share_integration_service_pb2.AcknowledgeDataShareEventResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('AcknowledgeDataShareEvent', extra={'fields': {'endpoint': request.details.endpoint}})
            await deps.repository.audit(
                request.context.tenant_id,
                'AcknowledgeDataShareEvent',
                {'endpoint': request.details.endpoint}
            )
            response_0 = authorization_v1_access_policy_validation_service_pb2.ExplainAccessPolicyDecisionResponse()
            response_1 = customers_v1_preference_lifecycle_service_pb2.SchedulePreferenceExpiryResponse()
            response_2 = fanportal_v1_fan_session_service_pb2.CreateFanSessionResponse()
            outgoing_0 = authorization_v1_access_policy_validation_service_pb2.ExplainAccessPolicyDecisionRequest(
                access_policy=authorization_v1_authorization_pb2.AccessPolicy(
                    block=authorization_v1_authorization_pb2.AccessPolicyBlockAction(reason=request.reason),
                    owner=identity_v1_refs_pb2.UserRef(email=request.context.actor.email)
                ),
                context=request.context
            )
            response_0 = await DataShareIntegrationAcknowledgeDataShareEvent0Adapter(
                deps.clients.authorization_access_policy_validation,
                deps.settings.timeout
            )(outgoing_0)
            outgoing_1 = customers_v1_preference_lifecycle_service_pb2.SchedulePreferenceExpiryRequest()
            outgoing_1.context.CopyFrom(request.context)
            if response_0.access_policy.WhichOneof('action') == 'discount':
                outgoing_1.preference.discount.amount.CopyFrom(response_0.access_policy.discount.amount)
            outgoing_1.preference.owner.display_name = response_0.access_policy.owner.display_name
            outgoing_1.preference.owner.user_id = response_0.access_policy.owner.user_id
            response_1 = await deps.clients.customers_preference_lifecycle.SchedulePreferenceExpiry(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = fanportal_v1_fan_session_service_pb2.CreateFanSessionRequest(
                context=request.context,
                fan_session=fanportal_v1_fanportal_pb2.FanSession(
                    customer=fanportal_v1_refs_pb2.WishlistRef(display_name=response_1.preference.owner.display_name)
                )
            )
            response_2 = await deps.clients.fanportal_fan_session.CreateFanSession(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.outcome.status
            if returned_0_0:
                response.result.status = returned_0_0
            returned_1_0 = response_1.result.correlation_id
            if returned_1_0:
                response.result.correlation_id = returned_1_0
            returned_2_0 = response_2.result.message
            if returned_2_0:
                response.result.message = returned_2_0
            echoed_0 = request.data_share_id
            response.data_share.data_share_id = echoed_0
            return response

    async def handle_connect_data_share_source(
        self,
        request: datahub_v1_data_share_integration_service_pb2.ConnectDataShareSourceRequest
    ) -> datahub_v1_data_share_integration_service_pb2.ConnectDataShareSourceResponse:
        """Connects a data share."""
        deps = self.deps
        response = datahub_v1_data_share_integration_service_pb2.ConnectDataShareSourceResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ConnectDataShareSource', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'ConnectDataShareSource', {'reason': request.reason})
            response_0 = metrics_v1_metric_series_service_pb2.CloneMetricSeriesResponse()
            response_1 = driverapp_v1_driver_home_service_pb2.SearchDriverHomesResponse()
            response_2 = metrics_v1_dashboard_sync_service_pb2.SyncDashboardsResponse()
            response_3 = customers_v1_customer_segment_approval_service_pb2.ListPendingCustomerSegmentsResponse()
            outgoing_0 = metrics_v1_metric_series_service_pb2.CloneMetricSeriesRequest(
                context=request.context,
                metric_series=metrics_v1_metrics_pb2.MetricSeries(
                    audit=common_v1_audit_pb2.AuditInfo(updated_at=request.details.received_at),
                    owner=identity_v1_refs_pb2.UserRef(
                        email=request.context.actor.email,
                        user_id=request.context.actor.user_id
                    )
                )
            )
            method_name_0 = 'CloneMetricSeries'
            response_0 = await getattr(
                deps.clients.metrics_metric_series,
                method_name_0
            )(outgoing_0, timeout=deps.settings.timeout)
            outgoing_1 = driverapp_v1_driver_home_service_pb2.SearchDriverHomesRequest()
            outgoing_1.context.CopyFrom(request.context)
            if response_0.metric_series.WhichOneof('locator') == 'address':
                outgoing_1.filter.region = response_0.metric_series.address.region
            outgoing_1.filter.created_after.CopyFrom(response_0.metric_series.audit.created_at)
            outgoing_1.filter.owner_id = response_0.metric_series.components.get(
                'primary',
                metrics_v1_metrics_pb2.MetricSeriesComponent()
            ).component_id
            response_1 = await deps.clients.driverapp_driver_home.SearchDriverHomes(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = metrics_v1_dashboard_sync_service_pb2.SyncDashboardsRequest(
                context=request.context,
                dashboard=metrics_v1_metrics_pb2.Dashboard(
                    billing_address=common_v1_address_pb2.PostalAddress(
                        locality=response_0.metric_series.address.locality
                    )
                )
            )
            document_2 = MessageToDict(outgoing_2, preserving_proto_field_name=True)
            outgoing_2 = ParseDict(document_2, metrics_v1_dashboard_sync_service_pb2.SyncDashboardsRequest())
            response_2 = await deps.clients.metrics_dashboard_sync.SyncDashboards(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            outgoing_3 = customers_v1_customer_segment_approval_service_pb2.ListPendingCustomerSegmentsRequest(
                context=request.context,
                filter=customers_v1_customer_segment_approval_service_pb2.ListPendingCustomerSegmentsRequest.Filter(
                    created_after=response_0.metric_series.audit.created_at,
                    region=response_2.dashboard.billing_address.region
                )
            )
            document_3 = MessageToJson(outgoing_3, preserving_proto_field_name=True)
            outgoing_3 = Parse(
                document_3,
                customers_v1_customer_segment_approval_service_pb2.ListPendingCustomerSegmentsRequest()
            )
            response_3 = await deps.clients.customers_customer_segment_approval.ListPendingCustomerSegments(
                outgoing_3,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.metric_series.address.recipient
            if returned_0_0:
                response.data_share.billing_address.recipient = returned_0_0
            returned_0_1 = response_0.metric_series.audit.created_at
            if returned_0_1.ListFields():
                response.data_share.audit.created_at.MergeFrom(returned_0_1)
            returned_1_0 = response_1.result.status
            if returned_1_0:
                response.outcome.status = returned_1_0
            returned_1_1 = response_1.result.details
            response.result.details.update(returned_1_1)
            returned_2_0 = response_2.dashboard.billing_address.country_code
            if returned_2_0:
                response.data_share.billing_address.country_code = returned_2_0
            returned_2_1 = response_2.dashboard.audit.created_at
            if returned_2_1.ListFields():
                response.data_share.audit.created_at.MergeFrom(returned_2_1)
            returned_3_0 = response_3.result.correlation_id
            if returned_3_0:
                response.result.correlation_id = returned_3_0
            returned_3_1 = response_3.result.message
            if returned_3_1:
                response.result.message = returned_3_1
            echoed_0 = request.data_share_id
            response.data_share.data_share_id = echoed_0
            return response

    async def handle_disconnect_data_share_source(
        self,
        request: datahub_v1_data_share_integration_service_pb2.DisconnectDataShareSourceRequest
    ) -> datahub_v1_data_share_integration_service_pb2.DisconnectDataShareSourceResponse:
        """Disconnects a data share."""
        deps = self.deps
        response = datahub_v1_data_share_integration_service_pb2.DisconnectDataShareSourceResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('DisconnectDataShareSource', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'DisconnectDataShareSource',
                {'reason': request.reason}
            )
            response_0 = metrics_v1_metric_series_service_pb2.SearchMetricSeriesesResponse()
            response_1 = datahub_v1_notebook_workflow_service_pb2.PauseNotebookWorkflowResponse()
            response_2 = customers_v1_preference_lifecycle_service_pb2.SchedulePreferenceExpiryResponse()
            outgoing_0 = metrics_v1_metric_series_service_pb2.SearchMetricSeriesesRequest()
            outgoing_0.context.CopyFrom(request.context)
            outgoing_0.filter.created_after.CopyFrom(request.details.received_at)
            outgoing_0.filter.owner_id = request.details.message_id
            outgoing_0.filter.labels.update(dict(request.annotations))
            merged_0 = metrics_v1_metric_series_service_pb2.SearchMetricSeriesesRequest()
            merged_0.MergeFrom(outgoing_0)
            outgoing_0.CopyFrom(merged_0)
            response_0 = await deps.clients.metrics_metric_series.SearchMetricSerieses(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = datahub_v1_notebook_workflow_service_pb2.PauseNotebookWorkflowRequest(
                annotations=dict(request.annotations),
                context=request.context
            )
            envelope_1 = AnyMessage()
            envelope_1.Pack(outgoing_1)
            outgoing_1 = datahub_v1_notebook_workflow_service_pb2.PauseNotebookWorkflowRequest()
            if not envelope_1.Unpack(outgoing_1):
                raise ValueError("partner envelope contains the wrong request type")
            response_1 = await deps.clients.datahub_notebook_workflow.PauseNotebookWorkflow(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = customers_v1_preference_lifecycle_service_pb2.SchedulePreferenceExpiryRequest(
                context=request.context,
                preference=customers_v1_customers_pb2.Preference(
                    owner=identity_v1_refs_pb2.UserRef(display_name=response_1.notebook.counterparty.display_name),
                    priority=response_1.notebook.counterparty.priority
                )
            )
            registered_2 = cast(
                customers_v1_preference_lifecycle_service_pb2_grpc.PreferenceLifecycleServiceStub,
                deps.clients.registry['acme.customers.v1.PreferenceLifecycleService']
            )
            response_2 = await registered_2.SchedulePreferenceExpiry(outgoing_2, timeout=deps.settings.timeout)
            returned_0_0 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_0)
            returned_0_1 = response_0.result.status
            if returned_0_1:
                response.result.status = returned_0_1
            returned_1_0 = response_1.notebook.audit.created_at
            if returned_1_0.ListFields():
                response.data_share.audit.created_at.MergeFrom(returned_1_0)
            returned_1_1 = response_1.notebook.audit.updated_at
            if returned_1_1.ListFields():
                response.data_share.audit.updated_at.MergeFrom(returned_1_1)
            returned_2_0 = response_2.result.status
            if returned_2_0:
                response.outcome.status = returned_2_0
            echoed_0 = request.data_share_id
            response.data_share.data_share_id = echoed_0
            return response

    async def handle_ingest_data_share_events(
        self,
        request: datahub_v1_data_share_integration_service_pb2.IngestDataShareEventsRequest
    ) -> datahub_v1_data_share_integration_service_pb2.IngestDataShareEventsResponse:
        """Takes a stream of data shares and answers once at the end."""
        deps = self.deps
        response = datahub_v1_data_share_integration_service_pb2.IngestDataShareEventsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('IngestDataShareEvents', extra={'fields': {'sequence': request.sequence}})
            await deps.repository.audit(
                request.context.tenant_id,
                'IngestDataShareEvents',
                {'sequence': request.sequence}
            )
            if request.WhichOneof('chunk') == 'record':
                await deps.repository.save_data_share(request.context.tenant_id, request.record)
            response_0 = datahub_v1_workspace_approval_service_pb2.CommentWorkspaceApprovalResponse()
            response_1 = authorization_v1_access_policy_validation_service_pb2.ScoreAccessPolicyResponse()
            response_2 = analytics_v1_cohort_workflow_service_pb2.ListCohortWorkflowsResponse()
            response_3 = pipelines_v1_pipeline_approval_service_pb2.ListPendingPipelinesResponse()
            outgoing_0 = datahub_v1_workspace_approval_service_pb2.CommentWorkspaceApprovalRequest()
            outgoing_0.context.CopyFrom(request.context)
            if request.WhichOneof('chunk') == 'header':
                outgoing_0.workspace.assignee.email = request.header.submitted_by.email
            if request.WhichOneof('chunk') == 'header':
                outgoing_0.workspace.requester.phone = request.header.submitted_by.phone
            if request.WhichOneof('chunk') == 'record':
                outgoing_0.workspace.audit.etag = request.record.audit.etag
            if request.WhichOneof('chunk') == 'record':
                field_0_4_part_1 = outgoing_0.workspace.comments.add()
                field_0_4_part_1.created_at.CopyFrom(request.record.audit.created_at)
            response_0 = await deps.clients.datahub_workspace_approval.CommentWorkspaceApproval(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            command_1 = DataShareIntegrationIngestDataShareEvents1Command.model_validate(
                {
                    'context': request.context,
                    'access_policy_audit_updated_by': request.record.audit.updated_by,
                    'access_policy_audit_updated_at': request.record.audit.updated_at,
                    'details_destination_recipient': request.record.billing_address.recipient
                }
            )
            outgoing_1 = to_data_share_integration_ingest_data_share_events1_command(command_1)
            response_1 = await deps.clients.authorization_access_policy_validation.ScoreAccessPolicy(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = analytics_v1_cohort_workflow_service_pb2.ListCohortWorkflowsRequest(
                context=request.context,
                filter=analytics_v1_cohort_workflow_service_pb2.ListCohortWorkflowsRequest.Filter(
                    created_after=response_0.outcome.effective_at,
                    labels=dict(response_1.access_policy.parameters),
                    owner_id=response_0.workspace.customer.customer_id,
                    region=request.record.billing_address.region
                )
            )
            send_2 = partial(deps.clients.analytics_cohort_workflow.ListCohortWorkflows, timeout=deps.settings.timeout)
            response_2 = await send_2(outgoing_2)
            outgoing_3 = pipelines_v1_pipeline_approval_service_pb2.ListPendingPipelinesRequest()
            outgoing_3.context.CopyFrom(request.context)
            if request.WhichOneof('chunk') == 'record':
                outgoing_3.filter.region = request.record.billing_address.region
            response_3 = await deps.clients.pipelines_pipeline_approval.ListPendingPipelines(
                outgoing_3,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.result.message = returned_0_0
            returned_1_0 = response_1.result.reference_ids
            response.result.reference_ids.extend(returned_1_0)
            returned_1_1 = response_1.access_policy.block.reason
            returned_1_1_part_0 = response.rejections.add()
            if returned_1_1:
                returned_1_1_part_0.reason = returned_1_1
            returned_2_0 = response_2.result.status
            if returned_2_0:
                response.result.status = returned_2_0
            returned_2_1 = response_2.result.details
            response.result.details.update(returned_2_1)
            returned_3_0 = response_3.result.details
            response.result.details.update(returned_3_0)
            return response

    async def handle_list_data_share_sources(
        self,
        request: datahub_v1_data_share_integration_service_pb2.ListDataShareSourcesRequest
    ) -> datahub_v1_data_share_integration_service_pb2.ListDataShareSourcesResponse:
        """Lists data shares a page at a time."""
        deps = self.deps
        response = datahub_v1_data_share_integration_service_pb2.ListDataShareSourcesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ListDataShareSources', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ListDataShareSources',
                {'order_by': request.order_by}
            )
            response_0 = metrics_v1_metric_series_service_pb2.SearchMetricSeriesesResponse()
            response_1 = datahub_v1_workspace_notification_service_pb2.SendWorkspaceTestNoticeResponse()
            outgoing_0 = metrics_v1_metric_series_service_pb2.SearchMetricSeriesesRequest(
                context=request.context,
                filter=metrics_v1_metric_series_service_pb2.SearchMetricSeriesesRequest.Filter(
                    created_after=request.filter.created_after,
                    query=request.filter.query
                )
            )
            response_0 = await deps.clients.metrics_metric_series.SearchMetricSerieses(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = datahub_v1_workspace_notification_service_pb2.SendWorkspaceTestNoticeRequest(
                annotations=dict(request.filter.labels),
                context=request.context,
                details=datahub_v1_workspace_notification_service_pb2.SendWorkspaceTestNoticeRequest.Details(
                    recipient=common_v1_contact_pb2.ContactInfo(email=request.context.actor.email),
                    variables=dict(response_0.result.details)
                )
            )
            port_1: DataShareIntegrationListDataShareSources1Port = DataShareIntegrationListDataShareSources1Adapter(
                deps.clients.datahub_workspace_notification,
                deps.settings.timeout
            )
            response_1 = await port_1.execute(outgoing_1)
            returned_0_0 = response_0.page_info.total_size
            if returned_0_0:
                response.page_info.total_size = returned_0_0
            returned_1_0 = response_1.outcome.message
            if returned_1_0:
                response.result.message = returned_1_0
            return response

    async def handle_relay_data_share_messages(
        self,
        request: datahub_v1_data_share_integration_service_pb2.RelayDataShareMessagesRequest
    ) -> datahub_v1_data_share_integration_service_pb2.RelayDataShareMessagesResponse:
        """Exchanges changes of data shares with a peer."""
        deps = self.deps
        response = datahub_v1_data_share_integration_service_pb2.RelayDataShareMessagesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('RelayDataShareMessages', extra={'fields': {'cursor': request.cursor}})
            await deps.repository.audit(request.context.tenant_id, 'RelayDataShareMessages', {'cursor': request.cursor})
            if request.WhichOneof('frame') == 'change':
                await deps.repository.save_data_share(request.context.tenant_id, request.change)
            response_0 = datahub_v1_notebook_integration_service_pb2.DisconnectNotebookSourceResponse()
            response_1 = customers_v1_preference_import_service_pb2.ValidatePreferenceImportResponse()
            outgoing_0 = datahub_v1_notebook_integration_service_pb2.DisconnectNotebookSourceRequest()
            outgoing_0.context.CopyFrom(request.context)
            if request.WhichOneof('frame') == 'change':
                outgoing_0.notebook_id = request.change.counterparty.notebook_id
            if request.WhichOneof('frame') == 'change':
                outgoing_0.details.received_at.CopyFrom(request.change.audit.created_at)
            if request.WhichOneof('frame') == 'change':
                outgoing_0.details.message_id = request.change.data_share_id
            if request.WhichOneof('frame') == 'change':
                outgoing_0.annotations.update(dict(request.change.metadata))
            response_0 = await deps.clients.datahub_notebook_integration.DisconnectNotebookSource(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = customers_v1_preference_import_service_pb2.ValidatePreferenceImportRequest(
                context=request.context,
                preference=customers_v1_customers_pb2.Preference(
                    audit=common_v1_audit_pb2.AuditInfo(
                        etag=request.change.audit.etag,
                        updated_at=request.change.audit.updated_at
                    )
                )
            )
            response_1 = await DataShareIntegrationRelayDataShareMessages1Adapter(
                deps.clients.customers_preference_import,
                deps.settings.timeout
            )(outgoing_1)
            returned_0_0 = response_0.result.status
            if returned_0_0:
                response.result.status = returned_0_0
            returned_0_1 = response_0.notebook.audit.created_at
            if returned_0_1.ListFields():
                response.data_share.audit.created_at.MergeFrom(returned_0_1)
            returned_1_0 = response_1.result.details
            response.result.details.update(returned_1_0)
            echoed_0 = request.change.metadata
            response.data_share.metadata.update(echoed_0)
            echoed_1 = request.change.status
            response.data_share.status = echoed_1
            return response

    async def handle_replay_data_share_events(
        self,
        request: datahub_v1_data_share_integration_service_pb2.ReplayDataShareEventsRequest
    ) -> datahub_v1_data_share_integration_service_pb2.ReplayDataShareEventsResponse:
        """Replays a data share."""
        deps = self.deps
        response = datahub_v1_data_share_integration_service_pb2.ReplayDataShareEventsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ReplayDataShareEvents', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'ReplayDataShareEvents', {'reason': request.reason})
            response_0 = customers_v1_customer_segment_approval_service_pb2.RejectCustomerSegmentResponse()
            response_1 = authorization_v1_access_policy_validation_service_pb2.CheckAccessPolicyEligibilityResponse()
            outgoing_0 = customers_v1_customer_segment_approval_service_pb2.RejectCustomerSegmentRequest(
                annotations=dict(request.annotations),
                context=request.context,
                details=customers_v1_customer_segment_approval_service_pb2.RejectCustomerSegmentRequest.Details(
                    approver=identity_v1_refs_pb2.UserRef(email=request.context.actor.email)
                )
            )
            response_0 = cast(customers_v1_customer_segment_approval_service_pb2.RejectCustomerSegmentResponse, await deps.bus.request(
                'acme.datahub.v1.DataShareIntegrationService/ReplayDataShareEvents/0', outgoing_0, deps.settings.timeout,
            ))
            outgoing_1 = authorization_v1_access_policy_validation_service_pb2.CheckAccessPolicyEligibilityRequest()
            outgoing_1.context.CopyFrom(request.context)
            if response_0.customer_segment.WhichOneof('action') == 'block':
                outgoing_1.access_policy.block.reason = response_0.customer_segment.block.reason
            outgoing_1.access_policy.owner.user_id = response_0.customer_segment.owner.user_id
            outgoing_1.access_policy.audit.etag = response_0.customer_segment.audit.etag
            response_1 = await deps.clients.authorization_access_policy_validation.CheckAccessPolicyEligibility(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.customer_segment.discount.amount
            returned_0_0_part_1 = response.data_share.lines.add()
            if returned_0_0.ListFields():
                returned_0_0_part_1.tax.amount.MergeFrom(returned_0_0)
            returned_0_1 = response_0.result.details
            response.result.details.update(returned_0_1)
            returned_1_0 = response_1.access_policy.audit.updated_at
            if returned_1_0.ListFields():
                response.data_share.audit.updated_at.MergeFrom(returned_1_0)
            echoed_0 = request.data_share_id
            response.data_share.data_share_id = echoed_0
            return response
