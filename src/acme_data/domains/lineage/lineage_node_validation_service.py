"""Checks lineage nodes against the rules before anything acts on them."""

from __future__ import annotations

from collections.abc import AsyncIterator
from dataclasses import dataclass
from functools import partial
from typing import Any
from typing import cast
import logging

from google.protobuf.json_format import MessageToDict
from google.protobuf.json_format import MessageToJson
from google.protobuf.json_format import Parse
from google.protobuf.json_format import ParseDict
import grpc

from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.featureflags.v1 import feature_flag_query_service_pb2 as featureflags_v1_feature_flag_query_service_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.lineage.v1 import lineage_edge_calculation_service_pb2 as lineage_v1_lineage_edge_calculation_service_pb2
from acme.lineage.v1 import (
    lineage_edge_calculation_service_pb2_grpc as lineage_v1_lineage_edge_calculation_service_pb2_grpc,
)
from acme.lineage.v1 import lineage_node_calculation_service_pb2 as lineage_v1_lineage_node_calculation_service_pb2
from acme.lineage.v1 import lineage_node_validation_service_pb2 as lineage_v1_lineage_node_validation_service_pb2
from acme.lineage.v1 import (
    lineage_node_validation_service_pb2_grpc as lineage_v1_lineage_node_validation_service_pb2_grpc,
)
from acme.lineage.v1 import lineage_pb2 as lineage_v1_lineage_pb2
from acme.lineage.v1 import refs_pb2 as lineage_v1_refs_pb2
from acme.search.v1 import search_index_service_pb2 as search_v1_search_index_service_pb2
from acme.search.v1 import search_pb2 as search_v1_search_pb2

from acme_data.domains.lineage.adapters import LineageNodeValidationCheckLineageNodeEligibility0Adapter
from acme_data.domains.lineage.adapters import LineageNodeValidationCheckLineageNodeEligibility0Port
from acme_data.domains.lineage.adapters import LineageNodeValidationCheckLineageNodeEligibility2Adapter
from acme_data.domains.lineage.dependencies import Dependencies
from acme_data.domains.lineage.models import LineageNodeValidationPreviewLineageNode3Command
from acme_data.domains.lineage.models import LineageNodeValidationValidateLineageNode0Command
from acme_data.domains.lineage.models import to_lineage_node_validation_preview_lineage_node3_command
from acme_data.domains.lineage.models import to_lineage_node_validation_validate_lineage_node0_command
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import run_steps
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


@dataclass(slots=True)
class LineageNodeValidationServicer(
    lineage_v1_lineage_node_validation_service_pb2_grpc.LineageNodeValidationServiceServicer
):
    deps: Dependencies

    @rpc_errors
    async def CheckLineageNodeEligibility(
        self, request: lineage_v1_lineage_node_validation_service_pb2.CheckLineageNodeEligibilityRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_lineage_node_validation_service_pb2.CheckLineageNodeEligibilityResponse:
        """Checks a lineage node."""
        return await self.handle_check_lineage_node_eligibility(request)

    @rpc_errors
    async def ExplainLineageNodeDecision(
        self, request: lineage_v1_lineage_node_validation_service_pb2.ExplainLineageNodeDecisionRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_lineage_node_validation_service_pb2.ExplainLineageNodeDecisionResponse:
        """Explains a lineage node."""
        return await self.handle_explain_lineage_node_decision(request)

    @rpc_errors
    @retry_transient
    async def GetLineageNodeRules(
        self, request: lineage_v1_lineage_node_validation_service_pb2.GetLineageNodeRulesRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_lineage_node_validation_service_pb2.GetLineageNodeRulesResponse:
        """Returns a lineage node."""
        return await self.handle_get_lineage_node_rules(request)

    @rpc_errors
    async def LintLineageNodes(
        self, request: lineage_v1_lineage_node_validation_service_pb2.LintLineageNodesRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_lineage_node_validation_service_pb2.LintLineageNodesResponse:
        """Lints a lineage node."""
        return await self.handle_lint_lineage_nodes(request)

    @rpc_errors
    async def NormalizeLineageNode(
        self, request: lineage_v1_lineage_node_validation_service_pb2.NormalizeLineageNodeRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_lineage_node_validation_service_pb2.NormalizeLineageNodeResponse:
        """Normalizes a lineage node."""
        return await self.handle_normalize_lineage_node(request)

    @rpc_errors
    async def PreviewLineageNode(
        self, request: lineage_v1_lineage_node_validation_service_pb2.PreviewLineageNodeRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_lineage_node_validation_service_pb2.PreviewLineageNodeResponse:
        """Previews a lineage node."""
        return await self.handle_preview_lineage_node(request)

    @rpc_errors
    async def ValidateLineageNode(
        self, request: lineage_v1_lineage_node_validation_service_pb2.ValidateLineageNodeRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_lineage_node_validation_service_pb2.ValidateLineageNodeResponse:
        """Validates a lineage node."""
        return await self.handle_validate_lineage_node(request)

    async def handle_check_lineage_node_eligibility(
        self,
        request: lineage_v1_lineage_node_validation_service_pb2.CheckLineageNodeEligibilityRequest
    ) -> lineage_v1_lineage_node_validation_service_pb2.CheckLineageNodeEligibilityResponse:
        """Checks a lineage node."""
        deps = self.deps
        response = lineage_v1_lineage_node_validation_service_pb2.CheckLineageNodeEligibilityResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CheckLineageNodeEligibility', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'CheckLineageNodeEligibility',
                {'reason': request.reason}
            )
            await deps.repository.save_lineage_node(request.context.tenant_id, request.lineage_node)
            response_0 = lineage_v1_lineage_node_calculation_service_pb2.ExplainLineageNodeCalculationResponse()
            response_1 = lineage_v1_lineage_node_calculation_service_pb2.GetLineageNodeRatesResponse()
            response_2 = lineage_v1_lineage_edge_calculation_service_pb2.CompareLineageEdgeOptionsResponse()
            outgoing_0 = lineage_v1_lineage_node_calculation_service_pb2.ExplainLineageNodeCalculationRequest(
                context=request.context,
                lineage_node=lineage_v1_lineage_pb2.LineageNode(
                    children=[
                        lineage_v1_lineage_pb2.LineageNode(
                            children=[
                                lineage_v1_lineage_pb2.LineageNode(
                                    location=common_v1_address_pb2.PostalAddress(
                                        locality=request.lineage_node.location.locality,
                                        postal_code=request.lineage_node.location.postal_code,
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
            port_0: LineageNodeValidationCheckLineageNodeEligibility0Port = LineageNodeValidationCheckLineageNodeEligibility0Adapter(
                deps.clients.lineage_lineage_node_calculation,
                deps.settings.timeout
            )
            response_0 = await port_0.execute(outgoing_0)
            outgoing_1 = lineage_v1_lineage_node_calculation_service_pb2.GetLineageNodeRatesRequest(
                context=request.context,
                lineage_node_id=request.lineage_node_id
            )
            steps_1 = [
                partial(
                    deps.clients.lineage_lineage_node_calculation.GetLineageNodeRates,
                    outgoing_1,
                    timeout=deps.settings.timeout
                )
            ]
            results_1 = await run_steps(steps_1)
            response_1 = results_1[-1]
            outgoing_2 = lineage_v1_lineage_edge_calculation_service_pb2.CompareLineageEdgeOptionsRequest(
                context=request.context,
                details=lineage_v1_lineage_edge_calculation_service_pb2.CompareLineageEdgeOptionsRequest.Details(
                    destination=common_v1_address_pb2.PostalAddress(
                        lines=list(response_0.lineage_node.location.lines),
                        recipient=response_1.lineage_node.location.recipient
                    )
                ),
                lineage_edge=lineage_v1_lineage_pb2.LineageEdge(
                    subject=lineage_v1_refs_pb2.ImpactRef(display_name=response_1.lineage_node.manager.display_name)
                )
            )
            response_2 = await LineageNodeValidationCheckLineageNodeEligibility2Adapter(
                deps.clients.lineage_lineage_edge_calculation,
                deps.settings.timeout
            )(outgoing_2)
            returned_0_0 = response_0.lineage_node.attributes
            returned_0_0_part_1 = response.lineage_node.children.add()
            returned_0_0_part_2 = returned_0_0_part_1.children.add()
            returned_0_0_part_2.attributes.update(returned_0_0)
            returned_0_1 = response_0.lineage_node.audit.updated_by
            if returned_0_1:
                response.lineage_node.audit.updated_by = returned_0_1
            returned_1_0 = response_1.lineage_node.location
            returned_1_0_part_1 = response.lineage_node.children.add()
            returned_1_0_part_2 = returned_1_0_part_1.children.add()
            returned_1_0_part_3 = returned_1_0_part_2.children.add()
            if returned_1_0.ListFields():
                returned_1_0_part_3.location.MergeFrom(returned_1_0)
            returned_1_1 = response_1.lineage_node.depth
            returned_1_1_part_1 = response.lineage_node.children.add()
            if returned_1_1:
                returned_1_1_part_1.depth = returned_1_1
            returned_2_0 = response_2.result.details
            response.result.details.update(returned_2_0)
            echoed_0 = request.lineage_node_id
            response.lineage_node.lineage_node_id = echoed_0
            echoed_1 = request.lineage_node.attributes
            response.lineage_node.attributes.update(echoed_1)
            return response

    async def handle_explain_lineage_node_decision(
        self,
        request: lineage_v1_lineage_node_validation_service_pb2.ExplainLineageNodeDecisionRequest
    ) -> lineage_v1_lineage_node_validation_service_pb2.ExplainLineageNodeDecisionResponse:
        """Explains a lineage node."""
        deps = self.deps
        response = lineage_v1_lineage_node_validation_service_pb2.ExplainLineageNodeDecisionResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ExplainLineageNodeDecision', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ExplainLineageNodeDecision',
                {'reason': request.reason}
            )
            await deps.repository.save_lineage_node(request.context.tenant_id, request.lineage_node)
            response_0 = lineage_v1_lineage_edge_calculation_service_pb2.SimulateLineageEdgeResponse()
            response_1 = lineage_v1_lineage_node_calculation_service_pb2.EstimateLineageNodeResponse()
            outgoing_0 = lineage_v1_lineage_edge_calculation_service_pb2.SimulateLineageEdgeRequest(
                context=request.context,
                details=lineage_v1_lineage_edge_calculation_service_pb2.SimulateLineageEdgeRequest.Details(
                    destination=common_v1_address_pb2.PostalAddress(
                        lines=list(request.lineage_node.location.lines),
                        postal_code=request.lineage_node.location.postal_code,
                        recipient=request.lineage_node.location.recipient
                    )
                )
            )
            response_0 = cast(lineage_v1_lineage_edge_calculation_service_pb2.SimulateLineageEdgeResponse, await deps.bus.request(
                'acme.lineage.v1.LineageNodeValidationService/ExplainLineageNodeDecision/0', outgoing_0, deps.settings.timeout,
            ))
            outgoing_1 = lineage_v1_lineage_node_calculation_service_pb2.EstimateLineageNodeRequest(
                context=request.context,
                lineage_node=lineage_v1_lineage_pb2.LineageNode(
                    children=[
                        lineage_v1_lineage_pb2.LineageNode(
                            children=[
                                lineage_v1_lineage_pb2.LineageNode(
                                    audit=common_v1_audit_pb2.AuditInfo(
                                        created_by=request.lineage_node.audit.created_by
                                    ),
                                    location=common_v1_address_pb2.PostalAddress(
                                        lines=list(request.lineage_node.location.lines),
                                        recipient=request.lineage_node.location.recipient
                                    ),
                                    manager=identity_v1_refs_pb2.UserRef(email=request.details.contact.email)
                                )
                            ]
                        )
                    ]
                )
            )
            response_1 = await deps.clients.lineage_lineage_node_calculation.EstimateLineageNode(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.status
            if returned_0_0:
                response.result.status = returned_0_0
            returned_0_1 = response_0.lineage_edge.subject.display_name
            returned_0_1_part_1 = response.lineage_node.children.add()
            returned_0_1_part_2 = returned_0_1_part_1.children.add()
            if returned_0_1:
                returned_0_1_part_2.manager.display_name = returned_0_1
            returned_1_0 = response_1.lineage_node.depth
            if returned_1_0:
                response.lineage_node.depth = returned_1_0
            echoed_0 = request.lineage_node_id
            response.lineage_node.lineage_node_id = echoed_0
            echoed_1 = request.lineage_node.attributes
            response.lineage_node.attributes.update(echoed_1)
            return response

    async def handle_get_lineage_node_rules(
        self,
        request: lineage_v1_lineage_node_validation_service_pb2.GetLineageNodeRulesRequest
    ) -> lineage_v1_lineage_node_validation_service_pb2.GetLineageNodeRulesResponse:
        """Returns a lineage node."""
        deps = self.deps
        response = lineage_v1_lineage_node_validation_service_pb2.GetLineageNodeRulesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('GetLineageNodeRules', extra={'fields': {'locale': request.context.locale}})
            await deps.repository.audit(
                request.context.tenant_id,
                'GetLineageNodeRules',
                {'locale': request.context.locale}
            )
            echoed_0 = request.lineage_node_id
            response.lineage_node.lineage_node_id = echoed_0
            return response

    async def handle_lint_lineage_nodes(
        self,
        request: lineage_v1_lineage_node_validation_service_pb2.LintLineageNodesRequest
    ) -> lineage_v1_lineage_node_validation_service_pb2.LintLineageNodesResponse:
        """Lints a lineage node."""
        deps = self.deps
        response = lineage_v1_lineage_node_validation_service_pb2.LintLineageNodesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('LintLineageNodes', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'LintLineageNodes', {'reason': request.reason})
            await deps.repository.save_lineage_node(request.context.tenant_id, request.lineage_node)
            response_0 = lineage_v1_lineage_node_calculation_service_pb2.ExplainLineageNodeCalculationResponse()
            response_1 = lineage_v1_lineage_edge_calculation_service_pb2.EstimateLineageEdgeResponse()
            outgoing_0 = lineage_v1_lineage_node_calculation_service_pb2.ExplainLineageNodeCalculationRequest(
                context=request.context,
                lineage_node=lineage_v1_lineage_pb2.LineageNode(
                    children=[
                        lineage_v1_lineage_pb2.LineageNode(
                            children=[
                                lineage_v1_lineage_pb2.LineageNode(
                                    audit=common_v1_audit_pb2.AuditInfo(
                                        updated_by=request.lineage_node.audit.updated_by
                                    ),
                                    location=common_v1_address_pb2.PostalAddress(
                                        country_code=request.lineage_node.location.country_code
                                    ),
                                    manager=identity_v1_refs_pb2.UserRef(
                                        display_name=request.lineage_node.manager.display_name,
                                        user_id=request.lineage_node.manager.user_id
                                    )
                                )
                            ]
                        )
                    ]
                )
            )
            method_name_0 = 'ExplainLineageNodeCalculation'
            response_0 = await getattr(
                deps.clients.lineage_lineage_node_calculation,
                method_name_0
            )(outgoing_0, timeout=deps.settings.timeout)
            fields_1: dict[str, Any] = {
                'context': request.context,
                'details': {
                    'destination': {
                        'lines': list(response_0.lineage_node.location.lines),
                        'region': request.lineage_node.location.region
                    }
                },
                'lineage_edge': {'subject': {'display_name': request.lineage_node.manager.display_name}}
            }
            outgoing_1 = lineage_v1_lineage_edge_calculation_service_pb2.EstimateLineageEdgeRequest(**fields_1)
            response_1 = await deps.clients.lineage_lineage_edge_calculation.EstimateLineageEdge(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.lineage_node.parent_id
            returned_0_0_part_1 = response.lineage_node.children.add()
            returned_0_0_part_2 = returned_0_0_part_1.children.add()
            if returned_0_0:
                returned_0_0_part_2.parent_id = returned_0_0
            returned_1_0 = response_1.result.message
            if returned_1_0:
                response.outcome.message = returned_1_0
            echoed_0 = request.lineage_node_id
            response.lineage_node.lineage_node_id = echoed_0
            echoed_1 = request.lineage_node.status
            response.lineage_node.status = echoed_1
            return response

    async def handle_normalize_lineage_node(
        self,
        request: lineage_v1_lineage_node_validation_service_pb2.NormalizeLineageNodeRequest
    ) -> lineage_v1_lineage_node_validation_service_pb2.NormalizeLineageNodeResponse:
        """Normalizes a lineage node."""
        deps = self.deps
        response = lineage_v1_lineage_node_validation_service_pb2.NormalizeLineageNodeResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('NormalizeLineageNode', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'NormalizeLineageNode', {'reason': request.reason})
            await deps.repository.save_lineage_node(request.context.tenant_id, request.lineage_node)
            response_0 = lineage_v1_lineage_node_calculation_service_pb2.EstimateLineageNodeResponse()
            response_1 = search_v1_search_index_service_pb2.UpdateSearchIndexResponse()
            outgoing_0 = lineage_v1_lineage_node_calculation_service_pb2.EstimateLineageNodeRequest(
                context=request.context,
                lineage_node=lineage_v1_lineage_pb2.LineageNode(
                    children=[
                        lineage_v1_lineage_pb2.LineageNode(
                            children=[
                                lineage_v1_lineage_pb2.LineageNode(
                                    audit=common_v1_audit_pb2.AuditInfo(
                                        created_by=request.lineage_node.audit.created_by
                                    ),
                                    children=[
                                        lineage_v1_lineage_pb2.LineageNode(
                                            attributes=dict(request.lineage_node.attributes)
                                        )
                                    ],
                                    location=common_v1_address_pb2.PostalAddress(
                                        region=request.lineage_node.location.region
                                    ),
                                    manager=identity_v1_refs_pb2.UserRef(email=request.details.contact.email)
                                )
                            ]
                        )
                    ]
                )
            )
            document_0 = MessageToDict(outgoing_0, preserving_proto_field_name=True)
            outgoing_0 = ParseDict(
                document_0,
                lineage_v1_lineage_node_calculation_service_pb2.EstimateLineageNodeRequest()
            )
            response_0 = await deps.clients.lineage_lineage_node_calculation.EstimateLineageNode(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = search_v1_search_index_service_pb2.UpdateSearchIndexRequest(
                context=request.context,
                search_index=search_v1_search_pb2.SearchIndex(
                    owner=identity_v1_refs_pb2.UserRef(email=request.details.contact.email)
                )
            )
            document_1 = MessageToJson(outgoing_1, preserving_proto_field_name=True)
            outgoing_1 = Parse(document_1, search_v1_search_index_service_pb2.UpdateSearchIndexRequest())
            response_1 = await deps.clients.search_search_index.UpdateSearchIndex(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.lineage_node.audit.updated_by
            returned_0_0_part_1 = response.lineage_node.children.add()
            returned_0_0_part_2 = returned_0_0_part_1.children.add()
            if returned_0_0:
                returned_0_0_part_2.audit.updated_by = returned_0_0
            returned_0_1 = response_0.lineage_node.audit.created_at
            returned_0_1_part_1 = response.lineage_node.children.add()
            returned_0_1_part_2 = returned_0_1_part_1.children.add()
            if returned_0_1.ListFields():
                returned_0_1_part_2.audit.created_at.MergeFrom(returned_0_1)
            returned_1_0 = response_1.search_index.address.lines
            returned_1_0_part_1 = response.lineage_node.children.add()
            returned_1_0_part_2 = returned_1_0_part_1.children.add()
            returned_1_0_part_2.location.lines.extend(returned_1_0)
            echoed_0 = request.lineage_node_id
            response.lineage_node.lineage_node_id = echoed_0
            echoed_1 = request.lineage_node.attributes
            response.lineage_node.attributes.update(echoed_1)
            return response

    async def handle_preview_lineage_node(
        self,
        request: lineage_v1_lineage_node_validation_service_pb2.PreviewLineageNodeRequest
    ) -> lineage_v1_lineage_node_validation_service_pb2.PreviewLineageNodeResponse:
        """Previews a lineage node."""
        deps = self.deps
        response = lineage_v1_lineage_node_validation_service_pb2.PreviewLineageNodeResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('PreviewLineageNode', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'PreviewLineageNode', {'reason': request.reason})
            await deps.repository.save_lineage_node(request.context.tenant_id, request.lineage_node)
            response_0 = lineage_v1_lineage_node_calculation_service_pb2.EstimateLineageNodeResponse()
            response_1 = featureflags_v1_feature_flag_query_service_pb2.ExportFeatureFlagsResponse()
            response_2 = lineage_v1_lineage_edge_calculation_service_pb2.EstimateLineageEdgeResponse()
            response_3 = lineage_v1_lineage_edge_calculation_service_pb2.CompareLineageEdgeOptionsResponse()
            outgoing_0 = lineage_v1_lineage_node_calculation_service_pb2.EstimateLineageNodeRequest()
            outgoing_0.context.CopyFrom(request.context)
            field_0_1_part_1 = outgoing_0.lineage_node.children.add()
            field_0_1_part_2 = field_0_1_part_1.children.add()
            field_0_1_part_2.audit.created_at.CopyFrom(request.lineage_node.audit.created_at)
            field_0_2_part_1 = outgoing_0.lineage_node.children.add()
            field_0_2_part_2 = field_0_2_part_1.children.add()
            field_0_2_part_3 = field_0_2_part_2.children.add()
            field_0_2_part_3.parent_id = request.lineage_node.parent_id
            field_0_3_part_1 = outgoing_0.lineage_node.children.add()
            field_0_3_part_2 = field_0_3_part_1.children.add()
            field_0_3_part_3 = field_0_3_part_2.children.add()
            field_0_3_part_3.status = request.lineage_node.status
            field_0_4_part_1 = outgoing_0.lineage_node.children.add()
            field_0_4_part_2 = field_0_4_part_1.children.add()
            field_0_4_part_3 = field_0_4_part_2.children.add()
            field_0_4_part_3.manager.CopyFrom(request.lineage_node.manager)
            merged_0 = lineage_v1_lineage_node_calculation_service_pb2.EstimateLineageNodeRequest()
            merged_0.MergeFrom(outgoing_0)
            outgoing_0.CopyFrom(merged_0)
            response_0 = await deps.clients.lineage_lineage_node_calculation.EstimateLineageNode(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = featureflags_v1_feature_flag_query_service_pb2.ExportFeatureFlagsRequest(
                context=request.context,
                filter=featureflags_v1_feature_flag_query_service_pb2.ExportFeatureFlagsRequest.Filter(
                    region=response_0.lineage_node.location.region
                )
            )
            async for chunk_1 in deps.clients.featureflags_feature_flag_query.ExportFeatureFlags(
                outgoing_1,
                timeout=deps.settings.timeout
            ):
                response_1 = chunk_1
            outgoing_2 = lineage_v1_lineage_edge_calculation_service_pb2.EstimateLineageEdgeRequest(
                context=request.context,
                details=lineage_v1_lineage_edge_calculation_service_pb2.EstimateLineageEdgeRequest.Details(
                    currency_code=response_0.breakdown.currency_code,
                    destination=common_v1_address_pb2.PostalAddress(
                        lines=list(request.lineage_node.location.lines),
                        locality=request.lineage_node.location.locality
                    )
                ),
                lineage_edge=lineage_v1_lineage_pb2.LineageEdge(
                    subject=lineage_v1_refs_pb2.ImpactRef(display_name=request.lineage_node.manager.display_name)
                )
            )
            registered_2 = cast(
                lineage_v1_lineage_edge_calculation_service_pb2_grpc.LineageEdgeCalculationServiceStub,
                deps.clients.registry['acme.lineage.v1.LineageEdgeCalculationService']
            )
            response_2 = await registered_2.EstimateLineageEdge(outgoing_2, timeout=deps.settings.timeout)
            command_3 = LineageNodeValidationPreviewLineageNode3Command(
                context=request.context,
                lineage_edge_subject_display_name=request.lineage_node.manager.display_name,
                details_destination_region=response_0.lineage_node.location.region
            )
            outgoing_3 = to_lineage_node_validation_preview_lineage_node3_command(command_3)
            response_3 = await deps.clients.lineage_lineage_edge_calculation.CompareLineageEdgeOptions(
                outgoing_3,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.lineage_node.path
            returned_0_0_part_1 = response.lineage_node.children.add()
            returned_0_0_part_2 = returned_0_0_part_1.children.add()
            returned_0_0_part_2.path.extend(returned_0_0)
            returned_2_0 = response_2.result.details
            response.result.details.update(returned_2_0)
            returned_3_0 = response_3.result.details
            response.result.details.update(returned_3_0)
            returned_3_1 = response_3.result.message
            if returned_3_1:
                response.result.message = returned_3_1
            echoed_0 = request.lineage_node_id
            response.lineage_node.lineage_node_id = echoed_0
            echoed_1 = request.lineage_node.status
            response.lineage_node.status = echoed_1
            return response

    async def handle_validate_lineage_node(
        self,
        request: lineage_v1_lineage_node_validation_service_pb2.ValidateLineageNodeRequest
    ) -> lineage_v1_lineage_node_validation_service_pb2.ValidateLineageNodeResponse:
        """Validates a lineage node."""
        deps = self.deps
        response = lineage_v1_lineage_node_validation_service_pb2.ValidateLineageNodeResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ValidateLineageNode', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'ValidateLineageNode', {'reason': request.reason})
            await deps.repository.save_lineage_node(request.context.tenant_id, request.lineage_node)
            response_0 = lineage_v1_lineage_node_calculation_service_pb2.RecalculateLineageNodesResponse()
            command_0 = LineageNodeValidationValidateLineageNode0Command.model_validate(
                {
                    'context': request.context,
                    'lineage_node_children_children_audit_created_by': request.lineage_node.audit.created_by,
                    'lineage_node_children_location_country_code': request.lineage_node.location.country_code
                }
            )
            outgoing_0 = to_lineage_node_validation_validate_lineage_node0_command(command_0)
            response_0 = await deps.clients.lineage_lineage_node_calculation.RecalculateLineageNodes(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.lineage_node.audit.updated_by
            if returned_0_0:
                response.lineage_node.audit.updated_by = returned_0_0
            returned_0_1 = response_0.lineage_node.location.lines
            response.lineage_node.location.lines.extend(returned_0_1)
            echoed_0 = request.lineage_node_id
            response.lineage_node.lineage_node_id = echoed_0
            echoed_1 = request.lineage_node.depth
            response.lineage_node.depth = echoed_1
            return response
