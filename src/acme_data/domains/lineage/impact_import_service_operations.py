"""Functional operations behind ImpactImportService."""

from __future__ import annotations

from collections.abc import Awaitable
from collections.abc import Callable
from functools import partial
from typing import cast
import asyncio
import logging

from google.protobuf.json_format import MessageToDict
from google.protobuf.json_format import ParseDict

from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.common.v1 import paging_pb2 as common_v1_paging_pb2
from acme.customers.v1 import (
    consent_record_validation_service_pb2 as customers_v1_consent_record_validation_service_pb2,
)
from acme.customers.v1 import customers_pb2 as customers_v1_customers_pb2
from acme.customers.v1 import refs_pb2 as customers_v1_refs_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.lineage.v1 import impact_import_service_pb2 as lineage_v1_impact_import_service_pb2
from acme.lineage.v1 import impact_validation_service_pb2 as lineage_v1_impact_validation_service_pb2
from acme.lineage.v1 import lineage_edge_calculation_service_pb2 as lineage_v1_lineage_edge_calculation_service_pb2
from acme.lineage.v1 import lineage_edge_import_service_pb2 as lineage_v1_lineage_edge_import_service_pb2
from acme.lineage.v1 import lineage_node_service_pb2 as lineage_v1_lineage_node_service_pb2
from acme.lineage.v1 import lineage_node_sync_service_pb2 as lineage_v1_lineage_node_sync_service_pb2
from acme.lineage.v1 import lineage_pb2 as lineage_v1_lineage_pb2
from acme.lineage.v1 import refs_pb2 as lineage_v1_refs_pb2
from acme.metrics.v1 import metric_series_service_pb2 as metrics_v1_metric_series_service_pb2
from acme.metrics.v1 import metrics_pb2 as metrics_v1_metrics_pb2

from acme_data.domains.lineage.dependencies import Dependencies
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import run_steps
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


async def handle_cancel_impact_import(
    deps: Dependencies,
    request: lineage_v1_impact_import_service_pb2.CancelImpactImportRequest
) -> lineage_v1_impact_import_service_pb2.CancelImpactImportResponse:
    """Cancels an impact."""
    response = lineage_v1_impact_import_service_pb2.CancelImpactImportResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('CancelImpactImport', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'CancelImpactImport', {'reason': request.reason})
        response_0 = lineage_v1_lineage_edge_calculation_service_pb2.CalculateLineageEdgeResponse()
        response_1 = customers_v1_consent_record_validation_service_pb2.ValidateConsentRecordResponse()
        outgoing_0 = lineage_v1_lineage_edge_calculation_service_pb2.CalculateLineageEdgeRequest(
            annotations=dict(request.annotations),
            context=request.context,
            lineage_edge=lineage_v1_lineage_pb2.LineageEdge(
                subject=lineage_v1_refs_pb2.ImpactRef(
                    display_name=request.details.new_owner.display_name,
                    impact_id=request.impact_id
                )
            )
        )
        response_0 = await deps.clients.lineage_lineage_edge_calculation.CalculateLineageEdge(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = customers_v1_consent_record_validation_service_pb2.ValidateConsentRecordRequest(
            consent_record=customers_v1_customers_pb2.ConsentRecord(
                attributes=dict(response_0.lineage_edge.attributes),
                subject=customers_v1_refs_pb2.HouseholdRef(display_name=response_0.lineage_edge.subject.display_name)
            ),
            context=request.context,
            details=customers_v1_consent_record_validation_service_pb2.ValidateConsentRecordRequest.Details(
                contact=common_v1_contact_pb2.ContactInfo(
                    name=request.details.notify_contact.name,
                    preferred_channel=request.details.notify_contact.preferred_channel
                )
            )
        )
        steps_1 = [
            partial(
                deps.clients.customers_consent_record_validation.ValidateConsentRecord,
                outgoing_1,
                timeout=deps.settings.timeout
            )
        ]
        results_1 = await run_steps(steps_1)
        response_1 = results_1[-1]
        returned_0_0 = response_0.result.reference_ids
        response.result.reference_ids.extend(returned_0_0)
        returned_1_0 = response_1.result.reference_ids
        response.result.reference_ids.extend(returned_1_0)
        returned_1_1 = response_1.consent_record.subject.display_name
        if returned_1_1:
            response.impact.assignee.display_name = returned_1_1
        echoed_0 = request.impact_id
        response.impact.impact_id = echoed_0
        echoed_1 = request.details.effective_at
        response.outcome.effective_at.CopyFrom(echoed_1)
        return response


async def handle_get_impact_import_status(
    deps: Dependencies,
    request: lineage_v1_impact_import_service_pb2.GetImpactImportStatusRequest
) -> lineage_v1_impact_import_service_pb2.GetImpactImportStatusResponse:
    """Returns an impact."""
    response = lineage_v1_impact_import_service_pb2.GetImpactImportStatusResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('GetImpactImportStatus', extra={'fields': {'impact_id': request.impact_id}})
        await deps.repository.audit(
            request.context.tenant_id,
            'GetImpactImportStatus',
            {'impact_id': request.impact_id}
        )
        response_0 = metrics_v1_metric_series_service_pb2.CreateMetricSeriesResponse()
        response_1 = lineage_v1_impact_validation_service_pb2.LintImpactsResponse()
        outgoing_0 = metrics_v1_metric_series_service_pb2.CreateMetricSeriesRequest(
            context=request.context,
            metric_series=metrics_v1_metrics_pb2.MetricSeries(
                owner=identity_v1_refs_pb2.UserRef(email=request.context.actor.email)
            )
        )
        response_0 = await deps.clients.metrics_metric_series.CreateMetricSeries(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = lineage_v1_impact_validation_service_pb2.LintImpactsRequest(
            context=request.context,
            impact=lineage_v1_lineage_pb2.Impact(
                audit=common_v1_audit_pb2.AuditInfo(etag=response_0.metric_series.audit.etag)
            )
        )
        response_1 = cast(lineage_v1_impact_validation_service_pb2.LintImpactsResponse, await deps.bus.request(
            'acme.lineage.v1.ImpactImportService/GetImpactImportStatus/1', outgoing_1, deps.settings.timeout,
        ))
        returned_0_0 = response_0.metric_series.audit.created_at
        returned_0_0_part_1 = response.impact.comments.add()
        if returned_0_0.ListFields():
            returned_0_0_part_1.created_at.MergeFrom(returned_0_0)
        returned_0_1 = response_0.metric_series.owner.display_name
        if returned_0_1:
            response.impact.assignee.display_name = returned_0_1
        returned_1_0 = response_1.impact.impact_id
        if returned_1_0:
            response.impact.impact_id = returned_1_0
        return response


async def handle_import_impacts(
    deps: Dependencies,
    request: lineage_v1_impact_import_service_pb2.ImportImpactsRequest
) -> lineage_v1_impact_import_service_pb2.ImportImpactsResponse:
    """Takes a stream of impacts and answers once at the end."""
    response = lineage_v1_impact_import_service_pb2.ImportImpactsResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('ImportImpacts', extra={'fields': {'sequence': request.sequence}})
        await deps.repository.audit(request.context.tenant_id, 'ImportImpacts', {'sequence': request.sequence})
        if request.WhichOneof('chunk') == 'record':
            await deps.repository.save_impact(request.context.tenant_id, request.record)
        response_0 = lineage_v1_lineage_node_sync_service_pb2.ListLineageNodeConflictsResponse()
        outgoing_0 = lineage_v1_lineage_node_sync_service_pb2.ListLineageNodeConflictsRequest(
            context=request.context,
            filter=lineage_v1_lineage_node_sync_service_pb2.ListLineageNodeConflictsRequest.Filter(
                created_after=request.record.audit.updated_at,
                labels=dict(request.record.custom_fields),
                owner_id=request.record.assignee.user_id
            )
        )
        response_0 = await deps.clients.lineage_lineage_node_sync.ListLineageNodeConflicts(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.result.message
        if returned_0_0:
            response.result.message = returned_0_0
        returned_0_1 = response_0.result.reference_ids
        response.result.reference_ids.extend(returned_0_1)
        return response


async def handle_list_impact_imports(
    deps: Dependencies,
    request: lineage_v1_impact_import_service_pb2.ListImpactImportsRequest
) -> lineage_v1_impact_import_service_pb2.ListImpactImportsResponse:
    """Lists impacts a page at a time."""
    response = lineage_v1_impact_import_service_pb2.ListImpactImportsResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('ListImpactImports', extra={'fields': {'order_by': request.order_by}})
        await deps.repository.audit(request.context.tenant_id, 'ListImpactImports', {'order_by': request.order_by})
        response_0 = lineage_v1_lineage_edge_import_service_pb2.ListLineageEdgeImportsResponse()
        outgoing_0 = lineage_v1_lineage_edge_import_service_pb2.ListLineageEdgeImportsRequest(
            context=request.context,
            filter=lineage_v1_lineage_edge_import_service_pb2.ListLineageEdgeImportsRequest.Filter(
                owner_id=request.filter.owner_id,
                region=request.filter.region
            ),
            page=common_v1_paging_pb2.PageRequest(page_size=request.page.page_size)
        )
        response_0 = await deps.clients.lineage_lineage_edge_import.ListLineageEdgeImports(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.result.reference_ids
        response.result.reference_ids.extend(returned_0_0)
        return response


async def handle_map_impact_import_columns(
    deps: Dependencies,
    request: lineage_v1_impact_import_service_pb2.MapImpactImportColumnsRequest
) -> lineage_v1_impact_import_service_pb2.MapImpactImportColumnsResponse:
    """Maps an impact."""
    response = lineage_v1_impact_import_service_pb2.MapImpactImportColumnsResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('MapImpactImportColumns', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'MapImpactImportColumns', {'reason': request.reason})
        await deps.repository.save_impact(request.context.tenant_id, request.impact)
        response_0 = lineage_v1_lineage_node_service_pb2.BatchGetLineageNodesResponse()
        response_1 = lineage_v1_lineage_node_sync_service_pb2.ListLineageNodeConflictsResponse()
        outgoing_0 = lineage_v1_lineage_node_service_pb2.BatchGetLineageNodesRequest(context=request.context)
        response_0 = await deps.clients.lineage_lineage_node.BatchGetLineageNodes(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = lineage_v1_lineage_node_sync_service_pb2.ListLineageNodeConflictsRequest(
            context=request.context,
            filter=lineage_v1_lineage_node_sync_service_pb2.ListLineageNodeConflictsRequest.Filter(
                created_after=request.impact.audit.updated_at
            )
        )
        document_1 = MessageToDict(outgoing_1, preserving_proto_field_name=True)
        outgoing_1 = ParseDict(document_1, lineage_v1_lineage_node_sync_service_pb2.ListLineageNodeConflictsRequest())
        response_1 = await deps.clients.lineage_lineage_node_sync.ListLineageNodeConflicts(
            outgoing_1,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.result.reference_ids
        response.result.reference_ids.extend(returned_0_0)
        returned_1_0 = response_1.result.reference_ids
        response.result.reference_ids.extend(returned_1_0)
        returned_1_1 = response_1.result.message
        if returned_1_1:
            response.result.message = returned_1_1
        echoed_0 = request.impact_id
        response.impact.impact_id = echoed_0
        echoed_1 = request.impact.priority
        response.impact.priority = echoed_1
        return response


async def handle_validate_impact_import(
    deps: Dependencies,
    request: lineage_v1_impact_import_service_pb2.ValidateImpactImportRequest
) -> lineage_v1_impact_import_service_pb2.ValidateImpactImportResponse:
    """Validates an impact."""
    response = lineage_v1_impact_import_service_pb2.ValidateImpactImportResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('ValidateImpactImport', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'ValidateImpactImport', {'reason': request.reason})
        await deps.repository.save_impact(request.context.tenant_id, request.impact)
        response_0 = lineage_v1_lineage_node_sync_service_pb2.ReconcileLineageNodesResponse()
        for item_0 in request.impact.comments:
            outgoing_0 = lineage_v1_lineage_node_sync_service_pb2.ReconcileLineageNodesRequest(
                context=request.context,
                lineage_node=lineage_v1_lineage_pb2.LineageNode(
                    children=[
                        lineage_v1_lineage_pb2.LineageNode(
                            children=[
                                lineage_v1_lineage_pb2.LineageNode(
                                    audit=common_v1_audit_pb2.AuditInfo(created_at=item_0.created_at),
                                    manager=identity_v1_refs_pb2.UserRef(
                                        display_name=request.impact.assignee.display_name,
                                        email=request.details.contact.email
                                    )
                                )
                            ],
                            manager=identity_v1_refs_pb2.UserRef(email=item_0.author_email)
                        )
                    ]
                )
            )
            response_0 = await deps.clients.lineage_lineage_node_sync.ReconcileLineageNodes(
                outgoing_0,
                timeout=deps.settings.timeout
            )
        echoed_0 = request.impact_id
        response.impact.impact_id = echoed_0
        echoed_1 = request.impact.requester
        response.impact.requester.CopyFrom(echoed_1)
        return response
