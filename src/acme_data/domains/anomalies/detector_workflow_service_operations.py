"""Functional operations behind DetectorWorkflowService."""

from __future__ import annotations

from functools import partial
from typing import Any
import logging

from acme.anomalies.v1 import anomalies_pb2 as anomalies_v1_anomalies_pb2
from acme.anomalies.v1 import (
    anomaly_feedback_approval_service_pb2 as anomalies_v1_anomaly_feedback_approval_service_pb2,
)
from acme.anomalies.v1 import anomaly_service_pb2 as anomalies_v1_anomaly_service_pb2
from acme.anomalies.v1 import anomaly_workflow_service_pb2 as anomalies_v1_anomaly_workflow_service_pb2
from acme.anomalies.v1 import detector_workflow_service_pb2 as anomalies_v1_detector_workflow_service_pb2
from acme.authorization.v1 import (
    access_policy_validation_service_pb2 as authorization_v1_access_policy_validation_service_pb2,
)
from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.datasets.v1 import data_schema_validation_service_pb2 as datasets_v1_data_schema_validation_service_pb2
from acme.datasets.v1 import dataset_validation_service_pb2 as datasets_v1_dataset_validation_service_pb2
from acme.datasets.v1 import dataset_version_query_service_pb2 as datasets_v1_dataset_version_query_service_pb2
from acme.datasets.v1 import datasets_pb2 as datasets_v1_datasets_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.learning.v1 import course_service_pb2 as learning_v1_course_service_pb2
from acme.learning.v1 import learning_pb2 as learning_v1_learning_pb2
from acme.lineage.v1 import lineage_edge_import_service_pb2 as lineage_v1_lineage_edge_import_service_pb2
from acme.lineage.v1 import lineage_edge_sync_service_pb2 as lineage_v1_lineage_edge_sync_service_pb2
from acme.lineage.v1 import lineage_node_approval_service_pb2 as lineage_v1_lineage_node_approval_service_pb2
from acme.lineage.v1 import lineage_node_sync_service_pb2 as lineage_v1_lineage_node_sync_service_pb2
from acme.lineage.v1 import lineage_pb2 as lineage_v1_lineage_pb2
from acme.lineage.v1 import refs_pb2 as lineage_v1_refs_pb2
from acme.telehealth.v1 import telehealth_pb2 as telehealth_v1_telehealth_pb2
from acme.telehealth.v1 import video_visit_service_pb2 as telehealth_v1_video_visit_service_pb2

from acme_data.domains.anomalies.adapters import DetectorWorkflowAdvanceDetectorWorkflow1Adapter
from acme_data.domains.anomalies.dependencies import Dependencies
from acme_data.platform.rpc import async_messages
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


async def handle_advance_detector_workflow(
    deps: Dependencies,
    request: anomalies_v1_detector_workflow_service_pb2.AdvanceDetectorWorkflowRequest
) -> anomalies_v1_detector_workflow_service_pb2.AdvanceDetectorWorkflowResponse:
    """Advances a detector."""
    response = anomalies_v1_detector_workflow_service_pb2.AdvanceDetectorWorkflowResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('AdvanceDetectorWorkflow', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'AdvanceDetectorWorkflow', {'reason': request.reason})
        await deps.repository.save_detector(request.context.tenant_id, request.detector)
        response_0 = telehealth_v1_video_visit_service_pb2.CreateVideoVisitResponse()
        response_1 = lineage_v1_lineage_node_approval_service_pb2.SubmitLineageNodeResponse()
        outgoing_0 = telehealth_v1_video_visit_service_pb2.CreateVideoVisitRequest(
            context=request.context,
            video_visit=telehealth_v1_telehealth_pb2.VideoVisit(
                audit=common_v1_audit_pb2.AuditInfo(updated_at=request.detector.audit.updated_at),
                organizer=identity_v1_refs_pb2.UserRef(display_name=request.detector.owner.display_name),
                participants=[
                    telehealth_v1_telehealth_pb2.VideoVisitParticipant(
                        contact=common_v1_contact_pb2.ContactInfo(
                            name=request.details.notify.name,
                            preferred_channel=request.details.notify.preferred_channel
                        )
                    )
                ]
            )
        )
        response_0 = await deps.clients.telehealth_video_visit.CreateVideoVisit(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = lineage_v1_lineage_node_approval_service_pb2.SubmitLineageNodeRequest(
            context=request.context,
            lineage_node=lineage_v1_lineage_pb2.LineageNode(
                children=[
                    lineage_v1_lineage_pb2.LineageNode(
                        children=[
                            lineage_v1_lineage_pb2.LineageNode(
                                audit=common_v1_audit_pb2.AuditInfo(updated_by=response_0.video_visit.audit.updated_by)
                            )
                        ]
                    )
                ]
            )
        )
        response_1 = await DetectorWorkflowAdvanceDetectorWorkflow1Adapter(
            deps.clients.lineage_lineage_node_approval,
            deps.settings.timeout
        )(outgoing_1)
        returned_0_0 = response_0.result.correlation_id
        if returned_0_0:
            response.result.correlation_id = returned_0_0
        returned_0_1 = response_0.video_visit.organizer.email
        if returned_0_1:
            response.detector.owner.email = returned_0_1
        returned_1_0 = response_1.result.status
        if returned_1_0:
            response.outcome.status = returned_1_0
        returned_1_1 = response_1.lineage_node.audit.updated_at
        if returned_1_1.ListFields():
            response.detector.audit.updated_at.MergeFrom(returned_1_1)
        echoed_0 = request.detector_id
        response.detector.detector_id = echoed_0
        echoed_1 = request.detector.name
        response.detector.name = echoed_1
        return response


async def handle_cancel_detector_workflow(
    deps: Dependencies,
    request: anomalies_v1_detector_workflow_service_pb2.CancelDetectorWorkflowRequest
) -> anomalies_v1_detector_workflow_service_pb2.CancelDetectorWorkflowResponse:
    """Cancels a detector."""
    response = anomalies_v1_detector_workflow_service_pb2.CancelDetectorWorkflowResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('CancelDetectorWorkflow', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'CancelDetectorWorkflow', {'reason': request.reason})
        await deps.repository.save_detector(request.context.tenant_id, request.detector)
        response_0 = lineage_v1_lineage_node_sync_service_pb2.SyncLineageNodesResponse()
        response_1 = anomalies_v1_anomaly_workflow_service_pb2.CancelAnomalyWorkflowResponse()
        outgoing_0 = lineage_v1_lineage_node_sync_service_pb2.SyncLineageNodesRequest(
            context=request.context,
            lineage_node=lineage_v1_lineage_pb2.LineageNode(
                children=[
                    lineage_v1_lineage_pb2.LineageNode(
                        children=[
                            lineage_v1_lineage_pb2.LineageNode(
                                audit=common_v1_audit_pb2.AuditInfo(created_at=request.detector.audit.created_at)
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
        outgoing_1 = anomalies_v1_anomaly_workflow_service_pb2.CancelAnomalyWorkflowRequest(
            anomaly=anomalies_v1_anomalies_pb2.Anomaly(
                audit=common_v1_audit_pb2.AuditInfo(updated_at=request.detector.audit.updated_at)
            ),
            context=request.context,
            details=anomalies_v1_anomaly_workflow_service_pb2.CancelAnomalyWorkflowRequest.Details(
                notify=common_v1_contact_pb2.ContactInfo(
                    email=request.detector.owner.email,
                    name=request.details.notify.name
                )
            )
        )
        response_1 = await deps.clients.anomalies_anomaly_workflow.CancelAnomalyWorkflow(
            outgoing_1,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.result.message
        if returned_0_0:
            response.result.message = returned_0_0
        returned_1_0 = response_1.anomaly.customer.version
        if returned_1_0:
            response.detector.version = returned_1_0
        returned_1_1 = response_1.anomaly.assignee.email
        if returned_1_1:
            response.detector.owner.email = returned_1_1
        echoed_0 = request.detector_id
        response.detector.detector_id = echoed_0
        echoed_1 = request.detector.name
        response.detector.name = echoed_1
        return response


async def handle_inspect_detector_workflow(
    deps: Dependencies,
    request: anomalies_v1_detector_workflow_service_pb2.InspectDetectorWorkflowRequest
) -> anomalies_v1_detector_workflow_service_pb2.InspectDetectorWorkflowResponse:
    """Returns a detector."""
    response = anomalies_v1_detector_workflow_service_pb2.InspectDetectorWorkflowResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('InspectDetectorWorkflow', extra={'fields': {'domain': 'anomalies'}})
        await deps.repository.audit(request.context.tenant_id, 'InspectDetectorWorkflow', {})
        response_0 = datasets_v1_dataset_version_query_service_pb2.FindDatasetVersionsResponse()
        response_1 = datasets_v1_dataset_validation_service_pb2.CheckDatasetEligibilityResponse()
        outgoing_0 = datasets_v1_dataset_version_query_service_pb2.FindDatasetVersionsRequest(
            context=request.context,
            filter=datasets_v1_dataset_version_query_service_pb2.FindDatasetVersionsRequest.Filter(
                owner_id=request.detector_id
            )
        )
        response_0 = await deps.clients.datasets_dataset_version_query.FindDatasetVersions(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        fields_1: dict[str, Any] = {
            'context': request.context,
            'dataset': {
                'components': {'primary': {'component_id': response_0.result.correlation_id}},
                'owner': {'user_id': request.context.actor.user_id}
            },
            'details': {'contact': {'email': request.context.actor.email}, 'locale': request.context.locale}
        }
        outgoing_1 = datasets_v1_dataset_validation_service_pb2.CheckDatasetEligibilityRequest(**fields_1)
        response_1 = await deps.clients.datasets_dataset_validation.CheckDatasetEligibility(
            outgoing_1,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.result.reference_ids
        response.result.reference_ids.extend(returned_0_0)
        returned_0_1 = response_0.result.details
        response.result.details.update(returned_0_1)
        returned_1_0 = response_1.dataset.audit.etag
        if returned_1_0:
            response.detector.audit.etag = returned_1_0
        returned_1_1 = response_1.dataset.audit.created_by
        if returned_1_1:
            response.detector.audit.created_by = returned_1_1
        echoed_0 = request.detector_id
        response.detector.detector_id = echoed_0
        return response


async def handle_list_detector_workflows(
    deps: Dependencies,
    request: anomalies_v1_detector_workflow_service_pb2.ListDetectorWorkflowsRequest
) -> anomalies_v1_detector_workflow_service_pb2.ListDetectorWorkflowsResponse:
    """Lists detectors a page at a time."""
    response = anomalies_v1_detector_workflow_service_pb2.ListDetectorWorkflowsResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('ListDetectorWorkflows', extra={'fields': {'order_by': request.order_by}})
        await deps.repository.audit(request.context.tenant_id, 'ListDetectorWorkflows', {'order_by': request.order_by})
        response_0 = learning_v1_course_service_pb2.CloneCourseResponse()
        outgoing_0 = learning_v1_course_service_pb2.CloneCourseRequest(
            context=request.context,
            course=learning_v1_learning_pb2.Course(
                address=common_v1_address_pb2.PostalAddress(region=request.filter.region)
            )
        )
        response_0 = await deps.clients.learning_course.CloneCourse(outgoing_0, timeout=deps.settings.timeout)
        returned_0_0 = response_0.result.status
        if returned_0_0:
            response.result.status = returned_0_0
        return response


async def handle_retry_detector_workflow(
    deps: Dependencies,
    request: anomalies_v1_detector_workflow_service_pb2.RetryDetectorWorkflowRequest
) -> anomalies_v1_detector_workflow_service_pb2.RetryDetectorWorkflowResponse:
    """Retrys a detector."""
    response = anomalies_v1_detector_workflow_service_pb2.RetryDetectorWorkflowResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('RetryDetectorWorkflow', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'RetryDetectorWorkflow', {'reason': request.reason})
        await deps.repository.save_detector(request.context.tenant_id, request.detector)
        response_0 = datasets_v1_data_schema_validation_service_pb2.CheckDataSchemaEligibilityResponse()
        response_1 = anomalies_v1_anomaly_feedback_approval_service_pb2.CommentAnomalyFeedbackApprovalResponse()
        outgoing_0 = datasets_v1_data_schema_validation_service_pb2.CheckDataSchemaEligibilityRequest(
            context=request.context,
            data_schema=datasets_v1_datasets_pb2.DataSchema(
                children=[
                    datasets_v1_datasets_pb2.DataSchema(
                        children=[
                            datasets_v1_datasets_pb2.DataSchema(
                                audit=common_v1_audit_pb2.AuditInfo(etag=request.detector.audit.etag)
                            )
                        ]
                    )
                ]
            )
        )
        response_0 = await deps.clients.datasets_data_schema_validation.CheckDataSchemaEligibility(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = anomalies_v1_anomaly_feedback_approval_service_pb2.CommentAnomalyFeedbackApprovalRequest()
        outgoing_1.context.CopyFrom(request.context)
        outgoing_1.anomaly_feedback.subject.display_name = response_0.data_schema.manager.display_name
        merged_1 = anomalies_v1_anomaly_feedback_approval_service_pb2.CommentAnomalyFeedbackApprovalRequest()
        merged_1.MergeFrom(outgoing_1)
        outgoing_1.CopyFrom(merged_1)
        response_1 = await deps.clients.anomalies_anomaly_feedback_approval.CommentAnomalyFeedbackApproval(
            outgoing_1,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.result.status
        if returned_0_0:
            response.outcome.status = returned_0_0
        returned_1_0 = response_1.result.details
        response.result.details.update(returned_1_0)
        echoed_0 = request.detector_id
        response.detector.detector_id = echoed_0
        echoed_1 = request.detector.priority
        response.detector.priority = echoed_1
        return response


async def handle_signal_detector_workflow(
    deps: Dependencies,
    request: anomalies_v1_detector_workflow_service_pb2.SignalDetectorWorkflowRequest
) -> anomalies_v1_detector_workflow_service_pb2.SignalDetectorWorkflowResponse:
    """Signals a detector."""
    response = anomalies_v1_detector_workflow_service_pb2.SignalDetectorWorkflowResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('SignalDetectorWorkflow', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'SignalDetectorWorkflow', {'reason': request.reason})
        await deps.repository.save_detector(request.context.tenant_id, request.detector)
        response_0 = authorization_v1_access_policy_validation_service_pb2.NormalizeAccessPolicyResponse()
        outgoing_0 = authorization_v1_access_policy_validation_service_pb2.NormalizeAccessPolicyRequest()
        outgoing_0.context.CopyFrom(request.context)
        if request.detector.WhichOneof('action') == 'discount':
            outgoing_0.access_policy.discount.percent = request.detector.discount.percent
        outgoing_0.access_policy.audit.etag = request.detector.audit.etag
        outgoing_0.details.contact.email = request.detector.owner.email
        outgoing_0.access_policy.owner.email = request.details.notify.email
        response_0 = await deps.clients.authorization_access_policy_validation.NormalizeAccessPolicy(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.outcome.message
        if returned_0_0:
            response.result.message = returned_0_0
        returned_0_1 = response_0.access_policy.owner.user_id
        if returned_0_1:
            response.detector.owner.user_id = returned_0_1
        echoed_0 = request.detector_id
        response.detector.detector_id = echoed_0
        echoed_1 = request.detector.priority
        response.detector.priority = echoed_1
        return response


async def handle_start_detector_workflow(
    deps: Dependencies,
    request: anomalies_v1_detector_workflow_service_pb2.StartDetectorWorkflowRequest
) -> anomalies_v1_detector_workflow_service_pb2.StartDetectorWorkflowResponse:
    """Starts a detector."""
    response = anomalies_v1_detector_workflow_service_pb2.StartDetectorWorkflowResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('StartDetectorWorkflow', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'StartDetectorWorkflow', {'reason': request.reason})
        await deps.repository.save_detector(request.context.tenant_id, request.detector)
        response_0 = anomalies_v1_anomaly_feedback_approval_service_pb2.ApproveAnomalyFeedbackResponse()
        response_1 = anomalies_v1_anomaly_service_pb2.BatchCreateAnomaliesResponse()
        response_2 = lineage_v1_lineage_edge_sync_service_pb2.ResolveLineageEdgeConflictResponse()
        response_3 = lineage_v1_lineage_edge_import_service_pb2.RetryLineageEdgeImportResponse()
        outgoing_0 = anomalies_v1_anomaly_feedback_approval_service_pb2.ApproveAnomalyFeedbackRequest(
            context=request.context,
            details=anomalies_v1_anomaly_feedback_approval_service_pb2.ApproveAnomalyFeedbackRequest.Details(
                approver=identity_v1_refs_pb2.UserRef(email=request.detector.owner.email)
            )
        )
        response_0 = await deps.clients.anomalies_anomaly_feedback_approval.ApproveAnomalyFeedback(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = anomalies_v1_anomaly_service_pb2.BatchCreateAnomaliesRequest(
            context=request.context,
            header=anomalies_v1_anomaly_service_pb2.BatchCreateAnomaliesRequest.StreamHeader(
                submitted_by=common_v1_contact_pb2.ContactInfo(
                    preferred_channel=request.details.notify.preferred_channel
                )
            )
        )
        response_1 = await deps.clients.anomalies_anomaly.BatchCreateAnomalies(
            async_messages((outgoing_1,)),
            timeout=deps.settings.timeout
        )
        outgoing_2 = lineage_v1_lineage_edge_sync_service_pb2.ResolveLineageEdgeConflictRequest()
        outgoing_2.context.CopyFrom(request.context)
        if request.detector.WhichOneof('action') == 'block':
            outgoing_2.reason = request.detector.block.reason
        outgoing_2.lineage_edge.source = response_0.anomaly_feedback.source
        outgoing_2.lineage_edge.subject.priority = request.detector.priority
        response_2 = await deps.clients.lineage_lineage_edge_sync.ResolveLineageEdgeConflict(
            outgoing_2,
            timeout=deps.settings.timeout
        )
        outgoing_3 = lineage_v1_lineage_edge_import_service_pb2.RetryLineageEdgeImportRequest(
            context=request.context,
            details=lineage_v1_lineage_edge_import_service_pb2.RetryLineageEdgeImportRequest.Details(
                notify=common_v1_contact_pb2.ContactInfo(
                    name=request.details.notify.name,
                    phone=request.details.notify.phone
                )
            ),
            lineage_edge=lineage_v1_lineage_pb2.LineageEdge(
                subject=lineage_v1_refs_pb2.ImpactRef(
                    display_name=response_2.lineage_edge.subject.display_name,
                    impact_id=response_2.lineage_edge.subject.impact_id
                )
            )
        )
        send_3 = partial(deps.clients.lineage_lineage_edge_import.RetryLineageEdgeImport, timeout=deps.settings.timeout)
        response_3 = await send_3(outgoing_3)
        returned_0_0 = response_0.outcome.next_steps
        response.outcome.next_steps.extend(returned_0_0)
        returned_0_1 = response_0.outcome.reference_id
        if returned_0_1:
            response.outcome.reference_id = returned_0_1
        returned_2_0 = response_2.lineage_edge.subject.display_name
        if returned_2_0:
            response.detector.owner.display_name = returned_2_0
        returned_2_1 = response_2.outcome.reference_id
        if returned_2_1:
            response.outcome.reference_id = returned_2_1
        returned_3_0 = response_3.result.reference_ids
        response.result.reference_ids.extend(returned_3_0)
        returned_3_1 = response_3.lineage_edge.subject.priority
        if returned_3_1:
            response.detector.priority = returned_3_1
        echoed_0 = request.detector_id
        response.detector.detector_id = echoed_0
        echoed_1 = request.detector.description
        response.detector.description = echoed_1
        return response
