"""Reusable transport mixin for DeploymentLifecycleService."""

from __future__ import annotations

from collections.abc import AsyncIterator
from functools import partial
from typing import cast
import asyncio
import logging

from google.protobuf.json_format import MessageToDict
from google.protobuf.json_format import ParseDict
import grpc

from acme.anomalies.v1 import anomaly_approval_service_pb2 as anomalies_v1_anomaly_approval_service_pb2
from acme.cart.v1 import cart_query_service_pb2 as cart_v1_cart_query_service_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.customers.v1 import customers_pb2 as customers_v1_customers_pb2
from acme.customers.v1 import household_calculation_service_pb2 as customers_v1_household_calculation_service_pb2
from acme.customers.v1 import preference_calculation_service_pb2 as customers_v1_preference_calculation_service_pb2
from acme.featurestore.v1 import entity_approval_service_pb2 as featurestore_v1_entity_approval_service_pb2
from acme.featurestore.v1 import feature_view_sync_service_pb2 as featurestore_v1_feature_view_sync_service_pb2
from acme.featurestore.v1 import featurestore_pb2 as featurestore_v1_featurestore_pb2
from acme.identity.v1 import identity_pb2 as identity_v1_identity_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.identity.v1 import user_service_pb2 as identity_v1_user_service_pb2
from acme.ledger.v1 import ledger_account_query_service_pb2 as ledger_v1_ledger_account_query_service_pb2
from acme.lineage.v1 import lineage_node_approval_service_pb2 as lineage_v1_lineage_node_approval_service_pb2
from acme.metrics.v1 import dashboard_sync_service_pb2 as metrics_v1_dashboard_sync_service_pb2
from acme.modelregistry.v1 import (
    deployment_calculation_service_pb2 as modelregistry_v1_deployment_calculation_service_pb2,
)
from acme.modelregistry.v1 import deployment_import_service_pb2 as modelregistry_v1_deployment_import_service_pb2
from acme.modelregistry.v1 import deployment_lifecycle_service_pb2 as modelregistry_v1_deployment_lifecycle_service_pb2
from acme.modelregistry.v1 import modelregistry_pb2 as modelregistry_v1_modelregistry_pb2
from acme.modelregistry.v1 import (
    registered_model_sync_service_pb2 as modelregistry_v1_registered_model_sync_service_pb2,
)

from acme_data.domains.modelregistry import hooks
from acme_data.domains.modelregistry.adapters import DeploymentLifecycleRenewDeployment0Adapter
from acme_data.domains.modelregistry.adapters import DeploymentLifecycleRenewDeployment0Port
from acme_data.domains.modelregistry.adapters import DeploymentLifecycleScheduleDeploymentExpiry0Adapter
from acme_data.domains.modelregistry.dependencies import Dependencies
from acme_data.domains.modelregistry.models import DeploymentLifecycleExpireDeployment3Command
from acme_data.domains.modelregistry.models import DeploymentLifecycleReinstateDeployment0Command
from acme_data.domains.modelregistry.models import to_deployment_lifecycle_expire_deployment3_command
from acme_data.domains.modelregistry.models import to_deployment_lifecycle_reinstate_deployment0_command
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import run_steps
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_id
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class DeploymentLifecycleServicerHandlers:
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    async def ActivateDeployment(
        self, request: modelregistry_v1_deployment_lifecycle_service_pb2.ActivateDeploymentRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_deployment_lifecycle_service_pb2.ActivateDeploymentResponse:
        """Activates a deployment."""
        return await self.handle_activate_deployment(request)

    @rpc_errors
    async def ExpireDeployment(
        self, request: modelregistry_v1_deployment_lifecycle_service_pb2.ExpireDeploymentRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_deployment_lifecycle_service_pb2.ExpireDeploymentResponse:
        """Expires a deployment."""
        return await self.handle_expire_deployment(request)

    @rpc_errors
    @retry_transient
    async def GetDeploymentLifecycle(
        self, request: modelregistry_v1_deployment_lifecycle_service_pb2.GetDeploymentLifecycleRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_deployment_lifecycle_service_pb2.GetDeploymentLifecycleResponse:
        """Returns a deployment."""
        return await self.handle_get_deployment_lifecycle(request)

    @rpc_errors
    async def ReinstateDeployment(
        self, request: modelregistry_v1_deployment_lifecycle_service_pb2.ReinstateDeploymentRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_deployment_lifecycle_service_pb2.ReinstateDeploymentResponse:
        """Reinstates a deployment."""
        return await self.handle_reinstate_deployment(request)

    @rpc_errors
    async def RenewDeployment(
        self, request: modelregistry_v1_deployment_lifecycle_service_pb2.RenewDeploymentRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_deployment_lifecycle_service_pb2.RenewDeploymentResponse:
        """Renews a deployment."""
        return await self.handle_renew_deployment(request)

    @rpc_errors
    async def ScheduleDeploymentExpiry(
        self, request: modelregistry_v1_deployment_lifecycle_service_pb2.ScheduleDeploymentExpiryRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_deployment_lifecycle_service_pb2.ScheduleDeploymentExpiryResponse:
        """Schedules a deployment."""
        return await self.handle_schedule_deployment_expiry(request)

    @rpc_errors
    async def SuspendDeployment(
        self, request: modelregistry_v1_deployment_lifecycle_service_pb2.SuspendDeploymentRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_deployment_lifecycle_service_pb2.SuspendDeploymentResponse:
        """Suspends a deployment."""
        return await self.handle_suspend_deployment(request)

    @rpc_errors
    async def TerminateDeployment(
        self, request: modelregistry_v1_deployment_lifecycle_service_pb2.TerminateDeploymentRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_deployment_lifecycle_service_pb2.TerminateDeploymentResponse:
        """Terminates a deployment."""
        return await self.handle_terminate_deployment(request)

    async def handle_activate_deployment(
        self,
        request: modelregistry_v1_deployment_lifecycle_service_pb2.ActivateDeploymentRequest
    ) -> modelregistry_v1_deployment_lifecycle_service_pb2.ActivateDeploymentResponse:
        """Activates a deployment."""
        deps = self.deps
        response = modelregistry_v1_deployment_lifecycle_service_pb2.ActivateDeploymentResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ActivateDeployment', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'ActivateDeployment', {'reason': request.reason})
            response_0 = modelregistry_v1_registered_model_sync_service_pb2.ReconcileRegisteredModelsResponse()
            response_1 = customers_v1_household_calculation_service_pb2.QuoteHouseholdResponse()
            outgoing_0 = modelregistry_v1_registered_model_sync_service_pb2.ReconcileRegisteredModelsRequest(
                context=request.context,
                registered_model=modelregistry_v1_modelregistry_pb2.RegisteredModel(
                    owner=identity_v1_refs_pb2.UserRef(
                        display_name=request.details.new_owner.display_name,
                        email=request.details.notify_contact.email
                    )
                )
            )
            document_0 = MessageToDict(outgoing_0, preserving_proto_field_name=True)
            outgoing_0 = ParseDict(
                document_0,
                modelregistry_v1_registered_model_sync_service_pb2.ReconcileRegisteredModelsRequest()
            )
            response_0 = await deps.clients.modelregistry_registered_model_sync.ReconcileRegisteredModels(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = customers_v1_household_calculation_service_pb2.QuoteHouseholdRequest()
            outgoing_1.context.CopyFrom(request.context)
            if response_0.registered_model.WhichOneof('locator') == 'address':
                field_1_1_part_1 = outgoing_1.household.children.add()
                field_1_1_part_2 = field_1_1_part_1.children.add()
                field_1_1_part_2.location.postal_code = response_0.registered_model.address.postal_code
            response_1 = await deps.clients.customers_household_calculation.QuoteHousehold(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.registered_model.audit.created_at
            if returned_0_0.ListFields():
                response.deployment.audit.created_at.MergeFrom(returned_0_0)
            returned_1_0 = response_1.result.reference_ids
            response.result.reference_ids.extend(returned_1_0)
            echoed_0 = request.deployment_id
            response.deployment.deployment_id = echoed_0
            echoed_1 = request.details.effective_at
            response.outcome.effective_at.CopyFrom(echoed_1)
            return response

    async def handle_expire_deployment(
        self,
        request: modelregistry_v1_deployment_lifecycle_service_pb2.ExpireDeploymentRequest
    ) -> modelregistry_v1_deployment_lifecycle_service_pb2.ExpireDeploymentResponse:
        """Expires a deployment."""
        deps = self.deps
        response = modelregistry_v1_deployment_lifecycle_service_pb2.ExpireDeploymentResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ExpireDeployment', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'ExpireDeployment', {'reason': request.reason})
            response_0 = cart_v1_cart_query_service_pb2.BrowseCartsResponse()
            response_1 = identity_v1_user_service_pb2.CloneUserResponse()
            response_2 = featurestore_v1_entity_approval_service_pb2.ApproveEntityResponse()
            response_3 = modelregistry_v1_registered_model_sync_service_pb2.PushRegisteredModelResponse()
            outgoing_0 = cart_v1_cart_query_service_pb2.BrowseCartsRequest(
                context=request.context,
                filter=cart_v1_cart_query_service_pb2.BrowseCartsRequest.Filter(
                    created_after=request.details.effective_at,
                    owner_id=request.details.new_owner.user_id
                )
            )
            outgoing_1 = identity_v1_user_service_pb2.CloneUserRequest(
                context=request.context,
                user=identity_v1_identity_pb2.User(
                    contact=common_v1_contact_pb2.ContactInfo(phone=request.details.notify_contact.phone)
                )
            )
            outgoing_2 = featurestore_v1_entity_approval_service_pb2.ApproveEntityRequest(
                context=request.context,
                entity=featurestore_v1_featurestore_pb2.Entity(
                    relationship_manager=identity_v1_refs_pb2.UserRef(email=request.details.new_owner.email)
                )
            )
            response_0, response_1, response_2 = await asyncio.gather(
                deps.clients.cart_cart_query.BrowseCarts(outgoing_0, timeout=deps.settings.timeout),
                deps.clients.identity_user.CloneUser(outgoing_1, timeout=deps.settings.timeout),
                deps.clients.featurestore_entity_approval.ApproveEntity(outgoing_2, timeout=deps.settings.timeout),
            )
            command_3 = DeploymentLifecycleExpireDeployment3Command(
                context=request.context,
                registered_model_audit_updated_by=response_2.entity.audit.updated_by,
                registered_model_address_locality=response_1.user.primary_address.locality
            )
            outgoing_3 = to_deployment_lifecycle_expire_deployment3_command(command_3)
            response_3 = await deps.clients.modelregistry_registered_model_sync.PushRegisteredModel(
                outgoing_3,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.status
            if returned_0_0:
                response.outcome.status = returned_0_0
            returned_0_1 = response_0.result.message
            if returned_0_1:
                response.result.message = returned_0_1
            returned_1_0 = response_1.user.relationship_manager.email
            returned_1_0_part_1 = response.deployment.participants.add()
            if returned_1_0:
                returned_1_0_part_1.contact.email = returned_1_0
            returned_2_0 = response_2.entity.name
            returned_2_0_part_1 = response.deployment.participants.add()
            if returned_2_0.ListFields():
                returned_2_0_part_1.contact.name.MergeFrom(returned_2_0)
            returned_2_1 = response_2.entity.relationship_manager.user_id
            if returned_2_1:
                response.deployment.organizer.user_id = returned_2_1
            returned_3_0 = response_3.registered_model.owner.user_id
            if returned_3_0:
                response.deployment.organizer.user_id = returned_3_0
            returned_3_1 = response_3.registered_model.address.lines
            response.deployment.location.lines.extend(returned_3_1)
            echoed_0 = request.deployment_id
            response.deployment.deployment_id = echoed_0
            echoed_1 = request.details.effective_at
            response.outcome.effective_at.CopyFrom(echoed_1)
            return response

    async def handle_get_deployment_lifecycle(
        self,
        request: modelregistry_v1_deployment_lifecycle_service_pb2.GetDeploymentLifecycleRequest
    ) -> modelregistry_v1_deployment_lifecycle_service_pb2.GetDeploymentLifecycleResponse:
        """Returns a deployment."""
        deps = self.deps
        response = modelregistry_v1_deployment_lifecycle_service_pb2.GetDeploymentLifecycleResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('GetDeploymentLifecycle', extra={'fields': {'locale': request.context.locale}})
            await deps.repository.audit(
                request.context.tenant_id,
                'GetDeploymentLifecycle',
                {'locale': request.context.locale}
            )
            echoed_0 = request.deployment_id
            response.deployment.deployment_id = echoed_0
            return response

    async def handle_reinstate_deployment(
        self,
        request: modelregistry_v1_deployment_lifecycle_service_pb2.ReinstateDeploymentRequest
    ) -> modelregistry_v1_deployment_lifecycle_service_pb2.ReinstateDeploymentResponse:
        """Reinstates a deployment."""
        deps = self.deps
        response = modelregistry_v1_deployment_lifecycle_service_pb2.ReinstateDeploymentResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ReinstateDeployment', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'ReinstateDeployment', {'reason': request.reason})
            response_0 = lineage_v1_lineage_node_approval_service_pb2.DelegateLineageNodeApprovalResponse()
            response_1 = customers_v1_household_calculation_service_pb2.CalculateHouseholdResponse()
            response_2 = anomalies_v1_anomaly_approval_service_pb2.RejectAnomalyResponse()
            response_3 = metrics_v1_dashboard_sync_service_pb2.ListDashboardConflictsResponse()
            command_0 = DeploymentLifecycleReinstateDeployment0Command.model_validate(
                {
                    'context': request.context,
                    'lineage_node_children_children_manager_email': request.details.new_owner.email,
                    'details_approver_display_name': request.details.new_owner.display_name,
                    'lineage_node_children_manager_user_id': request.details.new_owner.user_id,
                    'details_approver_email': request.details.notify_contact.email
                }
            )
            outgoing_0 = to_deployment_lifecycle_reinstate_deployment0_command(command_0)
            response_0 = await deps.clients.lineage_lineage_node_approval.DelegateLineageNodeApproval(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = customers_v1_household_calculation_service_pb2.CalculateHouseholdRequest(
                context=request.context,
                household=customers_v1_customers_pb2.Household(
                    children=[
                        customers_v1_customers_pb2.Household(
                            children=[
                                customers_v1_customers_pb2.Household(
                                    manager=identity_v1_refs_pb2.UserRef(email=request.details.new_owner.email)
                                )
                            ]
                        )
                    ]
                )
            )
            send_1 = partial(
                deps.clients.customers_household_calculation.CalculateHousehold,
                timeout=deps.settings.timeout
            )
            response_1 = await send_1(outgoing_1)
            outgoing_2 = anomalies_v1_anomaly_approval_service_pb2.RejectAnomalyRequest(
                context=request.context,
                details=anomalies_v1_anomaly_approval_service_pb2.RejectAnomalyRequest.Details(
                    approver=identity_v1_refs_pb2.UserRef(user_id=request.details.new_owner.user_id)
                )
            )
            response_2 = await hooks.deployment_lifecycle_reinstate_deployment2(
                deps.clients.anomalies_anomaly_approval,
                outgoing_2,
                deps.settings.timeout
            )
            outgoing_3 = metrics_v1_dashboard_sync_service_pb2.ListDashboardConflictsRequest()
            outgoing_3.context.CopyFrom(request.context)
            outgoing_3.filter.region = response_1.household.location.region
            outgoing_3.filter.created_after.CopyFrom(response_2.anomaly.sla.due_at)
            outgoing_3.filter.owner_id = response_1.household.manager.user_id
            outgoing_3.context.tenant_id = tenant_id.get()
            response_3 = await deps.clients.metrics_dashboard_sync.ListDashboardConflicts(
                outgoing_3,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.lineage_node.audit.updated_at
            if returned_0_0.ListFields():
                response.deployment.audit.updated_at.MergeFrom(returned_0_0)
            returned_0_1 = response_0.lineage_node.location.lines
            response.deployment.location.lines.extend(returned_0_1)
            returned_1_0 = response_1.household.location.postal_code
            if returned_1_0:
                response.deployment.location.postal_code = returned_1_0
            returned_2_0 = response_2.result.reference_ids
            response.result.reference_ids.extend(returned_2_0)
            returned_3_0 = response_3.result.message
            if returned_3_0:
                response.result.message = returned_3_0
            returned_3_1 = response_3.result.details
            response.result.details.update(returned_3_1)
            echoed_0 = request.deployment_id
            response.deployment.deployment_id = echoed_0
            echoed_1 = request.details.effective_at
            response.outcome.effective_at.CopyFrom(echoed_1)
            return response

    async def handle_renew_deployment(
        self,
        request: modelregistry_v1_deployment_lifecycle_service_pb2.RenewDeploymentRequest
    ) -> modelregistry_v1_deployment_lifecycle_service_pb2.RenewDeploymentResponse:
        """Renews a deployment."""
        deps = self.deps
        response = modelregistry_v1_deployment_lifecycle_service_pb2.RenewDeploymentResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('RenewDeployment', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'RenewDeployment', {'reason': request.reason})
            response_0 = modelregistry_v1_deployment_import_service_pb2.RetryDeploymentImportResponse()
            response_1 = customers_v1_preference_calculation_service_pb2.SimulatePreferenceResponse()
            outgoing_0 = modelregistry_v1_deployment_import_service_pb2.RetryDeploymentImportRequest(
                context=request.context,
                deployment=modelregistry_v1_modelregistry_pb2.Deployment(
                    organizer=identity_v1_refs_pb2.UserRef(
                        display_name=request.details.new_owner.display_name,
                        email=request.details.new_owner.email
                    ),
                    participants=[
                        modelregistry_v1_modelregistry_pb2.DeploymentParticipant(
                            contact=common_v1_contact_pb2.ContactInfo(name=request.details.notify_contact.name)
                        )
                    ]
                ),
                details=modelregistry_v1_deployment_import_service_pb2.RetryDeploymentImportRequest.Details(
                    notify=common_v1_contact_pb2.ContactInfo(
                        preferred_channel=request.details.notify_contact.preferred_channel
                    )
                )
            )
            port_0: DeploymentLifecycleRenewDeployment0Port = DeploymentLifecycleRenewDeployment0Adapter(
                deps.clients.modelregistry_deployment_import,
                deps.settings.timeout
            )
            response_0 = await port_0.execute(outgoing_0)
            outgoing_1 = customers_v1_preference_calculation_service_pb2.SimulatePreferenceRequest(
                context=request.context,
                preference=customers_v1_customers_pb2.Preference(
                    audit=common_v1_audit_pb2.AuditInfo(created_by=response_0.deployment.audit.created_by)
                )
            )
            steps_1 = [
                partial(
                    deps.clients.customers_preference_calculation.SimulatePreference,
                    outgoing_1,
                    timeout=deps.settings.timeout
                )
            ]
            results_1 = await run_steps(steps_1)
            response_1 = results_1[-1]
            returned_0_0 = response_0.deployment.location.locality
            if returned_0_0:
                response.deployment.location.locality = returned_0_0
            returned_1_0 = response_1.result.message
            if returned_1_0:
                response.outcome.message = returned_1_0
            echoed_0 = request.deployment_id
            response.deployment.deployment_id = echoed_0
            echoed_1 = request.details.effective_at
            response.outcome.effective_at.CopyFrom(echoed_1)
            return response

    async def handle_schedule_deployment_expiry(
        self,
        request: modelregistry_v1_deployment_lifecycle_service_pb2.ScheduleDeploymentExpiryRequest
    ) -> modelregistry_v1_deployment_lifecycle_service_pb2.ScheduleDeploymentExpiryResponse:
        """Schedules a deployment."""
        deps = self.deps
        response = modelregistry_v1_deployment_lifecycle_service_pb2.ScheduleDeploymentExpiryResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ScheduleDeploymentExpiry', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ScheduleDeploymentExpiry',
                {'reason': request.reason}
            )
            await deps.repository.save_deployment(request.context.tenant_id, request.deployment)
            response_0 = ledger_v1_ledger_account_query_service_pb2.SuggestLedgerAccountsResponse()
            outgoing_0 = ledger_v1_ledger_account_query_service_pb2.SuggestLedgerAccountsRequest(
                context=request.context,
                filter=ledger_v1_ledger_account_query_service_pb2.SuggestLedgerAccountsRequest.Filter(
                    created_after=request.deployment.audit.created_at,
                    labels=dict(request.details.parameters),
                    region=request.deployment.location.region
                )
            )
            response_0 = await DeploymentLifecycleScheduleDeploymentExpiry0Adapter(
                deps.clients.ledger_ledger_account_query,
                deps.settings.timeout
            )(outgoing_0)
            returned_0_0 = response_0.result.details
            response.result.details.update(returned_0_0)
            echoed_0 = request.deployment_id
            response.deployment.deployment_id = echoed_0
            echoed_1 = request.deployment.title
            response.deployment.title = echoed_1
            return response

    async def handle_suspend_deployment(
        self,
        request: modelregistry_v1_deployment_lifecycle_service_pb2.SuspendDeploymentRequest
    ) -> modelregistry_v1_deployment_lifecycle_service_pb2.SuspendDeploymentResponse:
        """Suspends a deployment."""
        deps = self.deps
        response = modelregistry_v1_deployment_lifecycle_service_pb2.SuspendDeploymentResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SuspendDeployment', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'SuspendDeployment', {'reason': request.reason})
            response_0 = modelregistry_v1_deployment_import_service_pb2.RetryDeploymentImportResponse()
            response_1 = featurestore_v1_feature_view_sync_service_pb2.ListFeatureViewConflictsResponse()
            outgoing_0 = modelregistry_v1_deployment_import_service_pb2.RetryDeploymentImportRequest(
                context=request.context,
                deployment=modelregistry_v1_modelregistry_pb2.Deployment(
                    participants=[
                        modelregistry_v1_modelregistry_pb2.DeploymentParticipant(
                            contact=common_v1_contact_pb2.ContactInfo(email=request.details.new_owner.email)
                        )
                    ]
                )
            )
            response_0 = cast(modelregistry_v1_deployment_import_service_pb2.RetryDeploymentImportResponse, await deps.bus.request(
                'acme.modelregistry.v1.DeploymentLifecycleService/SuspendDeployment/0', outgoing_0, deps.settings.timeout,
            ))
            outgoing_1 = featurestore_v1_feature_view_sync_service_pb2.ListFeatureViewConflictsRequest(
                context=request.context,
                filter=featurestore_v1_feature_view_sync_service_pb2.ListFeatureViewConflictsRequest.Filter(
                    created_after=response_0.deployment.audit.updated_at,
                    labels=dict(response_0.result.details),
                    region=response_0.deployment.location.region
                )
            )
            response_1 = await deps.clients.featurestore_feature_view_sync.ListFeatureViewConflicts(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.deployment.audit.etag
            if returned_0_0:
                response.deployment.audit.etag = returned_0_0
            returned_0_1 = response_0.deployment.status
            if returned_0_1:
                response.deployment.status = returned_0_1
            returned_1_0 = response_1.result.message
            if returned_1_0:
                response.outcome.message = returned_1_0
            echoed_0 = request.deployment_id
            response.deployment.deployment_id = echoed_0
            echoed_1 = request.details.effective_at
            response.outcome.effective_at.CopyFrom(echoed_1)
            return response

    async def handle_terminate_deployment(
        self,
        request: modelregistry_v1_deployment_lifecycle_service_pb2.TerminateDeploymentRequest
    ) -> modelregistry_v1_deployment_lifecycle_service_pb2.TerminateDeploymentResponse:
        """Terminates a deployment."""
        deps = self.deps
        response = modelregistry_v1_deployment_lifecycle_service_pb2.TerminateDeploymentResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('TerminateDeployment', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'TerminateDeployment', {'reason': request.reason})
            response_0 = lineage_v1_lineage_node_approval_service_pb2.ListPendingLineageNodesResponse()
            response_1 = modelregistry_v1_deployment_calculation_service_pb2.CalculateDeploymentResponse()
            outgoing_0 = lineage_v1_lineage_node_approval_service_pb2.ListPendingLineageNodesRequest(
                context=request.context,
                filter=lineage_v1_lineage_node_approval_service_pb2.ListPendingLineageNodesRequest.Filter(
                    created_after=request.details.effective_at,
                    owner_id=request.details.new_owner.user_id
                )
            )
            outgoing_1 = modelregistry_v1_deployment_calculation_service_pb2.CalculateDeploymentRequest(
                context=request.context,
                deployment=modelregistry_v1_modelregistry_pb2.Deployment(
                    organizer=identity_v1_refs_pb2.UserRef(user_id=request.details.new_owner.user_id),
                    participants=[
                        modelregistry_v1_modelregistry_pb2.DeploymentParticipant(
                            contact=common_v1_contact_pb2.ContactInfo(
                                email=request.details.new_owner.email,
                                phone=request.details.notify_contact.phone,
                                preferred_channel=request.details.notify_contact.preferred_channel
                            )
                        )
                    ]
                )
            )
            response_0, response_1 = await asyncio.gather(
                deps.clients.lineage_lineage_node_approval.ListPendingLineageNodes(
                    outgoing_0,
                    timeout=deps.settings.timeout
                ),
                deps.clients.modelregistry_deployment_calculation.CalculateDeployment(
                    outgoing_1,
                    timeout=deps.settings.timeout
                ),
            )
            returned_0_0 = response_0.result.details
            response.result.details.update(returned_0_0)
            returned_0_1 = response_0.result.message
            if returned_0_1:
                response.outcome.message = returned_0_1
            returned_1_0 = response_1.deployment.location.lines
            response.deployment.location.lines.extend(returned_1_0)
            returned_1_1 = response_1.deployment.audit.updated_by
            if returned_1_1:
                response.deployment.audit.updated_by = returned_1_1
            echoed_0 = request.deployment_id
            response.deployment.deployment_id = echoed_0
            echoed_1 = request.details.effective_at
            response.outcome.effective_at.CopyFrom(echoed_1)
            return response
