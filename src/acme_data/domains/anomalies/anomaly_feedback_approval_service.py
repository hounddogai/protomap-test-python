"""Routes anomaly feedbacks through approval, with escalation and delegation."""

from __future__ import annotations

from collections.abc import AsyncIterator

import grpc

from acme.anomalies.v1 import (
    anomaly_feedback_approval_service_pb2 as anomalies_v1_anomaly_feedback_approval_service_pb2,
)
from acme.anomalies.v1 import (
    anomaly_feedback_approval_service_pb2_grpc as anomalies_v1_anomaly_feedback_approval_service_pb2_grpc,
)

from acme_data.domains.anomalies.anomaly_feedback_approval_service_workflow import (
    AnomalyFeedbackApprovalServicerWorkflow,
)
from acme_data.domains.anomalies.dependencies import Dependencies
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors


class AnomalyFeedbackApprovalServicer(
    anomalies_v1_anomaly_feedback_approval_service_pb2_grpc.AnomalyFeedbackApprovalServiceServicer
):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps
        self.workflow = AnomalyFeedbackApprovalServicerWorkflow(deps)

    @rpc_errors
    async def ApproveAnomalyFeedback(
        self, request: anomalies_v1_anomaly_feedback_approval_service_pb2.ApproveAnomalyFeedbackRequest, context: grpc.aio.ServicerContext,
    ) -> anomalies_v1_anomaly_feedback_approval_service_pb2.ApproveAnomalyFeedbackResponse:
        """Approves an anomaly feedback."""
        return await self.workflow.handle_approve_anomaly_feedback(request)

    @rpc_errors
    async def CommentAnomalyFeedbackApproval(
        self, request: anomalies_v1_anomaly_feedback_approval_service_pb2.CommentAnomalyFeedbackApprovalRequest, context: grpc.aio.ServicerContext,
    ) -> anomalies_v1_anomaly_feedback_approval_service_pb2.CommentAnomalyFeedbackApprovalResponse:
        """Comments an anomaly feedback."""
        return await self.workflow.handle_comment_anomaly_feedback_approval(request)

    @rpc_errors
    async def DelegateAnomalyFeedbackApproval(
        self, request: anomalies_v1_anomaly_feedback_approval_service_pb2.DelegateAnomalyFeedbackApprovalRequest, context: grpc.aio.ServicerContext,
    ) -> anomalies_v1_anomaly_feedback_approval_service_pb2.DelegateAnomalyFeedbackApprovalResponse:
        """Delegates an anomaly feedback."""
        return await self.workflow.handle_delegate_anomaly_feedback_approval(request)

    @rpc_errors
    async def EscalateAnomalyFeedback(
        self, request: anomalies_v1_anomaly_feedback_approval_service_pb2.EscalateAnomalyFeedbackRequest, context: grpc.aio.ServicerContext,
    ) -> anomalies_v1_anomaly_feedback_approval_service_pb2.EscalateAnomalyFeedbackResponse:
        """Escalates an anomaly feedback."""
        return await self.workflow.handle_escalate_anomaly_feedback(request)

    @rpc_errors
    @retry_transient
    async def GetAnomalyFeedbackApprovalStatus(
        self, request: anomalies_v1_anomaly_feedback_approval_service_pb2.GetAnomalyFeedbackApprovalStatusRequest, context: grpc.aio.ServicerContext,
    ) -> anomalies_v1_anomaly_feedback_approval_service_pb2.GetAnomalyFeedbackApprovalStatusResponse:
        """Returns an anomaly feedback."""
        return await self.workflow.handle_get_anomaly_feedback_approval_status(request)

    @rpc_errors
    @retry_transient
    async def ListPendingAnomalyFeedbacks(
        self, request: anomalies_v1_anomaly_feedback_approval_service_pb2.ListPendingAnomalyFeedbacksRequest, context: grpc.aio.ServicerContext,
    ) -> anomalies_v1_anomaly_feedback_approval_service_pb2.ListPendingAnomalyFeedbacksResponse:
        """Lists anomaly feedbacks a page at a time."""
        return await self.workflow.handle_list_pending_anomaly_feedbacks(request)

    @rpc_errors
    async def RecallAnomalyFeedback(
        self, request: anomalies_v1_anomaly_feedback_approval_service_pb2.RecallAnomalyFeedbackRequest, context: grpc.aio.ServicerContext,
    ) -> anomalies_v1_anomaly_feedback_approval_service_pb2.RecallAnomalyFeedbackResponse:
        """Recalls an anomaly feedback."""
        return await self.workflow.handle_recall_anomaly_feedback(request)

    @rpc_errors
    async def RejectAnomalyFeedback(
        self, request: anomalies_v1_anomaly_feedback_approval_service_pb2.RejectAnomalyFeedbackRequest, context: grpc.aio.ServicerContext,
    ) -> anomalies_v1_anomaly_feedback_approval_service_pb2.RejectAnomalyFeedbackResponse:
        """Rejects an anomaly feedback."""
        return await self.workflow.handle_reject_anomaly_feedback(request)

    @rpc_errors
    async def SubmitAnomalyFeedback(
        self, request: anomalies_v1_anomaly_feedback_approval_service_pb2.SubmitAnomalyFeedbackRequest, context: grpc.aio.ServicerContext,
    ) -> anomalies_v1_anomaly_feedback_approval_service_pb2.SubmitAnomalyFeedbackResponse:
        """Submits an anomaly feedback."""
        return await self.workflow.handle_submit_anomaly_feedback(request)
