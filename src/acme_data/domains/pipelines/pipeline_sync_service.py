"""Keeps pipelines in step with the systems of record in other regions."""

from __future__ import annotations

from collections.abc import AsyncIterator
from collections.abc import Awaitable
from collections.abc import Callable
from dataclasses import dataclass
from functools import partial
from typing import cast
import asyncio
import logging

from google.protobuf.any_pb2 import Any as AnyMessage
from google.protobuf.json_format import MessageToDict
from google.protobuf.json_format import MessageToJson
from google.protobuf.json_format import Parse
from google.protobuf.json_format import ParseDict
import grpc

from acme.anomalies.v1 import anomalies_pb2 as anomalies_v1_anomalies_pb2
from acme.anomalies.v1 import anomaly_workflow_service_pb2 as anomalies_v1_anomaly_workflow_service_pb2
from acme.assets.v1 import fixed_asset_query_service_pb2 as assets_v1_fixed_asset_query_service_pb2
from acme.authorization.v1 import access_policy_service_pb2 as authorization_v1_access_policy_service_pb2
from acme.authorization.v1 import authorization_pb2 as authorization_v1_authorization_pb2
from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.expenses.v1 import expense_report_query_service_pb2 as expenses_v1_expense_report_query_service_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.identity.v1 import user_service_pb2 as identity_v1_user_service_pb2
from acme.lineage.v1 import impact_lifecycle_service_pb2 as lineage_v1_impact_lifecycle_service_pb2
from acme.lineage.v1 import lineage_node_approval_service_pb2 as lineage_v1_lineage_node_approval_service_pb2
from acme.lineage.v1 import lineage_pb2 as lineage_v1_lineage_pb2
from acme.metrics.v1 import metric_alert_query_service_pb2 as metrics_v1_metric_alert_query_service_pb2
from acme.pipelines.v1 import pipeline_query_service_pb2 as pipelines_v1_pipeline_query_service_pb2
from acme.pipelines.v1 import pipeline_run_calculation_service_pb2 as pipelines_v1_pipeline_run_calculation_service_pb2
from acme.pipelines.v1 import pipeline_run_import_service_pb2 as pipelines_v1_pipeline_run_import_service_pb2
from acme.pipelines.v1 import (
    pipeline_step_calculation_service_pb2 as pipelines_v1_pipeline_step_calculation_service_pb2,
)
from acme.pipelines.v1 import pipeline_step_validation_service_pb2 as pipelines_v1_pipeline_step_validation_service_pb2
from acme.pipelines.v1 import pipeline_sync_service_pb2 as pipelines_v1_pipeline_sync_service_pb2
from acme.pipelines.v1 import pipeline_sync_service_pb2_grpc as pipelines_v1_pipeline_sync_service_pb2_grpc
from acme.pipelines.v1 import pipeline_validation_service_pb2 as pipelines_v1_pipeline_validation_service_pb2
from acme.pipelines.v1 import pipelines_pb2 as pipelines_v1_pipelines_pb2

from acme_data.domains.pipelines import hooks
from acme_data.domains.pipelines.adapters import PipelineSyncReconcilePipelines0Adapter
from acme_data.domains.pipelines.adapters import PipelineSyncReconcilePipelines0Port
from acme_data.domains.pipelines.adapters import PipelineSyncResolvePipelineConflict1Adapter
from acme_data.domains.pipelines.dependencies import Dependencies
from acme_data.domains.pipelines.models import PipelineSyncPullPipelines3Command
from acme_data.domains.pipelines.models import to_pipeline_sync_pull_pipelines3_command
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import run_steps
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_id
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


@dataclass(slots=True)
class PipelineSyncServicer(pipelines_v1_pipeline_sync_service_pb2_grpc.PipelineSyncServiceServicer):
    deps: Dependencies

    @rpc_errors
    @retry_transient
    async def GetPipelineSyncState(
        self, request: pipelines_v1_pipeline_sync_service_pb2.GetPipelineSyncStateRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_sync_service_pb2.GetPipelineSyncStateResponse:
        """Returns a pipeline."""
        return await self.handle_get_pipeline_sync_state(request)

    @rpc_errors
    @retry_transient
    async def ListPipelineConflicts(
        self, request: pipelines_v1_pipeline_sync_service_pb2.ListPipelineConflictsRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_sync_service_pb2.ListPipelineConflictsResponse:
        """Lists pipelines a page at a time."""
        return await self.handle_list_pipeline_conflicts(request)

    @rpc_errors
    async def PullPipelines(
        self, request: pipelines_v1_pipeline_sync_service_pb2.PullPipelinesRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_sync_service_pb2.PullPipelinesResponse:
        """Pulls a pipeline."""
        return await self.handle_pull_pipelines(request)

    @rpc_errors
    async def PushPipeline(
        self, request: pipelines_v1_pipeline_sync_service_pb2.PushPipelineRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_sync_service_pb2.PushPipelineResponse:
        """Pushs a pipeline."""
        return await self.handle_push_pipeline(request)

    @rpc_errors
    async def ReconcilePipelines(
        self, request: pipelines_v1_pipeline_sync_service_pb2.ReconcilePipelinesRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_sync_service_pb2.ReconcilePipelinesResponse:
        """Reconciles a pipeline."""
        return await self.handle_reconcile_pipelines(request)

    @rpc_errors
    async def ResolvePipelineConflict(
        self, request: pipelines_v1_pipeline_sync_service_pb2.ResolvePipelineConflictRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_sync_service_pb2.ResolvePipelineConflictResponse:
        """Resolves a pipeline."""
        return await self.handle_resolve_pipeline_conflict(request)

    @stream_errors
    async def StreamPipelineChanges(
        self, requests: AsyncIterator[
            pipelines_v1_pipeline_sync_service_pb2.StreamPipelineChangesRequest
        ], context: grpc.aio.ServicerContext,
    ) -> AsyncIterator[pipelines_v1_pipeline_sync_service_pb2.StreamPipelineChangesResponse]:
        """Exchanges changes of pipelines with a peer."""
        async for request in requests:
            yield await self.handle_stream_pipeline_changes(request)

    @rpc_errors
    async def SyncPipelines(
        self, request: pipelines_v1_pipeline_sync_service_pb2.SyncPipelinesRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_sync_service_pb2.SyncPipelinesResponse:
        """Syncs a pipeline."""
        return await self.handle_sync_pipelines(request)

    async def handle_get_pipeline_sync_state(
        self,
        request: pipelines_v1_pipeline_sync_service_pb2.GetPipelineSyncStateRequest
    ) -> pipelines_v1_pipeline_sync_service_pb2.GetPipelineSyncStateResponse:
        """Returns a pipeline."""
        deps = self.deps
        response = pipelines_v1_pipeline_sync_service_pb2.GetPipelineSyncStateResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('GetPipelineSyncState', extra={'fields': {'pipeline_id': request.pipeline_id}})
            await deps.repository.audit(
                request.context.tenant_id,
                'GetPipelineSyncState',
                {'pipeline_id': request.pipeline_id}
            )
            response_0 = pipelines_v1_pipeline_run_calculation_service_pb2.ExplainPipelineRunCalculationResponse()
            outgoing_0 = pipelines_v1_pipeline_run_calculation_service_pb2.ExplainPipelineRunCalculationRequest(
                context=request.context,
                details=pipelines_v1_pipeline_run_calculation_service_pb2.ExplainPipelineRunCalculationRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(email=request.context.actor.email)
                )
            )
            response_0 = await deps.clients.pipelines_pipeline_run_calculation.ExplainPipelineRunCalculation(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.pipeline_run.customer.pipeline_id
            if returned_0_0:
                response.pipeline.pipeline_id = returned_0_0
            returned_0_1 = response_0.pipeline_run.assignee.email
            if returned_0_1:
                response.pipeline.organizer.email = returned_0_1
            return response

    async def handle_list_pipeline_conflicts(
        self,
        request: pipelines_v1_pipeline_sync_service_pb2.ListPipelineConflictsRequest
    ) -> pipelines_v1_pipeline_sync_service_pb2.ListPipelineConflictsResponse:
        """Lists pipelines a page at a time."""
        deps = self.deps
        response = pipelines_v1_pipeline_sync_service_pb2.ListPipelineConflictsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ListPipelineConflicts', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ListPipelineConflicts',
                {'order_by': request.order_by}
            )
            response_0 = identity_v1_user_service_pb2.GetUserResponse()
            response_1 = pipelines_v1_pipeline_run_import_service_pb2.MapPipelineRunImportColumnsResponse()
            outgoing_0 = identity_v1_user_service_pb2.GetUserRequest(
                context=request.context,
                user_id=request.context.actor.user_id
            )
            response_0 = await deps.clients.identity_user.GetUser(outgoing_0, timeout=deps.settings.timeout)
            outgoing_1 = pipelines_v1_pipeline_run_import_service_pb2.MapPipelineRunImportColumnsRequest()
            outgoing_1.context.CopyFrom(request.context)
            outgoing_1.pipeline_run.audit.etag = response_0.user.audit.etag
            outgoing_1.pipeline_run.requester.phone = response_0.user.contact.phone
            outgoing_1.pipeline_run.requester.email = response_0.user.relationship_manager.email
            merged_1 = pipelines_v1_pipeline_run_import_service_pb2.MapPipelineRunImportColumnsRequest()
            merged_1.MergeFrom(outgoing_1)
            outgoing_1.CopyFrom(merged_1)
            response_1 = await deps.clients.pipelines_pipeline_run_import.MapPipelineRunImportColumns(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.user.relationship_manager.email
            returned_0_0_part_0 = response.pipelines.add()
            if returned_0_0:
                returned_0_0_part_0.organizer.email = returned_0_0
            returned_0_1 = response_0.user.primary_address.postal_code
            returned_0_1_part_0 = response.pipelines.add()
            if returned_0_1:
                returned_0_1_part_0.location.postal_code = returned_0_1
            returned_1_0 = response_1.pipeline_run.audit.updated_by
            returned_1_0_part_0 = response.pipelines.add()
            if returned_1_0:
                returned_1_0_part_0.audit.updated_by = returned_1_0
            returned_1_1 = response_1.pipeline_run.requester.phone
            returned_1_1_part_0 = response.pipelines.add()
            returned_1_1_part_1 = returned_1_1_part_0.participants.add()
            if returned_1_1:
                returned_1_1_part_1.contact.phone = returned_1_1
            return response

    async def handle_pull_pipelines(
        self,
        request: pipelines_v1_pipeline_sync_service_pb2.PullPipelinesRequest
    ) -> pipelines_v1_pipeline_sync_service_pb2.PullPipelinesResponse:
        """Pulls a pipeline."""
        deps = self.deps
        response = pipelines_v1_pipeline_sync_service_pb2.PullPipelinesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('PullPipelines', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'PullPipelines', {'reason': request.reason})
            await deps.repository.save_pipeline(request.context.tenant_id, request.pipeline)
            response_0 = metrics_v1_metric_alert_query_service_pb2.BrowseMetricAlertsResponse()
            response_1 = lineage_v1_impact_lifecycle_service_pb2.ScheduleImpactExpiryResponse()
            response_2 = lineage_v1_lineage_node_approval_service_pb2.SubmitLineageNodeResponse()
            response_3 = pipelines_v1_pipeline_step_validation_service_pb2.ScorePipelineStepResponse()
            outgoing_0 = metrics_v1_metric_alert_query_service_pb2.BrowseMetricAlertsRequest(
                context=request.context,
                filter=metrics_v1_metric_alert_query_service_pb2.BrowseMetricAlertsRequest.Filter(
                    created_after=request.pipeline.audit.created_at,
                    owner_id=request.pipeline.organizer.user_id,
                    region=request.pipeline.location.region
                )
            )
            envelope_0 = AnyMessage()
            envelope_0.Pack(outgoing_0)
            outgoing_0 = metrics_v1_metric_alert_query_service_pb2.BrowseMetricAlertsRequest()
            if not envelope_0.Unpack(outgoing_0):
                raise ValueError("partner envelope contains the wrong request type")
            response_0 = await deps.clients.metrics_metric_alert_query.BrowseMetricAlerts(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            callbacks_1: list[
                Callable[[], Awaitable[lineage_v1_impact_lifecycle_service_pb2.ScheduleImpactExpiryResponse]]
            ] = []
            for item_1 in request.pipeline.participants:
                outgoing_1 = lineage_v1_impact_lifecycle_service_pb2.ScheduleImpactExpiryRequest(
                    context=request.context,
                    details=lineage_v1_impact_lifecycle_service_pb2.ScheduleImpactExpiryRequest.Details(
                        notify=common_v1_contact_pb2.ContactInfo(phone=item_1.contact.phone)
                    ),
                    impact=lineage_v1_lineage_pb2.Impact(
                        assignee=identity_v1_refs_pb2.UserRef(email=item_1.contact.email),
                        requester=common_v1_contact_pb2.ContactInfo(name=item_1.contact.name)
                    )
                )
                async def send_1(
                    payload: lineage_v1_impact_lifecycle_service_pb2.ScheduleImpactExpiryRequest = outgoing_1
                ) -> lineage_v1_impact_lifecycle_service_pb2.ScheduleImpactExpiryResponse:
                    return await deps.clients.lineage_impact_lifecycle.ScheduleImpactExpiry(
                        payload,
                        timeout=deps.settings.timeout
                    )
                callbacks_1.append(send_1)
            for callback_1 in callbacks_1:
                response_1 = await callback_1()
            async for item_2 in async_messages(request.pipeline.participants):
                outgoing_2 = lineage_v1_lineage_node_approval_service_pb2.SubmitLineageNodeRequest(
                    context=request.context,
                    lineage_node=lineage_v1_lineage_pb2.LineageNode(
                        children=[
                            lineage_v1_lineage_pb2.LineageNode(
                                children=[
                                    lineage_v1_lineage_pb2.LineageNode(
                                        audit=common_v1_audit_pb2.AuditInfo(etag=request.pipeline.audit.etag),
                                        location=common_v1_address_pb2.PostalAddress(
                                            lines=list(request.pipeline.location.lines),
                                            region=request.pipeline.location.region
                                        ),
                                        manager=identity_v1_refs_pb2.UserRef(email=item_2.contact.email)
                                    )
                                ]
                            )
                        ]
                    )
                )
                response_2 = await deps.clients.lineage_lineage_node_approval.SubmitLineageNode(
                    outgoing_2,
                    timeout=deps.settings.timeout
                )
            command_3 = PipelineSyncPullPipelines3Command.model_validate(
                {
                    'context': request.context,
                    'pipeline_step_audit_updated_at': request.pipeline.audit.updated_at,
                    'details_destination_recipient': request.pipeline.location.recipient,
                    'pipeline_step_owner_user_id': request.pipeline.organizer.user_id
                }
            )
            outgoing_3 = to_pipeline_sync_pull_pipelines3_command(command_3)
            response_3 = await deps.clients.pipelines_pipeline_step_validation.ScorePipelineStep(
                outgoing_3,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.result.message = returned_0_0
            returned_3_0 = response_3.pipeline_step.owner.user_id
            if returned_3_0:
                response.pipeline.organizer.user_id = returned_3_0
            returned_3_1 = response_3.pipeline_step.audit.updated_at
            if returned_3_1.ListFields():
                response.pipeline.audit.updated_at.MergeFrom(returned_3_1)
            echoed_0 = request.pipeline_id
            response.pipeline.pipeline_id = echoed_0
            echoed_1 = request.pipeline.window
            response.pipeline.window.CopyFrom(echoed_1)
            return response

    async def handle_push_pipeline(
        self,
        request: pipelines_v1_pipeline_sync_service_pb2.PushPipelineRequest
    ) -> pipelines_v1_pipeline_sync_service_pb2.PushPipelineResponse:
        """Pushs a pipeline."""
        deps = self.deps
        response = pipelines_v1_pipeline_sync_service_pb2.PushPipelineResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('PushPipeline', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'PushPipeline', {'reason': request.reason})
            await deps.repository.save_pipeline(request.context.tenant_id, request.pipeline)
            response_0 = authorization_v1_access_policy_service_pb2.CloneAccessPolicyResponse()
            response_1 = pipelines_v1_pipeline_query_service_pb2.BrowsePipelinesResponse()
            response_2 = expenses_v1_expense_report_query_service_pb2.CountExpenseReportsResponse()
            for item_0 in request.pipeline.participants:
                outgoing_0 = authorization_v1_access_policy_service_pb2.CloneAccessPolicyRequest(
                    access_policy=authorization_v1_authorization_pb2.AccessPolicy(
                        owner=identity_v1_refs_pb2.UserRef(
                            email=item_0.contact.email,
                            user_id=request.pipeline.organizer.user_id
                        )
                    ),
                    context=request.context
                )
                response_0 = await deps.clients.authorization_access_policy.CloneAccessPolicy(
                    outgoing_0,
                    timeout=deps.settings.timeout
                )
            outgoing_1 = pipelines_v1_pipeline_query_service_pb2.BrowsePipelinesRequest(
                context=request.context,
                filter=pipelines_v1_pipeline_query_service_pb2.BrowsePipelinesRequest.Filter(
                    created_after=request.pipeline.audit.updated_at,
                    labels=dict(request.pipeline.metadata),
                    owner_id=response_0.result.correlation_id,
                    region=request.pipeline.location.region
                )
            )
            response_1 = await hooks.pipeline_sync_push_pipeline1(
                deps.clients.pipelines_pipeline_query,
                outgoing_1,
                deps.settings.timeout
            )
            outgoing_2 = expenses_v1_expense_report_query_service_pb2.CountExpenseReportsRequest()
            outgoing_2.context.CopyFrom(request.context)
            outgoing_2.filter.region = request.pipeline.location.region
            outgoing_2.filter.created_after.CopyFrom(response_0.access_policy.audit.created_at)
            outgoing_2.context.tenant_id = tenant_id.get()
            response_2 = await deps.clients.expenses_expense_report_query.CountExpenseReports(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            returned_1_0 = response_1.result.message
            if returned_1_0:
                response.outcome.message = returned_1_0
            returned_2_0 = response_2.result.status
            if returned_2_0:
                response.outcome.status = returned_2_0
            echoed_0 = request.pipeline_id
            response.pipeline.pipeline_id = echoed_0
            echoed_1 = request.pipeline.title
            response.pipeline.title = echoed_1
            return response

    async def handle_reconcile_pipelines(
        self,
        request: pipelines_v1_pipeline_sync_service_pb2.ReconcilePipelinesRequest
    ) -> pipelines_v1_pipeline_sync_service_pb2.ReconcilePipelinesResponse:
        """Reconciles a pipeline."""
        deps = self.deps
        response = pipelines_v1_pipeline_sync_service_pb2.ReconcilePipelinesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ReconcilePipelines', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'ReconcilePipelines', {'reason': request.reason})
            await deps.repository.save_pipeline(request.context.tenant_id, request.pipeline)
            response_0 = pipelines_v1_pipeline_validation_service_pb2.ScorePipelineResponse()
            outgoing_0 = pipelines_v1_pipeline_validation_service_pb2.ScorePipelineRequest(
                context=request.context,
                pipeline=pipelines_v1_pipelines_pb2.Pipeline(
                    location=common_v1_address_pb2.PostalAddress(country_code=request.pipeline.location.country_code)
                )
            )
            port_0: PipelineSyncReconcilePipelines0Port = PipelineSyncReconcilePipelines0Adapter(
                deps.clients.pipelines_pipeline_validation,
                deps.settings.timeout
            )
            response_0 = await port_0.execute(outgoing_0)
            returned_0_0 = response_0.pipeline.location.locality
            if returned_0_0:
                response.pipeline.location.locality = returned_0_0
            returned_0_1 = response_0.pipeline.location.country_code
            if returned_0_1:
                response.pipeline.location.country_code = returned_0_1
            echoed_0 = request.pipeline_id
            response.pipeline.pipeline_id = echoed_0
            echoed_1 = request.pipeline.metadata
            response.pipeline.metadata.update(echoed_1)
            return response

    async def handle_resolve_pipeline_conflict(
        self,
        request: pipelines_v1_pipeline_sync_service_pb2.ResolvePipelineConflictRequest
    ) -> pipelines_v1_pipeline_sync_service_pb2.ResolvePipelineConflictResponse:
        """Resolves a pipeline."""
        deps = self.deps
        response = pipelines_v1_pipeline_sync_service_pb2.ResolvePipelineConflictResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ResolvePipelineConflict', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ResolvePipelineConflict',
                {'reason': request.reason}
            )
            await deps.repository.save_pipeline(request.context.tenant_id, request.pipeline)
            response_0 = anomalies_v1_anomaly_workflow_service_pb2.RetryAnomalyWorkflowResponse()
            response_1 = pipelines_v1_pipeline_step_calculation_service_pb2.CalculatePipelineStepResponse()
            outgoing_0 = anomalies_v1_anomaly_workflow_service_pb2.RetryAnomalyWorkflowRequest(
                anomaly=anomalies_v1_anomalies_pb2.Anomaly(
                    assignee=identity_v1_refs_pb2.UserRef(display_name=request.pipeline.organizer.display_name),
                    audit=common_v1_audit_pb2.AuditInfo(updated_at=request.pipeline.audit.updated_at),
                    comments=[anomalies_v1_anomalies_pb2.AnomalyComment(created_at=request.pipeline.audit.created_at)]
                ),
                context=request.context
            )
            steps_0 = [
                partial(
                    deps.clients.anomalies_anomaly_workflow.RetryAnomalyWorkflow,
                    outgoing_0,
                    timeout=deps.settings.timeout
                )
            ]
            results_0 = await run_steps(steps_0)
            response_0 = results_0[-1]
            outgoing_1 = pipelines_v1_pipeline_step_calculation_service_pb2.CalculatePipelineStepRequest(
                context=request.context,
                details=pipelines_v1_pipeline_step_calculation_service_pb2.CalculatePipelineStepRequest.Details(
                    destination=common_v1_address_pb2.PostalAddress(
                        postal_code=request.pipeline.location.postal_code,
                        recipient=request.pipeline.location.recipient
                    )
                ),
                pipeline_step=pipelines_v1_pipelines_pb2.PipelineStep(
                    audit=common_v1_audit_pb2.AuditInfo(created_by=response_0.anomaly.audit.created_by)
                )
            )
            response_1 = await PipelineSyncResolvePipelineConflict1Adapter(
                deps.clients.pipelines_pipeline_step_calculation,
                deps.settings.timeout
            )(outgoing_1)
            returned_0_0 = response_0.anomaly.audit.created_at
            if returned_0_0.ListFields():
                response.pipeline.audit.created_at.MergeFrom(returned_0_0)
            returned_0_1 = response_0.outcome.status
            if returned_0_1:
                response.result.status = returned_0_1
            returned_1_0 = response_1.pipeline_step.owner.email
            returned_1_0_part_1 = response.pipeline.participants.add()
            if returned_1_0:
                returned_1_0_part_1.contact.email = returned_1_0
            echoed_0 = request.pipeline_id
            response.pipeline.pipeline_id = echoed_0
            echoed_1 = request.pipeline.location
            response.pipeline.location.CopyFrom(echoed_1)
            return response

    async def handle_stream_pipeline_changes(
        self,
        request: pipelines_v1_pipeline_sync_service_pb2.StreamPipelineChangesRequest
    ) -> pipelines_v1_pipeline_sync_service_pb2.StreamPipelineChangesResponse:
        """Exchanges changes of pipelines with a peer."""
        deps = self.deps
        response = pipelines_v1_pipeline_sync_service_pb2.StreamPipelineChangesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('StreamPipelineChanges', extra={'fields': {'cursor': request.cursor}})
            await deps.repository.audit(request.context.tenant_id, 'StreamPipelineChanges', {'cursor': request.cursor})
            if request.WhichOneof('frame') == 'change':
                await deps.repository.save_pipeline(request.context.tenant_id, request.change)
            response_0 = pipelines_v1_pipeline_query_service_pb2.ResolvePipelinesResponse()
            response_1 = pipelines_v1_pipeline_step_validation_service_pb2.PreviewPipelineStepResponse()
            response_2 = authorization_v1_access_policy_service_pb2.UpdateAccessPolicyResponse()
            outgoing_0 = pipelines_v1_pipeline_query_service_pb2.ResolvePipelinesRequest(context=request.context)
            response_0 = cast(pipelines_v1_pipeline_query_service_pb2.ResolvePipelinesResponse, await deps.bus.request(
                'acme.pipelines.v1.PipelineSyncService/StreamPipelineChanges/0', outgoing_0, deps.settings.timeout,
            ))
            requests_1: list[pipelines_v1_pipeline_step_validation_service_pb2.PreviewPipelineStepRequest] = []
            for item_1 in request.change.participants:
                outgoing_1 = pipelines_v1_pipeline_step_validation_service_pb2.PreviewPipelineStepRequest(
                    context=request.context,
                    details=pipelines_v1_pipeline_step_validation_service_pb2.PreviewPipelineStepRequest.Details(
                        contact=common_v1_contact_pb2.ContactInfo(preferred_channel=item_1.contact.preferred_channel)
                    )
                )
                requests_1.append(outgoing_1)
            replies_1 = await asyncio.gather(*(
                deps.clients.pipelines_pipeline_step_validation.PreviewPipelineStep(
                    entry,
                    timeout=deps.settings.timeout
                ) for entry in requests_1
            ))
            if replies_1:
                response_1 = replies_1[-1]
            outgoing_2 = authorization_v1_access_policy_service_pb2.UpdateAccessPolicyRequest()
            outgoing_2.context.CopyFrom(request.context)
            if request.WhichOneof('frame') == 'change':
                outgoing_2.access_policy.audit.created_by = request.change.audit.created_by
            response_2 = await deps.clients.authorization_access_policy.UpdateAccessPolicy(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.details
            response.result.details.update(returned_0_0)
            returned_0_1 = response_0.result.status
            if returned_0_1:
                response.result.status = returned_0_1
            returned_2_0 = response_2.access_policy.audit.updated_at
            if returned_2_0.ListFields():
                response.pipeline.audit.updated_at.MergeFrom(returned_2_0)
            echoed_0 = request.change.window
            response.pipeline.window.CopyFrom(echoed_0)
            echoed_1 = request.change.title
            response.pipeline.title = echoed_1
            return response

    async def handle_sync_pipelines(
        self,
        request: pipelines_v1_pipeline_sync_service_pb2.SyncPipelinesRequest
    ) -> pipelines_v1_pipeline_sync_service_pb2.SyncPipelinesResponse:
        """Syncs a pipeline."""
        deps = self.deps
        response = pipelines_v1_pipeline_sync_service_pb2.SyncPipelinesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SyncPipelines', extra={'fields': {'checksum': request.details.checksum}})
            await deps.repository.audit(
                request.context.tenant_id,
                'SyncPipelines',
                {'checksum': request.details.checksum}
            )
            await deps.repository.save_pipeline(request.context.tenant_id, request.pipeline)
            response_0 = lineage_v1_lineage_node_approval_service_pb2.RejectLineageNodeResponse()
            response_1 = assets_v1_fixed_asset_query_service_pb2.SummarizeFixedAssetsResponse()
            response_2 = pipelines_v1_pipeline_run_calculation_service_pb2.ExplainPipelineRunCalculationResponse()
            callbacks_0: list[
                Callable[[], Awaitable[lineage_v1_lineage_node_approval_service_pb2.RejectLineageNodeResponse]]
            ] = []
            for item_0 in request.pipeline.participants:
                outgoing_0 = lineage_v1_lineage_node_approval_service_pb2.RejectLineageNodeRequest(
                    context=request.context,
                    lineage_node=lineage_v1_lineage_pb2.LineageNode(
                        children=[
                            lineage_v1_lineage_pb2.LineageNode(
                                children=[
                                    lineage_v1_lineage_pb2.LineageNode(
                                        audit=common_v1_audit_pb2.AuditInfo(
                                            updated_at=request.pipeline.audit.updated_at
                                        ),
                                        manager=identity_v1_refs_pb2.UserRef(email=item_0.contact.email)
                                    )
                                ]
                            )
                        ]
                    )
                )
                async def send_0(
                    payload: lineage_v1_lineage_node_approval_service_pb2.RejectLineageNodeRequest = outgoing_0
                ) -> lineage_v1_lineage_node_approval_service_pb2.RejectLineageNodeResponse:
                    return await deps.clients.lineage_lineage_node_approval.RejectLineageNode(
                        payload,
                        timeout=deps.settings.timeout
                    )
                callbacks_0.append(send_0)
            for callback_0 in callbacks_0:
                response_0 = await callback_0()
            outgoing_1 = assets_v1_fixed_asset_query_service_pb2.SummarizeFixedAssetsRequest(
                annotations=dict(request.annotations),
                context=request.context,
                reason=request.reason
            )
            document_1 = MessageToDict(outgoing_1, preserving_proto_field_name=True)
            outgoing_1 = ParseDict(document_1, assets_v1_fixed_asset_query_service_pb2.SummarizeFixedAssetsRequest())
            response_1 = await deps.clients.assets_fixed_asset_query.SummarizeFixedAssets(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = pipelines_v1_pipeline_run_calculation_service_pb2.ExplainPipelineRunCalculationRequest(
                context=request.context,
                pipeline_run=pipelines_v1_pipelines_pb2.PipelineRun(
                    assignee=identity_v1_refs_pb2.UserRef(
                        display_name=request.pipeline.organizer.display_name,
                        user_id=request.pipeline.organizer.user_id
                    ),
                    audit=common_v1_audit_pb2.AuditInfo(
                        etag=request.pipeline.audit.etag,
                        updated_at=request.pipeline.audit.updated_at
                    )
                )
            )
            document_2 = MessageToJson(outgoing_2, preserving_proto_field_name=True)
            outgoing_2 = Parse(
                document_2,
                pipelines_v1_pipeline_run_calculation_service_pb2.ExplainPipelineRunCalculationRequest()
            )
            response_2 = await deps.clients.pipelines_pipeline_run_calculation.ExplainPipelineRunCalculation(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            returned_1_0 = response_1.result.status
            if returned_1_0:
                response.result.status = returned_1_0
            returned_2_0 = response_2.pipeline_run.assignee.display_name
            if returned_2_0:
                response.pipeline.organizer.display_name = returned_2_0
            echoed_0 = request.pipeline_id
            response.pipeline.pipeline_id = echoed_0
            echoed_1 = request.pipeline.status
            response.pipeline.status = echoed_1
            return response
