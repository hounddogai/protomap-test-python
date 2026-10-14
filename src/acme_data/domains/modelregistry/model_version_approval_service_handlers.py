"""Reusable transport mixin for ModelVersionApprovalService."""

from __future__ import annotations

from collections.abc import AsyncIterator
from collections.abc import Awaitable
from collections.abc import Callable
from typing import Any
from typing import cast
import asyncio
import logging

from google.protobuf.json_format import MessageToJson
from google.protobuf.json_format import Parse
import grpc

from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.customers.v1 import customers_pb2 as customers_v1_customers_pb2
from acme.customers.v1 import preference_calculation_service_pb2 as customers_v1_preference_calculation_service_pb2
from acme.customers.v1 import refs_pb2 as customers_v1_refs_pb2
from acme.documents.v1 import document_service_pb2 as documents_v1_document_service_pb2
from acme.featurestore.v1 import (
    feature_value_approval_service_pb2 as featurestore_v1_feature_value_approval_service_pb2,
)
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.metrics.v1 import metric_alert_notification_service_pb2 as metrics_v1_metric_alert_notification_service_pb2
from acme.modelregistry.v1 import deployment_reporting_service_pb2 as modelregistry_v1_deployment_reporting_service_pb2
from acme.modelregistry.v1 import (
    model_version_approval_service_pb2 as modelregistry_v1_model_version_approval_service_pb2,
)
from acme.modelregistry.v1 import model_version_sync_service_pb2 as modelregistry_v1_model_version_sync_service_pb2
from acme.modelregistry.v1 import modelregistry_pb2 as modelregistry_v1_modelregistry_pb2
from acme.modelregistry.v1 import (
    registered_model_reporting_service_pb2 as modelregistry_v1_registered_model_reporting_service_pb2,
)
from acme.modelregistry.v1 import registered_model_service_pb2 as modelregistry_v1_registered_model_service_pb2

from acme_data.domains.modelregistry.dependencies import Dependencies
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class ModelVersionApprovalServicerHandlers:
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    async def ApproveModelVersion(
        self, request: modelregistry_v1_model_version_approval_service_pb2.ApproveModelVersionRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_model_version_approval_service_pb2.ApproveModelVersionResponse:
        """Approves a model version."""
        return await self.handle_approve_model_version(request)

    @rpc_errors
    async def DelegateModelVersionApproval(
        self, request: modelregistry_v1_model_version_approval_service_pb2.DelegateModelVersionApprovalRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_model_version_approval_service_pb2.DelegateModelVersionApprovalResponse:
        """Delegates a model version."""
        return await self.handle_delegate_model_version_approval(request)

    @rpc_errors
    async def EscalateModelVersion(
        self, request: modelregistry_v1_model_version_approval_service_pb2.EscalateModelVersionRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_model_version_approval_service_pb2.EscalateModelVersionResponse:
        """Escalates a model version."""
        return await self.handle_escalate_model_version(request)

    @rpc_errors
    @retry_transient
    async def GetModelVersionApprovalStatus(
        self, request: modelregistry_v1_model_version_approval_service_pb2.GetModelVersionApprovalStatusRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_model_version_approval_service_pb2.GetModelVersionApprovalStatusResponse:
        """Returns a model version."""
        return await self.handle_get_model_version_approval_status(request)

    @rpc_errors
    async def RecallModelVersion(
        self, request: modelregistry_v1_model_version_approval_service_pb2.RecallModelVersionRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_model_version_approval_service_pb2.RecallModelVersionResponse:
        """Recalls a model version."""
        return await self.handle_recall_model_version(request)

    @rpc_errors
    async def SubmitModelVersion(
        self, request: modelregistry_v1_model_version_approval_service_pb2.SubmitModelVersionRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_model_version_approval_service_pb2.SubmitModelVersionResponse:
        """Submits a model version."""
        return await self.handle_submit_model_version(request)

    async def handle_approve_model_version(
        self,
        request: modelregistry_v1_model_version_approval_service_pb2.ApproveModelVersionRequest
    ) -> modelregistry_v1_model_version_approval_service_pb2.ApproveModelVersionResponse:
        """Approves a model version."""
        deps = self.deps
        response = modelregistry_v1_model_version_approval_service_pb2.ApproveModelVersionResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ApproveModelVersion', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'ApproveModelVersion', {'reason': request.reason})
            await deps.repository.save_model_version(request.context.tenant_id, request.model_version)
            response_0 = modelregistry_v1_registered_model_reporting_service_pb2.ListRegisteredModelReportsResponse()
            outgoing_0 = modelregistry_v1_registered_model_reporting_service_pb2.ListRegisteredModelReportsRequest(
                context=request.context,
                filter=modelregistry_v1_registered_model_reporting_service_pb2.ListRegisteredModelReportsRequest.Filter(
                    created_after=request.details.effective_at,
                    owner_id=request.details.approver.user_id
                )
            )
            response_0 = cast(modelregistry_v1_registered_model_reporting_service_pb2.ListRegisteredModelReportsResponse, await deps.bus.request(
                'acme.modelregistry.v1.ModelVersionApprovalService/ApproveModelVersion/0', outgoing_0, deps.settings.timeout,
            ))
            returned_0_0 = response_0.result.status
            if returned_0_0:
                response.outcome.status = returned_0_0
            returned_0_1 = response_0.result.status
            if returned_0_1:
                response.result.status = returned_0_1
            echoed_0 = request.model_version_id
            response.model_version.model_version_id = echoed_0
            echoed_1 = request.model_version.kind
            response.model_version.kind = echoed_1
            return response

    async def handle_delegate_model_version_approval(
        self,
        request: modelregistry_v1_model_version_approval_service_pb2.DelegateModelVersionApprovalRequest
    ) -> modelregistry_v1_model_version_approval_service_pb2.DelegateModelVersionApprovalResponse:
        """Delegates a model version."""
        deps = self.deps
        response = modelregistry_v1_model_version_approval_service_pb2.DelegateModelVersionApprovalResponse()
        with tenant_scope(request.context.tenant_id):
            log.info(
                'DelegateModelVersionApproval',
                extra={'fields': {'approver_email': request.details.approver_email}}
            )
            await deps.repository.audit(
                request.context.tenant_id,
                'DelegateModelVersionApproval',
                {'approver_email': request.details.approver_email}
            )
            await deps.repository.save_model_version(request.context.tenant_id, request.model_version)
            response_0 = modelregistry_v1_model_version_sync_service_pb2.ResolveModelVersionConflictResponse()
            response_1 = featurestore_v1_feature_value_approval_service_pb2.RejectFeatureValueResponse()
            response_2 = metrics_v1_metric_alert_notification_service_pb2.SubscribeMetricAlertUpdatesResponse()
            response_3 = documents_v1_document_service_pb2.WatchDocumentsResponse()
            outgoing_0 = modelregistry_v1_model_version_sync_service_pb2.ResolveModelVersionConflictRequest(
                context=request.context,
                model_version=modelregistry_v1_modelregistry_pb2.ModelVersion(
                    subject=customers_v1_refs_pb2.CustomerRef(
                        display_name=request.model_version.subject.display_name,
                        email=request.details.approver.email
                    )
                )
            )
            response_0 = await deps.clients.modelregistry_model_version_sync.ResolveModelVersionConflict(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = featurestore_v1_feature_value_approval_service_pb2.RejectFeatureValueRequest(
                context=request.context,
                details=featurestore_v1_feature_value_approval_service_pb2.RejectFeatureValueRequest.Details(
                    approver=identity_v1_refs_pb2.UserRef(display_name=response_0.model_version.subject.display_name)
                )
            )
            method_name_1 = 'RejectFeatureValue'
            response_1 = await getattr(
                deps.clients.featurestore_feature_value_approval,
                method_name_1
            )(outgoing_1, timeout=deps.settings.timeout)
            fields_2: dict[str, Any] = {
                'annotations': dict(request.annotations),
                'context': request.context,
                'details': {'recipient': {'email': request.model_version.subject.email}},
                'reason': request.reason
            }
            outgoing_2 = metrics_v1_metric_alert_notification_service_pb2.SubscribeMetricAlertUpdatesRequest(**fields_2)
            response_2 = await deps.clients.metrics_metric_alert_notification.SubscribeMetricAlertUpdates(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            outgoing_3 = documents_v1_document_service_pb2.WatchDocumentsRequest(
                context=request.context,
                subscriber=common_v1_contact_pb2.ContactInfo(email=request.model_version.subject.email)
            )
            async for chunk_3 in deps.clients.documents_document.WatchDocuments(
                outgoing_3,
                timeout=deps.settings.timeout
            ):
                response_3 = chunk_3
            returned_0_0 = response_0.model_version.attributes
            response.model_version.attributes.update(returned_0_0)
            returned_1_0 = response_1.result.reference_ids
            response.result.reference_ids.extend(returned_1_0)
            returned_1_1 = response_1.result.details
            response.result.details.update(returned_1_1)
            returned_2_0 = response_2.outcome.reference_id
            if returned_2_0:
                response.outcome.reference_id = returned_2_0
            returned_2_1 = response_2.result.status
            if returned_2_1:
                response.outcome.status = returned_2_1
            echoed_0 = request.model_version_id
            response.model_version.model_version_id = echoed_0
            echoed_1 = request.model_version.sequence
            response.model_version.sequence = echoed_1
            return response

    async def handle_escalate_model_version(
        self,
        request: modelregistry_v1_model_version_approval_service_pb2.EscalateModelVersionRequest
    ) -> modelregistry_v1_model_version_approval_service_pb2.EscalateModelVersionResponse:
        """Escalates a model version."""
        deps = self.deps
        response = modelregistry_v1_model_version_approval_service_pb2.EscalateModelVersionResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('EscalateModelVersion', extra={'fields': {'approver_email': request.details.approver_email}})
            await deps.repository.audit(
                request.context.tenant_id,
                'EscalateModelVersion',
                {'approver_email': request.details.approver_email}
            )
            await deps.repository.save_model_version(request.context.tenant_id, request.model_version)
            response_0 = modelregistry_v1_registered_model_reporting_service_pb2.GenerateRegisteredModelReportResponse()
            outgoing_0 = modelregistry_v1_registered_model_reporting_service_pb2.GenerateRegisteredModelReportRequest(
                annotations=dict(request.annotations),
                context=request.context,
                details=modelregistry_v1_registered_model_reporting_service_pb2.GenerateRegisteredModelReportRequest.Details(
                    filters=dict(request.model_version.attributes)
                ),
                reason=request.reason
            )
            document_0 = MessageToJson(outgoing_0, preserving_proto_field_name=True)
            outgoing_0 = Parse(
                document_0,
                modelregistry_v1_registered_model_reporting_service_pb2.GenerateRegisteredModelReportRequest()
            )
            response_0 = await deps.clients.modelregistry_registered_model_reporting.GenerateRegisteredModelReport(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.correlation_id
            if returned_0_0:
                response.result.correlation_id = returned_0_0
            returned_0_1 = response_0.result.details
            response.result.details.update(returned_0_1)
            echoed_0 = request.model_version_id
            response.model_version.model_version_id = echoed_0
            echoed_1 = request.model_version.source
            response.model_version.source = echoed_1
            return response

    async def handle_get_model_version_approval_status(
        self,
        request: modelregistry_v1_model_version_approval_service_pb2.GetModelVersionApprovalStatusRequest
    ) -> modelregistry_v1_model_version_approval_service_pb2.GetModelVersionApprovalStatusResponse:
        """Returns a model version."""
        deps = self.deps
        response = modelregistry_v1_model_version_approval_service_pb2.GetModelVersionApprovalStatusResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('GetModelVersionApprovalStatus', extra={'fields': {'locale': request.context.locale}})
            await deps.repository.audit(
                request.context.tenant_id,
                'GetModelVersionApprovalStatus',
                {'locale': request.context.locale}
            )
            echoed_0 = request.model_version_id
            response.model_version.model_version_id = echoed_0
            return response

    async def handle_recall_model_version(
        self,
        request: modelregistry_v1_model_version_approval_service_pb2.RecallModelVersionRequest
    ) -> modelregistry_v1_model_version_approval_service_pb2.RecallModelVersionResponse:
        """Recalls a model version."""
        deps = self.deps
        response = modelregistry_v1_model_version_approval_service_pb2.RecallModelVersionResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('RecallModelVersion', extra={'fields': {'approver_email': request.details.approver_email}})
            await deps.repository.audit(
                request.context.tenant_id,
                'RecallModelVersion',
                {'approver_email': request.details.approver_email}
            )
            await deps.repository.save_model_version(request.context.tenant_id, request.model_version)
            response_0 = modelregistry_v1_deployment_reporting_service_pb2.GenerateDeploymentReportResponse()
            response_1 = modelregistry_v1_registered_model_service_pb2.CloneRegisteredModelResponse()
            outgoing_0 = modelregistry_v1_deployment_reporting_service_pb2.GenerateDeploymentReportRequest()
            outgoing_0.context.CopyFrom(request.context)
            outgoing_0.reason = request.reason
            merged_0 = modelregistry_v1_deployment_reporting_service_pb2.GenerateDeploymentReportRequest()
            merged_0.MergeFrom(outgoing_0)
            outgoing_0.CopyFrom(merged_0)
            response_0 = await deps.clients.modelregistry_deployment_reporting.GenerateDeploymentReport(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            requests_1: list[modelregistry_v1_registered_model_service_pb2.CloneRegisteredModelRequest] = []
            for item_1 in request.model_version.measurements:
                outgoing_1 = modelregistry_v1_registered_model_service_pb2.CloneRegisteredModelRequest(
                    context=request.context,
                    registered_model=modelregistry_v1_modelregistry_pb2.RegisteredModel(
                        dimensions=modelregistry_v1_modelregistry_pb2.RegisteredModelDimensions(unit=item_1.unit)
                    )
                )
                requests_1.append(outgoing_1)
            replies_1 = await asyncio.gather(*(
                deps.clients.modelregistry_registered_model.CloneRegisteredModel(
                    entry,
                    timeout=deps.settings.timeout
                ) for entry in requests_1
            ))
            if replies_1:
                response_1 = replies_1[-1]
            returned_0_0 = response_0.result.details
            response.result.details.update(returned_0_0)
            echoed_0 = request.model_version_id
            response.model_version.model_version_id = echoed_0
            echoed_1 = request.model_version.sequence
            response.model_version.sequence = echoed_1
            return response

    async def handle_submit_model_version(
        self,
        request: modelregistry_v1_model_version_approval_service_pb2.SubmitModelVersionRequest
    ) -> modelregistry_v1_model_version_approval_service_pb2.SubmitModelVersionResponse:
        """Submits a model version."""
        deps = self.deps
        response = modelregistry_v1_model_version_approval_service_pb2.SubmitModelVersionResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SubmitModelVersion', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'SubmitModelVersion', {'reason': request.reason})
            await deps.repository.save_model_version(request.context.tenant_id, request.model_version)
            response_0 = customers_v1_preference_calculation_service_pb2.CalculatePreferenceResponse()
            callbacks_0: list[
                Callable[[], Awaitable[customers_v1_preference_calculation_service_pb2.CalculatePreferenceResponse]]
            ] = []
            for item_0 in request.model_version.measurements:
                outgoing_0 = customers_v1_preference_calculation_service_pb2.CalculatePreferenceRequest(
                    context=request.context,
                    preference=customers_v1_customers_pb2.Preference(
                        audit=common_v1_audit_pb2.AuditInfo(created_at=item_0.observed_at),
                        owner=identity_v1_refs_pb2.UserRef(
                            display_name=request.details.approver.display_name,
                            email=request.details.approver.email,
                            user_id=request.details.approver.user_id
                        )
                    )
                )
                async def send_0(
                    payload: customers_v1_preference_calculation_service_pb2.CalculatePreferenceRequest = outgoing_0
                ) -> customers_v1_preference_calculation_service_pb2.CalculatePreferenceResponse:
                    return await deps.clients.customers_preference_calculation.CalculatePreference(
                        payload,
                        timeout=deps.settings.timeout
                    )
                callbacks_0.append(send_0)
            for callback_0 in callbacks_0:
                response_0 = await callback_0()
            echoed_0 = request.model_version_id
            response.model_version.model_version_id = echoed_0
            echoed_1 = request.model_version.occurred_at
            response.model_version.occurred_at.CopyFrom(echoed_1)
            return response
