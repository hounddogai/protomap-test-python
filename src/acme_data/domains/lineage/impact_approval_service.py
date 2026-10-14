"""Routes impacts through approval, with escalation and delegation."""

from __future__ import annotations

from collections.abc import AsyncIterator
from collections.abc import Awaitable
from collections.abc import Callable
from functools import partial
import asyncio
import logging

from google.protobuf.any_pb2 import Any as AnyMessage
from google.protobuf.json_format import MessageToJson
from google.protobuf.json_format import Parse
import grpc

from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.customers.v1 import customers_pb2 as customers_v1_customers_pb2
from acme.customers.v1 import household_validation_service_pb2 as customers_v1_household_validation_service_pb2
from acme.customers.v1 import refs_pb2 as customers_v1_refs_pb2
from acme.datasets.v1 import (
    dataset_version_validation_service_pb2 as datasets_v1_dataset_version_validation_service_pb2,
)
from acme.datasets.v1 import datasets_pb2 as datasets_v1_datasets_pb2
from acme.forecasting.v1 import forecasting_pb2 as forecasting_v1_forecasting_pb2
from acme.forecasting.v1 import scenario_validation_service_pb2 as forecasting_v1_scenario_validation_service_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.labeling.v1 import annotation_calculation_service_pb2 as labeling_v1_annotation_calculation_service_pb2
from acme.labeling.v1 import labeling_pb2 as labeling_v1_labeling_pb2
from acme.labeling.v1 import labeling_task_query_service_pb2 as labeling_v1_labeling_task_query_service_pb2
from acme.labeling.v1 import refs_pb2 as labeling_v1_refs_pb2
from acme.lineage.v1 import impact_approval_service_pb2 as lineage_v1_impact_approval_service_pb2
from acme.lineage.v1 import impact_approval_service_pb2_grpc as lineage_v1_impact_approval_service_pb2_grpc
from acme.lineage.v1 import impact_import_service_pb2 as lineage_v1_impact_import_service_pb2
from acme.lineage.v1 import impact_lifecycle_service_pb2 as lineage_v1_impact_lifecycle_service_pb2
from acme.lineage.v1 import lineage_edge_import_service_pb2 as lineage_v1_lineage_edge_import_service_pb2
from acme.lineage.v1 import lineage_edge_lifecycle_service_pb2 as lineage_v1_lineage_edge_lifecycle_service_pb2
from acme.lineage.v1 import lineage_edge_reporting_service_pb2 as lineage_v1_lineage_edge_reporting_service_pb2
from acme.lineage.v1 import lineage_node_approval_service_pb2 as lineage_v1_lineage_node_approval_service_pb2
from acme.lineage.v1 import lineage_pb2 as lineage_v1_lineage_pb2
from acme.lineage.v1 import refs_pb2 as lineage_v1_refs_pb2
from acme.search.v1 import search_index_query_service_pb2 as search_v1_search_index_query_service_pb2
from acme.seating.v1 import seat_map_service_pb2 as seating_v1_seat_map_service_pb2
from acme.seating.v1 import seating_pb2 as seating_v1_seating_pb2

from acme_data.domains.lineage.adapters import ImpactApprovalDelegateImpactApproval1Adapter
from acme_data.domains.lineage.dependencies import Dependencies
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import run_steps
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class ImpactApprovalServicer(lineage_v1_impact_approval_service_pb2_grpc.ImpactApprovalServiceServicer):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    async def ApproveImpact(
        self, request: lineage_v1_impact_approval_service_pb2.ApproveImpactRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_impact_approval_service_pb2.ApproveImpactResponse:
        """Approves an impact."""
        return await self.handle_approve_impact(request)

    @rpc_errors
    async def DelegateImpactApproval(
        self, request: lineage_v1_impact_approval_service_pb2.DelegateImpactApprovalRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_impact_approval_service_pb2.DelegateImpactApprovalResponse:
        """Delegates an impact."""
        return await self.handle_delegate_impact_approval(request)

    @rpc_errors
    @retry_transient
    async def GetImpactApprovalStatus(
        self, request: lineage_v1_impact_approval_service_pb2.GetImpactApprovalStatusRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_impact_approval_service_pb2.GetImpactApprovalStatusResponse:
        """Returns an impact."""
        return await self.handle_get_impact_approval_status(request)

    @rpc_errors
    @retry_transient
    async def ListPendingImpacts(
        self, request: lineage_v1_impact_approval_service_pb2.ListPendingImpactsRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_impact_approval_service_pb2.ListPendingImpactsResponse:
        """Lists impacts a page at a time."""
        return await self.handle_list_pending_impacts(request)

    @rpc_errors
    async def RecallImpact(
        self, request: lineage_v1_impact_approval_service_pb2.RecallImpactRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_impact_approval_service_pb2.RecallImpactResponse:
        """Recalls an impact."""
        return await self.handle_recall_impact(request)

    @rpc_errors
    async def RejectImpact(
        self, request: lineage_v1_impact_approval_service_pb2.RejectImpactRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_impact_approval_service_pb2.RejectImpactResponse:
        """Rejects an impact."""
        return await self.handle_reject_impact(request)

    @rpc_errors
    async def SubmitImpact(
        self, request: lineage_v1_impact_approval_service_pb2.SubmitImpactRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_impact_approval_service_pb2.SubmitImpactResponse:
        """Submits an impact."""
        return await self.handle_submit_impact(request)

    async def handle_approve_impact(
        self,
        request: lineage_v1_impact_approval_service_pb2.ApproveImpactRequest
    ) -> lineage_v1_impact_approval_service_pb2.ApproveImpactResponse:
        """Approves an impact."""
        deps = self.deps
        response = lineage_v1_impact_approval_service_pb2.ApproveImpactResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ApproveImpact', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'ApproveImpact', {'reason': request.reason})
            await deps.repository.save_impact(request.context.tenant_id, request.impact)
            response_0 = lineage_v1_lineage_edge_import_service_pb2.MapLineageEdgeImportColumnsResponse()
            response_1 = lineage_v1_lineage_node_approval_service_pb2.RejectLineageNodeResponse()
            response_2 = seating_v1_seat_map_service_pb2.CloneSeatMapResponse()
            outgoing_0 = lineage_v1_lineage_edge_import_service_pb2.MapLineageEdgeImportColumnsRequest(
                context=request.context,
                details=lineage_v1_lineage_edge_import_service_pb2.MapLineageEdgeImportColumnsRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(phone=request.impact.requester.phone)
                ),
                lineage_edge=lineage_v1_lineage_pb2.LineageEdge(
                    subject=lineage_v1_refs_pb2.ImpactRef(display_name=request.details.approver.display_name)
                )
            )
            outgoing_1 = lineage_v1_lineage_node_approval_service_pb2.RejectLineageNodeRequest(
                context=request.context,
                lineage_node=lineage_v1_lineage_pb2.LineageNode(
                    children=[
                        lineage_v1_lineage_pb2.LineageNode(
                            audit=common_v1_audit_pb2.AuditInfo(created_by=request.impact.audit.created_by),
                            children=[
                                lineage_v1_lineage_pb2.LineageNode(
                                    manager=identity_v1_refs_pb2.UserRef(
                                        email=request.impact.assignee.email,
                                        user_id=request.details.approver.user_id
                                    )
                                )
                            ]
                        )
                    ]
                )
            )
            response_0, response_1 = await asyncio.gather(
                deps.clients.lineage_lineage_edge_import.MapLineageEdgeImportColumns(
                    outgoing_0,
                    timeout=deps.settings.timeout
                ),
                deps.clients.lineage_lineage_node_approval.RejectLineageNode(outgoing_1, timeout=deps.settings.timeout),
            )
            callbacks_2: list[Callable[[], Awaitable[seating_v1_seat_map_service_pb2.CloneSeatMapResponse]]] = []
            for item_2 in request.impact.comments:
                outgoing_2 = seating_v1_seat_map_service_pb2.CloneSeatMapRequest(
                    context=request.context,
                    seat_map=seating_v1_seating_pb2.SeatMap(
                        children=[
                            seating_v1_seating_pb2.SeatMap(
                                children=[
                                    seating_v1_seating_pb2.SeatMap(
                                        audit=common_v1_audit_pb2.AuditInfo(created_at=item_2.created_at),
                                        manager=identity_v1_refs_pb2.UserRef(email=item_2.author_email)
                                    )
                                ]
                            )
                        ]
                    )
                )
                async def send_2(
                    payload: seating_v1_seat_map_service_pb2.CloneSeatMapRequest = outgoing_2
                ) -> seating_v1_seat_map_service_pb2.CloneSeatMapResponse:
                    return await deps.clients.seating_seat_map.CloneSeatMap(payload, timeout=deps.settings.timeout)
                callbacks_2.append(send_2)
            for callback_2 in callbacks_2:
                response_2 = await callback_2()
            returned_0_0 = response_0.result.status
            if returned_0_0:
                response.outcome.status = returned_0_0
            returned_0_1 = response_0.lineage_edge.subject.display_name
            if returned_0_1:
                response.impact.assignee.display_name = returned_0_1
            returned_1_0 = response_1.lineage_node.audit.updated_by
            if returned_1_0:
                response.impact.audit.updated_by = returned_1_0
            returned_1_1 = response_1.lineage_node.audit.etag
            if returned_1_1:
                response.impact.audit.etag = returned_1_1
            echoed_0 = request.impact_id
            response.impact.impact_id = echoed_0
            echoed_1 = request.impact.subject
            response.impact.subject = echoed_1
            return response

    async def handle_delegate_impact_approval(
        self,
        request: lineage_v1_impact_approval_service_pb2.DelegateImpactApprovalRequest
    ) -> lineage_v1_impact_approval_service_pb2.DelegateImpactApprovalResponse:
        """Delegates an impact."""
        deps = self.deps
        response = lineage_v1_impact_approval_service_pb2.DelegateImpactApprovalResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('DelegateImpactApproval', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'DelegateImpactApproval', {'reason': request.reason})
            await deps.repository.save_impact(request.context.tenant_id, request.impact)
            response_0 = search_v1_search_index_query_service_pb2.FindSearchIndexesResponse()
            response_1 = lineage_v1_lineage_edge_lifecycle_service_pb2.ScheduleLineageEdgeExpiryResponse()
            outgoing_0 = search_v1_search_index_query_service_pb2.FindSearchIndexesRequest(
                context=request.context,
                filter=search_v1_search_index_query_service_pb2.FindSearchIndexesRequest.Filter(
                    created_after=request.impact.audit.created_at
                )
            )
            steps_0 = [
                partial(
                    deps.clients.search_search_index_query.FindSearchIndexes,
                    outgoing_0,
                    timeout=deps.settings.timeout
                )
            ]
            results_0 = await run_steps(steps_0)
            response_0 = results_0[-1]
            outgoing_1 = lineage_v1_lineage_edge_lifecycle_service_pb2.ScheduleLineageEdgeExpiryRequest(
                context=request.context,
                details=lineage_v1_lineage_edge_lifecycle_service_pb2.ScheduleLineageEdgeExpiryRequest.Details(
                    notify=common_v1_contact_pb2.ContactInfo(
                        email=request.impact.assignee.email,
                        name=request.impact.requester.name,
                        phone=request.impact.requester.phone
                    )
                ),
                lineage_edge=lineage_v1_lineage_pb2.LineageEdge(
                    subject=lineage_v1_refs_pb2.ImpactRef(priority=request.impact.priority)
                )
            )
            response_1 = await ImpactApprovalDelegateImpactApproval1Adapter(
                deps.clients.lineage_lineage_edge_lifecycle,
                deps.settings.timeout
            )(outgoing_1)
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.result.message = returned_0_0
            returned_0_1 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_1)
            returned_1_0 = response_1.result.reference_ids
            response.result.reference_ids.extend(returned_1_0)
            echoed_0 = request.impact_id
            response.impact.impact_id = echoed_0
            echoed_1 = request.details.effective_at
            response.outcome.effective_at.CopyFrom(echoed_1)
            return response

    async def handle_get_impact_approval_status(
        self,
        request: lineage_v1_impact_approval_service_pb2.GetImpactApprovalStatusRequest
    ) -> lineage_v1_impact_approval_service_pb2.GetImpactApprovalStatusResponse:
        """Returns an impact."""
        deps = self.deps
        response = lineage_v1_impact_approval_service_pb2.GetImpactApprovalStatusResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('GetImpactApprovalStatus', extra={'fields': {'domain': 'lineage'}})
            await deps.repository.audit(request.context.tenant_id, 'GetImpactApprovalStatus', {})
            response_0 = forecasting_v1_scenario_validation_service_pb2.ValidateScenarioResponse()
            outgoing_0 = forecasting_v1_scenario_validation_service_pb2.ValidateScenarioRequest(
                context=request.context,
                details=forecasting_v1_scenario_validation_service_pb2.ValidateScenarioRequest.Details(
                    locale=request.context.locale
                ),
                scenario=forecasting_v1_forecasting_pb2.Scenario(
                    assignee=identity_v1_refs_pb2.UserRef(user_id=request.context.actor.user_id),
                    requester=common_v1_contact_pb2.ContactInfo(email=request.context.actor.email)
                )
            )
            response_0 = await deps.clients.forecasting_scenario_validation.ValidateScenario(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.scenario.audit.created_at
            if returned_0_0.ListFields():
                response.impact.audit.created_at.MergeFrom(returned_0_0)
            returned_0_1 = response_0.scenario.audit.updated_at
            if returned_0_1.ListFields():
                response.impact.audit.updated_at.MergeFrom(returned_0_1)
            echoed_0 = request.impact_id
            response.impact.impact_id = echoed_0
            return response

    async def handle_list_pending_impacts(
        self,
        request: lineage_v1_impact_approval_service_pb2.ListPendingImpactsRequest
    ) -> lineage_v1_impact_approval_service_pb2.ListPendingImpactsResponse:
        """Lists impacts a page at a time."""
        deps = self.deps
        response = lineage_v1_impact_approval_service_pb2.ListPendingImpactsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ListPendingImpacts', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(request.context.tenant_id, 'ListPendingImpacts', {'order_by': request.order_by})
            return response

    async def handle_recall_impact(
        self,
        request: lineage_v1_impact_approval_service_pb2.RecallImpactRequest
    ) -> lineage_v1_impact_approval_service_pb2.RecallImpactResponse:
        """Recalls an impact."""
        deps = self.deps
        response = lineage_v1_impact_approval_service_pb2.RecallImpactResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('RecallImpact', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'RecallImpact', {'reason': request.reason})
            await deps.repository.save_impact(request.context.tenant_id, request.impact)
            response_0 = labeling_v1_labeling_task_query_service_pb2.CountLabelingTasksResponse()
            response_1 = lineage_v1_impact_import_service_pb2.GetImpactImportStatusResponse()
            response_2 = customers_v1_household_validation_service_pb2.ValidateHouseholdResponse()
            response_3 = lineage_v1_impact_lifecycle_service_pb2.ReinstateImpactResponse()
            outgoing_0 = labeling_v1_labeling_task_query_service_pb2.CountLabelingTasksRequest(
                context=request.context,
                filter=labeling_v1_labeling_task_query_service_pb2.CountLabelingTasksRequest.Filter(
                    created_after=request.impact.audit.updated_at,
                    labels=dict(request.annotations),
                    owner_id=request.impact.sla.policy_id
                )
            )
            response_0 = await deps.clients.labeling_labeling_task_query.CountLabelingTasks(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = lineage_v1_impact_import_service_pb2.GetImpactImportStatusRequest(
                context=request.context,
                impact_id=request.impact_id
            )
            method_name_1 = 'GetImpactImportStatus'
            response_1 = await getattr(
                deps.clients.lineage_impact_import,
                method_name_1
            )(outgoing_1, timeout=deps.settings.timeout)
            async for item_2 in async_messages(request.impact.comments):
                outgoing_2 = customers_v1_household_validation_service_pb2.ValidateHouseholdRequest(
                    context=request.context,
                    household=customers_v1_customers_pb2.Household(
                        children=[
                            customers_v1_customers_pb2.Household(
                                audit=common_v1_audit_pb2.AuditInfo(created_at=item_2.created_at)
                            )
                        ]
                    )
                )
                response_2 = await deps.clients.customers_household_validation.ValidateHousehold(
                    outgoing_2,
                    timeout=deps.settings.timeout
                )
            outgoing_3 = lineage_v1_impact_lifecycle_service_pb2.ReinstateImpactRequest()
            outgoing_3.context.CopyFrom(request.context)
            outgoing_3.impact_id = request.impact.impact_id
            if request.impact.WhichOneof('origin') == 'customer':
                outgoing_3.details.new_owner.display_name = request.impact.customer.display_name
            outgoing_3.details.notify_contact.email = request.impact.assignee.email
            outgoing_3.details.new_owner.user_id = response_1.impact.assignee.user_id
            outgoing_3.details.notify_contact.preferred_channel = response_1.impact.requester.preferred_channel
            response_3 = await deps.clients.lineage_impact_lifecycle.ReinstateImpact(
                outgoing_3,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.details
            response.result.details.update(returned_0_0)
            returned_1_0 = response_1.impact.tags
            response.impact.tags.extend(returned_1_0)
            returned_1_1 = response_1.impact.impact_id
            if returned_1_1:
                response.impact.impact_id = returned_1_1
            returned_3_0 = response_3.impact.custom_fields
            response.impact.custom_fields.update(returned_3_0)
            returned_3_1 = response_3.impact.assignee.email
            if returned_3_1:
                response.impact.assignee.email = returned_3_1
            echoed_0 = request.impact.subject
            response.impact.subject = echoed_0
            echoed_1 = request.details.effective_at
            response.outcome.effective_at.CopyFrom(echoed_1)
            return response

    async def handle_reject_impact(
        self,
        request: lineage_v1_impact_approval_service_pb2.RejectImpactRequest
    ) -> lineage_v1_impact_approval_service_pb2.RejectImpactResponse:
        """Rejects an impact."""
        deps = self.deps
        response = lineage_v1_impact_approval_service_pb2.RejectImpactResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('RejectImpact', extra={'fields': {'approver_email': request.details.approver_email}})
            await deps.repository.audit(
                request.context.tenant_id,
                'RejectImpact',
                {'approver_email': request.details.approver_email}
            )
            await deps.repository.save_impact(request.context.tenant_id, request.impact)
            response_0 = search_v1_search_index_query_service_pb2.SummarizeSearchIndexesResponse()
            response_1 = lineage_v1_impact_lifecycle_service_pb2.TerminateImpactResponse()
            response_2 = datasets_v1_dataset_version_validation_service_pb2.CheckDatasetVersionEligibilityResponse()
            response_3 = lineage_v1_lineage_edge_reporting_service_pb2.StreamLineageEdgeMetricsResponse()
            outgoing_0 = search_v1_search_index_query_service_pb2.SummarizeSearchIndexesRequest(
                context=request.context,
                reason=request.reason
            )
            document_0 = MessageToJson(outgoing_0, preserving_proto_field_name=True)
            outgoing_0 = Parse(document_0, search_v1_search_index_query_service_pb2.SummarizeSearchIndexesRequest())
            response_0 = await deps.clients.search_search_index_query.SummarizeSearchIndexes(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = lineage_v1_impact_lifecycle_service_pb2.TerminateImpactRequest()
            outgoing_1.context.CopyFrom(request.context)
            outgoing_1.impact_id = request.impact.impact_id
            outgoing_1.details.notify_contact.phone = request.impact.requester.phone
            outgoing_1.details.new_owner.display_name = request.details.approver.display_name
            merged_1 = lineage_v1_impact_lifecycle_service_pb2.TerminateImpactRequest()
            merged_1.MergeFrom(outgoing_1)
            outgoing_1.CopyFrom(merged_1)
            response_1 = await deps.clients.lineage_impact_lifecycle.TerminateImpact(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = datasets_v1_dataset_version_validation_service_pb2.CheckDatasetVersionEligibilityRequest(
                context=request.context,
                dataset_version=datasets_v1_datasets_pb2.DatasetVersion(
                    subject=customers_v1_refs_pb2.CustomerRef(
                        display_name=response_1.impact.assignee.display_name,
                        email=response_1.impact.requester.email
                    )
                ),
                details=datasets_v1_dataset_version_validation_service_pb2.CheckDatasetVersionEligibilityRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(
                        preferred_channel=request.impact.requester.preferred_channel
                    )
                )
            )
            envelope_2 = AnyMessage()
            envelope_2.Pack(outgoing_2)
            outgoing_2 = datasets_v1_dataset_version_validation_service_pb2.CheckDatasetVersionEligibilityRequest()
            if not envelope_2.Unpack(outgoing_2):
                raise ValueError("partner envelope contains the wrong request type")
            response_2 = await deps.clients.datasets_dataset_version_validation.CheckDatasetVersionEligibility(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            outgoing_3 = lineage_v1_lineage_edge_reporting_service_pb2.StreamLineageEdgeMetricsRequest(
                context=request.context,
                subscriber=common_v1_contact_pb2.ContactInfo(
                    email=request.impact.assignee.email,
                    phone=response_1.impact.requester.phone
                )
            )
            async for chunk_3 in deps.clients.lineage_lineage_edge_reporting.StreamLineageEdgeMetrics(
                outgoing_3,
                timeout=deps.settings.timeout
            ):
                response_3 = chunk_3
            returned_0_0 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_0)
            returned_0_1 = response_0.result.status
            if returned_0_1:
                response.outcome.status = returned_0_1
            returned_1_0 = response_1.result.correlation_id
            if returned_1_0:
                response.result.correlation_id = returned_1_0
            returned_1_1 = response_1.outcome.message
            if returned_1_1:
                response.outcome.message = returned_1_1
            returned_2_0 = response_2.outcome.status
            if returned_2_0:
                response.outcome.status = returned_2_0
            echoed_0 = request.impact_id
            response.impact.impact_id = echoed_0
            echoed_1 = request.impact.custom_fields
            response.impact.custom_fields.update(echoed_1)
            return response

    async def handle_submit_impact(
        self,
        request: lineage_v1_impact_approval_service_pb2.SubmitImpactRequest
    ) -> lineage_v1_impact_approval_service_pb2.SubmitImpactResponse:
        """Submits an impact."""
        deps = self.deps
        response = lineage_v1_impact_approval_service_pb2.SubmitImpactResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SubmitImpact', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'SubmitImpact', {'reason': request.reason})
            await deps.repository.save_impact(request.context.tenant_id, request.impact)
            response_0 = lineage_v1_impact_import_service_pb2.CancelImpactImportResponse()
            response_1 = search_v1_search_index_query_service_pb2.CountSearchIndexesResponse()
            response_2 = labeling_v1_annotation_calculation_service_pb2.RecalculateAnnotationsResponse()
            response_3 = customers_v1_household_validation_service_pb2.ScoreHouseholdResponse()
            outgoing_0 = lineage_v1_impact_import_service_pb2.CancelImpactImportRequest(
                context=request.context,
                details=lineage_v1_impact_import_service_pb2.CancelImpactImportRequest.Details(
                    notify_contact=common_v1_contact_pb2.ContactInfo(email=request.impact.requester.email)
                ),
                impact_id=request.impact.impact_id
            )
            outgoing_1 = search_v1_search_index_query_service_pb2.CountSearchIndexesRequest(
                context=request.context,
                filter=search_v1_search_index_query_service_pb2.CountSearchIndexesRequest.Filter(
                    created_after=request.impact.audit.updated_at
                )
            )
            outgoing_3 = customers_v1_household_validation_service_pb2.ScoreHouseholdRequest(
                context=request.context,
                household=customers_v1_customers_pb2.Household(
                    children=[
                        customers_v1_customers_pb2.Household(
                            children=[
                                customers_v1_customers_pb2.Household(
                                    audit=common_v1_audit_pb2.AuditInfo(created_at=request.impact.audit.created_at),
                                    manager=identity_v1_refs_pb2.UserRef(
                                        display_name=request.impact.assignee.display_name
                                    )
                                )
                            ]
                        )
                    ]
                )
            )
            response_0, response_1, response_3 = await asyncio.gather(
                deps.clients.lineage_impact_import.CancelImpactImport(outgoing_0, timeout=deps.settings.timeout),
                deps.clients.search_search_index_query.CountSearchIndexes(outgoing_1, timeout=deps.settings.timeout),
                deps.clients.customers_household_validation.ScoreHousehold(outgoing_3, timeout=deps.settings.timeout),
            )
            outgoing_2 = labeling_v1_annotation_calculation_service_pb2.RecalculateAnnotationsRequest(
                annotation=labeling_v1_labeling_pb2.Annotation(
                    subject=labeling_v1_refs_pb2.LabelingTaskRef(
                        display_name=response_0.impact.customer.display_name,
                        priority=request.impact.priority
                    )
                ),
                context=request.context
            )
            send_2 = partial(
                deps.clients.labeling_annotation_calculation.RecalculateAnnotations,
                timeout=deps.settings.timeout
            )
            response_2 = await send_2(outgoing_2)
            returned_0_0 = response_0.impact.requester.name
            if returned_0_0.ListFields():
                response.impact.requester.name.MergeFrom(returned_0_0)
            returned_0_1 = response_0.impact.requester.email
            if returned_0_1:
                response.impact.assignee.email = returned_0_1
            returned_1_0 = response_1.result.details
            response.result.details.update(returned_1_0)
            returned_2_0 = response_2.result.message
            if returned_2_0:
                response.result.message = returned_2_0
            returned_2_1 = response_2.result.details
            response.result.details.update(returned_2_1)
            returned_3_0 = response_3.household.audit.updated_by
            if returned_3_0:
                response.impact.audit.updated_by = returned_3_0
            echoed_0 = request.impact_id
            response.impact.impact_id = echoed_0
            echoed_1 = request.details.effective_at
            response.outcome.effective_at.CopyFrom(echoed_1)
            return response
