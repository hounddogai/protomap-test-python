"""Reusable transport mixin for ImpactLifecycleService."""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import cast
import asyncio
import logging

import grpc

from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.customers.v1 import customer_calculation_service_pb2 as customers_v1_customer_calculation_service_pb2
from acme.customers.v1 import (
    customer_segment_calculation_service_pb2 as customers_v1_customer_segment_calculation_service_pb2,
)
from acme.customers.v1 import customers_pb2 as customers_v1_customers_pb2
from acme.customers.v1 import preference_calculation_service_pb2 as customers_v1_preference_calculation_service_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.lineage.v1 import impact_import_service_pb2 as lineage_v1_impact_import_service_pb2
from acme.lineage.v1 import impact_lifecycle_service_pb2 as lineage_v1_impact_lifecycle_service_pb2
from acme.lineage.v1 import impact_sync_service_pb2 as lineage_v1_impact_sync_service_pb2
from acme.lineage.v1 import lineage_edge_reporting_service_pb2 as lineage_v1_lineage_edge_reporting_service_pb2
from acme.lineage.v1 import lineage_edge_sync_service_pb2 as lineage_v1_lineage_edge_sync_service_pb2
from acme.lineage.v1 import lineage_pb2 as lineage_v1_lineage_pb2
from acme.metrics.v1 import metric_alert_validation_service_pb2 as metrics_v1_metric_alert_validation_service_pb2
from acme.pipelines.v1 import pipeline_validation_service_pb2 as pipelines_v1_pipeline_validation_service_pb2
from acme.pipelines.v1 import pipelines_pb2 as pipelines_v1_pipelines_pb2
from acme.shipping.v1 import shipment_query_service_pb2 as shipping_v1_shipment_query_service_pb2
from acme.shipping.v1 import shipment_query_service_pb2_grpc as shipping_v1_shipment_query_service_pb2_grpc
from acme.venues.v1 import venue_validation_service_pb2 as venues_v1_venue_validation_service_pb2

from acme_data.domains.lineage import hooks
from acme_data.domains.lineage.adapters import ImpactLifecycleScheduleImpactExpiry0Adapter
from acme_data.domains.lineage.adapters import ImpactLifecycleScheduleImpactExpiry0Port
from acme_data.domains.lineage.adapters import ImpactLifecycleTerminateImpact0Adapter
from acme_data.domains.lineage.dependencies import Dependencies
from acme_data.domains.lineage.models import ImpactLifecycleExpireImpact1Command
from acme_data.domains.lineage.models import to_impact_lifecycle_expire_impact1_command
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_id
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class ImpactLifecycleServicerHandlers:
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    async def ActivateImpact(
        self, request: lineage_v1_impact_lifecycle_service_pb2.ActivateImpactRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_impact_lifecycle_service_pb2.ActivateImpactResponse:
        """Activates an impact."""
        return await self.handle_activate_impact(request)

    @rpc_errors
    async def ExpireImpact(
        self, request: lineage_v1_impact_lifecycle_service_pb2.ExpireImpactRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_impact_lifecycle_service_pb2.ExpireImpactResponse:
        """Expires an impact."""
        return await self.handle_expire_impact(request)

    @rpc_errors
    @retry_transient
    async def GetImpactLifecycle(
        self, request: lineage_v1_impact_lifecycle_service_pb2.GetImpactLifecycleRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_impact_lifecycle_service_pb2.GetImpactLifecycleResponse:
        """Returns an impact."""
        return await self.handle_get_impact_lifecycle(request)

    @rpc_errors
    async def ReinstateImpact(
        self, request: lineage_v1_impact_lifecycle_service_pb2.ReinstateImpactRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_impact_lifecycle_service_pb2.ReinstateImpactResponse:
        """Reinstates an impact."""
        return await self.handle_reinstate_impact(request)

    @rpc_errors
    async def RenewImpact(
        self, request: lineage_v1_impact_lifecycle_service_pb2.RenewImpactRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_impact_lifecycle_service_pb2.RenewImpactResponse:
        """Renews an impact."""
        return await self.handle_renew_impact(request)

    @rpc_errors
    async def ScheduleImpactExpiry(
        self, request: lineage_v1_impact_lifecycle_service_pb2.ScheduleImpactExpiryRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_impact_lifecycle_service_pb2.ScheduleImpactExpiryResponse:
        """Schedules an impact."""
        return await self.handle_schedule_impact_expiry(request)

    @rpc_errors
    async def SuspendImpact(
        self, request: lineage_v1_impact_lifecycle_service_pb2.SuspendImpactRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_impact_lifecycle_service_pb2.SuspendImpactResponse:
        """Suspends an impact."""
        return await self.handle_suspend_impact(request)

    @rpc_errors
    async def TerminateImpact(
        self, request: lineage_v1_impact_lifecycle_service_pb2.TerminateImpactRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_impact_lifecycle_service_pb2.TerminateImpactResponse:
        """Terminates an impact."""
        return await self.handle_terminate_impact(request)

    async def handle_activate_impact(
        self,
        request: lineage_v1_impact_lifecycle_service_pb2.ActivateImpactRequest
    ) -> lineage_v1_impact_lifecycle_service_pb2.ActivateImpactResponse:
        """Activates an impact."""
        deps = self.deps
        response = lineage_v1_impact_lifecycle_service_pb2.ActivateImpactResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ActivateImpact', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'ActivateImpact', {'reason': request.reason})
            response_0 = pipelines_v1_pipeline_validation_service_pb2.NormalizePipelineResponse()
            response_1 = metrics_v1_metric_alert_validation_service_pb2.PreviewMetricAlertResponse()
            outgoing_0 = pipelines_v1_pipeline_validation_service_pb2.NormalizePipelineRequest(
                context=request.context,
                pipeline=pipelines_v1_pipelines_pb2.Pipeline(
                    participants=[
                        pipelines_v1_pipelines_pb2.PipelineParticipant(
                            contact=common_v1_contact_pb2.ContactInfo(
                                email=request.details.new_owner.email,
                                phone=request.details.notify_contact.phone
                            )
                        )
                    ]
                )
            )
            outgoing_1 = metrics_v1_metric_alert_validation_service_pb2.PreviewMetricAlertRequest(
                context=request.context,
                details=metrics_v1_metric_alert_validation_service_pb2.PreviewMetricAlertRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(
                        preferred_channel=request.details.notify_contact.preferred_channel
                    )
                )
            )
            response_0, response_1 = await asyncio.gather(
                deps.clients.pipelines_pipeline_validation.NormalizePipeline(outgoing_0, timeout=deps.settings.timeout),
                deps.clients.metrics_metric_alert_validation.PreviewMetricAlert(
                    outgoing_1,
                    timeout=deps.settings.timeout
                ),
            )
            returned_0_0 = response_0.pipeline.organizer.user_id
            if returned_0_0:
                response.impact.assignee.user_id = returned_0_0
            returned_1_0 = response_1.result.status
            if returned_1_0:
                response.outcome.status = returned_1_0
            returned_1_1 = response_1.outcome.next_steps
            response.outcome.next_steps.extend(returned_1_1)
            echoed_0 = request.impact_id
            response.impact.impact_id = echoed_0
            echoed_1 = request.details.effective_at
            response.outcome.effective_at.CopyFrom(echoed_1)
            return response

    async def handle_expire_impact(
        self,
        request: lineage_v1_impact_lifecycle_service_pb2.ExpireImpactRequest
    ) -> lineage_v1_impact_lifecycle_service_pb2.ExpireImpactResponse:
        """Expires an impact."""
        deps = self.deps
        response = lineage_v1_impact_lifecycle_service_pb2.ExpireImpactResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ExpireImpact', extra={'fields': {'impact_id': request.impact_id}})
            await deps.repository.audit(request.context.tenant_id, 'ExpireImpact', {'impact_id': request.impact_id})
            response_0 = shipping_v1_shipment_query_service_pb2.SuggestShipmentsResponse()
            response_1 = lineage_v1_lineage_edge_sync_service_pb2.ResolveLineageEdgeConflictResponse()
            outgoing_0 = shipping_v1_shipment_query_service_pb2.SuggestShipmentsRequest(
                context=request.context,
                filter=shipping_v1_shipment_query_service_pb2.SuggestShipmentsRequest.Filter(
                    created_after=request.details.effective_at
                )
            )
            registered_0 = cast(
                shipping_v1_shipment_query_service_pb2_grpc.ShipmentQueryServiceStub,
                deps.clients.registry['acme.shipping.v1.ShipmentQueryService']
            )
            response_0 = await registered_0.SuggestShipments(outgoing_0, timeout=deps.settings.timeout)
            command_1 = ImpactLifecycleExpireImpact1Command(
                context=request.context,
                lineage_edge_subject_display_name=request.details.new_owner.display_name
            )
            outgoing_1 = to_impact_lifecycle_expire_impact1_command(command_1)
            response_1 = await deps.clients.lineage_lineage_edge_sync.ResolveLineageEdgeConflict(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.details
            response.result.details.update(returned_0_0)
            returned_0_1 = response_0.result.status
            if returned_0_1:
                response.outcome.status = returned_0_1
            returned_1_0 = response_1.lineage_edge.subject.impact_id
            if returned_1_0:
                response.impact.impact_id = returned_1_0
            returned_1_1 = response_1.lineage_edge.subject.priority
            if returned_1_1:
                response.impact.priority = returned_1_1
            echoed_0 = request.details.effective_at
            response.outcome.effective_at.CopyFrom(echoed_0)
            echoed_1 = request.details.notify_contact.phone
            response.impact.requester.phone = echoed_1
            return response

    async def handle_get_impact_lifecycle(
        self,
        request: lineage_v1_impact_lifecycle_service_pb2.GetImpactLifecycleRequest
    ) -> lineage_v1_impact_lifecycle_service_pb2.GetImpactLifecycleResponse:
        """Returns an impact."""
        deps = self.deps
        response = lineage_v1_impact_lifecycle_service_pb2.GetImpactLifecycleResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('GetImpactLifecycle', extra={'fields': {'domain': 'lineage'}})
            await deps.repository.audit(request.context.tenant_id, 'GetImpactLifecycle', {})
            response_0 = lineage_v1_impact_sync_service_pb2.PushImpactResponse()
            outgoing_0 = lineage_v1_impact_sync_service_pb2.PushImpactRequest(
                context=request.context,
                impact=lineage_v1_lineage_pb2.Impact(impact_id=request.impact_id)
            )
            response_0 = await deps.clients.lineage_impact_sync.PushImpact(outgoing_0, timeout=deps.settings.timeout)
            returned_0_0 = response_0.impact.requester.phone
            if returned_0_0:
                response.impact.requester.phone = returned_0_0
            echoed_0 = request.impact_id
            response.impact.impact_id = echoed_0
            return response

    async def handle_reinstate_impact(
        self,
        request: lineage_v1_impact_lifecycle_service_pb2.ReinstateImpactRequest
    ) -> lineage_v1_impact_lifecycle_service_pb2.ReinstateImpactResponse:
        """Reinstates an impact."""
        deps = self.deps
        response = lineage_v1_impact_lifecycle_service_pb2.ReinstateImpactResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ReinstateImpact', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'ReinstateImpact', {'reason': request.reason})
            response_0 = lineage_v1_impact_import_service_pb2.ImportImpactsResponse()
            response_1 = customers_v1_customer_calculation_service_pb2.RecalculateCustomersResponse()
            outgoing_0 = lineage_v1_impact_import_service_pb2.ImportImpactsRequest(
                context=request.context,
                record=lineage_v1_lineage_pb2.Impact(
                    requester=common_v1_contact_pb2.ContactInfo(phone=request.details.notify_contact.phone)
                )
            )
            response_0 = await deps.clients.lineage_impact_import.ImportImpacts(
                async_messages((outgoing_0,)),
                timeout=deps.settings.timeout
            )
            outgoing_1 = customers_v1_customer_calculation_service_pb2.RecalculateCustomersRequest(
                context=request.context,
                customer=customers_v1_customers_pb2.Customer(
                    contact=common_v1_contact_pb2.ContactInfo(
                        preferred_channel=request.details.notify_contact.preferred_channel
                    ),
                    relationship_manager=identity_v1_refs_pb2.UserRef(user_id=request.details.new_owner.user_id)
                )
            )
            response_1 = await hooks.impact_lifecycle_reinstate_impact1(
                deps.clients.customers_customer_calculation,
                outgoing_1,
                deps.settings.timeout
            )
            returned_1_0 = response_1.customer.audit.etag
            if returned_1_0:
                response.impact.audit.etag = returned_1_0
            returned_1_1 = response_1.customer.relationship_manager.email
            if returned_1_1:
                response.impact.requester.email = returned_1_1
            echoed_0 = request.impact_id
            response.impact.impact_id = echoed_0
            echoed_1 = request.details.effective_at
            response.outcome.effective_at.CopyFrom(echoed_1)
            return response

    async def handle_renew_impact(
        self,
        request: lineage_v1_impact_lifecycle_service_pb2.RenewImpactRequest
    ) -> lineage_v1_impact_lifecycle_service_pb2.RenewImpactResponse:
        """Renews an impact."""
        deps = self.deps
        response = lineage_v1_impact_lifecycle_service_pb2.RenewImpactResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('RenewImpact', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'RenewImpact', {'reason': request.reason})
            response_0 = customers_v1_customer_segment_calculation_service_pb2.ExplainCustomerSegmentCalculationResponse()
            outgoing_0 = customers_v1_customer_segment_calculation_service_pb2.ExplainCustomerSegmentCalculationRequest()
            outgoing_0.context.CopyFrom(request.context)
            outgoing_0.customer_segment.owner.user_id = request.details.new_owner.user_id
            outgoing_0.customer_segment.owner.display_name = request.details.new_owner.display_name
            outgoing_0.details.contact.name.CopyFrom(request.details.notify_contact.name)
            outgoing_0.context.tenant_id = tenant_id.get()
            response_0 = await deps.clients.customers_customer_segment_calculation.ExplainCustomerSegmentCalculation(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.customer_segment.owner.user_id
            if returned_0_0:
                response.impact.assignee.user_id = returned_0_0
            returned_0_1 = response_0.result.status
            if returned_0_1:
                response.result.status = returned_0_1
            echoed_0 = request.impact_id
            response.impact.impact_id = echoed_0
            echoed_1 = request.details.effective_at
            response.outcome.effective_at.CopyFrom(echoed_1)
            return response

    async def handle_schedule_impact_expiry(
        self,
        request: lineage_v1_impact_lifecycle_service_pb2.ScheduleImpactExpiryRequest
    ) -> lineage_v1_impact_lifecycle_service_pb2.ScheduleImpactExpiryResponse:
        """Schedules an impact."""
        deps = self.deps
        response = lineage_v1_impact_lifecycle_service_pb2.ScheduleImpactExpiryResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ScheduleImpactExpiry', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'ScheduleImpactExpiry', {'reason': request.reason})
            await deps.repository.save_impact(request.context.tenant_id, request.impact)
            response_0 = customers_v1_preference_calculation_service_pb2.ComparePreferenceOptionsResponse()
            outgoing_0 = customers_v1_preference_calculation_service_pb2.ComparePreferenceOptionsRequest(
                context=request.context,
                preference=customers_v1_customers_pb2.Preference(
                    owner=identity_v1_refs_pb2.UserRef(display_name=request.impact.customer.display_name)
                )
            )
            port_0: ImpactLifecycleScheduleImpactExpiry0Port = ImpactLifecycleScheduleImpactExpiry0Adapter(
                deps.clients.customers_preference_calculation,
                deps.settings.timeout
            )
            response_0 = await port_0.execute(outgoing_0)
            returned_0_0 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_0)
            echoed_0 = request.impact_id
            response.impact.impact_id = echoed_0
            echoed_1 = request.impact.subject
            response.impact.subject = echoed_1
            return response

    async def handle_suspend_impact(
        self,
        request: lineage_v1_impact_lifecycle_service_pb2.SuspendImpactRequest
    ) -> lineage_v1_impact_lifecycle_service_pb2.SuspendImpactResponse:
        """Suspends an impact."""
        deps = self.deps
        response = lineage_v1_impact_lifecycle_service_pb2.SuspendImpactResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SuspendImpact', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'SuspendImpact', {'reason': request.reason})
            response_0 = lineage_v1_lineage_edge_reporting_service_pb2.StreamLineageEdgeMetricsResponse()
            outgoing_0 = lineage_v1_lineage_edge_reporting_service_pb2.StreamLineageEdgeMetricsRequest(
                context=request.context,
                subscriber=common_v1_contact_pb2.ContactInfo(name=request.details.notify_contact.name)
            )
            async for chunk_0 in deps.clients.lineage_lineage_edge_reporting.StreamLineageEdgeMetrics(
                outgoing_0,
                timeout=deps.settings.timeout
            ):
                response_0 = chunk_0
            echoed_0 = request.impact_id
            response.impact.impact_id = echoed_0
            echoed_1 = request.details.effective_at
            response.outcome.effective_at.CopyFrom(echoed_1)
            return response

    async def handle_terminate_impact(
        self,
        request: lineage_v1_impact_lifecycle_service_pb2.TerminateImpactRequest
    ) -> lineage_v1_impact_lifecycle_service_pb2.TerminateImpactResponse:
        """Terminates an impact."""
        deps = self.deps
        response = lineage_v1_impact_lifecycle_service_pb2.TerminateImpactResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('TerminateImpact', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'TerminateImpact', {'reason': request.reason})
            response_0 = venues_v1_venue_validation_service_pb2.NormalizeVenueResponse()
            outgoing_0 = venues_v1_venue_validation_service_pb2.NormalizeVenueRequest(
                context=request.context,
                details=venues_v1_venue_validation_service_pb2.NormalizeVenueRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(
                        email=request.details.notify_contact.email,
                        name=request.details.notify_contact.name,
                        phone=request.details.notify_contact.phone
                    )
                )
            )
            response_0 = await ImpactLifecycleTerminateImpact0Adapter(
                deps.clients.venues_venue_validation,
                deps.settings.timeout
            )(outgoing_0)
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.result.message = returned_0_0
            returned_0_1 = response_0.outcome.effective_at
            if returned_0_1.ListFields():
                response.outcome.effective_at.MergeFrom(returned_0_1)
            echoed_0 = request.impact_id
            response.impact.impact_id = echoed_0
            echoed_1 = request.details.notify_contact.preferred_channel
            response.impact.requester.preferred_channel = echoed_1
            return response
