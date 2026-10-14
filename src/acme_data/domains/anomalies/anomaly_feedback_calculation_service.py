"""Computes the figures of an anomaly feedback, such as totals, taxes, and estimates."""

from __future__ import annotations

from collections.abc import AsyncIterator

import grpc

from acme.anomalies.v1 import (
    anomaly_feedback_calculation_service_pb2 as anomalies_v1_anomaly_feedback_calculation_service_pb2,
)
from acme.anomalies.v1 import (
    anomaly_feedback_calculation_service_pb2_grpc as anomalies_v1_anomaly_feedback_calculation_service_pb2_grpc,
)

from acme_data.domains.anomalies.anomaly_feedback_calculation_service_operations import (
    handle_calculate_anomaly_feedback,
)
from acme_data.domains.anomalies.anomaly_feedback_calculation_service_operations import (
    handle_compare_anomaly_feedback_options,
)
from acme_data.domains.anomalies.anomaly_feedback_calculation_service_operations import handle_estimate_anomaly_feedback
from acme_data.domains.anomalies.anomaly_feedback_calculation_service_operations import (
    handle_explain_anomaly_feedback_calculation,
)
from acme_data.domains.anomalies.anomaly_feedback_calculation_service_operations import (
    handle_get_anomaly_feedback_rates,
)
from acme_data.domains.anomalies.anomaly_feedback_calculation_service_operations import handle_quote_anomaly_feedback
from acme_data.domains.anomalies.anomaly_feedback_calculation_service_operations import (
    handle_recalculate_anomaly_feedbacks,
)
from acme_data.domains.anomalies.anomaly_feedback_calculation_service_operations import handle_simulate_anomaly_feedback
from acme_data.domains.anomalies.dependencies import Dependencies
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors


class AnomalyFeedbackCalculationServicer(
    anomalies_v1_anomaly_feedback_calculation_service_pb2_grpc.AnomalyFeedbackCalculationServiceServicer
):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    async def CalculateAnomalyFeedback(
        self, request: anomalies_v1_anomaly_feedback_calculation_service_pb2.CalculateAnomalyFeedbackRequest, context: grpc.aio.ServicerContext,
    ) -> anomalies_v1_anomaly_feedback_calculation_service_pb2.CalculateAnomalyFeedbackResponse:
        """Calculates an anomaly feedback."""
        return await handle_calculate_anomaly_feedback(self.deps, request)

    @rpc_errors
    async def CompareAnomalyFeedbackOptions(
        self, request: anomalies_v1_anomaly_feedback_calculation_service_pb2.CompareAnomalyFeedbackOptionsRequest, context: grpc.aio.ServicerContext,
    ) -> anomalies_v1_anomaly_feedback_calculation_service_pb2.CompareAnomalyFeedbackOptionsResponse:
        """Compares an anomaly feedback."""
        return await handle_compare_anomaly_feedback_options(self.deps, request)

    @rpc_errors
    async def EstimateAnomalyFeedback(
        self, request: anomalies_v1_anomaly_feedback_calculation_service_pb2.EstimateAnomalyFeedbackRequest, context: grpc.aio.ServicerContext,
    ) -> anomalies_v1_anomaly_feedback_calculation_service_pb2.EstimateAnomalyFeedbackResponse:
        """Estimates an anomaly feedback."""
        return await handle_estimate_anomaly_feedback(self.deps, request)

    @rpc_errors
    async def ExplainAnomalyFeedbackCalculation(
        self, request: anomalies_v1_anomaly_feedback_calculation_service_pb2.ExplainAnomalyFeedbackCalculationRequest, context: grpc.aio.ServicerContext,
    ) -> anomalies_v1_anomaly_feedback_calculation_service_pb2.ExplainAnomalyFeedbackCalculationResponse:
        """Explains an anomaly feedback."""
        return await handle_explain_anomaly_feedback_calculation(self.deps, request)

    @rpc_errors
    @retry_transient
    async def GetAnomalyFeedbackRates(
        self, request: anomalies_v1_anomaly_feedback_calculation_service_pb2.GetAnomalyFeedbackRatesRequest, context: grpc.aio.ServicerContext,
    ) -> anomalies_v1_anomaly_feedback_calculation_service_pb2.GetAnomalyFeedbackRatesResponse:
        """Returns an anomaly feedback."""
        return await handle_get_anomaly_feedback_rates(self.deps, request)

    @rpc_errors
    async def QuoteAnomalyFeedback(
        self, request: anomalies_v1_anomaly_feedback_calculation_service_pb2.QuoteAnomalyFeedbackRequest, context: grpc.aio.ServicerContext,
    ) -> anomalies_v1_anomaly_feedback_calculation_service_pb2.QuoteAnomalyFeedbackResponse:
        """Quotes an anomaly feedback."""
        return await handle_quote_anomaly_feedback(self.deps, request)

    @rpc_errors
    async def RecalculateAnomalyFeedbacks(
        self, request: anomalies_v1_anomaly_feedback_calculation_service_pb2.RecalculateAnomalyFeedbacksRequest, context: grpc.aio.ServicerContext,
    ) -> anomalies_v1_anomaly_feedback_calculation_service_pb2.RecalculateAnomalyFeedbacksResponse:
        """Recalculates an anomaly feedback."""
        return await handle_recalculate_anomaly_feedbacks(self.deps, request)

    @rpc_errors
    async def SimulateAnomalyFeedback(
        self, request: anomalies_v1_anomaly_feedback_calculation_service_pb2.SimulateAnomalyFeedbackRequest, context: grpc.aio.ServicerContext,
    ) -> anomalies_v1_anomaly_feedback_calculation_service_pb2.SimulateAnomalyFeedbackResponse:
        """Simulates an anomaly feedback."""
        return await handle_simulate_anomaly_feedback(self.deps, request)
