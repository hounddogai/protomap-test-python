"""Takes lineage edges in bulk from partners and legacy systems."""

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
from google.protobuf.json_format import ParseDict
import grpc

from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.customers.v1 import (
    consent_record_calculation_service_pb2 as customers_v1_consent_record_calculation_service_pb2,
)
from acme.customers.v1 import customer_query_service_pb2 as customers_v1_customer_query_service_pb2
from acme.customers.v1 import customers_pb2 as customers_v1_customers_pb2
from acme.customers.v1 import household_calculation_service_pb2 as customers_v1_household_calculation_service_pb2
from acme.customers.v1 import preference_validation_service_pb2 as customers_v1_preference_validation_service_pb2
from acme.customers.v1 import refs_pb2 as customers_v1_refs_pb2
from acme.featurestore.v1 import (
    feature_value_calculation_service_pb2 as featurestore_v1_feature_value_calculation_service_pb2,
)
from acme.featurestore.v1 import feature_view_service_pb2 as featurestore_v1_feature_view_service_pb2
from acme.featurestore.v1 import feature_view_service_pb2_grpc as featurestore_v1_feature_view_service_pb2_grpc
from acme.featurestore.v1 import featurestore_pb2 as featurestore_v1_featurestore_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.lineage.v1 import impact_calculation_service_pb2 as lineage_v1_impact_calculation_service_pb2
from acme.lineage.v1 import lineage_edge_import_service_pb2 as lineage_v1_lineage_edge_import_service_pb2
from acme.lineage.v1 import lineage_edge_import_service_pb2_grpc as lineage_v1_lineage_edge_import_service_pb2_grpc
from acme.lineage.v1 import lineage_edge_query_service_pb2 as lineage_v1_lineage_edge_query_service_pb2
from acme.lineage.v1 import lineage_edge_validation_service_pb2 as lineage_v1_lineage_edge_validation_service_pb2
from acme.lineage.v1 import lineage_node_service_pb2 as lineage_v1_lineage_node_service_pb2
from acme.lineage.v1 import lineage_pb2 as lineage_v1_lineage_pb2
from acme.lineage.v1 import refs_pb2 as lineage_v1_refs_pb2
from acme.pipelines.v1 import pipeline_run_calculation_service_pb2 as pipelines_v1_pipeline_run_calculation_service_pb2

from acme_data.domains.lineage import hooks
from acme_data.domains.lineage.adapters import LineageEdgeImportMapLineageEdgeImportColumns0Adapter
from acme_data.domains.lineage.adapters import LineageEdgeImportMapLineageEdgeImportColumns0Port
from acme_data.domains.lineage.adapters import LineageEdgeImportMapLineageEdgeImportColumns2Adapter
from acme_data.domains.lineage.dependencies import Dependencies
from acme_data.domains.lineage.models import LineageEdgeImportCancelLineageEdgeImport1Command
from acme_data.domains.lineage.models import to_lineage_edge_import_cancel_lineage_edge_import1_command
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import run_steps
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class LineageEdgeImportServicer(lineage_v1_lineage_edge_import_service_pb2_grpc.LineageEdgeImportServiceServicer):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    async def CancelLineageEdgeImport(
        self, request: lineage_v1_lineage_edge_import_service_pb2.CancelLineageEdgeImportRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_lineage_edge_import_service_pb2.CancelLineageEdgeImportResponse:
        """Cancels a lineage edge."""
        return await self.handle_cancel_lineage_edge_import(request)

    @rpc_errors
    @retry_transient
    async def GetLineageEdgeImportStatus(
        self, request: lineage_v1_lineage_edge_import_service_pb2.GetLineageEdgeImportStatusRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_lineage_edge_import_service_pb2.GetLineageEdgeImportStatusResponse:
        """Returns a lineage edge."""
        return await self.handle_get_lineage_edge_import_status(request)

    @rpc_errors
    async def ImportLineageEdges(
        self, requests: AsyncIterator[
            lineage_v1_lineage_edge_import_service_pb2.ImportLineageEdgesRequest
        ], context: grpc.aio.ServicerContext,
    ) -> lineage_v1_lineage_edge_import_service_pb2.ImportLineageEdgesResponse:
        """Takes a stream of lineage edges and answers once at the end."""
        response = lineage_v1_lineage_edge_import_service_pb2.ImportLineageEdgesResponse()
        async for request in requests:
            response.MergeFrom(await self.handle_import_lineage_edges(request))
        return response

    @rpc_errors
    @retry_transient
    async def ListLineageEdgeImports(
        self, request: lineage_v1_lineage_edge_import_service_pb2.ListLineageEdgeImportsRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_lineage_edge_import_service_pb2.ListLineageEdgeImportsResponse:
        """Lists lineage edges a page at a time."""
        return await self.handle_list_lineage_edge_imports(request)

    @rpc_errors
    async def MapLineageEdgeImportColumns(
        self, request: lineage_v1_lineage_edge_import_service_pb2.MapLineageEdgeImportColumnsRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_lineage_edge_import_service_pb2.MapLineageEdgeImportColumnsResponse:
        """Maps a lineage edge."""
        return await self.handle_map_lineage_edge_import_columns(request)

    @rpc_errors
    async def RetryLineageEdgeImport(
        self, request: lineage_v1_lineage_edge_import_service_pb2.RetryLineageEdgeImportRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_lineage_edge_import_service_pb2.RetryLineageEdgeImportResponse:
        """Retrys a lineage edge."""
        return await self.handle_retry_lineage_edge_import(request)

    @rpc_errors
    async def ValidateLineageEdgeImport(
        self, request: lineage_v1_lineage_edge_import_service_pb2.ValidateLineageEdgeImportRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_lineage_edge_import_service_pb2.ValidateLineageEdgeImportResponse:
        """Validates a lineage edge."""
        return await self.handle_validate_lineage_edge_import(request)

    async def handle_cancel_lineage_edge_import(
        self,
        request: lineage_v1_lineage_edge_import_service_pb2.CancelLineageEdgeImportRequest
    ) -> lineage_v1_lineage_edge_import_service_pb2.CancelLineageEdgeImportResponse:
        """Cancels a lineage edge."""
        deps = self.deps
        response = lineage_v1_lineage_edge_import_service_pb2.CancelLineageEdgeImportResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CancelLineageEdgeImport', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'CancelLineageEdgeImport',
                {'reason': request.reason}
            )
            response_0 = featurestore_v1_feature_view_service_pb2.CreateFeatureViewResponse()
            response_1 = lineage_v1_lineage_edge_query_service_pb2.ResolveLineageEdgesResponse()
            outgoing_0 = featurestore_v1_feature_view_service_pb2.CreateFeatureViewRequest(
                context=request.context,
                feature_view=featurestore_v1_featurestore_pb2.FeatureView(
                    owner=identity_v1_refs_pb2.UserRef(display_name=request.details.new_owner.display_name)
                )
            )
            registered_0 = cast(
                featurestore_v1_feature_view_service_pb2_grpc.FeatureViewServiceStub,
                deps.clients.registry['acme.featurestore.v1.FeatureViewService']
            )
            response_0 = await registered_0.CreateFeatureView(outgoing_0, timeout=deps.settings.timeout)
            command_1 = LineageEdgeImportCancelLineageEdgeImport1Command(context=request.context)
            outgoing_1 = to_lineage_edge_import_cancel_lineage_edge_import1_command(command_1)
            response_1 = await deps.clients.lineage_lineage_edge_query.ResolveLineageEdges(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.outcome.message = returned_0_0
            returned_1_0 = response_1.result.correlation_id
            if returned_1_0:
                response.lineage_edge.correlation_id = returned_1_0
            echoed_0 = request.lineage_edge_id
            response.lineage_edge.lineage_edge_id = echoed_0
            echoed_1 = request.details.effective_at
            response.outcome.effective_at.CopyFrom(echoed_1)
            return response

    async def handle_get_lineage_edge_import_status(
        self,
        request: lineage_v1_lineage_edge_import_service_pb2.GetLineageEdgeImportStatusRequest
    ) -> lineage_v1_lineage_edge_import_service_pb2.GetLineageEdgeImportStatusResponse:
        """Returns a lineage edge."""
        deps = self.deps
        response = lineage_v1_lineage_edge_import_service_pb2.GetLineageEdgeImportStatusResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('GetLineageEdgeImportStatus', extra={'fields': {'locale': request.context.locale}})
            await deps.repository.audit(
                request.context.tenant_id,
                'GetLineageEdgeImportStatus',
                {'locale': request.context.locale}
            )
            echoed_0 = request.lineage_edge_id
            response.lineage_edge.lineage_edge_id = echoed_0
            return response

    async def handle_import_lineage_edges(
        self,
        request: lineage_v1_lineage_edge_import_service_pb2.ImportLineageEdgesRequest
    ) -> lineage_v1_lineage_edge_import_service_pb2.ImportLineageEdgesResponse:
        """Takes a stream of lineage edges and answers once at the end."""
        deps = self.deps
        response = lineage_v1_lineage_edge_import_service_pb2.ImportLineageEdgesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ImportLineageEdges', extra={'fields': {'sequence': request.sequence}})
            await deps.repository.audit(request.context.tenant_id, 'ImportLineageEdges', {'sequence': request.sequence})
            if request.WhichOneof('chunk') == 'record':
                await deps.repository.save_lineage_edge(request.context.tenant_id, request.record)
            response_0 = customers_v1_customer_query_service_pb2.BrowseCustomersResponse()
            response_1 = lineage_v1_lineage_edge_validation_service_pb2.PreviewLineageEdgeResponse()
            response_2 = customers_v1_preference_validation_service_pb2.NormalizePreferenceResponse()
            outgoing_0 = customers_v1_customer_query_service_pb2.BrowseCustomersRequest(
                context=request.context,
                filter=customers_v1_customer_query_service_pb2.BrowseCustomersRequest.Filter(
                    created_after=request.record.occurred_at,
                    labels=dict(request.record.attributes),
                    owner_id=request.record.lineage_edge_id
                )
            )
            outgoing_1 = lineage_v1_lineage_edge_validation_service_pb2.PreviewLineageEdgeRequest(
                context=request.context,
                details=lineage_v1_lineage_edge_validation_service_pb2.PreviewLineageEdgeRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(
                        name=request.header.submitted_by.name,
                        phone=request.header.submitted_by.phone,
                        preferred_channel=request.header.submitted_by.preferred_channel
                    )
                ),
                lineage_edge=lineage_v1_lineage_pb2.LineageEdge(
                    subject=lineage_v1_refs_pb2.ImpactRef(impact_id=request.record.subject.impact_id)
                )
            )
            response_0, response_1 = await asyncio.gather(
                deps.clients.customers_customer_query.BrowseCustomers(outgoing_0, timeout=deps.settings.timeout),
                deps.clients.lineage_lineage_edge_validation.PreviewLineageEdge(
                    outgoing_1,
                    timeout=deps.settings.timeout
                ),
            )
            outgoing_2 = customers_v1_preference_validation_service_pb2.NormalizePreferenceRequest(
                context=request.context,
                details=customers_v1_preference_validation_service_pb2.NormalizePreferenceRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(
                        name=request.header.submitted_by.name,
                        preferred_channel=request.header.submitted_by.preferred_channel
                    )
                ),
                preference=customers_v1_customers_pb2.Preference(
                    owner=identity_v1_refs_pb2.UserRef(display_name=response_1.lineage_edge.subject.display_name)
                )
            )
            response_2 = await hooks.lineage_edge_import_import_lineage_edges2(
                deps.clients.customers_preference_validation,
                outgoing_2,
                deps.settings.timeout
            )
            returned_0_0 = response_0.result.correlation_id
            if returned_0_0:
                response.result.correlation_id = returned_0_0
            returned_0_1 = response_0.result.message
            if returned_0_1:
                response.result.message = returned_0_1
            returned_1_0 = response_1.result.correlation_id
            if returned_1_0:
                response.result.correlation_id = returned_1_0
            returned_2_0 = response_2.outcome.status
            if returned_2_0:
                response.result.status = returned_2_0
            return response

    async def handle_list_lineage_edge_imports(
        self,
        request: lineage_v1_lineage_edge_import_service_pb2.ListLineageEdgeImportsRequest
    ) -> lineage_v1_lineage_edge_import_service_pb2.ListLineageEdgeImportsResponse:
        """Lists lineage edges a page at a time."""
        deps = self.deps
        response = lineage_v1_lineage_edge_import_service_pb2.ListLineageEdgeImportsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ListLineageEdgeImports', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ListLineageEdgeImports',
                {'order_by': request.order_by}
            )
            response_0 = featurestore_v1_feature_view_service_pb2.ListFeatureViewsResponse()
            outgoing_0 = featurestore_v1_feature_view_service_pb2.ListFeatureViewsRequest(
                context=request.context,
                filter=featurestore_v1_feature_view_service_pb2.ListFeatureViewsRequest.Filter(
                    labels=dict(request.filter.labels)
                )
            )
            response_0 = await deps.clients.featurestore_feature_view.ListFeatureViews(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.result.message = returned_0_0
            returned_0_1 = response_0.result.status
            if returned_0_1:
                response.result.status = returned_0_1
            return response

    async def handle_map_lineage_edge_import_columns(
        self,
        request: lineage_v1_lineage_edge_import_service_pb2.MapLineageEdgeImportColumnsRequest
    ) -> lineage_v1_lineage_edge_import_service_pb2.MapLineageEdgeImportColumnsResponse:
        """Maps a lineage edge."""
        deps = self.deps
        response = lineage_v1_lineage_edge_import_service_pb2.MapLineageEdgeImportColumnsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('MapLineageEdgeImportColumns', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'MapLineageEdgeImportColumns',
                {'reason': request.reason}
            )
            await deps.repository.save_lineage_edge(request.context.tenant_id, request.lineage_edge)
            response_0 = lineage_v1_impact_calculation_service_pb2.SimulateImpactResponse()
            response_1 = featurestore_v1_feature_view_service_pb2.UpdateFeatureViewResponse()
            response_2 = customers_v1_consent_record_calculation_service_pb2.CompareConsentRecordOptionsResponse()
            outgoing_0 = lineage_v1_impact_calculation_service_pb2.SimulateImpactRequest(
                context=request.context,
                impact=lineage_v1_lineage_pb2.Impact(
                    assignee=identity_v1_refs_pb2.UserRef(email=request.details.contact.email),
                    customer=customers_v1_refs_pb2.CustomerRef(display_name=request.lineage_edge.subject.display_name),
                    requester=common_v1_contact_pb2.ContactInfo(
                        name=request.details.contact.name,
                        phone=request.details.contact.phone
                    )
                )
            )
            port_0: LineageEdgeImportMapLineageEdgeImportColumns0Port = LineageEdgeImportMapLineageEdgeImportColumns0Adapter(
                deps.clients.lineage_impact_calculation,
                deps.settings.timeout
            )
            response_0 = await port_0.execute(outgoing_0)
            outgoing_1 = featurestore_v1_feature_view_service_pb2.UpdateFeatureViewRequest(
                context=request.context,
                feature_view=featurestore_v1_featurestore_pb2.FeatureView(
                    owner=identity_v1_refs_pb2.UserRef(
                        display_name=response_0.impact.assignee.display_name,
                        email=response_0.impact.requester.email
                    )
                )
            )
            steps_1 = [
                partial(
                    deps.clients.featurestore_feature_view.UpdateFeatureView,
                    outgoing_1,
                    timeout=deps.settings.timeout
                )
            ]
            results_1 = await run_steps(steps_1)
            response_1 = results_1[-1]
            outgoing_2 = customers_v1_consent_record_calculation_service_pb2.CompareConsentRecordOptionsRequest(
                consent_record=customers_v1_customers_pb2.ConsentRecord(
                    subject=customers_v1_refs_pb2.HouseholdRef(display_name=response_0.impact.assignee.display_name)
                ),
                context=request.context
            )
            response_2 = await LineageEdgeImportMapLineageEdgeImportColumns2Adapter(
                deps.clients.customers_consent_record_calculation,
                deps.settings.timeout
            )(outgoing_2)
            returned_0_0 = response_0.result.status
            if returned_0_0:
                response.result.status = returned_0_0
            returned_0_1 = response_0.result.details
            response.result.details.update(returned_0_1)
            returned_1_0 = response_1.result.reference_ids
            response.result.reference_ids.extend(returned_1_0)
            returned_1_1 = response_1.result.status
            if returned_1_1:
                response.result.status = returned_1_1
            returned_2_0 = response_2.result.message
            if returned_2_0:
                response.outcome.message = returned_2_0
            echoed_0 = request.lineage_edge_id
            response.lineage_edge.lineage_edge_id = echoed_0
            echoed_1 = request.lineage_edge.correlation_id
            response.result.correlation_id = echoed_1
            return response

    async def handle_retry_lineage_edge_import(
        self,
        request: lineage_v1_lineage_edge_import_service_pb2.RetryLineageEdgeImportRequest
    ) -> lineage_v1_lineage_edge_import_service_pb2.RetryLineageEdgeImportResponse:
        """Retrys a lineage edge."""
        deps = self.deps
        response = lineage_v1_lineage_edge_import_service_pb2.RetryLineageEdgeImportResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('RetryLineageEdgeImport', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'RetryLineageEdgeImport', {'reason': request.reason})
            await deps.repository.save_lineage_edge(request.context.tenant_id, request.lineage_edge)
            response_0 = featurestore_v1_feature_value_calculation_service_pb2.RecalculateFeatureValuesResponse()
            response_1 = lineage_v1_lineage_node_service_pb2.WatchLineageNodesResponse()
            response_2 = customers_v1_household_calculation_service_pb2.CalculateHouseholdResponse()
            response_3 = pipelines_v1_pipeline_run_calculation_service_pb2.ComparePipelineRunOptionsResponse()
            outgoing_0 = featurestore_v1_feature_value_calculation_service_pb2.RecalculateFeatureValuesRequest(
                context=request.context,
                feature_value=featurestore_v1_featurestore_pb2.FeatureValue(
                    attributes=dict(request.lineage_edge.attributes),
                    occurred_at=request.lineage_edge.occurred_at
                )
            )
            response_0 = cast(featurestore_v1_feature_value_calculation_service_pb2.RecalculateFeatureValuesResponse, await deps.bus.request(
                'acme.lineage.v1.LineageEdgeImportService/RetryLineageEdgeImport/0', outgoing_0, deps.settings.timeout,
            ))
            outgoing_1 = lineage_v1_lineage_node_service_pb2.WatchLineageNodesRequest(
                context=request.context,
                subscriber=common_v1_contact_pb2.ContactInfo(preferred_channel=request.details.notify.preferred_channel)
            )
            async for chunk_1 in deps.clients.lineage_lineage_node.WatchLineageNodes(
                outgoing_1,
                timeout=deps.settings.timeout
            ):
                response_1 = chunk_1
            callbacks_2: list[
                Callable[[], Awaitable[customers_v1_household_calculation_service_pb2.CalculateHouseholdResponse]]
            ] = []
            for item_2 in request.lineage_edge.measurements:
                outgoing_2 = customers_v1_household_calculation_service_pb2.CalculateHouseholdRequest(
                    context=request.context,
                    household=customers_v1_customers_pb2.Household(
                        children=[
                            customers_v1_customers_pb2.Household(
                                children=[
                                    customers_v1_customers_pb2.Household(
                                        audit=common_v1_audit_pb2.AuditInfo(created_at=item_2.observed_at),
                                        manager=identity_v1_refs_pb2.UserRef(email=request.details.notify.email)
                                    )
                                ]
                            )
                        ]
                    )
                )
                async def send_2(
                    payload: customers_v1_household_calculation_service_pb2.CalculateHouseholdRequest = outgoing_2
                ) -> customers_v1_household_calculation_service_pb2.CalculateHouseholdResponse:
                    return await deps.clients.customers_household_calculation.CalculateHousehold(
                        payload,
                        timeout=deps.settings.timeout
                    )
                callbacks_2.append(send_2)
            for callback_2 in callbacks_2:
                response_2 = await callback_2()
            fields_3: dict[str, Any] = {
                'context': request.context,
                'details': {'destination': {'postal_code': response_2.household.location.postal_code}},
                'pipeline_run': {
                    'customer': {'display_name': request.lineage_edge.subject.display_name},
                    'requester': {'email': request.details.notify.email}
                }
            }
            outgoing_3 = pipelines_v1_pipeline_run_calculation_service_pb2.ComparePipelineRunOptionsRequest(**fields_3)
            response_3 = await deps.clients.pipelines_pipeline_run_calculation.ComparePipelineRunOptions(
                outgoing_3,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_0)
            returned_3_0 = response_3.pipeline_run.customer.display_name
            if returned_3_0:
                response.lineage_edge.subject.display_name = returned_3_0
            echoed_0 = request.lineage_edge_id
            response.lineage_edge.lineage_edge_id = echoed_0
            echoed_1 = request.lineage_edge.correlation_id
            response.lineage_edge.correlation_id = echoed_1
            return response

    async def handle_validate_lineage_edge_import(
        self,
        request: lineage_v1_lineage_edge_import_service_pb2.ValidateLineageEdgeImportRequest
    ) -> lineage_v1_lineage_edge_import_service_pb2.ValidateLineageEdgeImportResponse:
        """Validates a lineage edge."""
        deps = self.deps
        response = lineage_v1_lineage_edge_import_service_pb2.ValidateLineageEdgeImportResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ValidateLineageEdgeImport', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ValidateLineageEdgeImport',
                {'reason': request.reason}
            )
            await deps.repository.save_lineage_edge(request.context.tenant_id, request.lineage_edge)
            response_0 = lineage_v1_impact_calculation_service_pb2.QuoteImpactResponse()
            outgoing_0 = lineage_v1_impact_calculation_service_pb2.QuoteImpactRequest(
                context=request.context,
                impact=lineage_v1_lineage_pb2.Impact(
                    customer=customers_v1_refs_pb2.CustomerRef(display_name=request.lineage_edge.subject.display_name),
                    requester=common_v1_contact_pb2.ContactInfo(email=request.details.contact.email)
                ),
                impact_id=request.lineage_edge.subject.impact_id
            )
            document_0 = MessageToDict(outgoing_0, preserving_proto_field_name=True)
            outgoing_0 = ParseDict(document_0, lineage_v1_impact_calculation_service_pb2.QuoteImpactRequest())
            response_0 = await deps.clients.lineage_impact_calculation.QuoteImpact(
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
