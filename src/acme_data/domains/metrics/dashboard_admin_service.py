"""Operator actions on dashboards that support staff run by hand."""

from __future__ import annotations

from collections.abc import AsyncIterator
import logging

import grpc

from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.metrics.v1 import dashboard_admin_service_pb2 as metrics_v1_dashboard_admin_service_pb2
from acme.metrics.v1 import dashboard_admin_service_pb2_grpc as metrics_v1_dashboard_admin_service_pb2_grpc
from acme.metrics.v1 import dashboard_export_service_pb2 as metrics_v1_dashboard_export_service_pb2

from acme_data.domains.metrics.adapters import DashboardAdminPurgeDashboard0Adapter
from acme_data.domains.metrics.adapters import DashboardAdminPurgeDashboard0Port
from acme_data.domains.metrics.dependencies import Dependencies
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_id
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class DashboardAdminServicer(metrics_v1_dashboard_admin_service_pb2_grpc.DashboardAdminServiceServicer):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    async def ArchiveDashboard(
        self, request: metrics_v1_dashboard_admin_service_pb2.ArchiveDashboardRequest, context: grpc.aio.ServicerContext,
    ) -> metrics_v1_dashboard_admin_service_pb2.ArchiveDashboardResponse:
        """Archives a dashboard."""
        return await self.handle_archive_dashboard(request)

    @rpc_errors
    @retry_transient
    async def InspectDashboard(
        self, request: metrics_v1_dashboard_admin_service_pb2.InspectDashboardRequest, context: grpc.aio.ServicerContext,
    ) -> metrics_v1_dashboard_admin_service_pb2.InspectDashboardResponse:
        """Returns a dashboard."""
        return await self.handle_inspect_dashboard(request)

    @rpc_errors
    async def LockDashboard(
        self, request: metrics_v1_dashboard_admin_service_pb2.LockDashboardRequest, context: grpc.aio.ServicerContext,
    ) -> metrics_v1_dashboard_admin_service_pb2.LockDashboardResponse:
        """Locks a dashboard."""
        return await self.handle_lock_dashboard(request)

    @rpc_errors
    async def PurgeDashboard(
        self, request: metrics_v1_dashboard_admin_service_pb2.PurgeDashboardRequest, context: grpc.aio.ServicerContext,
    ) -> metrics_v1_dashboard_admin_service_pb2.PurgeDashboardResponse:
        """Deletes a dashboard."""
        return await self.handle_purge_dashboard(request)

    @rpc_errors
    async def ReassignDashboard(
        self, request: metrics_v1_dashboard_admin_service_pb2.ReassignDashboardRequest, context: grpc.aio.ServicerContext,
    ) -> metrics_v1_dashboard_admin_service_pb2.ReassignDashboardResponse:
        """Reassigns a dashboard."""
        return await self.handle_reassign_dashboard(request)

    @rpc_errors
    async def RepairDashboard(
        self, request: metrics_v1_dashboard_admin_service_pb2.RepairDashboardRequest, context: grpc.aio.ServicerContext,
    ) -> metrics_v1_dashboard_admin_service_pb2.RepairDashboardResponse:
        """Repairs a dashboard."""
        return await self.handle_repair_dashboard(request)

    @rpc_errors
    async def RestoreDashboard(
        self, request: metrics_v1_dashboard_admin_service_pb2.RestoreDashboardRequest, context: grpc.aio.ServicerContext,
    ) -> metrics_v1_dashboard_admin_service_pb2.RestoreDashboardResponse:
        """Restores a dashboard."""
        return await self.handle_restore_dashboard(request)

    @rpc_errors
    async def TransferDashboard(
        self, request: metrics_v1_dashboard_admin_service_pb2.TransferDashboardRequest, context: grpc.aio.ServicerContext,
    ) -> metrics_v1_dashboard_admin_service_pb2.TransferDashboardResponse:
        """Transfers a dashboard."""
        return await self.handle_transfer_dashboard(request)

    @rpc_errors
    async def UnlockDashboard(
        self, request: metrics_v1_dashboard_admin_service_pb2.UnlockDashboardRequest, context: grpc.aio.ServicerContext,
    ) -> metrics_v1_dashboard_admin_service_pb2.UnlockDashboardResponse:
        """Unlocks a dashboard."""
        return await self.handle_unlock_dashboard(request)

    async def handle_archive_dashboard(
        self,
        request: metrics_v1_dashboard_admin_service_pb2.ArchiveDashboardRequest
    ) -> metrics_v1_dashboard_admin_service_pb2.ArchiveDashboardResponse:
        """Archives a dashboard."""
        deps = self.deps
        response = metrics_v1_dashboard_admin_service_pb2.ArchiveDashboardResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ArchiveDashboard', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'ArchiveDashboard', {'reason': request.reason})
            echoed_0 = request.dashboard_id
            response.dashboard.dashboard_id = echoed_0
            echoed_1 = request.details.effective_at
            response.outcome.effective_at.CopyFrom(echoed_1)
            return response

    async def handle_inspect_dashboard(
        self,
        request: metrics_v1_dashboard_admin_service_pb2.InspectDashboardRequest
    ) -> metrics_v1_dashboard_admin_service_pb2.InspectDashboardResponse:
        """Returns a dashboard."""
        deps = self.deps
        response = metrics_v1_dashboard_admin_service_pb2.InspectDashboardResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('InspectDashboard', extra={'fields': {'locale': request.context.locale}})
            await deps.repository.audit(
                request.context.tenant_id,
                'InspectDashboard',
                {'locale': request.context.locale}
            )
            echoed_0 = request.dashboard_id
            response.dashboard.dashboard_id = echoed_0
            return response

    async def handle_lock_dashboard(
        self,
        request: metrics_v1_dashboard_admin_service_pb2.LockDashboardRequest
    ) -> metrics_v1_dashboard_admin_service_pb2.LockDashboardResponse:
        """Locks a dashboard."""
        deps = self.deps
        response = metrics_v1_dashboard_admin_service_pb2.LockDashboardResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('LockDashboard', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'LockDashboard', {'reason': request.reason})
            response_0 = metrics_v1_dashboard_export_service_pb2.ShareDashboardExportResponse()
            outgoing_0 = metrics_v1_dashboard_export_service_pb2.ShareDashboardExportRequest()
            outgoing_0.context.CopyFrom(request.context)
            outgoing_0.details.recipient.phone = request.details.notify_contact.phone
            outgoing_0.details.recipient.email = request.details.notify_contact.email
            outgoing_0.context.tenant_id = tenant_id.get()
            response_0 = await deps.clients.metrics_dashboard_export.ShareDashboardExport(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.dashboard.billing_address.region
            if returned_0_0:
                response.dashboard.billing_address.region = returned_0_0
            echoed_0 = request.dashboard_id
            response.dashboard.dashboard_id = echoed_0
            echoed_1 = request.details.effective_at
            response.outcome.effective_at.CopyFrom(echoed_1)
            return response

    async def handle_purge_dashboard(
        self,
        request: metrics_v1_dashboard_admin_service_pb2.PurgeDashboardRequest
    ) -> metrics_v1_dashboard_admin_service_pb2.PurgeDashboardResponse:
        """Deletes a dashboard."""
        deps = self.deps
        response = metrics_v1_dashboard_admin_service_pb2.PurgeDashboardResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('PurgeDashboard', extra={'fields': {'dashboard_id': request.dashboard_id}})
            await deps.repository.audit(
                request.context.tenant_id,
                'PurgeDashboard',
                {'dashboard_id': request.dashboard_id}
            )
            response_0 = metrics_v1_dashboard_export_service_pb2.ShareDashboardExportResponse()
            outgoing_0 = metrics_v1_dashboard_export_service_pb2.ShareDashboardExportRequest(
                context=request.context,
                details=metrics_v1_dashboard_export_service_pb2.ShareDashboardExportRequest.Details(
                    recipient=common_v1_contact_pb2.ContactInfo(email=request.context.actor.email)
                ),
                reason=request.reason
            )
            port_0: DashboardAdminPurgeDashboard0Port = DashboardAdminPurgeDashboard0Adapter(
                deps.clients.metrics_dashboard_export,
                deps.settings.timeout
            )
            response_0 = await port_0.execute(outgoing_0)
            returned_0_0 = response_0.result.status
            if returned_0_0:
                response.result.status = returned_0_0
            return response

    async def handle_reassign_dashboard(
        self,
        request: metrics_v1_dashboard_admin_service_pb2.ReassignDashboardRequest
    ) -> metrics_v1_dashboard_admin_service_pb2.ReassignDashboardResponse:
        """Reassigns a dashboard."""
        deps = self.deps
        response = metrics_v1_dashboard_admin_service_pb2.ReassignDashboardResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ReassignDashboard', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'ReassignDashboard', {'reason': request.reason})
            echoed_0 = request.dashboard_id
            response.dashboard.dashboard_id = echoed_0
            echoed_1 = request.details.assignee.display_name
            response.dashboard.counterparty.display_name = echoed_1
            return response

    async def handle_repair_dashboard(
        self,
        request: metrics_v1_dashboard_admin_service_pb2.RepairDashboardRequest
    ) -> metrics_v1_dashboard_admin_service_pb2.RepairDashboardResponse:
        """Repairs a dashboard."""
        deps = self.deps
        response = metrics_v1_dashboard_admin_service_pb2.RepairDashboardResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('RepairDashboard', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'RepairDashboard', {'reason': request.reason})
            await deps.repository.save_dashboard(request.context.tenant_id, request.dashboard)
            echoed_0 = request.dashboard_id
            response.dashboard.dashboard_id = echoed_0
            echoed_1 = request.dashboard.status
            response.dashboard.status = echoed_1
            return response

    async def handle_restore_dashboard(
        self,
        request: metrics_v1_dashboard_admin_service_pb2.RestoreDashboardRequest
    ) -> metrics_v1_dashboard_admin_service_pb2.RestoreDashboardResponse:
        """Restores a dashboard."""
        deps = self.deps
        response = metrics_v1_dashboard_admin_service_pb2.RestoreDashboardResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('RestoreDashboard', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'RestoreDashboard', {'reason': request.reason})
            echoed_0 = request.dashboard_id
            response.dashboard.dashboard_id = echoed_0
            echoed_1 = request.details.effective_at
            response.outcome.effective_at.CopyFrom(echoed_1)
            return response

    async def handle_transfer_dashboard(
        self,
        request: metrics_v1_dashboard_admin_service_pb2.TransferDashboardRequest
    ) -> metrics_v1_dashboard_admin_service_pb2.TransferDashboardResponse:
        """Transfers a dashboard."""
        deps = self.deps
        response = metrics_v1_dashboard_admin_service_pb2.TransferDashboardResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('TransferDashboard', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'TransferDashboard', {'reason': request.reason})
            echoed_0 = request.dashboard_id
            response.dashboard.dashboard_id = echoed_0
            echoed_1 = request.details.effective_at
            response.outcome.effective_at.CopyFrom(echoed_1)
            return response

    async def handle_unlock_dashboard(
        self,
        request: metrics_v1_dashboard_admin_service_pb2.UnlockDashboardRequest
    ) -> metrics_v1_dashboard_admin_service_pb2.UnlockDashboardResponse:
        """Unlocks a dashboard."""
        deps = self.deps
        response = metrics_v1_dashboard_admin_service_pb2.UnlockDashboardResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('UnlockDashboard', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'UnlockDashboard', {'reason': request.reason})
            echoed_0 = request.dashboard_id
            response.dashboard.dashboard_id = echoed_0
            echoed_1 = request.details.effective_at
            response.outcome.effective_at.CopyFrom(echoed_1)
            return response
