"""Moves a pipeline step between the states of its lifecycle."""

from __future__ import annotations

from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Any
from typing import cast
import asyncio
import logging

from google.protobuf.any_pb2 import Any as AnyMessage
from google.protobuf.json_format import MessageToDict
from google.protobuf.json_format import ParseDict
import grpc

from acme.anomalies.v1 import anomalies_pb2 as anomalies_v1_anomalies_pb2
from acme.anomalies.v1 import anomaly_approval_service_pb2 as anomalies_v1_anomaly_approval_service_pb2
from acme.anomalies.v1 import anomaly_approval_service_pb2_grpc as anomalies_v1_anomaly_approval_service_pb2_grpc
from acme.audit.v1 import audit_event_service_pb2 as audit_v1_audit_event_service_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.compliance.v1 import compliance_case_query_service_pb2 as compliance_v1_compliance_case_query_service_pb2
from acme.documents.v1 import document_query_service_pb2 as documents_v1_document_query_service_pb2
from acme.helpdesk.v1 import helpdesk_pb2 as helpdesk_v1_helpdesk_pb2
from acme.helpdesk.v1 import refs_pb2 as helpdesk_v1_refs_pb2
from acme.helpdesk.v1 import ticket_service_pb2 as helpdesk_v1_ticket_service_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.labeling.v1 import labeling_task_workflow_service_pb2 as labeling_v1_labeling_task_workflow_service_pb2
from acme.lending.v1 import loan_application_query_service_pb2 as lending_v1_loan_application_query_service_pb2
from acme.metrics.v1 import dashboard_sync_service_pb2 as metrics_v1_dashboard_sync_service_pb2
from acme.pipelines.v1 import pipeline_query_service_pb2 as pipelines_v1_pipeline_query_service_pb2
from acme.pipelines.v1 import pipeline_run_lifecycle_service_pb2 as pipelines_v1_pipeline_run_lifecycle_service_pb2
from acme.pipelines.v1 import pipeline_run_reporting_service_pb2 as pipelines_v1_pipeline_run_reporting_service_pb2
from acme.pipelines.v1 import pipeline_step_export_service_pb2 as pipelines_v1_pipeline_step_export_service_pb2
from acme.pipelines.v1 import pipeline_step_lifecycle_service_pb2 as pipelines_v1_pipeline_step_lifecycle_service_pb2
from acme.pipelines.v1 import (
    pipeline_step_lifecycle_service_pb2_grpc as pipelines_v1_pipeline_step_lifecycle_service_pb2_grpc,
)
from acme.pipelines.v1 import pipeline_sync_service_pb2 as pipelines_v1_pipeline_sync_service_pb2
from acme.pipelines.v1 import pipelines_pb2 as pipelines_v1_pipelines_pb2
from acme.pipelines.v1 import refs_pb2 as pipelines_v1_refs_pb2
from acme.search.v1 import search_index_service_pb2 as search_v1_search_index_service_pb2
from acme.search.v1 import search_pb2 as search_v1_search_pb2
from acme.timekeeping.v1 import timesheet_service_pb2 as timekeeping_v1_timesheet_service_pb2
from acme.venues.v1 import venue_validation_service_pb2 as venues_v1_venue_validation_service_pb2
from acme.venues.v1 import venues_pb2 as venues_v1_venues_pb2

from acme_data.domains.pipelines import hooks
from acme_data.domains.pipelines.adapters import PipelineStepLifecycleSuspendPipelineStep2Adapter
from acme_data.domains.pipelines.dependencies import Dependencies
from acme_data.domains.pipelines.models import PipelineStepLifecycleSchedulePipelineStepExpiry0Command
from acme_data.domains.pipelines.models import to_pipeline_step_lifecycle_schedule_pipeline_step_expiry0_command
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


@dataclass(slots=True)
class PipelineStepLifecycleServicer(
    pipelines_v1_pipeline_step_lifecycle_service_pb2_grpc.PipelineStepLifecycleServiceServicer
):
    deps: Dependencies

    @rpc_errors
    async def ActivatePipelineStep(
        self, request: pipelines_v1_pipeline_step_lifecycle_service_pb2.ActivatePipelineStepRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_step_lifecycle_service_pb2.ActivatePipelineStepResponse:
        """Activates a pipeline step."""
        return await self.handle_activate_pipeline_step(request)

    @rpc_errors
    async def ExpirePipelineStep(
        self, request: pipelines_v1_pipeline_step_lifecycle_service_pb2.ExpirePipelineStepRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_step_lifecycle_service_pb2.ExpirePipelineStepResponse:
        """Expires a pipeline step."""
        return await self.handle_expire_pipeline_step(request)

    @rpc_errors
    @retry_transient
    async def GetPipelineStepLifecycle(
        self, request: pipelines_v1_pipeline_step_lifecycle_service_pb2.GetPipelineStepLifecycleRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_step_lifecycle_service_pb2.GetPipelineStepLifecycleResponse:
        """Returns a pipeline step."""
        return await self.handle_get_pipeline_step_lifecycle(request)

    @rpc_errors
    async def RenewPipelineStep(
        self, request: pipelines_v1_pipeline_step_lifecycle_service_pb2.RenewPipelineStepRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_step_lifecycle_service_pb2.RenewPipelineStepResponse:
        """Renews a pipeline step."""
        return await self.handle_renew_pipeline_step(request)

    @rpc_errors
    async def SchedulePipelineStepExpiry(
        self, request: pipelines_v1_pipeline_step_lifecycle_service_pb2.SchedulePipelineStepExpiryRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_step_lifecycle_service_pb2.SchedulePipelineStepExpiryResponse:
        """Schedules a pipeline step."""
        return await self.handle_schedule_pipeline_step_expiry(request)

    @rpc_errors
    async def SuspendPipelineStep(
        self, request: pipelines_v1_pipeline_step_lifecycle_service_pb2.SuspendPipelineStepRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_step_lifecycle_service_pb2.SuspendPipelineStepResponse:
        """Suspends a pipeline step."""
        return await self.handle_suspend_pipeline_step(request)

    @rpc_errors
    async def TerminatePipelineStep(
        self, request: pipelines_v1_pipeline_step_lifecycle_service_pb2.TerminatePipelineStepRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_step_lifecycle_service_pb2.TerminatePipelineStepResponse:
        """Terminates a pipeline step."""
        return await self.handle_terminate_pipeline_step(request)

    async def handle_activate_pipeline_step(
        self,
        request: pipelines_v1_pipeline_step_lifecycle_service_pb2.ActivatePipelineStepRequest
    ) -> pipelines_v1_pipeline_step_lifecycle_service_pb2.ActivatePipelineStepResponse:
        """Activates a pipeline step."""
        deps = self.deps
        response = pipelines_v1_pipeline_step_lifecycle_service_pb2.ActivatePipelineStepResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ActivatePipelineStep', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'ActivatePipelineStep', {'reason': request.reason})
            response_0 = venues_v1_venue_validation_service_pb2.CheckVenueEligibilityResponse()
            response_1 = venues_v1_venue_validation_service_pb2.ExplainVenueDecisionResponse()
            outgoing_0 = venues_v1_venue_validation_service_pb2.CheckVenueEligibilityRequest(
                context=request.context,
                details=venues_v1_venue_validation_service_pb2.CheckVenueEligibilityRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(
                        preferred_channel=request.details.notify_contact.preferred_channel
                    )
                ),
                venue=venues_v1_venues_pb2.Venue(
                    owner=identity_v1_refs_pb2.UserRef(user_id=request.details.new_owner.user_id)
                )
            )
            response_0 = await deps.clients.venues_venue_validation.CheckVenueEligibility(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = venues_v1_venue_validation_service_pb2.ExplainVenueDecisionRequest(
                context=request.context,
                venue=venues_v1_venues_pb2.Venue(
                    owner=identity_v1_refs_pb2.UserRef(user_id=request.details.new_owner.user_id)
                )
            )
            method_name_1 = 'ExplainVenueDecision'
            response_1 = await getattr(
                deps.clients.venues_venue_validation,
                method_name_1
            )(outgoing_1, timeout=deps.settings.timeout)
            returned_0_0 = response_0.result.correlation_id
            if returned_0_0:
                response.result.correlation_id = returned_0_0
            returned_1_0 = response_1.result.message
            if returned_1_0:
                response.result.message = returned_1_0
            echoed_0 = request.pipeline_step_id
            response.pipeline_step.pipeline_step_id = echoed_0
            echoed_1 = request.details.effective_at
            response.outcome.effective_at.CopyFrom(echoed_1)
            return response

    async def handle_expire_pipeline_step(
        self,
        request: pipelines_v1_pipeline_step_lifecycle_service_pb2.ExpirePipelineStepRequest
    ) -> pipelines_v1_pipeline_step_lifecycle_service_pb2.ExpirePipelineStepResponse:
        """Expires a pipeline step."""
        deps = self.deps
        response = pipelines_v1_pipeline_step_lifecycle_service_pb2.ExpirePipelineStepResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ExpirePipelineStep', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'ExpirePipelineStep', {'reason': request.reason})
            response_0 = timekeeping_v1_timesheet_service_pb2.CloneTimesheetResponse()
            response_1 = metrics_v1_dashboard_sync_service_pb2.ListDashboardConflictsResponse()
            fields_0: dict[str, Any] = {
                'context': request.context,
                'timesheet': {'counterparty': {'email': request.details.notify_contact.email}}
            }
            outgoing_0 = timekeeping_v1_timesheet_service_pb2.CloneTimesheetRequest(**fields_0)
            response_0 = await deps.clients.timekeeping_timesheet.CloneTimesheet(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = metrics_v1_dashboard_sync_service_pb2.ListDashboardConflictsRequest(
                context=request.context,
                filter=metrics_v1_dashboard_sync_service_pb2.ListDashboardConflictsRequest.Filter(
                    created_after=request.details.effective_at,
                    labels=dict(response_0.result.details),
                    owner_id=response_0.result.correlation_id,
                    region=response_0.timesheet.billing_address.region
                )
            )
            document_1 = MessageToDict(outgoing_1, preserving_proto_field_name=True)
            outgoing_1 = ParseDict(document_1, metrics_v1_dashboard_sync_service_pb2.ListDashboardConflictsRequest())
            response_1 = await deps.clients.metrics_dashboard_sync.ListDashboardConflicts(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.result.message = returned_0_0
            returned_0_1 = response_0.timesheet.audit.created_at
            if returned_0_1.ListFields():
                response.pipeline_step.audit.created_at.MergeFrom(returned_0_1)
            returned_1_0 = response_1.result.status
            if returned_1_0:
                response.outcome.status = returned_1_0
            echoed_0 = request.pipeline_step_id
            response.pipeline_step.pipeline_step_id = echoed_0
            echoed_1 = request.details.effective_at
            response.outcome.effective_at.CopyFrom(echoed_1)
            return response

    async def handle_get_pipeline_step_lifecycle(
        self,
        request: pipelines_v1_pipeline_step_lifecycle_service_pb2.GetPipelineStepLifecycleRequest
    ) -> pipelines_v1_pipeline_step_lifecycle_service_pb2.GetPipelineStepLifecycleResponse:
        """Returns a pipeline step."""
        deps = self.deps
        response = pipelines_v1_pipeline_step_lifecycle_service_pb2.GetPipelineStepLifecycleResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('GetPipelineStepLifecycle', extra={'fields': {'domain': 'pipelines'}})
            await deps.repository.audit(request.context.tenant_id, 'GetPipelineStepLifecycle', {})
            response_0 = pipelines_v1_pipeline_sync_service_pb2.ReconcilePipelinesResponse()
            outgoing_0 = pipelines_v1_pipeline_sync_service_pb2.ReconcilePipelinesRequest(
                context=request.context,
                pipeline=pipelines_v1_pipelines_pb2.Pipeline(
                    participants=[
                        pipelines_v1_pipelines_pb2.PipelineParticipant(
                            contact=common_v1_contact_pb2.ContactInfo(email=request.context.actor.email)
                        )
                    ]
                )
            )
            response_0 = await deps.clients.pipelines_pipeline_sync.ReconcilePipelines(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.correlation_id
            if returned_0_0:
                response.result.correlation_id = returned_0_0
            returned_0_1 = response_0.pipeline.audit.created_at
            if returned_0_1.ListFields():
                response.pipeline_step.audit.created_at.MergeFrom(returned_0_1)
            echoed_0 = request.pipeline_step_id
            response.pipeline_step.pipeline_step_id = echoed_0
            return response

    async def handle_renew_pipeline_step(
        self,
        request: pipelines_v1_pipeline_step_lifecycle_service_pb2.RenewPipelineStepRequest
    ) -> pipelines_v1_pipeline_step_lifecycle_service_pb2.RenewPipelineStepResponse:
        """Renews a pipeline step."""
        deps = self.deps
        response = pipelines_v1_pipeline_step_lifecycle_service_pb2.RenewPipelineStepResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('RenewPipelineStep', extra={'fields': {'reason_code': request.details.reason_code}})
            await deps.repository.audit(
                request.context.tenant_id,
                'RenewPipelineStep',
                {'reason_code': request.details.reason_code}
            )
            response_0 = search_v1_search_index_service_pb2.UpdateSearchIndexResponse()
            response_1 = pipelines_v1_pipeline_step_export_service_pb2.SchedulePipelineStepExportResponse()
            response_2 = anomalies_v1_anomaly_approval_service_pb2.DelegateAnomalyApprovalResponse()
            response_3 = documents_v1_document_query_service_pb2.SuggestDocumentsResponse()
            outgoing_0 = search_v1_search_index_service_pb2.UpdateSearchIndexRequest()
            outgoing_0.context.CopyFrom(request.context)
            outgoing_0.search_index.owner.email = request.details.notify_contact.email
            outgoing_0.search_index.owner.display_name = request.details.new_owner.display_name
            outgoing_0.search_index.owner.user_id = request.details.new_owner.user_id
            merged_0 = search_v1_search_index_service_pb2.UpdateSearchIndexRequest()
            merged_0.MergeFrom(outgoing_0)
            outgoing_0.CopyFrom(merged_0)
            response_0 = await deps.clients.search_search_index.UpdateSearchIndex(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = pipelines_v1_pipeline_step_export_service_pb2.SchedulePipelineStepExportRequest(
                annotations=dict(request.annotations),
                context=request.context,
                pipeline_step_id=request.pipeline_step_id,
                reason=request.reason
            )
            envelope_1 = AnyMessage()
            envelope_1.Pack(outgoing_1)
            outgoing_1 = pipelines_v1_pipeline_step_export_service_pb2.SchedulePipelineStepExportRequest()
            if not envelope_1.Unpack(outgoing_1):
                raise ValueError("partner envelope contains the wrong request type")
            response_1 = await deps.clients.pipelines_pipeline_step_export.SchedulePipelineStepExport(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = anomalies_v1_anomaly_approval_service_pb2.DelegateAnomalyApprovalRequest(
                anomaly=anomalies_v1_anomalies_pb2.Anomaly(
                    assignee=identity_v1_refs_pb2.UserRef(email=request.details.new_owner.email)
                ),
                context=request.context
            )
            registered_2 = cast(
                anomalies_v1_anomaly_approval_service_pb2_grpc.AnomalyApprovalServiceStub,
                deps.clients.registry['acme.anomalies.v1.AnomalyApprovalService']
            )
            response_2 = await registered_2.DelegateAnomalyApproval(outgoing_2, timeout=deps.settings.timeout)
            outgoing_3 = documents_v1_document_query_service_pb2.SuggestDocumentsRequest()
            outgoing_3.context.CopyFrom(request.context)
            if response_0.search_index.WhichOneof('locator') == 'address':
                outgoing_3.filter.region = response_0.search_index.address.region
            outgoing_3.filter.created_after.CopyFrom(response_2.anomaly.audit.updated_at)
            response_3 = await deps.clients.documents_document_query.SuggestDocuments(
                outgoing_3,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.search_index.audit.created_by
            if returned_0_0:
                response.pipeline_step.audit.created_by = returned_0_0
            returned_1_0 = response_1.result.message
            if returned_1_0:
                response.result.message = returned_1_0
            returned_2_0 = response_2.anomaly.audit.updated_by
            if returned_2_0:
                response.pipeline_step.audit.updated_by = returned_2_0
            returned_2_1 = response_2.result.correlation_id
            if returned_2_1:
                response.result.correlation_id = returned_2_1
            returned_3_0 = response_3.result.details
            response.result.details.update(returned_3_0)
            returned_3_1 = response_3.result.message
            if returned_3_1:
                response.result.message = returned_3_1
            echoed_0 = request.pipeline_step_id
            response.pipeline_step.pipeline_step_id = echoed_0
            echoed_1 = request.details.effective_at
            response.outcome.effective_at.CopyFrom(echoed_1)
            return response

    async def handle_schedule_pipeline_step_expiry(
        self,
        request: pipelines_v1_pipeline_step_lifecycle_service_pb2.SchedulePipelineStepExpiryRequest
    ) -> pipelines_v1_pipeline_step_lifecycle_service_pb2.SchedulePipelineStepExpiryResponse:
        """Schedules a pipeline step."""
        deps = self.deps
        response = pipelines_v1_pipeline_step_lifecycle_service_pb2.SchedulePipelineStepExpiryResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SchedulePipelineStepExpiry', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'SchedulePipelineStepExpiry',
                {'reason': request.reason}
            )
            await deps.repository.save_pipeline_step(request.context.tenant_id, request.pipeline_step)
            response_0 = compliance_v1_compliance_case_query_service_pb2.FindComplianceCasesResponse()
            response_1 = pipelines_v1_pipeline_run_reporting_service_pb2.StreamPipelineRunMetricsResponse()
            response_2 = pipelines_v1_pipeline_run_reporting_service_pb2.CountPipelineRunTotalsResponse()
            response_3 = lending_v1_loan_application_query_service_pb2.ExportLoanApplicationsResponse()
            command_0 = PipelineStepLifecycleSchedulePipelineStepExpiry0Command.model_validate(
                {'context': request.context, 'filter_created_after': request.pipeline_step.audit.updated_at}
            )
            outgoing_0 = to_pipeline_step_lifecycle_schedule_pipeline_step_expiry0_command(command_0)
            response_0 = await deps.clients.compliance_compliance_case_query.FindComplianceCases(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = pipelines_v1_pipeline_run_reporting_service_pb2.StreamPipelineRunMetricsRequest(
                context=request.context,
                subscriber=common_v1_contact_pb2.ContactInfo(
                    name=request.details.notify.name,
                    preferred_channel=request.details.notify.preferred_channel
                )
            )
            async for chunk_1 in deps.clients.pipelines_pipeline_run_reporting.StreamPipelineRunMetrics(
                outgoing_1,
                timeout=deps.settings.timeout
            ):
                response_1 = chunk_1
            outgoing_2 = pipelines_v1_pipeline_run_reporting_service_pb2.CountPipelineRunTotalsRequest(
                context=request.context,
                filter=pipelines_v1_pipeline_run_reporting_service_pb2.CountPipelineRunTotalsRequest.Filter(
                    created_after=request.pipeline_step.audit.created_at,
                    owner_id=request.pipeline_step.owner.user_id
                )
            )
            response_2 = await hooks.pipeline_step_lifecycle_schedule_pipeline_step_expiry2(
                deps.clients.pipelines_pipeline_run_reporting,
                outgoing_2,
                deps.settings.timeout
            )
            outgoing_3 = lending_v1_loan_application_query_service_pb2.ExportLoanApplicationsRequest(
                context=request.context,
                filter=lending_v1_loan_application_query_service_pb2.ExportLoanApplicationsRequest.Filter(
                    created_after=request.pipeline_step.audit.created_at,
                    labels=dict(response_0.result.details),
                    owner_id=response_2.result.correlation_id
                )
            )
            async for chunk_3 in deps.clients.lending_loan_application_query.ExportLoanApplications(
                outgoing_3,
                timeout=deps.settings.timeout
            ):
                response_3 = chunk_3
            returned_0_0 = response_0.result.correlation_id
            if returned_0_0:
                response.result.correlation_id = returned_0_0
            returned_2_0 = response_2.result.correlation_id
            if returned_2_0:
                response.result.correlation_id = returned_2_0
            returned_2_1 = response_2.result.message
            if returned_2_1:
                response.result.message = returned_2_1
            echoed_0 = request.pipeline_step_id
            response.pipeline_step.pipeline_step_id = echoed_0
            echoed_1 = request.pipeline_step.description
            response.pipeline_step.description = echoed_1
            return response

    async def handle_suspend_pipeline_step(
        self,
        request: pipelines_v1_pipeline_step_lifecycle_service_pb2.SuspendPipelineStepRequest
    ) -> pipelines_v1_pipeline_step_lifecycle_service_pb2.SuspendPipelineStepResponse:
        """Suspends a pipeline step."""
        deps = self.deps
        response = pipelines_v1_pipeline_step_lifecycle_service_pb2.SuspendPipelineStepResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SuspendPipelineStep', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'SuspendPipelineStep', {'reason': request.reason})
            response_0 = pipelines_v1_pipeline_run_lifecycle_service_pb2.SchedulePipelineRunExpiryResponse()
            response_1 = audit_v1_audit_event_service_pb2.BatchGetAuditEventsResponse()
            response_2 = search_v1_search_index_service_pb2.UpdateSearchIndexResponse()
            outgoing_0 = pipelines_v1_pipeline_run_lifecycle_service_pb2.SchedulePipelineRunExpiryRequest(
                context=request.context,
                details=pipelines_v1_pipeline_run_lifecycle_service_pb2.SchedulePipelineRunExpiryRequest.Details(
                    notify=common_v1_contact_pb2.ContactInfo(
                        email=request.details.notify_contact.email,
                        preferred_channel=request.details.notify_contact.preferred_channel
                    )
                ),
                pipeline_run=pipelines_v1_pipelines_pb2.PipelineRun(
                    customer=pipelines_v1_refs_pb2.PipelineRef(display_name=request.details.new_owner.display_name)
                )
            )
            outgoing_1 = audit_v1_audit_event_service_pb2.BatchGetAuditEventsRequest(context=request.context)
            response_0, response_1 = await asyncio.gather(
                deps.clients.pipelines_pipeline_run_lifecycle.SchedulePipelineRunExpiry(
                    outgoing_0,
                    timeout=deps.settings.timeout
                ),
                deps.clients.audit_audit_event.BatchGetAuditEvents(outgoing_1, timeout=deps.settings.timeout),
            )
            outgoing_2 = search_v1_search_index_service_pb2.UpdateSearchIndexRequest(
                context=request.context,
                search_index=search_v1_search_pb2.SearchIndex(
                    audit=common_v1_audit_pb2.AuditInfo(
                        created_by=response_0.pipeline_run.audit.created_by,
                        updated_by=response_0.pipeline_run.audit.updated_by
                    ),
                    owner=identity_v1_refs_pb2.UserRef(
                        email=request.details.notify_contact.email,
                        user_id=request.details.new_owner.user_id
                    )
                )
            )
            response_2 = await PipelineStepLifecycleSuspendPipelineStep2Adapter(
                deps.clients.search_search_index,
                deps.settings.timeout
            )(outgoing_2)
            returned_0_0 = response_0.outcome.message
            if returned_0_0:
                response.result.message = returned_0_0
            returned_1_0 = response_1.result.status
            if returned_1_0:
                response.outcome.status = returned_1_0
            returned_1_1 = response_1.result.correlation_id
            if returned_1_1:
                response.result.correlation_id = returned_1_1
            returned_2_0 = response_2.search_index.owner
            if returned_2_0.ListFields():
                response.pipeline_step.owner.MergeFrom(returned_2_0)
            returned_2_1 = response_2.search_index.components.get(
                'primary',
                search_v1_search_pb2.SearchIndexComponent()
            ).description
            if returned_2_1:
                response.pipeline_step.description = returned_2_1
            echoed_0 = request.pipeline_step_id
            response.pipeline_step.pipeline_step_id = echoed_0
            echoed_1 = request.details.effective_at
            response.outcome.effective_at.CopyFrom(echoed_1)
            return response

    async def handle_terminate_pipeline_step(
        self,
        request: pipelines_v1_pipeline_step_lifecycle_service_pb2.TerminatePipelineStepRequest
    ) -> pipelines_v1_pipeline_step_lifecycle_service_pb2.TerminatePipelineStepResponse:
        """Terminates a pipeline step."""
        deps = self.deps
        response = pipelines_v1_pipeline_step_lifecycle_service_pb2.TerminatePipelineStepResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('TerminatePipelineStep', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'TerminatePipelineStep', {'reason': request.reason})
            response_0 = helpdesk_v1_ticket_service_pb2.CreateTicketResponse()
            response_1 = pipelines_v1_pipeline_query_service_pb2.SuggestPipelinesResponse()
            response_2 = pipelines_v1_pipeline_step_export_service_pb2.RetryPipelineStepExportResponse()
            response_3 = labeling_v1_labeling_task_workflow_service_pb2.RetryLabelingTaskWorkflowResponse()
            outgoing_0 = helpdesk_v1_ticket_service_pb2.CreateTicketRequest(
                context=request.context,
                ticket=helpdesk_v1_helpdesk_pb2.Ticket(
                    customer=helpdesk_v1_refs_pb2.KnowledgeArticleRef(
                        display_name=request.details.new_owner.display_name
                    ),
                    requester=common_v1_contact_pb2.ContactInfo(
                        email=request.details.notify_contact.email,
                        phone=request.details.notify_contact.phone
                    )
                )
            )
            response_0 = cast(helpdesk_v1_ticket_service_pb2.CreateTicketResponse, await deps.bus.request(
                'acme.pipelines.v1.PipelineStepLifecycleService/TerminatePipelineStep/0', outgoing_0, deps.settings.timeout,
            ))
            outgoing_1 = pipelines_v1_pipeline_query_service_pb2.SuggestPipelinesRequest(
                context=request.context,
                filter=pipelines_v1_pipeline_query_service_pb2.SuggestPipelinesRequest.Filter(
                    created_after=response_0.ticket.audit.created_at,
                    labels=dict(response_0.ticket.custom_fields),
                    owner_id=response_0.ticket.ticket_id
                )
            )
            response_1 = await deps.clients.pipelines_pipeline_query.SuggestPipelines(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = pipelines_v1_pipeline_step_export_service_pb2.RetryPipelineStepExportRequest(
                context=request.context,
                details=pipelines_v1_pipeline_step_export_service_pb2.RetryPipelineStepExportRequest.Details(
                    notify=common_v1_contact_pb2.ContactInfo(name=request.details.notify_contact.name)
                )
            )
            method_name_2 = 'RetryPipelineStepExport'
            response_2 = await getattr(
                deps.clients.pipelines_pipeline_step_export,
                method_name_2
            )(outgoing_2, timeout=deps.settings.timeout)
            fields_3: dict[str, Any] = {
                'context': request.context,
                'labeling_task': {
                    'comments': [{'created_at': response_0.ticket.audit.created_at}],
                    'customer': {'display_name': response_0.ticket.assignee.display_name},
                    'requester': {'email': response_0.ticket.assignee.email}
                }
            }
            outgoing_3 = labeling_v1_labeling_task_workflow_service_pb2.RetryLabelingTaskWorkflowRequest(**fields_3)
            response_3 = await deps.clients.labeling_labeling_task_workflow.RetryLabelingTaskWorkflow(
                outgoing_3,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.ticket.audit.etag
            if returned_0_0:
                response.pipeline_step.audit.etag = returned_0_0
            returned_0_1 = response_0.result.message
            if returned_0_1:
                response.result.message = returned_0_1
            returned_1_0 = response_1.result.correlation_id
            if returned_1_0:
                response.result.correlation_id = returned_1_0
            returned_2_0 = response_2.pipeline_step.name
            if returned_2_0:
                response.pipeline_step.name = returned_2_0
            returned_3_0 = response_3.labeling_task.audit.etag
            if returned_3_0:
                response.pipeline_step.audit.etag = returned_3_0
            echoed_0 = request.pipeline_step_id
            response.pipeline_step.pipeline_step_id = echoed_0
            echoed_1 = request.details.effective_at
            response.outcome.effective_at.CopyFrom(echoed_1)
            return response
