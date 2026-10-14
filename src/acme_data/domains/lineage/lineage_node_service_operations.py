"""Functional operations behind LineageNodeService."""

from __future__ import annotations

from functools import partial
from typing import cast
import logging

from google.protobuf.json_format import MessageToDict
from google.protobuf.json_format import ParseDict

from acme.audit.v1 import audit_event_query_service_pb2 as audit_v1_audit_event_query_service_pb2
from acme.authorization.v1 import access_policy_service_pb2 as authorization_v1_access_policy_service_pb2
from acme.authorization.v1 import (
    access_policy_validation_service_pb2 as authorization_v1_access_policy_validation_service_pb2,
)
from acme.careplans.v1 import care_plan_calculation_service_pb2 as careplans_v1_care_plan_calculation_service_pb2
from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.common.v1 import paging_pb2 as common_v1_paging_pb2
from acme.concessions.v1 import (
    concession_stand_calculation_service_pb2 as concessions_v1_concession_stand_calculation_service_pb2,
)
from acme.concessions.v1 import concessions_pb2 as concessions_v1_concessions_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.lineage.v1 import impact_validation_service_pb2 as lineage_v1_impact_validation_service_pb2
from acme.lineage.v1 import lineage_edge_calculation_service_pb2 as lineage_v1_lineage_edge_calculation_service_pb2
from acme.lineage.v1 import lineage_edge_query_service_pb2 as lineage_v1_lineage_edge_query_service_pb2
from acme.lineage.v1 import lineage_edge_validation_service_pb2 as lineage_v1_lineage_edge_validation_service_pb2
from acme.lineage.v1 import lineage_node_calculation_service_pb2 as lineage_v1_lineage_node_calculation_service_pb2
from acme.lineage.v1 import lineage_node_service_pb2 as lineage_v1_lineage_node_service_pb2
from acme.lineage.v1 import lineage_node_validation_service_pb2 as lineage_v1_lineage_node_validation_service_pb2
from acme.lineage.v1 import lineage_pb2 as lineage_v1_lineage_pb2
from acme.metrics.v1 import metric_series_query_service_pb2 as metrics_v1_metric_series_query_service_pb2
from acme.metrics.v1 import metric_series_query_service_pb2_grpc as metrics_v1_metric_series_query_service_pb2_grpc
from acme.venues.v1 import venue_validation_service_pb2 as venues_v1_venue_validation_service_pb2

from acme_data.domains.lineage.adapters import LineageNodeBatchGetLineageNodes1Adapter
from acme_data.domains.lineage.dependencies import Dependencies
from acme_data.platform.rpc import async_messages
from acme_data.platform.tenancy import tenant_id
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


async def handle_batch_create_lineage_nodes(
    deps: Dependencies,
    request: lineage_v1_lineage_node_service_pb2.BatchCreateLineageNodesRequest
) -> lineage_v1_lineage_node_service_pb2.BatchCreateLineageNodesResponse:
    """Takes a stream of lineage nodes and answers once at the end."""
    response = lineage_v1_lineage_node_service_pb2.BatchCreateLineageNodesResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('BatchCreateLineageNodes', extra={'fields': {'sequence': request.sequence}})
        await deps.repository.audit(
            request.context.tenant_id,
            'BatchCreateLineageNodes',
            {'sequence': request.sequence}
        )
        if request.WhichOneof('chunk') == 'record':
            await deps.repository.save_lineage_node(request.context.tenant_id, request.record)
        response_0 = lineage_v1_lineage_edge_validation_service_pb2.NormalizeLineageEdgeResponse()
        response_1 = authorization_v1_access_policy_service_pb2.WatchAccessPoliciesResponse()
        response_2 = authorization_v1_access_policy_validation_service_pb2.ValidateAccessPolicyResponse()
        outgoing_0 = lineage_v1_lineage_edge_validation_service_pb2.NormalizeLineageEdgeRequest(
            context=request.context,
            details=lineage_v1_lineage_edge_validation_service_pb2.NormalizeLineageEdgeRequest.Details(
                contact=common_v1_contact_pb2.ContactInfo(
                    email=request.header.submitted_by.email,
                    preferred_channel=request.header.submitted_by.preferred_channel
                )
            ),
            lineage_edge=lineage_v1_lineage_pb2.LineageEdge(attributes=dict(request.record.attributes))
        )
        response_0 = await deps.clients.lineage_lineage_edge_validation.NormalizeLineageEdge(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = authorization_v1_access_policy_service_pb2.WatchAccessPoliciesRequest(
            context=request.context,
            subscriber=common_v1_contact_pb2.ContactInfo(name=request.header.submitted_by.name)
        )
        async for chunk_1 in deps.clients.authorization_access_policy.WatchAccessPolicies(
            outgoing_1,
            timeout=deps.settings.timeout
        ):
            response_1 = chunk_1
        outgoing_2 = authorization_v1_access_policy_validation_service_pb2.ValidateAccessPolicyRequest()
        outgoing_2.context.CopyFrom(request.context)
        if request.WhichOneof('chunk') == 'record':
            outgoing_2.access_policy.audit.updated_by = request.record.audit.updated_by
        if request.WhichOneof('chunk') == 'record':
            outgoing_2.access_policy.audit.created_by = request.record.audit.created_by
        if request.WhichOneof('chunk') == 'record':
            outgoing_2.access_policy.owner.email = request.record.manager.email
        response_2 = await deps.clients.authorization_access_policy_validation.ValidateAccessPolicy(
            outgoing_2,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.result.message
        if returned_0_0:
            response.result.message = returned_0_0
        returned_2_0 = response_2.result.details
        response.result.details.update(returned_2_0)
        returned_2_1 = response_2.result.reference_ids
        response.result.reference_ids.extend(returned_2_1)
        return response


async def handle_batch_get_lineage_nodes(
    deps: Dependencies,
    request: lineage_v1_lineage_node_service_pb2.BatchGetLineageNodesRequest
) -> lineage_v1_lineage_node_service_pb2.BatchGetLineageNodesResponse:
    """Returns several lineage nodes at once."""
    response = lineage_v1_lineage_node_service_pb2.BatchGetLineageNodesResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('BatchGetLineageNodes', extra={'fields': {'domain': 'lineage'}})
        await deps.repository.audit(request.context.tenant_id, 'BatchGetLineageNodes', {})
        response_0 = audit_v1_audit_event_query_service_pb2.CountAuditEventsResponse()
        response_1 = lineage_v1_lineage_edge_validation_service_pb2.ScoreLineageEdgeResponse()
        outgoing_0 = audit_v1_audit_event_query_service_pb2.CountAuditEventsRequest(
            context=request.context,
            filter=audit_v1_audit_event_query_service_pb2.CountAuditEventsRequest.Filter(
                labels=dict(request.context.baggage),
                owner_id=request.context.actor.user_id
            )
        )
        response_0 = await deps.clients.audit_audit_event_query.CountAuditEvents(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = lineage_v1_lineage_edge_validation_service_pb2.ScoreLineageEdgeRequest(
            context=request.context,
            lineage_edge=lineage_v1_lineage_pb2.LineageEdge(
                attributes=dict(response_0.result.details),
                correlation_id=response_0.result.correlation_id
            )
        )
        response_1 = await LineageNodeBatchGetLineageNodes1Adapter(
            deps.clients.lineage_lineage_edge_validation,
            deps.settings.timeout
        )(outgoing_1)
        returned_0_0 = response_0.result.reference_ids
        response.result.reference_ids.extend(returned_0_0)
        returned_0_1 = response_0.result.correlation_id
        if returned_0_1:
            response.result.correlation_id = returned_0_1
        returned_1_0 = response_1.lineage_edge.attributes
        returned_1_0_part_0 = response.lineage_nodes.add()
        returned_1_0_part_1 = returned_1_0_part_0.children.add()
        returned_1_0_part_1.attributes.update(returned_1_0)
        returned_1_1 = response_1.lineage_edge.correlation_id
        if returned_1_1:
            response.result.correlation_id = returned_1_1
        return response


async def handle_clone_lineage_node(
    deps: Dependencies,
    request: lineage_v1_lineage_node_service_pb2.CloneLineageNodeRequest
) -> lineage_v1_lineage_node_service_pb2.CloneLineageNodeResponse:
    """Creates a lineage node."""
    response = lineage_v1_lineage_node_service_pb2.CloneLineageNodeResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('CloneLineageNode', extra={'fields': {'request_id': request.request_id}})
        await deps.repository.audit(request.context.tenant_id, 'CloneLineageNode', {'request_id': request.request_id})
        await deps.repository.save_lineage_node(request.context.tenant_id, request.lineage_node)
        response_0 = lineage_v1_lineage_node_calculation_service_pb2.EstimateLineageNodeResponse()
        outgoing_0 = lineage_v1_lineage_node_calculation_service_pb2.EstimateLineageNodeRequest(
            context=request.context,
            lineage_node=lineage_v1_lineage_pb2.LineageNode(
                children=[
                    lineage_v1_lineage_pb2.LineageNode(
                        audit=common_v1_audit_pb2.AuditInfo(updated_by=request.lineage_node.audit.updated_by),
                        children=[
                            lineage_v1_lineage_pb2.LineageNode(
                                audit=common_v1_audit_pb2.AuditInfo(
                                    created_by=request.lineage_node.audit.created_by,
                                    updated_at=request.lineage_node.audit.updated_at
                                ),
                                children=[
                                    lineage_v1_lineage_pb2.LineageNode(
                                        lineage_node_id=request.lineage_node.lineage_node_id
                                    )
                                ]
                            )
                        ]
                    )
                ]
            )
        )
        response_0 = await deps.clients.lineage_lineage_node_calculation.EstimateLineageNode(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.lineage_node.path
        response.lineage_node.path.extend(returned_0_0)
        echoed_0 = request.lineage_node.depth
        response.lineage_node.depth = echoed_0
        echoed_1 = request.lineage_node.parent_id
        response.lineage_node.parent_id = echoed_1
        return response


async def handle_create_lineage_node(
    deps: Dependencies,
    request: lineage_v1_lineage_node_service_pb2.CreateLineageNodeRequest
) -> lineage_v1_lineage_node_service_pb2.CreateLineageNodeResponse:
    """Creates a lineage node."""
    response = lineage_v1_lineage_node_service_pb2.CreateLineageNodeResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('CreateLineageNode', extra={'fields': {'request_id': request.request_id}})
        await deps.repository.audit(request.context.tenant_id, 'CreateLineageNode', {'request_id': request.request_id})
        await deps.repository.save_lineage_node(request.context.tenant_id, request.lineage_node)
        response_0 = lineage_v1_lineage_edge_calculation_service_pb2.QuoteLineageEdgeResponse()
        response_1 = lineage_v1_lineage_node_validation_service_pb2.ExplainLineageNodeDecisionResponse()
        outgoing_0 = lineage_v1_lineage_edge_calculation_service_pb2.QuoteLineageEdgeRequest(
            context=request.context,
            details=lineage_v1_lineage_edge_calculation_service_pb2.QuoteLineageEdgeRequest.Details(
                destination=common_v1_address_pb2.PostalAddress(lines=list(request.lineage_node.location.lines))
            )
        )
        response_0 = await deps.clients.lineage_lineage_edge_calculation.QuoteLineageEdge(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = lineage_v1_lineage_node_validation_service_pb2.ExplainLineageNodeDecisionRequest(
            context=request.context,
            lineage_node=lineage_v1_lineage_pb2.LineageNode(
                children=[
                    lineage_v1_lineage_pb2.LineageNode(
                        children=[
                            lineage_v1_lineage_pb2.LineageNode(
                                audit=common_v1_audit_pb2.AuditInfo(
                                    created_at=request.lineage_node.audit.created_at,
                                    updated_by=request.lineage_node.audit.updated_by
                                ),
                                location=common_v1_address_pb2.PostalAddress(
                                    locality=request.lineage_node.location.locality
                                ),
                                manager=identity_v1_refs_pb2.UserRef(
                                    display_name=response_0.lineage_edge.subject.display_name
                                )
                            )
                        ]
                    )
                ]
            )
        )
        method_name_1 = 'ExplainLineageNodeDecision'
        response_1 = await getattr(
            deps.clients.lineage_lineage_node_validation,
            method_name_1
        )(outgoing_1, timeout=deps.settings.timeout)
        returned_0_0 = response_0.lineage_edge.attributes
        returned_0_0_part_1 = response.lineage_node.children.add()
        returned_0_0_part_1.attributes.update(returned_0_0)
        returned_1_0 = response_1.result.message
        if returned_1_0:
            response.result.message = returned_1_0
        returned_1_1 = response_1.lineage_node.location.region
        returned_1_1_part_1 = response.lineage_node.children.add()
        if returned_1_1:
            returned_1_1_part_1.location.region = returned_1_1
        echoed_0 = request.lineage_node.parent_id
        response.lineage_node.parent_id = echoed_0
        echoed_1 = request.lineage_node.name
        response.lineage_node.name = echoed_1
        return response


async def handle_delete_lineage_node(
    deps: Dependencies,
    request: lineage_v1_lineage_node_service_pb2.DeleteLineageNodeRequest
) -> lineage_v1_lineage_node_service_pb2.DeleteLineageNodeResponse:
    """Deletes a lineage node."""
    response = lineage_v1_lineage_node_service_pb2.DeleteLineageNodeResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('DeleteLineageNode', extra={'fields': {'force': request.force}})
        await deps.repository.audit(request.context.tenant_id, 'DeleteLineageNode', {'force': request.force})
        response_0 = lineage_v1_impact_validation_service_pb2.ValidateImpactResponse()
        response_1 = audit_v1_audit_event_query_service_pb2.BrowseAuditEventsResponse()
        outgoing_0 = lineage_v1_impact_validation_service_pb2.ValidateImpactRequest(
            context=request.context,
            impact=lineage_v1_lineage_pb2.Impact(audit=common_v1_audit_pb2.AuditInfo(etag=request.etag))
        )
        response_0 = await deps.clients.lineage_impact_validation.ValidateImpact(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = audit_v1_audit_event_query_service_pb2.BrowseAuditEventsRequest(
            context=request.context,
            filter=audit_v1_audit_event_query_service_pb2.BrowseAuditEventsRequest.Filter(
                created_after=response_0.outcome.effective_at,
                labels=dict(response_0.impact.custom_fields),
                owner_id=response_0.impact.customer.customer_id
            )
        )
        document_1 = MessageToDict(outgoing_1, preserving_proto_field_name=True)
        outgoing_1 = ParseDict(document_1, audit_v1_audit_event_query_service_pb2.BrowseAuditEventsRequest())
        response_1 = await deps.clients.audit_audit_event_query.BrowseAuditEvents(
            outgoing_1,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.outcome.effective_at
        if returned_0_0.ListFields():
            response.effective_at.MergeFrom(returned_0_0)
        returned_0_1 = response_0.result.status
        if returned_0_1:
            response.result.status = returned_0_1
        returned_1_0 = response_1.result.reference_ids
        response.result.reference_ids.extend(returned_1_0)
        returned_1_1 = response_1.result.details
        response.result.details.update(returned_1_1)
        return response


async def handle_get_lineage_node(
    deps: Dependencies,
    request: lineage_v1_lineage_node_service_pb2.GetLineageNodeRequest
) -> lineage_v1_lineage_node_service_pb2.GetLineageNodeResponse:
    """Returns a lineage node."""
    response = lineage_v1_lineage_node_service_pb2.GetLineageNodeResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('GetLineageNode', extra={'fields': {'domain': 'lineage'}})
        await deps.repository.audit(request.context.tenant_id, 'GetLineageNode', {})
        response_0 = lineage_v1_lineage_node_validation_service_pb2.ValidateLineageNodeResponse()
        response_1 = venues_v1_venue_validation_service_pb2.ValidateVenueResponse()
        outgoing_0 = lineage_v1_lineage_node_validation_service_pb2.ValidateLineageNodeRequest(
            context=request.context,
            details=lineage_v1_lineage_node_validation_service_pb2.ValidateLineageNodeRequest.Details(
                contact=common_v1_contact_pb2.ContactInfo(email=request.context.actor.email),
                locale=request.context.locale
            ),
            lineage_node=lineage_v1_lineage_pb2.LineageNode(
                children=[
                    lineage_v1_lineage_pb2.LineageNode(
                        children=[
                            lineage_v1_lineage_pb2.LineageNode(
                                children=[lineage_v1_lineage_pb2.LineageNode(lineage_node_id=request.lineage_node_id)],
                                manager=identity_v1_refs_pb2.UserRef(user_id=request.context.actor.user_id)
                            )
                        ]
                    )
                ]
            )
        )
        response_0 = await deps.clients.lineage_lineage_node_validation.ValidateLineageNode(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = venues_v1_venue_validation_service_pb2.ValidateVenueRequest()
        outgoing_1.context.CopyFrom(request.context)
        outgoing_1.venue.audit.etag = response_0.lineage_node.audit.etag
        merged_1 = venues_v1_venue_validation_service_pb2.ValidateVenueRequest()
        merged_1.MergeFrom(outgoing_1)
        outgoing_1.CopyFrom(merged_1)
        response_1 = await deps.clients.venues_venue_validation.ValidateVenue(outgoing_1, timeout=deps.settings.timeout)
        returned_0_0 = response_0.lineage_node.name
        returned_0_0_part_1 = response.lineage_node.children.add()
        if returned_0_0:
            returned_0_0_part_1.name = returned_0_0
        returned_0_1 = response_0.lineage_node.parent_id
        returned_0_1_part_1 = response.lineage_node.children.add()
        returned_0_1_part_2 = returned_0_1_part_1.children.add()
        returned_0_1_part_3 = returned_0_1_part_2.children.add()
        if returned_0_1:
            returned_0_1_part_3.parent_id = returned_0_1
        returned_1_0 = response_1.venue.address.postal_code
        returned_1_0_part_1 = response.lineage_node.children.add()
        if returned_1_0:
            returned_1_0_part_1.location.postal_code = returned_1_0
        returned_1_1 = response_1.result.reference_ids
        response.result.reference_ids.extend(returned_1_1)
        echoed_0 = request.lineage_node_id
        response.lineage_node.lineage_node_id = echoed_0
        return response


async def handle_list_lineage_nodes(
    deps: Dependencies,
    request: lineage_v1_lineage_node_service_pb2.ListLineageNodesRequest
) -> lineage_v1_lineage_node_service_pb2.ListLineageNodesResponse:
    """Lists lineage nodes a page at a time."""
    response = lineage_v1_lineage_node_service_pb2.ListLineageNodesResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('ListLineageNodes', extra={'fields': {'order_by': request.order_by}})
        await deps.repository.audit(request.context.tenant_id, 'ListLineageNodes', {'order_by': request.order_by})
        response_0 = lineage_v1_lineage_edge_validation_service_pb2.ValidateLineageEdgeResponse()
        response_1 = metrics_v1_metric_series_query_service_pb2.BrowseMetricSeriesesResponse()
        outgoing_0 = lineage_v1_lineage_edge_validation_service_pb2.ValidateLineageEdgeRequest(
            context=request.context,
            details=lineage_v1_lineage_edge_validation_service_pb2.ValidateLineageEdgeRequest.Details(
                locale=request.context.locale
            )
        )
        response_0 = await deps.clients.lineage_lineage_edge_validation.ValidateLineageEdge(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = metrics_v1_metric_series_query_service_pb2.BrowseMetricSeriesesRequest(
            context=request.context,
            filter=metrics_v1_metric_series_query_service_pb2.BrowseMetricSeriesesRequest.Filter(
                owner_id=request.filter.owner_id,
                region=request.filter.region
            ),
            page=common_v1_paging_pb2.PageRequest(page_size=request.page.page_size, page_token=request.page.page_token)
        )
        registered_1 = cast(
            metrics_v1_metric_series_query_service_pb2_grpc.MetricSeriesQueryServiceStub,
            deps.clients.registry['acme.metrics.v1.MetricSeriesQueryService']
        )
        response_1 = await registered_1.BrowseMetricSerieses(outgoing_1, timeout=deps.settings.timeout)
        returned_0_0 = response_0.lineage_edge.attributes
        returned_0_0_part_0 = response.lineage_nodes.add()
        returned_0_0_part_0.attributes.update(returned_0_0)
        returned_0_1 = response_0.result.status
        if returned_0_1:
            response.result.status = returned_0_1
        returned_1_0 = response_1.result.status
        if returned_1_0:
            response.result.status = returned_1_0
        return response


async def handle_search_lineage_nodes(
    deps: Dependencies,
    request: lineage_v1_lineage_node_service_pb2.SearchLineageNodesRequest
) -> lineage_v1_lineage_node_service_pb2.SearchLineageNodesResponse:
    """Lists lineage nodes a page at a time."""
    response = lineage_v1_lineage_node_service_pb2.SearchLineageNodesResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('SearchLineageNodes', extra={'fields': {'order_by': request.order_by}})
        await deps.repository.audit(request.context.tenant_id, 'SearchLineageNodes', {'order_by': request.order_by})
        response_0 = lineage_v1_lineage_edge_query_service_pb2.BrowseLineageEdgesResponse()
        outgoing_0 = lineage_v1_lineage_edge_query_service_pb2.BrowseLineageEdgesRequest(
            context=request.context,
            filter=lineage_v1_lineage_edge_query_service_pb2.BrowseLineageEdgesRequest.Filter(
                created_after=request.filter.created_after,
                owner_id=request.filter.owner_id
            ),
            page=common_v1_paging_pb2.PageRequest(page_size=request.page.page_size, page_token=request.page.page_token)
        )
        response_0 = await deps.clients.lineage_lineage_edge_query.BrowseLineageEdges(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.result.message
        if returned_0_0:
            response.result.message = returned_0_0
        returned_0_1 = response_0.page_info.total_size
        if returned_0_1:
            response.page_info.total_size = returned_0_1
        return response


async def handle_update_lineage_node(
    deps: Dependencies,
    request: lineage_v1_lineage_node_service_pb2.UpdateLineageNodeRequest
) -> lineage_v1_lineage_node_service_pb2.UpdateLineageNodeResponse:
    """Changes a lineage node."""
    response = lineage_v1_lineage_node_service_pb2.UpdateLineageNodeResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('UpdateLineageNode', extra={'fields': {'allow_missing': request.allow_missing}})
        await deps.repository.audit(
            request.context.tenant_id,
            'UpdateLineageNode',
            {'allow_missing': request.allow_missing}
        )
        await deps.repository.save_lineage_node(request.context.tenant_id, request.lineage_node)
        response_0 = concessions_v1_concession_stand_calculation_service_pb2.CalculateConcessionStandResponse()
        response_1 = lineage_v1_lineage_node_validation_service_pb2.PreviewLineageNodeResponse()
        outgoing_0 = concessions_v1_concession_stand_calculation_service_pb2.CalculateConcessionStandRequest(
            concession_stand=concessions_v1_concessions_pb2.ConcessionStand(
                address=common_v1_address_pb2.PostalAddress(region=request.lineage_node.location.region),
                audit=common_v1_audit_pb2.AuditInfo(created_at=request.lineage_node.audit.created_at),
                owner=identity_v1_refs_pb2.UserRef(user_id=request.lineage_node.manager.user_id)
            ),
            context=request.context,
            details=concessions_v1_concession_stand_calculation_service_pb2.CalculateConcessionStandRequest.Details(
                destination=common_v1_address_pb2.PostalAddress(country_code=request.lineage_node.location.country_code)
            )
        )
        response_0 = await deps.clients.concessions_concession_stand_calculation.CalculateConcessionStand(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = lineage_v1_lineage_node_validation_service_pb2.PreviewLineageNodeRequest(
            context=request.context,
            lineage_node=lineage_v1_lineage_pb2.LineageNode(
                children=[
                    lineage_v1_lineage_pb2.LineageNode(
                        children=[
                            lineage_v1_lineage_pb2.LineageNode(
                                audit=common_v1_audit_pb2.AuditInfo(etag=request.lineage_node.audit.etag),
                                children=[lineage_v1_lineage_pb2.LineageNode(status=request.lineage_node.status)],
                                location=common_v1_address_pb2.PostalAddress(
                                    region=request.lineage_node.location.region
                                )
                            )
                        ]
                    )
                ]
            )
        )
        send_1 = partial(deps.clients.lineage_lineage_node_validation.PreviewLineageNode, timeout=deps.settings.timeout)
        response_1 = await send_1(outgoing_1)
        returned_0_0 = response_0.concession_stand.owner.email
        returned_0_0_part_1 = response.lineage_node.children.add()
        if returned_0_0:
            returned_0_0_part_1.manager.email = returned_0_0
        returned_0_1 = response_0.result.status
        if returned_0_1:
            response.result.status = returned_0_1
        returned_1_0 = response_1.lineage_node.location.region
        returned_1_0_part_1 = response.lineage_node.children.add()
        if returned_1_0:
            returned_1_0_part_1.location.region = returned_1_0
        returned_1_1 = response_1.lineage_node.depth
        returned_1_1_part_1 = response.lineage_node.children.add()
        returned_1_1_part_2 = returned_1_1_part_1.children.add()
        if returned_1_1:
            returned_1_1_part_2.depth = returned_1_1
        echoed_0 = request.lineage_node.name
        response.lineage_node.name = echoed_0
        echoed_1 = request.lineage_node.manager
        response.lineage_node.manager.CopyFrom(echoed_1)
        return response


async def handle_watch_lineage_nodes(
    deps: Dependencies,
    request: lineage_v1_lineage_node_service_pb2.WatchLineageNodesRequest
) -> lineage_v1_lineage_node_service_pb2.WatchLineageNodesResponse:
    """Streams the changes of lineage nodes as they happen."""
    response = lineage_v1_lineage_node_service_pb2.WatchLineageNodesResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('WatchLineageNodes', extra={'fields': {'max_events': request.max_events}})
        await deps.repository.audit(request.context.tenant_id, 'WatchLineageNodes', {'max_events': request.max_events})
        response_0 = lineage_v1_lineage_edge_query_service_pb2.FindLineageEdgesResponse()
        response_1 = careplans_v1_care_plan_calculation_service_pb2.QuoteCarePlanResponse()
        outgoing_0 = lineage_v1_lineage_edge_query_service_pb2.FindLineageEdgesRequest(
            context=request.context,
            filter=lineage_v1_lineage_edge_query_service_pb2.FindLineageEdgesRequest.Filter(
                owner_id=request.filter.owner_id,
                query=request.filter.query
            )
        )
        response_0 = await deps.clients.lineage_lineage_edge_query.FindLineageEdges(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = careplans_v1_care_plan_calculation_service_pb2.QuoteCarePlanRequest()
        outgoing_1.context.CopyFrom(request.context)
        outgoing_1.details.destination.region = request.filter.region
        outgoing_1.care_plan.audit.updated_at.CopyFrom(request.since)
        field_1_3_part_1 = outgoing_1.care_plan.lines.add()
        field_1_3_part_1.attributes.update(dict(response_0.result.details))
        outgoing_1.context.tenant_id = tenant_id.get()
        response_1 = await deps.clients.careplans_care_plan_calculation.QuoteCarePlan(
            outgoing_1,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.result.details
        response.result.details.update(returned_0_0)
        returned_1_0 = response_1.care_plan.billing_address.lines
        response.lineage_node.location.lines.extend(returned_1_0)
        returned_1_1 = response_1.care_plan.audit.updated_by
        returned_1_1_part_1 = response.lineage_node.children.add()
        returned_1_1_part_2 = returned_1_1_part_1.children.add()
        if returned_1_1:
            returned_1_1_part_2.audit.updated_by = returned_1_1
        echoed_0 = request.filter.region
        response.lineage_node.location.region = echoed_0
        echoed_1 = request.subscriber.email
        response.lineage_node.manager.email = echoed_1
        return response
