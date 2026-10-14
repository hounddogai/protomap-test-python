"""Runs the long-lived workflow that takes a lineage node from start to finish."""

from __future__ import annotations

from collections.abc import AsyncIterator
from functools import partial
from typing import Any
from typing import cast
import asyncio
import logging

from google.protobuf.any_pb2 import Any as AnyMessage
from google.protobuf.json_format import MessageToDict
from google.protobuf.json_format import MessageToJson
from google.protobuf.json_format import Parse
from google.protobuf.json_format import ParseDict
import grpc

from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.customers.v1 import customer_calculation_service_pb2 as customers_v1_customer_calculation_service_pb2
from acme.customers.v1 import customer_query_service_pb2 as customers_v1_customer_query_service_pb2
from acme.customers.v1 import (
    customer_segment_calculation_service_pb2 as customers_v1_customer_segment_calculation_service_pb2,
)
from acme.customers.v1 import (
    customer_segment_calculation_service_pb2_grpc as customers_v1_customer_segment_calculation_service_pb2_grpc,
)
from acme.customers.v1 import (
    customer_segment_validation_service_pb2 as customers_v1_customer_segment_validation_service_pb2,
)
from acme.customers.v1 import customer_validation_service_pb2 as customers_v1_customer_validation_service_pb2
from acme.customers.v1 import customers_pb2 as customers_v1_customers_pb2
from acme.customers.v1 import household_calculation_service_pb2 as customers_v1_household_calculation_service_pb2
from acme.customers.v1 import preference_calculation_service_pb2 as customers_v1_preference_calculation_service_pb2
from acme.datasets.v1 import refs_pb2 as datasets_v1_refs_pb2
from acme.featurestore.v1 import (
    feature_value_calculation_service_pb2 as featurestore_v1_feature_value_calculation_service_pb2,
)
from acme.featurestore.v1 import featurestore_pb2 as featurestore_v1_featurestore_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.keymanagement.v1 import crypto_key_service_pb2 as keymanagement_v1_crypto_key_service_pb2
from acme.lineage.v1 import lineage_edge_approval_service_pb2 as lineage_v1_lineage_edge_approval_service_pb2
from acme.lineage.v1 import lineage_edge_reporting_service_pb2 as lineage_v1_lineage_edge_reporting_service_pb2
from acme.lineage.v1 import lineage_node_approval_service_pb2 as lineage_v1_lineage_node_approval_service_pb2
from acme.lineage.v1 import lineage_node_sync_service_pb2 as lineage_v1_lineage_node_sync_service_pb2
from acme.lineage.v1 import lineage_node_workflow_service_pb2 as lineage_v1_lineage_node_workflow_service_pb2
from acme.lineage.v1 import lineage_node_workflow_service_pb2_grpc as lineage_v1_lineage_node_workflow_service_pb2_grpc
from acme.lineage.v1 import lineage_pb2 as lineage_v1_lineage_pb2
from acme.lineage.v1 import refs_pb2 as lineage_v1_refs_pb2
from acme.recommendations.v1 import (
    recommendation_model_validation_service_pb2 as recommendations_v1_recommendation_model_validation_service_pb2,
)
from acme.recommendations.v1 import recommendations_pb2 as recommendations_v1_recommendations_pb2
from acme.travel.v1 import trip_query_service_pb2 as travel_v1_trip_query_service_pb2
from acme.venues.v1 import venue_query_service_pb2 as venues_v1_venue_query_service_pb2

from acme_data.domains.lineage import hooks
from acme_data.domains.lineage.dependencies import Dependencies
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_id
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class LineageNodeWorkflowServicer(lineage_v1_lineage_node_workflow_service_pb2_grpc.LineageNodeWorkflowServiceServicer):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    async def AdvanceLineageNodeWorkflow(
        self, request: lineage_v1_lineage_node_workflow_service_pb2.AdvanceLineageNodeWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_lineage_node_workflow_service_pb2.AdvanceLineageNodeWorkflowResponse:
        """Advances a lineage node."""
        return await self.handle_advance_lineage_node_workflow(request)

    @rpc_errors
    async def CancelLineageNodeWorkflow(
        self, request: lineage_v1_lineage_node_workflow_service_pb2.CancelLineageNodeWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_lineage_node_workflow_service_pb2.CancelLineageNodeWorkflowResponse:
        """Cancels a lineage node."""
        return await self.handle_cancel_lineage_node_workflow(request)

    @rpc_errors
    @retry_transient
    async def InspectLineageNodeWorkflow(
        self, request: lineage_v1_lineage_node_workflow_service_pb2.InspectLineageNodeWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_lineage_node_workflow_service_pb2.InspectLineageNodeWorkflowResponse:
        """Returns a lineage node."""
        return await self.handle_inspect_lineage_node_workflow(request)

    @rpc_errors
    @retry_transient
    async def ListLineageNodeWorkflows(
        self, request: lineage_v1_lineage_node_workflow_service_pb2.ListLineageNodeWorkflowsRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_lineage_node_workflow_service_pb2.ListLineageNodeWorkflowsResponse:
        """Lists lineage nodes a page at a time."""
        return await self.handle_list_lineage_node_workflows(request)

    @rpc_errors
    async def PauseLineageNodeWorkflow(
        self, request: lineage_v1_lineage_node_workflow_service_pb2.PauseLineageNodeWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_lineage_node_workflow_service_pb2.PauseLineageNodeWorkflowResponse:
        """Pauses a lineage node."""
        return await self.handle_pause_lineage_node_workflow(request)

    @rpc_errors
    async def ResumeLineageNodeWorkflow(
        self, request: lineage_v1_lineage_node_workflow_service_pb2.ResumeLineageNodeWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_lineage_node_workflow_service_pb2.ResumeLineageNodeWorkflowResponse:
        """Resumes a lineage node."""
        return await self.handle_resume_lineage_node_workflow(request)

    @rpc_errors
    async def RetryLineageNodeWorkflow(
        self, request: lineage_v1_lineage_node_workflow_service_pb2.RetryLineageNodeWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_lineage_node_workflow_service_pb2.RetryLineageNodeWorkflowResponse:
        """Retrys a lineage node."""
        return await self.handle_retry_lineage_node_workflow(request)

    @rpc_errors
    async def StartLineageNodeWorkflow(
        self, request: lineage_v1_lineage_node_workflow_service_pb2.StartLineageNodeWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_lineage_node_workflow_service_pb2.StartLineageNodeWorkflowResponse:
        """Starts a lineage node."""
        return await self.handle_start_lineage_node_workflow(request)

    async def handle_advance_lineage_node_workflow(
        self,
        request: lineage_v1_lineage_node_workflow_service_pb2.AdvanceLineageNodeWorkflowRequest
    ) -> lineage_v1_lineage_node_workflow_service_pb2.AdvanceLineageNodeWorkflowResponse:
        """Advances a lineage node."""
        deps = self.deps
        response = lineage_v1_lineage_node_workflow_service_pb2.AdvanceLineageNodeWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('AdvanceLineageNodeWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'AdvanceLineageNodeWorkflow',
                {'reason': request.reason}
            )
            await deps.repository.save_lineage_node(request.context.tenant_id, request.lineage_node)
            response_0 = featurestore_v1_feature_value_calculation_service_pb2.CalculateFeatureValueResponse()
            response_1 = customers_v1_household_calculation_service_pb2.EstimateHouseholdResponse()
            outgoing_0 = featurestore_v1_feature_value_calculation_service_pb2.CalculateFeatureValueRequest(
                context=request.context,
                details=featurestore_v1_feature_value_calculation_service_pb2.CalculateFeatureValueRequest.Details(
                    destination=common_v1_address_pb2.PostalAddress(
                        postal_code=request.lineage_node.location.postal_code
                    )
                ),
                feature_value=featurestore_v1_featurestore_pb2.FeatureValue(
                    subject=datasets_v1_refs_pb2.DatasetRef(display_name=request.lineage_node.manager.display_name)
                )
            )
            send_0 = partial(
                deps.clients.featurestore_feature_value_calculation.CalculateFeatureValue,
                timeout=deps.settings.timeout
            )
            response_0 = await send_0(outgoing_0)
            outgoing_1 = customers_v1_household_calculation_service_pb2.EstimateHouseholdRequest(
                context=request.context,
                household=customers_v1_customers_pb2.Household(
                    children=[
                        customers_v1_customers_pb2.Household(
                            children=[
                                customers_v1_customers_pb2.Household(
                                    location=common_v1_address_pb2.PostalAddress(
                                        region=request.lineage_node.location.region
                                    ),
                                    manager=identity_v1_refs_pb2.UserRef(
                                        display_name=request.lineage_node.manager.display_name
                                    )
                                )
                            ]
                        )
                    ]
                )
            )
            response_1 = await hooks.lineage_node_workflow_advance_lineage_node_workflow1(
                deps.clients.customers_household_calculation,
                outgoing_1,
                deps.settings.timeout
            )
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.outcome.message = returned_0_0
            returned_1_0 = response_1.household.location.lines
            response.lineage_node.location.lines.extend(returned_1_0)
            echoed_0 = request.lineage_node_id
            response.lineage_node.lineage_node_id = echoed_0
            echoed_1 = request.lineage_node.name
            response.lineage_node.name = echoed_1
            return response

    async def handle_cancel_lineage_node_workflow(
        self,
        request: lineage_v1_lineage_node_workflow_service_pb2.CancelLineageNodeWorkflowRequest
    ) -> lineage_v1_lineage_node_workflow_service_pb2.CancelLineageNodeWorkflowResponse:
        """Cancels a lineage node."""
        deps = self.deps
        response = lineage_v1_lineage_node_workflow_service_pb2.CancelLineageNodeWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CancelLineageNodeWorkflow', extra={'fields': {'initiated_by': request.details.initiated_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'CancelLineageNodeWorkflow',
                {'initiated_by': request.details.initiated_by}
            )
            await deps.repository.save_lineage_node(request.context.tenant_id, request.lineage_node)
            response_0 = venues_v1_venue_query_service_pb2.SummarizeVenuesResponse()
            outgoing_0 = venues_v1_venue_query_service_pb2.SummarizeVenuesRequest()
            outgoing_0.context.CopyFrom(request.context)
            outgoing_0.annotations.update(dict(request.annotations))
            outgoing_0.reason = request.reason
            outgoing_0.details.filters.update(dict(request.lineage_node.attributes))
            outgoing_0.context.tenant_id = tenant_id.get()
            response_0 = await deps.clients.venues_venue_query.SummarizeVenues(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.result.message = returned_0_0
            returned_0_1 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_1)
            echoed_0 = request.lineage_node_id
            response.lineage_node.lineage_node_id = echoed_0
            echoed_1 = request.lineage_node.location
            response.lineage_node.location.CopyFrom(echoed_1)
            return response

    async def handle_inspect_lineage_node_workflow(
        self,
        request: lineage_v1_lineage_node_workflow_service_pb2.InspectLineageNodeWorkflowRequest
    ) -> lineage_v1_lineage_node_workflow_service_pb2.InspectLineageNodeWorkflowResponse:
        """Returns a lineage node."""
        deps = self.deps
        response = lineage_v1_lineage_node_workflow_service_pb2.InspectLineageNodeWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('InspectLineageNodeWorkflow', extra={'fields': {'locale': request.context.locale}})
            await deps.repository.audit(
                request.context.tenant_id,
                'InspectLineageNodeWorkflow',
                {'locale': request.context.locale}
            )
            echoed_0 = request.lineage_node_id
            response.lineage_node.lineage_node_id = echoed_0
            return response

    async def handle_list_lineage_node_workflows(
        self,
        request: lineage_v1_lineage_node_workflow_service_pb2.ListLineageNodeWorkflowsRequest
    ) -> lineage_v1_lineage_node_workflow_service_pb2.ListLineageNodeWorkflowsResponse:
        """Lists lineage nodes a page at a time."""
        deps = self.deps
        response = lineage_v1_lineage_node_workflow_service_pb2.ListLineageNodeWorkflowsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ListLineageNodeWorkflows', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ListLineageNodeWorkflows',
                {'order_by': request.order_by}
            )
            response_0 = lineage_v1_lineage_node_approval_service_pb2.ListPendingLineageNodesResponse()
            outgoing_0 = lineage_v1_lineage_node_approval_service_pb2.ListPendingLineageNodesRequest(
                context=request.context,
                filter=lineage_v1_lineage_node_approval_service_pb2.ListPendingLineageNodesRequest.Filter(
                    region=request.filter.region
                )
            )
            response_0 = await deps.clients.lineage_lineage_node_approval.ListPendingLineageNodes(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.details
            response.result.details.update(returned_0_0)
            return response

    async def handle_pause_lineage_node_workflow(
        self,
        request: lineage_v1_lineage_node_workflow_service_pb2.PauseLineageNodeWorkflowRequest
    ) -> lineage_v1_lineage_node_workflow_service_pb2.PauseLineageNodeWorkflowResponse:
        """Pauses a lineage node."""
        deps = self.deps
        response = lineage_v1_lineage_node_workflow_service_pb2.PauseLineageNodeWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('PauseLineageNodeWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'PauseLineageNodeWorkflow',
                {'reason': request.reason}
            )
            await deps.repository.save_lineage_node(request.context.tenant_id, request.lineage_node)
            response_0 = recommendations_v1_recommendation_model_validation_service_pb2.PreviewRecommendationModelResponse()
            response_1 = customers_v1_preference_calculation_service_pb2.CalculatePreferenceResponse()
            response_2 = lineage_v1_lineage_node_approval_service_pb2.EscalateLineageNodeResponse()
            response_3 = lineage_v1_lineage_node_sync_service_pb2.ResolveLineageNodeConflictResponse()
            outgoing_0 = recommendations_v1_recommendation_model_validation_service_pb2.PreviewRecommendationModelRequest(
                context=request.context,
                recommendation_model=recommendations_v1_recommendations_pb2.RecommendationModel(
                    address=common_v1_address_pb2.PostalAddress(
                        country_code=request.lineage_node.location.country_code
                    ),
                    audit=common_v1_audit_pb2.AuditInfo(updated_at=request.lineage_node.audit.updated_at)
                )
            )
            outgoing_1 = customers_v1_preference_calculation_service_pb2.CalculatePreferenceRequest(
                context=request.context,
                preference=customers_v1_customers_pb2.Preference(
                    audit=common_v1_audit_pb2.AuditInfo(
                        created_at=request.lineage_node.audit.created_at,
                        etag=request.lineage_node.audit.etag
                    )
                )
            )
            response_0, response_1 = await asyncio.gather(
                deps.clients.recommendations_recommendation_model_validation.PreviewRecommendationModel(
                    outgoing_0,
                    timeout=deps.settings.timeout
                ),
                deps.clients.customers_preference_calculation.CalculatePreference(
                    outgoing_1,
                    timeout=deps.settings.timeout
                ),
            )
            outgoing_2 = lineage_v1_lineage_node_approval_service_pb2.EscalateLineageNodeRequest(
                context=request.context,
                lineage_node=lineage_v1_lineage_pb2.LineageNode(
                    children=[
                        lineage_v1_lineage_pb2.LineageNode(
                            children=[
                                lineage_v1_lineage_pb2.LineageNode(
                                    manager=identity_v1_refs_pb2.UserRef(
                                        display_name=response_1.preference.owner.display_name
                                    )
                                )
                            ]
                        )
                    ]
                )
            )
            response_2 = cast(lineage_v1_lineage_node_approval_service_pb2.EscalateLineageNodeResponse, await deps.bus.request(
                'acme.lineage.v1.LineageNodeWorkflowService/PauseLineageNodeWorkflow/2', outgoing_2, deps.settings.timeout,
            ))
            outgoing_3 = lineage_v1_lineage_node_sync_service_pb2.ResolveLineageNodeConflictRequest(
                context=request.context,
                lineage_node=lineage_v1_lineage_pb2.LineageNode(
                    children=[
                        lineage_v1_lineage_pb2.LineageNode(
                            children=[
                                lineage_v1_lineage_pb2.LineageNode(
                                    location=common_v1_address_pb2.PostalAddress(
                                        postal_code=response_2.lineage_node.location.postal_code
                                    )
                                )
                            ]
                        )
                    ]
                )
            )
            response_3 = await deps.clients.lineage_lineage_node_sync.ResolveLineageNodeConflict(
                outgoing_3,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.outcome.next_steps
            response.outcome.next_steps.extend(returned_0_0)
            returned_0_1 = response_0.recommendation_model.address.postal_code
            if returned_0_1:
                response.lineage_node.location.postal_code = returned_0_1
            returned_1_0 = response_1.preference.audit.created_at
            returned_1_0_part_1 = response.lineage_node.children.add()
            returned_1_0_part_2 = returned_1_0_part_1.children.add()
            if returned_1_0.ListFields():
                returned_1_0_part_2.audit.created_at.MergeFrom(returned_1_0)
            returned_2_0 = response_2.lineage_node.location.country_code
            if returned_2_0:
                response.lineage_node.location.country_code = returned_2_0
            returned_3_0 = response_3.lineage_node.audit.etag
            if returned_3_0:
                response.lineage_node.audit.etag = returned_3_0
            returned_3_1 = response_3.lineage_node.path
            returned_3_1_part_1 = response.lineage_node.children.add()
            returned_3_1_part_2 = returned_3_1_part_1.children.add()
            returned_3_1_part_2.path.extend(returned_3_1)
            echoed_0 = request.lineage_node_id
            response.lineage_node.lineage_node_id = echoed_0
            echoed_1 = request.lineage_node.parent_id
            response.lineage_node.parent_id = echoed_1
            return response

    async def handle_resume_lineage_node_workflow(
        self,
        request: lineage_v1_lineage_node_workflow_service_pb2.ResumeLineageNodeWorkflowRequest
    ) -> lineage_v1_lineage_node_workflow_service_pb2.ResumeLineageNodeWorkflowResponse:
        """Resumes a lineage node."""
        deps = self.deps
        response = lineage_v1_lineage_node_workflow_service_pb2.ResumeLineageNodeWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ResumeLineageNodeWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ResumeLineageNodeWorkflow',
                {'reason': request.reason}
            )
            await deps.repository.save_lineage_node(request.context.tenant_id, request.lineage_node)
            response_0 = lineage_v1_lineage_edge_approval_service_pb2.RejectLineageEdgeResponse()
            response_1 = lineage_v1_lineage_edge_approval_service_pb2.EscalateLineageEdgeResponse()
            response_2 = customers_v1_household_calculation_service_pb2.SimulateHouseholdResponse()
            outgoing_0 = lineage_v1_lineage_edge_approval_service_pb2.RejectLineageEdgeRequest(
                context=request.context,
                details=lineage_v1_lineage_edge_approval_service_pb2.RejectLineageEdgeRequest.Details(
                    approver=identity_v1_refs_pb2.UserRef(email=request.lineage_node.manager.email)
                ),
                lineage_edge=lineage_v1_lineage_pb2.LineageEdge(
                    subject=lineage_v1_refs_pb2.ImpactRef(display_name=request.lineage_node.manager.display_name)
                )
            )
            method_name_0 = 'RejectLineageEdge'
            response_0 = await getattr(
                deps.clients.lineage_lineage_edge_approval,
                method_name_0
            )(outgoing_0, timeout=deps.settings.timeout)
            fields_1: dict[str, Any] = {
                'context': request.context,
                'details': {'approver': {'email': request.details.notify.email}},
                'lineage_edge': {
                    'subject': {
                        'display_name': request.lineage_node.manager.display_name,
                        'priority': response_0.lineage_edge.subject.priority
                    }
                }
            }
            outgoing_1 = lineage_v1_lineage_edge_approval_service_pb2.EscalateLineageEdgeRequest(**fields_1)
            response_1 = await deps.clients.lineage_lineage_edge_approval.EscalateLineageEdge(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = customers_v1_household_calculation_service_pb2.SimulateHouseholdRequest(
                context=request.context,
                household=customers_v1_customers_pb2.Household(
                    children=[
                        customers_v1_customers_pb2.Household(
                            children=[
                                customers_v1_customers_pb2.Household(
                                    audit=common_v1_audit_pb2.AuditInfo(etag=request.lineage_node.audit.etag),
                                    location=common_v1_address_pb2.PostalAddress(
                                        lines=list(request.lineage_node.location.lines),
                                        locality=request.lineage_node.location.locality
                                    ),
                                    manager=identity_v1_refs_pb2.UserRef(email=request.details.notify.email)
                                )
                            ]
                        )
                    ]
                )
            )
            document_2 = MessageToDict(outgoing_2, preserving_proto_field_name=True)
            outgoing_2 = ParseDict(
                document_2,
                customers_v1_household_calculation_service_pb2.SimulateHouseholdRequest()
            )
            response_2 = await deps.clients.customers_household_calculation.SimulateHousehold(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.result.message = returned_0_0
            returned_1_0 = response_1.result.reference_ids
            response.result.reference_ids.extend(returned_1_0)
            returned_2_0 = response_2.household.audit.updated_at
            returned_2_0_part_1 = response.lineage_node.children.add()
            if returned_2_0.ListFields():
                returned_2_0_part_1.audit.updated_at.MergeFrom(returned_2_0)
            echoed_0 = request.lineage_node_id
            response.lineage_node.lineage_node_id = echoed_0
            echoed_1 = request.lineage_node.location
            response.lineage_node.location.CopyFrom(echoed_1)
            return response

    async def handle_retry_lineage_node_workflow(
        self,
        request: lineage_v1_lineage_node_workflow_service_pb2.RetryLineageNodeWorkflowRequest
    ) -> lineage_v1_lineage_node_workflow_service_pb2.RetryLineageNodeWorkflowResponse:
        """Retrys a lineage node."""
        deps = self.deps
        response = lineage_v1_lineage_node_workflow_service_pb2.RetryLineageNodeWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('RetryLineageNodeWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'RetryLineageNodeWorkflow',
                {'reason': request.reason}
            )
            await deps.repository.save_lineage_node(request.context.tenant_id, request.lineage_node)
            response_0 = customers_v1_customer_query_service_pb2.SuggestCustomersResponse()
            response_1 = travel_v1_trip_query_service_pb2.CountTripsResponse()
            response_2 = customers_v1_customer_validation_service_pb2.LintCustomersResponse()
            response_3 = customers_v1_customer_segment_calculation_service_pb2.CalculateCustomerSegmentResponse()
            outgoing_0 = customers_v1_customer_query_service_pb2.SuggestCustomersRequest(
                context=request.context,
                filter=customers_v1_customer_query_service_pb2.SuggestCustomersRequest.Filter(
                    created_after=request.lineage_node.audit.updated_at,
                    owner_id=request.lineage_node.manager.user_id,
                    region=request.lineage_node.location.region
                )
            )
            document_0 = MessageToJson(outgoing_0, preserving_proto_field_name=True)
            outgoing_0 = Parse(document_0, customers_v1_customer_query_service_pb2.SuggestCustomersRequest())
            response_0 = await deps.clients.customers_customer_query.SuggestCustomers(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = travel_v1_trip_query_service_pb2.CountTripsRequest()
            outgoing_1.context.CopyFrom(request.context)
            outgoing_1.filter.region = request.lineage_node.location.region
            outgoing_1.filter.created_after.CopyFrom(request.lineage_node.audit.created_at)
            outgoing_1.filter.labels.update(dict(request.details.parameters))
            outgoing_1.filter.owner_id = request.lineage_node.manager.user_id
            merged_1 = travel_v1_trip_query_service_pb2.CountTripsRequest()
            merged_1.MergeFrom(outgoing_1)
            outgoing_1.CopyFrom(merged_1)
            response_1 = await deps.clients.travel_trip_query.CountTrips(outgoing_1, timeout=deps.settings.timeout)
            outgoing_2 = customers_v1_customer_validation_service_pb2.LintCustomersRequest(
                context=request.context,
                customer=customers_v1_customers_pb2.Customer(
                    audit=common_v1_audit_pb2.AuditInfo(etag=request.lineage_node.audit.etag),
                    contact=common_v1_contact_pb2.ContactInfo(phone=request.details.notify.phone),
                    primary_address=common_v1_address_pb2.PostalAddress(
                        postal_code=request.lineage_node.location.postal_code,
                        recipient=request.lineage_node.location.recipient
                    )
                )
            )
            envelope_2 = AnyMessage()
            envelope_2.Pack(outgoing_2)
            outgoing_2 = customers_v1_customer_validation_service_pb2.LintCustomersRequest()
            if not envelope_2.Unpack(outgoing_2):
                raise ValueError("partner envelope contains the wrong request type")
            response_2 = await deps.clients.customers_customer_validation.LintCustomers(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            outgoing_3 = customers_v1_customer_segment_calculation_service_pb2.CalculateCustomerSegmentRequest(
                context=request.context,
                customer_segment=customers_v1_customers_pb2.CustomerSegment(
                    audit=common_v1_audit_pb2.AuditInfo(
                        created_by=request.lineage_node.audit.created_by,
                        etag=response_2.customer.audit.etag,
                        updated_at=response_2.customer.audit.updated_at
                    ),
                    owner=identity_v1_refs_pb2.UserRef(email=request.lineage_node.manager.email)
                )
            )
            registered_3 = cast(
                customers_v1_customer_segment_calculation_service_pb2_grpc.CustomerSegmentCalculationServiceStub,
                deps.clients.registry['acme.customers.v1.CustomerSegmentCalculationService']
            )
            response_3 = await registered_3.CalculateCustomerSegment(outgoing_3, timeout=deps.settings.timeout)
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.outcome.message = returned_0_0
            returned_1_0 = response_1.result.message
            if returned_1_0:
                response.outcome.message = returned_1_0
            returned_2_0 = response_2.customer.audit.updated_at
            if returned_2_0.ListFields():
                response.lineage_node.audit.updated_at.MergeFrom(returned_2_0)
            returned_3_0 = response_3.customer_segment.owner.email
            returned_3_0_part_1 = response.lineage_node.children.add()
            if returned_3_0:
                returned_3_0_part_1.manager.email = returned_3_0
            echoed_0 = request.lineage_node_id
            response.lineage_node.lineage_node_id = echoed_0
            echoed_1 = request.lineage_node.attributes
            response.lineage_node.attributes.update(echoed_1)
            return response

    async def handle_start_lineage_node_workflow(
        self,
        request: lineage_v1_lineage_node_workflow_service_pb2.StartLineageNodeWorkflowRequest
    ) -> lineage_v1_lineage_node_workflow_service_pb2.StartLineageNodeWorkflowResponse:
        """Starts a lineage node."""
        deps = self.deps
        response = lineage_v1_lineage_node_workflow_service_pb2.StartLineageNodeWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('StartLineageNodeWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'StartLineageNodeWorkflow',
                {'reason': request.reason}
            )
            await deps.repository.save_lineage_node(request.context.tenant_id, request.lineage_node)
            response_0 = customers_v1_customer_segment_validation_service_pb2.ExplainCustomerSegmentDecisionResponse()
            response_1 = customers_v1_customer_calculation_service_pb2.EstimateCustomerResponse()
            response_2 = keymanagement_v1_crypto_key_service_pb2.WatchCryptoKeysResponse()
            response_3 = lineage_v1_lineage_edge_reporting_service_pb2.CountLineageEdgeTotalsResponse()
            outgoing_0 = customers_v1_customer_segment_validation_service_pb2.ExplainCustomerSegmentDecisionRequest(
                context=request.context,
                customer_segment=customers_v1_customers_pb2.CustomerSegment(
                    owner=identity_v1_refs_pb2.UserRef(user_id=request.lineage_node.manager.user_id)
                ),
                details=customers_v1_customer_segment_validation_service_pb2.ExplainCustomerSegmentDecisionRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(
                        preferred_channel=request.details.notify.preferred_channel
                    )
                )
            )
            outgoing_1 = customers_v1_customer_calculation_service_pb2.EstimateCustomerRequest(
                context=request.context,
                customer=customers_v1_customers_pb2.Customer(
                    relationship_manager=identity_v1_refs_pb2.UserRef(user_id=request.lineage_node.manager.user_id)
                ),
                details=customers_v1_customer_calculation_service_pb2.EstimateCustomerRequest.Details(
                    destination=common_v1_address_pb2.PostalAddress(lines=list(request.lineage_node.location.lines))
                )
            )
            outgoing_3 = lineage_v1_lineage_edge_reporting_service_pb2.CountLineageEdgeTotalsRequest(
                context=request.context,
                filter=lineage_v1_lineage_edge_reporting_service_pb2.CountLineageEdgeTotalsRequest.Filter(
                    created_after=request.lineage_node.audit.updated_at,
                    region=request.lineage_node.location.region
                )
            )
            response_0, response_1, response_3 = await asyncio.gather(
                deps.clients.customers_customer_segment_validation.ExplainCustomerSegmentDecision(
                    outgoing_0,
                    timeout=deps.settings.timeout
                ),
                deps.clients.customers_customer_calculation.EstimateCustomer(outgoing_1, timeout=deps.settings.timeout),
                deps.clients.lineage_lineage_edge_reporting.CountLineageEdgeTotals(
                    outgoing_3,
                    timeout=deps.settings.timeout
                ),
            )
            outgoing_2 = keymanagement_v1_crypto_key_service_pb2.WatchCryptoKeysRequest(
                context=request.context,
                filter=keymanagement_v1_crypto_key_service_pb2.WatchCryptoKeysRequest.Filter(
                    region=request.lineage_node.location.region
                ),
                subscriber=common_v1_contact_pb2.ContactInfo(
                    email=response_0.customer_segment.owner.email,
                    name=response_1.customer.contact.name,
                    phone=response_1.customer.contact.phone
                )
            )
            async for chunk_2 in deps.clients.keymanagement_crypto_key.WatchCryptoKeys(
                outgoing_2,
                timeout=deps.settings.timeout
            ):
                response_2 = chunk_2
            returned_0_0 = response_0.customer_segment.audit.created_by
            if returned_0_0:
                response.lineage_node.audit.created_by = returned_0_0
            returned_1_0 = response_1.customer.primary_address.country_code
            returned_1_0_part_1 = response.lineage_node.children.add()
            returned_1_0_part_2 = returned_1_0_part_1.children.add()
            if returned_1_0:
                returned_1_0_part_2.location.country_code = returned_1_0
            returned_3_0 = response_3.result.message
            if returned_3_0:
                response.result.message = returned_3_0
            returned_3_1 = response_3.result.status
            if returned_3_1:
                response.outcome.status = returned_3_1
            echoed_0 = request.lineage_node_id
            response.lineage_node.lineage_node_id = echoed_0
            echoed_1 = request.lineage_node.attributes
            response.lineage_node.attributes.update(echoed_1)
            return response
