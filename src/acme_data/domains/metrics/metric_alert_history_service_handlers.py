"""Reusable transport mixin for MetricAlertHistoryService."""

from __future__ import annotations

from collections.abc import AsyncIterator
import logging

import grpc

from acme.metrics.v1 import metric_alert_history_service_pb2 as metrics_v1_metric_alert_history_service_pb2

from acme_data.domains.metrics.dependencies import Dependencies
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class MetricAlertHistoryServicerHandlers:
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    async def AnnotateMetricAlertVersion(
        self, request: metrics_v1_metric_alert_history_service_pb2.AnnotateMetricAlertVersionRequest, context: grpc.aio.ServicerContext,
    ) -> metrics_v1_metric_alert_history_service_pb2.AnnotateMetricAlertVersionResponse:
        """Annotates a metric alert."""
        return await self.handle_annotate_metric_alert_version(request)

    @rpc_errors
    async def CompareMetricAlertVersions(
        self, request: metrics_v1_metric_alert_history_service_pb2.CompareMetricAlertVersionsRequest, context: grpc.aio.ServicerContext,
    ) -> metrics_v1_metric_alert_history_service_pb2.CompareMetricAlertVersionsResponse:
        """Compares a metric alert."""
        return await self.handle_compare_metric_alert_versions(request)

    @rpc_errors
    @retry_transient
    async def GetMetricAlertVersion(
        self, request: metrics_v1_metric_alert_history_service_pb2.GetMetricAlertVersionRequest, context: grpc.aio.ServicerContext,
    ) -> metrics_v1_metric_alert_history_service_pb2.GetMetricAlertVersionResponse:
        """Returns a metric alert."""
        return await self.handle_get_metric_alert_version(request)

    @rpc_errors
    @retry_transient
    async def ListMetricAlertVersions(
        self, request: metrics_v1_metric_alert_history_service_pb2.ListMetricAlertVersionsRequest, context: grpc.aio.ServicerContext,
    ) -> metrics_v1_metric_alert_history_service_pb2.ListMetricAlertVersionsResponse:
        """Lists metric alerts a page at a time."""
        return await self.handle_list_metric_alert_versions(request)

    @rpc_errors
    async def PruneMetricAlertVersions(
        self, request: metrics_v1_metric_alert_history_service_pb2.PruneMetricAlertVersionsRequest, context: grpc.aio.ServicerContext,
    ) -> metrics_v1_metric_alert_history_service_pb2.PruneMetricAlertVersionsResponse:
        """Deletes a metric alert."""
        return await self.handle_prune_metric_alert_versions(request)

    @rpc_errors
    async def RecordMetricAlertVersion(
        self, request: metrics_v1_metric_alert_history_service_pb2.RecordMetricAlertVersionRequest, context: grpc.aio.ServicerContext,
    ) -> metrics_v1_metric_alert_history_service_pb2.RecordMetricAlertVersionResponse:
        """Records a metric alert."""
        return await self.handle_record_metric_alert_version(request)

    @rpc_errors
    async def RevertMetricAlert(
        self, request: metrics_v1_metric_alert_history_service_pb2.RevertMetricAlertRequest, context: grpc.aio.ServicerContext,
    ) -> metrics_v1_metric_alert_history_service_pb2.RevertMetricAlertResponse:
        """Reverts a metric alert."""
        return await self.handle_revert_metric_alert(request)

    async def handle_annotate_metric_alert_version(
        self,
        request: metrics_v1_metric_alert_history_service_pb2.AnnotateMetricAlertVersionRequest
    ) -> metrics_v1_metric_alert_history_service_pb2.AnnotateMetricAlertVersionResponse:
        """Annotates a metric alert."""
        deps = self.deps
        response = metrics_v1_metric_alert_history_service_pb2.AnnotateMetricAlertVersionResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('AnnotateMetricAlertVersion', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'AnnotateMetricAlertVersion',
                {'reason': request.reason}
            )
            await deps.repository.save_metric_alert(request.context.tenant_id, request.metric_alert)
            echoed_0 = request.metric_alert_id
            response.metric_alert.metric_alert_id = echoed_0
            echoed_1 = request.metric_alert.status
            response.metric_alert.status = echoed_1
            return response

    async def handle_compare_metric_alert_versions(
        self,
        request: metrics_v1_metric_alert_history_service_pb2.CompareMetricAlertVersionsRequest
    ) -> metrics_v1_metric_alert_history_service_pb2.CompareMetricAlertVersionsResponse:
        """Compares a metric alert."""
        deps = self.deps
        response = metrics_v1_metric_alert_history_service_pb2.CompareMetricAlertVersionsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CompareMetricAlertVersions', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'CompareMetricAlertVersions',
                {'reason': request.reason}
            )
            await deps.repository.save_metric_alert(request.context.tenant_id, request.metric_alert)
            echoed_0 = request.metric_alert_id
            response.metric_alert.metric_alert_id = echoed_0
            echoed_1 = request.metric_alert.status
            response.metric_alert.status = echoed_1
            return response

    async def handle_get_metric_alert_version(
        self,
        request: metrics_v1_metric_alert_history_service_pb2.GetMetricAlertVersionRequest
    ) -> metrics_v1_metric_alert_history_service_pb2.GetMetricAlertVersionResponse:
        """Returns a metric alert."""
        deps = self.deps
        response = metrics_v1_metric_alert_history_service_pb2.GetMetricAlertVersionResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('GetMetricAlertVersion', extra={'fields': {'locale': request.context.locale}})
            await deps.repository.audit(
                request.context.tenant_id,
                'GetMetricAlertVersion',
                {'locale': request.context.locale}
            )
            echoed_0 = request.metric_alert_id
            response.metric_alert.metric_alert_id = echoed_0
            return response

    async def handle_list_metric_alert_versions(
        self,
        request: metrics_v1_metric_alert_history_service_pb2.ListMetricAlertVersionsRequest
    ) -> metrics_v1_metric_alert_history_service_pb2.ListMetricAlertVersionsResponse:
        """Lists metric alerts a page at a time."""
        deps = self.deps
        response = metrics_v1_metric_alert_history_service_pb2.ListMetricAlertVersionsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ListMetricAlertVersions', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ListMetricAlertVersions',
                {'order_by': request.order_by}
            )
            return response

    async def handle_prune_metric_alert_versions(
        self,
        request: metrics_v1_metric_alert_history_service_pb2.PruneMetricAlertVersionsRequest
    ) -> metrics_v1_metric_alert_history_service_pb2.PruneMetricAlertVersionsResponse:
        """Deletes a metric alert."""
        deps = self.deps
        response = metrics_v1_metric_alert_history_service_pb2.PruneMetricAlertVersionsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('PruneMetricAlertVersions', extra={'fields': {'etag': request.etag}})
            await deps.repository.audit(request.context.tenant_id, 'PruneMetricAlertVersions', {'etag': request.etag})
            return response

    async def handle_record_metric_alert_version(
        self,
        request: metrics_v1_metric_alert_history_service_pb2.RecordMetricAlertVersionRequest
    ) -> metrics_v1_metric_alert_history_service_pb2.RecordMetricAlertVersionResponse:
        """Records a metric alert."""
        deps = self.deps
        response = metrics_v1_metric_alert_history_service_pb2.RecordMetricAlertVersionResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('RecordMetricAlertVersion', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'RecordMetricAlertVersion',
                {'reason': request.reason}
            )
            await deps.repository.save_metric_alert(request.context.tenant_id, request.metric_alert)
            echoed_0 = request.metric_alert_id
            response.metric_alert.metric_alert_id = echoed_0
            echoed_1 = request.details.version
            response.metric_alert.version = echoed_1
            return response

    async def handle_revert_metric_alert(
        self,
        request: metrics_v1_metric_alert_history_service_pb2.RevertMetricAlertRequest
    ) -> metrics_v1_metric_alert_history_service_pb2.RevertMetricAlertResponse:
        """Reverts a metric alert."""
        deps = self.deps
        response = metrics_v1_metric_alert_history_service_pb2.RevertMetricAlertResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('RevertMetricAlert', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'RevertMetricAlert', {'reason': request.reason})
            await deps.repository.save_metric_alert(request.context.tenant_id, request.metric_alert)
            echoed_0 = request.metric_alert_id
            response.metric_alert.metric_alert_id = echoed_0
            echoed_1 = request.metric_alert.effective
            response.metric_alert.effective.CopyFrom(echoed_1)
            return response
