"""Background event handlers owned by the recommendations team."""

from __future__ import annotations

from functools import partial
from typing import cast

from google.protobuf.message import Message

from acme.appointments.v1 import appointment_query_service_pb2 as appointments_v1_appointment_query_service_pb2
from acme.customers.v1 import (
    customer_segment_calculation_service_pb2 as customers_v1_customer_segment_calculation_service_pb2,
)
from acme.customers.v1 import household_calculation_service_pb2 as customers_v1_household_calculation_service_pb2
from acme.ledger.v1 import ledger_account_service_pb2 as ledger_v1_ledger_account_service_pb2
from acme.metrics.v1 import metric_alert_validation_service_pb2 as metrics_v1_metric_alert_validation_service_pb2
from acme.recommendations.v1 import (
    interaction_validation_service_pb2 as recommendations_v1_interaction_validation_service_pb2,
)
from acme.recommendations.v1 import (
    recommendation_model_calculation_service_pb2 as recommendations_v1_recommendation_model_calculation_service_pb2,
)
from acme.recommendations.v1 import (
    recommendation_model_query_service_pb2 as recommendations_v1_recommendation_model_query_service_pb2,
)
from acme.recommendations.v1 import (
    recommendation_set_approval_service_pb2 as recommendations_v1_recommendation_set_approval_service_pb2,
)

from acme_data.domains.recommendations.dependencies import Dependencies


async def on_interaction_calculation_service_recalculate_interactions_2(
    deps: Dependencies,
    payload: Message
) -> Message:
    request = cast(
        recommendations_v1_recommendation_model_calculation_service_pb2.CalculateRecommendationModelRequest,
        payload
    )
    return await deps.clients.recommendations_recommendation_model_calculation.CalculateRecommendationModel(
        request,
        timeout=deps.settings.timeout
    )


async def on_interaction_lifecycle_service_reinstate_interaction_2(deps: Dependencies, payload: Message) -> Message:
    request = cast(customers_v1_household_calculation_service_pb2.SimulateHouseholdRequest, payload)
    return await deps.clients.customers_household_calculation.SimulateHousehold(request, timeout=deps.settings.timeout)


async def on_interaction_validation_service_preview_interaction_2(deps: Dependencies, payload: Message) -> Message:
    request = cast(appointments_v1_appointment_query_service_pb2.SuggestAppointmentsRequest, payload)
    return await deps.clients.appointments_appointment_query.SuggestAppointments(request, timeout=deps.settings.timeout)


async def on_interaction_workflow_service_signal_interaction_workflow_2(
    deps: Dependencies,
    payload: Message
) -> Message:
    request = cast(customers_v1_customer_segment_calculation_service_pb2.SimulateCustomerSegmentRequest, payload)
    return await deps.clients.customers_customer_segment_calculation.SimulateCustomerSegment(
        request,
        timeout=deps.settings.timeout
    )


async def on_recommendation_model_calculation_service_quote_recommendation_model_0(
    deps: Dependencies,
    payload: Message
) -> Message:
    request = cast(metrics_v1_metric_alert_validation_service_pb2.ScoreMetricAlertRequest, payload)
    return await deps.clients.metrics_metric_alert_validation.ScoreMetricAlert(request, timeout=deps.settings.timeout)


async def on_recommendation_model_workflow_service_cancel_recommendation_model_workflow_1(
    deps: Dependencies,
    payload: Message
) -> Message:
    request = cast(
        recommendations_v1_recommendation_set_approval_service_pb2.ListPendingRecommendationSetsRequest,
        payload
    )
    return await deps.clients.recommendations_recommendation_set_approval.ListPendingRecommendationSets(
        request,
        timeout=deps.settings.timeout
    )


async def on_recommendation_model_workflow_service_start_recommendation_model_workflow_1(
    deps: Dependencies,
    payload: Message
) -> Message:
    request = cast(recommendations_v1_interaction_validation_service_pb2.ValidateInteractionRequest, payload)
    return await deps.clients.recommendations_interaction_validation.ValidateInteraction(
        request,
        timeout=deps.settings.timeout
    )


async def on_recommendation_set_approval_service_submit_recommendation_set_2(
    deps: Dependencies,
    payload: Message
) -> Message:
    request = cast(recommendations_v1_recommendation_model_query_service_pb2.FindRecommendationModelsRequest, payload)
    return await deps.clients.recommendations_recommendation_model_query.FindRecommendationModels(
        request,
        timeout=deps.settings.timeout
    )


async def on_recommendation_set_validation_service_preview_recommendation_set_1(
    deps: Dependencies,
    payload: Message
) -> Message:
    request = cast(
        recommendations_v1_recommendation_model_calculation_service_pb2.CompareRecommendationModelOptionsRequest,
        payload
    )
    return await deps.clients.recommendations_recommendation_model_calculation.CompareRecommendationModelOptions(
        request,
        timeout=deps.settings.timeout
    )


async def on_recommendation_set_workflow_service_signal_recommendation_set_workflow_2(
    deps: Dependencies,
    payload: Message
) -> Message:
    request = cast(ledger_v1_ledger_account_service_pb2.CloneLedgerAccountRequest, payload)
    return await deps.clients.ledger_ledger_account.CloneLedgerAccount(request, timeout=deps.settings.timeout)


def subscribe(deps: Dependencies) -> None:
    deps.bus.subscribe(
        'acme.recommendations.v1.InteractionCalculationService/RecalculateInteractions/2',
        partial(on_interaction_calculation_service_recalculate_interactions_2, deps)
    )
    deps.bus.subscribe(
        'acme.recommendations.v1.InteractionLifecycleService/ReinstateInteraction/2',
        partial(on_interaction_lifecycle_service_reinstate_interaction_2, deps)
    )
    deps.bus.subscribe(
        'acme.recommendations.v1.InteractionValidationService/PreviewInteraction/2',
        partial(on_interaction_validation_service_preview_interaction_2, deps)
    )
    deps.bus.subscribe(
        'acme.recommendations.v1.InteractionWorkflowService/SignalInteractionWorkflow/2',
        partial(on_interaction_workflow_service_signal_interaction_workflow_2, deps)
    )
    deps.bus.subscribe(
        'acme.recommendations.v1.RecommendationModelCalculationService/QuoteRecommendationModel/0',
        partial(on_recommendation_model_calculation_service_quote_recommendation_model_0, deps)
    )
    deps.bus.subscribe(
        'acme.recommendations.v1.RecommendationModelWorkflowService/CancelRecommendationModelWorkflow/1',
        partial(on_recommendation_model_workflow_service_cancel_recommendation_model_workflow_1, deps)
    )
    deps.bus.subscribe(
        'acme.recommendations.v1.RecommendationModelWorkflowService/StartRecommendationModelWorkflow/1',
        partial(on_recommendation_model_workflow_service_start_recommendation_model_workflow_1, deps)
    )
    deps.bus.subscribe(
        'acme.recommendations.v1.RecommendationSetApprovalService/SubmitRecommendationSet/2',
        partial(on_recommendation_set_approval_service_submit_recommendation_set_2, deps)
    )
    deps.bus.subscribe(
        'acme.recommendations.v1.RecommendationSetValidationService/PreviewRecommendationSet/1',
        partial(on_recommendation_set_validation_service_preview_recommendation_set_1, deps)
    )
    deps.bus.subscribe(
        'acme.recommendations.v1.RecommendationSetWorkflowService/SignalRecommendationSetWorkflow/2',
        partial(on_recommendation_set_workflow_service_signal_recommendation_set_workflow_2, deps)
    )
