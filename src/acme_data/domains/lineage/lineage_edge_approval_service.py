"""Routes lineage edges through approval, with escalation and delegation."""

from __future__ import annotations

from collections.abc import AsyncIterator

import grpc

from acme.lineage.v1 import lineage_edge_approval_service_pb2_grpc as lineage_v1_lineage_edge_approval_service_pb2_grpc

from acme_data.domains.lineage.dependencies import Dependencies
from acme_data.domains.lineage.lineage_edge_approval_service_handlers import LineageEdgeApprovalServicerHandlers
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors


class LineageEdgeApprovalServicer(
    LineageEdgeApprovalServicerHandlers,
    lineage_v1_lineage_edge_approval_service_pb2_grpc.LineageEdgeApprovalServiceServicer
):
    """Routes lineage edges through approval, with escalation and delegation."""
