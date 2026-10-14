"""Background event handlers owned by the analytics team."""

from __future__ import annotations

from functools import partial
from typing import cast

from google.protobuf.message import Message

from acme.analytics.v1 import analytics_event_query_service_pb2 as analytics_v1_analytics_event_query_service_pb2
from acme.anomalies.v1 import detector_query_service_pb2 as anomalies_v1_detector_query_service_pb2
from acme.audit.v1 import audit_event_query_service_pb2 as audit_v1_audit_event_query_service_pb2
from acme.customers.v1 import household_validation_service_pb2 as customers_v1_household_validation_service_pb2
from acme.customers.v1 import preference_calculation_service_pb2 as customers_v1_preference_calculation_service_pb2
from acme.datasets.v1 import data_schema_calculation_service_pb2 as datasets_v1_data_schema_calculation_service_pb2
from acme.featureflags.v1 import feature_flag_service_pb2 as featureflags_v1_feature_flag_service_pb2
from acme.forecasting.v1 import (
    forecast_model_workflow_service_pb2 as forecasting_v1_forecast_model_workflow_service_pb2,
)
from acme.identity.v1 import user_validation_service_pb2 as identity_v1_user_validation_service_pb2
from acme.treasury.v1 import cash_position_service_pb2 as treasury_v1_cash_position_service_pb2

from acme_data.domains.analytics.dependencies import Dependencies


async def on_analytics_event_validation_service_lint_analytics_events_2(
    deps: Dependencies,
    payload: Message
) -> Message:
    request = cast(anomalies_v1_detector_query_service_pb2.FindDetectorsRequest, payload)
    return await deps.clients.anomalies_detector_query.FindDetectors(request, timeout=deps.settings.timeout)


async def on_analytics_event_workflow_service_retry_analytics_event_workflow_0(
    deps: Dependencies,
    payload: Message
) -> Message:
    request = cast(treasury_v1_cash_position_service_pb2.UpdateCashPositionRequest, payload)
    return await deps.clients.treasury_cash_position.UpdateCashPosition(request, timeout=deps.settings.timeout)


async def on_analytics_report_approval_service_escalate_analytics_report_0(
    deps: Dependencies,
    payload: Message
) -> Message:
    request = cast(audit_v1_audit_event_query_service_pb2.CountAuditEventsRequest, payload)
    return await deps.clients.audit_audit_event_query.CountAuditEvents(request, timeout=deps.settings.timeout)


async def on_analytics_report_calculation_service_estimate_analytics_report_0(
    deps: Dependencies,
    payload: Message
) -> Message:
    request = cast(featureflags_v1_feature_flag_service_pb2.BatchGetFeatureFlagsRequest, payload)
    return await deps.clients.featureflags_feature_flag.BatchGetFeatureFlags(request, timeout=deps.settings.timeout)


async def on_analytics_report_lifecycle_service_renew_analytics_report_1(
    deps: Dependencies,
    payload: Message
) -> Message:
    request = cast(customers_v1_household_validation_service_pb2.ValidateHouseholdRequest, payload)
    return await deps.clients.customers_household_validation.ValidateHousehold(request, timeout=deps.settings.timeout)


async def on_analytics_report_validation_service_preview_analytics_report_2(
    deps: Dependencies,
    payload: Message
) -> Message:
    request = cast(identity_v1_user_validation_service_pb2.ExplainUserDecisionRequest, payload)
    return await deps.clients.identity_user_validation.ExplainUserDecision(request, timeout=deps.settings.timeout)


async def on_cohort_calculation_service_quote_cohort_1(deps: Dependencies, payload: Message) -> Message:
    request = cast(datasets_v1_data_schema_calculation_service_pb2.CompareDataSchemaOptionsRequest, payload)
    return await deps.clients.datasets_data_schema_calculation.CompareDataSchemaOptions(
        request,
        timeout=deps.settings.timeout
    )


async def on_cohort_lifecycle_service_terminate_cohort_0(deps: Dependencies, payload: Message) -> Message:
    request = cast(analytics_v1_analytics_event_query_service_pb2.ResolveAnalyticsEventsRequest, payload)
    return await deps.clients.analytics_analytics_event_query.ResolveAnalyticsEvents(
        request,
        timeout=deps.settings.timeout
    )


async def on_funnel_approval_service_delegate_funnel_approval_0(deps: Dependencies, payload: Message) -> Message:
    request = cast(forecasting_v1_forecast_model_workflow_service_pb2.SignalForecastModelWorkflowRequest, payload)
    return await deps.clients.forecasting_forecast_model_workflow.SignalForecastModelWorkflow(
        request,
        timeout=deps.settings.timeout
    )


async def on_funnel_workflow_service_advance_funnel_workflow_0(deps: Dependencies, payload: Message) -> Message:
    request = cast(customers_v1_preference_calculation_service_pb2.EstimatePreferenceRequest, payload)
    return await deps.clients.customers_preference_calculation.EstimatePreference(
        request,
        timeout=deps.settings.timeout
    )


def subscribe(deps: Dependencies) -> None:
    deps.bus.subscribe(
        'acme.analytics.v1.AnalyticsEventValidationService/LintAnalyticsEvents/2',
        partial(on_analytics_event_validation_service_lint_analytics_events_2, deps)
    )
    deps.bus.subscribe(
        'acme.analytics.v1.AnalyticsEventWorkflowService/RetryAnalyticsEventWorkflow/0',
        partial(on_analytics_event_workflow_service_retry_analytics_event_workflow_0, deps)
    )
    deps.bus.subscribe(
        'acme.analytics.v1.AnalyticsReportApprovalService/EscalateAnalyticsReport/0',
        partial(on_analytics_report_approval_service_escalate_analytics_report_0, deps)
    )
    deps.bus.subscribe(
        'acme.analytics.v1.AnalyticsReportCalculationService/EstimateAnalyticsReport/0',
        partial(on_analytics_report_calculation_service_estimate_analytics_report_0, deps)
    )
    deps.bus.subscribe(
        'acme.analytics.v1.AnalyticsReportLifecycleService/RenewAnalyticsReport/1',
        partial(on_analytics_report_lifecycle_service_renew_analytics_report_1, deps)
    )
    deps.bus.subscribe(
        'acme.analytics.v1.AnalyticsReportValidationService/PreviewAnalyticsReport/2',
        partial(on_analytics_report_validation_service_preview_analytics_report_2, deps)
    )
    deps.bus.subscribe(
        'acme.analytics.v1.CohortCalculationService/QuoteCohort/1',
        partial(on_cohort_calculation_service_quote_cohort_1, deps)
    )
    deps.bus.subscribe(
        'acme.analytics.v1.CohortLifecycleService/TerminateCohort/0',
        partial(on_cohort_lifecycle_service_terminate_cohort_0, deps)
    )
    deps.bus.subscribe(
        'acme.analytics.v1.FunnelApprovalService/DelegateFunnelApproval/0',
        partial(on_funnel_approval_service_delegate_funnel_approval_0, deps)
    )
    deps.bus.subscribe(
        'acme.analytics.v1.FunnelWorkflowService/AdvanceFunnelWorkflow/0',
        partial(on_funnel_workflow_service_advance_funnel_workflow_0, deps)
    )
