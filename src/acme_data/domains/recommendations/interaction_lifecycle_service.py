"""Moves an interaction between the states of its lifecycle."""

from __future__ import annotations

from collections.abc import AsyncIterator

import grpc

from acme.recommendations.v1 import (
    interaction_lifecycle_service_pb2 as recommendations_v1_interaction_lifecycle_service_pb2,
)
from acme.recommendations.v1 import (
    interaction_lifecycle_service_pb2_grpc as recommendations_v1_interaction_lifecycle_service_pb2_grpc,
)

from acme_data.domains.recommendations.dependencies import Dependencies
from acme_data.domains.recommendations.interaction_lifecycle_service_operations import handle_activate_interaction
from acme_data.domains.recommendations.interaction_lifecycle_service_operations import handle_expire_interaction
from acme_data.domains.recommendations.interaction_lifecycle_service_operations import handle_get_interaction_lifecycle
from acme_data.domains.recommendations.interaction_lifecycle_service_operations import handle_reinstate_interaction
from acme_data.domains.recommendations.interaction_lifecycle_service_operations import handle_renew_interaction
from acme_data.domains.recommendations.interaction_lifecycle_service_operations import (
    handle_schedule_interaction_expiry,
)
from acme_data.domains.recommendations.interaction_lifecycle_service_operations import handle_suspend_interaction
from acme_data.domains.recommendations.interaction_lifecycle_service_operations import handle_terminate_interaction
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors


class InteractionLifecycleServicer(
    recommendations_v1_interaction_lifecycle_service_pb2_grpc.InteractionLifecycleServiceServicer
):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    async def ActivateInteraction(
        self, request: recommendations_v1_interaction_lifecycle_service_pb2.ActivateInteractionRequest, context: grpc.aio.ServicerContext,
    ) -> recommendations_v1_interaction_lifecycle_service_pb2.ActivateInteractionResponse:
        """Activates an interaction."""
        return await handle_activate_interaction(self.deps, request)

    @rpc_errors
    async def ExpireInteraction(
        self, request: recommendations_v1_interaction_lifecycle_service_pb2.ExpireInteractionRequest, context: grpc.aio.ServicerContext,
    ) -> recommendations_v1_interaction_lifecycle_service_pb2.ExpireInteractionResponse:
        """Expires an interaction."""
        return await handle_expire_interaction(self.deps, request)

    @rpc_errors
    @retry_transient
    async def GetInteractionLifecycle(
        self, request: recommendations_v1_interaction_lifecycle_service_pb2.GetInteractionLifecycleRequest, context: grpc.aio.ServicerContext,
    ) -> recommendations_v1_interaction_lifecycle_service_pb2.GetInteractionLifecycleResponse:
        """Returns an interaction."""
        return await handle_get_interaction_lifecycle(self.deps, request)

    @rpc_errors
    async def ReinstateInteraction(
        self, request: recommendations_v1_interaction_lifecycle_service_pb2.ReinstateInteractionRequest, context: grpc.aio.ServicerContext,
    ) -> recommendations_v1_interaction_lifecycle_service_pb2.ReinstateInteractionResponse:
        """Reinstates an interaction."""
        return await handle_reinstate_interaction(self.deps, request)

    @rpc_errors
    async def RenewInteraction(
        self, request: recommendations_v1_interaction_lifecycle_service_pb2.RenewInteractionRequest, context: grpc.aio.ServicerContext,
    ) -> recommendations_v1_interaction_lifecycle_service_pb2.RenewInteractionResponse:
        """Renews an interaction."""
        return await handle_renew_interaction(self.deps, request)

    @rpc_errors
    async def ScheduleInteractionExpiry(
        self, request: recommendations_v1_interaction_lifecycle_service_pb2.ScheduleInteractionExpiryRequest, context: grpc.aio.ServicerContext,
    ) -> recommendations_v1_interaction_lifecycle_service_pb2.ScheduleInteractionExpiryResponse:
        """Schedules an interaction."""
        return await handle_schedule_interaction_expiry(self.deps, request)

    @rpc_errors
    async def SuspendInteraction(
        self, request: recommendations_v1_interaction_lifecycle_service_pb2.SuspendInteractionRequest, context: grpc.aio.ServicerContext,
    ) -> recommendations_v1_interaction_lifecycle_service_pb2.SuspendInteractionResponse:
        """Suspends an interaction."""
        return await handle_suspend_interaction(self.deps, request)

    @rpc_errors
    async def TerminateInteraction(
        self, request: recommendations_v1_interaction_lifecycle_service_pb2.TerminateInteractionRequest, context: grpc.aio.ServicerContext,
    ) -> recommendations_v1_interaction_lifecycle_service_pb2.TerminateInteractionResponse:
        """Terminates an interaction."""
        return await handle_terminate_interaction(self.deps, request)
