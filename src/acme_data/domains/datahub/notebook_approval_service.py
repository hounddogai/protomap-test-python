"""Routes notebooks through approval, with escalation and delegation."""

from __future__ import annotations

from collections.abc import AsyncIterator

import grpc

from acme.datahub.v1 import notebook_approval_service_pb2 as datahub_v1_notebook_approval_service_pb2
from acme.datahub.v1 import notebook_approval_service_pb2_grpc as datahub_v1_notebook_approval_service_pb2_grpc

from acme_data.domains.datahub.dependencies import Dependencies
from acme_data.domains.datahub.notebook_approval_service_operations import handle_approve_notebook
from acme_data.domains.datahub.notebook_approval_service_operations import handle_comment_notebook_approval
from acme_data.domains.datahub.notebook_approval_service_operations import handle_delegate_notebook_approval
from acme_data.domains.datahub.notebook_approval_service_operations import handle_escalate_notebook
from acme_data.domains.datahub.notebook_approval_service_operations import handle_get_notebook_approval_status
from acme_data.domains.datahub.notebook_approval_service_operations import handle_list_pending_notebooks
from acme_data.domains.datahub.notebook_approval_service_operations import handle_recall_notebook
from acme_data.domains.datahub.notebook_approval_service_operations import handle_reject_notebook
from acme_data.domains.datahub.notebook_approval_service_operations import handle_submit_notebook
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors


class NotebookApprovalServicer(datahub_v1_notebook_approval_service_pb2_grpc.NotebookApprovalServiceServicer):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    async def ApproveNotebook(
        self, request: datahub_v1_notebook_approval_service_pb2.ApproveNotebookRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_notebook_approval_service_pb2.ApproveNotebookResponse:
        """Approves a notebook."""
        return await handle_approve_notebook(self.deps, request)

    @rpc_errors
    async def CommentNotebookApproval(
        self, request: datahub_v1_notebook_approval_service_pb2.CommentNotebookApprovalRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_notebook_approval_service_pb2.CommentNotebookApprovalResponse:
        """Comments a notebook."""
        return await handle_comment_notebook_approval(self.deps, request)

    @rpc_errors
    async def DelegateNotebookApproval(
        self, request: datahub_v1_notebook_approval_service_pb2.DelegateNotebookApprovalRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_notebook_approval_service_pb2.DelegateNotebookApprovalResponse:
        """Delegates a notebook."""
        return await handle_delegate_notebook_approval(self.deps, request)

    @rpc_errors
    async def EscalateNotebook(
        self, request: datahub_v1_notebook_approval_service_pb2.EscalateNotebookRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_notebook_approval_service_pb2.EscalateNotebookResponse:
        """Escalates a notebook."""
        return await handle_escalate_notebook(self.deps, request)

    @rpc_errors
    @retry_transient
    async def GetNotebookApprovalStatus(
        self, request: datahub_v1_notebook_approval_service_pb2.GetNotebookApprovalStatusRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_notebook_approval_service_pb2.GetNotebookApprovalStatusResponse:
        """Returns a notebook."""
        return await handle_get_notebook_approval_status(self.deps, request)

    @rpc_errors
    @retry_transient
    async def ListPendingNotebooks(
        self, request: datahub_v1_notebook_approval_service_pb2.ListPendingNotebooksRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_notebook_approval_service_pb2.ListPendingNotebooksResponse:
        """Lists notebooks a page at a time."""
        return await handle_list_pending_notebooks(self.deps, request)

    @rpc_errors
    async def RecallNotebook(
        self, request: datahub_v1_notebook_approval_service_pb2.RecallNotebookRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_notebook_approval_service_pb2.RecallNotebookResponse:
        """Recalls a notebook."""
        return await handle_recall_notebook(self.deps, request)

    @rpc_errors
    async def RejectNotebook(
        self, request: datahub_v1_notebook_approval_service_pb2.RejectNotebookRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_notebook_approval_service_pb2.RejectNotebookResponse:
        """Rejects a notebook."""
        return await handle_reject_notebook(self.deps, request)

    @rpc_errors
    async def SubmitNotebook(
        self, request: datahub_v1_notebook_approval_service_pb2.SubmitNotebookRequest, context: grpc.aio.ServicerContext,
    ) -> datahub_v1_notebook_approval_service_pb2.SubmitNotebookResponse:
        """Submits a notebook."""
        return await handle_submit_notebook(self.deps, request)
