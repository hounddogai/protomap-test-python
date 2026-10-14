"""Keeps entities in step with the systems of record in other regions."""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any
from typing import cast
import logging

from google.protobuf.json_format import MessageToDict
from google.protobuf.json_format import ParseDict
import grpc

from acme.anomalies.v1 import detector_approval_service_pb2 as anomalies_v1_detector_approval_service_pb2
from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.datasets.v1 import data_schema_validation_service_pb2 as datasets_v1_data_schema_validation_service_pb2
from acme.datasets.v1 import dataset_service_pb2 as datasets_v1_dataset_service_pb2
from acme.datasets.v1 import (
    dataset_version_validation_service_pb2 as datasets_v1_dataset_version_validation_service_pb2,
)
from acme.datasets.v1 import datasets_pb2 as datasets_v1_datasets_pb2
from acme.documents.v1 import document_service_pb2 as documents_v1_document_service_pb2
from acme.featureflags.v1 import feature_flag_service_pb2 as featureflags_v1_feature_flag_service_pb2
from acme.featureflags.v1 import (
    feature_flag_validation_service_pb2 as featureflags_v1_feature_flag_validation_service_pb2,
)
from acme.featureflags.v1 import featureflags_pb2 as featureflags_v1_featureflags_pb2
from acme.featurestore.v1 import entity_sync_service_pb2 as featurestore_v1_entity_sync_service_pb2
from acme.featurestore.v1 import entity_sync_service_pb2_grpc as featurestore_v1_entity_sync_service_pb2_grpc
from acme.featurestore.v1 import (
    feature_value_validation_service_pb2 as featurestore_v1_feature_value_validation_service_pb2,
)
from acme.featurestore.v1 import feature_view_query_service_pb2 as featurestore_v1_feature_view_query_service_pb2
from acme.featurestore.v1 import (
    feature_view_reporting_service_pb2 as featurestore_v1_feature_view_reporting_service_pb2,
)
from acme.featurestore.v1 import featurestore_pb2 as featurestore_v1_featurestore_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.identity.v1 import user_query_service_pb2 as identity_v1_user_query_service_pb2
from acme.metrics.v1 import dashboard_validation_service_pb2 as metrics_v1_dashboard_validation_service_pb2

from acme_data.domains.featurestore import hooks
from acme_data.domains.featurestore.adapters import EntitySyncReconcileEntities0Adapter
from acme_data.domains.featurestore.adapters import EntitySyncReconcileEntities0Port
from acme_data.domains.featurestore.adapters import EntitySyncStreamEntityChanges0Adapter
from acme_data.domains.featurestore.dependencies import Dependencies
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class EntitySyncServicer(featurestore_v1_entity_sync_service_pb2_grpc.EntitySyncServiceServicer):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    @retry_transient
    async def GetEntitySyncState(
        self, request: featurestore_v1_entity_sync_service_pb2.GetEntitySyncStateRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_entity_sync_service_pb2.GetEntitySyncStateResponse:
        """Returns an entity."""
        return await self.handle_get_entity_sync_state(request)

    @rpc_errors
    @retry_transient
    async def ListEntityConflicts(
        self, request: featurestore_v1_entity_sync_service_pb2.ListEntityConflictsRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_entity_sync_service_pb2.ListEntityConflictsResponse:
        """Lists entities a page at a time."""
        return await self.handle_list_entity_conflicts(request)

    @rpc_errors
    async def PushEntity(
        self, request: featurestore_v1_entity_sync_service_pb2.PushEntityRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_entity_sync_service_pb2.PushEntityResponse:
        """Pushs an entity."""
        return await self.handle_push_entity(request)

    @rpc_errors
    async def ReconcileEntities(
        self, request: featurestore_v1_entity_sync_service_pb2.ReconcileEntitiesRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_entity_sync_service_pb2.ReconcileEntitiesResponse:
        """Reconciles an entity."""
        return await self.handle_reconcile_entities(request)

    @stream_errors
    async def StreamEntityChanges(
        self, requests: AsyncIterator[
            featurestore_v1_entity_sync_service_pb2.StreamEntityChangesRequest
        ], context: grpc.aio.ServicerContext,
    ) -> AsyncIterator[featurestore_v1_entity_sync_service_pb2.StreamEntityChangesResponse]:
        """Exchanges changes of entities with a peer."""
        async for request in requests:
            yield await self.handle_stream_entity_changes(request)

    @rpc_errors
    async def SyncEntities(
        self, request: featurestore_v1_entity_sync_service_pb2.SyncEntitiesRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_entity_sync_service_pb2.SyncEntitiesResponse:
        """Syncs an entity."""
        return await self.handle_sync_entities(request)

    async def handle_get_entity_sync_state(
        self,
        request: featurestore_v1_entity_sync_service_pb2.GetEntitySyncStateRequest
    ) -> featurestore_v1_entity_sync_service_pb2.GetEntitySyncStateResponse:
        """Returns an entity."""
        deps = self.deps
        response = featurestore_v1_entity_sync_service_pb2.GetEntitySyncStateResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('GetEntitySyncState', extra={'fields': {'domain': 'featurestore'}})
            await deps.repository.audit(request.context.tenant_id, 'GetEntitySyncState', {})
            response_0 = datasets_v1_data_schema_validation_service_pb2.CheckDataSchemaEligibilityResponse()
            outgoing_0 = datasets_v1_data_schema_validation_service_pb2.CheckDataSchemaEligibilityRequest(
                context=request.context,
                data_schema=datasets_v1_datasets_pb2.DataSchema(
                    children=[
                        datasets_v1_datasets_pb2.DataSchema(
                            children=[
                                datasets_v1_datasets_pb2.DataSchema(
                                    children=[datasets_v1_datasets_pb2.DataSchema(parent_id=request.entity_id)],
                                    manager=identity_v1_refs_pb2.UserRef(
                                        email=request.context.actor.email,
                                        user_id=request.context.actor.user_id
                                    )
                                )
                            ]
                        )
                    ]
                ),
                details=datasets_v1_data_schema_validation_service_pb2.CheckDataSchemaEligibilityRequest.Details(
                    locale=request.context.locale
                )
            )
            response_0 = await deps.clients.datasets_data_schema_validation.CheckDataSchemaEligibility(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.data_schema.audit.etag
            if returned_0_0:
                response.entity.audit.etag = returned_0_0
            echoed_0 = request.entity_id
            response.entity.entity_id = echoed_0
            return response

    async def handle_list_entity_conflicts(
        self,
        request: featurestore_v1_entity_sync_service_pb2.ListEntityConflictsRequest
    ) -> featurestore_v1_entity_sync_service_pb2.ListEntityConflictsResponse:
        """Lists entities a page at a time."""
        deps = self.deps
        response = featurestore_v1_entity_sync_service_pb2.ListEntityConflictsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ListEntityConflicts', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ListEntityConflicts',
                {'order_by': request.order_by}
            )
            response_0 = featureflags_v1_feature_flag_validation_service_pb2.ScoreFeatureFlagResponse()
            outgoing_0 = featureflags_v1_feature_flag_validation_service_pb2.ScoreFeatureFlagRequest(
                context=request.context,
                details=featureflags_v1_feature_flag_validation_service_pb2.ScoreFeatureFlagRequest.Details(
                    destination=common_v1_address_pb2.PostalAddress(region=request.filter.region)
                ),
                feature_flag=featureflags_v1_featureflags_pb2.FeatureFlag(
                    owner=identity_v1_refs_pb2.UserRef(user_id=request.context.actor.user_id)
                )
            )
            response_0 = await deps.clients.featureflags_feature_flag_validation.ScoreFeatureFlag(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.feature_flag.audit.created_by
            returned_0_0_part_0 = response.entities.add()
            if returned_0_0:
                returned_0_0_part_0.audit.created_by = returned_0_0
            return response

    async def handle_push_entity(
        self,
        request: featurestore_v1_entity_sync_service_pb2.PushEntityRequest
    ) -> featurestore_v1_entity_sync_service_pb2.PushEntityResponse:
        """Pushs an entity."""
        deps = self.deps
        response = featurestore_v1_entity_sync_service_pb2.PushEntityResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('PushEntity', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'PushEntity', {'reason': request.reason})
            await deps.repository.save_entity(request.context.tenant_id, request.entity)
            response_0 = datasets_v1_dataset_service_pb2.UpdateDatasetResponse()
            response_1 = datasets_v1_dataset_version_validation_service_pb2.ScoreDatasetVersionResponse()
            outgoing_0 = datasets_v1_dataset_service_pb2.UpdateDatasetRequest(
                context=request.context,
                dataset=datasets_v1_datasets_pb2.Dataset(
                    address=common_v1_address_pb2.PostalAddress(postal_code=request.entity.primary_address.postal_code),
                    audit=common_v1_audit_pb2.AuditInfo(created_at=request.entity.audit.created_at),
                    owner=identity_v1_refs_pb2.UserRef(display_name=request.entity.relationship_manager.display_name)
                )
            )
            response_0 = await hooks.entity_sync_push_entity0(
                deps.clients.datasets_dataset,
                outgoing_0,
                deps.settings.timeout
            )
            outgoing_1 = datasets_v1_dataset_version_validation_service_pb2.ScoreDatasetVersionRequest()
            outgoing_1.context.CopyFrom(request.context)
            if response_0.dataset.WhichOneof('locator') == 'address':
                outgoing_1.details.destination.locality = response_0.dataset.address.locality
            outgoing_1.dataset_version.subject.email = request.entity.relationship_manager.email
            if response_0.dataset.WhichOneof('locator') == 'address':
                outgoing_1.details.destination.country_code = response_0.dataset.address.country_code
            if response_0.dataset.WhichOneof('locator') == 'address':
                outgoing_1.details.destination.lines.extend(list(response_0.dataset.address.lines))
            response_1 = await deps.clients.datasets_dataset_version_validation.ScoreDatasetVersion(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.dataset.audit.updated_at
            if returned_0_0.ListFields():
                response.entity.audit.updated_at.MergeFrom(returned_0_0)
            returned_1_0 = response_1.dataset_version.subject.display_name
            if returned_1_0:
                response.entity.relationship_manager.display_name = returned_1_0
            echoed_0 = request.entity_id
            response.entity.entity_id = echoed_0
            echoed_1 = request.entity.contact
            response.entity.contact.CopyFrom(echoed_1)
            return response

    async def handle_reconcile_entities(
        self,
        request: featurestore_v1_entity_sync_service_pb2.ReconcileEntitiesRequest
    ) -> featurestore_v1_entity_sync_service_pb2.ReconcileEntitiesResponse:
        """Reconciles an entity."""
        deps = self.deps
        response = featurestore_v1_entity_sync_service_pb2.ReconcileEntitiesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ReconcileEntities', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'ReconcileEntities', {'reason': request.reason})
            await deps.repository.save_entity(request.context.tenant_id, request.entity)
            response_0 = featurestore_v1_feature_view_reporting_service_pb2.ListFeatureViewReportsResponse()
            response_1 = identity_v1_user_query_service_pb2.ExportUsersResponse()
            outgoing_0 = featurestore_v1_feature_view_reporting_service_pb2.ListFeatureViewReportsRequest(
                context=request.context,
                filter=featurestore_v1_feature_view_reporting_service_pb2.ListFeatureViewReportsRequest.Filter(
                    created_after=request.entity.passport.expires_at,
                    region=request.entity.primary_address.region
                )
            )
            port_0: EntitySyncReconcileEntities0Port = EntitySyncReconcileEntities0Adapter(
                deps.clients.featurestore_feature_view_reporting,
                deps.settings.timeout
            )
            response_0 = await port_0.execute(outgoing_0)
            outgoing_1 = identity_v1_user_query_service_pb2.ExportUsersRequest(
                context=request.context,
                filter=identity_v1_user_query_service_pb2.ExportUsersRequest.Filter(
                    created_after=request.entity.passport.expires_at,
                    owner_id=request.entity.relationship_manager.user_id,
                    region=request.entity.primary_address.region
                )
            )
            async for chunk_1 in deps.clients.identity_user_query.ExportUsers(
                outgoing_1,
                timeout=deps.settings.timeout
            ):
                response_1 = chunk_1
            returned_0_0 = response_0.result.status
            if returned_0_0:
                response.outcome.status = returned_0_0
            echoed_0 = request.entity_id
            response.entity.entity_id = echoed_0
            echoed_1 = request.entity.relationship_manager
            response.entity.relationship_manager.CopyFrom(echoed_1)
            return response

    async def handle_stream_entity_changes(
        self,
        request: featurestore_v1_entity_sync_service_pb2.StreamEntityChangesRequest
    ) -> featurestore_v1_entity_sync_service_pb2.StreamEntityChangesResponse:
        """Exchanges changes of entities with a peer."""
        deps = self.deps
        response = featurestore_v1_entity_sync_service_pb2.StreamEntityChangesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('StreamEntityChanges', extra={'fields': {'cursor': request.cursor}})
            await deps.repository.audit(request.context.tenant_id, 'StreamEntityChanges', {'cursor': request.cursor})
            if request.WhichOneof('frame') == 'change':
                await deps.repository.save_entity(request.context.tenant_id, request.change)
            response_0 = featureflags_v1_feature_flag_service_pb2.BatchGetFeatureFlagsResponse()
            response_1 = documents_v1_document_service_pb2.ListDocumentsResponse()
            outgoing_0 = featureflags_v1_feature_flag_service_pb2.BatchGetFeatureFlagsRequest(context=request.context)
            response_0 = await EntitySyncStreamEntityChanges0Adapter(
                deps.clients.featureflags_feature_flag,
                deps.settings.timeout
            )(outgoing_0)
            outgoing_1 = documents_v1_document_service_pb2.ListDocumentsRequest(
                context=request.context,
                filter=documents_v1_document_service_pb2.ListDocumentsRequest.Filter(
                    created_after=request.change.audit.updated_at,
                    owner_id=request.change.relationship_manager.user_id,
                    region=request.change.primary_address.region
                )
            )
            response_1 = cast(documents_v1_document_service_pb2.ListDocumentsResponse, await deps.bus.request(
                'acme.featurestore.v1.EntitySyncService/StreamEntityChanges/1', outgoing_1, deps.settings.timeout,
            ))
            returned_0_0 = response_0.result.correlation_id
            if returned_0_0:
                response.result.correlation_id = returned_0_0
            returned_0_1 = response_0.result.details
            response.result.details.update(returned_0_1)
            returned_1_0 = response_1.result.message
            if returned_1_0:
                response.result.message = returned_1_0
            echoed_0 = request.change.name
            response.entity.name.CopyFrom(echoed_0)
            echoed_1 = request.change.relationship_manager
            response.entity.relationship_manager.CopyFrom(echoed_1)
            return response

    async def handle_sync_entities(
        self,
        request: featurestore_v1_entity_sync_service_pb2.SyncEntitiesRequest
    ) -> featurestore_v1_entity_sync_service_pb2.SyncEntitiesResponse:
        """Syncs an entity."""
        deps = self.deps
        response = featurestore_v1_entity_sync_service_pb2.SyncEntitiesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SyncEntities', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'SyncEntities', {'reason': request.reason})
            await deps.repository.save_entity(request.context.tenant_id, request.entity)
            response_0 = featurestore_v1_feature_value_validation_service_pb2.PreviewFeatureValueResponse()
            response_1 = featurestore_v1_feature_view_query_service_pb2.BrowseFeatureViewsResponse()
            response_2 = metrics_v1_dashboard_validation_service_pb2.CheckDashboardEligibilityResponse()
            response_3 = anomalies_v1_detector_approval_service_pb2.SubmitDetectorResponse()
            outgoing_0 = featurestore_v1_feature_value_validation_service_pb2.PreviewFeatureValueRequest(
                context=request.context,
                details=featurestore_v1_feature_value_validation_service_pb2.PreviewFeatureValueRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(name=request.entity.contact.name)
                ),
                feature_value=featurestore_v1_featurestore_pb2.FeatureValue(attributes=dict(request.entity.attributes))
            )
            response_0 = await deps.clients.featurestore_feature_value_validation.PreviewFeatureValue(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = featurestore_v1_feature_view_query_service_pb2.BrowseFeatureViewsRequest()
            outgoing_1.context.CopyFrom(request.context)
            outgoing_1.filter.region = request.entity.primary_address.region
            if request.entity.WhichOneof('identity_document') == 'passport':
                outgoing_1.filter.created_after.CopyFrom(request.entity.passport.expires_at)
            response_1 = await deps.clients.featurestore_feature_view_query.BrowseFeatureViews(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            fields_2: dict[str, Any] = {
                'context': request.context,
                'dashboard': {
                    'billing_address': {'recipient': request.entity.primary_address.recipient},
                    'lines': [{'attributes': dict(response_0.feature_value.attributes)}]
                },
                'details': {
                    'contact': {
                        'email': request.entity.contact.email,
                        'preferred_channel': request.entity.contact.preferred_channel
                    }
                }
            }
            outgoing_2 = metrics_v1_dashboard_validation_service_pb2.CheckDashboardEligibilityRequest(**fields_2)
            response_2 = await deps.clients.metrics_dashboard_validation.CheckDashboardEligibility(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            outgoing_3 = anomalies_v1_detector_approval_service_pb2.SubmitDetectorRequest(
                context=request.context,
                details=anomalies_v1_detector_approval_service_pb2.SubmitDetectorRequest.Details(
                    approver=identity_v1_refs_pb2.UserRef(
                        display_name=response_0.feature_value.subject.display_name,
                        email=request.entity.relationship_manager.email
                    )
                )
            )
            document_3 = MessageToDict(outgoing_3, preserving_proto_field_name=True)
            outgoing_3 = ParseDict(document_3, anomalies_v1_detector_approval_service_pb2.SubmitDetectorRequest())
            response_3 = await deps.clients.anomalies_detector_approval.SubmitDetector(
                outgoing_3,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.outcome.next_steps
            response.outcome.next_steps.extend(returned_0_0)
            returned_0_1 = response_0.outcome.status
            if returned_0_1:
                response.outcome.status = returned_0_1
            returned_1_0 = response_1.result.message
            if returned_1_0:
                response.outcome.message = returned_1_0
            returned_2_0 = response_2.dashboard.billing_address.region
            if returned_2_0:
                response.entity.primary_address.region = returned_2_0
            returned_2_1 = response_2.dashboard.billing_address.country_code
            if returned_2_1:
                response.entity.primary_address.country_code = returned_2_1
            returned_3_0 = response_3.detector.audit.created_by
            if returned_3_0:
                response.entity.audit.created_by = returned_3_0
            returned_3_1 = response_3.detector.audit.updated_at
            if returned_3_1.ListFields():
                response.entity.audit.updated_at.MergeFrom(returned_3_1)
            echoed_0 = request.entity_id
            response.entity.entity_id = echoed_0
            echoed_1 = request.entity.name
            response.entity.name.CopyFrom(echoed_1)
            return response
