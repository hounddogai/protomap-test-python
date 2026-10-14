"""Routes pipeline runs through approval, with escalation and delegation."""

from __future__ import annotations

from collections.abc import AsyncIterator
from collections.abc import Awaitable
from collections.abc import Callable
from functools import partial
import asyncio
import logging

from google.protobuf.any_pb2 import Any as AnyMessage
from google.protobuf.json_format import MessageToDict
from google.protobuf.json_format import ParseDict
import grpc

from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.featurestore.v1 import entity_approval_service_pb2 as featurestore_v1_entity_approval_service_pb2
from acme.featurestore.v1 import entity_sync_service_pb2 as featurestore_v1_entity_sync_service_pb2
from acme.featurestore.v1 import featurestore_pb2 as featurestore_v1_featurestore_pb2
from acme.fulfillment.v1 import fulfillment_query_service_pb2 as fulfillment_v1_fulfillment_query_service_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.lineage.v1 import impact_reporting_service_pb2 as lineage_v1_impact_reporting_service_pb2
from acme.metrics.v1 import dashboard_validation_service_pb2 as metrics_v1_dashboard_validation_service_pb2
from acme.metrics.v1 import metric_alert_history_service_pb2 as metrics_v1_metric_alert_history_service_pb2
from acme.metrics.v1 import metric_alert_notification_service_pb2 as metrics_v1_metric_alert_notification_service_pb2
from acme.metrics.v1 import metrics_pb2 as metrics_v1_metrics_pb2
from acme.notifications.v1 import notification_service_pb2 as notifications_v1_notification_service_pb2
from acme.notifications.v1 import notifications_pb2 as notifications_v1_notifications_pb2
from acme.pipelines.v1 import pipeline_approval_service_pb2 as pipelines_v1_pipeline_approval_service_pb2
from acme.pipelines.v1 import pipeline_reporting_service_pb2 as pipelines_v1_pipeline_reporting_service_pb2
from acme.pipelines.v1 import pipeline_run_approval_service_pb2 as pipelines_v1_pipeline_run_approval_service_pb2
from acme.pipelines.v1 import (
    pipeline_run_approval_service_pb2_grpc as pipelines_v1_pipeline_run_approval_service_pb2_grpc,
)
from acme.pipelines.v1 import pipeline_run_lifecycle_service_pb2 as pipelines_v1_pipeline_run_lifecycle_service_pb2
from acme.pipelines.v1 import pipeline_run_validation_service_pb2 as pipelines_v1_pipeline_run_validation_service_pb2
from acme.pipelines.v1 import pipeline_step_export_service_pb2 as pipelines_v1_pipeline_step_export_service_pb2
from acme.pipelines.v1 import pipeline_validation_service_pb2 as pipelines_v1_pipeline_validation_service_pb2
from acme.pipelines.v1 import pipelines_pb2 as pipelines_v1_pipelines_pb2
from acme.search.v1 import search_index_validation_service_pb2 as search_v1_search_index_validation_service_pb2
from acme.search.v1 import search_pb2 as search_v1_search_pb2
from acme.venues.v1 import venue_query_service_pb2 as venues_v1_venue_query_service_pb2

from acme_data.domains.pipelines import hooks
from acme_data.domains.pipelines.adapters import PipelineRunApprovalListPendingPipelineRuns1Adapter
from acme_data.domains.pipelines.adapters import PipelineRunApprovalListPendingPipelineRuns1Port
from acme_data.domains.pipelines.dependencies import Dependencies
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import run_steps
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class PipelineRunApprovalServicer(
    pipelines_v1_pipeline_run_approval_service_pb2_grpc.PipelineRunApprovalServiceServicer
):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    async def ApprovePipelineRun(
        self, request: pipelines_v1_pipeline_run_approval_service_pb2.ApprovePipelineRunRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_run_approval_service_pb2.ApprovePipelineRunResponse:
        """Approves a pipeline run."""
        return await self.handle_approve_pipeline_run(request)

    @rpc_errors
    async def CommentPipelineRunApproval(
        self, request: pipelines_v1_pipeline_run_approval_service_pb2.CommentPipelineRunApprovalRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_run_approval_service_pb2.CommentPipelineRunApprovalResponse:
        """Comments a pipeline run."""
        return await self.handle_comment_pipeline_run_approval(request)

    @rpc_errors
    async def DelegatePipelineRunApproval(
        self, request: pipelines_v1_pipeline_run_approval_service_pb2.DelegatePipelineRunApprovalRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_run_approval_service_pb2.DelegatePipelineRunApprovalResponse:
        """Delegates a pipeline run."""
        return await self.handle_delegate_pipeline_run_approval(request)

    @rpc_errors
    async def EscalatePipelineRun(
        self, request: pipelines_v1_pipeline_run_approval_service_pb2.EscalatePipelineRunRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_run_approval_service_pb2.EscalatePipelineRunResponse:
        """Escalates a pipeline run."""
        return await self.handle_escalate_pipeline_run(request)

    @rpc_errors
    @retry_transient
    async def ListPendingPipelineRuns(
        self, request: pipelines_v1_pipeline_run_approval_service_pb2.ListPendingPipelineRunsRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_run_approval_service_pb2.ListPendingPipelineRunsResponse:
        """Lists pipeline runs a page at a time."""
        return await self.handle_list_pending_pipeline_runs(request)

    @rpc_errors
    async def RecallPipelineRun(
        self, request: pipelines_v1_pipeline_run_approval_service_pb2.RecallPipelineRunRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_run_approval_service_pb2.RecallPipelineRunResponse:
        """Recalls a pipeline run."""
        return await self.handle_recall_pipeline_run(request)

    @rpc_errors
    async def RejectPipelineRun(
        self, request: pipelines_v1_pipeline_run_approval_service_pb2.RejectPipelineRunRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_run_approval_service_pb2.RejectPipelineRunResponse:
        """Rejects a pipeline run."""
        return await self.handle_reject_pipeline_run(request)

    @rpc_errors
    async def SubmitPipelineRun(
        self, request: pipelines_v1_pipeline_run_approval_service_pb2.SubmitPipelineRunRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_run_approval_service_pb2.SubmitPipelineRunResponse:
        """Submits a pipeline run."""
        return await self.handle_submit_pipeline_run(request)

    async def handle_approve_pipeline_run(
        self,
        request: pipelines_v1_pipeline_run_approval_service_pb2.ApprovePipelineRunRequest
    ) -> pipelines_v1_pipeline_run_approval_service_pb2.ApprovePipelineRunResponse:
        """Approves a pipeline run."""
        deps = self.deps
        response = pipelines_v1_pipeline_run_approval_service_pb2.ApprovePipelineRunResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ApprovePipelineRun', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'ApprovePipelineRun', {'reason': request.reason})
            await deps.repository.save_pipeline_run(request.context.tenant_id, request.pipeline_run)
            response_0 = pipelines_v1_pipeline_run_validation_service_pb2.PreviewPipelineRunResponse()
            async for item_0 in async_messages(request.pipeline_run.history):
                outgoing_0 = pipelines_v1_pipeline_run_validation_service_pb2.PreviewPipelineRunRequest(
                    context=request.context,
                    pipeline_run=pipelines_v1_pipelines_pb2.PipelineRun(
                        history=[pipelines_v1_pipelines_pb2.PipelineRunStatusChange(changed_at=item_0.changed_at)]
                    )
                )
                response_0 = await deps.clients.pipelines_pipeline_run_validation.PreviewPipelineRun(
                    outgoing_0,
                    timeout=deps.settings.timeout
                )
            echoed_0 = request.pipeline_run_id
            response.pipeline_run.pipeline_run_id = echoed_0
            echoed_1 = request.pipeline_run.custom_fields
            response.pipeline_run.custom_fields.update(echoed_1)
            return response

    async def handle_comment_pipeline_run_approval(
        self,
        request: pipelines_v1_pipeline_run_approval_service_pb2.CommentPipelineRunApprovalRequest
    ) -> pipelines_v1_pipeline_run_approval_service_pb2.CommentPipelineRunApprovalResponse:
        """Comments a pipeline run."""
        deps = self.deps
        response = pipelines_v1_pipeline_run_approval_service_pb2.CommentPipelineRunApprovalResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CommentPipelineRunApproval', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'CommentPipelineRunApproval',
                {'reason': request.reason}
            )
            await deps.repository.save_pipeline_run(request.context.tenant_id, request.pipeline_run)
            response_0 = lineage_v1_impact_reporting_service_pb2.StreamImpactMetricsResponse()
            response_1 = featurestore_v1_entity_sync_service_pb2.PushEntityResponse()
            response_2 = metrics_v1_metric_alert_notification_service_pb2.UnsubscribeMetricAlertUpdatesResponse()
            outgoing_0 = lineage_v1_impact_reporting_service_pb2.StreamImpactMetricsRequest(
                context=request.context,
                subscriber=common_v1_contact_pb2.ContactInfo(
                    email=request.pipeline_run.requester.email,
                    phone=request.pipeline_run.requester.phone,
                    preferred_channel=request.pipeline_run.requester.preferred_channel
                )
            )
            async for chunk_0 in deps.clients.lineage_impact_reporting.StreamImpactMetrics(
                outgoing_0,
                timeout=deps.settings.timeout
            ):
                response_0 = chunk_0
            outgoing_1 = featurestore_v1_entity_sync_service_pb2.PushEntityRequest()
            outgoing_1.context.CopyFrom(request.context)
            outgoing_1.entity.audit.etag = request.pipeline_run.audit.etag
            outgoing_1.entity.relationship_manager.display_name = request.pipeline_run.assignee.display_name
            outgoing_1.entity.audit.created_by = request.pipeline_run.audit.created_by
            merged_1 = featurestore_v1_entity_sync_service_pb2.PushEntityRequest()
            merged_1.MergeFrom(outgoing_1)
            outgoing_1.CopyFrom(merged_1)
            response_1 = await deps.clients.featurestore_entity_sync.PushEntity(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = metrics_v1_metric_alert_notification_service_pb2.UnsubscribeMetricAlertUpdatesRequest(
                context=request.context,
                details=metrics_v1_metric_alert_notification_service_pb2.UnsubscribeMetricAlertUpdatesRequest.Details(
                    recipient=common_v1_contact_pb2.ContactInfo(
                        email=request.details.approver.email,
                        phone=response_1.entity.contact.phone,
                        preferred_channel=response_1.entity.contact.preferred_channel
                    )
                )
            )
            envelope_2 = AnyMessage()
            envelope_2.Pack(outgoing_2)
            outgoing_2 = metrics_v1_metric_alert_notification_service_pb2.UnsubscribeMetricAlertUpdatesRequest()
            if not envelope_2.Unpack(outgoing_2):
                raise ValueError("partner envelope contains the wrong request type")
            response_2 = await deps.clients.metrics_metric_alert_notification.UnsubscribeMetricAlertUpdates(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            returned_1_0 = response_1.entity.name
            if returned_1_0.ListFields():
                response.pipeline_run.requester.name.MergeFrom(returned_1_0)
            returned_2_0 = response_2.outcome.status
            if returned_2_0:
                response.outcome.status = returned_2_0
            returned_2_1 = response_2.metric_alert.owner.email
            if returned_2_1:
                response.pipeline_run.assignee.email = returned_2_1
            echoed_0 = request.pipeline_run_id
            response.pipeline_run.pipeline_run_id = echoed_0
            echoed_1 = request.pipeline_run.subject
            response.pipeline_run.subject = echoed_1
            return response

    async def handle_delegate_pipeline_run_approval(
        self,
        request: pipelines_v1_pipeline_run_approval_service_pb2.DelegatePipelineRunApprovalRequest
    ) -> pipelines_v1_pipeline_run_approval_service_pb2.DelegatePipelineRunApprovalResponse:
        """Delegates a pipeline run."""
        deps = self.deps
        response = pipelines_v1_pipeline_run_approval_service_pb2.DelegatePipelineRunApprovalResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('DelegatePipelineRunApproval', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'DelegatePipelineRunApproval',
                {'reason': request.reason}
            )
            await deps.repository.save_pipeline_run(request.context.tenant_id, request.pipeline_run)
            response_0 = pipelines_v1_pipeline_step_export_service_pb2.StreamPipelineStepExportResponse()
            response_1 = pipelines_v1_pipeline_validation_service_pb2.ScorePipelineResponse()
            response_2 = metrics_v1_dashboard_validation_service_pb2.PreviewDashboardResponse()
            outgoing_1 = pipelines_v1_pipeline_validation_service_pb2.ScorePipelineRequest(
                context=request.context,
                pipeline=pipelines_v1_pipelines_pb2.Pipeline(
                    audit=common_v1_audit_pb2.AuditInfo(etag=request.pipeline_run.audit.etag),
                    organizer=identity_v1_refs_pb2.UserRef(email=request.details.approver.email)
                )
            )
            outgoing_2 = metrics_v1_dashboard_validation_service_pb2.PreviewDashboardRequest(
                context=request.context,
                details=metrics_v1_dashboard_validation_service_pb2.PreviewDashboardRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(name=request.pipeline_run.requester.name)
                )
            )
            response_1, response_2 = await asyncio.gather(
                deps.clients.pipelines_pipeline_validation.ScorePipeline(outgoing_1, timeout=deps.settings.timeout),
                deps.clients.metrics_dashboard_validation.PreviewDashboard(outgoing_2, timeout=deps.settings.timeout),
            )
            outgoing_0 = pipelines_v1_pipeline_step_export_service_pb2.StreamPipelineStepExportRequest(
                context=request.context,
                filter=pipelines_v1_pipeline_step_export_service_pb2.StreamPipelineStepExportRequest.Filter(
                    created_after=request.pipeline_run.customer.starts_at
                )
            )
            async for chunk_0 in deps.clients.pipelines_pipeline_step_export.StreamPipelineStepExport(
                outgoing_0,
                timeout=deps.settings.timeout
            ):
                response_0 = chunk_0
            returned_1_0 = response_1.result.correlation_id
            if returned_1_0:
                response.result.correlation_id = returned_1_0
            returned_2_0 = response_2.dashboard.counterparty.display_name
            if returned_2_0:
                response.pipeline_run.assignee.display_name = returned_2_0
            returned_2_1 = response_2.result.reference_ids
            response.result.reference_ids.extend(returned_2_1)
            echoed_0 = request.pipeline_run_id
            response.pipeline_run.pipeline_run_id = echoed_0
            echoed_1 = request.details.effective_at
            response.outcome.effective_at.CopyFrom(echoed_1)
            return response

    async def handle_escalate_pipeline_run(
        self,
        request: pipelines_v1_pipeline_run_approval_service_pb2.EscalatePipelineRunRequest
    ) -> pipelines_v1_pipeline_run_approval_service_pb2.EscalatePipelineRunResponse:
        """Escalates a pipeline run."""
        deps = self.deps
        response = pipelines_v1_pipeline_run_approval_service_pb2.EscalatePipelineRunResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('EscalatePipelineRun', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'EscalatePipelineRun', {'reason': request.reason})
            await deps.repository.save_pipeline_run(request.context.tenant_id, request.pipeline_run)
            response_0 = pipelines_v1_pipeline_reporting_service_pb2.StreamPipelineMetricsResponse()
            response_1 = notifications_v1_notification_service_pb2.CreateNotificationResponse()
            outgoing_0 = pipelines_v1_pipeline_reporting_service_pb2.StreamPipelineMetricsRequest(
                context=request.context,
                subscriber=common_v1_contact_pb2.ContactInfo(
                    email=request.pipeline_run.assignee.email,
                    phone=request.pipeline_run.requester.phone,
                    preferred_channel=request.pipeline_run.requester.preferred_channel
                )
            )
            async for chunk_0 in deps.clients.pipelines_pipeline_reporting.StreamPipelineMetrics(
                outgoing_0,
                timeout=deps.settings.timeout
            ):
                response_0 = chunk_0
            outgoing_1 = notifications_v1_notification_service_pb2.CreateNotificationRequest(
                context=request.context,
                notification=notifications_v1_notifications_pb2.Notification(
                    assignee=identity_v1_refs_pb2.UserRef(user_id=request.pipeline_run.assignee.user_id)
                )
            )
            response_1 = await hooks.pipeline_run_approval_escalate_pipeline_run1(
                deps.clients.notifications_notification,
                outgoing_1,
                deps.settings.timeout
            )
            returned_1_0 = response_1.notification.customer.display_name
            if returned_1_0:
                response.pipeline_run.assignee.display_name = returned_1_0
            echoed_0 = request.pipeline_run_id
            response.pipeline_run.pipeline_run_id = echoed_0
            echoed_1 = request.pipeline_run.priority
            response.pipeline_run.priority = echoed_1
            return response

    async def handle_list_pending_pipeline_runs(
        self,
        request: pipelines_v1_pipeline_run_approval_service_pb2.ListPendingPipelineRunsRequest
    ) -> pipelines_v1_pipeline_run_approval_service_pb2.ListPendingPipelineRunsResponse:
        """Lists pipeline runs a page at a time."""
        deps = self.deps
        response = pipelines_v1_pipeline_run_approval_service_pb2.ListPendingPipelineRunsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ListPendingPipelineRuns', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ListPendingPipelineRuns',
                {'order_by': request.order_by}
            )
            response_0 = metrics_v1_metric_alert_history_service_pb2.RevertMetricAlertResponse()
            response_1 = featurestore_v1_entity_sync_service_pb2.SyncEntitiesResponse()
            outgoing_0 = metrics_v1_metric_alert_history_service_pb2.RevertMetricAlertRequest(
                context=request.context,
                metric_alert=metrics_v1_metrics_pb2.MetricAlert(
                    audit=common_v1_audit_pb2.AuditInfo(updated_at=request.filter.created_after),
                    owner=identity_v1_refs_pb2.UserRef(
                        email=request.context.actor.email,
                        user_id=request.context.actor.user_id
                    )
                )
            )
            response_0 = await deps.clients.metrics_metric_alert_history.RevertMetricAlert(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = featurestore_v1_entity_sync_service_pb2.SyncEntitiesRequest(
                context=request.context,
                entity=featurestore_v1_featurestore_pb2.Entity(
                    audit=common_v1_audit_pb2.AuditInfo(
                        etag=response_0.metric_alert.audit.etag,
                        updated_at=response_0.metric_alert.audit.updated_at
                    )
                )
            )
            port_1: PipelineRunApprovalListPendingPipelineRuns1Port = PipelineRunApprovalListPendingPipelineRuns1Adapter(
                deps.clients.featurestore_entity_sync,
                deps.settings.timeout
            )
            response_1 = await port_1.execute(outgoing_1)
            returned_0_0 = response_0.metric_alert.priority
            returned_0_0_part_0 = response.pipeline_runs.add()
            if returned_0_0:
                returned_0_0_part_0.priority = returned_0_0
            returned_0_1 = response_0.metric_alert.audit.updated_by
            returned_0_1_part_0 = response.pipeline_runs.add()
            if returned_0_1:
                returned_0_1_part_0.audit.updated_by = returned_0_1
            returned_1_0 = response_1.entity.contact.preferred_channel
            returned_1_0_part_0 = response.pipeline_runs.add()
            if returned_1_0:
                returned_1_0_part_0.requester.preferred_channel = returned_1_0
            return response

    async def handle_recall_pipeline_run(
        self,
        request: pipelines_v1_pipeline_run_approval_service_pb2.RecallPipelineRunRequest
    ) -> pipelines_v1_pipeline_run_approval_service_pb2.RecallPipelineRunResponse:
        """Recalls a pipeline run."""
        deps = self.deps
        response = pipelines_v1_pipeline_run_approval_service_pb2.RecallPipelineRunResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('RecallPipelineRun', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'RecallPipelineRun', {'reason': request.reason})
            await deps.repository.save_pipeline_run(request.context.tenant_id, request.pipeline_run)
            response_0 = pipelines_v1_pipeline_run_lifecycle_service_pb2.ReinstatePipelineRunResponse()
            response_1 = venues_v1_venue_query_service_pb2.FindVenuesResponse()
            outgoing_0 = pipelines_v1_pipeline_run_lifecycle_service_pb2.ReinstatePipelineRunRequest(
                context=request.context,
                details=pipelines_v1_pipeline_run_lifecycle_service_pb2.ReinstatePipelineRunRequest.Details(
                    notify_contact=common_v1_contact_pb2.ContactInfo(email=request.details.approver.email)
                ),
                pipeline_run_id=request.pipeline_run.pipeline_run_id
            )
            steps_0 = [
                partial(
                    deps.clients.pipelines_pipeline_run_lifecycle.ReinstatePipelineRun,
                    outgoing_0,
                    timeout=deps.settings.timeout
                )
            ]
            results_0 = await run_steps(steps_0)
            response_0 = results_0[-1]
            for item_1 in request.pipeline_run.comments:
                outgoing_1 = venues_v1_venue_query_service_pb2.FindVenuesRequest(
                    context=request.context,
                    filter=venues_v1_venue_query_service_pb2.FindVenuesRequest.Filter(
                        created_after=item_1.created_at,
                        owner_id=item_1.comment_id
                    )
                )
                response_1 = await deps.clients.venues_venue_query.FindVenues(outgoing_1, timeout=deps.settings.timeout)
            returned_0_0 = response_0.result.correlation_id
            if returned_0_0:
                response.result.correlation_id = returned_0_0
            returned_0_1 = response_0.outcome.message
            if returned_0_1:
                response.outcome.message = returned_0_1
            echoed_0 = request.pipeline_run_id
            response.pipeline_run.pipeline_run_id = echoed_0
            echoed_1 = request.pipeline_run.priority
            response.pipeline_run.priority = echoed_1
            return response

    async def handle_reject_pipeline_run(
        self,
        request: pipelines_v1_pipeline_run_approval_service_pb2.RejectPipelineRunRequest
    ) -> pipelines_v1_pipeline_run_approval_service_pb2.RejectPipelineRunResponse:
        """Rejects a pipeline run."""
        deps = self.deps
        response = pipelines_v1_pipeline_run_approval_service_pb2.RejectPipelineRunResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('RejectPipelineRun', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'RejectPipelineRun', {'reason': request.reason})
            await deps.repository.save_pipeline_run(request.context.tenant_id, request.pipeline_run)
            response_0 = fulfillment_v1_fulfillment_query_service_pb2.ExportFulfillmentsResponse()
            response_1 = featurestore_v1_entity_approval_service_pb2.CommentEntityApprovalResponse()
            response_2 = search_v1_search_index_validation_service_pb2.LintSearchIndexesResponse()
            response_3 = search_v1_search_index_validation_service_pb2.ExplainSearchIndexDecisionResponse()
            for item_0 in request.pipeline_run.history:
                outgoing_0 = fulfillment_v1_fulfillment_query_service_pb2.ExportFulfillmentsRequest(
                    context=request.context,
                    filter=fulfillment_v1_fulfillment_query_service_pb2.ExportFulfillmentsRequest.Filter(
                        created_after=item_0.changed_at,
                        labels=dict(request.pipeline_run.custom_fields),
                        owner_id=request.pipeline_run.customer.pipeline_id
                    )
                )
                async for result_0 in deps.clients.fulfillment_fulfillment_query.ExportFulfillments(
                    outgoing_0,
                    timeout=deps.settings.timeout
                ):
                    response_0 = result_0
            outgoing_1 = featurestore_v1_entity_approval_service_pb2.CommentEntityApprovalRequest(
                context=request.context,
                entity=featurestore_v1_featurestore_pb2.Entity(
                    contact=common_v1_contact_pb2.ContactInfo(name=request.pipeline_run.requester.name),
                    relationship_manager=identity_v1_refs_pb2.UserRef(
                        display_name=request.pipeline_run.customer.display_name,
                        email=request.details.approver.email
                    )
                )
            )
            response_1 = await deps.clients.featurestore_entity_approval.CommentEntityApproval(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = search_v1_search_index_validation_service_pb2.LintSearchIndexesRequest(
                context=request.context,
                search_index=search_v1_search_pb2.SearchIndex(
                    owner=identity_v1_refs_pb2.UserRef(display_name=request.pipeline_run.customer.display_name)
                )
            )
            method_name_2 = 'LintSearchIndexes'
            response_2 = await getattr(
                deps.clients.search_search_index_validation,
                method_name_2
            )(outgoing_2, timeout=deps.settings.timeout)
            outgoing_3 = search_v1_search_index_validation_service_pb2.ExplainSearchIndexDecisionRequest()
            outgoing_3.context.CopyFrom(request.context)
            if response_2.search_index.WhichOneof('locator') == 'address':
                outgoing_3.search_index.address.country_code = response_2.search_index.address.country_code
            outgoing_3.search_index.audit.created_by = request.pipeline_run.audit.created_by
            outgoing_3.search_index.owner.email = response_2.search_index.owner.email
            outgoing_3.search_index.owner.display_name = request.pipeline_run.assignee.display_name
            response_3 = await deps.clients.search_search_index_validation.ExplainSearchIndexDecision(
                outgoing_3,
                timeout=deps.settings.timeout
            )
            returned_1_0 = response_1.result.reference_ids
            response.result.reference_ids.extend(returned_1_0)
            returned_2_0 = response_2.result.message
            if returned_2_0:
                response.result.message = returned_2_0
            returned_3_0 = response_3.outcome.message
            if returned_3_0:
                response.outcome.message = returned_3_0
            echoed_0 = request.pipeline_run_id
            response.pipeline_run.pipeline_run_id = echoed_0
            echoed_1 = request.pipeline_run.status
            response.pipeline_run.status = echoed_1
            return response

    async def handle_submit_pipeline_run(
        self,
        request: pipelines_v1_pipeline_run_approval_service_pb2.SubmitPipelineRunRequest
    ) -> pipelines_v1_pipeline_run_approval_service_pb2.SubmitPipelineRunResponse:
        """Submits a pipeline run."""
        deps = self.deps
        response = pipelines_v1_pipeline_run_approval_service_pb2.SubmitPipelineRunResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SubmitPipelineRun', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'SubmitPipelineRun', {'reason': request.reason})
            await deps.repository.save_pipeline_run(request.context.tenant_id, request.pipeline_run)
            response_0 = pipelines_v1_pipeline_approval_service_pb2.SubmitPipelineResponse()
            outgoing_0 = pipelines_v1_pipeline_approval_service_pb2.SubmitPipelineRequest(
                context=request.context,
                pipeline=pipelines_v1_pipelines_pb2.Pipeline(
                    participants=[
                        pipelines_v1_pipelines_pb2.PipelineParticipant(
                            contact=common_v1_contact_pb2.ContactInfo(email=request.pipeline_run.requester.email)
                        )
                    ]
                )
            )
            document_0 = MessageToDict(outgoing_0, preserving_proto_field_name=True)
            outgoing_0 = ParseDict(document_0, pipelines_v1_pipeline_approval_service_pb2.SubmitPipelineRequest())
            response_0 = await deps.clients.pipelines_pipeline_approval.SubmitPipeline(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.pipeline.organizer.display_name
            if returned_0_0:
                response.pipeline_run.assignee.display_name = returned_0_0
            returned_0_1 = response_0.pipeline.audit.updated_by
            if returned_0_1:
                response.pipeline_run.audit.updated_by = returned_0_1
            echoed_0 = request.pipeline_run_id
            response.pipeline_run.pipeline_run_id = echoed_0
            echoed_1 = request.pipeline_run.custom_fields
            response.pipeline_run.custom_fields.update(echoed_1)
            return response
