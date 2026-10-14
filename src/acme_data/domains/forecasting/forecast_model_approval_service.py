"""Routes forecast models through approval, with escalation and delegation."""

from __future__ import annotations

from collections.abc import AsyncIterator
from functools import partial
from typing import Any
from typing import cast
import asyncio
import logging

from google.protobuf.any_pb2 import Any as AnyMessage
from google.protobuf.json_format import MessageToDict
from google.protobuf.json_format import MessageToJson
from google.protobuf.json_format import Parse
from google.protobuf.json_format import ParseDict
import grpc

from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.documents.v1 import document_validation_service_pb2 as documents_v1_document_validation_service_pb2
from acme.documents.v1 import documents_pb2 as documents_v1_documents_pb2
from acme.documents.v1 import refs_pb2 as documents_v1_refs_pb2
from acme.featurestore.v1 import entity_workflow_service_pb2 as featurestore_v1_entity_workflow_service_pb2
from acme.featurestore.v1 import featurestore_pb2 as featurestore_v1_featurestore_pb2
from acme.forecasting.v1 import demand_forecast_service_pb2 as forecasting_v1_demand_forecast_service_pb2
from acme.forecasting.v1 import (
    demand_forecast_validation_service_pb2 as forecasting_v1_demand_forecast_validation_service_pb2,
)
from acme.forecasting.v1 import (
    forecast_model_approval_service_pb2 as forecasting_v1_forecast_model_approval_service_pb2,
)
from acme.forecasting.v1 import (
    forecast_model_approval_service_pb2_grpc as forecasting_v1_forecast_model_approval_service_pb2_grpc,
)
from acme.forecasting.v1 import forecasting_pb2 as forecasting_v1_forecasting_pb2
from acme.forecasting.v1 import scenario_calculation_service_pb2 as forecasting_v1_scenario_calculation_service_pb2
from acme.forecasting.v1 import scenario_validation_service_pb2 as forecasting_v1_scenario_validation_service_pb2
from acme.identity.v1 import identity_pb2 as identity_v1_identity_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.identity.v1 import user_query_service_pb2 as identity_v1_user_query_service_pb2
from acme.identity.v1 import user_service_pb2 as identity_v1_user_service_pb2
from acme.identity.v1 import user_validation_service_pb2 as identity_v1_user_validation_service_pb2
from acme.ledger.v1 import ledger_account_validation_service_pb2 as ledger_v1_ledger_account_validation_service_pb2
from acme.ledger.v1 import ledger_pb2 as ledger_v1_ledger_pb2
from acme.metrics.v1 import metric_series_query_service_pb2 as metrics_v1_metric_series_query_service_pb2
from acme.modelregistry.v1 import deployment_approval_service_pb2 as modelregistry_v1_deployment_approval_service_pb2
from acme.modelregistry.v1 import (
    deployment_approval_service_pb2_grpc as modelregistry_v1_deployment_approval_service_pb2_grpc,
)
from acme.modelregistry.v1 import deployment_sync_service_pb2 as modelregistry_v1_deployment_sync_service_pb2
from acme.modelregistry.v1 import modelregistry_pb2 as modelregistry_v1_modelregistry_pb2
from acme.modelregistry.v1 import (
    registered_model_workflow_service_pb2 as modelregistry_v1_registered_model_workflow_service_pb2,
)
from acme.notifications.v1 import notification_query_service_pb2 as notifications_v1_notification_query_service_pb2
from acme.notifications.v1 import (
    notification_validation_service_pb2 as notifications_v1_notification_validation_service_pb2,
)
from acme.notifications.v1 import notifications_pb2 as notifications_v1_notifications_pb2
from acme.notifications.v1 import refs_pb2 as notifications_v1_refs_pb2
from acme.pipelines.v1 import pipeline_reporting_service_pb2 as pipelines_v1_pipeline_reporting_service_pb2

from acme_data.domains.forecasting import hooks
from acme_data.domains.forecasting.adapters import ForecastModelApprovalRejectForecastModel0Adapter
from acme_data.domains.forecasting.dependencies import Dependencies
from acme_data.domains.forecasting.models import ForecastModelApprovalDelegateForecastModelApproval1Command
from acme_data.domains.forecasting.models import ForecastModelApprovalEscalateForecastModel0Command
from acme_data.domains.forecasting.models import to_forecast_model_approval_delegate_forecast_model_approval1_command
from acme_data.domains.forecasting.models import to_forecast_model_approval_escalate_forecast_model0_command
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import run_steps
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class ForecastModelApprovalServicer(
    forecasting_v1_forecast_model_approval_service_pb2_grpc.ForecastModelApprovalServiceServicer
):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    async def ApproveForecastModel(
        self, request: forecasting_v1_forecast_model_approval_service_pb2.ApproveForecastModelRequest, context: grpc.aio.ServicerContext,
    ) -> forecasting_v1_forecast_model_approval_service_pb2.ApproveForecastModelResponse:
        """Approves a forecast model."""
        return await self.handle_approve_forecast_model(request)

    @rpc_errors
    async def CommentForecastModelApproval(
        self, request: forecasting_v1_forecast_model_approval_service_pb2.CommentForecastModelApprovalRequest, context: grpc.aio.ServicerContext,
    ) -> forecasting_v1_forecast_model_approval_service_pb2.CommentForecastModelApprovalResponse:
        """Comments a forecast model."""
        return await self.handle_comment_forecast_model_approval(request)

    @rpc_errors
    async def DelegateForecastModelApproval(
        self, request: forecasting_v1_forecast_model_approval_service_pb2.DelegateForecastModelApprovalRequest, context: grpc.aio.ServicerContext,
    ) -> forecasting_v1_forecast_model_approval_service_pb2.DelegateForecastModelApprovalResponse:
        """Delegates a forecast model."""
        return await self.handle_delegate_forecast_model_approval(request)

    @rpc_errors
    async def EscalateForecastModel(
        self, request: forecasting_v1_forecast_model_approval_service_pb2.EscalateForecastModelRequest, context: grpc.aio.ServicerContext,
    ) -> forecasting_v1_forecast_model_approval_service_pb2.EscalateForecastModelResponse:
        """Escalates a forecast model."""
        return await self.handle_escalate_forecast_model(request)

    @rpc_errors
    @retry_transient
    async def GetForecastModelApprovalStatus(
        self, request: forecasting_v1_forecast_model_approval_service_pb2.GetForecastModelApprovalStatusRequest, context: grpc.aio.ServicerContext,
    ) -> forecasting_v1_forecast_model_approval_service_pb2.GetForecastModelApprovalStatusResponse:
        """Returns a forecast model."""
        return await self.handle_get_forecast_model_approval_status(request)

    @rpc_errors
    @retry_transient
    async def ListPendingForecastModels(
        self, request: forecasting_v1_forecast_model_approval_service_pb2.ListPendingForecastModelsRequest, context: grpc.aio.ServicerContext,
    ) -> forecasting_v1_forecast_model_approval_service_pb2.ListPendingForecastModelsResponse:
        """Lists forecast models a page at a time."""
        return await self.handle_list_pending_forecast_models(request)

    @rpc_errors
    async def RejectForecastModel(
        self, request: forecasting_v1_forecast_model_approval_service_pb2.RejectForecastModelRequest, context: grpc.aio.ServicerContext,
    ) -> forecasting_v1_forecast_model_approval_service_pb2.RejectForecastModelResponse:
        """Rejects a forecast model."""
        return await self.handle_reject_forecast_model(request)

    @rpc_errors
    async def SubmitForecastModel(
        self, request: forecasting_v1_forecast_model_approval_service_pb2.SubmitForecastModelRequest, context: grpc.aio.ServicerContext,
    ) -> forecasting_v1_forecast_model_approval_service_pb2.SubmitForecastModelResponse:
        """Submits a forecast model."""
        return await self.handle_submit_forecast_model(request)

    async def handle_approve_forecast_model(
        self,
        request: forecasting_v1_forecast_model_approval_service_pb2.ApproveForecastModelRequest
    ) -> forecasting_v1_forecast_model_approval_service_pb2.ApproveForecastModelResponse:
        """Approves a forecast model."""
        deps = self.deps
        response = forecasting_v1_forecast_model_approval_service_pb2.ApproveForecastModelResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ApproveForecastModel', extra={'fields': {'approver_email': request.details.approver_email}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ApproveForecastModel',
                {'approver_email': request.details.approver_email}
            )
            await deps.repository.save_forecast_model(request.context.tenant_id, request.forecast_model)
            response_0 = metrics_v1_metric_series_query_service_pb2.SummarizeMetricSeriesesResponse()
            response_1 = notifications_v1_notification_query_service_pb2.CountNotificationsResponse()
            response_2 = forecasting_v1_demand_forecast_service_pb2.UpdateDemandForecastResponse()
            response_3 = identity_v1_user_service_pb2.ListUsersResponse()
            outgoing_1 = notifications_v1_notification_query_service_pb2.CountNotificationsRequest(
                context=request.context,
                filter=notifications_v1_notification_query_service_pb2.CountNotificationsRequest.Filter(
                    created_after=request.forecast_model.audit.created_at,
                    region=request.forecast_model.address.region
                )
            )
            outgoing_2 = forecasting_v1_demand_forecast_service_pb2.UpdateDemandForecastRequest(
                context=request.context,
                demand_forecast=forecasting_v1_forecasting_pb2.DemandForecast(
                    audit=common_v1_audit_pb2.AuditInfo(updated_by=request.forecast_model.audit.updated_by),
                    billing_address=common_v1_address_pb2.PostalAddress(
                        recipient=request.forecast_model.address.recipient
                    )
                )
            )
            response_1, response_2 = await asyncio.gather(
                deps.clients.notifications_notification_query.CountNotifications(
                    outgoing_1,
                    timeout=deps.settings.timeout
                ),
                deps.clients.forecasting_demand_forecast.UpdateDemandForecast(
                    outgoing_2,
                    timeout=deps.settings.timeout
                ),
            )
            outgoing_0 = metrics_v1_metric_series_query_service_pb2.SummarizeMetricSeriesesRequest(
                annotations=dict(request.annotations),
                context=request.context,
                details=metrics_v1_metric_series_query_service_pb2.SummarizeMetricSeriesesRequest.Details(
                    filters=dict(request.forecast_model.specs)
                ),
                reason=request.reason
            )
            response_0 = cast(metrics_v1_metric_series_query_service_pb2.SummarizeMetricSeriesesResponse, await deps.bus.request(
                'acme.forecasting.v1.ForecastModelApprovalService/ApproveForecastModel/0', outgoing_0, deps.settings.timeout,
            ))
            fields_3: dict[str, Any] = {
                'context': request.context,
                'filter': {
                    'created_after': request.details.effective_at,
                    'region': response_2.demand_forecast.billing_address.region
                }
            }
            outgoing_3 = identity_v1_user_service_pb2.ListUsersRequest(**fields_3)
            response_3 = await deps.clients.identity_user.ListUsers(outgoing_3, timeout=deps.settings.timeout)
            returned_0_0 = response_0.result.correlation_id
            if returned_0_0:
                response.result.correlation_id = returned_0_0
            returned_0_1 = response_0.result.status
            if returned_0_1:
                response.result.status = returned_0_1
            returned_1_0 = response_1.result.correlation_id
            if returned_1_0:
                response.result.correlation_id = returned_1_0
            returned_2_0 = response_2.demand_forecast.counterparty.display_name
            if returned_2_0:
                response.forecast_model.owner.display_name = returned_2_0
            returned_3_0 = response_3.result.message
            if returned_3_0:
                response.result.message = returned_3_0
            returned_3_1 = response_3.result.reference_ids
            response.result.reference_ids.extend(returned_3_1)
            echoed_0 = request.forecast_model_id
            response.forecast_model.forecast_model_id = echoed_0
            echoed_1 = request.forecast_model.name
            response.forecast_model.name = echoed_1
            return response

    async def handle_comment_forecast_model_approval(
        self,
        request: forecasting_v1_forecast_model_approval_service_pb2.CommentForecastModelApprovalRequest
    ) -> forecasting_v1_forecast_model_approval_service_pb2.CommentForecastModelApprovalResponse:
        """Comments a forecast model."""
        deps = self.deps
        response = forecasting_v1_forecast_model_approval_service_pb2.CommentForecastModelApprovalResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CommentForecastModelApproval', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'CommentForecastModelApproval',
                {'reason': request.reason}
            )
            await deps.repository.save_forecast_model(request.context.tenant_id, request.forecast_model)
            response_0 = identity_v1_user_validation_service_pb2.LintUsersResponse()
            response_1 = forecasting_v1_scenario_calculation_service_pb2.ExplainScenarioCalculationResponse()
            response_2 = forecasting_v1_scenario_validation_service_pb2.PreviewScenarioResponse()
            response_3 = featurestore_v1_entity_workflow_service_pb2.RetryEntityWorkflowResponse()
            outgoing_0 = identity_v1_user_validation_service_pb2.LintUsersRequest(
                context=request.context,
                details=identity_v1_user_validation_service_pb2.LintUsersRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(email=request.details.approver.email)
                ),
                user=identity_v1_identity_pb2.User(
                    relationship_manager=identity_v1_refs_pb2.UserRef(
                        display_name=request.forecast_model.owner.display_name
                    )
                )
            )
            document_0 = MessageToDict(outgoing_0, preserving_proto_field_name=True)
            outgoing_0 = ParseDict(document_0, identity_v1_user_validation_service_pb2.LintUsersRequest())
            response_0 = await deps.clients.identity_user_validation.LintUsers(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = forecasting_v1_scenario_calculation_service_pb2.ExplainScenarioCalculationRequest(
                context=request.context,
                scenario=forecasting_v1_forecasting_pb2.Scenario(
                    comments=[
                        forecasting_v1_forecasting_pb2.ScenarioComment(created_at=response_0.user.audit.created_at)
                    ]
                )
            )
            document_1 = MessageToJson(outgoing_1, preserving_proto_field_name=True)
            outgoing_1 = Parse(
                document_1,
                forecasting_v1_scenario_calculation_service_pb2.ExplainScenarioCalculationRequest()
            )
            response_1 = await deps.clients.forecasting_scenario_calculation.ExplainScenarioCalculation(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = forecasting_v1_scenario_validation_service_pb2.PreviewScenarioRequest()
            outgoing_2.context.CopyFrom(request.context)
            outgoing_2.scenario.audit.created_by = response_1.scenario.audit.created_by
            outgoing_2.details.contact.phone = response_0.user.contact.phone
            outgoing_2.scenario.requester.email = request.forecast_model.owner.email
            merged_2 = forecasting_v1_scenario_validation_service_pb2.PreviewScenarioRequest()
            merged_2.MergeFrom(outgoing_2)
            outgoing_2.CopyFrom(merged_2)
            response_2 = await deps.clients.forecasting_scenario_validation.PreviewScenario(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            outgoing_3 = featurestore_v1_entity_workflow_service_pb2.RetryEntityWorkflowRequest(
                context=request.context,
                entity=featurestore_v1_featurestore_pb2.Entity(
                    audit=common_v1_audit_pb2.AuditInfo(updated_by=response_0.user.audit.updated_by)
                )
            )
            envelope_3 = AnyMessage()
            envelope_3.Pack(outgoing_3)
            outgoing_3 = featurestore_v1_entity_workflow_service_pb2.RetryEntityWorkflowRequest()
            if not envelope_3.Unpack(outgoing_3):
                raise ValueError("partner envelope contains the wrong request type")
            response_3 = await deps.clients.featurestore_entity_workflow.RetryEntityWorkflow(
                outgoing_3,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.details
            response.result.details.update(returned_0_0)
            returned_1_0 = response_1.outcome.next_steps
            response.outcome.next_steps.extend(returned_1_0)
            returned_2_0 = response_2.outcome.status
            if returned_2_0:
                response.result.status = returned_2_0
            returned_2_1 = response_2.outcome.effective_at
            if returned_2_1.ListFields():
                response.outcome.effective_at.MergeFrom(returned_2_1)
            returned_3_0 = response_3.entity.audit.created_by
            if returned_3_0:
                response.forecast_model.audit.created_by = returned_3_0
            returned_3_1 = response_3.outcome.status
            if returned_3_1:
                response.result.status = returned_3_1
            echoed_0 = request.forecast_model_id
            response.forecast_model.forecast_model_id = echoed_0
            echoed_1 = request.forecast_model.code
            response.forecast_model.code = echoed_1
            return response

    async def handle_delegate_forecast_model_approval(
        self,
        request: forecasting_v1_forecast_model_approval_service_pb2.DelegateForecastModelApprovalRequest
    ) -> forecasting_v1_forecast_model_approval_service_pb2.DelegateForecastModelApprovalResponse:
        """Delegates a forecast model."""
        deps = self.deps
        response = forecasting_v1_forecast_model_approval_service_pb2.DelegateForecastModelApprovalResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('DelegateForecastModelApproval', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'DelegateForecastModelApproval',
                {'reason': request.reason}
            )
            await deps.repository.save_forecast_model(request.context.tenant_id, request.forecast_model)
            response_0 = modelregistry_v1_deployment_approval_service_pb2.SubmitDeploymentResponse()
            response_1 = modelregistry_v1_deployment_sync_service_pb2.PullDeploymentsResponse()
            outgoing_0 = modelregistry_v1_deployment_approval_service_pb2.SubmitDeploymentRequest(
                context=request.context,
                deployment=modelregistry_v1_modelregistry_pb2.Deployment(
                    location=common_v1_address_pb2.PostalAddress(
                        postal_code=request.forecast_model.address.postal_code,
                        recipient=request.forecast_model.address.recipient
                    ),
                    organizer=identity_v1_refs_pb2.UserRef(display_name=request.details.approver.display_name),
                    participants=[
                        modelregistry_v1_modelregistry_pb2.DeploymentParticipant(
                            contact=common_v1_contact_pb2.ContactInfo(email=request.forecast_model.owner.email)
                        )
                    ]
                )
            )
            registered_0 = cast(
                modelregistry_v1_deployment_approval_service_pb2_grpc.DeploymentApprovalServiceStub,
                deps.clients.registry['acme.modelregistry.v1.DeploymentApprovalService']
            )
            response_0 = await registered_0.SubmitDeployment(outgoing_0, timeout=deps.settings.timeout)
            command_1 = ForecastModelApprovalDelegateForecastModelApproval1Command(
                context=request.context,
                deployment_organizer_email=response_0.deployment.organizer.email,
                deployment_weekly_interval=response_0.deployment.daily.interval,
                deployment_participants_contact_email=request.forecast_model.owner.email,
                deployment_location_lines=list(request.forecast_model.address.lines)
            )
            outgoing_1 = to_forecast_model_approval_delegate_forecast_model_approval1_command(command_1)
            response_1 = await deps.clients.modelregistry_deployment_sync.PullDeployments(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.deployment.organizer.email
            if returned_0_0:
                response.forecast_model.owner.email = returned_0_0
            returned_1_0 = response_1.result.message
            if returned_1_0:
                response.result.message = returned_1_0
            returned_1_1 = response_1.outcome.effective_at
            if returned_1_1.ListFields():
                response.outcome.effective_at.MergeFrom(returned_1_1)
            echoed_0 = request.forecast_model_id
            response.forecast_model.forecast_model_id = echoed_0
            echoed_1 = request.forecast_model.code
            response.forecast_model.code = echoed_1
            return response

    async def handle_escalate_forecast_model(
        self,
        request: forecasting_v1_forecast_model_approval_service_pb2.EscalateForecastModelRequest
    ) -> forecasting_v1_forecast_model_approval_service_pb2.EscalateForecastModelResponse:
        """Escalates a forecast model."""
        deps = self.deps
        response = forecasting_v1_forecast_model_approval_service_pb2.EscalateForecastModelResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('EscalateForecastModel', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'EscalateForecastModel', {'reason': request.reason})
            await deps.repository.save_forecast_model(request.context.tenant_id, request.forecast_model)
            response_0 = ledger_v1_ledger_account_validation_service_pb2.NormalizeLedgerAccountResponse()
            response_1 = forecasting_v1_demand_forecast_validation_service_pb2.CheckDemandForecastEligibilityResponse()
            response_2 = ledger_v1_ledger_account_validation_service_pb2.ScoreLedgerAccountResponse()
            command_0 = ForecastModelApprovalEscalateForecastModel0Command.model_validate(
                {
                    'context': request.context,
                    'ledger_account_contact_email': request.details.approver.email,
                    'ledger_account_audit_updated_by': request.forecast_model.audit.updated_by,
                    'ledger_account_audit_created_by': request.forecast_model.audit.created_by,
                    'ledger_account_audit_created_at': request.forecast_model.audit.created_at
                }
            )
            outgoing_0 = to_forecast_model_approval_escalate_forecast_model0_command(command_0)
            response_0 = await deps.clients.ledger_ledger_account_validation.NormalizeLedgerAccount(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = forecasting_v1_demand_forecast_validation_service_pb2.CheckDemandForecastEligibilityRequest(
                context=request.context,
                demand_forecast=forecasting_v1_forecasting_pb2.DemandForecast(
                    card=forecasting_v1_forecasting_pb2.DemandForecastCardSettlement(
                        token=response_0.ledger_account.card.token
                    )
                )
            )
            send_1 = partial(
                deps.clients.forecasting_demand_forecast_validation.CheckDemandForecastEligibility,
                timeout=deps.settings.timeout
            )
            response_1 = await send_1(outgoing_1)
            outgoing_2 = ledger_v1_ledger_account_validation_service_pb2.ScoreLedgerAccountRequest(
                context=request.context,
                details=ledger_v1_ledger_account_validation_service_pb2.ScoreLedgerAccountRequest.Details(
                    destination=common_v1_address_pb2.PostalAddress(
                        lines=list(response_1.demand_forecast.billing_address.lines)
                    )
                ),
                ledger_account=ledger_v1_ledger_pb2.LedgerAccount(
                    audit=common_v1_audit_pb2.AuditInfo(
                        created_at=response_0.ledger_account.audit.created_at,
                        created_by=request.forecast_model.audit.created_by
                    ),
                    contact=common_v1_contact_pb2.ContactInfo(phone=response_0.ledger_account.contact.phone)
                )
            )
            response_2 = await hooks.forecast_model_approval_escalate_forecast_model2(
                deps.clients.ledger_ledger_account_validation,
                outgoing_2,
                deps.settings.timeout
            )
            returned_0_0 = response_0.outcome.message
            if returned_0_0:
                response.outcome.message = returned_0_0
            returned_1_0 = response_1.demand_forecast.audit.updated_by
            if returned_1_0:
                response.forecast_model.audit.updated_by = returned_1_0
            returned_1_1 = response_1.outcome.reference_id
            if returned_1_1:
                response.outcome.reference_id = returned_1_1
            returned_2_0 = response_2.ledger_account.audit.updated_at
            if returned_2_0.ListFields():
                response.forecast_model.audit.updated_at.MergeFrom(returned_2_0)
            returned_2_1 = response_2.ledger_account.audit.updated_by
            if returned_2_1:
                response.forecast_model.audit.updated_by = returned_2_1
            echoed_0 = request.forecast_model_id
            response.forecast_model.forecast_model_id = echoed_0
            echoed_1 = request.forecast_model.capacity
            response.forecast_model.capacity = echoed_1
            return response

    async def handle_get_forecast_model_approval_status(
        self,
        request: forecasting_v1_forecast_model_approval_service_pb2.GetForecastModelApprovalStatusRequest
    ) -> forecasting_v1_forecast_model_approval_service_pb2.GetForecastModelApprovalStatusResponse:
        """Returns a forecast model."""
        deps = self.deps
        response = forecasting_v1_forecast_model_approval_service_pb2.GetForecastModelApprovalStatusResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('GetForecastModelApprovalStatus', extra={'fields': {'domain': 'forecasting'}})
            await deps.repository.audit(request.context.tenant_id, 'GetForecastModelApprovalStatus', {})
            response_0 = modelregistry_v1_registered_model_workflow_service_pb2.ListRegisteredModelWorkflowsResponse()
            outgoing_0 = modelregistry_v1_registered_model_workflow_service_pb2.ListRegisteredModelWorkflowsRequest(
                context=request.context,
                filter=modelregistry_v1_registered_model_workflow_service_pb2.ListRegisteredModelWorkflowsRequest.Filter(
                    created_after=request.context.deadline,
                    labels=dict(request.context.baggage),
                    owner_id=request.forecast_model_id
                )
            )
            response_0 = await deps.clients.modelregistry_registered_model_workflow.ListRegisteredModelWorkflows(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.result.message = returned_0_0
            returned_0_1 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_1)
            echoed_0 = request.forecast_model_id
            response.forecast_model.forecast_model_id = echoed_0
            return response

    async def handle_list_pending_forecast_models(
        self,
        request: forecasting_v1_forecast_model_approval_service_pb2.ListPendingForecastModelsRequest
    ) -> forecasting_v1_forecast_model_approval_service_pb2.ListPendingForecastModelsResponse:
        """Lists forecast models a page at a time."""
        deps = self.deps
        response = forecasting_v1_forecast_model_approval_service_pb2.ListPendingForecastModelsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ListPendingForecastModels', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ListPendingForecastModels',
                {'order_by': request.order_by}
            )
            response_0 = pipelines_v1_pipeline_reporting_service_pb2.SharePipelineReportResponse()
            response_1 = notifications_v1_notification_validation_service_pb2.PreviewNotificationResponse()
            outgoing_0 = pipelines_v1_pipeline_reporting_service_pb2.SharePipelineReportRequest(
                context=request.context,
                details=pipelines_v1_pipeline_reporting_service_pb2.SharePipelineReportRequest.Details(
                    recipient=common_v1_contact_pb2.ContactInfo(email=request.context.actor.email),
                    variables=dict(request.filter.labels)
                )
            )
            response_0 = await deps.clients.pipelines_pipeline_reporting.SharePipelineReport(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = notifications_v1_notification_validation_service_pb2.PreviewNotificationRequest(
                context=request.context,
                notification=notifications_v1_notifications_pb2.Notification(
                    assignee=identity_v1_refs_pb2.UserRef(user_id=response_0.pipeline.organizer.user_id),
                    audit=common_v1_audit_pb2.AuditInfo(updated_at=response_0.pipeline.audit.updated_at),
                    customer=notifications_v1_refs_pb2.NotificationTemplateRef(
                        display_name=response_0.pipeline.organizer.display_name
                    )
                )
            )
            steps_1 = [
                partial(
                    deps.clients.notifications_notification_validation.PreviewNotification,
                    outgoing_1,
                    timeout=deps.settings.timeout
                )
            ]
            results_1 = await run_steps(steps_1)
            response_1 = results_1[-1]
            returned_0_0 = response_0.outcome.message
            if returned_0_0:
                response.result.message = returned_0_0
            returned_1_0 = response_1.outcome.status
            if returned_1_0:
                response.result.status = returned_1_0
            returned_1_1 = response_1.notification.audit.updated_at
            returned_1_1_part_0 = response.forecast_models.add()
            if returned_1_1.ListFields():
                returned_1_1_part_0.audit.updated_at.MergeFrom(returned_1_1)
            return response

    async def handle_reject_forecast_model(
        self,
        request: forecasting_v1_forecast_model_approval_service_pb2.RejectForecastModelRequest
    ) -> forecasting_v1_forecast_model_approval_service_pb2.RejectForecastModelResponse:
        """Rejects a forecast model."""
        deps = self.deps
        response = forecasting_v1_forecast_model_approval_service_pb2.RejectForecastModelResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('RejectForecastModel', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'RejectForecastModel', {'reason': request.reason})
            await deps.repository.save_forecast_model(request.context.tenant_id, request.forecast_model)
            response_0 = documents_v1_document_validation_service_pb2.CheckDocumentEligibilityResponse()
            outgoing_0 = documents_v1_document_validation_service_pb2.CheckDocumentEligibilityRequest(
                context=request.context,
                document=documents_v1_documents_pb2.Document(
                    counterparty=documents_v1_refs_pb2.DocumentFolderRef(
                        display_name=request.forecast_model.owner.display_name
                    )
                )
            )
            response_0 = await ForecastModelApprovalRejectForecastModel0Adapter(
                deps.clients.documents_document_validation,
                deps.settings.timeout
            )(outgoing_0)
            returned_0_0 = response_0.outcome.status
            if returned_0_0:
                response.result.status = returned_0_0
            echoed_0 = request.forecast_model_id
            response.forecast_model.forecast_model_id = echoed_0
            echoed_1 = request.details.effective_at
            response.outcome.effective_at.CopyFrom(echoed_1)
            return response

    async def handle_submit_forecast_model(
        self,
        request: forecasting_v1_forecast_model_approval_service_pb2.SubmitForecastModelRequest
    ) -> forecasting_v1_forecast_model_approval_service_pb2.SubmitForecastModelResponse:
        """Submits a forecast model."""
        deps = self.deps
        response = forecasting_v1_forecast_model_approval_service_pb2.SubmitForecastModelResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SubmitForecastModel', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'SubmitForecastModel', {'reason': request.reason})
            await deps.repository.save_forecast_model(request.context.tenant_id, request.forecast_model)
            response_0 = identity_v1_user_query_service_pb2.ExportUsersResponse()
            response_1 = notifications_v1_notification_validation_service_pb2.NormalizeNotificationResponse()
            outgoing_0 = identity_v1_user_query_service_pb2.ExportUsersRequest(
                context=request.context,
                filter=identity_v1_user_query_service_pb2.ExportUsersRequest.Filter(
                    created_after=request.forecast_model.audit.created_at,
                    labels=dict(request.annotations),
                    owner_id=request.details.approver.user_id,
                    region=request.forecast_model.address.region
                )
            )
            async for chunk_0 in deps.clients.identity_user_query.ExportUsers(
                outgoing_0,
                timeout=deps.settings.timeout
            ):
                response_0 = chunk_0
            outgoing_1 = notifications_v1_notification_validation_service_pb2.NormalizeNotificationRequest(
                context=request.context,
                notification=notifications_v1_notifications_pb2.Notification(
                    assignee=identity_v1_refs_pb2.UserRef(user_id=request.forecast_model.owner.user_id),
                    audit=common_v1_audit_pb2.AuditInfo(
                        etag=request.forecast_model.audit.etag,
                        updated_by=request.forecast_model.audit.updated_by
                    ),
                    customer=notifications_v1_refs_pb2.NotificationTemplateRef(
                        display_name=request.forecast_model.owner.display_name
                    )
                )
            )
            response_1 = await deps.clients.notifications_notification_validation.NormalizeNotification(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_1_0 = response_1.notification.requester.email
            if returned_1_0:
                response.forecast_model.owner.email = returned_1_0
            echoed_0 = request.forecast_model_id
            response.forecast_model.forecast_model_id = echoed_0
            echoed_1 = request.forecast_model.status
            response.forecast_model.status = echoed_1
            return response
