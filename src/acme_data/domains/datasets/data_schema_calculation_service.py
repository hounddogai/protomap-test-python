"""Computes the figures of a data schema, such as totals, taxes, and estimates."""

from __future__ import annotations

from collections.abc import AsyncIterator

import grpc

from acme.datasets.v1 import data_schema_calculation_service_pb2 as datasets_v1_data_schema_calculation_service_pb2
from acme.datasets.v1 import (
    data_schema_calculation_service_pb2_grpc as datasets_v1_data_schema_calculation_service_pb2_grpc,
)

from acme_data.domains.datasets.data_schema_calculation_service_workflow import DataSchemaCalculationServicerWorkflow
from acme_data.domains.datasets.dependencies import Dependencies
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors


class DataSchemaCalculationServicer(
    datasets_v1_data_schema_calculation_service_pb2_grpc.DataSchemaCalculationServiceServicer
):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps
        self.workflow = DataSchemaCalculationServicerWorkflow(deps)

    @rpc_errors
    async def CalculateDataSchema(
        self, request: datasets_v1_data_schema_calculation_service_pb2.CalculateDataSchemaRequest, context: grpc.aio.ServicerContext,
    ) -> datasets_v1_data_schema_calculation_service_pb2.CalculateDataSchemaResponse:
        """Calculates a data schema."""
        return await self.workflow.handle_calculate_data_schema(request)

    @rpc_errors
    async def CompareDataSchemaOptions(
        self, request: datasets_v1_data_schema_calculation_service_pb2.CompareDataSchemaOptionsRequest, context: grpc.aio.ServicerContext,
    ) -> datasets_v1_data_schema_calculation_service_pb2.CompareDataSchemaOptionsResponse:
        """Compares a data schema."""
        return await self.workflow.handle_compare_data_schema_options(request)

    @rpc_errors
    async def EstimateDataSchema(
        self, request: datasets_v1_data_schema_calculation_service_pb2.EstimateDataSchemaRequest, context: grpc.aio.ServicerContext,
    ) -> datasets_v1_data_schema_calculation_service_pb2.EstimateDataSchemaResponse:
        """Estimates a data schema."""
        return await self.workflow.handle_estimate_data_schema(request)

    @rpc_errors
    async def ExplainDataSchemaCalculation(
        self, request: datasets_v1_data_schema_calculation_service_pb2.ExplainDataSchemaCalculationRequest, context: grpc.aio.ServicerContext,
    ) -> datasets_v1_data_schema_calculation_service_pb2.ExplainDataSchemaCalculationResponse:
        """Explains a data schema."""
        return await self.workflow.handle_explain_data_schema_calculation(request)

    @rpc_errors
    @retry_transient
    async def GetDataSchemaRates(
        self, request: datasets_v1_data_schema_calculation_service_pb2.GetDataSchemaRatesRequest, context: grpc.aio.ServicerContext,
    ) -> datasets_v1_data_schema_calculation_service_pb2.GetDataSchemaRatesResponse:
        """Returns a data schema."""
        return await self.workflow.handle_get_data_schema_rates(request)

    @rpc_errors
    async def QuoteDataSchema(
        self, request: datasets_v1_data_schema_calculation_service_pb2.QuoteDataSchemaRequest, context: grpc.aio.ServicerContext,
    ) -> datasets_v1_data_schema_calculation_service_pb2.QuoteDataSchemaResponse:
        """Quotes a data schema."""
        return await self.workflow.handle_quote_data_schema(request)

    @rpc_errors
    async def RecalculateDataSchemas(
        self, request: datasets_v1_data_schema_calculation_service_pb2.RecalculateDataSchemasRequest, context: grpc.aio.ServicerContext,
    ) -> datasets_v1_data_schema_calculation_service_pb2.RecalculateDataSchemasResponse:
        """Recalculates a data schema."""
        return await self.workflow.handle_recalculate_data_schemas(request)
