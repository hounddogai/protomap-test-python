"""Routes feature values through approval, with escalation and delegation."""

from __future__ import annotations

from collections.abc import AsyncIterator

import grpc

from acme.featurestore.v1 import (
    feature_value_approval_service_pb2_grpc as featurestore_v1_feature_value_approval_service_pb2_grpc,
)

from acme_data.domains.featurestore.dependencies import Dependencies
from acme_data.domains.featurestore.feature_value_approval_service_handlers import FeatureValueApprovalServicerHandlers
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors


class FeatureValueApprovalServicer(
    FeatureValueApprovalServicerHandlers,
    featurestore_v1_feature_value_approval_service_pb2_grpc.FeatureValueApprovalServiceServicer
):
    """Routes feature values through approval, with escalation and delegation."""
