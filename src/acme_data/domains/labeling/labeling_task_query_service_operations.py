"""Functional operations behind LabelingTaskQueryService."""

from __future__ import annotations

from functools import partial
from typing import Any
import logging

from google.protobuf.json_format import MessageToDict
from google.protobuf.json_format import MessageToJson
from google.protobuf.json_format import Parse
from google.protobuf.json_format import ParseDict

from acme.admissions.v1 import admission_service_pb2 as admissions_v1_admission_service_pb2
from acme.admissions.v1 import admissions_pb2 as admissions_v1_admissions_pb2
from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.documents.v1 import document_validation_service_pb2 as documents_v1_document_validation_service_pb2
from acme.documents.v1 import documents_pb2 as documents_v1_documents_pb2
from acme.documents.v1 import refs_pb2 as documents_v1_refs_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.labeling.v1 import annotation_calculation_service_pb2 as labeling_v1_annotation_calculation_service_pb2
from acme.labeling.v1 import label_set_validation_service_pb2 as labeling_v1_label_set_validation_service_pb2
from acme.labeling.v1 import labeling_pb2 as labeling_v1_labeling_pb2
from acme.labeling.v1 import labeling_task_query_service_pb2 as labeling_v1_labeling_task_query_service_pb2
from acme.labeling.v1 import labeling_task_validation_service_pb2 as labeling_v1_labeling_task_validation_service_pb2
from acme.labeling.v1 import refs_pb2 as labeling_v1_refs_pb2
from acme.metrics.v1 import metric_alert_history_service_pb2 as metrics_v1_metric_alert_history_service_pb2
from acme.metrics.v1 import metrics_pb2 as metrics_v1_metrics_pb2
from acme.modelregistry.v1 import (
    deployment_calculation_service_pb2 as modelregistry_v1_deployment_calculation_service_pb2,
)
from acme.modelregistry.v1 import modelregistry_pb2 as modelregistry_v1_modelregistry_pb2

from acme_data.domains.labeling.dependencies import Dependencies
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


async def handle_browse_labeling_tasks(
    deps: Dependencies,
    request: labeling_v1_labeling_task_query_service_pb2.BrowseLabelingTasksRequest
) -> labeling_v1_labeling_task_query_service_pb2.BrowseLabelingTasksResponse:
    """Lists labeling tasks a page at a time."""
    response = labeling_v1_labeling_task_query_service_pb2.BrowseLabelingTasksResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('BrowseLabelingTasks', extra={'fields': {'order_by': request.order_by}})
        await deps.repository.audit(request.context.tenant_id, 'BrowseLabelingTasks', {'order_by': request.order_by})
        response_0 = metrics_v1_metric_alert_history_service_pb2.RevertMetricAlertResponse()
        outgoing_0 = metrics_v1_metric_alert_history_service_pb2.RevertMetricAlertRequest(
            context=request.context,
            metric_alert=metrics_v1_metrics_pb2.MetricAlert(
                owner=identity_v1_refs_pb2.UserRef(user_id=request.context.actor.user_id)
            )
        )
        response_0 = await deps.clients.metrics_metric_alert_history.RevertMetricAlert(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.metric_alert.audit.etag
        returned_0_0_part_0 = response.labeling_tasks.add()
        if returned_0_0:
            returned_0_0_part_0.audit.etag = returned_0_0
        return response


async def handle_count_labeling_tasks(
    deps: Dependencies,
    request: labeling_v1_labeling_task_query_service_pb2.CountLabelingTasksRequest
) -> labeling_v1_labeling_task_query_service_pb2.CountLabelingTasksResponse:
    """Counts labeling tasks by status."""
    response = labeling_v1_labeling_task_query_service_pb2.CountLabelingTasksResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('CountLabelingTasks', extra={'fields': {'order_by': request.order_by}})
        await deps.repository.audit(request.context.tenant_id, 'CountLabelingTasks', {'order_by': request.order_by})
        response_0 = labeling_v1_annotation_calculation_service_pb2.SimulateAnnotationResponse()
        outgoing_0 = labeling_v1_annotation_calculation_service_pb2.SimulateAnnotationRequest(
            annotation=labeling_v1_labeling_pb2.Annotation(
                measurements=[labeling_v1_labeling_pb2.AnnotationMeasurement(observed_at=request.filter.created_after)]
            ),
            context=request.context,
            details=labeling_v1_annotation_calculation_service_pb2.SimulateAnnotationRequest.Details(
                destination=common_v1_address_pb2.PostalAddress(region=request.filter.region)
            )
        )
        response_0 = await deps.clients.labeling_annotation_calculation.SimulateAnnotation(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.result.reference_ids
        response.result.reference_ids.extend(returned_0_0)
        return response


async def handle_export_labeling_tasks(
    deps: Dependencies,
    request: labeling_v1_labeling_task_query_service_pb2.ExportLabelingTasksRequest
) -> labeling_v1_labeling_task_query_service_pb2.ExportLabelingTasksResponse:
    """Streams every matching labeling task."""
    response = labeling_v1_labeling_task_query_service_pb2.ExportLabelingTasksResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('ExportLabelingTasks', extra={'fields': {'destination_uri': request.destination_uri}})
        await deps.repository.audit(
            request.context.tenant_id,
            'ExportLabelingTasks',
            {'destination_uri': request.destination_uri}
        )
        response_0 = labeling_v1_labeling_task_validation_service_pb2.CheckLabelingTaskEligibilityResponse()
        response_1 = metrics_v1_metric_alert_history_service_pb2.ListMetricAlertVersionsResponse()
        response_2 = labeling_v1_annotation_calculation_service_pb2.CalculateAnnotationResponse()
        response_3 = modelregistry_v1_deployment_calculation_service_pb2.CalculateDeploymentResponse()
        outgoing_0 = labeling_v1_labeling_task_validation_service_pb2.CheckLabelingTaskEligibilityRequest(
            context=request.context,
            details=labeling_v1_labeling_task_validation_service_pb2.CheckLabelingTaskEligibilityRequest.Details(
                contact=common_v1_contact_pb2.ContactInfo(email=request.context.actor.email)
            ),
            labeling_task=labeling_v1_labeling_pb2.LabelingTask(
                assignee=identity_v1_refs_pb2.UserRef(user_id=request.context.actor.user_id),
                audit=common_v1_audit_pb2.AuditInfo(updated_at=request.filter.created_after)
            )
        )
        response_0 = await deps.clients.labeling_labeling_task_validation.CheckLabelingTaskEligibility(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        fields_1: dict[str, Any] = {'context': request.context, 'filter': {'owner_id': request.filter.owner_id}}
        outgoing_1 = metrics_v1_metric_alert_history_service_pb2.ListMetricAlertVersionsRequest(**fields_1)
        response_1 = await deps.clients.metrics_metric_alert_history.ListMetricAlertVersions(
            outgoing_1,
            timeout=deps.settings.timeout
        )
        outgoing_2 = labeling_v1_annotation_calculation_service_pb2.CalculateAnnotationRequest(
            annotation=labeling_v1_labeling_pb2.Annotation(
                correlation_id=response_0.result.correlation_id,
                subject=labeling_v1_refs_pb2.LabelingTaskRef(
                    display_name=response_0.labeling_task.assignee.display_name,
                    labeling_task_id=response_0.labeling_task.labeling_task_id
                )
            ),
            context=request.context,
            details=labeling_v1_annotation_calculation_service_pb2.CalculateAnnotationRequest.Details(
                destination=common_v1_address_pb2.PostalAddress(region=request.filter.region)
            )
        )
        document_2 = MessageToDict(outgoing_2, preserving_proto_field_name=True)
        outgoing_2 = ParseDict(document_2, labeling_v1_annotation_calculation_service_pb2.CalculateAnnotationRequest())
        response_2 = await deps.clients.labeling_annotation_calculation.CalculateAnnotation(
            outgoing_2,
            timeout=deps.settings.timeout
        )
        outgoing_3 = modelregistry_v1_deployment_calculation_service_pb2.CalculateDeploymentRequest(
            context=request.context,
            deployment=modelregistry_v1_modelregistry_pb2.Deployment(
                audit=common_v1_audit_pb2.AuditInfo(updated_by=response_0.labeling_task.audit.updated_by),
                organizer=identity_v1_refs_pb2.UserRef(email=response_0.labeling_task.requester.email),
                participants=[
                    modelregistry_v1_modelregistry_pb2.DeploymentParticipant(
                        contact=common_v1_contact_pb2.ContactInfo(
                            name=response_0.labeling_task.requester.name,
                            phone=response_0.labeling_task.requester.phone
                        )
                    )
                ]
            )
        )
        document_3 = MessageToJson(outgoing_3, preserving_proto_field_name=True)
        outgoing_3 = Parse(document_3, modelregistry_v1_deployment_calculation_service_pb2.CalculateDeploymentRequest())
        response_3 = await deps.clients.modelregistry_deployment_calculation.CalculateDeployment(
            outgoing_3,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.outcome.message
        if returned_0_0:
            response.result.message = returned_0_0
        returned_0_1 = response_0.result.status
        if returned_0_1:
            response.result.status = returned_0_1
        returned_1_0 = response_1.result.message
        if returned_1_0:
            response.result.message = returned_1_0
        returned_1_1 = response_1.result.details
        response.result.details.update(returned_1_1)
        returned_2_0 = response_2.result.correlation_id
        if returned_2_0:
            response.result.correlation_id = returned_2_0
        returned_2_1 = response_2.result.reference_ids
        response.result.reference_ids.extend(returned_2_1)
        returned_3_0 = response_3.result.details
        response.result.details.update(returned_3_0)
        returned_3_1 = response_3.deployment.audit.updated_by
        if returned_3_1:
            response.labeling_task.audit.updated_by = returned_3_1
        return response


async def handle_find_labeling_tasks(
    deps: Dependencies,
    request: labeling_v1_labeling_task_query_service_pb2.FindLabelingTasksRequest
) -> labeling_v1_labeling_task_query_service_pb2.FindLabelingTasksResponse:
    """Lists labeling tasks a page at a time."""
    response = labeling_v1_labeling_task_query_service_pb2.FindLabelingTasksResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('FindLabelingTasks', extra={'fields': {'order_by': request.order_by}})
        await deps.repository.audit(request.context.tenant_id, 'FindLabelingTasks', {'order_by': request.order_by})
        return response


async def handle_lookup_labeling_task(
    deps: Dependencies,
    request: labeling_v1_labeling_task_query_service_pb2.LookupLabelingTaskRequest
) -> labeling_v1_labeling_task_query_service_pb2.LookupLabelingTaskResponse:
    """Returns a labeling task."""
    response = labeling_v1_labeling_task_query_service_pb2.LookupLabelingTaskResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('LookupLabelingTask', extra={'fields': {'domain': 'labeling'}})
        await deps.repository.audit(request.context.tenant_id, 'LookupLabelingTask', {})
        response_0 = labeling_v1_annotation_calculation_service_pb2.SimulateAnnotationResponse()
        outgoing_0 = labeling_v1_annotation_calculation_service_pb2.SimulateAnnotationRequest(
            annotation=labeling_v1_labeling_pb2.Annotation(
                attributes=dict(request.context.baggage),
                occurred_at=request.context.deadline,
                source=request.context.trace_id,
                subject=labeling_v1_refs_pb2.LabelingTaskRef(labeling_task_id=request.labeling_task_id)
            ),
            context=request.context
        )
        response_0 = await deps.clients.labeling_annotation_calculation.SimulateAnnotation(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.annotation.correlation_id
        if returned_0_0:
            response.result.correlation_id = returned_0_0
        returned_0_1 = response_0.annotation.subject.labeling_task_id
        if returned_0_1:
            response.labeling_task.labeling_task_id = returned_0_1
        return response


async def handle_peek_labeling_task(
    deps: Dependencies,
    request: labeling_v1_labeling_task_query_service_pb2.PeekLabelingTaskRequest
) -> labeling_v1_labeling_task_query_service_pb2.PeekLabelingTaskResponse:
    """Returns a labeling task."""
    response = labeling_v1_labeling_task_query_service_pb2.PeekLabelingTaskResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('PeekLabelingTask', extra={'fields': {'domain': 'labeling'}})
        await deps.repository.audit(request.context.tenant_id, 'PeekLabelingTask', {})
        response_0 = admissions_v1_admission_service_pb2.CreateAdmissionResponse()
        outgoing_0 = admissions_v1_admission_service_pb2.CreateAdmissionRequest(
            admission=admissions_v1_admissions_pb2.Admission(
                correlation_id=request.labeling_task_id,
                occurred_at=request.context.deadline,
                source=request.context.actor.user_id
            ),
            context=request.context
        )
        response_0 = await deps.clients.admissions_admission.CreateAdmission(outgoing_0, timeout=deps.settings.timeout)
        returned_0_0 = response_0.result.reference_ids
        response.result.reference_ids.extend(returned_0_0)
        echoed_0 = request.labeling_task_id
        response.labeling_task.labeling_task_id = echoed_0
        return response


async def handle_resolve_labeling_tasks(
    deps: Dependencies,
    request: labeling_v1_labeling_task_query_service_pb2.ResolveLabelingTasksRequest
) -> labeling_v1_labeling_task_query_service_pb2.ResolveLabelingTasksResponse:
    """Returns several labeling tasks at once."""
    response = labeling_v1_labeling_task_query_service_pb2.ResolveLabelingTasksResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('ResolveLabelingTasks', extra={'fields': {'domain': 'labeling'}})
        await deps.repository.audit(request.context.tenant_id, 'ResolveLabelingTasks', {})
        response_0 = labeling_v1_annotation_calculation_service_pb2.CompareAnnotationOptionsResponse()
        outgoing_0 = labeling_v1_annotation_calculation_service_pb2.CompareAnnotationOptionsRequest(
            annotation=labeling_v1_labeling_pb2.Annotation(
                correlation_id=request.context.trace_id,
                occurred_at=request.context.deadline
            ),
            context=request.context
        )
        response_0 = await deps.clients.labeling_annotation_calculation.CompareAnnotationOptions(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.annotation.subject.display_name
        returned_0_0_part_0 = response.labeling_tasks.add()
        if returned_0_0:
            returned_0_0_part_0.assignee.display_name = returned_0_0
        return response


async def handle_suggest_labeling_tasks(
    deps: Dependencies,
    request: labeling_v1_labeling_task_query_service_pb2.SuggestLabelingTasksRequest
) -> labeling_v1_labeling_task_query_service_pb2.SuggestLabelingTasksResponse:
    """Lists labeling tasks a page at a time."""
    response = labeling_v1_labeling_task_query_service_pb2.SuggestLabelingTasksResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('SuggestLabelingTasks', extra={'fields': {'order_by': request.order_by}})
        await deps.repository.audit(request.context.tenant_id, 'SuggestLabelingTasks', {'order_by': request.order_by})
        response_0 = labeling_v1_annotation_calculation_service_pb2.EstimateAnnotationResponse()
        outgoing_0 = labeling_v1_annotation_calculation_service_pb2.EstimateAnnotationRequest(
            annotation=labeling_v1_labeling_pb2.Annotation(
                measurements=[labeling_v1_labeling_pb2.AnnotationMeasurement(observed_at=request.filter.created_after)],
                source=request.filter.owner_id
            ),
            context=request.context,
            details=labeling_v1_annotation_calculation_service_pb2.EstimateAnnotationRequest.Details(
                destination=common_v1_address_pb2.PostalAddress(region=request.filter.region)
            )
        )
        response_0 = await deps.clients.labeling_annotation_calculation.EstimateAnnotation(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.annotation.correlation_id
        if returned_0_0:
            response.result.correlation_id = returned_0_0
        return response


async def handle_summarize_labeling_tasks(
    deps: Dependencies,
    request: labeling_v1_labeling_task_query_service_pb2.SummarizeLabelingTasksRequest
) -> labeling_v1_labeling_task_query_service_pb2.SummarizeLabelingTasksResponse:
    """Summarizes a labeling task."""
    response = labeling_v1_labeling_task_query_service_pb2.SummarizeLabelingTasksResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('SummarizeLabelingTasks', extra={'fields': {'labeling_task_id': request.labeling_task_id}})
        await deps.repository.audit(
            request.context.tenant_id,
            'SummarizeLabelingTasks',
            {'labeling_task_id': request.labeling_task_id}
        )
        response_0 = labeling_v1_label_set_validation_service_pb2.PreviewLabelSetResponse()
        response_1 = documents_v1_document_validation_service_pb2.LintDocumentsResponse()
        outgoing_0 = labeling_v1_label_set_validation_service_pb2.PreviewLabelSetRequest(
            context=request.context,
            label_set=labeling_v1_labeling_pb2.LabelSet(
                children=[
                    labeling_v1_labeling_pb2.LabelSet(
                        children=[
                            labeling_v1_labeling_pb2.LabelSet(
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
        response_0 = await deps.clients.labeling_label_set_validation.PreviewLabelSet(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = documents_v1_document_validation_service_pb2.LintDocumentsRequest(
            context=request.context,
            document=documents_v1_documents_pb2.Document(
                billing_address=common_v1_address_pb2.PostalAddress(
                    postal_code=response_0.label_set.location.postal_code
                ),
                counterparty=documents_v1_refs_pb2.DocumentFolderRef(
                    display_name=response_0.label_set.manager.display_name
                )
            )
        )
        send_1 = partial(deps.clients.documents_document_validation.LintDocuments, timeout=deps.settings.timeout)
        response_1 = await send_1(outgoing_1)
        returned_0_0 = response_0.outcome.message
        if returned_0_0:
            response.result.message = returned_0_0
        returned_1_0 = response_1.result.reference_ids
        response.result.reference_ids.extend(returned_1_0)
        returned_1_1 = response_1.result.details
        response.result.details.update(returned_1_1)
        echoed_0 = request.details.period
        response.period.CopyFrom(echoed_0)
        return response
