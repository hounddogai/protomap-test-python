"""Moves a feature value between the states of its lifecycle."""

from __future__ import annotations

from collections.abc import AsyncIterator

import grpc

from acme.featurestore.v1 import (
    feature_value_lifecycle_service_pb2 as featurestore_v1_feature_value_lifecycle_service_pb2,
)
from acme.featurestore.v1 import (
    feature_value_lifecycle_service_pb2_grpc as featurestore_v1_feature_value_lifecycle_service_pb2_grpc,
)

from acme_data.domains.featurestore.dependencies import Dependencies
from acme_data.domains.featurestore.feature_value_lifecycle_service_workflow import (
    FeatureValueLifecycleServicerWorkflow,
)
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors


class FeatureValueLifecycleServicer(
    featurestore_v1_feature_value_lifecycle_service_pb2_grpc.FeatureValueLifecycleServiceServicer
):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps
        self.workflow = FeatureValueLifecycleServicerWorkflow(deps)

    @rpc_errors
    async def ActivateFeatureValue(
        self, request: featurestore_v1_feature_value_lifecycle_service_pb2.ActivateFeatureValueRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_feature_value_lifecycle_service_pb2.ActivateFeatureValueResponse:
        """Activates a feature value."""
        return await self.workflow.handle_activate_feature_value(request)

    @rpc_errors
    async def ExpireFeatureValue(
        self, request: featurestore_v1_feature_value_lifecycle_service_pb2.ExpireFeatureValueRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_feature_value_lifecycle_service_pb2.ExpireFeatureValueResponse:
        """Expires a feature value."""
        return await self.workflow.handle_expire_feature_value(request)

    @rpc_errors
    @retry_transient
    async def GetFeatureValueLifecycle(
        self, request: featurestore_v1_feature_value_lifecycle_service_pb2.GetFeatureValueLifecycleRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_feature_value_lifecycle_service_pb2.GetFeatureValueLifecycleResponse:
        """Returns a feature value."""
        return await self.workflow.handle_get_feature_value_lifecycle(request)

    @rpc_errors
    async def ReinstateFeatureValue(
        self, request: featurestore_v1_feature_value_lifecycle_service_pb2.ReinstateFeatureValueRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_feature_value_lifecycle_service_pb2.ReinstateFeatureValueResponse:
        """Reinstates a feature value."""
        return await self.workflow.handle_reinstate_feature_value(request)

    @rpc_errors
    async def RenewFeatureValue(
        self, request: featurestore_v1_feature_value_lifecycle_service_pb2.RenewFeatureValueRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_feature_value_lifecycle_service_pb2.RenewFeatureValueResponse:
        """Renews a feature value."""
        return await self.workflow.handle_renew_feature_value(request)

    @rpc_errors
    async def ScheduleFeatureValueExpiry(
        self, request: featurestore_v1_feature_value_lifecycle_service_pb2.ScheduleFeatureValueExpiryRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_feature_value_lifecycle_service_pb2.ScheduleFeatureValueExpiryResponse:
        """Schedules a feature value."""
        return await self.workflow.handle_schedule_feature_value_expiry(request)

    @rpc_errors
    async def SuspendFeatureValue(
        self, request: featurestore_v1_feature_value_lifecycle_service_pb2.SuspendFeatureValueRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_feature_value_lifecycle_service_pb2.SuspendFeatureValueResponse:
        """Suspends a feature value."""
        return await self.workflow.handle_suspend_feature_value(request)

    @rpc_errors
    async def TerminateFeatureValue(
        self, request: featurestore_v1_feature_value_lifecycle_service_pb2.TerminateFeatureValueRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_feature_value_lifecycle_service_pb2.TerminateFeatureValueResponse:
        """Terminates a feature value."""
        return await self.workflow.handle_terminate_feature_value(request)
