"""Routes feature views through approval, with escalation and delegation."""

from __future__ import annotations

from collections.abc import AsyncIterator

import grpc

from acme.featurestore.v1 import feature_view_approval_service_pb2 as featurestore_v1_feature_view_approval_service_pb2
from acme.featurestore.v1 import (
    feature_view_approval_service_pb2_grpc as featurestore_v1_feature_view_approval_service_pb2_grpc,
)

from acme_data.domains.featurestore.dependencies import Dependencies
from acme_data.domains.featurestore.feature_view_approval_service_operations import handle_approve_feature_view
from acme_data.domains.featurestore.feature_view_approval_service_operations import handle_comment_feature_view_approval
from acme_data.domains.featurestore.feature_view_approval_service_operations import (
    handle_delegate_feature_view_approval,
)
from acme_data.domains.featurestore.feature_view_approval_service_operations import handle_escalate_feature_view
from acme_data.domains.featurestore.feature_view_approval_service_operations import handle_recall_feature_view
from acme_data.domains.featurestore.feature_view_approval_service_operations import handle_reject_feature_view
from acme_data.domains.featurestore.feature_view_approval_service_operations import handle_submit_feature_view
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors


class FeatureViewApprovalServicer(
    featurestore_v1_feature_view_approval_service_pb2_grpc.FeatureViewApprovalServiceServicer
):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    async def ApproveFeatureView(
        self, request: featurestore_v1_feature_view_approval_service_pb2.ApproveFeatureViewRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_feature_view_approval_service_pb2.ApproveFeatureViewResponse:
        """Approves a feature view."""
        return await handle_approve_feature_view(self.deps, request)

    @rpc_errors
    async def CommentFeatureViewApproval(
        self, request: featurestore_v1_feature_view_approval_service_pb2.CommentFeatureViewApprovalRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_feature_view_approval_service_pb2.CommentFeatureViewApprovalResponse:
        """Comments a feature view."""
        return await handle_comment_feature_view_approval(self.deps, request)

    @rpc_errors
    async def DelegateFeatureViewApproval(
        self, request: featurestore_v1_feature_view_approval_service_pb2.DelegateFeatureViewApprovalRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_feature_view_approval_service_pb2.DelegateFeatureViewApprovalResponse:
        """Delegates a feature view."""
        return await handle_delegate_feature_view_approval(self.deps, request)

    @rpc_errors
    async def EscalateFeatureView(
        self, request: featurestore_v1_feature_view_approval_service_pb2.EscalateFeatureViewRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_feature_view_approval_service_pb2.EscalateFeatureViewResponse:
        """Escalates a feature view."""
        return await handle_escalate_feature_view(self.deps, request)

    @rpc_errors
    async def RecallFeatureView(
        self, request: featurestore_v1_feature_view_approval_service_pb2.RecallFeatureViewRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_feature_view_approval_service_pb2.RecallFeatureViewResponse:
        """Recalls a feature view."""
        return await handle_recall_feature_view(self.deps, request)

    @rpc_errors
    async def RejectFeatureView(
        self, request: featurestore_v1_feature_view_approval_service_pb2.RejectFeatureViewRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_feature_view_approval_service_pb2.RejectFeatureViewResponse:
        """Rejects a feature view."""
        return await handle_reject_feature_view(self.deps, request)

    @rpc_errors
    async def SubmitFeatureView(
        self, request: featurestore_v1_feature_view_approval_service_pb2.SubmitFeatureViewRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_feature_view_approval_service_pb2.SubmitFeatureViewResponse:
        """Submits a feature view."""
        return await handle_submit_feature_view(self.deps, request)
