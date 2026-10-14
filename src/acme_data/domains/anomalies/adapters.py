"""Transport adapters used by anomalies workflows."""

from __future__ import annotations

from typing import Protocol

from acme.analytics.v1 import funnel_query_service_pb2 as analytics_v1_funnel_query_service_pb2
from acme.analytics.v1 import funnel_query_service_pb2_grpc as analytics_v1_funnel_query_service_pb2_grpc
from acme.anomalies.v1 import (
    anomaly_feedback_calculation_service_pb2 as anomalies_v1_anomaly_feedback_calculation_service_pb2,
)
from acme.anomalies.v1 import (
    anomaly_feedback_calculation_service_pb2_grpc as anomalies_v1_anomaly_feedback_calculation_service_pb2_grpc,
)
from acme.anomalies.v1 import detector_approval_service_pb2 as anomalies_v1_detector_approval_service_pb2
from acme.anomalies.v1 import detector_approval_service_pb2_grpc as anomalies_v1_detector_approval_service_pb2_grpc
from acme.anomalies.v1 import detector_query_service_pb2 as anomalies_v1_detector_query_service_pb2
from acme.anomalies.v1 import detector_query_service_pb2_grpc as anomalies_v1_detector_query_service_pb2_grpc
from acme.anomalies.v1 import detector_validation_service_pb2 as anomalies_v1_detector_validation_service_pb2
from acme.anomalies.v1 import detector_validation_service_pb2_grpc as anomalies_v1_detector_validation_service_pb2_grpc
from acme.boxoffice.v1 import box_office_sale_query_service_pb2 as boxoffice_v1_box_office_sale_query_service_pb2
from acme.boxoffice.v1 import (
    box_office_sale_query_service_pb2_grpc as boxoffice_v1_box_office_sale_query_service_pb2_grpc,
)
from acme.datasets.v1 import data_schema_calculation_service_pb2 as datasets_v1_data_schema_calculation_service_pb2
from acme.datasets.v1 import (
    data_schema_calculation_service_pb2_grpc as datasets_v1_data_schema_calculation_service_pb2_grpc,
)
from acme.datasets.v1 import dataset_query_service_pb2 as datasets_v1_dataset_query_service_pb2
from acme.datasets.v1 import dataset_query_service_pb2_grpc as datasets_v1_dataset_query_service_pb2_grpc
from acme.datasets.v1 import dataset_service_pb2 as datasets_v1_dataset_service_pb2
from acme.datasets.v1 import dataset_service_pb2_grpc as datasets_v1_dataset_service_pb2_grpc
from acme.lineage.v1 import impact_calculation_service_pb2 as lineage_v1_impact_calculation_service_pb2
from acme.lineage.v1 import impact_calculation_service_pb2_grpc as lineage_v1_impact_calculation_service_pb2_grpc
from acme.lineage.v1 import impact_workflow_service_pb2 as lineage_v1_impact_workflow_service_pb2
from acme.lineage.v1 import impact_workflow_service_pb2_grpc as lineage_v1_impact_workflow_service_pb2_grpc
from acme.lineage.v1 import lineage_edge_validation_service_pb2 as lineage_v1_lineage_edge_validation_service_pb2
from acme.lineage.v1 import (
    lineage_edge_validation_service_pb2_grpc as lineage_v1_lineage_edge_validation_service_pb2_grpc,
)
from acme.lineage.v1 import lineage_node_approval_service_pb2 as lineage_v1_lineage_node_approval_service_pb2
from acme.lineage.v1 import lineage_node_approval_service_pb2_grpc as lineage_v1_lineage_node_approval_service_pb2_grpc
from acme.lineage.v1 import lineage_node_query_service_pb2 as lineage_v1_lineage_node_query_service_pb2
from acme.lineage.v1 import lineage_node_query_service_pb2_grpc as lineage_v1_lineage_node_query_service_pb2_grpc
from acme.lineage.v1 import lineage_node_service_pb2 as lineage_v1_lineage_node_service_pb2
from acme.lineage.v1 import lineage_node_service_pb2_grpc as lineage_v1_lineage_node_service_pb2_grpc
from acme.metrics.v1 import metric_series_query_service_pb2 as metrics_v1_metric_series_query_service_pb2
from acme.metrics.v1 import metric_series_query_service_pb2_grpc as metrics_v1_metric_series_query_service_pb2_grpc
from acme.search.v1 import search_index_service_pb2 as search_v1_search_index_service_pb2
from acme.search.v1 import search_index_service_pb2_grpc as search_v1_search_index_service_pb2_grpc
from acme.search.v1 import search_index_validation_service_pb2 as search_v1_search_index_validation_service_pb2
from acme.search.v1 import (
    search_index_validation_service_pb2_grpc as search_v1_search_index_validation_service_pb2_grpc,
)


class AnomalyApprovalCommentAnomalyApproval0Adapter:
    def __init__(
        self,
        client: datasets_v1_dataset_query_service_pb2_grpc.DatasetQueryServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def __call__(
        self,
        request: datasets_v1_dataset_query_service_pb2.ResolveDatasetsRequest
    ) -> datasets_v1_dataset_query_service_pb2.ResolveDatasetsResponse:
        return await self.client.ResolveDatasets(request, timeout=self.timeout)


class AnomalyFeedbackApprovalApproveAnomalyFeedback2Adapter:
    def __init__(
        self,
        client: search_v1_search_index_validation_service_pb2_grpc.SearchIndexValidationServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def __call__(
        self,
        request: search_v1_search_index_validation_service_pb2.NormalizeSearchIndexRequest
    ) -> search_v1_search_index_validation_service_pb2.NormalizeSearchIndexResponse:
        return await self.client.NormalizeSearchIndex(request, timeout=self.timeout)


async def anomaly_feedback_approval_reject_anomaly_feedback1(
    client: search_v1_search_index_service_pb2_grpc.SearchIndexServiceStub,
    request: search_v1_search_index_service_pb2.BatchGetSearchIndexesRequest,
    timeout: float
) -> search_v1_search_index_service_pb2.BatchGetSearchIndexesResponse:
    return await client.BatchGetSearchIndexes(request, timeout=timeout)


class AnomalyFeedbackApprovalSubmitAnomalyFeedback1Port(Protocol):
    async def execute(
        self,
        request: anomalies_v1_detector_approval_service_pb2.ApproveDetectorRequest
    ) -> anomalies_v1_detector_approval_service_pb2.ApproveDetectorResponse: ...


class AnomalyFeedbackApprovalSubmitAnomalyFeedback1Adapter:
    def __init__(
        self,
        client: anomalies_v1_detector_approval_service_pb2_grpc.DetectorApprovalServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def execute(
        self,
        request: anomalies_v1_detector_approval_service_pb2.ApproveDetectorRequest
    ) -> anomalies_v1_detector_approval_service_pb2.ApproveDetectorResponse:
        return await self.client.ApproveDetector(request, timeout=self.timeout)


class AnomalyFeedbackApprovalSubmitAnomalyFeedback3Adapter:
    def __init__(
        self,
        client: lineage_v1_impact_workflow_service_pb2_grpc.ImpactWorkflowServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def __call__(
        self,
        request: lineage_v1_impact_workflow_service_pb2.RetryImpactWorkflowRequest
    ) -> lineage_v1_impact_workflow_service_pb2.RetryImpactWorkflowResponse:
        return await self.client.RetryImpactWorkflow(request, timeout=self.timeout)


class AnomalyFeedbackCalculationSimulateAnomalyFeedback1Port(Protocol):
    async def execute(
        self,
        request: lineage_v1_lineage_edge_validation_service_pb2.CheckLineageEdgeEligibilityRequest
    ) -> lineage_v1_lineage_edge_validation_service_pb2.CheckLineageEdgeEligibilityResponse: ...


class AnomalyFeedbackCalculationSimulateAnomalyFeedback1Adapter:
    def __init__(
        self,
        client: lineage_v1_lineage_edge_validation_service_pb2_grpc.LineageEdgeValidationServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def execute(
        self,
        request: lineage_v1_lineage_edge_validation_service_pb2.CheckLineageEdgeEligibilityRequest
    ) -> lineage_v1_lineage_edge_validation_service_pb2.CheckLineageEdgeEligibilityResponse:
        return await self.client.CheckLineageEdgeEligibility(request, timeout=self.timeout)


class AnomalyFeedbackValidationCheckAnomalyFeedbackEligibility0Adapter:
    def __init__(
        self,
        client: boxoffice_v1_box_office_sale_query_service_pb2_grpc.BoxOfficeSaleQueryServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def __call__(
        self,
        request: boxoffice_v1_box_office_sale_query_service_pb2.ResolveBoxOfficeSalesRequest
    ) -> boxoffice_v1_box_office_sale_query_service_pb2.ResolveBoxOfficeSalesResponse:
        return await self.client.ResolveBoxOfficeSales(request, timeout=self.timeout)


async def anomaly_feedback_validation_preview_anomaly_feedback1(
    client: lineage_v1_impact_calculation_service_pb2_grpc.ImpactCalculationServiceStub,
    request: lineage_v1_impact_calculation_service_pb2.RecalculateImpactsRequest,
    timeout: float
) -> lineage_v1_impact_calculation_service_pb2.RecalculateImpactsResponse:
    return await client.RecalculateImpacts(request, timeout=timeout)


class AnomalyFeedbackValidationScoreAnomalyFeedback0Port(Protocol):
    async def execute(
        self,
        request: anomalies_v1_detector_validation_service_pb2.NormalizeDetectorRequest
    ) -> anomalies_v1_detector_validation_service_pb2.NormalizeDetectorResponse: ...


class AnomalyFeedbackValidationScoreAnomalyFeedback0Adapter:
    def __init__(
        self,
        client: anomalies_v1_detector_validation_service_pb2_grpc.DetectorValidationServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def execute(
        self,
        request: anomalies_v1_detector_validation_service_pb2.NormalizeDetectorRequest
    ) -> anomalies_v1_detector_validation_service_pb2.NormalizeDetectorResponse:
        return await self.client.NormalizeDetector(request, timeout=self.timeout)


async def anomaly_feedback_workflow_retry_anomaly_feedback_workflow1(
    client: datasets_v1_data_schema_calculation_service_pb2_grpc.DataSchemaCalculationServiceStub,
    request: datasets_v1_data_schema_calculation_service_pb2.EstimateDataSchemaRequest,
    timeout: float
) -> datasets_v1_data_schema_calculation_service_pb2.EstimateDataSchemaResponse:
    return await client.EstimateDataSchema(request, timeout=timeout)


class AnomalyFeedbackWorkflowRetryAnomalyFeedbackWorkflow3Port(Protocol):
    async def execute(
        self,
        request: anomalies_v1_detector_validation_service_pb2.ValidateDetectorRequest
    ) -> anomalies_v1_detector_validation_service_pb2.ValidateDetectorResponse: ...


class AnomalyFeedbackWorkflowRetryAnomalyFeedbackWorkflow3Adapter:
    def __init__(
        self,
        client: anomalies_v1_detector_validation_service_pb2_grpc.DetectorValidationServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def execute(
        self,
        request: anomalies_v1_detector_validation_service_pb2.ValidateDetectorRequest
    ) -> anomalies_v1_detector_validation_service_pb2.ValidateDetectorResponse:
        return await self.client.ValidateDetector(request, timeout=self.timeout)


class AnomalyFeedbackWorkflowSignalAnomalyFeedbackWorkflow1Adapter:
    def __init__(
        self,
        client: anomalies_v1_detector_query_service_pb2_grpc.DetectorQueryServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def __call__(
        self,
        request: anomalies_v1_detector_query_service_pb2.BrowseDetectorsRequest
    ) -> anomalies_v1_detector_query_service_pb2.BrowseDetectorsResponse:
        return await self.client.BrowseDetectors(request, timeout=self.timeout)


async def anomaly_query_summarize_anomalies0(
    client: lineage_v1_lineage_node_query_service_pb2_grpc.LineageNodeQueryServiceStub,
    request: lineage_v1_lineage_node_query_service_pb2.SuggestLineageNodesRequest,
    timeout: float
) -> lineage_v1_lineage_node_query_service_pb2.SuggestLineageNodesResponse:
    return await client.SuggestLineageNodes(request, timeout=timeout)


class AnomalyValidationExplainAnomalyDecision2Port(Protocol):
    async def execute(
        self,
        request: lineage_v1_lineage_edge_validation_service_pb2.ExplainLineageEdgeDecisionRequest
    ) -> lineage_v1_lineage_edge_validation_service_pb2.ExplainLineageEdgeDecisionResponse: ...


class AnomalyValidationExplainAnomalyDecision2Adapter:
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


class AnomalyWorkflowPauseAnomalyWorkflow1Adapter:
    def __init__(self, client: datasets_v1_dataset_service_pb2_grpc.DatasetServiceStub, timeout: float) -> None:
        self.client = client
        self.timeout = timeout

    async def __call__(
        self,
        request: datasets_v1_dataset_service_pb2.UpdateDatasetRequest
    ) -> datasets_v1_dataset_service_pb2.UpdateDatasetResponse:
        return await self.client.UpdateDataset(request, timeout=self.timeout)


async def detector_approval_approve_detector3(
    client: anomalies_v1_anomaly_feedback_calculation_service_pb2_grpc.AnomalyFeedbackCalculationServiceStub,
    request: anomalies_v1_anomaly_feedback_calculation_service_pb2.EstimateAnomalyFeedbackRequest,
    timeout: float
) -> anomalies_v1_anomaly_feedback_calculation_service_pb2.EstimateAnomalyFeedbackResponse:
    return await client.EstimateAnomalyFeedback(request, timeout=timeout)


class DetectorApprovalCommentDetectorApproval1Port(Protocol):
    async def execute(
        self,
        request: analytics_v1_funnel_query_service_pb2.SuggestFunnelsRequest
    ) -> analytics_v1_funnel_query_service_pb2.SuggestFunnelsResponse: ...


class DetectorApprovalCommentDetectorApproval1Adapter:
    def __init__(
        self,
        client: analytics_v1_funnel_query_service_pb2_grpc.FunnelQueryServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def execute(
        self,
        request: analytics_v1_funnel_query_service_pb2.SuggestFunnelsRequest
    ) -> analytics_v1_funnel_query_service_pb2.SuggestFunnelsResponse:
        return await self.client.SuggestFunnels(request, timeout=self.timeout)


async def detector_approval_submit_detector2(
    client: metrics_v1_metric_series_query_service_pb2_grpc.MetricSeriesQueryServiceStub,
    request: metrics_v1_metric_series_query_service_pb2.SuggestMetricSeriesesRequest,
    timeout: float
) -> metrics_v1_metric_series_query_service_pb2.SuggestMetricSeriesesResponse:
    return await client.SuggestMetricSerieses(request, timeout=timeout)


async def detector_validation_validate_detector1(
    client: lineage_v1_lineage_node_service_pb2_grpc.LineageNodeServiceStub,
    request: lineage_v1_lineage_node_service_pb2.ListLineageNodesRequest,
    timeout: float
) -> lineage_v1_lineage_node_service_pb2.ListLineageNodesResponse:
    return await client.ListLineageNodes(request, timeout=timeout)


class DetectorValidationValidateDetector3Port(Protocol):
    async def execute(
        self,
        request: anomalies_v1_anomaly_feedback_calculation_service_pb2.CompareAnomalyFeedbackOptionsRequest
    ) -> anomalies_v1_anomaly_feedback_calculation_service_pb2.CompareAnomalyFeedbackOptionsResponse: ...


class DetectorValidationValidateDetector3Adapter:
    def __init__(
        self,
        client: anomalies_v1_anomaly_feedback_calculation_service_pb2_grpc.AnomalyFeedbackCalculationServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def execute(
        self,
        request: anomalies_v1_anomaly_feedback_calculation_service_pb2.CompareAnomalyFeedbackOptionsRequest
    ) -> anomalies_v1_anomaly_feedback_calculation_service_pb2.CompareAnomalyFeedbackOptionsResponse:
        return await self.client.CompareAnomalyFeedbackOptions(request, timeout=self.timeout)


class DetectorWorkflowAdvanceDetectorWorkflow1Adapter:
    def __init__(
        self,
        client: lineage_v1_lineage_node_approval_service_pb2_grpc.LineageNodeApprovalServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def __call__(
        self,
        request: lineage_v1_lineage_node_approval_service_pb2.SubmitLineageNodeRequest
    ) -> lineage_v1_lineage_node_approval_service_pb2.SubmitLineageNodeResponse:
        return await self.client.SubmitLineageNode(request, timeout=self.timeout)
