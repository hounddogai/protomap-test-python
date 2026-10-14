"""Transport adapters used by datahub workflows."""

from __future__ import annotations

from typing import Protocol

from acme.analytics.v1 import analytics_event_approval_service_pb2 as analytics_v1_analytics_event_approval_service_pb2
from acme.analytics.v1 import (
    analytics_event_approval_service_pb2_grpc as analytics_v1_analytics_event_approval_service_pb2_grpc,
)
from acme.analytics.v1 import (
    analytics_report_approval_service_pb2 as analytics_v1_analytics_report_approval_service_pb2,
)
from acme.analytics.v1 import (
    analytics_report_approval_service_pb2_grpc as analytics_v1_analytics_report_approval_service_pb2_grpc,
)
from acme.anomalies.v1 import anomaly_workflow_service_pb2 as anomalies_v1_anomaly_workflow_service_pb2
from acme.anomalies.v1 import anomaly_workflow_service_pb2_grpc as anomalies_v1_anomaly_workflow_service_pb2_grpc
from acme.authorization.v1 import (
    access_policy_validation_service_pb2 as authorization_v1_access_policy_validation_service_pb2,
)
from acme.authorization.v1 import (
    access_policy_validation_service_pb2_grpc as authorization_v1_access_policy_validation_service_pb2_grpc,
)
from acme.customers.v1 import consent_record_approval_service_pb2 as customers_v1_consent_record_approval_service_pb2
from acme.customers.v1 import (
    consent_record_approval_service_pb2_grpc as customers_v1_consent_record_approval_service_pb2_grpc,
)
from acme.customers.v1 import customer_approval_service_pb2 as customers_v1_customer_approval_service_pb2
from acme.customers.v1 import customer_approval_service_pb2_grpc as customers_v1_customer_approval_service_pb2_grpc
from acme.customers.v1 import customer_workflow_service_pb2 as customers_v1_customer_workflow_service_pb2
from acme.customers.v1 import customer_workflow_service_pb2_grpc as customers_v1_customer_workflow_service_pb2_grpc
from acme.customers.v1 import household_reporting_service_pb2 as customers_v1_household_reporting_service_pb2
from acme.customers.v1 import household_reporting_service_pb2_grpc as customers_v1_household_reporting_service_pb2_grpc
from acme.customers.v1 import household_workflow_service_pb2 as customers_v1_household_workflow_service_pb2
from acme.customers.v1 import household_workflow_service_pb2_grpc as customers_v1_household_workflow_service_pb2_grpc
from acme.customers.v1 import preference_import_service_pb2 as customers_v1_preference_import_service_pb2
from acme.customers.v1 import preference_import_service_pb2_grpc as customers_v1_preference_import_service_pb2_grpc
from acme.customers.v1 import preference_sync_service_pb2 as customers_v1_preference_sync_service_pb2
from acme.customers.v1 import preference_sync_service_pb2_grpc as customers_v1_preference_sync_service_pb2_grpc
from acme.datahub.v1 import data_share_approval_service_pb2 as datahub_v1_data_share_approval_service_pb2
from acme.datahub.v1 import data_share_approval_service_pb2_grpc as datahub_v1_data_share_approval_service_pb2_grpc
from acme.datahub.v1 import data_share_reporting_service_pb2 as datahub_v1_data_share_reporting_service_pb2
from acme.datahub.v1 import data_share_reporting_service_pb2_grpc as datahub_v1_data_share_reporting_service_pb2_grpc
from acme.datahub.v1 import data_share_validation_service_pb2 as datahub_v1_data_share_validation_service_pb2
from acme.datahub.v1 import data_share_validation_service_pb2_grpc as datahub_v1_data_share_validation_service_pb2_grpc
from acme.datahub.v1 import data_share_workflow_service_pb2 as datahub_v1_data_share_workflow_service_pb2
from acme.datahub.v1 import data_share_workflow_service_pb2_grpc as datahub_v1_data_share_workflow_service_pb2_grpc
from acme.datahub.v1 import notebook_approval_service_pb2 as datahub_v1_notebook_approval_service_pb2
from acme.datahub.v1 import notebook_approval_service_pb2_grpc as datahub_v1_notebook_approval_service_pb2_grpc
from acme.datahub.v1 import notebook_integration_service_pb2 as datahub_v1_notebook_integration_service_pb2
from acme.datahub.v1 import notebook_integration_service_pb2_grpc as datahub_v1_notebook_integration_service_pb2_grpc
from acme.datahub.v1 import workspace_approval_service_pb2 as datahub_v1_workspace_approval_service_pb2
from acme.datahub.v1 import workspace_approval_service_pb2_grpc as datahub_v1_workspace_approval_service_pb2_grpc
from acme.datahub.v1 import workspace_integration_service_pb2 as datahub_v1_workspace_integration_service_pb2
from acme.datahub.v1 import workspace_integration_service_pb2_grpc as datahub_v1_workspace_integration_service_pb2_grpc
from acme.datahub.v1 import workspace_notification_service_pb2 as datahub_v1_workspace_notification_service_pb2
from acme.datahub.v1 import (
    workspace_notification_service_pb2_grpc as datahub_v1_workspace_notification_service_pb2_grpc,
)
from acme.datahub.v1 import workspace_reporting_service_pb2 as datahub_v1_workspace_reporting_service_pb2
from acme.datahub.v1 import workspace_reporting_service_pb2_grpc as datahub_v1_workspace_reporting_service_pb2_grpc
from acme.datahub.v1 import workspace_workflow_service_pb2 as datahub_v1_workspace_workflow_service_pb2
from acme.datahub.v1 import workspace_workflow_service_pb2_grpc as datahub_v1_workspace_workflow_service_pb2_grpc
from acme.documents.v1 import document_service_pb2 as documents_v1_document_service_pb2
from acme.documents.v1 import document_service_pb2_grpc as documents_v1_document_service_pb2_grpc
from acme.fanportal.v1 import fan_session_query_service_pb2 as fanportal_v1_fan_session_query_service_pb2
from acme.fanportal.v1 import fan_session_query_service_pb2_grpc as fanportal_v1_fan_session_query_service_pb2_grpc
from acme.fanportal.v1 import fan_session_service_pb2 as fanportal_v1_fan_session_service_pb2
from acme.fanportal.v1 import fan_session_service_pb2_grpc as fanportal_v1_fan_session_service_pb2_grpc
from acme.featureflags.v1 import feature_flag_service_pb2 as featureflags_v1_feature_flag_service_pb2
from acme.featureflags.v1 import feature_flag_service_pb2_grpc as featureflags_v1_feature_flag_service_pb2_grpc
from acme.featureflags.v1 import (
    feature_flag_validation_service_pb2 as featureflags_v1_feature_flag_validation_service_pb2,
)
from acme.featureflags.v1 import (
    feature_flag_validation_service_pb2_grpc as featureflags_v1_feature_flag_validation_service_pb2_grpc,
)
from acme.featurestore.v1 import (
    feature_value_reporting_service_pb2 as featurestore_v1_feature_value_reporting_service_pb2,
)
from acme.featurestore.v1 import (
    feature_value_reporting_service_pb2_grpc as featurestore_v1_feature_value_reporting_service_pb2_grpc,
)
from acme.forecasting.v1 import (
    demand_forecast_approval_service_pb2 as forecasting_v1_demand_forecast_approval_service_pb2,
)
from acme.forecasting.v1 import (
    demand_forecast_approval_service_pb2_grpc as forecasting_v1_demand_forecast_approval_service_pb2_grpc,
)
from acme.identity.v1 import user_query_service_pb2 as identity_v1_user_query_service_pb2
from acme.identity.v1 import user_query_service_pb2_grpc as identity_v1_user_query_service_pb2_grpc
from acme.labeling.v1 import label_set_approval_service_pb2 as labeling_v1_label_set_approval_service_pb2
from acme.labeling.v1 import label_set_approval_service_pb2_grpc as labeling_v1_label_set_approval_service_pb2_grpc
from acme.metrics.v1 import metric_alert_validation_service_pb2 as metrics_v1_metric_alert_validation_service_pb2
from acme.metrics.v1 import (
    metric_alert_validation_service_pb2_grpc as metrics_v1_metric_alert_validation_service_pb2_grpc,
)
from acme.metrics.v1 import metric_series_admin_service_pb2 as metrics_v1_metric_series_admin_service_pb2
from acme.metrics.v1 import metric_series_admin_service_pb2_grpc as metrics_v1_metric_series_admin_service_pb2_grpc
from acme.pipelines.v1 import pipeline_run_workflow_service_pb2 as pipelines_v1_pipeline_run_workflow_service_pb2
from acme.pipelines.v1 import (
    pipeline_run_workflow_service_pb2_grpc as pipelines_v1_pipeline_run_workflow_service_pb2_grpc,
)
from acme.pipelines.v1 import pipeline_step_reporting_service_pb2 as pipelines_v1_pipeline_step_reporting_service_pb2
from acme.pipelines.v1 import (
    pipeline_step_reporting_service_pb2_grpc as pipelines_v1_pipeline_step_reporting_service_pb2_grpc,
)
from acme.search.v1 import search_index_validation_service_pb2 as search_v1_search_index_validation_service_pb2
from acme.search.v1 import (
    search_index_validation_service_pb2_grpc as search_v1_search_index_validation_service_pb2_grpc,
)


async def data_share_approval_approve_data_share0(
    client: datahub_v1_data_share_validation_service_pb2_grpc.DataShareValidationServiceStub,
    request: datahub_v1_data_share_validation_service_pb2.ScoreDataShareRequest,
    timeout: float
) -> datahub_v1_data_share_validation_service_pb2.ScoreDataShareResponse:
    return await client.ScoreDataShare(request, timeout=timeout)


class DataShareApprovalApproveDataShare2Port(Protocol):
    async def execute(
        self,
        request: analytics_v1_analytics_report_approval_service_pb2.ListPendingAnalyticsReportsRequest
    ) -> analytics_v1_analytics_report_approval_service_pb2.ListPendingAnalyticsReportsResponse: ...


class DataShareApprovalApproveDataShare2Adapter:
    def __init__(
        self,
        client: analytics_v1_analytics_report_approval_service_pb2_grpc.AnalyticsReportApprovalServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def execute(
        self,
        request: analytics_v1_analytics_report_approval_service_pb2.ListPendingAnalyticsReportsRequest
    ) -> analytics_v1_analytics_report_approval_service_pb2.ListPendingAnalyticsReportsResponse:
        return await self.client.ListPendingAnalyticsReports(request, timeout=self.timeout)


class DataShareApprovalCommentDataShareApproval1Adapter:
    def __init__(
        self,
        client: datahub_v1_notebook_approval_service_pb2_grpc.NotebookApprovalServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def __call__(
        self,
        request: datahub_v1_notebook_approval_service_pb2.DelegateNotebookApprovalRequest
    ) -> datahub_v1_notebook_approval_service_pb2.DelegateNotebookApprovalResponse:
        return await self.client.DelegateNotebookApproval(request, timeout=self.timeout)


async def data_share_approval_reject_data_share3(
    client: customers_v1_household_reporting_service_pb2_grpc.HouseholdReportingServiceStub,
    request: customers_v1_household_reporting_service_pb2.ListHouseholdReportsRequest,
    timeout: float
) -> customers_v1_household_reporting_service_pb2.ListHouseholdReportsResponse:
    return await client.ListHouseholdReports(request, timeout=timeout)


class DataShareApprovalSubmitDataShare1Port(Protocol):
    async def execute(
        self,
        request: datahub_v1_workspace_approval_service_pb2.EscalateWorkspaceRequest
    ) -> datahub_v1_workspace_approval_service_pb2.EscalateWorkspaceResponse: ...


class DataShareApprovalSubmitDataShare1Adapter:
    def __init__(
        self,
        client: datahub_v1_workspace_approval_service_pb2_grpc.WorkspaceApprovalServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def execute(
        self,
        request: datahub_v1_workspace_approval_service_pb2.EscalateWorkspaceRequest
    ) -> datahub_v1_workspace_approval_service_pb2.EscalateWorkspaceResponse:
        return await self.client.EscalateWorkspace(request, timeout=self.timeout)


class DataShareIntegrationAcknowledgeDataShareEvent0Adapter:
    def __init__(
        self,
        client: authorization_v1_access_policy_validation_service_pb2_grpc.AccessPolicyValidationServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def __call__(
        self,
        request: authorization_v1_access_policy_validation_service_pb2.ExplainAccessPolicyDecisionRequest
    ) -> authorization_v1_access_policy_validation_service_pb2.ExplainAccessPolicyDecisionResponse:
        return await self.client.ExplainAccessPolicyDecision(request, timeout=self.timeout)


class DataShareIntegrationListDataShareSources1Port(Protocol):
    async def execute(
        self,
        request: datahub_v1_workspace_notification_service_pb2.SendWorkspaceTestNoticeRequest
    ) -> datahub_v1_workspace_notification_service_pb2.SendWorkspaceTestNoticeResponse: ...


class DataShareIntegrationListDataShareSources1Adapter:
    def __init__(
        self,
        client: datahub_v1_workspace_notification_service_pb2_grpc.WorkspaceNotificationServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def execute(
        self,
        request: datahub_v1_workspace_notification_service_pb2.SendWorkspaceTestNoticeRequest
    ) -> datahub_v1_workspace_notification_service_pb2.SendWorkspaceTestNoticeResponse:
        return await self.client.SendWorkspaceTestNotice(request, timeout=self.timeout)


class DataShareIntegrationRelayDataShareMessages1Adapter:
    def __init__(
        self,
        client: customers_v1_preference_import_service_pb2_grpc.PreferenceImportServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def __call__(
        self,
        request: customers_v1_preference_import_service_pb2.ValidatePreferenceImportRequest
    ) -> customers_v1_preference_import_service_pb2.ValidatePreferenceImportResponse:
        return await self.client.ValidatePreferenceImport(request, timeout=self.timeout)


async def data_share_notification_unsubscribe_data_share_updates1(
    client: search_v1_search_index_validation_service_pb2_grpc.SearchIndexValidationServiceStub,
    request: search_v1_search_index_validation_service_pb2.LintSearchIndexesRequest,
    timeout: float
) -> search_v1_search_index_validation_service_pb2.LintSearchIndexesResponse:
    return await client.LintSearchIndexes(request, timeout=timeout)


class DataShareQueryExportDataShares0Adapter:
    def __init__(
        self,
        client: customers_v1_customer_workflow_service_pb2_grpc.CustomerWorkflowServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def __call__(
        self,
        request: customers_v1_customer_workflow_service_pb2.StartCustomerWorkflowRequest
    ) -> customers_v1_customer_workflow_service_pb2.StartCustomerWorkflowResponse:
        return await self.client.StartCustomerWorkflow(request, timeout=self.timeout)


class DataShareReportingDeleteDataShareReport1Port(Protocol):
    async def execute(
        self,
        request: fanportal_v1_fan_session_service_pb2.CreateFanSessionRequest
    ) -> fanportal_v1_fan_session_service_pb2.CreateFanSessionResponse: ...


class DataShareReportingDeleteDataShareReport1Adapter:
    def __init__(self, client: fanportal_v1_fan_session_service_pb2_grpc.FanSessionServiceStub, timeout: float) -> None:
        self.client = client
        self.timeout = timeout

    async def execute(
        self,
        request: fanportal_v1_fan_session_service_pb2.CreateFanSessionRequest
    ) -> fanportal_v1_fan_session_service_pb2.CreateFanSessionResponse:
        return await self.client.CreateFanSession(request, timeout=self.timeout)


async def data_share_validation_check_data_share_eligibility1(
    client: datahub_v1_workspace_approval_service_pb2_grpc.WorkspaceApprovalServiceStub,
    request: datahub_v1_workspace_approval_service_pb2.DelegateWorkspaceApprovalRequest,
    timeout: float
) -> datahub_v1_workspace_approval_service_pb2.DelegateWorkspaceApprovalResponse:
    return await client.DelegateWorkspaceApproval(request, timeout=timeout)


class DataShareValidationCheckDataShareEligibility3Port(Protocol):
    async def execute(
        self,
        request: featureflags_v1_feature_flag_validation_service_pb2.ScoreFeatureFlagRequest
    ) -> featureflags_v1_feature_flag_validation_service_pb2.ScoreFeatureFlagResponse: ...


class DataShareValidationCheckDataShareEligibility3Adapter:
    def __init__(
        self,
        client: featureflags_v1_feature_flag_validation_service_pb2_grpc.FeatureFlagValidationServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def execute(
        self,
        request: featureflags_v1_feature_flag_validation_service_pb2.ScoreFeatureFlagRequest
    ) -> featureflags_v1_feature_flag_validation_service_pb2.ScoreFeatureFlagResponse:
        return await self.client.ScoreFeatureFlag(request, timeout=self.timeout)


async def data_share_validation_validate_data_share0(
    client: datahub_v1_workspace_approval_service_pb2_grpc.WorkspaceApprovalServiceStub,
    request: datahub_v1_workspace_approval_service_pb2.SubmitWorkspaceRequest,
    timeout: float
) -> datahub_v1_workspace_approval_service_pb2.SubmitWorkspaceResponse:
    return await client.SubmitWorkspace(request, timeout=timeout)


class DataShareValidationValidateDataShare2Port(Protocol):
    async def execute(
        self,
        request: datahub_v1_workspace_approval_service_pb2.RecallWorkspaceRequest
    ) -> datahub_v1_workspace_approval_service_pb2.RecallWorkspaceResponse: ...


class DataShareValidationValidateDataShare2Adapter:
    def __init__(
        self,
        client: datahub_v1_workspace_approval_service_pb2_grpc.WorkspaceApprovalServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def execute(
        self,
        request: datahub_v1_workspace_approval_service_pb2.RecallWorkspaceRequest
    ) -> datahub_v1_workspace_approval_service_pb2.RecallWorkspaceResponse:
        return await self.client.RecallWorkspace(request, timeout=self.timeout)


async def data_share_workflow_retry_data_share_workflow2(
    client: customers_v1_preference_sync_service_pb2_grpc.PreferenceSyncServiceStub,
    request: customers_v1_preference_sync_service_pb2.ResolvePreferenceConflictRequest,
    timeout: float
) -> customers_v1_preference_sync_service_pb2.ResolvePreferenceConflictResponse:
    return await client.ResolvePreferenceConflict(request, timeout=timeout)


class DataShareWorkflowSignalDataShareWorkflow0Port(Protocol):
    async def execute(
        self,
        request: datahub_v1_data_share_reporting_service_pb2.DeleteDataShareReportRequest
    ) -> datahub_v1_data_share_reporting_service_pb2.DeleteDataShareReportResponse: ...


class DataShareWorkflowSignalDataShareWorkflow0Adapter:
    def __init__(
        self,
        client: datahub_v1_data_share_reporting_service_pb2_grpc.DataShareReportingServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def execute(
        self,
        request: datahub_v1_data_share_reporting_service_pb2.DeleteDataShareReportRequest
    ) -> datahub_v1_data_share_reporting_service_pb2.DeleteDataShareReportResponse:
        return await self.client.DeleteDataShareReport(request, timeout=self.timeout)


class DataShareWorkflowSignalDataShareWorkflow2Adapter:
    def __init__(
        self,
        client: datahub_v1_notebook_approval_service_pb2_grpc.NotebookApprovalServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def __call__(
        self,
        request: datahub_v1_notebook_approval_service_pb2.RejectNotebookRequest
    ) -> datahub_v1_notebook_approval_service_pb2.RejectNotebookResponse:
        return await self.client.RejectNotebook(request, timeout=self.timeout)


async def notebook_integration_connect_notebook_source0(
    client: analytics_v1_analytics_event_approval_service_pb2_grpc.AnalyticsEventApprovalServiceStub,
    request: analytics_v1_analytics_event_approval_service_pb2.EscalateAnalyticsEventRequest,
    timeout: float
) -> analytics_v1_analytics_event_approval_service_pb2.EscalateAnalyticsEventResponse:
    return await client.EscalateAnalyticsEvent(request, timeout=timeout)


class NotebookIntegrationConnectNotebookSource2Port(Protocol):
    async def execute(
        self,
        request: datahub_v1_workspace_integration_service_pb2.AcknowledgeWorkspaceEventRequest
    ) -> datahub_v1_workspace_integration_service_pb2.AcknowledgeWorkspaceEventResponse: ...


class NotebookIntegrationConnectNotebookSource2Adapter:
    def __init__(
        self,
        client: datahub_v1_workspace_integration_service_pb2_grpc.WorkspaceIntegrationServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def execute(
        self,
        request: datahub_v1_workspace_integration_service_pb2.AcknowledgeWorkspaceEventRequest
    ) -> datahub_v1_workspace_integration_service_pb2.AcknowledgeWorkspaceEventResponse:
        return await self.client.AcknowledgeWorkspaceEvent(request, timeout=self.timeout)


class NotebookIntegrationDisconnectNotebookSource1Adapter:
    def __init__(
        self,
        client: datahub_v1_workspace_workflow_service_pb2_grpc.WorkspaceWorkflowServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def __call__(
        self,
        request: datahub_v1_workspace_workflow_service_pb2.StartWorkspaceWorkflowRequest
    ) -> datahub_v1_workspace_workflow_service_pb2.StartWorkspaceWorkflowResponse:
        return await self.client.StartWorkspaceWorkflow(request, timeout=self.timeout)


async def notebook_notification_notify_notebook_watchers2(
    client: datahub_v1_data_share_workflow_service_pb2_grpc.DataShareWorkflowServiceStub,
    request: datahub_v1_data_share_workflow_service_pb2.PauseDataShareWorkflowRequest,
    timeout: float
) -> datahub_v1_data_share_workflow_service_pb2.PauseDataShareWorkflowResponse:
    return await client.PauseDataShareWorkflow(request, timeout=timeout)


class NotebookNotificationSendNotebookTestNotice1Port(Protocol):
    async def execute(
        self,
        request: pipelines_v1_pipeline_run_workflow_service_pb2.StartPipelineRunWorkflowRequest
    ) -> pipelines_v1_pipeline_run_workflow_service_pb2.StartPipelineRunWorkflowResponse: ...


class NotebookNotificationSendNotebookTestNotice1Adapter:
    def __init__(
        self,
        client: pipelines_v1_pipeline_run_workflow_service_pb2_grpc.PipelineRunWorkflowServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def execute(
        self,
        request: pipelines_v1_pipeline_run_workflow_service_pb2.StartPipelineRunWorkflowRequest
    ) -> pipelines_v1_pipeline_run_workflow_service_pb2.StartPipelineRunWorkflowResponse:
        return await self.client.StartPipelineRunWorkflow(request, timeout=self.timeout)


class NotebookNotificationStreamNotebookNotices1Adapter:
    def __init__(
        self,
        client: customers_v1_customer_approval_service_pb2_grpc.CustomerApprovalServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def __call__(
        self,
        request: customers_v1_customer_approval_service_pb2.ListPendingCustomersRequest
    ) -> customers_v1_customer_approval_service_pb2.ListPendingCustomersResponse:
        return await self.client.ListPendingCustomers(request, timeout=self.timeout)


class NotebookReportingDeleteNotebookReport1Adapter:
    def __init__(
        self,
        client: datahub_v1_notebook_approval_service_pb2_grpc.NotebookApprovalServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def __call__(
        self,
        request: datahub_v1_notebook_approval_service_pb2.EscalateNotebookRequest
    ) -> datahub_v1_notebook_approval_service_pb2.EscalateNotebookResponse:
        return await self.client.EscalateNotebook(request, timeout=self.timeout)


async def notebook_reporting_share_notebook_report1(
    client: identity_v1_user_query_service_pb2_grpc.UserQueryServiceStub,
    request: identity_v1_user_query_service_pb2.FindUsersRequest,
    timeout: float
) -> identity_v1_user_query_service_pb2.FindUsersResponse:
    return await client.FindUsers(request, timeout=timeout)


class NotebookReportingStreamNotebookMetrics0Port(Protocol):
    async def execute(
        self,
        request: datahub_v1_workspace_reporting_service_pb2.ShareWorkspaceReportRequest
    ) -> datahub_v1_workspace_reporting_service_pb2.ShareWorkspaceReportResponse: ...


class NotebookReportingStreamNotebookMetrics0Adapter:
    def __init__(
        self,
        client: datahub_v1_workspace_reporting_service_pb2_grpc.WorkspaceReportingServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def execute(
        self,
        request: datahub_v1_workspace_reporting_service_pb2.ShareWorkspaceReportRequest
    ) -> datahub_v1_workspace_reporting_service_pb2.ShareWorkspaceReportResponse:
        return await self.client.ShareWorkspaceReport(request, timeout=self.timeout)


class NotebookWatchNotebooks1Adapter:
    def __init__(
        self,
        client: metrics_v1_metric_alert_validation_service_pb2_grpc.MetricAlertValidationServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def __call__(
        self,
        request: metrics_v1_metric_alert_validation_service_pb2.ExplainMetricAlertDecisionRequest
    ) -> metrics_v1_metric_alert_validation_service_pb2.ExplainMetricAlertDecisionResponse:
        return await self.client.ExplainMetricAlertDecision(request, timeout=self.timeout)


async def notebook_workflow_pause_notebook_workflow3(
    client: documents_v1_document_service_pb2_grpc.DocumentServiceStub,
    request: documents_v1_document_service_pb2.ListDocumentsRequest,
    timeout: float
) -> documents_v1_document_service_pb2.ListDocumentsResponse:
    return await client.ListDocuments(request, timeout=timeout)


class NotebookWorkflowResumeNotebookWorkflow1Port(Protocol):
    async def execute(
        self,
        request: anomalies_v1_anomaly_workflow_service_pb2.StartAnomalyWorkflowRequest
    ) -> anomalies_v1_anomaly_workflow_service_pb2.StartAnomalyWorkflowResponse: ...


class NotebookWorkflowResumeNotebookWorkflow1Adapter:
    def __init__(
        self,
        client: anomalies_v1_anomaly_workflow_service_pb2_grpc.AnomalyWorkflowServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def execute(
        self,
        request: anomalies_v1_anomaly_workflow_service_pb2.StartAnomalyWorkflowRequest
    ) -> anomalies_v1_anomaly_workflow_service_pb2.StartAnomalyWorkflowResponse:
        return await self.client.StartAnomalyWorkflow(request, timeout=self.timeout)


class NotebookWorkflowResumeNotebookWorkflow3Adapter:
    def __init__(
        self,
        client: datahub_v1_workspace_workflow_service_pb2_grpc.WorkspaceWorkflowServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def __call__(
        self,
        request: datahub_v1_workspace_workflow_service_pb2.CancelWorkspaceWorkflowRequest
    ) -> datahub_v1_workspace_workflow_service_pb2.CancelWorkspaceWorkflowResponse:
        return await self.client.CancelWorkspaceWorkflow(request, timeout=self.timeout)


async def workspace_approval_comment_workspace_approval0(
    client: customers_v1_consent_record_approval_service_pb2_grpc.ConsentRecordApprovalServiceStub,
    request: customers_v1_consent_record_approval_service_pb2.RecallConsentRecordRequest,
    timeout: float
) -> customers_v1_consent_record_approval_service_pb2.RecallConsentRecordResponse:
    return await client.RecallConsentRecord(request, timeout=timeout)


class WorkspaceApprovalCommentWorkspaceApproval2Port(Protocol):
    async def execute(
        self,
        request: analytics_v1_analytics_report_approval_service_pb2.CommentAnalyticsReportApprovalRequest
    ) -> analytics_v1_analytics_report_approval_service_pb2.CommentAnalyticsReportApprovalResponse: ...


class WorkspaceApprovalCommentWorkspaceApproval2Adapter:
    def __init__(
        self,
        client: analytics_v1_analytics_report_approval_service_pb2_grpc.AnalyticsReportApprovalServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def execute(
        self,
        request: analytics_v1_analytics_report_approval_service_pb2.CommentAnalyticsReportApprovalRequest
    ) -> analytics_v1_analytics_report_approval_service_pb2.CommentAnalyticsReportApprovalResponse:
        return await self.client.CommentAnalyticsReportApproval(request, timeout=self.timeout)


class WorkspaceApprovalDelegateWorkspaceApproval1Adapter:
    def __init__(
        self,
        client: featureflags_v1_feature_flag_service_pb2_grpc.FeatureFlagServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def __call__(
        self,
        request: featureflags_v1_feature_flag_service_pb2.CreateFeatureFlagRequest
    ) -> featureflags_v1_feature_flag_service_pb2.CreateFeatureFlagResponse:
        return await self.client.CreateFeatureFlag(request, timeout=self.timeout)


class WorkspaceGatewayComposeWorkspacePage2Port(Protocol):
    async def execute(
        self,
        request: datahub_v1_notebook_integration_service_pb2.ConnectNotebookSourceRequest
    ) -> datahub_v1_notebook_integration_service_pb2.ConnectNotebookSourceResponse: ...


class WorkspaceGatewayComposeWorkspacePage2Adapter:
    def __init__(
        self,
        client: datahub_v1_notebook_integration_service_pb2_grpc.NotebookIntegrationServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def execute(
        self,
        request: datahub_v1_notebook_integration_service_pb2.ConnectNotebookSourceRequest
    ) -> datahub_v1_notebook_integration_service_pb2.ConnectNotebookSourceResponse:
        return await self.client.ConnectNotebookSource(request, timeout=self.timeout)


class WorkspaceGatewayUploadWorkspaceAttachments0Port(Protocol):
    async def execute(
        self,
        request: datahub_v1_data_share_workflow_service_pb2.CancelDataShareWorkflowRequest
    ) -> datahub_v1_data_share_workflow_service_pb2.CancelDataShareWorkflowResponse: ...


class WorkspaceGatewayUploadWorkspaceAttachments0Adapter:
    def __init__(
        self,
        client: datahub_v1_data_share_workflow_service_pb2_grpc.DataShareWorkflowServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def execute(
        self,
        request: datahub_v1_data_share_workflow_service_pb2.CancelDataShareWorkflowRequest
    ) -> datahub_v1_data_share_workflow_service_pb2.CancelDataShareWorkflowResponse:
        return await self.client.CancelDataShareWorkflow(request, timeout=self.timeout)


class WorkspaceIntegrationAcknowledgeWorkspaceEvent0Adapter:
    def __init__(
        self,
        client: datahub_v1_workspace_reporting_service_pb2_grpc.WorkspaceReportingServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def __call__(
        self,
        request: datahub_v1_workspace_reporting_service_pb2.FetchWorkspaceReportRequest
    ) -> datahub_v1_workspace_reporting_service_pb2.FetchWorkspaceReportResponse:
        return await self.client.FetchWorkspaceReport(request, timeout=self.timeout)


async def workspace_integration_replay_workspace_events0(
    client: datahub_v1_data_share_approval_service_pb2_grpc.DataShareApprovalServiceStub,
    request: datahub_v1_data_share_approval_service_pb2.ApproveDataShareRequest,
    timeout: float
) -> datahub_v1_data_share_approval_service_pb2.ApproveDataShareResponse:
    return await client.ApproveDataShare(request, timeout=timeout)


class WorkspaceIntegrationTestWorkspaceConnection0Port(Protocol):
    async def execute(
        self,
        request: metrics_v1_metric_series_admin_service_pb2.RepairMetricSeriesRequest
    ) -> metrics_v1_metric_series_admin_service_pb2.RepairMetricSeriesResponse: ...


class WorkspaceIntegrationTestWorkspaceConnection0Adapter:
    def __init__(
        self,
        client: metrics_v1_metric_series_admin_service_pb2_grpc.MetricSeriesAdminServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def execute(
        self,
        request: metrics_v1_metric_series_admin_service_pb2.RepairMetricSeriesRequest
    ) -> metrics_v1_metric_series_admin_service_pb2.RepairMetricSeriesResponse:
        return await self.client.RepairMetricSeries(request, timeout=self.timeout)


class WorkspaceIntegrationTestWorkspaceConnection2Adapter:
    def __init__(
        self,
        client: datahub_v1_workspace_workflow_service_pb2_grpc.WorkspaceWorkflowServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def __call__(
        self,
        request: datahub_v1_workspace_workflow_service_pb2.AdvanceWorkspaceWorkflowRequest
    ) -> datahub_v1_workspace_workflow_service_pb2.AdvanceWorkspaceWorkflowResponse:
        return await self.client.AdvanceWorkspaceWorkflow(request, timeout=self.timeout)


async def workspace_notification_subscribe_workspace_updates1(
    client: fanportal_v1_fan_session_query_service_pb2_grpc.FanSessionQueryServiceStub,
    request: fanportal_v1_fan_session_query_service_pb2.CountFanSessionsRequest,
    timeout: float
) -> fanportal_v1_fan_session_query_service_pb2.CountFanSessionsResponse:
    return await client.CountFanSessions(request, timeout=timeout)


class WorkspaceNotificationUnsubscribeWorkspaceUpdates2Adapter:
    def __init__(
        self,
        client: customers_v1_household_workflow_service_pb2_grpc.HouseholdWorkflowServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def __call__(
        self,
        request: customers_v1_household_workflow_service_pb2.ResumeHouseholdWorkflowRequest
    ) -> customers_v1_household_workflow_service_pb2.ResumeHouseholdWorkflowResponse:
        return await self.client.ResumeHouseholdWorkflow(request, timeout=self.timeout)


async def workspace_reporting_count_workspace_totals1(
    client: datahub_v1_workspace_approval_service_pb2_grpc.WorkspaceApprovalServiceStub,
    request: datahub_v1_workspace_approval_service_pb2.RecallWorkspaceRequest,
    timeout: float
) -> datahub_v1_workspace_approval_service_pb2.RecallWorkspaceResponse:
    return await client.RecallWorkspace(request, timeout=timeout)


class WorkspaceReportingDeleteWorkspaceReport1Port(Protocol):
    async def execute(
        self,
        request: forecasting_v1_demand_forecast_approval_service_pb2.EscalateDemandForecastRequest
    ) -> forecasting_v1_demand_forecast_approval_service_pb2.EscalateDemandForecastResponse: ...


class WorkspaceReportingDeleteWorkspaceReport1Adapter:
    def __init__(
        self,
        client: forecasting_v1_demand_forecast_approval_service_pb2_grpc.DemandForecastApprovalServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def execute(
        self,
        request: forecasting_v1_demand_forecast_approval_service_pb2.EscalateDemandForecastRequest
    ) -> forecasting_v1_demand_forecast_approval_service_pb2.EscalateDemandForecastResponse:
        return await self.client.EscalateDemandForecast(request, timeout=self.timeout)


async def workspace_batch_create_workspaces0(
    client: labeling_v1_label_set_approval_service_pb2_grpc.LabelSetApprovalServiceStub,
    request: labeling_v1_label_set_approval_service_pb2.RecallLabelSetRequest,
    timeout: float
) -> labeling_v1_label_set_approval_service_pb2.RecallLabelSetResponse:
    return await client.RecallLabelSet(request, timeout=timeout)


class WorkspaceBatchCreateWorkspaces2Port(Protocol):
    async def execute(
        self,
        request: pipelines_v1_pipeline_step_reporting_service_pb2.SchedulePipelineStepReportRequest
    ) -> pipelines_v1_pipeline_step_reporting_service_pb2.SchedulePipelineStepReportResponse: ...


class WorkspaceBatchCreateWorkspaces2Adapter:
    def __init__(
        self,
        client: pipelines_v1_pipeline_step_reporting_service_pb2_grpc.PipelineStepReportingServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def execute(
        self,
        request: pipelines_v1_pipeline_step_reporting_service_pb2.SchedulePipelineStepReportRequest
    ) -> pipelines_v1_pipeline_step_reporting_service_pb2.SchedulePipelineStepReportResponse:
        return await self.client.SchedulePipelineStepReport(request, timeout=self.timeout)


async def workspace_search_workspaces1(
    client: customers_v1_customer_workflow_service_pb2_grpc.CustomerWorkflowServiceStub,
    request: customers_v1_customer_workflow_service_pb2.ListCustomerWorkflowsRequest,
    timeout: float
) -> customers_v1_customer_workflow_service_pb2.ListCustomerWorkflowsResponse:
    return await client.ListCustomerWorkflows(request, timeout=timeout)


class WorkspaceUpdateWorkspace1Port(Protocol):
    async def execute(
        self,
        request: featurestore_v1_feature_value_reporting_service_pb2.GenerateFeatureValueReportRequest
    ) -> featurestore_v1_feature_value_reporting_service_pb2.GenerateFeatureValueReportResponse: ...


class WorkspaceUpdateWorkspace1Adapter:
    def __init__(
        self,
        client: featurestore_v1_feature_value_reporting_service_pb2_grpc.FeatureValueReportingServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def execute(
        self,
        request: featurestore_v1_feature_value_reporting_service_pb2.GenerateFeatureValueReportRequest
    ) -> featurestore_v1_feature_value_reporting_service_pb2.GenerateFeatureValueReportResponse:
        return await self.client.GenerateFeatureValueReport(request, timeout=self.timeout)


class WorkspaceWatchWorkspaces0Adapter:
    def __init__(
        self,
        client: datahub_v1_workspace_integration_service_pb2_grpc.WorkspaceIntegrationServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def __call__(
        self,
        request: datahub_v1_workspace_integration_service_pb2.AcknowledgeWorkspaceEventRequest
    ) -> datahub_v1_workspace_integration_service_pb2.AcknowledgeWorkspaceEventResponse:
        return await self.client.AcknowledgeWorkspaceEvent(request, timeout=self.timeout)


class WorkspaceWorkflowResumeWorkspaceWorkflow2Port(Protocol):
    async def execute(
        self,
        request: datahub_v1_data_share_approval_service_pb2.SubmitDataShareRequest
    ) -> datahub_v1_data_share_approval_service_pb2.SubmitDataShareResponse: ...


class WorkspaceWorkflowResumeWorkspaceWorkflow2Adapter:
    def __init__(
        self,
        client: datahub_v1_data_share_approval_service_pb2_grpc.DataShareApprovalServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def execute(
        self,
        request: datahub_v1_data_share_approval_service_pb2.SubmitDataShareRequest
    ) -> datahub_v1_data_share_approval_service_pb2.SubmitDataShareResponse:
        return await self.client.SubmitDataShare(request, timeout=self.timeout)
