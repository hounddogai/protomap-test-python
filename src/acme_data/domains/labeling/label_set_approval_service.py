"""Routes label sets through approval, with escalation and delegation."""

from __future__ import annotations

from collections.abc import AsyncIterator

import grpc

from acme.labeling.v1 import label_set_approval_service_pb2 as labeling_v1_label_set_approval_service_pb2
from acme.labeling.v1 import label_set_approval_service_pb2_grpc as labeling_v1_label_set_approval_service_pb2_grpc

from acme_data.domains.labeling.dependencies import Dependencies
from acme_data.domains.labeling.label_set_approval_service_operations import handle_approve_label_set
from acme_data.domains.labeling.label_set_approval_service_operations import handle_comment_label_set_approval
from acme_data.domains.labeling.label_set_approval_service_operations import handle_delegate_label_set_approval
from acme_data.domains.labeling.label_set_approval_service_operations import handle_escalate_label_set
from acme_data.domains.labeling.label_set_approval_service_operations import handle_list_pending_label_sets
from acme_data.domains.labeling.label_set_approval_service_operations import handle_recall_label_set
from acme_data.domains.labeling.label_set_approval_service_operations import handle_reject_label_set
from acme_data.domains.labeling.label_set_approval_service_operations import handle_submit_label_set
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors


class LabelSetApprovalServicer(labeling_v1_label_set_approval_service_pb2_grpc.LabelSetApprovalServiceServicer):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    async def ApproveLabelSet(
        self, request: labeling_v1_label_set_approval_service_pb2.ApproveLabelSetRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_label_set_approval_service_pb2.ApproveLabelSetResponse:
        """Approves a label set."""
        return await handle_approve_label_set(self.deps, request)

    @rpc_errors
    async def CommentLabelSetApproval(
        self, request: labeling_v1_label_set_approval_service_pb2.CommentLabelSetApprovalRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_label_set_approval_service_pb2.CommentLabelSetApprovalResponse:
        """Comments a label set."""
        return await handle_comment_label_set_approval(self.deps, request)

    @rpc_errors
    async def DelegateLabelSetApproval(
        self, request: labeling_v1_label_set_approval_service_pb2.DelegateLabelSetApprovalRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_label_set_approval_service_pb2.DelegateLabelSetApprovalResponse:
        """Delegates a label set."""
        return await handle_delegate_label_set_approval(self.deps, request)

    @rpc_errors
    async def EscalateLabelSet(
        self, request: labeling_v1_label_set_approval_service_pb2.EscalateLabelSetRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_label_set_approval_service_pb2.EscalateLabelSetResponse:
        """Escalates a label set."""
        return await handle_escalate_label_set(self.deps, request)

    @rpc_errors
    @retry_transient
    async def ListPendingLabelSets(
        self, request: labeling_v1_label_set_approval_service_pb2.ListPendingLabelSetsRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_label_set_approval_service_pb2.ListPendingLabelSetsResponse:
        """Lists label sets a page at a time."""
        return await handle_list_pending_label_sets(self.deps, request)

    @rpc_errors
    async def RecallLabelSet(
        self, request: labeling_v1_label_set_approval_service_pb2.RecallLabelSetRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_label_set_approval_service_pb2.RecallLabelSetResponse:
        """Recalls a label set."""
        return await handle_recall_label_set(self.deps, request)

    @rpc_errors
    async def RejectLabelSet(
        self, request: labeling_v1_label_set_approval_service_pb2.RejectLabelSetRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_label_set_approval_service_pb2.RejectLabelSetResponse:
        """Rejects a label set."""
        return await handle_reject_label_set(self.deps, request)

    @rpc_errors
    async def SubmitLabelSet(
        self, request: labeling_v1_label_set_approval_service_pb2.SubmitLabelSetRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_label_set_approval_service_pb2.SubmitLabelSetResponse:
        """Submits a label set."""
        return await handle_submit_label_set(self.deps, request)
