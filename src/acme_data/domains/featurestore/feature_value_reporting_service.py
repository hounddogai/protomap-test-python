"""Builds and schedules reports about feature values."""

from __future__ import annotations

from collections.abc import AsyncIterator

import grpc

from acme.featurestore.v1 import (
    feature_value_reporting_service_pb2_grpc as featurestore_v1_feature_value_reporting_service_pb2_grpc,
)

from acme_data.domains.featurestore.dependencies import Dependencies
from acme_data.domains.featurestore.feature_value_reporting_service_handlers import (
    FeatureValueReportingServicerHandlers,
)
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors


class FeatureValueReportingServicer(
    FeatureValueReportingServicerHandlers,
    featurestore_v1_feature_value_reporting_service_pb2_grpc.FeatureValueReportingServiceServicer
):
    """Builds and schedules reports about feature values."""
