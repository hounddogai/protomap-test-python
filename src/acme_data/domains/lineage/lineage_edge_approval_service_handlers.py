"""Reusable transport mixin for LineageEdgeApprovalService."""

from __future__ import annotations

from collections.abc import AsyncIterator
from collections.abc import Awaitable
from collections.abc import Callable
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

from acme.analytics.v1 import analytics_event_service_pb2 as analytics_v1_analytics_event_service_pb2
from acme.analytics.v1 import analytics_pb2 as analytics_v1_analytics_pb2
from acme.analytics.v1 import refs_pb2 as analytics_v1_refs_pb2
from acme.audit.v1 import audit_event_service_pb2 as audit_v1_audit_event_service_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.customers.v1 import (
    consent_record_validation_service_pb2 as customers_v1_consent_record_validation_service_pb2,
)
from acme.customers.v1 import customer_service_pb2 as customers_v1_customer_service_pb2
from acme.customers.v1 import customers_pb2 as customers_v1_customers_pb2
from acme.customers.v1 import household_calculation_service_pb2 as customers_v1_household_calculation_service_pb2
from acme.customers.v1 import preference_calculation_service_pb2 as customers_v1_preference_calculation_service_pb2
from acme.customers.v1 import preference_validation_service_pb2 as customers_v1_preference_validation_service_pb2
from acme.customers.v1 import refs_pb2 as customers_v1_refs_pb2
from acme.forecasting.v1 import forecasting_pb2 as forecasting_v1_forecasting_pb2
from acme.forecasting.v1 import refs_pb2 as forecasting_v1_refs_pb2
from acme.forecasting.v1 import scenario_calculation_service_pb2 as forecasting_v1_scenario_calculation_service_pb2
from acme.fulfillment.v1 import fulfillment_query_service_pb2 as fulfillment_v1_fulfillment_query_service_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.labeling.v1 import label_set_validation_service_pb2 as labeling_v1_label_set_validation_service_pb2
from acme.labeling.v1 import labeling_pb2 as labeling_v1_labeling_pb2
from acme.lineage.v1 import impact_lifecycle_service_pb2 as lineage_v1_impact_lifecycle_service_pb2
from acme.lineage.v1 import impact_reporting_service_pb2 as lineage_v1_impact_reporting_service_pb2
from acme.lineage.v1 import impact_sync_service_pb2 as lineage_v1_impact_sync_service_pb2
from acme.lineage.v1 import impact_sync_service_pb2_grpc as lineage_v1_impact_sync_service_pb2_grpc
from acme.lineage.v1 import lineage_edge_approval_service_pb2 as lineage_v1_lineage_edge_approval_service_pb2
from acme.lineage.v1 import lineage_edge_import_service_pb2 as lineage_v1_lineage_edge_import_service_pb2
from acme.lineage.v1 import lineage_edge_lifecycle_service_pb2 as lineage_v1_lineage_edge_lifecycle_service_pb2
from acme.lineage.v1 import lineage_edge_reporting_service_pb2 as lineage_v1_lineage_edge_reporting_service_pb2
from acme.lineage.v1 import lineage_edge_sync_service_pb2 as lineage_v1_lineage_edge_sync_service_pb2
from acme.lineage.v1 import lineage_node_approval_service_pb2 as lineage_v1_lineage_node_approval_service_pb2
from acme.lineage.v1 import lineage_pb2 as lineage_v1_lineage_pb2
from acme.lineage.v1 import refs_pb2 as lineage_v1_refs_pb2
from acme.metrics.v1 import metric_alert_history_service_pb2 as metrics_v1_metric_alert_history_service_pb2
from acme.metrics.v1 import metrics_pb2 as metrics_v1_metrics_pb2
from acme.modelregistry.v1 import (
    model_version_calculation_service_pb2 as modelregistry_v1_model_version_calculation_service_pb2,
)
from acme.modelregistry.v1 import modelregistry_pb2 as modelregistry_v1_modelregistry_pb2
from acme.pipelines.v1 import (
    pipeline_step_calculation_service_pb2 as pipelines_v1_pipeline_step_calculation_service_pb2,
)
from acme.pipelines.v1 import pipelines_pb2 as pipelines_v1_pipelines_pb2

from acme_data.domains.lineage.adapters import LineageEdgeApprovalListPendingLineageEdges1Adapter
from acme_data.domains.lineage.dependencies import Dependencies
from acme_data.domains.lineage.models import LineageEdgeApprovalDelegateLineageEdgeApproval3Command
from acme_data.domains.lineage.models import to_lineage_edge_approval_delegate_lineage_edge_approval3_command
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_id
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class LineageEdgeApprovalServicerHandlers:
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    async def ApproveLineageEdge(
        self, request: lineage_v1_lineage_edge_approval_service_pb2.ApproveLineageEdgeRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_lineage_edge_approval_service_pb2.ApproveLineageEdgeResponse:
        """Approves a lineage edge."""
        return await self.handle_approve_lineage_edge(request)

    @rpc_errors
    async def CommentLineageEdgeApproval(
        self, request: lineage_v1_lineage_edge_approval_service_pb2.CommentLineageEdgeApprovalRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_lineage_edge_approval_service_pb2.CommentLineageEdgeApprovalResponse:
        """Comments a lineage edge."""
        return await self.handle_comment_lineage_edge_approval(request)

    @rpc_errors
    async def DelegateLineageEdgeApproval(
        self, request: lineage_v1_lineage_edge_approval_service_pb2.DelegateLineageEdgeApprovalRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_lineage_edge_approval_service_pb2.DelegateLineageEdgeApprovalResponse:
        """Delegates a lineage edge."""
        return await self.handle_delegate_lineage_edge_approval(request)

    @rpc_errors
    async def EscalateLineageEdge(
        self, request: lineage_v1_lineage_edge_approval_service_pb2.EscalateLineageEdgeRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_lineage_edge_approval_service_pb2.EscalateLineageEdgeResponse:
        """Escalates a lineage edge."""
        return await self.handle_escalate_lineage_edge(request)

    @rpc_errors
    @retry_transient
    async def GetLineageEdgeApprovalStatus(
        self, request: lineage_v1_lineage_edge_approval_service_pb2.GetLineageEdgeApprovalStatusRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_lineage_edge_approval_service_pb2.GetLineageEdgeApprovalStatusResponse:
        """Returns a lineage edge."""
        return await self.handle_get_lineage_edge_approval_status(request)

    @rpc_errors
    @retry_transient
    async def ListPendingLineageEdges(
        self, request: lineage_v1_lineage_edge_approval_service_pb2.ListPendingLineageEdgesRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_lineage_edge_approval_service_pb2.ListPendingLineageEdgesResponse:
        """Lists lineage edges a page at a time."""
        return await self.handle_list_pending_lineage_edges(request)

    @rpc_errors
    async def RecallLineageEdge(
        self, request: lineage_v1_lineage_edge_approval_service_pb2.RecallLineageEdgeRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_lineage_edge_approval_service_pb2.RecallLineageEdgeResponse:
        """Recalls a lineage edge."""
        return await self.handle_recall_lineage_edge(request)

    @rpc_errors
    async def RejectLineageEdge(
        self, request: lineage_v1_lineage_edge_approval_service_pb2.RejectLineageEdgeRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_lineage_edge_approval_service_pb2.RejectLineageEdgeResponse:
        """Rejects a lineage edge."""
        return await self.handle_reject_lineage_edge(request)

    @rpc_errors
    async def SubmitLineageEdge(
        self, request: lineage_v1_lineage_edge_approval_service_pb2.SubmitLineageEdgeRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_lineage_edge_approval_service_pb2.SubmitLineageEdgeResponse:
        """Submits a lineage edge."""
        return await self.handle_submit_lineage_edge(request)

    async def handle_approve_lineage_edge(
        self,
        request: lineage_v1_lineage_edge_approval_service_pb2.ApproveLineageEdgeRequest
    ) -> lineage_v1_lineage_edge_approval_service_pb2.ApproveLineageEdgeResponse:
        """Approves a lineage edge."""
        deps = self.deps
        response = lineage_v1_lineage_edge_approval_service_pb2.ApproveLineageEdgeResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ApproveLineageEdge', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'ApproveLineageEdge', {'reason': request.reason})
            await deps.repository.save_lineage_edge(request.context.tenant_id, request.lineage_edge)
            response_0 = lineage_v1_lineage_edge_sync_service_pb2.SyncLineageEdgesResponse()
            response_1 = modelregistry_v1_model_version_calculation_service_pb2.EstimateModelVersionResponse()
            outgoing_0 = lineage_v1_lineage_edge_sync_service_pb2.SyncLineageEdgesRequest(
                context=request.context,
                lineage_edge=lineage_v1_lineage_pb2.LineageEdge(
                    subject=lineage_v1_refs_pb2.ImpactRef(
                        impact_id=request.lineage_edge.subject.impact_id,
                        priority=request.lineage_edge.subject.priority
                    )
                )
            )
            outgoing_1 = modelregistry_v1_model_version_calculation_service_pb2.EstimateModelVersionRequest(
                context=request.context,
                model_version=modelregistry_v1_modelregistry_pb2.ModelVersion(
                    subject=customers_v1_refs_pb2.CustomerRef(
                        display_name=request.lineage_edge.subject.display_name,
                        email=request.details.approver.email
                    )
                )
            )
            response_0, response_1 = await asyncio.gather(
                deps.clients.lineage_lineage_edge_sync.SyncLineageEdges(outgoing_0, timeout=deps.settings.timeout),
                deps.clients.modelregistry_model_version_calculation.EstimateModelVersion(
                    outgoing_1,
                    timeout=deps.settings.timeout
                ),
            )
            returned_0_0 = response_0.outcome.reference_id
            if returned_0_0:
                response.outcome.reference_id = returned_0_0
            returned_0_1 = response_0.lineage_edge.subject.display_name
            if returned_0_1:
                response.lineage_edge.subject.display_name = returned_0_1
            returned_1_0 = response_1.model_version.attributes
            response.lineage_edge.attributes.update(returned_1_0)
            returned_1_1 = response_1.result.reference_ids
            response.result.reference_ids.extend(returned_1_1)
            echoed_0 = request.lineage_edge_id
            response.lineage_edge.lineage_edge_id = echoed_0
            echoed_1 = request.lineage_edge.kind
            response.lineage_edge.kind = echoed_1
            return response

    async def handle_comment_lineage_edge_approval(
        self,
        request: lineage_v1_lineage_edge_approval_service_pb2.CommentLineageEdgeApprovalRequest
    ) -> lineage_v1_lineage_edge_approval_service_pb2.CommentLineageEdgeApprovalResponse:
        """Comments a lineage edge."""
        deps = self.deps
        response = lineage_v1_lineage_edge_approval_service_pb2.CommentLineageEdgeApprovalResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CommentLineageEdgeApproval', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'CommentLineageEdgeApproval',
                {'reason': request.reason}
            )
            await deps.repository.save_lineage_edge(request.context.tenant_id, request.lineage_edge)
            response_0 = analytics_v1_analytics_event_service_pb2.BatchCreateAnalyticsEventsResponse()
            response_1 = lineage_v1_impact_lifecycle_service_pb2.TerminateImpactResponse()
            response_2 = lineage_v1_lineage_edge_lifecycle_service_pb2.SuspendLineageEdgeResponse()
            outgoing_0 = analytics_v1_analytics_event_service_pb2.BatchCreateAnalyticsEventsRequest(
                context=request.context,
                record=analytics_v1_analytics_pb2.AnalyticsEvent(
                    subject=analytics_v1_refs_pb2.FunnelRef(display_name=request.lineage_edge.subject.display_name)
                )
            )
            response_0 = await deps.clients.analytics_analytics_event.BatchCreateAnalyticsEvents(
                async_messages((outgoing_0,)),
                timeout=deps.settings.timeout
            )
            outgoing_1 = lineage_v1_impact_lifecycle_service_pb2.TerminateImpactRequest(
                context=request.context,
                details=lineage_v1_impact_lifecycle_service_pb2.TerminateImpactRequest.Details(
                    new_owner=identity_v1_refs_pb2.UserRef(display_name=request.lineage_edge.subject.display_name),
                    notify_contact=common_v1_contact_pb2.ContactInfo(email=request.details.approver.email)
                ),
                impact_id=request.lineage_edge.subject.impact_id
            )
            document_1 = MessageToDict(outgoing_1, preserving_proto_field_name=True)
            outgoing_1 = ParseDict(document_1, lineage_v1_impact_lifecycle_service_pb2.TerminateImpactRequest())
            response_1 = await deps.clients.lineage_impact_lifecycle.TerminateImpact(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = lineage_v1_lineage_edge_lifecycle_service_pb2.SuspendLineageEdgeRequest(
                context=request.context,
                details=lineage_v1_lineage_edge_lifecycle_service_pb2.SuspendLineageEdgeRequest.Details(
                    notify_contact=common_v1_contact_pb2.ContactInfo(phone=response_1.impact.requester.phone)
                ),
                lineage_edge_id=request.lineage_edge.lineage_edge_id
            )
            document_2 = MessageToJson(outgoing_2, preserving_proto_field_name=True)
            outgoing_2 = Parse(document_2, lineage_v1_lineage_edge_lifecycle_service_pb2.SuspendLineageEdgeRequest())
            response_2 = await deps.clients.lineage_lineage_edge_lifecycle.SuspendLineageEdge(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            returned_1_0 = response_1.result.message
            if returned_1_0:
                response.outcome.message = returned_1_0
            returned_1_1 = response_1.result.status
            if returned_1_1:
                response.result.status = returned_1_1
            returned_2_0 = response_2.result.message
            if returned_2_0:
                response.outcome.message = returned_2_0
            echoed_0 = request.lineage_edge_id
            response.lineage_edge.lineage_edge_id = echoed_0
            echoed_1 = request.lineage_edge.correlation_id
            response.lineage_edge.correlation_id = echoed_1
            return response

    async def handle_delegate_lineage_edge_approval(
        self,
        request: lineage_v1_lineage_edge_approval_service_pb2.DelegateLineageEdgeApprovalRequest
    ) -> lineage_v1_lineage_edge_approval_service_pb2.DelegateLineageEdgeApprovalResponse:
        """Delegates a lineage edge."""
        deps = self.deps
        response = lineage_v1_lineage_edge_approval_service_pb2.DelegateLineageEdgeApprovalResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('DelegateLineageEdgeApproval', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'DelegateLineageEdgeApproval',
                {'reason': request.reason}
            )
            await deps.repository.save_lineage_edge(request.context.tenant_id, request.lineage_edge)
            response_0 = customers_v1_preference_calculation_service_pb2.SimulatePreferenceResponse()
            response_1 = customers_v1_household_calculation_service_pb2.RecalculateHouseholdsResponse()
            response_2 = lineage_v1_impact_sync_service_pb2.SyncImpactsResponse()
            response_3 = customers_v1_preference_validation_service_pb2.ValidatePreferenceResponse()
            outgoing_0 = customers_v1_preference_calculation_service_pb2.SimulatePreferenceRequest()
            outgoing_0.context.CopyFrom(request.context)
            outgoing_0.preference.owner.display_name = request.lineage_edge.subject.display_name
            outgoing_0.preference.owner.email = request.details.approver.email
            outgoing_0.preference.owner.user_id = request.details.approver.user_id
            merged_0 = customers_v1_preference_calculation_service_pb2.SimulatePreferenceRequest()
            merged_0.MergeFrom(outgoing_0)
            outgoing_0.CopyFrom(merged_0)
            response_0 = await deps.clients.customers_preference_calculation.SimulatePreference(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = customers_v1_household_calculation_service_pb2.RecalculateHouseholdsRequest(
                context=request.context,
                household=customers_v1_customers_pb2.Household(
                    children=[
                        customers_v1_customers_pb2.Household(
                            children=[
                                customers_v1_customers_pb2.Household(
                                    audit=common_v1_audit_pb2.AuditInfo(
                                        updated_by=response_0.preference.audit.updated_by
                                    ),
                                    manager=identity_v1_refs_pb2.UserRef(
                                        display_name=response_0.preference.owner.display_name
                                    )
                                )
                            ]
                        )
                    ]
                )
            )
            envelope_1 = AnyMessage()
            envelope_1.Pack(outgoing_1)
            outgoing_1 = customers_v1_household_calculation_service_pb2.RecalculateHouseholdsRequest()
            if not envelope_1.Unpack(outgoing_1):
                raise ValueError("partner envelope contains the wrong request type")
            response_1 = await deps.clients.customers_household_calculation.RecalculateHouseholds(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = lineage_v1_impact_sync_service_pb2.SyncImpactsRequest(
                context=request.context,
                impact=lineage_v1_lineage_pb2.Impact(
                    audit=common_v1_audit_pb2.AuditInfo(etag=response_0.preference.audit.etag),
                    customer=customers_v1_refs_pb2.CustomerRef(display_name=request.lineage_edge.subject.display_name)
                )
            )
            registered_2 = cast(
                lineage_v1_impact_sync_service_pb2_grpc.ImpactSyncServiceStub,
                deps.clients.registry['acme.lineage.v1.ImpactSyncService']
            )
            response_2 = await registered_2.SyncImpacts(outgoing_2, timeout=deps.settings.timeout)
            command_3 = LineageEdgeApprovalDelegateLineageEdgeApproval3Command(
                context=request.context,
                preference_block_notify_email=response_0.preference.block.notify_email,
                preference_audit_updated_by=response_0.preference.audit.updated_by,
                preference_owner_email=response_0.preference.owner.email
            )
            outgoing_3 = to_lineage_edge_approval_delegate_lineage_edge_approval3_command(command_3)
            response_3 = await deps.clients.customers_preference_validation.ValidatePreference(
                outgoing_3,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.preference.priority
            if returned_0_0:
                response.lineage_edge.subject.priority = returned_0_0
            returned_1_0 = response_1.household.manager.display_name
            if returned_1_0:
                response.lineage_edge.subject.display_name = returned_1_0
            returned_2_0 = response_2.result.correlation_id
            if returned_2_0:
                response.result.correlation_id = returned_2_0
            returned_2_1 = response_2.result.message
            if returned_2_1:
                response.outcome.message = returned_2_1
            returned_3_0 = response_3.result.status
            if returned_3_0:
                response.result.status = returned_3_0
            returned_3_1 = response_3.result.message
            if returned_3_1:
                response.outcome.message = returned_3_1
            echoed_0 = request.lineage_edge_id
            response.lineage_edge.lineage_edge_id = echoed_0
            echoed_1 = request.lineage_edge.attributes
            response.lineage_edge.attributes.update(echoed_1)
            return response

    async def handle_escalate_lineage_edge(
        self,
        request: lineage_v1_lineage_edge_approval_service_pb2.EscalateLineageEdgeRequest
    ) -> lineage_v1_lineage_edge_approval_service_pb2.EscalateLineageEdgeResponse:
        """Escalates a lineage edge."""
        deps = self.deps
        response = lineage_v1_lineage_edge_approval_service_pb2.EscalateLineageEdgeResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('EscalateLineageEdge', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'EscalateLineageEdge', {'reason': request.reason})
            await deps.repository.save_lineage_edge(request.context.tenant_id, request.lineage_edge)
            response_0 = customers_v1_customer_service_pb2.WatchCustomersResponse()
            response_1 = audit_v1_audit_event_service_pb2.ListAuditEventsResponse()
            response_2 = labeling_v1_label_set_validation_service_pb2.CheckLabelSetEligibilityResponse()
            response_3 = fulfillment_v1_fulfillment_query_service_pb2.FindFulfillmentsResponse()
            outgoing_1 = audit_v1_audit_event_service_pb2.ListAuditEventsRequest(
                context=request.context,
                filter=audit_v1_audit_event_service_pb2.ListAuditEventsRequest.Filter(
                    created_after=request.details.effective_at,
                    owner_id=request.lineage_edge.subject.impact_id
                )
            )
            outgoing_2 = labeling_v1_label_set_validation_service_pb2.CheckLabelSetEligibilityRequest(
                context=request.context,
                label_set=labeling_v1_labeling_pb2.LabelSet(
                    children=[
                        labeling_v1_labeling_pb2.LabelSet(
                            children=[
                                labeling_v1_labeling_pb2.LabelSet(
                                    manager=identity_v1_refs_pb2.UserRef(
                                        display_name=request.lineage_edge.subject.display_name,
                                        email=request.details.approver.email,
                                        user_id=request.details.approver.user_id
                                    )
                                )
                            ]
                        )
                    ],
                    manager=identity_v1_refs_pb2.UserRef(display_name=request.details.approver.display_name)
                )
            )
            response_1, response_2 = await asyncio.gather(
                deps.clients.audit_audit_event.ListAuditEvents(outgoing_1, timeout=deps.settings.timeout),
                deps.clients.labeling_label_set_validation.CheckLabelSetEligibility(
                    outgoing_2,
                    timeout=deps.settings.timeout
                ),
            )
            outgoing_0 = customers_v1_customer_service_pb2.WatchCustomersRequest(
                context=request.context,
                filter=customers_v1_customer_service_pb2.WatchCustomersRequest.Filter(
                    created_after=request.lineage_edge.occurred_at
                ),
                since=request.details.effective_at,
                subscriber=common_v1_contact_pb2.ContactInfo(email=request.details.approver.email)
            )
            async for chunk_0 in deps.clients.customers_customer.WatchCustomers(
                outgoing_0,
                timeout=deps.settings.timeout
            ):
                response_0 = chunk_0
            outgoing_3 = fulfillment_v1_fulfillment_query_service_pb2.FindFulfillmentsRequest()
            outgoing_3.context.CopyFrom(request.context)
            outgoing_3.filter.region = response_2.label_set.location.region
            outgoing_3.context.tenant_id = tenant_id.get()
            response_3 = await deps.clients.fulfillment_fulfillment_query.FindFulfillments(
                outgoing_3,
                timeout=deps.settings.timeout
            )
            returned_1_0 = response_1.result.correlation_id
            if returned_1_0:
                response.result.correlation_id = returned_1_0
            returned_1_1 = response_1.result.reference_ids
            response.result.reference_ids.extend(returned_1_1)
            returned_2_0 = response_2.outcome.message
            if returned_2_0:
                response.outcome.message = returned_2_0
            returned_2_1 = response_2.outcome.reference_id
            if returned_2_1:
                response.outcome.reference_id = returned_2_1
            returned_3_0 = response_3.result.correlation_id
            if returned_3_0:
                response.lineage_edge.correlation_id = returned_3_0
            returned_3_1 = response_3.result.status
            if returned_3_1:
                response.outcome.status = returned_3_1
            echoed_0 = request.lineage_edge_id
            response.lineage_edge.lineage_edge_id = echoed_0
            echoed_1 = request.lineage_edge.source
            response.lineage_edge.source = echoed_1
            return response

    async def handle_get_lineage_edge_approval_status(
        self,
        request: lineage_v1_lineage_edge_approval_service_pb2.GetLineageEdgeApprovalStatusRequest
    ) -> lineage_v1_lineage_edge_approval_service_pb2.GetLineageEdgeApprovalStatusResponse:
        """Returns a lineage edge."""
        deps = self.deps
        response = lineage_v1_lineage_edge_approval_service_pb2.GetLineageEdgeApprovalStatusResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('GetLineageEdgeApprovalStatus', extra={'fields': {'domain': 'lineage'}})
            await deps.repository.audit(request.context.tenant_id, 'GetLineageEdgeApprovalStatus', {})
            response_0 = metrics_v1_metric_alert_history_service_pb2.AnnotateMetricAlertVersionResponse()
            outgoing_0 = metrics_v1_metric_alert_history_service_pb2.AnnotateMetricAlertVersionRequest(
                context=request.context,
                metric_alert=metrics_v1_metrics_pb2.MetricAlert(
                    audit=common_v1_audit_pb2.AuditInfo(created_at=request.context.deadline),
                    owner=identity_v1_refs_pb2.UserRef(
                        email=request.context.actor.email,
                        user_id=request.context.actor.user_id
                    )
                )
            )
            response_0 = await deps.clients.metrics_metric_alert_history.AnnotateMetricAlertVersion(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.correlation_id
            if returned_0_0:
                response.lineage_edge.correlation_id = returned_0_0
            returned_0_1 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_1)
            echoed_0 = request.lineage_edge_id
            response.lineage_edge.lineage_edge_id = echoed_0
            return response

    async def handle_list_pending_lineage_edges(
        self,
        request: lineage_v1_lineage_edge_approval_service_pb2.ListPendingLineageEdgesRequest
    ) -> lineage_v1_lineage_edge_approval_service_pb2.ListPendingLineageEdgesResponse:
        """Lists lineage edges a page at a time."""
        deps = self.deps
        response = lineage_v1_lineage_edge_approval_service_pb2.ListPendingLineageEdgesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ListPendingLineageEdges', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ListPendingLineageEdges',
                {'order_by': request.order_by}
            )
            response_0 = lineage_v1_impact_sync_service_pb2.PullImpactsResponse()
            response_1 = forecasting_v1_scenario_calculation_service_pb2.QuoteScenarioResponse()
            outgoing_0 = lineage_v1_impact_sync_service_pb2.PullImpactsRequest(
                context=request.context,
                impact=lineage_v1_lineage_pb2.Impact(
                    assignee=identity_v1_refs_pb2.UserRef(
                        email=request.context.actor.email,
                        user_id=request.context.actor.user_id
                    ),
                    comments=[lineage_v1_lineage_pb2.ImpactComment(created_at=request.filter.created_after)],
                    subject=request.filter.owner_id
                )
            )
            response_0 = await deps.clients.lineage_impact_sync.PullImpacts(outgoing_0, timeout=deps.settings.timeout)
            outgoing_1 = forecasting_v1_scenario_calculation_service_pb2.QuoteScenarioRequest(
                context=request.context,
                scenario=forecasting_v1_forecasting_pb2.Scenario(
                    channel=forecasting_v1_forecasting_pb2.ScenarioChannelOrigin(
                        address=response_0.impact.channel.address
                    ),
                    requester=common_v1_contact_pb2.ContactInfo(email=response_0.impact.assignee.email),
                    sla=forecasting_v1_forecasting_pb2.ScenarioSla(due_at=response_0.impact.sla.due_at)
                )
            )
            response_1 = await LineageEdgeApprovalListPendingLineageEdges1Adapter(
                deps.clients.forecasting_scenario_calculation,
                deps.settings.timeout
            )(outgoing_1)
            returned_0_0 = response_0.result.correlation_id
            if returned_0_0:
                response.result.correlation_id = returned_0_0
            returned_1_0 = response_1.result.correlation_id
            if returned_1_0:
                response.result.correlation_id = returned_1_0
            return response

    async def handle_recall_lineage_edge(
        self,
        request: lineage_v1_lineage_edge_approval_service_pb2.RecallLineageEdgeRequest
    ) -> lineage_v1_lineage_edge_approval_service_pb2.RecallLineageEdgeResponse:
        """Recalls a lineage edge."""
        deps = self.deps
        response = lineage_v1_lineage_edge_approval_service_pb2.RecallLineageEdgeResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('RecallLineageEdge', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'RecallLineageEdge', {'reason': request.reason})
            await deps.repository.save_lineage_edge(request.context.tenant_id, request.lineage_edge)
            response_0 = lineage_v1_impact_reporting_service_pb2.ListImpactReportsResponse()
            response_1 = forecasting_v1_scenario_calculation_service_pb2.SimulateScenarioResponse()
            response_2 = pipelines_v1_pipeline_step_calculation_service_pb2.QuotePipelineStepResponse()
            outgoing_0 = lineage_v1_impact_reporting_service_pb2.ListImpactReportsRequest(
                context=request.context,
                filter=lineage_v1_impact_reporting_service_pb2.ListImpactReportsRequest.Filter(
                    created_after=request.lineage_edge.occurred_at,
                    owner_id=request.lineage_edge.lineage_edge_id
                )
            )
            response_0 = cast(lineage_v1_impact_reporting_service_pb2.ListImpactReportsResponse, await deps.bus.request(
                'acme.lineage.v1.LineageEdgeApprovalService/RecallLineageEdge/0', outgoing_0, deps.settings.timeout,
            ))
            outgoing_1 = forecasting_v1_scenario_calculation_service_pb2.SimulateScenarioRequest(
                context=request.context,
                scenario=forecasting_v1_forecasting_pb2.Scenario(
                    assignee=identity_v1_refs_pb2.UserRef(user_id=request.details.approver.user_id),
                    customer=forecasting_v1_refs_pb2.ForecastModelRef(
                        display_name=request.lineage_edge.subject.display_name
                    )
                )
            )
            response_1 = await deps.clients.forecasting_scenario_calculation.SimulateScenario(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = pipelines_v1_pipeline_step_calculation_service_pb2.QuotePipelineStepRequest(
                context=request.context,
                pipeline_step=pipelines_v1_pipelines_pb2.PipelineStep(
                    owner=identity_v1_refs_pb2.UserRef(display_name=response_1.scenario.customer.display_name)
                )
            )
            method_name_2 = 'QuotePipelineStep'
            response_2 = await getattr(
                deps.clients.pipelines_pipeline_step_calculation,
                method_name_2
            )(outgoing_2, timeout=deps.settings.timeout)
            returned_0_0 = response_0.result.details
            response.result.details.update(returned_0_0)
            returned_1_0 = response_1.result.reference_ids
            response.result.reference_ids.extend(returned_1_0)
            returned_1_1 = response_1.result.message
            if returned_1_1:
                response.outcome.message = returned_1_1
            returned_2_0 = response_2.result.status
            if returned_2_0:
                response.result.status = returned_2_0
            echoed_0 = request.lineage_edge_id
            response.lineage_edge.lineage_edge_id = echoed_0
            echoed_1 = request.details.effective_at
            response.outcome.effective_at.CopyFrom(echoed_1)
            return response

    async def handle_reject_lineage_edge(
        self,
        request: lineage_v1_lineage_edge_approval_service_pb2.RejectLineageEdgeRequest
    ) -> lineage_v1_lineage_edge_approval_service_pb2.RejectLineageEdgeResponse:
        """Rejects a lineage edge."""
        deps = self.deps
        response = lineage_v1_lineage_edge_approval_service_pb2.RejectLineageEdgeResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('RejectLineageEdge', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'RejectLineageEdge', {'reason': request.reason})
            await deps.repository.save_lineage_edge(request.context.tenant_id, request.lineage_edge)
            response_0 = lineage_v1_lineage_edge_import_service_pb2.GetLineageEdgeImportStatusResponse()
            response_1 = lineage_v1_lineage_node_approval_service_pb2.CommentLineageNodeApprovalResponse()
            response_2 = labeling_v1_label_set_validation_service_pb2.NormalizeLabelSetResponse()
            response_3 = lineage_v1_lineage_edge_reporting_service_pb2.StreamLineageEdgeMetricsResponse()
            fields_0: dict[str, Any] = {
                'context': request.context,
                'lineage_edge_id': request.lineage_edge.lineage_edge_id
            }
            outgoing_0 = lineage_v1_lineage_edge_import_service_pb2.GetLineageEdgeImportStatusRequest(**fields_0)
            response_0 = await deps.clients.lineage_lineage_edge_import.GetLineageEdgeImportStatus(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = lineage_v1_lineage_node_approval_service_pb2.CommentLineageNodeApprovalRequest(
                context=request.context,
                lineage_node=lineage_v1_lineage_pb2.LineageNode(
                    children=[
                        lineage_v1_lineage_pb2.LineageNode(
                            children=[
                                lineage_v1_lineage_pb2.LineageNode(
                                    children=[
                                        lineage_v1_lineage_pb2.LineageNode(
                                            attributes=dict(request.lineage_edge.attributes)
                                        )
                                    ],
                                    manager=identity_v1_refs_pb2.UserRef(
                                        display_name=request.details.approver.display_name
                                    )
                                )
                            ]
                        )
                    ]
                )
            )
            document_1 = MessageToDict(outgoing_1, preserving_proto_field_name=True)
            outgoing_1 = ParseDict(
                document_1,
                lineage_v1_lineage_node_approval_service_pb2.CommentLineageNodeApprovalRequest()
            )
            response_1 = await deps.clients.lineage_lineage_node_approval.CommentLineageNodeApproval(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = labeling_v1_label_set_validation_service_pb2.NormalizeLabelSetRequest(
                context=request.context,
                label_set=labeling_v1_labeling_pb2.LabelSet(
                    children=[
                        labeling_v1_labeling_pb2.LabelSet(
                            children=[
                                labeling_v1_labeling_pb2.LabelSet(
                                    manager=identity_v1_refs_pb2.UserRef(email=request.details.approver.email)
                                )
                            ]
                        )
                    ]
                )
            )
            document_2 = MessageToJson(outgoing_2, preserving_proto_field_name=True)
            outgoing_2 = Parse(document_2, labeling_v1_label_set_validation_service_pb2.NormalizeLabelSetRequest())
            response_2 = await deps.clients.labeling_label_set_validation.NormalizeLabelSet(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            for item_3 in request.lineage_edge.measurements:
                outgoing_3 = lineage_v1_lineage_edge_reporting_service_pb2.StreamLineageEdgeMetricsRequest(
                    context=request.context,
                    filter=lineage_v1_lineage_edge_reporting_service_pb2.StreamLineageEdgeMetricsRequest.Filter(
                        created_after=item_3.observed_at,
                        owner_id=request.details.approver.user_id,
                        region=response_1.lineage_node.location.region
                    ),
                    subscriber=common_v1_contact_pb2.ContactInfo(email=request.details.approver.email)
                )
                async for result_3 in deps.clients.lineage_lineage_edge_reporting.StreamLineageEdgeMetrics(
                    outgoing_3,
                    timeout=deps.settings.timeout
                ):
                    response_3 = result_3
            returned_0_0 = response_0.result.correlation_id
            if returned_0_0:
                response.result.correlation_id = returned_0_0
            returned_0_1 = response_0.lineage_edge.kind
            if returned_0_1:
                response.lineage_edge.kind = returned_0_1
            returned_1_0 = response_1.result.correlation_id
            if returned_1_0:
                response.lineage_edge.correlation_id = returned_1_0
            returned_2_0 = response_2.outcome.message
            if returned_2_0:
                response.result.message = returned_2_0
            returned_2_1 = response_2.result.status
            if returned_2_1:
                response.result.status = returned_2_1
            echoed_0 = request.lineage_edge_id
            response.lineage_edge.lineage_edge_id = echoed_0
            echoed_1 = request.lineage_edge.source
            response.lineage_edge.source = echoed_1
            return response

    async def handle_submit_lineage_edge(
        self,
        request: lineage_v1_lineage_edge_approval_service_pb2.SubmitLineageEdgeRequest
    ) -> lineage_v1_lineage_edge_approval_service_pb2.SubmitLineageEdgeResponse:
        """Submits a lineage edge."""
        deps = self.deps
        response = lineage_v1_lineage_edge_approval_service_pb2.SubmitLineageEdgeResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SubmitLineageEdge', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'SubmitLineageEdge', {'reason': request.reason})
            await deps.repository.save_lineage_edge(request.context.tenant_id, request.lineage_edge)
            response_0 = customers_v1_consent_record_validation_service_pb2.ExplainConsentRecordDecisionResponse()
            outgoing_0 = customers_v1_consent_record_validation_service_pb2.ExplainConsentRecordDecisionRequest(
                consent_record=customers_v1_customers_pb2.ConsentRecord(
                    kind=request.lineage_edge.kind,
                    subject=customers_v1_refs_pb2.HouseholdRef(display_name=request.lineage_edge.subject.display_name)
                ),
                context=request.context,
                details=customers_v1_consent_record_validation_service_pb2.ExplainConsentRecordDecisionRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(email=request.details.approver.email)
                )
            )
            envelope_0 = AnyMessage()
            envelope_0.Pack(outgoing_0)
            outgoing_0 = customers_v1_consent_record_validation_service_pb2.ExplainConsentRecordDecisionRequest()
            if not envelope_0.Unpack(outgoing_0):
                raise ValueError("partner envelope contains the wrong request type")
            response_0 = await deps.clients.customers_consent_record_validation.ExplainConsentRecordDecision(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.status
            if returned_0_0:
                response.outcome.status = returned_0_0
            returned_0_1 = response_0.result.correlation_id
            if returned_0_1:
                response.lineage_edge.correlation_id = returned_0_1
            echoed_0 = request.lineage_edge_id
            response.lineage_edge.lineage_edge_id = echoed_0
            echoed_1 = request.lineage_edge.attributes
            response.lineage_edge.attributes.update(echoed_1)
            return response
