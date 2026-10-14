"""Application workflow for AnalyticsReport Calculation."""

from __future__ import annotations

from collections.abc import Awaitable
from collections.abc import Callable
from functools import partial
from typing import cast
import asyncio
import logging

from google.protobuf.json_format import MessageToDict
from google.protobuf.json_format import MessageToJson
from google.protobuf.json_format import Parse
from google.protobuf.json_format import ParseDict

from acme.analytics.v1 import analytics_pb2 as analytics_v1_analytics_pb2
from acme.analytics.v1 import (
    analytics_report_calculation_service_pb2 as analytics_v1_analytics_report_calculation_service_pb2,
)
from acme.analytics.v1 import cohort_calculation_service_pb2 as analytics_v1_cohort_calculation_service_pb2
from acme.analytics.v1 import funnel_validation_service_pb2 as analytics_v1_funnel_validation_service_pb2
from acme.appointments.v1 import appointment_query_service_pb2 as appointments_v1_appointment_query_service_pb2
from acme.audit.v1 import audit_event_service_pb2 as audit_v1_audit_event_service_pb2
from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.featureflags.v1 import feature_flag_service_pb2 as featureflags_v1_feature_flag_service_pb2
from acme.featurestore.v1 import (
    feature_view_validation_service_pb2 as featurestore_v1_feature_view_validation_service_pb2,
)
from acme.featurestore.v1 import featurestore_pb2 as featurestore_v1_featurestore_pb2
from acme.metrics.v1 import dashboard_validation_service_pb2 as metrics_v1_dashboard_validation_service_pb2
from acme.metrics.v1 import metric_alert_notification_service_pb2 as metrics_v1_metric_alert_notification_service_pb2
from acme.metrics.v1 import metrics_pb2 as metrics_v1_metrics_pb2
from acme.ratelimiting.v1 import rate_limit_query_service_pb2 as ratelimiting_v1_rate_limit_query_service_pb2

from acme_data.domains.analytics.adapters import AnalyticsReportCalculationCalculateAnalyticsReport1Adapter
from acme_data.domains.analytics.adapters import AnalyticsReportCalculationCalculateAnalyticsReport1Port
from acme_data.domains.analytics.adapters import AnalyticsReportCalculationCompareAnalyticsReportOptions0Adapter
from acme_data.domains.analytics.dependencies import Dependencies
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import run_steps
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class AnalyticsReportCalculationServicerWorkflow:
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    async def handle_calculate_analytics_report(
        self,
        request: analytics_v1_analytics_report_calculation_service_pb2.CalculateAnalyticsReportRequest
    ) -> analytics_v1_analytics_report_calculation_service_pb2.CalculateAnalyticsReportResponse:
        """Calculates an analytics report."""
        deps = self.deps
        response = analytics_v1_analytics_report_calculation_service_pb2.CalculateAnalyticsReportResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CalculateAnalyticsReport', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'CalculateAnalyticsReport',
                {'reason': request.reason}
            )
            await deps.repository.save_analytics_report(request.context.tenant_id, request.analytics_report)
            response_0 = appointments_v1_appointment_query_service_pb2.ExportAppointmentsResponse()
            response_1 = featurestore_v1_feature_view_validation_service_pb2.CheckFeatureViewEligibilityResponse()
            response_2 = audit_v1_audit_event_service_pb2.BatchGetAuditEventsResponse()
            outgoing_0 = appointments_v1_appointment_query_service_pb2.ExportAppointmentsRequest(
                context=request.context,
                filter=appointments_v1_appointment_query_service_pb2.ExportAppointmentsRequest.Filter(
                    created_after=request.analytics_report.issued_at,
                    region=request.details.destination.region
                )
            )
            async for chunk_0 in deps.clients.appointments_appointment_query.ExportAppointments(
                outgoing_0,
                timeout=deps.settings.timeout
            ):
                response_0 = chunk_0
            outgoing_1 = featurestore_v1_feature_view_validation_service_pb2.CheckFeatureViewEligibilityRequest(
                context=request.context,
                details=featurestore_v1_feature_view_validation_service_pb2.CheckFeatureViewEligibilityRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(email=request.analytics_report.counterparty.email)
                ),
                feature_view=featurestore_v1_featurestore_pb2.FeatureView(
                    address=common_v1_address_pb2.PostalAddress(
                        country_code=request.analytics_report.billing_address.country_code,
                        postal_code=request.details.destination.postal_code
                    ),
                    audit=common_v1_audit_pb2.AuditInfo(etag=request.analytics_report.audit.etag)
                )
            )
            port_1: AnalyticsReportCalculationCalculateAnalyticsReport1Port = AnalyticsReportCalculationCalculateAnalyticsReport1Adapter(
                deps.clients.featurestore_feature_view_validation,
                deps.settings.timeout
            )
            response_1 = await port_1.execute(outgoing_1)
            outgoing_2 = audit_v1_audit_event_service_pb2.BatchGetAuditEventsRequest(context=request.context)
            steps_2 = [
                partial(deps.clients.audit_audit_event.BatchGetAuditEvents, outgoing_2, timeout=deps.settings.timeout)
            ]
            results_2 = await run_steps(steps_2)
            response_2 = results_2[-1]
            returned_1_0 = response_1.outcome.status
            if returned_1_0:
                response.result.status = returned_1_0
            returned_1_1 = response_1.feature_view.audit.updated_at
            if returned_1_1.ListFields():
                response.analytics_report.audit.updated_at.MergeFrom(returned_1_1)
            returned_2_0 = response_2.result.reference_ids
            response.result.reference_ids.extend(returned_2_0)
            returned_2_1 = response_2.result.status
            if returned_2_1:
                response.result.status = returned_2_1
            echoed_0 = request.analytics_report_id
            response.analytics_report.analytics_report_id = echoed_0
            echoed_1 = request.analytics_report.number
            response.analytics_report.number = echoed_1
            return response

    async def handle_compare_analytics_report_options(
        self,
        request: analytics_v1_analytics_report_calculation_service_pb2.CompareAnalyticsReportOptionsRequest
    ) -> analytics_v1_analytics_report_calculation_service_pb2.CompareAnalyticsReportOptionsResponse:
        """Compares an analytics report."""
        deps = self.deps
        response = analytics_v1_analytics_report_calculation_service_pb2.CompareAnalyticsReportOptionsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CompareAnalyticsReportOptions', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'CompareAnalyticsReportOptions',
                {'reason': request.reason}
            )
            await deps.repository.save_analytics_report(request.context.tenant_id, request.analytics_report)
            response_0 = analytics_v1_funnel_validation_service_pb2.CheckFunnelEligibilityResponse()
            outgoing_0 = analytics_v1_funnel_validation_service_pb2.CheckFunnelEligibilityRequest(
                context=request.context,
                funnel=analytics_v1_analytics_pb2.Funnel(
                    audit=common_v1_audit_pb2.AuditInfo(etag=request.analytics_report.audit.etag)
                )
            )
            response_0 = await AnalyticsReportCalculationCompareAnalyticsReportOptions0Adapter(
                deps.clients.analytics_funnel_validation,
                deps.settings.timeout
            )(outgoing_0)
            returned_0_0 = response_0.funnel.discount.amount
            returned_0_0_part_1 = response.breakdown.lines.add()
            if returned_0_0.ListFields():
                returned_0_0_part_1.amount.MergeFrom(returned_0_0)
            echoed_0 = request.analytics_report_id
            response.analytics_report.analytics_report_id = echoed_0
            echoed_1 = request.details.currency_code
            response.breakdown.currency_code = echoed_1
            return response

    async def handle_estimate_analytics_report(
        self,
        request: analytics_v1_analytics_report_calculation_service_pb2.EstimateAnalyticsReportRequest
    ) -> analytics_v1_analytics_report_calculation_service_pb2.EstimateAnalyticsReportResponse:
        """Estimates an analytics report."""
        deps = self.deps
        response = analytics_v1_analytics_report_calculation_service_pb2.EstimateAnalyticsReportResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('EstimateAnalyticsReport', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'EstimateAnalyticsReport',
                {'reason': request.reason}
            )
            await deps.repository.save_analytics_report(request.context.tenant_id, request.analytics_report)
            response_0 = featureflags_v1_feature_flag_service_pb2.BatchGetFeatureFlagsResponse()
            response_1 = ratelimiting_v1_rate_limit_query_service_pb2.ExportRateLimitsResponse()
            outgoing_0 = featureflags_v1_feature_flag_service_pb2.BatchGetFeatureFlagsRequest(context=request.context)
            response_0 = cast(featureflags_v1_feature_flag_service_pb2.BatchGetFeatureFlagsResponse, await deps.bus.request(
                'acme.analytics.v1.AnalyticsReportCalculationService/EstimateAnalyticsReport/0', outgoing_0, deps.settings.timeout,
            ))
            outgoing_1 = ratelimiting_v1_rate_limit_query_service_pb2.ExportRateLimitsRequest(
                context=request.context,
                filter=ratelimiting_v1_rate_limit_query_service_pb2.ExportRateLimitsRequest.Filter(
                    created_after=request.analytics_report.audit.updated_at,
                    owner_id=request.analytics_report.analytics_report_id,
                    region=request.analytics_report.billing_address.region
                )
            )
            async for chunk_1 in deps.clients.ratelimiting_rate_limit_query.ExportRateLimits(
                outgoing_1,
                timeout=deps.settings.timeout
            ):
                response_1 = chunk_1
            returned_0_0 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_0)
            echoed_0 = request.analytics_report_id
            response.analytics_report.analytics_report_id = echoed_0
            echoed_1 = request.analytics_report.total
            response.breakdown.total.CopyFrom(echoed_1)
            return response

    async def handle_explain_analytics_report_calculation(
        self,
        request: analytics_v1_analytics_report_calculation_service_pb2.ExplainAnalyticsReportCalculationRequest
    ) -> analytics_v1_analytics_report_calculation_service_pb2.ExplainAnalyticsReportCalculationResponse:
        """Explains an analytics report."""
        deps = self.deps
        response = analytics_v1_analytics_report_calculation_service_pb2.ExplainAnalyticsReportCalculationResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ExplainAnalyticsReportCalculation', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ExplainAnalyticsReportCalculation',
                {'reason': request.reason}
            )
            await deps.repository.save_analytics_report(request.context.tenant_id, request.analytics_report)
            response_0 = metrics_v1_dashboard_validation_service_pb2.LintDashboardsResponse()
            response_1 = metrics_v1_metric_alert_notification_service_pb2.StreamMetricAlertNoticesResponse()
            outgoing_0 = metrics_v1_dashboard_validation_service_pb2.LintDashboardsRequest(
                context=request.context,
                dashboard=metrics_v1_metrics_pb2.Dashboard(
                    billing_address=common_v1_address_pb2.PostalAddress(
                        postal_code=request.analytics_report.billing_address.postal_code
                    )
                ),
                details=metrics_v1_dashboard_validation_service_pb2.LintDashboardsRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(
                        email=request.analytics_report.counterparty.email,
                        phone=request.details.contact.phone
                    )
                )
            )
            method_name_0 = 'LintDashboards'
            response_0 = await getattr(
                deps.clients.metrics_dashboard_validation,
                method_name_0
            )(outgoing_0, timeout=deps.settings.timeout)
            outgoing_1 = metrics_v1_metric_alert_notification_service_pb2.StreamMetricAlertNoticesRequest(
                context=request.context,
                filter=metrics_v1_metric_alert_notification_service_pb2.StreamMetricAlertNoticesRequest.Filter(
                    region=request.analytics_report.billing_address.region
                ),
                subscriber=common_v1_contact_pb2.ContactInfo(
                    email=request.details.contact.email,
                    name=request.details.contact.name,
                    phone=request.details.contact.phone
                )
            )
            async for chunk_1 in deps.clients.metrics_metric_alert_notification.StreamMetricAlertNotices(
                outgoing_1,
                timeout=deps.settings.timeout
            ):
                response_1 = chunk_1
            returned_0_0 = response_0.dashboard.billing_address.region
            if returned_0_0:
                response.analytics_report.billing_address.region = returned_0_0
            echoed_0 = request.analytics_report_id
            response.analytics_report.analytics_report_id = echoed_0
            echoed_1 = request.analytics_report.total
            response.analytics_report.total.CopyFrom(echoed_1)
            return response

    async def handle_quote_analytics_report(
        self,
        request: analytics_v1_analytics_report_calculation_service_pb2.QuoteAnalyticsReportRequest
    ) -> analytics_v1_analytics_report_calculation_service_pb2.QuoteAnalyticsReportResponse:
        """Quotes an analytics report."""
        deps = self.deps
        response = analytics_v1_analytics_report_calculation_service_pb2.QuoteAnalyticsReportResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('QuoteAnalyticsReport', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'QuoteAnalyticsReport', {'reason': request.reason})
            await deps.repository.save_analytics_report(request.context.tenant_id, request.analytics_report)
            response_0 = analytics_v1_funnel_validation_service_pb2.NormalizeFunnelResponse()
            outgoing_0 = analytics_v1_funnel_validation_service_pb2.NormalizeFunnelRequest(
                context=request.context,
                funnel=analytics_v1_analytics_pb2.Funnel(
                    audit=common_v1_audit_pb2.AuditInfo(updated_by=request.analytics_report.audit.updated_by)
                )
            )
            document_0 = MessageToDict(outgoing_0, preserving_proto_field_name=True)
            outgoing_0 = ParseDict(document_0, analytics_v1_funnel_validation_service_pb2.NormalizeFunnelRequest())
            response_0 = await deps.clients.analytics_funnel_validation.NormalizeFunnel(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.funnel.audit.updated_by
            if returned_0_0:
                response.analytics_report.audit.updated_by = returned_0_0
            returned_0_1 = response_0.result.message
            if returned_0_1:
                response.result.message = returned_0_1
            echoed_0 = request.analytics_report_id
            response.analytics_report.analytics_report_id = echoed_0
            echoed_1 = request.analytics_report.due_at
            response.analytics_report.due_at.CopyFrom(echoed_1)
            return response

    async def handle_recalculate_analytics_reports(
        self,
        request: analytics_v1_analytics_report_calculation_service_pb2.RecalculateAnalyticsReportsRequest
    ) -> analytics_v1_analytics_report_calculation_service_pb2.RecalculateAnalyticsReportsResponse:
        """Recalculates an analytics report."""
        deps = self.deps
        response = analytics_v1_analytics_report_calculation_service_pb2.RecalculateAnalyticsReportsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('RecalculateAnalyticsReports', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'RecalculateAnalyticsReports',
                {'reason': request.reason}
            )
            await deps.repository.save_analytics_report(request.context.tenant_id, request.analytics_report)
            response_0 = analytics_v1_cohort_calculation_service_pb2.SimulateCohortResponse()
            outgoing_0 = analytics_v1_cohort_calculation_service_pb2.SimulateCohortRequest(
                cohort=analytics_v1_analytics_pb2.Cohort(
                    audit=common_v1_audit_pb2.AuditInfo(updated_at=request.analytics_report.audit.updated_at)
                ),
                context=request.context,
                details=analytics_v1_cohort_calculation_service_pb2.SimulateCohortRequest.Details(
                    destination=common_v1_address_pb2.PostalAddress(
                        lines=list(request.analytics_report.billing_address.lines),
                        locality=request.analytics_report.billing_address.locality
                    )
                )
            )
            document_0 = MessageToJson(outgoing_0, preserving_proto_field_name=True)
            outgoing_0 = Parse(document_0, analytics_v1_cohort_calculation_service_pb2.SimulateCohortRequest())
            response_0 = await deps.clients.analytics_cohort_calculation.SimulateCohort(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.cohort.description
            returned_0_0_part_1 = response.analytics_report.lines.add()
            if returned_0_0:
                returned_0_0_part_1.description = returned_0_0
            returned_0_1 = response_0.cohort.audit.created_by
            if returned_0_1:
                response.analytics_report.audit.created_by = returned_0_1
            echoed_0 = request.analytics_report_id
            response.analytics_report.analytics_report_id = echoed_0
            echoed_1 = request.analytics_report.number
            response.analytics_report.number = echoed_1
            return response

    async def handle_simulate_analytics_report(
        self,
        request: analytics_v1_analytics_report_calculation_service_pb2.SimulateAnalyticsReportRequest
    ) -> analytics_v1_analytics_report_calculation_service_pb2.SimulateAnalyticsReportResponse:
        """Simulates an analytics report."""
        deps = self.deps
        response = analytics_v1_analytics_report_calculation_service_pb2.SimulateAnalyticsReportResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SimulateAnalyticsReport', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'SimulateAnalyticsReport',
                {'reason': request.reason}
            )
            await deps.repository.save_analytics_report(request.context.tenant_id, request.analytics_report)
            response_0 = analytics_v1_cohort_calculation_service_pb2.ExplainCohortCalculationResponse()
            response_1 = analytics_v1_cohort_calculation_service_pb2.SimulateCohortResponse()
            outgoing_0 = analytics_v1_cohort_calculation_service_pb2.ExplainCohortCalculationRequest()
            outgoing_0.context.CopyFrom(request.context)
            outgoing_0.details.contact.email = request.analytics_report.counterparty.email
            merged_0 = analytics_v1_cohort_calculation_service_pb2.ExplainCohortCalculationRequest()
            merged_0.MergeFrom(outgoing_0)
            outgoing_0.CopyFrom(merged_0)
            response_0 = await deps.clients.analytics_cohort_calculation.ExplainCohortCalculation(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            async for item_1 in async_messages(request.analytics_report.lines):
                outgoing_1 = analytics_v1_cohort_calculation_service_pb2.SimulateCohortRequest(
                    cohort=analytics_v1_analytics_pb2.Cohort(
                        discount=analytics_v1_analytics_pb2.CohortDiscountAction(amount=item_1.amount)
                    ),
                    context=request.context
                )
                response_1 = await deps.clients.analytics_cohort_calculation.SimulateCohort(
                    outgoing_1,
                    timeout=deps.settings.timeout
                )
            returned_0_0 = response_0.result.details
            response.result.details.update(returned_0_0)
            returned_0_1 = response_0.cohort.audit.created_at
            if returned_0_1.ListFields():
                response.analytics_report.audit.created_at.MergeFrom(returned_0_1)
            echoed_0 = request.analytics_report_id
            response.analytics_report.analytics_report_id = echoed_0
            echoed_1 = request.analytics_report.status
            response.analytics_report.status = echoed_1
            return response
