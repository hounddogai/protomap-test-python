"""Routes lineage nodes through approval, with escalation and delegation."""

from __future__ import annotations

from collections.abc import AsyncIterator

import grpc

from acme.lineage.v1 import lineage_node_approval_service_pb2 as lineage_v1_lineage_node_approval_service_pb2
from acme.lineage.v1 import lineage_node_approval_service_pb2_grpc as lineage_v1_lineage_node_approval_service_pb2_grpc

from acme_data.domains.lineage.dependencies import Dependencies
from acme_data.domains.lineage.lineage_node_approval_service_operations import handle_approve_lineage_node
from acme_data.domains.lineage.lineage_node_approval_service_operations import handle_comment_lineage_node_approval
from acme_data.domains.lineage.lineage_node_approval_service_operations import handle_delegate_lineage_node_approval
from acme_data.domains.lineage.lineage_node_approval_service_operations import handle_escalate_lineage_node
from acme_data.domains.lineage.lineage_node_approval_service_operations import handle_get_lineage_node_approval_status
from acme_data.domains.lineage.lineage_node_approval_service_operations import handle_list_pending_lineage_nodes
from acme_data.domains.lineage.lineage_node_approval_service_operations import handle_recall_lineage_node
from acme_data.domains.lineage.lineage_node_approval_service_operations import handle_reject_lineage_node
from acme_data.domains.lineage.lineage_node_approval_service_operations import handle_submit_lineage_node
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors


class LineageNodeApprovalServicer(lineage_v1_lineage_node_approval_service_pb2_grpc.LineageNodeApprovalServiceServicer):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    async def ApproveLineageNode(
        self, request: lineage_v1_lineage_node_approval_service_pb2.ApproveLineageNodeRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_lineage_node_approval_service_pb2.ApproveLineageNodeResponse:
        """Approves a lineage node."""
        return await handle_approve_lineage_node(self.deps, request)

    @rpc_errors
    async def CommentLineageNodeApproval(
        self, request: lineage_v1_lineage_node_approval_service_pb2.CommentLineageNodeApprovalRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_lineage_node_approval_service_pb2.CommentLineageNodeApprovalResponse:
        """Comments a lineage node."""
        return await handle_comment_lineage_node_approval(self.deps, request)

    @rpc_errors
    async def DelegateLineageNodeApproval(
        self, request: lineage_v1_lineage_node_approval_service_pb2.DelegateLineageNodeApprovalRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_lineage_node_approval_service_pb2.DelegateLineageNodeApprovalResponse:
        """Delegates a lineage node."""
        return await handle_delegate_lineage_node_approval(self.deps, request)

    @rpc_errors
    async def EscalateLineageNode(
        self, request: lineage_v1_lineage_node_approval_service_pb2.EscalateLineageNodeRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_lineage_node_approval_service_pb2.EscalateLineageNodeResponse:
        """Escalates a lineage node."""
        return await handle_escalate_lineage_node(self.deps, request)

    @rpc_errors
    @retry_transient
    async def GetLineageNodeApprovalStatus(
        self, request: lineage_v1_lineage_node_approval_service_pb2.GetLineageNodeApprovalStatusRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_lineage_node_approval_service_pb2.GetLineageNodeApprovalStatusResponse:
        """Returns a lineage node."""
        return await handle_get_lineage_node_approval_status(self.deps, request)

    @rpc_errors
    @retry_transient
    async def ListPendingLineageNodes(
        self, request: lineage_v1_lineage_node_approval_service_pb2.ListPendingLineageNodesRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_lineage_node_approval_service_pb2.ListPendingLineageNodesResponse:
        """Lists lineage nodes a page at a time."""
        return await handle_list_pending_lineage_nodes(self.deps, request)

    @rpc_errors
    async def RecallLineageNode(
        self, request: lineage_v1_lineage_node_approval_service_pb2.RecallLineageNodeRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_lineage_node_approval_service_pb2.RecallLineageNodeResponse:
        """Recalls a lineage node."""
        return await handle_recall_lineage_node(self.deps, request)

    @rpc_errors
    async def RejectLineageNode(
        self, request: lineage_v1_lineage_node_approval_service_pb2.RejectLineageNodeRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_lineage_node_approval_service_pb2.RejectLineageNodeResponse:
        """Rejects a lineage node."""
        return await handle_reject_lineage_node(self.deps, request)

    @rpc_errors
    async def SubmitLineageNode(
        self, request: lineage_v1_lineage_node_approval_service_pb2.SubmitLineageNodeRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_lineage_node_approval_service_pb2.SubmitLineageNodeResponse:
        """Submits a lineage node."""
        return await handle_submit_lineage_node(self.deps, request)
