"""Reusable transport mixin for FeatureViewSyncService."""

from __future__ import annotations

from collections.abc import AsyncIterator
from functools import partial
from typing import cast
import asyncio
import logging

import grpc

from acme.anomalies.v1 import (
    anomaly_feedback_workflow_service_pb2 as anomalies_v1_anomaly_feedback_workflow_service_pb2,
)
from acme.chat.v1 import chat_room_service_pb2 as chat_v1_chat_room_service_pb2
from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.datasets.v1 import dataset_service_pb2 as datasets_v1_dataset_service_pb2
from acme.datasets.v1 import refs_pb2 as datasets_v1_refs_pb2
from acme.featurestore.v1 import entity_calculation_service_pb2 as featurestore_v1_entity_calculation_service_pb2
from acme.featurestore.v1 import entity_validation_service_pb2 as featurestore_v1_entity_validation_service_pb2
from acme.featurestore.v1 import feature_value_import_service_pb2 as featurestore_v1_feature_value_import_service_pb2
from acme.featurestore.v1 import (
    feature_view_calculation_service_pb2 as featurestore_v1_feature_view_calculation_service_pb2,
)
from acme.featurestore.v1 import feature_view_sync_service_pb2 as featurestore_v1_feature_view_sync_service_pb2
from acme.featurestore.v1 import featurestore_pb2 as featurestore_v1_featurestore_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.metrics.v1 import dashboard_notification_service_pb2 as metrics_v1_dashboard_notification_service_pb2
from acme.venues.v1 import venue_validation_service_pb2 as venues_v1_venue_validation_service_pb2
from acme.venues.v1 import venues_pb2 as venues_v1_venues_pb2

from acme_data.domains.featurestore import hooks
from acme_data.domains.featurestore.adapters import FeatureViewSyncSyncFeatureViews0Adapter
from acme_data.domains.featurestore.dependencies import Dependencies
from acme_data.domains.featurestore.models import FeatureViewSyncPushFeatureView0Command
from acme_data.domains.featurestore.models import to_feature_view_sync_push_feature_view0_command
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class FeatureViewSyncServicerHandlers:
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    @retry_transient
    async def GetFeatureViewSyncState(
        self, request: featurestore_v1_feature_view_sync_service_pb2.GetFeatureViewSyncStateRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_feature_view_sync_service_pb2.GetFeatureViewSyncStateResponse:
        """Returns a feature view."""
        return await self.handle_get_feature_view_sync_state(request)

    @rpc_errors
    @retry_transient
    async def ListFeatureViewConflicts(
        self, request: featurestore_v1_feature_view_sync_service_pb2.ListFeatureViewConflictsRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_feature_view_sync_service_pb2.ListFeatureViewConflictsResponse:
        """Lists feature views a page at a time."""
        return await self.handle_list_feature_view_conflicts(request)

    @rpc_errors
    async def PushFeatureView(
        self, request: featurestore_v1_feature_view_sync_service_pb2.PushFeatureViewRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_feature_view_sync_service_pb2.PushFeatureViewResponse:
        """Pushs a feature view."""
        return await self.handle_push_feature_view(request)

    @rpc_errors
    async def ReconcileFeatureViews(
        self, request: featurestore_v1_feature_view_sync_service_pb2.ReconcileFeatureViewsRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_feature_view_sync_service_pb2.ReconcileFeatureViewsResponse:
        """Reconciles a feature view."""
        return await self.handle_reconcile_feature_views(request)

    @stream_errors
    async def StreamFeatureViewChanges(
        self, requests: AsyncIterator[
            featurestore_v1_feature_view_sync_service_pb2.StreamFeatureViewChangesRequest
        ], context: grpc.aio.ServicerContext,
    ) -> AsyncIterator[featurestore_v1_feature_view_sync_service_pb2.StreamFeatureViewChangesResponse]:
        """Exchanges changes of feature views with a peer."""
        async for request in requests:
            yield await self.handle_stream_feature_view_changes(request)

    @rpc_errors
    async def SyncFeatureViews(
        self, request: featurestore_v1_feature_view_sync_service_pb2.SyncFeatureViewsRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_feature_view_sync_service_pb2.SyncFeatureViewsResponse:
        """Syncs a feature view."""
        return await self.handle_sync_feature_views(request)

    async def handle_get_feature_view_sync_state(
        self,
        request: featurestore_v1_feature_view_sync_service_pb2.GetFeatureViewSyncStateRequest
    ) -> featurestore_v1_feature_view_sync_service_pb2.GetFeatureViewSyncStateResponse:
        """Returns a feature view."""
        deps = self.deps
        response = featurestore_v1_feature_view_sync_service_pb2.GetFeatureViewSyncStateResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('GetFeatureViewSyncState', extra={'fields': {'domain': 'featurestore'}})
            await deps.repository.audit(request.context.tenant_id, 'GetFeatureViewSyncState', {})
            response_0 = featurestore_v1_entity_calculation_service_pb2.ExplainEntityCalculationResponse()
            response_1 = datasets_v1_dataset_service_pb2.WatchDatasetsResponse()
            outgoing_0 = featurestore_v1_entity_calculation_service_pb2.ExplainEntityCalculationRequest(
                context=request.context,
                entity=featurestore_v1_featurestore_pb2.Entity(
                    relationship_manager=identity_v1_refs_pb2.UserRef(
                        email=request.context.actor.email,
                        user_id=request.context.actor.user_id
                    )
                )
            )
            response_0 = await deps.clients.featurestore_entity_calculation.ExplainEntityCalculation(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = datasets_v1_dataset_service_pb2.WatchDatasetsRequest(
                context=request.context,
                subscriber=common_v1_contact_pb2.ContactInfo(email=response_0.entity.contact.email)
            )
            async for chunk_1 in deps.clients.datasets_dataset.WatchDatasets(outgoing_1, timeout=deps.settings.timeout):
                response_1 = chunk_1
            returned_0_0 = response_0.entity.contact.email
            if returned_0_0:
                response.feature_view.owner.email = returned_0_0
            echoed_0 = request.feature_view_id
            response.feature_view.feature_view_id = echoed_0
            return response

    async def handle_list_feature_view_conflicts(
        self,
        request: featurestore_v1_feature_view_sync_service_pb2.ListFeatureViewConflictsRequest
    ) -> featurestore_v1_feature_view_sync_service_pb2.ListFeatureViewConflictsResponse:
        """Lists feature views a page at a time."""
        deps = self.deps
        response = featurestore_v1_feature_view_sync_service_pb2.ListFeatureViewConflictsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ListFeatureViewConflicts', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ListFeatureViewConflicts',
                {'order_by': request.order_by}
            )
            response_0 = featurestore_v1_feature_view_calculation_service_pb2.SimulateFeatureViewResponse()
            outgoing_0 = featurestore_v1_feature_view_calculation_service_pb2.SimulateFeatureViewRequest(
                context=request.context,
                feature_view=featurestore_v1_featurestore_pb2.FeatureView(
                    address=common_v1_address_pb2.PostalAddress(region=request.filter.region),
                    audit=common_v1_audit_pb2.AuditInfo(created_at=request.filter.created_after),
                    owner=identity_v1_refs_pb2.UserRef(
                        email=request.context.actor.email,
                        user_id=request.context.actor.user_id
                    )
                )
            )
            response_0 = await deps.clients.featurestore_feature_view_calculation.SimulateFeatureView(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.feature_view.owner.email
            returned_0_0_part_0 = response.feature_views.add()
            if returned_0_0:
                returned_0_0_part_0.owner.email = returned_0_0
            return response

    async def handle_push_feature_view(
        self,
        request: featurestore_v1_feature_view_sync_service_pb2.PushFeatureViewRequest
    ) -> featurestore_v1_feature_view_sync_service_pb2.PushFeatureViewResponse:
        """Pushs a feature view."""
        deps = self.deps
        response = featurestore_v1_feature_view_sync_service_pb2.PushFeatureViewResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('PushFeatureView', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'PushFeatureView', {'reason': request.reason})
            await deps.repository.save_feature_view(request.context.tenant_id, request.feature_view)
            response_0 = anomalies_v1_anomaly_feedback_workflow_service_pb2.ResumeAnomalyFeedbackWorkflowResponse()
            response_1 = metrics_v1_dashboard_notification_service_pb2.SendDashboardTestNoticeResponse()
            response_2 = datasets_v1_dataset_service_pb2.BatchGetDatasetsResponse()
            command_0 = FeatureViewSyncPushFeatureView0Command.model_validate(
                {
                    'context': request.context,
                    'anomaly_feedback_subject_display_name': request.feature_view.owner.display_name,
                    'details_notify_email': request.feature_view.owner.email,
                    'anomaly_feedback_measurements_unit': request.feature_view.dimensions.unit
                }
            )
            outgoing_0 = to_feature_view_sync_push_feature_view0_command(command_0)
            response_0 = await deps.clients.anomalies_anomaly_feedback_workflow.ResumeAnomalyFeedbackWorkflow(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = metrics_v1_dashboard_notification_service_pb2.SendDashboardTestNoticeRequest(
                context=request.context,
                details=metrics_v1_dashboard_notification_service_pb2.SendDashboardTestNoticeRequest.Details(
                    recipient=common_v1_contact_pb2.ContactInfo(email=request.feature_view.owner.email)
                )
            )
            send_1 = partial(
                deps.clients.metrics_dashboard_notification.SendDashboardTestNotice,
                timeout=deps.settings.timeout
            )
            response_1 = await send_1(outgoing_1)
            outgoing_2 = datasets_v1_dataset_service_pb2.BatchGetDatasetsRequest(context=request.context)
            response_2 = await hooks.feature_view_sync_push_feature_view2(
                deps.clients.datasets_dataset,
                outgoing_2,
                deps.settings.timeout
            )
            returned_0_0 = response_0.anomaly_feedback.subject.code
            if returned_0_0:
                response.feature_view.code = returned_0_0
            returned_1_0 = response_1.outcome.message
            if returned_1_0:
                response.outcome.message = returned_1_0
            returned_2_0 = response_2.result.details
            response.result.details.update(returned_2_0)
            echoed_0 = request.feature_view_id
            response.feature_view.feature_view_id = echoed_0
            echoed_1 = request.feature_view.specs
            response.feature_view.specs.update(echoed_1)
            return response

    async def handle_reconcile_feature_views(
        self,
        request: featurestore_v1_feature_view_sync_service_pb2.ReconcileFeatureViewsRequest
    ) -> featurestore_v1_feature_view_sync_service_pb2.ReconcileFeatureViewsResponse:
        """Reconciles a feature view."""
        deps = self.deps
        response = featurestore_v1_feature_view_sync_service_pb2.ReconcileFeatureViewsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ReconcileFeatureViews', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'ReconcileFeatureViews', {'reason': request.reason})
            await deps.repository.save_feature_view(request.context.tenant_id, request.feature_view)
            response_0 = chat_v1_chat_room_service_pb2.ListChatRoomsResponse()
            response_1 = venues_v1_venue_validation_service_pb2.ValidateVenueResponse()
            outgoing_0 = chat_v1_chat_room_service_pb2.ListChatRoomsRequest(
                context=request.context,
                filter=chat_v1_chat_room_service_pb2.ListChatRoomsRequest.Filter(
                    created_after=request.feature_view.audit.updated_at,
                    owner_id=request.feature_view.owner.user_id,
                    region=request.feature_view.address.region
                )
            )
            outgoing_1 = venues_v1_venue_validation_service_pb2.ValidateVenueRequest(
                context=request.context,
                venue=venues_v1_venues_pb2.Venue(
                    address=common_v1_address_pb2.PostalAddress(region=request.feature_view.address.region),
                    audit=common_v1_audit_pb2.AuditInfo(updated_by=request.feature_view.audit.updated_by),
                    owner=identity_v1_refs_pb2.UserRef(display_name=request.feature_view.owner.display_name)
                )
            )
            response_0, response_1 = await asyncio.gather(
                deps.clients.chat_chat_room.ListChatRooms(outgoing_0, timeout=deps.settings.timeout),
                deps.clients.venues_venue_validation.ValidateVenue(outgoing_1, timeout=deps.settings.timeout),
            )
            returned_0_0 = response_0.result.status
            if returned_0_0:
                response.outcome.status = returned_0_0
            returned_1_0 = response_1.outcome.status
            if returned_1_0:
                response.result.status = returned_1_0
            returned_1_1 = response_1.venue.name
            if returned_1_1:
                response.feature_view.name = returned_1_1
            echoed_0 = request.feature_view_id
            response.feature_view.feature_view_id = echoed_0
            echoed_1 = request.feature_view.specs
            response.feature_view.specs.update(echoed_1)
            return response

    async def handle_stream_feature_view_changes(
        self,
        request: featurestore_v1_feature_view_sync_service_pb2.StreamFeatureViewChangesRequest
    ) -> featurestore_v1_feature_view_sync_service_pb2.StreamFeatureViewChangesResponse:
        """Exchanges changes of feature views with a peer."""
        deps = self.deps
        response = featurestore_v1_feature_view_sync_service_pb2.StreamFeatureViewChangesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('StreamFeatureViewChanges', extra={'fields': {'cursor': request.cursor}})
            await deps.repository.audit(
                request.context.tenant_id,
                'StreamFeatureViewChanges',
                {'cursor': request.cursor}
            )
            if request.WhichOneof('frame') == 'change':
                await deps.repository.save_feature_view(request.context.tenant_id, request.change)
            response_0 = featurestore_v1_entity_validation_service_pb2.ValidateEntityResponse()
            outgoing_0 = featurestore_v1_entity_validation_service_pb2.ValidateEntityRequest()
            outgoing_0.context.CopyFrom(request.context)
            if request.WhichOneof('frame') == 'change':
                outgoing_0.entity.audit.etag = request.change.audit.etag
            if request.WhichOneof('frame') == 'change' and request.change.WhichOneof('locator') == 'address':
                outgoing_0.entity.primary_address.region = request.change.address.region
            if request.WhichOneof('frame') == 'change':
                outgoing_0.entity.audit.updated_by = request.change.audit.updated_by
            response_0 = await deps.clients.featurestore_entity_validation.ValidateEntity(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.entity.contact.email
            if returned_0_0:
                response.feature_view.owner.email = returned_0_0
            echoed_0 = request.change.name
            response.feature_view.name = echoed_0
            echoed_1 = request.ack.sequence
            response.sequence = echoed_1
            return response

    async def handle_sync_feature_views(
        self,
        request: featurestore_v1_feature_view_sync_service_pb2.SyncFeatureViewsRequest
    ) -> featurestore_v1_feature_view_sync_service_pb2.SyncFeatureViewsResponse:
        """Syncs a feature view."""
        deps = self.deps
        response = featurestore_v1_feature_view_sync_service_pb2.SyncFeatureViewsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SyncFeatureViews', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'SyncFeatureViews', {'reason': request.reason})
            await deps.repository.save_feature_view(request.context.tenant_id, request.feature_view)
            response_0 = featurestore_v1_entity_validation_service_pb2.ExplainEntityDecisionResponse()
            response_1 = featurestore_v1_feature_value_import_service_pb2.RetryFeatureValueImportResponse()
            outgoing_0 = featurestore_v1_entity_validation_service_pb2.ExplainEntityDecisionRequest(
                context=request.context,
                entity=featurestore_v1_featurestore_pb2.Entity(
                    audit=common_v1_audit_pb2.AuditInfo(updated_at=request.feature_view.audit.updated_at),
                    primary_address=common_v1_address_pb2.PostalAddress(
                        country_code=request.feature_view.address.country_code,
                        locality=request.feature_view.address.locality
                    ),
                    relationship_manager=identity_v1_refs_pb2.UserRef(user_id=request.feature_view.owner.user_id)
                )
            )
            response_0 = await FeatureViewSyncSyncFeatureViews0Adapter(
                deps.clients.featurestore_entity_validation,
                deps.settings.timeout
            )(outgoing_0)
            outgoing_1 = featurestore_v1_feature_value_import_service_pb2.RetryFeatureValueImportRequest(
                context=request.context,
                details=featurestore_v1_feature_value_import_service_pb2.RetryFeatureValueImportRequest.Details(
                    notify=common_v1_contact_pb2.ContactInfo(phone=response_0.entity.contact.phone)
                ),
                feature_value=featurestore_v1_featurestore_pb2.FeatureValue(
                    measurements=[
                        featurestore_v1_featurestore_pb2.FeatureValueMeasurement(
                            unit=request.feature_view.dimensions.unit
                        )
                    ],
                    subject=datasets_v1_refs_pb2.DatasetRef(display_name=request.feature_view.owner.display_name)
                )
            )
            response_1 = cast(featurestore_v1_feature_value_import_service_pb2.RetryFeatureValueImportResponse, await deps.bus.request(
                'acme.featurestore.v1.FeatureViewSyncService/SyncFeatureViews/1', outgoing_1, deps.settings.timeout,
            ))
            returned_0_0 = response_0.outcome.status
            if returned_0_0:
                response.result.status = returned_0_0
            returned_1_0 = response_1.outcome.message
            if returned_1_0:
                response.result.message = returned_1_0
            returned_1_1 = response_1.outcome.status
            if returned_1_1:
                response.outcome.status = returned_1_1
            echoed_0 = request.feature_view_id
            response.feature_view.feature_view_id = echoed_0
            echoed_1 = request.feature_view.code
            response.feature_view.code = echoed_1
            return response
