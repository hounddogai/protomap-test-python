"""Keeps lineage nodes in step with the systems of record in other regions."""

from __future__ import annotations

from collections.abc import AsyncIterator

import grpc

from acme.lineage.v1 import lineage_node_sync_service_pb2_grpc as lineage_v1_lineage_node_sync_service_pb2_grpc

from acme_data.domains.lineage.dependencies import Dependencies
from acme_data.domains.lineage.lineage_node_sync_service_handlers import LineageNodeSyncServicerHandlers
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors


class LineageNodeSyncServicer(
    LineageNodeSyncServicerHandlers,
    lineage_v1_lineage_node_sync_service_pb2_grpc.LineageNodeSyncServiceServicer
):
    """Keeps lineage nodes in step with the systems of record in other regions."""
