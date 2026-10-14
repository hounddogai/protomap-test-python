"""Functional operations behind RegisteredModelSyncService."""

from __future__ import annotations

import logging

from google.protobuf.json_format import MessageToJson
from google.protobuf.json_format import Parse

from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.community.v1 import forum_query_service_pb2 as community_v1_forum_query_service_pb2
from acme.customers.v1 import customer_validation_service_pb2 as customers_v1_customer_validation_service_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.lineage.v1 import impact_workflow_service_pb2 as lineage_v1_impact_workflow_service_pb2
from acme.lineage.v1 import lineage_edge_approval_service_pb2 as lineage_v1_lineage_edge_approval_service_pb2
from acme.lineage.v1 import lineage_node_sync_service_pb2 as lineage_v1_lineage_node_sync_service_pb2
from acme.lineage.v1 import lineage_pb2 as lineage_v1_lineage_pb2
from acme.modelregistry.v1 import (
    deployment_calculation_service_pb2 as modelregistry_v1_deployment_calculation_service_pb2,
)
from acme.modelregistry.v1 import (
    model_version_calculation_service_pb2 as modelregistry_v1_model_version_calculation_service_pb2,
)
from acme.modelregistry.v1 import modelregistry_pb2 as modelregistry_v1_modelregistry_pb2
from acme.modelregistry.v1 import (
    registered_model_query_service_pb2 as modelregistry_v1_registered_model_query_service_pb2,
)
from acme.modelregistry.v1 import registered_model_service_pb2 as modelregistry_v1_registered_model_service_pb2
from acme.modelregistry.v1 import (
    registered_model_sync_service_pb2 as modelregistry_v1_registered_model_sync_service_pb2,
)

from acme_data.domains.modelregistry.dependencies import Dependencies
from acme_data.domains.modelregistry.models import RegisteredModelSyncReconcileRegisteredModels1Command
from acme_data.domains.modelregistry.models import to_registered_model_sync_reconcile_registered_models1_command
from acme_data.platform.rpc import async_messages
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


async def handle_list_registered_model_conflicts(
    deps: Dependencies,
    request: modelregistry_v1_registered_model_sync_service_pb2.ListRegisteredModelConflictsRequest
) -> modelregistry_v1_registered_model_sync_service_pb2.ListRegisteredModelConflictsResponse:
    """Lists registered models a page at a time."""
    response = modelregistry_v1_registered_model_sync_service_pb2.ListRegisteredModelConflictsResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('ListRegisteredModelConflicts', extra={'fields': {'order_by': request.order_by}})
        await deps.repository.audit(
            request.context.tenant_id,
            'ListRegisteredModelConflicts',
            {'order_by': request.order_by}
        )
        response_0 = lineage_v1_lineage_edge_approval_service_pb2.CommentLineageEdgeApprovalResponse()
        outgoing_0 = lineage_v1_lineage_edge_approval_service_pb2.CommentLineageEdgeApprovalRequest(
            context=request.context,
            details=lineage_v1_lineage_edge_approval_service_pb2.CommentLineageEdgeApprovalRequest.Details(
                approver=identity_v1_refs_pb2.UserRef(
                    email=request.context.actor.email,
                    user_id=request.context.actor.user_id
                )
            )
        )
        response_0 = await deps.clients.lineage_lineage_edge_approval.CommentLineageEdgeApproval(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.result.reference_ids
        response.result.reference_ids.extend(returned_0_0)
        return response


async def handle_pull_registered_models(
    deps: Dependencies,
    request: modelregistry_v1_registered_model_sync_service_pb2.PullRegisteredModelsRequest
) -> modelregistry_v1_registered_model_sync_service_pb2.PullRegisteredModelsResponse:
    """Pulls a registered model."""
    response = modelregistry_v1_registered_model_sync_service_pb2.PullRegisteredModelsResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('PullRegisteredModels', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'PullRegisteredModels', {'reason': request.reason})
        await deps.repository.save_registered_model(request.context.tenant_id, request.registered_model)
        response_0 = modelregistry_v1_registered_model_service_pb2.UpdateRegisteredModelResponse()
        response_1 = lineage_v1_impact_workflow_service_pb2.PauseImpactWorkflowResponse()
        outgoing_0 = modelregistry_v1_registered_model_service_pb2.UpdateRegisteredModelRequest(
            context=request.context,
            registered_model=modelregistry_v1_modelregistry_pb2.RegisteredModel(
                audit=common_v1_audit_pb2.AuditInfo(
                    etag=request.registered_model.audit.etag,
                    updated_by=request.registered_model.audit.updated_by
                )
            )
        )
        response_0 = await deps.clients.modelregistry_registered_model.UpdateRegisteredModel(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = lineage_v1_impact_workflow_service_pb2.PauseImpactWorkflowRequest(
            context=request.context,
            impact=lineage_v1_lineage_pb2.Impact(
                assignee=identity_v1_refs_pb2.UserRef(email=request.registered_model.owner.email),
                audit=common_v1_audit_pb2.AuditInfo(etag=response_0.registered_model.audit.etag)
            )
        )
        document_1 = MessageToJson(outgoing_1, preserving_proto_field_name=True)
        outgoing_1 = Parse(document_1, lineage_v1_impact_workflow_service_pb2.PauseImpactWorkflowRequest())
        response_1 = await deps.clients.lineage_impact_workflow.PauseImpactWorkflow(
            outgoing_1,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.registered_model.dimensions.height
        if returned_0_0:
            response.registered_model.dimensions.height = returned_0_0
        returned_0_1 = response_0.registered_model.dimensions.width
        if returned_0_1:
            response.registered_model.dimensions.width = returned_0_1
        returned_1_0 = response_1.outcome.next_steps
        response.outcome.next_steps.extend(returned_1_0)
        returned_1_1 = response_1.result.reference_ids
        response.result.reference_ids.extend(returned_1_1)
        echoed_0 = request.registered_model_id
        response.registered_model.registered_model_id = echoed_0
        echoed_1 = request.registered_model.code
        response.registered_model.code = echoed_1
        return response


async def handle_push_registered_model(
    deps: Dependencies,
    request: modelregistry_v1_registered_model_sync_service_pb2.PushRegisteredModelRequest
) -> modelregistry_v1_registered_model_sync_service_pb2.PushRegisteredModelResponse:
    """Pushs a registered model."""
    response = modelregistry_v1_registered_model_sync_service_pb2.PushRegisteredModelResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('PushRegisteredModel', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'PushRegisteredModel', {'reason': request.reason})
        await deps.repository.save_registered_model(request.context.tenant_id, request.registered_model)
        response_0 = modelregistry_v1_registered_model_service_pb2.BatchGetRegisteredModelsResponse()
        response_1 = customers_v1_customer_validation_service_pb2.ExplainCustomerDecisionResponse()
        outgoing_0 = modelregistry_v1_registered_model_service_pb2.BatchGetRegisteredModelsRequest(
            context=request.context
        )
        response_0 = await deps.clients.modelregistry_registered_model.BatchGetRegisteredModels(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = customers_v1_customer_validation_service_pb2.ExplainCustomerDecisionRequest()
        outgoing_1.context.CopyFrom(request.context)
        if request.registered_model.WhichOneof('locator') == 'address':
            outgoing_1.customer.primary_address.recipient = request.registered_model.address.recipient
        outgoing_1.customer.audit.created_at.CopyFrom(request.registered_model.audit.created_at)
        outgoing_1.customer.audit.created_by = request.registered_model.audit.created_by
        response_1 = await deps.clients.customers_customer_validation.ExplainCustomerDecision(
            outgoing_1,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.result.correlation_id
        if returned_0_0:
            response.result.correlation_id = returned_0_0
        returned_0_1 = response_0.result.message
        if returned_0_1:
            response.result.message = returned_0_1
        returned_1_0 = response_1.customer.relationship_manager.user_id
        if returned_1_0:
            response.registered_model.owner.user_id = returned_1_0
        echoed_0 = request.registered_model_id
        response.registered_model.registered_model_id = echoed_0
        echoed_1 = request.registered_model.code
        response.registered_model.code = echoed_1
        return response


async def handle_reconcile_registered_models(
    deps: Dependencies,
    request: modelregistry_v1_registered_model_sync_service_pb2.ReconcileRegisteredModelsRequest
) -> modelregistry_v1_registered_model_sync_service_pb2.ReconcileRegisteredModelsResponse:
    """Reconciles a registered model."""
    response = modelregistry_v1_registered_model_sync_service_pb2.ReconcileRegisteredModelsResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('ReconcileRegisteredModels', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'ReconcileRegisteredModels', {'reason': request.reason})
        await deps.repository.save_registered_model(request.context.tenant_id, request.registered_model)
        response_0 = community_v1_forum_query_service_pb2.BrowseForumsResponse()
        response_1 = modelregistry_v1_deployment_calculation_service_pb2.CalculateDeploymentResponse()
        outgoing_0 = community_v1_forum_query_service_pb2.BrowseForumsRequest(
            context=request.context,
            filter=community_v1_forum_query_service_pb2.BrowseForumsRequest.Filter(
                region=request.registered_model.address.region
            )
        )
        response_0 = await deps.clients.community_forum_query.BrowseForums(outgoing_0, timeout=deps.settings.timeout)
        command_1 = RegisteredModelSyncReconcileRegisteredModels1Command(
            context=request.context,
            deployment_participants_contact_email=request.registered_model.owner.email,
            deployment_audit_created_at=request.registered_model.audit.created_at
        )
        outgoing_1 = to_registered_model_sync_reconcile_registered_models1_command(command_1)
        response_1 = await deps.clients.modelregistry_deployment_calculation.CalculateDeployment(
            outgoing_1,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.result.message
        if returned_0_0:
            response.result.message = returned_0_0
        returned_1_0 = response_1.result.message
        if returned_1_0:
            response.result.message = returned_1_0
        returned_1_1 = response_1.result.reference_ids
        response.result.reference_ids.extend(returned_1_1)
        echoed_0 = request.registered_model_id
        response.registered_model.registered_model_id = echoed_0
        echoed_1 = request.registered_model.status
        response.registered_model.status = echoed_1
        return response


async def handle_resolve_registered_model_conflict(
    deps: Dependencies,
    request: modelregistry_v1_registered_model_sync_service_pb2.ResolveRegisteredModelConflictRequest
) -> modelregistry_v1_registered_model_sync_service_pb2.ResolveRegisteredModelConflictResponse:
    """Resolves a registered model."""
    response = modelregistry_v1_registered_model_sync_service_pb2.ResolveRegisteredModelConflictResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('ResolveRegisteredModelConflict', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(
            request.context.tenant_id,
            'ResolveRegisteredModelConflict',
            {'reason': request.reason}
        )
        await deps.repository.save_registered_model(request.context.tenant_id, request.registered_model)
        response_0 = modelregistry_v1_registered_model_query_service_pb2.PeekRegisteredModelResponse()
        outgoing_0 = modelregistry_v1_registered_model_query_service_pb2.PeekRegisteredModelRequest(
            context=request.context,
            registered_model_id=request.registered_model.registered_model_id
        )
        response_0 = await deps.clients.modelregistry_registered_model_query.PeekRegisteredModel(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.registered_model.components.get(
            'primary',
            modelregistry_v1_modelregistry_pb2.RegisteredModelComponent()
        ).quantity
        if returned_0_0:
            response.registered_model.components['primary'].quantity = returned_0_0
        echoed_0 = request.registered_model_id
        response.registered_model.registered_model_id = echoed_0
        echoed_1 = request.registered_model.capacity
        response.registered_model.capacity = echoed_1
        return response


async def handle_stream_registered_model_changes(
    deps: Dependencies,
    request: modelregistry_v1_registered_model_sync_service_pb2.StreamRegisteredModelChangesRequest
) -> modelregistry_v1_registered_model_sync_service_pb2.StreamRegisteredModelChangesResponse:
    """Exchanges changes of registered models with a peer."""
    response = modelregistry_v1_registered_model_sync_service_pb2.StreamRegisteredModelChangesResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('StreamRegisteredModelChanges', extra={'fields': {'cursor': request.cursor}})
        await deps.repository.audit(
            request.context.tenant_id,
            'StreamRegisteredModelChanges',
            {'cursor': request.cursor}
        )
        if request.WhichOneof('frame') == 'change':
            await deps.repository.save_registered_model(request.context.tenant_id, request.change)
        response_0 = modelregistry_v1_registered_model_query_service_pb2.FindRegisteredModelsResponse()
        response_1 = lineage_v1_lineage_node_sync_service_pb2.StreamLineageNodeChangesResponse()
        outgoing_0 = modelregistry_v1_registered_model_query_service_pb2.FindRegisteredModelsRequest(
            context=request.context,
            filter=modelregistry_v1_registered_model_query_service_pb2.FindRegisteredModelsRequest.Filter(
                region=request.change.address.region
            )
        )
        response_0 = await deps.clients.modelregistry_registered_model_query.FindRegisteredModels(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = lineage_v1_lineage_node_sync_service_pb2.StreamLineageNodeChangesRequest(
            change=lineage_v1_lineage_pb2.LineageNode(
                children=[
                    lineage_v1_lineage_pb2.LineageNode(
                        children=[
                            lineage_v1_lineage_pb2.LineageNode(
                                location=common_v1_address_pb2.PostalAddress(
                                    country_code=request.change.address.country_code,
                                    postal_code=request.change.address.postal_code
                                )
                            )
                        ]
                    )
                ]
            ),
            context=request.context
        )
        async for chunk_1 in deps.clients.lineage_lineage_node_sync.StreamLineageNodeChanges(
            async_messages((outgoing_1,)),
            timeout=deps.settings.timeout
        ):
            response_1 = chunk_1
        returned_0_0 = response_0.result.details
        response.result.details.update(returned_0_0)
        returned_0_1 = response_0.result.correlation_id
        if returned_0_1:
            response.result.correlation_id = returned_0_1
        echoed_0 = request.change.owner
        response.registered_model.owner.CopyFrom(echoed_0)
        echoed_1 = request.ack.status
        response.result.status = echoed_1
        return response


async def handle_sync_registered_models(
    deps: Dependencies,
    request: modelregistry_v1_registered_model_sync_service_pb2.SyncRegisteredModelsRequest
) -> modelregistry_v1_registered_model_sync_service_pb2.SyncRegisteredModelsResponse:
    """Syncs a registered model."""
    response = modelregistry_v1_registered_model_sync_service_pb2.SyncRegisteredModelsResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('SyncRegisteredModels', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'SyncRegisteredModels', {'reason': request.reason})
        await deps.repository.save_registered_model(request.context.tenant_id, request.registered_model)
        response_0 = modelregistry_v1_model_version_calculation_service_pb2.CalculateModelVersionResponse()
        outgoing_0 = modelregistry_v1_model_version_calculation_service_pb2.CalculateModelVersionRequest()
        outgoing_0.context.CopyFrom(request.context)
        if request.registered_model.WhichOneof('locator') == 'address':
            outgoing_0.details.destination.lines.extend(list(request.registered_model.address.lines))
        outgoing_0.model_version.subject.display_name = request.registered_model.owner.display_name
        if request.registered_model.WhichOneof('locator') == 'address':
            outgoing_0.details.destination.country_code = request.registered_model.address.country_code
        response_0 = await deps.clients.modelregistry_model_version_calculation.CalculateModelVersion(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.result.details
        response.result.details.update(returned_0_0)
        echoed_0 = request.registered_model_id
        response.registered_model.registered_model_id = echoed_0
        echoed_1 = request.registered_model.code
        response.registered_model.code = echoed_1
        return response
