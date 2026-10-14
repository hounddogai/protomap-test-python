"""Checks lineage edges against the rules before anything acts on them."""

from __future__ import annotations

from collections.abc import AsyncIterator
from collections.abc import Awaitable
from collections.abc import Callable
from functools import partial
from typing import Any
from typing import cast
import asyncio
import logging

from google.protobuf.json_format import MessageToDict
from google.protobuf.json_format import MessageToJson
from google.protobuf.json_format import Parse
from google.protobuf.json_format import ParseDict
import grpc

from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.customers.v1 import refs_pb2 as customers_v1_refs_pb2
from acme.featureflags.v1 import feature_flag_service_pb2 as featureflags_v1_feature_flag_service_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.ledger.v1 import ledger_account_service_pb2 as ledger_v1_ledger_account_service_pb2
from acme.ledger.v1 import ledger_pb2 as ledger_v1_ledger_pb2
from acme.ledger.v1 import refs_pb2 as ledger_v1_refs_pb2
from acme.lineage.v1 import impact_calculation_service_pb2 as lineage_v1_impact_calculation_service_pb2
from acme.lineage.v1 import impact_calculation_service_pb2_grpc as lineage_v1_impact_calculation_service_pb2_grpc
from acme.lineage.v1 import lineage_edge_validation_service_pb2 as lineage_v1_lineage_edge_validation_service_pb2
from acme.lineage.v1 import (
    lineage_edge_validation_service_pb2_grpc as lineage_v1_lineage_edge_validation_service_pb2_grpc,
)
from acme.lineage.v1 import lineage_node_calculation_service_pb2 as lineage_v1_lineage_node_calculation_service_pb2
from acme.lineage.v1 import lineage_pb2 as lineage_v1_lineage_pb2
from acme.metrics.v1 import metric_alert_history_service_pb2 as metrics_v1_metric_alert_history_service_pb2
from acme.metrics.v1 import metric_series_export_service_pb2 as metrics_v1_metric_series_export_service_pb2
from acme.metrics.v1 import metric_series_notification_service_pb2 as metrics_v1_metric_series_notification_service_pb2
from acme.performers.v1 import performer_query_service_pb2 as performers_v1_performer_query_service_pb2

from acme_data.domains.lineage import hooks
from acme_data.domains.lineage.adapters import LineageEdgeValidationPreviewLineageEdge3Adapter
from acme_data.domains.lineage.dependencies import Dependencies
from acme_data.domains.lineage.models import LineageEdgeValidationCheckLineageEdgeEligibility1Command
from acme_data.domains.lineage.models import LineageEdgeValidationExplainLineageEdgeDecision0Command
from acme_data.domains.lineage.models import to_lineage_edge_validation_check_lineage_edge_eligibility1_command
from acme_data.domains.lineage.models import to_lineage_edge_validation_explain_lineage_edge_decision0_command
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_id
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class LineageEdgeValidationServicer(
    lineage_v1_lineage_edge_validation_service_pb2_grpc.LineageEdgeValidationServiceServicer
):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    async def CheckLineageEdgeEligibility(
        self, request: lineage_v1_lineage_edge_validation_service_pb2.CheckLineageEdgeEligibilityRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_lineage_edge_validation_service_pb2.CheckLineageEdgeEligibilityResponse:
        """Checks a lineage edge."""
        return await self.handle_check_lineage_edge_eligibility(request)

    @rpc_errors
    async def ExplainLineageEdgeDecision(
        self, request: lineage_v1_lineage_edge_validation_service_pb2.ExplainLineageEdgeDecisionRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_lineage_edge_validation_service_pb2.ExplainLineageEdgeDecisionResponse:
        """Explains a lineage edge."""
        return await self.handle_explain_lineage_edge_decision(request)

    @rpc_errors
    @retry_transient
    async def GetLineageEdgeRules(
        self, request: lineage_v1_lineage_edge_validation_service_pb2.GetLineageEdgeRulesRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_lineage_edge_validation_service_pb2.GetLineageEdgeRulesResponse:
        """Returns a lineage edge."""
        return await self.handle_get_lineage_edge_rules(request)

    @rpc_errors
    async def NormalizeLineageEdge(
        self, request: lineage_v1_lineage_edge_validation_service_pb2.NormalizeLineageEdgeRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_lineage_edge_validation_service_pb2.NormalizeLineageEdgeResponse:
        """Normalizes a lineage edge."""
        return await self.handle_normalize_lineage_edge(request)

    @rpc_errors
    async def PreviewLineageEdge(
        self, request: lineage_v1_lineage_edge_validation_service_pb2.PreviewLineageEdgeRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_lineage_edge_validation_service_pb2.PreviewLineageEdgeResponse:
        """Previews a lineage edge."""
        return await self.handle_preview_lineage_edge(request)

    @rpc_errors
    async def ScoreLineageEdge(
        self, request: lineage_v1_lineage_edge_validation_service_pb2.ScoreLineageEdgeRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_lineage_edge_validation_service_pb2.ScoreLineageEdgeResponse:
        """Scores a lineage edge."""
        return await self.handle_score_lineage_edge(request)

    @rpc_errors
    async def ValidateLineageEdge(
        self, request: lineage_v1_lineage_edge_validation_service_pb2.ValidateLineageEdgeRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_lineage_edge_validation_service_pb2.ValidateLineageEdgeResponse:
        """Validates a lineage edge."""
        return await self.handle_validate_lineage_edge(request)

    async def handle_check_lineage_edge_eligibility(
        self,
        request: lineage_v1_lineage_edge_validation_service_pb2.CheckLineageEdgeEligibilityRequest
    ) -> lineage_v1_lineage_edge_validation_service_pb2.CheckLineageEdgeEligibilityResponse:
        """Checks a lineage edge."""
        deps = self.deps
        response = lineage_v1_lineage_edge_validation_service_pb2.CheckLineageEdgeEligibilityResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CheckLineageEdgeEligibility', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'CheckLineageEdgeEligibility',
                {'reason': request.reason}
            )
            await deps.repository.save_lineage_edge(request.context.tenant_id, request.lineage_edge)
            response_0 = lineage_v1_impact_calculation_service_pb2.RecalculateImpactsResponse()
            response_1 = metrics_v1_metric_alert_history_service_pb2.RevertMetricAlertResponse()
            outgoing_0 = lineage_v1_impact_calculation_service_pb2.RecalculateImpactsRequest(
                context=request.context,
                impact=lineage_v1_lineage_pb2.Impact(
                    assignee=identity_v1_refs_pb2.UserRef(display_name=request.lineage_edge.subject.display_name),
                    requester=common_v1_contact_pb2.ContactInfo(
                        preferred_channel=request.details.contact.preferred_channel
                    )
                )
            )
            registered_0 = cast(
                lineage_v1_impact_calculation_service_pb2_grpc.ImpactCalculationServiceStub,
                deps.clients.registry['acme.lineage.v1.ImpactCalculationService']
            )
            response_0 = await registered_0.RecalculateImpacts(outgoing_0, timeout=deps.settings.timeout)
            command_1 = LineageEdgeValidationCheckLineageEdgeEligibility1Command(
                context=request.context,
                metric_alert_owner_user_id=response_0.impact.assignee.user_id,
                metric_alert_audit_etag=response_0.impact.audit.etag
            )
            outgoing_1 = to_lineage_edge_validation_check_lineage_edge_eligibility1_command(command_1)
            response_1 = await deps.clients.metrics_metric_alert_history.RevertMetricAlert(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.status
            if returned_0_0:
                response.outcome.status = returned_0_0
            returned_0_1 = response_0.result.correlation_id
            if returned_0_1:
                response.result.correlation_id = returned_0_1
            returned_1_0 = response_1.outcome.status
            if returned_1_0:
                response.result.status = returned_1_0
            returned_1_1 = response_1.result.message
            if returned_1_1:
                response.result.message = returned_1_1
            echoed_0 = request.lineage_edge_id
            response.lineage_edge.lineage_edge_id = echoed_0
            echoed_1 = request.lineage_edge.occurred_at
            response.lineage_edge.occurred_at.CopyFrom(echoed_1)
            return response

    async def handle_explain_lineage_edge_decision(
        self,
        request: lineage_v1_lineage_edge_validation_service_pb2.ExplainLineageEdgeDecisionRequest
    ) -> lineage_v1_lineage_edge_validation_service_pb2.ExplainLineageEdgeDecisionResponse:
        """Explains a lineage edge."""
        deps = self.deps
        response = lineage_v1_lineage_edge_validation_service_pb2.ExplainLineageEdgeDecisionResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ExplainLineageEdgeDecision', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ExplainLineageEdgeDecision',
                {'reason': request.reason}
            )
            await deps.repository.save_lineage_edge(request.context.tenant_id, request.lineage_edge)
            response_0 = lineage_v1_impact_calculation_service_pb2.EstimateImpactResponse()
            command_0 = LineageEdgeValidationExplainLineageEdgeDecision0Command.model_validate(
                {
                    'context': request.context,
                    'impact_requester_email': request.details.contact.email,
                    'impact_customer_display_name': request.lineage_edge.subject.display_name,
                    'impact_requester_phone': request.details.contact.phone
                }
            )
            outgoing_0 = to_lineage_edge_validation_explain_lineage_edge_decision0_command(command_0)
            response_0 = await deps.clients.lineage_impact_calculation.EstimateImpact(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.correlation_id
            if returned_0_0:
                response.lineage_edge.correlation_id = returned_0_0
            echoed_0 = request.lineage_edge_id
            response.lineage_edge.lineage_edge_id = echoed_0
            echoed_1 = request.lineage_edge.subject
            response.lineage_edge.subject.CopyFrom(echoed_1)
            return response

    async def handle_get_lineage_edge_rules(
        self,
        request: lineage_v1_lineage_edge_validation_service_pb2.GetLineageEdgeRulesRequest
    ) -> lineage_v1_lineage_edge_validation_service_pb2.GetLineageEdgeRulesResponse:
        """Returns a lineage edge."""
        deps = self.deps
        response = lineage_v1_lineage_edge_validation_service_pb2.GetLineageEdgeRulesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('GetLineageEdgeRules', extra={'fields': {'locale': request.context.locale}})
            await deps.repository.audit(
                request.context.tenant_id,
                'GetLineageEdgeRules',
                {'locale': request.context.locale}
            )
            echoed_0 = request.lineage_edge_id
            response.lineage_edge.lineage_edge_id = echoed_0
            return response

    async def handle_normalize_lineage_edge(
        self,
        request: lineage_v1_lineage_edge_validation_service_pb2.NormalizeLineageEdgeRequest
    ) -> lineage_v1_lineage_edge_validation_service_pb2.NormalizeLineageEdgeResponse:
        """Normalizes a lineage edge."""
        deps = self.deps
        response = lineage_v1_lineage_edge_validation_service_pb2.NormalizeLineageEdgeResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('NormalizeLineageEdge', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'NormalizeLineageEdge', {'reason': request.reason})
            await deps.repository.save_lineage_edge(request.context.tenant_id, request.lineage_edge)
            response_0 = ledger_v1_ledger_account_service_pb2.CreateLedgerAccountResponse()
            response_1 = lineage_v1_impact_calculation_service_pb2.ExplainImpactCalculationResponse()
            outgoing_0 = ledger_v1_ledger_account_service_pb2.CreateLedgerAccountRequest(
                context=request.context,
                ledger_account=ledger_v1_ledger_pb2.LedgerAccount(
                    holder=ledger_v1_refs_pb2.PostingBatchRef(display_name=request.lineage_edge.subject.display_name)
                )
            )
            send_0 = partial(deps.clients.ledger_ledger_account.CreateLedgerAccount, timeout=deps.settings.timeout)
            response_0 = await send_0(outgoing_0)
            outgoing_1 = lineage_v1_impact_calculation_service_pb2.ExplainImpactCalculationRequest(
                context=request.context,
                impact=lineage_v1_lineage_pb2.Impact(
                    audit=common_v1_audit_pb2.AuditInfo(
                        created_by=response_0.ledger_account.audit.created_by,
                        updated_by=response_0.ledger_account.audit.updated_by
                    ),
                    comments=[
                        lineage_v1_lineage_pb2.ImpactComment(created_at=response_0.ledger_account.audit.created_at)
                    ]
                )
            )
            response_1 = await hooks.lineage_edge_validation_normalize_lineage_edge1(
                deps.clients.lineage_impact_calculation,
                outgoing_1,
                deps.settings.timeout
            )
            returned_0_0 = response_0.result.correlation_id
            if returned_0_0:
                response.result.correlation_id = returned_0_0
            returned_0_1 = response_0.result.details
            response.result.details.update(returned_0_1)
            returned_1_0 = response_1.result.reference_ids
            response.result.reference_ids.extend(returned_1_0)
            echoed_0 = request.lineage_edge_id
            response.lineage_edge.lineage_edge_id = echoed_0
            echoed_1 = request.lineage_edge.sequence
            response.lineage_edge.sequence = echoed_1
            return response

    async def handle_preview_lineage_edge(
        self,
        request: lineage_v1_lineage_edge_validation_service_pb2.PreviewLineageEdgeRequest
    ) -> lineage_v1_lineage_edge_validation_service_pb2.PreviewLineageEdgeResponse:
        """Previews a lineage edge."""
        deps = self.deps
        response = lineage_v1_lineage_edge_validation_service_pb2.PreviewLineageEdgeResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('PreviewLineageEdge', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'PreviewLineageEdge', {'reason': request.reason})
            await deps.repository.save_lineage_edge(request.context.tenant_id, request.lineage_edge)
            response_0 = lineage_v1_impact_calculation_service_pb2.GetImpactRatesResponse()
            response_1 = lineage_v1_impact_calculation_service_pb2.SimulateImpactResponse()
            response_2 = metrics_v1_metric_series_notification_service_pb2.StreamMetricSeriesNoticesResponse()
            response_3 = performers_v1_performer_query_service_pb2.SuggestPerformersResponse()
            outgoing_0 = lineage_v1_impact_calculation_service_pb2.GetImpactRatesRequest()
            outgoing_0.context.CopyFrom(request.context)
            outgoing_0.impact_id = request.lineage_edge.subject.impact_id
            outgoing_0.context.tenant_id = tenant_id.get()
            response_0 = await deps.clients.lineage_impact_calculation.GetImpactRates(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            async for item_1 in async_messages(request.lineage_edge.measurements):
                outgoing_1 = lineage_v1_impact_calculation_service_pb2.SimulateImpactRequest(
                    context=request.context,
                    impact=lineage_v1_lineage_pb2.Impact(
                        comments=[lineage_v1_lineage_pb2.ImpactComment(created_at=item_1.observed_at)]
                    )
                )
                response_1 = await deps.clients.lineage_impact_calculation.SimulateImpact(
                    outgoing_1,
                    timeout=deps.settings.timeout
                )
            outgoing_2 = metrics_v1_metric_series_notification_service_pb2.StreamMetricSeriesNoticesRequest(
                context=request.context,
                subscriber=common_v1_contact_pb2.ContactInfo(
                    email=response_1.impact.assignee.email,
                    name=response_1.impact.requester.name,
                    preferred_channel=response_1.impact.requester.preferred_channel
                )
            )
            async for chunk_2 in deps.clients.metrics_metric_series_notification.StreamMetricSeriesNotices(
                outgoing_2,
                timeout=deps.settings.timeout
            ):
                response_2 = chunk_2
            outgoing_3 = performers_v1_performer_query_service_pb2.SuggestPerformersRequest(
                context=request.context,
                filter=performers_v1_performer_query_service_pb2.SuggestPerformersRequest.Filter(
                    created_after=request.lineage_edge.occurred_at,
                    labels=dict(response_0.result.details),
                    owner_id=response_0.impact.sla.policy_id
                )
            )
            response_3 = await LineageEdgeValidationPreviewLineageEdge3Adapter(
                deps.clients.performers_performer_query,
                deps.settings.timeout
            )(outgoing_3)
            returned_0_0 = response_0.result.details
            response.result.details.update(returned_0_0)
            returned_3_0 = response_3.result.message
            if returned_3_0:
                response.result.message = returned_3_0
            echoed_0 = request.lineage_edge_id
            response.lineage_edge.lineage_edge_id = echoed_0
            echoed_1 = request.lineage_edge.attributes
            response.lineage_edge.attributes.update(echoed_1)
            return response

    async def handle_score_lineage_edge(
        self,
        request: lineage_v1_lineage_edge_validation_service_pb2.ScoreLineageEdgeRequest
    ) -> lineage_v1_lineage_edge_validation_service_pb2.ScoreLineageEdgeResponse:
        """Scores a lineage edge."""
        deps = self.deps
        response = lineage_v1_lineage_edge_validation_service_pb2.ScoreLineageEdgeResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ScoreLineageEdge', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'ScoreLineageEdge', {'reason': request.reason})
            await deps.repository.save_lineage_edge(request.context.tenant_id, request.lineage_edge)
            response_0 = lineage_v1_impact_calculation_service_pb2.ExplainImpactCalculationResponse()
            response_1 = featureflags_v1_feature_flag_service_pb2.BatchGetFeatureFlagsResponse()
            response_2 = lineage_v1_impact_calculation_service_pb2.EstimateImpactResponse()
            for item_0 in request.lineage_edge.measurements:
                outgoing_0 = lineage_v1_impact_calculation_service_pb2.ExplainImpactCalculationRequest(
                    context=request.context,
                    impact=lineage_v1_lineage_pb2.Impact(
                        customer=customers_v1_refs_pb2.CustomerRef(
                            display_name=request.lineage_edge.subject.display_name
                        ),
                        priority=request.lineage_edge.subject.priority,
                        sla=lineage_v1_lineage_pb2.ImpactSla(due_at=item_0.observed_at)
                    ),
                    impact_id=request.lineage_edge.subject.impact_id
                )
                response_0 = await deps.clients.lineage_impact_calculation.ExplainImpactCalculation(
                    outgoing_0,
                    timeout=deps.settings.timeout
                )
            outgoing_1 = featureflags_v1_feature_flag_service_pb2.BatchGetFeatureFlagsRequest(context=request.context)
            response_1 = await deps.clients.featureflags_feature_flag.BatchGetFeatureFlags(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = lineage_v1_impact_calculation_service_pb2.EstimateImpactRequest(
                context=request.context,
                impact=lineage_v1_lineage_pb2.Impact(
                    assignee=identity_v1_refs_pb2.UserRef(display_name=response_0.impact.assignee.display_name)
                )
            )
            method_name_2 = 'EstimateImpact'
            response_2 = await getattr(
                deps.clients.lineage_impact_calculation,
                method_name_2
            )(outgoing_2, timeout=deps.settings.timeout)
            returned_1_0 = response_1.result.details
            response.result.details.update(returned_1_0)
            returned_1_1 = response_1.result.message
            if returned_1_1:
                response.result.message = returned_1_1
            returned_2_0 = response_2.impact.impact_id
            if returned_2_0:
                response.lineage_edge.subject.impact_id = returned_2_0
            echoed_0 = request.lineage_edge_id
            response.lineage_edge.lineage_edge_id = echoed_0
            echoed_1 = request.lineage_edge.correlation_id
            response.lineage_edge.correlation_id = echoed_1
            return response

    async def handle_validate_lineage_edge(
        self,
        request: lineage_v1_lineage_edge_validation_service_pb2.ValidateLineageEdgeRequest
    ) -> lineage_v1_lineage_edge_validation_service_pb2.ValidateLineageEdgeResponse:
        """Validates a lineage edge."""
        deps = self.deps
        response = lineage_v1_lineage_edge_validation_service_pb2.ValidateLineageEdgeResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ValidateLineageEdge', extra={'fields': {'locale': request.details.locale}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ValidateLineageEdge',
                {'locale': request.details.locale}
            )
            await deps.repository.save_lineage_edge(request.context.tenant_id, request.lineage_edge)
            response_0 = lineage_v1_impact_calculation_service_pb2.CalculateImpactResponse()
            response_1 = metrics_v1_metric_series_export_service_pb2.ScheduleMetricSeriesExportResponse()
            response_2 = lineage_v1_lineage_node_calculation_service_pb2.CalculateLineageNodeResponse()
            response_3 = lineage_v1_impact_calculation_service_pb2.SimulateImpactResponse()
            fields_0: dict[str, Any] = {
                'context': request.context,
                'impact': {'requester': {'preferred_channel': request.details.contact.preferred_channel}}
            }
            outgoing_0 = lineage_v1_impact_calculation_service_pb2.CalculateImpactRequest(**fields_0)
            response_0 = await deps.clients.lineage_impact_calculation.CalculateImpact(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = metrics_v1_metric_series_export_service_pb2.ScheduleMetricSeriesExportRequest(
                annotations=dict(request.annotations),
                context=request.context,
                details=metrics_v1_metric_series_export_service_pb2.ScheduleMetricSeriesExportRequest.Details(
                    filters=dict(response_0.result.details)
                ),
                reason=request.reason
            )
            document_1 = MessageToDict(outgoing_1, preserving_proto_field_name=True)
            outgoing_1 = ParseDict(
                document_1,
                metrics_v1_metric_series_export_service_pb2.ScheduleMetricSeriesExportRequest()
            )
            response_1 = await deps.clients.metrics_metric_series_export.ScheduleMetricSeriesExport(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = lineage_v1_lineage_node_calculation_service_pb2.CalculateLineageNodeRequest(
                context=request.context,
                lineage_node=lineage_v1_lineage_pb2.LineageNode(
                    children=[
                        lineage_v1_lineage_pb2.LineageNode(
                            children=[
                                lineage_v1_lineage_pb2.LineageNode(
                                    audit=common_v1_audit_pb2.AuditInfo(updated_at=response_0.impact.audit.updated_at),
                                    manager=identity_v1_refs_pb2.UserRef(
                                        display_name=response_0.impact.customer.display_name,
                                        email=response_0.impact.requester.email
                                    )
                                )
                            ]
                        )
                    ]
                )
            )
            document_2 = MessageToJson(outgoing_2, preserving_proto_field_name=True)
            outgoing_2 = Parse(
                document_2,
                lineage_v1_lineage_node_calculation_service_pb2.CalculateLineageNodeRequest()
            )
            response_2 = await deps.clients.lineage_lineage_node_calculation.CalculateLineageNode(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            outgoing_3 = lineage_v1_impact_calculation_service_pb2.SimulateImpactRequest()
            outgoing_3.context.CopyFrom(request.context)
            outgoing_3.details.destination.region = response_2.lineage_node.location.region
            outgoing_3.details.destination.postal_code = response_2.lineage_node.location.postal_code
            merged_3 = lineage_v1_impact_calculation_service_pb2.SimulateImpactRequest()
            merged_3.MergeFrom(outgoing_3)
            outgoing_3.CopyFrom(merged_3)
            response_3 = await deps.clients.lineage_impact_calculation.SimulateImpact(
                outgoing_3,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.correlation_id
            if returned_0_0:
                response.result.correlation_id = returned_0_0
            returned_0_1 = response_0.result.status
            if returned_0_1:
                response.result.status = returned_0_1
            returned_1_0 = response_1.result.details
            response.result.details.update(returned_1_0)
            returned_2_0 = response_2.result.reference_ids
            response.result.reference_ids.extend(returned_2_0)
            returned_2_1 = response_2.lineage_node.manager.display_name
            if returned_2_1:
                response.lineage_edge.subject.display_name = returned_2_1
            returned_3_0 = response_3.impact.impact_id
            if returned_3_0:
                response.lineage_edge.subject.impact_id = returned_3_0
            echoed_0 = request.lineage_edge_id
            response.lineage_edge.lineage_edge_id = echoed_0
            echoed_1 = request.lineage_edge.source
            response.lineage_edge.source = echoed_1
            return response
