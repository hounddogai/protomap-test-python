"""Application workflow for LineageEdge Lifecycle."""

from __future__ import annotations

from collections.abc import Awaitable
from collections.abc import Callable
from typing import Any
import asyncio
import logging

from google.protobuf.json_format import MessageToDict
from google.protobuf.json_format import MessageToJson
from google.protobuf.json_format import Parse
from google.protobuf.json_format import ParseDict

from acme.analytics.v1 import analytics_pb2 as analytics_v1_analytics_pb2
from acme.analytics.v1 import funnel_validation_service_pb2 as analytics_v1_funnel_validation_service_pb2
from acme.catalog.v1 import product_query_service_pb2 as catalog_v1_product_query_service_pb2
from acme.checkout.v1 import checkout_session_service_pb2 as checkout_v1_checkout_session_service_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.customers.v1 import customers_pb2 as customers_v1_customers_pb2
from acme.customers.v1 import household_calculation_service_pb2 as customers_v1_household_calculation_service_pb2
from acme.customers.v1 import preference_validation_service_pb2 as customers_v1_preference_validation_service_pb2
from acme.customers.v1 import refs_pb2 as customers_v1_refs_pb2
from acme.featureflags.v1 import feature_flag_service_pb2 as featureflags_v1_feature_flag_service_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.lineage.v1 import lineage_edge_calculation_service_pb2 as lineage_v1_lineage_edge_calculation_service_pb2
from acme.lineage.v1 import lineage_edge_import_service_pb2 as lineage_v1_lineage_edge_import_service_pb2
from acme.lineage.v1 import lineage_edge_lifecycle_service_pb2 as lineage_v1_lineage_edge_lifecycle_service_pb2
from acme.lineage.v1 import lineage_edge_reporting_service_pb2 as lineage_v1_lineage_edge_reporting_service_pb2
from acme.lineage.v1 import lineage_node_reporting_service_pb2 as lineage_v1_lineage_node_reporting_service_pb2
from acme.lineage.v1 import lineage_node_sync_service_pb2 as lineage_v1_lineage_node_sync_service_pb2
from acme.lineage.v1 import lineage_pb2 as lineage_v1_lineage_pb2
from acme.notifications.v1 import notification_service_pb2 as notifications_v1_notification_service_pb2
from acme.recommendations.v1 import (
    interaction_validation_service_pb2 as recommendations_v1_interaction_validation_service_pb2,
)
from acme.recommendations.v1 import (
    recommendation_model_validation_service_pb2 as recommendations_v1_recommendation_model_validation_service_pb2,
)
from acme.recommendations.v1 import recommendations_pb2 as recommendations_v1_recommendations_pb2

from acme_data.domains.lineage import hooks
from acme_data.domains.lineage.adapters import LineageEdgeLifecycleScheduleLineageEdgeExpiry0Adapter
from acme_data.domains.lineage.dependencies import Dependencies
from acme_data.domains.lineage.models import LineageEdgeLifecycleExpireLineageEdge1Command
from acme_data.domains.lineage.models import to_lineage_edge_lifecycle_expire_lineage_edge1_command
from acme_data.platform.rpc import async_messages
from acme_data.platform.tenancy import tenant_id
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class LineageEdgeLifecycleServicerWorkflow:
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    async def handle_activate_lineage_edge(
        self,
        request: lineage_v1_lineage_edge_lifecycle_service_pb2.ActivateLineageEdgeRequest
    ) -> lineage_v1_lineage_edge_lifecycle_service_pb2.ActivateLineageEdgeResponse:
        """Activates a lineage edge."""
        deps = self.deps
        response = lineage_v1_lineage_edge_lifecycle_service_pb2.ActivateLineageEdgeResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ActivateLineageEdge', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'ActivateLineageEdge', {'reason': request.reason})
            response_0 = lineage_v1_lineage_edge_import_service_pb2.MapLineageEdgeImportColumnsResponse()
            response_1 = customers_v1_household_calculation_service_pb2.ExplainHouseholdCalculationResponse()
            response_2 = checkout_v1_checkout_session_service_pb2.WatchCheckoutSessionsResponse()
            outgoing_0 = lineage_v1_lineage_edge_import_service_pb2.MapLineageEdgeImportColumnsRequest(
                context=request.context,
                details=lineage_v1_lineage_edge_import_service_pb2.MapLineageEdgeImportColumnsRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(
                        email=request.details.new_owner.email,
                        phone=request.details.notify_contact.phone,
                        preferred_channel=request.details.notify_contact.preferred_channel
                    )
                )
            )
            document_0 = MessageToJson(outgoing_0, preserving_proto_field_name=True)
            outgoing_0 = Parse(
                document_0,
                lineage_v1_lineage_edge_import_service_pb2.MapLineageEdgeImportColumnsRequest()
            )
            response_0 = await deps.clients.lineage_lineage_edge_import.MapLineageEdgeImportColumns(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = customers_v1_household_calculation_service_pb2.ExplainHouseholdCalculationRequest()
            outgoing_1.context.CopyFrom(request.context)
            field_1_1_part_1 = outgoing_1.household.children.add()
            field_1_1_part_2 = field_1_1_part_1.children.add()
            field_1_1_part_2.manager.display_name = response_0.lineage_edge.subject.display_name
            field_1_2_part_1 = outgoing_1.household.children.add()
            field_1_2_part_1.manager.email = request.details.notify_contact.email
            merged_1 = customers_v1_household_calculation_service_pb2.ExplainHouseholdCalculationRequest()
            merged_1.MergeFrom(outgoing_1)
            outgoing_1.CopyFrom(merged_1)
            response_1 = await deps.clients.customers_household_calculation.ExplainHouseholdCalculation(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = checkout_v1_checkout_session_service_pb2.WatchCheckoutSessionsRequest(
                context=request.context,
                filter=checkout_v1_checkout_session_service_pb2.WatchCheckoutSessionsRequest.Filter(
                    region=response_1.household.location.region
                ),
                subscriber=common_v1_contact_pb2.ContactInfo(
                    email=request.details.notify_contact.email,
                    phone=request.details.notify_contact.phone
                )
            )
            async for chunk_2 in deps.clients.checkout_checkout_session.WatchCheckoutSessions(
                outgoing_2,
                timeout=deps.settings.timeout
            ):
                response_2 = chunk_2
            returned_0_0 = response_0.lineage_edge.subject.priority
            if returned_0_0:
                response.lineage_edge.subject.priority = returned_0_0
            returned_1_0 = response_1.household.manager.display_name
            if returned_1_0:
                response.lineage_edge.subject.display_name = returned_1_0
            echoed_0 = request.lineage_edge_id
            response.lineage_edge.lineage_edge_id = echoed_0
            echoed_1 = request.details.effective_at
            response.outcome.effective_at.CopyFrom(echoed_1)
            return response

    async def handle_expire_lineage_edge(
        self,
        request: lineage_v1_lineage_edge_lifecycle_service_pb2.ExpireLineageEdgeRequest
    ) -> lineage_v1_lineage_edge_lifecycle_service_pb2.ExpireLineageEdgeResponse:
        """Expires a lineage edge."""
        deps = self.deps
        response = lineage_v1_lineage_edge_lifecycle_service_pb2.ExpireLineageEdgeResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ExpireLineageEdge', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'ExpireLineageEdge', {'reason': request.reason})
            response_0 = notifications_v1_notification_service_pb2.BatchGetNotificationsResponse()
            response_1 = lineage_v1_lineage_node_reporting_service_pb2.ListLineageNodeReportsResponse()
            response_2 = customers_v1_preference_validation_service_pb2.NormalizePreferenceResponse()
            response_3 = recommendations_v1_interaction_validation_service_pb2.ValidateInteractionResponse()
            outgoing_0 = notifications_v1_notification_service_pb2.BatchGetNotificationsRequest(context=request.context)
            outgoing_2 = customers_v1_preference_validation_service_pb2.NormalizePreferenceRequest(
                context=request.context,
                details=customers_v1_preference_validation_service_pb2.NormalizePreferenceRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(
                        email=request.details.new_owner.email,
                        name=request.details.notify_contact.name,
                        preferred_channel=request.details.notify_contact.preferred_channel
                    )
                ),
                preference=customers_v1_customers_pb2.Preference(
                    owner=identity_v1_refs_pb2.UserRef(display_name=request.details.new_owner.display_name)
                )
            )
            outgoing_3 = recommendations_v1_interaction_validation_service_pb2.ValidateInteractionRequest(
                context=request.context,
                interaction=recommendations_v1_recommendations_pb2.Interaction(
                    subject=customers_v1_refs_pb2.CustomerRef(email=request.details.new_owner.email)
                )
            )
            response_0, response_2, response_3 = await asyncio.gather(
                deps.clients.notifications_notification.BatchGetNotifications(
                    outgoing_0,
                    timeout=deps.settings.timeout
                ),
                deps.clients.customers_preference_validation.NormalizePreference(
                    outgoing_2,
                    timeout=deps.settings.timeout
                ),
                deps.clients.recommendations_interaction_validation.ValidateInteraction(
                    outgoing_3,
                    timeout=deps.settings.timeout
                ),
            )
            command_1 = LineageEdgeLifecycleExpireLineageEdge1Command(
                context=request.context,
                filter_created_after=request.details.effective_at,
                filter_owner_id=response_0.result.correlation_id,
                filter_labels=dict(response_0.result.details)
            )
            outgoing_1 = to_lineage_edge_lifecycle_expire_lineage_edge1_command(command_1)
            response_1 = await deps.clients.lineage_lineage_node_reporting.ListLineageNodeReports(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_0)
            returned_1_0 = response_1.result.status
            if returned_1_0:
                response.result.status = returned_1_0
            returned_1_1 = response_1.result.reference_ids
            response.result.reference_ids.extend(returned_1_1)
            returned_2_0 = response_2.result.reference_ids
            response.result.reference_ids.extend(returned_2_0)
            returned_3_0 = response_3.result.status
            if returned_3_0:
                response.outcome.status = returned_3_0
            returned_3_1 = response_3.result.correlation_id
            if returned_3_1:
                response.result.correlation_id = returned_3_1
            echoed_0 = request.lineage_edge_id
            response.lineage_edge.lineage_edge_id = echoed_0
            echoed_1 = request.details.effective_at
            response.outcome.effective_at.CopyFrom(echoed_1)
            return response

    async def handle_get_lineage_edge_lifecycle(
        self,
        request: lineage_v1_lineage_edge_lifecycle_service_pb2.GetLineageEdgeLifecycleRequest
    ) -> lineage_v1_lineage_edge_lifecycle_service_pb2.GetLineageEdgeLifecycleResponse:
        """Returns a lineage edge."""
        deps = self.deps
        response = lineage_v1_lineage_edge_lifecycle_service_pb2.GetLineageEdgeLifecycleResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('GetLineageEdgeLifecycle', extra={'fields': {'locale': request.context.locale}})
            await deps.repository.audit(
                request.context.tenant_id,
                'GetLineageEdgeLifecycle',
                {'locale': request.context.locale}
            )
            echoed_0 = request.lineage_edge_id
            response.lineage_edge.lineage_edge_id = echoed_0
            return response

    async def handle_reinstate_lineage_edge(
        self,
        request: lineage_v1_lineage_edge_lifecycle_service_pb2.ReinstateLineageEdgeRequest
    ) -> lineage_v1_lineage_edge_lifecycle_service_pb2.ReinstateLineageEdgeResponse:
        """Reinstates a lineage edge."""
        deps = self.deps
        response = lineage_v1_lineage_edge_lifecycle_service_pb2.ReinstateLineageEdgeResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ReinstateLineageEdge', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'ReinstateLineageEdge', {'reason': request.reason})
            response_0 = lineage_v1_lineage_node_sync_service_pb2.PullLineageNodesResponse()
            response_1 = catalog_v1_product_query_service_pb2.FindProductsResponse()
            outgoing_0 = lineage_v1_lineage_node_sync_service_pb2.PullLineageNodesRequest(
                context=request.context,
                lineage_node=lineage_v1_lineage_pb2.LineageNode(
                    children=[
                        lineage_v1_lineage_pb2.LineageNode(
                            children=[
                                lineage_v1_lineage_pb2.LineageNode(
                                    manager=identity_v1_refs_pb2.UserRef(email=request.details.new_owner.email)
                                )
                            ],
                            manager=identity_v1_refs_pb2.UserRef(display_name=request.details.new_owner.display_name)
                        )
                    ]
                )
            )
            response_0 = await hooks.lineage_edge_lifecycle_reinstate_lineage_edge0(
                deps.clients.lineage_lineage_node_sync,
                outgoing_0,
                deps.settings.timeout
            )
            outgoing_1 = catalog_v1_product_query_service_pb2.FindProductsRequest()
            outgoing_1.context.CopyFrom(request.context)
            outgoing_1.filter.region = response_0.lineage_node.location.region
            outgoing_1.context.tenant_id = tenant_id.get()
            response_1 = await deps.clients.catalog_product_query.FindProducts(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.correlation_id
            if returned_0_0:
                response.lineage_edge.correlation_id = returned_0_0
            returned_1_0 = response_1.result.correlation_id
            if returned_1_0:
                response.lineage_edge.correlation_id = returned_1_0
            echoed_0 = request.lineage_edge_id
            response.lineage_edge.lineage_edge_id = echoed_0
            echoed_1 = request.details.effective_at
            response.outcome.effective_at.CopyFrom(echoed_1)
            return response

    async def handle_renew_lineage_edge(
        self,
        request: lineage_v1_lineage_edge_lifecycle_service_pb2.RenewLineageEdgeRequest
    ) -> lineage_v1_lineage_edge_lifecycle_service_pb2.RenewLineageEdgeResponse:
        """Renews a lineage edge."""
        deps = self.deps
        response = lineage_v1_lineage_edge_lifecycle_service_pb2.RenewLineageEdgeResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('RenewLineageEdge', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'RenewLineageEdge', {'reason': request.reason})
            response_0 = lineage_v1_lineage_node_reporting_service_pb2.ListLineageNodeReportsResponse()
            response_1 = lineage_v1_lineage_edge_reporting_service_pb2.ListLineageEdgeReportsResponse()
            outgoing_0 = lineage_v1_lineage_node_reporting_service_pb2.ListLineageNodeReportsRequest(
                context=request.context,
                filter=lineage_v1_lineage_node_reporting_service_pb2.ListLineageNodeReportsRequest.Filter(
                    created_after=request.details.effective_at,
                    labels=dict(request.annotations)
                )
            )
            outgoing_1 = lineage_v1_lineage_edge_reporting_service_pb2.ListLineageEdgeReportsRequest(
                context=request.context,
                filter=lineage_v1_lineage_edge_reporting_service_pb2.ListLineageEdgeReportsRequest.Filter(
                    created_after=request.details.effective_at
                )
            )
            response_0, response_1 = await asyncio.gather(
                deps.clients.lineage_lineage_node_reporting.ListLineageNodeReports(
                    outgoing_0,
                    timeout=deps.settings.timeout
                ),
                deps.clients.lineage_lineage_edge_reporting.ListLineageEdgeReports(
                    outgoing_1,
                    timeout=deps.settings.timeout
                ),
            )
            returned_0_0 = response_0.result.status
            if returned_0_0:
                response.result.status = returned_0_0
            returned_0_1 = response_0.result.details
            response.result.details.update(returned_0_1)
            returned_1_0 = response_1.result.message
            if returned_1_0:
                response.outcome.message = returned_1_0
            returned_1_1 = response_1.result.details
            response.result.details.update(returned_1_1)
            echoed_0 = request.lineage_edge_id
            response.lineage_edge.lineage_edge_id = echoed_0
            echoed_1 = request.details.effective_at
            response.outcome.effective_at.CopyFrom(echoed_1)
            return response

    async def handle_schedule_lineage_edge_expiry(
        self,
        request: lineage_v1_lineage_edge_lifecycle_service_pb2.ScheduleLineageEdgeExpiryRequest
    ) -> lineage_v1_lineage_edge_lifecycle_service_pb2.ScheduleLineageEdgeExpiryResponse:
        """Schedules a lineage edge."""
        deps = self.deps
        response = lineage_v1_lineage_edge_lifecycle_service_pb2.ScheduleLineageEdgeExpiryResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ScheduleLineageEdgeExpiry', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ScheduleLineageEdgeExpiry',
                {'reason': request.reason}
            )
            await deps.repository.save_lineage_edge(request.context.tenant_id, request.lineage_edge)
            response_0 = analytics_v1_funnel_validation_service_pb2.ScoreFunnelResponse()
            response_1 = featureflags_v1_feature_flag_service_pb2.CreateFeatureFlagResponse()
            response_2 = recommendations_v1_recommendation_model_validation_service_pb2.ExplainRecommendationModelDecisionResponse()
            response_3 = lineage_v1_lineage_edge_reporting_service_pb2.CountLineageEdgeTotalsResponse()
            outgoing_0 = analytics_v1_funnel_validation_service_pb2.ScoreFunnelRequest(
                context=request.context,
                funnel=analytics_v1_analytics_pb2.Funnel(
                    owner=identity_v1_refs_pb2.UserRef(
                        display_name=request.lineage_edge.subject.display_name,
                        email=request.details.notify.email
                    )
                )
            )
            response_0 = await LineageEdgeLifecycleScheduleLineageEdgeExpiry0Adapter(
                deps.clients.analytics_funnel_validation,
                deps.settings.timeout
            )(outgoing_0)
            outgoing_1 = featureflags_v1_feature_flag_service_pb2.CreateFeatureFlagRequest()
            outgoing_1.context.CopyFrom(request.context)
            outgoing_1.feature_flag.owner.email = request.details.notify.email
            if response_0.funnel.WhichOneof('action') == 'route':
                outgoing_1.feature_flag.route.target = response_0.funnel.route.target
            if response_0.funnel.WhichOneof('action') == 'route':
                outgoing_1.feature_flag.route.weight = response_0.funnel.route.weight
            response_1 = await deps.clients.featureflags_feature_flag.CreateFeatureFlag(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            async for item_2 in async_messages(request.lineage_edge.measurements):
                outgoing_2 = recommendations_v1_recommendation_model_validation_service_pb2.ExplainRecommendationModelDecisionRequest(
                    context=request.context,
                    details=recommendations_v1_recommendation_model_validation_service_pb2.ExplainRecommendationModelDecisionRequest.Details(
                        contact=common_v1_contact_pb2.ContactInfo(email=response_1.feature_flag.owner.email)
                    ),
                    recommendation_model=recommendations_v1_recommendations_pb2.RecommendationModel(
                        audit=common_v1_audit_pb2.AuditInfo(created_at=response_0.funnel.audit.created_at),
                        dimensions=recommendations_v1_recommendations_pb2.RecommendationModelDimensions(
                            unit=item_2.unit
                        )
                    )
                )
                response_2 = await deps.clients.recommendations_recommendation_model_validation.ExplainRecommendationModelDecision(
                    outgoing_2,
                    timeout=deps.settings.timeout
                )
            outgoing_3 = lineage_v1_lineage_edge_reporting_service_pb2.CountLineageEdgeTotalsRequest(
                context=request.context,
                filter=lineage_v1_lineage_edge_reporting_service_pb2.CountLineageEdgeTotalsRequest.Filter(
                    created_after=response_2.recommendation_model.audit.created_at,
                    region=response_2.recommendation_model.address.region
                )
            )
            method_name_3 = 'CountLineageEdgeTotals'
            response_3 = await getattr(
                deps.clients.lineage_lineage_edge_reporting,
                method_name_3
            )(outgoing_3, timeout=deps.settings.timeout)
            returned_0_0 = response_0.result.correlation_id
            if returned_0_0:
                response.result.correlation_id = returned_0_0
            returned_0_1 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_1)
            returned_1_0 = response_1.result.status
            if returned_1_0:
                response.outcome.status = returned_1_0
            returned_1_1 = response_1.result.message
            if returned_1_1:
                response.outcome.message = returned_1_1
            returned_3_0 = response_3.result.reference_ids
            response.result.reference_ids.extend(returned_3_0)
            echoed_0 = request.lineage_edge_id
            response.lineage_edge.lineage_edge_id = echoed_0
            echoed_1 = request.lineage_edge.occurred_at
            response.lineage_edge.occurred_at.CopyFrom(echoed_1)
            return response

    async def handle_suspend_lineage_edge(
        self,
        request: lineage_v1_lineage_edge_lifecycle_service_pb2.SuspendLineageEdgeRequest
    ) -> lineage_v1_lineage_edge_lifecycle_service_pb2.SuspendLineageEdgeResponse:
        """Suspends a lineage edge."""
        deps = self.deps
        response = lineage_v1_lineage_edge_lifecycle_service_pb2.SuspendLineageEdgeResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SuspendLineageEdge', extra={'fields': {'reason_code': request.details.reason_code}})
            await deps.repository.audit(
                request.context.tenant_id,
                'SuspendLineageEdge',
                {'reason_code': request.details.reason_code}
            )
            response_0 = lineage_v1_lineage_edge_reporting_service_pb2.DeleteLineageEdgeReportResponse()
            response_1 = lineage_v1_lineage_edge_calculation_service_pb2.ExplainLineageEdgeCalculationResponse()
            response_2 = lineage_v1_lineage_edge_reporting_service_pb2.ListLineageEdgeReportsResponse()
            response_3 = checkout_v1_checkout_session_service_pb2.BatchGetCheckoutSessionsResponse()
            fields_0: dict[str, Any] = {
                'context': request.context,
                'lineage_edge_id': request.lineage_edge_id,
                'reason': request.reason
            }
            outgoing_0 = lineage_v1_lineage_edge_reporting_service_pb2.DeleteLineageEdgeReportRequest(**fields_0)
            response_0 = await deps.clients.lineage_lineage_edge_reporting.DeleteLineageEdgeReport(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = lineage_v1_lineage_edge_calculation_service_pb2.ExplainLineageEdgeCalculationRequest(
                context=request.context,
                details=lineage_v1_lineage_edge_calculation_service_pb2.ExplainLineageEdgeCalculationRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(
                        email=request.details.new_owner.email,
                        name=request.details.notify_contact.name,
                        preferred_channel=request.details.notify_contact.preferred_channel
                    )
                )
            )
            document_1 = MessageToDict(outgoing_1, preserving_proto_field_name=True)
            outgoing_1 = ParseDict(
                document_1,
                lineage_v1_lineage_edge_calculation_service_pb2.ExplainLineageEdgeCalculationRequest()
            )
            response_1 = await deps.clients.lineage_lineage_edge_calculation.ExplainLineageEdgeCalculation(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = lineage_v1_lineage_edge_reporting_service_pb2.ListLineageEdgeReportsRequest(
                context=request.context,
                filter=lineage_v1_lineage_edge_reporting_service_pb2.ListLineageEdgeReportsRequest.Filter(
                    created_after=response_1.outcome.effective_at,
                    labels=dict(response_0.result.details),
                    owner_id=response_1.lineage_edge.lineage_edge_id
                )
            )
            document_2 = MessageToJson(outgoing_2, preserving_proto_field_name=True)
            outgoing_2 = Parse(
                document_2,
                lineage_v1_lineage_edge_reporting_service_pb2.ListLineageEdgeReportsRequest()
            )
            response_2 = await deps.clients.lineage_lineage_edge_reporting.ListLineageEdgeReports(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            outgoing_3 = checkout_v1_checkout_session_service_pb2.BatchGetCheckoutSessionsRequest()
            outgoing_3.context.CopyFrom(request.context)
            merged_3 = checkout_v1_checkout_session_service_pb2.BatchGetCheckoutSessionsRequest()
            merged_3.MergeFrom(outgoing_3)
            outgoing_3.CopyFrom(merged_3)
            response_3 = await deps.clients.checkout_checkout_session.BatchGetCheckoutSessions(
                outgoing_3,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.effective_at
            if returned_0_0.ListFields():
                response.outcome.effective_at.MergeFrom(returned_0_0)
            returned_1_0 = response_1.lineage_edge.lineage_edge_id
            if returned_1_0:
                response.lineage_edge.lineage_edge_id = returned_1_0
            returned_1_1 = response_1.lineage_edge.attributes
            response.lineage_edge.attributes.update(returned_1_1)
            returned_2_0 = response_2.result.status
            if returned_2_0:
                response.result.status = returned_2_0
            returned_3_0 = response_3.result.message
            if returned_3_0:
                response.outcome.message = returned_3_0
            echoed_0 = request.details.new_owner.display_name
            response.lineage_edge.subject.display_name = echoed_0
            return response
