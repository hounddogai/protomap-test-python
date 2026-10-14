"""Moves a feature view between the states of its lifecycle."""

from __future__ import annotations

from collections.abc import AsyncIterator
from dataclasses import dataclass
from functools import partial
from typing import cast
import asyncio
import logging

from google.protobuf.any_pb2 import Any as AnyMessage
import grpc

from acme.anomalies.v1 import (
    anomaly_feedback_approval_service_pb2 as anomalies_v1_anomaly_feedback_approval_service_pb2,
)
from acme.campaigns.v1 import marketing_campaign_query_service_pb2 as campaigns_v1_marketing_campaign_query_service_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.datasets.v1 import data_schema_validation_service_pb2 as datasets_v1_data_schema_validation_service_pb2
from acme.datasets.v1 import datasets_pb2 as datasets_v1_datasets_pb2
from acme.documents.v1 import document_query_service_pb2 as documents_v1_document_query_service_pb2
from acme.featurestore.v1 import entity_sync_service_pb2 as featurestore_v1_entity_sync_service_pb2
from acme.featurestore.v1 import feature_value_import_service_pb2 as featurestore_v1_feature_value_import_service_pb2
from acme.featurestore.v1 import (
    feature_view_lifecycle_service_pb2 as featurestore_v1_feature_view_lifecycle_service_pb2,
)
from acme.featurestore.v1 import (
    feature_view_lifecycle_service_pb2_grpc as featurestore_v1_feature_view_lifecycle_service_pb2_grpc,
)
from acme.featurestore.v1 import feature_view_service_pb2 as featurestore_v1_feature_view_service_pb2
from acme.featurestore.v1 import feature_view_sync_service_pb2 as featurestore_v1_feature_view_sync_service_pb2
from acme.featurestore.v1 import featurestore_pb2 as featurestore_v1_featurestore_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.lineage.v1 import lineage_edge_reporting_service_pb2 as lineage_v1_lineage_edge_reporting_service_pb2
from acme.metrics.v1 import metric_series_export_service_pb2 as metrics_v1_metric_series_export_service_pb2
from acme.metrics.v1 import metric_series_export_service_pb2_grpc as metrics_v1_metric_series_export_service_pb2_grpc
from acme.notifications.v1 import notification_query_service_pb2 as notifications_v1_notification_query_service_pb2
from acme.search.v1 import search_index_service_pb2 as search_v1_search_index_service_pb2

from acme_data.domains.featurestore import hooks
from acme_data.domains.featurestore.adapters import FeatureViewLifecycleActivateFeatureView0Adapter
from acme_data.domains.featurestore.adapters import FeatureViewLifecycleActivateFeatureView0Port
from acme_data.domains.featurestore.adapters import FeatureViewLifecycleExpireFeatureView0Adapter
from acme_data.domains.featurestore.adapters import FeatureViewLifecycleTerminateFeatureView1Adapter
from acme_data.domains.featurestore.adapters import FeatureViewLifecycleTerminateFeatureView1Port
from acme_data.domains.featurestore.dependencies import Dependencies
from acme_data.domains.featurestore.models import FeatureViewLifecycleScheduleFeatureViewExpiry2Command
from acme_data.domains.featurestore.models import to_feature_view_lifecycle_schedule_feature_view_expiry2_command
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import run_steps
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_id
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


@dataclass(slots=True)
class FeatureViewLifecycleServicer(
    featurestore_v1_feature_view_lifecycle_service_pb2_grpc.FeatureViewLifecycleServiceServicer
):
    deps: Dependencies

    @rpc_errors
    async def ActivateFeatureView(
        self, request: featurestore_v1_feature_view_lifecycle_service_pb2.ActivateFeatureViewRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_feature_view_lifecycle_service_pb2.ActivateFeatureViewResponse:
        """Activates a feature view."""
        return await self.handle_activate_feature_view(request)

    @rpc_errors
    async def ExpireFeatureView(
        self, request: featurestore_v1_feature_view_lifecycle_service_pb2.ExpireFeatureViewRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_feature_view_lifecycle_service_pb2.ExpireFeatureViewResponse:
        """Expires a feature view."""
        return await self.handle_expire_feature_view(request)

    @rpc_errors
    @retry_transient
    async def GetFeatureViewLifecycle(
        self, request: featurestore_v1_feature_view_lifecycle_service_pb2.GetFeatureViewLifecycleRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_feature_view_lifecycle_service_pb2.GetFeatureViewLifecycleResponse:
        """Returns a feature view."""
        return await self.handle_get_feature_view_lifecycle(request)

    @rpc_errors
    async def ReinstateFeatureView(
        self, request: featurestore_v1_feature_view_lifecycle_service_pb2.ReinstateFeatureViewRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_feature_view_lifecycle_service_pb2.ReinstateFeatureViewResponse:
        """Reinstates a feature view."""
        return await self.handle_reinstate_feature_view(request)

    @rpc_errors
    async def RenewFeatureView(
        self, request: featurestore_v1_feature_view_lifecycle_service_pb2.RenewFeatureViewRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_feature_view_lifecycle_service_pb2.RenewFeatureViewResponse:
        """Renews a feature view."""
        return await self.handle_renew_feature_view(request)

    @rpc_errors
    async def ScheduleFeatureViewExpiry(
        self, request: featurestore_v1_feature_view_lifecycle_service_pb2.ScheduleFeatureViewExpiryRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_feature_view_lifecycle_service_pb2.ScheduleFeatureViewExpiryResponse:
        """Schedules a feature view."""
        return await self.handle_schedule_feature_view_expiry(request)

    @rpc_errors
    async def SuspendFeatureView(
        self, request: featurestore_v1_feature_view_lifecycle_service_pb2.SuspendFeatureViewRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_feature_view_lifecycle_service_pb2.SuspendFeatureViewResponse:
        """Suspends a feature view."""
        return await self.handle_suspend_feature_view(request)

    @rpc_errors
    async def TerminateFeatureView(
        self, request: featurestore_v1_feature_view_lifecycle_service_pb2.TerminateFeatureViewRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_feature_view_lifecycle_service_pb2.TerminateFeatureViewResponse:
        """Terminates a feature view."""
        return await self.handle_terminate_feature_view(request)

    async def handle_activate_feature_view(
        self,
        request: featurestore_v1_feature_view_lifecycle_service_pb2.ActivateFeatureViewRequest
    ) -> featurestore_v1_feature_view_lifecycle_service_pb2.ActivateFeatureViewResponse:
        """Activates a feature view."""
        deps = self.deps
        response = featurestore_v1_feature_view_lifecycle_service_pb2.ActivateFeatureViewResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ActivateFeatureView', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'ActivateFeatureView', {'reason': request.reason})
            response_0 = featurestore_v1_feature_view_service_pb2.GetFeatureViewResponse()
            response_1 = featurestore_v1_feature_view_sync_service_pb2.PushFeatureViewResponse()
            outgoing_0 = featurestore_v1_feature_view_service_pb2.GetFeatureViewRequest(
                context=request.context,
                feature_view_id=request.feature_view_id
            )
            port_0: FeatureViewLifecycleActivateFeatureView0Port = FeatureViewLifecycleActivateFeatureView0Adapter(
                deps.clients.featurestore_feature_view,
                deps.settings.timeout
            )
            response_0 = await port_0.execute(outgoing_0)
            outgoing_1 = featurestore_v1_feature_view_sync_service_pb2.PushFeatureViewRequest(
                context=request.context,
                feature_view=featurestore_v1_featurestore_pb2.FeatureView(
                    dimensions=featurestore_v1_featurestore_pb2.FeatureViewDimensions(
                        height=response_0.feature_view.dimensions.height
                    )
                )
            )
            steps_1 = [
                partial(
                    deps.clients.featurestore_feature_view_sync.PushFeatureView,
                    outgoing_1,
                    timeout=deps.settings.timeout
                )
            ]
            results_1 = await run_steps(steps_1)
            response_1 = results_1[-1]
            returned_0_0 = response_0.feature_view.name
            if returned_0_0:
                response.feature_view.name = returned_0_0
            returned_1_0 = response_1.feature_view.audit.updated_at
            if returned_1_0.ListFields():
                response.feature_view.audit.updated_at.MergeFrom(returned_1_0)
            echoed_0 = request.feature_view_id
            response.feature_view.feature_view_id = echoed_0
            echoed_1 = request.details.effective_at
            response.outcome.effective_at.CopyFrom(echoed_1)
            return response

    async def handle_expire_feature_view(
        self,
        request: featurestore_v1_feature_view_lifecycle_service_pb2.ExpireFeatureViewRequest
    ) -> featurestore_v1_feature_view_lifecycle_service_pb2.ExpireFeatureViewResponse:
        """Expires a feature view."""
        deps = self.deps
        response = featurestore_v1_feature_view_lifecycle_service_pb2.ExpireFeatureViewResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ExpireFeatureView', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'ExpireFeatureView', {'reason': request.reason})
            response_0 = featurestore_v1_feature_view_service_pb2.BatchGetFeatureViewsResponse()
            response_1 = featurestore_v1_feature_view_sync_service_pb2.GetFeatureViewSyncStateResponse()
            response_2 = documents_v1_document_query_service_pb2.ExportDocumentsResponse()
            response_3 = anomalies_v1_anomaly_feedback_approval_service_pb2.RecallAnomalyFeedbackResponse()
            outgoing_0 = featurestore_v1_feature_view_service_pb2.BatchGetFeatureViewsRequest(context=request.context)
            response_0 = await FeatureViewLifecycleExpireFeatureView0Adapter(
                deps.clients.featurestore_feature_view,
                deps.settings.timeout
            )(outgoing_0)
            outgoing_1 = featurestore_v1_feature_view_sync_service_pb2.GetFeatureViewSyncStateRequest(
                context=request.context,
                feature_view_id=request.feature_view_id
            )
            response_1 = cast(featurestore_v1_feature_view_sync_service_pb2.GetFeatureViewSyncStateResponse, await deps.bus.request(
                'acme.featurestore.v1.FeatureViewLifecycleService/ExpireFeatureView/1', outgoing_1, deps.settings.timeout,
            ))
            outgoing_2 = documents_v1_document_query_service_pb2.ExportDocumentsRequest(
                context=request.context,
                filter=documents_v1_document_query_service_pb2.ExportDocumentsRequest.Filter(
                    created_after=response_1.feature_view.audit.created_at,
                    labels=dict(response_1.result.details),
                    owner_id=response_1.result.correlation_id,
                    region=response_1.feature_view.address.region
                )
            )
            async for chunk_2 in deps.clients.documents_document_query.ExportDocuments(
                outgoing_2,
                timeout=deps.settings.timeout
            ):
                response_2 = chunk_2
            outgoing_3 = anomalies_v1_anomaly_feedback_approval_service_pb2.RecallAnomalyFeedbackRequest(
                context=request.context,
                details=anomalies_v1_anomaly_feedback_approval_service_pb2.RecallAnomalyFeedbackRequest.Details(
                    approver=identity_v1_refs_pb2.UserRef(user_id=request.details.new_owner.user_id)
                )
            )
            method_name_3 = 'RecallAnomalyFeedback'
            response_3 = await getattr(
                deps.clients.anomalies_anomaly_feedback_approval,
                method_name_3
            )(outgoing_3, timeout=deps.settings.timeout)
            returned_0_0 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_0)
            returned_0_1 = response_0.result.status
            if returned_0_1:
                response.result.status = returned_0_1
            returned_1_0 = response_1.feature_view.dimensions.weight
            if returned_1_0:
                response.feature_view.dimensions.weight = returned_1_0
            returned_1_1 = response_1.feature_view.dimensions.unit
            if returned_1_1:
                response.feature_view.dimensions.unit = returned_1_1
            returned_3_0 = response_3.result.reference_ids
            response.result.reference_ids.extend(returned_3_0)
            returned_3_1 = response_3.result.correlation_id
            if returned_3_1:
                response.result.correlation_id = returned_3_1
            echoed_0 = request.feature_view_id
            response.feature_view.feature_view_id = echoed_0
            echoed_1 = request.details.effective_at
            response.outcome.effective_at.CopyFrom(echoed_1)
            return response

    async def handle_get_feature_view_lifecycle(
        self,
        request: featurestore_v1_feature_view_lifecycle_service_pb2.GetFeatureViewLifecycleRequest
    ) -> featurestore_v1_feature_view_lifecycle_service_pb2.GetFeatureViewLifecycleResponse:
        """Returns a feature view."""
        deps = self.deps
        response = featurestore_v1_feature_view_lifecycle_service_pb2.GetFeatureViewLifecycleResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('GetFeatureViewLifecycle', extra={'fields': {'domain': 'featurestore'}})
            await deps.repository.audit(request.context.tenant_id, 'GetFeatureViewLifecycle', {})
            response_0 = search_v1_search_index_service_pb2.SearchSearchIndexesResponse()
            outgoing_0 = search_v1_search_index_service_pb2.SearchSearchIndexesRequest(
                context=request.context,
                filter=search_v1_search_index_service_pb2.SearchSearchIndexesRequest.Filter(
                    created_after=request.context.deadline,
                    labels=dict(request.context.baggage),
                    owner_id=request.feature_view_id
                )
            )
            response_0 = await deps.clients.search_search_index.SearchSearchIndexes(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_0)
            returned_0_1 = response_0.result.details
            response.result.details.update(returned_0_1)
            echoed_0 = request.feature_view_id
            response.feature_view.feature_view_id = echoed_0
            return response

    async def handle_reinstate_feature_view(
        self,
        request: featurestore_v1_feature_view_lifecycle_service_pb2.ReinstateFeatureViewRequest
    ) -> featurestore_v1_feature_view_lifecycle_service_pb2.ReinstateFeatureViewResponse:
        """Reinstates a feature view."""
        deps = self.deps
        response = featurestore_v1_feature_view_lifecycle_service_pb2.ReinstateFeatureViewResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ReinstateFeatureView', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'ReinstateFeatureView', {'reason': request.reason})
            response_0 = anomalies_v1_anomaly_feedback_approval_service_pb2.SubmitAnomalyFeedbackResponse()
            response_1 = anomalies_v1_anomaly_feedback_approval_service_pb2.CommentAnomalyFeedbackApprovalResponse()
            outgoing_0 = anomalies_v1_anomaly_feedback_approval_service_pb2.SubmitAnomalyFeedbackRequest(
                context=request.context,
                details=anomalies_v1_anomaly_feedback_approval_service_pb2.SubmitAnomalyFeedbackRequest.Details(
                    approver=identity_v1_refs_pb2.UserRef(
                        display_name=request.details.new_owner.display_name,
                        email=request.details.notify_contact.email
                    )
                )
            )
            outgoing_1 = anomalies_v1_anomaly_feedback_approval_service_pb2.CommentAnomalyFeedbackApprovalRequest(
                context=request.context,
                details=anomalies_v1_anomaly_feedback_approval_service_pb2.CommentAnomalyFeedbackApprovalRequest.Details(
                    approver=identity_v1_refs_pb2.UserRef(display_name=request.details.new_owner.display_name)
                )
            )
            response_0, response_1 = await asyncio.gather(
                deps.clients.anomalies_anomaly_feedback_approval.SubmitAnomalyFeedback(
                    outgoing_0,
                    timeout=deps.settings.timeout
                ),
                deps.clients.anomalies_anomaly_feedback_approval.CommentAnomalyFeedbackApproval(
                    outgoing_1,
                    timeout=deps.settings.timeout
                ),
            )
            returned_0_0 = response_0.result.details
            response.result.details.update(returned_0_0)
            returned_0_1 = response_0.outcome.effective_at
            if returned_0_1.ListFields():
                response.outcome.effective_at.MergeFrom(returned_0_1)
            returned_1_0 = response_1.outcome.status
            if returned_1_0:
                response.result.status = returned_1_0
            echoed_0 = request.feature_view_id
            response.feature_view.feature_view_id = echoed_0
            echoed_1 = request.details.new_owner.email
            response.feature_view.owner.email = echoed_1
            return response

    async def handle_renew_feature_view(
        self,
        request: featurestore_v1_feature_view_lifecycle_service_pb2.RenewFeatureViewRequest
    ) -> featurestore_v1_feature_view_lifecycle_service_pb2.RenewFeatureViewResponse:
        """Renews a feature view."""
        deps = self.deps
        response = featurestore_v1_feature_view_lifecycle_service_pb2.RenewFeatureViewResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('RenewFeatureView', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'RenewFeatureView', {'reason': request.reason})
            response_0 = featurestore_v1_feature_value_import_service_pb2.ValidateFeatureValueImportResponse()
            response_1 = featurestore_v1_entity_sync_service_pb2.ReconcileEntitiesResponse()
            outgoing_0 = featurestore_v1_feature_value_import_service_pb2.ValidateFeatureValueImportRequest()
            outgoing_0.context.CopyFrom(request.context)
            outgoing_0.details.contact.name.CopyFrom(request.details.notify_contact.name)
            outgoing_0.details.contact.preferred_channel = request.details.notify_contact.preferred_channel
            merged_0 = featurestore_v1_feature_value_import_service_pb2.ValidateFeatureValueImportRequest()
            merged_0.MergeFrom(outgoing_0)
            outgoing_0.CopyFrom(merged_0)
            response_0 = await deps.clients.featurestore_feature_value_import.ValidateFeatureValueImport(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = featurestore_v1_entity_sync_service_pb2.ReconcileEntitiesRequest(
                context=request.context,
                entity=featurestore_v1_featurestore_pb2.Entity(
                    contact=common_v1_contact_pb2.ContactInfo(
                        email=request.details.notify_contact.email,
                        preferred_channel=request.details.notify_contact.preferred_channel
                    ),
                    name=request.details.notify_contact.name,
                    relationship_manager=identity_v1_refs_pb2.UserRef(
                        display_name=request.details.new_owner.display_name
                    )
                )
            )
            envelope_1 = AnyMessage()
            envelope_1.Pack(outgoing_1)
            outgoing_1 = featurestore_v1_entity_sync_service_pb2.ReconcileEntitiesRequest()
            if not envelope_1.Unpack(outgoing_1):
                raise ValueError("partner envelope contains the wrong request type")
            response_1 = await deps.clients.featurestore_entity_sync.ReconcileEntities(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.details
            response.result.details.update(returned_0_0)
            returned_0_1 = response_0.result.status
            if returned_0_1:
                response.outcome.status = returned_0_1
            returned_1_0 = response_1.result.details
            response.result.details.update(returned_1_0)
            returned_1_1 = response_1.result.status
            if returned_1_1:
                response.outcome.status = returned_1_1
            echoed_0 = request.feature_view_id
            response.feature_view.feature_view_id = echoed_0
            echoed_1 = request.details.effective_at
            response.outcome.effective_at.CopyFrom(echoed_1)
            return response

    async def handle_schedule_feature_view_expiry(
        self,
        request: featurestore_v1_feature_view_lifecycle_service_pb2.ScheduleFeatureViewExpiryRequest
    ) -> featurestore_v1_feature_view_lifecycle_service_pb2.ScheduleFeatureViewExpiryResponse:
        """Schedules a feature view."""
        deps = self.deps
        response = featurestore_v1_feature_view_lifecycle_service_pb2.ScheduleFeatureViewExpiryResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ScheduleFeatureViewExpiry', extra={'fields': {'initiated_by': request.details.initiated_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ScheduleFeatureViewExpiry',
                {'initiated_by': request.details.initiated_by}
            )
            await deps.repository.save_feature_view(request.context.tenant_id, request.feature_view)
            response_0 = metrics_v1_metric_series_export_service_pb2.ShareMetricSeriesExportResponse()
            response_1 = campaigns_v1_marketing_campaign_query_service_pb2.SuggestMarketingCampaignsResponse()
            response_2 = notifications_v1_notification_query_service_pb2.SummarizeNotificationsResponse()
            response_3 = featurestore_v1_feature_view_service_pb2.SearchFeatureViewsResponse()
            outgoing_0 = metrics_v1_metric_series_export_service_pb2.ShareMetricSeriesExportRequest(
                annotations=dict(request.annotations),
                context=request.context,
                details=metrics_v1_metric_series_export_service_pb2.ShareMetricSeriesExportRequest.Details(
                    recipient=common_v1_contact_pb2.ContactInfo(
                        email=request.feature_view.owner.email,
                        name=request.details.notify.name,
                        preferred_channel=request.details.notify.preferred_channel
                    )
                )
            )
            registered_0 = cast(
                metrics_v1_metric_series_export_service_pb2_grpc.MetricSeriesExportServiceStub,
                deps.clients.registry['acme.metrics.v1.MetricSeriesExportService']
            )
            response_0 = await registered_0.ShareMetricSeriesExport(outgoing_0, timeout=deps.settings.timeout)
            outgoing_1 = campaigns_v1_marketing_campaign_query_service_pb2.SuggestMarketingCampaignsRequest()
            outgoing_1.context.CopyFrom(request.context)
            if response_0.metric_series.WhichOneof('locator') == 'address':
                outgoing_1.filter.region = response_0.metric_series.address.region
            outgoing_1.filter.created_after.CopyFrom(response_0.metric_series.audit.updated_at)
            outgoing_1.filter.owner_id = request.feature_view.components.get(
                'primary',
                featurestore_v1_featurestore_pb2.FeatureViewComponent()
            ).component_id
            response_1 = await deps.clients.campaigns_marketing_campaign_query.SuggestMarketingCampaigns(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            command_2 = FeatureViewLifecycleScheduleFeatureViewExpiry2Command.model_validate(
                {
                    'context': request.context,
                    'annotations': dict(request.annotations),
                    'reason': request.reason,
                    'details_filters': dict(request.details.parameters)
                }
            )
            outgoing_2 = to_feature_view_lifecycle_schedule_feature_view_expiry2_command(command_2)
            response_2 = await deps.clients.notifications_notification_query.SummarizeNotifications(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            outgoing_3 = featurestore_v1_feature_view_service_pb2.SearchFeatureViewsRequest(
                context=request.context,
                filter=featurestore_v1_feature_view_service_pb2.SearchFeatureViewsRequest.Filter(
                    created_after=request.feature_view.audit.updated_at,
                    owner_id=response_0.metric_series.owner.user_id,
                    region=request.feature_view.address.region
                )
            )
            send_3 = partial(deps.clients.featurestore_feature_view.SearchFeatureViews, timeout=deps.settings.timeout)
            response_3 = await send_3(outgoing_3)
            returned_0_0 = response_0.metric_series.audit.created_at
            if returned_0_0.ListFields():
                response.feature_view.audit.created_at.MergeFrom(returned_0_0)
            returned_0_1 = response_0.metric_series.code
            if returned_0_1:
                response.feature_view.code = returned_0_1
            returned_1_0 = response_1.result.message
            if returned_1_0:
                response.outcome.message = returned_1_0
            returned_1_1 = response_1.result.message
            if returned_1_1:
                response.result.message = returned_1_1
            returned_2_0 = response_2.result.correlation_id
            if returned_2_0:
                response.result.correlation_id = returned_2_0
            returned_2_1 = response_2.result.reference_ids
            response.result.reference_ids.extend(returned_2_1)
            returned_3_0 = response_3.result.reference_ids
            response.result.reference_ids.extend(returned_3_0)
            echoed_0 = request.feature_view_id
            response.feature_view.feature_view_id = echoed_0
            echoed_1 = request.feature_view.status
            response.feature_view.status = echoed_1
            return response

    async def handle_suspend_feature_view(
        self,
        request: featurestore_v1_feature_view_lifecycle_service_pb2.SuspendFeatureViewRequest
    ) -> featurestore_v1_feature_view_lifecycle_service_pb2.SuspendFeatureViewResponse:
        """Suspends a feature view."""
        deps = self.deps
        response = featurestore_v1_feature_view_lifecycle_service_pb2.SuspendFeatureViewResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SuspendFeatureView', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'SuspendFeatureView', {'reason': request.reason})
            response_0 = featurestore_v1_feature_value_import_service_pb2.ValidateFeatureValueImportResponse()
            outgoing_0 = featurestore_v1_feature_value_import_service_pb2.ValidateFeatureValueImportRequest(
                context=request.context,
                details=featurestore_v1_feature_value_import_service_pb2.ValidateFeatureValueImportRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(
                        email=request.details.new_owner.email,
                        name=request.details.notify_contact.name,
                        phone=request.details.notify_contact.phone
                    )
                )
            )
            response_0 = await hooks.feature_view_lifecycle_suspend_feature_view0(
                deps.clients.featurestore_feature_value_import,
                outgoing_0,
                deps.settings.timeout
            )
            returned_0_0 = response_0.result.correlation_id
            if returned_0_0:
                response.result.correlation_id = returned_0_0
            echoed_0 = request.feature_view_id
            response.feature_view.feature_view_id = echoed_0
            echoed_1 = request.details.effective_at
            response.outcome.effective_at.CopyFrom(echoed_1)
            return response

    async def handle_terminate_feature_view(
        self,
        request: featurestore_v1_feature_view_lifecycle_service_pb2.TerminateFeatureViewRequest
    ) -> featurestore_v1_feature_view_lifecycle_service_pb2.TerminateFeatureViewResponse:
        """Terminates a feature view."""
        deps = self.deps
        response = featurestore_v1_feature_view_lifecycle_service_pb2.TerminateFeatureViewResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('TerminateFeatureView', extra={'fields': {'reason_code': request.details.reason_code}})
            await deps.repository.audit(
                request.context.tenant_id,
                'TerminateFeatureView',
                {'reason_code': request.details.reason_code}
            )
            response_0 = lineage_v1_lineage_edge_reporting_service_pb2.ScheduleLineageEdgeReportResponse()
            response_1 = datasets_v1_data_schema_validation_service_pb2.CheckDataSchemaEligibilityResponse()
            outgoing_0 = lineage_v1_lineage_edge_reporting_service_pb2.ScheduleLineageEdgeReportRequest()
            outgoing_0.context.CopyFrom(request.context)
            outgoing_0.reason = request.reason
            outgoing_0.annotations.update(dict(request.annotations))
            outgoing_0.details.filters.update(dict(request.context.baggage))
            outgoing_0.context.tenant_id = tenant_id.get()
            response_0 = await deps.clients.lineage_lineage_edge_reporting.ScheduleLineageEdgeReport(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = datasets_v1_data_schema_validation_service_pb2.CheckDataSchemaEligibilityRequest(
                context=request.context,
                data_schema=datasets_v1_datasets_pb2.DataSchema(
                    children=[
                        datasets_v1_datasets_pb2.DataSchema(
                            manager=identity_v1_refs_pb2.UserRef(email=request.details.new_owner.email)
                        )
                    ]
                )
            )
            port_1: FeatureViewLifecycleTerminateFeatureView1Port = FeatureViewLifecycleTerminateFeatureView1Adapter(
                deps.clients.datasets_data_schema_validation,
                deps.settings.timeout
            )
            response_1 = await port_1.execute(outgoing_1)
            returned_0_0 = response_0.result.status
            if returned_0_0:
                response.outcome.status = returned_0_0
            returned_0_1 = response_0.result.details
            response.result.details.update(returned_0_1)
            returned_1_0 = response_1.result.reference_ids
            response.result.reference_ids.extend(returned_1_0)
            echoed_0 = request.feature_view_id
            response.feature_view.feature_view_id = echoed_0
            echoed_1 = request.details.effective_at
            response.outcome.effective_at.CopyFrom(echoed_1)
            return response
