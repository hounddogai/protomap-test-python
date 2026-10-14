"""Reusable transport mixin for PipelineStepImportService."""

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
from acme.featurestore.v1 import entity_reporting_service_pb2 as featurestore_v1_entity_reporting_service_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.ledger.v1 import ledger_account_service_pb2 as ledger_v1_ledger_account_service_pb2
from acme.metrics.v1 import metric_series_notification_service_pb2 as metrics_v1_metric_series_notification_service_pb2
from acme.modelregistry.v1 import deployment_sync_service_pb2 as modelregistry_v1_deployment_sync_service_pb2
from acme.modelregistry.v1 import (
    registered_model_workflow_service_pb2 as modelregistry_v1_registered_model_workflow_service_pb2,
)
from acme.notifications.v1 import notification_service_pb2 as notifications_v1_notification_service_pb2
from acme.pipelines.v1 import pipeline_run_calculation_service_pb2 as pipelines_v1_pipeline_run_calculation_service_pb2
from acme.pipelines.v1 import pipeline_run_import_service_pb2 as pipelines_v1_pipeline_run_import_service_pb2
from acme.pipelines.v1 import pipeline_run_query_service_pb2 as pipelines_v1_pipeline_run_query_service_pb2
from acme.pipelines.v1 import pipeline_run_validation_service_pb2 as pipelines_v1_pipeline_run_validation_service_pb2
from acme.pipelines.v1 import pipeline_service_pb2 as pipelines_v1_pipeline_service_pb2
from acme.pipelines.v1 import pipeline_step_export_service_pb2 as pipelines_v1_pipeline_step_export_service_pb2
from acme.pipelines.v1 import pipeline_step_import_service_pb2 as pipelines_v1_pipeline_step_import_service_pb2
from acme.pipelines.v1 import pipeline_step_validation_service_pb2 as pipelines_v1_pipeline_step_validation_service_pb2
from acme.pipelines.v1 import pipelines_pb2 as pipelines_v1_pipelines_pb2

from acme_data.domains.pipelines import hooks
from acme_data.domains.pipelines.adapters import PipelineStepImportRetryPipelineStepImport2Adapter
from acme_data.domains.pipelines.adapters import PipelineStepImportRetryPipelineStepImport2Port
from acme_data.domains.pipelines.dependencies import Dependencies
from acme_data.domains.pipelines.models import PipelineStepImportMapPipelineStepImportColumns0Command
from acme_data.domains.pipelines.models import PipelineStepImportMapPipelineStepImportColumns1Command
from acme_data.domains.pipelines.models import to_pipeline_step_import_map_pipeline_step_import_columns0_command
from acme_data.domains.pipelines.models import to_pipeline_step_import_map_pipeline_step_import_columns1_command
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_id
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class PipelineStepImportServicerHandlers:
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    async def CancelPipelineStepImport(
        self, request: pipelines_v1_pipeline_step_import_service_pb2.CancelPipelineStepImportRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_step_import_service_pb2.CancelPipelineStepImportResponse:
        """Cancels a pipeline step."""
        return await self.handle_cancel_pipeline_step_import(request)

    @rpc_errors
    @retry_transient
    async def GetPipelineStepImportStatus(
        self, request: pipelines_v1_pipeline_step_import_service_pb2.GetPipelineStepImportStatusRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_step_import_service_pb2.GetPipelineStepImportStatusResponse:
        """Returns a pipeline step."""
        return await self.handle_get_pipeline_step_import_status(request)

    @rpc_errors
    async def ImportPipelineSteps(
        self, requests: AsyncIterator[
            pipelines_v1_pipeline_step_import_service_pb2.ImportPipelineStepsRequest
        ], context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_step_import_service_pb2.ImportPipelineStepsResponse:
        """Takes a stream of pipeline steps and answers once at the end."""
        response = pipelines_v1_pipeline_step_import_service_pb2.ImportPipelineStepsResponse()
        async for request in requests:
            response.MergeFrom(await self.handle_import_pipeline_steps(request))
        return response

    @rpc_errors
    @retry_transient
    async def ListPipelineStepImports(
        self, request: pipelines_v1_pipeline_step_import_service_pb2.ListPipelineStepImportsRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_step_import_service_pb2.ListPipelineStepImportsResponse:
        """Lists pipeline steps a page at a time."""
        return await self.handle_list_pipeline_step_imports(request)

    @rpc_errors
    async def MapPipelineStepImportColumns(
        self, request: pipelines_v1_pipeline_step_import_service_pb2.MapPipelineStepImportColumnsRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_step_import_service_pb2.MapPipelineStepImportColumnsResponse:
        """Maps a pipeline step."""
        return await self.handle_map_pipeline_step_import_columns(request)

    @rpc_errors
    async def RetryPipelineStepImport(
        self, request: pipelines_v1_pipeline_step_import_service_pb2.RetryPipelineStepImportRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_step_import_service_pb2.RetryPipelineStepImportResponse:
        """Retrys a pipeline step."""
        return await self.handle_retry_pipeline_step_import(request)

    @rpc_errors
    async def ValidatePipelineStepImport(
        self, request: pipelines_v1_pipeline_step_import_service_pb2.ValidatePipelineStepImportRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_step_import_service_pb2.ValidatePipelineStepImportResponse:
        """Validates a pipeline step."""
        return await self.handle_validate_pipeline_step_import(request)

    async def handle_cancel_pipeline_step_import(
        self,
        request: pipelines_v1_pipeline_step_import_service_pb2.CancelPipelineStepImportRequest
    ) -> pipelines_v1_pipeline_step_import_service_pb2.CancelPipelineStepImportResponse:
        """Cancels a pipeline step."""
        deps = self.deps
        response = pipelines_v1_pipeline_step_import_service_pb2.CancelPipelineStepImportResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CancelPipelineStepImport', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'CancelPipelineStepImport',
                {'reason': request.reason}
            )
            response_0 = featurestore_v1_entity_reporting_service_pb2.ShareEntityReportResponse()
            response_1 = modelregistry_v1_registered_model_workflow_service_pb2.ListRegisteredModelWorkflowsResponse()
            outgoing_0 = featurestore_v1_entity_reporting_service_pb2.ShareEntityReportRequest(
                context=request.context,
                details=featurestore_v1_entity_reporting_service_pb2.ShareEntityReportRequest.Details(
                    recipient=common_v1_contact_pb2.ContactInfo(
                        email=request.details.new_owner.email,
                        name=request.details.notify_contact.name,
                        phone=request.details.notify_contact.phone,
                        preferred_channel=request.details.notify_contact.preferred_channel
                    )
                )
            )
            response_0 = await deps.clients.featurestore_entity_reporting.ShareEntityReport(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = modelregistry_v1_registered_model_workflow_service_pb2.ListRegisteredModelWorkflowsRequest(
                context=request.context,
                filter=modelregistry_v1_registered_model_workflow_service_pb2.ListRegisteredModelWorkflowsRequest.Filter(
                    created_after=response_0.entity.audit.created_at,
                    region=response_0.entity.primary_address.region
                )
            )
            method_name_1 = 'ListRegisteredModelWorkflows'
            response_1 = await getattr(
                deps.clients.modelregistry_registered_model_workflow,
                method_name_1
            )(outgoing_1, timeout=deps.settings.timeout)
            returned_0_0 = response_0.result.status
            if returned_0_0:
                response.result.status = returned_0_0
            returned_0_1 = response_0.result.correlation_id
            if returned_0_1:
                response.result.correlation_id = returned_0_1
            returned_1_0 = response_1.result.details
            response.result.details.update(returned_1_0)
            returned_1_1 = response_1.result.reference_ids
            response.result.reference_ids.extend(returned_1_1)
            echoed_0 = request.pipeline_step_id
            response.pipeline_step.pipeline_step_id = echoed_0
            echoed_1 = request.details.effective_at
            response.outcome.effective_at.CopyFrom(echoed_1)
            return response

    async def handle_get_pipeline_step_import_status(
        self,
        request: pipelines_v1_pipeline_step_import_service_pb2.GetPipelineStepImportStatusRequest
    ) -> pipelines_v1_pipeline_step_import_service_pb2.GetPipelineStepImportStatusResponse:
        """Returns a pipeline step."""
        deps = self.deps
        response = pipelines_v1_pipeline_step_import_service_pb2.GetPipelineStepImportStatusResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('GetPipelineStepImportStatus', extra={'fields': {'domain': 'pipelines'}})
            await deps.repository.audit(request.context.tenant_id, 'GetPipelineStepImportStatus', {})
            response_0 = pipelines_v1_pipeline_run_validation_service_pb2.CheckPipelineRunEligibilityResponse()
            response_1 = pipelines_v1_pipeline_service_pb2.ClonePipelineResponse()
            outgoing_0 = pipelines_v1_pipeline_run_validation_service_pb2.CheckPipelineRunEligibilityRequest(
                context=request.context,
                details=pipelines_v1_pipeline_run_validation_service_pb2.CheckPipelineRunEligibilityRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(email=request.context.actor.email),
                    locale=request.context.locale
                ),
                pipeline_run=pipelines_v1_pipelines_pb2.PipelineRun(
                    assignee=identity_v1_refs_pb2.UserRef(user_id=request.context.actor.user_id)
                )
            )
            response_0 = await deps.clients.pipelines_pipeline_run_validation.CheckPipelineRunEligibility(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = pipelines_v1_pipeline_service_pb2.ClonePipelineRequest(
                context=request.context,
                pipeline=pipelines_v1_pipelines_pb2.Pipeline(
                    audit=common_v1_audit_pb2.AuditInfo(created_at=response_0.pipeline_run.audit.created_at),
                    organizer=identity_v1_refs_pb2.UserRef(email=response_0.pipeline_run.assignee.email),
                    participants=[
                        pipelines_v1_pipelines_pb2.PipelineParticipant(
                            contact=common_v1_contact_pb2.ContactInfo(email=response_0.pipeline_run.requester.email)
                        )
                    ]
                )
            )
            document_1 = MessageToDict(outgoing_1, preserving_proto_field_name=True)
            outgoing_1 = ParseDict(document_1, pipelines_v1_pipeline_service_pb2.ClonePipelineRequest())
            response_1 = await deps.clients.pipelines_pipeline.ClonePipeline(outgoing_1, timeout=deps.settings.timeout)
            returned_0_0 = response_0.result.details
            response.result.details.update(returned_0_0)
            returned_1_0 = response_1.pipeline.organizer.display_name
            if returned_1_0:
                response.pipeline_step.owner.display_name = returned_1_0
            returned_1_1 = response_1.pipeline.audit.updated_by
            if returned_1_1:
                response.pipeline_step.audit.updated_by = returned_1_1
            echoed_0 = request.pipeline_step_id
            response.pipeline_step.pipeline_step_id = echoed_0
            return response

    async def handle_import_pipeline_steps(
        self,
        request: pipelines_v1_pipeline_step_import_service_pb2.ImportPipelineStepsRequest
    ) -> pipelines_v1_pipeline_step_import_service_pb2.ImportPipelineStepsResponse:
        """Takes a stream of pipeline steps and answers once at the end."""
        deps = self.deps
        response = pipelines_v1_pipeline_step_import_service_pb2.ImportPipelineStepsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ImportPipelineSteps', extra={'fields': {'sequence': request.sequence}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ImportPipelineSteps',
                {'sequence': request.sequence}
            )
            if request.WhichOneof('chunk') == 'record':
                await deps.repository.save_pipeline_step(request.context.tenant_id, request.record)
            response_0 = notifications_v1_notification_service_pb2.SearchNotificationsResponse()
            response_1 = modelregistry_v1_deployment_sync_service_pb2.ResolveDeploymentConflictResponse()
            response_2 = metrics_v1_metric_series_notification_service_pb2.UnsubscribeMetricSeriesUpdatesResponse()
            response_3 = pipelines_v1_pipeline_run_query_service_pb2.SummarizePipelineRunsResponse()
            outgoing_0 = notifications_v1_notification_service_pb2.SearchNotificationsRequest()
            outgoing_0.context.CopyFrom(request.context)
            if request.WhichOneof('chunk') == 'record':
                outgoing_0.filter.created_after.CopyFrom(request.record.audit.updated_at)
            response_0 = await deps.clients.notifications_notification.SearchNotifications(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = modelregistry_v1_deployment_sync_service_pb2.ResolveDeploymentConflictRequest()
            outgoing_1.context.CopyFrom(request.context)
            outgoing_1.deployment.audit.updated_by = request.record.audit.updated_by
            field_1_2_part_1 = outgoing_1.deployment.participants.add()
            field_1_2_part_1.contact.email = request.header.submitted_by.email
            merged_1 = modelregistry_v1_deployment_sync_service_pb2.ResolveDeploymentConflictRequest()
            merged_1.MergeFrom(outgoing_1)
            outgoing_1.CopyFrom(merged_1)
            response_1 = await deps.clients.modelregistry_deployment_sync.ResolveDeploymentConflict(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = metrics_v1_metric_series_notification_service_pb2.UnsubscribeMetricSeriesUpdatesRequest(
                context=request.context,
                details=metrics_v1_metric_series_notification_service_pb2.UnsubscribeMetricSeriesUpdatesRequest.Details(
                    recipient=common_v1_contact_pb2.ContactInfo(
                        email=request.record.owner.email,
                        name=request.header.submitted_by.name
                    )
                ),
                reason=request.record.block.reason
            )
            envelope_2 = AnyMessage()
            envelope_2.Pack(outgoing_2)
            outgoing_2 = metrics_v1_metric_series_notification_service_pb2.UnsubscribeMetricSeriesUpdatesRequest()
            if not envelope_2.Unpack(outgoing_2):
                raise ValueError("partner envelope contains the wrong request type")
            response_2 = await deps.clients.metrics_metric_series_notification.UnsubscribeMetricSeriesUpdates(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            outgoing_3 = pipelines_v1_pipeline_run_query_service_pb2.SummarizePipelineRunsRequest()
            outgoing_3.context.CopyFrom(request.context)
            if request.WhichOneof('chunk') == 'record' and request.record.WhichOneof('action') == 'block':
                outgoing_3.reason = request.record.block.reason
            if request.WhichOneof('chunk') == 'header':
                outgoing_3.details.format = request.header.format
            if request.WhichOneof('chunk') == 'record':
                outgoing_3.details.period.CopyFrom(request.record.effective)
            response_3 = await deps.clients.pipelines_pipeline_run_query.SummarizePipelineRuns(
                outgoing_3,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.status
            if returned_0_0:
                response.result.status = returned_0_0
            returned_1_0 = response_1.result.status
            if returned_1_0:
                response.result.status = returned_1_0
            returned_2_0 = response_2.result.details
            response.result.details.update(returned_2_0)
            returned_2_1 = response_2.result.correlation_id
            if returned_2_1:
                response.result.correlation_id = returned_2_1
            returned_3_0 = response_3.result.reference_ids
            response.result.reference_ids.extend(returned_3_0)
            return response

    async def handle_list_pipeline_step_imports(
        self,
        request: pipelines_v1_pipeline_step_import_service_pb2.ListPipelineStepImportsRequest
    ) -> pipelines_v1_pipeline_step_import_service_pb2.ListPipelineStepImportsResponse:
        """Lists pipeline steps a page at a time."""
        deps = self.deps
        response = pipelines_v1_pipeline_step_import_service_pb2.ListPipelineStepImportsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ListPipelineStepImports', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ListPipelineStepImports',
                {'order_by': request.order_by}
            )
            return response

    async def handle_map_pipeline_step_import_columns(
        self,
        request: pipelines_v1_pipeline_step_import_service_pb2.MapPipelineStepImportColumnsRequest
    ) -> pipelines_v1_pipeline_step_import_service_pb2.MapPipelineStepImportColumnsResponse:
        """Maps a pipeline step."""
        deps = self.deps
        response = pipelines_v1_pipeline_step_import_service_pb2.MapPipelineStepImportColumnsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('MapPipelineStepImportColumns', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'MapPipelineStepImportColumns',
                {'reason': request.reason}
            )
            await deps.repository.save_pipeline_step(request.context.tenant_id, request.pipeline_step)
            response_0 = pipelines_v1_pipeline_step_export_service_pb2.SchedulePipelineStepExportResponse()
            response_1 = pipelines_v1_pipeline_run_validation_service_pb2.CheckPipelineRunEligibilityResponse()
            response_2 = pipelines_v1_pipeline_run_validation_service_pb2.ExplainPipelineRunDecisionResponse()
            command_0 = PipelineStepImportMapPipelineStepImportColumns0Command(
                context=request.context,
                pipeline_step_id=request.pipeline_step.pipeline_step_id,
                reason=request.pipeline_step.block.reason,
                annotations=dict(request.annotations)
            )
            outgoing_0 = to_pipeline_step_import_map_pipeline_step_import_columns0_command(command_0)
            response_0 = await deps.clients.pipelines_pipeline_step_export.SchedulePipelineStepExport(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            command_1 = PipelineStepImportMapPipelineStepImportColumns1Command.model_validate(
                {
                    'context': request.context,
                    'pipeline_run_requester_phone': request.details.contact.phone,
                    'details_contact_email': request.details.contact.email,
                    'pipeline_run_requester_name': request.details.contact.name
                }
            )
            outgoing_1 = to_pipeline_step_import_map_pipeline_step_import_columns1_command(command_1)
            response_1 = await deps.clients.pipelines_pipeline_run_validation.CheckPipelineRunEligibility(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = pipelines_v1_pipeline_run_validation_service_pb2.ExplainPipelineRunDecisionRequest(
                context=request.context,
                details=pipelines_v1_pipeline_run_validation_service_pb2.ExplainPipelineRunDecisionRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(email=response_1.pipeline_run.assignee.email)
                )
            )
            send_2 = partial(
                deps.clients.pipelines_pipeline_run_validation.ExplainPipelineRunDecision,
                timeout=deps.settings.timeout
            )
            response_2 = await send_2(outgoing_2)
            returned_0_0 = response_0.result.status
            if returned_0_0:
                response.outcome.status = returned_0_0
            returned_0_1 = response_0.result.correlation_id
            if returned_0_1:
                response.result.correlation_id = returned_0_1
            returned_1_0 = response_1.outcome.effective_at
            if returned_1_0.ListFields():
                response.outcome.effective_at.MergeFrom(returned_1_0)
            returned_1_1 = response_1.outcome.message
            if returned_1_1:
                response.outcome.message = returned_1_1
            returned_2_0 = response_2.pipeline_run.assignee.display_name
            if returned_2_0:
                response.pipeline_step.owner.display_name = returned_2_0
            echoed_0 = request.pipeline_step_id
            response.pipeline_step.pipeline_step_id = echoed_0
            echoed_1 = request.pipeline_step.effective
            response.pipeline_step.effective.CopyFrom(echoed_1)
            return response

    async def handle_retry_pipeline_step_import(
        self,
        request: pipelines_v1_pipeline_step_import_service_pb2.RetryPipelineStepImportRequest
    ) -> pipelines_v1_pipeline_step_import_service_pb2.RetryPipelineStepImportResponse:
        """Retrys a pipeline step."""
        deps = self.deps
        response = pipelines_v1_pipeline_step_import_service_pb2.RetryPipelineStepImportResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('RetryPipelineStepImport', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'RetryPipelineStepImport',
                {'reason': request.reason}
            )
            await deps.repository.save_pipeline_step(request.context.tenant_id, request.pipeline_step)
            response_0 = ledger_v1_ledger_account_service_pb2.SearchLedgerAccountsResponse()
            response_1 = pipelines_v1_pipeline_run_import_service_pb2.MapPipelineRunImportColumnsResponse()
            response_2 = pipelines_v1_pipeline_run_calculation_service_pb2.ComparePipelineRunOptionsResponse()
            outgoing_0 = ledger_v1_ledger_account_service_pb2.SearchLedgerAccountsRequest(
                context=request.context,
                filter=ledger_v1_ledger_account_service_pb2.SearchLedgerAccountsRequest.Filter(
                    created_after=request.pipeline_step.audit.created_at,
                    labels=dict(request.pipeline_step.parameters)
                )
            )
            response_0 = await hooks.pipeline_step_import_retry_pipeline_step_import0(
                deps.clients.ledger_ledger_account,
                outgoing_0,
                deps.settings.timeout
            )
            outgoing_1 = pipelines_v1_pipeline_run_import_service_pb2.MapPipelineRunImportColumnsRequest()
            outgoing_1.context.CopyFrom(request.context)
            outgoing_1.pipeline_run.requester.phone = request.details.notify.phone
            outgoing_1.context.tenant_id = tenant_id.get()
            response_1 = await deps.clients.pipelines_pipeline_run_import.MapPipelineRunImportColumns(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = pipelines_v1_pipeline_run_calculation_service_pb2.ComparePipelineRunOptionsRequest(
                context=request.context,
                pipeline_run=pipelines_v1_pipelines_pb2.PipelineRun(
                    comments=[
                        pipelines_v1_pipelines_pb2.PipelineRunComment(
                            created_at=response_1.pipeline_run.audit.created_at
                        )
                    ],
                    sla=pipelines_v1_pipelines_pb2.PipelineRunSla(paused_for=response_1.pipeline_run.sla.paused_for)
                )
            )
            port_2: PipelineStepImportRetryPipelineStepImport2Port = PipelineStepImportRetryPipelineStepImport2Adapter(
                deps.clients.pipelines_pipeline_run_calculation,
                deps.settings.timeout
            )
            response_2 = await port_2.execute(outgoing_2)
            returned_0_0 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_0)
            returned_1_0 = response_1.outcome.status
            if returned_1_0:
                response.outcome.status = returned_1_0
            returned_2_0 = response_2.pipeline_run.audit.created_by
            if returned_2_0:
                response.pipeline_step.audit.created_by = returned_2_0
            echoed_0 = request.pipeline_step_id
            response.pipeline_step.pipeline_step_id = echoed_0
            echoed_1 = request.pipeline_step.owner
            response.pipeline_step.owner.CopyFrom(echoed_1)
            return response

    async def handle_validate_pipeline_step_import(
        self,
        request: pipelines_v1_pipeline_step_import_service_pb2.ValidatePipelineStepImportRequest
    ) -> pipelines_v1_pipeline_step_import_service_pb2.ValidatePipelineStepImportResponse:
        """Validates a pipeline step."""
        deps = self.deps
        response = pipelines_v1_pipeline_step_import_service_pb2.ValidatePipelineStepImportResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ValidatePipelineStepImport', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ValidatePipelineStepImport',
                {'reason': request.reason}
            )
            await deps.repository.save_pipeline_step(request.context.tenant_id, request.pipeline_step)
            response_0 = pipelines_v1_pipeline_step_export_service_pb2.ListPipelineStepExportsResponse()
            response_1 = pipelines_v1_pipeline_step_export_service_pb2.SharePipelineStepExportResponse()
            response_2 = pipelines_v1_pipeline_step_validation_service_pb2.CheckPipelineStepEligibilityResponse()
            outgoing_0 = pipelines_v1_pipeline_step_export_service_pb2.ListPipelineStepExportsRequest(
                context=request.context,
                filter=pipelines_v1_pipeline_step_export_service_pb2.ListPipelineStepExportsRequest.Filter(
                    created_after=request.pipeline_step.audit.created_at
                )
            )
            outgoing_1 = pipelines_v1_pipeline_step_export_service_pb2.SharePipelineStepExportRequest(
                context=request.context,
                details=pipelines_v1_pipeline_step_export_service_pb2.SharePipelineStepExportRequest.Details(
                    recipient=common_v1_contact_pb2.ContactInfo(email=request.details.contact.email)
                )
            )
            response_0, response_1 = await asyncio.gather(
                deps.clients.pipelines_pipeline_step_export.ListPipelineStepExports(
                    outgoing_0,
                    timeout=deps.settings.timeout
                ),
                deps.clients.pipelines_pipeline_step_export.SharePipelineStepExport(
                    outgoing_1,
                    timeout=deps.settings.timeout
                ),
            )
            for item_2 in request.pipeline_step.conditions:
                outgoing_2 = pipelines_v1_pipeline_step_validation_service_pb2.CheckPipelineStepEligibilityRequest(
                    context=request.context,
                    pipeline_step=pipelines_v1_pipelines_pb2.PipelineStep(
                        conditions=[
                            pipelines_v1_pipelines_pb2.PipelineStepCondition(
                                negate=item_2.negate,
                                operator=item_2.operator,
                                value=item_2.value
                            )
                        ]
                    )
                )
                response_2 = await deps.clients.pipelines_pipeline_step_validation.CheckPipelineStepEligibility(
                    outgoing_2,
                    timeout=deps.settings.timeout
                )
            returned_0_0 = response_0.result.status
            if returned_0_0:
                response.outcome.status = returned_0_0
            returned_1_0 = response_1.pipeline_step.audit.updated_at
            if returned_1_0.ListFields():
                response.pipeline_step.audit.updated_at.MergeFrom(returned_1_0)
            returned_1_1 = response_1.pipeline_step.audit.updated_by
            if returned_1_1:
                response.pipeline_step.audit.updated_by = returned_1_1
            echoed_0 = request.pipeline_step_id
            response.pipeline_step.pipeline_step_id = echoed_0
            echoed_1 = request.pipeline_step.name
            response.pipeline_step.name = echoed_1
            return response
