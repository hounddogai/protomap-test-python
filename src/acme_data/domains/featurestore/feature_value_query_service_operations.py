"""Functional operations behind FeatureValueQueryService."""

from __future__ import annotations

import logging

from google.protobuf.any_pb2 import Any as AnyMessage
from google.protobuf.json_format import MessageToJson
from google.protobuf.json_format import Parse

from acme.anomalies.v1 import anomalies_pb2 as anomalies_v1_anomalies_pb2
from acme.anomalies.v1 import anomaly_service_pb2 as anomalies_v1_anomaly_service_pb2
from acme.anomalies.v1 import detector_validation_service_pb2 as anomalies_v1_detector_validation_service_pb2
from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.customers.v1 import refs_pb2 as customers_v1_refs_pb2
from acme.featurestore.v1 import entity_calculation_service_pb2 as featurestore_v1_entity_calculation_service_pb2
from acme.featurestore.v1 import feature_value_query_service_pb2 as featurestore_v1_feature_value_query_service_pb2
from acme.featurestore.v1 import (
    feature_value_validation_service_pb2 as featurestore_v1_feature_value_validation_service_pb2,
)
from acme.featurestore.v1 import featurestore_pb2 as featurestore_v1_featurestore_pb2
from acme.identity.v1 import identity_pb2 as identity_v1_identity_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.identity.v1 import user_service_pb2 as identity_v1_user_service_pb2
from acme.lineage.v1 import impact_validation_service_pb2 as lineage_v1_impact_validation_service_pb2
from acme.lineage.v1 import lineage_edge_calculation_service_pb2 as lineage_v1_lineage_edge_calculation_service_pb2
from acme.lineage.v1 import lineage_pb2 as lineage_v1_lineage_pb2
from acme.metrics.v1 import dashboard_validation_service_pb2 as metrics_v1_dashboard_validation_service_pb2
from acme.metrics.v1 import metric_series_history_service_pb2 as metrics_v1_metric_series_history_service_pb2
from acme.metrics.v1 import metric_series_validation_service_pb2 as metrics_v1_metric_series_validation_service_pb2
from acme.metrics.v1 import metrics_pb2 as metrics_v1_metrics_pb2
from acme.search.v1 import search_index_validation_service_pb2 as search_v1_search_index_validation_service_pb2

from acme_data.domains.featurestore import hooks
from acme_data.domains.featurestore.dependencies import Dependencies
from acme_data.platform.tenancy import tenant_id
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


async def handle_browse_feature_values(
    deps: Dependencies,
    request: featurestore_v1_feature_value_query_service_pb2.BrowseFeatureValuesRequest
) -> featurestore_v1_feature_value_query_service_pb2.BrowseFeatureValuesResponse:
    """Lists feature values a page at a time."""
    response = featurestore_v1_feature_value_query_service_pb2.BrowseFeatureValuesResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('BrowseFeatureValues', extra={'fields': {'order_by': request.order_by}})
        await deps.repository.audit(request.context.tenant_id, 'BrowseFeatureValues', {'order_by': request.order_by})
        response_0 = anomalies_v1_detector_validation_service_pb2.NormalizeDetectorResponse()
        response_1 = metrics_v1_metric_series_history_service_pb2.RevertMetricSeriesResponse()
        outgoing_0 = anomalies_v1_detector_validation_service_pb2.NormalizeDetectorRequest(
            context=request.context,
            detector=anomalies_v1_anomalies_pb2.Detector(
                owner=identity_v1_refs_pb2.UserRef(email=request.context.actor.email)
            )
        )
        response_0 = await deps.clients.anomalies_detector_validation.NormalizeDetector(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = metrics_v1_metric_series_history_service_pb2.RevertMetricSeriesRequest(
            context=request.context,
            metric_series=metrics_v1_metrics_pb2.MetricSeries(
                audit=common_v1_audit_pb2.AuditInfo(updated_at=response_0.detector.audit.updated_at),
                owner=identity_v1_refs_pb2.UserRef(display_name=response_0.detector.owner.display_name)
            )
        )
        method_name_1 = 'RevertMetricSeries'
        response_1 = await getattr(
            deps.clients.metrics_metric_series_history,
            method_name_1
        )(outgoing_1, timeout=deps.settings.timeout)
        returned_0_0 = response_0.result.correlation_id
        if returned_0_0:
            response.result.correlation_id = returned_0_0
        returned_1_0 = response_1.result.correlation_id
        returned_1_0_part_0 = response.feature_values.add()
        if returned_1_0:
            returned_1_0_part_0.correlation_id = returned_1_0
        return response


async def handle_count_feature_values(
    deps: Dependencies,
    request: featurestore_v1_feature_value_query_service_pb2.CountFeatureValuesRequest
) -> featurestore_v1_feature_value_query_service_pb2.CountFeatureValuesResponse:
    """Counts feature values by status."""
    response = featurestore_v1_feature_value_query_service_pb2.CountFeatureValuesResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('CountFeatureValues', extra={'fields': {'order_by': request.order_by}})
        await deps.repository.audit(request.context.tenant_id, 'CountFeatureValues', {'order_by': request.order_by})
        response_0 = identity_v1_user_service_pb2.CreateUserResponse()
        outgoing_0 = identity_v1_user_service_pb2.CreateUserRequest(
            context=request.context,
            user=identity_v1_identity_pb2.User(
                primary_address=common_v1_address_pb2.PostalAddress(region=request.filter.region)
            )
        )
        response_0 = await deps.clients.identity_user.CreateUser(outgoing_0, timeout=deps.settings.timeout)
        returned_0_0 = response_0.result.details
        response.result.details.update(returned_0_0)
        return response


async def handle_export_feature_values(
    deps: Dependencies,
    request: featurestore_v1_feature_value_query_service_pb2.ExportFeatureValuesRequest
) -> featurestore_v1_feature_value_query_service_pb2.ExportFeatureValuesResponse:
    """Streams every matching feature value."""
    response = featurestore_v1_feature_value_query_service_pb2.ExportFeatureValuesResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('ExportFeatureValues', extra={'fields': {'destination_uri': request.destination_uri}})
        await deps.repository.audit(
            request.context.tenant_id,
            'ExportFeatureValues',
            {'destination_uri': request.destination_uri}
        )
        response_0 = lineage_v1_lineage_edge_calculation_service_pb2.CompareLineageEdgeOptionsResponse()
        response_1 = anomalies_v1_anomaly_service_pb2.BatchGetAnomaliesResponse()
        outgoing_0 = lineage_v1_lineage_edge_calculation_service_pb2.CompareLineageEdgeOptionsRequest(
            context=request.context,
            details=lineage_v1_lineage_edge_calculation_service_pb2.CompareLineageEdgeOptionsRequest.Details(
                destination=common_v1_address_pb2.PostalAddress(region=request.filter.region)
            ),
            lineage_edge=lineage_v1_lineage_pb2.LineageEdge(
                measurements=[lineage_v1_lineage_pb2.LineageEdgeMeasurement(observed_at=request.filter.created_after)]
            )
        )
        response_0 = await deps.clients.lineage_lineage_edge_calculation.CompareLineageEdgeOptions(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = anomalies_v1_anomaly_service_pb2.BatchGetAnomaliesRequest(context=request.context)
        document_1 = MessageToJson(outgoing_1, preserving_proto_field_name=True)
        outgoing_1 = Parse(document_1, anomalies_v1_anomaly_service_pb2.BatchGetAnomaliesRequest())
        response_1 = await deps.clients.anomalies_anomaly.BatchGetAnomalies(outgoing_1, timeout=deps.settings.timeout)
        returned_0_0 = response_0.result.message
        if returned_0_0:
            response.result.message = returned_0_0
        returned_1_0 = response_1.result.message
        if returned_1_0:
            response.result.message = returned_1_0
        return response


async def handle_find_feature_values(
    deps: Dependencies,
    request: featurestore_v1_feature_value_query_service_pb2.FindFeatureValuesRequest
) -> featurestore_v1_feature_value_query_service_pb2.FindFeatureValuesResponse:
    """Lists feature values a page at a time."""
    response = featurestore_v1_feature_value_query_service_pb2.FindFeatureValuesResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('FindFeatureValues', extra={'fields': {'order_by': request.order_by}})
        await deps.repository.audit(request.context.tenant_id, 'FindFeatureValues', {'order_by': request.order_by})
        response_0 = featurestore_v1_entity_calculation_service_pb2.ExplainEntityCalculationResponse()
        response_1 = featurestore_v1_feature_value_validation_service_pb2.ExplainFeatureValueDecisionResponse()
        outgoing_0 = featurestore_v1_entity_calculation_service_pb2.ExplainEntityCalculationRequest(
            context=request.context,
            entity=featurestore_v1_featurestore_pb2.Entity(
                primary_address=common_v1_address_pb2.PostalAddress(region=request.filter.region)
            )
        )
        response_0 = await deps.clients.featurestore_entity_calculation.ExplainEntityCalculation(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = featurestore_v1_feature_value_validation_service_pb2.ExplainFeatureValueDecisionRequest(
            context=request.context,
            details=featurestore_v1_feature_value_validation_service_pb2.ExplainFeatureValueDecisionRequest.Details(
                contact=common_v1_contact_pb2.ContactInfo(
                    email=response_0.entity.relationship_manager.email,
                    name=response_0.entity.contact.name,
                    phone=response_0.entity.contact.phone,
                    preferred_channel=response_0.entity.contact.preferred_channel
                )
            )
        )
        envelope_1 = AnyMessage()
        envelope_1.Pack(outgoing_1)
        outgoing_1 = featurestore_v1_feature_value_validation_service_pb2.ExplainFeatureValueDecisionRequest()
        if not envelope_1.Unpack(outgoing_1):
            raise ValueError("partner envelope contains the wrong request type")
        response_1 = await deps.clients.featurestore_feature_value_validation.ExplainFeatureValueDecision(
            outgoing_1,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.result.status
        if returned_0_0:
            response.result.status = returned_0_0
        returned_1_0 = response_1.feature_value.subject
        returned_1_0_part_0 = response.feature_values.add()
        if returned_1_0.ListFields():
            returned_1_0_part_0.subject.MergeFrom(returned_1_0)
        return response


async def handle_lookup_feature_value(
    deps: Dependencies,
    request: featurestore_v1_feature_value_query_service_pb2.LookupFeatureValueRequest
) -> featurestore_v1_feature_value_query_service_pb2.LookupFeatureValueResponse:
    """Returns a feature value."""
    response = featurestore_v1_feature_value_query_service_pb2.LookupFeatureValueResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('LookupFeatureValue', extra={'fields': {'domain': 'featurestore'}})
        await deps.repository.audit(request.context.tenant_id, 'LookupFeatureValue', {})
        response_0 = featurestore_v1_feature_value_validation_service_pb2.ExplainFeatureValueDecisionResponse()
        outgoing_0 = featurestore_v1_feature_value_validation_service_pb2.ExplainFeatureValueDecisionRequest(
            context=request.context,
            feature_value=featurestore_v1_featurestore_pb2.FeatureValue(feature_value_id=request.feature_value_id)
        )
        response_0 = await deps.clients.featurestore_feature_value_validation.ExplainFeatureValueDecision(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.outcome.status
        if returned_0_0:
            response.result.status = returned_0_0
        returned_0_1 = response_0.result.correlation_id
        if returned_0_1:
            response.result.correlation_id = returned_0_1
        echoed_0 = request.feature_value_id
        response.feature_value.feature_value_id = echoed_0
        return response


async def handle_peek_feature_value(
    deps: Dependencies,
    request: featurestore_v1_feature_value_query_service_pb2.PeekFeatureValueRequest
) -> featurestore_v1_feature_value_query_service_pb2.PeekFeatureValueResponse:
    """Returns a feature value."""
    response = featurestore_v1_feature_value_query_service_pb2.PeekFeatureValueResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('PeekFeatureValue', extra={'fields': {'locale': request.context.locale}})
        await deps.repository.audit(request.context.tenant_id, 'PeekFeatureValue', {'locale': request.context.locale})
        echoed_0 = request.feature_value_id
        response.feature_value.feature_value_id = echoed_0
        return response


async def handle_resolve_feature_values(
    deps: Dependencies,
    request: featurestore_v1_feature_value_query_service_pb2.ResolveFeatureValuesRequest
) -> featurestore_v1_feature_value_query_service_pb2.ResolveFeatureValuesResponse:
    """Returns several feature values at once."""
    response = featurestore_v1_feature_value_query_service_pb2.ResolveFeatureValuesResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('ResolveFeatureValues', extra={'fields': {'domain': 'featurestore'}})
        await deps.repository.audit(request.context.tenant_id, 'ResolveFeatureValues', {})
        response_0 = featurestore_v1_entity_calculation_service_pb2.EstimateEntityResponse()
        outgoing_0 = featurestore_v1_entity_calculation_service_pb2.EstimateEntityRequest(
            context=request.context,
            entity=featurestore_v1_featurestore_pb2.Entity(
                relationship_manager=identity_v1_refs_pb2.UserRef(email=request.context.actor.email)
            )
        )
        response_0 = await deps.clients.featurestore_entity_calculation.EstimateEntity(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.result.correlation_id
        if returned_0_0:
            response.result.correlation_id = returned_0_0
        return response


async def handle_suggest_feature_values(
    deps: Dependencies,
    request: featurestore_v1_feature_value_query_service_pb2.SuggestFeatureValuesRequest
) -> featurestore_v1_feature_value_query_service_pb2.SuggestFeatureValuesResponse:
    """Lists feature values a page at a time."""
    response = featurestore_v1_feature_value_query_service_pb2.SuggestFeatureValuesResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('SuggestFeatureValues', extra={'fields': {'order_by': request.order_by}})
        await deps.repository.audit(request.context.tenant_id, 'SuggestFeatureValues', {'order_by': request.order_by})
        response_0 = metrics_v1_dashboard_validation_service_pb2.CheckDashboardEligibilityResponse()
        outgoing_0 = metrics_v1_dashboard_validation_service_pb2.CheckDashboardEligibilityRequest(
            context=request.context,
            dashboard=metrics_v1_metrics_pb2.Dashboard(
                audit=common_v1_audit_pb2.AuditInfo(created_at=request.filter.created_after),
                billing_address=common_v1_address_pb2.PostalAddress(region=request.filter.region)
            ),
            details=metrics_v1_dashboard_validation_service_pb2.CheckDashboardEligibilityRequest.Details(
                contact=common_v1_contact_pb2.ContactInfo(email=request.context.actor.email),
                locale=request.context.locale
            )
        )
        response_0 = await deps.clients.metrics_dashboard_validation.CheckDashboardEligibility(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.result.status
        if returned_0_0:
            response.result.status = returned_0_0
        return response


async def handle_summarize_feature_values(
    deps: Dependencies,
    request: featurestore_v1_feature_value_query_service_pb2.SummarizeFeatureValuesRequest
) -> featurestore_v1_feature_value_query_service_pb2.SummarizeFeatureValuesResponse:
    """Summarizes a feature value."""
    response = featurestore_v1_feature_value_query_service_pb2.SummarizeFeatureValuesResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('SummarizeFeatureValues', extra={'fields': {'feature_value_id': request.feature_value_id}})
        await deps.repository.audit(
            request.context.tenant_id,
            'SummarizeFeatureValues',
            {'feature_value_id': request.feature_value_id}
        )
        response_0 = metrics_v1_metric_series_validation_service_pb2.ExplainMetricSeriesDecisionResponse()
        response_1 = lineage_v1_impact_validation_service_pb2.ExplainImpactDecisionResponse()
        response_2 = search_v1_search_index_validation_service_pb2.ValidateSearchIndexResponse()
        outgoing_0 = metrics_v1_metric_series_validation_service_pb2.ExplainMetricSeriesDecisionRequest(
            context=request.context,
            metric_series=metrics_v1_metrics_pb2.MetricSeries(
                owner=identity_v1_refs_pb2.UserRef(user_id=request.context.actor.user_id)
            ),
            reason=request.reason
        )
        response_0 = await deps.clients.metrics_metric_series_validation.ExplainMetricSeriesDecision(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = lineage_v1_impact_validation_service_pb2.ExplainImpactDecisionRequest(
            context=request.context,
            impact=lineage_v1_lineage_pb2.Impact(
                assignee=identity_v1_refs_pb2.UserRef(user_id=response_0.metric_series.owner.user_id),
                customer=customers_v1_refs_pb2.CustomerRef(display_name=response_0.metric_series.owner.display_name)
            )
        )
        response_1 = await hooks.feature_value_query_summarize_feature_values1(
            deps.clients.lineage_impact_validation,
            outgoing_1,
            deps.settings.timeout
        )
        outgoing_2 = search_v1_search_index_validation_service_pb2.ValidateSearchIndexRequest()
        outgoing_2.context.CopyFrom(request.context)
        outgoing_2.search_index.owner.email = response_0.metric_series.owner.email
        outgoing_2.context.tenant_id = tenant_id.get()
        response_2 = await deps.clients.search_search_index_validation.ValidateSearchIndex(
            outgoing_2,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.result.correlation_id
        if returned_0_0:
            response.result.correlation_id = returned_0_0
        returned_0_1 = response_0.outcome.message
        if returned_0_1:
            response.result.message = returned_0_1
        returned_1_0 = response_1.result.details
        response.result.details.update(returned_1_0)
        returned_1_1 = response_1.outcome.status
        if returned_1_1:
            response.result.status = returned_1_1
        returned_2_0 = response_2.result.correlation_id
        if returned_2_0:
            response.result.correlation_id = returned_2_0
        echoed_0 = request.details.period
        response.period.CopyFrom(echoed_0)
        return response
