"""Routes scenarios through approval, with escalation and delegation."""

from __future__ import annotations

from collections.abc import AsyncIterator
from collections.abc import Awaitable
from collections.abc import Callable
from dataclasses import dataclass
from functools import partial
from typing import cast
import asyncio
import logging

import grpc

from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.customers.v1 import refs_pb2 as customers_v1_refs_pb2
from acme.featureflags.v1 import feature_flag_service_pb2 as featureflags_v1_feature_flag_service_pb2
from acme.featurestore.v1 import entity_approval_service_pb2 as featurestore_v1_entity_approval_service_pb2
from acme.forecasting.v1 import (
    demand_forecast_approval_service_pb2 as forecasting_v1_demand_forecast_approval_service_pb2,
)
from acme.forecasting.v1 import (
    demand_forecast_approval_service_pb2_grpc as forecasting_v1_demand_forecast_approval_service_pb2_grpc,
)
from acme.forecasting.v1 import demand_forecast_query_service_pb2 as forecasting_v1_demand_forecast_query_service_pb2
from acme.forecasting.v1 import demand_forecast_service_pb2 as forecasting_v1_demand_forecast_service_pb2
from acme.forecasting.v1 import (
    demand_forecast_validation_service_pb2 as forecasting_v1_demand_forecast_validation_service_pb2,
)
from acme.forecasting.v1 import (
    demand_forecast_workflow_service_pb2 as forecasting_v1_demand_forecast_workflow_service_pb2,
)
from acme.forecasting.v1 import (
    forecast_model_approval_service_pb2 as forecasting_v1_forecast_model_approval_service_pb2,
)
from acme.forecasting.v1 import forecast_model_query_service_pb2 as forecasting_v1_forecast_model_query_service_pb2
from acme.forecasting.v1 import forecasting_pb2 as forecasting_v1_forecasting_pb2
from acme.forecasting.v1 import scenario_approval_service_pb2 as forecasting_v1_scenario_approval_service_pb2
from acme.forecasting.v1 import scenario_approval_service_pb2_grpc as forecasting_v1_scenario_approval_service_pb2_grpc
from acme.forecasting.v1 import scenario_calculation_service_pb2 as forecasting_v1_scenario_calculation_service_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.labeling.v1 import annotation_workflow_service_pb2 as labeling_v1_annotation_workflow_service_pb2
from acme.labeling.v1 import labeling_pb2 as labeling_v1_labeling_pb2
from acme.labeling.v1 import refs_pb2 as labeling_v1_refs_pb2
from acme.lineage.v1 import lineage_node_sync_service_pb2 as lineage_v1_lineage_node_sync_service_pb2
from acme.modelregistry.v1 import (
    model_version_lifecycle_service_pb2 as modelregistry_v1_model_version_lifecycle_service_pb2,
)
from acme.modelregistry.v1 import modelregistry_pb2 as modelregistry_v1_modelregistry_pb2
from acme.notifications.v1 import notification_query_service_pb2 as notifications_v1_notification_query_service_pb2
from acme.pipelines.v1 import pipeline_step_import_service_pb2 as pipelines_v1_pipeline_step_import_service_pb2
from acme.pipelines.v1 import pipeline_workflow_service_pb2 as pipelines_v1_pipeline_workflow_service_pb2
from acme.pipelines.v1 import pipelines_pb2 as pipelines_v1_pipelines_pb2

from acme_data.domains.forecasting import hooks
from acme_data.domains.forecasting.adapters import ScenarioApprovalDelegateScenarioApproval1Adapter
from acme_data.domains.forecasting.adapters import ScenarioApprovalDelegateScenarioApproval1Port
from acme_data.domains.forecasting.adapters import ScenarioApprovalDelegateScenarioApproval3Adapter
from acme_data.domains.forecasting.dependencies import Dependencies
from acme_data.domains.forecasting.models import ScenarioApprovalApproveScenario1Command
from acme_data.domains.forecasting.models import ScenarioApprovalCommentScenarioApproval0Command
from acme_data.domains.forecasting.models import to_scenario_approval_approve_scenario1_command
from acme_data.domains.forecasting.models import to_scenario_approval_comment_scenario_approval0_command
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import run_steps
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


@dataclass(slots=True)
class ScenarioApprovalServicer(forecasting_v1_scenario_approval_service_pb2_grpc.ScenarioApprovalServiceServicer):
    deps: Dependencies

    @rpc_errors
    async def ApproveScenario(
        self, request: forecasting_v1_scenario_approval_service_pb2.ApproveScenarioRequest, context: grpc.aio.ServicerContext,
    ) -> forecasting_v1_scenario_approval_service_pb2.ApproveScenarioResponse:
        """Approves a scenario."""
        return await self.handle_approve_scenario(request)

    @rpc_errors
    async def CommentScenarioApproval(
        self, request: forecasting_v1_scenario_approval_service_pb2.CommentScenarioApprovalRequest, context: grpc.aio.ServicerContext,
    ) -> forecasting_v1_scenario_approval_service_pb2.CommentScenarioApprovalResponse:
        """Comments a scenario."""
        return await self.handle_comment_scenario_approval(request)

    @rpc_errors
    async def DelegateScenarioApproval(
        self, request: forecasting_v1_scenario_approval_service_pb2.DelegateScenarioApprovalRequest, context: grpc.aio.ServicerContext,
    ) -> forecasting_v1_scenario_approval_service_pb2.DelegateScenarioApprovalResponse:
        """Delegates a scenario."""
        return await self.handle_delegate_scenario_approval(request)

    @rpc_errors
    async def EscalateScenario(
        self, request: forecasting_v1_scenario_approval_service_pb2.EscalateScenarioRequest, context: grpc.aio.ServicerContext,
    ) -> forecasting_v1_scenario_approval_service_pb2.EscalateScenarioResponse:
        """Escalates a scenario."""
        return await self.handle_escalate_scenario(request)

    @rpc_errors
    @retry_transient
    async def GetScenarioApprovalStatus(
        self, request: forecasting_v1_scenario_approval_service_pb2.GetScenarioApprovalStatusRequest, context: grpc.aio.ServicerContext,
    ) -> forecasting_v1_scenario_approval_service_pb2.GetScenarioApprovalStatusResponse:
        """Returns a scenario."""
        return await self.handle_get_scenario_approval_status(request)

    @rpc_errors
    @retry_transient
    async def ListPendingScenarios(
        self, request: forecasting_v1_scenario_approval_service_pb2.ListPendingScenariosRequest, context: grpc.aio.ServicerContext,
    ) -> forecasting_v1_scenario_approval_service_pb2.ListPendingScenariosResponse:
        """Lists scenarios a page at a time."""
        return await self.handle_list_pending_scenarios(request)

    @rpc_errors
    async def RecallScenario(
        self, request: forecasting_v1_scenario_approval_service_pb2.RecallScenarioRequest, context: grpc.aio.ServicerContext,
    ) -> forecasting_v1_scenario_approval_service_pb2.RecallScenarioResponse:
        """Recalls a scenario."""
        return await self.handle_recall_scenario(request)

    @rpc_errors
    async def SubmitScenario(
        self, request: forecasting_v1_scenario_approval_service_pb2.SubmitScenarioRequest, context: grpc.aio.ServicerContext,
    ) -> forecasting_v1_scenario_approval_service_pb2.SubmitScenarioResponse:
        """Submits a scenario."""
        return await self.handle_submit_scenario(request)

    async def handle_approve_scenario(
        self,
        request: forecasting_v1_scenario_approval_service_pb2.ApproveScenarioRequest
    ) -> forecasting_v1_scenario_approval_service_pb2.ApproveScenarioResponse:
        """Approves a scenario."""
        deps = self.deps
        response = forecasting_v1_scenario_approval_service_pb2.ApproveScenarioResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ApproveScenario', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'ApproveScenario', {'reason': request.reason})
            await deps.repository.save_scenario(request.context.tenant_id, request.scenario)
            response_0 = forecasting_v1_demand_forecast_validation_service_pb2.LintDemandForecastsResponse()
            response_1 = forecasting_v1_demand_forecast_service_pb2.ListDemandForecastsResponse()
            async for item_0 in async_messages(request.scenario.comments):
                outgoing_0 = forecasting_v1_demand_forecast_validation_service_pb2.LintDemandForecastsRequest(
                    context=request.context,
                    demand_forecast=forecasting_v1_forecasting_pb2.DemandForecast(
                        audit=common_v1_audit_pb2.AuditInfo(created_at=item_0.created_at)
                    ),
                    details=forecasting_v1_demand_forecast_validation_service_pb2.LintDemandForecastsRequest.Details(
                        contact=common_v1_contact_pb2.ContactInfo(email=item_0.author_email)
                    )
                )
                response_0 = await deps.clients.forecasting_demand_forecast_validation.LintDemandForecasts(
                    outgoing_0,
                    timeout=deps.settings.timeout
                )
            command_1 = ScenarioApprovalApproveScenario1Command(
                context=request.context,
                filter_region=response_0.demand_forecast.billing_address.region,
                filter_created_after=request.scenario.audit.updated_at,
                filter_owner_id=request.scenario.customer.forecast_model_id
            )
            outgoing_1 = to_scenario_approval_approve_scenario1_command(command_1)
            response_1 = await deps.clients.forecasting_demand_forecast.ListDemandForecasts(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_1_0 = response_1.result.message
            if returned_1_0:
                response.result.message = returned_1_0
            returned_1_1 = response_1.result.reference_ids
            response.result.reference_ids.extend(returned_1_1)
            echoed_0 = request.scenario_id
            response.scenario.scenario_id = echoed_0
            echoed_1 = request.scenario.requester
            response.scenario.requester.CopyFrom(echoed_1)
            return response

    async def handle_comment_scenario_approval(
        self,
        request: forecasting_v1_scenario_approval_service_pb2.CommentScenarioApprovalRequest
    ) -> forecasting_v1_scenario_approval_service_pb2.CommentScenarioApprovalResponse:
        """Comments a scenario."""
        deps = self.deps
        response = forecasting_v1_scenario_approval_service_pb2.CommentScenarioApprovalResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CommentScenarioApproval', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'CommentScenarioApproval',
                {'reason': request.reason}
            )
            await deps.repository.save_scenario(request.context.tenant_id, request.scenario)
            response_0 = forecasting_v1_demand_forecast_approval_service_pb2.ApproveDemandForecastResponse()
            response_1 = forecasting_v1_demand_forecast_query_service_pb2.ExportDemandForecastsResponse()
            response_2 = labeling_v1_annotation_workflow_service_pb2.SignalAnnotationWorkflowResponse()
            command_0 = ScenarioApprovalCommentScenarioApproval0Command.model_validate(
                {
                    'context': request.context,
                    'details_approver_email': request.scenario.requester.email,
                    'demand_forecast_audit_created_by': request.scenario.audit.created_by,
                    'details_approver_display_name': request.scenario.assignee.display_name
                }
            )
            outgoing_0 = to_scenario_approval_comment_scenario_approval0_command(command_0)
            response_0 = await deps.clients.forecasting_demand_forecast_approval.ApproveDemandForecast(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = forecasting_v1_demand_forecast_query_service_pb2.ExportDemandForecastsRequest(
                context=request.context,
                filter=forecasting_v1_demand_forecast_query_service_pb2.ExportDemandForecastsRequest.Filter(
                    created_after=response_0.demand_forecast.audit.created_at,
                    region=response_0.demand_forecast.billing_address.region
                )
            )
            async for chunk_1 in deps.clients.forecasting_demand_forecast_query.ExportDemandForecasts(
                outgoing_1,
                timeout=deps.settings.timeout
            ):
                response_1 = chunk_1
            outgoing_2 = labeling_v1_annotation_workflow_service_pb2.SignalAnnotationWorkflowRequest(
                annotation=labeling_v1_labeling_pb2.Annotation(
                    subject=labeling_v1_refs_pb2.LabelingTaskRef(
                        display_name=request.scenario.customer.display_name,
                        priority=response_0.demand_forecast.counterparty.priority
                    )
                ),
                context=request.context,
                details=labeling_v1_annotation_workflow_service_pb2.SignalAnnotationWorkflowRequest.Details(
                    notify=common_v1_contact_pb2.ContactInfo(name=request.scenario.requester.name)
                )
            )
            response_2 = await hooks.scenario_approval_comment_scenario_approval2(
                deps.clients.labeling_annotation_workflow,
                outgoing_2,
                deps.settings.timeout
            )
            returned_0_0 = response_0.outcome.message
            if returned_0_0:
                response.outcome.message = returned_0_0
            returned_2_0 = response_2.result.message
            if returned_2_0:
                response.outcome.message = returned_2_0
            returned_2_1 = response_2.result.status
            if returned_2_1:
                response.outcome.status = returned_2_1
            echoed_0 = request.scenario_id
            response.scenario.scenario_id = echoed_0
            echoed_1 = request.scenario.priority
            response.scenario.priority = echoed_1
            return response

    async def handle_delegate_scenario_approval(
        self,
        request: forecasting_v1_scenario_approval_service_pb2.DelegateScenarioApprovalRequest
    ) -> forecasting_v1_scenario_approval_service_pb2.DelegateScenarioApprovalResponse:
        """Delegates a scenario."""
        deps = self.deps
        response = forecasting_v1_scenario_approval_service_pb2.DelegateScenarioApprovalResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('DelegateScenarioApproval', extra={'fields': {'approver_email': request.details.approver_email}})
            await deps.repository.audit(
                request.context.tenant_id,
                'DelegateScenarioApproval',
                {'approver_email': request.details.approver_email}
            )
            await deps.repository.save_scenario(request.context.tenant_id, request.scenario)
            response_0 = forecasting_v1_forecast_model_query_service_pb2.SummarizeForecastModelsResponse()
            response_1 = featureflags_v1_feature_flag_service_pb2.ListFeatureFlagsResponse()
            response_2 = pipelines_v1_pipeline_workflow_service_pb2.CancelPipelineWorkflowResponse()
            response_3 = featurestore_v1_entity_approval_service_pb2.ListPendingEntitiesResponse()
            outgoing_0 = forecasting_v1_forecast_model_query_service_pb2.SummarizeForecastModelsRequest()
            outgoing_0.context.CopyFrom(request.context)
            if request.scenario.WhichOneof('origin') == 'customer':
                outgoing_0.forecast_model_id = request.scenario.customer.forecast_model_id
            outgoing_0.reason = request.reason
            outgoing_0.annotations.update(dict(request.annotations))
            response_0 = await deps.clients.forecasting_forecast_model_query.SummarizeForecastModels(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = featureflags_v1_feature_flag_service_pb2.ListFeatureFlagsRequest(
                context=request.context,
                filter=featureflags_v1_feature_flag_service_pb2.ListFeatureFlagsRequest.Filter(
                    created_after=request.details.effective_at
                )
            )
            port_1: ScenarioApprovalDelegateScenarioApproval1Port = ScenarioApprovalDelegateScenarioApproval1Adapter(
                deps.clients.featureflags_feature_flag,
                deps.settings.timeout
            )
            response_1 = await port_1.execute(outgoing_1)
            outgoing_2 = pipelines_v1_pipeline_workflow_service_pb2.CancelPipelineWorkflowRequest(
                context=request.context,
                pipeline=pipelines_v1_pipelines_pb2.Pipeline(
                    participants=[
                        pipelines_v1_pipelines_pb2.PipelineParticipant(
                            contact=common_v1_contact_pb2.ContactInfo(
                                preferred_channel=request.scenario.requester.preferred_channel
                            )
                        )
                    ]
                )
            )
            steps_2 = [
                partial(
                    deps.clients.pipelines_pipeline_workflow.CancelPipelineWorkflow,
                    outgoing_2,
                    timeout=deps.settings.timeout
                )
            ]
            results_2 = await run_steps(steps_2)
            response_2 = results_2[-1]
            outgoing_3 = featurestore_v1_entity_approval_service_pb2.ListPendingEntitiesRequest(
                context=request.context,
                filter=featurestore_v1_entity_approval_service_pb2.ListPendingEntitiesRequest.Filter(
                    created_after=request.scenario.audit.created_at,
                    region=response_2.pipeline.location.region
                )
            )
            response_3 = await ScenarioApprovalDelegateScenarioApproval3Adapter(
                deps.clients.featurestore_entity_approval,
                deps.settings.timeout
            )(outgoing_3)
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.result.message = returned_0_0
            returned_1_0 = response_1.result.status
            if returned_1_0:
                response.outcome.status = returned_1_0
            returned_1_1 = response_1.result.details
            response.result.details.update(returned_1_1)
            returned_2_0 = response_2.outcome.status
            if returned_2_0:
                response.outcome.status = returned_2_0
            returned_2_1 = response_2.pipeline.audit.updated_by
            if returned_2_1:
                response.scenario.audit.updated_by = returned_2_1
            returned_3_0 = response_3.result.message
            if returned_3_0:
                response.outcome.message = returned_3_0
            returned_3_1 = response_3.result.status
            if returned_3_1:
                response.result.status = returned_3_1
            echoed_0 = request.scenario_id
            response.scenario.scenario_id = echoed_0
            echoed_1 = request.scenario.assignee
            response.scenario.assignee.CopyFrom(echoed_1)
            return response

    async def handle_escalate_scenario(
        self,
        request: forecasting_v1_scenario_approval_service_pb2.EscalateScenarioRequest
    ) -> forecasting_v1_scenario_approval_service_pb2.EscalateScenarioResponse:
        """Escalates a scenario."""
        deps = self.deps
        response = forecasting_v1_scenario_approval_service_pb2.EscalateScenarioResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('EscalateScenario', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'EscalateScenario', {'reason': request.reason})
            await deps.repository.save_scenario(request.context.tenant_id, request.scenario)
            response_0 = modelregistry_v1_model_version_lifecycle_service_pb2.ScheduleModelVersionExpiryResponse()
            response_1 = forecasting_v1_forecast_model_approval_service_pb2.SubmitForecastModelResponse()
            outgoing_0 = modelregistry_v1_model_version_lifecycle_service_pb2.ScheduleModelVersionExpiryRequest(
                context=request.context,
                details=modelregistry_v1_model_version_lifecycle_service_pb2.ScheduleModelVersionExpiryRequest.Details(
                    notify=common_v1_contact_pb2.ContactInfo(
                        email=request.scenario.assignee.email,
                        phone=request.scenario.requester.phone
                    )
                ),
                model_version=modelregistry_v1_modelregistry_pb2.ModelVersion(
                    subject=customers_v1_refs_pb2.CustomerRef(
                        display_name=request.scenario.customer.display_name,
                        email=request.details.approver.email
                    )
                )
            )
            response_0 = cast(modelregistry_v1_model_version_lifecycle_service_pb2.ScheduleModelVersionExpiryResponse, await deps.bus.request(
                'acme.forecasting.v1.ScenarioApprovalService/EscalateScenario/0', outgoing_0, deps.settings.timeout,
            ))
            outgoing_1 = forecasting_v1_forecast_model_approval_service_pb2.SubmitForecastModelRequest(
                context=request.context,
                forecast_model=forecasting_v1_forecasting_pb2.ForecastModel(
                    owner=identity_v1_refs_pb2.UserRef(email=response_0.model_version.subject.email)
                )
            )
            response_1 = await deps.clients.forecasting_forecast_model_approval.SubmitForecastModel(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.outcome.reference_id
            if returned_0_0:
                response.outcome.reference_id = returned_0_0
            returned_0_1 = response_0.model_version.subject.display_name
            if returned_0_1:
                response.scenario.assignee.display_name = returned_0_1
            returned_1_0 = response_1.forecast_model.tags
            response.scenario.tags.extend(returned_1_0)
            echoed_0 = request.scenario_id
            response.scenario.scenario_id = echoed_0
            echoed_1 = request.scenario.subject
            response.scenario.subject = echoed_1
            return response

    async def handle_get_scenario_approval_status(
        self,
        request: forecasting_v1_scenario_approval_service_pb2.GetScenarioApprovalStatusRequest
    ) -> forecasting_v1_scenario_approval_service_pb2.GetScenarioApprovalStatusResponse:
        """Returns a scenario."""
        deps = self.deps
        response = forecasting_v1_scenario_approval_service_pb2.GetScenarioApprovalStatusResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('GetScenarioApprovalStatus', extra={'fields': {'domain': 'forecasting'}})
            await deps.repository.audit(request.context.tenant_id, 'GetScenarioApprovalStatus', {})
            response_0 = forecasting_v1_forecast_model_approval_service_pb2.ListPendingForecastModelsResponse()
            outgoing_0 = forecasting_v1_forecast_model_approval_service_pb2.ListPendingForecastModelsRequest(
                context=request.context,
                filter=forecasting_v1_forecast_model_approval_service_pb2.ListPendingForecastModelsRequest.Filter(
                    created_after=request.context.deadline,
                    labels=dict(request.context.baggage),
                    owner_id=request.scenario_id
                )
            )
            response_0 = await deps.clients.forecasting_forecast_model_approval.ListPendingForecastModels(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.status
            if returned_0_0:
                response.result.status = returned_0_0
            echoed_0 = request.scenario_id
            response.scenario.scenario_id = echoed_0
            return response

    async def handle_list_pending_scenarios(
        self,
        request: forecasting_v1_scenario_approval_service_pb2.ListPendingScenariosRequest
    ) -> forecasting_v1_scenario_approval_service_pb2.ListPendingScenariosResponse:
        """Lists scenarios a page at a time."""
        deps = self.deps
        response = forecasting_v1_scenario_approval_service_pb2.ListPendingScenariosResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ListPendingScenarios', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ListPendingScenarios',
                {'order_by': request.order_by}
            )
            response_0 = lineage_v1_lineage_node_sync_service_pb2.ListLineageNodeConflictsResponse()
            outgoing_0 = lineage_v1_lineage_node_sync_service_pb2.ListLineageNodeConflictsRequest(
                context=request.context,
                filter=lineage_v1_lineage_node_sync_service_pb2.ListLineageNodeConflictsRequest.Filter(
                    region=request.filter.region
                )
            )
            response_0 = await deps.clients.lineage_lineage_node_sync.ListLineageNodeConflicts(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.page_info.next_page_token
            if returned_0_0:
                response.page_info.next_page_token = returned_0_0
            return response

    async def handle_recall_scenario(
        self,
        request: forecasting_v1_scenario_approval_service_pb2.RecallScenarioRequest
    ) -> forecasting_v1_scenario_approval_service_pb2.RecallScenarioResponse:
        """Recalls a scenario."""
        deps = self.deps
        response = forecasting_v1_scenario_approval_service_pb2.RecallScenarioResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('RecallScenario', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'RecallScenario', {'reason': request.reason})
            await deps.repository.save_scenario(request.context.tenant_id, request.scenario)
            response_0 = notifications_v1_notification_query_service_pb2.FindNotificationsResponse()
            response_1 = forecasting_v1_scenario_calculation_service_pb2.CompareScenarioOptionsResponse()
            response_2 = pipelines_v1_pipeline_step_import_service_pb2.MapPipelineStepImportColumnsResponse()
            outgoing_0 = notifications_v1_notification_query_service_pb2.FindNotificationsRequest(
                context=request.context,
                filter=notifications_v1_notification_query_service_pb2.FindNotificationsRequest.Filter(
                    created_after=request.scenario.sla.due_at
                )
            )
            outgoing_1 = forecasting_v1_scenario_calculation_service_pb2.CompareScenarioOptionsRequest(
                context=request.context,
                scenario=forecasting_v1_forecasting_pb2.Scenario(
                    audit=common_v1_audit_pb2.AuditInfo(etag=request.scenario.audit.etag),
                    requester=common_v1_contact_pb2.ContactInfo(
                        email=request.scenario.requester.email,
                        phone=request.scenario.requester.phone
                    )
                )
            )
            response_0, response_1 = await asyncio.gather(
                deps.clients.notifications_notification_query.FindNotifications(
                    outgoing_0,
                    timeout=deps.settings.timeout
                ),
                deps.clients.forecasting_scenario_calculation.CompareScenarioOptions(
                    outgoing_1,
                    timeout=deps.settings.timeout
                ),
            )
            outgoing_2 = pipelines_v1_pipeline_step_import_service_pb2.MapPipelineStepImportColumnsRequest()
            outgoing_2.context.CopyFrom(request.context)
            outgoing_2.details.contact.name.CopyFrom(response_1.scenario.requester.name)
            outgoing_2.pipeline_step.audit.created_by = response_1.scenario.audit.created_by
            outgoing_2.pipeline_step.owner.user_id = request.details.approver.user_id
            merged_2 = pipelines_v1_pipeline_step_import_service_pb2.MapPipelineStepImportColumnsRequest()
            merged_2.MergeFrom(outgoing_2)
            outgoing_2.CopyFrom(merged_2)
            response_2 = await deps.clients.pipelines_pipeline_step_import.MapPipelineStepImportColumns(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.status
            if returned_0_0:
                response.result.status = returned_0_0
            returned_0_1 = response_0.result.status
            if returned_0_1:
                response.outcome.status = returned_0_1
            returned_1_0 = response_1.result.details
            response.result.details.update(returned_1_0)
            returned_1_1 = response_1.scenario.assignee.user_id
            if returned_1_1:
                response.scenario.assignee.user_id = returned_1_1
            returned_2_0 = response_2.result.details
            response.result.details.update(returned_2_0)
            echoed_0 = request.scenario_id
            response.scenario.scenario_id = echoed_0
            echoed_1 = request.scenario.priority
            response.scenario.priority = echoed_1
            return response

    async def handle_submit_scenario(
        self,
        request: forecasting_v1_scenario_approval_service_pb2.SubmitScenarioRequest
    ) -> forecasting_v1_scenario_approval_service_pb2.SubmitScenarioResponse:
        """Submits a scenario."""
        deps = self.deps
        response = forecasting_v1_scenario_approval_service_pb2.SubmitScenarioResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SubmitScenario', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'SubmitScenario', {'reason': request.reason})
            await deps.repository.save_scenario(request.context.tenant_id, request.scenario)
            response_0 = forecasting_v1_demand_forecast_workflow_service_pb2.ResumeDemandForecastWorkflowResponse()
            response_1 = forecasting_v1_demand_forecast_approval_service_pb2.ApproveDemandForecastResponse()
            for item_0 in request.scenario.comments:
                outgoing_0 = forecasting_v1_demand_forecast_workflow_service_pb2.ResumeDemandForecastWorkflowRequest(
                    context=request.context,
                    demand_forecast=forecasting_v1_forecasting_pb2.DemandForecast(
                        audit=common_v1_audit_pb2.AuditInfo(created_at=item_0.created_at)
                    ),
                    details=forecasting_v1_demand_forecast_workflow_service_pb2.ResumeDemandForecastWorkflowRequest.Details(
                        notify=common_v1_contact_pb2.ContactInfo(email=item_0.author_email)
                    )
                )
                response_0 = await deps.clients.forecasting_demand_forecast_workflow.ResumeDemandForecastWorkflow(
                    outgoing_0,
                    timeout=deps.settings.timeout
                )
            outgoing_1 = forecasting_v1_demand_forecast_approval_service_pb2.ApproveDemandForecastRequest(
                context=request.context,
                demand_forecast=forecasting_v1_forecasting_pb2.DemandForecast(
                    billing_address=common_v1_address_pb2.PostalAddress(
                        country_code=response_0.demand_forecast.billing_address.country_code
                    )
                )
            )
            registered_1 = cast(
                forecasting_v1_demand_forecast_approval_service_pb2_grpc.DemandForecastApprovalServiceStub,
                deps.clients.registry['acme.forecasting.v1.DemandForecastApprovalService']
            )
            response_1 = await registered_1.ApproveDemandForecast(outgoing_1, timeout=deps.settings.timeout)
            returned_1_0 = response_1.demand_forecast.audit.created_at
            returned_1_0_part_1 = response.scenario.comments.add()
            if returned_1_0.ListFields():
                returned_1_0_part_1.created_at.MergeFrom(returned_1_0)
            echoed_0 = request.scenario_id
            response.scenario.scenario_id = echoed_0
            echoed_1 = request.scenario.status
            response.scenario.status = echoed_1
            return response
