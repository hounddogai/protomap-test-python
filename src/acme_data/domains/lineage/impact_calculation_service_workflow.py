"""Application workflow for Impact Calculation."""

from __future__ import annotations

from functools import partial
from typing import Any
from typing import cast
import logging

from google.protobuf.any_pb2 import Any as AnyMessage
from google.protobuf.json_format import MessageToDict
from google.protobuf.json_format import ParseDict

from acme.authorization.v1 import access_policy_query_service_pb2 as authorization_v1_access_policy_query_service_pb2
from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.configuration.v1 import (
    config_set_calculation_service_pb2 as configuration_v1_config_set_calculation_service_pb2,
)
from acme.fleet.v1 import fleet_pb2 as fleet_v1_fleet_pb2
from acme.fleet.v1 import vehicle_service_pb2 as fleet_v1_vehicle_service_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.lineage.v1 import impact_calculation_service_pb2 as lineage_v1_impact_calculation_service_pb2
from acme.lineage.v1 import lineage_edge_calculation_service_pb2 as lineage_v1_lineage_edge_calculation_service_pb2
from acme.lineage.v1 import lineage_node_calculation_service_pb2 as lineage_v1_lineage_node_calculation_service_pb2
from acme.lineage.v1 import (
    lineage_node_calculation_service_pb2_grpc as lineage_v1_lineage_node_calculation_service_pb2_grpc,
)
from acme.lineage.v1 import lineage_node_validation_service_pb2 as lineage_v1_lineage_node_validation_service_pb2
from acme.lineage.v1 import lineage_pb2 as lineage_v1_lineage_pb2
from acme.lineage.v1 import refs_pb2 as lineage_v1_refs_pb2
from acme.search.v1 import search_index_query_service_pb2 as search_v1_search_index_query_service_pb2

from acme_data.domains.lineage import hooks
from acme_data.domains.lineage.adapters import ImpactCalculationCalculateImpact1Adapter
from acme_data.domains.lineage.adapters import ImpactCalculationCalculateImpact1Port
from acme_data.domains.lineage.adapters import ImpactCalculationCompareImpactOptions1Adapter
from acme_data.domains.lineage.dependencies import Dependencies
from acme_data.domains.lineage.models import ImpactCalculationRecalculateImpacts0Command
from acme_data.domains.lineage.models import ImpactCalculationRecalculateImpacts1Command
from acme_data.domains.lineage.models import to_impact_calculation_recalculate_impacts0_command
from acme_data.domains.lineage.models import to_impact_calculation_recalculate_impacts1_command
from acme_data.platform.rpc import run_steps
from acme_data.platform.tenancy import tenant_id
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class ImpactCalculationServicerWorkflow:
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    async def handle_calculate_impact(
        self,
        request: lineage_v1_impact_calculation_service_pb2.CalculateImpactRequest
    ) -> lineage_v1_impact_calculation_service_pb2.CalculateImpactResponse:
        """Calculates an impact."""
        deps = self.deps
        response = lineage_v1_impact_calculation_service_pb2.CalculateImpactResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CalculateImpact', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'CalculateImpact', {'reason': request.reason})
            await deps.repository.save_impact(request.context.tenant_id, request.impact)
            response_0 = configuration_v1_config_set_calculation_service_pb2.EstimateConfigSetResponse()
            response_1 = lineage_v1_lineage_node_calculation_service_pb2.SimulateLineageNodeResponse()
            outgoing_0 = configuration_v1_config_set_calculation_service_pb2.EstimateConfigSetRequest()
            outgoing_0.context.CopyFrom(request.context)
            field_0_1_part_1 = outgoing_0.config_set.children.add()
            field_0_1_part_2 = field_0_1_part_1.children.add()
            field_0_1_part_2.audit.updated_at.CopyFrom(request.impact.audit.updated_at)
            field_0_2_part_1 = outgoing_0.config_set.children.add()
            field_0_2_part_1.manager.email = request.impact.requester.email
            field_0_3_part_1 = outgoing_0.config_set.children.add()
            field_0_3_part_2 = field_0_3_part_1.children.add()
            field_0_3_part_2.audit.created_at.CopyFrom(request.impact.audit.created_at)
            field_0_4_part_1 = outgoing_0.config_set.children.add()
            field_0_4_part_2 = field_0_4_part_1.children.add()
            field_0_4_part_2.location.lines.extend(list(request.details.destination.lines))
            outgoing_0.context.tenant_id = tenant_id.get()
            response_0 = await deps.clients.configuration_config_set_calculation.EstimateConfigSet(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = lineage_v1_lineage_node_calculation_service_pb2.SimulateLineageNodeRequest(
                context=request.context,
                lineage_node=lineage_v1_lineage_pb2.LineageNode(
                    children=[
                        lineage_v1_lineage_pb2.LineageNode(
                            children=[
                                lineage_v1_lineage_pb2.LineageNode(
                                    audit=common_v1_audit_pb2.AuditInfo(
                                        created_at=response_0.config_set.audit.created_at
                                    ),
                                    location=common_v1_address_pb2.PostalAddress(
                                        country_code=request.details.destination.country_code
                                    ),
                                    manager=identity_v1_refs_pb2.UserRef(
                                        display_name=request.impact.customer.display_name
                                    )
                                )
                            ]
                        )
                    ]
                )
            )
            port_1: ImpactCalculationCalculateImpact1Port = ImpactCalculationCalculateImpact1Adapter(
                deps.clients.lineage_lineage_node_calculation,
                deps.settings.timeout
            )
            response_1 = await port_1.execute(outgoing_1)
            returned_0_0 = response_0.config_set.audit.updated_at
            if returned_0_0.ListFields():
                response.impact.audit.updated_at.MergeFrom(returned_0_0)
            returned_0_1 = response_0.config_set.manager.email
            if returned_0_1:
                response.impact.requester.email = returned_0_1
            returned_1_0 = response_1.result.correlation_id
            if returned_1_0:
                response.result.correlation_id = returned_1_0
            returned_1_1 = response_1.result.reference_ids
            response.result.reference_ids.extend(returned_1_1)
            echoed_0 = request.impact_id
            response.impact.impact_id = echoed_0
            echoed_1 = request.details.currency_code
            response.breakdown.currency_code = echoed_1
            return response

    async def handle_compare_impact_options(
        self,
        request: lineage_v1_impact_calculation_service_pb2.CompareImpactOptionsRequest
    ) -> lineage_v1_impact_calculation_service_pb2.CompareImpactOptionsResponse:
        """Compares an impact."""
        deps = self.deps
        response = lineage_v1_impact_calculation_service_pb2.CompareImpactOptionsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CompareImpactOptions', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'CompareImpactOptions', {'reason': request.reason})
            await deps.repository.save_impact(request.context.tenant_id, request.impact)
            response_0 = lineage_v1_lineage_node_calculation_service_pb2.EstimateLineageNodeResponse()
            response_1 = lineage_v1_lineage_node_calculation_service_pb2.SimulateLineageNodeResponse()
            response_2 = search_v1_search_index_query_service_pb2.BrowseSearchIndexesResponse()
            outgoing_0 = lineage_v1_lineage_node_calculation_service_pb2.EstimateLineageNodeRequest(
                context=request.context,
                lineage_node=lineage_v1_lineage_pb2.LineageNode(
                    children=[
                        lineage_v1_lineage_pb2.LineageNode(
                            children=[
                                lineage_v1_lineage_pb2.LineageNode(
                                    location=common_v1_address_pb2.PostalAddress(
                                        lines=list(request.details.destination.lines)
                                    ),
                                    manager=identity_v1_refs_pb2.UserRef(
                                        display_name=request.impact.customer.display_name
                                    )
                                )
                            ]
                        )
                    ]
                )
            )
            steps_0 = [
                partial(
                    deps.clients.lineage_lineage_node_calculation.EstimateLineageNode,
                    outgoing_0,
                    timeout=deps.settings.timeout
                )
            ]
            results_0 = await run_steps(steps_0)
            response_0 = results_0[-1]
            outgoing_1 = lineage_v1_lineage_node_calculation_service_pb2.SimulateLineageNodeRequest(
                context=request.context,
                lineage_node=lineage_v1_lineage_pb2.LineageNode(
                    children=[
                        lineage_v1_lineage_pb2.LineageNode(
                            children=[
                                lineage_v1_lineage_pb2.LineageNode(
                                    location=common_v1_address_pb2.PostalAddress(
                                        country_code=response_0.lineage_node.location.country_code
                                    ),
                                    manager=identity_v1_refs_pb2.UserRef(email=response_0.lineage_node.manager.email)
                                )
                            ]
                        )
                    ]
                )
            )
            response_1 = await ImpactCalculationCompareImpactOptions1Adapter(
                deps.clients.lineage_lineage_node_calculation,
                deps.settings.timeout
            )(outgoing_1)
            outgoing_2 = search_v1_search_index_query_service_pb2.BrowseSearchIndexesRequest(
                context=request.context,
                filter=search_v1_search_index_query_service_pb2.BrowseSearchIndexesRequest.Filter(
                    created_after=response_0.lineage_node.audit.updated_at,
                    labels=dict(response_0.result.details),
                    owner_id=request.impact.sla.policy_id,
                    region=response_1.lineage_node.location.region
                )
            )
            response_2 = cast(search_v1_search_index_query_service_pb2.BrowseSearchIndexesResponse, await deps.bus.request(
                'acme.lineage.v1.ImpactCalculationService/CompareImpactOptions/2', outgoing_2, deps.settings.timeout,
            ))
            returned_0_0 = response_0.lineage_node.audit.created_at
            if returned_0_0.ListFields():
                response.impact.audit.created_at.MergeFrom(returned_0_0)
            returned_1_0 = response_1.lineage_node.audit.created_at
            if returned_1_0.ListFields():
                response.impact.audit.created_at.MergeFrom(returned_1_0)
            returned_2_0 = response_2.result.correlation_id
            if returned_2_0:
                response.result.correlation_id = returned_2_0
            echoed_0 = request.impact_id
            response.impact.impact_id = echoed_0
            echoed_1 = request.impact.status
            response.impact.status = echoed_1
            return response

    async def handle_estimate_impact(
        self,
        request: lineage_v1_impact_calculation_service_pb2.EstimateImpactRequest
    ) -> lineage_v1_impact_calculation_service_pb2.EstimateImpactResponse:
        """Estimates an impact."""
        deps = self.deps
        response = lineage_v1_impact_calculation_service_pb2.EstimateImpactResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('EstimateImpact', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'EstimateImpact', {'reason': request.reason})
            await deps.repository.save_impact(request.context.tenant_id, request.impact)
            response_0 = lineage_v1_lineage_node_calculation_service_pb2.RecalculateLineageNodesResponse()
            response_1 = lineage_v1_lineage_edge_calculation_service_pb2.CompareLineageEdgeOptionsResponse()
            response_2 = lineage_v1_lineage_node_calculation_service_pb2.SimulateLineageNodeResponse()
            response_3 = search_v1_search_index_query_service_pb2.BrowseSearchIndexesResponse()
            outgoing_0 = lineage_v1_lineage_node_calculation_service_pb2.RecalculateLineageNodesRequest(
                context=request.context,
                lineage_node=lineage_v1_lineage_pb2.LineageNode(
                    children=[
                        lineage_v1_lineage_pb2.LineageNode(
                            children=[
                                lineage_v1_lineage_pb2.LineageNode(
                                    location=common_v1_address_pb2.PostalAddress(
                                        recipient=request.details.destination.recipient
                                    ),
                                    manager=identity_v1_refs_pb2.UserRef(email=request.impact.requester.email)
                                )
                            ]
                        )
                    ]
                )
            )
            response_0 = await deps.clients.lineage_lineage_node_calculation.RecalculateLineageNodes(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = lineage_v1_lineage_edge_calculation_service_pb2.CompareLineageEdgeOptionsRequest(
                context=request.context,
                details=lineage_v1_lineage_edge_calculation_service_pb2.CompareLineageEdgeOptionsRequest.Details(
                    destination=common_v1_address_pb2.PostalAddress(
                        lines=list(response_0.lineage_node.location.lines),
                        locality=response_0.lineage_node.location.locality
                    )
                ),
                lineage_edge=lineage_v1_lineage_pb2.LineageEdge(
                    subject=lineage_v1_refs_pb2.ImpactRef(display_name=response_0.lineage_node.manager.display_name)
                )
            )
            method_name_1 = 'CompareLineageEdgeOptions'
            response_1 = await getattr(
                deps.clients.lineage_lineage_edge_calculation,
                method_name_1
            )(outgoing_1, timeout=deps.settings.timeout)
            fields_2: dict[str, Any] = {
                'context': request.context,
                'lineage_node': {
                    'children': [
                        {
                            'children': [
                                {
                                    'audit': {'etag': request.impact.audit.etag},
                                    'location': {'region': response_0.lineage_node.location.region}
                                }
                            ]
                        }
                    ]
                }
            }
            outgoing_2 = lineage_v1_lineage_node_calculation_service_pb2.SimulateLineageNodeRequest(**fields_2)
            response_2 = await deps.clients.lineage_lineage_node_calculation.SimulateLineageNode(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            outgoing_3 = search_v1_search_index_query_service_pb2.BrowseSearchIndexesRequest(
                context=request.context,
                filter=search_v1_search_index_query_service_pb2.BrowseSearchIndexesRequest.Filter(
                    created_after=response_2.lineage_node.audit.created_at,
                    owner_id=response_2.lineage_node.manager.user_id,
                    region=response_2.lineage_node.location.region
                )
            )
            document_3 = MessageToDict(outgoing_3, preserving_proto_field_name=True)
            outgoing_3 = ParseDict(document_3, search_v1_search_index_query_service_pb2.BrowseSearchIndexesRequest())
            response_3 = await deps.clients.search_search_index_query.BrowseSearchIndexes(
                outgoing_3,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.correlation_id
            if returned_0_0:
                response.result.correlation_id = returned_0_0
            returned_1_0 = response_1.lineage_edge.correlation_id
            if returned_1_0:
                response.result.correlation_id = returned_1_0
            returned_1_1 = response_1.lineage_edge.subject.priority
            if returned_1_1:
                response.impact.priority = returned_1_1
            returned_2_0 = response_2.lineage_node.audit.created_by
            if returned_2_0:
                response.impact.audit.created_by = returned_2_0
            returned_2_1 = response_2.breakdown.total
            if returned_2_1.ListFields():
                response.breakdown.total.MergeFrom(returned_2_1)
            returned_3_0 = response_3.result.correlation_id
            if returned_3_0:
                response.result.correlation_id = returned_3_0
            echoed_0 = request.impact_id
            response.impact.impact_id = echoed_0
            echoed_1 = request.impact.custom_fields
            response.impact.custom_fields.update(echoed_1)
            return response

    async def handle_explain_impact_calculation(
        self,
        request: lineage_v1_impact_calculation_service_pb2.ExplainImpactCalculationRequest
    ) -> lineage_v1_impact_calculation_service_pb2.ExplainImpactCalculationResponse:
        """Explains an impact."""
        deps = self.deps
        response = lineage_v1_impact_calculation_service_pb2.ExplainImpactCalculationResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ExplainImpactCalculation', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ExplainImpactCalculation',
                {'reason': request.reason}
            )
            await deps.repository.save_impact(request.context.tenant_id, request.impact)
            response_0 = lineage_v1_lineage_node_calculation_service_pb2.RecalculateLineageNodesResponse()
            response_1 = lineage_v1_lineage_node_validation_service_pb2.NormalizeLineageNodeResponse()
            response_2 = fleet_v1_vehicle_service_pb2.CreateVehicleResponse()
            outgoing_0 = lineage_v1_lineage_node_calculation_service_pb2.RecalculateLineageNodesRequest()
            outgoing_0.context.CopyFrom(request.context)
            field_0_1_part_1 = outgoing_0.lineage_node.children.add()
            field_0_1_part_2 = field_0_1_part_1.children.add()
            field_0_1_part_2.audit.created_by = request.impact.audit.created_by
            field_0_2_part_1 = outgoing_0.lineage_node.children.add()
            field_0_2_part_2 = field_0_2_part_1.children.add()
            field_0_2_part_2.manager.email = request.impact.requester.email
            field_0_3_part_1 = outgoing_0.lineage_node.children.add()
            field_0_3_part_2 = field_0_3_part_1.children.add()
            field_0_3_part_2.manager.user_id = request.impact.assignee.user_id
            if request.impact.WhichOneof('origin') == 'customer':
                field_0_4_part_1 = outgoing_0.lineage_node.children.add()
                field_0_4_part_2 = field_0_4_part_1.children.add()
                field_0_4_part_2.manager.display_name = request.impact.customer.display_name
            response_0 = await deps.clients.lineage_lineage_node_calculation.RecalculateLineageNodes(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = lineage_v1_lineage_node_validation_service_pb2.NormalizeLineageNodeRequest()
            outgoing_1.context.CopyFrom(request.context)
            field_1_1_part_1 = outgoing_1.lineage_node.children.add()
            field_1_1_part_2 = field_1_1_part_1.children.add()
            field_1_1_part_2.audit.updated_by = request.impact.audit.updated_by
            field_1_2_part_1 = outgoing_1.lineage_node.children.add()
            field_1_2_part_2 = field_1_2_part_1.children.add()
            field_1_2_part_2.audit.updated_at.CopyFrom(response_0.lineage_node.audit.updated_at)
            field_1_3_part_1 = outgoing_1.lineage_node.children.add()
            field_1_3_part_2 = field_1_3_part_1.children.add()
            field_1_3_part_2.location.locality = response_0.lineage_node.location.locality
            field_1_4_part_1 = outgoing_1.lineage_node.children.add()
            field_1_4_part_2 = field_1_4_part_1.children.add()
            field_1_4_part_2.manager.email = request.impact.requester.email
            merged_1 = lineage_v1_lineage_node_validation_service_pb2.NormalizeLineageNodeRequest()
            merged_1.MergeFrom(outgoing_1)
            outgoing_1.CopyFrom(merged_1)
            response_1 = await deps.clients.lineage_lineage_node_validation.NormalizeLineageNode(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = fleet_v1_vehicle_service_pb2.CreateVehicleRequest(
                context=request.context,
                vehicle=fleet_v1_fleet_pb2.Vehicle(
                    address=common_v1_address_pb2.PostalAddress(
                        country_code=response_0.lineage_node.location.country_code,
                        recipient=response_0.lineage_node.location.recipient
                    ),
                    audit=common_v1_audit_pb2.AuditInfo(etag=response_0.lineage_node.audit.etag),
                    owner=identity_v1_refs_pb2.UserRef(email=request.impact.assignee.email)
                )
            )
            envelope_2 = AnyMessage()
            envelope_2.Pack(outgoing_2)
            outgoing_2 = fleet_v1_vehicle_service_pb2.CreateVehicleRequest()
            if not envelope_2.Unpack(outgoing_2):
                raise ValueError("partner envelope contains the wrong request type")
            response_2 = await deps.clients.fleet_vehicle.CreateVehicle(outgoing_2, timeout=deps.settings.timeout)
            returned_0_0 = response_0.lineage_node.audit.updated_at
            if returned_0_0.ListFields():
                response.impact.audit.updated_at.MergeFrom(returned_0_0)
            returned_0_1 = response_0.result.status
            if returned_0_1:
                response.result.status = returned_0_1
            returned_1_0 = response_1.lineage_node.manager.user_id
            if returned_1_0:
                response.impact.assignee.user_id = returned_1_0
            returned_2_0 = response_2.vehicle.audit.updated_by
            if returned_2_0:
                response.impact.audit.updated_by = returned_2_0
            echoed_0 = request.impact_id
            response.impact.impact_id = echoed_0
            echoed_1 = request.impact.subject
            response.impact.subject = echoed_1
            return response

    async def handle_get_impact_rates(
        self,
        request: lineage_v1_impact_calculation_service_pb2.GetImpactRatesRequest
    ) -> lineage_v1_impact_calculation_service_pb2.GetImpactRatesResponse:
        """Returns an impact."""
        deps = self.deps
        response = lineage_v1_impact_calculation_service_pb2.GetImpactRatesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('GetImpactRates', extra={'fields': {'locale': request.context.locale}})
            await deps.repository.audit(request.context.tenant_id, 'GetImpactRates', {'locale': request.context.locale})
            echoed_0 = request.impact_id
            response.impact.impact_id = echoed_0
            return response

    async def handle_quote_impact(
        self,
        request: lineage_v1_impact_calculation_service_pb2.QuoteImpactRequest
    ) -> lineage_v1_impact_calculation_service_pb2.QuoteImpactResponse:
        """Quotes an impact."""
        deps = self.deps
        response = lineage_v1_impact_calculation_service_pb2.QuoteImpactResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('QuoteImpact', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'QuoteImpact', {'reason': request.reason})
            await deps.repository.save_impact(request.context.tenant_id, request.impact)
            response_0 = lineage_v1_lineage_node_calculation_service_pb2.RecalculateLineageNodesResponse()
            outgoing_0 = lineage_v1_lineage_node_calculation_service_pb2.RecalculateLineageNodesRequest(
                context=request.context,
                lineage_node=lineage_v1_lineage_pb2.LineageNode(
                    children=[
                        lineage_v1_lineage_pb2.LineageNode(
                            children=[
                                lineage_v1_lineage_pb2.LineageNode(
                                    audit=common_v1_audit_pb2.AuditInfo(etag=request.impact.audit.etag),
                                    location=common_v1_address_pb2.PostalAddress(
                                        locality=request.details.destination.locality
                                    )
                                )
                            ]
                        )
                    ]
                )
            )
            registered_0 = cast(
                lineage_v1_lineage_node_calculation_service_pb2_grpc.LineageNodeCalculationServiceStub,
                deps.clients.registry['acme.lineage.v1.LineageNodeCalculationService']
            )
            response_0 = await registered_0.RecalculateLineageNodes(outgoing_0, timeout=deps.settings.timeout)
            returned_0_0 = response_0.lineage_node.audit.created_at
            if returned_0_0.ListFields():
                response.impact.audit.created_at.MergeFrom(returned_0_0)
            returned_0_1 = response_0.lineage_node.manager.email
            if returned_0_1:
                response.impact.assignee.email = returned_0_1
            echoed_0 = request.impact_id
            response.impact.impact_id = echoed_0
            echoed_1 = request.impact.status
            response.impact.status = echoed_1
            return response

    async def handle_recalculate_impacts(
        self,
        request: lineage_v1_impact_calculation_service_pb2.RecalculateImpactsRequest
    ) -> lineage_v1_impact_calculation_service_pb2.RecalculateImpactsResponse:
        """Recalculates an impact."""
        deps = self.deps
        response = lineage_v1_impact_calculation_service_pb2.RecalculateImpactsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('RecalculateImpacts', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'RecalculateImpacts', {'reason': request.reason})
            await deps.repository.save_impact(request.context.tenant_id, request.impact)
            response_0 = authorization_v1_access_policy_query_service_pb2.BrowseAccessPoliciesResponse()
            response_1 = lineage_v1_lineage_edge_calculation_service_pb2.EstimateLineageEdgeResponse()
            response_2 = lineage_v1_lineage_node_calculation_service_pb2.CalculateLineageNodeResponse()
            response_3 = lineage_v1_lineage_node_calculation_service_pb2.QuoteLineageNodeResponse()
            command_0 = ImpactCalculationRecalculateImpacts0Command(
                context=request.context,
                filter_region=request.details.destination.region,
                filter_created_after=request.impact.audit.updated_at,
                filter_owner_id=request.impact.customer.customer_id
            )
            outgoing_0 = to_impact_calculation_recalculate_impacts0_command(command_0)
            response_0 = await deps.clients.authorization_access_policy_query.BrowseAccessPolicies(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            command_1 = ImpactCalculationRecalculateImpacts1Command.model_validate(
                {
                    'context': request.context,
                    'details_destination_recipient': request.details.destination.recipient,
                    'details_destination_region': request.details.destination.region,
                    'details_destination_country_code': request.details.destination.country_code
                }
            )
            outgoing_1 = to_impact_calculation_recalculate_impacts1_command(command_1)
            response_1 = await deps.clients.lineage_lineage_edge_calculation.EstimateLineageEdge(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = lineage_v1_lineage_node_calculation_service_pb2.CalculateLineageNodeRequest(
                context=request.context,
                lineage_node=lineage_v1_lineage_pb2.LineageNode(
                    children=[
                        lineage_v1_lineage_pb2.LineageNode(
                            children=[
                                lineage_v1_lineage_pb2.LineageNode(
                                    audit=common_v1_audit_pb2.AuditInfo(etag=request.impact.audit.etag),
                                    location=common_v1_address_pb2.PostalAddress(
                                        region=request.details.destination.region
                                    ),
                                    manager=identity_v1_refs_pb2.UserRef(email=request.impact.assignee.email)
                                )
                            ]
                        )
                    ]
                )
            )
            send_2 = partial(
                deps.clients.lineage_lineage_node_calculation.CalculateLineageNode,
                timeout=deps.settings.timeout
            )
            response_2 = await send_2(outgoing_2)
            outgoing_3 = lineage_v1_lineage_node_calculation_service_pb2.QuoteLineageNodeRequest(
                context=request.context,
                lineage_node=lineage_v1_lineage_pb2.LineageNode(
                    children=[
                        lineage_v1_lineage_pb2.LineageNode(
                            children=[
                                lineage_v1_lineage_pb2.LineageNode(
                                    location=common_v1_address_pb2.PostalAddress(
                                        region=request.details.destination.region
                                    ),
                                    manager=identity_v1_refs_pb2.UserRef(
                                        display_name=request.impact.customer.display_name
                                    )
                                )
                            ]
                        )
                    ]
                )
            )
            response_3 = await hooks.impact_calculation_recalculate_impacts3(
                deps.clients.lineage_lineage_node_calculation,
                outgoing_3,
                deps.settings.timeout
            )
            returned_0_0 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_0)
            returned_1_0 = response_1.lineage_edge.correlation_id
            if returned_1_0:
                response.result.correlation_id = returned_1_0
            returned_2_0 = response_2.result.status
            if returned_2_0:
                response.result.status = returned_2_0
            returned_2_1 = response_2.breakdown.currency_code
            if returned_2_1:
                response.breakdown.currency_code = returned_2_1
            returned_3_0 = response_3.lineage_node.audit.created_by
            if returned_3_0:
                response.impact.audit.created_by = returned_3_0
            returned_3_1 = response_3.result.details
            response.result.details.update(returned_3_1)
            echoed_0 = request.impact_id
            response.impact.impact_id = echoed_0
            echoed_1 = request.impact.status
            response.impact.status = echoed_1
            return response

    async def handle_simulate_impact(
        self,
        request: lineage_v1_impact_calculation_service_pb2.SimulateImpactRequest
    ) -> lineage_v1_impact_calculation_service_pb2.SimulateImpactResponse:
        """Simulates an impact."""
        deps = self.deps
        response = lineage_v1_impact_calculation_service_pb2.SimulateImpactResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SimulateImpact', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'SimulateImpact', {'reason': request.reason})
            await deps.repository.save_impact(request.context.tenant_id, request.impact)
            response_0 = lineage_v1_lineage_node_calculation_service_pb2.EstimateLineageNodeResponse()
            outgoing_0 = lineage_v1_lineage_node_calculation_service_pb2.EstimateLineageNodeRequest()
            outgoing_0.context.CopyFrom(request.context)
            field_0_1_part_1 = outgoing_0.lineage_node.children.add()
            field_0_1_part_2 = field_0_1_part_1.children.add()
            field_0_1_part_2.location.lines.extend(list(request.details.destination.lines))
            field_0_2_part_1 = outgoing_0.lineage_node.children.add()
            field_0_2_part_2 = field_0_2_part_1.children.add()
            field_0_2_part_2.manager.email = request.impact.requester.email
            outgoing_0.context.tenant_id = tenant_id.get()
            response_0 = await deps.clients.lineage_lineage_node_calculation.EstimateLineageNode(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.lineage_node.manager.email
            if returned_0_0:
                response.impact.requester.email = returned_0_0
            echoed_0 = request.impact_id
            response.impact.impact_id = echoed_0
            echoed_1 = request.details.currency_code
            response.breakdown.currency_code = echoed_1
            return response
