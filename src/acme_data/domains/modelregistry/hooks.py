"""Replaceable partner hooks of the modelregistry domain."""

from __future__ import annotations

from acme.anomalies.v1 import anomaly_approval_service_pb2 as anomalies_v1_anomaly_approval_service_pb2
from acme.anomalies.v1 import anomaly_approval_service_pb2_grpc as anomalies_v1_anomaly_approval_service_pb2_grpc
from acme.anomalies.v1 import anomaly_validation_service_pb2 as anomalies_v1_anomaly_validation_service_pb2
from acme.anomalies.v1 import anomaly_validation_service_pb2_grpc as anomalies_v1_anomaly_validation_service_pb2_grpc
from acme.customers.v1 import household_validation_service_pb2 as customers_v1_household_validation_service_pb2
from acme.customers.v1 import (
    household_validation_service_pb2_grpc as customers_v1_household_validation_service_pb2_grpc,
)
from acme.featureflags.v1 import (
    feature_flag_validation_service_pb2 as featureflags_v1_feature_flag_validation_service_pb2,
)
from acme.featureflags.v1 import (
    feature_flag_validation_service_pb2_grpc as featureflags_v1_feature_flag_validation_service_pb2_grpc,
)
from acme.identity.v1 import user_service_pb2 as identity_v1_user_service_pb2
from acme.identity.v1 import user_service_pb2_grpc as identity_v1_user_service_pb2_grpc
from acme.lineage.v1 import lineage_edge_sync_service_pb2 as lineage_v1_lineage_edge_sync_service_pb2
from acme.lineage.v1 import lineage_edge_sync_service_pb2_grpc as lineage_v1_lineage_edge_sync_service_pb2_grpc
from acme.metrics.v1 import dashboard_validation_service_pb2 as metrics_v1_dashboard_validation_service_pb2
from acme.metrics.v1 import dashboard_validation_service_pb2_grpc as metrics_v1_dashboard_validation_service_pb2_grpc
from acme.modelregistry.v1 import (
    model_version_approval_service_pb2 as modelregistry_v1_model_version_approval_service_pb2,
)
from acme.modelregistry.v1 import (
    model_version_approval_service_pb2_grpc as modelregistry_v1_model_version_approval_service_pb2_grpc,
)
from acme.modelregistry.v1 import (
    model_version_calculation_service_pb2 as modelregistry_v1_model_version_calculation_service_pb2,
)
from acme.modelregistry.v1 import (
    model_version_calculation_service_pb2_grpc as modelregistry_v1_model_version_calculation_service_pb2_grpc,
)
from acme.modelregistry.v1 import (
    model_version_reporting_service_pb2 as modelregistry_v1_model_version_reporting_service_pb2,
)
from acme.modelregistry.v1 import (
    model_version_reporting_service_pb2_grpc as modelregistry_v1_model_version_reporting_service_pb2_grpc,
)
from acme.modelregistry.v1 import model_version_sync_service_pb2 as modelregistry_v1_model_version_sync_service_pb2
from acme.modelregistry.v1 import (
    model_version_sync_service_pb2_grpc as modelregistry_v1_model_version_sync_service_pb2_grpc,
)
from acme.modelregistry.v1 import (
    model_version_validation_service_pb2 as modelregistry_v1_model_version_validation_service_pb2,
)
from acme.modelregistry.v1 import (
    model_version_validation_service_pb2_grpc as modelregistry_v1_model_version_validation_service_pb2_grpc,
)
from acme.modelregistry.v1 import (
    registered_model_calculation_service_pb2 as modelregistry_v1_registered_model_calculation_service_pb2,
)
from acme.modelregistry.v1 import (
    registered_model_calculation_service_pb2_grpc as modelregistry_v1_registered_model_calculation_service_pb2_grpc,
)
from acme.modelregistry.v1 import (
    registered_model_query_service_pb2 as modelregistry_v1_registered_model_query_service_pb2,
)
from acme.modelregistry.v1 import (
    registered_model_query_service_pb2_grpc as modelregistry_v1_registered_model_query_service_pb2_grpc,
)
from acme.modelregistry.v1 import (
    registered_model_reporting_service_pb2 as modelregistry_v1_registered_model_reporting_service_pb2,
)
from acme.modelregistry.v1 import (
    registered_model_reporting_service_pb2_grpc as modelregistry_v1_registered_model_reporting_service_pb2_grpc,
)


async def deployment_approval_approve_deployment0(
    client: modelregistry_v1_registered_model_reporting_service_pb2_grpc.RegisteredModelReportingServiceStub,
    request: modelregistry_v1_registered_model_reporting_service_pb2.ScheduleRegisteredModelReportRequest,
    timeout: float
) -> modelregistry_v1_registered_model_reporting_service_pb2.ScheduleRegisteredModelReportResponse:
    raise RuntimeError("domain hook was not installed")


async def deployment_calculation_compare_deployment_options2(
    client: anomalies_v1_anomaly_validation_service_pb2_grpc.AnomalyValidationServiceStub,
    request: anomalies_v1_anomaly_validation_service_pb2.ScoreAnomalyRequest,
    timeout: float
) -> anomalies_v1_anomaly_validation_service_pb2.ScoreAnomalyResponse:
    raise RuntimeError("domain hook was not installed")


async def deployment_import_map_deployment_import_columns1(
    client: modelregistry_v1_registered_model_calculation_service_pb2_grpc.RegisteredModelCalculationServiceStub,
    request: modelregistry_v1_registered_model_calculation_service_pb2.QuoteRegisteredModelRequest,
    timeout: float
) -> modelregistry_v1_registered_model_calculation_service_pb2.QuoteRegisteredModelResponse:
    raise RuntimeError("domain hook was not installed")


async def deployment_lifecycle_reinstate_deployment2(
    client: anomalies_v1_anomaly_approval_service_pb2_grpc.AnomalyApprovalServiceStub,
    request: anomalies_v1_anomaly_approval_service_pb2.RejectAnomalyRequest,
    timeout: float
) -> anomalies_v1_anomaly_approval_service_pb2.RejectAnomalyResponse:
    raise RuntimeError("domain hook was not installed")


async def deployment_validation_normalize_deployment0(
    client: modelregistry_v1_model_version_validation_service_pb2_grpc.ModelVersionValidationServiceStub,
    request: modelregistry_v1_model_version_validation_service_pb2.ExplainModelVersionDecisionRequest,
    timeout: float
) -> modelregistry_v1_model_version_validation_service_pb2.ExplainModelVersionDecisionResponse:
    raise RuntimeError("domain hook was not installed")


async def deployment_workflow_signal_deployment_workflow1(
    client: customers_v1_household_validation_service_pb2_grpc.HouseholdValidationServiceStub,
    request: customers_v1_household_validation_service_pb2.CheckHouseholdEligibilityRequest,
    timeout: float
) -> customers_v1_household_validation_service_pb2.CheckHouseholdEligibilityResponse:
    raise RuntimeError("domain hook was not installed")


async def model_version_reporting_stream_model_version_metrics2(
    client: modelregistry_v1_model_version_sync_service_pb2_grpc.ModelVersionSyncServiceStub,
    request: modelregistry_v1_model_version_sync_service_pb2.ReconcileModelVersionsRequest,
    timeout: float
) -> modelregistry_v1_model_version_sync_service_pb2.ReconcileModelVersionsResponse:
    raise RuntimeError("domain hook was not installed")


async def model_version_sync_sync_model_versions0(
    client: modelregistry_v1_registered_model_query_service_pb2_grpc.RegisteredModelQueryServiceStub,
    request: modelregistry_v1_registered_model_query_service_pb2.ResolveRegisteredModelsRequest,
    timeout: float
) -> modelregistry_v1_registered_model_query_service_pb2.ResolveRegisteredModelsResponse:
    raise RuntimeError("domain hook was not installed")


async def model_version_validation_preview_model_version1(
    client: identity_v1_user_service_pb2_grpc.UserServiceStub,
    request: identity_v1_user_service_pb2.SearchUsersRequest,
    timeout: float
) -> identity_v1_user_service_pb2.SearchUsersResponse:
    raise RuntimeError("domain hook was not installed")


async def registered_model_approval_get_registered_model_approval_status1(
    client: lineage_v1_lineage_edge_sync_service_pb2_grpc.LineageEdgeSyncServiceStub,
    request: lineage_v1_lineage_edge_sync_service_pb2.ResolveLineageEdgeConflictRequest,
    timeout: float
) -> lineage_v1_lineage_edge_sync_service_pb2.ResolveLineageEdgeConflictResponse:
    raise RuntimeError("domain hook was not installed")


async def registered_model_lifecycle_suspend_registered_model0(
    client: modelregistry_v1_model_version_reporting_service_pb2_grpc.ModelVersionReportingServiceStub,
    request: modelregistry_v1_model_version_reporting_service_pb2.ShareModelVersionReportRequest,
    timeout: float
) -> modelregistry_v1_model_version_reporting_service_pb2.ShareModelVersionReportResponse:
    raise RuntimeError("domain hook was not installed")


async def registered_model_reporting_delete_registered_model_report3(
    client: modelregistry_v1_model_version_calculation_service_pb2_grpc.ModelVersionCalculationServiceStub,
    request: modelregistry_v1_model_version_calculation_service_pb2.RecalculateModelVersionsRequest,
    timeout: float
) -> modelregistry_v1_model_version_calculation_service_pb2.RecalculateModelVersionsResponse:
    raise RuntimeError("domain hook was not installed")


async def registered_model_delete_registered_model0(
    client: featureflags_v1_feature_flag_validation_service_pb2_grpc.FeatureFlagValidationServiceStub,
    request: featureflags_v1_feature_flag_validation_service_pb2.LintFeatureFlagsRequest,
    timeout: float
) -> featureflags_v1_feature_flag_validation_service_pb2.LintFeatureFlagsResponse:
    raise RuntimeError("domain hook was not installed")


async def registered_model_validation_validate_registered_model0(
    client: metrics_v1_dashboard_validation_service_pb2_grpc.DashboardValidationServiceStub,
    request: metrics_v1_dashboard_validation_service_pb2.CheckDashboardEligibilityRequest,
    timeout: float
) -> metrics_v1_dashboard_validation_service_pb2.CheckDashboardEligibilityResponse:
    raise RuntimeError("domain hook was not installed")


async def registered_model_workflow_start_registered_model_workflow1(
    client: modelregistry_v1_model_version_approval_service_pb2_grpc.ModelVersionApprovalServiceStub,
    request: modelregistry_v1_model_version_approval_service_pb2.EscalateModelVersionRequest,
    timeout: float
) -> modelregistry_v1_model_version_approval_service_pb2.EscalateModelVersionResponse:
    raise RuntimeError("domain hook was not installed")
