"""Checks entities against the rules before anything acts on them."""

from __future__ import annotations

from collections.abc import AsyncIterator

import grpc

from acme.featurestore.v1 import entity_validation_service_pb2 as featurestore_v1_entity_validation_service_pb2
from acme.featurestore.v1 import (
    entity_validation_service_pb2_grpc as featurestore_v1_entity_validation_service_pb2_grpc,
)

from acme_data.domains.featurestore.dependencies import Dependencies
from acme_data.domains.featurestore.entity_validation_service_workflow import EntityValidationServicerWorkflow
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors


class EntityValidationServicer(featurestore_v1_entity_validation_service_pb2_grpc.EntityValidationServiceServicer):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps
        self.workflow = EntityValidationServicerWorkflow(deps)

    @rpc_errors
    async def CheckEntityEligibility(
        self, request: featurestore_v1_entity_validation_service_pb2.CheckEntityEligibilityRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_entity_validation_service_pb2.CheckEntityEligibilityResponse:
        """Checks an entity."""
        return await self.workflow.handle_check_entity_eligibility(request)

    @rpc_errors
    async def ExplainEntityDecision(
        self, request: featurestore_v1_entity_validation_service_pb2.ExplainEntityDecisionRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_entity_validation_service_pb2.ExplainEntityDecisionResponse:
        """Explains an entity."""
        return await self.workflow.handle_explain_entity_decision(request)

    @rpc_errors
    @retry_transient
    async def GetEntityRules(
        self, request: featurestore_v1_entity_validation_service_pb2.GetEntityRulesRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_entity_validation_service_pb2.GetEntityRulesResponse:
        """Returns an entity."""
        return await self.workflow.handle_get_entity_rules(request)

    @rpc_errors
    async def LintEntities(
        self, request: featurestore_v1_entity_validation_service_pb2.LintEntitiesRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_entity_validation_service_pb2.LintEntitiesResponse:
        """Lints an entity."""
        return await self.workflow.handle_lint_entities(request)

    @rpc_errors
    async def NormalizeEntity(
        self, request: featurestore_v1_entity_validation_service_pb2.NormalizeEntityRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_entity_validation_service_pb2.NormalizeEntityResponse:
        """Normalizes an entity."""
        return await self.workflow.handle_normalize_entity(request)

    @rpc_errors
    async def PreviewEntity(
        self, request: featurestore_v1_entity_validation_service_pb2.PreviewEntityRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_entity_validation_service_pb2.PreviewEntityResponse:
        """Previews an entity."""
        return await self.workflow.handle_preview_entity(request)

    @rpc_errors
    async def ScoreEntity(
        self, request: featurestore_v1_entity_validation_service_pb2.ScoreEntityRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_entity_validation_service_pb2.ScoreEntityResponse:
        """Scores an entity."""
        return await self.workflow.handle_score_entity(request)

    @rpc_errors
    async def ValidateEntity(
        self, request: featurestore_v1_entity_validation_service_pb2.ValidateEntityRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_entity_validation_service_pb2.ValidateEntityResponse:
        """Validates an entity."""
        return await self.workflow.handle_validate_entity(request)
