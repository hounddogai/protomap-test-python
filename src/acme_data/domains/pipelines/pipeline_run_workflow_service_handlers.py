"""Reusable transport mixin for PipelineRunWorkflowService."""

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
import grpc

from acme.audit.v1 import audit_event_query_service_pb2 as audit_v1_audit_event_query_service_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.featureflags.v1 import (
    feature_flag_validation_service_pb2 as featureflags_v1_feature_flag_validation_service_pb2,
)
from acme.featureflags.v1 import featureflags_pb2 as featureflags_v1_featureflags_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.identity.v1 import user_query_service_pb2 as identity_v1_user_query_service_pb2
from acme.ledger.v1 import ledger_account_query_service_pb2 as ledger_v1_ledger_account_query_service_pb2
from acme.lineage.v1 import impact_approval_service_pb2 as lineage_v1_impact_approval_service_pb2
from acme.lineage.v1 import impact_sync_service_pb2 as lineage_v1_impact_sync_service_pb2
from acme.lineage.v1 import lineage_edge_approval_service_pb2 as lineage_v1_lineage_edge_approval_service_pb2
from acme.lineage.v1 import lineage_edge_approval_service_pb2_grpc as lineage_v1_lineage_edge_approval_service_pb2_grpc
from acme.lineage.v1 import lineage_pb2 as lineage_v1_lineage_pb2
from acme.lineage.v1 import refs_pb2 as lineage_v1_refs_pb2
from acme.pipelines.v1 import pipeline_approval_service_pb2 as pipelines_v1_pipeline_approval_service_pb2
from acme.pipelines.v1 import pipeline_run_reporting_service_pb2 as pipelines_v1_pipeline_run_reporting_service_pb2
from acme.pipelines.v1 import pipeline_run_workflow_service_pb2 as pipelines_v1_pipeline_run_workflow_service_pb2
from acme.pipelines.v1 import pipeline_step_approval_service_pb2 as pipelines_v1_pipeline_step_approval_service_pb2
from acme.pipelines.v1 import pipeline_step_import_service_pb2 as pipelines_v1_pipeline_step_import_service_pb2
from acme.pipelines.v1 import pipeline_validation_service_pb2 as pipelines_v1_pipeline_validation_service_pb2
from acme.pipelines.v1 import pipelines_pb2 as pipelines_v1_pipelines_pb2

from acme_data.domains.pipelines import hooks
from acme_data.domains.pipelines.adapters import PipelineRunWorkflowAdvancePipelineRunWorkflow0Adapter
from acme_data.domains.pipelines.dependencies import Dependencies
from acme_data.domains.pipelines.models import PipelineRunWorkflowSignalPipelineRunWorkflow0Command
from acme_data.domains.pipelines.models import PipelineRunWorkflowSignalPipelineRunWorkflow1Command
from acme_data.domains.pipelines.models import to_pipeline_run_workflow_signal_pipeline_run_workflow0_command
from acme_data.domains.pipelines.models import to_pipeline_run_workflow_signal_pipeline_run_workflow1_command
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_id
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class PipelineRunWorkflowServicerHandlers:
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    async def AdvancePipelineRunWorkflow(
        self, request: pipelines_v1_pipeline_run_workflow_service_pb2.AdvancePipelineRunWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_run_workflow_service_pb2.AdvancePipelineRunWorkflowResponse:
        """Advances a pipeline run."""
        return await self.handle_advance_pipeline_run_workflow(request)

    @rpc_errors
    async def CancelPipelineRunWorkflow(
        self, request: pipelines_v1_pipeline_run_workflow_service_pb2.CancelPipelineRunWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_run_workflow_service_pb2.CancelPipelineRunWorkflowResponse:
        """Cancels a pipeline run."""
        return await self.handle_cancel_pipeline_run_workflow(request)

    @rpc_errors
    @retry_transient
    async def ListPipelineRunWorkflows(
        self, request: pipelines_v1_pipeline_run_workflow_service_pb2.ListPipelineRunWorkflowsRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_run_workflow_service_pb2.ListPipelineRunWorkflowsResponse:
        """Lists pipeline runs a page at a time."""
        return await self.handle_list_pipeline_run_workflows(request)

    @rpc_errors
    async def PausePipelineRunWorkflow(
        self, request: pipelines_v1_pipeline_run_workflow_service_pb2.PausePipelineRunWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_run_workflow_service_pb2.PausePipelineRunWorkflowResponse:
        """Pauses a pipeline run."""
        return await self.handle_pause_pipeline_run_workflow(request)

    @rpc_errors
    async def ResumePipelineRunWorkflow(
        self, request: pipelines_v1_pipeline_run_workflow_service_pb2.ResumePipelineRunWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_run_workflow_service_pb2.ResumePipelineRunWorkflowResponse:
        """Resumes a pipeline run."""
        return await self.handle_resume_pipeline_run_workflow(request)

    @rpc_errors
    async def RetryPipelineRunWorkflow(
        self, request: pipelines_v1_pipeline_run_workflow_service_pb2.RetryPipelineRunWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_run_workflow_service_pb2.RetryPipelineRunWorkflowResponse:
        """Retrys a pipeline run."""
        return await self.handle_retry_pipeline_run_workflow(request)

    @rpc_errors
    async def SignalPipelineRunWorkflow(
        self, request: pipelines_v1_pipeline_run_workflow_service_pb2.SignalPipelineRunWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_run_workflow_service_pb2.SignalPipelineRunWorkflowResponse:
        """Signals a pipeline run."""
        return await self.handle_signal_pipeline_run_workflow(request)

    @rpc_errors
    async def StartPipelineRunWorkflow(
        self, request: pipelines_v1_pipeline_run_workflow_service_pb2.StartPipelineRunWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_run_workflow_service_pb2.StartPipelineRunWorkflowResponse:
        """Starts a pipeline run."""
        return await self.handle_start_pipeline_run_workflow(request)

    async def handle_advance_pipeline_run_workflow(
        self,
        request: pipelines_v1_pipeline_run_workflow_service_pb2.AdvancePipelineRunWorkflowRequest
    ) -> pipelines_v1_pipeline_run_workflow_service_pb2.AdvancePipelineRunWorkflowResponse:
        """Advances a pipeline run."""
        deps = self.deps
        response = pipelines_v1_pipeline_run_workflow_service_pb2.AdvancePipelineRunWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('AdvancePipelineRunWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'AdvancePipelineRunWorkflow',
                {'reason': request.reason}
            )
            await deps.repository.save_pipeline_run(request.context.tenant_id, request.pipeline_run)
            response_0 = featureflags_v1_feature_flag_validation_service_pb2.CheckFeatureFlagEligibilityResponse()
            response_1 = pipelines_v1_pipeline_approval_service_pb2.EscalatePipelineResponse()
            outgoing_0 = featureflags_v1_feature_flag_validation_service_pb2.CheckFeatureFlagEligibilityRequest(
                context=request.context,
                details=featureflags_v1_feature_flag_validation_service_pb2.CheckFeatureFlagEligibilityRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(
                        name=request.details.notify.name,
                        phone=request.details.notify.phone
                    )
                ),
                feature_flag=featureflags_v1_featureflags_pb2.FeatureFlag(
                    audit=common_v1_audit_pb2.AuditInfo(updated_at=request.pipeline_run.audit.updated_at),
                    owner=identity_v1_refs_pb2.UserRef(display_name=request.pipeline_run.assignee.display_name)
                )
            )
            response_0 = await PipelineRunWorkflowAdvancePipelineRunWorkflow0Adapter(
                deps.clients.featureflags_feature_flag_validation,
                deps.settings.timeout
            )(outgoing_0)
            outgoing_1 = pipelines_v1_pipeline_approval_service_pb2.EscalatePipelineRequest(
                context=request.context,
                details=pipelines_v1_pipeline_approval_service_pb2.EscalatePipelineRequest.Details(
                    approver=identity_v1_refs_pb2.UserRef(email=response_0.feature_flag.owner.email)
                ),
                pipeline=pipelines_v1_pipelines_pb2.Pipeline(
                    audit=common_v1_audit_pb2.AuditInfo(updated_at=request.pipeline_run.audit.updated_at),
                    organizer=identity_v1_refs_pb2.UserRef(user_id=request.pipeline_run.assignee.user_id),
                    participants=[
                        pipelines_v1_pipelines_pb2.PipelineParticipant(
                            contact=common_v1_contact_pb2.ContactInfo(name=request.pipeline_run.requester.name)
                        )
                    ]
                )
            )
            response_1 = cast(pipelines_v1_pipeline_approval_service_pb2.EscalatePipelineResponse, await deps.bus.request(
                'acme.pipelines.v1.PipelineRunWorkflowService/AdvancePipelineRunWorkflow/1', outgoing_1, deps.settings.timeout,
            ))
            returned_0_0 = response_0.feature_flag.owner.email
            if returned_0_0:
                response.pipeline_run.requester.email = returned_0_0
            returned_0_1 = response_0.feature_flag.owner.display_name
            if returned_0_1:
                response.pipeline_run.assignee.display_name = returned_0_1
            returned_1_0 = response_1.result.correlation_id
            if returned_1_0:
                response.result.correlation_id = returned_1_0
            returned_1_1 = response_1.result.message
            if returned_1_1:
                response.result.message = returned_1_1
            echoed_0 = request.pipeline_run_id
            response.pipeline_run.pipeline_run_id = echoed_0
            echoed_1 = request.pipeline_run.priority
            response.pipeline_run.priority = echoed_1
            return response

    async def handle_cancel_pipeline_run_workflow(
        self,
        request: pipelines_v1_pipeline_run_workflow_service_pb2.CancelPipelineRunWorkflowRequest
    ) -> pipelines_v1_pipeline_run_workflow_service_pb2.CancelPipelineRunWorkflowResponse:
        """Cancels a pipeline run."""
        deps = self.deps
        response = pipelines_v1_pipeline_run_workflow_service_pb2.CancelPipelineRunWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CancelPipelineRunWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'CancelPipelineRunWorkflow',
                {'reason': request.reason}
            )
            await deps.repository.save_pipeline_run(request.context.tenant_id, request.pipeline_run)
            response_0 = lineage_v1_impact_sync_service_pb2.ResolveImpactConflictResponse()
            response_1 = audit_v1_audit_event_query_service_pb2.ResolveAuditEventsResponse()
            outgoing_0 = lineage_v1_impact_sync_service_pb2.ResolveImpactConflictRequest(
                context=request.context,
                impact=lineage_v1_lineage_pb2.Impact(
                    audit=common_v1_audit_pb2.AuditInfo(created_by=request.pipeline_run.audit.created_by)
                )
            )
            response_0 = await deps.clients.lineage_impact_sync.ResolveImpactConflict(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = audit_v1_audit_event_query_service_pb2.ResolveAuditEventsRequest(context=request.context)
            method_name_1 = 'ResolveAuditEvents'
            response_1 = await getattr(
                deps.clients.audit_audit_event_query,
                method_name_1
            )(outgoing_1, timeout=deps.settings.timeout)
            returned_0_0 = response_0.impact.audit.updated_at
            if returned_0_0.ListFields():
                response.pipeline_run.audit.updated_at.MergeFrom(returned_0_0)
            returned_0_1 = response_0.impact.requester.name
            if returned_0_1.ListFields():
                response.pipeline_run.requester.name.MergeFrom(returned_0_1)
            returned_1_0 = response_1.result.message
            if returned_1_0:
                response.result.message = returned_1_0
            echoed_0 = request.pipeline_run_id
            response.pipeline_run.pipeline_run_id = echoed_0
            echoed_1 = request.pipeline_run.custom_fields
            response.pipeline_run.custom_fields.update(echoed_1)
            return response

    async def handle_list_pipeline_run_workflows(
        self,
        request: pipelines_v1_pipeline_run_workflow_service_pb2.ListPipelineRunWorkflowsRequest
    ) -> pipelines_v1_pipeline_run_workflow_service_pb2.ListPipelineRunWorkflowsResponse:
        """Lists pipeline runs a page at a time."""
        deps = self.deps
        response = pipelines_v1_pipeline_run_workflow_service_pb2.ListPipelineRunWorkflowsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ListPipelineRunWorkflows', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ListPipelineRunWorkflows',
                {'order_by': request.order_by}
            )
            return response

    async def handle_pause_pipeline_run_workflow(
        self,
        request: pipelines_v1_pipeline_run_workflow_service_pb2.PausePipelineRunWorkflowRequest
    ) -> pipelines_v1_pipeline_run_workflow_service_pb2.PausePipelineRunWorkflowResponse:
        """Pauses a pipeline run."""
        deps = self.deps
        response = pipelines_v1_pipeline_run_workflow_service_pb2.PausePipelineRunWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('PausePipelineRunWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'PausePipelineRunWorkflow',
                {'reason': request.reason}
            )
            await deps.repository.save_pipeline_run(request.context.tenant_id, request.pipeline_run)
            response_0 = pipelines_v1_pipeline_step_import_service_pb2.ListPipelineStepImportsResponse()
            response_1 = pipelines_v1_pipeline_run_reporting_service_pb2.StreamPipelineRunMetricsResponse()
            response_2 = identity_v1_user_query_service_pb2.BrowseUsersResponse()
            fields_0: dict[str, Any] = {
                'context': request.context,
                'filter': {
                    'created_after': request.pipeline_run.audit.updated_at,
                    'owner_id': request.pipeline_run.sla.policy_id
                }
            }
            outgoing_0 = pipelines_v1_pipeline_step_import_service_pb2.ListPipelineStepImportsRequest(**fields_0)
            response_0 = await deps.clients.pipelines_pipeline_step_import.ListPipelineStepImports(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = pipelines_v1_pipeline_run_reporting_service_pb2.StreamPipelineRunMetricsRequest(
                context=request.context,
                subscriber=common_v1_contact_pb2.ContactInfo(phone=request.pipeline_run.requester.phone)
            )
            async for chunk_1 in deps.clients.pipelines_pipeline_run_reporting.StreamPipelineRunMetrics(
                outgoing_1,
                timeout=deps.settings.timeout
            ):
                response_1 = chunk_1
            async for item_2 in async_messages(request.pipeline_run.history):
                outgoing_2 = identity_v1_user_query_service_pb2.BrowseUsersRequest(
                    context=request.context,
                    filter=identity_v1_user_query_service_pb2.BrowseUsersRequest.Filter(
                        created_after=item_2.changed_at,
                        labels=dict(request.details.parameters),
                        owner_id=request.pipeline_run.customer.pipeline_id
                    )
                )
                response_2 = await deps.clients.identity_user_query.BrowseUsers(
                    outgoing_2,
                    timeout=deps.settings.timeout
                )
            returned_0_0 = response_0.result.correlation_id
            if returned_0_0:
                response.result.correlation_id = returned_0_0
            returned_0_1 = response_0.result.status
            if returned_0_1:
                response.result.status = returned_0_1
            echoed_0 = request.pipeline_run_id
            response.pipeline_run.pipeline_run_id = echoed_0
            echoed_1 = request.pipeline_run.assignee
            response.pipeline_run.assignee.CopyFrom(echoed_1)
            return response

    async def handle_resume_pipeline_run_workflow(
        self,
        request: pipelines_v1_pipeline_run_workflow_service_pb2.ResumePipelineRunWorkflowRequest
    ) -> pipelines_v1_pipeline_run_workflow_service_pb2.ResumePipelineRunWorkflowResponse:
        """Resumes a pipeline run."""
        deps = self.deps
        response = pipelines_v1_pipeline_run_workflow_service_pb2.ResumePipelineRunWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ResumePipelineRunWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ResumePipelineRunWorkflow',
                {'reason': request.reason}
            )
            await deps.repository.save_pipeline_run(request.context.tenant_id, request.pipeline_run)
            response_0 = lineage_v1_impact_approval_service_pb2.DelegateImpactApprovalResponse()
            response_1 = lineage_v1_impact_sync_service_pb2.PushImpactResponse()
            outgoing_0 = lineage_v1_impact_approval_service_pb2.DelegateImpactApprovalRequest()
            outgoing_0.context.CopyFrom(request.context)
            outgoing_0.impact.customer.email = request.pipeline_run.assignee.email
            outgoing_0.impact.sla.policy_id = request.pipeline_run.sla.policy_id
            if request.pipeline_run.WhichOneof('origin') == 'customer':
                outgoing_0.details.approver.display_name = request.pipeline_run.customer.display_name
            outgoing_0.impact.audit.updated_at.CopyFrom(request.pipeline_run.audit.updated_at)
            response_0 = await deps.clients.lineage_impact_approval.DelegateImpactApproval(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = lineage_v1_impact_sync_service_pb2.PushImpactRequest(
                context=request.context,
                impact=lineage_v1_lineage_pb2.Impact(
                    requester=common_v1_contact_pb2.ContactInfo(phone=response_0.impact.requester.phone)
                )
            )
            envelope_1 = AnyMessage()
            envelope_1.Pack(outgoing_1)
            outgoing_1 = lineage_v1_impact_sync_service_pb2.PushImpactRequest()
            if not envelope_1.Unpack(outgoing_1):
                raise ValueError("partner envelope contains the wrong request type")
            response_1 = await deps.clients.lineage_impact_sync.PushImpact(outgoing_1, timeout=deps.settings.timeout)
            returned_0_0 = response_0.impact.audit.etag
            if returned_0_0:
                response.pipeline_run.audit.etag = returned_0_0
            returned_1_0 = response_1.impact.audit.updated_by
            if returned_1_0:
                response.pipeline_run.audit.updated_by = returned_1_0
            returned_1_1 = response_1.outcome.message
            if returned_1_1:
                response.outcome.message = returned_1_1
            echoed_0 = request.pipeline_run_id
            response.pipeline_run.pipeline_run_id = echoed_0
            echoed_1 = request.pipeline_run.priority
            response.pipeline_run.priority = echoed_1
            return response

    async def handle_retry_pipeline_run_workflow(
        self,
        request: pipelines_v1_pipeline_run_workflow_service_pb2.RetryPipelineRunWorkflowRequest
    ) -> pipelines_v1_pipeline_run_workflow_service_pb2.RetryPipelineRunWorkflowResponse:
        """Retrys a pipeline run."""
        deps = self.deps
        response = pipelines_v1_pipeline_run_workflow_service_pb2.RetryPipelineRunWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('RetryPipelineRunWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'RetryPipelineRunWorkflow',
                {'reason': request.reason}
            )
            await deps.repository.save_pipeline_run(request.context.tenant_id, request.pipeline_run)
            response_0 = lineage_v1_lineage_edge_approval_service_pb2.DelegateLineageEdgeApprovalResponse()
            outgoing_0 = lineage_v1_lineage_edge_approval_service_pb2.DelegateLineageEdgeApprovalRequest(
                context=request.context,
                lineage_edge=lineage_v1_lineage_pb2.LineageEdge(
                    subject=lineage_v1_refs_pb2.ImpactRef(display_name=request.pipeline_run.customer.display_name)
                )
            )
            registered_0 = cast(
                lineage_v1_lineage_edge_approval_service_pb2_grpc.LineageEdgeApprovalServiceStub,
                deps.clients.registry['acme.lineage.v1.LineageEdgeApprovalService']
            )
            response_0 = await registered_0.DelegateLineageEdgeApproval(outgoing_0, timeout=deps.settings.timeout)
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.outcome.message = returned_0_0
            returned_0_1 = response_0.outcome.message
            if returned_0_1:
                response.result.message = returned_0_1
            echoed_0 = request.pipeline_run_id
            response.pipeline_run.pipeline_run_id = echoed_0
            echoed_1 = request.pipeline_run.status
            response.pipeline_run.status = echoed_1
            return response

    async def handle_signal_pipeline_run_workflow(
        self,
        request: pipelines_v1_pipeline_run_workflow_service_pb2.SignalPipelineRunWorkflowRequest
    ) -> pipelines_v1_pipeline_run_workflow_service_pb2.SignalPipelineRunWorkflowResponse:
        """Signals a pipeline run."""
        deps = self.deps
        response = pipelines_v1_pipeline_run_workflow_service_pb2.SignalPipelineRunWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SignalPipelineRunWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'SignalPipelineRunWorkflow',
                {'reason': request.reason}
            )
            await deps.repository.save_pipeline_run(request.context.tenant_id, request.pipeline_run)
            response_0 = pipelines_v1_pipeline_validation_service_pb2.NormalizePipelineResponse()
            response_1 = pipelines_v1_pipeline_step_approval_service_pb2.RejectPipelineStepResponse()
            command_0 = PipelineRunWorkflowSignalPipelineRunWorkflow0Command(
                context=request.context,
                pipeline_participants_contact_name=request.details.notify.name,
                pipeline_participants_contact_email=request.pipeline_run.assignee.email,
                pipeline_organizer_user_id=request.pipeline_run.assignee.user_id
            )
            outgoing_0 = to_pipeline_run_workflow_signal_pipeline_run_workflow0_command(command_0)
            response_0 = await deps.clients.pipelines_pipeline_validation.NormalizePipeline(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            command_1 = PipelineRunWorkflowSignalPipelineRunWorkflow1Command.model_validate(
                {
                    'context': request.context,
                    'pipeline_step_owner_display_name': response_0.pipeline.organizer.display_name,
                    'pipeline_step_owner_user_id': response_0.pipeline.organizer.user_id,
                    'pipeline_step_owner_email': request.pipeline_run.assignee.email
                }
            )
            outgoing_1 = to_pipeline_run_workflow_signal_pipeline_run_workflow1_command(command_1)
            response_1 = await deps.clients.pipelines_pipeline_step_approval.RejectPipelineStep(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.outcome.status
            if returned_0_0:
                response.result.status = returned_0_0
            returned_0_1 = response_0.outcome.reference_id
            if returned_0_1:
                response.outcome.reference_id = returned_0_1
            returned_1_0 = response_1.outcome.effective_at
            if returned_1_0.ListFields():
                response.outcome.effective_at.MergeFrom(returned_1_0)
            echoed_0 = request.pipeline_run_id
            response.pipeline_run.pipeline_run_id = echoed_0
            echoed_1 = request.pipeline_run.priority
            response.pipeline_run.priority = echoed_1
            return response

    async def handle_start_pipeline_run_workflow(
        self,
        request: pipelines_v1_pipeline_run_workflow_service_pb2.StartPipelineRunWorkflowRequest
    ) -> pipelines_v1_pipeline_run_workflow_service_pb2.StartPipelineRunWorkflowResponse:
        """Starts a pipeline run."""
        deps = self.deps
        response = pipelines_v1_pipeline_run_workflow_service_pb2.StartPipelineRunWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('StartPipelineRunWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'StartPipelineRunWorkflow',
                {'reason': request.reason}
            )
            await deps.repository.save_pipeline_run(request.context.tenant_id, request.pipeline_run)
            response_0 = pipelines_v1_pipeline_approval_service_pb2.RejectPipelineResponse()
            response_1 = pipelines_v1_pipeline_run_reporting_service_pb2.SharePipelineRunReportResponse()
            response_2 = ledger_v1_ledger_account_query_service_pb2.SuggestLedgerAccountsResponse()
            outgoing_0 = pipelines_v1_pipeline_approval_service_pb2.RejectPipelineRequest(
                context=request.context,
                pipeline=pipelines_v1_pipelines_pb2.Pipeline(
                    participants=[
                        pipelines_v1_pipelines_pb2.PipelineParticipant(
                            contact=common_v1_contact_pb2.ContactInfo(name=request.details.notify.name)
                        )
                    ]
                )
            )
            send_0 = partial(deps.clients.pipelines_pipeline_approval.RejectPipeline, timeout=deps.settings.timeout)
            response_0 = await send_0(outgoing_0)
            outgoing_1 = pipelines_v1_pipeline_run_reporting_service_pb2.SharePipelineRunReportRequest(
                context=request.context,
                details=pipelines_v1_pipeline_run_reporting_service_pb2.SharePipelineRunReportRequest.Details(
                    recipient=common_v1_contact_pb2.ContactInfo(
                        email=request.pipeline_run.requester.email,
                        phone=request.details.notify.phone
                    )
                )
            )
            response_1 = await hooks.pipeline_run_workflow_start_pipeline_run_workflow1(
                deps.clients.pipelines_pipeline_run_reporting,
                outgoing_1,
                deps.settings.timeout
            )
            outgoing_2 = ledger_v1_ledger_account_query_service_pb2.SuggestLedgerAccountsRequest()
            outgoing_2.context.CopyFrom(request.context)
            outgoing_2.filter.region = response_0.pipeline.location.region
            outgoing_2.context.tenant_id = tenant_id.get()
            response_2 = await deps.clients.ledger_ledger_account_query.SuggestLedgerAccounts(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.correlation_id
            if returned_0_0:
                response.result.correlation_id = returned_0_0
            returned_0_1 = response_0.outcome.next_steps
            response.outcome.next_steps.extend(returned_0_1)
            returned_1_0 = response_1.pipeline_run.customer.display_name
            if returned_1_0:
                response.pipeline_run.assignee.display_name = returned_1_0
            returned_1_1 = response_1.pipeline_run.priority
            if returned_1_1:
                response.pipeline_run.priority = returned_1_1
            returned_2_0 = response_2.result.status
            if returned_2_0:
                response.outcome.status = returned_2_0
            returned_2_1 = response_2.result.message
            if returned_2_1:
                response.outcome.message = returned_2_1
            echoed_0 = request.pipeline_run_id
            response.pipeline_run.pipeline_run_id = echoed_0
            echoed_1 = request.pipeline_run.status
            response.pipeline_run.status = echoed_1
            return response
