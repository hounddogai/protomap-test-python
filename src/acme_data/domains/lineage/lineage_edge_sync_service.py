"""Keeps lineage edges in step with the systems of record in other regions."""

from __future__ import annotations

from collections.abc import AsyncIterator
from collections.abc import Awaitable
from collections.abc import Callable
from dataclasses import dataclass
from functools import partial
from typing import Any
from typing import cast
import asyncio
import logging

from google.protobuf.any_pb2 import Any as AnyMessage
from google.protobuf.json_format import MessageToJson
from google.protobuf.json_format import Parse
import grpc

from acme.authorization.v1 import (
    access_policy_validation_service_pb2 as authorization_v1_access_policy_validation_service_pb2,
)
from acme.authorization.v1 import authorization_pb2 as authorization_v1_authorization_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.featureflags.v1 import (
    feature_flag_validation_service_pb2 as featureflags_v1_feature_flag_validation_service_pb2,
)
from acme.featureflags.v1 import featureflags_pb2 as featureflags_v1_featureflags_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.keymanagement.v1 import crypto_key_query_service_pb2 as keymanagement_v1_crypto_key_query_service_pb2
from acme.lineage.v1 import lineage_edge_import_service_pb2 as lineage_v1_lineage_edge_import_service_pb2
from acme.lineage.v1 import lineage_edge_sync_service_pb2 as lineage_v1_lineage_edge_sync_service_pb2
from acme.lineage.v1 import lineage_edge_sync_service_pb2_grpc as lineage_v1_lineage_edge_sync_service_pb2_grpc
from acme.lineage.v1 import lineage_edge_validation_service_pb2 as lineage_v1_lineage_edge_validation_service_pb2
from acme.lineage.v1 import lineage_node_sync_service_pb2 as lineage_v1_lineage_node_sync_service_pb2
from acme.lineage.v1 import lineage_pb2 as lineage_v1_lineage_pb2
from acme.metrics.v1 import metric_series_notification_service_pb2 as metrics_v1_metric_series_notification_service_pb2
from acme.notifications.v1 import (
    notification_validation_service_pb2 as notifications_v1_notification_validation_service_pb2,
)
from acme.notifications.v1 import notifications_pb2 as notifications_v1_notifications_pb2
from acme.pipelines.v1 import pipeline_service_pb2 as pipelines_v1_pipeline_service_pb2

from acme_data.domains.lineage.adapters import LineageEdgeSyncPushLineageEdge1Adapter
from acme_data.domains.lineage.adapters import LineageEdgeSyncPushLineageEdge1Port
from acme_data.domains.lineage.dependencies import Dependencies
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import run_steps
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_id
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


@dataclass(slots=True)
class LineageEdgeSyncServicer(lineage_v1_lineage_edge_sync_service_pb2_grpc.LineageEdgeSyncServiceServicer):
    deps: Dependencies

    @rpc_errors
    @retry_transient
    async def ListLineageEdgeConflicts(
        self, request: lineage_v1_lineage_edge_sync_service_pb2.ListLineageEdgeConflictsRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_lineage_edge_sync_service_pb2.ListLineageEdgeConflictsResponse:
        """Lists lineage edges a page at a time."""
        return await self.handle_list_lineage_edge_conflicts(request)

    @rpc_errors
    async def PushLineageEdge(
        self, request: lineage_v1_lineage_edge_sync_service_pb2.PushLineageEdgeRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_lineage_edge_sync_service_pb2.PushLineageEdgeResponse:
        """Pushs a lineage edge."""
        return await self.handle_push_lineage_edge(request)

    @rpc_errors
    async def ReconcileLineageEdges(
        self, request: lineage_v1_lineage_edge_sync_service_pb2.ReconcileLineageEdgesRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_lineage_edge_sync_service_pb2.ReconcileLineageEdgesResponse:
        """Reconciles a lineage edge."""
        return await self.handle_reconcile_lineage_edges(request)

    @rpc_errors
    async def ResolveLineageEdgeConflict(
        self, request: lineage_v1_lineage_edge_sync_service_pb2.ResolveLineageEdgeConflictRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_lineage_edge_sync_service_pb2.ResolveLineageEdgeConflictResponse:
        """Resolves a lineage edge."""
        return await self.handle_resolve_lineage_edge_conflict(request)

    @stream_errors
    async def StreamLineageEdgeChanges(
        self, requests: AsyncIterator[
            lineage_v1_lineage_edge_sync_service_pb2.StreamLineageEdgeChangesRequest
        ], context: grpc.aio.ServicerContext,
    ) -> AsyncIterator[lineage_v1_lineage_edge_sync_service_pb2.StreamLineageEdgeChangesResponse]:
        """Exchanges changes of lineage edges with a peer."""
        async for request in requests:
            yield await self.handle_stream_lineage_edge_changes(request)

    @rpc_errors
    async def SyncLineageEdges(
        self, request: lineage_v1_lineage_edge_sync_service_pb2.SyncLineageEdgesRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_lineage_edge_sync_service_pb2.SyncLineageEdgesResponse:
        """Syncs a lineage edge."""
        return await self.handle_sync_lineage_edges(request)

    async def handle_list_lineage_edge_conflicts(
        self,
        request: lineage_v1_lineage_edge_sync_service_pb2.ListLineageEdgeConflictsRequest
    ) -> lineage_v1_lineage_edge_sync_service_pb2.ListLineageEdgeConflictsResponse:
        """Lists lineage edges a page at a time."""
        deps = self.deps
        response = lineage_v1_lineage_edge_sync_service_pb2.ListLineageEdgeConflictsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ListLineageEdgeConflicts', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ListLineageEdgeConflicts',
                {'order_by': request.order_by}
            )
            return response

    async def handle_push_lineage_edge(
        self,
        request: lineage_v1_lineage_edge_sync_service_pb2.PushLineageEdgeRequest
    ) -> lineage_v1_lineage_edge_sync_service_pb2.PushLineageEdgeResponse:
        """Pushs a lineage edge."""
        deps = self.deps
        response = lineage_v1_lineage_edge_sync_service_pb2.PushLineageEdgeResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('PushLineageEdge', extra={'fields': {'checksum': request.details.checksum}})
            await deps.repository.audit(
                request.context.tenant_id,
                'PushLineageEdge',
                {'checksum': request.details.checksum}
            )
            await deps.repository.save_lineage_edge(request.context.tenant_id, request.lineage_edge)
            response_0 = metrics_v1_metric_series_notification_service_pb2.SendMetricSeriesTestNoticeResponse()
            response_1 = lineage_v1_lineage_edge_import_service_pb2.CancelLineageEdgeImportResponse()
            response_2 = keymanagement_v1_crypto_key_query_service_pb2.SuggestCryptoKeysResponse()
            response_3 = pipelines_v1_pipeline_service_pb2.ClonePipelineResponse()
            outgoing_0 = metrics_v1_metric_series_notification_service_pb2.SendMetricSeriesTestNoticeRequest()
            outgoing_0.context.CopyFrom(request.context)
            outgoing_0.reason = request.reason
            outgoing_0.annotations.update(dict(request.annotations))
            outgoing_0.context.tenant_id = tenant_id.get()
            response_0 = await deps.clients.metrics_metric_series_notification.SendMetricSeriesTestNotice(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = lineage_v1_lineage_edge_import_service_pb2.CancelLineageEdgeImportRequest(
                annotations=dict(request.annotations),
                context=request.context,
                details=lineage_v1_lineage_edge_import_service_pb2.CancelLineageEdgeImportRequest.Details(
                    new_owner=identity_v1_refs_pb2.UserRef(
                        display_name=response_0.metric_series.owner.display_name,
                        user_id=response_0.metric_series.owner.user_id
                    ),
                    notify_contact=common_v1_contact_pb2.ContactInfo(email=response_0.metric_series.owner.email)
                ),
                lineage_edge_id=request.lineage_edge_id
            )
            port_1: LineageEdgeSyncPushLineageEdge1Port = LineageEdgeSyncPushLineageEdge1Adapter(
                deps.clients.lineage_lineage_edge_import,
                deps.settings.timeout
            )
            response_1 = await port_1.execute(outgoing_1)
            outgoing_2 = keymanagement_v1_crypto_key_query_service_pb2.SuggestCryptoKeysRequest(
                context=request.context,
                filter=keymanagement_v1_crypto_key_query_service_pb2.SuggestCryptoKeysRequest.Filter(
                    created_after=response_1.lineage_edge.occurred_at,
                    region=response_0.metric_series.address.region
                )
            )
            steps_2 = [
                partial(
                    deps.clients.keymanagement_crypto_key_query.SuggestCryptoKeys,
                    outgoing_2,
                    timeout=deps.settings.timeout
                )
            ]
            results_2 = await run_steps(steps_2)
            response_2 = results_2[-1]
            outgoing_3 = pipelines_v1_pipeline_service_pb2.ClonePipelineRequest()
            outgoing_3.context.CopyFrom(request.context)
            if response_0.metric_series.WhichOneof('locator') == 'address':
                outgoing_3.pipeline.location.locality = response_0.metric_series.address.locality
            if response_0.metric_series.WhichOneof('locator') == 'address':
                outgoing_3.pipeline.location.region = response_0.metric_series.address.region
            outgoing_3.pipeline.organizer.user_id = response_0.metric_series.owner.user_id
            outgoing_3.pipeline.audit.etag = response_0.metric_series.audit.etag
            response_3 = await deps.clients.pipelines_pipeline.ClonePipeline(outgoing_3, timeout=deps.settings.timeout)
            returned_0_0 = response_0.outcome.next_steps
            response.outcome.next_steps.extend(returned_0_0)
            returned_0_1 = response_0.outcome.effective_at
            if returned_0_1.ListFields():
                response.outcome.effective_at.MergeFrom(returned_0_1)
            returned_1_0 = response_1.lineage_edge.lineage_edge_id
            if returned_1_0:
                response.lineage_edge.lineage_edge_id = returned_1_0
            returned_1_1 = response_1.lineage_edge.subject
            if returned_1_1.ListFields():
                response.lineage_edge.subject.MergeFrom(returned_1_1)
            returned_2_0 = response_2.result.correlation_id
            if returned_2_0:
                response.result.correlation_id = returned_2_0
            returned_3_0 = response_3.result.status
            if returned_3_0:
                response.outcome.status = returned_3_0
            echoed_0 = request.lineage_edge.source
            response.lineage_edge.source = echoed_0
            echoed_1 = request.lineage_edge.correlation_id
            response.lineage_edge.correlation_id = echoed_1
            return response

    async def handle_reconcile_lineage_edges(
        self,
        request: lineage_v1_lineage_edge_sync_service_pb2.ReconcileLineageEdgesRequest
    ) -> lineage_v1_lineage_edge_sync_service_pb2.ReconcileLineageEdgesResponse:
        """Reconciles a lineage edge."""
        deps = self.deps
        response = lineage_v1_lineage_edge_sync_service_pb2.ReconcileLineageEdgesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ReconcileLineageEdges', extra={'fields': {'checksum': request.details.checksum}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ReconcileLineageEdges',
                {'checksum': request.details.checksum}
            )
            await deps.repository.save_lineage_edge(request.context.tenant_id, request.lineage_edge)
            response_0 = featureflags_v1_feature_flag_validation_service_pb2.PreviewFeatureFlagResponse()
            response_1 = notifications_v1_notification_validation_service_pb2.ScoreNotificationResponse()
            outgoing_0 = featureflags_v1_feature_flag_validation_service_pb2.PreviewFeatureFlagRequest(
                context=request.context,
                feature_flag=featureflags_v1_featureflags_pb2.FeatureFlag(
                    block=featureflags_v1_featureflags_pb2.FeatureFlagBlockAction(reason=request.reason)
                )
            )
            response_0 = cast(featureflags_v1_feature_flag_validation_service_pb2.PreviewFeatureFlagResponse, await deps.bus.request(
                'acme.lineage.v1.LineageEdgeSyncService/ReconcileLineageEdges/0', outgoing_0, deps.settings.timeout,
            ))
            outgoing_1 = notifications_v1_notification_validation_service_pb2.ScoreNotificationRequest(
                context=request.context,
                notification=notifications_v1_notifications_pb2.Notification(
                    assignee=identity_v1_refs_pb2.UserRef(user_id=response_0.feature_flag.owner.user_id),
                    comments=[
                        notifications_v1_notifications_pb2.NotificationComment(
                            created_at=response_0.feature_flag.audit.created_at
                        )
                    ]
                )
            )
            response_1 = await deps.clients.notifications_notification_validation.ScoreNotification(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.outcome.status
            if returned_0_0:
                response.result.status = returned_0_0
            returned_0_1 = response_0.result.correlation_id
            if returned_0_1:
                response.lineage_edge.correlation_id = returned_0_1
            returned_1_0 = response_1.notification.customer.display_name
            if returned_1_0:
                response.lineage_edge.subject.display_name = returned_1_0
            returned_1_1 = response_1.result.status
            if returned_1_1:
                response.result.status = returned_1_1
            echoed_0 = request.lineage_edge_id
            response.lineage_edge.lineage_edge_id = echoed_0
            echoed_1 = request.lineage_edge.sequence
            response.lineage_edge.sequence = echoed_1
            return response

    async def handle_resolve_lineage_edge_conflict(
        self,
        request: lineage_v1_lineage_edge_sync_service_pb2.ResolveLineageEdgeConflictRequest
    ) -> lineage_v1_lineage_edge_sync_service_pb2.ResolveLineageEdgeConflictResponse:
        """Resolves a lineage edge."""
        deps = self.deps
        response = lineage_v1_lineage_edge_sync_service_pb2.ResolveLineageEdgeConflictResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ResolveLineageEdgeConflict', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ResolveLineageEdgeConflict',
                {'reason': request.reason}
            )
            await deps.repository.save_lineage_edge(request.context.tenant_id, request.lineage_edge)
            response_0 = lineage_v1_lineage_edge_validation_service_pb2.ExplainLineageEdgeDecisionResponse()
            response_1 = lineage_v1_lineage_node_sync_service_pb2.ReconcileLineageNodesResponse()
            for item_0 in request.lineage_edge.measurements:
                outgoing_0 = lineage_v1_lineage_edge_validation_service_pb2.ExplainLineageEdgeDecisionRequest(
                    context=request.context,
                    lineage_edge=lineage_v1_lineage_pb2.LineageEdge(
                        measurements=[
                            lineage_v1_lineage_pb2.LineageEdgeMeasurement(
                                metric=item_0.metric,
                                observed_at=item_0.observed_at,
                                unit=item_0.unit,
                                value=item_0.value
                            )
                        ]
                    )
                )
                response_0 = await deps.clients.lineage_lineage_edge_validation.ExplainLineageEdgeDecision(
                    outgoing_0,
                    timeout=deps.settings.timeout
                )
            fields_1: dict[str, Any] = {
                'context': request.context,
                'lineage_node': {
                    'children': [
                        {'children': [{'manager': {'display_name': response_0.lineage_edge.subject.display_name}}]}
                    ]
                }
            }
            outgoing_1 = lineage_v1_lineage_node_sync_service_pb2.ReconcileLineageNodesRequest(**fields_1)
            response_1 = await deps.clients.lineage_lineage_node_sync.ReconcileLineageNodes(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_1_0 = response_1.lineage_node.attributes
            response.lineage_edge.attributes.update(returned_1_0)
            returned_1_1 = response_1.result.message
            if returned_1_1:
                response.outcome.message = returned_1_1
            echoed_0 = request.lineage_edge_id
            response.lineage_edge.lineage_edge_id = echoed_0
            echoed_1 = request.lineage_edge.correlation_id
            response.lineage_edge.correlation_id = echoed_1
            return response

    async def handle_stream_lineage_edge_changes(
        self,
        request: lineage_v1_lineage_edge_sync_service_pb2.StreamLineageEdgeChangesRequest
    ) -> lineage_v1_lineage_edge_sync_service_pb2.StreamLineageEdgeChangesResponse:
        """Exchanges changes of lineage edges with a peer."""
        deps = self.deps
        response = lineage_v1_lineage_edge_sync_service_pb2.StreamLineageEdgeChangesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('StreamLineageEdgeChanges', extra={'fields': {'cursor': request.cursor}})
            await deps.repository.audit(
                request.context.tenant_id,
                'StreamLineageEdgeChanges',
                {'cursor': request.cursor}
            )
            if request.WhichOneof('frame') == 'change':
                await deps.repository.save_lineage_edge(request.context.tenant_id, request.change)
            response_0 = lineage_v1_lineage_edge_validation_service_pb2.CheckLineageEdgeEligibilityResponse()
            response_1 = authorization_v1_access_policy_validation_service_pb2.NormalizeAccessPolicyResponse()
            requests_0: list[lineage_v1_lineage_edge_validation_service_pb2.CheckLineageEdgeEligibilityRequest] = []
            for item_0 in request.change.measurements:
                outgoing_0 = lineage_v1_lineage_edge_validation_service_pb2.CheckLineageEdgeEligibilityRequest(
                    context=request.context,
                    lineage_edge=lineage_v1_lineage_pb2.LineageEdge(
                        measurements=[
                            lineage_v1_lineage_pb2.LineageEdgeMeasurement(
                                metric=item_0.metric,
                                observed_at=item_0.observed_at,
                                unit=item_0.unit,
                                value=item_0.value
                            )
                        ]
                    )
                )
                requests_0.append(outgoing_0)
            replies_0 = await asyncio.gather(*(
                deps.clients.lineage_lineage_edge_validation.CheckLineageEdgeEligibility(
                    entry,
                    timeout=deps.settings.timeout
                ) for entry in requests_0
            ))
            if replies_0:
                response_0 = replies_0[-1]
            outgoing_1 = authorization_v1_access_policy_validation_service_pb2.NormalizeAccessPolicyRequest(
                access_policy=authorization_v1_authorization_pb2.AccessPolicy(
                    owner=identity_v1_refs_pb2.UserRef(display_name=response_0.lineage_edge.subject.display_name),
                    priority=response_0.lineage_edge.subject.priority
                ),
                context=request.context
            )
            document_1 = MessageToJson(outgoing_1, preserving_proto_field_name=True)
            outgoing_1 = Parse(
                document_1,
                authorization_v1_access_policy_validation_service_pb2.NormalizeAccessPolicyRequest()
            )
            response_1 = await deps.clients.authorization_access_policy_validation.NormalizeAccessPolicy(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_1_0 = response_1.result.correlation_id
            if returned_1_0:
                response.result.correlation_id = returned_1_0
            echoed_0 = request.ack.sequence
            response.sequence = echoed_0
            echoed_1 = request.change.sequence
            response.lineage_edge.sequence = echoed_1
            return response

    async def handle_sync_lineage_edges(
        self,
        request: lineage_v1_lineage_edge_sync_service_pb2.SyncLineageEdgesRequest
    ) -> lineage_v1_lineage_edge_sync_service_pb2.SyncLineageEdgesResponse:
        """Syncs a lineage edge."""
        deps = self.deps
        response = lineage_v1_lineage_edge_sync_service_pb2.SyncLineageEdgesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SyncLineageEdges', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'SyncLineageEdges', {'reason': request.reason})
            await deps.repository.save_lineage_edge(request.context.tenant_id, request.lineage_edge)
            response_0 = lineage_v1_lineage_edge_validation_service_pb2.ExplainLineageEdgeDecisionResponse()
            response_1 = lineage_v1_lineage_node_sync_service_pb2.ResolveLineageNodeConflictResponse()
            callbacks_0: list[
                Callable[
                    [],
                    Awaitable[lineage_v1_lineage_edge_validation_service_pb2.ExplainLineageEdgeDecisionResponse]
                ]
            ] = []
            for item_0 in request.lineage_edge.measurements:
                outgoing_0 = lineage_v1_lineage_edge_validation_service_pb2.ExplainLineageEdgeDecisionRequest(
                    context=request.context,
                    lineage_edge=lineage_v1_lineage_pb2.LineageEdge(
                        measurements=[
                            lineage_v1_lineage_pb2.LineageEdgeMeasurement(
                                observed_at=item_0.observed_at,
                                unit=item_0.unit,
                                value=item_0.value
                            )
                        ]
                    )
                )
                async def send_0(
                    payload: lineage_v1_lineage_edge_validation_service_pb2.ExplainLineageEdgeDecisionRequest = outgoing_0
                ) -> lineage_v1_lineage_edge_validation_service_pb2.ExplainLineageEdgeDecisionResponse:
                    return await deps.clients.lineage_lineage_edge_validation.ExplainLineageEdgeDecision(
                        payload,
                        timeout=deps.settings.timeout
                    )
                callbacks_0.append(send_0)
            for callback_0 in callbacks_0:
                response_0 = await callback_0()
            outgoing_1 = lineage_v1_lineage_node_sync_service_pb2.ResolveLineageNodeConflictRequest(
                context=request.context,
                lineage_node=lineage_v1_lineage_pb2.LineageNode(
                    children=[
                        lineage_v1_lineage_pb2.LineageNode(
                            children=[
                                lineage_v1_lineage_pb2.LineageNode(
                                    children=[
                                        lineage_v1_lineage_pb2.LineageNode(
                                            attributes=dict(response_0.lineage_edge.attributes)
                                        )
                                    ]
                                )
                            ]
                        )
                    ]
                )
            )
            envelope_1 = AnyMessage()
            envelope_1.Pack(outgoing_1)
            outgoing_1 = lineage_v1_lineage_node_sync_service_pb2.ResolveLineageNodeConflictRequest()
            if not envelope_1.Unpack(outgoing_1):
                raise ValueError("partner envelope contains the wrong request type")
            response_1 = await deps.clients.lineage_lineage_node_sync.ResolveLineageNodeConflict(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_1_0 = response_1.outcome.message
            if returned_1_0:
                response.outcome.message = returned_1_0
            echoed_0 = request.lineage_edge_id
            response.lineage_edge.lineage_edge_id = echoed_0
            echoed_1 = request.lineage_edge.source
            response.lineage_edge.source = echoed_1
            return response
