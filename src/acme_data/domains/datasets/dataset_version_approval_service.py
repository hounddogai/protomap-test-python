"""Routes dataset versions through approval, with escalation and delegation."""

from __future__ import annotations

from collections.abc import AsyncIterator

import grpc

from acme.datasets.v1 import (
    dataset_version_approval_service_pb2_grpc as datasets_v1_dataset_version_approval_service_pb2_grpc,
)

from acme_data.domains.datasets.dataset_version_approval_service_handlers import DatasetVersionApprovalServicerHandlers
from acme_data.domains.datasets.dependencies import Dependencies
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors


class DatasetVersionApprovalServicer(
    DatasetVersionApprovalServicerHandlers,
    datasets_v1_dataset_version_approval_service_pb2_grpc.DatasetVersionApprovalServiceServicer
):
    """Routes dataset versions through approval, with escalation and delegation."""
