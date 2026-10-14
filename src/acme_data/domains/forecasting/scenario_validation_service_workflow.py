"""Application workflow for Scenario Validation."""

from __future__ import annotations

from collections.abc import Awaitable
from collections.abc import Callable
from functools import partial
from typing import Any
from typing import cast
import asyncio
import logging

from google.protobuf.any_pb2 import Any as AnyMessage
from google.protobuf.json_format import MessageToJson
from google.protobuf.json_format import Parse

from acme.anomalies.v1 import (
    anomaly_feedback_calculation_service_pb2 as anomalies_v1_anomaly_feedback_calculation_service_pb2,
)
from acme.appointments.v1 import appointment_query_service_pb2 as appointments_v1_appointment_query_service_pb2
from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.featurestore.v1 import entity_validation_service_pb2 as featurestore_v1_entity_validation_service_pb2
from acme.featurestore.v1 import featurestore_pb2 as featurestore_v1_featurestore_pb2
from acme.forecasting.v1 import (
    demand_forecast_validation_service_pb2 as forecasting_v1_demand_forecast_validation_service_pb2,
)
from acme.forecasting.v1 import (
    forecast_model_validation_service_pb2 as forecasting_v1_forecast_model_validation_service_pb2,
)
from acme.forecasting.v1 import forecasting_pb2 as forecasting_v1_forecasting_pb2
from acme.forecasting.v1 import refs_pb2 as forecasting_v1_refs_pb2
from acme.forecasting.v1 import scenario_calculation_service_pb2 as forecasting_v1_scenario_calculation_service_pb2
from acme.forecasting.v1 import scenario_validation_service_pb2 as forecasting_v1_scenario_validation_service_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.identity.v1 import user_service_pb2 as identity_v1_user_service_pb2
from acme.metrics.v1 import dashboard_validation_service_pb2 as metrics_v1_dashboard_validation_service_pb2
from acme.metrics.v1 import metrics_pb2 as metrics_v1_metrics_pb2
from acme.modelregistry.v1 import (
    deployment_validation_service_pb2 as modelregistry_v1_deployment_validation_service_pb2,
)
from acme.modelregistry.v1 import modelregistry_pb2 as modelregistry_v1_modelregistry_pb2
from acme.notifications.v1 import notification_service_pb2 as notifications_v1_notification_service_pb2
from acme.pipelines.v1 import (
    pipeline_step_calculation_service_pb2 as pipelines_v1_pipeline_step_calculation_service_pb2,
)
from acme.pipelines.v1 import pipelines_pb2 as pipelines_v1_pipelines_pb2
from acme.search.v1 import search_index_service_pb2 as search_v1_search_index_service_pb2
from acme.search.v1 import search_index_service_pb2_grpc as search_v1_search_index_service_pb2_grpc
from acme.search.v1 import search_index_validation_service_pb2 as search_v1_search_index_validation_service_pb2
from acme.search.v1 import search_pb2 as search_v1_search_pb2
from acme.venues.v1 import venue_validation_service_pb2 as venues_v1_venue_validation_service_pb2
from acme.venues.v1 import venues_pb2 as venues_v1_venues_pb2

from acme_data.domains.forecasting import hooks
from acme_data.domains.forecasting.adapters import ScenarioValidationNormalizeScenario2Adapter
from acme_data.domains.forecasting.adapters import ScenarioValidationNormalizeScenario2Port
from acme_data.domains.forecasting.dependencies import Dependencies
from acme_data.domains.forecasting.models import ScenarioValidationExplainScenarioDecision1Command
from acme_data.domains.forecasting.models import to_scenario_validation_explain_scenario_decision1_command
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import run_steps
from acme_data.platform.tenancy import tenant_id
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class ScenarioValidationServicerWorkflow:
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    async def handle_check_scenario_eligibility(
        self,
        request: forecasting_v1_scenario_validation_service_pb2.CheckScenarioEligibilityRequest
    ) -> forecasting_v1_scenario_validation_service_pb2.CheckScenarioEligibilityResponse:
        """Checks a scenario."""
        deps = self.deps
        response = forecasting_v1_scenario_validation_service_pb2.CheckScenarioEligibilityResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CheckScenarioEligibility', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'CheckScenarioEligibility',
                {'reason': request.reason}
            )
            await deps.repository.save_scenario(request.context.tenant_id, request.scenario)
            response_0 = appointments_v1_appointment_query_service_pb2.BrowseAppointmentsResponse()
            response_1 = identity_v1_user_service_pb2.GetUserResponse()
            response_2 = forecasting_v1_forecast_model_validation_service_pb2.PreviewForecastModelResponse()
            outgoing_0 = appointments_v1_appointment_query_service_pb2.BrowseAppointmentsRequest(
                context=request.context,
                filter=appointments_v1_appointment_query_service_pb2.BrowseAppointmentsRequest.Filter(
                    created_after=request.scenario.audit.created_at,
                    labels=dict(request.annotations),
                    owner_id=request.scenario.customer.forecast_model_id
                )
            )
            document_0 = MessageToJson(outgoing_0, preserving_proto_field_name=True)
            outgoing_0 = Parse(document_0, appointments_v1_appointment_query_service_pb2.BrowseAppointmentsRequest())
            response_0 = await deps.clients.appointments_appointment_query.BrowseAppointments(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = identity_v1_user_service_pb2.GetUserRequest()
            outgoing_1.context.CopyFrom(request.context)
            outgoing_1.user_id = request.scenario.assignee.user_id
            merged_1 = identity_v1_user_service_pb2.GetUserRequest()
            merged_1.MergeFrom(outgoing_1)
            outgoing_1.CopyFrom(merged_1)
            response_1 = await deps.clients.identity_user.GetUser(outgoing_1, timeout=deps.settings.timeout)
            outgoing_2 = forecasting_v1_forecast_model_validation_service_pb2.PreviewForecastModelRequest(
                context=request.context,
                forecast_model=forecasting_v1_forecasting_pb2.ForecastModel(
                    address=common_v1_address_pb2.PostalAddress(
                        postal_code=response_1.user.primary_address.postal_code
                    ),
                    audit=common_v1_audit_pb2.AuditInfo(created_by=response_1.user.audit.created_by),
                    owner=identity_v1_refs_pb2.UserRef(display_name=request.scenario.assignee.display_name)
                )
            )
            envelope_2 = AnyMessage()
            envelope_2.Pack(outgoing_2)
            outgoing_2 = forecasting_v1_forecast_model_validation_service_pb2.PreviewForecastModelRequest()
            if not envelope_2.Unpack(outgoing_2):
                raise ValueError("partner envelope contains the wrong request type")
            response_2 = await deps.clients.forecasting_forecast_model_validation.PreviewForecastModel(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.status
            if returned_0_0:
                response.outcome.status = returned_0_0
            returned_0_1 = response_0.result.status
            if returned_0_1:
                response.result.status = returned_0_1
            returned_1_0 = response_1.user.audit.created_at
            returned_1_0_part_1 = response.scenario.comments.add()
            if returned_1_0.ListFields():
                returned_1_0_part_1.created_at.MergeFrom(returned_1_0)
            returned_2_0 = response_2.outcome.status
            if returned_2_0:
                response.result.status = returned_2_0
            returned_2_1 = response_2.forecast_model.audit.updated_by
            if returned_2_1:
                response.scenario.audit.updated_by = returned_2_1
            echoed_0 = request.scenario_id
            response.scenario.scenario_id = echoed_0
            echoed_1 = request.scenario.custom_fields
            response.scenario.custom_fields.update(echoed_1)
            return response

    async def handle_explain_scenario_decision(
        self,
        request: forecasting_v1_scenario_validation_service_pb2.ExplainScenarioDecisionRequest
    ) -> forecasting_v1_scenario_validation_service_pb2.ExplainScenarioDecisionResponse:
        """Explains a scenario."""
        deps = self.deps
        response = forecasting_v1_scenario_validation_service_pb2.ExplainScenarioDecisionResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ExplainScenarioDecision', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ExplainScenarioDecision',
                {'reason': request.reason}
            )
            await deps.repository.save_scenario(request.context.tenant_id, request.scenario)
            response_0 = search_v1_search_index_service_pb2.UpdateSearchIndexResponse()
            response_1 = forecasting_v1_demand_forecast_validation_service_pb2.PreviewDemandForecastResponse()
            outgoing_0 = search_v1_search_index_service_pb2.UpdateSearchIndexRequest(
                context=request.context,
                search_index=search_v1_search_pb2.SearchIndex(
                    owner=identity_v1_refs_pb2.UserRef(email=request.scenario.assignee.email)
                )
            )
            registered_0 = cast(
                search_v1_search_index_service_pb2_grpc.SearchIndexServiceStub,
                deps.clients.registry['acme.search.v1.SearchIndexService']
            )
            response_0 = await registered_0.UpdateSearchIndex(outgoing_0, timeout=deps.settings.timeout)
            command_1 = ScenarioValidationExplainScenarioDecision1Command(
                context=request.context,
                details_contact_email=request.scenario.assignee.email,
                demand_forecast_counterparty_display_name=response_0.search_index.owner.display_name,
                demand_forecast_lines_quantity=response_0.search_index.components.get(
                    'primary',
                    search_v1_search_pb2.SearchIndexComponent()
                ).quantity
            )
            outgoing_1 = to_scenario_validation_explain_scenario_decision1_command(command_1)
            response_1 = await deps.clients.forecasting_demand_forecast_validation.PreviewDemandForecast(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.search_index.owner.email
            if returned_0_0:
                response.scenario.assignee.email = returned_0_0
            returned_0_1 = response_0.result.message
            if returned_0_1:
                response.result.message = returned_0_1
            returned_1_0 = response_1.result.status
            if returned_1_0:
                response.result.status = returned_1_0
            returned_1_1 = response_1.outcome.next_steps
            response.outcome.next_steps.extend(returned_1_1)
            echoed_0 = request.scenario_id
            response.scenario.scenario_id = echoed_0
            echoed_1 = request.scenario.priority
            response.scenario.priority = echoed_1
            return response

    async def handle_get_scenario_rules(
        self,
        request: forecasting_v1_scenario_validation_service_pb2.GetScenarioRulesRequest
    ) -> forecasting_v1_scenario_validation_service_pb2.GetScenarioRulesResponse:
        """Returns a scenario."""
        deps = self.deps
        response = forecasting_v1_scenario_validation_service_pb2.GetScenarioRulesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('GetScenarioRules', extra={'fields': {'domain': 'forecasting'}})
            await deps.repository.audit(request.context.tenant_id, 'GetScenarioRules', {})
            response_0 = forecasting_v1_demand_forecast_validation_service_pb2.NormalizeDemandForecastResponse()
            outgoing_0 = forecasting_v1_demand_forecast_validation_service_pb2.NormalizeDemandForecastRequest(
                context=request.context,
                demand_forecast=forecasting_v1_forecasting_pb2.DemandForecast(
                    counterparty=forecasting_v1_refs_pb2.ScenarioRef(scenario_id=request.scenario_id)
                ),
                details=forecasting_v1_demand_forecast_validation_service_pb2.NormalizeDemandForecastRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(email=request.context.actor.email),
                    locale=request.context.locale
                )
            )
            response_0 = await deps.clients.forecasting_demand_forecast_validation.NormalizeDemandForecast(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.demand_forecast.counterparty.display_name
            if returned_0_0:
                response.scenario.assignee.display_name = returned_0_0
            returned_0_1 = response_0.demand_forecast.audit.updated_at
            if returned_0_1.ListFields():
                response.scenario.audit.updated_at.MergeFrom(returned_0_1)
            echoed_0 = request.scenario_id
            response.scenario.scenario_id = echoed_0
            return response

    async def handle_lint_scenarios(
        self,
        request: forecasting_v1_scenario_validation_service_pb2.LintScenariosRequest
    ) -> forecasting_v1_scenario_validation_service_pb2.LintScenariosResponse:
        """Lints a scenario."""
        deps = self.deps
        response = forecasting_v1_scenario_validation_service_pb2.LintScenariosResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('LintScenarios', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'LintScenarios', {'reason': request.reason})
            await deps.repository.save_scenario(request.context.tenant_id, request.scenario)
            response_0 = forecasting_v1_scenario_calculation_service_pb2.CompareScenarioOptionsResponse()
            async for item_0 in async_messages(request.scenario.comments):
                outgoing_0 = forecasting_v1_scenario_calculation_service_pb2.CompareScenarioOptionsRequest(
                    context=request.context,
                    scenario=forecasting_v1_forecasting_pb2.Scenario(
                        comments=[
                            forecasting_v1_forecasting_pb2.ScenarioComment(
                                body=item_0.body,
                                comment_id=item_0.comment_id,
                                created_at=item_0.created_at
                            )
                        ],
                        requester=common_v1_contact_pb2.ContactInfo(email=item_0.author_email)
                    )
                )
                response_0 = await deps.clients.forecasting_scenario_calculation.CompareScenarioOptions(
                    outgoing_0,
                    timeout=deps.settings.timeout
                )
            echoed_0 = request.scenario_id
            response.scenario.scenario_id = echoed_0
            echoed_1 = request.scenario.custom_fields
            response.scenario.custom_fields.update(echoed_1)
            return response

    async def handle_normalize_scenario(
        self,
        request: forecasting_v1_scenario_validation_service_pb2.NormalizeScenarioRequest
    ) -> forecasting_v1_scenario_validation_service_pb2.NormalizeScenarioResponse:
        """Normalizes a scenario."""
        deps = self.deps
        response = forecasting_v1_scenario_validation_service_pb2.NormalizeScenarioResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('NormalizeScenario', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'NormalizeScenario', {'reason': request.reason})
            await deps.repository.save_scenario(request.context.tenant_id, request.scenario)
            response_0 = venues_v1_venue_validation_service_pb2.LintVenuesResponse()
            response_1 = forecasting_v1_forecast_model_validation_service_pb2.ValidateForecastModelResponse()
            response_2 = metrics_v1_dashboard_validation_service_pb2.ValidateDashboardResponse()
            outgoing_0 = venues_v1_venue_validation_service_pb2.LintVenuesRequest(
                context=request.context,
                details=venues_v1_venue_validation_service_pb2.LintVenuesRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(email=request.scenario.requester.email)
                ),
                venue=venues_v1_venues_pb2.Venue(
                    owner=identity_v1_refs_pb2.UserRef(user_id=request.scenario.assignee.user_id)
                )
            )
            response_0 = await hooks.scenario_validation_normalize_scenario0(
                deps.clients.venues_venue_validation,
                outgoing_0,
                deps.settings.timeout
            )
            outgoing_1 = forecasting_v1_forecast_model_validation_service_pb2.ValidateForecastModelRequest()
            outgoing_1.context.CopyFrom(request.context)
            outgoing_1.forecast_model.components['primary'].quantity = response_0.venue.components.get(
                'primary',
                venues_v1_venues_pb2.VenueComponent()
            ).quantity
            outgoing_1.forecast_model.address.country_code = response_0.venue.address.country_code
            outgoing_1.context.tenant_id = tenant_id.get()
            response_1 = await deps.clients.forecasting_forecast_model_validation.ValidateForecastModel(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = metrics_v1_dashboard_validation_service_pb2.ValidateDashboardRequest(
                context=request.context,
                dashboard=metrics_v1_metrics_pb2.Dashboard(
                    billing_address=common_v1_address_pb2.PostalAddress(recipient=response_0.venue.address.recipient),
                    lines=[
                        metrics_v1_metrics_pb2.DashboardLine(
                            quantity=response_1.forecast_model.components.get(
                                'primary',
                                forecasting_v1_forecasting_pb2.ForecastModelComponent()
                            ).quantity
                        )
                    ]
                )
            )
            port_2: ScenarioValidationNormalizeScenario2Port = ScenarioValidationNormalizeScenario2Adapter(
                deps.clients.metrics_dashboard_validation,
                deps.settings.timeout
            )
            response_2 = await port_2.execute(outgoing_2)
            returned_0_0 = response_0.outcome.status
            if returned_0_0:
                response.result.status = returned_0_0
            returned_0_1 = response_0.outcome.status
            if returned_0_1:
                response.outcome.status = returned_0_1
            returned_1_0 = response_1.forecast_model.audit.created_at
            returned_1_0_part_1 = response.scenario.comments.add()
            if returned_1_0.ListFields():
                returned_1_0_part_1.created_at.MergeFrom(returned_1_0)
            returned_1_1 = response_1.result.details
            response.result.details.update(returned_1_1)
            returned_2_0 = response_2.dashboard.counterparty.display_name
            if returned_2_0:
                response.scenario.assignee.display_name = returned_2_0
            returned_2_1 = response_2.dashboard.audit.created_at
            if returned_2_1.ListFields():
                response.scenario.audit.created_at.MergeFrom(returned_2_1)
            echoed_0 = request.scenario_id
            response.scenario.scenario_id = echoed_0
            echoed_1 = request.scenario.status
            response.scenario.status = echoed_1
            return response

    async def handle_preview_scenario(
        self,
        request: forecasting_v1_scenario_validation_service_pb2.PreviewScenarioRequest
    ) -> forecasting_v1_scenario_validation_service_pb2.PreviewScenarioResponse:
        """Previews a scenario."""
        deps = self.deps
        response = forecasting_v1_scenario_validation_service_pb2.PreviewScenarioResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('PreviewScenario', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'PreviewScenario', {'reason': request.reason})
            await deps.repository.save_scenario(request.context.tenant_id, request.scenario)
            response_0 = search_v1_search_index_validation_service_pb2.PreviewSearchIndexResponse()
            response_1 = modelregistry_v1_deployment_validation_service_pb2.ValidateDeploymentResponse()
            response_2 = pipelines_v1_pipeline_step_calculation_service_pb2.EstimatePipelineStepResponse()
            outgoing_0 = search_v1_search_index_validation_service_pb2.PreviewSearchIndexRequest(
                context=request.context,
                details=search_v1_search_index_validation_service_pb2.PreviewSearchIndexRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(name=request.details.contact.name)
                )
            )
            steps_0 = [
                partial(
                    deps.clients.search_search_index_validation.PreviewSearchIndex,
                    outgoing_0,
                    timeout=deps.settings.timeout
                )
            ]
            results_0 = await run_steps(steps_0)
            response_0 = results_0[-1]
            for item_1 in request.scenario.comments:
                outgoing_1 = modelregistry_v1_deployment_validation_service_pb2.ValidateDeploymentRequest(
                    context=request.context,
                    deployment=modelregistry_v1_modelregistry_pb2.Deployment(
                        audit=common_v1_audit_pb2.AuditInfo(created_at=item_1.created_at)
                    )
                )
                response_1 = await deps.clients.modelregistry_deployment_validation.ValidateDeployment(
                    outgoing_1,
                    timeout=deps.settings.timeout
                )
            outgoing_2 = pipelines_v1_pipeline_step_calculation_service_pb2.EstimatePipelineStepRequest(
                context=request.context,
                details=pipelines_v1_pipeline_step_calculation_service_pb2.EstimatePipelineStepRequest.Details(
                    destination=common_v1_address_pb2.PostalAddress(recipient=response_1.deployment.location.recipient)
                ),
                pipeline_step=pipelines_v1_pipelines_pb2.PipelineStep(
                    audit=common_v1_audit_pb2.AuditInfo(created_at=request.scenario.audit.created_at),
                    owner=identity_v1_refs_pb2.UserRef(email=request.scenario.assignee.email)
                )
            )
            response_2 = cast(pipelines_v1_pipeline_step_calculation_service_pb2.EstimatePipelineStepResponse, await deps.bus.request(
                'acme.forecasting.v1.ScenarioValidationService/PreviewScenario/2', outgoing_2, deps.settings.timeout,
            ))
            returned_0_0 = response_0.outcome.next_steps
            response.outcome.next_steps.extend(returned_0_0)
            returned_0_1 = response_0.search_index.audit.created_at
            if returned_0_1.ListFields():
                response.scenario.audit.created_at.MergeFrom(returned_0_1)
            returned_2_0 = response_2.pipeline_step.owner.email
            if returned_2_0:
                response.scenario.assignee.email = returned_2_0
            echoed_0 = request.scenario_id
            response.scenario.scenario_id = echoed_0
            echoed_1 = request.scenario.custom_fields
            response.scenario.custom_fields.update(echoed_1)
            return response

    async def handle_score_scenario(
        self,
        request: forecasting_v1_scenario_validation_service_pb2.ScoreScenarioRequest
    ) -> forecasting_v1_scenario_validation_service_pb2.ScoreScenarioResponse:
        """Scores a scenario."""
        deps = self.deps
        response = forecasting_v1_scenario_validation_service_pb2.ScoreScenarioResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ScoreScenario', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'ScoreScenario', {'reason': request.reason})
            await deps.repository.save_scenario(request.context.tenant_id, request.scenario)
            response_0 = featurestore_v1_entity_validation_service_pb2.ExplainEntityDecisionResponse()
            response_1 = forecasting_v1_demand_forecast_validation_service_pb2.ExplainDemandForecastDecisionResponse()
            response_2 = forecasting_v1_scenario_calculation_service_pb2.GetScenarioRatesResponse()
            response_3 = notifications_v1_notification_service_pb2.CreateNotificationResponse()
            requests_0: list[featurestore_v1_entity_validation_service_pb2.ExplainEntityDecisionRequest] = []
            for item_0 in request.scenario.comments:
                outgoing_0 = featurestore_v1_entity_validation_service_pb2.ExplainEntityDecisionRequest(
                    context=request.context,
                    details=featurestore_v1_entity_validation_service_pb2.ExplainEntityDecisionRequest.Details(
                        contact=common_v1_contact_pb2.ContactInfo(email=item_0.author_email)
                    ),
                    entity=featurestore_v1_featurestore_pb2.Entity(
                        audit=common_v1_audit_pb2.AuditInfo(created_at=item_0.created_at)
                    )
                )
                requests_0.append(outgoing_0)
            replies_0 = await asyncio.gather(*(
                deps.clients.featurestore_entity_validation.ExplainEntityDecision(
                    entry,
                    timeout=deps.settings.timeout
                ) for entry in requests_0
            ))
            if replies_0:
                response_0 = replies_0[-1]
            outgoing_1 = forecasting_v1_demand_forecast_validation_service_pb2.ExplainDemandForecastDecisionRequest(
                context=request.context,
                demand_forecast=forecasting_v1_forecasting_pb2.DemandForecast(
                    audit=common_v1_audit_pb2.AuditInfo(created_at=request.scenario.audit.created_at),
                    billing_address=common_v1_address_pb2.PostalAddress(
                        recipient=response_0.entity.primary_address.recipient
                    ),
                    counterparty=forecasting_v1_refs_pb2.ScenarioRef(
                        display_name=response_0.entity.relationship_manager.display_name
                    )
                ),
                details=forecasting_v1_demand_forecast_validation_service_pb2.ExplainDemandForecastDecisionRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(email=request.scenario.assignee.email)
                )
            )
            method_name_1 = 'ExplainDemandForecastDecision'
            response_1 = await getattr(
                deps.clients.forecasting_demand_forecast_validation,
                method_name_1
            )(outgoing_1, timeout=deps.settings.timeout)
            fields_2: dict[str, Any] = {'context': request.context, 'scenario_id': request.scenario.scenario_id}
            outgoing_2 = forecasting_v1_scenario_calculation_service_pb2.GetScenarioRatesRequest(**fields_2)
            response_2 = await deps.clients.forecasting_scenario_calculation.GetScenarioRates(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            outgoing_3 = notifications_v1_notification_service_pb2.CreateNotificationRequest()
            outgoing_3.context.CopyFrom(request.context)
            if request.scenario.WhichOneof('origin') == 'channel':
                outgoing_3.notification.channel.channel = request.scenario.channel.channel
            outgoing_3.notification.requester.phone = response_2.scenario.requester.phone
            outgoing_3.notification.audit.updated_at.CopyFrom(response_0.entity.audit.updated_at)
            response_3 = await deps.clients.notifications_notification.CreateNotification(
                outgoing_3,
                timeout=deps.settings.timeout
            )
            returned_1_0 = response_1.demand_forecast.due_at
            if returned_1_0.ListFields():
                response.scenario.sla.due_at.MergeFrom(returned_1_0)
            returned_2_0 = response_2.scenario.sla.due_at
            if returned_2_0.ListFields():
                response.scenario.sla.due_at.MergeFrom(returned_2_0)
            returned_2_1 = response_2.scenario.custom_fields
            response.scenario.custom_fields.update(returned_2_1)
            returned_3_0 = response_3.notification.customer.display_name
            if returned_3_0:
                response.scenario.assignee.display_name = returned_3_0
            echoed_0 = request.scenario_id
            response.scenario.scenario_id = echoed_0
            echoed_1 = request.scenario.requester
            response.scenario.requester.CopyFrom(echoed_1)
            return response

    async def handle_validate_scenario(
        self,
        request: forecasting_v1_scenario_validation_service_pb2.ValidateScenarioRequest
    ) -> forecasting_v1_scenario_validation_service_pb2.ValidateScenarioResponse:
        """Validates a scenario."""
        deps = self.deps
        response = forecasting_v1_scenario_validation_service_pb2.ValidateScenarioResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ValidateScenario', extra={'fields': {'locale': request.details.locale}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ValidateScenario',
                {'locale': request.details.locale}
            )
            await deps.repository.save_scenario(request.context.tenant_id, request.scenario)
            response_0 = forecasting_v1_scenario_calculation_service_pb2.QuoteScenarioResponse()
            response_1 = anomalies_v1_anomaly_feedback_calculation_service_pb2.QuoteAnomalyFeedbackResponse()
            outgoing_0 = forecasting_v1_scenario_calculation_service_pb2.QuoteScenarioRequest(
                context=request.context,
                scenario=forecasting_v1_forecasting_pb2.Scenario(
                    audit=common_v1_audit_pb2.AuditInfo(updated_by=request.scenario.audit.updated_by),
                    requester=common_v1_contact_pb2.ContactInfo(
                        preferred_channel=request.details.contact.preferred_channel
                    )
                )
            )
            document_0 = MessageToJson(outgoing_0, preserving_proto_field_name=True)
            outgoing_0 = Parse(document_0, forecasting_v1_scenario_calculation_service_pb2.QuoteScenarioRequest())
            response_0 = await deps.clients.forecasting_scenario_calculation.QuoteScenario(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = anomalies_v1_anomaly_feedback_calculation_service_pb2.QuoteAnomalyFeedbackRequest()
            outgoing_1.context.CopyFrom(request.context)
            outgoing_1.anomaly_feedback.subject.display_name = response_0.scenario.assignee.display_name
            outgoing_1.anomaly_feedback.subject.code = response_0.scenario.customer.code
            outgoing_1.reason = request.reason
            outgoing_1.details.currency_code = response_0.breakdown.currency_code
            merged_1 = anomalies_v1_anomaly_feedback_calculation_service_pb2.QuoteAnomalyFeedbackRequest()
            merged_1.MergeFrom(outgoing_1)
            outgoing_1.CopyFrom(merged_1)
            response_1 = await deps.clients.anomalies_anomaly_feedback_calculation.QuoteAnomalyFeedback(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.scenario.sla.paused_for
            if returned_0_0.ListFields():
                response.scenario.sla.paused_for.MergeFrom(returned_0_0)
            returned_1_0 = response_1.result.message
            if returned_1_0:
                response.outcome.message = returned_1_0
            returned_1_1 = response_1.result.message
            if returned_1_1:
                response.result.message = returned_1_1
            echoed_0 = request.scenario_id
            response.scenario.scenario_id = echoed_0
            echoed_1 = request.scenario.requester
            response.scenario.requester.CopyFrom(echoed_1)
            return response
