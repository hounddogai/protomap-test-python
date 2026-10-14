"""Runs the long-lived workflow that takes a notebook from start to finish."""

from __future__ import annotations

from collections.abc import AsyncIterator

import grpc

from acme.datahub.v1 import notebook_workflow_service_pb2_grpc as datahub_v1_notebook_workflow_service_pb2_grpc

from acme_data.domains.datahub.dependencies import Dependencies
from acme_data.domains.datahub.notebook_workflow_service_handlers import NotebookWorkflowServicerHandlers
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors


class NotebookWorkflowServicer(
    NotebookWorkflowServicerHandlers,
    datahub_v1_notebook_workflow_service_pb2_grpc.NotebookWorkflowServiceServicer
):
    """Runs the long-lived workflow that takes a notebook from start to finish."""
