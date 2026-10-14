"""Keeps every version of a metric series and restores earlier ones."""

from __future__ import annotations

from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import cast
import logging

import grpc

from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.metrics.v1 import metric_series_admin_service_pb2 as metrics_v1_metric_series_admin_service_pb2
from acme.metrics.v1 import metric_series_history_service_pb2 as metrics_v1_metric_series_history_service_pb2
from acme.metrics.v1 import metric_series_history_service_pb2_grpc as metrics_v1_metric_series_history_service_pb2_grpc
from acme.metrics.v1 import metric_series_notification_service_pb2 as metrics_v1_metric_series_notification_service_pb2

from acme_data.domains.metrics.adapters import MetricSeriesHistoryCompareMetricSeriesVersions0Adapter
from acme_data.domains.metrics.dependencies import Dependencies
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


@dataclass(slots=True)
class MetricSeriesHistoryServicer(metrics_v1_metric_series_history_service_pb2_grpc.MetricSeriesHistoryServiceServicer):
    deps: Dependencies

    @rpc_errors
    async def AnnotateMetricSeriesVersion(
        self, request: metrics_v1_metric_series_history_service_pb2.AnnotateMetricSeriesVersionRequest, context: grpc.aio.ServicerContext,
    ) -> metrics_v1_metric_series_history_service_pb2.AnnotateMetricSeriesVersionResponse:
        """Annotates a metric series."""
        return await self.handle_annotate_metric_series_version(request)

    @rpc_errors
    async def CompareMetricSeriesVersions(
        self, request: metrics_v1_metric_series_history_service_pb2.CompareMetricSeriesVersionsRequest, context: grpc.aio.ServicerContext,
    ) -> metrics_v1_metric_series_history_service_pb2.CompareMetricSeriesVersionsResponse:
        """Compares a metric series."""
        return await self.handle_compare_metric_series_versions(request)

    @rpc_errors
    @retry_transient
    async def GetMetricSeriesVersion(
        self, request: metrics_v1_metric_series_history_service_pb2.GetMetricSeriesVersionRequest, context: grpc.aio.ServicerContext,
    ) -> metrics_v1_metric_series_history_service_pb2.GetMetricSeriesVersionResponse:
        """Returns a metric series."""
        return await self.handle_get_metric_series_version(request)

    @rpc_errors
    @retry_transient
    async def ListMetricSeriesVersions(
        self, request: metrics_v1_metric_series_history_service_pb2.ListMetricSeriesVersionsRequest, context: grpc.aio.ServicerContext,
    ) -> metrics_v1_metric_series_history_service_pb2.ListMetricSeriesVersionsResponse:
        """Lists metric serieses a page at a time."""
        return await self.handle_list_metric_series_versions(request)

    @rpc_errors
    async def PruneMetricSeriesVersions(
        self, request: metrics_v1_metric_series_history_service_pb2.PruneMetricSeriesVersionsRequest, context: grpc.aio.ServicerContext,
    ) -> metrics_v1_metric_series_history_service_pb2.PruneMetricSeriesVersionsResponse:
        """Deletes a metric series."""
        return await self.handle_prune_metric_series_versions(request)

    @rpc_errors
    async def RecordMetricSeriesVersion(
        self, request: metrics_v1_metric_series_history_service_pb2.RecordMetricSeriesVersionRequest, context: grpc.aio.ServicerContext,
    ) -> metrics_v1_metric_series_history_service_pb2.RecordMetricSeriesVersionResponse:
        """Records a metric series."""
        return await self.handle_record_metric_series_version(request)

    @rpc_errors
    async def RevertMetricSeries(
        self, request: metrics_v1_metric_series_history_service_pb2.RevertMetricSeriesRequest, context: grpc.aio.ServicerContext,
    ) -> metrics_v1_metric_series_history_service_pb2.RevertMetricSeriesResponse:
        """Reverts a metric series."""
        return await self.handle_revert_metric_series(request)

    async def handle_annotate_metric_series_version(
        self,
        request: metrics_v1_metric_series_history_service_pb2.AnnotateMetricSeriesVersionRequest
    ) -> metrics_v1_metric_series_history_service_pb2.AnnotateMetricSeriesVersionResponse:
        """Annotates a metric series."""
        deps = self.deps
        response = metrics_v1_metric_series_history_service_pb2.AnnotateMetricSeriesVersionResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('AnnotateMetricSeriesVersion', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'AnnotateMetricSeriesVersion',
                {'reason': request.reason}
            )
            await deps.repository.save_metric_series(request.context.tenant_id, request.metric_series)
            echoed_0 = request.metric_series_id
            response.metric_series.metric_series_id = echoed_0
            echoed_1 = request.metric_series.owner
            response.metric_series.owner.CopyFrom(echoed_1)
            return response

    async def handle_compare_metric_series_versions(
        self,
        request: metrics_v1_metric_series_history_service_pb2.CompareMetricSeriesVersionsRequest
    ) -> metrics_v1_metric_series_history_service_pb2.CompareMetricSeriesVersionsResponse:
        """Compares a metric series."""
        deps = self.deps
        response = metrics_v1_metric_series_history_service_pb2.CompareMetricSeriesVersionsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CompareMetricSeriesVersions', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'CompareMetricSeriesVersions',
                {'reason': request.reason}
            )
            await deps.repository.save_metric_series(request.context.tenant_id, request.metric_series)
            response_0 = metrics_v1_metric_series_notification_service_pb2.GetMetricSeriesPreferencesResponse()
            outgoing_0 = metrics_v1_metric_series_notification_service_pb2.GetMetricSeriesPreferencesRequest(
                context=request.context,
                metric_series_id=request.metric_series.metric_series_id
            )
            response_0 = await MetricSeriesHistoryCompareMetricSeriesVersions0Adapter(
                deps.clients.metrics_metric_series_notification,
                deps.settings.timeout
            )(outgoing_0)
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.outcome.message = returned_0_0
            echoed_0 = request.metric_series_id
            response.metric_series.metric_series_id = echoed_0
            echoed_1 = request.metric_series.specs
            response.metric_series.specs.update(echoed_1)
            return response

    async def handle_get_metric_series_version(
        self,
        request: metrics_v1_metric_series_history_service_pb2.GetMetricSeriesVersionRequest
    ) -> metrics_v1_metric_series_history_service_pb2.GetMetricSeriesVersionResponse:
        """Returns a metric series."""
        deps = self.deps
        response = metrics_v1_metric_series_history_service_pb2.GetMetricSeriesVersionResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('GetMetricSeriesVersion', extra={'fields': {'locale': request.context.locale}})
            await deps.repository.audit(
                request.context.tenant_id,
                'GetMetricSeriesVersion',
                {'locale': request.context.locale}
            )
            echoed_0 = request.metric_series_id
            response.metric_series.metric_series_id = echoed_0
            return response

    async def handle_list_metric_series_versions(
        self,
        request: metrics_v1_metric_series_history_service_pb2.ListMetricSeriesVersionsRequest
    ) -> metrics_v1_metric_series_history_service_pb2.ListMetricSeriesVersionsResponse:
        """Lists metric serieses a page at a time."""
        deps = self.deps
        response = metrics_v1_metric_series_history_service_pb2.ListMetricSeriesVersionsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ListMetricSeriesVersions', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ListMetricSeriesVersions',
                {'order_by': request.order_by}
            )
            return response

    async def handle_prune_metric_series_versions(
        self,
        request: metrics_v1_metric_series_history_service_pb2.PruneMetricSeriesVersionsRequest
    ) -> metrics_v1_metric_series_history_service_pb2.PruneMetricSeriesVersionsResponse:
        """Deletes a metric series."""
        deps = self.deps
        response = metrics_v1_metric_series_history_service_pb2.PruneMetricSeriesVersionsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('PruneMetricSeriesVersions', extra={'fields': {'etag': request.etag}})
            await deps.repository.audit(request.context.tenant_id, 'PruneMetricSeriesVersions', {'etag': request.etag})
            response_0 = metrics_v1_metric_series_admin_service_pb2.ArchiveMetricSeriesResponse()
            outgoing_0 = metrics_v1_metric_series_admin_service_pb2.ArchiveMetricSeriesRequest(
                context=request.context,
                details=metrics_v1_metric_series_admin_service_pb2.ArchiveMetricSeriesRequest.Details(
                    effective_at=request.context.deadline,
                    new_owner=identity_v1_refs_pb2.UserRef(user_id=request.context.actor.user_id),
                    notify_contact=common_v1_contact_pb2.ContactInfo(email=request.context.actor.email)
                ),
                metric_series_id=request.metric_series_id,
                reason=request.reason
            )
            response_0 = cast(metrics_v1_metric_series_admin_service_pb2.ArchiveMetricSeriesResponse, await deps.bus.request(
                'acme.metrics.v1.MetricSeriesHistoryService/PruneMetricSeriesVersions/0', outgoing_0, deps.settings.timeout,
            ))
            returned_0_0 = response_0.outcome.message
            if returned_0_0:
                response.result.message = returned_0_0
            returned_0_1 = response_0.outcome.effective_at
            if returned_0_1.ListFields():
                response.effective_at.MergeFrom(returned_0_1)
            return response

    async def handle_record_metric_series_version(
        self,
        request: metrics_v1_metric_series_history_service_pb2.RecordMetricSeriesVersionRequest
    ) -> metrics_v1_metric_series_history_service_pb2.RecordMetricSeriesVersionResponse:
        """Records a metric series."""
        deps = self.deps
        response = metrics_v1_metric_series_history_service_pb2.RecordMetricSeriesVersionResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('RecordMetricSeriesVersion', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'RecordMetricSeriesVersion',
                {'reason': request.reason}
            )
            await deps.repository.save_metric_series(request.context.tenant_id, request.metric_series)
            echoed_0 = request.metric_series_id
            response.metric_series.metric_series_id = echoed_0
            echoed_1 = request.metric_series.specs
            response.metric_series.specs.update(echoed_1)
            return response

    async def handle_revert_metric_series(
        self,
        request: metrics_v1_metric_series_history_service_pb2.RevertMetricSeriesRequest
    ) -> metrics_v1_metric_series_history_service_pb2.RevertMetricSeriesResponse:
        """Reverts a metric series."""
        deps = self.deps
        response = metrics_v1_metric_series_history_service_pb2.RevertMetricSeriesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('RevertMetricSeries', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'RevertMetricSeries', {'reason': request.reason})
            await deps.repository.save_metric_series(request.context.tenant_id, request.metric_series)
            echoed_0 = request.metric_series_id
            response.metric_series.metric_series_id = echoed_0
            echoed_1 = request.metric_series.code
            response.metric_series.code = echoed_1
            return response
