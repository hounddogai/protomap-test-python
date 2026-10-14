"""Runs the long-lived workflow that takes a data schema from start to finish."""

from __future__ import annotations

from collections.abc import AsyncIterator

import grpc

from acme.datasets.v1 import data_schema_workflow_service_pb2_grpc as datasets_v1_data_schema_workflow_service_pb2_grpc

from acme_data.domains.datasets.data_schema_workflow_service_handlers import DataSchemaWorkflowServicerHandlers
from acme_data.domains.datasets.dependencies import Dependencies
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors


class DataSchemaWorkflowServicer(
    DataSchemaWorkflowServicerHandlers,
    datasets_v1_data_schema_workflow_service_pb2_grpc.DataSchemaWorkflowServiceServicer
):
    """Runs the long-lived workflow that takes a data schema from start to finish."""
