"""Routes analytics events through approval, with escalation and delegation."""

from __future__ import annotations

from collections.abc import AsyncIterator
from collections.abc import Awaitable
from collections.abc import Callable
from functools import partial
import asyncio
import logging

from google.protobuf.json_format import MessageToDict
from google.protobuf.json_format import MessageToJson
from google.protobuf.json_format import Parse
from google.protobuf.json_format import ParseDict
import grpc

from acme.analytics.v1 import analytics_event_approval_service_pb2 as analytics_v1_analytics_event_approval_service_pb2
from acme.analytics.v1 import (
    analytics_event_approval_service_pb2_grpc as analytics_v1_analytics_event_approval_service_pb2_grpc,
)
from acme.analytics.v1 import analytics_event_query_service_pb2 as analytics_v1_analytics_event_query_service_pb2
from acme.analytics.v1 import analytics_pb2 as analytics_v1_analytics_pb2
from acme.analytics.v1 import (
    analytics_report_calculation_service_pb2 as analytics_v1_analytics_report_calculation_service_pb2,
)
from acme.analytics.v1 import funnel_calculation_service_pb2 as analytics_v1_funnel_calculation_service_pb2
from acme.audit.v1 import audit_event_query_service_pb2 as audit_v1_audit_event_query_service_pb2
from acme.billing.v1 import billing_account_query_service_pb2 as billing_v1_billing_account_query_service_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.customers.v1 import (
    consent_record_validation_service_pb2 as customers_v1_consent_record_validation_service_pb2,
)
from acme.customers.v1 import customer_service_pb2 as customers_v1_customer_service_pb2
from acme.customers.v1 import customers_pb2 as customers_v1_customers_pb2
from acme.customers.v1 import refs_pb2 as customers_v1_refs_pb2
from acme.featurestore.v1 import entity_reporting_service_pb2 as featurestore_v1_entity_reporting_service_pb2
from acme.featurestore.v1 import (
    feature_view_lifecycle_service_pb2 as featurestore_v1_feature_view_lifecycle_service_pb2,
)
from acme.featurestore.v1 import featurestore_pb2 as featurestore_v1_featurestore_pb2
from acme.identity.v1 import identity_pb2 as identity_v1_identity_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.identity.v1 import user_validation_service_pb2 as identity_v1_user_validation_service_pb2
from acme.lineage.v1 import impact_sync_service_pb2 as lineage_v1_impact_sync_service_pb2
from acme.lineage.v1 import impact_workflow_service_pb2 as lineage_v1_impact_workflow_service_pb2
from acme.lineage.v1 import lineage_pb2 as lineage_v1_lineage_pb2
from acme.metrics.v1 import metric_series_query_service_pb2 as metrics_v1_metric_series_query_service_pb2
from acme.pipelines.v1 import pipeline_run_sync_service_pb2 as pipelines_v1_pipeline_run_sync_service_pb2
from acme.pipelines.v1 import pipelines_pb2 as pipelines_v1_pipelines_pb2
from acme.pipelines.v1 import refs_pb2 as pipelines_v1_refs_pb2

from acme_data.domains.analytics import hooks
from acme_data.domains.analytics.adapters import AnalyticsEventApprovalSubmitAnalyticsEvent1Adapter
from acme_data.domains.analytics.dependencies import Dependencies
from acme_data.domains.analytics.models import AnalyticsEventApprovalEscalateAnalyticsEvent2Command
from acme_data.domains.analytics.models import to_analytics_event_approval_escalate_analytics_event2_command
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import run_steps
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class AnalyticsEventApprovalServicer(
    analytics_v1_analytics_event_approval_service_pb2_grpc.AnalyticsEventApprovalServiceServicer
):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    async def ApproveAnalyticsEvent(
        self, request: analytics_v1_analytics_event_approval_service_pb2.ApproveAnalyticsEventRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_analytics_event_approval_service_pb2.ApproveAnalyticsEventResponse:
        """Approves an analytics event."""
        return await self.handle_approve_analytics_event(request)

    @rpc_errors
    async def CommentAnalyticsEventApproval(
        self, request: analytics_v1_analytics_event_approval_service_pb2.CommentAnalyticsEventApprovalRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_analytics_event_approval_service_pb2.CommentAnalyticsEventApprovalResponse:
        """Comments an analytics event."""
        return await self.handle_comment_analytics_event_approval(request)

    @rpc_errors
    async def EscalateAnalyticsEvent(
        self, request: analytics_v1_analytics_event_approval_service_pb2.EscalateAnalyticsEventRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_analytics_event_approval_service_pb2.EscalateAnalyticsEventResponse:
        """Escalates an analytics event."""
        return await self.handle_escalate_analytics_event(request)

    @rpc_errors
    @retry_transient
    async def ListPendingAnalyticsEvents(
        self, request: analytics_v1_analytics_event_approval_service_pb2.ListPendingAnalyticsEventsRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_analytics_event_approval_service_pb2.ListPendingAnalyticsEventsResponse:
        """Lists analytics events a page at a time."""
        return await self.handle_list_pending_analytics_events(request)

    @rpc_errors
    async def RecallAnalyticsEvent(
        self, request: analytics_v1_analytics_event_approval_service_pb2.RecallAnalyticsEventRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_analytics_event_approval_service_pb2.RecallAnalyticsEventResponse:
        """Recalls an analytics event."""
        return await self.handle_recall_analytics_event(request)

    @rpc_errors
    async def RejectAnalyticsEvent(
        self, request: analytics_v1_analytics_event_approval_service_pb2.RejectAnalyticsEventRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_analytics_event_approval_service_pb2.RejectAnalyticsEventResponse:
        """Rejects an analytics event."""
        return await self.handle_reject_analytics_event(request)

    @rpc_errors
    async def SubmitAnalyticsEvent(
        self, request: analytics_v1_analytics_event_approval_service_pb2.SubmitAnalyticsEventRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_analytics_event_approval_service_pb2.SubmitAnalyticsEventResponse:
        """Submits an analytics event."""
        return await self.handle_submit_analytics_event(request)

    async def handle_approve_analytics_event(
        self,
        request: analytics_v1_analytics_event_approval_service_pb2.ApproveAnalyticsEventRequest
    ) -> analytics_v1_analytics_event_approval_service_pb2.ApproveAnalyticsEventResponse:
        """Approves an analytics event."""
        deps = self.deps
        response = analytics_v1_analytics_event_approval_service_pb2.ApproveAnalyticsEventResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ApproveAnalyticsEvent', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'ApproveAnalyticsEvent', {'reason': request.reason})
            await deps.repository.save_analytics_event(request.context.tenant_id, request.analytics_event)
            response_0 = customers_v1_customer_service_pb2.SearchCustomersResponse()
            response_1 = featurestore_v1_feature_view_lifecycle_service_pb2.ScheduleFeatureViewExpiryResponse()
            outgoing_0 = customers_v1_customer_service_pb2.SearchCustomersRequest(
                context=request.context,
                filter=customers_v1_customer_service_pb2.SearchCustomersRequest.Filter(
                    created_after=request.details.effective_at,
                    labels=dict(request.analytics_event.attributes),
                    owner_id=request.analytics_event.correlation_id
                )
            )
            response_0 = await deps.clients.customers_customer.SearchCustomers(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = featurestore_v1_feature_view_lifecycle_service_pb2.ScheduleFeatureViewExpiryRequest(
                context=request.context,
                details=featurestore_v1_feature_view_lifecycle_service_pb2.ScheduleFeatureViewExpiryRequest.Details(
                    notify=common_v1_contact_pb2.ContactInfo(email=request.details.approver.email)
                ),
                feature_view=featurestore_v1_featurestore_pb2.FeatureView(
                    owner=identity_v1_refs_pb2.UserRef(user_id=request.details.approver.user_id)
                )
            )
            method_name_1 = 'ScheduleFeatureViewExpiry'
            response_1 = await getattr(
                deps.clients.featurestore_feature_view_lifecycle,
                method_name_1
            )(outgoing_1, timeout=deps.settings.timeout)
            returned_0_0 = response_0.result.status
            if returned_0_0:
                response.result.status = returned_0_0
            returned_1_0 = response_1.feature_view.dimensions.unit
            returned_1_0_part_1 = response.analytics_event.measurements.add()
            if returned_1_0:
                returned_1_0_part_1.unit = returned_1_0
            returned_1_1 = response_1.result.status
            if returned_1_1:
                response.result.status = returned_1_1
            echoed_0 = request.analytics_event_id
            response.analytics_event.analytics_event_id = echoed_0
            echoed_1 = request.analytics_event.kind
            response.analytics_event.kind = echoed_1
            return response

    async def handle_comment_analytics_event_approval(
        self,
        request: analytics_v1_analytics_event_approval_service_pb2.CommentAnalyticsEventApprovalRequest
    ) -> analytics_v1_analytics_event_approval_service_pb2.CommentAnalyticsEventApprovalResponse:
        """Comments an analytics event."""
        deps = self.deps
        response = analytics_v1_analytics_event_approval_service_pb2.CommentAnalyticsEventApprovalResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CommentAnalyticsEventApproval', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'CommentAnalyticsEventApproval',
                {'reason': request.reason}
            )
            await deps.repository.save_analytics_event(request.context.tenant_id, request.analytics_event)
            response_0 = pipelines_v1_pipeline_run_sync_service_pb2.ResolvePipelineRunConflictResponse()
            response_1 = customers_v1_consent_record_validation_service_pb2.ValidateConsentRecordResponse()
            response_2 = pipelines_v1_pipeline_run_sync_service_pb2.SyncPipelineRunsResponse()
            response_3 = featurestore_v1_entity_reporting_service_pb2.ShareEntityReportResponse()
            for item_0 in request.analytics_event.measurements:
                outgoing_0 = pipelines_v1_pipeline_run_sync_service_pb2.ResolvePipelineRunConflictRequest(
                    context=request.context,
                    pipeline_run=pipelines_v1_pipelines_pb2.PipelineRun(
                        history=[pipelines_v1_pipelines_pb2.PipelineRunStatusChange(changed_at=item_0.observed_at)]
                    )
                )
                response_0 = await deps.clients.pipelines_pipeline_run_sync.ResolvePipelineRunConflict(
                    outgoing_0,
                    timeout=deps.settings.timeout
                )
            outgoing_1 = customers_v1_consent_record_validation_service_pb2.ValidateConsentRecordRequest(
                consent_record=customers_v1_customers_pb2.ConsentRecord(
                    subject=customers_v1_refs_pb2.HouseholdRef(
                        display_name=request.analytics_event.subject.display_name
                    )
                ),
                context=request.context,
                details=customers_v1_consent_record_validation_service_pb2.ValidateConsentRecordRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(phone=response_0.pipeline_run.requester.phone)
                )
            )
            document_1 = MessageToDict(outgoing_1, preserving_proto_field_name=True)
            outgoing_1 = ParseDict(
                document_1,
                customers_v1_consent_record_validation_service_pb2.ValidateConsentRecordRequest()
            )
            response_1 = await deps.clients.customers_consent_record_validation.ValidateConsentRecord(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = pipelines_v1_pipeline_run_sync_service_pb2.SyncPipelineRunsRequest(
                context=request.context,
                pipeline_run=pipelines_v1_pipelines_pb2.PipelineRun(
                    assignee=identity_v1_refs_pb2.UserRef(user_id=request.details.approver.user_id),
                    audit=common_v1_audit_pb2.AuditInfo(etag=response_0.pipeline_run.audit.etag),
                    customer=pipelines_v1_refs_pb2.PipelineRef(
                        display_name=request.analytics_event.subject.display_name
                    ),
                    sla=pipelines_v1_pipelines_pb2.PipelineRunSla(breached=response_0.pipeline_run.sla.breached)
                )
            )
            document_2 = MessageToJson(outgoing_2, preserving_proto_field_name=True)
            outgoing_2 = Parse(document_2, pipelines_v1_pipeline_run_sync_service_pb2.SyncPipelineRunsRequest())
            response_2 = await deps.clients.pipelines_pipeline_run_sync.SyncPipelineRuns(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            outgoing_3 = featurestore_v1_entity_reporting_service_pb2.ShareEntityReportRequest()
            outgoing_3.context.CopyFrom(request.context)
            outgoing_3.details.recipient.email = response_2.pipeline_run.requester.email
            merged_3 = featurestore_v1_entity_reporting_service_pb2.ShareEntityReportRequest()
            merged_3.MergeFrom(outgoing_3)
            outgoing_3.CopyFrom(merged_3)
            response_3 = await deps.clients.featurestore_entity_reporting.ShareEntityReport(
                outgoing_3,
                timeout=deps.settings.timeout
            )
            returned_1_0 = response_1.consent_record.correlation_id
            if returned_1_0:
                response.result.correlation_id = returned_1_0
            returned_1_1 = response_1.consent_record.subject.display_name
            if returned_1_1:
                response.analytics_event.subject.display_name = returned_1_1
            returned_2_0 = response_2.result.correlation_id
            if returned_2_0:
                response.result.correlation_id = returned_2_0
            returned_2_1 = response_2.result.reference_ids
            response.result.reference_ids.extend(returned_2_1)
            returned_3_0 = response_3.result.correlation_id
            if returned_3_0:
                response.analytics_event.correlation_id = returned_3_0
            returned_3_1 = response_3.outcome.status
            if returned_3_1:
                response.result.status = returned_3_1
            echoed_0 = request.analytics_event_id
            response.analytics_event.analytics_event_id = echoed_0
            echoed_1 = request.details.effective_at
            response.outcome.effective_at.CopyFrom(echoed_1)
            return response

    async def handle_escalate_analytics_event(
        self,
        request: analytics_v1_analytics_event_approval_service_pb2.EscalateAnalyticsEventRequest
    ) -> analytics_v1_analytics_event_approval_service_pb2.EscalateAnalyticsEventResponse:
        """Escalates an analytics event."""
        deps = self.deps
        response = analytics_v1_analytics_event_approval_service_pb2.EscalateAnalyticsEventResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('EscalateAnalyticsEvent', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'EscalateAnalyticsEvent', {'reason': request.reason})
            await deps.repository.save_analytics_event(request.context.tenant_id, request.analytics_event)
            response_0 = identity_v1_user_validation_service_pb2.CheckUserEligibilityResponse()
            response_1 = customers_v1_customer_service_pb2.BatchGetCustomersResponse()
            response_2 = billing_v1_billing_account_query_service_pb2.FindBillingAccountsResponse()
            outgoing_0 = identity_v1_user_validation_service_pb2.CheckUserEligibilityRequest(
                context=request.context,
                user=identity_v1_identity_pb2.User(
                    relationship_manager=identity_v1_refs_pb2.UserRef(
                        display_name=request.details.approver.display_name
                    )
                )
            )
            outgoing_1 = customers_v1_customer_service_pb2.BatchGetCustomersRequest(context=request.context)
            response_0, response_1 = await asyncio.gather(
                deps.clients.identity_user_validation.CheckUserEligibility(outgoing_0, timeout=deps.settings.timeout),
                deps.clients.customers_customer.BatchGetCustomers(outgoing_1, timeout=deps.settings.timeout),
            )
            command_2 = AnalyticsEventApprovalEscalateAnalyticsEvent2Command(
                context=request.context,
                filter_region=response_0.user.primary_address.region,
                filter_created_after=response_0.user.audit.created_at,
                filter_owner_id=request.analytics_event.subject.funnel_id,
                filter_labels=dict(request.analytics_event.attributes)
            )
            outgoing_2 = to_analytics_event_approval_escalate_analytics_event2_command(command_2)
            response_2 = await deps.clients.billing_billing_account_query.FindBillingAccounts(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.outcome.status
            if returned_0_0:
                response.result.status = returned_0_0
            returned_1_0 = response_1.result.correlation_id
            if returned_1_0:
                response.analytics_event.correlation_id = returned_1_0
            returned_1_1 = response_1.result.status
            if returned_1_1:
                response.outcome.status = returned_1_1
            returned_2_0 = response_2.result.status
            if returned_2_0:
                response.outcome.status = returned_2_0
            echoed_0 = request.analytics_event_id
            response.analytics_event.analytics_event_id = echoed_0
            echoed_1 = request.analytics_event.subject
            response.analytics_event.subject.CopyFrom(echoed_1)
            return response

    async def handle_list_pending_analytics_events(
        self,
        request: analytics_v1_analytics_event_approval_service_pb2.ListPendingAnalyticsEventsRequest
    ) -> analytics_v1_analytics_event_approval_service_pb2.ListPendingAnalyticsEventsResponse:
        """Lists analytics events a page at a time."""
        deps = self.deps
        response = analytics_v1_analytics_event_approval_service_pb2.ListPendingAnalyticsEventsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ListPendingAnalyticsEvents', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ListPendingAnalyticsEvents',
                {'order_by': request.order_by}
            )
            response_0 = customers_v1_consent_record_validation_service_pb2.ExplainConsentRecordDecisionResponse()
            outgoing_0 = customers_v1_consent_record_validation_service_pb2.ExplainConsentRecordDecisionRequest(
                consent_record=customers_v1_customers_pb2.ConsentRecord(
                    correlation_id=request.filter.owner_id,
                    measurements=[
                        customers_v1_customers_pb2.ConsentRecordMeasurement(observed_at=request.filter.created_after)
                    ]
                ),
                context=request.context,
                details=customers_v1_consent_record_validation_service_pb2.ExplainConsentRecordDecisionRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(email=request.context.actor.email),
                    locale=request.context.locale
                )
            )
            response_0 = await deps.clients.customers_consent_record_validation.ExplainConsentRecordDecision(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.consent_record.subject.display_name
            returned_0_0_part_0 = response.analytics_events.add()
            if returned_0_0:
                returned_0_0_part_0.subject.display_name = returned_0_0
            return response

    async def handle_recall_analytics_event(
        self,
        request: analytics_v1_analytics_event_approval_service_pb2.RecallAnalyticsEventRequest
    ) -> analytics_v1_analytics_event_approval_service_pb2.RecallAnalyticsEventResponse:
        """Recalls an analytics event."""
        deps = self.deps
        response = analytics_v1_analytics_event_approval_service_pb2.RecallAnalyticsEventResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('RecallAnalyticsEvent', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'RecallAnalyticsEvent', {'reason': request.reason})
            await deps.repository.save_analytics_event(request.context.tenant_id, request.analytics_event)
            response_0 = lineage_v1_impact_workflow_service_pb2.SignalImpactWorkflowResponse()
            response_1 = analytics_v1_analytics_report_calculation_service_pb2.CompareAnalyticsReportOptionsResponse()
            outgoing_0 = lineage_v1_impact_workflow_service_pb2.SignalImpactWorkflowRequest(
                context=request.context,
                impact=lineage_v1_lineage_pb2.Impact(
                    assignee=identity_v1_refs_pb2.UserRef(
                        display_name=request.details.approver.display_name,
                        user_id=request.details.approver.user_id
                    )
                )
            )
            send_0 = partial(deps.clients.lineage_impact_workflow.SignalImpactWorkflow, timeout=deps.settings.timeout)
            response_0 = await send_0(outgoing_0)
            outgoing_1 = analytics_v1_analytics_report_calculation_service_pb2.CompareAnalyticsReportOptionsRequest(
                analytics_report=analytics_v1_analytics_pb2.AnalyticsReport(
                    audit=common_v1_audit_pb2.AuditInfo(created_at=response_0.impact.audit.created_at)
                ),
                context=request.context
            )
            response_1 = await hooks.analytics_event_approval_recall_analytics_event1(
                deps.clients.analytics_analytics_report_calculation,
                outgoing_1,
                deps.settings.timeout
            )
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.result.message = returned_0_0
            returned_1_0 = response_1.result.message
            if returned_1_0:
                response.outcome.message = returned_1_0
            echoed_0 = request.analytics_event_id
            response.analytics_event.analytics_event_id = echoed_0
            echoed_1 = request.analytics_event.attributes
            response.analytics_event.attributes.update(echoed_1)
            return response

    async def handle_reject_analytics_event(
        self,
        request: analytics_v1_analytics_event_approval_service_pb2.RejectAnalyticsEventRequest
    ) -> analytics_v1_analytics_event_approval_service_pb2.RejectAnalyticsEventResponse:
        """Rejects an analytics event."""
        deps = self.deps
        response = analytics_v1_analytics_event_approval_service_pb2.RejectAnalyticsEventResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('RejectAnalyticsEvent', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'RejectAnalyticsEvent', {'reason': request.reason})
            await deps.repository.save_analytics_event(request.context.tenant_id, request.analytics_event)
            response_0 = lineage_v1_impact_sync_service_pb2.ListImpactConflictsResponse()
            response_1 = analytics_v1_funnel_calculation_service_pb2.CompareFunnelOptionsResponse()
            outgoing_0 = lineage_v1_impact_sync_service_pb2.ListImpactConflictsRequest(
                context=request.context,
                filter=lineage_v1_impact_sync_service_pb2.ListImpactConflictsRequest.Filter(
                    created_after=request.analytics_event.occurred_at,
                    labels=dict(request.analytics_event.attributes),
                    owner_id=request.analytics_event.subject.funnel_id
                )
            )
            outgoing_1 = analytics_v1_funnel_calculation_service_pb2.CompareFunnelOptionsRequest(
                context=request.context,
                funnel=analytics_v1_analytics_pb2.Funnel(
                    owner=identity_v1_refs_pb2.UserRef(
                        email=request.details.approver.email,
                        user_id=request.details.approver.user_id
                    )
                )
            )
            response_0, response_1 = await asyncio.gather(
                deps.clients.lineage_impact_sync.ListImpactConflicts(outgoing_0, timeout=deps.settings.timeout),
                deps.clients.analytics_funnel_calculation.CompareFunnelOptions(
                    outgoing_1,
                    timeout=deps.settings.timeout
                ),
            )
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.result.message = returned_0_0
            returned_1_0 = response_1.result.reference_ids
            response.result.reference_ids.extend(returned_1_0)
            returned_1_1 = response_1.result.status
            if returned_1_1:
                response.result.status = returned_1_1
            echoed_0 = request.analytics_event_id
            response.analytics_event.analytics_event_id = echoed_0
            echoed_1 = request.analytics_event.subject
            response.analytics_event.subject.CopyFrom(echoed_1)
            return response

    async def handle_submit_analytics_event(
        self,
        request: analytics_v1_analytics_event_approval_service_pb2.SubmitAnalyticsEventRequest
    ) -> analytics_v1_analytics_event_approval_service_pb2.SubmitAnalyticsEventResponse:
        """Submits an analytics event."""
        deps = self.deps
        response = analytics_v1_analytics_event_approval_service_pb2.SubmitAnalyticsEventResponse()
        with tenant_scope(request.context.tenant_id):
            log.info(
                'SubmitAnalyticsEvent',
                extra={'fields': {'analytics_event_id': request.analytics_event.analytics_event_id}}
            )
            await deps.repository.audit(
                request.context.tenant_id,
                'SubmitAnalyticsEvent',
                {'analytics_event_id': request.analytics_event.analytics_event_id}
            )
            await deps.repository.save_analytics_event(request.context.tenant_id, request.analytics_event)
            response_0 = metrics_v1_metric_series_query_service_pb2.SummarizeMetricSeriesesResponse()
            response_1 = analytics_v1_analytics_event_query_service_pb2.ResolveAnalyticsEventsResponse()
            response_2 = audit_v1_audit_event_query_service_pb2.BrowseAuditEventsResponse()
            outgoing_0 = metrics_v1_metric_series_query_service_pb2.SummarizeMetricSeriesesRequest(
                annotations=dict(request.annotations),
                context=request.context,
                details=metrics_v1_metric_series_query_service_pb2.SummarizeMetricSeriesesRequest.Details(
                    filters=dict(request.analytics_event.attributes)
                ),
                reason=request.reason
            )
            steps_0 = [
                partial(
                    deps.clients.metrics_metric_series_query.SummarizeMetricSerieses,
                    outgoing_0,
                    timeout=deps.settings.timeout
                )
            ]
            results_0 = await run_steps(steps_0)
            response_0 = results_0[-1]
            outgoing_1 = analytics_v1_analytics_event_query_service_pb2.ResolveAnalyticsEventsRequest(
                context=request.context
            )
            response_1 = await AnalyticsEventApprovalSubmitAnalyticsEvent1Adapter(
                deps.clients.analytics_analytics_event_query,
                deps.settings.timeout
            )(outgoing_1)
            requests_2: list[audit_v1_audit_event_query_service_pb2.BrowseAuditEventsRequest] = []
            for item_2 in request.analytics_event.measurements:
                outgoing_2 = audit_v1_audit_event_query_service_pb2.BrowseAuditEventsRequest(
                    context=request.context,
                    filter=audit_v1_audit_event_query_service_pb2.BrowseAuditEventsRequest.Filter(
                        created_after=item_2.observed_at,
                        labels=dict(response_0.result.details),
                        owner_id=request.details.approver.user_id
                    )
                )
                requests_2.append(outgoing_2)
            replies_2 = await asyncio.gather(*(
                deps.clients.audit_audit_event_query.BrowseAuditEvents(
                    entry,
                    timeout=deps.settings.timeout
                ) for entry in requests_2
            ))
            if replies_2:
                response_2 = replies_2[-1]
            returned_0_0 = response_0.result.status
            if returned_0_0:
                response.result.status = returned_0_0
            returned_1_0 = response_1.result.message
            if returned_1_0:
                response.result.message = returned_1_0
            returned_1_1 = response_1.result.status
            if returned_1_1:
                response.result.status = returned_1_1
            echoed_0 = request.analytics_event_id
            response.analytics_event.analytics_event_id = echoed_0
            echoed_1 = request.analytics_event.subject
            response.analytics_event.subject.CopyFrom(echoed_1)
            return response
