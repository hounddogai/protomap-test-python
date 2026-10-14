"""Runs the long-lived workflow that takes an analytics event from start to finish."""

from __future__ import annotations

from collections.abc import AsyncIterator
from collections.abc import Awaitable
from collections.abc import Callable
from dataclasses import dataclass
from functools import partial
from typing import Any
from typing import cast
import asyncio
import logging

from google.protobuf.json_format import MessageToDict
from google.protobuf.json_format import MessageToJson
from google.protobuf.json_format import Parse
from google.protobuf.json_format import ParseDict
import grpc

from acme.admissions.v1 import admission_calculation_service_pb2 as admissions_v1_admission_calculation_service_pb2
from acme.analytics.v1 import analytics_event_approval_service_pb2 as analytics_v1_analytics_event_approval_service_pb2
from acme.analytics.v1 import analytics_event_query_service_pb2 as analytics_v1_analytics_event_query_service_pb2
from acme.analytics.v1 import analytics_event_workflow_service_pb2 as analytics_v1_analytics_event_workflow_service_pb2
from acme.analytics.v1 import (
    analytics_event_workflow_service_pb2_grpc as analytics_v1_analytics_event_workflow_service_pb2_grpc,
)
from acme.analytics.v1 import analytics_pb2 as analytics_v1_analytics_pb2
from acme.analytics.v1 import cohort_calculation_service_pb2 as analytics_v1_cohort_calculation_service_pb2
from acme.analytics.v1 import cohort_validation_service_pb2 as analytics_v1_cohort_validation_service_pb2
from acme.analytics.v1 import funnel_calculation_service_pb2 as analytics_v1_funnel_calculation_service_pb2
from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.customers.v1 import (
    consent_record_calculation_service_pb2 as customers_v1_consent_record_calculation_service_pb2,
)
from acme.customers.v1 import (
    consent_record_validation_service_pb2 as customers_v1_consent_record_validation_service_pb2,
)
from acme.customers.v1 import customers_pb2 as customers_v1_customers_pb2
from acme.customers.v1 import household_validation_service_pb2 as customers_v1_household_validation_service_pb2
from acme.customers.v1 import refs_pb2 as customers_v1_refs_pb2
from acme.datasets.v1 import dataset_approval_service_pb2 as datasets_v1_dataset_approval_service_pb2
from acme.identity.v1 import identity_pb2 as identity_v1_identity_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.identity.v1 import user_validation_service_pb2 as identity_v1_user_validation_service_pb2
from acme.ledger.v1 import ledger_account_query_service_pb2 as ledger_v1_ledger_account_query_service_pb2
from acme.lineage.v1 import lineage_edge_workflow_service_pb2 as lineage_v1_lineage_edge_workflow_service_pb2
from acme.lineage.v1 import lineage_edge_workflow_service_pb2_grpc as lineage_v1_lineage_edge_workflow_service_pb2_grpc
from acme.lineage.v1 import lineage_pb2 as lineage_v1_lineage_pb2
from acme.lineage.v1 import refs_pb2 as lineage_v1_refs_pb2
from acme.treasury.v1 import cash_position_service_pb2 as treasury_v1_cash_position_service_pb2
from acme.treasury.v1 import treasury_pb2 as treasury_v1_treasury_pb2
from acme.venues.v1 import venue_service_pb2 as venues_v1_venue_service_pb2
from acme.venues.v1 import venue_validation_service_pb2 as venues_v1_venue_validation_service_pb2
from acme.venues.v1 import venues_pb2 as venues_v1_venues_pb2

from acme_data.domains.analytics.dependencies import Dependencies
from acme_data.domains.analytics.models import AnalyticsEventWorkflowPauseAnalyticsEventWorkflow0Command
from acme_data.domains.analytics.models import to_analytics_event_workflow_pause_analytics_event_workflow0_command
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import run_steps
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_id
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


@dataclass(slots=True)
class AnalyticsEventWorkflowServicer(
    analytics_v1_analytics_event_workflow_service_pb2_grpc.AnalyticsEventWorkflowServiceServicer
):
    deps: Dependencies

    @rpc_errors
    async def AdvanceAnalyticsEventWorkflow(
        self, request: analytics_v1_analytics_event_workflow_service_pb2.AdvanceAnalyticsEventWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_analytics_event_workflow_service_pb2.AdvanceAnalyticsEventWorkflowResponse:
        """Advances an analytics event."""
        return await self.handle_advance_analytics_event_workflow(request)

    @rpc_errors
    async def CancelAnalyticsEventWorkflow(
        self, request: analytics_v1_analytics_event_workflow_service_pb2.CancelAnalyticsEventWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_analytics_event_workflow_service_pb2.CancelAnalyticsEventWorkflowResponse:
        """Cancels an analytics event."""
        return await self.handle_cancel_analytics_event_workflow(request)

    @rpc_errors
    @retry_transient
    async def InspectAnalyticsEventWorkflow(
        self, request: analytics_v1_analytics_event_workflow_service_pb2.InspectAnalyticsEventWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_analytics_event_workflow_service_pb2.InspectAnalyticsEventWorkflowResponse:
        """Returns an analytics event."""
        return await self.handle_inspect_analytics_event_workflow(request)

    @rpc_errors
    @retry_transient
    async def ListAnalyticsEventWorkflows(
        self, request: analytics_v1_analytics_event_workflow_service_pb2.ListAnalyticsEventWorkflowsRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_analytics_event_workflow_service_pb2.ListAnalyticsEventWorkflowsResponse:
        """Lists analytics events a page at a time."""
        return await self.handle_list_analytics_event_workflows(request)

    @rpc_errors
    async def PauseAnalyticsEventWorkflow(
        self, request: analytics_v1_analytics_event_workflow_service_pb2.PauseAnalyticsEventWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_analytics_event_workflow_service_pb2.PauseAnalyticsEventWorkflowResponse:
        """Pauses an analytics event."""
        return await self.handle_pause_analytics_event_workflow(request)

    @rpc_errors
    async def ResumeAnalyticsEventWorkflow(
        self, request: analytics_v1_analytics_event_workflow_service_pb2.ResumeAnalyticsEventWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_analytics_event_workflow_service_pb2.ResumeAnalyticsEventWorkflowResponse:
        """Resumes an analytics event."""
        return await self.handle_resume_analytics_event_workflow(request)

    @rpc_errors
    async def RetryAnalyticsEventWorkflow(
        self, request: analytics_v1_analytics_event_workflow_service_pb2.RetryAnalyticsEventWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_analytics_event_workflow_service_pb2.RetryAnalyticsEventWorkflowResponse:
        """Retrys an analytics event."""
        return await self.handle_retry_analytics_event_workflow(request)

    @rpc_errors
    async def SignalAnalyticsEventWorkflow(
        self, request: analytics_v1_analytics_event_workflow_service_pb2.SignalAnalyticsEventWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_analytics_event_workflow_service_pb2.SignalAnalyticsEventWorkflowResponse:
        """Signals an analytics event."""
        return await self.handle_signal_analytics_event_workflow(request)

    @rpc_errors
    async def StartAnalyticsEventWorkflow(
        self, request: analytics_v1_analytics_event_workflow_service_pb2.StartAnalyticsEventWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_analytics_event_workflow_service_pb2.StartAnalyticsEventWorkflowResponse:
        """Starts an analytics event."""
        return await self.handle_start_analytics_event_workflow(request)

    async def handle_advance_analytics_event_workflow(
        self,
        request: analytics_v1_analytics_event_workflow_service_pb2.AdvanceAnalyticsEventWorkflowRequest
    ) -> analytics_v1_analytics_event_workflow_service_pb2.AdvanceAnalyticsEventWorkflowResponse:
        """Advances an analytics event."""
        deps = self.deps
        response = analytics_v1_analytics_event_workflow_service_pb2.AdvanceAnalyticsEventWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info(
                'AdvanceAnalyticsEventWorkflow',
                extra={'fields': {'analytics_event_id': request.analytics_event.analytics_event_id}}
            )
            await deps.repository.audit(
                request.context.tenant_id,
                'AdvanceAnalyticsEventWorkflow',
                {'analytics_event_id': request.analytics_event.analytics_event_id}
            )
            await deps.repository.save_analytics_event(request.context.tenant_id, request.analytics_event)
            response_0 = ledger_v1_ledger_account_query_service_pb2.SummarizeLedgerAccountsResponse()
            response_1 = datasets_v1_dataset_approval_service_pb2.RecallDatasetResponse()
            response_2 = analytics_v1_analytics_event_approval_service_pb2.ListPendingAnalyticsEventsResponse()
            outgoing_0 = ledger_v1_ledger_account_query_service_pb2.SummarizeLedgerAccountsRequest(
                annotations=dict(request.annotations),
                context=request.context,
                details=ledger_v1_ledger_account_query_service_pb2.SummarizeLedgerAccountsRequest.Details(
                    filters=dict(request.details.parameters)
                ),
                reason=request.reason
            )
            document_0 = MessageToJson(outgoing_0, preserving_proto_field_name=True)
            outgoing_0 = Parse(document_0, ledger_v1_ledger_account_query_service_pb2.SummarizeLedgerAccountsRequest())
            response_0 = await deps.clients.ledger_ledger_account_query.SummarizeLedgerAccounts(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = datasets_v1_dataset_approval_service_pb2.RecallDatasetRequest()
            outgoing_1.context.CopyFrom(request.context)
            outgoing_1.dataset.owner.email = request.details.notify.email
            outgoing_1.details.approver.display_name = request.analytics_event.subject.display_name
            merged_1 = datasets_v1_dataset_approval_service_pb2.RecallDatasetRequest()
            merged_1.MergeFrom(outgoing_1)
            outgoing_1.CopyFrom(merged_1)
            response_1 = await deps.clients.datasets_dataset_approval.RecallDataset(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            callbacks_2: list[
                Callable[
                    [],
                    Awaitable[analytics_v1_analytics_event_approval_service_pb2.ListPendingAnalyticsEventsResponse]
                ]
            ] = []
            for item_2 in request.analytics_event.measurements:
                outgoing_2 = analytics_v1_analytics_event_approval_service_pb2.ListPendingAnalyticsEventsRequest(
                    context=request.context,
                    filter=analytics_v1_analytics_event_approval_service_pb2.ListPendingAnalyticsEventsRequest.Filter(
                        created_after=item_2.observed_at
                    )
                )
                async def send_2(
                    payload: analytics_v1_analytics_event_approval_service_pb2.ListPendingAnalyticsEventsRequest = outgoing_2
                ) -> analytics_v1_analytics_event_approval_service_pb2.ListPendingAnalyticsEventsResponse:
                    return await deps.clients.analytics_analytics_event_approval.ListPendingAnalyticsEvents(
                        payload,
                        timeout=deps.settings.timeout
                    )
                callbacks_2.append(send_2)
            for callback_2 in callbacks_2:
                response_2 = await callback_2()
            returned_0_0 = response_0.result.correlation_id
            if returned_0_0:
                response.result.correlation_id = returned_0_0
            returned_0_1 = response_0.result.details
            response.result.details.update(returned_0_1)
            returned_1_0 = response_1.outcome.status
            if returned_1_0:
                response.outcome.status = returned_1_0
            returned_1_1 = response_1.result.message
            if returned_1_1:
                response.result.message = returned_1_1
            echoed_0 = request.analytics_event_id
            response.analytics_event.analytics_event_id = echoed_0
            echoed_1 = request.analytics_event.occurred_at
            response.analytics_event.occurred_at.CopyFrom(echoed_1)
            return response

    async def handle_cancel_analytics_event_workflow(
        self,
        request: analytics_v1_analytics_event_workflow_service_pb2.CancelAnalyticsEventWorkflowRequest
    ) -> analytics_v1_analytics_event_workflow_service_pb2.CancelAnalyticsEventWorkflowResponse:
        """Cancels an analytics event."""
        deps = self.deps
        response = analytics_v1_analytics_event_workflow_service_pb2.CancelAnalyticsEventWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CancelAnalyticsEventWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'CancelAnalyticsEventWorkflow',
                {'reason': request.reason}
            )
            await deps.repository.save_analytics_event(request.context.tenant_id, request.analytics_event)
            response_0 = lineage_v1_lineage_edge_workflow_service_pb2.RetryLineageEdgeWorkflowResponse()
            outgoing_0 = lineage_v1_lineage_edge_workflow_service_pb2.RetryLineageEdgeWorkflowRequest(
                context=request.context,
                details=lineage_v1_lineage_edge_workflow_service_pb2.RetryLineageEdgeWorkflowRequest.Details(
                    notify=common_v1_contact_pb2.ContactInfo(
                        email=request.details.notify.email,
                        name=request.details.notify.name,
                        phone=request.details.notify.phone
                    )
                ),
                lineage_edge=lineage_v1_lineage_pb2.LineageEdge(
                    subject=lineage_v1_refs_pb2.ImpactRef(display_name=request.analytics_event.subject.display_name)
                )
            )
            registered_0 = cast(
                lineage_v1_lineage_edge_workflow_service_pb2_grpc.LineageEdgeWorkflowServiceStub,
                deps.clients.registry['acme.lineage.v1.LineageEdgeWorkflowService']
            )
            response_0 = await registered_0.RetryLineageEdgeWorkflow(outgoing_0, timeout=deps.settings.timeout)
            returned_0_0 = response_0.outcome.status
            if returned_0_0:
                response.result.status = returned_0_0
            echoed_0 = request.analytics_event_id
            response.analytics_event.analytics_event_id = echoed_0
            echoed_1 = request.analytics_event.sequence
            response.analytics_event.sequence = echoed_1
            return response

    async def handle_inspect_analytics_event_workflow(
        self,
        request: analytics_v1_analytics_event_workflow_service_pb2.InspectAnalyticsEventWorkflowRequest
    ) -> analytics_v1_analytics_event_workflow_service_pb2.InspectAnalyticsEventWorkflowResponse:
        """Returns an analytics event."""
        deps = self.deps
        response = analytics_v1_analytics_event_workflow_service_pb2.InspectAnalyticsEventWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('InspectAnalyticsEventWorkflow', extra={'fields': {'locale': request.context.locale}})
            await deps.repository.audit(
                request.context.tenant_id,
                'InspectAnalyticsEventWorkflow',
                {'locale': request.context.locale}
            )
            echoed_0 = request.analytics_event_id
            response.analytics_event.analytics_event_id = echoed_0
            return response

    async def handle_list_analytics_event_workflows(
        self,
        request: analytics_v1_analytics_event_workflow_service_pb2.ListAnalyticsEventWorkflowsRequest
    ) -> analytics_v1_analytics_event_workflow_service_pb2.ListAnalyticsEventWorkflowsResponse:
        """Lists analytics events a page at a time."""
        deps = self.deps
        response = analytics_v1_analytics_event_workflow_service_pb2.ListAnalyticsEventWorkflowsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ListAnalyticsEventWorkflows', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ListAnalyticsEventWorkflows',
                {'order_by': request.order_by}
            )
            response_0 = analytics_v1_cohort_calculation_service_pb2.CompareCohortOptionsResponse()
            outgoing_0 = analytics_v1_cohort_calculation_service_pb2.CompareCohortOptionsRequest(
                cohort=analytics_v1_analytics_pb2.Cohort(
                    owner=identity_v1_refs_pb2.UserRef(
                        email=request.context.actor.email,
                        user_id=request.context.actor.user_id
                    )
                ),
                context=request.context,
                details=analytics_v1_cohort_calculation_service_pb2.CompareCohortOptionsRequest.Details(
                    destination=common_v1_address_pb2.PostalAddress(region=request.filter.region)
                )
            )
            response_0 = await deps.clients.analytics_cohort_calculation.CompareCohortOptions(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.cohort.owner.display_name
            returned_0_0_part_0 = response.analytics_events.add()
            if returned_0_0:
                returned_0_0_part_0.subject.display_name = returned_0_0
            returned_0_1 = response_0.result.correlation_id
            returned_0_1_part_0 = response.analytics_events.add()
            if returned_0_1:
                returned_0_1_part_0.correlation_id = returned_0_1
            return response

    async def handle_pause_analytics_event_workflow(
        self,
        request: analytics_v1_analytics_event_workflow_service_pb2.PauseAnalyticsEventWorkflowRequest
    ) -> analytics_v1_analytics_event_workflow_service_pb2.PauseAnalyticsEventWorkflowResponse:
        """Pauses an analytics event."""
        deps = self.deps
        response = analytics_v1_analytics_event_workflow_service_pb2.PauseAnalyticsEventWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('PauseAnalyticsEventWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'PauseAnalyticsEventWorkflow',
                {'reason': request.reason}
            )
            await deps.repository.save_analytics_event(request.context.tenant_id, request.analytics_event)
            response_0 = venues_v1_venue_service_pb2.CreateVenueResponse()
            response_1 = venues_v1_venue_validation_service_pb2.ScoreVenueResponse()
            response_2 = customers_v1_household_validation_service_pb2.ScoreHouseholdResponse()
            response_3 = analytics_v1_cohort_validation_service_pb2.PreviewCohortResponse()
            command_0 = AnalyticsEventWorkflowPauseAnalyticsEventWorkflow0Command.model_validate(
                {
                    'context': request.context,
                    'venue_owner_display_name': request.analytics_event.subject.display_name,
                    'venue_owner_email': request.details.notify.email
                }
            )
            outgoing_0 = to_analytics_event_workflow_pause_analytics_event_workflow0_command(command_0)
            response_0 = await deps.clients.venues_venue.CreateVenue(outgoing_0, timeout=deps.settings.timeout)
            outgoing_1 = venues_v1_venue_validation_service_pb2.ScoreVenueRequest(
                context=request.context,
                venue=venues_v1_venues_pb2.Venue(
                    address=common_v1_address_pb2.PostalAddress(locality=response_0.venue.address.locality),
                    audit=common_v1_audit_pb2.AuditInfo(
                        etag=response_0.venue.audit.etag,
                        updated_at=response_0.venue.audit.updated_at
                    )
                )
            )
            send_1 = partial(deps.clients.venues_venue_validation.ScoreVenue, timeout=deps.settings.timeout)
            response_1 = await send_1(outgoing_1)
            outgoing_2 = customers_v1_household_validation_service_pb2.ScoreHouseholdRequest()
            outgoing_2.context.CopyFrom(request.context)
            field_2_1_part_1 = outgoing_2.household.children.add()
            field_2_1_part_2 = field_2_1_part_1.children.add()
            field_2_1_part_2.audit.created_at.CopyFrom(response_0.venue.audit.created_at)
            if response_1.venue.WhichOneof('locator') == 'address':
                field_2_2_part_1 = outgoing_2.household.children.add()
                field_2_2_part_2 = field_2_2_part_1.children.add()
                field_2_2_part_2.location.lines.extend(list(response_1.venue.address.lines))
            field_2_3_part_1 = outgoing_2.household.children.add()
            field_2_3_part_2 = field_2_3_part_1.children.add()
            field_2_3_part_2.manager.email = response_0.venue.owner.email
            field_2_4_part_1 = outgoing_2.household.children.add()
            field_2_4_part_2 = field_2_4_part_1.children.add()
            field_2_4_part_2.manager.user_id = response_1.venue.owner.user_id
            response_2 = await deps.clients.customers_household_validation.ScoreHousehold(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            outgoing_3 = analytics_v1_cohort_validation_service_pb2.PreviewCohortRequest()
            outgoing_3.context.CopyFrom(request.context)
            outgoing_3.cohort.owner.user_id = response_2.household.manager.user_id
            outgoing_3.cohort.audit.etag = response_0.venue.audit.etag
            outgoing_3.cohort.audit.created_at.CopyFrom(response_0.venue.audit.created_at)
            outgoing_3.context.tenant_id = tenant_id.get()
            response_3 = await deps.clients.analytics_cohort_validation.PreviewCohort(
                outgoing_3,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.result.message = returned_0_0
            returned_0_1 = response_0.result.correlation_id
            if returned_0_1:
                response.result.correlation_id = returned_0_1
            returned_1_0 = response_1.result.status
            if returned_1_0:
                response.outcome.status = returned_1_0
            returned_1_1 = response_1.result.message
            if returned_1_1:
                response.outcome.message = returned_1_1
            returned_2_0 = response_2.result.correlation_id
            if returned_2_0:
                response.analytics_event.correlation_id = returned_2_0
            returned_3_0 = response_3.outcome.effective_at
            if returned_3_0.ListFields():
                response.outcome.effective_at.MergeFrom(returned_3_0)
            echoed_0 = request.analytics_event_id
            response.analytics_event.analytics_event_id = echoed_0
            echoed_1 = request.analytics_event.subject
            response.analytics_event.subject.CopyFrom(echoed_1)
            return response

    async def handle_resume_analytics_event_workflow(
        self,
        request: analytics_v1_analytics_event_workflow_service_pb2.ResumeAnalyticsEventWorkflowRequest
    ) -> analytics_v1_analytics_event_workflow_service_pb2.ResumeAnalyticsEventWorkflowResponse:
        """Resumes an analytics event."""
        deps = self.deps
        response = analytics_v1_analytics_event_workflow_service_pb2.ResumeAnalyticsEventWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ResumeAnalyticsEventWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ResumeAnalyticsEventWorkflow',
                {'reason': request.reason}
            )
            await deps.repository.save_analytics_event(request.context.tenant_id, request.analytics_event)
            response_0 = customers_v1_consent_record_calculation_service_pb2.RecalculateConsentRecordsResponse()
            response_1 = customers_v1_consent_record_validation_service_pb2.ValidateConsentRecordResponse()
            response_2 = analytics_v1_cohort_validation_service_pb2.NormalizeCohortResponse()
            outgoing_0 = customers_v1_consent_record_calculation_service_pb2.RecalculateConsentRecordsRequest(
                consent_record=customers_v1_customers_pb2.ConsentRecord(
                    correlation_id=request.analytics_event.correlation_id,
                    kind=request.analytics_event.kind,
                    occurred_at=request.analytics_event.occurred_at
                ),
                context=request.context
            )
            outgoing_2 = analytics_v1_cohort_validation_service_pb2.NormalizeCohortRequest(
                cohort=analytics_v1_analytics_pb2.Cohort(
                    owner=identity_v1_refs_pb2.UserRef(display_name=request.analytics_event.subject.display_name),
                    parameters=dict(request.details.parameters)
                ),
                context=request.context,
                details=analytics_v1_cohort_validation_service_pb2.NormalizeCohortRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(phone=request.details.notify.phone)
                )
            )
            response_0, response_2 = await asyncio.gather(
                deps.clients.customers_consent_record_calculation.RecalculateConsentRecords(
                    outgoing_0,
                    timeout=deps.settings.timeout
                ),
                deps.clients.analytics_cohort_validation.NormalizeCohort(outgoing_2, timeout=deps.settings.timeout),
            )
            outgoing_1 = customers_v1_consent_record_validation_service_pb2.ValidateConsentRecordRequest(
                consent_record=customers_v1_customers_pb2.ConsentRecord(
                    subject=customers_v1_refs_pb2.HouseholdRef(
                        household_id=response_0.consent_record.subject.household_id
                    )
                ),
                context=request.context,
                details=customers_v1_consent_record_validation_service_pb2.ValidateConsentRecordRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(
                        phone=request.details.notify.phone,
                        preferred_channel=request.details.notify.preferred_channel
                    )
                )
            )
            steps_1 = [
                partial(
                    deps.clients.customers_consent_record_validation.ValidateConsentRecord,
                    outgoing_1,
                    timeout=deps.settings.timeout
                )
            ]
            results_1 = await run_steps(steps_1)
            response_1 = results_1[-1]
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.outcome.message = returned_0_0
            returned_1_0 = response_1.outcome.message
            if returned_1_0:
                response.result.message = returned_1_0
            returned_1_1 = response_1.consent_record.source
            if returned_1_1:
                response.analytics_event.source = returned_1_1
            returned_2_0 = response_2.result.message
            if returned_2_0:
                response.outcome.message = returned_2_0
            echoed_0 = request.analytics_event_id
            response.analytics_event.analytics_event_id = echoed_0
            echoed_1 = request.analytics_event.attributes
            response.analytics_event.attributes.update(echoed_1)
            return response

    async def handle_retry_analytics_event_workflow(
        self,
        request: analytics_v1_analytics_event_workflow_service_pb2.RetryAnalyticsEventWorkflowRequest
    ) -> analytics_v1_analytics_event_workflow_service_pb2.RetryAnalyticsEventWorkflowResponse:
        """Retrys an analytics event."""
        deps = self.deps
        response = analytics_v1_analytics_event_workflow_service_pb2.RetryAnalyticsEventWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('RetryAnalyticsEventWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'RetryAnalyticsEventWorkflow',
                {'reason': request.reason}
            )
            await deps.repository.save_analytics_event(request.context.tenant_id, request.analytics_event)
            response_0 = treasury_v1_cash_position_service_pb2.UpdateCashPositionResponse()
            response_1 = identity_v1_user_validation_service_pb2.NormalizeUserResponse()
            outgoing_0 = treasury_v1_cash_position_service_pb2.UpdateCashPositionRequest(
                cash_position=treasury_v1_treasury_pb2.CashPosition(
                    contact=common_v1_contact_pb2.ContactInfo(
                        name=request.details.notify.name,
                        phone=request.details.notify.phone
                    )
                ),
                context=request.context
            )
            response_0 = cast(treasury_v1_cash_position_service_pb2.UpdateCashPositionResponse, await deps.bus.request(
                'acme.analytics.v1.AnalyticsEventWorkflowService/RetryAnalyticsEventWorkflow/0', outgoing_0, deps.settings.timeout,
            ))
            outgoing_1 = identity_v1_user_validation_service_pb2.NormalizeUserRequest(
                context=request.context,
                details=identity_v1_user_validation_service_pb2.NormalizeUserRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(email=response_0.cash_position.contact.email)
                ),
                user=identity_v1_identity_pb2.User(
                    audit=common_v1_audit_pb2.AuditInfo(etag=response_0.cash_position.audit.etag),
                    contact=common_v1_contact_pb2.ContactInfo(phone=request.details.notify.phone)
                )
            )
            response_1 = await deps.clients.identity_user_validation.NormalizeUser(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.correlation_id
            if returned_0_0:
                response.result.correlation_id = returned_0_0
            returned_0_1 = response_0.cash_position.holder.display_name
            if returned_0_1:
                response.analytics_event.subject.display_name = returned_0_1
            returned_1_0 = response_1.user.attributes
            response.analytics_event.attributes.update(returned_1_0)
            echoed_0 = request.analytics_event_id
            response.analytics_event.analytics_event_id = echoed_0
            echoed_1 = request.analytics_event.source
            response.analytics_event.source = echoed_1
            return response

    async def handle_signal_analytics_event_workflow(
        self,
        request: analytics_v1_analytics_event_workflow_service_pb2.SignalAnalyticsEventWorkflowRequest
    ) -> analytics_v1_analytics_event_workflow_service_pb2.SignalAnalyticsEventWorkflowResponse:
        """Signals an analytics event."""
        deps = self.deps
        response = analytics_v1_analytics_event_workflow_service_pb2.SignalAnalyticsEventWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SignalAnalyticsEventWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'SignalAnalyticsEventWorkflow',
                {'reason': request.reason}
            )
            await deps.repository.save_analytics_event(request.context.tenant_id, request.analytics_event)
            response_0 = venues_v1_venue_service_pb2.SearchVenuesResponse()
            response_1 = admissions_v1_admission_calculation_service_pb2.EstimateAdmissionResponse()
            response_2 = analytics_v1_funnel_calculation_service_pb2.ExplainFunnelCalculationResponse()
            outgoing_0 = venues_v1_venue_service_pb2.SearchVenuesRequest(
                context=request.context,
                filter=venues_v1_venue_service_pb2.SearchVenuesRequest.Filter(
                    created_after=request.analytics_event.occurred_at,
                    labels=dict(request.analytics_event.attributes),
                    owner_id=request.analytics_event.correlation_id
                )
            )
            method_name_0 = 'SearchVenues'
            response_0 = await getattr(deps.clients.venues_venue, method_name_0)(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            fields_1: dict[str, Any] = {
                'admission': {'correlation_id': response_0.result.correlation_id, 'kind': request.analytics_event.kind},
                'context': request.context
            }
            outgoing_1 = admissions_v1_admission_calculation_service_pb2.EstimateAdmissionRequest(**fields_1)
            response_1 = await deps.clients.admissions_admission_calculation.EstimateAdmission(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = analytics_v1_funnel_calculation_service_pb2.ExplainFunnelCalculationRequest(
                context=request.context,
                details=analytics_v1_funnel_calculation_service_pb2.ExplainFunnelCalculationRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(
                        phone=request.details.notify.phone,
                        preferred_channel=request.details.notify.preferred_channel
                    )
                ),
                funnel=analytics_v1_analytics_pb2.Funnel(
                    owner=identity_v1_refs_pb2.UserRef(display_name=request.analytics_event.subject.display_name)
                )
            )
            document_2 = MessageToDict(outgoing_2, preserving_proto_field_name=True)
            outgoing_2 = ParseDict(
                document_2,
                analytics_v1_funnel_calculation_service_pb2.ExplainFunnelCalculationRequest()
            )
            response_2 = await deps.clients.analytics_funnel_calculation.ExplainFunnelCalculation(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.result.message = returned_0_0
            returned_1_0 = response_1.admission.correlation_id
            if returned_1_0:
                response.result.correlation_id = returned_1_0
            returned_2_0 = response_2.result.message
            if returned_2_0:
                response.result.message = returned_2_0
            echoed_0 = request.analytics_event_id
            response.analytics_event.analytics_event_id = echoed_0
            echoed_1 = request.analytics_event.attributes
            response.analytics_event.attributes.update(echoed_1)
            return response

    async def handle_start_analytics_event_workflow(
        self,
        request: analytics_v1_analytics_event_workflow_service_pb2.StartAnalyticsEventWorkflowRequest
    ) -> analytics_v1_analytics_event_workflow_service_pb2.StartAnalyticsEventWorkflowResponse:
        """Starts an analytics event."""
        deps = self.deps
        response = analytics_v1_analytics_event_workflow_service_pb2.StartAnalyticsEventWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('StartAnalyticsEventWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'StartAnalyticsEventWorkflow',
                {'reason': request.reason}
            )
            await deps.repository.save_analytics_event(request.context.tenant_id, request.analytics_event)
            response_0 = analytics_v1_analytics_event_query_service_pb2.LookupAnalyticsEventResponse()
            outgoing_0 = analytics_v1_analytics_event_query_service_pb2.LookupAnalyticsEventRequest(
                analytics_event_id=request.analytics_event.analytics_event_id,
                context=request.context
            )
            document_0 = MessageToJson(outgoing_0, preserving_proto_field_name=True)
            outgoing_0 = Parse(document_0, analytics_v1_analytics_event_query_service_pb2.LookupAnalyticsEventRequest())
            response_0 = await deps.clients.analytics_analytics_event_query.LookupAnalyticsEvent(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.analytics_event.subject.funnel_id
            if returned_0_0:
                response.analytics_event.subject.funnel_id = returned_0_0
            returned_0_1 = response_0.result.status
            if returned_0_1:
                response.outcome.status = returned_0_1
            echoed_0 = request.analytics_event_id
            response.analytics_event.analytics_event_id = echoed_0
            echoed_1 = request.analytics_event.occurred_at
            response.analytics_event.occurred_at.CopyFrom(echoed_1)
            return response
