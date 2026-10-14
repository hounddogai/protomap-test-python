"""Checks data schemas against the rules before anything acts on them."""

from __future__ import annotations

from collections.abc import AsyncIterator

import grpc

from acme.datasets.v1 import data_schema_validation_service_pb2 as datasets_v1_data_schema_validation_service_pb2
from acme.datasets.v1 import (
    data_schema_validation_service_pb2_grpc as datasets_v1_data_schema_validation_service_pb2_grpc,
)

from acme_data.domains.datasets.data_schema_validation_service_operations import handle_check_data_schema_eligibility
from acme_data.domains.datasets.data_schema_validation_service_operations import handle_explain_data_schema_decision
from acme_data.domains.datasets.data_schema_validation_service_operations import handle_get_data_schema_rules
from acme_data.domains.datasets.data_schema_validation_service_operations import handle_preview_data_schema
from acme_data.domains.datasets.data_schema_validation_service_operations import handle_score_data_schema
from acme_data.domains.datasets.data_schema_validation_service_operations import handle_validate_data_schema
from acme_data.domains.datasets.dependencies import Dependencies
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors


class DataSchemaValidationServicer(
    datasets_v1_data_schema_validation_service_pb2_grpc.DataSchemaValidationServiceServicer
):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    async def CheckDataSchemaEligibility(
        self, request: datasets_v1_data_schema_validation_service_pb2.CheckDataSchemaEligibilityRequest, context: grpc.aio.ServicerContext,
    ) -> datasets_v1_data_schema_validation_service_pb2.CheckDataSchemaEligibilityResponse:
        """Checks a data schema."""
        return await handle_check_data_schema_eligibility(self.deps, request)

    @rpc_errors
    async def ExplainDataSchemaDecision(
        self, request: datasets_v1_data_schema_validation_service_pb2.ExplainDataSchemaDecisionRequest, context: grpc.aio.ServicerContext,
    ) -> datasets_v1_data_schema_validation_service_pb2.ExplainDataSchemaDecisionResponse:
        """Explains a data schema."""
        return await handle_explain_data_schema_decision(self.deps, request)

    @rpc_errors
    @retry_transient
    async def GetDataSchemaRules(
        self, request: datasets_v1_data_schema_validation_service_pb2.GetDataSchemaRulesRequest, context: grpc.aio.ServicerContext,
    ) -> datasets_v1_data_schema_validation_service_pb2.GetDataSchemaRulesResponse:
        """Returns a data schema."""
        return await handle_get_data_schema_rules(self.deps, request)

    @rpc_errors
    async def PreviewDataSchema(
        self, request: datasets_v1_data_schema_validation_service_pb2.PreviewDataSchemaRequest, context: grpc.aio.ServicerContext,
    ) -> datasets_v1_data_schema_validation_service_pb2.PreviewDataSchemaResponse:
        """Previews a data schema."""
        return await handle_preview_data_schema(self.deps, request)

    @rpc_errors
    async def ScoreDataSchema(
        self, request: datasets_v1_data_schema_validation_service_pb2.ScoreDataSchemaRequest, context: grpc.aio.ServicerContext,
    ) -> datasets_v1_data_schema_validation_service_pb2.ScoreDataSchemaResponse:
        """Scores a data schema."""
        return await handle_score_data_schema(self.deps, request)

    @rpc_errors
    async def ValidateDataSchema(
        self, request: datasets_v1_data_schema_validation_service_pb2.ValidateDataSchemaRequest, context: grpc.aio.ServicerContext,
    ) -> datasets_v1_data_schema_validation_service_pb2.ValidateDataSchemaResponse:
        """Validates a data schema."""
        return await handle_validate_data_schema(self.deps, request)
