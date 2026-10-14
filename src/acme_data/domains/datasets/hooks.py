"""Replaceable partner hooks of the datasets domain."""

from __future__ import annotations

from acme.anomalies.v1 import (
    anomaly_feedback_workflow_service_pb2 as anomalies_v1_anomaly_feedback_workflow_service_pb2,
)
from acme.anomalies.v1 import (
    anomaly_feedback_workflow_service_pb2_grpc as anomalies_v1_anomaly_feedback_workflow_service_pb2_grpc,
)
from acme.anomalies.v1 import anomaly_validation_service_pb2 as anomalies_v1_anomaly_validation_service_pb2
from acme.anomalies.v1 import anomaly_validation_service_pb2_grpc as anomalies_v1_anomaly_validation_service_pb2_grpc
from acme.authorization.v1 import (
    access_policy_validation_service_pb2 as authorization_v1_access_policy_validation_service_pb2,
)
from acme.authorization.v1 import (
    access_policy_validation_service_pb2_grpc as authorization_v1_access_policy_validation_service_pb2_grpc,
)
from acme.datasets.v1 import (
    dataset_version_calculation_service_pb2 as datasets_v1_dataset_version_calculation_service_pb2,
)
from acme.datasets.v1 import (
    dataset_version_calculation_service_pb2_grpc as datasets_v1_dataset_version_calculation_service_pb2_grpc,
)
from acme.featurestore.v1 import feature_value_sync_service_pb2 as featurestore_v1_feature_value_sync_service_pb2
from acme.featurestore.v1 import (
    feature_value_sync_service_pb2_grpc as featurestore_v1_feature_value_sync_service_pb2_grpc,
)
from acme.featurestore.v1 import (
    feature_value_validation_service_pb2 as featurestore_v1_feature_value_validation_service_pb2,
)
from acme.featurestore.v1 import (
    feature_value_validation_service_pb2_grpc as featurestore_v1_feature_value_validation_service_pb2_grpc,
)
from acme.identity.v1 import user_service_pb2 as identity_v1_user_service_pb2
from acme.identity.v1 import user_service_pb2_grpc as identity_v1_user_service_pb2_grpc


async def data_schema_calculation_quote_data_schema1(
    client: anomalies_v1_anomaly_validation_service_pb2_grpc.AnomalyValidationServiceStub,
    request: anomalies_v1_anomaly_validation_service_pb2.CheckAnomalyEligibilityRequest,
    timeout: float
) -> anomalies_v1_anomaly_validation_service_pb2.CheckAnomalyEligibilityResponse:
    raise RuntimeError("domain hook was not installed")


async def data_schema_workflow_start_data_schema_workflow0(
    client: anomalies_v1_anomaly_feedback_workflow_service_pb2_grpc.AnomalyFeedbackWorkflowServiceStub,
    request: anomalies_v1_anomaly_feedback_workflow_service_pb2.AdvanceAnomalyFeedbackWorkflowRequest,
    timeout: float
) -> anomalies_v1_anomaly_feedback_workflow_service_pb2.AdvanceAnomalyFeedbackWorkflowResponse:
    raise RuntimeError("domain hook was not installed")


async def dataset_approval_reject_dataset1(
    client: featurestore_v1_feature_value_sync_service_pb2_grpc.FeatureValueSyncServiceStub,
    request: featurestore_v1_feature_value_sync_service_pb2.PushFeatureValueRequest,
    timeout: float
) -> featurestore_v1_feature_value_sync_service_pb2.PushFeatureValueResponse:
    raise RuntimeError("domain hook was not installed")


async def dataset_batch_get_datasets1(
    client: featurestore_v1_feature_value_validation_service_pb2_grpc.FeatureValueValidationServiceStub,
    request: featurestore_v1_feature_value_validation_service_pb2.PreviewFeatureValueRequest,
    timeout: float
) -> featurestore_v1_feature_value_validation_service_pb2.PreviewFeatureValueResponse:
    raise RuntimeError("domain hook was not installed")


async def dataset_validation_check_dataset_eligibility3(
    client: datasets_v1_dataset_version_calculation_service_pb2_grpc.DatasetVersionCalculationServiceStub,
    request: datasets_v1_dataset_version_calculation_service_pb2.CalculateDatasetVersionRequest,
    timeout: float
) -> datasets_v1_dataset_version_calculation_service_pb2.CalculateDatasetVersionResponse:
    raise RuntimeError("domain hook was not installed")


async def dataset_validation_validate_dataset1(
    client: authorization_v1_access_policy_validation_service_pb2_grpc.AccessPolicyValidationServiceStub,
    request: authorization_v1_access_policy_validation_service_pb2.CheckAccessPolicyEligibilityRequest,
    timeout: float
) -> authorization_v1_access_policy_validation_service_pb2.CheckAccessPolicyEligibilityResponse:
    raise RuntimeError("domain hook was not installed")


async def dataset_version_calculation_simulate_dataset_version2(
    client: identity_v1_user_service_pb2_grpc.UserServiceStub,
    request: identity_v1_user_service_pb2.CloneUserRequest,
    timeout: float
) -> identity_v1_user_service_pb2.CloneUserResponse:
    raise RuntimeError("domain hook was not installed")


async def dataset_version_validation_lint_dataset_versions0(
    client: datasets_v1_dataset_version_calculation_service_pb2_grpc.DatasetVersionCalculationServiceStub,
    request: datasets_v1_dataset_version_calculation_service_pb2.EstimateDatasetVersionRequest,
    timeout: float
) -> datasets_v1_dataset_version_calculation_service_pb2.EstimateDatasetVersionResponse:
    raise RuntimeError("domain hook was not installed")
