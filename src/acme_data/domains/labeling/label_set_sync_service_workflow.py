"""Application workflow for LabelSet Sync."""

from __future__ import annotations

from typing import cast
import asyncio
import logging

from google.protobuf.json_format import MessageToDict
from google.protobuf.json_format import MessageToJson
from google.protobuf.json_format import Parse
from google.protobuf.json_format import ParseDict

from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.labeling.v1 import label_set_calculation_service_pb2 as labeling_v1_label_set_calculation_service_pb2
from acme.labeling.v1 import label_set_sync_service_pb2 as labeling_v1_label_set_sync_service_pb2
from acme.labeling.v1 import label_set_validation_service_pb2 as labeling_v1_label_set_validation_service_pb2
from acme.labeling.v1 import labeling_pb2 as labeling_v1_labeling_pb2
from acme.labeling.v1 import labeling_task_query_service_pb2 as labeling_v1_labeling_task_query_service_pb2
from acme.labeling.v1 import labeling_task_service_pb2 as labeling_v1_labeling_task_service_pb2
from acme.labeling.v1 import labeling_task_validation_service_pb2 as labeling_v1_labeling_task_validation_service_pb2
from acme.lineage.v1 import lineage_node_reporting_service_pb2 as lineage_v1_lineage_node_reporting_service_pb2
from acme.metrics.v1 import metric_alert_admin_service_pb2 as metrics_v1_metric_alert_admin_service_pb2
from acme.metrics.v1 import metrics_pb2 as metrics_v1_metrics_pb2
from acme.notifications.v1 import notification_query_service_pb2 as notifications_v1_notification_query_service_pb2

from acme_data.domains.labeling.adapters import LabelSetSyncPullLabelSets1Adapter
from acme_data.domains.labeling.adapters import LabelSetSyncPullLabelSets1Port
from acme_data.domains.labeling.dependencies import Dependencies
from acme_data.platform.rpc import async_messages
from acme_data.platform.tenancy import tenant_id
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class LabelSetSyncServicerWorkflow:
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    async def handle_list_label_set_conflicts(
        self,
        request: labeling_v1_label_set_sync_service_pb2.ListLabelSetConflictsRequest
    ) -> labeling_v1_label_set_sync_service_pb2.ListLabelSetConflictsResponse:
        """Lists label sets a page at a time."""
        deps = self.deps
        response = labeling_v1_label_set_sync_service_pb2.ListLabelSetConflictsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ListLabelSetConflicts', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ListLabelSetConflicts',
                {'order_by': request.order_by}
            )
            return response

    async def handle_pull_label_sets(
        self,
        request: labeling_v1_label_set_sync_service_pb2.PullLabelSetsRequest
    ) -> labeling_v1_label_set_sync_service_pb2.PullLabelSetsResponse:
        """Pulls a label set."""
        deps = self.deps
        response = labeling_v1_label_set_sync_service_pb2.PullLabelSetsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('PullLabelSets', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'PullLabelSets', {'reason': request.reason})
            await deps.repository.save_label_set(request.context.tenant_id, request.label_set)
            response_0 = labeling_v1_labeling_task_validation_service_pb2.ExplainLabelingTaskDecisionResponse()
            response_1 = labeling_v1_labeling_task_service_pb2.BatchGetLabelingTasksResponse()
            outgoing_0 = labeling_v1_labeling_task_validation_service_pb2.ExplainLabelingTaskDecisionRequest()
            outgoing_0.context.CopyFrom(request.context)
            outgoing_0.labeling_task.audit.updated_at.CopyFrom(request.label_set.audit.updated_at)
            outgoing_0.labeling_task.audit.updated_by = request.label_set.audit.updated_by
            outgoing_0.labeling_task.assignee.email = request.label_set.manager.email
            outgoing_0.labeling_task.assignee.display_name = request.label_set.manager.display_name
            outgoing_0.context.tenant_id = tenant_id.get()
            response_0 = await deps.clients.labeling_labeling_task_validation.ExplainLabelingTaskDecision(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = labeling_v1_labeling_task_service_pb2.BatchGetLabelingTasksRequest(context=request.context)
            port_1: LabelSetSyncPullLabelSets1Port = LabelSetSyncPullLabelSets1Adapter(
                deps.clients.labeling_labeling_task,
                deps.settings.timeout
            )
            response_1 = await port_1.execute(outgoing_1)
            returned_0_0 = response_0.labeling_task.audit.updated_at
            returned_0_0_part_1 = response.label_set.children.add()
            if returned_0_0.ListFields():
                returned_0_0_part_1.audit.updated_at.MergeFrom(returned_0_0)
            returned_1_0 = response_1.result.message
            if returned_1_0:
                response.result.message = returned_1_0
            returned_1_1 = response_1.result.correlation_id
            if returned_1_1:
                response.result.correlation_id = returned_1_1
            echoed_0 = request.label_set_id
            response.label_set.label_set_id = echoed_0
            echoed_1 = request.label_set.status
            response.label_set.status = echoed_1
            return response

    async def handle_push_label_set(
        self,
        request: labeling_v1_label_set_sync_service_pb2.PushLabelSetRequest
    ) -> labeling_v1_label_set_sync_service_pb2.PushLabelSetResponse:
        """Pushs a label set."""
        deps = self.deps
        response = labeling_v1_label_set_sync_service_pb2.PushLabelSetResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('PushLabelSet', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'PushLabelSet', {'reason': request.reason})
            await deps.repository.save_label_set(request.context.tenant_id, request.label_set)
            response_0 = metrics_v1_metric_alert_admin_service_pb2.RepairMetricAlertResponse()
            response_1 = labeling_v1_labeling_task_query_service_pb2.CountLabelingTasksResponse()
            outgoing_0 = metrics_v1_metric_alert_admin_service_pb2.RepairMetricAlertRequest(
                context=request.context,
                metric_alert=metrics_v1_metrics_pb2.MetricAlert(
                    audit=common_v1_audit_pb2.AuditInfo(
                        etag=request.label_set.audit.etag,
                        updated_by=request.label_set.audit.updated_by
                    )
                )
            )
            outgoing_1 = labeling_v1_labeling_task_query_service_pb2.CountLabelingTasksRequest(
                context=request.context,
                filter=labeling_v1_labeling_task_query_service_pb2.CountLabelingTasksRequest.Filter(
                    created_after=request.label_set.audit.updated_at,
                    region=request.label_set.location.region
                )
            )
            response_0, response_1 = await asyncio.gather(
                deps.clients.metrics_metric_alert_admin.RepairMetricAlert(outgoing_0, timeout=deps.settings.timeout),
                deps.clients.labeling_labeling_task_query.CountLabelingTasks(outgoing_1, timeout=deps.settings.timeout),
            )
            returned_0_0 = response_0.metric_alert.owner.display_name
            returned_0_0_part_1 = response.label_set.children.add()
            if returned_0_0:
                returned_0_0_part_1.manager.display_name = returned_0_0
            returned_1_0 = response_1.result.reference_ids
            response.result.reference_ids.extend(returned_1_0)
            returned_1_1 = response_1.result.details
            response.result.details.update(returned_1_1)
            echoed_0 = request.label_set_id
            response.label_set.label_set_id = echoed_0
            echoed_1 = request.label_set.depth
            response.label_set.depth = echoed_1
            return response

    async def handle_resolve_label_set_conflict(
        self,
        request: labeling_v1_label_set_sync_service_pb2.ResolveLabelSetConflictRequest
    ) -> labeling_v1_label_set_sync_service_pb2.ResolveLabelSetConflictResponse:
        """Resolves a label set."""
        deps = self.deps
        response = labeling_v1_label_set_sync_service_pb2.ResolveLabelSetConflictResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ResolveLabelSetConflict', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ResolveLabelSetConflict',
                {'reason': request.reason}
            )
            await deps.repository.save_label_set(request.context.tenant_id, request.label_set)
            response_0 = lineage_v1_lineage_node_reporting_service_pb2.CountLineageNodeTotalsResponse()
            response_1 = labeling_v1_labeling_task_service_pb2.BatchGetLabelingTasksResponse()
            outgoing_0 = lineage_v1_lineage_node_reporting_service_pb2.CountLineageNodeTotalsRequest(
                context=request.context,
                filter=lineage_v1_lineage_node_reporting_service_pb2.CountLineageNodeTotalsRequest.Filter(
                    created_after=request.label_set.audit.updated_at,
                    region=request.label_set.location.region
                )
            )
            response_0 = cast(lineage_v1_lineage_node_reporting_service_pb2.CountLineageNodeTotalsResponse, await deps.bus.request(
                'acme.labeling.v1.LabelSetSyncService/ResolveLabelSetConflict/0', outgoing_0, deps.settings.timeout,
            ))
            outgoing_1 = labeling_v1_labeling_task_service_pb2.BatchGetLabelingTasksRequest(context=request.context)
            response_1 = await deps.clients.labeling_labeling_task.BatchGetLabelingTasks(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_0)
            returned_0_1 = response_0.result.message
            if returned_0_1:
                response.result.message = returned_0_1
            returned_1_0 = response_1.result.message
            if returned_1_0:
                response.outcome.message = returned_1_0
            returned_1_1 = response_1.result.details
            response.result.details.update(returned_1_1)
            echoed_0 = request.label_set_id
            response.label_set.label_set_id = echoed_0
            echoed_1 = request.label_set.depth
            response.label_set.depth = echoed_1
            return response

    async def handle_stream_label_set_changes(
        self,
        request: labeling_v1_label_set_sync_service_pb2.StreamLabelSetChangesRequest
    ) -> labeling_v1_label_set_sync_service_pb2.StreamLabelSetChangesResponse:
        """Exchanges changes of label sets with a peer."""
        deps = self.deps
        response = labeling_v1_label_set_sync_service_pb2.StreamLabelSetChangesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('StreamLabelSetChanges', extra={'fields': {'cursor': request.cursor}})
            await deps.repository.audit(request.context.tenant_id, 'StreamLabelSetChanges', {'cursor': request.cursor})
            if request.WhichOneof('frame') == 'change':
                await deps.repository.save_label_set(request.context.tenant_id, request.change)
            response_0 = labeling_v1_label_set_calculation_service_pb2.EstimateLabelSetResponse()
            response_1 = notifications_v1_notification_query_service_pb2.ExportNotificationsResponse()
            outgoing_0 = labeling_v1_label_set_calculation_service_pb2.EstimateLabelSetRequest(
                context=request.context,
                label_set=labeling_v1_labeling_pb2.LabelSet(
                    children=[
                        labeling_v1_labeling_pb2.LabelSet(
                            children=[
                                labeling_v1_labeling_pb2.LabelSet(
                                    audit=common_v1_audit_pb2.AuditInfo(created_at=request.change.audit.created_at),
                                    location=common_v1_address_pb2.PostalAddress(
                                        locality=request.change.location.locality,
                                        postal_code=request.change.location.postal_code
                                    )
                                )
                            ]
                        )
                    ]
                )
            )
            method_name_0 = 'EstimateLabelSet'
            response_0 = await getattr(
                deps.clients.labeling_label_set_calculation,
                method_name_0
            )(outgoing_0, timeout=deps.settings.timeout)
            outgoing_1 = notifications_v1_notification_query_service_pb2.ExportNotificationsRequest(
                context=request.context,
                filter=notifications_v1_notification_query_service_pb2.ExportNotificationsRequest.Filter(
                    created_after=response_0.label_set.audit.created_at,
                    labels=dict(request.change.attributes),
                    owner_id=request.change.manager.user_id,
                    region=request.change.location.region
                )
            )
            async for chunk_1 in deps.clients.notifications_notification_query.ExportNotifications(
                outgoing_1,
                timeout=deps.settings.timeout
            ):
                response_1 = chunk_1
            returned_0_0 = response_0.label_set.audit.created_at
            returned_0_0_part_1 = response.label_set.children.add()
            if returned_0_0.ListFields():
                returned_0_0_part_1.audit.created_at.MergeFrom(returned_0_0)
            echoed_0 = request.change.manager
            response.label_set.manager.CopyFrom(echoed_0)
            echoed_1 = request.change.location
            response.label_set.location.CopyFrom(echoed_1)
            return response

    async def handle_sync_label_sets(
        self,
        request: labeling_v1_label_set_sync_service_pb2.SyncLabelSetsRequest
    ) -> labeling_v1_label_set_sync_service_pb2.SyncLabelSetsResponse:
        """Syncs a label set."""
        deps = self.deps
        response = labeling_v1_label_set_sync_service_pb2.SyncLabelSetsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SyncLabelSets', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'SyncLabelSets', {'reason': request.reason})
            await deps.repository.save_label_set(request.context.tenant_id, request.label_set)
            response_0 = labeling_v1_label_set_validation_service_pb2.GetLabelSetRulesResponse()
            response_1 = labeling_v1_labeling_task_validation_service_pb2.CheckLabelingTaskEligibilityResponse()
            outgoing_0 = labeling_v1_label_set_validation_service_pb2.GetLabelSetRulesRequest(
                context=request.context,
                label_set_id=request.label_set_id
            )
            document_0 = MessageToDict(outgoing_0, preserving_proto_field_name=True)
            outgoing_0 = ParseDict(document_0, labeling_v1_label_set_validation_service_pb2.GetLabelSetRulesRequest())
            response_0 = await deps.clients.labeling_label_set_validation.GetLabelSetRules(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = labeling_v1_labeling_task_validation_service_pb2.CheckLabelingTaskEligibilityRequest(
                context=request.context,
                details=labeling_v1_labeling_task_validation_service_pb2.CheckLabelingTaskEligibilityRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(email=response_0.label_set.manager.email)
                ),
                labeling_task=labeling_v1_labeling_pb2.LabelingTask(
                    assignee=identity_v1_refs_pb2.UserRef(email=request.label_set.manager.email),
                    audit=common_v1_audit_pb2.AuditInfo(updated_by=request.label_set.audit.updated_by)
                )
            )
            document_1 = MessageToJson(outgoing_1, preserving_proto_field_name=True)
            outgoing_1 = Parse(
                document_1,
                labeling_v1_labeling_task_validation_service_pb2.CheckLabelingTaskEligibilityRequest()
            )
            response_1 = await deps.clients.labeling_labeling_task_validation.CheckLabelingTaskEligibility(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.label_set.manager
            returned_0_0_part_1 = response.label_set.children.add()
            if returned_0_0.ListFields():
                returned_0_0_part_1.manager.MergeFrom(returned_0_0)
            returned_0_1 = response_0.label_set.location
            if returned_0_1.ListFields():
                response.label_set.location.MergeFrom(returned_0_1)
            returned_1_0 = response_1.labeling_task.customer.display_name
            returned_1_0_part_1 = response.label_set.children.add()
            returned_1_0_part_2 = returned_1_0_part_1.children.add()
            if returned_1_0:
                returned_1_0_part_2.manager.display_name = returned_1_0
            echoed_0 = request.label_set_id
            response.label_set.label_set_id = echoed_0
            echoed_1 = request.label_set.attributes
            response.label_set.attributes.update(echoed_1)
            return response
