"""Moves an annotation between the states of its lifecycle."""

from __future__ import annotations

from collections.abc import AsyncIterator

import grpc

from acme.labeling.v1 import annotation_lifecycle_service_pb2 as labeling_v1_annotation_lifecycle_service_pb2
from acme.labeling.v1 import annotation_lifecycle_service_pb2_grpc as labeling_v1_annotation_lifecycle_service_pb2_grpc

from acme_data.domains.labeling.annotation_lifecycle_service_operations import handle_activate_annotation
from acme_data.domains.labeling.annotation_lifecycle_service_operations import handle_expire_annotation
from acme_data.domains.labeling.annotation_lifecycle_service_operations import handle_get_annotation_lifecycle
from acme_data.domains.labeling.annotation_lifecycle_service_operations import handle_reinstate_annotation
from acme_data.domains.labeling.annotation_lifecycle_service_operations import handle_renew_annotation
from acme_data.domains.labeling.annotation_lifecycle_service_operations import handle_schedule_annotation_expiry
from acme_data.domains.labeling.annotation_lifecycle_service_operations import handle_suspend_annotation
from acme_data.domains.labeling.annotation_lifecycle_service_operations import handle_terminate_annotation
from acme_data.domains.labeling.dependencies import Dependencies
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors


class AnnotationLifecycleServicer(labeling_v1_annotation_lifecycle_service_pb2_grpc.AnnotationLifecycleServiceServicer):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    async def ActivateAnnotation(
        self, request: labeling_v1_annotation_lifecycle_service_pb2.ActivateAnnotationRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_annotation_lifecycle_service_pb2.ActivateAnnotationResponse:
        """Activates an annotation."""
        return await handle_activate_annotation(self.deps, request)

    @rpc_errors
    async def ExpireAnnotation(
        self, request: labeling_v1_annotation_lifecycle_service_pb2.ExpireAnnotationRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_annotation_lifecycle_service_pb2.ExpireAnnotationResponse:
        """Expires an annotation."""
        return await handle_expire_annotation(self.deps, request)

    @rpc_errors
    @retry_transient
    async def GetAnnotationLifecycle(
        self, request: labeling_v1_annotation_lifecycle_service_pb2.GetAnnotationLifecycleRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_annotation_lifecycle_service_pb2.GetAnnotationLifecycleResponse:
        """Returns an annotation."""
        return await handle_get_annotation_lifecycle(self.deps, request)

    @rpc_errors
    async def ReinstateAnnotation(
        self, request: labeling_v1_annotation_lifecycle_service_pb2.ReinstateAnnotationRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_annotation_lifecycle_service_pb2.ReinstateAnnotationResponse:
        """Reinstates an annotation."""
        return await handle_reinstate_annotation(self.deps, request)

    @rpc_errors
    async def RenewAnnotation(
        self, request: labeling_v1_annotation_lifecycle_service_pb2.RenewAnnotationRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_annotation_lifecycle_service_pb2.RenewAnnotationResponse:
        """Renews an annotation."""
        return await handle_renew_annotation(self.deps, request)

    @rpc_errors
    async def ScheduleAnnotationExpiry(
        self, request: labeling_v1_annotation_lifecycle_service_pb2.ScheduleAnnotationExpiryRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_annotation_lifecycle_service_pb2.ScheduleAnnotationExpiryResponse:
        """Schedules an annotation."""
        return await handle_schedule_annotation_expiry(self.deps, request)

    @rpc_errors
    async def SuspendAnnotation(
        self, request: labeling_v1_annotation_lifecycle_service_pb2.SuspendAnnotationRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_annotation_lifecycle_service_pb2.SuspendAnnotationResponse:
        """Suspends an annotation."""
        return await handle_suspend_annotation(self.deps, request)

    @rpc_errors
    async def TerminateAnnotation(
        self, request: labeling_v1_annotation_lifecycle_service_pb2.TerminateAnnotationRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_annotation_lifecycle_service_pb2.TerminateAnnotationResponse:
        """Terminates an annotation."""
        return await handle_terminate_annotation(self.deps, request)
