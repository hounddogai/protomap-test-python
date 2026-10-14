"""Reusable transport mixin for LabelingTaskService."""

from __future__ import annotations

from collections.abc import AsyncIterator
from collections.abc import Awaitable
from collections.abc import Callable
from typing import Any
import asyncio
import logging

from google.protobuf.any_pb2 import Any as AnyMessage
from google.protobuf.json_format import MessageToJson
from google.protobuf.json_format import Parse
import grpc

from acme.anomalies.v1 import anomalies_pb2 as anomalies_v1_anomalies_pb2
from acme.anomalies.v1 import (
    anomaly_feedback_calculation_service_pb2 as anomalies_v1_anomaly_feedback_calculation_service_pb2,
)
from acme.anomalies.v1 import anomaly_validation_service_pb2 as anomalies_v1_anomaly_validation_service_pb2
from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.featurestore.v1 import (
    feature_value_validation_service_pb2 as featurestore_v1_feature_value_validation_service_pb2,
)
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.labeling.v1 import annotation_calculation_service_pb2 as labeling_v1_annotation_calculation_service_pb2
from acme.labeling.v1 import annotation_query_service_pb2 as labeling_v1_annotation_query_service_pb2
from acme.labeling.v1 import annotation_validation_service_pb2 as labeling_v1_annotation_validation_service_pb2
from acme.labeling.v1 import label_set_calculation_service_pb2 as labeling_v1_label_set_calculation_service_pb2
from acme.labeling.v1 import label_set_validation_service_pb2 as labeling_v1_label_set_validation_service_pb2
from acme.labeling.v1 import labeling_pb2 as labeling_v1_labeling_pb2
from acme.labeling.v1 import labeling_task_calculation_service_pb2 as labeling_v1_labeling_task_calculation_service_pb2
from acme.labeling.v1 import labeling_task_service_pb2 as labeling_v1_labeling_task_service_pb2
from acme.labeling.v1 import labeling_task_validation_service_pb2 as labeling_v1_labeling_task_validation_service_pb2
from acme.labeling.v1 import refs_pb2 as labeling_v1_refs_pb2
from acme.lineage.v1 import lineage_edge_calculation_service_pb2 as lineage_v1_lineage_edge_calculation_service_pb2
from acme.lineage.v1 import lineage_pb2 as lineage_v1_lineage_pb2
from acme.metrics.v1 import dashboard_notification_service_pb2 as metrics_v1_dashboard_notification_service_pb2
from acme.modelregistry.v1 import modelregistry_pb2 as modelregistry_v1_modelregistry_pb2
from acme.modelregistry.v1 import registered_model_service_pb2 as modelregistry_v1_registered_model_service_pb2
from acme.prescriptions.v1 import prescription_query_service_pb2 as prescriptions_v1_prescription_query_service_pb2

from acme_data.domains.labeling.adapters import LabelingTaskCloneLabelingTask0Adapter
from acme_data.domains.labeling.adapters import LabelingTaskCloneLabelingTask0Port
from acme_data.domains.labeling.adapters import LabelingTaskCreateLabelingTask1Adapter
from acme_data.domains.labeling.dependencies import Dependencies
from acme_data.domains.labeling.models import LabelingTaskUpdateLabelingTask0Command
from acme_data.domains.labeling.models import to_labeling_task_update_labeling_task0_command
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_id
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class LabelingTaskServicerHandlers:
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    @retry_transient
    async def BatchGetLabelingTasks(
        self, request: labeling_v1_labeling_task_service_pb2.BatchGetLabelingTasksRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_labeling_task_service_pb2.BatchGetLabelingTasksResponse:
        """Returns several labeling tasks at once."""
        return await self.handle_batch_get_labeling_tasks(request)

    @rpc_errors
    async def CloneLabelingTask(
        self, request: labeling_v1_labeling_task_service_pb2.CloneLabelingTaskRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_labeling_task_service_pb2.CloneLabelingTaskResponse:
        """Creates a labeling task."""
        return await self.handle_clone_labeling_task(request)

    @rpc_errors
    async def CreateLabelingTask(
        self, request: labeling_v1_labeling_task_service_pb2.CreateLabelingTaskRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_labeling_task_service_pb2.CreateLabelingTaskResponse:
        """Creates a labeling task."""
        return await self.handle_create_labeling_task(request)

    @rpc_errors
    async def DeleteLabelingTask(
        self, request: labeling_v1_labeling_task_service_pb2.DeleteLabelingTaskRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_labeling_task_service_pb2.DeleteLabelingTaskResponse:
        """Deletes a labeling task."""
        return await self.handle_delete_labeling_task(request)

    @rpc_errors
    @retry_transient
    async def GetLabelingTask(
        self, request: labeling_v1_labeling_task_service_pb2.GetLabelingTaskRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_labeling_task_service_pb2.GetLabelingTaskResponse:
        """Returns a labeling task."""
        return await self.handle_get_labeling_task(request)

    @rpc_errors
    @retry_transient
    async def ListLabelingTasks(
        self, request: labeling_v1_labeling_task_service_pb2.ListLabelingTasksRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_labeling_task_service_pb2.ListLabelingTasksResponse:
        """Lists labeling tasks a page at a time."""
        return await self.handle_list_labeling_tasks(request)

    @rpc_errors
    @retry_transient
    async def SearchLabelingTasks(
        self, request: labeling_v1_labeling_task_service_pb2.SearchLabelingTasksRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_labeling_task_service_pb2.SearchLabelingTasksResponse:
        """Lists labeling tasks a page at a time."""
        return await self.handle_search_labeling_tasks(request)

    @rpc_errors
    async def UpdateLabelingTask(
        self, request: labeling_v1_labeling_task_service_pb2.UpdateLabelingTaskRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_labeling_task_service_pb2.UpdateLabelingTaskResponse:
        """Changes a labeling task."""
        return await self.handle_update_labeling_task(request)

    async def handle_batch_get_labeling_tasks(
        self,
        request: labeling_v1_labeling_task_service_pb2.BatchGetLabelingTasksRequest
    ) -> labeling_v1_labeling_task_service_pb2.BatchGetLabelingTasksResponse:
        """Returns several labeling tasks at once."""
        deps = self.deps
        response = labeling_v1_labeling_task_service_pb2.BatchGetLabelingTasksResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('BatchGetLabelingTasks', extra={'fields': {'domain': 'labeling'}})
            await deps.repository.audit(request.context.tenant_id, 'BatchGetLabelingTasks', {})
            response_0 = labeling_v1_annotation_validation_service_pb2.LintAnnotationsResponse()
            response_1 = metrics_v1_dashboard_notification_service_pb2.ListDashboardSubscriptionsResponse()
            outgoing_0 = labeling_v1_annotation_validation_service_pb2.LintAnnotationsRequest(
                annotation=labeling_v1_labeling_pb2.Annotation(
                    occurred_at=request.context.deadline,
                    source=request.context.actor.user_id
                ),
                context=request.context,
                details=labeling_v1_annotation_validation_service_pb2.LintAnnotationsRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(email=request.context.actor.email),
                    locale=request.context.locale
                )
            )
            response_0 = await deps.clients.labeling_annotation_validation.LintAnnotations(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = metrics_v1_dashboard_notification_service_pb2.ListDashboardSubscriptionsRequest()
            outgoing_1.context.CopyFrom(request.context)
            outgoing_1.filter.created_after.CopyFrom(response_0.outcome.effective_at)
            outgoing_1.filter.owner_id = response_0.annotation.subject.labeling_task_id
            outgoing_1.context.tenant_id = tenant_id.get()
            response_1 = await deps.clients.metrics_dashboard_notification.ListDashboardSubscriptions(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.outcome.message
            if returned_0_0:
                response.result.message = returned_0_0
            returned_1_0 = response_1.result.correlation_id
            if returned_1_0:
                response.result.correlation_id = returned_1_0
            returned_1_1 = response_1.result.details
            response.result.details.update(returned_1_1)
            return response

    async def handle_clone_labeling_task(
        self,
        request: labeling_v1_labeling_task_service_pb2.CloneLabelingTaskRequest
    ) -> labeling_v1_labeling_task_service_pb2.CloneLabelingTaskResponse:
        """Creates a labeling task."""
        deps = self.deps
        response = labeling_v1_labeling_task_service_pb2.CloneLabelingTaskResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CloneLabelingTask', extra={'fields': {'request_id': request.request_id}})
            await deps.repository.audit(
                request.context.tenant_id,
                'CloneLabelingTask',
                {'request_id': request.request_id}
            )
            await deps.repository.save_labeling_task(request.context.tenant_id, request.labeling_task)
            response_0 = labeling_v1_labeling_task_validation_service_pb2.PreviewLabelingTaskResponse()
            outgoing_0 = labeling_v1_labeling_task_validation_service_pb2.PreviewLabelingTaskRequest(
                context=request.context,
                details=labeling_v1_labeling_task_validation_service_pb2.PreviewLabelingTaskRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(name=request.labeling_task.requester.name)
                ),
                labeling_task=labeling_v1_labeling_pb2.LabelingTask(
                    channel=labeling_v1_labeling_pb2.LabelingTaskChannelOrigin(
                        channel=request.labeling_task.channel.channel
                    ),
                    sla=labeling_v1_labeling_pb2.LabelingTaskSla(breached=request.labeling_task.sla.breached)
                )
            )
            port_0: LabelingTaskCloneLabelingTask0Port = LabelingTaskCloneLabelingTask0Adapter(
                deps.clients.labeling_labeling_task_validation,
                deps.settings.timeout
            )
            response_0 = await port_0.execute(outgoing_0)
            returned_0_0 = response_0.result.details
            response.result.details.update(returned_0_0)
            returned_0_1 = response_0.result.message
            if returned_0_1:
                response.result.message = returned_0_1
            echoed_0 = request.labeling_task.requester
            response.labeling_task.requester.CopyFrom(echoed_0)
            echoed_1 = request.labeling_task.status
            response.labeling_task.status = echoed_1
            return response

    async def handle_create_labeling_task(
        self,
        request: labeling_v1_labeling_task_service_pb2.CreateLabelingTaskRequest
    ) -> labeling_v1_labeling_task_service_pb2.CreateLabelingTaskResponse:
        """Creates a labeling task."""
        deps = self.deps
        response = labeling_v1_labeling_task_service_pb2.CreateLabelingTaskResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CreateLabelingTask', extra={'fields': {'request_id': request.request_id}})
            await deps.repository.audit(
                request.context.tenant_id,
                'CreateLabelingTask',
                {'request_id': request.request_id}
            )
            await deps.repository.save_labeling_task(request.context.tenant_id, request.labeling_task)
            response_0 = labeling_v1_annotation_query_service_pb2.ExportAnnotationsResponse()
            response_1 = featurestore_v1_feature_value_validation_service_pb2.ValidateFeatureValueResponse()
            response_2 = labeling_v1_annotation_query_service_pb2.CountAnnotationsResponse()
            outgoing_0 = labeling_v1_annotation_query_service_pb2.ExportAnnotationsRequest(
                context=request.context,
                filter=labeling_v1_annotation_query_service_pb2.ExportAnnotationsRequest.Filter(
                    created_after=request.labeling_task.audit.updated_at,
                    labels=dict(request.labeling_task.custom_fields),
                    owner_id=request.labeling_task.assignee.user_id
                )
            )
            async for chunk_0 in deps.clients.labeling_annotation_query.ExportAnnotations(
                outgoing_0,
                timeout=deps.settings.timeout
            ):
                response_0 = chunk_0
            outgoing_1 = featurestore_v1_feature_value_validation_service_pb2.ValidateFeatureValueRequest(
                context=request.context,
                details=featurestore_v1_feature_value_validation_service_pb2.ValidateFeatureValueRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(phone=request.labeling_task.requester.phone)
                )
            )
            response_1 = await LabelingTaskCreateLabelingTask1Adapter(
                deps.clients.featurestore_feature_value_validation,
                deps.settings.timeout
            )(outgoing_1)
            requests_2: list[labeling_v1_annotation_query_service_pb2.CountAnnotationsRequest] = []
            for item_2 in request.labeling_task.history:
                outgoing_2 = labeling_v1_annotation_query_service_pb2.CountAnnotationsRequest(
                    context=request.context,
                    filter=labeling_v1_annotation_query_service_pb2.CountAnnotationsRequest.Filter(
                        created_after=item_2.changed_at,
                        labels=dict(response_1.result.details),
                        owner_id=request.labeling_task.assignee.user_id
                    )
                )
                requests_2.append(outgoing_2)
            replies_2 = await asyncio.gather(*(
                deps.clients.labeling_annotation_query.CountAnnotations(
                    entry,
                    timeout=deps.settings.timeout
                ) for entry in requests_2
            ))
            if replies_2:
                response_2 = replies_2[-1]
            returned_1_0 = response_1.feature_value.subject.display_name
            if returned_1_0:
                response.labeling_task.assignee.display_name = returned_1_0
            echoed_0 = request.labeling_task.custom_fields
            response.labeling_task.custom_fields.update(echoed_0)
            echoed_1 = request.labeling_task.subject
            response.labeling_task.subject = echoed_1
            return response

    async def handle_delete_labeling_task(
        self,
        request: labeling_v1_labeling_task_service_pb2.DeleteLabelingTaskRequest
    ) -> labeling_v1_labeling_task_service_pb2.DeleteLabelingTaskResponse:
        """Deletes a labeling task."""
        deps = self.deps
        response = labeling_v1_labeling_task_service_pb2.DeleteLabelingTaskResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('DeleteLabelingTask', extra={'fields': {'force': request.force}})
            await deps.repository.audit(request.context.tenant_id, 'DeleteLabelingTask', {'force': request.force})
            response_0 = labeling_v1_annotation_calculation_service_pb2.CompareAnnotationOptionsResponse()
            response_1 = labeling_v1_labeling_task_calculation_service_pb2.CompareLabelingTaskOptionsResponse()
            response_2 = anomalies_v1_anomaly_feedback_calculation_service_pb2.SimulateAnomalyFeedbackResponse()
            outgoing_0 = labeling_v1_annotation_calculation_service_pb2.CompareAnnotationOptionsRequest(
                annotation=labeling_v1_labeling_pb2.Annotation(
                    occurred_at=request.context.deadline,
                    subject=labeling_v1_refs_pb2.LabelingTaskRef(labeling_task_id=request.labeling_task_id)
                ),
                context=request.context,
                reason=request.reason
            )
            outgoing_1 = labeling_v1_labeling_task_calculation_service_pb2.CompareLabelingTaskOptionsRequest(
                context=request.context,
                labeling_task=labeling_v1_labeling_pb2.LabelingTask(
                    audit=common_v1_audit_pb2.AuditInfo(etag=request.etag)
                )
            )
            response_0, response_1 = await asyncio.gather(
                deps.clients.labeling_annotation_calculation.CompareAnnotationOptions(
                    outgoing_0,
                    timeout=deps.settings.timeout
                ),
                deps.clients.labeling_labeling_task_calculation.CompareLabelingTaskOptions(
                    outgoing_1,
                    timeout=deps.settings.timeout
                ),
            )
            fields_2: dict[str, Any] = {
                'anomaly_feedback': {
                    'occurred_at': response_0.annotation.occurred_at,
                    'sequence': response_0.annotation.sequence,
                    'source': response_0.annotation.source,
                    'subject': {'display_name': response_1.labeling_task.customer.display_name}
                },
                'context': request.context
            }
            outgoing_2 = anomalies_v1_anomaly_feedback_calculation_service_pb2.SimulateAnomalyFeedbackRequest(**fields_2)
            response_2 = await deps.clients.anomalies_anomaly_feedback_calculation.SimulateAnomalyFeedback(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.result.message = returned_0_0
            returned_0_1 = response_0.result.details
            response.result.details.update(returned_0_1)
            returned_1_0 = response_1.result.reference_ids
            response.result.reference_ids.extend(returned_1_0)
            returned_1_1 = response_1.result.correlation_id
            if returned_1_1:
                response.result.correlation_id = returned_1_1
            returned_2_0 = response_2.anomaly_feedback.correlation_id
            if returned_2_0:
                response.result.correlation_id = returned_2_0
            returned_2_1 = response_2.result.status
            if returned_2_1:
                response.result.status = returned_2_1
            return response

    async def handle_get_labeling_task(
        self,
        request: labeling_v1_labeling_task_service_pb2.GetLabelingTaskRequest
    ) -> labeling_v1_labeling_task_service_pb2.GetLabelingTaskResponse:
        """Returns a labeling task."""
        deps = self.deps
        response = labeling_v1_labeling_task_service_pb2.GetLabelingTaskResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('GetLabelingTask', extra={'fields': {'domain': 'labeling'}})
            await deps.repository.audit(request.context.tenant_id, 'GetLabelingTask', {})
            response_0 = modelregistry_v1_registered_model_service_pb2.UpdateRegisteredModelResponse()
            response_1 = anomalies_v1_anomaly_validation_service_pb2.ScoreAnomalyResponse()
            outgoing_0 = modelregistry_v1_registered_model_service_pb2.UpdateRegisteredModelRequest(
                context=request.context,
                registered_model=modelregistry_v1_modelregistry_pb2.RegisteredModel(
                    audit=common_v1_audit_pb2.AuditInfo(created_at=request.context.deadline),
                    owner=identity_v1_refs_pb2.UserRef(
                        email=request.context.actor.email,
                        user_id=request.context.actor.user_id
                    )
                )
            )
            response_0 = await deps.clients.modelregistry_registered_model.UpdateRegisteredModel(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = anomalies_v1_anomaly_validation_service_pb2.ScoreAnomalyRequest(
                anomaly=anomalies_v1_anomalies_pb2.Anomaly(
                    audit=common_v1_audit_pb2.AuditInfo(etag=response_0.registered_model.audit.etag)
                ),
                context=request.context,
                details=anomalies_v1_anomaly_validation_service_pb2.ScoreAnomalyRequest.Details(
                    destination=common_v1_address_pb2.PostalAddress(
                        locality=response_0.registered_model.address.locality,
                        postal_code=response_0.registered_model.address.postal_code
                    )
                )
            )
            document_1 = MessageToJson(outgoing_1, preserving_proto_field_name=True)
            outgoing_1 = Parse(document_1, anomalies_v1_anomaly_validation_service_pb2.ScoreAnomalyRequest())
            response_1 = await deps.clients.anomalies_anomaly_validation.ScoreAnomaly(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.registered_model.audit.created_at
            returned_0_0_part_1 = response.labeling_task.comments.add()
            if returned_0_0.ListFields():
                returned_0_0_part_1.created_at.MergeFrom(returned_0_0)
            returned_1_0 = response_1.result.correlation_id
            if returned_1_0:
                response.result.correlation_id = returned_1_0
            returned_1_1 = response_1.anomaly.audit.created_by
            if returned_1_1:
                response.labeling_task.audit.created_by = returned_1_1
            echoed_0 = request.labeling_task_id
            response.labeling_task.labeling_task_id = echoed_0
            return response

    async def handle_list_labeling_tasks(
        self,
        request: labeling_v1_labeling_task_service_pb2.ListLabelingTasksRequest
    ) -> labeling_v1_labeling_task_service_pb2.ListLabelingTasksResponse:
        """Lists labeling tasks a page at a time."""
        deps = self.deps
        response = labeling_v1_labeling_task_service_pb2.ListLabelingTasksResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ListLabelingTasks', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(request.context.tenant_id, 'ListLabelingTasks', {'order_by': request.order_by})
            response_0 = prescriptions_v1_prescription_query_service_pb2.ResolvePrescriptionsResponse()
            response_1 = lineage_v1_lineage_edge_calculation_service_pb2.CompareLineageEdgeOptionsResponse()
            outgoing_0 = prescriptions_v1_prescription_query_service_pb2.ResolvePrescriptionsRequest(
                context=request.context
            )
            response_0 = await deps.clients.prescriptions_prescription_query.ResolvePrescriptions(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = lineage_v1_lineage_edge_calculation_service_pb2.CompareLineageEdgeOptionsRequest(
                context=request.context,
                details=lineage_v1_lineage_edge_calculation_service_pb2.CompareLineageEdgeOptionsRequest.Details(
                    destination=common_v1_address_pb2.PostalAddress(region=request.filter.region)
                ),
                lineage_edge=lineage_v1_lineage_pb2.LineageEdge(
                    correlation_id=response_0.result.correlation_id,
                    measurements=[
                        lineage_v1_lineage_pb2.LineageEdgeMeasurement(observed_at=request.filter.created_after)
                    ]
                )
            )
            envelope_1 = AnyMessage()
            envelope_1.Pack(outgoing_1)
            outgoing_1 = lineage_v1_lineage_edge_calculation_service_pb2.CompareLineageEdgeOptionsRequest()
            if not envelope_1.Unpack(outgoing_1):
                raise ValueError("partner envelope contains the wrong request type")
            response_1 = await deps.clients.lineage_lineage_edge_calculation.CompareLineageEdgeOptions(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.correlation_id
            if returned_0_0:
                response.result.correlation_id = returned_0_0
            returned_0_1 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_1)
            returned_1_0 = response_1.result.reference_ids
            response.result.reference_ids.extend(returned_1_0)
            return response

    async def handle_search_labeling_tasks(
        self,
        request: labeling_v1_labeling_task_service_pb2.SearchLabelingTasksRequest
    ) -> labeling_v1_labeling_task_service_pb2.SearchLabelingTasksResponse:
        """Lists labeling tasks a page at a time."""
        deps = self.deps
        response = labeling_v1_labeling_task_service_pb2.SearchLabelingTasksResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SearchLabelingTasks', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'SearchLabelingTasks',
                {'order_by': request.order_by}
            )
            response_0 = labeling_v1_label_set_validation_service_pb2.ExplainLabelSetDecisionResponse()
            outgoing_0 = labeling_v1_label_set_validation_service_pb2.ExplainLabelSetDecisionRequest(
                context=request.context,
                label_set=labeling_v1_labeling_pb2.LabelSet(
                    children=[
                        labeling_v1_labeling_pb2.LabelSet(
                            audit=common_v1_audit_pb2.AuditInfo(created_at=request.filter.created_after),
                            children=[
                                labeling_v1_labeling_pb2.LabelSet(
                                    location=common_v1_address_pb2.PostalAddress(region=request.filter.region),
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
            response_0 = await deps.clients.labeling_label_set_validation.ExplainLabelSetDecision(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.label_set.audit.etag
            returned_0_0_part_0 = response.labeling_tasks.add()
            if returned_0_0:
                returned_0_0_part_0.audit.etag = returned_0_0
            return response

    async def handle_update_labeling_task(
        self,
        request: labeling_v1_labeling_task_service_pb2.UpdateLabelingTaskRequest
    ) -> labeling_v1_labeling_task_service_pb2.UpdateLabelingTaskResponse:
        """Changes a labeling task."""
        deps = self.deps
        response = labeling_v1_labeling_task_service_pb2.UpdateLabelingTaskResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('UpdateLabelingTask', extra={'fields': {'allow_missing': request.allow_missing}})
            await deps.repository.audit(
                request.context.tenant_id,
                'UpdateLabelingTask',
                {'allow_missing': request.allow_missing}
            )
            await deps.repository.save_labeling_task(request.context.tenant_id, request.labeling_task)
            response_0 = labeling_v1_label_set_calculation_service_pb2.RecalculateLabelSetsResponse()
            command_0 = LabelingTaskUpdateLabelingTask0Command(
                context=request.context,
                label_set_children_children_audit_created_by=request.labeling_task.audit.created_by,
                label_set_children_children_audit_updated_at=request.labeling_task.audit.updated_at,
                label_set_children_children_audit_etag=request.labeling_task.audit.etag
            )
            outgoing_0 = to_labeling_task_update_labeling_task0_command(command_0)
            response_0 = await deps.clients.labeling_label_set_calculation.RecalculateLabelSets(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.label_set.audit.updated_at
            if returned_0_0.ListFields():
                response.labeling_task.audit.updated_at.MergeFrom(returned_0_0)
            echoed_0 = request.labeling_task.custom_fields
            response.labeling_task.custom_fields.update(echoed_0)
            echoed_1 = request.labeling_task.requester
            response.labeling_task.requester.CopyFrom(echoed_1)
            return response
