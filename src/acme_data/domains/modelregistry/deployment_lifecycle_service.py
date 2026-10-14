"""Moves a deployment between the states of its lifecycle."""

from __future__ import annotations

from collections.abc import AsyncIterator

import grpc

from acme.modelregistry.v1 import (
    deployment_lifecycle_service_pb2_grpc as modelregistry_v1_deployment_lifecycle_service_pb2_grpc,
)

from acme_data.domains.modelregistry.dependencies import Dependencies
from acme_data.domains.modelregistry.deployment_lifecycle_service_handlers import DeploymentLifecycleServicerHandlers
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors


class DeploymentLifecycleServicer(
    DeploymentLifecycleServicerHandlers,
    modelregistry_v1_deployment_lifecycle_service_pb2_grpc.DeploymentLifecycleServiceServicer
):
    """Moves a deployment between the states of its lifecycle."""
