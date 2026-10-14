"""Reusable transport mixin for RegisteredModelLifecycleService."""

from __future__ import annotations

from collections.abc import AsyncIterator
from functools import partial
from typing import Any
from typing import cast
import logging

from google.protobuf.json_format import MessageToJson
from google.protobuf.json_format import Parse
import grpc

from acme.anomalies.v1 import anomalies_pb2 as anomalies_v1_anomalies_pb2
from acme.anomalies.v1 import (
    anomaly_feedback_approval_service_pb2 as anomalies_v1_anomaly_feedback_approval_service_pb2,
)
from acme.anomalies.v1 import anomaly_workflow_service_pb2 as anomalies_v1_anomaly_workflow_service_pb2
from acme.anomalies.v1 import refs_pb2 as anomalies_v1_refs_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.customers.v1 import customers_pb2 as customers_v1_customers_pb2
from acme.customers.v1 import preference_validation_service_pb2 as customers_v1_preference_validation_service_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.identity.v1 import user_query_service_pb2 as identity_v1_user_query_service_pb2
from acme.identity.v1 import user_query_service_pb2_grpc as identity_v1_user_query_service_pb2_grpc
from acme.lineage.v1 import lineage_edge_import_service_pb2 as lineage_v1_lineage_edge_import_service_pb2
from acme.lineage.v1 import lineage_node_sync_service_pb2 as lineage_v1_lineage_node_sync_service_pb2
from acme.metrics.v1 import dashboard_export_service_pb2 as metrics_v1_dashboard_export_service_pb2
from acme.metrics.v1 import metric_series_export_service_pb2 as metrics_v1_metric_series_export_service_pb2
from acme.modelregistry.v1 import deployment_sync_service_pb2 as modelregistry_v1_deployment_sync_service_pb2
from acme.modelregistry.v1 import (
    model_version_reporting_service_pb2 as modelregistry_v1_model_version_reporting_service_pb2,
)
from acme.modelregistry.v1 import modelregistry_pb2 as modelregistry_v1_modelregistry_pb2
from acme.modelregistry.v1 import (
    registered_model_lifecycle_service_pb2 as modelregistry_v1_registered_model_lifecycle_service_pb2,
)
from acme.modelregistry.v1 import (
    registered_model_reporting_service_pb2 as modelregistry_v1_registered_model_reporting_service_pb2,
)
from acme.modelregistry.v1 import (
    registered_model_sync_service_pb2 as modelregistry_v1_registered_model_sync_service_pb2,
)

from acme_data.domains.modelregistry import hooks
from acme_data.domains.modelregistry.adapters import RegisteredModelLifecycleTerminateRegisteredModel0Adapter
from acme_data.domains.modelregistry.adapters import RegisteredModelLifecycleTerminateRegisteredModel0Port
from acme_data.domains.modelregistry.adapters import RegisteredModelLifecycleTerminateRegisteredModel2Adapter
from acme_data.domains.modelregistry.dependencies import Dependencies
from acme_data.domains.modelregistry.models import RegisteredModelLifecycleRenewRegisteredModel1Command
from acme_data.domains.modelregistry.models import to_registered_model_lifecycle_renew_registered_model1_command
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import run_steps
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_id
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class RegisteredModelLifecycleServicerHandlers:
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    async def ActivateRegisteredModel(
        self, request: modelregistry_v1_registered_model_lifecycle_service_pb2.ActivateRegisteredModelRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_registered_model_lifecycle_service_pb2.ActivateRegisteredModelResponse:
        """Activates a registered model."""
        return await self.handle_activate_registered_model(request)

    @rpc_errors
    async def ExpireRegisteredModel(
        self, request: modelregistry_v1_registered_model_lifecycle_service_pb2.ExpireRegisteredModelRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_registered_model_lifecycle_service_pb2.ExpireRegisteredModelResponse:
        """Expires a registered model."""
        return await self.handle_expire_registered_model(request)

    @rpc_errors
    @retry_transient
    async def GetRegisteredModelLifecycle(
        self, request: modelregistry_v1_registered_model_lifecycle_service_pb2.GetRegisteredModelLifecycleRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_registered_model_lifecycle_service_pb2.GetRegisteredModelLifecycleResponse:
        """Returns a registered model."""
        return await self.handle_get_registered_model_lifecycle(request)

    @rpc_errors
    async def ReinstateRegisteredModel(
        self, request: modelregistry_v1_registered_model_lifecycle_service_pb2.ReinstateRegisteredModelRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_registered_model_lifecycle_service_pb2.ReinstateRegisteredModelResponse:
        """Reinstates a registered model."""
        return await self.handle_reinstate_registered_model(request)

    @rpc_errors
    async def RenewRegisteredModel(
        self, request: modelregistry_v1_registered_model_lifecycle_service_pb2.RenewRegisteredModelRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_registered_model_lifecycle_service_pb2.RenewRegisteredModelResponse:
        """Renews a registered model."""
        return await self.handle_renew_registered_model(request)

    @rpc_errors
    async def ScheduleRegisteredModelExpiry(
        self, request: modelregistry_v1_registered_model_lifecycle_service_pb2.ScheduleRegisteredModelExpiryRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_registered_model_lifecycle_service_pb2.ScheduleRegisteredModelExpiryResponse:
        """Schedules a registered model."""
        return await self.handle_schedule_registered_model_expiry(request)

    @rpc_errors
    async def SuspendRegisteredModel(
        self, request: modelregistry_v1_registered_model_lifecycle_service_pb2.SuspendRegisteredModelRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_registered_model_lifecycle_service_pb2.SuspendRegisteredModelResponse:
        """Suspends a registered model."""
        return await self.handle_suspend_registered_model(request)

    @rpc_errors
    async def TerminateRegisteredModel(
        self, request: modelregistry_v1_registered_model_lifecycle_service_pb2.TerminateRegisteredModelRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_registered_model_lifecycle_service_pb2.TerminateRegisteredModelResponse:
        """Terminates a registered model."""
        return await self.handle_terminate_registered_model(request)

    async def handle_activate_registered_model(
        self,
        request: modelregistry_v1_registered_model_lifecycle_service_pb2.ActivateRegisteredModelRequest
    ) -> modelregistry_v1_registered_model_lifecycle_service_pb2.ActivateRegisteredModelResponse:
        """Activates a registered model."""
        deps = self.deps
        response = modelregistry_v1_registered_model_lifecycle_service_pb2.ActivateRegisteredModelResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ActivateRegisteredModel', extra={'fields': {'reason_code': request.details.reason_code}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ActivateRegisteredModel',
                {'reason_code': request.details.reason_code}
            )
            response_0 = modelregistry_v1_deployment_sync_service_pb2.PullDeploymentsResponse()
            response_1 = modelregistry_v1_registered_model_reporting_service_pb2.GenerateRegisteredModelReportResponse()
            response_2 = customers_v1_preference_validation_service_pb2.ExplainPreferenceDecisionResponse()
            outgoing_0 = modelregistry_v1_deployment_sync_service_pb2.PullDeploymentsRequest(
                context=request.context,
                deployment=modelregistry_v1_modelregistry_pb2.Deployment(
                    participants=[
                        modelregistry_v1_modelregistry_pb2.DeploymentParticipant(
                            contact=common_v1_contact_pb2.ContactInfo(
                                email=request.details.notify_contact.email,
                                name=request.details.notify_contact.name,
                                phone=request.details.notify_contact.phone
                            )
                        )
                    ]
                )
            )
            response_0 = cast(modelregistry_v1_deployment_sync_service_pb2.PullDeploymentsResponse, await deps.bus.request(
                'acme.modelregistry.v1.RegisteredModelLifecycleService/ActivateRegisteredModel/0', outgoing_0, deps.settings.timeout,
            ))
            outgoing_1 = modelregistry_v1_registered_model_reporting_service_pb2.GenerateRegisteredModelReportRequest(
                annotations=dict(request.annotations),
                context=request.context,
                details=modelregistry_v1_registered_model_reporting_service_pb2.GenerateRegisteredModelReportRequest.Details(
                    period=response_0.deployment.window
                ),
                reason=request.reason,
                registered_model_id=request.registered_model_id
            )
            response_1 = await deps.clients.modelregistry_registered_model_reporting.GenerateRegisteredModelReport(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = customers_v1_preference_validation_service_pb2.ExplainPreferenceDecisionRequest(
                context=request.context,
                details=customers_v1_preference_validation_service_pb2.ExplainPreferenceDecisionRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(
                        preferred_channel=request.details.notify_contact.preferred_channel
                    )
                ),
                preference=customers_v1_customers_pb2.Preference(
                    audit=common_v1_audit_pb2.AuditInfo(created_at=response_0.deployment.audit.created_at),
                    owner=identity_v1_refs_pb2.UserRef(
                        email=response_0.deployment.organizer.email,
                        user_id=response_0.deployment.organizer.user_id
                    )
                )
            )
            method_name_2 = 'ExplainPreferenceDecision'
            response_2 = await getattr(
                deps.clients.customers_preference_validation,
                method_name_2
            )(outgoing_2, timeout=deps.settings.timeout)
            returned_0_0 = response_0.deployment.organizer.display_name
            if returned_0_0:
                response.registered_model.owner.display_name = returned_0_0
            returned_1_0 = response_1.result.message
            if returned_1_0:
                response.outcome.message = returned_1_0
            returned_2_0 = response_2.preference.audit.etag
            if returned_2_0:
                response.registered_model.audit.etag = returned_2_0
            echoed_0 = request.registered_model_id
            response.registered_model.registered_model_id = echoed_0
            echoed_1 = request.details.effective_at
            response.outcome.effective_at.CopyFrom(echoed_1)
            return response

    async def handle_expire_registered_model(
        self,
        request: modelregistry_v1_registered_model_lifecycle_service_pb2.ExpireRegisteredModelRequest
    ) -> modelregistry_v1_registered_model_lifecycle_service_pb2.ExpireRegisteredModelResponse:
        """Expires a registered model."""
        deps = self.deps
        response = modelregistry_v1_registered_model_lifecycle_service_pb2.ExpireRegisteredModelResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ExpireRegisteredModel', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'ExpireRegisteredModel', {'reason': request.reason})
            response_0 = customers_v1_preference_validation_service_pb2.NormalizePreferenceResponse()
            fields_0: dict[str, Any] = {
                'context': request.context,
                'details': {
                    'contact': {
                        'email': request.details.notify_contact.email,
                        'preferred_channel': request.details.notify_contact.preferred_channel
                    }
                }
            }
            outgoing_0 = customers_v1_preference_validation_service_pb2.NormalizePreferenceRequest(**fields_0)
            response_0 = await deps.clients.customers_preference_validation.NormalizePreference(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.preference.audit.created_at
            if returned_0_0.ListFields():
                response.registered_model.audit.created_at.MergeFrom(returned_0_0)
            echoed_0 = request.registered_model_id
            response.registered_model.registered_model_id = echoed_0
            echoed_1 = request.details.effective_at
            response.outcome.effective_at.CopyFrom(echoed_1)
            return response

    async def handle_get_registered_model_lifecycle(
        self,
        request: modelregistry_v1_registered_model_lifecycle_service_pb2.GetRegisteredModelLifecycleRequest
    ) -> modelregistry_v1_registered_model_lifecycle_service_pb2.GetRegisteredModelLifecycleResponse:
        """Returns a registered model."""
        deps = self.deps
        response = modelregistry_v1_registered_model_lifecycle_service_pb2.GetRegisteredModelLifecycleResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('GetRegisteredModelLifecycle', extra={'fields': {'domain': 'modelregistry'}})
            await deps.repository.audit(request.context.tenant_id, 'GetRegisteredModelLifecycle', {})
            response_0 = lineage_v1_lineage_edge_import_service_pb2.ListLineageEdgeImportsResponse()
            outgoing_0 = lineage_v1_lineage_edge_import_service_pb2.ListLineageEdgeImportsRequest(
                context=request.context,
                filter=lineage_v1_lineage_edge_import_service_pb2.ListLineageEdgeImportsRequest.Filter(
                    created_after=request.context.deadline,
                    labels=dict(request.context.baggage),
                    owner_id=request.registered_model_id
                )
            )
            response_0 = await deps.clients.lineage_lineage_edge_import.ListLineageEdgeImports(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_0)
            echoed_0 = request.registered_model_id
            response.registered_model.registered_model_id = echoed_0
            return response

    async def handle_reinstate_registered_model(
        self,
        request: modelregistry_v1_registered_model_lifecycle_service_pb2.ReinstateRegisteredModelRequest
    ) -> modelregistry_v1_registered_model_lifecycle_service_pb2.ReinstateRegisteredModelResponse:
        """Reinstates a registered model."""
        deps = self.deps
        response = modelregistry_v1_registered_model_lifecycle_service_pb2.ReinstateRegisteredModelResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ReinstateRegisteredModel', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ReinstateRegisteredModel',
                {'reason': request.reason}
            )
            response_0 = anomalies_v1_anomaly_workflow_service_pb2.StartAnomalyWorkflowResponse()
            response_1 = modelregistry_v1_registered_model_sync_service_pb2.PushRegisteredModelResponse()
            response_2 = modelregistry_v1_model_version_reporting_service_pb2.ListModelVersionReportsResponse()
            outgoing_0 = anomalies_v1_anomaly_workflow_service_pb2.StartAnomalyWorkflowRequest(
                anomaly=anomalies_v1_anomalies_pb2.Anomaly(
                    assignee=identity_v1_refs_pb2.UserRef(email=request.details.notify_contact.email)
                ),
                context=request.context,
                details=anomalies_v1_anomaly_workflow_service_pb2.StartAnomalyWorkflowRequest.Details(
                    notify=common_v1_contact_pb2.ContactInfo(
                        email=request.details.new_owner.email,
                        name=request.details.notify_contact.name
                    )
                )
            )
            document_0 = MessageToJson(outgoing_0, preserving_proto_field_name=True)
            outgoing_0 = Parse(document_0, anomalies_v1_anomaly_workflow_service_pb2.StartAnomalyWorkflowRequest())
            response_0 = await deps.clients.anomalies_anomaly_workflow.StartAnomalyWorkflow(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = modelregistry_v1_registered_model_sync_service_pb2.PushRegisteredModelRequest()
            outgoing_1.context.CopyFrom(request.context)
            outgoing_1.registered_model.audit.created_by = response_0.anomaly.audit.created_by
            outgoing_1.registered_model.owner.user_id = request.details.new_owner.user_id
            outgoing_1.registered_model.audit.updated_by = response_0.anomaly.audit.updated_by
            merged_1 = modelregistry_v1_registered_model_sync_service_pb2.PushRegisteredModelRequest()
            merged_1.MergeFrom(outgoing_1)
            outgoing_1.CopyFrom(merged_1)
            response_1 = await deps.clients.modelregistry_registered_model_sync.PushRegisteredModel(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = modelregistry_v1_model_version_reporting_service_pb2.ListModelVersionReportsRequest()
            outgoing_2.context.CopyFrom(request.context)
            if response_1.registered_model.WhichOneof('locator') == 'address':
                outgoing_2.filter.region = response_1.registered_model.address.region
            response_2 = await deps.clients.modelregistry_model_version_reporting.ListModelVersionReports(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.anomaly.customer.display_name
            if returned_0_0:
                response.registered_model.owner.display_name = returned_0_0
            returned_1_0 = response_1.registered_model.registered_model_id
            if returned_1_0:
                response.registered_model.registered_model_id = returned_1_0
            returned_2_0 = response_2.result.status
            if returned_2_0:
                response.outcome.status = returned_2_0
            returned_2_1 = response_2.result.reference_ids
            response.result.reference_ids.extend(returned_2_1)
            echoed_0 = request.details.effective_at
            response.outcome.effective_at.CopyFrom(echoed_0)
            echoed_1 = request.details.notify_contact.email
            response.registered_model.owner.email = echoed_1
            return response

    async def handle_renew_registered_model(
        self,
        request: modelregistry_v1_registered_model_lifecycle_service_pb2.RenewRegisteredModelRequest
    ) -> modelregistry_v1_registered_model_lifecycle_service_pb2.RenewRegisteredModelResponse:
        """Renews a registered model."""
        deps = self.deps
        response = modelregistry_v1_registered_model_lifecycle_service_pb2.RenewRegisteredModelResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('RenewRegisteredModel', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'RenewRegisteredModel', {'reason': request.reason})
            response_0 = identity_v1_user_query_service_pb2.PeekUserResponse()
            response_1 = identity_v1_user_query_service_pb2.ResolveUsersResponse()
            outgoing_0 = identity_v1_user_query_service_pb2.PeekUserRequest(
                context=request.context,
                user_id=request.details.new_owner.user_id
            )
            registered_0 = cast(
                identity_v1_user_query_service_pb2_grpc.UserQueryServiceStub,
                deps.clients.registry['acme.identity.v1.UserQueryService']
            )
            response_0 = await registered_0.PeekUser(outgoing_0, timeout=deps.settings.timeout)
            command_1 = RegisteredModelLifecycleRenewRegisteredModel1Command(context=request.context)
            outgoing_1 = to_registered_model_lifecycle_renew_registered_model1_command(command_1)
            response_1 = await deps.clients.identity_user_query.ResolveUsers(outgoing_1, timeout=deps.settings.timeout)
            returned_0_0 = response_0.result.details
            response.result.details.update(returned_0_0)
            returned_1_0 = response_1.result.reference_ids
            response.result.reference_ids.extend(returned_1_0)
            returned_1_1 = response_1.result.message
            if returned_1_1:
                response.outcome.message = returned_1_1
            echoed_0 = request.registered_model_id
            response.registered_model.registered_model_id = echoed_0
            echoed_1 = request.details.effective_at
            response.outcome.effective_at.CopyFrom(echoed_1)
            return response

    async def handle_schedule_registered_model_expiry(
        self,
        request: modelregistry_v1_registered_model_lifecycle_service_pb2.ScheduleRegisteredModelExpiryRequest
    ) -> modelregistry_v1_registered_model_lifecycle_service_pb2.ScheduleRegisteredModelExpiryResponse:
        """Schedules a registered model."""
        deps = self.deps
        response = modelregistry_v1_registered_model_lifecycle_service_pb2.ScheduleRegisteredModelExpiryResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ScheduleRegisteredModelExpiry', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ScheduleRegisteredModelExpiry',
                {'reason': request.reason}
            )
            await deps.repository.save_registered_model(request.context.tenant_id, request.registered_model)
            response_0 = anomalies_v1_anomaly_feedback_approval_service_pb2.ListPendingAnomalyFeedbacksResponse()
            response_1 = anomalies_v1_anomaly_workflow_service_pb2.CancelAnomalyWorkflowResponse()
            outgoing_0 = anomalies_v1_anomaly_feedback_approval_service_pb2.ListPendingAnomalyFeedbacksRequest()
            outgoing_0.context.CopyFrom(request.context)
            if request.registered_model.WhichOneof('locator') == 'address':
                outgoing_0.filter.region = request.registered_model.address.region
            response_0 = await deps.clients.anomalies_anomaly_feedback_approval.ListPendingAnomalyFeedbacks(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = anomalies_v1_anomaly_workflow_service_pb2.CancelAnomalyWorkflowRequest(
                anomaly=anomalies_v1_anomalies_pb2.Anomaly(
                    audit=common_v1_audit_pb2.AuditInfo(
                        created_by=request.registered_model.audit.created_by,
                        updated_at=request.registered_model.audit.updated_at
                    ),
                    customer=anomalies_v1_refs_pb2.DetectorRef(display_name=request.registered_model.owner.display_name)
                ),
                context=request.context,
                details=anomalies_v1_anomaly_workflow_service_pb2.CancelAnomalyWorkflowRequest.Details(
                    notify=common_v1_contact_pb2.ContactInfo(email=request.details.notify.email)
                )
            )
            send_1 = partial(
                deps.clients.anomalies_anomaly_workflow.CancelAnomalyWorkflow,
                timeout=deps.settings.timeout
            )
            response_1 = await send_1(outgoing_1)
            returned_0_0 = response_0.result.correlation_id
            if returned_0_0:
                response.result.correlation_id = returned_0_0
            returned_1_0 = response_1.result.reference_ids
            response.result.reference_ids.extend(returned_1_0)
            echoed_0 = request.registered_model_id
            response.registered_model.registered_model_id = echoed_0
            echoed_1 = request.registered_model.name
            response.registered_model.name = echoed_1
            return response

    async def handle_suspend_registered_model(
        self,
        request: modelregistry_v1_registered_model_lifecycle_service_pb2.SuspendRegisteredModelRequest
    ) -> modelregistry_v1_registered_model_lifecycle_service_pb2.SuspendRegisteredModelResponse:
        """Suspends a registered model."""
        deps = self.deps
        response = modelregistry_v1_registered_model_lifecycle_service_pb2.SuspendRegisteredModelResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SuspendRegisteredModel', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'SuspendRegisteredModel', {'reason': request.reason})
            response_0 = modelregistry_v1_model_version_reporting_service_pb2.ShareModelVersionReportResponse()
            response_1 = lineage_v1_lineage_node_sync_service_pb2.SyncLineageNodesResponse()
            outgoing_0 = modelregistry_v1_model_version_reporting_service_pb2.ShareModelVersionReportRequest(
                context=request.context,
                details=modelregistry_v1_model_version_reporting_service_pb2.ShareModelVersionReportRequest.Details(
                    recipient=common_v1_contact_pb2.ContactInfo(
                        preferred_channel=request.details.notify_contact.preferred_channel
                    )
                )
            )
            response_0 = await hooks.registered_model_lifecycle_suspend_registered_model0(
                deps.clients.modelregistry_model_version_reporting,
                outgoing_0,
                deps.settings.timeout
            )
            outgoing_1 = lineage_v1_lineage_node_sync_service_pb2.SyncLineageNodesRequest()
            outgoing_1.context.CopyFrom(request.context)
            field_1_1_part_1 = outgoing_1.lineage_node.children.add()
            field_1_1_part_2 = field_1_1_part_1.children.add()
            field_1_1_part_2.manager.user_id = request.details.new_owner.user_id
            field_1_2_part_1 = outgoing_1.lineage_node.children.add()
            field_1_2_part_2 = field_1_2_part_1.children.add()
            field_1_2_part_2.manager.email = request.details.new_owner.email
            field_1_3_part_1 = outgoing_1.lineage_node.children.add()
            field_1_3_part_1.manager.display_name = request.details.new_owner.display_name
            outgoing_1.lineage_node.manager.display_name = response_0.model_version.subject.display_name
            outgoing_1.context.tenant_id = tenant_id.get()
            response_1 = await deps.clients.lineage_lineage_node_sync.SyncLineageNodes(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.model_version.subject.email
            if returned_0_0:
                response.registered_model.owner.email = returned_0_0
            returned_1_0 = response_1.outcome.next_steps
            response.outcome.next_steps.extend(returned_1_0)
            echoed_0 = request.registered_model_id
            response.registered_model.registered_model_id = echoed_0
            echoed_1 = request.details.effective_at
            response.outcome.effective_at.CopyFrom(echoed_1)
            return response

    async def handle_terminate_registered_model(
        self,
        request: modelregistry_v1_registered_model_lifecycle_service_pb2.TerminateRegisteredModelRequest
    ) -> modelregistry_v1_registered_model_lifecycle_service_pb2.TerminateRegisteredModelResponse:
        """Terminates a registered model."""
        deps = self.deps
        response = modelregistry_v1_registered_model_lifecycle_service_pb2.TerminateRegisteredModelResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('TerminateRegisteredModel', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'TerminateRegisteredModel',
                {'reason': request.reason}
            )
            response_0 = metrics_v1_metric_series_export_service_pb2.ShareMetricSeriesExportResponse()
            response_1 = metrics_v1_dashboard_export_service_pb2.ShareDashboardExportResponse()
            response_2 = modelregistry_v1_registered_model_sync_service_pb2.ReconcileRegisteredModelsResponse()
            response_3 = customers_v1_preference_validation_service_pb2.CheckPreferenceEligibilityResponse()
            outgoing_0 = metrics_v1_metric_series_export_service_pb2.ShareMetricSeriesExportRequest(
                context=request.context,
                details=metrics_v1_metric_series_export_service_pb2.ShareMetricSeriesExportRequest.Details(
                    recipient=common_v1_contact_pb2.ContactInfo(name=request.details.notify_contact.name)
                )
            )
            port_0: RegisteredModelLifecycleTerminateRegisteredModel0Port = RegisteredModelLifecycleTerminateRegisteredModel0Adapter(
                deps.clients.metrics_metric_series_export,
                deps.settings.timeout
            )
            response_0 = await port_0.execute(outgoing_0)
            outgoing_1 = metrics_v1_dashboard_export_service_pb2.ShareDashboardExportRequest(
                context=request.context,
                details=metrics_v1_dashboard_export_service_pb2.ShareDashboardExportRequest.Details(
                    recipient=common_v1_contact_pb2.ContactInfo(
                        email=request.details.new_owner.email,
                        phone=request.details.notify_contact.phone
                    )
                )
            )
            steps_1 = [
                partial(
                    deps.clients.metrics_dashboard_export.ShareDashboardExport,
                    outgoing_1,
                    timeout=deps.settings.timeout
                )
            ]
            results_1 = await run_steps(steps_1)
            response_1 = results_1[-1]
            outgoing_2 = modelregistry_v1_registered_model_sync_service_pb2.ReconcileRegisteredModelsRequest(
                context=request.context,
                registered_model=modelregistry_v1_modelregistry_pb2.RegisteredModel(
                    dimensions=modelregistry_v1_modelregistry_pb2.RegisteredModelDimensions(
                        unit=response_0.metric_series.dimensions.unit
                    )
                )
            )
            response_2 = await RegisteredModelLifecycleTerminateRegisteredModel2Adapter(
                deps.clients.modelregistry_registered_model_sync,
                deps.settings.timeout
            )(outgoing_2)
            outgoing_3 = customers_v1_preference_validation_service_pb2.CheckPreferenceEligibilityRequest(
                context=request.context,
                details=customers_v1_preference_validation_service_pb2.CheckPreferenceEligibilityRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(
                        preferred_channel=request.details.notify_contact.preferred_channel
                    )
                ),
                preference=customers_v1_customers_pb2.Preference(
                    audit=common_v1_audit_pb2.AuditInfo(updated_by=response_2.registered_model.audit.updated_by),
                    owner=identity_v1_refs_pb2.UserRef(display_name=response_1.dashboard.counterparty.display_name)
                )
            )
            response_3 = cast(customers_v1_preference_validation_service_pb2.CheckPreferenceEligibilityResponse, await deps.bus.request(
                'acme.modelregistry.v1.RegisteredModelLifecycleService/TerminateRegisteredModel/3', outgoing_3, deps.settings.timeout,
            ))
            returned_0_0 = response_0.metric_series.specs
            response.registered_model.specs.update(returned_0_0)
            returned_0_1 = response_0.outcome.status
            if returned_0_1:
                response.outcome.status = returned_0_1
            returned_1_0 = response_1.outcome.message
            if returned_1_0:
                response.outcome.message = returned_1_0
            returned_2_0 = response_2.result.details
            response.result.details.update(returned_2_0)
            returned_3_0 = response_3.outcome.message
            if returned_3_0:
                response.outcome.message = returned_3_0
            returned_3_1 = response_3.preference.audit.created_at
            if returned_3_1.ListFields():
                response.registered_model.audit.created_at.MergeFrom(returned_3_1)
            echoed_0 = request.registered_model_id
            response.registered_model.registered_model_id = echoed_0
            echoed_1 = request.details.effective_at
            response.outcome.effective_at.CopyFrom(echoed_1)
            return response
