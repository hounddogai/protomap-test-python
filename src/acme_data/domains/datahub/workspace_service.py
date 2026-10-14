"""Manages workspaces: creates, reads, changes, and lists them."""

from __future__ import annotations

from collections.abc import AsyncIterator
from collections.abc import Awaitable
from collections.abc import Callable
from typing import Any
from typing import cast
import asyncio
import logging

from google.protobuf.any_pb2 import Any as AnyMessage
from google.protobuf.json_format import MessageToJson
from google.protobuf.json_format import Parse
import grpc

from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.customers.v1 import consent_record_workflow_service_pb2 as customers_v1_consent_record_workflow_service_pb2
from acme.customers.v1 import customer_segment_sync_service_pb2 as customers_v1_customer_segment_sync_service_pb2
from acme.customers.v1 import customer_workflow_service_pb2 as customers_v1_customer_workflow_service_pb2
from acme.customers.v1 import customers_pb2 as customers_v1_customers_pb2
from acme.customers.v1 import household_approval_service_pb2 as customers_v1_household_approval_service_pb2
from acme.customers.v1 import refs_pb2 as customers_v1_refs_pb2
from acme.datahub.v1 import data_share_approval_service_pb2 as datahub_v1_data_share_approval_service_pb2
from acme.datahub.v1 import data_share_validation_service_pb2 as datahub_v1_data_share_validation_service_pb2
from acme.datahub.v1 import datahub_pb2 as datahub_v1_datahub_pb2
from acme.datahub.v1 import notebook_approval_service_pb2 as datahub_v1_notebook_approval_service_pb2
from acme.datahub.v1 import notebook_workflow_service_pb2 as datahub_v1_notebook_workflow_service_pb2
from acme.datahub.v1 import workspace_approval_service_pb2 as datahub_v1_workspace_approval_service_pb2
from acme.datahub.v1 import workspace_integration_service_pb2 as datahub_v1_workspace_integration_service_pb2
from acme.datahub.v1 import workspace_notification_service_pb2 as datahub_v1_workspace_notification_service_pb2
from acme.datahub.v1 import workspace_service_pb2 as datahub_v1_workspace_service_pb2
from acme.datahub.v1 import workspace_service_pb2_grpc as datahub_v1_workspace_service_pb2_grpc
from acme.datahub.v1 import workspace_workflow_service_pb2 as datahub_v1_workspace_workflow_service_pb2
from acme.featurestore.v1 import (
    feature_value_reporting_service_pb2 as featurestore_v1_feature_value_reporting_service_pb2,
)
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.labeling.v1 import annotation_approval_service_pb2 as labeling_v1_annotation_approval_service_pb2
from acme.labeling.v1 import label_set_approval_service_pb2 as labeling_v1_label_set_approval_service_pb2
from acme.labeling.v1 import labeling_pb2 as labeling_v1_labeling_pb2
from acme.labeling.v1 import refs_pb2 as labeling_v1_refs_pb2
from acme.lineage.v1 import lineage_node_workflow_service_pb2 as lineage_v1_lineage_node_workflow_service_pb2
from acme.lineage.v1 import lineage_pb2 as lineage_v1_lineage_pb2
from acme.metrics.v1 import metric_series_history_service_pb2 as metrics_v1_metric_series_history_service_pb2
from acme.metrics.v1 import metrics_pb2 as metrics_v1_metrics_pb2
from acme.pipelines.v1 import pipeline_step_reporting_service_pb2 as pipelines_v1_pipeline_step_reporting_service_pb2

from acme_data.domains.datahub import hooks
from acme_data.domains.datahub.adapters import WorkspaceBatchCreateWorkspaces2Adapter
from acme_data.domains.datahub.adapters import WorkspaceBatchCreateWorkspaces2Port
from acme_data.domains.datahub.adapters import WorkspaceUpdateWorkspace1Adapter
from acme_data.domains.datahub.adapters import WorkspaceUpdateWorkspace1Port
from acme_data.domains.datahub.adapters import WorkspaceWatchWorkspaces0Adapter
from acme_data.domains.datahub.dependencies import Dependencies
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_id
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class WorkspaceServicer(datahub_v1_workspace_service_pb2_grpc.WorkspaceServiceServicer):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    async def BatchCreateWorkspaces(
        self, requests: AsyncIterator[
            datahub_v1_workspace_service_pb2.BatchCreateWorkspacesRequest
        ], context: grpc.aio.ServicerContext,
    ) -> datahub_v1_workspace_service_pb2.BatchCreateWorkspacesResponse:
        """Takes a stream of workspaces and answers once at the end."""
        response = datahub_v1_workspace_service_pb2.BatchCreateWorkspacesResponse()
        async for request in requests:
            response.MergeFrom(await self.handle_batch_create_workspaces(request))
        return response

    @rpc_errors
    @retry_transient
    async def BatchGetWorkspaces(
        self, request: datahub_v1_workspace_service_pb2.BatchGetWorkspacesRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_workspace_service_pb2.BatchGetWorkspacesResponse:
        """Returns several workspaces at once."""
        return await self.handle_batch_get_workspaces(request)

    @rpc_errors
    async def CloneWorkspace(
        self, request: datahub_v1_workspace_service_pb2.CloneWorkspaceRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_workspace_service_pb2.CloneWorkspaceResponse:
        """Creates a workspace."""
        return await self.handle_clone_workspace(request)

    @rpc_errors
    async def CreateWorkspace(
        self, request: datahub_v1_workspace_service_pb2.CreateWorkspaceRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_workspace_service_pb2.CreateWorkspaceResponse:
        """Creates a workspace."""
        return await self.handle_create_workspace(request)

    @rpc_errors
    async def DeleteWorkspace(
        self, request: datahub_v1_workspace_service_pb2.DeleteWorkspaceRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_workspace_service_pb2.DeleteWorkspaceResponse:
        """Deletes a workspace."""
        return await self.handle_delete_workspace(request)

    @rpc_errors
    @retry_transient
    async def GetWorkspace(
        self, request: datahub_v1_workspace_service_pb2.GetWorkspaceRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_workspace_service_pb2.GetWorkspaceResponse:
        """Returns a workspace."""
        return await self.handle_get_workspace(request)

    @rpc_errors
    @retry_transient
    async def ListWorkspaces(
        self, request: datahub_v1_workspace_service_pb2.ListWorkspacesRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_workspace_service_pb2.ListWorkspacesResponse:
        """Lists workspaces a page at a time."""
        return await self.handle_list_workspaces(request)

    @rpc_errors
    @retry_transient
    async def SearchWorkspaces(
        self, request: datahub_v1_workspace_service_pb2.SearchWorkspacesRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_workspace_service_pb2.SearchWorkspacesResponse:
        """Lists workspaces a page at a time."""
        return await self.handle_search_workspaces(request)

    @rpc_errors
    async def UpdateWorkspace(
        self, request: datahub_v1_workspace_service_pb2.UpdateWorkspaceRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_workspace_service_pb2.UpdateWorkspaceResponse:
        """Changes a workspace."""
        return await self.handle_update_workspace(request)

    @stream_errors
    async def WatchWorkspaces(
        self, request: datahub_v1_workspace_service_pb2.WatchWorkspacesRequest, context: grpc.aio.ServicerContext,
    ) -> AsyncIterator[datahub_v1_workspace_service_pb2.WatchWorkspacesResponse]:
        """Streams the changes of workspaces as they happen."""
        response = await self.handle_watch_workspaces(request)
        for item in messages((response,)):
            yield item

    async def handle_batch_create_workspaces(
        self,
        request: datahub_v1_workspace_service_pb2.BatchCreateWorkspacesRequest
    ) -> datahub_v1_workspace_service_pb2.BatchCreateWorkspacesResponse:
        """Takes a stream of workspaces and answers once at the end."""
        deps = self.deps
        response = datahub_v1_workspace_service_pb2.BatchCreateWorkspacesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('BatchCreateWorkspaces', extra={'fields': {'sequence': request.sequence}})
            await deps.repository.audit(
                request.context.tenant_id,
                'BatchCreateWorkspaces',
                {'sequence': request.sequence}
            )
            if request.WhichOneof('chunk') == 'record':
                await deps.repository.save_workspace(request.context.tenant_id, request.record)
            response_0 = labeling_v1_label_set_approval_service_pb2.RecallLabelSetResponse()
            response_1 = datahub_v1_workspace_notification_service_pb2.SubscribeWorkspaceUpdatesResponse()
            response_2 = pipelines_v1_pipeline_step_reporting_service_pb2.SchedulePipelineStepReportResponse()
            response_3 = datahub_v1_data_share_approval_service_pb2.RejectDataShareResponse()
            outgoing_0 = labeling_v1_label_set_approval_service_pb2.RecallLabelSetRequest(
                context=request.context,
                label_set=labeling_v1_labeling_pb2.LabelSet(
                    children=[
                        labeling_v1_labeling_pb2.LabelSet(
                            children=[
                                labeling_v1_labeling_pb2.LabelSet(
                                    manager=identity_v1_refs_pb2.UserRef(
                                        email=request.record.requester.email,
                                        user_id=request.record.assignee.user_id
                                    )
                                )
                            ],
                            manager=identity_v1_refs_pb2.UserRef(email=request.record.customer.email)
                        )
                    ]
                )
            )
            response_0 = await hooks.workspace_batch_create_workspaces0(
                deps.clients.labeling_label_set_approval,
                outgoing_0,
                deps.settings.timeout
            )
            outgoing_1 = datahub_v1_workspace_notification_service_pb2.SubscribeWorkspaceUpdatesRequest()
            outgoing_1.context.CopyFrom(request.context)
            if request.WhichOneof('chunk') == 'record':
                outgoing_1.details.recipient.name.CopyFrom(request.record.requester.name)
            if request.WhichOneof('chunk') == 'record':
                outgoing_1.details.recipient.preferred_channel = request.record.requester.preferred_channel
            response_1 = await deps.clients.datahub_workspace_notification.SubscribeWorkspaceUpdates(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = pipelines_v1_pipeline_step_reporting_service_pb2.SchedulePipelineStepReportRequest(
                annotations=dict(response_1.result.details),
                context=request.context,
                details=pipelines_v1_pipeline_step_reporting_service_pb2.SchedulePipelineStepReportRequest.Details(
                    filters=dict(request.record.custom_fields),
                    format=request.header.format
                )
            )
            port_2: WorkspaceBatchCreateWorkspaces2Port = WorkspaceBatchCreateWorkspaces2Adapter(
                deps.clients.pipelines_pipeline_step_reporting,
                deps.settings.timeout
            )
            response_2 = await port_2.execute(outgoing_2)
            async for item_3 in async_messages(request.record.comments):
                outgoing_3 = datahub_v1_data_share_approval_service_pb2.RejectDataShareRequest(
                    context=request.context,
                    data_share=datahub_v1_datahub_pb2.DataShare(
                        audit=common_v1_audit_pb2.AuditInfo(created_at=item_3.created_at)
                    ),
                    details=datahub_v1_data_share_approval_service_pb2.RejectDataShareRequest.Details(
                        approver_email=item_3.author_email
                    )
                )
                response_3 = await deps.clients.datahub_data_share_approval.RejectDataShare(
                    outgoing_3,
                    timeout=deps.settings.timeout
                )
            returned_0_0 = response_0.outcome.status
            if returned_0_0:
                response.result.status = returned_0_0
            returned_1_0 = response_1.result.reference_ids
            response.result.reference_ids.extend(returned_1_0)
            returned_2_0 = response_2.result.details
            response.result.details.update(returned_2_0)
            returned_2_1 = response_2.result.message
            if returned_2_1:
                response.result.message = returned_2_1
            return response

    async def handle_batch_get_workspaces(
        self,
        request: datahub_v1_workspace_service_pb2.BatchGetWorkspacesRequest
    ) -> datahub_v1_workspace_service_pb2.BatchGetWorkspacesResponse:
        """Returns several workspaces at once."""
        deps = self.deps
        response = datahub_v1_workspace_service_pb2.BatchGetWorkspacesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('BatchGetWorkspaces', extra={'fields': {'domain': 'datahub'}})
            await deps.repository.audit(request.context.tenant_id, 'BatchGetWorkspaces', {})
            response_0 = customers_v1_household_approval_service_pb2.CommentHouseholdApprovalResponse()
            outgoing_0 = customers_v1_household_approval_service_pb2.CommentHouseholdApprovalRequest(
                context=request.context,
                household=customers_v1_customers_pb2.Household(
                    children=[
                        customers_v1_customers_pb2.Household(
                            children=[
                                customers_v1_customers_pb2.Household(
                                    audit=common_v1_audit_pb2.AuditInfo(updated_at=request.context.deadline)
                                )
                            ]
                        )
                    ],
                    manager=identity_v1_refs_pb2.UserRef(
                        email=request.context.actor.email,
                        user_id=request.context.actor.user_id
                    )
                )
            )
            response_0 = await deps.clients.customers_household_approval.CommentHouseholdApproval(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.outcome.status
            if returned_0_0:
                response.result.status = returned_0_0
            return response

    async def handle_clone_workspace(
        self,
        request: datahub_v1_workspace_service_pb2.CloneWorkspaceRequest
    ) -> datahub_v1_workspace_service_pb2.CloneWorkspaceResponse:
        """Creates a workspace."""
        deps = self.deps
        response = datahub_v1_workspace_service_pb2.CloneWorkspaceResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CloneWorkspace', extra={'fields': {'request_id': request.request_id}})
            await deps.repository.audit(request.context.tenant_id, 'CloneWorkspace', {'request_id': request.request_id})
            await deps.repository.save_workspace(request.context.tenant_id, request.workspace)
            response_0 = datahub_v1_data_share_validation_service_pb2.LintDataSharesResponse()
            response_1 = datahub_v1_workspace_approval_service_pb2.EscalateWorkspaceResponse()
            response_2 = customers_v1_consent_record_workflow_service_pb2.AdvanceConsentRecordWorkflowResponse()
            outgoing_0 = datahub_v1_data_share_validation_service_pb2.LintDataSharesRequest(
                context=request.context,
                details=datahub_v1_data_share_validation_service_pb2.LintDataSharesRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(
                        email=request.workspace.customer.email,
                        name=request.workspace.requester.name,
                        preferred_channel=request.workspace.requester.preferred_channel
                    )
                )
            )
            response_0 = cast(datahub_v1_data_share_validation_service_pb2.LintDataSharesResponse, await deps.bus.request(
                'acme.datahub.v1.WorkspaceService/CloneWorkspace/0', outgoing_0, deps.settings.timeout,
            ))
            outgoing_1 = datahub_v1_workspace_approval_service_pb2.EscalateWorkspaceRequest(
                context=request.context,
                details=datahub_v1_workspace_approval_service_pb2.EscalateWorkspaceRequest.Details(
                    approver=identity_v1_refs_pb2.UserRef(
                        email=request.workspace.requester.email,
                        user_id=request.workspace.assignee.user_id
                    )
                ),
                workspace=datahub_v1_datahub_pb2.Workspace(
                    assignee=identity_v1_refs_pb2.UserRef(email=request.workspace.assignee.email),
                    audit=common_v1_audit_pb2.AuditInfo(updated_by=request.workspace.audit.updated_by)
                )
            )
            response_1 = await deps.clients.datahub_workspace_approval.EscalateWorkspace(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = customers_v1_consent_record_workflow_service_pb2.AdvanceConsentRecordWorkflowRequest(
                consent_record=customers_v1_customers_pb2.ConsentRecord(
                    subject=customers_v1_refs_pb2.HouseholdRef(
                        display_name=response_0.data_share.counterparty.display_name
                    )
                ),
                context=request.context,
                details=customers_v1_consent_record_workflow_service_pb2.AdvanceConsentRecordWorkflowRequest.Details(
                    notify=common_v1_contact_pb2.ContactInfo(
                        email=request.workspace.requester.email,
                        name=request.workspace.requester.name
                    )
                )
            )
            method_name_2 = 'AdvanceConsentRecordWorkflow'
            response_2 = await getattr(
                deps.clients.customers_consent_record_workflow,
                method_name_2
            )(outgoing_2, timeout=deps.settings.timeout)
            returned_0_0 = response_0.data_share.counterparty.display_name
            if returned_0_0:
                response.workspace.assignee.display_name = returned_0_0
            returned_1_0 = response_1.workspace.audit.created_at
            if returned_1_0.ListFields():
                response.workspace.audit.created_at.MergeFrom(returned_1_0)
            returned_1_1 = response_1.workspace.audit.created_at
            returned_1_1_part_1 = response.workspace.comments.add()
            if returned_1_1.ListFields():
                returned_1_1_part_1.created_at.MergeFrom(returned_1_1)
            returned_2_0 = response_2.outcome.message
            if returned_2_0:
                response.result.message = returned_2_0
            returned_2_1 = response_2.result.status
            if returned_2_1:
                response.result.status = returned_2_1
            echoed_0 = request.workspace.requester
            response.workspace.requester.CopyFrom(echoed_0)
            echoed_1 = request.workspace.custom_fields
            response.workspace.custom_fields.update(echoed_1)
            return response

    async def handle_create_workspace(
        self,
        request: datahub_v1_workspace_service_pb2.CreateWorkspaceRequest
    ) -> datahub_v1_workspace_service_pb2.CreateWorkspaceResponse:
        """Creates a workspace."""
        deps = self.deps
        response = datahub_v1_workspace_service_pb2.CreateWorkspaceResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CreateWorkspace', extra={'fields': {'request_id': request.request_id}})
            await deps.repository.audit(
                request.context.tenant_id,
                'CreateWorkspace',
                {'request_id': request.request_id}
            )
            await deps.repository.save_workspace(request.context.tenant_id, request.workspace)
            response_0 = lineage_v1_lineage_node_workflow_service_pb2.ListLineageNodeWorkflowsResponse()
            response_1 = metrics_v1_metric_series_history_service_pb2.CompareMetricSeriesVersionsResponse()
            fields_0: dict[str, Any] = {
                'context': request.context,
                'filter': {
                    'created_after': request.workspace.sla.due_at,
                    'labels': dict(request.workspace.custom_fields),
                    'owner_id': request.workspace.customer.customer_id
                }
            }
            outgoing_0 = lineage_v1_lineage_node_workflow_service_pb2.ListLineageNodeWorkflowsRequest(**fields_0)
            response_0 = await deps.clients.lineage_lineage_node_workflow.ListLineageNodeWorkflows(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            for item_1 in request.workspace.comments:
                outgoing_1 = metrics_v1_metric_series_history_service_pb2.CompareMetricSeriesVersionsRequest(
                    context=request.context,
                    details=metrics_v1_metric_series_history_service_pb2.CompareMetricSeriesVersionsRequest.Details(
                        author_email=item_1.author_email
                    ),
                    metric_series=metrics_v1_metrics_pb2.MetricSeries(
                        audit=common_v1_audit_pb2.AuditInfo(
                            created_at=item_1.created_at,
                            etag=request.workspace.audit.etag
                        ),
                        owner=identity_v1_refs_pb2.UserRef(email=request.workspace.assignee.email)
                    )
                )
                response_1 = await deps.clients.metrics_metric_series_history.CompareMetricSeriesVersions(
                    outgoing_1,
                    timeout=deps.settings.timeout
                )
            returned_0_0 = response_0.result.details
            response.result.details.update(returned_0_0)
            echoed_0 = request.workspace.status
            response.workspace.status = echoed_0
            echoed_1 = request.workspace.requester
            response.workspace.requester.CopyFrom(echoed_1)
            return response

    async def handle_delete_workspace(
        self,
        request: datahub_v1_workspace_service_pb2.DeleteWorkspaceRequest
    ) -> datahub_v1_workspace_service_pb2.DeleteWorkspaceResponse:
        """Deletes a workspace."""
        deps = self.deps
        response = datahub_v1_workspace_service_pb2.DeleteWorkspaceResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('DeleteWorkspace', extra={'fields': {'force': request.force}})
            await deps.repository.audit(request.context.tenant_id, 'DeleteWorkspace', {'force': request.force})
            response_0 = customers_v1_customer_segment_sync_service_pb2.ReconcileCustomerSegmentsResponse()
            response_1 = datahub_v1_notebook_approval_service_pb2.RecallNotebookResponse()
            response_2 = datahub_v1_workspace_workflow_service_pb2.StartWorkspaceWorkflowResponse()
            response_3 = datahub_v1_notebook_workflow_service_pb2.SignalNotebookWorkflowResponse()
            outgoing_0 = customers_v1_customer_segment_sync_service_pb2.ReconcileCustomerSegmentsRequest(
                context=request.context,
                customer_segment=customers_v1_customers_pb2.CustomerSegment(
                    audit=common_v1_audit_pb2.AuditInfo(etag=request.etag),
                    owner=identity_v1_refs_pb2.UserRef(user_id=request.context.actor.user_id)
                ),
                reason=request.reason
            )
            document_0 = MessageToJson(outgoing_0, preserving_proto_field_name=True)
            outgoing_0 = Parse(
                document_0,
                customers_v1_customer_segment_sync_service_pb2.ReconcileCustomerSegmentsRequest()
            )
            response_0 = await deps.clients.customers_customer_segment_sync.ReconcileCustomerSegments(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = datahub_v1_notebook_approval_service_pb2.RecallNotebookRequest()
            outgoing_1.context.CopyFrom(request.context)
            field_1_1_part_1 = outgoing_1.notebook.lines.add()
            field_1_1_part_1.amount.CopyFrom(response_0.customer_segment.discount.amount)
            outgoing_1.notebook.audit.created_by = response_0.customer_segment.audit.created_by
            merged_1 = datahub_v1_notebook_approval_service_pb2.RecallNotebookRequest()
            merged_1.MergeFrom(outgoing_1)
            outgoing_1.CopyFrom(merged_1)
            response_1 = await deps.clients.datahub_notebook_approval.RecallNotebook(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = datahub_v1_workspace_workflow_service_pb2.StartWorkspaceWorkflowRequest(
                context=request.context,
                workspace=datahub_v1_datahub_pb2.Workspace(
                    audit=common_v1_audit_pb2.AuditInfo(etag=response_1.notebook.audit.etag)
                )
            )
            envelope_2 = AnyMessage()
            envelope_2.Pack(outgoing_2)
            outgoing_2 = datahub_v1_workspace_workflow_service_pb2.StartWorkspaceWorkflowRequest()
            if not envelope_2.Unpack(outgoing_2):
                raise ValueError("partner envelope contains the wrong request type")
            response_2 = await deps.clients.datahub_workspace_workflow.StartWorkspaceWorkflow(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            outgoing_3 = datahub_v1_notebook_workflow_service_pb2.SignalNotebookWorkflowRequest()
            outgoing_3.context.CopyFrom(request.context)
            outgoing_3.notebook.audit.etag = response_0.customer_segment.audit.etag
            if response_1.notebook.WhichOneof('settlement') == 'bank':
                outgoing_3.notebook.bank.iban = response_1.notebook.bank.iban
            outgoing_3.notebook.counterparty.display_name = response_2.workspace.assignee.display_name
            response_3 = await deps.clients.datahub_notebook_workflow.SignalNotebookWorkflow(
                outgoing_3,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.result.message = returned_0_0
            returned_0_1 = response_0.result.status
            if returned_0_1:
                response.result.status = returned_0_1
            returned_1_0 = response_1.result.correlation_id
            if returned_1_0:
                response.result.correlation_id = returned_1_0
            returned_2_0 = response_2.result.reference_ids
            response.result.reference_ids.extend(returned_2_0)
            returned_2_1 = response_2.outcome.status
            if returned_2_1:
                response.result.status = returned_2_1
            returned_3_0 = response_3.result.correlation_id
            if returned_3_0:
                response.result.correlation_id = returned_3_0
            returned_3_1 = response_3.result.reference_ids
            response.result.reference_ids.extend(returned_3_1)
            return response

    async def handle_get_workspace(
        self,
        request: datahub_v1_workspace_service_pb2.GetWorkspaceRequest
    ) -> datahub_v1_workspace_service_pb2.GetWorkspaceResponse:
        """Returns a workspace."""
        deps = self.deps
        response = datahub_v1_workspace_service_pb2.GetWorkspaceResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('GetWorkspace', extra={'fields': {'domain': 'datahub'}})
            await deps.repository.audit(request.context.tenant_id, 'GetWorkspace', {})
            response_0 = datahub_v1_data_share_approval_service_pb2.EscalateDataShareResponse()
            outgoing_0 = datahub_v1_data_share_approval_service_pb2.EscalateDataShareRequest(
                context=request.context,
                details=datahub_v1_data_share_approval_service_pb2.EscalateDataShareRequest.Details(
                    approver=identity_v1_refs_pb2.UserRef(user_id=request.context.actor.user_id)
                )
            )
            response_0 = await deps.clients.datahub_data_share_approval.EscalateDataShare(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.data_share.audit.created_by
            if returned_0_0:
                response.workspace.audit.created_by = returned_0_0
            echoed_0 = request.workspace_id
            response.workspace.workspace_id = echoed_0
            return response

    async def handle_list_workspaces(
        self,
        request: datahub_v1_workspace_service_pb2.ListWorkspacesRequest
    ) -> datahub_v1_workspace_service_pb2.ListWorkspacesResponse:
        """Lists workspaces a page at a time."""
        deps = self.deps
        response = datahub_v1_workspace_service_pb2.ListWorkspacesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ListWorkspaces', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(request.context.tenant_id, 'ListWorkspaces', {'order_by': request.order_by})
            response_0 = lineage_v1_lineage_node_workflow_service_pb2.PauseLineageNodeWorkflowResponse()
            outgoing_0 = lineage_v1_lineage_node_workflow_service_pb2.PauseLineageNodeWorkflowRequest(
                context=request.context,
                lineage_node=lineage_v1_lineage_pb2.LineageNode(
                    children=[
                        lineage_v1_lineage_pb2.LineageNode(
                            children=[
                                lineage_v1_lineage_pb2.LineageNode(
                                    location=common_v1_address_pb2.PostalAddress(region=request.filter.region)
                                )
                            ]
                        )
                    ],
                    manager=identity_v1_refs_pb2.UserRef(user_id=request.context.actor.user_id)
                )
            )
            response_0 = await deps.clients.lineage_lineage_node_workflow.PauseLineageNodeWorkflow(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.correlation_id
            if returned_0_0:
                response.result.correlation_id = returned_0_0
            returned_0_1 = response_0.outcome.status
            if returned_0_1:
                response.result.status = returned_0_1
            return response

    async def handle_search_workspaces(
        self,
        request: datahub_v1_workspace_service_pb2.SearchWorkspacesRequest
    ) -> datahub_v1_workspace_service_pb2.SearchWorkspacesResponse:
        """Lists workspaces a page at a time."""
        deps = self.deps
        response = datahub_v1_workspace_service_pb2.SearchWorkspacesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SearchWorkspaces', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(request.context.tenant_id, 'SearchWorkspaces', {'order_by': request.order_by})
            response_0 = labeling_v1_label_set_approval_service_pb2.DelegateLabelSetApprovalResponse()
            response_1 = customers_v1_customer_workflow_service_pb2.ListCustomerWorkflowsResponse()
            outgoing_0 = labeling_v1_label_set_approval_service_pb2.DelegateLabelSetApprovalRequest(
                context=request.context,
                label_set=labeling_v1_labeling_pb2.LabelSet(
                    children=[
                        labeling_v1_labeling_pb2.LabelSet(
                            children=[
                                labeling_v1_labeling_pb2.LabelSet(
                                    location=common_v1_address_pb2.PostalAddress(region=request.filter.region)
                                )
                            ]
                        )
                    ]
                )
            )
            response_0 = await deps.clients.labeling_label_set_approval.DelegateLabelSetApproval(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = customers_v1_customer_workflow_service_pb2.ListCustomerWorkflowsRequest(
                context=request.context,
                filter=customers_v1_customer_workflow_service_pb2.ListCustomerWorkflowsRequest.Filter(
                    created_after=request.filter.created_after,
                    labels=dict(request.filter.labels),
                    owner_id=request.filter.owner_id
                )
            )
            response_1 = await hooks.workspace_search_workspaces1(
                deps.clients.customers_customer_workflow,
                outgoing_1,
                deps.settings.timeout
            )
            returned_0_0 = response_0.label_set.audit.created_at
            returned_0_0_part_0 = response.workspaces.add()
            if returned_0_0.ListFields():
                returned_0_0_part_0.audit.created_at.MergeFrom(returned_0_0)
            returned_0_1 = response_0.label_set.audit.created_by
            returned_0_1_part_0 = response.workspaces.add()
            if returned_0_1:
                returned_0_1_part_0.audit.created_by = returned_0_1
            returned_1_0 = response_1.result.status
            if returned_1_0:
                response.result.status = returned_1_0
            returned_1_1 = response_1.result.message
            if returned_1_1:
                response.result.message = returned_1_1
            return response

    async def handle_update_workspace(
        self,
        request: datahub_v1_workspace_service_pb2.UpdateWorkspaceRequest
    ) -> datahub_v1_workspace_service_pb2.UpdateWorkspaceResponse:
        """Changes a workspace."""
        deps = self.deps
        response = datahub_v1_workspace_service_pb2.UpdateWorkspaceResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('UpdateWorkspace', extra={'fields': {'allow_missing': request.allow_missing}})
            await deps.repository.audit(
                request.context.tenant_id,
                'UpdateWorkspace',
                {'allow_missing': request.allow_missing}
            )
            await deps.repository.save_workspace(request.context.tenant_id, request.workspace)
            response_0 = datahub_v1_data_share_validation_service_pb2.PreviewDataShareResponse()
            response_1 = featurestore_v1_feature_value_reporting_service_pb2.GenerateFeatureValueReportResponse()
            response_2 = labeling_v1_annotation_approval_service_pb2.EscalateAnnotationResponse()
            outgoing_0 = datahub_v1_data_share_validation_service_pb2.PreviewDataShareRequest()
            outgoing_0.context.CopyFrom(request.context)
            outgoing_0.data_share.audit.created_at.CopyFrom(request.workspace.audit.created_at)
            outgoing_0.context.tenant_id = tenant_id.get()
            response_0 = await deps.clients.datahub_data_share_validation.PreviewDataShare(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = featurestore_v1_feature_value_reporting_service_pb2.GenerateFeatureValueReportRequest(
                annotations=dict(request.workspace.custom_fields),
                context=request.context,
                details=featurestore_v1_feature_value_reporting_service_pb2.GenerateFeatureValueReportRequest.Details(
                    filters=dict(response_0.data_share.metadata)
                )
            )
            port_1: WorkspaceUpdateWorkspace1Port = WorkspaceUpdateWorkspace1Adapter(
                deps.clients.featurestore_feature_value_reporting,
                deps.settings.timeout
            )
            response_1 = await port_1.execute(outgoing_1)
            requests_2: list[labeling_v1_annotation_approval_service_pb2.EscalateAnnotationRequest] = []
            for item_2 in request.workspace.history:
                outgoing_2 = labeling_v1_annotation_approval_service_pb2.EscalateAnnotationRequest(
                    annotation=labeling_v1_labeling_pb2.Annotation(
                        subject=labeling_v1_refs_pb2.LabelingTaskRef(
                            display_name=response_0.data_share.counterparty.display_name,
                            priority=request.workspace.priority
                        )
                    ),
                    context=request.context,
                    details=labeling_v1_annotation_approval_service_pb2.EscalateAnnotationRequest.Details(
                        approver=identity_v1_refs_pb2.UserRef(email=request.workspace.customer.email),
                        effective_at=item_2.changed_at
                    )
                )
                requests_2.append(outgoing_2)
            replies_2 = await asyncio.gather(*(
                deps.clients.labeling_annotation_approval.EscalateAnnotation(
                    entry,
                    timeout=deps.settings.timeout
                ) for entry in requests_2
            ))
            if replies_2:
                response_2 = replies_2[-1]
            returned_0_0 = response_0.result.details
            response.result.details.update(returned_0_0)
            returned_0_1 = response_0.data_share.audit.created_by
            if returned_0_1:
                response.workspace.audit.created_by = returned_0_1
            returned_1_0 = response_1.result.reference_ids
            response.result.reference_ids.extend(returned_1_0)
            returned_1_1 = response_1.result.message
            if returned_1_1:
                response.result.message = returned_1_1
            echoed_0 = request.workspace.workspace_id
            response.workspace.workspace_id = echoed_0
            echoed_1 = request.workspace.custom_fields
            response.workspace.custom_fields.update(echoed_1)
            return response

    async def handle_watch_workspaces(
        self,
        request: datahub_v1_workspace_service_pb2.WatchWorkspacesRequest
    ) -> datahub_v1_workspace_service_pb2.WatchWorkspacesResponse:
        """Streams the changes of workspaces as they happen."""
        deps = self.deps
        response = datahub_v1_workspace_service_pb2.WatchWorkspacesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('WatchWorkspaces', extra={'fields': {'max_events': request.max_events}})
            await deps.repository.audit(
                request.context.tenant_id,
                'WatchWorkspaces',
                {'max_events': request.max_events}
            )
            response_0 = datahub_v1_workspace_integration_service_pb2.AcknowledgeWorkspaceEventResponse()
            response_1 = datahub_v1_data_share_validation_service_pb2.ScoreDataShareResponse()
            outgoing_0 = datahub_v1_workspace_integration_service_pb2.AcknowledgeWorkspaceEventRequest(
                context=request.context,
                details=datahub_v1_workspace_integration_service_pb2.AcknowledgeWorkspaceEventRequest.Details(
                    received_at=request.since
                )
            )
            response_0 = await WorkspaceWatchWorkspaces0Adapter(
                deps.clients.datahub_workspace_integration,
                deps.settings.timeout
            )(outgoing_0)
            outgoing_1 = datahub_v1_data_share_validation_service_pb2.ScoreDataShareRequest()
            outgoing_1.context.CopyFrom(request.context)
            if response_0.workspace.WhichOneof('origin') == 'customer':
                outgoing_1.data_share.counterparty.display_name = response_0.workspace.customer.display_name
            outgoing_1.data_share.audit.updated_by = response_0.workspace.audit.updated_by
            response_1 = await deps.clients.datahub_data_share_validation.ScoreDataShare(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.details
            response.result.details.update(returned_0_0)
            returned_1_0 = response_1.data_share.audit.updated_by
            if returned_1_0:
                response.workspace.audit.updated_by = returned_1_0
            echoed_0 = request.subscriber.phone
            response.workspace.requester.phone = echoed_0
            echoed_1 = request.subscriber.email
            response.workspace.requester.email = echoed_1
            return response
