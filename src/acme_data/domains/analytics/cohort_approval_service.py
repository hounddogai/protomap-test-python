"""Routes cohorts through approval, with escalation and delegation."""

from __future__ import annotations

from collections.abc import AsyncIterator
from dataclasses import dataclass
from functools import partial
from typing import cast
import logging

from google.protobuf.any_pb2 import Any as AnyMessage
from google.protobuf.json_format import MessageToDict
from google.protobuf.json_format import MessageToJson
from google.protobuf.json_format import Parse
from google.protobuf.json_format import ParseDict
import grpc

from acme.analytics.v1 import (
    analytics_event_validation_service_pb2 as analytics_v1_analytics_event_validation_service_pb2,
)
from acme.analytics.v1 import analytics_event_workflow_service_pb2 as analytics_v1_analytics_event_workflow_service_pb2
from acme.analytics.v1 import analytics_pb2 as analytics_v1_analytics_pb2
from acme.analytics.v1 import (
    analytics_report_calculation_service_pb2 as analytics_v1_analytics_report_calculation_service_pb2,
)
from acme.analytics.v1 import (
    analytics_report_calculation_service_pb2_grpc as analytics_v1_analytics_report_calculation_service_pb2_grpc,
)
from acme.analytics.v1 import (
    analytics_report_validation_service_pb2 as analytics_v1_analytics_report_validation_service_pb2,
)
from acme.analytics.v1 import cohort_approval_service_pb2 as analytics_v1_cohort_approval_service_pb2
from acme.analytics.v1 import cohort_approval_service_pb2_grpc as analytics_v1_cohort_approval_service_pb2_grpc
from acme.analytics.v1 import cohort_lifecycle_service_pb2 as analytics_v1_cohort_lifecycle_service_pb2
from acme.analytics.v1 import funnel_validation_service_pb2 as analytics_v1_funnel_validation_service_pb2
from acme.analytics.v1 import refs_pb2 as analytics_v1_refs_pb2
from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.customers.v1 import (
    consent_record_validation_service_pb2 as customers_v1_consent_record_validation_service_pb2,
)
from acme.customers.v1 import customer_query_service_pb2 as customers_v1_customer_query_service_pb2
from acme.customers.v1 import (
    customer_segment_calculation_service_pb2 as customers_v1_customer_segment_calculation_service_pb2,
)
from acme.customers.v1 import (
    customer_segment_validation_service_pb2 as customers_v1_customer_segment_validation_service_pb2,
)
from acme.customers.v1 import customer_validation_service_pb2 as customers_v1_customer_validation_service_pb2
from acme.customers.v1 import customers_pb2 as customers_v1_customers_pb2
from acme.customers.v1 import refs_pb2 as customers_v1_refs_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.lineage.v1 import impact_lifecycle_service_pb2 as lineage_v1_impact_lifecycle_service_pb2
from acme.lineage.v1 import lineage_node_approval_service_pb2 as lineage_v1_lineage_node_approval_service_pb2
from acme.lineage.v1 import lineage_pb2 as lineage_v1_lineage_pb2
from acme.metrics.v1 import metric_alert_validation_service_pb2 as metrics_v1_metric_alert_validation_service_pb2
from acme.metrics.v1 import metrics_pb2 as metrics_v1_metrics_pb2
from acme.modelregistry.v1 import model_version_sync_service_pb2 as modelregistry_v1_model_version_sync_service_pb2
from acme.modelregistry.v1 import modelregistry_pb2 as modelregistry_v1_modelregistry_pb2
from acme.pipelines.v1 import pipeline_sync_service_pb2 as pipelines_v1_pipeline_sync_service_pb2

from acme_data.domains.analytics import hooks
from acme_data.domains.analytics.adapters import CohortApprovalEscalateCohort2Adapter
from acme_data.domains.analytics.adapters import CohortApprovalEscalateCohort2Port
from acme_data.domains.analytics.dependencies import Dependencies
from acme_data.domains.analytics.models import CohortApprovalDelegateCohortApproval1Command
from acme_data.domains.analytics.models import CohortApprovalDelegateCohortApproval2Command
from acme_data.domains.analytics.models import to_cohort_approval_delegate_cohort_approval1_command
from acme_data.domains.analytics.models import to_cohort_approval_delegate_cohort_approval2_command
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_id
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


@dataclass(slots=True)
class CohortApprovalServicer(analytics_v1_cohort_approval_service_pb2_grpc.CohortApprovalServiceServicer):
    deps: Dependencies

    @rpc_errors
    async def ApproveCohort(
        self, request: analytics_v1_cohort_approval_service_pb2.ApproveCohortRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_cohort_approval_service_pb2.ApproveCohortResponse:
        """Approves a cohort."""
        return await self.handle_approve_cohort(request)

    @rpc_errors
    async def CommentCohortApproval(
        self, request: analytics_v1_cohort_approval_service_pb2.CommentCohortApprovalRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_cohort_approval_service_pb2.CommentCohortApprovalResponse:
        """Comments a cohort."""
        return await self.handle_comment_cohort_approval(request)

    @rpc_errors
    async def DelegateCohortApproval(
        self, request: analytics_v1_cohort_approval_service_pb2.DelegateCohortApprovalRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_cohort_approval_service_pb2.DelegateCohortApprovalResponse:
        """Delegates a cohort."""
        return await self.handle_delegate_cohort_approval(request)

    @rpc_errors
    async def EscalateCohort(
        self, request: analytics_v1_cohort_approval_service_pb2.EscalateCohortRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_cohort_approval_service_pb2.EscalateCohortResponse:
        """Escalates a cohort."""
        return await self.handle_escalate_cohort(request)

    @rpc_errors
    @retry_transient
    async def GetCohortApprovalStatus(
        self, request: analytics_v1_cohort_approval_service_pb2.GetCohortApprovalStatusRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_cohort_approval_service_pb2.GetCohortApprovalStatusResponse:
        """Returns a cohort."""
        return await self.handle_get_cohort_approval_status(request)

    @rpc_errors
    @retry_transient
    async def ListPendingCohorts(
        self, request: analytics_v1_cohort_approval_service_pb2.ListPendingCohortsRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_cohort_approval_service_pb2.ListPendingCohortsResponse:
        """Lists cohorts a page at a time."""
        return await self.handle_list_pending_cohorts(request)

    @rpc_errors
    async def RecallCohort(
        self, request: analytics_v1_cohort_approval_service_pb2.RecallCohortRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_cohort_approval_service_pb2.RecallCohortResponse:
        """Recalls a cohort."""
        return await self.handle_recall_cohort(request)

    @rpc_errors
    async def RejectCohort(
        self, request: analytics_v1_cohort_approval_service_pb2.RejectCohortRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_cohort_approval_service_pb2.RejectCohortResponse:
        """Rejects a cohort."""
        return await self.handle_reject_cohort(request)

    @rpc_errors
    async def SubmitCohort(
        self, request: analytics_v1_cohort_approval_service_pb2.SubmitCohortRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_cohort_approval_service_pb2.SubmitCohortResponse:
        """Submits a cohort."""
        return await self.handle_submit_cohort(request)

    async def handle_approve_cohort(
        self,
        request: analytics_v1_cohort_approval_service_pb2.ApproveCohortRequest
    ) -> analytics_v1_cohort_approval_service_pb2.ApproveCohortResponse:
        """Approves a cohort."""
        deps = self.deps
        response = analytics_v1_cohort_approval_service_pb2.ApproveCohortResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ApproveCohort', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'ApproveCohort', {'reason': request.reason})
            await deps.repository.save_cohort(request.context.tenant_id, request.cohort)
            response_0 = analytics_v1_analytics_event_workflow_service_pb2.SignalAnalyticsEventWorkflowResponse()
            outgoing_0 = analytics_v1_analytics_event_workflow_service_pb2.SignalAnalyticsEventWorkflowRequest(
                analytics_event=analytics_v1_analytics_pb2.AnalyticsEvent(
                    subject=analytics_v1_refs_pb2.FunnelRef(
                        display_name=request.details.approver.display_name,
                        version=request.cohort.version
                    )
                ),
                context=request.context,
                details=analytics_v1_analytics_event_workflow_service_pb2.SignalAnalyticsEventWorkflowRequest.Details(
                    notify=common_v1_contact_pb2.ContactInfo(email=request.cohort.owner.email),
                    parameters=dict(request.cohort.parameters)
                )
            )
            document_0 = MessageToJson(outgoing_0, preserving_proto_field_name=True)
            outgoing_0 = Parse(
                document_0,
                analytics_v1_analytics_event_workflow_service_pb2.SignalAnalyticsEventWorkflowRequest()
            )
            response_0 = await deps.clients.analytics_analytics_event_workflow.SignalAnalyticsEventWorkflow(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.outcome.message = returned_0_0
            returned_0_1 = response_0.outcome.next_steps
            response.outcome.next_steps.extend(returned_0_1)
            echoed_0 = request.cohort_id
            response.cohort.cohort_id = echoed_0
            echoed_1 = request.cohort.version
            response.cohort.version = echoed_1
            return response

    async def handle_comment_cohort_approval(
        self,
        request: analytics_v1_cohort_approval_service_pb2.CommentCohortApprovalRequest
    ) -> analytics_v1_cohort_approval_service_pb2.CommentCohortApprovalResponse:
        """Comments a cohort."""
        deps = self.deps
        response = analytics_v1_cohort_approval_service_pb2.CommentCohortApprovalResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CommentCohortApproval', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'CommentCohortApproval', {'reason': request.reason})
            await deps.repository.save_cohort(request.context.tenant_id, request.cohort)
            response_0 = pipelines_v1_pipeline_sync_service_pb2.PushPipelineResponse()
            response_1 = customers_v1_customer_validation_service_pb2.ValidateCustomerResponse()
            outgoing_0 = pipelines_v1_pipeline_sync_service_pb2.PushPipelineRequest()
            outgoing_0.context.CopyFrom(request.context)
            outgoing_0.pipeline.audit.etag = request.cohort.audit.etag
            outgoing_0.pipeline.audit.created_by = request.cohort.audit.created_by
            merged_0 = pipelines_v1_pipeline_sync_service_pb2.PushPipelineRequest()
            merged_0.MergeFrom(outgoing_0)
            outgoing_0.CopyFrom(merged_0)
            response_0 = await deps.clients.pipelines_pipeline_sync.PushPipeline(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = customers_v1_customer_validation_service_pb2.ValidateCustomerRequest(
                context=request.context,
                customer=customers_v1_customers_pb2.Customer(
                    audit=common_v1_audit_pb2.AuditInfo(etag=response_0.pipeline.audit.etag),
                    primary_address=common_v1_address_pb2.PostalAddress(locality=response_0.pipeline.location.locality)
                )
            )
            envelope_1 = AnyMessage()
            envelope_1.Pack(outgoing_1)
            outgoing_1 = customers_v1_customer_validation_service_pb2.ValidateCustomerRequest()
            if not envelope_1.Unpack(outgoing_1):
                raise ValueError("partner envelope contains the wrong request type")
            response_1 = await deps.clients.customers_customer_validation.ValidateCustomer(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.pipeline.organizer.user_id
            if returned_0_0:
                response.cohort.owner.user_id = returned_0_0
            returned_1_0 = response_1.result.details
            response.result.details.update(returned_1_0)
            echoed_0 = request.cohort_id
            response.cohort.cohort_id = echoed_0
            echoed_1 = request.cohort.status
            response.cohort.status = echoed_1
            return response

    async def handle_delegate_cohort_approval(
        self,
        request: analytics_v1_cohort_approval_service_pb2.DelegateCohortApprovalRequest
    ) -> analytics_v1_cohort_approval_service_pb2.DelegateCohortApprovalResponse:
        """Delegates a cohort."""
        deps = self.deps
        response = analytics_v1_cohort_approval_service_pb2.DelegateCohortApprovalResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('DelegateCohortApproval', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'DelegateCohortApproval', {'reason': request.reason})
            await deps.repository.save_cohort(request.context.tenant_id, request.cohort)
            response_0 = analytics_v1_analytics_report_calculation_service_pb2.CalculateAnalyticsReportResponse()
            response_1 = analytics_v1_analytics_report_validation_service_pb2.ExplainAnalyticsReportDecisionResponse()
            response_2 = analytics_v1_cohort_lifecycle_service_pb2.GetCohortLifecycleResponse()
            response_3 = customers_v1_customer_validation_service_pb2.ValidateCustomerResponse()
            outgoing_0 = analytics_v1_analytics_report_calculation_service_pb2.CalculateAnalyticsReportRequest(
                analytics_report=analytics_v1_analytics_pb2.AnalyticsReport(
                    audit=common_v1_audit_pb2.AuditInfo(updated_by=request.cohort.audit.updated_by)
                ),
                context=request.context
            )
            registered_0 = cast(
                analytics_v1_analytics_report_calculation_service_pb2_grpc.AnalyticsReportCalculationServiceStub,
                deps.clients.registry['acme.analytics.v1.AnalyticsReportCalculationService']
            )
            response_0 = await registered_0.CalculateAnalyticsReport(outgoing_0, timeout=deps.settings.timeout)
            command_1 = CohortApprovalDelegateCohortApproval1Command(
                context=request.context,
                analytics_report_lines_tax_amount=request.cohort.discount.amount,
                analytics_report_counterparty_display_name=request.details.approver.display_name,
                analytics_report_audit_updated_at=request.cohort.audit.updated_at,
                analytics_report_audit_created_at=response_0.analytics_report.audit.created_at
            )
            outgoing_1 = to_cohort_approval_delegate_cohort_approval1_command(command_1)
            response_1 = await deps.clients.analytics_analytics_report_validation.ExplainAnalyticsReportDecision(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            command_2 = CohortApprovalDelegateCohortApproval2Command.model_validate(
                {'context': request.context, 'cohort_id': request.cohort.cohort_id}
            )
            outgoing_2 = to_cohort_approval_delegate_cohort_approval2_command(command_2)
            response_2 = await deps.clients.analytics_cohort_lifecycle.GetCohortLifecycle(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            outgoing_3 = customers_v1_customer_validation_service_pb2.ValidateCustomerRequest(
                context=request.context,
                customer=customers_v1_customers_pb2.Customer(
                    primary_address=common_v1_address_pb2.PostalAddress(
                        locality=response_1.analytics_report.billing_address.locality
                    )
                )
            )
            send_3 = partial(deps.clients.customers_customer_validation.ValidateCustomer, timeout=deps.settings.timeout)
            response_3 = await send_3(outgoing_3)
            returned_0_0 = response_0.analytics_report.audit.updated_by
            if returned_0_0:
                response.cohort.audit.updated_by = returned_0_0
            returned_0_1 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_1)
            returned_1_0 = response_1.analytics_report.counterparty.email
            if returned_1_0:
                response.cohort.owner.email = returned_1_0
            returned_2_0 = response_2.cohort.priority
            if returned_2_0:
                response.cohort.priority = returned_2_0
            returned_2_1 = response_2.result.status
            if returned_2_1:
                response.outcome.status = returned_2_1
            returned_3_0 = response_3.customer.audit.updated_at
            if returned_3_0.ListFields():
                response.cohort.audit.updated_at.MergeFrom(returned_3_0)
            returned_3_1 = response_3.customer.relationship_manager.user_id
            if returned_3_1:
                response.cohort.owner.user_id = returned_3_1
            echoed_0 = request.cohort_id
            response.cohort.cohort_id = echoed_0
            echoed_1 = request.cohort.effective
            response.cohort.effective.CopyFrom(echoed_1)
            return response

    async def handle_escalate_cohort(
        self,
        request: analytics_v1_cohort_approval_service_pb2.EscalateCohortRequest
    ) -> analytics_v1_cohort_approval_service_pb2.EscalateCohortResponse:
        """Escalates a cohort."""
        deps = self.deps
        response = analytics_v1_cohort_approval_service_pb2.EscalateCohortResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('EscalateCohort', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'EscalateCohort', {'reason': request.reason})
            await deps.repository.save_cohort(request.context.tenant_id, request.cohort)
            response_0 = customers_v1_customer_segment_validation_service_pb2.CheckCustomerSegmentEligibilityResponse()
            response_1 = analytics_v1_funnel_validation_service_pb2.NormalizeFunnelResponse()
            response_2 = analytics_v1_analytics_event_workflow_service_pb2.ResumeAnalyticsEventWorkflowResponse()
            outgoing_0 = customers_v1_customer_segment_validation_service_pb2.CheckCustomerSegmentEligibilityRequest(
                context=request.context,
                customer_segment=customers_v1_customers_pb2.CustomerSegment(
                    audit=common_v1_audit_pb2.AuditInfo(updated_at=request.cohort.audit.updated_at),
                    owner=identity_v1_refs_pb2.UserRef(
                        email=request.details.approver.email,
                        user_id=request.cohort.owner.user_id
                    )
                )
            )
            response_0 = await hooks.cohort_approval_escalate_cohort0(
                deps.clients.customers_customer_segment_validation,
                outgoing_0,
                deps.settings.timeout
            )
            outgoing_1 = analytics_v1_funnel_validation_service_pb2.NormalizeFunnelRequest()
            outgoing_1.context.CopyFrom(request.context)
            outgoing_1.funnel.audit.created_by = response_0.customer_segment.audit.created_by
            outgoing_1.funnel.owner.display_name = request.details.approver.display_name
            outgoing_1.context.tenant_id = tenant_id.get()
            response_1 = await deps.clients.analytics_funnel_validation.NormalizeFunnel(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = analytics_v1_analytics_event_workflow_service_pb2.ResumeAnalyticsEventWorkflowRequest(
                context=request.context,
                details=analytics_v1_analytics_event_workflow_service_pb2.ResumeAnalyticsEventWorkflowRequest.Details(
                    notify=common_v1_contact_pb2.ContactInfo(email=response_0.customer_segment.owner.email)
                )
            )
            port_2: CohortApprovalEscalateCohort2Port = CohortApprovalEscalateCohort2Adapter(
                deps.clients.analytics_analytics_event_workflow,
                deps.settings.timeout
            )
            response_2 = await port_2.execute(outgoing_2)
            returned_0_0 = response_0.customer_segment.scopes
            response.cohort.scopes.extend(returned_0_0)
            returned_1_0 = response_1.funnel.audit.updated_at
            if returned_1_0.ListFields():
                response.cohort.audit.updated_at.MergeFrom(returned_1_0)
            returned_2_0 = response_2.result.status
            if returned_2_0:
                response.outcome.status = returned_2_0
            returned_2_1 = response_2.result.details
            response.result.details.update(returned_2_1)
            echoed_0 = request.cohort_id
            response.cohort.cohort_id = echoed_0
            echoed_1 = request.cohort.description
            response.cohort.description = echoed_1
            return response

    async def handle_get_cohort_approval_status(
        self,
        request: analytics_v1_cohort_approval_service_pb2.GetCohortApprovalStatusRequest
    ) -> analytics_v1_cohort_approval_service_pb2.GetCohortApprovalStatusResponse:
        """Returns a cohort."""
        deps = self.deps
        response = analytics_v1_cohort_approval_service_pb2.GetCohortApprovalStatusResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('GetCohortApprovalStatus', extra={'fields': {'domain': 'analytics'}})
            await deps.repository.audit(request.context.tenant_id, 'GetCohortApprovalStatus', {})
            response_0 = lineage_v1_impact_lifecycle_service_pb2.ScheduleImpactExpiryResponse()
            outgoing_0 = lineage_v1_impact_lifecycle_service_pb2.ScheduleImpactExpiryRequest(
                context=request.context,
                impact=lineage_v1_lineage_pb2.Impact(
                    customer=customers_v1_refs_pb2.CustomerRef(email=request.context.actor.email)
                )
            )
            response_0 = await deps.clients.lineage_impact_lifecycle.ScheduleImpactExpiry(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.impact.customer.email
            if returned_0_0:
                response.cohort.owner.email = returned_0_0
            echoed_0 = request.cohort_id
            response.cohort.cohort_id = echoed_0
            return response

    async def handle_list_pending_cohorts(
        self,
        request: analytics_v1_cohort_approval_service_pb2.ListPendingCohortsRequest
    ) -> analytics_v1_cohort_approval_service_pb2.ListPendingCohortsResponse:
        """Lists cohorts a page at a time."""
        deps = self.deps
        response = analytics_v1_cohort_approval_service_pb2.ListPendingCohortsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ListPendingCohorts', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(request.context.tenant_id, 'ListPendingCohorts', {'order_by': request.order_by})
            response_0 = customers_v1_consent_record_validation_service_pb2.ExplainConsentRecordDecisionResponse()
            outgoing_0 = customers_v1_consent_record_validation_service_pb2.ExplainConsentRecordDecisionRequest(
                consent_record=customers_v1_customers_pb2.ConsentRecord(
                    attributes=dict(request.filter.labels),
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
            returned_0_0 = response_0.outcome.message
            if returned_0_0:
                response.result.message = returned_0_0
            returned_0_1 = response_0.result.status
            if returned_0_1:
                response.result.status = returned_0_1
            return response

    async def handle_recall_cohort(
        self,
        request: analytics_v1_cohort_approval_service_pb2.RecallCohortRequest
    ) -> analytics_v1_cohort_approval_service_pb2.RecallCohortResponse:
        """Recalls a cohort."""
        deps = self.deps
        response = analytics_v1_cohort_approval_service_pb2.RecallCohortResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('RecallCohort', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'RecallCohort', {'reason': request.reason})
            await deps.repository.save_cohort(request.context.tenant_id, request.cohort)
            response_0 = analytics_v1_analytics_event_workflow_service_pb2.AdvanceAnalyticsEventWorkflowResponse()
            response_1 = customers_v1_customer_segment_calculation_service_pb2.ExplainCustomerSegmentCalculationResponse()
            response_2 = modelregistry_v1_model_version_sync_service_pb2.PullModelVersionsResponse()
            outgoing_0 = analytics_v1_analytics_event_workflow_service_pb2.AdvanceAnalyticsEventWorkflowRequest()
            outgoing_0.context.CopyFrom(request.context)
            outgoing_0.details.notify.email = request.cohort.owner.email
            outgoing_0.analytics_event.subject.display_name = request.details.approver.display_name
            if request.cohort.WhichOneof('action') == 'block':
                outgoing_0.reason = request.cohort.block.reason
            response_0 = await deps.clients.analytics_analytics_event_workflow.AdvanceAnalyticsEventWorkflow(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = customers_v1_customer_segment_calculation_service_pb2.ExplainCustomerSegmentCalculationRequest(
                context=request.context,
                customer_segment=customers_v1_customers_pb2.CustomerSegment(
                    block=customers_v1_customers_pb2.CustomerSegmentBlockAction(reason=request.cohort.block.reason),
                    owner=identity_v1_refs_pb2.UserRef(user_id=request.details.approver.user_id)
                )
            )
            response_1 = await deps.clients.customers_customer_segment_calculation.ExplainCustomerSegmentCalculation(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = modelregistry_v1_model_version_sync_service_pb2.PullModelVersionsRequest(
                context=request.context,
                model_version=modelregistry_v1_modelregistry_pb2.ModelVersion(
                    subject=customers_v1_refs_pb2.CustomerRef(email=request.cohort.owner.email)
                )
            )
            method_name_2 = 'PullModelVersions'
            response_2 = await getattr(
                deps.clients.modelregistry_model_version_sync,
                method_name_2
            )(outgoing_2, timeout=deps.settings.timeout)
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.result.message = returned_0_0
            returned_0_1 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_1)
            returned_1_0 = response_1.customer_segment.audit.etag
            if returned_1_0:
                response.cohort.audit.etag = returned_1_0
            returned_1_1 = response_1.outcome.message
            if returned_1_1:
                response.result.message = returned_1_1
            returned_2_0 = response_2.outcome.next_steps
            response.outcome.next_steps.extend(returned_2_0)
            echoed_0 = request.cohort_id
            response.cohort.cohort_id = echoed_0
            echoed_1 = request.cohort.parameters
            response.cohort.parameters.update(echoed_1)
            return response

    async def handle_reject_cohort(
        self,
        request: analytics_v1_cohort_approval_service_pb2.RejectCohortRequest
    ) -> analytics_v1_cohort_approval_service_pb2.RejectCohortResponse:
        """Rejects a cohort."""
        deps = self.deps
        response = analytics_v1_cohort_approval_service_pb2.RejectCohortResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('RejectCohort', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'RejectCohort', {'reason': request.reason})
            await deps.repository.save_cohort(request.context.tenant_id, request.cohort)
            response_0 = customers_v1_customer_query_service_pb2.ExportCustomersResponse()
            outgoing_0 = customers_v1_customer_query_service_pb2.ExportCustomersRequest(
                context=request.context,
                filter=customers_v1_customer_query_service_pb2.ExportCustomersRequest.Filter(
                    created_after=request.cohort.audit.updated_at
                )
            )
            async for chunk_0 in deps.clients.customers_customer_query.ExportCustomers(
                outgoing_0,
                timeout=deps.settings.timeout
            ):
                response_0 = chunk_0
            echoed_0 = request.cohort_id
            response.cohort.cohort_id = echoed_0
            echoed_1 = request.cohort.parameters
            response.cohort.parameters.update(echoed_1)
            return response

    async def handle_submit_cohort(
        self,
        request: analytics_v1_cohort_approval_service_pb2.SubmitCohortRequest
    ) -> analytics_v1_cohort_approval_service_pb2.SubmitCohortResponse:
        """Submits a cohort."""
        deps = self.deps
        response = analytics_v1_cohort_approval_service_pb2.SubmitCohortResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SubmitCohort', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'SubmitCohort', {'reason': request.reason})
            await deps.repository.save_cohort(request.context.tenant_id, request.cohort)
            response_0 = lineage_v1_lineage_node_approval_service_pb2.SubmitLineageNodeResponse()
            response_1 = metrics_v1_metric_alert_validation_service_pb2.ValidateMetricAlertResponse()
            response_2 = analytics_v1_analytics_event_validation_service_pb2.PreviewAnalyticsEventResponse()
            response_3 = analytics_v1_analytics_event_workflow_service_pb2.ResumeAnalyticsEventWorkflowResponse()
            outgoing_0 = lineage_v1_lineage_node_approval_service_pb2.SubmitLineageNodeRequest(
                context=request.context,
                lineage_node=lineage_v1_lineage_pb2.LineageNode(
                    children=[
                        lineage_v1_lineage_pb2.LineageNode(
                            children=[
                                lineage_v1_lineage_pb2.LineageNode(
                                    audit=common_v1_audit_pb2.AuditInfo(
                                        created_by=request.cohort.audit.created_by,
                                        updated_at=request.cohort.audit.updated_at,
                                        updated_by=request.cohort.audit.updated_by
                                    ),
                                    manager=identity_v1_refs_pb2.UserRef(
                                        display_name=request.details.approver.display_name
                                    )
                                )
                            ]
                        )
                    ]
                )
            )
            document_0 = MessageToDict(outgoing_0, preserving_proto_field_name=True)
            outgoing_0 = ParseDict(document_0, lineage_v1_lineage_node_approval_service_pb2.SubmitLineageNodeRequest())
            response_0 = await deps.clients.lineage_lineage_node_approval.SubmitLineageNode(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = metrics_v1_metric_alert_validation_service_pb2.ValidateMetricAlertRequest(
                context=request.context,
                metric_alert=metrics_v1_metrics_pb2.MetricAlert(
                    audit=common_v1_audit_pb2.AuditInfo(
                        created_at=request.cohort.audit.created_at,
                        created_by=response_0.lineage_node.audit.created_by
                    ),
                    block=metrics_v1_metrics_pb2.MetricAlertBlockAction(notify_email=request.cohort.block.notify_email),
                    owner=identity_v1_refs_pb2.UserRef(display_name=request.cohort.owner.display_name)
                )
            )
            document_1 = MessageToJson(outgoing_1, preserving_proto_field_name=True)
            outgoing_1 = Parse(document_1, metrics_v1_metric_alert_validation_service_pb2.ValidateMetricAlertRequest())
            response_1 = await deps.clients.metrics_metric_alert_validation.ValidateMetricAlert(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = analytics_v1_analytics_event_validation_service_pb2.PreviewAnalyticsEventRequest()
            outgoing_2.context.CopyFrom(request.context)
            outgoing_2.analytics_event.subject.display_name = response_0.lineage_node.manager.display_name
            merged_2 = analytics_v1_analytics_event_validation_service_pb2.PreviewAnalyticsEventRequest()
            merged_2.MergeFrom(outgoing_2)
            outgoing_2.CopyFrom(merged_2)
            response_2 = await deps.clients.analytics_analytics_event_validation.PreviewAnalyticsEvent(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            outgoing_3 = analytics_v1_analytics_event_workflow_service_pb2.ResumeAnalyticsEventWorkflowRequest(
                analytics_event=analytics_v1_analytics_pb2.AnalyticsEvent(
                    subject=analytics_v1_refs_pb2.FunnelRef(
                        display_name=request.details.approver.display_name,
                        funnel_id=response_2.analytics_event.subject.funnel_id,
                        version=response_1.metric_alert.version
                    )
                ),
                context=request.context,
                details=analytics_v1_analytics_event_workflow_service_pb2.ResumeAnalyticsEventWorkflowRequest.Details(
                    notify=common_v1_contact_pb2.ContactInfo(email=request.cohort.owner.email)
                )
            )
            envelope_3 = AnyMessage()
            envelope_3.Pack(outgoing_3)
            outgoing_3 = analytics_v1_analytics_event_workflow_service_pb2.ResumeAnalyticsEventWorkflowRequest()
            if not envelope_3.Unpack(outgoing_3):
                raise ValueError("partner envelope contains the wrong request type")
            response_3 = await deps.clients.analytics_analytics_event_workflow.ResumeAnalyticsEventWorkflow(
                outgoing_3,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.outcome.message
            if returned_0_0:
                response.outcome.message = returned_0_0
            returned_0_1 = response_0.result.message
            if returned_0_1:
                response.result.message = returned_0_1
            returned_1_0 = response_1.result.message
            if returned_1_0:
                response.result.message = returned_1_0
            returned_1_1 = response_1.result.status
            if returned_1_1:
                response.outcome.status = returned_1_1
            returned_2_0 = response_2.outcome.reference_id
            if returned_2_0:
                response.outcome.reference_id = returned_2_0
            returned_3_0 = response_3.outcome.next_steps
            response.outcome.next_steps.extend(returned_3_0)
            returned_3_1 = response_3.result.status
            if returned_3_1:
                response.outcome.status = returned_3_1
            echoed_0 = request.cohort_id
            response.cohort.cohort_id = echoed_0
            echoed_1 = request.cohort.priority
            response.cohort.priority = echoed_1
            return response
