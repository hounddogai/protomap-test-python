"""Application workflow for Cohort Lifecycle."""

from __future__ import annotations

from functools import partial
from typing import cast
import logging

from google.protobuf.any_pb2 import Any as AnyMessage
from google.protobuf.json_format import MessageToJson
from google.protobuf.json_format import Parse

from acme.analytics.v1 import analytics_event_query_service_pb2 as analytics_v1_analytics_event_query_service_pb2
from acme.analytics.v1 import analytics_pb2 as analytics_v1_analytics_pb2
from acme.analytics.v1 import cohort_calculation_service_pb2 as analytics_v1_cohort_calculation_service_pb2
from acme.analytics.v1 import cohort_lifecycle_service_pb2 as analytics_v1_cohort_lifecycle_service_pb2
from acme.analytics.v1 import funnel_calculation_service_pb2 as analytics_v1_funnel_calculation_service_pb2
from acme.analytics.v1 import funnel_query_service_pb2 as analytics_v1_funnel_query_service_pb2
from acme.checkout.v1 import checkout_session_query_service_pb2 as checkout_v1_checkout_session_query_service_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.customers.v1 import customer_calculation_service_pb2 as customers_v1_customer_calculation_service_pb2
from acme.customers.v1 import (
    customer_segment_validation_service_pb2 as customers_v1_customer_segment_validation_service_pb2,
)
from acme.customers.v1 import customers_pb2 as customers_v1_customers_pb2
from acme.documents.v1 import document_query_service_pb2 as documents_v1_document_query_service_pb2
from acme.documents.v1 import document_query_service_pb2_grpc as documents_v1_document_query_service_pb2_grpc
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.lineage.v1 import lineage_node_workflow_service_pb2 as lineage_v1_lineage_node_workflow_service_pb2
from acme.lineage.v1 import lineage_pb2 as lineage_v1_lineage_pb2
from acme.pipelines.v1 import pipeline_reporting_service_pb2 as pipelines_v1_pipeline_reporting_service_pb2

from acme_data.domains.analytics import hooks
from acme_data.domains.analytics.adapters import CohortLifecycleSuspendCohort1Adapter
from acme_data.domains.analytics.adapters import CohortLifecycleSuspendCohort1Port
from acme_data.domains.analytics.adapters import CohortLifecycleSuspendCohort3Adapter
from acme_data.domains.analytics.dependencies import Dependencies
from acme_data.domains.analytics.models import CohortLifecycleRenewCohort0Command
from acme_data.domains.analytics.models import to_cohort_lifecycle_renew_cohort0_command
from acme_data.platform.rpc import run_steps
from acme_data.platform.tenancy import tenant_id
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class CohortLifecycleServicerWorkflow:
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    async def handle_activate_cohort(
        self,
        request: analytics_v1_cohort_lifecycle_service_pb2.ActivateCohortRequest
    ) -> analytics_v1_cohort_lifecycle_service_pb2.ActivateCohortResponse:
        """Activates a cohort."""
        deps = self.deps
        response = analytics_v1_cohort_lifecycle_service_pb2.ActivateCohortResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ActivateCohort', extra={'fields': {'reason_code': request.details.reason_code}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ActivateCohort',
                {'reason_code': request.details.reason_code}
            )
            response_0 = pipelines_v1_pipeline_reporting_service_pb2.SchedulePipelineReportResponse()
            response_1 = customers_v1_customer_segment_validation_service_pb2.ValidateCustomerSegmentResponse()
            outgoing_0 = pipelines_v1_pipeline_reporting_service_pb2.SchedulePipelineReportRequest(
                context=request.context,
                reason=request.reason
            )
            document_0 = MessageToJson(outgoing_0, preserving_proto_field_name=True)
            outgoing_0 = Parse(document_0, pipelines_v1_pipeline_reporting_service_pb2.SchedulePipelineReportRequest())
            response_0 = await deps.clients.pipelines_pipeline_reporting.SchedulePipelineReport(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = customers_v1_customer_segment_validation_service_pb2.ValidateCustomerSegmentRequest()
            outgoing_1.context.CopyFrom(request.context)
            outgoing_1.customer_segment.owner.user_id = request.details.new_owner.user_id
            outgoing_1.customer_segment.owner.display_name = request.details.new_owner.display_name
            merged_1 = customers_v1_customer_segment_validation_service_pb2.ValidateCustomerSegmentRequest()
            merged_1.MergeFrom(outgoing_1)
            outgoing_1.CopyFrom(merged_1)
            response_1 = await deps.clients.customers_customer_segment_validation.ValidateCustomerSegment(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.correlation_id
            if returned_0_0:
                response.result.correlation_id = returned_0_0
            returned_1_0 = response_1.customer_segment.parameters
            response.cohort.parameters.update(returned_1_0)
            returned_1_1 = response_1.customer_segment.audit.updated_by
            if returned_1_1:
                response.cohort.audit.updated_by = returned_1_1
            echoed_0 = request.cohort_id
            response.cohort.cohort_id = echoed_0
            echoed_1 = request.details.effective_at
            response.outcome.effective_at.CopyFrom(echoed_1)
            return response

    async def handle_expire_cohort(
        self,
        request: analytics_v1_cohort_lifecycle_service_pb2.ExpireCohortRequest
    ) -> analytics_v1_cohort_lifecycle_service_pb2.ExpireCohortResponse:
        """Expires a cohort."""
        deps = self.deps
        response = analytics_v1_cohort_lifecycle_service_pb2.ExpireCohortResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ExpireCohort', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'ExpireCohort', {'reason': request.reason})
            response_0 = lineage_v1_lineage_node_workflow_service_pb2.AdvanceLineageNodeWorkflowResponse()
            response_1 = documents_v1_document_query_service_pb2.SummarizeDocumentsResponse()
            outgoing_0 = lineage_v1_lineage_node_workflow_service_pb2.AdvanceLineageNodeWorkflowRequest(
                context=request.context,
                details=lineage_v1_lineage_node_workflow_service_pb2.AdvanceLineageNodeWorkflowRequest.Details(
                    notify=common_v1_contact_pb2.ContactInfo(phone=request.details.notify_contact.phone)
                ),
                lineage_node=lineage_v1_lineage_pb2.LineageNode(
                    children=[
                        lineage_v1_lineage_pb2.LineageNode(
                            children=[
                                lineage_v1_lineage_pb2.LineageNode(
                                    manager=identity_v1_refs_pb2.UserRef(email=request.details.new_owner.email)
                                )
                            ]
                        )
                    ],
                    manager=identity_v1_refs_pb2.UserRef(email=request.details.notify_contact.email)
                )
            )
            envelope_0 = AnyMessage()
            envelope_0.Pack(outgoing_0)
            outgoing_0 = lineage_v1_lineage_node_workflow_service_pb2.AdvanceLineageNodeWorkflowRequest()
            if not envelope_0.Unpack(outgoing_0):
                raise ValueError("partner envelope contains the wrong request type")
            response_0 = await deps.clients.lineage_lineage_node_workflow.AdvanceLineageNodeWorkflow(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = documents_v1_document_query_service_pb2.SummarizeDocumentsRequest(
                annotations=dict(request.annotations),
                context=request.context
            )
            registered_1 = cast(
                documents_v1_document_query_service_pb2_grpc.DocumentQueryServiceStub,
                deps.clients.registry['acme.documents.v1.DocumentQueryService']
            )
            response_1 = await registered_1.SummarizeDocuments(outgoing_1, timeout=deps.settings.timeout)
            returned_0_0 = response_0.lineage_node.manager.display_name
            if returned_0_0:
                response.cohort.owner.display_name = returned_0_0
            returned_0_1 = response_0.outcome.status
            if returned_0_1:
                response.result.status = returned_0_1
            returned_1_0 = response_1.result.status
            if returned_1_0:
                response.result.status = returned_1_0
            echoed_0 = request.cohort_id
            response.cohort.cohort_id = echoed_0
            echoed_1 = request.details.effective_at
            response.outcome.effective_at.CopyFrom(echoed_1)
            return response

    async def handle_get_cohort_lifecycle(
        self,
        request: analytics_v1_cohort_lifecycle_service_pb2.GetCohortLifecycleRequest
    ) -> analytics_v1_cohort_lifecycle_service_pb2.GetCohortLifecycleResponse:
        """Returns a cohort."""
        deps = self.deps
        response = analytics_v1_cohort_lifecycle_service_pb2.GetCohortLifecycleResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('GetCohortLifecycle', extra={'fields': {'domain': 'analytics'}})
            await deps.repository.audit(request.context.tenant_id, 'GetCohortLifecycle', {})
            response_0 = documents_v1_document_query_service_pb2.FindDocumentsResponse()
            outgoing_0 = documents_v1_document_query_service_pb2.FindDocumentsRequest(
                context=request.context,
                filter=documents_v1_document_query_service_pb2.FindDocumentsRequest.Filter(
                    created_after=request.context.deadline,
                    labels=dict(request.context.baggage)
                )
            )
            response_0 = await deps.clients.documents_document_query.FindDocuments(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.status
            if returned_0_0:
                response.result.status = returned_0_0
            returned_0_1 = response_0.result.details
            response.result.details.update(returned_0_1)
            echoed_0 = request.cohort_id
            response.cohort.cohort_id = echoed_0
            return response

    async def handle_renew_cohort(
        self,
        request: analytics_v1_cohort_lifecycle_service_pb2.RenewCohortRequest
    ) -> analytics_v1_cohort_lifecycle_service_pb2.RenewCohortResponse:
        """Renews a cohort."""
        deps = self.deps
        response = analytics_v1_cohort_lifecycle_service_pb2.RenewCohortResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('RenewCohort', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'RenewCohort', {'reason': request.reason})
            response_0 = analytics_v1_cohort_calculation_service_pb2.SimulateCohortResponse()
            response_1 = customers_v1_customer_calculation_service_pb2.ExplainCustomerCalculationResponse()
            response_2 = checkout_v1_checkout_session_query_service_pb2.ResolveCheckoutSessionsResponse()
            command_0 = CohortLifecycleRenewCohort0Command.model_validate(
                {'context': request.context, 'cohort_owner_email': request.details.new_owner.email}
            )
            outgoing_0 = to_cohort_lifecycle_renew_cohort0_command(command_0)
            response_0 = await deps.clients.analytics_cohort_calculation.SimulateCohort(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = customers_v1_customer_calculation_service_pb2.ExplainCustomerCalculationRequest(
                context=request.context,
                customer=customers_v1_customers_pb2.Customer(
                    contact=common_v1_contact_pb2.ContactInfo(email=request.details.new_owner.email)
                ),
                details=customers_v1_customer_calculation_service_pb2.ExplainCustomerCalculationRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(
                        name=request.details.notify_contact.name,
                        phone=request.details.notify_contact.phone,
                        preferred_channel=request.details.notify_contact.preferred_channel
                    )
                )
            )
            send_1 = partial(
                deps.clients.customers_customer_calculation.ExplainCustomerCalculation,
                timeout=deps.settings.timeout
            )
            response_1 = await send_1(outgoing_1)
            outgoing_2 = checkout_v1_checkout_session_query_service_pb2.ResolveCheckoutSessionsRequest(
                context=request.context
            )
            response_2 = await hooks.cohort_lifecycle_renew_cohort2(
                deps.clients.checkout_checkout_session_query,
                outgoing_2,
                deps.settings.timeout
            )
            returned_0_0 = response_0.cohort.owner
            if returned_0_0.ListFields():
                response.cohort.owner.MergeFrom(returned_0_0)
            returned_0_1 = response_0.result.message
            if returned_0_1:
                response.outcome.message = returned_0_1
            returned_1_0 = response_1.outcome.next_steps
            response.outcome.next_steps.extend(returned_1_0)
            returned_1_1 = response_1.customer.audit.created_at
            if returned_1_1.ListFields():
                response.cohort.audit.created_at.MergeFrom(returned_1_1)
            returned_2_0 = response_2.result.correlation_id
            if returned_2_0:
                response.result.correlation_id = returned_2_0
            echoed_0 = request.cohort_id
            response.cohort.cohort_id = echoed_0
            echoed_1 = request.details.effective_at
            response.outcome.effective_at.CopyFrom(echoed_1)
            return response

    async def handle_suspend_cohort(
        self,
        request: analytics_v1_cohort_lifecycle_service_pb2.SuspendCohortRequest
    ) -> analytics_v1_cohort_lifecycle_service_pb2.SuspendCohortResponse:
        """Suspends a cohort."""
        deps = self.deps
        response = analytics_v1_cohort_lifecycle_service_pb2.SuspendCohortResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SuspendCohort', extra={'fields': {'reason_code': request.details.reason_code}})
            await deps.repository.audit(
                request.context.tenant_id,
                'SuspendCohort',
                {'reason_code': request.details.reason_code}
            )
            response_0 = analytics_v1_funnel_calculation_service_pb2.CalculateFunnelResponse()
            response_1 = analytics_v1_funnel_query_service_pb2.BrowseFunnelsResponse()
            response_2 = lineage_v1_lineage_node_workflow_service_pb2.ResumeLineageNodeWorkflowResponse()
            response_3 = analytics_v1_funnel_calculation_service_pb2.EstimateFunnelResponse()
            outgoing_0 = analytics_v1_funnel_calculation_service_pb2.CalculateFunnelRequest()
            outgoing_0.context.CopyFrom(request.context)
            outgoing_0.funnel.block.reason = request.reason
            outgoing_0.funnel.owner.email = request.details.new_owner.email
            outgoing_0.context.tenant_id = tenant_id.get()
            response_0 = await deps.clients.analytics_funnel_calculation.CalculateFunnel(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = analytics_v1_funnel_query_service_pb2.BrowseFunnelsRequest(
                context=request.context,
                filter=analytics_v1_funnel_query_service_pb2.BrowseFunnelsRequest.Filter(
                    created_after=response_0.funnel.audit.updated_at,
                    labels=dict(response_0.result.details),
                    owner_id=response_0.result.correlation_id
                )
            )
            port_1: CohortLifecycleSuspendCohort1Port = CohortLifecycleSuspendCohort1Adapter(
                deps.clients.analytics_funnel_query,
                deps.settings.timeout
            )
            response_1 = await port_1.execute(outgoing_1)
            outgoing_2 = lineage_v1_lineage_node_workflow_service_pb2.ResumeLineageNodeWorkflowRequest(
                context=request.context,
                lineage_node=lineage_v1_lineage_pb2.LineageNode(
                    children=[
                        lineage_v1_lineage_pb2.LineageNode(
                            children=[
                                lineage_v1_lineage_pb2.LineageNode(
                                    audit=common_v1_audit_pb2.AuditInfo(
                                        created_at=response_0.funnel.audit.created_at,
                                        created_by=response_0.funnel.audit.created_by
                                    ),
                                    manager=identity_v1_refs_pb2.UserRef(
                                        display_name=request.details.new_owner.display_name,
                                        email=request.details.notify_contact.email
                                    )
                                )
                            ]
                        )
                    ]
                )
            )
            steps_2 = [
                partial(
                    deps.clients.lineage_lineage_node_workflow.ResumeLineageNodeWorkflow,
                    outgoing_2,
                    timeout=deps.settings.timeout
                )
            ]
            results_2 = await run_steps(steps_2)
            response_2 = results_2[-1]
            outgoing_3 = analytics_v1_funnel_calculation_service_pb2.EstimateFunnelRequest(
                context=request.context,
                funnel=analytics_v1_analytics_pb2.Funnel(
                    owner=identity_v1_refs_pb2.UserRef(display_name=request.details.new_owner.display_name)
                )
            )
            response_3 = await CohortLifecycleSuspendCohort3Adapter(
                deps.clients.analytics_funnel_calculation,
                deps.settings.timeout
            )(outgoing_3)
            returned_0_0 = response_0.result.status
            if returned_0_0:
                response.result.status = returned_0_0
            returned_1_0 = response_1.result.message
            if returned_1_0:
                response.outcome.message = returned_1_0
            returned_2_0 = response_2.lineage_node.audit.etag
            if returned_2_0:
                response.cohort.audit.etag = returned_2_0
            returned_3_0 = response_3.funnel.audit.etag
            if returned_3_0:
                response.cohort.audit.etag = returned_3_0
            returned_3_1 = response_3.funnel.audit.created_by
            if returned_3_1:
                response.cohort.audit.created_by = returned_3_1
            echoed_0 = request.cohort_id
            response.cohort.cohort_id = echoed_0
            echoed_1 = request.details.effective_at
            response.outcome.effective_at.CopyFrom(echoed_1)
            return response

    async def handle_terminate_cohort(
        self,
        request: analytics_v1_cohort_lifecycle_service_pb2.TerminateCohortRequest
    ) -> analytics_v1_cohort_lifecycle_service_pb2.TerminateCohortResponse:
        """Terminates a cohort."""
        deps = self.deps
        response = analytics_v1_cohort_lifecycle_service_pb2.TerminateCohortResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('TerminateCohort', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'TerminateCohort', {'reason': request.reason})
            response_0 = analytics_v1_analytics_event_query_service_pb2.ResolveAnalyticsEventsResponse()
            outgoing_0 = analytics_v1_analytics_event_query_service_pb2.ResolveAnalyticsEventsRequest(
                context=request.context
            )
            response_0 = cast(analytics_v1_analytics_event_query_service_pb2.ResolveAnalyticsEventsResponse, await deps.bus.request(
                'acme.analytics.v1.CohortLifecycleService/TerminateCohort/0', outgoing_0, deps.settings.timeout,
            ))
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.outcome.message = returned_0_0
            returned_0_1 = response_0.result.status
            if returned_0_1:
                response.outcome.status = returned_0_1
            echoed_0 = request.cohort_id
            response.cohort.cohort_id = echoed_0
            echoed_1 = request.details.effective_at
            response.outcome.effective_at.CopyFrom(echoed_1)
            return response
