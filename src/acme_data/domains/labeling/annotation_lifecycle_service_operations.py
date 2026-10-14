"""Functional operations behind AnnotationLifecycleService."""

from __future__ import annotations

from functools import partial
import logging

from google.protobuf.json_format import MessageToJson
from google.protobuf.json_format import Parse

from acme.anomalies.v1 import anomalies_pb2 as anomalies_v1_anomalies_pb2
from acme.anomalies.v1 import (
    anomaly_feedback_approval_service_pb2 as anomalies_v1_anomaly_feedback_approval_service_pb2,
)
from acme.audit.v1 import audit_event_service_pb2 as audit_v1_audit_event_service_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.customers.v1 import customer_service_pb2 as customers_v1_customer_service_pb2
from acme.datasets.v1 import refs_pb2 as datasets_v1_refs_pb2
from acme.identity.v1 import identity_pb2 as identity_v1_identity_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.identity.v1 import user_validation_service_pb2 as identity_v1_user_validation_service_pb2
from acme.labeling.v1 import annotation_lifecycle_service_pb2 as labeling_v1_annotation_lifecycle_service_pb2
from acme.labeling.v1 import annotation_query_service_pb2 as labeling_v1_annotation_query_service_pb2
from acme.labeling.v1 import label_set_sync_service_pb2 as labeling_v1_label_set_sync_service_pb2
from acme.labeling.v1 import labeling_pb2 as labeling_v1_labeling_pb2
from acme.labeling.v1 import labeling_task_calculation_service_pb2 as labeling_v1_labeling_task_calculation_service_pb2
from acme.labeling.v1 import labeling_task_service_pb2 as labeling_v1_labeling_task_service_pb2
from acme.metrics.v1 import dashboard_sync_service_pb2 as metrics_v1_dashboard_sync_service_pb2
from acme.search.v1 import search_index_query_service_pb2 as search_v1_search_index_query_service_pb2
from acme.venues.v1 import venue_validation_service_pb2 as venues_v1_venue_validation_service_pb2
from acme.venues.v1 import venues_pb2 as venues_v1_venues_pb2

from acme_data.domains.labeling.dependencies import Dependencies
from acme_data.domains.labeling.models import AnnotationLifecycleReinstateAnnotation1Command
from acme_data.domains.labeling.models import to_annotation_lifecycle_reinstate_annotation1_command
from acme_data.platform.rpc import run_steps
from acme_data.platform.tenancy import tenant_id
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


async def handle_activate_annotation(
    deps: Dependencies,
    request: labeling_v1_annotation_lifecycle_service_pb2.ActivateAnnotationRequest
) -> labeling_v1_annotation_lifecycle_service_pb2.ActivateAnnotationResponse:
    """Activates an annotation."""
    response = labeling_v1_annotation_lifecycle_service_pb2.ActivateAnnotationResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('ActivateAnnotation', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'ActivateAnnotation', {'reason': request.reason})
        response_0 = customers_v1_customer_service_pb2.ListCustomersResponse()
        response_1 = labeling_v1_labeling_task_calculation_service_pb2.EstimateLabelingTaskResponse()
        outgoing_0 = customers_v1_customer_service_pb2.ListCustomersRequest(
            context=request.context,
            filter=customers_v1_customer_service_pb2.ListCustomersRequest.Filter(
                created_after=request.details.effective_at,
                labels=dict(request.annotations)
            )
        )
        response_0 = await deps.clients.customers_customer.ListCustomers(outgoing_0, timeout=deps.settings.timeout)
        outgoing_1 = labeling_v1_labeling_task_calculation_service_pb2.EstimateLabelingTaskRequest(
            context=request.context,
            labeling_task=labeling_v1_labeling_pb2.LabelingTask(
                assignee=identity_v1_refs_pb2.UserRef(email=request.details.notify_contact.email)
            )
        )
        document_1 = MessageToJson(outgoing_1, preserving_proto_field_name=True)
        outgoing_1 = Parse(document_1, labeling_v1_labeling_task_calculation_service_pb2.EstimateLabelingTaskRequest())
        response_1 = await deps.clients.labeling_labeling_task_calculation.EstimateLabelingTask(
            outgoing_1,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.result.message
        if returned_0_0:
            response.result.message = returned_0_0
        returned_0_1 = response_0.result.correlation_id
        if returned_0_1:
            response.annotation.correlation_id = returned_0_1
        returned_1_0 = response_1.labeling_task.labeling_task_id
        if returned_1_0:
            response.annotation.subject.labeling_task_id = returned_1_0
        echoed_0 = request.annotation_id
        response.annotation.annotation_id = echoed_0
        echoed_1 = request.details.effective_at
        response.outcome.effective_at.CopyFrom(echoed_1)
        return response


async def handle_expire_annotation(
    deps: Dependencies,
    request: labeling_v1_annotation_lifecycle_service_pb2.ExpireAnnotationRequest
) -> labeling_v1_annotation_lifecycle_service_pb2.ExpireAnnotationResponse:
    """Expires an annotation."""
    response = labeling_v1_annotation_lifecycle_service_pb2.ExpireAnnotationResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('ExpireAnnotation', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'ExpireAnnotation', {'reason': request.reason})
        response_0 = venues_v1_venue_validation_service_pb2.ScoreVenueResponse()
        outgoing_0 = venues_v1_venue_validation_service_pb2.ScoreVenueRequest(
            context=request.context,
            venue=venues_v1_venues_pb2.Venue(
                owner=identity_v1_refs_pb2.UserRef(
                    display_name=request.details.new_owner.display_name,
                    email=request.details.notify_contact.email,
                    user_id=request.details.new_owner.user_id
                )
            )
        )
        response_0 = await deps.clients.venues_venue_validation.ScoreVenue(outgoing_0, timeout=deps.settings.timeout)
        returned_0_0 = response_0.result.message
        if returned_0_0:
            response.result.message = returned_0_0
        echoed_0 = request.annotation_id
        response.annotation.annotation_id = echoed_0
        echoed_1 = request.details.effective_at
        response.outcome.effective_at.CopyFrom(echoed_1)
        return response


async def handle_get_annotation_lifecycle(
    deps: Dependencies,
    request: labeling_v1_annotation_lifecycle_service_pb2.GetAnnotationLifecycleRequest
) -> labeling_v1_annotation_lifecycle_service_pb2.GetAnnotationLifecycleResponse:
    """Returns an annotation."""
    response = labeling_v1_annotation_lifecycle_service_pb2.GetAnnotationLifecycleResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('GetAnnotationLifecycle', extra={'fields': {'domain': 'labeling'}})
        await deps.repository.audit(request.context.tenant_id, 'GetAnnotationLifecycle', {})
        response_0 = search_v1_search_index_query_service_pb2.CountSearchIndexesResponse()
        outgoing_0 = search_v1_search_index_query_service_pb2.CountSearchIndexesRequest(
            context=request.context,
            filter=search_v1_search_index_query_service_pb2.CountSearchIndexesRequest.Filter(
                created_after=request.context.deadline,
                owner_id=request.annotation_id
            )
        )
        response_0 = await deps.clients.search_search_index_query.CountSearchIndexes(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.result.message
        if returned_0_0:
            response.result.message = returned_0_0
        returned_0_1 = response_0.result.reference_ids
        response.result.reference_ids.extend(returned_0_1)
        echoed_0 = request.annotation_id
        response.annotation.annotation_id = echoed_0
        return response


async def handle_reinstate_annotation(
    deps: Dependencies,
    request: labeling_v1_annotation_lifecycle_service_pb2.ReinstateAnnotationRequest
) -> labeling_v1_annotation_lifecycle_service_pb2.ReinstateAnnotationResponse:
    """Reinstates an annotation."""
    response = labeling_v1_annotation_lifecycle_service_pb2.ReinstateAnnotationResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('ReinstateAnnotation', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'ReinstateAnnotation', {'reason': request.reason})
        response_0 = identity_v1_user_validation_service_pb2.ValidateUserResponse()
        response_1 = labeling_v1_labeling_task_calculation_service_pb2.SimulateLabelingTaskResponse()
        outgoing_0 = identity_v1_user_validation_service_pb2.ValidateUserRequest(
            context=request.context,
            details=identity_v1_user_validation_service_pb2.ValidateUserRequest.Details(
                contact=common_v1_contact_pb2.ContactInfo(
                    preferred_channel=request.details.notify_contact.preferred_channel
                )
            ),
            user=identity_v1_identity_pb2.User(
                contact=common_v1_contact_pb2.ContactInfo(email=request.details.notify_contact.email)
            )
        )
        response_0 = await deps.clients.identity_user_validation.ValidateUser(outgoing_0, timeout=deps.settings.timeout)
        command_1 = AnnotationLifecycleReinstateAnnotation1Command(
            context=request.context,
            labeling_task_assignee_display_name=request.details.new_owner.display_name,
            labeling_task_assignee_email=response_0.user.contact.email
        )
        outgoing_1 = to_annotation_lifecycle_reinstate_annotation1_command(command_1)
        response_1 = await deps.clients.labeling_labeling_task_calculation.SimulateLabelingTask(
            outgoing_1,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.outcome.status
        if returned_0_0:
            response.outcome.status = returned_0_0
        returned_1_0 = response_1.labeling_task.labeling_task_id
        if returned_1_0:
            response.annotation.subject.labeling_task_id = returned_1_0
        echoed_0 = request.annotation_id
        response.annotation.annotation_id = echoed_0
        echoed_1 = request.details.effective_at
        response.outcome.effective_at.CopyFrom(echoed_1)
        return response


async def handle_renew_annotation(
    deps: Dependencies,
    request: labeling_v1_annotation_lifecycle_service_pb2.RenewAnnotationRequest
) -> labeling_v1_annotation_lifecycle_service_pb2.RenewAnnotationResponse:
    """Renews an annotation."""
    response = labeling_v1_annotation_lifecycle_service_pb2.RenewAnnotationResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('RenewAnnotation', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'RenewAnnotation', {'reason': request.reason})
        response_0 = audit_v1_audit_event_service_pb2.SearchAuditEventsResponse()
        outgoing_0 = audit_v1_audit_event_service_pb2.SearchAuditEventsRequest(
            context=request.context,
            filter=audit_v1_audit_event_service_pb2.SearchAuditEventsRequest.Filter(
                created_after=request.details.effective_at,
                labels=dict(request.annotations),
                owner_id=request.annotation_id
            )
        )
        response_0 = await deps.clients.audit_audit_event.SearchAuditEvents(outgoing_0, timeout=deps.settings.timeout)
        returned_0_0 = response_0.result.status
        if returned_0_0:
            response.result.status = returned_0_0
        echoed_0 = request.annotation_id
        response.annotation.annotation_id = echoed_0
        echoed_1 = request.details.effective_at
        response.outcome.effective_at.CopyFrom(echoed_1)
        return response


async def handle_schedule_annotation_expiry(
    deps: Dependencies,
    request: labeling_v1_annotation_lifecycle_service_pb2.ScheduleAnnotationExpiryRequest
) -> labeling_v1_annotation_lifecycle_service_pb2.ScheduleAnnotationExpiryResponse:
    """Schedules an annotation."""
    response = labeling_v1_annotation_lifecycle_service_pb2.ScheduleAnnotationExpiryResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('ScheduleAnnotationExpiry', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'ScheduleAnnotationExpiry', {'reason': request.reason})
        await deps.repository.save_annotation(request.context.tenant_id, request.annotation)
        response_0 = labeling_v1_annotation_query_service_pb2.BrowseAnnotationsResponse()
        outgoing_0 = labeling_v1_annotation_query_service_pb2.BrowseAnnotationsRequest(
            context=request.context,
            filter=labeling_v1_annotation_query_service_pb2.BrowseAnnotationsRequest.Filter(
                created_after=request.annotation.occurred_at,
                labels=dict(request.annotation.attributes),
                owner_id=request.annotation.subject.labeling_task_id
            )
        )
        response_0 = await deps.clients.labeling_annotation_query.BrowseAnnotations(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.result.message
        if returned_0_0:
            response.outcome.message = returned_0_0
        returned_0_1 = response_0.result.details
        response.result.details.update(returned_0_1)
        echoed_0 = request.annotation_id
        response.annotation.annotation_id = echoed_0
        echoed_1 = request.annotation.attributes
        response.annotation.attributes.update(echoed_1)
        return response


async def handle_suspend_annotation(
    deps: Dependencies,
    request: labeling_v1_annotation_lifecycle_service_pb2.SuspendAnnotationRequest
) -> labeling_v1_annotation_lifecycle_service_pb2.SuspendAnnotationResponse:
    """Suspends an annotation."""
    response = labeling_v1_annotation_lifecycle_service_pb2.SuspendAnnotationResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('SuspendAnnotation', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'SuspendAnnotation', {'reason': request.reason})
        response_0 = anomalies_v1_anomaly_feedback_approval_service_pb2.RecallAnomalyFeedbackResponse()
        response_1 = metrics_v1_dashboard_sync_service_pb2.SyncDashboardsResponse()
        outgoing_0 = anomalies_v1_anomaly_feedback_approval_service_pb2.RecallAnomalyFeedbackRequest(
            anomaly_feedback=anomalies_v1_anomalies_pb2.AnomalyFeedback(
                subject=datasets_v1_refs_pb2.DatasetRef(display_name=request.details.new_owner.display_name)
            ),
            context=request.context,
            details=anomalies_v1_anomaly_feedback_approval_service_pb2.RecallAnomalyFeedbackRequest.Details(
                approver=identity_v1_refs_pb2.UserRef(
                    email=request.details.new_owner.email,
                    user_id=request.details.new_owner.user_id
                )
            )
        )
        response_0 = await deps.clients.anomalies_anomaly_feedback_approval.RecallAnomalyFeedback(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = metrics_v1_dashboard_sync_service_pb2.SyncDashboardsRequest()
        outgoing_1.context.CopyFrom(request.context)
        outgoing_1.dashboard.counterparty.display_name = response_0.anomaly_feedback.subject.display_name
        field_1_2_part_1 = outgoing_1.dashboard.lines.add()
        field_1_2_part_1.attributes.update(dict(response_0.anomaly_feedback.attributes))
        outgoing_1.context.tenant_id = tenant_id.get()
        response_1 = await deps.clients.metrics_dashboard_sync.SyncDashboards(outgoing_1, timeout=deps.settings.timeout)
        returned_0_0 = response_0.outcome.effective_at
        if returned_0_0.ListFields():
            response.outcome.effective_at.MergeFrom(returned_0_0)
        returned_0_1 = response_0.anomaly_feedback.attributes
        response.annotation.attributes.update(returned_0_1)
        returned_1_0 = response_1.result.correlation_id
        if returned_1_0:
            response.annotation.correlation_id = returned_1_0
        echoed_0 = request.annotation_id
        response.annotation.annotation_id = echoed_0
        echoed_1 = request.details.new_owner.display_name
        response.annotation.subject.display_name = echoed_1
        return response


async def handle_terminate_annotation(
    deps: Dependencies,
    request: labeling_v1_annotation_lifecycle_service_pb2.TerminateAnnotationRequest
) -> labeling_v1_annotation_lifecycle_service_pb2.TerminateAnnotationResponse:
    """Terminates an annotation."""
    response = labeling_v1_annotation_lifecycle_service_pb2.TerminateAnnotationResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('TerminateAnnotation', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'TerminateAnnotation', {'reason': request.reason})
        response_0 = labeling_v1_labeling_task_service_pb2.CreateLabelingTaskResponse()
        response_1 = labeling_v1_label_set_sync_service_pb2.ResolveLabelSetConflictResponse()
        outgoing_0 = labeling_v1_labeling_task_service_pb2.CreateLabelingTaskRequest(
            context=request.context,
            labeling_task=labeling_v1_labeling_pb2.LabelingTask(
                assignee=identity_v1_refs_pb2.UserRef(display_name=request.details.new_owner.display_name),
                requester=common_v1_contact_pb2.ContactInfo(
                    email=request.details.new_owner.email,
                    phone=request.details.notify_contact.phone,
                    preferred_channel=request.details.notify_contact.preferred_channel
                )
            )
        )
        response_0 = await deps.clients.labeling_labeling_task.CreateLabelingTask(
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
                                audit=common_v1_audit_pb2.AuditInfo(etag=response_0.labeling_task.audit.etag),
                                children=[
                                    labeling_v1_labeling_pb2.LabelSet(
                                        label_set_id=response_0.labeling_task.customer.label_set_id
                                    )
                                ],
                                manager=identity_v1_refs_pb2.UserRef(
                                    display_name=response_0.labeling_task.customer.display_name,
                                    email=request.details.new_owner.email
                                )
                            )
                        ]
                    )
                ]
            )
        )
        steps_1 = [
            partial(
                deps.clients.labeling_label_set_sync.ResolveLabelSetConflict,
                outgoing_1,
                timeout=deps.settings.timeout
            )
        ]
        results_1 = await run_steps(steps_1)
        response_1 = results_1[-1]
        returned_0_0 = response_0.result.details
        response.result.details.update(returned_0_0)
        returned_1_0 = response_1.outcome.status
        if returned_1_0:
            response.result.status = returned_1_0
        echoed_0 = request.annotation_id
        response.annotation.annotation_id = echoed_0
        echoed_1 = request.details.effective_at
        response.outcome.effective_at.CopyFrom(echoed_1)
        return response
