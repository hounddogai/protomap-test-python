"""Transport adapters used by modelregistry workflows."""

from __future__ import annotations

from typing import Protocol

from acme.anomalies.v1 import anomaly_approval_service_pb2 as anomalies_v1_anomaly_approval_service_pb2
from acme.anomalies.v1 import anomaly_approval_service_pb2_grpc as anomalies_v1_anomaly_approval_service_pb2_grpc
from acme.anomalies.v1 import anomaly_validation_service_pb2 as anomalies_v1_anomaly_validation_service_pb2
from acme.anomalies.v1 import anomaly_validation_service_pb2_grpc as anomalies_v1_anomaly_validation_service_pb2_grpc
from acme.customers.v1 import customer_validation_service_pb2 as customers_v1_customer_validation_service_pb2
from acme.customers.v1 import customer_validation_service_pb2_grpc as customers_v1_customer_validation_service_pb2_grpc
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
from acme.featurestore.v1 import entity_reporting_service_pb2 as featurestore_v1_entity_reporting_service_pb2
from acme.featurestore.v1 import entity_reporting_service_pb2_grpc as featurestore_v1_entity_reporting_service_pb2_grpc
from acme.featurestore.v1 import (
    feature_value_validation_service_pb2 as featurestore_v1_feature_value_validation_service_pb2,
)
from acme.featurestore.v1 import (
    feature_value_validation_service_pb2_grpc as featurestore_v1_feature_value_validation_service_pb2_grpc,
)
from acme.featurestore.v1 import (
    feature_view_calculation_service_pb2 as featurestore_v1_feature_view_calculation_service_pb2,
)
from acme.featurestore.v1 import (
    feature_view_calculation_service_pb2_grpc as featurestore_v1_feature_view_calculation_service_pb2_grpc,
)
from acme.identity.v1 import user_service_pb2 as identity_v1_user_service_pb2
from acme.identity.v1 import user_service_pb2_grpc as identity_v1_user_service_pb2_grpc
from acme.identity.v1 import user_validation_service_pb2 as identity_v1_user_validation_service_pb2
from acme.identity.v1 import user_validation_service_pb2_grpc as identity_v1_user_validation_service_pb2_grpc
from acme.ledger.v1 import ledger_account_query_service_pb2 as ledger_v1_ledger_account_query_service_pb2
from acme.ledger.v1 import ledger_account_query_service_pb2_grpc as ledger_v1_ledger_account_query_service_pb2_grpc
from acme.lineage.v1 import lineage_edge_sync_service_pb2 as lineage_v1_lineage_edge_sync_service_pb2
from acme.lineage.v1 import lineage_edge_sync_service_pb2_grpc as lineage_v1_lineage_edge_sync_service_pb2_grpc
from acme.metrics.v1 import dashboard_history_service_pb2 as metrics_v1_dashboard_history_service_pb2
from acme.metrics.v1 import dashboard_history_service_pb2_grpc as metrics_v1_dashboard_history_service_pb2_grpc
from acme.metrics.v1 import dashboard_validation_service_pb2 as metrics_v1_dashboard_validation_service_pb2
from acme.metrics.v1 import dashboard_validation_service_pb2_grpc as metrics_v1_dashboard_validation_service_pb2_grpc
from acme.metrics.v1 import metric_series_export_service_pb2 as metrics_v1_metric_series_export_service_pb2
from acme.metrics.v1 import metric_series_export_service_pb2_grpc as metrics_v1_metric_series_export_service_pb2_grpc
from acme.modelregistry.v1 import deployment_import_service_pb2 as modelregistry_v1_deployment_import_service_pb2
from acme.modelregistry.v1 import (
    deployment_import_service_pb2_grpc as modelregistry_v1_deployment_import_service_pb2_grpc,
)
from acme.modelregistry.v1 import (
    deployment_validation_service_pb2 as modelregistry_v1_deployment_validation_service_pb2,
)
from acme.modelregistry.v1 import (
    deployment_validation_service_pb2_grpc as modelregistry_v1_deployment_validation_service_pb2_grpc,
)
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
    registered_model_lifecycle_service_pb2 as modelregistry_v1_registered_model_lifecycle_service_pb2,
)
from acme.modelregistry.v1 import (
    registered_model_lifecycle_service_pb2_grpc as modelregistry_v1_registered_model_lifecycle_service_pb2_grpc,
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
from acme.modelregistry.v1 import registered_model_service_pb2 as modelregistry_v1_registered_model_service_pb2
from acme.modelregistry.v1 import (
    registered_model_service_pb2_grpc as modelregistry_v1_registered_model_service_pb2_grpc,
)
from acme.modelregistry.v1 import (
    registered_model_sync_service_pb2 as modelregistry_v1_registered_model_sync_service_pb2,
)
from acme.modelregistry.v1 import (
    registered_model_sync_service_pb2_grpc as modelregistry_v1_registered_model_sync_service_pb2_grpc,
)
from acme.modelregistry.v1 import (
    registered_model_validation_service_pb2 as modelregistry_v1_registered_model_validation_service_pb2,
)
from acme.modelregistry.v1 import (
    registered_model_validation_service_pb2_grpc as modelregistry_v1_registered_model_validation_service_pb2_grpc,
)
from acme.search.v1 import search_index_validation_service_pb2 as search_v1_search_index_validation_service_pb2
from acme.search.v1 import (
    search_index_validation_service_pb2_grpc as search_v1_search_index_validation_service_pb2_grpc,
)


async def deployment_approval_approve_deployment0(
    client: modelregistry_v1_registered_model_reporting_service_pb2_grpc.RegisteredModelReportingServiceStub,
    request: modelregistry_v1_registered_model_reporting_service_pb2.ScheduleRegisteredModelReportRequest,
    timeout: float
) -> modelregistry_v1_registered_model_reporting_service_pb2.ScheduleRegisteredModelReportResponse:
    return await client.ScheduleRegisteredModelReport(request, timeout=timeout)


class DeploymentApprovalDelegateDeploymentApproval0Adapter:
    def __init__(
        self,
        client: customers_v1_customer_validation_service_pb2_grpc.CustomerValidationServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def __call__(
        self,
        request: customers_v1_customer_validation_service_pb2.PreviewCustomerRequest
    ) -> customers_v1_customer_validation_service_pb2.PreviewCustomerResponse:
        return await self.client.PreviewCustomer(request, timeout=self.timeout)


async def deployment_calculation_compare_deployment_options2(
    client: anomalies_v1_anomaly_validation_service_pb2_grpc.AnomalyValidationServiceStub,
    request: anomalies_v1_anomaly_validation_service_pb2.ScoreAnomalyRequest,
    timeout: float
) -> anomalies_v1_anomaly_validation_service_pb2.ScoreAnomalyResponse:
    return await client.ScoreAnomaly(request, timeout=timeout)


async def deployment_import_map_deployment_import_columns1(
    client: modelregistry_v1_registered_model_calculation_service_pb2_grpc.RegisteredModelCalculationServiceStub,
    request: modelregistry_v1_registered_model_calculation_service_pb2.QuoteRegisteredModelRequest,
    timeout: float
) -> modelregistry_v1_registered_model_calculation_service_pb2.QuoteRegisteredModelResponse:
    return await client.QuoteRegisteredModel(request, timeout=timeout)


async def deployment_lifecycle_reinstate_deployment2(
    client: anomalies_v1_anomaly_approval_service_pb2_grpc.AnomalyApprovalServiceStub,
    request: anomalies_v1_anomaly_approval_service_pb2.RejectAnomalyRequest,
    timeout: float
) -> anomalies_v1_anomaly_approval_service_pb2.RejectAnomalyResponse:
    return await client.RejectAnomaly(request, timeout=timeout)


class DeploymentLifecycleRenewDeployment0Port(Protocol):
    async def execute(
        self,
        request: modelregistry_v1_deployment_import_service_pb2.RetryDeploymentImportRequest
    ) -> modelregistry_v1_deployment_import_service_pb2.RetryDeploymentImportResponse: ...


class DeploymentLifecycleRenewDeployment0Adapter:
    def __init__(
        self,
        client: modelregistry_v1_deployment_import_service_pb2_grpc.DeploymentImportServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def execute(
        self,
        request: modelregistry_v1_deployment_import_service_pb2.RetryDeploymentImportRequest
    ) -> modelregistry_v1_deployment_import_service_pb2.RetryDeploymentImportResponse:
        return await self.client.RetryDeploymentImport(request, timeout=self.timeout)


class DeploymentLifecycleScheduleDeploymentExpiry0Adapter:
    def __init__(
        self,
        client: ledger_v1_ledger_account_query_service_pb2_grpc.LedgerAccountQueryServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def __call__(
        self,
        request: ledger_v1_ledger_account_query_service_pb2.SuggestLedgerAccountsRequest
    ) -> ledger_v1_ledger_account_query_service_pb2.SuggestLedgerAccountsResponse:
        return await self.client.SuggestLedgerAccounts(request, timeout=self.timeout)


class DeploymentReportingScheduleDeploymentReport0Port(Protocol):
    async def execute(
        self,
        request: modelregistry_v1_registered_model_service_pb2.CreateRegisteredModelRequest
    ) -> modelregistry_v1_registered_model_service_pb2.CreateRegisteredModelResponse: ...


class DeploymentReportingScheduleDeploymentReport0Adapter:
    def __init__(
        self,
        client: modelregistry_v1_registered_model_service_pb2_grpc.RegisteredModelServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def execute(
        self,
        request: modelregistry_v1_registered_model_service_pb2.CreateRegisteredModelRequest
    ) -> modelregistry_v1_registered_model_service_pb2.CreateRegisteredModelResponse:
        return await self.client.CreateRegisteredModel(request, timeout=self.timeout)


class DeploymentReportingScheduleDeploymentReport2Adapter:
    def __init__(
        self,
        client: modelregistry_v1_registered_model_validation_service_pb2_grpc.RegisteredModelValidationServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def __call__(
        self,
        request: modelregistry_v1_registered_model_validation_service_pb2.LintRegisteredModelsRequest
    ) -> modelregistry_v1_registered_model_validation_service_pb2.LintRegisteredModelsResponse:
        return await self.client.LintRegisteredModels(request, timeout=self.timeout)


class DeploymentSyncResolveDeploymentConflict1Port(Protocol):
    async def execute(
        self,
        request: modelregistry_v1_model_version_validation_service_pb2.ValidateModelVersionRequest
    ) -> modelregistry_v1_model_version_validation_service_pb2.ValidateModelVersionResponse: ...


class DeploymentSyncResolveDeploymentConflict1Adapter:
    def __init__(
        self,
        client: modelregistry_v1_model_version_validation_service_pb2_grpc.ModelVersionValidationServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def execute(
        self,
        request: modelregistry_v1_model_version_validation_service_pb2.ValidateModelVersionRequest
    ) -> modelregistry_v1_model_version_validation_service_pb2.ValidateModelVersionResponse:
        return await self.client.ValidateModelVersion(request, timeout=self.timeout)


async def deployment_validation_normalize_deployment0(
    client: modelregistry_v1_model_version_validation_service_pb2_grpc.ModelVersionValidationServiceStub,
    request: modelregistry_v1_model_version_validation_service_pb2.ExplainModelVersionDecisionRequest,
    timeout: float
) -> modelregistry_v1_model_version_validation_service_pb2.ExplainModelVersionDecisionResponse:
    return await client.ExplainModelVersionDecision(request, timeout=timeout)


class DeploymentValidationScoreDeployment0Adapter:
    def __init__(
        self,
        client: search_v1_search_index_validation_service_pb2_grpc.SearchIndexValidationServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def __call__(
        self,
        request: search_v1_search_index_validation_service_pb2.ScoreSearchIndexRequest
    ) -> search_v1_search_index_validation_service_pb2.ScoreSearchIndexResponse:
        return await self.client.ScoreSearchIndex(request, timeout=self.timeout)


async def deployment_workflow_signal_deployment_workflow1(
    client: customers_v1_household_validation_service_pb2_grpc.HouseholdValidationServiceStub,
    request: customers_v1_household_validation_service_pb2.CheckHouseholdEligibilityRequest,
    timeout: float
) -> customers_v1_household_validation_service_pb2.CheckHouseholdEligibilityResponse:
    return await client.CheckHouseholdEligibility(request, timeout=timeout)


class DeploymentWorkflowStartDeploymentWorkflow1Port(Protocol):
    async def execute(
        self,
        request: modelregistry_v1_deployment_import_service_pb2.MapDeploymentImportColumnsRequest
    ) -> modelregistry_v1_deployment_import_service_pb2.MapDeploymentImportColumnsResponse: ...


class DeploymentWorkflowStartDeploymentWorkflow1Adapter:
    def __init__(
        self,
        client: modelregistry_v1_deployment_import_service_pb2_grpc.DeploymentImportServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def execute(
        self,
        request: modelregistry_v1_deployment_import_service_pb2.MapDeploymentImportColumnsRequest
    ) -> modelregistry_v1_deployment_import_service_pb2.MapDeploymentImportColumnsResponse:
        return await self.client.MapDeploymentImportColumns(request, timeout=self.timeout)


class DeploymentWorkflowStartDeploymentWorkflow3Adapter:
    def __init__(
        self,
        client: modelregistry_v1_model_version_reporting_service_pb2_grpc.ModelVersionReportingServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def __call__(
        self,
        request: modelregistry_v1_model_version_reporting_service_pb2.ScheduleModelVersionReportRequest
    ) -> modelregistry_v1_model_version_reporting_service_pb2.ScheduleModelVersionReportResponse:
        return await self.client.ScheduleModelVersionReport(request, timeout=self.timeout)


class ModelVersionCalculationExplainModelVersionCalculation0Port(Protocol):
    async def execute(
        self,
        request: modelregistry_v1_registered_model_calculation_service_pb2.EstimateRegisteredModelRequest
    ) -> modelregistry_v1_registered_model_calculation_service_pb2.EstimateRegisteredModelResponse: ...


class ModelVersionCalculationExplainModelVersionCalculation0Adapter:
    def __init__(
        self,
        client: modelregistry_v1_registered_model_calculation_service_pb2_grpc.RegisteredModelCalculationServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def execute(
        self,
        request: modelregistry_v1_registered_model_calculation_service_pb2.EstimateRegisteredModelRequest
    ) -> modelregistry_v1_registered_model_calculation_service_pb2.EstimateRegisteredModelResponse:
        return await self.client.EstimateRegisteredModel(request, timeout=self.timeout)


class ModelVersionCalculationExplainModelVersionCalculation2Adapter:
    def __init__(
        self,
        client: metrics_v1_dashboard_history_service_pb2_grpc.DashboardHistoryServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def __call__(
        self,
        request: metrics_v1_dashboard_history_service_pb2.RecordDashboardVersionRequest
    ) -> metrics_v1_dashboard_history_service_pb2.RecordDashboardVersionResponse:
        return await self.client.RecordDashboardVersion(request, timeout=self.timeout)


class ModelVersionQueryPeekModelVersion1Port(Protocol):
    async def execute(
        self,
        request: featurestore_v1_feature_view_calculation_service_pb2.CalculateFeatureViewRequest
    ) -> featurestore_v1_feature_view_calculation_service_pb2.CalculateFeatureViewResponse: ...


class ModelVersionQueryPeekModelVersion1Adapter:
    def __init__(
        self,
        client: featurestore_v1_feature_view_calculation_service_pb2_grpc.FeatureViewCalculationServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def execute(
        self,
        request: featurestore_v1_feature_view_calculation_service_pb2.CalculateFeatureViewRequest
    ) -> featurestore_v1_feature_view_calculation_service_pb2.CalculateFeatureViewResponse:
        return await self.client.CalculateFeatureView(request, timeout=self.timeout)


class ModelVersionQuerySummarizeModelVersions1Adapter:
    def __init__(
        self,
        client: modelregistry_v1_deployment_validation_service_pb2_grpc.DeploymentValidationServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def __call__(
        self,
        request: modelregistry_v1_deployment_validation_service_pb2.NormalizeDeploymentRequest
    ) -> modelregistry_v1_deployment_validation_service_pb2.NormalizeDeploymentResponse:
        return await self.client.NormalizeDeployment(request, timeout=self.timeout)


async def model_version_reporting_stream_model_version_metrics2(
    client: modelregistry_v1_model_version_sync_service_pb2_grpc.ModelVersionSyncServiceStub,
    request: modelregistry_v1_model_version_sync_service_pb2.ReconcileModelVersionsRequest,
    timeout: float
) -> modelregistry_v1_model_version_sync_service_pb2.ReconcileModelVersionsResponse:
    return await client.ReconcileModelVersions(request, timeout=timeout)


class ModelVersionSyncPullModelVersions0Adapter:
    def __init__(
        self,
        client: featurestore_v1_entity_reporting_service_pb2_grpc.EntityReportingServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def __call__(
        self,
        request: featurestore_v1_entity_reporting_service_pb2.CountEntityTotalsRequest
    ) -> featurestore_v1_entity_reporting_service_pb2.CountEntityTotalsResponse:
        return await self.client.CountEntityTotals(request, timeout=self.timeout)


async def model_version_sync_sync_model_versions0(
    client: modelregistry_v1_registered_model_query_service_pb2_grpc.RegisteredModelQueryServiceStub,
    request: modelregistry_v1_registered_model_query_service_pb2.ResolveRegisteredModelsRequest,
    timeout: float
) -> modelregistry_v1_registered_model_query_service_pb2.ResolveRegisteredModelsResponse:
    return await client.ResolveRegisteredModels(request, timeout=timeout)


class ModelVersionSyncSyncModelVersions2Port(Protocol):
    async def execute(
        self,
        request: ledger_v1_ledger_account_query_service_pb2.ResolveLedgerAccountsRequest
    ) -> ledger_v1_ledger_account_query_service_pb2.ResolveLedgerAccountsResponse: ...


class ModelVersionSyncSyncModelVersions2Adapter:
    def __init__(
        self,
        client: ledger_v1_ledger_account_query_service_pb2_grpc.LedgerAccountQueryServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def execute(
        self,
        request: ledger_v1_ledger_account_query_service_pb2.ResolveLedgerAccountsRequest
    ) -> ledger_v1_ledger_account_query_service_pb2.ResolveLedgerAccountsResponse:
        return await self.client.ResolveLedgerAccounts(request, timeout=self.timeout)


async def model_version_validation_preview_model_version1(
    client: identity_v1_user_service_pb2_grpc.UserServiceStub,
    request: identity_v1_user_service_pb2.SearchUsersRequest,
    timeout: float
) -> identity_v1_user_service_pb2.SearchUsersResponse:
    return await client.SearchUsers(request, timeout=timeout)


class ModelVersionValidationScoreModelVersion1Adapter:
    def __init__(
        self,
        client: modelregistry_v1_model_version_calculation_service_pb2_grpc.ModelVersionCalculationServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def __call__(
        self,
        request: modelregistry_v1_model_version_calculation_service_pb2.CalculateModelVersionRequest
    ) -> modelregistry_v1_model_version_calculation_service_pb2.CalculateModelVersionResponse:
        return await self.client.CalculateModelVersion(request, timeout=self.timeout)


class ModelVersionWorkflowPauseModelVersionWorkflow3Port(Protocol):
    async def execute(
        self,
        request: modelregistry_v1_registered_model_sync_service_pb2.SyncRegisteredModelsRequest
    ) -> modelregistry_v1_registered_model_sync_service_pb2.SyncRegisteredModelsResponse: ...


class ModelVersionWorkflowPauseModelVersionWorkflow3Adapter:
    def __init__(
        self,
        client: modelregistry_v1_registered_model_sync_service_pb2_grpc.RegisteredModelSyncServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def execute(
        self,
        request: modelregistry_v1_registered_model_sync_service_pb2.SyncRegisteredModelsRequest
    ) -> modelregistry_v1_registered_model_sync_service_pb2.SyncRegisteredModelsResponse:
        return await self.client.SyncRegisteredModels(request, timeout=self.timeout)


async def registered_model_approval_get_registered_model_approval_status1(
    client: lineage_v1_lineage_edge_sync_service_pb2_grpc.LineageEdgeSyncServiceStub,
    request: lineage_v1_lineage_edge_sync_service_pb2.ResolveLineageEdgeConflictRequest,
    timeout: float
) -> lineage_v1_lineage_edge_sync_service_pb2.ResolveLineageEdgeConflictResponse:
    return await client.ResolveLineageEdgeConflict(request, timeout=timeout)


class RegisteredModelApprovalRecallRegisteredModel0Port(Protocol):
    async def execute(
        self,
        request: modelregistry_v1_model_version_sync_service_pb2.PushModelVersionRequest
    ) -> modelregistry_v1_model_version_sync_service_pb2.PushModelVersionResponse: ...


class RegisteredModelApprovalRecallRegisteredModel0Adapter:
    def __init__(
        self,
        client: modelregistry_v1_model_version_sync_service_pb2_grpc.ModelVersionSyncServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def execute(
        self,
        request: modelregistry_v1_model_version_sync_service_pb2.PushModelVersionRequest
    ) -> modelregistry_v1_model_version_sync_service_pb2.PushModelVersionResponse:
        return await self.client.PushModelVersion(request, timeout=self.timeout)


class RegisteredModelApprovalRejectRegisteredModel0Adapter:
    def __init__(
        self,
        client: modelregistry_v1_registered_model_lifecycle_service_pb2_grpc.RegisteredModelLifecycleServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def __call__(
        self,
        request: modelregistry_v1_registered_model_lifecycle_service_pb2.ExpireRegisteredModelRequest
    ) -> modelregistry_v1_registered_model_lifecycle_service_pb2.ExpireRegisteredModelResponse:
        return await self.client.ExpireRegisteredModel(request, timeout=self.timeout)


class RegisteredModelCalculationRecalculateRegisteredModels1Port(Protocol):
    async def execute(
        self,
        request: identity_v1_user_validation_service_pb2.ScoreUserRequest
    ) -> identity_v1_user_validation_service_pb2.ScoreUserResponse: ...


class RegisteredModelCalculationRecalculateRegisteredModels1Adapter:
    def __init__(
        self,
        client: identity_v1_user_validation_service_pb2_grpc.UserValidationServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def execute(
        self,
        request: identity_v1_user_validation_service_pb2.ScoreUserRequest
    ) -> identity_v1_user_validation_service_pb2.ScoreUserResponse:
        return await self.client.ScoreUser(request, timeout=self.timeout)


async def registered_model_lifecycle_suspend_registered_model0(
    client: modelregistry_v1_model_version_reporting_service_pb2_grpc.ModelVersionReportingServiceStub,
    request: modelregistry_v1_model_version_reporting_service_pb2.ShareModelVersionReportRequest,
    timeout: float
) -> modelregistry_v1_model_version_reporting_service_pb2.ShareModelVersionReportResponse:
    return await client.ShareModelVersionReport(request, timeout=timeout)


class RegisteredModelLifecycleTerminateRegisteredModel0Port(Protocol):
    async def execute(
        self,
        request: metrics_v1_metric_series_export_service_pb2.ShareMetricSeriesExportRequest
    ) -> metrics_v1_metric_series_export_service_pb2.ShareMetricSeriesExportResponse: ...


class RegisteredModelLifecycleTerminateRegisteredModel0Adapter:
    def __init__(
        self,
        client: metrics_v1_metric_series_export_service_pb2_grpc.MetricSeriesExportServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def execute(
        self,
        request: metrics_v1_metric_series_export_service_pb2.ShareMetricSeriesExportRequest
    ) -> metrics_v1_metric_series_export_service_pb2.ShareMetricSeriesExportResponse:
        return await self.client.ShareMetricSeriesExport(request, timeout=self.timeout)


class RegisteredModelLifecycleTerminateRegisteredModel2Adapter:
    def __init__(
        self,
        client: modelregistry_v1_registered_model_sync_service_pb2_grpc.RegisteredModelSyncServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def __call__(
        self,
        request: modelregistry_v1_registered_model_sync_service_pb2.ReconcileRegisteredModelsRequest
    ) -> modelregistry_v1_registered_model_sync_service_pb2.ReconcileRegisteredModelsResponse:
        return await self.client.ReconcileRegisteredModels(request, timeout=self.timeout)


async def registered_model_reporting_delete_registered_model_report3(
    client: modelregistry_v1_model_version_calculation_service_pb2_grpc.ModelVersionCalculationServiceStub,
    request: modelregistry_v1_model_version_calculation_service_pb2.RecalculateModelVersionsRequest,
    timeout: float
) -> modelregistry_v1_model_version_calculation_service_pb2.RecalculateModelVersionsResponse:
    return await client.RecalculateModelVersions(request, timeout=timeout)


class RegisteredModelReportingGenerateRegisteredModelReport1Port(Protocol):
    async def execute(
        self,
        request: modelregistry_v1_registered_model_sync_service_pb2.ReconcileRegisteredModelsRequest
    ) -> modelregistry_v1_registered_model_sync_service_pb2.ReconcileRegisteredModelsResponse: ...


class RegisteredModelReportingGenerateRegisteredModelReport1Adapter:
    def __init__(
        self,
        client: modelregistry_v1_registered_model_sync_service_pb2_grpc.RegisteredModelSyncServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def execute(
        self,
        request: modelregistry_v1_registered_model_sync_service_pb2.ReconcileRegisteredModelsRequest
    ) -> modelregistry_v1_registered_model_sync_service_pb2.ReconcileRegisteredModelsResponse:
        return await self.client.ReconcileRegisteredModels(request, timeout=self.timeout)


async def registered_model_delete_registered_model0(
    client: featureflags_v1_feature_flag_validation_service_pb2_grpc.FeatureFlagValidationServiceStub,
    request: featureflags_v1_feature_flag_validation_service_pb2.LintFeatureFlagsRequest,
    timeout: float
) -> featureflags_v1_feature_flag_validation_service_pb2.LintFeatureFlagsResponse:
    return await client.LintFeatureFlags(request, timeout=timeout)


class RegisteredModelUpdateRegisteredModel0Adapter:
    def __init__(
        self,
        client: modelregistry_v1_registered_model_calculation_service_pb2_grpc.RegisteredModelCalculationServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def __call__(
        self,
        request: modelregistry_v1_registered_model_calculation_service_pb2.RecalculateRegisteredModelsRequest
    ) -> modelregistry_v1_registered_model_calculation_service_pb2.RecalculateRegisteredModelsResponse:
        return await self.client.RecalculateRegisteredModels(request, timeout=self.timeout)


async def registered_model_validation_validate_registered_model0(
    client: metrics_v1_dashboard_validation_service_pb2_grpc.DashboardValidationServiceStub,
    request: metrics_v1_dashboard_validation_service_pb2.CheckDashboardEligibilityRequest,
    timeout: float
) -> metrics_v1_dashboard_validation_service_pb2.CheckDashboardEligibilityResponse:
    return await client.CheckDashboardEligibility(request, timeout=timeout)


class RegisteredModelValidationValidateRegisteredModel2Port(Protocol):
    async def execute(
        self,
        request: featurestore_v1_feature_value_validation_service_pb2.ExplainFeatureValueDecisionRequest
    ) -> featurestore_v1_feature_value_validation_service_pb2.ExplainFeatureValueDecisionResponse: ...


class RegisteredModelValidationValidateRegisteredModel2Adapter:
    def __init__(
        self,
        client: featurestore_v1_feature_value_validation_service_pb2_grpc.FeatureValueValidationServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def execute(
        self,
        request: featurestore_v1_feature_value_validation_service_pb2.ExplainFeatureValueDecisionRequest
    ) -> featurestore_v1_feature_value_validation_service_pb2.ExplainFeatureValueDecisionResponse:
        return await self.client.ExplainFeatureValueDecision(request, timeout=self.timeout)


class RegisteredModelWorkflowAdvanceRegisteredModelWorkflow1Adapter:
    def __init__(
        self,
        client: ledger_v1_ledger_account_query_service_pb2_grpc.LedgerAccountQueryServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def __call__(
        self,
        request: ledger_v1_ledger_account_query_service_pb2.BrowseLedgerAccountsRequest
    ) -> ledger_v1_ledger_account_query_service_pb2.BrowseLedgerAccountsResponse:
        return await self.client.BrowseLedgerAccounts(request, timeout=self.timeout)


async def registered_model_workflow_start_registered_model_workflow1(
    client: modelregistry_v1_model_version_approval_service_pb2_grpc.ModelVersionApprovalServiceStub,
    request: modelregistry_v1_model_version_approval_service_pb2.EscalateModelVersionRequest,
    timeout: float
) -> modelregistry_v1_model_version_approval_service_pb2.EscalateModelVersionResponse:
    return await client.EscalateModelVersion(request, timeout=timeout)
