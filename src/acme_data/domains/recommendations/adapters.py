"""Transport adapters used by recommendations workflows."""

from __future__ import annotations

from typing import Protocol

from acme.customers.v1 import (
    consent_record_calculation_service_pb2 as customers_v1_consent_record_calculation_service_pb2,
)
from acme.customers.v1 import (
    consent_record_calculation_service_pb2_grpc as customers_v1_consent_record_calculation_service_pb2_grpc,
)
from acme.customers.v1 import household_calculation_service_pb2 as customers_v1_household_calculation_service_pb2
from acme.customers.v1 import (
    household_calculation_service_pb2_grpc as customers_v1_household_calculation_service_pb2_grpc,
)
from acme.customers.v1 import household_validation_service_pb2 as customers_v1_household_validation_service_pb2
from acme.customers.v1 import (
    household_validation_service_pb2_grpc as customers_v1_household_validation_service_pb2_grpc,
)
from acme.datasets.v1 import data_schema_calculation_service_pb2 as datasets_v1_data_schema_calculation_service_pb2
from acme.datasets.v1 import (
    data_schema_calculation_service_pb2_grpc as datasets_v1_data_schema_calculation_service_pb2_grpc,
)
from acme.featurestore.v1 import feature_value_query_service_pb2 as featurestore_v1_feature_value_query_service_pb2
from acme.featurestore.v1 import (
    feature_value_query_service_pb2_grpc as featurestore_v1_feature_value_query_service_pb2_grpc,
)
from acme.featurestore.v1 import (
    feature_view_calculation_service_pb2 as featurestore_v1_feature_view_calculation_service_pb2,
)
from acme.featurestore.v1 import (
    feature_view_calculation_service_pb2_grpc as featurestore_v1_feature_view_calculation_service_pb2_grpc,
)
from acme.featurestore.v1 import (
    feature_view_validation_service_pb2 as featurestore_v1_feature_view_validation_service_pb2,
)
from acme.featurestore.v1 import (
    feature_view_validation_service_pb2_grpc as featurestore_v1_feature_view_validation_service_pb2_grpc,
)
from acme.identity.v1 import user_query_service_pb2 as identity_v1_user_query_service_pb2
from acme.identity.v1 import user_query_service_pb2_grpc as identity_v1_user_query_service_pb2_grpc
from acme.identity.v1 import user_validation_service_pb2 as identity_v1_user_validation_service_pb2
from acme.identity.v1 import user_validation_service_pb2_grpc as identity_v1_user_validation_service_pb2_grpc
from acme.labeling.v1 import label_set_lifecycle_service_pb2 as labeling_v1_label_set_lifecycle_service_pb2
from acme.labeling.v1 import label_set_lifecycle_service_pb2_grpc as labeling_v1_label_set_lifecycle_service_pb2_grpc
from acme.lineage.v1 import impact_sync_service_pb2 as lineage_v1_impact_sync_service_pb2
from acme.lineage.v1 import impact_sync_service_pb2_grpc as lineage_v1_impact_sync_service_pb2_grpc
from acme.lineage.v1 import lineage_edge_validation_service_pb2 as lineage_v1_lineage_edge_validation_service_pb2
from acme.lineage.v1 import (
    lineage_edge_validation_service_pb2_grpc as lineage_v1_lineage_edge_validation_service_pb2_grpc,
)
from acme.lineage.v1 import lineage_node_reporting_service_pb2 as lineage_v1_lineage_node_reporting_service_pb2
from acme.lineage.v1 import (
    lineage_node_reporting_service_pb2_grpc as lineage_v1_lineage_node_reporting_service_pb2_grpc,
)
from acme.metrics.v1 import metric_alert_notification_service_pb2 as metrics_v1_metric_alert_notification_service_pb2
from acme.metrics.v1 import (
    metric_alert_notification_service_pb2_grpc as metrics_v1_metric_alert_notification_service_pb2_grpc,
)
from acme.metrics.v1 import metric_series_notification_service_pb2 as metrics_v1_metric_series_notification_service_pb2
from acme.metrics.v1 import (
    metric_series_notification_service_pb2_grpc as metrics_v1_metric_series_notification_service_pb2_grpc,
)
from acme.notifications.v1 import notification_query_service_pb2 as notifications_v1_notification_query_service_pb2
from acme.notifications.v1 import (
    notification_query_service_pb2_grpc as notifications_v1_notification_query_service_pb2_grpc,
)
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
    recommendation_model_approval_service_pb2 as recommendations_v1_recommendation_model_approval_service_pb2,
)
from acme.recommendations.v1 import (
    recommendation_model_approval_service_pb2_grpc as recommendations_v1_recommendation_model_approval_service_pb2_grpc,
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
from acme.recommendations.v1 import (
    recommendation_model_workflow_service_pb2 as recommendations_v1_recommendation_model_workflow_service_pb2,
)
from acme.recommendations.v1 import (
    recommendation_model_workflow_service_pb2_grpc as recommendations_v1_recommendation_model_workflow_service_pb2_grpc,
)
from acme.recommendations.v1 import (
    recommendation_set_query_service_pb2 as recommendations_v1_recommendation_set_query_service_pb2,
)
from acme.recommendations.v1 import (
    recommendation_set_query_service_pb2_grpc as recommendations_v1_recommendation_set_query_service_pb2_grpc,
)
from acme.recommendations.v1 import recommendation_set_service_pb2 as recommendations_v1_recommendation_set_service_pb2
from acme.recommendations.v1 import (
    recommendation_set_service_pb2_grpc as recommendations_v1_recommendation_set_service_pb2_grpc,
)
from acme.recommendations.v1 import (
    recommendation_set_validation_service_pb2 as recommendations_v1_recommendation_set_validation_service_pb2,
)
from acme.recommendations.v1 import (
    recommendation_set_validation_service_pb2_grpc as recommendations_v1_recommendation_set_validation_service_pb2_grpc,
)


async def interaction_approval_comment_interaction_approval3(
    client: pipelines_v1_pipeline_lifecycle_service_pb2_grpc.PipelineLifecycleServiceStub,
    request: pipelines_v1_pipeline_lifecycle_service_pb2.SchedulePipelineExpiryRequest,
    timeout: float
) -> pipelines_v1_pipeline_lifecycle_service_pb2.SchedulePipelineExpiryResponse:
    return await client.SchedulePipelineExpiry(request, timeout=timeout)


class InteractionApprovalDelegateInteractionApproval1Port(Protocol):
    async def execute(
        self,
        request: recommendations_v1_recommendation_set_validation_service_pb2.NormalizeRecommendationSetRequest
    ) -> recommendations_v1_recommendation_set_validation_service_pb2.NormalizeRecommendationSetResponse: ...


class InteractionApprovalDelegateInteractionApproval1Adapter:
    def __init__(
        self,
        client: recommendations_v1_recommendation_set_validation_service_pb2_grpc.RecommendationSetValidationServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def execute(
        self,
        request: recommendations_v1_recommendation_set_validation_service_pb2.NormalizeRecommendationSetRequest
    ) -> recommendations_v1_recommendation_set_validation_service_pb2.NormalizeRecommendationSetResponse:
        return await self.client.NormalizeRecommendationSet(request, timeout=self.timeout)


class InteractionApprovalRecallInteraction0Adapter:
    def __init__(self, client: lineage_v1_impact_sync_service_pb2_grpc.ImpactSyncServiceStub, timeout: float) -> None:
        self.client = client
        self.timeout = timeout

    async def __call__(
        self,
        request: lineage_v1_impact_sync_service_pb2.ResolveImpactConflictRequest
    ) -> lineage_v1_impact_sync_service_pb2.ResolveImpactConflictResponse:
        return await self.client.ResolveImpactConflict(request, timeout=self.timeout)


async def interaction_calculation_quote_interaction1(
    client: recommendations_v1_recommendation_model_calculation_service_pb2_grpc.RecommendationModelCalculationServiceStub,
    request: recommendations_v1_recommendation_model_calculation_service_pb2.RecalculateRecommendationModelsRequest,
    timeout: float
) -> recommendations_v1_recommendation_model_calculation_service_pb2.RecalculateRecommendationModelsResponse:
    return await client.RecalculateRecommendationModels(request, timeout=timeout)


async def interaction_lifecycle_expire_interaction2(
    client: recommendations_v1_recommendation_model_query_service_pb2_grpc.RecommendationModelQueryServiceStub,
    request: recommendations_v1_recommendation_model_query_service_pb2.CountRecommendationModelsRequest,
    timeout: float
) -> recommendations_v1_recommendation_model_query_service_pb2.CountRecommendationModelsResponse:
    return await client.CountRecommendationModels(request, timeout=timeout)


class InteractionLifecycleGetInteractionLifecycle1Port(Protocol):
    async def execute(
        self,
        request: customers_v1_consent_record_calculation_service_pb2.EstimateConsentRecordRequest
    ) -> customers_v1_consent_record_calculation_service_pb2.EstimateConsentRecordResponse: ...


class InteractionLifecycleGetInteractionLifecycle1Adapter:
    def __init__(
        self,
        client: customers_v1_consent_record_calculation_service_pb2_grpc.ConsentRecordCalculationServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def execute(
        self,
        request: customers_v1_consent_record_calculation_service_pb2.EstimateConsentRecordRequest
    ) -> customers_v1_consent_record_calculation_service_pb2.EstimateConsentRecordResponse:
        return await self.client.EstimateConsentRecord(request, timeout=self.timeout)


class InteractionLifecycleReinstateInteraction1Adapter:
    def __init__(
        self,
        client: recommendations_v1_recommendation_set_service_pb2_grpc.RecommendationSetServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def __call__(
        self,
        request: recommendations_v1_recommendation_set_service_pb2.CloneRecommendationSetRequest
    ) -> recommendations_v1_recommendation_set_service_pb2.CloneRecommendationSetResponse:
        return await self.client.CloneRecommendationSet(request, timeout=self.timeout)


async def interaction_validation_lint_interactions0(
    client: performers_v1_performer_service_pb2_grpc.PerformerServiceStub,
    request: performers_v1_performer_service_pb2.BatchGetPerformersRequest,
    timeout: float
) -> performers_v1_performer_service_pb2.BatchGetPerformersResponse:
    return await client.BatchGetPerformers(request, timeout=timeout)


class InteractionValidationNormalizeInteraction1Port(Protocol):
    async def execute(
        self,
        request: identity_v1_user_query_service_pb2.BrowseUsersRequest
    ) -> identity_v1_user_query_service_pb2.BrowseUsersResponse: ...


class InteractionValidationNormalizeInteraction1Adapter:
    def __init__(self, client: identity_v1_user_query_service_pb2_grpc.UserQueryServiceStub, timeout: float) -> None:
        self.client = client
        self.timeout = timeout

    async def execute(
        self,
        request: identity_v1_user_query_service_pb2.BrowseUsersRequest
    ) -> identity_v1_user_query_service_pb2.BrowseUsersResponse:
        return await self.client.BrowseUsers(request, timeout=self.timeout)


class InteractionWorkflowResumeInteractionWorkflow2Port(Protocol):
    async def execute(
        self,
        request: recommendations_v1_recommendation_model_workflow_service_pb2.AdvanceRecommendationModelWorkflowRequest
    ) -> recommendations_v1_recommendation_model_workflow_service_pb2.AdvanceRecommendationModelWorkflowResponse: ...


class InteractionWorkflowResumeInteractionWorkflow2Adapter:
    def __init__(
        self,
        client: recommendations_v1_recommendation_model_workflow_service_pb2_grpc.RecommendationModelWorkflowServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def execute(
        self,
        request: recommendations_v1_recommendation_model_workflow_service_pb2.AdvanceRecommendationModelWorkflowRequest
    ) -> recommendations_v1_recommendation_model_workflow_service_pb2.AdvanceRecommendationModelWorkflowResponse:
        return await self.client.AdvanceRecommendationModelWorkflow(request, timeout=self.timeout)


class InteractionWorkflowSignalInteractionWorkflow1Adapter:
    def __init__(
        self,
        client: labeling_v1_label_set_lifecycle_service_pb2_grpc.LabelSetLifecycleServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def __call__(
        self,
        request: labeling_v1_label_set_lifecycle_service_pb2.ScheduleLabelSetExpiryRequest
    ) -> labeling_v1_label_set_lifecycle_service_pb2.ScheduleLabelSetExpiryResponse:
        return await self.client.ScheduleLabelSetExpiry(request, timeout=self.timeout)


async def recommendation_model_approval_delegate_recommendation_model_approval2(
    client: recommendations_v1_interaction_validation_service_pb2_grpc.InteractionValidationServiceStub,
    request: recommendations_v1_interaction_validation_service_pb2.ExplainInteractionDecisionRequest,
    timeout: float
) -> recommendations_v1_interaction_validation_service_pb2.ExplainInteractionDecisionResponse:
    return await client.ExplainInteractionDecision(request, timeout=timeout)


class RecommendationModelApprovalEscalateRecommendationModel0Port(Protocol):
    async def execute(
        self,
        request: customers_v1_household_validation_service_pb2.ScoreHouseholdRequest
    ) -> customers_v1_household_validation_service_pb2.ScoreHouseholdResponse: ...


class RecommendationModelApprovalEscalateRecommendationModel0Adapter:
    def __init__(
        self,
        client: customers_v1_household_validation_service_pb2_grpc.HouseholdValidationServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def execute(
        self,
        request: customers_v1_household_validation_service_pb2.ScoreHouseholdRequest
    ) -> customers_v1_household_validation_service_pb2.ScoreHouseholdResponse:
        return await self.client.ScoreHousehold(request, timeout=self.timeout)


class RecommendationModelApprovalGetRecommendationModelApprovalStatus1Adapter:
    def __init__(
        self,
        client: metrics_v1_metric_alert_notification_service_pb2_grpc.MetricAlertNotificationServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def __call__(
        self,
        request: metrics_v1_metric_alert_notification_service_pb2.SubscribeMetricAlertUpdatesRequest
    ) -> metrics_v1_metric_alert_notification_service_pb2.SubscribeMetricAlertUpdatesResponse:
        return await self.client.SubscribeMetricAlertUpdates(request, timeout=self.timeout)


async def recommendation_model_calculation_compare_recommendation_model_options2(
    client: identity_v1_user_validation_service_pb2_grpc.UserValidationServiceStub,
    request: identity_v1_user_validation_service_pb2.CheckUserEligibilityRequest,
    timeout: float
) -> identity_v1_user_validation_service_pb2.CheckUserEligibilityResponse:
    return await client.CheckUserEligibility(request, timeout=timeout)


class RecommendationModelCalculationEstimateRecommendationModel1Port(Protocol):
    async def execute(
        self,
        request: featurestore_v1_feature_value_query_service_pb2.SummarizeFeatureValuesRequest
    ) -> featurestore_v1_feature_value_query_service_pb2.SummarizeFeatureValuesResponse: ...


class RecommendationModelCalculationEstimateRecommendationModel1Adapter:
    def __init__(
        self,
        client: featurestore_v1_feature_value_query_service_pb2_grpc.FeatureValueQueryServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def execute(
        self,
        request: featurestore_v1_feature_value_query_service_pb2.SummarizeFeatureValuesRequest
    ) -> featurestore_v1_feature_value_query_service_pb2.SummarizeFeatureValuesResponse:
        return await self.client.SummarizeFeatureValues(request, timeout=self.timeout)


class RecommendationModelValidationCheckRecommendationModelEligibility0Port(Protocol):
    async def execute(
        self,
        request: metrics_v1_metric_series_notification_service_pb2.SubscribeMetricSeriesUpdatesRequest
    ) -> metrics_v1_metric_series_notification_service_pb2.SubscribeMetricSeriesUpdatesResponse: ...


class RecommendationModelValidationCheckRecommendationModelEligibility0Adapter:
    def __init__(
        self,
        client: metrics_v1_metric_series_notification_service_pb2_grpc.MetricSeriesNotificationServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def execute(
        self,
        request: metrics_v1_metric_series_notification_service_pb2.SubscribeMetricSeriesUpdatesRequest
    ) -> metrics_v1_metric_series_notification_service_pb2.SubscribeMetricSeriesUpdatesResponse:
        return await self.client.SubscribeMetricSeriesUpdates(request, timeout=self.timeout)


class RecommendationModelWorkflowCancelRecommendationModelWorkflow0Adapter:
    def __init__(
        self,
        client: notifications_v1_notification_query_service_pb2_grpc.NotificationQueryServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def __call__(
        self,
        request: notifications_v1_notification_query_service_pb2.CountNotificationsRequest
    ) -> notifications_v1_notification_query_service_pb2.CountNotificationsResponse:
        return await self.client.CountNotifications(request, timeout=self.timeout)


async def recommendation_model_workflow_retry_recommendation_model_workflow2(
    client: recommendations_v1_recommendation_set_service_pb2_grpc.RecommendationSetServiceStub,
    request: recommendations_v1_recommendation_set_service_pb2.UpdateRecommendationSetRequest,
    timeout: float
) -> recommendations_v1_recommendation_set_service_pb2.UpdateRecommendationSetResponse:
    return await client.UpdateRecommendationSet(request, timeout=timeout)


class RecommendationModelWorkflowSignalRecommendationModelWorkflow1Port(Protocol):
    async def execute(
        self,
        request: recommendations_v1_recommendation_set_query_service_pb2.FindRecommendationSetsRequest
    ) -> recommendations_v1_recommendation_set_query_service_pb2.FindRecommendationSetsResponse: ...


class RecommendationModelWorkflowSignalRecommendationModelWorkflow1Adapter:
    def __init__(
        self,
        client: recommendations_v1_recommendation_set_query_service_pb2_grpc.RecommendationSetQueryServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def execute(
        self,
        request: recommendations_v1_recommendation_set_query_service_pb2.FindRecommendationSetsRequest
    ) -> recommendations_v1_recommendation_set_query_service_pb2.FindRecommendationSetsResponse:
        return await self.client.FindRecommendationSets(request, timeout=self.timeout)


class RecommendationSetApprovalRecallRecommendationSet2Port(Protocol):
    async def execute(
        self,
        request: identity_v1_user_validation_service_pb2.CheckUserEligibilityRequest
    ) -> identity_v1_user_validation_service_pb2.CheckUserEligibilityResponse: ...


class RecommendationSetApprovalRecallRecommendationSet2Adapter:
    def __init__(
        self,
        client: identity_v1_user_validation_service_pb2_grpc.UserValidationServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def execute(
        self,
        request: identity_v1_user_validation_service_pb2.CheckUserEligibilityRequest
    ) -> identity_v1_user_validation_service_pb2.CheckUserEligibilityResponse:
        return await self.client.CheckUserEligibility(request, timeout=self.timeout)


class RecommendationSetApprovalSubmitRecommendationSet1Adapter:
    def __init__(
        self,
        client: lineage_v1_lineage_node_reporting_service_pb2_grpc.LineageNodeReportingServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def __call__(
        self,
        request: lineage_v1_lineage_node_reporting_service_pb2.ScheduleLineageNodeReportRequest
    ) -> lineage_v1_lineage_node_reporting_service_pb2.ScheduleLineageNodeReportResponse:
        return await self.client.ScheduleLineageNodeReport(request, timeout=self.timeout)


class RecommendationSetDeleteRecommendationSet1Port(Protocol):
    async def execute(
        self,
        request: recommendations_v1_recommendation_model_query_service_pb2.FindRecommendationModelsRequest
    ) -> recommendations_v1_recommendation_model_query_service_pb2.FindRecommendationModelsResponse: ...


class RecommendationSetDeleteRecommendationSet1Adapter:
    def __init__(
        self,
        client: recommendations_v1_recommendation_model_query_service_pb2_grpc.RecommendationModelQueryServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def execute(
        self,
        request: recommendations_v1_recommendation_model_query_service_pb2.FindRecommendationModelsRequest
    ) -> recommendations_v1_recommendation_model_query_service_pb2.FindRecommendationModelsResponse:
        return await self.client.FindRecommendationModels(request, timeout=self.timeout)


class RecommendationSetDeleteRecommendationSet3Adapter:
    def __init__(
        self,
        client: featurestore_v1_feature_view_calculation_service_pb2_grpc.FeatureViewCalculationServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def __call__(
        self,
        request: featurestore_v1_feature_view_calculation_service_pb2.CalculateFeatureViewRequest
    ) -> featurestore_v1_feature_view_calculation_service_pb2.CalculateFeatureViewResponse:
        return await self.client.CalculateFeatureView(request, timeout=self.timeout)


async def recommendation_set_validation_lint_recommendation_sets1(
    client: datasets_v1_data_schema_calculation_service_pb2_grpc.DataSchemaCalculationServiceStub,
    request: datasets_v1_data_schema_calculation_service_pb2.CalculateDataSchemaRequest,
    timeout: float
) -> datasets_v1_data_schema_calculation_service_pb2.CalculateDataSchemaResponse:
    return await client.CalculateDataSchema(request, timeout=timeout)


class RecommendationSetValidationNormalizeRecommendationSet1Port(Protocol):
    async def execute(
        self,
        request: lineage_v1_lineage_edge_validation_service_pb2.ExplainLineageEdgeDecisionRequest
    ) -> lineage_v1_lineage_edge_validation_service_pb2.ExplainLineageEdgeDecisionResponse: ...


class RecommendationSetValidationNormalizeRecommendationSet1Adapter:
    def __init__(
        self,
        client: lineage_v1_lineage_edge_validation_service_pb2_grpc.LineageEdgeValidationServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def execute(
        self,
        request: lineage_v1_lineage_edge_validation_service_pb2.ExplainLineageEdgeDecisionRequest
    ) -> lineage_v1_lineage_edge_validation_service_pb2.ExplainLineageEdgeDecisionResponse:
        return await self.client.ExplainLineageEdgeDecision(request, timeout=self.timeout)


class RecommendationSetValidationPreviewRecommendationSet0Adapter:
    def __init__(
        self,
        client: featurestore_v1_feature_view_validation_service_pb2_grpc.FeatureViewValidationServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def __call__(
        self,
        request: featurestore_v1_feature_view_validation_service_pb2.ExplainFeatureViewDecisionRequest
    ) -> featurestore_v1_feature_view_validation_service_pb2.ExplainFeatureViewDecisionResponse:
        return await self.client.ExplainFeatureViewDecision(request, timeout=self.timeout)


async def recommendation_set_workflow_retry_recommendation_set_workflow0(
    client: recommendations_v1_recommendation_model_validation_service_pb2_grpc.RecommendationModelValidationServiceStub,
    request: recommendations_v1_recommendation_model_validation_service_pb2.CheckRecommendationModelEligibilityRequest,
    timeout: float
) -> recommendations_v1_recommendation_model_validation_service_pb2.CheckRecommendationModelEligibilityResponse:
    return await client.CheckRecommendationModelEligibility(request, timeout=timeout)


class RecommendationSetWorkflowRetryRecommendationSetWorkflow2Port(Protocol):
    async def execute(
        self,
        request: recommendations_v1_recommendation_model_approval_service_pb2.DelegateRecommendationModelApprovalRequest
    ) -> recommendations_v1_recommendation_model_approval_service_pb2.DelegateRecommendationModelApprovalResponse: ...


class RecommendationSetWorkflowRetryRecommendationSetWorkflow2Adapter:
    def __init__(
        self,
        client: recommendations_v1_recommendation_model_approval_service_pb2_grpc.RecommendationModelApprovalServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def execute(
        self,
        request: recommendations_v1_recommendation_model_approval_service_pb2.DelegateRecommendationModelApprovalRequest
    ) -> recommendations_v1_recommendation_model_approval_service_pb2.DelegateRecommendationModelApprovalResponse:
        return await self.client.DelegateRecommendationModelApproval(request, timeout=self.timeout)


class RecommendationSetWorkflowSignalRecommendationSetWorkflow1Adapter:
    def __init__(
        self,
        client: customers_v1_household_calculation_service_pb2_grpc.HouseholdCalculationServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def __call__(
        self,
        request: customers_v1_household_calculation_service_pb2.RecalculateHouseholdsRequest
    ) -> customers_v1_household_calculation_service_pb2.RecalculateHouseholdsResponse:
        return await self.client.RecalculateHouseholds(request, timeout=self.timeout)
