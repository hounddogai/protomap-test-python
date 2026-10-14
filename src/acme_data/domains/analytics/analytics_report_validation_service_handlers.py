"""Reusable transport mixin for AnalyticsReportValidationService."""

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
from google.protobuf.json_format import ParseDict
import grpc

from acme.analytics.v1 import (
    analytics_event_validation_service_pb2 as analytics_v1_analytics_event_validation_service_pb2,
)
from acme.analytics.v1 import analytics_pb2 as analytics_v1_analytics_pb2
from acme.analytics.v1 import (
    analytics_report_validation_service_pb2 as analytics_v1_analytics_report_validation_service_pb2,
)
from acme.analytics.v1 import cohort_validation_service_pb2 as analytics_v1_cohort_validation_service_pb2
from acme.analytics.v1 import funnel_calculation_service_pb2 as analytics_v1_funnel_calculation_service_pb2
from acme.analytics.v1 import funnel_validation_service_pb2 as analytics_v1_funnel_validation_service_pb2
from acme.anomalies.v1 import anomalies_pb2 as anomalies_v1_anomalies_pb2
from acme.anomalies.v1 import (
    anomaly_feedback_calculation_service_pb2 as anomalies_v1_anomaly_feedback_calculation_service_pb2,
)
from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.customers.v1 import refs_pb2 as customers_v1_refs_pb2
from acme.datasets.v1 import refs_pb2 as datasets_v1_refs_pb2
from acme.identity.v1 import identity_pb2 as identity_v1_identity_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.identity.v1 import user_validation_service_pb2 as identity_v1_user_validation_service_pb2
from acme.ledger.v1 import ledger_account_validation_service_pb2 as ledger_v1_ledger_account_validation_service_pb2
from acme.performers.v1 import performer_query_service_pb2 as performers_v1_performer_query_service_pb2
from acme.recommendations.v1 import (
    interaction_calculation_service_pb2 as recommendations_v1_interaction_calculation_service_pb2,
)
from acme.recommendations.v1 import recommendations_pb2 as recommendations_v1_recommendations_pb2
from acme.secrets.v1 import secret_query_service_pb2 as secrets_v1_secret_query_service_pb2
from acme.ticketing.v1 import ticket_query_service_pb2 as ticketing_v1_ticket_query_service_pb2

from acme_data.domains.analytics import hooks
from acme_data.domains.analytics.adapters import AnalyticsReportValidationPreviewAnalyticsReport1Adapter
from acme_data.domains.analytics.dependencies import Dependencies
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import run_steps
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_id
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class AnalyticsReportValidationServicerHandlers:
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    async def ExplainAnalyticsReportDecision(
        self, request: analytics_v1_analytics_report_validation_service_pb2.ExplainAnalyticsReportDecisionRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_analytics_report_validation_service_pb2.ExplainAnalyticsReportDecisionResponse:
        """Explains an analytics report."""
        return await self.handle_explain_analytics_report_decision(request)

    @rpc_errors
    @retry_transient
    async def GetAnalyticsReportRules(
        self, request: analytics_v1_analytics_report_validation_service_pb2.GetAnalyticsReportRulesRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_analytics_report_validation_service_pb2.GetAnalyticsReportRulesResponse:
        """Returns an analytics report."""
        return await self.handle_get_analytics_report_rules(request)

    @rpc_errors
    async def LintAnalyticsReports(
        self, request: analytics_v1_analytics_report_validation_service_pb2.LintAnalyticsReportsRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_analytics_report_validation_service_pb2.LintAnalyticsReportsResponse:
        """Lints an analytics report."""
        return await self.handle_lint_analytics_reports(request)

    @rpc_errors
    async def NormalizeAnalyticsReport(
        self, request: analytics_v1_analytics_report_validation_service_pb2.NormalizeAnalyticsReportRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_analytics_report_validation_service_pb2.NormalizeAnalyticsReportResponse:
        """Normalizes an analytics report."""
        return await self.handle_normalize_analytics_report(request)

    @rpc_errors
    async def PreviewAnalyticsReport(
        self, request: analytics_v1_analytics_report_validation_service_pb2.PreviewAnalyticsReportRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_analytics_report_validation_service_pb2.PreviewAnalyticsReportResponse:
        """Previews an analytics report."""
        return await self.handle_preview_analytics_report(request)

    @rpc_errors
    async def ScoreAnalyticsReport(
        self, request: analytics_v1_analytics_report_validation_service_pb2.ScoreAnalyticsReportRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_analytics_report_validation_service_pb2.ScoreAnalyticsReportResponse:
        """Scores an analytics report."""
        return await self.handle_score_analytics_report(request)

    @rpc_errors
    async def ValidateAnalyticsReport(
        self, request: analytics_v1_analytics_report_validation_service_pb2.ValidateAnalyticsReportRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_analytics_report_validation_service_pb2.ValidateAnalyticsReportResponse:
        """Validates an analytics report."""
        return await self.handle_validate_analytics_report(request)

    async def handle_explain_analytics_report_decision(
        self,
        request: analytics_v1_analytics_report_validation_service_pb2.ExplainAnalyticsReportDecisionRequest
    ) -> analytics_v1_analytics_report_validation_service_pb2.ExplainAnalyticsReportDecisionResponse:
        """Explains an analytics report."""
        deps = self.deps
        response = analytics_v1_analytics_report_validation_service_pb2.ExplainAnalyticsReportDecisionResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ExplainAnalyticsReportDecision', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ExplainAnalyticsReportDecision',
                {'reason': request.reason}
            )
            await deps.repository.save_analytics_report(request.context.tenant_id, request.analytics_report)
            response_0 = analytics_v1_cohort_validation_service_pb2.PreviewCohortResponse()
            response_1 = analytics_v1_analytics_event_validation_service_pb2.ValidateAnalyticsEventResponse()
            outgoing_0 = analytics_v1_cohort_validation_service_pb2.PreviewCohortRequest()
            outgoing_0.context.CopyFrom(request.context)
            outgoing_0.cohort.audit.created_by = request.analytics_report.audit.created_by
            merged_0 = analytics_v1_cohort_validation_service_pb2.PreviewCohortRequest()
            merged_0.MergeFrom(outgoing_0)
            outgoing_0.CopyFrom(merged_0)
            response_0 = await deps.clients.analytics_cohort_validation.PreviewCohort(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = analytics_v1_analytics_event_validation_service_pb2.ValidateAnalyticsEventRequest(
                context=request.context,
                details=analytics_v1_analytics_event_validation_service_pb2.ValidateAnalyticsEventRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(email=response_0.cohort.owner.email)
                )
            )
            envelope_1 = AnyMessage()
            envelope_1.Pack(outgoing_1)
            outgoing_1 = analytics_v1_analytics_event_validation_service_pb2.ValidateAnalyticsEventRequest()
            if not envelope_1.Unpack(outgoing_1):
                raise ValueError("partner envelope contains the wrong request type")
            response_1 = await deps.clients.analytics_analytics_event_validation.ValidateAnalyticsEvent(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.correlation_id
            if returned_0_0:
                response.result.correlation_id = returned_0_0
            returned_1_0 = response_1.outcome.status
            if returned_1_0:
                response.outcome.status = returned_1_0
            returned_1_1 = response_1.outcome.message
            if returned_1_1:
                response.outcome.message = returned_1_1
            echoed_0 = request.analytics_report_id
            response.analytics_report.analytics_report_id = echoed_0
            echoed_1 = request.analytics_report.total
            response.analytics_report.total.CopyFrom(echoed_1)
            return response

    async def handle_get_analytics_report_rules(
        self,
        request: analytics_v1_analytics_report_validation_service_pb2.GetAnalyticsReportRulesRequest
    ) -> analytics_v1_analytics_report_validation_service_pb2.GetAnalyticsReportRulesResponse:
        """Returns an analytics report."""
        deps = self.deps
        response = analytics_v1_analytics_report_validation_service_pb2.GetAnalyticsReportRulesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('GetAnalyticsReportRules', extra={'fields': {'domain': 'analytics'}})
            await deps.repository.audit(request.context.tenant_id, 'GetAnalyticsReportRules', {})
            response_0 = analytics_v1_cohort_validation_service_pb2.ScoreCohortResponse()
            outgoing_0 = analytics_v1_cohort_validation_service_pb2.ScoreCohortRequest(
                cohort=analytics_v1_analytics_pb2.Cohort(
                    owner=identity_v1_refs_pb2.UserRef(
                        email=request.context.actor.email,
                        user_id=request.context.actor.user_id
                    )
                ),
                context=request.context
            )
            response_0 = await deps.clients.analytics_cohort_validation.ScoreCohort(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.cohort.owner.display_name
            if returned_0_0:
                response.analytics_report.counterparty.display_name = returned_0_0
            returned_0_1 = response_0.cohort.owner.email
            if returned_0_1:
                response.analytics_report.counterparty.email = returned_0_1
            echoed_0 = request.analytics_report_id
            response.analytics_report.analytics_report_id = echoed_0
            return response

    async def handle_lint_analytics_reports(
        self,
        request: analytics_v1_analytics_report_validation_service_pb2.LintAnalyticsReportsRequest
    ) -> analytics_v1_analytics_report_validation_service_pb2.LintAnalyticsReportsResponse:
        """Lints an analytics report."""
        deps = self.deps
        response = analytics_v1_analytics_report_validation_service_pb2.LintAnalyticsReportsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('LintAnalyticsReports', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'LintAnalyticsReports', {'reason': request.reason})
            await deps.repository.save_analytics_report(request.context.tenant_id, request.analytics_report)
            response_0 = analytics_v1_funnel_validation_service_pb2.NormalizeFunnelResponse()
            response_1 = recommendations_v1_interaction_calculation_service_pb2.CalculateInteractionResponse()
            response_2 = analytics_v1_funnel_calculation_service_pb2.CompareFunnelOptionsResponse()
            outgoing_0 = analytics_v1_funnel_validation_service_pb2.NormalizeFunnelRequest(
                context=request.context,
                details=analytics_v1_funnel_validation_service_pb2.NormalizeFunnelRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(
                        phone=request.details.contact.phone,
                        preferred_channel=request.details.contact.preferred_channel
                    )
                ),
                funnel=analytics_v1_analytics_pb2.Funnel(
                    audit=common_v1_audit_pb2.AuditInfo(updated_by=request.analytics_report.audit.updated_by)
                )
            )
            outgoing_1 = recommendations_v1_interaction_calculation_service_pb2.CalculateInteractionRequest(
                context=request.context,
                details=recommendations_v1_interaction_calculation_service_pb2.CalculateInteractionRequest.Details(
                    destination=common_v1_address_pb2.PostalAddress(
                        lines=list(request.analytics_report.billing_address.lines),
                        postal_code=request.analytics_report.billing_address.postal_code
                    )
                ),
                interaction=recommendations_v1_recommendations_pb2.Interaction(
                    subject=customers_v1_refs_pb2.CustomerRef(
                        display_name=request.analytics_report.counterparty.display_name,
                        email=request.details.contact.email
                    )
                )
            )
            response_0, response_1 = await asyncio.gather(
                deps.clients.analytics_funnel_validation.NormalizeFunnel(outgoing_0, timeout=deps.settings.timeout),
                deps.clients.recommendations_interaction_calculation.CalculateInteraction(
                    outgoing_1,
                    timeout=deps.settings.timeout
                ),
            )
            outgoing_2 = analytics_v1_funnel_calculation_service_pb2.CompareFunnelOptionsRequest(
                context=request.context,
                funnel=analytics_v1_analytics_pb2.Funnel(
                    audit=common_v1_audit_pb2.AuditInfo(created_by=response_0.funnel.audit.created_by),
                    route=analytics_v1_analytics_pb2.FunnelRouteAction(
                        target=response_0.funnel.route.target,
                        weight=response_0.funnel.route.weight
                    )
                )
            )
            send_2 = partial(
                deps.clients.analytics_funnel_calculation.CompareFunnelOptions,
                timeout=deps.settings.timeout
            )
            response_2 = await send_2(outgoing_2)
            returned_0_0 = response_0.funnel.audit.created_at
            if returned_0_0.ListFields():
                response.analytics_report.audit.created_at.MergeFrom(returned_0_0)
            returned_0_1 = response_0.result.message
            if returned_0_1:
                response.outcome.message = returned_0_1
            returned_1_0 = response_1.result.correlation_id
            if returned_1_0:
                response.result.correlation_id = returned_1_0
            returned_1_1 = response_1.interaction.subject.email
            if returned_1_1:
                response.analytics_report.counterparty.email = returned_1_1
            returned_2_0 = response_2.funnel.owner.display_name
            if returned_2_0:
                response.analytics_report.counterparty.display_name = returned_2_0
            returned_2_1 = response_2.funnel.discount.amount
            returned_2_1_part_1 = response.analytics_report.lines.add()
            if returned_2_1.ListFields():
                returned_2_1_part_1.amount.MergeFrom(returned_2_1)
            echoed_0 = request.analytics_report_id
            response.analytics_report.analytics_report_id = echoed_0
            echoed_1 = request.analytics_report.status
            response.analytics_report.status = echoed_1
            return response

    async def handle_normalize_analytics_report(
        self,
        request: analytics_v1_analytics_report_validation_service_pb2.NormalizeAnalyticsReportRequest
    ) -> analytics_v1_analytics_report_validation_service_pb2.NormalizeAnalyticsReportResponse:
        """Normalizes an analytics report."""
        deps = self.deps
        response = analytics_v1_analytics_report_validation_service_pb2.NormalizeAnalyticsReportResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('NormalizeAnalyticsReport', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'NormalizeAnalyticsReport',
                {'reason': request.reason}
            )
            await deps.repository.save_analytics_report(request.context.tenant_id, request.analytics_report)
            response_0 = ledger_v1_ledger_account_validation_service_pb2.PreviewLedgerAccountResponse()
            response_1 = analytics_v1_analytics_event_validation_service_pb2.ValidateAnalyticsEventResponse()
            response_2 = analytics_v1_cohort_validation_service_pb2.PreviewCohortResponse()
            outgoing_0 = ledger_v1_ledger_account_validation_service_pb2.PreviewLedgerAccountRequest(
                context=request.context,
                details=ledger_v1_ledger_account_validation_service_pb2.PreviewLedgerAccountRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(email=request.details.contact.email)
                )
            )
            response_0 = await hooks.analytics_report_validation_normalize_analytics_report0(
                deps.clients.ledger_ledger_account_validation,
                outgoing_0,
                deps.settings.timeout
            )
            outgoing_1 = analytics_v1_analytics_event_validation_service_pb2.ValidateAnalyticsEventRequest()
            outgoing_1.context.CopyFrom(request.context)
            outgoing_1.details.contact.email = response_0.ledger_account.contact.email
            outgoing_1.analytics_event.subject.display_name = request.analytics_report.counterparty.display_name
            outgoing_1.details.contact.phone = response_0.ledger_account.contact.phone
            outgoing_1.context.tenant_id = tenant_id.get()
            response_1 = await deps.clients.analytics_analytics_event_validation.ValidateAnalyticsEvent(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            for item_2 in request.analytics_report.lines:
                outgoing_2 = analytics_v1_cohort_validation_service_pb2.PreviewCohortRequest(
                    cohort=analytics_v1_analytics_pb2.Cohort(
                        audit=common_v1_audit_pb2.AuditInfo(created_by=request.analytics_report.audit.created_by),
                        description=item_2.description,
                        discount=analytics_v1_analytics_pb2.CohortDiscountAction(amount=item_2.tax.amount)
                    ),
                    context=request.context
                )
                response_2 = await deps.clients.analytics_cohort_validation.PreviewCohort(
                    outgoing_2,
                    timeout=deps.settings.timeout
                )
            returned_0_0 = response_0.outcome.message
            if returned_0_0:
                response.result.message = returned_0_0
            returned_0_1 = response_0.outcome.next_steps
            response.outcome.next_steps.extend(returned_0_1)
            returned_1_0 = response_1.result.details
            response.result.details.update(returned_1_0)
            echoed_0 = request.analytics_report_id
            response.analytics_report.analytics_report_id = echoed_0
            echoed_1 = request.analytics_report.number
            response.analytics_report.number = echoed_1
            return response

    async def handle_preview_analytics_report(
        self,
        request: analytics_v1_analytics_report_validation_service_pb2.PreviewAnalyticsReportRequest
    ) -> analytics_v1_analytics_report_validation_service_pb2.PreviewAnalyticsReportResponse:
        """Previews an analytics report."""
        deps = self.deps
        response = analytics_v1_analytics_report_validation_service_pb2.PreviewAnalyticsReportResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('PreviewAnalyticsReport', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'PreviewAnalyticsReport', {'reason': request.reason})
            await deps.repository.save_analytics_report(request.context.tenant_id, request.analytics_report)
            response_0 = ticketing_v1_ticket_query_service_pb2.CountTicketsResponse()
            response_1 = analytics_v1_cohort_validation_service_pb2.PreviewCohortResponse()
            response_2 = identity_v1_user_validation_service_pb2.ExplainUserDecisionResponse()
            outgoing_0 = ticketing_v1_ticket_query_service_pb2.CountTicketsRequest(
                context=request.context,
                filter=ticketing_v1_ticket_query_service_pb2.CountTicketsRequest.Filter(
                    region=request.analytics_report.billing_address.region
                )
            )
            steps_0 = [
                partial(deps.clients.ticketing_ticket_query.CountTickets, outgoing_0, timeout=deps.settings.timeout)
            ]
            results_0 = await run_steps(steps_0)
            response_0 = results_0[-1]
            outgoing_1 = analytics_v1_cohort_validation_service_pb2.PreviewCohortRequest(
                cohort=analytics_v1_analytics_pb2.Cohort(
                    audit=common_v1_audit_pb2.AuditInfo(created_at=request.analytics_report.audit.created_at)
                ),
                context=request.context,
                details=analytics_v1_cohort_validation_service_pb2.PreviewCohortRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(phone=request.details.contact.phone)
                )
            )
            response_1 = await AnalyticsReportValidationPreviewAnalyticsReport1Adapter(
                deps.clients.analytics_cohort_validation,
                deps.settings.timeout
            )(outgoing_1)
            outgoing_2 = identity_v1_user_validation_service_pb2.ExplainUserDecisionRequest(
                context=request.context,
                user=identity_v1_identity_pb2.User(
                    contact=common_v1_contact_pb2.ContactInfo(
                        preferred_channel=request.details.contact.preferred_channel
                    )
                )
            )
            response_2 = cast(identity_v1_user_validation_service_pb2.ExplainUserDecisionResponse, await deps.bus.request(
                'acme.analytics.v1.AnalyticsReportValidationService/PreviewAnalyticsReport/2', outgoing_2, deps.settings.timeout,
            ))
            returned_0_0 = response_0.result.status
            if returned_0_0:
                response.result.status = returned_0_0
            returned_1_0 = response_1.cohort.audit.updated_at
            if returned_1_0.ListFields():
                response.analytics_report.audit.updated_at.MergeFrom(returned_1_0)
            returned_2_0 = response_2.result.message
            if returned_2_0:
                response.result.message = returned_2_0
            echoed_0 = request.analytics_report_id
            response.analytics_report.analytics_report_id = echoed_0
            echoed_1 = request.analytics_report.total
            response.analytics_report.total.CopyFrom(echoed_1)
            return response

    async def handle_score_analytics_report(
        self,
        request: analytics_v1_analytics_report_validation_service_pb2.ScoreAnalyticsReportRequest
    ) -> analytics_v1_analytics_report_validation_service_pb2.ScoreAnalyticsReportResponse:
        """Scores an analytics report."""
        deps = self.deps
        response = analytics_v1_analytics_report_validation_service_pb2.ScoreAnalyticsReportResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ScoreAnalyticsReport', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'ScoreAnalyticsReport', {'reason': request.reason})
            await deps.repository.save_analytics_report(request.context.tenant_id, request.analytics_report)
            response_0 = anomalies_v1_anomaly_feedback_calculation_service_pb2.CompareAnomalyFeedbackOptionsResponse()
            outgoing_0 = anomalies_v1_anomaly_feedback_calculation_service_pb2.CompareAnomalyFeedbackOptionsRequest(
                anomaly_feedback=anomalies_v1_anomalies_pb2.AnomalyFeedback(
                    subject=datasets_v1_refs_pb2.DatasetRef(
                        display_name=request.analytics_report.counterparty.display_name
                    )
                ),
                context=request.context,
                details=anomalies_v1_anomaly_feedback_calculation_service_pb2.CompareAnomalyFeedbackOptionsRequest.Details(
                    destination=common_v1_address_pb2.PostalAddress(
                        country_code=request.details.destination.country_code,
                        region=request.details.destination.region
                    )
                )
            )
            response_0 = await deps.clients.anomalies_anomaly_feedback_calculation.CompareAnomalyFeedbackOptions(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.result.message = returned_0_0
            returned_0_1 = response_0.anomaly_feedback.correlation_id
            if returned_0_1:
                response.result.correlation_id = returned_0_1
            echoed_0 = request.analytics_report_id
            response.analytics_report.analytics_report_id = echoed_0
            echoed_1 = request.analytics_report.notes
            response.analytics_report.notes = echoed_1
            return response

    async def handle_validate_analytics_report(
        self,
        request: analytics_v1_analytics_report_validation_service_pb2.ValidateAnalyticsReportRequest
    ) -> analytics_v1_analytics_report_validation_service_pb2.ValidateAnalyticsReportResponse:
        """Validates an analytics report."""
        deps = self.deps
        response = analytics_v1_analytics_report_validation_service_pb2.ValidateAnalyticsReportResponse()
        with tenant_scope(request.context.tenant_id):
            log.info(
                'ValidateAnalyticsReport',
                extra={'fields': {'analytics_report_id': request.analytics_report.analytics_report_id}}
            )
            await deps.repository.audit(
                request.context.tenant_id,
                'ValidateAnalyticsReport',
                {'analytics_report_id': request.analytics_report.analytics_report_id}
            )
            await deps.repository.save_analytics_report(request.context.tenant_id, request.analytics_report)
            response_0 = analytics_v1_analytics_event_validation_service_pb2.PreviewAnalyticsEventResponse()
            response_1 = secrets_v1_secret_query_service_pb2.SummarizeSecretsResponse()
            response_2 = performers_v1_performer_query_service_pb2.SummarizePerformersResponse()
            outgoing_0 = analytics_v1_analytics_event_validation_service_pb2.PreviewAnalyticsEventRequest(
                context=request.context,
                details=analytics_v1_analytics_event_validation_service_pb2.PreviewAnalyticsEventRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(
                        name=request.details.contact.name,
                        preferred_channel=request.details.contact.preferred_channel
                    )
                )
            )
            method_name_0 = 'PreviewAnalyticsEvent'
            response_0 = await getattr(
                deps.clients.analytics_analytics_event_validation,
                method_name_0
            )(outgoing_0, timeout=deps.settings.timeout)
            requests_1: list[secrets_v1_secret_query_service_pb2.SummarizeSecretsRequest] = []
            for item_1 in request.analytics_report.lines:
                outgoing_1 = secrets_v1_secret_query_service_pb2.SummarizeSecretsRequest(
                    context=request.context,
                    details=secrets_v1_secret_query_service_pb2.SummarizeSecretsRequest.Details(
                        filters=dict(item_1.attributes)
                    )
                )
                requests_1.append(outgoing_1)
            replies_1 = await asyncio.gather(*(
                deps.clients.secrets_secret_query.SummarizeSecrets(
                    entry,
                    timeout=deps.settings.timeout
                ) for entry in requests_1
            ))
            if replies_1:
                response_1 = replies_1[-1]
            outgoing_2 = performers_v1_performer_query_service_pb2.SummarizePerformersRequest(
                annotations=dict(request.annotations),
                context=request.context,
                details=performers_v1_performer_query_service_pb2.SummarizePerformersRequest.Details(
                    filters=dict(request.analytics_report.metadata),
                    period=response_1.period
                ),
                reason=request.reason
            )
            document_2 = MessageToDict(outgoing_2, preserving_proto_field_name=True)
            outgoing_2 = ParseDict(document_2, performers_v1_performer_query_service_pb2.SummarizePerformersRequest())
            response_2 = await deps.clients.performers_performer_query.SummarizePerformers(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.outcome.message = returned_0_0
            returned_0_1 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_1)
            returned_2_0 = response_2.result.status
            if returned_2_0:
                response.outcome.status = returned_2_0
            returned_2_1 = response_2.result.message
            if returned_2_1:
                response.outcome.message = returned_2_1
            echoed_0 = request.analytics_report_id
            response.analytics_report.analytics_report_id = echoed_0
            echoed_1 = request.analytics_report.number
            response.analytics_report.number = echoed_1
            return response
