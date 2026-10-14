"""Application workflow for Entity Calculation."""

from __future__ import annotations

from functools import partial
from typing import cast
import logging

from google.protobuf.json_format import MessageToDict
from google.protobuf.json_format import MessageToJson
from google.protobuf.json_format import Parse
from google.protobuf.json_format import ParseDict

from acme.boxoffice.v1 import box_office_sale_query_service_pb2 as boxoffice_v1_box_office_sale_query_service_pb2
from acme.broadcasts.v1 import broadcast_service_pb2 as broadcasts_v1_broadcast_service_pb2
from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.customers.v1 import refs_pb2 as customers_v1_refs_pb2
from acme.featurestore.v1 import entity_calculation_service_pb2 as featurestore_v1_entity_calculation_service_pb2
from acme.featurestore.v1 import (
    feature_value_calculation_service_pb2 as featurestore_v1_feature_value_calculation_service_pb2,
)
from acme.featurestore.v1 import (
    feature_view_validation_service_pb2 as featurestore_v1_feature_view_validation_service_pb2,
)
from acme.featurestore.v1 import featurestore_pb2 as featurestore_v1_featurestore_pb2
from acme.fleet.v1 import vehicle_service_pb2 as fleet_v1_vehicle_service_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.lineage.v1 import impact_validation_service_pb2 as lineage_v1_impact_validation_service_pb2
from acme.lineage.v1 import impact_validation_service_pb2_grpc as lineage_v1_impact_validation_service_pb2_grpc
from acme.lineage.v1 import lineage_edge_query_service_pb2 as lineage_v1_lineage_edge_query_service_pb2
from acme.lineage.v1 import lineage_edge_validation_service_pb2 as lineage_v1_lineage_edge_validation_service_pb2
from acme.lineage.v1 import lineage_node_query_service_pb2 as lineage_v1_lineage_node_query_service_pb2
from acme.lineage.v1 import lineage_pb2 as lineage_v1_lineage_pb2
from acme.lineage.v1 import refs_pb2 as lineage_v1_refs_pb2
from acme.metrics.v1 import metric_alert_export_service_pb2 as metrics_v1_metric_alert_export_service_pb2

from acme_data.domains.featurestore.adapters import EntityCalculationExplainEntityCalculation2Adapter
from acme_data.domains.featurestore.adapters import EntityCalculationExplainEntityCalculation2Port
from acme_data.domains.featurestore.dependencies import Dependencies
from acme_data.domains.featurestore.models import EntityCalculationCompareEntityOptions1Command
from acme_data.domains.featurestore.models import EntityCalculationEstimateEntity0Command
from acme_data.domains.featurestore.models import to_entity_calculation_compare_entity_options1_command
from acme_data.domains.featurestore.models import to_entity_calculation_estimate_entity0_command
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import run_steps
from acme_data.platform.tenancy import tenant_id
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class EntityCalculationServicerWorkflow:
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    async def handle_calculate_entity(
        self,
        request: featurestore_v1_entity_calculation_service_pb2.CalculateEntityRequest
    ) -> featurestore_v1_entity_calculation_service_pb2.CalculateEntityResponse:
        """Calculates an entity."""
        deps = self.deps
        response = featurestore_v1_entity_calculation_service_pb2.CalculateEntityResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CalculateEntity', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'CalculateEntity', {'reason': request.reason})
            await deps.repository.save_entity(request.context.tenant_id, request.entity)
            response_0 = lineage_v1_lineage_edge_query_service_pb2.CountLineageEdgesResponse()
            response_1 = lineage_v1_lineage_edge_validation_service_pb2.ScoreLineageEdgeResponse()
            response_2 = metrics_v1_metric_alert_export_service_pb2.RetryMetricAlertExportResponse()
            response_3 = metrics_v1_metric_alert_export_service_pb2.StreamMetricAlertExportResponse()
            outgoing_0 = lineage_v1_lineage_edge_query_service_pb2.CountLineageEdgesRequest(
                context=request.context,
                filter=lineage_v1_lineage_edge_query_service_pb2.CountLineageEdgesRequest.Filter(
                    created_after=request.entity.audit.updated_at,
                    labels=dict(request.entity.attributes),
                    owner_id=request.entity.relationship_manager.user_id,
                    region=request.details.destination.region
                )
            )
            document_0 = MessageToDict(outgoing_0, preserving_proto_field_name=True)
            outgoing_0 = ParseDict(document_0, lineage_v1_lineage_edge_query_service_pb2.CountLineageEdgesRequest())
            response_0 = await deps.clients.lineage_lineage_edge_query.CountLineageEdges(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = lineage_v1_lineage_edge_validation_service_pb2.ScoreLineageEdgeRequest(
                context=request.context,
                details=lineage_v1_lineage_edge_validation_service_pb2.ScoreLineageEdgeRequest.Details(
                    destination=common_v1_address_pb2.PostalAddress(locality=request.entity.primary_address.locality)
                ),
                lineage_edge=lineage_v1_lineage_pb2.LineageEdge(
                    subject=lineage_v1_refs_pb2.ImpactRef(display_name=request.entity.relationship_manager.display_name)
                )
            )
            document_1 = MessageToJson(outgoing_1, preserving_proto_field_name=True)
            outgoing_1 = Parse(document_1, lineage_v1_lineage_edge_validation_service_pb2.ScoreLineageEdgeRequest())
            response_1 = await deps.clients.lineage_lineage_edge_validation.ScoreLineageEdge(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = metrics_v1_metric_alert_export_service_pb2.RetryMetricAlertExportRequest()
            outgoing_2.context.CopyFrom(request.context)
            outgoing_2.details.notify.email = request.entity.contact.email
            outgoing_2.metric_alert.audit.updated_at.CopyFrom(request.entity.audit.updated_at)
            outgoing_2.metric_alert.owner.display_name = request.entity.relationship_manager.display_name
            outgoing_2.metric_alert.owner.user_id = request.entity.relationship_manager.user_id
            merged_2 = metrics_v1_metric_alert_export_service_pb2.RetryMetricAlertExportRequest()
            merged_2.MergeFrom(outgoing_2)
            outgoing_2.CopyFrom(merged_2)
            response_2 = await deps.clients.metrics_metric_alert_export.RetryMetricAlertExport(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            outgoing_3 = metrics_v1_metric_alert_export_service_pb2.StreamMetricAlertExportRequest(
                context=request.context,
                filter=metrics_v1_metric_alert_export_service_pb2.StreamMetricAlertExportRequest.Filter(
                    created_after=request.entity.audit.created_at,
                    labels=dict(request.entity.attributes),
                    owner_id=response_0.result.correlation_id,
                    region=request.entity.primary_address.region
                )
            )
            async for chunk_3 in deps.clients.metrics_metric_alert_export.StreamMetricAlertExport(
                outgoing_3,
                timeout=deps.settings.timeout
            ):
                response_3 = chunk_3
            returned_0_0 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_0)
            returned_0_1 = response_0.result.status
            if returned_0_1:
                response.result.status = returned_0_1
            returned_1_0 = response_1.result.reference_ids
            response.result.reference_ids.extend(returned_1_0)
            returned_1_1 = response_1.result.correlation_id
            if returned_1_1:
                response.result.correlation_id = returned_1_1
            returned_2_0 = response_2.result.status
            if returned_2_0:
                response.result.status = returned_2_0
            echoed_0 = request.entity_id
            response.entity.entity_id = echoed_0
            echoed_1 = request.entity.name
            response.entity.contact.name.CopyFrom(echoed_1)
            return response

    async def handle_compare_entity_options(
        self,
        request: featurestore_v1_entity_calculation_service_pb2.CompareEntityOptionsRequest
    ) -> featurestore_v1_entity_calculation_service_pb2.CompareEntityOptionsResponse:
        """Compares an entity."""
        deps = self.deps
        response = featurestore_v1_entity_calculation_service_pb2.CompareEntityOptionsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CompareEntityOptions', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'CompareEntityOptions', {'reason': request.reason})
            await deps.repository.save_entity(request.context.tenant_id, request.entity)
            response_0 = lineage_v1_impact_validation_service_pb2.LintImpactsResponse()
            response_1 = featurestore_v1_feature_view_validation_service_pb2.ScoreFeatureViewResponse()
            outgoing_0 = lineage_v1_impact_validation_service_pb2.LintImpactsRequest(
                context=request.context,
                details=lineage_v1_impact_validation_service_pb2.LintImpactsRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(phone=request.entity.contact.phone)
                ),
                impact=lineage_v1_lineage_pb2.Impact(
                    customer=customers_v1_refs_pb2.CustomerRef(email=request.entity.relationship_manager.email)
                )
            )
            registered_0 = cast(
                lineage_v1_impact_validation_service_pb2_grpc.ImpactValidationServiceStub,
                deps.clients.registry['acme.lineage.v1.ImpactValidationService']
            )
            response_0 = await registered_0.LintImpacts(outgoing_0, timeout=deps.settings.timeout)
            command_1 = EntityCalculationCompareEntityOptions1Command(
                context=request.context,
                details_destination_lines=list(request.entity.primary_address.lines),
                feature_view_owner_email=response_0.impact.requester.email
            )
            outgoing_1 = to_entity_calculation_compare_entity_options1_command(command_1)
            response_1 = await deps.clients.featurestore_feature_view_validation.ScoreFeatureView(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.impact.audit.created_by
            if returned_0_0:
                response.entity.audit.created_by = returned_0_0
            returned_1_0 = response_1.feature_view.address.lines
            response.entity.primary_address.lines.extend(returned_1_0)
            echoed_0 = request.entity_id
            response.entity.entity_id = echoed_0
            echoed_1 = request.details.currency_code
            response.breakdown.currency_code = echoed_1
            return response

    async def handle_estimate_entity(
        self,
        request: featurestore_v1_entity_calculation_service_pb2.EstimateEntityRequest
    ) -> featurestore_v1_entity_calculation_service_pb2.EstimateEntityResponse:
        """Estimates an entity."""
        deps = self.deps
        response = featurestore_v1_entity_calculation_service_pb2.EstimateEntityResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('EstimateEntity', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'EstimateEntity', {'reason': request.reason})
            await deps.repository.save_entity(request.context.tenant_id, request.entity)
            response_0 = featurestore_v1_feature_view_validation_service_pb2.ScoreFeatureViewResponse()
            response_1 = boxoffice_v1_box_office_sale_query_service_pb2.ExportBoxOfficeSalesResponse()
            command_0 = EntityCalculationEstimateEntity0Command.model_validate(
                {
                    'context': request.context,
                    'feature_view_audit_updated_by': request.entity.audit.updated_by,
                    'feature_view_address_locality': request.details.destination.locality
                }
            )
            outgoing_0 = to_entity_calculation_estimate_entity0_command(command_0)
            response_0 = await deps.clients.featurestore_feature_view_validation.ScoreFeatureView(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = boxoffice_v1_box_office_sale_query_service_pb2.ExportBoxOfficeSalesRequest(
                context=request.context,
                filter=boxoffice_v1_box_office_sale_query_service_pb2.ExportBoxOfficeSalesRequest.Filter(
                    created_after=request.entity.audit.created_at,
                    region=request.entity.primary_address.region
                )
            )
            async for chunk_1 in deps.clients.boxoffice_box_office_sale_query.ExportBoxOfficeSales(
                outgoing_1,
                timeout=deps.settings.timeout
            ):
                response_1 = chunk_1
            returned_0_0 = response_0.feature_view.owner.display_name
            if returned_0_0:
                response.entity.relationship_manager.display_name = returned_0_0
            echoed_0 = request.entity_id
            response.entity.entity_id = echoed_0
            echoed_1 = request.entity.name
            response.entity.name.CopyFrom(echoed_1)
            return response

    async def handle_explain_entity_calculation(
        self,
        request: featurestore_v1_entity_calculation_service_pb2.ExplainEntityCalculationRequest
    ) -> featurestore_v1_entity_calculation_service_pb2.ExplainEntityCalculationResponse:
        """Explains an entity."""
        deps = self.deps
        response = featurestore_v1_entity_calculation_service_pb2.ExplainEntityCalculationResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ExplainEntityCalculation', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ExplainEntityCalculation',
                {'reason': request.reason}
            )
            await deps.repository.save_entity(request.context.tenant_id, request.entity)
            response_0 = lineage_v1_lineage_node_query_service_pb2.ExportLineageNodesResponse()
            response_1 = featurestore_v1_feature_value_calculation_service_pb2.QuoteFeatureValueResponse()
            response_2 = featurestore_v1_feature_view_validation_service_pb2.ScoreFeatureViewResponse()
            response_3 = fleet_v1_vehicle_service_pb2.BatchGetVehiclesResponse()
            outgoing_0 = lineage_v1_lineage_node_query_service_pb2.ExportLineageNodesRequest(
                context=request.context,
                filter=lineage_v1_lineage_node_query_service_pb2.ExportLineageNodesRequest.Filter(
                    region=request.entity.primary_address.region
                )
            )
            async for chunk_0 in deps.clients.lineage_lineage_node_query.ExportLineageNodes(
                outgoing_0,
                timeout=deps.settings.timeout
            ):
                response_0 = chunk_0
            outgoing_1 = featurestore_v1_feature_value_calculation_service_pb2.QuoteFeatureValueRequest()
            outgoing_1.context.CopyFrom(request.context)
            outgoing_1.details.destination.country_code = request.entity.primary_address.country_code
            outgoing_1.details.destination.region = request.entity.primary_address.region
            outgoing_1.details.destination.postal_code = request.entity.primary_address.postal_code
            outgoing_1.details.destination.lines.extend(list(request.entity.primary_address.lines))
            outgoing_1.context.tenant_id = tenant_id.get()
            response_1 = await deps.clients.featurestore_feature_value_calculation.QuoteFeatureValue(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = featurestore_v1_feature_view_validation_service_pb2.ScoreFeatureViewRequest(
                context=request.context,
                details=featurestore_v1_feature_view_validation_service_pb2.ScoreFeatureViewRequest.Details(
                    destination=common_v1_address_pb2.PostalAddress(lines=list(request.entity.primary_address.lines))
                ),
                feature_view=featurestore_v1_featurestore_pb2.FeatureView(
                    address=common_v1_address_pb2.PostalAddress(
                        postal_code=request.entity.primary_address.postal_code,
                        region=request.entity.primary_address.region
                    ),
                    audit=common_v1_audit_pb2.AuditInfo(created_by=request.entity.audit.created_by)
                )
            )
            port_2: EntityCalculationExplainEntityCalculation2Port = EntityCalculationExplainEntityCalculation2Adapter(
                deps.clients.featurestore_feature_view_validation,
                deps.settings.timeout
            )
            response_2 = await port_2.execute(outgoing_2)
            outgoing_3 = fleet_v1_vehicle_service_pb2.BatchGetVehiclesRequest(context=request.context)
            steps_3 = [partial(deps.clients.fleet_vehicle.BatchGetVehicles, outgoing_3, timeout=deps.settings.timeout)]
            results_3 = await run_steps(steps_3)
            response_3 = results_3[-1]
            returned_1_0 = response_1.result.details
            response.result.details.update(returned_1_0)
            returned_2_0 = response_2.result.message
            if returned_2_0:
                response.outcome.message = returned_2_0
            returned_3_0 = response_3.result.message
            if returned_3_0:
                response.outcome.message = returned_3_0
            returned_3_1 = response_3.result.status
            if returned_3_1:
                response.result.status = returned_3_1
            echoed_0 = request.entity_id
            response.entity.entity_id = echoed_0
            echoed_1 = request.entity.name
            response.entity.name.CopyFrom(echoed_1)
            return response

    async def handle_get_entity_rates(
        self,
        request: featurestore_v1_entity_calculation_service_pb2.GetEntityRatesRequest
    ) -> featurestore_v1_entity_calculation_service_pb2.GetEntityRatesResponse:
        """Returns an entity."""
        deps = self.deps
        response = featurestore_v1_entity_calculation_service_pb2.GetEntityRatesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('GetEntityRates', extra={'fields': {'domain': 'featurestore'}})
            await deps.repository.audit(request.context.tenant_id, 'GetEntityRates', {})
            response_0 = broadcasts_v1_broadcast_service_pb2.BatchGetBroadcastsResponse()
            outgoing_0 = broadcasts_v1_broadcast_service_pb2.BatchGetBroadcastsRequest(context=request.context)
            response_0 = await deps.clients.broadcasts_broadcast.BatchGetBroadcasts(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.result.message = returned_0_0
            echoed_0 = request.entity_id
            response.entity.entity_id = echoed_0
            return response

    async def handle_quote_entity(
        self,
        request: featurestore_v1_entity_calculation_service_pb2.QuoteEntityRequest
    ) -> featurestore_v1_entity_calculation_service_pb2.QuoteEntityResponse:
        """Quotes an entity."""
        deps = self.deps
        response = featurestore_v1_entity_calculation_service_pb2.QuoteEntityResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('QuoteEntity', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'QuoteEntity', {'reason': request.reason})
            await deps.repository.save_entity(request.context.tenant_id, request.entity)
            response_0 = featurestore_v1_feature_view_validation_service_pb2.ValidateFeatureViewResponse()
            outgoing_0 = featurestore_v1_feature_view_validation_service_pb2.ValidateFeatureViewRequest(
                context=request.context,
                feature_view=featurestore_v1_featurestore_pb2.FeatureView(
                    address=common_v1_address_pb2.PostalAddress(
                        country_code=request.entity.primary_address.country_code,
                        lines=list(request.entity.primary_address.lines)
                    ),
                    audit=common_v1_audit_pb2.AuditInfo(created_at=request.entity.audit.created_at),
                    owner=identity_v1_refs_pb2.UserRef(email=request.entity.contact.email)
                )
            )
            response_0 = cast(featurestore_v1_feature_view_validation_service_pb2.ValidateFeatureViewResponse, await deps.bus.request(
                'acme.featurestore.v1.EntityCalculationService/QuoteEntity/0', outgoing_0, deps.settings.timeout,
            ))
            returned_0_0 = response_0.feature_view.audit.etag
            if returned_0_0:
                response.entity.audit.etag = returned_0_0
            echoed_0 = request.entity_id
            response.entity.entity_id = echoed_0
            echoed_1 = request.entity.status
            response.entity.status = echoed_1
            return response
