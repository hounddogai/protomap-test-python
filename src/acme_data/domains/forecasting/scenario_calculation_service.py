"""Computes the figures of a scenario, such as totals, taxes, and estimates."""

from __future__ import annotations

from collections.abc import AsyncIterator
from collections.abc import Awaitable
from collections.abc import Callable
from functools import partial
from typing import cast
import asyncio
import logging

from google.protobuf.json_format import MessageToDict
from google.protobuf.json_format import ParseDict
import grpc

from acme.appointments.v1 import appointment_query_service_pb2 as appointments_v1_appointment_query_service_pb2
from acme.audit.v1 import audit_event_validation_service_pb2 as audit_v1_audit_event_validation_service_pb2
from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.datasets.v1 import (
    dataset_version_validation_service_pb2 as datasets_v1_dataset_version_validation_service_pb2,
)
from acme.forecasting.v1 import (
    demand_forecast_validation_service_pb2 as forecasting_v1_demand_forecast_validation_service_pb2,
)
from acme.forecasting.v1 import forecasting_pb2 as forecasting_v1_forecasting_pb2
from acme.forecasting.v1 import refs_pb2 as forecasting_v1_refs_pb2
from acme.forecasting.v1 import scenario_calculation_service_pb2 as forecasting_v1_scenario_calculation_service_pb2
from acme.forecasting.v1 import (
    scenario_calculation_service_pb2_grpc as forecasting_v1_scenario_calculation_service_pb2_grpc,
)
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.identity.v1 import user_validation_service_pb2 as identity_v1_user_validation_service_pb2
from acme.labeling.v1 import label_set_validation_service_pb2 as labeling_v1_label_set_validation_service_pb2
from acme.labeling.v1 import labeling_pb2 as labeling_v1_labeling_pb2
from acme.metrics.v1 import dashboard_sync_service_pb2 as metrics_v1_dashboard_sync_service_pb2
from acme.metrics.v1 import metric_series_notification_service_pb2 as metrics_v1_metric_series_notification_service_pb2
from acme.metrics.v1 import metric_series_validation_service_pb2 as metrics_v1_metric_series_validation_service_pb2
from acme.metrics.v1 import metrics_pb2 as metrics_v1_metrics_pb2
from acme.modelregistry.v1 import (
    registered_model_query_service_pb2 as modelregistry_v1_registered_model_query_service_pb2,
)
from acme.venues.v1 import venue_query_service_pb2 as venues_v1_venue_query_service_pb2

from acme_data.domains.forecasting import hooks
from acme_data.domains.forecasting.adapters import ScenarioCalculationEstimateScenario2Adapter
from acme_data.domains.forecasting.adapters import ScenarioCalculationEstimateScenario2Port
from acme_data.domains.forecasting.dependencies import Dependencies
from acme_data.domains.forecasting.models import ScenarioCalculationCalculateScenario0Command
from acme_data.domains.forecasting.models import ScenarioCalculationCalculateScenario1Command
from acme_data.domains.forecasting.models import to_scenario_calculation_calculate_scenario0_command
from acme_data.domains.forecasting.models import to_scenario_calculation_calculate_scenario1_command
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_id
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class ScenarioCalculationServicer(
    forecasting_v1_scenario_calculation_service_pb2_grpc.ScenarioCalculationServiceServicer
):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    async def CalculateScenario(
        self, request: forecasting_v1_scenario_calculation_service_pb2.CalculateScenarioRequest, context: grpc.aio.ServicerContext,
    ) -> forecasting_v1_scenario_calculation_service_pb2.CalculateScenarioResponse:
        """Calculates a scenario."""
        return await self.handle_calculate_scenario(request)

    @rpc_errors
    async def CompareScenarioOptions(
        self, request: forecasting_v1_scenario_calculation_service_pb2.CompareScenarioOptionsRequest, context: grpc.aio.ServicerContext,
    ) -> forecasting_v1_scenario_calculation_service_pb2.CompareScenarioOptionsResponse:
        """Compares a scenario."""
        return await self.handle_compare_scenario_options(request)

    @rpc_errors
    async def EstimateScenario(
        self, request: forecasting_v1_scenario_calculation_service_pb2.EstimateScenarioRequest, context: grpc.aio.ServicerContext,
    ) -> forecasting_v1_scenario_calculation_service_pb2.EstimateScenarioResponse:
        """Estimates a scenario."""
        return await self.handle_estimate_scenario(request)

    @rpc_errors
    async def ExplainScenarioCalculation(
        self, request: forecasting_v1_scenario_calculation_service_pb2.ExplainScenarioCalculationRequest, context: grpc.aio.ServicerContext,
    ) -> forecasting_v1_scenario_calculation_service_pb2.ExplainScenarioCalculationResponse:
        """Explains a scenario."""
        return await self.handle_explain_scenario_calculation(request)

    @rpc_errors
    @retry_transient
    async def GetScenarioRates(
        self, request: forecasting_v1_scenario_calculation_service_pb2.GetScenarioRatesRequest, context: grpc.aio.ServicerContext,
    ) -> forecasting_v1_scenario_calculation_service_pb2.GetScenarioRatesResponse:
        """Returns a scenario."""
        return await self.handle_get_scenario_rates(request)

    @rpc_errors
    async def QuoteScenario(
        self, request: forecasting_v1_scenario_calculation_service_pb2.QuoteScenarioRequest, context: grpc.aio.ServicerContext,
    ) -> forecasting_v1_scenario_calculation_service_pb2.QuoteScenarioResponse:
        """Quotes a scenario."""
        return await self.handle_quote_scenario(request)

    @rpc_errors
    async def RecalculateScenarios(
        self, request: forecasting_v1_scenario_calculation_service_pb2.RecalculateScenariosRequest, context: grpc.aio.ServicerContext,
    ) -> forecasting_v1_scenario_calculation_service_pb2.RecalculateScenariosResponse:
        """Recalculates a scenario."""
        return await self.handle_recalculate_scenarios(request)

    @rpc_errors
    async def SimulateScenario(
        self, request: forecasting_v1_scenario_calculation_service_pb2.SimulateScenarioRequest, context: grpc.aio.ServicerContext,
    ) -> forecasting_v1_scenario_calculation_service_pb2.SimulateScenarioResponse:
        """Simulates a scenario."""
        return await self.handle_simulate_scenario(request)

    async def handle_calculate_scenario(
        self,
        request: forecasting_v1_scenario_calculation_service_pb2.CalculateScenarioRequest
    ) -> forecasting_v1_scenario_calculation_service_pb2.CalculateScenarioResponse:
        """Calculates a scenario."""
        deps = self.deps
        response = forecasting_v1_scenario_calculation_service_pb2.CalculateScenarioResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CalculateScenario', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'CalculateScenario', {'reason': request.reason})
            await deps.repository.save_scenario(request.context.tenant_id, request.scenario)
            response_0 = identity_v1_user_validation_service_pb2.ScoreUserResponse()
            response_1 = datasets_v1_dataset_version_validation_service_pb2.ScoreDatasetVersionResponse()
            command_0 = ScenarioCalculationCalculateScenario0Command(
                context=request.context,
                user_relationship_manager_user_id=request.scenario.assignee.user_id,
                user_audit_updated_by=request.scenario.audit.updated_by,
                details_destination_recipient=request.details.destination.recipient,
                user_primary_address_locality=request.details.destination.locality
            )
            outgoing_0 = to_scenario_calculation_calculate_scenario0_command(command_0)
            response_0 = await deps.clients.identity_user_validation.ScoreUser(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            command_1 = ScenarioCalculationCalculateScenario1Command.model_validate(
                {
                    'context': request.context,
                    'details_destination_locality': request.details.destination.locality,
                    'details_destination_lines': list(response_0.user.primary_address.lines),
                    'dataset_version_subject_email': request.scenario.requester.email,
                    'details_destination_region': request.details.destination.region
                }
            )
            outgoing_1 = to_scenario_calculation_calculate_scenario1_command(command_1)
            response_1 = await deps.clients.datasets_dataset_version_validation.ScoreDatasetVersion(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.user.audit.updated_by
            if returned_0_0:
                response.scenario.audit.updated_by = returned_0_0
            returned_0_1 = response_0.result.message
            if returned_0_1:
                response.result.message = returned_0_1
            returned_1_0 = response_1.result.reference_ids
            response.result.reference_ids.extend(returned_1_0)
            returned_1_1 = response_1.result.details
            response.result.details.update(returned_1_1)
            echoed_0 = request.scenario_id
            response.scenario.scenario_id = echoed_0
            echoed_1 = request.scenario.priority
            response.scenario.priority = echoed_1
            return response

    async def handle_compare_scenario_options(
        self,
        request: forecasting_v1_scenario_calculation_service_pb2.CompareScenarioOptionsRequest
    ) -> forecasting_v1_scenario_calculation_service_pb2.CompareScenarioOptionsResponse:
        """Compares a scenario."""
        deps = self.deps
        response = forecasting_v1_scenario_calculation_service_pb2.CompareScenarioOptionsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CompareScenarioOptions', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'CompareScenarioOptions', {'reason': request.reason})
            await deps.repository.save_scenario(request.context.tenant_id, request.scenario)
            response_0 = forecasting_v1_demand_forecast_validation_service_pb2.NormalizeDemandForecastResponse()
            outgoing_0 = forecasting_v1_demand_forecast_validation_service_pb2.NormalizeDemandForecastRequest(
                context=request.context,
                demand_forecast=forecasting_v1_forecasting_pb2.DemandForecast(
                    audit=common_v1_audit_pb2.AuditInfo(created_by=request.scenario.audit.created_by),
                    counterparty=forecasting_v1_refs_pb2.ScenarioRef(
                        display_name=request.scenario.assignee.display_name
                    )
                )
            )
            send_0 = partial(
                deps.clients.forecasting_demand_forecast_validation.NormalizeDemandForecast,
                timeout=deps.settings.timeout
            )
            response_0 = await send_0(outgoing_0)
            returned_0_0 = response_0.demand_forecast.counterparty.display_name
            if returned_0_0:
                response.scenario.assignee.display_name = returned_0_0
            returned_0_1 = response_0.result.correlation_id
            if returned_0_1:
                response.result.correlation_id = returned_0_1
            echoed_0 = request.scenario_id
            response.scenario.scenario_id = echoed_0
            echoed_1 = request.scenario.requester
            response.scenario.requester.CopyFrom(echoed_1)
            return response

    async def handle_estimate_scenario(
        self,
        request: forecasting_v1_scenario_calculation_service_pb2.EstimateScenarioRequest
    ) -> forecasting_v1_scenario_calculation_service_pb2.EstimateScenarioResponse:
        """Estimates a scenario."""
        deps = self.deps
        response = forecasting_v1_scenario_calculation_service_pb2.EstimateScenarioResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('EstimateScenario', extra={'fields': {'currency_code': request.details.currency_code}})
            await deps.repository.audit(
                request.context.tenant_id,
                'EstimateScenario',
                {'currency_code': request.details.currency_code}
            )
            await deps.repository.save_scenario(request.context.tenant_id, request.scenario)
            response_0 = venues_v1_venue_query_service_pb2.SummarizeVenuesResponse()
            response_1 = audit_v1_audit_event_validation_service_pb2.PreviewAuditEventResponse()
            response_2 = forecasting_v1_demand_forecast_validation_service_pb2.NormalizeDemandForecastResponse()
            outgoing_0 = venues_v1_venue_query_service_pb2.SummarizeVenuesRequest(
                annotations=dict(request.annotations),
                context=request.context,
                reason=request.reason
            )
            response_0 = await hooks.scenario_calculation_estimate_scenario0(
                deps.clients.venues_venue_query,
                outgoing_0,
                deps.settings.timeout
            )
            outgoing_1 = audit_v1_audit_event_validation_service_pb2.PreviewAuditEventRequest()
            outgoing_1.context.CopyFrom(request.context)
            outgoing_1.details.contact.email = request.scenario.requester.email
            outgoing_1.context.tenant_id = tenant_id.get()
            response_1 = await deps.clients.audit_audit_event_validation.PreviewAuditEvent(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = forecasting_v1_demand_forecast_validation_service_pb2.NormalizeDemandForecastRequest(
                context=request.context,
                demand_forecast=forecasting_v1_forecasting_pb2.DemandForecast(
                    audit=common_v1_audit_pb2.AuditInfo(updated_at=request.scenario.audit.updated_at),
                    billing_address=common_v1_address_pb2.PostalAddress(region=request.details.destination.region)
                ),
                details=forecasting_v1_demand_forecast_validation_service_pb2.NormalizeDemandForecastRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(
                        email=request.scenario.requester.email,
                        preferred_channel=request.scenario.requester.preferred_channel
                    )
                )
            )
            port_2: ScenarioCalculationEstimateScenario2Port = ScenarioCalculationEstimateScenario2Adapter(
                deps.clients.forecasting_demand_forecast_validation,
                deps.settings.timeout
            )
            response_2 = await port_2.execute(outgoing_2)
            returned_0_0 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_0)
            returned_1_0 = response_1.audit_event.subject.display_name
            if returned_1_0:
                response.scenario.assignee.display_name = returned_1_0
            returned_2_0 = response_2.demand_forecast.audit.created_at
            returned_2_0_part_1 = response.scenario.comments.add()
            if returned_2_0.ListFields():
                returned_2_0_part_1.created_at.MergeFrom(returned_2_0)
            echoed_0 = request.scenario_id
            response.scenario.scenario_id = echoed_0
            echoed_1 = request.scenario.requester
            response.scenario.requester.CopyFrom(echoed_1)
            return response

    async def handle_explain_scenario_calculation(
        self,
        request: forecasting_v1_scenario_calculation_service_pb2.ExplainScenarioCalculationRequest
    ) -> forecasting_v1_scenario_calculation_service_pb2.ExplainScenarioCalculationResponse:
        """Explains a scenario."""
        deps = self.deps
        response = forecasting_v1_scenario_calculation_service_pb2.ExplainScenarioCalculationResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ExplainScenarioCalculation', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ExplainScenarioCalculation',
                {'reason': request.reason}
            )
            await deps.repository.save_scenario(request.context.tenant_id, request.scenario)
            response_0 = metrics_v1_dashboard_sync_service_pb2.PullDashboardsResponse()
            requests_0: list[metrics_v1_dashboard_sync_service_pb2.PullDashboardsRequest] = []
            for item_0 in request.scenario.comments:
                outgoing_0 = metrics_v1_dashboard_sync_service_pb2.PullDashboardsRequest(
                    context=request.context,
                    dashboard=metrics_v1_metrics_pb2.Dashboard(
                        audit=common_v1_audit_pb2.AuditInfo(
                            created_at=item_0.created_at,
                            updated_by=request.scenario.audit.updated_by
                        )
                    )
                )
                requests_0.append(outgoing_0)
            replies_0 = await asyncio.gather(*(
                deps.clients.metrics_dashboard_sync.PullDashboards(
                    entry,
                    timeout=deps.settings.timeout
                ) for entry in requests_0
            ))
            if replies_0:
                response_0 = replies_0[-1]
            echoed_0 = request.scenario_id
            response.scenario.scenario_id = echoed_0
            echoed_1 = request.scenario.priority
            response.scenario.priority = echoed_1
            return response

    async def handle_get_scenario_rates(
        self,
        request: forecasting_v1_scenario_calculation_service_pb2.GetScenarioRatesRequest
    ) -> forecasting_v1_scenario_calculation_service_pb2.GetScenarioRatesResponse:
        """Returns a scenario."""
        deps = self.deps
        response = forecasting_v1_scenario_calculation_service_pb2.GetScenarioRatesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('GetScenarioRates', extra={'fields': {'domain': 'forecasting'}})
            await deps.repository.audit(request.context.tenant_id, 'GetScenarioRates', {})
            response_0 = modelregistry_v1_registered_model_query_service_pb2.ResolveRegisteredModelsResponse()
            outgoing_0 = modelregistry_v1_registered_model_query_service_pb2.ResolveRegisteredModelsRequest(
                context=request.context
            )
            response_0 = await deps.clients.modelregistry_registered_model_query.ResolveRegisteredModels(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.details
            response.result.details.update(returned_0_0)
            returned_0_1 = response_0.result.message
            if returned_0_1:
                response.result.message = returned_0_1
            echoed_0 = request.scenario_id
            response.scenario.scenario_id = echoed_0
            return response

    async def handle_quote_scenario(
        self,
        request: forecasting_v1_scenario_calculation_service_pb2.QuoteScenarioRequest
    ) -> forecasting_v1_scenario_calculation_service_pb2.QuoteScenarioResponse:
        """Quotes a scenario."""
        deps = self.deps
        response = forecasting_v1_scenario_calculation_service_pb2.QuoteScenarioResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('QuoteScenario', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'QuoteScenario', {'reason': request.reason})
            await deps.repository.save_scenario(request.context.tenant_id, request.scenario)
            response_0 = appointments_v1_appointment_query_service_pb2.SuggestAppointmentsResponse()
            response_1 = labeling_v1_label_set_validation_service_pb2.NormalizeLabelSetResponse()
            outgoing_0 = appointments_v1_appointment_query_service_pb2.SuggestAppointmentsRequest(
                context=request.context,
                filter=appointments_v1_appointment_query_service_pb2.SuggestAppointmentsRequest.Filter(
                    created_after=request.scenario.audit.created_at,
                    region=request.details.destination.region
                )
            )
            response_0 = cast(appointments_v1_appointment_query_service_pb2.SuggestAppointmentsResponse, await deps.bus.request(
                'acme.forecasting.v1.ScenarioCalculationService/QuoteScenario/0', outgoing_0, deps.settings.timeout,
            ))
            outgoing_1 = labeling_v1_label_set_validation_service_pb2.NormalizeLabelSetRequest(
                context=request.context,
                label_set=labeling_v1_labeling_pb2.LabelSet(
                    children=[
                        labeling_v1_labeling_pb2.LabelSet(
                            children=[
                                labeling_v1_labeling_pb2.LabelSet(
                                    audit=common_v1_audit_pb2.AuditInfo(etag=request.scenario.audit.etag),
                                    manager=identity_v1_refs_pb2.UserRef(email=request.scenario.requester.email)
                                )
                            ],
                            location=common_v1_address_pb2.PostalAddress(lines=list(request.details.destination.lines))
                        )
                    ]
                )
            )
            response_1 = await deps.clients.labeling_label_set_validation.NormalizeLabelSet(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.result.message = returned_0_0
            returned_0_1 = response_0.result.details
            response.result.details.update(returned_0_1)
            returned_1_0 = response_1.label_set.audit.created_by
            if returned_1_0:
                response.scenario.audit.created_by = returned_1_0
            returned_1_1 = response_1.result.details
            response.result.details.update(returned_1_1)
            echoed_0 = request.scenario_id
            response.scenario.scenario_id = echoed_0
            echoed_1 = request.scenario.requester
            response.scenario.requester.CopyFrom(echoed_1)
            return response

    async def handle_recalculate_scenarios(
        self,
        request: forecasting_v1_scenario_calculation_service_pb2.RecalculateScenariosRequest
    ) -> forecasting_v1_scenario_calculation_service_pb2.RecalculateScenariosResponse:
        """Recalculates a scenario."""
        deps = self.deps
        response = forecasting_v1_scenario_calculation_service_pb2.RecalculateScenariosResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('RecalculateScenarios', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'RecalculateScenarios', {'reason': request.reason})
            await deps.repository.save_scenario(request.context.tenant_id, request.scenario)
            response_0 = labeling_v1_label_set_validation_service_pb2.PreviewLabelSetResponse()
            response_1 = metrics_v1_metric_series_notification_service_pb2.UnsubscribeMetricSeriesUpdatesResponse()
            outgoing_0 = labeling_v1_label_set_validation_service_pb2.PreviewLabelSetRequest(
                context=request.context,
                label_set=labeling_v1_labeling_pb2.LabelSet(
                    children=[
                        labeling_v1_labeling_pb2.LabelSet(
                            children=[
                                labeling_v1_labeling_pb2.LabelSet(
                                    audit=common_v1_audit_pb2.AuditInfo(
                                        created_by=request.scenario.audit.created_by,
                                        updated_at=request.scenario.audit.updated_at
                                    ),
                                    location=common_v1_address_pb2.PostalAddress(
                                        country_code=request.details.destination.country_code
                                    ),
                                    manager=identity_v1_refs_pb2.UserRef(
                                        display_name=request.scenario.assignee.display_name
                                    )
                                )
                            ]
                        )
                    ]
                )
            )
            method_name_0 = 'PreviewLabelSet'
            response_0 = await getattr(
                deps.clients.labeling_label_set_validation,
                method_name_0
            )(outgoing_0, timeout=deps.settings.timeout)
            callbacks_1: list[
                Callable[
                    [],
                    Awaitable[metrics_v1_metric_series_notification_service_pb2.UnsubscribeMetricSeriesUpdatesResponse]
                ]
            ] = []
            for item_1 in request.scenario.comments:
                outgoing_1 = metrics_v1_metric_series_notification_service_pb2.UnsubscribeMetricSeriesUpdatesRequest(
                    context=request.context,
                    details=metrics_v1_metric_series_notification_service_pb2.UnsubscribeMetricSeriesUpdatesRequest.Details(
                        recipient=common_v1_contact_pb2.ContactInfo(
                            email=item_1.author_email,
                            name=request.scenario.requester.name,
                            phone=request.scenario.requester.phone,
                            preferred_channel=request.scenario.requester.preferred_channel
                        )
                    )
                )
                async def send_1(
                    payload: metrics_v1_metric_series_notification_service_pb2.UnsubscribeMetricSeriesUpdatesRequest = outgoing_1
                ) -> metrics_v1_metric_series_notification_service_pb2.UnsubscribeMetricSeriesUpdatesResponse:
                    return await deps.clients.metrics_metric_series_notification.UnsubscribeMetricSeriesUpdates(
                        payload,
                        timeout=deps.settings.timeout
                    )
                callbacks_1.append(send_1)
            for callback_1 in callbacks_1:
                response_1 = await callback_1()
            returned_0_0 = response_0.outcome.status
            if returned_0_0:
                response.result.status = returned_0_0
            returned_0_1 = response_0.result.correlation_id
            if returned_0_1:
                response.result.correlation_id = returned_0_1
            echoed_0 = request.scenario_id
            response.scenario.scenario_id = echoed_0
            echoed_1 = request.scenario.priority
            response.scenario.priority = echoed_1
            return response

    async def handle_simulate_scenario(
        self,
        request: forecasting_v1_scenario_calculation_service_pb2.SimulateScenarioRequest
    ) -> forecasting_v1_scenario_calculation_service_pb2.SimulateScenarioResponse:
        """Simulates a scenario."""
        deps = self.deps
        response = forecasting_v1_scenario_calculation_service_pb2.SimulateScenarioResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SimulateScenario', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'SimulateScenario', {'reason': request.reason})
            await deps.repository.save_scenario(request.context.tenant_id, request.scenario)
            response_0 = metrics_v1_metric_series_validation_service_pb2.NormalizeMetricSeriesResponse()
            outgoing_0 = metrics_v1_metric_series_validation_service_pb2.NormalizeMetricSeriesRequest(
                context=request.context,
                metric_series=metrics_v1_metrics_pb2.MetricSeries(
                    address=common_v1_address_pb2.PostalAddress(recipient=request.details.destination.recipient)
                )
            )
            document_0 = MessageToDict(outgoing_0, preserving_proto_field_name=True)
            outgoing_0 = ParseDict(
                document_0,
                metrics_v1_metric_series_validation_service_pb2.NormalizeMetricSeriesRequest()
            )
            response_0 = await deps.clients.metrics_metric_series_validation.NormalizeMetricSeries(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.metric_series.audit.created_at
            if returned_0_0.ListFields():
                response.scenario.audit.created_at.MergeFrom(returned_0_0)
            returned_0_1 = response_0.metric_series.owner.email
            if returned_0_1:
                response.scenario.assignee.email = returned_0_1
            echoed_0 = request.scenario_id
            response.scenario.scenario_id = echoed_0
            echoed_1 = request.scenario.priority
            response.scenario.priority = echoed_1
            return response
