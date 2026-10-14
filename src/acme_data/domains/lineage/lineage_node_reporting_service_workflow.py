"""Application workflow for LineageNode Reporting."""

from __future__ import annotations

from functools import partial
import asyncio
import logging

from google.protobuf.json_format import MessageToDict
from google.protobuf.json_format import MessageToJson
from google.protobuf.json_format import Parse
from google.protobuf.json_format import ParseDict

from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.customers.v1 import (
    consent_record_validation_service_pb2 as customers_v1_consent_record_validation_service_pb2,
)
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.lineage.v1 import lineage_edge_sync_service_pb2 as lineage_v1_lineage_edge_sync_service_pb2
from acme.lineage.v1 import lineage_node_calculation_service_pb2 as lineage_v1_lineage_node_calculation_service_pb2
from acme.lineage.v1 import lineage_node_query_service_pb2 as lineage_v1_lineage_node_query_service_pb2
from acme.lineage.v1 import lineage_node_reporting_service_pb2 as lineage_v1_lineage_node_reporting_service_pb2
from acme.lineage.v1 import lineage_pb2 as lineage_v1_lineage_pb2
from acme.notifications.v1 import notification_service_pb2 as notifications_v1_notification_service_pb2
from acme.notifications.v1 import notifications_pb2 as notifications_v1_notifications_pb2

from acme_data.domains.lineage.dependencies import Dependencies
from acme_data.domains.lineage.models import LineageNodeReportingGenerateLineageNodeReport2Command
from acme_data.domains.lineage.models import LineageNodeReportingScheduleLineageNodeReport0Command
from acme_data.domains.lineage.models import to_lineage_node_reporting_generate_lineage_node_report2_command
from acme_data.domains.lineage.models import to_lineage_node_reporting_schedule_lineage_node_report0_command
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class LineageNodeReportingServicerWorkflow:
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    async def handle_count_lineage_node_totals(
        self,
        request: lineage_v1_lineage_node_reporting_service_pb2.CountLineageNodeTotalsRequest
    ) -> lineage_v1_lineage_node_reporting_service_pb2.CountLineageNodeTotalsResponse:
        """Counts lineage nodes by status."""
        deps = self.deps
        response = lineage_v1_lineage_node_reporting_service_pb2.CountLineageNodeTotalsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CountLineageNodeTotals', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'CountLineageNodeTotals',
                {'order_by': request.order_by}
            )
            return response

    async def handle_delete_lineage_node_report(
        self,
        request: lineage_v1_lineage_node_reporting_service_pb2.DeleteLineageNodeReportRequest
    ) -> lineage_v1_lineage_node_reporting_service_pb2.DeleteLineageNodeReportResponse:
        """Deletes a lineage node."""
        deps = self.deps
        response = lineage_v1_lineage_node_reporting_service_pb2.DeleteLineageNodeReportResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('DeleteLineageNodeReport', extra={'fields': {'force': request.force}})
            await deps.repository.audit(request.context.tenant_id, 'DeleteLineageNodeReport', {'force': request.force})
            response_0 = lineage_v1_lineage_node_calculation_service_pb2.RecalculateLineageNodesResponse()
            response_1 = lineage_v1_lineage_edge_sync_service_pb2.ListLineageEdgeConflictsResponse()
            outgoing_0 = lineage_v1_lineage_node_calculation_service_pb2.RecalculateLineageNodesRequest(
                context=request.context,
                lineage_node=lineage_v1_lineage_pb2.LineageNode(
                    children=[
                        lineage_v1_lineage_pb2.LineageNode(
                            children=[
                                lineage_v1_lineage_pb2.LineageNode(
                                    audit=common_v1_audit_pb2.AuditInfo(etag=request.etag)
                                )
                            ],
                            lineage_node_id=request.lineage_node_id
                        )
                    ],
                    manager=identity_v1_refs_pb2.UserRef(email=request.context.actor.email)
                ),
                reason=request.reason
            )
            document_0 = MessageToDict(outgoing_0, preserving_proto_field_name=True)
            outgoing_0 = ParseDict(
                document_0,
                lineage_v1_lineage_node_calculation_service_pb2.RecalculateLineageNodesRequest()
            )
            response_0 = await deps.clients.lineage_lineage_node_calculation.RecalculateLineageNodes(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = lineage_v1_lineage_edge_sync_service_pb2.ListLineageEdgeConflictsRequest(
                context=request.context,
                filter=lineage_v1_lineage_edge_sync_service_pb2.ListLineageEdgeConflictsRequest.Filter(
                    created_after=response_0.lineage_node.audit.created_at,
                    labels=dict(response_0.lineage_node.attributes),
                    owner_id=response_0.lineage_node.manager.user_id,
                    region=response_0.lineage_node.location.region
                )
            )
            document_1 = MessageToJson(outgoing_1, preserving_proto_field_name=True)
            outgoing_1 = Parse(document_1, lineage_v1_lineage_edge_sync_service_pb2.ListLineageEdgeConflictsRequest())
            response_1 = await deps.clients.lineage_lineage_edge_sync.ListLineageEdgeConflicts(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.details
            response.result.details.update(returned_0_0)
            returned_0_1 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_1)
            returned_1_0 = response_1.result.details
            response.result.details.update(returned_1_0)
            return response

    async def handle_fetch_lineage_node_report(
        self,
        request: lineage_v1_lineage_node_reporting_service_pb2.FetchLineageNodeReportRequest
    ) -> lineage_v1_lineage_node_reporting_service_pb2.FetchLineageNodeReportResponse:
        """Returns a lineage node."""
        deps = self.deps
        response = lineage_v1_lineage_node_reporting_service_pb2.FetchLineageNodeReportResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('FetchLineageNodeReport', extra={'fields': {'domain': 'lineage'}})
            await deps.repository.audit(request.context.tenant_id, 'FetchLineageNodeReport', {})
            response_0 = lineage_v1_lineage_node_calculation_service_pb2.GetLineageNodeRatesResponse()
            outgoing_0 = lineage_v1_lineage_node_calculation_service_pb2.GetLineageNodeRatesRequest(
                context=request.context,
                lineage_node_id=request.lineage_node_id
            )
            response_0 = await deps.clients.lineage_lineage_node_calculation.GetLineageNodeRates(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.lineage_node.lineage_node_id
            returned_0_0_part_1 = response.lineage_node.children.add()
            if returned_0_0:
                returned_0_0_part_1.lineage_node_id = returned_0_0
            echoed_0 = request.lineage_node_id
            response.lineage_node.lineage_node_id = echoed_0
            return response

    async def handle_generate_lineage_node_report(
        self,
        request: lineage_v1_lineage_node_reporting_service_pb2.GenerateLineageNodeReportRequest
    ) -> lineage_v1_lineage_node_reporting_service_pb2.GenerateLineageNodeReportResponse:
        """Generates a lineage node."""
        deps = self.deps
        response = lineage_v1_lineage_node_reporting_service_pb2.GenerateLineageNodeReportResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('GenerateLineageNodeReport', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'GenerateLineageNodeReport',
                {'reason': request.reason}
            )
            response_0 = notifications_v1_notification_service_pb2.CreateNotificationResponse()
            response_1 = lineage_v1_lineage_node_query_service_pb2.PeekLineageNodeResponse()
            response_2 = notifications_v1_notification_service_pb2.CloneNotificationResponse()
            outgoing_0 = notifications_v1_notification_service_pb2.CreateNotificationRequest(
                context=request.context,
                notification=notifications_v1_notifications_pb2.Notification(
                    requester=common_v1_contact_pb2.ContactInfo(email=request.context.actor.email)
                )
            )
            outgoing_1 = lineage_v1_lineage_node_query_service_pb2.PeekLineageNodeRequest(
                context=request.context,
                lineage_node_id=request.lineage_node_id
            )
            response_0, response_1 = await asyncio.gather(
                deps.clients.notifications_notification.CreateNotification(outgoing_0, timeout=deps.settings.timeout),
                deps.clients.lineage_lineage_node_query.PeekLineageNode(outgoing_1, timeout=deps.settings.timeout),
            )
            command_2 = LineageNodeReportingGenerateLineageNodeReport2Command(
                context=request.context,
                notification_requester_email=response_0.notification.assignee.email,
                notification_requester_preferred_channel=response_0.notification.requester.preferred_channel,
                notification_audit_updated_at=response_0.notification.audit.updated_at
            )
            outgoing_2 = to_lineage_node_reporting_generate_lineage_node_report2_command(command_2)
            response_2 = await deps.clients.notifications_notification.CloneNotification(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.details
            response.result.details.update(returned_0_0)
            returned_1_0 = response_1.result.status
            if returned_1_0:
                response.result.status = returned_1_0
            returned_1_1 = response_1.result.message
            if returned_1_1:
                response.result.message = returned_1_1
            returned_2_0 = response_2.result.details
            response.result.details.update(returned_2_0)
            echoed_0 = request.details.period
            response.period.CopyFrom(echoed_0)
            return response

    async def handle_list_lineage_node_reports(
        self,
        request: lineage_v1_lineage_node_reporting_service_pb2.ListLineageNodeReportsRequest
    ) -> lineage_v1_lineage_node_reporting_service_pb2.ListLineageNodeReportsResponse:
        """Lists lineage nodes a page at a time."""
        deps = self.deps
        response = lineage_v1_lineage_node_reporting_service_pb2.ListLineageNodeReportsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ListLineageNodeReports', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ListLineageNodeReports',
                {'order_by': request.order_by}
            )
            return response

    async def handle_schedule_lineage_node_report(
        self,
        request: lineage_v1_lineage_node_reporting_service_pb2.ScheduleLineageNodeReportRequest
    ) -> lineage_v1_lineage_node_reporting_service_pb2.ScheduleLineageNodeReportResponse:
        """Schedules a lineage node."""
        deps = self.deps
        response = lineage_v1_lineage_node_reporting_service_pb2.ScheduleLineageNodeReportResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ScheduleLineageNodeReport', extra={'fields': {'lineage_node_id': request.lineage_node_id}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ScheduleLineageNodeReport',
                {'lineage_node_id': request.lineage_node_id}
            )
            response_0 = customers_v1_consent_record_validation_service_pb2.ScoreConsentRecordResponse()
            command_0 = LineageNodeReportingScheduleLineageNodeReport0Command.model_validate(
                {
                    'context': request.context,
                    'annotations': dict(request.annotations),
                    'reason': request.reason,
                    'consent_record_attributes': dict(request.details.filters)
                }
            )
            outgoing_0 = to_lineage_node_reporting_schedule_lineage_node_report0_command(command_0)
            response_0 = await deps.clients.customers_consent_record_validation.ScoreConsentRecord(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.consent_record.correlation_id
            if returned_0_0:
                response.result.correlation_id = returned_0_0
            echoed_0 = request.details.period
            response.period.CopyFrom(echoed_0)
            return response

    async def handle_share_lineage_node_report(
        self,
        request: lineage_v1_lineage_node_reporting_service_pb2.ShareLineageNodeReportRequest
    ) -> lineage_v1_lineage_node_reporting_service_pb2.ShareLineageNodeReportResponse:
        """Shares a lineage node."""
        deps = self.deps
        response = lineage_v1_lineage_node_reporting_service_pb2.ShareLineageNodeReportResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ShareLineageNodeReport', extra={'fields': {'channel': request.details.channel}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ShareLineageNodeReport',
                {'channel': request.details.channel}
            )
            response_0 = lineage_v1_lineage_edge_sync_service_pb2.SyncLineageEdgesResponse()
            outgoing_0 = lineage_v1_lineage_edge_sync_service_pb2.SyncLineageEdgesRequest(
                annotations=dict(request.annotations),
                context=request.context,
                lineage_edge=lineage_v1_lineage_pb2.LineageEdge(correlation_id=request.details.template_id),
                reason=request.reason
            )
            send_0 = partial(deps.clients.lineage_lineage_edge_sync.SyncLineageEdges, timeout=deps.settings.timeout)
            response_0 = await send_0(outgoing_0)
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.result.message = returned_0_0
            echoed_0 = request.lineage_node_id
            response.lineage_node.lineage_node_id = echoed_0
            echoed_1 = request.details.recipient.email
            response.lineage_node.manager.email = echoed_1
            return response
