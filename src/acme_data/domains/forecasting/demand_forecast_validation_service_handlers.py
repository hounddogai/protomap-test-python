"""Reusable transport mixin for DemandForecastValidationService."""

from __future__ import annotations

from collections.abc import AsyncIterator
from functools import partial
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
from acme.customers.v1 import refs_pb2 as customers_v1_refs_pb2
from acme.featurestore.v1 import feature_view_query_service_pb2 as featurestore_v1_feature_view_query_service_pb2
from acme.forecasting.v1 import (
    demand_forecast_validation_service_pb2 as forecasting_v1_demand_forecast_validation_service_pb2,
)
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.labeling.v1 import annotation_validation_service_pb2 as labeling_v1_annotation_validation_service_pb2
from acme.labeling.v1 import labeling_task_query_service_pb2 as labeling_v1_labeling_task_query_service_pb2
from acme.metrics.v1 import dashboard_notification_service_pb2 as metrics_v1_dashboard_notification_service_pb2
from acme.metrics.v1 import metric_series_history_service_pb2 as metrics_v1_metric_series_history_service_pb2
from acme.metrics.v1 import metrics_pb2 as metrics_v1_metrics_pb2
from acme.modelregistry.v1 import (
    model_version_validation_service_pb2 as modelregistry_v1_model_version_validation_service_pb2,
)
from acme.modelregistry.v1 import modelregistry_pb2 as modelregistry_v1_modelregistry_pb2
from acme.pipelines.v1 import pipeline_run_calculation_service_pb2 as pipelines_v1_pipeline_run_calculation_service_pb2
from acme.pipelines.v1 import pipeline_run_validation_service_pb2 as pipelines_v1_pipeline_run_validation_service_pb2
from acme.pipelines.v1 import pipelines_pb2 as pipelines_v1_pipelines_pb2
from acme.pipelines.v1 import refs_pb2 as pipelines_v1_refs_pb2
from acme.routing.v1 import route_service_pb2 as routing_v1_route_service_pb2
from acme.venues.v1 import venue_service_pb2 as venues_v1_venue_service_pb2
from acme.venues.v1 import venue_validation_service_pb2 as venues_v1_venue_validation_service_pb2
from acme.venues.v1 import venues_pb2 as venues_v1_venues_pb2

from acme_data.domains.forecasting.adapters import DemandForecastValidationPreviewDemandForecast0Adapter
from acme_data.domains.forecasting.adapters import DemandForecastValidationPreviewDemandForecast0Port
from acme_data.domains.forecasting.adapters import DemandForecastValidationValidateDemandForecast0Adapter
from acme_data.domains.forecasting.dependencies import Dependencies
from acme_data.domains.forecasting.models import DemandForecastValidationLintDemandForecasts0Command
from acme_data.domains.forecasting.models import to_demand_forecast_validation_lint_demand_forecasts0_command
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import run_steps
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_id
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class DemandForecastValidationServicerHandlers:
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    async def CheckDemandForecastEligibility(
        self, request: forecasting_v1_demand_forecast_validation_service_pb2.CheckDemandForecastEligibilityRequest, context: grpc.aio.ServicerContext,
    ) -> forecasting_v1_demand_forecast_validation_service_pb2.CheckDemandForecastEligibilityResponse:
        """Checks a demand forecast."""
        return await self.handle_check_demand_forecast_eligibility(request)

    @rpc_errors
    async def ExplainDemandForecastDecision(
        self, request: forecasting_v1_demand_forecast_validation_service_pb2.ExplainDemandForecastDecisionRequest, context: grpc.aio.ServicerContext,
    ) -> forecasting_v1_demand_forecast_validation_service_pb2.ExplainDemandForecastDecisionResponse:
        """Explains a demand forecast."""
        return await self.handle_explain_demand_forecast_decision(request)

    @rpc_errors
    @retry_transient
    async def GetDemandForecastRules(
        self, request: forecasting_v1_demand_forecast_validation_service_pb2.GetDemandForecastRulesRequest, context: grpc.aio.ServicerContext,
    ) -> forecasting_v1_demand_forecast_validation_service_pb2.GetDemandForecastRulesResponse:
        """Returns a demand forecast."""
        return await self.handle_get_demand_forecast_rules(request)

    @rpc_errors
    async def LintDemandForecasts(
        self, request: forecasting_v1_demand_forecast_validation_service_pb2.LintDemandForecastsRequest, context: grpc.aio.ServicerContext,
    ) -> forecasting_v1_demand_forecast_validation_service_pb2.LintDemandForecastsResponse:
        """Lints a demand forecast."""
        return await self.handle_lint_demand_forecasts(request)

    @rpc_errors
    async def NormalizeDemandForecast(
        self, request: forecasting_v1_demand_forecast_validation_service_pb2.NormalizeDemandForecastRequest, context: grpc.aio.ServicerContext,
    ) -> forecasting_v1_demand_forecast_validation_service_pb2.NormalizeDemandForecastResponse:
        """Normalizes a demand forecast."""
        return await self.handle_normalize_demand_forecast(request)

    @rpc_errors
    async def PreviewDemandForecast(
        self, request: forecasting_v1_demand_forecast_validation_service_pb2.PreviewDemandForecastRequest, context: grpc.aio.ServicerContext,
    ) -> forecasting_v1_demand_forecast_validation_service_pb2.PreviewDemandForecastResponse:
        """Previews a demand forecast."""
        return await self.handle_preview_demand_forecast(request)

    @rpc_errors
    async def ValidateDemandForecast(
        self, request: forecasting_v1_demand_forecast_validation_service_pb2.ValidateDemandForecastRequest, context: grpc.aio.ServicerContext,
    ) -> forecasting_v1_demand_forecast_validation_service_pb2.ValidateDemandForecastResponse:
        """Validates a demand forecast."""
        return await self.handle_validate_demand_forecast(request)

    async def handle_check_demand_forecast_eligibility(
        self,
        request: forecasting_v1_demand_forecast_validation_service_pb2.CheckDemandForecastEligibilityRequest
    ) -> forecasting_v1_demand_forecast_validation_service_pb2.CheckDemandForecastEligibilityResponse:
        """Checks a demand forecast."""
        deps = self.deps
        response = forecasting_v1_demand_forecast_validation_service_pb2.CheckDemandForecastEligibilityResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CheckDemandForecastEligibility', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'CheckDemandForecastEligibility',
                {'reason': request.reason}
            )
            await deps.repository.save_demand_forecast(request.context.tenant_id, request.demand_forecast)
            response_0 = venues_v1_venue_validation_service_pb2.ExplainVenueDecisionResponse()
            response_1 = pipelines_v1_pipeline_run_validation_service_pb2.NormalizePipelineRunResponse()
            outgoing_0 = venues_v1_venue_validation_service_pb2.ExplainVenueDecisionRequest(
                context=request.context,
                venue=venues_v1_venues_pb2.Venue(
                    address=common_v1_address_pb2.PostalAddress(
                        country_code=request.demand_forecast.billing_address.country_code,
                        region=request.demand_forecast.billing_address.region
                    ),
                    owner=identity_v1_refs_pb2.UserRef(display_name=request.demand_forecast.counterparty.display_name)
                )
            )
            document_0 = MessageToDict(outgoing_0, preserving_proto_field_name=True)
            outgoing_0 = ParseDict(document_0, venues_v1_venue_validation_service_pb2.ExplainVenueDecisionRequest())
            response_0 = await deps.clients.venues_venue_validation.ExplainVenueDecision(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = pipelines_v1_pipeline_run_validation_service_pb2.NormalizePipelineRunRequest(
                context=request.context,
                pipeline_run=pipelines_v1_pipelines_pb2.PipelineRun(
                    assignee=identity_v1_refs_pb2.UserRef(user_id=response_0.venue.owner.user_id),
                    audit=common_v1_audit_pb2.AuditInfo(
                        created_at=response_0.venue.audit.created_at,
                        etag=response_0.venue.audit.etag,
                        updated_at=response_0.venue.audit.updated_at
                    )
                )
            )
            document_1 = MessageToJson(outgoing_1, preserving_proto_field_name=True)
            outgoing_1 = Parse(
                document_1,
                pipelines_v1_pipeline_run_validation_service_pb2.NormalizePipelineRunRequest()
            )
            response_1 = await deps.clients.pipelines_pipeline_run_validation.NormalizePipelineRun(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.venue.audit.created_at
            if returned_0_0.ListFields():
                response.demand_forecast.audit.created_at.MergeFrom(returned_0_0)
            returned_0_1 = response_0.outcome.message
            if returned_0_1:
                response.result.message = returned_0_1
            returned_1_0 = response_1.pipeline_run.customer.display_name
            if returned_1_0:
                response.demand_forecast.counterparty.display_name = returned_1_0
            echoed_0 = request.demand_forecast_id
            response.demand_forecast.demand_forecast_id = echoed_0
            echoed_1 = request.demand_forecast.status
            response.demand_forecast.status = echoed_1
            return response

    async def handle_explain_demand_forecast_decision(
        self,
        request: forecasting_v1_demand_forecast_validation_service_pb2.ExplainDemandForecastDecisionRequest
    ) -> forecasting_v1_demand_forecast_validation_service_pb2.ExplainDemandForecastDecisionResponse:
        """Explains a demand forecast."""
        deps = self.deps
        response = forecasting_v1_demand_forecast_validation_service_pb2.ExplainDemandForecastDecisionResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ExplainDemandForecastDecision', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ExplainDemandForecastDecision',
                {'reason': request.reason}
            )
            await deps.repository.save_demand_forecast(request.context.tenant_id, request.demand_forecast)
            response_0 = labeling_v1_annotation_validation_service_pb2.PreviewAnnotationResponse()
            response_1 = pipelines_v1_pipeline_run_calculation_service_pb2.QuotePipelineRunResponse()
            outgoing_0 = labeling_v1_annotation_validation_service_pb2.PreviewAnnotationRequest(
                context=request.context,
                details=labeling_v1_annotation_validation_service_pb2.PreviewAnnotationRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(email=request.details.contact.email)
                )
            )
            outgoing_1 = pipelines_v1_pipeline_run_calculation_service_pb2.QuotePipelineRunRequest(
                context=request.context,
                pipeline_run=pipelines_v1_pipelines_pb2.PipelineRun(
                    audit=common_v1_audit_pb2.AuditInfo(etag=request.demand_forecast.audit.etag),
                    customer=pipelines_v1_refs_pb2.PipelineRef(
                        display_name=request.demand_forecast.counterparty.display_name
                    )
                )
            )
            response_0, response_1 = await asyncio.gather(
                deps.clients.labeling_annotation_validation.PreviewAnnotation(
                    outgoing_0,
                    timeout=deps.settings.timeout
                ),
                deps.clients.pipelines_pipeline_run_calculation.QuotePipelineRun(
                    outgoing_1,
                    timeout=deps.settings.timeout
                ),
            )
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.result.message = returned_0_0
            returned_1_0 = response_1.pipeline_run.customer.display_name
            if returned_1_0:
                response.demand_forecast.counterparty.display_name = returned_1_0
            echoed_0 = request.demand_forecast_id
            response.demand_forecast.demand_forecast_id = echoed_0
            echoed_1 = request.demand_forecast.due_at
            response.demand_forecast.due_at.CopyFrom(echoed_1)
            return response

    async def handle_get_demand_forecast_rules(
        self,
        request: forecasting_v1_demand_forecast_validation_service_pb2.GetDemandForecastRulesRequest
    ) -> forecasting_v1_demand_forecast_validation_service_pb2.GetDemandForecastRulesResponse:
        """Returns a demand forecast."""
        deps = self.deps
        response = forecasting_v1_demand_forecast_validation_service_pb2.GetDemandForecastRulesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('GetDemandForecastRules', extra={'fields': {'domain': 'forecasting'}})
            await deps.repository.audit(request.context.tenant_id, 'GetDemandForecastRules', {})
            response_0 = venues_v1_venue_service_pb2.CloneVenueResponse()
            outgoing_0 = venues_v1_venue_service_pb2.CloneVenueRequest(
                context=request.context,
                venue=venues_v1_venues_pb2.Venue(
                    owner=identity_v1_refs_pb2.UserRef(
                        email=request.context.actor.email,
                        user_id=request.context.actor.user_id
                    )
                )
            )
            response_0 = await deps.clients.venues_venue.CloneVenue(outgoing_0, timeout=deps.settings.timeout)
            returned_0_0 = response_0.result.details
            response.result.details.update(returned_0_0)
            echoed_0 = request.demand_forecast_id
            response.demand_forecast.demand_forecast_id = echoed_0
            return response

    async def handle_lint_demand_forecasts(
        self,
        request: forecasting_v1_demand_forecast_validation_service_pb2.LintDemandForecastsRequest
    ) -> forecasting_v1_demand_forecast_validation_service_pb2.LintDemandForecastsResponse:
        """Lints a demand forecast."""
        deps = self.deps
        response = forecasting_v1_demand_forecast_validation_service_pb2.LintDemandForecastsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('LintDemandForecasts', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'LintDemandForecasts', {'reason': request.reason})
            await deps.repository.save_demand_forecast(request.context.tenant_id, request.demand_forecast)
            response_0 = pipelines_v1_pipeline_run_validation_service_pb2.ValidatePipelineRunResponse()
            command_0 = DemandForecastValidationLintDemandForecasts0Command(
                context=request.context,
                details_contact_name=request.details.contact.name,
                pipeline_run_audit_updated_by=request.demand_forecast.audit.updated_by
            )
            outgoing_0 = to_demand_forecast_validation_lint_demand_forecasts0_command(command_0)
            response_0 = await deps.clients.pipelines_pipeline_run_validation.ValidatePipelineRun(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.pipeline_run.sla.due_at
            if returned_0_0.ListFields():
                response.demand_forecast.due_at.MergeFrom(returned_0_0)
            echoed_0 = request.demand_forecast_id
            response.demand_forecast.demand_forecast_id = echoed_0
            echoed_1 = request.demand_forecast.billing_address
            response.demand_forecast.billing_address.CopyFrom(echoed_1)
            return response

    async def handle_normalize_demand_forecast(
        self,
        request: forecasting_v1_demand_forecast_validation_service_pb2.NormalizeDemandForecastRequest
    ) -> forecasting_v1_demand_forecast_validation_service_pb2.NormalizeDemandForecastResponse:
        """Normalizes a demand forecast."""
        deps = self.deps
        response = forecasting_v1_demand_forecast_validation_service_pb2.NormalizeDemandForecastResponse()
        with tenant_scope(request.context.tenant_id):
            log.info(
                'NormalizeDemandForecast',
                extra={'fields': {'demand_forecast_id': request.demand_forecast.demand_forecast_id}}
            )
            await deps.repository.audit(
                request.context.tenant_id,
                'NormalizeDemandForecast',
                {'demand_forecast_id': request.demand_forecast.demand_forecast_id}
            )
            await deps.repository.save_demand_forecast(request.context.tenant_id, request.demand_forecast)
            response_0 = metrics_v1_dashboard_notification_service_pb2.UnsubscribeDashboardUpdatesResponse()
            response_1 = modelregistry_v1_model_version_validation_service_pb2.ScoreModelVersionResponse()
            response_2 = featurestore_v1_feature_view_query_service_pb2.SummarizeFeatureViewsResponse()
            response_3 = routing_v1_route_service_pb2.CloneRouteResponse()
            outgoing_0 = metrics_v1_dashboard_notification_service_pb2.UnsubscribeDashboardUpdatesRequest(
                context=request.context,
                details=metrics_v1_dashboard_notification_service_pb2.UnsubscribeDashboardUpdatesRequest.Details(
                    recipient=common_v1_contact_pb2.ContactInfo(name=request.details.contact.name)
                )
            )
            outgoing_2 = featurestore_v1_feature_view_query_service_pb2.SummarizeFeatureViewsRequest(
                context=request.context,
                reason=request.reason
            )
            response_0, response_2 = await asyncio.gather(
                deps.clients.metrics_dashboard_notification.UnsubscribeDashboardUpdates(
                    outgoing_0,
                    timeout=deps.settings.timeout
                ),
                deps.clients.featurestore_feature_view_query.SummarizeFeatureViews(
                    outgoing_2,
                    timeout=deps.settings.timeout
                ),
            )
            outgoing_1 = modelregistry_v1_model_version_validation_service_pb2.ScoreModelVersionRequest(
                context=request.context,
                details=modelregistry_v1_model_version_validation_service_pb2.ScoreModelVersionRequest.Details(
                    destination=common_v1_address_pb2.PostalAddress(
                        country_code=response_0.dashboard.billing_address.country_code,
                        recipient=response_0.dashboard.billing_address.recipient
                    )
                ),
                model_version=modelregistry_v1_modelregistry_pb2.ModelVersion(
                    subject=customers_v1_refs_pb2.CustomerRef(
                        display_name=request.demand_forecast.counterparty.display_name
                    )
                )
            )
            send_1 = partial(
                deps.clients.modelregistry_model_version_validation.ScoreModelVersion,
                timeout=deps.settings.timeout
            )
            response_1 = await send_1(outgoing_1)
            outgoing_3 = routing_v1_route_service_pb2.CloneRouteRequest()
            outgoing_3.context.CopyFrom(request.context)
            outgoing_3.route.card.token = response_0.dashboard.card.token
            outgoing_3.route.card.holder_name = response_0.dashboard.card.holder_name
            outgoing_3.context.tenant_id = tenant_id.get()
            response_3 = await deps.clients.routing_route.CloneRoute(outgoing_3, timeout=deps.settings.timeout)
            returned_0_0 = response_0.dashboard.billing_address.recipient
            if returned_0_0:
                response.demand_forecast.billing_address.recipient = returned_0_0
            returned_0_1 = response_0.result.message
            if returned_0_1:
                response.outcome.message = returned_0_1
            returned_1_0 = response_1.result.details
            response.result.details.update(returned_1_0)
            returned_1_1 = response_1.result.message
            if returned_1_1:
                response.outcome.message = returned_1_1
            returned_2_0 = response_2.result.status
            if returned_2_0:
                response.result.status = returned_2_0
            returned_2_1 = response_2.result.details
            response.result.details.update(returned_2_1)
            returned_3_0 = response_3.result.correlation_id
            if returned_3_0:
                response.result.correlation_id = returned_3_0
            echoed_0 = request.demand_forecast_id
            response.demand_forecast.demand_forecast_id = echoed_0
            echoed_1 = request.demand_forecast.number
            response.demand_forecast.number = echoed_1
            return response

    async def handle_preview_demand_forecast(
        self,
        request: forecasting_v1_demand_forecast_validation_service_pb2.PreviewDemandForecastRequest
    ) -> forecasting_v1_demand_forecast_validation_service_pb2.PreviewDemandForecastResponse:
        """Previews a demand forecast."""
        deps = self.deps
        response = forecasting_v1_demand_forecast_validation_service_pb2.PreviewDemandForecastResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('PreviewDemandForecast', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'PreviewDemandForecast', {'reason': request.reason})
            await deps.repository.save_demand_forecast(request.context.tenant_id, request.demand_forecast)
            response_0 = labeling_v1_labeling_task_query_service_pb2.FindLabelingTasksResponse()
            response_1 = metrics_v1_metric_series_history_service_pb2.AnnotateMetricSeriesVersionResponse()
            outgoing_0 = labeling_v1_labeling_task_query_service_pb2.FindLabelingTasksRequest(
                context=request.context,
                filter=labeling_v1_labeling_task_query_service_pb2.FindLabelingTasksRequest.Filter(
                    created_after=request.demand_forecast.audit.created_at,
                    owner_id=request.demand_forecast.counterparty.scenario_id,
                    region=request.demand_forecast.billing_address.region
                )
            )
            port_0: DemandForecastValidationPreviewDemandForecast0Port = DemandForecastValidationPreviewDemandForecast0Adapter(
                deps.clients.labeling_labeling_task_query,
                deps.settings.timeout
            )
            response_0 = await port_0.execute(outgoing_0)
            outgoing_1 = metrics_v1_metric_series_history_service_pb2.AnnotateMetricSeriesVersionRequest(
                context=request.context,
                metric_series=metrics_v1_metrics_pb2.MetricSeries(
                    address=common_v1_address_pb2.PostalAddress(
                        locality=request.demand_forecast.billing_address.locality
                    ),
                    audit=common_v1_audit_pb2.AuditInfo(created_at=request.demand_forecast.audit.created_at)
                )
            )
            steps_1 = [
                partial(
                    deps.clients.metrics_metric_series_history.AnnotateMetricSeriesVersion,
                    outgoing_1,
                    timeout=deps.settings.timeout
                )
            ]
            results_1 = await run_steps(steps_1)
            response_1 = results_1[-1]
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.outcome.message = returned_0_0
            returned_1_0 = response_1.result.status
            if returned_1_0:
                response.result.status = returned_1_0
            returned_1_1 = response_1.metric_series.audit.created_by
            if returned_1_1:
                response.demand_forecast.audit.created_by = returned_1_1
            echoed_0 = request.demand_forecast_id
            response.demand_forecast.demand_forecast_id = echoed_0
            echoed_1 = request.demand_forecast.counterparty
            response.demand_forecast.counterparty.CopyFrom(echoed_1)
            return response

    async def handle_validate_demand_forecast(
        self,
        request: forecasting_v1_demand_forecast_validation_service_pb2.ValidateDemandForecastRequest
    ) -> forecasting_v1_demand_forecast_validation_service_pb2.ValidateDemandForecastResponse:
        """Validates a demand forecast."""
        deps = self.deps
        response = forecasting_v1_demand_forecast_validation_service_pb2.ValidateDemandForecastResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ValidateDemandForecast', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'ValidateDemandForecast', {'reason': request.reason})
            await deps.repository.save_demand_forecast(request.context.tenant_id, request.demand_forecast)
            response_0 = pipelines_v1_pipeline_run_validation_service_pb2.LintPipelineRunsResponse()
            outgoing_0 = pipelines_v1_pipeline_run_validation_service_pb2.LintPipelineRunsRequest(
                context=request.context,
                pipeline_run=pipelines_v1_pipelines_pb2.PipelineRun(
                    audit=common_v1_audit_pb2.AuditInfo(created_at=request.demand_forecast.audit.created_at)
                )
            )
            response_0 = await DemandForecastValidationValidateDemandForecast0Adapter(
                deps.clients.pipelines_pipeline_run_validation,
                deps.settings.timeout
            )(outgoing_0)
            returned_0_0 = response_0.outcome.reference_id
            if returned_0_0:
                response.outcome.reference_id = returned_0_0
            echoed_0 = request.demand_forecast_id
            response.demand_forecast.demand_forecast_id = echoed_0
            echoed_1 = request.demand_forecast.total
            response.demand_forecast.total.CopyFrom(echoed_1)
            return response
