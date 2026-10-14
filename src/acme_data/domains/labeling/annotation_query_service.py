"""Answers read-only questions about annotations, for screens and reports."""

from __future__ import annotations

from collections.abc import AsyncIterator

import grpc

from acme.labeling.v1 import annotation_query_service_pb2_grpc as labeling_v1_annotation_query_service_pb2_grpc

from acme_data.domains.labeling.annotation_query_service_handlers import AnnotationQueryServicerHandlers
from acme_data.domains.labeling.dependencies import Dependencies
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors


class AnnotationQueryServicer(
    AnnotationQueryServicerHandlers,
    labeling_v1_annotation_query_service_pb2_grpc.AnnotationQueryServiceServicer
):
    """Answers read-only questions about annotations, for screens and reports."""
