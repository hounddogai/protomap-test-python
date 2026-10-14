"""Reusable transport mixin for LabelSetWorkflowService."""

from __future__ import annotations

from collections.abc import AsyncIterator
from functools import partial
from typing import Any
from typing import cast
import asyncio
import logging

from google.protobuf.any_pb2 import Any as AnyMessage
from google.protobuf.json_format import MessageToDict
from google.protobuf.json_format import MessageToJson
from google.protobuf.json_format import Parse
from google.protobuf.json_format import ParseDict
import grpc

from acme.authorization.v1 import access_policy_query_service_pb2 as authorization_v1_access_policy_query_service_pb2
from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.datasets.v1 import refs_pb2 as datasets_v1_refs_pb2
from acme.featurestore.v1 import feature_value_sync_service_pb2 as featurestore_v1_feature_value_sync_service_pb2
from acme.featurestore.v1 import (
    feature_view_reporting_service_pb2 as featurestore_v1_feature_view_reporting_service_pb2,
)
from acme.featurestore.v1 import featurestore_pb2 as featurestore_v1_featurestore_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.identity.v1 import user_query_service_pb2 as identity_v1_user_query_service_pb2
from acme.identity.v1 import user_query_service_pb2_grpc as identity_v1_user_query_service_pb2_grpc
from acme.invoicing.v1 import invoice_batch_service_pb2 as invoicing_v1_invoice_batch_service_pb2
from acme.labeling.v1 import annotation_reporting_service_pb2 as labeling_v1_annotation_reporting_service_pb2
from acme.labeling.v1 import annotation_workflow_service_pb2 as labeling_v1_annotation_workflow_service_pb2
from acme.labeling.v1 import label_set_approval_service_pb2 as labeling_v1_label_set_approval_service_pb2
from acme.labeling.v1 import label_set_calculation_service_pb2 as labeling_v1_label_set_calculation_service_pb2
from acme.labeling.v1 import label_set_sync_service_pb2 as labeling_v1_label_set_sync_service_pb2
from acme.labeling.v1 import label_set_workflow_service_pb2 as labeling_v1_label_set_workflow_service_pb2
from acme.labeling.v1 import labeling_pb2 as labeling_v1_labeling_pb2
from acme.labeling.v1 import labeling_task_approval_service_pb2 as labeling_v1_labeling_task_approval_service_pb2
from acme.labeling.v1 import labeling_task_query_service_pb2 as labeling_v1_labeling_task_query_service_pb2
from acme.labeling.v1 import refs_pb2 as labeling_v1_refs_pb2
from acme.lineage.v1 import lineage_node_approval_service_pb2 as lineage_v1_lineage_node_approval_service_pb2
from acme.lineage.v1 import lineage_pb2 as lineage_v1_lineage_pb2
from acme.metrics.v1 import dashboard_history_service_pb2 as metrics_v1_dashboard_history_service_pb2
from acme.metrics.v1 import metrics_pb2 as metrics_v1_metrics_pb2

from acme_data.domains.labeling import hooks
from acme_data.domains.labeling.adapters import LabelSetWorkflowResumeLabelSetWorkflow1Adapter
from acme_data.domains.labeling.adapters import LabelSetWorkflowResumeLabelSetWorkflow1Port
from acme_data.domains.labeling.adapters import LabelSetWorkflowRetryLabelSetWorkflow1Adapter
from acme_data.domains.labeling.dependencies import Dependencies
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import run_steps
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_id
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class LabelSetWorkflowServicerHandlers:
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    async def AdvanceLabelSetWorkflow(
        self, request: labeling_v1_label_set_workflow_service_pb2.AdvanceLabelSetWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_label_set_workflow_service_pb2.AdvanceLabelSetWorkflowResponse:
        """Advances a label set."""
        return await self.handle_advance_label_set_workflow(request)

    @rpc_errors
    async def CancelLabelSetWorkflow(
        self, request: labeling_v1_label_set_workflow_service_pb2.CancelLabelSetWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_label_set_workflow_service_pb2.CancelLabelSetWorkflowResponse:
        """Cancels a label set."""
        return await self.handle_cancel_label_set_workflow(request)

    @rpc_errors
    @retry_transient
    async def InspectLabelSetWorkflow(
        self, request: labeling_v1_label_set_workflow_service_pb2.InspectLabelSetWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_label_set_workflow_service_pb2.InspectLabelSetWorkflowResponse:
        """Returns a label set."""
        return await self.handle_inspect_label_set_workflow(request)

    @rpc_errors
    @retry_transient
    async def ListLabelSetWorkflows(
        self, request: labeling_v1_label_set_workflow_service_pb2.ListLabelSetWorkflowsRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_label_set_workflow_service_pb2.ListLabelSetWorkflowsResponse:
        """Lists label sets a page at a time."""
        return await self.handle_list_label_set_workflows(request)

    @rpc_errors
    async def PauseLabelSetWorkflow(
        self, request: labeling_v1_label_set_workflow_service_pb2.PauseLabelSetWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_label_set_workflow_service_pb2.PauseLabelSetWorkflowResponse:
        """Pauses a label set."""
        return await self.handle_pause_label_set_workflow(request)

    @rpc_errors
    async def ResumeLabelSetWorkflow(
        self, request: labeling_v1_label_set_workflow_service_pb2.ResumeLabelSetWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_label_set_workflow_service_pb2.ResumeLabelSetWorkflowResponse:
        """Resumes a label set."""
        return await self.handle_resume_label_set_workflow(request)

    @rpc_errors
    async def RetryLabelSetWorkflow(
        self, request: labeling_v1_label_set_workflow_service_pb2.RetryLabelSetWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_label_set_workflow_service_pb2.RetryLabelSetWorkflowResponse:
        """Retrys a label set."""
        return await self.handle_retry_label_set_workflow(request)

    @rpc_errors
    async def SignalLabelSetWorkflow(
        self, request: labeling_v1_label_set_workflow_service_pb2.SignalLabelSetWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_label_set_workflow_service_pb2.SignalLabelSetWorkflowResponse:
        """Signals a label set."""
        return await self.handle_signal_label_set_workflow(request)

    @rpc_errors
    async def StartLabelSetWorkflow(
        self, request: labeling_v1_label_set_workflow_service_pb2.StartLabelSetWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_label_set_workflow_service_pb2.StartLabelSetWorkflowResponse:
        """Starts a label set."""
        return await self.handle_start_label_set_workflow(request)

    async def handle_advance_label_set_workflow(
        self,
        request: labeling_v1_label_set_workflow_service_pb2.AdvanceLabelSetWorkflowRequest
    ) -> labeling_v1_label_set_workflow_service_pb2.AdvanceLabelSetWorkflowResponse:
        """Advances a label set."""
        deps = self.deps
        response = labeling_v1_label_set_workflow_service_pb2.AdvanceLabelSetWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('AdvanceLabelSetWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'AdvanceLabelSetWorkflow',
                {'reason': request.reason}
            )
            await deps.repository.save_label_set(request.context.tenant_id, request.label_set)
            response_0 = labeling_v1_labeling_task_query_service_pb2.CountLabelingTasksResponse()
            response_1 = labeling_v1_annotation_workflow_service_pb2.StartAnnotationWorkflowResponse()
            outgoing_0 = labeling_v1_labeling_task_query_service_pb2.CountLabelingTasksRequest(
                context=request.context,
                filter=labeling_v1_labeling_task_query_service_pb2.CountLabelingTasksRequest.Filter(
                    created_after=request.label_set.audit.updated_at,
                    labels=dict(request.annotations),
                    owner_id=request.label_set.manager.user_id,
                    region=request.label_set.location.region
                )
            )
            outgoing_1 = labeling_v1_annotation_workflow_service_pb2.StartAnnotationWorkflowRequest(
                annotation=labeling_v1_labeling_pb2.Annotation(
                    subject=labeling_v1_refs_pb2.LabelingTaskRef(display_name=request.label_set.manager.display_name)
                ),
                context=request.context,
                details=labeling_v1_annotation_workflow_service_pb2.StartAnnotationWorkflowRequest.Details(
                    notify=common_v1_contact_pb2.ContactInfo(
                        email=request.details.notify.email,
                        name=request.details.notify.name,
                        preferred_channel=request.details.notify.preferred_channel
                    )
                )
            )
            response_0, response_1 = await asyncio.gather(
                deps.clients.labeling_labeling_task_query.CountLabelingTasks(outgoing_0, timeout=deps.settings.timeout),
                deps.clients.labeling_annotation_workflow.StartAnnotationWorkflow(
                    outgoing_1,
                    timeout=deps.settings.timeout
                ),
            )
            returned_0_0 = response_0.result.status
            if returned_0_0:
                response.outcome.status = returned_0_0
            returned_0_1 = response_0.result.message
            if returned_0_1:
                response.result.message = returned_0_1
            returned_1_0 = response_1.result.message
            if returned_1_0:
                response.outcome.message = returned_1_0
            echoed_0 = request.label_set_id
            response.label_set.label_set_id = echoed_0
            echoed_1 = request.label_set.attributes
            response.label_set.attributes.update(echoed_1)
            return response

    async def handle_cancel_label_set_workflow(
        self,
        request: labeling_v1_label_set_workflow_service_pb2.CancelLabelSetWorkflowRequest
    ) -> labeling_v1_label_set_workflow_service_pb2.CancelLabelSetWorkflowResponse:
        """Cancels a label set."""
        deps = self.deps
        response = labeling_v1_label_set_workflow_service_pb2.CancelLabelSetWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CancelLabelSetWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'CancelLabelSetWorkflow', {'reason': request.reason})
            await deps.repository.save_label_set(request.context.tenant_id, request.label_set)
            response_0 = featurestore_v1_feature_value_sync_service_pb2.PullFeatureValuesResponse()
            response_1 = identity_v1_user_query_service_pb2.LookupUserResponse()
            outgoing_0 = featurestore_v1_feature_value_sync_service_pb2.PullFeatureValuesRequest(
                context=request.context,
                feature_value=featurestore_v1_featurestore_pb2.FeatureValue(
                    subject=datasets_v1_refs_pb2.DatasetRef(display_name=request.label_set.manager.display_name)
                )
            )
            envelope_0 = AnyMessage()
            envelope_0.Pack(outgoing_0)
            outgoing_0 = featurestore_v1_feature_value_sync_service_pb2.PullFeatureValuesRequest()
            if not envelope_0.Unpack(outgoing_0):
                raise ValueError("partner envelope contains the wrong request type")
            response_0 = await deps.clients.featurestore_feature_value_sync.PullFeatureValues(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = identity_v1_user_query_service_pb2.LookupUserRequest(
                context=request.context,
                user_id=request.label_set.manager.user_id
            )
            registered_1 = cast(
                identity_v1_user_query_service_pb2_grpc.UserQueryServiceStub,
                deps.clients.registry['acme.identity.v1.UserQueryService']
            )
            response_1 = await registered_1.LookupUser(outgoing_1, timeout=deps.settings.timeout)
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.outcome.message = returned_0_0
            returned_0_1 = response_0.outcome.next_steps
            response.outcome.next_steps.extend(returned_0_1)
            returned_1_0 = response_1.user.primary_address.country_code
            returned_1_0_part_1 = response.label_set.children.add()
            if returned_1_0:
                returned_1_0_part_1.location.country_code = returned_1_0
            returned_1_1 = response_1.user.audit.created_by
            returned_1_1_part_1 = response.label_set.children.add()
            if returned_1_1:
                returned_1_1_part_1.audit.created_by = returned_1_1
            echoed_0 = request.label_set_id
            response.label_set.label_set_id = echoed_0
            echoed_1 = request.label_set.name
            response.label_set.name = echoed_1
            return response

    async def handle_inspect_label_set_workflow(
        self,
        request: labeling_v1_label_set_workflow_service_pb2.InspectLabelSetWorkflowRequest
    ) -> labeling_v1_label_set_workflow_service_pb2.InspectLabelSetWorkflowResponse:
        """Returns a label set."""
        deps = self.deps
        response = labeling_v1_label_set_workflow_service_pb2.InspectLabelSetWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('InspectLabelSetWorkflow', extra={'fields': {'domain': 'labeling'}})
            await deps.repository.audit(request.context.tenant_id, 'InspectLabelSetWorkflow', {})
            response_0 = featurestore_v1_feature_value_sync_service_pb2.ListFeatureValueConflictsResponse()
            outgoing_0 = featurestore_v1_feature_value_sync_service_pb2.ListFeatureValueConflictsRequest(
                context=request.context,
                filter=featurestore_v1_feature_value_sync_service_pb2.ListFeatureValueConflictsRequest.Filter(
                    created_after=request.context.deadline
                )
            )
            response_0 = await deps.clients.featurestore_feature_value_sync.ListFeatureValueConflicts(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.correlation_id
            if returned_0_0:
                response.result.correlation_id = returned_0_0
            returned_0_1 = response_0.result.message
            if returned_0_1:
                response.result.message = returned_0_1
            echoed_0 = request.label_set_id
            response.label_set.label_set_id = echoed_0
            return response

    async def handle_list_label_set_workflows(
        self,
        request: labeling_v1_label_set_workflow_service_pb2.ListLabelSetWorkflowsRequest
    ) -> labeling_v1_label_set_workflow_service_pb2.ListLabelSetWorkflowsResponse:
        """Lists label sets a page at a time."""
        deps = self.deps
        response = labeling_v1_label_set_workflow_service_pb2.ListLabelSetWorkflowsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ListLabelSetWorkflows', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ListLabelSetWorkflows',
                {'order_by': request.order_by}
            )
            response_0 = lineage_v1_lineage_node_approval_service_pb2.RecallLineageNodeResponse()
            outgoing_0 = lineage_v1_lineage_node_approval_service_pb2.RecallLineageNodeRequest(
                context=request.context,
                lineage_node=lineage_v1_lineage_pb2.LineageNode(
                    children=[
                        lineage_v1_lineage_pb2.LineageNode(
                            children=[
                                lineage_v1_lineage_pb2.LineageNode(
                                    location=common_v1_address_pb2.PostalAddress(region=request.filter.region),
                                    manager=identity_v1_refs_pb2.UserRef(email=request.context.actor.email)
                                )
                            ]
                        )
                    ]
                )
            )
            response_0 = await deps.clients.lineage_lineage_node_approval.RecallLineageNode(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.lineage_node.attributes
            returned_0_0_part_0 = response.label_sets.add()
            returned_0_0_part_1 = returned_0_0_part_0.children.add()
            returned_0_0_part_2 = returned_0_0_part_1.children.add()
            returned_0_0_part_3 = returned_0_0_part_2.children.add()
            returned_0_0_part_3.attributes.update(returned_0_0)
            returned_0_1 = response_0.lineage_node.location
            returned_0_1_part_0 = response.label_sets.add()
            returned_0_1_part_1 = returned_0_1_part_0.children.add()
            returned_0_1_part_2 = returned_0_1_part_1.children.add()
            returned_0_1_part_3 = returned_0_1_part_2.children.add()
            if returned_0_1.ListFields():
                returned_0_1_part_3.location.MergeFrom(returned_0_1)
            return response

    async def handle_pause_label_set_workflow(
        self,
        request: labeling_v1_label_set_workflow_service_pb2.PauseLabelSetWorkflowRequest
    ) -> labeling_v1_label_set_workflow_service_pb2.PauseLabelSetWorkflowResponse:
        """Pauses a label set."""
        deps = self.deps
        response = labeling_v1_label_set_workflow_service_pb2.PauseLabelSetWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('PauseLabelSetWorkflow', extra={'fields': {'initiated_by': request.details.initiated_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'PauseLabelSetWorkflow',
                {'initiated_by': request.details.initiated_by}
            )
            await deps.repository.save_label_set(request.context.tenant_id, request.label_set)
            response_0 = metrics_v1_dashboard_history_service_pb2.AnnotateDashboardVersionResponse()
            response_1 = featurestore_v1_feature_view_reporting_service_pb2.ScheduleFeatureViewReportResponse()
            outgoing_0 = metrics_v1_dashboard_history_service_pb2.AnnotateDashboardVersionRequest(
                context=request.context,
                dashboard=metrics_v1_metrics_pb2.Dashboard(
                    audit=common_v1_audit_pb2.AuditInfo(
                        updated_at=request.label_set.audit.updated_at,
                        updated_by=request.label_set.audit.updated_by
                    ),
                    billing_address=common_v1_address_pb2.PostalAddress(lines=list(request.label_set.location.lines)),
                    lines=[metrics_v1_metrics_pb2.DashboardLine(attributes=dict(request.label_set.attributes))]
                )
            )
            send_0 = partial(
                deps.clients.metrics_dashboard_history.AnnotateDashboardVersion,
                timeout=deps.settings.timeout
            )
            response_0 = await send_0(outgoing_0)
            outgoing_1 = featurestore_v1_feature_view_reporting_service_pb2.ScheduleFeatureViewReportRequest(
                annotations=dict(request.annotations),
                context=request.context,
                details=featurestore_v1_feature_view_reporting_service_pb2.ScheduleFeatureViewReportRequest.Details(
                    filters=dict(response_0.result.details)
                ),
                reason=request.reason
            )
            response_1 = await hooks.label_set_workflow_pause_label_set_workflow1(
                deps.clients.featurestore_feature_view_reporting,
                outgoing_1,
                deps.settings.timeout
            )
            returned_0_0 = response_0.dashboard.audit.etag
            if returned_0_0:
                response.label_set.audit.etag = returned_0_0
            returned_0_1 = response_0.dashboard.billing_address.recipient
            returned_0_1_part_1 = response.label_set.children.add()
            returned_0_1_part_2 = returned_0_1_part_1.children.add()
            if returned_0_1:
                returned_0_1_part_2.location.recipient = returned_0_1
            returned_1_0 = response_1.result.reference_ids
            response.result.reference_ids.extend(returned_1_0)
            echoed_0 = request.label_set_id
            response.label_set.label_set_id = echoed_0
            echoed_1 = request.label_set.location
            response.label_set.location.CopyFrom(echoed_1)
            return response

    async def handle_resume_label_set_workflow(
        self,
        request: labeling_v1_label_set_workflow_service_pb2.ResumeLabelSetWorkflowRequest
    ) -> labeling_v1_label_set_workflow_service_pb2.ResumeLabelSetWorkflowResponse:
        """Resumes a label set."""
        deps = self.deps
        response = labeling_v1_label_set_workflow_service_pb2.ResumeLabelSetWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ResumeLabelSetWorkflow', extra={'fields': {'initiated_by': request.details.initiated_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ResumeLabelSetWorkflow',
                {'initiated_by': request.details.initiated_by}
            )
            await deps.repository.save_label_set(request.context.tenant_id, request.label_set)
            response_0 = invoicing_v1_invoice_batch_service_pb2.CloneInvoiceBatchResponse()
            response_1 = featurestore_v1_feature_view_reporting_service_pb2.GenerateFeatureViewReportResponse()
            outgoing_0 = invoicing_v1_invoice_batch_service_pb2.CloneInvoiceBatchRequest()
            outgoing_0.context.CopyFrom(request.context)
            outgoing_0.invoice_batch.billing_address.locality = request.label_set.location.locality
            outgoing_0.invoice_batch.audit.updated_at.CopyFrom(request.label_set.audit.updated_at)
            outgoing_0.invoice_batch.billing_address.lines.extend(list(request.label_set.location.lines))
            field_0_4_part_1 = outgoing_0.invoice_batch.lines.add()
            field_0_4_part_1.attributes.update(dict(request.label_set.attributes))
            outgoing_0.context.tenant_id = tenant_id.get()
            response_0 = await deps.clients.invoicing_invoice_batch.CloneInvoiceBatch(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = featurestore_v1_feature_view_reporting_service_pb2.GenerateFeatureViewReportRequest(
                annotations=dict(request.annotations),
                context=request.context,
                details=featurestore_v1_feature_view_reporting_service_pb2.GenerateFeatureViewReportRequest.Details(
                    filters=dict(request.details.parameters)
                ),
                reason=request.reason
            )
            port_1: LabelSetWorkflowResumeLabelSetWorkflow1Port = LabelSetWorkflowResumeLabelSetWorkflow1Adapter(
                deps.clients.featurestore_feature_view_reporting,
                deps.settings.timeout
            )
            response_1 = await port_1.execute(outgoing_1)
            returned_0_0 = response_0.invoice_batch.billing_address.recipient
            returned_0_0_part_1 = response.label_set.children.add()
            if returned_0_0:
                returned_0_0_part_1.location.recipient = returned_0_0
            returned_1_0 = response_1.result.correlation_id
            if returned_1_0:
                response.result.correlation_id = returned_1_0
            echoed_0 = request.label_set_id
            response.label_set.label_set_id = echoed_0
            echoed_1 = request.label_set.location
            response.label_set.location.CopyFrom(echoed_1)
            return response

    async def handle_retry_label_set_workflow(
        self,
        request: labeling_v1_label_set_workflow_service_pb2.RetryLabelSetWorkflowRequest
    ) -> labeling_v1_label_set_workflow_service_pb2.RetryLabelSetWorkflowResponse:
        """Retrys a label set."""
        deps = self.deps
        response = labeling_v1_label_set_workflow_service_pb2.RetryLabelSetWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('RetryLabelSetWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'RetryLabelSetWorkflow', {'reason': request.reason})
            await deps.repository.save_label_set(request.context.tenant_id, request.label_set)
            response_0 = labeling_v1_label_set_calculation_service_pb2.CompareLabelSetOptionsResponse()
            response_1 = labeling_v1_labeling_task_approval_service_pb2.RejectLabelingTaskResponse()
            response_2 = labeling_v1_label_set_sync_service_pb2.ResolveLabelSetConflictResponse()
            response_3 = authorization_v1_access_policy_query_service_pb2.CountAccessPoliciesResponse()
            outgoing_0 = labeling_v1_label_set_calculation_service_pb2.CompareLabelSetOptionsRequest(
                context=request.context,
                label_set=labeling_v1_labeling_pb2.LabelSet(
                    children=[
                        labeling_v1_labeling_pb2.LabelSet(
                            audit=common_v1_audit_pb2.AuditInfo(etag=request.label_set.audit.etag),
                            children=[
                                labeling_v1_labeling_pb2.LabelSet(
                                    children=[labeling_v1_labeling_pb2.LabelSet(path=list(request.label_set.path))],
                                    manager=identity_v1_refs_pb2.UserRef(email=request.label_set.manager.email)
                                )
                            ],
                            location=common_v1_address_pb2.PostalAddress(
                                postal_code=request.label_set.location.postal_code
                            )
                        )
                    ]
                )
            )
            steps_0 = [
                partial(
                    deps.clients.labeling_label_set_calculation.CompareLabelSetOptions,
                    outgoing_0,
                    timeout=deps.settings.timeout
                )
            ]
            results_0 = await run_steps(steps_0)
            response_0 = results_0[-1]
            outgoing_1 = labeling_v1_labeling_task_approval_service_pb2.RejectLabelingTaskRequest(
                context=request.context,
                details=labeling_v1_labeling_task_approval_service_pb2.RejectLabelingTaskRequest.Details(
                    approver=identity_v1_refs_pb2.UserRef(
                        email=request.details.notify.email,
                        user_id=response_0.label_set.manager.user_id
                    )
                ),
                labeling_task=labeling_v1_labeling_pb2.LabelingTask(
                    audit=common_v1_audit_pb2.AuditInfo(etag=response_0.label_set.audit.etag),
                    requester=common_v1_contact_pb2.ContactInfo(phone=request.details.notify.phone)
                )
            )
            response_1 = await LabelSetWorkflowRetryLabelSetWorkflow1Adapter(
                deps.clients.labeling_labeling_task_approval,
                deps.settings.timeout
            )(outgoing_1)
            outgoing_2 = labeling_v1_label_set_sync_service_pb2.ResolveLabelSetConflictRequest(
                context=request.context,
                label_set=labeling_v1_labeling_pb2.LabelSet(
                    children=[
                        labeling_v1_labeling_pb2.LabelSet(
                            children=[
                                labeling_v1_labeling_pb2.LabelSet(
                                    audit=common_v1_audit_pb2.AuditInfo(updated_by=request.label_set.audit.updated_by)
                                )
                            ]
                        )
                    ]
                )
            )
            response_2 = cast(labeling_v1_label_set_sync_service_pb2.ResolveLabelSetConflictResponse, await deps.bus.request(
                'acme.labeling.v1.LabelSetWorkflowService/RetryLabelSetWorkflow/2', outgoing_2, deps.settings.timeout,
            ))
            outgoing_3 = authorization_v1_access_policy_query_service_pb2.CountAccessPoliciesRequest(
                context=request.context,
                filter=authorization_v1_access_policy_query_service_pb2.CountAccessPoliciesRequest.Filter(
                    created_after=response_1.labeling_task.audit.updated_at,
                    owner_id=response_2.label_set.manager.user_id,
                    region=response_0.label_set.location.region
                )
            )
            response_3 = await deps.clients.authorization_access_policy_query.CountAccessPolicies(
                outgoing_3,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.label_set.manager.email
            if returned_0_0:
                response.label_set.manager.email = returned_0_0
            returned_1_0 = response_1.labeling_task.audit.etag
            if returned_1_0:
                response.label_set.audit.etag = returned_1_0
            returned_1_1 = response_1.result.details
            response.result.details.update(returned_1_1)
            returned_2_0 = response_2.label_set.status
            returned_2_0_part_1 = response.label_set.children.add()
            returned_2_0_part_2 = returned_2_0_part_1.children.add()
            if returned_2_0:
                returned_2_0_part_2.status = returned_2_0
            returned_3_0 = response_3.result.message
            if returned_3_0:
                response.outcome.message = returned_3_0
            returned_3_1 = response_3.result.status
            if returned_3_1:
                response.result.status = returned_3_1
            echoed_0 = request.label_set_id
            response.label_set.label_set_id = echoed_0
            echoed_1 = request.label_set.name
            response.label_set.name = echoed_1
            return response

    async def handle_signal_label_set_workflow(
        self,
        request: labeling_v1_label_set_workflow_service_pb2.SignalLabelSetWorkflowRequest
    ) -> labeling_v1_label_set_workflow_service_pb2.SignalLabelSetWorkflowResponse:
        """Signals a label set."""
        deps = self.deps
        response = labeling_v1_label_set_workflow_service_pb2.SignalLabelSetWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SignalLabelSetWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'SignalLabelSetWorkflow', {'reason': request.reason})
            await deps.repository.save_label_set(request.context.tenant_id, request.label_set)
            response_0 = featurestore_v1_feature_view_reporting_service_pb2.ListFeatureViewReportsResponse()
            response_1 = labeling_v1_annotation_reporting_service_pb2.CountAnnotationTotalsResponse()
            response_2 = labeling_v1_label_set_approval_service_pb2.RecallLabelSetResponse()
            response_3 = labeling_v1_label_set_sync_service_pb2.PushLabelSetResponse()
            outgoing_0 = featurestore_v1_feature_view_reporting_service_pb2.ListFeatureViewReportsRequest(
                context=request.context,
                filter=featurestore_v1_feature_view_reporting_service_pb2.ListFeatureViewReportsRequest.Filter(
                    region=request.label_set.location.region
                )
            )
            method_name_0 = 'ListFeatureViewReports'
            response_0 = await getattr(
                deps.clients.featurestore_feature_view_reporting,
                method_name_0
            )(outgoing_0, timeout=deps.settings.timeout)
            fields_1: dict[str, Any] = {
                'context': request.context,
                'filter': {'region': request.label_set.location.region}
            }
            outgoing_1 = labeling_v1_annotation_reporting_service_pb2.CountAnnotationTotalsRequest(**fields_1)
            response_1 = await deps.clients.labeling_annotation_reporting.CountAnnotationTotals(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = labeling_v1_label_set_approval_service_pb2.RecallLabelSetRequest(
                context=request.context,
                label_set=labeling_v1_labeling_pb2.LabelSet(
                    children=[
                        labeling_v1_labeling_pb2.LabelSet(
                            children=[
                                labeling_v1_labeling_pb2.LabelSet(
                                    audit=common_v1_audit_pb2.AuditInfo(created_at=request.label_set.audit.created_at),
                                    location=common_v1_address_pb2.PostalAddress(
                                        lines=list(request.label_set.location.lines)
                                    )
                                )
                            ]
                        )
                    ]
                )
            )
            document_2 = MessageToDict(outgoing_2, preserving_proto_field_name=True)
            outgoing_2 = ParseDict(document_2, labeling_v1_label_set_approval_service_pb2.RecallLabelSetRequest())
            response_2 = await deps.clients.labeling_label_set_approval.RecallLabelSet(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            outgoing_3 = labeling_v1_label_set_sync_service_pb2.PushLabelSetRequest(
                context=request.context,
                label_set=labeling_v1_labeling_pb2.LabelSet(
                    children=[
                        labeling_v1_labeling_pb2.LabelSet(
                            children=[
                                labeling_v1_labeling_pb2.LabelSet(
                                    audit=common_v1_audit_pb2.AuditInfo(
                                        created_at=response_2.label_set.audit.created_at
                                    )
                                )
                            ]
                        )
                    ]
                )
            )
            document_3 = MessageToJson(outgoing_3, preserving_proto_field_name=True)
            outgoing_3 = Parse(document_3, labeling_v1_label_set_sync_service_pb2.PushLabelSetRequest())
            response_3 = await deps.clients.labeling_label_set_sync.PushLabelSet(
                outgoing_3,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_0)
            returned_1_0 = response_1.result.message
            if returned_1_0:
                response.result.message = returned_1_0
            returned_2_0 = response_2.label_set.manager
            returned_2_0_part_1 = response.label_set.children.add()
            if returned_2_0.ListFields():
                returned_2_0_part_1.manager.MergeFrom(returned_2_0)
            returned_3_0 = response_3.label_set.attributes
            returned_3_0_part_1 = response.label_set.children.add()
            returned_3_0_part_1.attributes.update(returned_3_0)
            echoed_0 = request.label_set_id
            response.label_set.label_set_id = echoed_0
            echoed_1 = request.label_set.parent_id
            response.label_set.parent_id = echoed_1
            return response

    async def handle_start_label_set_workflow(
        self,
        request: labeling_v1_label_set_workflow_service_pb2.StartLabelSetWorkflowRequest
    ) -> labeling_v1_label_set_workflow_service_pb2.StartLabelSetWorkflowResponse:
        """Starts a label set."""
        deps = self.deps
        response = labeling_v1_label_set_workflow_service_pb2.StartLabelSetWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('StartLabelSetWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'StartLabelSetWorkflow', {'reason': request.reason})
            await deps.repository.save_label_set(request.context.tenant_id, request.label_set)
            response_0 = labeling_v1_label_set_sync_service_pb2.PullLabelSetsResponse()
            outgoing_0 = labeling_v1_label_set_sync_service_pb2.PullLabelSetsRequest()
            outgoing_0.context.CopyFrom(request.context)
            field_0_1_part_1 = outgoing_0.label_set.children.add()
            field_0_1_part_2 = field_0_1_part_1.children.add()
            field_0_1_part_2.manager.email = request.label_set.manager.email
            field_0_2_part_1 = outgoing_0.label_set.children.add()
            field_0_2_part_2 = field_0_2_part_1.children.add()
            field_0_2_part_2.location.lines.extend(list(request.label_set.location.lines))
            merged_0 = labeling_v1_label_set_sync_service_pb2.PullLabelSetsRequest()
            merged_0.MergeFrom(outgoing_0)
            outgoing_0.CopyFrom(merged_0)
            response_0 = await deps.clients.labeling_label_set_sync.PullLabelSets(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.label_set.manager
            if returned_0_0.ListFields():
                response.label_set.manager.MergeFrom(returned_0_0)
            echoed_0 = request.label_set_id
            response.label_set.label_set_id = echoed_0
            echoed_1 = request.label_set.depth
            response.label_set.depth = echoed_1
            return response
