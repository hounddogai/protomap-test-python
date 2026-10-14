"""Reusable transport mixin for NotebookWorkflowService."""

from __future__ import annotations

from collections.abc import AsyncIterator
from collections.abc import Awaitable
from collections.abc import Callable
from functools import partial
from typing import Any
from typing import cast
import asyncio
import logging

from google.protobuf.any_pb2 import Any as AnyMessage
from google.protobuf.json_format import MessageToDict
from google.protobuf.json_format import ParseDict
import grpc

from acme.analytics.v1 import analytics_event_approval_service_pb2 as analytics_v1_analytics_event_approval_service_pb2
from acme.analytics.v1 import (
    analytics_event_approval_service_pb2_grpc as analytics_v1_analytics_event_approval_service_pb2_grpc,
)
from acme.anomalies.v1 import anomalies_pb2 as anomalies_v1_anomalies_pb2
from acme.anomalies.v1 import anomaly_workflow_service_pb2 as anomalies_v1_anomaly_workflow_service_pb2
from acme.billing.v1 import billing_account_query_service_pb2 as billing_v1_billing_account_query_service_pb2
from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.customers.v1 import customer_segment_import_service_pb2 as customers_v1_customer_segment_import_service_pb2
from acme.customers.v1 import customers_pb2 as customers_v1_customers_pb2
from acme.customers.v1 import refs_pb2 as customers_v1_refs_pb2
from acme.datahub.v1 import data_share_approval_service_pb2 as datahub_v1_data_share_approval_service_pb2
from acme.datahub.v1 import data_share_reporting_service_pb2 as datahub_v1_data_share_reporting_service_pb2
from acme.datahub.v1 import data_share_validation_service_pb2 as datahub_v1_data_share_validation_service_pb2
from acme.datahub.v1 import datahub_pb2 as datahub_v1_datahub_pb2
from acme.datahub.v1 import notebook_reporting_service_pb2 as datahub_v1_notebook_reporting_service_pb2
from acme.datahub.v1 import notebook_workflow_service_pb2 as datahub_v1_notebook_workflow_service_pb2
from acme.datahub.v1 import workspace_reporting_service_pb2 as datahub_v1_workspace_reporting_service_pb2
from acme.datahub.v1 import workspace_workflow_service_pb2 as datahub_v1_workspace_workflow_service_pb2
from acme.documents.v1 import document_query_service_pb2 as documents_v1_document_query_service_pb2
from acme.documents.v1 import document_service_pb2 as documents_v1_document_service_pb2
from acme.documents.v1 import document_validation_service_pb2 as documents_v1_document_validation_service_pb2
from acme.fanportal.v1 import fan_session_service_pb2 as fanportal_v1_fan_session_service_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.identity.v1 import user_query_service_pb2 as identity_v1_user_query_service_pb2
from acme.labeling.v1 import label_set_approval_service_pb2 as labeling_v1_label_set_approval_service_pb2
from acme.labeling.v1 import labeling_pb2 as labeling_v1_labeling_pb2
from acme.pipelines.v1 import pipeline_step_export_service_pb2 as pipelines_v1_pipeline_step_export_service_pb2
from acme.pipelines.v1 import pipelines_pb2 as pipelines_v1_pipelines_pb2

from acme_data.domains.datahub import hooks
from acme_data.domains.datahub.adapters import NotebookWorkflowResumeNotebookWorkflow1Adapter
from acme_data.domains.datahub.adapters import NotebookWorkflowResumeNotebookWorkflow1Port
from acme_data.domains.datahub.adapters import NotebookWorkflowResumeNotebookWorkflow3Adapter
from acme_data.domains.datahub.dependencies import Dependencies
from acme_data.domains.datahub.models import NotebookWorkflowPauseNotebookWorkflow0Command
from acme_data.domains.datahub.models import NotebookWorkflowPauseNotebookWorkflow1Command
from acme_data.domains.datahub.models import NotebookWorkflowStartNotebookWorkflow2Command
from acme_data.domains.datahub.models import to_notebook_workflow_pause_notebook_workflow0_command
from acme_data.domains.datahub.models import to_notebook_workflow_pause_notebook_workflow1_command
from acme_data.domains.datahub.models import to_notebook_workflow_start_notebook_workflow2_command
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_id
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class NotebookWorkflowServicerHandlers:
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    async def AdvanceNotebookWorkflow(
        self, request: datahub_v1_notebook_workflow_service_pb2.AdvanceNotebookWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_notebook_workflow_service_pb2.AdvanceNotebookWorkflowResponse:
        """Advances a notebook."""
        return await self.handle_advance_notebook_workflow(request)

    @rpc_errors
    async def CancelNotebookWorkflow(
        self, request: datahub_v1_notebook_workflow_service_pb2.CancelNotebookWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_notebook_workflow_service_pb2.CancelNotebookWorkflowResponse:
        """Cancels a notebook."""
        return await self.handle_cancel_notebook_workflow(request)

    @rpc_errors
    @retry_transient
    async def ListNotebookWorkflows(
        self, request: datahub_v1_notebook_workflow_service_pb2.ListNotebookWorkflowsRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_notebook_workflow_service_pb2.ListNotebookWorkflowsResponse:
        """Lists notebooks a page at a time."""
        return await self.handle_list_notebook_workflows(request)

    @rpc_errors
    async def PauseNotebookWorkflow(
        self, request: datahub_v1_notebook_workflow_service_pb2.PauseNotebookWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_notebook_workflow_service_pb2.PauseNotebookWorkflowResponse:
        """Pauses a notebook."""
        return await self.handle_pause_notebook_workflow(request)

    @rpc_errors
    async def ResumeNotebookWorkflow(
        self, request: datahub_v1_notebook_workflow_service_pb2.ResumeNotebookWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_notebook_workflow_service_pb2.ResumeNotebookWorkflowResponse:
        """Resumes a notebook."""
        return await self.handle_resume_notebook_workflow(request)

    @rpc_errors
    async def RetryNotebookWorkflow(
        self, request: datahub_v1_notebook_workflow_service_pb2.RetryNotebookWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_notebook_workflow_service_pb2.RetryNotebookWorkflowResponse:
        """Retrys a notebook."""
        return await self.handle_retry_notebook_workflow(request)

    @rpc_errors
    async def SignalNotebookWorkflow(
        self, request: datahub_v1_notebook_workflow_service_pb2.SignalNotebookWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_notebook_workflow_service_pb2.SignalNotebookWorkflowResponse:
        """Signals a notebook."""
        return await self.handle_signal_notebook_workflow(request)

    @rpc_errors
    async def StartNotebookWorkflow(
        self, request: datahub_v1_notebook_workflow_service_pb2.StartNotebookWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_notebook_workflow_service_pb2.StartNotebookWorkflowResponse:
        """Starts a notebook."""
        return await self.handle_start_notebook_workflow(request)

    async def handle_advance_notebook_workflow(
        self,
        request: datahub_v1_notebook_workflow_service_pb2.AdvanceNotebookWorkflowRequest
    ) -> datahub_v1_notebook_workflow_service_pb2.AdvanceNotebookWorkflowResponse:
        """Advances a notebook."""
        deps = self.deps
        response = datahub_v1_notebook_workflow_service_pb2.AdvanceNotebookWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('AdvanceNotebookWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'AdvanceNotebookWorkflow',
                {'reason': request.reason}
            )
            await deps.repository.save_notebook(request.context.tenant_id, request.notebook)
            response_0 = datahub_v1_workspace_reporting_service_pb2.ListWorkspaceReportsResponse()
            response_1 = datahub_v1_data_share_approval_service_pb2.EscalateDataShareResponse()
            response_2 = labeling_v1_label_set_approval_service_pb2.EscalateLabelSetResponse()
            outgoing_0 = datahub_v1_workspace_reporting_service_pb2.ListWorkspaceReportsRequest(
                context=request.context,
                filter=datahub_v1_workspace_reporting_service_pb2.ListWorkspaceReportsRequest.Filter(
                    region=request.notebook.billing_address.region
                )
            )
            method_name_0 = 'ListWorkspaceReports'
            response_0 = await getattr(
                deps.clients.datahub_workspace_reporting,
                method_name_0
            )(outgoing_0, timeout=deps.settings.timeout)
            requests_1: list[datahub_v1_data_share_approval_service_pb2.EscalateDataShareRequest] = []
            for item_1 in request.notebook.attachments:
                outgoing_1 = datahub_v1_data_share_approval_service_pb2.EscalateDataShareRequest(
                    context=request.context,
                    data_share=datahub_v1_datahub_pb2.DataShare(
                        attachments=[
                            datahub_v1_datahub_pb2.DataShareAttachment(
                                content_type=item_1.content_type,
                                size_bytes=item_1.size_bytes,
                                uri=item_1.uri
                            )
                        ]
                    )
                )
                requests_1.append(outgoing_1)
            replies_1 = await asyncio.gather(*(
                deps.clients.datahub_data_share_approval.EscalateDataShare(
                    entry,
                    timeout=deps.settings.timeout
                ) for entry in requests_1
            ))
            if replies_1:
                response_1 = replies_1[-1]
            outgoing_2 = labeling_v1_label_set_approval_service_pb2.EscalateLabelSetRequest(
                context=request.context,
                label_set=labeling_v1_labeling_pb2.LabelSet(
                    children=[
                        labeling_v1_labeling_pb2.LabelSet(
                            children=[
                                labeling_v1_labeling_pb2.LabelSet(
                                    location=common_v1_address_pb2.PostalAddress(
                                        lines=list(request.notebook.billing_address.lines),
                                        locality=request.notebook.billing_address.locality,
                                        postal_code=request.notebook.billing_address.postal_code
                                    )
                                )
                            ]
                        )
                    ]
                )
            )
            document_2 = MessageToDict(outgoing_2, preserving_proto_field_name=True)
            outgoing_2 = ParseDict(document_2, labeling_v1_label_set_approval_service_pb2.EscalateLabelSetRequest())
            response_2 = await deps.clients.labeling_label_set_approval.EscalateLabelSet(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.status
            if returned_0_0:
                response.result.status = returned_0_0
            returned_2_0 = response_2.label_set.manager.display_name
            if returned_2_0:
                response.notebook.counterparty.display_name = returned_2_0
            returned_2_1 = response_2.outcome.next_steps
            response.outcome.next_steps.extend(returned_2_1)
            echoed_0 = request.notebook_id
            response.notebook.notebook_id = echoed_0
            echoed_1 = request.notebook.metadata
            response.notebook.metadata.update(echoed_1)
            return response

    async def handle_cancel_notebook_workflow(
        self,
        request: datahub_v1_notebook_workflow_service_pb2.CancelNotebookWorkflowRequest
    ) -> datahub_v1_notebook_workflow_service_pb2.CancelNotebookWorkflowResponse:
        """Cancels a notebook."""
        deps = self.deps
        response = datahub_v1_notebook_workflow_service_pb2.CancelNotebookWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CancelNotebookWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'CancelNotebookWorkflow', {'reason': request.reason})
            await deps.repository.save_notebook(request.context.tenant_id, request.notebook)
            response_0 = datahub_v1_data_share_reporting_service_pb2.StreamDataShareMetricsResponse()
            response_1 = labeling_v1_label_set_approval_service_pb2.RejectLabelSetResponse()
            response_2 = pipelines_v1_pipeline_step_export_service_pb2.ListPipelineStepExportsResponse()
            outgoing_0 = datahub_v1_data_share_reporting_service_pb2.StreamDataShareMetricsRequest(
                context=request.context,
                subscriber=common_v1_contact_pb2.ContactInfo(
                    email=request.details.notify.email,
                    name=request.details.notify.name,
                    phone=request.details.notify.phone,
                    preferred_channel=request.details.notify.preferred_channel
                )
            )
            async for chunk_0 in deps.clients.datahub_data_share_reporting.StreamDataShareMetrics(
                outgoing_0,
                timeout=deps.settings.timeout
            ):
                response_0 = chunk_0
            outgoing_1 = labeling_v1_label_set_approval_service_pb2.RejectLabelSetRequest()
            outgoing_1.context.CopyFrom(request.context)
            field_1_1_part_1 = outgoing_1.label_set.children.add()
            field_1_1_part_2 = field_1_1_part_1.children.add()
            field_1_1_part_2.location.locality = request.notebook.billing_address.locality
            field_1_2_part_1 = outgoing_1.label_set.children.add()
            field_1_2_part_2 = field_1_2_part_1.children.add()
            field_1_2_part_2.location.postal_code = request.notebook.billing_address.postal_code
            merged_1 = labeling_v1_label_set_approval_service_pb2.RejectLabelSetRequest()
            merged_1.MergeFrom(outgoing_1)
            outgoing_1.CopyFrom(merged_1)
            response_1 = await deps.clients.labeling_label_set_approval.RejectLabelSet(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = pipelines_v1_pipeline_step_export_service_pb2.ListPipelineStepExportsRequest(
                context=request.context,
                filter=pipelines_v1_pipeline_step_export_service_pb2.ListPipelineStepExportsRequest.Filter(
                    created_after=request.notebook.audit.updated_at,
                    region=response_1.label_set.location.region
                )
            )
            envelope_2 = AnyMessage()
            envelope_2.Pack(outgoing_2)
            outgoing_2 = pipelines_v1_pipeline_step_export_service_pb2.ListPipelineStepExportsRequest()
            if not envelope_2.Unpack(outgoing_2):
                raise ValueError("partner envelope contains the wrong request type")
            response_2 = await deps.clients.pipelines_pipeline_step_export.ListPipelineStepExports(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            returned_1_0 = response_1.label_set.attributes
            returned_1_0_part_1 = response.notebook.lines.add()
            returned_1_0_part_1.attributes.update(returned_1_0)
            returned_1_1 = response_1.outcome.message
            if returned_1_1:
                response.outcome.message = returned_1_1
            returned_2_0 = response_2.result.correlation_id
            if returned_2_0:
                response.result.correlation_id = returned_2_0
            returned_2_1 = response_2.result.message
            if returned_2_1:
                response.outcome.message = returned_2_1
            echoed_0 = request.notebook_id
            response.notebook.notebook_id = echoed_0
            echoed_1 = request.notebook.billing_address
            response.notebook.billing_address.CopyFrom(echoed_1)
            return response

    async def handle_list_notebook_workflows(
        self,
        request: datahub_v1_notebook_workflow_service_pb2.ListNotebookWorkflowsRequest
    ) -> datahub_v1_notebook_workflow_service_pb2.ListNotebookWorkflowsResponse:
        """Lists notebooks a page at a time."""
        deps = self.deps
        response = datahub_v1_notebook_workflow_service_pb2.ListNotebookWorkflowsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ListNotebookWorkflows', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ListNotebookWorkflows',
                {'order_by': request.order_by}
            )
            response_0 = datahub_v1_data_share_validation_service_pb2.PreviewDataShareResponse()
            outgoing_0 = datahub_v1_data_share_validation_service_pb2.PreviewDataShareRequest(
                context=request.context,
                data_share=datahub_v1_datahub_pb2.DataShare(
                    billing_address=common_v1_address_pb2.PostalAddress(region=request.filter.region)
                )
            )
            response_0 = await deps.clients.datahub_data_share_validation.PreviewDataShare(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.data_share.number
            returned_0_0_part_0 = response.notebooks.add()
            if returned_0_0:
                returned_0_0_part_0.number = returned_0_0
            returned_0_1 = response_0.data_share.billing_address.country_code
            returned_0_1_part_0 = response.notebooks.add()
            if returned_0_1:
                returned_0_1_part_0.billing_address.country_code = returned_0_1
            return response

    async def handle_pause_notebook_workflow(
        self,
        request: datahub_v1_notebook_workflow_service_pb2.PauseNotebookWorkflowRequest
    ) -> datahub_v1_notebook_workflow_service_pb2.PauseNotebookWorkflowResponse:
        """Pauses a notebook."""
        deps = self.deps
        response = datahub_v1_notebook_workflow_service_pb2.PauseNotebookWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('PauseNotebookWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'PauseNotebookWorkflow', {'reason': request.reason})
            await deps.repository.save_notebook(request.context.tenant_id, request.notebook)
            response_0 = identity_v1_user_query_service_pb2.CountUsersResponse()
            response_1 = billing_v1_billing_account_query_service_pb2.ResolveBillingAccountsResponse()
            response_2 = datahub_v1_data_share_validation_service_pb2.NormalizeDataShareResponse()
            response_3 = documents_v1_document_service_pb2.ListDocumentsResponse()
            command_0 = NotebookWorkflowPauseNotebookWorkflow0Command(
                context=request.context,
                filter_region=request.notebook.billing_address.region,
                filter_created_after=request.notebook.audit.created_at
            )
            outgoing_0 = to_notebook_workflow_pause_notebook_workflow0_command(command_0)
            response_0 = await deps.clients.identity_user_query.CountUsers(outgoing_0, timeout=deps.settings.timeout)
            command_1 = NotebookWorkflowPauseNotebookWorkflow1Command.model_validate({'context': request.context})
            outgoing_1 = to_notebook_workflow_pause_notebook_workflow1_command(command_1)
            response_1 = await deps.clients.billing_billing_account_query.ResolveBillingAccounts(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = datahub_v1_data_share_validation_service_pb2.NormalizeDataShareRequest(
                context=request.context,
                data_share=datahub_v1_datahub_pb2.DataShare(
                    billing_address=common_v1_address_pb2.PostalAddress(
                        lines=list(request.notebook.billing_address.lines),
                        locality=request.notebook.billing_address.locality
                    ),
                    card=datahub_v1_datahub_pb2.DataShareCardSettlement(
                        last4=request.notebook.card.last4,
                        network=request.notebook.card.network
                    )
                )
            )
            send_2 = partial(
                deps.clients.datahub_data_share_validation.NormalizeDataShare,
                timeout=deps.settings.timeout
            )
            response_2 = await send_2(outgoing_2)
            outgoing_3 = documents_v1_document_service_pb2.ListDocumentsRequest(
                context=request.context,
                filter=documents_v1_document_service_pb2.ListDocumentsRequest.Filter(
                    created_after=request.notebook.audit.updated_at,
                    region=response_2.data_share.billing_address.region
                )
            )
            response_3 = await hooks.notebook_workflow_pause_notebook_workflow3(
                deps.clients.documents_document,
                outgoing_3,
                deps.settings.timeout
            )
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.outcome.message = returned_0_0
            returned_0_1 = response_0.result.message
            if returned_0_1:
                response.result.message = returned_0_1
            returned_1_0 = response_1.result.details
            response.result.details.update(returned_1_0)
            returned_2_0 = response_2.data_share.audit.updated_at
            if returned_2_0.ListFields():
                response.notebook.audit.updated_at.MergeFrom(returned_2_0)
            returned_2_1 = response_2.result.message
            if returned_2_1:
                response.result.message = returned_2_1
            returned_3_0 = response_3.result.message
            if returned_3_0:
                response.result.message = returned_3_0
            echoed_0 = request.notebook_id
            response.notebook.notebook_id = echoed_0
            echoed_1 = request.notebook.metadata
            response.notebook.metadata.update(echoed_1)
            return response

    async def handle_resume_notebook_workflow(
        self,
        request: datahub_v1_notebook_workflow_service_pb2.ResumeNotebookWorkflowRequest
    ) -> datahub_v1_notebook_workflow_service_pb2.ResumeNotebookWorkflowResponse:
        """Resumes a notebook."""
        deps = self.deps
        response = datahub_v1_notebook_workflow_service_pb2.ResumeNotebookWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ResumeNotebookWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'ResumeNotebookWorkflow', {'reason': request.reason})
            await deps.repository.save_notebook(request.context.tenant_id, request.notebook)
            response_0 = datahub_v1_workspace_reporting_service_pb2.CountWorkspaceTotalsResponse()
            response_1 = anomalies_v1_anomaly_workflow_service_pb2.StartAnomalyWorkflowResponse()
            response_2 = fanportal_v1_fan_session_service_pb2.WatchFanSessionsResponse()
            response_3 = datahub_v1_workspace_workflow_service_pb2.CancelWorkspaceWorkflowResponse()
            outgoing_0 = datahub_v1_workspace_reporting_service_pb2.CountWorkspaceTotalsRequest()
            outgoing_0.context.CopyFrom(request.context)
            outgoing_0.filter.region = request.notebook.billing_address.region
            outgoing_0.filter.created_after.CopyFrom(request.notebook.audit.created_at)
            outgoing_0.context.tenant_id = tenant_id.get()
            response_0 = await deps.clients.datahub_workspace_reporting.CountWorkspaceTotals(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = anomalies_v1_anomaly_workflow_service_pb2.StartAnomalyWorkflowRequest(
                anomaly=anomalies_v1_anomalies_pb2.Anomaly(
                    assignee=identity_v1_refs_pb2.UserRef(email=request.details.notify.email)
                ),
                context=request.context,
                details=anomalies_v1_anomaly_workflow_service_pb2.StartAnomalyWorkflowRequest.Details(
                    notify=common_v1_contact_pb2.ContactInfo(
                        name=request.details.notify.name,
                        phone=request.details.notify.phone
                    )
                )
            )
            port_1: NotebookWorkflowResumeNotebookWorkflow1Port = NotebookWorkflowResumeNotebookWorkflow1Adapter(
                deps.clients.anomalies_anomaly_workflow,
                deps.settings.timeout
            )
            response_1 = await port_1.execute(outgoing_1)
            outgoing_2 = fanportal_v1_fan_session_service_pb2.WatchFanSessionsRequest(
                context=request.context,
                subscriber=common_v1_contact_pb2.ContactInfo(
                    email=request.details.notify.email,
                    phone=response_1.anomaly.requester.phone,
                    preferred_channel=response_1.anomaly.requester.preferred_channel
                )
            )
            async for chunk_2 in deps.clients.fanportal_fan_session.WatchFanSessions(
                outgoing_2,
                timeout=deps.settings.timeout
            ):
                response_2 = chunk_2
            outgoing_3 = datahub_v1_workspace_workflow_service_pb2.CancelWorkspaceWorkflowRequest(
                context=request.context,
                details=datahub_v1_workspace_workflow_service_pb2.CancelWorkspaceWorkflowRequest.Details(
                    notify=common_v1_contact_pb2.ContactInfo(name=request.details.notify.name)
                )
            )
            response_3 = await NotebookWorkflowResumeNotebookWorkflow3Adapter(
                deps.clients.datahub_workspace_workflow,
                deps.settings.timeout
            )(outgoing_3)
            returned_0_0 = response_0.result.status
            if returned_0_0:
                response.outcome.status = returned_0_0
            returned_1_0 = response_1.anomaly.audit.created_by
            if returned_1_0:
                response.notebook.audit.created_by = returned_1_0
            returned_1_1 = response_1.outcome.next_steps
            response.outcome.next_steps.extend(returned_1_1)
            returned_3_0 = response_3.outcome.message
            if returned_3_0:
                response.result.message = returned_3_0
            returned_3_1 = response_3.result.details
            response.result.details.update(returned_3_1)
            echoed_0 = request.notebook_id
            response.notebook.notebook_id = echoed_0
            echoed_1 = request.notebook.number
            response.notebook.number = echoed_1
            return response

    async def handle_retry_notebook_workflow(
        self,
        request: datahub_v1_notebook_workflow_service_pb2.RetryNotebookWorkflowRequest
    ) -> datahub_v1_notebook_workflow_service_pb2.RetryNotebookWorkflowResponse:
        """Retrys a notebook."""
        deps = self.deps
        response = datahub_v1_notebook_workflow_service_pb2.RetryNotebookWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('RetryNotebookWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'RetryNotebookWorkflow', {'reason': request.reason})
            await deps.repository.save_notebook(request.context.tenant_id, request.notebook)
            response_0 = customers_v1_customer_segment_import_service_pb2.RetryCustomerSegmentImportResponse()
            response_1 = documents_v1_document_validation_service_pb2.ValidateDocumentResponse()
            response_2 = datahub_v1_data_share_reporting_service_pb2.GenerateDataShareReportResponse()
            outgoing_0 = customers_v1_customer_segment_import_service_pb2.RetryCustomerSegmentImportRequest(
                context=request.context,
                customer_segment=customers_v1_customers_pb2.CustomerSegment(
                    audit=common_v1_audit_pb2.AuditInfo(
                        created_by=request.notebook.audit.created_by,
                        etag=request.notebook.audit.etag
                    ),
                    priority=request.notebook.counterparty.priority
                )
            )
            response_0 = cast(customers_v1_customer_segment_import_service_pb2.RetryCustomerSegmentImportResponse, await deps.bus.request(
                'acme.datahub.v1.NotebookWorkflowService/RetryNotebookWorkflow/0', outgoing_0, deps.settings.timeout,
            ))
            outgoing_1 = documents_v1_document_validation_service_pb2.ValidateDocumentRequest()
            outgoing_1.context.CopyFrom(request.context)
            if response_0.customer_segment.WhichOneof('action') == 'discount':
                field_1_1_part_1 = outgoing_1.document.lines.add()
                field_1_1_part_1.tax.amount.CopyFrom(response_0.customer_segment.discount.amount)
            response_1 = await deps.clients.documents_document_validation.ValidateDocument(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = datahub_v1_data_share_reporting_service_pb2.GenerateDataShareReportRequest(
                annotations=dict(request.annotations),
                context=request.context,
                details=datahub_v1_data_share_reporting_service_pb2.GenerateDataShareReportRequest.Details(
                    filters=dict(response_1.document.metadata),
                    period=response_0.customer_segment.effective
                ),
                reason=response_0.customer_segment.block.reason
            )
            method_name_2 = 'GenerateDataShareReport'
            response_2 = await getattr(
                deps.clients.datahub_data_share_reporting,
                method_name_2
            )(outgoing_2, timeout=deps.settings.timeout)
            returned_0_0 = response_0.customer_segment.audit.created_by
            if returned_0_0:
                response.notebook.audit.created_by = returned_0_0
            returned_0_1 = response_0.customer_segment.discount.amount
            returned_0_1_part_1 = response.notebook.lines.add()
            if returned_0_1.ListFields():
                returned_0_1_part_1.tax.amount.MergeFrom(returned_0_1)
            returned_1_0 = response_1.document.billing_address.recipient
            if returned_1_0:
                response.notebook.billing_address.recipient = returned_1_0
            returned_1_1 = response_1.outcome.status
            if returned_1_1:
                response.outcome.status = returned_1_1
            returned_2_0 = response_2.result.correlation_id
            if returned_2_0:
                response.result.correlation_id = returned_2_0
            echoed_0 = request.notebook_id
            response.notebook.notebook_id = echoed_0
            echoed_1 = request.notebook.counterparty
            response.notebook.counterparty.CopyFrom(echoed_1)
            return response

    async def handle_signal_notebook_workflow(
        self,
        request: datahub_v1_notebook_workflow_service_pb2.SignalNotebookWorkflowRequest
    ) -> datahub_v1_notebook_workflow_service_pb2.SignalNotebookWorkflowResponse:
        """Signals a notebook."""
        deps = self.deps
        response = datahub_v1_notebook_workflow_service_pb2.SignalNotebookWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SignalNotebookWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'SignalNotebookWorkflow', {'reason': request.reason})
            await deps.repository.save_notebook(request.context.tenant_id, request.notebook)
            response_0 = documents_v1_document_query_service_pb2.BrowseDocumentsResponse()
            response_1 = datahub_v1_workspace_workflow_service_pb2.StartWorkspaceWorkflowResponse()
            response_2 = pipelines_v1_pipeline_step_export_service_pb2.RetryPipelineStepExportResponse()
            response_3 = documents_v1_document_service_pb2.ListDocumentsResponse()
            fields_0: dict[str, Any] = {
                'context': request.context,
                'filter': {'created_after': request.notebook.due_at, 'region': request.notebook.billing_address.region}
            }
            outgoing_0 = documents_v1_document_query_service_pb2.BrowseDocumentsRequest(**fields_0)
            response_0 = await deps.clients.documents_document_query.BrowseDocuments(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = datahub_v1_workspace_workflow_service_pb2.StartWorkspaceWorkflowRequest(
                context=request.context,
                workspace=datahub_v1_datahub_pb2.Workspace(
                    customer=customers_v1_refs_pb2.CustomerRef(email=request.details.notify.email),
                    requester=common_v1_contact_pb2.ContactInfo(phone=request.details.notify.phone)
                )
            )
            document_1 = MessageToDict(outgoing_1, preserving_proto_field_name=True)
            outgoing_1 = ParseDict(
                document_1,
                datahub_v1_workspace_workflow_service_pb2.StartWorkspaceWorkflowRequest()
            )
            response_1 = await deps.clients.datahub_workspace_workflow.StartWorkspaceWorkflow(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            callbacks_2: list[
                Callable[[], Awaitable[pipelines_v1_pipeline_step_export_service_pb2.RetryPipelineStepExportResponse]]
            ] = []
            for item_2 in request.notebook.lines:
                outgoing_2 = pipelines_v1_pipeline_step_export_service_pb2.RetryPipelineStepExportRequest(
                    context=request.context,
                    pipeline_step=pipelines_v1_pipelines_pb2.PipelineStep(
                        description=item_2.description,
                        discount=pipelines_v1_pipelines_pb2.PipelineStepDiscountAction(amount=item_2.tax.amount)
                    )
                )
                async def send_2(
                    payload: pipelines_v1_pipeline_step_export_service_pb2.RetryPipelineStepExportRequest = outgoing_2
                ) -> pipelines_v1_pipeline_step_export_service_pb2.RetryPipelineStepExportResponse:
                    return await deps.clients.pipelines_pipeline_step_export.RetryPipelineStepExport(
                        payload,
                        timeout=deps.settings.timeout
                    )
                callbacks_2.append(send_2)
            for callback_2 in callbacks_2:
                response_2 = await callback_2()
            outgoing_3 = documents_v1_document_service_pb2.ListDocumentsRequest()
            outgoing_3.context.CopyFrom(request.context)
            outgoing_3.filter.region = request.notebook.billing_address.region
            merged_3 = documents_v1_document_service_pb2.ListDocumentsRequest()
            merged_3.MergeFrom(outgoing_3)
            outgoing_3.CopyFrom(merged_3)
            response_3 = await deps.clients.documents_document.ListDocuments(outgoing_3, timeout=deps.settings.timeout)
            returned_0_0 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_0)
            returned_1_0 = response_1.workspace.audit.updated_by
            if returned_1_0:
                response.notebook.audit.updated_by = returned_1_0
            returned_1_1 = response_1.outcome.status
            if returned_1_1:
                response.outcome.status = returned_1_1
            returned_3_0 = response_3.result.status
            if returned_3_0:
                response.outcome.status = returned_3_0
            returned_3_1 = response_3.result.message
            if returned_3_1:
                response.result.message = returned_3_1
            echoed_0 = request.notebook_id
            response.notebook.notebook_id = echoed_0
            echoed_1 = request.notebook.status
            response.notebook.status = echoed_1
            return response

    async def handle_start_notebook_workflow(
        self,
        request: datahub_v1_notebook_workflow_service_pb2.StartNotebookWorkflowRequest
    ) -> datahub_v1_notebook_workflow_service_pb2.StartNotebookWorkflowResponse:
        """Starts a notebook."""
        deps = self.deps
        response = datahub_v1_notebook_workflow_service_pb2.StartNotebookWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('StartNotebookWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'StartNotebookWorkflow', {'reason': request.reason})
            await deps.repository.save_notebook(request.context.tenant_id, request.notebook)
            response_0 = datahub_v1_notebook_reporting_service_pb2.CountNotebookTotalsResponse()
            response_1 = analytics_v1_analytics_event_approval_service_pb2.RejectAnalyticsEventResponse()
            response_2 = documents_v1_document_service_pb2.BatchGetDocumentsResponse()
            async for item_0 in async_messages(request.notebook.lines):
                outgoing_0 = datahub_v1_notebook_reporting_service_pb2.CountNotebookTotalsRequest(
                    context=request.context,
                    filter=datahub_v1_notebook_reporting_service_pb2.CountNotebookTotalsRequest.Filter(
                        created_after=request.notebook.audit.created_at,
                        labels=dict(item_0.attributes),
                        owner_id=item_0.line_id,
                        region=request.notebook.billing_address.region
                    )
                )
                response_0 = await deps.clients.datahub_notebook_reporting.CountNotebookTotals(
                    outgoing_0,
                    timeout=deps.settings.timeout
                )
            outgoing_1 = analytics_v1_analytics_event_approval_service_pb2.RejectAnalyticsEventRequest(
                context=request.context,
                details=analytics_v1_analytics_event_approval_service_pb2.RejectAnalyticsEventRequest.Details(
                    approver=identity_v1_refs_pb2.UserRef(email=request.details.notify.email)
                )
            )
            registered_1 = cast(
                analytics_v1_analytics_event_approval_service_pb2_grpc.AnalyticsEventApprovalServiceStub,
                deps.clients.registry['acme.analytics.v1.AnalyticsEventApprovalService']
            )
            response_1 = await registered_1.RejectAnalyticsEvent(outgoing_1, timeout=deps.settings.timeout)
            command_2 = NotebookWorkflowStartNotebookWorkflow2Command(context=request.context)
            outgoing_2 = to_notebook_workflow_start_notebook_workflow2_command(command_2)
            response_2 = await deps.clients.documents_document.BatchGetDocuments(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            returned_1_0 = response_1.result.status
            if returned_1_0:
                response.outcome.status = returned_1_0
            returned_2_0 = response_2.result.details
            response.result.details.update(returned_2_0)
            returned_2_1 = response_2.result.reference_ids
            response.result.reference_ids.extend(returned_2_1)
            echoed_0 = request.notebook_id
            response.notebook.notebook_id = echoed_0
            echoed_1 = request.notebook.notes
            response.notebook.notes = echoed_1
            return response
