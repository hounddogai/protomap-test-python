"""Replaceable partner hooks of the lineage domain."""

from __future__ import annotations

from acme.audit.v1 import audit_event_query_service_pb2 as audit_v1_audit_event_query_service_pb2
from acme.audit.v1 import audit_event_query_service_pb2_grpc as audit_v1_audit_event_query_service_pb2_grpc
from acme.customers.v1 import customer_calculation_service_pb2 as customers_v1_customer_calculation_service_pb2
from acme.customers.v1 import (
    customer_calculation_service_pb2_grpc as customers_v1_customer_calculation_service_pb2_grpc,
)
from acme.customers.v1 import household_calculation_service_pb2 as customers_v1_household_calculation_service_pb2
from acme.customers.v1 import (
    household_calculation_service_pb2_grpc as customers_v1_household_calculation_service_pb2_grpc,
)
from acme.customers.v1 import preference_validation_service_pb2 as customers_v1_preference_validation_service_pb2
from acme.customers.v1 import (
    preference_validation_service_pb2_grpc as customers_v1_preference_validation_service_pb2_grpc,
)
from acme.dispatch.v1 import dispatch_order_query_service_pb2 as dispatch_v1_dispatch_order_query_service_pb2
from acme.dispatch.v1 import dispatch_order_query_service_pb2_grpc as dispatch_v1_dispatch_order_query_service_pb2_grpc
from acme.lending.v1 import loan_application_service_pb2 as lending_v1_loan_application_service_pb2
from acme.lending.v1 import loan_application_service_pb2_grpc as lending_v1_loan_application_service_pb2_grpc
from acme.lineage.v1 import impact_calculation_service_pb2 as lineage_v1_impact_calculation_service_pb2
from acme.lineage.v1 import impact_calculation_service_pb2_grpc as lineage_v1_impact_calculation_service_pb2_grpc
from acme.lineage.v1 import lineage_edge_import_service_pb2 as lineage_v1_lineage_edge_import_service_pb2
from acme.lineage.v1 import lineage_edge_import_service_pb2_grpc as lineage_v1_lineage_edge_import_service_pb2_grpc
from acme.lineage.v1 import lineage_edge_validation_service_pb2 as lineage_v1_lineage_edge_validation_service_pb2
from acme.lineage.v1 import (
    lineage_edge_validation_service_pb2_grpc as lineage_v1_lineage_edge_validation_service_pb2_grpc,
)
from acme.lineage.v1 import lineage_node_calculation_service_pb2 as lineage_v1_lineage_node_calculation_service_pb2
from acme.lineage.v1 import (
    lineage_node_calculation_service_pb2_grpc as lineage_v1_lineage_node_calculation_service_pb2_grpc,
)
from acme.lineage.v1 import lineage_node_lifecycle_service_pb2 as lineage_v1_lineage_node_lifecycle_service_pb2
from acme.lineage.v1 import (
    lineage_node_lifecycle_service_pb2_grpc as lineage_v1_lineage_node_lifecycle_service_pb2_grpc,
)
from acme.lineage.v1 import lineage_node_sync_service_pb2 as lineage_v1_lineage_node_sync_service_pb2
from acme.lineage.v1 import lineage_node_sync_service_pb2_grpc as lineage_v1_lineage_node_sync_service_pb2_grpc
from acme.metrics.v1 import dashboard_validation_service_pb2 as metrics_v1_dashboard_validation_service_pb2
from acme.metrics.v1 import dashboard_validation_service_pb2_grpc as metrics_v1_dashboard_validation_service_pb2_grpc
from acme.metrics.v1 import metric_series_history_service_pb2 as metrics_v1_metric_series_history_service_pb2
from acme.metrics.v1 import metric_series_history_service_pb2_grpc as metrics_v1_metric_series_history_service_pb2_grpc


async def impact_calculation_recalculate_impacts3(
    client: lineage_v1_lineage_node_calculation_service_pb2_grpc.LineageNodeCalculationServiceStub,
    request: lineage_v1_lineage_node_calculation_service_pb2.QuoteLineageNodeRequest,
    timeout: float
) -> lineage_v1_lineage_node_calculation_service_pb2.QuoteLineageNodeResponse:
    raise RuntimeError("domain hook was not installed")


async def impact_lifecycle_reinstate_impact1(
    client: customers_v1_customer_calculation_service_pb2_grpc.CustomerCalculationServiceStub,
    request: customers_v1_customer_calculation_service_pb2.RecalculateCustomersRequest,
    timeout: float
) -> customers_v1_customer_calculation_service_pb2.RecalculateCustomersResponse:
    raise RuntimeError("domain hook was not installed")


async def impact_reporting_share_impact_report0(
    client: lending_v1_loan_application_service_pb2_grpc.LoanApplicationServiceStub,
    request: lending_v1_loan_application_service_pb2.CloneLoanApplicationRequest,
    timeout: float
) -> lending_v1_loan_application_service_pb2.CloneLoanApplicationResponse:
    raise RuntimeError("domain hook was not installed")


async def impact_sync_stream_impact_changes1(
    client: metrics_v1_metric_series_history_service_pb2_grpc.MetricSeriesHistoryServiceStub,
    request: metrics_v1_metric_series_history_service_pb2.CompareMetricSeriesVersionsRequest,
    timeout: float
) -> metrics_v1_metric_series_history_service_pb2.CompareMetricSeriesVersionsResponse:
    raise RuntimeError("domain hook was not installed")


async def impact_validation_lint_impacts1(
    client: lineage_v1_lineage_node_calculation_service_pb2_grpc.LineageNodeCalculationServiceStub,
    request: lineage_v1_lineage_node_calculation_service_pb2.EstimateLineageNodeRequest,
    timeout: float
) -> lineage_v1_lineage_node_calculation_service_pb2.EstimateLineageNodeResponse:
    raise RuntimeError("domain hook was not installed")


async def impact_workflow_pause_impact_workflow1(
    client: audit_v1_audit_event_query_service_pb2_grpc.AuditEventQueryServiceStub,
    request: audit_v1_audit_event_query_service_pb2.ResolveAuditEventsRequest,
    timeout: float
) -> audit_v1_audit_event_query_service_pb2.ResolveAuditEventsResponse:
    raise RuntimeError("domain hook was not installed")


async def lineage_edge_calculation_compare_lineage_edge_options2(
    client: lineage_v1_lineage_node_calculation_service_pb2_grpc.LineageNodeCalculationServiceStub,
    request: lineage_v1_lineage_node_calculation_service_pb2.QuoteLineageNodeRequest,
    timeout: float
) -> lineage_v1_lineage_node_calculation_service_pb2.QuoteLineageNodeResponse:
    raise RuntimeError("domain hook was not installed")


async def lineage_edge_import_import_lineage_edges2(
    client: customers_v1_preference_validation_service_pb2_grpc.PreferenceValidationServiceStub,
    request: customers_v1_preference_validation_service_pb2.NormalizePreferenceRequest,
    timeout: float
) -> customers_v1_preference_validation_service_pb2.NormalizePreferenceResponse:
    raise RuntimeError("domain hook was not installed")


async def lineage_edge_lifecycle_reinstate_lineage_edge0(
    client: lineage_v1_lineage_node_sync_service_pb2_grpc.LineageNodeSyncServiceStub,
    request: lineage_v1_lineage_node_sync_service_pb2.PullLineageNodesRequest,
    timeout: float
) -> lineage_v1_lineage_node_sync_service_pb2.PullLineageNodesResponse:
    raise RuntimeError("domain hook was not installed")


async def lineage_edge_reporting_stream_lineage_edge_metrics0(
    client: lineage_v1_lineage_edge_import_service_pb2_grpc.LineageEdgeImportServiceStub,
    request: lineage_v1_lineage_edge_import_service_pb2.RetryLineageEdgeImportRequest,
    timeout: float
) -> lineage_v1_lineage_edge_import_service_pb2.RetryLineageEdgeImportResponse:
    raise RuntimeError("domain hook was not installed")


async def lineage_edge_validation_normalize_lineage_edge1(
    client: lineage_v1_impact_calculation_service_pb2_grpc.ImpactCalculationServiceStub,
    request: lineage_v1_impact_calculation_service_pb2.ExplainImpactCalculationRequest,
    timeout: float
) -> lineage_v1_impact_calculation_service_pb2.ExplainImpactCalculationResponse:
    raise RuntimeError("domain hook was not installed")


async def lineage_node_approval_comment_lineage_node_approval3(
    client: lineage_v1_lineage_node_lifecycle_service_pb2_grpc.LineageNodeLifecycleServiceStub,
    request: lineage_v1_lineage_node_lifecycle_service_pb2.ExpireLineageNodeRequest,
    timeout: float
) -> lineage_v1_lineage_node_lifecycle_service_pb2.ExpireLineageNodeResponse:
    raise RuntimeError("domain hook was not installed")


async def lineage_node_calculation_calculate_lineage_node0(
    client: dispatch_v1_dispatch_order_query_service_pb2_grpc.DispatchOrderQueryServiceStub,
    request: dispatch_v1_dispatch_order_query_service_pb2.SuggestDispatchOrdersRequest,
    timeout: float
) -> dispatch_v1_dispatch_order_query_service_pb2.SuggestDispatchOrdersResponse:
    raise RuntimeError("domain hook was not installed")


async def lineage_node_lifecycle_activate_lineage_node0(
    client: metrics_v1_dashboard_validation_service_pb2_grpc.DashboardValidationServiceStub,
    request: metrics_v1_dashboard_validation_service_pb2.ExplainDashboardDecisionRequest,
    timeout: float
) -> metrics_v1_dashboard_validation_service_pb2.ExplainDashboardDecisionResponse:
    raise RuntimeError("domain hook was not installed")


async def lineage_node_query_export_lineage_nodes2(
    client: lineage_v1_lineage_edge_validation_service_pb2_grpc.LineageEdgeValidationServiceStub,
    request: lineage_v1_lineage_edge_validation_service_pb2.CheckLineageEdgeEligibilityRequest,
    timeout: float
) -> lineage_v1_lineage_edge_validation_service_pb2.CheckLineageEdgeEligibilityResponse:
    raise RuntimeError("domain hook was not installed")


async def lineage_node_workflow_advance_lineage_node_workflow1(
    client: customers_v1_household_calculation_service_pb2_grpc.HouseholdCalculationServiceStub,
    request: customers_v1_household_calculation_service_pb2.EstimateHouseholdRequest,
    timeout: float
) -> customers_v1_household_calculation_service_pb2.EstimateHouseholdResponse:
    raise RuntimeError("domain hook was not installed")
