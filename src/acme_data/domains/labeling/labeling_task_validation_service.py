"""Checks labeling tasks against the rules before anything acts on them."""

from __future__ import annotations

from collections.abc import AsyncIterator
from collections.abc import Awaitable
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any
from typing import cast
import asyncio
import logging

from google.protobuf.any_pb2 import Any as AnyMessage
from google.protobuf.json_format import MessageToDict
from google.protobuf.json_format import MessageToJson
from google.protobuf.json_format import Parse
from google.protobuf.json_format import ParseDict
import grpc

from acme.anomalies.v1 import anomalies_pb2 as anomalies_v1_anomalies_pb2
from acme.anomalies.v1 import detector_validation_service_pb2 as anomalies_v1_detector_validation_service_pb2
from acme.audit.v1 import audit_event_query_service_pb2 as audit_v1_audit_event_query_service_pb2
from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.documents.v1 import document_query_service_pb2 as documents_v1_document_query_service_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.identity.v1 import user_service_pb2 as identity_v1_user_service_pb2
from acme.labeling.v1 import annotation_calculation_service_pb2 as labeling_v1_annotation_calculation_service_pb2
from acme.labeling.v1 import labeling_pb2 as labeling_v1_labeling_pb2
from acme.labeling.v1 import labeling_task_calculation_service_pb2 as labeling_v1_labeling_task_calculation_service_pb2
from acme.labeling.v1 import labeling_task_validation_service_pb2 as labeling_v1_labeling_task_validation_service_pb2
from acme.labeling.v1 import (
    labeling_task_validation_service_pb2_grpc as labeling_v1_labeling_task_validation_service_pb2_grpc,
)
from acme.labeling.v1 import refs_pb2 as labeling_v1_refs_pb2
from acme.lineage.v1 import impact_validation_service_pb2 as lineage_v1_impact_validation_service_pb2
from acme.lineage.v1 import lineage_edge_query_service_pb2 as lineage_v1_lineage_edge_query_service_pb2
from acme.lineage.v1 import lineage_pb2 as lineage_v1_lineage_pb2
from acme.modelregistry.v1 import modelregistry_pb2 as modelregistry_v1_modelregistry_pb2
from acme.modelregistry.v1 import (
    registered_model_calculation_service_pb2 as modelregistry_v1_registered_model_calculation_service_pb2,
)
from acme.prescriptions.v1 import prescription_query_service_pb2 as prescriptions_v1_prescription_query_service_pb2
from acme.search.v1 import search_index_validation_service_pb2 as search_v1_search_index_validation_service_pb2
from acme.search.v1 import search_pb2 as search_v1_search_pb2

from acme_data.domains.labeling import hooks
from acme_data.domains.labeling.adapters import LabelingTaskValidationLintLabelingTasks0Adapter
from acme_data.domains.labeling.dependencies import Dependencies
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


@dataclass(slots=True)
class LabelingTaskValidationServicer(
    labeling_v1_labeling_task_validation_service_pb2_grpc.LabelingTaskValidationServiceServicer
):
    deps: Dependencies

    @rpc_errors
    async def CheckLabelingTaskEligibility(
        self, request: labeling_v1_labeling_task_validation_service_pb2.CheckLabelingTaskEligibilityRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_labeling_task_validation_service_pb2.CheckLabelingTaskEligibilityResponse:
        """Checks a labeling task."""
        return await self.handle_check_labeling_task_eligibility(request)

    @rpc_errors
    async def ExplainLabelingTaskDecision(
        self, request: labeling_v1_labeling_task_validation_service_pb2.ExplainLabelingTaskDecisionRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_labeling_task_validation_service_pb2.ExplainLabelingTaskDecisionResponse:
        """Explains a labeling task."""
        return await self.handle_explain_labeling_task_decision(request)

    @rpc_errors
    @retry_transient
    async def GetLabelingTaskRules(
        self, request: labeling_v1_labeling_task_validation_service_pb2.GetLabelingTaskRulesRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_labeling_task_validation_service_pb2.GetLabelingTaskRulesResponse:
        """Returns a labeling task."""
        return await self.handle_get_labeling_task_rules(request)

    @rpc_errors
    async def LintLabelingTasks(
        self, request: labeling_v1_labeling_task_validation_service_pb2.LintLabelingTasksRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_labeling_task_validation_service_pb2.LintLabelingTasksResponse:
        """Lints a labeling task."""
        return await self.handle_lint_labeling_tasks(request)

    @rpc_errors
    async def NormalizeLabelingTask(
        self, request: labeling_v1_labeling_task_validation_service_pb2.NormalizeLabelingTaskRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_labeling_task_validation_service_pb2.NormalizeLabelingTaskResponse:
        """Normalizes a labeling task."""
        return await self.handle_normalize_labeling_task(request)

    @rpc_errors
    async def PreviewLabelingTask(
        self, request: labeling_v1_labeling_task_validation_service_pb2.PreviewLabelingTaskRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_labeling_task_validation_service_pb2.PreviewLabelingTaskResponse:
        """Previews a labeling task."""
        return await self.handle_preview_labeling_task(request)

    @rpc_errors
    async def ValidateLabelingTask(
        self, request: labeling_v1_labeling_task_validation_service_pb2.ValidateLabelingTaskRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_labeling_task_validation_service_pb2.ValidateLabelingTaskResponse:
        """Validates a labeling task."""
        return await self.handle_validate_labeling_task(request)

    async def handle_check_labeling_task_eligibility(
        self,
        request: labeling_v1_labeling_task_validation_service_pb2.CheckLabelingTaskEligibilityRequest
    ) -> labeling_v1_labeling_task_validation_service_pb2.CheckLabelingTaskEligibilityResponse:
        """Checks a labeling task."""
        deps = self.deps
        response = labeling_v1_labeling_task_validation_service_pb2.CheckLabelingTaskEligibilityResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CheckLabelingTaskEligibility', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'CheckLabelingTaskEligibility',
                {'reason': request.reason}
            )
            await deps.repository.save_labeling_task(request.context.tenant_id, request.labeling_task)
            response_0 = labeling_v1_annotation_calculation_service_pb2.ExplainAnnotationCalculationResponse()
            response_1 = identity_v1_user_service_pb2.WatchUsersResponse()
            response_2 = audit_v1_audit_event_query_service_pb2.ResolveAuditEventsResponse()
            outgoing_0 = labeling_v1_annotation_calculation_service_pb2.ExplainAnnotationCalculationRequest()
            outgoing_0.context.CopyFrom(request.context)
            if request.labeling_task.WhichOneof('origin') == 'customer':
                outgoing_0.annotation.subject.display_name = request.labeling_task.customer.display_name
            outgoing_0.details.contact.email = request.labeling_task.assignee.email
            response_0 = await deps.clients.labeling_annotation_calculation.ExplainAnnotationCalculation(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = identity_v1_user_service_pb2.WatchUsersRequest(
                context=request.context,
                subscriber=common_v1_contact_pb2.ContactInfo(
                    name=request.labeling_task.requester.name,
                    phone=request.details.contact.phone
                )
            )
            async for chunk_1 in deps.clients.identity_user.WatchUsers(outgoing_1, timeout=deps.settings.timeout):
                response_1 = chunk_1
            outgoing_2 = audit_v1_audit_event_query_service_pb2.ResolveAuditEventsRequest(context=request.context)
            response_2 = await hooks.labeling_task_validation_check_labeling_task_eligibility2(
                deps.clients.audit_audit_event_query,
                outgoing_2,
                deps.settings.timeout
            )
            returned_0_0 = response_0.outcome.reference_id
            if returned_0_0:
                response.outcome.reference_id = returned_0_0
            returned_0_1 = response_0.result.message
            if returned_0_1:
                response.result.message = returned_0_1
            returned_2_0 = response_2.result.status
            if returned_2_0:
                response.result.status = returned_2_0
            echoed_0 = request.labeling_task_id
            response.labeling_task.labeling_task_id = echoed_0
            echoed_1 = request.labeling_task.requester
            response.labeling_task.requester.CopyFrom(echoed_1)
            return response

    async def handle_explain_labeling_task_decision(
        self,
        request: labeling_v1_labeling_task_validation_service_pb2.ExplainLabelingTaskDecisionRequest
    ) -> labeling_v1_labeling_task_validation_service_pb2.ExplainLabelingTaskDecisionResponse:
        """Explains a labeling task."""
        deps = self.deps
        response = labeling_v1_labeling_task_validation_service_pb2.ExplainLabelingTaskDecisionResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ExplainLabelingTaskDecision', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ExplainLabelingTaskDecision',
                {'reason': request.reason}
            )
            await deps.repository.save_labeling_task(request.context.tenant_id, request.labeling_task)
            response_0 = labeling_v1_annotation_calculation_service_pb2.EstimateAnnotationResponse()
            response_1 = anomalies_v1_detector_validation_service_pb2.LintDetectorsResponse()
            callbacks_0: list[
                Callable[[], Awaitable[labeling_v1_annotation_calculation_service_pb2.EstimateAnnotationResponse]]
            ] = []
            for item_0 in request.labeling_task.history:
                outgoing_0 = labeling_v1_annotation_calculation_service_pb2.EstimateAnnotationRequest(
                    annotation=labeling_v1_labeling_pb2.Annotation(
                        occurred_at=item_0.changed_at,
                        subject=labeling_v1_refs_pb2.LabelingTaskRef(
                            display_name=request.labeling_task.customer.display_name,
                            labeling_task_id=request.labeling_task.labeling_task_id,
                            priority=request.labeling_task.priority
                        )
                    ),
                    context=request.context
                )
                async def send_0(
                    payload: labeling_v1_annotation_calculation_service_pb2.EstimateAnnotationRequest = outgoing_0
                ) -> labeling_v1_annotation_calculation_service_pb2.EstimateAnnotationResponse:
                    return await deps.clients.labeling_annotation_calculation.EstimateAnnotation(
                        payload,
                        timeout=deps.settings.timeout
                    )
                callbacks_0.append(send_0)
            for callback_0 in callbacks_0:
                response_0 = await callback_0()
            async for item_1 in async_messages(request.labeling_task.comments):
                outgoing_1 = anomalies_v1_detector_validation_service_pb2.LintDetectorsRequest(
                    context=request.context,
                    detector=anomalies_v1_anomalies_pb2.Detector(
                        audit=common_v1_audit_pb2.AuditInfo(created_at=item_1.created_at),
                        owner=identity_v1_refs_pb2.UserRef(email=item_1.author_email)
                    )
                )
                response_1 = await deps.clients.anomalies_detector_validation.LintDetectors(
                    outgoing_1,
                    timeout=deps.settings.timeout
                )
            echoed_0 = request.labeling_task_id
            response.labeling_task.labeling_task_id = echoed_0
            echoed_1 = request.labeling_task.subject
            response.labeling_task.subject = echoed_1
            return response

    async def handle_get_labeling_task_rules(
        self,
        request: labeling_v1_labeling_task_validation_service_pb2.GetLabelingTaskRulesRequest
    ) -> labeling_v1_labeling_task_validation_service_pb2.GetLabelingTaskRulesResponse:
        """Returns a labeling task."""
        deps = self.deps
        response = labeling_v1_labeling_task_validation_service_pb2.GetLabelingTaskRulesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('GetLabelingTaskRules', extra={'fields': {'domain': 'labeling'}})
            await deps.repository.audit(request.context.tenant_id, 'GetLabelingTaskRules', {})
            response_0 = prescriptions_v1_prescription_query_service_pb2.ResolvePrescriptionsResponse()
            outgoing_0 = prescriptions_v1_prescription_query_service_pb2.ResolvePrescriptionsRequest(
                context=request.context
            )
            response_0 = await deps.clients.prescriptions_prescription_query.ResolvePrescriptions(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.correlation_id
            if returned_0_0:
                response.result.correlation_id = returned_0_0
            echoed_0 = request.labeling_task_id
            response.labeling_task.labeling_task_id = echoed_0
            return response

    async def handle_lint_labeling_tasks(
        self,
        request: labeling_v1_labeling_task_validation_service_pb2.LintLabelingTasksRequest
    ) -> labeling_v1_labeling_task_validation_service_pb2.LintLabelingTasksResponse:
        """Lints a labeling task."""
        deps = self.deps
        response = labeling_v1_labeling_task_validation_service_pb2.LintLabelingTasksResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('LintLabelingTasks', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'LintLabelingTasks', {'reason': request.reason})
            await deps.repository.save_labeling_task(request.context.tenant_id, request.labeling_task)
            response_0 = audit_v1_audit_event_query_service_pb2.SuggestAuditEventsResponse()
            outgoing_0 = audit_v1_audit_event_query_service_pb2.SuggestAuditEventsRequest(
                context=request.context,
                filter=audit_v1_audit_event_query_service_pb2.SuggestAuditEventsRequest.Filter(
                    created_after=request.labeling_task.audit.updated_at
                )
            )
            response_0 = await LabelingTaskValidationLintLabelingTasks0Adapter(
                deps.clients.audit_audit_event_query,
                deps.settings.timeout
            )(outgoing_0)
            returned_0_0 = response_0.result.correlation_id
            if returned_0_0:
                response.result.correlation_id = returned_0_0
            returned_0_1 = response_0.result.message
            if returned_0_1:
                response.outcome.message = returned_0_1
            echoed_0 = request.labeling_task_id
            response.labeling_task.labeling_task_id = echoed_0
            echoed_1 = request.labeling_task.requester
            response.labeling_task.requester.CopyFrom(echoed_1)
            return response

    async def handle_normalize_labeling_task(
        self,
        request: labeling_v1_labeling_task_validation_service_pb2.NormalizeLabelingTaskRequest
    ) -> labeling_v1_labeling_task_validation_service_pb2.NormalizeLabelingTaskResponse:
        """Normalizes a labeling task."""
        deps = self.deps
        response = labeling_v1_labeling_task_validation_service_pb2.NormalizeLabelingTaskResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('NormalizeLabelingTask', extra={'fields': {'locale': request.details.locale}})
            await deps.repository.audit(
                request.context.tenant_id,
                'NormalizeLabelingTask',
                {'locale': request.details.locale}
            )
            await deps.repository.save_labeling_task(request.context.tenant_id, request.labeling_task)
            response_0 = lineage_v1_impact_validation_service_pb2.NormalizeImpactResponse()
            response_1 = audit_v1_audit_event_query_service_pb2.FindAuditEventsResponse()
            response_2 = documents_v1_document_query_service_pb2.SummarizeDocumentsResponse()
            outgoing_1 = audit_v1_audit_event_query_service_pb2.FindAuditEventsRequest(
                context=request.context,
                filter=audit_v1_audit_event_query_service_pb2.FindAuditEventsRequest.Filter(
                    created_after=request.labeling_task.audit.created_at
                )
            )
            outgoing_2 = documents_v1_document_query_service_pb2.SummarizeDocumentsRequest(
                annotations=dict(request.annotations),
                context=request.context,
                details=documents_v1_document_query_service_pb2.SummarizeDocumentsRequest.Details(
                    filters=dict(request.labeling_task.custom_fields)
                ),
                reason=request.reason
            )
            response_1, response_2 = await asyncio.gather(
                deps.clients.audit_audit_event_query.FindAuditEvents(outgoing_1, timeout=deps.settings.timeout),
                deps.clients.documents_document_query.SummarizeDocuments(outgoing_2, timeout=deps.settings.timeout),
            )
            outgoing_0 = lineage_v1_impact_validation_service_pb2.NormalizeImpactRequest(
                context=request.context,
                details=lineage_v1_impact_validation_service_pb2.NormalizeImpactRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(name=request.details.contact.name)
                ),
                impact=lineage_v1_lineage_pb2.Impact(
                    sla=lineage_v1_lineage_pb2.ImpactSla(paused_for=request.labeling_task.sla.paused_for)
                )
            )
            response_0 = cast(lineage_v1_impact_validation_service_pb2.NormalizeImpactResponse, await deps.bus.request(
                'acme.labeling.v1.LabelingTaskValidationService/NormalizeLabelingTask/0', outgoing_0, deps.settings.timeout,
            ))
            returned_0_0 = response_0.impact.sla.due_at
            if returned_0_0.ListFields():
                response.labeling_task.sla.due_at.MergeFrom(returned_0_0)
            returned_1_0 = response_1.result.message
            if returned_1_0:
                response.result.message = returned_1_0
            returned_2_0 = response_2.result.details
            response.result.details.update(returned_2_0)
            echoed_0 = request.labeling_task_id
            response.labeling_task.labeling_task_id = echoed_0
            echoed_1 = request.labeling_task.status
            response.labeling_task.status = echoed_1
            return response

    async def handle_preview_labeling_task(
        self,
        request: labeling_v1_labeling_task_validation_service_pb2.PreviewLabelingTaskRequest
    ) -> labeling_v1_labeling_task_validation_service_pb2.PreviewLabelingTaskResponse:
        """Previews a labeling task."""
        deps = self.deps
        response = labeling_v1_labeling_task_validation_service_pb2.PreviewLabelingTaskResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('PreviewLabelingTask', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'PreviewLabelingTask', {'reason': request.reason})
            await deps.repository.save_labeling_task(request.context.tenant_id, request.labeling_task)
            response_0 = modelregistry_v1_registered_model_calculation_service_pb2.ExplainRegisteredModelCalculationResponse()
            response_1 = search_v1_search_index_validation_service_pb2.ValidateSearchIndexResponse()
            response_2 = lineage_v1_lineage_edge_query_service_pb2.ResolveLineageEdgesResponse()
            fields_0: dict[str, Any] = {
                'context': request.context,
                'details': {'contact': {'name': request.details.contact.name}},
                'registered_model': {
                    'audit': {'updated_at': request.labeling_task.audit.updated_at},
                    'owner': {'email': request.labeling_task.requester.email}
                }
            }
            outgoing_0 = modelregistry_v1_registered_model_calculation_service_pb2.ExplainRegisteredModelCalculationRequest(**fields_0)
            response_0 = await deps.clients.modelregistry_registered_model_calculation.ExplainRegisteredModelCalculation(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = search_v1_search_index_validation_service_pb2.ValidateSearchIndexRequest(
                context=request.context,
                search_index=search_v1_search_pb2.SearchIndex(
                    address=common_v1_address_pb2.PostalAddress(
                        country_code=response_0.registered_model.address.country_code
                    ),
                    audit=common_v1_audit_pb2.AuditInfo(created_by=response_0.registered_model.audit.created_by),
                    components={
                        'primary': search_v1_search_pb2.SearchIndexComponent(
                            description=response_0.registered_model.components.get(
                                'primary',
                                modelregistry_v1_modelregistry_pb2.RegisteredModelComponent()
                            ).description
                        )
                    }
                )
            )
            document_1 = MessageToDict(outgoing_1, preserving_proto_field_name=True)
            outgoing_1 = ParseDict(
                document_1,
                search_v1_search_index_validation_service_pb2.ValidateSearchIndexRequest()
            )
            response_1 = await deps.clients.search_search_index_validation.ValidateSearchIndex(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = lineage_v1_lineage_edge_query_service_pb2.ResolveLineageEdgesRequest(context=request.context)
            document_2 = MessageToJson(outgoing_2, preserving_proto_field_name=True)
            outgoing_2 = Parse(document_2, lineage_v1_lineage_edge_query_service_pb2.ResolveLineageEdgesRequest())
            response_2 = await deps.clients.lineage_lineage_edge_query.ResolveLineageEdges(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.correlation_id
            if returned_0_0:
                response.result.correlation_id = returned_0_0
            returned_1_0 = response_1.search_index.owner.user_id
            if returned_1_0:
                response.labeling_task.assignee.user_id = returned_1_0
            returned_2_0 = response_2.result.message
            if returned_2_0:
                response.outcome.message = returned_2_0
            echoed_0 = request.labeling_task_id
            response.labeling_task.labeling_task_id = echoed_0
            echoed_1 = request.labeling_task.status
            response.labeling_task.status = echoed_1
            return response

    async def handle_validate_labeling_task(
        self,
        request: labeling_v1_labeling_task_validation_service_pb2.ValidateLabelingTaskRequest
    ) -> labeling_v1_labeling_task_validation_service_pb2.ValidateLabelingTaskResponse:
        """Validates a labeling task."""
        deps = self.deps
        response = labeling_v1_labeling_task_validation_service_pb2.ValidateLabelingTaskResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ValidateLabelingTask', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'ValidateLabelingTask', {'reason': request.reason})
            await deps.repository.save_labeling_task(request.context.tenant_id, request.labeling_task)
            response_0 = lineage_v1_impact_validation_service_pb2.LintImpactsResponse()
            response_1 = labeling_v1_labeling_task_calculation_service_pb2.SimulateLabelingTaskResponse()
            outgoing_0 = lineage_v1_impact_validation_service_pb2.LintImpactsRequest()
            outgoing_0.context.CopyFrom(request.context)
            outgoing_0.impact.customer.email = request.details.contact.email
            outgoing_0.details.contact.preferred_channel = request.labeling_task.requester.preferred_channel
            outgoing_0.impact.requester.phone = request.details.contact.phone
            merged_0 = lineage_v1_impact_validation_service_pb2.LintImpactsRequest()
            merged_0.MergeFrom(outgoing_0)
            outgoing_0.CopyFrom(merged_0)
            response_0 = await deps.clients.lineage_impact_validation.LintImpacts(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = labeling_v1_labeling_task_calculation_service_pb2.SimulateLabelingTaskRequest(
                context=request.context,
                labeling_task=labeling_v1_labeling_pb2.LabelingTask(
                    assignee=identity_v1_refs_pb2.UserRef(email=response_0.impact.assignee.email),
                    audit=common_v1_audit_pb2.AuditInfo(updated_by=request.labeling_task.audit.updated_by),
                    customer=labeling_v1_refs_pb2.LabelSetRef(display_name=request.labeling_task.customer.display_name),
                    requester=common_v1_contact_pb2.ContactInfo(name=request.labeling_task.requester.name)
                )
            )
            envelope_1 = AnyMessage()
            envelope_1.Pack(outgoing_1)
            outgoing_1 = labeling_v1_labeling_task_calculation_service_pb2.SimulateLabelingTaskRequest()
            if not envelope_1.Unpack(outgoing_1):
                raise ValueError("partner envelope contains the wrong request type")
            response_1 = await deps.clients.labeling_labeling_task_calculation.SimulateLabelingTask(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.impact.customer.email
            if returned_0_0:
                response.labeling_task.requester.email = returned_0_0
            returned_0_1 = response_0.impact.requester.name
            if returned_0_1.ListFields():
                response.labeling_task.requester.name.MergeFrom(returned_0_1)
            returned_1_0 = response_1.labeling_task.requester.name
            if returned_1_0.ListFields():
                response.labeling_task.requester.name.MergeFrom(returned_1_0)
            echoed_0 = request.labeling_task_id
            response.labeling_task.labeling_task_id = echoed_0
            echoed_1 = request.labeling_task.assignee
            response.labeling_task.assignee.CopyFrom(echoed_1)
            return response
