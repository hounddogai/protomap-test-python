"""Functional operations behind PipelineRunImportService."""

from __future__ import annotations

from collections.abc import Awaitable
from collections.abc import Callable
from typing import cast
import asyncio
import logging

from acme.audit.v1 import audit_event_validation_service_pb2 as audit_v1_audit_event_validation_service_pb2
from acme.audit.v1 import audit_pb2 as audit_v1_audit_pb2
from acme.audit.v1 import refs_pb2 as audit_v1_refs_pb2
from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.documents.v1 import document_service_pb2 as documents_v1_document_service_pb2
from acme.documents.v1 import documents_pb2 as documents_v1_documents_pb2
from acme.featurestore.v1 import entity_import_service_pb2 as featurestore_v1_entity_import_service_pb2
from acme.featurestore.v1 import entity_reporting_service_pb2 as featurestore_v1_entity_reporting_service_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.modelregistry.v1 import deployment_import_service_pb2 as modelregistry_v1_deployment_import_service_pb2
from acme.modelregistry.v1 import modelregistry_pb2 as modelregistry_v1_modelregistry_pb2
from acme.pipelines.v1 import pipeline_query_service_pb2 as pipelines_v1_pipeline_query_service_pb2
from acme.pipelines.v1 import pipeline_run_calculation_service_pb2 as pipelines_v1_pipeline_run_calculation_service_pb2
from acme.pipelines.v1 import pipeline_run_import_service_pb2 as pipelines_v1_pipeline_run_import_service_pb2
from acme.pipelines.v1 import pipeline_run_validation_service_pb2 as pipelines_v1_pipeline_run_validation_service_pb2
from acme.pipelines.v1 import (
    pipeline_run_validation_service_pb2_grpc as pipelines_v1_pipeline_run_validation_service_pb2_grpc,
)
from acme.pipelines.v1 import pipeline_service_pb2 as pipelines_v1_pipeline_service_pb2
from acme.pipelines.v1 import (
    pipeline_step_calculation_service_pb2 as pipelines_v1_pipeline_step_calculation_service_pb2,
)
from acme.pipelines.v1 import pipeline_step_validation_service_pb2 as pipelines_v1_pipeline_step_validation_service_pb2
from acme.pipelines.v1 import pipelines_pb2 as pipelines_v1_pipelines_pb2

from acme_data.domains.pipelines.adapters import PipelineRunImportValidatePipelineRunImport1Adapter
from acme_data.domains.pipelines.dependencies import Dependencies
from acme_data.platform.rpc import async_messages
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


async def handle_cancel_pipeline_run_import(
    deps: Dependencies,
    request: pipelines_v1_pipeline_run_import_service_pb2.CancelPipelineRunImportRequest
) -> pipelines_v1_pipeline_run_import_service_pb2.CancelPipelineRunImportResponse:
    """Cancels a pipeline run."""
    response = pipelines_v1_pipeline_run_import_service_pb2.CancelPipelineRunImportResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('CancelPipelineRunImport', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'CancelPipelineRunImport', {'reason': request.reason})
        response_0 = pipelines_v1_pipeline_step_validation_service_pb2.LintPipelineStepsResponse()
        response_1 = featurestore_v1_entity_import_service_pb2.RetryEntityImportResponse()
        outgoing_0 = pipelines_v1_pipeline_step_validation_service_pb2.LintPipelineStepsRequest(
            context=request.context,
            details=pipelines_v1_pipeline_step_validation_service_pb2.LintPipelineStepsRequest.Details(
                contact=common_v1_contact_pb2.ContactInfo(
                    preferred_channel=request.details.notify_contact.preferred_channel
                )
            ),
            pipeline_step=pipelines_v1_pipelines_pb2.PipelineStep(
                owner=identity_v1_refs_pb2.UserRef(display_name=request.details.new_owner.display_name)
            )
        )
        response_0 = await deps.clients.pipelines_pipeline_step_validation.LintPipelineSteps(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = featurestore_v1_entity_import_service_pb2.RetryEntityImportRequest()
        outgoing_1.context.CopyFrom(request.context)
        outgoing_1.entity.relationship_manager.email = request.details.notify_contact.email
        outgoing_1.entity.audit.updated_at.CopyFrom(response_0.pipeline_step.audit.updated_at)
        outgoing_1.details.notify.email = response_0.pipeline_step.owner.email
        outgoing_1.entity.name.CopyFrom(request.details.notify_contact.name)
        merged_1 = featurestore_v1_entity_import_service_pb2.RetryEntityImportRequest()
        merged_1.MergeFrom(outgoing_1)
        outgoing_1.CopyFrom(merged_1)
        response_1 = await deps.clients.featurestore_entity_import.RetryEntityImport(
            outgoing_1,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.pipeline_step.audit.created_at
        returned_0_0_part_1 = response.pipeline_run.comments.add()
        if returned_0_0.ListFields():
            returned_0_0_part_1.created_at.MergeFrom(returned_0_0)
        returned_0_1 = response_0.result.status
        if returned_0_1:
            response.outcome.status = returned_0_1
        returned_1_0 = response_1.entity.relationship_manager.user_id
        if returned_1_0:
            response.pipeline_run.assignee.user_id = returned_1_0
        echoed_0 = request.pipeline_run_id
        response.pipeline_run.pipeline_run_id = echoed_0
        echoed_1 = request.details.effective_at
        response.outcome.effective_at.CopyFrom(echoed_1)
        return response


async def handle_get_pipeline_run_import_status(
    deps: Dependencies,
    request: pipelines_v1_pipeline_run_import_service_pb2.GetPipelineRunImportStatusRequest
) -> pipelines_v1_pipeline_run_import_service_pb2.GetPipelineRunImportStatusResponse:
    """Returns a pipeline run."""
    response = pipelines_v1_pipeline_run_import_service_pb2.GetPipelineRunImportStatusResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('GetPipelineRunImportStatus', extra={'fields': {'domain': 'pipelines'}})
        await deps.repository.audit(request.context.tenant_id, 'GetPipelineRunImportStatus', {})
        response_0 = pipelines_v1_pipeline_step_calculation_service_pb2.ComparePipelineStepOptionsResponse()
        response_1 = pipelines_v1_pipeline_run_validation_service_pb2.LintPipelineRunsResponse()
        outgoing_0 = pipelines_v1_pipeline_step_calculation_service_pb2.ComparePipelineStepOptionsRequest(
            context=request.context,
            pipeline_step=pipelines_v1_pipelines_pb2.PipelineStep(
                owner=identity_v1_refs_pb2.UserRef(email=request.context.actor.email)
            )
        )
        response_0 = await deps.clients.pipelines_pipeline_step_calculation.ComparePipelineStepOptions(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = pipelines_v1_pipeline_run_validation_service_pb2.LintPipelineRunsRequest(
            context=request.context,
            pipeline_run=pipelines_v1_pipelines_pb2.PipelineRun(
                requester=common_v1_contact_pb2.ContactInfo(email=response_0.pipeline_step.owner.email)
            )
        )
        registered_1 = cast(
            pipelines_v1_pipeline_run_validation_service_pb2_grpc.PipelineRunValidationServiceStub,
            deps.clients.registry['acme.pipelines.v1.PipelineRunValidationService']
        )
        response_1 = await registered_1.LintPipelineRuns(outgoing_1, timeout=deps.settings.timeout)
        returned_0_0 = response_0.result.status
        if returned_0_0:
            response.result.status = returned_0_0
        returned_0_1 = response_0.pipeline_step.owner.display_name
        if returned_0_1:
            response.pipeline_run.assignee.display_name = returned_0_1
        returned_1_0 = response_1.pipeline_run.sla.due_at
        if returned_1_0.ListFields():
            response.pipeline_run.sla.due_at.MergeFrom(returned_1_0)
        returned_1_1 = response_1.pipeline_run.requester.email
        if returned_1_1:
            response.pipeline_run.assignee.email = returned_1_1
        echoed_0 = request.pipeline_run_id
        response.pipeline_run.pipeline_run_id = echoed_0
        return response


async def handle_import_pipeline_runs(
    deps: Dependencies,
    request: pipelines_v1_pipeline_run_import_service_pb2.ImportPipelineRunsRequest
) -> pipelines_v1_pipeline_run_import_service_pb2.ImportPipelineRunsResponse:
    """Takes a stream of pipeline runs and answers once at the end."""
    response = pipelines_v1_pipeline_run_import_service_pb2.ImportPipelineRunsResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('ImportPipelineRuns', extra={'fields': {'sequence': request.sequence}})
        await deps.repository.audit(request.context.tenant_id, 'ImportPipelineRuns', {'sequence': request.sequence})
        if request.WhichOneof('chunk') == 'record':
            await deps.repository.save_pipeline_run(request.context.tenant_id, request.record)
        response_0 = pipelines_v1_pipeline_query_service_pb2.FindPipelinesResponse()
        response_1 = pipelines_v1_pipeline_service_pb2.UpdatePipelineResponse()
        response_2 = documents_v1_document_service_pb2.CreateDocumentResponse()
        outgoing_0 = pipelines_v1_pipeline_query_service_pb2.FindPipelinesRequest(
            context=request.context,
            filter=pipelines_v1_pipeline_query_service_pb2.FindPipelinesRequest.Filter(
                created_after=request.record.audit.created_at,
                owner_id=request.record.customer.pipeline_id
            )
        )
        response_0 = await deps.clients.pipelines_pipeline_query.FindPipelines(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = pipelines_v1_pipeline_service_pb2.UpdatePipelineRequest()
        outgoing_1.context.CopyFrom(request.context)
        if request.WhichOneof('chunk') == 'record':
            field_1_1_part_1 = outgoing_1.pipeline.participants.add()
            field_1_1_part_1.contact.email = request.record.requester.email
        if request.WhichOneof('chunk') == 'record':
            field_1_2_part_1 = outgoing_1.pipeline.participants.add()
            field_1_2_part_1.contact.phone = request.record.requester.phone
        response_1 = await deps.clients.pipelines_pipeline.UpdatePipeline(outgoing_1, timeout=deps.settings.timeout)
        async for item_2 in async_messages(request.record.comments):
            outgoing_2 = documents_v1_document_service_pb2.CreateDocumentRequest(
                context=request.context,
                document=documents_v1_documents_pb2.Document(
                    audit=common_v1_audit_pb2.AuditInfo(
                        created_at=item_2.created_at,
                        updated_at=response_1.pipeline.audit.updated_at
                    ),
                    billing_address=common_v1_address_pb2.PostalAddress(
                        country_code=response_1.pipeline.location.country_code
                    )
                )
            )
            response_2 = await deps.clients.documents_document.CreateDocument(outgoing_2, timeout=deps.settings.timeout)
        returned_0_0 = response_0.result.message
        if returned_0_0:
            response.result.message = returned_0_0
        returned_1_0 = response_1.result.correlation_id
        if returned_1_0:
            response.result.correlation_id = returned_1_0
        return response


async def handle_list_pipeline_run_imports(
    deps: Dependencies,
    request: pipelines_v1_pipeline_run_import_service_pb2.ListPipelineRunImportsRequest
) -> pipelines_v1_pipeline_run_import_service_pb2.ListPipelineRunImportsResponse:
    """Lists pipeline runs a page at a time."""
    response = pipelines_v1_pipeline_run_import_service_pb2.ListPipelineRunImportsResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('ListPipelineRunImports', extra={'fields': {'order_by': request.order_by}})
        await deps.repository.audit(request.context.tenant_id, 'ListPipelineRunImports', {'order_by': request.order_by})
        return response


async def handle_map_pipeline_run_import_columns(
    deps: Dependencies,
    request: pipelines_v1_pipeline_run_import_service_pb2.MapPipelineRunImportColumnsRequest
) -> pipelines_v1_pipeline_run_import_service_pb2.MapPipelineRunImportColumnsResponse:
    """Maps a pipeline run."""
    response = pipelines_v1_pipeline_run_import_service_pb2.MapPipelineRunImportColumnsResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('MapPipelineRunImportColumns', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(
            request.context.tenant_id,
            'MapPipelineRunImportColumns',
            {'reason': request.reason}
        )
        await deps.repository.save_pipeline_run(request.context.tenant_id, request.pipeline_run)
        response_0 = pipelines_v1_pipeline_query_service_pb2.ExportPipelinesResponse()
        outgoing_0 = pipelines_v1_pipeline_query_service_pb2.ExportPipelinesRequest(
            context=request.context,
            filter=pipelines_v1_pipeline_query_service_pb2.ExportPipelinesRequest.Filter(
                created_after=request.pipeline_run.audit.updated_at,
                labels=dict(request.pipeline_run.custom_fields),
                owner_id=request.pipeline_run.sla.policy_id
            )
        )
        async for chunk_0 in deps.clients.pipelines_pipeline_query.ExportPipelines(
            outgoing_0,
            timeout=deps.settings.timeout
        ):
            response_0 = chunk_0
        echoed_0 = request.pipeline_run_id
        response.pipeline_run.pipeline_run_id = echoed_0
        echoed_1 = request.pipeline_run.subject
        response.pipeline_run.subject = echoed_1
        return response


async def handle_retry_pipeline_run_import(
    deps: Dependencies,
    request: pipelines_v1_pipeline_run_import_service_pb2.RetryPipelineRunImportRequest
) -> pipelines_v1_pipeline_run_import_service_pb2.RetryPipelineRunImportResponse:
    """Retrys a pipeline run."""
    response = pipelines_v1_pipeline_run_import_service_pb2.RetryPipelineRunImportResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('RetryPipelineRunImport', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'RetryPipelineRunImport', {'reason': request.reason})
        await deps.repository.save_pipeline_run(request.context.tenant_id, request.pipeline_run)
        response_0 = audit_v1_audit_event_validation_service_pb2.CheckAuditEventEligibilityResponse()
        response_1 = pipelines_v1_pipeline_run_calculation_service_pb2.GetPipelineRunRatesResponse()
        outgoing_0 = audit_v1_audit_event_validation_service_pb2.CheckAuditEventEligibilityRequest(
            audit_event=audit_v1_audit_pb2.AuditEvent(
                subject=audit_v1_refs_pb2.AuditTrailRef(display_name=request.pipeline_run.customer.display_name)
            ),
            context=request.context,
            details=audit_v1_audit_event_validation_service_pb2.CheckAuditEventEligibilityRequest.Details(
                contact=common_v1_contact_pb2.ContactInfo(
                    email=request.details.notify.email,
                    phone=request.details.notify.phone,
                    preferred_channel=request.pipeline_run.requester.preferred_channel
                )
            )
        )
        outgoing_1 = pipelines_v1_pipeline_run_calculation_service_pb2.GetPipelineRunRatesRequest(
            context=request.context,
            pipeline_run_id=request.pipeline_run.pipeline_run_id
        )
        response_0, response_1 = await asyncio.gather(
            deps.clients.audit_audit_event_validation.CheckAuditEventEligibility(
                outgoing_0,
                timeout=deps.settings.timeout
            ),
            deps.clients.pipelines_pipeline_run_calculation.GetPipelineRunRates(
                outgoing_1,
                timeout=deps.settings.timeout
            ),
        )
        returned_0_0 = response_0.result.correlation_id
        if returned_0_0:
            response.result.correlation_id = returned_0_0
        returned_1_0 = response_1.pipeline_run.requester.email
        if returned_1_0:
            response.pipeline_run.requester.email = returned_1_0
        returned_1_1 = response_1.pipeline_run.requester.email
        if returned_1_1:
            response.pipeline_run.assignee.email = returned_1_1
        echoed_0 = request.pipeline_run_id
        response.pipeline_run.pipeline_run_id = echoed_0
        echoed_1 = request.pipeline_run.priority
        response.pipeline_run.priority = echoed_1
        return response


async def handle_validate_pipeline_run_import(
    deps: Dependencies,
    request: pipelines_v1_pipeline_run_import_service_pb2.ValidatePipelineRunImportRequest
) -> pipelines_v1_pipeline_run_import_service_pb2.ValidatePipelineRunImportResponse:
    """Validates a pipeline run."""
    response = pipelines_v1_pipeline_run_import_service_pb2.ValidatePipelineRunImportResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('ValidatePipelineRunImport', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'ValidatePipelineRunImport', {'reason': request.reason})
        await deps.repository.save_pipeline_run(request.context.tenant_id, request.pipeline_run)
        response_0 = featurestore_v1_entity_reporting_service_pb2.ListEntityReportsResponse()
        response_1 = modelregistry_v1_deployment_import_service_pb2.ValidateDeploymentImportResponse()
        outgoing_0 = featurestore_v1_entity_reporting_service_pb2.ListEntityReportsRequest(
            context=request.context,
            filter=featurestore_v1_entity_reporting_service_pb2.ListEntityReportsRequest.Filter(
                created_after=request.pipeline_run.audit.created_at,
                labels=dict(request.annotations),
                owner_id=request.pipeline_run.assignee.user_id
            )
        )
        response_0 = await deps.clients.featurestore_entity_reporting.ListEntityReports(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = modelregistry_v1_deployment_import_service_pb2.ValidateDeploymentImportRequest(
            context=request.context,
            deployment=modelregistry_v1_modelregistry_pb2.Deployment(
                participants=[
                    modelregistry_v1_modelregistry_pb2.DeploymentParticipant(
                        contact=common_v1_contact_pb2.ContactInfo(
                            email=request.pipeline_run.assignee.email,
                            preferred_channel=request.details.contact.preferred_channel
                        )
                    )
                ]
            )
        )
        response_1 = await PipelineRunImportValidatePipelineRunImport1Adapter(
            deps.clients.modelregistry_deployment_import,
            deps.settings.timeout
        )(outgoing_1)
        returned_0_0 = response_0.result.message
        if returned_0_0:
            response.outcome.message = returned_0_0
        returned_1_0 = response_1.result.message
        if returned_1_0:
            response.outcome.message = returned_1_0
        returned_1_1 = response_1.deployment.audit.created_at
        if returned_1_1.ListFields():
            response.pipeline_run.audit.created_at.MergeFrom(returned_1_1)
        echoed_0 = request.pipeline_run_id
        response.pipeline_run.pipeline_run_id = echoed_0
        echoed_1 = request.pipeline_run.custom_fields
        response.pipeline_run.custom_fields.update(echoed_1)
        return response
