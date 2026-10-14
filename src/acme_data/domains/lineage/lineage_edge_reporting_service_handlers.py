"""Reusable transport mixin for LineageEdgeReportingService."""

from __future__ import annotations

from collections.abc import AsyncIterator
from functools import partial
from typing import Any
import logging

from google.protobuf.any_pb2 import Any as AnyMessage
from google.protobuf.json_format import MessageToDict
from google.protobuf.json_format import MessageToJson
from google.protobuf.json_format import Parse
from google.protobuf.json_format import ParseDict
import grpc

from acme.audit.v1 import audit_event_query_service_pb2 as audit_v1_audit_event_query_service_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.common.v1 import paging_pb2 as common_v1_paging_pb2
from acme.customers.v1 import customer_validation_service_pb2 as customers_v1_customer_validation_service_pb2
from acme.customers.v1 import customers_pb2 as customers_v1_customers_pb2
from acme.customers.v1 import preference_validation_service_pb2 as customers_v1_preference_validation_service_pb2
from acme.forecasting.v1 import scenario_calculation_service_pb2 as forecasting_v1_scenario_calculation_service_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.ledger.v1 import ledger_account_validation_service_pb2 as ledger_v1_ledger_account_validation_service_pb2
from acme.lineage.v1 import impact_import_service_pb2 as lineage_v1_impact_import_service_pb2
from acme.lineage.v1 import lineage_edge_import_service_pb2 as lineage_v1_lineage_edge_import_service_pb2
from acme.lineage.v1 import lineage_edge_reporting_service_pb2 as lineage_v1_lineage_edge_reporting_service_pb2
from acme.lineage.v1 import lineage_node_reporting_service_pb2 as lineage_v1_lineage_node_reporting_service_pb2
from acme.notifications.v1 import notification_service_pb2 as notifications_v1_notification_service_pb2
from acme.recruiting.v1 import job_opening_query_service_pb2 as recruiting_v1_job_opening_query_service_pb2

from acme_data.domains.lineage import hooks
from acme_data.domains.lineage.dependencies import Dependencies
from acme_data.domains.lineage.models import LineageEdgeReportingScheduleLineageEdgeReport0Command
from acme_data.domains.lineage.models import LineageEdgeReportingShareLineageEdgeReport0Command
from acme_data.domains.lineage.models import to_lineage_edge_reporting_schedule_lineage_edge_report0_command
from acme_data.domains.lineage.models import to_lineage_edge_reporting_share_lineage_edge_report0_command
from acme_data.platform.rpc import messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class LineageEdgeReportingServicerHandlers:
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    @retry_transient
    async def CountLineageEdgeTotals(
        self, request: lineage_v1_lineage_edge_reporting_service_pb2.CountLineageEdgeTotalsRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_lineage_edge_reporting_service_pb2.CountLineageEdgeTotalsResponse:
        """Counts lineage edges by status."""
        return await self.handle_count_lineage_edge_totals(request)

    @rpc_errors
    async def DeleteLineageEdgeReport(
        self, request: lineage_v1_lineage_edge_reporting_service_pb2.DeleteLineageEdgeReportRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_lineage_edge_reporting_service_pb2.DeleteLineageEdgeReportResponse:
        """Deletes a lineage edge."""
        return await self.handle_delete_lineage_edge_report(request)

    @rpc_errors
    @retry_transient
    async def FetchLineageEdgeReport(
        self, request: lineage_v1_lineage_edge_reporting_service_pb2.FetchLineageEdgeReportRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_lineage_edge_reporting_service_pb2.FetchLineageEdgeReportResponse:
        """Returns a lineage edge."""
        return await self.handle_fetch_lineage_edge_report(request)

    @rpc_errors
    async def GenerateLineageEdgeReport(
        self, request: lineage_v1_lineage_edge_reporting_service_pb2.GenerateLineageEdgeReportRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_lineage_edge_reporting_service_pb2.GenerateLineageEdgeReportResponse:
        """Generates a lineage edge."""
        return await self.handle_generate_lineage_edge_report(request)

    @rpc_errors
    @retry_transient
    async def ListLineageEdgeReports(
        self, request: lineage_v1_lineage_edge_reporting_service_pb2.ListLineageEdgeReportsRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_lineage_edge_reporting_service_pb2.ListLineageEdgeReportsResponse:
        """Lists lineage edges a page at a time."""
        return await self.handle_list_lineage_edge_reports(request)

    @rpc_errors
    async def ScheduleLineageEdgeReport(
        self, request: lineage_v1_lineage_edge_reporting_service_pb2.ScheduleLineageEdgeReportRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_lineage_edge_reporting_service_pb2.ScheduleLineageEdgeReportResponse:
        """Schedules a lineage edge."""
        return await self.handle_schedule_lineage_edge_report(request)

    @rpc_errors
    async def ShareLineageEdgeReport(
        self, request: lineage_v1_lineage_edge_reporting_service_pb2.ShareLineageEdgeReportRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_lineage_edge_reporting_service_pb2.ShareLineageEdgeReportResponse:
        """Shares a lineage edge."""
        return await self.handle_share_lineage_edge_report(request)

    @stream_errors
    async def StreamLineageEdgeMetrics(
        self, request: lineage_v1_lineage_edge_reporting_service_pb2.StreamLineageEdgeMetricsRequest, context: grpc.aio.ServicerContext,
    ) -> AsyncIterator[lineage_v1_lineage_edge_reporting_service_pb2.StreamLineageEdgeMetricsResponse]:
        """Streams the changes of lineage edges as they happen."""
        response = await self.handle_stream_lineage_edge_metrics(request)
        for item in messages((response,)):
            yield item

    async def handle_count_lineage_edge_totals(
        self,
        request: lineage_v1_lineage_edge_reporting_service_pb2.CountLineageEdgeTotalsRequest
    ) -> lineage_v1_lineage_edge_reporting_service_pb2.CountLineageEdgeTotalsResponse:
        """Counts lineage edges by status."""
        deps = self.deps
        response = lineage_v1_lineage_edge_reporting_service_pb2.CountLineageEdgeTotalsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CountLineageEdgeTotals', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'CountLineageEdgeTotals',
                {'order_by': request.order_by}
            )
            response_0 = audit_v1_audit_event_query_service_pb2.SuggestAuditEventsResponse()
            response_1 = lineage_v1_lineage_node_reporting_service_pb2.CountLineageNodeTotalsResponse()
            outgoing_0 = audit_v1_audit_event_query_service_pb2.SuggestAuditEventsRequest(
                context=request.context,
                filter=audit_v1_audit_event_query_service_pb2.SuggestAuditEventsRequest.Filter(
                    created_after=request.filter.created_after,
                    owner_id=request.filter.owner_id,
                    region=request.filter.region
                ),
                page=common_v1_paging_pb2.PageRequest(page_token=request.page.page_token)
            )
            response_0 = await deps.clients.audit_audit_event_query.SuggestAuditEvents(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = lineage_v1_lineage_node_reporting_service_pb2.CountLineageNodeTotalsRequest(
                context=request.context,
                filter=lineage_v1_lineage_node_reporting_service_pb2.CountLineageNodeTotalsRequest.Filter(
                    region=request.filter.region
                ),
                page=common_v1_paging_pb2.PageRequest(page_size=request.page.page_size)
            )
            method_name_1 = 'CountLineageNodeTotals'
            response_1 = await getattr(
                deps.clients.lineage_lineage_node_reporting,
                method_name_1
            )(outgoing_1, timeout=deps.settings.timeout)
            returned_0_0 = response_0.result.status
            if returned_0_0:
                response.result.status = returned_0_0
            returned_0_1 = response_0.result.message
            if returned_0_1:
                response.result.message = returned_0_1
            returned_1_0 = response_1.result.correlation_id
            if returned_1_0:
                response.result.correlation_id = returned_1_0
            return response

    async def handle_delete_lineage_edge_report(
        self,
        request: lineage_v1_lineage_edge_reporting_service_pb2.DeleteLineageEdgeReportRequest
    ) -> lineage_v1_lineage_edge_reporting_service_pb2.DeleteLineageEdgeReportResponse:
        """Deletes a lineage edge."""
        deps = self.deps
        response = lineage_v1_lineage_edge_reporting_service_pb2.DeleteLineageEdgeReportResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('DeleteLineageEdgeReport', extra={'fields': {'etag': request.etag}})
            await deps.repository.audit(request.context.tenant_id, 'DeleteLineageEdgeReport', {'etag': request.etag})
            response_0 = lineage_v1_lineage_edge_import_service_pb2.MapLineageEdgeImportColumnsResponse()
            response_1 = customers_v1_preference_validation_service_pb2.PreviewPreferenceResponse()
            response_2 = lineage_v1_impact_import_service_pb2.ListImpactImportsResponse()
            response_3 = forecasting_v1_scenario_calculation_service_pb2.EstimateScenarioResponse()
            fields_0: dict[str, Any] = {
                'context': request.context,
                'details': {'contact': {'email': request.context.actor.email}, 'locale': request.context.locale},
                'lineage_edge': {'lineage_edge_id': request.lineage_edge_id},
                'reason': request.reason
            }
            outgoing_0 = lineage_v1_lineage_edge_import_service_pb2.MapLineageEdgeImportColumnsRequest(**fields_0)
            response_0 = await deps.clients.lineage_lineage_edge_import.MapLineageEdgeImportColumns(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = customers_v1_preference_validation_service_pb2.PreviewPreferenceRequest(
                context=request.context,
                preference=customers_v1_customers_pb2.Preference(
                    owner=identity_v1_refs_pb2.UserRef(display_name=response_0.lineage_edge.subject.display_name)
                )
            )
            document_1 = MessageToDict(outgoing_1, preserving_proto_field_name=True)
            outgoing_1 = ParseDict(
                document_1,
                customers_v1_preference_validation_service_pb2.PreviewPreferenceRequest()
            )
            response_1 = await deps.clients.customers_preference_validation.PreviewPreference(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = lineage_v1_impact_import_service_pb2.ListImpactImportsRequest(
                context=request.context,
                filter=lineage_v1_impact_import_service_pb2.ListImpactImportsRequest.Filter(
                    created_after=response_1.preference.audit.updated_at,
                    labels=dict(response_0.lineage_edge.attributes),
                    owner_id=response_1.preference.preference_id
                )
            )
            document_2 = MessageToJson(outgoing_2, preserving_proto_field_name=True)
            outgoing_2 = Parse(document_2, lineage_v1_impact_import_service_pb2.ListImpactImportsRequest())
            response_2 = await deps.clients.lineage_impact_import.ListImpactImports(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            outgoing_3 = forecasting_v1_scenario_calculation_service_pb2.EstimateScenarioRequest()
            outgoing_3.context.CopyFrom(request.context)
            field_3_1_part_1 = outgoing_3.scenario.comments.add()
            field_3_1_part_1.created_at.CopyFrom(response_1.preference.audit.created_at)
            outgoing_3.scenario.customer.display_name = response_1.preference.owner.display_name
            merged_3 = forecasting_v1_scenario_calculation_service_pb2.EstimateScenarioRequest()
            merged_3.MergeFrom(outgoing_3)
            outgoing_3.CopyFrom(merged_3)
            response_3 = await deps.clients.forecasting_scenario_calculation.EstimateScenario(
                outgoing_3,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.correlation_id
            if returned_0_0:
                response.result.correlation_id = returned_0_0
            returned_1_0 = response_1.result.reference_ids
            response.result.reference_ids.extend(returned_1_0)
            returned_1_1 = response_1.outcome.effective_at
            if returned_1_1.ListFields():
                response.effective_at.MergeFrom(returned_1_1)
            returned_2_0 = response_2.result.status
            if returned_2_0:
                response.result.status = returned_2_0
            returned_3_0 = response_3.result.message
            if returned_3_0:
                response.result.message = returned_3_0
            return response

    async def handle_fetch_lineage_edge_report(
        self,
        request: lineage_v1_lineage_edge_reporting_service_pb2.FetchLineageEdgeReportRequest
    ) -> lineage_v1_lineage_edge_reporting_service_pb2.FetchLineageEdgeReportResponse:
        """Returns a lineage edge."""
        deps = self.deps
        response = lineage_v1_lineage_edge_reporting_service_pb2.FetchLineageEdgeReportResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('FetchLineageEdgeReport', extra={'fields': {'locale': request.context.locale}})
            await deps.repository.audit(
                request.context.tenant_id,
                'FetchLineageEdgeReport',
                {'locale': request.context.locale}
            )
            echoed_0 = request.lineage_edge_id
            response.lineage_edge.lineage_edge_id = echoed_0
            return response

    async def handle_generate_lineage_edge_report(
        self,
        request: lineage_v1_lineage_edge_reporting_service_pb2.GenerateLineageEdgeReportRequest
    ) -> lineage_v1_lineage_edge_reporting_service_pb2.GenerateLineageEdgeReportResponse:
        """Generates a lineage edge."""
        deps = self.deps
        response = lineage_v1_lineage_edge_reporting_service_pb2.GenerateLineageEdgeReportResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('GenerateLineageEdgeReport', extra={'fields': {'lineage_edge_id': request.lineage_edge_id}})
            await deps.repository.audit(
                request.context.tenant_id,
                'GenerateLineageEdgeReport',
                {'lineage_edge_id': request.lineage_edge_id}
            )
            response_0 = customers_v1_customer_validation_service_pb2.LintCustomersResponse()
            outgoing_0 = customers_v1_customer_validation_service_pb2.LintCustomersRequest(
                context=request.context,
                customer=customers_v1_customers_pb2.Customer(
                    relationship_manager=identity_v1_refs_pb2.UserRef(user_id=request.context.actor.user_id)
                )
            )
            envelope_0 = AnyMessage()
            envelope_0.Pack(outgoing_0)
            outgoing_0 = customers_v1_customer_validation_service_pb2.LintCustomersRequest()
            if not envelope_0.Unpack(outgoing_0):
                raise ValueError("partner envelope contains the wrong request type")
            response_0 = await deps.clients.customers_customer_validation.LintCustomers(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.status
            if returned_0_0:
                response.result.status = returned_0_0
            returned_0_1 = response_0.result.message
            if returned_0_1:
                response.result.message = returned_0_1
            echoed_0 = request.details.period
            response.period.CopyFrom(echoed_0)
            return response

    async def handle_list_lineage_edge_reports(
        self,
        request: lineage_v1_lineage_edge_reporting_service_pb2.ListLineageEdgeReportsRequest
    ) -> lineage_v1_lineage_edge_reporting_service_pb2.ListLineageEdgeReportsResponse:
        """Lists lineage edges a page at a time."""
        deps = self.deps
        response = lineage_v1_lineage_edge_reporting_service_pb2.ListLineageEdgeReportsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ListLineageEdgeReports', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ListLineageEdgeReports',
                {'order_by': request.order_by}
            )
            response_0 = notifications_v1_notification_service_pb2.ListNotificationsResponse()
            outgoing_0 = notifications_v1_notification_service_pb2.ListNotificationsRequest(
                context=request.context,
                filter=notifications_v1_notification_service_pb2.ListNotificationsRequest.Filter(
                    created_after=request.filter.created_after
                ),
                page=common_v1_paging_pb2.PageRequest(page_token=request.page.page_token)
            )
            response_0 = await deps.clients.notifications_notification.ListNotifications(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.status
            if returned_0_0:
                response.result.status = returned_0_0
            returned_0_1 = response_0.page_info.next_page_token
            if returned_0_1:
                response.page_info.next_page_token = returned_0_1
            return response

    async def handle_schedule_lineage_edge_report(
        self,
        request: lineage_v1_lineage_edge_reporting_service_pb2.ScheduleLineageEdgeReportRequest
    ) -> lineage_v1_lineage_edge_reporting_service_pb2.ScheduleLineageEdgeReportResponse:
        """Schedules a lineage edge."""
        deps = self.deps
        response = lineage_v1_lineage_edge_reporting_service_pb2.ScheduleLineageEdgeReportResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ScheduleLineageEdgeReport', extra={'fields': {'lineage_edge_id': request.lineage_edge_id}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ScheduleLineageEdgeReport',
                {'lineage_edge_id': request.lineage_edge_id}
            )
            response_0 = recruiting_v1_job_opening_query_service_pb2.BrowseJobOpeningsResponse()
            command_0 = LineageEdgeReportingScheduleLineageEdgeReport0Command(
                context=request.context,
                filter_labels=dict(request.details.filters),
                filter_owner_id=request.context.actor.user_id
            )
            outgoing_0 = to_lineage_edge_reporting_schedule_lineage_edge_report0_command(command_0)
            response_0 = await deps.clients.recruiting_job_opening_query.BrowseJobOpenings(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.correlation_id
            if returned_0_0:
                response.result.correlation_id = returned_0_0
            returned_0_1 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_1)
            echoed_0 = request.details.period
            response.period.CopyFrom(echoed_0)
            return response

    async def handle_share_lineage_edge_report(
        self,
        request: lineage_v1_lineage_edge_reporting_service_pb2.ShareLineageEdgeReportRequest
    ) -> lineage_v1_lineage_edge_reporting_service_pb2.ShareLineageEdgeReportResponse:
        """Shares a lineage edge."""
        deps = self.deps
        response = lineage_v1_lineage_edge_reporting_service_pb2.ShareLineageEdgeReportResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ShareLineageEdgeReport', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'ShareLineageEdgeReport', {'reason': request.reason})
            response_0 = ledger_v1_ledger_account_validation_service_pb2.ValidateLedgerAccountResponse()
            response_1 = lineage_v1_lineage_node_reporting_service_pb2.ListLineageNodeReportsResponse()
            command_0 = LineageEdgeReportingShareLineageEdgeReport0Command.model_validate(
                {
                    'context': request.context,
                    'ledger_account_contact_email': request.details.recipient.email,
                    'details_contact_phone': request.details.recipient.phone,
                    'ledger_account_contact_name': request.details.recipient.name
                }
            )
            outgoing_0 = to_lineage_edge_reporting_share_lineage_edge_report0_command(command_0)
            response_0 = await deps.clients.ledger_ledger_account_validation.ValidateLedgerAccount(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = lineage_v1_lineage_node_reporting_service_pb2.ListLineageNodeReportsRequest(
                context=request.context,
                filter=lineage_v1_lineage_node_reporting_service_pb2.ListLineageNodeReportsRequest.Filter(
                    created_after=response_0.ledger_account.audit.created_at,
                    labels=dict(response_0.ledger_account.labels),
                    owner_id=response_0.result.correlation_id
                )
            )
            send_1 = partial(
                deps.clients.lineage_lineage_node_reporting.ListLineageNodeReports,
                timeout=deps.settings.timeout
            )
            response_1 = await send_1(outgoing_1)
            returned_0_0 = response_0.outcome.reference_id
            if returned_0_0:
                response.outcome.reference_id = returned_0_0
            returned_1_0 = response_1.result.correlation_id
            if returned_1_0:
                response.result.correlation_id = returned_1_0
            echoed_0 = request.lineage_edge_id
            response.lineage_edge.lineage_edge_id = echoed_0
            return response

    async def handle_stream_lineage_edge_metrics(
        self,
        request: lineage_v1_lineage_edge_reporting_service_pb2.StreamLineageEdgeMetricsRequest
    ) -> lineage_v1_lineage_edge_reporting_service_pb2.StreamLineageEdgeMetricsResponse:
        """Streams the changes of lineage edges as they happen."""
        deps = self.deps
        response = lineage_v1_lineage_edge_reporting_service_pb2.StreamLineageEdgeMetricsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('StreamLineageEdgeMetrics', extra={'fields': {'max_events': request.max_events}})
            await deps.repository.audit(
                request.context.tenant_id,
                'StreamLineageEdgeMetrics',
                {'max_events': request.max_events}
            )
            response_0 = lineage_v1_lineage_edge_import_service_pb2.RetryLineageEdgeImportResponse()
            outgoing_0 = lineage_v1_lineage_edge_import_service_pb2.RetryLineageEdgeImportRequest(
                context=request.context,
                details=lineage_v1_lineage_edge_import_service_pb2.RetryLineageEdgeImportRequest.Details(
                    notify=common_v1_contact_pb2.ContactInfo(
                        email=request.subscriber.email,
                        name=request.subscriber.name,
                        phone=request.subscriber.phone,
                        preferred_channel=request.subscriber.preferred_channel
                    )
                )
            )
            response_0 = await hooks.lineage_edge_reporting_stream_lineage_edge_metrics0(
                deps.clients.lineage_lineage_edge_import,
                outgoing_0,
                deps.settings.timeout
            )
            returned_0_0 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_0)
            returned_0_1 = response_0.result.status
            if returned_0_1:
                response.result.status = returned_0_1
            return response
