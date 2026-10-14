"""Connects external systems that send notebook events."""

from __future__ import annotations

from collections.abc import AsyncIterator

import grpc

from acme.datahub.v1 import notebook_integration_service_pb2_grpc as datahub_v1_notebook_integration_service_pb2_grpc

from acme_data.domains.datahub.dependencies import Dependencies
from acme_data.domains.datahub.notebook_integration_service_handlers import NotebookIntegrationServicerHandlers
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors


class NotebookIntegrationServicer(
    NotebookIntegrationServicerHandlers,
    datahub_v1_notebook_integration_service_pb2_grpc.NotebookIntegrationServiceServicer
):
    """Connects external systems that send notebook events."""
