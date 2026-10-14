"""Keeps feature views in step with the systems of record in other regions."""

from __future__ import annotations

from collections.abc import AsyncIterator

import grpc

from acme.featurestore.v1 import (
    feature_view_sync_service_pb2_grpc as featurestore_v1_feature_view_sync_service_pb2_grpc,
)

from acme_data.domains.featurestore.dependencies import Dependencies
from acme_data.domains.featurestore.feature_view_sync_service_handlers import FeatureViewSyncServicerHandlers
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors


class FeatureViewSyncServicer(
    FeatureViewSyncServicerHandlers,
    featurestore_v1_feature_view_sync_service_pb2_grpc.FeatureViewSyncServiceServicer
):
    """Keeps feature views in step with the systems of record in other regions."""
