"""Functional operations behind DemandForecastService."""

from __future__ import annotations

from functools import partial
from typing import Any
from typing import cast
import logging

from acme.anomalies.v1 import anomaly_query_service_pb2 as anomalies_v1_anomaly_query_service_pb2
from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.datasets.v1 import dataset_service_pb2 as datasets_v1_dataset_service_pb2
from acme.datasets.v1 import datasets_pb2 as datasets_v1_datasets_pb2
from acme.documents.v1 import document_query_service_pb2 as documents_v1_document_query_service_pb2
from acme.documents.v1 import document_service_pb2 as documents_v1_document_service_pb2
from acme.documents.v1 import documents_pb2 as documents_v1_documents_pb2
from acme.forecasting.v1 import demand_forecast_query_service_pb2 as forecasting_v1_demand_forecast_query_service_pb2
from acme.forecasting.v1 import demand_forecast_service_pb2 as forecasting_v1_demand_forecast_service_pb2
from acme.forecasting.v1 import forecast_model_query_service_pb2 as forecasting_v1_forecast_model_query_service_pb2
from acme.forecasting.v1 import (
    forecast_model_validation_service_pb2 as forecasting_v1_forecast_model_validation_service_pb2,
)
from acme.forecasting.v1 import forecasting_pb2 as forecasting_v1_forecasting_pb2
from acme.identity.v1 import identity_pb2 as identity_v1_identity_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.identity.v1 import user_validation_service_pb2 as identity_v1_user_validation_service_pb2
from acme.modelregistry.v1 import (
    registered_model_query_service_pb2 as modelregistry_v1_registered_model_query_service_pb2,
)
from acme.pipelines.v1 import pipeline_step_validation_service_pb2 as pipelines_v1_pipeline_step_validation_service_pb2
from acme.recommendations.v1 import (
    recommendation_model_calculation_service_pb2 as recommendations_v1_recommendation_model_calculation_service_pb2,
)
from acme.recommendations.v1 import (
    recommendation_model_calculation_service_pb2_grpc as recommendations_v1_recommendation_model_calculation_service_pb2_grpc,
)
from acme.recommendations.v1 import recommendations_pb2 as recommendations_v1_recommendations_pb2
from acme.shows.v1 import show_calculation_service_pb2 as shows_v1_show_calculation_service_pb2
from acme.shows.v1 import show_query_service_pb2 as shows_v1_show_query_service_pb2

from acme_data.domains.forecasting import hooks
from acme_data.domains.forecasting.dependencies import Dependencies
from acme_data.domains.forecasting.models import DemandForecastCloneDemandForecast1Command
from acme_data.domains.forecasting.models import to_demand_forecast_clone_demand_forecast1_command
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import run_steps
from acme_data.platform.tenancy import tenant_id
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


async def handle_batch_create_demand_forecasts(
    deps: Dependencies,
    request: forecasting_v1_demand_forecast_service_pb2.BatchCreateDemandForecastsRequest
) -> forecasting_v1_demand_forecast_service_pb2.BatchCreateDemandForecastsResponse:
    """Takes a stream of demand forecasts and answers once at the end."""
    response = forecasting_v1_demand_forecast_service_pb2.BatchCreateDemandForecastsResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('BatchCreateDemandForecasts', extra={'fields': {'sequence': request.sequence}})
        await deps.repository.audit(
            request.context.tenant_id,
            'BatchCreateDemandForecasts',
            {'sequence': request.sequence}
        )
        if request.WhichOneof('chunk') == 'record':
            await deps.repository.save_demand_forecast(request.context.tenant_id, request.record)
        response_0 = datasets_v1_dataset_service_pb2.CreateDatasetResponse()
        response_1 = pipelines_v1_pipeline_step_validation_service_pb2.ScorePipelineStepResponse()
        outgoing_0 = datasets_v1_dataset_service_pb2.CreateDatasetRequest(
            context=request.context,
            dataset=datasets_v1_datasets_pb2.Dataset(
                address=common_v1_address_pb2.PostalAddress(
                    lines=list(request.record.billing_address.lines),
                    recipient=request.record.billing_address.recipient
                ),
                audit=common_v1_audit_pb2.AuditInfo(created_by=request.record.audit.created_by)
            )
        )
        response_0 = await deps.clients.datasets_dataset.CreateDataset(outgoing_0, timeout=deps.settings.timeout)
        outgoing_1 = pipelines_v1_pipeline_step_validation_service_pb2.ScorePipelineStepRequest()
        outgoing_1.context.CopyFrom(request.context)
        outgoing_1.pipeline_step.audit.etag = response_0.dataset.audit.etag
        outgoing_1.details.destination.locality = response_0.dataset.address.locality
        outgoing_1.details.destination.country_code = request.record.billing_address.country_code
        merged_1 = pipelines_v1_pipeline_step_validation_service_pb2.ScorePipelineStepRequest()
        merged_1.MergeFrom(outgoing_1)
        outgoing_1.CopyFrom(merged_1)
        response_1 = await deps.clients.pipelines_pipeline_step_validation.ScorePipelineStep(
            outgoing_1,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.result.details
        response.result.details.update(returned_0_0)
        returned_1_0 = response_1.result.details
        response.result.details.update(returned_1_0)
        return response


async def handle_batch_get_demand_forecasts(
    deps: Dependencies,
    request: forecasting_v1_demand_forecast_service_pb2.BatchGetDemandForecastsRequest
) -> forecasting_v1_demand_forecast_service_pb2.BatchGetDemandForecastsResponse:
    """Returns several demand forecasts at once."""
    response = forecasting_v1_demand_forecast_service_pb2.BatchGetDemandForecastsResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('BatchGetDemandForecasts', extra={'fields': {'domain': 'forecasting'}})
        await deps.repository.audit(request.context.tenant_id, 'BatchGetDemandForecasts', {})
        response_0 = forecasting_v1_forecast_model_query_service_pb2.CountForecastModelsResponse()
        response_1 = recommendations_v1_recommendation_model_calculation_service_pb2.CompareRecommendationModelOptionsResponse()
        outgoing_0 = forecasting_v1_forecast_model_query_service_pb2.CountForecastModelsRequest(
            context=request.context,
            filter=forecasting_v1_forecast_model_query_service_pb2.CountForecastModelsRequest.Filter(
                created_after=request.context.deadline,
                labels=dict(request.context.baggage),
                owner_id=request.context.actor.user_id
            )
        )
        response_0 = await deps.clients.forecasting_forecast_model_query.CountForecastModels(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = recommendations_v1_recommendation_model_calculation_service_pb2.CompareRecommendationModelOptionsRequest(
            annotations=dict(response_0.result.details),
            context=request.context,
            recommendation_model=recommendations_v1_recommendations_pb2.RecommendationModel(
                owner=identity_v1_refs_pb2.UserRef(
                    email=request.context.actor.email,
                    user_id=request.context.actor.user_id
                )
            )
        )
        registered_1 = cast(
            recommendations_v1_recommendation_model_calculation_service_pb2_grpc.RecommendationModelCalculationServiceStub,
            deps.clients.registry['acme.recommendations.v1.RecommendationModelCalculationService']
        )
        response_1 = await registered_1.CompareRecommendationModelOptions(outgoing_1, timeout=deps.settings.timeout)
        returned_0_0 = response_0.result.reference_ids
        response.result.reference_ids.extend(returned_0_0)
        returned_0_1 = response_0.result.message
        if returned_0_1:
            response.result.message = returned_0_1
        returned_1_0 = response_1.breakdown.total
        returned_1_0_part_0 = response.demand_forecasts.add()
        if returned_1_0.ListFields():
            returned_1_0_part_0.total.MergeFrom(returned_1_0)
        return response


async def handle_clone_demand_forecast(
    deps: Dependencies,
    request: forecasting_v1_demand_forecast_service_pb2.CloneDemandForecastRequest
) -> forecasting_v1_demand_forecast_service_pb2.CloneDemandForecastResponse:
    """Creates a demand forecast."""
    response = forecasting_v1_demand_forecast_service_pb2.CloneDemandForecastResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('CloneDemandForecast', extra={'fields': {'request_id': request.request_id}})
        await deps.repository.audit(
            request.context.tenant_id,
            'CloneDemandForecast',
            {'request_id': request.request_id}
        )
        await deps.repository.save_demand_forecast(request.context.tenant_id, request.demand_forecast)
        response_0 = documents_v1_document_service_pb2.CreateDocumentResponse()
        response_1 = shows_v1_show_calculation_service_pb2.SimulateShowResponse()
        outgoing_0 = documents_v1_document_service_pb2.CreateDocumentRequest(
            context=request.context,
            document=documents_v1_documents_pb2.Document(
                audit=common_v1_audit_pb2.AuditInfo(created_at=request.demand_forecast.audit.created_at),
                billing_address=common_v1_address_pb2.PostalAddress(
                    recipient=request.demand_forecast.billing_address.recipient
                ),
                card=documents_v1_documents_pb2.DocumentCardSettlement(token=request.demand_forecast.card.token)
            )
        )
        response_0 = await deps.clients.documents_document.CreateDocument(outgoing_0, timeout=deps.settings.timeout)
        command_1 = DemandForecastCloneDemandForecast1Command.model_validate(
            {
                'context': request.context,
                'show_location_locality': response_0.document.billing_address.locality,
                'show_organizer_display_name': request.demand_forecast.counterparty.display_name,
                'show_location_postal_code': response_0.document.billing_address.postal_code
            }
        )
        outgoing_1 = to_demand_forecast_clone_demand_forecast1_command(command_1)
        response_1 = await deps.clients.shows_show_calculation.SimulateShow(outgoing_1, timeout=deps.settings.timeout)
        returned_0_0 = response_0.result.reference_ids
        response.result.reference_ids.extend(returned_0_0)
        returned_0_1 = response_0.result.correlation_id
        if returned_0_1:
            response.result.correlation_id = returned_0_1
        returned_1_0 = response_1.show.audit.created_at
        if returned_1_0.ListFields():
            response.demand_forecast.audit.created_at.MergeFrom(returned_1_0)
        returned_1_1 = response_1.show.audit.created_by
        if returned_1_1:
            response.demand_forecast.audit.created_by = returned_1_1
        echoed_0 = request.demand_forecast.status
        response.demand_forecast.status = echoed_0
        echoed_1 = request.demand_forecast.total
        response.demand_forecast.total.CopyFrom(echoed_1)
        return response


async def handle_create_demand_forecast(
    deps: Dependencies,
    request: forecasting_v1_demand_forecast_service_pb2.CreateDemandForecastRequest
) -> forecasting_v1_demand_forecast_service_pb2.CreateDemandForecastResponse:
    """Creates a demand forecast."""
    response = forecasting_v1_demand_forecast_service_pb2.CreateDemandForecastResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('CreateDemandForecast', extra={'fields': {'request_id': request.request_id}})
        await deps.repository.audit(
            request.context.tenant_id,
            'CreateDemandForecast',
            {'request_id': request.request_id}
        )
        await deps.repository.save_demand_forecast(request.context.tenant_id, request.demand_forecast)
        response_0 = shows_v1_show_query_service_pb2.SuggestShowsResponse()
        response_1 = forecasting_v1_forecast_model_validation_service_pb2.NormalizeForecastModelResponse()
        response_2 = modelregistry_v1_registered_model_query_service_pb2.ResolveRegisteredModelsResponse()
        outgoing_0 = shows_v1_show_query_service_pb2.SuggestShowsRequest(
            context=request.context,
            filter=shows_v1_show_query_service_pb2.SuggestShowsRequest.Filter(
                created_after=request.demand_forecast.audit.created_at,
                labels=dict(request.demand_forecast.metadata),
                owner_id=request.demand_forecast.counterparty.scenario_id,
                region=request.demand_forecast.billing_address.region
            )
        )
        response_0 = await deps.clients.shows_show_query.SuggestShows(outgoing_0, timeout=deps.settings.timeout)
        outgoing_1 = forecasting_v1_forecast_model_validation_service_pb2.NormalizeForecastModelRequest(
            context=request.context,
            forecast_model=forecasting_v1_forecasting_pb2.ForecastModel(
                audit=common_v1_audit_pb2.AuditInfo(created_by=request.demand_forecast.audit.created_by)
            )
        )
        response_1 = await hooks.demand_forecast_create_demand_forecast1(
            deps.clients.forecasting_forecast_model_validation,
            outgoing_1,
            deps.settings.timeout
        )
        outgoing_2 = modelregistry_v1_registered_model_query_service_pb2.ResolveRegisteredModelsRequest()
        outgoing_2.context.CopyFrom(request.context)
        outgoing_2.context.tenant_id = tenant_id.get()
        response_2 = await deps.clients.modelregistry_registered_model_query.ResolveRegisteredModels(
            outgoing_2,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.result.details
        response.result.details.update(returned_0_0)
        returned_0_1 = response_0.result.message
        if returned_0_1:
            response.result.message = returned_0_1
        returned_1_0 = response_1.outcome.message
        if returned_1_0:
            response.result.message = returned_1_0
        returned_2_0 = response_2.result.message
        if returned_2_0:
            response.result.message = returned_2_0
        returned_2_1 = response_2.result.status
        if returned_2_1:
            response.result.status = returned_2_1
        echoed_0 = request.demand_forecast.number
        response.demand_forecast.number = echoed_0
        echoed_1 = request.demand_forecast.metadata
        response.demand_forecast.metadata.update(echoed_1)
        return response


async def handle_delete_demand_forecast(
    deps: Dependencies,
    request: forecasting_v1_demand_forecast_service_pb2.DeleteDemandForecastRequest
) -> forecasting_v1_demand_forecast_service_pb2.DeleteDemandForecastResponse:
    """Deletes a demand forecast."""
    response = forecasting_v1_demand_forecast_service_pb2.DeleteDemandForecastResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('DeleteDemandForecast', extra={'fields': {'force': request.force}})
        await deps.repository.audit(request.context.tenant_id, 'DeleteDemandForecast', {'force': request.force})
        response_0 = identity_v1_user_validation_service_pb2.ExplainUserDecisionResponse()
        response_1 = forecasting_v1_demand_forecast_query_service_pb2.LookupDemandForecastResponse()
        outgoing_0 = identity_v1_user_validation_service_pb2.ExplainUserDecisionRequest(
            context=request.context,
            user=identity_v1_identity_pb2.User(audit=common_v1_audit_pb2.AuditInfo(etag=request.etag))
        )
        response_0 = await deps.clients.identity_user_validation.ExplainUserDecision(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = forecasting_v1_demand_forecast_query_service_pb2.LookupDemandForecastRequest(
            context=request.context,
            demand_forecast_id=request.demand_forecast_id
        )
        steps_1 = [
            partial(
                deps.clients.forecasting_demand_forecast_query.LookupDemandForecast,
                outgoing_1,
                timeout=deps.settings.timeout
            )
        ]
        results_1 = await run_steps(steps_1)
        response_1 = results_1[-1]
        returned_0_0 = response_0.result.reference_ids
        response.result.reference_ids.extend(returned_0_0)
        returned_1_0 = response_1.result.status
        if returned_1_0:
            response.result.status = returned_1_0
        returned_1_1 = response_1.result.correlation_id
        if returned_1_1:
            response.result.correlation_id = returned_1_1
        return response


async def handle_get_demand_forecast(
    deps: Dependencies,
    request: forecasting_v1_demand_forecast_service_pb2.GetDemandForecastRequest
) -> forecasting_v1_demand_forecast_service_pb2.GetDemandForecastResponse:
    """Returns a demand forecast."""
    response = forecasting_v1_demand_forecast_service_pb2.GetDemandForecastResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('GetDemandForecast', extra={'fields': {'domain': 'forecasting'}})
        await deps.repository.audit(request.context.tenant_id, 'GetDemandForecast', {})
        response_0 = documents_v1_document_query_service_pb2.ResolveDocumentsResponse()
        outgoing_0 = documents_v1_document_query_service_pb2.ResolveDocumentsRequest(context=request.context)
        response_0 = await deps.clients.documents_document_query.ResolveDocuments(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.result.reference_ids
        response.result.reference_ids.extend(returned_0_0)
        returned_0_1 = response_0.result.status
        if returned_0_1:
            response.result.status = returned_0_1
        echoed_0 = request.demand_forecast_id
        response.demand_forecast.demand_forecast_id = echoed_0
        return response


async def handle_list_demand_forecasts(
    deps: Dependencies,
    request: forecasting_v1_demand_forecast_service_pb2.ListDemandForecastsRequest
) -> forecasting_v1_demand_forecast_service_pb2.ListDemandForecastsResponse:
    """Lists demand forecasts a page at a time."""
    response = forecasting_v1_demand_forecast_service_pb2.ListDemandForecastsResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('ListDemandForecasts', extra={'fields': {'order_by': request.order_by}})
        await deps.repository.audit(request.context.tenant_id, 'ListDemandForecasts', {'order_by': request.order_by})
        return response


async def handle_search_demand_forecasts(
    deps: Dependencies,
    request: forecasting_v1_demand_forecast_service_pb2.SearchDemandForecastsRequest
) -> forecasting_v1_demand_forecast_service_pb2.SearchDemandForecastsResponse:
    """Lists demand forecasts a page at a time."""
    response = forecasting_v1_demand_forecast_service_pb2.SearchDemandForecastsResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('SearchDemandForecasts', extra={'fields': {'order_by': request.order_by}})
        await deps.repository.audit(request.context.tenant_id, 'SearchDemandForecasts', {'order_by': request.order_by})
        response_0 = forecasting_v1_demand_forecast_query_service_pb2.CountDemandForecastsResponse()
        response_1 = forecasting_v1_forecast_model_query_service_pb2.SummarizeForecastModelsResponse()
        outgoing_0 = forecasting_v1_demand_forecast_query_service_pb2.CountDemandForecastsRequest(
            context=request.context,
            filter=forecasting_v1_demand_forecast_query_service_pb2.CountDemandForecastsRequest.Filter(
                labels=dict(request.filter.labels),
                owner_id=request.filter.owner_id,
                region=request.filter.region
            )
        )
        response_0 = await deps.clients.forecasting_demand_forecast_query.CountDemandForecasts(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = forecasting_v1_forecast_model_query_service_pb2.SummarizeForecastModelsRequest(
            annotations=dict(response_0.result.details),
            context=request.context,
            details=forecasting_v1_forecast_model_query_service_pb2.SummarizeForecastModelsRequest.Details(
                filters=dict(request.filter.labels)
            )
        )
        response_1 = await deps.clients.forecasting_forecast_model_query.SummarizeForecastModels(
            outgoing_1,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.result.status
        if returned_0_0:
            response.result.status = returned_0_0
        returned_0_1 = response_0.result.details
        response.result.details.update(returned_0_1)
        returned_1_0 = response_1.result.status
        if returned_1_0:
            response.result.status = returned_1_0
        return response


async def handle_update_demand_forecast(
    deps: Dependencies,
    request: forecasting_v1_demand_forecast_service_pb2.UpdateDemandForecastRequest
) -> forecasting_v1_demand_forecast_service_pb2.UpdateDemandForecastResponse:
    """Changes a demand forecast."""
    response = forecasting_v1_demand_forecast_service_pb2.UpdateDemandForecastResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('UpdateDemandForecast', extra={'fields': {'allow_missing': request.allow_missing}})
        await deps.repository.audit(
            request.context.tenant_id,
            'UpdateDemandForecast',
            {'allow_missing': request.allow_missing}
        )
        await deps.repository.save_demand_forecast(request.context.tenant_id, request.demand_forecast)
        response_0 = anomalies_v1_anomaly_query_service_pb2.ExportAnomaliesResponse()
        response_1 = recommendations_v1_recommendation_model_calculation_service_pb2.CalculateRecommendationModelResponse()
        outgoing_0 = anomalies_v1_anomaly_query_service_pb2.ExportAnomaliesRequest(
            context=request.context,
            filter=anomalies_v1_anomaly_query_service_pb2.ExportAnomaliesRequest.Filter(
                created_after=request.demand_forecast.issued_at,
                owner_id=request.demand_forecast.counterparty.scenario_id,
                region=request.demand_forecast.billing_address.region
            )
        )
        async for chunk_0 in deps.clients.anomalies_anomaly_query.ExportAnomalies(
            outgoing_0,
            timeout=deps.settings.timeout
        ):
            response_0 = chunk_0
        fields_1: dict[str, Any] = {
            'context': request.context,
            'details': {'destination': {'country_code': request.demand_forecast.billing_address.country_code}},
            'recommendation_model': {'audit': {'updated_by': request.demand_forecast.audit.updated_by}}
        }
        outgoing_1 = recommendations_v1_recommendation_model_calculation_service_pb2.CalculateRecommendationModelRequest(**fields_1)
        response_1 = await deps.clients.recommendations_recommendation_model_calculation.CalculateRecommendationModel(
            outgoing_1,
            timeout=deps.settings.timeout
        )
        returned_1_0 = response_1.recommendation_model.address.locality
        if returned_1_0:
            response.demand_forecast.billing_address.locality = returned_1_0
        echoed_0 = request.demand_forecast.notes
        response.demand_forecast.notes = echoed_0
        echoed_1 = request.demand_forecast.issued_at
        response.demand_forecast.issued_at.CopyFrom(echoed_1)
        return response
