"""Routes demand forecasts through approval, with escalation and delegation."""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any
from typing import cast
import logging

from google.protobuf.any_pb2 import Any as AnyMessage
from google.protobuf.json_format import MessageToDict
from google.protobuf.json_format import MessageToJson
from google.protobuf.json_format import Parse
from google.protobuf.json_format import ParseDict
import grpc

from acme.authorization.v1 import access_policy_service_pb2 as authorization_v1_access_policy_service_pb2
from acme.authorization.v1 import (
    access_policy_validation_service_pb2 as authorization_v1_access_policy_validation_service_pb2,
)
from acme.authorization.v1 import authorization_pb2 as authorization_v1_authorization_pb2
from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.documents.v1 import document_validation_service_pb2 as documents_v1_document_validation_service_pb2
from acme.documents.v1 import documents_pb2 as documents_v1_documents_pb2
from acme.featurestore.v1 import entity_approval_service_pb2 as featurestore_v1_entity_approval_service_pb2
from acme.featurestore.v1 import entity_approval_service_pb2_grpc as featurestore_v1_entity_approval_service_pb2_grpc
from acme.forecasting.v1 import (
    demand_forecast_approval_service_pb2 as forecasting_v1_demand_forecast_approval_service_pb2,
)
from acme.forecasting.v1 import (
    demand_forecast_approval_service_pb2_grpc as forecasting_v1_demand_forecast_approval_service_pb2_grpc,
)
from acme.forecasting.v1 import (
    forecast_model_validation_service_pb2 as forecasting_v1_forecast_model_validation_service_pb2,
)
from acme.forecasting.v1 import forecasting_pb2 as forecasting_v1_forecasting_pb2
from acme.forecasting.v1 import scenario_calculation_service_pb2 as forecasting_v1_scenario_calculation_service_pb2
from acme.forecasting.v1 import scenario_validation_service_pb2 as forecasting_v1_scenario_validation_service_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2

from acme_data.domains.forecasting.dependencies import Dependencies
from acme_data.domains.forecasting.models import DemandForecastApprovalSubmitDemandForecast1Command
from acme_data.domains.forecasting.models import DemandForecastApprovalSubmitDemandForecast2Command
from acme_data.domains.forecasting.models import to_demand_forecast_approval_submit_demand_forecast1_command
from acme_data.domains.forecasting.models import to_demand_forecast_approval_submit_demand_forecast2_command
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class DemandForecastApprovalServicer(
    forecasting_v1_demand_forecast_approval_service_pb2_grpc.DemandForecastApprovalServiceServicer
):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    async def ApproveDemandForecast(
        self, request: forecasting_v1_demand_forecast_approval_service_pb2.ApproveDemandForecastRequest, context: grpc.aio.ServicerContext,
    ) -> forecasting_v1_demand_forecast_approval_service_pb2.ApproveDemandForecastResponse:
        """Approves a demand forecast."""
        return await self.handle_approve_demand_forecast(request)

    @rpc_errors
    async def CommentDemandForecastApproval(
        self, request: forecasting_v1_demand_forecast_approval_service_pb2.CommentDemandForecastApprovalRequest, context: grpc.aio.ServicerContext,
    ) -> forecasting_v1_demand_forecast_approval_service_pb2.CommentDemandForecastApprovalResponse:
        """Comments a demand forecast."""
        return await self.handle_comment_demand_forecast_approval(request)

    @rpc_errors
    async def EscalateDemandForecast(
        self, request: forecasting_v1_demand_forecast_approval_service_pb2.EscalateDemandForecastRequest, context: grpc.aio.ServicerContext,
    ) -> forecasting_v1_demand_forecast_approval_service_pb2.EscalateDemandForecastResponse:
        """Escalates a demand forecast."""
        return await self.handle_escalate_demand_forecast(request)

    @rpc_errors
    @retry_transient
    async def ListPendingDemandForecasts(
        self, request: forecasting_v1_demand_forecast_approval_service_pb2.ListPendingDemandForecastsRequest, context: grpc.aio.ServicerContext,
    ) -> forecasting_v1_demand_forecast_approval_service_pb2.ListPendingDemandForecastsResponse:
        """Lists demand forecasts a page at a time."""
        return await self.handle_list_pending_demand_forecasts(request)

    @rpc_errors
    async def RejectDemandForecast(
        self, request: forecasting_v1_demand_forecast_approval_service_pb2.RejectDemandForecastRequest, context: grpc.aio.ServicerContext,
    ) -> forecasting_v1_demand_forecast_approval_service_pb2.RejectDemandForecastResponse:
        """Rejects a demand forecast."""
        return await self.handle_reject_demand_forecast(request)

    @rpc_errors
    async def SubmitDemandForecast(
        self, request: forecasting_v1_demand_forecast_approval_service_pb2.SubmitDemandForecastRequest, context: grpc.aio.ServicerContext,
    ) -> forecasting_v1_demand_forecast_approval_service_pb2.SubmitDemandForecastResponse:
        """Submits a demand forecast."""
        return await self.handle_submit_demand_forecast(request)

    async def handle_approve_demand_forecast(
        self,
        request: forecasting_v1_demand_forecast_approval_service_pb2.ApproveDemandForecastRequest
    ) -> forecasting_v1_demand_forecast_approval_service_pb2.ApproveDemandForecastResponse:
        """Approves a demand forecast."""
        deps = self.deps
        response = forecasting_v1_demand_forecast_approval_service_pb2.ApproveDemandForecastResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ApproveDemandForecast', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'ApproveDemandForecast', {'reason': request.reason})
            await deps.repository.save_demand_forecast(request.context.tenant_id, request.demand_forecast)
            response_0 = documents_v1_document_validation_service_pb2.ValidateDocumentResponse()
            outgoing_0 = documents_v1_document_validation_service_pb2.ValidateDocumentRequest(
                context=request.context,
                document=documents_v1_documents_pb2.Document(
                    billing_address=common_v1_address_pb2.PostalAddress(
                        recipient=request.demand_forecast.billing_address.recipient
                    )
                )
            )
            response_0 = cast(documents_v1_document_validation_service_pb2.ValidateDocumentResponse, await deps.bus.request(
                'acme.forecasting.v1.DemandForecastApprovalService/ApproveDemandForecast/0', outgoing_0, deps.settings.timeout,
            ))
            returned_0_0 = response_0.document.billing_address.lines
            response.demand_forecast.billing_address.lines.extend(returned_0_0)
            returned_0_1 = response_0.document.audit.etag
            if returned_0_1:
                response.demand_forecast.audit.etag = returned_0_1
            echoed_0 = request.demand_forecast_id
            response.demand_forecast.demand_forecast_id = echoed_0
            echoed_1 = request.demand_forecast.due_at
            response.demand_forecast.due_at.CopyFrom(echoed_1)
            return response

    async def handle_comment_demand_forecast_approval(
        self,
        request: forecasting_v1_demand_forecast_approval_service_pb2.CommentDemandForecastApprovalRequest
    ) -> forecasting_v1_demand_forecast_approval_service_pb2.CommentDemandForecastApprovalResponse:
        """Comments a demand forecast."""
        deps = self.deps
        response = forecasting_v1_demand_forecast_approval_service_pb2.CommentDemandForecastApprovalResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CommentDemandForecastApproval', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'CommentDemandForecastApproval',
                {'reason': request.reason}
            )
            await deps.repository.save_demand_forecast(request.context.tenant_id, request.demand_forecast)
            response_0 = forecasting_v1_scenario_validation_service_pb2.PreviewScenarioResponse()
            response_1 = authorization_v1_access_policy_validation_service_pb2.PreviewAccessPolicyResponse()
            outgoing_0 = forecasting_v1_scenario_validation_service_pb2.PreviewScenarioRequest(
                context=request.context,
                scenario=forecasting_v1_forecasting_pb2.Scenario(
                    audit=common_v1_audit_pb2.AuditInfo(updated_at=request.demand_forecast.audit.updated_at)
                )
            )
            response_0 = await deps.clients.forecasting_scenario_validation.PreviewScenario(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = authorization_v1_access_policy_validation_service_pb2.PreviewAccessPolicyRequest(
                access_policy=authorization_v1_authorization_pb2.AccessPolicy(
                    audit=common_v1_audit_pb2.AuditInfo(updated_by=response_0.scenario.audit.updated_by),
                    owner=identity_v1_refs_pb2.UserRef(
                        email=response_0.scenario.assignee.email,
                        user_id=request.details.approver.user_id
                    )
                ),
                context=request.context,
                details=authorization_v1_access_policy_validation_service_pb2.PreviewAccessPolicyRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(phone=response_0.scenario.requester.phone)
                )
            )
            method_name_1 = 'PreviewAccessPolicy'
            response_1 = await getattr(
                deps.clients.authorization_access_policy_validation,
                method_name_1
            )(outgoing_1, timeout=deps.settings.timeout)
            returned_0_0 = response_0.outcome.next_steps
            response.outcome.next_steps.extend(returned_0_0)
            returned_1_0 = response_1.outcome.status
            if returned_1_0:
                response.outcome.status = returned_1_0
            returned_1_1 = response_1.access_policy.audit.etag
            if returned_1_1:
                response.demand_forecast.audit.etag = returned_1_1
            echoed_0 = request.demand_forecast_id
            response.demand_forecast.demand_forecast_id = echoed_0
            echoed_1 = request.demand_forecast.notes
            response.demand_forecast.notes = echoed_1
            return response

    async def handle_escalate_demand_forecast(
        self,
        request: forecasting_v1_demand_forecast_approval_service_pb2.EscalateDemandForecastRequest
    ) -> forecasting_v1_demand_forecast_approval_service_pb2.EscalateDemandForecastResponse:
        """Escalates a demand forecast."""
        deps = self.deps
        response = forecasting_v1_demand_forecast_approval_service_pb2.EscalateDemandForecastResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('EscalateDemandForecast', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'EscalateDemandForecast', {'reason': request.reason})
            await deps.repository.save_demand_forecast(request.context.tenant_id, request.demand_forecast)
            response_0 = forecasting_v1_forecast_model_validation_service_pb2.ValidateForecastModelResponse()
            response_1 = authorization_v1_access_policy_service_pb2.UpdateAccessPolicyResponse()
            response_2 = forecasting_v1_scenario_validation_service_pb2.CheckScenarioEligibilityResponse()
            fields_0: dict[str, Any] = {
                'context': request.context,
                'forecast_model': {
                    'address': {
                        'country_code': request.demand_forecast.billing_address.country_code,
                        'locality': request.demand_forecast.billing_address.locality,
                        'recipient': request.demand_forecast.billing_address.recipient
                    },
                    'owner': {'display_name': request.demand_forecast.counterparty.display_name}
                }
            }
            outgoing_0 = forecasting_v1_forecast_model_validation_service_pb2.ValidateForecastModelRequest(**fields_0)
            response_0 = await deps.clients.forecasting_forecast_model_validation.ValidateForecastModel(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = authorization_v1_access_policy_service_pb2.UpdateAccessPolicyRequest(
                access_policy=authorization_v1_authorization_pb2.AccessPolicy(
                    audit=common_v1_audit_pb2.AuditInfo(created_at=response_0.forecast_model.audit.created_at),
                    owner=identity_v1_refs_pb2.UserRef(
                        display_name=request.demand_forecast.counterparty.display_name,
                        user_id=request.details.approver.user_id
                    )
                ),
                context=request.context
            )
            document_1 = MessageToDict(outgoing_1, preserving_proto_field_name=True)
            outgoing_1 = ParseDict(document_1, authorization_v1_access_policy_service_pb2.UpdateAccessPolicyRequest())
            response_1 = await deps.clients.authorization_access_policy.UpdateAccessPolicy(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = forecasting_v1_scenario_validation_service_pb2.CheckScenarioEligibilityRequest(
                context=request.context,
                scenario=forecasting_v1_forecasting_pb2.Scenario(
                    audit=common_v1_audit_pb2.AuditInfo(
                        created_by=response_1.access_policy.audit.created_by,
                        updated_at=response_0.forecast_model.audit.updated_at
                    ),
                    comments=[
                        forecasting_v1_forecasting_pb2.ScenarioComment(
                            created_at=request.demand_forecast.audit.created_at
                        )
                    ]
                )
            )
            document_2 = MessageToJson(outgoing_2, preserving_proto_field_name=True)
            outgoing_2 = Parse(
                document_2,
                forecasting_v1_scenario_validation_service_pb2.CheckScenarioEligibilityRequest()
            )
            response_2 = await deps.clients.forecasting_scenario_validation.CheckScenarioEligibility(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.forecast_model.address.recipient
            if returned_0_0:
                response.demand_forecast.billing_address.recipient = returned_0_0
            returned_1_0 = response_1.result.message
            if returned_1_0:
                response.result.message = returned_1_0
            returned_1_1 = response_1.result.details
            response.result.details.update(returned_1_1)
            returned_2_0 = response_2.scenario.audit.updated_at
            if returned_2_0.ListFields():
                response.demand_forecast.audit.updated_at.MergeFrom(returned_2_0)
            echoed_0 = request.demand_forecast_id
            response.demand_forecast.demand_forecast_id = echoed_0
            echoed_1 = request.demand_forecast.issued_at
            response.demand_forecast.issued_at.CopyFrom(echoed_1)
            return response

    async def handle_list_pending_demand_forecasts(
        self,
        request: forecasting_v1_demand_forecast_approval_service_pb2.ListPendingDemandForecastsRequest
    ) -> forecasting_v1_demand_forecast_approval_service_pb2.ListPendingDemandForecastsResponse:
        """Lists demand forecasts a page at a time."""
        deps = self.deps
        response = forecasting_v1_demand_forecast_approval_service_pb2.ListPendingDemandForecastsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ListPendingDemandForecasts', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ListPendingDemandForecasts',
                {'order_by': request.order_by}
            )
            response_0 = forecasting_v1_forecast_model_validation_service_pb2.NormalizeForecastModelResponse()
            outgoing_0 = forecasting_v1_forecast_model_validation_service_pb2.NormalizeForecastModelRequest(
                context=request.context,
                details=forecasting_v1_forecast_model_validation_service_pb2.NormalizeForecastModelRequest.Details(
                    locale=request.context.locale
                ),
                forecast_model=forecasting_v1_forecasting_pb2.ForecastModel(
                    address=common_v1_address_pb2.PostalAddress(region=request.filter.region)
                )
            )
            response_0 = await deps.clients.forecasting_forecast_model_validation.NormalizeForecastModel(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.forecast_model.audit.updated_by
            returned_0_0_part_0 = response.demand_forecasts.add()
            if returned_0_0:
                returned_0_0_part_0.audit.updated_by = returned_0_0
            return response

    async def handle_reject_demand_forecast(
        self,
        request: forecasting_v1_demand_forecast_approval_service_pb2.RejectDemandForecastRequest
    ) -> forecasting_v1_demand_forecast_approval_service_pb2.RejectDemandForecastResponse:
        """Rejects a demand forecast."""
        deps = self.deps
        response = forecasting_v1_demand_forecast_approval_service_pb2.RejectDemandForecastResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('RejectDemandForecast', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'RejectDemandForecast', {'reason': request.reason})
            await deps.repository.save_demand_forecast(request.context.tenant_id, request.demand_forecast)
            response_0 = forecasting_v1_forecast_model_validation_service_pb2.PreviewForecastModelResponse()
            outgoing_0 = forecasting_v1_forecast_model_validation_service_pb2.PreviewForecastModelRequest(
                context=request.context,
                forecast_model=forecasting_v1_forecasting_pb2.ForecastModel(
                    address=common_v1_address_pb2.PostalAddress(
                        lines=list(request.demand_forecast.billing_address.lines)
                    ),
                    owner=identity_v1_refs_pb2.UserRef(user_id=request.details.approver.user_id)
                )
            )
            envelope_0 = AnyMessage()
            envelope_0.Pack(outgoing_0)
            outgoing_0 = forecasting_v1_forecast_model_validation_service_pb2.PreviewForecastModelRequest()
            if not envelope_0.Unpack(outgoing_0):
                raise ValueError("partner envelope contains the wrong request type")
            response_0 = await deps.clients.forecasting_forecast_model_validation.PreviewForecastModel(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.forecast_model.address.recipient
            if returned_0_0:
                response.demand_forecast.billing_address.recipient = returned_0_0
            echoed_0 = request.demand_forecast_id
            response.demand_forecast.demand_forecast_id = echoed_0
            echoed_1 = request.demand_forecast.status
            response.demand_forecast.status = echoed_1
            return response

    async def handle_submit_demand_forecast(
        self,
        request: forecasting_v1_demand_forecast_approval_service_pb2.SubmitDemandForecastRequest
    ) -> forecasting_v1_demand_forecast_approval_service_pb2.SubmitDemandForecastResponse:
        """Submits a demand forecast."""
        deps = self.deps
        response = forecasting_v1_demand_forecast_approval_service_pb2.SubmitDemandForecastResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SubmitDemandForecast', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'SubmitDemandForecast', {'reason': request.reason})
            await deps.repository.save_demand_forecast(request.context.tenant_id, request.demand_forecast)
            response_0 = featurestore_v1_entity_approval_service_pb2.SubmitEntityResponse()
            response_1 = forecasting_v1_scenario_calculation_service_pb2.EstimateScenarioResponse()
            response_2 = forecasting_v1_forecast_model_validation_service_pb2.CheckForecastModelEligibilityResponse()
            outgoing_0 = featurestore_v1_entity_approval_service_pb2.SubmitEntityRequest(
                context=request.context,
                details=featurestore_v1_entity_approval_service_pb2.SubmitEntityRequest.Details(
                    approver=identity_v1_refs_pb2.UserRef(display_name=request.details.approver.display_name)
                )
            )
            registered_0 = cast(
                featurestore_v1_entity_approval_service_pb2_grpc.EntityApprovalServiceStub,
                deps.clients.registry['acme.featurestore.v1.EntityApprovalService']
            )
            response_0 = await registered_0.SubmitEntity(outgoing_0, timeout=deps.settings.timeout)
            command_1 = DemandForecastApprovalSubmitDemandForecast1Command(
                context=request.context,
                details_destination_postal_code=request.demand_forecast.billing_address.postal_code,
                scenario_audit_updated_at=response_0.entity.audit.updated_at
            )
            outgoing_1 = to_demand_forecast_approval_submit_demand_forecast1_command(command_1)
            response_1 = await deps.clients.forecasting_scenario_calculation.EstimateScenario(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            command_2 = DemandForecastApprovalSubmitDemandForecast2Command.model_validate(
                {
                    'context': request.context,
                    'details_contact_phone': response_1.scenario.requester.phone,
                    'forecast_model_audit_created_by': response_0.entity.audit.created_by,
                    'forecast_model_address_postal_code': response_0.entity.primary_address.postal_code,
                    'forecast_model_audit_updated_at': response_0.entity.audit.updated_at
                }
            )
            outgoing_2 = to_demand_forecast_approval_submit_demand_forecast2_command(command_2)
            response_2 = await deps.clients.forecasting_forecast_model_validation.CheckForecastModelEligibility(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.entity.primary_address.postal_code
            if returned_0_0:
                response.demand_forecast.billing_address.postal_code = returned_0_0
            returned_1_0 = response_1.scenario.audit.created_by
            if returned_1_0:
                response.demand_forecast.audit.created_by = returned_1_0
            returned_2_0 = response_2.forecast_model.audit.updated_by
            if returned_2_0:
                response.demand_forecast.audit.updated_by = returned_2_0
            echoed_0 = request.demand_forecast_id
            response.demand_forecast.demand_forecast_id = echoed_0
            echoed_1 = request.demand_forecast.metadata
            response.demand_forecast.metadata.update(echoed_1)
            return response
