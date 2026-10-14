"""Transport adapters used by datasets workflows."""

from __future__ import annotations

from typing import Protocol

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
from acme.billing.v1 import billing_account_query_service_pb2 as billing_v1_billing_account_query_service_pb2
from acme.billing.v1 import billing_account_query_service_pb2_grpc as billing_v1_billing_account_query_service_pb2_grpc
from acme.customers.v1 import preference_calculation_service_pb2 as customers_v1_preference_calculation_service_pb2
from acme.customers.v1 import (
    preference_calculation_service_pb2_grpc as customers_v1_preference_calculation_service_pb2_grpc,
)
from acme.datasets.v1 import data_schema_approval_service_pb2 as datasets_v1_data_schema_approval_service_pb2
from acme.datasets.v1 import data_schema_approval_service_pb2_grpc as datasets_v1_data_schema_approval_service_pb2_grpc
from acme.datasets.v1 import data_schema_calculation_service_pb2 as datasets_v1_data_schema_calculation_service_pb2
from acme.datasets.v1 import (
    data_schema_calculation_service_pb2_grpc as datasets_v1_data_schema_calculation_service_pb2_grpc,
)
from acme.datasets.v1 import dataset_approval_service_pb2 as datasets_v1_dataset_approval_service_pb2
from acme.datasets.v1 import dataset_approval_service_pb2_grpc as datasets_v1_dataset_approval_service_pb2_grpc
from acme.datasets.v1 import dataset_query_service_pb2 as datasets_v1_dataset_query_service_pb2
from acme.datasets.v1 import dataset_query_service_pb2_grpc as datasets_v1_dataset_query_service_pb2_grpc
from acme.datasets.v1 import dataset_validation_service_pb2 as datasets_v1_dataset_validation_service_pb2
from acme.datasets.v1 import dataset_validation_service_pb2_grpc as datasets_v1_dataset_validation_service_pb2_grpc
from acme.datasets.v1 import (
    dataset_version_calculation_service_pb2 as datasets_v1_dataset_version_calculation_service_pb2,
)
from acme.datasets.v1 import (
    dataset_version_calculation_service_pb2_grpc as datasets_v1_dataset_version_calculation_service_pb2_grpc,
)
from acme.featurestore.v1 import (
    feature_value_calculation_service_pb2 as featurestore_v1_feature_value_calculation_service_pb2,
)
from acme.featurestore.v1 import (
    feature_value_calculation_service_pb2_grpc as featurestore_v1_feature_value_calculation_service_pb2_grpc,
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
from acme.featurestore.v1 import (
    feature_view_calculation_service_pb2 as featurestore_v1_feature_view_calculation_service_pb2,
)
from acme.featurestore.v1 import (
    feature_view_calculation_service_pb2_grpc as featurestore_v1_feature_view_calculation_service_pb2_grpc,
)
from acme.identity.v1 import user_service_pb2 as identity_v1_user_service_pb2
from acme.identity.v1 import user_service_pb2_grpc as identity_v1_user_service_pb2_grpc
from acme.labeling.v1 import label_set_sync_service_pb2 as labeling_v1_label_set_sync_service_pb2
from acme.labeling.v1 import label_set_sync_service_pb2_grpc as labeling_v1_label_set_sync_service_pb2_grpc
from acme.lineage.v1 import lineage_edge_calculation_service_pb2 as lineage_v1_lineage_edge_calculation_service_pb2
from acme.lineage.v1 import (
    lineage_edge_calculation_service_pb2_grpc as lineage_v1_lineage_edge_calculation_service_pb2_grpc,
)
from acme.metrics.v1 import metric_alert_history_service_pb2 as metrics_v1_metric_alert_history_service_pb2
from acme.metrics.v1 import metric_alert_history_service_pb2_grpc as metrics_v1_metric_alert_history_service_pb2_grpc
from acme.search.v1 import search_index_query_service_pb2 as search_v1_search_index_query_service_pb2
from acme.search.v1 import search_index_query_service_pb2_grpc as search_v1_search_index_query_service_pb2_grpc
from acme.ticketing.v1 import ticket_query_service_pb2 as ticketing_v1_ticket_query_service_pb2
from acme.ticketing.v1 import ticket_query_service_pb2_grpc as ticketing_v1_ticket_query_service_pb2_grpc


class DataSchemaApprovalDelegateDataSchemaApproval0Port(Protocol):
    async def execute(
        self,
        request: datasets_v1_dataset_query_service_pb2.SummarizeDatasetsRequest
    ) -> datasets_v1_dataset_query_service_pb2.SummarizeDatasetsResponse: ...


class DataSchemaApprovalDelegateDataSchemaApproval0Adapter:
    def __init__(
        self,
        client: datasets_v1_dataset_query_service_pb2_grpc.DatasetQueryServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def execute(
        self,
        request: datasets_v1_dataset_query_service_pb2.SummarizeDatasetsRequest
    ) -> datasets_v1_dataset_query_service_pb2.SummarizeDatasetsResponse:
        return await self.client.SummarizeDatasets(request, timeout=self.timeout)


class DataSchemaApprovalDelegateDataSchemaApproval2Adapter:
    def __init__(
        self,
        client: labeling_v1_label_set_sync_service_pb2_grpc.LabelSetSyncServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def __call__(
        self,
        request: labeling_v1_label_set_sync_service_pb2.SyncLabelSetsRequest
    ) -> labeling_v1_label_set_sync_service_pb2.SyncLabelSetsResponse:
        return await self.client.SyncLabelSets(request, timeout=self.timeout)


class DataSchemaApprovalRejectDataSchema3Port(Protocol):
    async def execute(
        self,
        request: datasets_v1_dataset_approval_service_pb2.CommentDatasetApprovalRequest
    ) -> datasets_v1_dataset_approval_service_pb2.CommentDatasetApprovalResponse: ...


class DataSchemaApprovalRejectDataSchema3Adapter:
    def __init__(
        self,
        client: datasets_v1_dataset_approval_service_pb2_grpc.DatasetApprovalServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def execute(
        self,
        request: datasets_v1_dataset_approval_service_pb2.CommentDatasetApprovalRequest
    ) -> datasets_v1_dataset_approval_service_pb2.CommentDatasetApprovalResponse:
        return await self.client.CommentDatasetApproval(request, timeout=self.timeout)


class DataSchemaApprovalSubmitDataSchema1Adapter:
    def __init__(
        self,
        client: customers_v1_preference_calculation_service_pb2_grpc.PreferenceCalculationServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def __call__(
        self,
        request: customers_v1_preference_calculation_service_pb2.EstimatePreferenceRequest
    ) -> customers_v1_preference_calculation_service_pb2.EstimatePreferenceResponse:
        return await self.client.EstimatePreference(request, timeout=self.timeout)


async def data_schema_calculation_quote_data_schema1(
    client: anomalies_v1_anomaly_validation_service_pb2_grpc.AnomalyValidationServiceStub,
    request: anomalies_v1_anomaly_validation_service_pb2.CheckAnomalyEligibilityRequest,
    timeout: float
) -> anomalies_v1_anomaly_validation_service_pb2.CheckAnomalyEligibilityResponse:
    return await client.CheckAnomalyEligibility(request, timeout=timeout)


class DataSchemaCalculationRecalculateDataSchemas0Port(Protocol):
    async def execute(
        self,
        request: datasets_v1_dataset_version_calculation_service_pb2.QuoteDatasetVersionRequest
    ) -> datasets_v1_dataset_version_calculation_service_pb2.QuoteDatasetVersionResponse: ...


class DataSchemaCalculationRecalculateDataSchemas0Adapter:
    def __init__(
        self,
        client: datasets_v1_dataset_version_calculation_service_pb2_grpc.DatasetVersionCalculationServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def execute(
        self,
        request: datasets_v1_dataset_version_calculation_service_pb2.QuoteDatasetVersionRequest
    ) -> datasets_v1_dataset_version_calculation_service_pb2.QuoteDatasetVersionResponse:
        return await self.client.QuoteDatasetVersion(request, timeout=self.timeout)


class DataSchemaValidationScoreDataSchema2Port(Protocol):
    async def execute(
        self,
        request: lineage_v1_lineage_edge_calculation_service_pb2.EstimateLineageEdgeRequest
    ) -> lineage_v1_lineage_edge_calculation_service_pb2.EstimateLineageEdgeResponse: ...


class DataSchemaValidationScoreDataSchema2Adapter:
    def __init__(
        self,
        client: lineage_v1_lineage_edge_calculation_service_pb2_grpc.LineageEdgeCalculationServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def execute(
        self,
        request: lineage_v1_lineage_edge_calculation_service_pb2.EstimateLineageEdgeRequest
    ) -> lineage_v1_lineage_edge_calculation_service_pb2.EstimateLineageEdgeResponse:
        return await self.client.EstimateLineageEdge(request, timeout=self.timeout)


async def data_schema_workflow_start_data_schema_workflow0(
    client: anomalies_v1_anomaly_feedback_workflow_service_pb2_grpc.AnomalyFeedbackWorkflowServiceStub,
    request: anomalies_v1_anomaly_feedback_workflow_service_pb2.AdvanceAnomalyFeedbackWorkflowRequest,
    timeout: float
) -> anomalies_v1_anomaly_feedback_workflow_service_pb2.AdvanceAnomalyFeedbackWorkflowResponse:
    return await client.AdvanceAnomalyFeedbackWorkflow(request, timeout=timeout)


class DataSchemaWorkflowStartDataSchemaWorkflow2Port(Protocol):
    async def execute(
        self,
        request: datasets_v1_data_schema_approval_service_pb2.RecallDataSchemaRequest
    ) -> datasets_v1_data_schema_approval_service_pb2.RecallDataSchemaResponse: ...


class DataSchemaWorkflowStartDataSchemaWorkflow2Adapter:
    def __init__(
        self,
        client: datasets_v1_data_schema_approval_service_pb2_grpc.DataSchemaApprovalServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def execute(
        self,
        request: datasets_v1_data_schema_approval_service_pb2.RecallDataSchemaRequest
    ) -> datasets_v1_data_schema_approval_service_pb2.RecallDataSchemaResponse:
        return await self.client.RecallDataSchema(request, timeout=self.timeout)


async def dataset_approval_reject_dataset1(
    client: featurestore_v1_feature_value_sync_service_pb2_grpc.FeatureValueSyncServiceStub,
    request: featurestore_v1_feature_value_sync_service_pb2.PushFeatureValueRequest,
    timeout: float
) -> featurestore_v1_feature_value_sync_service_pb2.PushFeatureValueResponse:
    return await client.PushFeatureValue(request, timeout=timeout)


class DatasetApprovalRejectDataset3Port(Protocol):
    async def execute(
        self,
        request: datasets_v1_data_schema_calculation_service_pb2.CompareDataSchemaOptionsRequest
    ) -> datasets_v1_data_schema_calculation_service_pb2.CompareDataSchemaOptionsResponse: ...


class DatasetApprovalRejectDataset3Adapter:
    def __init__(
        self,
        client: datasets_v1_data_schema_calculation_service_pb2_grpc.DataSchemaCalculationServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def execute(
        self,
        request: datasets_v1_data_schema_calculation_service_pb2.CompareDataSchemaOptionsRequest
    ) -> datasets_v1_data_schema_calculation_service_pb2.CompareDataSchemaOptionsResponse:
        return await self.client.CompareDataSchemaOptions(request, timeout=self.timeout)


async def dataset_batch_get_datasets1(
    client: featurestore_v1_feature_value_validation_service_pb2_grpc.FeatureValueValidationServiceStub,
    request: featurestore_v1_feature_value_validation_service_pb2.PreviewFeatureValueRequest,
    timeout: float
) -> featurestore_v1_feature_value_validation_service_pb2.PreviewFeatureValueResponse:
    return await client.PreviewFeatureValue(request, timeout=timeout)


class DatasetCloneDataset1Port(Protocol):
    async def execute(
        self,
        request: metrics_v1_metric_alert_history_service_pb2.CompareMetricAlertVersionsRequest
    ) -> metrics_v1_metric_alert_history_service_pb2.CompareMetricAlertVersionsResponse: ...


class DatasetCloneDataset1Adapter:
    def __init__(
        self,
        client: metrics_v1_metric_alert_history_service_pb2_grpc.MetricAlertHistoryServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def execute(
        self,
        request: metrics_v1_metric_alert_history_service_pb2.CompareMetricAlertVersionsRequest
    ) -> metrics_v1_metric_alert_history_service_pb2.CompareMetricAlertVersionsResponse:
        return await self.client.CompareMetricAlertVersions(request, timeout=self.timeout)


class DatasetCreateDataset1Adapter:
    def __init__(
        self,
        client: ticketing_v1_ticket_query_service_pb2_grpc.TicketQueryServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def __call__(
        self,
        request: ticketing_v1_ticket_query_service_pb2.SummarizeTicketsRequest
    ) -> ticketing_v1_ticket_query_service_pb2.SummarizeTicketsResponse:
        return await self.client.SummarizeTickets(request, timeout=self.timeout)


async def dataset_validation_check_dataset_eligibility3(
    client: datasets_v1_dataset_version_calculation_service_pb2_grpc.DatasetVersionCalculationServiceStub,
    request: datasets_v1_dataset_version_calculation_service_pb2.CalculateDatasetVersionRequest,
    timeout: float
) -> datasets_v1_dataset_version_calculation_service_pb2.CalculateDatasetVersionResponse:
    return await client.CalculateDatasetVersion(request, timeout=timeout)


async def dataset_validation_validate_dataset1(
    client: authorization_v1_access_policy_validation_service_pb2_grpc.AccessPolicyValidationServiceStub,
    request: authorization_v1_access_policy_validation_service_pb2.CheckAccessPolicyEligibilityRequest,
    timeout: float
) -> authorization_v1_access_policy_validation_service_pb2.CheckAccessPolicyEligibilityResponse:
    return await client.CheckAccessPolicyEligibility(request, timeout=timeout)


class DatasetVersionApprovalApproveDatasetVersion1Port(Protocol):
    async def execute(
        self,
        request: billing_v1_billing_account_query_service_pb2.ResolveBillingAccountsRequest
    ) -> billing_v1_billing_account_query_service_pb2.ResolveBillingAccountsResponse: ...


class DatasetVersionApprovalApproveDatasetVersion1Adapter:
    def __init__(
        self,
        client: billing_v1_billing_account_query_service_pb2_grpc.BillingAccountQueryServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def execute(
        self,
        request: billing_v1_billing_account_query_service_pb2.ResolveBillingAccountsRequest
    ) -> billing_v1_billing_account_query_service_pb2.ResolveBillingAccountsResponse:
        return await self.client.ResolveBillingAccounts(request, timeout=self.timeout)


class DatasetVersionApprovalCommentDatasetVersionApproval1Adapter:
    def __init__(
        self,
        client: datasets_v1_dataset_validation_service_pb2_grpc.DatasetValidationServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def __call__(
        self,
        request: datasets_v1_dataset_validation_service_pb2.ScoreDatasetRequest
    ) -> datasets_v1_dataset_validation_service_pb2.ScoreDatasetResponse:
        return await self.client.ScoreDataset(request, timeout=self.timeout)


class DatasetVersionCalculationCalculateDatasetVersion1Port(Protocol):
    async def execute(
        self,
        request: featurestore_v1_feature_view_calculation_service_pb2.QuoteFeatureViewRequest
    ) -> featurestore_v1_feature_view_calculation_service_pb2.QuoteFeatureViewResponse: ...


class DatasetVersionCalculationCalculateDatasetVersion1Adapter:
    def __init__(
        self,
        client: featurestore_v1_feature_view_calculation_service_pb2_grpc.FeatureViewCalculationServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def execute(
        self,
        request: featurestore_v1_feature_view_calculation_service_pb2.QuoteFeatureViewRequest
    ) -> featurestore_v1_feature_view_calculation_service_pb2.QuoteFeatureViewResponse:
        return await self.client.QuoteFeatureView(request, timeout=self.timeout)


async def dataset_version_calculation_simulate_dataset_version2(
    client: identity_v1_user_service_pb2_grpc.UserServiceStub,
    request: identity_v1_user_service_pb2.CloneUserRequest,
    timeout: float
) -> identity_v1_user_service_pb2.CloneUserResponse:
    return await client.CloneUser(request, timeout=timeout)


class DatasetVersionQueryBrowseDatasetVersions1Port(Protocol):
    async def execute(
        self,
        request: datasets_v1_data_schema_calculation_service_pb2.CalculateDataSchemaRequest
    ) -> datasets_v1_data_schema_calculation_service_pb2.CalculateDataSchemaResponse: ...


class DatasetVersionQueryBrowseDatasetVersions1Adapter:
    def __init__(
        self,
        client: datasets_v1_data_schema_calculation_service_pb2_grpc.DataSchemaCalculationServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def execute(
        self,
        request: datasets_v1_data_schema_calculation_service_pb2.CalculateDataSchemaRequest
    ) -> datasets_v1_data_schema_calculation_service_pb2.CalculateDataSchemaResponse:
        return await self.client.CalculateDataSchema(request, timeout=self.timeout)


class DatasetVersionQueryCountDatasetVersions1Adapter:
    def __init__(
        self,
        client: featurestore_v1_feature_value_calculation_service_pb2_grpc.FeatureValueCalculationServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def __call__(
        self,
        request: featurestore_v1_feature_value_calculation_service_pb2.RecalculateFeatureValuesRequest
    ) -> featurestore_v1_feature_value_calculation_service_pb2.RecalculateFeatureValuesResponse:
        return await self.client.RecalculateFeatureValues(request, timeout=self.timeout)


async def dataset_version_validation_lint_dataset_versions0(
    client: datasets_v1_dataset_version_calculation_service_pb2_grpc.DatasetVersionCalculationServiceStub,
    request: datasets_v1_dataset_version_calculation_service_pb2.EstimateDatasetVersionRequest,
    timeout: float
) -> datasets_v1_dataset_version_calculation_service_pb2.EstimateDatasetVersionResponse:
    return await client.EstimateDatasetVersion(request, timeout=timeout)


class DatasetVersionValidationNormalizeDatasetVersion0Port(Protocol):
    async def execute(
        self,
        request: datasets_v1_data_schema_calculation_service_pb2.QuoteDataSchemaRequest
    ) -> datasets_v1_data_schema_calculation_service_pb2.QuoteDataSchemaResponse: ...


class DatasetVersionValidationNormalizeDatasetVersion0Adapter:
    def __init__(
        self,
        client: datasets_v1_data_schema_calculation_service_pb2_grpc.DataSchemaCalculationServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def execute(
        self,
        request: datasets_v1_data_schema_calculation_service_pb2.QuoteDataSchemaRequest
    ) -> datasets_v1_data_schema_calculation_service_pb2.QuoteDataSchemaResponse:
        return await self.client.QuoteDataSchema(request, timeout=self.timeout)


class DatasetWorkflowResumeDatasetWorkflow1Adapter:
    def __init__(
        self,
        client: search_v1_search_index_query_service_pb2_grpc.SearchIndexQueryServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def __call__(
        self,
        request: search_v1_search_index_query_service_pb2.BrowseSearchIndexesRequest
    ) -> search_v1_search_index_query_service_pb2.BrowseSearchIndexesResponse:
        return await self.client.BrowseSearchIndexes(request, timeout=self.timeout)
