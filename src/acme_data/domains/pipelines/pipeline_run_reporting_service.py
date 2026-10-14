"""Builds and schedules reports about pipeline runs."""

from __future__ import annotations

from collections.abc import AsyncIterator
from functools import partial
from typing import cast
import logging

import grpc

from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.featurestore.v1 import entity_approval_service_pb2 as featurestore_v1_entity_approval_service_pb2
from acme.featurestore.v1 import entity_workflow_service_pb2 as featurestore_v1_entity_workflow_service_pb2
from acme.featurestore.v1 import featurestore_pb2 as featurestore_v1_featurestore_pb2
from acme.labeling.v1 import label_set_sync_service_pb2 as labeling_v1_label_set_sync_service_pb2
from acme.ledger.v1 import ledger_account_query_service_pb2 as ledger_v1_ledger_account_query_service_pb2
from acme.metrics.v1 import metric_alert_history_service_pb2 as metrics_v1_metric_alert_history_service_pb2
from acme.metrics.v1 import metric_series_export_service_pb2 as metrics_v1_metric_series_export_service_pb2
from acme.modelregistry.v1 import (
    model_version_lifecycle_service_pb2 as modelregistry_v1_model_version_lifecycle_service_pb2,
)
from acme.pipelines.v1 import pipeline_run_reporting_service_pb2 as pipelines_v1_pipeline_run_reporting_service_pb2
from acme.pipelines.v1 import (
    pipeline_run_reporting_service_pb2_grpc as pipelines_v1_pipeline_run_reporting_service_pb2_grpc,
)
from acme.pipelines.v1 import pipeline_run_sync_service_pb2 as pipelines_v1_pipeline_run_sync_service_pb2
from acme.pipelines.v1 import pipeline_sync_service_pb2 as pipelines_v1_pipeline_sync_service_pb2
from acme.pipelines.v1 import pipelines_pb2 as pipelines_v1_pipelines_pb2

from acme_data.domains.pipelines.adapters import PipelineRunReportingGeneratePipelineRunReport1Adapter
from acme_data.domains.pipelines.adapters import PipelineRunReportingGeneratePipelineRunReport1Port
from acme_data.domains.pipelines.adapters import PipelineRunReportingSharePipelineRunReport1Adapter
from acme_data.domains.pipelines.dependencies import Dependencies
from acme_data.domains.pipelines.models import PipelineRunReportingDeletePipelineRunReport0Command
from acme_data.domains.pipelines.models import to_pipeline_run_reporting_delete_pipeline_run_report0_command
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import run_steps
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_id
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class PipelineRunReportingServicer(
    pipelines_v1_pipeline_run_reporting_service_pb2_grpc.PipelineRunReportingServiceServicer
):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    @retry_transient
    async def CountPipelineRunTotals(
        self, request: pipelines_v1_pipeline_run_reporting_service_pb2.CountPipelineRunTotalsRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_run_reporting_service_pb2.CountPipelineRunTotalsResponse:
        """Counts pipeline runs by status."""
        return await self.handle_count_pipeline_run_totals(request)

    @rpc_errors
    async def DeletePipelineRunReport(
        self, request: pipelines_v1_pipeline_run_reporting_service_pb2.DeletePipelineRunReportRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_run_reporting_service_pb2.DeletePipelineRunReportResponse:
        """Deletes a pipeline run."""
        return await self.handle_delete_pipeline_run_report(request)

    @rpc_errors
    @retry_transient
    async def FetchPipelineRunReport(
        self, request: pipelines_v1_pipeline_run_reporting_service_pb2.FetchPipelineRunReportRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_run_reporting_service_pb2.FetchPipelineRunReportResponse:
        """Returns a pipeline run."""
        return await self.handle_fetch_pipeline_run_report(request)

    @rpc_errors
    async def GeneratePipelineRunReport(
        self, request: pipelines_v1_pipeline_run_reporting_service_pb2.GeneratePipelineRunReportRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_run_reporting_service_pb2.GeneratePipelineRunReportResponse:
        """Generates a pipeline run."""
        return await self.handle_generate_pipeline_run_report(request)

    @rpc_errors
    async def SharePipelineRunReport(
        self, request: pipelines_v1_pipeline_run_reporting_service_pb2.SharePipelineRunReportRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_run_reporting_service_pb2.SharePipelineRunReportResponse:
        """Shares a pipeline run."""
        return await self.handle_share_pipeline_run_report(request)

    @stream_errors
    async def StreamPipelineRunMetrics(
        self, request: pipelines_v1_pipeline_run_reporting_service_pb2.StreamPipelineRunMetricsRequest, context: grpc.aio.ServicerContext,
    ) -> AsyncIterator[pipelines_v1_pipeline_run_reporting_service_pb2.StreamPipelineRunMetricsResponse]:
        """Streams the changes of pipeline runs as they happen."""
        response = await self.handle_stream_pipeline_run_metrics(request)
        for item in messages((response,)):
            yield item

    async def handle_count_pipeline_run_totals(
        self,
        request: pipelines_v1_pipeline_run_reporting_service_pb2.CountPipelineRunTotalsRequest
    ) -> pipelines_v1_pipeline_run_reporting_service_pb2.CountPipelineRunTotalsResponse:
        """Counts pipeline runs by status."""
        deps = self.deps
        response = pipelines_v1_pipeline_run_reporting_service_pb2.CountPipelineRunTotalsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CountPipelineRunTotals', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'CountPipelineRunTotals',
                {'order_by': request.order_by}
            )
            response_0 = metrics_v1_metric_series_export_service_pb2.ShareMetricSeriesExportResponse()
            outgoing_0 = metrics_v1_metric_series_export_service_pb2.ShareMetricSeriesExportRequest(
                annotations=dict(request.context.baggage),
                context=request.context,
                details=metrics_v1_metric_series_export_service_pb2.ShareMetricSeriesExportRequest.Details(
                    recipient=common_v1_contact_pb2.ContactInfo(email=request.context.actor.email),
                    variables=dict(request.filter.labels)
                )
            )
            response_0 = await deps.clients.metrics_metric_series_export.ShareMetricSeriesExport(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.outcome.message
            if returned_0_0:
                response.result.message = returned_0_0
            returned_0_1 = response_0.result.correlation_id
            if returned_0_1:
                response.result.correlation_id = returned_0_1
            return response

    async def handle_delete_pipeline_run_report(
        self,
        request: pipelines_v1_pipeline_run_reporting_service_pb2.DeletePipelineRunReportRequest
    ) -> pipelines_v1_pipeline_run_reporting_service_pb2.DeletePipelineRunReportResponse:
        """Deletes a pipeline run."""
        deps = self.deps
        response = pipelines_v1_pipeline_run_reporting_service_pb2.DeletePipelineRunReportResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('DeletePipelineRunReport', extra={'fields': {'etag': request.etag}})
            await deps.repository.audit(request.context.tenant_id, 'DeletePipelineRunReport', {'etag': request.etag})
            response_0 = modelregistry_v1_model_version_lifecycle_service_pb2.ScheduleModelVersionExpiryResponse()
            response_1 = pipelines_v1_pipeline_run_sync_service_pb2.StreamPipelineRunChangesResponse()
            command_0 = PipelineRunReportingDeletePipelineRunReport0Command.model_validate(
                {'context': request.context, 'reason': request.reason}
            )
            outgoing_0 = to_pipeline_run_reporting_delete_pipeline_run_report0_command(command_0)
            response_0 = await deps.clients.modelregistry_model_version_lifecycle.ScheduleModelVersionExpiry(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = pipelines_v1_pipeline_run_sync_service_pb2.StreamPipelineRunChangesRequest(
                ack=pipelines_v1_pipeline_run_sync_service_pb2.StreamPipelineRunChangesRequest.ChangeAck(
                    status=response_0.outcome.status
                ),
                context=request.context
            )
            async for chunk_1 in deps.clients.pipelines_pipeline_run_sync.StreamPipelineRunChanges(
                async_messages((outgoing_1,)),
                timeout=deps.settings.timeout
            ):
                response_1 = chunk_1
            returned_0_0 = response_0.outcome.message
            if returned_0_0:
                response.result.message = returned_0_0
            returned_0_1 = response_0.result.correlation_id
            if returned_0_1:
                response.result.correlation_id = returned_0_1
            return response

    async def handle_fetch_pipeline_run_report(
        self,
        request: pipelines_v1_pipeline_run_reporting_service_pb2.FetchPipelineRunReportRequest
    ) -> pipelines_v1_pipeline_run_reporting_service_pb2.FetchPipelineRunReportResponse:
        """Returns a pipeline run."""
        deps = self.deps
        response = pipelines_v1_pipeline_run_reporting_service_pb2.FetchPipelineRunReportResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('FetchPipelineRunReport', extra={'fields': {'domain': 'pipelines'}})
            await deps.repository.audit(request.context.tenant_id, 'FetchPipelineRunReport', {})
            response_0 = ledger_v1_ledger_account_query_service_pb2.ResolveLedgerAccountsResponse()
            outgoing_0 = ledger_v1_ledger_account_query_service_pb2.ResolveLedgerAccountsRequest(
                context=request.context
            )
            response_0 = await deps.clients.ledger_ledger_account_query.ResolveLedgerAccounts(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.details
            response.result.details.update(returned_0_0)
            echoed_0 = request.pipeline_run_id
            response.pipeline_run.pipeline_run_id = echoed_0
            return response

    async def handle_generate_pipeline_run_report(
        self,
        request: pipelines_v1_pipeline_run_reporting_service_pb2.GeneratePipelineRunReportRequest
    ) -> pipelines_v1_pipeline_run_reporting_service_pb2.GeneratePipelineRunReportResponse:
        """Generates a pipeline run."""
        deps = self.deps
        response = pipelines_v1_pipeline_run_reporting_service_pb2.GeneratePipelineRunReportResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('GeneratePipelineRunReport', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'GeneratePipelineRunReport',
                {'reason': request.reason}
            )
            response_0 = metrics_v1_metric_alert_history_service_pb2.ListMetricAlertVersionsResponse()
            response_1 = pipelines_v1_pipeline_sync_service_pb2.ReconcilePipelinesResponse()
            outgoing_0 = metrics_v1_metric_alert_history_service_pb2.ListMetricAlertVersionsRequest()
            outgoing_0.context.CopyFrom(request.context)
            outgoing_0.filter.labels.update(dict(request.details.filters))
            outgoing_0.filter.owner_id = request.pipeline_run_id
            outgoing_0.context.tenant_id = tenant_id.get()
            response_0 = await deps.clients.metrics_metric_alert_history.ListMetricAlertVersions(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = pipelines_v1_pipeline_sync_service_pb2.ReconcilePipelinesRequest(
                annotations=dict(request.annotations),
                context=request.context,
                pipeline=pipelines_v1_pipelines_pb2.Pipeline(
                    participants=[
                        pipelines_v1_pipelines_pb2.PipelineParticipant(
                            contact=common_v1_contact_pb2.ContactInfo(email=request.context.actor.email)
                        )
                    ]
                )
            )
            port_1: PipelineRunReportingGeneratePipelineRunReport1Port = PipelineRunReportingGeneratePipelineRunReport1Adapter(
                deps.clients.pipelines_pipeline_sync,
                deps.settings.timeout
            )
            response_1 = await port_1.execute(outgoing_1)
            returned_0_0 = response_0.result.correlation_id
            if returned_0_0:
                response.result.correlation_id = returned_0_0
            returned_1_0 = response_1.result.message
            if returned_1_0:
                response.result.message = returned_1_0
            echoed_0 = request.details.period
            response.period.CopyFrom(echoed_0)
            return response

    async def handle_share_pipeline_run_report(
        self,
        request: pipelines_v1_pipeline_run_reporting_service_pb2.SharePipelineRunReportRequest
    ) -> pipelines_v1_pipeline_run_reporting_service_pb2.SharePipelineRunReportResponse:
        """Shares a pipeline run."""
        deps = self.deps
        response = pipelines_v1_pipeline_run_reporting_service_pb2.SharePipelineRunReportResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SharePipelineRunReport', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'SharePipelineRunReport', {'reason': request.reason})
            response_0 = featurestore_v1_entity_workflow_service_pb2.PauseEntityWorkflowResponse()
            response_1 = featurestore_v1_entity_approval_service_pb2.RecallEntityResponse()
            outgoing_0 = featurestore_v1_entity_workflow_service_pb2.PauseEntityWorkflowRequest(
                context=request.context,
                entity=featurestore_v1_featurestore_pb2.Entity(
                    contact=common_v1_contact_pb2.ContactInfo(
                        email=request.details.recipient.email,
                        phone=request.details.recipient.phone
                    )
                )
            )
            steps_0 = [
                partial(
                    deps.clients.featurestore_entity_workflow.PauseEntityWorkflow,
                    outgoing_0,
                    timeout=deps.settings.timeout
                )
            ]
            results_0 = await run_steps(steps_0)
            response_0 = results_0[-1]
            outgoing_1 = featurestore_v1_entity_approval_service_pb2.RecallEntityRequest(
                context=request.context,
                entity=featurestore_v1_featurestore_pb2.Entity(
                    audit=common_v1_audit_pb2.AuditInfo(created_at=response_0.entity.audit.created_at),
                    contact=common_v1_contact_pb2.ContactInfo(
                        email=request.details.recipient.email,
                        phone=request.details.recipient.phone
                    )
                )
            )
            response_1 = await PipelineRunReportingSharePipelineRunReport1Adapter(
                deps.clients.featurestore_entity_approval,
                deps.settings.timeout
            )(outgoing_1)
            returned_0_0 = response_0.entity.relationship_manager.email
            if returned_0_0:
                response.pipeline_run.requester.email = returned_0_0
            returned_1_0 = response_1.result.message
            if returned_1_0:
                response.result.message = returned_1_0
            returned_1_1 = response_1.outcome.effective_at
            if returned_1_1.ListFields():
                response.outcome.effective_at.MergeFrom(returned_1_1)
            echoed_0 = request.pipeline_run_id
            response.pipeline_run.pipeline_run_id = echoed_0
            echoed_1 = request.details.recipient.phone
            response.pipeline_run.requester.phone = echoed_1
            return response

    async def handle_stream_pipeline_run_metrics(
        self,
        request: pipelines_v1_pipeline_run_reporting_service_pb2.StreamPipelineRunMetricsRequest
    ) -> pipelines_v1_pipeline_run_reporting_service_pb2.StreamPipelineRunMetricsResponse:
        """Streams the changes of pipeline runs as they happen."""
        deps = self.deps
        response = pipelines_v1_pipeline_run_reporting_service_pb2.StreamPipelineRunMetricsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('StreamPipelineRunMetrics', extra={'fields': {'max_events': request.max_events}})
            await deps.repository.audit(
                request.context.tenant_id,
                'StreamPipelineRunMetrics',
                {'max_events': request.max_events}
            )
            response_0 = labeling_v1_label_set_sync_service_pb2.ListLabelSetConflictsResponse()
            outgoing_0 = labeling_v1_label_set_sync_service_pb2.ListLabelSetConflictsRequest(
                context=request.context,
                filter=labeling_v1_label_set_sync_service_pb2.ListLabelSetConflictsRequest.Filter(
                    created_after=request.filter.created_after,
                    labels=dict(request.filter.labels)
                )
            )
            response_0 = cast(labeling_v1_label_set_sync_service_pb2.ListLabelSetConflictsResponse, await deps.bus.request(
                'acme.pipelines.v1.PipelineRunReportingService/StreamPipelineRunMetrics/0', outgoing_0, deps.settings.timeout,
            ))
            returned_0_0 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_0)
            echoed_0 = request.subscriber.email
            response.pipeline_run.requester.email = echoed_0
            echoed_1 = request.subscriber.email
            response.pipeline_run.assignee.email = echoed_1
            return response
