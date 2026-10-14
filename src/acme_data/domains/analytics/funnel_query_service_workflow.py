"""Application workflow for Funnel Query."""

from __future__ import annotations

from typing import Any
import logging

from google.protobuf.json_format import MessageToDict
from google.protobuf.json_format import MessageToJson
from google.protobuf.json_format import Parse
from google.protobuf.json_format import ParseDict

from acme.analytics.v1 import analytics_pb2 as analytics_v1_analytics_pb2
from acme.analytics.v1 import (
    analytics_report_validation_service_pb2 as analytics_v1_analytics_report_validation_service_pb2,
)
from acme.analytics.v1 import cohort_calculation_service_pb2 as analytics_v1_cohort_calculation_service_pb2
from acme.analytics.v1 import cohort_validation_service_pb2 as analytics_v1_cohort_validation_service_pb2
from acme.analytics.v1 import funnel_query_service_pb2 as analytics_v1_funnel_query_service_pb2
from acme.analytics.v1 import funnel_validation_service_pb2 as analytics_v1_funnel_validation_service_pb2
from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.common.v1 import paging_pb2 as common_v1_paging_pb2
from acme.customers.v1 import refs_pb2 as customers_v1_refs_pb2
from acme.deliveries.v1 import delivery_query_service_pb2 as deliveries_v1_delivery_query_service_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.identity.v1 import user_query_service_pb2 as identity_v1_user_query_service_pb2
from acme.metrics.v1 import dashboard_history_service_pb2 as metrics_v1_dashboard_history_service_pb2
from acme.metrics.v1 import metrics_pb2 as metrics_v1_metrics_pb2
from acme.patients.v1 import patient_calculation_service_pb2 as patients_v1_patient_calculation_service_pb2
from acme.patients.v1 import patients_pb2 as patients_v1_patients_pb2
from acme.venues.v1 import venue_service_pb2 as venues_v1_venue_service_pb2

from acme_data.domains.analytics.dependencies import Dependencies
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class FunnelQueryServicerWorkflow:
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    async def handle_browse_funnels(
        self,
        request: analytics_v1_funnel_query_service_pb2.BrowseFunnelsRequest
    ) -> analytics_v1_funnel_query_service_pb2.BrowseFunnelsResponse:
        """Lists funnels a page at a time."""
        deps = self.deps
        response = analytics_v1_funnel_query_service_pb2.BrowseFunnelsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('BrowseFunnels', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(request.context.tenant_id, 'BrowseFunnels', {'order_by': request.order_by})
            response_0 = metrics_v1_dashboard_history_service_pb2.RevertDashboardResponse()
            outgoing_0 = metrics_v1_dashboard_history_service_pb2.RevertDashboardRequest(
                context=request.context,
                dashboard=metrics_v1_metrics_pb2.Dashboard(
                    audit=common_v1_audit_pb2.AuditInfo(updated_at=request.filter.created_after),
                    billing_address=common_v1_address_pb2.PostalAddress(region=request.filter.region),
                    metadata=dict(request.filter.labels)
                ),
                details=metrics_v1_dashboard_history_service_pb2.RevertDashboardRequest.Details(
                    author_email=request.context.actor.email
                )
            )
            response_0 = await deps.clients.metrics_dashboard_history.RevertDashboard(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.outcome.message
            if returned_0_0:
                response.result.message = returned_0_0
            return response

    async def handle_count_funnels(
        self,
        request: analytics_v1_funnel_query_service_pb2.CountFunnelsRequest
    ) -> analytics_v1_funnel_query_service_pb2.CountFunnelsResponse:
        """Counts funnels by status."""
        deps = self.deps
        response = analytics_v1_funnel_query_service_pb2.CountFunnelsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CountFunnels', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(request.context.tenant_id, 'CountFunnels', {'order_by': request.order_by})
            response_0 = deliveries_v1_delivery_query_service_pb2.CountDeliveriesResponse()
            outgoing_0 = deliveries_v1_delivery_query_service_pb2.CountDeliveriesRequest(
                context=request.context,
                filter=deliveries_v1_delivery_query_service_pb2.CountDeliveriesRequest.Filter(
                    labels=dict(request.filter.labels),
                    region=request.filter.region
                ),
                page=common_v1_paging_pb2.PageRequest(page_size=request.page.page_size)
            )
            response_0 = await deps.clients.deliveries_delivery_query.CountDeliveries(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.correlation_id
            if returned_0_0:
                response.result.correlation_id = returned_0_0
            return response

    async def handle_find_funnels(
        self,
        request: analytics_v1_funnel_query_service_pb2.FindFunnelsRequest
    ) -> analytics_v1_funnel_query_service_pb2.FindFunnelsResponse:
        """Lists funnels a page at a time."""
        deps = self.deps
        response = analytics_v1_funnel_query_service_pb2.FindFunnelsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('FindFunnels', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(request.context.tenant_id, 'FindFunnels', {'order_by': request.order_by})
            response_0 = analytics_v1_cohort_validation_service_pb2.ValidateCohortResponse()
            outgoing_0 = analytics_v1_cohort_validation_service_pb2.ValidateCohortRequest(
                cohort=analytics_v1_analytics_pb2.Cohort(
                    block=analytics_v1_analytics_pb2.CohortBlockAction(notify_email=request.context.actor.email),
                    owner=identity_v1_refs_pb2.UserRef(user_id=request.context.actor.user_id)
                ),
                context=request.context
            )
            response_0 = await deps.clients.analytics_cohort_validation.ValidateCohort(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.cohort.effective
            returned_0_0_part_0 = response.funnels.add()
            if returned_0_0.ListFields():
                returned_0_0_part_0.effective.MergeFrom(returned_0_0)
            return response

    async def handle_lookup_funnel(
        self,
        request: analytics_v1_funnel_query_service_pb2.LookupFunnelRequest
    ) -> analytics_v1_funnel_query_service_pb2.LookupFunnelResponse:
        """Returns a funnel."""
        deps = self.deps
        response = analytics_v1_funnel_query_service_pb2.LookupFunnelResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('LookupFunnel', extra={'fields': {'locale': request.context.locale}})
            await deps.repository.audit(request.context.tenant_id, 'LookupFunnel', {'locale': request.context.locale})
            echoed_0 = request.funnel_id
            response.funnel.funnel_id = echoed_0
            return response

    async def handle_peek_funnel(
        self,
        request: analytics_v1_funnel_query_service_pb2.PeekFunnelRequest
    ) -> analytics_v1_funnel_query_service_pb2.PeekFunnelResponse:
        """Returns a funnel."""
        deps = self.deps
        response = analytics_v1_funnel_query_service_pb2.PeekFunnelResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('PeekFunnel', extra={'fields': {'domain': 'analytics'}})
            await deps.repository.audit(request.context.tenant_id, 'PeekFunnel', {})
            response_0 = analytics_v1_funnel_validation_service_pb2.ScoreFunnelResponse()
            outgoing_0 = analytics_v1_funnel_validation_service_pb2.ScoreFunnelRequest(
                context=request.context,
                funnel=analytics_v1_analytics_pb2.Funnel(
                    audit=common_v1_audit_pb2.AuditInfo(updated_at=request.context.deadline),
                    block=analytics_v1_analytics_pb2.FunnelBlockAction(notify_email=request.context.actor.email),
                    funnel_id=request.funnel_id,
                    owner=identity_v1_refs_pb2.UserRef(user_id=request.context.actor.user_id)
                )
            )
            response_0 = await deps.clients.analytics_funnel_validation.ScoreFunnel(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.status
            if returned_0_0:
                response.result.status = returned_0_0
            echoed_0 = request.funnel_id
            response.funnel.funnel_id = echoed_0
            return response

    async def handle_resolve_funnels(
        self,
        request: analytics_v1_funnel_query_service_pb2.ResolveFunnelsRequest
    ) -> analytics_v1_funnel_query_service_pb2.ResolveFunnelsResponse:
        """Returns several funnels at once."""
        deps = self.deps
        response = analytics_v1_funnel_query_service_pb2.ResolveFunnelsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ResolveFunnels', extra={'fields': {'domain': 'analytics'}})
            await deps.repository.audit(request.context.tenant_id, 'ResolveFunnels', {})
            response_0 = analytics_v1_analytics_report_validation_service_pb2.ValidateAnalyticsReportResponse()
            response_1 = identity_v1_user_query_service_pb2.CountUsersResponse()
            outgoing_0 = analytics_v1_analytics_report_validation_service_pb2.ValidateAnalyticsReportRequest(
                analytics_report=analytics_v1_analytics_pb2.AnalyticsReport(
                    counterparty=customers_v1_refs_pb2.CustomerRef(email=request.context.actor.email)
                ),
                context=request.context,
                details=analytics_v1_analytics_report_validation_service_pb2.ValidateAnalyticsReportRequest.Details(
                    locale=request.context.locale
                )
            )
            response_0 = await deps.clients.analytics_analytics_report_validation.ValidateAnalyticsReport(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = identity_v1_user_query_service_pb2.CountUsersRequest(
                context=request.context,
                filter=identity_v1_user_query_service_pb2.CountUsersRequest.Filter(
                    created_after=response_0.outcome.effective_at,
                    labels=dict(response_0.analytics_report.metadata),
                    region=response_0.analytics_report.billing_address.region
                )
            )
            method_name_1 = 'CountUsers'
            response_1 = await getattr(
                deps.clients.identity_user_query,
                method_name_1
            )(outgoing_1, timeout=deps.settings.timeout)
            returned_0_0 = response_0.analytics_report.audit.etag
            returned_0_0_part_0 = response.funnels.add()
            if returned_0_0:
                returned_0_0_part_0.audit.etag = returned_0_0
            returned_0_1 = response_0.analytics_report.counterparty.display_name
            returned_0_1_part_0 = response.funnels.add()
            if returned_0_1:
                returned_0_1_part_0.owner.display_name = returned_0_1
            returned_1_0 = response_1.result.status
            if returned_1_0:
                response.result.status = returned_1_0
            return response

    async def handle_suggest_funnels(
        self,
        request: analytics_v1_funnel_query_service_pb2.SuggestFunnelsRequest
    ) -> analytics_v1_funnel_query_service_pb2.SuggestFunnelsResponse:
        """Lists funnels a page at a time."""
        deps = self.deps
        response = analytics_v1_funnel_query_service_pb2.SuggestFunnelsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SuggestFunnels', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(request.context.tenant_id, 'SuggestFunnels', {'order_by': request.order_by})
            return response

    async def handle_summarize_funnels(
        self,
        request: analytics_v1_funnel_query_service_pb2.SummarizeFunnelsRequest
    ) -> analytics_v1_funnel_query_service_pb2.SummarizeFunnelsResponse:
        """Summarizes a funnel."""
        deps = self.deps
        response = analytics_v1_funnel_query_service_pb2.SummarizeFunnelsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SummarizeFunnels', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'SummarizeFunnels', {'reason': request.reason})
            response_0 = venues_v1_venue_service_pb2.UpdateVenueResponse()
            response_1 = patients_v1_patient_calculation_service_pb2.ExplainPatientCalculationResponse()
            response_2 = analytics_v1_funnel_validation_service_pb2.CheckFunnelEligibilityResponse()
            response_3 = analytics_v1_cohort_calculation_service_pb2.SimulateCohortResponse()
            fields_0: dict[str, Any] = {
                'context': request.context,
                'venue': {
                    'components': {'primary': {'component_id': request.funnel_id}},
                    'owner': {'email': request.context.actor.email, 'user_id': request.context.actor.user_id},
                    'specs': dict(request.details.filters)
                }
            }
            outgoing_0 = venues_v1_venue_service_pb2.UpdateVenueRequest(**fields_0)
            response_0 = await deps.clients.venues_venue.UpdateVenue(outgoing_0, timeout=deps.settings.timeout)
            outgoing_1 = patients_v1_patient_calculation_service_pb2.ExplainPatientCalculationRequest(
                context=request.context,
                details=patients_v1_patient_calculation_service_pb2.ExplainPatientCalculationRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(email=response_0.venue.owner.email)
                ),
                patient=patients_v1_patients_pb2.Patient(
                    audit=common_v1_audit_pb2.AuditInfo(updated_by=response_0.venue.audit.updated_by)
                )
            )
            document_1 = MessageToDict(outgoing_1, preserving_proto_field_name=True)
            outgoing_1 = ParseDict(
                document_1,
                patients_v1_patient_calculation_service_pb2.ExplainPatientCalculationRequest()
            )
            response_1 = await deps.clients.patients_patient_calculation.ExplainPatientCalculation(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = analytics_v1_funnel_validation_service_pb2.CheckFunnelEligibilityRequest(
                context=request.context,
                funnel=analytics_v1_analytics_pb2.Funnel(
                    audit=common_v1_audit_pb2.AuditInfo(updated_at=response_0.venue.audit.updated_at),
                    owner=identity_v1_refs_pb2.UserRef(email=response_1.patient.contact.email)
                )
            )
            document_2 = MessageToJson(outgoing_2, preserving_proto_field_name=True)
            outgoing_2 = Parse(document_2, analytics_v1_funnel_validation_service_pb2.CheckFunnelEligibilityRequest())
            response_2 = await deps.clients.analytics_funnel_validation.CheckFunnelEligibility(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            outgoing_3 = analytics_v1_cohort_calculation_service_pb2.SimulateCohortRequest()
            outgoing_3.context.CopyFrom(request.context)
            outgoing_3.cohort.owner.display_name = response_2.funnel.owner.display_name
            merged_3 = analytics_v1_cohort_calculation_service_pb2.SimulateCohortRequest()
            merged_3.MergeFrom(outgoing_3)
            outgoing_3.CopyFrom(merged_3)
            response_3 = await deps.clients.analytics_cohort_calculation.SimulateCohort(
                outgoing_3,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_0)
            returned_1_0 = response_1.result.correlation_id
            if returned_1_0:
                response.result.correlation_id = returned_1_0
            returned_1_1 = response_1.outcome.message
            if returned_1_1:
                response.result.message = returned_1_1
            returned_2_0 = response_2.result.message
            if returned_2_0:
                response.result.message = returned_2_0
            returned_3_0 = response_3.result.reference_ids
            response.result.reference_ids.extend(returned_3_0)
            returned_3_1 = response_3.result.details
            response.result.details.update(returned_3_1)
            echoed_0 = request.details.period
            response.period.CopyFrom(echoed_0)
            return response
