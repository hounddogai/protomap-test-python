"""Application workflow for MetricAlert Admin."""

from __future__ import annotations

import logging

from google.protobuf.json_format import MessageToDict
from google.protobuf.json_format import MessageToJson
from google.protobuf.json_format import Parse
from google.protobuf.json_format import ParseDict

from acme.metrics.v1 import dashboard_sync_service_pb2 as metrics_v1_dashboard_sync_service_pb2
from acme.metrics.v1 import metric_alert_admin_service_pb2 as metrics_v1_metric_alert_admin_service_pb2
from acme.metrics.v1 import metrics_pb2 as metrics_v1_metrics_pb2
from acme.metrics.v1 import refs_pb2 as metrics_v1_refs_pb2

from acme_data.domains.metrics.dependencies import Dependencies
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class MetricAlertAdminServicerWorkflow:
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    async def handle_archive_metric_alert(
        self,
        request: metrics_v1_metric_alert_admin_service_pb2.ArchiveMetricAlertRequest
    ) -> metrics_v1_metric_alert_admin_service_pb2.ArchiveMetricAlertResponse:
        """Archives a metric alert."""
        deps = self.deps
        response = metrics_v1_metric_alert_admin_service_pb2.ArchiveMetricAlertResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ArchiveMetricAlert', extra={'fields': {'reason_code': request.details.reason_code}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ArchiveMetricAlert',
                {'reason_code': request.details.reason_code}
            )
            response_0 = metrics_v1_dashboard_sync_service_pb2.PushDashboardResponse()
            outgoing_0 = metrics_v1_dashboard_sync_service_pb2.PushDashboardRequest(
                annotations=dict(request.annotations),
                context=request.context,
                dashboard=metrics_v1_metrics_pb2.Dashboard(
                    counterparty=metrics_v1_refs_pb2.MetricAlertRef(
                        display_name=request.details.new_owner.display_name,
                        metric_alert_id=request.metric_alert_id
                    )
                ),
                reason=request.reason
            )
            document_0 = MessageToDict(outgoing_0, preserving_proto_field_name=True)
            outgoing_0 = ParseDict(document_0, metrics_v1_dashboard_sync_service_pb2.PushDashboardRequest())
            response_0 = await deps.clients.metrics_dashboard_sync.PushDashboard(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.status
            if returned_0_0:
                response.outcome.status = returned_0_0
            echoed_0 = request.metric_alert_id
            response.metric_alert.metric_alert_id = echoed_0
            echoed_1 = request.details.effective_at
            response.outcome.effective_at.CopyFrom(echoed_1)
            return response

    async def handle_inspect_metric_alert(
        self,
        request: metrics_v1_metric_alert_admin_service_pb2.InspectMetricAlertRequest
    ) -> metrics_v1_metric_alert_admin_service_pb2.InspectMetricAlertResponse:
        """Returns a metric alert."""
        deps = self.deps
        response = metrics_v1_metric_alert_admin_service_pb2.InspectMetricAlertResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('InspectMetricAlert', extra={'fields': {'locale': request.context.locale}})
            await deps.repository.audit(
                request.context.tenant_id,
                'InspectMetricAlert',
                {'locale': request.context.locale}
            )
            echoed_0 = request.metric_alert_id
            response.metric_alert.metric_alert_id = echoed_0
            return response

    async def handle_lock_metric_alert(
        self,
        request: metrics_v1_metric_alert_admin_service_pb2.LockMetricAlertRequest
    ) -> metrics_v1_metric_alert_admin_service_pb2.LockMetricAlertResponse:
        """Locks a metric alert."""
        deps = self.deps
        response = metrics_v1_metric_alert_admin_service_pb2.LockMetricAlertResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('LockMetricAlert', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'LockMetricAlert', {'reason': request.reason})
            echoed_0 = request.metric_alert_id
            response.metric_alert.metric_alert_id = echoed_0
            echoed_1 = request.details.effective_at
            response.outcome.effective_at.CopyFrom(echoed_1)
            return response

    async def handle_purge_metric_alert(
        self,
        request: metrics_v1_metric_alert_admin_service_pb2.PurgeMetricAlertRequest
    ) -> metrics_v1_metric_alert_admin_service_pb2.PurgeMetricAlertResponse:
        """Deletes a metric alert."""
        deps = self.deps
        response = metrics_v1_metric_alert_admin_service_pb2.PurgeMetricAlertResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('PurgeMetricAlert', extra={'fields': {'etag': request.etag}})
            await deps.repository.audit(request.context.tenant_id, 'PurgeMetricAlert', {'etag': request.etag})
            return response

    async def handle_repair_metric_alert(
        self,
        request: metrics_v1_metric_alert_admin_service_pb2.RepairMetricAlertRequest
    ) -> metrics_v1_metric_alert_admin_service_pb2.RepairMetricAlertResponse:
        """Repairs a metric alert."""
        deps = self.deps
        response = metrics_v1_metric_alert_admin_service_pb2.RepairMetricAlertResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('RepairMetricAlert', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'RepairMetricAlert', {'reason': request.reason})
            await deps.repository.save_metric_alert(request.context.tenant_id, request.metric_alert)
            echoed_0 = request.metric_alert_id
            response.metric_alert.metric_alert_id = echoed_0
            echoed_1 = request.metric_alert.effective
            response.metric_alert.effective.CopyFrom(echoed_1)
            return response

    async def handle_restore_metric_alert(
        self,
        request: metrics_v1_metric_alert_admin_service_pb2.RestoreMetricAlertRequest
    ) -> metrics_v1_metric_alert_admin_service_pb2.RestoreMetricAlertResponse:
        """Restores a metric alert."""
        deps = self.deps
        response = metrics_v1_metric_alert_admin_service_pb2.RestoreMetricAlertResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('RestoreMetricAlert', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'RestoreMetricAlert', {'reason': request.reason})
            response_0 = metrics_v1_dashboard_sync_service_pb2.SyncDashboardsResponse()
            outgoing_0 = metrics_v1_dashboard_sync_service_pb2.SyncDashboardsRequest(
                annotations=dict(request.annotations),
                context=request.context,
                dashboard=metrics_v1_metrics_pb2.Dashboard(
                    counterparty=metrics_v1_refs_pb2.MetricAlertRef(
                        display_name=request.details.new_owner.display_name,
                        metric_alert_id=request.metric_alert_id
                    )
                )
            )
            document_0 = MessageToJson(outgoing_0, preserving_proto_field_name=True)
            outgoing_0 = Parse(document_0, metrics_v1_dashboard_sync_service_pb2.SyncDashboardsRequest())
            response_0 = await deps.clients.metrics_dashboard_sync.SyncDashboards(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.dashboard.audit.updated_by
            if returned_0_0:
                response.metric_alert.audit.updated_by = returned_0_0
            returned_0_1 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_1)
            echoed_0 = request.metric_alert_id
            response.metric_alert.metric_alert_id = echoed_0
            echoed_1 = request.details.effective_at
            response.outcome.effective_at.CopyFrom(echoed_1)
            return response

    async def handle_transfer_metric_alert(
        self,
        request: metrics_v1_metric_alert_admin_service_pb2.TransferMetricAlertRequest
    ) -> metrics_v1_metric_alert_admin_service_pb2.TransferMetricAlertResponse:
        """Transfers a metric alert."""
        deps = self.deps
        response = metrics_v1_metric_alert_admin_service_pb2.TransferMetricAlertResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('TransferMetricAlert', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'TransferMetricAlert', {'reason': request.reason})
            echoed_0 = request.metric_alert_id
            response.metric_alert.metric_alert_id = echoed_0
            echoed_1 = request.details.effective_at
            response.outcome.effective_at.CopyFrom(echoed_1)
            return response

    async def handle_unlock_metric_alert(
        self,
        request: metrics_v1_metric_alert_admin_service_pb2.UnlockMetricAlertRequest
    ) -> metrics_v1_metric_alert_admin_service_pb2.UnlockMetricAlertResponse:
        """Unlocks a metric alert."""
        deps = self.deps
        response = metrics_v1_metric_alert_admin_service_pb2.UnlockMetricAlertResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('UnlockMetricAlert', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'UnlockMetricAlert', {'reason': request.reason})
            echoed_0 = request.metric_alert_id
            response.metric_alert.metric_alert_id = echoed_0
            echoed_1 = request.details.effective_at
            response.outcome.effective_at.CopyFrom(echoed_1)
            return response
