"""Runs the long-lived workflow that takes a dataset from start to finish."""

from __future__ import annotations

from collections.abc import AsyncIterator

import grpc

from acme.datasets.v1 import dataset_workflow_service_pb2_grpc as datasets_v1_dataset_workflow_service_pb2_grpc

from acme_data.domains.datasets.dataset_workflow_service_handlers import DatasetWorkflowServicerHandlers
from acme_data.domains.datasets.dependencies import Dependencies
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors


class DatasetWorkflowServicer(
    DatasetWorkflowServicerHandlers,
    datasets_v1_dataset_workflow_service_pb2_grpc.DatasetWorkflowServiceServicer
):
    """Runs the long-lived workflow that takes a dataset from start to finish."""
