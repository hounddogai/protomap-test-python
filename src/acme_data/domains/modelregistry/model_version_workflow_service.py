"""Runs the long-lived workflow that takes a model version from start to finish."""

from __future__ import annotations

from collections.abc import AsyncIterator
from collections.abc import Awaitable
from collections.abc import Callable
from functools import partial
from typing import Any
from typing import cast
import asyncio
import logging

from google.protobuf.json_format import MessageToJson
from google.protobuf.json_format import Parse
import grpc

from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.customers.v1 import (
    consent_record_calculation_service_pb2 as customers_v1_consent_record_calculation_service_pb2,
)
from acme.customers.v1 import customer_calculation_service_pb2 as customers_v1_customer_calculation_service_pb2
from acme.customers.v1 import customer_validation_service_pb2 as customers_v1_customer_validation_service_pb2
from acme.customers.v1 import customers_pb2 as customers_v1_customers_pb2
from acme.featurestore.v1 import entity_approval_service_pb2 as featurestore_v1_entity_approval_service_pb2
from acme.featurestore.v1 import entity_approval_service_pb2_grpc as featurestore_v1_entity_approval_service_pb2_grpc
from acme.featurestore.v1 import feature_value_sync_service_pb2 as featurestore_v1_feature_value_sync_service_pb2
from acme.featurestore.v1 import featurestore_pb2 as featurestore_v1_featurestore_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.identity.v1 import user_query_service_pb2 as identity_v1_user_query_service_pb2
from acme.ledger.v1 import ledger_account_service_pb2 as ledger_v1_ledger_account_service_pb2
from acme.ledger.v1 import ledger_pb2 as ledger_v1_ledger_pb2
from acme.lineage.v1 import impact_approval_service_pb2 as lineage_v1_impact_approval_service_pb2
from acme.lineage.v1 import lineage_node_workflow_service_pb2 as lineage_v1_lineage_node_workflow_service_pb2
from acme.modelregistry.v1 import deployment_approval_service_pb2 as modelregistry_v1_deployment_approval_service_pb2
from acme.modelregistry.v1 import (
    model_version_lifecycle_service_pb2 as modelregistry_v1_model_version_lifecycle_service_pb2,
)
from acme.modelregistry.v1 import (
    model_version_workflow_service_pb2 as modelregistry_v1_model_version_workflow_service_pb2,
)
from acme.modelregistry.v1 import (
    model_version_workflow_service_pb2_grpc as modelregistry_v1_model_version_workflow_service_pb2_grpc,
)
from acme.modelregistry.v1 import modelregistry_pb2 as modelregistry_v1_modelregistry_pb2
from acme.modelregistry.v1 import (
    registered_model_approval_service_pb2 as modelregistry_v1_registered_model_approval_service_pb2,
)
from acme.modelregistry.v1 import (
    registered_model_query_service_pb2 as modelregistry_v1_registered_model_query_service_pb2,
)
from acme.modelregistry.v1 import (
    registered_model_reporting_service_pb2 as modelregistry_v1_registered_model_reporting_service_pb2,
)
from acme.modelregistry.v1 import (
    registered_model_sync_service_pb2 as modelregistry_v1_registered_model_sync_service_pb2,
)
from acme.modelregistry.v1 import (
    registered_model_validation_service_pb2 as modelregistry_v1_registered_model_validation_service_pb2,
)
from acme.search.v1 import search_index_validation_service_pb2 as search_v1_search_index_validation_service_pb2
from acme.search.v1 import search_pb2 as search_v1_search_pb2

from acme_data.domains.modelregistry.adapters import ModelVersionWorkflowPauseModelVersionWorkflow3Adapter
from acme_data.domains.modelregistry.adapters import ModelVersionWorkflowPauseModelVersionWorkflow3Port
from acme_data.domains.modelregistry.dependencies import Dependencies
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import run_steps
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_id
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class ModelVersionWorkflowServicer(
    modelregistry_v1_model_version_workflow_service_pb2_grpc.ModelVersionWorkflowServiceServicer
):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    async def AdvanceModelVersionWorkflow(
        self, request: modelregistry_v1_model_version_workflow_service_pb2.AdvanceModelVersionWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_model_version_workflow_service_pb2.AdvanceModelVersionWorkflowResponse:
        """Advances a model version."""
        return await self.handle_advance_model_version_workflow(request)

    @rpc_errors
    async def CancelModelVersionWorkflow(
        self, request: modelregistry_v1_model_version_workflow_service_pb2.CancelModelVersionWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_model_version_workflow_service_pb2.CancelModelVersionWorkflowResponse:
        """Cancels a model version."""
        return await self.handle_cancel_model_version_workflow(request)

    @rpc_errors
    @retry_transient
    async def InspectModelVersionWorkflow(
        self, request: modelregistry_v1_model_version_workflow_service_pb2.InspectModelVersionWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_model_version_workflow_service_pb2.InspectModelVersionWorkflowResponse:
        """Returns a model version."""
        return await self.handle_inspect_model_version_workflow(request)

    @rpc_errors
    @retry_transient
    async def ListModelVersionWorkflows(
        self, request: modelregistry_v1_model_version_workflow_service_pb2.ListModelVersionWorkflowsRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_model_version_workflow_service_pb2.ListModelVersionWorkflowsResponse:
        """Lists model versions a page at a time."""
        return await self.handle_list_model_version_workflows(request)

    @rpc_errors
    async def PauseModelVersionWorkflow(
        self, request: modelregistry_v1_model_version_workflow_service_pb2.PauseModelVersionWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_model_version_workflow_service_pb2.PauseModelVersionWorkflowResponse:
        """Pauses a model version."""
        return await self.handle_pause_model_version_workflow(request)

    @rpc_errors
    async def ResumeModelVersionWorkflow(
        self, request: modelregistry_v1_model_version_workflow_service_pb2.ResumeModelVersionWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_model_version_workflow_service_pb2.ResumeModelVersionWorkflowResponse:
        """Resumes a model version."""
        return await self.handle_resume_model_version_workflow(request)

    @rpc_errors
    async def RetryModelVersionWorkflow(
        self, request: modelregistry_v1_model_version_workflow_service_pb2.RetryModelVersionWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_model_version_workflow_service_pb2.RetryModelVersionWorkflowResponse:
        """Retrys a model version."""
        return await self.handle_retry_model_version_workflow(request)

    @rpc_errors
    async def SignalModelVersionWorkflow(
        self, request: modelregistry_v1_model_version_workflow_service_pb2.SignalModelVersionWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_model_version_workflow_service_pb2.SignalModelVersionWorkflowResponse:
        """Signals a model version."""
        return await self.handle_signal_model_version_workflow(request)

    @rpc_errors
    async def StartModelVersionWorkflow(
        self, request: modelregistry_v1_model_version_workflow_service_pb2.StartModelVersionWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_model_version_workflow_service_pb2.StartModelVersionWorkflowResponse:
        """Starts a model version."""
        return await self.handle_start_model_version_workflow(request)

    async def handle_advance_model_version_workflow(
        self,
        request: modelregistry_v1_model_version_workflow_service_pb2.AdvanceModelVersionWorkflowRequest
    ) -> modelregistry_v1_model_version_workflow_service_pb2.AdvanceModelVersionWorkflowResponse:
        """Advances a model version."""
        deps = self.deps
        response = modelregistry_v1_model_version_workflow_service_pb2.AdvanceModelVersionWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('AdvanceModelVersionWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'AdvanceModelVersionWorkflow',
                {'reason': request.reason}
            )
            await deps.repository.save_model_version(request.context.tenant_id, request.model_version)
            response_0 = lineage_v1_impact_approval_service_pb2.SubmitImpactResponse()
            response_1 = modelregistry_v1_registered_model_validation_service_pb2.PreviewRegisteredModelResponse()
            response_2 = customers_v1_customer_validation_service_pb2.ValidateCustomerResponse()
            response_3 = modelregistry_v1_deployment_approval_service_pb2.SubmitDeploymentResponse()
            fields_0: dict[str, Any] = {
                'context': request.context,
                'impact': {'customer': {'email': request.details.notify.email}}
            }
            outgoing_0 = lineage_v1_impact_approval_service_pb2.SubmitImpactRequest(**fields_0)
            response_0 = await deps.clients.lineage_impact_approval.SubmitImpact(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            async for item_1 in async_messages(request.model_version.measurements):
                outgoing_1 = modelregistry_v1_registered_model_validation_service_pb2.PreviewRegisteredModelRequest(
                    context=request.context,
                    registered_model=modelregistry_v1_modelregistry_pb2.RegisteredModel(
                        dimensions=modelregistry_v1_modelregistry_pb2.RegisteredModelDimensions(unit=item_1.unit),
                        owner=identity_v1_refs_pb2.UserRef(email=response_0.impact.assignee.email)
                    )
                )
                response_1 = await deps.clients.modelregistry_registered_model_validation.PreviewRegisteredModel(
                    outgoing_1,
                    timeout=deps.settings.timeout
                )
            outgoing_2 = customers_v1_customer_validation_service_pb2.ValidateCustomerRequest(
                context=request.context,
                customer=customers_v1_customers_pb2.Customer(
                    relationship_manager=identity_v1_refs_pb2.UserRef(email=request.model_version.subject.email)
                ),
                details=customers_v1_customer_validation_service_pb2.ValidateCustomerRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(name=request.details.notify.name)
                )
            )
            document_2 = MessageToJson(outgoing_2, preserving_proto_field_name=True)
            outgoing_2 = Parse(document_2, customers_v1_customer_validation_service_pb2.ValidateCustomerRequest())
            response_2 = await deps.clients.customers_customer_validation.ValidateCustomer(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            outgoing_3 = modelregistry_v1_deployment_approval_service_pb2.SubmitDeploymentRequest()
            outgoing_3.context.CopyFrom(request.context)
            field_3_1_part_1 = outgoing_3.deployment.participants.add()
            field_3_1_part_1.contact.email = request.details.notify.email
            field_3_2_part_1 = outgoing_3.deployment.participants.add()
            field_3_2_part_1.contact.name.CopyFrom(request.details.notify.name)
            outgoing_3.details.approver.email = response_0.impact.assignee.email
            merged_3 = modelregistry_v1_deployment_approval_service_pb2.SubmitDeploymentRequest()
            merged_3.MergeFrom(outgoing_3)
            outgoing_3.CopyFrom(merged_3)
            response_3 = await deps.clients.modelregistry_deployment_approval.SubmitDeployment(
                outgoing_3,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.impact.customer.customer_id
            if returned_0_0:
                response.model_version.subject.customer_id = returned_0_0
            returned_2_0 = response_2.customer.relationship_manager.email
            if returned_2_0:
                response.model_version.subject.email = returned_2_0
            returned_3_0 = response_3.deployment.organizer.email
            if returned_3_0:
                response.model_version.subject.email = returned_3_0
            returned_3_1 = response_3.result.correlation_id
            if returned_3_1:
                response.result.correlation_id = returned_3_1
            echoed_0 = request.model_version_id
            response.model_version.model_version_id = echoed_0
            echoed_1 = request.model_version.attributes
            response.model_version.attributes.update(echoed_1)
            return response

    async def handle_cancel_model_version_workflow(
        self,
        request: modelregistry_v1_model_version_workflow_service_pb2.CancelModelVersionWorkflowRequest
    ) -> modelregistry_v1_model_version_workflow_service_pb2.CancelModelVersionWorkflowResponse:
        """Cancels a model version."""
        deps = self.deps
        response = modelregistry_v1_model_version_workflow_service_pb2.CancelModelVersionWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CancelModelVersionWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'CancelModelVersionWorkflow',
                {'reason': request.reason}
            )
            await deps.repository.save_model_version(request.context.tenant_id, request.model_version)
            response_0 = modelregistry_v1_model_version_lifecycle_service_pb2.ScheduleModelVersionExpiryResponse()
            response_1 = featurestore_v1_entity_approval_service_pb2.CommentEntityApprovalResponse()
            for item_0 in request.model_version.measurements:
                outgoing_0 = modelregistry_v1_model_version_lifecycle_service_pb2.ScheduleModelVersionExpiryRequest(
                    context=request.context,
                    model_version=modelregistry_v1_modelregistry_pb2.ModelVersion(
                        measurements=[
                            modelregistry_v1_modelregistry_pb2.ModelVersionMeasurement(
                                metric=item_0.metric,
                                observed_at=item_0.observed_at,
                                unit=item_0.unit,
                                value=item_0.value
                            )
                        ]
                    )
                )
                response_0 = await deps.clients.modelregistry_model_version_lifecycle.ScheduleModelVersionExpiry(
                    outgoing_0,
                    timeout=deps.settings.timeout
                )
            outgoing_1 = featurestore_v1_entity_approval_service_pb2.CommentEntityApprovalRequest(
                context=request.context,
                entity=featurestore_v1_featurestore_pb2.Entity(
                    contact=common_v1_contact_pb2.ContactInfo(name=request.details.notify.name)
                )
            )
            registered_1 = cast(
                featurestore_v1_entity_approval_service_pb2_grpc.EntityApprovalServiceStub,
                deps.clients.registry['acme.featurestore.v1.EntityApprovalService']
            )
            response_1 = await registered_1.CommentEntityApproval(outgoing_1, timeout=deps.settings.timeout)
            returned_1_0 = response_1.outcome.message
            if returned_1_0:
                response.outcome.message = returned_1_0
            returned_1_1 = response_1.entity.attributes
            response.model_version.attributes.update(returned_1_1)
            echoed_0 = request.model_version_id
            response.model_version.model_version_id = echoed_0
            echoed_1 = request.model_version.subject
            response.model_version.subject.CopyFrom(echoed_1)
            return response

    async def handle_inspect_model_version_workflow(
        self,
        request: modelregistry_v1_model_version_workflow_service_pb2.InspectModelVersionWorkflowRequest
    ) -> modelregistry_v1_model_version_workflow_service_pb2.InspectModelVersionWorkflowResponse:
        """Returns a model version."""
        deps = self.deps
        response = modelregistry_v1_model_version_workflow_service_pb2.InspectModelVersionWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('InspectModelVersionWorkflow', extra={'fields': {'domain': 'modelregistry'}})
            await deps.repository.audit(request.context.tenant_id, 'InspectModelVersionWorkflow', {})
            response_0 = modelregistry_v1_deployment_approval_service_pb2.DelegateDeploymentApprovalResponse()
            outgoing_0 = modelregistry_v1_deployment_approval_service_pb2.DelegateDeploymentApprovalRequest(
                context=request.context,
                deployment=modelregistry_v1_modelregistry_pb2.Deployment(
                    organizer=identity_v1_refs_pb2.UserRef(user_id=request.context.actor.user_id),
                    participants=[
                        modelregistry_v1_modelregistry_pb2.DeploymentParticipant(
                            contact=common_v1_contact_pb2.ContactInfo(email=request.context.actor.email),
                            participant_id=request.model_version_id
                        )
                    ]
                )
            )
            response_0 = await deps.clients.modelregistry_deployment_approval.DelegateDeploymentApproval(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.result.message = returned_0_0
            echoed_0 = request.model_version_id
            response.model_version.model_version_id = echoed_0
            return response

    async def handle_list_model_version_workflows(
        self,
        request: modelregistry_v1_model_version_workflow_service_pb2.ListModelVersionWorkflowsRequest
    ) -> modelregistry_v1_model_version_workflow_service_pb2.ListModelVersionWorkflowsResponse:
        """Lists model versions a page at a time."""
        deps = self.deps
        response = modelregistry_v1_model_version_workflow_service_pb2.ListModelVersionWorkflowsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ListModelVersionWorkflows', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ListModelVersionWorkflows',
                {'order_by': request.order_by}
            )
            response_0 = ledger_v1_ledger_account_service_pb2.CloneLedgerAccountResponse()
            outgoing_0 = ledger_v1_ledger_account_service_pb2.CloneLedgerAccountRequest(
                context=request.context,
                ledger_account=ledger_v1_ledger_pb2.LedgerAccount(labels=dict(request.filter.labels))
            )
            response_0 = await deps.clients.ledger_ledger_account.CloneLedgerAccount(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.status
            if returned_0_0:
                response.result.status = returned_0_0
            returned_0_1 = response_0.result.correlation_id
            if returned_0_1:
                response.result.correlation_id = returned_0_1
            return response

    async def handle_pause_model_version_workflow(
        self,
        request: modelregistry_v1_model_version_workflow_service_pb2.PauseModelVersionWorkflowRequest
    ) -> modelregistry_v1_model_version_workflow_service_pb2.PauseModelVersionWorkflowResponse:
        """Pauses a model version."""
        deps = self.deps
        response = modelregistry_v1_model_version_workflow_service_pb2.PauseModelVersionWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('PauseModelVersionWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'PauseModelVersionWorkflow',
                {'reason': request.reason}
            )
            await deps.repository.save_model_version(request.context.tenant_id, request.model_version)
            response_0 = customers_v1_customer_calculation_service_pb2.ExplainCustomerCalculationResponse()
            response_1 = featurestore_v1_feature_value_sync_service_pb2.PullFeatureValuesResponse()
            response_2 = lineage_v1_lineage_node_workflow_service_pb2.AdvanceLineageNodeWorkflowResponse()
            response_3 = modelregistry_v1_registered_model_sync_service_pb2.SyncRegisteredModelsResponse()
            outgoing_0 = customers_v1_customer_calculation_service_pb2.ExplainCustomerCalculationRequest(
                context=request.context,
                customer=customers_v1_customers_pb2.Customer(
                    contact=common_v1_contact_pb2.ContactInfo(email=request.model_version.subject.email),
                    relationship_manager=identity_v1_refs_pb2.UserRef(
                        display_name=request.model_version.subject.display_name
                    )
                )
            )
            send_0 = partial(
                deps.clients.customers_customer_calculation.ExplainCustomerCalculation,
                timeout=deps.settings.timeout
            )
            response_0 = await send_0(outgoing_0)
            requests_1: list[featurestore_v1_feature_value_sync_service_pb2.PullFeatureValuesRequest] = []
            for item_1 in request.model_version.measurements:
                outgoing_1 = featurestore_v1_feature_value_sync_service_pb2.PullFeatureValuesRequest(
                    context=request.context,
                    feature_value=featurestore_v1_featurestore_pb2.FeatureValue(
                        measurements=[
                            featurestore_v1_featurestore_pb2.FeatureValueMeasurement(
                                metric=item_1.metric,
                                observed_at=item_1.observed_at,
                                unit=item_1.unit,
                                value=item_1.value
                            )
                        ]
                    )
                )
                requests_1.append(outgoing_1)
            replies_1 = await asyncio.gather(*(
                deps.clients.featurestore_feature_value_sync.PullFeatureValues(
                    entry,
                    timeout=deps.settings.timeout
                ) for entry in requests_1
            ))
            if replies_1:
                response_1 = replies_1[-1]
            outgoing_2 = lineage_v1_lineage_node_workflow_service_pb2.AdvanceLineageNodeWorkflowRequest()
            outgoing_2.context.CopyFrom(request.context)
            field_2_1_part_1 = outgoing_2.lineage_node.children.add()
            field_2_1_part_2 = field_2_1_part_1.children.add()
            field_2_1_part_2.audit.updated_at.CopyFrom(response_0.customer.audit.updated_at)
            field_2_2_part_1 = outgoing_2.lineage_node.children.add()
            field_2_2_part_2 = field_2_2_part_1.children.add()
            field_2_2_part_2.manager.display_name = response_1.feature_value.subject.display_name
            field_2_3_part_1 = outgoing_2.lineage_node.children.add()
            field_2_3_part_2 = field_2_3_part_1.children.add()
            field_2_3_part_2.audit.created_at.CopyFrom(response_0.customer.audit.created_at)
            outgoing_2.context.tenant_id = tenant_id.get()
            response_2 = await deps.clients.lineage_lineage_node_workflow.AdvanceLineageNodeWorkflow(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            outgoing_3 = modelregistry_v1_registered_model_sync_service_pb2.SyncRegisteredModelsRequest(
                context=request.context,
                registered_model=modelregistry_v1_modelregistry_pb2.RegisteredModel(
                    address=common_v1_address_pb2.PostalAddress(
                        locality=response_2.lineage_node.location.locality,
                        recipient=response_2.lineage_node.location.recipient
                    ),
                    owner=identity_v1_refs_pb2.UserRef(display_name=request.model_version.subject.display_name)
                )
            )
            port_3: ModelVersionWorkflowPauseModelVersionWorkflow3Port = ModelVersionWorkflowPauseModelVersionWorkflow3Adapter(
                deps.clients.modelregistry_registered_model_sync,
                deps.settings.timeout
            )
            response_3 = await port_3.execute(outgoing_3)
            returned_0_0 = response_0.customer.contact.email
            if returned_0_0:
                response.model_version.subject.email = returned_0_0
            returned_2_0 = response_2.outcome.reference_id
            if returned_2_0:
                response.outcome.reference_id = returned_2_0
            returned_3_0 = response_3.outcome.status
            if returned_3_0:
                response.result.status = returned_3_0
            returned_3_1 = response_3.result.message
            if returned_3_1:
                response.outcome.message = returned_3_1
            echoed_0 = request.model_version_id
            response.model_version.model_version_id = echoed_0
            echoed_1 = request.model_version.kind
            response.model_version.kind = echoed_1
            return response

    async def handle_resume_model_version_workflow(
        self,
        request: modelregistry_v1_model_version_workflow_service_pb2.ResumeModelVersionWorkflowRequest
    ) -> modelregistry_v1_model_version_workflow_service_pb2.ResumeModelVersionWorkflowResponse:
        """Resumes a model version."""
        deps = self.deps
        response = modelregistry_v1_model_version_workflow_service_pb2.ResumeModelVersionWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ResumeModelVersionWorkflow', extra={'fields': {'initiated_by': request.details.initiated_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ResumeModelVersionWorkflow',
                {'initiated_by': request.details.initiated_by}
            )
            await deps.repository.save_model_version(request.context.tenant_id, request.model_version)
            response_0 = modelregistry_v1_registered_model_approval_service_pb2.SubmitRegisteredModelResponse()
            response_1 = customers_v1_consent_record_calculation_service_pb2.CompareConsentRecordOptionsResponse()
            outgoing_0 = modelregistry_v1_registered_model_approval_service_pb2.SubmitRegisteredModelRequest(
                annotations=dict(request.annotations),
                context=request.context,
                details=modelregistry_v1_registered_model_approval_service_pb2.SubmitRegisteredModelRequest.Details(
                    approver=identity_v1_refs_pb2.UserRef(email=request.details.notify.email)
                ),
                reason=request.reason,
                registered_model=modelregistry_v1_modelregistry_pb2.RegisteredModel(
                    owner=identity_v1_refs_pb2.UserRef(display_name=request.model_version.subject.display_name)
                )
            )
            steps_0 = [
                partial(
                    deps.clients.modelregistry_registered_model_approval.SubmitRegisteredModel,
                    outgoing_0,
                    timeout=deps.settings.timeout
                )
            ]
            results_0 = await run_steps(steps_0)
            response_0 = results_0[-1]
            callbacks_1: list[
                Callable[
                    [],
                    Awaitable[customers_v1_consent_record_calculation_service_pb2.CompareConsentRecordOptionsResponse]
                ]
            ] = []
            for item_1 in request.model_version.measurements:
                outgoing_1 = customers_v1_consent_record_calculation_service_pb2.CompareConsentRecordOptionsRequest(
                    consent_record=customers_v1_customers_pb2.ConsentRecord(
                        measurements=[
                            customers_v1_customers_pb2.ConsentRecordMeasurement(
                                metric=item_1.metric,
                                observed_at=item_1.observed_at,
                                value=item_1.value
                            )
                        ]
                    ),
                    context=request.context
                )
                async def send_1(
                    payload: customers_v1_consent_record_calculation_service_pb2.CompareConsentRecordOptionsRequest = outgoing_1
                ) -> customers_v1_consent_record_calculation_service_pb2.CompareConsentRecordOptionsResponse:
                    return await deps.clients.customers_consent_record_calculation.CompareConsentRecordOptions(
                        payload,
                        timeout=deps.settings.timeout
                    )
                callbacks_1.append(send_1)
            for callback_1 in callbacks_1:
                response_1 = await callback_1()
            returned_0_0 = response_0.outcome.reference_id
            if returned_0_0:
                response.outcome.reference_id = returned_0_0
            returned_0_1 = response_0.outcome.message
            if returned_0_1:
                response.result.message = returned_0_1
            echoed_0 = request.model_version_id
            response.model_version.model_version_id = echoed_0
            echoed_1 = request.model_version.correlation_id
            response.model_version.correlation_id = echoed_1
            return response

    async def handle_retry_model_version_workflow(
        self,
        request: modelregistry_v1_model_version_workflow_service_pb2.RetryModelVersionWorkflowRequest
    ) -> modelregistry_v1_model_version_workflow_service_pb2.RetryModelVersionWorkflowResponse:
        """Retrys a model version."""
        deps = self.deps
        response = modelregistry_v1_model_version_workflow_service_pb2.RetryModelVersionWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('RetryModelVersionWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'RetryModelVersionWorkflow',
                {'reason': request.reason}
            )
            await deps.repository.save_model_version(request.context.tenant_id, request.model_version)
            response_0 = modelregistry_v1_deployment_approval_service_pb2.SubmitDeploymentResponse()
            response_1 = modelregistry_v1_registered_model_reporting_service_pb2.StreamRegisteredModelMetricsResponse()
            outgoing_0 = modelregistry_v1_deployment_approval_service_pb2.SubmitDeploymentRequest(
                context=request.context,
                deployment=modelregistry_v1_modelregistry_pb2.Deployment(
                    participants=[
                        modelregistry_v1_modelregistry_pb2.DeploymentParticipant(
                            contact=common_v1_contact_pb2.ContactInfo(phone=request.details.notify.phone)
                        )
                    ]
                ),
                details=modelregistry_v1_deployment_approval_service_pb2.SubmitDeploymentRequest.Details(
                    approver=identity_v1_refs_pb2.UserRef(email=request.details.notify.email)
                )
            )
            response_0 = cast(modelregistry_v1_deployment_approval_service_pb2.SubmitDeploymentResponse, await deps.bus.request(
                'acme.modelregistry.v1.ModelVersionWorkflowService/RetryModelVersionWorkflow/0', outgoing_0, deps.settings.timeout,
            ))
            outgoing_1 = modelregistry_v1_registered_model_reporting_service_pb2.StreamRegisteredModelMetricsRequest(
                context=request.context,
                subscriber=common_v1_contact_pb2.ContactInfo(
                    email=request.details.notify.email,
                    name=request.details.notify.name,
                    phone=request.details.notify.phone,
                    preferred_channel=request.details.notify.preferred_channel
                )
            )
            async for chunk_1 in deps.clients.modelregistry_registered_model_reporting.StreamRegisteredModelMetrics(
                outgoing_1,
                timeout=deps.settings.timeout
            ):
                response_1 = chunk_1
            returned_0_0 = response_0.outcome.effective_at
            if returned_0_0.ListFields():
                response.outcome.effective_at.MergeFrom(returned_0_0)
            echoed_0 = request.model_version_id
            response.model_version.model_version_id = echoed_0
            echoed_1 = request.model_version.subject
            response.model_version.subject.CopyFrom(echoed_1)
            return response

    async def handle_signal_model_version_workflow(
        self,
        request: modelregistry_v1_model_version_workflow_service_pb2.SignalModelVersionWorkflowRequest
    ) -> modelregistry_v1_model_version_workflow_service_pb2.SignalModelVersionWorkflowResponse:
        """Signals a model version."""
        deps = self.deps
        response = modelregistry_v1_model_version_workflow_service_pb2.SignalModelVersionWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SignalModelVersionWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'SignalModelVersionWorkflow',
                {'reason': request.reason}
            )
            await deps.repository.save_model_version(request.context.tenant_id, request.model_version)
            response_0 = search_v1_search_index_validation_service_pb2.CheckSearchIndexEligibilityResponse()
            async for item_0 in async_messages(request.model_version.measurements):
                outgoing_0 = search_v1_search_index_validation_service_pb2.CheckSearchIndexEligibilityRequest(
                    context=request.context,
                    details=search_v1_search_index_validation_service_pb2.CheckSearchIndexEligibilityRequest.Details(
                        contact=common_v1_contact_pb2.ContactInfo(
                            email=request.model_version.subject.email,
                            preferred_channel=request.details.notify.preferred_channel
                        )
                    ),
                    search_index=search_v1_search_pb2.SearchIndex(
                        audit=common_v1_audit_pb2.AuditInfo(created_at=item_0.observed_at),
                        dimensions=search_v1_search_pb2.SearchIndexDimensions(unit=item_0.unit)
                    )
                )
                response_0 = await deps.clients.search_search_index_validation.CheckSearchIndexEligibility(
                    outgoing_0,
                    timeout=deps.settings.timeout
                )
            echoed_0 = request.model_version_id
            response.model_version.model_version_id = echoed_0
            echoed_1 = request.model_version.sequence
            response.model_version.sequence = echoed_1
            return response

    async def handle_start_model_version_workflow(
        self,
        request: modelregistry_v1_model_version_workflow_service_pb2.StartModelVersionWorkflowRequest
    ) -> modelregistry_v1_model_version_workflow_service_pb2.StartModelVersionWorkflowResponse:
        """Starts a model version."""
        deps = self.deps
        response = modelregistry_v1_model_version_workflow_service_pb2.StartModelVersionWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('StartModelVersionWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'StartModelVersionWorkflow',
                {'reason': request.reason}
            )
            await deps.repository.save_model_version(request.context.tenant_id, request.model_version)
            response_0 = modelregistry_v1_registered_model_query_service_pb2.ResolveRegisteredModelsResponse()
            response_1 = identity_v1_user_query_service_pb2.LookupUserResponse()
            outgoing_0 = modelregistry_v1_registered_model_query_service_pb2.ResolveRegisteredModelsRequest(
                context=request.context
            )
            outgoing_1 = identity_v1_user_query_service_pb2.LookupUserRequest(
                context=request.context,
                user_id=request.context.actor.user_id
            )
            response_0, response_1 = await asyncio.gather(
                deps.clients.modelregistry_registered_model_query.ResolveRegisteredModels(
                    outgoing_0,
                    timeout=deps.settings.timeout
                ),
                deps.clients.identity_user_query.LookupUser(outgoing_1, timeout=deps.settings.timeout),
            )
            returned_0_0 = response_0.result.status
            if returned_0_0:
                response.result.status = returned_0_0
            returned_0_1 = response_0.result.message
            if returned_0_1:
                response.outcome.message = returned_0_1
            returned_1_0 = response_1.user.contact.email
            if returned_1_0:
                response.model_version.subject.email = returned_1_0
            returned_1_1 = response_1.result.correlation_id
            if returned_1_1:
                response.result.correlation_id = returned_1_1
            echoed_0 = request.model_version_id
            response.model_version.model_version_id = echoed_0
            echoed_1 = request.model_version.sequence
            response.model_version.sequence = echoed_1
            return response
