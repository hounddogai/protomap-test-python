"""Reusable transport mixin for MetricSeriesExportService."""

from __future__ import annotations

from collections.abc import AsyncIterator
from functools import partial
import logging

import grpc

from acme.featureflags.v1 import feature_flag_service_pb2 as featureflags_v1_feature_flag_service_pb2
from acme.featureflags.v1 import featureflags_pb2 as featureflags_v1_featureflags_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.metrics.v1 import metric_series_export_service_pb2 as metrics_v1_metric_series_export_service_pb2
from acme.venues.v1 import venue_service_pb2 as venues_v1_venue_service_pb2
from acme.venues.v1 import venues_pb2 as venues_v1_venues_pb2

from acme_data.domains.metrics.adapters import MetricSeriesExportShareMetricSeriesExport0Adapter
from acme_data.domains.metrics.adapters import MetricSeriesExportShareMetricSeriesExport0Port
from acme_data.domains.metrics.dependencies import Dependencies
from acme_data.platform.rpc import messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import run_steps
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class MetricSeriesExportServicerHandlers:
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    async def CancelMetricSeriesExport(
        self, request: metrics_v1_metric_series_export_service_pb2.CancelMetricSeriesExportRequest, context: grpc.aio.ServicerContext,
    ) -> metrics_v1_metric_series_export_service_pb2.CancelMetricSeriesExportResponse:
        """Cancels a metric series."""
        return await self.handle_cancel_metric_series_export(request)

    @rpc_errors
    @retry_transient
    async def GetMetricSeriesExport(
        self, request: metrics_v1_metric_series_export_service_pb2.GetMetricSeriesExportRequest, context: grpc.aio.ServicerContext,
    ) -> metrics_v1_metric_series_export_service_pb2.GetMetricSeriesExportResponse:
        """Returns a metric series."""
        return await self.handle_get_metric_series_export(request)

    @rpc_errors
    async def RetryMetricSeriesExport(
        self, request: metrics_v1_metric_series_export_service_pb2.RetryMetricSeriesExportRequest, context: grpc.aio.ServicerContext,
    ) -> metrics_v1_metric_series_export_service_pb2.RetryMetricSeriesExportResponse:
        """Retrys a metric series."""
        return await self.handle_retry_metric_series_export(request)

    @rpc_errors
    async def ScheduleMetricSeriesExport(
        self, request: metrics_v1_metric_series_export_service_pb2.ScheduleMetricSeriesExportRequest, context: grpc.aio.ServicerContext,
    ) -> metrics_v1_metric_series_export_service_pb2.ScheduleMetricSeriesExportResponse:
        """Schedules a metric series."""
        return await self.handle_schedule_metric_series_export(request)

    @rpc_errors
    async def ShareMetricSeriesExport(
        self, request: metrics_v1_metric_series_export_service_pb2.ShareMetricSeriesExportRequest, context: grpc.aio.ServicerContext,
    ) -> metrics_v1_metric_series_export_service_pb2.ShareMetricSeriesExportResponse:
        """Shares a metric series."""
        return await self.handle_share_metric_series_export(request)

    @stream_errors
    async def StreamMetricSeriesExport(
        self, request: metrics_v1_metric_series_export_service_pb2.StreamMetricSeriesExportRequest, context: grpc.aio.ServicerContext,
    ) -> AsyncIterator[metrics_v1_metric_series_export_service_pb2.StreamMetricSeriesExportResponse]:
        """Streams every matching metric series."""
        response = await self.handle_stream_metric_series_export(request)
        for item in messages((response,)):
            yield item

    async def handle_cancel_metric_series_export(
        self,
        request: metrics_v1_metric_series_export_service_pb2.CancelMetricSeriesExportRequest
    ) -> metrics_v1_metric_series_export_service_pb2.CancelMetricSeriesExportResponse:
        """Cancels a metric series."""
        deps = self.deps
        response = metrics_v1_metric_series_export_service_pb2.CancelMetricSeriesExportResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CancelMetricSeriesExport', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'CancelMetricSeriesExport',
                {'reason': request.reason}
            )
            echoed_0 = request.metric_series_id
            response.metric_series.metric_series_id = echoed_0
            echoed_1 = request.details.effective_at
            response.outcome.effective_at.CopyFrom(echoed_1)
            return response

    async def handle_get_metric_series_export(
        self,
        request: metrics_v1_metric_series_export_service_pb2.GetMetricSeriesExportRequest
    ) -> metrics_v1_metric_series_export_service_pb2.GetMetricSeriesExportResponse:
        """Returns a metric series."""
        deps = self.deps
        response = metrics_v1_metric_series_export_service_pb2.GetMetricSeriesExportResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('GetMetricSeriesExport', extra={'fields': {'locale': request.context.locale}})
            await deps.repository.audit(
                request.context.tenant_id,
                'GetMetricSeriesExport',
                {'locale': request.context.locale}
            )
            echoed_0 = request.metric_series_id
            response.metric_series.metric_series_id = echoed_0
            return response

    async def handle_retry_metric_series_export(
        self,
        request: metrics_v1_metric_series_export_service_pb2.RetryMetricSeriesExportRequest
    ) -> metrics_v1_metric_series_export_service_pb2.RetryMetricSeriesExportResponse:
        """Retrys a metric series."""
        deps = self.deps
        response = metrics_v1_metric_series_export_service_pb2.RetryMetricSeriesExportResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('RetryMetricSeriesExport', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'RetryMetricSeriesExport',
                {'reason': request.reason}
            )
            await deps.repository.save_metric_series(request.context.tenant_id, request.metric_series)
            echoed_0 = request.metric_series_id
            response.metric_series.metric_series_id = echoed_0
            echoed_1 = request.metric_series.capacity
            response.metric_series.capacity = echoed_1
            return response

    async def handle_schedule_metric_series_export(
        self,
        request: metrics_v1_metric_series_export_service_pb2.ScheduleMetricSeriesExportRequest
    ) -> metrics_v1_metric_series_export_service_pb2.ScheduleMetricSeriesExportResponse:
        """Schedules a metric series."""
        deps = self.deps
        response = metrics_v1_metric_series_export_service_pb2.ScheduleMetricSeriesExportResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ScheduleMetricSeriesExport', extra={'fields': {'metric_series_id': request.metric_series_id}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ScheduleMetricSeriesExport',
                {'metric_series_id': request.metric_series_id}
            )
            echoed_0 = request.details.period
            response.period.CopyFrom(echoed_0)
            return response

    async def handle_share_metric_series_export(
        self,
        request: metrics_v1_metric_series_export_service_pb2.ShareMetricSeriesExportRequest
    ) -> metrics_v1_metric_series_export_service_pb2.ShareMetricSeriesExportResponse:
        """Shares a metric series."""
        deps = self.deps
        response = metrics_v1_metric_series_export_service_pb2.ShareMetricSeriesExportResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ShareMetricSeriesExport', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ShareMetricSeriesExport',
                {'reason': request.reason}
            )
            response_0 = venues_v1_venue_service_pb2.CloneVenueResponse()
            outgoing_0 = venues_v1_venue_service_pb2.CloneVenueRequest(
                context=request.context,
                venue=venues_v1_venues_pb2.Venue(
                    owner=identity_v1_refs_pb2.UserRef(email=request.details.recipient.email)
                )
            )
            port_0: MetricSeriesExportShareMetricSeriesExport0Port = MetricSeriesExportShareMetricSeriesExport0Adapter(
                deps.clients.venues_venue,
                deps.settings.timeout
            )
            response_0 = await port_0.execute(outgoing_0)
            returned_0_0 = response_0.venue.dimensions.weight
            if returned_0_0:
                response.metric_series.dimensions.weight = returned_0_0
            echoed_0 = request.metric_series_id
            response.metric_series.metric_series_id = echoed_0
            echoed_1 = request.details.recipient.email
            response.metric_series.owner.email = echoed_1
            return response

    async def handle_stream_metric_series_export(
        self,
        request: metrics_v1_metric_series_export_service_pb2.StreamMetricSeriesExportRequest
    ) -> metrics_v1_metric_series_export_service_pb2.StreamMetricSeriesExportResponse:
        """Streams every matching metric series."""
        deps = self.deps
        response = metrics_v1_metric_series_export_service_pb2.StreamMetricSeriesExportResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('StreamMetricSeriesExport', extra={'fields': {'destination_uri': request.destination_uri}})
            await deps.repository.audit(
                request.context.tenant_id,
                'StreamMetricSeriesExport',
                {'destination_uri': request.destination_uri}
            )
            response_0 = featureflags_v1_feature_flag_service_pb2.CreateFeatureFlagResponse()
            outgoing_0 = featureflags_v1_feature_flag_service_pb2.CreateFeatureFlagRequest(
                context=request.context,
                feature_flag=featureflags_v1_featureflags_pb2.FeatureFlag(
                    owner=identity_v1_refs_pb2.UserRef(
                        email=request.context.actor.email,
                        user_id=request.context.actor.user_id
                    )
                )
            )
            steps_0 = [
                partial(
                    deps.clients.featureflags_feature_flag.CreateFeatureFlag,
                    outgoing_0,
                    timeout=deps.settings.timeout
                )
            ]
            results_0 = await run_steps(steps_0)
            response_0 = results_0[-1]
            returned_0_0 = response_0.feature_flag.audit.created_by
            if returned_0_0:
                response.metric_series.audit.created_by = returned_0_0
            return response
