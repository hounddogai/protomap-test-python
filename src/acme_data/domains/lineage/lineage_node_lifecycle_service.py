"""Moves a lineage node between the states of its lifecycle."""

from __future__ import annotations

from collections.abc import AsyncIterator
from dataclasses import dataclass
from functools import partial
from typing import Any
from typing import cast
import logging

from google.protobuf.json_format import MessageToDict
from google.protobuf.json_format import MessageToJson
from google.protobuf.json_format import Parse
from google.protobuf.json_format import ParseDict
import grpc

from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.customers.v1 import customer_query_service_pb2 as customers_v1_customer_query_service_pb2
from acme.forms.v1 import form_query_service_pb2 as forms_v1_form_query_service_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.labeling.v1 import labeling_pb2 as labeling_v1_labeling_pb2
from acme.labeling.v1 import labeling_task_validation_service_pb2 as labeling_v1_labeling_task_validation_service_pb2
from acme.lineage.v1 import impact_import_service_pb2 as lineage_v1_impact_import_service_pb2
from acme.lineage.v1 import lineage_edge_import_service_pb2 as lineage_v1_lineage_edge_import_service_pb2
from acme.lineage.v1 import lineage_edge_sync_service_pb2 as lineage_v1_lineage_edge_sync_service_pb2
from acme.lineage.v1 import lineage_node_calculation_service_pb2 as lineage_v1_lineage_node_calculation_service_pb2
from acme.lineage.v1 import lineage_node_lifecycle_service_pb2 as lineage_v1_lineage_node_lifecycle_service_pb2
from acme.lineage.v1 import (
    lineage_node_lifecycle_service_pb2_grpc as lineage_v1_lineage_node_lifecycle_service_pb2_grpc,
)
from acme.lineage.v1 import lineage_node_reporting_service_pb2 as lineage_v1_lineage_node_reporting_service_pb2
from acme.lineage.v1 import lineage_pb2 as lineage_v1_lineage_pb2
from acme.lineage.v1 import refs_pb2 as lineage_v1_refs_pb2
from acme.metrics.v1 import dashboard_validation_service_pb2 as metrics_v1_dashboard_validation_service_pb2
from acme.performers.v1 import performer_query_service_pb2 as performers_v1_performer_query_service_pb2
from acme.recommendations.v1 import (
    recommendation_model_calculation_service_pb2 as recommendations_v1_recommendation_model_calculation_service_pb2,
)

from acme_data.domains.lineage import hooks
from acme_data.domains.lineage.adapters import LineageNodeLifecycleExpireLineageNode0Adapter
from acme_data.domains.lineage.adapters import LineageNodeLifecycleExpireLineageNode0Port
from acme_data.domains.lineage.dependencies import Dependencies
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import run_steps
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_id
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


@dataclass(slots=True)
class LineageNodeLifecycleServicer(
    lineage_v1_lineage_node_lifecycle_service_pb2_grpc.LineageNodeLifecycleServiceServicer
):
    deps: Dependencies

    @rpc_errors
    async def ActivateLineageNode(
        self, request: lineage_v1_lineage_node_lifecycle_service_pb2.ActivateLineageNodeRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_lineage_node_lifecycle_service_pb2.ActivateLineageNodeResponse:
        """Activates a lineage node."""
        return await self.handle_activate_lineage_node(request)

    @rpc_errors
    async def ExpireLineageNode(
        self, request: lineage_v1_lineage_node_lifecycle_service_pb2.ExpireLineageNodeRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_lineage_node_lifecycle_service_pb2.ExpireLineageNodeResponse:
        """Expires a lineage node."""
        return await self.handle_expire_lineage_node(request)

    @rpc_errors
    @retry_transient
    async def GetLineageNodeLifecycle(
        self, request: lineage_v1_lineage_node_lifecycle_service_pb2.GetLineageNodeLifecycleRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_lineage_node_lifecycle_service_pb2.GetLineageNodeLifecycleResponse:
        """Returns a lineage node."""
        return await self.handle_get_lineage_node_lifecycle(request)

    @rpc_errors
    async def ReinstateLineageNode(
        self, request: lineage_v1_lineage_node_lifecycle_service_pb2.ReinstateLineageNodeRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_lineage_node_lifecycle_service_pb2.ReinstateLineageNodeResponse:
        """Reinstates a lineage node."""
        return await self.handle_reinstate_lineage_node(request)

    @rpc_errors
    async def RenewLineageNode(
        self, request: lineage_v1_lineage_node_lifecycle_service_pb2.RenewLineageNodeRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_lineage_node_lifecycle_service_pb2.RenewLineageNodeResponse:
        """Renews a lineage node."""
        return await self.handle_renew_lineage_node(request)

    @rpc_errors
    async def SuspendLineageNode(
        self, request: lineage_v1_lineage_node_lifecycle_service_pb2.SuspendLineageNodeRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_lineage_node_lifecycle_service_pb2.SuspendLineageNodeResponse:
        """Suspends a lineage node."""
        return await self.handle_suspend_lineage_node(request)

    @rpc_errors
    async def TerminateLineageNode(
        self, request: lineage_v1_lineage_node_lifecycle_service_pb2.TerminateLineageNodeRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_lineage_node_lifecycle_service_pb2.TerminateLineageNodeResponse:
        """Terminates a lineage node."""
        return await self.handle_terminate_lineage_node(request)

    async def handle_activate_lineage_node(
        self,
        request: lineage_v1_lineage_node_lifecycle_service_pb2.ActivateLineageNodeRequest
    ) -> lineage_v1_lineage_node_lifecycle_service_pb2.ActivateLineageNodeResponse:
        """Activates a lineage node."""
        deps = self.deps
        response = lineage_v1_lineage_node_lifecycle_service_pb2.ActivateLineageNodeResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ActivateLineageNode', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'ActivateLineageNode', {'reason': request.reason})
            response_0 = metrics_v1_dashboard_validation_service_pb2.ExplainDashboardDecisionResponse()
            response_1 = customers_v1_customer_query_service_pb2.BrowseCustomersResponse()
            outgoing_0 = metrics_v1_dashboard_validation_service_pb2.ExplainDashboardDecisionRequest(
                context=request.context,
                details=metrics_v1_dashboard_validation_service_pb2.ExplainDashboardDecisionRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(
                        email=request.details.new_owner.email,
                        phone=request.details.notify_contact.phone,
                        preferred_channel=request.details.notify_contact.preferred_channel
                    )
                )
            )
            response_0 = await hooks.lineage_node_lifecycle_activate_lineage_node0(
                deps.clients.metrics_dashboard_validation,
                outgoing_0,
                deps.settings.timeout
            )
            outgoing_1 = customers_v1_customer_query_service_pb2.BrowseCustomersRequest()
            outgoing_1.context.CopyFrom(request.context)
            outgoing_1.filter.region = response_0.dashboard.billing_address.region
            outgoing_1.filter.created_after.CopyFrom(response_0.dashboard.issued_at)
            outgoing_1.context.tenant_id = tenant_id.get()
            response_1 = await deps.clients.customers_customer_query.BrowseCustomers(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.dashboard.counterparty.display_name
            returned_0_0_part_1 = response.lineage_node.children.add()
            returned_0_0_part_2 = returned_0_0_part_1.children.add()
            if returned_0_0:
                returned_0_0_part_2.manager.display_name = returned_0_0
            returned_0_1 = response_0.dashboard.billing_address.lines
            returned_0_1_part_1 = response.lineage_node.children.add()
            returned_0_1_part_2 = returned_0_1_part_1.children.add()
            returned_0_1_part_2.location.lines.extend(returned_0_1)
            returned_1_0 = response_1.result.message
            if returned_1_0:
                response.outcome.message = returned_1_0
            returned_1_1 = response_1.result.correlation_id
            if returned_1_1:
                response.result.correlation_id = returned_1_1
            echoed_0 = request.lineage_node_id
            response.lineage_node.lineage_node_id = echoed_0
            echoed_1 = request.details.effective_at
            response.outcome.effective_at.CopyFrom(echoed_1)
            return response

    async def handle_expire_lineage_node(
        self,
        request: lineage_v1_lineage_node_lifecycle_service_pb2.ExpireLineageNodeRequest
    ) -> lineage_v1_lineage_node_lifecycle_service_pb2.ExpireLineageNodeResponse:
        """Expires a lineage node."""
        deps = self.deps
        response = lineage_v1_lineage_node_lifecycle_service_pb2.ExpireLineageNodeResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ExpireLineageNode', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'ExpireLineageNode', {'reason': request.reason})
            response_0 = performers_v1_performer_query_service_pb2.SuggestPerformersResponse()
            response_1 = lineage_v1_lineage_node_reporting_service_pb2.CountLineageNodeTotalsResponse()
            outgoing_0 = performers_v1_performer_query_service_pb2.SuggestPerformersRequest(
                context=request.context,
                filter=performers_v1_performer_query_service_pb2.SuggestPerformersRequest.Filter(
                    created_after=request.details.effective_at,
                    labels=dict(request.annotations),
                    owner_id=request.details.new_owner.user_id
                )
            )
            port_0: LineageNodeLifecycleExpireLineageNode0Port = LineageNodeLifecycleExpireLineageNode0Adapter(
                deps.clients.performers_performer_query,
                deps.settings.timeout
            )
            response_0 = await port_0.execute(outgoing_0)
            outgoing_1 = lineage_v1_lineage_node_reporting_service_pb2.CountLineageNodeTotalsRequest(
                context=request.context,
                filter=lineage_v1_lineage_node_reporting_service_pb2.CountLineageNodeTotalsRequest.Filter(
                    created_after=request.details.effective_at
                )
            )
            steps_1 = [
                partial(
                    deps.clients.lineage_lineage_node_reporting.CountLineageNodeTotals,
                    outgoing_1,
                    timeout=deps.settings.timeout
                )
            ]
            results_1 = await run_steps(steps_1)
            response_1 = results_1[-1]
            returned_0_0 = response_0.result.details
            response.result.details.update(returned_0_0)
            returned_1_0 = response_1.result.correlation_id
            if returned_1_0:
                response.result.correlation_id = returned_1_0
            echoed_0 = request.lineage_node_id
            response.lineage_node.lineage_node_id = echoed_0
            echoed_1 = request.details.effective_at
            response.outcome.effective_at.CopyFrom(echoed_1)
            return response

    async def handle_get_lineage_node_lifecycle(
        self,
        request: lineage_v1_lineage_node_lifecycle_service_pb2.GetLineageNodeLifecycleRequest
    ) -> lineage_v1_lineage_node_lifecycle_service_pb2.GetLineageNodeLifecycleResponse:
        """Returns a lineage node."""
        deps = self.deps
        response = lineage_v1_lineage_node_lifecycle_service_pb2.GetLineageNodeLifecycleResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('GetLineageNodeLifecycle', extra={'fields': {'domain': 'lineage'}})
            await deps.repository.audit(request.context.tenant_id, 'GetLineageNodeLifecycle', {})
            response_0 = lineage_v1_lineage_node_calculation_service_pb2.GetLineageNodeRatesResponse()
            outgoing_0 = lineage_v1_lineage_node_calculation_service_pb2.GetLineageNodeRatesRequest(
                context=request.context,
                lineage_node_id=request.lineage_node_id
            )
            response_0 = await deps.clients.lineage_lineage_node_calculation.GetLineageNodeRates(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.lineage_node.audit.created_by
            returned_0_0_part_1 = response.lineage_node.children.add()
            if returned_0_0:
                returned_0_0_part_1.audit.created_by = returned_0_0
            echoed_0 = request.lineage_node_id
            response.lineage_node.lineage_node_id = echoed_0
            return response

    async def handle_reinstate_lineage_node(
        self,
        request: lineage_v1_lineage_node_lifecycle_service_pb2.ReinstateLineageNodeRequest
    ) -> lineage_v1_lineage_node_lifecycle_service_pb2.ReinstateLineageNodeResponse:
        """Reinstates a lineage node."""
        deps = self.deps
        response = lineage_v1_lineage_node_lifecycle_service_pb2.ReinstateLineageNodeResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ReinstateLineageNode', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'ReinstateLineageNode', {'reason': request.reason})
            response_0 = labeling_v1_labeling_task_validation_service_pb2.ValidateLabelingTaskResponse()
            response_1 = lineage_v1_impact_import_service_pb2.ValidateImpactImportResponse()
            outgoing_0 = labeling_v1_labeling_task_validation_service_pb2.ValidateLabelingTaskRequest(
                context=request.context,
                details=labeling_v1_labeling_task_validation_service_pb2.ValidateLabelingTaskRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(
                        email=request.details.new_owner.email,
                        phone=request.details.notify_contact.phone
                    )
                ),
                labeling_task=labeling_v1_labeling_pb2.LabelingTask(
                    assignee=identity_v1_refs_pb2.UserRef(display_name=request.details.new_owner.display_name),
                    requester=common_v1_contact_pb2.ContactInfo(email=request.details.notify_contact.email)
                )
            )
            response_0 = cast(labeling_v1_labeling_task_validation_service_pb2.ValidateLabelingTaskResponse, await deps.bus.request(
                'acme.lineage.v1.LineageNodeLifecycleService/ReinstateLineageNode/0', outgoing_0, deps.settings.timeout,
            ))
            outgoing_1 = lineage_v1_impact_import_service_pb2.ValidateImpactImportRequest()
            outgoing_1.context.CopyFrom(request.context)
            outgoing_1.impact.requester.email = response_0.labeling_task.requester.email
            if response_0.labeling_task.WhichOneof('origin') == 'customer':
                outgoing_1.impact.customer.display_name = response_0.labeling_task.customer.display_name
            response_1 = await deps.clients.lineage_impact_import.ValidateImpactImport(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.labeling_task.requester.email
            returned_0_0_part_1 = response.lineage_node.children.add()
            if returned_0_0:
                returned_0_0_part_1.manager.email = returned_0_0
            returned_1_0 = response_1.impact.assignee.user_id
            returned_1_0_part_1 = response.lineage_node.children.add()
            if returned_1_0:
                returned_1_0_part_1.manager.user_id = returned_1_0
            returned_1_1 = response_1.impact.requester.email
            if returned_1_1:
                response.lineage_node.manager.email = returned_1_1
            echoed_0 = request.lineage_node_id
            response.lineage_node.lineage_node_id = echoed_0
            echoed_1 = request.details.effective_at
            response.outcome.effective_at.CopyFrom(echoed_1)
            return response

    async def handle_renew_lineage_node(
        self,
        request: lineage_v1_lineage_node_lifecycle_service_pb2.RenewLineageNodeRequest
    ) -> lineage_v1_lineage_node_lifecycle_service_pb2.RenewLineageNodeResponse:
        """Renews a lineage node."""
        deps = self.deps
        response = lineage_v1_lineage_node_lifecycle_service_pb2.RenewLineageNodeResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('RenewLineageNode', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'RenewLineageNode', {'reason': request.reason})
            response_0 = forms_v1_form_query_service_pb2.ExportFormsResponse()
            outgoing_0 = forms_v1_form_query_service_pb2.ExportFormsRequest(
                context=request.context,
                filter=forms_v1_form_query_service_pb2.ExportFormsRequest.Filter(owner_id=request.lineage_node_id)
            )
            async for chunk_0 in deps.clients.forms_form_query.ExportForms(outgoing_0, timeout=deps.settings.timeout):
                response_0 = chunk_0
            echoed_0 = request.lineage_node_id
            response.lineage_node.lineage_node_id = echoed_0
            echoed_1 = request.details.effective_at
            response.outcome.effective_at.CopyFrom(echoed_1)
            return response

    async def handle_suspend_lineage_node(
        self,
        request: lineage_v1_lineage_node_lifecycle_service_pb2.SuspendLineageNodeRequest
    ) -> lineage_v1_lineage_node_lifecycle_service_pb2.SuspendLineageNodeResponse:
        """Suspends a lineage node."""
        deps = self.deps
        response = lineage_v1_lineage_node_lifecycle_service_pb2.SuspendLineageNodeResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SuspendLineageNode', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'SuspendLineageNode', {'reason': request.reason})
            response_0 = lineage_v1_lineage_edge_import_service_pb2.ValidateLineageEdgeImportResponse()
            response_1 = lineage_v1_lineage_edge_import_service_pb2.ListLineageEdgeImportsResponse()
            response_2 = lineage_v1_lineage_edge_sync_service_pb2.SyncLineageEdgesResponse()
            fields_0: dict[str, Any] = {
                'context': request.context,
                'details': {'contact': {'name': request.details.notify_contact.name}}
            }
            outgoing_0 = lineage_v1_lineage_edge_import_service_pb2.ValidateLineageEdgeImportRequest(**fields_0)
            response_0 = await deps.clients.lineage_lineage_edge_import.ValidateLineageEdgeImport(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = lineage_v1_lineage_edge_import_service_pb2.ListLineageEdgeImportsRequest(
                context=request.context,
                filter=lineage_v1_lineage_edge_import_service_pb2.ListLineageEdgeImportsRequest.Filter(
                    created_after=response_0.outcome.effective_at,
                    owner_id=response_0.result.correlation_id
                )
            )
            document_1 = MessageToDict(outgoing_1, preserving_proto_field_name=True)
            outgoing_1 = ParseDict(
                document_1,
                lineage_v1_lineage_edge_import_service_pb2.ListLineageEdgeImportsRequest()
            )
            response_1 = await deps.clients.lineage_lineage_edge_import.ListLineageEdgeImports(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = lineage_v1_lineage_edge_sync_service_pb2.SyncLineageEdgesRequest(
                context=request.context,
                lineage_edge=lineage_v1_lineage_pb2.LineageEdge(
                    correlation_id=response_0.result.correlation_id,
                    subject=lineage_v1_refs_pb2.ImpactRef(
                        display_name=response_0.lineage_edge.subject.display_name,
                        impact_id=response_0.lineage_edge.subject.impact_id,
                        priority=response_0.lineage_edge.subject.priority
                    )
                )
            )
            document_2 = MessageToJson(outgoing_2, preserving_proto_field_name=True)
            outgoing_2 = Parse(document_2, lineage_v1_lineage_edge_sync_service_pb2.SyncLineageEdgesRequest())
            response_2 = await deps.clients.lineage_lineage_edge_sync.SyncLineageEdges(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.outcome.message = returned_0_0
            returned_0_1 = response_0.result.correlation_id
            if returned_0_1:
                response.result.correlation_id = returned_0_1
            returned_1_0 = response_1.result.correlation_id
            if returned_1_0:
                response.result.correlation_id = returned_1_0
            returned_1_1 = response_1.result.status
            if returned_1_1:
                response.outcome.status = returned_1_1
            returned_2_0 = response_2.outcome.status
            if returned_2_0:
                response.result.status = returned_2_0
            returned_2_1 = response_2.result.reference_ids
            response.result.reference_ids.extend(returned_2_1)
            echoed_0 = request.lineage_node_id
            response.lineage_node.lineage_node_id = echoed_0
            echoed_1 = request.details.effective_at
            response.outcome.effective_at.CopyFrom(echoed_1)
            return response

    async def handle_terminate_lineage_node(
        self,
        request: lineage_v1_lineage_node_lifecycle_service_pb2.TerminateLineageNodeRequest
    ) -> lineage_v1_lineage_node_lifecycle_service_pb2.TerminateLineageNodeResponse:
        """Terminates a lineage node."""
        deps = self.deps
        response = lineage_v1_lineage_node_lifecycle_service_pb2.TerminateLineageNodeResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('TerminateLineageNode', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'TerminateLineageNode', {'reason': request.reason})
            response_0 = recommendations_v1_recommendation_model_calculation_service_pb2.CompareRecommendationModelOptionsResponse()
            outgoing_0 = recommendations_v1_recommendation_model_calculation_service_pb2.CompareRecommendationModelOptionsRequest()
            outgoing_0.context.CopyFrom(request.context)
            outgoing_0.recommendation_model.owner.user_id = request.details.new_owner.user_id
            outgoing_0.recommendation_model.owner.display_name = request.details.new_owner.display_name
            outgoing_0.recommendation_model.owner.email = request.details.notify_contact.email
            merged_0 = recommendations_v1_recommendation_model_calculation_service_pb2.CompareRecommendationModelOptionsRequest()
            merged_0.MergeFrom(outgoing_0)
            outgoing_0.CopyFrom(merged_0)
            response_0 = await deps.clients.recommendations_recommendation_model_calculation.CompareRecommendationModelOptions(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.recommendation_model.audit.created_by
            if returned_0_0:
                response.lineage_node.audit.created_by = returned_0_0
            echoed_0 = request.lineage_node_id
            response.lineage_node.lineage_node_id = echoed_0
            echoed_1 = request.details.effective_at
            response.outcome.effective_at.CopyFrom(echoed_1)
            return response
