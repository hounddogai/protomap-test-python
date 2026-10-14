"""Routes entities through approval, with escalation and delegation."""

from __future__ import annotations

from collections.abc import AsyncIterator
from functools import partial
from typing import cast
import asyncio
import logging

import grpc

from acme.anomalies.v1 import anomalies_pb2 as anomalies_v1_anomalies_pb2
from acme.anomalies.v1 import anomaly_workflow_service_pb2 as anomalies_v1_anomaly_workflow_service_pb2
from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.datasets.v1 import dataset_service_pb2 as datasets_v1_dataset_service_pb2
from acme.featurestore.v1 import entity_approval_service_pb2 as featurestore_v1_entity_approval_service_pb2
from acme.featurestore.v1 import entity_approval_service_pb2_grpc as featurestore_v1_entity_approval_service_pb2_grpc
from acme.featurestore.v1 import entity_import_service_pb2 as featurestore_v1_entity_import_service_pb2
from acme.featurestore.v1 import (
    feature_value_approval_service_pb2 as featurestore_v1_feature_value_approval_service_pb2,
)
from acme.featurestore.v1 import feature_value_sync_service_pb2 as featurestore_v1_feature_value_sync_service_pb2
from acme.featurestore.v1 import feature_view_sync_service_pb2 as featurestore_v1_feature_view_sync_service_pb2
from acme.featurestore.v1 import featurestore_pb2 as featurestore_v1_featurestore_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.lineage.v1 import lineage_edge_import_service_pb2 as lineage_v1_lineage_edge_import_service_pb2
from acme.lineage.v1 import lineage_pb2 as lineage_v1_lineage_pb2
from acme.lineage.v1 import refs_pb2 as lineage_v1_refs_pb2
from acme.metrics.v1 import dashboard_export_service_pb2 as metrics_v1_dashboard_export_service_pb2
from acme.metrics.v1 import metric_alert_notification_service_pb2 as metrics_v1_metric_alert_notification_service_pb2
from acme.search.v1 import search_index_validation_service_pb2 as search_v1_search_index_validation_service_pb2

from acme_data.domains.featurestore import hooks
from acme_data.domains.featurestore.adapters import EntityApprovalRecallEntity0Adapter
from acme_data.domains.featurestore.adapters import EntityApprovalRecallEntity0Port
from acme_data.domains.featurestore.adapters import EntityApprovalRecallEntity2Adapter
from acme_data.domains.featurestore.dependencies import Dependencies
from acme_data.domains.featurestore.models import EntityApprovalApproveEntity0Command
from acme_data.domains.featurestore.models import to_entity_approval_approve_entity0_command
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import run_steps
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_id
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class EntityApprovalServicer(featurestore_v1_entity_approval_service_pb2_grpc.EntityApprovalServiceServicer):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    async def ApproveEntity(
        self, request: featurestore_v1_entity_approval_service_pb2.ApproveEntityRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_entity_approval_service_pb2.ApproveEntityResponse:
        """Approves an entity."""
        return await self.handle_approve_entity(request)

    @rpc_errors
    async def CommentEntityApproval(
        self, request: featurestore_v1_entity_approval_service_pb2.CommentEntityApprovalRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_entity_approval_service_pb2.CommentEntityApprovalResponse:
        """Comments an entity."""
        return await self.handle_comment_entity_approval(request)

    @rpc_errors
    @retry_transient
    async def ListPendingEntities(
        self, request: featurestore_v1_entity_approval_service_pb2.ListPendingEntitiesRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_entity_approval_service_pb2.ListPendingEntitiesResponse:
        """Lists entities a page at a time."""
        return await self.handle_list_pending_entities(request)

    @rpc_errors
    async def RecallEntity(
        self, request: featurestore_v1_entity_approval_service_pb2.RecallEntityRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_entity_approval_service_pb2.RecallEntityResponse:
        """Recalls an entity."""
        return await self.handle_recall_entity(request)

    @rpc_errors
    async def RejectEntity(
        self, request: featurestore_v1_entity_approval_service_pb2.RejectEntityRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_entity_approval_service_pb2.RejectEntityResponse:
        """Rejects an entity."""
        return await self.handle_reject_entity(request)

    @rpc_errors
    async def SubmitEntity(
        self, request: featurestore_v1_entity_approval_service_pb2.SubmitEntityRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_entity_approval_service_pb2.SubmitEntityResponse:
        """Submits an entity."""
        return await self.handle_submit_entity(request)

    async def handle_approve_entity(
        self,
        request: featurestore_v1_entity_approval_service_pb2.ApproveEntityRequest
    ) -> featurestore_v1_entity_approval_service_pb2.ApproveEntityResponse:
        """Approves an entity."""
        deps = self.deps
        response = featurestore_v1_entity_approval_service_pb2.ApproveEntityResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ApproveEntity', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'ApproveEntity', {'reason': request.reason})
            await deps.repository.save_entity(request.context.tenant_id, request.entity)
            response_0 = search_v1_search_index_validation_service_pb2.PreviewSearchIndexResponse()
            command_0 = EntityApprovalApproveEntity0Command(
                context=request.context,
                details_contact_email=request.entity.contact.email,
                details_contact_preferred_channel=request.entity.contact.preferred_channel,
                search_index_owner_email=request.details.approver.email
            )
            outgoing_0 = to_entity_approval_approve_entity0_command(command_0)
            response_0 = await deps.clients.search_search_index_validation.PreviewSearchIndex(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.outcome.message
            if returned_0_0:
                response.result.message = returned_0_0
            echoed_0 = request.entity_id
            response.entity.entity_id = echoed_0
            echoed_1 = request.entity.contact
            response.entity.contact.CopyFrom(echoed_1)
            return response

    async def handle_comment_entity_approval(
        self,
        request: featurestore_v1_entity_approval_service_pb2.CommentEntityApprovalRequest
    ) -> featurestore_v1_entity_approval_service_pb2.CommentEntityApprovalResponse:
        """Comments an entity."""
        deps = self.deps
        response = featurestore_v1_entity_approval_service_pb2.CommentEntityApprovalResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CommentEntityApproval', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'CommentEntityApproval', {'reason': request.reason})
            await deps.repository.save_entity(request.context.tenant_id, request.entity)
            response_0 = metrics_v1_dashboard_export_service_pb2.StreamDashboardExportResponse()
            response_1 = lineage_v1_lineage_edge_import_service_pb2.RetryLineageEdgeImportResponse()
            response_2 = featurestore_v1_feature_value_sync_service_pb2.ListFeatureValueConflictsResponse()
            response_3 = metrics_v1_metric_alert_notification_service_pb2.SubscribeMetricAlertUpdatesResponse()
            outgoing_0 = metrics_v1_dashboard_export_service_pb2.StreamDashboardExportRequest(
                context=request.context,
                filter=metrics_v1_dashboard_export_service_pb2.StreamDashboardExportRequest.Filter(
                    region=request.entity.primary_address.region
                )
            )
            async for chunk_0 in deps.clients.metrics_dashboard_export.StreamDashboardExport(
                outgoing_0,
                timeout=deps.settings.timeout
            ):
                response_0 = chunk_0
            outgoing_1 = lineage_v1_lineage_edge_import_service_pb2.RetryLineageEdgeImportRequest(
                context=request.context,
                details=lineage_v1_lineage_edge_import_service_pb2.RetryLineageEdgeImportRequest.Details(
                    notify=common_v1_contact_pb2.ContactInfo(
                        email=request.details.approver.email,
                        name=request.entity.contact.name,
                        preferred_channel=request.entity.contact.preferred_channel
                    )
                ),
                lineage_edge=lineage_v1_lineage_pb2.LineageEdge(
                    subject=lineage_v1_refs_pb2.ImpactRef(display_name=request.entity.relationship_manager.display_name)
                )
            )
            send_1 = partial(
                deps.clients.lineage_lineage_edge_import.RetryLineageEdgeImport,
                timeout=deps.settings.timeout
            )
            response_1 = await send_1(outgoing_1)
            outgoing_2 = featurestore_v1_feature_value_sync_service_pb2.ListFeatureValueConflictsRequest(
                context=request.context,
                filter=featurestore_v1_feature_value_sync_service_pb2.ListFeatureValueConflictsRequest.Filter(
                    region=request.entity.primary_address.region
                )
            )
            response_2 = await hooks.entity_approval_comment_entity_approval2(
                deps.clients.featurestore_feature_value_sync,
                outgoing_2,
                deps.settings.timeout
            )
            outgoing_3 = metrics_v1_metric_alert_notification_service_pb2.SubscribeMetricAlertUpdatesRequest()
            outgoing_3.context.CopyFrom(request.context)
            outgoing_3.details.recipient.email = request.entity.contact.email
            outgoing_3.details.recipient.phone = request.entity.contact.phone
            outgoing_3.context.tenant_id = tenant_id.get()
            response_3 = await deps.clients.metrics_metric_alert_notification.SubscribeMetricAlertUpdates(
                outgoing_3,
                timeout=deps.settings.timeout
            )
            returned_1_0 = response_1.outcome.status
            if returned_1_0:
                response.result.status = returned_1_0
            returned_2_0 = response_2.result.status
            if returned_2_0:
                response.result.status = returned_2_0
            returned_3_0 = response_3.outcome.next_steps
            response.outcome.next_steps.extend(returned_3_0)
            returned_3_1 = response_3.outcome.message
            if returned_3_1:
                response.result.message = returned_3_1
            echoed_0 = request.entity_id
            response.entity.entity_id = echoed_0
            echoed_1 = request.entity.relationship_manager
            response.entity.relationship_manager.CopyFrom(echoed_1)
            return response

    async def handle_list_pending_entities(
        self,
        request: featurestore_v1_entity_approval_service_pb2.ListPendingEntitiesRequest
    ) -> featurestore_v1_entity_approval_service_pb2.ListPendingEntitiesResponse:
        """Lists entities a page at a time."""
        deps = self.deps
        response = featurestore_v1_entity_approval_service_pb2.ListPendingEntitiesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ListPendingEntities', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ListPendingEntities',
                {'order_by': request.order_by}
            )
            return response

    async def handle_recall_entity(
        self,
        request: featurestore_v1_entity_approval_service_pb2.RecallEntityRequest
    ) -> featurestore_v1_entity_approval_service_pb2.RecallEntityResponse:
        """Recalls an entity."""
        deps = self.deps
        response = featurestore_v1_entity_approval_service_pb2.RecallEntityResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('RecallEntity', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'RecallEntity', {'reason': request.reason})
            await deps.repository.save_entity(request.context.tenant_id, request.entity)
            response_0 = featurestore_v1_entity_import_service_pb2.ListEntityImportsResponse()
            response_1 = featurestore_v1_feature_view_sync_service_pb2.SyncFeatureViewsResponse()
            response_2 = anomalies_v1_anomaly_workflow_service_pb2.AdvanceAnomalyWorkflowResponse()
            outgoing_0 = featurestore_v1_entity_import_service_pb2.ListEntityImportsRequest(
                context=request.context,
                filter=featurestore_v1_entity_import_service_pb2.ListEntityImportsRequest.Filter(
                    created_after=request.entity.audit.created_at,
                    labels=dict(request.annotations),
                    owner_id=request.details.approver.user_id,
                    region=request.entity.primary_address.region
                )
            )
            port_0: EntityApprovalRecallEntity0Port = EntityApprovalRecallEntity0Adapter(
                deps.clients.featurestore_entity_import,
                deps.settings.timeout
            )
            response_0 = await port_0.execute(outgoing_0)
            outgoing_1 = featurestore_v1_feature_view_sync_service_pb2.SyncFeatureViewsRequest(
                context=request.context,
                feature_view=featurestore_v1_featurestore_pb2.FeatureView(
                    address=common_v1_address_pb2.PostalAddress(
                        country_code=request.entity.primary_address.country_code,
                        locality=request.entity.primary_address.locality
                    ),
                    audit=common_v1_audit_pb2.AuditInfo(
                        created_by=request.entity.audit.created_by,
                        updated_by=request.entity.audit.updated_by
                    )
                )
            )
            steps_1 = [
                partial(
                    deps.clients.featurestore_feature_view_sync.SyncFeatureViews,
                    outgoing_1,
                    timeout=deps.settings.timeout
                )
            ]
            results_1 = await run_steps(steps_1)
            response_1 = results_1[-1]
            outgoing_2 = anomalies_v1_anomaly_workflow_service_pb2.AdvanceAnomalyWorkflowRequest(
                anomaly=anomalies_v1_anomalies_pb2.Anomaly(
                    audit=common_v1_audit_pb2.AuditInfo(created_by=response_1.feature_view.audit.created_by)
                ),
                context=request.context,
                details=anomalies_v1_anomaly_workflow_service_pb2.AdvanceAnomalyWorkflowRequest.Details(
                    notify=common_v1_contact_pb2.ContactInfo(name=request.entity.contact.name)
                )
            )
            response_2 = await EntityApprovalRecallEntity2Adapter(
                deps.clients.anomalies_anomaly_workflow,
                deps.settings.timeout
            )(outgoing_2)
            returned_0_0 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_0)
            returned_0_1 = response_0.result.status
            if returned_0_1:
                response.result.status = returned_0_1
            returned_1_0 = response_1.feature_view.address.locality
            if returned_1_0:
                response.entity.primary_address.locality = returned_1_0
            returned_1_1 = response_1.feature_view.owner.email
            if returned_1_1:
                response.entity.relationship_manager.email = returned_1_1
            returned_2_0 = response_2.anomaly.audit.created_by
            if returned_2_0:
                response.entity.audit.created_by = returned_2_0
            returned_2_1 = response_2.result.message
            if returned_2_1:
                response.result.message = returned_2_1
            echoed_0 = request.entity_id
            response.entity.entity_id = echoed_0
            echoed_1 = request.entity.name
            response.entity.contact.name.CopyFrom(echoed_1)
            return response

    async def handle_reject_entity(
        self,
        request: featurestore_v1_entity_approval_service_pb2.RejectEntityRequest
    ) -> featurestore_v1_entity_approval_service_pb2.RejectEntityResponse:
        """Rejects an entity."""
        deps = self.deps
        response = featurestore_v1_entity_approval_service_pb2.RejectEntityResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('RejectEntity', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'RejectEntity', {'reason': request.reason})
            await deps.repository.save_entity(request.context.tenant_id, request.entity)
            response_0 = datasets_v1_dataset_service_pb2.BatchGetDatasetsResponse()
            outgoing_0 = datasets_v1_dataset_service_pb2.BatchGetDatasetsRequest(context=request.context)
            response_0 = cast(datasets_v1_dataset_service_pb2.BatchGetDatasetsResponse, await deps.bus.request(
                'acme.featurestore.v1.EntityApprovalService/RejectEntity/0', outgoing_0, deps.settings.timeout,
            ))
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.result.message = returned_0_0
            returned_0_1 = response_0.result.details
            response.result.details.update(returned_0_1)
            echoed_0 = request.entity_id
            response.entity.entity_id = echoed_0
            echoed_1 = request.entity.name
            response.entity.contact.name.CopyFrom(echoed_1)
            return response

    async def handle_submit_entity(
        self,
        request: featurestore_v1_entity_approval_service_pb2.SubmitEntityRequest
    ) -> featurestore_v1_entity_approval_service_pb2.SubmitEntityResponse:
        """Submits an entity."""
        deps = self.deps
        response = featurestore_v1_entity_approval_service_pb2.SubmitEntityResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SubmitEntity', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'SubmitEntity', {'reason': request.reason})
            await deps.repository.save_entity(request.context.tenant_id, request.entity)
            response_0 = featurestore_v1_feature_value_approval_service_pb2.CommentFeatureValueApprovalResponse()
            response_1 = featurestore_v1_entity_import_service_pb2.ListEntityImportsResponse()
            response_2 = lineage_v1_lineage_edge_import_service_pb2.RetryLineageEdgeImportResponse()
            outgoing_0 = featurestore_v1_feature_value_approval_service_pb2.CommentFeatureValueApprovalRequest(
                context=request.context,
                details=featurestore_v1_feature_value_approval_service_pb2.CommentFeatureValueApprovalRequest.Details(
                    approver=identity_v1_refs_pb2.UserRef(
                        display_name=request.entity.relationship_manager.display_name,
                        email=request.entity.contact.email,
                        user_id=request.entity.relationship_manager.user_id
                    )
                )
            )
            outgoing_1 = featurestore_v1_entity_import_service_pb2.ListEntityImportsRequest(
                context=request.context,
                filter=featurestore_v1_entity_import_service_pb2.ListEntityImportsRequest.Filter(
                    created_after=request.entity.audit.created_at,
                    region=request.entity.primary_address.region
                )
            )
            outgoing_2 = lineage_v1_lineage_edge_import_service_pb2.RetryLineageEdgeImportRequest(
                context=request.context,
                details=lineage_v1_lineage_edge_import_service_pb2.RetryLineageEdgeImportRequest.Details(
                    notify=common_v1_contact_pb2.ContactInfo(
                        email=request.details.approver.email,
                        name=request.entity.name,
                        preferred_channel=request.entity.contact.preferred_channel
                    )
                ),
                lineage_edge=lineage_v1_lineage_pb2.LineageEdge(
                    subject=lineage_v1_refs_pb2.ImpactRef(display_name=request.entity.relationship_manager.display_name)
                )
            )
            response_0, response_1, response_2 = await asyncio.gather(
                deps.clients.featurestore_feature_value_approval.CommentFeatureValueApproval(
                    outgoing_0,
                    timeout=deps.settings.timeout
                ),
                deps.clients.featurestore_entity_import.ListEntityImports(outgoing_1, timeout=deps.settings.timeout),
                deps.clients.lineage_lineage_edge_import.RetryLineageEdgeImport(
                    outgoing_2,
                    timeout=deps.settings.timeout
                ),
            )
            returned_0_0 = response_0.result.status
            if returned_0_0:
                response.outcome.status = returned_0_0
            returned_0_1 = response_0.outcome.message
            if returned_0_1:
                response.outcome.message = returned_0_1
            returned_1_0 = response_1.result.correlation_id
            if returned_1_0:
                response.result.correlation_id = returned_1_0
            returned_2_0 = response_2.lineage_edge.correlation_id
            if returned_2_0:
                response.result.correlation_id = returned_2_0
            returned_2_1 = response_2.lineage_edge.attributes
            response.entity.attributes.update(returned_2_1)
            echoed_0 = request.entity_id
            response.entity.entity_id = echoed_0
            echoed_1 = request.details.effective_at
            response.outcome.effective_at.CopyFrom(echoed_1)
            return response
