"""Reusable transport mixin for PipelineStepWorkflowService."""

from __future__ import annotations

from collections.abc import AsyncIterator
from functools import partial
from typing import Any
from typing import cast
import asyncio
import logging

import grpc

from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.identity.v1 import user_service_pb2 as identity_v1_user_service_pb2
from acme.metrics.v1 import metric_series_history_service_pb2 as metrics_v1_metric_series_history_service_pb2
from acme.metrics.v1 import metrics_pb2 as metrics_v1_metrics_pb2
from acme.pipelines.v1 import pipeline_lifecycle_service_pb2 as pipelines_v1_pipeline_lifecycle_service_pb2
from acme.pipelines.v1 import pipeline_run_lifecycle_service_pb2 as pipelines_v1_pipeline_run_lifecycle_service_pb2
from acme.pipelines.v1 import pipeline_step_approval_service_pb2 as pipelines_v1_pipeline_step_approval_service_pb2
from acme.pipelines.v1 import pipeline_step_export_service_pb2 as pipelines_v1_pipeline_step_export_service_pb2
from acme.pipelines.v1 import pipeline_step_workflow_service_pb2 as pipelines_v1_pipeline_step_workflow_service_pb2
from acme.pipelines.v1 import pipelines_pb2 as pipelines_v1_pipelines_pb2
from acme.pipelines.v1 import refs_pb2 as pipelines_v1_refs_pb2
from acme.search.v1 import search_index_validation_service_pb2 as search_v1_search_index_validation_service_pb2

from acme_data.domains.pipelines import hooks
from acme_data.domains.pipelines.adapters import PipelineStepWorkflowCancelPipelineStepWorkflow0Adapter
from acme_data.domains.pipelines.adapters import PipelineStepWorkflowCancelPipelineStepWorkflow0Port
from acme_data.domains.pipelines.dependencies import Dependencies
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import run_steps
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class PipelineStepWorkflowServicerHandlers:
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    async def AdvancePipelineStepWorkflow(
        self, request: pipelines_v1_pipeline_step_workflow_service_pb2.AdvancePipelineStepWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_step_workflow_service_pb2.AdvancePipelineStepWorkflowResponse:
        """Advances a pipeline step."""
        return await self.handle_advance_pipeline_step_workflow(request)

    @rpc_errors
    async def CancelPipelineStepWorkflow(
        self, request: pipelines_v1_pipeline_step_workflow_service_pb2.CancelPipelineStepWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_step_workflow_service_pb2.CancelPipelineStepWorkflowResponse:
        """Cancels a pipeline step."""
        return await self.handle_cancel_pipeline_step_workflow(request)

    @rpc_errors
    @retry_transient
    async def InspectPipelineStepWorkflow(
        self, request: pipelines_v1_pipeline_step_workflow_service_pb2.InspectPipelineStepWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_step_workflow_service_pb2.InspectPipelineStepWorkflowResponse:
        """Returns a pipeline step."""
        return await self.handle_inspect_pipeline_step_workflow(request)

    @rpc_errors
    @retry_transient
    async def ListPipelineStepWorkflows(
        self, request: pipelines_v1_pipeline_step_workflow_service_pb2.ListPipelineStepWorkflowsRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_step_workflow_service_pb2.ListPipelineStepWorkflowsResponse:
        """Lists pipeline steps a page at a time."""
        return await self.handle_list_pipeline_step_workflows(request)

    @rpc_errors
    async def SignalPipelineStepWorkflow(
        self, request: pipelines_v1_pipeline_step_workflow_service_pb2.SignalPipelineStepWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_step_workflow_service_pb2.SignalPipelineStepWorkflowResponse:
        """Signals a pipeline step."""
        return await self.handle_signal_pipeline_step_workflow(request)

    @rpc_errors
    async def StartPipelineStepWorkflow(
        self, request: pipelines_v1_pipeline_step_workflow_service_pb2.StartPipelineStepWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_step_workflow_service_pb2.StartPipelineStepWorkflowResponse:
        """Starts a pipeline step."""
        return await self.handle_start_pipeline_step_workflow(request)

    async def handle_advance_pipeline_step_workflow(
        self,
        request: pipelines_v1_pipeline_step_workflow_service_pb2.AdvancePipelineStepWorkflowRequest
    ) -> pipelines_v1_pipeline_step_workflow_service_pb2.AdvancePipelineStepWorkflowResponse:
        """Advances a pipeline step."""
        deps = self.deps
        response = pipelines_v1_pipeline_step_workflow_service_pb2.AdvancePipelineStepWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('AdvancePipelineStepWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'AdvancePipelineStepWorkflow',
                {'reason': request.reason}
            )
            await deps.repository.save_pipeline_step(request.context.tenant_id, request.pipeline_step)
            response_0 = metrics_v1_metric_series_history_service_pb2.RevertMetricSeriesResponse()
            response_1 = pipelines_v1_pipeline_lifecycle_service_pb2.SchedulePipelineExpiryResponse()
            response_2 = pipelines_v1_pipeline_step_export_service_pb2.ListPipelineStepExportsResponse()
            response_3 = pipelines_v1_pipeline_step_approval_service_pb2.DelegatePipelineStepApprovalResponse()
            outgoing_0 = metrics_v1_metric_series_history_service_pb2.RevertMetricSeriesRequest(
                context=request.context,
                metric_series=metrics_v1_metrics_pb2.MetricSeries(
                    audit=common_v1_audit_pb2.AuditInfo(
                        created_at=request.pipeline_step.audit.created_at,
                        updated_by=request.pipeline_step.audit.updated_by
                    ),
                    components={
                        'primary': metrics_v1_metrics_pb2.MetricSeriesComponent(
                            description=request.pipeline_step.description
                        )
                    },
                    owner=identity_v1_refs_pb2.UserRef(email=request.pipeline_step.owner.email)
                )
            )
            outgoing_3 = pipelines_v1_pipeline_step_approval_service_pb2.DelegatePipelineStepApprovalRequest(
                context=request.context,
                pipeline_step=pipelines_v1_pipelines_pb2.PipelineStep(
                    owner=identity_v1_refs_pb2.UserRef(display_name=request.pipeline_step.owner.display_name)
                )
            )
            response_0, response_3 = await asyncio.gather(
                deps.clients.metrics_metric_series_history.RevertMetricSeries(
                    outgoing_0,
                    timeout=deps.settings.timeout
                ),
                deps.clients.pipelines_pipeline_step_approval.DelegatePipelineStepApproval(
                    outgoing_3,
                    timeout=deps.settings.timeout
                ),
            )
            outgoing_1 = pipelines_v1_pipeline_lifecycle_service_pb2.SchedulePipelineExpiryRequest(
                context=request.context,
                pipeline=pipelines_v1_pipelines_pb2.Pipeline(
                    audit=common_v1_audit_pb2.AuditInfo(etag=request.pipeline_step.audit.etag),
                    participants=[
                        pipelines_v1_pipelines_pb2.PipelineParticipant(
                            contact=common_v1_contact_pb2.ContactInfo(email=response_0.metric_series.owner.email)
                        )
                    ]
                )
            )
            send_1 = partial(
                deps.clients.pipelines_pipeline_lifecycle.SchedulePipelineExpiry,
                timeout=deps.settings.timeout
            )
            response_1 = await send_1(outgoing_1)
            outgoing_2 = pipelines_v1_pipeline_step_export_service_pb2.ListPipelineStepExportsRequest(
                context=request.context,
                filter=pipelines_v1_pipeline_step_export_service_pb2.ListPipelineStepExportsRequest.Filter(
                    created_after=request.pipeline_step.audit.created_at,
                    labels=dict(request.pipeline_step.parameters),
                    owner_id=response_0.metric_series.components.get(
                        'primary',
                        metrics_v1_metrics_pb2.MetricSeriesComponent()
                    ).component_id,
                    region=response_1.pipeline.location.region
                )
            )
            response_2 = await hooks.pipeline_step_workflow_advance_pipeline_step_workflow2(
                deps.clients.pipelines_pipeline_step_export,
                outgoing_2,
                deps.settings.timeout
            )
            returned_0_0 = response_0.metric_series.owner.user_id
            if returned_0_0:
                response.pipeline_step.owner.user_id = returned_0_0
            returned_1_0 = response_1.pipeline.audit.updated_by
            if returned_1_0:
                response.pipeline_step.audit.updated_by = returned_1_0
            returned_1_1 = response_1.outcome.status
            if returned_1_1:
                response.outcome.status = returned_1_1
            returned_2_0 = response_2.result.status
            if returned_2_0:
                response.result.status = returned_2_0
            returned_3_0 = response_3.pipeline_step.status
            if returned_3_0:
                response.pipeline_step.status = returned_3_0
            echoed_0 = request.pipeline_step_id
            response.pipeline_step.pipeline_step_id = echoed_0
            echoed_1 = request.details.parameters
            response.pipeline_step.parameters.update(echoed_1)
            return response

    async def handle_cancel_pipeline_step_workflow(
        self,
        request: pipelines_v1_pipeline_step_workflow_service_pb2.CancelPipelineStepWorkflowRequest
    ) -> pipelines_v1_pipeline_step_workflow_service_pb2.CancelPipelineStepWorkflowResponse:
        """Cancels a pipeline step."""
        deps = self.deps
        response = pipelines_v1_pipeline_step_workflow_service_pb2.CancelPipelineStepWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CancelPipelineStepWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'CancelPipelineStepWorkflow',
                {'reason': request.reason}
            )
            await deps.repository.save_pipeline_step(request.context.tenant_id, request.pipeline_step)
            response_0 = identity_v1_user_service_pb2.SearchUsersResponse()
            response_1 = pipelines_v1_pipeline_run_lifecycle_service_pb2.SchedulePipelineRunExpiryResponse()
            outgoing_0 = identity_v1_user_service_pb2.SearchUsersRequest(
                context=request.context,
                filter=identity_v1_user_service_pb2.SearchUsersRequest.Filter(
                    created_after=request.pipeline_step.audit.created_at
                )
            )
            port_0: PipelineStepWorkflowCancelPipelineStepWorkflow0Port = PipelineStepWorkflowCancelPipelineStepWorkflow0Adapter(
                deps.clients.identity_user,
                deps.settings.timeout
            )
            response_0 = await port_0.execute(outgoing_0)
            outgoing_1 = pipelines_v1_pipeline_run_lifecycle_service_pb2.SchedulePipelineRunExpiryRequest(
                context=request.context,
                details=pipelines_v1_pipeline_run_lifecycle_service_pb2.SchedulePipelineRunExpiryRequest.Details(
                    notify=common_v1_contact_pb2.ContactInfo(email=request.details.notify.email)
                ),
                pipeline_run=pipelines_v1_pipelines_pb2.PipelineRun(
                    audit=common_v1_audit_pb2.AuditInfo(created_by=request.pipeline_step.audit.created_by),
                    customer=pipelines_v1_refs_pb2.PipelineRef(display_name=request.pipeline_step.owner.display_name)
                )
            )
            steps_1 = [
                partial(
                    deps.clients.pipelines_pipeline_run_lifecycle.SchedulePipelineRunExpiry,
                    outgoing_1,
                    timeout=deps.settings.timeout
                )
            ]
            results_1 = await run_steps(steps_1)
            response_1 = results_1[-1]
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.result.message = returned_0_0
            returned_0_1 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_1)
            returned_1_0 = response_1.pipeline_run.audit.etag
            if returned_1_0:
                response.pipeline_step.audit.etag = returned_1_0
            returned_1_1 = response_1.result.status
            if returned_1_1:
                response.result.status = returned_1_1
            echoed_0 = request.pipeline_step_id
            response.pipeline_step.pipeline_step_id = echoed_0
            echoed_1 = request.pipeline_step.name
            response.pipeline_step.name = echoed_1
            return response

    async def handle_inspect_pipeline_step_workflow(
        self,
        request: pipelines_v1_pipeline_step_workflow_service_pb2.InspectPipelineStepWorkflowRequest
    ) -> pipelines_v1_pipeline_step_workflow_service_pb2.InspectPipelineStepWorkflowResponse:
        """Returns a pipeline step."""
        deps = self.deps
        response = pipelines_v1_pipeline_step_workflow_service_pb2.InspectPipelineStepWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('InspectPipelineStepWorkflow', extra={'fields': {'domain': 'pipelines'}})
            await deps.repository.audit(request.context.tenant_id, 'InspectPipelineStepWorkflow', {})
            response_0 = identity_v1_user_service_pb2.WatchUsersResponse()
            outgoing_0 = identity_v1_user_service_pb2.WatchUsersRequest(
                context=request.context,
                subscriber=common_v1_contact_pb2.ContactInfo(email=request.context.actor.email)
            )
            async for chunk_0 in deps.clients.identity_user.WatchUsers(outgoing_0, timeout=deps.settings.timeout):
                response_0 = chunk_0
            echoed_0 = request.pipeline_step_id
            response.pipeline_step.pipeline_step_id = echoed_0
            return response

    async def handle_list_pipeline_step_workflows(
        self,
        request: pipelines_v1_pipeline_step_workflow_service_pb2.ListPipelineStepWorkflowsRequest
    ) -> pipelines_v1_pipeline_step_workflow_service_pb2.ListPipelineStepWorkflowsResponse:
        """Lists pipeline steps a page at a time."""
        deps = self.deps
        response = pipelines_v1_pipeline_step_workflow_service_pb2.ListPipelineStepWorkflowsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ListPipelineStepWorkflows', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ListPipelineStepWorkflows',
                {'order_by': request.order_by}
            )
            return response

    async def handle_signal_pipeline_step_workflow(
        self,
        request: pipelines_v1_pipeline_step_workflow_service_pb2.SignalPipelineStepWorkflowRequest
    ) -> pipelines_v1_pipeline_step_workflow_service_pb2.SignalPipelineStepWorkflowResponse:
        """Signals a pipeline step."""
        deps = self.deps
        response = pipelines_v1_pipeline_step_workflow_service_pb2.SignalPipelineStepWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SignalPipelineStepWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'SignalPipelineStepWorkflow',
                {'reason': request.reason}
            )
            await deps.repository.save_pipeline_step(request.context.tenant_id, request.pipeline_step)
            response_0 = pipelines_v1_pipeline_run_lifecycle_service_pb2.SchedulePipelineRunExpiryResponse()
            outgoing_0 = pipelines_v1_pipeline_run_lifecycle_service_pb2.SchedulePipelineRunExpiryRequest(
                context=request.context,
                details=pipelines_v1_pipeline_run_lifecycle_service_pb2.SchedulePipelineRunExpiryRequest.Details(
                    notify=common_v1_contact_pb2.ContactInfo(phone=request.details.notify.phone)
                )
            )
            response_0 = cast(pipelines_v1_pipeline_run_lifecycle_service_pb2.SchedulePipelineRunExpiryResponse, await deps.bus.request(
                'acme.pipelines.v1.PipelineStepWorkflowService/SignalPipelineStepWorkflow/0', outgoing_0, deps.settings.timeout,
            ))
            returned_0_0 = response_0.outcome.effective_at
            if returned_0_0.ListFields():
                response.outcome.effective_at.MergeFrom(returned_0_0)
            returned_0_1 = response_0.result.message
            if returned_0_1:
                response.result.message = returned_0_1
            echoed_0 = request.pipeline_step_id
            response.pipeline_step.pipeline_step_id = echoed_0
            echoed_1 = request.pipeline_step.description
            response.pipeline_step.description = echoed_1
            return response

    async def handle_start_pipeline_step_workflow(
        self,
        request: pipelines_v1_pipeline_step_workflow_service_pb2.StartPipelineStepWorkflowRequest
    ) -> pipelines_v1_pipeline_step_workflow_service_pb2.StartPipelineStepWorkflowResponse:
        """Starts a pipeline step."""
        deps = self.deps
        response = pipelines_v1_pipeline_step_workflow_service_pb2.StartPipelineStepWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('StartPipelineStepWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'StartPipelineStepWorkflow',
                {'reason': request.reason}
            )
            await deps.repository.save_pipeline_step(request.context.tenant_id, request.pipeline_step)
            response_0 = search_v1_search_index_validation_service_pb2.ValidateSearchIndexResponse()
            response_1 = pipelines_v1_pipeline_step_export_service_pb2.RetryPipelineStepExportResponse()
            response_2 = pipelines_v1_pipeline_step_export_service_pb2.SchedulePipelineStepExportResponse()
            outgoing_0 = search_v1_search_index_validation_service_pb2.ValidateSearchIndexRequest(
                context=request.context,
                details=search_v1_search_index_validation_service_pb2.ValidateSearchIndexRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(
                        email=request.pipeline_step.owner.email,
                        preferred_channel=request.details.notify.preferred_channel
                    )
                )
            )
            response_0 = await deps.clients.search_search_index_validation.ValidateSearchIndex(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = pipelines_v1_pipeline_step_export_service_pb2.RetryPipelineStepExportRequest(
                context=request.context,
                details=pipelines_v1_pipeline_step_export_service_pb2.RetryPipelineStepExportRequest.Details(
                    notify=common_v1_contact_pb2.ContactInfo(email=request.details.notify.email)
                ),
                pipeline_step=pipelines_v1_pipelines_pb2.PipelineStep(
                    audit=common_v1_audit_pb2.AuditInfo(updated_at=request.pipeline_step.audit.updated_at),
                    block=pipelines_v1_pipelines_pb2.PipelineStepBlockAction(reason=request.pipeline_step.block.reason)
                )
            )
            method_name_1 = 'RetryPipelineStepExport'
            response_1 = await getattr(
                deps.clients.pipelines_pipeline_step_export,
                method_name_1
            )(outgoing_1, timeout=deps.settings.timeout)
            fields_2: dict[str, Any] = {
                'annotations': dict(request.annotations),
                'context': request.context,
                'pipeline_step_id': response_1.pipeline_step.pipeline_step_id,
                'reason': request.pipeline_step.block.reason
            }
            outgoing_2 = pipelines_v1_pipeline_step_export_service_pb2.SchedulePipelineStepExportRequest(**fields_2)
            response_2 = await deps.clients.pipelines_pipeline_step_export.SchedulePipelineStepExport(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.status
            if returned_0_0:
                response.outcome.status = returned_0_0
            returned_0_1 = response_0.outcome.status
            if returned_0_1:
                response.result.status = returned_0_1
            returned_1_0 = response_1.pipeline_step.effective
            if returned_1_0.ListFields():
                response.pipeline_step.effective.MergeFrom(returned_1_0)
            returned_2_0 = response_2.result.correlation_id
            if returned_2_0:
                response.result.correlation_id = returned_2_0
            returned_2_1 = response_2.result.message
            if returned_2_1:
                response.result.message = returned_2_1
            echoed_0 = request.pipeline_step_id
            response.pipeline_step.pipeline_step_id = echoed_0
            echoed_1 = request.pipeline_step.parameters
            response.pipeline_step.parameters.update(echoed_1)
            return response
