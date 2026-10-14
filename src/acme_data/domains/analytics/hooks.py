"""Replaceable partner hooks of the analytics domain."""

from __future__ import annotations

from acme.analytics.v1 import analytics_event_query_service_pb2 as analytics_v1_analytics_event_query_service_pb2
from acme.analytics.v1 import (
    analytics_event_query_service_pb2_grpc as analytics_v1_analytics_event_query_service_pb2_grpc,
)
from acme.analytics.v1 import analytics_event_workflow_service_pb2 as analytics_v1_analytics_event_workflow_service_pb2
from acme.analytics.v1 import (
    analytics_event_workflow_service_pb2_grpc as analytics_v1_analytics_event_workflow_service_pb2_grpc,
)
from acme.analytics.v1 import (
    analytics_report_calculation_service_pb2 as analytics_v1_analytics_report_calculation_service_pb2,
)
from acme.analytics.v1 import (
    analytics_report_calculation_service_pb2_grpc as analytics_v1_analytics_report_calculation_service_pb2_grpc,
)
from acme.analytics.v1 import funnel_calculation_service_pb2 as analytics_v1_funnel_calculation_service_pb2
from acme.analytics.v1 import funnel_calculation_service_pb2_grpc as analytics_v1_funnel_calculation_service_pb2_grpc
from acme.anomalies.v1 import (
    anomaly_feedback_approval_service_pb2 as anomalies_v1_anomaly_feedback_approval_service_pb2,
)
from acme.anomalies.v1 import (
    anomaly_feedback_approval_service_pb2_grpc as anomalies_v1_anomaly_feedback_approval_service_pb2_grpc,
)
from acme.checkout.v1 import checkout_session_query_service_pb2 as checkout_v1_checkout_session_query_service_pb2
from acme.checkout.v1 import (
    checkout_session_query_service_pb2_grpc as checkout_v1_checkout_session_query_service_pb2_grpc,
)
from acme.customers.v1 import (
    customer_segment_validation_service_pb2 as customers_v1_customer_segment_validation_service_pb2,
)
from acme.customers.v1 import (
    customer_segment_validation_service_pb2_grpc as customers_v1_customer_segment_validation_service_pb2_grpc,
)
from acme.customers.v1 import preference_calculation_service_pb2 as customers_v1_preference_calculation_service_pb2
from acme.customers.v1 import (
    preference_calculation_service_pb2_grpc as customers_v1_preference_calculation_service_pb2_grpc,
)
from acme.ledger.v1 import ledger_account_validation_service_pb2 as ledger_v1_ledger_account_validation_service_pb2
from acme.ledger.v1 import (
    ledger_account_validation_service_pb2_grpc as ledger_v1_ledger_account_validation_service_pb2_grpc,
)
from acme.metrics.v1 import metric_alert_query_service_pb2 as metrics_v1_metric_alert_query_service_pb2
from acme.metrics.v1 import metric_alert_query_service_pb2_grpc as metrics_v1_metric_alert_query_service_pb2_grpc
from acme.metrics.v1 import metric_alert_validation_service_pb2 as metrics_v1_metric_alert_validation_service_pb2
from acme.metrics.v1 import (
    metric_alert_validation_service_pb2_grpc as metrics_v1_metric_alert_validation_service_pb2_grpc,
)


async def analytics_event_approval_recall_analytics_event1(
    client: analytics_v1_analytics_report_calculation_service_pb2_grpc.AnalyticsReportCalculationServiceStub,
    request: analytics_v1_analytics_report_calculation_service_pb2.CompareAnalyticsReportOptionsRequest,
    timeout: float
) -> analytics_v1_analytics_report_calculation_service_pb2.CompareAnalyticsReportOptionsResponse:
    raise RuntimeError("domain hook was not installed")


async def analytics_event_batch_create_analytics_events1(
    client: analytics_v1_funnel_calculation_service_pb2_grpc.FunnelCalculationServiceStub,
    request: analytics_v1_funnel_calculation_service_pb2.EstimateFunnelRequest,
    timeout: float
) -> analytics_v1_funnel_calculation_service_pb2.EstimateFunnelResponse:
    raise RuntimeError("domain hook was not installed")


async def analytics_event_watch_analytics_events1(
    client: metrics_v1_metric_alert_validation_service_pb2_grpc.MetricAlertValidationServiceStub,
    request: metrics_v1_metric_alert_validation_service_pb2.ExplainMetricAlertDecisionRequest,
    timeout: float
) -> metrics_v1_metric_alert_validation_service_pb2.ExplainMetricAlertDecisionResponse:
    raise RuntimeError("domain hook was not installed")


async def analytics_report_approval_comment_analytics_report_approval2(
    client: customers_v1_preference_calculation_service_pb2_grpc.PreferenceCalculationServiceStub,
    request: customers_v1_preference_calculation_service_pb2.QuotePreferenceRequest,
    timeout: float
) -> customers_v1_preference_calculation_service_pb2.QuotePreferenceResponse:
    raise RuntimeError("domain hook was not installed")


async def analytics_report_lifecycle_expire_analytics_report2(
    client: analytics_v1_analytics_event_query_service_pb2_grpc.AnalyticsEventQueryServiceStub,
    request: analytics_v1_analytics_event_query_service_pb2.FindAnalyticsEventsRequest,
    timeout: float
) -> analytics_v1_analytics_event_query_service_pb2.FindAnalyticsEventsResponse:
    raise RuntimeError("domain hook was not installed")


async def analytics_report_validation_normalize_analytics_report0(
    client: ledger_v1_ledger_account_validation_service_pb2_grpc.LedgerAccountValidationServiceStub,
    request: ledger_v1_ledger_account_validation_service_pb2.PreviewLedgerAccountRequest,
    timeout: float
) -> ledger_v1_ledger_account_validation_service_pb2.PreviewLedgerAccountResponse:
    raise RuntimeError("domain hook was not installed")


async def cohort_approval_escalate_cohort0(
    client: customers_v1_customer_segment_validation_service_pb2_grpc.CustomerSegmentValidationServiceStub,
    request: customers_v1_customer_segment_validation_service_pb2.CheckCustomerSegmentEligibilityRequest,
    timeout: float
) -> customers_v1_customer_segment_validation_service_pb2.CheckCustomerSegmentEligibilityResponse:
    raise RuntimeError("domain hook was not installed")


async def cohort_lifecycle_renew_cohort2(
    client: checkout_v1_checkout_session_query_service_pb2_grpc.CheckoutSessionQueryServiceStub,
    request: checkout_v1_checkout_session_query_service_pb2.ResolveCheckoutSessionsRequest,
    timeout: float
) -> checkout_v1_checkout_session_query_service_pb2.ResolveCheckoutSessionsResponse:
    raise RuntimeError("domain hook was not installed")


async def cohort_workflow_signal_cohort_workflow0(
    client: analytics_v1_funnel_calculation_service_pb2_grpc.FunnelCalculationServiceStub,
    request: analytics_v1_funnel_calculation_service_pb2.QuoteFunnelRequest,
    timeout: float
) -> analytics_v1_funnel_calculation_service_pb2.QuoteFunnelResponse:
    raise RuntimeError("domain hook was not installed")


async def funnel_approval_submit_funnel0(
    client: anomalies_v1_anomaly_feedback_approval_service_pb2_grpc.AnomalyFeedbackApprovalServiceStub,
    request: anomalies_v1_anomaly_feedback_approval_service_pb2.EscalateAnomalyFeedbackRequest,
    timeout: float
) -> anomalies_v1_anomaly_feedback_approval_service_pb2.EscalateAnomalyFeedbackResponse:
    raise RuntimeError("domain hook was not installed")


async def funnel_calculation_simulate_funnel2(
    client: metrics_v1_metric_alert_query_service_pb2_grpc.MetricAlertQueryServiceStub,
    request: metrics_v1_metric_alert_query_service_pb2.FindMetricAlertsRequest,
    timeout: float
) -> metrics_v1_metric_alert_query_service_pb2.FindMetricAlertsResponse:
    raise RuntimeError("domain hook was not installed")


async def funnel_workflow_signal_funnel_workflow1(
    client: analytics_v1_analytics_event_workflow_service_pb2_grpc.AnalyticsEventWorkflowServiceStub,
    request: analytics_v1_analytics_event_workflow_service_pb2.CancelAnalyticsEventWorkflowRequest,
    timeout: float
) -> analytics_v1_analytics_event_workflow_service_pb2.CancelAnalyticsEventWorkflowResponse:
    raise RuntimeError("domain hook was not installed")
