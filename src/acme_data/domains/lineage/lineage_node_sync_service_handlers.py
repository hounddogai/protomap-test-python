"""Reusable transport mixin for LineageNodeSyncService."""

from __future__ import annotations

from collections.abc import AsyncIterator
from functools import partial
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

from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.customers.v1 import (
    customer_segment_calculation_service_pb2 as customers_v1_customer_segment_calculation_service_pb2,
)
from acme.customers.v1 import (
    customer_segment_validation_service_pb2 as customers_v1_customer_segment_validation_service_pb2,
)
from acme.customers.v1 import customers_pb2 as customers_v1_customers_pb2
from acme.customers.v1 import household_query_service_pb2 as customers_v1_household_query_service_pb2
from acme.deliveries.v1 import delivery_service_pb2 as deliveries_v1_delivery_service_pb2
from acme.forecasting.v1 import (
    forecast_model_validation_service_pb2 as forecasting_v1_forecast_model_validation_service_pb2,
)
from acme.forecasting.v1 import forecasting_pb2 as forecasting_v1_forecasting_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.identity.v1 import user_query_service_pb2 as identity_v1_user_query_service_pb2
from acme.ledger.v1 import ledger_account_validation_service_pb2 as ledger_v1_ledger_account_validation_service_pb2
from acme.ledger.v1 import ledger_pb2 as ledger_v1_ledger_pb2
from acme.ledger.v1 import refs_pb2 as ledger_v1_refs_pb2
from acme.lineage.v1 import impact_validation_service_pb2 as lineage_v1_impact_validation_service_pb2
from acme.lineage.v1 import lineage_node_query_service_pb2 as lineage_v1_lineage_node_query_service_pb2
from acme.lineage.v1 import lineage_node_sync_service_pb2 as lineage_v1_lineage_node_sync_service_pb2
from acme.lineage.v1 import lineage_pb2 as lineage_v1_lineage_pb2
from acme.metrics.v1 import dashboard_validation_service_pb2 as metrics_v1_dashboard_validation_service_pb2
from acme.modelregistry.v1 import (
    registered_model_query_service_pb2 as modelregistry_v1_registered_model_query_service_pb2,
)
from acme.pipelines.v1 import pipeline_run_validation_service_pb2 as pipelines_v1_pipeline_run_validation_service_pb2
from acme.recommendations.v1 import recommendation_set_service_pb2 as recommendations_v1_recommendation_set_service_pb2
from acme.returns.v1 import return_request_query_service_pb2 as returns_v1_return_request_query_service_pb2

from acme_data.domains.lineage.dependencies import Dependencies
from acme_data.domains.lineage.models import LineageNodeSyncResolveLineageNodeConflict1Command
from acme_data.domains.lineage.models import to_lineage_node_sync_resolve_lineage_node_conflict1_command
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import run_steps
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class LineageNodeSyncServicerHandlers:
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    @retry_transient
    async def GetLineageNodeSyncState(
        self, request: lineage_v1_lineage_node_sync_service_pb2.GetLineageNodeSyncStateRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_lineage_node_sync_service_pb2.GetLineageNodeSyncStateResponse:
        """Returns a lineage node."""
        return await self.handle_get_lineage_node_sync_state(request)

    @rpc_errors
    @retry_transient
    async def ListLineageNodeConflicts(
        self, request: lineage_v1_lineage_node_sync_service_pb2.ListLineageNodeConflictsRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_lineage_node_sync_service_pb2.ListLineageNodeConflictsResponse:
        """Lists lineage nodes a page at a time."""
        return await self.handle_list_lineage_node_conflicts(request)

    @rpc_errors
    async def PullLineageNodes(
        self, request: lineage_v1_lineage_node_sync_service_pb2.PullLineageNodesRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_lineage_node_sync_service_pb2.PullLineageNodesResponse:
        """Pulls a lineage node."""
        return await self.handle_pull_lineage_nodes(request)

    @rpc_errors
    async def PushLineageNode(
        self, request: lineage_v1_lineage_node_sync_service_pb2.PushLineageNodeRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_lineage_node_sync_service_pb2.PushLineageNodeResponse:
        """Pushs a lineage node."""
        return await self.handle_push_lineage_node(request)

    @rpc_errors
    async def ReconcileLineageNodes(
        self, request: lineage_v1_lineage_node_sync_service_pb2.ReconcileLineageNodesRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_lineage_node_sync_service_pb2.ReconcileLineageNodesResponse:
        """Reconciles a lineage node."""
        return await self.handle_reconcile_lineage_nodes(request)

    @rpc_errors
    async def ResolveLineageNodeConflict(
        self, request: lineage_v1_lineage_node_sync_service_pb2.ResolveLineageNodeConflictRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_lineage_node_sync_service_pb2.ResolveLineageNodeConflictResponse:
        """Resolves a lineage node."""
        return await self.handle_resolve_lineage_node_conflict(request)

    @stream_errors
    async def StreamLineageNodeChanges(
        self, requests: AsyncIterator[
            lineage_v1_lineage_node_sync_service_pb2.StreamLineageNodeChangesRequest
        ], context: grpc.aio.ServicerContext,
    ) -> AsyncIterator[lineage_v1_lineage_node_sync_service_pb2.StreamLineageNodeChangesResponse]:
        """Exchanges changes of lineage nodes with a peer."""
        async for request in requests:
            yield await self.handle_stream_lineage_node_changes(request)

    @rpc_errors
    async def SyncLineageNodes(
        self, request: lineage_v1_lineage_node_sync_service_pb2.SyncLineageNodesRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_lineage_node_sync_service_pb2.SyncLineageNodesResponse:
        """Syncs a lineage node."""
        return await self.handle_sync_lineage_nodes(request)

    async def handle_get_lineage_node_sync_state(
        self,
        request: lineage_v1_lineage_node_sync_service_pb2.GetLineageNodeSyncStateRequest
    ) -> lineage_v1_lineage_node_sync_service_pb2.GetLineageNodeSyncStateResponse:
        """Returns a lineage node."""
        deps = self.deps
        response = lineage_v1_lineage_node_sync_service_pb2.GetLineageNodeSyncStateResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('GetLineageNodeSyncState', extra={'fields': {'domain': 'lineage'}})
            await deps.repository.audit(request.context.tenant_id, 'GetLineageNodeSyncState', {})
            response_0 = metrics_v1_dashboard_validation_service_pb2.CheckDashboardEligibilityResponse()
            response_1 = ledger_v1_ledger_account_validation_service_pb2.NormalizeLedgerAccountResponse()
            outgoing_0 = metrics_v1_dashboard_validation_service_pb2.CheckDashboardEligibilityRequest(
                context=request.context,
                details=metrics_v1_dashboard_validation_service_pb2.CheckDashboardEligibilityRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(email=request.context.actor.email)
                )
            )
            response_0 = await deps.clients.metrics_dashboard_validation.CheckDashboardEligibility(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = ledger_v1_ledger_account_validation_service_pb2.NormalizeLedgerAccountRequest(
                context=request.context,
                ledger_account=ledger_v1_ledger_pb2.LedgerAccount(
                    holder=ledger_v1_refs_pb2.PostingBatchRef(
                        display_name=response_0.dashboard.counterparty.display_name
                    )
                )
            )
            steps_1 = [
                partial(
                    deps.clients.ledger_ledger_account_validation.NormalizeLedgerAccount,
                    outgoing_1,
                    timeout=deps.settings.timeout
                )
            ]
            results_1 = await run_steps(steps_1)
            response_1 = results_1[-1]
            returned_0_0 = response_0.dashboard.billing_address.locality
            returned_0_0_part_1 = response.lineage_node.children.add()
            if returned_0_0:
                returned_0_0_part_1.location.locality = returned_0_0
            returned_1_0 = response_1.ledger_account.audit.etag
            if returned_1_0:
                response.lineage_node.audit.etag = returned_1_0
            returned_1_1 = response_1.ledger_account.contact.email
            returned_1_1_part_1 = response.lineage_node.children.add()
            returned_1_1_part_2 = returned_1_1_part_1.children.add()
            if returned_1_1:
                returned_1_1_part_2.manager.email = returned_1_1
            echoed_0 = request.lineage_node_id
            response.lineage_node.lineage_node_id = echoed_0
            return response

    async def handle_list_lineage_node_conflicts(
        self,
        request: lineage_v1_lineage_node_sync_service_pb2.ListLineageNodeConflictsRequest
    ) -> lineage_v1_lineage_node_sync_service_pb2.ListLineageNodeConflictsResponse:
        """Lists lineage nodes a page at a time."""
        deps = self.deps
        response = lineage_v1_lineage_node_sync_service_pb2.ListLineageNodeConflictsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ListLineageNodeConflicts', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ListLineageNodeConflicts',
                {'order_by': request.order_by}
            )
            response_0 = lineage_v1_impact_validation_service_pb2.CheckImpactEligibilityResponse()
            outgoing_0 = lineage_v1_impact_validation_service_pb2.CheckImpactEligibilityRequest(
                context=request.context,
                impact=lineage_v1_lineage_pb2.Impact(
                    requester=common_v1_contact_pb2.ContactInfo(email=request.context.actor.email)
                )
            )
            response_0 = await deps.clients.lineage_impact_validation.CheckImpactEligibility(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.impact.audit.created_by
            returned_0_0_part_0 = response.lineage_nodes.add()
            returned_0_0_part_1 = returned_0_0_part_0.children.add()
            if returned_0_0:
                returned_0_0_part_1.audit.created_by = returned_0_0
            returned_0_1 = response_0.impact.customer.email
            returned_0_1_part_0 = response.lineage_nodes.add()
            if returned_0_1:
                returned_0_1_part_0.manager.email = returned_0_1
            return response

    async def handle_pull_lineage_nodes(
        self,
        request: lineage_v1_lineage_node_sync_service_pb2.PullLineageNodesRequest
    ) -> lineage_v1_lineage_node_sync_service_pb2.PullLineageNodesResponse:
        """Pulls a lineage node."""
        deps = self.deps
        response = lineage_v1_lineage_node_sync_service_pb2.PullLineageNodesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('PullLineageNodes', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'PullLineageNodes', {'reason': request.reason})
            await deps.repository.save_lineage_node(request.context.tenant_id, request.lineage_node)
            response_0 = customers_v1_customer_segment_validation_service_pb2.CheckCustomerSegmentEligibilityResponse()
            response_1 = returns_v1_return_request_query_service_pb2.BrowseReturnRequestsResponse()
            outgoing_0 = customers_v1_customer_segment_validation_service_pb2.CheckCustomerSegmentEligibilityRequest(
                context=request.context,
                customer_segment=customers_v1_customers_pb2.CustomerSegment(
                    audit=common_v1_audit_pb2.AuditInfo(
                        created_at=request.lineage_node.audit.created_at,
                        created_by=request.lineage_node.audit.created_by,
                        etag=request.lineage_node.audit.etag,
                        updated_at=request.lineage_node.audit.updated_at
                    )
                )
            )
            response_0 = cast(customers_v1_customer_segment_validation_service_pb2.CheckCustomerSegmentEligibilityResponse, await deps.bus.request(
                'acme.lineage.v1.LineageNodeSyncService/PullLineageNodes/0', outgoing_0, deps.settings.timeout,
            ))
            outgoing_1 = returns_v1_return_request_query_service_pb2.BrowseReturnRequestsRequest(
                context=request.context,
                filter=returns_v1_return_request_query_service_pb2.BrowseReturnRequestsRequest.Filter(
                    created_after=response_0.customer_segment.audit.updated_at,
                    labels=dict(response_0.result.details),
                    owner_id=response_0.customer_segment.owner.user_id,
                    region=request.lineage_node.location.region
                )
            )
            response_1 = await deps.clients.returns_return_request_query.BrowseReturnRequests(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.outcome.status
            if returned_0_0:
                response.outcome.status = returned_0_0
            returned_0_1 = response_0.customer_segment.audit.created_by
            returned_0_1_part_1 = response.lineage_node.children.add()
            returned_0_1_part_2 = returned_0_1_part_1.children.add()
            if returned_0_1:
                returned_0_1_part_2.audit.created_by = returned_0_1
            returned_1_0 = response_1.result.reference_ids
            response.result.reference_ids.extend(returned_1_0)
            echoed_0 = request.lineage_node_id
            response.lineage_node.lineage_node_id = echoed_0
            echoed_1 = request.lineage_node.parent_id
            response.lineage_node.parent_id = echoed_1
            return response

    async def handle_push_lineage_node(
        self,
        request: lineage_v1_lineage_node_sync_service_pb2.PushLineageNodeRequest
    ) -> lineage_v1_lineage_node_sync_service_pb2.PushLineageNodeResponse:
        """Pushs a lineage node."""
        deps = self.deps
        response = lineage_v1_lineage_node_sync_service_pb2.PushLineageNodeResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('PushLineageNode', extra={'fields': {'checksum': request.details.checksum}})
            await deps.repository.audit(
                request.context.tenant_id,
                'PushLineageNode',
                {'checksum': request.details.checksum}
            )
            await deps.repository.save_lineage_node(request.context.tenant_id, request.lineage_node)
            response_0 = customers_v1_household_query_service_pb2.SummarizeHouseholdsResponse()
            response_1 = pipelines_v1_pipeline_run_validation_service_pb2.NormalizePipelineRunResponse()
            outgoing_0 = customers_v1_household_query_service_pb2.SummarizeHouseholdsRequest(
                annotations=dict(request.annotations),
                context=request.context,
                reason=request.reason
            )
            method_name_0 = 'SummarizeHouseholds'
            response_0 = await getattr(
                deps.clients.customers_household_query,
                method_name_0
            )(outgoing_0, timeout=deps.settings.timeout)
            fields_1: dict[str, Any] = {
                'context': request.context,
                'pipeline_run': {
                    'assignee': {'user_id': request.lineage_node.manager.user_id},
                    'requester': {'email': request.lineage_node.manager.email}
                }
            }
            outgoing_1 = pipelines_v1_pipeline_run_validation_service_pb2.NormalizePipelineRunRequest(**fields_1)
            response_1 = await deps.clients.pipelines_pipeline_run_validation.NormalizePipelineRun(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.correlation_id
            if returned_0_0:
                response.result.correlation_id = returned_0_0
            returned_1_0 = response_1.outcome.reference_id
            if returned_1_0:
                response.outcome.reference_id = returned_1_0
            returned_1_1 = response_1.pipeline_run.customer.display_name
            returned_1_1_part_1 = response.lineage_node.children.add()
            returned_1_1_part_2 = returned_1_1_part_1.children.add()
            if returned_1_1:
                returned_1_1_part_2.manager.display_name = returned_1_1
            echoed_0 = request.lineage_node_id
            response.lineage_node.lineage_node_id = echoed_0
            echoed_1 = request.lineage_node.attributes
            response.lineage_node.attributes.update(echoed_1)
            return response

    async def handle_reconcile_lineage_nodes(
        self,
        request: lineage_v1_lineage_node_sync_service_pb2.ReconcileLineageNodesRequest
    ) -> lineage_v1_lineage_node_sync_service_pb2.ReconcileLineageNodesResponse:
        """Reconciles a lineage node."""
        deps = self.deps
        response = lineage_v1_lineage_node_sync_service_pb2.ReconcileLineageNodesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ReconcileLineageNodes', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'ReconcileLineageNodes', {'reason': request.reason})
            await deps.repository.save_lineage_node(request.context.tenant_id, request.lineage_node)
            response_0 = identity_v1_user_query_service_pb2.LookupUserResponse()
            response_1 = forecasting_v1_forecast_model_validation_service_pb2.PreviewForecastModelResponse()
            response_2 = deliveries_v1_delivery_service_pb2.CloneDeliveryResponse()
            response_3 = lineage_v1_lineage_node_query_service_pb2.CountLineageNodesResponse()
            outgoing_0 = identity_v1_user_query_service_pb2.LookupUserRequest(
                context=request.context,
                user_id=request.lineage_node.manager.user_id
            )
            document_0 = MessageToDict(outgoing_0, preserving_proto_field_name=True)
            outgoing_0 = ParseDict(document_0, identity_v1_user_query_service_pb2.LookupUserRequest())
            response_0 = await deps.clients.identity_user_query.LookupUser(outgoing_0, timeout=deps.settings.timeout)
            outgoing_1 = forecasting_v1_forecast_model_validation_service_pb2.PreviewForecastModelRequest(
                context=request.context,
                forecast_model=forecasting_v1_forecasting_pb2.ForecastModel(
                    address=common_v1_address_pb2.PostalAddress(
                        country_code=request.lineage_node.location.country_code,
                        recipient=request.lineage_node.location.recipient,
                        region=response_0.user.primary_address.region
                    ),
                    owner=identity_v1_refs_pb2.UserRef(email=response_0.user.contact.email)
                )
            )
            document_1 = MessageToJson(outgoing_1, preserving_proto_field_name=True)
            outgoing_1 = Parse(
                document_1,
                forecasting_v1_forecast_model_validation_service_pb2.PreviewForecastModelRequest()
            )
            response_1 = await deps.clients.forecasting_forecast_model_validation.PreviewForecastModel(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = deliveries_v1_delivery_service_pb2.CloneDeliveryRequest()
            outgoing_2.context.CopyFrom(request.context)
            outgoing_2.delivery.audit.updated_at.CopyFrom(response_1.forecast_model.audit.updated_at)
            outgoing_2.delivery.billing_address.lines.extend(list(response_0.user.primary_address.lines))
            merged_2 = deliveries_v1_delivery_service_pb2.CloneDeliveryRequest()
            merged_2.MergeFrom(outgoing_2)
            outgoing_2.CopyFrom(merged_2)
            response_2 = await deps.clients.deliveries_delivery.CloneDelivery(outgoing_2, timeout=deps.settings.timeout)
            outgoing_3 = lineage_v1_lineage_node_query_service_pb2.CountLineageNodesRequest(
                context=request.context,
                filter=lineage_v1_lineage_node_query_service_pb2.CountLineageNodesRequest.Filter(
                    region=response_2.delivery.billing_address.region
                )
            )
            envelope_3 = AnyMessage()
            envelope_3.Pack(outgoing_3)
            outgoing_3 = lineage_v1_lineage_node_query_service_pb2.CountLineageNodesRequest()
            if not envelope_3.Unpack(outgoing_3):
                raise ValueError("partner envelope contains the wrong request type")
            response_3 = await deps.clients.lineage_lineage_node_query.CountLineageNodes(
                outgoing_3,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.outcome.message = returned_0_0
            returned_0_1 = response_0.user.primary_address.recipient
            returned_0_1_part_1 = response.lineage_node.children.add()
            returned_0_1_part_2 = returned_0_1_part_1.children.add()
            if returned_0_1:
                returned_0_1_part_2.location.recipient = returned_0_1
            returned_1_0 = response_1.result.correlation_id
            if returned_1_0:
                response.result.correlation_id = returned_1_0
            returned_2_0 = response_2.delivery.counterparty.display_name
            returned_2_0_part_1 = response.lineage_node.children.add()
            returned_2_0_part_2 = returned_2_0_part_1.children.add()
            if returned_2_0:
                returned_2_0_part_2.manager.display_name = returned_2_0
            returned_2_1 = response_2.delivery.audit.created_by
            if returned_2_1:
                response.lineage_node.audit.created_by = returned_2_1
            returned_3_0 = response_3.result.correlation_id
            if returned_3_0:
                response.result.correlation_id = returned_3_0
            returned_3_1 = response_3.result.status
            if returned_3_1:
                response.outcome.status = returned_3_1
            echoed_0 = request.lineage_node_id
            response.lineage_node.lineage_node_id = echoed_0
            echoed_1 = request.lineage_node.status
            response.lineage_node.status = echoed_1
            return response

    async def handle_resolve_lineage_node_conflict(
        self,
        request: lineage_v1_lineage_node_sync_service_pb2.ResolveLineageNodeConflictRequest
    ) -> lineage_v1_lineage_node_sync_service_pb2.ResolveLineageNodeConflictResponse:
        """Resolves a lineage node."""
        deps = self.deps
        response = lineage_v1_lineage_node_sync_service_pb2.ResolveLineageNodeConflictResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ResolveLineageNodeConflict', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ResolveLineageNodeConflict',
                {'reason': request.reason}
            )
            await deps.repository.save_lineage_node(request.context.tenant_id, request.lineage_node)
            response_0 = lineage_v1_lineage_node_query_service_pb2.ExportLineageNodesResponse()
            response_1 = modelregistry_v1_registered_model_query_service_pb2.BrowseRegisteredModelsResponse()
            outgoing_0 = lineage_v1_lineage_node_query_service_pb2.ExportLineageNodesRequest(
                context=request.context,
                filter=lineage_v1_lineage_node_query_service_pb2.ExportLineageNodesRequest.Filter(
                    created_after=request.lineage_node.audit.updated_at,
                    region=request.lineage_node.location.region
                )
            )
            async for chunk_0 in deps.clients.lineage_lineage_node_query.ExportLineageNodes(
                outgoing_0,
                timeout=deps.settings.timeout
            ):
                response_0 = chunk_0
            command_1 = LineageNodeSyncResolveLineageNodeConflict1Command(
                context=request.context,
                filter_region=request.lineage_node.location.region,
                filter_created_after=request.lineage_node.audit.updated_at,
                filter_labels=dict(request.annotations)
            )
            outgoing_1 = to_lineage_node_sync_resolve_lineage_node_conflict1_command(command_1)
            response_1 = await deps.clients.modelregistry_registered_model_query.BrowseRegisteredModels(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_1_0 = response_1.result.details
            response.result.details.update(returned_1_0)
            returned_1_1 = response_1.result.message
            if returned_1_1:
                response.result.message = returned_1_1
            echoed_0 = request.lineage_node_id
            response.lineage_node.lineage_node_id = echoed_0
            echoed_1 = request.lineage_node.parent_id
            response.lineage_node.parent_id = echoed_1
            return response

    async def handle_stream_lineage_node_changes(
        self,
        request: lineage_v1_lineage_node_sync_service_pb2.StreamLineageNodeChangesRequest
    ) -> lineage_v1_lineage_node_sync_service_pb2.StreamLineageNodeChangesResponse:
        """Exchanges changes of lineage nodes with a peer."""
        deps = self.deps
        response = lineage_v1_lineage_node_sync_service_pb2.StreamLineageNodeChangesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('StreamLineageNodeChanges', extra={'fields': {'cursor': request.cursor}})
            await deps.repository.audit(
                request.context.tenant_id,
                'StreamLineageNodeChanges',
                {'cursor': request.cursor}
            )
            if request.WhichOneof('frame') == 'change':
                await deps.repository.save_lineage_node(request.context.tenant_id, request.change)
            response_0 = customers_v1_customer_segment_calculation_service_pb2.RecalculateCustomerSegmentsResponse()
            response_1 = lineage_v1_impact_validation_service_pb2.PreviewImpactResponse()
            outgoing_0 = customers_v1_customer_segment_calculation_service_pb2.RecalculateCustomerSegmentsRequest()
            outgoing_0.context.CopyFrom(request.context)
            if request.WhichOneof('frame') == 'change':
                outgoing_0.customer_segment.owner.display_name = request.change.manager.display_name
            if request.WhichOneof('frame') == 'change':
                outgoing_0.customer_segment.audit.updated_by = request.change.audit.updated_by
            response_0 = await deps.clients.customers_customer_segment_calculation.RecalculateCustomerSegments(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = lineage_v1_impact_validation_service_pb2.PreviewImpactRequest(
                context=request.context,
                details=lineage_v1_impact_validation_service_pb2.PreviewImpactRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(email=response_0.customer_segment.owner.email)
                ),
                impact=lineage_v1_lineage_pb2.Impact(
                    assignee=identity_v1_refs_pb2.UserRef(display_name=request.change.manager.display_name)
                )
            )
            send_1 = partial(deps.clients.lineage_impact_validation.PreviewImpact, timeout=deps.settings.timeout)
            response_1 = await send_1(outgoing_1)
            returned_0_0 = response_0.customer_segment.name
            returned_0_0_part_1 = response.lineage_node.children.add()
            if returned_0_0:
                returned_0_0_part_1.name = returned_0_0
            returned_1_0 = response_1.impact.audit.created_by
            if returned_1_0:
                response.lineage_node.audit.created_by = returned_1_0
            echoed_0 = request.change.attributes
            response.lineage_node.attributes.update(echoed_0)
            echoed_1 = request.change.parent_id
            response.lineage_node.parent_id = echoed_1
            return response

    async def handle_sync_lineage_nodes(
        self,
        request: lineage_v1_lineage_node_sync_service_pb2.SyncLineageNodesRequest
    ) -> lineage_v1_lineage_node_sync_service_pb2.SyncLineageNodesResponse:
        """Syncs a lineage node."""
        deps = self.deps
        response = lineage_v1_lineage_node_sync_service_pb2.SyncLineageNodesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SyncLineageNodes', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'SyncLineageNodes', {'reason': request.reason})
            await deps.repository.save_lineage_node(request.context.tenant_id, request.lineage_node)
            response_0 = recommendations_v1_recommendation_set_service_pb2.SearchRecommendationSetsResponse()
            response_1 = customers_v1_customer_segment_calculation_service_pb2.ExplainCustomerSegmentCalculationResponse()
            outgoing_0 = recommendations_v1_recommendation_set_service_pb2.SearchRecommendationSetsRequest(
                context=request.context,
                filter=recommendations_v1_recommendation_set_service_pb2.SearchRecommendationSetsRequest.Filter(
                    created_after=request.lineage_node.audit.updated_at,
                    owner_id=request.lineage_node.manager.user_id,
                    region=request.lineage_node.location.region
                )
            )
            outgoing_1 = customers_v1_customer_segment_calculation_service_pb2.ExplainCustomerSegmentCalculationRequest(
                context=request.context,
                customer_segment=customers_v1_customers_pb2.CustomerSegment(
                    audit=common_v1_audit_pb2.AuditInfo(
                        created_at=request.lineage_node.audit.created_at,
                        created_by=request.lineage_node.audit.created_by,
                        updated_by=request.lineage_node.audit.updated_by
                    ),
                    owner=identity_v1_refs_pb2.UserRef(display_name=request.lineage_node.manager.display_name)
                )
            )
            response_0, response_1 = await asyncio.gather(
                deps.clients.recommendations_recommendation_set.SearchRecommendationSets(
                    outgoing_0,
                    timeout=deps.settings.timeout
                ),
                deps.clients.customers_customer_segment_calculation.ExplainCustomerSegmentCalculation(
                    outgoing_1,
                    timeout=deps.settings.timeout
                ),
            )
            returned_0_0 = response_0.result.status
            if returned_0_0:
                response.result.status = returned_0_0
            returned_0_1 = response_0.result.details
            response.result.details.update(returned_0_1)
            returned_1_0 = response_1.result.correlation_id
            if returned_1_0:
                response.result.correlation_id = returned_1_0
            echoed_0 = request.lineage_node_id
            response.lineage_node.lineage_node_id = echoed_0
            echoed_1 = request.lineage_node.status
            response.lineage_node.status = echoed_1
            return response
