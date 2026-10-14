"""Replaceable partner hooks of the recommendations domain."""

from __future__ import annotations

from acme.datasets.v1 import data_schema_calculation_service_pb2 as datasets_v1_data_schema_calculation_service_pb2
from acme.datasets.v1 import (
    data_schema_calculation_service_pb2_grpc as datasets_v1_data_schema_calculation_service_pb2_grpc,
)
from acme.identity.v1 import user_validation_service_pb2 as identity_v1_user_validation_service_pb2
from acme.identity.v1 import user_validation_service_pb2_grpc as identity_v1_user_validation_service_pb2_grpc
from acme.performers.v1 import performer_service_pb2 as performers_v1_performer_service_pb2
from acme.performers.v1 import performer_service_pb2_grpc as performers_v1_performer_service_pb2_grpc
from acme.pipelines.v1 import pipeline_lifecycle_service_pb2 as pipelines_v1_pipeline_lifecycle_service_pb2
from acme.pipelines.v1 import pipeline_lifecycle_service_pb2_grpc as pipelines_v1_pipeline_lifecycle_service_pb2_grpc
from acme.recommendations.v1 import (
    interaction_validation_service_pb2 as recommendations_v1_interaction_validation_service_pb2,
)
from acme.recommendations.v1 import (
    interaction_validation_service_pb2_grpc as recommendations_v1_interaction_validation_service_pb2_grpc,
)
from acme.recommendations.v1 import (
    recommendation_model_calculation_service_pb2 as recommendations_v1_recommendation_model_calculation_service_pb2,
)
from acme.recommendations.v1 import (
    recommendation_model_calculation_service_pb2_grpc as recommendations_v1_recommendation_model_calculation_service_pb2_grpc,
)
from acme.recommendations.v1 import (
    recommendation_model_query_service_pb2 as recommendations_v1_recommendation_model_query_service_pb2,
)
from acme.recommendations.v1 import (
    recommendation_model_query_service_pb2_grpc as recommendations_v1_recommendation_model_query_service_pb2_grpc,
)
from acme.recommendations.v1 import (
    recommendation_model_validation_service_pb2 as recommendations_v1_recommendation_model_validation_service_pb2,
)
from acme.recommendations.v1 import (
    recommendation_model_validation_service_pb2_grpc as recommendations_v1_recommendation_model_validation_service_pb2_grpc,
)
from acme.recommendations.v1 import recommendation_set_service_pb2 as recommendations_v1_recommendation_set_service_pb2
from acme.recommendations.v1 import (
    recommendation_set_service_pb2_grpc as recommendations_v1_recommendation_set_service_pb2_grpc,
)


async def interaction_approval_comment_interaction_approval3(
    client: pipelines_v1_pipeline_lifecycle_service_pb2_grpc.PipelineLifecycleServiceStub,
    request: pipelines_v1_pipeline_lifecycle_service_pb2.SchedulePipelineExpiryRequest,
    timeout: float
) -> pipelines_v1_pipeline_lifecycle_service_pb2.SchedulePipelineExpiryResponse:
    raise RuntimeError("domain hook was not installed")


async def interaction_calculation_quote_interaction1(
    client: recommendations_v1_recommendation_model_calculation_service_pb2_grpc.RecommendationModelCalculationServiceStub,
    request: recommendations_v1_recommendation_model_calculation_service_pb2.RecalculateRecommendationModelsRequest,
    timeout: float
) -> recommendations_v1_recommendation_model_calculation_service_pb2.RecalculateRecommendationModelsResponse:
    raise RuntimeError("domain hook was not installed")


async def interaction_lifecycle_expire_interaction2(
    client: recommendations_v1_recommendation_model_query_service_pb2_grpc.RecommendationModelQueryServiceStub,
    request: recommendations_v1_recommendation_model_query_service_pb2.CountRecommendationModelsRequest,
    timeout: float
) -> recommendations_v1_recommendation_model_query_service_pb2.CountRecommendationModelsResponse:
    raise RuntimeError("domain hook was not installed")


async def interaction_validation_lint_interactions0(
    client: performers_v1_performer_service_pb2_grpc.PerformerServiceStub,
    request: performers_v1_performer_service_pb2.BatchGetPerformersRequest,
    timeout: float
) -> performers_v1_performer_service_pb2.BatchGetPerformersResponse:
    raise RuntimeError("domain hook was not installed")


async def recommendation_model_approval_delegate_recommendation_model_approval2(
    client: recommendations_v1_interaction_validation_service_pb2_grpc.InteractionValidationServiceStub,
    request: recommendations_v1_interaction_validation_service_pb2.ExplainInteractionDecisionRequest,
    timeout: float
) -> recommendations_v1_interaction_validation_service_pb2.ExplainInteractionDecisionResponse:
    raise RuntimeError("domain hook was not installed")


async def recommendation_model_calculation_compare_recommendation_model_options2(
    client: identity_v1_user_validation_service_pb2_grpc.UserValidationServiceStub,
    request: identity_v1_user_validation_service_pb2.CheckUserEligibilityRequest,
    timeout: float
) -> identity_v1_user_validation_service_pb2.CheckUserEligibilityResponse:
    raise RuntimeError("domain hook was not installed")


async def recommendation_model_workflow_retry_recommendation_model_workflow2(
    client: recommendations_v1_recommendation_set_service_pb2_grpc.RecommendationSetServiceStub,
    request: recommendations_v1_recommendation_set_service_pb2.UpdateRecommendationSetRequest,
    timeout: float
) -> recommendations_v1_recommendation_set_service_pb2.UpdateRecommendationSetResponse:
    raise RuntimeError("domain hook was not installed")


async def recommendation_set_validation_lint_recommendation_sets1(
    client: datasets_v1_data_schema_calculation_service_pb2_grpc.DataSchemaCalculationServiceStub,
    request: datasets_v1_data_schema_calculation_service_pb2.CalculateDataSchemaRequest,
    timeout: float
) -> datasets_v1_data_schema_calculation_service_pb2.CalculateDataSchemaResponse:
    raise RuntimeError("domain hook was not installed")


async def recommendation_set_workflow_retry_recommendation_set_workflow0(
    client: recommendations_v1_recommendation_model_validation_service_pb2_grpc.RecommendationModelValidationServiceStub,
    request: recommendations_v1_recommendation_model_validation_service_pb2.CheckRecommendationModelEligibilityRequest,
    timeout: float
) -> recommendations_v1_recommendation_model_validation_service_pb2.CheckRecommendationModelEligibilityResponse:
    raise RuntimeError("domain hook was not installed")
