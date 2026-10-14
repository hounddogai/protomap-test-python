"""Transport adapters used by pipelines workflows."""

from __future__ import annotations

from typing import Protocol

from acme.authorization.v1 import (
    access_policy_validation_service_pb2 as authorization_v1_access_policy_validation_service_pb2,
)
from acme.authorization.v1 import (
    access_policy_validation_service_pb2_grpc as authorization_v1_access_policy_validation_service_pb2_grpc,
)
from acme.concessions.v1 import concession_stand_service_pb2 as concessions_v1_concession_stand_service_pb2
from acme.concessions.v1 import concession_stand_service_pb2_grpc as concessions_v1_concession_stand_service_pb2_grpc
from acme.documents.v1 import document_query_service_pb2 as documents_v1_document_query_service_pb2
from acme.documents.v1 import document_query_service_pb2_grpc as documents_v1_document_query_service_pb2_grpc
from acme.drivers.v1 import driver_calculation_service_pb2 as drivers_v1_driver_calculation_service_pb2
from acme.drivers.v1 import driver_calculation_service_pb2_grpc as drivers_v1_driver_calculation_service_pb2_grpc
from acme.featureflags.v1 import (
    feature_flag_validation_service_pb2 as featureflags_v1_feature_flag_validation_service_pb2,
)
from acme.featureflags.v1 import (
    feature_flag_validation_service_pb2_grpc as featureflags_v1_feature_flag_validation_service_pb2_grpc,
)
from acme.featurestore.v1 import entity_approval_service_pb2 as featurestore_v1_entity_approval_service_pb2
from acme.featurestore.v1 import entity_approval_service_pb2_grpc as featurestore_v1_entity_approval_service_pb2_grpc
from acme.featurestore.v1 import entity_sync_service_pb2 as featurestore_v1_entity_sync_service_pb2
from acme.featurestore.v1 import entity_sync_service_pb2_grpc as featurestore_v1_entity_sync_service_pb2_grpc
from acme.featurestore.v1 import feature_view_approval_service_pb2 as featurestore_v1_feature_view_approval_service_pb2
from acme.featurestore.v1 import (
    feature_view_approval_service_pb2_grpc as featurestore_v1_feature_view_approval_service_pb2_grpc,
)
from acme.featurestore.v1 import (
    feature_view_calculation_service_pb2 as featurestore_v1_feature_view_calculation_service_pb2,
)
from acme.featurestore.v1 import (
    feature_view_calculation_service_pb2_grpc as featurestore_v1_feature_view_calculation_service_pb2_grpc,
)
from acme.identity.v1 import user_query_service_pb2 as identity_v1_user_query_service_pb2
from acme.identity.v1 import user_query_service_pb2_grpc as identity_v1_user_query_service_pb2_grpc
from acme.identity.v1 import user_service_pb2 as identity_v1_user_service_pb2
from acme.identity.v1 import user_service_pb2_grpc as identity_v1_user_service_pb2_grpc
from acme.labeling.v1 import label_set_validation_service_pb2 as labeling_v1_label_set_validation_service_pb2
from acme.labeling.v1 import label_set_validation_service_pb2_grpc as labeling_v1_label_set_validation_service_pb2_grpc
from acme.labeling.v1 import labeling_task_service_pb2 as labeling_v1_labeling_task_service_pb2
from acme.labeling.v1 import labeling_task_service_pb2_grpc as labeling_v1_labeling_task_service_pb2_grpc
from acme.ledger.v1 import ledger_account_query_service_pb2 as ledger_v1_ledger_account_query_service_pb2
from acme.ledger.v1 import ledger_account_query_service_pb2_grpc as ledger_v1_ledger_account_query_service_pb2_grpc
from acme.ledger.v1 import ledger_account_service_pb2 as ledger_v1_ledger_account_service_pb2
from acme.ledger.v1 import ledger_account_service_pb2_grpc as ledger_v1_ledger_account_service_pb2_grpc
from acme.lineage.v1 import lineage_edge_calculation_service_pb2 as lineage_v1_lineage_edge_calculation_service_pb2
from acme.lineage.v1 import (
    lineage_edge_calculation_service_pb2_grpc as lineage_v1_lineage_edge_calculation_service_pb2_grpc,
)
from acme.metrics.v1 import dashboard_sync_service_pb2 as metrics_v1_dashboard_sync_service_pb2
from acme.metrics.v1 import dashboard_sync_service_pb2_grpc as metrics_v1_dashboard_sync_service_pb2_grpc
from acme.metrics.v1 import metric_alert_query_service_pb2 as metrics_v1_metric_alert_query_service_pb2
from acme.metrics.v1 import metric_alert_query_service_pb2_grpc as metrics_v1_metric_alert_query_service_pb2_grpc
from acme.metrics.v1 import metric_series_export_service_pb2 as metrics_v1_metric_series_export_service_pb2
from acme.metrics.v1 import metric_series_export_service_pb2_grpc as metrics_v1_metric_series_export_service_pb2_grpc
from acme.modelregistry.v1 import deployment_approval_service_pb2 as modelregistry_v1_deployment_approval_service_pb2
from acme.modelregistry.v1 import (
    deployment_approval_service_pb2_grpc as modelregistry_v1_deployment_approval_service_pb2_grpc,
)
from acme.modelregistry.v1 import deployment_import_service_pb2 as modelregistry_v1_deployment_import_service_pb2
from acme.modelregistry.v1 import (
    deployment_import_service_pb2_grpc as modelregistry_v1_deployment_import_service_pb2_grpc,
)
from acme.modelregistry.v1 import (
    model_version_reporting_service_pb2 as modelregistry_v1_model_version_reporting_service_pb2,
)
from acme.modelregistry.v1 import (
    model_version_reporting_service_pb2_grpc as modelregistry_v1_model_version_reporting_service_pb2_grpc,
)
from acme.notifications.v1 import notification_service_pb2 as notifications_v1_notification_service_pb2
from acme.notifications.v1 import notification_service_pb2_grpc as notifications_v1_notification_service_pb2_grpc
from acme.pipelines.v1 import pipeline_approval_service_pb2 as pipelines_v1_pipeline_approval_service_pb2
from acme.pipelines.v1 import pipeline_approval_service_pb2_grpc as pipelines_v1_pipeline_approval_service_pb2_grpc
from acme.pipelines.v1 import pipeline_calculation_service_pb2 as pipelines_v1_pipeline_calculation_service_pb2
from acme.pipelines.v1 import (
    pipeline_calculation_service_pb2_grpc as pipelines_v1_pipeline_calculation_service_pb2_grpc,
)
from acme.pipelines.v1 import pipeline_query_service_pb2 as pipelines_v1_pipeline_query_service_pb2
from acme.pipelines.v1 import pipeline_query_service_pb2_grpc as pipelines_v1_pipeline_query_service_pb2_grpc
from acme.pipelines.v1 import pipeline_run_calculation_service_pb2 as pipelines_v1_pipeline_run_calculation_service_pb2
from acme.pipelines.v1 import (
    pipeline_run_calculation_service_pb2_grpc as pipelines_v1_pipeline_run_calculation_service_pb2_grpc,
)
from acme.pipelines.v1 import pipeline_run_import_service_pb2 as pipelines_v1_pipeline_run_import_service_pb2
from acme.pipelines.v1 import pipeline_run_import_service_pb2_grpc as pipelines_v1_pipeline_run_import_service_pb2_grpc
from acme.pipelines.v1 import pipeline_run_reporting_service_pb2 as pipelines_v1_pipeline_run_reporting_service_pb2
from acme.pipelines.v1 import (
    pipeline_run_reporting_service_pb2_grpc as pipelines_v1_pipeline_run_reporting_service_pb2_grpc,
)
from acme.pipelines.v1 import (
    pipeline_step_calculation_service_pb2 as pipelines_v1_pipeline_step_calculation_service_pb2,
)
from acme.pipelines.v1 import (
    pipeline_step_calculation_service_pb2_grpc as pipelines_v1_pipeline_step_calculation_service_pb2_grpc,
)
from acme.pipelines.v1 import pipeline_step_export_service_pb2 as pipelines_v1_pipeline_step_export_service_pb2
from acme.pipelines.v1 import (
    pipeline_step_export_service_pb2_grpc as pipelines_v1_pipeline_step_export_service_pb2_grpc,
)
from acme.pipelines.v1 import pipeline_sync_service_pb2 as pipelines_v1_pipeline_sync_service_pb2
from acme.pipelines.v1 import pipeline_sync_service_pb2_grpc as pipelines_v1_pipeline_sync_service_pb2_grpc
from acme.pipelines.v1 import pipeline_validation_service_pb2 as pipelines_v1_pipeline_validation_service_pb2
from acme.pipelines.v1 import pipeline_validation_service_pb2_grpc as pipelines_v1_pipeline_validation_service_pb2_grpc
from acme.prescriptions.v1 import prescription_query_service_pb2 as prescriptions_v1_prescription_query_service_pb2
from acme.prescriptions.v1 import (
    prescription_query_service_pb2_grpc as prescriptions_v1_prescription_query_service_pb2_grpc,
)
from acme.recruiting.v1 import job_opening_service_pb2 as recruiting_v1_job_opening_service_pb2
from acme.recruiting.v1 import job_opening_service_pb2_grpc as recruiting_v1_job_opening_service_pb2_grpc
from acme.search.v1 import search_index_service_pb2 as search_v1_search_index_service_pb2
from acme.search.v1 import search_index_service_pb2_grpc as search_v1_search_index_service_pb2_grpc
from acme.telematics.v1 import telemetry_reading_query_service_pb2 as telematics_v1_telemetry_reading_query_service_pb2
from acme.telematics.v1 import (
    telemetry_reading_query_service_pb2_grpc as telematics_v1_telemetry_reading_query_service_pb2_grpc,
)
from acme.yards.v1 import yard_query_service_pb2 as yards_v1_yard_query_service_pb2
from acme.yards.v1 import yard_query_service_pb2_grpc as yards_v1_yard_query_service_pb2_grpc


class PipelineApprovalDelegatePipelineApproval0Port(Protocol):
    async def execute(
        self,
        request: metrics_v1_metric_series_export_service_pb2.ScheduleMetricSeriesExportRequest
    ) -> metrics_v1_metric_series_export_service_pb2.ScheduleMetricSeriesExportResponse: ...


class PipelineApprovalDelegatePipelineApproval0Adapter:
    def __init__(
        self,
        client: metrics_v1_metric_series_export_service_pb2_grpc.MetricSeriesExportServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def execute(
        self,
        request: metrics_v1_metric_series_export_service_pb2.ScheduleMetricSeriesExportRequest
    ) -> metrics_v1_metric_series_export_service_pb2.ScheduleMetricSeriesExportResponse:
        return await self.client.ScheduleMetricSeriesExport(request, timeout=self.timeout)


class PipelineApprovalDelegatePipelineApproval2Adapter:
    def __init__(
        self,
        client: pipelines_v1_pipeline_calculation_service_pb2_grpc.PipelineCalculationServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def __call__(
        self,
        request: pipelines_v1_pipeline_calculation_service_pb2.ExplainPipelineCalculationRequest
    ) -> pipelines_v1_pipeline_calculation_service_pb2.ExplainPipelineCalculationResponse:
        return await self.client.ExplainPipelineCalculation(request, timeout=self.timeout)


async def pipeline_calculation_calculate_pipeline0(
    client: concessions_v1_concession_stand_service_pb2_grpc.ConcessionStandServiceStub,
    request: concessions_v1_concession_stand_service_pb2.CreateConcessionStandRequest,
    timeout: float
) -> concessions_v1_concession_stand_service_pb2.CreateConcessionStandResponse:
    return await client.CreateConcessionStand(request, timeout=timeout)


class PipelineCalculationCalculatePipeline2Port(Protocol):
    async def execute(
        self,
        request: telematics_v1_telemetry_reading_query_service_pb2.FindTelemetryReadingsRequest
    ) -> telematics_v1_telemetry_reading_query_service_pb2.FindTelemetryReadingsResponse: ...


class PipelineCalculationCalculatePipeline2Adapter:
    def __init__(
        self,
        client: telematics_v1_telemetry_reading_query_service_pb2_grpc.TelemetryReadingQueryServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def execute(
        self,
        request: telematics_v1_telemetry_reading_query_service_pb2.FindTelemetryReadingsRequest
    ) -> telematics_v1_telemetry_reading_query_service_pb2.FindTelemetryReadingsResponse:
        return await self.client.FindTelemetryReadings(request, timeout=self.timeout)


class PipelineCalculationComparePipelineOptions0Adapter:
    def __init__(
        self,
        client: metrics_v1_metric_alert_query_service_pb2_grpc.MetricAlertQueryServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def __call__(
        self,
        request: metrics_v1_metric_alert_query_service_pb2.ResolveMetricAlertsRequest
    ) -> metrics_v1_metric_alert_query_service_pb2.ResolveMetricAlertsResponse:
        return await self.client.ResolveMetricAlerts(request, timeout=self.timeout)


class PipelineLifecycleExpirePipeline1Adapter:
    def __init__(
        self,
        client: metrics_v1_dashboard_sync_service_pb2_grpc.DashboardSyncServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def __call__(
        self,
        request: metrics_v1_dashboard_sync_service_pb2.ResolveDashboardConflictRequest
    ) -> metrics_v1_dashboard_sync_service_pb2.ResolveDashboardConflictResponse:
        return await self.client.ResolveDashboardConflict(request, timeout=self.timeout)


class PipelineQueryExportPipelines0Port(Protocol):
    async def execute(
        self,
        request: authorization_v1_access_policy_validation_service_pb2.NormalizeAccessPolicyRequest
    ) -> authorization_v1_access_policy_validation_service_pb2.NormalizeAccessPolicyResponse: ...


class PipelineQueryExportPipelines0Adapter:
    def __init__(
        self,
        client: authorization_v1_access_policy_validation_service_pb2_grpc.AccessPolicyValidationServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def execute(
        self,
        request: authorization_v1_access_policy_validation_service_pb2.NormalizeAccessPolicyRequest
    ) -> authorization_v1_access_policy_validation_service_pb2.NormalizeAccessPolicyResponse:
        return await self.client.NormalizeAccessPolicy(request, timeout=self.timeout)


async def pipeline_reporting_generate_pipeline_report0(
    client: identity_v1_user_query_service_pb2_grpc.UserQueryServiceStub,
    request: identity_v1_user_query_service_pb2.ResolveUsersRequest,
    timeout: float
) -> identity_v1_user_query_service_pb2.ResolveUsersResponse:
    return await client.ResolveUsers(request, timeout=timeout)


class PipelineReportingSchedulePipelineReport1Port(Protocol):
    async def execute(
        self,
        request: pipelines_v1_pipeline_run_import_service_pb2.RetryPipelineRunImportRequest
    ) -> pipelines_v1_pipeline_run_import_service_pb2.RetryPipelineRunImportResponse: ...


class PipelineReportingSchedulePipelineReport1Adapter:
    def __init__(
        self,
        client: pipelines_v1_pipeline_run_import_service_pb2_grpc.PipelineRunImportServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def execute(
        self,
        request: pipelines_v1_pipeline_run_import_service_pb2.RetryPipelineRunImportRequest
    ) -> pipelines_v1_pipeline_run_import_service_pb2.RetryPipelineRunImportResponse:
        return await self.client.RetryPipelineRunImport(request, timeout=self.timeout)


class PipelineReportingSharePipelineReport0Adapter:
    def __init__(
        self,
        client: ledger_v1_ledger_account_query_service_pb2_grpc.LedgerAccountQueryServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def __call__(
        self,
        request: ledger_v1_ledger_account_query_service_pb2.CountLedgerAccountsRequest
    ) -> ledger_v1_ledger_account_query_service_pb2.CountLedgerAccountsResponse:
        return await self.client.CountLedgerAccounts(request, timeout=self.timeout)


async def pipeline_run_approval_escalate_pipeline_run1(
    client: notifications_v1_notification_service_pb2_grpc.NotificationServiceStub,
    request: notifications_v1_notification_service_pb2.CreateNotificationRequest,
    timeout: float
) -> notifications_v1_notification_service_pb2.CreateNotificationResponse:
    return await client.CreateNotification(request, timeout=timeout)


class PipelineRunApprovalListPendingPipelineRuns1Port(Protocol):
    async def execute(
        self,
        request: featurestore_v1_entity_sync_service_pb2.SyncEntitiesRequest
    ) -> featurestore_v1_entity_sync_service_pb2.SyncEntitiesResponse: ...


class PipelineRunApprovalListPendingPipelineRuns1Adapter:
    def __init__(
        self,
        client: featurestore_v1_entity_sync_service_pb2_grpc.EntitySyncServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def execute(
        self,
        request: featurestore_v1_entity_sync_service_pb2.SyncEntitiesRequest
    ) -> featurestore_v1_entity_sync_service_pb2.SyncEntitiesResponse:
        return await self.client.SyncEntities(request, timeout=self.timeout)


class PipelineRunCalculationEstimatePipelineRun1Port(Protocol):
    async def execute(
        self,
        request: pipelines_v1_pipeline_calculation_service_pb2.RecalculatePipelinesRequest
    ) -> pipelines_v1_pipeline_calculation_service_pb2.RecalculatePipelinesResponse: ...


class PipelineRunCalculationEstimatePipelineRun1Adapter:
    def __init__(
        self,
        client: pipelines_v1_pipeline_calculation_service_pb2_grpc.PipelineCalculationServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def execute(
        self,
        request: pipelines_v1_pipeline_calculation_service_pb2.RecalculatePipelinesRequest
    ) -> pipelines_v1_pipeline_calculation_service_pb2.RecalculatePipelinesResponse:
        return await self.client.RecalculatePipelines(request, timeout=self.timeout)


class PipelineRunImportValidatePipelineRunImport1Adapter:
    def __init__(
        self,
        client: modelregistry_v1_deployment_import_service_pb2_grpc.DeploymentImportServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def __call__(
        self,
        request: modelregistry_v1_deployment_import_service_pb2.ValidateDeploymentImportRequest
    ) -> modelregistry_v1_deployment_import_service_pb2.ValidateDeploymentImportResponse:
        return await self.client.ValidateDeploymentImport(request, timeout=self.timeout)


async def pipeline_run_lifecycle_suspend_pipeline_run0(
    client: documents_v1_document_query_service_pb2_grpc.DocumentQueryServiceStub,
    request: documents_v1_document_query_service_pb2.SuggestDocumentsRequest,
    timeout: float
) -> documents_v1_document_query_service_pb2.SuggestDocumentsResponse:
    return await client.SuggestDocuments(request, timeout=timeout)


class PipelineRunLifecycleSuspendPipelineRun2Port(Protocol):
    async def execute(
        self,
        request: pipelines_v1_pipeline_run_import_service_pb2.ValidatePipelineRunImportRequest
    ) -> pipelines_v1_pipeline_run_import_service_pb2.ValidatePipelineRunImportResponse: ...


class PipelineRunLifecycleSuspendPipelineRun2Adapter:
    def __init__(
        self,
        client: pipelines_v1_pipeline_run_import_service_pb2_grpc.PipelineRunImportServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def execute(
        self,
        request: pipelines_v1_pipeline_run_import_service_pb2.ValidatePipelineRunImportRequest
    ) -> pipelines_v1_pipeline_run_import_service_pb2.ValidatePipelineRunImportResponse:
        return await self.client.ValidatePipelineRunImport(request, timeout=self.timeout)


class PipelineRunReportingGeneratePipelineRunReport1Port(Protocol):
    async def execute(
        self,
        request: pipelines_v1_pipeline_sync_service_pb2.ReconcilePipelinesRequest
    ) -> pipelines_v1_pipeline_sync_service_pb2.ReconcilePipelinesResponse: ...


class PipelineRunReportingGeneratePipelineRunReport1Adapter:
    def __init__(
        self,
        client: pipelines_v1_pipeline_sync_service_pb2_grpc.PipelineSyncServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def execute(
        self,
        request: pipelines_v1_pipeline_sync_service_pb2.ReconcilePipelinesRequest
    ) -> pipelines_v1_pipeline_sync_service_pb2.ReconcilePipelinesResponse:
        return await self.client.ReconcilePipelines(request, timeout=self.timeout)


class PipelineRunReportingSharePipelineRunReport1Adapter:
    def __init__(
        self,
        client: featurestore_v1_entity_approval_service_pb2_grpc.EntityApprovalServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def __call__(
        self,
        request: featurestore_v1_entity_approval_service_pb2.RecallEntityRequest
    ) -> featurestore_v1_entity_approval_service_pb2.RecallEntityResponse:
        return await self.client.RecallEntity(request, timeout=self.timeout)


class PipelineRunSyncSyncPipelineRuns0Port(Protocol):
    async def execute(
        self,
        request: modelregistry_v1_deployment_approval_service_pb2.CommentDeploymentApprovalRequest
    ) -> modelregistry_v1_deployment_approval_service_pb2.CommentDeploymentApprovalResponse: ...


class PipelineRunSyncSyncPipelineRuns0Adapter:
    def __init__(
        self,
        client: modelregistry_v1_deployment_approval_service_pb2_grpc.DeploymentApprovalServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def execute(
        self,
        request: modelregistry_v1_deployment_approval_service_pb2.CommentDeploymentApprovalRequest
    ) -> modelregistry_v1_deployment_approval_service_pb2.CommentDeploymentApprovalResponse:
        return await self.client.CommentDeploymentApproval(request, timeout=self.timeout)


async def pipeline_run_validation_score_pipeline_run1(
    client: pipelines_v1_pipeline_step_calculation_service_pb2_grpc.PipelineStepCalculationServiceStub,
    request: pipelines_v1_pipeline_step_calculation_service_pb2.EstimatePipelineStepRequest,
    timeout: float
) -> pipelines_v1_pipeline_step_calculation_service_pb2.EstimatePipelineStepResponse:
    return await client.EstimatePipelineStep(request, timeout=timeout)


class PipelineRunWorkflowAdvancePipelineRunWorkflow0Adapter:
    def __init__(
        self,
        client: featureflags_v1_feature_flag_validation_service_pb2_grpc.FeatureFlagValidationServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def __call__(
        self,
        request: featureflags_v1_feature_flag_validation_service_pb2.CheckFeatureFlagEligibilityRequest
    ) -> featureflags_v1_feature_flag_validation_service_pb2.CheckFeatureFlagEligibilityResponse:
        return await self.client.CheckFeatureFlagEligibility(request, timeout=self.timeout)


async def pipeline_run_workflow_start_pipeline_run_workflow1(
    client: pipelines_v1_pipeline_run_reporting_service_pb2_grpc.PipelineRunReportingServiceStub,
    request: pipelines_v1_pipeline_run_reporting_service_pb2.SharePipelineRunReportRequest,
    timeout: float
) -> pipelines_v1_pipeline_run_reporting_service_pb2.SharePipelineRunReportResponse:
    return await client.SharePipelineRunReport(request, timeout=timeout)


async def pipeline_search_pipelines1(
    client: pipelines_v1_pipeline_query_service_pb2_grpc.PipelineQueryServiceStub,
    request: pipelines_v1_pipeline_query_service_pb2.ResolvePipelinesRequest,
    timeout: float
) -> pipelines_v1_pipeline_query_service_pb2.ResolvePipelinesResponse:
    return await client.ResolvePipelines(request, timeout=timeout)


class PipelineUpdatePipeline1Port(Protocol):
    async def execute(
        self,
        request: featurestore_v1_feature_view_calculation_service_pb2.SimulateFeatureViewRequest
    ) -> featurestore_v1_feature_view_calculation_service_pb2.SimulateFeatureViewResponse: ...


class PipelineUpdatePipeline1Adapter:
    def __init__(
        self,
        client: featurestore_v1_feature_view_calculation_service_pb2_grpc.FeatureViewCalculationServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def execute(
        self,
        request: featurestore_v1_feature_view_calculation_service_pb2.SimulateFeatureViewRequest
    ) -> featurestore_v1_feature_view_calculation_service_pb2.SimulateFeatureViewResponse:
        return await self.client.SimulateFeatureView(request, timeout=self.timeout)


async def pipeline_step_approval_reject_pipeline_step1(
    client: modelregistry_v1_model_version_reporting_service_pb2_grpc.ModelVersionReportingServiceStub,
    request: modelregistry_v1_model_version_reporting_service_pb2.GenerateModelVersionReportRequest,
    timeout: float
) -> modelregistry_v1_model_version_reporting_service_pb2.GenerateModelVersionReportResponse:
    return await client.GenerateModelVersionReport(request, timeout=timeout)


class PipelineStepCalculationCalculatePipelineStep1Adapter:
    def __init__(
        self,
        client: lineage_v1_lineage_edge_calculation_service_pb2_grpc.LineageEdgeCalculationServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def __call__(
        self,
        request: lineage_v1_lineage_edge_calculation_service_pb2.QuoteLineageEdgeRequest
    ) -> lineage_v1_lineage_edge_calculation_service_pb2.QuoteLineageEdgeResponse:
        return await self.client.QuoteLineageEdge(request, timeout=self.timeout)


async def pipeline_step_calculation_simulate_pipeline_step0(
    client: pipelines_v1_pipeline_run_calculation_service_pb2_grpc.PipelineRunCalculationServiceStub,
    request: pipelines_v1_pipeline_run_calculation_service_pb2.CalculatePipelineRunRequest,
    timeout: float
) -> pipelines_v1_pipeline_run_calculation_service_pb2.CalculatePipelineRunResponse:
    return await client.CalculatePipelineRun(request, timeout=timeout)


class PipelineStepCalculationSimulatePipelineStep2Port(Protocol):
    async def execute(
        self,
        request: labeling_v1_label_set_validation_service_pb2.NormalizeLabelSetRequest
    ) -> labeling_v1_label_set_validation_service_pb2.NormalizeLabelSetResponse: ...


class PipelineStepCalculationSimulatePipelineStep2Adapter:
    def __init__(
        self,
        client: labeling_v1_label_set_validation_service_pb2_grpc.LabelSetValidationServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def execute(
        self,
        request: labeling_v1_label_set_validation_service_pb2.NormalizeLabelSetRequest
    ) -> labeling_v1_label_set_validation_service_pb2.NormalizeLabelSetResponse:
        return await self.client.NormalizeLabelSet(request, timeout=self.timeout)


class PipelineStepExportStreamPipelineStepExport2Adapter:
    def __init__(
        self,
        client: pipelines_v1_pipeline_calculation_service_pb2_grpc.PipelineCalculationServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def __call__(
        self,
        request: pipelines_v1_pipeline_calculation_service_pb2.CalculatePipelineRequest
    ) -> pipelines_v1_pipeline_calculation_service_pb2.CalculatePipelineResponse:
        return await self.client.CalculatePipeline(request, timeout=self.timeout)


async def pipeline_step_import_retry_pipeline_step_import0(
    client: ledger_v1_ledger_account_service_pb2_grpc.LedgerAccountServiceStub,
    request: ledger_v1_ledger_account_service_pb2.SearchLedgerAccountsRequest,
    timeout: float
) -> ledger_v1_ledger_account_service_pb2.SearchLedgerAccountsResponse:
    return await client.SearchLedgerAccounts(request, timeout=timeout)


class PipelineStepImportRetryPipelineStepImport2Port(Protocol):
    async def execute(
        self,
        request: pipelines_v1_pipeline_run_calculation_service_pb2.ComparePipelineRunOptionsRequest
    ) -> pipelines_v1_pipeline_run_calculation_service_pb2.ComparePipelineRunOptionsResponse: ...


class PipelineStepImportRetryPipelineStepImport2Adapter:
    def __init__(
        self,
        client: pipelines_v1_pipeline_run_calculation_service_pb2_grpc.PipelineRunCalculationServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def execute(
        self,
        request: pipelines_v1_pipeline_run_calculation_service_pb2.ComparePipelineRunOptionsRequest
    ) -> pipelines_v1_pipeline_run_calculation_service_pb2.ComparePipelineRunOptionsResponse:
        return await self.client.ComparePipelineRunOptions(request, timeout=self.timeout)


async def pipeline_step_lifecycle_schedule_pipeline_step_expiry2(
    client: pipelines_v1_pipeline_run_reporting_service_pb2_grpc.PipelineRunReportingServiceStub,
    request: pipelines_v1_pipeline_run_reporting_service_pb2.CountPipelineRunTotalsRequest,
    timeout: float
) -> pipelines_v1_pipeline_run_reporting_service_pb2.CountPipelineRunTotalsResponse:
    return await client.CountPipelineRunTotals(request, timeout=timeout)


class PipelineStepLifecycleSuspendPipelineStep2Adapter:
    def __init__(self, client: search_v1_search_index_service_pb2_grpc.SearchIndexServiceStub, timeout: float) -> None:
        self.client = client
        self.timeout = timeout

    async def __call__(
        self,
        request: search_v1_search_index_service_pb2.UpdateSearchIndexRequest
    ) -> search_v1_search_index_service_pb2.UpdateSearchIndexResponse:
        return await self.client.UpdateSearchIndex(request, timeout=self.timeout)


async def pipeline_step_reporting_schedule_pipeline_step_report0(
    client: recruiting_v1_job_opening_service_pb2_grpc.JobOpeningServiceStub,
    request: recruiting_v1_job_opening_service_pb2.CloneJobOpeningRequest,
    timeout: float
) -> recruiting_v1_job_opening_service_pb2.CloneJobOpeningResponse:
    return await client.CloneJobOpening(request, timeout=timeout)


class PipelineStepSyncPullPipelineSteps0Adapter:
    def __init__(
        self,
        client: featurestore_v1_feature_view_approval_service_pb2_grpc.FeatureViewApprovalServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def __call__(
        self,
        request: featurestore_v1_feature_view_approval_service_pb2.ApproveFeatureViewRequest
    ) -> featurestore_v1_feature_view_approval_service_pb2.ApproveFeatureViewResponse:
        return await self.client.ApproveFeatureView(request, timeout=self.timeout)


async def pipeline_step_validation_check_pipeline_step_eligibility2(
    client: prescriptions_v1_prescription_query_service_pb2_grpc.PrescriptionQueryServiceStub,
    request: prescriptions_v1_prescription_query_service_pb2.BrowsePrescriptionsRequest,
    timeout: float
) -> prescriptions_v1_prescription_query_service_pb2.BrowsePrescriptionsResponse:
    return await client.BrowsePrescriptions(request, timeout=timeout)


class PipelineStepValidationLintPipelineSteps1Adapter:
    def __init__(self, client: yards_v1_yard_query_service_pb2_grpc.YardQueryServiceStub, timeout: float) -> None:
        self.client = client
        self.timeout = timeout

    async def __call__(
        self,
        request: yards_v1_yard_query_service_pb2.BrowseYardsRequest
    ) -> yards_v1_yard_query_service_pb2.BrowseYardsResponse:
        return await self.client.BrowseYards(request, timeout=self.timeout)


async def pipeline_step_workflow_advance_pipeline_step_workflow2(
    client: pipelines_v1_pipeline_step_export_service_pb2_grpc.PipelineStepExportServiceStub,
    request: pipelines_v1_pipeline_step_export_service_pb2.ListPipelineStepExportsRequest,
    timeout: float
) -> pipelines_v1_pipeline_step_export_service_pb2.ListPipelineStepExportsResponse:
    return await client.ListPipelineStepExports(request, timeout=timeout)


class PipelineStepWorkflowCancelPipelineStepWorkflow0Port(Protocol):
    async def execute(
        self,
        request: identity_v1_user_service_pb2.SearchUsersRequest
    ) -> identity_v1_user_service_pb2.SearchUsersResponse: ...


class PipelineStepWorkflowCancelPipelineStepWorkflow0Adapter:
    def __init__(self, client: identity_v1_user_service_pb2_grpc.UserServiceStub, timeout: float) -> None:
        self.client = client
        self.timeout = timeout

    async def execute(
        self,
        request: identity_v1_user_service_pb2.SearchUsersRequest
    ) -> identity_v1_user_service_pb2.SearchUsersResponse:
        return await self.client.SearchUsers(request, timeout=self.timeout)


async def pipeline_sync_push_pipeline1(
    client: pipelines_v1_pipeline_query_service_pb2_grpc.PipelineQueryServiceStub,
    request: pipelines_v1_pipeline_query_service_pb2.BrowsePipelinesRequest,
    timeout: float
) -> pipelines_v1_pipeline_query_service_pb2.BrowsePipelinesResponse:
    return await client.BrowsePipelines(request, timeout=timeout)


class PipelineSyncReconcilePipelines0Port(Protocol):
    async def execute(
        self,
        request: pipelines_v1_pipeline_validation_service_pb2.ScorePipelineRequest
    ) -> pipelines_v1_pipeline_validation_service_pb2.ScorePipelineResponse: ...


class PipelineSyncReconcilePipelines0Adapter:
    def __init__(
        self,
        client: pipelines_v1_pipeline_validation_service_pb2_grpc.PipelineValidationServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def execute(
        self,
        request: pipelines_v1_pipeline_validation_service_pb2.ScorePipelineRequest
    ) -> pipelines_v1_pipeline_validation_service_pb2.ScorePipelineResponse:
        return await self.client.ScorePipeline(request, timeout=self.timeout)


class PipelineSyncResolvePipelineConflict1Adapter:
    def __init__(
        self,
        client: pipelines_v1_pipeline_step_calculation_service_pb2_grpc.PipelineStepCalculationServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def __call__(
        self,
        request: pipelines_v1_pipeline_step_calculation_service_pb2.CalculatePipelineStepRequest
    ) -> pipelines_v1_pipeline_step_calculation_service_pb2.CalculatePipelineStepResponse:
        return await self.client.CalculatePipelineStep(request, timeout=self.timeout)


async def pipeline_validation_preview_pipeline2(
    client: labeling_v1_labeling_task_service_pb2_grpc.LabelingTaskServiceStub,
    request: labeling_v1_labeling_task_service_pb2.ListLabelingTasksRequest,
    timeout: float
) -> labeling_v1_labeling_task_service_pb2.ListLabelingTasksResponse:
    return await client.ListLabelingTasks(request, timeout=timeout)


class PipelineValidationScorePipeline2Adapter:
    def __init__(
        self,
        client: pipelines_v1_pipeline_calculation_service_pb2_grpc.PipelineCalculationServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def __call__(
        self,
        request: pipelines_v1_pipeline_calculation_service_pb2.EstimatePipelineRequest
    ) -> pipelines_v1_pipeline_calculation_service_pb2.EstimatePipelineResponse:
        return await self.client.EstimatePipeline(request, timeout=self.timeout)


async def pipeline_workflow_pause_pipeline_workflow3(
    client: drivers_v1_driver_calculation_service_pb2_grpc.DriverCalculationServiceStub,
    request: drivers_v1_driver_calculation_service_pb2.CalculateDriverRequest,
    timeout: float
) -> drivers_v1_driver_calculation_service_pb2.CalculateDriverResponse:
    return await client.CalculateDriver(request, timeout=timeout)


class PipelineWorkflowResumePipelineWorkflow1Port(Protocol):
    async def execute(
        self,
        request: pipelines_v1_pipeline_sync_service_pb2.PullPipelinesRequest
    ) -> pipelines_v1_pipeline_sync_service_pb2.PullPipelinesResponse: ...


class PipelineWorkflowResumePipelineWorkflow1Adapter:
    def __init__(
        self,
        client: pipelines_v1_pipeline_sync_service_pb2_grpc.PipelineSyncServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def execute(
        self,
        request: pipelines_v1_pipeline_sync_service_pb2.PullPipelinesRequest
    ) -> pipelines_v1_pipeline_sync_service_pb2.PullPipelinesResponse:
        return await self.client.PullPipelines(request, timeout=self.timeout)


class PipelineWorkflowRetryPipelineWorkflow0Adapter:
    def __init__(
        self,
        client: pipelines_v1_pipeline_approval_service_pb2_grpc.PipelineApprovalServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def __call__(
        self,
        request: pipelines_v1_pipeline_approval_service_pb2.EscalatePipelineRequest
    ) -> pipelines_v1_pipeline_approval_service_pb2.EscalatePipelineResponse:
        return await self.client.EscalatePipeline(request, timeout=self.timeout)
