"""Reusable transport mixin for CohortWorkflowService."""

from __future__ import annotations

from collections.abc import AsyncIterator
from collections.abc import Awaitable
from collections.abc import Callable
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

from acme.analytics.v1 import analytics_pb2 as analytics_v1_analytics_pb2
from acme.analytics.v1 import (
    analytics_report_approval_service_pb2 as analytics_v1_analytics_report_approval_service_pb2,
)
from acme.analytics.v1 import (
    analytics_report_calculation_service_pb2 as analytics_v1_analytics_report_calculation_service_pb2,
)
from acme.analytics.v1 import (
    analytics_report_lifecycle_service_pb2 as analytics_v1_analytics_report_lifecycle_service_pb2,
)
from acme.analytics.v1 import cohort_validation_service_pb2 as analytics_v1_cohort_validation_service_pb2
from acme.analytics.v1 import cohort_workflow_service_pb2 as analytics_v1_cohort_workflow_service_pb2
from acme.analytics.v1 import funnel_approval_service_pb2 as analytics_v1_funnel_approval_service_pb2
from acme.analytics.v1 import funnel_calculation_service_pb2 as analytics_v1_funnel_calculation_service_pb2
from acme.authorization.v1 import access_policy_query_service_pb2 as authorization_v1_access_policy_query_service_pb2
from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.customers.v1 import (
    consent_record_validation_service_pb2 as customers_v1_consent_record_validation_service_pb2,
)
from acme.customers.v1 import (
    consent_record_validation_service_pb2_grpc as customers_v1_consent_record_validation_service_pb2_grpc,
)
from acme.customers.v1 import customer_service_pb2 as customers_v1_customer_service_pb2
from acme.customers.v1 import customers_pb2 as customers_v1_customers_pb2
from acme.customers.v1 import household_calculation_service_pb2 as customers_v1_household_calculation_service_pb2
from acme.forecasting.v1 import (
    forecast_model_approval_service_pb2 as forecasting_v1_forecast_model_approval_service_pb2,
)
from acme.forecasting.v1 import forecasting_pb2 as forecasting_v1_forecasting_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.metrics.v1 import metric_series_export_service_pb2 as metrics_v1_metric_series_export_service_pb2
from acme.pipelines.v1 import pipeline_run_workflow_service_pb2 as pipelines_v1_pipeline_run_workflow_service_pb2
from acme.pipelines.v1 import pipeline_step_approval_service_pb2 as pipelines_v1_pipeline_step_approval_service_pb2
from acme.pipelines.v1 import pipelines_pb2 as pipelines_v1_pipelines_pb2
from acme.yards.v1 import yard_calculation_service_pb2 as yards_v1_yard_calculation_service_pb2
from acme.yards.v1 import yards_pb2 as yards_v1_yards_pb2

from acme_data.domains.analytics import hooks
from acme_data.domains.analytics.adapters import CohortWorkflowAdvanceCohortWorkflow0Adapter
from acme_data.domains.analytics.adapters import CohortWorkflowAdvanceCohortWorkflow0Port
from acme_data.domains.analytics.adapters import CohortWorkflowAdvanceCohortWorkflow2Adapter
from acme_data.domains.analytics.dependencies import Dependencies
from acme_data.domains.analytics.models import CohortWorkflowRetryCohortWorkflow0Command
from acme_data.domains.analytics.models import to_cohort_workflow_retry_cohort_workflow0_command
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_id
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class CohortWorkflowServicerHandlers:
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    async def AdvanceCohortWorkflow(
        self, request: analytics_v1_cohort_workflow_service_pb2.AdvanceCohortWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_cohort_workflow_service_pb2.AdvanceCohortWorkflowResponse:
        """Advances a cohort."""
        return await self.handle_advance_cohort_workflow(request)

    @rpc_errors
    async def CancelCohortWorkflow(
        self, request: analytics_v1_cohort_workflow_service_pb2.CancelCohortWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_cohort_workflow_service_pb2.CancelCohortWorkflowResponse:
        """Cancels a cohort."""
        return await self.handle_cancel_cohort_workflow(request)

    @rpc_errors
    @retry_transient
    async def InspectCohortWorkflow(
        self, request: analytics_v1_cohort_workflow_service_pb2.InspectCohortWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_cohort_workflow_service_pb2.InspectCohortWorkflowResponse:
        """Returns a cohort."""
        return await self.handle_inspect_cohort_workflow(request)

    @rpc_errors
    @retry_transient
    async def ListCohortWorkflows(
        self, request: analytics_v1_cohort_workflow_service_pb2.ListCohortWorkflowsRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_cohort_workflow_service_pb2.ListCohortWorkflowsResponse:
        """Lists cohorts a page at a time."""
        return await self.handle_list_cohort_workflows(request)

    @rpc_errors
    async def PauseCohortWorkflow(
        self, request: analytics_v1_cohort_workflow_service_pb2.PauseCohortWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_cohort_workflow_service_pb2.PauseCohortWorkflowResponse:
        """Pauses a cohort."""
        return await self.handle_pause_cohort_workflow(request)

    @rpc_errors
    async def ResumeCohortWorkflow(
        self, request: analytics_v1_cohort_workflow_service_pb2.ResumeCohortWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_cohort_workflow_service_pb2.ResumeCohortWorkflowResponse:
        """Resumes a cohort."""
        return await self.handle_resume_cohort_workflow(request)

    @rpc_errors
    async def RetryCohortWorkflow(
        self, request: analytics_v1_cohort_workflow_service_pb2.RetryCohortWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_cohort_workflow_service_pb2.RetryCohortWorkflowResponse:
        """Retrys a cohort."""
        return await self.handle_retry_cohort_workflow(request)

    @rpc_errors
    async def SignalCohortWorkflow(
        self, request: analytics_v1_cohort_workflow_service_pb2.SignalCohortWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_cohort_workflow_service_pb2.SignalCohortWorkflowResponse:
        """Signals a cohort."""
        return await self.handle_signal_cohort_workflow(request)

    @rpc_errors
    async def StartCohortWorkflow(
        self, request: analytics_v1_cohort_workflow_service_pb2.StartCohortWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_cohort_workflow_service_pb2.StartCohortWorkflowResponse:
        """Starts a cohort."""
        return await self.handle_start_cohort_workflow(request)

    async def handle_advance_cohort_workflow(
        self,
        request: analytics_v1_cohort_workflow_service_pb2.AdvanceCohortWorkflowRequest
    ) -> analytics_v1_cohort_workflow_service_pb2.AdvanceCohortWorkflowResponse:
        """Advances a cohort."""
        deps = self.deps
        response = analytics_v1_cohort_workflow_service_pb2.AdvanceCohortWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('AdvanceCohortWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'AdvanceCohortWorkflow', {'reason': request.reason})
            await deps.repository.save_cohort(request.context.tenant_id, request.cohort)
            response_0 = analytics_v1_analytics_report_approval_service_pb2.EscalateAnalyticsReportResponse()
            response_1 = metrics_v1_metric_series_export_service_pb2.StreamMetricSeriesExportResponse()
            response_2 = analytics_v1_analytics_report_approval_service_pb2.ApproveAnalyticsReportResponse()
            outgoing_0 = analytics_v1_analytics_report_approval_service_pb2.EscalateAnalyticsReportRequest(
                context=request.context,
                details=analytics_v1_analytics_report_approval_service_pb2.EscalateAnalyticsReportRequest.Details(
                    approver=identity_v1_refs_pb2.UserRef(display_name=request.cohort.owner.display_name)
                )
            )
            port_0: CohortWorkflowAdvanceCohortWorkflow0Port = CohortWorkflowAdvanceCohortWorkflow0Adapter(
                deps.clients.analytics_analytics_report_approval,
                deps.settings.timeout
            )
            response_0 = await port_0.execute(outgoing_0)
            outgoing_1 = metrics_v1_metric_series_export_service_pb2.StreamMetricSeriesExportRequest(
                context=request.context,
                filter=metrics_v1_metric_series_export_service_pb2.StreamMetricSeriesExportRequest.Filter(
                    region=response_0.analytics_report.billing_address.region
                )
            )
            async for chunk_1 in deps.clients.metrics_metric_series_export.StreamMetricSeriesExport(
                outgoing_1,
                timeout=deps.settings.timeout
            ):
                response_1 = chunk_1
            outgoing_2 = analytics_v1_analytics_report_approval_service_pb2.ApproveAnalyticsReportRequest(
                analytics_report=analytics_v1_analytics_pb2.AnalyticsReport(
                    lines=[
                        analytics_v1_analytics_pb2.AnalyticsReportLine(
                            tax=analytics_v1_analytics_pb2.AnalyticsReportLineTax(amount=request.cohort.discount.amount)
                        )
                    ]
                ),
                context=request.context
            )
            response_2 = await CohortWorkflowAdvanceCohortWorkflow2Adapter(
                deps.clients.analytics_analytics_report_approval,
                deps.settings.timeout
            )(outgoing_2)
            returned_0_0 = response_0.outcome.status
            if returned_0_0:
                response.outcome.status = returned_0_0
            returned_0_1 = response_0.outcome.effective_at
            if returned_0_1.ListFields():
                response.outcome.effective_at.MergeFrom(returned_0_1)
            returned_2_0 = response_2.outcome.status
            if returned_2_0:
                response.outcome.status = returned_2_0
            echoed_0 = request.cohort_id
            response.cohort.cohort_id = echoed_0
            echoed_1 = request.cohort.status
            response.cohort.status = echoed_1
            return response

    async def handle_cancel_cohort_workflow(
        self,
        request: analytics_v1_cohort_workflow_service_pb2.CancelCohortWorkflowRequest
    ) -> analytics_v1_cohort_workflow_service_pb2.CancelCohortWorkflowResponse:
        """Cancels a cohort."""
        deps = self.deps
        response = analytics_v1_cohort_workflow_service_pb2.CancelCohortWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CancelCohortWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'CancelCohortWorkflow', {'reason': request.reason})
            await deps.repository.save_cohort(request.context.tenant_id, request.cohort)
            response_0 = pipelines_v1_pipeline_step_approval_service_pb2.DelegatePipelineStepApprovalResponse()
            response_1 = analytics_v1_analytics_report_lifecycle_service_pb2.ScheduleAnalyticsReportExpiryResponse()
            for item_0 in request.cohort.conditions:
                outgoing_0 = pipelines_v1_pipeline_step_approval_service_pb2.DelegatePipelineStepApprovalRequest(
                    context=request.context,
                    pipeline_step=pipelines_v1_pipelines_pb2.PipelineStep(
                        conditions=[
                            pipelines_v1_pipelines_pb2.PipelineStepCondition(
                                negate=item_0.negate,
                                operator=item_0.operator,
                                value=item_0.value
                            )
                        ]
                    )
                )
                response_0 = await deps.clients.pipelines_pipeline_step_approval.DelegatePipelineStepApproval(
                    outgoing_0,
                    timeout=deps.settings.timeout
                )
            outgoing_1 = analytics_v1_analytics_report_lifecycle_service_pb2.ScheduleAnalyticsReportExpiryRequest(
                analytics_report=analytics_v1_analytics_pb2.AnalyticsReport(
                    lines=[
                        analytics_v1_analytics_pb2.AnalyticsReportLine(
                            tax=analytics_v1_analytics_pb2.AnalyticsReportLineTax(amount=request.cohort.discount.amount)
                        )
                    ]
                ),
                context=request.context
            )
            response_1 = await deps.clients.analytics_analytics_report_lifecycle.ScheduleAnalyticsReportExpiry(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_1_0 = response_1.result.message
            if returned_1_0:
                response.result.message = returned_1_0
            returned_1_1 = response_1.analytics_report.audit.etag
            if returned_1_1:
                response.cohort.audit.etag = returned_1_1
            echoed_0 = request.cohort_id
            response.cohort.cohort_id = echoed_0
            echoed_1 = request.cohort.priority
            response.cohort.priority = echoed_1
            return response

    async def handle_inspect_cohort_workflow(
        self,
        request: analytics_v1_cohort_workflow_service_pb2.InspectCohortWorkflowRequest
    ) -> analytics_v1_cohort_workflow_service_pb2.InspectCohortWorkflowResponse:
        """Returns a cohort."""
        deps = self.deps
        response = analytics_v1_cohort_workflow_service_pb2.InspectCohortWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('InspectCohortWorkflow', extra={'fields': {'locale': request.context.locale}})
            await deps.repository.audit(
                request.context.tenant_id,
                'InspectCohortWorkflow',
                {'locale': request.context.locale}
            )
            echoed_0 = request.cohort_id
            response.cohort.cohort_id = echoed_0
            return response

    async def handle_list_cohort_workflows(
        self,
        request: analytics_v1_cohort_workflow_service_pb2.ListCohortWorkflowsRequest
    ) -> analytics_v1_cohort_workflow_service_pb2.ListCohortWorkflowsResponse:
        """Lists cohorts a page at a time."""
        deps = self.deps
        response = analytics_v1_cohort_workflow_service_pb2.ListCohortWorkflowsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ListCohortWorkflows', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ListCohortWorkflows',
                {'order_by': request.order_by}
            )
            response_0 = yards_v1_yard_calculation_service_pb2.QuoteYardResponse()
            outgoing_0 = yards_v1_yard_calculation_service_pb2.QuoteYardRequest(
                context=request.context,
                details=yards_v1_yard_calculation_service_pb2.QuoteYardRequest.Details(
                    destination=common_v1_address_pb2.PostalAddress(region=request.filter.region)
                ),
                yard=yards_v1_yards_pb2.Yard(
                    owner=identity_v1_refs_pb2.UserRef(
                        email=request.context.actor.email,
                        user_id=request.context.actor.user_id
                    )
                )
            )
            response_0 = await deps.clients.yards_yard_calculation.QuoteYard(outgoing_0, timeout=deps.settings.timeout)
            returned_0_0 = response_0.yard.audit.updated_by
            returned_0_0_part_0 = response.cohorts.add()
            if returned_0_0:
                returned_0_0_part_0.audit.updated_by = returned_0_0
            return response

    async def handle_pause_cohort_workflow(
        self,
        request: analytics_v1_cohort_workflow_service_pb2.PauseCohortWorkflowRequest
    ) -> analytics_v1_cohort_workflow_service_pb2.PauseCohortWorkflowResponse:
        """Pauses a cohort."""
        deps = self.deps
        response = analytics_v1_cohort_workflow_service_pb2.PauseCohortWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('PauseCohortWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'PauseCohortWorkflow', {'reason': request.reason})
            await deps.repository.save_cohort(request.context.tenant_id, request.cohort)
            response_0 = customers_v1_household_calculation_service_pb2.QuoteHouseholdResponse()
            response_1 = pipelines_v1_pipeline_run_workflow_service_pb2.RetryPipelineRunWorkflowResponse()
            response_2 = analytics_v1_analytics_report_calculation_service_pb2.CalculateAnalyticsReportResponse()
            fields_0: dict[str, Any] = {
                'context': request.context,
                'household': {
                    'children': [{'children': [{'manager': {'display_name': request.cohort.owner.display_name}}]}]
                }
            }
            outgoing_0 = customers_v1_household_calculation_service_pb2.QuoteHouseholdRequest(**fields_0)
            response_0 = await deps.clients.customers_household_calculation.QuoteHousehold(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = pipelines_v1_pipeline_run_workflow_service_pb2.RetryPipelineRunWorkflowRequest(
                context=request.context,
                pipeline_run=pipelines_v1_pipelines_pb2.PipelineRun(
                    assignee=identity_v1_refs_pb2.UserRef(display_name=response_0.household.manager.display_name)
                )
            )
            document_1 = MessageToDict(outgoing_1, preserving_proto_field_name=True)
            outgoing_1 = ParseDict(
                document_1,
                pipelines_v1_pipeline_run_workflow_service_pb2.RetryPipelineRunWorkflowRequest()
            )
            response_1 = await deps.clients.pipelines_pipeline_run_workflow.RetryPipelineRunWorkflow(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = analytics_v1_analytics_report_calculation_service_pb2.CalculateAnalyticsReportRequest(
                analytics_report=analytics_v1_analytics_pb2.AnalyticsReport(
                    lines=[
                        analytics_v1_analytics_pb2.AnalyticsReportLine(
                            tax=analytics_v1_analytics_pb2.AnalyticsReportLineTax(amount=request.cohort.discount.amount)
                        )
                    ]
                ),
                context=request.context
            )
            document_2 = MessageToJson(outgoing_2, preserving_proto_field_name=True)
            outgoing_2 = Parse(
                document_2,
                analytics_v1_analytics_report_calculation_service_pb2.CalculateAnalyticsReportRequest()
            )
            response_2 = await deps.clients.analytics_analytics_report_calculation.CalculateAnalyticsReport(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.status
            if returned_0_0:
                response.result.status = returned_0_0
            returned_1_0 = response_1.outcome.status
            if returned_1_0:
                response.result.status = returned_1_0
            returned_2_0 = response_2.analytics_report.counterparty.email
            if returned_2_0:
                response.cohort.owner.email = returned_2_0
            returned_2_1 = response_2.analytics_report.audit.created_at
            if returned_2_1.ListFields():
                response.cohort.audit.created_at.MergeFrom(returned_2_1)
            echoed_0 = request.cohort_id
            response.cohort.cohort_id = echoed_0
            echoed_1 = request.cohort.version
            response.cohort.version = echoed_1
            return response

    async def handle_resume_cohort_workflow(
        self,
        request: analytics_v1_cohort_workflow_service_pb2.ResumeCohortWorkflowRequest
    ) -> analytics_v1_cohort_workflow_service_pb2.ResumeCohortWorkflowResponse:
        """Resumes a cohort."""
        deps = self.deps
        response = analytics_v1_cohort_workflow_service_pb2.ResumeCohortWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ResumeCohortWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'ResumeCohortWorkflow', {'reason': request.reason})
            await deps.repository.save_cohort(request.context.tenant_id, request.cohort)
            response_0 = forecasting_v1_forecast_model_approval_service_pb2.RejectForecastModelResponse()
            response_1 = authorization_v1_access_policy_query_service_pb2.ResolveAccessPoliciesResponse()
            response_2 = customers_v1_consent_record_validation_service_pb2.NormalizeConsentRecordResponse()
            response_3 = analytics_v1_cohort_validation_service_pb2.PreviewCohortResponse()
            outgoing_0 = forecasting_v1_forecast_model_approval_service_pb2.RejectForecastModelRequest(
                context=request.context,
                forecast_model=forecasting_v1_forecasting_pb2.ForecastModel(
                    audit=common_v1_audit_pb2.AuditInfo(created_at=request.cohort.audit.created_at),
                    owner=identity_v1_refs_pb2.UserRef(email=request.details.notify.email)
                )
            )
            outgoing_1 = authorization_v1_access_policy_query_service_pb2.ResolveAccessPoliciesRequest(
                context=request.context
            )
            outgoing_3 = analytics_v1_cohort_validation_service_pb2.PreviewCohortRequest(
                cohort=analytics_v1_analytics_pb2.Cohort(
                    audit=common_v1_audit_pb2.AuditInfo(created_by=request.cohort.audit.created_by),
                    block=analytics_v1_analytics_pb2.CohortBlockAction(notify_email=request.cohort.block.notify_email)
                ),
                context=request.context
            )
            response_0, response_1, response_3 = await asyncio.gather(
                deps.clients.forecasting_forecast_model_approval.RejectForecastModel(
                    outgoing_0,
                    timeout=deps.settings.timeout
                ),
                deps.clients.authorization_access_policy_query.ResolveAccessPolicies(
                    outgoing_1,
                    timeout=deps.settings.timeout
                ),
                deps.clients.analytics_cohort_validation.PreviewCohort(outgoing_3, timeout=deps.settings.timeout),
            )
            outgoing_2 = customers_v1_consent_record_validation_service_pb2.NormalizeConsentRecordRequest(
                consent_record=customers_v1_customers_pb2.ConsentRecord(
                    measurements=[
                        customers_v1_customers_pb2.ConsentRecordMeasurement(
                            unit=response_0.forecast_model.dimensions.unit
                        )
                    ]
                ),
                context=request.context,
                details=customers_v1_consent_record_validation_service_pb2.NormalizeConsentRecordRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(
                        name=request.details.notify.name,
                        phone=request.details.notify.phone,
                        preferred_channel=request.details.notify.preferred_channel
                    )
                )
            )
            registered_2 = cast(
                customers_v1_consent_record_validation_service_pb2_grpc.ConsentRecordValidationServiceStub,
                deps.clients.registry['acme.customers.v1.ConsentRecordValidationService']
            )
            response_2 = await registered_2.NormalizeConsentRecord(outgoing_2, timeout=deps.settings.timeout)
            returned_0_0 = response_0.outcome.effective_at
            if returned_0_0.ListFields():
                response.outcome.effective_at.MergeFrom(returned_0_0)
            returned_0_1 = response_0.forecast_model.owner.display_name
            if returned_0_1:
                response.cohort.owner.display_name = returned_0_1
            returned_1_0 = response_1.result.reference_ids
            response.result.reference_ids.extend(returned_1_0)
            returned_1_1 = response_1.result.message
            if returned_1_1:
                response.result.message = returned_1_1
            returned_2_0 = response_2.result.message
            if returned_2_0:
                response.outcome.message = returned_2_0
            returned_2_1 = response_2.outcome.next_steps
            response.outcome.next_steps.extend(returned_2_1)
            returned_3_0 = response_3.outcome.status
            if returned_3_0:
                response.outcome.status = returned_3_0
            echoed_0 = request.cohort_id
            response.cohort.cohort_id = echoed_0
            echoed_1 = request.cohort.parameters
            response.cohort.parameters.update(echoed_1)
            return response

    async def handle_retry_cohort_workflow(
        self,
        request: analytics_v1_cohort_workflow_service_pb2.RetryCohortWorkflowRequest
    ) -> analytics_v1_cohort_workflow_service_pb2.RetryCohortWorkflowResponse:
        """Retrys a cohort."""
        deps = self.deps
        response = analytics_v1_cohort_workflow_service_pb2.RetryCohortWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('RetryCohortWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'RetryCohortWorkflow', {'reason': request.reason})
            await deps.repository.save_cohort(request.context.tenant_id, request.cohort)
            response_0 = authorization_v1_access_policy_query_service_pb2.BrowseAccessPoliciesResponse()
            response_1 = analytics_v1_funnel_approval_service_pb2.ListPendingFunnelsResponse()
            command_0 = CohortWorkflowRetryCohortWorkflow0Command.model_validate(
                {'context': request.context, 'filter_labels': dict(request.cohort.parameters)}
            )
            outgoing_0 = to_cohort_workflow_retry_cohort_workflow0_command(command_0)
            response_0 = await deps.clients.authorization_access_policy_query.BrowseAccessPolicies(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = analytics_v1_funnel_approval_service_pb2.ListPendingFunnelsRequest(
                context=request.context,
                filter=analytics_v1_funnel_approval_service_pb2.ListPendingFunnelsRequest.Filter(
                    created_after=request.cohort.audit.updated_at
                )
            )
            send_1 = partial(deps.clients.analytics_funnel_approval.ListPendingFunnels, timeout=deps.settings.timeout)
            response_1 = await send_1(outgoing_1)
            returned_0_0 = response_0.result.correlation_id
            if returned_0_0:
                response.result.correlation_id = returned_0_0
            returned_1_0 = response_1.result.status
            if returned_1_0:
                response.result.status = returned_1_0
            echoed_0 = request.cohort_id
            response.cohort.cohort_id = echoed_0
            echoed_1 = request.cohort.owner
            response.cohort.owner.CopyFrom(echoed_1)
            return response

    async def handle_signal_cohort_workflow(
        self,
        request: analytics_v1_cohort_workflow_service_pb2.SignalCohortWorkflowRequest
    ) -> analytics_v1_cohort_workflow_service_pb2.SignalCohortWorkflowResponse:
        """Signals a cohort."""
        deps = self.deps
        response = analytics_v1_cohort_workflow_service_pb2.SignalCohortWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SignalCohortWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'SignalCohortWorkflow', {'reason': request.reason})
            await deps.repository.save_cohort(request.context.tenant_id, request.cohort)
            response_0 = analytics_v1_funnel_calculation_service_pb2.QuoteFunnelResponse()
            outgoing_0 = analytics_v1_funnel_calculation_service_pb2.QuoteFunnelRequest(
                context=request.context,
                funnel=analytics_v1_analytics_pb2.Funnel(
                    owner=identity_v1_refs_pb2.UserRef(email=request.cohort.owner.email)
                )
            )
            response_0 = await hooks.cohort_workflow_signal_cohort_workflow0(
                deps.clients.analytics_funnel_calculation,
                outgoing_0,
                deps.settings.timeout
            )
            returned_0_0 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_0)
            echoed_0 = request.cohort_id
            response.cohort.cohort_id = echoed_0
            echoed_1 = request.cohort.priority
            response.cohort.priority = echoed_1
            return response

    async def handle_start_cohort_workflow(
        self,
        request: analytics_v1_cohort_workflow_service_pb2.StartCohortWorkflowRequest
    ) -> analytics_v1_cohort_workflow_service_pb2.StartCohortWorkflowResponse:
        """Starts a cohort."""
        deps = self.deps
        response = analytics_v1_cohort_workflow_service_pb2.StartCohortWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('StartCohortWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'StartCohortWorkflow', {'reason': request.reason})
            await deps.repository.save_cohort(request.context.tenant_id, request.cohort)
            response_0 = customers_v1_customer_service_pb2.UpdateCustomerResponse()
            outgoing_0 = customers_v1_customer_service_pb2.UpdateCustomerRequest()
            outgoing_0.context.CopyFrom(request.context)
            outgoing_0.customer.contact.phone = request.details.notify.phone
            outgoing_0.context.tenant_id = tenant_id.get()
            response_0 = await deps.clients.customers_customer.UpdateCustomer(outgoing_0, timeout=deps.settings.timeout)
            returned_0_0 = response_0.result.correlation_id
            if returned_0_0:
                response.result.correlation_id = returned_0_0
            echoed_0 = request.cohort_id
            response.cohort.cohort_id = echoed_0
            echoed_1 = request.cohort.owner
            response.cohort.owner.CopyFrom(echoed_1)
            return response
