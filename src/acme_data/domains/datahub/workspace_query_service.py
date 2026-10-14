"""Answers read-only questions about workspaces, for screens and reports."""

from __future__ import annotations

from collections.abc import AsyncIterator

import grpc

from acme.datahub.v1 import workspace_query_service_pb2_grpc as datahub_v1_workspace_query_service_pb2_grpc

from acme_data.domains.datahub.dependencies import Dependencies
from acme_data.domains.datahub.workspace_query_service_handlers import WorkspaceQueryServicerHandlers
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors


class WorkspaceQueryServicer(
    WorkspaceQueryServicerHandlers,
    datahub_v1_workspace_query_service_pb2_grpc.WorkspaceQueryServiceServicer
):
    """Answers read-only questions about workspaces, for screens and reports."""
