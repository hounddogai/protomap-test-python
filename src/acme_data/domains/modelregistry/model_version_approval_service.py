"""Routes model versions through approval, with escalation and delegation."""

from __future__ import annotations

from collections.abc import AsyncIterator

import grpc

from acme.modelregistry.v1 import (
    model_version_approval_service_pb2_grpc as modelregistry_v1_model_version_approval_service_pb2_grpc,
)

from acme_data.domains.modelregistry.dependencies import Dependencies
from acme_data.domains.modelregistry.model_version_approval_service_handlers import ModelVersionApprovalServicerHandlers
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors


class ModelVersionApprovalServicer(
    ModelVersionApprovalServicerHandlers,
    modelregistry_v1_model_version_approval_service_pb2_grpc.ModelVersionApprovalServiceServicer
):
    """Routes model versions through approval, with escalation and delegation."""
