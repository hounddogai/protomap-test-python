"""Runs the long-lived workflow that takes a recommendation set from start to finish."""

from __future__ import annotations

from collections.abc import AsyncIterator
from collections.abc import Awaitable
from collections.abc import Callable
from dataclasses import dataclass
from functools import partial
from typing import Any
from typing import cast
import asyncio
import logging

from google.protobuf.any_pb2 import Any as AnyMessage
from google.protobuf.json_format import MessageToDict
from google.protobuf.json_format import ParseDict
import grpc

from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.customers.v1 import customer_calculation_service_pb2 as customers_v1_customer_calculation_service_pb2
from acme.customers.v1 import customer_service_pb2 as customers_v1_customer_service_pb2
from acme.customers.v1 import customers_pb2 as customers_v1_customers_pb2
from acme.customers.v1 import household_calculation_service_pb2 as customers_v1_household_calculation_service_pb2
from acme.customers.v1 import preference_validation_service_pb2 as customers_v1_preference_validation_service_pb2
from acme.customers.v1 import (
    preference_validation_service_pb2_grpc as customers_v1_preference_validation_service_pb2_grpc,
)
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.ledger.v1 import ledger_account_service_pb2 as ledger_v1_ledger_account_service_pb2
from acme.ledger.v1 import ledger_pb2 as ledger_v1_ledger_pb2
from acme.modelregistry.v1 import deployment_workflow_service_pb2 as modelregistry_v1_deployment_workflow_service_pb2
from acme.recommendations.v1 import (
    interaction_lifecycle_service_pb2 as recommendations_v1_interaction_lifecycle_service_pb2,
)
from acme.recommendations.v1 import (
    recommendation_model_approval_service_pb2 as recommendations_v1_recommendation_model_approval_service_pb2,
)
from acme.recommendations.v1 import (
    recommendation_model_calculation_service_pb2 as recommendations_v1_recommendation_model_calculation_service_pb2,
)
from acme.recommendations.v1 import (
    recommendation_model_validation_service_pb2 as recommendations_v1_recommendation_model_validation_service_pb2,
)
from acme.recommendations.v1 import (
    recommendation_set_validation_service_pb2 as recommendations_v1_recommendation_set_validation_service_pb2,
)
from acme.recommendations.v1 import (
    recommendation_set_workflow_service_pb2 as recommendations_v1_recommendation_set_workflow_service_pb2,
)
from acme.recommendations.v1 import (
    recommendation_set_workflow_service_pb2_grpc as recommendations_v1_recommendation_set_workflow_service_pb2_grpc,
)
from acme.recommendations.v1 import recommendations_pb2 as recommendations_v1_recommendations_pb2

from acme_data.domains.recommendations import hooks
from acme_data.domains.recommendations.adapters import RecommendationSetWorkflowRetryRecommendationSetWorkflow2Adapter
from acme_data.domains.recommendations.adapters import RecommendationSetWorkflowRetryRecommendationSetWorkflow2Port
from acme_data.domains.recommendations.adapters import RecommendationSetWorkflowSignalRecommendationSetWorkflow1Adapter
from acme_data.domains.recommendations.dependencies import Dependencies
from acme_data.domains.recommendations.models import RecommendationSetWorkflowResumeRecommendationSetWorkflow0Command
from acme_data.domains.recommendations.models import (
    to_recommendation_set_workflow_resume_recommendation_set_workflow0_command,
)
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import run_steps
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_id
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


@dataclass(slots=True)
class RecommendationSetWorkflowServicer(
    recommendations_v1_recommendation_set_workflow_service_pb2_grpc.RecommendationSetWorkflowServiceServicer
):
    deps: Dependencies

    @rpc_errors
    async def AdvanceRecommendationSetWorkflow(
        self, request: recommendations_v1_recommendation_set_workflow_service_pb2.AdvanceRecommendationSetWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> recommendations_v1_recommendation_set_workflow_service_pb2.AdvanceRecommendationSetWorkflowResponse:
        """Advances a recommendation set."""
        return await self.handle_advance_recommendation_set_workflow(request)

    @rpc_errors
    async def CancelRecommendationSetWorkflow(
        self, request: recommendations_v1_recommendation_set_workflow_service_pb2.CancelRecommendationSetWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> recommendations_v1_recommendation_set_workflow_service_pb2.CancelRecommendationSetWorkflowResponse:
        """Cancels a recommendation set."""
        return await self.handle_cancel_recommendation_set_workflow(request)

    @rpc_errors
    @retry_transient
    async def InspectRecommendationSetWorkflow(
        self, request: recommendations_v1_recommendation_set_workflow_service_pb2.InspectRecommendationSetWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> recommendations_v1_recommendation_set_workflow_service_pb2.InspectRecommendationSetWorkflowResponse:
        """Returns a recommendation set."""
        return await self.handle_inspect_recommendation_set_workflow(request)

    @rpc_errors
    @retry_transient
    async def ListRecommendationSetWorkflows(
        self, request: recommendations_v1_recommendation_set_workflow_service_pb2.ListRecommendationSetWorkflowsRequest, context: grpc.aio.ServicerContext,
    ) -> recommendations_v1_recommendation_set_workflow_service_pb2.ListRecommendationSetWorkflowsResponse:
        """Lists recommendation sets a page at a time."""
        return await self.handle_list_recommendation_set_workflows(request)

    @rpc_errors
    async def ResumeRecommendationSetWorkflow(
        self, request: recommendations_v1_recommendation_set_workflow_service_pb2.ResumeRecommendationSetWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> recommendations_v1_recommendation_set_workflow_service_pb2.ResumeRecommendationSetWorkflowResponse:
        """Resumes a recommendation set."""
        return await self.handle_resume_recommendation_set_workflow(request)

    @rpc_errors
    async def RetryRecommendationSetWorkflow(
        self, request: recommendations_v1_recommendation_set_workflow_service_pb2.RetryRecommendationSetWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> recommendations_v1_recommendation_set_workflow_service_pb2.RetryRecommendationSetWorkflowResponse:
        """Retrys a recommendation set."""
        return await self.handle_retry_recommendation_set_workflow(request)

    @rpc_errors
    async def SignalRecommendationSetWorkflow(
        self, request: recommendations_v1_recommendation_set_workflow_service_pb2.SignalRecommendationSetWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> recommendations_v1_recommendation_set_workflow_service_pb2.SignalRecommendationSetWorkflowResponse:
        """Signals a recommendation set."""
        return await self.handle_signal_recommendation_set_workflow(request)

    @rpc_errors
    async def StartRecommendationSetWorkflow(
        self, request: recommendations_v1_recommendation_set_workflow_service_pb2.StartRecommendationSetWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> recommendations_v1_recommendation_set_workflow_service_pb2.StartRecommendationSetWorkflowResponse:
        """Starts a recommendation set."""
        return await self.handle_start_recommendation_set_workflow(request)

    async def handle_advance_recommendation_set_workflow(
        self,
        request: recommendations_v1_recommendation_set_workflow_service_pb2.AdvanceRecommendationSetWorkflowRequest
    ) -> recommendations_v1_recommendation_set_workflow_service_pb2.AdvanceRecommendationSetWorkflowResponse:
        """Advances a recommendation set."""
        deps = self.deps
        response = recommendations_v1_recommendation_set_workflow_service_pb2.AdvanceRecommendationSetWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('AdvanceRecommendationSetWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'AdvanceRecommendationSetWorkflow',
                {'reason': request.reason}
            )
            await deps.repository.save_recommendation_set(request.context.tenant_id, request.recommendation_set)
            response_0 = recommendations_v1_interaction_lifecycle_service_pb2.ScheduleInteractionExpiryResponse()
            outgoing_0 = recommendations_v1_interaction_lifecycle_service_pb2.ScheduleInteractionExpiryRequest()
            outgoing_0.context.CopyFrom(request.context)
            outgoing_0.interaction.subject.display_name = request.recommendation_set.counterparty.display_name
            merged_0 = recommendations_v1_interaction_lifecycle_service_pb2.ScheduleInteractionExpiryRequest()
            merged_0.MergeFrom(outgoing_0)
            outgoing_0.CopyFrom(merged_0)
            response_0 = await deps.clients.recommendations_interaction_lifecycle.ScheduleInteractionExpiry(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.interaction.subject.customer_id
            if returned_0_0:
                response.recommendation_set.counterparty.customer_id = returned_0_0
            echoed_0 = request.recommendation_set_id
            response.recommendation_set.recommendation_set_id = echoed_0
            echoed_1 = request.recommendation_set.metadata
            response.recommendation_set.metadata.update(echoed_1)
            return response

    async def handle_cancel_recommendation_set_workflow(
        self,
        request: recommendations_v1_recommendation_set_workflow_service_pb2.CancelRecommendationSetWorkflowRequest
    ) -> recommendations_v1_recommendation_set_workflow_service_pb2.CancelRecommendationSetWorkflowResponse:
        """Cancels a recommendation set."""
        deps = self.deps
        response = recommendations_v1_recommendation_set_workflow_service_pb2.CancelRecommendationSetWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CancelRecommendationSetWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'CancelRecommendationSetWorkflow',
                {'reason': request.reason}
            )
            await deps.repository.save_recommendation_set(request.context.tenant_id, request.recommendation_set)
            response_0 = recommendations_v1_recommendation_model_validation_service_pb2.CheckRecommendationModelEligibilityResponse()
            response_1 = customers_v1_preference_validation_service_pb2.ValidatePreferenceResponse()
            outgoing_0 = recommendations_v1_recommendation_model_validation_service_pb2.CheckRecommendationModelEligibilityRequest(
                context=request.context,
                details=recommendations_v1_recommendation_model_validation_service_pb2.CheckRecommendationModelEligibilityRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(email=request.recommendation_set.counterparty.email)
                ),
                recommendation_model=recommendations_v1_recommendations_pb2.RecommendationModel(
                    address=common_v1_address_pb2.PostalAddress(
                        lines=list(request.recommendation_set.billing_address.lines)
                    )
                )
            )
            envelope_0 = AnyMessage()
            envelope_0.Pack(outgoing_0)
            outgoing_0 = recommendations_v1_recommendation_model_validation_service_pb2.CheckRecommendationModelEligibilityRequest()
            if not envelope_0.Unpack(outgoing_0):
                raise ValueError("partner envelope contains the wrong request type")
            response_0 = await deps.clients.recommendations_recommendation_model_validation.CheckRecommendationModelEligibility(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = customers_v1_preference_validation_service_pb2.ValidatePreferenceRequest(
                context=request.context,
                preference=customers_v1_customers_pb2.Preference(
                    audit=common_v1_audit_pb2.AuditInfo(etag=response_0.recommendation_model.audit.etag)
                )
            )
            registered_1 = cast(
                customers_v1_preference_validation_service_pb2_grpc.PreferenceValidationServiceStub,
                deps.clients.registry['acme.customers.v1.PreferenceValidationService']
            )
            response_1 = await registered_1.ValidatePreference(outgoing_1, timeout=deps.settings.timeout)
            returned_0_0 = response_0.result.status
            if returned_0_0:
                response.result.status = returned_0_0
            returned_0_1 = response_0.recommendation_model.components.get(
                'primary',
                recommendations_v1_recommendations_pb2.RecommendationModelComponent()
            ).quantity
            returned_0_1_part_1 = response.recommendation_set.lines.add()
            if returned_0_1:
                returned_0_1_part_1.quantity = returned_0_1
            returned_1_0 = response_1.outcome.message
            if returned_1_0:
                response.result.message = returned_1_0
            echoed_0 = request.recommendation_set_id
            response.recommendation_set.recommendation_set_id = echoed_0
            echoed_1 = request.recommendation_set.number
            response.recommendation_set.number = echoed_1
            return response

    async def handle_inspect_recommendation_set_workflow(
        self,
        request: recommendations_v1_recommendation_set_workflow_service_pb2.InspectRecommendationSetWorkflowRequest
    ) -> recommendations_v1_recommendation_set_workflow_service_pb2.InspectRecommendationSetWorkflowResponse:
        """Returns a recommendation set."""
        deps = self.deps
        response = recommendations_v1_recommendation_set_workflow_service_pb2.InspectRecommendationSetWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('InspectRecommendationSetWorkflow', extra={'fields': {'locale': request.context.locale}})
            await deps.repository.audit(
                request.context.tenant_id,
                'InspectRecommendationSetWorkflow',
                {'locale': request.context.locale}
            )
            echoed_0 = request.recommendation_set_id
            response.recommendation_set.recommendation_set_id = echoed_0
            return response

    async def handle_list_recommendation_set_workflows(
        self,
        request: recommendations_v1_recommendation_set_workflow_service_pb2.ListRecommendationSetWorkflowsRequest
    ) -> recommendations_v1_recommendation_set_workflow_service_pb2.ListRecommendationSetWorkflowsResponse:
        """Lists recommendation sets a page at a time."""
        deps = self.deps
        response = recommendations_v1_recommendation_set_workflow_service_pb2.ListRecommendationSetWorkflowsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ListRecommendationSetWorkflows', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ListRecommendationSetWorkflows',
                {'order_by': request.order_by}
            )
            response_0 = customers_v1_customer_service_pb2.BatchGetCustomersResponse()
            outgoing_0 = customers_v1_customer_service_pb2.BatchGetCustomersRequest(context=request.context)
            response_0 = await deps.clients.customers_customer.BatchGetCustomers(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.page_info.next_page_token
            if returned_0_0:
                response.page_info.next_page_token = returned_0_0
            return response

    async def handle_resume_recommendation_set_workflow(
        self,
        request: recommendations_v1_recommendation_set_workflow_service_pb2.ResumeRecommendationSetWorkflowRequest
    ) -> recommendations_v1_recommendation_set_workflow_service_pb2.ResumeRecommendationSetWorkflowResponse:
        """Resumes a recommendation set."""
        deps = self.deps
        response = recommendations_v1_recommendation_set_workflow_service_pb2.ResumeRecommendationSetWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ResumeRecommendationSetWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ResumeRecommendationSetWorkflow',
                {'reason': request.reason}
            )
            await deps.repository.save_recommendation_set(request.context.tenant_id, request.recommendation_set)
            response_0 = recommendations_v1_recommendation_model_validation_service_pb2.ExplainRecommendationModelDecisionResponse()
            response_1 = customers_v1_household_calculation_service_pb2.SimulateHouseholdResponse()
            command_0 = RecommendationSetWorkflowResumeRecommendationSetWorkflow0Command.model_validate(
                {'context': request.context, 'details_contact_email': request.recommendation_set.counterparty.email}
            )
            outgoing_0 = to_recommendation_set_workflow_resume_recommendation_set_workflow0_command(command_0)
            response_0 = await deps.clients.recommendations_recommendation_model_validation.ExplainRecommendationModelDecision(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            async for item_1 in async_messages(request.recommendation_set.lines):
                outgoing_1 = customers_v1_household_calculation_service_pb2.SimulateHouseholdRequest(
                    context=request.context,
                    household=customers_v1_customers_pb2.Household(
                        children=[
                            customers_v1_customers_pb2.Household(
                                children=[
                                    customers_v1_customers_pb2.Household(
                                        children=[
                                            customers_v1_customers_pb2.Household(attributes=dict(item_1.attributes))
                                        ],
                                        location=common_v1_address_pb2.PostalAddress(
                                            postal_code=request.recommendation_set.billing_address.postal_code
                                        )
                                    )
                                ]
                            )
                        ]
                    )
                )
                response_1 = await deps.clients.customers_household_calculation.SimulateHousehold(
                    outgoing_1,
                    timeout=deps.settings.timeout
                )
            returned_0_0 = response_0.recommendation_model.audit.updated_at
            if returned_0_0.ListFields():
                response.recommendation_set.audit.updated_at.MergeFrom(returned_0_0)
            returned_0_1 = response_0.recommendation_model.audit.created_at
            if returned_0_1.ListFields():
                response.recommendation_set.audit.created_at.MergeFrom(returned_0_1)
            echoed_0 = request.recommendation_set_id
            response.recommendation_set.recommendation_set_id = echoed_0
            echoed_1 = request.recommendation_set.total
            response.recommendation_set.total.CopyFrom(echoed_1)
            return response

    async def handle_retry_recommendation_set_workflow(
        self,
        request: recommendations_v1_recommendation_set_workflow_service_pb2.RetryRecommendationSetWorkflowRequest
    ) -> recommendations_v1_recommendation_set_workflow_service_pb2.RetryRecommendationSetWorkflowResponse:
        """Retrys a recommendation set."""
        deps = self.deps
        response = recommendations_v1_recommendation_set_workflow_service_pb2.RetryRecommendationSetWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('RetryRecommendationSetWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'RetryRecommendationSetWorkflow',
                {'reason': request.reason}
            )
            await deps.repository.save_recommendation_set(request.context.tenant_id, request.recommendation_set)
            response_0 = recommendations_v1_recommendation_model_validation_service_pb2.CheckRecommendationModelEligibilityResponse()
            response_1 = recommendations_v1_recommendation_set_validation_service_pb2.NormalizeRecommendationSetResponse()
            response_2 = recommendations_v1_recommendation_model_approval_service_pb2.DelegateRecommendationModelApprovalResponse()
            outgoing_0 = recommendations_v1_recommendation_model_validation_service_pb2.CheckRecommendationModelEligibilityRequest(
                context=request.context,
                details=recommendations_v1_recommendation_model_validation_service_pb2.CheckRecommendationModelEligibilityRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(email=request.recommendation_set.counterparty.email)
                ),
                recommendation_model=recommendations_v1_recommendations_pb2.RecommendationModel(
                    address=common_v1_address_pb2.PostalAddress(
                        country_code=request.recommendation_set.billing_address.country_code,
                        lines=list(request.recommendation_set.billing_address.lines)
                    ),
                    owner=identity_v1_refs_pb2.UserRef(
                        display_name=request.recommendation_set.counterparty.display_name
                    )
                )
            )
            response_0 = await hooks.recommendation_set_workflow_retry_recommendation_set_workflow0(
                deps.clients.recommendations_recommendation_model_validation,
                outgoing_0,
                deps.settings.timeout
            )
            outgoing_1 = recommendations_v1_recommendation_set_validation_service_pb2.NormalizeRecommendationSetRequest()
            outgoing_1.context.CopyFrom(request.context)
            outgoing_1.recommendation_set.counterparty.display_name = request.recommendation_set.counterparty.display_name
            outgoing_1.recommendation_set.billing_address.postal_code = request.recommendation_set.billing_address.postal_code
            outgoing_1.recommendation_set.billing_address.country_code = response_0.recommendation_model.address.country_code
            outgoing_1.recommendation_set.card.network = request.recommendation_set.card.network
            outgoing_1.context.tenant_id = tenant_id.get()
            response_1 = await deps.clients.recommendations_recommendation_set_validation.NormalizeRecommendationSet(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = recommendations_v1_recommendation_model_approval_service_pb2.DelegateRecommendationModelApprovalRequest(
                context=request.context,
                recommendation_model=recommendations_v1_recommendations_pb2.RecommendationModel(
                    audit=common_v1_audit_pb2.AuditInfo(updated_by=response_1.recommendation_set.audit.updated_by)
                )
            )
            port_2: RecommendationSetWorkflowRetryRecommendationSetWorkflow2Port = RecommendationSetWorkflowRetryRecommendationSetWorkflow2Adapter(
                deps.clients.recommendations_recommendation_model_approval,
                deps.settings.timeout
            )
            response_2 = await port_2.execute(outgoing_2)
            returned_0_0 = response_0.result.status
            if returned_0_0:
                response.outcome.status = returned_0_0
            returned_1_0 = response_1.result.correlation_id
            if returned_1_0:
                response.result.correlation_id = returned_1_0
            returned_1_1 = response_1.outcome.message
            if returned_1_1:
                response.outcome.message = returned_1_1
            returned_2_0 = response_2.outcome.status
            if returned_2_0:
                response.result.status = returned_2_0
            echoed_0 = request.recommendation_set_id
            response.recommendation_set.recommendation_set_id = echoed_0
            echoed_1 = request.recommendation_set.status
            response.recommendation_set.status = echoed_1
            return response

    async def handle_signal_recommendation_set_workflow(
        self,
        request: recommendations_v1_recommendation_set_workflow_service_pb2.SignalRecommendationSetWorkflowRequest
    ) -> recommendations_v1_recommendation_set_workflow_service_pb2.SignalRecommendationSetWorkflowResponse:
        """Signals a recommendation set."""
        deps = self.deps
        response = recommendations_v1_recommendation_set_workflow_service_pb2.SignalRecommendationSetWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SignalRecommendationSetWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'SignalRecommendationSetWorkflow',
                {'reason': request.reason}
            )
            await deps.repository.save_recommendation_set(request.context.tenant_id, request.recommendation_set)
            response_0 = recommendations_v1_recommendation_model_validation_service_pb2.ValidateRecommendationModelResponse()
            response_1 = customers_v1_household_calculation_service_pb2.RecalculateHouseholdsResponse()
            response_2 = ledger_v1_ledger_account_service_pb2.CloneLedgerAccountResponse()
            response_3 = recommendations_v1_recommendation_set_validation_service_pb2.NormalizeRecommendationSetResponse()
            outgoing_0 = recommendations_v1_recommendation_model_validation_service_pb2.ValidateRecommendationModelRequest(
                context=request.context,
                recommendation_model=recommendations_v1_recommendations_pb2.RecommendationModel(
                    owner=identity_v1_refs_pb2.UserRef(email=request.recommendation_set.counterparty.email)
                )
            )
            steps_0 = [
                partial(
                    deps.clients.recommendations_recommendation_model_validation.ValidateRecommendationModel,
                    outgoing_0,
                    timeout=deps.settings.timeout
                )
            ]
            results_0 = await run_steps(steps_0)
            response_0 = results_0[-1]
            outgoing_1 = customers_v1_household_calculation_service_pb2.RecalculateHouseholdsRequest(
                context=request.context,
                household=customers_v1_customers_pb2.Household(
                    children=[
                        customers_v1_customers_pb2.Household(
                            children=[
                                customers_v1_customers_pb2.Household(
                                    audit=common_v1_audit_pb2.AuditInfo(etag=request.recommendation_set.audit.etag),
                                    location=common_v1_address_pb2.PostalAddress(
                                        region=response_0.recommendation_model.address.region
                                    )
                                )
                            ]
                        )
                    ]
                )
            )
            response_1 = await RecommendationSetWorkflowSignalRecommendationSetWorkflow1Adapter(
                deps.clients.customers_household_calculation,
                deps.settings.timeout
            )(outgoing_1)
            outgoing_2 = ledger_v1_ledger_account_service_pb2.CloneLedgerAccountRequest(
                context=request.context,
                ledger_account=ledger_v1_ledger_pb2.LedgerAccount(
                    audit=common_v1_audit_pb2.AuditInfo(
                        etag=request.recommendation_set.audit.etag,
                        updated_at=response_1.household.audit.updated_at,
                        updated_by=request.recommendation_set.audit.updated_by
                    ),
                    contact=common_v1_contact_pb2.ContactInfo(email=response_1.household.manager.email)
                )
            )
            response_2 = cast(ledger_v1_ledger_account_service_pb2.CloneLedgerAccountResponse, await deps.bus.request(
                'acme.recommendations.v1.RecommendationSetWorkflowService/SignalRecommendationSetWorkflow/2', outgoing_2, deps.settings.timeout,
            ))
            outgoing_3 = recommendations_v1_recommendation_set_validation_service_pb2.NormalizeRecommendationSetRequest(
                context=request.context,
                details=recommendations_v1_recommendation_set_validation_service_pb2.NormalizeRecommendationSetRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(
                        email=request.recommendation_set.counterparty.email,
                        name=response_2.ledger_account.contact.name
                    )
                ),
                recommendation_set=recommendations_v1_recommendations_pb2.RecommendationSet(
                    audit=common_v1_audit_pb2.AuditInfo(created_by=request.recommendation_set.audit.created_by),
                    billing_address=common_v1_address_pb2.PostalAddress(
                        country_code=request.recommendation_set.billing_address.country_code
                    )
                )
            )
            response_3 = await deps.clients.recommendations_recommendation_set_validation.NormalizeRecommendationSet(
                outgoing_3,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.recommendation_model.audit.created_by
            if returned_0_0:
                response.recommendation_set.audit.created_by = returned_0_0
            returned_0_1 = response_0.outcome.status
            if returned_0_1:
                response.outcome.status = returned_0_1
            returned_1_0 = response_1.household.attributes
            returned_1_0_part_1 = response.recommendation_set.lines.add()
            returned_1_0_part_1.attributes.update(returned_1_0)
            returned_1_1 = response_1.household.manager.display_name
            if returned_1_1:
                response.recommendation_set.counterparty.display_name = returned_1_1
            returned_2_0 = response_2.ledger_account.audit.created_by
            if returned_2_0:
                response.recommendation_set.audit.created_by = returned_2_0
            returned_2_1 = response_2.result.status
            if returned_2_1:
                response.outcome.status = returned_2_1
            returned_3_0 = response_3.result.details
            response.result.details.update(returned_3_0)
            echoed_0 = request.recommendation_set_id
            response.recommendation_set.recommendation_set_id = echoed_0
            echoed_1 = request.recommendation_set.billing_address
            response.recommendation_set.billing_address.CopyFrom(echoed_1)
            return response

    async def handle_start_recommendation_set_workflow(
        self,
        request: recommendations_v1_recommendation_set_workflow_service_pb2.StartRecommendationSetWorkflowRequest
    ) -> recommendations_v1_recommendation_set_workflow_service_pb2.StartRecommendationSetWorkflowResponse:
        """Starts a recommendation set."""
        deps = self.deps
        response = recommendations_v1_recommendation_set_workflow_service_pb2.StartRecommendationSetWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('StartRecommendationSetWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'StartRecommendationSetWorkflow',
                {'reason': request.reason}
            )
            await deps.repository.save_recommendation_set(request.context.tenant_id, request.recommendation_set)
            response_0 = customers_v1_customer_calculation_service_pb2.SimulateCustomerResponse()
            response_1 = modelregistry_v1_deployment_workflow_service_pb2.CancelDeploymentWorkflowResponse()
            response_2 = recommendations_v1_recommendation_model_calculation_service_pb2.CalculateRecommendationModelResponse()
            for item_0 in request.recommendation_set.lines:
                outgoing_0 = customers_v1_customer_calculation_service_pb2.SimulateCustomerRequest(
                    context=request.context,
                    customer=customers_v1_customers_pb2.Customer(
                        attributes=dict(item_0.attributes),
                        audit=common_v1_audit_pb2.AuditInfo(created_by=request.recommendation_set.audit.created_by),
                        relationship_manager=identity_v1_refs_pb2.UserRef(
                            email=request.recommendation_set.counterparty.email
                        )
                    )
                )
                response_0 = await deps.clients.customers_customer_calculation.SimulateCustomer(
                    outgoing_0,
                    timeout=deps.settings.timeout
                )
            fields_1: dict[str, Any] = {
                'context': request.context,
                'deployment': {
                    'participants': [
                        {'contact': {'name': request.details.notify.name, 'phone': response_0.customer.contact.phone}}
                    ]
                }
            }
            outgoing_1 = modelregistry_v1_deployment_workflow_service_pb2.CancelDeploymentWorkflowRequest(**fields_1)
            response_1 = await deps.clients.modelregistry_deployment_workflow.CancelDeploymentWorkflow(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = recommendations_v1_recommendation_model_calculation_service_pb2.CalculateRecommendationModelRequest(
                context=request.context,
                details=recommendations_v1_recommendation_model_calculation_service_pb2.CalculateRecommendationModelRequest.Details(
                    destination=common_v1_address_pb2.PostalAddress(
                        country_code=response_0.customer.primary_address.country_code,
                        postal_code=request.recommendation_set.billing_address.postal_code
                    )
                ),
                recommendation_model=recommendations_v1_recommendations_pb2.RecommendationModel(
                    address=common_v1_address_pb2.PostalAddress(
                        postal_code=response_1.deployment.location.postal_code,
                        region=response_0.customer.primary_address.region
                    )
                )
            )
            document_2 = MessageToDict(outgoing_2, preserving_proto_field_name=True)
            outgoing_2 = ParseDict(
                document_2,
                recommendations_v1_recommendation_model_calculation_service_pb2.CalculateRecommendationModelRequest()
            )
            response_2 = await deps.clients.recommendations_recommendation_model_calculation.CalculateRecommendationModel(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            returned_1_0 = response_1.outcome.message
            if returned_1_0:
                response.outcome.message = returned_1_0
            returned_2_0 = response_2.recommendation_model.address.postal_code
            if returned_2_0:
                response.recommendation_set.billing_address.postal_code = returned_2_0
            returned_2_1 = response_2.recommendation_model.components.get(
                'primary',
                recommendations_v1_recommendations_pb2.RecommendationModelComponent()
            ).description
            returned_2_1_part_1 = response.recommendation_set.lines.add()
            if returned_2_1:
                returned_2_1_part_1.description = returned_2_1
            echoed_0 = request.recommendation_set_id
            response.recommendation_set.recommendation_set_id = echoed_0
            echoed_1 = request.recommendation_set.status
            response.recommendation_set.status = echoed_1
            return response
