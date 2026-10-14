"""Functional operations behind FeatureViewService."""

from __future__ import annotations

from typing import Any
import logging

from google.protobuf.any_pb2 import Any as AnyMessage
from google.protobuf.json_format import MessageToJson
from google.protobuf.json_format import Parse

from acme.anomalies.v1 import anomalies_pb2 as anomalies_v1_anomalies_pb2
from acme.anomalies.v1 import (
    anomaly_feedback_calculation_service_pb2 as anomalies_v1_anomaly_feedback_calculation_service_pb2,
)
from acme.anomalies.v1 import anomaly_service_pb2 as anomalies_v1_anomaly_service_pb2
from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.datasets.v1 import refs_pb2 as datasets_v1_refs_pb2
from acme.documents.v1 import document_service_pb2 as documents_v1_document_service_pb2
from acme.featurestore.v1 import (
    feature_value_calculation_service_pb2 as featurestore_v1_feature_value_calculation_service_pb2,
)
from acme.featurestore.v1 import (
    feature_value_validation_service_pb2 as featurestore_v1_feature_value_validation_service_pb2,
)
from acme.featurestore.v1 import (
    feature_view_calculation_service_pb2 as featurestore_v1_feature_view_calculation_service_pb2,
)
from acme.featurestore.v1 import feature_view_query_service_pb2 as featurestore_v1_feature_view_query_service_pb2
from acme.featurestore.v1 import feature_view_service_pb2 as featurestore_v1_feature_view_service_pb2
from acme.featurestore.v1 import featurestore_pb2 as featurestore_v1_featurestore_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.ledger.v1 import ledger_account_validation_service_pb2 as ledger_v1_ledger_account_validation_service_pb2
from acme.lineage.v1 import lineage_node_calculation_service_pb2 as lineage_v1_lineage_node_calculation_service_pb2
from acme.lineage.v1 import lineage_node_validation_service_pb2 as lineage_v1_lineage_node_validation_service_pb2
from acme.lineage.v1 import lineage_pb2 as lineage_v1_lineage_pb2
from acme.metrics.v1 import dashboard_validation_service_pb2 as metrics_v1_dashboard_validation_service_pb2
from acme.metrics.v1 import metrics_pb2 as metrics_v1_metrics_pb2
from acme.notifications.v1 import (
    notification_validation_service_pb2 as notifications_v1_notification_validation_service_pb2,
)
from acme.notifications.v1 import notifications_pb2 as notifications_v1_notifications_pb2
from acme.search.v1 import search_index_query_service_pb2 as search_v1_search_index_query_service_pb2
from acme.search.v1 import search_index_service_pb2 as search_v1_search_index_service_pb2
from acme.search.v1 import search_pb2 as search_v1_search_pb2
from acme.telehealth.v1 import video_visit_service_pb2 as telehealth_v1_video_visit_service_pb2

from acme_data.domains.featurestore import hooks
from acme_data.domains.featurestore.adapters import FeatureViewDeleteFeatureView1Adapter
from acme_data.domains.featurestore.adapters import FeatureViewDeleteFeatureView1Port
from acme_data.domains.featurestore.dependencies import Dependencies
from acme_data.domains.featurestore.models import FeatureViewCloneFeatureView1Command
from acme_data.domains.featurestore.models import FeatureViewCloneFeatureView2Command
from acme_data.domains.featurestore.models import to_feature_view_clone_feature_view1_command
from acme_data.domains.featurestore.models import to_feature_view_clone_feature_view2_command
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


async def handle_batch_create_feature_views(
    deps: Dependencies,
    request: featurestore_v1_feature_view_service_pb2.BatchCreateFeatureViewsRequest
) -> featurestore_v1_feature_view_service_pb2.BatchCreateFeatureViewsResponse:
    """Takes a stream of feature views and answers once at the end."""
    response = featurestore_v1_feature_view_service_pb2.BatchCreateFeatureViewsResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('BatchCreateFeatureViews', extra={'fields': {'sequence': request.sequence}})
        await deps.repository.audit(
            request.context.tenant_id,
            'BatchCreateFeatureViews',
            {'sequence': request.sequence}
        )
        if request.WhichOneof('chunk') == 'record':
            await deps.repository.save_feature_view(request.context.tenant_id, request.record)
        response_0 = featurestore_v1_feature_value_validation_service_pb2.ScoreFeatureValueResponse()
        response_1 = anomalies_v1_anomaly_service_pb2.UpdateAnomalyResponse()
        response_2 = search_v1_search_index_query_service_pb2.FindSearchIndexesResponse()
        outgoing_0 = featurestore_v1_feature_value_validation_service_pb2.ScoreFeatureValueRequest()
        outgoing_0.context.CopyFrom(request.context)
        if request.WhichOneof('chunk') == 'record':
            field_0_1_part_1 = outgoing_0.feature_value.measurements.add()
            field_0_1_part_1.unit = request.record.dimensions.unit
        if request.WhichOneof('chunk') == 'record' and request.record.WhichOneof('locator') == 'address':
            outgoing_0.details.destination.locality = request.record.address.locality
        response_0 = await deps.clients.featurestore_feature_value_validation.ScoreFeatureValue(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = anomalies_v1_anomaly_service_pb2.UpdateAnomalyRequest()
        outgoing_1.context.CopyFrom(request.context)
        outgoing_1.anomaly.assignee.email = request.header.submitted_by.email
        outgoing_1.anomaly.assignee.user_id = request.record.owner.user_id
        merged_1 = anomalies_v1_anomaly_service_pb2.UpdateAnomalyRequest()
        merged_1.MergeFrom(outgoing_1)
        outgoing_1.CopyFrom(merged_1)
        response_1 = await deps.clients.anomalies_anomaly.UpdateAnomaly(outgoing_1, timeout=deps.settings.timeout)
        outgoing_2 = search_v1_search_index_query_service_pb2.FindSearchIndexesRequest(
            context=request.context,
            filter=search_v1_search_index_query_service_pb2.FindSearchIndexesRequest.Filter(
                created_after=response_1.anomaly.audit.updated_at,
                labels=dict(response_1.anomaly.custom_fields),
                owner_id=request.record.components.get(
                    'primary',
                    featurestore_v1_featurestore_pb2.FeatureViewComponent()
                ).component_id,
                region=request.record.address.region
            )
        )
        envelope_2 = AnyMessage()
        envelope_2.Pack(outgoing_2)
        outgoing_2 = search_v1_search_index_query_service_pb2.FindSearchIndexesRequest()
        if not envelope_2.Unpack(outgoing_2):
            raise ValueError("partner envelope contains the wrong request type")
        response_2 = await deps.clients.search_search_index_query.FindSearchIndexes(
            outgoing_2,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.result.message
        if returned_0_0:
            response.result.message = returned_0_0
        returned_1_0 = response_1.result.message
        if returned_1_0:
            response.result.message = returned_1_0
        returned_1_1 = response_1.result.reference_ids
        response.result.reference_ids.extend(returned_1_1)
        returned_2_0 = response_2.result.status
        if returned_2_0:
            response.result.status = returned_2_0
        returned_2_1 = response_2.result.details
        response.result.details.update(returned_2_1)
        return response


async def handle_batch_get_feature_views(
    deps: Dependencies,
    request: featurestore_v1_feature_view_service_pb2.BatchGetFeatureViewsRequest
) -> featurestore_v1_feature_view_service_pb2.BatchGetFeatureViewsResponse:
    """Returns several feature views at once."""
    response = featurestore_v1_feature_view_service_pb2.BatchGetFeatureViewsResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('BatchGetFeatureViews', extra={'fields': {'locale': request.context.locale}})
        await deps.repository.audit(
            request.context.tenant_id,
            'BatchGetFeatureViews',
            {'locale': request.context.locale}
        )
        return response


async def handle_clone_feature_view(
    deps: Dependencies,
    request: featurestore_v1_feature_view_service_pb2.CloneFeatureViewRequest
) -> featurestore_v1_feature_view_service_pb2.CloneFeatureViewResponse:
    """Creates a feature view."""
    response = featurestore_v1_feature_view_service_pb2.CloneFeatureViewResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('CloneFeatureView', extra={'fields': {'request_id': request.request_id}})
        await deps.repository.audit(request.context.tenant_id, 'CloneFeatureView', {'request_id': request.request_id})
        await deps.repository.save_feature_view(request.context.tenant_id, request.feature_view)
        response_0 = anomalies_v1_anomaly_feedback_calculation_service_pb2.QuoteAnomalyFeedbackResponse()
        response_1 = ledger_v1_ledger_account_validation_service_pb2.ExplainLedgerAccountDecisionResponse()
        response_2 = telehealth_v1_video_visit_service_pb2.SearchVideoVisitsResponse()
        outgoing_0 = anomalies_v1_anomaly_feedback_calculation_service_pb2.QuoteAnomalyFeedbackRequest(
            anomaly_feedback=anomalies_v1_anomalies_pb2.AnomalyFeedback(
                subject=datasets_v1_refs_pb2.DatasetRef(display_name=request.feature_view.owner.display_name)
            ),
            context=request.context
        )
        response_0 = await deps.clients.anomalies_anomaly_feedback_calculation.QuoteAnomalyFeedback(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        command_1 = FeatureViewCloneFeatureView1Command(
            context=request.context,
            ledger_account_audit_updated_by=request.feature_view.audit.updated_by,
            ledger_account_audit_created_at=request.feature_view.audit.created_at
        )
        outgoing_1 = to_feature_view_clone_feature_view1_command(command_1)
        response_1 = await deps.clients.ledger_ledger_account_validation.ExplainLedgerAccountDecision(
            outgoing_1,
            timeout=deps.settings.timeout
        )
        command_2 = FeatureViewCloneFeatureView2Command.model_validate(
            {
                'context': request.context,
                'filter_labels': dict(response_1.ledger_account.labels),
                'filter_region': request.feature_view.address.region
            }
        )
        outgoing_2 = to_feature_view_clone_feature_view2_command(command_2)
        response_2 = await deps.clients.telehealth_video_visit.SearchVideoVisits(
            outgoing_2,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.anomaly_feedback.subject.code
        if returned_0_0:
            response.feature_view.code = returned_0_0
        returned_1_0 = response_1.result.message
        if returned_1_0:
            response.result.message = returned_1_0
        returned_2_0 = response_2.result.message
        if returned_2_0:
            response.result.message = returned_2_0
        echoed_0 = request.feature_view.capacity
        response.feature_view.capacity = echoed_0
        echoed_1 = request.feature_view.owner
        response.feature_view.owner.CopyFrom(echoed_1)
        return response


async def handle_create_feature_view(
    deps: Dependencies,
    request: featurestore_v1_feature_view_service_pb2.CreateFeatureViewRequest
) -> featurestore_v1_feature_view_service_pb2.CreateFeatureViewResponse:
    """Creates a feature view."""
    response = featurestore_v1_feature_view_service_pb2.CreateFeatureViewResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('CreateFeatureView', extra={'fields': {'request_id': request.request_id}})
        await deps.repository.audit(request.context.tenant_id, 'CreateFeatureView', {'request_id': request.request_id})
        await deps.repository.save_feature_view(request.context.tenant_id, request.feature_view)
        response_0 = anomalies_v1_anomaly_service_pb2.UpdateAnomalyResponse()
        response_1 = featurestore_v1_feature_view_query_service_pb2.BrowseFeatureViewsResponse()
        outgoing_0 = anomalies_v1_anomaly_service_pb2.UpdateAnomalyRequest(
            anomaly=anomalies_v1_anomalies_pb2.Anomaly(
                audit=common_v1_audit_pb2.AuditInfo(created_by=request.feature_view.audit.created_by)
            ),
            context=request.context
        )
        response_0 = await deps.clients.anomalies_anomaly.UpdateAnomaly(outgoing_0, timeout=deps.settings.timeout)
        outgoing_1 = featurestore_v1_feature_view_query_service_pb2.BrowseFeatureViewsRequest(
            context=request.context,
            filter=featurestore_v1_feature_view_query_service_pb2.BrowseFeatureViewsRequest.Filter(
                region=request.feature_view.address.region
            )
        )
        response_1 = await hooks.feature_view_create_feature_view1(
            deps.clients.featurestore_feature_view_query,
            outgoing_1,
            deps.settings.timeout
        )
        returned_0_0 = response_0.anomaly.audit.etag
        if returned_0_0:
            response.feature_view.audit.etag = returned_0_0
        returned_1_0 = response_1.result.details
        response.result.details.update(returned_1_0)
        echoed_0 = request.feature_view.specs
        response.feature_view.specs.update(echoed_0)
        echoed_1 = request.feature_view.code
        response.feature_view.code = echoed_1
        return response


async def handle_delete_feature_view(
    deps: Dependencies,
    request: featurestore_v1_feature_view_service_pb2.DeleteFeatureViewRequest
) -> featurestore_v1_feature_view_service_pb2.DeleteFeatureViewResponse:
    """Deletes a feature view."""
    response = featurestore_v1_feature_view_service_pb2.DeleteFeatureViewResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('DeleteFeatureView', extra={'fields': {'etag': request.etag}})
        await deps.repository.audit(request.context.tenant_id, 'DeleteFeatureView', {'etag': request.etag})
        response_0 = featurestore_v1_feature_value_validation_service_pb2.ExplainFeatureValueDecisionResponse()
        response_1 = documents_v1_document_service_pb2.ListDocumentsResponse()
        outgoing_0 = featurestore_v1_feature_value_validation_service_pb2.ExplainFeatureValueDecisionRequest(
            context=request.context,
            details=featurestore_v1_feature_value_validation_service_pb2.ExplainFeatureValueDecisionRequest.Details(
                contact=common_v1_contact_pb2.ContactInfo(email=request.context.actor.email)
            ),
            reason=request.reason
        )
        response_0 = await deps.clients.featurestore_feature_value_validation.ExplainFeatureValueDecision(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = documents_v1_document_service_pb2.ListDocumentsRequest(
            context=request.context,
            filter=documents_v1_document_service_pb2.ListDocumentsRequest.Filter(
                created_after=response_0.outcome.effective_at
            )
        )
        port_1: FeatureViewDeleteFeatureView1Port = FeatureViewDeleteFeatureView1Adapter(
            deps.clients.documents_document,
            deps.settings.timeout
        )
        response_1 = await port_1.execute(outgoing_1)
        returned_0_0 = response_0.result.details
        response.result.details.update(returned_0_0)
        returned_1_0 = response_1.result.correlation_id
        if returned_1_0:
            response.result.correlation_id = returned_1_0
        returned_1_1 = response_1.result.reference_ids
        response.result.reference_ids.extend(returned_1_1)
        return response


async def handle_get_feature_view(
    deps: Dependencies,
    request: featurestore_v1_feature_view_service_pb2.GetFeatureViewRequest
) -> featurestore_v1_feature_view_service_pb2.GetFeatureViewResponse:
    """Returns a feature view."""
    response = featurestore_v1_feature_view_service_pb2.GetFeatureViewResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('GetFeatureView', extra={'fields': {'domain': 'featurestore'}})
        await deps.repository.audit(request.context.tenant_id, 'GetFeatureView', {})
        response_0 = featurestore_v1_feature_value_calculation_service_pb2.EstimateFeatureValueResponse()
        outgoing_0 = featurestore_v1_feature_value_calculation_service_pb2.EstimateFeatureValueRequest(
            context=request.context,
            feature_value=featurestore_v1_featurestore_pb2.FeatureValue(
                correlation_id=request.feature_view_id,
                measurements=[
                    featurestore_v1_featurestore_pb2.FeatureValueMeasurement(observed_at=request.context.deadline)
                ],
                source=request.context.actor.user_id
            )
        )
        response_0 = await deps.clients.featurestore_feature_value_calculation.EstimateFeatureValue(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.result.message
        if returned_0_0:
            response.result.message = returned_0_0
        echoed_0 = request.feature_view_id
        response.feature_view.feature_view_id = echoed_0
        return response


async def handle_list_feature_views(
    deps: Dependencies,
    request: featurestore_v1_feature_view_service_pb2.ListFeatureViewsRequest
) -> featurestore_v1_feature_view_service_pb2.ListFeatureViewsResponse:
    """Lists feature views a page at a time."""
    response = featurestore_v1_feature_view_service_pb2.ListFeatureViewsResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('ListFeatureViews', extra={'fields': {'order_by': request.order_by}})
        await deps.repository.audit(request.context.tenant_id, 'ListFeatureViews', {'order_by': request.order_by})
        response_0 = featurestore_v1_feature_value_calculation_service_pb2.ExplainFeatureValueCalculationResponse()
        outgoing_0 = featurestore_v1_feature_value_calculation_service_pb2.ExplainFeatureValueCalculationRequest(
            context=request.context,
            details=featurestore_v1_feature_value_calculation_service_pb2.ExplainFeatureValueCalculationRequest.Details(
                contact=common_v1_contact_pb2.ContactInfo(email=request.context.actor.email)
            )
        )
        response_0 = await deps.clients.featurestore_feature_value_calculation.ExplainFeatureValueCalculation(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.result.correlation_id
        if returned_0_0:
            response.result.correlation_id = returned_0_0
        return response


async def handle_search_feature_views(
    deps: Dependencies,
    request: featurestore_v1_feature_view_service_pb2.SearchFeatureViewsRequest
) -> featurestore_v1_feature_view_service_pb2.SearchFeatureViewsResponse:
    """Lists feature views a page at a time."""
    response = featurestore_v1_feature_view_service_pb2.SearchFeatureViewsResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('SearchFeatureViews', extra={'fields': {'order_by': request.order_by}})
        await deps.repository.audit(request.context.tenant_id, 'SearchFeatureViews', {'order_by': request.order_by})
        response_0 = search_v1_search_index_service_pb2.CreateSearchIndexResponse()
        outgoing_0 = search_v1_search_index_service_pb2.CreateSearchIndexRequest(
            context=request.context,
            search_index=search_v1_search_pb2.SearchIndex(
                address=common_v1_address_pb2.PostalAddress(region=request.filter.region),
                owner=identity_v1_refs_pb2.UserRef(user_id=request.context.actor.user_id)
            )
        )
        response_0 = await deps.clients.search_search_index.CreateSearchIndex(outgoing_0, timeout=deps.settings.timeout)
        returned_0_0 = response_0.search_index.capacity
        returned_0_0_part_0 = response.feature_views.add()
        if returned_0_0:
            returned_0_0_part_0.capacity = returned_0_0
        returned_0_1 = response_0.search_index.dimensions.height
        returned_0_1_part_0 = response.feature_views.add()
        if returned_0_1:
            returned_0_1_part_0.dimensions.height = returned_0_1
        return response


async def handle_update_feature_view(
    deps: Dependencies,
    request: featurestore_v1_feature_view_service_pb2.UpdateFeatureViewRequest
) -> featurestore_v1_feature_view_service_pb2.UpdateFeatureViewResponse:
    """Changes a feature view."""
    response = featurestore_v1_feature_view_service_pb2.UpdateFeatureViewResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('UpdateFeatureView', extra={'fields': {'allow_missing': request.allow_missing}})
        await deps.repository.audit(
            request.context.tenant_id,
            'UpdateFeatureView',
            {'allow_missing': request.allow_missing}
        )
        await deps.repository.save_feature_view(request.context.tenant_id, request.feature_view)
        response_0 = notifications_v1_notification_validation_service_pb2.NormalizeNotificationResponse()
        response_1 = metrics_v1_dashboard_validation_service_pb2.CheckDashboardEligibilityResponse()
        response_2 = featurestore_v1_feature_view_calculation_service_pb2.CompareFeatureViewOptionsResponse()
        outgoing_0 = notifications_v1_notification_validation_service_pb2.NormalizeNotificationRequest(
            context=request.context,
            notification=notifications_v1_notifications_pb2.Notification(
                audit=common_v1_audit_pb2.AuditInfo(
                    created_at=request.feature_view.audit.created_at,
                    etag=request.feature_view.audit.etag,
                    updated_by=request.feature_view.audit.updated_by
                )
            )
        )
        response_0 = await deps.clients.notifications_notification_validation.NormalizeNotification(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = metrics_v1_dashboard_validation_service_pb2.CheckDashboardEligibilityRequest(
            context=request.context,
            dashboard=metrics_v1_metrics_pb2.Dashboard(
                billing_address=common_v1_address_pb2.PostalAddress(recipient=request.feature_view.address.recipient)
            )
        )
        method_name_1 = 'CheckDashboardEligibility'
        response_1 = await getattr(
            deps.clients.metrics_dashboard_validation,
            method_name_1
        )(outgoing_1, timeout=deps.settings.timeout)
        fields_2: dict[str, Any] = {
            'context': request.context,
            'feature_view': {
                'address': {'recipient': response_1.dashboard.billing_address.recipient},
                'audit': {
                    'created_by': response_0.notification.audit.created_by,
                    'updated_at': response_1.dashboard.audit.updated_at
                },
                'components': {
                    'primary': {
                        'description': request.feature_view.components.get(
                            'primary',
                            featurestore_v1_featurestore_pb2.FeatureViewComponent()
                        ).description
                    }
                }
            }
        }
        outgoing_2 = featurestore_v1_feature_view_calculation_service_pb2.CompareFeatureViewOptionsRequest(**fields_2)
        response_2 = await deps.clients.featurestore_feature_view_calculation.CompareFeatureViewOptions(
            outgoing_2,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.notification.assignee.display_name
        if returned_0_0:
            response.feature_view.owner.display_name = returned_0_0
        returned_0_1 = response_0.notification.assignee.email
        if returned_0_1:
            response.feature_view.owner.email = returned_0_1
        returned_1_0 = response_1.dashboard.counterparty.display_name
        if returned_1_0:
            response.feature_view.owner.display_name = returned_1_0
        returned_2_0 = response_2.feature_view.components.get(
            'primary',
            featurestore_v1_featurestore_pb2.FeatureViewComponent()
        ).quantity
        if returned_2_0:
            response.feature_view.components['primary'].quantity = returned_2_0
        returned_2_1 = response_2.feature_view.dimensions.height
        if returned_2_1:
            response.feature_view.dimensions.height = returned_2_1
        echoed_0 = request.feature_view.status
        response.feature_view.status = echoed_0
        echoed_1 = request.feature_view.capacity
        response.feature_view.capacity = echoed_1
        return response


async def handle_watch_feature_views(
    deps: Dependencies,
    request: featurestore_v1_feature_view_service_pb2.WatchFeatureViewsRequest
) -> featurestore_v1_feature_view_service_pb2.WatchFeatureViewsResponse:
    """Streams the changes of feature views as they happen."""
    response = featurestore_v1_feature_view_service_pb2.WatchFeatureViewsResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('WatchFeatureViews', extra={'fields': {'max_events': request.max_events}})
        await deps.repository.audit(request.context.tenant_id, 'WatchFeatureViews', {'max_events': request.max_events})
        response_0 = metrics_v1_dashboard_validation_service_pb2.PreviewDashboardResponse()
        response_1 = lineage_v1_lineage_node_validation_service_pb2.NormalizeLineageNodeResponse()
        response_2 = lineage_v1_lineage_node_calculation_service_pb2.RecalculateLineageNodesResponse()
        outgoing_0 = metrics_v1_dashboard_validation_service_pb2.PreviewDashboardRequest(
            context=request.context,
            details=metrics_v1_dashboard_validation_service_pb2.PreviewDashboardRequest.Details(
                contact=common_v1_contact_pb2.ContactInfo(email=request.subscriber.email)
            )
        )
        response_0 = await deps.clients.metrics_dashboard_validation.PreviewDashboard(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = lineage_v1_lineage_node_validation_service_pb2.NormalizeLineageNodeRequest(
            context=request.context,
            lineage_node=lineage_v1_lineage_pb2.LineageNode(
                children=[
                    lineage_v1_lineage_pb2.LineageNode(
                        children=[
                            lineage_v1_lineage_pb2.LineageNode(
                                audit=common_v1_audit_pb2.AuditInfo(
                                    created_at=response_0.dashboard.audit.created_at,
                                    etag=response_0.dashboard.audit.etag,
                                    updated_at=response_0.dashboard.audit.updated_at
                                ),
                                manager=identity_v1_refs_pb2.UserRef(
                                    display_name=response_0.dashboard.counterparty.display_name
                                )
                            )
                        ]
                    )
                ]
            )
        )
        document_1 = MessageToJson(outgoing_1, preserving_proto_field_name=True)
        outgoing_1 = Parse(document_1, lineage_v1_lineage_node_validation_service_pb2.NormalizeLineageNodeRequest())
        response_1 = await deps.clients.lineage_lineage_node_validation.NormalizeLineageNode(
            outgoing_1,
            timeout=deps.settings.timeout
        )
        outgoing_2 = lineage_v1_lineage_node_calculation_service_pb2.RecalculateLineageNodesRequest()
        outgoing_2.context.CopyFrom(request.context)
        field_2_1_part_1 = outgoing_2.lineage_node.children.add()
        field_2_1_part_2 = field_2_1_part_1.children.add()
        field_2_1_part_2.audit.updated_at.CopyFrom(response_1.lineage_node.audit.updated_at)
        field_2_2_part_1 = outgoing_2.lineage_node.children.add()
        field_2_2_part_2 = field_2_2_part_1.children.add()
        field_2_2_part_2.location.recipient = response_1.lineage_node.location.recipient
        merged_2 = lineage_v1_lineage_node_calculation_service_pb2.RecalculateLineageNodesRequest()
        merged_2.MergeFrom(outgoing_2)
        outgoing_2.CopyFrom(merged_2)
        response_2 = await deps.clients.lineage_lineage_node_calculation.RecalculateLineageNodes(
            outgoing_2,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.outcome.status
        if returned_0_0:
            response.result.status = returned_0_0
        returned_0_1 = response_0.dashboard.counterparty.display_name
        if returned_0_1:
            response.feature_view.owner.display_name = returned_0_1
        returned_1_0 = response_1.lineage_node.audit.updated_by
        if returned_1_0:
            response.feature_view.audit.updated_by = returned_1_0
        returned_1_1 = response_1.result.reference_ids
        response.result.reference_ids.extend(returned_1_1)
        returned_2_0 = response_2.lineage_node.audit.created_at
        if returned_2_0.ListFields():
            response.feature_view.audit.created_at.MergeFrom(returned_2_0)
        echoed_0 = request.subscriber.email
        response.feature_view.owner.email = echoed_0
        return response
