"""Runs the long-lived workflow that takes a labeling task from start to finish."""

from __future__ import annotations

from collections.abc import AsyncIterator
from collections.abc import Awaitable
from collections.abc import Callable
from functools import partial
from typing import cast
import asyncio
import logging

from google.protobuf.any_pb2 import Any as AnyMessage
import grpc

from acme.anomalies.v1 import anomalies_pb2 as anomalies_v1_anomalies_pb2
from acme.anomalies.v1 import anomaly_approval_service_pb2 as anomalies_v1_anomaly_approval_service_pb2
from acme.audit.v1 import audit_event_query_service_pb2 as audit_v1_audit_event_query_service_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.common.v1 import paging_pb2 as common_v1_paging_pb2
from acme.featurestore.v1 import feature_view_approval_service_pb2 as featurestore_v1_feature_view_approval_service_pb2
from acme.featurestore.v1 import featurestore_pb2 as featurestore_v1_featurestore_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.labeling.v1 import annotation_reporting_service_pb2 as labeling_v1_annotation_reporting_service_pb2
from acme.labeling.v1 import label_set_sync_service_pb2 as labeling_v1_label_set_sync_service_pb2
from acme.labeling.v1 import labeling_pb2 as labeling_v1_labeling_pb2
from acme.labeling.v1 import labeling_task_approval_service_pb2 as labeling_v1_labeling_task_approval_service_pb2
from acme.labeling.v1 import (
    labeling_task_approval_service_pb2_grpc as labeling_v1_labeling_task_approval_service_pb2_grpc,
)
from acme.labeling.v1 import labeling_task_lifecycle_service_pb2 as labeling_v1_labeling_task_lifecycle_service_pb2
from acme.labeling.v1 import labeling_task_query_service_pb2 as labeling_v1_labeling_task_query_service_pb2
from acme.labeling.v1 import labeling_task_workflow_service_pb2 as labeling_v1_labeling_task_workflow_service_pb2
from acme.labeling.v1 import (
    labeling_task_workflow_service_pb2_grpc as labeling_v1_labeling_task_workflow_service_pb2_grpc,
)
from acme.metrics.v1 import dashboard_validation_service_pb2 as metrics_v1_dashboard_validation_service_pb2
from acme.metrics.v1 import metric_alert_admin_service_pb2 as metrics_v1_metric_alert_admin_service_pb2
from acme.metrics.v1 import metric_series_history_service_pb2 as metrics_v1_metric_series_history_service_pb2
from acme.metrics.v1 import metric_series_query_service_pb2 as metrics_v1_metric_series_query_service_pb2
from acme.metrics.v1 import metrics_pb2 as metrics_v1_metrics_pb2
from acme.notifications.v1 import notification_query_service_pb2 as notifications_v1_notification_query_service_pb2
from acme.pricing.v1 import price_list_query_service_pb2 as pricing_v1_price_list_query_service_pb2
from acme.ratelimiting.v1 import rate_limit_service_pb2 as ratelimiting_v1_rate_limit_service_pb2
from acme.timekeeping.v1 import timesheet_service_pb2 as timekeeping_v1_timesheet_service_pb2

from acme_data.domains.labeling import hooks
from acme_data.domains.labeling.adapters import LabelingTaskWorkflowResumeLabelingTaskWorkflow0Adapter
from acme_data.domains.labeling.dependencies import Dependencies
from acme_data.domains.labeling.models import LabelingTaskWorkflowCancelLabelingTaskWorkflow0Command
from acme_data.domains.labeling.models import LabelingTaskWorkflowSignalLabelingTaskWorkflow2Command
from acme_data.domains.labeling.models import to_labeling_task_workflow_cancel_labeling_task_workflow0_command
from acme_data.domains.labeling.models import to_labeling_task_workflow_signal_labeling_task_workflow2_command
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import run_steps
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class LabelingTaskWorkflowServicer(
    labeling_v1_labeling_task_workflow_service_pb2_grpc.LabelingTaskWorkflowServiceServicer
):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    async def AdvanceLabelingTaskWorkflow(
        self, request: labeling_v1_labeling_task_workflow_service_pb2.AdvanceLabelingTaskWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_labeling_task_workflow_service_pb2.AdvanceLabelingTaskWorkflowResponse:
        """Advances a labeling task."""
        return await self.handle_advance_labeling_task_workflow(request)

    @rpc_errors
    async def CancelLabelingTaskWorkflow(
        self, request: labeling_v1_labeling_task_workflow_service_pb2.CancelLabelingTaskWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_labeling_task_workflow_service_pb2.CancelLabelingTaskWorkflowResponse:
        """Cancels a labeling task."""
        return await self.handle_cancel_labeling_task_workflow(request)

    @rpc_errors
    @retry_transient
    async def InspectLabelingTaskWorkflow(
        self, request: labeling_v1_labeling_task_workflow_service_pb2.InspectLabelingTaskWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_labeling_task_workflow_service_pb2.InspectLabelingTaskWorkflowResponse:
        """Returns a labeling task."""
        return await self.handle_inspect_labeling_task_workflow(request)

    @rpc_errors
    @retry_transient
    async def ListLabelingTaskWorkflows(
        self, request: labeling_v1_labeling_task_workflow_service_pb2.ListLabelingTaskWorkflowsRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_labeling_task_workflow_service_pb2.ListLabelingTaskWorkflowsResponse:
        """Lists labeling tasks a page at a time."""
        return await self.handle_list_labeling_task_workflows(request)

    @rpc_errors
    async def PauseLabelingTaskWorkflow(
        self, request: labeling_v1_labeling_task_workflow_service_pb2.PauseLabelingTaskWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_labeling_task_workflow_service_pb2.PauseLabelingTaskWorkflowResponse:
        """Pauses a labeling task."""
        return await self.handle_pause_labeling_task_workflow(request)

    @rpc_errors
    async def ResumeLabelingTaskWorkflow(
        self, request: labeling_v1_labeling_task_workflow_service_pb2.ResumeLabelingTaskWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_labeling_task_workflow_service_pb2.ResumeLabelingTaskWorkflowResponse:
        """Resumes a labeling task."""
        return await self.handle_resume_labeling_task_workflow(request)

    @rpc_errors
    async def RetryLabelingTaskWorkflow(
        self, request: labeling_v1_labeling_task_workflow_service_pb2.RetryLabelingTaskWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_labeling_task_workflow_service_pb2.RetryLabelingTaskWorkflowResponse:
        """Retrys a labeling task."""
        return await self.handle_retry_labeling_task_workflow(request)

    @rpc_errors
    async def SignalLabelingTaskWorkflow(
        self, request: labeling_v1_labeling_task_workflow_service_pb2.SignalLabelingTaskWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_labeling_task_workflow_service_pb2.SignalLabelingTaskWorkflowResponse:
        """Signals a labeling task."""
        return await self.handle_signal_labeling_task_workflow(request)

    @rpc_errors
    async def StartLabelingTaskWorkflow(
        self, request: labeling_v1_labeling_task_workflow_service_pb2.StartLabelingTaskWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_labeling_task_workflow_service_pb2.StartLabelingTaskWorkflowResponse:
        """Starts a labeling task."""
        return await self.handle_start_labeling_task_workflow(request)

    async def handle_advance_labeling_task_workflow(
        self,
        request: labeling_v1_labeling_task_workflow_service_pb2.AdvanceLabelingTaskWorkflowRequest
    ) -> labeling_v1_labeling_task_workflow_service_pb2.AdvanceLabelingTaskWorkflowResponse:
        """Advances a labeling task."""
        deps = self.deps
        response = labeling_v1_labeling_task_workflow_service_pb2.AdvanceLabelingTaskWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('AdvanceLabelingTaskWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'AdvanceLabelingTaskWorkflow',
                {'reason': request.reason}
            )
            await deps.repository.save_labeling_task(request.context.tenant_id, request.labeling_task)
            response_0 = anomalies_v1_anomaly_approval_service_pb2.CommentAnomalyApprovalResponse()
            response_1 = metrics_v1_dashboard_validation_service_pb2.ValidateDashboardResponse()
            outgoing_0 = anomalies_v1_anomaly_approval_service_pb2.CommentAnomalyApprovalRequest(
                anomaly=anomalies_v1_anomalies_pb2.Anomaly(
                    requester=common_v1_contact_pb2.ContactInfo(
                        name=request.labeling_task.requester.name,
                        phone=request.details.notify.phone
                    ),
                    sla=anomalies_v1_anomalies_pb2.AnomalySla(paused_for=request.labeling_task.sla.paused_for)
                ),
                context=request.context,
                details=anomalies_v1_anomaly_approval_service_pb2.CommentAnomalyApprovalRequest.Details(
                    approver=identity_v1_refs_pb2.UserRef(email=request.details.notify.email)
                )
            )
            outgoing_1 = metrics_v1_dashboard_validation_service_pb2.ValidateDashboardRequest(
                context=request.context,
                dashboard=metrics_v1_metrics_pb2.Dashboard(
                    audit=common_v1_audit_pb2.AuditInfo(created_at=request.labeling_task.audit.created_at)
                ),
                details=metrics_v1_dashboard_validation_service_pb2.ValidateDashboardRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(
                        email=request.details.notify.email,
                        phone=request.labeling_task.requester.phone
                    )
                )
            )
            response_0, response_1 = await asyncio.gather(
                deps.clients.anomalies_anomaly_approval.CommentAnomalyApproval(
                    outgoing_0,
                    timeout=deps.settings.timeout
                ),
                deps.clients.metrics_dashboard_validation.ValidateDashboard(outgoing_1, timeout=deps.settings.timeout),
            )
            returned_0_0 = response_0.anomaly.assignee.display_name
            if returned_0_0:
                response.labeling_task.assignee.display_name = returned_0_0
            returned_1_0 = response_1.result.status
            if returned_1_0:
                response.outcome.status = returned_1_0
            returned_1_1 = response_1.dashboard.audit.etag
            if returned_1_1:
                response.labeling_task.audit.etag = returned_1_1
            echoed_0 = request.labeling_task_id
            response.labeling_task.labeling_task_id = echoed_0
            echoed_1 = request.labeling_task.priority
            response.labeling_task.priority = echoed_1
            return response

    async def handle_cancel_labeling_task_workflow(
        self,
        request: labeling_v1_labeling_task_workflow_service_pb2.CancelLabelingTaskWorkflowRequest
    ) -> labeling_v1_labeling_task_workflow_service_pb2.CancelLabelingTaskWorkflowResponse:
        """Cancels a labeling task."""
        deps = self.deps
        response = labeling_v1_labeling_task_workflow_service_pb2.CancelLabelingTaskWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CancelLabelingTaskWorkflow', extra={'fields': {'initiated_by': request.details.initiated_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'CancelLabelingTaskWorkflow',
                {'initiated_by': request.details.initiated_by}
            )
            await deps.repository.save_labeling_task(request.context.tenant_id, request.labeling_task)
            response_0 = labeling_v1_labeling_task_approval_service_pb2.RecallLabelingTaskResponse()
            response_1 = labeling_v1_annotation_reporting_service_pb2.GenerateAnnotationReportResponse()
            response_2 = labeling_v1_label_set_sync_service_pb2.PushLabelSetResponse()
            command_0 = LabelingTaskWorkflowCancelLabelingTaskWorkflow0Command.model_validate(
                {'context': request.context, 'labeling_task_sla_breached': request.labeling_task.sla.breached}
            )
            outgoing_0 = to_labeling_task_workflow_cancel_labeling_task_workflow0_command(command_0)
            response_0 = await deps.clients.labeling_labeling_task_approval.RecallLabelingTask(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = labeling_v1_annotation_reporting_service_pb2.GenerateAnnotationReportRequest(
                annotations=dict(request.annotations),
                context=request.context,
                details=labeling_v1_annotation_reporting_service_pb2.GenerateAnnotationReportRequest.Details(
                    filters=dict(response_0.result.details)
                ),
                reason=request.reason
            )
            send_1 = partial(
                deps.clients.labeling_annotation_reporting.GenerateAnnotationReport,
                timeout=deps.settings.timeout
            )
            response_1 = await send_1(outgoing_1)
            outgoing_2 = labeling_v1_label_set_sync_service_pb2.PushLabelSetRequest(
                context=request.context,
                label_set=labeling_v1_labeling_pb2.LabelSet(
                    children=[
                        labeling_v1_labeling_pb2.LabelSet(
                            children=[
                                labeling_v1_labeling_pb2.LabelSet(
                                    children=[
                                        labeling_v1_labeling_pb2.LabelSet(
                                            label_set_id=response_0.labeling_task.customer.label_set_id
                                        )
                                    ],
                                    manager=identity_v1_refs_pb2.UserRef(
                                        display_name=response_0.labeling_task.assignee.display_name,
                                        email=request.details.notify.email
                                    )
                                )
                            ]
                        )
                    ]
                )
            )
            response_2 = await hooks.labeling_task_workflow_cancel_labeling_task_workflow2(
                deps.clients.labeling_label_set_sync,
                outgoing_2,
                deps.settings.timeout
            )
            returned_0_0 = response_0.result.correlation_id
            if returned_0_0:
                response.result.correlation_id = returned_0_0
            returned_1_0 = response_1.result.message
            if returned_1_0:
                response.outcome.message = returned_1_0
            returned_1_1 = response_1.result.details
            response.result.details.update(returned_1_1)
            returned_2_0 = response_2.outcome.status
            if returned_2_0:
                response.outcome.status = returned_2_0
            echoed_0 = request.labeling_task_id
            response.labeling_task.labeling_task_id = echoed_0
            echoed_1 = request.labeling_task.requester
            response.labeling_task.requester.CopyFrom(echoed_1)
            return response

    async def handle_inspect_labeling_task_workflow(
        self,
        request: labeling_v1_labeling_task_workflow_service_pb2.InspectLabelingTaskWorkflowRequest
    ) -> labeling_v1_labeling_task_workflow_service_pb2.InspectLabelingTaskWorkflowResponse:
        """Returns a labeling task."""
        deps = self.deps
        response = labeling_v1_labeling_task_workflow_service_pb2.InspectLabelingTaskWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('InspectLabelingTaskWorkflow', extra={'fields': {'locale': request.context.locale}})
            await deps.repository.audit(
                request.context.tenant_id,
                'InspectLabelingTaskWorkflow',
                {'locale': request.context.locale}
            )
            echoed_0 = request.labeling_task_id
            response.labeling_task.labeling_task_id = echoed_0
            return response

    async def handle_list_labeling_task_workflows(
        self,
        request: labeling_v1_labeling_task_workflow_service_pb2.ListLabelingTaskWorkflowsRequest
    ) -> labeling_v1_labeling_task_workflow_service_pb2.ListLabelingTaskWorkflowsResponse:
        """Lists labeling tasks a page at a time."""
        deps = self.deps
        response = labeling_v1_labeling_task_workflow_service_pb2.ListLabelingTaskWorkflowsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ListLabelingTaskWorkflows', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ListLabelingTaskWorkflows',
                {'order_by': request.order_by}
            )
            response_0 = timekeeping_v1_timesheet_service_pb2.SearchTimesheetsResponse()
            outgoing_0 = timekeeping_v1_timesheet_service_pb2.SearchTimesheetsRequest(
                context=request.context,
                filter=timekeeping_v1_timesheet_service_pb2.SearchTimesheetsRequest.Filter(
                    labels=dict(request.filter.labels)
                ),
                page=common_v1_paging_pb2.PageRequest(
                    page_size=request.page.page_size,
                    page_token=request.page.page_token
                )
            )
            response_0 = await deps.clients.timekeeping_timesheet.SearchTimesheets(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.result.message = returned_0_0
            returned_0_1 = response_0.result.details
            response.result.details.update(returned_0_1)
            return response

    async def handle_pause_labeling_task_workflow(
        self,
        request: labeling_v1_labeling_task_workflow_service_pb2.PauseLabelingTaskWorkflowRequest
    ) -> labeling_v1_labeling_task_workflow_service_pb2.PauseLabelingTaskWorkflowResponse:
        """Pauses a labeling task."""
        deps = self.deps
        response = labeling_v1_labeling_task_workflow_service_pb2.PauseLabelingTaskWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('PauseLabelingTaskWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'PauseLabelingTaskWorkflow',
                {'reason': request.reason}
            )
            await deps.repository.save_labeling_task(request.context.tenant_id, request.labeling_task)
            response_0 = pricing_v1_price_list_query_service_pb2.SuggestPriceListsResponse()
            response_1 = featurestore_v1_feature_view_approval_service_pb2.RejectFeatureViewResponse()
            outgoing_0 = pricing_v1_price_list_query_service_pb2.SuggestPriceListsRequest()
            outgoing_0.context.CopyFrom(request.context)
            outgoing_0.filter.created_after.CopyFrom(request.labeling_task.sla.due_at)
            if request.labeling_task.WhichOneof('origin') == 'customer':
                outgoing_0.filter.owner_id = request.labeling_task.customer.label_set_id
            outgoing_0.filter.labels.update(dict(request.annotations))
            response_0 = await deps.clients.pricing_price_list_query.SuggestPriceLists(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = featurestore_v1_feature_view_approval_service_pb2.RejectFeatureViewRequest(
                context=request.context,
                details=featurestore_v1_feature_view_approval_service_pb2.RejectFeatureViewRequest.Details(
                    approver=identity_v1_refs_pb2.UserRef(email=request.details.notify.email)
                ),
                feature_view=featurestore_v1_featurestore_pb2.FeatureView(
                    owner=identity_v1_refs_pb2.UserRef(
                        display_name=request.labeling_task.assignee.display_name,
                        email=request.labeling_task.requester.email,
                        user_id=request.labeling_task.assignee.user_id
                    )
                )
            )
            steps_1 = [
                partial(
                    deps.clients.featurestore_feature_view_approval.RejectFeatureView,
                    outgoing_1,
                    timeout=deps.settings.timeout
                )
            ]
            results_1 = await run_steps(steps_1)
            response_1 = results_1[-1]
            returned_0_0 = response_0.result.details
            response.result.details.update(returned_0_0)
            returned_1_0 = response_1.outcome.status
            if returned_1_0:
                response.result.status = returned_1_0
            echoed_0 = request.labeling_task_id
            response.labeling_task.labeling_task_id = echoed_0
            echoed_1 = request.labeling_task.subject
            response.labeling_task.subject = echoed_1
            return response

    async def handle_resume_labeling_task_workflow(
        self,
        request: labeling_v1_labeling_task_workflow_service_pb2.ResumeLabelingTaskWorkflowRequest
    ) -> labeling_v1_labeling_task_workflow_service_pb2.ResumeLabelingTaskWorkflowResponse:
        """Resumes a labeling task."""
        deps = self.deps
        response = labeling_v1_labeling_task_workflow_service_pb2.ResumeLabelingTaskWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ResumeLabelingTaskWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ResumeLabelingTaskWorkflow',
                {'reason': request.reason}
            )
            await deps.repository.save_labeling_task(request.context.tenant_id, request.labeling_task)
            response_0 = metrics_v1_metric_alert_admin_service_pb2.RepairMetricAlertResponse()
            response_1 = metrics_v1_dashboard_validation_service_pb2.ExplainDashboardDecisionResponse()
            response_2 = pricing_v1_price_list_query_service_pb2.SummarizePriceListsResponse()
            response_3 = labeling_v1_labeling_task_lifecycle_service_pb2.TerminateLabelingTaskResponse()
            outgoing_0 = metrics_v1_metric_alert_admin_service_pb2.RepairMetricAlertRequest(
                context=request.context,
                metric_alert=metrics_v1_metrics_pb2.MetricAlert(
                    audit=common_v1_audit_pb2.AuditInfo(
                        created_by=request.labeling_task.audit.created_by,
                        etag=request.labeling_task.audit.etag,
                        updated_at=request.labeling_task.audit.updated_at
                    ),
                    owner=identity_v1_refs_pb2.UserRef(email=request.labeling_task.assignee.email)
                )
            )
            response_0 = await LabelingTaskWorkflowResumeLabelingTaskWorkflow0Adapter(
                deps.clients.metrics_metric_alert_admin,
                deps.settings.timeout
            )(outgoing_0)
            for item_1 in request.labeling_task.comments:
                outgoing_1 = metrics_v1_dashboard_validation_service_pb2.ExplainDashboardDecisionRequest(
                    context=request.context,
                    dashboard=metrics_v1_metrics_pb2.Dashboard(
                        audit=common_v1_audit_pb2.AuditInfo(created_at=item_1.created_at)
                    ),
                    details=metrics_v1_dashboard_validation_service_pb2.ExplainDashboardDecisionRequest.Details(
                        contact=common_v1_contact_pb2.ContactInfo(email=item_1.author_email)
                    )
                )
                response_1 = await deps.clients.metrics_dashboard_validation.ExplainDashboardDecision(
                    outgoing_1,
                    timeout=deps.settings.timeout
                )
            outgoing_2 = pricing_v1_price_list_query_service_pb2.SummarizePriceListsRequest(
                annotations=dict(request.annotations),
                context=request.context,
                details=pricing_v1_price_list_query_service_pb2.SummarizePriceListsRequest.Details(
                    filters=dict(response_1.dashboard.metadata)
                ),
                reason=response_0.metric_alert.block.reason
            )
            response_2 = await deps.clients.pricing_price_list_query.SummarizePriceLists(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            outgoing_3 = labeling_v1_labeling_task_lifecycle_service_pb2.TerminateLabelingTaskRequest(
                context=request.context,
                details=labeling_v1_labeling_task_lifecycle_service_pb2.TerminateLabelingTaskRequest.Details(
                    new_owner=identity_v1_refs_pb2.UserRef(user_id=response_0.metric_alert.owner.user_id),
                    notify_contact=common_v1_contact_pb2.ContactInfo(email=request.labeling_task.requester.email)
                ),
                labeling_task_id=request.labeling_task_id
            )
            method_name_3 = 'TerminateLabelingTask'
            response_3 = await getattr(
                deps.clients.labeling_labeling_task_lifecycle,
                method_name_3
            )(outgoing_3, timeout=deps.settings.timeout)
            returned_0_0 = response_0.metric_alert.audit.created_at
            if returned_0_0.ListFields():
                response.labeling_task.audit.created_at.MergeFrom(returned_0_0)
            returned_0_1 = response_0.result.status
            if returned_0_1:
                response.result.status = returned_0_1
            returned_2_0 = response_2.result.message
            if returned_2_0:
                response.outcome.message = returned_2_0
            returned_3_0 = response_3.labeling_task.sla.breached
            if returned_3_0:
                response.labeling_task.sla.breached = returned_3_0
            echoed_0 = request.labeling_task_id
            response.labeling_task.labeling_task_id = echoed_0
            echoed_1 = request.labeling_task.priority
            response.labeling_task.priority = echoed_1
            return response

    async def handle_retry_labeling_task_workflow(
        self,
        request: labeling_v1_labeling_task_workflow_service_pb2.RetryLabelingTaskWorkflowRequest
    ) -> labeling_v1_labeling_task_workflow_service_pb2.RetryLabelingTaskWorkflowResponse:
        """Retrys a labeling task."""
        deps = self.deps
        response = labeling_v1_labeling_task_workflow_service_pb2.RetryLabelingTaskWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('RetryLabelingTaskWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'RetryLabelingTaskWorkflow',
                {'reason': request.reason}
            )
            await deps.repository.save_labeling_task(request.context.tenant_id, request.labeling_task)
            response_0 = metrics_v1_metric_series_query_service_pb2.SuggestMetricSeriesesResponse()
            response_1 = labeling_v1_annotation_reporting_service_pb2.CountAnnotationTotalsResponse()
            response_2 = labeling_v1_labeling_task_query_service_pb2.LookupLabelingTaskResponse()
            response_3 = metrics_v1_metric_series_history_service_pb2.RecordMetricSeriesVersionResponse()
            outgoing_0 = metrics_v1_metric_series_query_service_pb2.SuggestMetricSeriesesRequest(
                context=request.context,
                filter=metrics_v1_metric_series_query_service_pb2.SuggestMetricSeriesesRequest.Filter(
                    created_after=request.labeling_task.sla.due_at,
                    owner_id=request.labeling_task.assignee.user_id
                )
            )
            outgoing_1 = labeling_v1_annotation_reporting_service_pb2.CountAnnotationTotalsRequest(
                context=request.context,
                filter=labeling_v1_annotation_reporting_service_pb2.CountAnnotationTotalsRequest.Filter(
                    created_after=request.labeling_task.audit.created_at
                )
            )
            outgoing_2 = labeling_v1_labeling_task_query_service_pb2.LookupLabelingTaskRequest(
                context=request.context,
                labeling_task_id=request.labeling_task.labeling_task_id
            )
            response_0, response_1, response_2 = await asyncio.gather(
                deps.clients.metrics_metric_series_query.SuggestMetricSerieses(
                    outgoing_0,
                    timeout=deps.settings.timeout
                ),
                deps.clients.labeling_annotation_reporting.CountAnnotationTotals(
                    outgoing_1,
                    timeout=deps.settings.timeout
                ),
                deps.clients.labeling_labeling_task_query.LookupLabelingTask(outgoing_2, timeout=deps.settings.timeout),
            )
            outgoing_3 = metrics_v1_metric_series_history_service_pb2.RecordMetricSeriesVersionRequest()
            outgoing_3.context.CopyFrom(request.context)
            outgoing_3.metric_series.owner.display_name = response_2.labeling_task.assignee.display_name
            outgoing_3.metric_series.audit.updated_at.CopyFrom(request.labeling_task.audit.updated_at)
            outgoing_3.metric_series.owner.user_id = request.labeling_task.assignee.user_id
            merged_3 = metrics_v1_metric_series_history_service_pb2.RecordMetricSeriesVersionRequest()
            merged_3.MergeFrom(outgoing_3)
            outgoing_3.CopyFrom(merged_3)
            response_3 = await deps.clients.metrics_metric_series_history.RecordMetricSeriesVersion(
                outgoing_3,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.correlation_id
            if returned_0_0:
                response.result.correlation_id = returned_0_0
            returned_1_0 = response_1.result.status
            if returned_1_0:
                response.outcome.status = returned_1_0
            returned_1_1 = response_1.result.message
            if returned_1_1:
                response.outcome.message = returned_1_1
            returned_2_0 = response_2.labeling_task.requester.name
            if returned_2_0.ListFields():
                response.labeling_task.requester.name.MergeFrom(returned_2_0)
            returned_3_0 = response_3.metric_series.owner.email
            if returned_3_0:
                response.labeling_task.requester.email = returned_3_0
            echoed_0 = request.labeling_task_id
            response.labeling_task.labeling_task_id = echoed_0
            echoed_1 = request.labeling_task.subject
            response.labeling_task.subject = echoed_1
            return response

    async def handle_signal_labeling_task_workflow(
        self,
        request: labeling_v1_labeling_task_workflow_service_pb2.SignalLabelingTaskWorkflowRequest
    ) -> labeling_v1_labeling_task_workflow_service_pb2.SignalLabelingTaskWorkflowResponse:
        """Signals a labeling task."""
        deps = self.deps
        response = labeling_v1_labeling_task_workflow_service_pb2.SignalLabelingTaskWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SignalLabelingTaskWorkflow', extra={'fields': {'initiated_by': request.details.initiated_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'SignalLabelingTaskWorkflow',
                {'initiated_by': request.details.initiated_by}
            )
            await deps.repository.save_labeling_task(request.context.tenant_id, request.labeling_task)
            response_0 = notifications_v1_notification_query_service_pb2.SummarizeNotificationsResponse()
            response_1 = labeling_v1_labeling_task_approval_service_pb2.ApproveLabelingTaskResponse()
            response_2 = labeling_v1_labeling_task_lifecycle_service_pb2.TerminateLabelingTaskResponse()
            outgoing_0 = notifications_v1_notification_query_service_pb2.SummarizeNotificationsRequest(
                annotations=dict(request.annotations),
                context=request.context,
                details=notifications_v1_notification_query_service_pb2.SummarizeNotificationsRequest.Details(
                    filters=dict(request.labeling_task.custom_fields)
                ),
                reason=request.reason
            )
            envelope_0 = AnyMessage()
            envelope_0.Pack(outgoing_0)
            outgoing_0 = notifications_v1_notification_query_service_pb2.SummarizeNotificationsRequest()
            if not envelope_0.Unpack(outgoing_0):
                raise ValueError("partner envelope contains the wrong request type")
            response_0 = await deps.clients.notifications_notification_query.SummarizeNotifications(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = labeling_v1_labeling_task_approval_service_pb2.ApproveLabelingTaskRequest(
                context=request.context,
                labeling_task=labeling_v1_labeling_pb2.LabelingTask(
                    sla=labeling_v1_labeling_pb2.LabelingTaskSla(paused_for=request.labeling_task.sla.paused_for)
                )
            )
            registered_1 = cast(
                labeling_v1_labeling_task_approval_service_pb2_grpc.LabelingTaskApprovalServiceStub,
                deps.clients.registry['acme.labeling.v1.LabelingTaskApprovalService']
            )
            response_1 = await registered_1.ApproveLabelingTask(outgoing_1, timeout=deps.settings.timeout)
            command_2 = LabelingTaskWorkflowSignalLabelingTaskWorkflow2Command(
                context=request.context,
                labeling_task_id=request.labeling_task.labeling_task_id,
                details_notify_contact_phone=request.labeling_task.requester.phone,
                details_new_owner_email=request.labeling_task.requester.email,
                details_notify_contact_email=response_1.labeling_task.requester.email,
                details_notify_contact_name=request.labeling_task.requester.name
            )
            outgoing_2 = to_labeling_task_workflow_signal_labeling_task_workflow2_command(command_2)
            response_2 = await deps.clients.labeling_labeling_task_lifecycle.TerminateLabelingTask(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.status
            if returned_0_0:
                response.result.status = returned_0_0
            returned_1_0 = response_1.result.status
            if returned_1_0:
                response.result.status = returned_1_0
            returned_1_1 = response_1.labeling_task.requester.email
            if returned_1_1:
                response.labeling_task.assignee.email = returned_1_1
            returned_2_0 = response_2.outcome.status
            if returned_2_0:
                response.result.status = returned_2_0
            returned_2_1 = response_2.result.details
            response.result.details.update(returned_2_1)
            echoed_0 = request.labeling_task_id
            response.labeling_task.labeling_task_id = echoed_0
            echoed_1 = request.labeling_task.status
            response.labeling_task.status = echoed_1
            return response

    async def handle_start_labeling_task_workflow(
        self,
        request: labeling_v1_labeling_task_workflow_service_pb2.StartLabelingTaskWorkflowRequest
    ) -> labeling_v1_labeling_task_workflow_service_pb2.StartLabelingTaskWorkflowResponse:
        """Starts a labeling task."""
        deps = self.deps
        response = labeling_v1_labeling_task_workflow_service_pb2.StartLabelingTaskWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('StartLabelingTaskWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'StartLabelingTaskWorkflow',
                {'reason': request.reason}
            )
            await deps.repository.save_labeling_task(request.context.tenant_id, request.labeling_task)
            response_0 = audit_v1_audit_event_query_service_pb2.BrowseAuditEventsResponse()
            response_1 = ratelimiting_v1_rate_limit_service_pb2.WatchRateLimitsResponse()
            requests_0: list[audit_v1_audit_event_query_service_pb2.BrowseAuditEventsRequest] = []
            for item_0 in request.labeling_task.comments:
                outgoing_0 = audit_v1_audit_event_query_service_pb2.BrowseAuditEventsRequest(
                    context=request.context,
                    filter=audit_v1_audit_event_query_service_pb2.BrowseAuditEventsRequest.Filter(
                        created_after=item_0.created_at,
                        owner_id=item_0.comment_id
                    )
                )
                requests_0.append(outgoing_0)
            replies_0 = await asyncio.gather(*(
                deps.clients.audit_audit_event_query.BrowseAuditEvents(
                    entry,
                    timeout=deps.settings.timeout
                ) for entry in requests_0
            ))
            if replies_0:
                response_0 = replies_0[-1]
            outgoing_1 = ratelimiting_v1_rate_limit_service_pb2.WatchRateLimitsRequest(
                context=request.context,
                subscriber=common_v1_contact_pb2.ContactInfo(
                    email=request.labeling_task.requester.email,
                    name=request.labeling_task.requester.name,
                    phone=request.labeling_task.requester.phone,
                    preferred_channel=request.details.notify.preferred_channel
                )
            )
            async for chunk_1 in deps.clients.ratelimiting_rate_limit.WatchRateLimits(
                outgoing_1,
                timeout=deps.settings.timeout
            ):
                response_1 = chunk_1
            echoed_0 = request.labeling_task_id
            response.labeling_task.labeling_task_id = echoed_0
            echoed_1 = request.labeling_task.status
            response.labeling_task.status = echoed_1
            return response
