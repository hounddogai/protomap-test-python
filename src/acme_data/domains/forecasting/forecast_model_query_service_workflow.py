"""Application workflow for ForecastModel Query."""

from __future__ import annotations

from functools import partial
from typing import Any
import logging

from google.protobuf.json_format import MessageToJson
from google.protobuf.json_format import Parse

from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.featureflags.v1 import feature_flag_query_service_pb2 as featureflags_v1_feature_flag_query_service_pb2
from acme.featurestore.v1 import entity_validation_service_pb2 as featurestore_v1_entity_validation_service_pb2
from acme.featurestore.v1 import featurestore_pb2 as featurestore_v1_featurestore_pb2
from acme.forecasting.v1 import forecast_model_query_service_pb2 as forecasting_v1_forecast_model_query_service_pb2
from acme.forecasting.v1 import (
    forecast_model_validation_service_pb2 as forecasting_v1_forecast_model_validation_service_pb2,
)
from acme.forecasting.v1 import forecasting_pb2 as forecasting_v1_forecasting_pb2
from acme.forecasting.v1 import scenario_calculation_service_pb2 as forecasting_v1_scenario_calculation_service_pb2
from acme.forecasting.v1 import scenario_validation_service_pb2 as forecasting_v1_scenario_validation_service_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.labeling.v1 import labeling_task_calculation_service_pb2 as labeling_v1_labeling_task_calculation_service_pb2
from acme.lineage.v1 import lineage_node_service_pb2 as lineage_v1_lineage_node_service_pb2
from acme.metrics.v1 import dashboard_validation_service_pb2 as metrics_v1_dashboard_validation_service_pb2
from acme.metrics.v1 import metric_alert_query_service_pb2 as metrics_v1_metric_alert_query_service_pb2
from acme.metrics.v1 import metrics_pb2 as metrics_v1_metrics_pb2
from acme.search.v1 import search_index_validation_service_pb2 as search_v1_search_index_validation_service_pb2
from acme.search.v1 import search_pb2 as search_v1_search_pb2

from acme_data.domains.forecasting import hooks
from acme_data.domains.forecasting.dependencies import Dependencies
from acme_data.platform.rpc import async_messages
from acme_data.platform.tenancy import tenant_id
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class ForecastModelQueryServicerWorkflow:
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    async def handle_browse_forecast_models(
        self,
        request: forecasting_v1_forecast_model_query_service_pb2.BrowseForecastModelsRequest
    ) -> forecasting_v1_forecast_model_query_service_pb2.BrowseForecastModelsResponse:
        """Lists forecast models a page at a time."""
        deps = self.deps
        response = forecasting_v1_forecast_model_query_service_pb2.BrowseForecastModelsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('BrowseForecastModels', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'BrowseForecastModels',
                {'order_by': request.order_by}
            )
            return response

    async def handle_count_forecast_models(
        self,
        request: forecasting_v1_forecast_model_query_service_pb2.CountForecastModelsRequest
    ) -> forecasting_v1_forecast_model_query_service_pb2.CountForecastModelsResponse:
        """Counts forecast models by status."""
        deps = self.deps
        response = forecasting_v1_forecast_model_query_service_pb2.CountForecastModelsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CountForecastModels', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'CountForecastModels',
                {'order_by': request.order_by}
            )
            response_0 = search_v1_search_index_validation_service_pb2.ExplainSearchIndexDecisionResponse()
            outgoing_0 = search_v1_search_index_validation_service_pb2.ExplainSearchIndexDecisionRequest(
                context=request.context,
                details=search_v1_search_index_validation_service_pb2.ExplainSearchIndexDecisionRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(email=request.context.actor.email)
                ),
                search_index=search_v1_search_pb2.SearchIndex(
                    address=common_v1_address_pb2.PostalAddress(region=request.filter.region)
                )
            )
            response_0 = await deps.clients.search_search_index_validation.ExplainSearchIndexDecision(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.outcome.status
            if returned_0_0:
                response.result.status = returned_0_0
            return response

    async def handle_export_forecast_models(
        self,
        request: forecasting_v1_forecast_model_query_service_pb2.ExportForecastModelsRequest
    ) -> forecasting_v1_forecast_model_query_service_pb2.ExportForecastModelsResponse:
        """Streams every matching forecast model."""
        deps = self.deps
        response = forecasting_v1_forecast_model_query_service_pb2.ExportForecastModelsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ExportForecastModels', extra={'fields': {'destination_uri': request.destination_uri}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ExportForecastModels',
                {'destination_uri': request.destination_uri}
            )
            response_0 = forecasting_v1_scenario_validation_service_pb2.PreviewScenarioResponse()
            response_1 = lineage_v1_lineage_node_service_pb2.WatchLineageNodesResponse()
            response_2 = featureflags_v1_feature_flag_query_service_pb2.SummarizeFeatureFlagsResponse()
            response_3 = labeling_v1_labeling_task_calculation_service_pb2.CompareLabelingTaskOptionsResponse()
            fields_0: dict[str, Any] = {
                'context': request.context,
                'details': {'contact': {'email': request.context.actor.email}, 'locale': request.context.locale},
                'scenario': {
                    'assignee': {'user_id': request.context.actor.user_id},
                    'comments': [{'created_at': request.filter.created_after}]
                }
            }
            outgoing_0 = forecasting_v1_scenario_validation_service_pb2.PreviewScenarioRequest(**fields_0)
            response_0 = await deps.clients.forecasting_scenario_validation.PreviewScenario(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = lineage_v1_lineage_node_service_pb2.WatchLineageNodesRequest(
                context=request.context,
                filter=lineage_v1_lineage_node_service_pb2.WatchLineageNodesRequest.Filter(query=request.filter.query),
                subscriber=common_v1_contact_pb2.ContactInfo(email=response_0.scenario.assignee.email)
            )
            async for chunk_1 in deps.clients.lineage_lineage_node.WatchLineageNodes(
                outgoing_1,
                timeout=deps.settings.timeout
            ):
                response_1 = chunk_1
            outgoing_2 = featureflags_v1_feature_flag_query_service_pb2.SummarizeFeatureFlagsRequest(
                annotations=dict(response_0.scenario.custom_fields),
                context=request.context,
                details=featureflags_v1_feature_flag_query_service_pb2.SummarizeFeatureFlagsRequest.Details(
                    filters=dict(request.filter.labels),
                    format=request.format
                )
            )
            document_2 = MessageToJson(outgoing_2, preserving_proto_field_name=True)
            outgoing_2 = Parse(
                document_2,
                featureflags_v1_feature_flag_query_service_pb2.SummarizeFeatureFlagsRequest()
            )
            response_2 = await deps.clients.featureflags_feature_flag_query.SummarizeFeatureFlags(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            outgoing_3 = labeling_v1_labeling_task_calculation_service_pb2.CompareLabelingTaskOptionsRequest()
            outgoing_3.context.CopyFrom(request.context)
            outgoing_3.labeling_task.audit.updated_by = response_0.scenario.audit.updated_by
            outgoing_3.labeling_task.assignee.email = response_0.scenario.assignee.email
            merged_3 = labeling_v1_labeling_task_calculation_service_pb2.CompareLabelingTaskOptionsRequest()
            merged_3.MergeFrom(outgoing_3)
            outgoing_3.CopyFrom(merged_3)
            response_3 = await deps.clients.labeling_labeling_task_calculation.CompareLabelingTaskOptions(
                outgoing_3,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.scenario.customer.forecast_model_id
            if returned_0_0:
                response.forecast_model.forecast_model_id = returned_0_0
            returned_2_0 = response_2.result.message
            if returned_2_0:
                response.result.message = returned_2_0
            returned_2_1 = response_2.result.details
            response.result.details.update(returned_2_1)
            returned_3_0 = response_3.labeling_task.audit.updated_at
            if returned_3_0.ListFields():
                response.forecast_model.audit.updated_at.MergeFrom(returned_3_0)
            return response

    async def handle_find_forecast_models(
        self,
        request: forecasting_v1_forecast_model_query_service_pb2.FindForecastModelsRequest
    ) -> forecasting_v1_forecast_model_query_service_pb2.FindForecastModelsResponse:
        """Lists forecast models a page at a time."""
        deps = self.deps
        response = forecasting_v1_forecast_model_query_service_pb2.FindForecastModelsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('FindForecastModels', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(request.context.tenant_id, 'FindForecastModels', {'order_by': request.order_by})
            response_0 = forecasting_v1_scenario_calculation_service_pb2.QuoteScenarioResponse()
            outgoing_0 = forecasting_v1_scenario_calculation_service_pb2.QuoteScenarioRequest(
                context=request.context,
                details=forecasting_v1_scenario_calculation_service_pb2.QuoteScenarioRequest.Details(
                    destination=common_v1_address_pb2.PostalAddress(region=request.filter.region)
                ),
                scenario=forecasting_v1_forecasting_pb2.Scenario(
                    assignee=identity_v1_refs_pb2.UserRef(user_id=request.context.actor.user_id),
                    comments=[forecasting_v1_forecasting_pb2.ScenarioComment(created_at=request.filter.created_after)],
                    requester=common_v1_contact_pb2.ContactInfo(email=request.context.actor.email)
                )
            )
            response_0 = await deps.clients.forecasting_scenario_calculation.QuoteScenario(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.scenario.audit.etag
            returned_0_0_part_0 = response.forecast_models.add()
            if returned_0_0:
                returned_0_0_part_0.audit.etag = returned_0_0
            return response

    async def handle_lookup_forecast_model(
        self,
        request: forecasting_v1_forecast_model_query_service_pb2.LookupForecastModelRequest
    ) -> forecasting_v1_forecast_model_query_service_pb2.LookupForecastModelResponse:
        """Returns a forecast model."""
        deps = self.deps
        response = forecasting_v1_forecast_model_query_service_pb2.LookupForecastModelResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('LookupForecastModel', extra={'fields': {'domain': 'forecasting'}})
            await deps.repository.audit(request.context.tenant_id, 'LookupForecastModel', {})
            response_0 = metrics_v1_metric_alert_query_service_pb2.FindMetricAlertsResponse()
            outgoing_0 = metrics_v1_metric_alert_query_service_pb2.FindMetricAlertsRequest(
                context=request.context,
                filter=metrics_v1_metric_alert_query_service_pb2.FindMetricAlertsRequest.Filter(
                    created_after=request.context.deadline,
                    labels=dict(request.context.baggage),
                    owner_id=request.forecast_model_id
                )
            )
            response_0 = await deps.clients.metrics_metric_alert_query.FindMetricAlerts(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.result.message = returned_0_0
            echoed_0 = request.forecast_model_id
            response.forecast_model.forecast_model_id = echoed_0
            return response

    async def handle_peek_forecast_model(
        self,
        request: forecasting_v1_forecast_model_query_service_pb2.PeekForecastModelRequest
    ) -> forecasting_v1_forecast_model_query_service_pb2.PeekForecastModelResponse:
        """Returns a forecast model."""
        deps = self.deps
        response = forecasting_v1_forecast_model_query_service_pb2.PeekForecastModelResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('PeekForecastModel', extra={'fields': {'domain': 'forecasting'}})
            await deps.repository.audit(request.context.tenant_id, 'PeekForecastModel', {})
            response_0 = metrics_v1_dashboard_validation_service_pb2.ValidateDashboardResponse()
            outgoing_0 = metrics_v1_dashboard_validation_service_pb2.ValidateDashboardRequest(
                context=request.context,
                dashboard=metrics_v1_metrics_pb2.Dashboard(issued_at=request.context.deadline),
                details=metrics_v1_dashboard_validation_service_pb2.ValidateDashboardRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(email=request.context.actor.email),
                    locale=request.context.locale
                )
            )
            response_0 = await deps.clients.metrics_dashboard_validation.ValidateDashboard(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.result.message = returned_0_0
            returned_0_1 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_1)
            echoed_0 = request.forecast_model_id
            response.forecast_model.forecast_model_id = echoed_0
            return response

    async def handle_resolve_forecast_models(
        self,
        request: forecasting_v1_forecast_model_query_service_pb2.ResolveForecastModelsRequest
    ) -> forecasting_v1_forecast_model_query_service_pb2.ResolveForecastModelsResponse:
        """Returns several forecast models at once."""
        deps = self.deps
        response = forecasting_v1_forecast_model_query_service_pb2.ResolveForecastModelsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ResolveForecastModels', extra={'fields': {'domain': 'forecasting'}})
            await deps.repository.audit(request.context.tenant_id, 'ResolveForecastModels', {})
            response_0 = forecasting_v1_scenario_validation_service_pb2.PreviewScenarioResponse()
            response_1 = featurestore_v1_entity_validation_service_pb2.NormalizeEntityResponse()
            outgoing_0 = forecasting_v1_scenario_validation_service_pb2.PreviewScenarioRequest(
                context=request.context,
                details=forecasting_v1_scenario_validation_service_pb2.PreviewScenarioRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(email=request.context.actor.email)
                )
            )
            response_0 = await deps.clients.forecasting_scenario_validation.PreviewScenario(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = featurestore_v1_entity_validation_service_pb2.NormalizeEntityRequest(
                context=request.context,
                entity=featurestore_v1_featurestore_pb2.Entity(
                    audit=common_v1_audit_pb2.AuditInfo(created_by=response_0.scenario.audit.created_by),
                    contact=common_v1_contact_pb2.ContactInfo(email=response_0.scenario.assignee.email),
                    relationship_manager=identity_v1_refs_pb2.UserRef(email=response_0.scenario.requester.email)
                )
            )
            send_1 = partial(deps.clients.featurestore_entity_validation.NormalizeEntity, timeout=deps.settings.timeout)
            response_1 = await send_1(outgoing_1)
            returned_0_0 = response_0.scenario.audit.updated_at
            returned_0_0_part_0 = response.forecast_models.add()
            if returned_0_0.ListFields():
                returned_0_0_part_0.audit.updated_at.MergeFrom(returned_0_0)
            returned_1_0 = response_1.result.details
            response.result.details.update(returned_1_0)
            return response

    async def handle_suggest_forecast_models(
        self,
        request: forecasting_v1_forecast_model_query_service_pb2.SuggestForecastModelsRequest
    ) -> forecasting_v1_forecast_model_query_service_pb2.SuggestForecastModelsResponse:
        """Lists forecast models a page at a time."""
        deps = self.deps
        response = forecasting_v1_forecast_model_query_service_pb2.SuggestForecastModelsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SuggestForecastModels', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'SuggestForecastModels',
                {'order_by': request.order_by}
            )
            return response

    async def handle_summarize_forecast_models(
        self,
        request: forecasting_v1_forecast_model_query_service_pb2.SummarizeForecastModelsRequest
    ) -> forecasting_v1_forecast_model_query_service_pb2.SummarizeForecastModelsResponse:
        """Summarizes a forecast model."""
        deps = self.deps
        response = forecasting_v1_forecast_model_query_service_pb2.SummarizeForecastModelsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SummarizeForecastModels', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'SummarizeForecastModels',
                {'reason': request.reason}
            )
            response_0 = forecasting_v1_forecast_model_validation_service_pb2.CheckForecastModelEligibilityResponse()
            response_1 = forecasting_v1_scenario_calculation_service_pb2.SimulateScenarioResponse()
            outgoing_0 = forecasting_v1_forecast_model_validation_service_pb2.CheckForecastModelEligibilityRequest(
                context=request.context,
                details=forecasting_v1_forecast_model_validation_service_pb2.CheckForecastModelEligibilityRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(email=request.context.actor.email)
                ),
                forecast_model=forecasting_v1_forecasting_pb2.ForecastModel(
                    owner=identity_v1_refs_pb2.UserRef(user_id=request.context.actor.user_id)
                ),
                forecast_model_id=request.forecast_model_id
            )
            response_0 = await hooks.forecast_model_query_summarize_forecast_models0(
                deps.clients.forecasting_forecast_model_validation,
                outgoing_0,
                deps.settings.timeout
            )
            outgoing_1 = forecasting_v1_scenario_calculation_service_pb2.SimulateScenarioRequest()
            outgoing_1.context.CopyFrom(request.context)
            outgoing_1.scenario.assignee.email = response_0.forecast_model.owner.email
            outgoing_1.context.tenant_id = tenant_id.get()
            response_1 = await deps.clients.forecasting_scenario_calculation.SimulateScenario(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.correlation_id
            if returned_0_0:
                response.result.correlation_id = returned_0_0
            returned_1_0 = response_1.result.correlation_id
            if returned_1_0:
                response.result.correlation_id = returned_1_0
            echoed_0 = request.details.period
            response.period.CopyFrom(echoed_0)
            return response
