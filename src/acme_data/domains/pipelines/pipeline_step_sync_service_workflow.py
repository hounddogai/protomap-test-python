"""Application workflow for PipelineStep Sync."""

from __future__ import annotations

from typing import Any
from typing import cast
import logging

from google.protobuf.any_pb2 import Any as AnyMessage
from google.protobuf.json_format import MessageToDict
from google.protobuf.json_format import ParseDict

from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.featurestore.v1 import feature_view_approval_service_pb2 as featurestore_v1_feature_view_approval_service_pb2
from acme.featurestore.v1 import featurestore_pb2 as featurestore_v1_featurestore_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.labeling.v1 import annotation_approval_service_pb2 as labeling_v1_annotation_approval_service_pb2
from acme.labeling.v1 import labeling_pb2 as labeling_v1_labeling_pb2
from acme.labeling.v1 import refs_pb2 as labeling_v1_refs_pb2
from acme.lineage.v1 import lineage_edge_sync_service_pb2 as lineage_v1_lineage_edge_sync_service_pb2
from acme.lineage.v1 import lineage_pb2 as lineage_v1_lineage_pb2
from acme.metrics.v1 import metric_alert_export_service_pb2 as metrics_v1_metric_alert_export_service_pb2
from acme.pipelines.v1 import pipeline_reporting_service_pb2 as pipelines_v1_pipeline_reporting_service_pb2
from acme.pipelines.v1 import pipeline_run_query_service_pb2 as pipelines_v1_pipeline_run_query_service_pb2
from acme.pipelines.v1 import pipeline_step_export_service_pb2 as pipelines_v1_pipeline_step_export_service_pb2
from acme.pipelines.v1 import pipeline_step_sync_service_pb2 as pipelines_v1_pipeline_step_sync_service_pb2

from acme_data.domains.pipelines.adapters import PipelineStepSyncPullPipelineSteps0Adapter
from acme_data.domains.pipelines.dependencies import Dependencies
from acme_data.platform.rpc import async_messages
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class PipelineStepSyncServicerWorkflow:
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    async def handle_get_pipeline_step_sync_state(
        self,
        request: pipelines_v1_pipeline_step_sync_service_pb2.GetPipelineStepSyncStateRequest
    ) -> pipelines_v1_pipeline_step_sync_service_pb2.GetPipelineStepSyncStateResponse:
        """Returns a pipeline step."""
        deps = self.deps
        response = pipelines_v1_pipeline_step_sync_service_pb2.GetPipelineStepSyncStateResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('GetPipelineStepSyncState', extra={'fields': {'domain': 'pipelines'}})
            await deps.repository.audit(request.context.tenant_id, 'GetPipelineStepSyncState', {})
            response_0 = lineage_v1_lineage_edge_sync_service_pb2.ReconcileLineageEdgesResponse()
            outgoing_0 = lineage_v1_lineage_edge_sync_service_pb2.ReconcileLineageEdgesRequest(
                context=request.context,
                lineage_edge=lineage_v1_lineage_pb2.LineageEdge(
                    measurements=[lineage_v1_lineage_pb2.LineageEdgeMeasurement(observed_at=request.context.deadline)]
                )
            )
            response_0 = await deps.clients.lineage_lineage_edge_sync.ReconcileLineageEdges(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.outcome.message
            if returned_0_0:
                response.result.message = returned_0_0
            returned_0_1 = response_0.outcome.status
            if returned_0_1:
                response.result.status = returned_0_1
            echoed_0 = request.pipeline_step_id
            response.pipeline_step.pipeline_step_id = echoed_0
            return response

    async def handle_pull_pipeline_steps(
        self,
        request: pipelines_v1_pipeline_step_sync_service_pb2.PullPipelineStepsRequest
    ) -> pipelines_v1_pipeline_step_sync_service_pb2.PullPipelineStepsResponse:
        """Pulls a pipeline step."""
        deps = self.deps
        response = pipelines_v1_pipeline_step_sync_service_pb2.PullPipelineStepsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('PullPipelineSteps', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'PullPipelineSteps', {'reason': request.reason})
            await deps.repository.save_pipeline_step(request.context.tenant_id, request.pipeline_step)
            response_0 = featurestore_v1_feature_view_approval_service_pb2.ApproveFeatureViewResponse()
            response_1 = pipelines_v1_pipeline_reporting_service_pb2.SchedulePipelineReportResponse()
            outgoing_0 = featurestore_v1_feature_view_approval_service_pb2.ApproveFeatureViewRequest(
                context=request.context,
                details=featurestore_v1_feature_view_approval_service_pb2.ApproveFeatureViewRequest.Details(
                    approver=identity_v1_refs_pb2.UserRef(display_name=request.pipeline_step.owner.display_name)
                ),
                feature_view=featurestore_v1_featurestore_pb2.FeatureView(
                    components={
                        'primary': featurestore_v1_featurestore_pb2.FeatureViewComponent(
                            description=request.pipeline_step.description
                        )
                    }
                )
            )
            response_0 = await PipelineStepSyncPullPipelineSteps0Adapter(
                deps.clients.featurestore_feature_view_approval,
                deps.settings.timeout
            )(outgoing_0)
            outgoing_1 = pipelines_v1_pipeline_reporting_service_pb2.SchedulePipelineReportRequest(
                context=request.context,
                reason=request.pipeline_step.block.reason
            )
            response_1 = cast(pipelines_v1_pipeline_reporting_service_pb2.SchedulePipelineReportResponse, await deps.bus.request(
                'acme.pipelines.v1.PipelineStepSyncService/PullPipelineSteps/1', outgoing_1, deps.settings.timeout,
            ))
            returned_0_0 = response_0.feature_view.owner.user_id
            if returned_0_0:
                response.pipeline_step.owner.user_id = returned_0_0
            returned_1_0 = response_1.result.correlation_id
            if returned_1_0:
                response.result.correlation_id = returned_1_0
            echoed_0 = request.pipeline_step_id
            response.pipeline_step.pipeline_step_id = echoed_0
            echoed_1 = request.pipeline_step.version
            response.pipeline_step.version = echoed_1
            return response

    async def handle_push_pipeline_step(
        self,
        request: pipelines_v1_pipeline_step_sync_service_pb2.PushPipelineStepRequest
    ) -> pipelines_v1_pipeline_step_sync_service_pb2.PushPipelineStepResponse:
        """Pushs a pipeline step."""
        deps = self.deps
        response = pipelines_v1_pipeline_step_sync_service_pb2.PushPipelineStepResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('PushPipelineStep', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'PushPipelineStep', {'reason': request.reason})
            await deps.repository.save_pipeline_step(request.context.tenant_id, request.pipeline_step)
            response_0 = pipelines_v1_pipeline_run_query_service_pb2.FindPipelineRunsResponse()
            response_1 = pipelines_v1_pipeline_step_export_service_pb2.SharePipelineStepExportResponse()
            outgoing_0 = pipelines_v1_pipeline_run_query_service_pb2.FindPipelineRunsRequest(
                context=request.context,
                filter=pipelines_v1_pipeline_run_query_service_pb2.FindPipelineRunsRequest.Filter(
                    created_after=request.pipeline_step.audit.created_at,
                    labels=dict(request.pipeline_step.parameters),
                    owner_id=request.pipeline_step.owner.user_id
                )
            )
            response_0 = await deps.clients.pipelines_pipeline_run_query.FindPipelineRuns(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = pipelines_v1_pipeline_step_export_service_pb2.SharePipelineStepExportRequest(
                context=request.context,
                details=pipelines_v1_pipeline_step_export_service_pb2.SharePipelineStepExportRequest.Details(
                    recipient=common_v1_contact_pb2.ContactInfo(email=request.pipeline_step.owner.email)
                )
            )
            method_name_1 = 'SharePipelineStepExport'
            response_1 = await getattr(
                deps.clients.pipelines_pipeline_step_export,
                method_name_1
            )(outgoing_1, timeout=deps.settings.timeout)
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.result.message = returned_0_0
            returned_0_1 = response_0.result.correlation_id
            if returned_0_1:
                response.result.correlation_id = returned_0_1
            returned_1_0 = response_1.pipeline_step.owner.user_id
            if returned_1_0:
                response.pipeline_step.owner.user_id = returned_1_0
            echoed_0 = request.pipeline_step_id
            response.pipeline_step.pipeline_step_id = echoed_0
            echoed_1 = request.pipeline_step.name
            response.pipeline_step.name = echoed_1
            return response

    async def handle_reconcile_pipeline_steps(
        self,
        request: pipelines_v1_pipeline_step_sync_service_pb2.ReconcilePipelineStepsRequest
    ) -> pipelines_v1_pipeline_step_sync_service_pb2.ReconcilePipelineStepsResponse:
        """Reconciles a pipeline step."""
        deps = self.deps
        response = pipelines_v1_pipeline_step_sync_service_pb2.ReconcilePipelineStepsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ReconcilePipelineSteps', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'ReconcilePipelineSteps', {'reason': request.reason})
            await deps.repository.save_pipeline_step(request.context.tenant_id, request.pipeline_step)
            response_0 = featurestore_v1_feature_view_approval_service_pb2.RecallFeatureViewResponse()
            fields_0: dict[str, Any] = {
                'context': request.context,
                'details': {'approver': {'user_id': request.pipeline_step.owner.user_id}},
                'feature_view': {
                    'audit': {'etag': request.pipeline_step.audit.etag},
                    'owner': {
                        'display_name': request.pipeline_step.owner.display_name,
                        'email': request.pipeline_step.owner.email
                    }
                }
            }
            outgoing_0 = featurestore_v1_feature_view_approval_service_pb2.RecallFeatureViewRequest(**fields_0)
            response_0 = await deps.clients.featurestore_feature_view_approval.RecallFeatureView(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.details
            response.result.details.update(returned_0_0)
            echoed_0 = request.pipeline_step_id
            response.pipeline_step.pipeline_step_id = echoed_0
            echoed_1 = request.pipeline_step.version
            response.pipeline_step.version = echoed_1
            return response

    async def handle_resolve_pipeline_step_conflict(
        self,
        request: pipelines_v1_pipeline_step_sync_service_pb2.ResolvePipelineStepConflictRequest
    ) -> pipelines_v1_pipeline_step_sync_service_pb2.ResolvePipelineStepConflictResponse:
        """Resolves a pipeline step."""
        deps = self.deps
        response = pipelines_v1_pipeline_step_sync_service_pb2.ResolvePipelineStepConflictResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ResolvePipelineStepConflict', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ResolvePipelineStepConflict',
                {'reason': request.reason}
            )
            await deps.repository.save_pipeline_step(request.context.tenant_id, request.pipeline_step)
            response_0 = pipelines_v1_pipeline_reporting_service_pb2.SharePipelineReportResponse()
            response_1 = pipelines_v1_pipeline_step_export_service_pb2.StreamPipelineStepExportResponse()
            response_2 = pipelines_v1_pipeline_run_query_service_pb2.FindPipelineRunsResponse()
            response_3 = labeling_v1_annotation_approval_service_pb2.EscalateAnnotationResponse()
            outgoing_0 = pipelines_v1_pipeline_reporting_service_pb2.SharePipelineReportRequest(
                context=request.context,
                details=pipelines_v1_pipeline_reporting_service_pb2.SharePipelineReportRequest.Details(
                    recipient=common_v1_contact_pb2.ContactInfo(email=request.pipeline_step.block.notify_email)
                ),
                reason=request.pipeline_step.block.reason
            )
            document_0 = MessageToDict(outgoing_0, preserving_proto_field_name=True)
            outgoing_0 = ParseDict(document_0, pipelines_v1_pipeline_reporting_service_pb2.SharePipelineReportRequest())
            response_0 = await deps.clients.pipelines_pipeline_reporting.SharePipelineReport(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = pipelines_v1_pipeline_step_export_service_pb2.StreamPipelineStepExportRequest(
                context=request.context,
                filter=pipelines_v1_pipeline_step_export_service_pb2.StreamPipelineStepExportRequest.Filter(
                    created_after=request.pipeline_step.audit.created_at,
                    labels=dict(response_0.result.details),
                    owner_id=response_0.pipeline.organizer.user_id,
                    region=response_0.pipeline.location.region
                )
            )
            async for chunk_1 in deps.clients.pipelines_pipeline_step_export.StreamPipelineStepExport(
                outgoing_1,
                timeout=deps.settings.timeout
            ):
                response_1 = chunk_1
            outgoing_2 = pipelines_v1_pipeline_run_query_service_pb2.FindPipelineRunsRequest()
            outgoing_2.context.CopyFrom(request.context)
            outgoing_2.filter.region = response_0.pipeline.location.region
            outgoing_2.filter.created_after.CopyFrom(request.pipeline_step.audit.created_at)
            merged_2 = pipelines_v1_pipeline_run_query_service_pb2.FindPipelineRunsRequest()
            merged_2.MergeFrom(outgoing_2)
            outgoing_2.CopyFrom(merged_2)
            response_2 = await deps.clients.pipelines_pipeline_run_query.FindPipelineRuns(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            outgoing_3 = labeling_v1_annotation_approval_service_pb2.EscalateAnnotationRequest(
                annotation=labeling_v1_labeling_pb2.Annotation(
                    correlation_id=response_2.result.correlation_id,
                    subject=labeling_v1_refs_pb2.LabelingTaskRef(
                        display_name=response_0.pipeline.organizer.display_name
                    )
                ),
                context=request.context,
                details=labeling_v1_annotation_approval_service_pb2.EscalateAnnotationRequest.Details(
                    approver=identity_v1_refs_pb2.UserRef(user_id=response_0.pipeline.organizer.user_id)
                )
            )
            envelope_3 = AnyMessage()
            envelope_3.Pack(outgoing_3)
            outgoing_3 = labeling_v1_annotation_approval_service_pb2.EscalateAnnotationRequest()
            if not envelope_3.Unpack(outgoing_3):
                raise ValueError("partner envelope contains the wrong request type")
            response_3 = await deps.clients.labeling_annotation_approval.EscalateAnnotation(
                outgoing_3,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.pipeline.organizer.display_name
            if returned_0_0:
                response.pipeline_step.owner.display_name = returned_0_0
            returned_2_0 = response_2.result.details
            response.result.details.update(returned_2_0)
            returned_2_1 = response_2.result.message
            if returned_2_1:
                response.outcome.message = returned_2_1
            returned_3_0 = response_3.outcome.effective_at
            if returned_3_0.ListFields():
                response.outcome.effective_at.MergeFrom(returned_3_0)
            returned_3_1 = response_3.outcome.message
            if returned_3_1:
                response.outcome.message = returned_3_1
            echoed_0 = request.pipeline_step_id
            response.pipeline_step.pipeline_step_id = echoed_0
            echoed_1 = request.pipeline_step.status
            response.pipeline_step.status = echoed_1
            return response

    async def handle_stream_pipeline_step_changes(
        self,
        request: pipelines_v1_pipeline_step_sync_service_pb2.StreamPipelineStepChangesRequest
    ) -> pipelines_v1_pipeline_step_sync_service_pb2.StreamPipelineStepChangesResponse:
        """Exchanges changes of pipeline steps with a peer."""
        deps = self.deps
        response = pipelines_v1_pipeline_step_sync_service_pb2.StreamPipelineStepChangesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('StreamPipelineStepChanges', extra={'fields': {'cursor': request.cursor}})
            await deps.repository.audit(
                request.context.tenant_id,
                'StreamPipelineStepChanges',
                {'cursor': request.cursor}
            )
            if request.WhichOneof('frame') == 'change':
                await deps.repository.save_pipeline_step(request.context.tenant_id, request.change)
            response_0 = pipelines_v1_pipeline_run_query_service_pb2.BrowsePipelineRunsResponse()
            outgoing_0 = pipelines_v1_pipeline_run_query_service_pb2.BrowsePipelineRunsRequest()
            outgoing_0.context.CopyFrom(request.context)
            if request.WhichOneof('frame') == 'change':
                outgoing_0.filter.created_after.CopyFrom(request.change.audit.created_at)
            if request.WhichOneof('frame') == 'change':
                outgoing_0.filter.owner_id = request.change.pipeline_step_id
            if request.WhichOneof('frame') == 'change':
                outgoing_0.filter.labels.update(dict(request.change.parameters))
            response_0 = await deps.clients.pipelines_pipeline_run_query.BrowsePipelineRuns(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.result.message = returned_0_0
            returned_0_1 = response_0.result.status
            if returned_0_1:
                response.result.status = returned_0_1
            echoed_0 = request.ack.sequence
            response.sequence = echoed_0
            echoed_1 = request.change.owner
            response.pipeline_step.owner.CopyFrom(echoed_1)
            return response

    async def handle_sync_pipeline_steps(
        self,
        request: pipelines_v1_pipeline_step_sync_service_pb2.SyncPipelineStepsRequest
    ) -> pipelines_v1_pipeline_step_sync_service_pb2.SyncPipelineStepsResponse:
        """Syncs a pipeline step."""
        deps = self.deps
        response = pipelines_v1_pipeline_step_sync_service_pb2.SyncPipelineStepsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SyncPipelineSteps', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'SyncPipelineSteps', {'reason': request.reason})
            await deps.repository.save_pipeline_step(request.context.tenant_id, request.pipeline_step)
            response_0 = metrics_v1_metric_alert_export_service_pb2.StreamMetricAlertExportResponse()
            outgoing_0 = metrics_v1_metric_alert_export_service_pb2.StreamMetricAlertExportRequest(
                context=request.context,
                filter=metrics_v1_metric_alert_export_service_pb2.StreamMetricAlertExportRequest.Filter(
                    created_after=request.pipeline_step.audit.updated_at,
                    labels=dict(request.pipeline_step.parameters),
                    owner_id=request.pipeline_step.owner.user_id
                )
            )
            async for chunk_0 in deps.clients.metrics_metric_alert_export.StreamMetricAlertExport(
                outgoing_0,
                timeout=deps.settings.timeout
            ):
                response_0 = chunk_0
            echoed_0 = request.pipeline_step_id
            response.pipeline_step.pipeline_step_id = echoed_0
            echoed_1 = request.pipeline_step.name
            response.pipeline_step.name = echoed_1
            return response
