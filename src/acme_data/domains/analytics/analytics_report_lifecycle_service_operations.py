"""Functional operations behind AnalyticsReportLifecycleService."""

from __future__ import annotations

from functools import partial
from typing import cast
import logging

from acme.analytics.v1 import analytics_event_query_service_pb2 as analytics_v1_analytics_event_query_service_pb2
from acme.analytics.v1 import (
    analytics_event_validation_service_pb2 as analytics_v1_analytics_event_validation_service_pb2,
)
from acme.analytics.v1 import analytics_pb2 as analytics_v1_analytics_pb2
from acme.analytics.v1 import (
    analytics_report_calculation_service_pb2 as analytics_v1_analytics_report_calculation_service_pb2,
)
from acme.analytics.v1 import (
    analytics_report_lifecycle_service_pb2 as analytics_v1_analytics_report_lifecycle_service_pb2,
)
from acme.analytics.v1 import funnel_query_service_pb2 as analytics_v1_funnel_query_service_pb2
from acme.analytics.v1 import refs_pb2 as analytics_v1_refs_pb2
from acme.anomalies.v1 import (
    anomaly_feedback_workflow_service_pb2 as anomalies_v1_anomaly_feedback_workflow_service_pb2,
)
from acme.audit.v1 import audit_event_validation_service_pb2 as audit_v1_audit_event_validation_service_pb2
from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.customers.v1 import (
    consent_record_validation_service_pb2 as customers_v1_consent_record_validation_service_pb2,
)
from acme.customers.v1 import customer_validation_service_pb2 as customers_v1_customer_validation_service_pb2
from acme.customers.v1 import customers_pb2 as customers_v1_customers_pb2
from acme.customers.v1 import household_calculation_service_pb2 as customers_v1_household_calculation_service_pb2
from acme.customers.v1 import household_validation_service_pb2 as customers_v1_household_validation_service_pb2
from acme.customers.v1 import preference_calculation_service_pb2 as customers_v1_preference_calculation_service_pb2
from acme.customers.v1 import refs_pb2 as customers_v1_refs_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.lineage.v1 import impact_reporting_service_pb2 as lineage_v1_impact_reporting_service_pb2
from acme.lineage.v1 import lineage_node_workflow_service_pb2 as lineage_v1_lineage_node_workflow_service_pb2
from acme.lineage.v1 import lineage_pb2 as lineage_v1_lineage_pb2
from acme.modelregistry.v1 import (
    registered_model_reporting_service_pb2 as modelregistry_v1_registered_model_reporting_service_pb2,
)
from acme.modelregistry.v1 import (
    registered_model_workflow_service_pb2 as modelregistry_v1_registered_model_workflow_service_pb2,
)

from acme_data.domains.analytics import hooks
from acme_data.domains.analytics.dependencies import Dependencies
from acme_data.domains.analytics.models import AnalyticsReportLifecycleActivateAnalyticsReport1Command
from acme_data.domains.analytics.models import to_analytics_report_lifecycle_activate_analytics_report1_command
from acme_data.platform.tenancy import tenant_id
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


async def handle_activate_analytics_report(
    deps: Dependencies,
    request: analytics_v1_analytics_report_lifecycle_service_pb2.ActivateAnalyticsReportRequest
) -> analytics_v1_analytics_report_lifecycle_service_pb2.ActivateAnalyticsReportResponse:
    """Activates an analytics report."""
    response = analytics_v1_analytics_report_lifecycle_service_pb2.ActivateAnalyticsReportResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('ActivateAnalyticsReport', extra={'fields': {'analytics_report_id': request.analytics_report_id}})
        await deps.repository.audit(
            request.context.tenant_id,
            'ActivateAnalyticsReport',
            {'analytics_report_id': request.analytics_report_id}
        )
        response_0 = analytics_v1_analytics_report_calculation_service_pb2.RecalculateAnalyticsReportsResponse()
        response_1 = analytics_v1_funnel_query_service_pb2.BrowseFunnelsResponse()
        outgoing_0 = analytics_v1_analytics_report_calculation_service_pb2.RecalculateAnalyticsReportsRequest(
            analytics_report=analytics_v1_analytics_pb2.AnalyticsReport(
                counterparty=customers_v1_refs_pb2.CustomerRef(
                    display_name=request.details.new_owner.display_name,
                    email=request.details.notify_contact.email
                )
            ),
            context=request.context
        )
        response_0 = await deps.clients.analytics_analytics_report_calculation.RecalculateAnalyticsReports(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        command_1 = AnalyticsReportLifecycleActivateAnalyticsReport1Command(
            context=request.context,
            filter_region=response_0.analytics_report.billing_address.region,
            filter_created_after=response_0.analytics_report.issued_at
        )
        outgoing_1 = to_analytics_report_lifecycle_activate_analytics_report1_command(command_1)
        response_1 = await deps.clients.analytics_funnel_query.BrowseFunnels(outgoing_1, timeout=deps.settings.timeout)
        returned_0_0 = response_0.analytics_report.total
        if returned_0_0.ListFields():
            response.analytics_report.total.MergeFrom(returned_0_0)
        returned_0_1 = response_0.analytics_report.analytics_report_id
        if returned_0_1:
            response.analytics_report.analytics_report_id = returned_0_1
        returned_1_0 = response_1.result.correlation_id
        if returned_1_0:
            response.result.correlation_id = returned_1_0
        returned_1_1 = response_1.result.status
        if returned_1_1:
            response.result.status = returned_1_1
        echoed_0 = request.details.effective_at
        response.outcome.effective_at.CopyFrom(echoed_0)
        echoed_1 = request.details.notify_contact.email
        response.analytics_report.counterparty.email = echoed_1
        return response


async def handle_expire_analytics_report(
    deps: Dependencies,
    request: analytics_v1_analytics_report_lifecycle_service_pb2.ExpireAnalyticsReportRequest
) -> analytics_v1_analytics_report_lifecycle_service_pb2.ExpireAnalyticsReportResponse:
    """Expires an analytics report."""
    response = analytics_v1_analytics_report_lifecycle_service_pb2.ExpireAnalyticsReportResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('ExpireAnalyticsReport', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'ExpireAnalyticsReport', {'reason': request.reason})
        response_0 = lineage_v1_lineage_node_workflow_service_pb2.PauseLineageNodeWorkflowResponse()
        response_1 = analytics_v1_analytics_event_validation_service_pb2.LintAnalyticsEventsResponse()
        response_2 = analytics_v1_analytics_event_query_service_pb2.FindAnalyticsEventsResponse()
        response_3 = modelregistry_v1_registered_model_workflow_service_pb2.ResumeRegisteredModelWorkflowResponse()
        outgoing_0 = lineage_v1_lineage_node_workflow_service_pb2.PauseLineageNodeWorkflowRequest(
            context=request.context,
            lineage_node=lineage_v1_lineage_pb2.LineageNode(
                children=[
                    lineage_v1_lineage_pb2.LineageNode(
                        children=[
                            lineage_v1_lineage_pb2.LineageNode(
                                manager=identity_v1_refs_pb2.UserRef(
                                    display_name=request.details.new_owner.display_name
                                )
                            )
                        ]
                    )
                ]
            )
        )
        response_0 = await deps.clients.lineage_lineage_node_workflow.PauseLineageNodeWorkflow(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = analytics_v1_analytics_event_validation_service_pb2.LintAnalyticsEventsRequest(
            analytics_event=analytics_v1_analytics_pb2.AnalyticsEvent(
                subject=analytics_v1_refs_pb2.FunnelRef(display_name=response_0.lineage_node.manager.display_name)
            ),
            context=request.context,
            details=analytics_v1_analytics_event_validation_service_pb2.LintAnalyticsEventsRequest.Details(
                contact=common_v1_contact_pb2.ContactInfo(
                    email=request.details.notify_contact.email,
                    name=request.details.notify_contact.name,
                    preferred_channel=request.details.notify_contact.preferred_channel
                )
            )
        )
        send_1 = partial(
            deps.clients.analytics_analytics_event_validation.LintAnalyticsEvents,
            timeout=deps.settings.timeout
        )
        response_1 = await send_1(outgoing_1)
        outgoing_2 = analytics_v1_analytics_event_query_service_pb2.FindAnalyticsEventsRequest(
            context=request.context,
            filter=analytics_v1_analytics_event_query_service_pb2.FindAnalyticsEventsRequest.Filter(
                created_after=response_0.lineage_node.audit.updated_at,
                region=response_0.lineage_node.location.region
            )
        )
        response_2 = await hooks.analytics_report_lifecycle_expire_analytics_report2(
            deps.clients.analytics_analytics_event_query,
            outgoing_2,
            deps.settings.timeout
        )
        outgoing_3 = modelregistry_v1_registered_model_workflow_service_pb2.ResumeRegisteredModelWorkflowRequest()
        outgoing_3.context.CopyFrom(request.context)
        outgoing_3.registered_model.owner.user_id = request.details.new_owner.user_id
        outgoing_3.context.tenant_id = tenant_id.get()
        response_3 = await deps.clients.modelregistry_registered_model_workflow.ResumeRegisteredModelWorkflow(
            outgoing_3,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.lineage_node.audit.created_at
        if returned_0_0.ListFields():
            response.analytics_report.audit.created_at.MergeFrom(returned_0_0)
        returned_0_1 = response_0.lineage_node.audit.created_by
        if returned_0_1:
            response.analytics_report.audit.created_by = returned_0_1
        returned_1_0 = response_1.outcome.status
        if returned_1_0:
            response.outcome.status = returned_1_0
        returned_2_0 = response_2.result.status
        if returned_2_0:
            response.result.status = returned_2_0
        returned_3_0 = response_3.result.details
        response.result.details.update(returned_3_0)
        returned_3_1 = response_3.registered_model.audit.created_at
        if returned_3_1.ListFields():
            response.analytics_report.audit.created_at.MergeFrom(returned_3_1)
        echoed_0 = request.analytics_report_id
        response.analytics_report.analytics_report_id = echoed_0
        echoed_1 = request.details.effective_at
        response.outcome.effective_at.CopyFrom(echoed_1)
        return response


async def handle_get_analytics_report_lifecycle(
    deps: Dependencies,
    request: analytics_v1_analytics_report_lifecycle_service_pb2.GetAnalyticsReportLifecycleRequest
) -> analytics_v1_analytics_report_lifecycle_service_pb2.GetAnalyticsReportLifecycleResponse:
    """Returns an analytics report."""
    response = analytics_v1_analytics_report_lifecycle_service_pb2.GetAnalyticsReportLifecycleResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('GetAnalyticsReportLifecycle', extra={'fields': {'domain': 'analytics'}})
        await deps.repository.audit(request.context.tenant_id, 'GetAnalyticsReportLifecycle', {})
        response_0 = customers_v1_preference_calculation_service_pb2.SimulatePreferenceResponse()
        outgoing_0 = customers_v1_preference_calculation_service_pb2.SimulatePreferenceRequest(
            context=request.context,
            preference=customers_v1_customers_pb2.Preference(
                audit=common_v1_audit_pb2.AuditInfo(created_at=request.context.deadline),
                owner=identity_v1_refs_pb2.UserRef(
                    email=request.context.actor.email,
                    user_id=request.context.actor.user_id
                )
            )
        )
        response_0 = await deps.clients.customers_preference_calculation.SimulatePreference(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.preference.description
        returned_0_0_part_1 = response.analytics_report.lines.add()
        if returned_0_0:
            returned_0_0_part_1.description = returned_0_0
        echoed_0 = request.analytics_report_id
        response.analytics_report.analytics_report_id = echoed_0
        return response


async def handle_reinstate_analytics_report(
    deps: Dependencies,
    request: analytics_v1_analytics_report_lifecycle_service_pb2.ReinstateAnalyticsReportRequest
) -> analytics_v1_analytics_report_lifecycle_service_pb2.ReinstateAnalyticsReportResponse:
    """Reinstates an analytics report."""
    response = analytics_v1_analytics_report_lifecycle_service_pb2.ReinstateAnalyticsReportResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('ReinstateAnalyticsReport', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'ReinstateAnalyticsReport', {'reason': request.reason})
        response_0 = audit_v1_audit_event_validation_service_pb2.NormalizeAuditEventResponse()
        outgoing_0 = audit_v1_audit_event_validation_service_pb2.NormalizeAuditEventRequest(
            context=request.context,
            details=audit_v1_audit_event_validation_service_pb2.NormalizeAuditEventRequest.Details(
                contact=common_v1_contact_pb2.ContactInfo(name=request.details.notify_contact.name)
            )
        )
        response_0 = await deps.clients.audit_audit_event_validation.NormalizeAuditEvent(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.outcome.message
        if returned_0_0:
            response.outcome.message = returned_0_0
        returned_0_1 = response_0.result.correlation_id
        if returned_0_1:
            response.result.correlation_id = returned_0_1
        echoed_0 = request.analytics_report_id
        response.analytics_report.analytics_report_id = echoed_0
        echoed_1 = request.details.effective_at
        response.outcome.effective_at.CopyFrom(echoed_1)
        return response


async def handle_renew_analytics_report(
    deps: Dependencies,
    request: analytics_v1_analytics_report_lifecycle_service_pb2.RenewAnalyticsReportRequest
) -> analytics_v1_analytics_report_lifecycle_service_pb2.RenewAnalyticsReportResponse:
    """Renews an analytics report."""
    response = analytics_v1_analytics_report_lifecycle_service_pb2.RenewAnalyticsReportResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('RenewAnalyticsReport', extra={'fields': {'reason_code': request.details.reason_code}})
        await deps.repository.audit(
            request.context.tenant_id,
            'RenewAnalyticsReport',
            {'reason_code': request.details.reason_code}
        )
        response_0 = customers_v1_consent_record_validation_service_pb2.ScoreConsentRecordResponse()
        response_1 = customers_v1_household_validation_service_pb2.ValidateHouseholdResponse()
        response_2 = anomalies_v1_anomaly_feedback_workflow_service_pb2.ResumeAnomalyFeedbackWorkflowResponse()
        outgoing_0 = customers_v1_consent_record_validation_service_pb2.ScoreConsentRecordRequest(
            annotations=dict(request.annotations),
            consent_record=customers_v1_customers_pb2.ConsentRecord(
                subject=customers_v1_refs_pb2.HouseholdRef(display_name=request.details.new_owner.display_name)
            ),
            context=request.context,
            reason=request.reason
        )
        response_0 = await deps.clients.customers_consent_record_validation.ScoreConsentRecord(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = customers_v1_household_validation_service_pb2.ValidateHouseholdRequest(
            context=request.context,
            household=customers_v1_customers_pb2.Household(
                children=[
                    customers_v1_customers_pb2.Household(
                        children=[
                            customers_v1_customers_pb2.Household(
                                manager=identity_v1_refs_pb2.UserRef(
                                    display_name=response_0.consent_record.subject.display_name
                                )
                            )
                        ]
                    )
                ]
            )
        )
        response_1 = cast(customers_v1_household_validation_service_pb2.ValidateHouseholdResponse, await deps.bus.request(
            'acme.analytics.v1.AnalyticsReportLifecycleService/RenewAnalyticsReport/1', outgoing_1, deps.settings.timeout,
        ))
        outgoing_2 = anomalies_v1_anomaly_feedback_workflow_service_pb2.ResumeAnomalyFeedbackWorkflowRequest(
            context=request.context,
            details=anomalies_v1_anomaly_feedback_workflow_service_pb2.ResumeAnomalyFeedbackWorkflowRequest.Details(
                notify=common_v1_contact_pb2.ContactInfo(name=request.details.notify_contact.name)
            )
        )
        response_2 = await deps.clients.anomalies_anomaly_feedback_workflow.ResumeAnomalyFeedbackWorkflow(
            outgoing_2,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.result.message
        if returned_0_0:
            response.result.message = returned_0_0
        returned_1_0 = response_1.household.audit.created_at
        if returned_1_0.ListFields():
            response.analytics_report.audit.created_at.MergeFrom(returned_1_0)
        returned_1_1 = response_1.result.details
        response.result.details.update(returned_1_1)
        returned_2_0 = response_2.anomaly_feedback.subject.display_name
        if returned_2_0:
            response.analytics_report.counterparty.display_name = returned_2_0
        returned_2_1 = response_2.outcome.status
        if returned_2_1:
            response.outcome.status = returned_2_1
        echoed_0 = request.analytics_report_id
        response.analytics_report.analytics_report_id = echoed_0
        echoed_1 = request.details.effective_at
        response.outcome.effective_at.CopyFrom(echoed_1)
        return response


async def handle_schedule_analytics_report_expiry(
    deps: Dependencies,
    request: analytics_v1_analytics_report_lifecycle_service_pb2.ScheduleAnalyticsReportExpiryRequest
) -> analytics_v1_analytics_report_lifecycle_service_pb2.ScheduleAnalyticsReportExpiryResponse:
    """Schedules an analytics report."""
    response = analytics_v1_analytics_report_lifecycle_service_pb2.ScheduleAnalyticsReportExpiryResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('ScheduleAnalyticsReportExpiry', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(
            request.context.tenant_id,
            'ScheduleAnalyticsReportExpiry',
            {'reason': request.reason}
        )
        await deps.repository.save_analytics_report(request.context.tenant_id, request.analytics_report)
        response_0 = customers_v1_household_calculation_service_pb2.RecalculateHouseholdsResponse()
        outgoing_0 = customers_v1_household_calculation_service_pb2.RecalculateHouseholdsRequest(
            context=request.context,
            household=customers_v1_customers_pb2.Household(
                children=[
                    customers_v1_customers_pb2.Household(
                        children=[
                            customers_v1_customers_pb2.Household(
                                audit=common_v1_audit_pb2.AuditInfo(
                                    created_at=request.analytics_report.audit.created_at,
                                    updated_at=request.analytics_report.audit.updated_at
                                ),
                                location=common_v1_address_pb2.PostalAddress(
                                    lines=list(request.analytics_report.billing_address.lines)
                                ),
                                manager=identity_v1_refs_pb2.UserRef(
                                    display_name=request.analytics_report.counterparty.display_name
                                )
                            )
                        ]
                    )
                ]
            )
        )
        response_0 = await deps.clients.customers_household_calculation.RecalculateHouseholds(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.result.message
        if returned_0_0:
            response.result.message = returned_0_0
        returned_0_1 = response_0.household.audit.created_by
        if returned_0_1:
            response.analytics_report.audit.created_by = returned_0_1
        echoed_0 = request.analytics_report_id
        response.analytics_report.analytics_report_id = echoed_0
        echoed_1 = request.analytics_report.total
        response.analytics_report.total.CopyFrom(echoed_1)
        return response


async def handle_suspend_analytics_report(
    deps: Dependencies,
    request: analytics_v1_analytics_report_lifecycle_service_pb2.SuspendAnalyticsReportRequest
) -> analytics_v1_analytics_report_lifecycle_service_pb2.SuspendAnalyticsReportResponse:
    """Suspends an analytics report."""
    response = analytics_v1_analytics_report_lifecycle_service_pb2.SuspendAnalyticsReportResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('SuspendAnalyticsReport', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'SuspendAnalyticsReport', {'reason': request.reason})
        response_0 = customers_v1_customer_validation_service_pb2.ValidateCustomerResponse()
        response_1 = modelregistry_v1_registered_model_reporting_service_pb2.CountRegisteredModelTotalsResponse()
        outgoing_0 = customers_v1_customer_validation_service_pb2.ValidateCustomerRequest(
            context=request.context,
            customer=customers_v1_customers_pb2.Customer(
                relationship_manager=identity_v1_refs_pb2.UserRef(display_name=request.details.new_owner.display_name)
            )
        )
        response_0 = await deps.clients.customers_customer_validation.ValidateCustomer(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = modelregistry_v1_registered_model_reporting_service_pb2.CountRegisteredModelTotalsRequest()
        outgoing_1.context.CopyFrom(request.context)
        outgoing_1.filter.region = response_0.customer.primary_address.region
        if response_0.customer.WhichOneof('identity_document') == 'passport':
            outgoing_1.filter.created_after.CopyFrom(response_0.customer.passport.expires_at)
        response_1 = await deps.clients.modelregistry_registered_model_reporting.CountRegisteredModelTotals(
            outgoing_1,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.outcome.next_steps
        response.outcome.next_steps.extend(returned_0_0)
        returned_1_0 = response_1.result.status
        if returned_1_0:
            response.result.status = returned_1_0
        echoed_0 = request.analytics_report_id
        response.analytics_report.analytics_report_id = echoed_0
        echoed_1 = request.details.effective_at
        response.outcome.effective_at.CopyFrom(echoed_1)
        return response


async def handle_terminate_analytics_report(
    deps: Dependencies,
    request: analytics_v1_analytics_report_lifecycle_service_pb2.TerminateAnalyticsReportRequest
) -> analytics_v1_analytics_report_lifecycle_service_pb2.TerminateAnalyticsReportResponse:
    """Terminates an analytics report."""
    response = analytics_v1_analytics_report_lifecycle_service_pb2.TerminateAnalyticsReportResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('TerminateAnalyticsReport', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'TerminateAnalyticsReport', {'reason': request.reason})
        response_0 = lineage_v1_impact_reporting_service_pb2.ShareImpactReportResponse()
        outgoing_0 = lineage_v1_impact_reporting_service_pb2.ShareImpactReportRequest(
            context=request.context,
            details=lineage_v1_impact_reporting_service_pb2.ShareImpactReportRequest.Details(
                recipient=common_v1_contact_pb2.ContactInfo(
                    email=request.details.notify_contact.email,
                    phone=request.details.notify_contact.phone
                )
            )
        )
        response_0 = await deps.clients.lineage_impact_reporting.ShareImpactReport(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.result.status
        if returned_0_0:
            response.result.status = returned_0_0
        echoed_0 = request.analytics_report_id
        response.analytics_report.analytics_report_id = echoed_0
        echoed_1 = request.details.effective_at
        response.outcome.effective_at.CopyFrom(echoed_1)
        return response
