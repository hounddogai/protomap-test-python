"""Functional operations behind LabelSetApprovalService."""

from __future__ import annotations

from functools import partial
from typing import cast
import logging

from google.protobuf.any_pb2 import Any as AnyMessage
from google.protobuf.json_format import MessageToDict
from google.protobuf.json_format import ParseDict

from acme.admissions.v1 import admission_calculation_service_pb2 as admissions_v1_admission_calculation_service_pb2
from acme.admissions.v1 import admissions_pb2 as admissions_v1_admissions_pb2
from acme.anomalies.v1 import (
    anomaly_feedback_approval_service_pb2 as anomalies_v1_anomaly_feedback_approval_service_pb2,
)
from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.customers.v1 import refs_pb2 as customers_v1_refs_pb2
from acme.documents.v1 import document_service_pb2 as documents_v1_document_service_pb2
from acme.featurestore.v1 import feature_value_sync_service_pb2 as featurestore_v1_feature_value_sync_service_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.labeling.v1 import annotation_approval_service_pb2 as labeling_v1_annotation_approval_service_pb2
from acme.labeling.v1 import annotation_reporting_service_pb2 as labeling_v1_annotation_reporting_service_pb2
from acme.labeling.v1 import label_set_approval_service_pb2 as labeling_v1_label_set_approval_service_pb2
from acme.labeling.v1 import label_set_lifecycle_service_pb2 as labeling_v1_label_set_lifecycle_service_pb2
from acme.labeling.v1 import label_set_sync_service_pb2 as labeling_v1_label_set_sync_service_pb2
from acme.labeling.v1 import labeling_pb2 as labeling_v1_labeling_pb2
from acme.labeling.v1 import labeling_task_approval_service_pb2 as labeling_v1_labeling_task_approval_service_pb2
from acme.labeling.v1 import labeling_task_query_service_pb2 as labeling_v1_labeling_task_query_service_pb2
from acme.labeling.v1 import labeling_task_workflow_service_pb2 as labeling_v1_labeling_task_workflow_service_pb2
from acme.labeling.v1 import refs_pb2 as labeling_v1_refs_pb2
from acme.lineage.v1 import impact_sync_service_pb2 as lineage_v1_impact_sync_service_pb2
from acme.lineage.v1 import lineage_pb2 as lineage_v1_lineage_pb2
from acme.modelregistry.v1 import (
    model_version_workflow_service_pb2 as modelregistry_v1_model_version_workflow_service_pb2,
)
from acme.modelregistry.v1 import modelregistry_pb2 as modelregistry_v1_modelregistry_pb2
from acme.modelregistry.v1 import (
    registered_model_approval_service_pb2 as modelregistry_v1_registered_model_approval_service_pb2,
)
from acme.search.v1 import search_index_query_service_pb2 as search_v1_search_index_query_service_pb2

from acme_data.domains.labeling import hooks
from acme_data.domains.labeling.dependencies import Dependencies
from acme_data.domains.labeling.models import LabelSetApprovalRejectLabelSet1Command
from acme_data.domains.labeling.models import LabelSetApprovalRejectLabelSet2Command
from acme_data.domains.labeling.models import to_label_set_approval_reject_label_set1_command
from acme_data.domains.labeling.models import to_label_set_approval_reject_label_set2_command
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import run_steps
from acme_data.platform.tenancy import tenant_id
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


async def handle_approve_label_set(
    deps: Dependencies,
    request: labeling_v1_label_set_approval_service_pb2.ApproveLabelSetRequest
) -> labeling_v1_label_set_approval_service_pb2.ApproveLabelSetResponse:
    """Approves a label set."""
    response = labeling_v1_label_set_approval_service_pb2.ApproveLabelSetResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('ApproveLabelSet', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'ApproveLabelSet', {'reason': request.reason})
        await deps.repository.save_label_set(request.context.tenant_id, request.label_set)
        response_0 = labeling_v1_labeling_task_approval_service_pb2.ListPendingLabelingTasksResponse()
        response_1 = labeling_v1_labeling_task_workflow_service_pb2.ListLabelingTaskWorkflowsResponse()
        outgoing_0 = labeling_v1_labeling_task_approval_service_pb2.ListPendingLabelingTasksRequest(
            context=request.context,
            filter=labeling_v1_labeling_task_approval_service_pb2.ListPendingLabelingTasksRequest.Filter(
                created_after=request.label_set.audit.updated_at,
                labels=dict(request.annotations),
                owner_id=request.label_set.manager.user_id,
                region=request.label_set.location.region
            )
        )
        response_0 = await deps.clients.labeling_labeling_task_approval.ListPendingLabelingTasks(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = labeling_v1_labeling_task_workflow_service_pb2.ListLabelingTaskWorkflowsRequest()
        outgoing_1.context.CopyFrom(request.context)
        outgoing_1.filter.region = request.label_set.location.region
        outgoing_1.context.tenant_id = tenant_id.get()
        response_1 = await deps.clients.labeling_labeling_task_workflow.ListLabelingTaskWorkflows(
            outgoing_1,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.result.correlation_id
        if returned_0_0:
            response.result.correlation_id = returned_0_0
        returned_1_0 = response_1.result.details
        response.result.details.update(returned_1_0)
        echoed_0 = request.label_set_id
        response.label_set.label_set_id = echoed_0
        echoed_1 = request.label_set.depth
        response.label_set.depth = echoed_1
        return response


async def handle_comment_label_set_approval(
    deps: Dependencies,
    request: labeling_v1_label_set_approval_service_pb2.CommentLabelSetApprovalRequest
) -> labeling_v1_label_set_approval_service_pb2.CommentLabelSetApprovalResponse:
    """Comments a label set."""
    response = labeling_v1_label_set_approval_service_pb2.CommentLabelSetApprovalResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('CommentLabelSetApproval', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'CommentLabelSetApproval', {'reason': request.reason})
        await deps.repository.save_label_set(request.context.tenant_id, request.label_set)
        response_0 = labeling_v1_label_set_lifecycle_service_pb2.ScheduleLabelSetExpiryResponse()
        response_1 = labeling_v1_labeling_task_query_service_pb2.BrowseLabelingTasksResponse()
        outgoing_0 = labeling_v1_label_set_lifecycle_service_pb2.ScheduleLabelSetExpiryRequest(
            context=request.context,
            label_set=labeling_v1_labeling_pb2.LabelSet(
                children=[
                    labeling_v1_labeling_pb2.LabelSet(
                        children=[
                            labeling_v1_labeling_pb2.LabelSet(
                                audit=common_v1_audit_pb2.AuditInfo(created_at=request.label_set.audit.created_at),
                                location=common_v1_address_pb2.PostalAddress(
                                    lines=list(request.label_set.location.lines),
                                    locality=request.label_set.location.locality
                                )
                            )
                        ]
                    )
                ]
            )
        )
        response_0 = await deps.clients.labeling_label_set_lifecycle.ScheduleLabelSetExpiry(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = labeling_v1_labeling_task_query_service_pb2.BrowseLabelingTasksRequest(
            context=request.context,
            filter=labeling_v1_labeling_task_query_service_pb2.BrowseLabelingTasksRequest.Filter(
                created_after=request.label_set.audit.created_at,
                region=request.label_set.location.region
            )
        )
        steps_1 = [
            partial(
                deps.clients.labeling_labeling_task_query.BrowseLabelingTasks,
                outgoing_1,
                timeout=deps.settings.timeout
            )
        ]
        results_1 = await run_steps(steps_1)
        response_1 = results_1[-1]
        returned_0_0 = response_0.label_set.manager.display_name
        returned_0_0_part_1 = response.label_set.children.add()
        if returned_0_0:
            returned_0_0_part_1.manager.display_name = returned_0_0
        returned_1_0 = response_1.result.status
        if returned_1_0:
            response.outcome.status = returned_1_0
        echoed_0 = request.label_set_id
        response.label_set.label_set_id = echoed_0
        echoed_1 = request.details.effective_at
        response.outcome.effective_at.CopyFrom(echoed_1)
        return response


async def handle_delegate_label_set_approval(
    deps: Dependencies,
    request: labeling_v1_label_set_approval_service_pb2.DelegateLabelSetApprovalRequest
) -> labeling_v1_label_set_approval_service_pb2.DelegateLabelSetApprovalResponse:
    """Delegates a label set."""
    response = labeling_v1_label_set_approval_service_pb2.DelegateLabelSetApprovalResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('DelegateLabelSetApproval', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'DelegateLabelSetApproval', {'reason': request.reason})
        await deps.repository.save_label_set(request.context.tenant_id, request.label_set)
        response_0 = labeling_v1_annotation_approval_service_pb2.CommentAnnotationApprovalResponse()
        response_1 = labeling_v1_label_set_sync_service_pb2.ResolveLabelSetConflictResponse()
        response_2 = lineage_v1_impact_sync_service_pb2.PullImpactsResponse()
        response_3 = modelregistry_v1_model_version_workflow_service_pb2.CancelModelVersionWorkflowResponse()
        outgoing_0 = labeling_v1_annotation_approval_service_pb2.CommentAnnotationApprovalRequest(
            context=request.context,
            details=labeling_v1_annotation_approval_service_pb2.CommentAnnotationApprovalRequest.Details(
                approver=identity_v1_refs_pb2.UserRef(
                    display_name=request.label_set.manager.display_name,
                    email=request.details.approver.email,
                    user_id=request.label_set.manager.user_id
                )
            )
        )
        response_0 = await deps.clients.labeling_annotation_approval.CommentAnnotationApproval(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = labeling_v1_label_set_sync_service_pb2.ResolveLabelSetConflictRequest(
            context=request.context,
            label_set=labeling_v1_labeling_pb2.LabelSet(
                children=[
                    labeling_v1_labeling_pb2.LabelSet(
                        children=[
                            labeling_v1_labeling_pb2.LabelSet(
                                audit=common_v1_audit_pb2.AuditInfo(updated_by=request.label_set.audit.updated_by),
                                location=common_v1_address_pb2.PostalAddress(
                                    locality=request.label_set.location.locality
                                ),
                                manager=identity_v1_refs_pb2.UserRef(email=request.details.approver.email)
                            )
                        ],
                        location=common_v1_address_pb2.PostalAddress(region=request.label_set.location.region)
                    )
                ]
            )
        )
        response_1 = cast(labeling_v1_label_set_sync_service_pb2.ResolveLabelSetConflictResponse, await deps.bus.request(
            'acme.labeling.v1.LabelSetApprovalService/DelegateLabelSetApproval/1', outgoing_1, deps.settings.timeout,
        ))
        outgoing_2 = lineage_v1_impact_sync_service_pb2.PullImpactsRequest(
            context=request.context,
            impact=lineage_v1_lineage_pb2.Impact(
                assignee=identity_v1_refs_pb2.UserRef(user_id=request.label_set.manager.user_id),
                customer=customers_v1_refs_pb2.CustomerRef(display_name=response_1.label_set.manager.display_name)
            )
        )
        response_2 = await deps.clients.lineage_impact_sync.PullImpacts(outgoing_2, timeout=deps.settings.timeout)
        outgoing_3 = modelregistry_v1_model_version_workflow_service_pb2.CancelModelVersionWorkflowRequest(
            context=request.context,
            details=modelregistry_v1_model_version_workflow_service_pb2.CancelModelVersionWorkflowRequest.Details(
                notify=common_v1_contact_pb2.ContactInfo(phone=response_2.impact.requester.phone)
            ),
            model_version=modelregistry_v1_modelregistry_pb2.ModelVersion(
                subject=customers_v1_refs_pb2.CustomerRef(customer_id=response_2.impact.customer.customer_id)
            )
        )
        method_name_3 = 'CancelModelVersionWorkflow'
        response_3 = await getattr(
            deps.clients.modelregistry_model_version_workflow,
            method_name_3
        )(outgoing_3, timeout=deps.settings.timeout)
        returned_0_0 = response_0.result.reference_ids
        response.result.reference_ids.extend(returned_0_0)
        returned_0_1 = response_0.outcome.status
        if returned_0_1:
            response.outcome.status = returned_0_1
        returned_1_0 = response_1.label_set.location.region
        returned_1_0_part_1 = response.label_set.children.add()
        if returned_1_0:
            returned_1_0_part_1.location.region = returned_1_0
        returned_2_0 = response_2.result.status
        if returned_2_0:
            response.outcome.status = returned_2_0
        returned_3_0 = response_3.model_version.correlation_id
        if returned_3_0:
            response.result.correlation_id = returned_3_0
        returned_3_1 = response_3.model_version.attributes
        returned_3_1_part_1 = response.label_set.children.add()
        returned_3_1_part_2 = returned_3_1_part_1.children.add()
        returned_3_1_part_3 = returned_3_1_part_2.children.add()
        returned_3_1_part_3.attributes.update(returned_3_1)
        echoed_0 = request.label_set_id
        response.label_set.label_set_id = echoed_0
        echoed_1 = request.label_set.parent_id
        response.label_set.parent_id = echoed_1
        return response


async def handle_escalate_label_set(
    deps: Dependencies,
    request: labeling_v1_label_set_approval_service_pb2.EscalateLabelSetRequest
) -> labeling_v1_label_set_approval_service_pb2.EscalateLabelSetResponse:
    """Escalates a label set."""
    response = labeling_v1_label_set_approval_service_pb2.EscalateLabelSetResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('EscalateLabelSet', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'EscalateLabelSet', {'reason': request.reason})
        await deps.repository.save_label_set(request.context.tenant_id, request.label_set)
        response_0 = labeling_v1_label_set_lifecycle_service_pb2.GetLabelSetLifecycleResponse()
        response_1 = labeling_v1_annotation_reporting_service_pb2.GenerateAnnotationReportResponse()
        outgoing_0 = labeling_v1_label_set_lifecycle_service_pb2.GetLabelSetLifecycleRequest(
            context=request.context,
            label_set_id=request.label_set.label_set_id
        )
        response_0 = await deps.clients.labeling_label_set_lifecycle.GetLabelSetLifecycle(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = labeling_v1_annotation_reporting_service_pb2.GenerateAnnotationReportRequest(
            annotations=dict(request.annotations),
            context=request.context
        )
        document_1 = MessageToDict(outgoing_1, preserving_proto_field_name=True)
        outgoing_1 = ParseDict(
            document_1,
            labeling_v1_annotation_reporting_service_pb2.GenerateAnnotationReportRequest()
        )
        response_1 = await deps.clients.labeling_annotation_reporting.GenerateAnnotationReport(
            outgoing_1,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.label_set.audit.updated_by
        if returned_0_0:
            response.label_set.audit.updated_by = returned_0_0
        returned_1_0 = response_1.result.correlation_id
        if returned_1_0:
            response.result.correlation_id = returned_1_0
        echoed_0 = request.label_set_id
        response.label_set.label_set_id = echoed_0
        echoed_1 = request.label_set.manager
        response.label_set.manager.CopyFrom(echoed_1)
        return response


async def handle_list_pending_label_sets(
    deps: Dependencies,
    request: labeling_v1_label_set_approval_service_pb2.ListPendingLabelSetsRequest
) -> labeling_v1_label_set_approval_service_pb2.ListPendingLabelSetsResponse:
    """Lists label sets a page at a time."""
    response = labeling_v1_label_set_approval_service_pb2.ListPendingLabelSetsResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('ListPendingLabelSets', extra={'fields': {'order_by': request.order_by}})
        await deps.repository.audit(request.context.tenant_id, 'ListPendingLabelSets', {'order_by': request.order_by})
        response_0 = admissions_v1_admission_calculation_service_pb2.CalculateAdmissionResponse()
        outgoing_0 = admissions_v1_admission_calculation_service_pb2.CalculateAdmissionRequest(
            admission=admissions_v1_admissions_pb2.Admission(
                attributes=dict(request.filter.labels),
                occurred_at=request.filter.created_after,
                source=request.filter.owner_id
            ),
            context=request.context,
            details=admissions_v1_admission_calculation_service_pb2.CalculateAdmissionRequest.Details(
                destination=common_v1_address_pb2.PostalAddress(region=request.filter.region)
            )
        )
        response_0 = await deps.clients.admissions_admission_calculation.CalculateAdmission(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.result.correlation_id
        if returned_0_0:
            response.result.correlation_id = returned_0_0
        return response


async def handle_recall_label_set(
    deps: Dependencies,
    request: labeling_v1_label_set_approval_service_pb2.RecallLabelSetRequest
) -> labeling_v1_label_set_approval_service_pb2.RecallLabelSetResponse:
    """Recalls a label set."""
    response = labeling_v1_label_set_approval_service_pb2.RecallLabelSetResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('RecallLabelSet', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'RecallLabelSet', {'reason': request.reason})
        await deps.repository.save_label_set(request.context.tenant_id, request.label_set)
        response_0 = labeling_v1_annotation_approval_service_pb2.SubmitAnnotationResponse()
        response_1 = search_v1_search_index_query_service_pb2.ResolveSearchIndexesResponse()
        outgoing_0 = labeling_v1_annotation_approval_service_pb2.SubmitAnnotationRequest(
            annotation=labeling_v1_labeling_pb2.Annotation(
                subject=labeling_v1_refs_pb2.LabelingTaskRef(display_name=request.details.approver.display_name)
            ),
            context=request.context,
            details=labeling_v1_annotation_approval_service_pb2.SubmitAnnotationRequest.Details(
                approver=identity_v1_refs_pb2.UserRef(
                    display_name=request.label_set.manager.display_name,
                    email=request.label_set.manager.email,
                    user_id=request.label_set.manager.user_id
                )
            )
        )
        response_0 = await deps.clients.labeling_annotation_approval.SubmitAnnotation(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = search_v1_search_index_query_service_pb2.ResolveSearchIndexesRequest(context=request.context)
        envelope_1 = AnyMessage()
        envelope_1.Pack(outgoing_1)
        outgoing_1 = search_v1_search_index_query_service_pb2.ResolveSearchIndexesRequest()
        if not envelope_1.Unpack(outgoing_1):
            raise ValueError("partner envelope contains the wrong request type")
        response_1 = await deps.clients.search_search_index_query.ResolveSearchIndexes(
            outgoing_1,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.result.message
        if returned_0_0:
            response.result.message = returned_0_0
        returned_1_0 = response_1.result.message
        if returned_1_0:
            response.outcome.message = returned_1_0
        returned_1_1 = response_1.result.message
        if returned_1_1:
            response.result.message = returned_1_1
        echoed_0 = request.label_set_id
        response.label_set.label_set_id = echoed_0
        echoed_1 = request.label_set.status
        response.label_set.status = echoed_1
        return response


async def handle_reject_label_set(
    deps: Dependencies,
    request: labeling_v1_label_set_approval_service_pb2.RejectLabelSetRequest
) -> labeling_v1_label_set_approval_service_pb2.RejectLabelSetResponse:
    """Rejects a label set."""
    response = labeling_v1_label_set_approval_service_pb2.RejectLabelSetResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('RejectLabelSet', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'RejectLabelSet', {'reason': request.reason})
        await deps.repository.save_label_set(request.context.tenant_id, request.label_set)
        response_0 = anomalies_v1_anomaly_feedback_approval_service_pb2.EscalateAnomalyFeedbackResponse()
        response_1 = featurestore_v1_feature_value_sync_service_pb2.PushFeatureValueResponse()
        response_2 = modelregistry_v1_registered_model_approval_service_pb2.RecallRegisteredModelResponse()
        outgoing_0 = anomalies_v1_anomaly_feedback_approval_service_pb2.EscalateAnomalyFeedbackRequest(
            context=request.context,
            details=anomalies_v1_anomaly_feedback_approval_service_pb2.EscalateAnomalyFeedbackRequest.Details(
                approver=identity_v1_refs_pb2.UserRef(
                    display_name=request.details.approver.display_name,
                    email=request.details.approver.email,
                    user_id=request.label_set.manager.user_id
                )
            )
        )
        response_0 = await deps.clients.anomalies_anomaly_feedback_approval.EscalateAnomalyFeedback(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        command_1 = LabelSetApprovalRejectLabelSet1Command(
            context=request.context,
            feature_value_subject_dataset_id=response_0.anomaly_feedback.subject.dataset_id,
            feature_value_subject_display_name=response_0.anomaly_feedback.subject.display_name,
            feature_value_kind=response_0.anomaly_feedback.kind
        )
        outgoing_1 = to_label_set_approval_reject_label_set1_command(command_1)
        response_1 = await deps.clients.featurestore_feature_value_sync.PushFeatureValue(
            outgoing_1,
            timeout=deps.settings.timeout
        )
        command_2 = LabelSetApprovalRejectLabelSet2Command.model_validate(
            {'context': request.context, 'registered_model_audit_updated_by': request.label_set.audit.updated_by}
        )
        outgoing_2 = to_label_set_approval_reject_label_set2_command(command_2)
        response_2 = await deps.clients.modelregistry_registered_model_approval.RecallRegisteredModel(
            outgoing_2,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.result.status
        if returned_0_0:
            response.outcome.status = returned_0_0
        returned_1_0 = response_1.feature_value.subject.display_name
        returned_1_0_part_1 = response.label_set.children.add()
        returned_1_0_part_2 = returned_1_0_part_1.children.add()
        if returned_1_0:
            returned_1_0_part_2.manager.display_name = returned_1_0
        returned_1_1 = response_1.outcome.message
        if returned_1_1:
            response.result.message = returned_1_1
        returned_2_0 = response_2.result.status
        if returned_2_0:
            response.outcome.status = returned_2_0
        returned_2_1 = response_2.outcome.reference_id
        if returned_2_1:
            response.outcome.reference_id = returned_2_1
        echoed_0 = request.label_set_id
        response.label_set.label_set_id = echoed_0
        echoed_1 = request.details.effective_at
        response.outcome.effective_at.CopyFrom(echoed_1)
        return response


async def handle_submit_label_set(
    deps: Dependencies,
    request: labeling_v1_label_set_approval_service_pb2.SubmitLabelSetRequest
) -> labeling_v1_label_set_approval_service_pb2.SubmitLabelSetResponse:
    """Submits a label set."""
    response = labeling_v1_label_set_approval_service_pb2.SubmitLabelSetResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('SubmitLabelSet', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'SubmitLabelSet', {'reason': request.reason})
        await deps.repository.save_label_set(request.context.tenant_id, request.label_set)
        response_0 = documents_v1_document_service_pb2.WatchDocumentsResponse()
        response_1 = labeling_v1_label_set_lifecycle_service_pb2.ScheduleLabelSetExpiryResponse()
        outgoing_0 = documents_v1_document_service_pb2.WatchDocumentsRequest(
            context=request.context,
            subscriber=common_v1_contact_pb2.ContactInfo(email=request.label_set.manager.email)
        )
        async for chunk_0 in deps.clients.documents_document.WatchDocuments(outgoing_0, timeout=deps.settings.timeout):
            response_0 = chunk_0
        outgoing_1 = labeling_v1_label_set_lifecycle_service_pb2.ScheduleLabelSetExpiryRequest(
            context=request.context,
            label_set=labeling_v1_labeling_pb2.LabelSet(
                children=[
                    labeling_v1_labeling_pb2.LabelSet(
                        children=[
                            labeling_v1_labeling_pb2.LabelSet(
                                audit=common_v1_audit_pb2.AuditInfo(updated_at=request.label_set.audit.updated_at)
                            )
                        ],
                        location=common_v1_address_pb2.PostalAddress(recipient=request.label_set.location.recipient)
                    )
                ]
            )
        )
        response_1 = await hooks.label_set_approval_submit_label_set1(
            deps.clients.labeling_label_set_lifecycle,
            outgoing_1,
            deps.settings.timeout
        )
        returned_1_0 = response_1.label_set.location.locality
        returned_1_0_part_1 = response.label_set.children.add()
        if returned_1_0:
            returned_1_0_part_1.location.locality = returned_1_0
        returned_1_1 = response_1.label_set.depth
        returned_1_1_part_1 = response.label_set.children.add()
        returned_1_1_part_2 = returned_1_1_part_1.children.add()
        if returned_1_1:
            returned_1_1_part_2.depth = returned_1_1
        echoed_0 = request.label_set_id
        response.label_set.label_set_id = echoed_0
        echoed_1 = request.label_set.manager
        response.label_set.manager.CopyFrom(echoed_1)
        return response
