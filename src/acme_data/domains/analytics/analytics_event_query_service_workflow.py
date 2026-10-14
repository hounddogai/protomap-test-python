"""Application workflow for AnalyticsEvent Query."""

from __future__ import annotations

import logging

from google.protobuf.json_format import MessageToDict
from google.protobuf.json_format import MessageToJson
from google.protobuf.json_format import Parse
from google.protobuf.json_format import ParseDict

from acme.analytics.v1 import analytics_event_query_service_pb2 as analytics_v1_analytics_event_query_service_pb2
from acme.analytics.v1 import (
    analytics_event_validation_service_pb2 as analytics_v1_analytics_event_validation_service_pb2,
)
from acme.analytics.v1 import analytics_pb2 as analytics_v1_analytics_pb2
from acme.analytics.v1 import (
    analytics_report_validation_service_pb2 as analytics_v1_analytics_report_validation_service_pb2,
)
from acme.analytics.v1 import cohort_calculation_service_pb2 as analytics_v1_cohort_calculation_service_pb2
from acme.analytics.v1 import funnel_validation_service_pb2 as analytics_v1_funnel_validation_service_pb2
from acme.anomalies.v1 import (
    anomaly_feedback_validation_service_pb2 as anomalies_v1_anomaly_feedback_validation_service_pb2,
)
from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.customers.v1 import refs_pb2 as customers_v1_refs_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.metrics.v1 import metric_series_query_service_pb2 as metrics_v1_metric_series_query_service_pb2
from acme.notifications.v1 import notification_query_service_pb2 as notifications_v1_notification_query_service_pb2
from acme.pipelines.v1 import pipeline_run_query_service_pb2 as pipelines_v1_pipeline_run_query_service_pb2

from acme_data.domains.analytics.dependencies import Dependencies
from acme_data.domains.analytics.models import AnalyticsEventQueryResolveAnalyticsEvents1Command
from acme_data.domains.analytics.models import AnalyticsEventQuerySummarizeAnalyticsEvents0Command
from acme_data.domains.analytics.models import to_analytics_event_query_resolve_analytics_events1_command
from acme_data.domains.analytics.models import to_analytics_event_query_summarize_analytics_events0_command
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class AnalyticsEventQueryServicerWorkflow:
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    async def handle_browse_analytics_events(
        self,
        request: analytics_v1_analytics_event_query_service_pb2.BrowseAnalyticsEventsRequest
    ) -> analytics_v1_analytics_event_query_service_pb2.BrowseAnalyticsEventsResponse:
        """Lists analytics events a page at a time."""
        deps = self.deps
        response = analytics_v1_analytics_event_query_service_pb2.BrowseAnalyticsEventsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('BrowseAnalyticsEvents', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'BrowseAnalyticsEvents',
                {'order_by': request.order_by}
            )
            response_0 = analytics_v1_cohort_calculation_service_pb2.EstimateCohortResponse()
            response_1 = analytics_v1_analytics_report_validation_service_pb2.ValidateAnalyticsReportResponse()
            outgoing_0 = analytics_v1_cohort_calculation_service_pb2.EstimateCohortRequest(
                cohort=analytics_v1_analytics_pb2.Cohort(
                    owner=identity_v1_refs_pb2.UserRef(user_id=request.context.actor.user_id)
                ),
                context=request.context,
                details=analytics_v1_cohort_calculation_service_pb2.EstimateCohortRequest.Details(
                    destination=common_v1_address_pb2.PostalAddress(region=request.filter.region)
                )
            )
            response_0 = await deps.clients.analytics_cohort_calculation.EstimateCohort(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = analytics_v1_analytics_report_validation_service_pb2.ValidateAnalyticsReportRequest(
                analytics_report=analytics_v1_analytics_pb2.AnalyticsReport(
                    audit=common_v1_audit_pb2.AuditInfo(updated_by=response_0.cohort.audit.updated_by),
                    lines=[
                        analytics_v1_analytics_pb2.AnalyticsReportLine(
                            tax=analytics_v1_analytics_pb2.AnalyticsReportLineTax(
                                amount=response_0.cohort.discount.amount
                            )
                        )
                    ]
                ),
                context=request.context
            )
            method_name_1 = 'ValidateAnalyticsReport'
            response_1 = await getattr(
                deps.clients.analytics_analytics_report_validation,
                method_name_1
            )(outgoing_1, timeout=deps.settings.timeout)
            returned_0_0 = response_0.result.correlation_id
            returned_0_0_part_0 = response.analytics_events.add()
            if returned_0_0:
                returned_0_0_part_0.correlation_id = returned_0_0
            returned_0_1 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_1)
            returned_1_0 = response_1.result.correlation_id
            if returned_1_0:
                response.result.correlation_id = returned_1_0
            returned_1_1 = response_1.result.message
            if returned_1_1:
                response.result.message = returned_1_1
            return response

    async def handle_count_analytics_events(
        self,
        request: analytics_v1_analytics_event_query_service_pb2.CountAnalyticsEventsRequest
    ) -> analytics_v1_analytics_event_query_service_pb2.CountAnalyticsEventsResponse:
        """Counts analytics events by status."""
        deps = self.deps
        response = analytics_v1_analytics_event_query_service_pb2.CountAnalyticsEventsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CountAnalyticsEvents', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'CountAnalyticsEvents',
                {'order_by': request.order_by}
            )
            response_0 = metrics_v1_metric_series_query_service_pb2.SummarizeMetricSeriesesResponse()
            response_1 = analytics_v1_funnel_validation_service_pb2.PreviewFunnelResponse()
            outgoing_0 = metrics_v1_metric_series_query_service_pb2.SummarizeMetricSeriesesRequest(
                annotations=dict(request.context.baggage),
                context=request.context,
                details=metrics_v1_metric_series_query_service_pb2.SummarizeMetricSeriesesRequest.Details(
                    filters=dict(request.filter.labels)
                )
            )
            response_0 = await deps.clients.metrics_metric_series_query.SummarizeMetricSerieses(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = analytics_v1_funnel_validation_service_pb2.PreviewFunnelRequest(
                context=request.context,
                details=analytics_v1_funnel_validation_service_pb2.PreviewFunnelRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(email=request.context.actor.email),
                    locale=request.context.locale
                ),
                funnel=analytics_v1_analytics_pb2.Funnel(
                    owner=identity_v1_refs_pb2.UserRef(user_id=request.context.actor.user_id)
                )
            )
            document_1 = MessageToDict(outgoing_1, preserving_proto_field_name=True)
            outgoing_1 = ParseDict(document_1, analytics_v1_funnel_validation_service_pb2.PreviewFunnelRequest())
            response_1 = await deps.clients.analytics_funnel_validation.PreviewFunnel(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.result.message = returned_0_0
            returned_0_1 = response_0.result.correlation_id
            if returned_0_1:
                response.result.correlation_id = returned_0_1
            returned_1_0 = response_1.result.correlation_id
            if returned_1_0:
                response.result.correlation_id = returned_1_0
            returned_1_1 = response_1.result.status
            if returned_1_1:
                response.result.status = returned_1_1
            return response

    async def handle_export_analytics_events(
        self,
        request: analytics_v1_analytics_event_query_service_pb2.ExportAnalyticsEventsRequest
    ) -> analytics_v1_analytics_event_query_service_pb2.ExportAnalyticsEventsResponse:
        """Streams every matching analytics event."""
        deps = self.deps
        response = analytics_v1_analytics_event_query_service_pb2.ExportAnalyticsEventsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ExportAnalyticsEvents', extra={'fields': {'destination_uri': request.destination_uri}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ExportAnalyticsEvents',
                {'destination_uri': request.destination_uri}
            )
            response_0 = analytics_v1_analytics_report_validation_service_pb2.ScoreAnalyticsReportResponse()
            response_1 = analytics_v1_analytics_event_validation_service_pb2.ExplainAnalyticsEventDecisionResponse()
            outgoing_0 = analytics_v1_analytics_report_validation_service_pb2.ScoreAnalyticsReportRequest(
                context=request.context,
                details=analytics_v1_analytics_report_validation_service_pb2.ScoreAnalyticsReportRequest.Details(
                    destination=common_v1_address_pb2.PostalAddress(region=request.filter.region)
                )
            )
            document_0 = MessageToJson(outgoing_0, preserving_proto_field_name=True)
            outgoing_0 = Parse(
                document_0,
                analytics_v1_analytics_report_validation_service_pb2.ScoreAnalyticsReportRequest()
            )
            response_0 = await deps.clients.analytics_analytics_report_validation.ScoreAnalyticsReport(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = analytics_v1_analytics_event_validation_service_pb2.ExplainAnalyticsEventDecisionRequest()
            outgoing_1.context.CopyFrom(request.context)
            outgoing_1.analytics_event.subject.display_name = response_0.analytics_report.counterparty.display_name
            outgoing_1.analytics_event.correlation_id = response_0.result.correlation_id
            outgoing_1.details.contact.email = response_0.analytics_report.counterparty.email
            field_1_4_part_1 = outgoing_1.analytics_event.measurements.add()
            field_1_4_part_1.observed_at.CopyFrom(response_0.analytics_report.audit.updated_at)
            merged_1 = analytics_v1_analytics_event_validation_service_pb2.ExplainAnalyticsEventDecisionRequest()
            merged_1.MergeFrom(outgoing_1)
            outgoing_1.CopyFrom(merged_1)
            response_1 = await deps.clients.analytics_analytics_event_validation.ExplainAnalyticsEventDecision(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.status
            if returned_0_0:
                response.result.status = returned_0_0
            returned_0_1 = response_0.analytics_report.counterparty.display_name
            if returned_0_1:
                response.analytics_event.subject.display_name = returned_0_1
            returned_1_0 = response_1.result.correlation_id
            if returned_1_0:
                response.analytics_event.correlation_id = returned_1_0
            returned_1_1 = response_1.analytics_event.subject
            if returned_1_1.ListFields():
                response.analytics_event.subject.MergeFrom(returned_1_1)
            return response

    async def handle_find_analytics_events(
        self,
        request: analytics_v1_analytics_event_query_service_pb2.FindAnalyticsEventsRequest
    ) -> analytics_v1_analytics_event_query_service_pb2.FindAnalyticsEventsResponse:
        """Lists analytics events a page at a time."""
        deps = self.deps
        response = analytics_v1_analytics_event_query_service_pb2.FindAnalyticsEventsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('FindAnalyticsEvents', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'FindAnalyticsEvents',
                {'order_by': request.order_by}
            )
            return response

    async def handle_lookup_analytics_event(
        self,
        request: analytics_v1_analytics_event_query_service_pb2.LookupAnalyticsEventRequest
    ) -> analytics_v1_analytics_event_query_service_pb2.LookupAnalyticsEventResponse:
        """Returns an analytics event."""
        deps = self.deps
        response = analytics_v1_analytics_event_query_service_pb2.LookupAnalyticsEventResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('LookupAnalyticsEvent', extra={'fields': {'locale': request.context.locale}})
            await deps.repository.audit(
                request.context.tenant_id,
                'LookupAnalyticsEvent',
                {'locale': request.context.locale}
            )
            echoed_0 = request.analytics_event_id
            response.analytics_event.analytics_event_id = echoed_0
            return response

    async def handle_peek_analytics_event(
        self,
        request: analytics_v1_analytics_event_query_service_pb2.PeekAnalyticsEventRequest
    ) -> analytics_v1_analytics_event_query_service_pb2.PeekAnalyticsEventResponse:
        """Returns an analytics event."""
        deps = self.deps
        response = analytics_v1_analytics_event_query_service_pb2.PeekAnalyticsEventResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('PeekAnalyticsEvent', extra={'fields': {'domain': 'analytics'}})
            await deps.repository.audit(request.context.tenant_id, 'PeekAnalyticsEvent', {})
            response_0 = analytics_v1_analytics_report_validation_service_pb2.LintAnalyticsReportsResponse()
            outgoing_0 = analytics_v1_analytics_report_validation_service_pb2.LintAnalyticsReportsRequest(
                analytics_report=analytics_v1_analytics_pb2.AnalyticsReport(
                    counterparty=customers_v1_refs_pb2.CustomerRef(email=request.context.actor.email)
                ),
                context=request.context,
                details=analytics_v1_analytics_report_validation_service_pb2.LintAnalyticsReportsRequest.Details(
                    locale=request.context.locale
                )
            )
            response_0 = await deps.clients.analytics_analytics_report_validation.LintAnalyticsReports(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.correlation_id
            if returned_0_0:
                response.analytics_event.correlation_id = returned_0_0
            returned_0_1 = response_0.result.correlation_id
            if returned_0_1:
                response.result.correlation_id = returned_0_1
            echoed_0 = request.analytics_event_id
            response.analytics_event.analytics_event_id = echoed_0
            return response

    async def handle_resolve_analytics_events(
        self,
        request: analytics_v1_analytics_event_query_service_pb2.ResolveAnalyticsEventsRequest
    ) -> analytics_v1_analytics_event_query_service_pb2.ResolveAnalyticsEventsResponse:
        """Returns several analytics events at once."""
        deps = self.deps
        response = analytics_v1_analytics_event_query_service_pb2.ResolveAnalyticsEventsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ResolveAnalyticsEvents', extra={'fields': {'domain': 'analytics'}})
            await deps.repository.audit(request.context.tenant_id, 'ResolveAnalyticsEvents', {})
            response_0 = notifications_v1_notification_query_service_pb2.FindNotificationsResponse()
            response_1 = pipelines_v1_pipeline_run_query_service_pb2.BrowsePipelineRunsResponse()
            outgoing_0 = notifications_v1_notification_query_service_pb2.FindNotificationsRequest(
                context=request.context,
                filter=notifications_v1_notification_query_service_pb2.FindNotificationsRequest.Filter(
                    created_after=request.context.deadline
                )
            )
            response_0 = await deps.clients.notifications_notification_query.FindNotifications(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            command_1 = AnalyticsEventQueryResolveAnalyticsEvents1Command(
                context=request.context,
                filter_owner_id=response_0.result.correlation_id
            )
            outgoing_1 = to_analytics_event_query_resolve_analytics_events1_command(command_1)
            response_1 = await deps.clients.pipelines_pipeline_run_query.BrowsePipelineRuns(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.details
            response.result.details.update(returned_0_0)
            returned_0_1 = response_0.page_info.next_page_token
            if returned_0_1:
                response.page_info.next_page_token = returned_0_1
            returned_1_0 = response_1.result.correlation_id
            if returned_1_0:
                response.result.correlation_id = returned_1_0
            returned_1_1 = response_1.result.correlation_id
            returned_1_1_part_0 = response.analytics_events.add()
            if returned_1_1:
                returned_1_1_part_0.correlation_id = returned_1_1
            return response

    async def handle_suggest_analytics_events(
        self,
        request: analytics_v1_analytics_event_query_service_pb2.SuggestAnalyticsEventsRequest
    ) -> analytics_v1_analytics_event_query_service_pb2.SuggestAnalyticsEventsResponse:
        """Lists analytics events a page at a time."""
        deps = self.deps
        response = analytics_v1_analytics_event_query_service_pb2.SuggestAnalyticsEventsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SuggestAnalyticsEvents', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'SuggestAnalyticsEvents',
                {'order_by': request.order_by}
            )
            return response

    async def handle_summarize_analytics_events(
        self,
        request: analytics_v1_analytics_event_query_service_pb2.SummarizeAnalyticsEventsRequest
    ) -> analytics_v1_analytics_event_query_service_pb2.SummarizeAnalyticsEventsResponse:
        """Summarizes an analytics event."""
        deps = self.deps
        response = analytics_v1_analytics_event_query_service_pb2.SummarizeAnalyticsEventsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SummarizeAnalyticsEvents', extra={'fields': {'analytics_event_id': request.analytics_event_id}})
            await deps.repository.audit(
                request.context.tenant_id,
                'SummarizeAnalyticsEvents',
                {'analytics_event_id': request.analytics_event_id}
            )
            response_0 = anomalies_v1_anomaly_feedback_validation_service_pb2.NormalizeAnomalyFeedbackResponse()
            command_0 = AnalyticsEventQuerySummarizeAnalyticsEvents0Command.model_validate(
                {
                    'context': request.context,
                    'annotations': dict(request.annotations),
                    'details_contact_email': request.context.actor.email,
                    'reason': request.reason,
                    'details_locale': request.context.locale
                }
            )
            outgoing_0 = to_analytics_event_query_summarize_analytics_events0_command(command_0)
            response_0 = await deps.clients.anomalies_anomaly_feedback_validation.NormalizeAnomalyFeedback(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_0)
            echoed_0 = request.details.period
            response.period.CopyFrom(echoed_0)
            return response
