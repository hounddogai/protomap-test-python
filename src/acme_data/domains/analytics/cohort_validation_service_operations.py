"""Functional operations behind CohortValidationService."""

from __future__ import annotations

from collections.abc import Awaitable
from collections.abc import Callable
import asyncio
import logging

from google.protobuf.any_pb2 import Any as AnyMessage
from google.protobuf.json_format import MessageToJson
from google.protobuf.json_format import Parse

from acme.analytics.v1 import analytics_pb2 as analytics_v1_analytics_pb2
from acme.analytics.v1 import (
    analytics_report_calculation_service_pb2 as analytics_v1_analytics_report_calculation_service_pb2,
)
from acme.analytics.v1 import cohort_calculation_service_pb2 as analytics_v1_cohort_calculation_service_pb2
from acme.analytics.v1 import cohort_validation_service_pb2 as analytics_v1_cohort_validation_service_pb2
from acme.analytics.v1 import funnel_calculation_service_pb2 as analytics_v1_funnel_calculation_service_pb2
from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.customers.v1 import refs_pb2 as customers_v1_refs_pb2
from acme.drivers.v1 import refs_pb2 as drivers_v1_refs_pb2
from acme.featurestore.v1 import feature_value_query_service_pb2 as featurestore_v1_feature_value_query_service_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.maintenance.v1 import maintenance_pb2 as maintenance_v1_maintenance_pb2
from acme.maintenance.v1 import work_order_calculation_service_pb2 as maintenance_v1_work_order_calculation_service_pb2
from acme.metrics.v1 import dashboard_history_service_pb2 as metrics_v1_dashboard_history_service_pb2
from acme.metrics.v1 import metric_series_query_service_pb2 as metrics_v1_metric_series_query_service_pb2
from acme.metrics.v1 import metrics_pb2 as metrics_v1_metrics_pb2
from acme.notifications.v1 import notification_query_service_pb2 as notifications_v1_notification_query_service_pb2
from acme.pipelines.v1 import pipeline_run_validation_service_pb2 as pipelines_v1_pipeline_run_validation_service_pb2
from acme.pipelines.v1 import pipelines_pb2 as pipelines_v1_pipelines_pb2
from acme.search.v1 import search_index_query_service_pb2 as search_v1_search_index_query_service_pb2

from acme_data.domains.analytics.dependencies import Dependencies
from acme_data.domains.analytics.models import CohortValidationPreviewCohort1Command
from acme_data.domains.analytics.models import to_cohort_validation_preview_cohort1_command
from acme_data.platform.rpc import async_messages
from acme_data.platform.tenancy import tenant_id
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


async def handle_check_cohort_eligibility(
    deps: Dependencies,
    request: analytics_v1_cohort_validation_service_pb2.CheckCohortEligibilityRequest
) -> analytics_v1_cohort_validation_service_pb2.CheckCohortEligibilityResponse:
    """Checks a cohort."""
    response = analytics_v1_cohort_validation_service_pb2.CheckCohortEligibilityResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('CheckCohortEligibility', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'CheckCohortEligibility', {'reason': request.reason})
        await deps.repository.save_cohort(request.context.tenant_id, request.cohort)
        response_0 = metrics_v1_metric_series_query_service_pb2.SummarizeMetricSeriesesResponse()
        response_1 = metrics_v1_metric_series_query_service_pb2.CountMetricSeriesesResponse()
        outgoing_0 = metrics_v1_metric_series_query_service_pb2.SummarizeMetricSeriesesRequest(
            context=request.context,
            reason=request.cohort.block.reason
        )
        response_0 = await deps.clients.metrics_metric_series_query.SummarizeMetricSerieses(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = metrics_v1_metric_series_query_service_pb2.CountMetricSeriesesRequest(
            context=request.context,
            filter=metrics_v1_metric_series_query_service_pb2.CountMetricSeriesesRequest.Filter(
                created_after=request.cohort.audit.updated_at,
                labels=dict(request.cohort.parameters),
                owner_id=request.cohort.owner.user_id
            )
        )
        method_name_1 = 'CountMetricSerieses'
        response_1 = await getattr(
            deps.clients.metrics_metric_series_query,
            method_name_1
        )(outgoing_1, timeout=deps.settings.timeout)
        returned_0_0 = response_0.result.status
        if returned_0_0:
            response.result.status = returned_0_0
        returned_0_1 = response_0.result.message
        if returned_0_1:
            response.outcome.message = returned_0_1
        returned_1_0 = response_1.result.details
        response.result.details.update(returned_1_0)
        returned_1_1 = response_1.result.correlation_id
        if returned_1_1:
            response.result.correlation_id = returned_1_1
        echoed_0 = request.cohort_id
        response.cohort.cohort_id = echoed_0
        echoed_1 = request.cohort.description
        response.cohort.description = echoed_1
        return response


async def handle_get_cohort_rules(
    deps: Dependencies,
    request: analytics_v1_cohort_validation_service_pb2.GetCohortRulesRequest
) -> analytics_v1_cohort_validation_service_pb2.GetCohortRulesResponse:
    """Returns a cohort."""
    response = analytics_v1_cohort_validation_service_pb2.GetCohortRulesResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('GetCohortRules', extra={'fields': {'domain': 'analytics'}})
        await deps.repository.audit(request.context.tenant_id, 'GetCohortRules', {})
        response_0 = analytics_v1_analytics_report_calculation_service_pb2.CompareAnalyticsReportOptionsResponse()
        outgoing_0 = analytics_v1_analytics_report_calculation_service_pb2.CompareAnalyticsReportOptionsRequest(
            analytics_report=analytics_v1_analytics_pb2.AnalyticsReport(
                audit=common_v1_audit_pb2.AuditInfo(updated_at=request.context.deadline),
                counterparty=customers_v1_refs_pb2.CustomerRef(email=request.context.actor.email)
            ),
            context=request.context
        )
        response_0 = await deps.clients.analytics_analytics_report_calculation.CompareAnalyticsReportOptions(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.result.reference_ids
        response.result.reference_ids.extend(returned_0_0)
        echoed_0 = request.cohort_id
        response.cohort.cohort_id = echoed_0
        return response


async def handle_normalize_cohort(
    deps: Dependencies,
    request: analytics_v1_cohort_validation_service_pb2.NormalizeCohortRequest
) -> analytics_v1_cohort_validation_service_pb2.NormalizeCohortResponse:
    """Normalizes a cohort."""
    response = analytics_v1_cohort_validation_service_pb2.NormalizeCohortResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('NormalizeCohort', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'NormalizeCohort', {'reason': request.reason})
        await deps.repository.save_cohort(request.context.tenant_id, request.cohort)
        response_0 = analytics_v1_funnel_calculation_service_pb2.SimulateFunnelResponse()
        response_1 = maintenance_v1_work_order_calculation_service_pb2.SimulateWorkOrderResponse()
        response_2 = analytics_v1_analytics_report_calculation_service_pb2.QuoteAnalyticsReportResponse()
        response_3 = metrics_v1_dashboard_history_service_pb2.RevertDashboardResponse()
        outgoing_0 = analytics_v1_funnel_calculation_service_pb2.SimulateFunnelRequest(
            context=request.context,
            funnel=analytics_v1_analytics_pb2.Funnel(
                audit=common_v1_audit_pb2.AuditInfo(updated_at=request.cohort.audit.updated_at),
                owner=identity_v1_refs_pb2.UserRef(email=request.cohort.owner.email)
            )
        )
        response_0 = await deps.clients.analytics_funnel_calculation.SimulateFunnel(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = maintenance_v1_work_order_calculation_service_pb2.SimulateWorkOrderRequest(
            context=request.context,
            work_order=maintenance_v1_maintenance_pb2.WorkOrder(
                assignee=identity_v1_refs_pb2.UserRef(email=request.details.contact.email),
                audit=common_v1_audit_pb2.AuditInfo(etag=request.cohort.audit.etag),
                customer=drivers_v1_refs_pb2.DriverRef(display_name=response_0.funnel.owner.display_name)
            )
        )
        document_1 = MessageToJson(outgoing_1, preserving_proto_field_name=True)
        outgoing_1 = Parse(document_1, maintenance_v1_work_order_calculation_service_pb2.SimulateWorkOrderRequest())
        response_1 = await deps.clients.maintenance_work_order_calculation.SimulateWorkOrder(
            outgoing_1,
            timeout=deps.settings.timeout
        )
        outgoing_2 = analytics_v1_analytics_report_calculation_service_pb2.QuoteAnalyticsReportRequest()
        outgoing_2.context.CopyFrom(request.context)
        field_2_1_part_1 = outgoing_2.analytics_report.lines.add()
        field_2_1_part_1.tax.amount.CopyFrom(request.cohort.discount.amount)
        merged_2 = analytics_v1_analytics_report_calculation_service_pb2.QuoteAnalyticsReportRequest()
        merged_2.MergeFrom(outgoing_2)
        outgoing_2.CopyFrom(merged_2)
        response_2 = await deps.clients.analytics_analytics_report_calculation.QuoteAnalyticsReport(
            outgoing_2,
            timeout=deps.settings.timeout
        )
        outgoing_3 = metrics_v1_dashboard_history_service_pb2.RevertDashboardRequest(
            context=request.context,
            dashboard=metrics_v1_metrics_pb2.Dashboard(
                audit=common_v1_audit_pb2.AuditInfo(
                    created_at=request.cohort.audit.created_at,
                    updated_at=response_0.funnel.audit.updated_at
                ),
                bank=metrics_v1_metrics_pb2.DashboardBankSettlement(
                    account_holder=response_2.analytics_report.bank.account_holder
                ),
                billing_address=common_v1_address_pb2.PostalAddress(
                    lines=list(response_2.analytics_report.billing_address.lines)
                )
            )
        )
        envelope_3 = AnyMessage()
        envelope_3.Pack(outgoing_3)
        outgoing_3 = metrics_v1_dashboard_history_service_pb2.RevertDashboardRequest()
        if not envelope_3.Unpack(outgoing_3):
            raise ValueError("partner envelope contains the wrong request type")
        response_3 = await deps.clients.metrics_dashboard_history.RevertDashboard(
            outgoing_3,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.funnel.owner
        if returned_0_0.ListFields():
            response.cohort.owner.MergeFrom(returned_0_0)
        returned_1_0 = response_1.work_order.assignee.user_id
        if returned_1_0:
            response.cohort.owner.user_id = returned_1_0
        returned_2_0 = response_2.analytics_report.audit.created_by
        if returned_2_0:
            response.cohort.audit.created_by = returned_2_0
        returned_3_0 = response_3.outcome.status
        if returned_3_0:
            response.result.status = returned_3_0
        echoed_0 = request.cohort_id
        response.cohort.cohort_id = echoed_0
        echoed_1 = request.cohort.effective
        response.cohort.effective.CopyFrom(echoed_1)
        return response


async def handle_preview_cohort(
    deps: Dependencies,
    request: analytics_v1_cohort_validation_service_pb2.PreviewCohortRequest
) -> analytics_v1_cohort_validation_service_pb2.PreviewCohortResponse:
    """Previews a cohort."""
    response = analytics_v1_cohort_validation_service_pb2.PreviewCohortResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('PreviewCohort', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'PreviewCohort', {'reason': request.reason})
        await deps.repository.save_cohort(request.context.tenant_id, request.cohort)
        response_0 = featurestore_v1_feature_value_query_service_pb2.ExportFeatureValuesResponse()
        response_1 = notifications_v1_notification_query_service_pb2.BrowseNotificationsResponse()
        outgoing_0 = featurestore_v1_feature_value_query_service_pb2.ExportFeatureValuesRequest(
            context=request.context,
            filter=featurestore_v1_feature_value_query_service_pb2.ExportFeatureValuesRequest.Filter(
                created_after=request.cohort.audit.updated_at,
                owner_id=request.cohort.owner.user_id
            )
        )
        async for chunk_0 in deps.clients.featurestore_feature_value_query.ExportFeatureValues(
            outgoing_0,
            timeout=deps.settings.timeout
        ):
            response_0 = chunk_0
        command_1 = CohortValidationPreviewCohort1Command(
            context=request.context,
            filter_created_after=request.cohort.audit.created_at,
            filter_owner_id=request.cohort.owner.user_id,
            filter_labels=dict(request.cohort.parameters)
        )
        outgoing_1 = to_cohort_validation_preview_cohort1_command(command_1)
        response_1 = await deps.clients.notifications_notification_query.BrowseNotifications(
            outgoing_1,
            timeout=deps.settings.timeout
        )
        returned_1_0 = response_1.result.message
        if returned_1_0:
            response.result.message = returned_1_0
        echoed_0 = request.cohort_id
        response.cohort.cohort_id = echoed_0
        echoed_1 = request.cohort.priority
        response.cohort.priority = echoed_1
        return response


async def handle_score_cohort(
    deps: Dependencies,
    request: analytics_v1_cohort_validation_service_pb2.ScoreCohortRequest
) -> analytics_v1_cohort_validation_service_pb2.ScoreCohortResponse:
    """Scores a cohort."""
    response = analytics_v1_cohort_validation_service_pb2.ScoreCohortResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('ScoreCohort', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'ScoreCohort', {'reason': request.reason})
        await deps.repository.save_cohort(request.context.tenant_id, request.cohort)
        response_0 = pipelines_v1_pipeline_run_validation_service_pb2.NormalizePipelineRunResponse()
        response_1 = analytics_v1_analytics_report_calculation_service_pb2.CalculateAnalyticsReportResponse()
        outgoing_0 = pipelines_v1_pipeline_run_validation_service_pb2.NormalizePipelineRunRequest(
            context=request.context,
            pipeline_run=pipelines_v1_pipelines_pb2.PipelineRun(
                assignee=identity_v1_refs_pb2.UserRef(
                    display_name=request.cohort.owner.display_name,
                    email=request.cohort.block.notify_email
                ),
                audit=common_v1_audit_pb2.AuditInfo(created_at=request.cohort.audit.created_at),
                requester=common_v1_contact_pb2.ContactInfo(email=request.cohort.owner.email)
            )
        )
        response_0 = await deps.clients.pipelines_pipeline_run_validation.NormalizePipelineRun(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = analytics_v1_analytics_report_calculation_service_pb2.CalculateAnalyticsReportRequest()
        outgoing_1.context.CopyFrom(request.context)
        if request.cohort.WhichOneof('action') == 'discount':
            field_1_1_part_1 = outgoing_1.analytics_report.lines.add()
            field_1_1_part_1.amount.CopyFrom(request.cohort.discount.amount)
        outgoing_1.details.destination.recipient = request.details.destination.recipient
        response_1 = await deps.clients.analytics_analytics_report_calculation.CalculateAnalyticsReport(
            outgoing_1,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.outcome.message
        if returned_0_0:
            response.result.message = returned_0_0
        returned_1_0 = response_1.analytics_report.audit.etag
        if returned_1_0:
            response.cohort.audit.etag = returned_1_0
        echoed_0 = request.cohort_id
        response.cohort.cohort_id = echoed_0
        echoed_1 = request.cohort.effective
        response.cohort.effective.CopyFrom(echoed_1)
        return response


async def handle_validate_cohort(
    deps: Dependencies,
    request: analytics_v1_cohort_validation_service_pb2.ValidateCohortRequest
) -> analytics_v1_cohort_validation_service_pb2.ValidateCohortResponse:
    """Validates a cohort."""
    response = analytics_v1_cohort_validation_service_pb2.ValidateCohortResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('ValidateCohort', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'ValidateCohort', {'reason': request.reason})
        await deps.repository.save_cohort(request.context.tenant_id, request.cohort)
        response_0 = analytics_v1_cohort_calculation_service_pb2.QuoteCohortResponse()
        response_1 = search_v1_search_index_query_service_pb2.SummarizeSearchIndexesResponse()
        async for item_0 in async_messages(request.cohort.conditions):
            outgoing_0 = analytics_v1_cohort_calculation_service_pb2.QuoteCohortRequest(
                cohort=analytics_v1_analytics_pb2.Cohort(
                    conditions=[
                        analytics_v1_analytics_pb2.CohortCondition(
                            attribute=item_0.attribute,
                            negate=item_0.negate,
                            operator=item_0.operator,
                            value=item_0.value
                        )
                    ]
                ),
                context=request.context
            )
            response_0 = await deps.clients.analytics_cohort_calculation.QuoteCohort(
                outgoing_0,
                timeout=deps.settings.timeout
            )
        outgoing_1 = search_v1_search_index_query_service_pb2.SummarizeSearchIndexesRequest()
        outgoing_1.context.CopyFrom(request.context)
        outgoing_1.reason = response_0.cohort.block.reason
        outgoing_1.annotations.update(dict(request.annotations))
        outgoing_1.context.tenant_id = tenant_id.get()
        response_1 = await deps.clients.search_search_index_query.SummarizeSearchIndexes(
            outgoing_1,
            timeout=deps.settings.timeout
        )
        returned_1_0 = response_1.result.message
        if returned_1_0:
            response.outcome.message = returned_1_0
        echoed_0 = request.cohort_id
        response.cohort.cohort_id = echoed_0
        echoed_1 = request.cohort.name
        response.cohort.name = echoed_1
        return response
