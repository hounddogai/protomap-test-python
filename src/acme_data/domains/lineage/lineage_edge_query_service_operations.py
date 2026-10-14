"""Functional operations behind LineageEdgeQueryService."""

from __future__ import annotations

from functools import partial
from typing import cast
import logging

from acme.certificates.v1 import (
    certificate_calculation_service_pb2 as certificates_v1_certificate_calculation_service_pb2,
)
from acme.certificates.v1 import certificates_pb2 as certificates_v1_certificates_pb2
from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.customers.v1 import refs_pb2 as customers_v1_refs_pb2
from acme.featureflags.v1 import (
    feature_flag_validation_service_pb2 as featureflags_v1_feature_flag_validation_service_pb2,
)
from acme.featureflags.v1 import featureflags_pb2 as featureflags_v1_featureflags_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.lineage.v1 import impact_calculation_service_pb2 as lineage_v1_impact_calculation_service_pb2
from acme.lineage.v1 import impact_validation_service_pb2 as lineage_v1_impact_validation_service_pb2
from acme.lineage.v1 import lineage_edge_query_service_pb2 as lineage_v1_lineage_edge_query_service_pb2
from acme.lineage.v1 import lineage_node_calculation_service_pb2 as lineage_v1_lineage_node_calculation_service_pb2
from acme.lineage.v1 import lineage_node_query_service_pb2 as lineage_v1_lineage_node_query_service_pb2
from acme.lineage.v1 import lineage_pb2 as lineage_v1_lineage_pb2
from acme.metrics.v1 import dashboard_sync_service_pb2 as metrics_v1_dashboard_sync_service_pb2
from acme.metrics.v1 import metric_alert_history_service_pb2 as metrics_v1_metric_alert_history_service_pb2
from acme.metrics.v1 import metric_series_export_service_pb2 as metrics_v1_metric_series_export_service_pb2
from acme.metrics.v1 import metric_series_export_service_pb2_grpc as metrics_v1_metric_series_export_service_pb2_grpc
from acme.metrics.v1 import metrics_pb2 as metrics_v1_metrics_pb2

from acme_data.domains.lineage.adapters import LineageEdgeQuerySummarizeLineageEdges2Adapter
from acme_data.domains.lineage.dependencies import Dependencies
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import run_steps
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


async def handle_browse_lineage_edges(
    deps: Dependencies,
    request: lineage_v1_lineage_edge_query_service_pb2.BrowseLineageEdgesRequest
) -> lineage_v1_lineage_edge_query_service_pb2.BrowseLineageEdgesResponse:
    """Lists lineage edges a page at a time."""
    response = lineage_v1_lineage_edge_query_service_pb2.BrowseLineageEdgesResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('BrowseLineageEdges', extra={'fields': {'order_by': request.order_by}})
        await deps.repository.audit(request.context.tenant_id, 'BrowseLineageEdges', {'order_by': request.order_by})
        response_0 = lineage_v1_lineage_node_calculation_service_pb2.EstimateLineageNodeResponse()
        response_1 = metrics_v1_metric_series_export_service_pb2.RetryMetricSeriesExportResponse()
        outgoing_0 = lineage_v1_lineage_node_calculation_service_pb2.EstimateLineageNodeRequest(
            context=request.context,
            lineage_node=lineage_v1_lineage_pb2.LineageNode(
                children=[
                    lineage_v1_lineage_pb2.LineageNode(
                        children=[
                            lineage_v1_lineage_pb2.LineageNode(
                                location=common_v1_address_pb2.PostalAddress(region=request.filter.region)
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
        outgoing_1 = metrics_v1_metric_series_export_service_pb2.RetryMetricSeriesExportRequest(
            context=request.context,
            metric_series=metrics_v1_metrics_pb2.MetricSeries(
                audit=common_v1_audit_pb2.AuditInfo(created_at=response_0.lineage_node.audit.created_at)
            )
        )
        registered_1 = cast(
            metrics_v1_metric_series_export_service_pb2_grpc.MetricSeriesExportServiceStub,
            deps.clients.registry['acme.metrics.v1.MetricSeriesExportService']
        )
        response_1 = await registered_1.RetryMetricSeriesExport(outgoing_1, timeout=deps.settings.timeout)
        returned_0_0 = response_0.result.correlation_id
        if returned_0_0:
            response.result.correlation_id = returned_0_0
        returned_0_1 = response_0.lineage_node.attributes
        returned_0_1_part_0 = response.lineage_edges.add()
        returned_0_1_part_0.attributes.update(returned_0_1)
        returned_1_0 = response_1.result.correlation_id
        if returned_1_0:
            response.result.correlation_id = returned_1_0
        returned_1_1 = response_1.result.correlation_id
        returned_1_1_part_0 = response.lineage_edges.add()
        if returned_1_1:
            returned_1_1_part_0.correlation_id = returned_1_1
        return response


async def handle_count_lineage_edges(
    deps: Dependencies,
    request: lineage_v1_lineage_edge_query_service_pb2.CountLineageEdgesRequest
) -> lineage_v1_lineage_edge_query_service_pb2.CountLineageEdgesResponse:
    """Counts lineage edges by status."""
    response = lineage_v1_lineage_edge_query_service_pb2.CountLineageEdgesResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('CountLineageEdges', extra={'fields': {'order_by': request.order_by}})
        await deps.repository.audit(request.context.tenant_id, 'CountLineageEdges', {'order_by': request.order_by})
        response_0 = lineage_v1_impact_validation_service_pb2.ValidateImpactResponse()
        outgoing_0 = lineage_v1_impact_validation_service_pb2.ValidateImpactRequest(
            context=request.context,
            impact=lineage_v1_lineage_pb2.Impact(
                assignee=identity_v1_refs_pb2.UserRef(user_id=request.context.actor.user_id),
                customer=customers_v1_refs_pb2.CustomerRef(email=request.context.actor.email)
            )
        )
        response_0 = await deps.clients.lineage_impact_validation.ValidateImpact(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.result.status
        if returned_0_0:
            response.result.status = returned_0_0
        return response


async def handle_find_lineage_edges(
    deps: Dependencies,
    request: lineage_v1_lineage_edge_query_service_pb2.FindLineageEdgesRequest
) -> lineage_v1_lineage_edge_query_service_pb2.FindLineageEdgesResponse:
    """Lists lineage edges a page at a time."""
    response = lineage_v1_lineage_edge_query_service_pb2.FindLineageEdgesResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('FindLineageEdges', extra={'fields': {'order_by': request.order_by}})
        await deps.repository.audit(request.context.tenant_id, 'FindLineageEdges', {'order_by': request.order_by})
        return response


async def handle_lookup_lineage_edge(
    deps: Dependencies,
    request: lineage_v1_lineage_edge_query_service_pb2.LookupLineageEdgeRequest
) -> lineage_v1_lineage_edge_query_service_pb2.LookupLineageEdgeResponse:
    """Returns a lineage edge."""
    response = lineage_v1_lineage_edge_query_service_pb2.LookupLineageEdgeResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('LookupLineageEdge', extra={'fields': {'locale': request.context.locale}})
        await deps.repository.audit(request.context.tenant_id, 'LookupLineageEdge', {'locale': request.context.locale})
        echoed_0 = request.lineage_edge_id
        response.lineage_edge.lineage_edge_id = echoed_0
        return response


async def handle_peek_lineage_edge(
    deps: Dependencies,
    request: lineage_v1_lineage_edge_query_service_pb2.PeekLineageEdgeRequest
) -> lineage_v1_lineage_edge_query_service_pb2.PeekLineageEdgeResponse:
    """Returns a lineage edge."""
    response = lineage_v1_lineage_edge_query_service_pb2.PeekLineageEdgeResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('PeekLineageEdge', extra={'fields': {'domain': 'lineage'}})
        await deps.repository.audit(request.context.tenant_id, 'PeekLineageEdge', {})
        response_0 = lineage_v1_impact_validation_service_pb2.LintImpactsResponse()
        response_1 = lineage_v1_impact_calculation_service_pb2.CalculateImpactResponse()
        outgoing_0 = lineage_v1_impact_validation_service_pb2.LintImpactsRequest(
            context=request.context,
            impact=lineage_v1_lineage_pb2.Impact(
                assignee=identity_v1_refs_pb2.UserRef(user_id=request.context.actor.user_id),
                customer=customers_v1_refs_pb2.CustomerRef(email=request.context.actor.email)
            )
        )
        response_0 = await deps.clients.lineage_impact_validation.LintImpacts(outgoing_0, timeout=deps.settings.timeout)
        outgoing_1 = lineage_v1_impact_calculation_service_pb2.CalculateImpactRequest(
            context=request.context,
            impact=lineage_v1_lineage_pb2.Impact(
                requester=common_v1_contact_pb2.ContactInfo(email=response_0.impact.customer.email),
                sla=lineage_v1_lineage_pb2.ImpactSla(
                    due_at=response_0.impact.sla.due_at,
                    paused_for=response_0.impact.sla.paused_for
                )
            )
        )
        send_1 = partial(deps.clients.lineage_impact_calculation.CalculateImpact, timeout=deps.settings.timeout)
        response_1 = await send_1(outgoing_1)
        returned_0_0 = response_0.result.status
        if returned_0_0:
            response.result.status = returned_0_0
        returned_0_1 = response_0.result.reference_ids
        response.result.reference_ids.extend(returned_0_1)
        returned_1_0 = response_1.impact.priority
        if returned_1_0:
            response.lineage_edge.subject.priority = returned_1_0
        returned_1_1 = response_1.result.details
        response.result.details.update(returned_1_1)
        echoed_0 = request.lineage_edge_id
        response.lineage_edge.lineage_edge_id = echoed_0
        return response


async def handle_resolve_lineage_edges(
    deps: Dependencies,
    request: lineage_v1_lineage_edge_query_service_pb2.ResolveLineageEdgesRequest
) -> lineage_v1_lineage_edge_query_service_pb2.ResolveLineageEdgesResponse:
    """Returns several lineage edges at once."""
    response = lineage_v1_lineage_edge_query_service_pb2.ResolveLineageEdgesResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('ResolveLineageEdges', extra={'fields': {'domain': 'lineage'}})
        await deps.repository.audit(request.context.tenant_id, 'ResolveLineageEdges', {})
        response_0 = featureflags_v1_feature_flag_validation_service_pb2.ScoreFeatureFlagResponse()
        outgoing_0 = featureflags_v1_feature_flag_validation_service_pb2.ScoreFeatureFlagRequest(
            context=request.context,
            feature_flag=featureflags_v1_featureflags_pb2.FeatureFlag(
                audit=common_v1_audit_pb2.AuditInfo(created_at=request.context.deadline),
                owner=identity_v1_refs_pb2.UserRef(
                    email=request.context.actor.email,
                    user_id=request.context.actor.user_id
                ),
                scopes=list(request.lineage_edge_ids)
            )
        )
        response_0 = await deps.clients.featureflags_feature_flag_validation.ScoreFeatureFlag(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.feature_flag.owner.display_name
        returned_0_0_part_0 = response.lineage_edges.add()
        if returned_0_0:
            returned_0_0_part_0.subject.display_name = returned_0_0
        return response


async def handle_suggest_lineage_edges(
    deps: Dependencies,
    request: lineage_v1_lineage_edge_query_service_pb2.SuggestLineageEdgesRequest
) -> lineage_v1_lineage_edge_query_service_pb2.SuggestLineageEdgesResponse:
    """Lists lineage edges a page at a time."""
    response = lineage_v1_lineage_edge_query_service_pb2.SuggestLineageEdgesResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('SuggestLineageEdges', extra={'fields': {'order_by': request.order_by}})
        await deps.repository.audit(request.context.tenant_id, 'SuggestLineageEdges', {'order_by': request.order_by})
        response_0 = lineage_v1_lineage_node_query_service_pb2.ExportLineageNodesResponse()
        outgoing_0 = lineage_v1_lineage_node_query_service_pb2.ExportLineageNodesRequest(
            context=request.context,
            filter=lineage_v1_lineage_node_query_service_pb2.ExportLineageNodesRequest.Filter(
                created_after=request.filter.created_after,
                labels=dict(request.filter.labels)
            )
        )
        async for chunk_0 in deps.clients.lineage_lineage_node_query.ExportLineageNodes(
            outgoing_0,
            timeout=deps.settings.timeout
        ):
            response_0 = chunk_0
        return response


async def handle_summarize_lineage_edges(
    deps: Dependencies,
    request: lineage_v1_lineage_edge_query_service_pb2.SummarizeLineageEdgesRequest
) -> lineage_v1_lineage_edge_query_service_pb2.SummarizeLineageEdgesResponse:
    """Summarizes a lineage edge."""
    response = lineage_v1_lineage_edge_query_service_pb2.SummarizeLineageEdgesResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('SummarizeLineageEdges', extra={'fields': {'lineage_edge_id': request.lineage_edge_id}})
        await deps.repository.audit(
            request.context.tenant_id,
            'SummarizeLineageEdges',
            {'lineage_edge_id': request.lineage_edge_id}
        )
        response_0 = lineage_v1_lineage_node_calculation_service_pb2.EstimateLineageNodeResponse()
        response_1 = certificates_v1_certificate_calculation_service_pb2.CompareCertificateOptionsResponse()
        response_2 = metrics_v1_dashboard_sync_service_pb2.ListDashboardConflictsResponse()
        response_3 = metrics_v1_metric_alert_history_service_pb2.RevertMetricAlertResponse()
        outgoing_0 = lineage_v1_lineage_node_calculation_service_pb2.EstimateLineageNodeRequest(
            context=request.context,
            lineage_node=lineage_v1_lineage_pb2.LineageNode(
                children=[
                    lineage_v1_lineage_pb2.LineageNode(
                        children=[
                            lineage_v1_lineage_pb2.LineageNode(
                                manager=identity_v1_refs_pb2.UserRef(
                                    email=request.context.actor.email,
                                    user_id=request.context.actor.user_id
                                )
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
        outgoing_1 = certificates_v1_certificate_calculation_service_pb2.CompareCertificateOptionsRequest(
            certificate=certificates_v1_certificates_pb2.Certificate(
                billing_address=common_v1_address_pb2.PostalAddress(locality=response_0.lineage_node.location.locality)
            ),
            context=request.context
        )
        steps_1 = [
            partial(
                deps.clients.certificates_certificate_calculation.CompareCertificateOptions,
                outgoing_1,
                timeout=deps.settings.timeout
            )
        ]
        results_1 = await run_steps(steps_1)
        response_1 = results_1[-1]
        outgoing_2 = metrics_v1_dashboard_sync_service_pb2.ListDashboardConflictsRequest(
            context=request.context,
            filter=metrics_v1_dashboard_sync_service_pb2.ListDashboardConflictsRequest.Filter(
                created_after=response_0.lineage_node.audit.updated_at,
                region=response_1.certificate.billing_address.region
            )
        )
        response_2 = await LineageEdgeQuerySummarizeLineageEdges2Adapter(
            deps.clients.metrics_dashboard_sync,
            deps.settings.timeout
        )(outgoing_2)
        outgoing_3 = metrics_v1_metric_alert_history_service_pb2.RevertMetricAlertRequest(
            context=request.context,
            metric_alert=metrics_v1_metrics_pb2.MetricAlert(
                audit=common_v1_audit_pb2.AuditInfo(
                    created_at=response_1.certificate.audit.created_at,
                    created_by=response_0.lineage_node.audit.created_by
                ),
                owner=identity_v1_refs_pb2.UserRef(display_name=response_0.lineage_node.manager.display_name)
            )
        )
        response_3 = cast(metrics_v1_metric_alert_history_service_pb2.RevertMetricAlertResponse, await deps.bus.request(
            'acme.lineage.v1.LineageEdgeQueryService/SummarizeLineageEdges/3', outgoing_3, deps.settings.timeout,
        ))
        returned_0_0 = response_0.result.status
        if returned_0_0:
            response.result.status = returned_0_0
        returned_1_0 = response_1.result.message
        if returned_1_0:
            response.result.message = returned_1_0
        returned_1_1 = response_1.result.details
        response.result.details.update(returned_1_1)
        returned_2_0 = response_2.result.message
        if returned_2_0:
            response.result.message = returned_2_0
        returned_3_0 = response_3.result.reference_ids
        response.result.reference_ids.extend(returned_3_0)
        echoed_0 = request.details.period
        response.period.CopyFrom(echoed_0)
        return response
