"""Functional operations behind AnomalyValidationService."""

from __future__ import annotations

from collections.abc import Awaitable
from collections.abc import Callable
from typing import cast
import asyncio
import logging

from google.protobuf.json_format import MessageToDict
from google.protobuf.json_format import ParseDict

from acme.admissions.v1 import admission_calculation_service_pb2 as admissions_v1_admission_calculation_service_pb2
from acme.admissions.v1 import admissions_pb2 as admissions_v1_admissions_pb2
from acme.admissions.v1 import refs_pb2 as admissions_v1_refs_pb2
from acme.anomalies.v1 import anomaly_validation_service_pb2 as anomalies_v1_anomaly_validation_service_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.lineage.v1 import lineage_edge_calculation_service_pb2 as lineage_v1_lineage_edge_calculation_service_pb2
from acme.lineage.v1 import lineage_edge_query_service_pb2 as lineage_v1_lineage_edge_query_service_pb2
from acme.lineage.v1 import lineage_edge_validation_service_pb2 as lineage_v1_lineage_edge_validation_service_pb2
from acme.lineage.v1 import lineage_node_calculation_service_pb2 as lineage_v1_lineage_node_calculation_service_pb2
from acme.lineage.v1 import lineage_node_service_pb2 as lineage_v1_lineage_node_service_pb2
from acme.lineage.v1 import lineage_node_validation_service_pb2 as lineage_v1_lineage_node_validation_service_pb2
from acme.lineage.v1 import lineage_pb2 as lineage_v1_lineage_pb2
from acme.lineage.v1 import refs_pb2 as lineage_v1_refs_pb2
from acme.metrics.v1 import dashboard_notification_service_pb2 as metrics_v1_dashboard_notification_service_pb2
from acme.metrics.v1 import metric_alert_export_service_pb2 as metrics_v1_metric_alert_export_service_pb2
from acme.metrics.v1 import metric_alert_query_service_pb2 as metrics_v1_metric_alert_query_service_pb2
from acme.patients.v1 import patient_query_service_pb2 as patients_v1_patient_query_service_pb2

from acme_data.domains.anomalies.adapters import AnomalyValidationExplainAnomalyDecision2Adapter
from acme_data.domains.anomalies.adapters import AnomalyValidationExplainAnomalyDecision2Port
from acme_data.domains.anomalies.dependencies import Dependencies
from acme_data.platform.rpc import async_messages
from acme_data.platform.tenancy import tenant_id
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


async def handle_check_anomaly_eligibility(
    deps: Dependencies,
    request: anomalies_v1_anomaly_validation_service_pb2.CheckAnomalyEligibilityRequest
) -> anomalies_v1_anomaly_validation_service_pb2.CheckAnomalyEligibilityResponse:
    """Checks an anomaly."""
    response = anomalies_v1_anomaly_validation_service_pb2.CheckAnomalyEligibilityResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('CheckAnomalyEligibility', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'CheckAnomalyEligibility', {'reason': request.reason})
        await deps.repository.save_anomaly(request.context.tenant_id, request.anomaly)
        response_0 = lineage_v1_lineage_node_calculation_service_pb2.QuoteLineageNodeResponse()
        response_1 = metrics_v1_metric_alert_query_service_pb2.CountMetricAlertsResponse()
        outgoing_0 = lineage_v1_lineage_node_calculation_service_pb2.QuoteLineageNodeRequest(
            context=request.context,
            lineage_node=lineage_v1_lineage_pb2.LineageNode(
                children=[
                    lineage_v1_lineage_pb2.LineageNode(
                        children=[
                            lineage_v1_lineage_pb2.LineageNode(
                                manager=identity_v1_refs_pb2.UserRef(display_name=request.anomaly.customer.display_name)
                            )
                        ]
                    )
                ]
            )
        )
        response_0 = await deps.clients.lineage_lineage_node_calculation.QuoteLineageNode(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = metrics_v1_metric_alert_query_service_pb2.CountMetricAlertsRequest()
        outgoing_1.context.CopyFrom(request.context)
        outgoing_1.filter.region = response_0.lineage_node.location.region
        outgoing_1.filter.created_after.CopyFrom(response_0.lineage_node.audit.created_at)
        if request.anomaly.WhichOneof('origin') == 'customer':
            outgoing_1.filter.owner_id = request.anomaly.customer.detector_id
        response_1 = await deps.clients.metrics_metric_alert_query.CountMetricAlerts(
            outgoing_1,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.lineage_node.audit.updated_by
        if returned_0_0:
            response.anomaly.audit.updated_by = returned_0_0
        returned_1_0 = response_1.result.details
        response.result.details.update(returned_1_0)
        echoed_0 = request.anomaly_id
        response.anomaly.anomaly_id = echoed_0
        echoed_1 = request.anomaly.assignee
        response.anomaly.assignee.CopyFrom(echoed_1)
        return response


async def handle_explain_anomaly_decision(
    deps: Dependencies,
    request: anomalies_v1_anomaly_validation_service_pb2.ExplainAnomalyDecisionRequest
) -> anomalies_v1_anomaly_validation_service_pb2.ExplainAnomalyDecisionResponse:
    """Explains an anomaly."""
    response = anomalies_v1_anomaly_validation_service_pb2.ExplainAnomalyDecisionResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('ExplainAnomalyDecision', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'ExplainAnomalyDecision', {'reason': request.reason})
        await deps.repository.save_anomaly(request.context.tenant_id, request.anomaly)
        response_0 = metrics_v1_metric_alert_export_service_pb2.ShareMetricAlertExportResponse()
        response_1 = lineage_v1_lineage_node_service_pb2.ListLineageNodesResponse()
        response_2 = lineage_v1_lineage_edge_validation_service_pb2.ExplainLineageEdgeDecisionResponse()
        outgoing_0 = metrics_v1_metric_alert_export_service_pb2.ShareMetricAlertExportRequest(
            context=request.context,
            details=metrics_v1_metric_alert_export_service_pb2.ShareMetricAlertExportRequest.Details(
                channel=request.anomaly.channel.channel,
                recipient=common_v1_contact_pb2.ContactInfo(
                    email=request.anomaly.assignee.email,
                    phone=request.details.contact.phone,
                    preferred_channel=request.anomaly.requester.preferred_channel
                )
            )
        )
        response_0 = await deps.clients.metrics_metric_alert_export.ShareMetricAlertExport(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = lineage_v1_lineage_node_service_pb2.ListLineageNodesRequest()
        outgoing_1.context.CopyFrom(request.context)
        outgoing_1.filter.created_after.CopyFrom(request.anomaly.audit.created_at)
        outgoing_1.context.tenant_id = tenant_id.get()
        response_1 = await deps.clients.lineage_lineage_node.ListLineageNodes(outgoing_1, timeout=deps.settings.timeout)
        outgoing_2 = lineage_v1_lineage_edge_validation_service_pb2.ExplainLineageEdgeDecisionRequest(
            context=request.context,
            details=lineage_v1_lineage_edge_validation_service_pb2.ExplainLineageEdgeDecisionRequest.Details(
                contact=common_v1_contact_pb2.ContactInfo(
                    email=request.anomaly.requester.email,
                    phone=request.anomaly.requester.phone,
                    preferred_channel=request.details.contact.preferred_channel
                )
            ),
            lineage_edge=lineage_v1_lineage_pb2.LineageEdge(
                subject=lineage_v1_refs_pb2.ImpactRef(display_name=response_0.metric_alert.owner.display_name)
            )
        )
        port_2: AnomalyValidationExplainAnomalyDecision2Port = AnomalyValidationExplainAnomalyDecision2Adapter(
            deps.clients.lineage_lineage_edge_validation,
            deps.settings.timeout
        )
        response_2 = await port_2.execute(outgoing_2)
        returned_0_0 = response_0.outcome.effective_at
        if returned_0_0.ListFields():
            response.outcome.effective_at.MergeFrom(returned_0_0)
        returned_0_1 = response_0.metric_alert.audit.created_at
        if returned_0_1.ListFields():
            response.anomaly.audit.created_at.MergeFrom(returned_0_1)
        returned_1_0 = response_1.result.status
        if returned_1_0:
            response.outcome.status = returned_1_0
        returned_2_0 = response_2.outcome.next_steps
        response.outcome.next_steps.extend(returned_2_0)
        echoed_0 = request.anomaly_id
        response.anomaly.anomaly_id = echoed_0
        echoed_1 = request.anomaly.status
        response.anomaly.status = echoed_1
        return response


async def handle_lint_anomalies(
    deps: Dependencies,
    request: anomalies_v1_anomaly_validation_service_pb2.LintAnomaliesRequest
) -> anomalies_v1_anomaly_validation_service_pb2.LintAnomaliesResponse:
    """Lints an anomaly."""
    response = anomalies_v1_anomaly_validation_service_pb2.LintAnomaliesResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('LintAnomalies', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'LintAnomalies', {'reason': request.reason})
        await deps.repository.save_anomaly(request.context.tenant_id, request.anomaly)
        response_0 = metrics_v1_metric_alert_query_service_pb2.CountMetricAlertsResponse()
        outgoing_0 = metrics_v1_metric_alert_query_service_pb2.CountMetricAlertsRequest(
            context=request.context,
            filter=metrics_v1_metric_alert_query_service_pb2.CountMetricAlertsRequest.Filter(
                created_after=request.anomaly.audit.updated_at,
                labels=dict(request.anomaly.custom_fields),
                owner_id=request.anomaly.assignee.user_id
            )
        )
        response_0 = await deps.clients.metrics_metric_alert_query.CountMetricAlerts(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.result.correlation_id
        if returned_0_0:
            response.result.correlation_id = returned_0_0
        returned_0_1 = response_0.result.message
        if returned_0_1:
            response.outcome.message = returned_0_1
        echoed_0 = request.anomaly_id
        response.anomaly.anomaly_id = echoed_0
        echoed_1 = request.anomaly.custom_fields
        response.anomaly.custom_fields.update(echoed_1)
        return response


async def handle_normalize_anomaly(
    deps: Dependencies,
    request: anomalies_v1_anomaly_validation_service_pb2.NormalizeAnomalyRequest
) -> anomalies_v1_anomaly_validation_service_pb2.NormalizeAnomalyResponse:
    """Normalizes an anomaly."""
    response = anomalies_v1_anomaly_validation_service_pb2.NormalizeAnomalyResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('NormalizeAnomaly', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'NormalizeAnomaly', {'reason': request.reason})
        await deps.repository.save_anomaly(request.context.tenant_id, request.anomaly)
        response_0 = admissions_v1_admission_calculation_service_pb2.SimulateAdmissionResponse()
        response_1 = lineage_v1_lineage_node_validation_service_pb2.LintLineageNodesResponse()
        response_2 = metrics_v1_dashboard_notification_service_pb2.StreamDashboardNoticesResponse()
        response_3 = lineage_v1_lineage_edge_query_service_pb2.BrowseLineageEdgesResponse()
        outgoing_0 = admissions_v1_admission_calculation_service_pb2.SimulateAdmissionRequest(
            admission=admissions_v1_admissions_pb2.Admission(
                measurements=[
                    admissions_v1_admissions_pb2.AdmissionMeasurement(observed_at=request.anomaly.audit.updated_at)
                ],
                subject=admissions_v1_refs_pb2.GateScanRef(display_name=request.anomaly.customer.display_name)
            ),
            annotations=dict(request.annotations),
            context=request.context
        )
        response_0 = await deps.clients.admissions_admission_calculation.SimulateAdmission(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = lineage_v1_lineage_node_validation_service_pb2.LintLineageNodesRequest(
            context=request.context,
            lineage_node=lineage_v1_lineage_pb2.LineageNode(
                children=[
                    lineage_v1_lineage_pb2.LineageNode(
                        children=[
                            lineage_v1_lineage_pb2.LineageNode(
                                manager=identity_v1_refs_pb2.UserRef(display_name=request.anomaly.assignee.display_name)
                            )
                        ]
                    )
                ]
            )
        )
        response_1 = cast(lineage_v1_lineage_node_validation_service_pb2.LintLineageNodesResponse, await deps.bus.request(
            'acme.anomalies.v1.AnomalyValidationService/NormalizeAnomaly/1', outgoing_1, deps.settings.timeout,
        ))
        outgoing_2 = metrics_v1_dashboard_notification_service_pb2.StreamDashboardNoticesRequest(
            context=request.context,
            filter=metrics_v1_dashboard_notification_service_pb2.StreamDashboardNoticesRequest.Filter(
                region=response_1.lineage_node.location.region
            ),
            subscriber=common_v1_contact_pb2.ContactInfo(name=request.details.contact.name)
        )
        async for chunk_2 in deps.clients.metrics_dashboard_notification.StreamDashboardNotices(
            outgoing_2,
            timeout=deps.settings.timeout
        ):
            response_2 = chunk_2
        async for item_3 in async_messages(request.anomaly.comments):
            outgoing_3 = lineage_v1_lineage_edge_query_service_pb2.BrowseLineageEdgesRequest(
                context=request.context,
                filter=lineage_v1_lineage_edge_query_service_pb2.BrowseLineageEdgesRequest.Filter(
                    created_after=item_3.created_at,
                    region=response_1.lineage_node.location.region
                )
            )
            response_3 = await deps.clients.lineage_lineage_edge_query.BrowseLineageEdges(
                outgoing_3,
                timeout=deps.settings.timeout
            )
        returned_0_0 = response_0.result.correlation_id
        if returned_0_0:
            response.result.correlation_id = returned_0_0
        returned_1_0 = response_1.lineage_node.audit.created_at
        returned_1_0_part_1 = response.anomaly.comments.add()
        if returned_1_0.ListFields():
            returned_1_0_part_1.created_at.MergeFrom(returned_1_0)
        returned_1_1 = response_1.outcome.status
        if returned_1_1:
            response.result.status = returned_1_1
        echoed_0 = request.anomaly_id
        response.anomaly.anomaly_id = echoed_0
        echoed_1 = request.anomaly.subject
        response.anomaly.subject = echoed_1
        return response


async def handle_preview_anomaly(
    deps: Dependencies,
    request: anomalies_v1_anomaly_validation_service_pb2.PreviewAnomalyRequest
) -> anomalies_v1_anomaly_validation_service_pb2.PreviewAnomalyResponse:
    """Previews an anomaly."""
    response = anomalies_v1_anomaly_validation_service_pb2.PreviewAnomalyResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('PreviewAnomaly', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'PreviewAnomaly', {'reason': request.reason})
        await deps.repository.save_anomaly(request.context.tenant_id, request.anomaly)
        response_0 = metrics_v1_metric_alert_query_service_pb2.FindMetricAlertsResponse()
        response_1 = lineage_v1_lineage_edge_query_service_pb2.BrowseLineageEdgesResponse()
        outgoing_0 = metrics_v1_metric_alert_query_service_pb2.FindMetricAlertsRequest(
            context=request.context,
            filter=metrics_v1_metric_alert_query_service_pb2.FindMetricAlertsRequest.Filter(
                created_after=request.anomaly.audit.created_at
            )
        )
        response_0 = await deps.clients.metrics_metric_alert_query.FindMetricAlerts(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = lineage_v1_lineage_edge_query_service_pb2.BrowseLineageEdgesRequest(
            context=request.context,
            filter=lineage_v1_lineage_edge_query_service_pb2.BrowseLineageEdgesRequest.Filter(
                created_after=request.anomaly.sla.due_at,
                labels=dict(response_0.result.details),
                owner_id=request.anomaly.assignee.user_id
            )
        )
        document_1 = MessageToDict(outgoing_1, preserving_proto_field_name=True)
        outgoing_1 = ParseDict(document_1, lineage_v1_lineage_edge_query_service_pb2.BrowseLineageEdgesRequest())
        response_1 = await deps.clients.lineage_lineage_edge_query.BrowseLineageEdges(
            outgoing_1,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.result.status
        if returned_0_0:
            response.result.status = returned_0_0
        returned_0_1 = response_0.result.correlation_id
        if returned_0_1:
            response.result.correlation_id = returned_0_1
        returned_1_0 = response_1.result.details
        response.result.details.update(returned_1_0)
        echoed_0 = request.anomaly_id
        response.anomaly.anomaly_id = echoed_0
        echoed_1 = request.anomaly.assignee
        response.anomaly.assignee.CopyFrom(echoed_1)
        return response


async def handle_score_anomaly(
    deps: Dependencies,
    request: anomalies_v1_anomaly_validation_service_pb2.ScoreAnomalyRequest
) -> anomalies_v1_anomaly_validation_service_pb2.ScoreAnomalyResponse:
    """Scores an anomaly."""
    response = anomalies_v1_anomaly_validation_service_pb2.ScoreAnomalyResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('ScoreAnomaly', extra={'fields': {'anomaly_id': request.anomaly.anomaly_id}})
        await deps.repository.audit(
            request.context.tenant_id,
            'ScoreAnomaly',
            {'anomaly_id': request.anomaly.anomaly_id}
        )
        await deps.repository.save_anomaly(request.context.tenant_id, request.anomaly)
        response_0 = patients_v1_patient_query_service_pb2.SummarizePatientsResponse()
        response_1 = lineage_v1_lineage_edge_calculation_service_pb2.ExplainLineageEdgeCalculationResponse()
        outgoing_0 = patients_v1_patient_query_service_pb2.SummarizePatientsRequest(
            annotations=dict(request.annotations),
            context=request.context,
            details=patients_v1_patient_query_service_pb2.SummarizePatientsRequest.Details(
                filters=dict(request.anomaly.custom_fields)
            ),
            reason=request.reason
        )
        response_0 = await deps.clients.patients_patient_query.SummarizePatients(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        for item_1 in request.anomaly.comments:
            outgoing_1 = lineage_v1_lineage_edge_calculation_service_pb2.ExplainLineageEdgeCalculationRequest(
                context=request.context,
                details=lineage_v1_lineage_edge_calculation_service_pb2.ExplainLineageEdgeCalculationRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(
                        email=item_1.author_email,
                        phone=request.anomaly.requester.phone
                    )
                )
            )
            response_1 = await deps.clients.lineage_lineage_edge_calculation.ExplainLineageEdgeCalculation(
                outgoing_1,
                timeout=deps.settings.timeout
            )
        returned_0_0 = response_0.result.details
        response.result.details.update(returned_0_0)
        returned_0_1 = response_0.result.message
        if returned_0_1:
            response.result.message = returned_0_1
        echoed_0 = request.anomaly_id
        response.anomaly.anomaly_id = echoed_0
        echoed_1 = request.anomaly.priority
        response.anomaly.priority = echoed_1
        return response


async def handle_validate_anomaly(
    deps: Dependencies,
    request: anomalies_v1_anomaly_validation_service_pb2.ValidateAnomalyRequest
) -> anomalies_v1_anomaly_validation_service_pb2.ValidateAnomalyResponse:
    """Validates an anomaly."""
    response = anomalies_v1_anomaly_validation_service_pb2.ValidateAnomalyResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('ValidateAnomaly', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'ValidateAnomaly', {'reason': request.reason})
        await deps.repository.save_anomaly(request.context.tenant_id, request.anomaly)
        response_0 = lineage_v1_lineage_edge_query_service_pb2.SuggestLineageEdgesResponse()
        outgoing_0 = lineage_v1_lineage_edge_query_service_pb2.SuggestLineageEdgesRequest(
            context=request.context,
            filter=lineage_v1_lineage_edge_query_service_pb2.SuggestLineageEdgesRequest.Filter(
                created_after=request.anomaly.sla.due_at,
                labels=dict(request.annotations),
                owner_id=request.anomaly.customer.detector_id
            )
        )
        response_0 = await deps.clients.lineage_lineage_edge_query.SuggestLineageEdges(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.result.reference_ids
        response.result.reference_ids.extend(returned_0_0)
        echoed_0 = request.anomaly_id
        response.anomaly.anomaly_id = echoed_0
        echoed_1 = request.anomaly.priority
        response.anomaly.priority = echoed_1
        return response
