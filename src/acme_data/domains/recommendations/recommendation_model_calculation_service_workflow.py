"""Application workflow for RecommendationModel Calculation."""

from __future__ import annotations

from functools import partial
from typing import Any
from typing import cast
import asyncio
import logging

from google.protobuf.any_pb2 import Any as AnyMessage
from google.protobuf.json_format import MessageToDict
from google.protobuf.json_format import ParseDict

from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.featureflags.v1 import feature_flag_service_pb2 as featureflags_v1_feature_flag_service_pb2
from acme.featurestore.v1 import feature_value_query_service_pb2 as featurestore_v1_feature_value_query_service_pb2
from acme.featurestore.v1 import feature_view_service_pb2 as featurestore_v1_feature_view_service_pb2
from acme.identity.v1 import identity_pb2 as identity_v1_identity_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.identity.v1 import user_validation_service_pb2 as identity_v1_user_validation_service_pb2
from acme.labeling.v1 import annotation_calculation_service_pb2 as labeling_v1_annotation_calculation_service_pb2
from acme.lineage.v1 import lineage_node_validation_service_pb2 as lineage_v1_lineage_node_validation_service_pb2
from acme.metrics.v1 import metric_alert_notification_service_pb2 as metrics_v1_metric_alert_notification_service_pb2
from acme.metrics.v1 import metric_alert_validation_service_pb2 as metrics_v1_metric_alert_validation_service_pb2
from acme.metrics.v1 import metric_series_history_service_pb2 as metrics_v1_metric_series_history_service_pb2
from acme.metrics.v1 import metric_series_query_service_pb2 as metrics_v1_metric_series_query_service_pb2
from acme.metrics.v1 import metrics_pb2 as metrics_v1_metrics_pb2
from acme.modelregistry.v1 import registered_model_service_pb2 as modelregistry_v1_registered_model_service_pb2
from acme.notifications.v1 import notification_query_service_pb2 as notifications_v1_notification_query_service_pb2
from acme.patients.v1 import patient_query_service_pb2 as patients_v1_patient_query_service_pb2
from acme.ratelimiting.v1 import (
    rate_limit_calculation_service_pb2 as ratelimiting_v1_rate_limit_calculation_service_pb2,
)
from acme.ratelimiting.v1 import ratelimiting_pb2 as ratelimiting_v1_ratelimiting_pb2
from acme.recommendations.v1 import (
    recommendation_model_calculation_service_pb2 as recommendations_v1_recommendation_model_calculation_service_pb2,
)
from acme.shows.v1 import show_calculation_service_pb2 as shows_v1_show_calculation_service_pb2
from acme.shows.v1 import show_calculation_service_pb2_grpc as shows_v1_show_calculation_service_pb2_grpc
from acme.shows.v1 import shows_pb2 as shows_v1_shows_pb2

from acme_data.domains.recommendations import hooks
from acme_data.domains.recommendations.adapters import RecommendationModelCalculationEstimateRecommendationModel1Adapter
from acme_data.domains.recommendations.adapters import RecommendationModelCalculationEstimateRecommendationModel1Port
from acme_data.domains.recommendations.dependencies import Dependencies
from acme_data.domains.recommendations.models import RecommendationModelCalculationCalculateRecommendationModel2Command
from acme_data.domains.recommendations.models import (
    to_recommendation_model_calculation_calculate_recommendation_model2_command,
)
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class RecommendationModelCalculationServicerWorkflow:
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    async def handle_calculate_recommendation_model(
        self,
        request: recommendations_v1_recommendation_model_calculation_service_pb2.CalculateRecommendationModelRequest
    ) -> recommendations_v1_recommendation_model_calculation_service_pb2.CalculateRecommendationModelResponse:
        """Calculates a recommendation model."""
        deps = self.deps
        response = recommendations_v1_recommendation_model_calculation_service_pb2.CalculateRecommendationModelResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CalculateRecommendationModel', extra={'fields': {'currency_code': request.details.currency_code}})
            await deps.repository.audit(
                request.context.tenant_id,
                'CalculateRecommendationModel',
                {'currency_code': request.details.currency_code}
            )
            await deps.repository.save_recommendation_model(request.context.tenant_id, request.recommendation_model)
            response_0 = notifications_v1_notification_query_service_pb2.SummarizeNotificationsResponse()
            response_1 = shows_v1_show_calculation_service_pb2.SimulateShowResponse()
            response_2 = labeling_v1_annotation_calculation_service_pb2.CompareAnnotationOptionsResponse()
            outgoing_0 = notifications_v1_notification_query_service_pb2.SummarizeNotificationsRequest(
                annotations=dict(request.annotations),
                context=request.context,
                details=notifications_v1_notification_query_service_pb2.SummarizeNotificationsRequest.Details(
                    filters=dict(request.recommendation_model.specs)
                ),
                reason=request.reason
            )
            envelope_0 = AnyMessage()
            envelope_0.Pack(outgoing_0)
            outgoing_0 = notifications_v1_notification_query_service_pb2.SummarizeNotificationsRequest()
            if not envelope_0.Unpack(outgoing_0):
                raise ValueError("partner envelope contains the wrong request type")
            response_0 = await deps.clients.notifications_notification_query.SummarizeNotifications(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = shows_v1_show_calculation_service_pb2.SimulateShowRequest(
                context=request.context,
                details=shows_v1_show_calculation_service_pb2.SimulateShowRequest.Details(
                    destination=common_v1_address_pb2.PostalAddress(region=request.details.destination.region)
                ),
                show=shows_v1_shows_pb2.Show(
                    audit=common_v1_audit_pb2.AuditInfo(updated_at=request.recommendation_model.audit.updated_at)
                )
            )
            registered_1 = cast(
                shows_v1_show_calculation_service_pb2_grpc.ShowCalculationServiceStub,
                deps.clients.registry['acme.shows.v1.ShowCalculationService']
            )
            response_1 = await registered_1.SimulateShow(outgoing_1, timeout=deps.settings.timeout)
            command_2 = RecommendationModelCalculationCalculateRecommendationModel2Command(
                context=request.context,
                details_destination_country_code=response_1.show.location.country_code,
                details_destination_postal_code=request.recommendation_model.address.postal_code,
                details_destination_lines=list(request.details.destination.lines),
                details_destination_locality=request.recommendation_model.address.locality
            )
            outgoing_2 = to_recommendation_model_calculation_calculate_recommendation_model2_command(command_2)
            response_2 = await deps.clients.labeling_annotation_calculation.CompareAnnotationOptions(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.correlation_id
            if returned_0_0:
                response.result.correlation_id = returned_0_0
            returned_0_1 = response_0.result.status
            if returned_0_1:
                response.result.status = returned_0_1
            returned_1_0 = response_1.show.organizer.display_name
            if returned_1_0:
                response.recommendation_model.owner.display_name = returned_1_0
            returned_2_0 = response_2.breakdown.total
            if returned_2_0.ListFields():
                response.breakdown.total.MergeFrom(returned_2_0)
            echoed_0 = request.recommendation_model_id
            response.recommendation_model.recommendation_model_id = echoed_0
            echoed_1 = request.recommendation_model.capacity
            response.recommendation_model.capacity = echoed_1
            return response

    async def handle_compare_recommendation_model_options(
        self,
        request: recommendations_v1_recommendation_model_calculation_service_pb2.CompareRecommendationModelOptionsRequest
    ) -> recommendations_v1_recommendation_model_calculation_service_pb2.CompareRecommendationModelOptionsResponse:
        """Compares a recommendation model."""
        deps = self.deps
        response = recommendations_v1_recommendation_model_calculation_service_pb2.CompareRecommendationModelOptionsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CompareRecommendationModelOptions', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'CompareRecommendationModelOptions',
                {'reason': request.reason}
            )
            await deps.repository.save_recommendation_model(request.context.tenant_id, request.recommendation_model)
            response_0 = modelregistry_v1_registered_model_service_pb2.CloneRegisteredModelResponse()
            response_1 = modelregistry_v1_registered_model_service_pb2.BatchGetRegisteredModelsResponse()
            response_2 = identity_v1_user_validation_service_pb2.CheckUserEligibilityResponse()
            outgoing_0 = modelregistry_v1_registered_model_service_pb2.CloneRegisteredModelRequest()
            outgoing_0.context.CopyFrom(request.context)
            outgoing_0.registered_model.dimensions.length = request.recommendation_model.dimensions.length
            if request.recommendation_model.WhichOneof('locator') == 'address':
                outgoing_0.registered_model.address.lines.extend(list(request.recommendation_model.address.lines))
            if request.recommendation_model.WhichOneof('locator') == 'address':
                outgoing_0.registered_model.address.postal_code = request.recommendation_model.address.postal_code
            response_0 = await deps.clients.modelregistry_registered_model.CloneRegisteredModel(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = modelregistry_v1_registered_model_service_pb2.BatchGetRegisteredModelsRequest(
                context=request.context
            )
            send_1 = partial(
                deps.clients.modelregistry_registered_model.BatchGetRegisteredModels,
                timeout=deps.settings.timeout
            )
            response_1 = await send_1(outgoing_1)
            outgoing_2 = identity_v1_user_validation_service_pb2.CheckUserEligibilityRequest(
                context=request.context,
                user=identity_v1_identity_pb2.User(
                    audit=common_v1_audit_pb2.AuditInfo(updated_by=response_0.registered_model.audit.updated_by),
                    primary_address=common_v1_address_pb2.PostalAddress(
                        country_code=request.recommendation_model.address.country_code,
                        recipient=response_0.registered_model.address.recipient
                    )
                )
            )
            response_2 = await hooks.recommendation_model_calculation_compare_recommendation_model_options2(
                deps.clients.identity_user_validation,
                outgoing_2,
                deps.settings.timeout
            )
            returned_0_0 = response_0.result.status
            if returned_0_0:
                response.result.status = returned_0_0
            returned_1_0 = response_1.result.message
            if returned_1_0:
                response.result.message = returned_1_0
            returned_1_1 = response_1.result.reference_ids
            response.result.reference_ids.extend(returned_1_1)
            returned_2_0 = response_2.outcome.message
            if returned_2_0:
                response.result.message = returned_2_0
            returned_2_1 = response_2.user.contact.email
            if returned_2_1:
                response.recommendation_model.owner.email = returned_2_1
            echoed_0 = request.recommendation_model_id
            response.recommendation_model.recommendation_model_id = echoed_0
            echoed_1 = request.recommendation_model.status
            response.recommendation_model.status = echoed_1
            return response

    async def handle_estimate_recommendation_model(
        self,
        request: recommendations_v1_recommendation_model_calculation_service_pb2.EstimateRecommendationModelRequest
    ) -> recommendations_v1_recommendation_model_calculation_service_pb2.EstimateRecommendationModelResponse:
        """Estimates a recommendation model."""
        deps = self.deps
        response = recommendations_v1_recommendation_model_calculation_service_pb2.EstimateRecommendationModelResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('EstimateRecommendationModel', extra={'fields': {'currency_code': request.details.currency_code}})
            await deps.repository.audit(
                request.context.tenant_id,
                'EstimateRecommendationModel',
                {'currency_code': request.details.currency_code}
            )
            await deps.repository.save_recommendation_model(request.context.tenant_id, request.recommendation_model)
            response_0 = notifications_v1_notification_query_service_pb2.CountNotificationsResponse()
            response_1 = featurestore_v1_feature_value_query_service_pb2.SummarizeFeatureValuesResponse()
            response_2 = metrics_v1_metric_series_history_service_pb2.ListMetricSeriesVersionsResponse()
            response_3 = patients_v1_patient_query_service_pb2.ResolvePatientsResponse()
            outgoing_0 = notifications_v1_notification_query_service_pb2.CountNotificationsRequest(
                context=request.context,
                filter=notifications_v1_notification_query_service_pb2.CountNotificationsRequest.Filter(
                    created_after=request.recommendation_model.audit.updated_at,
                    labels=dict(request.recommendation_model.specs),
                    owner_id=request.recommendation_model.owner.user_id,
                    region=request.details.destination.region
                )
            )
            outgoing_2 = metrics_v1_metric_series_history_service_pb2.ListMetricSeriesVersionsRequest(
                context=request.context,
                filter=metrics_v1_metric_series_history_service_pb2.ListMetricSeriesVersionsRequest.Filter(
                    region=request.details.destination.region
                )
            )
            outgoing_3 = patients_v1_patient_query_service_pb2.ResolvePatientsRequest(context=request.context)
            response_0, response_2, response_3 = await asyncio.gather(
                deps.clients.notifications_notification_query.CountNotifications(
                    outgoing_0,
                    timeout=deps.settings.timeout
                ),
                deps.clients.metrics_metric_series_history.ListMetricSeriesVersions(
                    outgoing_2,
                    timeout=deps.settings.timeout
                ),
                deps.clients.patients_patient_query.ResolvePatients(outgoing_3, timeout=deps.settings.timeout),
            )
            outgoing_1 = featurestore_v1_feature_value_query_service_pb2.SummarizeFeatureValuesRequest(
                annotations=dict(request.annotations),
                context=request.context,
                details=featurestore_v1_feature_value_query_service_pb2.SummarizeFeatureValuesRequest.Details(
                    filters=dict(response_0.result.details)
                ),
                reason=request.reason
            )
            port_1: RecommendationModelCalculationEstimateRecommendationModel1Port = RecommendationModelCalculationEstimateRecommendationModel1Adapter(
                deps.clients.featurestore_feature_value_query,
                deps.settings.timeout
            )
            response_1 = await port_1.execute(outgoing_1)
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.result.message = returned_0_0
            returned_0_1 = response_0.result.correlation_id
            if returned_0_1:
                response.result.correlation_id = returned_0_1
            returned_1_0 = response_1.result.details
            response.result.details.update(returned_1_0)
            returned_1_1 = response_1.result.status
            if returned_1_1:
                response.result.status = returned_1_1
            returned_2_0 = response_2.result.status
            if returned_2_0:
                response.result.status = returned_2_0
            returned_3_0 = response_3.result.message
            if returned_3_0:
                response.result.message = returned_3_0
            returned_3_1 = response_3.result.correlation_id
            if returned_3_1:
                response.result.correlation_id = returned_3_1
            echoed_0 = request.recommendation_model_id
            response.recommendation_model.recommendation_model_id = echoed_0
            echoed_1 = request.recommendation_model.owner
            response.recommendation_model.owner.CopyFrom(echoed_1)
            return response

    async def handle_quote_recommendation_model(
        self,
        request: recommendations_v1_recommendation_model_calculation_service_pb2.QuoteRecommendationModelRequest
    ) -> recommendations_v1_recommendation_model_calculation_service_pb2.QuoteRecommendationModelResponse:
        """Quotes a recommendation model."""
        deps = self.deps
        response = recommendations_v1_recommendation_model_calculation_service_pb2.QuoteRecommendationModelResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('QuoteRecommendationModel', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'QuoteRecommendationModel',
                {'reason': request.reason}
            )
            await deps.repository.save_recommendation_model(request.context.tenant_id, request.recommendation_model)
            response_0 = metrics_v1_metric_alert_validation_service_pb2.ScoreMetricAlertResponse()
            response_1 = featureflags_v1_feature_flag_service_pb2.BatchGetFeatureFlagsResponse()
            outgoing_0 = metrics_v1_metric_alert_validation_service_pb2.ScoreMetricAlertRequest(
                context=request.context,
                details=metrics_v1_metric_alert_validation_service_pb2.ScoreMetricAlertRequest.Details(
                    destination=common_v1_address_pb2.PostalAddress(
                        lines=list(request.recommendation_model.address.lines),
                        locality=request.recommendation_model.address.locality
                    )
                ),
                metric_alert=metrics_v1_metrics_pb2.MetricAlert(
                    audit=common_v1_audit_pb2.AuditInfo(updated_at=request.recommendation_model.audit.updated_at),
                    owner=identity_v1_refs_pb2.UserRef(user_id=request.recommendation_model.owner.user_id)
                )
            )
            response_0 = cast(metrics_v1_metric_alert_validation_service_pb2.ScoreMetricAlertResponse, await deps.bus.request(
                'acme.recommendations.v1.RecommendationModelCalculationService/QuoteRecommendationModel/0', outgoing_0, deps.settings.timeout,
            ))
            outgoing_1 = featureflags_v1_feature_flag_service_pb2.BatchGetFeatureFlagsRequest(context=request.context)
            response_1 = await deps.clients.featureflags_feature_flag.BatchGetFeatureFlags(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.metric_alert.description
            if returned_0_0:
                response.recommendation_model.components['primary'].description = returned_0_0
            returned_0_1 = response_0.metric_alert.owner.user_id
            if returned_0_1:
                response.recommendation_model.owner.user_id = returned_0_1
            returned_1_0 = response_1.result.correlation_id
            if returned_1_0:
                response.result.correlation_id = returned_1_0
            echoed_0 = request.recommendation_model_id
            response.recommendation_model.recommendation_model_id = echoed_0
            echoed_1 = request.recommendation_model.status
            response.recommendation_model.status = echoed_1
            return response

    async def handle_recalculate_recommendation_models(
        self,
        request: recommendations_v1_recommendation_model_calculation_service_pb2.RecalculateRecommendationModelsRequest
    ) -> recommendations_v1_recommendation_model_calculation_service_pb2.RecalculateRecommendationModelsResponse:
        """Recalculates a recommendation model."""
        deps = self.deps
        response = recommendations_v1_recommendation_model_calculation_service_pb2.RecalculateRecommendationModelsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('RecalculateRecommendationModels', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'RecalculateRecommendationModels',
                {'reason': request.reason}
            )
            await deps.repository.save_recommendation_model(request.context.tenant_id, request.recommendation_model)
            response_0 = ratelimiting_v1_rate_limit_calculation_service_pb2.EstimateRateLimitResponse()
            response_1 = lineage_v1_lineage_node_validation_service_pb2.PreviewLineageNodeResponse()
            response_2 = metrics_v1_metric_series_query_service_pb2.SuggestMetricSeriesesResponse()
            outgoing_0 = ratelimiting_v1_rate_limit_calculation_service_pb2.EstimateRateLimitRequest(
                context=request.context,
                rate_limit=ratelimiting_v1_ratelimiting_pb2.RateLimit(
                    audit=common_v1_audit_pb2.AuditInfo(etag=request.recommendation_model.audit.etag)
                )
            )
            method_name_0 = 'EstimateRateLimit'
            response_0 = await getattr(
                deps.clients.ratelimiting_rate_limit_calculation,
                method_name_0
            )(outgoing_0, timeout=deps.settings.timeout)
            fields_1: dict[str, Any] = {
                'context': request.context,
                'lineage_node': {
                    'children': [{'children': [{'manager': {'user_id': request.recommendation_model.owner.user_id}}]}]
                }
            }
            outgoing_1 = lineage_v1_lineage_node_validation_service_pb2.PreviewLineageNodeRequest(**fields_1)
            response_1 = await deps.clients.lineage_lineage_node_validation.PreviewLineageNode(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = metrics_v1_metric_series_query_service_pb2.SuggestMetricSeriesesRequest(
                context=request.context,
                filter=metrics_v1_metric_series_query_service_pb2.SuggestMetricSeriesesRequest.Filter(
                    created_after=request.recommendation_model.audit.updated_at,
                    region=request.recommendation_model.address.region
                )
            )
            document_2 = MessageToDict(outgoing_2, preserving_proto_field_name=True)
            outgoing_2 = ParseDict(
                document_2,
                metrics_v1_metric_series_query_service_pb2.SuggestMetricSeriesesRequest()
            )
            response_2 = await deps.clients.metrics_metric_series_query.SuggestMetricSerieses(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.rate_limit.discount.amount
            returned_0_0_part_1 = response.breakdown.lines.add()
            if returned_0_0.ListFields():
                returned_0_0_part_1.amount.MergeFrom(returned_0_0)
            returned_1_0 = response_1.lineage_node.name
            if returned_1_0:
                response.recommendation_model.name = returned_1_0
            returned_2_0 = response_2.result.status
            if returned_2_0:
                response.result.status = returned_2_0
            returned_2_1 = response_2.result.message
            if returned_2_1:
                response.result.message = returned_2_1
            echoed_0 = request.recommendation_model_id
            response.recommendation_model.recommendation_model_id = echoed_0
            echoed_1 = request.recommendation_model.code
            response.recommendation_model.code = echoed_1
            return response

    async def handle_simulate_recommendation_model(
        self,
        request: recommendations_v1_recommendation_model_calculation_service_pb2.SimulateRecommendationModelRequest
    ) -> recommendations_v1_recommendation_model_calculation_service_pb2.SimulateRecommendationModelResponse:
        """Simulates a recommendation model."""
        deps = self.deps
        response = recommendations_v1_recommendation_model_calculation_service_pb2.SimulateRecommendationModelResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SimulateRecommendationModel', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'SimulateRecommendationModel',
                {'reason': request.reason}
            )
            await deps.repository.save_recommendation_model(request.context.tenant_id, request.recommendation_model)
            response_0 = metrics_v1_metric_alert_notification_service_pb2.ListMetricAlertSubscriptionsResponse()
            response_1 = featurestore_v1_feature_view_service_pb2.SearchFeatureViewsResponse()
            outgoing_0 = metrics_v1_metric_alert_notification_service_pb2.ListMetricAlertSubscriptionsRequest(
                context=request.context,
                filter=metrics_v1_metric_alert_notification_service_pb2.ListMetricAlertSubscriptionsRequest.Filter(
                    region=request.recommendation_model.address.region
                )
            )
            outgoing_1 = featurestore_v1_feature_view_service_pb2.SearchFeatureViewsRequest(
                context=request.context,
                filter=featurestore_v1_feature_view_service_pb2.SearchFeatureViewsRequest.Filter(
                    created_after=request.recommendation_model.audit.created_at,
                    region=request.details.destination.region
                )
            )
            response_0, response_1 = await asyncio.gather(
                deps.clients.metrics_metric_alert_notification.ListMetricAlertSubscriptions(
                    outgoing_0,
                    timeout=deps.settings.timeout
                ),
                deps.clients.featurestore_feature_view.SearchFeatureViews(outgoing_1, timeout=deps.settings.timeout),
            )
            returned_0_0 = response_0.result.status
            if returned_0_0:
                response.result.status = returned_0_0
            returned_0_1 = response_0.result.details
            response.result.details.update(returned_0_1)
            returned_1_0 = response_1.result.details
            response.result.details.update(returned_1_0)
            returned_1_1 = response_1.result.reference_ids
            response.result.reference_ids.extend(returned_1_1)
            echoed_0 = request.recommendation_model_id
            response.recommendation_model.recommendation_model_id = echoed_0
            echoed_1 = request.recommendation_model.owner
            response.recommendation_model.owner.CopyFrom(echoed_1)
            return response
