"""Application workflow for RegisteredModel Approval."""

from __future__ import annotations

from functools import partial
from typing import cast
import logging

from google.protobuf.any_pb2 import Any as AnyMessage
from google.protobuf.json_format import MessageToJson
from google.protobuf.json_format import Parse

from acme.banking.v1 import bank_account_query_service_pb2 as banking_v1_bank_account_query_service_pb2
from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.customers.v1 import household_query_service_pb2 as customers_v1_household_query_service_pb2
from acme.customers.v1 import preference_validation_service_pb2 as customers_v1_preference_validation_service_pb2
from acme.customers.v1 import refs_pb2 as customers_v1_refs_pb2
from acme.datasets.v1 import refs_pb2 as datasets_v1_refs_pb2
from acme.documents.v1 import document_validation_service_pb2 as documents_v1_document_validation_service_pb2
from acme.featurestore.v1 import feature_value_sync_service_pb2 as featurestore_v1_feature_value_sync_service_pb2
from acme.featurestore.v1 import featurestore_pb2 as featurestore_v1_featurestore_pb2
from acme.lineage.v1 import lineage_edge_sync_service_pb2 as lineage_v1_lineage_edge_sync_service_pb2
from acme.lineage.v1 import lineage_pb2 as lineage_v1_lineage_pb2
from acme.metrics.v1 import metric_alert_notification_service_pb2 as metrics_v1_metric_alert_notification_service_pb2
from acme.modelregistry.v1 import deployment_sync_service_pb2 as modelregistry_v1_deployment_sync_service_pb2
from acme.modelregistry.v1 import (
    model_version_reporting_service_pb2 as modelregistry_v1_model_version_reporting_service_pb2,
)
from acme.modelregistry.v1 import model_version_sync_service_pb2 as modelregistry_v1_model_version_sync_service_pb2
from acme.modelregistry.v1 import modelregistry_pb2 as modelregistry_v1_modelregistry_pb2
from acme.modelregistry.v1 import (
    registered_model_approval_service_pb2 as modelregistry_v1_registered_model_approval_service_pb2,
)
from acme.modelregistry.v1 import (
    registered_model_lifecycle_service_pb2 as modelregistry_v1_registered_model_lifecycle_service_pb2,
)
from acme.modelregistry.v1 import (
    registered_model_reporting_service_pb2 as modelregistry_v1_registered_model_reporting_service_pb2,
)
from acme.modelregistry.v1 import (
    registered_model_sync_service_pb2 as modelregistry_v1_registered_model_sync_service_pb2,
)
from acme.notifications.v1 import notification_service_pb2 as notifications_v1_notification_service_pb2
from acme.notifications.v1 import notifications_pb2 as notifications_v1_notifications_pb2
from acme.notifications.v1 import refs_pb2 as notifications_v1_refs_pb2

from acme_data.domains.modelregistry import hooks
from acme_data.domains.modelregistry.adapters import RegisteredModelApprovalRecallRegisteredModel0Adapter
from acme_data.domains.modelregistry.adapters import RegisteredModelApprovalRecallRegisteredModel0Port
from acme_data.domains.modelregistry.adapters import RegisteredModelApprovalRejectRegisteredModel0Adapter
from acme_data.domains.modelregistry.dependencies import Dependencies
from acme_data.domains.modelregistry.models import RegisteredModelApprovalCommentRegisteredModelApproval1Command
from acme_data.domains.modelregistry.models import RegisteredModelApprovalCommentRegisteredModelApproval2Command
from acme_data.domains.modelregistry.models import (
    to_registered_model_approval_comment_registered_model_approval1_command,
)
from acme_data.domains.modelregistry.models import (
    to_registered_model_approval_comment_registered_model_approval2_command,
)
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import run_steps
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class RegisteredModelApprovalServicerWorkflow:
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    async def handle_approve_registered_model(
        self,
        request: modelregistry_v1_registered_model_approval_service_pb2.ApproveRegisteredModelRequest
    ) -> modelregistry_v1_registered_model_approval_service_pb2.ApproveRegisteredModelResponse:
        """Approves a registered model."""
        deps = self.deps
        response = modelregistry_v1_registered_model_approval_service_pb2.ApproveRegisteredModelResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ApproveRegisteredModel', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'ApproveRegisteredModel', {'reason': request.reason})
            await deps.repository.save_registered_model(request.context.tenant_id, request.registered_model)
            response_0 = modelregistry_v1_registered_model_reporting_service_pb2.FetchRegisteredModelReportResponse()
            response_1 = customers_v1_preference_validation_service_pb2.PreviewPreferenceResponse()
            response_2 = modelregistry_v1_deployment_sync_service_pb2.ResolveDeploymentConflictResponse()
            outgoing_0 = modelregistry_v1_registered_model_reporting_service_pb2.FetchRegisteredModelReportRequest(
                context=request.context,
                registered_model_id=request.registered_model_id
            )
            document_0 = MessageToJson(outgoing_0, preserving_proto_field_name=True)
            outgoing_0 = Parse(
                document_0,
                modelregistry_v1_registered_model_reporting_service_pb2.FetchRegisteredModelReportRequest()
            )
            response_0 = await deps.clients.modelregistry_registered_model_reporting.FetchRegisteredModelReport(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = customers_v1_preference_validation_service_pb2.PreviewPreferenceRequest()
            outgoing_1.context.CopyFrom(request.context)
            outgoing_1.preference.audit.created_by = request.registered_model.audit.created_by
            merged_1 = customers_v1_preference_validation_service_pb2.PreviewPreferenceRequest()
            merged_1.MergeFrom(outgoing_1)
            outgoing_1.CopyFrom(merged_1)
            response_1 = await deps.clients.customers_preference_validation.PreviewPreference(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = modelregistry_v1_deployment_sync_service_pb2.ResolveDeploymentConflictRequest(
                context=request.context,
                deployment=modelregistry_v1_modelregistry_pb2.Deployment(
                    audit=common_v1_audit_pb2.AuditInfo(updated_at=response_1.preference.audit.updated_at),
                    location=common_v1_address_pb2.PostalAddress(locality=response_0.registered_model.address.locality)
                )
            )
            envelope_2 = AnyMessage()
            envelope_2.Pack(outgoing_2)
            outgoing_2 = modelregistry_v1_deployment_sync_service_pb2.ResolveDeploymentConflictRequest()
            if not envelope_2.Unpack(outgoing_2):
                raise ValueError("partner envelope contains the wrong request type")
            response_2 = await deps.clients.modelregistry_deployment_sync.ResolveDeploymentConflict(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.registered_model.dimensions.length
            if returned_0_0:
                response.registered_model.dimensions.length = returned_0_0
            returned_0_1 = response_0.result.status
            if returned_0_1:
                response.outcome.status = returned_0_1
            returned_1_0 = response_1.preference.audit.created_at
            if returned_1_0.ListFields():
                response.registered_model.audit.created_at.MergeFrom(returned_1_0)
            returned_1_1 = response_1.preference.audit.updated_by
            if returned_1_1:
                response.registered_model.audit.updated_by = returned_1_1
            returned_2_0 = response_2.outcome.message
            if returned_2_0:
                response.result.message = returned_2_0
            echoed_0 = request.registered_model_id
            response.registered_model.registered_model_id = echoed_0
            echoed_1 = request.registered_model.name
            response.registered_model.name = echoed_1
            return response

    async def handle_comment_registered_model_approval(
        self,
        request: modelregistry_v1_registered_model_approval_service_pb2.CommentRegisteredModelApprovalRequest
    ) -> modelregistry_v1_registered_model_approval_service_pb2.CommentRegisteredModelApprovalResponse:
        """Comments a registered model."""
        deps = self.deps
        response = modelregistry_v1_registered_model_approval_service_pb2.CommentRegisteredModelApprovalResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CommentRegisteredModelApproval', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'CommentRegisteredModelApproval',
                {'reason': request.reason}
            )
            await deps.repository.save_registered_model(request.context.tenant_id, request.registered_model)
            response_0 = modelregistry_v1_model_version_reporting_service_pb2.StreamModelVersionMetricsResponse()
            response_1 = metrics_v1_metric_alert_notification_service_pb2.UnsubscribeMetricAlertUpdatesResponse()
            response_2 = documents_v1_document_validation_service_pb2.NormalizeDocumentResponse()
            outgoing_0 = modelregistry_v1_model_version_reporting_service_pb2.StreamModelVersionMetricsRequest(
                context=request.context,
                filter=modelregistry_v1_model_version_reporting_service_pb2.StreamModelVersionMetricsRequest.Filter(
                    created_after=request.registered_model.audit.created_at,
                    region=request.registered_model.address.region
                ),
                subscriber=common_v1_contact_pb2.ContactInfo(email=request.details.approver.email)
            )
            async for chunk_0 in deps.clients.modelregistry_model_version_reporting.StreamModelVersionMetrics(
                outgoing_0,
                timeout=deps.settings.timeout
            ):
                response_0 = chunk_0
            command_1 = RegisteredModelApprovalCommentRegisteredModelApproval1Command(
                context=request.context,
                details_recipient_email=request.details.approver.email
            )
            outgoing_1 = to_registered_model_approval_comment_registered_model_approval1_command(command_1)
            response_1 = await deps.clients.metrics_metric_alert_notification.UnsubscribeMetricAlertUpdates(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            command_2 = RegisteredModelApprovalCommentRegisteredModelApproval2Command.model_validate(
                {
                    'context': request.context,
                    'document_billing_address_recipient': request.registered_model.address.recipient,
                    'document_counterparty_display_name': response_1.metric_alert.owner.display_name
                }
            )
            outgoing_2 = to_registered_model_approval_comment_registered_model_approval2_command(command_2)
            response_2 = await deps.clients.documents_document_validation.NormalizeDocument(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            returned_1_0 = response_1.outcome.reference_id
            if returned_1_0:
                response.outcome.reference_id = returned_1_0
            returned_1_1 = response_1.metric_alert.owner
            if returned_1_1.ListFields():
                response.registered_model.owner.MergeFrom(returned_1_1)
            returned_2_0 = response_2.document.counterparty.display_name
            if returned_2_0:
                response.registered_model.owner.display_name = returned_2_0
            returned_2_1 = response_2.outcome.message
            if returned_2_1:
                response.outcome.message = returned_2_1
            echoed_0 = request.registered_model_id
            response.registered_model.registered_model_id = echoed_0
            echoed_1 = request.registered_model.specs
            response.registered_model.specs.update(echoed_1)
            return response

    async def handle_get_registered_model_approval_status(
        self,
        request: modelregistry_v1_registered_model_approval_service_pb2.GetRegisteredModelApprovalStatusRequest
    ) -> modelregistry_v1_registered_model_approval_service_pb2.GetRegisteredModelApprovalStatusResponse:
        """Returns a registered model."""
        deps = self.deps
        response = modelregistry_v1_registered_model_approval_service_pb2.GetRegisteredModelApprovalStatusResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('GetRegisteredModelApprovalStatus', extra={'fields': {'domain': 'modelregistry'}})
            await deps.repository.audit(request.context.tenant_id, 'GetRegisteredModelApprovalStatus', {})
            response_0 = modelregistry_v1_model_version_sync_service_pb2.ResolveModelVersionConflictResponse()
            response_1 = lineage_v1_lineage_edge_sync_service_pb2.ResolveLineageEdgeConflictResponse()
            outgoing_0 = modelregistry_v1_model_version_sync_service_pb2.ResolveModelVersionConflictRequest(
                context=request.context,
                model_version=modelregistry_v1_modelregistry_pb2.ModelVersion(
                    correlation_id=request.context.actor.user_id,
                    occurred_at=request.context.deadline,
                    subject=customers_v1_refs_pb2.CustomerRef(email=request.context.actor.email)
                )
            )
            response_0 = await deps.clients.modelregistry_model_version_sync.ResolveModelVersionConflict(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = lineage_v1_lineage_edge_sync_service_pb2.ResolveLineageEdgeConflictRequest(
                context=request.context,
                lineage_edge=lineage_v1_lineage_pb2.LineageEdge(occurred_at=response_0.model_version.occurred_at)
            )
            response_1 = await hooks.registered_model_approval_get_registered_model_approval_status1(
                deps.clients.lineage_lineage_edge_sync,
                outgoing_1,
                deps.settings.timeout
            )
            returned_0_0 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_0)
            returned_1_0 = response_1.result.correlation_id
            if returned_1_0:
                response.result.correlation_id = returned_1_0
            echoed_0 = request.registered_model_id
            response.registered_model.registered_model_id = echoed_0
            return response

    async def handle_list_pending_registered_models(
        self,
        request: modelregistry_v1_registered_model_approval_service_pb2.ListPendingRegisteredModelsRequest
    ) -> modelregistry_v1_registered_model_approval_service_pb2.ListPendingRegisteredModelsResponse:
        """Lists registered models a page at a time."""
        deps = self.deps
        response = modelregistry_v1_registered_model_approval_service_pb2.ListPendingRegisteredModelsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ListPendingRegisteredModels', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ListPendingRegisteredModels',
                {'order_by': request.order_by}
            )
            response_0 = customers_v1_household_query_service_pb2.ResolveHouseholdsResponse()
            outgoing_0 = customers_v1_household_query_service_pb2.ResolveHouseholdsRequest(context=request.context)
            response_0 = await deps.clients.customers_household_query.ResolveHouseholds(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_0)
            returned_0_1 = response_0.page_info.next_page_token
            if returned_0_1:
                response.page_info.next_page_token = returned_0_1
            return response

    async def handle_recall_registered_model(
        self,
        request: modelregistry_v1_registered_model_approval_service_pb2.RecallRegisteredModelRequest
    ) -> modelregistry_v1_registered_model_approval_service_pb2.RecallRegisteredModelResponse:
        """Recalls a registered model."""
        deps = self.deps
        response = modelregistry_v1_registered_model_approval_service_pb2.RecallRegisteredModelResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('RecallRegisteredModel', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'RecallRegisteredModel', {'reason': request.reason})
            await deps.repository.save_registered_model(request.context.tenant_id, request.registered_model)
            response_0 = modelregistry_v1_model_version_sync_service_pb2.PushModelVersionResponse()
            response_1 = modelregistry_v1_registered_model_sync_service_pb2.PullRegisteredModelsResponse()
            outgoing_0 = modelregistry_v1_model_version_sync_service_pb2.PushModelVersionRequest(
                context=request.context,
                model_version=modelregistry_v1_modelregistry_pb2.ModelVersion(
                    measurements=[
                        modelregistry_v1_modelregistry_pb2.ModelVersionMeasurement(
                            unit=request.registered_model.dimensions.unit
                        )
                    ],
                    subject=customers_v1_refs_pb2.CustomerRef(
                        display_name=request.registered_model.owner.display_name,
                        email=request.registered_model.owner.email
                    )
                )
            )
            port_0: RegisteredModelApprovalRecallRegisteredModel0Port = RegisteredModelApprovalRecallRegisteredModel0Adapter(
                deps.clients.modelregistry_model_version_sync,
                deps.settings.timeout
            )
            response_0 = await port_0.execute(outgoing_0)
            outgoing_1 = modelregistry_v1_registered_model_sync_service_pb2.PullRegisteredModelsRequest(
                context=request.context,
                registered_model=modelregistry_v1_modelregistry_pb2.RegisteredModel(
                    address=common_v1_address_pb2.PostalAddress(
                        lines=list(request.registered_model.address.lines),
                        postal_code=request.registered_model.address.postal_code
                    ),
                    audit=common_v1_audit_pb2.AuditInfo(etag=request.registered_model.audit.etag)
                )
            )
            steps_1 = [
                partial(
                    deps.clients.modelregistry_registered_model_sync.PullRegisteredModels,
                    outgoing_1,
                    timeout=deps.settings.timeout
                )
            ]
            results_1 = await run_steps(steps_1)
            response_1 = results_1[-1]
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.outcome.message = returned_0_0
            returned_1_0 = response_1.registered_model.owner.display_name
            if returned_1_0:
                response.registered_model.owner.display_name = returned_1_0
            returned_1_1 = response_1.outcome.message
            if returned_1_1:
                response.outcome.message = returned_1_1
            echoed_0 = request.registered_model_id
            response.registered_model.registered_model_id = echoed_0
            echoed_1 = request.registered_model.name
            response.registered_model.name = echoed_1
            return response

    async def handle_reject_registered_model(
        self,
        request: modelregistry_v1_registered_model_approval_service_pb2.RejectRegisteredModelRequest
    ) -> modelregistry_v1_registered_model_approval_service_pb2.RejectRegisteredModelResponse:
        """Rejects a registered model."""
        deps = self.deps
        response = modelregistry_v1_registered_model_approval_service_pb2.RejectRegisteredModelResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('RejectRegisteredModel', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'RejectRegisteredModel', {'reason': request.reason})
            await deps.repository.save_registered_model(request.context.tenant_id, request.registered_model)
            response_0 = modelregistry_v1_registered_model_lifecycle_service_pb2.ExpireRegisteredModelResponse()
            response_1 = notifications_v1_notification_service_pb2.CloneNotificationResponse()
            response_2 = featurestore_v1_feature_value_sync_service_pb2.ResolveFeatureValueConflictResponse()
            outgoing_0 = modelregistry_v1_registered_model_lifecycle_service_pb2.ExpireRegisteredModelRequest(
                context=request.context,
                details=modelregistry_v1_registered_model_lifecycle_service_pb2.ExpireRegisteredModelRequest.Details(
                    notify_contact=common_v1_contact_pb2.ContactInfo(email=request.details.approver.email)
                ),
                registered_model_id=request.registered_model.registered_model_id
            )
            response_0 = await RegisteredModelApprovalRejectRegisteredModel0Adapter(
                deps.clients.modelregistry_registered_model_lifecycle,
                deps.settings.timeout
            )(outgoing_0)
            outgoing_1 = notifications_v1_notification_service_pb2.CloneNotificationRequest(
                context=request.context,
                notification=notifications_v1_notifications_pb2.Notification(
                    audit=common_v1_audit_pb2.AuditInfo(
                        created_at=response_0.registered_model.audit.created_at,
                        created_by=request.registered_model.audit.created_by,
                        etag=response_0.registered_model.audit.etag
                    ),
                    customer=notifications_v1_refs_pb2.NotificationTemplateRef(
                        display_name=request.details.approver.display_name
                    )
                )
            )
            response_1 = cast(notifications_v1_notification_service_pb2.CloneNotificationResponse, await deps.bus.request(
                'acme.modelregistry.v1.RegisteredModelApprovalService/RejectRegisteredModel/1', outgoing_1, deps.settings.timeout,
            ))
            outgoing_2 = featurestore_v1_feature_value_sync_service_pb2.ResolveFeatureValueConflictRequest(
                context=request.context,
                feature_value=featurestore_v1_featurestore_pb2.FeatureValue(
                    measurements=[
                        featurestore_v1_featurestore_pb2.FeatureValueMeasurement(
                            unit=request.registered_model.dimensions.unit
                        )
                    ],
                    subject=datasets_v1_refs_pb2.DatasetRef(display_name=response_0.registered_model.owner.display_name)
                )
            )
            response_2 = await deps.clients.featurestore_feature_value_sync.ResolveFeatureValueConflict(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.registered_model.audit.etag
            if returned_0_0:
                response.registered_model.audit.etag = returned_0_0
            returned_0_1 = response_0.result.status
            if returned_0_1:
                response.result.status = returned_0_1
            returned_1_0 = response_1.notification.audit.created_at
            if returned_1_0.ListFields():
                response.registered_model.audit.created_at.MergeFrom(returned_1_0)
            returned_2_0 = response_2.outcome.message
            if returned_2_0:
                response.outcome.message = returned_2_0
            returned_2_1 = response_2.outcome.next_steps
            response.outcome.next_steps.extend(returned_2_1)
            echoed_0 = request.registered_model_id
            response.registered_model.registered_model_id = echoed_0
            echoed_1 = request.registered_model.code
            response.registered_model.code = echoed_1
            return response

    async def handle_submit_registered_model(
        self,
        request: modelregistry_v1_registered_model_approval_service_pb2.SubmitRegisteredModelRequest
    ) -> modelregistry_v1_registered_model_approval_service_pb2.SubmitRegisteredModelResponse:
        """Submits a registered model."""
        deps = self.deps
        response = modelregistry_v1_registered_model_approval_service_pb2.SubmitRegisteredModelResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SubmitRegisteredModel', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'SubmitRegisteredModel', {'reason': request.reason})
            await deps.repository.save_registered_model(request.context.tenant_id, request.registered_model)
            response_0 = banking_v1_bank_account_query_service_pb2.BrowseBankAccountsResponse()
            outgoing_0 = banking_v1_bank_account_query_service_pb2.BrowseBankAccountsRequest(
                context=request.context,
                filter=banking_v1_bank_account_query_service_pb2.BrowseBankAccountsRequest.Filter(
                    region=request.registered_model.address.region
                )
            )
            method_name_0 = 'BrowseBankAccounts'
            response_0 = await getattr(
                deps.clients.banking_bank_account_query,
                method_name_0
            )(outgoing_0, timeout=deps.settings.timeout)
            returned_0_0 = response_0.result.correlation_id
            if returned_0_0:
                response.result.correlation_id = returned_0_0
            echoed_0 = request.registered_model_id
            response.registered_model.registered_model_id = echoed_0
            echoed_1 = request.registered_model.capacity
            response.registered_model.capacity = echoed_1
            return response
