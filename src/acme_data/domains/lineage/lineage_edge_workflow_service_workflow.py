"""Application workflow for LineageEdge Workflow."""

from __future__ import annotations

from collections.abc import Awaitable
from collections.abc import Callable
from typing import Any
from typing import cast
import asyncio
import logging

from google.protobuf.any_pb2 import Any as AnyMessage
from google.protobuf.json_format import MessageToDict
from google.protobuf.json_format import ParseDict

from acme.analytics.v1 import analytics_pb2 as analytics_v1_analytics_pb2
from acme.analytics.v1 import funnel_validation_service_pb2 as analytics_v1_funnel_validation_service_pb2
from acme.authorization.v1 import access_policy_query_service_pb2 as authorization_v1_access_policy_query_service_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.customers.v1 import (
    customer_segment_calculation_service_pb2 as customers_v1_customer_segment_calculation_service_pb2,
)
from acme.customers.v1 import (
    customer_segment_validation_service_pb2 as customers_v1_customer_segment_validation_service_pb2,
)
from acme.customers.v1 import customers_pb2 as customers_v1_customers_pb2
from acme.customers.v1 import household_calculation_service_pb2 as customers_v1_household_calculation_service_pb2
from acme.customers.v1 import household_validation_service_pb2 as customers_v1_household_validation_service_pb2
from acme.customers.v1 import refs_pb2 as customers_v1_refs_pb2
from acme.datasets.v1 import (
    dataset_version_validation_service_pb2 as datasets_v1_dataset_version_validation_service_pb2,
)
from acme.datasets.v1 import datasets_pb2 as datasets_v1_datasets_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.labeling.v1 import labeling_pb2 as labeling_v1_labeling_pb2
from acme.labeling.v1 import labeling_task_service_pb2 as labeling_v1_labeling_task_service_pb2
from acme.lineage.v1 import impact_reporting_service_pb2 as lineage_v1_impact_reporting_service_pb2
from acme.lineage.v1 import lineage_edge_approval_service_pb2 as lineage_v1_lineage_edge_approval_service_pb2
from acme.lineage.v1 import lineage_edge_workflow_service_pb2 as lineage_v1_lineage_edge_workflow_service_pb2
from acme.lineage.v1 import lineage_pb2 as lineage_v1_lineage_pb2
from acme.lineage.v1 import refs_pb2 as lineage_v1_refs_pb2
from acme.promotions.v1 import promotion_query_service_pb2 as promotions_v1_promotion_query_service_pb2
from acme.recommendations.v1 import (
    recommendation_model_validation_service_pb2 as recommendations_v1_recommendation_model_validation_service_pb2,
)
from acme.recommendations.v1 import recommendations_pb2 as recommendations_v1_recommendations_pb2
from acme.search.v1 import search_index_query_service_pb2 as search_v1_search_index_query_service_pb2

from acme_data.domains.lineage.adapters import LineageEdgeWorkflowPauseLineageEdgeWorkflow0Adapter
from acme_data.domains.lineage.adapters import LineageEdgeWorkflowPauseLineageEdgeWorkflow0Port
from acme_data.domains.lineage.dependencies import Dependencies
from acme_data.domains.lineage.models import LineageEdgeWorkflowAdvanceLineageEdgeWorkflow2Command
from acme_data.domains.lineage.models import to_lineage_edge_workflow_advance_lineage_edge_workflow2_command
from acme_data.platform.rpc import async_messages
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class LineageEdgeWorkflowServicerWorkflow:
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    async def handle_advance_lineage_edge_workflow(
        self,
        request: lineage_v1_lineage_edge_workflow_service_pb2.AdvanceLineageEdgeWorkflowRequest
    ) -> lineage_v1_lineage_edge_workflow_service_pb2.AdvanceLineageEdgeWorkflowResponse:
        """Advances a lineage edge."""
        deps = self.deps
        response = lineage_v1_lineage_edge_workflow_service_pb2.AdvanceLineageEdgeWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('AdvanceLineageEdgeWorkflow', extra={'fields': {'initiated_by': request.details.initiated_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'AdvanceLineageEdgeWorkflow',
                {'initiated_by': request.details.initiated_by}
            )
            await deps.repository.save_lineage_edge(request.context.tenant_id, request.lineage_edge)
            response_0 = authorization_v1_access_policy_query_service_pb2.ResolveAccessPoliciesResponse()
            response_1 = promotions_v1_promotion_query_service_pb2.ExportPromotionsResponse()
            response_2 = authorization_v1_access_policy_query_service_pb2.SummarizeAccessPoliciesResponse()
            response_3 = customers_v1_household_validation_service_pb2.CheckHouseholdEligibilityResponse()
            outgoing_0 = authorization_v1_access_policy_query_service_pb2.ResolveAccessPoliciesRequest(
                context=request.context
            )
            envelope_0 = AnyMessage()
            envelope_0.Pack(outgoing_0)
            outgoing_0 = authorization_v1_access_policy_query_service_pb2.ResolveAccessPoliciesRequest()
            if not envelope_0.Unpack(outgoing_0):
                raise ValueError("partner envelope contains the wrong request type")
            response_0 = await deps.clients.authorization_access_policy_query.ResolveAccessPolicies(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            for item_1 in request.lineage_edge.measurements:
                outgoing_1 = promotions_v1_promotion_query_service_pb2.ExportPromotionsRequest(
                    context=request.context,
                    filter=promotions_v1_promotion_query_service_pb2.ExportPromotionsRequest.Filter(
                        created_after=item_1.observed_at,
                        labels=dict(request.lineage_edge.attributes),
                        owner_id=request.lineage_edge.lineage_edge_id
                    )
                )
                async for result_1 in deps.clients.promotions_promotion_query.ExportPromotions(
                    outgoing_1,
                    timeout=deps.settings.timeout
                ):
                    response_1 = result_1
            command_2 = LineageEdgeWorkflowAdvanceLineageEdgeWorkflow2Command(
                context=request.context,
                annotations=dict(request.annotations),
                reason=request.reason
            )
            outgoing_2 = to_lineage_edge_workflow_advance_lineage_edge_workflow2_command(command_2)
            response_2 = await deps.clients.authorization_access_policy_query.SummarizeAccessPolicies(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            requests_3: list[customers_v1_household_validation_service_pb2.CheckHouseholdEligibilityRequest] = []
            for item_3 in request.lineage_edge.measurements:
                outgoing_3 = customers_v1_household_validation_service_pb2.CheckHouseholdEligibilityRequest(
                    context=request.context,
                    household=customers_v1_customers_pb2.Household(
                        children=[
                            customers_v1_customers_pb2.Household(
                                children=[
                                    customers_v1_customers_pb2.Household(
                                        audit=common_v1_audit_pb2.AuditInfo(created_at=item_3.observed_at),
                                        manager=identity_v1_refs_pb2.UserRef(
                                            display_name=request.lineage_edge.subject.display_name,
                                            email=request.details.notify.email
                                        )
                                    )
                                ]
                            )
                        ]
                    )
                )
                requests_3.append(outgoing_3)
            replies_3 = await asyncio.gather(*(
                deps.clients.customers_household_validation.CheckHouseholdEligibility(
                    entry,
                    timeout=deps.settings.timeout
                ) for entry in requests_3
            ))
            if replies_3:
                response_3 = replies_3[-1]
            returned_0_0 = response_0.result.status
            if returned_0_0:
                response.outcome.status = returned_0_0
            returned_0_1 = response_0.result.status
            if returned_0_1:
                response.result.status = returned_0_1
            returned_2_0 = response_2.result.status
            if returned_2_0:
                response.outcome.status = returned_2_0
            returned_2_1 = response_2.result.message
            if returned_2_1:
                response.result.message = returned_2_1
            echoed_0 = request.lineage_edge_id
            response.lineage_edge.lineage_edge_id = echoed_0
            echoed_1 = request.lineage_edge.correlation_id
            response.result.correlation_id = echoed_1
            return response

    async def handle_cancel_lineage_edge_workflow(
        self,
        request: lineage_v1_lineage_edge_workflow_service_pb2.CancelLineageEdgeWorkflowRequest
    ) -> lineage_v1_lineage_edge_workflow_service_pb2.CancelLineageEdgeWorkflowResponse:
        """Cancels a lineage edge."""
        deps = self.deps
        response = lineage_v1_lineage_edge_workflow_service_pb2.CancelLineageEdgeWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CancelLineageEdgeWorkflow', extra={'fields': {'initiated_by': request.details.initiated_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'CancelLineageEdgeWorkflow',
                {'initiated_by': request.details.initiated_by}
            )
            await deps.repository.save_lineage_edge(request.context.tenant_id, request.lineage_edge)
            response_0 = lineage_v1_impact_reporting_service_pb2.DeleteImpactReportResponse()
            response_1 = customers_v1_household_calculation_service_pb2.CompareHouseholdOptionsResponse()
            outgoing_0 = lineage_v1_impact_reporting_service_pb2.DeleteImpactReportRequest(
                context=request.context,
                impact_id=request.lineage_edge.subject.impact_id,
                reason=request.reason
            )
            outgoing_1 = customers_v1_household_calculation_service_pb2.CompareHouseholdOptionsRequest(
                context=request.context,
                household=customers_v1_customers_pb2.Household(
                    children=[
                        customers_v1_customers_pb2.Household(
                            children=[
                                customers_v1_customers_pb2.Household(
                                    children=[
                                        customers_v1_customers_pb2.Household(
                                            attributes=dict(request.lineage_edge.attributes)
                                        )
                                    ],
                                    manager=identity_v1_refs_pb2.UserRef(
                                        display_name=request.lineage_edge.subject.display_name
                                    )
                                )
                            ],
                            manager=identity_v1_refs_pb2.UserRef(email=request.details.notify.email)
                        )
                    ]
                )
            )
            response_0, response_1 = await asyncio.gather(
                deps.clients.lineage_impact_reporting.DeleteImpactReport(outgoing_0, timeout=deps.settings.timeout),
                deps.clients.customers_household_calculation.CompareHouseholdOptions(
                    outgoing_1,
                    timeout=deps.settings.timeout
                ),
            )
            returned_0_0 = response_0.result.status
            if returned_0_0:
                response.outcome.status = returned_0_0
            returned_1_0 = response_1.result.status
            if returned_1_0:
                response.result.status = returned_1_0
            returned_1_1 = response_1.result.status
            if returned_1_1:
                response.outcome.status = returned_1_1
            echoed_0 = request.lineage_edge_id
            response.lineage_edge.lineage_edge_id = echoed_0
            echoed_1 = request.lineage_edge.occurred_at
            response.lineage_edge.occurred_at.CopyFrom(echoed_1)
            return response

    async def handle_inspect_lineage_edge_workflow(
        self,
        request: lineage_v1_lineage_edge_workflow_service_pb2.InspectLineageEdgeWorkflowRequest
    ) -> lineage_v1_lineage_edge_workflow_service_pb2.InspectLineageEdgeWorkflowResponse:
        """Returns a lineage edge."""
        deps = self.deps
        response = lineage_v1_lineage_edge_workflow_service_pb2.InspectLineageEdgeWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('InspectLineageEdgeWorkflow', extra={'fields': {'locale': request.context.locale}})
            await deps.repository.audit(
                request.context.tenant_id,
                'InspectLineageEdgeWorkflow',
                {'locale': request.context.locale}
            )
            echoed_0 = request.lineage_edge_id
            response.lineage_edge.lineage_edge_id = echoed_0
            return response

    async def handle_list_lineage_edge_workflows(
        self,
        request: lineage_v1_lineage_edge_workflow_service_pb2.ListLineageEdgeWorkflowsRequest
    ) -> lineage_v1_lineage_edge_workflow_service_pb2.ListLineageEdgeWorkflowsResponse:
        """Lists lineage edges a page at a time."""
        deps = self.deps
        response = lineage_v1_lineage_edge_workflow_service_pb2.ListLineageEdgeWorkflowsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ListLineageEdgeWorkflows', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ListLineageEdgeWorkflows',
                {'order_by': request.order_by}
            )
            response_0 = datasets_v1_dataset_version_validation_service_pb2.ExplainDatasetVersionDecisionResponse()
            outgoing_0 = datasets_v1_dataset_version_validation_service_pb2.ExplainDatasetVersionDecisionRequest(
                context=request.context,
                dataset_version=datasets_v1_datasets_pb2.DatasetVersion(
                    subject=customers_v1_refs_pb2.CustomerRef(email=request.context.actor.email)
                ),
                details=datasets_v1_dataset_version_validation_service_pb2.ExplainDatasetVersionDecisionRequest.Details(
                    locale=request.context.locale
                )
            )
            response_0 = await deps.clients.datasets_dataset_version_validation.ExplainDatasetVersionDecision(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.outcome.status
            if returned_0_0:
                response.result.status = returned_0_0
            return response

    async def handle_pause_lineage_edge_workflow(
        self,
        request: lineage_v1_lineage_edge_workflow_service_pb2.PauseLineageEdgeWorkflowRequest
    ) -> lineage_v1_lineage_edge_workflow_service_pb2.PauseLineageEdgeWorkflowResponse:
        """Pauses a lineage edge."""
        deps = self.deps
        response = lineage_v1_lineage_edge_workflow_service_pb2.PauseLineageEdgeWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('PauseLineageEdgeWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'PauseLineageEdgeWorkflow',
                {'reason': request.reason}
            )
            await deps.repository.save_lineage_edge(request.context.tenant_id, request.lineage_edge)
            response_0 = lineage_v1_lineage_edge_approval_service_pb2.SubmitLineageEdgeResponse()
            response_1 = recommendations_v1_recommendation_model_validation_service_pb2.ExplainRecommendationModelDecisionResponse()
            outgoing_0 = lineage_v1_lineage_edge_approval_service_pb2.SubmitLineageEdgeRequest(
                context=request.context,
                lineage_edge=lineage_v1_lineage_pb2.LineageEdge(
                    kind=request.lineage_edge.kind,
                    lineage_edge_id=request.lineage_edge.lineage_edge_id,
                    subject=lineage_v1_refs_pb2.ImpactRef(
                        display_name=request.lineage_edge.subject.display_name,
                        priority=request.lineage_edge.subject.priority
                    )
                )
            )
            port_0: LineageEdgeWorkflowPauseLineageEdgeWorkflow0Port = LineageEdgeWorkflowPauseLineageEdgeWorkflow0Adapter(
                deps.clients.lineage_lineage_edge_approval,
                deps.settings.timeout
            )
            response_0 = await port_0.execute(outgoing_0)
            callbacks_1: list[
                Callable[
                    [],
                    Awaitable[
                        recommendations_v1_recommendation_model_validation_service_pb2.ExplainRecommendationModelDecisionResponse
                    ]
                ]
            ] = []
            for item_1 in request.lineage_edge.measurements:
                outgoing_1 = recommendations_v1_recommendation_model_validation_service_pb2.ExplainRecommendationModelDecisionRequest(
                    context=request.context,
                    details=recommendations_v1_recommendation_model_validation_service_pb2.ExplainRecommendationModelDecisionRequest.Details(
                        contact=common_v1_contact_pb2.ContactInfo(
                            email=request.details.notify.email,
                            preferred_channel=request.details.notify.preferred_channel
                        )
                    ),
                    recommendation_model=recommendations_v1_recommendations_pb2.RecommendationModel(
                        dimensions=recommendations_v1_recommendations_pb2.RecommendationModelDimensions(
                            unit=item_1.unit
                        )
                    )
                )
                async def send_1(
                    payload: recommendations_v1_recommendation_model_validation_service_pb2.ExplainRecommendationModelDecisionRequest = outgoing_1
                ) -> recommendations_v1_recommendation_model_validation_service_pb2.ExplainRecommendationModelDecisionResponse:
                    return await deps.clients.recommendations_recommendation_model_validation.ExplainRecommendationModelDecision(
                        payload,
                        timeout=deps.settings.timeout
                    )
                callbacks_1.append(send_1)
            for callback_1 in callbacks_1:
                response_1 = await callback_1()
            returned_0_0 = response_0.lineage_edge.sequence
            if returned_0_0:
                response.lineage_edge.sequence = returned_0_0
            returned_0_1 = response_0.result.message
            if returned_0_1:
                response.result.message = returned_0_1
            echoed_0 = request.lineage_edge_id
            response.lineage_edge.lineage_edge_id = echoed_0
            echoed_1 = request.lineage_edge.source
            response.lineage_edge.source = echoed_1
            return response

    async def handle_resume_lineage_edge_workflow(
        self,
        request: lineage_v1_lineage_edge_workflow_service_pb2.ResumeLineageEdgeWorkflowRequest
    ) -> lineage_v1_lineage_edge_workflow_service_pb2.ResumeLineageEdgeWorkflowResponse:
        """Resumes a lineage edge."""
        deps = self.deps
        response = lineage_v1_lineage_edge_workflow_service_pb2.ResumeLineageEdgeWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ResumeLineageEdgeWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ResumeLineageEdgeWorkflow',
                {'reason': request.reason}
            )
            await deps.repository.save_lineage_edge(request.context.tenant_id, request.lineage_edge)
            response_0 = search_v1_search_index_query_service_pb2.SuggestSearchIndexesResponse()
            response_1 = customers_v1_customer_segment_validation_service_pb2.ExplainCustomerSegmentDecisionResponse()
            response_2 = search_v1_search_index_query_service_pb2.ExportSearchIndexesResponse()
            response_3 = analytics_v1_funnel_validation_service_pb2.CheckFunnelEligibilityResponse()
            async for item_0 in async_messages(request.lineage_edge.measurements):
                outgoing_0 = search_v1_search_index_query_service_pb2.SuggestSearchIndexesRequest(
                    context=request.context,
                    filter=search_v1_search_index_query_service_pb2.SuggestSearchIndexesRequest.Filter(
                        created_after=item_0.observed_at
                    )
                )
                response_0 = await deps.clients.search_search_index_query.SuggestSearchIndexes(
                    outgoing_0,
                    timeout=deps.settings.timeout
                )
            outgoing_1 = customers_v1_customer_segment_validation_service_pb2.ExplainCustomerSegmentDecisionRequest(
                context=request.context,
                customer_segment=customers_v1_customers_pb2.CustomerSegment(
                    owner=identity_v1_refs_pb2.UserRef(email=request.details.notify.email)
                ),
                details=customers_v1_customer_segment_validation_service_pb2.ExplainCustomerSegmentDecisionRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(name=request.details.notify.name)
                )
            )
            response_1 = cast(customers_v1_customer_segment_validation_service_pb2.ExplainCustomerSegmentDecisionResponse, await deps.bus.request(
                'acme.lineage.v1.LineageEdgeWorkflowService/ResumeLineageEdgeWorkflow/1', outgoing_1, deps.settings.timeout,
            ))
            outgoing_2 = search_v1_search_index_query_service_pb2.ExportSearchIndexesRequest(
                context=request.context,
                filter=search_v1_search_index_query_service_pb2.ExportSearchIndexesRequest.Filter(
                    created_after=response_1.customer_segment.audit.created_at,
                    labels=dict(request.details.parameters),
                    owner_id=request.lineage_edge.subject.impact_id
                )
            )
            async for chunk_2 in deps.clients.search_search_index_query.ExportSearchIndexes(
                outgoing_2,
                timeout=deps.settings.timeout
            ):
                response_2 = chunk_2
            outgoing_3 = analytics_v1_funnel_validation_service_pb2.CheckFunnelEligibilityRequest(
                context=request.context,
                details=analytics_v1_funnel_validation_service_pb2.CheckFunnelEligibilityRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(email=response_1.customer_segment.owner.email)
                ),
                funnel=analytics_v1_analytics_pb2.Funnel(
                    discount=analytics_v1_analytics_pb2.FunnelDiscountAction(
                        amount=response_1.customer_segment.discount.amount
                    )
                )
            )
            method_name_3 = 'CheckFunnelEligibility'
            response_3 = await getattr(
                deps.clients.analytics_funnel_validation,
                method_name_3
            )(outgoing_3, timeout=deps.settings.timeout)
            returned_1_0 = response_1.result.message
            if returned_1_0:
                response.outcome.message = returned_1_0
            returned_3_0 = response_3.result.message
            if returned_3_0:
                response.result.message = returned_3_0
            returned_3_1 = response_3.funnel.owner.display_name
            if returned_3_1:
                response.lineage_edge.subject.display_name = returned_3_1
            echoed_0 = request.lineage_edge_id
            response.lineage_edge.lineage_edge_id = echoed_0
            echoed_1 = request.lineage_edge.sequence
            response.lineage_edge.sequence = echoed_1
            return response

    async def handle_retry_lineage_edge_workflow(
        self,
        request: lineage_v1_lineage_edge_workflow_service_pb2.RetryLineageEdgeWorkflowRequest
    ) -> lineage_v1_lineage_edge_workflow_service_pb2.RetryLineageEdgeWorkflowResponse:
        """Retrys a lineage edge."""
        deps = self.deps
        response = lineage_v1_lineage_edge_workflow_service_pb2.RetryLineageEdgeWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('RetryLineageEdgeWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'RetryLineageEdgeWorkflow',
                {'reason': request.reason}
            )
            await deps.repository.save_lineage_edge(request.context.tenant_id, request.lineage_edge)
            response_0 = customers_v1_customer_segment_validation_service_pb2.ValidateCustomerSegmentResponse()
            fields_0: dict[str, Any] = {
                'context': request.context,
                'customer_segment': {'owner': {'email': request.details.notify.email}}
            }
            outgoing_0 = customers_v1_customer_segment_validation_service_pb2.ValidateCustomerSegmentRequest(**fields_0)
            response_0 = await deps.clients.customers_customer_segment_validation.ValidateCustomerSegment(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.details
            response.result.details.update(returned_0_0)
            returned_0_1 = response_0.customer_segment.owner.display_name
            if returned_0_1:
                response.lineage_edge.subject.display_name = returned_0_1
            echoed_0 = request.lineage_edge_id
            response.lineage_edge.lineage_edge_id = echoed_0
            echoed_1 = request.lineage_edge.attributes
            response.lineage_edge.attributes.update(echoed_1)
            return response

    async def handle_signal_lineage_edge_workflow(
        self,
        request: lineage_v1_lineage_edge_workflow_service_pb2.SignalLineageEdgeWorkflowRequest
    ) -> lineage_v1_lineage_edge_workflow_service_pb2.SignalLineageEdgeWorkflowResponse:
        """Signals a lineage edge."""
        deps = self.deps
        response = lineage_v1_lineage_edge_workflow_service_pb2.SignalLineageEdgeWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SignalLineageEdgeWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'SignalLineageEdgeWorkflow',
                {'reason': request.reason}
            )
            await deps.repository.save_lineage_edge(request.context.tenant_id, request.lineage_edge)
            response_0 = customers_v1_household_calculation_service_pb2.EstimateHouseholdResponse()
            response_1 = labeling_v1_labeling_task_service_pb2.UpdateLabelingTaskResponse()
            outgoing_0 = customers_v1_household_calculation_service_pb2.EstimateHouseholdRequest(
                context=request.context,
                household=customers_v1_customers_pb2.Household(
                    children=[
                        customers_v1_customers_pb2.Household(
                            attributes=dict(request.lineage_edge.attributes),
                            children=[
                                customers_v1_customers_pb2.Household(
                                    manager=identity_v1_refs_pb2.UserRef(
                                        display_name=request.lineage_edge.subject.display_name,
                                        user_id=request.context.actor.user_id
                                    )
                                )
                            ],
                            manager=identity_v1_refs_pb2.UserRef(email=request.details.notify.email)
                        )
                    ]
                )
            )
            document_0 = MessageToDict(outgoing_0, preserving_proto_field_name=True)
            outgoing_0 = ParseDict(
                document_0,
                customers_v1_household_calculation_service_pb2.EstimateHouseholdRequest()
            )
            response_0 = await deps.clients.customers_household_calculation.EstimateHousehold(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            for item_1 in request.lineage_edge.measurements:
                outgoing_1 = labeling_v1_labeling_task_service_pb2.UpdateLabelingTaskRequest(
                    context=request.context,
                    labeling_task=labeling_v1_labeling_pb2.LabelingTask(
                        comments=[labeling_v1_labeling_pb2.LabelingTaskComment(created_at=item_1.observed_at)],
                        requester=common_v1_contact_pb2.ContactInfo(email=response_0.household.manager.email)
                    )
                )
                response_1 = await deps.clients.labeling_labeling_task.UpdateLabelingTask(
                    outgoing_1,
                    timeout=deps.settings.timeout
                )
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.result.message = returned_0_0
            returned_0_1 = response_0.result.status
            if returned_0_1:
                response.result.status = returned_0_1
            echoed_0 = request.lineage_edge_id
            response.lineage_edge.lineage_edge_id = echoed_0
            echoed_1 = request.lineage_edge.attributes
            response.lineage_edge.attributes.update(echoed_1)
            return response

    async def handle_start_lineage_edge_workflow(
        self,
        request: lineage_v1_lineage_edge_workflow_service_pb2.StartLineageEdgeWorkflowRequest
    ) -> lineage_v1_lineage_edge_workflow_service_pb2.StartLineageEdgeWorkflowResponse:
        """Starts a lineage edge."""
        deps = self.deps
        response = lineage_v1_lineage_edge_workflow_service_pb2.StartLineageEdgeWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('StartLineageEdgeWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'StartLineageEdgeWorkflow',
                {'reason': request.reason}
            )
            await deps.repository.save_lineage_edge(request.context.tenant_id, request.lineage_edge)
            response_0 = customers_v1_customer_segment_calculation_service_pb2.QuoteCustomerSegmentResponse()
            outgoing_0 = customers_v1_customer_segment_calculation_service_pb2.QuoteCustomerSegmentRequest()
            outgoing_0.context.CopyFrom(request.context)
            outgoing_0.customer_segment.owner.email = request.details.notify.email
            merged_0 = customers_v1_customer_segment_calculation_service_pb2.QuoteCustomerSegmentRequest()
            merged_0.MergeFrom(outgoing_0)
            outgoing_0.CopyFrom(merged_0)
            response_0 = await deps.clients.customers_customer_segment_calculation.QuoteCustomerSegment(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.correlation_id
            if returned_0_0:
                response.lineage_edge.correlation_id = returned_0_0
            returned_0_1 = response_0.result.correlation_id
            if returned_0_1:
                response.result.correlation_id = returned_0_1
            echoed_0 = request.lineage_edge_id
            response.lineage_edge.lineage_edge_id = echoed_0
            echoed_1 = request.lineage_edge.occurred_at
            response.lineage_edge.occurred_at.CopyFrom(echoed_1)
            return response
