"""Typed commands crossing the analytics application boundary."""

from __future__ import annotations

from dataclasses import dataclass

from google.protobuf import timestamp_pb2 as timestamp_pb2

from acme.analytics.v1 import (
    analytics_event_validation_service_pb2 as analytics_v1_analytics_event_validation_service_pb2,
)
from acme.analytics.v1 import analytics_pb2 as analytics_v1_analytics_pb2
from acme.analytics.v1 import (
    analytics_report_validation_service_pb2 as analytics_v1_analytics_report_validation_service_pb2,
)
from acme.analytics.v1 import cohort_calculation_service_pb2 as analytics_v1_cohort_calculation_service_pb2
from acme.analytics.v1 import cohort_lifecycle_service_pb2 as analytics_v1_cohort_lifecycle_service_pb2
from acme.analytics.v1 import funnel_query_service_pb2 as analytics_v1_funnel_query_service_pb2
from acme.analytics.v1 import refs_pb2 as analytics_v1_refs_pb2
from acme.anomalies.v1 import (
    anomaly_feedback_validation_service_pb2 as anomalies_v1_anomaly_feedback_validation_service_pb2,
)
from acme.authorization.v1 import access_policy_query_service_pb2 as authorization_v1_access_policy_query_service_pb2
from acme.billing.v1 import billing_account_query_service_pb2 as billing_v1_billing_account_query_service_pb2
from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.common.v1 import context_pb2 as common_v1_context_pb2
from acme.common.v1 import money_pb2 as common_v1_money_pb2
from acme.concessions.v1 import concession_stand_query_service_pb2 as concessions_v1_concession_stand_query_service_pb2
from acme.customers.v1 import refs_pb2 as customers_v1_refs_pb2
from acme.featureflags.v1 import (
    feature_flag_validation_service_pb2 as featureflags_v1_feature_flag_validation_service_pb2,
)
from acme.featureflags.v1 import featureflags_pb2 as featureflags_v1_featureflags_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.metrics.v1 import metric_alert_query_service_pb2 as metrics_v1_metric_alert_query_service_pb2
from acme.metrics.v1 import metric_series_service_pb2 as metrics_v1_metric_series_service_pb2
from acme.metrics.v1 import metrics_pb2 as metrics_v1_metrics_pb2
from acme.notifications.v1 import notification_query_service_pb2 as notifications_v1_notification_query_service_pb2
from acme.pipelines.v1 import pipeline_run_query_service_pb2 as pipelines_v1_pipeline_run_query_service_pb2
from acme.venues.v1 import venue_service_pb2 as venues_v1_venue_service_pb2
from acme.venues.v1 import venues_pb2 as venues_v1_venues_pb2

from acme_data.platform.models import ValidatedModel


@dataclass(frozen=True, slots=True)
class AnalyticsEventApprovalEscalateAnalyticsEvent2Command:
    """Inputs required to find billing accounts."""
    context: common_v1_context_pb2.RequestContext
    filter_region: str
    filter_created_after: timestamp_pb2.Timestamp
    filter_owner_id: str
    filter_labels: dict[str, str]


def to_analytics_event_approval_escalate_analytics_event2_command(
    command: AnalyticsEventApprovalEscalateAnalyticsEvent2Command
) -> billing_v1_billing_account_query_service_pb2.FindBillingAccountsRequest:
    return billing_v1_billing_account_query_service_pb2.FindBillingAccountsRequest(
        context=command.context,
        filter=billing_v1_billing_account_query_service_pb2.FindBillingAccountsRequest.Filter(
            created_after=command.filter_created_after,
            labels=command.filter_labels,
            owner_id=command.filter_owner_id,
            region=command.filter_region
        )
    )


@dataclass(frozen=True, slots=True)
class AnalyticsEventQueryResolveAnalyticsEvents1Command:
    """Inputs required to browse pipeline runs."""
    context: common_v1_context_pb2.RequestContext
    filter_owner_id: str


def to_analytics_event_query_resolve_analytics_events1_command(
    command: AnalyticsEventQueryResolveAnalyticsEvents1Command
) -> pipelines_v1_pipeline_run_query_service_pb2.BrowsePipelineRunsRequest:
    return pipelines_v1_pipeline_run_query_service_pb2.BrowsePipelineRunsRequest(
        context=command.context,
        filter=pipelines_v1_pipeline_run_query_service_pb2.BrowsePipelineRunsRequest.Filter(
            owner_id=command.filter_owner_id
        )
    )


@dataclass(frozen=True, slots=True)
class AnalyticsEventQuerySummarizeAnalyticsEvents0Command(ValidatedModel):
    """Inputs required to normalize anomaly feedback."""
    context: common_v1_context_pb2.RequestContext
    annotations: dict[str, str]
    details_contact_email: str
    reason: str
    details_locale: str


def to_analytics_event_query_summarize_analytics_events0_command(
    command: AnalyticsEventQuerySummarizeAnalyticsEvents0Command
) -> anomalies_v1_anomaly_feedback_validation_service_pb2.NormalizeAnomalyFeedbackRequest:
    return anomalies_v1_anomaly_feedback_validation_service_pb2.NormalizeAnomalyFeedbackRequest(
        annotations=command.annotations,
        context=command.context,
        details=anomalies_v1_anomaly_feedback_validation_service_pb2.NormalizeAnomalyFeedbackRequest.Details(
            contact=common_v1_contact_pb2.ContactInfo(email=command.details_contact_email),
            locale=command.details_locale
        ),
        reason=command.reason
    )


@dataclass(frozen=True, slots=True)
class AnalyticsEventUpdateAnalyticsEvent1Command(ValidatedModel):
    """Inputs required to count concession stands."""
    context: common_v1_context_pb2.RequestContext
    filter_created_after: timestamp_pb2.Timestamp


def to_analytics_event_update_analytics_event1_command(
    command: AnalyticsEventUpdateAnalyticsEvent1Command
) -> concessions_v1_concession_stand_query_service_pb2.CountConcessionStandsRequest:
    return concessions_v1_concession_stand_query_service_pb2.CountConcessionStandsRequest(
        context=command.context,
        filter=concessions_v1_concession_stand_query_service_pb2.CountConcessionStandsRequest.Filter(
            created_after=command.filter_created_after
        )
    )


@dataclass(frozen=True, slots=True)
class AnalyticsEventWorkflowPauseAnalyticsEventWorkflow0Command(ValidatedModel):
    """Inputs required to create venue."""
    context: common_v1_context_pb2.RequestContext
    venue_owner_display_name: str
    venue_owner_email: str


def to_analytics_event_workflow_pause_analytics_event_workflow0_command(
    command: AnalyticsEventWorkflowPauseAnalyticsEventWorkflow0Command
) -> venues_v1_venue_service_pb2.CreateVenueRequest:
    return venues_v1_venue_service_pb2.CreateVenueRequest(
        context=command.context,
        venue=venues_v1_venues_pb2.Venue(
            owner=identity_v1_refs_pb2.UserRef(
                display_name=command.venue_owner_display_name,
                email=command.venue_owner_email
            )
        )
    )


@dataclass(frozen=True, slots=True)
class AnalyticsReportApprovalCommentAnalyticsReportApproval0Command(ValidatedModel):
    """Inputs required to create metric series."""
    context: common_v1_context_pb2.RequestContext
    metric_series_address_locality: str


def to_analytics_report_approval_comment_analytics_report_approval0_command(
    command: AnalyticsReportApprovalCommentAnalyticsReportApproval0Command
) -> metrics_v1_metric_series_service_pb2.CreateMetricSeriesRequest:
    return metrics_v1_metric_series_service_pb2.CreateMetricSeriesRequest(
        context=command.context,
        metric_series=metrics_v1_metrics_pb2.MetricSeries(
            address=common_v1_address_pb2.PostalAddress(locality=command.metric_series_address_locality)
        )
    )


@dataclass(frozen=True, slots=True)
class AnalyticsReportLifecycleActivateAnalyticsReport1Command:
    """Inputs required to browse funnels."""
    context: common_v1_context_pb2.RequestContext
    filter_region: str
    filter_created_after: timestamp_pb2.Timestamp


def to_analytics_report_lifecycle_activate_analytics_report1_command(
    command: AnalyticsReportLifecycleActivateAnalyticsReport1Command
) -> analytics_v1_funnel_query_service_pb2.BrowseFunnelsRequest:
    return analytics_v1_funnel_query_service_pb2.BrowseFunnelsRequest(
        context=command.context,
        filter=analytics_v1_funnel_query_service_pb2.BrowseFunnelsRequest.Filter(
            created_after=command.filter_created_after,
            region=command.filter_region
        )
    )


@dataclass(frozen=True, slots=True)
class CohortApprovalDelegateCohortApproval1Command:
    """Inputs required to explain analytics report decision."""
    context: common_v1_context_pb2.RequestContext
    analytics_report_lines_tax_amount: common_v1_money_pb2.Money
    analytics_report_counterparty_display_name: str
    analytics_report_audit_updated_at: timestamp_pb2.Timestamp
    analytics_report_audit_created_at: timestamp_pb2.Timestamp


def to_cohort_approval_delegate_cohort_approval1_command(
    command: CohortApprovalDelegateCohortApproval1Command
) -> analytics_v1_analytics_report_validation_service_pb2.ExplainAnalyticsReportDecisionRequest:
    return analytics_v1_analytics_report_validation_service_pb2.ExplainAnalyticsReportDecisionRequest(
        analytics_report=analytics_v1_analytics_pb2.AnalyticsReport(
            audit=common_v1_audit_pb2.AuditInfo(
                created_at=command.analytics_report_audit_created_at,
                updated_at=command.analytics_report_audit_updated_at
            ),
            counterparty=customers_v1_refs_pb2.CustomerRef(
                display_name=command.analytics_report_counterparty_display_name
            ),
            lines=[
                analytics_v1_analytics_pb2.AnalyticsReportLine(
                    tax=analytics_v1_analytics_pb2.AnalyticsReportLineTax(
                        amount=command.analytics_report_lines_tax_amount
                    )
                )
            ]
        ),
        context=command.context
    )


@dataclass(frozen=True, slots=True)
class CohortApprovalDelegateCohortApproval2Command(ValidatedModel):
    """Inputs required to get cohort lifecycle."""
    context: common_v1_context_pb2.RequestContext
    cohort_id: str


def to_cohort_approval_delegate_cohort_approval2_command(
    command: CohortApprovalDelegateCohortApproval2Command
) -> analytics_v1_cohort_lifecycle_service_pb2.GetCohortLifecycleRequest:
    return analytics_v1_cohort_lifecycle_service_pb2.GetCohortLifecycleRequest(
        cohort_id=command.cohort_id,
        context=command.context
    )


@dataclass(frozen=True, slots=True)
class CohortCalculationCompareCohortOptions0Command(ValidatedModel):
    """Inputs required to check feature flag eligibility."""
    context: common_v1_context_pb2.RequestContext
    feature_flag_audit_created_by: str


def to_cohort_calculation_compare_cohort_options0_command(
    command: CohortCalculationCompareCohortOptions0Command
) -> featureflags_v1_feature_flag_validation_service_pb2.CheckFeatureFlagEligibilityRequest:
    return featureflags_v1_feature_flag_validation_service_pb2.CheckFeatureFlagEligibilityRequest(
        context=command.context,
        feature_flag=featureflags_v1_featureflags_pb2.FeatureFlag(
            audit=common_v1_audit_pb2.AuditInfo(created_by=command.feature_flag_audit_created_by)
        )
    )


@dataclass(frozen=True, slots=True)
class CohortLifecycleRenewCohort0Command(ValidatedModel):
    """Inputs required to simulate cohort."""
    context: common_v1_context_pb2.RequestContext
    cohort_owner_email: str


def to_cohort_lifecycle_renew_cohort0_command(
    command: CohortLifecycleRenewCohort0Command
) -> analytics_v1_cohort_calculation_service_pb2.SimulateCohortRequest:
    return analytics_v1_cohort_calculation_service_pb2.SimulateCohortRequest(
        cohort=analytics_v1_analytics_pb2.Cohort(owner=identity_v1_refs_pb2.UserRef(email=command.cohort_owner_email)),
        context=command.context
    )


@dataclass(frozen=True, slots=True)
class CohortValidationPreviewCohort1Command:
    """Inputs required to browse notifications."""
    context: common_v1_context_pb2.RequestContext
    filter_created_after: timestamp_pb2.Timestamp
    filter_owner_id: str
    filter_labels: dict[str, str]


def to_cohort_validation_preview_cohort1_command(
    command: CohortValidationPreviewCohort1Command
) -> notifications_v1_notification_query_service_pb2.BrowseNotificationsRequest:
    return notifications_v1_notification_query_service_pb2.BrowseNotificationsRequest(
        context=command.context,
        filter=notifications_v1_notification_query_service_pb2.BrowseNotificationsRequest.Filter(
            created_after=command.filter_created_after,
            labels=command.filter_labels,
            owner_id=command.filter_owner_id
        )
    )


@dataclass(frozen=True, slots=True)
class CohortWorkflowRetryCohortWorkflow0Command(ValidatedModel):
    """Inputs required to browse access policies."""
    context: common_v1_context_pb2.RequestContext
    filter_labels: dict[str, str]


def to_cohort_workflow_retry_cohort_workflow0_command(
    command: CohortWorkflowRetryCohortWorkflow0Command
) -> authorization_v1_access_policy_query_service_pb2.BrowseAccessPoliciesRequest:
    return authorization_v1_access_policy_query_service_pb2.BrowseAccessPoliciesRequest(
        context=command.context,
        filter=authorization_v1_access_policy_query_service_pb2.BrowseAccessPoliciesRequest.Filter(
            labels=command.filter_labels
        )
    )


@dataclass(frozen=True, slots=True)
class FunnelApprovalRejectFunnel1Command:
    """Inputs required to normalize analytics event."""
    context: common_v1_context_pb2.RequestContext
    details_contact_email: str
    analytics_event_subject_funnel_id: str
    analytics_event_subject_display_name: str


def to_funnel_approval_reject_funnel1_command(
    command: FunnelApprovalRejectFunnel1Command
) -> analytics_v1_analytics_event_validation_service_pb2.NormalizeAnalyticsEventRequest:
    return analytics_v1_analytics_event_validation_service_pb2.NormalizeAnalyticsEventRequest(
        analytics_event=analytics_v1_analytics_pb2.AnalyticsEvent(
            subject=analytics_v1_refs_pb2.FunnelRef(
                display_name=command.analytics_event_subject_display_name,
                funnel_id=command.analytics_event_subject_funnel_id
            )
        ),
        context=command.context,
        details=analytics_v1_analytics_event_validation_service_pb2.NormalizeAnalyticsEventRequest.Details(
            contact=common_v1_contact_pb2.ContactInfo(email=command.details_contact_email)
        )
    )


@dataclass(frozen=True, slots=True)
class FunnelCalculationQuoteFunnel1Command:
    """Inputs required to find metric alerts."""
    context: common_v1_context_pb2.RequestContext
    filter_region: str
    filter_created_after: timestamp_pb2.Timestamp
    filter_owner_id: str
    filter_labels: dict[str, str]


def to_funnel_calculation_quote_funnel1_command(
    command: FunnelCalculationQuoteFunnel1Command
) -> metrics_v1_metric_alert_query_service_pb2.FindMetricAlertsRequest:
    return metrics_v1_metric_alert_query_service_pb2.FindMetricAlertsRequest(
        context=command.context,
        filter=metrics_v1_metric_alert_query_service_pb2.FindMetricAlertsRequest.Filter(
            created_after=command.filter_created_after,
            labels=command.filter_labels,
            owner_id=command.filter_owner_id,
            region=command.filter_region
        )
    )
