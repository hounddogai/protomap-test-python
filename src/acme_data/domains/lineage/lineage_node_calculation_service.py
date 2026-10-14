"""Computes the figures of a lineage node, such as totals, taxes, and estimates."""

from __future__ import annotations

from collections.abc import AsyncIterator

import grpc

from acme.lineage.v1 import (
    lineage_node_calculation_service_pb2_grpc as lineage_v1_lineage_node_calculation_service_pb2_grpc,
)

from acme_data.domains.lineage.dependencies import Dependencies
from acme_data.domains.lineage.lineage_node_calculation_service_handlers import LineageNodeCalculationServicerHandlers
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors


class LineageNodeCalculationServicer(
    LineageNodeCalculationServicerHandlers,
    lineage_v1_lineage_node_calculation_service_pb2_grpc.LineageNodeCalculationServiceServicer
):
    """Computes the figures of a lineage node, such as totals, taxes, and estimates."""
