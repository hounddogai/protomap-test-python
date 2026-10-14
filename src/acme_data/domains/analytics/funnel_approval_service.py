"""Routes funnels through approval, with escalation and delegation."""

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
import grpc

from acme.analytics.v1 import analytics_event_approval_service_pb2 as analytics_v1_analytics_event_approval_service_pb2
from acme.analytics.v1 import (
    analytics_event_validation_service_pb2 as analytics_v1_analytics_event_validation_service_pb2,
)
from acme.analytics.v1 import analytics_pb2 as analytics_v1_analytics_pb2
from acme.analytics.v1 import (
    analytics_report_calculation_service_pb2 as analytics_v1_analytics_report_calculation_service_pb2,
)
from acme.analytics.v1 import (
    analytics_report_validation_service_pb2 as analytics_v1_analytics_report_validation_service_pb2,
)
from acme.analytics.v1 import funnel_approval_service_pb2 as analytics_v1_funnel_approval_service_pb2
from acme.analytics.v1 import funnel_approval_service_pb2_grpc as analytics_v1_funnel_approval_service_pb2_grpc
from acme.analytics.v1 import funnel_calculation_service_pb2 as analytics_v1_funnel_calculation_service_pb2
from acme.anomalies.v1 import anomalies_pb2 as anomalies_v1_anomalies_pb2
from acme.anomalies.v1 import (
    anomaly_feedback_approval_service_pb2 as anomalies_v1_anomaly_feedback_approval_service_pb2,
)
from acme.audit.v1 import audit_event_query_service_pb2 as audit_v1_audit_event_query_service_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.customers.v1 import (
    consent_record_calculation_service_pb2 as customers_v1_consent_record_calculation_service_pb2,
)
from acme.customers.v1 import customer_query_service_pb2 as customers_v1_customer_query_service_pb2
from acme.customers.v1 import customers_pb2 as customers_v1_customers_pb2
from acme.customers.v1 import household_calculation_service_pb2 as customers_v1_household_calculation_service_pb2
from acme.customers.v1 import refs_pb2 as customers_v1_refs_pb2
from acme.datasets.v1 import refs_pb2 as datasets_v1_refs_pb2
from acme.employees.v1 import refs_pb2 as employees_v1_refs_pb2
from acme.forecasting.v1 import (
    forecast_model_workflow_service_pb2 as forecasting_v1_forecast_model_workflow_service_pb2,
)
from acme.forecasting.v1 import forecasting_pb2 as forecasting_v1_forecasting_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.ledger.v1 import ledger_account_query_service_pb2 as ledger_v1_ledger_account_query_service_pb2
from acme.risk.v1 import risk_register_query_service_pb2 as risk_v1_risk_register_query_service_pb2
from acme.risk.v1 import risk_register_query_service_pb2_grpc as risk_v1_risk_register_query_service_pb2_grpc
from acme.travel.v1 import travel_pb2 as travel_v1_travel_pb2
from acme.travel.v1 import trip_calculation_service_pb2 as travel_v1_trip_calculation_service_pb2

from acme_data.domains.analytics import hooks
from acme_data.domains.analytics.adapters import FunnelApprovalApproveFunnel0Adapter
from acme_data.domains.analytics.adapters import FunnelApprovalApproveFunnel0Port
from acme_data.domains.analytics.adapters import FunnelApprovalCommentFunnelApproval1Adapter
from acme_data.domains.analytics.dependencies import Dependencies
from acme_data.domains.analytics.models import FunnelApprovalRejectFunnel1Command
from acme_data.domains.analytics.models import to_funnel_approval_reject_funnel1_command
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_id
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


@dataclass(slots=True)
class FunnelApprovalServicer(analytics_v1_funnel_approval_service_pb2_grpc.FunnelApprovalServiceServicer):
    deps: Dependencies

    @rpc_errors
    async def ApproveFunnel(
        self, request: analytics_v1_funnel_approval_service_pb2.ApproveFunnelRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_funnel_approval_service_pb2.ApproveFunnelResponse:
        """Approves a funnel."""
        return await self.handle_approve_funnel(request)

    @rpc_errors
    async def CommentFunnelApproval(
        self, request: analytics_v1_funnel_approval_service_pb2.CommentFunnelApprovalRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_funnel_approval_service_pb2.CommentFunnelApprovalResponse:
        """Comments a funnel."""
        return await self.handle_comment_funnel_approval(request)

    @rpc_errors
    async def DelegateFunnelApproval(
        self, request: analytics_v1_funnel_approval_service_pb2.DelegateFunnelApprovalRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_funnel_approval_service_pb2.DelegateFunnelApprovalResponse:
        """Delegates a funnel."""
        return await self.handle_delegate_funnel_approval(request)

    @rpc_errors
    async def EscalateFunnel(
        self, request: analytics_v1_funnel_approval_service_pb2.EscalateFunnelRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_funnel_approval_service_pb2.EscalateFunnelResponse:
        """Escalates a funnel."""
        return await self.handle_escalate_funnel(request)

    @rpc_errors
    @retry_transient
    async def GetFunnelApprovalStatus(
        self, request: analytics_v1_funnel_approval_service_pb2.GetFunnelApprovalStatusRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_funnel_approval_service_pb2.GetFunnelApprovalStatusResponse:
        """Returns a funnel."""
        return await self.handle_get_funnel_approval_status(request)

    @rpc_errors
    @retry_transient
    async def ListPendingFunnels(
        self, request: analytics_v1_funnel_approval_service_pb2.ListPendingFunnelsRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_funnel_approval_service_pb2.ListPendingFunnelsResponse:
        """Lists funnels a page at a time."""
        return await self.handle_list_pending_funnels(request)

    @rpc_errors
    async def RecallFunnel(
        self, request: analytics_v1_funnel_approval_service_pb2.RecallFunnelRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_funnel_approval_service_pb2.RecallFunnelResponse:
        """Recalls a funnel."""
        return await self.handle_recall_funnel(request)

    @rpc_errors
    async def RejectFunnel(
        self, request: analytics_v1_funnel_approval_service_pb2.RejectFunnelRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_funnel_approval_service_pb2.RejectFunnelResponse:
        """Rejects a funnel."""
        return await self.handle_reject_funnel(request)

    @rpc_errors
    async def SubmitFunnel(
        self, request: analytics_v1_funnel_approval_service_pb2.SubmitFunnelRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_funnel_approval_service_pb2.SubmitFunnelResponse:
        """Submits a funnel."""
        return await self.handle_submit_funnel(request)

    async def handle_approve_funnel(
        self,
        request: analytics_v1_funnel_approval_service_pb2.ApproveFunnelRequest
    ) -> analytics_v1_funnel_approval_service_pb2.ApproveFunnelResponse:
        """Approves a funnel."""
        deps = self.deps
        response = analytics_v1_funnel_approval_service_pb2.ApproveFunnelResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ApproveFunnel', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'ApproveFunnel', {'reason': request.reason})
            await deps.repository.save_funnel(request.context.tenant_id, request.funnel)
            response_0 = analytics_v1_funnel_calculation_service_pb2.SimulateFunnelResponse()
            outgoing_0 = analytics_v1_funnel_calculation_service_pb2.SimulateFunnelRequest(
                context=request.context,
                funnel=analytics_v1_analytics_pb2.Funnel(
                    audit=common_v1_audit_pb2.AuditInfo(updated_by=request.funnel.audit.updated_by),
                    discount=analytics_v1_analytics_pb2.FunnelDiscountAction(
                        amount=request.funnel.discount.amount,
                        percent=request.funnel.discount.percent
                    ),
                    owner=identity_v1_refs_pb2.UserRef(user_id=request.details.approver.user_id)
                )
            )
            port_0: FunnelApprovalApproveFunnel0Port = FunnelApprovalApproveFunnel0Adapter(
                deps.clients.analytics_funnel_calculation,
                deps.settings.timeout
            )
            response_0 = await port_0.execute(outgoing_0)
            returned_0_0 = response_0.funnel.status
            if returned_0_0:
                response.funnel.status = returned_0_0
            echoed_0 = request.funnel_id
            response.funnel.funnel_id = echoed_0
            echoed_1 = request.funnel.effective
            response.funnel.effective.CopyFrom(echoed_1)
            return response

    async def handle_comment_funnel_approval(
        self,
        request: analytics_v1_funnel_approval_service_pb2.CommentFunnelApprovalRequest
    ) -> analytics_v1_funnel_approval_service_pb2.CommentFunnelApprovalResponse:
        """Comments a funnel."""
        deps = self.deps
        response = analytics_v1_funnel_approval_service_pb2.CommentFunnelApprovalResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CommentFunnelApproval', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'CommentFunnelApproval', {'reason': request.reason})
            await deps.repository.save_funnel(request.context.tenant_id, request.funnel)
            response_0 = customers_v1_consent_record_calculation_service_pb2.CompareConsentRecordOptionsResponse()
            response_1 = customers_v1_household_calculation_service_pb2.QuoteHouseholdResponse()
            outgoing_0 = customers_v1_consent_record_calculation_service_pb2.CompareConsentRecordOptionsRequest()
            outgoing_0.context.CopyFrom(request.context)
            if request.funnel.WhichOneof('action') == 'block':
                outgoing_0.reason = request.funnel.block.reason
            outgoing_0.consent_record.subject.display_name = request.details.approver.display_name
            response_0 = await deps.clients.customers_consent_record_calculation.CompareConsentRecordOptions(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = customers_v1_household_calculation_service_pb2.QuoteHouseholdRequest(
                context=request.context,
                household=customers_v1_customers_pb2.Household(
                    children=[
                        customers_v1_customers_pb2.Household(
                            children=[
                                customers_v1_customers_pb2.Household(
                                    audit=common_v1_audit_pb2.AuditInfo(etag=request.funnel.audit.etag),
                                    children=[
                                        customers_v1_customers_pb2.Household(
                                            attributes=dict(response_0.consent_record.attributes)
                                        )
                                    ]
                                )
                            ],
                            manager=identity_v1_refs_pb2.UserRef(user_id=request.funnel.owner.user_id)
                        )
                    ]
                )
            )
            response_1 = await FunnelApprovalCommentFunnelApproval1Adapter(
                deps.clients.customers_household_calculation,
                deps.settings.timeout
            )(outgoing_1)
            returned_0_0 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_0)
            returned_1_0 = response_1.household.audit.created_at
            if returned_1_0.ListFields():
                response.funnel.audit.created_at.MergeFrom(returned_1_0)
            echoed_0 = request.funnel_id
            response.funnel.funnel_id = echoed_0
            echoed_1 = request.funnel.owner
            response.funnel.owner.CopyFrom(echoed_1)
            return response

    async def handle_delegate_funnel_approval(
        self,
        request: analytics_v1_funnel_approval_service_pb2.DelegateFunnelApprovalRequest
    ) -> analytics_v1_funnel_approval_service_pb2.DelegateFunnelApprovalResponse:
        """Delegates a funnel."""
        deps = self.deps
        response = analytics_v1_funnel_approval_service_pb2.DelegateFunnelApprovalResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('DelegateFunnelApproval', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'DelegateFunnelApproval', {'reason': request.reason})
            await deps.repository.save_funnel(request.context.tenant_id, request.funnel)
            response_0 = forecasting_v1_forecast_model_workflow_service_pb2.SignalForecastModelWorkflowResponse()
            outgoing_0 = forecasting_v1_forecast_model_workflow_service_pb2.SignalForecastModelWorkflowRequest(
                context=request.context,
                forecast_model=forecasting_v1_forecasting_pb2.ForecastModel(
                    audit=common_v1_audit_pb2.AuditInfo(created_at=request.funnel.audit.created_at)
                )
            )
            response_0 = cast(forecasting_v1_forecast_model_workflow_service_pb2.SignalForecastModelWorkflowResponse, await deps.bus.request(
                'acme.analytics.v1.FunnelApprovalService/DelegateFunnelApproval/0', outgoing_0, deps.settings.timeout,
            ))
            returned_0_0 = response_0.forecast_model.owner
            if returned_0_0.ListFields():
                response.funnel.owner.MergeFrom(returned_0_0)
            echoed_0 = request.funnel_id
            response.funnel.funnel_id = echoed_0
            echoed_1 = request.details.effective_at
            response.outcome.effective_at.CopyFrom(echoed_1)
            return response

    async def handle_escalate_funnel(
        self,
        request: analytics_v1_funnel_approval_service_pb2.EscalateFunnelRequest
    ) -> analytics_v1_funnel_approval_service_pb2.EscalateFunnelResponse:
        """Escalates a funnel."""
        deps = self.deps
        response = analytics_v1_funnel_approval_service_pb2.EscalateFunnelResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('EscalateFunnel', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'EscalateFunnel', {'reason': request.reason})
            await deps.repository.save_funnel(request.context.tenant_id, request.funnel)
            response_0 = audit_v1_audit_event_query_service_pb2.SuggestAuditEventsResponse()
            response_1 = analytics_v1_funnel_calculation_service_pb2.ExplainFunnelCalculationResponse()
            response_2 = ledger_v1_ledger_account_query_service_pb2.FindLedgerAccountsResponse()
            outgoing_0 = audit_v1_audit_event_query_service_pb2.SuggestAuditEventsRequest(
                context=request.context,
                filter=audit_v1_audit_event_query_service_pb2.SuggestAuditEventsRequest.Filter(
                    created_after=request.funnel.audit.updated_at,
                    labels=dict(request.funnel.parameters),
                    owner_id=request.funnel.owner.user_id
                )
            )
            response_0 = await deps.clients.audit_audit_event_query.SuggestAuditEvents(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            requests_1: list[analytics_v1_funnel_calculation_service_pb2.ExplainFunnelCalculationRequest] = []
            for item_1 in request.funnel.conditions:
                outgoing_1 = analytics_v1_funnel_calculation_service_pb2.ExplainFunnelCalculationRequest(
                    context=request.context,
                    funnel=analytics_v1_analytics_pb2.Funnel(
                        conditions=[
                            analytics_v1_analytics_pb2.FunnelCondition(
                                attribute=item_1.attribute,
                                negate=item_1.negate,
                                operator=item_1.operator,
                                value=item_1.value
                            )
                        ]
                    )
                )
                requests_1.append(outgoing_1)
            replies_1 = await asyncio.gather(*(
                deps.clients.analytics_funnel_calculation.ExplainFunnelCalculation(
                    entry,
                    timeout=deps.settings.timeout
                ) for entry in requests_1
            ))
            if replies_1:
                response_1 = replies_1[-1]
            fields_2: dict[str, Any] = {
                'context': request.context,
                'filter': {
                    'created_after': response_1.funnel.audit.updated_at,
                    'labels': dict(response_1.funnel.parameters),
                    'owner_id': request.funnel.owner.user_id
                }
            }
            outgoing_2 = ledger_v1_ledger_account_query_service_pb2.FindLedgerAccountsRequest(**fields_2)
            response_2 = await deps.clients.ledger_ledger_account_query.FindLedgerAccounts(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_0)
            returned_0_1 = response_0.result.status
            if returned_0_1:
                response.outcome.status = returned_0_1
            returned_2_0 = response_2.result.status
            if returned_2_0:
                response.result.status = returned_2_0
            echoed_0 = request.funnel_id
            response.funnel.funnel_id = echoed_0
            echoed_1 = request.funnel.description
            response.funnel.description = echoed_1
            return response

    async def handle_get_funnel_approval_status(
        self,
        request: analytics_v1_funnel_approval_service_pb2.GetFunnelApprovalStatusRequest
    ) -> analytics_v1_funnel_approval_service_pb2.GetFunnelApprovalStatusResponse:
        """Returns a funnel."""
        deps = self.deps
        response = analytics_v1_funnel_approval_service_pb2.GetFunnelApprovalStatusResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('GetFunnelApprovalStatus', extra={'fields': {'domain': 'analytics'}})
            await deps.repository.audit(request.context.tenant_id, 'GetFunnelApprovalStatus', {})
            response_0 = travel_v1_trip_calculation_service_pb2.CalculateTripResponse()
            outgoing_0 = travel_v1_trip_calculation_service_pb2.CalculateTripRequest(
                context=request.context,
                trip=travel_v1_travel_pb2.Trip(
                    audit=common_v1_audit_pb2.AuditInfo(created_at=request.context.deadline),
                    counterparty=employees_v1_refs_pb2.EmployeeRef(email=request.context.actor.email),
                    metadata=dict(request.context.baggage)
                )
            )
            response_0 = await deps.clients.travel_trip_calculation.CalculateTrip(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.trip.audit.etag
            if returned_0_0:
                response.funnel.audit.etag = returned_0_0
            returned_0_1 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_1)
            echoed_0 = request.funnel_id
            response.funnel.funnel_id = echoed_0
            return response

    async def handle_list_pending_funnels(
        self,
        request: analytics_v1_funnel_approval_service_pb2.ListPendingFunnelsRequest
    ) -> analytics_v1_funnel_approval_service_pb2.ListPendingFunnelsResponse:
        """Lists funnels a page at a time."""
        deps = self.deps
        response = analytics_v1_funnel_approval_service_pb2.ListPendingFunnelsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ListPendingFunnels', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(request.context.tenant_id, 'ListPendingFunnels', {'order_by': request.order_by})
            response_0 = analytics_v1_analytics_event_approval_service_pb2.SubmitAnalyticsEventResponse()
            outgoing_0 = analytics_v1_analytics_event_approval_service_pb2.SubmitAnalyticsEventRequest(
                context=request.context,
                details=analytics_v1_analytics_event_approval_service_pb2.SubmitAnalyticsEventRequest.Details(
                    approver=identity_v1_refs_pb2.UserRef(email=request.context.actor.email)
                )
            )
            response_0 = await deps.clients.analytics_analytics_event_approval.SubmitAnalyticsEvent(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.analytics_event.correlation_id
            if returned_0_0:
                response.result.correlation_id = returned_0_0
            return response

    async def handle_recall_funnel(
        self,
        request: analytics_v1_funnel_approval_service_pb2.RecallFunnelRequest
    ) -> analytics_v1_funnel_approval_service_pb2.RecallFunnelResponse:
        """Recalls a funnel."""
        deps = self.deps
        response = analytics_v1_funnel_approval_service_pb2.RecallFunnelResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('RecallFunnel', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'RecallFunnel', {'reason': request.reason})
            await deps.repository.save_funnel(request.context.tenant_id, request.funnel)
            response_0 = customers_v1_customer_query_service_pb2.ResolveCustomersResponse()
            response_1 = analytics_v1_analytics_report_calculation_service_pb2.RecalculateAnalyticsReportsResponse()
            outgoing_0 = customers_v1_customer_query_service_pb2.ResolveCustomersRequest()
            outgoing_0.context.CopyFrom(request.context)
            merged_0 = customers_v1_customer_query_service_pb2.ResolveCustomersRequest()
            merged_0.MergeFrom(outgoing_0)
            outgoing_0.CopyFrom(merged_0)
            response_0 = await deps.clients.customers_customer_query.ResolveCustomers(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = analytics_v1_analytics_report_calculation_service_pb2.RecalculateAnalyticsReportsRequest(
                analytics_report=analytics_v1_analytics_pb2.AnalyticsReport(
                    audit=common_v1_audit_pb2.AuditInfo(
                        created_by=request.funnel.audit.created_by,
                        updated_at=request.funnel.audit.updated_at
                    ),
                    counterparty=customers_v1_refs_pb2.CustomerRef(
                        display_name=request.funnel.owner.display_name,
                        email=request.details.approver.email
                    )
                ),
                context=request.context
            )
            envelope_1 = AnyMessage()
            envelope_1.Pack(outgoing_1)
            outgoing_1 = analytics_v1_analytics_report_calculation_service_pb2.RecalculateAnalyticsReportsRequest()
            if not envelope_1.Unpack(outgoing_1):
                raise ValueError("partner envelope contains the wrong request type")
            response_1 = await deps.clients.analytics_analytics_report_calculation.RecalculateAnalyticsReports(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.outcome.message = returned_0_0
            returned_1_0 = response_1.result.status
            if returned_1_0:
                response.outcome.status = returned_1_0
            echoed_0 = request.funnel_id
            response.funnel.funnel_id = echoed_0
            echoed_1 = request.funnel.owner
            response.funnel.owner.CopyFrom(echoed_1)
            return response

    async def handle_reject_funnel(
        self,
        request: analytics_v1_funnel_approval_service_pb2.RejectFunnelRequest
    ) -> analytics_v1_funnel_approval_service_pb2.RejectFunnelResponse:
        """Rejects a funnel."""
        deps = self.deps
        response = analytics_v1_funnel_approval_service_pb2.RejectFunnelResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('RejectFunnel', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'RejectFunnel', {'reason': request.reason})
            await deps.repository.save_funnel(request.context.tenant_id, request.funnel)
            response_0 = risk_v1_risk_register_query_service_pb2.SummarizeRiskRegistersResponse()
            response_1 = analytics_v1_analytics_event_validation_service_pb2.NormalizeAnalyticsEventResponse()
            response_2 = analytics_v1_analytics_report_validation_service_pb2.NormalizeAnalyticsReportResponse()
            response_3 = analytics_v1_analytics_report_validation_service_pb2.ScoreAnalyticsReportResponse()
            outgoing_0 = risk_v1_risk_register_query_service_pb2.SummarizeRiskRegistersRequest(
                annotations=dict(request.annotations),
                context=request.context,
                reason=request.funnel.block.reason
            )
            registered_0 = cast(
                risk_v1_risk_register_query_service_pb2_grpc.RiskRegisterQueryServiceStub,
                deps.clients.registry['acme.risk.v1.RiskRegisterQueryService']
            )
            response_0 = await registered_0.SummarizeRiskRegisters(outgoing_0, timeout=deps.settings.timeout)
            command_1 = FunnelApprovalRejectFunnel1Command(
                context=request.context,
                details_contact_email=request.funnel.owner.email,
                analytics_event_subject_funnel_id=request.funnel_id,
                analytics_event_subject_display_name=request.details.approver.display_name
            )
            outgoing_1 = to_funnel_approval_reject_funnel1_command(command_1)
            response_1 = await deps.clients.analytics_analytics_event_validation.NormalizeAnalyticsEvent(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = analytics_v1_analytics_report_validation_service_pb2.NormalizeAnalyticsReportRequest()
            outgoing_2.context.CopyFrom(request.context)
            outgoing_2.analytics_report.audit.updated_by = request.funnel.audit.updated_by
            outgoing_2.details.contact.email = request.funnel.owner.email
            if request.funnel.WhichOneof('action') == 'discount':
                field_2_3_part_1 = outgoing_2.analytics_report.lines.add()
                field_2_3_part_1.tax.amount.CopyFrom(request.funnel.discount.amount)
            response_2 = await deps.clients.analytics_analytics_report_validation.NormalizeAnalyticsReport(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            outgoing_3 = analytics_v1_analytics_report_validation_service_pb2.ScoreAnalyticsReportRequest(
                analytics_report=analytics_v1_analytics_pb2.AnalyticsReport(
                    audit=common_v1_audit_pb2.AuditInfo(updated_by=response_2.analytics_report.audit.updated_by),
                    counterparty=customers_v1_refs_pb2.CustomerRef(
                        display_name=response_1.analytics_event.subject.display_name
                    )
                ),
                context=request.context
            )
            send_3 = partial(
                deps.clients.analytics_analytics_report_validation.ScoreAnalyticsReport,
                timeout=deps.settings.timeout
            )
            response_3 = await send_3(outgoing_3)
            returned_0_0 = response_0.result.correlation_id
            if returned_0_0:
                response.result.correlation_id = returned_0_0
            returned_1_0 = response_1.analytics_event.subject.version
            if returned_1_0:
                response.funnel.version = returned_1_0
            returned_1_1 = response_1.outcome.message
            if returned_1_1:
                response.outcome.message = returned_1_1
            returned_2_0 = response_2.analytics_report.audit.created_at
            if returned_2_0.ListFields():
                response.funnel.audit.created_at.MergeFrom(returned_2_0)
            returned_3_0 = response_3.result.status
            if returned_3_0:
                response.outcome.status = returned_3_0
            echoed_0 = request.funnel_id
            response.funnel.funnel_id = echoed_0
            echoed_1 = request.funnel.description
            response.funnel.description = echoed_1
            return response

    async def handle_submit_funnel(
        self,
        request: analytics_v1_funnel_approval_service_pb2.SubmitFunnelRequest
    ) -> analytics_v1_funnel_approval_service_pb2.SubmitFunnelResponse:
        """Submits a funnel."""
        deps = self.deps
        response = analytics_v1_funnel_approval_service_pb2.SubmitFunnelResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SubmitFunnel', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'SubmitFunnel', {'reason': request.reason})
            await deps.repository.save_funnel(request.context.tenant_id, request.funnel)
            response_0 = anomalies_v1_anomaly_feedback_approval_service_pb2.EscalateAnomalyFeedbackResponse()
            response_1 = anomalies_v1_anomaly_feedback_approval_service_pb2.CommentAnomalyFeedbackApprovalResponse()
            outgoing_0 = anomalies_v1_anomaly_feedback_approval_service_pb2.EscalateAnomalyFeedbackRequest(
                anomaly_feedback=anomalies_v1_anomalies_pb2.AnomalyFeedback(
                    subject=datasets_v1_refs_pb2.DatasetRef(display_name=request.details.approver.display_name)
                ),
                context=request.context,
                details=anomalies_v1_anomaly_feedback_approval_service_pb2.EscalateAnomalyFeedbackRequest.Details(
                    approver=identity_v1_refs_pb2.UserRef(
                        display_name=request.funnel.owner.display_name,
                        user_id=request.funnel.owner.user_id
                    ),
                    effective_at=request.details.effective_at
                )
            )
            response_0 = await hooks.funnel_approval_submit_funnel0(
                deps.clients.anomalies_anomaly_feedback_approval,
                outgoing_0,
                deps.settings.timeout
            )
            outgoing_1 = anomalies_v1_anomaly_feedback_approval_service_pb2.CommentAnomalyFeedbackApprovalRequest()
            outgoing_1.context.CopyFrom(request.context)
            outgoing_1.details.approver.email = request.funnel.owner.email
            outgoing_1.details.approver.display_name = request.funnel.owner.display_name
            outgoing_1.anomaly_feedback.subject.display_name = response_0.anomaly_feedback.subject.display_name
            outgoing_1.context.tenant_id = tenant_id.get()
            response_1 = await deps.clients.anomalies_anomaly_feedback_approval.CommentAnomalyFeedbackApproval(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.status
            if returned_0_0:
                response.outcome.status = returned_0_0
            returned_1_0 = response_1.result.status
            if returned_1_0:
                response.result.status = returned_1_0
            echoed_0 = request.funnel_id
            response.funnel.funnel_id = echoed_0
            echoed_1 = request.funnel.status
            response.funnel.status = echoed_1
            return response
