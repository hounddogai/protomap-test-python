"""Reusable transport mixin for RecommendationSetValidationService."""

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

from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.datasets.v1 import data_schema_calculation_service_pb2 as datasets_v1_data_schema_calculation_service_pb2
from acme.datasets.v1 import dataset_service_pb2 as datasets_v1_dataset_service_pb2
from acme.datasets.v1 import datasets_pb2 as datasets_v1_datasets_pb2
from acme.featurestore.v1 import (
    feature_view_validation_service_pb2 as featurestore_v1_feature_view_validation_service_pb2,
)
from acme.featurestore.v1 import featurestore_pb2 as featurestore_v1_featurestore_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.keymanagement.v1 import crypto_key_service_pb2 as keymanagement_v1_crypto_key_service_pb2
from acme.ledger.v1 import ledger_account_query_service_pb2 as ledger_v1_ledger_account_query_service_pb2
from acme.lineage.v1 import lineage_edge_validation_service_pb2 as lineage_v1_lineage_edge_validation_service_pb2
from acme.metrics.v1 import dashboard_export_service_pb2 as metrics_v1_dashboard_export_service_pb2
from acme.metrics.v1 import metric_alert_query_service_pb2 as metrics_v1_metric_alert_query_service_pb2
from acme.metrics.v1 import metric_alert_validation_service_pb2 as metrics_v1_metric_alert_validation_service_pb2
from acme.metrics.v1 import metrics_pb2 as metrics_v1_metrics_pb2
from acme.modelregistry.v1 import modelregistry_pb2 as modelregistry_v1_modelregistry_pb2
from acme.modelregistry.v1 import (
    registered_model_validation_service_pb2 as modelregistry_v1_registered_model_validation_service_pb2,
)
from acme.recommendations.v1 import (
    recommendation_model_calculation_service_pb2 as recommendations_v1_recommendation_model_calculation_service_pb2,
)
from acme.recommendations.v1 import (
    recommendation_model_calculation_service_pb2_grpc as recommendations_v1_recommendation_model_calculation_service_pb2_grpc,
)
from acme.recommendations.v1 import (
    recommendation_set_validation_service_pb2 as recommendations_v1_recommendation_set_validation_service_pb2,
)
from acme.recommendations.v1 import recommendations_pb2 as recommendations_v1_recommendations_pb2

from acme_data.domains.recommendations import hooks
from acme_data.domains.recommendations.adapters import RecommendationSetValidationNormalizeRecommendationSet1Adapter
from acme_data.domains.recommendations.adapters import RecommendationSetValidationNormalizeRecommendationSet1Port
from acme_data.domains.recommendations.adapters import RecommendationSetValidationPreviewRecommendationSet0Adapter
from acme_data.domains.recommendations.dependencies import Dependencies
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class RecommendationSetValidationServicerHandlers:
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    async def CheckRecommendationSetEligibility(
        self, request: recommendations_v1_recommendation_set_validation_service_pb2.CheckRecommendationSetEligibilityRequest, context: grpc.aio.ServicerContext,
    ) -> recommendations_v1_recommendation_set_validation_service_pb2.CheckRecommendationSetEligibilityResponse:
        """Checks a recommendation set."""
        return await self.handle_check_recommendation_set_eligibility(request)

    @rpc_errors
    async def ExplainRecommendationSetDecision(
        self, request: recommendations_v1_recommendation_set_validation_service_pb2.ExplainRecommendationSetDecisionRequest, context: grpc.aio.ServicerContext,
    ) -> recommendations_v1_recommendation_set_validation_service_pb2.ExplainRecommendationSetDecisionResponse:
        """Explains a recommendation set."""
        return await self.handle_explain_recommendation_set_decision(request)

    @rpc_errors
    @retry_transient
    async def GetRecommendationSetRules(
        self, request: recommendations_v1_recommendation_set_validation_service_pb2.GetRecommendationSetRulesRequest, context: grpc.aio.ServicerContext,
    ) -> recommendations_v1_recommendation_set_validation_service_pb2.GetRecommendationSetRulesResponse:
        """Returns a recommendation set."""
        return await self.handle_get_recommendation_set_rules(request)

    @rpc_errors
    async def LintRecommendationSets(
        self, request: recommendations_v1_recommendation_set_validation_service_pb2.LintRecommendationSetsRequest, context: grpc.aio.ServicerContext,
    ) -> recommendations_v1_recommendation_set_validation_service_pb2.LintRecommendationSetsResponse:
        """Lints a recommendation set."""
        return await self.handle_lint_recommendation_sets(request)

    @rpc_errors
    async def NormalizeRecommendationSet(
        self, request: recommendations_v1_recommendation_set_validation_service_pb2.NormalizeRecommendationSetRequest, context: grpc.aio.ServicerContext,
    ) -> recommendations_v1_recommendation_set_validation_service_pb2.NormalizeRecommendationSetResponse:
        """Normalizes a recommendation set."""
        return await self.handle_normalize_recommendation_set(request)

    @rpc_errors
    async def PreviewRecommendationSet(
        self, request: recommendations_v1_recommendation_set_validation_service_pb2.PreviewRecommendationSetRequest, context: grpc.aio.ServicerContext,
    ) -> recommendations_v1_recommendation_set_validation_service_pb2.PreviewRecommendationSetResponse:
        """Previews a recommendation set."""
        return await self.handle_preview_recommendation_set(request)

    @rpc_errors
    async def ScoreRecommendationSet(
        self, request: recommendations_v1_recommendation_set_validation_service_pb2.ScoreRecommendationSetRequest, context: grpc.aio.ServicerContext,
    ) -> recommendations_v1_recommendation_set_validation_service_pb2.ScoreRecommendationSetResponse:
        """Scores a recommendation set."""
        return await self.handle_score_recommendation_set(request)

    @rpc_errors
    async def ValidateRecommendationSet(
        self, request: recommendations_v1_recommendation_set_validation_service_pb2.ValidateRecommendationSetRequest, context: grpc.aio.ServicerContext,
    ) -> recommendations_v1_recommendation_set_validation_service_pb2.ValidateRecommendationSetResponse:
        """Validates a recommendation set."""
        return await self.handle_validate_recommendation_set(request)

    async def handle_check_recommendation_set_eligibility(
        self,
        request: recommendations_v1_recommendation_set_validation_service_pb2.CheckRecommendationSetEligibilityRequest
    ) -> recommendations_v1_recommendation_set_validation_service_pb2.CheckRecommendationSetEligibilityResponse:
        """Checks a recommendation set."""
        deps = self.deps
        response = recommendations_v1_recommendation_set_validation_service_pb2.CheckRecommendationSetEligibilityResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CheckRecommendationSetEligibility', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'CheckRecommendationSetEligibility',
                {'reason': request.reason}
            )
            await deps.repository.save_recommendation_set(request.context.tenant_id, request.recommendation_set)
            response_0 = metrics_v1_dashboard_export_service_pb2.StreamDashboardExportResponse()
            response_1 = datasets_v1_dataset_service_pb2.SearchDatasetsResponse()
            response_2 = recommendations_v1_recommendation_model_calculation_service_pb2.EstimateRecommendationModelResponse()
            outgoing_0 = metrics_v1_dashboard_export_service_pb2.StreamDashboardExportRequest(
                context=request.context,
                filter=metrics_v1_dashboard_export_service_pb2.StreamDashboardExportRequest.Filter(
                    created_after=request.recommendation_set.audit.created_at,
                    owner_id=request.recommendation_set.recommendation_set_id,
                    region=request.recommendation_set.billing_address.region
                )
            )
            async for chunk_0 in deps.clients.metrics_dashboard_export.StreamDashboardExport(
                outgoing_0,
                timeout=deps.settings.timeout
            ):
                response_0 = chunk_0
            outgoing_1 = datasets_v1_dataset_service_pb2.SearchDatasetsRequest(
                context=request.context,
                filter=datasets_v1_dataset_service_pb2.SearchDatasetsRequest.Filter(
                    created_after=request.recommendation_set.due_at,
                    owner_id=request.recommendation_set.counterparty.customer_id,
                    region=request.recommendation_set.billing_address.region
                )
            )
            document_1 = MessageToJson(outgoing_1, preserving_proto_field_name=True)
            outgoing_1 = Parse(document_1, datasets_v1_dataset_service_pb2.SearchDatasetsRequest())
            response_1 = await deps.clients.datasets_dataset.SearchDatasets(outgoing_1, timeout=deps.settings.timeout)
            outgoing_2 = recommendations_v1_recommendation_model_calculation_service_pb2.EstimateRecommendationModelRequest()
            outgoing_2.context.CopyFrom(request.context)
            outgoing_2.recommendation_model.address.country_code = request.recommendation_set.billing_address.country_code
            merged_2 = recommendations_v1_recommendation_model_calculation_service_pb2.EstimateRecommendationModelRequest()
            merged_2.MergeFrom(outgoing_2)
            outgoing_2.CopyFrom(merged_2)
            response_2 = await deps.clients.recommendations_recommendation_model_calculation.EstimateRecommendationModel(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            returned_1_0 = response_1.result.status
            if returned_1_0:
                response.outcome.status = returned_1_0
            returned_2_0 = response_2.recommendation_model.address.recipient
            if returned_2_0:
                response.recommendation_set.billing_address.recipient = returned_2_0
            returned_2_1 = response_2.result.message
            if returned_2_1:
                response.result.message = returned_2_1
            echoed_0 = request.recommendation_set_id
            response.recommendation_set.recommendation_set_id = echoed_0
            echoed_1 = request.recommendation_set.due_at
            response.recommendation_set.due_at.CopyFrom(echoed_1)
            return response

    async def handle_explain_recommendation_set_decision(
        self,
        request: recommendations_v1_recommendation_set_validation_service_pb2.ExplainRecommendationSetDecisionRequest
    ) -> recommendations_v1_recommendation_set_validation_service_pb2.ExplainRecommendationSetDecisionResponse:
        """Explains a recommendation set."""
        deps = self.deps
        response = recommendations_v1_recommendation_set_validation_service_pb2.ExplainRecommendationSetDecisionResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ExplainRecommendationSetDecision', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ExplainRecommendationSetDecision',
                {'reason': request.reason}
            )
            await deps.repository.save_recommendation_set(request.context.tenant_id, request.recommendation_set)
            response_0 = metrics_v1_metric_alert_validation_service_pb2.PreviewMetricAlertResponse()
            response_1 = recommendations_v1_recommendation_model_calculation_service_pb2.CompareRecommendationModelOptionsResponse()
            requests_0: list[metrics_v1_metric_alert_validation_service_pb2.PreviewMetricAlertRequest] = []
            for item_0 in request.recommendation_set.lines:
                outgoing_0 = metrics_v1_metric_alert_validation_service_pb2.PreviewMetricAlertRequest(
                    context=request.context,
                    metric_alert=metrics_v1_metrics_pb2.MetricAlert(
                        description=item_0.description,
                        discount=metrics_v1_metrics_pb2.MetricAlertDiscountAction(amount=item_0.tax.amount)
                    )
                )
                requests_0.append(outgoing_0)
            replies_0 = await asyncio.gather(*(
                deps.clients.metrics_metric_alert_validation.PreviewMetricAlert(
                    entry,
                    timeout=deps.settings.timeout
                ) for entry in requests_0
            ))
            if replies_0:
                response_0 = replies_0[-1]
            outgoing_1 = recommendations_v1_recommendation_model_calculation_service_pb2.CompareRecommendationModelOptionsRequest(
                context=request.context,
                recommendation_model=recommendations_v1_recommendations_pb2.RecommendationModel(
                    address=common_v1_address_pb2.PostalAddress(
                        recipient=request.recommendation_set.billing_address.recipient
                    ),
                    owner=identity_v1_refs_pb2.UserRef(display_name=response_0.metric_alert.owner.display_name)
                )
            )
            registered_1 = cast(
                recommendations_v1_recommendation_model_calculation_service_pb2_grpc.RecommendationModelCalculationServiceStub,
                deps.clients.registry['acme.recommendations.v1.RecommendationModelCalculationService']
            )
            response_1 = await registered_1.CompareRecommendationModelOptions(outgoing_1, timeout=deps.settings.timeout)
            returned_1_0 = response_1.recommendation_model.audit.updated_at
            if returned_1_0.ListFields():
                response.recommendation_set.audit.updated_at.MergeFrom(returned_1_0)
            returned_1_1 = response_1.recommendation_model.audit.created_by
            if returned_1_1:
                response.recommendation_set.audit.created_by = returned_1_1
            echoed_0 = request.recommendation_set_id
            response.recommendation_set.recommendation_set_id = echoed_0
            echoed_1 = request.recommendation_set.total
            response.recommendation_set.total.CopyFrom(echoed_1)
            return response

    async def handle_get_recommendation_set_rules(
        self,
        request: recommendations_v1_recommendation_set_validation_service_pb2.GetRecommendationSetRulesRequest
    ) -> recommendations_v1_recommendation_set_validation_service_pb2.GetRecommendationSetRulesResponse:
        """Returns a recommendation set."""
        deps = self.deps
        response = recommendations_v1_recommendation_set_validation_service_pb2.GetRecommendationSetRulesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('GetRecommendationSetRules', extra={'fields': {'domain': 'recommendations'}})
            await deps.repository.audit(request.context.tenant_id, 'GetRecommendationSetRules', {})
            response_0 = modelregistry_v1_registered_model_validation_service_pb2.NormalizeRegisteredModelResponse()
            response_1 = recommendations_v1_recommendation_model_calculation_service_pb2.EstimateRecommendationModelResponse()
            outgoing_0 = modelregistry_v1_registered_model_validation_service_pb2.NormalizeRegisteredModelRequest(
                context=request.context,
                registered_model=modelregistry_v1_modelregistry_pb2.RegisteredModel(
                    owner=identity_v1_refs_pb2.UserRef(
                        email=request.context.actor.email,
                        user_id=request.context.actor.user_id
                    )
                )
            )
            response_0 = await deps.clients.modelregistry_registered_model_validation.NormalizeRegisteredModel(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = recommendations_v1_recommendation_model_calculation_service_pb2.EstimateRecommendationModelRequest()
            outgoing_1.context.CopyFrom(request.context)
            if response_0.registered_model.WhichOneof('locator') == 'address':
                outgoing_1.recommendation_model.address.recipient = response_0.registered_model.address.recipient
            outgoing_1.recommendation_model.components['primary'].component_id = response_0.registered_model.components.get(
                'primary',
                modelregistry_v1_modelregistry_pb2.RegisteredModelComponent()
            ).component_id
            outgoing_1.recommendation_model.dimensions.width = response_0.registered_model.dimensions.width
            outgoing_1.recommendation_model.dimensions.length = response_0.registered_model.dimensions.length
            response_1 = await deps.clients.recommendations_recommendation_model_calculation.EstimateRecommendationModel(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.registered_model.audit.created_by
            if returned_0_0:
                response.recommendation_set.audit.created_by = returned_0_0
            returned_0_1 = response_0.registered_model.audit.updated_at
            if returned_0_1.ListFields():
                response.recommendation_set.audit.updated_at.MergeFrom(returned_0_1)
            returned_1_0 = response_1.recommendation_model.audit.etag
            if returned_1_0:
                response.recommendation_set.audit.etag = returned_1_0
            echoed_0 = request.recommendation_set_id
            response.recommendation_set.recommendation_set_id = echoed_0
            return response

    async def handle_lint_recommendation_sets(
        self,
        request: recommendations_v1_recommendation_set_validation_service_pb2.LintRecommendationSetsRequest
    ) -> recommendations_v1_recommendation_set_validation_service_pb2.LintRecommendationSetsResponse:
        """Lints a recommendation set."""
        deps = self.deps
        response = recommendations_v1_recommendation_set_validation_service_pb2.LintRecommendationSetsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('LintRecommendationSets', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'LintRecommendationSets', {'reason': request.reason})
            await deps.repository.save_recommendation_set(request.context.tenant_id, request.recommendation_set)
            response_0 = featurestore_v1_feature_view_validation_service_pb2.ScoreFeatureViewResponse()
            response_1 = datasets_v1_data_schema_calculation_service_pb2.CalculateDataSchemaResponse()
            outgoing_0 = featurestore_v1_feature_view_validation_service_pb2.ScoreFeatureViewRequest(
                context=request.context,
                feature_view=featurestore_v1_featurestore_pb2.FeatureView(
                    address=common_v1_address_pb2.PostalAddress(
                        country_code=request.recommendation_set.billing_address.country_code,
                        recipient=request.recommendation_set.billing_address.recipient
                    )
                )
            )
            send_0 = partial(
                deps.clients.featurestore_feature_view_validation.ScoreFeatureView,
                timeout=deps.settings.timeout
            )
            response_0 = await send_0(outgoing_0)
            outgoing_1 = datasets_v1_data_schema_calculation_service_pb2.CalculateDataSchemaRequest(
                context=request.context,
                data_schema=datasets_v1_datasets_pb2.DataSchema(
                    children=[
                        datasets_v1_datasets_pb2.DataSchema(
                            children=[
                                datasets_v1_datasets_pb2.DataSchema(
                                    location=common_v1_address_pb2.PostalAddress(
                                        recipient=request.recommendation_set.billing_address.recipient
                                    )
                                )
                            ]
                        )
                    ]
                )
            )
            response_1 = await hooks.recommendation_set_validation_lint_recommendation_sets1(
                deps.clients.datasets_data_schema_calculation,
                outgoing_1,
                deps.settings.timeout
            )
            returned_0_0 = response_0.feature_view.audit.created_by
            if returned_0_0:
                response.recommendation_set.audit.created_by = returned_0_0
            returned_1_0 = response_1.data_schema.audit.created_by
            if returned_1_0:
                response.recommendation_set.audit.created_by = returned_1_0
            returned_1_1 = response_1.data_schema.audit.created_at
            if returned_1_1.ListFields():
                response.recommendation_set.audit.created_at.MergeFrom(returned_1_1)
            echoed_0 = request.recommendation_set_id
            response.recommendation_set.recommendation_set_id = echoed_0
            echoed_1 = request.recommendation_set.issued_at
            response.recommendation_set.issued_at.CopyFrom(echoed_1)
            return response

    async def handle_normalize_recommendation_set(
        self,
        request: recommendations_v1_recommendation_set_validation_service_pb2.NormalizeRecommendationSetRequest
    ) -> recommendations_v1_recommendation_set_validation_service_pb2.NormalizeRecommendationSetResponse:
        """Normalizes a recommendation set."""
        deps = self.deps
        response = recommendations_v1_recommendation_set_validation_service_pb2.NormalizeRecommendationSetResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('NormalizeRecommendationSet', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'NormalizeRecommendationSet',
                {'reason': request.reason}
            )
            await deps.repository.save_recommendation_set(request.context.tenant_id, request.recommendation_set)
            response_0 = recommendations_v1_recommendation_model_calculation_service_pb2.RecalculateRecommendationModelsResponse()
            response_1 = lineage_v1_lineage_edge_validation_service_pb2.ExplainLineageEdgeDecisionResponse()
            response_2 = metrics_v1_metric_alert_query_service_pb2.ExportMetricAlertsResponse()
            callbacks_0: list[
                Callable[
                    [],
                    Awaitable[
                        recommendations_v1_recommendation_model_calculation_service_pb2.RecalculateRecommendationModelsResponse
                    ]
                ]
            ] = []
            for item_0 in request.recommendation_set.lines:
                outgoing_0 = recommendations_v1_recommendation_model_calculation_service_pb2.RecalculateRecommendationModelsRequest(
                    context=request.context,
                    recommendation_model=recommendations_v1_recommendations_pb2.RecommendationModel(
                        components={
                            'primary': recommendations_v1_recommendations_pb2.RecommendationModelComponent(
                                description=item_0.description,
                                quantity=item_0.quantity
                            )
                        },
                        owner=identity_v1_refs_pb2.UserRef(
                            display_name=request.recommendation_set.counterparty.display_name
                        )
                    )
                )
                async def send_0(
                    payload: recommendations_v1_recommendation_model_calculation_service_pb2.RecalculateRecommendationModelsRequest = outgoing_0
                ) -> recommendations_v1_recommendation_model_calculation_service_pb2.RecalculateRecommendationModelsResponse:
                    return await deps.clients.recommendations_recommendation_model_calculation.RecalculateRecommendationModels(
                        payload,
                        timeout=deps.settings.timeout
                    )
                callbacks_0.append(send_0)
            for callback_0 in callbacks_0:
                response_0 = await callback_0()
            outgoing_1 = lineage_v1_lineage_edge_validation_service_pb2.ExplainLineageEdgeDecisionRequest(
                context=request.context,
                details=lineage_v1_lineage_edge_validation_service_pb2.ExplainLineageEdgeDecisionRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(email=response_0.recommendation_model.owner.email)
                )
            )
            port_1: RecommendationSetValidationNormalizeRecommendationSet1Port = RecommendationSetValidationNormalizeRecommendationSet1Adapter(
                deps.clients.lineage_lineage_edge_validation,
                deps.settings.timeout
            )
            response_1 = await port_1.execute(outgoing_1)
            outgoing_2 = metrics_v1_metric_alert_query_service_pb2.ExportMetricAlertsRequest(
                context=request.context,
                filter=metrics_v1_metric_alert_query_service_pb2.ExportMetricAlertsRequest.Filter(
                    region=request.recommendation_set.billing_address.region
                )
            )
            async for chunk_2 in deps.clients.metrics_metric_alert_query.ExportMetricAlerts(
                outgoing_2,
                timeout=deps.settings.timeout
            ):
                response_2 = chunk_2
            returned_1_0 = response_1.lineage_edge.correlation_id
            if returned_1_0:
                response.result.correlation_id = returned_1_0
            returned_1_1 = response_1.outcome.effective_at
            if returned_1_1.ListFields():
                response.outcome.effective_at.MergeFrom(returned_1_1)
            echoed_0 = request.recommendation_set_id
            response.recommendation_set.recommendation_set_id = echoed_0
            echoed_1 = request.recommendation_set.issued_at
            response.recommendation_set.issued_at.CopyFrom(echoed_1)
            return response

    async def handle_preview_recommendation_set(
        self,
        request: recommendations_v1_recommendation_set_validation_service_pb2.PreviewRecommendationSetRequest
    ) -> recommendations_v1_recommendation_set_validation_service_pb2.PreviewRecommendationSetResponse:
        """Previews a recommendation set."""
        deps = self.deps
        response = recommendations_v1_recommendation_set_validation_service_pb2.PreviewRecommendationSetResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('PreviewRecommendationSet', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'PreviewRecommendationSet',
                {'reason': request.reason}
            )
            await deps.repository.save_recommendation_set(request.context.tenant_id, request.recommendation_set)
            response_0 = featurestore_v1_feature_view_validation_service_pb2.ExplainFeatureViewDecisionResponse()
            response_1 = recommendations_v1_recommendation_model_calculation_service_pb2.CompareRecommendationModelOptionsResponse()
            response_2 = recommendations_v1_recommendation_model_calculation_service_pb2.EstimateRecommendationModelResponse()
            outgoing_0 = featurestore_v1_feature_view_validation_service_pb2.ExplainFeatureViewDecisionRequest(
                context=request.context,
                feature_view=featurestore_v1_featurestore_pb2.FeatureView(
                    address=common_v1_address_pb2.PostalAddress(
                        country_code=request.recommendation_set.billing_address.country_code
                    ),
                    owner=identity_v1_refs_pb2.UserRef(email=request.details.contact.email)
                )
            )
            response_0 = await RecommendationSetValidationPreviewRecommendationSet0Adapter(
                deps.clients.featurestore_feature_view_validation,
                deps.settings.timeout
            )(outgoing_0)
            outgoing_1 = recommendations_v1_recommendation_model_calculation_service_pb2.CompareRecommendationModelOptionsRequest(
                context=request.context,
                recommendation_model=recommendations_v1_recommendations_pb2.RecommendationModel(
                    address=common_v1_address_pb2.PostalAddress(
                        country_code=response_0.feature_view.address.country_code,
                        lines=list(response_0.feature_view.address.lines),
                        recipient=request.recommendation_set.billing_address.recipient
                    ),
                    audit=common_v1_audit_pb2.AuditInfo(updated_at=request.recommendation_set.audit.updated_at)
                )
            )
            response_1 = cast(recommendations_v1_recommendation_model_calculation_service_pb2.CompareRecommendationModelOptionsResponse, await deps.bus.request(
                'acme.recommendations.v1.RecommendationSetValidationService/PreviewRecommendationSet/1', outgoing_1, deps.settings.timeout,
            ))
            outgoing_2 = recommendations_v1_recommendation_model_calculation_service_pb2.EstimateRecommendationModelRequest(
                context=request.context,
                recommendation_model=recommendations_v1_recommendations_pb2.RecommendationModel(
                    owner=identity_v1_refs_pb2.UserRef(email=response_1.recommendation_model.owner.email)
                )
            )
            response_2 = await deps.clients.recommendations_recommendation_model_calculation.EstimateRecommendationModel(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.outcome.message = returned_0_0
            returned_0_1 = response_0.feature_view.address.locality
            if returned_0_1:
                response.recommendation_set.billing_address.locality = returned_0_1
            returned_1_0 = response_1.recommendation_model.address.region
            if returned_1_0:
                response.recommendation_set.billing_address.region = returned_1_0
            returned_2_0 = response_2.recommendation_model.audit.created_by
            if returned_2_0:
                response.recommendation_set.audit.created_by = returned_2_0
            returned_2_1 = response_2.recommendation_model.address.recipient
            if returned_2_1:
                response.recommendation_set.billing_address.recipient = returned_2_1
            echoed_0 = request.recommendation_set_id
            response.recommendation_set.recommendation_set_id = echoed_0
            echoed_1 = request.recommendation_set.metadata
            response.recommendation_set.metadata.update(echoed_1)
            return response

    async def handle_score_recommendation_set(
        self,
        request: recommendations_v1_recommendation_set_validation_service_pb2.ScoreRecommendationSetRequest
    ) -> recommendations_v1_recommendation_set_validation_service_pb2.ScoreRecommendationSetResponse:
        """Scores a recommendation set."""
        deps = self.deps
        response = recommendations_v1_recommendation_set_validation_service_pb2.ScoreRecommendationSetResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ScoreRecommendationSet', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'ScoreRecommendationSet', {'reason': request.reason})
            await deps.repository.save_recommendation_set(request.context.tenant_id, request.recommendation_set)
            response_0 = recommendations_v1_recommendation_model_calculation_service_pb2.CompareRecommendationModelOptionsResponse()
            outgoing_0 = recommendations_v1_recommendation_model_calculation_service_pb2.CompareRecommendationModelOptionsRequest(
                context=request.context,
                details=recommendations_v1_recommendation_model_calculation_service_pb2.CompareRecommendationModelOptionsRequest.Details(
                    destination=common_v1_address_pb2.PostalAddress(locality=request.details.destination.locality)
                ),
                recommendation_model=recommendations_v1_recommendations_pb2.RecommendationModel(
                    audit=common_v1_audit_pb2.AuditInfo(updated_at=request.recommendation_set.audit.updated_at)
                )
            )
            method_name_0 = 'CompareRecommendationModelOptions'
            response_0 = await getattr(
                deps.clients.recommendations_recommendation_model_calculation,
                method_name_0
            )(outgoing_0, timeout=deps.settings.timeout)
            returned_0_0 = response_0.recommendation_model.audit.updated_by
            if returned_0_0:
                response.recommendation_set.audit.updated_by = returned_0_0
            returned_0_1 = response_0.result.status
            if returned_0_1:
                response.result.status = returned_0_1
            echoed_0 = request.recommendation_set_id
            response.recommendation_set.recommendation_set_id = echoed_0
            echoed_1 = request.details.currency_code
            response.breakdown.currency_code = echoed_1
            return response

    async def handle_validate_recommendation_set(
        self,
        request: recommendations_v1_recommendation_set_validation_service_pb2.ValidateRecommendationSetRequest
    ) -> recommendations_v1_recommendation_set_validation_service_pb2.ValidateRecommendationSetResponse:
        """Validates a recommendation set."""
        deps = self.deps
        response = recommendations_v1_recommendation_set_validation_service_pb2.ValidateRecommendationSetResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ValidateRecommendationSet', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ValidateRecommendationSet',
                {'reason': request.reason}
            )
            await deps.repository.save_recommendation_set(request.context.tenant_id, request.recommendation_set)
            response_0 = keymanagement_v1_crypto_key_service_pb2.BatchGetCryptoKeysResponse()
            response_1 = recommendations_v1_recommendation_model_calculation_service_pb2.CompareRecommendationModelOptionsResponse()
            response_2 = ledger_v1_ledger_account_query_service_pb2.BrowseLedgerAccountsResponse()
            fields_0: dict[str, Any] = {'context': request.context}
            outgoing_0 = keymanagement_v1_crypto_key_service_pb2.BatchGetCryptoKeysRequest(**fields_0)
            response_0 = await deps.clients.keymanagement_crypto_key.BatchGetCryptoKeys(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = recommendations_v1_recommendation_model_calculation_service_pb2.CompareRecommendationModelOptionsRequest(
                context=request.context,
                recommendation_model=recommendations_v1_recommendations_pb2.RecommendationModel(
                    address=common_v1_address_pb2.PostalAddress(
                        postal_code=request.recommendation_set.billing_address.postal_code
                    ),
                    audit=common_v1_audit_pb2.AuditInfo(
                        etag=request.recommendation_set.audit.etag,
                        updated_at=request.recommendation_set.audit.updated_at,
                        updated_by=request.recommendation_set.audit.updated_by
                    )
                )
            )
            document_1 = MessageToDict(outgoing_1, preserving_proto_field_name=True)
            outgoing_1 = ParseDict(
                document_1,
                recommendations_v1_recommendation_model_calculation_service_pb2.CompareRecommendationModelOptionsRequest()
            )
            response_1 = await deps.clients.recommendations_recommendation_model_calculation.CompareRecommendationModelOptions(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = ledger_v1_ledger_account_query_service_pb2.BrowseLedgerAccountsRequest(
                context=request.context,
                filter=ledger_v1_ledger_account_query_service_pb2.BrowseLedgerAccountsRequest.Filter(
                    region=request.recommendation_set.billing_address.region
                )
            )
            document_2 = MessageToJson(outgoing_2, preserving_proto_field_name=True)
            outgoing_2 = Parse(document_2, ledger_v1_ledger_account_query_service_pb2.BrowseLedgerAccountsRequest())
            response_2 = await deps.clients.ledger_ledger_account_query.BrowseLedgerAccounts(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.outcome.message = returned_0_0
            returned_1_0 = response_1.result.message
            if returned_1_0:
                response.result.message = returned_1_0
            returned_2_0 = response_2.result.status
            if returned_2_0:
                response.result.status = returned_2_0
            returned_2_1 = response_2.result.message
            if returned_2_1:
                response.outcome.message = returned_2_1
            echoed_0 = request.recommendation_set_id
            response.recommendation_set.recommendation_set_id = echoed_0
            echoed_1 = request.recommendation_set.number
            response.recommendation_set.number = echoed_1
            return response
