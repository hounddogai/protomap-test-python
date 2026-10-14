"""Replaceable partner hooks of the anomalies domain."""

from __future__ import annotations

from acme.anomalies.v1 import (
    anomaly_feedback_calculation_service_pb2 as anomalies_v1_anomaly_feedback_calculation_service_pb2,
)
from acme.anomalies.v1 import (
    anomaly_feedback_calculation_service_pb2_grpc as anomalies_v1_anomaly_feedback_calculation_service_pb2_grpc,
)
from acme.datasets.v1 import data_schema_calculation_service_pb2 as datasets_v1_data_schema_calculation_service_pb2
from acme.datasets.v1 import (
    data_schema_calculation_service_pb2_grpc as datasets_v1_data_schema_calculation_service_pb2_grpc,
)
from acme.lineage.v1 import impact_calculation_service_pb2 as lineage_v1_impact_calculation_service_pb2
from acme.lineage.v1 import impact_calculation_service_pb2_grpc as lineage_v1_impact_calculation_service_pb2_grpc
from acme.lineage.v1 import lineage_node_query_service_pb2 as lineage_v1_lineage_node_query_service_pb2
from acme.lineage.v1 import lineage_node_query_service_pb2_grpc as lineage_v1_lineage_node_query_service_pb2_grpc
from acme.lineage.v1 import lineage_node_service_pb2 as lineage_v1_lineage_node_service_pb2
from acme.lineage.v1 import lineage_node_service_pb2_grpc as lineage_v1_lineage_node_service_pb2_grpc
from acme.metrics.v1 import metric_series_query_service_pb2 as metrics_v1_metric_series_query_service_pb2
from acme.metrics.v1 import metric_series_query_service_pb2_grpc as metrics_v1_metric_series_query_service_pb2_grpc
from acme.search.v1 import search_index_service_pb2 as search_v1_search_index_service_pb2
from acme.search.v1 import search_index_service_pb2_grpc as search_v1_search_index_service_pb2_grpc


async def anomaly_feedback_approval_reject_anomaly_feedback1(
    client: search_v1_search_index_service_pb2_grpc.SearchIndexServiceStub,
    request: search_v1_search_index_service_pb2.BatchGetSearchIndexesRequest,
    timeout: float
) -> search_v1_search_index_service_pb2.BatchGetSearchIndexesResponse:
    raise RuntimeError("domain hook was not installed")


async def anomaly_feedback_validation_preview_anomaly_feedback1(
    client: lineage_v1_impact_calculation_service_pb2_grpc.ImpactCalculationServiceStub,
    request: lineage_v1_impact_calculation_service_pb2.RecalculateImpactsRequest,
    timeout: float
) -> lineage_v1_impact_calculation_service_pb2.RecalculateImpactsResponse:
    raise RuntimeError("domain hook was not installed")


async def anomaly_feedback_workflow_retry_anomaly_feedback_workflow1(
    client: datasets_v1_data_schema_calculation_service_pb2_grpc.DataSchemaCalculationServiceStub,
    request: datasets_v1_data_schema_calculation_service_pb2.EstimateDataSchemaRequest,
    timeout: float
) -> datasets_v1_data_schema_calculation_service_pb2.EstimateDataSchemaResponse:
    raise RuntimeError("domain hook was not installed")


async def anomaly_query_summarize_anomalies0(
    client: lineage_v1_lineage_node_query_service_pb2_grpc.LineageNodeQueryServiceStub,
    request: lineage_v1_lineage_node_query_service_pb2.SuggestLineageNodesRequest,
    timeout: float
) -> lineage_v1_lineage_node_query_service_pb2.SuggestLineageNodesResponse:
    raise RuntimeError("domain hook was not installed")


async def detector_approval_approve_detector3(
    client: anomalies_v1_anomaly_feedback_calculation_service_pb2_grpc.AnomalyFeedbackCalculationServiceStub,
    request: anomalies_v1_anomaly_feedback_calculation_service_pb2.EstimateAnomalyFeedbackRequest,
    timeout: float
) -> anomalies_v1_anomaly_feedback_calculation_service_pb2.EstimateAnomalyFeedbackResponse:
    raise RuntimeError("domain hook was not installed")


async def detector_approval_submit_detector2(
    client: metrics_v1_metric_series_query_service_pb2_grpc.MetricSeriesQueryServiceStub,
    request: metrics_v1_metric_series_query_service_pb2.SuggestMetricSeriesesRequest,
    timeout: float
) -> metrics_v1_metric_series_query_service_pb2.SuggestMetricSeriesesResponse:
    raise RuntimeError("domain hook was not installed")


async def detector_validation_validate_detector1(
    client: lineage_v1_lineage_node_service_pb2_grpc.LineageNodeServiceStub,
    request: lineage_v1_lineage_node_service_pb2.ListLineageNodesRequest,
    timeout: float
) -> lineage_v1_lineage_node_service_pb2.ListLineageNodesResponse:
    raise RuntimeError("domain hook was not installed")
