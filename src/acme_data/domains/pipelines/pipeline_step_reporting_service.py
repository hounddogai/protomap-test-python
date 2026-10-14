"""Builds and schedules reports about pipeline steps."""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import cast
import asyncio
import logging

import grpc

from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.featurestore.v1 import feature_view_approval_service_pb2 as featurestore_v1_feature_view_approval_service_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.lineage.v1 import lineage_edge_approval_service_pb2 as lineage_v1_lineage_edge_approval_service_pb2
from acme.lineage.v1 import lineage_edge_approval_service_pb2_grpc as lineage_v1_lineage_edge_approval_service_pb2_grpc
from acme.lineage.v1 import lineage_pb2 as lineage_v1_lineage_pb2
from acme.metrics.v1 import metric_alert_history_service_pb2 as metrics_v1_metric_alert_history_service_pb2
from acme.metrics.v1 import metric_alert_query_service_pb2 as metrics_v1_metric_alert_query_service_pb2
from acme.metrics.v1 import metrics_pb2 as metrics_v1_metrics_pb2
from acme.modelregistry.v1 import modelregistry_pb2 as modelregistry_v1_modelregistry_pb2
from acme.modelregistry.v1 import (
    registered_model_approval_service_pb2 as modelregistry_v1_registered_model_approval_service_pb2,
)
from acme.pipelines.v1 import pipeline_query_service_pb2 as pipelines_v1_pipeline_query_service_pb2
from acme.pipelines.v1 import pipeline_reporting_service_pb2 as pipelines_v1_pipeline_reporting_service_pb2
from acme.pipelines.v1 import pipeline_step_reporting_service_pb2 as pipelines_v1_pipeline_step_reporting_service_pb2
from acme.pipelines.v1 import (
    pipeline_step_reporting_service_pb2_grpc as pipelines_v1_pipeline_step_reporting_service_pb2_grpc,
)
from acme.pipelines.v1 import pipeline_step_sync_service_pb2 as pipelines_v1_pipeline_step_sync_service_pb2
from acme.pipelines.v1 import pipelines_pb2 as pipelines_v1_pipelines_pb2
from acme.recruiting.v1 import job_opening_service_pb2 as recruiting_v1_job_opening_service_pb2
from acme.recruiting.v1 import recruiting_pb2 as recruiting_v1_recruiting_pb2

from acme_data.domains.pipelines import hooks
from acme_data.domains.pipelines.dependencies import Dependencies
from acme_data.domains.pipelines.models import PipelineStepReportingGeneratePipelineStepReport0Command
from acme_data.domains.pipelines.models import to_pipeline_step_reporting_generate_pipeline_step_report0_command
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_id
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class PipelineStepReportingServicer(
    pipelines_v1_pipeline_step_reporting_service_pb2_grpc.PipelineStepReportingServiceServicer
):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    @retry_transient
    async def CountPipelineStepTotals(
        self, request: pipelines_v1_pipeline_step_reporting_service_pb2.CountPipelineStepTotalsRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_step_reporting_service_pb2.CountPipelineStepTotalsResponse:
        """Counts pipeline steps by status."""
        return await self.handle_count_pipeline_step_totals(request)

    @rpc_errors
    async def DeletePipelineStepReport(
        self, request: pipelines_v1_pipeline_step_reporting_service_pb2.DeletePipelineStepReportRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_step_reporting_service_pb2.DeletePipelineStepReportResponse:
        """Deletes a pipeline step."""
        return await self.handle_delete_pipeline_step_report(request)

    @rpc_errors
    @retry_transient
    async def FetchPipelineStepReport(
        self, request: pipelines_v1_pipeline_step_reporting_service_pb2.FetchPipelineStepReportRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_step_reporting_service_pb2.FetchPipelineStepReportResponse:
        """Returns a pipeline step."""
        return await self.handle_fetch_pipeline_step_report(request)

    @rpc_errors
    async def GeneratePipelineStepReport(
        self, request: pipelines_v1_pipeline_step_reporting_service_pb2.GeneratePipelineStepReportRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_step_reporting_service_pb2.GeneratePipelineStepReportResponse:
        """Generates a pipeline step."""
        return await self.handle_generate_pipeline_step_report(request)

    @rpc_errors
    @retry_transient
    async def ListPipelineStepReports(
        self, request: pipelines_v1_pipeline_step_reporting_service_pb2.ListPipelineStepReportsRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_step_reporting_service_pb2.ListPipelineStepReportsResponse:
        """Lists pipeline steps a page at a time."""
        return await self.handle_list_pipeline_step_reports(request)

    @rpc_errors
    async def SchedulePipelineStepReport(
        self, request: pipelines_v1_pipeline_step_reporting_service_pb2.SchedulePipelineStepReportRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_step_reporting_service_pb2.SchedulePipelineStepReportResponse:
        """Schedules a pipeline step."""
        return await self.handle_schedule_pipeline_step_report(request)

    @stream_errors
    async def StreamPipelineStepMetrics(
        self, request: pipelines_v1_pipeline_step_reporting_service_pb2.StreamPipelineStepMetricsRequest, context: grpc.aio.ServicerContext,
    ) -> AsyncIterator[pipelines_v1_pipeline_step_reporting_service_pb2.StreamPipelineStepMetricsResponse]:
        """Streams the changes of pipeline steps as they happen."""
        response = await self.handle_stream_pipeline_step_metrics(request)
        for item in messages((response,)):
            yield item

    async def handle_count_pipeline_step_totals(
        self,
        request: pipelines_v1_pipeline_step_reporting_service_pb2.CountPipelineStepTotalsRequest
    ) -> pipelines_v1_pipeline_step_reporting_service_pb2.CountPipelineStepTotalsResponse:
        """Counts pipeline steps by status."""
        deps = self.deps
        response = pipelines_v1_pipeline_step_reporting_service_pb2.CountPipelineStepTotalsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CountPipelineStepTotals', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'CountPipelineStepTotals',
                {'order_by': request.order_by}
            )
            response_0 = pipelines_v1_pipeline_step_sync_service_pb2.ReconcilePipelineStepsResponse()
            outgoing_0 = pipelines_v1_pipeline_step_sync_service_pb2.ReconcilePipelineStepsRequest(
                context=request.context,
                pipeline_step=pipelines_v1_pipelines_pb2.PipelineStep(
                    owner=identity_v1_refs_pb2.UserRef(
                        email=request.context.actor.email,
                        user_id=request.context.actor.user_id
                    )
                )
            )
            response_0 = await deps.clients.pipelines_pipeline_step_sync.ReconcilePipelineSteps(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.outcome.status
            if returned_0_0:
                response.result.status = returned_0_0
            return response

    async def handle_delete_pipeline_step_report(
        self,
        request: pipelines_v1_pipeline_step_reporting_service_pb2.DeletePipelineStepReportRequest
    ) -> pipelines_v1_pipeline_step_reporting_service_pb2.DeletePipelineStepReportResponse:
        """Deletes a pipeline step."""
        deps = self.deps
        response = pipelines_v1_pipeline_step_reporting_service_pb2.DeletePipelineStepReportResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('DeletePipelineStepReport', extra={'fields': {'force': request.force}})
            await deps.repository.audit(request.context.tenant_id, 'DeletePipelineStepReport', {'force': request.force})
            response_0 = metrics_v1_metric_alert_query_service_pb2.FindMetricAlertsResponse()
            response_1 = pipelines_v1_pipeline_query_service_pb2.ResolvePipelinesResponse()
            response_2 = modelregistry_v1_registered_model_approval_service_pb2.ApproveRegisteredModelResponse()
            response_3 = lineage_v1_lineage_edge_approval_service_pb2.SubmitLineageEdgeResponse()
            outgoing_0 = metrics_v1_metric_alert_query_service_pb2.FindMetricAlertsRequest(
                context=request.context,
                filter=metrics_v1_metric_alert_query_service_pb2.FindMetricAlertsRequest.Filter(
                    owner_id=request.pipeline_step_id
                )
            )
            outgoing_1 = pipelines_v1_pipeline_query_service_pb2.ResolvePipelinesRequest(context=request.context)
            outgoing_2 = modelregistry_v1_registered_model_approval_service_pb2.ApproveRegisteredModelRequest(
                context=request.context,
                details=modelregistry_v1_registered_model_approval_service_pb2.ApproveRegisteredModelRequest.Details(
                    approver=identity_v1_refs_pb2.UserRef(user_id=request.context.actor.user_id)
                ),
                reason=request.reason,
                registered_model=modelregistry_v1_modelregistry_pb2.RegisteredModel(
                    audit=common_v1_audit_pb2.AuditInfo(etag=request.etag),
                    owner=identity_v1_refs_pb2.UserRef(email=request.context.actor.email)
                )
            )
            response_0, response_1, response_2 = await asyncio.gather(
                deps.clients.metrics_metric_alert_query.FindMetricAlerts(outgoing_0, timeout=deps.settings.timeout),
                deps.clients.pipelines_pipeline_query.ResolvePipelines(outgoing_1, timeout=deps.settings.timeout),
                deps.clients.modelregistry_registered_model_approval.ApproveRegisteredModel(
                    outgoing_2,
                    timeout=deps.settings.timeout
                ),
            )
            outgoing_3 = lineage_v1_lineage_edge_approval_service_pb2.SubmitLineageEdgeRequest(
                context=request.context,
                details=lineage_v1_lineage_edge_approval_service_pb2.SubmitLineageEdgeRequest.Details(
                    approver=identity_v1_refs_pb2.UserRef(
                        display_name=response_2.registered_model.owner.display_name,
                        user_id=response_2.registered_model.owner.user_id
                    )
                ),
                lineage_edge=lineage_v1_lineage_pb2.LineageEdge(
                    correlation_id=response_2.result.correlation_id,
                    measurements=[
                        lineage_v1_lineage_pb2.LineageEdgeMeasurement(unit=response_2.registered_model.dimensions.unit)
                    ]
                )
            )
            registered_3 = cast(
                lineage_v1_lineage_edge_approval_service_pb2_grpc.LineageEdgeApprovalServiceStub,
                deps.clients.registry['acme.lineage.v1.LineageEdgeApprovalService']
            )
            response_3 = await registered_3.SubmitLineageEdge(outgoing_3, timeout=deps.settings.timeout)
            returned_0_0 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_0)
            returned_1_0 = response_1.result.status
            if returned_1_0:
                response.result.status = returned_1_0
            returned_1_1 = response_1.result.correlation_id
            if returned_1_1:
                response.result.correlation_id = returned_1_1
            returned_2_0 = response_2.result.correlation_id
            if returned_2_0:
                response.result.correlation_id = returned_2_0
            returned_3_0 = response_3.result.message
            if returned_3_0:
                response.result.message = returned_3_0
            return response

    async def handle_fetch_pipeline_step_report(
        self,
        request: pipelines_v1_pipeline_step_reporting_service_pb2.FetchPipelineStepReportRequest
    ) -> pipelines_v1_pipeline_step_reporting_service_pb2.FetchPipelineStepReportResponse:
        """Returns a pipeline step."""
        deps = self.deps
        response = pipelines_v1_pipeline_step_reporting_service_pb2.FetchPipelineStepReportResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('FetchPipelineStepReport', extra={'fields': {'domain': 'pipelines'}})
            await deps.repository.audit(request.context.tenant_id, 'FetchPipelineStepReport', {})
            response_0 = pipelines_v1_pipeline_reporting_service_pb2.CountPipelineTotalsResponse()
            outgoing_0 = pipelines_v1_pipeline_reporting_service_pb2.CountPipelineTotalsRequest(
                context=request.context,
                filter=pipelines_v1_pipeline_reporting_service_pb2.CountPipelineTotalsRequest.Filter(
                    owner_id=request.pipeline_step_id
                )
            )
            response_0 = await deps.clients.pipelines_pipeline_reporting.CountPipelineTotals(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_0)
            returned_0_1 = response_0.result.details
            response.result.details.update(returned_0_1)
            echoed_0 = request.pipeline_step_id
            response.pipeline_step.pipeline_step_id = echoed_0
            return response

    async def handle_generate_pipeline_step_report(
        self,
        request: pipelines_v1_pipeline_step_reporting_service_pb2.GeneratePipelineStepReportRequest
    ) -> pipelines_v1_pipeline_step_reporting_service_pb2.GeneratePipelineStepReportResponse:
        """Generates a pipeline step."""
        deps = self.deps
        response = pipelines_v1_pipeline_step_reporting_service_pb2.GeneratePipelineStepReportResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('GeneratePipelineStepReport', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'GeneratePipelineStepReport',
                {'reason': request.reason}
            )
            response_0 = metrics_v1_metric_alert_query_service_pb2.CountMetricAlertsResponse()
            command_0 = PipelineStepReportingGeneratePipelineStepReport0Command.model_validate(
                {
                    'context': request.context,
                    'filter_labels': dict(request.details.filters),
                    'filter_owner_id': request.pipeline_step_id,
                    'filter_created_after': request.context.deadline
                }
            )
            outgoing_0 = to_pipeline_step_reporting_generate_pipeline_step_report0_command(command_0)
            response_0 = await deps.clients.metrics_metric_alert_query.CountMetricAlerts(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.result.message = returned_0_0
            echoed_0 = request.details.period
            response.period.CopyFrom(echoed_0)
            return response

    async def handle_list_pipeline_step_reports(
        self,
        request: pipelines_v1_pipeline_step_reporting_service_pb2.ListPipelineStepReportsRequest
    ) -> pipelines_v1_pipeline_step_reporting_service_pb2.ListPipelineStepReportsResponse:
        """Lists pipeline steps a page at a time."""
        deps = self.deps
        response = pipelines_v1_pipeline_step_reporting_service_pb2.ListPipelineStepReportsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ListPipelineStepReports', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ListPipelineStepReports',
                {'order_by': request.order_by}
            )
            response_0 = metrics_v1_metric_alert_history_service_pb2.RecordMetricAlertVersionResponse()
            outgoing_0 = metrics_v1_metric_alert_history_service_pb2.RecordMetricAlertVersionRequest(
                context=request.context,
                metric_alert=metrics_v1_metrics_pb2.MetricAlert(
                    audit=common_v1_audit_pb2.AuditInfo(created_at=request.filter.created_after),
                    owner=identity_v1_refs_pb2.UserRef(
                        email=request.context.actor.email,
                        user_id=request.context.actor.user_id
                    )
                )
            )
            response_0 = await deps.clients.metrics_metric_alert_history.RecordMetricAlertVersion(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.metric_alert.name
            returned_0_0_part_0 = response.pipeline_steps.add()
            if returned_0_0:
                returned_0_0_part_0.name = returned_0_0
            returned_0_1 = response_0.metric_alert.owner.display_name
            returned_0_1_part_0 = response.pipeline_steps.add()
            if returned_0_1:
                returned_0_1_part_0.owner.display_name = returned_0_1
            return response

    async def handle_schedule_pipeline_step_report(
        self,
        request: pipelines_v1_pipeline_step_reporting_service_pb2.SchedulePipelineStepReportRequest
    ) -> pipelines_v1_pipeline_step_reporting_service_pb2.SchedulePipelineStepReportResponse:
        """Schedules a pipeline step."""
        deps = self.deps
        response = pipelines_v1_pipeline_step_reporting_service_pb2.SchedulePipelineStepReportResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SchedulePipelineStepReport', extra={'fields': {'pipeline_step_id': request.pipeline_step_id}})
            await deps.repository.audit(
                request.context.tenant_id,
                'SchedulePipelineStepReport',
                {'pipeline_step_id': request.pipeline_step_id}
            )
            response_0 = recruiting_v1_job_opening_service_pb2.CloneJobOpeningResponse()
            response_1 = featurestore_v1_feature_view_approval_service_pb2.RejectFeatureViewResponse()
            outgoing_0 = recruiting_v1_job_opening_service_pb2.CloneJobOpeningRequest(
                context=request.context,
                job_opening=recruiting_v1_recruiting_pb2.JobOpening(
                    audit=common_v1_audit_pb2.AuditInfo(created_at=request.context.deadline),
                    lines=[recruiting_v1_recruiting_pb2.JobOpeningLine(attributes=dict(request.details.filters))],
                    metadata=dict(request.annotations)
                )
            )
            response_0 = await hooks.pipeline_step_reporting_schedule_pipeline_step_report0(
                deps.clients.recruiting_job_opening,
                outgoing_0,
                deps.settings.timeout
            )
            outgoing_1 = featurestore_v1_feature_view_approval_service_pb2.RejectFeatureViewRequest()
            outgoing_1.context.CopyFrom(request.context)
            outgoing_1.feature_view.audit.updated_at.CopyFrom(response_0.job_opening.audit.updated_at)
            outgoing_1.feature_view.audit.created_by = response_0.job_opening.audit.created_by
            outgoing_1.feature_view.audit.etag = response_0.job_opening.audit.etag
            outgoing_1.context.tenant_id = tenant_id.get()
            response_1 = await deps.clients.featurestore_feature_view_approval.RejectFeatureView(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.result.message = returned_0_0
            returned_1_0 = response_1.outcome.message
            if returned_1_0:
                response.result.message = returned_1_0
            returned_1_1 = response_1.result.status
            if returned_1_1:
                response.result.status = returned_1_1
            echoed_0 = request.details.period
            response.period.CopyFrom(echoed_0)
            return response

    async def handle_stream_pipeline_step_metrics(
        self,
        request: pipelines_v1_pipeline_step_reporting_service_pb2.StreamPipelineStepMetricsRequest
    ) -> pipelines_v1_pipeline_step_reporting_service_pb2.StreamPipelineStepMetricsResponse:
        """Streams the changes of pipeline steps as they happen."""
        deps = self.deps
        response = pipelines_v1_pipeline_step_reporting_service_pb2.StreamPipelineStepMetricsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('StreamPipelineStepMetrics', extra={'fields': {'owner_id': request.filter.owner_id}})
            await deps.repository.audit(
                request.context.tenant_id,
                'StreamPipelineStepMetrics',
                {'owner_id': request.filter.owner_id}
            )
            response_0 = pipelines_v1_pipeline_reporting_service_pb2.StreamPipelineMetricsResponse()
            outgoing_0 = pipelines_v1_pipeline_reporting_service_pb2.StreamPipelineMetricsRequest(
                context=request.context,
                filter=pipelines_v1_pipeline_reporting_service_pb2.StreamPipelineMetricsRequest.Filter(
                    region=request.filter.region
                ),
                max_events=request.max_events,
                subscriber=common_v1_contact_pb2.ContactInfo(name=request.subscriber.name)
            )
            async for chunk_0 in deps.clients.pipelines_pipeline_reporting.StreamPipelineMetrics(
                outgoing_0,
                timeout=deps.settings.timeout
            ):
                response_0 = chunk_0
            echoed_0 = request.subscriber.email
            response.pipeline_step.owner.email = echoed_0
            return response
