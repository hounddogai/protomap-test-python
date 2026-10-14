"""Operator actions on metric alerts that support staff run by hand."""

from __future__ import annotations

from collections.abc import AsyncIterator

import grpc

from acme.metrics.v1 import metric_alert_admin_service_pb2 as metrics_v1_metric_alert_admin_service_pb2
from acme.metrics.v1 import metric_alert_admin_service_pb2_grpc as metrics_v1_metric_alert_admin_service_pb2_grpc

from acme_data.domains.metrics.dependencies import Dependencies
from acme_data.domains.metrics.metric_alert_admin_service_workflow import MetricAlertAdminServicerWorkflow
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors


class MetricAlertAdminServicer(metrics_v1_metric_alert_admin_service_pb2_grpc.MetricAlertAdminServiceServicer):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps
        self.workflow = MetricAlertAdminServicerWorkflow(deps)

    @rpc_errors
    async def ArchiveMetricAlert(
        self, request: metrics_v1_metric_alert_admin_service_pb2.ArchiveMetricAlertRequest, context: grpc.aio.ServicerContext,
    ) -> metrics_v1_metric_alert_admin_service_pb2.ArchiveMetricAlertResponse:
        """Archives a metric alert."""
        return await self.workflow.handle_archive_metric_alert(request)

    @rpc_errors
    @retry_transient
    async def InspectMetricAlert(
        self, request: metrics_v1_metric_alert_admin_service_pb2.InspectMetricAlertRequest, context: grpc.aio.ServicerContext,
    ) -> metrics_v1_metric_alert_admin_service_pb2.InspectMetricAlertResponse:
        """Returns a metric alert."""
        return await self.workflow.handle_inspect_metric_alert(request)

    @rpc_errors
    async def LockMetricAlert(
        self, request: metrics_v1_metric_alert_admin_service_pb2.LockMetricAlertRequest, context: grpc.aio.ServicerContext,
    ) -> metrics_v1_metric_alert_admin_service_pb2.LockMetricAlertResponse:
        """Locks a metric alert."""
        return await self.workflow.handle_lock_metric_alert(request)

    @rpc_errors
    async def PurgeMetricAlert(
        self, request: metrics_v1_metric_alert_admin_service_pb2.PurgeMetricAlertRequest, context: grpc.aio.ServicerContext,
    ) -> metrics_v1_metric_alert_admin_service_pb2.PurgeMetricAlertResponse:
        """Deletes a metric alert."""
        return await self.workflow.handle_purge_metric_alert(request)

    @rpc_errors
    async def RepairMetricAlert(
        self, request: metrics_v1_metric_alert_admin_service_pb2.RepairMetricAlertRequest, context: grpc.aio.ServicerContext,
    ) -> metrics_v1_metric_alert_admin_service_pb2.RepairMetricAlertResponse:
        """Repairs a metric alert."""
        return await self.workflow.handle_repair_metric_alert(request)

    @rpc_errors
    async def RestoreMetricAlert(
        self, request: metrics_v1_metric_alert_admin_service_pb2.RestoreMetricAlertRequest, context: grpc.aio.ServicerContext,
    ) -> metrics_v1_metric_alert_admin_service_pb2.RestoreMetricAlertResponse:
        """Restores a metric alert."""
        return await self.workflow.handle_restore_metric_alert(request)

    @rpc_errors
    async def TransferMetricAlert(
        self, request: metrics_v1_metric_alert_admin_service_pb2.TransferMetricAlertRequest, context: grpc.aio.ServicerContext,
    ) -> metrics_v1_metric_alert_admin_service_pb2.TransferMetricAlertResponse:
        """Transfers a metric alert."""
        return await self.workflow.handle_transfer_metric_alert(request)

    @rpc_errors
    async def UnlockMetricAlert(
        self, request: metrics_v1_metric_alert_admin_service_pb2.UnlockMetricAlertRequest, context: grpc.aio.ServicerContext,
    ) -> metrics_v1_metric_alert_admin_service_pb2.UnlockMetricAlertResponse:
        """Unlocks a metric alert."""
        return await self.workflow.handle_unlock_metric_alert(request)
