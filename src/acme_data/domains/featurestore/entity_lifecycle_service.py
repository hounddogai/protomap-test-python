"""Moves an entity between the states of its lifecycle."""

from __future__ import annotations

from collections.abc import AsyncIterator

import grpc

from acme.featurestore.v1 import entity_lifecycle_service_pb2_grpc as featurestore_v1_entity_lifecycle_service_pb2_grpc

from acme_data.domains.featurestore.dependencies import Dependencies
from acme_data.domains.featurestore.entity_lifecycle_service_handlers import EntityLifecycleServicerHandlers
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors


class EntityLifecycleServicer(
    EntityLifecycleServicerHandlers,
    featurestore_v1_entity_lifecycle_service_pb2_grpc.EntityLifecycleServiceServicer
):
    """Moves an entity between the states of its lifecycle."""
