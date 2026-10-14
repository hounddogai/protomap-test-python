"""Reusable transport mixin for FeatureViewCalculationService."""

from __future__ import annotations

from collections.abc import AsyncIterator
from functools import partial
from typing import cast
import asyncio
import logging

from google.protobuf.json_format import MessageToJson
from google.protobuf.json_format import Parse
import grpc

from acme.anomalies.v1 import detector_validation_service_pb2 as anomalies_v1_detector_validation_service_pb2
from acme.audit.v1 import audit_event_query_service_pb2 as audit_v1_audit_event_query_service_pb2
from acme.boxoffice.v1 import box_office_sale_service_pb2 as boxoffice_v1_box_office_sale_service_pb2
from acme.certificates.v1 import (
    certificate_calculation_service_pb2 as certificates_v1_certificate_calculation_service_pb2,
)
from acme.certificates.v1 import certificates_pb2 as certificates_v1_certificates_pb2
from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.concessions.v1 import (
    concession_stand_calculation_service_pb2 as concessions_v1_concession_stand_calculation_service_pb2,
)
from acme.concessions.v1 import concessions_pb2 as concessions_v1_concessions_pb2
from acme.customers.v1 import refs_pb2 as customers_v1_refs_pb2
from acme.drivers.v1 import driver_query_service_pb2 as drivers_v1_driver_query_service_pb2
from acme.featurestore.v1 import (
    feature_view_calculation_service_pb2 as featurestore_v1_feature_view_calculation_service_pb2,
)
from acme.featurestore.v1 import featurestore_pb2 as featurestore_v1_featurestore_pb2
from acme.identity.v1 import identity_pb2 as identity_v1_identity_pb2
from acme.identity.v1 import user_validation_service_pb2 as identity_v1_user_validation_service_pb2
from acme.lineage.v1 import impact_validation_service_pb2 as lineage_v1_impact_validation_service_pb2
from acme.lineage.v1 import lineage_node_query_service_pb2 as lineage_v1_lineage_node_query_service_pb2
from acme.lineage.v1 import lineage_node_service_pb2 as lineage_v1_lineage_node_service_pb2
from acme.lineage.v1 import lineage_pb2 as lineage_v1_lineage_pb2
from acme.metrics.v1 import dashboard_export_service_pb2 as metrics_v1_dashboard_export_service_pb2
from acme.metrics.v1 import dashboard_notification_service_pb2 as metrics_v1_dashboard_notification_service_pb2
from acme.metrics.v1 import metric_series_service_pb2 as metrics_v1_metric_series_service_pb2

from acme_data.domains.featurestore import hooks
from acme_data.domains.featurestore.adapters import FeatureViewCalculationCalculateFeatureView0Adapter
from acme_data.domains.featurestore.adapters import FeatureViewCalculationCalculateFeatureView0Port
from acme_data.domains.featurestore.dependencies import Dependencies
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import run_steps
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_id
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class FeatureViewCalculationServicerHandlers:
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    async def CalculateFeatureView(
        self, request: featurestore_v1_feature_view_calculation_service_pb2.CalculateFeatureViewRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_feature_view_calculation_service_pb2.CalculateFeatureViewResponse:
        """Calculates a feature view."""
        return await self.handle_calculate_feature_view(request)

    @rpc_errors
    async def CompareFeatureViewOptions(
        self, request: featurestore_v1_feature_view_calculation_service_pb2.CompareFeatureViewOptionsRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_feature_view_calculation_service_pb2.CompareFeatureViewOptionsResponse:
        """Compares a feature view."""
        return await self.handle_compare_feature_view_options(request)

    @rpc_errors
    async def EstimateFeatureView(
        self, request: featurestore_v1_feature_view_calculation_service_pb2.EstimateFeatureViewRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_feature_view_calculation_service_pb2.EstimateFeatureViewResponse:
        """Estimates a feature view."""
        return await self.handle_estimate_feature_view(request)

    @rpc_errors
    async def ExplainFeatureViewCalculation(
        self, request: featurestore_v1_feature_view_calculation_service_pb2.ExplainFeatureViewCalculationRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_feature_view_calculation_service_pb2.ExplainFeatureViewCalculationResponse:
        """Explains a feature view."""
        return await self.handle_explain_feature_view_calculation(request)

    @rpc_errors
    @retry_transient
    async def GetFeatureViewRates(
        self, request: featurestore_v1_feature_view_calculation_service_pb2.GetFeatureViewRatesRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_feature_view_calculation_service_pb2.GetFeatureViewRatesResponse:
        """Returns a feature view."""
        return await self.handle_get_feature_view_rates(request)

    @rpc_errors
    async def QuoteFeatureView(
        self, request: featurestore_v1_feature_view_calculation_service_pb2.QuoteFeatureViewRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_feature_view_calculation_service_pb2.QuoteFeatureViewResponse:
        """Quotes a feature view."""
        return await self.handle_quote_feature_view(request)

    @rpc_errors
    async def RecalculateFeatureViews(
        self, request: featurestore_v1_feature_view_calculation_service_pb2.RecalculateFeatureViewsRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_feature_view_calculation_service_pb2.RecalculateFeatureViewsResponse:
        """Recalculates a feature view."""
        return await self.handle_recalculate_feature_views(request)

    @rpc_errors
    async def SimulateFeatureView(
        self, request: featurestore_v1_feature_view_calculation_service_pb2.SimulateFeatureViewRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_feature_view_calculation_service_pb2.SimulateFeatureViewResponse:
        """Simulates a feature view."""
        return await self.handle_simulate_feature_view(request)

    async def handle_calculate_feature_view(
        self,
        request: featurestore_v1_feature_view_calculation_service_pb2.CalculateFeatureViewRequest
    ) -> featurestore_v1_feature_view_calculation_service_pb2.CalculateFeatureViewResponse:
        """Calculates a feature view."""
        deps = self.deps
        response = featurestore_v1_feature_view_calculation_service_pb2.CalculateFeatureViewResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CalculateFeatureView', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'CalculateFeatureView', {'reason': request.reason})
            await deps.repository.save_feature_view(request.context.tenant_id, request.feature_view)
            response_0 = certificates_v1_certificate_calculation_service_pb2.CompareCertificateOptionsResponse()
            response_1 = concessions_v1_concession_stand_calculation_service_pb2.CompareConcessionStandOptionsResponse()
            response_2 = boxoffice_v1_box_office_sale_service_pb2.SearchBoxOfficeSalesResponse()
            outgoing_0 = certificates_v1_certificate_calculation_service_pb2.CompareCertificateOptionsRequest(
                certificate=certificates_v1_certificates_pb2.Certificate(
                    billing_address=common_v1_address_pb2.PostalAddress(recipient=request.details.destination.recipient)
                ),
                context=request.context,
                details=certificates_v1_certificate_calculation_service_pb2.CompareCertificateOptionsRequest.Details(
                    destination=common_v1_address_pb2.PostalAddress(
                        country_code=request.feature_view.address.country_code,
                        lines=list(request.feature_view.address.lines),
                        locality=request.details.destination.locality
                    )
                )
            )
            port_0: FeatureViewCalculationCalculateFeatureView0Port = FeatureViewCalculationCalculateFeatureView0Adapter(
                deps.clients.certificates_certificate_calculation,
                deps.settings.timeout
            )
            response_0 = await port_0.execute(outgoing_0)
            outgoing_1 = concessions_v1_concession_stand_calculation_service_pb2.CompareConcessionStandOptionsRequest(
                concession_stand=concessions_v1_concessions_pb2.ConcessionStand(
                    address=common_v1_address_pb2.PostalAddress(recipient=request.feature_view.address.recipient),
                    audit=common_v1_audit_pb2.AuditInfo(etag=response_0.certificate.audit.etag)
                ),
                context=request.context,
                details=concessions_v1_concession_stand_calculation_service_pb2.CompareConcessionStandOptionsRequest.Details(
                    destination=common_v1_address_pb2.PostalAddress(region=request.feature_view.address.region)
                )
            )
            steps_1 = [
                partial(
                    deps.clients.concessions_concession_stand_calculation.CompareConcessionStandOptions,
                    outgoing_1,
                    timeout=deps.settings.timeout
                )
            ]
            results_1 = await run_steps(steps_1)
            response_1 = results_1[-1]
            outgoing_2 = boxoffice_v1_box_office_sale_service_pb2.SearchBoxOfficeSalesRequest()
            outgoing_2.context.CopyFrom(request.context)
            if request.feature_view.WhichOneof('locator') == 'address':
                outgoing_2.filter.region = request.feature_view.address.region
            outgoing_2.filter.created_after.CopyFrom(response_1.concession_stand.audit.created_at)
            response_2 = await deps.clients.boxoffice_box_office_sale.SearchBoxOfficeSales(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.certificate.audit.created_at
            if returned_0_0.ListFields():
                response.feature_view.audit.created_at.MergeFrom(returned_0_0)
            returned_0_1 = response_0.certificate.total
            if returned_0_1.ListFields():
                response.breakdown.total.MergeFrom(returned_0_1)
            returned_1_0 = response_1.result.correlation_id
            if returned_1_0:
                response.result.correlation_id = returned_1_0
            returned_1_1 = response_1.concession_stand.dimensions.unit
            if returned_1_1:
                response.feature_view.dimensions.unit = returned_1_1
            returned_2_0 = response_2.result.reference_ids
            response.result.reference_ids.extend(returned_2_0)
            returned_2_1 = response_2.result.correlation_id
            if returned_2_1:
                response.result.correlation_id = returned_2_1
            echoed_0 = request.feature_view_id
            response.feature_view.feature_view_id = echoed_0
            echoed_1 = request.details.currency_code
            response.breakdown.currency_code = echoed_1
            return response

    async def handle_compare_feature_view_options(
        self,
        request: featurestore_v1_feature_view_calculation_service_pb2.CompareFeatureViewOptionsRequest
    ) -> featurestore_v1_feature_view_calculation_service_pb2.CompareFeatureViewOptionsResponse:
        """Compares a feature view."""
        deps = self.deps
        response = featurestore_v1_feature_view_calculation_service_pb2.CompareFeatureViewOptionsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CompareFeatureViewOptions', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'CompareFeatureViewOptions',
                {'reason': request.reason}
            )
            await deps.repository.save_feature_view(request.context.tenant_id, request.feature_view)
            response_0 = lineage_v1_lineage_node_query_service_pb2.CountLineageNodesResponse()
            response_1 = lineage_v1_lineage_node_service_pb2.UpdateLineageNodeResponse()
            outgoing_0 = lineage_v1_lineage_node_query_service_pb2.CountLineageNodesRequest(
                context=request.context,
                filter=lineage_v1_lineage_node_query_service_pb2.CountLineageNodesRequest.Filter(
                    created_after=request.feature_view.audit.updated_at,
                    labels=dict(request.feature_view.specs),
                    owner_id=request.feature_view.owner.user_id,
                    region=request.details.destination.region
                )
            )
            response_0 = cast(lineage_v1_lineage_node_query_service_pb2.CountLineageNodesResponse, await deps.bus.request(
                'acme.featurestore.v1.FeatureViewCalculationService/CompareFeatureViewOptions/0', outgoing_0, deps.settings.timeout,
            ))
            outgoing_1 = lineage_v1_lineage_node_service_pb2.UpdateLineageNodeRequest(
                context=request.context,
                lineage_node=lineage_v1_lineage_pb2.LineageNode(
                    children=[
                        lineage_v1_lineage_pb2.LineageNode(
                            children=[
                                lineage_v1_lineage_pb2.LineageNode(
                                    audit=common_v1_audit_pb2.AuditInfo(
                                        created_at=request.feature_view.audit.created_at
                                    ),
                                    location=common_v1_address_pb2.PostalAddress(
                                        lines=list(request.details.destination.lines)
                                    )
                                )
                            ]
                        )
                    ]
                )
            )
            response_1 = await deps.clients.lineage_lineage_node.UpdateLineageNode(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_0)
            returned_1_0 = response_1.result.details
            response.result.details.update(returned_1_0)
            echoed_0 = request.feature_view_id
            response.feature_view.feature_view_id = echoed_0
            echoed_1 = request.feature_view.owner
            response.feature_view.owner.CopyFrom(echoed_1)
            return response

    async def handle_estimate_feature_view(
        self,
        request: featurestore_v1_feature_view_calculation_service_pb2.EstimateFeatureViewRequest
    ) -> featurestore_v1_feature_view_calculation_service_pb2.EstimateFeatureViewResponse:
        """Estimates a feature view."""
        deps = self.deps
        response = featurestore_v1_feature_view_calculation_service_pb2.EstimateFeatureViewResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('EstimateFeatureView', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'EstimateFeatureView', {'reason': request.reason})
            await deps.repository.save_feature_view(request.context.tenant_id, request.feature_view)
            response_0 = audit_v1_audit_event_query_service_pb2.ResolveAuditEventsResponse()
            outgoing_0 = audit_v1_audit_event_query_service_pb2.ResolveAuditEventsRequest(context=request.context)
            method_name_0 = 'ResolveAuditEvents'
            response_0 = await getattr(
                deps.clients.audit_audit_event_query,
                method_name_0
            )(outgoing_0, timeout=deps.settings.timeout)
            returned_0_0 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_0)
            echoed_0 = request.feature_view_id
            response.feature_view.feature_view_id = echoed_0
            echoed_1 = request.feature_view.specs
            response.feature_view.specs.update(echoed_1)
            return response

    async def handle_explain_feature_view_calculation(
        self,
        request: featurestore_v1_feature_view_calculation_service_pb2.ExplainFeatureViewCalculationRequest
    ) -> featurestore_v1_feature_view_calculation_service_pb2.ExplainFeatureViewCalculationResponse:
        """Explains a feature view."""
        deps = self.deps
        response = featurestore_v1_feature_view_calculation_service_pb2.ExplainFeatureViewCalculationResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ExplainFeatureViewCalculation', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ExplainFeatureViewCalculation',
                {'reason': request.reason}
            )
            await deps.repository.save_feature_view(request.context.tenant_id, request.feature_view)
            response_0 = metrics_v1_dashboard_notification_service_pb2.StreamDashboardNoticesResponse()
            response_1 = metrics_v1_metric_series_service_pb2.WatchMetricSeriesesResponse()
            response_2 = lineage_v1_impact_validation_service_pb2.CheckImpactEligibilityResponse()
            response_3 = drivers_v1_driver_query_service_pb2.CountDriversResponse()
            outgoing_0 = metrics_v1_dashboard_notification_service_pb2.StreamDashboardNoticesRequest(
                context=request.context,
                filter=metrics_v1_dashboard_notification_service_pb2.StreamDashboardNoticesRequest.Filter(
                    region=request.feature_view.address.region
                ),
                subscriber=common_v1_contact_pb2.ContactInfo(
                    phone=request.details.contact.phone,
                    preferred_channel=request.details.contact.preferred_channel
                )
            )
            async for chunk_0 in deps.clients.metrics_dashboard_notification.StreamDashboardNotices(
                outgoing_0,
                timeout=deps.settings.timeout
            ):
                response_0 = chunk_0
            outgoing_1 = metrics_v1_metric_series_service_pb2.WatchMetricSeriesesRequest(
                context=request.context,
                filter=metrics_v1_metric_series_service_pb2.WatchMetricSeriesesRequest.Filter(
                    region=request.feature_view.address.region
                ),
                subscriber=common_v1_contact_pb2.ContactInfo(
                    email=request.feature_view.owner.email,
                    phone=request.details.contact.phone,
                    preferred_channel=request.details.contact.preferred_channel
                )
            )
            async for chunk_1 in deps.clients.metrics_metric_series.WatchMetricSerieses(
                outgoing_1,
                timeout=deps.settings.timeout
            ):
                response_1 = chunk_1
            outgoing_2 = lineage_v1_impact_validation_service_pb2.CheckImpactEligibilityRequest(
                context=request.context,
                impact=lineage_v1_lineage_pb2.Impact(
                    customer=customers_v1_refs_pb2.CustomerRef(display_name=request.feature_view.owner.display_name)
                )
            )
            document_2 = MessageToJson(outgoing_2, preserving_proto_field_name=True)
            outgoing_2 = Parse(document_2, lineage_v1_impact_validation_service_pb2.CheckImpactEligibilityRequest())
            response_2 = await deps.clients.lineage_impact_validation.CheckImpactEligibility(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            outgoing_3 = drivers_v1_driver_query_service_pb2.CountDriversRequest()
            outgoing_3.context.CopyFrom(request.context)
            outgoing_3.filter.region = request.feature_view.address.region
            outgoing_3.filter.created_after.CopyFrom(response_2.impact.audit.updated_at)
            outgoing_3.filter.owner_id = request.feature_view.components.get(
                'primary',
                featurestore_v1_featurestore_pb2.FeatureViewComponent()
            ).component_id
            outgoing_3.filter.labels.update(dict(response_2.impact.custom_fields))
            merged_3 = drivers_v1_driver_query_service_pb2.CountDriversRequest()
            merged_3.MergeFrom(outgoing_3)
            outgoing_3.CopyFrom(merged_3)
            response_3 = await deps.clients.drivers_driver_query.CountDrivers(outgoing_3, timeout=deps.settings.timeout)
            returned_2_0 = response_2.outcome.next_steps
            response.outcome.next_steps.extend(returned_2_0)
            returned_2_1 = response_2.outcome.status
            if returned_2_1:
                response.result.status = returned_2_1
            returned_3_0 = response_3.result.correlation_id
            if returned_3_0:
                response.result.correlation_id = returned_3_0
            returned_3_1 = response_3.result.message
            if returned_3_1:
                response.outcome.message = returned_3_1
            echoed_0 = request.feature_view_id
            response.feature_view.feature_view_id = echoed_0
            echoed_1 = request.feature_view.specs
            response.feature_view.specs.update(echoed_1)
            return response

    async def handle_get_feature_view_rates(
        self,
        request: featurestore_v1_feature_view_calculation_service_pb2.GetFeatureViewRatesRequest
    ) -> featurestore_v1_feature_view_calculation_service_pb2.GetFeatureViewRatesResponse:
        """Returns a feature view."""
        deps = self.deps
        response = featurestore_v1_feature_view_calculation_service_pb2.GetFeatureViewRatesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('GetFeatureViewRates', extra={'fields': {'locale': request.context.locale}})
            await deps.repository.audit(
                request.context.tenant_id,
                'GetFeatureViewRates',
                {'locale': request.context.locale}
            )
            echoed_0 = request.feature_view_id
            response.feature_view.feature_view_id = echoed_0
            return response

    async def handle_quote_feature_view(
        self,
        request: featurestore_v1_feature_view_calculation_service_pb2.QuoteFeatureViewRequest
    ) -> featurestore_v1_feature_view_calculation_service_pb2.QuoteFeatureViewResponse:
        """Quotes a feature view."""
        deps = self.deps
        response = featurestore_v1_feature_view_calculation_service_pb2.QuoteFeatureViewResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('QuoteFeatureView', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'QuoteFeatureView', {'reason': request.reason})
            await deps.repository.save_feature_view(request.context.tenant_id, request.feature_view)
            response_0 = audit_v1_audit_event_query_service_pb2.ResolveAuditEventsResponse()
            response_1 = audit_v1_audit_event_query_service_pb2.CountAuditEventsResponse()
            response_2 = identity_v1_user_validation_service_pb2.ScoreUserResponse()
            outgoing_0 = audit_v1_audit_event_query_service_pb2.ResolveAuditEventsRequest(context=request.context)
            outgoing_1 = audit_v1_audit_event_query_service_pb2.CountAuditEventsRequest(
                context=request.context,
                filter=audit_v1_audit_event_query_service_pb2.CountAuditEventsRequest.Filter(
                    created_after=request.feature_view.audit.updated_at,
                    labels=dict(request.feature_view.specs),
                    region=request.details.destination.region
                )
            )
            outgoing_2 = identity_v1_user_validation_service_pb2.ScoreUserRequest(
                context=request.context,
                user=identity_v1_identity_pb2.User(
                    primary_address=common_v1_address_pb2.PostalAddress(
                        postal_code=request.details.destination.postal_code
                    )
                )
            )
            response_0, response_1, response_2 = await asyncio.gather(
                deps.clients.audit_audit_event_query.ResolveAuditEvents(outgoing_0, timeout=deps.settings.timeout),
                deps.clients.audit_audit_event_query.CountAuditEvents(outgoing_1, timeout=deps.settings.timeout),
                deps.clients.identity_user_validation.ScoreUser(outgoing_2, timeout=deps.settings.timeout),
            )
            returned_0_0 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_0)
            returned_1_0 = response_1.result.correlation_id
            if returned_1_0:
                response.result.correlation_id = returned_1_0
            returned_1_1 = response_1.result.reference_ids
            response.result.reference_ids.extend(returned_1_1)
            returned_2_0 = response_2.user.audit.updated_at
            if returned_2_0.ListFields():
                response.feature_view.audit.updated_at.MergeFrom(returned_2_0)
            returned_2_1 = response_2.user.audit.created_by
            if returned_2_1:
                response.feature_view.audit.created_by = returned_2_1
            echoed_0 = request.feature_view_id
            response.feature_view.feature_view_id = echoed_0
            echoed_1 = request.feature_view.capacity
            response.feature_view.capacity = echoed_1
            return response

    async def handle_recalculate_feature_views(
        self,
        request: featurestore_v1_feature_view_calculation_service_pb2.RecalculateFeatureViewsRequest
    ) -> featurestore_v1_feature_view_calculation_service_pb2.RecalculateFeatureViewsResponse:
        """Recalculates a feature view."""
        deps = self.deps
        response = featurestore_v1_feature_view_calculation_service_pb2.RecalculateFeatureViewsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info(
                'RecalculateFeatureViews',
                extra={'fields': {'include_breakdown': request.details.include_breakdown}}
            )
            await deps.repository.audit(
                request.context.tenant_id,
                'RecalculateFeatureViews',
                {'include_breakdown': request.details.include_breakdown}
            )
            await deps.repository.save_feature_view(request.context.tenant_id, request.feature_view)
            response_0 = lineage_v1_lineage_node_query_service_pb2.ExportLineageNodesResponse()
            response_1 = metrics_v1_dashboard_export_service_pb2.ShareDashboardExportResponse()
            outgoing_0 = lineage_v1_lineage_node_query_service_pb2.ExportLineageNodesRequest(
                context=request.context,
                filter=lineage_v1_lineage_node_query_service_pb2.ExportLineageNodesRequest.Filter(
                    created_after=request.feature_view.audit.created_at,
                    region=request.feature_view.address.region
                )
            )
            async for chunk_0 in deps.clients.lineage_lineage_node_query.ExportLineageNodes(
                outgoing_0,
                timeout=deps.settings.timeout
            ):
                response_0 = chunk_0
            outgoing_1 = metrics_v1_dashboard_export_service_pb2.ShareDashboardExportRequest(
                annotations=dict(request.annotations),
                context=request.context,
                details=metrics_v1_dashboard_export_service_pb2.ShareDashboardExportRequest.Details(
                    recipient=common_v1_contact_pb2.ContactInfo(email=request.feature_view.owner.email)
                ),
                reason=request.reason
            )
            send_1 = partial(deps.clients.metrics_dashboard_export.ShareDashboardExport, timeout=deps.settings.timeout)
            response_1 = await send_1(outgoing_1)
            returned_1_0 = response_1.outcome.message
            if returned_1_0:
                response.result.message = returned_1_0
            echoed_0 = request.feature_view_id
            response.feature_view.feature_view_id = echoed_0
            echoed_1 = request.details.currency_code
            response.breakdown.currency_code = echoed_1
            return response

    async def handle_simulate_feature_view(
        self,
        request: featurestore_v1_feature_view_calculation_service_pb2.SimulateFeatureViewRequest
    ) -> featurestore_v1_feature_view_calculation_service_pb2.SimulateFeatureViewResponse:
        """Simulates a feature view."""
        deps = self.deps
        response = featurestore_v1_feature_view_calculation_service_pb2.SimulateFeatureViewResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SimulateFeatureView', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'SimulateFeatureView', {'reason': request.reason})
            await deps.repository.save_feature_view(request.context.tenant_id, request.feature_view)
            response_0 = identity_v1_user_validation_service_pb2.GetUserRulesResponse()
            response_1 = anomalies_v1_detector_validation_service_pb2.LintDetectorsResponse()
            outgoing_0 = identity_v1_user_validation_service_pb2.GetUserRulesRequest(
                context=request.context,
                user_id=request.feature_view.owner.user_id
            )
            response_0 = await hooks.feature_view_calculation_simulate_feature_view0(
                deps.clients.identity_user_validation,
                outgoing_0,
                deps.settings.timeout
            )
            outgoing_1 = anomalies_v1_detector_validation_service_pb2.LintDetectorsRequest()
            outgoing_1.context.CopyFrom(request.context)
            outgoing_1.detector.audit.created_at.CopyFrom(response_0.user.audit.created_at)
            outgoing_1.details.contact.preferred_channel = response_0.user.contact.preferred_channel
            outgoing_1.context.tenant_id = tenant_id.get()
            response_1 = await deps.clients.anomalies_detector_validation.LintDetectors(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.user.relationship_manager.user_id
            if returned_0_0:
                response.feature_view.owner.user_id = returned_0_0
            returned_0_1 = response_0.user.contact.email
            if returned_0_1:
                response.feature_view.owner.email = returned_0_1
            returned_1_0 = response_1.result.reference_ids
            response.result.reference_ids.extend(returned_1_0)
            returned_1_1 = response_1.detector.audit.updated_by
            if returned_1_1:
                response.feature_view.audit.updated_by = returned_1_1
            echoed_0 = request.feature_view_id
            response.feature_view.feature_view_id = echoed_0
            echoed_1 = request.feature_view.capacity
            response.feature_view.capacity = echoed_1
            return response
