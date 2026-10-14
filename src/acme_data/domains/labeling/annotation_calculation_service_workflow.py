"""Application workflow for Annotation Calculation."""

from __future__ import annotations

from collections.abc import Awaitable
from collections.abc import Callable
from typing import Any
from typing import cast
import asyncio
import logging

from google.protobuf.any_pb2 import Any as AnyMessage
from google.protobuf.json_format import MessageToJson
from google.protobuf.json_format import Parse

from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.labeling.v1 import annotation_calculation_service_pb2 as labeling_v1_annotation_calculation_service_pb2
from acme.labeling.v1 import labeling_pb2 as labeling_v1_labeling_pb2
from acme.labeling.v1 import labeling_task_calculation_service_pb2 as labeling_v1_labeling_task_calculation_service_pb2
from acme.labeling.v1 import (
    labeling_task_calculation_service_pb2_grpc as labeling_v1_labeling_task_calculation_service_pb2_grpc,
)
from acme.labeling.v1 import refs_pb2 as labeling_v1_refs_pb2
from acme.metrics.v1 import metric_series_notification_service_pb2 as metrics_v1_metric_series_notification_service_pb2
from acme.patients.v1 import patient_service_pb2 as patients_v1_patient_service_pb2
from acme.patients.v1 import patients_pb2 as patients_v1_patients_pb2
from acme.prescriptions.v1 import prescription_query_service_pb2 as prescriptions_v1_prescription_query_service_pb2
from acme.search.v1 import search_index_validation_service_pb2 as search_v1_search_index_validation_service_pb2
from acme.search.v1 import search_pb2 as search_v1_search_pb2
from acme.sponsorships.v1 import sponsor_service_pb2 as sponsorships_v1_sponsor_service_pb2

from acme_data.domains.labeling.adapters import AnnotationCalculationExplainAnnotationCalculation0Adapter
from acme_data.domains.labeling.adapters import AnnotationCalculationExplainAnnotationCalculation0Port
from acme_data.domains.labeling.adapters import AnnotationCalculationExplainAnnotationCalculation2Adapter
from acme_data.domains.labeling.dependencies import Dependencies
from acme_data.domains.labeling.models import AnnotationCalculationCompareAnnotationOptions3Command
from acme_data.domains.labeling.models import to_annotation_calculation_compare_annotation_options3_command
from acme_data.platform.rpc import async_messages
from acme_data.platform.tenancy import tenant_id
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class AnnotationCalculationServicerWorkflow:
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    async def handle_calculate_annotation(
        self,
        request: labeling_v1_annotation_calculation_service_pb2.CalculateAnnotationRequest
    ) -> labeling_v1_annotation_calculation_service_pb2.CalculateAnnotationResponse:
        """Calculates an annotation."""
        deps = self.deps
        response = labeling_v1_annotation_calculation_service_pb2.CalculateAnnotationResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CalculateAnnotation', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'CalculateAnnotation', {'reason': request.reason})
            await deps.repository.save_annotation(request.context.tenant_id, request.annotation)
            response_0 = prescriptions_v1_prescription_query_service_pb2.CountPrescriptionsResponse()
            response_1 = labeling_v1_labeling_task_calculation_service_pb2.CalculateLabelingTaskResponse()
            outgoing_0 = prescriptions_v1_prescription_query_service_pb2.CountPrescriptionsRequest(
                context=request.context,
                filter=prescriptions_v1_prescription_query_service_pb2.CountPrescriptionsRequest.Filter(
                    region=request.details.destination.region
                )
            )
            document_0 = MessageToJson(outgoing_0, preserving_proto_field_name=True)
            outgoing_0 = Parse(document_0, prescriptions_v1_prescription_query_service_pb2.CountPrescriptionsRequest())
            response_0 = await deps.clients.prescriptions_prescription_query.CountPrescriptions(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            for item_1 in request.annotation.measurements:
                outgoing_1 = labeling_v1_labeling_task_calculation_service_pb2.CalculateLabelingTaskRequest(
                    context=request.context,
                    details=labeling_v1_labeling_task_calculation_service_pb2.CalculateLabelingTaskRequest.Details(
                        destination=common_v1_address_pb2.PostalAddress(locality=request.details.destination.locality),
                        include_breakdown=request.details.include_breakdown
                    ),
                    labeling_task=labeling_v1_labeling_pb2.LabelingTask(
                        audit=common_v1_audit_pb2.AuditInfo(created_at=item_1.observed_at),
                        customer=labeling_v1_refs_pb2.LabelSetRef(display_name=request.annotation.subject.display_name)
                    )
                )
                response_1 = await deps.clients.labeling_labeling_task_calculation.CalculateLabelingTask(
                    outgoing_1,
                    timeout=deps.settings.timeout
                )
            returned_0_0 = response_0.result.details
            response.result.details.update(returned_0_0)
            returned_0_1 = response_0.result.correlation_id
            if returned_0_1:
                response.annotation.correlation_id = returned_0_1
            echoed_0 = request.annotation_id
            response.annotation.annotation_id = echoed_0
            echoed_1 = request.annotation.correlation_id
            response.result.correlation_id = echoed_1
            return response

    async def handle_compare_annotation_options(
        self,
        request: labeling_v1_annotation_calculation_service_pb2.CompareAnnotationOptionsRequest
    ) -> labeling_v1_annotation_calculation_service_pb2.CompareAnnotationOptionsResponse:
        """Compares an annotation."""
        deps = self.deps
        response = labeling_v1_annotation_calculation_service_pb2.CompareAnnotationOptionsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CompareAnnotationOptions', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'CompareAnnotationOptions',
                {'reason': request.reason}
            )
            await deps.repository.save_annotation(request.context.tenant_id, request.annotation)
            response_0 = patients_v1_patient_service_pb2.ClonePatientResponse()
            response_1 = labeling_v1_labeling_task_calculation_service_pb2.RecalculateLabelingTasksResponse()
            response_2 = labeling_v1_labeling_task_calculation_service_pb2.ExplainLabelingTaskCalculationResponse()
            response_3 = sponsorships_v1_sponsor_service_pb2.CloneSponsorResponse()
            outgoing_0 = patients_v1_patient_service_pb2.ClonePatientRequest(
                context=request.context,
                patient=patients_v1_patients_pb2.Patient(
                    primary_address=common_v1_address_pb2.PostalAddress(
                        country_code=request.details.destination.country_code,
                        lines=list(request.details.destination.lines),
                        postal_code=request.details.destination.postal_code,
                        recipient=request.details.destination.recipient
                    )
                )
            )
            envelope_0 = AnyMessage()
            envelope_0.Pack(outgoing_0)
            outgoing_0 = patients_v1_patient_service_pb2.ClonePatientRequest()
            if not envelope_0.Unpack(outgoing_0):
                raise ValueError("partner envelope contains the wrong request type")
            response_0 = await deps.clients.patients_patient.ClonePatient(outgoing_0, timeout=deps.settings.timeout)
            outgoing_1 = labeling_v1_labeling_task_calculation_service_pb2.RecalculateLabelingTasksRequest(
                context=request.context,
                details=labeling_v1_labeling_task_calculation_service_pb2.RecalculateLabelingTasksRequest.Details(
                    destination=common_v1_address_pb2.PostalAddress(
                        postal_code=request.details.destination.postal_code,
                        recipient=response_0.patient.primary_address.recipient
                    )
                ),
                labeling_task=labeling_v1_labeling_pb2.LabelingTask(
                    requester=common_v1_contact_pb2.ContactInfo(phone=response_0.patient.contact.phone)
                )
            )
            registered_1 = cast(
                labeling_v1_labeling_task_calculation_service_pb2_grpc.LabelingTaskCalculationServiceStub,
                deps.clients.registry['acme.labeling.v1.LabelingTaskCalculationService']
            )
            response_1 = await registered_1.RecalculateLabelingTasks(outgoing_1, timeout=deps.settings.timeout)
            requests_2: list[
                labeling_v1_labeling_task_calculation_service_pb2.ExplainLabelingTaskCalculationRequest
            ] = []
            for item_2 in request.annotation.measurements:
                outgoing_2 = labeling_v1_labeling_task_calculation_service_pb2.ExplainLabelingTaskCalculationRequest(
                    context=request.context,
                    labeling_task=labeling_v1_labeling_pb2.LabelingTask(
                        audit=common_v1_audit_pb2.AuditInfo(updated_at=item_2.observed_at)
                    )
                )
                requests_2.append(outgoing_2)
            replies_2 = await asyncio.gather(*(
                deps.clients.labeling_labeling_task_calculation.ExplainLabelingTaskCalculation(
                    entry,
                    timeout=deps.settings.timeout
                ) for entry in requests_2
            ))
            if replies_2:
                response_2 = replies_2[-1]
            command_3 = AnnotationCalculationCompareAnnotationOptions3Command.model_validate(
                {
                    'context': request.context,
                    'sponsor_passport_issuing_country': response_0.patient.national_id.issuing_country,
                    'sponsor_contact_email': response_1.labeling_task.requester.email,
                    'sponsor_relationship_manager_user_id': response_1.labeling_task.assignee.user_id,
                    'sponsor_audit_updated_at': response_0.patient.audit.updated_at
                }
            )
            outgoing_3 = to_annotation_calculation_compare_annotation_options3_command(command_3)
            response_3 = await deps.clients.sponsorships_sponsor.CloneSponsor(outgoing_3, timeout=deps.settings.timeout)
            returned_0_0 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_0)
            returned_0_1 = response_0.result.correlation_id
            if returned_0_1:
                response.result.correlation_id = returned_0_1
            returned_1_0 = response_1.result.message
            if returned_1_0:
                response.result.message = returned_1_0
            returned_3_0 = response_3.result.correlation_id
            if returned_3_0:
                response.result.correlation_id = returned_3_0
            returned_3_1 = response_3.result.status
            if returned_3_1:
                response.result.status = returned_3_1
            echoed_0 = request.annotation_id
            response.annotation.annotation_id = echoed_0
            echoed_1 = request.details.currency_code
            response.breakdown.currency_code = echoed_1
            return response

    async def handle_estimate_annotation(
        self,
        request: labeling_v1_annotation_calculation_service_pb2.EstimateAnnotationRequest
    ) -> labeling_v1_annotation_calculation_service_pb2.EstimateAnnotationResponse:
        """Estimates an annotation."""
        deps = self.deps
        response = labeling_v1_annotation_calculation_service_pb2.EstimateAnnotationResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('EstimateAnnotation', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'EstimateAnnotation', {'reason': request.reason})
            await deps.repository.save_annotation(request.context.tenant_id, request.annotation)
            response_0 = labeling_v1_labeling_task_calculation_service_pb2.SimulateLabelingTaskResponse()
            response_1 = metrics_v1_metric_series_notification_service_pb2.StreamMetricSeriesNoticesResponse()
            response_2 = labeling_v1_labeling_task_calculation_service_pb2.QuoteLabelingTaskResponse()
            callbacks_0: list[
                Callable[[], Awaitable[labeling_v1_labeling_task_calculation_service_pb2.SimulateLabelingTaskResponse]]
            ] = []
            for item_0 in request.annotation.measurements:
                outgoing_0 = labeling_v1_labeling_task_calculation_service_pb2.SimulateLabelingTaskRequest(
                    context=request.context,
                    labeling_task=labeling_v1_labeling_pb2.LabelingTask(
                        assignee=identity_v1_refs_pb2.UserRef(display_name=request.annotation.subject.display_name),
                        sla=labeling_v1_labeling_pb2.LabelingTaskSla(due_at=item_0.observed_at)
                    )
                )
                async def send_0(
                    payload: labeling_v1_labeling_task_calculation_service_pb2.SimulateLabelingTaskRequest = outgoing_0
                ) -> labeling_v1_labeling_task_calculation_service_pb2.SimulateLabelingTaskResponse:
                    return await deps.clients.labeling_labeling_task_calculation.SimulateLabelingTask(
                        payload,
                        timeout=deps.settings.timeout
                    )
                callbacks_0.append(send_0)
            for callback_0 in callbacks_0:
                response_0 = await callback_0()
            outgoing_1 = metrics_v1_metric_series_notification_service_pb2.StreamMetricSeriesNoticesRequest(
                context=request.context,
                subscriber=common_v1_contact_pb2.ContactInfo(
                    email=response_0.labeling_task.assignee.email,
                    phone=response_0.labeling_task.requester.phone,
                    preferred_channel=response_0.labeling_task.requester.preferred_channel
                )
            )
            async for chunk_1 in deps.clients.metrics_metric_series_notification.StreamMetricSeriesNotices(
                outgoing_1,
                timeout=deps.settings.timeout
            ):
                response_1 = chunk_1
            outgoing_2 = labeling_v1_labeling_task_calculation_service_pb2.QuoteLabelingTaskRequest()
            outgoing_2.context.CopyFrom(request.context)
            outgoing_2.labeling_task.audit.created_at.CopyFrom(response_0.labeling_task.audit.created_at)
            outgoing_2.labeling_task.assignee.user_id = response_0.labeling_task.assignee.user_id
            outgoing_2.labeling_task.requester.email = response_0.labeling_task.assignee.email
            outgoing_2.labeling_task.requester.preferred_channel = response_0.labeling_task.requester.preferred_channel
            outgoing_2.context.tenant_id = tenant_id.get()
            response_2 = await deps.clients.labeling_labeling_task_calculation.QuoteLabelingTask(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            returned_2_0 = response_2.result.status
            if returned_2_0:
                response.result.status = returned_2_0
            echoed_0 = request.annotation_id
            response.annotation.annotation_id = echoed_0
            echoed_1 = request.annotation.source
            response.annotation.source = echoed_1
            return response

    async def handle_explain_annotation_calculation(
        self,
        request: labeling_v1_annotation_calculation_service_pb2.ExplainAnnotationCalculationRequest
    ) -> labeling_v1_annotation_calculation_service_pb2.ExplainAnnotationCalculationResponse:
        """Explains an annotation."""
        deps = self.deps
        response = labeling_v1_annotation_calculation_service_pb2.ExplainAnnotationCalculationResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ExplainAnnotationCalculation', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ExplainAnnotationCalculation',
                {'reason': request.reason}
            )
            await deps.repository.save_annotation(request.context.tenant_id, request.annotation)
            response_0 = labeling_v1_labeling_task_calculation_service_pb2.QuoteLabelingTaskResponse()
            response_1 = search_v1_search_index_validation_service_pb2.NormalizeSearchIndexResponse()
            response_2 = labeling_v1_labeling_task_calculation_service_pb2.EstimateLabelingTaskResponse()
            outgoing_0 = labeling_v1_labeling_task_calculation_service_pb2.QuoteLabelingTaskRequest(
                context=request.context,
                labeling_task=labeling_v1_labeling_pb2.LabelingTask(
                    customer=labeling_v1_refs_pb2.LabelSetRef(display_name=request.annotation.subject.display_name),
                    labeling_task_id=request.annotation.subject.labeling_task_id,
                    requester=common_v1_contact_pb2.ContactInfo(
                        email=request.details.contact.email,
                        phone=request.details.contact.phone
                    )
                )
            )
            port_0: AnnotationCalculationExplainAnnotationCalculation0Port = AnnotationCalculationExplainAnnotationCalculation0Adapter(
                deps.clients.labeling_labeling_task_calculation,
                deps.settings.timeout
            )
            response_0 = await port_0.execute(outgoing_0)
            async for item_1 in async_messages(request.annotation.measurements):
                outgoing_1 = search_v1_search_index_validation_service_pb2.NormalizeSearchIndexRequest(
                    context=request.context,
                    search_index=search_v1_search_pb2.SearchIndex(
                        dimensions=search_v1_search_pb2.SearchIndexDimensions(unit=item_1.unit)
                    )
                )
                response_1 = await deps.clients.search_search_index_validation.NormalizeSearchIndex(
                    outgoing_1,
                    timeout=deps.settings.timeout
                )
            outgoing_2 = labeling_v1_labeling_task_calculation_service_pb2.EstimateLabelingTaskRequest(
                context=request.context,
                labeling_task=labeling_v1_labeling_pb2.LabelingTask(
                    assignee=identity_v1_refs_pb2.UserRef(display_name=response_0.labeling_task.assignee.display_name),
                    audit=common_v1_audit_pb2.AuditInfo(etag=response_0.labeling_task.audit.etag),
                    customer=labeling_v1_refs_pb2.LabelSetRef(
                        display_name=response_1.search_index.owner.display_name,
                        label_set_id=response_0.labeling_task.customer.label_set_id
                    )
                )
            )
            response_2 = await AnnotationCalculationExplainAnnotationCalculation2Adapter(
                deps.clients.labeling_labeling_task_calculation,
                deps.settings.timeout
            )(outgoing_2)
            returned_0_0 = response_0.labeling_task.assignee.display_name
            if returned_0_0:
                response.annotation.subject.display_name = returned_0_0
            returned_0_1 = response_0.result.message
            if returned_0_1:
                response.outcome.message = returned_0_1
            returned_2_0 = response_2.result.correlation_id
            if returned_2_0:
                response.result.correlation_id = returned_2_0
            returned_2_1 = response_2.result.status
            if returned_2_1:
                response.result.status = returned_2_1
            echoed_0 = request.annotation_id
            response.annotation.annotation_id = echoed_0
            echoed_1 = request.annotation.occurred_at
            response.annotation.occurred_at.CopyFrom(echoed_1)
            return response

    async def handle_recalculate_annotations(
        self,
        request: labeling_v1_annotation_calculation_service_pb2.RecalculateAnnotationsRequest
    ) -> labeling_v1_annotation_calculation_service_pb2.RecalculateAnnotationsResponse:
        """Recalculates an annotation."""
        deps = self.deps
        response = labeling_v1_annotation_calculation_service_pb2.RecalculateAnnotationsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('RecalculateAnnotations', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'RecalculateAnnotations', {'reason': request.reason})
            await deps.repository.save_annotation(request.context.tenant_id, request.annotation)
            response_0 = labeling_v1_labeling_task_calculation_service_pb2.CompareLabelingTaskOptionsResponse()
            response_1 = labeling_v1_labeling_task_calculation_service_pb2.GetLabelingTaskRatesResponse()
            outgoing_0 = labeling_v1_labeling_task_calculation_service_pb2.CompareLabelingTaskOptionsRequest(
                context=request.context,
                details=labeling_v1_labeling_task_calculation_service_pb2.CompareLabelingTaskOptionsRequest.Details(
                    destination=common_v1_address_pb2.PostalAddress(
                        locality=request.details.destination.locality,
                        region=request.details.destination.region
                    )
                ),
                labeling_task=labeling_v1_labeling_pb2.LabelingTask(
                    customer=labeling_v1_refs_pb2.LabelSetRef(display_name=request.annotation.subject.display_name)
                )
            )
            response_0 = cast(labeling_v1_labeling_task_calculation_service_pb2.CompareLabelingTaskOptionsResponse, await deps.bus.request(
                'acme.labeling.v1.AnnotationCalculationService/RecalculateAnnotations/0', outgoing_0, deps.settings.timeout,
            ))
            outgoing_1 = labeling_v1_labeling_task_calculation_service_pb2.GetLabelingTaskRatesRequest(
                context=request.context,
                labeling_task_id=request.annotation.subject.labeling_task_id
            )
            response_1 = await deps.clients.labeling_labeling_task_calculation.GetLabelingTaskRates(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.labeling_task.labeling_task_id
            if returned_0_0:
                response.annotation.subject.labeling_task_id = returned_0_0
            returned_0_1 = response_0.result.correlation_id
            if returned_0_1:
                response.annotation.correlation_id = returned_0_1
            returned_1_0 = response_1.result.status
            if returned_1_0:
                response.result.status = returned_1_0
            returned_1_1 = response_1.labeling_task.priority
            if returned_1_1:
                response.annotation.subject.priority = returned_1_1
            echoed_0 = request.annotation_id
            response.annotation.annotation_id = echoed_0
            echoed_1 = request.annotation.correlation_id
            response.result.correlation_id = echoed_1
            return response

    async def handle_simulate_annotation(
        self,
        request: labeling_v1_annotation_calculation_service_pb2.SimulateAnnotationRequest
    ) -> labeling_v1_annotation_calculation_service_pb2.SimulateAnnotationResponse:
        """Simulates an annotation."""
        deps = self.deps
        response = labeling_v1_annotation_calculation_service_pb2.SimulateAnnotationResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SimulateAnnotation', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'SimulateAnnotation', {'reason': request.reason})
            await deps.repository.save_annotation(request.context.tenant_id, request.annotation)
            response_0 = labeling_v1_labeling_task_calculation_service_pb2.CompareLabelingTaskOptionsResponse()
            response_1 = labeling_v1_labeling_task_calculation_service_pb2.GetLabelingTaskRatesResponse()
            for item_0 in request.annotation.measurements:
                outgoing_0 = labeling_v1_labeling_task_calculation_service_pb2.CompareLabelingTaskOptionsRequest(
                    context=request.context,
                    details=labeling_v1_labeling_task_calculation_service_pb2.CompareLabelingTaskOptionsRequest.Details(
                        destination=common_v1_address_pb2.PostalAddress(
                            locality=request.details.destination.locality,
                            postal_code=request.details.destination.postal_code,
                            recipient=request.details.destination.recipient
                        )
                    ),
                    labeling_task=labeling_v1_labeling_pb2.LabelingTask(
                        sla=labeling_v1_labeling_pb2.LabelingTaskSla(due_at=item_0.observed_at)
                    )
                )
                response_0 = await deps.clients.labeling_labeling_task_calculation.CompareLabelingTaskOptions(
                    outgoing_0,
                    timeout=deps.settings.timeout
                )
            fields_1: dict[str, Any] = {
                'context': request.context,
                'labeling_task_id': request.annotation.subject.labeling_task_id
            }
            outgoing_1 = labeling_v1_labeling_task_calculation_service_pb2.GetLabelingTaskRatesRequest(**fields_1)
            response_1 = await deps.clients.labeling_labeling_task_calculation.GetLabelingTaskRates(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_1_0 = response_1.labeling_task.priority
            if returned_1_0:
                response.annotation.subject.priority = returned_1_0
            returned_1_1 = response_1.labeling_task.labeling_task_id
            if returned_1_1:
                response.annotation.subject.labeling_task_id = returned_1_1
            echoed_0 = request.annotation_id
            response.annotation.annotation_id = echoed_0
            echoed_1 = request.annotation.occurred_at
            response.annotation.occurred_at.CopyFrom(echoed_1)
            return response
