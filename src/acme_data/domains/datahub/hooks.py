"""Replaceable partner hooks of the datahub domain."""

from __future__ import annotations

from acme.analytics.v1 import analytics_event_approval_service_pb2 as analytics_v1_analytics_event_approval_service_pb2
from acme.analytics.v1 import (
    analytics_event_approval_service_pb2_grpc as analytics_v1_analytics_event_approval_service_pb2_grpc,
)
from acme.customers.v1 import consent_record_approval_service_pb2 as customers_v1_consent_record_approval_service_pb2
from acme.customers.v1 import (
    consent_record_approval_service_pb2_grpc as customers_v1_consent_record_approval_service_pb2_grpc,
)
from acme.customers.v1 import customer_workflow_service_pb2 as customers_v1_customer_workflow_service_pb2
from acme.customers.v1 import customer_workflow_service_pb2_grpc as customers_v1_customer_workflow_service_pb2_grpc
from acme.customers.v1 import household_reporting_service_pb2 as customers_v1_household_reporting_service_pb2
from acme.customers.v1 import household_reporting_service_pb2_grpc as customers_v1_household_reporting_service_pb2_grpc
from acme.customers.v1 import preference_sync_service_pb2 as customers_v1_preference_sync_service_pb2
from acme.customers.v1 import preference_sync_service_pb2_grpc as customers_v1_preference_sync_service_pb2_grpc
from acme.datahub.v1 import data_share_approval_service_pb2 as datahub_v1_data_share_approval_service_pb2
from acme.datahub.v1 import data_share_approval_service_pb2_grpc as datahub_v1_data_share_approval_service_pb2_grpc
from acme.datahub.v1 import data_share_validation_service_pb2 as datahub_v1_data_share_validation_service_pb2
from acme.datahub.v1 import data_share_validation_service_pb2_grpc as datahub_v1_data_share_validation_service_pb2_grpc
from acme.datahub.v1 import data_share_workflow_service_pb2 as datahub_v1_data_share_workflow_service_pb2
from acme.datahub.v1 import data_share_workflow_service_pb2_grpc as datahub_v1_data_share_workflow_service_pb2_grpc
from acme.datahub.v1 import workspace_approval_service_pb2 as datahub_v1_workspace_approval_service_pb2
from acme.datahub.v1 import workspace_approval_service_pb2_grpc as datahub_v1_workspace_approval_service_pb2_grpc
from acme.documents.v1 import document_service_pb2 as documents_v1_document_service_pb2
from acme.documents.v1 import document_service_pb2_grpc as documents_v1_document_service_pb2_grpc
from acme.fanportal.v1 import fan_session_query_service_pb2 as fanportal_v1_fan_session_query_service_pb2
from acme.fanportal.v1 import fan_session_query_service_pb2_grpc as fanportal_v1_fan_session_query_service_pb2_grpc
from acme.identity.v1 import user_query_service_pb2 as identity_v1_user_query_service_pb2
from acme.identity.v1 import user_query_service_pb2_grpc as identity_v1_user_query_service_pb2_grpc
from acme.labeling.v1 import label_set_approval_service_pb2 as labeling_v1_label_set_approval_service_pb2
from acme.labeling.v1 import label_set_approval_service_pb2_grpc as labeling_v1_label_set_approval_service_pb2_grpc
from acme.search.v1 import search_index_validation_service_pb2 as search_v1_search_index_validation_service_pb2
from acme.search.v1 import (
    search_index_validation_service_pb2_grpc as search_v1_search_index_validation_service_pb2_grpc,
)


async def data_share_approval_approve_data_share0(
    client: datahub_v1_data_share_validation_service_pb2_grpc.DataShareValidationServiceStub,
    request: datahub_v1_data_share_validation_service_pb2.ScoreDataShareRequest,
    timeout: float
) -> datahub_v1_data_share_validation_service_pb2.ScoreDataShareResponse:
    raise RuntimeError("domain hook was not installed")


async def data_share_approval_reject_data_share3(
    client: customers_v1_household_reporting_service_pb2_grpc.HouseholdReportingServiceStub,
    request: customers_v1_household_reporting_service_pb2.ListHouseholdReportsRequest,
    timeout: float
) -> customers_v1_household_reporting_service_pb2.ListHouseholdReportsResponse:
    raise RuntimeError("domain hook was not installed")


async def data_share_notification_unsubscribe_data_share_updates1(
    client: search_v1_search_index_validation_service_pb2_grpc.SearchIndexValidationServiceStub,
    request: search_v1_search_index_validation_service_pb2.LintSearchIndexesRequest,
    timeout: float
) -> search_v1_search_index_validation_service_pb2.LintSearchIndexesResponse:
    raise RuntimeError("domain hook was not installed")


async def data_share_validation_check_data_share_eligibility1(
    client: datahub_v1_workspace_approval_service_pb2_grpc.WorkspaceApprovalServiceStub,
    request: datahub_v1_workspace_approval_service_pb2.DelegateWorkspaceApprovalRequest,
    timeout: float
) -> datahub_v1_workspace_approval_service_pb2.DelegateWorkspaceApprovalResponse:
    raise RuntimeError("domain hook was not installed")


async def data_share_validation_validate_data_share0(
    client: datahub_v1_workspace_approval_service_pb2_grpc.WorkspaceApprovalServiceStub,
    request: datahub_v1_workspace_approval_service_pb2.SubmitWorkspaceRequest,
    timeout: float
) -> datahub_v1_workspace_approval_service_pb2.SubmitWorkspaceResponse:
    raise RuntimeError("domain hook was not installed")


async def data_share_workflow_retry_data_share_workflow2(
    client: customers_v1_preference_sync_service_pb2_grpc.PreferenceSyncServiceStub,
    request: customers_v1_preference_sync_service_pb2.ResolvePreferenceConflictRequest,
    timeout: float
) -> customers_v1_preference_sync_service_pb2.ResolvePreferenceConflictResponse:
    raise RuntimeError("domain hook was not installed")


async def notebook_integration_connect_notebook_source0(
    client: analytics_v1_analytics_event_approval_service_pb2_grpc.AnalyticsEventApprovalServiceStub,
    request: analytics_v1_analytics_event_approval_service_pb2.EscalateAnalyticsEventRequest,
    timeout: float
) -> analytics_v1_analytics_event_approval_service_pb2.EscalateAnalyticsEventResponse:
    raise RuntimeError("domain hook was not installed")


async def notebook_notification_notify_notebook_watchers2(
    client: datahub_v1_data_share_workflow_service_pb2_grpc.DataShareWorkflowServiceStub,
    request: datahub_v1_data_share_workflow_service_pb2.PauseDataShareWorkflowRequest,
    timeout: float
) -> datahub_v1_data_share_workflow_service_pb2.PauseDataShareWorkflowResponse:
    raise RuntimeError("domain hook was not installed")


async def notebook_reporting_share_notebook_report1(
    client: identity_v1_user_query_service_pb2_grpc.UserQueryServiceStub,
    request: identity_v1_user_query_service_pb2.FindUsersRequest,
    timeout: float
) -> identity_v1_user_query_service_pb2.FindUsersResponse:
    raise RuntimeError("domain hook was not installed")


async def notebook_workflow_pause_notebook_workflow3(
    client: documents_v1_document_service_pb2_grpc.DocumentServiceStub,
    request: documents_v1_document_service_pb2.ListDocumentsRequest,
    timeout: float
) -> documents_v1_document_service_pb2.ListDocumentsResponse:
    raise RuntimeError("domain hook was not installed")


async def workspace_approval_comment_workspace_approval0(
    client: customers_v1_consent_record_approval_service_pb2_grpc.ConsentRecordApprovalServiceStub,
    request: customers_v1_consent_record_approval_service_pb2.RecallConsentRecordRequest,
    timeout: float
) -> customers_v1_consent_record_approval_service_pb2.RecallConsentRecordResponse:
    raise RuntimeError("domain hook was not installed")


async def workspace_integration_replay_workspace_events0(
    client: datahub_v1_data_share_approval_service_pb2_grpc.DataShareApprovalServiceStub,
    request: datahub_v1_data_share_approval_service_pb2.ApproveDataShareRequest,
    timeout: float
) -> datahub_v1_data_share_approval_service_pb2.ApproveDataShareResponse:
    raise RuntimeError("domain hook was not installed")


async def workspace_notification_subscribe_workspace_updates1(
    client: fanportal_v1_fan_session_query_service_pb2_grpc.FanSessionQueryServiceStub,
    request: fanportal_v1_fan_session_query_service_pb2.CountFanSessionsRequest,
    timeout: float
) -> fanportal_v1_fan_session_query_service_pb2.CountFanSessionsResponse:
    raise RuntimeError("domain hook was not installed")


async def workspace_reporting_count_workspace_totals1(
    client: datahub_v1_workspace_approval_service_pb2_grpc.WorkspaceApprovalServiceStub,
    request: datahub_v1_workspace_approval_service_pb2.RecallWorkspaceRequest,
    timeout: float
) -> datahub_v1_workspace_approval_service_pb2.RecallWorkspaceResponse:
    raise RuntimeError("domain hook was not installed")


async def workspace_batch_create_workspaces0(
    client: labeling_v1_label_set_approval_service_pb2_grpc.LabelSetApprovalServiceStub,
    request: labeling_v1_label_set_approval_service_pb2.RecallLabelSetRequest,
    timeout: float
) -> labeling_v1_label_set_approval_service_pb2.RecallLabelSetResponse:
    raise RuntimeError("domain hook was not installed")


async def workspace_search_workspaces1(
    client: customers_v1_customer_workflow_service_pb2_grpc.CustomerWorkflowServiceStub,
    request: customers_v1_customer_workflow_service_pb2.ListCustomerWorkflowsRequest,
    timeout: float
) -> customers_v1_customer_workflow_service_pb2.ListCustomerWorkflowsResponse:
    raise RuntimeError("domain hook was not installed")
