"""Transport adapters used by analytics workflows."""

from __future__ import annotations

from typing import Protocol

from acme.analytics.v1 import analytics_event_query_service_pb2 as analytics_v1_analytics_event_query_service_pb2
from acme.analytics.v1 import (
    analytics_event_query_service_pb2_grpc as analytics_v1_analytics_event_query_service_pb2_grpc,
)
from acme.analytics.v1 import (
    analytics_event_validation_service_pb2 as analytics_v1_analytics_event_validation_service_pb2,
)
from acme.analytics.v1 import (
    analytics_event_validation_service_pb2_grpc as analytics_v1_analytics_event_validation_service_pb2_grpc,
)
from acme.analytics.v1 import analytics_event_workflow_service_pb2 as analytics_v1_analytics_event_workflow_service_pb2
from acme.analytics.v1 import (
    analytics_event_workflow_service_pb2_grpc as analytics_v1_analytics_event_workflow_service_pb2_grpc,
)
from acme.analytics.v1 import (
    analytics_report_approval_service_pb2 as analytics_v1_analytics_report_approval_service_pb2,
)
from acme.analytics.v1 import (
    analytics_report_approval_service_pb2_grpc as analytics_v1_analytics_report_approval_service_pb2_grpc,
)
from acme.analytics.v1 import (
    analytics_report_calculation_service_pb2 as analytics_v1_analytics_report_calculation_service_pb2,
)
from acme.analytics.v1 import (
    analytics_report_calculation_service_pb2_grpc as analytics_v1_analytics_report_calculation_service_pb2_grpc,
)
from acme.analytics.v1 import cohort_calculation_service_pb2 as analytics_v1_cohort_calculation_service_pb2
from acme.analytics.v1 import cohort_calculation_service_pb2_grpc as analytics_v1_cohort_calculation_service_pb2_grpc
from acme.analytics.v1 import cohort_validation_service_pb2 as analytics_v1_cohort_validation_service_pb2
from acme.analytics.v1 import cohort_validation_service_pb2_grpc as analytics_v1_cohort_validation_service_pb2_grpc
from acme.analytics.v1 import funnel_calculation_service_pb2 as analytics_v1_funnel_calculation_service_pb2
from acme.analytics.v1 import funnel_calculation_service_pb2_grpc as analytics_v1_funnel_calculation_service_pb2_grpc
from acme.analytics.v1 import funnel_query_service_pb2 as analytics_v1_funnel_query_service_pb2
from acme.analytics.v1 import funnel_query_service_pb2_grpc as analytics_v1_funnel_query_service_pb2_grpc
from acme.analytics.v1 import funnel_validation_service_pb2 as analytics_v1_funnel_validation_service_pb2
from acme.analytics.v1 import funnel_validation_service_pb2_grpc as analytics_v1_funnel_validation_service_pb2_grpc
from acme.anomalies.v1 import (
    anomaly_feedback_approval_service_pb2 as anomalies_v1_anomaly_feedback_approval_service_pb2,
)
from acme.anomalies.v1 import (
    anomaly_feedback_approval_service_pb2_grpc as anomalies_v1_anomaly_feedback_approval_service_pb2_grpc,
)
from acme.anomalies.v1 import (
    anomaly_feedback_validation_service_pb2 as anomalies_v1_anomaly_feedback_validation_service_pb2,
)
from acme.anomalies.v1 import (
    anomaly_feedback_validation_service_pb2_grpc as anomalies_v1_anomaly_feedback_validation_service_pb2_grpc,
)
from acme.appointments.v1 import appointment_service_pb2 as appointments_v1_appointment_service_pb2
from acme.appointments.v1 import appointment_service_pb2_grpc as appointments_v1_appointment_service_pb2_grpc
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
from acme.customers.v1 import household_calculation_service_pb2 as customers_v1_household_calculation_service_pb2
from acme.customers.v1 import (
    household_calculation_service_pb2_grpc as customers_v1_household_calculation_service_pb2_grpc,
)
from acme.customers.v1 import preference_calculation_service_pb2 as customers_v1_preference_calculation_service_pb2
from acme.customers.v1 import (
    preference_calculation_service_pb2_grpc as customers_v1_preference_calculation_service_pb2_grpc,
)
from acme.datasets.v1 import data_schema_calculation_service_pb2 as datasets_v1_data_schema_calculation_service_pb2
from acme.datasets.v1 import (
    data_schema_calculation_service_pb2_grpc as datasets_v1_data_schema_calculation_service_pb2_grpc,
)
from acme.datasets.v1 import dataset_version_workflow_service_pb2 as datasets_v1_dataset_version_workflow_service_pb2
from acme.datasets.v1 import (
    dataset_version_workflow_service_pb2_grpc as datasets_v1_dataset_version_workflow_service_pb2_grpc,
)
from acme.featurestore.v1 import (
    feature_view_validation_service_pb2 as featurestore_v1_feature_view_validation_service_pb2,
)
from acme.featurestore.v1 import (
    feature_view_validation_service_pb2_grpc as featurestore_v1_feature_view_validation_service_pb2_grpc,
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
    return await client.CompareAnalyticsReportOptions(request, timeout=timeout)


class AnalyticsEventApprovalSubmitAnalyticsEvent1Adapter:
    def __init__(
        self,
        client: analytics_v1_analytics_event_query_service_pb2_grpc.AnalyticsEventQueryServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def __call__(
        self,
        request: analytics_v1_analytics_event_query_service_pb2.ResolveAnalyticsEventsRequest
    ) -> analytics_v1_analytics_event_query_service_pb2.ResolveAnalyticsEventsResponse:
        return await self.client.ResolveAnalyticsEvents(request, timeout=self.timeout)


async def analytics_event_batch_create_analytics_events1(
    client: analytics_v1_funnel_calculation_service_pb2_grpc.FunnelCalculationServiceStub,
    request: analytics_v1_funnel_calculation_service_pb2.EstimateFunnelRequest,
    timeout: float
) -> analytics_v1_funnel_calculation_service_pb2.EstimateFunnelResponse:
    return await client.EstimateFunnel(request, timeout=timeout)


class AnalyticsEventCreateAnalyticsEvent1Port(Protocol):
    async def execute(
        self,
        request: analytics_v1_cohort_calculation_service_pb2.CalculateCohortRequest
    ) -> analytics_v1_cohort_calculation_service_pb2.CalculateCohortResponse: ...


class AnalyticsEventCreateAnalyticsEvent1Adapter:
    def __init__(
        self,
        client: analytics_v1_cohort_calculation_service_pb2_grpc.CohortCalculationServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def execute(
        self,
        request: analytics_v1_cohort_calculation_service_pb2.CalculateCohortRequest
    ) -> analytics_v1_cohort_calculation_service_pb2.CalculateCohortResponse:
        return await self.client.CalculateCohort(request, timeout=self.timeout)


async def analytics_event_watch_analytics_events1(
    client: metrics_v1_metric_alert_validation_service_pb2_grpc.MetricAlertValidationServiceStub,
    request: metrics_v1_metric_alert_validation_service_pb2.ExplainMetricAlertDecisionRequest,
    timeout: float
) -> metrics_v1_metric_alert_validation_service_pb2.ExplainMetricAlertDecisionResponse:
    return await client.ExplainMetricAlertDecision(request, timeout=timeout)


async def analytics_report_approval_comment_analytics_report_approval2(
    client: customers_v1_preference_calculation_service_pb2_grpc.PreferenceCalculationServiceStub,
    request: customers_v1_preference_calculation_service_pb2.QuotePreferenceRequest,
    timeout: float
) -> customers_v1_preference_calculation_service_pb2.QuotePreferenceResponse:
    return await client.QuotePreference(request, timeout=timeout)


class AnalyticsReportCalculationCalculateAnalyticsReport1Port(Protocol):
    async def execute(
        self,
        request: featurestore_v1_feature_view_validation_service_pb2.CheckFeatureViewEligibilityRequest
    ) -> featurestore_v1_feature_view_validation_service_pb2.CheckFeatureViewEligibilityResponse: ...


class AnalyticsReportCalculationCalculateAnalyticsReport1Adapter:
    def __init__(
        self,
        client: featurestore_v1_feature_view_validation_service_pb2_grpc.FeatureViewValidationServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def execute(
        self,
        request: featurestore_v1_feature_view_validation_service_pb2.CheckFeatureViewEligibilityRequest
    ) -> featurestore_v1_feature_view_validation_service_pb2.CheckFeatureViewEligibilityResponse:
        return await self.client.CheckFeatureViewEligibility(request, timeout=self.timeout)


class AnalyticsReportCalculationCompareAnalyticsReportOptions0Adapter:
    def __init__(
        self,
        client: analytics_v1_funnel_validation_service_pb2_grpc.FunnelValidationServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def __call__(
        self,
        request: analytics_v1_funnel_validation_service_pb2.CheckFunnelEligibilityRequest
    ) -> analytics_v1_funnel_validation_service_pb2.CheckFunnelEligibilityResponse:
        return await self.client.CheckFunnelEligibility(request, timeout=self.timeout)


async def analytics_report_lifecycle_expire_analytics_report2(
    client: analytics_v1_analytics_event_query_service_pb2_grpc.AnalyticsEventQueryServiceStub,
    request: analytics_v1_analytics_event_query_service_pb2.FindAnalyticsEventsRequest,
    timeout: float
) -> analytics_v1_analytics_event_query_service_pb2.FindAnalyticsEventsResponse:
    return await client.FindAnalyticsEvents(request, timeout=timeout)


async def analytics_report_validation_normalize_analytics_report0(
    client: ledger_v1_ledger_account_validation_service_pb2_grpc.LedgerAccountValidationServiceStub,
    request: ledger_v1_ledger_account_validation_service_pb2.PreviewLedgerAccountRequest,
    timeout: float
) -> ledger_v1_ledger_account_validation_service_pb2.PreviewLedgerAccountResponse:
    return await client.PreviewLedgerAccount(request, timeout=timeout)


class AnalyticsReportValidationPreviewAnalyticsReport1Adapter:
    def __init__(
        self,
        client: analytics_v1_cohort_validation_service_pb2_grpc.CohortValidationServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def __call__(
        self,
        request: analytics_v1_cohort_validation_service_pb2.PreviewCohortRequest
    ) -> analytics_v1_cohort_validation_service_pb2.PreviewCohortResponse:
        return await self.client.PreviewCohort(request, timeout=self.timeout)


async def cohort_approval_escalate_cohort0(
    client: customers_v1_customer_segment_validation_service_pb2_grpc.CustomerSegmentValidationServiceStub,
    request: customers_v1_customer_segment_validation_service_pb2.CheckCustomerSegmentEligibilityRequest,
    timeout: float
) -> customers_v1_customer_segment_validation_service_pb2.CheckCustomerSegmentEligibilityResponse:
    return await client.CheckCustomerSegmentEligibility(request, timeout=timeout)


class CohortApprovalEscalateCohort2Port(Protocol):
    async def execute(
        self,
        request: analytics_v1_analytics_event_workflow_service_pb2.ResumeAnalyticsEventWorkflowRequest
    ) -> analytics_v1_analytics_event_workflow_service_pb2.ResumeAnalyticsEventWorkflowResponse: ...


class CohortApprovalEscalateCohort2Adapter:
    def __init__(
        self,
        client: analytics_v1_analytics_event_workflow_service_pb2_grpc.AnalyticsEventWorkflowServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def execute(
        self,
        request: analytics_v1_analytics_event_workflow_service_pb2.ResumeAnalyticsEventWorkflowRequest
    ) -> analytics_v1_analytics_event_workflow_service_pb2.ResumeAnalyticsEventWorkflowResponse:
        return await self.client.ResumeAnalyticsEventWorkflow(request, timeout=self.timeout)


class CohortCalculationExplainCohortCalculation1Port(Protocol):
    async def execute(
        self,
        request: datasets_v1_data_schema_calculation_service_pb2.RecalculateDataSchemasRequest
    ) -> datasets_v1_data_schema_calculation_service_pb2.RecalculateDataSchemasResponse: ...


class CohortCalculationExplainCohortCalculation1Adapter:
    def __init__(
        self,
        client: datasets_v1_data_schema_calculation_service_pb2_grpc.DataSchemaCalculationServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def execute(
        self,
        request: datasets_v1_data_schema_calculation_service_pb2.RecalculateDataSchemasRequest
    ) -> datasets_v1_data_schema_calculation_service_pb2.RecalculateDataSchemasResponse:
        return await self.client.RecalculateDataSchemas(request, timeout=self.timeout)


class CohortCalculationQuoteCohort0Adapter:
    def __init__(
        self,
        client: analytics_v1_analytics_event_validation_service_pb2_grpc.AnalyticsEventValidationServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def __call__(
        self,
        request: analytics_v1_analytics_event_validation_service_pb2.LintAnalyticsEventsRequest
    ) -> analytics_v1_analytics_event_validation_service_pb2.LintAnalyticsEventsResponse:
        return await self.client.LintAnalyticsEvents(request, timeout=self.timeout)


async def cohort_lifecycle_renew_cohort2(
    client: checkout_v1_checkout_session_query_service_pb2_grpc.CheckoutSessionQueryServiceStub,
    request: checkout_v1_checkout_session_query_service_pb2.ResolveCheckoutSessionsRequest,
    timeout: float
) -> checkout_v1_checkout_session_query_service_pb2.ResolveCheckoutSessionsResponse:
    return await client.ResolveCheckoutSessions(request, timeout=timeout)


class CohortLifecycleSuspendCohort1Port(Protocol):
    async def execute(
        self,
        request: analytics_v1_funnel_query_service_pb2.BrowseFunnelsRequest
    ) -> analytics_v1_funnel_query_service_pb2.BrowseFunnelsResponse: ...


class CohortLifecycleSuspendCohort1Adapter:
    def __init__(
        self,
        client: analytics_v1_funnel_query_service_pb2_grpc.FunnelQueryServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def execute(
        self,
        request: analytics_v1_funnel_query_service_pb2.BrowseFunnelsRequest
    ) -> analytics_v1_funnel_query_service_pb2.BrowseFunnelsResponse:
        return await self.client.BrowseFunnels(request, timeout=self.timeout)


class CohortLifecycleSuspendCohort3Adapter:
    def __init__(
        self,
        client: analytics_v1_funnel_calculation_service_pb2_grpc.FunnelCalculationServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def __call__(
        self,
        request: analytics_v1_funnel_calculation_service_pb2.EstimateFunnelRequest
    ) -> analytics_v1_funnel_calculation_service_pb2.EstimateFunnelResponse:
        return await self.client.EstimateFunnel(request, timeout=self.timeout)


class CohortWorkflowAdvanceCohortWorkflow0Port(Protocol):
    async def execute(
        self,
        request: analytics_v1_analytics_report_approval_service_pb2.EscalateAnalyticsReportRequest
    ) -> analytics_v1_analytics_report_approval_service_pb2.EscalateAnalyticsReportResponse: ...


class CohortWorkflowAdvanceCohortWorkflow0Adapter:
    def __init__(
        self,
        client: analytics_v1_analytics_report_approval_service_pb2_grpc.AnalyticsReportApprovalServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def execute(
        self,
        request: analytics_v1_analytics_report_approval_service_pb2.EscalateAnalyticsReportRequest
    ) -> analytics_v1_analytics_report_approval_service_pb2.EscalateAnalyticsReportResponse:
        return await self.client.EscalateAnalyticsReport(request, timeout=self.timeout)


class CohortWorkflowAdvanceCohortWorkflow2Adapter:
    def __init__(
        self,
        client: analytics_v1_analytics_report_approval_service_pb2_grpc.AnalyticsReportApprovalServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def __call__(
        self,
        request: analytics_v1_analytics_report_approval_service_pb2.ApproveAnalyticsReportRequest
    ) -> analytics_v1_analytics_report_approval_service_pb2.ApproveAnalyticsReportResponse:
        return await self.client.ApproveAnalyticsReport(request, timeout=self.timeout)


async def cohort_workflow_signal_cohort_workflow0(
    client: analytics_v1_funnel_calculation_service_pb2_grpc.FunnelCalculationServiceStub,
    request: analytics_v1_funnel_calculation_service_pb2.QuoteFunnelRequest,
    timeout: float
) -> analytics_v1_funnel_calculation_service_pb2.QuoteFunnelResponse:
    return await client.QuoteFunnel(request, timeout=timeout)


class FunnelApprovalApproveFunnel0Port(Protocol):
    async def execute(
        self,
        request: analytics_v1_funnel_calculation_service_pb2.SimulateFunnelRequest
    ) -> analytics_v1_funnel_calculation_service_pb2.SimulateFunnelResponse: ...


class FunnelApprovalApproveFunnel0Adapter:
    def __init__(
        self,
        client: analytics_v1_funnel_calculation_service_pb2_grpc.FunnelCalculationServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def execute(
        self,
        request: analytics_v1_funnel_calculation_service_pb2.SimulateFunnelRequest
    ) -> analytics_v1_funnel_calculation_service_pb2.SimulateFunnelResponse:
        return await self.client.SimulateFunnel(request, timeout=self.timeout)


class FunnelApprovalCommentFunnelApproval1Adapter:
    def __init__(
        self,
        client: customers_v1_household_calculation_service_pb2_grpc.HouseholdCalculationServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def __call__(
        self,
        request: customers_v1_household_calculation_service_pb2.QuoteHouseholdRequest
    ) -> customers_v1_household_calculation_service_pb2.QuoteHouseholdResponse:
        return await self.client.QuoteHousehold(request, timeout=self.timeout)


async def funnel_approval_submit_funnel0(
    client: anomalies_v1_anomaly_feedback_approval_service_pb2_grpc.AnomalyFeedbackApprovalServiceStub,
    request: anomalies_v1_anomaly_feedback_approval_service_pb2.EscalateAnomalyFeedbackRequest,
    timeout: float
) -> anomalies_v1_anomaly_feedback_approval_service_pb2.EscalateAnomalyFeedbackResponse:
    return await client.EscalateAnomalyFeedback(request, timeout=timeout)


class FunnelCalculationCalculateFunnel0Port(Protocol):
    async def execute(
        self,
        request: metrics_v1_metric_alert_query_service_pb2.BrowseMetricAlertsRequest
    ) -> metrics_v1_metric_alert_query_service_pb2.BrowseMetricAlertsResponse: ...


class FunnelCalculationCalculateFunnel0Adapter:
    def __init__(
        self,
        client: metrics_v1_metric_alert_query_service_pb2_grpc.MetricAlertQueryServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def execute(
        self,
        request: metrics_v1_metric_alert_query_service_pb2.BrowseMetricAlertsRequest
    ) -> metrics_v1_metric_alert_query_service_pb2.BrowseMetricAlertsResponse:
        return await self.client.BrowseMetricAlerts(request, timeout=self.timeout)


class FunnelCalculationCompareFunnelOptions0Adapter:
    def __init__(
        self,
        client: appointments_v1_appointment_service_pb2_grpc.AppointmentServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def __call__(
        self,
        request: appointments_v1_appointment_service_pb2.ListAppointmentsRequest
    ) -> appointments_v1_appointment_service_pb2.ListAppointmentsResponse:
        return await self.client.ListAppointments(request, timeout=self.timeout)


async def funnel_calculation_simulate_funnel2(
    client: metrics_v1_metric_alert_query_service_pb2_grpc.MetricAlertQueryServiceStub,
    request: metrics_v1_metric_alert_query_service_pb2.FindMetricAlertsRequest,
    timeout: float
) -> metrics_v1_metric_alert_query_service_pb2.FindMetricAlertsResponse:
    return await client.FindMetricAlerts(request, timeout=timeout)


class FunnelValidationValidateFunnel1Adapter:
    def __init__(
        self,
        client: anomalies_v1_anomaly_feedback_validation_service_pb2_grpc.AnomalyFeedbackValidationServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def __call__(
        self,
        request: anomalies_v1_anomaly_feedback_validation_service_pb2.NormalizeAnomalyFeedbackRequest
    ) -> anomalies_v1_anomaly_feedback_validation_service_pb2.NormalizeAnomalyFeedbackResponse:
        return await self.client.NormalizeAnomalyFeedback(request, timeout=self.timeout)


async def funnel_workflow_signal_funnel_workflow1(
    client: analytics_v1_analytics_event_workflow_service_pb2_grpc.AnalyticsEventWorkflowServiceStub,
    request: analytics_v1_analytics_event_workflow_service_pb2.CancelAnalyticsEventWorkflowRequest,
    timeout: float
) -> analytics_v1_analytics_event_workflow_service_pb2.CancelAnalyticsEventWorkflowResponse:
    return await client.CancelAnalyticsEventWorkflow(request, timeout=timeout)


class FunnelWorkflowStartFunnelWorkflow1Port(Protocol):
    async def execute(
        self,
        request: datasets_v1_dataset_version_workflow_service_pb2.AdvanceDatasetVersionWorkflowRequest
    ) -> datasets_v1_dataset_version_workflow_service_pb2.AdvanceDatasetVersionWorkflowResponse: ...


class FunnelWorkflowStartFunnelWorkflow1Adapter:
    def __init__(
        self,
        client: datasets_v1_dataset_version_workflow_service_pb2_grpc.DatasetVersionWorkflowServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def execute(
        self,
        request: datasets_v1_dataset_version_workflow_service_pb2.AdvanceDatasetVersionWorkflowRequest
    ) -> datasets_v1_dataset_version_workflow_service_pb2.AdvanceDatasetVersionWorkflowResponse:
        return await self.client.AdvanceDatasetVersionWorkflow(request, timeout=self.timeout)
