"""Reusable transport mixin for LineageNodeCalculationService."""

from __future__ import annotations

from collections.abc import AsyncIterator
from functools import partial
from typing import Any
from typing import cast
import asyncio
import logging

from google.protobuf.any_pb2 import Any as AnyMessage
import grpc

from acme.appointments.v1 import appointment_service_pb2 as appointments_v1_appointment_service_pb2
from acme.appointments.v1 import appointments_pb2 as appointments_v1_appointments_pb2
from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.dispatch.v1 import dispatch_order_query_service_pb2 as dispatch_v1_dispatch_order_query_service_pb2
from acme.documents.v1 import document_query_service_pb2 as documents_v1_document_query_service_pb2
from acme.featureflags.v1 import feature_flag_service_pb2 as featureflags_v1_feature_flag_service_pb2
from acme.identity.v1 import identity_pb2 as identity_v1_identity_pb2
from acme.identity.v1 import user_query_service_pb2 as identity_v1_user_query_service_pb2
from acme.identity.v1 import user_service_pb2 as identity_v1_user_service_pb2
from acme.lineage.v1 import lineage_node_calculation_service_pb2 as lineage_v1_lineage_node_calculation_service_pb2
from acme.metrics.v1 import dashboard_history_service_pb2 as metrics_v1_dashboard_history_service_pb2
from acme.metrics.v1 import dashboard_validation_service_pb2 as metrics_v1_dashboard_validation_service_pb2
from acme.metrics.v1 import dashboard_validation_service_pb2_grpc as metrics_v1_dashboard_validation_service_pb2_grpc
from acme.metrics.v1 import metric_alert_query_service_pb2 as metrics_v1_metric_alert_query_service_pb2
from acme.metrics.v1 import metrics_pb2 as metrics_v1_metrics_pb2
from acme.notifications.v1 import notification_query_service_pb2 as notifications_v1_notification_query_service_pb2
from acme.search.v1 import search_index_validation_service_pb2 as search_v1_search_index_validation_service_pb2
from acme.search.v1 import search_pb2 as search_v1_search_pb2

from acme_data.domains.lineage import hooks
from acme_data.domains.lineage.adapters import LineageNodeCalculationCalculateLineageNode2Adapter
from acme_data.domains.lineage.adapters import LineageNodeCalculationCalculateLineageNode2Port
from acme_data.domains.lineage.dependencies import Dependencies
from acme_data.domains.lineage.models import LineageNodeCalculationSimulateLineageNode0Command
from acme_data.domains.lineage.models import LineageNodeCalculationSimulateLineageNode1Command
from acme_data.domains.lineage.models import to_lineage_node_calculation_simulate_lineage_node0_command
from acme_data.domains.lineage.models import to_lineage_node_calculation_simulate_lineage_node1_command
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_id
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class LineageNodeCalculationServicerHandlers:
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    async def CalculateLineageNode(
        self, request: lineage_v1_lineage_node_calculation_service_pb2.CalculateLineageNodeRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_lineage_node_calculation_service_pb2.CalculateLineageNodeResponse:
        """Calculates a lineage node."""
        return await self.handle_calculate_lineage_node(request)

    @rpc_errors
    async def EstimateLineageNode(
        self, request: lineage_v1_lineage_node_calculation_service_pb2.EstimateLineageNodeRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_lineage_node_calculation_service_pb2.EstimateLineageNodeResponse:
        """Estimates a lineage node."""
        return await self.handle_estimate_lineage_node(request)

    @rpc_errors
    async def ExplainLineageNodeCalculation(
        self, request: lineage_v1_lineage_node_calculation_service_pb2.ExplainLineageNodeCalculationRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_lineage_node_calculation_service_pb2.ExplainLineageNodeCalculationResponse:
        """Explains a lineage node."""
        return await self.handle_explain_lineage_node_calculation(request)

    @rpc_errors
    @retry_transient
    async def GetLineageNodeRates(
        self, request: lineage_v1_lineage_node_calculation_service_pb2.GetLineageNodeRatesRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_lineage_node_calculation_service_pb2.GetLineageNodeRatesResponse:
        """Returns a lineage node."""
        return await self.handle_get_lineage_node_rates(request)

    @rpc_errors
    async def QuoteLineageNode(
        self, request: lineage_v1_lineage_node_calculation_service_pb2.QuoteLineageNodeRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_lineage_node_calculation_service_pb2.QuoteLineageNodeResponse:
        """Quotes a lineage node."""
        return await self.handle_quote_lineage_node(request)

    @rpc_errors
    async def RecalculateLineageNodes(
        self, request: lineage_v1_lineage_node_calculation_service_pb2.RecalculateLineageNodesRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_lineage_node_calculation_service_pb2.RecalculateLineageNodesResponse:
        """Recalculates a lineage node."""
        return await self.handle_recalculate_lineage_nodes(request)

    @rpc_errors
    async def SimulateLineageNode(
        self, request: lineage_v1_lineage_node_calculation_service_pb2.SimulateLineageNodeRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_lineage_node_calculation_service_pb2.SimulateLineageNodeResponse:
        """Simulates a lineage node."""
        return await self.handle_simulate_lineage_node(request)

    async def handle_calculate_lineage_node(
        self,
        request: lineage_v1_lineage_node_calculation_service_pb2.CalculateLineageNodeRequest
    ) -> lineage_v1_lineage_node_calculation_service_pb2.CalculateLineageNodeResponse:
        """Calculates a lineage node."""
        deps = self.deps
        response = lineage_v1_lineage_node_calculation_service_pb2.CalculateLineageNodeResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CalculateLineageNode', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'CalculateLineageNode', {'reason': request.reason})
            await deps.repository.save_lineage_node(request.context.tenant_id, request.lineage_node)
            response_0 = dispatch_v1_dispatch_order_query_service_pb2.SuggestDispatchOrdersResponse()
            response_1 = documents_v1_document_query_service_pb2.BrowseDocumentsResponse()
            response_2 = search_v1_search_index_validation_service_pb2.NormalizeSearchIndexResponse()
            outgoing_0 = dispatch_v1_dispatch_order_query_service_pb2.SuggestDispatchOrdersRequest(
                context=request.context,
                filter=dispatch_v1_dispatch_order_query_service_pb2.SuggestDispatchOrdersRequest.Filter(
                    created_after=request.lineage_node.audit.updated_at,
                    labels=dict(request.lineage_node.attributes),
                    owner_id=request.lineage_node.manager.user_id,
                    region=request.details.destination.region
                )
            )
            response_0 = await hooks.lineage_node_calculation_calculate_lineage_node0(
                deps.clients.dispatch_dispatch_order_query,
                outgoing_0,
                deps.settings.timeout
            )
            outgoing_1 = documents_v1_document_query_service_pb2.BrowseDocumentsRequest()
            outgoing_1.context.CopyFrom(request.context)
            outgoing_1.filter.region = request.lineage_node.location.region
            outgoing_1.filter.owner_id = request.lineage_node.manager.user_id
            outgoing_1.filter.created_after.CopyFrom(request.lineage_node.audit.created_at)
            outgoing_1.filter.labels.update(dict(response_0.result.details))
            outgoing_1.context.tenant_id = tenant_id.get()
            response_1 = await deps.clients.documents_document_query.BrowseDocuments(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = search_v1_search_index_validation_service_pb2.NormalizeSearchIndexRequest(
                context=request.context,
                search_index=search_v1_search_pb2.SearchIndex(
                    address=common_v1_address_pb2.PostalAddress(
                        country_code=request.details.destination.country_code,
                        lines=list(request.lineage_node.location.lines)
                    ),
                    audit=common_v1_audit_pb2.AuditInfo(created_by=request.lineage_node.audit.created_by)
                )
            )
            port_2: LineageNodeCalculationCalculateLineageNode2Port = LineageNodeCalculationCalculateLineageNode2Adapter(
                deps.clients.search_search_index_validation,
                deps.settings.timeout
            )
            response_2 = await port_2.execute(outgoing_2)
            returned_0_0 = response_0.result.correlation_id
            if returned_0_0:
                response.result.correlation_id = returned_0_0
            returned_1_0 = response_1.result.message
            if returned_1_0:
                response.result.message = returned_1_0
            returned_1_1 = response_1.result.details
            response.result.details.update(returned_1_1)
            returned_2_0 = response_2.search_index.address.recipient
            returned_2_0_part_1 = response.lineage_node.children.add()
            if returned_2_0:
                returned_2_0_part_1.location.recipient = returned_2_0
            echoed_0 = request.lineage_node_id
            response.lineage_node.lineage_node_id = echoed_0
            echoed_1 = request.lineage_node.depth
            response.lineage_node.depth = echoed_1
            return response

    async def handle_estimate_lineage_node(
        self,
        request: lineage_v1_lineage_node_calculation_service_pb2.EstimateLineageNodeRequest
    ) -> lineage_v1_lineage_node_calculation_service_pb2.EstimateLineageNodeResponse:
        """Estimates a lineage node."""
        deps = self.deps
        response = lineage_v1_lineage_node_calculation_service_pb2.EstimateLineageNodeResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('EstimateLineageNode', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'EstimateLineageNode', {'reason': request.reason})
            await deps.repository.save_lineage_node(request.context.tenant_id, request.lineage_node)
            response_0 = identity_v1_user_query_service_pb2.BrowseUsersResponse()
            response_1 = identity_v1_user_service_pb2.CreateUserResponse()
            response_2 = metrics_v1_metric_alert_query_service_pb2.ExportMetricAlertsResponse()
            outgoing_0 = identity_v1_user_query_service_pb2.BrowseUsersRequest(
                context=request.context,
                filter=identity_v1_user_query_service_pb2.BrowseUsersRequest.Filter(
                    created_after=request.lineage_node.audit.updated_at,
                    labels=dict(request.lineage_node.attributes),
                    owner_id=request.lineage_node.parent_id,
                    region=request.lineage_node.location.region
                )
            )
            outgoing_1 = identity_v1_user_service_pb2.CreateUserRequest(
                context=request.context,
                user=identity_v1_identity_pb2.User(
                    audit=common_v1_audit_pb2.AuditInfo(updated_at=request.lineage_node.audit.updated_at),
                    primary_address=common_v1_address_pb2.PostalAddress(
                        postal_code=request.lineage_node.location.postal_code,
                        recipient=request.details.destination.recipient
                    )
                )
            )
            response_0, response_1 = await asyncio.gather(
                deps.clients.identity_user_query.BrowseUsers(outgoing_0, timeout=deps.settings.timeout),
                deps.clients.identity_user.CreateUser(outgoing_1, timeout=deps.settings.timeout),
            )
            outgoing_2 = metrics_v1_metric_alert_query_service_pb2.ExportMetricAlertsRequest(
                context=request.context,
                filter=metrics_v1_metric_alert_query_service_pb2.ExportMetricAlertsRequest.Filter(
                    created_after=response_1.user.audit.updated_at,
                    owner_id=request.lineage_node.manager.user_id,
                    region=request.lineage_node.location.region
                )
            )
            async for chunk_2 in deps.clients.metrics_metric_alert_query.ExportMetricAlerts(
                outgoing_2,
                timeout=deps.settings.timeout
            ):
                response_2 = chunk_2
            returned_0_0 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_0)
            returned_1_0 = response_1.user.contact.email
            returned_1_0_part_1 = response.lineage_node.children.add()
            if returned_1_0:
                returned_1_0_part_1.manager.email = returned_1_0
            returned_1_1 = response_1.user.contact.email
            returned_1_1_part_1 = response.lineage_node.children.add()
            returned_1_1_part_2 = returned_1_1_part_1.children.add()
            if returned_1_1:
                returned_1_1_part_2.manager.email = returned_1_1
            echoed_0 = request.lineage_node_id
            response.lineage_node.lineage_node_id = echoed_0
            echoed_1 = request.lineage_node.location
            response.lineage_node.location.CopyFrom(echoed_1)
            return response

    async def handle_explain_lineage_node_calculation(
        self,
        request: lineage_v1_lineage_node_calculation_service_pb2.ExplainLineageNodeCalculationRequest
    ) -> lineage_v1_lineage_node_calculation_service_pb2.ExplainLineageNodeCalculationResponse:
        """Explains a lineage node."""
        deps = self.deps
        response = lineage_v1_lineage_node_calculation_service_pb2.ExplainLineageNodeCalculationResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ExplainLineageNodeCalculation', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ExplainLineageNodeCalculation',
                {'reason': request.reason}
            )
            await deps.repository.save_lineage_node(request.context.tenant_id, request.lineage_node)
            response_0 = identity_v1_user_service_pb2.WatchUsersResponse()
            outgoing_0 = identity_v1_user_service_pb2.WatchUsersRequest(
                context=request.context,
                filter=identity_v1_user_service_pb2.WatchUsersRequest.Filter(
                    region=request.lineage_node.location.region
                ),
                subscriber=common_v1_contact_pb2.ContactInfo(
                    name=request.details.contact.name,
                    phone=request.details.contact.phone,
                    preferred_channel=request.details.contact.preferred_channel
                )
            )
            async for chunk_0 in deps.clients.identity_user.WatchUsers(outgoing_0, timeout=deps.settings.timeout):
                response_0 = chunk_0
            echoed_0 = request.lineage_node_id
            response.lineage_node.lineage_node_id = echoed_0
            echoed_1 = request.lineage_node.name
            response.lineage_node.name = echoed_1
            return response

    async def handle_get_lineage_node_rates(
        self,
        request: lineage_v1_lineage_node_calculation_service_pb2.GetLineageNodeRatesRequest
    ) -> lineage_v1_lineage_node_calculation_service_pb2.GetLineageNodeRatesResponse:
        """Returns a lineage node."""
        deps = self.deps
        response = lineage_v1_lineage_node_calculation_service_pb2.GetLineageNodeRatesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('GetLineageNodeRates', extra={'fields': {'domain': 'lineage'}})
            await deps.repository.audit(request.context.tenant_id, 'GetLineageNodeRates', {})
            response_0 = metrics_v1_dashboard_history_service_pb2.CompareDashboardVersionsResponse()
            response_1 = featureflags_v1_feature_flag_service_pb2.BatchGetFeatureFlagsResponse()
            outgoing_0 = metrics_v1_dashboard_history_service_pb2.CompareDashboardVersionsRequest(
                context=request.context,
                details=metrics_v1_dashboard_history_service_pb2.CompareDashboardVersionsRequest.Details(
                    author_email=request.context.actor.email
                )
            )
            response_0 = await deps.clients.metrics_dashboard_history.CompareDashboardVersions(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            fields_1: dict[str, Any] = {'context': request.context}
            outgoing_1 = featureflags_v1_feature_flag_service_pb2.BatchGetFeatureFlagsRequest(**fields_1)
            response_1 = await deps.clients.featureflags_feature_flag.BatchGetFeatureFlags(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.dashboard.billing_address.lines
            response.lineage_node.location.lines.extend(returned_0_0)
            returned_1_0 = response_1.result.details
            response.result.details.update(returned_1_0)
            echoed_0 = request.lineage_node_id
            response.lineage_node.lineage_node_id = echoed_0
            return response

    async def handle_quote_lineage_node(
        self,
        request: lineage_v1_lineage_node_calculation_service_pb2.QuoteLineageNodeRequest
    ) -> lineage_v1_lineage_node_calculation_service_pb2.QuoteLineageNodeResponse:
        """Quotes a lineage node."""
        deps = self.deps
        response = lineage_v1_lineage_node_calculation_service_pb2.QuoteLineageNodeResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('QuoteLineageNode', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'QuoteLineageNode', {'reason': request.reason})
            await deps.repository.save_lineage_node(request.context.tenant_id, request.lineage_node)
            response_0 = metrics_v1_dashboard_history_service_pb2.ListDashboardVersionsResponse()
            response_1 = appointments_v1_appointment_service_pb2.CloneAppointmentResponse()
            response_2 = identity_v1_user_query_service_pb2.ExportUsersResponse()
            outgoing_0 = metrics_v1_dashboard_history_service_pb2.ListDashboardVersionsRequest(
                context=request.context,
                filter=metrics_v1_dashboard_history_service_pb2.ListDashboardVersionsRequest.Filter(
                    created_after=request.lineage_node.audit.created_at,
                    labels=dict(request.lineage_node.attributes),
                    owner_id=request.lineage_node.manager.user_id,
                    region=request.lineage_node.location.region
                )
            )
            outgoing_1 = appointments_v1_appointment_service_pb2.CloneAppointmentRequest(
                appointment=appointments_v1_appointments_pb2.Appointment(
                    location=common_v1_address_pb2.PostalAddress(
                        postal_code=request.details.destination.postal_code,
                        region=request.lineage_node.location.region
                    ),
                    participants=[
                        appointments_v1_appointments_pb2.AppointmentParticipant(
                            contact=common_v1_contact_pb2.ContactInfo(email=request.lineage_node.manager.email)
                        )
                    ]
                ),
                context=request.context
            )
            response_0, response_1 = await asyncio.gather(
                deps.clients.metrics_dashboard_history.ListDashboardVersions(outgoing_0, timeout=deps.settings.timeout),
                deps.clients.appointments_appointment.CloneAppointment(outgoing_1, timeout=deps.settings.timeout),
            )
            outgoing_2 = identity_v1_user_query_service_pb2.ExportUsersRequest(
                context=request.context,
                filter=identity_v1_user_query_service_pb2.ExportUsersRequest.Filter(
                    created_after=response_1.appointment.audit.updated_at,
                    labels=dict(request.annotations),
                    owner_id=request.lineage_node.parent_id,
                    region=request.details.destination.region
                )
            )
            async for chunk_2 in deps.clients.identity_user_query.ExportUsers(
                outgoing_2,
                timeout=deps.settings.timeout
            ):
                response_2 = chunk_2
            returned_0_0 = response_0.result.correlation_id
            if returned_0_0:
                response.result.correlation_id = returned_0_0
            returned_0_1 = response_0.result.details
            response.result.details.update(returned_0_1)
            returned_1_0 = response_1.appointment.organizer.user_id
            returned_1_0_part_1 = response.lineage_node.children.add()
            returned_1_0_part_2 = returned_1_0_part_1.children.add()
            if returned_1_0:
                returned_1_0_part_2.manager.user_id = returned_1_0
            returned_1_1 = response_1.result.reference_ids
            response.result.reference_ids.extend(returned_1_1)
            echoed_0 = request.lineage_node_id
            response.lineage_node.lineage_node_id = echoed_0
            echoed_1 = request.lineage_node.manager
            response.lineage_node.manager.CopyFrom(echoed_1)
            return response

    async def handle_recalculate_lineage_nodes(
        self,
        request: lineage_v1_lineage_node_calculation_service_pb2.RecalculateLineageNodesRequest
    ) -> lineage_v1_lineage_node_calculation_service_pb2.RecalculateLineageNodesResponse:
        """Recalculates a lineage node."""
        deps = self.deps
        response = lineage_v1_lineage_node_calculation_service_pb2.RecalculateLineageNodesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('RecalculateLineageNodes', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'RecalculateLineageNodes',
                {'reason': request.reason}
            )
            await deps.repository.save_lineage_node(request.context.tenant_id, request.lineage_node)
            response_0 = notifications_v1_notification_query_service_pb2.ResolveNotificationsResponse()
            response_1 = metrics_v1_dashboard_validation_service_pb2.LintDashboardsResponse()
            outgoing_0 = notifications_v1_notification_query_service_pb2.ResolveNotificationsRequest(
                context=request.context
            )
            envelope_0 = AnyMessage()
            envelope_0.Pack(outgoing_0)
            outgoing_0 = notifications_v1_notification_query_service_pb2.ResolveNotificationsRequest()
            if not envelope_0.Unpack(outgoing_0):
                raise ValueError("partner envelope contains the wrong request type")
            response_0 = await deps.clients.notifications_notification_query.ResolveNotifications(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = metrics_v1_dashboard_validation_service_pb2.LintDashboardsRequest(
                context=request.context,
                dashboard=metrics_v1_metrics_pb2.Dashboard(
                    audit=common_v1_audit_pb2.AuditInfo(
                        created_by=request.lineage_node.audit.created_by,
                        etag=request.lineage_node.audit.etag
                    )
                ),
                details=metrics_v1_dashboard_validation_service_pb2.LintDashboardsRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(email=request.lineage_node.manager.email)
                )
            )
            registered_1 = cast(
                metrics_v1_dashboard_validation_service_pb2_grpc.DashboardValidationServiceStub,
                deps.clients.registry['acme.metrics.v1.DashboardValidationService']
            )
            response_1 = await registered_1.LintDashboards(outgoing_1, timeout=deps.settings.timeout)
            returned_0_0 = response_0.result.details
            response.result.details.update(returned_0_0)
            returned_0_1 = response_0.result.status
            if returned_0_1:
                response.result.status = returned_0_1
            returned_1_0 = response_1.dashboard.billing_address.country_code
            if returned_1_0:
                response.lineage_node.location.country_code = returned_1_0
            echoed_0 = request.lineage_node_id
            response.lineage_node.lineage_node_id = echoed_0
            echoed_1 = request.lineage_node.depth
            response.lineage_node.depth = echoed_1
            return response

    async def handle_simulate_lineage_node(
        self,
        request: lineage_v1_lineage_node_calculation_service_pb2.SimulateLineageNodeRequest
    ) -> lineage_v1_lineage_node_calculation_service_pb2.SimulateLineageNodeResponse:
        """Simulates a lineage node."""
        deps = self.deps
        response = lineage_v1_lineage_node_calculation_service_pb2.SimulateLineageNodeResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SimulateLineageNode', extra={'fields': {'include_breakdown': request.details.include_breakdown}})
            await deps.repository.audit(
                request.context.tenant_id,
                'SimulateLineageNode',
                {'include_breakdown': request.details.include_breakdown}
            )
            await deps.repository.save_lineage_node(request.context.tenant_id, request.lineage_node)
            response_0 = documents_v1_document_query_service_pb2.SummarizeDocumentsResponse()
            response_1 = notifications_v1_notification_query_service_pb2.SummarizeNotificationsResponse()
            response_2 = documents_v1_document_query_service_pb2.CountDocumentsResponse()
            command_0 = LineageNodeCalculationSimulateLineageNode0Command(
                context=request.context,
                annotations=dict(request.annotations),
                reason=request.reason,
                details_filters=dict(request.lineage_node.attributes)
            )
            outgoing_0 = to_lineage_node_calculation_simulate_lineage_node0_command(command_0)
            response_0 = await deps.clients.documents_document_query.SummarizeDocuments(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            command_1 = LineageNodeCalculationSimulateLineageNode1Command.model_validate(
                {
                    'context': request.context,
                    'details_period': response_0.period,
                    'reason': request.reason,
                    'annotations': dict(request.annotations)
                }
            )
            outgoing_1 = to_lineage_node_calculation_simulate_lineage_node1_command(command_1)
            response_1 = await deps.clients.notifications_notification_query.SummarizeNotifications(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = documents_v1_document_query_service_pb2.CountDocumentsRequest(
                context=request.context,
                filter=documents_v1_document_query_service_pb2.CountDocumentsRequest.Filter(
                    created_after=request.lineage_node.audit.updated_at,
                    region=request.lineage_node.location.region
                )
            )
            send_2 = partial(deps.clients.documents_document_query.CountDocuments, timeout=deps.settings.timeout)
            response_2 = await send_2(outgoing_2)
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.result.message = returned_0_0
            returned_1_0 = response_1.result.correlation_id
            if returned_1_0:
                response.result.correlation_id = returned_1_0
            returned_1_1 = response_1.result.message
            if returned_1_1:
                response.result.message = returned_1_1
            returned_2_0 = response_2.result.reference_ids
            response.result.reference_ids.extend(returned_2_0)
            returned_2_1 = response_2.result.message
            if returned_2_1:
                response.result.message = returned_2_1
            echoed_0 = request.lineage_node_id
            response.lineage_node.lineage_node_id = echoed_0
            echoed_1 = request.details.currency_code
            response.breakdown.currency_code = echoed_1
            return response
