"""Functional operations behind LineageNodeApprovalService."""

from __future__ import annotations

from functools import partial
from typing import cast
import asyncio
import logging

from google.protobuf.json_format import MessageToJson
from google.protobuf.json_format import Parse

from acme.analytics.v1 import analytics_event_query_service_pb2 as analytics_v1_analytics_event_query_service_pb2
from acme.anomalies.v1 import (
    anomaly_feedback_validation_service_pb2 as anomalies_v1_anomaly_feedback_validation_service_pb2,
)
from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.common.v1 import paging_pb2 as common_v1_paging_pb2
from acme.customers.v1 import (
    consent_record_validation_service_pb2 as customers_v1_consent_record_validation_service_pb2,
)
from acme.customers.v1 import customer_calculation_service_pb2 as customers_v1_customer_calculation_service_pb2
from acme.customers.v1 import (
    customer_calculation_service_pb2_grpc as customers_v1_customer_calculation_service_pb2_grpc,
)
from acme.customers.v1 import (
    customer_segment_validation_service_pb2 as customers_v1_customer_segment_validation_service_pb2,
)
from acme.customers.v1 import customer_service_pb2 as customers_v1_customer_service_pb2
from acme.customers.v1 import customers_pb2 as customers_v1_customers_pb2
from acme.customers.v1 import household_query_service_pb2 as customers_v1_household_query_service_pb2
from acme.customers.v1 import refs_pb2 as customers_v1_refs_pb2
from acme.documents.v1 import document_query_service_pb2 as documents_v1_document_query_service_pb2
from acme.featurestore.v1 import (
    feature_view_validation_service_pb2 as featurestore_v1_feature_view_validation_service_pb2,
)
from acme.featurestore.v1 import featurestore_pb2 as featurestore_v1_featurestore_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.labeling.v1 import annotation_calculation_service_pb2 as labeling_v1_annotation_calculation_service_pb2
from acme.labeling.v1 import labeling_pb2 as labeling_v1_labeling_pb2
from acme.lineage.v1 import impact_reporting_service_pb2 as lineage_v1_impact_reporting_service_pb2
from acme.lineage.v1 import impact_sync_service_pb2 as lineage_v1_impact_sync_service_pb2
from acme.lineage.v1 import impact_validation_service_pb2 as lineage_v1_impact_validation_service_pb2
from acme.lineage.v1 import lineage_edge_reporting_service_pb2 as lineage_v1_lineage_edge_reporting_service_pb2
from acme.lineage.v1 import lineage_edge_sync_service_pb2 as lineage_v1_lineage_edge_sync_service_pb2
from acme.lineage.v1 import lineage_node_approval_service_pb2 as lineage_v1_lineage_node_approval_service_pb2
from acme.lineage.v1 import lineage_node_lifecycle_service_pb2 as lineage_v1_lineage_node_lifecycle_service_pb2
from acme.lineage.v1 import lineage_node_reporting_service_pb2 as lineage_v1_lineage_node_reporting_service_pb2
from acme.lineage.v1 import (
    lineage_node_reporting_service_pb2_grpc as lineage_v1_lineage_node_reporting_service_pb2_grpc,
)
from acme.lineage.v1 import lineage_node_sync_service_pb2 as lineage_v1_lineage_node_sync_service_pb2
from acme.lineage.v1 import lineage_pb2 as lineage_v1_lineage_pb2
from acme.lineage.v1 import refs_pb2 as lineage_v1_refs_pb2
from acme.metrics.v1 import metric_alert_notification_service_pb2 as metrics_v1_metric_alert_notification_service_pb2
from acme.pipelines.v1 import pipeline_query_service_pb2 as pipelines_v1_pipeline_query_service_pb2

from acme_data.domains.lineage import hooks
from acme_data.domains.lineage.dependencies import Dependencies
from acme_data.domains.lineage.models import LineageNodeApprovalRejectLineageNode2Command
from acme_data.domains.lineage.models import to_lineage_node_approval_reject_lineage_node2_command
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import run_steps
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


async def handle_approve_lineage_node(
    deps: Dependencies,
    request: lineage_v1_lineage_node_approval_service_pb2.ApproveLineageNodeRequest
) -> lineage_v1_lineage_node_approval_service_pb2.ApproveLineageNodeResponse:
    """Approves a lineage node."""
    response = lineage_v1_lineage_node_approval_service_pb2.ApproveLineageNodeResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('ApproveLineageNode', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'ApproveLineageNode', {'reason': request.reason})
        await deps.repository.save_lineage_node(request.context.tenant_id, request.lineage_node)
        response_0 = featurestore_v1_feature_view_validation_service_pb2.ValidateFeatureViewResponse()
        response_1 = lineage_v1_lineage_node_reporting_service_pb2.ListLineageNodeReportsResponse()
        outgoing_0 = featurestore_v1_feature_view_validation_service_pb2.ValidateFeatureViewRequest(
            context=request.context,
            details=featurestore_v1_feature_view_validation_service_pb2.ValidateFeatureViewRequest.Details(
                contact=common_v1_contact_pb2.ContactInfo(email=request.lineage_node.manager.email)
            ),
            feature_view=featurestore_v1_featurestore_pb2.FeatureView(
                address=common_v1_address_pb2.PostalAddress(postal_code=request.lineage_node.location.postal_code),
                owner=identity_v1_refs_pb2.UserRef(user_id=request.details.approver.user_id)
            )
        )
        response_0 = await deps.clients.featurestore_feature_view_validation.ValidateFeatureView(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = lineage_v1_lineage_node_reporting_service_pb2.ListLineageNodeReportsRequest(
            context=request.context,
            filter=lineage_v1_lineage_node_reporting_service_pb2.ListLineageNodeReportsRequest.Filter(
                region=response_0.feature_view.address.region
            )
        )
        registered_1 = cast(
            lineage_v1_lineage_node_reporting_service_pb2_grpc.LineageNodeReportingServiceStub,
            deps.clients.registry['acme.lineage.v1.LineageNodeReportingService']
        )
        response_1 = await registered_1.ListLineageNodeReports(outgoing_1, timeout=deps.settings.timeout)
        returned_0_0 = response_0.feature_view.name
        returned_0_0_part_1 = response.lineage_node.children.add()
        if returned_0_0:
            returned_0_0_part_1.name = returned_0_0
        returned_1_0 = response_1.result.message
        if returned_1_0:
            response.result.message = returned_1_0
        returned_1_1 = response_1.result.status
        if returned_1_1:
            response.outcome.status = returned_1_1
        echoed_0 = request.lineage_node_id
        response.lineage_node.lineage_node_id = echoed_0
        echoed_1 = request.lineage_node.name
        response.lineage_node.name = echoed_1
        return response


async def handle_comment_lineage_node_approval(
    deps: Dependencies,
    request: lineage_v1_lineage_node_approval_service_pb2.CommentLineageNodeApprovalRequest
) -> lineage_v1_lineage_node_approval_service_pb2.CommentLineageNodeApprovalResponse:
    """Comments a lineage node."""
    response = lineage_v1_lineage_node_approval_service_pb2.CommentLineageNodeApprovalResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('CommentLineageNodeApproval', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'CommentLineageNodeApproval', {'reason': request.reason})
        await deps.repository.save_lineage_node(request.context.tenant_id, request.lineage_node)
        response_0 = lineage_v1_lineage_edge_reporting_service_pb2.CountLineageEdgeTotalsResponse()
        response_1 = lineage_v1_impact_validation_service_pb2.NormalizeImpactResponse()
        response_2 = customers_v1_household_query_service_pb2.CountHouseholdsResponse()
        response_3 = lineage_v1_lineage_node_lifecycle_service_pb2.ExpireLineageNodeResponse()
        outgoing_1 = lineage_v1_impact_validation_service_pb2.NormalizeImpactRequest(
            context=request.context,
            impact=lineage_v1_lineage_pb2.Impact(
                assignee=identity_v1_refs_pb2.UserRef(user_id=request.lineage_node.manager.user_id),
                audit=common_v1_audit_pb2.AuditInfo(etag=request.lineage_node.audit.etag),
                customer=customers_v1_refs_pb2.CustomerRef(email=request.lineage_node.manager.email)
            )
        )
        outgoing_2 = customers_v1_household_query_service_pb2.CountHouseholdsRequest(
            context=request.context,
            filter=customers_v1_household_query_service_pb2.CountHouseholdsRequest.Filter(
                created_after=request.lineage_node.audit.created_at,
                labels=dict(request.lineage_node.attributes),
                owner_id=request.details.approver.user_id,
                region=request.lineage_node.location.region
            )
        )
        response_1, response_2 = await asyncio.gather(
            deps.clients.lineage_impact_validation.NormalizeImpact(outgoing_1, timeout=deps.settings.timeout),
            deps.clients.customers_household_query.CountHouseholds(outgoing_2, timeout=deps.settings.timeout),
        )
        outgoing_0 = lineage_v1_lineage_edge_reporting_service_pb2.CountLineageEdgeTotalsRequest(
            context=request.context,
            filter=lineage_v1_lineage_edge_reporting_service_pb2.CountLineageEdgeTotalsRequest.Filter(
                created_after=request.lineage_node.audit.updated_at,
                labels=dict(request.annotations),
                region=request.lineage_node.location.region
            )
        )
        response_0 = await deps.clients.lineage_lineage_edge_reporting.CountLineageEdgeTotals(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_3 = lineage_v1_lineage_node_lifecycle_service_pb2.ExpireLineageNodeRequest(
            context=request.context,
            details=lineage_v1_lineage_node_lifecycle_service_pb2.ExpireLineageNodeRequest.Details(
                new_owner=identity_v1_refs_pb2.UserRef(user_id=request.lineage_node.manager.user_id),
                notify_contact=common_v1_contact_pb2.ContactInfo(email=response_1.impact.assignee.email)
            ),
            lineage_node_id=request.lineage_node.lineage_node_id
        )
        response_3 = await hooks.lineage_node_approval_comment_lineage_node_approval3(
            deps.clients.lineage_lineage_node_lifecycle,
            outgoing_3,
            deps.settings.timeout
        )
        returned_0_0 = response_0.result.message
        if returned_0_0:
            response.outcome.message = returned_0_0
        returned_1_0 = response_1.impact.assignee.email
        returned_1_0_part_1 = response.lineage_node.children.add()
        if returned_1_0:
            returned_1_0_part_1.manager.email = returned_1_0
        returned_2_0 = response_2.result.details
        response.result.details.update(returned_2_0)
        returned_2_1 = response_2.result.status
        if returned_2_1:
            response.outcome.status = returned_2_1
        returned_3_0 = response_3.lineage_node.audit.updated_by
        returned_3_0_part_1 = response.lineage_node.children.add()
        returned_3_0_part_2 = returned_3_0_part_1.children.add()
        if returned_3_0:
            returned_3_0_part_2.audit.updated_by = returned_3_0
        echoed_0 = request.lineage_node_id
        response.lineage_node.lineage_node_id = echoed_0
        echoed_1 = request.lineage_node.parent_id
        response.lineage_node.parent_id = echoed_1
        return response


async def handle_delegate_lineage_node_approval(
    deps: Dependencies,
    request: lineage_v1_lineage_node_approval_service_pb2.DelegateLineageNodeApprovalRequest
) -> lineage_v1_lineage_node_approval_service_pb2.DelegateLineageNodeApprovalResponse:
    """Delegates a lineage node."""
    response = lineage_v1_lineage_node_approval_service_pb2.DelegateLineageNodeApprovalResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('DelegateLineageNodeApproval', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(
            request.context.tenant_id,
            'DelegateLineageNodeApproval',
            {'reason': request.reason}
        )
        await deps.repository.save_lineage_node(request.context.tenant_id, request.lineage_node)
        response_0 = customers_v1_customer_segment_validation_service_pb2.ValidateCustomerSegmentResponse()
        outgoing_0 = customers_v1_customer_segment_validation_service_pb2.ValidateCustomerSegmentRequest(
            context=request.context,
            customer_segment=customers_v1_customers_pb2.CustomerSegment(
                audit=common_v1_audit_pb2.AuditInfo(created_at=request.lineage_node.audit.created_at),
                owner=identity_v1_refs_pb2.UserRef(display_name=request.lineage_node.manager.display_name)
            ),
            details=customers_v1_customer_segment_validation_service_pb2.ValidateCustomerSegmentRequest.Details(
                contact=common_v1_contact_pb2.ContactInfo(email=request.details.approver.email)
            )
        )
        response_0 = await deps.clients.customers_customer_segment_validation.ValidateCustomerSegment(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.customer_segment.name
        returned_0_0_part_1 = response.lineage_node.children.add()
        returned_0_0_part_2 = returned_0_0_part_1.children.add()
        returned_0_0_part_3 = returned_0_0_part_2.children.add()
        if returned_0_0:
            returned_0_0_part_3.name = returned_0_0
        echoed_0 = request.lineage_node_id
        response.lineage_node.lineage_node_id = echoed_0
        echoed_1 = request.lineage_node.depth
        response.lineage_node.depth = echoed_1
        return response


async def handle_escalate_lineage_node(
    deps: Dependencies,
    request: lineage_v1_lineage_node_approval_service_pb2.EscalateLineageNodeRequest
) -> lineage_v1_lineage_node_approval_service_pb2.EscalateLineageNodeResponse:
    """Escalates a lineage node."""
    response = lineage_v1_lineage_node_approval_service_pb2.EscalateLineageNodeResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('EscalateLineageNode', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'EscalateLineageNode', {'reason': request.reason})
        await deps.repository.save_lineage_node(request.context.tenant_id, request.lineage_node)
        response_0 = lineage_v1_lineage_node_sync_service_pb2.SyncLineageNodesResponse()
        response_1 = customers_v1_customer_service_pb2.CloneCustomerResponse()
        response_2 = metrics_v1_metric_alert_notification_service_pb2.StreamMetricAlertNoticesResponse()
        outgoing_0 = lineage_v1_lineage_node_sync_service_pb2.SyncLineageNodesRequest(
            context=request.context,
            lineage_node=lineage_v1_lineage_pb2.LineageNode(
                children=[
                    lineage_v1_lineage_pb2.LineageNode(
                        children=[
                            lineage_v1_lineage_pb2.LineageNode(
                                audit=common_v1_audit_pb2.AuditInfo(
                                    etag=request.lineage_node.audit.etag,
                                    updated_at=request.lineage_node.audit.updated_at
                                )
                            )
                        ]
                    )
                ]
            )
        )
        response_0 = await deps.clients.lineage_lineage_node_sync.SyncLineageNodes(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = customers_v1_customer_service_pb2.CloneCustomerRequest(
            context=request.context,
            customer=customers_v1_customers_pb2.Customer(
                audit=common_v1_audit_pb2.AuditInfo(created_at=request.lineage_node.audit.created_at)
            )
        )
        steps_1 = [partial(deps.clients.customers_customer.CloneCustomer, outgoing_1, timeout=deps.settings.timeout)]
        results_1 = await run_steps(steps_1)
        response_1 = results_1[-1]
        outgoing_2 = metrics_v1_metric_alert_notification_service_pb2.StreamMetricAlertNoticesRequest(
            context=request.context,
            subscriber=common_v1_contact_pb2.ContactInfo(email=response_1.customer.relationship_manager.email)
        )
        async for chunk_2 in deps.clients.metrics_metric_alert_notification.StreamMetricAlertNotices(
            outgoing_2,
            timeout=deps.settings.timeout
        ):
            response_2 = chunk_2
        returned_0_0 = response_0.lineage_node.audit.created_at
        returned_0_0_part_1 = response.lineage_node.children.add()
        if returned_0_0.ListFields():
            returned_0_0_part_1.audit.created_at.MergeFrom(returned_0_0)
        returned_1_0 = response_1.result.reference_ids
        response.result.reference_ids.extend(returned_1_0)
        echoed_0 = request.lineage_node_id
        response.lineage_node.lineage_node_id = echoed_0
        echoed_1 = request.lineage_node.attributes
        response.lineage_node.attributes.update(echoed_1)
        return response


async def handle_get_lineage_node_approval_status(
    deps: Dependencies,
    request: lineage_v1_lineage_node_approval_service_pb2.GetLineageNodeApprovalStatusRequest
) -> lineage_v1_lineage_node_approval_service_pb2.GetLineageNodeApprovalStatusResponse:
    """Returns a lineage node."""
    response = lineage_v1_lineage_node_approval_service_pb2.GetLineageNodeApprovalStatusResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('GetLineageNodeApprovalStatus', extra={'fields': {'domain': 'lineage'}})
        await deps.repository.audit(request.context.tenant_id, 'GetLineageNodeApprovalStatus', {})
        response_0 = lineage_v1_lineage_node_sync_service_pb2.SyncLineageNodesResponse()
        outgoing_0 = lineage_v1_lineage_node_sync_service_pb2.SyncLineageNodesRequest(
            context=request.context,
            lineage_node=lineage_v1_lineage_pb2.LineageNode(
                children=[
                    lineage_v1_lineage_pb2.LineageNode(
                        children=[
                            lineage_v1_lineage_pb2.LineageNode(
                                children=[lineage_v1_lineage_pb2.LineageNode(lineage_node_id=request.lineage_node_id)],
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
        response_0 = await deps.clients.lineage_lineage_node_sync.SyncLineageNodes(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.lineage_node.audit.updated_by
        if returned_0_0:
            response.lineage_node.audit.updated_by = returned_0_0
        echoed_0 = request.lineage_node_id
        response.lineage_node.lineage_node_id = echoed_0
        return response


async def handle_list_pending_lineage_nodes(
    deps: Dependencies,
    request: lineage_v1_lineage_node_approval_service_pb2.ListPendingLineageNodesRequest
) -> lineage_v1_lineage_node_approval_service_pb2.ListPendingLineageNodesResponse:
    """Lists lineage nodes a page at a time."""
    response = lineage_v1_lineage_node_approval_service_pb2.ListPendingLineageNodesResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('ListPendingLineageNodes', extra={'fields': {'order_by': request.order_by}})
        await deps.repository.audit(
            request.context.tenant_id,
            'ListPendingLineageNodes',
            {'order_by': request.order_by}
        )
        response_0 = labeling_v1_annotation_calculation_service_pb2.RecalculateAnnotationsResponse()
        response_1 = lineage_v1_impact_sync_service_pb2.ListImpactConflictsResponse()
        outgoing_0 = labeling_v1_annotation_calculation_service_pb2.RecalculateAnnotationsRequest(
            annotation=labeling_v1_labeling_pb2.Annotation(
                attributes=dict(request.filter.labels),
                correlation_id=request.filter.owner_id,
                measurements=[labeling_v1_labeling_pb2.AnnotationMeasurement(observed_at=request.filter.created_after)]
            ),
            context=request.context,
            details=labeling_v1_annotation_calculation_service_pb2.RecalculateAnnotationsRequest.Details(
                destination=common_v1_address_pb2.PostalAddress(region=request.filter.region)
            )
        )
        response_0 = await deps.clients.labeling_annotation_calculation.RecalculateAnnotations(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = lineage_v1_impact_sync_service_pb2.ListImpactConflictsRequest(
            context=request.context,
            filter=lineage_v1_impact_sync_service_pb2.ListImpactConflictsRequest.Filter(
                owner_id=request.filter.owner_id
            ),
            page=common_v1_paging_pb2.PageRequest(page_size=request.page.page_size)
        )
        method_name_1 = 'ListImpactConflicts'
        response_1 = await getattr(
            deps.clients.lineage_impact_sync,
            method_name_1
        )(outgoing_1, timeout=deps.settings.timeout)
        returned_0_0 = response_0.annotation.attributes
        returned_0_0_part_0 = response.lineage_nodes.add()
        returned_0_0_part_1 = returned_0_0_part_0.children.add()
        returned_0_0_part_2 = returned_0_0_part_1.children.add()
        returned_0_0_part_2.attributes.update(returned_0_0)
        returned_1_0 = response_1.page_info.total_size
        if returned_1_0:
            response.page_info.total_size = returned_1_0
        return response


async def handle_recall_lineage_node(
    deps: Dependencies,
    request: lineage_v1_lineage_node_approval_service_pb2.RecallLineageNodeRequest
) -> lineage_v1_lineage_node_approval_service_pb2.RecallLineageNodeResponse:
    """Recalls a lineage node."""
    response = lineage_v1_lineage_node_approval_service_pb2.RecallLineageNodeResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('RecallLineageNode', extra={'fields': {'approver_email': request.details.approver_email}})
        await deps.repository.audit(
            request.context.tenant_id,
            'RecallLineageNode',
            {'approver_email': request.details.approver_email}
        )
        await deps.repository.save_lineage_node(request.context.tenant_id, request.lineage_node)
        response_0 = lineage_v1_impact_reporting_service_pb2.GenerateImpactReportResponse()
        response_1 = documents_v1_document_query_service_pb2.ExportDocumentsResponse()
        response_2 = metrics_v1_metric_alert_notification_service_pb2.SendMetricAlertTestNoticeResponse()
        response_3 = pipelines_v1_pipeline_query_service_pb2.BrowsePipelinesResponse()
        outgoing_0 = lineage_v1_impact_reporting_service_pb2.GenerateImpactReportRequest(
            annotations=dict(request.annotations),
            context=request.context,
            details=lineage_v1_impact_reporting_service_pb2.GenerateImpactReportRequest.Details(
                filters=dict(request.lineage_node.attributes)
            ),
            reason=request.reason
        )
        response_0 = await deps.clients.lineage_impact_reporting.GenerateImpactReport(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = documents_v1_document_query_service_pb2.ExportDocumentsRequest(
            context=request.context,
            filter=documents_v1_document_query_service_pb2.ExportDocumentsRequest.Filter(
                created_after=request.lineage_node.audit.created_at,
                labels=dict(request.lineage_node.attributes),
                region=request.lineage_node.location.region
            )
        )
        async for chunk_1 in deps.clients.documents_document_query.ExportDocuments(
            outgoing_1,
            timeout=deps.settings.timeout
        ):
            response_1 = chunk_1
        outgoing_2 = metrics_v1_metric_alert_notification_service_pb2.SendMetricAlertTestNoticeRequest(
            context=request.context,
            details=metrics_v1_metric_alert_notification_service_pb2.SendMetricAlertTestNoticeRequest.Details(
                recipient=common_v1_contact_pb2.ContactInfo(email=request.details.approver.email)
            ),
            reason=request.reason
        )
        document_2 = MessageToJson(outgoing_2, preserving_proto_field_name=True)
        outgoing_2 = Parse(
            document_2,
            metrics_v1_metric_alert_notification_service_pb2.SendMetricAlertTestNoticeRequest()
        )
        response_2 = await deps.clients.metrics_metric_alert_notification.SendMetricAlertTestNotice(
            outgoing_2,
            timeout=deps.settings.timeout
        )
        outgoing_3 = pipelines_v1_pipeline_query_service_pb2.BrowsePipelinesRequest()
        outgoing_3.context.CopyFrom(request.context)
        outgoing_3.filter.region = request.lineage_node.location.region
        outgoing_3.filter.created_after.CopyFrom(request.lineage_node.audit.created_at)
        outgoing_3.filter.owner_id = request.lineage_node.manager.user_id
        outgoing_3.filter.labels.update(dict(response_2.metric_alert.parameters))
        merged_3 = pipelines_v1_pipeline_query_service_pb2.BrowsePipelinesRequest()
        merged_3.MergeFrom(outgoing_3)
        outgoing_3.CopyFrom(merged_3)
        response_3 = await deps.clients.pipelines_pipeline_query.BrowsePipelines(
            outgoing_3,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.result.message
        if returned_0_0:
            response.outcome.message = returned_0_0
        returned_2_0 = response_2.metric_alert.owner.display_name
        returned_2_0_part_1 = response.lineage_node.children.add()
        returned_2_0_part_2 = returned_2_0_part_1.children.add()
        if returned_2_0:
            returned_2_0_part_2.manager.display_name = returned_2_0
        returned_3_0 = response_3.result.message
        if returned_3_0:
            response.outcome.message = returned_3_0
        echoed_0 = request.lineage_node_id
        response.lineage_node.lineage_node_id = echoed_0
        echoed_1 = request.lineage_node.parent_id
        response.lineage_node.parent_id = echoed_1
        return response


async def handle_reject_lineage_node(
    deps: Dependencies,
    request: lineage_v1_lineage_node_approval_service_pb2.RejectLineageNodeRequest
) -> lineage_v1_lineage_node_approval_service_pb2.RejectLineageNodeResponse:
    """Rejects a lineage node."""
    response = lineage_v1_lineage_node_approval_service_pb2.RejectLineageNodeResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('RejectLineageNode', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'RejectLineageNode', {'reason': request.reason})
        await deps.repository.save_lineage_node(request.context.tenant_id, request.lineage_node)
        response_0 = analytics_v1_analytics_event_query_service_pb2.FindAnalyticsEventsResponse()
        response_1 = customers_v1_customer_calculation_service_pb2.RecalculateCustomersResponse()
        response_2 = anomalies_v1_anomaly_feedback_validation_service_pb2.PreviewAnomalyFeedbackResponse()
        outgoing_0 = analytics_v1_analytics_event_query_service_pb2.FindAnalyticsEventsRequest(
            context=request.context,
            filter=analytics_v1_analytics_event_query_service_pb2.FindAnalyticsEventsRequest.Filter(
                created_after=request.lineage_node.audit.created_at,
                owner_id=request.details.approver.user_id,
                region=request.lineage_node.location.region
            )
        )
        response_0 = await deps.clients.analytics_analytics_event_query.FindAnalyticsEvents(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = customers_v1_customer_calculation_service_pb2.RecalculateCustomersRequest(
            context=request.context,
            customer=customers_v1_customers_pb2.Customer(
                audit=common_v1_audit_pb2.AuditInfo(created_at=request.lineage_node.audit.created_at),
                primary_address=common_v1_address_pb2.PostalAddress(
                    locality=request.lineage_node.location.locality,
                    recipient=request.lineage_node.location.recipient
                ),
                relationship_manager=identity_v1_refs_pb2.UserRef(user_id=request.lineage_node.manager.user_id)
            )
        )
        registered_1 = cast(
            customers_v1_customer_calculation_service_pb2_grpc.CustomerCalculationServiceStub,
            deps.clients.registry['acme.customers.v1.CustomerCalculationService']
        )
        response_1 = await registered_1.RecalculateCustomers(outgoing_1, timeout=deps.settings.timeout)
        command_2 = LineageNodeApprovalRejectLineageNode2Command(
            context=request.context,
            details_contact_email=response_1.customer.contact.email
        )
        outgoing_2 = to_lineage_node_approval_reject_lineage_node2_command(command_2)
        response_2 = await deps.clients.anomalies_anomaly_feedback_validation.PreviewAnomalyFeedback(
            outgoing_2,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.result.status
        if returned_0_0:
            response.outcome.status = returned_0_0
        returned_1_0 = response_1.customer.audit.updated_at
        if returned_1_0.ListFields():
            response.lineage_node.audit.updated_at.MergeFrom(returned_1_0)
        returned_1_1 = response_1.customer.audit.created_at
        returned_1_1_part_1 = response.lineage_node.children.add()
        if returned_1_1.ListFields():
            returned_1_1_part_1.audit.created_at.MergeFrom(returned_1_1)
        returned_2_0 = response_2.anomaly_feedback.attributes
        returned_2_0_part_1 = response.lineage_node.children.add()
        returned_2_0_part_2 = returned_2_0_part_1.children.add()
        returned_2_0_part_3 = returned_2_0_part_2.children.add()
        returned_2_0_part_3.attributes.update(returned_2_0)
        echoed_0 = request.lineage_node_id
        response.lineage_node.lineage_node_id = echoed_0
        echoed_1 = request.lineage_node.attributes
        response.lineage_node.attributes.update(echoed_1)
        return response


async def handle_submit_lineage_node(
    deps: Dependencies,
    request: lineage_v1_lineage_node_approval_service_pb2.SubmitLineageNodeRequest
) -> lineage_v1_lineage_node_approval_service_pb2.SubmitLineageNodeResponse:
    """Submits a lineage node."""
    response = lineage_v1_lineage_node_approval_service_pb2.SubmitLineageNodeResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('SubmitLineageNode', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'SubmitLineageNode', {'reason': request.reason})
        await deps.repository.save_lineage_node(request.context.tenant_id, request.lineage_node)
        response_0 = lineage_v1_lineage_edge_sync_service_pb2.ReconcileLineageEdgesResponse()
        response_1 = customers_v1_consent_record_validation_service_pb2.ValidateConsentRecordResponse()
        outgoing_0 = lineage_v1_lineage_edge_sync_service_pb2.ReconcileLineageEdgesRequest(
            annotations=dict(request.annotations),
            context=request.context,
            lineage_edge=lineage_v1_lineage_pb2.LineageEdge(
                attributes=dict(request.lineage_node.attributes),
                subject=lineage_v1_refs_pb2.ImpactRef(display_name=request.lineage_node.manager.display_name)
            )
        )
        response_0 = await deps.clients.lineage_lineage_edge_sync.ReconcileLineageEdges(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = customers_v1_consent_record_validation_service_pb2.ValidateConsentRecordRequest(
            consent_record=customers_v1_customers_pb2.ConsentRecord(
                correlation_id=response_0.lineage_edge.correlation_id,
                kind=response_0.lineage_edge.kind,
                sequence=response_0.lineage_edge.sequence,
                subject=customers_v1_refs_pb2.HouseholdRef(display_name=request.details.approver.display_name)
            ),
            context=request.context
        )
        send_1 = partial(
            deps.clients.customers_consent_record_validation.ValidateConsentRecord,
            timeout=deps.settings.timeout
        )
        response_1 = await send_1(outgoing_1)
        returned_0_0 = response_0.outcome.effective_at
        if returned_0_0.ListFields():
            response.outcome.effective_at.MergeFrom(returned_0_0)
        returned_0_1 = response_0.result.reference_ids
        response.result.reference_ids.extend(returned_0_1)
        returned_1_0 = response_1.consent_record.subject.display_name
        if returned_1_0:
            response.lineage_node.manager.display_name = returned_1_0
        returned_1_1 = response_1.consent_record.attributes
        response.lineage_node.attributes.update(returned_1_1)
        echoed_0 = request.lineage_node_id
        response.lineage_node.lineage_node_id = echoed_0
        echoed_1 = request.lineage_node.parent_id
        response.lineage_node.parent_id = echoed_1
        return response
