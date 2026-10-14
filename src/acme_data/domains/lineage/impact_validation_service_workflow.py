"""Application workflow for Impact Validation."""

from __future__ import annotations

from collections.abc import Awaitable
from collections.abc import Callable
from functools import partial
from typing import cast
import asyncio
import logging

from google.protobuf.any_pb2 import Any as AnyMessage
from google.protobuf.json_format import MessageToJson
from google.protobuf.json_format import Parse

from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.configuration.v1 import config_set_query_service_pb2 as configuration_v1_config_set_query_service_pb2
from acme.customers.v1 import refs_pb2 as customers_v1_refs_pb2
from acme.documents.v1 import document_query_service_pb2 as documents_v1_document_query_service_pb2
from acme.documents.v1 import document_validation_service_pb2 as documents_v1_document_validation_service_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.identity.v1 import user_query_service_pb2 as identity_v1_user_query_service_pb2
from acme.lineage.v1 import impact_calculation_service_pb2 as lineage_v1_impact_calculation_service_pb2
from acme.lineage.v1 import impact_validation_service_pb2 as lineage_v1_impact_validation_service_pb2
from acme.lineage.v1 import lineage_edge_validation_service_pb2 as lineage_v1_lineage_edge_validation_service_pb2
from acme.lineage.v1 import lineage_node_calculation_service_pb2 as lineage_v1_lineage_node_calculation_service_pb2
from acme.lineage.v1 import lineage_node_validation_service_pb2 as lineage_v1_lineage_node_validation_service_pb2
from acme.lineage.v1 import lineage_pb2 as lineage_v1_lineage_pb2
from acme.lineage.v1 import refs_pb2 as lineage_v1_refs_pb2
from acme.metrics.v1 import dashboard_history_service_pb2 as metrics_v1_dashboard_history_service_pb2
from acme.metrics.v1 import dashboard_history_service_pb2_grpc as metrics_v1_dashboard_history_service_pb2_grpc
from acme.metrics.v1 import metrics_pb2 as metrics_v1_metrics_pb2
from acme.search.v1 import search_index_service_pb2 as search_v1_search_index_service_pb2

from acme_data.domains.lineage import hooks
from acme_data.domains.lineage.adapters import ImpactValidationNormalizeImpact0Adapter
from acme_data.domains.lineage.adapters import ImpactValidationNormalizeImpact0Port
from acme_data.domains.lineage.adapters import ImpactValidationPreviewImpact0Adapter
from acme_data.domains.lineage.dependencies import Dependencies
from acme_data.domains.lineage.models import ImpactValidationExplainImpactDecision3Command
from acme_data.domains.lineage.models import to_impact_validation_explain_impact_decision3_command
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import run_steps
from acme_data.platform.tenancy import tenant_id
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class ImpactValidationServicerWorkflow:
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    async def handle_check_impact_eligibility(
        self,
        request: lineage_v1_impact_validation_service_pb2.CheckImpactEligibilityRequest
    ) -> lineage_v1_impact_validation_service_pb2.CheckImpactEligibilityResponse:
        """Checks an impact."""
        deps = self.deps
        response = lineage_v1_impact_validation_service_pb2.CheckImpactEligibilityResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CheckImpactEligibility', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'CheckImpactEligibility', {'reason': request.reason})
            await deps.repository.save_impact(request.context.tenant_id, request.impact)
            response_0 = lineage_v1_lineage_edge_validation_service_pb2.ExplainLineageEdgeDecisionResponse()
            response_1 = identity_v1_user_query_service_pb2.ExportUsersResponse()
            response_2 = lineage_v1_lineage_node_calculation_service_pb2.QuoteLineageNodeResponse()
            response_3 = configuration_v1_config_set_query_service_pb2.CountConfigSetsResponse()
            outgoing_0 = lineage_v1_lineage_edge_validation_service_pb2.ExplainLineageEdgeDecisionRequest(
                context=request.context,
                details=lineage_v1_lineage_edge_validation_service_pb2.ExplainLineageEdgeDecisionRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(phone=request.impact.requester.phone)
                )
            )
            method_name_0 = 'ExplainLineageEdgeDecision'
            response_0 = await getattr(
                deps.clients.lineage_lineage_edge_validation,
                method_name_0
            )(outgoing_0, timeout=deps.settings.timeout)
            outgoing_1 = identity_v1_user_query_service_pb2.ExportUsersRequest(
                context=request.context,
                filter=identity_v1_user_query_service_pb2.ExportUsersRequest.Filter(
                    created_after=request.impact.audit.created_at,
                    labels=dict(response_0.lineage_edge.attributes),
                    owner_id=response_0.lineage_edge.subject.impact_id
                )
            )
            async for chunk_1 in deps.clients.identity_user_query.ExportUsers(
                outgoing_1,
                timeout=deps.settings.timeout
            ):
                response_1 = chunk_1
            callbacks_2: list[
                Callable[[], Awaitable[lineage_v1_lineage_node_calculation_service_pb2.QuoteLineageNodeResponse]]
            ] = []
            for item_2 in request.impact.comments:
                outgoing_2 = lineage_v1_lineage_node_calculation_service_pb2.QuoteLineageNodeRequest(
                    context=request.context,
                    lineage_node=lineage_v1_lineage_pb2.LineageNode(
                        children=[
                            lineage_v1_lineage_pb2.LineageNode(
                                audit=common_v1_audit_pb2.AuditInfo(created_at=item_2.created_at)
                            )
                        ]
                    )
                )
                async def send_2(
                    payload: lineage_v1_lineage_node_calculation_service_pb2.QuoteLineageNodeRequest = outgoing_2
                ) -> lineage_v1_lineage_node_calculation_service_pb2.QuoteLineageNodeResponse:
                    return await deps.clients.lineage_lineage_node_calculation.QuoteLineageNode(
                        payload,
                        timeout=deps.settings.timeout
                    )
                callbacks_2.append(send_2)
            for callback_2 in callbacks_2:
                response_2 = await callback_2()
            outgoing_3 = configuration_v1_config_set_query_service_pb2.CountConfigSetsRequest(
                context=request.context,
                filter=configuration_v1_config_set_query_service_pb2.CountConfigSetsRequest.Filter(
                    created_after=response_0.lineage_edge.occurred_at,
                    labels=dict(request.impact.custom_fields),
                    region=response_2.lineage_node.location.region
                )
            )
            document_3 = MessageToJson(outgoing_3, preserving_proto_field_name=True)
            outgoing_3 = Parse(document_3, configuration_v1_config_set_query_service_pb2.CountConfigSetsRequest())
            response_3 = await deps.clients.configuration_config_set_query.CountConfigSets(
                outgoing_3,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.lineage_edge.subject.priority
            if returned_0_0:
                response.impact.priority = returned_0_0
            returned_0_1 = response_0.outcome.next_steps
            response.outcome.next_steps.extend(returned_0_1)
            returned_3_0 = response_3.result.message
            if returned_3_0:
                response.result.message = returned_3_0
            returned_3_1 = response_3.result.correlation_id
            if returned_3_1:
                response.result.correlation_id = returned_3_1
            echoed_0 = request.impact_id
            response.impact.impact_id = echoed_0
            echoed_1 = request.impact.subject
            response.impact.subject = echoed_1
            return response

    async def handle_explain_impact_decision(
        self,
        request: lineage_v1_impact_validation_service_pb2.ExplainImpactDecisionRequest
    ) -> lineage_v1_impact_validation_service_pb2.ExplainImpactDecisionResponse:
        """Explains an impact."""
        deps = self.deps
        response = lineage_v1_impact_validation_service_pb2.ExplainImpactDecisionResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ExplainImpactDecision', extra={'fields': {'impact_id': request.impact_id}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ExplainImpactDecision',
                {'impact_id': request.impact_id}
            )
            await deps.repository.save_impact(request.context.tenant_id, request.impact)
            response_0 = documents_v1_document_query_service_pb2.SummarizeDocumentsResponse()
            response_1 = lineage_v1_lineage_edge_validation_service_pb2.ScoreLineageEdgeResponse()
            response_2 = metrics_v1_dashboard_history_service_pb2.RevertDashboardResponse()
            response_3 = lineage_v1_impact_calculation_service_pb2.GetImpactRatesResponse()
            outgoing_0 = documents_v1_document_query_service_pb2.SummarizeDocumentsRequest()
            outgoing_0.context.CopyFrom(request.context)
            outgoing_0.reason = request.reason
            outgoing_0.annotations.update(dict(request.annotations))
            merged_0 = documents_v1_document_query_service_pb2.SummarizeDocumentsRequest()
            merged_0.MergeFrom(outgoing_0)
            outgoing_0.CopyFrom(merged_0)
            response_0 = await deps.clients.documents_document_query.SummarizeDocuments(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = lineage_v1_lineage_edge_validation_service_pb2.ScoreLineageEdgeRequest(
                context=request.context,
                lineage_edge=lineage_v1_lineage_pb2.LineageEdge(
                    subject=lineage_v1_refs_pb2.ImpactRef(display_name=request.impact.customer.display_name)
                )
            )
            envelope_1 = AnyMessage()
            envelope_1.Pack(outgoing_1)
            outgoing_1 = lineage_v1_lineage_edge_validation_service_pb2.ScoreLineageEdgeRequest()
            if not envelope_1.Unpack(outgoing_1):
                raise ValueError("partner envelope contains the wrong request type")
            response_1 = await deps.clients.lineage_lineage_edge_validation.ScoreLineageEdge(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = metrics_v1_dashboard_history_service_pb2.RevertDashboardRequest(
                context=request.context,
                dashboard=metrics_v1_metrics_pb2.Dashboard(
                    audit=common_v1_audit_pb2.AuditInfo(
                        etag=request.impact.audit.etag,
                        updated_at=request.impact.audit.updated_at,
                        updated_by=request.impact.audit.updated_by
                    )
                )
            )
            registered_2 = cast(
                metrics_v1_dashboard_history_service_pb2_grpc.DashboardHistoryServiceStub,
                deps.clients.registry['acme.metrics.v1.DashboardHistoryService']
            )
            response_2 = await registered_2.RevertDashboard(outgoing_2, timeout=deps.settings.timeout)
            command_3 = ImpactValidationExplainImpactDecision3Command(
                context=request.context,
                impact_id=request.impact.impact_id
            )
            outgoing_3 = to_impact_validation_explain_impact_decision3_command(command_3)
            response_3 = await deps.clients.lineage_impact_calculation.GetImpactRates(
                outgoing_3,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.status
            if returned_0_0:
                response.outcome.status = returned_0_0
            returned_0_1 = response_0.result.details
            response.result.details.update(returned_0_1)
            returned_1_0 = response_1.lineage_edge.subject.impact_id
            if returned_1_0:
                response.impact.impact_id = returned_1_0
            returned_2_0 = response_2.dashboard.audit.updated_by
            if returned_2_0:
                response.impact.audit.updated_by = returned_2_0
            returned_3_0 = response_3.impact.audit.updated_at
            if returned_3_0.ListFields():
                response.impact.audit.updated_at.MergeFrom(returned_3_0)
            echoed_0 = request.impact.status
            response.impact.status = echoed_0
            echoed_1 = request.impact.requester
            response.impact.requester.CopyFrom(echoed_1)
            return response

    async def handle_get_impact_rules(
        self,
        request: lineage_v1_impact_validation_service_pb2.GetImpactRulesRequest
    ) -> lineage_v1_impact_validation_service_pb2.GetImpactRulesResponse:
        """Returns an impact."""
        deps = self.deps
        response = lineage_v1_impact_validation_service_pb2.GetImpactRulesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('GetImpactRules', extra={'fields': {'domain': 'lineage'}})
            await deps.repository.audit(request.context.tenant_id, 'GetImpactRules', {})
            response_0 = lineage_v1_impact_calculation_service_pb2.QuoteImpactResponse()
            outgoing_0 = lineage_v1_impact_calculation_service_pb2.QuoteImpactRequest(
                context=request.context,
                impact=lineage_v1_lineage_pb2.Impact(
                    assignee=identity_v1_refs_pb2.UserRef(user_id=request.context.actor.user_id),
                    customer=customers_v1_refs_pb2.CustomerRef(email=request.context.actor.email)
                ),
                impact_id=request.impact_id
            )
            response_0 = await deps.clients.lineage_impact_calculation.QuoteImpact(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.impact.customer.email
            if returned_0_0:
                response.impact.assignee.email = returned_0_0
            returned_0_1 = response_0.impact.customer.display_name
            if returned_0_1:
                response.impact.assignee.display_name = returned_0_1
            echoed_0 = request.impact_id
            response.impact.impact_id = echoed_0
            return response

    async def handle_lint_impacts(
        self,
        request: lineage_v1_impact_validation_service_pb2.LintImpactsRequest
    ) -> lineage_v1_impact_validation_service_pb2.LintImpactsResponse:
        """Lints an impact."""
        deps = self.deps
        response = lineage_v1_impact_validation_service_pb2.LintImpactsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('LintImpacts', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'LintImpacts', {'reason': request.reason})
            await deps.repository.save_impact(request.context.tenant_id, request.impact)
            response_0 = lineage_v1_lineage_node_calculation_service_pb2.CalculateLineageNodeResponse()
            response_1 = lineage_v1_lineage_node_calculation_service_pb2.EstimateLineageNodeResponse()
            response_2 = lineage_v1_lineage_edge_validation_service_pb2.ScoreLineageEdgeResponse()
            async for item_0 in async_messages(request.impact.history):
                outgoing_0 = lineage_v1_lineage_node_calculation_service_pb2.CalculateLineageNodeRequest(
                    context=request.context,
                    lineage_node=lineage_v1_lineage_pb2.LineageNode(
                        children=[
                            lineage_v1_lineage_pb2.LineageNode(
                                children=[
                                    lineage_v1_lineage_pb2.LineageNode(
                                        audit=common_v1_audit_pb2.AuditInfo(updated_at=item_0.changed_at),
                                        manager=identity_v1_refs_pb2.UserRef(email=request.impact.requester.email)
                                    )
                                ]
                            )
                        ]
                    )
                )
                response_0 = await deps.clients.lineage_lineage_node_calculation.CalculateLineageNode(
                    outgoing_0,
                    timeout=deps.settings.timeout
                )
            outgoing_1 = lineage_v1_lineage_node_calculation_service_pb2.EstimateLineageNodeRequest(
                context=request.context,
                lineage_node=lineage_v1_lineage_pb2.LineageNode(
                    children=[
                        lineage_v1_lineage_pb2.LineageNode(
                            children=[
                                lineage_v1_lineage_pb2.LineageNode(
                                    location=common_v1_address_pb2.PostalAddress(
                                        locality=response_0.lineage_node.location.locality
                                    ),
                                    manager=identity_v1_refs_pb2.UserRef(email=response_0.lineage_node.manager.email)
                                )
                            ]
                        )
                    ]
                )
            )
            response_1 = await hooks.impact_validation_lint_impacts1(
                deps.clients.lineage_lineage_node_calculation,
                outgoing_1,
                deps.settings.timeout
            )
            outgoing_2 = lineage_v1_lineage_edge_validation_service_pb2.ScoreLineageEdgeRequest()
            outgoing_2.context.CopyFrom(request.context)
            outgoing_2.details.destination.region = response_1.lineage_node.location.region
            outgoing_2.context.tenant_id = tenant_id.get()
            response_2 = await deps.clients.lineage_lineage_edge_validation.ScoreLineageEdge(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            returned_1_0 = response_1.lineage_node.audit.created_by
            if returned_1_0:
                response.impact.audit.created_by = returned_1_0
            returned_1_1 = response_1.result.correlation_id
            if returned_1_1:
                response.result.correlation_id = returned_1_1
            returned_2_0 = response_2.result.message
            if returned_2_0:
                response.outcome.message = returned_2_0
            returned_2_1 = response_2.result.message
            if returned_2_1:
                response.result.message = returned_2_1
            echoed_0 = request.impact_id
            response.impact.impact_id = echoed_0
            echoed_1 = request.impact.assignee
            response.impact.assignee.CopyFrom(echoed_1)
            return response

    async def handle_normalize_impact(
        self,
        request: lineage_v1_impact_validation_service_pb2.NormalizeImpactRequest
    ) -> lineage_v1_impact_validation_service_pb2.NormalizeImpactResponse:
        """Normalizes an impact."""
        deps = self.deps
        response = lineage_v1_impact_validation_service_pb2.NormalizeImpactResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('NormalizeImpact', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'NormalizeImpact', {'reason': request.reason})
            await deps.repository.save_impact(request.context.tenant_id, request.impact)
            response_0 = lineage_v1_lineage_node_calculation_service_pb2.RecalculateLineageNodesResponse()
            response_1 = search_v1_search_index_service_pb2.BatchGetSearchIndexesResponse()
            outgoing_0 = lineage_v1_lineage_node_calculation_service_pb2.RecalculateLineageNodesRequest(
                context=request.context,
                lineage_node=lineage_v1_lineage_pb2.LineageNode(
                    children=[
                        lineage_v1_lineage_pb2.LineageNode(
                            children=[
                                lineage_v1_lineage_pb2.LineageNode(
                                    audit=common_v1_audit_pb2.AuditInfo(updated_by=request.impact.audit.updated_by),
                                    manager=identity_v1_refs_pb2.UserRef(email=request.impact.customer.email)
                                )
                            ]
                        )
                    ]
                )
            )
            port_0: ImpactValidationNormalizeImpact0Port = ImpactValidationNormalizeImpact0Adapter(
                deps.clients.lineage_lineage_node_calculation,
                deps.settings.timeout
            )
            response_0 = await port_0.execute(outgoing_0)
            outgoing_1 = search_v1_search_index_service_pb2.BatchGetSearchIndexesRequest(context=request.context)
            steps_1 = [
                partial(
                    deps.clients.search_search_index.BatchGetSearchIndexes,
                    outgoing_1,
                    timeout=deps.settings.timeout
                )
            ]
            results_1 = await run_steps(steps_1)
            response_1 = results_1[-1]
            returned_0_0 = response_0.result.status
            if returned_0_0:
                response.outcome.status = returned_0_0
            returned_1_0 = response_1.result.status
            if returned_1_0:
                response.result.status = returned_1_0
            returned_1_1 = response_1.result.correlation_id
            if returned_1_1:
                response.result.correlation_id = returned_1_1
            echoed_0 = request.impact_id
            response.impact.impact_id = echoed_0
            echoed_1 = request.impact.priority
            response.impact.priority = echoed_1
            return response

    async def handle_preview_impact(
        self,
        request: lineage_v1_impact_validation_service_pb2.PreviewImpactRequest
    ) -> lineage_v1_impact_validation_service_pb2.PreviewImpactResponse:
        """Previews an impact."""
        deps = self.deps
        response = lineage_v1_impact_validation_service_pb2.PreviewImpactResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('PreviewImpact', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'PreviewImpact', {'reason': request.reason})
            await deps.repository.save_impact(request.context.tenant_id, request.impact)
            response_0 = lineage_v1_lineage_node_validation_service_pb2.LintLineageNodesResponse()
            response_1 = lineage_v1_lineage_node_calculation_service_pb2.CalculateLineageNodeResponse()
            outgoing_0 = lineage_v1_lineage_node_validation_service_pb2.LintLineageNodesRequest(
                context=request.context,
                lineage_node=lineage_v1_lineage_pb2.LineageNode(
                    children=[
                        lineage_v1_lineage_pb2.LineageNode(
                            children=[
                                lineage_v1_lineage_pb2.LineageNode(
                                    audit=common_v1_audit_pb2.AuditInfo(created_by=request.impact.audit.created_by),
                                    manager=identity_v1_refs_pb2.UserRef(
                                        display_name=request.impact.customer.display_name,
                                        email=request.details.contact.email,
                                        user_id=request.impact.assignee.user_id
                                    )
                                )
                            ]
                        )
                    ]
                )
            )
            response_0 = await ImpactValidationPreviewImpact0Adapter(
                deps.clients.lineage_lineage_node_validation,
                deps.settings.timeout
            )(outgoing_0)
            outgoing_1 = lineage_v1_lineage_node_calculation_service_pb2.CalculateLineageNodeRequest(
                context=request.context,
                lineage_node=lineage_v1_lineage_pb2.LineageNode(
                    children=[
                        lineage_v1_lineage_pb2.LineageNode(
                            children=[
                                lineage_v1_lineage_pb2.LineageNode(
                                    audit=common_v1_audit_pb2.AuditInfo(created_by=request.impact.audit.created_by),
                                    manager=identity_v1_refs_pb2.UserRef(
                                        email=request.impact.requester.email,
                                        user_id=response_0.lineage_node.manager.user_id
                                    )
                                )
                            ],
                            manager=identity_v1_refs_pb2.UserRef(email=request.details.contact.email)
                        )
                    ]
                )
            )
            response_1 = cast(lineage_v1_lineage_node_calculation_service_pb2.CalculateLineageNodeResponse, await deps.bus.request(
                'acme.lineage.v1.ImpactValidationService/PreviewImpact/1', outgoing_1, deps.settings.timeout,
            ))
            returned_0_0 = response_0.lineage_node.audit.updated_by
            if returned_0_0:
                response.impact.audit.updated_by = returned_0_0
            returned_0_1 = response_0.outcome.next_steps
            response.outcome.next_steps.extend(returned_0_1)
            returned_1_0 = response_1.lineage_node.audit.created_at
            returned_1_0_part_1 = response.impact.comments.add()
            if returned_1_0.ListFields():
                returned_1_0_part_1.created_at.MergeFrom(returned_1_0)
            returned_1_1 = response_1.lineage_node.manager.email
            if returned_1_1:
                response.impact.requester.email = returned_1_1
            echoed_0 = request.impact_id
            response.impact.impact_id = echoed_0
            echoed_1 = request.impact.status
            response.impact.status = echoed_1
            return response

    async def handle_validate_impact(
        self,
        request: lineage_v1_impact_validation_service_pb2.ValidateImpactRequest
    ) -> lineage_v1_impact_validation_service_pb2.ValidateImpactResponse:
        """Validates an impact."""
        deps = self.deps
        response = lineage_v1_impact_validation_service_pb2.ValidateImpactResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ValidateImpact', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'ValidateImpact', {'reason': request.reason})
            await deps.repository.save_impact(request.context.tenant_id, request.impact)
            response_0 = lineage_v1_lineage_edge_validation_service_pb2.PreviewLineageEdgeResponse()
            response_1 = documents_v1_document_validation_service_pb2.LintDocumentsResponse()
            outgoing_0 = lineage_v1_lineage_edge_validation_service_pb2.PreviewLineageEdgeRequest(
                context=request.context,
                details=lineage_v1_lineage_edge_validation_service_pb2.PreviewLineageEdgeRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(
                        name=request.details.contact.name,
                        phone=request.impact.requester.phone
                    )
                )
            )
            outgoing_1 = documents_v1_document_validation_service_pb2.LintDocumentsRequest(
                context=request.context,
                details=documents_v1_document_validation_service_pb2.LintDocumentsRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(email=request.impact.customer.email)
                )
            )
            response_0, response_1 = await asyncio.gather(
                deps.clients.lineage_lineage_edge_validation.PreviewLineageEdge(
                    outgoing_0,
                    timeout=deps.settings.timeout
                ),
                deps.clients.documents_document_validation.LintDocuments(outgoing_1, timeout=deps.settings.timeout),
            )
            returned_0_0 = response_0.lineage_edge.correlation_id
            if returned_0_0:
                response.result.correlation_id = returned_0_0
            returned_1_0 = response_1.result.correlation_id
            if returned_1_0:
                response.result.correlation_id = returned_1_0
            returned_1_1 = response_1.document.audit.created_by
            if returned_1_1:
                response.impact.audit.created_by = returned_1_1
            echoed_0 = request.impact_id
            response.impact.impact_id = echoed_0
            echoed_1 = request.impact.status
            response.impact.status = echoed_1
            return response
