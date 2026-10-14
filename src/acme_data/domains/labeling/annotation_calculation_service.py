"""Computes the figures of an annotation, such as totals, taxes, and estimates."""

from __future__ import annotations

from collections.abc import AsyncIterator

import grpc

from acme.labeling.v1 import annotation_calculation_service_pb2 as labeling_v1_annotation_calculation_service_pb2
from acme.labeling.v1 import (
    annotation_calculation_service_pb2_grpc as labeling_v1_annotation_calculation_service_pb2_grpc,
)

from acme_data.domains.labeling.annotation_calculation_service_workflow import AnnotationCalculationServicerWorkflow
from acme_data.domains.labeling.dependencies import Dependencies
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors


class AnnotationCalculationServicer(
    labeling_v1_annotation_calculation_service_pb2_grpc.AnnotationCalculationServiceServicer
):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps
        self.workflow = AnnotationCalculationServicerWorkflow(deps)

    @rpc_errors
    async def CalculateAnnotation(
        self, request: labeling_v1_annotation_calculation_service_pb2.CalculateAnnotationRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_annotation_calculation_service_pb2.CalculateAnnotationResponse:
        """Calculates an annotation."""
        return await self.workflow.handle_calculate_annotation(request)

    @rpc_errors
    async def CompareAnnotationOptions(
        self, request: labeling_v1_annotation_calculation_service_pb2.CompareAnnotationOptionsRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_annotation_calculation_service_pb2.CompareAnnotationOptionsResponse:
        """Compares an annotation."""
        return await self.workflow.handle_compare_annotation_options(request)

    @rpc_errors
    async def EstimateAnnotation(
        self, request: labeling_v1_annotation_calculation_service_pb2.EstimateAnnotationRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_annotation_calculation_service_pb2.EstimateAnnotationResponse:
        """Estimates an annotation."""
        return await self.workflow.handle_estimate_annotation(request)

    @rpc_errors
    async def ExplainAnnotationCalculation(
        self, request: labeling_v1_annotation_calculation_service_pb2.ExplainAnnotationCalculationRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_annotation_calculation_service_pb2.ExplainAnnotationCalculationResponse:
        """Explains an annotation."""
        return await self.workflow.handle_explain_annotation_calculation(request)

    @rpc_errors
    async def RecalculateAnnotations(
        self, request: labeling_v1_annotation_calculation_service_pb2.RecalculateAnnotationsRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_annotation_calculation_service_pb2.RecalculateAnnotationsResponse:
        """Recalculates an annotation."""
        return await self.workflow.handle_recalculate_annotations(request)

    @rpc_errors
    async def SimulateAnnotation(
        self, request: labeling_v1_annotation_calculation_service_pb2.SimulateAnnotationRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_annotation_calculation_service_pb2.SimulateAnnotationResponse:
        """Simulates an annotation."""
        return await self.workflow.handle_simulate_annotation(request)
