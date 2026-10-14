"""Checks interactions against the rules before anything acts on them."""

from __future__ import annotations

from collections.abc import AsyncIterator

import grpc

from acme.recommendations.v1 import (
    interaction_validation_service_pb2_grpc as recommendations_v1_interaction_validation_service_pb2_grpc,
)

from acme_data.domains.recommendations.dependencies import Dependencies
from acme_data.domains.recommendations.interaction_validation_service_handlers import (
    InteractionValidationServicerHandlers,
)
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors


class InteractionValidationServicer(
    InteractionValidationServicerHandlers,
    recommendations_v1_interaction_validation_service_pb2_grpc.InteractionValidationServiceServicer
):
    """Checks interactions against the rules before anything acts on them."""
