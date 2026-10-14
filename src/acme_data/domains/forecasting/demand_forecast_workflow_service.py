"""Runs the long-lived workflow that takes a demand forecast from start to finish."""

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

from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.common.v1 import paging_pb2 as common_v1_paging_pb2
from acme.featurestore.v1 import (
    feature_view_reporting_service_pb2 as featurestore_v1_feature_view_reporting_service_pb2,
)
from acme.forecasting.v1 import (
    demand_forecast_approval_service_pb2 as forecasting_v1_demand_forecast_approval_service_pb2,
)
from acme.forecasting.v1 import demand_forecast_service_pb2 as forecasting_v1_demand_forecast_service_pb2
from acme.forecasting.v1 import (
    demand_forecast_validation_service_pb2 as forecasting_v1_demand_forecast_validation_service_pb2,
)
from acme.forecasting.v1 import (
    demand_forecast_workflow_service_pb2 as forecasting_v1_demand_forecast_workflow_service_pb2,
)
from acme.forecasting.v1 import (
    demand_forecast_workflow_service_pb2_grpc as forecasting_v1_demand_forecast_workflow_service_pb2_grpc,
)
from acme.forecasting.v1 import forecast_model_query_service_pb2 as forecasting_v1_forecast_model_query_service_pb2
from acme.forecasting.v1 import forecasting_pb2 as forecasting_v1_forecasting_pb2
from acme.forecasting.v1 import refs_pb2 as forecasting_v1_refs_pb2
from acme.forecasting.v1 import scenario_calculation_service_pb2 as forecasting_v1_scenario_calculation_service_pb2
from acme.forecasting.v1 import scenario_validation_service_pb2 as forecasting_v1_scenario_validation_service_pb2
from acme.forecasting.v1 import (
    scenario_validation_service_pb2_grpc as forecasting_v1_scenario_validation_service_pb2_grpc,
)
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.ledger.v1 import ledger_account_query_service_pb2 as ledger_v1_ledger_account_query_service_pb2
from acme.metrics.v1 import metric_alert_query_service_pb2 as metrics_v1_metric_alert_query_service_pb2
from acme.pipelines.v1 import pipeline_reporting_service_pb2 as pipelines_v1_pipeline_reporting_service_pb2
from acme.pipelines.v1 import pipeline_step_export_service_pb2 as pipelines_v1_pipeline_step_export_service_pb2
from acme.recommendations.v1 import (
    interaction_approval_service_pb2 as recommendations_v1_interaction_approval_service_pb2,
)
from acme.suppliers.v1 import supplier_service_pb2 as suppliers_v1_supplier_service_pb2
from acme.webhooks.v1 import webhook_endpoint_service_pb2 as webhooks_v1_webhook_endpoint_service_pb2

from acme_data.domains.forecasting.adapters import DemandForecastWorkflowSignalDemandForecastWorkflow0Adapter
from acme_data.domains.forecasting.adapters import DemandForecastWorkflowSignalDemandForecastWorkflow0Port
from acme_data.domains.forecasting.adapters import DemandForecastWorkflowStartDemandForecastWorkflow0Adapter
from acme_data.domains.forecasting.dependencies import Dependencies
from acme_data.domains.forecasting.models import DemandForecastWorkflowResumeDemandForecastWorkflow0Command
from acme_data.domains.forecasting.models import to_demand_forecast_workflow_resume_demand_forecast_workflow0_command
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


@dataclass(slots=True)
class DemandForecastWorkflowServicer(
    forecasting_v1_demand_forecast_workflow_service_pb2_grpc.DemandForecastWorkflowServiceServicer
):
    deps: Dependencies

    @rpc_errors
    async def AdvanceDemandForecastWorkflow(
        self, request: forecasting_v1_demand_forecast_workflow_service_pb2.AdvanceDemandForecastWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> forecasting_v1_demand_forecast_workflow_service_pb2.AdvanceDemandForecastWorkflowResponse:
        """Advances a demand forecast."""
        return await self.handle_advance_demand_forecast_workflow(request)

    @rpc_errors
    async def CancelDemandForecastWorkflow(
        self, request: forecasting_v1_demand_forecast_workflow_service_pb2.CancelDemandForecastWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> forecasting_v1_demand_forecast_workflow_service_pb2.CancelDemandForecastWorkflowResponse:
        """Cancels a demand forecast."""
        return await self.handle_cancel_demand_forecast_workflow(request)

    @rpc_errors
    @retry_transient
    async def InspectDemandForecastWorkflow(
        self, request: forecasting_v1_demand_forecast_workflow_service_pb2.InspectDemandForecastWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> forecasting_v1_demand_forecast_workflow_service_pb2.InspectDemandForecastWorkflowResponse:
        """Returns a demand forecast."""
        return await self.handle_inspect_demand_forecast_workflow(request)

    @rpc_errors
    @retry_transient
    async def ListDemandForecastWorkflows(
        self, request: forecasting_v1_demand_forecast_workflow_service_pb2.ListDemandForecastWorkflowsRequest, context: grpc.aio.ServicerContext,
    ) -> forecasting_v1_demand_forecast_workflow_service_pb2.ListDemandForecastWorkflowsResponse:
        """Lists demand forecasts a page at a time."""
        return await self.handle_list_demand_forecast_workflows(request)

    @rpc_errors
    async def PauseDemandForecastWorkflow(
        self, request: forecasting_v1_demand_forecast_workflow_service_pb2.PauseDemandForecastWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> forecasting_v1_demand_forecast_workflow_service_pb2.PauseDemandForecastWorkflowResponse:
        """Pauses a demand forecast."""
        return await self.handle_pause_demand_forecast_workflow(request)

    @rpc_errors
    async def ResumeDemandForecastWorkflow(
        self, request: forecasting_v1_demand_forecast_workflow_service_pb2.ResumeDemandForecastWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> forecasting_v1_demand_forecast_workflow_service_pb2.ResumeDemandForecastWorkflowResponse:
        """Resumes a demand forecast."""
        return await self.handle_resume_demand_forecast_workflow(request)

    @rpc_errors
    async def RetryDemandForecastWorkflow(
        self, request: forecasting_v1_demand_forecast_workflow_service_pb2.RetryDemandForecastWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> forecasting_v1_demand_forecast_workflow_service_pb2.RetryDemandForecastWorkflowResponse:
        """Retrys a demand forecast."""
        return await self.handle_retry_demand_forecast_workflow(request)

    @rpc_errors
    async def SignalDemandForecastWorkflow(
        self, request: forecasting_v1_demand_forecast_workflow_service_pb2.SignalDemandForecastWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> forecasting_v1_demand_forecast_workflow_service_pb2.SignalDemandForecastWorkflowResponse:
        """Signals a demand forecast."""
        return await self.handle_signal_demand_forecast_workflow(request)

    @rpc_errors
    async def StartDemandForecastWorkflow(
        self, request: forecasting_v1_demand_forecast_workflow_service_pb2.StartDemandForecastWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> forecasting_v1_demand_forecast_workflow_service_pb2.StartDemandForecastWorkflowResponse:
        """Starts a demand forecast."""
        return await self.handle_start_demand_forecast_workflow(request)

    async def handle_advance_demand_forecast_workflow(
        self,
        request: forecasting_v1_demand_forecast_workflow_service_pb2.AdvanceDemandForecastWorkflowRequest
    ) -> forecasting_v1_demand_forecast_workflow_service_pb2.AdvanceDemandForecastWorkflowResponse:
        """Advances a demand forecast."""
        deps = self.deps
        response = forecasting_v1_demand_forecast_workflow_service_pb2.AdvanceDemandForecastWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('AdvanceDemandForecastWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'AdvanceDemandForecastWorkflow',
                {'reason': request.reason}
            )
            await deps.repository.save_demand_forecast(request.context.tenant_id, request.demand_forecast)
            response_0 = forecasting_v1_demand_forecast_validation_service_pb2.ValidateDemandForecastResponse()
            response_1 = ledger_v1_ledger_account_query_service_pb2.SuggestLedgerAccountsResponse()
            outgoing_0 = forecasting_v1_demand_forecast_validation_service_pb2.ValidateDemandForecastRequest(
                context=request.context,
                demand_forecast=forecasting_v1_forecasting_pb2.DemandForecast(
                    audit=common_v1_audit_pb2.AuditInfo(etag=request.demand_forecast.audit.etag),
                    card=forecasting_v1_forecasting_pb2.DemandForecastCardSettlement(
                        network=request.demand_forecast.card.network
                    ),
                    counterparty=forecasting_v1_refs_pb2.ScenarioRef(
                        display_name=request.demand_forecast.counterparty.display_name
                    )
                )
            )
            outgoing_1 = ledger_v1_ledger_account_query_service_pb2.SuggestLedgerAccountsRequest(
                context=request.context,
                filter=ledger_v1_ledger_account_query_service_pb2.SuggestLedgerAccountsRequest.Filter(
                    region=request.demand_forecast.billing_address.region
                )
            )
            response_0, response_1 = await asyncio.gather(
                deps.clients.forecasting_demand_forecast_validation.ValidateDemandForecast(
                    outgoing_0,
                    timeout=deps.settings.timeout
                ),
                deps.clients.ledger_ledger_account_query.SuggestLedgerAccounts(
                    outgoing_1,
                    timeout=deps.settings.timeout
                ),
            )
            returned_0_0 = response_0.demand_forecast.billing_address.country_code
            if returned_0_0:
                response.demand_forecast.billing_address.country_code = returned_0_0
            returned_0_1 = response_0.result.message
            if returned_0_1:
                response.result.message = returned_0_1
            returned_1_0 = response_1.result.reference_ids
            response.result.reference_ids.extend(returned_1_0)
            returned_1_1 = response_1.result.message
            if returned_1_1:
                response.result.message = returned_1_1
            echoed_0 = request.demand_forecast_id
            response.demand_forecast.demand_forecast_id = echoed_0
            echoed_1 = request.demand_forecast.number
            response.demand_forecast.number = echoed_1
            return response

    async def handle_cancel_demand_forecast_workflow(
        self,
        request: forecasting_v1_demand_forecast_workflow_service_pb2.CancelDemandForecastWorkflowRequest
    ) -> forecasting_v1_demand_forecast_workflow_service_pb2.CancelDemandForecastWorkflowResponse:
        """Cancels a demand forecast."""
        deps = self.deps
        response = forecasting_v1_demand_forecast_workflow_service_pb2.CancelDemandForecastWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info(
                'CancelDemandForecastWorkflow',
                extra={'fields': {'demand_forecast_id': request.demand_forecast.demand_forecast_id}}
            )
            await deps.repository.audit(
                request.context.tenant_id,
                'CancelDemandForecastWorkflow',
                {'demand_forecast_id': request.demand_forecast.demand_forecast_id}
            )
            await deps.repository.save_demand_forecast(request.context.tenant_id, request.demand_forecast)
            response_0 = forecasting_v1_demand_forecast_validation_service_pb2.ValidateDemandForecastResponse()
            response_1 = forecasting_v1_forecast_model_query_service_pb2.BrowseForecastModelsResponse()
            response_2 = featurestore_v1_feature_view_reporting_service_pb2.ScheduleFeatureViewReportResponse()
            response_3 = pipelines_v1_pipeline_reporting_service_pb2.SchedulePipelineReportResponse()
            outgoing_0 = forecasting_v1_demand_forecast_validation_service_pb2.ValidateDemandForecastRequest(
                context=request.context,
                demand_forecast=forecasting_v1_forecasting_pb2.DemandForecast(
                    billing_address=common_v1_address_pb2.PostalAddress(
                        postal_code=request.demand_forecast.billing_address.postal_code
                    ),
                    card=forecasting_v1_forecasting_pb2.DemandForecastCardSettlement(
                        network=request.demand_forecast.card.network
                    ),
                    counterparty=forecasting_v1_refs_pb2.ScenarioRef(
                        display_name=request.demand_forecast.counterparty.display_name,
                        scenario_id=request.demand_forecast.counterparty.scenario_id
                    )
                )
            )
            method_name_0 = 'ValidateDemandForecast'
            response_0 = await getattr(
                deps.clients.forecasting_demand_forecast_validation,
                method_name_0
            )(outgoing_0, timeout=deps.settings.timeout)
            fields_1: dict[str, Any] = {
                'context': request.context,
                'filter': {
                    'created_after': request.demand_forecast.audit.created_at,
                    'region': request.demand_forecast.billing_address.region
                }
            }
            outgoing_1 = forecasting_v1_forecast_model_query_service_pb2.BrowseForecastModelsRequest(**fields_1)
            response_1 = await deps.clients.forecasting_forecast_model_query.BrowseForecastModels(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = featurestore_v1_feature_view_reporting_service_pb2.ScheduleFeatureViewReportRequest(
                annotations=dict(request.annotations),
                context=request.context,
                details=featurestore_v1_feature_view_reporting_service_pb2.ScheduleFeatureViewReportRequest.Details(
                    filters=dict(response_0.demand_forecast.metadata)
                ),
                reason=request.reason
            )
            document_2 = MessageToDict(outgoing_2, preserving_proto_field_name=True)
            outgoing_2 = ParseDict(
                document_2,
                featurestore_v1_feature_view_reporting_service_pb2.ScheduleFeatureViewReportRequest()
            )
            response_2 = await deps.clients.featurestore_feature_view_reporting.ScheduleFeatureViewReport(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            outgoing_3 = pipelines_v1_pipeline_reporting_service_pb2.SchedulePipelineReportRequest(
                annotations=dict(request.annotations),
                context=request.context,
                details=pipelines_v1_pipeline_reporting_service_pb2.SchedulePipelineReportRequest.Details(
                    period=response_2.period
                ),
                reason=request.reason
            )
            document_3 = MessageToJson(outgoing_3, preserving_proto_field_name=True)
            outgoing_3 = Parse(document_3, pipelines_v1_pipeline_reporting_service_pb2.SchedulePipelineReportRequest())
            response_3 = await deps.clients.pipelines_pipeline_reporting.SchedulePipelineReport(
                outgoing_3,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.demand_forecast.audit.updated_at
            if returned_0_0.ListFields():
                response.demand_forecast.audit.updated_at.MergeFrom(returned_0_0)
            returned_1_0 = response_1.result.reference_ids
            response.result.reference_ids.extend(returned_1_0)
            returned_1_1 = response_1.result.status
            if returned_1_1:
                response.result.status = returned_1_1
            returned_2_0 = response_2.result.message
            if returned_2_0:
                response.outcome.message = returned_2_0
            returned_2_1 = response_2.result.correlation_id
            if returned_2_1:
                response.result.correlation_id = returned_2_1
            returned_3_0 = response_3.result.message
            if returned_3_0:
                response.result.message = returned_3_0
            echoed_0 = request.demand_forecast_id
            response.demand_forecast.demand_forecast_id = echoed_0
            echoed_1 = request.demand_forecast.total
            response.demand_forecast.total.CopyFrom(echoed_1)
            return response

    async def handle_inspect_demand_forecast_workflow(
        self,
        request: forecasting_v1_demand_forecast_workflow_service_pb2.InspectDemandForecastWorkflowRequest
    ) -> forecasting_v1_demand_forecast_workflow_service_pb2.InspectDemandForecastWorkflowResponse:
        """Returns a demand forecast."""
        deps = self.deps
        response = forecasting_v1_demand_forecast_workflow_service_pb2.InspectDemandForecastWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('InspectDemandForecastWorkflow', extra={'fields': {'domain': 'forecasting'}})
            await deps.repository.audit(request.context.tenant_id, 'InspectDemandForecastWorkflow', {})
            response_0 = recommendations_v1_interaction_approval_service_pb2.SubmitInteractionResponse()
            outgoing_0 = recommendations_v1_interaction_approval_service_pb2.SubmitInteractionRequest(
                context=request.context,
                details=recommendations_v1_interaction_approval_service_pb2.SubmitInteractionRequest.Details(
                    approver=identity_v1_refs_pb2.UserRef(
                        email=request.context.actor.email,
                        user_id=request.context.actor.user_id
                    )
                )
            )
            response_0 = await deps.clients.recommendations_interaction_approval.SubmitInteraction(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_0)
            echoed_0 = request.demand_forecast_id
            response.demand_forecast.demand_forecast_id = echoed_0
            return response

    async def handle_list_demand_forecast_workflows(
        self,
        request: forecasting_v1_demand_forecast_workflow_service_pb2.ListDemandForecastWorkflowsRequest
    ) -> forecasting_v1_demand_forecast_workflow_service_pb2.ListDemandForecastWorkflowsResponse:
        """Lists demand forecasts a page at a time."""
        deps = self.deps
        response = forecasting_v1_demand_forecast_workflow_service_pb2.ListDemandForecastWorkflowsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ListDemandForecastWorkflows', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ListDemandForecastWorkflows',
                {'order_by': request.order_by}
            )
            response_0 = forecasting_v1_forecast_model_query_service_pb2.FindForecastModelsResponse()
            outgoing_0 = forecasting_v1_forecast_model_query_service_pb2.FindForecastModelsRequest(
                context=request.context,
                filter=forecasting_v1_forecast_model_query_service_pb2.FindForecastModelsRequest.Filter(
                    labels=dict(request.filter.labels)
                ),
                page=common_v1_paging_pb2.PageRequest(page_size=request.page.page_size)
            )
            response_0 = await deps.clients.forecasting_forecast_model_query.FindForecastModels(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.result.message = returned_0_0
            returned_0_1 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_1)
            return response

    async def handle_pause_demand_forecast_workflow(
        self,
        request: forecasting_v1_demand_forecast_workflow_service_pb2.PauseDemandForecastWorkflowRequest
    ) -> forecasting_v1_demand_forecast_workflow_service_pb2.PauseDemandForecastWorkflowResponse:
        """Pauses a demand forecast."""
        deps = self.deps
        response = forecasting_v1_demand_forecast_workflow_service_pb2.PauseDemandForecastWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('PauseDemandForecastWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'PauseDemandForecastWorkflow',
                {'reason': request.reason}
            )
            await deps.repository.save_demand_forecast(request.context.tenant_id, request.demand_forecast)
            response_0 = forecasting_v1_scenario_validation_service_pb2.ExplainScenarioDecisionResponse()
            response_1 = metrics_v1_metric_alert_query_service_pb2.ExportMetricAlertsResponse()
            outgoing_0 = forecasting_v1_scenario_validation_service_pb2.ExplainScenarioDecisionRequest(
                context=request.context,
                details=forecasting_v1_scenario_validation_service_pb2.ExplainScenarioDecisionRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(
                        preferred_channel=request.details.notify.preferred_channel
                    )
                ),
                scenario=forecasting_v1_forecasting_pb2.Scenario(
                    assignee=identity_v1_refs_pb2.UserRef(
                        display_name=request.demand_forecast.counterparty.display_name
                    ),
                    requester=common_v1_contact_pb2.ContactInfo(name=request.details.notify.name)
                )
            )
            registered_0 = cast(
                forecasting_v1_scenario_validation_service_pb2_grpc.ScenarioValidationServiceStub,
                deps.clients.registry['acme.forecasting.v1.ScenarioValidationService']
            )
            response_0 = await registered_0.ExplainScenarioDecision(outgoing_0, timeout=deps.settings.timeout)
            outgoing_1 = metrics_v1_metric_alert_query_service_pb2.ExportMetricAlertsRequest(
                context=request.context,
                filter=metrics_v1_metric_alert_query_service_pb2.ExportMetricAlertsRequest.Filter(
                    created_after=response_0.scenario.sla.due_at,
                    labels=dict(request.details.parameters),
                    region=request.demand_forecast.billing_address.region
                )
            )
            async for chunk_1 in deps.clients.metrics_metric_alert_query.ExportMetricAlerts(
                outgoing_1,
                timeout=deps.settings.timeout
            ):
                response_1 = chunk_1
            returned_0_0 = response_0.scenario.audit.updated_at
            if returned_0_0.ListFields():
                response.demand_forecast.audit.updated_at.MergeFrom(returned_0_0)
            echoed_0 = request.demand_forecast_id
            response.demand_forecast.demand_forecast_id = echoed_0
            echoed_1 = request.demand_forecast.status
            response.demand_forecast.status = echoed_1
            return response

    async def handle_resume_demand_forecast_workflow(
        self,
        request: forecasting_v1_demand_forecast_workflow_service_pb2.ResumeDemandForecastWorkflowRequest
    ) -> forecasting_v1_demand_forecast_workflow_service_pb2.ResumeDemandForecastWorkflowResponse:
        """Resumes a demand forecast."""
        deps = self.deps
        response = forecasting_v1_demand_forecast_workflow_service_pb2.ResumeDemandForecastWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ResumeDemandForecastWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ResumeDemandForecastWorkflow',
                {'reason': request.reason}
            )
            await deps.repository.save_demand_forecast(request.context.tenant_id, request.demand_forecast)
            response_0 = forecasting_v1_demand_forecast_service_pb2.CloneDemandForecastResponse()
            response_1 = forecasting_v1_scenario_calculation_service_pb2.QuoteScenarioResponse()
            command_0 = DemandForecastWorkflowResumeDemandForecastWorkflow0Command.model_validate(
                {
                    'context': request.context,
                    'demand_forecast_billing_address_country_code': request.demand_forecast.billing_address.country_code,
                    'demand_forecast_billing_address_lines': list(request.demand_forecast.billing_address.lines),
                    'demand_forecast_billing_address_postal_code': request.demand_forecast.billing_address.postal_code
                }
            )
            outgoing_0 = to_demand_forecast_workflow_resume_demand_forecast_workflow0_command(command_0)
            response_0 = await deps.clients.forecasting_demand_forecast.CloneDemandForecast(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = forecasting_v1_scenario_calculation_service_pb2.QuoteScenarioRequest(
                context=request.context,
                scenario=forecasting_v1_forecasting_pb2.Scenario(
                    audit=common_v1_audit_pb2.AuditInfo(
                        etag=response_0.demand_forecast.audit.etag,
                        updated_by=response_0.demand_forecast.audit.updated_by
                    )
                )
            )
            send_1 = partial(deps.clients.forecasting_scenario_calculation.QuoteScenario, timeout=deps.settings.timeout)
            response_1 = await send_1(outgoing_1)
            returned_0_0 = response_0.demand_forecast.audit.updated_at
            if returned_0_0.ListFields():
                response.demand_forecast.audit.updated_at.MergeFrom(returned_0_0)
            returned_1_0 = response_1.scenario.audit.etag
            if returned_1_0:
                response.demand_forecast.audit.etag = returned_1_0
            echoed_0 = request.demand_forecast_id
            response.demand_forecast.demand_forecast_id = echoed_0
            echoed_1 = request.demand_forecast.status
            response.demand_forecast.status = echoed_1
            return response

    async def handle_retry_demand_forecast_workflow(
        self,
        request: forecasting_v1_demand_forecast_workflow_service_pb2.RetryDemandForecastWorkflowRequest
    ) -> forecasting_v1_demand_forecast_workflow_service_pb2.RetryDemandForecastWorkflowResponse:
        """Retrys a demand forecast."""
        deps = self.deps
        response = forecasting_v1_demand_forecast_workflow_service_pb2.RetryDemandForecastWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('RetryDemandForecastWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'RetryDemandForecastWorkflow',
                {'reason': request.reason}
            )
            await deps.repository.save_demand_forecast(request.context.tenant_id, request.demand_forecast)
            response_0 = webhooks_v1_webhook_endpoint_service_pb2.SearchWebhookEndpointsResponse()
            response_1 = suppliers_v1_supplier_service_pb2.ListSuppliersResponse()
            requests_0: list[webhooks_v1_webhook_endpoint_service_pb2.SearchWebhookEndpointsRequest] = []
            for item_0 in request.demand_forecast.lines:
                outgoing_0 = webhooks_v1_webhook_endpoint_service_pb2.SearchWebhookEndpointsRequest(
                    context=request.context,
                    filter=webhooks_v1_webhook_endpoint_service_pb2.SearchWebhookEndpointsRequest.Filter(
                        labels=dict(item_0.attributes),
                        owner_id=item_0.line_id,
                        region=request.demand_forecast.billing_address.region
                    )
                )
                requests_0.append(outgoing_0)
            replies_0 = await asyncio.gather(*(
                deps.clients.webhooks_webhook_endpoint.SearchWebhookEndpoints(
                    entry,
                    timeout=deps.settings.timeout
                ) for entry in requests_0
            ))
            if replies_0:
                response_0 = replies_0[-1]
            callbacks_1: list[Callable[[], Awaitable[suppliers_v1_supplier_service_pb2.ListSuppliersResponse]]] = []
            for item_1 in request.demand_forecast.lines:
                outgoing_1 = suppliers_v1_supplier_service_pb2.ListSuppliersRequest(
                    context=request.context,
                    filter=suppliers_v1_supplier_service_pb2.ListSuppliersRequest.Filter(
                        labels=dict(item_1.attributes),
                        owner_id=item_1.line_id,
                        region=request.demand_forecast.billing_address.region
                    )
                )
                async def send_1(
                    payload: suppliers_v1_supplier_service_pb2.ListSuppliersRequest = outgoing_1
                ) -> suppliers_v1_supplier_service_pb2.ListSuppliersResponse:
                    return await deps.clients.suppliers_supplier.ListSuppliers(payload, timeout=deps.settings.timeout)
                callbacks_1.append(send_1)
            for callback_1 in callbacks_1:
                response_1 = await callback_1()
            echoed_0 = request.demand_forecast_id
            response.demand_forecast.demand_forecast_id = echoed_0
            echoed_1 = request.demand_forecast.notes
            response.demand_forecast.notes = echoed_1
            return response

    async def handle_signal_demand_forecast_workflow(
        self,
        request: forecasting_v1_demand_forecast_workflow_service_pb2.SignalDemandForecastWorkflowRequest
    ) -> forecasting_v1_demand_forecast_workflow_service_pb2.SignalDemandForecastWorkflowResponse:
        """Signals a demand forecast."""
        deps = self.deps
        response = forecasting_v1_demand_forecast_workflow_service_pb2.SignalDemandForecastWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info(
                'SignalDemandForecastWorkflow',
                extra={'fields': {'demand_forecast_id': request.demand_forecast.demand_forecast_id}}
            )
            await deps.repository.audit(
                request.context.tenant_id,
                'SignalDemandForecastWorkflow',
                {'demand_forecast_id': request.demand_forecast.demand_forecast_id}
            )
            await deps.repository.save_demand_forecast(request.context.tenant_id, request.demand_forecast)
            response_0 = forecasting_v1_forecast_model_query_service_pb2.SummarizeForecastModelsResponse()
            response_1 = pipelines_v1_pipeline_step_export_service_pb2.StreamPipelineStepExportResponse()
            outgoing_0 = forecasting_v1_forecast_model_query_service_pb2.SummarizeForecastModelsRequest(
                annotations=dict(request.annotations),
                context=request.context,
                reason=request.reason
            )
            port_0: DemandForecastWorkflowSignalDemandForecastWorkflow0Port = DemandForecastWorkflowSignalDemandForecastWorkflow0Adapter(
                deps.clients.forecasting_forecast_model_query,
                deps.settings.timeout
            )
            response_0 = await port_0.execute(outgoing_0)
            outgoing_1 = pipelines_v1_pipeline_step_export_service_pb2.StreamPipelineStepExportRequest(
                context=request.context,
                filter=pipelines_v1_pipeline_step_export_service_pb2.StreamPipelineStepExportRequest.Filter(
                    created_after=request.demand_forecast.due_at,
                    region=request.demand_forecast.billing_address.region
                )
            )
            async for chunk_1 in deps.clients.pipelines_pipeline_step_export.StreamPipelineStepExport(
                outgoing_1,
                timeout=deps.settings.timeout
            ):
                response_1 = chunk_1
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.outcome.message = returned_0_0
            returned_0_1 = response_0.result.status
            if returned_0_1:
                response.result.status = returned_0_1
            echoed_0 = request.demand_forecast_id
            response.demand_forecast.demand_forecast_id = echoed_0
            echoed_1 = request.demand_forecast.counterparty
            response.demand_forecast.counterparty.CopyFrom(echoed_1)
            return response

    async def handle_start_demand_forecast_workflow(
        self,
        request: forecasting_v1_demand_forecast_workflow_service_pb2.StartDemandForecastWorkflowRequest
    ) -> forecasting_v1_demand_forecast_workflow_service_pb2.StartDemandForecastWorkflowResponse:
        """Starts a demand forecast."""
        deps = self.deps
        response = forecasting_v1_demand_forecast_workflow_service_pb2.StartDemandForecastWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('StartDemandForecastWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'StartDemandForecastWorkflow',
                {'reason': request.reason}
            )
            await deps.repository.save_demand_forecast(request.context.tenant_id, request.demand_forecast)
            response_0 = forecasting_v1_demand_forecast_approval_service_pb2.SubmitDemandForecastResponse()
            outgoing_0 = forecasting_v1_demand_forecast_approval_service_pb2.SubmitDemandForecastRequest(
                context=request.context,
                demand_forecast=forecasting_v1_forecasting_pb2.DemandForecast(
                    audit=common_v1_audit_pb2.AuditInfo(created_at=request.demand_forecast.audit.created_at),
                    bank=forecasting_v1_forecasting_pb2.DemandForecastBankSettlement(
                        bic=request.demand_forecast.bank.bic
                    ),
                    counterparty=forecasting_v1_refs_pb2.ScenarioRef(
                        display_name=request.demand_forecast.counterparty.display_name
                    )
                )
            )
            response_0 = await DemandForecastWorkflowStartDemandForecastWorkflow0Adapter(
                deps.clients.forecasting_demand_forecast_approval,
                deps.settings.timeout
            )(outgoing_0)
            returned_0_0 = response_0.result.details
            response.result.details.update(returned_0_0)
            echoed_0 = request.demand_forecast_id
            response.demand_forecast.demand_forecast_id = echoed_0
            echoed_1 = request.demand_forecast.notes
            response.demand_forecast.notes = echoed_1
            return response
