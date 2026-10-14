"""Reusable transport mixin for ForecastModelWorkflowService."""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any
from typing import cast
import asyncio
import logging

import grpc

from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.forecasting.v1 import (
    forecast_model_approval_service_pb2 as forecasting_v1_forecast_model_approval_service_pb2,
)
from acme.forecasting.v1 import (
    forecast_model_validation_service_pb2 as forecasting_v1_forecast_model_validation_service_pb2,
)
from acme.forecasting.v1 import (
    forecast_model_workflow_service_pb2 as forecasting_v1_forecast_model_workflow_service_pb2,
)
from acme.forecasting.v1 import forecasting_pb2 as forecasting_v1_forecasting_pb2
from acme.forecasting.v1 import scenario_approval_service_pb2 as forecasting_v1_scenario_approval_service_pb2
from acme.forecasting.v1 import scenario_calculation_service_pb2 as forecasting_v1_scenario_calculation_service_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.labeling.v1 import labeling_pb2 as labeling_v1_labeling_pb2
from acme.labeling.v1 import labeling_task_workflow_service_pb2 as labeling_v1_labeling_task_workflow_service_pb2
from acme.metrics.v1 import metric_alert_history_service_pb2 as metrics_v1_metric_alert_history_service_pb2
from acme.metrics.v1 import metrics_pb2 as metrics_v1_metrics_pb2
from acme.recommendations.v1 import (
    recommendation_model_workflow_service_pb2 as recommendations_v1_recommendation_model_workflow_service_pb2,
)

from acme_data.domains.forecasting.dependencies import Dependencies
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class ForecastModelWorkflowServicerHandlers:
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    async def AdvanceForecastModelWorkflow(
        self, request: forecasting_v1_forecast_model_workflow_service_pb2.AdvanceForecastModelWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> forecasting_v1_forecast_model_workflow_service_pb2.AdvanceForecastModelWorkflowResponse:
        """Advances a forecast model."""
        return await self.handle_advance_forecast_model_workflow(request)

    @rpc_errors
    async def CancelForecastModelWorkflow(
        self, request: forecasting_v1_forecast_model_workflow_service_pb2.CancelForecastModelWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> forecasting_v1_forecast_model_workflow_service_pb2.CancelForecastModelWorkflowResponse:
        """Cancels a forecast model."""
        return await self.handle_cancel_forecast_model_workflow(request)

    @rpc_errors
    @retry_transient
    async def ListForecastModelWorkflows(
        self, request: forecasting_v1_forecast_model_workflow_service_pb2.ListForecastModelWorkflowsRequest, context: grpc.aio.ServicerContext,
    ) -> forecasting_v1_forecast_model_workflow_service_pb2.ListForecastModelWorkflowsResponse:
        """Lists forecast models a page at a time."""
        return await self.handle_list_forecast_model_workflows(request)

    @rpc_errors
    async def RetryForecastModelWorkflow(
        self, request: forecasting_v1_forecast_model_workflow_service_pb2.RetryForecastModelWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> forecasting_v1_forecast_model_workflow_service_pb2.RetryForecastModelWorkflowResponse:
        """Retrys a forecast model."""
        return await self.handle_retry_forecast_model_workflow(request)

    @rpc_errors
    async def SignalForecastModelWorkflow(
        self, request: forecasting_v1_forecast_model_workflow_service_pb2.SignalForecastModelWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> forecasting_v1_forecast_model_workflow_service_pb2.SignalForecastModelWorkflowResponse:
        """Signals a forecast model."""
        return await self.handle_signal_forecast_model_workflow(request)

    @rpc_errors
    async def StartForecastModelWorkflow(
        self, request: forecasting_v1_forecast_model_workflow_service_pb2.StartForecastModelWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> forecasting_v1_forecast_model_workflow_service_pb2.StartForecastModelWorkflowResponse:
        """Starts a forecast model."""
        return await self.handle_start_forecast_model_workflow(request)

    async def handle_advance_forecast_model_workflow(
        self,
        request: forecasting_v1_forecast_model_workflow_service_pb2.AdvanceForecastModelWorkflowRequest
    ) -> forecasting_v1_forecast_model_workflow_service_pb2.AdvanceForecastModelWorkflowResponse:
        """Advances a forecast model."""
        deps = self.deps
        response = forecasting_v1_forecast_model_workflow_service_pb2.AdvanceForecastModelWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('AdvanceForecastModelWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'AdvanceForecastModelWorkflow',
                {'reason': request.reason}
            )
            await deps.repository.save_forecast_model(request.context.tenant_id, request.forecast_model)
            response_0 = forecasting_v1_forecast_model_validation_service_pb2.ScoreForecastModelResponse()
            response_1 = metrics_v1_metric_alert_history_service_pb2.AnnotateMetricAlertVersionResponse()
            outgoing_0 = forecasting_v1_forecast_model_validation_service_pb2.ScoreForecastModelRequest(
                context=request.context,
                details=forecasting_v1_forecast_model_validation_service_pb2.ScoreForecastModelRequest.Details(
                    destination=common_v1_address_pb2.PostalAddress(recipient=request.forecast_model.address.recipient)
                ),
                forecast_model=forecasting_v1_forecasting_pb2.ForecastModel(
                    components={
                        'primary': forecasting_v1_forecasting_pb2.ForecastModelComponent(
                            quantity=request.forecast_model.components.get(
                                'primary',
                                forecasting_v1_forecasting_pb2.ForecastModelComponent()
                            ).quantity
                        )
                    },
                    dimensions=forecasting_v1_forecasting_pb2.ForecastModelDimensions(
                        length=request.forecast_model.dimensions.length
                    )
                )
            )
            response_0 = cast(forecasting_v1_forecast_model_validation_service_pb2.ScoreForecastModelResponse, await deps.bus.request(
                'acme.forecasting.v1.ForecastModelWorkflowService/AdvanceForecastModelWorkflow/0', outgoing_0, deps.settings.timeout,
            ))
            outgoing_1 = metrics_v1_metric_alert_history_service_pb2.AnnotateMetricAlertVersionRequest(
                context=request.context,
                metric_alert=metrics_v1_metrics_pb2.MetricAlert(
                    owner=identity_v1_refs_pb2.UserRef(email=request.forecast_model.owner.email)
                )
            )
            response_1 = await deps.clients.metrics_metric_alert_history.AnnotateMetricAlertVersion(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.forecast_model.dimensions.unit
            if returned_0_0:
                response.forecast_model.dimensions.unit = returned_0_0
            returned_1_0 = response_1.metric_alert.audit.updated_by
            if returned_1_0:
                response.forecast_model.audit.updated_by = returned_1_0
            echoed_0 = request.forecast_model_id
            response.forecast_model.forecast_model_id = echoed_0
            echoed_1 = request.forecast_model.specs
            response.forecast_model.specs.update(echoed_1)
            return response

    async def handle_cancel_forecast_model_workflow(
        self,
        request: forecasting_v1_forecast_model_workflow_service_pb2.CancelForecastModelWorkflowRequest
    ) -> forecasting_v1_forecast_model_workflow_service_pb2.CancelForecastModelWorkflowResponse:
        """Cancels a forecast model."""
        deps = self.deps
        response = forecasting_v1_forecast_model_workflow_service_pb2.CancelForecastModelWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CancelForecastModelWorkflow', extra={'fields': {'forecast_model_id': request.forecast_model_id}})
            await deps.repository.audit(
                request.context.tenant_id,
                'CancelForecastModelWorkflow',
                {'forecast_model_id': request.forecast_model_id}
            )
            await deps.repository.save_forecast_model(request.context.tenant_id, request.forecast_model)
            response_0 = labeling_v1_labeling_task_workflow_service_pb2.CancelLabelingTaskWorkflowResponse()
            response_1 = forecasting_v1_scenario_calculation_service_pb2.SimulateScenarioResponse()
            outgoing_0 = labeling_v1_labeling_task_workflow_service_pb2.CancelLabelingTaskWorkflowRequest(
                context=request.context,
                labeling_task=labeling_v1_labeling_pb2.LabelingTask(
                    requester=common_v1_contact_pb2.ContactInfo(email=request.details.notify.email)
                )
            )
            method_name_0 = 'CancelLabelingTaskWorkflow'
            response_0 = await getattr(
                deps.clients.labeling_labeling_task_workflow,
                method_name_0
            )(outgoing_0, timeout=deps.settings.timeout)
            fields_1: dict[str, Any] = {
                'context': request.context,
                'scenario': {
                    'audit': {'created_at': response_0.labeling_task.audit.created_at},
                    'requester': {'email': request.details.notify.email, 'name': request.details.notify.name}
                }
            }
            outgoing_1 = forecasting_v1_scenario_calculation_service_pb2.SimulateScenarioRequest(**fields_1)
            response_1 = await deps.clients.forecasting_scenario_calculation.SimulateScenario(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.outcome.effective_at
            if returned_0_0.ListFields():
                response.outcome.effective_at.MergeFrom(returned_0_0)
            returned_1_0 = response_1.scenario.customer.forecast_model_id
            if returned_1_0:
                response.forecast_model.forecast_model_id = returned_1_0
            returned_1_1 = response_1.result.status
            if returned_1_1:
                response.outcome.status = returned_1_1
            echoed_0 = request.forecast_model.capacity
            response.forecast_model.capacity = echoed_0
            echoed_1 = request.forecast_model.code
            response.forecast_model.code = echoed_1
            return response

    async def handle_list_forecast_model_workflows(
        self,
        request: forecasting_v1_forecast_model_workflow_service_pb2.ListForecastModelWorkflowsRequest
    ) -> forecasting_v1_forecast_model_workflow_service_pb2.ListForecastModelWorkflowsResponse:
        """Lists forecast models a page at a time."""
        deps = self.deps
        response = forecasting_v1_forecast_model_workflow_service_pb2.ListForecastModelWorkflowsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ListForecastModelWorkflows', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ListForecastModelWorkflows',
                {'order_by': request.order_by}
            )
            return response

    async def handle_retry_forecast_model_workflow(
        self,
        request: forecasting_v1_forecast_model_workflow_service_pb2.RetryForecastModelWorkflowRequest
    ) -> forecasting_v1_forecast_model_workflow_service_pb2.RetryForecastModelWorkflowResponse:
        """Retrys a forecast model."""
        deps = self.deps
        response = forecasting_v1_forecast_model_workflow_service_pb2.RetryForecastModelWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('RetryForecastModelWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'RetryForecastModelWorkflow',
                {'reason': request.reason}
            )
            await deps.repository.save_forecast_model(request.context.tenant_id, request.forecast_model)
            response_0 = forecasting_v1_scenario_approval_service_pb2.EscalateScenarioResponse()
            response_1 = forecasting_v1_forecast_model_approval_service_pb2.RejectForecastModelResponse()
            outgoing_0 = forecasting_v1_scenario_approval_service_pb2.EscalateScenarioRequest(
                context=request.context,
                details=forecasting_v1_scenario_approval_service_pb2.EscalateScenarioRequest.Details(
                    approver=identity_v1_refs_pb2.UserRef(
                        display_name=request.forecast_model.owner.display_name,
                        email=request.details.notify.email
                    )
                )
            )
            outgoing_1 = forecasting_v1_forecast_model_approval_service_pb2.RejectForecastModelRequest(
                context=request.context,
                details=forecasting_v1_forecast_model_approval_service_pb2.RejectForecastModelRequest.Details(
                    approver=identity_v1_refs_pb2.UserRef(email=request.forecast_model.owner.email)
                ),
                forecast_model=forecasting_v1_forecasting_pb2.ForecastModel(
                    dimensions=forecasting_v1_forecasting_pb2.ForecastModelDimensions(
                        height=request.forecast_model.dimensions.height
                    )
                )
            )
            response_0, response_1 = await asyncio.gather(
                deps.clients.forecasting_scenario_approval.EscalateScenario(outgoing_0, timeout=deps.settings.timeout),
                deps.clients.forecasting_forecast_model_approval.RejectForecastModel(
                    outgoing_1,
                    timeout=deps.settings.timeout
                ),
            )
            returned_0_0 = response_0.scenario.tags
            response.forecast_model.tags.extend(returned_0_0)
            returned_1_0 = response_1.forecast_model.name
            if returned_1_0:
                response.forecast_model.name = returned_1_0
            echoed_0 = request.forecast_model_id
            response.forecast_model.forecast_model_id = echoed_0
            echoed_1 = request.forecast_model.specs
            response.forecast_model.specs.update(echoed_1)
            return response

    async def handle_signal_forecast_model_workflow(
        self,
        request: forecasting_v1_forecast_model_workflow_service_pb2.SignalForecastModelWorkflowRequest
    ) -> forecasting_v1_forecast_model_workflow_service_pb2.SignalForecastModelWorkflowResponse:
        """Signals a forecast model."""
        deps = self.deps
        response = forecasting_v1_forecast_model_workflow_service_pb2.SignalForecastModelWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SignalForecastModelWorkflow', extra={'fields': {'forecast_model_id': request.forecast_model_id}})
            await deps.repository.audit(
                request.context.tenant_id,
                'SignalForecastModelWorkflow',
                {'forecast_model_id': request.forecast_model_id}
            )
            await deps.repository.save_forecast_model(request.context.tenant_id, request.forecast_model)
            response_0 = forecasting_v1_scenario_calculation_service_pb2.EstimateScenarioResponse()
            outgoing_0 = forecasting_v1_scenario_calculation_service_pb2.EstimateScenarioRequest()
            outgoing_0.context.CopyFrom(request.context)
            outgoing_0.scenario.requester.email = request.forecast_model.owner.email
            merged_0 = forecasting_v1_scenario_calculation_service_pb2.EstimateScenarioRequest()
            merged_0.MergeFrom(outgoing_0)
            outgoing_0.CopyFrom(merged_0)
            response_0 = await deps.clients.forecasting_scenario_calculation.EstimateScenario(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.scenario.customer.forecast_model_id
            if returned_0_0:
                response.forecast_model.forecast_model_id = returned_0_0
            returned_0_1 = response_0.result.correlation_id
            if returned_0_1:
                response.result.correlation_id = returned_0_1
            echoed_0 = request.forecast_model.name
            response.forecast_model.name = echoed_0
            echoed_1 = request.forecast_model.status
            response.forecast_model.status = echoed_1
            return response

    async def handle_start_forecast_model_workflow(
        self,
        request: forecasting_v1_forecast_model_workflow_service_pb2.StartForecastModelWorkflowRequest
    ) -> forecasting_v1_forecast_model_workflow_service_pb2.StartForecastModelWorkflowResponse:
        """Starts a forecast model."""
        deps = self.deps
        response = forecasting_v1_forecast_model_workflow_service_pb2.StartForecastModelWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('StartForecastModelWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'StartForecastModelWorkflow',
                {'reason': request.reason}
            )
            await deps.repository.save_forecast_model(request.context.tenant_id, request.forecast_model)
            response_0 = recommendations_v1_recommendation_model_workflow_service_pb2.ListRecommendationModelWorkflowsResponse()
            outgoing_0 = recommendations_v1_recommendation_model_workflow_service_pb2.ListRecommendationModelWorkflowsRequest()
            outgoing_0.context.CopyFrom(request.context)
            if request.forecast_model.WhichOneof('locator') == 'address':
                outgoing_0.filter.region = request.forecast_model.address.region
            outgoing_0.filter.created_after.CopyFrom(request.forecast_model.audit.created_at)
            outgoing_0.filter.owner_id = request.forecast_model.owner.user_id
            response_0 = await deps.clients.recommendations_recommendation_model_workflow.ListRecommendationModelWorkflows(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.outcome.message = returned_0_0
            returned_0_1 = response_0.result.details
            response.result.details.update(returned_0_1)
            echoed_0 = request.forecast_model_id
            response.forecast_model.forecast_model_id = echoed_0
            echoed_1 = request.forecast_model.capacity
            response.forecast_model.capacity = echoed_1
            return response
