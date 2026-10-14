"""Moves a registered model between the states of its lifecycle."""

from __future__ import annotations

from collections.abc import AsyncIterator

import grpc

from acme.modelregistry.v1 import (
    registered_model_lifecycle_service_pb2_grpc as modelregistry_v1_registered_model_lifecycle_service_pb2_grpc,
)

from acme_data.domains.modelregistry.dependencies import Dependencies
from acme_data.domains.modelregistry.registered_model_lifecycle_service_handlers import (
    RegisteredModelLifecycleServicerHandlers,
)
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors


class RegisteredModelLifecycleServicer(
    RegisteredModelLifecycleServicerHandlers,
    modelregistry_v1_registered_model_lifecycle_service_pb2_grpc.RegisteredModelLifecycleServiceServicer
):
    """Moves a registered model between the states of its lifecycle."""
