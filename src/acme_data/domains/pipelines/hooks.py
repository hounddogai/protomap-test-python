"""Replaceable partner hooks of the pipelines domain."""

from __future__ import annotations

from acme.concessions.v1 import concession_stand_service_pb2 as concessions_v1_concession_stand_service_pb2
from acme.concessions.v1 import concession_stand_service_pb2_grpc as concessions_v1_concession_stand_service_pb2_grpc
from acme.documents.v1 import document_query_service_pb2 as documents_v1_document_query_service_pb2
from acme.documents.v1 import document_query_service_pb2_grpc as documents_v1_document_query_service_pb2_grpc
from acme.drivers.v1 import driver_calculation_service_pb2 as drivers_v1_driver_calculation_service_pb2
from acme.drivers.v1 import driver_calculation_service_pb2_grpc as drivers_v1_driver_calculation_service_pb2_grpc
from acme.identity.v1 import user_query_service_pb2 as identity_v1_user_query_service_pb2
from acme.identity.v1 import user_query_service_pb2_grpc as identity_v1_user_query_service_pb2_grpc
from acme.labeling.v1 import labeling_task_service_pb2 as labeling_v1_labeling_task_service_pb2
from acme.labeling.v1 import labeling_task_service_pb2_grpc as labeling_v1_labeling_task_service_pb2_grpc
from acme.ledger.v1 import ledger_account_service_pb2 as ledger_v1_ledger_account_service_pb2
from acme.ledger.v1 import ledger_account_service_pb2_grpc as ledger_v1_ledger_account_service_pb2_grpc
from acme.modelregistry.v1 import (
    model_version_reporting_service_pb2 as modelregistry_v1_model_version_reporting_service_pb2,
)
from acme.modelregistry.v1 import (
    model_version_reporting_service_pb2_grpc as modelregistry_v1_model_version_reporting_service_pb2_grpc,
)
from acme.notifications.v1 import notification_service_pb2 as notifications_v1_notification_service_pb2
from acme.notifications.v1 import notification_service_pb2_grpc as notifications_v1_notification_service_pb2_grpc
from acme.pipelines.v1 import pipeline_query_service_pb2 as pipelines_v1_pipeline_query_service_pb2
from acme.pipelines.v1 import pipeline_query_service_pb2_grpc as pipelines_v1_pipeline_query_service_pb2_grpc
from acme.pipelines.v1 import pipeline_run_calculation_service_pb2 as pipelines_v1_pipeline_run_calculation_service_pb2
from acme.pipelines.v1 import (
    pipeline_run_calculation_service_pb2_grpc as pipelines_v1_pipeline_run_calculation_service_pb2_grpc,
)
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
from acme.prescriptions.v1 import prescription_query_service_pb2 as prescriptions_v1_prescription_query_service_pb2
from acme.prescriptions.v1 import (
    prescription_query_service_pb2_grpc as prescriptions_v1_prescription_query_service_pb2_grpc,
)
from acme.recruiting.v1 import job_opening_service_pb2 as recruiting_v1_job_opening_service_pb2
from acme.recruiting.v1 import job_opening_service_pb2_grpc as recruiting_v1_job_opening_service_pb2_grpc


async def pipeline_calculation_calculate_pipeline0(
    client: concessions_v1_concession_stand_service_pb2_grpc.ConcessionStandServiceStub,
    request: concessions_v1_concession_stand_service_pb2.CreateConcessionStandRequest,
    timeout: float
) -> concessions_v1_concession_stand_service_pb2.CreateConcessionStandResponse:
    raise RuntimeError("domain hook was not installed")


async def pipeline_reporting_generate_pipeline_report0(
    client: identity_v1_user_query_service_pb2_grpc.UserQueryServiceStub,
    request: identity_v1_user_query_service_pb2.ResolveUsersRequest,
    timeout: float
) -> identity_v1_user_query_service_pb2.ResolveUsersResponse:
    raise RuntimeError("domain hook was not installed")


async def pipeline_run_approval_escalate_pipeline_run1(
    client: notifications_v1_notification_service_pb2_grpc.NotificationServiceStub,
    request: notifications_v1_notification_service_pb2.CreateNotificationRequest,
    timeout: float
) -> notifications_v1_notification_service_pb2.CreateNotificationResponse:
    raise RuntimeError("domain hook was not installed")


async def pipeline_run_lifecycle_suspend_pipeline_run0(
    client: documents_v1_document_query_service_pb2_grpc.DocumentQueryServiceStub,
    request: documents_v1_document_query_service_pb2.SuggestDocumentsRequest,
    timeout: float
) -> documents_v1_document_query_service_pb2.SuggestDocumentsResponse:
    raise RuntimeError("domain hook was not installed")


async def pipeline_run_validation_score_pipeline_run1(
    client: pipelines_v1_pipeline_step_calculation_service_pb2_grpc.PipelineStepCalculationServiceStub,
    request: pipelines_v1_pipeline_step_calculation_service_pb2.EstimatePipelineStepRequest,
    timeout: float
) -> pipelines_v1_pipeline_step_calculation_service_pb2.EstimatePipelineStepResponse:
    raise RuntimeError("domain hook was not installed")


async def pipeline_run_workflow_start_pipeline_run_workflow1(
    client: pipelines_v1_pipeline_run_reporting_service_pb2_grpc.PipelineRunReportingServiceStub,
    request: pipelines_v1_pipeline_run_reporting_service_pb2.SharePipelineRunReportRequest,
    timeout: float
) -> pipelines_v1_pipeline_run_reporting_service_pb2.SharePipelineRunReportResponse:
    raise RuntimeError("domain hook was not installed")


async def pipeline_search_pipelines1(
    client: pipelines_v1_pipeline_query_service_pb2_grpc.PipelineQueryServiceStub,
    request: pipelines_v1_pipeline_query_service_pb2.ResolvePipelinesRequest,
    timeout: float
) -> pipelines_v1_pipeline_query_service_pb2.ResolvePipelinesResponse:
    raise RuntimeError("domain hook was not installed")


async def pipeline_step_approval_reject_pipeline_step1(
    client: modelregistry_v1_model_version_reporting_service_pb2_grpc.ModelVersionReportingServiceStub,
    request: modelregistry_v1_model_version_reporting_service_pb2.GenerateModelVersionReportRequest,
    timeout: float
) -> modelregistry_v1_model_version_reporting_service_pb2.GenerateModelVersionReportResponse:
    raise RuntimeError("domain hook was not installed")


async def pipeline_step_calculation_simulate_pipeline_step0(
    client: pipelines_v1_pipeline_run_calculation_service_pb2_grpc.PipelineRunCalculationServiceStub,
    request: pipelines_v1_pipeline_run_calculation_service_pb2.CalculatePipelineRunRequest,
    timeout: float
) -> pipelines_v1_pipeline_run_calculation_service_pb2.CalculatePipelineRunResponse:
    raise RuntimeError("domain hook was not installed")


async def pipeline_step_import_retry_pipeline_step_import0(
    client: ledger_v1_ledger_account_service_pb2_grpc.LedgerAccountServiceStub,
    request: ledger_v1_ledger_account_service_pb2.SearchLedgerAccountsRequest,
    timeout: float
) -> ledger_v1_ledger_account_service_pb2.SearchLedgerAccountsResponse:
    raise RuntimeError("domain hook was not installed")


async def pipeline_step_lifecycle_schedule_pipeline_step_expiry2(
    client: pipelines_v1_pipeline_run_reporting_service_pb2_grpc.PipelineRunReportingServiceStub,
    request: pipelines_v1_pipeline_run_reporting_service_pb2.CountPipelineRunTotalsRequest,
    timeout: float
) -> pipelines_v1_pipeline_run_reporting_service_pb2.CountPipelineRunTotalsResponse:
    raise RuntimeError("domain hook was not installed")


async def pipeline_step_reporting_schedule_pipeline_step_report0(
    client: recruiting_v1_job_opening_service_pb2_grpc.JobOpeningServiceStub,
    request: recruiting_v1_job_opening_service_pb2.CloneJobOpeningRequest,
    timeout: float
) -> recruiting_v1_job_opening_service_pb2.CloneJobOpeningResponse:
    raise RuntimeError("domain hook was not installed")


async def pipeline_step_validation_check_pipeline_step_eligibility2(
    client: prescriptions_v1_prescription_query_service_pb2_grpc.PrescriptionQueryServiceStub,
    request: prescriptions_v1_prescription_query_service_pb2.BrowsePrescriptionsRequest,
    timeout: float
) -> prescriptions_v1_prescription_query_service_pb2.BrowsePrescriptionsResponse:
    raise RuntimeError("domain hook was not installed")


async def pipeline_step_workflow_advance_pipeline_step_workflow2(
    client: pipelines_v1_pipeline_step_export_service_pb2_grpc.PipelineStepExportServiceStub,
    request: pipelines_v1_pipeline_step_export_service_pb2.ListPipelineStepExportsRequest,
    timeout: float
) -> pipelines_v1_pipeline_step_export_service_pb2.ListPipelineStepExportsResponse:
    raise RuntimeError("domain hook was not installed")


async def pipeline_sync_push_pipeline1(
    client: pipelines_v1_pipeline_query_service_pb2_grpc.PipelineQueryServiceStub,
    request: pipelines_v1_pipeline_query_service_pb2.BrowsePipelinesRequest,
    timeout: float
) -> pipelines_v1_pipeline_query_service_pb2.BrowsePipelinesResponse:
    raise RuntimeError("domain hook was not installed")


async def pipeline_validation_preview_pipeline2(
    client: labeling_v1_labeling_task_service_pb2_grpc.LabelingTaskServiceStub,
    request: labeling_v1_labeling_task_service_pb2.ListLabelingTasksRequest,
    timeout: float
) -> labeling_v1_labeling_task_service_pb2.ListLabelingTasksResponse:
    raise RuntimeError("domain hook was not installed")


async def pipeline_workflow_pause_pipeline_workflow3(
    client: drivers_v1_driver_calculation_service_pb2_grpc.DriverCalculationServiceStub,
    request: drivers_v1_driver_calculation_service_pb2.CalculateDriverRequest,
    timeout: float
) -> drivers_v1_driver_calculation_service_pb2.CalculateDriverResponse:
    raise RuntimeError("domain hook was not installed")
