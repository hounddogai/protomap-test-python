"""Functional operations behind ImpactWorkflowService."""

from __future__ import annotations

from collections.abc import Awaitable
from collections.abc import Callable
from typing import cast
import asyncio
import logging

from acme.anomalies.v1 import detector_query_service_pb2 as anomalies_v1_detector_query_service_pb2
from acme.audit.v1 import audit_event_query_service_pb2 as audit_v1_audit_event_query_service_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.customers.v1 import (
    consent_record_validation_service_pb2 as customers_v1_consent_record_validation_service_pb2,
)
from acme.customers.v1 import customer_service_pb2 as customers_v1_customer_service_pb2
from acme.customers.v1 import customer_service_pb2_grpc as customers_v1_customer_service_pb2_grpc
from acme.forecasting.v1 import (
    demand_forecast_validation_service_pb2 as forecasting_v1_demand_forecast_validation_service_pb2,
)
from acme.forecasting.v1 import forecasting_pb2 as forecasting_v1_forecasting_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.lineage.v1 import impact_lifecycle_service_pb2 as lineage_v1_impact_lifecycle_service_pb2
from acme.lineage.v1 import impact_sync_service_pb2 as lineage_v1_impact_sync_service_pb2
from acme.lineage.v1 import impact_workflow_service_pb2 as lineage_v1_impact_workflow_service_pb2
from acme.lineage.v1 import lineage_edge_calculation_service_pb2 as lineage_v1_lineage_edge_calculation_service_pb2
from acme.lineage.v1 import lineage_edge_reporting_service_pb2 as lineage_v1_lineage_edge_reporting_service_pb2
from acme.lineage.v1 import lineage_edge_workflow_service_pb2 as lineage_v1_lineage_edge_workflow_service_pb2
from acme.lineage.v1 import lineage_node_workflow_service_pb2 as lineage_v1_lineage_node_workflow_service_pb2
from acme.lineage.v1 import lineage_pb2 as lineage_v1_lineage_pb2
from acme.lineage.v1 import refs_pb2 as lineage_v1_refs_pb2
from acme.pipelines.v1 import pipeline_run_calculation_service_pb2 as pipelines_v1_pipeline_run_calculation_service_pb2
from acme.pipelines.v1 import pipelines_pb2 as pipelines_v1_pipelines_pb2

from acme_data.domains.lineage import hooks
from acme_data.domains.lineage.adapters import ImpactWorkflowSignalImpactWorkflow2Adapter
from acme_data.domains.lineage.dependencies import Dependencies
from acme_data.domains.lineage.models import ImpactWorkflowInspectImpactWorkflow1Command
from acme_data.domains.lineage.models import to_impact_workflow_inspect_impact_workflow1_command
from acme_data.platform.rpc import async_messages
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


async def handle_advance_impact_workflow(
    deps: Dependencies,
    request: lineage_v1_impact_workflow_service_pb2.AdvanceImpactWorkflowRequest
) -> lineage_v1_impact_workflow_service_pb2.AdvanceImpactWorkflowResponse:
    """Advances an impact."""
    response = lineage_v1_impact_workflow_service_pb2.AdvanceImpactWorkflowResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('AdvanceImpactWorkflow', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'AdvanceImpactWorkflow', {'reason': request.reason})
        await deps.repository.save_impact(request.context.tenant_id, request.impact)
        response_0 = customers_v1_consent_record_validation_service_pb2.ExplainConsentRecordDecisionResponse()
        response_1 = pipelines_v1_pipeline_run_calculation_service_pb2.RecalculatePipelineRunsResponse()
        outgoing_0 = customers_v1_consent_record_validation_service_pb2.ExplainConsentRecordDecisionRequest(
            context=request.context,
            details=customers_v1_consent_record_validation_service_pb2.ExplainConsentRecordDecisionRequest.Details(
                contact=common_v1_contact_pb2.ContactInfo(name=request.details.notify.name)
            )
        )
        response_0 = await deps.clients.customers_consent_record_validation.ExplainConsentRecordDecision(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        for item_1 in request.impact.history:
            outgoing_1 = pipelines_v1_pipeline_run_calculation_service_pb2.RecalculatePipelineRunsRequest(
                context=request.context,
                pipeline_run=pipelines_v1_pipelines_pb2.PipelineRun(
                    history=[
                        pipelines_v1_pipelines_pb2.PipelineRunStatusChange(
                            changed_at=item_1.changed_at,
                            changed_by=item_1.changed_by,
                            from_status=item_1.from_status,
                            to_status=item_1.to_status
                        )
                    ]
                )
            )
            response_1 = await deps.clients.pipelines_pipeline_run_calculation.RecalculatePipelineRuns(
                outgoing_1,
                timeout=deps.settings.timeout
            )
        returned_0_0 = response_0.outcome.message
        if returned_0_0:
            response.outcome.message = returned_0_0
        echoed_0 = request.impact_id
        response.impact.impact_id = echoed_0
        echoed_1 = request.impact.custom_fields
        response.impact.custom_fields.update(echoed_1)
        return response


async def handle_cancel_impact_workflow(
    deps: Dependencies,
    request: lineage_v1_impact_workflow_service_pb2.CancelImpactWorkflowRequest
) -> lineage_v1_impact_workflow_service_pb2.CancelImpactWorkflowResponse:
    """Cancels an impact."""
    response = lineage_v1_impact_workflow_service_pb2.CancelImpactWorkflowResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('CancelImpactWorkflow', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'CancelImpactWorkflow', {'reason': request.reason})
        await deps.repository.save_impact(request.context.tenant_id, request.impact)
        response_0 = lineage_v1_impact_lifecycle_service_pb2.RenewImpactResponse()
        response_1 = lineage_v1_lineage_node_workflow_service_pb2.AdvanceLineageNodeWorkflowResponse()
        response_2 = lineage_v1_impact_sync_service_pb2.PullImpactsResponse()
        response_3 = customers_v1_customer_service_pb2.BatchGetCustomersResponse()
        requests_0: list[lineage_v1_impact_lifecycle_service_pb2.RenewImpactRequest] = []
        for item_0 in request.impact.comments:
            outgoing_0 = lineage_v1_impact_lifecycle_service_pb2.RenewImpactRequest(
                context=request.context,
                details=lineage_v1_impact_lifecycle_service_pb2.RenewImpactRequest.Details(
                    new_owner=identity_v1_refs_pb2.UserRef(email=item_0.author_email),
                    notify_contact=common_v1_contact_pb2.ContactInfo(
                        phone=request.details.notify.phone,
                        preferred_channel=request.details.notify.preferred_channel
                    )
                ),
                impact_id=request.impact.impact_id
            )
            requests_0.append(outgoing_0)
        replies_0 = await asyncio.gather(*(
            deps.clients.lineage_impact_lifecycle.RenewImpact(
                entry,
                timeout=deps.settings.timeout
            ) for entry in requests_0
        ))
        if replies_0:
            response_0 = replies_0[-1]
        callbacks_1: list[
            Callable[[], Awaitable[lineage_v1_lineage_node_workflow_service_pb2.AdvanceLineageNodeWorkflowResponse]]
        ] = []
        for item_1 in request.impact.comments:
            outgoing_1 = lineage_v1_lineage_node_workflow_service_pb2.AdvanceLineageNodeWorkflowRequest(
                context=request.context,
                details=lineage_v1_lineage_node_workflow_service_pb2.AdvanceLineageNodeWorkflowRequest.Details(
                    notify=common_v1_contact_pb2.ContactInfo(email=item_1.author_email)
                ),
                lineage_node=lineage_v1_lineage_pb2.LineageNode(
                    children=[
                        lineage_v1_lineage_pb2.LineageNode(
                            audit=common_v1_audit_pb2.AuditInfo(created_at=item_1.created_at),
                            children=[
                                lineage_v1_lineage_pb2.LineageNode(
                                    manager=identity_v1_refs_pb2.UserRef(
                                        display_name=response_0.impact.assignee.display_name
                                    )
                                )
                            ]
                        )
                    ]
                )
            )
            async def send_1(
                payload: lineage_v1_lineage_node_workflow_service_pb2.AdvanceLineageNodeWorkflowRequest = outgoing_1
            ) -> lineage_v1_lineage_node_workflow_service_pb2.AdvanceLineageNodeWorkflowResponse:
                return await deps.clients.lineage_lineage_node_workflow.AdvanceLineageNodeWorkflow(
                    payload,
                    timeout=deps.settings.timeout
                )
            callbacks_1.append(send_1)
        for callback_1 in callbacks_1:
            response_1 = await callback_1()
        async for item_2 in async_messages(request.impact.comments):
            outgoing_2 = lineage_v1_impact_sync_service_pb2.PullImpactsRequest(
                context=request.context,
                impact=lineage_v1_lineage_pb2.Impact(
                    comments=[
                        lineage_v1_lineage_pb2.ImpactComment(
                            author_email=item_2.author_email,
                            created_at=item_2.created_at,
                            visibility=item_2.visibility
                        )
                    ]
                )
            )
            response_2 = await deps.clients.lineage_impact_sync.PullImpacts(outgoing_2, timeout=deps.settings.timeout)
        outgoing_3 = customers_v1_customer_service_pb2.BatchGetCustomersRequest(context=request.context)
        registered_3 = cast(
            customers_v1_customer_service_pb2_grpc.CustomerServiceStub,
            deps.clients.registry['acme.customers.v1.CustomerService']
        )
        response_3 = await registered_3.BatchGetCustomers(outgoing_3, timeout=deps.settings.timeout)
        returned_3_0 = response_3.result.details
        response.result.details.update(returned_3_0)
        echoed_0 = request.impact_id
        response.impact.impact_id = echoed_0
        echoed_1 = request.impact.priority
        response.impact.priority = echoed_1
        return response


async def handle_inspect_impact_workflow(
    deps: Dependencies,
    request: lineage_v1_impact_workflow_service_pb2.InspectImpactWorkflowRequest
) -> lineage_v1_impact_workflow_service_pb2.InspectImpactWorkflowResponse:
    """Returns an impact."""
    response = lineage_v1_impact_workflow_service_pb2.InspectImpactWorkflowResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('InspectImpactWorkflow', extra={'fields': {'domain': 'lineage'}})
        await deps.repository.audit(request.context.tenant_id, 'InspectImpactWorkflow', {})
        response_0 = lineage_v1_lineage_node_workflow_service_pb2.CancelLineageNodeWorkflowResponse()
        response_1 = lineage_v1_lineage_edge_workflow_service_pb2.PauseLineageEdgeWorkflowResponse()
        outgoing_0 = lineage_v1_lineage_node_workflow_service_pb2.CancelLineageNodeWorkflowRequest(
            context=request.context,
            details=lineage_v1_lineage_node_workflow_service_pb2.CancelLineageNodeWorkflowRequest.Details(
                notify=common_v1_contact_pb2.ContactInfo(email=request.context.actor.email)
            ),
            lineage_node=lineage_v1_lineage_pb2.LineageNode(
                children=[
                    lineage_v1_lineage_pb2.LineageNode(
                        children=[
                            lineage_v1_lineage_pb2.LineageNode(
                                manager=identity_v1_refs_pb2.UserRef(user_id=request.context.actor.user_id)
                            )
                        ]
                    )
                ]
            )
        )
        response_0 = await deps.clients.lineage_lineage_node_workflow.CancelLineageNodeWorkflow(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        command_1 = ImpactWorkflowInspectImpactWorkflow1Command.model_validate(
            {
                'context': request.context,
                'lineage_edge_subject_display_name': response_0.lineage_node.manager.display_name,
                'details_notify_email': response_0.lineage_node.manager.email,
                'lineage_edge_attributes': dict(response_0.lineage_node.attributes)
            }
        )
        outgoing_1 = to_impact_workflow_inspect_impact_workflow1_command(command_1)
        response_1 = await deps.clients.lineage_lineage_edge_workflow.PauseLineageEdgeWorkflow(
            outgoing_1,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.lineage_node.audit.created_at
        returned_0_0_part_1 = response.impact.comments.add()
        if returned_0_0.ListFields():
            returned_0_0_part_1.created_at.MergeFrom(returned_0_0)
        returned_1_0 = response_1.outcome.status
        if returned_1_0:
            response.result.status = returned_1_0
        echoed_0 = request.impact_id
        response.impact.impact_id = echoed_0
        return response


async def handle_list_impact_workflows(
    deps: Dependencies,
    request: lineage_v1_impact_workflow_service_pb2.ListImpactWorkflowsRequest
) -> lineage_v1_impact_workflow_service_pb2.ListImpactWorkflowsResponse:
    """Lists impacts a page at a time."""
    response = lineage_v1_impact_workflow_service_pb2.ListImpactWorkflowsResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('ListImpactWorkflows', extra={'fields': {'order_by': request.order_by}})
        await deps.repository.audit(request.context.tenant_id, 'ListImpactWorkflows', {'order_by': request.order_by})
        return response


async def handle_pause_impact_workflow(
    deps: Dependencies,
    request: lineage_v1_impact_workflow_service_pb2.PauseImpactWorkflowRequest
) -> lineage_v1_impact_workflow_service_pb2.PauseImpactWorkflowResponse:
    """Pauses an impact."""
    response = lineage_v1_impact_workflow_service_pb2.PauseImpactWorkflowResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('PauseImpactWorkflow', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'PauseImpactWorkflow', {'reason': request.reason})
        await deps.repository.save_impact(request.context.tenant_id, request.impact)
        response_0 = lineage_v1_lineage_edge_reporting_service_pb2.StreamLineageEdgeMetricsResponse()
        response_1 = audit_v1_audit_event_query_service_pb2.ResolveAuditEventsResponse()
        outgoing_0 = lineage_v1_lineage_edge_reporting_service_pb2.StreamLineageEdgeMetricsRequest(
            context=request.context,
            subscriber=common_v1_contact_pb2.ContactInfo(email=request.details.notify.email)
        )
        async for chunk_0 in deps.clients.lineage_lineage_edge_reporting.StreamLineageEdgeMetrics(
            outgoing_0,
            timeout=deps.settings.timeout
        ):
            response_0 = chunk_0
        outgoing_1 = audit_v1_audit_event_query_service_pb2.ResolveAuditEventsRequest(context=request.context)
        response_1 = await hooks.impact_workflow_pause_impact_workflow1(
            deps.clients.audit_audit_event_query,
            outgoing_1,
            deps.settings.timeout
        )
        returned_1_0 = response_1.result.details
        response.result.details.update(returned_1_0)
        returned_1_1 = response_1.result.status
        if returned_1_1:
            response.result.status = returned_1_1
        echoed_0 = request.impact_id
        response.impact.impact_id = echoed_0
        echoed_1 = request.impact.priority
        response.impact.priority = echoed_1
        return response


async def handle_retry_impact_workflow(
    deps: Dependencies,
    request: lineage_v1_impact_workflow_service_pb2.RetryImpactWorkflowRequest
) -> lineage_v1_impact_workflow_service_pb2.RetryImpactWorkflowResponse:
    """Retrys an impact."""
    response = lineage_v1_impact_workflow_service_pb2.RetryImpactWorkflowResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('RetryImpactWorkflow', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'RetryImpactWorkflow', {'reason': request.reason})
        await deps.repository.save_impact(request.context.tenant_id, request.impact)
        response_0 = audit_v1_audit_event_query_service_pb2.CountAuditEventsResponse()
        outgoing_0 = audit_v1_audit_event_query_service_pb2.CountAuditEventsRequest(
            context=request.context,
            filter=audit_v1_audit_event_query_service_pb2.CountAuditEventsRequest.Filter(
                created_after=request.impact.audit.created_at
            )
        )
        response_0 = await deps.clients.audit_audit_event_query.CountAuditEvents(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.result.message
        if returned_0_0:
            response.outcome.message = returned_0_0
        echoed_0 = request.impact_id
        response.impact.impact_id = echoed_0
        echoed_1 = request.impact.requester
        response.impact.requester.CopyFrom(echoed_1)
        return response


async def handle_signal_impact_workflow(
    deps: Dependencies,
    request: lineage_v1_impact_workflow_service_pb2.SignalImpactWorkflowRequest
) -> lineage_v1_impact_workflow_service_pb2.SignalImpactWorkflowResponse:
    """Signals an impact."""
    response = lineage_v1_impact_workflow_service_pb2.SignalImpactWorkflowResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('SignalImpactWorkflow', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'SignalImpactWorkflow', {'reason': request.reason})
        await deps.repository.save_impact(request.context.tenant_id, request.impact)
        response_0 = lineage_v1_lineage_edge_calculation_service_pb2.EstimateLineageEdgeResponse()
        response_1 = anomalies_v1_detector_query_service_pb2.SuggestDetectorsResponse()
        response_2 = forecasting_v1_demand_forecast_validation_service_pb2.ValidateDemandForecastResponse()
        outgoing_0 = lineage_v1_lineage_edge_calculation_service_pb2.EstimateLineageEdgeRequest(
            context=request.context,
            lineage_edge=lineage_v1_lineage_pb2.LineageEdge(
                subject=lineage_v1_refs_pb2.ImpactRef(display_name=request.impact.customer.display_name)
            )
        )
        response_0 = await deps.clients.lineage_lineage_edge_calculation.EstimateLineageEdge(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        for item_1 in request.impact.comments:
            outgoing_1 = anomalies_v1_detector_query_service_pb2.SuggestDetectorsRequest(
                context=request.context,
                filter=anomalies_v1_detector_query_service_pb2.SuggestDetectorsRequest.Filter(
                    created_after=item_1.created_at
                )
            )
            response_1 = await deps.clients.anomalies_detector_query.SuggestDetectors(
                outgoing_1,
                timeout=deps.settings.timeout
            )
        outgoing_2 = forecasting_v1_demand_forecast_validation_service_pb2.ValidateDemandForecastRequest(
            context=request.context,
            demand_forecast=forecasting_v1_forecasting_pb2.DemandForecast(due_at=request.impact.sla.due_at),
            details=forecasting_v1_demand_forecast_validation_service_pb2.ValidateDemandForecastRequest.Details(
                contact=common_v1_contact_pb2.ContactInfo(
                    email=request.impact.assignee.email,
                    phone=request.impact.requester.phone,
                    preferred_channel=request.details.notify.preferred_channel
                )
            )
        )
        response_2 = await ImpactWorkflowSignalImpactWorkflow2Adapter(
            deps.clients.forecasting_demand_forecast_validation,
            deps.settings.timeout
        )(outgoing_2)
        returned_0_0 = response_0.result.status
        if returned_0_0:
            response.result.status = returned_0_0
        returned_0_1 = response_0.result.reference_ids
        response.result.reference_ids.extend(returned_0_1)
        returned_2_0 = response_2.result.reference_ids
        response.result.reference_ids.extend(returned_2_0)
        returned_2_1 = response_2.result.status
        if returned_2_1:
            response.outcome.status = returned_2_1
        echoed_0 = request.impact_id
        response.impact.impact_id = echoed_0
        echoed_1 = request.impact.subject
        response.impact.subject = echoed_1
        return response


async def handle_start_impact_workflow(
    deps: Dependencies,
    request: lineage_v1_impact_workflow_service_pb2.StartImpactWorkflowRequest
) -> lineage_v1_impact_workflow_service_pb2.StartImpactWorkflowResponse:
    """Starts an impact."""
    response = lineage_v1_impact_workflow_service_pb2.StartImpactWorkflowResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('StartImpactWorkflow', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'StartImpactWorkflow', {'reason': request.reason})
        await deps.repository.save_impact(request.context.tenant_id, request.impact)
        response_0 = lineage_v1_lineage_edge_workflow_service_pb2.CancelLineageEdgeWorkflowResponse()
        outgoing_0 = lineage_v1_lineage_edge_workflow_service_pb2.CancelLineageEdgeWorkflowRequest(
            context=request.context,
            details=lineage_v1_lineage_edge_workflow_service_pb2.CancelLineageEdgeWorkflowRequest.Details(
                notify=common_v1_contact_pb2.ContactInfo(
                    email=request.impact.customer.email,
                    name=request.impact.requester.name
                )
            ),
            lineage_edge=lineage_v1_lineage_pb2.LineageEdge(
                subject=lineage_v1_refs_pb2.ImpactRef(display_name=request.impact.customer.display_name)
            )
        )
        response_0 = await deps.clients.lineage_lineage_edge_workflow.CancelLineageEdgeWorkflow(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.result.reference_ids
        response.result.reference_ids.extend(returned_0_0)
        returned_0_1 = response_0.outcome.message
        if returned_0_1:
            response.outcome.message = returned_0_1
        echoed_0 = request.impact_id
        response.impact.impact_id = echoed_0
        echoed_1 = request.impact.status
        response.impact.status = echoed_1
        return response
