"""Answers read-only questions about lineage nodes, for screens and reports."""

from __future__ import annotations

from collections.abc import AsyncIterator
from functools import partial
from typing import Any
import logging

import grpc

from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.documents.v1 import document_validation_service_pb2 as documents_v1_document_validation_service_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.lineage.v1 import impact_calculation_service_pb2 as lineage_v1_impact_calculation_service_pb2
from acme.lineage.v1 import impact_validation_service_pb2 as lineage_v1_impact_validation_service_pb2
from acme.lineage.v1 import lineage_edge_calculation_service_pb2 as lineage_v1_lineage_edge_calculation_service_pb2
from acme.lineage.v1 import lineage_edge_validation_service_pb2 as lineage_v1_lineage_edge_validation_service_pb2
from acme.lineage.v1 import lineage_node_query_service_pb2 as lineage_v1_lineage_node_query_service_pb2
from acme.lineage.v1 import lineage_node_query_service_pb2_grpc as lineage_v1_lineage_node_query_service_pb2_grpc
from acme.lineage.v1 import lineage_node_validation_service_pb2 as lineage_v1_lineage_node_validation_service_pb2
from acme.lineage.v1 import lineage_pb2 as lineage_v1_lineage_pb2
from acme.lineage.v1 import refs_pb2 as lineage_v1_refs_pb2
from acme.metrics.v1 import dashboard_export_service_pb2 as metrics_v1_dashboard_export_service_pb2
from acme.metrics.v1 import dashboard_validation_service_pb2 as metrics_v1_dashboard_validation_service_pb2
from acme.metrics.v1 import metrics_pb2 as metrics_v1_metrics_pb2
from acme.notifications.v1 import (
    notification_validation_service_pb2 as notifications_v1_notification_validation_service_pb2,
)
from acme.notifications.v1 import notifications_pb2 as notifications_v1_notifications_pb2

from acme_data.domains.lineage import hooks
from acme_data.domains.lineage.adapters import LineageNodeQueryPeekLineageNode1Adapter
from acme_data.domains.lineage.dependencies import Dependencies
from acme_data.domains.lineage.models import LineageNodeQueryExportLineageNodes0Command
from acme_data.domains.lineage.models import to_lineage_node_query_export_lineage_nodes0_command
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class LineageNodeQueryServicer(lineage_v1_lineage_node_query_service_pb2_grpc.LineageNodeQueryServiceServicer):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    @retry_transient
    async def BrowseLineageNodes(
        self, request: lineage_v1_lineage_node_query_service_pb2.BrowseLineageNodesRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_lineage_node_query_service_pb2.BrowseLineageNodesResponse:
        """Lists lineage nodes a page at a time."""
        return await self.handle_browse_lineage_nodes(request)

    @rpc_errors
    @retry_transient
    async def CountLineageNodes(
        self, request: lineage_v1_lineage_node_query_service_pb2.CountLineageNodesRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_lineage_node_query_service_pb2.CountLineageNodesResponse:
        """Counts lineage nodes by status."""
        return await self.handle_count_lineage_nodes(request)

    @stream_errors
    async def ExportLineageNodes(
        self, request: lineage_v1_lineage_node_query_service_pb2.ExportLineageNodesRequest, context: grpc.aio.ServicerContext,
    ) -> AsyncIterator[lineage_v1_lineage_node_query_service_pb2.ExportLineageNodesResponse]:
        """Streams every matching lineage node."""
        response = await self.handle_export_lineage_nodes(request)
        for item in messages((response,)):
            yield item

    @rpc_errors
    @retry_transient
    async def LookupLineageNode(
        self, request: lineage_v1_lineage_node_query_service_pb2.LookupLineageNodeRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_lineage_node_query_service_pb2.LookupLineageNodeResponse:
        """Returns a lineage node."""
        return await self.handle_lookup_lineage_node(request)

    @rpc_errors
    @retry_transient
    async def PeekLineageNode(
        self, request: lineage_v1_lineage_node_query_service_pb2.PeekLineageNodeRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_lineage_node_query_service_pb2.PeekLineageNodeResponse:
        """Returns a lineage node."""
        return await self.handle_peek_lineage_node(request)

    @rpc_errors
    @retry_transient
    async def ResolveLineageNodes(
        self, request: lineage_v1_lineage_node_query_service_pb2.ResolveLineageNodesRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_lineage_node_query_service_pb2.ResolveLineageNodesResponse:
        """Returns several lineage nodes at once."""
        return await self.handle_resolve_lineage_nodes(request)

    @rpc_errors
    @retry_transient
    async def SuggestLineageNodes(
        self, request: lineage_v1_lineage_node_query_service_pb2.SuggestLineageNodesRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_lineage_node_query_service_pb2.SuggestLineageNodesResponse:
        """Lists lineage nodes a page at a time."""
        return await self.handle_suggest_lineage_nodes(request)

    @rpc_errors
    async def SummarizeLineageNodes(
        self, request: lineage_v1_lineage_node_query_service_pb2.SummarizeLineageNodesRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_lineage_node_query_service_pb2.SummarizeLineageNodesResponse:
        """Summarizes a lineage node."""
        return await self.handle_summarize_lineage_nodes(request)

    async def handle_browse_lineage_nodes(
        self,
        request: lineage_v1_lineage_node_query_service_pb2.BrowseLineageNodesRequest
    ) -> lineage_v1_lineage_node_query_service_pb2.BrowseLineageNodesResponse:
        """Lists lineage nodes a page at a time."""
        deps = self.deps
        response = lineage_v1_lineage_node_query_service_pb2.BrowseLineageNodesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('BrowseLineageNodes', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(request.context.tenant_id, 'BrowseLineageNodes', {'order_by': request.order_by})
            response_0 = notifications_v1_notification_validation_service_pb2.CheckNotificationEligibilityResponse()
            outgoing_0 = notifications_v1_notification_validation_service_pb2.CheckNotificationEligibilityRequest(
                context=request.context,
                notification=notifications_v1_notifications_pb2.Notification(
                    assignee=identity_v1_refs_pb2.UserRef(user_id=request.context.actor.user_id),
                    audit=common_v1_audit_pb2.AuditInfo(created_at=request.filter.created_after),
                    requester=common_v1_contact_pb2.ContactInfo(email=request.context.actor.email)
                )
            )
            response_0 = await deps.clients.notifications_notification_validation.CheckNotificationEligibility(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.notification.assignee.email
            returned_0_0_part_0 = response.lineage_nodes.add()
            returned_0_0_part_1 = returned_0_0_part_0.children.add()
            returned_0_0_part_2 = returned_0_0_part_1.children.add()
            if returned_0_0:
                returned_0_0_part_2.manager.email = returned_0_0
            returned_0_1 = response_0.notification.assignee.user_id
            returned_0_1_part_0 = response.lineage_nodes.add()
            returned_0_1_part_1 = returned_0_1_part_0.children.add()
            if returned_0_1:
                returned_0_1_part_1.manager.user_id = returned_0_1
            return response

    async def handle_count_lineage_nodes(
        self,
        request: lineage_v1_lineage_node_query_service_pb2.CountLineageNodesRequest
    ) -> lineage_v1_lineage_node_query_service_pb2.CountLineageNodesResponse:
        """Counts lineage nodes by status."""
        deps = self.deps
        response = lineage_v1_lineage_node_query_service_pb2.CountLineageNodesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CountLineageNodes', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(request.context.tenant_id, 'CountLineageNodes', {'order_by': request.order_by})
            response_0 = lineage_v1_impact_validation_service_pb2.NormalizeImpactResponse()
            response_1 = metrics_v1_dashboard_export_service_pb2.StreamDashboardExportResponse()
            outgoing_0 = lineage_v1_impact_validation_service_pb2.NormalizeImpactRequest(
                context=request.context,
                impact=lineage_v1_lineage_pb2.Impact(
                    assignee=identity_v1_refs_pb2.UserRef(user_id=request.context.actor.user_id)
                )
            )
            response_0 = await deps.clients.lineage_impact_validation.NormalizeImpact(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = metrics_v1_dashboard_export_service_pb2.StreamDashboardExportRequest(
                context=request.context,
                filter=metrics_v1_dashboard_export_service_pb2.StreamDashboardExportRequest.Filter(
                    labels=dict(request.filter.labels),
                    owner_id=request.filter.owner_id
                )
            )
            async for chunk_1 in deps.clients.metrics_dashboard_export.StreamDashboardExport(
                outgoing_1,
                timeout=deps.settings.timeout
            ):
                response_1 = chunk_1
            returned_0_0 = response_0.result.status
            if returned_0_0:
                response.result.status = returned_0_0
            return response

    async def handle_export_lineage_nodes(
        self,
        request: lineage_v1_lineage_node_query_service_pb2.ExportLineageNodesRequest
    ) -> lineage_v1_lineage_node_query_service_pb2.ExportLineageNodesResponse:
        """Streams every matching lineage node."""
        deps = self.deps
        response = lineage_v1_lineage_node_query_service_pb2.ExportLineageNodesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ExportLineageNodes', extra={'fields': {'destination_uri': request.destination_uri}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ExportLineageNodes',
                {'destination_uri': request.destination_uri}
            )
            response_0 = lineage_v1_lineage_edge_calculation_service_pb2.CalculateLineageEdgeResponse()
            response_1 = notifications_v1_notification_validation_service_pb2.CheckNotificationEligibilityResponse()
            response_2 = lineage_v1_lineage_edge_validation_service_pb2.CheckLineageEdgeEligibilityResponse()
            response_3 = lineage_v1_lineage_edge_validation_service_pb2.PreviewLineageEdgeResponse()
            command_0 = LineageNodeQueryExportLineageNodes0Command.model_validate(
                {
                    'context': request.context,
                    'details_destination_region': request.filter.region,
                    'lineage_edge_occurred_at': request.filter.created_after
                }
            )
            outgoing_0 = to_lineage_node_query_export_lineage_nodes0_command(command_0)
            response_0 = await deps.clients.lineage_lineage_edge_calculation.CalculateLineageEdge(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = notifications_v1_notification_validation_service_pb2.CheckNotificationEligibilityRequest(
                context=request.context,
                notification=notifications_v1_notifications_pb2.Notification(
                    assignee=identity_v1_refs_pb2.UserRef(display_name=response_0.lineage_edge.subject.display_name)
                )
            )
            send_1 = partial(
                deps.clients.notifications_notification_validation.CheckNotificationEligibility,
                timeout=deps.settings.timeout
            )
            response_1 = await send_1(outgoing_1)
            outgoing_2 = lineage_v1_lineage_edge_validation_service_pb2.CheckLineageEdgeEligibilityRequest(
                context=request.context,
                details=lineage_v1_lineage_edge_validation_service_pb2.CheckLineageEdgeEligibilityRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(email=response_1.notification.requester.email)
                ),
                lineage_edge=lineage_v1_lineage_pb2.LineageEdge(
                    subject=lineage_v1_refs_pb2.ImpactRef(priority=response_0.lineage_edge.subject.priority)
                )
            )
            response_2 = await hooks.lineage_node_query_export_lineage_nodes2(
                deps.clients.lineage_lineage_edge_validation,
                outgoing_2,
                deps.settings.timeout
            )
            outgoing_3 = lineage_v1_lineage_edge_validation_service_pb2.PreviewLineageEdgeRequest()
            outgoing_3.context.CopyFrom(request.context)
            if response_1.notification.WhichOneof('origin') == 'customer':
                outgoing_3.lineage_edge.subject.display_name = response_1.notification.customer.display_name
            outgoing_3.details.contact.email = response_1.notification.requester.email
            response_3 = await deps.clients.lineage_lineage_edge_validation.PreviewLineageEdge(
                outgoing_3,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.lineage_edge.subject.display_name
            if returned_0_0:
                response.lineage_node.manager.display_name = returned_0_0
            returned_1_0 = response_1.notification.assignee.email
            returned_1_0_part_1 = response.lineage_node.children.add()
            returned_1_0_part_2 = returned_1_0_part_1.children.add()
            if returned_1_0:
                returned_1_0_part_2.manager.email = returned_1_0
            returned_1_1 = response_1.notification.assignee.display_name
            if returned_1_1:
                response.lineage_node.manager.display_name = returned_1_1
            returned_2_0 = response_2.lineage_edge.attributes
            returned_2_0_part_1 = response.lineage_node.children.add()
            returned_2_0_part_1.attributes.update(returned_2_0)
            returned_3_0 = response_3.lineage_edge.subject.display_name
            returned_3_0_part_1 = response.lineage_node.children.add()
            returned_3_0_part_2 = returned_3_0_part_1.children.add()
            if returned_3_0:
                returned_3_0_part_2.manager.display_name = returned_3_0
            returned_3_1 = response_3.result.correlation_id
            if returned_3_1:
                response.result.correlation_id = returned_3_1
            echoed_0 = request.filter.region
            response.lineage_node.location.region = echoed_0
            return response

    async def handle_lookup_lineage_node(
        self,
        request: lineage_v1_lineage_node_query_service_pb2.LookupLineageNodeRequest
    ) -> lineage_v1_lineage_node_query_service_pb2.LookupLineageNodeResponse:
        """Returns a lineage node."""
        deps = self.deps
        response = lineage_v1_lineage_node_query_service_pb2.LookupLineageNodeResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('LookupLineageNode', extra={'fields': {'domain': 'lineage'}})
            await deps.repository.audit(request.context.tenant_id, 'LookupLineageNode', {})
            response_0 = documents_v1_document_validation_service_pb2.PreviewDocumentResponse()
            outgoing_0 = documents_v1_document_validation_service_pb2.PreviewDocumentRequest(
                context=request.context,
                details=documents_v1_document_validation_service_pb2.PreviewDocumentRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(email=request.context.actor.email)
                )
            )
            response_0 = await deps.clients.documents_document_validation.PreviewDocument(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.document.billing_address.recipient
            if returned_0_0:
                response.lineage_node.location.recipient = returned_0_0
            echoed_0 = request.lineage_node_id
            response.lineage_node.lineage_node_id = echoed_0
            return response

    async def handle_peek_lineage_node(
        self,
        request: lineage_v1_lineage_node_query_service_pb2.PeekLineageNodeRequest
    ) -> lineage_v1_lineage_node_query_service_pb2.PeekLineageNodeResponse:
        """Returns a lineage node."""
        deps = self.deps
        response = lineage_v1_lineage_node_query_service_pb2.PeekLineageNodeResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('PeekLineageNode', extra={'fields': {'domain': 'lineage'}})
            await deps.repository.audit(request.context.tenant_id, 'PeekLineageNode', {})
            response_0 = notifications_v1_notification_validation_service_pb2.ExplainNotificationDecisionResponse()
            response_1 = lineage_v1_lineage_edge_validation_service_pb2.NormalizeLineageEdgeResponse()
            outgoing_0 = notifications_v1_notification_validation_service_pb2.ExplainNotificationDecisionRequest(
                context=request.context,
                details=notifications_v1_notification_validation_service_pb2.ExplainNotificationDecisionRequest.Details(
                    locale=request.context.locale
                ),
                notification=notifications_v1_notifications_pb2.Notification(
                    requester=common_v1_contact_pb2.ContactInfo(email=request.context.actor.email)
                )
            )
            response_0 = await deps.clients.notifications_notification_validation.ExplainNotificationDecision(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = lineage_v1_lineage_edge_validation_service_pb2.NormalizeLineageEdgeRequest(
                context=request.context,
                details=lineage_v1_lineage_edge_validation_service_pb2.NormalizeLineageEdgeRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(email=response_0.notification.requester.email)
                )
            )
            response_1 = await LineageNodeQueryPeekLineageNode1Adapter(
                deps.clients.lineage_lineage_edge_validation,
                deps.settings.timeout
            )(outgoing_1)
            returned_0_0 = response_0.notification.audit.updated_by
            returned_0_0_part_1 = response.lineage_node.children.add()
            if returned_0_0:
                returned_0_0_part_1.audit.updated_by = returned_0_0
            returned_1_0 = response_1.result.correlation_id
            if returned_1_0:
                response.result.correlation_id = returned_1_0
            returned_1_1 = response_1.result.status
            if returned_1_1:
                response.result.status = returned_1_1
            echoed_0 = request.lineage_node_id
            response.lineage_node.lineage_node_id = echoed_0
            return response

    async def handle_resolve_lineage_nodes(
        self,
        request: lineage_v1_lineage_node_query_service_pb2.ResolveLineageNodesRequest
    ) -> lineage_v1_lineage_node_query_service_pb2.ResolveLineageNodesResponse:
        """Returns several lineage nodes at once."""
        deps = self.deps
        response = lineage_v1_lineage_node_query_service_pb2.ResolveLineageNodesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ResolveLineageNodes', extra={'fields': {'domain': 'lineage'}})
            await deps.repository.audit(request.context.tenant_id, 'ResolveLineageNodes', {})
            response_0 = lineage_v1_impact_calculation_service_pb2.CalculateImpactResponse()
            outgoing_0 = lineage_v1_impact_calculation_service_pb2.CalculateImpactRequest(
                context=request.context,
                impact=lineage_v1_lineage_pb2.Impact(
                    assignee=identity_v1_refs_pb2.UserRef(
                        email=request.context.actor.email,
                        user_id=request.context.actor.user_id
                    ),
                    audit=common_v1_audit_pb2.AuditInfo(created_at=request.context.deadline)
                )
            )
            response_0 = await deps.clients.lineage_impact_calculation.CalculateImpact(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.impact.assignee.user_id
            returned_0_0_part_0 = response.lineage_nodes.add()
            returned_0_0_part_1 = returned_0_0_part_0.children.add()
            returned_0_0_part_2 = returned_0_0_part_1.children.add()
            if returned_0_0:
                returned_0_0_part_2.manager.user_id = returned_0_0
            returned_0_1 = response_0.impact.assignee.display_name
            returned_0_1_part_0 = response.lineage_nodes.add()
            returned_0_1_part_1 = returned_0_1_part_0.children.add()
            returned_0_1_part_2 = returned_0_1_part_1.children.add()
            if returned_0_1:
                returned_0_1_part_2.manager.display_name = returned_0_1
            return response

    async def handle_suggest_lineage_nodes(
        self,
        request: lineage_v1_lineage_node_query_service_pb2.SuggestLineageNodesRequest
    ) -> lineage_v1_lineage_node_query_service_pb2.SuggestLineageNodesResponse:
        """Lists lineage nodes a page at a time."""
        deps = self.deps
        response = lineage_v1_lineage_node_query_service_pb2.SuggestLineageNodesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SuggestLineageNodes', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'SuggestLineageNodes',
                {'order_by': request.order_by}
            )
            response_0 = metrics_v1_dashboard_validation_service_pb2.LintDashboardsResponse()
            outgoing_0 = metrics_v1_dashboard_validation_service_pb2.LintDashboardsRequest(
                context=request.context,
                dashboard=metrics_v1_metrics_pb2.Dashboard(
                    billing_address=common_v1_address_pb2.PostalAddress(region=request.filter.region)
                ),
                details=metrics_v1_dashboard_validation_service_pb2.LintDashboardsRequest.Details(
                    locale=request.context.locale
                )
            )
            response_0 = await deps.clients.metrics_dashboard_validation.LintDashboards(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.dashboard.billing_address.locality
            returned_0_0_part_0 = response.lineage_nodes.add()
            if returned_0_0:
                returned_0_0_part_0.location.locality = returned_0_0
            returned_0_1 = response_0.dashboard.counterparty.display_name
            returned_0_1_part_0 = response.lineage_nodes.add()
            if returned_0_1:
                returned_0_1_part_0.manager.display_name = returned_0_1
            return response

    async def handle_summarize_lineage_nodes(
        self,
        request: lineage_v1_lineage_node_query_service_pb2.SummarizeLineageNodesRequest
    ) -> lineage_v1_lineage_node_query_service_pb2.SummarizeLineageNodesResponse:
        """Summarizes a lineage node."""
        deps = self.deps
        response = lineage_v1_lineage_node_query_service_pb2.SummarizeLineageNodesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SummarizeLineageNodes', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'SummarizeLineageNodes', {'reason': request.reason})
            response_0 = lineage_v1_impact_validation_service_pb2.PreviewImpactResponse()
            response_1 = lineage_v1_lineage_node_validation_service_pb2.GetLineageNodeRulesResponse()
            outgoing_0 = lineage_v1_impact_validation_service_pb2.PreviewImpactRequest(
                context=request.context,
                details=lineage_v1_impact_validation_service_pb2.PreviewImpactRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(email=request.context.actor.email)
                )
            )
            method_name_0 = 'PreviewImpact'
            response_0 = await getattr(
                deps.clients.lineage_impact_validation,
                method_name_0
            )(outgoing_0, timeout=deps.settings.timeout)
            fields_1: dict[str, Any] = {'context': request.context, 'lineage_node_id': request.lineage_node_id}
            outgoing_1 = lineage_v1_lineage_node_validation_service_pb2.GetLineageNodeRulesRequest(**fields_1)
            response_1 = await deps.clients.lineage_lineage_node_validation.GetLineageNodeRules(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.result.message = returned_0_0
            returned_1_0 = response_1.result.reference_ids
            response.result.reference_ids.extend(returned_1_0)
            echoed_0 = request.details.period
            response.period.CopyFrom(echoed_0)
            return response
