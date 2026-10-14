"""Reusable transport mixin for LabelSetCalculationService."""

from __future__ import annotations

from collections.abc import AsyncIterator
from functools import partial
from typing import cast
import asyncio
import logging

from google.protobuf.any_pb2 import Any as AnyMessage
from google.protobuf.json_format import MessageToDict
from google.protobuf.json_format import MessageToJson
from google.protobuf.json_format import Parse
from google.protobuf.json_format import ParseDict
import grpc

from acme.anomalies.v1 import detector_validation_service_pb2 as anomalies_v1_detector_validation_service_pb2
from acme.audit.v1 import audit_event_validation_service_pb2 as audit_v1_audit_event_validation_service_pb2
from acme.audit.v1 import audit_pb2 as audit_v1_audit_pb2
from acme.audit.v1 import refs_pb2 as audit_v1_refs_pb2
from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.customers.v1 import refs_pb2 as customers_v1_refs_pb2
from acme.featurestore.v1 import (
    feature_view_validation_service_pb2 as featurestore_v1_feature_view_validation_service_pb2,
)
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.keymanagement.v1 import (
    crypto_key_calculation_service_pb2 as keymanagement_v1_crypto_key_calculation_service_pb2,
)
from acme.labeling.v1 import annotation_calculation_service_pb2 as labeling_v1_annotation_calculation_service_pb2
from acme.labeling.v1 import label_set_calculation_service_pb2 as labeling_v1_label_set_calculation_service_pb2
from acme.labeling.v1 import labeling_pb2 as labeling_v1_labeling_pb2
from acme.labeling.v1 import labeling_task_calculation_service_pb2 as labeling_v1_labeling_task_calculation_service_pb2
from acme.labeling.v1 import refs_pb2 as labeling_v1_refs_pb2
from acme.lineage.v1 import impact_calculation_service_pb2 as lineage_v1_impact_calculation_service_pb2
from acme.lineage.v1 import lineage_pb2 as lineage_v1_lineage_pb2
from acme.modelregistry.v1 import modelregistry_pb2 as modelregistry_v1_modelregistry_pb2
from acme.modelregistry.v1 import (
    registered_model_calculation_service_pb2 as modelregistry_v1_registered_model_calculation_service_pb2,
)
from acme.modelregistry.v1 import registered_model_service_pb2 as modelregistry_v1_registered_model_service_pb2
from acme.tours.v1 import tour_query_service_pb2 as tours_v1_tour_query_service_pb2

from acme_data.domains.labeling import hooks
from acme_data.domains.labeling.adapters import LabelSetCalculationCalculateLabelSet1Adapter
from acme_data.domains.labeling.adapters import LabelSetCalculationCalculateLabelSet1Port
from acme_data.domains.labeling.adapters import LabelSetCalculationCalculateLabelSet3Adapter
from acme_data.domains.labeling.adapters import LabelSetCalculationRecalculateLabelSets1Adapter
from acme_data.domains.labeling.adapters import LabelSetCalculationRecalculateLabelSets1Port
from acme_data.domains.labeling.dependencies import Dependencies
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import run_steps
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_id
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class LabelSetCalculationServicerHandlers:
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    async def CalculateLabelSet(
        self, request: labeling_v1_label_set_calculation_service_pb2.CalculateLabelSetRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_label_set_calculation_service_pb2.CalculateLabelSetResponse:
        """Calculates a label set."""
        return await self.handle_calculate_label_set(request)

    @rpc_errors
    async def CompareLabelSetOptions(
        self, request: labeling_v1_label_set_calculation_service_pb2.CompareLabelSetOptionsRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_label_set_calculation_service_pb2.CompareLabelSetOptionsResponse:
        """Compares a label set."""
        return await self.handle_compare_label_set_options(request)

    @rpc_errors
    async def EstimateLabelSet(
        self, request: labeling_v1_label_set_calculation_service_pb2.EstimateLabelSetRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_label_set_calculation_service_pb2.EstimateLabelSetResponse:
        """Estimates a label set."""
        return await self.handle_estimate_label_set(request)

    @rpc_errors
    async def ExplainLabelSetCalculation(
        self, request: labeling_v1_label_set_calculation_service_pb2.ExplainLabelSetCalculationRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_label_set_calculation_service_pb2.ExplainLabelSetCalculationResponse:
        """Explains a label set."""
        return await self.handle_explain_label_set_calculation(request)

    @rpc_errors
    @retry_transient
    async def GetLabelSetRates(
        self, request: labeling_v1_label_set_calculation_service_pb2.GetLabelSetRatesRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_label_set_calculation_service_pb2.GetLabelSetRatesResponse:
        """Returns a label set."""
        return await self.handle_get_label_set_rates(request)

    @rpc_errors
    async def QuoteLabelSet(
        self, request: labeling_v1_label_set_calculation_service_pb2.QuoteLabelSetRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_label_set_calculation_service_pb2.QuoteLabelSetResponse:
        """Quotes a label set."""
        return await self.handle_quote_label_set(request)

    @rpc_errors
    async def RecalculateLabelSets(
        self, request: labeling_v1_label_set_calculation_service_pb2.RecalculateLabelSetsRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_label_set_calculation_service_pb2.RecalculateLabelSetsResponse:
        """Recalculates a label set."""
        return await self.handle_recalculate_label_sets(request)

    @rpc_errors
    async def SimulateLabelSet(
        self, request: labeling_v1_label_set_calculation_service_pb2.SimulateLabelSetRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_label_set_calculation_service_pb2.SimulateLabelSetResponse:
        """Simulates a label set."""
        return await self.handle_simulate_label_set(request)

    async def handle_calculate_label_set(
        self,
        request: labeling_v1_label_set_calculation_service_pb2.CalculateLabelSetRequest
    ) -> labeling_v1_label_set_calculation_service_pb2.CalculateLabelSetResponse:
        """Calculates a label set."""
        deps = self.deps
        response = labeling_v1_label_set_calculation_service_pb2.CalculateLabelSetResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CalculateLabelSet', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'CalculateLabelSet', {'reason': request.reason})
            await deps.repository.save_label_set(request.context.tenant_id, request.label_set)
            response_0 = keymanagement_v1_crypto_key_calculation_service_pb2.QuoteCryptoKeyResponse()
            response_1 = labeling_v1_annotation_calculation_service_pb2.EstimateAnnotationResponse()
            response_2 = lineage_v1_impact_calculation_service_pb2.EstimateImpactResponse()
            response_3 = featurestore_v1_feature_view_validation_service_pb2.PreviewFeatureViewResponse()
            outgoing_0 = keymanagement_v1_crypto_key_calculation_service_pb2.QuoteCryptoKeyRequest()
            outgoing_0.context.CopyFrom(request.context)
            outgoing_0.details.destination.recipient = request.details.destination.recipient
            outgoing_0.details.destination.country_code = request.label_set.location.country_code
            outgoing_0.context.tenant_id = tenant_id.get()
            response_0 = await deps.clients.keymanagement_crypto_key_calculation.QuoteCryptoKey(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = labeling_v1_annotation_calculation_service_pb2.EstimateAnnotationRequest(
                context=request.context,
                details=labeling_v1_annotation_calculation_service_pb2.EstimateAnnotationRequest.Details(
                    destination=common_v1_address_pb2.PostalAddress(
                        lines=list(request.details.destination.lines),
                        recipient=request.details.destination.recipient
                    )
                )
            )
            port_1: LabelSetCalculationCalculateLabelSet1Port = LabelSetCalculationCalculateLabelSet1Adapter(
                deps.clients.labeling_annotation_calculation,
                deps.settings.timeout
            )
            response_1 = await port_1.execute(outgoing_1)
            outgoing_2 = lineage_v1_impact_calculation_service_pb2.EstimateImpactRequest(
                context=request.context,
                details=lineage_v1_impact_calculation_service_pb2.EstimateImpactRequest.Details(
                    destination=common_v1_address_pb2.PostalAddress(recipient=request.details.destination.recipient)
                ),
                impact=lineage_v1_lineage_pb2.Impact(
                    assignee=identity_v1_refs_pb2.UserRef(email=response_0.crypto_key.contact.email),
                    comments=[lineage_v1_lineage_pb2.ImpactComment(created_at=request.label_set.audit.created_at)]
                )
            )
            steps_2 = [
                partial(
                    deps.clients.lineage_impact_calculation.EstimateImpact,
                    outgoing_2,
                    timeout=deps.settings.timeout
                )
            ]
            results_2 = await run_steps(steps_2)
            response_2 = results_2[-1]
            outgoing_3 = featurestore_v1_feature_view_validation_service_pb2.PreviewFeatureViewRequest(
                context=request.context,
                details=featurestore_v1_feature_view_validation_service_pb2.PreviewFeatureViewRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(
                        email=response_2.impact.requester.email,
                        preferred_channel=response_0.crypto_key.contact.preferred_channel
                    )
                )
            )
            response_3 = await LabelSetCalculationCalculateLabelSet3Adapter(
                deps.clients.featurestore_feature_view_validation,
                deps.settings.timeout
            )(outgoing_3)
            returned_0_0 = response_0.crypto_key.audit.created_by
            if returned_0_0:
                response.label_set.audit.created_by = returned_0_0
            returned_1_0 = response_1.annotation.correlation_id
            if returned_1_0:
                response.result.correlation_id = returned_1_0
            returned_2_0 = response_2.impact.assignee.email
            returned_2_0_part_1 = response.label_set.children.add()
            if returned_2_0:
                returned_2_0_part_1.manager.email = returned_2_0
            returned_3_0 = response_3.feature_view.owner.display_name
            returned_3_0_part_1 = response.label_set.children.add()
            returned_3_0_part_2 = returned_3_0_part_1.children.add()
            if returned_3_0:
                returned_3_0_part_2.manager.display_name = returned_3_0
            returned_3_1 = response_3.feature_view.address.recipient
            if returned_3_1:
                response.label_set.location.recipient = returned_3_1
            echoed_0 = request.label_set_id
            response.label_set.label_set_id = echoed_0
            echoed_1 = request.label_set.parent_id
            response.label_set.parent_id = echoed_1
            return response

    async def handle_compare_label_set_options(
        self,
        request: labeling_v1_label_set_calculation_service_pb2.CompareLabelSetOptionsRequest
    ) -> labeling_v1_label_set_calculation_service_pb2.CompareLabelSetOptionsResponse:
        """Compares a label set."""
        deps = self.deps
        response = labeling_v1_label_set_calculation_service_pb2.CompareLabelSetOptionsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CompareLabelSetOptions', extra={'fields': {'currency_code': request.details.currency_code}})
            await deps.repository.audit(
                request.context.tenant_id,
                'CompareLabelSetOptions',
                {'currency_code': request.details.currency_code}
            )
            await deps.repository.save_label_set(request.context.tenant_id, request.label_set)
            response_0 = labeling_v1_annotation_calculation_service_pb2.CompareAnnotationOptionsResponse()
            response_1 = modelregistry_v1_registered_model_calculation_service_pb2.EstimateRegisteredModelResponse()
            response_2 = tours_v1_tour_query_service_pb2.SummarizeToursResponse()
            outgoing_0 = labeling_v1_annotation_calculation_service_pb2.CompareAnnotationOptionsRequest(
                context=request.context,
                details=labeling_v1_annotation_calculation_service_pb2.CompareAnnotationOptionsRequest.Details(
                    destination=common_v1_address_pb2.PostalAddress(
                        recipient=request.details.destination.recipient,
                        region=request.details.destination.region
                    )
                )
            )
            response_0 = cast(labeling_v1_annotation_calculation_service_pb2.CompareAnnotationOptionsResponse, await deps.bus.request(
                'acme.labeling.v1.LabelSetCalculationService/CompareLabelSetOptions/0', outgoing_0, deps.settings.timeout,
            ))
            outgoing_1 = modelregistry_v1_registered_model_calculation_service_pb2.EstimateRegisteredModelRequest(
                context=request.context,
                details=modelregistry_v1_registered_model_calculation_service_pb2.EstimateRegisteredModelRequest.Details(
                    destination=common_v1_address_pb2.PostalAddress(lines=list(request.details.destination.lines))
                ),
                registered_model=modelregistry_v1_modelregistry_pb2.RegisteredModel(
                    address=common_v1_address_pb2.PostalAddress(region=request.label_set.location.region),
                    owner=identity_v1_refs_pb2.UserRef(user_id=request.label_set.manager.user_id)
                )
            )
            response_1 = await deps.clients.modelregistry_registered_model_calculation.EstimateRegisteredModel(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = tours_v1_tour_query_service_pb2.SummarizeToursRequest(
                annotations=dict(request.annotations),
                context=request.context,
                reason=request.reason
            )
            method_name_2 = 'SummarizeTours'
            response_2 = await getattr(
                deps.clients.tours_tour_query,
                method_name_2
            )(outgoing_2, timeout=deps.settings.timeout)
            returned_0_0 = response_0.result.details
            response.result.details.update(returned_0_0)
            returned_0_1 = response_0.annotation.attributes
            returned_0_1_part_1 = response.label_set.children.add()
            returned_0_1_part_2 = returned_0_1_part_1.children.add()
            returned_0_1_part_3 = returned_0_1_part_2.children.add()
            returned_0_1_part_3.attributes.update(returned_0_1)
            returned_1_0 = response_1.registered_model.address.recipient
            returned_1_0_part_1 = response.label_set.children.add()
            returned_1_0_part_2 = returned_1_0_part_1.children.add()
            if returned_1_0:
                returned_1_0_part_2.location.recipient = returned_1_0
            returned_2_0 = response_2.result.details
            response.result.details.update(returned_2_0)
            echoed_0 = request.label_set_id
            response.label_set.label_set_id = echoed_0
            echoed_1 = request.label_set.status
            response.label_set.status = echoed_1
            return response

    async def handle_estimate_label_set(
        self,
        request: labeling_v1_label_set_calculation_service_pb2.EstimateLabelSetRequest
    ) -> labeling_v1_label_set_calculation_service_pb2.EstimateLabelSetResponse:
        """Estimates a label set."""
        deps = self.deps
        response = labeling_v1_label_set_calculation_service_pb2.EstimateLabelSetResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('EstimateLabelSet', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'EstimateLabelSet', {'reason': request.reason})
            await deps.repository.save_label_set(request.context.tenant_id, request.label_set)
            response_0 = labeling_v1_annotation_calculation_service_pb2.RecalculateAnnotationsResponse()
            response_1 = labeling_v1_annotation_calculation_service_pb2.ExplainAnnotationCalculationResponse()
            response_2 = labeling_v1_annotation_calculation_service_pb2.SimulateAnnotationResponse()
            response_3 = labeling_v1_labeling_task_calculation_service_pb2.QuoteLabelingTaskResponse()
            outgoing_0 = labeling_v1_annotation_calculation_service_pb2.RecalculateAnnotationsRequest(
                context=request.context,
                details=labeling_v1_annotation_calculation_service_pb2.RecalculateAnnotationsRequest.Details(
                    destination=common_v1_address_pb2.PostalAddress(
                        country_code=request.label_set.location.country_code,
                        recipient=request.details.destination.recipient,
                        region=request.details.destination.region
                    )
                )
            )
            outgoing_3 = labeling_v1_labeling_task_calculation_service_pb2.QuoteLabelingTaskRequest(
                context=request.context,
                labeling_task=labeling_v1_labeling_pb2.LabelingTask(
                    assignee=identity_v1_refs_pb2.UserRef(user_id=request.label_set.manager.user_id),
                    comments=[
                        labeling_v1_labeling_pb2.LabelingTaskComment(created_at=request.label_set.audit.created_at)
                    ]
                )
            )
            response_0, response_3 = await asyncio.gather(
                deps.clients.labeling_annotation_calculation.RecalculateAnnotations(
                    outgoing_0,
                    timeout=deps.settings.timeout
                ),
                deps.clients.labeling_labeling_task_calculation.QuoteLabelingTask(
                    outgoing_3,
                    timeout=deps.settings.timeout
                ),
            )
            outgoing_1 = labeling_v1_annotation_calculation_service_pb2.ExplainAnnotationCalculationRequest(
                annotation=labeling_v1_labeling_pb2.Annotation(
                    subject=labeling_v1_refs_pb2.LabelingTaskRef(priority=response_0.annotation.subject.priority)
                ),
                context=request.context
            )
            document_1 = MessageToDict(outgoing_1, preserving_proto_field_name=True)
            outgoing_1 = ParseDict(
                document_1,
                labeling_v1_annotation_calculation_service_pb2.ExplainAnnotationCalculationRequest()
            )
            response_1 = await deps.clients.labeling_annotation_calculation.ExplainAnnotationCalculation(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = labeling_v1_annotation_calculation_service_pb2.SimulateAnnotationRequest(
                annotation=labeling_v1_labeling_pb2.Annotation(
                    subject=labeling_v1_refs_pb2.LabelingTaskRef(
                        labeling_task_id=response_1.annotation.subject.labeling_task_id
                    )
                ),
                context=request.context
            )
            document_2 = MessageToJson(outgoing_2, preserving_proto_field_name=True)
            outgoing_2 = Parse(document_2, labeling_v1_annotation_calculation_service_pb2.SimulateAnnotationRequest())
            response_2 = await deps.clients.labeling_annotation_calculation.SimulateAnnotation(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.details
            response.result.details.update(returned_0_0)
            returned_1_0 = response_1.result.reference_ids
            response.result.reference_ids.extend(returned_1_0)
            returned_2_0 = response_2.annotation.attributes
            returned_2_0_part_1 = response.label_set.children.add()
            returned_2_0_part_1.attributes.update(returned_2_0)
            returned_3_0 = response_3.labeling_task.assignee.display_name
            returned_3_0_part_1 = response.label_set.children.add()
            returned_3_0_part_2 = returned_3_0_part_1.children.add()
            if returned_3_0:
                returned_3_0_part_2.manager.display_name = returned_3_0
            echoed_0 = request.label_set_id
            response.label_set.label_set_id = echoed_0
            echoed_1 = request.label_set.attributes
            response.label_set.attributes.update(echoed_1)
            return response

    async def handle_explain_label_set_calculation(
        self,
        request: labeling_v1_label_set_calculation_service_pb2.ExplainLabelSetCalculationRequest
    ) -> labeling_v1_label_set_calculation_service_pb2.ExplainLabelSetCalculationResponse:
        """Explains a label set."""
        deps = self.deps
        response = labeling_v1_label_set_calculation_service_pb2.ExplainLabelSetCalculationResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ExplainLabelSetCalculation', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ExplainLabelSetCalculation',
                {'reason': request.reason}
            )
            await deps.repository.save_label_set(request.context.tenant_id, request.label_set)
            response_0 = lineage_v1_impact_calculation_service_pb2.CalculateImpactResponse()
            outgoing_0 = lineage_v1_impact_calculation_service_pb2.CalculateImpactRequest(
                context=request.context,
                impact=lineage_v1_lineage_pb2.Impact(
                    audit=common_v1_audit_pb2.AuditInfo(updated_at=request.label_set.audit.updated_at),
                    customer=customers_v1_refs_pb2.CustomerRef(email=request.label_set.manager.email)
                )
            )
            envelope_0 = AnyMessage()
            envelope_0.Pack(outgoing_0)
            outgoing_0 = lineage_v1_impact_calculation_service_pb2.CalculateImpactRequest()
            if not envelope_0.Unpack(outgoing_0):
                raise ValueError("partner envelope contains the wrong request type")
            response_0 = await deps.clients.lineage_impact_calculation.CalculateImpact(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.impact.audit.created_at
            returned_0_0_part_1 = response.label_set.children.add()
            if returned_0_0.ListFields():
                returned_0_0_part_1.audit.created_at.MergeFrom(returned_0_0)
            returned_0_1 = response_0.impact.customer.email
            if returned_0_1:
                response.label_set.manager.email = returned_0_1
            echoed_0 = request.label_set_id
            response.label_set.label_set_id = echoed_0
            echoed_1 = request.label_set.status
            response.label_set.status = echoed_1
            return response

    async def handle_get_label_set_rates(
        self,
        request: labeling_v1_label_set_calculation_service_pb2.GetLabelSetRatesRequest
    ) -> labeling_v1_label_set_calculation_service_pb2.GetLabelSetRatesResponse:
        """Returns a label set."""
        deps = self.deps
        response = labeling_v1_label_set_calculation_service_pb2.GetLabelSetRatesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('GetLabelSetRates', extra={'fields': {'domain': 'labeling'}})
            await deps.repository.audit(request.context.tenant_id, 'GetLabelSetRates', {})
            response_0 = labeling_v1_annotation_calculation_service_pb2.CalculateAnnotationResponse()
            outgoing_0 = labeling_v1_annotation_calculation_service_pb2.CalculateAnnotationRequest(
                annotation=labeling_v1_labeling_pb2.Annotation(
                    correlation_id=request.context.actor.user_id,
                    measurements=[labeling_v1_labeling_pb2.AnnotationMeasurement(observed_at=request.context.deadline)],
                    source=request.label_set_id
                ),
                context=request.context
            )
            response_0 = await deps.clients.labeling_annotation_calculation.CalculateAnnotation(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.correlation_id
            if returned_0_0:
                response.result.correlation_id = returned_0_0
            echoed_0 = request.label_set_id
            response.label_set.label_set_id = echoed_0
            return response

    async def handle_quote_label_set(
        self,
        request: labeling_v1_label_set_calculation_service_pb2.QuoteLabelSetRequest
    ) -> labeling_v1_label_set_calculation_service_pb2.QuoteLabelSetResponse:
        """Quotes a label set."""
        deps = self.deps
        response = labeling_v1_label_set_calculation_service_pb2.QuoteLabelSetResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('QuoteLabelSet', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'QuoteLabelSet', {'reason': request.reason})
            await deps.repository.save_label_set(request.context.tenant_id, request.label_set)
            response_0 = anomalies_v1_detector_validation_service_pb2.ValidateDetectorResponse()
            response_1 = labeling_v1_annotation_calculation_service_pb2.RecalculateAnnotationsResponse()
            response_2 = labeling_v1_labeling_task_calculation_service_pb2.QuoteLabelingTaskResponse()
            response_3 = audit_v1_audit_event_validation_service_pb2.ExplainAuditEventDecisionResponse()
            outgoing_0 = anomalies_v1_detector_validation_service_pb2.ValidateDetectorRequest(
                context=request.context,
                details=anomalies_v1_detector_validation_service_pb2.ValidateDetectorRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(email=request.label_set.manager.email)
                )
            )
            outgoing_1 = labeling_v1_annotation_calculation_service_pb2.RecalculateAnnotationsRequest(
                context=request.context,
                details=labeling_v1_annotation_calculation_service_pb2.RecalculateAnnotationsRequest.Details(
                    destination=common_v1_address_pb2.PostalAddress(
                        country_code=request.label_set.location.country_code
                    )
                )
            )
            response_0, response_1 = await asyncio.gather(
                deps.clients.anomalies_detector_validation.ValidateDetector(outgoing_0, timeout=deps.settings.timeout),
                deps.clients.labeling_annotation_calculation.RecalculateAnnotations(
                    outgoing_1,
                    timeout=deps.settings.timeout
                ),
            )
            outgoing_2 = labeling_v1_labeling_task_calculation_service_pb2.QuoteLabelingTaskRequest(
                context=request.context,
                details=labeling_v1_labeling_task_calculation_service_pb2.QuoteLabelingTaskRequest.Details(
                    destination=common_v1_address_pb2.PostalAddress(region=request.label_set.location.region)
                ),
                labeling_task=labeling_v1_labeling_pb2.LabelingTask(
                    assignee=identity_v1_refs_pb2.UserRef(email=response_0.detector.owner.email),
                    audit=common_v1_audit_pb2.AuditInfo(updated_at=request.label_set.audit.updated_at)
                )
            )
            send_2 = partial(
                deps.clients.labeling_labeling_task_calculation.QuoteLabelingTask,
                timeout=deps.settings.timeout
            )
            response_2 = await send_2(outgoing_2)
            outgoing_3 = audit_v1_audit_event_validation_service_pb2.ExplainAuditEventDecisionRequest(
                audit_event=audit_v1_audit_pb2.AuditEvent(
                    subject=audit_v1_refs_pb2.AuditTrailRef(display_name=response_1.annotation.subject.display_name)
                ),
                context=request.context,
                details=audit_v1_audit_event_validation_service_pb2.ExplainAuditEventDecisionRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(email=response_2.labeling_task.requester.email)
                )
            )
            response_3 = await hooks.label_set_calculation_quote_label_set3(
                deps.clients.audit_audit_event_validation,
                outgoing_3,
                deps.settings.timeout
            )
            returned_0_0 = response_0.detector.owner.display_name
            if returned_0_0:
                response.label_set.manager.display_name = returned_0_0
            returned_0_1 = response_0.result.status
            if returned_0_1:
                response.result.status = returned_0_1
            returned_1_0 = response_1.breakdown.total
            if returned_1_0.ListFields():
                response.breakdown.total.MergeFrom(returned_1_0)
            returned_2_0 = response_2.breakdown.total
            if returned_2_0.ListFields():
                response.breakdown.total.MergeFrom(returned_2_0)
            returned_2_1 = response_2.labeling_task.assignee.user_id
            if returned_2_1:
                response.label_set.manager.user_id = returned_2_1
            returned_3_0 = response_3.outcome.status
            if returned_3_0:
                response.result.status = returned_3_0
            returned_3_1 = response_3.audit_event.attributes
            returned_3_1_part_1 = response.label_set.children.add()
            returned_3_1_part_1.attributes.update(returned_3_1)
            echoed_0 = request.label_set_id
            response.label_set.label_set_id = echoed_0
            echoed_1 = request.label_set.depth
            response.label_set.depth = echoed_1
            return response

    async def handle_recalculate_label_sets(
        self,
        request: labeling_v1_label_set_calculation_service_pb2.RecalculateLabelSetsRequest
    ) -> labeling_v1_label_set_calculation_service_pb2.RecalculateLabelSetsResponse:
        """Recalculates a label set."""
        deps = self.deps
        response = labeling_v1_label_set_calculation_service_pb2.RecalculateLabelSetsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('RecalculateLabelSets', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'RecalculateLabelSets', {'reason': request.reason})
            await deps.repository.save_label_set(request.context.tenant_id, request.label_set)
            response_0 = modelregistry_v1_registered_model_service_pb2.BatchCreateRegisteredModelsResponse()
            response_1 = labeling_v1_annotation_calculation_service_pb2.EstimateAnnotationResponse()
            outgoing_0 = modelregistry_v1_registered_model_service_pb2.BatchCreateRegisteredModelsRequest(
                context=request.context,
                record=modelregistry_v1_modelregistry_pb2.RegisteredModel(
                    address=common_v1_address_pb2.PostalAddress(
                        postal_code=request.label_set.location.postal_code,
                        region=request.label_set.location.region
                    ),
                    audit=common_v1_audit_pb2.AuditInfo(updated_by=request.label_set.audit.updated_by),
                    owner=identity_v1_refs_pb2.UserRef(user_id=request.label_set.manager.user_id)
                )
            )
            response_0 = await deps.clients.modelregistry_registered_model.BatchCreateRegisteredModels(
                async_messages((outgoing_0,)),
                timeout=deps.settings.timeout
            )
            outgoing_1 = labeling_v1_annotation_calculation_service_pb2.EstimateAnnotationRequest(
                context=request.context,
                details=labeling_v1_annotation_calculation_service_pb2.EstimateAnnotationRequest.Details(
                    destination=common_v1_address_pb2.PostalAddress(
                        locality=request.label_set.location.locality,
                        postal_code=request.details.destination.postal_code,
                        region=request.label_set.location.region
                    )
                )
            )
            port_1: LabelSetCalculationRecalculateLabelSets1Port = LabelSetCalculationRecalculateLabelSets1Adapter(
                deps.clients.labeling_annotation_calculation,
                deps.settings.timeout
            )
            response_1 = await port_1.execute(outgoing_1)
            returned_1_0 = response_1.result.reference_ids
            response.result.reference_ids.extend(returned_1_0)
            echoed_0 = request.label_set_id
            response.label_set.label_set_id = echoed_0
            echoed_1 = request.label_set.manager
            response.label_set.manager.CopyFrom(echoed_1)
            return response

    async def handle_simulate_label_set(
        self,
        request: labeling_v1_label_set_calculation_service_pb2.SimulateLabelSetRequest
    ) -> labeling_v1_label_set_calculation_service_pb2.SimulateLabelSetResponse:
        """Simulates a label set."""
        deps = self.deps
        response = labeling_v1_label_set_calculation_service_pb2.SimulateLabelSetResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SimulateLabelSet', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'SimulateLabelSet', {'reason': request.reason})
            await deps.repository.save_label_set(request.context.tenant_id, request.label_set)
            response_0 = labeling_v1_annotation_calculation_service_pb2.SimulateAnnotationResponse()
            outgoing_0 = labeling_v1_annotation_calculation_service_pb2.SimulateAnnotationRequest(
                context=request.context,
                details=labeling_v1_annotation_calculation_service_pb2.SimulateAnnotationRequest.Details(
                    destination=common_v1_address_pb2.PostalAddress(
                        lines=list(request.details.destination.lines),
                        recipient=request.label_set.location.recipient
                    )
                )
            )
            steps_0 = [
                partial(
                    deps.clients.labeling_annotation_calculation.SimulateAnnotation,
                    outgoing_0,
                    timeout=deps.settings.timeout
                )
            ]
            results_0 = await run_steps(steps_0)
            response_0 = results_0[-1]
            returned_0_0 = response_0.breakdown.currency_code
            if returned_0_0:
                response.breakdown.currency_code = returned_0_0
            echoed_0 = request.label_set_id
            response.label_set.label_set_id = echoed_0
            echoed_1 = request.label_set.attributes
            response.label_set.attributes.update(echoed_1)
            return response
