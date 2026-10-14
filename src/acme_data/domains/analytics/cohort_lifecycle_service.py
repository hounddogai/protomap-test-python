"""Moves a cohort between the states of its lifecycle."""

from __future__ import annotations

from collections.abc import AsyncIterator

import grpc

from acme.analytics.v1 import cohort_lifecycle_service_pb2 as analytics_v1_cohort_lifecycle_service_pb2
from acme.analytics.v1 import cohort_lifecycle_service_pb2_grpc as analytics_v1_cohort_lifecycle_service_pb2_grpc

from acme_data.domains.analytics.cohort_lifecycle_service_workflow import CohortLifecycleServicerWorkflow
from acme_data.domains.analytics.dependencies import Dependencies
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors


class CohortLifecycleServicer(analytics_v1_cohort_lifecycle_service_pb2_grpc.CohortLifecycleServiceServicer):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps
        self.workflow = CohortLifecycleServicerWorkflow(deps)

    @rpc_errors
    async def ActivateCohort(
        self, request: analytics_v1_cohort_lifecycle_service_pb2.ActivateCohortRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_cohort_lifecycle_service_pb2.ActivateCohortResponse:
        """Activates a cohort."""
        return await self.workflow.handle_activate_cohort(request)

    @rpc_errors
    async def ExpireCohort(
        self, request: analytics_v1_cohort_lifecycle_service_pb2.ExpireCohortRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_cohort_lifecycle_service_pb2.ExpireCohortResponse:
        """Expires a cohort."""
        return await self.workflow.handle_expire_cohort(request)

    @rpc_errors
    @retry_transient
    async def GetCohortLifecycle(
        self, request: analytics_v1_cohort_lifecycle_service_pb2.GetCohortLifecycleRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_cohort_lifecycle_service_pb2.GetCohortLifecycleResponse:
        """Returns a cohort."""
        return await self.workflow.handle_get_cohort_lifecycle(request)

    @rpc_errors
    async def RenewCohort(
        self, request: analytics_v1_cohort_lifecycle_service_pb2.RenewCohortRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_cohort_lifecycle_service_pb2.RenewCohortResponse:
        """Renews a cohort."""
        return await self.workflow.handle_renew_cohort(request)

    @rpc_errors
    async def SuspendCohort(
        self, request: analytics_v1_cohort_lifecycle_service_pb2.SuspendCohortRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_cohort_lifecycle_service_pb2.SuspendCohortResponse:
        """Suspends a cohort."""
        return await self.workflow.handle_suspend_cohort(request)

    @rpc_errors
    async def TerminateCohort(
        self, request: analytics_v1_cohort_lifecycle_service_pb2.TerminateCohortRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_cohort_lifecycle_service_pb2.TerminateCohortResponse:
        """Terminates a cohort."""
        return await self.workflow.handle_terminate_cohort(request)
