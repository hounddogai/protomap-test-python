"""Answers read-only questions about detectors, for screens and reports."""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import cast
import logging

import grpc

from acme.anomalies.v1 import anomalies_pb2 as anomalies_v1_anomalies_pb2
from acme.anomalies.v1 import (
    anomaly_feedback_calculation_service_pb2 as anomalies_v1_anomaly_feedback_calculation_service_pb2,
)
from acme.anomalies.v1 import anomaly_query_service_pb2 as anomalies_v1_anomaly_query_service_pb2
from acme.anomalies.v1 import anomaly_validation_service_pb2 as anomalies_v1_anomaly_validation_service_pb2
from acme.anomalies.v1 import detector_query_service_pb2 as anomalies_v1_detector_query_service_pb2
from acme.anomalies.v1 import detector_query_service_pb2_grpc as anomalies_v1_detector_query_service_pb2_grpc
from acme.anomalies.v1 import detector_validation_service_pb2 as anomalies_v1_detector_validation_service_pb2
from acme.anomalies.v1 import refs_pb2 as anomalies_v1_refs_pb2
from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.common.v1 import paging_pb2 as common_v1_paging_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.lineage.v1 import lineage_edge_validation_service_pb2 as lineage_v1_lineage_edge_validation_service_pb2

from acme_data.domains.anomalies.dependencies import Dependencies
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class DetectorQueryServicer(anomalies_v1_detector_query_service_pb2_grpc.DetectorQueryServiceServicer):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    @retry_transient
    async def BrowseDetectors(
        self, request: anomalies_v1_detector_query_service_pb2.BrowseDetectorsRequest, context: grpc.aio.ServicerContext,
    ) -> anomalies_v1_detector_query_service_pb2.BrowseDetectorsResponse:
        """Lists detectors a page at a time."""
        return await self.handle_browse_detectors(request)

    @rpc_errors
    @retry_transient
    async def CountDetectors(
        self, request: anomalies_v1_detector_query_service_pb2.CountDetectorsRequest, context: grpc.aio.ServicerContext,
    ) -> anomalies_v1_detector_query_service_pb2.CountDetectorsResponse:
        """Counts detectors by status."""
        return await self.handle_count_detectors(request)

    @rpc_errors
    @retry_transient
    async def FindDetectors(
        self, request: anomalies_v1_detector_query_service_pb2.FindDetectorsRequest, context: grpc.aio.ServicerContext,
    ) -> anomalies_v1_detector_query_service_pb2.FindDetectorsResponse:
        """Lists detectors a page at a time."""
        return await self.handle_find_detectors(request)

    @rpc_errors
    @retry_transient
    async def LookupDetector(
        self, request: anomalies_v1_detector_query_service_pb2.LookupDetectorRequest, context: grpc.aio.ServicerContext,
    ) -> anomalies_v1_detector_query_service_pb2.LookupDetectorResponse:
        """Returns a detector."""
        return await self.handle_lookup_detector(request)

    @rpc_errors
    @retry_transient
    async def PeekDetector(
        self, request: anomalies_v1_detector_query_service_pb2.PeekDetectorRequest, context: grpc.aio.ServicerContext,
    ) -> anomalies_v1_detector_query_service_pb2.PeekDetectorResponse:
        """Returns a detector."""
        return await self.handle_peek_detector(request)

    @rpc_errors
    @retry_transient
    async def SuggestDetectors(
        self, request: anomalies_v1_detector_query_service_pb2.SuggestDetectorsRequest, context: grpc.aio.ServicerContext,
    ) -> anomalies_v1_detector_query_service_pb2.SuggestDetectorsResponse:
        """Lists detectors a page at a time."""
        return await self.handle_suggest_detectors(request)

    @rpc_errors
    async def SummarizeDetectors(
        self, request: anomalies_v1_detector_query_service_pb2.SummarizeDetectorsRequest, context: grpc.aio.ServicerContext,
    ) -> anomalies_v1_detector_query_service_pb2.SummarizeDetectorsResponse:
        """Summarizes a detector."""
        return await self.handle_summarize_detectors(request)

    async def handle_browse_detectors(
        self,
        request: anomalies_v1_detector_query_service_pb2.BrowseDetectorsRequest
    ) -> anomalies_v1_detector_query_service_pb2.BrowseDetectorsResponse:
        """Lists detectors a page at a time."""
        deps = self.deps
        response = anomalies_v1_detector_query_service_pb2.BrowseDetectorsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('BrowseDetectors', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(request.context.tenant_id, 'BrowseDetectors', {'order_by': request.order_by})
            response_0 = anomalies_v1_detector_validation_service_pb2.ExplainDetectorDecisionResponse()
            outgoing_0 = anomalies_v1_detector_validation_service_pb2.ExplainDetectorDecisionRequest(
                context=request.context,
                detector=anomalies_v1_anomalies_pb2.Detector(
                    owner=identity_v1_refs_pb2.UserRef(
                        email=request.context.actor.email,
                        user_id=request.context.actor.user_id
                    )
                )
            )
            response_0 = await deps.clients.anomalies_detector_validation.ExplainDetectorDecision(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.detector.effective
            returned_0_0_part_0 = response.detectors.add()
            if returned_0_0.ListFields():
                returned_0_0_part_0.effective.MergeFrom(returned_0_0)
            return response

    async def handle_count_detectors(
        self,
        request: anomalies_v1_detector_query_service_pb2.CountDetectorsRequest
    ) -> anomalies_v1_detector_query_service_pb2.CountDetectorsResponse:
        """Counts detectors by status."""
        deps = self.deps
        response = anomalies_v1_detector_query_service_pb2.CountDetectorsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CountDetectors', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(request.context.tenant_id, 'CountDetectors', {'order_by': request.order_by})
            response_0 = lineage_v1_lineage_edge_validation_service_pb2.ScoreLineageEdgeResponse()
            outgoing_0 = lineage_v1_lineage_edge_validation_service_pb2.ScoreLineageEdgeRequest(
                context=request.context,
                details=lineage_v1_lineage_edge_validation_service_pb2.ScoreLineageEdgeRequest.Details(
                    destination=common_v1_address_pb2.PostalAddress(region=request.filter.region)
                )
            )
            response_0 = await deps.clients.lineage_lineage_edge_validation.ScoreLineageEdge(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.result.message = returned_0_0
            returned_0_1 = response_0.result.status
            if returned_0_1:
                response.result.status = returned_0_1
            return response

    async def handle_find_detectors(
        self,
        request: anomalies_v1_detector_query_service_pb2.FindDetectorsRequest
    ) -> anomalies_v1_detector_query_service_pb2.FindDetectorsResponse:
        """Lists detectors a page at a time."""
        deps = self.deps
        response = anomalies_v1_detector_query_service_pb2.FindDetectorsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('FindDetectors', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(request.context.tenant_id, 'FindDetectors', {'order_by': request.order_by})
            response_0 = anomalies_v1_anomaly_feedback_calculation_service_pb2.RecalculateAnomalyFeedbacksResponse()
            outgoing_0 = anomalies_v1_anomaly_feedback_calculation_service_pb2.RecalculateAnomalyFeedbacksRequest(
                context=request.context,
                details=anomalies_v1_anomaly_feedback_calculation_service_pb2.RecalculateAnomalyFeedbacksRequest.Details(
                    destination=common_v1_address_pb2.PostalAddress(region=request.filter.region)
                )
            )
            response_0 = await deps.clients.anomalies_anomaly_feedback_calculation.RecalculateAnomalyFeedbacks(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.details
            response.result.details.update(returned_0_0)
            return response

    async def handle_lookup_detector(
        self,
        request: anomalies_v1_detector_query_service_pb2.LookupDetectorRequest
    ) -> anomalies_v1_detector_query_service_pb2.LookupDetectorResponse:
        """Returns a detector."""
        deps = self.deps
        response = anomalies_v1_detector_query_service_pb2.LookupDetectorResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('LookupDetector', extra={'fields': {'locale': request.context.locale}})
            await deps.repository.audit(request.context.tenant_id, 'LookupDetector', {'locale': request.context.locale})
            echoed_0 = request.detector_id
            response.detector.detector_id = echoed_0
            return response

    async def handle_peek_detector(
        self,
        request: anomalies_v1_detector_query_service_pb2.PeekDetectorRequest
    ) -> anomalies_v1_detector_query_service_pb2.PeekDetectorResponse:
        """Returns a detector."""
        deps = self.deps
        response = anomalies_v1_detector_query_service_pb2.PeekDetectorResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('PeekDetector', extra={'fields': {'locale': request.context.locale}})
            await deps.repository.audit(request.context.tenant_id, 'PeekDetector', {'locale': request.context.locale})
            echoed_0 = request.detector_id
            response.detector.detector_id = echoed_0
            return response

    async def handle_suggest_detectors(
        self,
        request: anomalies_v1_detector_query_service_pb2.SuggestDetectorsRequest
    ) -> anomalies_v1_detector_query_service_pb2.SuggestDetectorsResponse:
        """Lists detectors a page at a time."""
        deps = self.deps
        response = anomalies_v1_detector_query_service_pb2.SuggestDetectorsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SuggestDetectors', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(request.context.tenant_id, 'SuggestDetectors', {'order_by': request.order_by})
            response_0 = anomalies_v1_anomaly_feedback_calculation_service_pb2.EstimateAnomalyFeedbackResponse()
            response_1 = anomalies_v1_anomaly_query_service_pb2.FindAnomaliesResponse()
            outgoing_0 = anomalies_v1_anomaly_feedback_calculation_service_pb2.EstimateAnomalyFeedbackRequest(
                anomaly_feedback=anomalies_v1_anomalies_pb2.AnomalyFeedback(
                    measurements=[
                        anomalies_v1_anomalies_pb2.AnomalyFeedbackMeasurement(observed_at=request.filter.created_after)
                    ]
                ),
                context=request.context,
                details=anomalies_v1_anomaly_feedback_calculation_service_pb2.EstimateAnomalyFeedbackRequest.Details(
                    destination=common_v1_address_pb2.PostalAddress(region=request.filter.region)
                )
            )
            response_0 = await deps.clients.anomalies_anomaly_feedback_calculation.EstimateAnomalyFeedback(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = anomalies_v1_anomaly_query_service_pb2.FindAnomaliesRequest(
                context=request.context,
                filter=anomalies_v1_anomaly_query_service_pb2.FindAnomaliesRequest.Filter(
                    created_after=request.filter.created_after,
                    owner_id=request.filter.owner_id,
                    query=request.filter.query
                ),
                page=common_v1_paging_pb2.PageRequest(page_size=request.page.page_size)
            )
            response_1 = cast(anomalies_v1_anomaly_query_service_pb2.FindAnomaliesResponse, await deps.bus.request(
                'acme.anomalies.v1.DetectorQueryService/SuggestDetectors/1', outgoing_1, deps.settings.timeout,
            ))
            returned_0_0 = response_0.result.correlation_id
            if returned_0_0:
                response.result.correlation_id = returned_0_0
            returned_1_0 = response_1.result.reference_ids
            response.result.reference_ids.extend(returned_1_0)
            returned_1_1 = response_1.result.message
            if returned_1_1:
                response.result.message = returned_1_1
            return response

    async def handle_summarize_detectors(
        self,
        request: anomalies_v1_detector_query_service_pb2.SummarizeDetectorsRequest
    ) -> anomalies_v1_detector_query_service_pb2.SummarizeDetectorsResponse:
        """Summarizes a detector."""
        deps = self.deps
        response = anomalies_v1_detector_query_service_pb2.SummarizeDetectorsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SummarizeDetectors', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'SummarizeDetectors', {'reason': request.reason})
            response_0 = anomalies_v1_anomaly_validation_service_pb2.ExplainAnomalyDecisionResponse()
            outgoing_0 = anomalies_v1_anomaly_validation_service_pb2.ExplainAnomalyDecisionRequest(
                anomaly=anomalies_v1_anomalies_pb2.Anomaly(
                    assignee=identity_v1_refs_pb2.UserRef(user_id=request.context.actor.user_id),
                    customer=anomalies_v1_refs_pb2.DetectorRef(detector_id=request.detector_id),
                    requester=common_v1_contact_pb2.ContactInfo(email=request.context.actor.email)
                ),
                context=request.context
            )
            response_0 = await deps.clients.anomalies_anomaly_validation.ExplainAnomalyDecision(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.outcome.message
            if returned_0_0:
                response.result.message = returned_0_0
            returned_0_1 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_1)
            echoed_0 = request.details.period
            response.period.CopyFrom(echoed_0)
            return response
