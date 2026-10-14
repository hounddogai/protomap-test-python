"""Routes analytics reports through approval, with escalation and delegation."""

from __future__ import annotations

from collections.abc import AsyncIterator
from collections.abc import Awaitable
from collections.abc import Callable
from functools import partial
from typing import cast
import asyncio
import logging

from google.protobuf.any_pb2 import Any as AnyMessage
from google.protobuf.json_format import MessageToDict
from google.protobuf.json_format import MessageToJson
from google.protobuf.json_format import Parse
from google.protobuf.json_format import ParseDict
import grpc

from acme.analytics.v1 import (
    analytics_event_validation_service_pb2 as analytics_v1_analytics_event_validation_service_pb2,
)
from acme.analytics.v1 import analytics_pb2 as analytics_v1_analytics_pb2
from acme.analytics.v1 import (
    analytics_report_approval_service_pb2 as analytics_v1_analytics_report_approval_service_pb2,
)
from acme.analytics.v1 import (
    analytics_report_approval_service_pb2_grpc as analytics_v1_analytics_report_approval_service_pb2_grpc,
)
from acme.analytics.v1 import cohort_calculation_service_pb2 as analytics_v1_cohort_calculation_service_pb2
from acme.analytics.v1 import funnel_approval_service_pb2 as analytics_v1_funnel_approval_service_pb2
from acme.analytics.v1 import funnel_calculation_service_pb2 as analytics_v1_funnel_calculation_service_pb2
from acme.analytics.v1 import funnel_validation_service_pb2 as analytics_v1_funnel_validation_service_pb2
from acme.analytics.v1 import funnel_workflow_service_pb2 as analytics_v1_funnel_workflow_service_pb2
from acme.analytics.v1 import refs_pb2 as analytics_v1_refs_pb2
from acme.audit.v1 import audit_event_query_service_pb2 as audit_v1_audit_event_query_service_pb2
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
from acme.customers.v1 import household_calculation_service_pb2 as customers_v1_household_calculation_service_pb2
from acme.customers.v1 import preference_calculation_service_pb2 as customers_v1_preference_calculation_service_pb2
from acme.customers.v1 import preference_validation_service_pb2 as customers_v1_preference_validation_service_pb2
from acme.featureflags.v1 import feature_flag_service_pb2 as featureflags_v1_feature_flag_service_pb2
from acme.featureflags.v1 import featureflags_pb2 as featureflags_v1_featureflags_pb2
from acme.featurestore.v1 import feature_view_workflow_service_pb2 as featurestore_v1_feature_view_workflow_service_pb2
from acme.featurestore.v1 import featurestore_pb2 as featurestore_v1_featurestore_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.identity.v1 import user_query_service_pb2 as identity_v1_user_query_service_pb2
from acme.identity.v1 import user_query_service_pb2_grpc as identity_v1_user_query_service_pb2_grpc
from acme.lineage.v1 import lineage_edge_lifecycle_service_pb2 as lineage_v1_lineage_edge_lifecycle_service_pb2
from acme.lineage.v1 import (
    lineage_edge_lifecycle_service_pb2_grpc as lineage_v1_lineage_edge_lifecycle_service_pb2_grpc,
)
from acme.lineage.v1 import lineage_pb2 as lineage_v1_lineage_pb2
from acme.lineage.v1 import refs_pb2 as lineage_v1_refs_pb2
from acme.metrics.v1 import metric_series_service_pb2 as metrics_v1_metric_series_service_pb2
from acme.onboarding.v1 import onboarding_pb2 as onboarding_v1_onboarding_pb2
from acme.onboarding.v1 import (
    onboarding_plan_calculation_service_pb2 as onboarding_v1_onboarding_plan_calculation_service_pb2,
)

from acme_data.domains.analytics import hooks
from acme_data.domains.analytics.dependencies import Dependencies
from acme_data.domains.analytics.models import AnalyticsReportApprovalCommentAnalyticsReportApproval0Command
from acme_data.domains.analytics.models import to_analytics_report_approval_comment_analytics_report_approval0_command
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_id
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class AnalyticsReportApprovalServicer(
    analytics_v1_analytics_report_approval_service_pb2_grpc.AnalyticsReportApprovalServiceServicer
):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    async def ApproveAnalyticsReport(
        self, request: analytics_v1_analytics_report_approval_service_pb2.ApproveAnalyticsReportRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_analytics_report_approval_service_pb2.ApproveAnalyticsReportResponse:
        """Approves an analytics report."""
        return await self.handle_approve_analytics_report(request)

    @rpc_errors
    async def CommentAnalyticsReportApproval(
        self, request: analytics_v1_analytics_report_approval_service_pb2.CommentAnalyticsReportApprovalRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_analytics_report_approval_service_pb2.CommentAnalyticsReportApprovalResponse:
        """Comments an analytics report."""
        return await self.handle_comment_analytics_report_approval(request)

    @rpc_errors
    async def DelegateAnalyticsReportApproval(
        self, request: analytics_v1_analytics_report_approval_service_pb2.DelegateAnalyticsReportApprovalRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_analytics_report_approval_service_pb2.DelegateAnalyticsReportApprovalResponse:
        """Delegates an analytics report."""
        return await self.handle_delegate_analytics_report_approval(request)

    @rpc_errors
    async def EscalateAnalyticsReport(
        self, request: analytics_v1_analytics_report_approval_service_pb2.EscalateAnalyticsReportRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_analytics_report_approval_service_pb2.EscalateAnalyticsReportResponse:
        """Escalates an analytics report."""
        return await self.handle_escalate_analytics_report(request)

    @rpc_errors
    @retry_transient
    async def GetAnalyticsReportApprovalStatus(
        self, request: analytics_v1_analytics_report_approval_service_pb2.GetAnalyticsReportApprovalStatusRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_analytics_report_approval_service_pb2.GetAnalyticsReportApprovalStatusResponse:
        """Returns an analytics report."""
        return await self.handle_get_analytics_report_approval_status(request)

    @rpc_errors
    @retry_transient
    async def ListPendingAnalyticsReports(
        self, request: analytics_v1_analytics_report_approval_service_pb2.ListPendingAnalyticsReportsRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_analytics_report_approval_service_pb2.ListPendingAnalyticsReportsResponse:
        """Lists analytics reports a page at a time."""
        return await self.handle_list_pending_analytics_reports(request)

    @rpc_errors
    async def RecallAnalyticsReport(
        self, request: analytics_v1_analytics_report_approval_service_pb2.RecallAnalyticsReportRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_analytics_report_approval_service_pb2.RecallAnalyticsReportResponse:
        """Recalls an analytics report."""
        return await self.handle_recall_analytics_report(request)

    @rpc_errors
    async def RejectAnalyticsReport(
        self, request: analytics_v1_analytics_report_approval_service_pb2.RejectAnalyticsReportRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_analytics_report_approval_service_pb2.RejectAnalyticsReportResponse:
        """Rejects an analytics report."""
        return await self.handle_reject_analytics_report(request)

    @rpc_errors
    async def SubmitAnalyticsReport(
        self, request: analytics_v1_analytics_report_approval_service_pb2.SubmitAnalyticsReportRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_analytics_report_approval_service_pb2.SubmitAnalyticsReportResponse:
        """Submits an analytics report."""
        return await self.handle_submit_analytics_report(request)

    async def handle_approve_analytics_report(
        self,
        request: analytics_v1_analytics_report_approval_service_pb2.ApproveAnalyticsReportRequest
    ) -> analytics_v1_analytics_report_approval_service_pb2.ApproveAnalyticsReportResponse:
        """Approves an analytics report."""
        deps = self.deps
        response = analytics_v1_analytics_report_approval_service_pb2.ApproveAnalyticsReportResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ApproveAnalyticsReport', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'ApproveAnalyticsReport', {'reason': request.reason})
            await deps.repository.save_analytics_report(request.context.tenant_id, request.analytics_report)
            response_0 = customers_v1_preference_validation_service_pb2.CheckPreferenceEligibilityResponse()
            response_1 = analytics_v1_funnel_approval_service_pb2.RecallFunnelResponse()
            response_2 = lineage_v1_lineage_edge_lifecycle_service_pb2.ScheduleLineageEdgeExpiryResponse()
            response_3 = audit_v1_audit_event_query_service_pb2.FindAuditEventsResponse()
            async for item_0 in async_messages(request.analytics_report.lines):
                outgoing_0 = customers_v1_preference_validation_service_pb2.CheckPreferenceEligibilityRequest(
                    context=request.context,
                    preference=customers_v1_customers_pb2.Preference(
                        discount=customers_v1_customers_pb2.PreferenceDiscountAction(amount=item_0.tax.amount)
                    )
                )
                response_0 = await deps.clients.customers_preference_validation.CheckPreferenceEligibility(
                    outgoing_0,
                    timeout=deps.settings.timeout
                )
            outgoing_1 = analytics_v1_funnel_approval_service_pb2.RecallFunnelRequest()
            outgoing_1.context.CopyFrom(request.context)
            outgoing_1.details.approver.display_name = request.details.approver.display_name
            outgoing_1.funnel.audit.created_at.CopyFrom(response_0.preference.audit.created_at)
            if response_0.preference.WhichOneof('action') == 'block':
                outgoing_1.funnel.block.notify_email = response_0.preference.block.notify_email
            outgoing_1.funnel.audit.updated_at.CopyFrom(response_0.preference.audit.updated_at)
            response_1 = await deps.clients.analytics_funnel_approval.RecallFunnel(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = lineage_v1_lineage_edge_lifecycle_service_pb2.ScheduleLineageEdgeExpiryRequest(
                context=request.context,
                details=lineage_v1_lineage_edge_lifecycle_service_pb2.ScheduleLineageEdgeExpiryRequest.Details(
                    notify=common_v1_contact_pb2.ContactInfo(email=response_0.preference.owner.email)
                ),
                lineage_edge=lineage_v1_lineage_pb2.LineageEdge(
                    correlation_id=response_1.result.correlation_id,
                    subject=lineage_v1_refs_pb2.ImpactRef(display_name=request.details.approver.display_name)
                ),
                reason=response_1.funnel.block.reason
            )
            registered_2 = cast(
                lineage_v1_lineage_edge_lifecycle_service_pb2_grpc.LineageEdgeLifecycleServiceStub,
                deps.clients.registry['acme.lineage.v1.LineageEdgeLifecycleService']
            )
            response_2 = await registered_2.ScheduleLineageEdgeExpiry(outgoing_2, timeout=deps.settings.timeout)
            for item_3 in request.analytics_report.lines:
                outgoing_3 = audit_v1_audit_event_query_service_pb2.FindAuditEventsRequest(
                    context=request.context,
                    filter=audit_v1_audit_event_query_service_pb2.FindAuditEventsRequest.Filter(
                        created_after=response_2.outcome.effective_at,
                        labels=dict(item_3.attributes),
                        owner_id=item_3.line_id,
                        region=request.analytics_report.billing_address.region
                    )
                )
                response_3 = await deps.clients.audit_audit_event_query.FindAuditEvents(
                    outgoing_3,
                    timeout=deps.settings.timeout
                )
            returned_1_0 = response_1.outcome.message
            if returned_1_0:
                response.result.message = returned_1_0
            returned_1_1 = response_1.funnel.discount.amount
            returned_1_1_part_1 = response.analytics_report.lines.add()
            if returned_1_1.ListFields():
                returned_1_1_part_1.amount.MergeFrom(returned_1_1)
            returned_2_0 = response_2.outcome.message
            if returned_2_0:
                response.outcome.message = returned_2_0
            returned_2_1 = response_2.outcome.effective_at
            if returned_2_1.ListFields():
                response.outcome.effective_at.MergeFrom(returned_2_1)
            echoed_0 = request.analytics_report_id
            response.analytics_report.analytics_report_id = echoed_0
            echoed_1 = request.analytics_report.status
            response.analytics_report.status = echoed_1
            return response

    async def handle_comment_analytics_report_approval(
        self,
        request: analytics_v1_analytics_report_approval_service_pb2.CommentAnalyticsReportApprovalRequest
    ) -> analytics_v1_analytics_report_approval_service_pb2.CommentAnalyticsReportApprovalResponse:
        """Comments an analytics report."""
        deps = self.deps
        response = analytics_v1_analytics_report_approval_service_pb2.CommentAnalyticsReportApprovalResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CommentAnalyticsReportApproval', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'CommentAnalyticsReportApproval',
                {'reason': request.reason}
            )
            await deps.repository.save_analytics_report(request.context.tenant_id, request.analytics_report)
            response_0 = metrics_v1_metric_series_service_pb2.CreateMetricSeriesResponse()
            response_1 = analytics_v1_funnel_workflow_service_pb2.ListFunnelWorkflowsResponse()
            response_2 = customers_v1_preference_calculation_service_pb2.QuotePreferenceResponse()
            response_3 = customers_v1_household_calculation_service_pb2.EstimateHouseholdResponse()
            command_0 = AnalyticsReportApprovalCommentAnalyticsReportApproval0Command.model_validate(
                {
                    'context': request.context,
                    'metric_series_address_locality': request.analytics_report.billing_address.locality
                }
            )
            outgoing_0 = to_analytics_report_approval_comment_analytics_report_approval0_command(command_0)
            response_0 = await deps.clients.metrics_metric_series.CreateMetricSeries(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = analytics_v1_funnel_workflow_service_pb2.ListFunnelWorkflowsRequest(
                context=request.context,
                filter=analytics_v1_funnel_workflow_service_pb2.ListFunnelWorkflowsRequest.Filter(
                    region=response_0.metric_series.address.region
                )
            )
            send_1 = partial(deps.clients.analytics_funnel_workflow.ListFunnelWorkflows, timeout=deps.settings.timeout)
            response_1 = await send_1(outgoing_1)
            outgoing_2 = customers_v1_preference_calculation_service_pb2.QuotePreferenceRequest(
                context=request.context,
                details=customers_v1_preference_calculation_service_pb2.QuotePreferenceRequest.Details(
                    destination=common_v1_address_pb2.PostalAddress(
                        lines=list(request.analytics_report.billing_address.lines)
                    )
                ),
                preference=customers_v1_customers_pb2.Preference(
                    audit=common_v1_audit_pb2.AuditInfo(updated_by=request.analytics_report.audit.updated_by),
                    owner=identity_v1_refs_pb2.UserRef(email=response_0.metric_series.owner.email)
                )
            )
            response_2 = await hooks.analytics_report_approval_comment_analytics_report_approval2(
                deps.clients.customers_preference_calculation,
                outgoing_2,
                deps.settings.timeout
            )
            outgoing_3 = customers_v1_household_calculation_service_pb2.EstimateHouseholdRequest()
            outgoing_3.context.CopyFrom(request.context)
            field_3_1_part_1 = outgoing_3.household.children.add()
            field_3_1_part_2 = field_3_1_part_1.children.add()
            field_3_1_part_2.manager.email = response_0.metric_series.owner.email
            field_3_2_part_1 = outgoing_3.household.children.add()
            field_3_2_part_2 = field_3_2_part_1.children.add()
            field_3_2_part_2.audit.updated_at.CopyFrom(response_0.metric_series.audit.updated_at)
            outgoing_3.context.tenant_id = tenant_id.get()
            response_3 = await deps.clients.customers_household_calculation.EstimateHousehold(
                outgoing_3,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.metric_series.address.recipient
            if returned_0_0:
                response.analytics_report.billing_address.recipient = returned_0_0
            returned_1_0 = response_1.result.message
            if returned_1_0:
                response.result.message = returned_1_0
            returned_2_0 = response_2.result.reference_ids
            response.result.reference_ids.extend(returned_2_0)
            returned_3_0 = response_3.result.reference_ids
            response.result.reference_ids.extend(returned_3_0)
            echoed_0 = request.analytics_report_id
            response.analytics_report.analytics_report_id = echoed_0
            echoed_1 = request.analytics_report.notes
            response.analytics_report.notes = echoed_1
            return response

    async def handle_delegate_analytics_report_approval(
        self,
        request: analytics_v1_analytics_report_approval_service_pb2.DelegateAnalyticsReportApprovalRequest
    ) -> analytics_v1_analytics_report_approval_service_pb2.DelegateAnalyticsReportApprovalResponse:
        """Delegates an analytics report."""
        deps = self.deps
        response = analytics_v1_analytics_report_approval_service_pb2.DelegateAnalyticsReportApprovalResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('DelegateAnalyticsReportApproval', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'DelegateAnalyticsReportApproval',
                {'reason': request.reason}
            )
            await deps.repository.save_analytics_report(request.context.tenant_id, request.analytics_report)
            response_0 = analytics_v1_analytics_event_validation_service_pb2.PreviewAnalyticsEventResponse()
            response_1 = customers_v1_preference_calculation_service_pb2.ComparePreferenceOptionsResponse()
            response_2 = customers_v1_customer_segment_calculation_service_pb2.SimulateCustomerSegmentResponse()
            outgoing_0 = analytics_v1_analytics_event_validation_service_pb2.PreviewAnalyticsEventRequest(
                analytics_event=analytics_v1_analytics_pb2.AnalyticsEvent(
                    subject=analytics_v1_refs_pb2.FunnelRef(display_name=request.details.approver.display_name)
                ),
                context=request.context
            )
            outgoing_1 = customers_v1_preference_calculation_service_pb2.ComparePreferenceOptionsRequest(
                context=request.context,
                details=customers_v1_preference_calculation_service_pb2.ComparePreferenceOptionsRequest.Details(
                    destination=common_v1_address_pb2.PostalAddress(
                        recipient=request.analytics_report.billing_address.recipient
                    )
                ),
                preference=customers_v1_customers_pb2.Preference(
                    audit=common_v1_audit_pb2.AuditInfo(etag=request.analytics_report.audit.etag)
                )
            )
            response_0, response_1 = await asyncio.gather(
                deps.clients.analytics_analytics_event_validation.PreviewAnalyticsEvent(
                    outgoing_0,
                    timeout=deps.settings.timeout
                ),
                deps.clients.customers_preference_calculation.ComparePreferenceOptions(
                    outgoing_1,
                    timeout=deps.settings.timeout
                ),
            )
            outgoing_2 = customers_v1_customer_segment_calculation_service_pb2.SimulateCustomerSegmentRequest()
            outgoing_2.context.CopyFrom(request.context)
            outgoing_2.details.destination.postal_code = request.analytics_report.billing_address.postal_code
            if response_1.preference.WhichOneof('action') == 'route':
                outgoing_2.customer_segment.route.target = response_1.preference.route.target
            outgoing_2.customer_segment.owner.email = response_1.preference.owner.email
            outgoing_2.customer_segment.audit.created_at.CopyFrom(request.analytics_report.audit.created_at)
            response_2 = await deps.clients.customers_customer_segment_calculation.SimulateCustomerSegment(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.status
            if returned_0_0:
                response.result.status = returned_0_0
            returned_0_1 = response_0.result.message
            if returned_0_1:
                response.outcome.message = returned_0_1
            returned_1_0 = response_1.preference.audit.updated_by
            if returned_1_0:
                response.analytics_report.audit.updated_by = returned_1_0
            returned_2_0 = response_2.result.status
            if returned_2_0:
                response.outcome.status = returned_2_0
            returned_2_1 = response_2.customer_segment.description
            returned_2_1_part_1 = response.analytics_report.lines.add()
            if returned_2_1:
                returned_2_1_part_1.description = returned_2_1
            echoed_0 = request.analytics_report_id
            response.analytics_report.analytics_report_id = echoed_0
            echoed_1 = request.analytics_report.status
            response.analytics_report.status = echoed_1
            return response

    async def handle_escalate_analytics_report(
        self,
        request: analytics_v1_analytics_report_approval_service_pb2.EscalateAnalyticsReportRequest
    ) -> analytics_v1_analytics_report_approval_service_pb2.EscalateAnalyticsReportResponse:
        """Escalates an analytics report."""
        deps = self.deps
        response = analytics_v1_analytics_report_approval_service_pb2.EscalateAnalyticsReportResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('EscalateAnalyticsReport', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'EscalateAnalyticsReport',
                {'reason': request.reason}
            )
            await deps.repository.save_analytics_report(request.context.tenant_id, request.analytics_report)
            response_0 = audit_v1_audit_event_query_service_pb2.CountAuditEventsResponse()
            response_1 = analytics_v1_funnel_validation_service_pb2.CheckFunnelEligibilityResponse()
            outgoing_0 = audit_v1_audit_event_query_service_pb2.CountAuditEventsRequest(
                context=request.context,
                filter=audit_v1_audit_event_query_service_pb2.CountAuditEventsRequest.Filter(
                    region=request.analytics_report.billing_address.region
                )
            )
            response_0 = cast(audit_v1_audit_event_query_service_pb2.CountAuditEventsResponse, await deps.bus.request(
                'acme.analytics.v1.AnalyticsReportApprovalService/EscalateAnalyticsReport/0', outgoing_0, deps.settings.timeout,
            ))
            outgoing_1 = analytics_v1_funnel_validation_service_pb2.CheckFunnelEligibilityRequest(
                context=request.context,
                details=analytics_v1_funnel_validation_service_pb2.CheckFunnelEligibilityRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(email=request.details.approver.email)
                ),
                funnel=analytics_v1_analytics_pb2.Funnel(
                    audit=common_v1_audit_pb2.AuditInfo(created_at=request.analytics_report.audit.created_at),
                    owner=identity_v1_refs_pb2.UserRef(
                        display_name=request.analytics_report.counterparty.display_name,
                        email=request.analytics_report.counterparty.email
                    )
                )
            )
            response_1 = await deps.clients.analytics_funnel_validation.CheckFunnelEligibility(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.correlation_id
            if returned_0_0:
                response.result.correlation_id = returned_0_0
            returned_1_0 = response_1.funnel.audit.created_by
            if returned_1_0:
                response.analytics_report.audit.created_by = returned_1_0
            echoed_0 = request.analytics_report_id
            response.analytics_report.analytics_report_id = echoed_0
            echoed_1 = request.analytics_report.notes
            response.analytics_report.notes = echoed_1
            return response

    async def handle_get_analytics_report_approval_status(
        self,
        request: analytics_v1_analytics_report_approval_service_pb2.GetAnalyticsReportApprovalStatusRequest
    ) -> analytics_v1_analytics_report_approval_service_pb2.GetAnalyticsReportApprovalStatusResponse:
        """Returns an analytics report."""
        deps = self.deps
        response = analytics_v1_analytics_report_approval_service_pb2.GetAnalyticsReportApprovalStatusResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('GetAnalyticsReportApprovalStatus', extra={'fields': {'domain': 'analytics'}})
            await deps.repository.audit(request.context.tenant_id, 'GetAnalyticsReportApprovalStatus', {})
            response_0 = customers_v1_customer_segment_calculation_service_pb2.QuoteCustomerSegmentResponse()
            outgoing_0 = customers_v1_customer_segment_calculation_service_pb2.QuoteCustomerSegmentRequest(
                context=request.context,
                customer_segment=customers_v1_customers_pb2.CustomerSegment(
                    audit=common_v1_audit_pb2.AuditInfo(updated_at=request.context.deadline),
                    owner=identity_v1_refs_pb2.UserRef(
                        email=request.context.actor.email,
                        user_id=request.context.actor.user_id
                    )
                )
            )
            response_0 = await deps.clients.customers_customer_segment_calculation.QuoteCustomerSegment(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.details
            response.result.details.update(returned_0_0)
            echoed_0 = request.analytics_report_id
            response.analytics_report.analytics_report_id = echoed_0
            return response

    async def handle_list_pending_analytics_reports(
        self,
        request: analytics_v1_analytics_report_approval_service_pb2.ListPendingAnalyticsReportsRequest
    ) -> analytics_v1_analytics_report_approval_service_pb2.ListPendingAnalyticsReportsResponse:
        """Lists analytics reports a page at a time."""
        deps = self.deps
        response = analytics_v1_analytics_report_approval_service_pb2.ListPendingAnalyticsReportsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ListPendingAnalyticsReports', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ListPendingAnalyticsReports',
                {'order_by': request.order_by}
            )
            response_0 = analytics_v1_funnel_calculation_service_pb2.QuoteFunnelResponse()
            outgoing_0 = analytics_v1_funnel_calculation_service_pb2.QuoteFunnelRequest(
                context=request.context,
                details=analytics_v1_funnel_calculation_service_pb2.QuoteFunnelRequest.Details(
                    destination=common_v1_address_pb2.PostalAddress(region=request.filter.region)
                ),
                funnel=analytics_v1_analytics_pb2.Funnel(
                    owner=identity_v1_refs_pb2.UserRef(
                        email=request.context.actor.email,
                        user_id=request.context.actor.user_id
                    )
                )
            )
            response_0 = await deps.clients.analytics_funnel_calculation.QuoteFunnel(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_0)
            return response

    async def handle_recall_analytics_report(
        self,
        request: analytics_v1_analytics_report_approval_service_pb2.RecallAnalyticsReportRequest
    ) -> analytics_v1_analytics_report_approval_service_pb2.RecallAnalyticsReportResponse:
        """Recalls an analytics report."""
        deps = self.deps
        response = analytics_v1_analytics_report_approval_service_pb2.RecallAnalyticsReportResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('RecallAnalyticsReport', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'RecallAnalyticsReport', {'reason': request.reason})
            await deps.repository.save_analytics_report(request.context.tenant_id, request.analytics_report)
            response_0 = customers_v1_household_calculation_service_pb2.SimulateHouseholdResponse()
            response_1 = featurestore_v1_feature_view_workflow_service_pb2.ResumeFeatureViewWorkflowResponse()
            outgoing_0 = customers_v1_household_calculation_service_pb2.SimulateHouseholdRequest(
                context=request.context,
                household=customers_v1_customers_pb2.Household(
                    children=[
                        customers_v1_customers_pb2.Household(
                            children=[
                                customers_v1_customers_pb2.Household(
                                    manager=identity_v1_refs_pb2.UserRef(
                                        email=request.analytics_report.counterparty.email
                                    )
                                )
                            ],
                            location=common_v1_address_pb2.PostalAddress(
                                lines=list(request.analytics_report.billing_address.lines)
                            )
                        )
                    ]
                )
            )
            document_0 = MessageToDict(outgoing_0, preserving_proto_field_name=True)
            outgoing_0 = ParseDict(
                document_0,
                customers_v1_household_calculation_service_pb2.SimulateHouseholdRequest()
            )
            response_0 = await deps.clients.customers_household_calculation.SimulateHousehold(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = featurestore_v1_feature_view_workflow_service_pb2.ResumeFeatureViewWorkflowRequest(
                context=request.context,
                details=featurestore_v1_feature_view_workflow_service_pb2.ResumeFeatureViewWorkflowRequest.Details(
                    notify=common_v1_contact_pb2.ContactInfo(email=request.analytics_report.counterparty.email)
                ),
                feature_view=featurestore_v1_featurestore_pb2.FeatureView(
                    address=common_v1_address_pb2.PostalAddress(
                        recipient=request.analytics_report.billing_address.recipient
                    ),
                    audit=common_v1_audit_pb2.AuditInfo(created_by=response_0.household.audit.created_by)
                )
            )
            document_1 = MessageToJson(outgoing_1, preserving_proto_field_name=True)
            outgoing_1 = Parse(
                document_1,
                featurestore_v1_feature_view_workflow_service_pb2.ResumeFeatureViewWorkflowRequest()
            )
            response_1 = await deps.clients.featurestore_feature_view_workflow.ResumeFeatureViewWorkflow(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.household.manager.display_name
            if returned_0_0:
                response.analytics_report.counterparty.display_name = returned_0_0
            returned_1_0 = response_1.result.message
            if returned_1_0:
                response.result.message = returned_1_0
            echoed_0 = request.analytics_report_id
            response.analytics_report.analytics_report_id = echoed_0
            echoed_1 = request.details.effective_at
            response.outcome.effective_at.CopyFrom(echoed_1)
            return response

    async def handle_reject_analytics_report(
        self,
        request: analytics_v1_analytics_report_approval_service_pb2.RejectAnalyticsReportRequest
    ) -> analytics_v1_analytics_report_approval_service_pb2.RejectAnalyticsReportResponse:
        """Rejects an analytics report."""
        deps = self.deps
        response = analytics_v1_analytics_report_approval_service_pb2.RejectAnalyticsReportResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('RejectAnalyticsReport', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'RejectAnalyticsReport', {'reason': request.reason})
            await deps.repository.save_analytics_report(request.context.tenant_id, request.analytics_report)
            response_0 = onboarding_v1_onboarding_plan_calculation_service_pb2.ExplainOnboardingPlanCalculationResponse()
            response_1 = analytics_v1_cohort_calculation_service_pb2.RecalculateCohortsResponse()
            response_2 = identity_v1_user_query_service_pb2.LookupUserResponse()
            requests_0: list[
                onboarding_v1_onboarding_plan_calculation_service_pb2.ExplainOnboardingPlanCalculationRequest
            ] = []
            for item_0 in request.analytics_report.attachments:
                outgoing_0 = onboarding_v1_onboarding_plan_calculation_service_pb2.ExplainOnboardingPlanCalculationRequest(
                    context=request.context,
                    onboarding_plan=onboarding_v1_onboarding_pb2.OnboardingPlan(
                        attachments=[
                            onboarding_v1_onboarding_pb2.OnboardingPlanAttachment(
                                content_type=item_0.content_type,
                                file_name=item_0.file_name
                            )
                        ]
                    )
                )
                requests_0.append(outgoing_0)
            replies_0 = await asyncio.gather(*(
                deps.clients.onboarding_onboarding_plan_calculation.ExplainOnboardingPlanCalculation(
                    entry,
                    timeout=deps.settings.timeout
                ) for entry in requests_0
            ))
            if replies_0:
                response_0 = replies_0[-1]
            outgoing_1 = analytics_v1_cohort_calculation_service_pb2.RecalculateCohortsRequest(
                cohort=analytics_v1_analytics_pb2.Cohort(
                    audit=common_v1_audit_pb2.AuditInfo(updated_at=response_0.onboarding_plan.audit.updated_at)
                ),
                context=request.context,
                details=analytics_v1_cohort_calculation_service_pb2.RecalculateCohortsRequest.Details(
                    destination=common_v1_address_pb2.PostalAddress(
                        country_code=response_0.onboarding_plan.billing_address.country_code,
                        locality=response_0.onboarding_plan.billing_address.locality,
                        region=request.analytics_report.billing_address.region
                    )
                )
            )
            envelope_1 = AnyMessage()
            envelope_1.Pack(outgoing_1)
            outgoing_1 = analytics_v1_cohort_calculation_service_pb2.RecalculateCohortsRequest()
            if not envelope_1.Unpack(outgoing_1):
                raise ValueError("partner envelope contains the wrong request type")
            response_1 = await deps.clients.analytics_cohort_calculation.RecalculateCohorts(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = identity_v1_user_query_service_pb2.LookupUserRequest(
                context=request.context,
                user_id=request.details.approver.user_id
            )
            registered_2 = cast(
                identity_v1_user_query_service_pb2_grpc.UserQueryServiceStub,
                deps.clients.registry['acme.identity.v1.UserQueryService']
            )
            response_2 = await registered_2.LookupUser(outgoing_2, timeout=deps.settings.timeout)
            returned_1_0 = response_1.cohort.discount.amount
            returned_1_0_part_1 = response.analytics_report.lines.add()
            if returned_1_0.ListFields():
                returned_1_0_part_1.tax.amount.MergeFrom(returned_1_0)
            returned_2_0 = response_2.user.primary_address.country_code
            if returned_2_0:
                response.analytics_report.billing_address.country_code = returned_2_0
            echoed_0 = request.analytics_report_id
            response.analytics_report.analytics_report_id = echoed_0
            echoed_1 = request.analytics_report.due_at
            response.analytics_report.due_at.CopyFrom(echoed_1)
            return response

    async def handle_submit_analytics_report(
        self,
        request: analytics_v1_analytics_report_approval_service_pb2.SubmitAnalyticsReportRequest
    ) -> analytics_v1_analytics_report_approval_service_pb2.SubmitAnalyticsReportResponse:
        """Submits an analytics report."""
        deps = self.deps
        response = analytics_v1_analytics_report_approval_service_pb2.SubmitAnalyticsReportResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SubmitAnalyticsReport', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'SubmitAnalyticsReport', {'reason': request.reason})
            await deps.repository.save_analytics_report(request.context.tenant_id, request.analytics_report)
            response_0 = featureflags_v1_feature_flag_service_pb2.BatchCreateFeatureFlagsResponse()
            response_1 = customers_v1_household_calculation_service_pb2.ExplainHouseholdCalculationResponse()
            response_2 = customers_v1_customer_segment_validation_service_pb2.LintCustomerSegmentsResponse()
            response_3 = analytics_v1_funnel_validation_service_pb2.PreviewFunnelResponse()
            outgoing_1 = customers_v1_household_calculation_service_pb2.ExplainHouseholdCalculationRequest(
                context=request.context,
                household=customers_v1_customers_pb2.Household(
                    children=[
                        customers_v1_customers_pb2.Household(
                            children=[
                                customers_v1_customers_pb2.Household(
                                    location=common_v1_address_pb2.PostalAddress(
                                        lines=list(request.analytics_report.billing_address.lines),
                                        locality=request.analytics_report.billing_address.locality
                                    ),
                                    manager=identity_v1_refs_pb2.UserRef(
                                        email=request.details.approver.email,
                                        user_id=request.details.approver.user_id
                                    )
                                )
                            ]
                        )
                    ]
                )
            )
            outgoing_2 = customers_v1_customer_segment_validation_service_pb2.LintCustomerSegmentsRequest(
                context=request.context,
                customer_segment=customers_v1_customers_pb2.CustomerSegment(
                    audit=common_v1_audit_pb2.AuditInfo(created_at=request.analytics_report.audit.created_at)
                )
            )
            response_1, response_2 = await asyncio.gather(
                deps.clients.customers_household_calculation.ExplainHouseholdCalculation(
                    outgoing_1,
                    timeout=deps.settings.timeout
                ),
                deps.clients.customers_customer_segment_validation.LintCustomerSegments(
                    outgoing_2,
                    timeout=deps.settings.timeout
                ),
            )
            outgoing_0 = featureflags_v1_feature_flag_service_pb2.BatchCreateFeatureFlagsRequest(
                context=request.context,
                record=featureflags_v1_featureflags_pb2.FeatureFlag(
                    audit=common_v1_audit_pb2.AuditInfo(updated_by=request.analytics_report.audit.updated_by),
                    owner=identity_v1_refs_pb2.UserRef(
                        display_name=request.details.approver.display_name,
                        email=request.details.approver.email,
                        user_id=request.details.approver.user_id
                    )
                )
            )
            response_0 = await deps.clients.featureflags_feature_flag.BatchCreateFeatureFlags(
                async_messages((outgoing_0,)),
                timeout=deps.settings.timeout
            )
            callbacks_3: list[
                Callable[[], Awaitable[analytics_v1_funnel_validation_service_pb2.PreviewFunnelResponse]]
            ] = []
            for item_3 in request.analytics_report.lines:
                outgoing_3 = analytics_v1_funnel_validation_service_pb2.PreviewFunnelRequest(
                    context=request.context,
                    funnel=analytics_v1_analytics_pb2.Funnel(
                        description=item_3.description,
                        discount=analytics_v1_analytics_pb2.FunnelDiscountAction(amount=item_3.tax.amount),
                        owner=identity_v1_refs_pb2.UserRef(email=request.details.approver.email)
                    )
                )
                async def send_3(
                    payload: analytics_v1_funnel_validation_service_pb2.PreviewFunnelRequest = outgoing_3
                ) -> analytics_v1_funnel_validation_service_pb2.PreviewFunnelResponse:
                    return await deps.clients.analytics_funnel_validation.PreviewFunnel(
                        payload,
                        timeout=deps.settings.timeout
                    )
                callbacks_3.append(send_3)
            for callback_3 in callbacks_3:
                response_3 = await callback_3()
            returned_1_0 = response_1.household.location.region
            if returned_1_0:
                response.analytics_report.billing_address.region = returned_1_0
            returned_1_1 = response_1.household.audit.updated_by
            if returned_1_1:
                response.analytics_report.audit.updated_by = returned_1_1
            returned_2_0 = response_2.customer_segment.audit.created_at
            if returned_2_0.ListFields():
                response.analytics_report.audit.created_at.MergeFrom(returned_2_0)
            echoed_0 = request.analytics_report_id
            response.analytics_report.analytics_report_id = echoed_0
            echoed_1 = request.analytics_report.due_at
            response.analytics_report.due_at.CopyFrom(echoed_1)
            return response
