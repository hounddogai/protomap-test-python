"""Routes deployments through approval, with escalation and delegation."""

from __future__ import annotations

from collections.abc import AsyncIterator
from collections.abc import Awaitable
from collections.abc import Callable
from functools import partial
from typing import cast
import asyncio
import logging

from google.protobuf.json_format import MessageToDict
from google.protobuf.json_format import ParseDict
import grpc

from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.customers.v1 import (
    customer_segment_validation_service_pb2 as customers_v1_customer_segment_validation_service_pb2,
)
from acme.customers.v1 import customer_validation_service_pb2 as customers_v1_customer_validation_service_pb2
from acme.customers.v1 import customers_pb2 as customers_v1_customers_pb2
from acme.customers.v1 import household_validation_service_pb2 as customers_v1_household_validation_service_pb2
from acme.featurestore.v1 import feature_value_import_service_pb2 as featurestore_v1_feature_value_import_service_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.metrics.v1 import metric_alert_validation_service_pb2 as metrics_v1_metric_alert_validation_service_pb2
from acme.modelregistry.v1 import deployment_approval_service_pb2 as modelregistry_v1_deployment_approval_service_pb2
from acme.modelregistry.v1 import (
    deployment_approval_service_pb2_grpc as modelregistry_v1_deployment_approval_service_pb2_grpc,
)
from acme.modelregistry.v1 import deployment_lifecycle_service_pb2 as modelregistry_v1_deployment_lifecycle_service_pb2
from acme.modelregistry.v1 import deployment_reporting_service_pb2 as modelregistry_v1_deployment_reporting_service_pb2
from acme.modelregistry.v1 import modelregistry_pb2 as modelregistry_v1_modelregistry_pb2
from acme.modelregistry.v1 import (
    registered_model_calculation_service_pb2 as modelregistry_v1_registered_model_calculation_service_pb2,
)
from acme.modelregistry.v1 import (
    registered_model_lifecycle_service_pb2 as modelregistry_v1_registered_model_lifecycle_service_pb2,
)
from acme.modelregistry.v1 import (
    registered_model_lifecycle_service_pb2_grpc as modelregistry_v1_registered_model_lifecycle_service_pb2_grpc,
)
from acme.modelregistry.v1 import (
    registered_model_query_service_pb2 as modelregistry_v1_registered_model_query_service_pb2,
)
from acme.modelregistry.v1 import (
    registered_model_reporting_service_pb2 as modelregistry_v1_registered_model_reporting_service_pb2,
)

from acme_data.domains.modelregistry import hooks
from acme_data.domains.modelregistry.adapters import DeploymentApprovalDelegateDeploymentApproval0Adapter
from acme_data.domains.modelregistry.dependencies import Dependencies
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import run_steps
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_id
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class DeploymentApprovalServicer(
    modelregistry_v1_deployment_approval_service_pb2_grpc.DeploymentApprovalServiceServicer
):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    async def ApproveDeployment(
        self, request: modelregistry_v1_deployment_approval_service_pb2.ApproveDeploymentRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_deployment_approval_service_pb2.ApproveDeploymentResponse:
        """Approves a deployment."""
        return await self.handle_approve_deployment(request)

    @rpc_errors
    async def CommentDeploymentApproval(
        self, request: modelregistry_v1_deployment_approval_service_pb2.CommentDeploymentApprovalRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_deployment_approval_service_pb2.CommentDeploymentApprovalResponse:
        """Comments a deployment."""
        return await self.handle_comment_deployment_approval(request)

    @rpc_errors
    async def DelegateDeploymentApproval(
        self, request: modelregistry_v1_deployment_approval_service_pb2.DelegateDeploymentApprovalRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_deployment_approval_service_pb2.DelegateDeploymentApprovalResponse:
        """Delegates a deployment."""
        return await self.handle_delegate_deployment_approval(request)

    @rpc_errors
    async def EscalateDeployment(
        self, request: modelregistry_v1_deployment_approval_service_pb2.EscalateDeploymentRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_deployment_approval_service_pb2.EscalateDeploymentResponse:
        """Escalates a deployment."""
        return await self.handle_escalate_deployment(request)

    @rpc_errors
    @retry_transient
    async def GetDeploymentApprovalStatus(
        self, request: modelregistry_v1_deployment_approval_service_pb2.GetDeploymentApprovalStatusRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_deployment_approval_service_pb2.GetDeploymentApprovalStatusResponse:
        """Returns a deployment."""
        return await self.handle_get_deployment_approval_status(request)

    @rpc_errors
    @retry_transient
    async def ListPendingDeployments(
        self, request: modelregistry_v1_deployment_approval_service_pb2.ListPendingDeploymentsRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_deployment_approval_service_pb2.ListPendingDeploymentsResponse:
        """Lists deployments a page at a time."""
        return await self.handle_list_pending_deployments(request)

    @rpc_errors
    async def RejectDeployment(
        self, request: modelregistry_v1_deployment_approval_service_pb2.RejectDeploymentRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_deployment_approval_service_pb2.RejectDeploymentResponse:
        """Rejects a deployment."""
        return await self.handle_reject_deployment(request)

    @rpc_errors
    async def SubmitDeployment(
        self, request: modelregistry_v1_deployment_approval_service_pb2.SubmitDeploymentRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_deployment_approval_service_pb2.SubmitDeploymentResponse:
        """Submits a deployment."""
        return await self.handle_submit_deployment(request)

    async def handle_approve_deployment(
        self,
        request: modelregistry_v1_deployment_approval_service_pb2.ApproveDeploymentRequest
    ) -> modelregistry_v1_deployment_approval_service_pb2.ApproveDeploymentResponse:
        """Approves a deployment."""
        deps = self.deps
        response = modelregistry_v1_deployment_approval_service_pb2.ApproveDeploymentResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ApproveDeployment', extra={'fields': {'deployment_id': request.deployment.deployment_id}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ApproveDeployment',
                {'deployment_id': request.deployment.deployment_id}
            )
            await deps.repository.save_deployment(request.context.tenant_id, request.deployment)
            response_0 = modelregistry_v1_registered_model_reporting_service_pb2.ScheduleRegisteredModelReportResponse()
            response_1 = metrics_v1_metric_alert_validation_service_pb2.LintMetricAlertsResponse()
            outgoing_0 = modelregistry_v1_registered_model_reporting_service_pb2.ScheduleRegisteredModelReportRequest(
                annotations=dict(request.annotations),
                context=request.context,
                details=modelregistry_v1_registered_model_reporting_service_pb2.ScheduleRegisteredModelReportRequest.Details(
                    period=request.deployment.window
                ),
                reason=request.reason
            )
            response_0 = await hooks.deployment_approval_approve_deployment0(
                deps.clients.modelregistry_registered_model_reporting,
                outgoing_0,
                deps.settings.timeout
            )
            outgoing_1 = metrics_v1_metric_alert_validation_service_pb2.LintMetricAlertsRequest()
            outgoing_1.context.CopyFrom(request.context)
            outgoing_1.metric_alert.owner.display_name = request.details.approver.display_name
            outgoing_1.metric_alert.audit.created_by = request.deployment.audit.created_by
            outgoing_1.metric_alert.owner.user_id = request.deployment.organizer.user_id
            outgoing_1.context.tenant_id = tenant_id.get()
            response_1 = await deps.clients.metrics_metric_alert_validation.LintMetricAlerts(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.details
            response.result.details.update(returned_0_0)
            returned_1_0 = response_1.metric_alert.owner.display_name
            if returned_1_0:
                response.deployment.organizer.display_name = returned_1_0
            returned_1_1 = response_1.metric_alert.owner.email
            if returned_1_1:
                response.deployment.organizer.email = returned_1_1
            echoed_0 = request.deployment_id
            response.deployment.deployment_id = echoed_0
            echoed_1 = request.deployment.title
            response.deployment.title = echoed_1
            return response

    async def handle_comment_deployment_approval(
        self,
        request: modelregistry_v1_deployment_approval_service_pb2.CommentDeploymentApprovalRequest
    ) -> modelregistry_v1_deployment_approval_service_pb2.CommentDeploymentApprovalResponse:
        """Comments a deployment."""
        deps = self.deps
        response = modelregistry_v1_deployment_approval_service_pb2.CommentDeploymentApprovalResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CommentDeploymentApproval', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'CommentDeploymentApproval',
                {'reason': request.reason}
            )
            await deps.repository.save_deployment(request.context.tenant_id, request.deployment)
            response_0 = customers_v1_customer_segment_validation_service_pb2.PreviewCustomerSegmentResponse()
            response_1 = modelregistry_v1_registered_model_calculation_service_pb2.EstimateRegisteredModelResponse()
            requests_0: list[customers_v1_customer_segment_validation_service_pb2.PreviewCustomerSegmentRequest] = []
            for item_0 in request.deployment.participants:
                outgoing_0 = customers_v1_customer_segment_validation_service_pb2.PreviewCustomerSegmentRequest(
                    context=request.context,
                    details=customers_v1_customer_segment_validation_service_pb2.PreviewCustomerSegmentRequest.Details(
                        contact=common_v1_contact_pb2.ContactInfo(phone=item_0.contact.phone)
                    )
                )
                requests_0.append(outgoing_0)
            replies_0 = await asyncio.gather(*(
                deps.clients.customers_customer_segment_validation.PreviewCustomerSegment(
                    entry,
                    timeout=deps.settings.timeout
                ) for entry in requests_0
            ))
            if replies_0:
                response_0 = replies_0[-1]
            outgoing_1 = modelregistry_v1_registered_model_calculation_service_pb2.EstimateRegisteredModelRequest(
                context=request.context,
                details=modelregistry_v1_registered_model_calculation_service_pb2.EstimateRegisteredModelRequest.Details(
                    destination=common_v1_address_pb2.PostalAddress(postal_code=request.deployment.location.postal_code)
                ),
                registered_model=modelregistry_v1_modelregistry_pb2.RegisteredModel(
                    address=common_v1_address_pb2.PostalAddress(country_code=request.deployment.location.country_code),
                    audit=common_v1_audit_pb2.AuditInfo(
                        created_at=request.deployment.audit.created_at,
                        updated_by=response_0.customer_segment.audit.updated_by
                    )
                )
            )
            steps_1 = [
                partial(
                    deps.clients.modelregistry_registered_model_calculation.EstimateRegisteredModel,
                    outgoing_1,
                    timeout=deps.settings.timeout
                )
            ]
            results_1 = await run_steps(steps_1)
            response_1 = results_1[-1]
            returned_1_0 = response_1.registered_model.audit.updated_by
            if returned_1_0:
                response.deployment.audit.updated_by = returned_1_0
            returned_1_1 = response_1.result.status
            if returned_1_1:
                response.outcome.status = returned_1_1
            echoed_0 = request.deployment_id
            response.deployment.deployment_id = echoed_0
            echoed_1 = request.deployment.location
            response.deployment.location.CopyFrom(echoed_1)
            return response

    async def handle_delegate_deployment_approval(
        self,
        request: modelregistry_v1_deployment_approval_service_pb2.DelegateDeploymentApprovalRequest
    ) -> modelregistry_v1_deployment_approval_service_pb2.DelegateDeploymentApprovalResponse:
        """Delegates a deployment."""
        deps = self.deps
        response = modelregistry_v1_deployment_approval_service_pb2.DelegateDeploymentApprovalResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('DelegateDeploymentApproval', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'DelegateDeploymentApproval',
                {'reason': request.reason}
            )
            await deps.repository.save_deployment(request.context.tenant_id, request.deployment)
            response_0 = customers_v1_customer_validation_service_pb2.PreviewCustomerResponse()
            response_1 = customers_v1_customer_segment_validation_service_pb2.ExplainCustomerSegmentDecisionResponse()
            response_2 = modelregistry_v1_registered_model_query_service_pb2.CountRegisteredModelsResponse()
            outgoing_0 = customers_v1_customer_validation_service_pb2.PreviewCustomerRequest(
                context=request.context,
                customer=customers_v1_customers_pb2.Customer(
                    audit=common_v1_audit_pb2.AuditInfo(
                        created_by=request.deployment.audit.created_by,
                        updated_by=request.deployment.audit.updated_by
                    ),
                    contact=common_v1_contact_pb2.ContactInfo(email=request.deployment.organizer.email),
                    relationship_manager=identity_v1_refs_pb2.UserRef(email=request.details.approver.email)
                )
            )
            response_0 = await DeploymentApprovalDelegateDeploymentApproval0Adapter(
                deps.clients.customers_customer_validation,
                deps.settings.timeout
            )(outgoing_0)
            outgoing_1 = customers_v1_customer_segment_validation_service_pb2.ExplainCustomerSegmentDecisionRequest(
                context=request.context,
                customer_segment=customers_v1_customers_pb2.CustomerSegment(
                    audit=common_v1_audit_pb2.AuditInfo(etag=response_0.customer.audit.etag),
                    owner=identity_v1_refs_pb2.UserRef(
                        email=response_0.customer.relationship_manager.email,
                        user_id=request.details.approver.user_id
                    )
                )
            )
            response_1 = cast(customers_v1_customer_segment_validation_service_pb2.ExplainCustomerSegmentDecisionResponse, await deps.bus.request(
                'acme.modelregistry.v1.DeploymentApprovalService/DelegateDeploymentApproval/1', outgoing_1, deps.settings.timeout,
            ))
            outgoing_2 = modelregistry_v1_registered_model_query_service_pb2.CountRegisteredModelsRequest(
                context=request.context,
                filter=modelregistry_v1_registered_model_query_service_pb2.CountRegisteredModelsRequest.Filter(
                    region=response_0.customer.primary_address.region
                )
            )
            response_2 = await deps.clients.modelregistry_registered_model_query.CountRegisteredModels(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.customer.contact.preferred_channel
            returned_0_0_part_1 = response.deployment.participants.add()
            if returned_0_0:
                returned_0_0_part_1.contact.preferred_channel = returned_0_0
            returned_0_1 = response_0.outcome.status
            if returned_0_1:
                response.result.status = returned_0_1
            returned_1_0 = response_1.result.message
            if returned_1_0:
                response.outcome.message = returned_1_0
            returned_1_1 = response_1.customer_segment.audit.updated_by
            if returned_1_1:
                response.deployment.audit.updated_by = returned_1_1
            returned_2_0 = response_2.result.message
            if returned_2_0:
                response.outcome.message = returned_2_0
            returned_2_1 = response_2.result.message
            if returned_2_1:
                response.result.message = returned_2_1
            echoed_0 = request.deployment_id
            response.deployment.deployment_id = echoed_0
            echoed_1 = request.deployment.title
            response.deployment.title = echoed_1
            return response

    async def handle_escalate_deployment(
        self,
        request: modelregistry_v1_deployment_approval_service_pb2.EscalateDeploymentRequest
    ) -> modelregistry_v1_deployment_approval_service_pb2.EscalateDeploymentResponse:
        """Escalates a deployment."""
        deps = self.deps
        response = modelregistry_v1_deployment_approval_service_pb2.EscalateDeploymentResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('EscalateDeployment', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'EscalateDeployment', {'reason': request.reason})
            await deps.repository.save_deployment(request.context.tenant_id, request.deployment)
            response_0 = customers_v1_customer_segment_validation_service_pb2.ExplainCustomerSegmentDecisionResponse()
            response_1 = featurestore_v1_feature_value_import_service_pb2.ValidateFeatureValueImportResponse()
            response_2 = customers_v1_customer_validation_service_pb2.ScoreCustomerResponse()
            outgoing_0 = customers_v1_customer_segment_validation_service_pb2.ExplainCustomerSegmentDecisionRequest(
                context=request.context,
                customer_segment=customers_v1_customers_pb2.CustomerSegment(
                    audit=common_v1_audit_pb2.AuditInfo(
                        etag=request.deployment.audit.etag,
                        updated_at=request.deployment.audit.updated_at
                    ),
                    owner=identity_v1_refs_pb2.UserRef(
                        email=request.deployment.organizer.email,
                        user_id=request.details.approver.user_id
                    )
                )
            )
            method_name_0 = 'ExplainCustomerSegmentDecision'
            response_0 = await getattr(
                deps.clients.customers_customer_segment_validation,
                method_name_0
            )(outgoing_0, timeout=deps.settings.timeout)
            callbacks_1: list[
                Callable[
                    [],
                    Awaitable[featurestore_v1_feature_value_import_service_pb2.ValidateFeatureValueImportResponse]
                ]
            ] = []
            for item_1 in request.deployment.participants:
                outgoing_1 = featurestore_v1_feature_value_import_service_pb2.ValidateFeatureValueImportRequest(
                    context=request.context,
                    details=featurestore_v1_feature_value_import_service_pb2.ValidateFeatureValueImportRequest.Details(
                        contact=common_v1_contact_pb2.ContactInfo(
                            email=item_1.contact.email,
                            name=item_1.contact.name,
                            phone=item_1.contact.phone,
                            preferred_channel=item_1.contact.preferred_channel
                        )
                    )
                )
                async def send_1(
                    payload: featurestore_v1_feature_value_import_service_pb2.ValidateFeatureValueImportRequest = outgoing_1
                ) -> featurestore_v1_feature_value_import_service_pb2.ValidateFeatureValueImportResponse:
                    return await deps.clients.featurestore_feature_value_import.ValidateFeatureValueImport(
                        payload,
                        timeout=deps.settings.timeout
                    )
                callbacks_1.append(send_1)
            for callback_1 in callbacks_1:
                response_1 = await callback_1()
            outgoing_2 = customers_v1_customer_validation_service_pb2.ScoreCustomerRequest(
                context=request.context,
                customer=customers_v1_customers_pb2.Customer(
                    relationship_manager=identity_v1_refs_pb2.UserRef(
                        display_name=request.deployment.organizer.display_name
                    )
                )
            )
            document_2 = MessageToDict(outgoing_2, preserving_proto_field_name=True)
            outgoing_2 = ParseDict(document_2, customers_v1_customer_validation_service_pb2.ScoreCustomerRequest())
            response_2 = await deps.clients.customers_customer_validation.ScoreCustomer(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.customer_segment.owner.email
            returned_0_0_part_1 = response.deployment.participants.add()
            if returned_0_0:
                returned_0_0_part_1.contact.email = returned_0_0
            returned_2_0 = response_2.customer.relationship_manager.email
            if returned_2_0:
                response.deployment.organizer.email = returned_2_0
            returned_2_1 = response_2.customer.primary_address.region
            if returned_2_1:
                response.deployment.location.region = returned_2_1
            echoed_0 = request.deployment_id
            response.deployment.deployment_id = echoed_0
            echoed_1 = request.deployment.title
            response.deployment.title = echoed_1
            return response

    async def handle_get_deployment_approval_status(
        self,
        request: modelregistry_v1_deployment_approval_service_pb2.GetDeploymentApprovalStatusRequest
    ) -> modelregistry_v1_deployment_approval_service_pb2.GetDeploymentApprovalStatusResponse:
        """Returns a deployment."""
        deps = self.deps
        response = modelregistry_v1_deployment_approval_service_pb2.GetDeploymentApprovalStatusResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('GetDeploymentApprovalStatus', extra={'fields': {'domain': 'modelregistry'}})
            await deps.repository.audit(request.context.tenant_id, 'GetDeploymentApprovalStatus', {})
            response_0 = customers_v1_household_validation_service_pb2.PreviewHouseholdResponse()
            outgoing_0 = customers_v1_household_validation_service_pb2.PreviewHouseholdRequest(
                context=request.context,
                household=customers_v1_customers_pb2.Household(
                    children=[
                        customers_v1_customers_pb2.Household(
                            manager=identity_v1_refs_pb2.UserRef(email=request.context.actor.email)
                        )
                    ]
                )
            )
            response_0 = await deps.clients.customers_household_validation.PreviewHousehold(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.correlation_id
            if returned_0_0:
                response.result.correlation_id = returned_0_0
            returned_0_1 = response_0.household.audit.created_by
            if returned_0_1:
                response.deployment.audit.created_by = returned_0_1
            echoed_0 = request.deployment_id
            response.deployment.deployment_id = echoed_0
            return response

    async def handle_list_pending_deployments(
        self,
        request: modelregistry_v1_deployment_approval_service_pb2.ListPendingDeploymentsRequest
    ) -> modelregistry_v1_deployment_approval_service_pb2.ListPendingDeploymentsResponse:
        """Lists deployments a page at a time."""
        deps = self.deps
        response = modelregistry_v1_deployment_approval_service_pb2.ListPendingDeploymentsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ListPendingDeployments', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ListPendingDeployments',
                {'order_by': request.order_by}
            )
            return response

    async def handle_reject_deployment(
        self,
        request: modelregistry_v1_deployment_approval_service_pb2.RejectDeploymentRequest
    ) -> modelregistry_v1_deployment_approval_service_pb2.RejectDeploymentResponse:
        """Rejects a deployment."""
        deps = self.deps
        response = modelregistry_v1_deployment_approval_service_pb2.RejectDeploymentResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('RejectDeployment', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'RejectDeployment', {'reason': request.reason})
            await deps.repository.save_deployment(request.context.tenant_id, request.deployment)
            response_0 = modelregistry_v1_deployment_reporting_service_pb2.ListDeploymentReportsResponse()
            response_1 = modelregistry_v1_deployment_lifecycle_service_pb2.ActivateDeploymentResponse()
            outgoing_0 = modelregistry_v1_deployment_reporting_service_pb2.ListDeploymentReportsRequest()
            outgoing_0.context.CopyFrom(request.context)
            outgoing_0.filter.region = request.deployment.location.region
            merged_0 = modelregistry_v1_deployment_reporting_service_pb2.ListDeploymentReportsRequest()
            merged_0.MergeFrom(outgoing_0)
            outgoing_0.CopyFrom(merged_0)
            response_0 = await deps.clients.modelregistry_deployment_reporting.ListDeploymentReports(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            async for item_1 in async_messages(request.deployment.participants):
                outgoing_1 = modelregistry_v1_deployment_lifecycle_service_pb2.ActivateDeploymentRequest(
                    context=request.context,
                    deployment_id=request.deployment_id,
                    details=modelregistry_v1_deployment_lifecycle_service_pb2.ActivateDeploymentRequest.Details(
                        new_owner=identity_v1_refs_pb2.UserRef(email=item_1.contact.email),
                        notify_contact=common_v1_contact_pb2.ContactInfo(
                            name=item_1.contact.name,
                            phone=item_1.contact.phone,
                            preferred_channel=item_1.contact.preferred_channel
                        )
                    )
                )
                response_1 = await deps.clients.modelregistry_deployment_lifecycle.ActivateDeployment(
                    outgoing_1,
                    timeout=deps.settings.timeout
                )
            returned_0_0 = response_0.result.status
            if returned_0_0:
                response.result.status = returned_0_0
            echoed_0 = request.deployment_id
            response.deployment.deployment_id = echoed_0
            echoed_1 = request.deployment.location
            response.deployment.location.CopyFrom(echoed_1)
            return response

    async def handle_submit_deployment(
        self,
        request: modelregistry_v1_deployment_approval_service_pb2.SubmitDeploymentRequest
    ) -> modelregistry_v1_deployment_approval_service_pb2.SubmitDeploymentResponse:
        """Submits a deployment."""
        deps = self.deps
        response = modelregistry_v1_deployment_approval_service_pb2.SubmitDeploymentResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SubmitDeployment', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'SubmitDeployment', {'reason': request.reason})
            await deps.repository.save_deployment(request.context.tenant_id, request.deployment)
            response_0 = modelregistry_v1_registered_model_lifecycle_service_pb2.ScheduleRegisteredModelExpiryResponse()
            outgoing_0 = modelregistry_v1_registered_model_lifecycle_service_pb2.ScheduleRegisteredModelExpiryRequest(
                context=request.context,
                registered_model=modelregistry_v1_modelregistry_pb2.RegisteredModel(
                    address=common_v1_address_pb2.PostalAddress(
                        lines=list(request.deployment.location.lines),
                        region=request.deployment.location.region
                    ),
                    audit=common_v1_audit_pb2.AuditInfo(etag=request.deployment.audit.etag)
                )
            )
            registered_0 = cast(
                modelregistry_v1_registered_model_lifecycle_service_pb2_grpc.RegisteredModelLifecycleServiceStub,
                deps.clients.registry['acme.modelregistry.v1.RegisteredModelLifecycleService']
            )
            response_0 = await registered_0.ScheduleRegisteredModelExpiry(outgoing_0, timeout=deps.settings.timeout)
            returned_0_0 = response_0.registered_model.address.country_code
            if returned_0_0:
                response.deployment.location.country_code = returned_0_0
            echoed_0 = request.deployment_id
            response.deployment.deployment_id = echoed_0
            echoed_1 = request.deployment.status
            response.deployment.status = echoed_1
            return response
