"""Computes the figures of a model version, such as totals, taxes, and estimates."""

from __future__ import annotations

from collections.abc import AsyncIterator
from collections.abc import Awaitable
from collections.abc import Callable
from dataclasses import dataclass
from functools import partial
from typing import Any
import asyncio
import logging

from google.protobuf.json_format import MessageToDict
from google.protobuf.json_format import MessageToJson
from google.protobuf.json_format import Parse
from google.protobuf.json_format import ParseDict
import grpc

from acme.anomalies.v1 import anomalies_pb2 as anomalies_v1_anomalies_pb2
from acme.anomalies.v1 import anomaly_validation_service_pb2 as anomalies_v1_anomaly_validation_service_pb2
from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.featurestore.v1 import (
    feature_view_validation_service_pb2 as featurestore_v1_feature_view_validation_service_pb2,
)
from acme.featurestore.v1 import featurestore_pb2 as featurestore_v1_featurestore_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.lineage.v1 import lineage_node_query_service_pb2 as lineage_v1_lineage_node_query_service_pb2
from acme.metrics.v1 import dashboard_history_service_pb2 as metrics_v1_dashboard_history_service_pb2
from acme.metrics.v1 import metric_series_export_service_pb2 as metrics_v1_metric_series_export_service_pb2
from acme.metrics.v1 import metrics_pb2 as metrics_v1_metrics_pb2
from acme.metrics.v1 import refs_pb2 as metrics_v1_refs_pb2
from acme.modelregistry.v1 import (
    model_version_calculation_service_pb2 as modelregistry_v1_model_version_calculation_service_pb2,
)
from acme.modelregistry.v1 import (
    model_version_calculation_service_pb2_grpc as modelregistry_v1_model_version_calculation_service_pb2_grpc,
)
from acme.modelregistry.v1 import modelregistry_pb2 as modelregistry_v1_modelregistry_pb2
from acme.modelregistry.v1 import (
    registered_model_calculation_service_pb2 as modelregistry_v1_registered_model_calculation_service_pb2,
)

from acme_data.domains.modelregistry.adapters import ModelVersionCalculationExplainModelVersionCalculation0Adapter
from acme_data.domains.modelregistry.adapters import ModelVersionCalculationExplainModelVersionCalculation0Port
from acme_data.domains.modelregistry.adapters import ModelVersionCalculationExplainModelVersionCalculation2Adapter
from acme_data.domains.modelregistry.dependencies import Dependencies
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import run_steps
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


@dataclass(slots=True)
class ModelVersionCalculationServicer(
    modelregistry_v1_model_version_calculation_service_pb2_grpc.ModelVersionCalculationServiceServicer
):
    deps: Dependencies

    @rpc_errors
    async def CalculateModelVersion(
        self, request: modelregistry_v1_model_version_calculation_service_pb2.CalculateModelVersionRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_model_version_calculation_service_pb2.CalculateModelVersionResponse:
        """Calculates a model version."""
        return await self.handle_calculate_model_version(request)

    @rpc_errors
    async def CompareModelVersionOptions(
        self, request: modelregistry_v1_model_version_calculation_service_pb2.CompareModelVersionOptionsRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_model_version_calculation_service_pb2.CompareModelVersionOptionsResponse:
        """Compares a model version."""
        return await self.handle_compare_model_version_options(request)

    @rpc_errors
    async def EstimateModelVersion(
        self, request: modelregistry_v1_model_version_calculation_service_pb2.EstimateModelVersionRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_model_version_calculation_service_pb2.EstimateModelVersionResponse:
        """Estimates a model version."""
        return await self.handle_estimate_model_version(request)

    @rpc_errors
    async def ExplainModelVersionCalculation(
        self, request: modelregistry_v1_model_version_calculation_service_pb2.ExplainModelVersionCalculationRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_model_version_calculation_service_pb2.ExplainModelVersionCalculationResponse:
        """Explains a model version."""
        return await self.handle_explain_model_version_calculation(request)

    @rpc_errors
    @retry_transient
    async def GetModelVersionRates(
        self, request: modelregistry_v1_model_version_calculation_service_pb2.GetModelVersionRatesRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_model_version_calculation_service_pb2.GetModelVersionRatesResponse:
        """Returns a model version."""
        return await self.handle_get_model_version_rates(request)

    @rpc_errors
    async def QuoteModelVersion(
        self, request: modelregistry_v1_model_version_calculation_service_pb2.QuoteModelVersionRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_model_version_calculation_service_pb2.QuoteModelVersionResponse:
        """Quotes a model version."""
        return await self.handle_quote_model_version(request)

    @rpc_errors
    async def RecalculateModelVersions(
        self, request: modelregistry_v1_model_version_calculation_service_pb2.RecalculateModelVersionsRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_model_version_calculation_service_pb2.RecalculateModelVersionsResponse:
        """Recalculates a model version."""
        return await self.handle_recalculate_model_versions(request)

    @rpc_errors
    async def SimulateModelVersion(
        self, request: modelregistry_v1_model_version_calculation_service_pb2.SimulateModelVersionRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_model_version_calculation_service_pb2.SimulateModelVersionResponse:
        """Simulates a model version."""
        return await self.handle_simulate_model_version(request)

    async def handle_calculate_model_version(
        self,
        request: modelregistry_v1_model_version_calculation_service_pb2.CalculateModelVersionRequest
    ) -> modelregistry_v1_model_version_calculation_service_pb2.CalculateModelVersionResponse:
        """Calculates a model version."""
        deps = self.deps
        response = modelregistry_v1_model_version_calculation_service_pb2.CalculateModelVersionResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CalculateModelVersion', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'CalculateModelVersion', {'reason': request.reason})
            await deps.repository.save_model_version(request.context.tenant_id, request.model_version)
            response_0 = modelregistry_v1_registered_model_calculation_service_pb2.ExplainRegisteredModelCalculationResponse()
            async for item_0 in async_messages(request.model_version.measurements):
                outgoing_0 = modelregistry_v1_registered_model_calculation_service_pb2.ExplainRegisteredModelCalculationRequest(
                    context=request.context,
                    registered_model=modelregistry_v1_modelregistry_pb2.RegisteredModel(
                        address=common_v1_address_pb2.PostalAddress(
                            country_code=request.details.destination.country_code
                        ),
                        dimensions=modelregistry_v1_modelregistry_pb2.RegisteredModelDimensions(unit=item_0.unit),
                        owner=identity_v1_refs_pb2.UserRef(display_name=request.model_version.subject.display_name)
                    )
                )
                response_0 = await deps.clients.modelregistry_registered_model_calculation.ExplainRegisteredModelCalculation(
                    outgoing_0,
                    timeout=deps.settings.timeout
                )
            echoed_0 = request.model_version_id
            response.model_version.model_version_id = echoed_0
            echoed_1 = request.model_version.attributes
            response.model_version.attributes.update(echoed_1)
            return response

    async def handle_compare_model_version_options(
        self,
        request: modelregistry_v1_model_version_calculation_service_pb2.CompareModelVersionOptionsRequest
    ) -> modelregistry_v1_model_version_calculation_service_pb2.CompareModelVersionOptionsResponse:
        """Compares a model version."""
        deps = self.deps
        response = modelregistry_v1_model_version_calculation_service_pb2.CompareModelVersionOptionsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CompareModelVersionOptions', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'CompareModelVersionOptions',
                {'reason': request.reason}
            )
            await deps.repository.save_model_version(request.context.tenant_id, request.model_version)
            response_0 = modelregistry_v1_registered_model_calculation_service_pb2.QuoteRegisteredModelResponse()
            response_1 = anomalies_v1_anomaly_validation_service_pb2.PreviewAnomalyResponse()
            for item_0 in request.model_version.measurements:
                outgoing_0 = modelregistry_v1_registered_model_calculation_service_pb2.QuoteRegisteredModelRequest(
                    context=request.context,
                    registered_model=modelregistry_v1_modelregistry_pb2.RegisteredModel(
                        dimensions=modelregistry_v1_modelregistry_pb2.RegisteredModelDimensions(unit=item_0.unit)
                    )
                )
                response_0 = await deps.clients.modelregistry_registered_model_calculation.QuoteRegisteredModel(
                    outgoing_0,
                    timeout=deps.settings.timeout
                )
            outgoing_1 = anomalies_v1_anomaly_validation_service_pb2.PreviewAnomalyRequest(
                anomaly=anomalies_v1_anomalies_pb2.Anomaly(
                    requester=common_v1_contact_pb2.ContactInfo(email=response_0.registered_model.owner.email)
                ),
                context=request.context
            )
            send_1 = partial(deps.clients.anomalies_anomaly_validation.PreviewAnomaly, timeout=deps.settings.timeout)
            response_1 = await send_1(outgoing_1)
            returned_1_0 = response_1.result.status
            if returned_1_0:
                response.result.status = returned_1_0
            returned_1_1 = response_1.result.message
            if returned_1_1:
                response.result.message = returned_1_1
            echoed_0 = request.model_version_id
            response.model_version.model_version_id = echoed_0
            echoed_1 = request.model_version.kind
            response.model_version.kind = echoed_1
            return response

    async def handle_estimate_model_version(
        self,
        request: modelregistry_v1_model_version_calculation_service_pb2.EstimateModelVersionRequest
    ) -> modelregistry_v1_model_version_calculation_service_pb2.EstimateModelVersionResponse:
        """Estimates a model version."""
        deps = self.deps
        response = modelregistry_v1_model_version_calculation_service_pb2.EstimateModelVersionResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('EstimateModelVersion', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'EstimateModelVersion', {'reason': request.reason})
            await deps.repository.save_model_version(request.context.tenant_id, request.model_version)
            response_0 = modelregistry_v1_registered_model_calculation_service_pb2.QuoteRegisteredModelResponse()
            response_1 = modelregistry_v1_registered_model_calculation_service_pb2.RecalculateRegisteredModelsResponse()
            requests_0: list[modelregistry_v1_registered_model_calculation_service_pb2.QuoteRegisteredModelRequest] = []
            for item_0 in request.model_version.measurements:
                outgoing_0 = modelregistry_v1_registered_model_calculation_service_pb2.QuoteRegisteredModelRequest(
                    context=request.context,
                    details=modelregistry_v1_registered_model_calculation_service_pb2.QuoteRegisteredModelRequest.Details(
                        destination=common_v1_address_pb2.PostalAddress(lines=list(request.details.destination.lines))
                    ),
                    registered_model=modelregistry_v1_modelregistry_pb2.RegisteredModel(
                        address=common_v1_address_pb2.PostalAddress(
                            postal_code=request.details.destination.postal_code
                        ),
                        audit=common_v1_audit_pb2.AuditInfo(created_at=item_0.observed_at),
                        dimensions=modelregistry_v1_modelregistry_pb2.RegisteredModelDimensions(unit=item_0.unit)
                    )
                )
                requests_0.append(outgoing_0)
            replies_0 = await asyncio.gather(*(
                deps.clients.modelregistry_registered_model_calculation.QuoteRegisteredModel(
                    entry,
                    timeout=deps.settings.timeout
                ) for entry in requests_0
            ))
            if replies_0:
                response_0 = replies_0[-1]
            callbacks_1: list[
                Callable[
                    [],
                    Awaitable[
                        modelregistry_v1_registered_model_calculation_service_pb2.RecalculateRegisteredModelsResponse
                    ]
                ]
            ] = []
            for item_1 in request.model_version.measurements:
                outgoing_1 = modelregistry_v1_registered_model_calculation_service_pb2.RecalculateRegisteredModelsRequest(
                    context=request.context,
                    registered_model=modelregistry_v1_modelregistry_pb2.RegisteredModel(
                        dimensions=modelregistry_v1_modelregistry_pb2.RegisteredModelDimensions(unit=item_1.unit),
                        owner=identity_v1_refs_pb2.UserRef(display_name=response_0.registered_model.owner.display_name)
                    )
                )
                async def send_1(
                    payload: modelregistry_v1_registered_model_calculation_service_pb2.RecalculateRegisteredModelsRequest = outgoing_1
                ) -> modelregistry_v1_registered_model_calculation_service_pb2.RecalculateRegisteredModelsResponse:
                    return await deps.clients.modelregistry_registered_model_calculation.RecalculateRegisteredModels(
                        payload,
                        timeout=deps.settings.timeout
                    )
                callbacks_1.append(send_1)
            for callback_1 in callbacks_1:
                response_1 = await callback_1()
            echoed_0 = request.model_version_id
            response.model_version.model_version_id = echoed_0
            echoed_1 = request.model_version.kind
            response.model_version.kind = echoed_1
            return response

    async def handle_explain_model_version_calculation(
        self,
        request: modelregistry_v1_model_version_calculation_service_pb2.ExplainModelVersionCalculationRequest
    ) -> modelregistry_v1_model_version_calculation_service_pb2.ExplainModelVersionCalculationResponse:
        """Explains a model version."""
        deps = self.deps
        response = modelregistry_v1_model_version_calculation_service_pb2.ExplainModelVersionCalculationResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ExplainModelVersionCalculation', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ExplainModelVersionCalculation',
                {'reason': request.reason}
            )
            await deps.repository.save_model_version(request.context.tenant_id, request.model_version)
            response_0 = modelregistry_v1_registered_model_calculation_service_pb2.EstimateRegisteredModelResponse()
            response_1 = metrics_v1_metric_series_export_service_pb2.RetryMetricSeriesExportResponse()
            response_2 = metrics_v1_dashboard_history_service_pb2.RecordDashboardVersionResponse()
            outgoing_0 = modelregistry_v1_registered_model_calculation_service_pb2.EstimateRegisteredModelRequest(
                annotations=dict(request.annotations),
                context=request.context,
                registered_model=modelregistry_v1_modelregistry_pb2.RegisteredModel(
                    owner=identity_v1_refs_pb2.UserRef(
                        display_name=request.model_version.subject.display_name,
                        email=request.model_version.subject.email
                    )
                )
            )
            port_0: ModelVersionCalculationExplainModelVersionCalculation0Port = ModelVersionCalculationExplainModelVersionCalculation0Adapter(
                deps.clients.modelregistry_registered_model_calculation,
                deps.settings.timeout
            )
            response_0 = await port_0.execute(outgoing_0)
            outgoing_1 = metrics_v1_metric_series_export_service_pb2.RetryMetricSeriesExportRequest(
                context=request.context,
                metric_series=metrics_v1_metrics_pb2.MetricSeries(
                    address=common_v1_address_pb2.PostalAddress(
                        postal_code=response_0.registered_model.address.postal_code
                    ),
                    dimensions=metrics_v1_metrics_pb2.MetricSeriesDimensions(
                        height=response_0.registered_model.dimensions.height
                    ),
                    owner=identity_v1_refs_pb2.UserRef(display_name=request.model_version.subject.display_name)
                )
            )
            steps_1 = [
                partial(
                    deps.clients.metrics_metric_series_export.RetryMetricSeriesExport,
                    outgoing_1,
                    timeout=deps.settings.timeout
                )
            ]
            results_1 = await run_steps(steps_1)
            response_1 = results_1[-1]
            outgoing_2 = metrics_v1_dashboard_history_service_pb2.RecordDashboardVersionRequest(
                context=request.context,
                dashboard=metrics_v1_metrics_pb2.Dashboard(
                    audit=common_v1_audit_pb2.AuditInfo(updated_at=response_1.metric_series.audit.updated_at),
                    counterparty=metrics_v1_refs_pb2.MetricAlertRef(
                        display_name=response_1.metric_series.owner.display_name
                    ),
                    lines=[
                        metrics_v1_metrics_pb2.DashboardLine(
                            description=response_1.metric_series.components.get(
                                'primary',
                                metrics_v1_metrics_pb2.MetricSeriesComponent()
                            ).description
                        )
                    ]
                )
            )
            response_2 = await ModelVersionCalculationExplainModelVersionCalculation2Adapter(
                deps.clients.metrics_dashboard_history,
                deps.settings.timeout
            )(outgoing_2)
            returned_0_0 = response_0.result.correlation_id
            if returned_0_0:
                response.model_version.correlation_id = returned_0_0
            returned_1_0 = response_1.outcome.message
            if returned_1_0:
                response.outcome.message = returned_1_0
            returned_2_0 = response_2.result.correlation_id
            if returned_2_0:
                response.model_version.correlation_id = returned_2_0
            returned_2_1 = response_2.result.message
            if returned_2_1:
                response.outcome.message = returned_2_1
            echoed_0 = request.model_version_id
            response.model_version.model_version_id = echoed_0
            echoed_1 = request.model_version.attributes
            response.model_version.attributes.update(echoed_1)
            return response

    async def handle_get_model_version_rates(
        self,
        request: modelregistry_v1_model_version_calculation_service_pb2.GetModelVersionRatesRequest
    ) -> modelregistry_v1_model_version_calculation_service_pb2.GetModelVersionRatesResponse:
        """Returns a model version."""
        deps = self.deps
        response = modelregistry_v1_model_version_calculation_service_pb2.GetModelVersionRatesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('GetModelVersionRates', extra={'fields': {'locale': request.context.locale}})
            await deps.repository.audit(
                request.context.tenant_id,
                'GetModelVersionRates',
                {'locale': request.context.locale}
            )
            echoed_0 = request.model_version_id
            response.model_version.model_version_id = echoed_0
            return response

    async def handle_quote_model_version(
        self,
        request: modelregistry_v1_model_version_calculation_service_pb2.QuoteModelVersionRequest
    ) -> modelregistry_v1_model_version_calculation_service_pb2.QuoteModelVersionResponse:
        """Quotes a model version."""
        deps = self.deps
        response = modelregistry_v1_model_version_calculation_service_pb2.QuoteModelVersionResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('QuoteModelVersion', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'QuoteModelVersion', {'reason': request.reason})
            await deps.repository.save_model_version(request.context.tenant_id, request.model_version)
            response_0 = modelregistry_v1_registered_model_calculation_service_pb2.SimulateRegisteredModelResponse()
            response_1 = anomalies_v1_anomaly_validation_service_pb2.CheckAnomalyEligibilityResponse()
            async for item_0 in async_messages(request.model_version.measurements):
                outgoing_0 = modelregistry_v1_registered_model_calculation_service_pb2.SimulateRegisteredModelRequest(
                    context=request.context,
                    registered_model=modelregistry_v1_modelregistry_pb2.RegisteredModel(
                        address=common_v1_address_pb2.PostalAddress(lines=list(request.details.destination.lines)),
                        audit=common_v1_audit_pb2.AuditInfo(updated_at=item_0.observed_at),
                        dimensions=modelregistry_v1_modelregistry_pb2.RegisteredModelDimensions(unit=item_0.unit)
                    )
                )
                response_0 = await deps.clients.modelregistry_registered_model_calculation.SimulateRegisteredModel(
                    outgoing_0,
                    timeout=deps.settings.timeout
                )
            for item_1 in request.model_version.measurements:
                outgoing_1 = anomalies_v1_anomaly_validation_service_pb2.CheckAnomalyEligibilityRequest(
                    anomaly=anomalies_v1_anomalies_pb2.Anomaly(
                        comments=[anomalies_v1_anomalies_pb2.AnomalyComment(created_at=item_1.observed_at)]
                    ),
                    context=request.context,
                    details=anomalies_v1_anomaly_validation_service_pb2.CheckAnomalyEligibilityRequest.Details(
                        contact=common_v1_contact_pb2.ContactInfo(email=request.model_version.subject.email)
                    )
                )
                response_1 = await deps.clients.anomalies_anomaly_validation.CheckAnomalyEligibility(
                    outgoing_1,
                    timeout=deps.settings.timeout
                )
            echoed_0 = request.model_version_id
            response.model_version.model_version_id = echoed_0
            echoed_1 = request.model_version.occurred_at
            response.model_version.occurred_at.CopyFrom(echoed_1)
            return response

    async def handle_recalculate_model_versions(
        self,
        request: modelregistry_v1_model_version_calculation_service_pb2.RecalculateModelVersionsRequest
    ) -> modelregistry_v1_model_version_calculation_service_pb2.RecalculateModelVersionsResponse:
        """Recalculates a model version."""
        deps = self.deps
        response = modelregistry_v1_model_version_calculation_service_pb2.RecalculateModelVersionsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('RecalculateModelVersions', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'RecalculateModelVersions',
                {'reason': request.reason}
            )
            await deps.repository.save_model_version(request.context.tenant_id, request.model_version)
            response_0 = featurestore_v1_feature_view_validation_service_pb2.ExplainFeatureViewDecisionResponse()
            outgoing_0 = featurestore_v1_feature_view_validation_service_pb2.ExplainFeatureViewDecisionRequest(
                context=request.context,
                details=featurestore_v1_feature_view_validation_service_pb2.ExplainFeatureViewDecisionRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(email=request.model_version.subject.email)
                ),
                feature_view=featurestore_v1_featurestore_pb2.FeatureView(
                    address=common_v1_address_pb2.PostalAddress(
                        locality=request.details.destination.locality,
                        postal_code=request.details.destination.postal_code
                    ),
                    owner=identity_v1_refs_pb2.UserRef(display_name=request.model_version.subject.display_name)
                )
            )
            method_name_0 = 'ExplainFeatureViewDecision'
            response_0 = await getattr(
                deps.clients.featurestore_feature_view_validation,
                method_name_0
            )(outgoing_0, timeout=deps.settings.timeout)
            returned_0_0 = response_0.feature_view.owner.email
            if returned_0_0:
                response.model_version.subject.email = returned_0_0
            returned_0_1 = response_0.outcome.status
            if returned_0_1:
                response.result.status = returned_0_1
            echoed_0 = request.model_version_id
            response.model_version.model_version_id = echoed_0
            echoed_1 = request.model_version.occurred_at
            response.model_version.occurred_at.CopyFrom(echoed_1)
            return response

    async def handle_simulate_model_version(
        self,
        request: modelregistry_v1_model_version_calculation_service_pb2.SimulateModelVersionRequest
    ) -> modelregistry_v1_model_version_calculation_service_pb2.SimulateModelVersionResponse:
        """Simulates a model version."""
        deps = self.deps
        response = modelregistry_v1_model_version_calculation_service_pb2.SimulateModelVersionResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SimulateModelVersion', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'SimulateModelVersion', {'reason': request.reason})
            await deps.repository.save_model_version(request.context.tenant_id, request.model_version)
            response_0 = modelregistry_v1_registered_model_calculation_service_pb2.EstimateRegisteredModelResponse()
            response_1 = lineage_v1_lineage_node_query_service_pb2.SuggestLineageNodesResponse()
            response_2 = modelregistry_v1_registered_model_calculation_service_pb2.SimulateRegisteredModelResponse()
            fields_0: dict[str, Any] = {
                'context': request.context,
                'registered_model': {'address': {'lines': list(request.details.destination.lines)}}
            }
            outgoing_0 = modelregistry_v1_registered_model_calculation_service_pb2.EstimateRegisteredModelRequest(**fields_0)
            response_0 = await deps.clients.modelregistry_registered_model_calculation.EstimateRegisteredModel(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = lineage_v1_lineage_node_query_service_pb2.SuggestLineageNodesRequest(
                context=request.context,
                filter=lineage_v1_lineage_node_query_service_pb2.SuggestLineageNodesRequest.Filter(
                    created_after=response_0.registered_model.audit.updated_at,
                    region=request.details.destination.region
                )
            )
            document_1 = MessageToDict(outgoing_1, preserving_proto_field_name=True)
            outgoing_1 = ParseDict(document_1, lineage_v1_lineage_node_query_service_pb2.SuggestLineageNodesRequest())
            response_1 = await deps.clients.lineage_lineage_node_query.SuggestLineageNodes(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = modelregistry_v1_registered_model_calculation_service_pb2.SimulateRegisteredModelRequest(
                context=request.context,
                registered_model=modelregistry_v1_modelregistry_pb2.RegisteredModel(
                    address=common_v1_address_pb2.PostalAddress(
                        country_code=request.details.destination.country_code,
                        locality=request.details.destination.locality
                    ),
                    audit=common_v1_audit_pb2.AuditInfo(created_at=response_0.registered_model.audit.created_at)
                )
            )
            document_2 = MessageToJson(outgoing_2, preserving_proto_field_name=True)
            outgoing_2 = Parse(
                document_2,
                modelregistry_v1_registered_model_calculation_service_pb2.SimulateRegisteredModelRequest()
            )
            response_2 = await deps.clients.modelregistry_registered_model_calculation.SimulateRegisteredModel(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.status
            if returned_0_0:
                response.result.status = returned_0_0
            returned_1_0 = response_1.result.message
            if returned_1_0:
                response.result.message = returned_1_0
            returned_1_1 = response_1.result.reference_ids
            response.result.reference_ids.extend(returned_1_1)
            returned_2_0 = response_2.result.reference_ids
            response.result.reference_ids.extend(returned_2_0)
            returned_2_1 = response_2.registered_model.owner.email
            if returned_2_1:
                response.model_version.subject.email = returned_2_1
            echoed_0 = request.model_version_id
            response.model_version.model_version_id = echoed_0
            echoed_1 = request.model_version.kind
            response.model_version.kind = echoed_1
            return response
