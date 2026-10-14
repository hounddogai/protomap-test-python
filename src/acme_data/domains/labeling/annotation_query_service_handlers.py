"""Reusable transport mixin for AnnotationQueryService."""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import cast
import logging

from google.protobuf.any_pb2 import Any as AnyMessage
from google.protobuf.json_format import MessageToDict
from google.protobuf.json_format import ParseDict
import grpc

from acme.anomalies.v1 import (
    anomaly_feedback_validation_service_pb2 as anomalies_v1_anomaly_feedback_validation_service_pb2,
)
from acme.broadcasts.v1 import broadcast_query_service_pb2 as broadcasts_v1_broadcast_query_service_pb2
from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.labeling.v1 import annotation_query_service_pb2 as labeling_v1_annotation_query_service_pb2
from acme.labeling.v1 import annotation_validation_service_pb2 as labeling_v1_annotation_validation_service_pb2
from acme.labeling.v1 import label_set_validation_service_pb2 as labeling_v1_label_set_validation_service_pb2
from acme.labeling.v1 import labeling_pb2 as labeling_v1_labeling_pb2
from acme.labeling.v1 import labeling_task_calculation_service_pb2 as labeling_v1_labeling_task_calculation_service_pb2
from acme.labeling.v1 import labeling_task_validation_service_pb2 as labeling_v1_labeling_task_validation_service_pb2
from acme.ledger.v1 import ledger_account_query_service_pb2 as ledger_v1_ledger_account_query_service_pb2

from acme_data.domains.labeling.dependencies import Dependencies
from acme_data.platform.rpc import messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class AnnotationQueryServicerHandlers:
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    @retry_transient
    async def BrowseAnnotations(
        self, request: labeling_v1_annotation_query_service_pb2.BrowseAnnotationsRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_annotation_query_service_pb2.BrowseAnnotationsResponse:
        """Lists annotations a page at a time."""
        return await self.handle_browse_annotations(request)

    @rpc_errors
    @retry_transient
    async def CountAnnotations(
        self, request: labeling_v1_annotation_query_service_pb2.CountAnnotationsRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_annotation_query_service_pb2.CountAnnotationsResponse:
        """Counts annotations by status."""
        return await self.handle_count_annotations(request)

    @stream_errors
    async def ExportAnnotations(
        self, request: labeling_v1_annotation_query_service_pb2.ExportAnnotationsRequest, context: grpc.aio.ServicerContext,
    ) -> AsyncIterator[labeling_v1_annotation_query_service_pb2.ExportAnnotationsResponse]:
        """Streams every matching annotation."""
        response = await self.handle_export_annotations(request)
        for item in messages((response,)):
            yield item

    @rpc_errors
    @retry_transient
    async def LookupAnnotation(
        self, request: labeling_v1_annotation_query_service_pb2.LookupAnnotationRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_annotation_query_service_pb2.LookupAnnotationResponse:
        """Returns an annotation."""
        return await self.handle_lookup_annotation(request)

    @rpc_errors
    @retry_transient
    async def PeekAnnotation(
        self, request: labeling_v1_annotation_query_service_pb2.PeekAnnotationRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_annotation_query_service_pb2.PeekAnnotationResponse:
        """Returns an annotation."""
        return await self.handle_peek_annotation(request)

    @rpc_errors
    @retry_transient
    async def SuggestAnnotations(
        self, request: labeling_v1_annotation_query_service_pb2.SuggestAnnotationsRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_annotation_query_service_pb2.SuggestAnnotationsResponse:
        """Lists annotations a page at a time."""
        return await self.handle_suggest_annotations(request)

    @rpc_errors
    async def SummarizeAnnotations(
        self, request: labeling_v1_annotation_query_service_pb2.SummarizeAnnotationsRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_annotation_query_service_pb2.SummarizeAnnotationsResponse:
        """Summarizes an annotation."""
        return await self.handle_summarize_annotations(request)

    async def handle_browse_annotations(
        self,
        request: labeling_v1_annotation_query_service_pb2.BrowseAnnotationsRequest
    ) -> labeling_v1_annotation_query_service_pb2.BrowseAnnotationsResponse:
        """Lists annotations a page at a time."""
        deps = self.deps
        response = labeling_v1_annotation_query_service_pb2.BrowseAnnotationsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('BrowseAnnotations', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(request.context.tenant_id, 'BrowseAnnotations', {'order_by': request.order_by})
            return response

    async def handle_count_annotations(
        self,
        request: labeling_v1_annotation_query_service_pb2.CountAnnotationsRequest
    ) -> labeling_v1_annotation_query_service_pb2.CountAnnotationsResponse:
        """Counts annotations by status."""
        deps = self.deps
        response = labeling_v1_annotation_query_service_pb2.CountAnnotationsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CountAnnotations', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(request.context.tenant_id, 'CountAnnotations', {'order_by': request.order_by})
            response_0 = labeling_v1_labeling_task_calculation_service_pb2.CompareLabelingTaskOptionsResponse()
            outgoing_0 = labeling_v1_labeling_task_calculation_service_pb2.CompareLabelingTaskOptionsRequest(
                context=request.context,
                details=labeling_v1_labeling_task_calculation_service_pb2.CompareLabelingTaskOptionsRequest.Details(
                    destination=common_v1_address_pb2.PostalAddress(region=request.filter.region)
                ),
                labeling_task=labeling_v1_labeling_pb2.LabelingTask(
                    requester=common_v1_contact_pb2.ContactInfo(email=request.context.actor.email)
                )
            )
            response_0 = await deps.clients.labeling_labeling_task_calculation.CompareLabelingTaskOptions(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.correlation_id
            if returned_0_0:
                response.result.correlation_id = returned_0_0
            return response

    async def handle_export_annotations(
        self,
        request: labeling_v1_annotation_query_service_pb2.ExportAnnotationsRequest
    ) -> labeling_v1_annotation_query_service_pb2.ExportAnnotationsResponse:
        """Streams every matching annotation."""
        deps = self.deps
        response = labeling_v1_annotation_query_service_pb2.ExportAnnotationsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ExportAnnotations', extra={'fields': {'destination_uri': request.destination_uri}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ExportAnnotations',
                {'destination_uri': request.destination_uri}
            )
            response_0 = labeling_v1_annotation_validation_service_pb2.LintAnnotationsResponse()
            response_1 = labeling_v1_label_set_validation_service_pb2.LintLabelSetsResponse()
            outgoing_0 = labeling_v1_annotation_validation_service_pb2.LintAnnotationsRequest(
                annotation=labeling_v1_labeling_pb2.Annotation(occurred_at=request.filter.created_after),
                context=request.context,
                details=labeling_v1_annotation_validation_service_pb2.LintAnnotationsRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(email=request.context.actor.email),
                    locale=request.context.locale
                )
            )
            response_0 = cast(labeling_v1_annotation_validation_service_pb2.LintAnnotationsResponse, await deps.bus.request(
                'acme.labeling.v1.AnnotationQueryService/ExportAnnotations/0', outgoing_0, deps.settings.timeout,
            ))
            outgoing_1 = labeling_v1_label_set_validation_service_pb2.LintLabelSetsRequest(
                context=request.context,
                label_set=labeling_v1_labeling_pb2.LabelSet(
                    children=[
                        labeling_v1_labeling_pb2.LabelSet(
                            children=[
                                labeling_v1_labeling_pb2.LabelSet(
                                    location=common_v1_address_pb2.PostalAddress(region=request.filter.region),
                                    manager=identity_v1_refs_pb2.UserRef(
                                        display_name=response_0.annotation.subject.display_name
                                    )
                                )
                            ]
                        )
                    ]
                )
            )
            response_1 = await deps.clients.labeling_label_set_validation.LintLabelSets(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.annotation.subject.priority
            if returned_0_0:
                response.annotation.subject.priority = returned_0_0
            returned_1_0 = response_1.outcome.message
            if returned_1_0:
                response.result.message = returned_1_0
            return response

    async def handle_lookup_annotation(
        self,
        request: labeling_v1_annotation_query_service_pb2.LookupAnnotationRequest
    ) -> labeling_v1_annotation_query_service_pb2.LookupAnnotationResponse:
        """Returns an annotation."""
        deps = self.deps
        response = labeling_v1_annotation_query_service_pb2.LookupAnnotationResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('LookupAnnotation', extra={'fields': {'domain': 'labeling'}})
            await deps.repository.audit(request.context.tenant_id, 'LookupAnnotation', {})
            response_0 = ledger_v1_ledger_account_query_service_pb2.SuggestLedgerAccountsResponse()
            outgoing_0 = ledger_v1_ledger_account_query_service_pb2.SuggestLedgerAccountsRequest(
                context=request.context,
                filter=ledger_v1_ledger_account_query_service_pb2.SuggestLedgerAccountsRequest.Filter(
                    created_after=request.context.deadline,
                    labels=dict(request.context.baggage),
                    owner_id=request.annotation_id
                )
            )
            response_0 = await deps.clients.ledger_ledger_account_query.SuggestLedgerAccounts(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.result.message = returned_0_0
            returned_0_1 = response_0.result.details
            response.result.details.update(returned_0_1)
            echoed_0 = request.annotation_id
            response.annotation.annotation_id = echoed_0
            return response

    async def handle_peek_annotation(
        self,
        request: labeling_v1_annotation_query_service_pb2.PeekAnnotationRequest
    ) -> labeling_v1_annotation_query_service_pb2.PeekAnnotationResponse:
        """Returns an annotation."""
        deps = self.deps
        response = labeling_v1_annotation_query_service_pb2.PeekAnnotationResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('PeekAnnotation', extra={'fields': {'domain': 'labeling'}})
            await deps.repository.audit(request.context.tenant_id, 'PeekAnnotation', {})
            response_0 = labeling_v1_labeling_task_validation_service_pb2.ValidateLabelingTaskResponse()
            response_1 = labeling_v1_label_set_validation_service_pb2.ValidateLabelSetResponse()
            outgoing_0 = labeling_v1_labeling_task_validation_service_pb2.ValidateLabelingTaskRequest(
                context=request.context,
                details=labeling_v1_labeling_task_validation_service_pb2.ValidateLabelingTaskRequest.Details(
                    locale=request.context.locale
                ),
                labeling_task=labeling_v1_labeling_pb2.LabelingTask(
                    assignee=identity_v1_refs_pb2.UserRef(
                        email=request.context.actor.email,
                        user_id=request.context.actor.user_id
                    )
                )
            )
            response_0 = await deps.clients.labeling_labeling_task_validation.ValidateLabelingTask(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = labeling_v1_label_set_validation_service_pb2.ValidateLabelSetRequest(
                context=request.context,
                label_set=labeling_v1_labeling_pb2.LabelSet(
                    children=[
                        labeling_v1_labeling_pb2.LabelSet(
                            children=[
                                labeling_v1_labeling_pb2.LabelSet(
                                    audit=common_v1_audit_pb2.AuditInfo(
                                        updated_by=response_0.labeling_task.audit.updated_by
                                    ),
                                    manager=identity_v1_refs_pb2.UserRef(
                                        user_id=response_0.labeling_task.assignee.user_id
                                    )
                                )
                            ]
                        )
                    ]
                )
            )
            document_1 = MessageToDict(outgoing_1, preserving_proto_field_name=True)
            outgoing_1 = ParseDict(document_1, labeling_v1_label_set_validation_service_pb2.ValidateLabelSetRequest())
            response_1 = await deps.clients.labeling_label_set_validation.ValidateLabelSet(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.labeling_task.priority
            if returned_0_0:
                response.annotation.subject.priority = returned_0_0
            returned_1_0 = response_1.result.reference_ids
            response.result.reference_ids.extend(returned_1_0)
            returned_1_1 = response_1.label_set.attributes
            response.annotation.attributes.update(returned_1_1)
            echoed_0 = request.annotation_id
            response.annotation.annotation_id = echoed_0
            return response

    async def handle_suggest_annotations(
        self,
        request: labeling_v1_annotation_query_service_pb2.SuggestAnnotationsRequest
    ) -> labeling_v1_annotation_query_service_pb2.SuggestAnnotationsResponse:
        """Lists annotations a page at a time."""
        deps = self.deps
        response = labeling_v1_annotation_query_service_pb2.SuggestAnnotationsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SuggestAnnotations', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(request.context.tenant_id, 'SuggestAnnotations', {'order_by': request.order_by})
            response_0 = labeling_v1_annotation_validation_service_pb2.ScoreAnnotationResponse()
            outgoing_0 = labeling_v1_annotation_validation_service_pb2.ScoreAnnotationRequest(
                context=request.context,
                details=labeling_v1_annotation_validation_service_pb2.ScoreAnnotationRequest.Details(
                    destination=common_v1_address_pb2.PostalAddress(region=request.filter.region)
                )
            )
            response_0 = await deps.clients.labeling_annotation_validation.ScoreAnnotation(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.annotation.sequence
            returned_0_0_part_0 = response.annotations.add()
            if returned_0_0:
                returned_0_0_part_0.sequence = returned_0_0
            return response

    async def handle_summarize_annotations(
        self,
        request: labeling_v1_annotation_query_service_pb2.SummarizeAnnotationsRequest
    ) -> labeling_v1_annotation_query_service_pb2.SummarizeAnnotationsResponse:
        """Summarizes an annotation."""
        deps = self.deps
        response = labeling_v1_annotation_query_service_pb2.SummarizeAnnotationsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SummarizeAnnotations', extra={'fields': {'annotation_id': request.annotation_id}})
            await deps.repository.audit(
                request.context.tenant_id,
                'SummarizeAnnotations',
                {'annotation_id': request.annotation_id}
            )
            response_0 = anomalies_v1_anomaly_feedback_validation_service_pb2.PreviewAnomalyFeedbackResponse()
            response_1 = broadcasts_v1_broadcast_query_service_pb2.ResolveBroadcastsResponse()
            outgoing_0 = anomalies_v1_anomaly_feedback_validation_service_pb2.PreviewAnomalyFeedbackRequest()
            outgoing_0.context.CopyFrom(request.context)
            outgoing_0.annotations.update(dict(request.annotations))
            outgoing_0.reason = request.reason
            outgoing_0.details.locale = request.context.locale
            outgoing_0.details.contact.email = request.context.actor.email
            merged_0 = anomalies_v1_anomaly_feedback_validation_service_pb2.PreviewAnomalyFeedbackRequest()
            merged_0.MergeFrom(outgoing_0)
            outgoing_0.CopyFrom(merged_0)
            response_0 = await deps.clients.anomalies_anomaly_feedback_validation.PreviewAnomalyFeedback(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = broadcasts_v1_broadcast_query_service_pb2.ResolveBroadcastsRequest(context=request.context)
            envelope_1 = AnyMessage()
            envelope_1.Pack(outgoing_1)
            outgoing_1 = broadcasts_v1_broadcast_query_service_pb2.ResolveBroadcastsRequest()
            if not envelope_1.Unpack(outgoing_1):
                raise ValueError("partner envelope contains the wrong request type")
            response_1 = await deps.clients.broadcasts_broadcast_query.ResolveBroadcasts(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.correlation_id
            if returned_0_0:
                response.result.correlation_id = returned_0_0
            returned_1_0 = response_1.result.status
            if returned_1_0:
                response.result.status = returned_1_0
            echoed_0 = request.details.period
            response.period.CopyFrom(echoed_0)
            return response
