"""Routes pipelines through approval, with escalation and delegation."""

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
from google.protobuf.json_format import MessageToJson
from google.protobuf.json_format import Parse
import grpc

from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.datasets.v1 import refs_pb2 as datasets_v1_refs_pb2
from acme.featurestore.v1 import (
    feature_value_workflow_service_pb2 as featurestore_v1_feature_value_workflow_service_pb2,
)
from acme.featurestore.v1 import feature_view_workflow_service_pb2 as featurestore_v1_feature_view_workflow_service_pb2
from acme.featurestore.v1 import featurestore_pb2 as featurestore_v1_featurestore_pb2
from acme.forms.v1 import form_query_service_pb2 as forms_v1_form_query_service_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.metrics.v1 import dashboard_admin_service_pb2 as metrics_v1_dashboard_admin_service_pb2
from acme.metrics.v1 import metric_alert_history_service_pb2 as metrics_v1_metric_alert_history_service_pb2
from acme.metrics.v1 import metric_series_export_service_pb2 as metrics_v1_metric_series_export_service_pb2
from acme.metrics.v1 import metrics_pb2 as metrics_v1_metrics_pb2
from acme.modelregistry.v1 import (
    registered_model_reporting_service_pb2 as modelregistry_v1_registered_model_reporting_service_pb2,
)
from acme.pipelines.v1 import pipeline_approval_service_pb2 as pipelines_v1_pipeline_approval_service_pb2
from acme.pipelines.v1 import pipeline_approval_service_pb2_grpc as pipelines_v1_pipeline_approval_service_pb2_grpc
from acme.pipelines.v1 import pipeline_calculation_service_pb2 as pipelines_v1_pipeline_calculation_service_pb2
from acme.pipelines.v1 import pipeline_reporting_service_pb2 as pipelines_v1_pipeline_reporting_service_pb2
from acme.pipelines.v1 import pipeline_reporting_service_pb2_grpc as pipelines_v1_pipeline_reporting_service_pb2_grpc
from acme.pipelines.v1 import pipeline_run_import_service_pb2 as pipelines_v1_pipeline_run_import_service_pb2
from acme.pipelines.v1 import pipeline_run_lifecycle_service_pb2 as pipelines_v1_pipeline_run_lifecycle_service_pb2
from acme.pipelines.v1 import pipeline_run_reporting_service_pb2 as pipelines_v1_pipeline_run_reporting_service_pb2
from acme.pipelines.v1 import pipeline_run_sync_service_pb2 as pipelines_v1_pipeline_run_sync_service_pb2
from acme.pipelines.v1 import pipeline_step_reporting_service_pb2 as pipelines_v1_pipeline_step_reporting_service_pb2
from acme.pipelines.v1 import pipeline_sync_service_pb2 as pipelines_v1_pipeline_sync_service_pb2
from acme.pipelines.v1 import pipelines_pb2 as pipelines_v1_pipelines_pb2
from acme.pipelines.v1 import refs_pb2 as pipelines_v1_refs_pb2

from acme_data.domains.pipelines.adapters import PipelineApprovalDelegatePipelineApproval0Adapter
from acme_data.domains.pipelines.adapters import PipelineApprovalDelegatePipelineApproval0Port
from acme_data.domains.pipelines.adapters import PipelineApprovalDelegatePipelineApproval2Adapter
from acme_data.domains.pipelines.dependencies import Dependencies
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import run_steps
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_id
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class PipelineApprovalServicer(pipelines_v1_pipeline_approval_service_pb2_grpc.PipelineApprovalServiceServicer):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    async def ApprovePipeline(
        self, request: pipelines_v1_pipeline_approval_service_pb2.ApprovePipelineRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_approval_service_pb2.ApprovePipelineResponse:
        """Approves a pipeline."""
        return await self.handle_approve_pipeline(request)

    @rpc_errors
    async def DelegatePipelineApproval(
        self, request: pipelines_v1_pipeline_approval_service_pb2.DelegatePipelineApprovalRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_approval_service_pb2.DelegatePipelineApprovalResponse:
        """Delegates a pipeline."""
        return await self.handle_delegate_pipeline_approval(request)

    @rpc_errors
    async def EscalatePipeline(
        self, request: pipelines_v1_pipeline_approval_service_pb2.EscalatePipelineRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_approval_service_pb2.EscalatePipelineResponse:
        """Escalates a pipeline."""
        return await self.handle_escalate_pipeline(request)

    @rpc_errors
    @retry_transient
    async def GetPipelineApprovalStatus(
        self, request: pipelines_v1_pipeline_approval_service_pb2.GetPipelineApprovalStatusRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_approval_service_pb2.GetPipelineApprovalStatusResponse:
        """Returns a pipeline."""
        return await self.handle_get_pipeline_approval_status(request)

    @rpc_errors
    @retry_transient
    async def ListPendingPipelines(
        self, request: pipelines_v1_pipeline_approval_service_pb2.ListPendingPipelinesRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_approval_service_pb2.ListPendingPipelinesResponse:
        """Lists pipelines a page at a time."""
        return await self.handle_list_pending_pipelines(request)

    @rpc_errors
    async def RejectPipeline(
        self, request: pipelines_v1_pipeline_approval_service_pb2.RejectPipelineRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_approval_service_pb2.RejectPipelineResponse:
        """Rejects a pipeline."""
        return await self.handle_reject_pipeline(request)

    @rpc_errors
    async def SubmitPipeline(
        self, request: pipelines_v1_pipeline_approval_service_pb2.SubmitPipelineRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_approval_service_pb2.SubmitPipelineResponse:
        """Submits a pipeline."""
        return await self.handle_submit_pipeline(request)

    async def handle_approve_pipeline(
        self,
        request: pipelines_v1_pipeline_approval_service_pb2.ApprovePipelineRequest
    ) -> pipelines_v1_pipeline_approval_service_pb2.ApprovePipelineResponse:
        """Approves a pipeline."""
        deps = self.deps
        response = pipelines_v1_pipeline_approval_service_pb2.ApprovePipelineResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ApprovePipeline', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'ApprovePipeline', {'reason': request.reason})
            await deps.repository.save_pipeline(request.context.tenant_id, request.pipeline)
            response_0 = pipelines_v1_pipeline_run_reporting_service_pb2.GeneratePipelineRunReportResponse()
            outgoing_0 = pipelines_v1_pipeline_run_reporting_service_pb2.GeneratePipelineRunReportRequest()
            outgoing_0.context.CopyFrom(request.context)
            outgoing_0.annotations.update(dict(request.annotations))
            outgoing_0.context.tenant_id = tenant_id.get()
            response_0 = await deps.clients.pipelines_pipeline_run_reporting.GeneratePipelineRunReport(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.status
            if returned_0_0:
                response.outcome.status = returned_0_0
            returned_0_1 = response_0.result.details
            response.result.details.update(returned_0_1)
            echoed_0 = request.pipeline_id
            response.pipeline.pipeline_id = echoed_0
            echoed_1 = request.details.effective_at
            response.outcome.effective_at.CopyFrom(echoed_1)
            return response

    async def handle_delegate_pipeline_approval(
        self,
        request: pipelines_v1_pipeline_approval_service_pb2.DelegatePipelineApprovalRequest
    ) -> pipelines_v1_pipeline_approval_service_pb2.DelegatePipelineApprovalResponse:
        """Delegates a pipeline."""
        deps = self.deps
        response = pipelines_v1_pipeline_approval_service_pb2.DelegatePipelineApprovalResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('DelegatePipelineApproval', extra={'fields': {'approver_email': request.details.approver_email}})
            await deps.repository.audit(
                request.context.tenant_id,
                'DelegatePipelineApproval',
                {'approver_email': request.details.approver_email}
            )
            await deps.repository.save_pipeline(request.context.tenant_id, request.pipeline)
            response_0 = metrics_v1_metric_series_export_service_pb2.ScheduleMetricSeriesExportResponse()
            response_1 = featurestore_v1_feature_value_workflow_service_pb2.AdvanceFeatureValueWorkflowResponse()
            response_2 = pipelines_v1_pipeline_calculation_service_pb2.ExplainPipelineCalculationResponse()
            response_3 = pipelines_v1_pipeline_run_import_service_pb2.ValidatePipelineRunImportResponse()
            outgoing_0 = metrics_v1_metric_series_export_service_pb2.ScheduleMetricSeriesExportRequest(
                annotations=dict(request.annotations),
                context=request.context,
                reason=request.reason
            )
            port_0: PipelineApprovalDelegatePipelineApproval0Port = PipelineApprovalDelegatePipelineApproval0Adapter(
                deps.clients.metrics_metric_series_export,
                deps.settings.timeout
            )
            response_0 = await port_0.execute(outgoing_0)
            outgoing_1 = featurestore_v1_feature_value_workflow_service_pb2.AdvanceFeatureValueWorkflowRequest(
                context=request.context,
                details=featurestore_v1_feature_value_workflow_service_pb2.AdvanceFeatureValueWorkflowRequest.Details(
                    notify=common_v1_contact_pb2.ContactInfo(email=request.pipeline.organizer.email)
                ),
                feature_value=featurestore_v1_featurestore_pb2.FeatureValue(
                    subject=datasets_v1_refs_pb2.DatasetRef(display_name=request.pipeline.organizer.display_name)
                )
            )
            steps_1 = [
                partial(
                    deps.clients.featurestore_feature_value_workflow.AdvanceFeatureValueWorkflow,
                    outgoing_1,
                    timeout=deps.settings.timeout
                )
            ]
            results_1 = await run_steps(steps_1)
            response_1 = results_1[-1]
            outgoing_2 = pipelines_v1_pipeline_calculation_service_pb2.ExplainPipelineCalculationRequest(
                context=request.context,
                pipeline=pipelines_v1_pipelines_pb2.Pipeline(
                    audit=common_v1_audit_pb2.AuditInfo(created_by=request.pipeline.audit.created_by),
                    location=common_v1_address_pb2.PostalAddress(locality=request.pipeline.location.locality),
                    organizer=identity_v1_refs_pb2.UserRef(display_name=response_1.feature_value.subject.display_name),
                    weekly=pipelines_v1_pipelines_pb2.PipelineWeeklyRule(interval=request.pipeline.daily.interval)
                )
            )
            response_2 = await PipelineApprovalDelegatePipelineApproval2Adapter(
                deps.clients.pipelines_pipeline_calculation,
                deps.settings.timeout
            )(outgoing_2)
            outgoing_3 = pipelines_v1_pipeline_run_import_service_pb2.ValidatePipelineRunImportRequest(
                context=request.context,
                pipeline_run=pipelines_v1_pipelines_pb2.PipelineRun(
                    assignee=identity_v1_refs_pb2.UserRef(email=response_2.pipeline.organizer.email),
                    audit=common_v1_audit_pb2.AuditInfo(created_at=response_2.pipeline.audit.created_at),
                    customer=pipelines_v1_refs_pb2.PipelineRef(display_name=request.details.approver.display_name)
                )
            )
            response_3 = cast(pipelines_v1_pipeline_run_import_service_pb2.ValidatePipelineRunImportResponse, await deps.bus.request(
                'acme.pipelines.v1.PipelineApprovalService/DelegatePipelineApproval/3', outgoing_3, deps.settings.timeout,
            ))
            returned_0_0 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_0)
            returned_0_1 = response_0.result.message
            if returned_0_1:
                response.result.message = returned_0_1
            returned_1_0 = response_1.outcome.next_steps
            response.outcome.next_steps.extend(returned_1_0)
            returned_2_0 = response_2.pipeline.organizer
            if returned_2_0.ListFields():
                response.pipeline.organizer.MergeFrom(returned_2_0)
            returned_2_1 = response_2.pipeline.location
            if returned_2_1.ListFields():
                response.pipeline.location.MergeFrom(returned_2_1)
            returned_3_0 = response_3.pipeline_run.requester.email
            if returned_3_0:
                response.pipeline.organizer.email = returned_3_0
            echoed_0 = request.pipeline_id
            response.pipeline.pipeline_id = echoed_0
            echoed_1 = request.details.effective_at
            response.outcome.effective_at.CopyFrom(echoed_1)
            return response

    async def handle_escalate_pipeline(
        self,
        request: pipelines_v1_pipeline_approval_service_pb2.EscalatePipelineRequest
    ) -> pipelines_v1_pipeline_approval_service_pb2.EscalatePipelineResponse:
        """Escalates a pipeline."""
        deps = self.deps
        response = pipelines_v1_pipeline_approval_service_pb2.EscalatePipelineResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('EscalatePipeline', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'EscalatePipeline', {'reason': request.reason})
            await deps.repository.save_pipeline(request.context.tenant_id, request.pipeline)
            response_0 = modelregistry_v1_registered_model_reporting_service_pb2.ScheduleRegisteredModelReportResponse()
            response_1 = pipelines_v1_pipeline_run_lifecycle_service_pb2.SchedulePipelineRunExpiryResponse()
            response_2 = pipelines_v1_pipeline_sync_service_pb2.ListPipelineConflictsResponse()
            outgoing_0 = modelregistry_v1_registered_model_reporting_service_pb2.ScheduleRegisteredModelReportRequest(
                annotations=dict(request.annotations),
                context=request.context
            )
            response_0 = await deps.clients.modelregistry_registered_model_reporting.ScheduleRegisteredModelReport(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = pipelines_v1_pipeline_run_lifecycle_service_pb2.SchedulePipelineRunExpiryRequest(
                context=request.context,
                pipeline_run=pipelines_v1_pipelines_pb2.PipelineRun(
                    assignee=identity_v1_refs_pb2.UserRef(email=request.pipeline.organizer.email),
                    audit=common_v1_audit_pb2.AuditInfo(updated_by=request.pipeline.audit.updated_by)
                )
            )
            method_name_1 = 'SchedulePipelineRunExpiry'
            response_1 = await getattr(
                deps.clients.pipelines_pipeline_run_lifecycle,
                method_name_1
            )(outgoing_1, timeout=deps.settings.timeout)
            fields_2: dict[str, Any] = {
                'context': request.context,
                'filter': {
                    'created_after': request.pipeline.audit.updated_at,
                    'owner_id': response_1.pipeline_run.assignee.user_id,
                    'region': request.pipeline.location.region
                }
            }
            outgoing_2 = pipelines_v1_pipeline_sync_service_pb2.ListPipelineConflictsRequest(**fields_2)
            response_2 = await deps.clients.pipelines_pipeline_sync.ListPipelineConflicts(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.outcome.message = returned_0_0
            returned_0_1 = response_0.result.details
            response.result.details.update(returned_0_1)
            returned_1_0 = response_1.pipeline_run.audit.etag
            if returned_1_0:
                response.pipeline.audit.etag = returned_1_0
            returned_2_0 = response_2.result.details
            response.result.details.update(returned_2_0)
            returned_2_1 = response_2.result.correlation_id
            if returned_2_1:
                response.result.correlation_id = returned_2_1
            echoed_0 = request.pipeline_id
            response.pipeline.pipeline_id = echoed_0
            echoed_1 = request.details.effective_at
            response.outcome.effective_at.CopyFrom(echoed_1)
            return response

    async def handle_get_pipeline_approval_status(
        self,
        request: pipelines_v1_pipeline_approval_service_pb2.GetPipelineApprovalStatusRequest
    ) -> pipelines_v1_pipeline_approval_service_pb2.GetPipelineApprovalStatusResponse:
        """Returns a pipeline."""
        deps = self.deps
        response = pipelines_v1_pipeline_approval_service_pb2.GetPipelineApprovalStatusResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('GetPipelineApprovalStatus', extra={'fields': {'domain': 'pipelines'}})
            await deps.repository.audit(request.context.tenant_id, 'GetPipelineApprovalStatus', {})
            response_0 = forms_v1_form_query_service_pb2.SuggestFormsResponse()
            response_1 = metrics_v1_metric_alert_history_service_pb2.ListMetricAlertVersionsResponse()
            outgoing_0 = forms_v1_form_query_service_pb2.SuggestFormsRequest(
                context=request.context,
                filter=forms_v1_form_query_service_pb2.SuggestFormsRequest.Filter(
                    labels=dict(request.context.baggage),
                    owner_id=request.pipeline_id
                )
            )
            response_0 = await deps.clients.forms_form_query.SuggestForms(outgoing_0, timeout=deps.settings.timeout)
            outgoing_1 = metrics_v1_metric_alert_history_service_pb2.ListMetricAlertVersionsRequest(
                context=request.context,
                filter=metrics_v1_metric_alert_history_service_pb2.ListMetricAlertVersionsRequest.Filter(
                    labels=dict(response_0.result.details)
                )
            )
            document_1 = MessageToJson(outgoing_1, preserving_proto_field_name=True)
            outgoing_1 = Parse(document_1, metrics_v1_metric_alert_history_service_pb2.ListMetricAlertVersionsRequest())
            response_1 = await deps.clients.metrics_metric_alert_history.ListMetricAlertVersions(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_0)
            returned_0_1 = response_0.result.details
            response.result.details.update(returned_0_1)
            returned_1_0 = response_1.result.status
            if returned_1_0:
                response.result.status = returned_1_0
            echoed_0 = request.pipeline_id
            response.pipeline.pipeline_id = echoed_0
            return response

    async def handle_list_pending_pipelines(
        self,
        request: pipelines_v1_pipeline_approval_service_pb2.ListPendingPipelinesRequest
    ) -> pipelines_v1_pipeline_approval_service_pb2.ListPendingPipelinesResponse:
        """Lists pipelines a page at a time."""
        deps = self.deps
        response = pipelines_v1_pipeline_approval_service_pb2.ListPendingPipelinesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ListPendingPipelines', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ListPendingPipelines',
                {'order_by': request.order_by}
            )
            response_0 = modelregistry_v1_registered_model_reporting_service_pb2.StreamRegisteredModelMetricsResponse()
            outgoing_0 = modelregistry_v1_registered_model_reporting_service_pb2.StreamRegisteredModelMetricsRequest(
                context=request.context,
                filter=modelregistry_v1_registered_model_reporting_service_pb2.StreamRegisteredModelMetricsRequest.Filter(
                    query=request.filter.query
                )
            )
            async for chunk_0 in deps.clients.modelregistry_registered_model_reporting.StreamRegisteredModelMetrics(
                outgoing_0,
                timeout=deps.settings.timeout
            ):
                response_0 = chunk_0
            return response

    async def handle_reject_pipeline(
        self,
        request: pipelines_v1_pipeline_approval_service_pb2.RejectPipelineRequest
    ) -> pipelines_v1_pipeline_approval_service_pb2.RejectPipelineResponse:
        """Rejects a pipeline."""
        deps = self.deps
        response = pipelines_v1_pipeline_approval_service_pb2.RejectPipelineResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('RejectPipeline', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'RejectPipeline', {'reason': request.reason})
            await deps.repository.save_pipeline(request.context.tenant_id, request.pipeline)
            response_0 = pipelines_v1_pipeline_run_sync_service_pb2.ReconcilePipelineRunsResponse()
            response_1 = pipelines_v1_pipeline_reporting_service_pb2.CountPipelineTotalsResponse()
            outgoing_0 = pipelines_v1_pipeline_run_sync_service_pb2.ReconcilePipelineRunsRequest(
                context=request.context,
                pipeline_run=pipelines_v1_pipelines_pb2.PipelineRun(
                    assignee=identity_v1_refs_pb2.UserRef(display_name=request.details.approver.display_name),
                    comments=[
                        pipelines_v1_pipelines_pb2.PipelineRunComment(created_at=request.pipeline.audit.created_at)
                    ]
                )
            )
            envelope_0 = AnyMessage()
            envelope_0.Pack(outgoing_0)
            outgoing_0 = pipelines_v1_pipeline_run_sync_service_pb2.ReconcilePipelineRunsRequest()
            if not envelope_0.Unpack(outgoing_0):
                raise ValueError("partner envelope contains the wrong request type")
            response_0 = await deps.clients.pipelines_pipeline_run_sync.ReconcilePipelineRuns(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = pipelines_v1_pipeline_reporting_service_pb2.CountPipelineTotalsRequest(
                context=request.context,
                filter=pipelines_v1_pipeline_reporting_service_pb2.CountPipelineTotalsRequest.Filter(
                    created_after=request.pipeline.audit.created_at,
                    region=request.pipeline.location.region
                )
            )
            registered_1 = cast(
                pipelines_v1_pipeline_reporting_service_pb2_grpc.PipelineReportingServiceStub,
                deps.clients.registry['acme.pipelines.v1.PipelineReportingService']
            )
            response_1 = await registered_1.CountPipelineTotals(outgoing_1, timeout=deps.settings.timeout)
            returned_0_0 = response_0.outcome.status
            if returned_0_0:
                response.result.status = returned_0_0
            returned_1_0 = response_1.result.message
            if returned_1_0:
                response.result.message = returned_1_0
            returned_1_1 = response_1.result.status
            if returned_1_1:
                response.outcome.status = returned_1_1
            echoed_0 = request.pipeline_id
            response.pipeline.pipeline_id = echoed_0
            echoed_1 = request.pipeline.organizer
            response.pipeline.organizer.CopyFrom(echoed_1)
            return response

    async def handle_submit_pipeline(
        self,
        request: pipelines_v1_pipeline_approval_service_pb2.SubmitPipelineRequest
    ) -> pipelines_v1_pipeline_approval_service_pb2.SubmitPipelineResponse:
        """Submits a pipeline."""
        deps = self.deps
        response = pipelines_v1_pipeline_approval_service_pb2.SubmitPipelineResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SubmitPipeline', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'SubmitPipeline', {'reason': request.reason})
            await deps.repository.save_pipeline(request.context.tenant_id, request.pipeline)
            response_0 = pipelines_v1_pipeline_step_reporting_service_pb2.ListPipelineStepReportsResponse()
            response_1 = metrics_v1_dashboard_admin_service_pb2.RepairDashboardResponse()
            response_2 = featurestore_v1_feature_view_workflow_service_pb2.CancelFeatureViewWorkflowResponse()
            outgoing_1 = metrics_v1_dashboard_admin_service_pb2.RepairDashboardRequest(
                context=request.context,
                dashboard=metrics_v1_metrics_pb2.Dashboard(
                    audit=common_v1_audit_pb2.AuditInfo(created_at=request.pipeline.audit.created_at)
                )
            )
            outgoing_2 = featurestore_v1_feature_view_workflow_service_pb2.CancelFeatureViewWorkflowRequest(
                context=request.context,
                feature_view=featurestore_v1_featurestore_pb2.FeatureView(
                    address=common_v1_address_pb2.PostalAddress(
                        country_code=request.pipeline.location.country_code,
                        postal_code=request.pipeline.location.postal_code
                    )
                )
            )
            response_1, response_2 = await asyncio.gather(
                deps.clients.metrics_dashboard_admin.RepairDashboard(outgoing_1, timeout=deps.settings.timeout),
                deps.clients.featurestore_feature_view_workflow.CancelFeatureViewWorkflow(
                    outgoing_2,
                    timeout=deps.settings.timeout
                ),
            )
            for item_0 in request.pipeline.participants:
                outgoing_0 = pipelines_v1_pipeline_step_reporting_service_pb2.ListPipelineStepReportsRequest(
                    context=request.context,
                    filter=pipelines_v1_pipeline_step_reporting_service_pb2.ListPipelineStepReportsRequest.Filter(
                        created_after=request.pipeline.audit.updated_at,
                        labels=dict(request.pipeline.metadata),
                        owner_id=item_0.participant_id,
                        region=request.pipeline.location.region
                    )
                )
                response_0 = await deps.clients.pipelines_pipeline_step_reporting.ListPipelineStepReports(
                    outgoing_0,
                    timeout=deps.settings.timeout
                )
            returned_1_0 = response_1.outcome.reference_id
            if returned_1_0:
                response.outcome.reference_id = returned_1_0
            returned_1_1 = response_1.dashboard.metadata
            response.pipeline.metadata.update(returned_1_1)
            returned_2_0 = response_2.outcome.status
            if returned_2_0:
                response.result.status = returned_2_0
            returned_2_1 = response_2.feature_view.address.region
            if returned_2_1:
                response.pipeline.location.region = returned_2_1
            echoed_0 = request.pipeline_id
            response.pipeline.pipeline_id = echoed_0
            echoed_1 = request.details.effective_at
            response.outcome.effective_at.CopyFrom(echoed_1)
            return response
