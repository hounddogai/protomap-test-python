"""Reusable transport mixin for PipelineRunLifecycleService."""

from __future__ import annotations

from collections.abc import AsyncIterator
from functools import partial
from typing import Any
from typing import cast
import asyncio
import logging

from google.protobuf.any_pb2 import Any as AnyMessage
from google.protobuf.json_format import MessageToJson
from google.protobuf.json_format import Parse
import grpc

from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.community.v1 import forum_query_service_pb2 as community_v1_forum_query_service_pb2
from acme.documents.v1 import document_query_service_pb2 as documents_v1_document_query_service_pb2
from acme.documents.v1 import document_validation_service_pb2 as documents_v1_document_validation_service_pb2
from acme.employees.v1 import refs_pb2 as employees_v1_refs_pb2
from acme.featurestore.v1 import entity_approval_service_pb2 as featurestore_v1_entity_approval_service_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.itsm.v1 import incident_service_pb2 as itsm_v1_incident_service_pb2
from acme.itsm.v1 import itsm_pb2 as itsm_v1_itsm_pb2
from acme.metrics.v1 import dashboard_sync_service_pb2 as metrics_v1_dashboard_sync_service_pb2
from acme.patients.v1 import patient_calculation_service_pb2 as patients_v1_patient_calculation_service_pb2
from acme.pipelines.v1 import pipeline_run_import_service_pb2 as pipelines_v1_pipeline_run_import_service_pb2
from acme.pipelines.v1 import pipeline_run_lifecycle_service_pb2 as pipelines_v1_pipeline_run_lifecycle_service_pb2
from acme.pipelines.v1 import pipeline_run_sync_service_pb2 as pipelines_v1_pipeline_run_sync_service_pb2
from acme.pipelines.v1 import pipeline_run_sync_service_pb2_grpc as pipelines_v1_pipeline_run_sync_service_pb2_grpc
from acme.pipelines.v1 import pipeline_service_pb2 as pipelines_v1_pipeline_service_pb2
from acme.pipelines.v1 import pipeline_step_import_service_pb2 as pipelines_v1_pipeline_step_import_service_pb2
from acme.pipelines.v1 import pipelines_pb2 as pipelines_v1_pipelines_pb2
from acme.pipelines.v1 import refs_pb2 as pipelines_v1_refs_pb2
from acme.search.v1 import search_index_query_service_pb2 as search_v1_search_index_query_service_pb2
from acme.treasury.v1 import cash_position_query_service_pb2 as treasury_v1_cash_position_query_service_pb2
from acme.venues.v1 import venue_service_pb2 as venues_v1_venue_service_pb2

from acme_data.domains.pipelines import hooks
from acme_data.domains.pipelines.adapters import PipelineRunLifecycleSuspendPipelineRun2Adapter
from acme_data.domains.pipelines.adapters import PipelineRunLifecycleSuspendPipelineRun2Port
from acme_data.domains.pipelines.dependencies import Dependencies
from acme_data.domains.pipelines.models import PipelineRunLifecycleRenewPipelineRun1Command
from acme_data.domains.pipelines.models import PipelineRunLifecycleRenewPipelineRun2Command
from acme_data.domains.pipelines.models import to_pipeline_run_lifecycle_renew_pipeline_run1_command
from acme_data.domains.pipelines.models import to_pipeline_run_lifecycle_renew_pipeline_run2_command
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_id
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class PipelineRunLifecycleServicerHandlers:
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    async def ActivatePipelineRun(
        self, request: pipelines_v1_pipeline_run_lifecycle_service_pb2.ActivatePipelineRunRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_run_lifecycle_service_pb2.ActivatePipelineRunResponse:
        """Activates a pipeline run."""
        return await self.handle_activate_pipeline_run(request)

    @rpc_errors
    async def ExpirePipelineRun(
        self, request: pipelines_v1_pipeline_run_lifecycle_service_pb2.ExpirePipelineRunRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_run_lifecycle_service_pb2.ExpirePipelineRunResponse:
        """Expires a pipeline run."""
        return await self.handle_expire_pipeline_run(request)

    @rpc_errors
    @retry_transient
    async def GetPipelineRunLifecycle(
        self, request: pipelines_v1_pipeline_run_lifecycle_service_pb2.GetPipelineRunLifecycleRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_run_lifecycle_service_pb2.GetPipelineRunLifecycleResponse:
        """Returns a pipeline run."""
        return await self.handle_get_pipeline_run_lifecycle(request)

    @rpc_errors
    async def ReinstatePipelineRun(
        self, request: pipelines_v1_pipeline_run_lifecycle_service_pb2.ReinstatePipelineRunRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_run_lifecycle_service_pb2.ReinstatePipelineRunResponse:
        """Reinstates a pipeline run."""
        return await self.handle_reinstate_pipeline_run(request)

    @rpc_errors
    async def RenewPipelineRun(
        self, request: pipelines_v1_pipeline_run_lifecycle_service_pb2.RenewPipelineRunRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_run_lifecycle_service_pb2.RenewPipelineRunResponse:
        """Renews a pipeline run."""
        return await self.handle_renew_pipeline_run(request)

    @rpc_errors
    async def SchedulePipelineRunExpiry(
        self, request: pipelines_v1_pipeline_run_lifecycle_service_pb2.SchedulePipelineRunExpiryRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_run_lifecycle_service_pb2.SchedulePipelineRunExpiryResponse:
        """Schedules a pipeline run."""
        return await self.handle_schedule_pipeline_run_expiry(request)

    @rpc_errors
    async def SuspendPipelineRun(
        self, request: pipelines_v1_pipeline_run_lifecycle_service_pb2.SuspendPipelineRunRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_run_lifecycle_service_pb2.SuspendPipelineRunResponse:
        """Suspends a pipeline run."""
        return await self.handle_suspend_pipeline_run(request)

    @rpc_errors
    async def TerminatePipelineRun(
        self, request: pipelines_v1_pipeline_run_lifecycle_service_pb2.TerminatePipelineRunRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_run_lifecycle_service_pb2.TerminatePipelineRunResponse:
        """Terminates a pipeline run."""
        return await self.handle_terminate_pipeline_run(request)

    async def handle_activate_pipeline_run(
        self,
        request: pipelines_v1_pipeline_run_lifecycle_service_pb2.ActivatePipelineRunRequest
    ) -> pipelines_v1_pipeline_run_lifecycle_service_pb2.ActivatePipelineRunResponse:
        """Activates a pipeline run."""
        deps = self.deps
        response = pipelines_v1_pipeline_run_lifecycle_service_pb2.ActivatePipelineRunResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ActivatePipelineRun', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'ActivatePipelineRun', {'reason': request.reason})
            response_0 = pipelines_v1_pipeline_step_import_service_pb2.ValidatePipelineStepImportResponse()
            response_1 = community_v1_forum_query_service_pb2.ExportForumsResponse()
            outgoing_0 = pipelines_v1_pipeline_step_import_service_pb2.ValidatePipelineStepImportRequest(
                context=request.context,
                details=pipelines_v1_pipeline_step_import_service_pb2.ValidatePipelineStepImportRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(
                        email=request.details.new_owner.email,
                        phone=request.details.notify_contact.phone,
                        preferred_channel=request.details.notify_contact.preferred_channel
                    )
                ),
                pipeline_step=pipelines_v1_pipelines_pb2.PipelineStep(
                    owner=identity_v1_refs_pb2.UserRef(email=request.details.notify_contact.email)
                )
            )
            response_0 = cast(pipelines_v1_pipeline_step_import_service_pb2.ValidatePipelineStepImportResponse, await deps.bus.request(
                'acme.pipelines.v1.PipelineRunLifecycleService/ActivatePipelineRun/0', outgoing_0, deps.settings.timeout,
            ))
            outgoing_1 = community_v1_forum_query_service_pb2.ExportForumsRequest(
                context=request.context,
                filter=community_v1_forum_query_service_pb2.ExportForumsRequest.Filter(
                    created_after=response_0.pipeline_step.audit.created_at
                )
            )
            async for chunk_1 in deps.clients.community_forum_query.ExportForums(
                outgoing_1,
                timeout=deps.settings.timeout
            ):
                response_1 = chunk_1
            returned_0_0 = response_0.result.status
            if returned_0_0:
                response.outcome.status = returned_0_0
            returned_0_1 = response_0.result.details
            response.result.details.update(returned_0_1)
            echoed_0 = request.pipeline_run_id
            response.pipeline_run.pipeline_run_id = echoed_0
            echoed_1 = request.details.effective_at
            response.outcome.effective_at.CopyFrom(echoed_1)
            return response

    async def handle_expire_pipeline_run(
        self,
        request: pipelines_v1_pipeline_run_lifecycle_service_pb2.ExpirePipelineRunRequest
    ) -> pipelines_v1_pipeline_run_lifecycle_service_pb2.ExpirePipelineRunResponse:
        """Expires a pipeline run."""
        deps = self.deps
        response = pipelines_v1_pipeline_run_lifecycle_service_pb2.ExpirePipelineRunResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ExpirePipelineRun', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'ExpirePipelineRun', {'reason': request.reason})
            response_0 = pipelines_v1_pipeline_service_pb2.ClonePipelineResponse()
            response_1 = documents_v1_document_validation_service_pb2.NormalizeDocumentResponse()
            outgoing_0 = pipelines_v1_pipeline_service_pb2.ClonePipelineRequest(
                context=request.context,
                pipeline=pipelines_v1_pipelines_pb2.Pipeline(
                    participants=[
                        pipelines_v1_pipelines_pb2.PipelineParticipant(
                            contact=common_v1_contact_pb2.ContactInfo(
                                name=request.details.notify_contact.name,
                                phone=request.details.notify_contact.phone
                            )
                        )
                    ]
                )
            )
            method_name_0 = 'ClonePipeline'
            response_0 = await getattr(
                deps.clients.pipelines_pipeline,
                method_name_0
            )(outgoing_0, timeout=deps.settings.timeout)
            fields_1: dict[str, Any] = {
                'context': request.context,
                'document': {
                    'audit': {
                        'created_by': response_0.pipeline.audit.created_by,
                        'etag': response_0.pipeline.audit.etag
                    },
                    'billing_address': {'region': response_0.pipeline.location.region}
                }
            }
            outgoing_1 = documents_v1_document_validation_service_pb2.NormalizeDocumentRequest(**fields_1)
            response_1 = await deps.clients.documents_document_validation.NormalizeDocument(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_0)
            returned_1_0 = response_1.document.audit.etag
            if returned_1_0:
                response.pipeline_run.audit.etag = returned_1_0
            returned_1_1 = response_1.outcome.effective_at
            if returned_1_1.ListFields():
                response.outcome.effective_at.MergeFrom(returned_1_1)
            echoed_0 = request.pipeline_run_id
            response.pipeline_run.pipeline_run_id = echoed_0
            echoed_1 = request.details.notify_contact.phone
            response.pipeline_run.requester.phone = echoed_1
            return response

    async def handle_get_pipeline_run_lifecycle(
        self,
        request: pipelines_v1_pipeline_run_lifecycle_service_pb2.GetPipelineRunLifecycleRequest
    ) -> pipelines_v1_pipeline_run_lifecycle_service_pb2.GetPipelineRunLifecycleResponse:
        """Returns a pipeline run."""
        deps = self.deps
        response = pipelines_v1_pipeline_run_lifecycle_service_pb2.GetPipelineRunLifecycleResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('GetPipelineRunLifecycle', extra={'fields': {'domain': 'pipelines'}})
            await deps.repository.audit(request.context.tenant_id, 'GetPipelineRunLifecycle', {})
            response_0 = itsm_v1_incident_service_pb2.CreateIncidentResponse()
            response_1 = pipelines_v1_pipeline_step_import_service_pb2.RetryPipelineStepImportResponse()
            outgoing_0 = itsm_v1_incident_service_pb2.CreateIncidentRequest(
                context=request.context,
                incident=itsm_v1_itsm_pb2.Incident(
                    assignee=identity_v1_refs_pb2.UserRef(user_id=request.context.actor.user_id),
                    comments=[itsm_v1_itsm_pb2.IncidentComment(created_at=request.context.deadline)],
                    customer=employees_v1_refs_pb2.EmployeeRef(email=request.context.actor.email),
                    subject=request.pipeline_run_id
                )
            )
            response_0 = await deps.clients.itsm_incident.CreateIncident(outgoing_0, timeout=deps.settings.timeout)
            outgoing_1 = pipelines_v1_pipeline_step_import_service_pb2.RetryPipelineStepImportRequest(
                context=request.context,
                details=pipelines_v1_pipeline_step_import_service_pb2.RetryPipelineStepImportRequest.Details(
                    notify=common_v1_contact_pb2.ContactInfo(email=response_0.incident.assignee.email)
                ),
                pipeline_step=pipelines_v1_pipelines_pb2.PipelineStep(
                    audit=common_v1_audit_pb2.AuditInfo(etag=response_0.incident.audit.etag),
                    owner=identity_v1_refs_pb2.UserRef(user_id=response_0.incident.assignee.user_id)
                )
            )
            document_1 = MessageToJson(outgoing_1, preserving_proto_field_name=True)
            outgoing_1 = Parse(
                document_1,
                pipelines_v1_pipeline_step_import_service_pb2.RetryPipelineStepImportRequest()
            )
            response_1 = await deps.clients.pipelines_pipeline_step_import.RetryPipelineStepImport(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.incident.requester.email
            if returned_0_0:
                response.pipeline_run.requester.email = returned_0_0
            returned_1_0 = response_1.pipeline_step.owner.display_name
            if returned_1_0:
                response.pipeline_run.assignee.display_name = returned_1_0
            returned_1_1 = response_1.pipeline_step.audit.updated_at
            if returned_1_1.ListFields():
                response.pipeline_run.audit.updated_at.MergeFrom(returned_1_1)
            echoed_0 = request.pipeline_run_id
            response.pipeline_run.pipeline_run_id = echoed_0
            return response

    async def handle_reinstate_pipeline_run(
        self,
        request: pipelines_v1_pipeline_run_lifecycle_service_pb2.ReinstatePipelineRunRequest
    ) -> pipelines_v1_pipeline_run_lifecycle_service_pb2.ReinstatePipelineRunResponse:
        """Reinstates a pipeline run."""
        deps = self.deps
        response = pipelines_v1_pipeline_run_lifecycle_service_pb2.ReinstatePipelineRunResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ReinstatePipelineRun', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'ReinstatePipelineRun', {'reason': request.reason})
            response_0 = featurestore_v1_entity_approval_service_pb2.SubmitEntityResponse()
            response_1 = pipelines_v1_pipeline_run_sync_service_pb2.ReconcilePipelineRunsResponse()
            outgoing_0 = featurestore_v1_entity_approval_service_pb2.SubmitEntityRequest()
            outgoing_0.context.CopyFrom(request.context)
            outgoing_0.entity.contact.name.CopyFrom(request.details.notify_contact.name)
            outgoing_0.entity.contact.email = request.details.notify_contact.email
            merged_0 = featurestore_v1_entity_approval_service_pb2.SubmitEntityRequest()
            merged_0.MergeFrom(outgoing_0)
            outgoing_0.CopyFrom(merged_0)
            response_0 = await deps.clients.featurestore_entity_approval.SubmitEntity(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = pipelines_v1_pipeline_run_sync_service_pb2.ReconcilePipelineRunsRequest(
                context=request.context,
                pipeline_run=pipelines_v1_pipelines_pb2.PipelineRun(
                    requester=common_v1_contact_pb2.ContactInfo(email=request.details.new_owner.email)
                )
            )
            envelope_1 = AnyMessage()
            envelope_1.Pack(outgoing_1)
            outgoing_1 = pipelines_v1_pipeline_run_sync_service_pb2.ReconcilePipelineRunsRequest()
            if not envelope_1.Unpack(outgoing_1):
                raise ValueError("partner envelope contains the wrong request type")
            response_1 = await deps.clients.pipelines_pipeline_run_sync.ReconcilePipelineRuns(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.result.message = returned_0_0
            returned_0_1 = response_0.result.correlation_id
            if returned_0_1:
                response.result.correlation_id = returned_0_1
            returned_1_0 = response_1.pipeline_run.assignee.user_id
            if returned_1_0:
                response.pipeline_run.assignee.user_id = returned_1_0
            returned_1_1 = response_1.pipeline_run.requester.name
            if returned_1_1.ListFields():
                response.pipeline_run.requester.name.MergeFrom(returned_1_1)
            echoed_0 = request.pipeline_run_id
            response.pipeline_run.pipeline_run_id = echoed_0
            echoed_1 = request.details.effective_at
            response.outcome.effective_at.CopyFrom(echoed_1)
            return response

    async def handle_renew_pipeline_run(
        self,
        request: pipelines_v1_pipeline_run_lifecycle_service_pb2.RenewPipelineRunRequest
    ) -> pipelines_v1_pipeline_run_lifecycle_service_pb2.RenewPipelineRunResponse:
        """Renews a pipeline run."""
        deps = self.deps
        response = pipelines_v1_pipeline_run_lifecycle_service_pb2.RenewPipelineRunResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('RenewPipelineRun', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'RenewPipelineRun', {'reason': request.reason})
            response_0 = pipelines_v1_pipeline_run_sync_service_pb2.GetPipelineRunSyncStateResponse()
            response_1 = patients_v1_patient_calculation_service_pb2.CalculatePatientResponse()
            response_2 = pipelines_v1_pipeline_step_import_service_pb2.ListPipelineStepImportsResponse()
            outgoing_0 = pipelines_v1_pipeline_run_sync_service_pb2.GetPipelineRunSyncStateRequest(
                context=request.context,
                pipeline_run_id=request.pipeline_run_id
            )
            registered_0 = cast(
                pipelines_v1_pipeline_run_sync_service_pb2_grpc.PipelineRunSyncServiceStub,
                deps.clients.registry['acme.pipelines.v1.PipelineRunSyncService']
            )
            response_0 = await registered_0.GetPipelineRunSyncState(outgoing_0, timeout=deps.settings.timeout)
            command_1 = PipelineRunLifecycleRenewPipelineRun1Command(
                context=request.context,
                patient_relationship_manager_user_id=response_0.pipeline_run.assignee.user_id,
                patient_contact_preferred_channel=request.details.notify_contact.preferred_channel,
                patient_relationship_manager_display_name=response_0.pipeline_run.customer.display_name,
                patient_relationship_manager_email=response_0.pipeline_run.assignee.email
            )
            outgoing_1 = to_pipeline_run_lifecycle_renew_pipeline_run1_command(command_1)
            response_1 = await deps.clients.patients_patient_calculation.CalculatePatient(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            command_2 = PipelineRunLifecycleRenewPipelineRun2Command.model_validate(
                {
                    'context': request.context,
                    'filter_region': response_1.patient.primary_address.region,
                    'filter_created_after': response_0.pipeline_run.customer.starts_at,
                    'filter_owner_id': response_1.patient.relationship_manager.user_id
                }
            )
            outgoing_2 = to_pipeline_run_lifecycle_renew_pipeline_run2_command(command_2)
            response_2 = await deps.clients.pipelines_pipeline_step_import.ListPipelineStepImports(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.pipeline_run.priority
            if returned_0_0:
                response.pipeline_run.priority = returned_0_0
            returned_1_0 = response_1.patient.relationship_manager.user_id
            if returned_1_0:
                response.pipeline_run.assignee.user_id = returned_1_0
            returned_2_0 = response_2.result.status
            if returned_2_0:
                response.outcome.status = returned_2_0
            returned_2_1 = response_2.result.reference_ids
            response.result.reference_ids.extend(returned_2_1)
            echoed_0 = request.pipeline_run_id
            response.pipeline_run.pipeline_run_id = echoed_0
            echoed_1 = request.details.effective_at
            response.outcome.effective_at.CopyFrom(echoed_1)
            return response

    async def handle_schedule_pipeline_run_expiry(
        self,
        request: pipelines_v1_pipeline_run_lifecycle_service_pb2.SchedulePipelineRunExpiryRequest
    ) -> pipelines_v1_pipeline_run_lifecycle_service_pb2.SchedulePipelineRunExpiryResponse:
        """Schedules a pipeline run."""
        deps = self.deps
        response = pipelines_v1_pipeline_run_lifecycle_service_pb2.SchedulePipelineRunExpiryResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SchedulePipelineRunExpiry', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'SchedulePipelineRunExpiry',
                {'reason': request.reason}
            )
            await deps.repository.save_pipeline_run(request.context.tenant_id, request.pipeline_run)
            response_0 = pipelines_v1_pipeline_run_sync_service_pb2.ResolvePipelineRunConflictResponse()
            outgoing_0 = pipelines_v1_pipeline_run_sync_service_pb2.ResolvePipelineRunConflictRequest(
                context=request.context,
                pipeline_run=pipelines_v1_pipelines_pb2.PipelineRun(
                    audit=common_v1_audit_pb2.AuditInfo(etag=request.pipeline_run.audit.etag),
                    requester=common_v1_contact_pb2.ContactInfo(
                        email=request.pipeline_run.assignee.email,
                        name=request.pipeline_run.requester.name,
                        phone=request.details.notify.phone
                    )
                )
            )
            send_0 = partial(
                deps.clients.pipelines_pipeline_run_sync.ResolvePipelineRunConflict,
                timeout=deps.settings.timeout
            )
            response_0 = await send_0(outgoing_0)
            returned_0_0 = response_0.outcome.status
            if returned_0_0:
                response.outcome.status = returned_0_0
            returned_0_1 = response_0.pipeline_run.status
            if returned_0_1:
                response.pipeline_run.status = returned_0_1
            echoed_0 = request.pipeline_run_id
            response.pipeline_run.pipeline_run_id = echoed_0
            echoed_1 = request.pipeline_run.assignee
            response.pipeline_run.assignee.CopyFrom(echoed_1)
            return response

    async def handle_suspend_pipeline_run(
        self,
        request: pipelines_v1_pipeline_run_lifecycle_service_pb2.SuspendPipelineRunRequest
    ) -> pipelines_v1_pipeline_run_lifecycle_service_pb2.SuspendPipelineRunResponse:
        """Suspends a pipeline run."""
        deps = self.deps
        response = pipelines_v1_pipeline_run_lifecycle_service_pb2.SuspendPipelineRunResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SuspendPipelineRun', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'SuspendPipelineRun', {'reason': request.reason})
            response_0 = documents_v1_document_query_service_pb2.SuggestDocumentsResponse()
            response_1 = metrics_v1_dashboard_sync_service_pb2.PushDashboardResponse()
            response_2 = pipelines_v1_pipeline_run_import_service_pb2.ValidatePipelineRunImportResponse()
            outgoing_0 = documents_v1_document_query_service_pb2.SuggestDocumentsRequest(
                context=request.context,
                filter=documents_v1_document_query_service_pb2.SuggestDocumentsRequest.Filter(
                    created_after=request.details.effective_at,
                    labels=dict(request.annotations),
                    owner_id=request.details.new_owner.user_id
                )
            )
            response_0 = await hooks.pipeline_run_lifecycle_suspend_pipeline_run0(
                deps.clients.documents_document_query,
                outgoing_0,
                deps.settings.timeout
            )
            outgoing_1 = metrics_v1_dashboard_sync_service_pb2.PushDashboardRequest()
            outgoing_1.context.CopyFrom(request.context)
            outgoing_1.dashboard.counterparty.display_name = request.details.new_owner.display_name
            outgoing_1.context.tenant_id = tenant_id.get()
            response_1 = await deps.clients.metrics_dashboard_sync.PushDashboard(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = pipelines_v1_pipeline_run_import_service_pb2.ValidatePipelineRunImportRequest(
                context=request.context,
                pipeline_run=pipelines_v1_pipelines_pb2.PipelineRun(
                    assignee=identity_v1_refs_pb2.UserRef(email=request.details.notify_contact.email),
                    customer=pipelines_v1_refs_pb2.PipelineRef(display_name=request.details.new_owner.display_name)
                )
            )
            port_2: PipelineRunLifecycleSuspendPipelineRun2Port = PipelineRunLifecycleSuspendPipelineRun2Adapter(
                deps.clients.pipelines_pipeline_run_import,
                deps.settings.timeout
            )
            response_2 = await port_2.execute(outgoing_2)
            returned_0_0 = response_0.result.correlation_id
            if returned_0_0:
                response.result.correlation_id = returned_0_0
            returned_1_0 = response_1.outcome.status
            if returned_1_0:
                response.outcome.status = returned_1_0
            returned_2_0 = response_2.pipeline_run.sla.breached
            if returned_2_0:
                response.pipeline_run.sla.breached = returned_2_0
            returned_2_1 = response_2.pipeline_run.requester.phone
            if returned_2_1:
                response.pipeline_run.requester.phone = returned_2_1
            echoed_0 = request.pipeline_run_id
            response.pipeline_run.pipeline_run_id = echoed_0
            echoed_1 = request.details.effective_at
            response.outcome.effective_at.CopyFrom(echoed_1)
            return response

    async def handle_terminate_pipeline_run(
        self,
        request: pipelines_v1_pipeline_run_lifecycle_service_pb2.TerminatePipelineRunRequest
    ) -> pipelines_v1_pipeline_run_lifecycle_service_pb2.TerminatePipelineRunResponse:
        """Terminates a pipeline run."""
        deps = self.deps
        response = pipelines_v1_pipeline_run_lifecycle_service_pb2.TerminatePipelineRunResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('TerminatePipelineRun', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'TerminatePipelineRun', {'reason': request.reason})
            response_0 = treasury_v1_cash_position_query_service_pb2.SuggestCashPositionsResponse()
            response_1 = search_v1_search_index_query_service_pb2.CountSearchIndexesResponse()
            response_2 = venues_v1_venue_service_pb2.SearchVenuesResponse()
            outgoing_0 = treasury_v1_cash_position_query_service_pb2.SuggestCashPositionsRequest(
                context=request.context,
                filter=treasury_v1_cash_position_query_service_pb2.SuggestCashPositionsRequest.Filter(
                    created_after=request.details.effective_at,
                    labels=dict(request.annotations),
                    owner_id=request.details.new_owner.user_id
                )
            )
            outgoing_1 = search_v1_search_index_query_service_pb2.CountSearchIndexesRequest(
                context=request.context,
                filter=search_v1_search_index_query_service_pb2.CountSearchIndexesRequest.Filter(
                    created_after=request.details.effective_at,
                    owner_id=request.details.new_owner.user_id
                )
            )
            response_0, response_1 = await asyncio.gather(
                deps.clients.treasury_cash_position_query.SuggestCashPositions(
                    outgoing_0,
                    timeout=deps.settings.timeout
                ),
                deps.clients.search_search_index_query.CountSearchIndexes(outgoing_1, timeout=deps.settings.timeout),
            )
            outgoing_2 = venues_v1_venue_service_pb2.SearchVenuesRequest(
                context=request.context,
                filter=venues_v1_venue_service_pb2.SearchVenuesRequest.Filter(
                    created_after=request.details.effective_at
                )
            )
            response_2 = cast(venues_v1_venue_service_pb2.SearchVenuesResponse, await deps.bus.request(
                'acme.pipelines.v1.PipelineRunLifecycleService/TerminatePipelineRun/2', outgoing_2, deps.settings.timeout,
            ))
            returned_0_0 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_0)
            returned_0_1 = response_0.result.message
            if returned_0_1:
                response.result.message = returned_0_1
            returned_1_0 = response_1.result.message
            if returned_1_0:
                response.outcome.message = returned_1_0
            returned_1_1 = response_1.result.reference_ids
            response.result.reference_ids.extend(returned_1_1)
            returned_2_0 = response_2.result.status
            if returned_2_0:
                response.result.status = returned_2_0
            returned_2_1 = response_2.result.status
            if returned_2_1:
                response.outcome.status = returned_2_1
            echoed_0 = request.pipeline_run_id
            response.pipeline_run.pipeline_run_id = echoed_0
            echoed_1 = request.details.effective_at
            response.outcome.effective_at.CopyFrom(echoed_1)
            return response
