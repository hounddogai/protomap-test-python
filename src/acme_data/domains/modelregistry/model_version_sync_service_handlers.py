"""Reusable transport mixin for ModelVersionSyncService."""

from __future__ import annotations

from collections.abc import AsyncIterator
from collections.abc import Awaitable
from collections.abc import Callable
from functools import partial
from typing import Any
from typing import cast
import asyncio
import logging

from google.protobuf.json_format import MessageToDict
from google.protobuf.json_format import MessageToJson
from google.protobuf.json_format import Parse
from google.protobuf.json_format import ParseDict
import grpc

from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.customers.v1 import customers_pb2 as customers_v1_customers_pb2
from acme.customers.v1 import household_calculation_service_pb2 as customers_v1_household_calculation_service_pb2
from acme.customers.v1 import household_query_service_pb2 as customers_v1_household_query_service_pb2
from acme.customers.v1 import preference_validation_service_pb2 as customers_v1_preference_validation_service_pb2
from acme.customers.v1 import refs_pb2 as customers_v1_refs_pb2
from acme.featurestore.v1 import entity_reporting_service_pb2 as featurestore_v1_entity_reporting_service_pb2
from acme.featurestore.v1 import entity_sync_service_pb2 as featurestore_v1_entity_sync_service_pb2
from acme.featurestore.v1 import feature_value_import_service_pb2 as featurestore_v1_feature_value_import_service_pb2
from acme.featurestore.v1 import featurestore_pb2 as featurestore_v1_featurestore_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.identity.v1 import user_query_service_pb2 as identity_v1_user_query_service_pb2
from acme.ledger.v1 import ledger_account_query_service_pb2 as ledger_v1_ledger_account_query_service_pb2
from acme.lineage.v1 import impact_approval_service_pb2 as lineage_v1_impact_approval_service_pb2
from acme.modelregistry.v1 import (
    deployment_calculation_service_pb2 as modelregistry_v1_deployment_calculation_service_pb2,
)
from acme.modelregistry.v1 import deployment_import_service_pb2 as modelregistry_v1_deployment_import_service_pb2
from acme.modelregistry.v1 import (
    deployment_validation_service_pb2 as modelregistry_v1_deployment_validation_service_pb2,
)
from acme.modelregistry.v1 import (
    model_version_calculation_service_pb2 as modelregistry_v1_model_version_calculation_service_pb2,
)
from acme.modelregistry.v1 import model_version_sync_service_pb2 as modelregistry_v1_model_version_sync_service_pb2
from acme.modelregistry.v1 import (
    model_version_validation_service_pb2 as modelregistry_v1_model_version_validation_service_pb2,
)
from acme.modelregistry.v1 import modelregistry_pb2 as modelregistry_v1_modelregistry_pb2
from acme.modelregistry.v1 import (
    registered_model_query_service_pb2 as modelregistry_v1_registered_model_query_service_pb2,
)
from acme.notifications.v1 import notification_service_pb2 as notifications_v1_notification_service_pb2

from acme_data.domains.modelregistry import hooks
from acme_data.domains.modelregistry.adapters import ModelVersionSyncPullModelVersions0Adapter
from acme_data.domains.modelregistry.adapters import ModelVersionSyncSyncModelVersions2Adapter
from acme_data.domains.modelregistry.adapters import ModelVersionSyncSyncModelVersions2Port
from acme_data.domains.modelregistry.dependencies import Dependencies
from acme_data.domains.modelregistry.models import ModelVersionSyncStreamModelVersionChanges1Command
from acme_data.domains.modelregistry.models import ModelVersionSyncStreamModelVersionChanges2Command
from acme_data.domains.modelregistry.models import to_model_version_sync_stream_model_version_changes1_command
from acme_data.domains.modelregistry.models import to_model_version_sync_stream_model_version_changes2_command
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import run_steps
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class ModelVersionSyncServicerHandlers:
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    @retry_transient
    async def GetModelVersionSyncState(
        self, request: modelregistry_v1_model_version_sync_service_pb2.GetModelVersionSyncStateRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_model_version_sync_service_pb2.GetModelVersionSyncStateResponse:
        """Returns a model version."""
        return await self.handle_get_model_version_sync_state(request)

    @rpc_errors
    @retry_transient
    async def ListModelVersionConflicts(
        self, request: modelregistry_v1_model_version_sync_service_pb2.ListModelVersionConflictsRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_model_version_sync_service_pb2.ListModelVersionConflictsResponse:
        """Lists model versions a page at a time."""
        return await self.handle_list_model_version_conflicts(request)

    @rpc_errors
    async def PullModelVersions(
        self, request: modelregistry_v1_model_version_sync_service_pb2.PullModelVersionsRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_model_version_sync_service_pb2.PullModelVersionsResponse:
        """Pulls a model version."""
        return await self.handle_pull_model_versions(request)

    @rpc_errors
    async def PushModelVersion(
        self, request: modelregistry_v1_model_version_sync_service_pb2.PushModelVersionRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_model_version_sync_service_pb2.PushModelVersionResponse:
        """Pushs a model version."""
        return await self.handle_push_model_version(request)

    @rpc_errors
    async def ReconcileModelVersions(
        self, request: modelregistry_v1_model_version_sync_service_pb2.ReconcileModelVersionsRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_model_version_sync_service_pb2.ReconcileModelVersionsResponse:
        """Reconciles a model version."""
        return await self.handle_reconcile_model_versions(request)

    @rpc_errors
    async def ResolveModelVersionConflict(
        self, request: modelregistry_v1_model_version_sync_service_pb2.ResolveModelVersionConflictRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_model_version_sync_service_pb2.ResolveModelVersionConflictResponse:
        """Resolves a model version."""
        return await self.handle_resolve_model_version_conflict(request)

    @stream_errors
    async def StreamModelVersionChanges(
        self, requests: AsyncIterator[
            modelregistry_v1_model_version_sync_service_pb2.StreamModelVersionChangesRequest
        ], context: grpc.aio.ServicerContext,
    ) -> AsyncIterator[modelregistry_v1_model_version_sync_service_pb2.StreamModelVersionChangesResponse]:
        """Exchanges changes of model versions with a peer."""
        async for request in requests:
            yield await self.handle_stream_model_version_changes(request)

    @rpc_errors
    async def SyncModelVersions(
        self, request: modelregistry_v1_model_version_sync_service_pb2.SyncModelVersionsRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_model_version_sync_service_pb2.SyncModelVersionsResponse:
        """Syncs a model version."""
        return await self.handle_sync_model_versions(request)

    async def handle_get_model_version_sync_state(
        self,
        request: modelregistry_v1_model_version_sync_service_pb2.GetModelVersionSyncStateRequest
    ) -> modelregistry_v1_model_version_sync_service_pb2.GetModelVersionSyncStateResponse:
        """Returns a model version."""
        deps = self.deps
        response = modelregistry_v1_model_version_sync_service_pb2.GetModelVersionSyncStateResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('GetModelVersionSyncState', extra={'fields': {'domain': 'modelregistry'}})
            await deps.repository.audit(request.context.tenant_id, 'GetModelVersionSyncState', {})
            response_0 = featurestore_v1_feature_value_import_service_pb2.RetryFeatureValueImportResponse()
            outgoing_0 = featurestore_v1_feature_value_import_service_pb2.RetryFeatureValueImportRequest(
                context=request.context,
                details=featurestore_v1_feature_value_import_service_pb2.RetryFeatureValueImportRequest.Details(
                    notify=common_v1_contact_pb2.ContactInfo(email=request.context.actor.email)
                ),
                feature_value=featurestore_v1_featurestore_pb2.FeatureValue(correlation_id=request.model_version_id)
            )
            response_0 = await deps.clients.featurestore_feature_value_import.RetryFeatureValueImport(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.outcome.status
            if returned_0_0:
                response.result.status = returned_0_0
            echoed_0 = request.model_version_id
            response.model_version.model_version_id = echoed_0
            return response

    async def handle_list_model_version_conflicts(
        self,
        request: modelregistry_v1_model_version_sync_service_pb2.ListModelVersionConflictsRequest
    ) -> modelregistry_v1_model_version_sync_service_pb2.ListModelVersionConflictsResponse:
        """Lists model versions a page at a time."""
        deps = self.deps
        response = modelregistry_v1_model_version_sync_service_pb2.ListModelVersionConflictsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ListModelVersionConflicts', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ListModelVersionConflicts',
                {'order_by': request.order_by}
            )
            response_0 = customers_v1_preference_validation_service_pb2.ValidatePreferenceResponse()
            response_1 = modelregistry_v1_model_version_validation_service_pb2.LintModelVersionsResponse()
            outgoing_0 = customers_v1_preference_validation_service_pb2.ValidatePreferenceRequest(
                context=request.context,
                details=customers_v1_preference_validation_service_pb2.ValidatePreferenceRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(email=request.context.actor.email)
                )
            )
            response_0 = await deps.clients.customers_preference_validation.ValidatePreference(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = modelregistry_v1_model_version_validation_service_pb2.LintModelVersionsRequest(
                context=request.context,
                details=modelregistry_v1_model_version_validation_service_pb2.LintModelVersionsRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(email=response_0.preference.owner.email)
                ),
                model_version=modelregistry_v1_modelregistry_pb2.ModelVersion(
                    correlation_id=response_0.result.correlation_id,
                    subject=customers_v1_refs_pb2.CustomerRef(
                        display_name=response_0.preference.owner.display_name,
                        email=response_0.preference.block.notify_email
                    )
                )
            )
            steps_1 = [
                partial(
                    deps.clients.modelregistry_model_version_validation.LintModelVersions,
                    outgoing_1,
                    timeout=deps.settings.timeout
                )
            ]
            results_1 = await run_steps(steps_1)
            response_1 = results_1[-1]
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.result.message = returned_0_0
            returned_1_0 = response_1.model_version.correlation_id
            if returned_1_0:
                response.result.correlation_id = returned_1_0
            returned_1_1 = response_1.model_version.subject
            returned_1_1_part_0 = response.model_versions.add()
            if returned_1_1.ListFields():
                returned_1_1_part_0.subject.MergeFrom(returned_1_1)
            return response

    async def handle_pull_model_versions(
        self,
        request: modelregistry_v1_model_version_sync_service_pb2.PullModelVersionsRequest
    ) -> modelregistry_v1_model_version_sync_service_pb2.PullModelVersionsResponse:
        """Pulls a model version."""
        deps = self.deps
        response = modelregistry_v1_model_version_sync_service_pb2.PullModelVersionsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('PullModelVersions', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'PullModelVersions', {'reason': request.reason})
            await deps.repository.save_model_version(request.context.tenant_id, request.model_version)
            response_0 = featurestore_v1_entity_reporting_service_pb2.CountEntityTotalsResponse()
            response_1 = featurestore_v1_entity_sync_service_pb2.PushEntityResponse()
            response_2 = customers_v1_household_query_service_pb2.BrowseHouseholdsResponse()
            outgoing_0 = featurestore_v1_entity_reporting_service_pb2.CountEntityTotalsRequest(
                context=request.context,
                filter=featurestore_v1_entity_reporting_service_pb2.CountEntityTotalsRequest.Filter(
                    created_after=request.model_version.occurred_at,
                    labels=dict(request.annotations),
                    owner_id=request.model_version.model_version_id
                )
            )
            response_0 = await ModelVersionSyncPullModelVersions0Adapter(
                deps.clients.featurestore_entity_reporting,
                deps.settings.timeout
            )(outgoing_0)
            outgoing_1 = featurestore_v1_entity_sync_service_pb2.PushEntityRequest(
                context=request.context,
                details=featurestore_v1_entity_sync_service_pb2.PushEntityRequest.Details(
                    checksum=request.details.checksum,
                    peer_region=request.details.peer_region
                ),
                entity=featurestore_v1_featurestore_pb2.Entity(
                    relationship_manager=identity_v1_refs_pb2.UserRef(
                        display_name=request.model_version.subject.display_name,
                        email=request.model_version.subject.email
                    )
                )
            )
            response_1 = cast(featurestore_v1_entity_sync_service_pb2.PushEntityResponse, await deps.bus.request(
                'acme.modelregistry.v1.ModelVersionSyncService/PullModelVersions/1', outgoing_1, deps.settings.timeout,
            ))
            outgoing_2 = customers_v1_household_query_service_pb2.BrowseHouseholdsRequest(
                context=request.context,
                filter=customers_v1_household_query_service_pb2.BrowseHouseholdsRequest.Filter(
                    region=response_1.entity.primary_address.region
                )
            )
            response_2 = await deps.clients.customers_household_query.BrowseHouseholds(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.status
            if returned_0_0:
                response.outcome.status = returned_0_0
            returned_1_0 = response_1.result.correlation_id
            if returned_1_0:
                response.model_version.correlation_id = returned_1_0
            returned_2_0 = response_2.result.message
            if returned_2_0:
                response.outcome.message = returned_2_0
            echoed_0 = request.model_version_id
            response.model_version.model_version_id = echoed_0
            echoed_1 = request.model_version.occurred_at
            response.model_version.occurred_at.CopyFrom(echoed_1)
            return response

    async def handle_push_model_version(
        self,
        request: modelregistry_v1_model_version_sync_service_pb2.PushModelVersionRequest
    ) -> modelregistry_v1_model_version_sync_service_pb2.PushModelVersionResponse:
        """Pushs a model version."""
        deps = self.deps
        response = modelregistry_v1_model_version_sync_service_pb2.PushModelVersionResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('PushModelVersion', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'PushModelVersion', {'reason': request.reason})
            await deps.repository.save_model_version(request.context.tenant_id, request.model_version)
            response_0 = modelregistry_v1_model_version_validation_service_pb2.CheckModelVersionEligibilityResponse()
            response_1 = lineage_v1_impact_approval_service_pb2.ListPendingImpactsResponse()
            outgoing_0 = modelregistry_v1_model_version_validation_service_pb2.CheckModelVersionEligibilityRequest(
                context=request.context,
                model_version=modelregistry_v1_modelregistry_pb2.ModelVersion(
                    subject=customers_v1_refs_pb2.CustomerRef(
                        customer_id=request.model_version.subject.customer_id,
                        email=request.model_version.subject.email
                    )
                ),
                model_version_id=request.model_version.model_version_id
            )
            method_name_0 = 'CheckModelVersionEligibility'
            response_0 = await getattr(
                deps.clients.modelregistry_model_version_validation,
                method_name_0
            )(outgoing_0, timeout=deps.settings.timeout)
            fields_1: dict[str, Any] = {
                'context': request.context,
                'filter': {
                    'created_after': response_0.outcome.effective_at,
                    'owner_id': response_0.model_version.model_version_id
                }
            }
            outgoing_1 = lineage_v1_impact_approval_service_pb2.ListPendingImpactsRequest(**fields_1)
            response_1 = await deps.clients.lineage_impact_approval.ListPendingImpacts(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.model_version.sequence
            if returned_0_0:
                response.model_version.sequence = returned_0_0
            returned_0_1 = response_0.model_version.kind
            if returned_0_1:
                response.model_version.kind = returned_0_1
            returned_1_0 = response_1.result.message
            if returned_1_0:
                response.outcome.message = returned_1_0
            returned_1_1 = response_1.result.correlation_id
            if returned_1_1:
                response.result.correlation_id = returned_1_1
            echoed_0 = request.model_version_id
            response.model_version.model_version_id = echoed_0
            echoed_1 = request.model_version.subject
            response.model_version.subject.CopyFrom(echoed_1)
            return response

    async def handle_reconcile_model_versions(
        self,
        request: modelregistry_v1_model_version_sync_service_pb2.ReconcileModelVersionsRequest
    ) -> modelregistry_v1_model_version_sync_service_pb2.ReconcileModelVersionsResponse:
        """Reconciles a model version."""
        deps = self.deps
        response = modelregistry_v1_model_version_sync_service_pb2.ReconcileModelVersionsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ReconcileModelVersions', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'ReconcileModelVersions', {'reason': request.reason})
            await deps.repository.save_model_version(request.context.tenant_id, request.model_version)
            response_0 = modelregistry_v1_model_version_calculation_service_pb2.EstimateModelVersionResponse()
            response_1 = modelregistry_v1_deployment_calculation_service_pb2.CalculateDeploymentResponse()
            outgoing_0 = modelregistry_v1_model_version_calculation_service_pb2.EstimateModelVersionRequest(
                context=request.context,
                model_version=modelregistry_v1_modelregistry_pb2.ModelVersion(
                    attributes=dict(request.model_version.attributes),
                    correlation_id=request.model_version.correlation_id,
                    sequence=request.model_version.sequence,
                    subject=customers_v1_refs_pb2.CustomerRef(customer_id=request.model_version.subject.customer_id)
                )
            )
            document_0 = MessageToDict(outgoing_0, preserving_proto_field_name=True)
            outgoing_0 = ParseDict(
                document_0,
                modelregistry_v1_model_version_calculation_service_pb2.EstimateModelVersionRequest()
            )
            response_0 = await deps.clients.modelregistry_model_version_calculation.EstimateModelVersion(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = modelregistry_v1_deployment_calculation_service_pb2.CalculateDeploymentRequest(
                context=request.context,
                deployment=modelregistry_v1_modelregistry_pb2.Deployment(
                    organizer=identity_v1_refs_pb2.UserRef(display_name=request.model_version.subject.display_name),
                    participants=[
                        modelregistry_v1_modelregistry_pb2.DeploymentParticipant(
                            contact=common_v1_contact_pb2.ContactInfo(email=response_0.model_version.subject.email)
                        )
                    ]
                )
            )
            document_1 = MessageToJson(outgoing_1, preserving_proto_field_name=True)
            outgoing_1 = Parse(
                document_1,
                modelregistry_v1_deployment_calculation_service_pb2.CalculateDeploymentRequest()
            )
            response_1 = await deps.clients.modelregistry_deployment_calculation.CalculateDeployment(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.correlation_id
            if returned_0_0:
                response.result.correlation_id = returned_0_0
            returned_0_1 = response_0.model_version.sequence
            if returned_0_1:
                response.model_version.sequence = returned_0_1
            returned_1_0 = response_1.deployment.organizer.email
            if returned_1_0:
                response.model_version.subject.email = returned_1_0
            echoed_0 = request.model_version_id
            response.model_version.model_version_id = echoed_0
            echoed_1 = request.model_version.kind
            response.model_version.kind = echoed_1
            return response

    async def handle_resolve_model_version_conflict(
        self,
        request: modelregistry_v1_model_version_sync_service_pb2.ResolveModelVersionConflictRequest
    ) -> modelregistry_v1_model_version_sync_service_pb2.ResolveModelVersionConflictResponse:
        """Resolves a model version."""
        deps = self.deps
        response = modelregistry_v1_model_version_sync_service_pb2.ResolveModelVersionConflictResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ResolveModelVersionConflict', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ResolveModelVersionConflict',
                {'reason': request.reason}
            )
            await deps.repository.save_model_version(request.context.tenant_id, request.model_version)
            response_0 = customers_v1_household_calculation_service_pb2.QuoteHouseholdResponse()
            response_1 = identity_v1_user_query_service_pb2.ExportUsersResponse()
            callbacks_0: list[
                Callable[[], Awaitable[customers_v1_household_calculation_service_pb2.QuoteHouseholdResponse]]
            ] = []
            for item_0 in request.model_version.measurements:
                outgoing_0 = customers_v1_household_calculation_service_pb2.QuoteHouseholdRequest(
                    context=request.context,
                    household=customers_v1_customers_pb2.Household(
                        children=[
                            customers_v1_customers_pb2.Household(
                                children=[
                                    customers_v1_customers_pb2.Household(
                                        attributes=dict(request.model_version.attributes),
                                        audit=common_v1_audit_pb2.AuditInfo(updated_at=item_0.observed_at)
                                    )
                                ]
                            )
                        ]
                    )
                )
                async def send_0(
                    payload: customers_v1_household_calculation_service_pb2.QuoteHouseholdRequest = outgoing_0
                ) -> customers_v1_household_calculation_service_pb2.QuoteHouseholdResponse:
                    return await deps.clients.customers_household_calculation.QuoteHousehold(
                        payload,
                        timeout=deps.settings.timeout
                    )
                callbacks_0.append(send_0)
            for callback_0 in callbacks_0:
                response_0 = await callback_0()
            outgoing_1 = identity_v1_user_query_service_pb2.ExportUsersRequest(
                context=request.context,
                filter=identity_v1_user_query_service_pb2.ExportUsersRequest.Filter(
                    region=response_0.household.location.region
                )
            )
            async for chunk_1 in deps.clients.identity_user_query.ExportUsers(
                outgoing_1,
                timeout=deps.settings.timeout
            ):
                response_1 = chunk_1
            echoed_0 = request.model_version_id
            response.model_version.model_version_id = echoed_0
            echoed_1 = request.model_version.source
            response.model_version.source = echoed_1
            return response

    async def handle_stream_model_version_changes(
        self,
        request: modelregistry_v1_model_version_sync_service_pb2.StreamModelVersionChangesRequest
    ) -> modelregistry_v1_model_version_sync_service_pb2.StreamModelVersionChangesResponse:
        """Exchanges changes of model versions with a peer."""
        deps = self.deps
        response = modelregistry_v1_model_version_sync_service_pb2.StreamModelVersionChangesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('StreamModelVersionChanges', extra={'fields': {'cursor': request.cursor}})
            await deps.repository.audit(
                request.context.tenant_id,
                'StreamModelVersionChanges',
                {'cursor': request.cursor}
            )
            if request.WhichOneof('frame') == 'change':
                await deps.repository.save_model_version(request.context.tenant_id, request.change)
            response_0 = modelregistry_v1_deployment_import_service_pb2.RetryDeploymentImportResponse()
            response_1 = featurestore_v1_entity_sync_service_pb2.PushEntityResponse()
            response_2 = modelregistry_v1_registered_model_query_service_pb2.CountRegisteredModelsResponse()
            response_3 = notifications_v1_notification_service_pb2.BatchGetNotificationsResponse()
            outgoing_0 = modelregistry_v1_deployment_import_service_pb2.RetryDeploymentImportRequest(
                context=request.context,
                details=modelregistry_v1_deployment_import_service_pb2.RetryDeploymentImportRequest.Details(
                    notify=common_v1_contact_pb2.ContactInfo(email=request.change.subject.email)
                )
            )
            outgoing_3 = notifications_v1_notification_service_pb2.BatchGetNotificationsRequest(context=request.context)
            response_0, response_3 = await asyncio.gather(
                deps.clients.modelregistry_deployment_import.RetryDeploymentImport(
                    outgoing_0,
                    timeout=deps.settings.timeout
                ),
                deps.clients.notifications_notification.BatchGetNotifications(
                    outgoing_3,
                    timeout=deps.settings.timeout
                ),
            )
            command_1 = ModelVersionSyncStreamModelVersionChanges1Command(
                context=request.context,
                entity_primary_address_recipient=response_0.deployment.location.recipient
            )
            outgoing_1 = to_model_version_sync_stream_model_version_changes1_command(command_1)
            response_1 = await deps.clients.featurestore_entity_sync.PushEntity(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            command_2 = ModelVersionSyncStreamModelVersionChanges2Command.model_validate(
                {'context': request.context, 'filter_region': response_1.entity.primary_address.region}
            )
            outgoing_2 = to_model_version_sync_stream_model_version_changes2_command(command_2)
            response_2 = await deps.clients.modelregistry_registered_model_query.CountRegisteredModels(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.details
            response.result.details.update(returned_0_0)
            returned_0_1 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_1)
            returned_1_0 = response_1.outcome.status
            if returned_1_0:
                response.result.status = returned_1_0
            returned_2_0 = response_2.result.correlation_id
            if returned_2_0:
                response.result.correlation_id = returned_2_0
            returned_3_0 = response_3.result.message
            if returned_3_0:
                response.result.message = returned_3_0
            returned_3_1 = response_3.result.correlation_id
            if returned_3_1:
                response.result.correlation_id = returned_3_1
            echoed_0 = request.change.kind
            response.model_version.kind = echoed_0
            echoed_1 = request.change.source
            response.model_version.source = echoed_1
            return response

    async def handle_sync_model_versions(
        self,
        request: modelregistry_v1_model_version_sync_service_pb2.SyncModelVersionsRequest
    ) -> modelregistry_v1_model_version_sync_service_pb2.SyncModelVersionsResponse:
        """Syncs a model version."""
        deps = self.deps
        response = modelregistry_v1_model_version_sync_service_pb2.SyncModelVersionsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SyncModelVersions', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'SyncModelVersions', {'reason': request.reason})
            await deps.repository.save_model_version(request.context.tenant_id, request.model_version)
            response_0 = modelregistry_v1_registered_model_query_service_pb2.ResolveRegisteredModelsResponse()
            response_1 = modelregistry_v1_deployment_validation_service_pb2.PreviewDeploymentResponse()
            response_2 = ledger_v1_ledger_account_query_service_pb2.ResolveLedgerAccountsResponse()
            response_3 = modelregistry_v1_model_version_validation_service_pb2.LintModelVersionsResponse()
            outgoing_0 = modelregistry_v1_registered_model_query_service_pb2.ResolveRegisteredModelsRequest(
                context=request.context
            )
            response_0 = await hooks.model_version_sync_sync_model_versions0(
                deps.clients.modelregistry_registered_model_query,
                outgoing_0,
                deps.settings.timeout
            )
            async for item_1 in async_messages(request.model_version.measurements):
                outgoing_1 = modelregistry_v1_deployment_validation_service_pb2.PreviewDeploymentRequest(
                    context=request.context,
                    deployment=modelregistry_v1_modelregistry_pb2.Deployment(
                        audit=common_v1_audit_pb2.AuditInfo(created_at=item_1.observed_at),
                        organizer=identity_v1_refs_pb2.UserRef(
                            display_name=request.model_version.subject.display_name,
                            email=request.model_version.subject.email,
                            user_id=request.context.actor.user_id
                        )
                    )
                )
                response_1 = await deps.clients.modelregistry_deployment_validation.PreviewDeployment(
                    outgoing_1,
                    timeout=deps.settings.timeout
                )
            outgoing_2 = ledger_v1_ledger_account_query_service_pb2.ResolveLedgerAccountsRequest(
                context=request.context
            )
            port_2: ModelVersionSyncSyncModelVersions2Port = ModelVersionSyncSyncModelVersions2Adapter(
                deps.clients.ledger_ledger_account_query,
                deps.settings.timeout
            )
            response_2 = await port_2.execute(outgoing_2)
            outgoing_3 = modelregistry_v1_model_version_validation_service_pb2.LintModelVersionsRequest(
                context=request.context,
                details=modelregistry_v1_model_version_validation_service_pb2.LintModelVersionsRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(email=request.model_version.subject.email)
                ),
                model_version=modelregistry_v1_modelregistry_pb2.ModelVersion(
                    correlation_id=response_0.result.correlation_id,
                    subject=customers_v1_refs_pb2.CustomerRef(
                        display_name=request.model_version.subject.display_name,
                        email=response_1.deployment.organizer.email
                    )
                )
            )
            steps_3 = [
                partial(
                    deps.clients.modelregistry_model_version_validation.LintModelVersions,
                    outgoing_3,
                    timeout=deps.settings.timeout
                )
            ]
            results_3 = await run_steps(steps_3)
            response_3 = results_3[-1]
            returned_0_0 = response_0.result.status
            if returned_0_0:
                response.result.status = returned_0_0
            returned_2_0 = response_2.result.message
            if returned_2_0:
                response.outcome.message = returned_2_0
            returned_2_1 = response_2.result.details
            response.result.details.update(returned_2_1)
            returned_3_0 = response_3.result.status
            if returned_3_0:
                response.result.status = returned_3_0
            returned_3_1 = response_3.result.message
            if returned_3_1:
                response.outcome.message = returned_3_1
            echoed_0 = request.model_version_id
            response.model_version.model_version_id = echoed_0
            echoed_1 = request.model_version.correlation_id
            response.result.correlation_id = echoed_1
            return response
