"""Answers read-only questions about data shares, for screens and reports."""

from __future__ import annotations

from collections.abc import AsyncIterator

import grpc

from acme.datahub.v1 import data_share_query_service_pb2_grpc as datahub_v1_data_share_query_service_pb2_grpc

from acme_data.domains.datahub.data_share_query_service_handlers import DataShareQueryServicerHandlers
from acme_data.domains.datahub.dependencies import Dependencies
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors


class DataShareQueryServicer(
    DataShareQueryServicerHandlers,
    datahub_v1_data_share_query_service_pb2_grpc.DataShareQueryServiceServicer
):
    """Answers read-only questions about data shares, for screens and reports."""
