"""Moves an impact between the states of its lifecycle."""

from __future__ import annotations

from collections.abc import AsyncIterator

import grpc

from acme.lineage.v1 import impact_lifecycle_service_pb2_grpc as lineage_v1_impact_lifecycle_service_pb2_grpc

from acme_data.domains.lineage.dependencies import Dependencies
from acme_data.domains.lineage.impact_lifecycle_service_handlers import ImpactLifecycleServicerHandlers
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors


class ImpactLifecycleServicer(
    ImpactLifecycleServicerHandlers,
    lineage_v1_impact_lifecycle_service_pb2_grpc.ImpactLifecycleServiceServicer
):
    """Moves an impact between the states of its lifecycle."""
