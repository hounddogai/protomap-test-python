"""Answers read-only questions about anomalies, for screens and reports."""

from __future__ import annotations

from collections.abc import AsyncIterator
from functools import partial
import logging

import grpc

from acme.anomalies.v1 import anomalies_pb2 as anomalies_v1_anomalies_pb2
from acme.anomalies.v1 import anomaly_query_service_pb2 as anomalies_v1_anomaly_query_service_pb2
from acme.anomalies.v1 import anomaly_query_service_pb2_grpc as anomalies_v1_anomaly_query_service_pb2_grpc
from acme.anomalies.v1 import anomaly_validation_service_pb2 as anomalies_v1_anomaly_validation_service_pb2
from acme.anomalies.v1 import detector_validation_service_pb2 as anomalies_v1_detector_validation_service_pb2
from acme.anomalies.v1 import refs_pb2 as anomalies_v1_refs_pb2
from acme.audit.v1 import audit_event_service_pb2 as audit_v1_audit_event_service_pb2
from acme.authorization.v1 import (
    access_policy_validation_service_pb2 as authorization_v1_access_policy_validation_service_pb2,
)
from acme.authorization.v1 import authorization_pb2 as authorization_v1_authorization_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.lineage.v1 import lineage_edge_validation_service_pb2 as lineage_v1_lineage_edge_validation_service_pb2
from acme.lineage.v1 import lineage_node_query_service_pb2 as lineage_v1_lineage_node_query_service_pb2
from acme.lineage.v1 import lineage_node_service_pb2 as lineage_v1_lineage_node_service_pb2
from acme.lineage.v1 import lineage_pb2 as lineage_v1_lineage_pb2

from acme_data.domains.anomalies import hooks
from acme_data.domains.anomalies.dependencies import Dependencies
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class AnomalyQueryServicer(anomalies_v1_anomaly_query_service_pb2_grpc.AnomalyQueryServiceServicer):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    @retry_transient
    async def BrowseAnomalies(
        self, request: anomalies_v1_anomaly_query_service_pb2.BrowseAnomaliesRequest, context: grpc.aio.ServicerContext,
    ) -> anomalies_v1_anomaly_query_service_pb2.BrowseAnomaliesResponse:
        """Lists anomalies a page at a time."""
        return await self.handle_browse_anomalies(request)

    @rpc_errors
    @retry_transient
    async def CountAnomalies(
        self, request: anomalies_v1_anomaly_query_service_pb2.CountAnomaliesRequest, context: grpc.aio.ServicerContext,
    ) -> anomalies_v1_anomaly_query_service_pb2.CountAnomaliesResponse:
        """Counts anomalies by status."""
        return await self.handle_count_anomalies(request)

    @stream_errors
    async def ExportAnomalies(
        self, request: anomalies_v1_anomaly_query_service_pb2.ExportAnomaliesRequest, context: grpc.aio.ServicerContext,
    ) -> AsyncIterator[anomalies_v1_anomaly_query_service_pb2.ExportAnomaliesResponse]:
        """Streams every matching anomaly."""
        response = await self.handle_export_anomalies(request)
        for item in messages((response,)):
            yield item

    @rpc_errors
    @retry_transient
    async def FindAnomalies(
        self, request: anomalies_v1_anomaly_query_service_pb2.FindAnomaliesRequest, context: grpc.aio.ServicerContext,
    ) -> anomalies_v1_anomaly_query_service_pb2.FindAnomaliesResponse:
        """Lists anomalies a page at a time."""
        return await self.handle_find_anomalies(request)

    @rpc_errors
    @retry_transient
    async def LookupAnomaly(
        self, request: anomalies_v1_anomaly_query_service_pb2.LookupAnomalyRequest, context: grpc.aio.ServicerContext,
    ) -> anomalies_v1_anomaly_query_service_pb2.LookupAnomalyResponse:
        """Returns an anomaly."""
        return await self.handle_lookup_anomaly(request)

    @rpc_errors
    @retry_transient
    async def PeekAnomaly(
        self, request: anomalies_v1_anomaly_query_service_pb2.PeekAnomalyRequest, context: grpc.aio.ServicerContext,
    ) -> anomalies_v1_anomaly_query_service_pb2.PeekAnomalyResponse:
        """Returns an anomaly."""
        return await self.handle_peek_anomaly(request)

    @rpc_errors
    @retry_transient
    async def ResolveAnomalies(
        self, request: anomalies_v1_anomaly_query_service_pb2.ResolveAnomaliesRequest, context: grpc.aio.ServicerContext,
    ) -> anomalies_v1_anomaly_query_service_pb2.ResolveAnomaliesResponse:
        """Returns several anomalies at once."""
        return await self.handle_resolve_anomalies(request)

    @rpc_errors
    async def SummarizeAnomalies(
        self, request: anomalies_v1_anomaly_query_service_pb2.SummarizeAnomaliesRequest, context: grpc.aio.ServicerContext,
    ) -> anomalies_v1_anomaly_query_service_pb2.SummarizeAnomaliesResponse:
        """Summarizes an anomaly."""
        return await self.handle_summarize_anomalies(request)

    async def handle_browse_anomalies(
        self,
        request: anomalies_v1_anomaly_query_service_pb2.BrowseAnomaliesRequest
    ) -> anomalies_v1_anomaly_query_service_pb2.BrowseAnomaliesResponse:
        """Lists anomalies a page at a time."""
        deps = self.deps
        response = anomalies_v1_anomaly_query_service_pb2.BrowseAnomaliesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('BrowseAnomalies', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(request.context.tenant_id, 'BrowseAnomalies', {'order_by': request.order_by})
            response_0 = anomalies_v1_anomaly_validation_service_pb2.CheckAnomalyEligibilityResponse()
            outgoing_0 = anomalies_v1_anomaly_validation_service_pb2.CheckAnomalyEligibilityRequest(
                anomaly=anomalies_v1_anomalies_pb2.Anomaly(
                    assignee=identity_v1_refs_pb2.UserRef(email=request.context.actor.email)
                ),
                context=request.context
            )
            response_0 = await deps.clients.anomalies_anomaly_validation.CheckAnomalyEligibility(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.anomaly.sla.paused_for
            returned_0_0_part_0 = response.anomalies.add()
            if returned_0_0.ListFields():
                returned_0_0_part_0.sla.paused_for.MergeFrom(returned_0_0)
            return response

    async def handle_count_anomalies(
        self,
        request: anomalies_v1_anomaly_query_service_pb2.CountAnomaliesRequest
    ) -> anomalies_v1_anomaly_query_service_pb2.CountAnomaliesResponse:
        """Counts anomalies by status."""
        deps = self.deps
        response = anomalies_v1_anomaly_query_service_pb2.CountAnomaliesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CountAnomalies', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(request.context.tenant_id, 'CountAnomalies', {'order_by': request.order_by})
            return response

    async def handle_export_anomalies(
        self,
        request: anomalies_v1_anomaly_query_service_pb2.ExportAnomaliesRequest
    ) -> anomalies_v1_anomaly_query_service_pb2.ExportAnomaliesResponse:
        """Streams every matching anomaly."""
        deps = self.deps
        response = anomalies_v1_anomaly_query_service_pb2.ExportAnomaliesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ExportAnomalies', extra={'fields': {'destination_uri': request.destination_uri}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ExportAnomalies',
                {'destination_uri': request.destination_uri}
            )
            response_0 = audit_v1_audit_event_service_pb2.WatchAuditEventsResponse()
            response_1 = lineage_v1_lineage_node_service_pb2.WatchLineageNodesResponse()
            outgoing_0 = audit_v1_audit_event_service_pb2.WatchAuditEventsRequest(
                context=request.context,
                filter=audit_v1_audit_event_service_pb2.WatchAuditEventsRequest.Filter(
                    labels=dict(request.filter.labels),
                    owner_id=request.filter.owner_id,
                    query=request.filter.query,
                    region=request.filter.region
                )
            )
            async for chunk_0 in deps.clients.audit_audit_event.WatchAuditEvents(
                outgoing_0,
                timeout=deps.settings.timeout
            ):
                response_0 = chunk_0
            outgoing_1 = lineage_v1_lineage_node_service_pb2.WatchLineageNodesRequest(
                context=request.context,
                filter=lineage_v1_lineage_node_service_pb2.WatchLineageNodesRequest.Filter(query=request.filter.query)
            )
            async for chunk_1 in deps.clients.lineage_lineage_node.WatchLineageNodes(
                outgoing_1,
                timeout=deps.settings.timeout
            ):
                response_1 = chunk_1
            return response

    async def handle_find_anomalies(
        self,
        request: anomalies_v1_anomaly_query_service_pb2.FindAnomaliesRequest
    ) -> anomalies_v1_anomaly_query_service_pb2.FindAnomaliesResponse:
        """Lists anomalies a page at a time."""
        deps = self.deps
        response = anomalies_v1_anomaly_query_service_pb2.FindAnomaliesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('FindAnomalies', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(request.context.tenant_id, 'FindAnomalies', {'order_by': request.order_by})
            response_0 = lineage_v1_lineage_edge_validation_service_pb2.ValidateLineageEdgeResponse()
            outgoing_0 = lineage_v1_lineage_edge_validation_service_pb2.ValidateLineageEdgeRequest(
                context=request.context,
                details=lineage_v1_lineage_edge_validation_service_pb2.ValidateLineageEdgeRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(email=request.context.actor.email),
                    locale=request.context.locale
                ),
                lineage_edge=lineage_v1_lineage_pb2.LineageEdge(
                    correlation_id=request.filter.owner_id,
                    measurements=[
                        lineage_v1_lineage_pb2.LineageEdgeMeasurement(observed_at=request.filter.created_after)
                    ]
                )
            )
            response_0 = await deps.clients.lineage_lineage_edge_validation.ValidateLineageEdge(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.outcome.status
            if returned_0_0:
                response.result.status = returned_0_0
            return response

    async def handle_lookup_anomaly(
        self,
        request: anomalies_v1_anomaly_query_service_pb2.LookupAnomalyRequest
    ) -> anomalies_v1_anomaly_query_service_pb2.LookupAnomalyResponse:
        """Returns an anomaly."""
        deps = self.deps
        response = anomalies_v1_anomaly_query_service_pb2.LookupAnomalyResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('LookupAnomaly', extra={'fields': {'domain': 'anomalies'}})
            await deps.repository.audit(request.context.tenant_id, 'LookupAnomaly', {})
            response_0 = anomalies_v1_anomaly_validation_service_pb2.CheckAnomalyEligibilityResponse()
            outgoing_0 = anomalies_v1_anomaly_validation_service_pb2.CheckAnomalyEligibilityRequest(
                anomaly=anomalies_v1_anomalies_pb2.Anomaly(anomaly_id=request.anomaly_id),
                context=request.context,
                details=anomalies_v1_anomaly_validation_service_pb2.CheckAnomalyEligibilityRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(email=request.context.actor.email)
                )
            )
            response_0 = await deps.clients.anomalies_anomaly_validation.CheckAnomalyEligibility(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_0)
            echoed_0 = request.anomaly_id
            response.anomaly.anomaly_id = echoed_0
            return response

    async def handle_peek_anomaly(
        self,
        request: anomalies_v1_anomaly_query_service_pb2.PeekAnomalyRequest
    ) -> anomalies_v1_anomaly_query_service_pb2.PeekAnomalyResponse:
        """Returns an anomaly."""
        deps = self.deps
        response = anomalies_v1_anomaly_query_service_pb2.PeekAnomalyResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('PeekAnomaly', extra={'fields': {'domain': 'anomalies'}})
            await deps.repository.audit(request.context.tenant_id, 'PeekAnomaly', {})
            response_0 = authorization_v1_access_policy_validation_service_pb2.PreviewAccessPolicyResponse()
            outgoing_0 = authorization_v1_access_policy_validation_service_pb2.PreviewAccessPolicyRequest(
                access_policy=authorization_v1_authorization_pb2.AccessPolicy(
                    owner=identity_v1_refs_pb2.UserRef(
                        email=request.context.actor.email,
                        user_id=request.context.actor.user_id
                    )
                ),
                context=request.context
            )
            response_0 = await deps.clients.authorization_access_policy_validation.PreviewAccessPolicy(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.access_policy.audit.created_at
            if returned_0_0.ListFields():
                response.anomaly.audit.created_at.MergeFrom(returned_0_0)
            returned_0_1 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_1)
            echoed_0 = request.anomaly_id
            response.anomaly.anomaly_id = echoed_0
            return response

    async def handle_resolve_anomalies(
        self,
        request: anomalies_v1_anomaly_query_service_pb2.ResolveAnomaliesRequest
    ) -> anomalies_v1_anomaly_query_service_pb2.ResolveAnomaliesResponse:
        """Returns several anomalies at once."""
        deps = self.deps
        response = anomalies_v1_anomaly_query_service_pb2.ResolveAnomaliesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ResolveAnomalies', extra={'fields': {'domain': 'anomalies'}})
            await deps.repository.audit(request.context.tenant_id, 'ResolveAnomalies', {})
            response_0 = anomalies_v1_detector_validation_service_pb2.ScoreDetectorResponse()
            response_1 = anomalies_v1_anomaly_validation_service_pb2.ScoreAnomalyResponse()
            outgoing_0 = anomalies_v1_detector_validation_service_pb2.ScoreDetectorRequest(
                context=request.context,
                detector=anomalies_v1_anomalies_pb2.Detector(
                    owner=identity_v1_refs_pb2.UserRef(email=request.context.actor.email)
                )
            )
            response_0 = await deps.clients.anomalies_detector_validation.ScoreDetector(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = anomalies_v1_anomaly_validation_service_pb2.ScoreAnomalyRequest(
                anomaly=anomalies_v1_anomalies_pb2.Anomaly(
                    audit=common_v1_audit_pb2.AuditInfo(created_by=response_0.detector.audit.created_by),
                    customer=anomalies_v1_refs_pb2.DetectorRef(detector_id=response_0.detector.detector_id)
                ),
                context=request.context
            )
            send_1 = partial(deps.clients.anomalies_anomaly_validation.ScoreAnomaly, timeout=deps.settings.timeout)
            response_1 = await send_1(outgoing_1)
            returned_0_0 = response_0.result.correlation_id
            if returned_0_0:
                response.result.correlation_id = returned_0_0
            returned_0_1 = response_0.result.details
            response.result.details.update(returned_0_1)
            returned_1_0 = response_1.anomaly.anomaly_id
            returned_1_0_part_0 = response.anomalies.add()
            if returned_1_0:
                returned_1_0_part_0.anomaly_id = returned_1_0
            return response

    async def handle_summarize_anomalies(
        self,
        request: anomalies_v1_anomaly_query_service_pb2.SummarizeAnomaliesRequest
    ) -> anomalies_v1_anomaly_query_service_pb2.SummarizeAnomaliesResponse:
        """Summarizes an anomaly."""
        deps = self.deps
        response = anomalies_v1_anomaly_query_service_pb2.SummarizeAnomaliesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SummarizeAnomalies', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'SummarizeAnomalies', {'reason': request.reason})
            response_0 = lineage_v1_lineage_node_query_service_pb2.SuggestLineageNodesResponse()
            outgoing_0 = lineage_v1_lineage_node_query_service_pb2.SuggestLineageNodesRequest(
                context=request.context,
                filter=lineage_v1_lineage_node_query_service_pb2.SuggestLineageNodesRequest.Filter(
                    labels=dict(request.details.filters),
                    owner_id=request.anomaly_id
                )
            )
            response_0 = await hooks.anomaly_query_summarize_anomalies0(
                deps.clients.lineage_lineage_node_query,
                outgoing_0,
                deps.settings.timeout
            )
            returned_0_0 = response_0.result.details
            response.result.details.update(returned_0_0)
            echoed_0 = request.details.period
            response.period.CopyFrom(echoed_0)
            return response
