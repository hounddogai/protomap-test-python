"""Application workflow for Pipeline Workflow."""

from __future__ import annotations

from collections.abc import Awaitable
from collections.abc import Callable
from functools import partial
from typing import Any
from typing import cast
import asyncio
import logging

from google.protobuf.json_format import MessageToDict
from google.protobuf.json_format import MessageToJson
from google.protobuf.json_format import Parse
from google.protobuf.json_format import ParseDict

from acme.authorization.v1 import access_policy_service_pb2 as authorization_v1_access_policy_service_pb2
from acme.authorization.v1 import authorization_pb2 as authorization_v1_authorization_pb2
from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.drivers.v1 import driver_calculation_service_pb2 as drivers_v1_driver_calculation_service_pb2
from acme.drivers.v1 import drivers_pb2 as drivers_v1_drivers_pb2
from acme.featurestore.v1 import (
    feature_value_approval_service_pb2 as featurestore_v1_feature_value_approval_service_pb2,
)
from acme.featurestore.v1 import feature_view_sync_service_pb2 as featurestore_v1_feature_view_sync_service_pb2
from acme.featurestore.v1 import featurestore_pb2 as featurestore_v1_featurestore_pb2
from acme.identity.v1 import identity_pb2 as identity_v1_identity_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.identity.v1 import user_validation_service_pb2 as identity_v1_user_validation_service_pb2
from acme.lineage.v1 import lineage_edge_import_service_pb2 as lineage_v1_lineage_edge_import_service_pb2
from acme.modelregistry.v1 import modelregistry_pb2 as modelregistry_v1_modelregistry_pb2
from acme.modelregistry.v1 import (
    registered_model_sync_service_pb2 as modelregistry_v1_registered_model_sync_service_pb2,
)
from acme.pipelines.v1 import pipeline_approval_service_pb2 as pipelines_v1_pipeline_approval_service_pb2
from acme.pipelines.v1 import pipeline_lifecycle_service_pb2 as pipelines_v1_pipeline_lifecycle_service_pb2
from acme.pipelines.v1 import pipeline_run_calculation_service_pb2 as pipelines_v1_pipeline_run_calculation_service_pb2
from acme.pipelines.v1 import pipeline_service_pb2 as pipelines_v1_pipeline_service_pb2
from acme.pipelines.v1 import pipeline_step_import_service_pb2 as pipelines_v1_pipeline_step_import_service_pb2
from acme.pipelines.v1 import pipeline_step_reporting_service_pb2 as pipelines_v1_pipeline_step_reporting_service_pb2
from acme.pipelines.v1 import pipeline_sync_service_pb2 as pipelines_v1_pipeline_sync_service_pb2
from acme.pipelines.v1 import pipeline_workflow_service_pb2 as pipelines_v1_pipeline_workflow_service_pb2
from acme.pipelines.v1 import pipelines_pb2 as pipelines_v1_pipelines_pb2
from acme.routing.v1 import route_service_pb2 as routing_v1_route_service_pb2

from acme_data.domains.pipelines import hooks
from acme_data.domains.pipelines.adapters import PipelineWorkflowResumePipelineWorkflow1Adapter
from acme_data.domains.pipelines.adapters import PipelineWorkflowResumePipelineWorkflow1Port
from acme_data.domains.pipelines.adapters import PipelineWorkflowRetryPipelineWorkflow0Adapter
from acme_data.domains.pipelines.dependencies import Dependencies
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import run_steps
from acme_data.platform.tenancy import tenant_id
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class PipelineWorkflowServicerWorkflow:
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    async def handle_advance_pipeline_workflow(
        self,
        request: pipelines_v1_pipeline_workflow_service_pb2.AdvancePipelineWorkflowRequest
    ) -> pipelines_v1_pipeline_workflow_service_pb2.AdvancePipelineWorkflowResponse:
        """Advances a pipeline."""
        deps = self.deps
        response = pipelines_v1_pipeline_workflow_service_pb2.AdvancePipelineWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('AdvancePipelineWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'AdvancePipelineWorkflow',
                {'reason': request.reason}
            )
            await deps.repository.save_pipeline(request.context.tenant_id, request.pipeline)
            response_0 = pipelines_v1_pipeline_lifecycle_service_pb2.SchedulePipelineExpiryResponse()
            response_1 = pipelines_v1_pipeline_lifecycle_service_pb2.TerminatePipelineResponse()
            response_2 = identity_v1_user_validation_service_pb2.PreviewUserResponse()
            outgoing_0 = pipelines_v1_pipeline_lifecycle_service_pb2.SchedulePipelineExpiryRequest(
                context=request.context,
                pipeline=pipelines_v1_pipelines_pb2.Pipeline(
                    daily=pipelines_v1_pipelines_pb2.PipelineDailyRule(interval=request.pipeline.weekly.interval),
                    participants=[
                        pipelines_v1_pipelines_pb2.PipelineParticipant(
                            contact=common_v1_contact_pb2.ContactInfo(email=request.pipeline.organizer.email)
                        )
                    ]
                )
            )
            method_name_0 = 'SchedulePipelineExpiry'
            response_0 = await getattr(
                deps.clients.pipelines_pipeline_lifecycle,
                method_name_0
            )(outgoing_0, timeout=deps.settings.timeout)
            requests_1: list[pipelines_v1_pipeline_lifecycle_service_pb2.TerminatePipelineRequest] = []
            for item_1 in request.pipeline.participants:
                outgoing_1 = pipelines_v1_pipeline_lifecycle_service_pb2.TerminatePipelineRequest(
                    context=request.context,
                    details=pipelines_v1_pipeline_lifecycle_service_pb2.TerminatePipelineRequest.Details(
                        notify_contact=common_v1_contact_pb2.ContactInfo(
                            email=item_1.contact.email,
                            name=item_1.contact.name,
                            phone=item_1.contact.phone,
                            preferred_channel=item_1.contact.preferred_channel
                        )
                    ),
                    pipeline_id=request.pipeline_id
                )
                requests_1.append(outgoing_1)
            replies_1 = await asyncio.gather(*(
                deps.clients.pipelines_pipeline_lifecycle.TerminatePipeline(
                    entry,
                    timeout=deps.settings.timeout
                ) for entry in requests_1
            ))
            if replies_1:
                response_1 = replies_1[-1]
            outgoing_2 = identity_v1_user_validation_service_pb2.PreviewUserRequest(
                context=request.context,
                details=identity_v1_user_validation_service_pb2.PreviewUserRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(email=response_0.pipeline.organizer.email)
                ),
                user=identity_v1_identity_pb2.User(
                    contact=common_v1_contact_pb2.ContactInfo(email=request.details.notify.email),
                    primary_address=common_v1_address_pb2.PostalAddress(
                        locality=request.pipeline.location.locality,
                        region=response_1.pipeline.location.region
                    )
                )
            )
            document_2 = MessageToDict(outgoing_2, preserving_proto_field_name=True)
            outgoing_2 = ParseDict(document_2, identity_v1_user_validation_service_pb2.PreviewUserRequest())
            response_2 = await deps.clients.identity_user_validation.PreviewUser(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.pipeline.location.country_code
            if returned_0_0:
                response.pipeline.location.country_code = returned_0_0
            returned_0_1 = response_0.pipeline.organizer.email
            returned_0_1_part_1 = response.pipeline.participants.add()
            if returned_0_1:
                returned_0_1_part_1.contact.email = returned_0_1
            returned_2_0 = response_2.result.reference_ids
            response.result.reference_ids.extend(returned_2_0)
            echoed_0 = request.pipeline_id
            response.pipeline.pipeline_id = echoed_0
            echoed_1 = request.pipeline.title
            response.pipeline.title = echoed_1
            return response

    async def handle_cancel_pipeline_workflow(
        self,
        request: pipelines_v1_pipeline_workflow_service_pb2.CancelPipelineWorkflowRequest
    ) -> pipelines_v1_pipeline_workflow_service_pb2.CancelPipelineWorkflowResponse:
        """Cancels a pipeline."""
        deps = self.deps
        response = pipelines_v1_pipeline_workflow_service_pb2.CancelPipelineWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CancelPipelineWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'CancelPipelineWorkflow', {'reason': request.reason})
            await deps.repository.save_pipeline(request.context.tenant_id, request.pipeline)
            response_0 = pipelines_v1_pipeline_sync_service_pb2.ReconcilePipelinesResponse()
            response_1 = modelregistry_v1_registered_model_sync_service_pb2.ResolveRegisteredModelConflictResponse()
            outgoing_0 = pipelines_v1_pipeline_sync_service_pb2.ReconcilePipelinesRequest(
                context=request.context,
                pipeline=pipelines_v1_pipelines_pb2.Pipeline(
                    daily=pipelines_v1_pipelines_pb2.PipelineDailyRule(interval=request.pipeline.daily.interval),
                    participants=[
                        pipelines_v1_pipelines_pb2.PipelineParticipant(
                            contact=common_v1_contact_pb2.ContactInfo(
                                preferred_channel=request.details.notify.preferred_channel
                            )
                        )
                    ]
                )
            )
            document_0 = MessageToJson(outgoing_0, preserving_proto_field_name=True)
            outgoing_0 = Parse(document_0, pipelines_v1_pipeline_sync_service_pb2.ReconcilePipelinesRequest())
            response_0 = await deps.clients.pipelines_pipeline_sync.ReconcilePipelines(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            callbacks_1: list[
                Callable[
                    [],
                    Awaitable[modelregistry_v1_registered_model_sync_service_pb2.ResolveRegisteredModelConflictResponse]
                ]
            ] = []
            for item_1 in request.pipeline.participants:
                outgoing_1 = modelregistry_v1_registered_model_sync_service_pb2.ResolveRegisteredModelConflictRequest(
                    context=request.context,
                    registered_model=modelregistry_v1_modelregistry_pb2.RegisteredModel(
                        address=common_v1_address_pb2.PostalAddress(locality=request.pipeline.location.locality),
                        owner=identity_v1_refs_pb2.UserRef(email=item_1.contact.email)
                    )
                )
                async def send_1(
                    payload: modelregistry_v1_registered_model_sync_service_pb2.ResolveRegisteredModelConflictRequest = outgoing_1
                ) -> modelregistry_v1_registered_model_sync_service_pb2.ResolveRegisteredModelConflictResponse:
                    return await deps.clients.modelregistry_registered_model_sync.ResolveRegisteredModelConflict(
                        payload,
                        timeout=deps.settings.timeout
                    )
                callbacks_1.append(send_1)
            for callback_1 in callbacks_1:
                response_1 = await callback_1()
            returned_0_0 = response_0.pipeline.location.lines
            response.pipeline.location.lines.extend(returned_0_0)
            echoed_0 = request.pipeline_id
            response.pipeline.pipeline_id = echoed_0
            echoed_1 = request.pipeline.organizer
            response.pipeline.organizer.CopyFrom(echoed_1)
            return response

    async def handle_inspect_pipeline_workflow(
        self,
        request: pipelines_v1_pipeline_workflow_service_pb2.InspectPipelineWorkflowRequest
    ) -> pipelines_v1_pipeline_workflow_service_pb2.InspectPipelineWorkflowResponse:
        """Returns a pipeline."""
        deps = self.deps
        response = pipelines_v1_pipeline_workflow_service_pb2.InspectPipelineWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('InspectPipelineWorkflow', extra={'fields': {'domain': 'pipelines'}})
            await deps.repository.audit(request.context.tenant_id, 'InspectPipelineWorkflow', {})
            response_0 = pipelines_v1_pipeline_step_import_service_pb2.RetryPipelineStepImportResponse()
            outgoing_0 = pipelines_v1_pipeline_step_import_service_pb2.RetryPipelineStepImportRequest(
                context=request.context,
                details=pipelines_v1_pipeline_step_import_service_pb2.RetryPipelineStepImportRequest.Details(
                    parameters=dict(request.context.baggage)
                ),
                pipeline_step=pipelines_v1_pipelines_pb2.PipelineStep(
                    audit=common_v1_audit_pb2.AuditInfo(created_at=request.context.deadline),
                    owner=identity_v1_refs_pb2.UserRef(
                        email=request.context.actor.email,
                        user_id=request.context.actor.user_id
                    )
                )
            )
            response_0 = await deps.clients.pipelines_pipeline_step_import.RetryPipelineStepImport(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.pipeline_step.audit.updated_by
            if returned_0_0:
                response.pipeline.audit.updated_by = returned_0_0
            echoed_0 = request.pipeline_id
            response.pipeline.pipeline_id = echoed_0
            return response

    async def handle_list_pipeline_workflows(
        self,
        request: pipelines_v1_pipeline_workflow_service_pb2.ListPipelineWorkflowsRequest
    ) -> pipelines_v1_pipeline_workflow_service_pb2.ListPipelineWorkflowsResponse:
        """Lists pipelines a page at a time."""
        deps = self.deps
        response = pipelines_v1_pipeline_workflow_service_pb2.ListPipelineWorkflowsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ListPipelineWorkflows', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ListPipelineWorkflows',
                {'order_by': request.order_by}
            )
            response_0 = pipelines_v1_pipeline_approval_service_pb2.RejectPipelineResponse()
            outgoing_0 = pipelines_v1_pipeline_approval_service_pb2.RejectPipelineRequest(
                context=request.context,
                pipeline=pipelines_v1_pipelines_pb2.Pipeline(
                    location=common_v1_address_pb2.PostalAddress(region=request.filter.region),
                    participants=[
                        pipelines_v1_pipelines_pb2.PipelineParticipant(
                            contact=common_v1_contact_pb2.ContactInfo(email=request.context.actor.email)
                        )
                    ]
                )
            )
            response_0 = await deps.clients.pipelines_pipeline_approval.RejectPipeline(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.pipeline.location.lines
            returned_0_0_part_0 = response.pipelines.add()
            returned_0_0_part_0.location.lines.extend(returned_0_0)
            returned_0_1 = response_0.pipeline.metadata
            returned_0_1_part_0 = response.pipelines.add()
            returned_0_1_part_0.metadata.update(returned_0_1)
            return response

    async def handle_pause_pipeline_workflow(
        self,
        request: pipelines_v1_pipeline_workflow_service_pb2.PausePipelineWorkflowRequest
    ) -> pipelines_v1_pipeline_workflow_service_pb2.PausePipelineWorkflowResponse:
        """Pauses a pipeline."""
        deps = self.deps
        response = pipelines_v1_pipeline_workflow_service_pb2.PausePipelineWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('PausePipelineWorkflow', extra={'fields': {'initiated_by': request.details.initiated_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'PausePipelineWorkflow',
                {'initiated_by': request.details.initiated_by}
            )
            await deps.repository.save_pipeline(request.context.tenant_id, request.pipeline)
            response_0 = lineage_v1_lineage_edge_import_service_pb2.ValidateLineageEdgeImportResponse()
            response_1 = pipelines_v1_pipeline_step_reporting_service_pb2.GeneratePipelineStepReportResponse()
            response_2 = pipelines_v1_pipeline_approval_service_pb2.GetPipelineApprovalStatusResponse()
            response_3 = drivers_v1_driver_calculation_service_pb2.CalculateDriverResponse()
            outgoing_1 = pipelines_v1_pipeline_step_reporting_service_pb2.GeneratePipelineStepReportRequest(
                annotations=dict(request.annotations),
                context=request.context,
                details=pipelines_v1_pipeline_step_reporting_service_pb2.GeneratePipelineStepReportRequest.Details(
                    period=request.pipeline.window
                ),
                reason=request.reason
            )
            outgoing_2 = pipelines_v1_pipeline_approval_service_pb2.GetPipelineApprovalStatusRequest(
                context=request.context,
                pipeline_id=request.pipeline.pipeline_id
            )
            response_1, response_2 = await asyncio.gather(
                deps.clients.pipelines_pipeline_step_reporting.GeneratePipelineStepReport(
                    outgoing_1,
                    timeout=deps.settings.timeout
                ),
                deps.clients.pipelines_pipeline_approval.GetPipelineApprovalStatus(
                    outgoing_2,
                    timeout=deps.settings.timeout
                ),
            )
            async for item_0 in async_messages(request.pipeline.participants):
                outgoing_0 = lineage_v1_lineage_edge_import_service_pb2.ValidateLineageEdgeImportRequest(
                    context=request.context,
                    details=lineage_v1_lineage_edge_import_service_pb2.ValidateLineageEdgeImportRequest.Details(
                        contact=common_v1_contact_pb2.ContactInfo(
                            email=item_0.contact.email,
                            phone=item_0.contact.phone,
                            preferred_channel=item_0.contact.preferred_channel
                        )
                    )
                )
                response_0 = await deps.clients.lineage_lineage_edge_import.ValidateLineageEdgeImport(
                    outgoing_0,
                    timeout=deps.settings.timeout
                )
            outgoing_3 = drivers_v1_driver_calculation_service_pb2.CalculateDriverRequest(
                context=request.context,
                driver=drivers_v1_drivers_pb2.Driver(
                    contact=common_v1_contact_pb2.ContactInfo(name=request.details.notify.name),
                    primary_address=common_v1_address_pb2.PostalAddress(region=response_2.pipeline.location.region),
                    relationship_manager=identity_v1_refs_pb2.UserRef(user_id=request.pipeline.organizer.user_id)
                )
            )
            response_3 = await hooks.pipeline_workflow_pause_pipeline_workflow3(
                deps.clients.drivers_driver_calculation,
                outgoing_3,
                deps.settings.timeout
            )
            returned_1_0 = response_1.result.reference_ids
            response.result.reference_ids.extend(returned_1_0)
            returned_2_0 = response_2.result.message
            if returned_2_0:
                response.outcome.message = returned_2_0
            returned_3_0 = response_3.driver.audit.updated_at
            if returned_3_0.ListFields():
                response.pipeline.audit.updated_at.MergeFrom(returned_3_0)
            returned_3_1 = response_3.driver.audit.etag
            if returned_3_1:
                response.pipeline.audit.etag = returned_3_1
            echoed_0 = request.pipeline_id
            response.pipeline.pipeline_id = echoed_0
            echoed_1 = request.pipeline.status
            response.pipeline.status = echoed_1
            return response

    async def handle_resume_pipeline_workflow(
        self,
        request: pipelines_v1_pipeline_workflow_service_pb2.ResumePipelineWorkflowRequest
    ) -> pipelines_v1_pipeline_workflow_service_pb2.ResumePipelineWorkflowResponse:
        """Resumes a pipeline."""
        deps = self.deps
        response = pipelines_v1_pipeline_workflow_service_pb2.ResumePipelineWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ResumePipelineWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'ResumePipelineWorkflow', {'reason': request.reason})
            await deps.repository.save_pipeline(request.context.tenant_id, request.pipeline)
            response_0 = pipelines_v1_pipeline_run_calculation_service_pb2.QuotePipelineRunResponse()
            response_1 = pipelines_v1_pipeline_sync_service_pb2.PullPipelinesResponse()
            response_2 = modelregistry_v1_registered_model_sync_service_pb2.ResolveRegisteredModelConflictResponse()
            outgoing_0 = pipelines_v1_pipeline_run_calculation_service_pb2.QuotePipelineRunRequest()
            outgoing_0.context.CopyFrom(request.context)
            field_0_1_part_1 = outgoing_0.pipeline_run.comments.add()
            field_0_1_part_1.created_at.CopyFrom(request.pipeline.audit.created_at)
            outgoing_0.pipeline_run.requester.preferred_channel = request.details.notify.preferred_channel
            outgoing_0.pipeline_run.requester.email = request.pipeline.organizer.email
            outgoing_0.pipeline_run.customer.display_name = request.pipeline.organizer.display_name
            outgoing_0.context.tenant_id = tenant_id.get()
            response_0 = await deps.clients.pipelines_pipeline_run_calculation.QuotePipelineRun(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = pipelines_v1_pipeline_sync_service_pb2.PullPipelinesRequest(
                context=request.context,
                pipeline=pipelines_v1_pipelines_pb2.Pipeline(
                    participants=[
                        pipelines_v1_pipelines_pb2.PipelineParticipant(
                            contact=common_v1_contact_pb2.ContactInfo(
                                email=response_0.pipeline_run.requester.email,
                                name=request.details.notify.name
                            )
                        )
                    ],
                    weekly=pipelines_v1_pipelines_pb2.PipelineWeeklyRule(days=list(request.pipeline.weekly.days))
                )
            )
            port_1: PipelineWorkflowResumePipelineWorkflow1Port = PipelineWorkflowResumePipelineWorkflow1Adapter(
                deps.clients.pipelines_pipeline_sync,
                deps.settings.timeout
            )
            response_1 = await port_1.execute(outgoing_1)
            outgoing_2 = modelregistry_v1_registered_model_sync_service_pb2.ResolveRegisteredModelConflictRequest(
                context=request.context,
                registered_model=modelregistry_v1_modelregistry_pb2.RegisteredModel(
                    address=common_v1_address_pb2.PostalAddress(locality=response_1.pipeline.location.locality),
                    audit=common_v1_audit_pb2.AuditInfo(etag=response_0.pipeline_run.audit.etag)
                )
            )
            steps_2 = [
                partial(
                    deps.clients.modelregistry_registered_model_sync.ResolveRegisteredModelConflict,
                    outgoing_2,
                    timeout=deps.settings.timeout
                )
            ]
            results_2 = await run_steps(steps_2)
            response_2 = results_2[-1]
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.outcome.message = returned_0_0
            returned_1_0 = response_1.pipeline.title
            if returned_1_0:
                response.pipeline.title = returned_1_0
            returned_1_1 = response_1.result.status
            if returned_1_1:
                response.result.status = returned_1_1
            returned_2_0 = response_2.outcome.reference_id
            if returned_2_0:
                response.outcome.reference_id = returned_2_0
            echoed_0 = request.pipeline_id
            response.pipeline.pipeline_id = echoed_0
            echoed_1 = request.pipeline.organizer
            response.pipeline.organizer.CopyFrom(echoed_1)
            return response

    async def handle_retry_pipeline_workflow(
        self,
        request: pipelines_v1_pipeline_workflow_service_pb2.RetryPipelineWorkflowRequest
    ) -> pipelines_v1_pipeline_workflow_service_pb2.RetryPipelineWorkflowResponse:
        """Retrys a pipeline."""
        deps = self.deps
        response = pipelines_v1_pipeline_workflow_service_pb2.RetryPipelineWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('RetryPipelineWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'RetryPipelineWorkflow', {'reason': request.reason})
            await deps.repository.save_pipeline(request.context.tenant_id, request.pipeline)
            response_0 = pipelines_v1_pipeline_approval_service_pb2.EscalatePipelineResponse()
            response_1 = authorization_v1_access_policy_service_pb2.CreateAccessPolicyResponse()
            response_2 = routing_v1_route_service_pb2.ListRoutesResponse()
            outgoing_0 = pipelines_v1_pipeline_approval_service_pb2.EscalatePipelineRequest(
                context=request.context,
                pipeline=pipelines_v1_pipelines_pb2.Pipeline(
                    participants=[
                        pipelines_v1_pipelines_pb2.PipelineParticipant(
                            contact=common_v1_contact_pb2.ContactInfo(email=request.pipeline.organizer.email)
                        )
                    ]
                )
            )
            response_0 = await PipelineWorkflowRetryPipelineWorkflow0Adapter(
                deps.clients.pipelines_pipeline_approval,
                deps.settings.timeout
            )(outgoing_0)
            outgoing_1 = authorization_v1_access_policy_service_pb2.CreateAccessPolicyRequest(
                access_policy=authorization_v1_authorization_pb2.AccessPolicy(
                    audit=common_v1_audit_pb2.AuditInfo(
                        created_at=request.pipeline.audit.created_at,
                        updated_at=request.pipeline.audit.updated_at
                    ),
                    owner=identity_v1_refs_pb2.UserRef(display_name=response_0.pipeline.organizer.display_name)
                ),
                context=request.context
            )
            response_1 = cast(authorization_v1_access_policy_service_pb2.CreateAccessPolicyResponse, await deps.bus.request(
                'acme.pipelines.v1.PipelineWorkflowService/RetryPipelineWorkflow/1', outgoing_1, deps.settings.timeout,
            ))
            outgoing_2 = routing_v1_route_service_pb2.ListRoutesRequest(
                context=request.context,
                filter=routing_v1_route_service_pb2.ListRoutesRequest.Filter(
                    created_after=response_1.access_policy.audit.updated_at,
                    region=request.pipeline.location.region
                )
            )
            response_2 = await deps.clients.routing_route.ListRoutes(outgoing_2, timeout=deps.settings.timeout)
            returned_0_0 = response_0.outcome.next_steps
            response.outcome.next_steps.extend(returned_0_0)
            returned_1_0 = response_1.access_policy.owner.user_id
            if returned_1_0:
                response.pipeline.organizer.user_id = returned_1_0
            returned_1_1 = response_1.access_policy.owner.email
            if returned_1_1:
                response.pipeline.organizer.email = returned_1_1
            returned_2_0 = response_2.result.correlation_id
            if returned_2_0:
                response.result.correlation_id = returned_2_0
            returned_2_1 = response_2.result.reference_ids
            response.result.reference_ids.extend(returned_2_1)
            echoed_0 = request.pipeline_id
            response.pipeline.pipeline_id = echoed_0
            echoed_1 = request.pipeline.status
            response.pipeline.status = echoed_1
            return response

    async def handle_signal_pipeline_workflow(
        self,
        request: pipelines_v1_pipeline_workflow_service_pb2.SignalPipelineWorkflowRequest
    ) -> pipelines_v1_pipeline_workflow_service_pb2.SignalPipelineWorkflowResponse:
        """Signals a pipeline."""
        deps = self.deps
        response = pipelines_v1_pipeline_workflow_service_pb2.SignalPipelineWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SignalPipelineWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'SignalPipelineWorkflow', {'reason': request.reason})
            await deps.repository.save_pipeline(request.context.tenant_id, request.pipeline)
            response_0 = featurestore_v1_feature_value_approval_service_pb2.CommentFeatureValueApprovalResponse()
            outgoing_0 = featurestore_v1_feature_value_approval_service_pb2.CommentFeatureValueApprovalRequest(
                context=request.context,
                details=featurestore_v1_feature_value_approval_service_pb2.CommentFeatureValueApprovalRequest.Details(
                    approver=identity_v1_refs_pb2.UserRef(email=request.pipeline.organizer.email)
                )
            )
            method_name_0 = 'CommentFeatureValueApproval'
            response_0 = await getattr(
                deps.clients.featurestore_feature_value_approval,
                method_name_0
            )(outgoing_0, timeout=deps.settings.timeout)
            returned_0_0 = response_0.result.status
            if returned_0_0:
                response.result.status = returned_0_0
            returned_0_1 = response_0.outcome.effective_at
            if returned_0_1.ListFields():
                response.outcome.effective_at.MergeFrom(returned_0_1)
            echoed_0 = request.pipeline_id
            response.pipeline.pipeline_id = echoed_0
            echoed_1 = request.pipeline.organizer
            response.pipeline.organizer.CopyFrom(echoed_1)
            return response

    async def handle_start_pipeline_workflow(
        self,
        request: pipelines_v1_pipeline_workflow_service_pb2.StartPipelineWorkflowRequest
    ) -> pipelines_v1_pipeline_workflow_service_pb2.StartPipelineWorkflowResponse:
        """Starts a pipeline."""
        deps = self.deps
        response = pipelines_v1_pipeline_workflow_service_pb2.StartPipelineWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('StartPipelineWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'StartPipelineWorkflow', {'reason': request.reason})
            await deps.repository.save_pipeline(request.context.tenant_id, request.pipeline)
            response_0 = pipelines_v1_pipeline_service_pb2.ListPipelinesResponse()
            response_1 = featurestore_v1_feature_view_sync_service_pb2.SyncFeatureViewsResponse()
            fields_0: dict[str, Any] = {
                'context': request.context,
                'filter': {'owner_id': request.pipeline.organizer.user_id, 'region': request.pipeline.location.region}
            }
            outgoing_0 = pipelines_v1_pipeline_service_pb2.ListPipelinesRequest(**fields_0)
            response_0 = await deps.clients.pipelines_pipeline.ListPipelines(outgoing_0, timeout=deps.settings.timeout)
            for item_1 in request.pipeline.participants:
                outgoing_1 = featurestore_v1_feature_view_sync_service_pb2.SyncFeatureViewsRequest(
                    context=request.context,
                    feature_view=featurestore_v1_featurestore_pb2.FeatureView(
                        address=common_v1_address_pb2.PostalAddress(
                            country_code=request.pipeline.location.country_code,
                            locality=request.pipeline.location.locality
                        ),
                        owner=identity_v1_refs_pb2.UserRef(email=item_1.contact.email)
                    )
                )
                response_1 = await deps.clients.featurestore_feature_view_sync.SyncFeatureViews(
                    outgoing_1,
                    timeout=deps.settings.timeout
                )
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.outcome.message = returned_0_0
            echoed_0 = request.pipeline_id
            response.pipeline.pipeline_id = echoed_0
            echoed_1 = request.pipeline.location
            response.pipeline.location.CopyFrom(echoed_1)
            return response
