"""Application workflow for PipelineRun Sync."""

from __future__ import annotations

from collections.abc import Awaitable
from collections.abc import Callable
from typing import Any
import asyncio
import logging

from google.protobuf.json_format import MessageToDict
from google.protobuf.json_format import ParseDict

from acme.chat.v1 import chat_pb2 as chat_v1_chat_pb2
from acme.chat.v1 import chat_room_service_pb2 as chat_v1_chat_room_service_pb2
from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.featurestore.v1 import (
    feature_value_approval_service_pb2 as featurestore_v1_feature_value_approval_service_pb2,
)
from acme.featurestore.v1 import feature_view_approval_service_pb2 as featurestore_v1_feature_view_approval_service_pb2
from acme.featurestore.v1 import featurestore_pb2 as featurestore_v1_featurestore_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.labeling.v1 import label_set_approval_service_pb2 as labeling_v1_label_set_approval_service_pb2
from acme.ledger.v1 import ledger_account_query_service_pb2 as ledger_v1_ledger_account_query_service_pb2
from acme.ledger.v1 import ledger_account_service_pb2 as ledger_v1_ledger_account_service_pb2
from acme.modelregistry.v1 import deployment_approval_service_pb2 as modelregistry_v1_deployment_approval_service_pb2
from acme.modelregistry.v1 import deployment_sync_service_pb2 as modelregistry_v1_deployment_sync_service_pb2
from acme.modelregistry.v1 import modelregistry_pb2 as modelregistry_v1_modelregistry_pb2
from acme.modelregistry.v1 import (
    registered_model_approval_service_pb2 as modelregistry_v1_registered_model_approval_service_pb2,
)
from acme.pipelines.v1 import pipeline_run_sync_service_pb2 as pipelines_v1_pipeline_run_sync_service_pb2
from acme.pipelines.v1 import pipeline_service_pb2 as pipelines_v1_pipeline_service_pb2
from acme.pipelines.v1 import pipeline_step_import_service_pb2 as pipelines_v1_pipeline_step_import_service_pb2
from acme.pipelines.v1 import pipeline_sync_service_pb2 as pipelines_v1_pipeline_sync_service_pb2
from acme.pipelines.v1 import pipelines_pb2 as pipelines_v1_pipelines_pb2
from acme.promotions.v1 import promotion_query_service_pb2 as promotions_v1_promotion_query_service_pb2

from acme_data.domains.pipelines.adapters import PipelineRunSyncSyncPipelineRuns0Adapter
from acme_data.domains.pipelines.adapters import PipelineRunSyncSyncPipelineRuns0Port
from acme_data.domains.pipelines.dependencies import Dependencies
from acme_data.domains.pipelines.models import PipelineRunSyncResolvePipelineRunConflict0Command
from acme_data.domains.pipelines.models import PipelineRunSyncResolvePipelineRunConflict1Command
from acme_data.domains.pipelines.models import to_pipeline_run_sync_resolve_pipeline_run_conflict0_command
from acme_data.domains.pipelines.models import to_pipeline_run_sync_resolve_pipeline_run_conflict1_command
from acme_data.platform.rpc import async_messages
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class PipelineRunSyncServicerWorkflow:
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    async def handle_get_pipeline_run_sync_state(
        self,
        request: pipelines_v1_pipeline_run_sync_service_pb2.GetPipelineRunSyncStateRequest
    ) -> pipelines_v1_pipeline_run_sync_service_pb2.GetPipelineRunSyncStateResponse:
        """Returns a pipeline run."""
        deps = self.deps
        response = pipelines_v1_pipeline_run_sync_service_pb2.GetPipelineRunSyncStateResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('GetPipelineRunSyncState', extra={'fields': {'domain': 'pipelines'}})
            await deps.repository.audit(request.context.tenant_id, 'GetPipelineRunSyncState', {})
            response_0 = pipelines_v1_pipeline_sync_service_pb2.PushPipelineResponse()
            outgoing_0 = pipelines_v1_pipeline_sync_service_pb2.PushPipelineRequest(
                context=request.context,
                pipeline=pipelines_v1_pipelines_pb2.Pipeline(
                    audit=common_v1_audit_pb2.AuditInfo(updated_at=request.context.deadline),
                    organizer=identity_v1_refs_pb2.UserRef(user_id=request.context.actor.user_id),
                    participants=[
                        pipelines_v1_pipelines_pb2.PipelineParticipant(
                            contact=common_v1_contact_pb2.ContactInfo(email=request.context.actor.email)
                        )
                    ]
                )
            )
            response_0 = await deps.clients.pipelines_pipeline_sync.PushPipeline(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.pipeline.audit.updated_by
            if returned_0_0:
                response.pipeline_run.audit.updated_by = returned_0_0
            echoed_0 = request.pipeline_run_id
            response.pipeline_run.pipeline_run_id = echoed_0
            return response

    async def handle_list_pipeline_run_conflicts(
        self,
        request: pipelines_v1_pipeline_run_sync_service_pb2.ListPipelineRunConflictsRequest
    ) -> pipelines_v1_pipeline_run_sync_service_pb2.ListPipelineRunConflictsResponse:
        """Lists pipeline runs a page at a time."""
        deps = self.deps
        response = pipelines_v1_pipeline_run_sync_service_pb2.ListPipelineRunConflictsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ListPipelineRunConflicts', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ListPipelineRunConflicts',
                {'order_by': request.order_by}
            )
            response_0 = chat_v1_chat_room_service_pb2.CloneChatRoomResponse()
            response_1 = ledger_v1_ledger_account_service_pb2.SearchLedgerAccountsResponse()
            outgoing_0 = chat_v1_chat_room_service_pb2.CloneChatRoomRequest(
                chat_room=chat_v1_chat_pb2.ChatRoom(
                    address=common_v1_address_pb2.PostalAddress(region=request.filter.region)
                ),
                context=request.context
            )
            response_0 = await deps.clients.chat_chat_room.CloneChatRoom(outgoing_0, timeout=deps.settings.timeout)
            fields_1: dict[str, Any] = {
                'context': request.context,
                'filter': {'query': request.filter.query, 'region': response_0.chat_room.address.region},
                'page': {'page_size': request.page.page_size}
            }
            outgoing_1 = ledger_v1_ledger_account_service_pb2.SearchLedgerAccountsRequest(**fields_1)
            response_1 = await deps.clients.ledger_ledger_account.SearchLedgerAccounts(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.chat_room.owner.user_id
            returned_0_0_part_0 = response.pipeline_runs.add()
            if returned_0_0:
                returned_0_0_part_0.assignee.user_id = returned_0_0
            returned_0_1 = response_0.chat_room.audit.created_at
            returned_0_1_part_0 = response.pipeline_runs.add()
            returned_0_1_part_1 = returned_0_1_part_0.comments.add()
            if returned_0_1.ListFields():
                returned_0_1_part_1.created_at.MergeFrom(returned_0_1)
            returned_1_0 = response_1.page_info.next_page_token
            if returned_1_0:
                response.page_info.next_page_token = returned_1_0
            return response

    async def handle_push_pipeline_run(
        self,
        request: pipelines_v1_pipeline_run_sync_service_pb2.PushPipelineRunRequest
    ) -> pipelines_v1_pipeline_run_sync_service_pb2.PushPipelineRunResponse:
        """Pushs a pipeline run."""
        deps = self.deps
        response = pipelines_v1_pipeline_run_sync_service_pb2.PushPipelineRunResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('PushPipelineRun', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'PushPipelineRun', {'reason': request.reason})
            await deps.repository.save_pipeline_run(request.context.tenant_id, request.pipeline_run)
            response_0 = modelregistry_v1_registered_model_approval_service_pb2.RecallRegisteredModelResponse()
            response_1 = modelregistry_v1_deployment_sync_service_pb2.ListDeploymentConflictsResponse()
            response_2 = labeling_v1_label_set_approval_service_pb2.CommentLabelSetApprovalResponse()
            outgoing_0 = modelregistry_v1_registered_model_approval_service_pb2.RecallRegisteredModelRequest(
                context=request.context,
                registered_model=modelregistry_v1_modelregistry_pb2.RegisteredModel(
                    owner=identity_v1_refs_pb2.UserRef(email=request.pipeline_run.assignee.email)
                )
            )
            document_0 = MessageToDict(outgoing_0, preserving_proto_field_name=True)
            outgoing_0 = ParseDict(
                document_0,
                modelregistry_v1_registered_model_approval_service_pb2.RecallRegisteredModelRequest()
            )
            response_0 = await deps.clients.modelregistry_registered_model_approval.RecallRegisteredModel(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            for item_1 in request.pipeline_run.comments:
                outgoing_1 = modelregistry_v1_deployment_sync_service_pb2.ListDeploymentConflictsRequest(
                    context=request.context,
                    filter=modelregistry_v1_deployment_sync_service_pb2.ListDeploymentConflictsRequest.Filter(
                        created_after=item_1.created_at,
                        owner_id=item_1.comment_id,
                        region=response_0.registered_model.address.region
                    )
                )
                response_1 = await deps.clients.modelregistry_deployment_sync.ListDeploymentConflicts(
                    outgoing_1,
                    timeout=deps.settings.timeout
                )
            outgoing_2 = labeling_v1_label_set_approval_service_pb2.CommentLabelSetApprovalRequest()
            outgoing_2.context.CopyFrom(request.context)
            field_2_1_part_1 = outgoing_2.label_set.children.add()
            field_2_1_part_2 = field_2_1_part_1.children.add()
            field_2_1_part_2.audit.updated_at.CopyFrom(request.pipeline_run.audit.updated_at)
            field_2_2_part_1 = outgoing_2.label_set.children.add()
            field_2_2_part_2 = field_2_2_part_1.children.add()
            field_2_2_part_2.location.region = response_0.registered_model.address.region
            merged_2 = labeling_v1_label_set_approval_service_pb2.CommentLabelSetApprovalRequest()
            merged_2.MergeFrom(outgoing_2)
            outgoing_2.CopyFrom(merged_2)
            response_2 = await deps.clients.labeling_label_set_approval.CommentLabelSetApproval(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.registered_model.audit.created_at
            returned_0_0_part_1 = response.pipeline_run.comments.add()
            if returned_0_0.ListFields():
                returned_0_0_part_1.created_at.MergeFrom(returned_0_0)
            returned_0_1 = response_0.outcome.status
            if returned_0_1:
                response.outcome.status = returned_0_1
            returned_2_0 = response_2.result.status
            if returned_2_0:
                response.result.status = returned_2_0
            echoed_0 = request.pipeline_run_id
            response.pipeline_run.pipeline_run_id = echoed_0
            echoed_1 = request.pipeline_run.status
            response.pipeline_run.status = echoed_1
            return response

    async def handle_reconcile_pipeline_runs(
        self,
        request: pipelines_v1_pipeline_run_sync_service_pb2.ReconcilePipelineRunsRequest
    ) -> pipelines_v1_pipeline_run_sync_service_pb2.ReconcilePipelineRunsResponse:
        """Reconciles a pipeline run."""
        deps = self.deps
        response = pipelines_v1_pipeline_run_sync_service_pb2.ReconcilePipelineRunsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ReconcilePipelineRuns', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'ReconcilePipelineRuns', {'reason': request.reason})
            await deps.repository.save_pipeline_run(request.context.tenant_id, request.pipeline_run)
            response_0 = featurestore_v1_feature_view_approval_service_pb2.SubmitFeatureViewResponse()
            response_1 = ledger_v1_ledger_account_query_service_pb2.ExportLedgerAccountsResponse()
            requests_0: list[featurestore_v1_feature_view_approval_service_pb2.SubmitFeatureViewRequest] = []
            for item_0 in request.pipeline_run.comments:
                outgoing_0 = featurestore_v1_feature_view_approval_service_pb2.SubmitFeatureViewRequest(
                    context=request.context,
                    details=featurestore_v1_feature_view_approval_service_pb2.SubmitFeatureViewRequest.Details(
                        approver=identity_v1_refs_pb2.UserRef(email=item_0.author_email)
                    ),
                    feature_view=featurestore_v1_featurestore_pb2.FeatureView(
                        audit=common_v1_audit_pb2.AuditInfo(created_at=item_0.created_at)
                    )
                )
                requests_0.append(outgoing_0)
            replies_0 = await asyncio.gather(*(
                deps.clients.featurestore_feature_view_approval.SubmitFeatureView(
                    entry,
                    timeout=deps.settings.timeout
                ) for entry in requests_0
            ))
            if replies_0:
                response_0 = replies_0[-1]
            for item_1 in request.pipeline_run.history:
                outgoing_1 = ledger_v1_ledger_account_query_service_pb2.ExportLedgerAccountsRequest(
                    context=request.context,
                    filter=ledger_v1_ledger_account_query_service_pb2.ExportLedgerAccountsRequest.Filter(
                        created_after=item_1.changed_at,
                        labels=dict(request.pipeline_run.custom_fields),
                        owner_id=request.pipeline_run.assignee.user_id,
                        region=response_0.feature_view.address.region
                    )
                )
                async for result_1 in deps.clients.ledger_ledger_account_query.ExportLedgerAccounts(
                    outgoing_1,
                    timeout=deps.settings.timeout
                ):
                    response_1 = result_1
            echoed_0 = request.pipeline_run_id
            response.pipeline_run.pipeline_run_id = echoed_0
            echoed_1 = request.pipeline_run.priority
            response.pipeline_run.priority = echoed_1
            return response

    async def handle_resolve_pipeline_run_conflict(
        self,
        request: pipelines_v1_pipeline_run_sync_service_pb2.ResolvePipelineRunConflictRequest
    ) -> pipelines_v1_pipeline_run_sync_service_pb2.ResolvePipelineRunConflictResponse:
        """Resolves a pipeline run."""
        deps = self.deps
        response = pipelines_v1_pipeline_run_sync_service_pb2.ResolvePipelineRunConflictResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ResolvePipelineRunConflict', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ResolvePipelineRunConflict',
                {'reason': request.reason}
            )
            await deps.repository.save_pipeline_run(request.context.tenant_id, request.pipeline_run)
            response_0 = pipelines_v1_pipeline_step_import_service_pb2.MapPipelineStepImportColumnsResponse()
            response_1 = pipelines_v1_pipeline_service_pb2.ListPipelinesResponse()
            command_0 = PipelineRunSyncResolvePipelineRunConflict0Command(
                context=request.context,
                details_contact_phone=request.pipeline_run.requester.phone,
                pipeline_step_owner_display_name=request.pipeline_run.customer.display_name,
                details_contact_name=request.pipeline_run.requester.name
            )
            outgoing_0 = to_pipeline_run_sync_resolve_pipeline_run_conflict0_command(command_0)
            response_0 = await deps.clients.pipelines_pipeline_step_import.MapPipelineStepImportColumns(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            command_1 = PipelineRunSyncResolvePipelineRunConflict1Command.model_validate(
                {'context': request.context, 'filter_created_after': request.pipeline_run.audit.created_at}
            )
            outgoing_1 = to_pipeline_run_sync_resolve_pipeline_run_conflict1_command(command_1)
            response_1 = await deps.clients.pipelines_pipeline.ListPipelines(outgoing_1, timeout=deps.settings.timeout)
            returned_0_0 = response_0.pipeline_step.priority
            if returned_0_0:
                response.pipeline_run.priority = returned_0_0
            returned_0_1 = response_0.outcome.message
            if returned_0_1:
                response.result.message = returned_0_1
            returned_1_0 = response_1.result.correlation_id
            if returned_1_0:
                response.result.correlation_id = returned_1_0
            returned_1_1 = response_1.result.message
            if returned_1_1:
                response.result.message = returned_1_1
            echoed_0 = request.pipeline_run_id
            response.pipeline_run.pipeline_run_id = echoed_0
            echoed_1 = request.pipeline_run.subject
            response.pipeline_run.subject = echoed_1
            return response

    async def handle_stream_pipeline_run_changes(
        self,
        request: pipelines_v1_pipeline_run_sync_service_pb2.StreamPipelineRunChangesRequest
    ) -> pipelines_v1_pipeline_run_sync_service_pb2.StreamPipelineRunChangesResponse:
        """Exchanges changes of pipeline runs with a peer."""
        deps = self.deps
        response = pipelines_v1_pipeline_run_sync_service_pb2.StreamPipelineRunChangesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('StreamPipelineRunChanges', extra={'fields': {'cursor': request.cursor}})
            await deps.repository.audit(
                request.context.tenant_id,
                'StreamPipelineRunChanges',
                {'cursor': request.cursor}
            )
            if request.WhichOneof('frame') == 'change':
                await deps.repository.save_pipeline_run(request.context.tenant_id, request.change)
            response_0 = promotions_v1_promotion_query_service_pb2.CountPromotionsResponse()
            response_1 = featurestore_v1_feature_value_approval_service_pb2.RejectFeatureValueResponse()
            response_2 = featurestore_v1_feature_view_approval_service_pb2.DelegateFeatureViewApprovalResponse()
            outgoing_1 = featurestore_v1_feature_value_approval_service_pb2.RejectFeatureValueRequest(
                context=request.context,
                details=featurestore_v1_feature_value_approval_service_pb2.RejectFeatureValueRequest.Details(
                    approver=identity_v1_refs_pb2.UserRef(display_name=request.change.customer.display_name)
                )
            )
            outgoing_2 = featurestore_v1_feature_view_approval_service_pb2.DelegateFeatureViewApprovalRequest(
                context=request.context,
                details=featurestore_v1_feature_view_approval_service_pb2.DelegateFeatureViewApprovalRequest.Details(
                    approver=identity_v1_refs_pb2.UserRef(user_id=request.change.assignee.user_id)
                ),
                feature_view=featurestore_v1_featurestore_pb2.FeatureView(
                    owner=identity_v1_refs_pb2.UserRef(email=request.change.requester.email)
                )
            )
            response_1, response_2 = await asyncio.gather(
                deps.clients.featurestore_feature_value_approval.RejectFeatureValue(
                    outgoing_1,
                    timeout=deps.settings.timeout
                ),
                deps.clients.featurestore_feature_view_approval.DelegateFeatureViewApproval(
                    outgoing_2,
                    timeout=deps.settings.timeout
                ),
            )
            callbacks_0: list[
                Callable[[], Awaitable[promotions_v1_promotion_query_service_pb2.CountPromotionsResponse]]
            ] = []
            for item_0 in request.change.history:
                outgoing_0 = promotions_v1_promotion_query_service_pb2.CountPromotionsRequest(
                    context=request.context,
                    filter=promotions_v1_promotion_query_service_pb2.CountPromotionsRequest.Filter(
                        created_after=item_0.changed_at,
                        owner_id=request.change.customer.pipeline_id
                    )
                )
                async def send_0(
                    payload: promotions_v1_promotion_query_service_pb2.CountPromotionsRequest = outgoing_0
                ) -> promotions_v1_promotion_query_service_pb2.CountPromotionsResponse:
                    return await deps.clients.promotions_promotion_query.CountPromotions(
                        payload,
                        timeout=deps.settings.timeout
                    )
                callbacks_0.append(send_0)
            for callback_0 in callbacks_0:
                response_0 = await callback_0()
            returned_1_0 = response_1.feature_value.sequence
            if returned_1_0:
                response.sequence = returned_1_0
            returned_1_1 = response_1.feature_value.subject.display_name
            if returned_1_1:
                response.pipeline_run.assignee.display_name = returned_1_1
            returned_2_0 = response_2.feature_view.audit.created_at
            if returned_2_0.ListFields():
                response.pipeline_run.audit.created_at.MergeFrom(returned_2_0)
            echoed_0 = request.change.status
            response.pipeline_run.status = echoed_0
            echoed_1 = request.change.priority
            response.pipeline_run.priority = echoed_1
            return response

    async def handle_sync_pipeline_runs(
        self,
        request: pipelines_v1_pipeline_run_sync_service_pb2.SyncPipelineRunsRequest
    ) -> pipelines_v1_pipeline_run_sync_service_pb2.SyncPipelineRunsResponse:
        """Syncs a pipeline run."""
        deps = self.deps
        response = pipelines_v1_pipeline_run_sync_service_pb2.SyncPipelineRunsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SyncPipelineRuns', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'SyncPipelineRuns', {'reason': request.reason})
            await deps.repository.save_pipeline_run(request.context.tenant_id, request.pipeline_run)
            response_0 = modelregistry_v1_deployment_approval_service_pb2.CommentDeploymentApprovalResponse()
            response_1 = pipelines_v1_pipeline_step_import_service_pb2.RetryPipelineStepImportResponse()
            outgoing_0 = modelregistry_v1_deployment_approval_service_pb2.CommentDeploymentApprovalRequest(
                context=request.context,
                deployment=modelregistry_v1_modelregistry_pb2.Deployment(
                    organizer=identity_v1_refs_pb2.UserRef(email=request.pipeline_run.assignee.email),
                    participants=[
                        modelregistry_v1_modelregistry_pb2.DeploymentParticipant(
                            contact=common_v1_contact_pb2.ContactInfo(phone=request.pipeline_run.requester.phone)
                        )
                    ]
                )
            )
            port_0: PipelineRunSyncSyncPipelineRuns0Port = PipelineRunSyncSyncPipelineRuns0Adapter(
                deps.clients.modelregistry_deployment_approval,
                deps.settings.timeout
            )
            response_0 = await port_0.execute(outgoing_0)
            async for item_1 in async_messages(request.pipeline_run.comments):
                outgoing_1 = pipelines_v1_pipeline_step_import_service_pb2.RetryPipelineStepImportRequest(
                    context=request.context,
                    pipeline_step=pipelines_v1_pipelines_pb2.PipelineStep(
                        audit=common_v1_audit_pb2.AuditInfo(created_at=item_1.created_at)
                    )
                )
                response_1 = await deps.clients.pipelines_pipeline_step_import.RetryPipelineStepImport(
                    outgoing_1,
                    timeout=deps.settings.timeout
                )
            returned_0_0 = response_0.deployment.organizer.display_name
            if returned_0_0:
                response.pipeline_run.assignee.display_name = returned_0_0
            echoed_0 = request.pipeline_run_id
            response.pipeline_run.pipeline_run_id = echoed_0
            echoed_1 = request.pipeline_run.requester
            response.pipeline_run.requester.CopyFrom(echoed_1)
            return response
