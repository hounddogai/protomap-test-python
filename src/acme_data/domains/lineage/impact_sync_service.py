"""Keeps impacts in step with the systems of record in other regions."""

from __future__ import annotations

from collections.abc import AsyncIterator
from collections.abc import Awaitable
from collections.abc import Callable
from functools import partial
from typing import Any
from typing import cast
import asyncio
import logging

from google.protobuf.json_format import MessageToDict
from google.protobuf.json_format import ParseDict
import grpc

from acme.audit.v1 import audit_event_query_service_pb2 as audit_v1_audit_event_query_service_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.configuration.v1 import config_set_query_service_pb2 as configuration_v1_config_set_query_service_pb2
from acme.customers.v1 import customer_query_service_pb2 as customers_v1_customer_query_service_pb2
from acme.customers.v1 import (
    customer_segment_calculation_service_pb2 as customers_v1_customer_segment_calculation_service_pb2,
)
from acme.customers.v1 import (
    customer_segment_validation_service_pb2 as customers_v1_customer_segment_validation_service_pb2,
)
from acme.customers.v1 import customers_pb2 as customers_v1_customers_pb2
from acme.customers.v1 import preference_validation_service_pb2 as customers_v1_preference_validation_service_pb2
from acme.forecasting.v1 import forecast_model_query_service_pb2 as forecasting_v1_forecast_model_query_service_pb2
from acme.forecasting.v1 import forecasting_pb2 as forecasting_v1_forecasting_pb2
from acme.forecasting.v1 import scenario_calculation_service_pb2 as forecasting_v1_scenario_calculation_service_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.lineage.v1 import impact_sync_service_pb2 as lineage_v1_impact_sync_service_pb2
from acme.lineage.v1 import impact_sync_service_pb2_grpc as lineage_v1_impact_sync_service_pb2_grpc
from acme.lineage.v1 import lineage_edge_sync_service_pb2 as lineage_v1_lineage_edge_sync_service_pb2
from acme.lineage.v1 import lineage_edge_validation_service_pb2 as lineage_v1_lineage_edge_validation_service_pb2
from acme.lineage.v1 import lineage_node_reporting_service_pb2 as lineage_v1_lineage_node_reporting_service_pb2
from acme.lineage.v1 import lineage_pb2 as lineage_v1_lineage_pb2
from acme.lineage.v1 import refs_pb2 as lineage_v1_refs_pb2
from acme.messaging.v1 import conversation_calculation_service_pb2 as messaging_v1_conversation_calculation_service_pb2
from acme.messaging.v1 import messaging_pb2 as messaging_v1_messaging_pb2
from acme.metrics.v1 import metric_alert_export_service_pb2 as metrics_v1_metric_alert_export_service_pb2
from acme.metrics.v1 import metric_series_history_service_pb2 as metrics_v1_metric_series_history_service_pb2
from acme.metrics.v1 import metric_series_notification_service_pb2 as metrics_v1_metric_series_notification_service_pb2
from acme.metrics.v1 import metrics_pb2 as metrics_v1_metrics_pb2
from acme.search.v1 import search_index_validation_service_pb2 as search_v1_search_index_validation_service_pb2
from acme.search.v1 import search_pb2 as search_v1_search_pb2

from acme_data.domains.lineage import hooks
from acme_data.domains.lineage.dependencies import Dependencies
from acme_data.domains.lineage.models import ImpactSyncResolveImpactConflict3Command
from acme_data.domains.lineage.models import to_impact_sync_resolve_impact_conflict3_command
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import run_steps
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class ImpactSyncServicer(lineage_v1_impact_sync_service_pb2_grpc.ImpactSyncServiceServicer):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    @retry_transient
    async def GetImpactSyncState(
        self, request: lineage_v1_impact_sync_service_pb2.GetImpactSyncStateRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_impact_sync_service_pb2.GetImpactSyncStateResponse:
        """Returns an impact."""
        return await self.handle_get_impact_sync_state(request)

    @rpc_errors
    @retry_transient
    async def ListImpactConflicts(
        self, request: lineage_v1_impact_sync_service_pb2.ListImpactConflictsRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_impact_sync_service_pb2.ListImpactConflictsResponse:
        """Lists impacts a page at a time."""
        return await self.handle_list_impact_conflicts(request)

    @rpc_errors
    async def PullImpacts(
        self, request: lineage_v1_impact_sync_service_pb2.PullImpactsRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_impact_sync_service_pb2.PullImpactsResponse:
        """Pulls an impact."""
        return await self.handle_pull_impacts(request)

    @rpc_errors
    async def PushImpact(
        self, request: lineage_v1_impact_sync_service_pb2.PushImpactRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_impact_sync_service_pb2.PushImpactResponse:
        """Pushs an impact."""
        return await self.handle_push_impact(request)

    @rpc_errors
    async def ReconcileImpacts(
        self, request: lineage_v1_impact_sync_service_pb2.ReconcileImpactsRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_impact_sync_service_pb2.ReconcileImpactsResponse:
        """Reconciles an impact."""
        return await self.handle_reconcile_impacts(request)

    @rpc_errors
    async def ResolveImpactConflict(
        self, request: lineage_v1_impact_sync_service_pb2.ResolveImpactConflictRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_impact_sync_service_pb2.ResolveImpactConflictResponse:
        """Resolves an impact."""
        return await self.handle_resolve_impact_conflict(request)

    @stream_errors
    async def StreamImpactChanges(
        self, requests: AsyncIterator[
            lineage_v1_impact_sync_service_pb2.StreamImpactChangesRequest
        ], context: grpc.aio.ServicerContext,
    ) -> AsyncIterator[lineage_v1_impact_sync_service_pb2.StreamImpactChangesResponse]:
        """Exchanges changes of impacts with a peer."""
        async for request in requests:
            yield await self.handle_stream_impact_changes(request)

    @rpc_errors
    async def SyncImpacts(
        self, request: lineage_v1_impact_sync_service_pb2.SyncImpactsRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_impact_sync_service_pb2.SyncImpactsResponse:
        """Syncs an impact."""
        return await self.handle_sync_impacts(request)

    async def handle_get_impact_sync_state(
        self,
        request: lineage_v1_impact_sync_service_pb2.GetImpactSyncStateRequest
    ) -> lineage_v1_impact_sync_service_pb2.GetImpactSyncStateResponse:
        """Returns an impact."""
        deps = self.deps
        response = lineage_v1_impact_sync_service_pb2.GetImpactSyncStateResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('GetImpactSyncState', extra={'fields': {'domain': 'lineage'}})
            await deps.repository.audit(request.context.tenant_id, 'GetImpactSyncState', {})
            response_0 = metrics_v1_metric_series_notification_service_pb2.NotifyMetricSeriesWatchersResponse()
            outgoing_0 = metrics_v1_metric_series_notification_service_pb2.NotifyMetricSeriesWatchersRequest(
                annotations=dict(request.context.baggage),
                context=request.context,
                details=metrics_v1_metric_series_notification_service_pb2.NotifyMetricSeriesWatchersRequest.Details(
                    recipient=common_v1_contact_pb2.ContactInfo(email=request.context.actor.email)
                )
            )
            response_0 = await deps.clients.metrics_metric_series_notification.NotifyMetricSeriesWatchers(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.metric_series.audit.created_by
            if returned_0_0:
                response.impact.audit.created_by = returned_0_0
            echoed_0 = request.impact_id
            response.impact.impact_id = echoed_0
            return response

    async def handle_list_impact_conflicts(
        self,
        request: lineage_v1_impact_sync_service_pb2.ListImpactConflictsRequest
    ) -> lineage_v1_impact_sync_service_pb2.ListImpactConflictsResponse:
        """Lists impacts a page at a time."""
        deps = self.deps
        response = lineage_v1_impact_sync_service_pb2.ListImpactConflictsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ListImpactConflicts', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ListImpactConflicts',
                {'order_by': request.order_by}
            )
            response_0 = forecasting_v1_scenario_calculation_service_pb2.ExplainScenarioCalculationResponse()
            outgoing_0 = forecasting_v1_scenario_calculation_service_pb2.ExplainScenarioCalculationRequest(
                context=request.context,
                details=forecasting_v1_scenario_calculation_service_pb2.ExplainScenarioCalculationRequest.Details(
                    locale=request.context.locale
                ),
                scenario=forecasting_v1_forecasting_pb2.Scenario(
                    requester=common_v1_contact_pb2.ContactInfo(email=request.context.actor.email),
                    sla=forecasting_v1_forecasting_pb2.ScenarioSla(due_at=request.filter.created_after)
                )
            )
            response_0 = await deps.clients.forecasting_scenario_calculation.ExplainScenarioCalculation(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.scenario.assignee.email
            returned_0_0_part_0 = response.impacts.add()
            if returned_0_0:
                returned_0_0_part_0.assignee.email = returned_0_0
            returned_0_1 = response_0.scenario.audit.etag
            returned_0_1_part_0 = response.impacts.add()
            if returned_0_1:
                returned_0_1_part_0.audit.etag = returned_0_1
            return response

    async def handle_pull_impacts(
        self,
        request: lineage_v1_impact_sync_service_pb2.PullImpactsRequest
    ) -> lineage_v1_impact_sync_service_pb2.PullImpactsResponse:
        """Pulls an impact."""
        deps = self.deps
        response = lineage_v1_impact_sync_service_pb2.PullImpactsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('PullImpacts', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'PullImpacts', {'reason': request.reason})
            await deps.repository.save_impact(request.context.tenant_id, request.impact)
            response_0 = lineage_v1_lineage_node_reporting_service_pb2.ScheduleLineageNodeReportResponse()
            outgoing_0 = lineage_v1_lineage_node_reporting_service_pb2.ScheduleLineageNodeReportRequest(
                annotations=dict(request.annotations),
                context=request.context
            )
            response_0 = cast(lineage_v1_lineage_node_reporting_service_pb2.ScheduleLineageNodeReportResponse, await deps.bus.request(
                'acme.lineage.v1.ImpactSyncService/PullImpacts/0', outgoing_0, deps.settings.timeout,
            ))
            returned_0_0 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_0)
            echoed_0 = request.impact_id
            response.impact.impact_id = echoed_0
            echoed_1 = request.impact.requester
            response.impact.requester.CopyFrom(echoed_1)
            return response

    async def handle_push_impact(
        self,
        request: lineage_v1_impact_sync_service_pb2.PushImpactRequest
    ) -> lineage_v1_impact_sync_service_pb2.PushImpactResponse:
        """Pushs an impact."""
        deps = self.deps
        response = lineage_v1_impact_sync_service_pb2.PushImpactResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('PushImpact', extra={'fields': {'impact_id': request.impact_id}})
            await deps.repository.audit(request.context.tenant_id, 'PushImpact', {'impact_id': request.impact_id})
            await deps.repository.save_impact(request.context.tenant_id, request.impact)
            response_0 = lineage_v1_lineage_edge_sync_service_pb2.PushLineageEdgeResponse()
            response_1 = configuration_v1_config_set_query_service_pb2.ExportConfigSetsResponse()
            response_2 = lineage_v1_lineage_node_reporting_service_pb2.GenerateLineageNodeReportResponse()
            outgoing_0 = lineage_v1_lineage_edge_sync_service_pb2.PushLineageEdgeRequest(
                context=request.context,
                details=lineage_v1_lineage_edge_sync_service_pb2.PushLineageEdgeRequest.Details(
                    peer_region=request.details.peer_region
                ),
                lineage_edge=lineage_v1_lineage_pb2.LineageEdge(
                    subject=lineage_v1_refs_pb2.ImpactRef(display_name=request.impact.customer.display_name)
                )
            )
            response_0 = await deps.clients.lineage_lineage_edge_sync.PushLineageEdge(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = configuration_v1_config_set_query_service_pb2.ExportConfigSetsRequest(
                context=request.context,
                filter=configuration_v1_config_set_query_service_pb2.ExportConfigSetsRequest.Filter(
                    created_after=request.impact.sla.due_at,
                    owner_id=response_0.outcome.reference_id
                )
            )
            async for chunk_1 in deps.clients.configuration_config_set_query.ExportConfigSets(
                outgoing_1,
                timeout=deps.settings.timeout
            ):
                response_1 = chunk_1
            fields_2: dict[str, Any] = {'annotations': dict(request.annotations), 'context': request.context}
            outgoing_2 = lineage_v1_lineage_node_reporting_service_pb2.GenerateLineageNodeReportRequest(**fields_2)
            response_2 = await deps.clients.lineage_lineage_node_reporting.GenerateLineageNodeReport(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.lineage_edge.subject.impact_id
            if returned_0_0:
                response.impact.impact_id = returned_0_0
            returned_2_0 = response_2.result.reference_ids
            response.result.reference_ids.extend(returned_2_0)
            echoed_0 = request.impact.assignee
            response.impact.assignee.CopyFrom(echoed_0)
            echoed_1 = request.impact.subject
            response.impact.subject = echoed_1
            return response

    async def handle_reconcile_impacts(
        self,
        request: lineage_v1_impact_sync_service_pb2.ReconcileImpactsRequest
    ) -> lineage_v1_impact_sync_service_pb2.ReconcileImpactsResponse:
        """Reconciles an impact."""
        deps = self.deps
        response = lineage_v1_impact_sync_service_pb2.ReconcileImpactsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ReconcileImpacts', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'ReconcileImpacts', {'reason': request.reason})
            await deps.repository.save_impact(request.context.tenant_id, request.impact)
            response_0 = metrics_v1_metric_alert_export_service_pb2.ShareMetricAlertExportResponse()
            response_1 = customers_v1_customer_query_service_pb2.FindCustomersResponse()
            response_2 = customers_v1_customer_segment_validation_service_pb2.ExplainCustomerSegmentDecisionResponse()
            outgoing_0 = metrics_v1_metric_alert_export_service_pb2.ShareMetricAlertExportRequest(
                context=request.context,
                details=metrics_v1_metric_alert_export_service_pb2.ShareMetricAlertExportRequest.Details(
                    recipient=common_v1_contact_pb2.ContactInfo(
                        name=request.impact.requester.name,
                        phone=request.impact.requester.phone
                    )
                )
            )
            document_0 = MessageToDict(outgoing_0, preserving_proto_field_name=True)
            outgoing_0 = ParseDict(
                document_0,
                metrics_v1_metric_alert_export_service_pb2.ShareMetricAlertExportRequest()
            )
            response_0 = await deps.clients.metrics_metric_alert_export.ShareMetricAlertExport(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = customers_v1_customer_query_service_pb2.FindCustomersRequest()
            outgoing_1.context.CopyFrom(request.context)
            outgoing_1.filter.created_after.CopyFrom(request.impact.sla.due_at)
            if request.impact.WhichOneof('origin') == 'customer':
                outgoing_1.filter.owner_id = request.impact.customer.customer_id
            response_1 = await deps.clients.customers_customer_query.FindCustomers(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = customers_v1_customer_segment_validation_service_pb2.ExplainCustomerSegmentDecisionRequest()
            outgoing_2.context.CopyFrom(request.context)
            outgoing_2.customer_segment.owner.email = request.impact.customer.email
            outgoing_2.details.contact.email = request.impact.assignee.email
            merged_2 = customers_v1_customer_segment_validation_service_pb2.ExplainCustomerSegmentDecisionRequest()
            merged_2.MergeFrom(outgoing_2)
            outgoing_2.CopyFrom(merged_2)
            response_2 = await deps.clients.customers_customer_segment_validation.ExplainCustomerSegmentDecision(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.status
            if returned_0_0:
                response.outcome.status = returned_0_0
            returned_0_1 = response_0.metric_alert.audit.etag
            if returned_0_1:
                response.impact.audit.etag = returned_0_1
            returned_1_0 = response_1.result.message
            if returned_1_0:
                response.result.message = returned_1_0
            returned_2_0 = response_2.customer_segment.owner.display_name
            if returned_2_0:
                response.impact.assignee.display_name = returned_2_0
            returned_2_1 = response_2.customer_segment.priority
            if returned_2_1:
                response.impact.priority = returned_2_1
            echoed_0 = request.impact_id
            response.impact.impact_id = echoed_0
            echoed_1 = request.impact.subject
            response.impact.subject = echoed_1
            return response

    async def handle_resolve_impact_conflict(
        self,
        request: lineage_v1_impact_sync_service_pb2.ResolveImpactConflictRequest
    ) -> lineage_v1_impact_sync_service_pb2.ResolveImpactConflictResponse:
        """Resolves an impact."""
        deps = self.deps
        response = lineage_v1_impact_sync_service_pb2.ResolveImpactConflictResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ResolveImpactConflict', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'ResolveImpactConflict', {'reason': request.reason})
            await deps.repository.save_impact(request.context.tenant_id, request.impact)
            response_0 = customers_v1_preference_validation_service_pb2.ExplainPreferenceDecisionResponse()
            response_1 = search_v1_search_index_validation_service_pb2.CheckSearchIndexEligibilityResponse()
            response_2 = customers_v1_customer_segment_calculation_service_pb2.ExplainCustomerSegmentCalculationResponse()
            response_3 = lineage_v1_lineage_edge_sync_service_pb2.ResolveLineageEdgeConflictResponse()
            outgoing_0 = customers_v1_preference_validation_service_pb2.ExplainPreferenceDecisionRequest(
                context=request.context,
                preference=customers_v1_customers_pb2.Preference(
                    audit=common_v1_audit_pb2.AuditInfo(created_at=request.impact.audit.created_at),
                    owner=identity_v1_refs_pb2.UserRef(display_name=request.impact.customer.display_name)
                )
            )
            outgoing_1 = search_v1_search_index_validation_service_pb2.CheckSearchIndexEligibilityRequest(
                context=request.context,
                details=search_v1_search_index_validation_service_pb2.CheckSearchIndexEligibilityRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(
                        name=request.impact.requester.name,
                        phone=request.impact.requester.phone
                    )
                ),
                search_index=search_v1_search_pb2.SearchIndex(
                    owner=identity_v1_refs_pb2.UserRef(email=request.impact.customer.email)
                )
            )
            response_0, response_1 = await asyncio.gather(
                deps.clients.customers_preference_validation.ExplainPreferenceDecision(
                    outgoing_0,
                    timeout=deps.settings.timeout
                ),
                deps.clients.search_search_index_validation.CheckSearchIndexEligibility(
                    outgoing_1,
                    timeout=deps.settings.timeout
                ),
            )
            requests_2: list[
                customers_v1_customer_segment_calculation_service_pb2.ExplainCustomerSegmentCalculationRequest
            ] = []
            for item_2 in request.impact.comments:
                outgoing_2 = customers_v1_customer_segment_calculation_service_pb2.ExplainCustomerSegmentCalculationRequest(
                    context=request.context,
                    customer_segment=customers_v1_customers_pb2.CustomerSegment(
                        audit=common_v1_audit_pb2.AuditInfo(
                            created_at=item_2.created_at,
                            updated_at=response_1.search_index.audit.updated_at
                        ),
                        owner=identity_v1_refs_pb2.UserRef(
                            email=item_2.author_email,
                            user_id=response_1.search_index.owner.user_id
                        )
                    )
                )
                requests_2.append(outgoing_2)
            replies_2 = await asyncio.gather(*(
                deps.clients.customers_customer_segment_calculation.ExplainCustomerSegmentCalculation(
                    entry,
                    timeout=deps.settings.timeout
                ) for entry in requests_2
            ))
            if replies_2:
                response_2 = replies_2[-1]
            command_3 = ImpactSyncResolveImpactConflict3Command.model_validate(
                {
                    'context': request.context,
                    'lineage_edge_subject_display_name': response_2.customer_segment.owner.display_name,
                    'lineage_edge_measurements_unit': response_1.search_index.dimensions.unit,
                    'lineage_edge_correlation_id': response_0.result.correlation_id
                }
            )
            outgoing_3 = to_impact_sync_resolve_impact_conflict3_command(command_3)
            response_3 = await deps.clients.lineage_lineage_edge_sync.ResolveLineageEdgeConflict(
                outgoing_3,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.status
            if returned_0_0:
                response.result.status = returned_0_0
            returned_0_1 = response_0.preference.audit.created_at
            returned_0_1_part_1 = response.impact.comments.add()
            if returned_0_1.ListFields():
                returned_0_1_part_1.created_at.MergeFrom(returned_0_1)
            returned_1_0 = response_1.search_index.audit.created_at
            returned_1_0_part_1 = response.impact.comments.add()
            if returned_1_0.ListFields():
                returned_1_0_part_1.created_at.MergeFrom(returned_1_0)
            returned_1_1 = response_1.outcome.message
            if returned_1_1:
                response.outcome.message = returned_1_1
            returned_3_0 = response_3.result.message
            if returned_3_0:
                response.result.message = returned_3_0
            returned_3_1 = response_3.outcome.reference_id
            if returned_3_1:
                response.outcome.reference_id = returned_3_1
            echoed_0 = request.impact_id
            response.impact.impact_id = echoed_0
            echoed_1 = request.impact.status
            response.impact.status = echoed_1
            return response

    async def handle_stream_impact_changes(
        self,
        request: lineage_v1_impact_sync_service_pb2.StreamImpactChangesRequest
    ) -> lineage_v1_impact_sync_service_pb2.StreamImpactChangesResponse:
        """Exchanges changes of impacts with a peer."""
        deps = self.deps
        response = lineage_v1_impact_sync_service_pb2.StreamImpactChangesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('StreamImpactChanges', extra={'fields': {'cursor': request.cursor}})
            await deps.repository.audit(request.context.tenant_id, 'StreamImpactChanges', {'cursor': request.cursor})
            if request.WhichOneof('frame') == 'change':
                await deps.repository.save_impact(request.context.tenant_id, request.change)
            response_0 = lineage_v1_lineage_edge_sync_service_pb2.PushLineageEdgeResponse()
            response_1 = metrics_v1_metric_series_history_service_pb2.CompareMetricSeriesVersionsResponse()
            response_2 = forecasting_v1_forecast_model_query_service_pb2.ExportForecastModelsResponse()
            response_3 = lineage_v1_lineage_node_reporting_service_pb2.CountLineageNodeTotalsResponse()
            outgoing_0 = lineage_v1_lineage_edge_sync_service_pb2.PushLineageEdgeRequest()
            outgoing_0.context.CopyFrom(request.context)
            if request.WhichOneof('frame') == 'change':
                outgoing_0.lineage_edge.subject.impact_id = request.change.impact_id
            if request.WhichOneof('frame') == 'change':
                outgoing_0.lineage_edge.subject.display_name = request.change.assignee.display_name
            if request.WhichOneof('frame') == 'change':
                outgoing_0.lineage_edge.subject.priority = request.change.priority
            if request.WhichOneof('frame') == 'ack':
                outgoing_0.lineage_edge.sequence = request.ack.sequence
            response_0 = await deps.clients.lineage_lineage_edge_sync.PushLineageEdge(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = metrics_v1_metric_series_history_service_pb2.CompareMetricSeriesVersionsRequest(
                context=request.context,
                metric_series=metrics_v1_metrics_pb2.MetricSeries(
                    audit=common_v1_audit_pb2.AuditInfo(
                        created_at=request.change.audit.created_at,
                        etag=request.change.audit.etag,
                        updated_at=request.change.audit.updated_at
                    ),
                    owner=identity_v1_refs_pb2.UserRef(email=request.change.requester.email)
                )
            )
            response_1 = await hooks.impact_sync_stream_impact_changes1(
                deps.clients.metrics_metric_series_history,
                outgoing_1,
                deps.settings.timeout
            )
            outgoing_2 = forecasting_v1_forecast_model_query_service_pb2.ExportForecastModelsRequest(
                context=request.context,
                filter=forecasting_v1_forecast_model_query_service_pb2.ExportForecastModelsRequest.Filter(
                    created_after=response_1.metric_series.audit.created_at,
                    labels=dict(response_0.result.details),
                    owner_id=response_0.result.correlation_id,
                    region=response_1.metric_series.address.region
                )
            )
            async for chunk_2 in deps.clients.forecasting_forecast_model_query.ExportForecastModels(
                outgoing_2,
                timeout=deps.settings.timeout
            ):
                response_2 = chunk_2
            outgoing_3 = lineage_v1_lineage_node_reporting_service_pb2.CountLineageNodeTotalsRequest()
            outgoing_3.context.CopyFrom(request.context)
            if response_1.metric_series.WhichOneof('locator') == 'address':
                outgoing_3.filter.region = response_1.metric_series.address.region
            if request.WhichOneof('frame') == 'change':
                outgoing_3.filter.created_after.CopyFrom(request.change.audit.updated_at)
            response_3 = await deps.clients.lineage_lineage_node_reporting.CountLineageNodeTotals(
                outgoing_3,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.status
            if returned_0_0:
                response.result.status = returned_0_0
            returned_0_1 = response_0.lineage_edge.correlation_id
            if returned_0_1:
                response.result.correlation_id = returned_0_1
            returned_1_0 = response_1.metric_series.owner.email
            if returned_1_0:
                response.impact.requester.email = returned_1_0
            returned_3_0 = response_3.result.message
            if returned_3_0:
                response.result.message = returned_3_0
            echoed_0 = request.ack.sequence
            response.sequence = echoed_0
            echoed_1 = request.change.priority
            response.impact.priority = echoed_1
            return response

    async def handle_sync_impacts(
        self,
        request: lineage_v1_impact_sync_service_pb2.SyncImpactsRequest
    ) -> lineage_v1_impact_sync_service_pb2.SyncImpactsResponse:
        """Syncs an impact."""
        deps = self.deps
        response = lineage_v1_impact_sync_service_pb2.SyncImpactsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SyncImpacts', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'SyncImpacts', {'reason': request.reason})
            await deps.repository.save_impact(request.context.tenant_id, request.impact)
            response_0 = audit_v1_audit_event_query_service_pb2.SuggestAuditEventsResponse()
            response_1 = metrics_v1_metric_alert_export_service_pb2.StreamMetricAlertExportResponse()
            response_2 = lineage_v1_lineage_edge_validation_service_pb2.ValidateLineageEdgeResponse()
            response_3 = messaging_v1_conversation_calculation_service_pb2.RecalculateConversationsResponse()
            outgoing_0 = audit_v1_audit_event_query_service_pb2.SuggestAuditEventsRequest(
                context=request.context,
                filter=audit_v1_audit_event_query_service_pb2.SuggestAuditEventsRequest.Filter(
                    created_after=request.impact.audit.updated_at,
                    owner_id=request.impact.customer.customer_id
                )
            )
            steps_0 = [
                partial(
                    deps.clients.audit_audit_event_query.SuggestAuditEvents,
                    outgoing_0,
                    timeout=deps.settings.timeout
                )
            ]
            results_0 = await run_steps(steps_0)
            response_0 = results_0[-1]
            outgoing_1 = metrics_v1_metric_alert_export_service_pb2.StreamMetricAlertExportRequest(
                context=request.context,
                filter=metrics_v1_metric_alert_export_service_pb2.StreamMetricAlertExportRequest.Filter(
                    created_after=request.impact.audit.created_at,
                    labels=dict(request.impact.custom_fields),
                    owner_id=request.impact.sla.policy_id
                )
            )
            async for chunk_1 in deps.clients.metrics_metric_alert_export.StreamMetricAlertExport(
                outgoing_1,
                timeout=deps.settings.timeout
            ):
                response_1 = chunk_1
            outgoing_2 = lineage_v1_lineage_edge_validation_service_pb2.ValidateLineageEdgeRequest(
                context=request.context,
                details=lineage_v1_lineage_edge_validation_service_pb2.ValidateLineageEdgeRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(
                        email=request.impact.assignee.email,
                        preferred_channel=request.impact.requester.preferred_channel
                    )
                )
            )
            response_2 = cast(lineage_v1_lineage_edge_validation_service_pb2.ValidateLineageEdgeResponse, await deps.bus.request(
                'acme.lineage.v1.ImpactSyncService/SyncImpacts/2', outgoing_2, deps.settings.timeout,
            ))
            outgoing_3 = messaging_v1_conversation_calculation_service_pb2.RecalculateConversationsRequest(
                context=request.context,
                conversation=messaging_v1_messaging_pb2.Conversation(
                    assignee=identity_v1_refs_pb2.UserRef(email=request.impact.customer.email),
                    audit=common_v1_audit_pb2.AuditInfo(created_by=request.impact.audit.created_by),
                    sla=messaging_v1_messaging_pb2.ConversationSla(breached=request.impact.sla.breached)
                )
            )
            response_3 = await deps.clients.messaging_conversation_calculation.RecalculateConversations(
                outgoing_3,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.details
            response.result.details.update(returned_0_0)
            returned_0_1 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_1)
            returned_2_0 = response_2.outcome.next_steps
            response.outcome.next_steps.extend(returned_2_0)
            returned_2_1 = response_2.result.reference_ids
            response.result.reference_ids.extend(returned_2_1)
            returned_3_0 = response_3.result.reference_ids
            response.result.reference_ids.extend(returned_3_0)
            echoed_0 = request.impact_id
            response.impact.impact_id = echoed_0
            echoed_1 = request.impact.priority
            response.impact.priority = echoed_1
            return response
