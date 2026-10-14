"""Functional operations behind AnalyticsEventService."""

from __future__ import annotations

from functools import partial
from typing import cast
import logging

from google.protobuf.json_format import MessageToDict
from google.protobuf.json_format import ParseDict

from acme.analytics.v1 import analytics_event_query_service_pb2 as analytics_v1_analytics_event_query_service_pb2
from acme.analytics.v1 import analytics_event_service_pb2 as analytics_v1_analytics_event_service_pb2
from acme.analytics.v1 import analytics_pb2 as analytics_v1_analytics_pb2
from acme.analytics.v1 import cohort_calculation_service_pb2 as analytics_v1_cohort_calculation_service_pb2
from acme.analytics.v1 import cohort_validation_service_pb2 as analytics_v1_cohort_validation_service_pb2
from acme.analytics.v1 import funnel_calculation_service_pb2 as analytics_v1_funnel_calculation_service_pb2
from acme.analytics.v1 import funnel_validation_service_pb2 as analytics_v1_funnel_validation_service_pb2
from acme.anomalies.v1 import anomalies_pb2 as anomalies_v1_anomalies_pb2
from acme.anomalies.v1 import anomaly_validation_service_pb2 as anomalies_v1_anomaly_validation_service_pb2
from acme.anomalies.v1 import detector_validation_service_pb2 as anomalies_v1_detector_validation_service_pb2
from acme.anomalies.v1 import refs_pb2 as anomalies_v1_refs_pb2
from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.common.v1 import paging_pb2 as common_v1_paging_pb2
from acme.concessions.v1 import concession_stand_query_service_pb2 as concessions_v1_concession_stand_query_service_pb2
from acme.featureflags.v1 import feature_flag_service_pb2 as featureflags_v1_feature_flag_service_pb2
from acme.featureflags.v1 import featureflags_pb2 as featureflags_v1_featureflags_pb2
from acme.forecasting.v1 import forecasting_pb2 as forecasting_v1_forecasting_pb2
from acme.forecasting.v1 import scenario_calculation_service_pb2 as forecasting_v1_scenario_calculation_service_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.labeling.v1 import label_set_calculation_service_pb2 as labeling_v1_label_set_calculation_service_pb2
from acme.labeling.v1 import labeling_pb2 as labeling_v1_labeling_pb2
from acme.metrics.v1 import metric_alert_validation_service_pb2 as metrics_v1_metric_alert_validation_service_pb2
from acme.metrics.v1 import metrics_pb2 as metrics_v1_metrics_pb2
from acme.modelregistry.v1 import modelregistry_pb2 as modelregistry_v1_modelregistry_pb2
from acme.modelregistry.v1 import (
    registered_model_calculation_service_pb2 as modelregistry_v1_registered_model_calculation_service_pb2,
)
from acme.recommendations.v1 import (
    recommendation_model_calculation_service_pb2 as recommendations_v1_recommendation_model_calculation_service_pb2,
)
from acme.recommendations.v1 import (
    recommendation_model_calculation_service_pb2_grpc as recommendations_v1_recommendation_model_calculation_service_pb2_grpc,
)
from acme.recommendations.v1 import recommendations_pb2 as recommendations_v1_recommendations_pb2

from acme_data.domains.analytics import hooks
from acme_data.domains.analytics.adapters import AnalyticsEventCreateAnalyticsEvent1Adapter
from acme_data.domains.analytics.adapters import AnalyticsEventCreateAnalyticsEvent1Port
from acme_data.domains.analytics.dependencies import Dependencies
from acme_data.domains.analytics.models import AnalyticsEventUpdateAnalyticsEvent1Command
from acme_data.domains.analytics.models import to_analytics_event_update_analytics_event1_command
from acme_data.platform.rpc import run_steps
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


async def handle_batch_create_analytics_events(
    deps: Dependencies,
    request: analytics_v1_analytics_event_service_pb2.BatchCreateAnalyticsEventsRequest
) -> analytics_v1_analytics_event_service_pb2.BatchCreateAnalyticsEventsResponse:
    """Takes a stream of analytics events and answers once at the end."""
    response = analytics_v1_analytics_event_service_pb2.BatchCreateAnalyticsEventsResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('BatchCreateAnalyticsEvents', extra={'fields': {'sequence': request.sequence}})
        await deps.repository.audit(
            request.context.tenant_id,
            'BatchCreateAnalyticsEvents',
            {'sequence': request.sequence}
        )
        if request.WhichOneof('chunk') == 'record':
            await deps.repository.save_analytics_event(request.context.tenant_id, request.record)
        response_0 = analytics_v1_funnel_validation_service_pb2.PreviewFunnelResponse()
        response_1 = analytics_v1_funnel_calculation_service_pb2.EstimateFunnelResponse()
        outgoing_0 = analytics_v1_funnel_validation_service_pb2.PreviewFunnelRequest(
            context=request.context,
            funnel=analytics_v1_analytics_pb2.Funnel(
                owner=identity_v1_refs_pb2.UserRef(email=request.header.submitted_by.email)
            )
        )
        response_0 = await deps.clients.analytics_funnel_validation.PreviewFunnel(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = analytics_v1_funnel_calculation_service_pb2.EstimateFunnelRequest(
            context=request.context,
            funnel=analytics_v1_analytics_pb2.Funnel(
                owner=identity_v1_refs_pb2.UserRef(
                    display_name=response_0.funnel.owner.display_name,
                    email=request.header.submitted_by.email
                ),
                route=analytics_v1_analytics_pb2.FunnelRouteAction(target=response_0.funnel.route.target)
            )
        )
        response_1 = await hooks.analytics_event_batch_create_analytics_events1(
            deps.clients.analytics_funnel_calculation,
            outgoing_1,
            deps.settings.timeout
        )
        returned_0_0 = response_0.result.correlation_id
        if returned_0_0:
            response.result.correlation_id = returned_0_0
        returned_0_1 = response_0.outcome.status
        if returned_0_1:
            response.result.status = returned_0_1
        returned_1_0 = response_1.result.correlation_id
        if returned_1_0:
            response.result.correlation_id = returned_1_0
        return response


async def handle_create_analytics_event(
    deps: Dependencies,
    request: analytics_v1_analytics_event_service_pb2.CreateAnalyticsEventRequest
) -> analytics_v1_analytics_event_service_pb2.CreateAnalyticsEventResponse:
    """Creates an analytics event."""
    response = analytics_v1_analytics_event_service_pb2.CreateAnalyticsEventResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('CreateAnalyticsEvent', extra={'fields': {'request_id': request.request_id}})
        await deps.repository.audit(
            request.context.tenant_id,
            'CreateAnalyticsEvent',
            {'request_id': request.request_id}
        )
        await deps.repository.save_analytics_event(request.context.tenant_id, request.analytics_event)
        response_0 = recommendations_v1_recommendation_model_calculation_service_pb2.RecalculateRecommendationModelsResponse()
        response_1 = analytics_v1_cohort_calculation_service_pb2.CalculateCohortResponse()
        response_2 = featureflags_v1_feature_flag_service_pb2.CreateFeatureFlagResponse()
        response_3 = metrics_v1_metric_alert_validation_service_pb2.ScoreMetricAlertResponse()
        outgoing_0 = recommendations_v1_recommendation_model_calculation_service_pb2.RecalculateRecommendationModelsRequest(
            context=request.context,
            recommendation_model=recommendations_v1_recommendations_pb2.RecommendationModel(
                components={
                    'primary': recommendations_v1_recommendations_pb2.RecommendationModelComponent(
                        component_id=request.analytics_event.subject.funnel_id
                    )
                },
                owner=identity_v1_refs_pb2.UserRef(
                    display_name=request.analytics_event.subject.display_name,
                    email=request.context.actor.email,
                    user_id=request.context.actor.user_id
                )
            )
        )
        response_0 = await deps.clients.recommendations_recommendation_model_calculation.RecalculateRecommendationModels(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = analytics_v1_cohort_calculation_service_pb2.CalculateCohortRequest(
            cohort=analytics_v1_analytics_pb2.Cohort(
                audit=common_v1_audit_pb2.AuditInfo(updated_at=response_0.recommendation_model.audit.updated_at),
                owner=identity_v1_refs_pb2.UserRef(email=response_0.recommendation_model.owner.email)
            ),
            context=request.context,
            details=analytics_v1_cohort_calculation_service_pb2.CalculateCohortRequest.Details(
                destination=common_v1_address_pb2.PostalAddress(
                    country_code=response_0.recommendation_model.address.country_code,
                    region=response_0.recommendation_model.address.region
                )
            )
        )
        port_1: AnalyticsEventCreateAnalyticsEvent1Port = AnalyticsEventCreateAnalyticsEvent1Adapter(
            deps.clients.analytics_cohort_calculation,
            deps.settings.timeout
        )
        response_1 = await port_1.execute(outgoing_1)
        outgoing_2 = featureflags_v1_feature_flag_service_pb2.CreateFeatureFlagRequest(
            context=request.context,
            feature_flag=featureflags_v1_featureflags_pb2.FeatureFlag(
                owner=identity_v1_refs_pb2.UserRef(user_id=response_1.cohort.owner.user_id),
                route=featureflags_v1_featureflags_pb2.FeatureFlagRouteAction(target=response_1.cohort.route.target)
            )
        )
        steps_2 = [
            partial(deps.clients.featureflags_feature_flag.CreateFeatureFlag, outgoing_2, timeout=deps.settings.timeout)
        ]
        results_2 = await run_steps(steps_2)
        response_2 = results_2[-1]
        outgoing_3 = metrics_v1_metric_alert_validation_service_pb2.ScoreMetricAlertRequest()
        outgoing_3.context.CopyFrom(request.context)
        outgoing_3.metric_alert.owner.email = response_1.cohort.owner.email
        outgoing_3.metric_alert.audit.etag = response_0.recommendation_model.audit.etag
        if response_1.cohort.WhichOneof('action') == 'discount':
            outgoing_3.metric_alert.discount.amount.CopyFrom(response_1.cohort.discount.amount)
        outgoing_3.metric_alert.audit.updated_at.CopyFrom(response_1.cohort.audit.updated_at)
        response_3 = await deps.clients.metrics_metric_alert_validation.ScoreMetricAlert(
            outgoing_3,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.result.message
        if returned_0_0:
            response.result.message = returned_0_0
        returned_1_0 = response_1.cohort.version
        if returned_1_0:
            response.analytics_event.subject.version = returned_1_0
        returned_1_1 = response_1.result.correlation_id
        if returned_1_1:
            response.result.correlation_id = returned_1_1
        returned_2_0 = response_2.result.correlation_id
        if returned_2_0:
            response.result.correlation_id = returned_2_0
        returned_2_1 = response_2.result.message
        if returned_2_1:
            response.result.message = returned_2_1
        returned_3_0 = response_3.metric_alert.version
        if returned_3_0:
            response.analytics_event.subject.version = returned_3_0
        echoed_0 = request.analytics_event.occurred_at
        response.analytics_event.occurred_at.CopyFrom(echoed_0)
        echoed_1 = request.analytics_event.analytics_event_id
        response.analytics_event.analytics_event_id = echoed_1
        return response


async def handle_delete_analytics_event(
    deps: Dependencies,
    request: analytics_v1_analytics_event_service_pb2.DeleteAnalyticsEventRequest
) -> analytics_v1_analytics_event_service_pb2.DeleteAnalyticsEventResponse:
    """Deletes an analytics event."""
    response = analytics_v1_analytics_event_service_pb2.DeleteAnalyticsEventResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('DeleteAnalyticsEvent', extra={'fields': {'analytics_event_id': request.analytics_event_id}})
        await deps.repository.audit(
            request.context.tenant_id,
            'DeleteAnalyticsEvent',
            {'analytics_event_id': request.analytics_event_id}
        )
        response_0 = labeling_v1_label_set_calculation_service_pb2.QuoteLabelSetResponse()
        response_1 = analytics_v1_funnel_validation_service_pb2.NormalizeFunnelResponse()
        response_2 = forecasting_v1_scenario_calculation_service_pb2.ExplainScenarioCalculationResponse()
        outgoing_0 = labeling_v1_label_set_calculation_service_pb2.QuoteLabelSetRequest(
            context=request.context,
            label_set=labeling_v1_labeling_pb2.LabelSet(
                audit=common_v1_audit_pb2.AuditInfo(etag=request.etag),
                children=[
                    labeling_v1_labeling_pb2.LabelSet(
                        children=[
                            labeling_v1_labeling_pb2.LabelSet(
                                manager=identity_v1_refs_pb2.UserRef(
                                    email=request.context.actor.email,
                                    user_id=request.context.actor.user_id
                                )
                            )
                        ]
                    )
                ]
            )
        )
        response_0 = await deps.clients.labeling_label_set_calculation.QuoteLabelSet(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = analytics_v1_funnel_validation_service_pb2.NormalizeFunnelRequest(
            context=request.context,
            funnel=analytics_v1_analytics_pb2.Funnel(
                audit=common_v1_audit_pb2.AuditInfo(created_by=response_0.label_set.audit.created_by),
                owner=identity_v1_refs_pb2.UserRef(email=response_0.label_set.manager.email)
            )
        )
        response_1 = await deps.clients.analytics_funnel_validation.NormalizeFunnel(
            outgoing_1,
            timeout=deps.settings.timeout
        )
        outgoing_2 = forecasting_v1_scenario_calculation_service_pb2.ExplainScenarioCalculationRequest(
            context=request.context,
            details=forecasting_v1_scenario_calculation_service_pb2.ExplainScenarioCalculationRequest.Details(
                contact=common_v1_contact_pb2.ContactInfo(email=response_0.label_set.manager.email)
            ),
            scenario=forecasting_v1_forecasting_pb2.Scenario(
                audit=common_v1_audit_pb2.AuditInfo(etag=response_1.funnel.audit.etag)
            )
        )
        method_name_2 = 'ExplainScenarioCalculation'
        response_2 = await getattr(
            deps.clients.forecasting_scenario_calculation,
            method_name_2
        )(outgoing_2, timeout=deps.settings.timeout)
        returned_0_0 = response_0.result.status
        if returned_0_0:
            response.result.status = returned_0_0
        returned_0_1 = response_0.result.reference_ids
        response.result.reference_ids.extend(returned_0_1)
        returned_1_0 = response_1.result.details
        response.result.details.update(returned_1_0)
        returned_2_0 = response_2.result.reference_ids
        response.result.reference_ids.extend(returned_2_0)
        return response


async def handle_get_analytics_event(
    deps: Dependencies,
    request: analytics_v1_analytics_event_service_pb2.GetAnalyticsEventRequest
) -> analytics_v1_analytics_event_service_pb2.GetAnalyticsEventResponse:
    """Returns an analytics event."""
    response = analytics_v1_analytics_event_service_pb2.GetAnalyticsEventResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('GetAnalyticsEvent', extra={'fields': {'domain': 'analytics'}})
        await deps.repository.audit(request.context.tenant_id, 'GetAnalyticsEvent', {})
        response_0 = anomalies_v1_detector_validation_service_pb2.ScoreDetectorResponse()
        response_1 = modelregistry_v1_registered_model_calculation_service_pb2.SimulateRegisteredModelResponse()
        outgoing_0 = anomalies_v1_detector_validation_service_pb2.ScoreDetectorRequest(
            context=request.context,
            detector=anomalies_v1_anomalies_pb2.Detector(
                owner=identity_v1_refs_pb2.UserRef(
                    email=request.context.actor.email,
                    user_id=request.context.actor.user_id
                )
            )
        )
        response_0 = await deps.clients.anomalies_detector_validation.ScoreDetector(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = modelregistry_v1_registered_model_calculation_service_pb2.SimulateRegisteredModelRequest(
            context=request.context,
            registered_model=modelregistry_v1_modelregistry_pb2.RegisteredModel(
                audit=common_v1_audit_pb2.AuditInfo(updated_by=response_0.detector.audit.updated_by)
            )
        )
        document_1 = MessageToDict(outgoing_1, preserving_proto_field_name=True)
        outgoing_1 = ParseDict(
            document_1,
            modelregistry_v1_registered_model_calculation_service_pb2.SimulateRegisteredModelRequest()
        )
        response_1 = await deps.clients.modelregistry_registered_model_calculation.SimulateRegisteredModel(
            outgoing_1,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.result.correlation_id
        if returned_0_0:
            response.result.correlation_id = returned_0_0
        returned_1_0 = response_1.result.reference_ids
        response.result.reference_ids.extend(returned_1_0)
        echoed_0 = request.analytics_event_id
        response.analytics_event.analytics_event_id = echoed_0
        return response


async def handle_list_analytics_events(
    deps: Dependencies,
    request: analytics_v1_analytics_event_service_pb2.ListAnalyticsEventsRequest
) -> analytics_v1_analytics_event_service_pb2.ListAnalyticsEventsResponse:
    """Lists analytics events a page at a time."""
    response = analytics_v1_analytics_event_service_pb2.ListAnalyticsEventsResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('ListAnalyticsEvents', extra={'fields': {'order_by': request.order_by}})
        await deps.repository.audit(request.context.tenant_id, 'ListAnalyticsEvents', {'order_by': request.order_by})
        response_0 = analytics_v1_analytics_event_query_service_pb2.BrowseAnalyticsEventsResponse()
        response_1 = analytics_v1_cohort_validation_service_pb2.NormalizeCohortResponse()
        outgoing_0 = analytics_v1_analytics_event_query_service_pb2.BrowseAnalyticsEventsRequest(
            context=request.context,
            filter=analytics_v1_analytics_event_query_service_pb2.BrowseAnalyticsEventsRequest.Filter(
                labels=dict(request.filter.labels),
                query=request.filter.query
            ),
            page=common_v1_paging_pb2.PageRequest(page_token=request.page.page_token)
        )
        response_0 = await deps.clients.analytics_analytics_event_query.BrowseAnalyticsEvents(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = analytics_v1_cohort_validation_service_pb2.NormalizeCohortRequest()
        outgoing_1.context.CopyFrom(request.context)
        outgoing_1.cohort.owner.email = request.context.actor.email
        merged_1 = analytics_v1_cohort_validation_service_pb2.NormalizeCohortRequest()
        merged_1.MergeFrom(outgoing_1)
        outgoing_1.CopyFrom(merged_1)
        response_1 = await deps.clients.analytics_cohort_validation.NormalizeCohort(
            outgoing_1,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.result.details
        response.result.details.update(returned_0_0)
        returned_1_0 = response_1.result.correlation_id
        returned_1_0_part_0 = response.analytics_events.add()
        if returned_1_0:
            returned_1_0_part_0.correlation_id = returned_1_0
        return response


async def handle_search_analytics_events(
    deps: Dependencies,
    request: analytics_v1_analytics_event_service_pb2.SearchAnalyticsEventsRequest
) -> analytics_v1_analytics_event_service_pb2.SearchAnalyticsEventsResponse:
    """Lists analytics events a page at a time."""
    response = analytics_v1_analytics_event_service_pb2.SearchAnalyticsEventsResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('SearchAnalyticsEvents', extra={'fields': {'order_by': request.order_by}})
        await deps.repository.audit(request.context.tenant_id, 'SearchAnalyticsEvents', {'order_by': request.order_by})
        response_0 = metrics_v1_metric_alert_validation_service_pb2.NormalizeMetricAlertResponse()
        response_1 = recommendations_v1_recommendation_model_calculation_service_pb2.SimulateRecommendationModelResponse()
        outgoing_0 = metrics_v1_metric_alert_validation_service_pb2.NormalizeMetricAlertRequest(
            context=request.context,
            details=metrics_v1_metric_alert_validation_service_pb2.NormalizeMetricAlertRequest.Details(
                contact=common_v1_contact_pb2.ContactInfo(email=request.context.actor.email),
                locale=request.context.locale
            ),
            metric_alert=metrics_v1_metrics_pb2.MetricAlert(
                audit=common_v1_audit_pb2.AuditInfo(created_at=request.filter.created_after),
                owner=identity_v1_refs_pb2.UserRef(user_id=request.context.actor.user_id)
            )
        )
        response_0 = await deps.clients.metrics_metric_alert_validation.NormalizeMetricAlert(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = recommendations_v1_recommendation_model_calculation_service_pb2.SimulateRecommendationModelRequest(
            context=request.context,
            recommendation_model=recommendations_v1_recommendations_pb2.RecommendationModel(
                audit=common_v1_audit_pb2.AuditInfo(
                    etag=response_0.metric_alert.audit.etag,
                    updated_at=response_0.metric_alert.audit.updated_at
                ),
                components={
                    'primary': recommendations_v1_recommendations_pb2.RecommendationModelComponent(
                        description=response_0.metric_alert.description
                    )
                }
            )
        )
        registered_1 = cast(
            recommendations_v1_recommendation_model_calculation_service_pb2_grpc.RecommendationModelCalculationServiceStub,
            deps.clients.registry['acme.recommendations.v1.RecommendationModelCalculationService']
        )
        response_1 = await registered_1.SimulateRecommendationModel(outgoing_1, timeout=deps.settings.timeout)
        returned_0_0 = response_0.result.correlation_id
        if returned_0_0:
            response.result.correlation_id = returned_0_0
        returned_0_1 = response_0.outcome.status
        if returned_0_1:
            response.result.status = returned_0_1
        returned_1_0 = response_1.result.message
        if returned_1_0:
            response.result.message = returned_1_0
        returned_1_1 = response_1.result.correlation_id
        returned_1_1_part_0 = response.analytics_events.add()
        if returned_1_1:
            returned_1_1_part_0.correlation_id = returned_1_1
        return response


async def handle_update_analytics_event(
    deps: Dependencies,
    request: analytics_v1_analytics_event_service_pb2.UpdateAnalyticsEventRequest
) -> analytics_v1_analytics_event_service_pb2.UpdateAnalyticsEventResponse:
    """Changes an analytics event."""
    response = analytics_v1_analytics_event_service_pb2.UpdateAnalyticsEventResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('UpdateAnalyticsEvent', extra={'fields': {'allow_missing': request.allow_missing}})
        await deps.repository.audit(
            request.context.tenant_id,
            'UpdateAnalyticsEvent',
            {'allow_missing': request.allow_missing}
        )
        await deps.repository.save_analytics_event(request.context.tenant_id, request.analytics_event)
        response_0 = anomalies_v1_anomaly_validation_service_pb2.ValidateAnomalyResponse()
        response_1 = concessions_v1_concession_stand_query_service_pb2.CountConcessionStandsResponse()
        outgoing_0 = anomalies_v1_anomaly_validation_service_pb2.ValidateAnomalyRequest(
            anomaly=anomalies_v1_anomalies_pb2.Anomaly(
                customer=anomalies_v1_refs_pb2.DetectorRef(
                    display_name=request.analytics_event.subject.display_name,
                    version=request.analytics_event.subject.version
                )
            ),
            context=request.context
        )
        response_0 = await deps.clients.anomalies_anomaly_validation.ValidateAnomaly(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        command_1 = AnalyticsEventUpdateAnalyticsEvent1Command.model_validate(
            {'context': request.context, 'filter_created_after': response_0.anomaly.audit.created_at}
        )
        outgoing_1 = to_analytics_event_update_analytics_event1_command(command_1)
        response_1 = await deps.clients.concessions_concession_stand_query.CountConcessionStands(
            outgoing_1,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.anomaly.customer.display_name
        if returned_0_0:
            response.analytics_event.subject.display_name = returned_0_0
        returned_0_1 = response_0.anomaly.customer.version
        if returned_0_1:
            response.analytics_event.subject.version = returned_0_1
        returned_1_0 = response_1.result.correlation_id
        if returned_1_0:
            response.analytics_event.correlation_id = returned_1_0
        echoed_0 = request.analytics_event.attributes
        response.analytics_event.attributes.update(echoed_0)
        echoed_1 = request.analytics_event.sequence
        response.analytics_event.sequence = echoed_1
        return response


async def handle_watch_analytics_events(
    deps: Dependencies,
    request: analytics_v1_analytics_event_service_pb2.WatchAnalyticsEventsRequest
) -> analytics_v1_analytics_event_service_pb2.WatchAnalyticsEventsResponse:
    """Streams the changes of analytics events as they happen."""
    response = analytics_v1_analytics_event_service_pb2.WatchAnalyticsEventsResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('WatchAnalyticsEvents', extra={'fields': {'max_events': request.max_events}})
        await deps.repository.audit(
            request.context.tenant_id,
            'WatchAnalyticsEvents',
            {'max_events': request.max_events}
        )
        response_0 = analytics_v1_funnel_validation_service_pb2.ValidateFunnelResponse()
        response_1 = metrics_v1_metric_alert_validation_service_pb2.ExplainMetricAlertDecisionResponse()
        outgoing_0 = analytics_v1_funnel_validation_service_pb2.ValidateFunnelRequest(
            context=request.context,
            details=analytics_v1_funnel_validation_service_pb2.ValidateFunnelRequest.Details(
                contact=common_v1_contact_pb2.ContactInfo(preferred_channel=request.subscriber.preferred_channel)
            )
        )
        response_0 = await deps.clients.analytics_funnel_validation.ValidateFunnel(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = metrics_v1_metric_alert_validation_service_pb2.ExplainMetricAlertDecisionRequest(
            context=request.context,
            metric_alert=metrics_v1_metrics_pb2.MetricAlert(
                audit=common_v1_audit_pb2.AuditInfo(etag=response_0.funnel.audit.etag),
                block=metrics_v1_metrics_pb2.MetricAlertBlockAction(
                    notify_email=response_0.funnel.block.notify_email,
                    reason=response_0.funnel.block.reason
                )
            )
        )
        response_1 = await hooks.analytics_event_watch_analytics_events1(
            deps.clients.metrics_metric_alert_validation,
            outgoing_1,
            deps.settings.timeout
        )
        returned_0_0 = response_0.result.reference_ids
        response.result.reference_ids.extend(returned_0_0)
        returned_1_0 = response_1.result.correlation_id
        if returned_1_0:
            response.analytics_event.correlation_id = returned_1_0
        return response
