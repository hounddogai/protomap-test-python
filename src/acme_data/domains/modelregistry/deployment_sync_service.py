"""Keeps deployments in step with the systems of record in other regions."""

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

from acme.anomalies.v1 import (
    anomaly_feedback_workflow_service_pb2 as anomalies_v1_anomaly_feedback_workflow_service_pb2,
)
from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.customers.v1 import (
    consent_record_calculation_service_pb2 as customers_v1_consent_record_calculation_service_pb2,
)
from acme.customers.v1 import (
    consent_record_validation_service_pb2 as customers_v1_consent_record_validation_service_pb2,
)
from acme.customers.v1 import customer_query_service_pb2 as customers_v1_customer_query_service_pb2
from acme.customers.v1 import (
    customer_segment_calculation_service_pb2 as customers_v1_customer_segment_calculation_service_pb2,
)
from acme.customers.v1 import (
    customer_segment_calculation_service_pb2_grpc as customers_v1_customer_segment_calculation_service_pb2_grpc,
)
from acme.customers.v1 import customers_pb2 as customers_v1_customers_pb2
from acme.customers.v1 import household_calculation_service_pb2 as customers_v1_household_calculation_service_pb2
from acme.customers.v1 import refs_pb2 as customers_v1_refs_pb2
from acme.documents.v1 import document_service_pb2 as documents_v1_document_service_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.identity.v1 import user_service_pb2 as identity_v1_user_service_pb2
from acme.lineage.v1 import lineage_node_reporting_service_pb2 as lineage_v1_lineage_node_reporting_service_pb2
from acme.metrics.v1 import dashboard_sync_service_pb2 as metrics_v1_dashboard_sync_service_pb2
from acme.metrics.v1 import metrics_pb2 as metrics_v1_metrics_pb2
from acme.modelregistry.v1 import deployment_import_service_pb2 as modelregistry_v1_deployment_import_service_pb2
from acme.modelregistry.v1 import deployment_sync_service_pb2 as modelregistry_v1_deployment_sync_service_pb2
from acme.modelregistry.v1 import deployment_sync_service_pb2_grpc as modelregistry_v1_deployment_sync_service_pb2_grpc
from acme.modelregistry.v1 import model_version_sync_service_pb2 as modelregistry_v1_model_version_sync_service_pb2
from acme.modelregistry.v1 import (
    model_version_validation_service_pb2 as modelregistry_v1_model_version_validation_service_pb2,
)
from acme.modelregistry.v1 import modelregistry_pb2 as modelregistry_v1_modelregistry_pb2
from acme.modelregistry.v1 import (
    registered_model_query_service_pb2 as modelregistry_v1_registered_model_query_service_pb2,
)
from acme.modelregistry.v1 import (
    registered_model_sync_service_pb2 as modelregistry_v1_registered_model_sync_service_pb2,
)
from acme.modelregistry.v1 import (
    registered_model_validation_service_pb2 as modelregistry_v1_registered_model_validation_service_pb2,
)

from acme_data.domains.modelregistry.adapters import DeploymentSyncResolveDeploymentConflict1Adapter
from acme_data.domains.modelregistry.adapters import DeploymentSyncResolveDeploymentConflict1Port
from acme_data.domains.modelregistry.dependencies import Dependencies
from acme_data.domains.modelregistry.models import DeploymentSyncPushDeployment1Command
from acme_data.domains.modelregistry.models import to_deployment_sync_push_deployment1_command
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import run_steps
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_id
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class DeploymentSyncServicer(modelregistry_v1_deployment_sync_service_pb2_grpc.DeploymentSyncServiceServicer):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    @retry_transient
    async def GetDeploymentSyncState(
        self, request: modelregistry_v1_deployment_sync_service_pb2.GetDeploymentSyncStateRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_deployment_sync_service_pb2.GetDeploymentSyncStateResponse:
        """Returns a deployment."""
        return await self.handle_get_deployment_sync_state(request)

    @rpc_errors
    @retry_transient
    async def ListDeploymentConflicts(
        self, request: modelregistry_v1_deployment_sync_service_pb2.ListDeploymentConflictsRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_deployment_sync_service_pb2.ListDeploymentConflictsResponse:
        """Lists deployments a page at a time."""
        return await self.handle_list_deployment_conflicts(request)

    @rpc_errors
    async def PullDeployments(
        self, request: modelregistry_v1_deployment_sync_service_pb2.PullDeploymentsRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_deployment_sync_service_pb2.PullDeploymentsResponse:
        """Pulls a deployment."""
        return await self.handle_pull_deployments(request)

    @rpc_errors
    async def PushDeployment(
        self, request: modelregistry_v1_deployment_sync_service_pb2.PushDeploymentRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_deployment_sync_service_pb2.PushDeploymentResponse:
        """Pushs a deployment."""
        return await self.handle_push_deployment(request)

    @rpc_errors
    async def ResolveDeploymentConflict(
        self, request: modelregistry_v1_deployment_sync_service_pb2.ResolveDeploymentConflictRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_deployment_sync_service_pb2.ResolveDeploymentConflictResponse:
        """Resolves a deployment."""
        return await self.handle_resolve_deployment_conflict(request)

    @stream_errors
    async def StreamDeploymentChanges(
        self, requests: AsyncIterator[
            modelregistry_v1_deployment_sync_service_pb2.StreamDeploymentChangesRequest
        ], context: grpc.aio.ServicerContext,
    ) -> AsyncIterator[modelregistry_v1_deployment_sync_service_pb2.StreamDeploymentChangesResponse]:
        """Exchanges changes of deployments with a peer."""
        async for request in requests:
            yield await self.handle_stream_deployment_changes(request)

    @rpc_errors
    async def SyncDeployments(
        self, request: modelregistry_v1_deployment_sync_service_pb2.SyncDeploymentsRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_deployment_sync_service_pb2.SyncDeploymentsResponse:
        """Syncs a deployment."""
        return await self.handle_sync_deployments(request)

    async def handle_get_deployment_sync_state(
        self,
        request: modelregistry_v1_deployment_sync_service_pb2.GetDeploymentSyncStateRequest
    ) -> modelregistry_v1_deployment_sync_service_pb2.GetDeploymentSyncStateResponse:
        """Returns a deployment."""
        deps = self.deps
        response = modelregistry_v1_deployment_sync_service_pb2.GetDeploymentSyncStateResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('GetDeploymentSyncState', extra={'fields': {'domain': 'modelregistry'}})
            await deps.repository.audit(request.context.tenant_id, 'GetDeploymentSyncState', {})
            response_0 = modelregistry_v1_deployment_import_service_pb2.ListDeploymentImportsResponse()
            outgoing_0 = modelregistry_v1_deployment_import_service_pb2.ListDeploymentImportsRequest(
                context=request.context,
                filter=modelregistry_v1_deployment_import_service_pb2.ListDeploymentImportsRequest.Filter(
                    created_after=request.context.deadline,
                    labels=dict(request.context.baggage),
                    owner_id=request.deployment_id
                )
            )
            response_0 = await deps.clients.modelregistry_deployment_import.ListDeploymentImports(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.details
            response.result.details.update(returned_0_0)
            echoed_0 = request.deployment_id
            response.deployment.deployment_id = echoed_0
            return response

    async def handle_list_deployment_conflicts(
        self,
        request: modelregistry_v1_deployment_sync_service_pb2.ListDeploymentConflictsRequest
    ) -> modelregistry_v1_deployment_sync_service_pb2.ListDeploymentConflictsResponse:
        """Lists deployments a page at a time."""
        deps = self.deps
        response = modelregistry_v1_deployment_sync_service_pb2.ListDeploymentConflictsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ListDeploymentConflicts', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ListDeploymentConflicts',
                {'order_by': request.order_by}
            )
            response_0 = modelregistry_v1_registered_model_sync_service_pb2.ReconcileRegisteredModelsResponse()
            outgoing_0 = modelregistry_v1_registered_model_sync_service_pb2.ReconcileRegisteredModelsRequest(
                context=request.context,
                registered_model=modelregistry_v1_modelregistry_pb2.RegisteredModel(
                    address=common_v1_address_pb2.PostalAddress(region=request.filter.region),
                    owner=identity_v1_refs_pb2.UserRef(
                        email=request.context.actor.email,
                        user_id=request.context.actor.user_id
                    )
                )
            )
            response_0 = await deps.clients.modelregistry_registered_model_sync.ReconcileRegisteredModels(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.registered_model.address.lines
            returned_0_0_part_0 = response.deployments.add()
            returned_0_0_part_0.location.lines.extend(returned_0_0)
            returned_0_1 = response_0.registered_model.audit.created_by
            returned_0_1_part_0 = response.deployments.add()
            if returned_0_1:
                returned_0_1_part_0.audit.created_by = returned_0_1
            return response

    async def handle_pull_deployments(
        self,
        request: modelregistry_v1_deployment_sync_service_pb2.PullDeploymentsRequest
    ) -> modelregistry_v1_deployment_sync_service_pb2.PullDeploymentsResponse:
        """Pulls a deployment."""
        deps = self.deps
        response = modelregistry_v1_deployment_sync_service_pb2.PullDeploymentsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('PullDeployments', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'PullDeployments', {'reason': request.reason})
            await deps.repository.save_deployment(request.context.tenant_id, request.deployment)
            response_0 = modelregistry_v1_model_version_sync_service_pb2.ListModelVersionConflictsResponse()
            response_1 = customers_v1_consent_record_calculation_service_pb2.EstimateConsentRecordResponse()
            response_2 = modelregistry_v1_model_version_sync_service_pb2.PullModelVersionsResponse()
            response_3 = customers_v1_customer_segment_calculation_service_pb2.ExplainCustomerSegmentCalculationResponse()
            outgoing_0 = modelregistry_v1_model_version_sync_service_pb2.ListModelVersionConflictsRequest(
                context=request.context,
                filter=modelregistry_v1_model_version_sync_service_pb2.ListModelVersionConflictsRequest.Filter(
                    created_after=request.deployment.audit.created_at,
                    owner_id=request.deployment.organizer.user_id,
                    region=request.deployment.location.region
                )
            )
            document_0 = MessageToJson(outgoing_0, preserving_proto_field_name=True)
            outgoing_0 = Parse(
                document_0,
                modelregistry_v1_model_version_sync_service_pb2.ListModelVersionConflictsRequest()
            )
            response_0 = await deps.clients.modelregistry_model_version_sync.ListModelVersionConflicts(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = customers_v1_consent_record_calculation_service_pb2.EstimateConsentRecordRequest()
            outgoing_1.context.CopyFrom(request.context)
            outgoing_1.consent_record.subject.display_name = request.deployment.organizer.display_name
            outgoing_1.details.destination.region = request.deployment.location.region
            outgoing_1.details.destination.recipient = request.deployment.location.recipient
            outgoing_1.details.destination.lines.extend(list(request.deployment.location.lines))
            merged_1 = customers_v1_consent_record_calculation_service_pb2.EstimateConsentRecordRequest()
            merged_1.MergeFrom(outgoing_1)
            outgoing_1.CopyFrom(merged_1)
            response_1 = await deps.clients.customers_consent_record_calculation.EstimateConsentRecord(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            requests_2: list[modelregistry_v1_model_version_sync_service_pb2.PullModelVersionsRequest] = []
            for item_2 in request.deployment.participants:
                outgoing_2 = modelregistry_v1_model_version_sync_service_pb2.PullModelVersionsRequest(
                    context=request.context,
                    details=modelregistry_v1_model_version_sync_service_pb2.PullModelVersionsRequest.Details(
                        checksum=request.details.checksum
                    ),
                    model_version=modelregistry_v1_modelregistry_pb2.ModelVersion(
                        subject=customers_v1_refs_pb2.CustomerRef(
                            display_name=request.deployment.organizer.display_name,
                            email=item_2.contact.email
                        )
                    )
                )
                requests_2.append(outgoing_2)
            replies_2 = await asyncio.gather(*(
                deps.clients.modelregistry_model_version_sync.PullModelVersions(
                    entry,
                    timeout=deps.settings.timeout
                ) for entry in requests_2
            ))
            if replies_2:
                response_2 = replies_2[-1]
            outgoing_3 = customers_v1_customer_segment_calculation_service_pb2.ExplainCustomerSegmentCalculationRequest(
                context=request.context,
                customer_segment=customers_v1_customers_pb2.CustomerSegment(
                    owner=identity_v1_refs_pb2.UserRef(email=response_2.model_version.subject.email)
                )
            )
            registered_3 = cast(
                customers_v1_customer_segment_calculation_service_pb2_grpc.CustomerSegmentCalculationServiceStub,
                deps.clients.registry['acme.customers.v1.CustomerSegmentCalculationService']
            )
            response_3 = await registered_3.ExplainCustomerSegmentCalculation(outgoing_3, timeout=deps.settings.timeout)
            returned_0_0 = response_0.result.status
            if returned_0_0:
                response.outcome.status = returned_0_0
            returned_1_0 = response_1.result.status
            if returned_1_0:
                response.result.status = returned_1_0
            returned_1_1 = response_1.result.message
            if returned_1_1:
                response.outcome.message = returned_1_1
            returned_3_0 = response_3.outcome.next_steps
            response.outcome.next_steps.extend(returned_3_0)
            returned_3_1 = response_3.result.message
            if returned_3_1:
                response.outcome.message = returned_3_1
            echoed_0 = request.deployment_id
            response.deployment.deployment_id = echoed_0
            echoed_1 = request.deployment.metadata
            response.deployment.metadata.update(echoed_1)
            return response

    async def handle_push_deployment(
        self,
        request: modelregistry_v1_deployment_sync_service_pb2.PushDeploymentRequest
    ) -> modelregistry_v1_deployment_sync_service_pb2.PushDeploymentResponse:
        """Pushs a deployment."""
        deps = self.deps
        response = modelregistry_v1_deployment_sync_service_pb2.PushDeploymentResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('PushDeployment', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'PushDeployment', {'reason': request.reason})
            await deps.repository.save_deployment(request.context.tenant_id, request.deployment)
            response_0 = anomalies_v1_anomaly_feedback_workflow_service_pb2.StartAnomalyFeedbackWorkflowResponse()
            response_1 = modelregistry_v1_registered_model_sync_service_pb2.SyncRegisteredModelsResponse()
            response_2 = documents_v1_document_service_pb2.WatchDocumentsResponse()
            response_3 = customers_v1_household_calculation_service_pb2.SimulateHouseholdResponse()
            callbacks_0: list[
                Callable[
                    [],
                    Awaitable[anomalies_v1_anomaly_feedback_workflow_service_pb2.StartAnomalyFeedbackWorkflowResponse]
                ]
            ] = []
            for item_0 in request.deployment.participants:
                outgoing_0 = anomalies_v1_anomaly_feedback_workflow_service_pb2.StartAnomalyFeedbackWorkflowRequest(
                    context=request.context,
                    details=anomalies_v1_anomaly_feedback_workflow_service_pb2.StartAnomalyFeedbackWorkflowRequest.Details(
                        notify=common_v1_contact_pb2.ContactInfo(
                            name=item_0.contact.name,
                            preferred_channel=item_0.contact.preferred_channel
                        )
                    )
                )
                async def send_0(
                    payload: anomalies_v1_anomaly_feedback_workflow_service_pb2.StartAnomalyFeedbackWorkflowRequest = outgoing_0
                ) -> anomalies_v1_anomaly_feedback_workflow_service_pb2.StartAnomalyFeedbackWorkflowResponse:
                    return await deps.clients.anomalies_anomaly_feedback_workflow.StartAnomalyFeedbackWorkflow(
                        payload,
                        timeout=deps.settings.timeout
                    )
                callbacks_0.append(send_0)
            for callback_0 in callbacks_0:
                response_0 = await callback_0()
            command_1 = DeploymentSyncPushDeployment1Command.model_validate(
                {
                    'context': request.context,
                    'registered_model_audit_etag': request.deployment.audit.etag,
                    'registered_model_audit_updated_by': request.deployment.audit.updated_by,
                    'registered_model_address_country_code': request.deployment.location.country_code
                }
            )
            outgoing_1 = to_deployment_sync_push_deployment1_command(command_1)
            response_1 = await deps.clients.modelregistry_registered_model_sync.SyncRegisteredModels(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = documents_v1_document_service_pb2.WatchDocumentsRequest(
                context=request.context,
                filter=documents_v1_document_service_pb2.WatchDocumentsRequest.Filter(
                    created_after=request.deployment.audit.updated_at,
                    region=response_1.registered_model.address.region
                ),
                since=request.deployment.audit.created_at,
                subscriber=common_v1_contact_pb2.ContactInfo(email=response_1.registered_model.owner.email)
            )
            async for chunk_2 in deps.clients.documents_document.WatchDocuments(
                outgoing_2,
                timeout=deps.settings.timeout
            ):
                response_2 = chunk_2
            async for item_3 in async_messages(request.deployment.participants):
                outgoing_3 = customers_v1_household_calculation_service_pb2.SimulateHouseholdRequest(
                    context=request.context,
                    household=customers_v1_customers_pb2.Household(
                        children=[
                            customers_v1_customers_pb2.Household(
                                children=[
                                    customers_v1_customers_pb2.Household(
                                        audit=common_v1_audit_pb2.AuditInfo(
                                            updated_by=request.deployment.audit.updated_by
                                        ),
                                        location=common_v1_address_pb2.PostalAddress(
                                            region=response_1.registered_model.address.region
                                        ),
                                        manager=identity_v1_refs_pb2.UserRef(
                                            email=item_3.contact.email,
                                            user_id=response_1.registered_model.owner.user_id
                                        )
                                    )
                                ]
                            )
                        ]
                    )
                )
                response_3 = await deps.clients.customers_household_calculation.SimulateHousehold(
                    outgoing_3,
                    timeout=deps.settings.timeout
                )
            returned_1_0 = response_1.result.details
            response.result.details.update(returned_1_0)
            returned_1_1 = response_1.outcome.status
            if returned_1_1:
                response.outcome.status = returned_1_1
            echoed_0 = request.deployment_id
            response.deployment.deployment_id = echoed_0
            echoed_1 = request.deployment.location
            response.deployment.location.CopyFrom(echoed_1)
            return response

    async def handle_resolve_deployment_conflict(
        self,
        request: modelregistry_v1_deployment_sync_service_pb2.ResolveDeploymentConflictRequest
    ) -> modelregistry_v1_deployment_sync_service_pb2.ResolveDeploymentConflictResponse:
        """Resolves a deployment."""
        deps = self.deps
        response = modelregistry_v1_deployment_sync_service_pb2.ResolveDeploymentConflictResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ResolveDeploymentConflict', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ResolveDeploymentConflict',
                {'reason': request.reason}
            )
            await deps.repository.save_deployment(request.context.tenant_id, request.deployment)
            response_0 = modelregistry_v1_model_version_validation_service_pb2.ScoreModelVersionResponse()
            response_1 = modelregistry_v1_model_version_validation_service_pb2.ValidateModelVersionResponse()
            outgoing_0 = modelregistry_v1_model_version_validation_service_pb2.ScoreModelVersionRequest()
            outgoing_0.context.CopyFrom(request.context)
            outgoing_0.details.destination.recipient = request.deployment.location.recipient
            outgoing_0.context.tenant_id = tenant_id.get()
            response_0 = await deps.clients.modelregistry_model_version_validation.ScoreModelVersion(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = modelregistry_v1_model_version_validation_service_pb2.ValidateModelVersionRequest(
                context=request.context,
                model_version=modelregistry_v1_modelregistry_pb2.ModelVersion(
                    subject=customers_v1_refs_pb2.CustomerRef(email=response_0.model_version.subject.email)
                )
            )
            port_1: DeploymentSyncResolveDeploymentConflict1Port = DeploymentSyncResolveDeploymentConflict1Adapter(
                deps.clients.modelregistry_model_version_validation,
                deps.settings.timeout
            )
            response_1 = await port_1.execute(outgoing_1)
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.result.message = returned_0_0
            returned_1_0 = response_1.result.reference_ids
            response.result.reference_ids.extend(returned_1_0)
            returned_1_1 = response_1.result.status
            if returned_1_1:
                response.result.status = returned_1_1
            echoed_0 = request.deployment_id
            response.deployment.deployment_id = echoed_0
            echoed_1 = request.deployment.location
            response.deployment.location.CopyFrom(echoed_1)
            return response

    async def handle_stream_deployment_changes(
        self,
        request: modelregistry_v1_deployment_sync_service_pb2.StreamDeploymentChangesRequest
    ) -> modelregistry_v1_deployment_sync_service_pb2.StreamDeploymentChangesResponse:
        """Exchanges changes of deployments with a peer."""
        deps = self.deps
        response = modelregistry_v1_deployment_sync_service_pb2.StreamDeploymentChangesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('StreamDeploymentChanges', extra={'fields': {'cursor': request.cursor}})
            await deps.repository.audit(
                request.context.tenant_id,
                'StreamDeploymentChanges',
                {'cursor': request.cursor}
            )
            if request.WhichOneof('frame') == 'change':
                await deps.repository.save_deployment(request.context.tenant_id, request.change)
            response_0 = customers_v1_consent_record_validation_service_pb2.ValidateConsentRecordResponse()
            response_1 = lineage_v1_lineage_node_reporting_service_pb2.ShareLineageNodeReportResponse()
            response_2 = modelregistry_v1_registered_model_query_service_pb2.CountRegisteredModelsResponse()
            outgoing_0 = customers_v1_consent_record_validation_service_pb2.ValidateConsentRecordRequest(
                consent_record=customers_v1_customers_pb2.ConsentRecord(
                    sequence=request.ack.sequence,
                    subject=customers_v1_refs_pb2.HouseholdRef(display_name=request.change.organizer.display_name)
                ),
                context=request.context
            )
            steps_0 = [
                partial(
                    deps.clients.customers_consent_record_validation.ValidateConsentRecord,
                    outgoing_0,
                    timeout=deps.settings.timeout
                )
            ]
            results_0 = await run_steps(steps_0)
            response_0 = results_0[-1]
            outgoing_1 = lineage_v1_lineage_node_reporting_service_pb2.ShareLineageNodeReportRequest()
            outgoing_1.context.CopyFrom(request.context)
            if request.WhichOneof('frame') == 'change':
                outgoing_1.details.recipient.email = request.change.organizer.email
            if request.WhichOneof('frame') == 'change':
                outgoing_1.details.variables.update(dict(request.change.metadata))
            response_1 = await deps.clients.lineage_lineage_node_reporting.ShareLineageNodeReport(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = modelregistry_v1_registered_model_query_service_pb2.CountRegisteredModelsRequest(
                context=request.context,
                filter=modelregistry_v1_registered_model_query_service_pb2.CountRegisteredModelsRequest.Filter(
                    region=response_1.lineage_node.location.region
                )
            )
            response_2 = cast(modelregistry_v1_registered_model_query_service_pb2.CountRegisteredModelsResponse, await deps.bus.request(
                'acme.modelregistry.v1.DeploymentSyncService/StreamDeploymentChanges/2', outgoing_2, deps.settings.timeout,
            ))
            returned_0_0 = response_0.consent_record.subject.display_name
            if returned_0_0:
                response.deployment.organizer.display_name = returned_0_0
            returned_1_0 = response_1.lineage_node.audit.created_by
            if returned_1_0:
                response.deployment.audit.created_by = returned_1_0
            returned_1_1 = response_1.lineage_node.audit.etag
            if returned_1_1:
                response.deployment.audit.etag = returned_1_1
            returned_2_0 = response_2.result.correlation_id
            if returned_2_0:
                response.result.correlation_id = returned_2_0
            returned_2_1 = response_2.result.message
            if returned_2_1:
                response.result.message = returned_2_1
            echoed_0 = request.ack.sequence
            response.sequence = echoed_0
            echoed_1 = request.ack.status
            response.result.status = echoed_1
            return response

    async def handle_sync_deployments(
        self,
        request: modelregistry_v1_deployment_sync_service_pb2.SyncDeploymentsRequest
    ) -> modelregistry_v1_deployment_sync_service_pb2.SyncDeploymentsResponse:
        """Syncs a deployment."""
        deps = self.deps
        response = modelregistry_v1_deployment_sync_service_pb2.SyncDeploymentsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SyncDeployments', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'SyncDeployments', {'reason': request.reason})
            await deps.repository.save_deployment(request.context.tenant_id, request.deployment)
            response_0 = customers_v1_customer_query_service_pb2.BrowseCustomersResponse()
            response_1 = metrics_v1_dashboard_sync_service_pb2.PullDashboardsResponse()
            response_2 = identity_v1_user_service_pb2.SearchUsersResponse()
            response_3 = modelregistry_v1_registered_model_validation_service_pb2.ScoreRegisteredModelResponse()
            outgoing_0 = customers_v1_customer_query_service_pb2.BrowseCustomersRequest(
                context=request.context,
                filter=customers_v1_customer_query_service_pb2.BrowseCustomersRequest.Filter(
                    created_after=request.deployment.audit.updated_at,
                    owner_id=request.deployment.organizer.user_id,
                    region=request.deployment.location.region
                )
            )
            outgoing_1 = metrics_v1_dashboard_sync_service_pb2.PullDashboardsRequest(
                context=request.context,
                dashboard=metrics_v1_metrics_pb2.Dashboard(
                    audit=common_v1_audit_pb2.AuditInfo(created_by=request.deployment.audit.created_by),
                    billing_address=common_v1_address_pb2.PostalAddress(
                        country_code=request.deployment.location.country_code,
                        postal_code=request.deployment.location.postal_code
                    )
                )
            )
            response_0, response_1 = await asyncio.gather(
                deps.clients.customers_customer_query.BrowseCustomers(outgoing_0, timeout=deps.settings.timeout),
                deps.clients.metrics_dashboard_sync.PullDashboards(outgoing_1, timeout=deps.settings.timeout),
            )
            fields_2: dict[str, Any] = {
                'context': request.context,
                'filter': {
                    'created_after': response_1.dashboard.audit.created_at,
                    'region': request.deployment.location.region
                }
            }
            outgoing_2 = identity_v1_user_service_pb2.SearchUsersRequest(**fields_2)
            response_2 = await deps.clients.identity_user.SearchUsers(outgoing_2, timeout=deps.settings.timeout)
            for item_3 in request.deployment.participants:
                outgoing_3 = modelregistry_v1_registered_model_validation_service_pb2.ScoreRegisteredModelRequest(
                    context=request.context,
                    details=modelregistry_v1_registered_model_validation_service_pb2.ScoreRegisteredModelRequest.Details(
                        destination=common_v1_address_pb2.PostalAddress(
                            country_code=request.deployment.location.country_code,
                            lines=list(response_1.dashboard.billing_address.lines),
                            locality=request.deployment.location.locality
                        )
                    ),
                    registered_model=modelregistry_v1_modelregistry_pb2.RegisteredModel(
                        owner=identity_v1_refs_pb2.UserRef(email=item_3.contact.email)
                    )
                )
                response_3 = await deps.clients.modelregistry_registered_model_validation.ScoreRegisteredModel(
                    outgoing_3,
                    timeout=deps.settings.timeout
                )
            returned_0_0 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_0)
            returned_0_1 = response_0.result.details
            response.result.details.update(returned_0_1)
            returned_1_0 = response_1.dashboard.audit.created_at
            if returned_1_0.ListFields():
                response.deployment.audit.created_at.MergeFrom(returned_1_0)
            returned_2_0 = response_2.result.status
            if returned_2_0:
                response.result.status = returned_2_0
            echoed_0 = request.deployment_id
            response.deployment.deployment_id = echoed_0
            echoed_1 = request.deployment.location
            response.deployment.location.CopyFrom(echoed_1)
            return response
