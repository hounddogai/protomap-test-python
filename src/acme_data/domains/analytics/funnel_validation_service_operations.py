"""Functional operations behind FunnelValidationService."""

from __future__ import annotations

from collections.abc import Awaitable
from collections.abc import Callable
from functools import partial
import asyncio
import logging

from acme.analytics.v1 import (
    analytics_event_validation_service_pb2 as analytics_v1_analytics_event_validation_service_pb2,
)
from acme.analytics.v1 import analytics_pb2 as analytics_v1_analytics_pb2
from acme.analytics.v1 import cohort_calculation_service_pb2 as analytics_v1_cohort_calculation_service_pb2
from acme.analytics.v1 import funnel_calculation_service_pb2 as analytics_v1_funnel_calculation_service_pb2
from acme.analytics.v1 import funnel_validation_service_pb2 as analytics_v1_funnel_validation_service_pb2
from acme.analytics.v1 import refs_pb2 as analytics_v1_refs_pb2
from acme.anomalies.v1 import (
    anomaly_feedback_validation_service_pb2 as anomalies_v1_anomaly_feedback_validation_service_pb2,
)
from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.forecasting.v1 import forecast_model_query_service_pb2 as forecasting_v1_forecast_model_query_service_pb2
from acme.ledger.v1 import ledger_account_service_pb2 as ledger_v1_ledger_account_service_pb2
from acme.ledger.v1 import ledger_pb2 as ledger_v1_ledger_pb2
from acme.notifications.v1 import notification_query_service_pb2 as notifications_v1_notification_query_service_pb2

from acme_data.domains.analytics.adapters import FunnelValidationValidateFunnel1Adapter
from acme_data.domains.analytics.dependencies import Dependencies
from acme_data.platform.rpc import async_messages
from acme_data.platform.tenancy import tenant_id
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


async def handle_check_funnel_eligibility(
    deps: Dependencies,
    request: analytics_v1_funnel_validation_service_pb2.CheckFunnelEligibilityRequest
) -> analytics_v1_funnel_validation_service_pb2.CheckFunnelEligibilityResponse:
    """Checks a funnel."""
    response = analytics_v1_funnel_validation_service_pb2.CheckFunnelEligibilityResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('CheckFunnelEligibility', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'CheckFunnelEligibility', {'reason': request.reason})
        await deps.repository.save_funnel(request.context.tenant_id, request.funnel)
        response_0 = forecasting_v1_forecast_model_query_service_pb2.SummarizeForecastModelsResponse()
        outgoing_0 = forecasting_v1_forecast_model_query_service_pb2.SummarizeForecastModelsRequest(
            annotations=dict(request.annotations),
            context=request.context,
            details=forecasting_v1_forecast_model_query_service_pb2.SummarizeForecastModelsRequest.Details(
                period=request.funnel.effective
            ),
            reason=request.funnel.block.reason
        )
        response_0 = await deps.clients.forecasting_forecast_model_query.SummarizeForecastModels(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.result.message
        if returned_0_0:
            response.result.message = returned_0_0
        echoed_0 = request.funnel_id
        response.funnel.funnel_id = echoed_0
        echoed_1 = request.funnel.effective
        response.funnel.effective.CopyFrom(echoed_1)
        return response


async def handle_get_funnel_rules(
    deps: Dependencies,
    request: analytics_v1_funnel_validation_service_pb2.GetFunnelRulesRequest
) -> analytics_v1_funnel_validation_service_pb2.GetFunnelRulesResponse:
    """Returns a funnel."""
    response = analytics_v1_funnel_validation_service_pb2.GetFunnelRulesResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('GetFunnelRules', extra={'fields': {'domain': 'analytics'}})
        await deps.repository.audit(request.context.tenant_id, 'GetFunnelRules', {})
        response_0 = ledger_v1_ledger_account_service_pb2.CreateLedgerAccountResponse()
        outgoing_0 = ledger_v1_ledger_account_service_pb2.CreateLedgerAccountRequest(
            context=request.context,
            ledger_account=ledger_v1_ledger_pb2.LedgerAccount(
                contact=common_v1_contact_pb2.ContactInfo(email=request.context.actor.email),
                external_account_id=request.funnel_id
            )
        )
        response_0 = await deps.clients.ledger_ledger_account.CreateLedgerAccount(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.ledger_account.audit.updated_at
        if returned_0_0.ListFields():
            response.funnel.audit.updated_at.MergeFrom(returned_0_0)
        echoed_0 = request.funnel_id
        response.funnel.funnel_id = echoed_0
        return response


async def handle_normalize_funnel(
    deps: Dependencies,
    request: analytics_v1_funnel_validation_service_pb2.NormalizeFunnelRequest
) -> analytics_v1_funnel_validation_service_pb2.NormalizeFunnelResponse:
    """Normalizes a funnel."""
    response = analytics_v1_funnel_validation_service_pb2.NormalizeFunnelResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('NormalizeFunnel', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'NormalizeFunnel', {'reason': request.reason})
        await deps.repository.save_funnel(request.context.tenant_id, request.funnel)
        response_0 = analytics_v1_funnel_calculation_service_pb2.ExplainFunnelCalculationResponse()
        response_1 = analytics_v1_cohort_calculation_service_pb2.CompareCohortOptionsResponse()
        response_2 = notifications_v1_notification_query_service_pb2.ResolveNotificationsResponse()
        outgoing_0 = analytics_v1_funnel_calculation_service_pb2.ExplainFunnelCalculationRequest(
            context=request.context,
            details=analytics_v1_funnel_calculation_service_pb2.ExplainFunnelCalculationRequest.Details(
                contact=common_v1_contact_pb2.ContactInfo(phone=request.details.contact.phone)
            )
        )
        response_0 = await deps.clients.analytics_funnel_calculation.ExplainFunnelCalculation(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        async for item_1 in async_messages(request.funnel.conditions):
            outgoing_1 = analytics_v1_cohort_calculation_service_pb2.CompareCohortOptionsRequest(
                cohort=analytics_v1_analytics_pb2.Cohort(
                    conditions=[
                        analytics_v1_analytics_pb2.CohortCondition(
                            attribute=item_1.attribute,
                            negate=item_1.negate,
                            operator=item_1.operator,
                            value=item_1.value
                        )
                    ]
                ),
                context=request.context
            )
            response_1 = await deps.clients.analytics_cohort_calculation.CompareCohortOptions(
                outgoing_1,
                timeout=deps.settings.timeout
            )
        outgoing_2 = notifications_v1_notification_query_service_pb2.ResolveNotificationsRequest(
            context=request.context
        )
        send_2 = partial(
            deps.clients.notifications_notification_query.ResolveNotifications,
            timeout=deps.settings.timeout
        )
        response_2 = await send_2(outgoing_2)
        returned_0_0 = response_0.outcome.status
        if returned_0_0:
            response.result.status = returned_0_0
        returned_0_1 = response_0.funnel.name
        if returned_0_1:
            response.funnel.name = returned_0_1
        returned_2_0 = response_2.result.reference_ids
        response.result.reference_ids.extend(returned_2_0)
        returned_2_1 = response_2.result.status
        if returned_2_1:
            response.result.status = returned_2_1
        echoed_0 = request.funnel_id
        response.funnel.funnel_id = echoed_0
        echoed_1 = request.funnel.version
        response.funnel.version = echoed_1
        return response


async def handle_preview_funnel(
    deps: Dependencies,
    request: analytics_v1_funnel_validation_service_pb2.PreviewFunnelRequest
) -> analytics_v1_funnel_validation_service_pb2.PreviewFunnelResponse:
    """Previews a funnel."""
    response = analytics_v1_funnel_validation_service_pb2.PreviewFunnelResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('PreviewFunnel', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'PreviewFunnel', {'reason': request.reason})
        await deps.repository.save_funnel(request.context.tenant_id, request.funnel)
        response_0 = analytics_v1_analytics_event_validation_service_pb2.ExplainAnalyticsEventDecisionResponse()
        response_1 = analytics_v1_analytics_event_validation_service_pb2.LintAnalyticsEventsResponse()
        outgoing_0 = analytics_v1_analytics_event_validation_service_pb2.ExplainAnalyticsEventDecisionRequest(
            analytics_event=analytics_v1_analytics_pb2.AnalyticsEvent(
                subject=analytics_v1_refs_pb2.FunnelRef(funnel_id=request.funnel.funnel_id)
            ),
            context=request.context,
            details=analytics_v1_analytics_event_validation_service_pb2.ExplainAnalyticsEventDecisionRequest.Details(
                contact=common_v1_contact_pb2.ContactInfo(preferred_channel=request.details.contact.preferred_channel)
            )
        )
        response_0 = await deps.clients.analytics_analytics_event_validation.ExplainAnalyticsEventDecision(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = analytics_v1_analytics_event_validation_service_pb2.LintAnalyticsEventsRequest()
        outgoing_1.context.CopyFrom(request.context)
        outgoing_1.details.contact.phone = request.details.contact.phone
        outgoing_1.context.tenant_id = tenant_id.get()
        response_1 = await deps.clients.analytics_analytics_event_validation.LintAnalyticsEvents(
            outgoing_1,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.result.correlation_id
        if returned_0_0:
            response.result.correlation_id = returned_0_0
        returned_1_0 = response_1.analytics_event.subject.display_name
        if returned_1_0:
            response.funnel.owner.display_name = returned_1_0
        returned_1_1 = response_1.outcome.message
        if returned_1_1:
            response.result.message = returned_1_1
        echoed_0 = request.funnel_id
        response.funnel.funnel_id = echoed_0
        echoed_1 = request.funnel.description
        response.funnel.description = echoed_1
        return response


async def handle_score_funnel(
    deps: Dependencies,
    request: analytics_v1_funnel_validation_service_pb2.ScoreFunnelRequest
) -> analytics_v1_funnel_validation_service_pb2.ScoreFunnelResponse:
    """Scores a funnel."""
    response = analytics_v1_funnel_validation_service_pb2.ScoreFunnelResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('ScoreFunnel', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'ScoreFunnel', {'reason': request.reason})
        await deps.repository.save_funnel(request.context.tenant_id, request.funnel)
        response_0 = analytics_v1_cohort_calculation_service_pb2.QuoteCohortResponse()
        outgoing_0 = analytics_v1_cohort_calculation_service_pb2.QuoteCohortRequest(
            cohort=analytics_v1_analytics_pb2.Cohort(
                audit=common_v1_audit_pb2.AuditInfo(updated_by=request.funnel.audit.updated_by),
                block=analytics_v1_analytics_pb2.CohortBlockAction(notify_email=request.funnel.block.notify_email)
            ),
            context=request.context,
            details=analytics_v1_cohort_calculation_service_pb2.QuoteCohortRequest.Details(
                destination=common_v1_address_pb2.PostalAddress(
                    recipient=request.details.destination.recipient,
                    region=request.details.destination.region
                )
            )
        )
        response_0 = await deps.clients.analytics_cohort_calculation.QuoteCohort(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.cohort.owner
        if returned_0_0.ListFields():
            response.funnel.owner.MergeFrom(returned_0_0)
        returned_0_1 = response_0.cohort.description
        if returned_0_1:
            response.funnel.description = returned_0_1
        echoed_0 = request.funnel_id
        response.funnel.funnel_id = echoed_0
        echoed_1 = request.funnel.status
        response.funnel.status = echoed_1
        return response


async def handle_validate_funnel(
    deps: Dependencies,
    request: analytics_v1_funnel_validation_service_pb2.ValidateFunnelRequest
) -> analytics_v1_funnel_validation_service_pb2.ValidateFunnelResponse:
    """Validates a funnel."""
    response = analytics_v1_funnel_validation_service_pb2.ValidateFunnelResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('ValidateFunnel', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'ValidateFunnel', {'reason': request.reason})
        await deps.repository.save_funnel(request.context.tenant_id, request.funnel)
        response_0 = analytics_v1_cohort_calculation_service_pb2.QuoteCohortResponse()
        response_1 = anomalies_v1_anomaly_feedback_validation_service_pb2.NormalizeAnomalyFeedbackResponse()
        for item_0 in request.funnel.conditions:
            outgoing_0 = analytics_v1_cohort_calculation_service_pb2.QuoteCohortRequest(
                cohort=analytics_v1_analytics_pb2.Cohort(
                    conditions=[analytics_v1_analytics_pb2.CohortCondition(value=item_0.value)]
                ),
                context=request.context
            )
            response_0 = await deps.clients.analytics_cohort_calculation.QuoteCohort(
                outgoing_0,
                timeout=deps.settings.timeout
            )
        outgoing_1 = anomalies_v1_anomaly_feedback_validation_service_pb2.NormalizeAnomalyFeedbackRequest(
            context=request.context,
            details=anomalies_v1_anomaly_feedback_validation_service_pb2.NormalizeAnomalyFeedbackRequest.Details(
                contact=common_v1_contact_pb2.ContactInfo(email=response_0.cohort.owner.email)
            )
        )
        response_1 = await FunnelValidationValidateFunnel1Adapter(
            deps.clients.anomalies_anomaly_feedback_validation,
            deps.settings.timeout
        )(outgoing_1)
        returned_1_0 = response_1.result.details
        response.result.details.update(returned_1_0)
        returned_1_1 = response_1.result.message
        if returned_1_1:
            response.result.message = returned_1_1
        echoed_0 = request.funnel_id
        response.funnel.funnel_id = echoed_0
        echoed_1 = request.funnel.effective
        response.funnel.effective.CopyFrom(echoed_1)
        return response
