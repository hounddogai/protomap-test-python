"""Reusable transport mixin for RecommendationModelValidationService."""

from __future__ import annotations

from collections.abc import AsyncIterator
from functools import partial
from typing import Any
from typing import cast
import asyncio
import logging

from google.protobuf.any_pb2 import Any as AnyMessage
from google.protobuf.json_format import MessageToDict
from google.protobuf.json_format import ParseDict
import grpc

from acme.admissions.v1 import admission_calculation_service_pb2 as admissions_v1_admission_calculation_service_pb2
from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.featurestore.v1 import (
    feature_value_validation_service_pb2 as featurestore_v1_feature_value_validation_service_pb2,
)
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.labeling.v1 import labeling_task_query_service_pb2 as labeling_v1_labeling_task_query_service_pb2
from acme.lineage.v1 import lineage_edge_query_service_pb2 as lineage_v1_lineage_edge_query_service_pb2
from acme.metrics.v1 import metric_series_notification_service_pb2 as metrics_v1_metric_series_notification_service_pb2
from acme.modelregistry.v1 import modelregistry_pb2 as modelregistry_v1_modelregistry_pb2
from acme.modelregistry.v1 import (
    registered_model_calculation_service_pb2 as modelregistry_v1_registered_model_calculation_service_pb2,
)
from acme.notifications.v1 import (
    notification_validation_service_pb2 as notifications_v1_notification_validation_service_pb2,
)
from acme.recommendations.v1 import (
    recommendation_model_calculation_service_pb2 as recommendations_v1_recommendation_model_calculation_service_pb2,
)
from acme.recommendations.v1 import (
    recommendation_model_calculation_service_pb2_grpc as recommendations_v1_recommendation_model_calculation_service_pb2_grpc,
)
from acme.recommendations.v1 import (
    recommendation_model_validation_service_pb2 as recommendations_v1_recommendation_model_validation_service_pb2,
)
from acme.recommendations.v1 import (
    recommendation_set_validation_service_pb2 as recommendations_v1_recommendation_set_validation_service_pb2,
)
from acme.recommendations.v1 import recommendations_pb2 as recommendations_v1_recommendations_pb2
from acme.search.v1 import search_index_query_service_pb2 as search_v1_search_index_query_service_pb2
from acme.sponsorships.v1 import sponsor_query_service_pb2 as sponsorships_v1_sponsor_query_service_pb2
from acme.telehealth.v1 import video_visit_query_service_pb2 as telehealth_v1_video_visit_query_service_pb2
from acme.venues.v1 import venue_validation_service_pb2 as venues_v1_venue_validation_service_pb2
from acme.venues.v1 import venues_pb2 as venues_v1_venues_pb2

from acme_data.domains.recommendations.adapters import (
    RecommendationModelValidationCheckRecommendationModelEligibility0Adapter,
)
from acme_data.domains.recommendations.adapters import (
    RecommendationModelValidationCheckRecommendationModelEligibility0Port,
)
from acme_data.domains.recommendations.dependencies import Dependencies
from acme_data.domains.recommendations.models import RecommendationModelValidationPreviewRecommendationModel1Command
from acme_data.domains.recommendations.models import RecommendationModelValidationScoreRecommendationModel0Command
from acme_data.domains.recommendations.models import (
    to_recommendation_model_validation_preview_recommendation_model1_command,
)
from acme_data.domains.recommendations.models import (
    to_recommendation_model_validation_score_recommendation_model0_command,
)
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import run_steps
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_id
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class RecommendationModelValidationServicerHandlers:
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    async def CheckRecommendationModelEligibility(
        self, request: recommendations_v1_recommendation_model_validation_service_pb2.CheckRecommendationModelEligibilityRequest, context: grpc.aio.ServicerContext,
    ) -> recommendations_v1_recommendation_model_validation_service_pb2.CheckRecommendationModelEligibilityResponse:
        """Checks a recommendation model."""
        return await self.handle_check_recommendation_model_eligibility(request)

    @rpc_errors
    async def ExplainRecommendationModelDecision(
        self, request: recommendations_v1_recommendation_model_validation_service_pb2.ExplainRecommendationModelDecisionRequest, context: grpc.aio.ServicerContext,
    ) -> recommendations_v1_recommendation_model_validation_service_pb2.ExplainRecommendationModelDecisionResponse:
        """Explains a recommendation model."""
        return await self.handle_explain_recommendation_model_decision(request)

    @rpc_errors
    @retry_transient
    async def GetRecommendationModelRules(
        self, request: recommendations_v1_recommendation_model_validation_service_pb2.GetRecommendationModelRulesRequest, context: grpc.aio.ServicerContext,
    ) -> recommendations_v1_recommendation_model_validation_service_pb2.GetRecommendationModelRulesResponse:
        """Returns a recommendation model."""
        return await self.handle_get_recommendation_model_rules(request)

    @rpc_errors
    async def NormalizeRecommendationModel(
        self, request: recommendations_v1_recommendation_model_validation_service_pb2.NormalizeRecommendationModelRequest, context: grpc.aio.ServicerContext,
    ) -> recommendations_v1_recommendation_model_validation_service_pb2.NormalizeRecommendationModelResponse:
        """Normalizes a recommendation model."""
        return await self.handle_normalize_recommendation_model(request)

    @rpc_errors
    async def PreviewRecommendationModel(
        self, request: recommendations_v1_recommendation_model_validation_service_pb2.PreviewRecommendationModelRequest, context: grpc.aio.ServicerContext,
    ) -> recommendations_v1_recommendation_model_validation_service_pb2.PreviewRecommendationModelResponse:
        """Previews a recommendation model."""
        return await self.handle_preview_recommendation_model(request)

    @rpc_errors
    async def ScoreRecommendationModel(
        self, request: recommendations_v1_recommendation_model_validation_service_pb2.ScoreRecommendationModelRequest, context: grpc.aio.ServicerContext,
    ) -> recommendations_v1_recommendation_model_validation_service_pb2.ScoreRecommendationModelResponse:
        """Scores a recommendation model."""
        return await self.handle_score_recommendation_model(request)

    @rpc_errors
    async def ValidateRecommendationModel(
        self, request: recommendations_v1_recommendation_model_validation_service_pb2.ValidateRecommendationModelRequest, context: grpc.aio.ServicerContext,
    ) -> recommendations_v1_recommendation_model_validation_service_pb2.ValidateRecommendationModelResponse:
        """Validates a recommendation model."""
        return await self.handle_validate_recommendation_model(request)

    async def handle_check_recommendation_model_eligibility(
        self,
        request: recommendations_v1_recommendation_model_validation_service_pb2.CheckRecommendationModelEligibilityRequest
    ) -> recommendations_v1_recommendation_model_validation_service_pb2.CheckRecommendationModelEligibilityResponse:
        """Checks a recommendation model."""
        deps = self.deps
        response = recommendations_v1_recommendation_model_validation_service_pb2.CheckRecommendationModelEligibilityResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CheckRecommendationModelEligibility', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'CheckRecommendationModelEligibility',
                {'reason': request.reason}
            )
            await deps.repository.save_recommendation_model(request.context.tenant_id, request.recommendation_model)
            response_0 = metrics_v1_metric_series_notification_service_pb2.SubscribeMetricSeriesUpdatesResponse()
            response_1 = recommendations_v1_recommendation_model_calculation_service_pb2.QuoteRecommendationModelResponse()
            response_2 = labeling_v1_labeling_task_query_service_pb2.ExportLabelingTasksResponse()
            response_3 = recommendations_v1_recommendation_set_validation_service_pb2.PreviewRecommendationSetResponse()
            outgoing_0 = metrics_v1_metric_series_notification_service_pb2.SubscribeMetricSeriesUpdatesRequest(
                context=request.context,
                details=metrics_v1_metric_series_notification_service_pb2.SubscribeMetricSeriesUpdatesRequest.Details(
                    recipient=common_v1_contact_pb2.ContactInfo(
                        name=request.details.contact.name,
                        phone=request.details.contact.phone,
                        preferred_channel=request.details.contact.preferred_channel
                    )
                )
            )
            port_0: RecommendationModelValidationCheckRecommendationModelEligibility0Port = RecommendationModelValidationCheckRecommendationModelEligibility0Adapter(
                deps.clients.metrics_metric_series_notification,
                deps.settings.timeout
            )
            response_0 = await port_0.execute(outgoing_0)
            outgoing_1 = recommendations_v1_recommendation_model_calculation_service_pb2.QuoteRecommendationModelRequest(
                context=request.context,
                details=recommendations_v1_recommendation_model_calculation_service_pb2.QuoteRecommendationModelRequest.Details(
                    destination=common_v1_address_pb2.PostalAddress(
                        country_code=response_0.metric_series.address.country_code
                    )
                ),
                recommendation_model=recommendations_v1_recommendations_pb2.RecommendationModel(
                    address=common_v1_address_pb2.PostalAddress(
                        postal_code=request.recommendation_model.address.postal_code
                    )
                )
            )
            steps_1 = [
                partial(
                    deps.clients.recommendations_recommendation_model_calculation.QuoteRecommendationModel,
                    outgoing_1,
                    timeout=deps.settings.timeout
                )
            ]
            results_1 = await run_steps(steps_1)
            response_1 = results_1[-1]
            outgoing_2 = labeling_v1_labeling_task_query_service_pb2.ExportLabelingTasksRequest(
                context=request.context,
                filter=labeling_v1_labeling_task_query_service_pb2.ExportLabelingTasksRequest.Filter(
                    created_after=request.recommendation_model.audit.updated_at,
                    owner_id=response_1.recommendation_model.components.get(
                        'primary',
                        recommendations_v1_recommendations_pb2.RecommendationModelComponent()
                    ).component_id,
                    region=response_0.metric_series.address.region
                )
            )
            async for chunk_2 in deps.clients.labeling_labeling_task_query.ExportLabelingTasks(
                outgoing_2,
                timeout=deps.settings.timeout
            ):
                response_2 = chunk_2
            outgoing_3 = recommendations_v1_recommendation_set_validation_service_pb2.PreviewRecommendationSetRequest()
            outgoing_3.context.CopyFrom(request.context)
            outgoing_3.recommendation_set.audit.created_by = response_1.recommendation_model.audit.created_by
            if request.recommendation_model.WhichOneof('locator') == 'address':
                outgoing_3.recommendation_set.billing_address.country_code = request.recommendation_model.address.country_code
            outgoing_3.details.contact.email = request.recommendation_model.owner.email
            if response_0.metric_series.WhichOneof('locator') == 'address':
                outgoing_3.recommendation_set.billing_address.locality = response_0.metric_series.address.locality
            response_3 = await deps.clients.recommendations_recommendation_set_validation.PreviewRecommendationSet(
                outgoing_3,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.metric_series.dimensions.height
            if returned_0_0:
                response.recommendation_model.dimensions.height = returned_0_0
            returned_1_0 = response_1.recommendation_model.owner.email
            if returned_1_0:
                response.recommendation_model.owner.email = returned_1_0
            returned_3_0 = response_3.result.message
            if returned_3_0:
                response.result.message = returned_3_0
            echoed_0 = request.recommendation_model_id
            response.recommendation_model.recommendation_model_id = echoed_0
            echoed_1 = request.recommendation_model.name
            response.recommendation_model.name = echoed_1
            return response

    async def handle_explain_recommendation_model_decision(
        self,
        request: recommendations_v1_recommendation_model_validation_service_pb2.ExplainRecommendationModelDecisionRequest
    ) -> recommendations_v1_recommendation_model_validation_service_pb2.ExplainRecommendationModelDecisionResponse:
        """Explains a recommendation model."""
        deps = self.deps
        response = recommendations_v1_recommendation_model_validation_service_pb2.ExplainRecommendationModelDecisionResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ExplainRecommendationModelDecision', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ExplainRecommendationModelDecision',
                {'reason': request.reason}
            )
            await deps.repository.save_recommendation_model(request.context.tenant_id, request.recommendation_model)
            response_0 = telehealth_v1_video_visit_query_service_pb2.SuggestVideoVisitsResponse()
            response_1 = modelregistry_v1_registered_model_calculation_service_pb2.QuoteRegisteredModelResponse()
            response_2 = modelregistry_v1_registered_model_calculation_service_pb2.CalculateRegisteredModelResponse()
            response_3 = sponsorships_v1_sponsor_query_service_pb2.SuggestSponsorsResponse()
            outgoing_0 = telehealth_v1_video_visit_query_service_pb2.SuggestVideoVisitsRequest(
                context=request.context,
                filter=telehealth_v1_video_visit_query_service_pb2.SuggestVideoVisitsRequest.Filter(
                    created_after=request.recommendation_model.audit.created_at,
                    owner_id=request.recommendation_model.components.get(
                        'primary',
                        recommendations_v1_recommendations_pb2.RecommendationModelComponent()
                    ).component_id,
                    region=request.recommendation_model.address.region
                )
            )
            outgoing_1 = modelregistry_v1_registered_model_calculation_service_pb2.QuoteRegisteredModelRequest(
                context=request.context,
                registered_model=modelregistry_v1_modelregistry_pb2.RegisteredModel(
                    audit=common_v1_audit_pb2.AuditInfo(created_by=request.recommendation_model.audit.created_by),
                    components={
                        'primary': modelregistry_v1_modelregistry_pb2.RegisteredModelComponent(
                            quantity=request.recommendation_model.components.get(
                                'primary',
                                recommendations_v1_recommendations_pb2.RecommendationModelComponent()
                            ).quantity
                        )
                    },
                    dimensions=modelregistry_v1_modelregistry_pb2.RegisteredModelDimensions(
                        height=request.recommendation_model.dimensions.height
                    )
                )
            )
            response_0, response_1 = await asyncio.gather(
                deps.clients.telehealth_video_visit_query.SuggestVideoVisits(outgoing_0, timeout=deps.settings.timeout),
                deps.clients.modelregistry_registered_model_calculation.QuoteRegisteredModel(
                    outgoing_1,
                    timeout=deps.settings.timeout
                ),
            )
            fields_2: dict[str, Any] = {
                'context': request.context,
                'registered_model': {
                    'audit': {'etag': request.recommendation_model.audit.etag},
                    'dimensions': {'weight': response_1.registered_model.dimensions.weight},
                    'owner': {'email': request.details.contact.email}
                }
            }
            outgoing_2 = modelregistry_v1_registered_model_calculation_service_pb2.CalculateRegisteredModelRequest(**fields_2)
            response_2 = await deps.clients.modelregistry_registered_model_calculation.CalculateRegisteredModel(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            outgoing_3 = sponsorships_v1_sponsor_query_service_pb2.SuggestSponsorsRequest(
                context=request.context,
                filter=sponsorships_v1_sponsor_query_service_pb2.SuggestSponsorsRequest.Filter(
                    created_after=response_2.registered_model.audit.updated_at,
                    owner_id=response_2.registered_model.components.get(
                        'primary',
                        modelregistry_v1_modelregistry_pb2.RegisteredModelComponent()
                    ).component_id,
                    region=response_2.registered_model.address.region
                )
            )
            document_3 = MessageToDict(outgoing_3, preserving_proto_field_name=True)
            outgoing_3 = ParseDict(document_3, sponsorships_v1_sponsor_query_service_pb2.SuggestSponsorsRequest())
            response_3 = await deps.clients.sponsorships_sponsor_query.SuggestSponsors(
                outgoing_3,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.outcome.message = returned_0_0
            returned_1_0 = response_1.registered_model.capacity
            if returned_1_0:
                response.recommendation_model.capacity = returned_1_0
            returned_2_0 = response_2.registered_model.tags
            response.recommendation_model.tags.extend(returned_2_0)
            returned_2_1 = response_2.result.message
            if returned_2_1:
                response.result.message = returned_2_1
            returned_3_0 = response_3.result.correlation_id
            if returned_3_0:
                response.result.correlation_id = returned_3_0
            returned_3_1 = response_3.result.status
            if returned_3_1:
                response.result.status = returned_3_1
            echoed_0 = request.recommendation_model_id
            response.recommendation_model.recommendation_model_id = echoed_0
            echoed_1 = request.recommendation_model.status
            response.recommendation_model.status = echoed_1
            return response

    async def handle_get_recommendation_model_rules(
        self,
        request: recommendations_v1_recommendation_model_validation_service_pb2.GetRecommendationModelRulesRequest
    ) -> recommendations_v1_recommendation_model_validation_service_pb2.GetRecommendationModelRulesResponse:
        """Returns a recommendation model."""
        deps = self.deps
        response = recommendations_v1_recommendation_model_validation_service_pb2.GetRecommendationModelRulesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('GetRecommendationModelRules', extra={'fields': {'domain': 'recommendations'}})
            await deps.repository.audit(request.context.tenant_id, 'GetRecommendationModelRules', {})
            response_0 = search_v1_search_index_query_service_pb2.ExportSearchIndexesResponse()
            response_1 = featurestore_v1_feature_value_validation_service_pb2.ValidateFeatureValueResponse()
            outgoing_0 = search_v1_search_index_query_service_pb2.ExportSearchIndexesRequest(
                context=request.context,
                filter=search_v1_search_index_query_service_pb2.ExportSearchIndexesRequest.Filter(
                    owner_id=request.context.actor.user_id
                )
            )
            async for chunk_0 in deps.clients.search_search_index_query.ExportSearchIndexes(
                outgoing_0,
                timeout=deps.settings.timeout
            ):
                response_0 = chunk_0
            outgoing_1 = featurestore_v1_feature_value_validation_service_pb2.ValidateFeatureValueRequest()
            outgoing_1.context.CopyFrom(request.context)
            outgoing_1.details.contact.email = request.context.actor.email
            outgoing_1.details.locale = request.context.locale
            outgoing_1.feature_value.source = request.recommendation_model_id
            outgoing_1.feature_value.occurred_at.CopyFrom(request.context.deadline)
            merged_1 = featurestore_v1_feature_value_validation_service_pb2.ValidateFeatureValueRequest()
            merged_1.MergeFrom(outgoing_1)
            outgoing_1.CopyFrom(merged_1)
            response_1 = await deps.clients.featurestore_feature_value_validation.ValidateFeatureValue(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_1_0 = response_1.result.reference_ids
            response.result.reference_ids.extend(returned_1_0)
            returned_1_1 = response_1.outcome.message
            if returned_1_1:
                response.result.message = returned_1_1
            echoed_0 = request.recommendation_model_id
            response.recommendation_model.recommendation_model_id = echoed_0
            return response

    async def handle_normalize_recommendation_model(
        self,
        request: recommendations_v1_recommendation_model_validation_service_pb2.NormalizeRecommendationModelRequest
    ) -> recommendations_v1_recommendation_model_validation_service_pb2.NormalizeRecommendationModelResponse:
        """Normalizes a recommendation model."""
        deps = self.deps
        response = recommendations_v1_recommendation_model_validation_service_pb2.NormalizeRecommendationModelResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('NormalizeRecommendationModel', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'NormalizeRecommendationModel',
                {'reason': request.reason}
            )
            await deps.repository.save_recommendation_model(request.context.tenant_id, request.recommendation_model)
            response_0 = search_v1_search_index_query_service_pb2.FindSearchIndexesResponse()
            outgoing_0 = search_v1_search_index_query_service_pb2.FindSearchIndexesRequest(
                context=request.context,
                filter=search_v1_search_index_query_service_pb2.FindSearchIndexesRequest.Filter(
                    created_after=request.recommendation_model.audit.created_at,
                    owner_id=request.recommendation_model.owner.user_id,
                    region=request.recommendation_model.address.region
                )
            )
            envelope_0 = AnyMessage()
            envelope_0.Pack(outgoing_0)
            outgoing_0 = search_v1_search_index_query_service_pb2.FindSearchIndexesRequest()
            if not envelope_0.Unpack(outgoing_0):
                raise ValueError("partner envelope contains the wrong request type")
            response_0 = await deps.clients.search_search_index_query.FindSearchIndexes(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.correlation_id
            if returned_0_0:
                response.result.correlation_id = returned_0_0
            echoed_0 = request.recommendation_model_id
            response.recommendation_model.recommendation_model_id = echoed_0
            echoed_1 = request.recommendation_model.status
            response.recommendation_model.status = echoed_1
            return response

    async def handle_preview_recommendation_model(
        self,
        request: recommendations_v1_recommendation_model_validation_service_pb2.PreviewRecommendationModelRequest
    ) -> recommendations_v1_recommendation_model_validation_service_pb2.PreviewRecommendationModelResponse:
        """Previews a recommendation model."""
        deps = self.deps
        response = recommendations_v1_recommendation_model_validation_service_pb2.PreviewRecommendationModelResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('PreviewRecommendationModel', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'PreviewRecommendationModel',
                {'reason': request.reason}
            )
            await deps.repository.save_recommendation_model(request.context.tenant_id, request.recommendation_model)
            response_0 = recommendations_v1_recommendation_model_calculation_service_pb2.SimulateRecommendationModelResponse()
            response_1 = notifications_v1_notification_validation_service_pb2.CheckNotificationEligibilityResponse()
            outgoing_0 = recommendations_v1_recommendation_model_calculation_service_pb2.SimulateRecommendationModelRequest(
                context=request.context,
                details=recommendations_v1_recommendation_model_calculation_service_pb2.SimulateRecommendationModelRequest.Details(
                    destination=common_v1_address_pb2.PostalAddress(
                        country_code=request.recommendation_model.address.country_code
                    )
                ),
                recommendation_model=recommendations_v1_recommendations_pb2.RecommendationModel(
                    audit=common_v1_audit_pb2.AuditInfo(updated_at=request.recommendation_model.audit.updated_at),
                    components={
                        'primary': recommendations_v1_recommendations_pb2.RecommendationModelComponent(
                            description=request.recommendation_model.components.get(
                                'primary',
                                recommendations_v1_recommendations_pb2.RecommendationModelComponent()
                            ).description
                        )
                    },
                    dimensions=recommendations_v1_recommendations_pb2.RecommendationModelDimensions(
                        unit=request.recommendation_model.dimensions.unit
                    )
                )
            )
            registered_0 = cast(
                recommendations_v1_recommendation_model_calculation_service_pb2_grpc.RecommendationModelCalculationServiceStub,
                deps.clients.registry['acme.recommendations.v1.RecommendationModelCalculationService']
            )
            response_0 = await registered_0.SimulateRecommendationModel(outgoing_0, timeout=deps.settings.timeout)
            command_1 = RecommendationModelValidationPreviewRecommendationModel1Command(
                context=request.context,
                notification_assignee_user_id=request.recommendation_model.owner.user_id,
                notification_audit_updated_at=response_0.recommendation_model.audit.updated_at,
                notification_customer_display_name=request.recommendation_model.owner.display_name
            )
            outgoing_1 = to_recommendation_model_validation_preview_recommendation_model1_command(command_1)
            response_1 = await deps.clients.notifications_notification_validation.CheckNotificationEligibility(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.recommendation_model.audit.etag
            if returned_0_0:
                response.recommendation_model.audit.etag = returned_0_0
            returned_1_0 = response_1.result.reference_ids
            response.result.reference_ids.extend(returned_1_0)
            returned_1_1 = response_1.outcome.status
            if returned_1_1:
                response.outcome.status = returned_1_1
            echoed_0 = request.recommendation_model_id
            response.recommendation_model.recommendation_model_id = echoed_0
            echoed_1 = request.recommendation_model.specs
            response.recommendation_model.specs.update(echoed_1)
            return response

    async def handle_score_recommendation_model(
        self,
        request: recommendations_v1_recommendation_model_validation_service_pb2.ScoreRecommendationModelRequest
    ) -> recommendations_v1_recommendation_model_validation_service_pb2.ScoreRecommendationModelResponse:
        """Scores a recommendation model."""
        deps = self.deps
        response = recommendations_v1_recommendation_model_validation_service_pb2.ScoreRecommendationModelResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ScoreRecommendationModel', extra={'fields': {'currency_code': request.details.currency_code}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ScoreRecommendationModel',
                {'currency_code': request.details.currency_code}
            )
            await deps.repository.save_recommendation_model(request.context.tenant_id, request.recommendation_model)
            response_0 = admissions_v1_admission_calculation_service_pb2.ExplainAdmissionCalculationResponse()
            response_1 = venues_v1_venue_validation_service_pb2.PreviewVenueResponse()
            command_0 = RecommendationModelValidationScoreRecommendationModel0Command.model_validate(
                {
                    'context': request.context,
                    'details_contact_email': request.recommendation_model.owner.email,
                    'admission_subject_display_name': request.recommendation_model.owner.display_name,
                    'admission_measurements_unit': request.recommendation_model.dimensions.unit,
                    'reason': request.reason
                }
            )
            outgoing_0 = to_recommendation_model_validation_score_recommendation_model0_command(command_0)
            response_0 = await deps.clients.admissions_admission_calculation.ExplainAdmissionCalculation(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = venues_v1_venue_validation_service_pb2.PreviewVenueRequest(
                context=request.context,
                venue=venues_v1_venues_pb2.Venue(
                    audit=common_v1_audit_pb2.AuditInfo(etag=request.recommendation_model.audit.etag),
                    owner=identity_v1_refs_pb2.UserRef(user_id=request.recommendation_model.owner.user_id)
                )
            )
            send_1 = partial(deps.clients.venues_venue_validation.PreviewVenue, timeout=deps.settings.timeout)
            response_1 = await send_1(outgoing_1)
            returned_0_0 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_0)
            returned_1_0 = response_1.venue.audit.created_by
            if returned_1_0:
                response.recommendation_model.audit.created_by = returned_1_0
            returned_1_1 = response_1.venue.dimensions.length
            if returned_1_1:
                response.recommendation_model.dimensions.length = returned_1_1
            echoed_0 = request.recommendation_model_id
            response.recommendation_model.recommendation_model_id = echoed_0
            echoed_1 = request.recommendation_model.specs
            response.recommendation_model.specs.update(echoed_1)
            return response

    async def handle_validate_recommendation_model(
        self,
        request: recommendations_v1_recommendation_model_validation_service_pb2.ValidateRecommendationModelRequest
    ) -> recommendations_v1_recommendation_model_validation_service_pb2.ValidateRecommendationModelResponse:
        """Validates a recommendation model."""
        deps = self.deps
        response = recommendations_v1_recommendation_model_validation_service_pb2.ValidateRecommendationModelResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ValidateRecommendationModel', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ValidateRecommendationModel',
                {'reason': request.reason}
            )
            await deps.repository.save_recommendation_model(request.context.tenant_id, request.recommendation_model)
            response_0 = lineage_v1_lineage_edge_query_service_pb2.CountLineageEdgesResponse()
            response_1 = recommendations_v1_recommendation_model_calculation_service_pb2.EstimateRecommendationModelResponse()
            outgoing_0 = lineage_v1_lineage_edge_query_service_pb2.CountLineageEdgesRequest()
            outgoing_0.context.CopyFrom(request.context)
            if request.recommendation_model.WhichOneof('locator') == 'address':
                outgoing_0.filter.region = request.recommendation_model.address.region
            response_0 = await deps.clients.lineage_lineage_edge_query.CountLineageEdges(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = recommendations_v1_recommendation_model_calculation_service_pb2.EstimateRecommendationModelRequest()
            outgoing_1.context.CopyFrom(request.context)
            outgoing_1.recommendation_model.dimensions.unit = request.recommendation_model.dimensions.unit
            outgoing_1.context.tenant_id = tenant_id.get()
            response_1 = await deps.clients.recommendations_recommendation_model_calculation.EstimateRecommendationModel(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.status
            if returned_0_0:
                response.result.status = returned_0_0
            returned_0_1 = response_0.result.status
            if returned_0_1:
                response.outcome.status = returned_0_1
            returned_1_0 = response_1.recommendation_model.category_path
            response.recommendation_model.category_path.extend(returned_1_0)
            echoed_0 = request.recommendation_model_id
            response.recommendation_model.recommendation_model_id = echoed_0
            echoed_1 = request.recommendation_model.status
            response.recommendation_model.status = echoed_1
            return response
