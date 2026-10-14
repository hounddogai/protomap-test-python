"""Computes the figures of a feature view, such as totals, taxes, and estimates."""

from __future__ import annotations

from collections.abc import AsyncIterator

import grpc

from acme.featurestore.v1 import (
    feature_view_calculation_service_pb2_grpc as featurestore_v1_feature_view_calculation_service_pb2_grpc,
)

from acme_data.domains.featurestore.dependencies import Dependencies
from acme_data.domains.featurestore.feature_view_calculation_service_handlers import (
    FeatureViewCalculationServicerHandlers,
)
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors


class FeatureViewCalculationServicer(
    FeatureViewCalculationServicerHandlers,
    featurestore_v1_feature_view_calculation_service_pb2_grpc.FeatureViewCalculationServiceServicer
):
    """Computes the figures of a feature view, such as totals, taxes, and estimates."""
