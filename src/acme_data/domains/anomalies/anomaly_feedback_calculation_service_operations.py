"""Functional operations behind AnomalyFeedbackCalculationService."""

from __future__ import annotations

from collections.abc import Awaitable
from collections.abc import Callable
from functools import partial
import asyncio
import logging

from google.protobuf.any_pb2 import Any as AnyMessage
from google.protobuf.json_format import MessageToJson
from google.protobuf.json_format import Parse

from acme.anomalies.v1 import anomalies_pb2 as anomalies_v1_anomalies_pb2
from acme.anomalies.v1 import (
    anomaly_feedback_calculation_service_pb2 as anomalies_v1_anomaly_feedback_calculation_service_pb2,
)
from acme.anomalies.v1 import anomaly_validation_service_pb2 as anomalies_v1_anomaly_validation_service_pb2
from acme.anomalies.v1 import refs_pb2 as anomalies_v1_refs_pb2
from acme.careplans.v1 import care_plan_query_service_pb2 as careplans_v1_care_plan_query_service_pb2
from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.customers.v1 import refs_pb2 as customers_v1_refs_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.identity.v1 import user_query_service_pb2 as identity_v1_user_query_service_pb2
from acme.ledger.v1 import ledger_account_validation_service_pb2 as ledger_v1_ledger_account_validation_service_pb2
from acme.ledger.v1 import ledger_pb2 as ledger_v1_ledger_pb2
from acme.lineage.v1 import impact_calculation_service_pb2 as lineage_v1_impact_calculation_service_pb2
from acme.lineage.v1 import lineage_edge_validation_service_pb2 as lineage_v1_lineage_edge_validation_service_pb2
from acme.lineage.v1 import lineage_pb2 as lineage_v1_lineage_pb2
from acme.lineage.v1 import refs_pb2 as lineage_v1_refs_pb2
from acme.metrics.v1 import metric_alert_validation_service_pb2 as metrics_v1_metric_alert_validation_service_pb2
from acme.metrics.v1 import metrics_pb2 as metrics_v1_metrics_pb2

from acme_data.domains.anomalies.adapters import AnomalyFeedbackCalculationSimulateAnomalyFeedback1Adapter
from acme_data.domains.anomalies.adapters import AnomalyFeedbackCalculationSimulateAnomalyFeedback1Port
from acme_data.domains.anomalies.dependencies import Dependencies
from acme_data.domains.anomalies.models import AnomalyFeedbackCalculationQuoteAnomalyFeedback2Command
from acme_data.domains.anomalies.models import to_anomaly_feedback_calculation_quote_anomaly_feedback2_command
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import run_steps
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


async def handle_calculate_anomaly_feedback(
    deps: Dependencies,
    request: anomalies_v1_anomaly_feedback_calculation_service_pb2.CalculateAnomalyFeedbackRequest
) -> anomalies_v1_anomaly_feedback_calculation_service_pb2.CalculateAnomalyFeedbackResponse:
    """Calculates an anomaly feedback."""
    response = anomalies_v1_anomaly_feedback_calculation_service_pb2.CalculateAnomalyFeedbackResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('CalculateAnomalyFeedback', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'CalculateAnomalyFeedback', {'reason': request.reason})
        await deps.repository.save_anomaly_feedback(request.context.tenant_id, request.anomaly_feedback)
        response_0 = anomalies_v1_anomaly_validation_service_pb2.ScoreAnomalyResponse()
        outgoing_0 = anomalies_v1_anomaly_validation_service_pb2.ScoreAnomalyRequest(
            context=request.context,
            details=anomalies_v1_anomaly_validation_service_pb2.ScoreAnomalyRequest.Details(
                destination=common_v1_address_pb2.PostalAddress(
                    postal_code=request.details.destination.postal_code,
                    region=request.details.destination.region
                )
            )
        )
        response_0 = await deps.clients.anomalies_anomaly_validation.ScoreAnomaly(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.breakdown.currency_code
        if returned_0_0:
            response.breakdown.currency_code = returned_0_0
        echoed_0 = request.anomaly_feedback_id
        response.anomaly_feedback.anomaly_feedback_id = echoed_0
        echoed_1 = request.anomaly_feedback.kind
        response.anomaly_feedback.kind = echoed_1
        return response


async def handle_compare_anomaly_feedback_options(
    deps: Dependencies,
    request: anomalies_v1_anomaly_feedback_calculation_service_pb2.CompareAnomalyFeedbackOptionsRequest
) -> anomalies_v1_anomaly_feedback_calculation_service_pb2.CompareAnomalyFeedbackOptionsResponse:
    """Compares an anomaly feedback."""
    response = anomalies_v1_anomaly_feedback_calculation_service_pb2.CompareAnomalyFeedbackOptionsResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('CompareAnomalyFeedbackOptions', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(
            request.context.tenant_id,
            'CompareAnomalyFeedbackOptions',
            {'reason': request.reason}
        )
        await deps.repository.save_anomaly_feedback(request.context.tenant_id, request.anomaly_feedback)
        response_0 = lineage_v1_impact_calculation_service_pb2.CalculateImpactResponse()
        response_1 = anomalies_v1_anomaly_validation_service_pb2.ScoreAnomalyResponse()
        outgoing_0 = lineage_v1_impact_calculation_service_pb2.CalculateImpactRequest(
            context=request.context,
            impact=lineage_v1_lineage_pb2.Impact(
                customer=customers_v1_refs_pb2.CustomerRef(display_name=request.anomaly_feedback.subject.display_name)
            )
        )
        response_0 = await deps.clients.lineage_impact_calculation.CalculateImpact(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = anomalies_v1_anomaly_validation_service_pb2.ScoreAnomalyRequest(
            context=request.context,
            details=anomalies_v1_anomaly_validation_service_pb2.ScoreAnomalyRequest.Details(
                destination=common_v1_address_pb2.PostalAddress(lines=list(request.details.destination.lines))
            )
        )
        method_name_1 = 'ScoreAnomaly'
        response_1 = await getattr(
            deps.clients.anomalies_anomaly_validation,
            method_name_1
        )(outgoing_1, timeout=deps.settings.timeout)
        returned_0_0 = response_0.impact.assignee.display_name
        if returned_0_0:
            response.anomaly_feedback.subject.display_name = returned_0_0
        returned_0_1 = response_0.result.message
        if returned_0_1:
            response.result.message = returned_0_1
        returned_1_0 = response_1.result.reference_ids
        response.result.reference_ids.extend(returned_1_0)
        echoed_0 = request.anomaly_feedback_id
        response.anomaly_feedback.anomaly_feedback_id = echoed_0
        echoed_1 = request.anomaly_feedback.attributes
        response.anomaly_feedback.attributes.update(echoed_1)
        return response


async def handle_estimate_anomaly_feedback(
    deps: Dependencies,
    request: anomalies_v1_anomaly_feedback_calculation_service_pb2.EstimateAnomalyFeedbackRequest
) -> anomalies_v1_anomaly_feedback_calculation_service_pb2.EstimateAnomalyFeedbackResponse:
    """Estimates an anomaly feedback."""
    response = anomalies_v1_anomaly_feedback_calculation_service_pb2.EstimateAnomalyFeedbackResponse()
    with tenant_scope(request.context.tenant_id):
        log.info(
            'EstimateAnomalyFeedback',
            extra={'fields': {'anomaly_feedback_id': request.anomaly_feedback.anomaly_feedback_id}}
        )
        await deps.repository.audit(
            request.context.tenant_id,
            'EstimateAnomalyFeedback',
            {'anomaly_feedback_id': request.anomaly_feedback.anomaly_feedback_id}
        )
        await deps.repository.save_anomaly_feedback(request.context.tenant_id, request.anomaly_feedback)
        response_0 = anomalies_v1_anomaly_validation_service_pb2.NormalizeAnomalyResponse()
        outgoing_0 = anomalies_v1_anomaly_validation_service_pb2.NormalizeAnomalyRequest(
            anomaly=anomalies_v1_anomalies_pb2.Anomaly(
                assignee=identity_v1_refs_pb2.UserRef(
                    display_name=request.anomaly_feedback.subject.display_name,
                    email=request.context.actor.email
                )
            ),
            context=request.context,
            reason=request.reason
        )
        response_0 = await deps.clients.anomalies_anomaly_validation.NormalizeAnomaly(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.result.correlation_id
        if returned_0_0:
            response.result.correlation_id = returned_0_0
        echoed_0 = request.anomaly_feedback_id
        response.anomaly_feedback.anomaly_feedback_id = echoed_0
        echoed_1 = request.anomaly_feedback.correlation_id
        response.anomaly_feedback.correlation_id = echoed_1
        return response


async def handle_explain_anomaly_feedback_calculation(
    deps: Dependencies,
    request: anomalies_v1_anomaly_feedback_calculation_service_pb2.ExplainAnomalyFeedbackCalculationRequest
) -> anomalies_v1_anomaly_feedback_calculation_service_pb2.ExplainAnomalyFeedbackCalculationResponse:
    """Explains an anomaly feedback."""
    response = anomalies_v1_anomaly_feedback_calculation_service_pb2.ExplainAnomalyFeedbackCalculationResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('ExplainAnomalyFeedbackCalculation', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(
            request.context.tenant_id,
            'ExplainAnomalyFeedbackCalculation',
            {'reason': request.reason}
        )
        await deps.repository.save_anomaly_feedback(request.context.tenant_id, request.anomaly_feedback)
        response_0 = anomalies_v1_anomaly_validation_service_pb2.ExplainAnomalyDecisionResponse()
        response_1 = metrics_v1_metric_alert_validation_service_pb2.ScoreMetricAlertResponse()
        outgoing_0 = anomalies_v1_anomaly_validation_service_pb2.ExplainAnomalyDecisionRequest(
            anomaly=anomalies_v1_anomalies_pb2.Anomaly(
                assignee=identity_v1_refs_pb2.UserRef(email=request.details.contact.email),
                requester=common_v1_contact_pb2.ContactInfo(
                    name=request.details.contact.name,
                    phone=request.details.contact.phone
                )
            ),
            context=request.context
        )
        response_0 = await deps.clients.anomalies_anomaly_validation.ExplainAnomalyDecision(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = metrics_v1_metric_alert_validation_service_pb2.ScoreMetricAlertRequest(
            context=request.context,
            metric_alert=metrics_v1_metrics_pb2.MetricAlert(
                owner=identity_v1_refs_pb2.UserRef(display_name=response_0.anomaly.assignee.display_name)
            )
        )
        document_1 = MessageToJson(outgoing_1, preserving_proto_field_name=True)
        outgoing_1 = Parse(document_1, metrics_v1_metric_alert_validation_service_pb2.ScoreMetricAlertRequest())
        response_1 = await deps.clients.metrics_metric_alert_validation.ScoreMetricAlert(
            outgoing_1,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.outcome.message
        if returned_0_0:
            response.outcome.message = returned_0_0
        returned_1_0 = response_1.result.message
        if returned_1_0:
            response.result.message = returned_1_0
        returned_1_1 = response_1.result.details
        response.result.details.update(returned_1_1)
        echoed_0 = request.anomaly_feedback_id
        response.anomaly_feedback.anomaly_feedback_id = echoed_0
        echoed_1 = request.anomaly_feedback.correlation_id
        response.result.correlation_id = echoed_1
        return response


async def handle_get_anomaly_feedback_rates(
    deps: Dependencies,
    request: anomalies_v1_anomaly_feedback_calculation_service_pb2.GetAnomalyFeedbackRatesRequest
) -> anomalies_v1_anomaly_feedback_calculation_service_pb2.GetAnomalyFeedbackRatesResponse:
    """Returns an anomaly feedback."""
    response = anomalies_v1_anomaly_feedback_calculation_service_pb2.GetAnomalyFeedbackRatesResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('GetAnomalyFeedbackRates', extra={'fields': {'domain': 'anomalies'}})
        await deps.repository.audit(request.context.tenant_id, 'GetAnomalyFeedbackRates', {})
        response_0 = metrics_v1_metric_alert_validation_service_pb2.PreviewMetricAlertResponse()
        response_1 = careplans_v1_care_plan_query_service_pb2.ResolveCarePlansResponse()
        outgoing_0 = metrics_v1_metric_alert_validation_service_pb2.PreviewMetricAlertRequest(
            context=request.context,
            metric_alert=metrics_v1_metrics_pb2.MetricAlert(
                owner=identity_v1_refs_pb2.UserRef(email=request.context.actor.email)
            )
        )
        response_0 = await deps.clients.metrics_metric_alert_validation.PreviewMetricAlert(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = careplans_v1_care_plan_query_service_pb2.ResolveCarePlansRequest(context=request.context)
        envelope_1 = AnyMessage()
        envelope_1.Pack(outgoing_1)
        outgoing_1 = careplans_v1_care_plan_query_service_pb2.ResolveCarePlansRequest()
        if not envelope_1.Unpack(outgoing_1):
            raise ValueError("partner envelope contains the wrong request type")
        response_1 = await deps.clients.careplans_care_plan_query.ResolveCarePlans(
            outgoing_1,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.outcome.message
        if returned_0_0:
            response.result.message = returned_0_0
        returned_0_1 = response_0.result.status
        if returned_0_1:
            response.result.status = returned_0_1
        returned_1_0 = response_1.result.details
        response.result.details.update(returned_1_0)
        echoed_0 = request.anomaly_feedback_id
        response.anomaly_feedback.anomaly_feedback_id = echoed_0
        return response


async def handle_quote_anomaly_feedback(
    deps: Dependencies,
    request: anomalies_v1_anomaly_feedback_calculation_service_pb2.QuoteAnomalyFeedbackRequest
) -> anomalies_v1_anomaly_feedback_calculation_service_pb2.QuoteAnomalyFeedbackResponse:
    """Quotes an anomaly feedback."""
    response = anomalies_v1_anomaly_feedback_calculation_service_pb2.QuoteAnomalyFeedbackResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('QuoteAnomalyFeedback', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'QuoteAnomalyFeedback', {'reason': request.reason})
        await deps.repository.save_anomaly_feedback(request.context.tenant_id, request.anomaly_feedback)
        response_0 = anomalies_v1_anomaly_validation_service_pb2.LintAnomaliesResponse()
        response_1 = lineage_v1_lineage_edge_validation_service_pb2.ExplainLineageEdgeDecisionResponse()
        response_2 = anomalies_v1_anomaly_validation_service_pb2.CheckAnomalyEligibilityResponse()
        response_3 = lineage_v1_impact_calculation_service_pb2.RecalculateImpactsResponse()
        async for item_0 in async_messages(request.anomaly_feedback.measurements):
            outgoing_0 = anomalies_v1_anomaly_validation_service_pb2.LintAnomaliesRequest(
                annotations=dict(request.annotations),
                anomaly=anomalies_v1_anomalies_pb2.Anomaly(
                    audit=common_v1_audit_pb2.AuditInfo(updated_at=item_0.observed_at),
                    customer=anomalies_v1_refs_pb2.DetectorRef(
                        display_name=request.anomaly_feedback.subject.display_name
                    )
                ),
                context=request.context
            )
            response_0 = await deps.clients.anomalies_anomaly_validation.LintAnomalies(
                outgoing_0,
                timeout=deps.settings.timeout
            )
        for item_1 in request.anomaly_feedback.measurements:
            outgoing_1 = lineage_v1_lineage_edge_validation_service_pb2.ExplainLineageEdgeDecisionRequest(
                context=request.context,
                lineage_edge=lineage_v1_lineage_pb2.LineageEdge(
                    measurements=[
                        lineage_v1_lineage_pb2.LineageEdgeMeasurement(
                            metric=item_1.metric,
                            observed_at=item_1.observed_at,
                            value=item_1.value
                        )
                    ]
                )
            )
            response_1 = await deps.clients.lineage_lineage_edge_validation.ExplainLineageEdgeDecision(
                outgoing_1,
                timeout=deps.settings.timeout
            )
        command_2 = AnomalyFeedbackCalculationQuoteAnomalyFeedback2Command.model_validate(
            {'context': request.context, 'anomaly_comments_created_at': response_0.anomaly.audit.created_at}
        )
        outgoing_2 = to_anomaly_feedback_calculation_quote_anomaly_feedback2_command(command_2)
        response_2 = await deps.clients.anomalies_anomaly_validation.CheckAnomalyEligibility(
            outgoing_2,
            timeout=deps.settings.timeout
        )
        outgoing_3 = lineage_v1_impact_calculation_service_pb2.RecalculateImpactsRequest(
            context=request.context,
            impact=lineage_v1_lineage_pb2.Impact(
                customer=customers_v1_refs_pb2.CustomerRef(email=response_2.anomaly.assignee.email),
                sla=lineage_v1_lineage_pb2.ImpactSla(paused_for=response_2.anomaly.sla.paused_for)
            )
        )
        send_3 = partial(deps.clients.lineage_impact_calculation.RecalculateImpacts, timeout=deps.settings.timeout)
        response_3 = await send_3(outgoing_3)
        returned_2_0 = response_2.anomaly.customer.display_name
        if returned_2_0:
            response.anomaly_feedback.subject.display_name = returned_2_0
        returned_2_1 = response_2.result.reference_ids
        response.result.reference_ids.extend(returned_2_1)
        returned_3_0 = response_3.breakdown.currency_code
        if returned_3_0:
            response.breakdown.currency_code = returned_3_0
        returned_3_1 = response_3.breakdown.total
        if returned_3_1.ListFields():
            response.breakdown.total.MergeFrom(returned_3_1)
        echoed_0 = request.anomaly_feedback_id
        response.anomaly_feedback.anomaly_feedback_id = echoed_0
        echoed_1 = request.anomaly_feedback.correlation_id
        response.anomaly_feedback.correlation_id = echoed_1
        return response


async def handle_recalculate_anomaly_feedbacks(
    deps: Dependencies,
    request: anomalies_v1_anomaly_feedback_calculation_service_pb2.RecalculateAnomalyFeedbacksRequest
) -> anomalies_v1_anomaly_feedback_calculation_service_pb2.RecalculateAnomalyFeedbacksResponse:
    """Recalculates an anomaly feedback."""
    response = anomalies_v1_anomaly_feedback_calculation_service_pb2.RecalculateAnomalyFeedbacksResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('RecalculateAnomalyFeedbacks', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(
            request.context.tenant_id,
            'RecalculateAnomalyFeedbacks',
            {'reason': request.reason}
        )
        await deps.repository.save_anomaly_feedback(request.context.tenant_id, request.anomaly_feedback)
        response_0 = ledger_v1_ledger_account_validation_service_pb2.LintLedgerAccountsResponse()
        requests_0: list[ledger_v1_ledger_account_validation_service_pb2.LintLedgerAccountsRequest] = []
        for item_0 in request.anomaly_feedback.measurements:
            outgoing_0 = ledger_v1_ledger_account_validation_service_pb2.LintLedgerAccountsRequest(
                context=request.context,
                ledger_account=ledger_v1_ledger_pb2.LedgerAccount(
                    audit=common_v1_audit_pb2.AuditInfo(created_at=item_0.observed_at)
                )
            )
            requests_0.append(outgoing_0)
        replies_0 = await asyncio.gather(*(
            deps.clients.ledger_ledger_account_validation.LintLedgerAccounts(
                entry,
                timeout=deps.settings.timeout
            ) for entry in requests_0
        ))
        if replies_0:
            response_0 = replies_0[-1]
        echoed_0 = request.anomaly_feedback_id
        response.anomaly_feedback.anomaly_feedback_id = echoed_0
        echoed_1 = request.anomaly_feedback.correlation_id
        response.anomaly_feedback.correlation_id = echoed_1
        return response


async def handle_simulate_anomaly_feedback(
    deps: Dependencies,
    request: anomalies_v1_anomaly_feedback_calculation_service_pb2.SimulateAnomalyFeedbackRequest
) -> anomalies_v1_anomaly_feedback_calculation_service_pb2.SimulateAnomalyFeedbackResponse:
    """Simulates an anomaly feedback."""
    response = anomalies_v1_anomaly_feedback_calculation_service_pb2.SimulateAnomalyFeedbackResponse()
    with tenant_scope(request.context.tenant_id):
        log.info(
            'SimulateAnomalyFeedback',
            extra={'fields': {'anomaly_feedback_id': request.anomaly_feedback.anomaly_feedback_id}}
        )
        await deps.repository.audit(
            request.context.tenant_id,
            'SimulateAnomalyFeedback',
            {'anomaly_feedback_id': request.anomaly_feedback.anomaly_feedback_id}
        )
        await deps.repository.save_anomaly_feedback(request.context.tenant_id, request.anomaly_feedback)
        response_0 = anomalies_v1_anomaly_validation_service_pb2.CheckAnomalyEligibilityResponse()
        response_1 = lineage_v1_lineage_edge_validation_service_pb2.CheckLineageEdgeEligibilityResponse()
        response_2 = identity_v1_user_query_service_pb2.LookupUserResponse()
        outgoing_0 = anomalies_v1_anomaly_validation_service_pb2.CheckAnomalyEligibilityRequest(
            anomaly=anomalies_v1_anomalies_pb2.Anomaly(
                customer=anomalies_v1_refs_pb2.DetectorRef(display_name=request.anomaly_feedback.subject.display_name)
            ),
            context=request.context,
            details=anomalies_v1_anomaly_validation_service_pb2.CheckAnomalyEligibilityRequest.Details(
                contact=common_v1_contact_pb2.ContactInfo(email=request.context.actor.email)
            ),
            reason=request.reason
        )
        response_0 = await deps.clients.anomalies_anomaly_validation.CheckAnomalyEligibility(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = lineage_v1_lineage_edge_validation_service_pb2.CheckLineageEdgeEligibilityRequest(
            context=request.context,
            lineage_edge=lineage_v1_lineage_pb2.LineageEdge(
                subject=lineage_v1_refs_pb2.ImpactRef(display_name=request.anomaly_feedback.subject.display_name)
            )
        )
        port_1: AnomalyFeedbackCalculationSimulateAnomalyFeedback1Port = AnomalyFeedbackCalculationSimulateAnomalyFeedback1Adapter(
            deps.clients.lineage_lineage_edge_validation,
            deps.settings.timeout
        )
        response_1 = await port_1.execute(outgoing_1)
        outgoing_2 = identity_v1_user_query_service_pb2.LookupUserRequest(
            context=request.context,
            user_id=request.context.actor.user_id
        )
        steps_2 = [partial(deps.clients.identity_user_query.LookupUser, outgoing_2, timeout=deps.settings.timeout)]
        results_2 = await run_steps(steps_2)
        response_2 = results_2[-1]
        returned_0_0 = response_0.result.message
        if returned_0_0:
            response.result.message = returned_0_0
        returned_1_0 = response_1.lineage_edge.source
        if returned_1_0:
            response.anomaly_feedback.source = returned_1_0
        returned_2_0 = response_2.result.correlation_id
        if returned_2_0:
            response.anomaly_feedback.correlation_id = returned_2_0
        returned_2_1 = response_2.result.details
        response.result.details.update(returned_2_1)
        echoed_0 = request.anomaly_feedback_id
        response.anomaly_feedback.anomaly_feedback_id = echoed_0
        echoed_1 = request.anomaly_feedback.sequence
        response.anomaly_feedback.sequence = echoed_1
        return response
