"""Functional operations behind ScenarioWorkflowService."""

from __future__ import annotations

from collections.abc import Awaitable
from collections.abc import Callable
from typing import cast
import asyncio
import logging

from acme.authorization.v1 import (
    access_policy_validation_service_pb2 as authorization_v1_access_policy_validation_service_pb2,
)
from acme.authorization.v1 import authorization_pb2 as authorization_v1_authorization_pb2
from acme.careplans.v1 import care_plan_query_service_pb2 as careplans_v1_care_plan_query_service_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.forecasting.v1 import (
    demand_forecast_approval_service_pb2 as forecasting_v1_demand_forecast_approval_service_pb2,
)
from acme.forecasting.v1 import (
    forecast_model_approval_service_pb2 as forecasting_v1_forecast_model_approval_service_pb2,
)
from acme.forecasting.v1 import (
    forecast_model_validation_service_pb2 as forecasting_v1_forecast_model_validation_service_pb2,
)
from acme.forecasting.v1 import forecasting_pb2 as forecasting_v1_forecasting_pb2
from acme.forecasting.v1 import refs_pb2 as forecasting_v1_refs_pb2
from acme.forecasting.v1 import scenario_approval_service_pb2 as forecasting_v1_scenario_approval_service_pb2
from acme.forecasting.v1 import scenario_validation_service_pb2 as forecasting_v1_scenario_validation_service_pb2
from acme.forecasting.v1 import scenario_workflow_service_pb2 as forecasting_v1_scenario_workflow_service_pb2
from acme.identity.v1 import identity_pb2 as identity_v1_identity_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.identity.v1 import user_validation_service_pb2 as identity_v1_user_validation_service_pb2
from acme.lineage.v1 import impact_workflow_service_pb2 as lineage_v1_impact_workflow_service_pb2
from acme.lineage.v1 import lineage_pb2 as lineage_v1_lineage_pb2
from acme.metrics.v1 import dashboard_sync_service_pb2 as metrics_v1_dashboard_sync_service_pb2
from acme.metrics.v1 import metrics_pb2 as metrics_v1_metrics_pb2

from acme_data.domains.forecasting import hooks
from acme_data.domains.forecasting.adapters import ScenarioWorkflowResumeScenarioWorkflow1Adapter
from acme_data.domains.forecasting.adapters import ScenarioWorkflowResumeScenarioWorkflow1Port
from acme_data.domains.forecasting.adapters import ScenarioWorkflowRetryScenarioWorkflow1Adapter
from acme_data.domains.forecasting.dependencies import Dependencies
from acme_data.domains.forecasting.models import ScenarioWorkflowAdvanceScenarioWorkflow2Command
from acme_data.domains.forecasting.models import to_scenario_workflow_advance_scenario_workflow2_command
from acme_data.platform.rpc import async_messages
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


async def handle_advance_scenario_workflow(
    deps: Dependencies,
    request: forecasting_v1_scenario_workflow_service_pb2.AdvanceScenarioWorkflowRequest
) -> forecasting_v1_scenario_workflow_service_pb2.AdvanceScenarioWorkflowResponse:
    """Advances a scenario."""
    response = forecasting_v1_scenario_workflow_service_pb2.AdvanceScenarioWorkflowResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('AdvanceScenarioWorkflow', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'AdvanceScenarioWorkflow', {'reason': request.reason})
        await deps.repository.save_scenario(request.context.tenant_id, request.scenario)
        response_0 = forecasting_v1_scenario_validation_service_pb2.GetScenarioRulesResponse()
        response_1 = forecasting_v1_forecast_model_approval_service_pb2.SubmitForecastModelResponse()
        response_2 = forecasting_v1_demand_forecast_approval_service_pb2.ListPendingDemandForecastsResponse()
        outgoing_0 = forecasting_v1_scenario_validation_service_pb2.GetScenarioRulesRequest(
            context=request.context,
            scenario_id=request.scenario.scenario_id
        )
        response_0 = await deps.clients.forecasting_scenario_validation.GetScenarioRules(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        callbacks_1: list[
            Callable[[], Awaitable[forecasting_v1_forecast_model_approval_service_pb2.SubmitForecastModelResponse]]
        ] = []
        for item_1 in request.scenario.comments:
            outgoing_1 = forecasting_v1_forecast_model_approval_service_pb2.SubmitForecastModelRequest(
                context=request.context,
                forecast_model=forecasting_v1_forecasting_pb2.ForecastModel(
                    audit=common_v1_audit_pb2.AuditInfo(
                        created_at=item_1.created_at,
                        updated_by=request.scenario.audit.updated_by
                    ),
                    owner=identity_v1_refs_pb2.UserRef(
                        display_name=request.scenario.customer.display_name,
                        email=item_1.author_email
                    )
                )
            )
            async def send_1(
                payload: forecasting_v1_forecast_model_approval_service_pb2.SubmitForecastModelRequest = outgoing_1
            ) -> forecasting_v1_forecast_model_approval_service_pb2.SubmitForecastModelResponse:
                return await deps.clients.forecasting_forecast_model_approval.SubmitForecastModel(
                    payload,
                    timeout=deps.settings.timeout
                )
            callbacks_1.append(send_1)
        for callback_1 in callbacks_1:
            response_1 = await callback_1()
        command_2 = ScenarioWorkflowAdvanceScenarioWorkflow2Command(
            context=request.context,
            filter_region=response_1.forecast_model.address.region,
            filter_created_after=response_0.scenario.audit.created_at
        )
        outgoing_2 = to_scenario_workflow_advance_scenario_workflow2_command(command_2)
        response_2 = await deps.clients.forecasting_demand_forecast_approval.ListPendingDemandForecasts(
            outgoing_2,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.scenario.audit.created_by
        if returned_0_0:
            response.scenario.audit.created_by = returned_0_0
        returned_0_1 = response_0.scenario.audit.created_at
        if returned_0_1.ListFields():
            response.scenario.audit.created_at.MergeFrom(returned_0_1)
        returned_2_0 = response_2.result.status
        if returned_2_0:
            response.outcome.status = returned_2_0
        echoed_0 = request.scenario_id
        response.scenario.scenario_id = echoed_0
        echoed_1 = request.scenario.custom_fields
        response.scenario.custom_fields.update(echoed_1)
        return response


async def handle_cancel_scenario_workflow(
    deps: Dependencies,
    request: forecasting_v1_scenario_workflow_service_pb2.CancelScenarioWorkflowRequest
) -> forecasting_v1_scenario_workflow_service_pb2.CancelScenarioWorkflowResponse:
    """Cancels a scenario."""
    response = forecasting_v1_scenario_workflow_service_pb2.CancelScenarioWorkflowResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('CancelScenarioWorkflow', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'CancelScenarioWorkflow', {'reason': request.reason})
        await deps.repository.save_scenario(request.context.tenant_id, request.scenario)
        response_0 = lineage_v1_impact_workflow_service_pb2.RetryImpactWorkflowResponse()
        outgoing_0 = lineage_v1_impact_workflow_service_pb2.RetryImpactWorkflowRequest(
            context=request.context,
            details=lineage_v1_impact_workflow_service_pb2.RetryImpactWorkflowRequest.Details(
                notify=common_v1_contact_pb2.ContactInfo(preferred_channel=request.details.notify.preferred_channel)
            ),
            impact=lineage_v1_lineage_pb2.Impact(
                audit=common_v1_audit_pb2.AuditInfo(updated_at=request.scenario.audit.updated_at),
                comments=[lineage_v1_lineage_pb2.ImpactComment(created_at=request.scenario.audit.created_at)]
            )
        )
        response_0 = await deps.clients.lineage_impact_workflow.RetryImpactWorkflow(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.outcome.message
        if returned_0_0:
            response.outcome.message = returned_0_0
        echoed_0 = request.scenario_id
        response.scenario.scenario_id = echoed_0
        echoed_1 = request.scenario.requester
        response.scenario.requester.CopyFrom(echoed_1)
        return response


async def handle_pause_scenario_workflow(
    deps: Dependencies,
    request: forecasting_v1_scenario_workflow_service_pb2.PauseScenarioWorkflowRequest
) -> forecasting_v1_scenario_workflow_service_pb2.PauseScenarioWorkflowResponse:
    """Pauses a scenario."""
    response = forecasting_v1_scenario_workflow_service_pb2.PauseScenarioWorkflowResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('PauseScenarioWorkflow', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'PauseScenarioWorkflow', {'reason': request.reason})
        await deps.repository.save_scenario(request.context.tenant_id, request.scenario)
        response_0 = identity_v1_user_validation_service_pb2.ValidateUserResponse()
        response_1 = careplans_v1_care_plan_query_service_pb2.ResolveCarePlansResponse()
        outgoing_0 = identity_v1_user_validation_service_pb2.ValidateUserRequest(
            context=request.context,
            details=identity_v1_user_validation_service_pb2.ValidateUserRequest.Details(
                contact=common_v1_contact_pb2.ContactInfo(
                    email=request.scenario.assignee.email,
                    preferred_channel=request.details.notify.preferred_channel
                )
            ),
            user=identity_v1_identity_pb2.User(
                contact=common_v1_contact_pb2.ContactInfo(name=request.scenario.requester.name)
            )
        )
        response_0 = await deps.clients.identity_user_validation.ValidateUser(outgoing_0, timeout=deps.settings.timeout)
        outgoing_1 = careplans_v1_care_plan_query_service_pb2.ResolveCarePlansRequest(context=request.context)
        response_1 = await hooks.scenario_workflow_pause_scenario_workflow1(
            deps.clients.careplans_care_plan_query,
            outgoing_1,
            deps.settings.timeout
        )
        returned_0_0 = response_0.result.status
        if returned_0_0:
            response.outcome.status = returned_0_0
        returned_0_1 = response_0.result.message
        if returned_0_1:
            response.outcome.message = returned_0_1
        returned_1_0 = response_1.result.details
        response.result.details.update(returned_1_0)
        echoed_0 = request.scenario_id
        response.scenario.scenario_id = echoed_0
        echoed_1 = request.scenario.subject
        response.scenario.subject = echoed_1
        return response


async def handle_resume_scenario_workflow(
    deps: Dependencies,
    request: forecasting_v1_scenario_workflow_service_pb2.ResumeScenarioWorkflowRequest
) -> forecasting_v1_scenario_workflow_service_pb2.ResumeScenarioWorkflowResponse:
    """Resumes a scenario."""
    response = forecasting_v1_scenario_workflow_service_pb2.ResumeScenarioWorkflowResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('ResumeScenarioWorkflow', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'ResumeScenarioWorkflow', {'reason': request.reason})
        await deps.repository.save_scenario(request.context.tenant_id, request.scenario)
        response_0 = forecasting_v1_forecast_model_approval_service_pb2.EscalateForecastModelResponse()
        response_1 = authorization_v1_access_policy_validation_service_pb2.CheckAccessPolicyEligibilityResponse()
        outgoing_0 = forecasting_v1_forecast_model_approval_service_pb2.EscalateForecastModelRequest(
            context=request.context,
            forecast_model=forecasting_v1_forecasting_pb2.ForecastModel(
                audit=common_v1_audit_pb2.AuditInfo(created_by=request.scenario.audit.created_by)
            )
        )
        response_0 = await deps.clients.forecasting_forecast_model_approval.EscalateForecastModel(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = authorization_v1_access_policy_validation_service_pb2.CheckAccessPolicyEligibilityRequest(
            access_policy=authorization_v1_authorization_pb2.AccessPolicy(
                audit=common_v1_audit_pb2.AuditInfo(etag=response_0.forecast_model.audit.etag)
            ),
            context=request.context,
            details=authorization_v1_access_policy_validation_service_pb2.CheckAccessPolicyEligibilityRequest.Details(
                contact=common_v1_contact_pb2.ContactInfo(
                    email=response_0.forecast_model.owner.email,
                    phone=request.scenario.requester.phone,
                    preferred_channel=request.details.notify.preferred_channel
                )
            )
        )
        port_1: ScenarioWorkflowResumeScenarioWorkflow1Port = ScenarioWorkflowResumeScenarioWorkflow1Adapter(
            deps.clients.authorization_access_policy_validation,
            deps.settings.timeout
        )
        response_1 = await port_1.execute(outgoing_1)
        returned_0_0 = response_0.outcome.message
        if returned_0_0:
            response.outcome.message = returned_0_0
        returned_0_1 = response_0.forecast_model.audit.updated_by
        if returned_0_1:
            response.scenario.audit.updated_by = returned_0_1
        returned_1_0 = response_1.access_policy.audit.created_at
        returned_1_0_part_1 = response.scenario.comments.add()
        if returned_1_0.ListFields():
            returned_1_0_part_1.created_at.MergeFrom(returned_1_0)
        echoed_0 = request.scenario_id
        response.scenario.scenario_id = echoed_0
        echoed_1 = request.scenario.priority
        response.scenario.priority = echoed_1
        return response


async def handle_retry_scenario_workflow(
    deps: Dependencies,
    request: forecasting_v1_scenario_workflow_service_pb2.RetryScenarioWorkflowRequest
) -> forecasting_v1_scenario_workflow_service_pb2.RetryScenarioWorkflowResponse:
    """Retrys a scenario."""
    response = forecasting_v1_scenario_workflow_service_pb2.RetryScenarioWorkflowResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('RetryScenarioWorkflow', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'RetryScenarioWorkflow', {'reason': request.reason})
        await deps.repository.save_scenario(request.context.tenant_id, request.scenario)
        response_0 = metrics_v1_dashboard_sync_service_pb2.ResolveDashboardConflictResponse()
        response_1 = forecasting_v1_forecast_model_validation_service_pb2.CheckForecastModelEligibilityResponse()
        response_2 = forecasting_v1_scenario_approval_service_pb2.CommentScenarioApprovalResponse()
        outgoing_0 = metrics_v1_dashboard_sync_service_pb2.ResolveDashboardConflictRequest(
            context=request.context,
            dashboard=metrics_v1_metrics_pb2.Dashboard(
                audit=common_v1_audit_pb2.AuditInfo(
                    created_at=request.scenario.audit.created_at,
                    etag=request.scenario.audit.etag
                )
            )
        )
        response_0 = await deps.clients.metrics_dashboard_sync.ResolveDashboardConflict(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = forecasting_v1_forecast_model_validation_service_pb2.CheckForecastModelEligibilityRequest(
            context=request.context,
            forecast_model=forecasting_v1_forecasting_pb2.ForecastModel(
                owner=identity_v1_refs_pb2.UserRef(user_id=request.scenario.assignee.user_id)
            )
        )
        response_1 = await ScenarioWorkflowRetryScenarioWorkflow1Adapter(
            deps.clients.forecasting_forecast_model_validation,
            deps.settings.timeout
        )(outgoing_1)
        outgoing_2 = forecasting_v1_scenario_approval_service_pb2.CommentScenarioApprovalRequest(
            context=request.context,
            scenario=forecasting_v1_forecasting_pb2.Scenario(
                customer=forecasting_v1_refs_pb2.ForecastModelRef(display_name=request.scenario.customer.display_name),
                requester=common_v1_contact_pb2.ContactInfo(name=request.details.notify.name),
                sla=forecasting_v1_forecasting_pb2.ScenarioSla(
                    paused_for=request.scenario.sla.paused_for,
                    policy_id=request.scenario.sla.policy_id
                )
            )
        )
        response_2 = cast(forecasting_v1_scenario_approval_service_pb2.CommentScenarioApprovalResponse, await deps.bus.request(
            'acme.forecasting.v1.ScenarioWorkflowService/RetryScenarioWorkflow/2', outgoing_2, deps.settings.timeout,
        ))
        returned_0_0 = response_0.dashboard.audit.created_at
        returned_0_0_part_1 = response.scenario.comments.add()
        if returned_0_0.ListFields():
            returned_0_0_part_1.created_at.MergeFrom(returned_0_0)
        returned_1_0 = response_1.outcome.status
        if returned_1_0:
            response.outcome.status = returned_1_0
        returned_2_0 = response_2.outcome.status
        if returned_2_0:
            response.result.status = returned_2_0
        echoed_0 = request.scenario_id
        response.scenario.scenario_id = echoed_0
        echoed_1 = request.scenario.subject
        response.scenario.subject = echoed_1
        return response


async def handle_signal_scenario_workflow(
    deps: Dependencies,
    request: forecasting_v1_scenario_workflow_service_pb2.SignalScenarioWorkflowRequest
) -> forecasting_v1_scenario_workflow_service_pb2.SignalScenarioWorkflowResponse:
    """Signals a scenario."""
    response = forecasting_v1_scenario_workflow_service_pb2.SignalScenarioWorkflowResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('SignalScenarioWorkflow', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'SignalScenarioWorkflow', {'reason': request.reason})
        await deps.repository.save_scenario(request.context.tenant_id, request.scenario)
        response_0 = forecasting_v1_forecast_model_approval_service_pb2.ListPendingForecastModelsResponse()
        outgoing_0 = forecasting_v1_forecast_model_approval_service_pb2.ListPendingForecastModelsRequest(
            context=request.context,
            filter=forecasting_v1_forecast_model_approval_service_pb2.ListPendingForecastModelsRequest.Filter(
                created_after=request.scenario.audit.updated_at,
                labels=dict(request.annotations),
                owner_id=request.scenario.customer.forecast_model_id
            )
        )
        response_0 = await deps.clients.forecasting_forecast_model_approval.ListPendingForecastModels(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.result.message
        if returned_0_0:
            response.outcome.message = returned_0_0
        returned_0_1 = response_0.result.status
        if returned_0_1:
            response.outcome.status = returned_0_1
        echoed_0 = request.scenario_id
        response.scenario.scenario_id = echoed_0
        echoed_1 = request.scenario.subject
        response.scenario.subject = echoed_1
        return response


async def handle_start_scenario_workflow(
    deps: Dependencies,
    request: forecasting_v1_scenario_workflow_service_pb2.StartScenarioWorkflowRequest
) -> forecasting_v1_scenario_workflow_service_pb2.StartScenarioWorkflowResponse:
    """Starts a scenario."""
    response = forecasting_v1_scenario_workflow_service_pb2.StartScenarioWorkflowResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('StartScenarioWorkflow', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'StartScenarioWorkflow', {'reason': request.reason})
        await deps.repository.save_scenario(request.context.tenant_id, request.scenario)
        response_0 = forecasting_v1_scenario_approval_service_pb2.ListPendingScenariosResponse()
        outgoing_0 = forecasting_v1_scenario_approval_service_pb2.ListPendingScenariosRequest(
            context=request.context,
            filter=forecasting_v1_scenario_approval_service_pb2.ListPendingScenariosRequest.Filter(
                created_after=request.scenario.audit.created_at
            )
        )
        response_0 = await deps.clients.forecasting_scenario_approval.ListPendingScenarios(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.result.correlation_id
        if returned_0_0:
            response.result.correlation_id = returned_0_0
        echoed_0 = request.scenario_id
        response.scenario.scenario_id = echoed_0
        echoed_1 = request.scenario.requester
        response.scenario.requester.CopyFrom(echoed_1)
        return response
