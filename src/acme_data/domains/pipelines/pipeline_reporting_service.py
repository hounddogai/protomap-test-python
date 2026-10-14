"""Builds and schedules reports about pipelines."""

from __future__ import annotations

from collections.abc import AsyncIterator
from dataclasses import dataclass
from functools import partial
from typing import cast
import asyncio
import logging

import grpc

from acme.audit.v1 import audit_event_validation_service_pb2 as audit_v1_audit_event_validation_service_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.featurestore.v1 import (
    feature_value_reporting_service_pb2 as featurestore_v1_feature_value_reporting_service_pb2,
)
from acme.identity.v1 import identity_pb2 as identity_v1_identity_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.identity.v1 import user_query_service_pb2 as identity_v1_user_query_service_pb2
from acme.identity.v1 import user_service_pb2 as identity_v1_user_service_pb2
from acme.labeling.v1 import annotation_approval_service_pb2 as labeling_v1_annotation_approval_service_pb2
from acme.labeling.v1 import labeling_pb2 as labeling_v1_labeling_pb2
from acme.labeling.v1 import refs_pb2 as labeling_v1_refs_pb2
from acme.ledger.v1 import ledger_account_query_service_pb2 as ledger_v1_ledger_account_query_service_pb2
from acme.metrics.v1 import dashboard_validation_service_pb2 as metrics_v1_dashboard_validation_service_pb2
from acme.metrics.v1 import metric_series_query_service_pb2 as metrics_v1_metric_series_query_service_pb2
from acme.metrics.v1 import metrics_pb2 as metrics_v1_metrics_pb2
from acme.pipelines.v1 import pipeline_reporting_service_pb2 as pipelines_v1_pipeline_reporting_service_pb2
from acme.pipelines.v1 import pipeline_reporting_service_pb2_grpc as pipelines_v1_pipeline_reporting_service_pb2_grpc
from acme.pipelines.v1 import pipeline_run_import_service_pb2 as pipelines_v1_pipeline_run_import_service_pb2
from acme.pipelines.v1 import pipeline_run_sync_service_pb2 as pipelines_v1_pipeline_run_sync_service_pb2
from acme.pipelines.v1 import pipeline_step_validation_service_pb2 as pipelines_v1_pipeline_step_validation_service_pb2
from acme.pipelines.v1 import pipelines_pb2 as pipelines_v1_pipelines_pb2
from acme.pipelines.v1 import refs_pb2 as pipelines_v1_refs_pb2

from acme_data.domains.pipelines import hooks
from acme_data.domains.pipelines.adapters import PipelineReportingSchedulePipelineReport1Adapter
from acme_data.domains.pipelines.adapters import PipelineReportingSchedulePipelineReport1Port
from acme_data.domains.pipelines.adapters import PipelineReportingSharePipelineReport0Adapter
from acme_data.domains.pipelines.dependencies import Dependencies
from acme_data.domains.pipelines.models import PipelineReportingDeletePipelineReport2Command
from acme_data.domains.pipelines.models import to_pipeline_reporting_delete_pipeline_report2_command
from acme_data.platform.rpc import messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import run_steps
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_id
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


@dataclass(slots=True)
class PipelineReportingServicer(pipelines_v1_pipeline_reporting_service_pb2_grpc.PipelineReportingServiceServicer):
    deps: Dependencies

    @rpc_errors
    @retry_transient
    async def CountPipelineTotals(
        self, request: pipelines_v1_pipeline_reporting_service_pb2.CountPipelineTotalsRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_reporting_service_pb2.CountPipelineTotalsResponse:
        """Counts pipelines by status."""
        return await self.handle_count_pipeline_totals(request)

    @rpc_errors
    async def DeletePipelineReport(
        self, request: pipelines_v1_pipeline_reporting_service_pb2.DeletePipelineReportRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_reporting_service_pb2.DeletePipelineReportResponse:
        """Deletes a pipeline."""
        return await self.handle_delete_pipeline_report(request)

    @rpc_errors
    @retry_transient
    async def FetchPipelineReport(
        self, request: pipelines_v1_pipeline_reporting_service_pb2.FetchPipelineReportRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_reporting_service_pb2.FetchPipelineReportResponse:
        """Returns a pipeline."""
        return await self.handle_fetch_pipeline_report(request)

    @rpc_errors
    async def GeneratePipelineReport(
        self, request: pipelines_v1_pipeline_reporting_service_pb2.GeneratePipelineReportRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_reporting_service_pb2.GeneratePipelineReportResponse:
        """Generates a pipeline."""
        return await self.handle_generate_pipeline_report(request)

    @rpc_errors
    @retry_transient
    async def ListPipelineReports(
        self, request: pipelines_v1_pipeline_reporting_service_pb2.ListPipelineReportsRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_reporting_service_pb2.ListPipelineReportsResponse:
        """Lists pipelines a page at a time."""
        return await self.handle_list_pipeline_reports(request)

    @rpc_errors
    async def SchedulePipelineReport(
        self, request: pipelines_v1_pipeline_reporting_service_pb2.SchedulePipelineReportRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_reporting_service_pb2.SchedulePipelineReportResponse:
        """Schedules a pipeline."""
        return await self.handle_schedule_pipeline_report(request)

    @rpc_errors
    async def SharePipelineReport(
        self, request: pipelines_v1_pipeline_reporting_service_pb2.SharePipelineReportRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_reporting_service_pb2.SharePipelineReportResponse:
        """Shares a pipeline."""
        return await self.handle_share_pipeline_report(request)

    @stream_errors
    async def StreamPipelineMetrics(
        self, request: pipelines_v1_pipeline_reporting_service_pb2.StreamPipelineMetricsRequest, context: grpc.aio.ServicerContext,
    ) -> AsyncIterator[pipelines_v1_pipeline_reporting_service_pb2.StreamPipelineMetricsResponse]:
        """Streams the changes of pipelines as they happen."""
        response = await self.handle_stream_pipeline_metrics(request)
        for item in messages((response,)):
            yield item

    async def handle_count_pipeline_totals(
        self,
        request: pipelines_v1_pipeline_reporting_service_pb2.CountPipelineTotalsRequest
    ) -> pipelines_v1_pipeline_reporting_service_pb2.CountPipelineTotalsResponse:
        """Counts pipelines by status."""
        deps = self.deps
        response = pipelines_v1_pipeline_reporting_service_pb2.CountPipelineTotalsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CountPipelineTotals', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'CountPipelineTotals',
                {'order_by': request.order_by}
            )
            response_0 = pipelines_v1_pipeline_step_validation_service_pb2.ValidatePipelineStepResponse()
            outgoing_0 = pipelines_v1_pipeline_step_validation_service_pb2.ValidatePipelineStepRequest(
                context=request.context,
                details=pipelines_v1_pipeline_step_validation_service_pb2.ValidatePipelineStepRequest.Details(
                    locale=request.context.locale
                ),
                pipeline_step=pipelines_v1_pipelines_pb2.PipelineStep(
                    audit=common_v1_audit_pb2.AuditInfo(created_at=request.filter.created_after),
                    owner=identity_v1_refs_pb2.UserRef(
                        email=request.context.actor.email,
                        user_id=request.context.actor.user_id
                    )
                )
            )
            response_0 = await deps.clients.pipelines_pipeline_step_validation.ValidatePipelineStep(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_0)
            return response

    async def handle_delete_pipeline_report(
        self,
        request: pipelines_v1_pipeline_reporting_service_pb2.DeletePipelineReportRequest
    ) -> pipelines_v1_pipeline_reporting_service_pb2.DeletePipelineReportResponse:
        """Deletes a pipeline."""
        deps = self.deps
        response = pipelines_v1_pipeline_reporting_service_pb2.DeletePipelineReportResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('DeletePipelineReport', extra={'fields': {'force': request.force}})
            await deps.repository.audit(request.context.tenant_id, 'DeletePipelineReport', {'force': request.force})
            response_0 = metrics_v1_metric_series_query_service_pb2.SuggestMetricSeriesesResponse()
            response_1 = metrics_v1_dashboard_validation_service_pb2.PreviewDashboardResponse()
            response_2 = ledger_v1_ledger_account_query_service_pb2.CountLedgerAccountsResponse()
            response_3 = labeling_v1_annotation_approval_service_pb2.EscalateAnnotationResponse()
            outgoing_0 = metrics_v1_metric_series_query_service_pb2.SuggestMetricSeriesesRequest(
                context=request.context,
                filter=metrics_v1_metric_series_query_service_pb2.SuggestMetricSeriesesRequest.Filter(
                    created_after=request.context.deadline,
                    labels=dict(request.context.baggage),
                    owner_id=request.pipeline_id
                )
            )
            outgoing_1 = metrics_v1_dashboard_validation_service_pb2.PreviewDashboardRequest(
                context=request.context,
                dashboard=metrics_v1_metrics_pb2.Dashboard(audit=common_v1_audit_pb2.AuditInfo(etag=request.etag)),
                details=metrics_v1_dashboard_validation_service_pb2.PreviewDashboardRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(email=request.context.actor.email),
                    locale=request.context.locale
                ),
                reason=request.reason
            )
            response_0, response_1 = await asyncio.gather(
                deps.clients.metrics_metric_series_query.SuggestMetricSerieses(
                    outgoing_0,
                    timeout=deps.settings.timeout
                ),
                deps.clients.metrics_dashboard_validation.PreviewDashboard(outgoing_1, timeout=deps.settings.timeout),
            )
            command_2 = PipelineReportingDeletePipelineReport2Command.model_validate(
                {
                    'context': request.context,
                    'filter_region': response_1.dashboard.billing_address.region,
                    'filter_created_after': response_1.dashboard.audit.created_at
                }
            )
            outgoing_2 = to_pipeline_reporting_delete_pipeline_report2_command(command_2)
            response_2 = await deps.clients.ledger_ledger_account_query.CountLedgerAccounts(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            outgoing_3 = labeling_v1_annotation_approval_service_pb2.EscalateAnnotationRequest(
                annotation=labeling_v1_labeling_pb2.Annotation(
                    subject=labeling_v1_refs_pb2.LabelingTaskRef(
                        display_name=response_1.dashboard.counterparty.display_name
                    )
                ),
                context=request.context
            )
            send_3 = partial(
                deps.clients.labeling_annotation_approval.EscalateAnnotation,
                timeout=deps.settings.timeout
            )
            response_3 = await send_3(outgoing_3)
            returned_0_0 = response_0.result.correlation_id
            if returned_0_0:
                response.result.correlation_id = returned_0_0
            returned_0_1 = response_0.result.message
            if returned_0_1:
                response.result.message = returned_0_1
            returned_1_0 = response_1.result.correlation_id
            if returned_1_0:
                response.result.correlation_id = returned_1_0
            returned_1_1 = response_1.outcome.effective_at
            if returned_1_1.ListFields():
                response.effective_at.MergeFrom(returned_1_1)
            returned_2_0 = response_2.result.reference_ids
            response.result.reference_ids.extend(returned_2_0)
            returned_2_1 = response_2.result.details
            response.result.details.update(returned_2_1)
            returned_3_0 = response_3.result.correlation_id
            if returned_3_0:
                response.result.correlation_id = returned_3_0
            returned_3_1 = response_3.result.details
            response.result.details.update(returned_3_1)
            return response

    async def handle_fetch_pipeline_report(
        self,
        request: pipelines_v1_pipeline_reporting_service_pb2.FetchPipelineReportRequest
    ) -> pipelines_v1_pipeline_reporting_service_pb2.FetchPipelineReportResponse:
        """Returns a pipeline."""
        deps = self.deps
        response = pipelines_v1_pipeline_reporting_service_pb2.FetchPipelineReportResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('FetchPipelineReport', extra={'fields': {'locale': request.context.locale}})
            await deps.repository.audit(
                request.context.tenant_id,
                'FetchPipelineReport',
                {'locale': request.context.locale}
            )
            echoed_0 = request.pipeline_id
            response.pipeline.pipeline_id = echoed_0
            return response

    async def handle_generate_pipeline_report(
        self,
        request: pipelines_v1_pipeline_reporting_service_pb2.GeneratePipelineReportRequest
    ) -> pipelines_v1_pipeline_reporting_service_pb2.GeneratePipelineReportResponse:
        """Generates a pipeline."""
        deps = self.deps
        response = pipelines_v1_pipeline_reporting_service_pb2.GeneratePipelineReportResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('GeneratePipelineReport', extra={'fields': {'pipeline_id': request.pipeline_id}})
            await deps.repository.audit(
                request.context.tenant_id,
                'GeneratePipelineReport',
                {'pipeline_id': request.pipeline_id}
            )
            response_0 = identity_v1_user_query_service_pb2.ResolveUsersResponse()
            outgoing_0 = identity_v1_user_query_service_pb2.ResolveUsersRequest(context=request.context)
            response_0 = await hooks.pipeline_reporting_generate_pipeline_report0(
                deps.clients.identity_user_query,
                outgoing_0,
                deps.settings.timeout
            )
            returned_0_0 = response_0.result.details
            response.result.details.update(returned_0_0)
            echoed_0 = request.details.period
            response.period.CopyFrom(echoed_0)
            return response

    async def handle_list_pipeline_reports(
        self,
        request: pipelines_v1_pipeline_reporting_service_pb2.ListPipelineReportsRequest
    ) -> pipelines_v1_pipeline_reporting_service_pb2.ListPipelineReportsResponse:
        """Lists pipelines a page at a time."""
        deps = self.deps
        response = pipelines_v1_pipeline_reporting_service_pb2.ListPipelineReportsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ListPipelineReports', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ListPipelineReports',
                {'order_by': request.order_by}
            )
            return response

    async def handle_schedule_pipeline_report(
        self,
        request: pipelines_v1_pipeline_reporting_service_pb2.SchedulePipelineReportRequest
    ) -> pipelines_v1_pipeline_reporting_service_pb2.SchedulePipelineReportResponse:
        """Schedules a pipeline."""
        deps = self.deps
        response = pipelines_v1_pipeline_reporting_service_pb2.SchedulePipelineReportResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SchedulePipelineReport', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'SchedulePipelineReport', {'reason': request.reason})
            response_0 = featurestore_v1_feature_value_reporting_service_pb2.CountFeatureValueTotalsResponse()
            response_1 = pipelines_v1_pipeline_run_import_service_pb2.RetryPipelineRunImportResponse()
            response_2 = audit_v1_audit_event_validation_service_pb2.ValidateAuditEventResponse()
            outgoing_0 = featurestore_v1_feature_value_reporting_service_pb2.CountFeatureValueTotalsRequest()
            outgoing_0.context.CopyFrom(request.context)
            outgoing_0.filter.owner_id = request.pipeline_id
            outgoing_0.filter.labels.update(dict(request.details.filters))
            outgoing_0.filter.created_after.CopyFrom(request.context.deadline)
            outgoing_0.context.tenant_id = tenant_id.get()
            response_0 = await deps.clients.featurestore_feature_value_reporting.CountFeatureValueTotals(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = pipelines_v1_pipeline_run_import_service_pb2.RetryPipelineRunImportRequest(
                context=request.context,
                pipeline_run=pipelines_v1_pipelines_pb2.PipelineRun(
                    customer=pipelines_v1_refs_pb2.PipelineRef(pipeline_id=request.pipeline_id)
                )
            )
            port_1: PipelineReportingSchedulePipelineReport1Port = PipelineReportingSchedulePipelineReport1Adapter(
                deps.clients.pipelines_pipeline_run_import,
                deps.settings.timeout
            )
            response_1 = await port_1.execute(outgoing_1)
            outgoing_2 = audit_v1_audit_event_validation_service_pb2.ValidateAuditEventRequest(
                context=request.context,
                details=audit_v1_audit_event_validation_service_pb2.ValidateAuditEventRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(email=response_1.pipeline_run.requester.email)
                )
            )
            steps_2 = [
                partial(
                    deps.clients.audit_audit_event_validation.ValidateAuditEvent,
                    outgoing_2,
                    timeout=deps.settings.timeout
                )
            ]
            results_2 = await run_steps(steps_2)
            response_2 = results_2[-1]
            returned_0_0 = response_0.result.details
            response.result.details.update(returned_0_0)
            returned_1_0 = response_1.result.reference_ids
            response.result.reference_ids.extend(returned_1_0)
            returned_1_1 = response_1.result.message
            if returned_1_1:
                response.result.message = returned_1_1
            returned_2_0 = response_2.result.reference_ids
            response.result.reference_ids.extend(returned_2_0)
            returned_2_1 = response_2.outcome.message
            if returned_2_1:
                response.result.message = returned_2_1
            echoed_0 = request.details.period
            response.period.CopyFrom(echoed_0)
            return response

    async def handle_share_pipeline_report(
        self,
        request: pipelines_v1_pipeline_reporting_service_pb2.SharePipelineReportRequest
    ) -> pipelines_v1_pipeline_reporting_service_pb2.SharePipelineReportResponse:
        """Shares a pipeline."""
        deps = self.deps
        response = pipelines_v1_pipeline_reporting_service_pb2.SharePipelineReportResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SharePipelineReport', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'SharePipelineReport', {'reason': request.reason})
            response_0 = ledger_v1_ledger_account_query_service_pb2.CountLedgerAccountsResponse()
            response_1 = pipelines_v1_pipeline_step_validation_service_pb2.ExplainPipelineStepDecisionResponse()
            response_2 = pipelines_v1_pipeline_run_sync_service_pb2.ResolvePipelineRunConflictResponse()
            outgoing_0 = ledger_v1_ledger_account_query_service_pb2.CountLedgerAccountsRequest(
                context=request.context,
                filter=ledger_v1_ledger_account_query_service_pb2.CountLedgerAccountsRequest.Filter(
                    created_after=request.context.deadline,
                    labels=dict(request.annotations),
                    owner_id=request.details.template_id
                )
            )
            response_0 = await PipelineReportingSharePipelineReport0Adapter(
                deps.clients.ledger_ledger_account_query,
                deps.settings.timeout
            )(outgoing_0)
            outgoing_1 = pipelines_v1_pipeline_step_validation_service_pb2.ExplainPipelineStepDecisionRequest(
                context=request.context,
                details=pipelines_v1_pipeline_step_validation_service_pb2.ExplainPipelineStepDecisionRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(
                        email=request.details.recipient.email,
                        name=request.details.recipient.name,
                        phone=request.details.recipient.phone,
                        preferred_channel=request.details.recipient.preferred_channel
                    )
                )
            )
            response_1 = cast(pipelines_v1_pipeline_step_validation_service_pb2.ExplainPipelineStepDecisionResponse, await deps.bus.request(
                'acme.pipelines.v1.PipelineReportingService/SharePipelineReport/1', outgoing_1, deps.settings.timeout,
            ))
            outgoing_2 = pipelines_v1_pipeline_run_sync_service_pb2.ResolvePipelineRunConflictRequest(
                context=request.context,
                pipeline_run=pipelines_v1_pipelines_pb2.PipelineRun(
                    assignee=identity_v1_refs_pb2.UserRef(email=request.details.recipient.email),
                    audit=common_v1_audit_pb2.AuditInfo(etag=response_1.pipeline_step.audit.etag),
                    comments=[
                        pipelines_v1_pipelines_pb2.PipelineRunComment(
                            created_at=response_1.pipeline_step.audit.created_at
                        )
                    ]
                )
            )
            response_2 = await deps.clients.pipelines_pipeline_run_sync.ResolvePipelineRunConflict(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_0)
            returned_1_0 = response_1.pipeline_step.owner.email
            returned_1_0_part_1 = response.pipeline.participants.add()
            if returned_1_0:
                returned_1_0_part_1.contact.email = returned_1_0
            returned_1_1 = response_1.pipeline_step.owner.email
            if returned_1_1:
                response.pipeline.organizer.email = returned_1_1
            returned_2_0 = response_2.result.message
            if returned_2_0:
                response.result.message = returned_2_0
            echoed_0 = request.pipeline_id
            response.pipeline.pipeline_id = echoed_0
            return response

    async def handle_stream_pipeline_metrics(
        self,
        request: pipelines_v1_pipeline_reporting_service_pb2.StreamPipelineMetricsRequest
    ) -> pipelines_v1_pipeline_reporting_service_pb2.StreamPipelineMetricsResponse:
        """Streams the changes of pipelines as they happen."""
        deps = self.deps
        response = pipelines_v1_pipeline_reporting_service_pb2.StreamPipelineMetricsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('StreamPipelineMetrics', extra={'fields': {'max_events': request.max_events}})
            await deps.repository.audit(
                request.context.tenant_id,
                'StreamPipelineMetrics',
                {'max_events': request.max_events}
            )
            response_0 = identity_v1_user_query_service_pb2.SuggestUsersResponse()
            response_1 = identity_v1_user_service_pb2.CloneUserResponse()
            outgoing_0 = identity_v1_user_query_service_pb2.SuggestUsersRequest(
                context=request.context,
                filter=identity_v1_user_query_service_pb2.SuggestUsersRequest.Filter(
                    owner_id=request.filter.owner_id,
                    region=request.filter.region
                )
            )
            outgoing_1 = identity_v1_user_service_pb2.CloneUserRequest(
                context=request.context,
                user=identity_v1_identity_pb2.User(
                    contact=common_v1_contact_pb2.ContactInfo(phone=request.subscriber.phone)
                )
            )
            response_0, response_1 = await asyncio.gather(
                deps.clients.identity_user_query.SuggestUsers(outgoing_0, timeout=deps.settings.timeout),
                deps.clients.identity_user.CloneUser(outgoing_1, timeout=deps.settings.timeout),
            )
            returned_0_0 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_0)
            returned_1_0 = response_1.user.contact
            returned_1_0_part_1 = response.pipeline.participants.add()
            if returned_1_0.ListFields():
                returned_1_0_part_1.contact.MergeFrom(returned_1_0)
            returned_1_1 = response_1.user.relationship_manager.display_name
            if returned_1_1:
                response.pipeline.organizer.display_name = returned_1_1
            echoed_0 = request.subscriber.email
            response.pipeline.organizer.email = echoed_0
            echoed_1 = request.filter.region
            response.pipeline.location.region = echoed_1
            return response
