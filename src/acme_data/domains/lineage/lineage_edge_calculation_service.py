"""Computes the figures of a lineage edge, such as totals, taxes, and estimates."""

from __future__ import annotations

from collections.abc import AsyncIterator
from collections.abc import Awaitable
from collections.abc import Callable
from dataclasses import dataclass
from functools import partial
from typing import Any
from typing import cast
import asyncio
import logging

from google.protobuf.json_format import MessageToDict
from google.protobuf.json_format import ParseDict
import grpc

from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.identity.v1 import user_service_pb2 as identity_v1_user_service_pb2
from acme.lineage.v1 import lineage_edge_calculation_service_pb2 as lineage_v1_lineage_edge_calculation_service_pb2
from acme.lineage.v1 import (
    lineage_edge_calculation_service_pb2_grpc as lineage_v1_lineage_edge_calculation_service_pb2_grpc,
)
from acme.lineage.v1 import lineage_node_calculation_service_pb2 as lineage_v1_lineage_node_calculation_service_pb2
from acme.lineage.v1 import (
    lineage_node_calculation_service_pb2_grpc as lineage_v1_lineage_node_calculation_service_pb2_grpc,
)
from acme.lineage.v1 import lineage_pb2 as lineage_v1_lineage_pb2
from acme.metrics.v1 import dashboard_export_service_pb2 as metrics_v1_dashboard_export_service_pb2
from acme.metrics.v1 import metric_alert_export_service_pb2 as metrics_v1_metric_alert_export_service_pb2
from acme.metrics.v1 import metric_series_query_service_pb2 as metrics_v1_metric_series_query_service_pb2
from acme.metrics.v1 import metric_series_validation_service_pb2 as metrics_v1_metric_series_validation_service_pb2
from acme.patients.v1 import refs_pb2 as patients_v1_refs_pb2
from acme.prescriptions.v1 import (
    prescription_calculation_service_pb2 as prescriptions_v1_prescription_calculation_service_pb2,
)
from acme.prescriptions.v1 import prescriptions_pb2 as prescriptions_v1_prescriptions_pb2
from acme.search.v1 import search_index_validation_service_pb2 as search_v1_search_index_validation_service_pb2
from acme.search.v1 import search_pb2 as search_v1_search_pb2

from acme_data.domains.lineage import hooks
from acme_data.domains.lineage.adapters import LineageEdgeCalculationEstimateLineageEdge0Adapter
from acme_data.domains.lineage.adapters import LineageEdgeCalculationEstimateLineageEdge0Port
from acme_data.domains.lineage.adapters import LineageEdgeCalculationExplainLineageEdgeCalculation0Adapter
from acme_data.domains.lineage.dependencies import Dependencies
from acme_data.domains.lineage.models import LineageEdgeCalculationCalculateLineageEdge1Command
from acme_data.domains.lineage.models import LineageEdgeCalculationCompareLineageEdgeOptions0Command
from acme_data.domains.lineage.models import to_lineage_edge_calculation_calculate_lineage_edge1_command
from acme_data.domains.lineage.models import to_lineage_edge_calculation_compare_lineage_edge_options0_command
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import run_steps
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_id
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


@dataclass(slots=True)
class LineageEdgeCalculationServicer(
    lineage_v1_lineage_edge_calculation_service_pb2_grpc.LineageEdgeCalculationServiceServicer
):
    deps: Dependencies

    @rpc_errors
    async def CalculateLineageEdge(
        self, request: lineage_v1_lineage_edge_calculation_service_pb2.CalculateLineageEdgeRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_lineage_edge_calculation_service_pb2.CalculateLineageEdgeResponse:
        """Calculates a lineage edge."""
        return await self.handle_calculate_lineage_edge(request)

    @rpc_errors
    async def CompareLineageEdgeOptions(
        self, request: lineage_v1_lineage_edge_calculation_service_pb2.CompareLineageEdgeOptionsRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_lineage_edge_calculation_service_pb2.CompareLineageEdgeOptionsResponse:
        """Compares a lineage edge."""
        return await self.handle_compare_lineage_edge_options(request)

    @rpc_errors
    async def EstimateLineageEdge(
        self, request: lineage_v1_lineage_edge_calculation_service_pb2.EstimateLineageEdgeRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_lineage_edge_calculation_service_pb2.EstimateLineageEdgeResponse:
        """Estimates a lineage edge."""
        return await self.handle_estimate_lineage_edge(request)

    @rpc_errors
    async def ExplainLineageEdgeCalculation(
        self, request: lineage_v1_lineage_edge_calculation_service_pb2.ExplainLineageEdgeCalculationRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_lineage_edge_calculation_service_pb2.ExplainLineageEdgeCalculationResponse:
        """Explains a lineage edge."""
        return await self.handle_explain_lineage_edge_calculation(request)

    @rpc_errors
    @retry_transient
    async def GetLineageEdgeRates(
        self, request: lineage_v1_lineage_edge_calculation_service_pb2.GetLineageEdgeRatesRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_lineage_edge_calculation_service_pb2.GetLineageEdgeRatesResponse:
        """Returns a lineage edge."""
        return await self.handle_get_lineage_edge_rates(request)

    @rpc_errors
    async def QuoteLineageEdge(
        self, request: lineage_v1_lineage_edge_calculation_service_pb2.QuoteLineageEdgeRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_lineage_edge_calculation_service_pb2.QuoteLineageEdgeResponse:
        """Quotes a lineage edge."""
        return await self.handle_quote_lineage_edge(request)

    @rpc_errors
    async def SimulateLineageEdge(
        self, request: lineage_v1_lineage_edge_calculation_service_pb2.SimulateLineageEdgeRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_lineage_edge_calculation_service_pb2.SimulateLineageEdgeResponse:
        """Simulates a lineage edge."""
        return await self.handle_simulate_lineage_edge(request)

    async def handle_calculate_lineage_edge(
        self,
        request: lineage_v1_lineage_edge_calculation_service_pb2.CalculateLineageEdgeRequest
    ) -> lineage_v1_lineage_edge_calculation_service_pb2.CalculateLineageEdgeResponse:
        """Calculates a lineage edge."""
        deps = self.deps
        response = lineage_v1_lineage_edge_calculation_service_pb2.CalculateLineageEdgeResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CalculateLineageEdge', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'CalculateLineageEdge', {'reason': request.reason})
            await deps.repository.save_lineage_edge(request.context.tenant_id, request.lineage_edge)
            response_0 = lineage_v1_lineage_node_calculation_service_pb2.EstimateLineageNodeResponse()
            response_1 = lineage_v1_lineage_node_calculation_service_pb2.RecalculateLineageNodesResponse()
            outgoing_0 = lineage_v1_lineage_node_calculation_service_pb2.EstimateLineageNodeRequest(
                context=request.context,
                lineage_node=lineage_v1_lineage_pb2.LineageNode(
                    children=[
                        lineage_v1_lineage_pb2.LineageNode(
                            children=[
                                lineage_v1_lineage_pb2.LineageNode(
                                    location=common_v1_address_pb2.PostalAddress(
                                        country_code=request.details.destination.country_code,
                                        lines=list(request.details.destination.lines),
                                        locality=request.details.destination.locality
                                    )
                                )
                            ],
                            manager=identity_v1_refs_pb2.UserRef(display_name=request.lineage_edge.subject.display_name)
                        )
                    ]
                )
            )
            registered_0 = cast(
                lineage_v1_lineage_node_calculation_service_pb2_grpc.LineageNodeCalculationServiceStub,
                deps.clients.registry['acme.lineage.v1.LineageNodeCalculationService']
            )
            response_0 = await registered_0.EstimateLineageNode(outgoing_0, timeout=deps.settings.timeout)
            command_1 = LineageEdgeCalculationCalculateLineageEdge1Command(
                context=request.context,
                lineage_node_children_children_audit_updated_at=response_0.lineage_node.audit.updated_at,
                lineage_node_children_children_location_recipient=request.details.destination.recipient,
                lineage_node_children_children_location_locality=response_0.lineage_node.location.locality
            )
            outgoing_1 = to_lineage_edge_calculation_calculate_lineage_edge1_command(command_1)
            response_1 = await deps.clients.lineage_lineage_node_calculation.RecalculateLineageNodes(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.details
            response.result.details.update(returned_0_0)
            returned_1_0 = response_1.result.message
            if returned_1_0:
                response.result.message = returned_1_0
            echoed_0 = request.lineage_edge_id
            response.lineage_edge.lineage_edge_id = echoed_0
            echoed_1 = request.lineage_edge.source
            response.lineage_edge.source = echoed_1
            return response

    async def handle_compare_lineage_edge_options(
        self,
        request: lineage_v1_lineage_edge_calculation_service_pb2.CompareLineageEdgeOptionsRequest
    ) -> lineage_v1_lineage_edge_calculation_service_pb2.CompareLineageEdgeOptionsResponse:
        """Compares a lineage edge."""
        deps = self.deps
        response = lineage_v1_lineage_edge_calculation_service_pb2.CompareLineageEdgeOptionsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CompareLineageEdgeOptions', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'CompareLineageEdgeOptions',
                {'reason': request.reason}
            )
            await deps.repository.save_lineage_edge(request.context.tenant_id, request.lineage_edge)
            response_0 = lineage_v1_lineage_node_calculation_service_pb2.ExplainLineageNodeCalculationResponse()
            response_1 = lineage_v1_lineage_node_calculation_service_pb2.CalculateLineageNodeResponse()
            response_2 = lineage_v1_lineage_node_calculation_service_pb2.QuoteLineageNodeResponse()
            response_3 = identity_v1_user_service_pb2.GetUserResponse()
            command_0 = LineageEdgeCalculationCompareLineageEdgeOptions0Command.model_validate(
                {
                    'context': request.context,
                    'lineage_node_children_children_location_lines': list(request.details.destination.lines),
                    'lineage_node_children_children_location_region': request.details.destination.region
                }
            )
            outgoing_0 = to_lineage_edge_calculation_compare_lineage_edge_options0_command(command_0)
            response_0 = await deps.clients.lineage_lineage_node_calculation.ExplainLineageNodeCalculation(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = lineage_v1_lineage_node_calculation_service_pb2.CalculateLineageNodeRequest(
                context=request.context,
                lineage_node=lineage_v1_lineage_pb2.LineageNode(
                    children=[
                        lineage_v1_lineage_pb2.LineageNode(
                            children=[
                                lineage_v1_lineage_pb2.LineageNode(
                                    audit=common_v1_audit_pb2.AuditInfo(
                                        created_by=response_0.lineage_node.audit.created_by
                                    ),
                                    location=common_v1_address_pb2.PostalAddress(
                                        locality=response_0.lineage_node.location.locality,
                                        recipient=request.details.destination.recipient
                                    ),
                                    manager=identity_v1_refs_pb2.UserRef(
                                        user_id=response_0.lineage_node.manager.user_id
                                    )
                                )
                            ]
                        )
                    ]
                )
            )
            send_1 = partial(
                deps.clients.lineage_lineage_node_calculation.CalculateLineageNode,
                timeout=deps.settings.timeout
            )
            response_1 = await send_1(outgoing_1)
            outgoing_2 = lineage_v1_lineage_node_calculation_service_pb2.QuoteLineageNodeRequest(
                context=request.context,
                lineage_node=lineage_v1_lineage_pb2.LineageNode(
                    children=[
                        lineage_v1_lineage_pb2.LineageNode(
                            children=[
                                lineage_v1_lineage_pb2.LineageNode(
                                    location=common_v1_address_pb2.PostalAddress(
                                        locality=response_1.lineage_node.location.locality,
                                        recipient=response_0.lineage_node.location.recipient,
                                        region=response_0.lineage_node.location.region
                                    )
                                )
                            ]
                        )
                    ]
                )
            )
            response_2 = await hooks.lineage_edge_calculation_compare_lineage_edge_options2(
                deps.clients.lineage_lineage_node_calculation,
                outgoing_2,
                deps.settings.timeout
            )
            outgoing_3 = identity_v1_user_service_pb2.GetUserRequest()
            outgoing_3.context.CopyFrom(request.context)
            outgoing_3.user_id = request.context.actor.user_id
            outgoing_3.context.tenant_id = tenant_id.get()
            response_3 = await deps.clients.identity_user.GetUser(outgoing_3, timeout=deps.settings.timeout)
            returned_0_0 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_0)
            returned_0_1 = response_0.result.message
            if returned_0_1:
                response.result.message = returned_0_1
            returned_1_0 = response_1.result.correlation_id
            if returned_1_0:
                response.result.correlation_id = returned_1_0
            returned_2_0 = response_2.result.reference_ids
            response.result.reference_ids.extend(returned_2_0)
            returned_2_1 = response_2.breakdown.currency_code
            if returned_2_1:
                response.breakdown.currency_code = returned_2_1
            returned_3_0 = response_3.result.message
            if returned_3_0:
                response.result.message = returned_3_0
            returned_3_1 = response_3.user.relationship_manager.display_name
            if returned_3_1:
                response.lineage_edge.subject.display_name = returned_3_1
            echoed_0 = request.lineage_edge_id
            response.lineage_edge.lineage_edge_id = echoed_0
            echoed_1 = request.lineage_edge.source
            response.lineage_edge.source = echoed_1
            return response

    async def handle_estimate_lineage_edge(
        self,
        request: lineage_v1_lineage_edge_calculation_service_pb2.EstimateLineageEdgeRequest
    ) -> lineage_v1_lineage_edge_calculation_service_pb2.EstimateLineageEdgeResponse:
        """Estimates a lineage edge."""
        deps = self.deps
        response = lineage_v1_lineage_edge_calculation_service_pb2.EstimateLineageEdgeResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('EstimateLineageEdge', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'EstimateLineageEdge', {'reason': request.reason})
            await deps.repository.save_lineage_edge(request.context.tenant_id, request.lineage_edge)
            response_0 = lineage_v1_lineage_node_calculation_service_pb2.RecalculateLineageNodesResponse()
            response_1 = search_v1_search_index_validation_service_pb2.ValidateSearchIndexResponse()
            outgoing_0 = lineage_v1_lineage_node_calculation_service_pb2.RecalculateLineageNodesRequest(
                context=request.context,
                lineage_node=lineage_v1_lineage_pb2.LineageNode(
                    children=[
                        lineage_v1_lineage_pb2.LineageNode(
                            children=[
                                lineage_v1_lineage_pb2.LineageNode(
                                    location=common_v1_address_pb2.PostalAddress(
                                        lines=list(request.details.destination.lines)
                                    )
                                )
                            ],
                            location=common_v1_address_pb2.PostalAddress(
                                postal_code=request.details.destination.postal_code
                            )
                        )
                    ]
                )
            )
            port_0: LineageEdgeCalculationEstimateLineageEdge0Port = LineageEdgeCalculationEstimateLineageEdge0Adapter(
                deps.clients.lineage_lineage_node_calculation,
                deps.settings.timeout
            )
            response_0 = await port_0.execute(outgoing_0)
            outgoing_1 = search_v1_search_index_validation_service_pb2.ValidateSearchIndexRequest(
                context=request.context,
                details=search_v1_search_index_validation_service_pb2.ValidateSearchIndexRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(email=response_0.lineage_node.manager.email)
                ),
                search_index=search_v1_search_pb2.SearchIndex(
                    address=common_v1_address_pb2.PostalAddress(
                        postal_code=response_0.lineage_node.location.postal_code
                    )
                )
            )
            steps_1 = [
                partial(
                    deps.clients.search_search_index_validation.ValidateSearchIndex,
                    outgoing_1,
                    timeout=deps.settings.timeout
                )
            ]
            results_1 = await run_steps(steps_1)
            response_1 = results_1[-1]
            returned_0_0 = response_0.breakdown.currency_code
            if returned_0_0:
                response.breakdown.currency_code = returned_0_0
            returned_1_0 = response_1.search_index.dimensions.unit
            returned_1_0_part_1 = response.lineage_edge.measurements.add()
            if returned_1_0:
                returned_1_0_part_1.unit = returned_1_0
            returned_1_1 = response_1.outcome.status
            if returned_1_1:
                response.result.status = returned_1_1
            echoed_0 = request.lineage_edge_id
            response.lineage_edge.lineage_edge_id = echoed_0
            echoed_1 = request.lineage_edge.attributes
            response.lineage_edge.attributes.update(echoed_1)
            return response

    async def handle_explain_lineage_edge_calculation(
        self,
        request: lineage_v1_lineage_edge_calculation_service_pb2.ExplainLineageEdgeCalculationRequest
    ) -> lineage_v1_lineage_edge_calculation_service_pb2.ExplainLineageEdgeCalculationResponse:
        """Explains a lineage edge."""
        deps = self.deps
        response = lineage_v1_lineage_edge_calculation_service_pb2.ExplainLineageEdgeCalculationResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ExplainLineageEdgeCalculation', extra={'fields': {'locale': request.details.locale}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ExplainLineageEdgeCalculation',
                {'locale': request.details.locale}
            )
            await deps.repository.save_lineage_edge(request.context.tenant_id, request.lineage_edge)
            response_0 = prescriptions_v1_prescription_calculation_service_pb2.EstimatePrescriptionResponse()
            response_1 = lineage_v1_lineage_node_calculation_service_pb2.SimulateLineageNodeResponse()
            response_2 = metrics_v1_metric_alert_export_service_pb2.ScheduleMetricAlertExportResponse()
            outgoing_0 = prescriptions_v1_prescription_calculation_service_pb2.EstimatePrescriptionRequest(
                context=request.context,
                prescription=prescriptions_v1_prescriptions_pb2.Prescription(
                    counterparty=patients_v1_refs_pb2.PatientRef(
                        display_name=request.lineage_edge.subject.display_name,
                        email=request.details.contact.email
                    )
                )
            )
            response_0 = await LineageEdgeCalculationExplainLineageEdgeCalculation0Adapter(
                deps.clients.prescriptions_prescription_calculation,
                deps.settings.timeout
            )(outgoing_0)
            outgoing_1 = lineage_v1_lineage_node_calculation_service_pb2.SimulateLineageNodeRequest(
                context=request.context,
                lineage_node=lineage_v1_lineage_pb2.LineageNode(
                    children=[
                        lineage_v1_lineage_pb2.LineageNode(
                            children=[
                                lineage_v1_lineage_pb2.LineageNode(
                                    location=common_v1_address_pb2.PostalAddress(
                                        postal_code=response_0.prescription.billing_address.postal_code
                                    ),
                                    manager=identity_v1_refs_pb2.UserRef(
                                        display_name=request.lineage_edge.subject.display_name
                                    )
                                )
                            ]
                        )
                    ]
                )
            )
            response_1 = cast(lineage_v1_lineage_node_calculation_service_pb2.SimulateLineageNodeResponse, await deps.bus.request(
                'acme.lineage.v1.LineageEdgeCalculationService/ExplainLineageEdgeCalculation/1', outgoing_1, deps.settings.timeout,
            ))
            outgoing_2 = metrics_v1_metric_alert_export_service_pb2.ScheduleMetricAlertExportRequest(
                annotations=dict(request.annotations),
                context=request.context,
                details=metrics_v1_metric_alert_export_service_pb2.ScheduleMetricAlertExportRequest.Details(
                    filters=dict(response_1.result.details)
                ),
                reason=request.reason
            )
            response_2 = await deps.clients.metrics_metric_alert_export.ScheduleMetricAlertExport(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.prescription.counterparty.display_name
            if returned_0_0:
                response.lineage_edge.subject.display_name = returned_0_0
            returned_1_0 = response_1.result.message
            if returned_1_0:
                response.outcome.message = returned_1_0
            returned_1_1 = response_1.result.status
            if returned_1_1:
                response.result.status = returned_1_1
            returned_2_0 = response_2.result.correlation_id
            if returned_2_0:
                response.result.correlation_id = returned_2_0
            returned_2_1 = response_2.result.message
            if returned_2_1:
                response.outcome.message = returned_2_1
            echoed_0 = request.lineage_edge_id
            response.lineage_edge.lineage_edge_id = echoed_0
            echoed_1 = request.lineage_edge.source
            response.lineage_edge.source = echoed_1
            return response

    async def handle_get_lineage_edge_rates(
        self,
        request: lineage_v1_lineage_edge_calculation_service_pb2.GetLineageEdgeRatesRequest
    ) -> lineage_v1_lineage_edge_calculation_service_pb2.GetLineageEdgeRatesResponse:
        """Returns a lineage edge."""
        deps = self.deps
        response = lineage_v1_lineage_edge_calculation_service_pb2.GetLineageEdgeRatesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('GetLineageEdgeRates', extra={'fields': {'domain': 'lineage'}})
            await deps.repository.audit(request.context.tenant_id, 'GetLineageEdgeRates', {})
            response_0 = lineage_v1_lineage_node_calculation_service_pb2.QuoteLineageNodeResponse()
            outgoing_0 = lineage_v1_lineage_node_calculation_service_pb2.QuoteLineageNodeRequest(
                context=request.context,
                lineage_node=lineage_v1_lineage_pb2.LineageNode(
                    children=[
                        lineage_v1_lineage_pb2.LineageNode(
                            children=[
                                lineage_v1_lineage_pb2.LineageNode(
                                    audit=common_v1_audit_pb2.AuditInfo(updated_at=request.context.deadline),
                                    manager=identity_v1_refs_pb2.UserRef(email=request.context.actor.email),
                                    parent_id=request.lineage_edge_id
                                )
                            ]
                        )
                    ],
                    manager=identity_v1_refs_pb2.UserRef(user_id=request.context.actor.user_id)
                )
            )
            response_0 = await deps.clients.lineage_lineage_node_calculation.QuoteLineageNode(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.lineage_node.manager.display_name
            if returned_0_0:
                response.lineage_edge.subject.display_name = returned_0_0
            echoed_0 = request.lineage_edge_id
            response.lineage_edge.lineage_edge_id = echoed_0
            return response

    async def handle_quote_lineage_edge(
        self,
        request: lineage_v1_lineage_edge_calculation_service_pb2.QuoteLineageEdgeRequest
    ) -> lineage_v1_lineage_edge_calculation_service_pb2.QuoteLineageEdgeResponse:
        """Quotes a lineage edge."""
        deps = self.deps
        response = lineage_v1_lineage_edge_calculation_service_pb2.QuoteLineageEdgeResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('QuoteLineageEdge', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'QuoteLineageEdge', {'reason': request.reason})
            await deps.repository.save_lineage_edge(request.context.tenant_id, request.lineage_edge)
            response_0 = metrics_v1_metric_series_validation_service_pb2.NormalizeMetricSeriesResponse()
            response_1 = lineage_v1_lineage_node_calculation_service_pb2.ExplainLineageNodeCalculationResponse()
            fields_0: dict[str, Any] = {
                'context': request.context,
                'metric_series': {
                    'address': {
                        'country_code': request.details.destination.country_code,
                        'lines': list(request.details.destination.lines)
                    }
                }
            }
            outgoing_0 = metrics_v1_metric_series_validation_service_pb2.NormalizeMetricSeriesRequest(**fields_0)
            response_0 = await deps.clients.metrics_metric_series_validation.NormalizeMetricSeries(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = lineage_v1_lineage_node_calculation_service_pb2.ExplainLineageNodeCalculationRequest(
                context=request.context,
                lineage_node=lineage_v1_lineage_pb2.LineageNode(
                    children=[
                        lineage_v1_lineage_pb2.LineageNode(
                            children=[
                                lineage_v1_lineage_pb2.LineageNode(
                                    location=common_v1_address_pb2.PostalAddress(
                                        country_code=request.details.destination.country_code
                                    )
                                )
                            ]
                        )
                    ]
                )
            )
            document_1 = MessageToDict(outgoing_1, preserving_proto_field_name=True)
            outgoing_1 = ParseDict(
                document_1,
                lineage_v1_lineage_node_calculation_service_pb2.ExplainLineageNodeCalculationRequest()
            )
            response_1 = await deps.clients.lineage_lineage_node_calculation.ExplainLineageNodeCalculation(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.outcome.message
            if returned_0_0:
                response.result.message = returned_0_0
            returned_0_1 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_1)
            returned_1_0 = response_1.outcome.message
            if returned_1_0:
                response.result.message = returned_1_0
            echoed_0 = request.lineage_edge_id
            response.lineage_edge.lineage_edge_id = echoed_0
            echoed_1 = request.lineage_edge.kind
            response.lineage_edge.kind = echoed_1
            return response

    async def handle_simulate_lineage_edge(
        self,
        request: lineage_v1_lineage_edge_calculation_service_pb2.SimulateLineageEdgeRequest
    ) -> lineage_v1_lineage_edge_calculation_service_pb2.SimulateLineageEdgeResponse:
        """Simulates a lineage edge."""
        deps = self.deps
        response = lineage_v1_lineage_edge_calculation_service_pb2.SimulateLineageEdgeResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SimulateLineageEdge', extra={'fields': {'currency_code': request.details.currency_code}})
            await deps.repository.audit(
                request.context.tenant_id,
                'SimulateLineageEdge',
                {'currency_code': request.details.currency_code}
            )
            await deps.repository.save_lineage_edge(request.context.tenant_id, request.lineage_edge)
            response_0 = metrics_v1_dashboard_export_service_pb2.ScheduleDashboardExportResponse()
            response_1 = metrics_v1_metric_series_query_service_pb2.BrowseMetricSeriesesResponse()
            response_2 = lineage_v1_lineage_node_calculation_service_pb2.SimulateLineageNodeResponse()
            outgoing_0 = metrics_v1_dashboard_export_service_pb2.ScheduleDashboardExportRequest(
                context=request.context,
                reason=request.reason
            )
            outgoing_2 = lineage_v1_lineage_node_calculation_service_pb2.SimulateLineageNodeRequest(
                context=request.context,
                lineage_node=lineage_v1_lineage_pb2.LineageNode(
                    children=[
                        lineage_v1_lineage_pb2.LineageNode(
                            children=[
                                lineage_v1_lineage_pb2.LineageNode(
                                    children=[
                                        lineage_v1_lineage_pb2.LineageNode(
                                            attributes=dict(request.lineage_edge.attributes)
                                        )
                                    ],
                                    manager=identity_v1_refs_pb2.UserRef(
                                        display_name=request.lineage_edge.subject.display_name
                                    )
                                )
                            ]
                        )
                    ]
                )
            )
            response_0, response_2 = await asyncio.gather(
                deps.clients.metrics_dashboard_export.ScheduleDashboardExport(
                    outgoing_0,
                    timeout=deps.settings.timeout
                ),
                deps.clients.lineage_lineage_node_calculation.SimulateLineageNode(
                    outgoing_2,
                    timeout=deps.settings.timeout
                ),
            )
            requests_1: list[metrics_v1_metric_series_query_service_pb2.BrowseMetricSeriesesRequest] = []
            for item_1 in request.lineage_edge.measurements:
                outgoing_1 = metrics_v1_metric_series_query_service_pb2.BrowseMetricSeriesesRequest(
                    context=request.context,
                    filter=metrics_v1_metric_series_query_service_pb2.BrowseMetricSeriesesRequest.Filter(
                        created_after=item_1.observed_at
                    )
                )
                requests_1.append(outgoing_1)
            replies_1 = await asyncio.gather(*(
                deps.clients.metrics_metric_series_query.BrowseMetricSerieses(
                    entry,
                    timeout=deps.settings.timeout
                ) for entry in requests_1
            ))
            if replies_1:
                response_1 = replies_1[-1]
            returned_0_0 = response_0.result.details
            response.result.details.update(returned_0_0)
            returned_2_0 = response_2.result.status
            if returned_2_0:
                response.result.status = returned_2_0
            returned_2_1 = response_2.lineage_node.manager.display_name
            if returned_2_1:
                response.lineage_edge.subject.display_name = returned_2_1
            echoed_0 = request.lineage_edge_id
            response.lineage_edge.lineage_edge_id = echoed_0
            echoed_1 = request.lineage_edge.source
            response.lineage_edge.source = echoed_1
            return response
