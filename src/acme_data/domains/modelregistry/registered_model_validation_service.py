"""Checks registered models against the rules before anything acts on them."""

from __future__ import annotations

from collections.abc import AsyncIterator

import grpc

from acme.modelregistry.v1 import (
    registered_model_validation_service_pb2_grpc as modelregistry_v1_registered_model_validation_service_pb2_grpc,
)

from acme_data.domains.modelregistry.dependencies import Dependencies
from acme_data.domains.modelregistry.registered_model_validation_service_handlers import (
    RegisteredModelValidationServicerHandlers,
)
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors


class RegisteredModelValidationServicer(
    RegisteredModelValidationServicerHandlers,
    modelregistry_v1_registered_model_validation_service_pb2_grpc.RegisteredModelValidationServiceServicer
):
    """Checks registered models against the rules before anything acts on them."""
