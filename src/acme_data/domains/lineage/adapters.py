"""Transport adapters used by lineage workflows."""

from __future__ import annotations

from typing import Protocol

from acme.analytics.v1 import funnel_validation_service_pb2 as analytics_v1_funnel_validation_service_pb2
from acme.analytics.v1 import funnel_validation_service_pb2_grpc as analytics_v1_funnel_validation_service_pb2_grpc
from acme.audit.v1 import audit_event_query_service_pb2 as audit_v1_audit_event_query_service_pb2
from acme.audit.v1 import audit_event_query_service_pb2_grpc as audit_v1_audit_event_query_service_pb2_grpc
from acme.customers.v1 import (
    consent_record_calculation_service_pb2 as customers_v1_consent_record_calculation_service_pb2,
)
from acme.customers.v1 import (
    consent_record_calculation_service_pb2_grpc as customers_v1_consent_record_calculation_service_pb2_grpc,
)
from acme.customers.v1 import customer_calculation_service_pb2 as customers_v1_customer_calculation_service_pb2
from acme.customers.v1 import (
    customer_calculation_service_pb2_grpc as customers_v1_customer_calculation_service_pb2_grpc,
)
from acme.customers.v1 import customer_validation_service_pb2 as customers_v1_customer_validation_service_pb2
from acme.customers.v1 import customer_validation_service_pb2_grpc as customers_v1_customer_validation_service_pb2_grpc
from acme.customers.v1 import household_calculation_service_pb2 as customers_v1_household_calculation_service_pb2
from acme.customers.v1 import (
    household_calculation_service_pb2_grpc as customers_v1_household_calculation_service_pb2_grpc,
)
from acme.customers.v1 import preference_calculation_service_pb2 as customers_v1_preference_calculation_service_pb2
from acme.customers.v1 import (
    preference_calculation_service_pb2_grpc as customers_v1_preference_calculation_service_pb2_grpc,
)
from acme.customers.v1 import preference_validation_service_pb2 as customers_v1_preference_validation_service_pb2
from acme.customers.v1 import (
    preference_validation_service_pb2_grpc as customers_v1_preference_validation_service_pb2_grpc,
)
from acme.dispatch.v1 import dispatch_order_query_service_pb2 as dispatch_v1_dispatch_order_query_service_pb2
from acme.dispatch.v1 import dispatch_order_query_service_pb2_grpc as dispatch_v1_dispatch_order_query_service_pb2_grpc
from acme.forecasting.v1 import (
    demand_forecast_validation_service_pb2 as forecasting_v1_demand_forecast_validation_service_pb2,
)
from acme.forecasting.v1 import (
    demand_forecast_validation_service_pb2_grpc as forecasting_v1_demand_forecast_validation_service_pb2_grpc,
)
from acme.forecasting.v1 import scenario_calculation_service_pb2 as forecasting_v1_scenario_calculation_service_pb2
from acme.forecasting.v1 import (
    scenario_calculation_service_pb2_grpc as forecasting_v1_scenario_calculation_service_pb2_grpc,
)
from acme.lending.v1 import loan_application_service_pb2 as lending_v1_loan_application_service_pb2
from acme.lending.v1 import loan_application_service_pb2_grpc as lending_v1_loan_application_service_pb2_grpc
from acme.lineage.v1 import impact_calculation_service_pb2 as lineage_v1_impact_calculation_service_pb2
from acme.lineage.v1 import impact_calculation_service_pb2_grpc as lineage_v1_impact_calculation_service_pb2_grpc
from acme.lineage.v1 import lineage_edge_approval_service_pb2 as lineage_v1_lineage_edge_approval_service_pb2
from acme.lineage.v1 import lineage_edge_approval_service_pb2_grpc as lineage_v1_lineage_edge_approval_service_pb2_grpc
from acme.lineage.v1 import lineage_edge_calculation_service_pb2 as lineage_v1_lineage_edge_calculation_service_pb2
from acme.lineage.v1 import (
    lineage_edge_calculation_service_pb2_grpc as lineage_v1_lineage_edge_calculation_service_pb2_grpc,
)
from acme.lineage.v1 import lineage_edge_import_service_pb2 as lineage_v1_lineage_edge_import_service_pb2
from acme.lineage.v1 import lineage_edge_import_service_pb2_grpc as lineage_v1_lineage_edge_import_service_pb2_grpc
from acme.lineage.v1 import lineage_edge_lifecycle_service_pb2 as lineage_v1_lineage_edge_lifecycle_service_pb2
from acme.lineage.v1 import (
    lineage_edge_lifecycle_service_pb2_grpc as lineage_v1_lineage_edge_lifecycle_service_pb2_grpc,
)
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
from acme.lineage.v1 import lineage_node_validation_service_pb2 as lineage_v1_lineage_node_validation_service_pb2
from acme.lineage.v1 import (
    lineage_node_validation_service_pb2_grpc as lineage_v1_lineage_node_validation_service_pb2_grpc,
)
from acme.metrics.v1 import dashboard_sync_service_pb2 as metrics_v1_dashboard_sync_service_pb2
from acme.metrics.v1 import dashboard_sync_service_pb2_grpc as metrics_v1_dashboard_sync_service_pb2_grpc
from acme.metrics.v1 import dashboard_validation_service_pb2 as metrics_v1_dashboard_validation_service_pb2
from acme.metrics.v1 import dashboard_validation_service_pb2_grpc as metrics_v1_dashboard_validation_service_pb2_grpc
from acme.metrics.v1 import metric_series_history_service_pb2 as metrics_v1_metric_series_history_service_pb2
from acme.metrics.v1 import metric_series_history_service_pb2_grpc as metrics_v1_metric_series_history_service_pb2_grpc
from acme.performers.v1 import performer_query_service_pb2 as performers_v1_performer_query_service_pb2
from acme.performers.v1 import performer_query_service_pb2_grpc as performers_v1_performer_query_service_pb2_grpc
from acme.prescriptions.v1 import (
    prescription_calculation_service_pb2 as prescriptions_v1_prescription_calculation_service_pb2,
)
from acme.prescriptions.v1 import (
    prescription_calculation_service_pb2_grpc as prescriptions_v1_prescription_calculation_service_pb2_grpc,
)
from acme.search.v1 import search_index_validation_service_pb2 as search_v1_search_index_validation_service_pb2
from acme.search.v1 import (
    search_index_validation_service_pb2_grpc as search_v1_search_index_validation_service_pb2_grpc,
)
from acme.venues.v1 import venue_validation_service_pb2 as venues_v1_venue_validation_service_pb2
from acme.venues.v1 import venue_validation_service_pb2_grpc as venues_v1_venue_validation_service_pb2_grpc


class ImpactApprovalDelegateImpactApproval1Adapter:
    def __init__(
        self,
        client: lineage_v1_lineage_edge_lifecycle_service_pb2_grpc.LineageEdgeLifecycleServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def __call__(
        self,
        request: lineage_v1_lineage_edge_lifecycle_service_pb2.ScheduleLineageEdgeExpiryRequest
    ) -> lineage_v1_lineage_edge_lifecycle_service_pb2.ScheduleLineageEdgeExpiryResponse:
        return await self.client.ScheduleLineageEdgeExpiry(request, timeout=self.timeout)


class ImpactCalculationCalculateImpact1Port(Protocol):
    async def execute(
        self,
        request: lineage_v1_lineage_node_calculation_service_pb2.SimulateLineageNodeRequest
    ) -> lineage_v1_lineage_node_calculation_service_pb2.SimulateLineageNodeResponse: ...


class ImpactCalculationCalculateImpact1Adapter:
    def __init__(
        self,
        client: lineage_v1_lineage_node_calculation_service_pb2_grpc.LineageNodeCalculationServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def execute(
        self,
        request: lineage_v1_lineage_node_calculation_service_pb2.SimulateLineageNodeRequest
    ) -> lineage_v1_lineage_node_calculation_service_pb2.SimulateLineageNodeResponse:
        return await self.client.SimulateLineageNode(request, timeout=self.timeout)


class ImpactCalculationCompareImpactOptions1Adapter:
    def __init__(
        self,
        client: lineage_v1_lineage_node_calculation_service_pb2_grpc.LineageNodeCalculationServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def __call__(
        self,
        request: lineage_v1_lineage_node_calculation_service_pb2.SimulateLineageNodeRequest
    ) -> lineage_v1_lineage_node_calculation_service_pb2.SimulateLineageNodeResponse:
        return await self.client.SimulateLineageNode(request, timeout=self.timeout)


async def impact_calculation_recalculate_impacts3(
    client: lineage_v1_lineage_node_calculation_service_pb2_grpc.LineageNodeCalculationServiceStub,
    request: lineage_v1_lineage_node_calculation_service_pb2.QuoteLineageNodeRequest,
    timeout: float
) -> lineage_v1_lineage_node_calculation_service_pb2.QuoteLineageNodeResponse:
    return await client.QuoteLineageNode(request, timeout=timeout)


async def impact_lifecycle_reinstate_impact1(
    client: customers_v1_customer_calculation_service_pb2_grpc.CustomerCalculationServiceStub,
    request: customers_v1_customer_calculation_service_pb2.RecalculateCustomersRequest,
    timeout: float
) -> customers_v1_customer_calculation_service_pb2.RecalculateCustomersResponse:
    return await client.RecalculateCustomers(request, timeout=timeout)


class ImpactLifecycleScheduleImpactExpiry0Port(Protocol):
    async def execute(
        self,
        request: customers_v1_preference_calculation_service_pb2.ComparePreferenceOptionsRequest
    ) -> customers_v1_preference_calculation_service_pb2.ComparePreferenceOptionsResponse: ...


class ImpactLifecycleScheduleImpactExpiry0Adapter:
    def __init__(
        self,
        client: customers_v1_preference_calculation_service_pb2_grpc.PreferenceCalculationServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def execute(
        self,
        request: customers_v1_preference_calculation_service_pb2.ComparePreferenceOptionsRequest
    ) -> customers_v1_preference_calculation_service_pb2.ComparePreferenceOptionsResponse:
        return await self.client.ComparePreferenceOptions(request, timeout=self.timeout)


class ImpactLifecycleTerminateImpact0Adapter:
    def __init__(
        self,
        client: venues_v1_venue_validation_service_pb2_grpc.VenueValidationServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def __call__(
        self,
        request: venues_v1_venue_validation_service_pb2.NormalizeVenueRequest
    ) -> venues_v1_venue_validation_service_pb2.NormalizeVenueResponse:
        return await self.client.NormalizeVenue(request, timeout=self.timeout)


async def impact_reporting_share_impact_report0(
    client: lending_v1_loan_application_service_pb2_grpc.LoanApplicationServiceStub,
    request: lending_v1_loan_application_service_pb2.CloneLoanApplicationRequest,
    timeout: float
) -> lending_v1_loan_application_service_pb2.CloneLoanApplicationResponse:
    return await client.CloneLoanApplication(request, timeout=timeout)


class ImpactReportingStreamImpactMetrics0Port(Protocol):
    async def execute(
        self,
        request: customers_v1_customer_validation_service_pb2.ExplainCustomerDecisionRequest
    ) -> customers_v1_customer_validation_service_pb2.ExplainCustomerDecisionResponse: ...


class ImpactReportingStreamImpactMetrics0Adapter:
    def __init__(
        self,
        client: customers_v1_customer_validation_service_pb2_grpc.CustomerValidationServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def execute(
        self,
        request: customers_v1_customer_validation_service_pb2.ExplainCustomerDecisionRequest
    ) -> customers_v1_customer_validation_service_pb2.ExplainCustomerDecisionResponse:
        return await self.client.ExplainCustomerDecision(request, timeout=self.timeout)


async def impact_sync_stream_impact_changes1(
    client: metrics_v1_metric_series_history_service_pb2_grpc.MetricSeriesHistoryServiceStub,
    request: metrics_v1_metric_series_history_service_pb2.CompareMetricSeriesVersionsRequest,
    timeout: float
) -> metrics_v1_metric_series_history_service_pb2.CompareMetricSeriesVersionsResponse:
    return await client.CompareMetricSeriesVersions(request, timeout=timeout)


async def impact_validation_lint_impacts1(
    client: lineage_v1_lineage_node_calculation_service_pb2_grpc.LineageNodeCalculationServiceStub,
    request: lineage_v1_lineage_node_calculation_service_pb2.EstimateLineageNodeRequest,
    timeout: float
) -> lineage_v1_lineage_node_calculation_service_pb2.EstimateLineageNodeResponse:
    return await client.EstimateLineageNode(request, timeout=timeout)


class ImpactValidationNormalizeImpact0Port(Protocol):
    async def execute(
        self,
        request: lineage_v1_lineage_node_calculation_service_pb2.RecalculateLineageNodesRequest
    ) -> lineage_v1_lineage_node_calculation_service_pb2.RecalculateLineageNodesResponse: ...


class ImpactValidationNormalizeImpact0Adapter:
    def __init__(
        self,
        client: lineage_v1_lineage_node_calculation_service_pb2_grpc.LineageNodeCalculationServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def execute(
        self,
        request: lineage_v1_lineage_node_calculation_service_pb2.RecalculateLineageNodesRequest
    ) -> lineage_v1_lineage_node_calculation_service_pb2.RecalculateLineageNodesResponse:
        return await self.client.RecalculateLineageNodes(request, timeout=self.timeout)


class ImpactValidationPreviewImpact0Adapter:
    def __init__(
        self,
        client: lineage_v1_lineage_node_validation_service_pb2_grpc.LineageNodeValidationServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def __call__(
        self,
        request: lineage_v1_lineage_node_validation_service_pb2.LintLineageNodesRequest
    ) -> lineage_v1_lineage_node_validation_service_pb2.LintLineageNodesResponse:
        return await self.client.LintLineageNodes(request, timeout=self.timeout)


async def impact_workflow_pause_impact_workflow1(
    client: audit_v1_audit_event_query_service_pb2_grpc.AuditEventQueryServiceStub,
    request: audit_v1_audit_event_query_service_pb2.ResolveAuditEventsRequest,
    timeout: float
) -> audit_v1_audit_event_query_service_pb2.ResolveAuditEventsResponse:
    return await client.ResolveAuditEvents(request, timeout=timeout)


class ImpactWorkflowSignalImpactWorkflow2Adapter:
    def __init__(
        self,
        client: forecasting_v1_demand_forecast_validation_service_pb2_grpc.DemandForecastValidationServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def __call__(
        self,
        request: forecasting_v1_demand_forecast_validation_service_pb2.ValidateDemandForecastRequest
    ) -> forecasting_v1_demand_forecast_validation_service_pb2.ValidateDemandForecastResponse:
        return await self.client.ValidateDemandForecast(request, timeout=self.timeout)


class LineageEdgeApprovalListPendingLineageEdges1Adapter:
    def __init__(
        self,
        client: forecasting_v1_scenario_calculation_service_pb2_grpc.ScenarioCalculationServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def __call__(
        self,
        request: forecasting_v1_scenario_calculation_service_pb2.QuoteScenarioRequest
    ) -> forecasting_v1_scenario_calculation_service_pb2.QuoteScenarioResponse:
        return await self.client.QuoteScenario(request, timeout=self.timeout)


async def lineage_edge_calculation_compare_lineage_edge_options2(
    client: lineage_v1_lineage_node_calculation_service_pb2_grpc.LineageNodeCalculationServiceStub,
    request: lineage_v1_lineage_node_calculation_service_pb2.QuoteLineageNodeRequest,
    timeout: float
) -> lineage_v1_lineage_node_calculation_service_pb2.QuoteLineageNodeResponse:
    return await client.QuoteLineageNode(request, timeout=timeout)


class LineageEdgeCalculationEstimateLineageEdge0Port(Protocol):
    async def execute(
        self,
        request: lineage_v1_lineage_node_calculation_service_pb2.RecalculateLineageNodesRequest
    ) -> lineage_v1_lineage_node_calculation_service_pb2.RecalculateLineageNodesResponse: ...


class LineageEdgeCalculationEstimateLineageEdge0Adapter:
    def __init__(
        self,
        client: lineage_v1_lineage_node_calculation_service_pb2_grpc.LineageNodeCalculationServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def execute(
        self,
        request: lineage_v1_lineage_node_calculation_service_pb2.RecalculateLineageNodesRequest
    ) -> lineage_v1_lineage_node_calculation_service_pb2.RecalculateLineageNodesResponse:
        return await self.client.RecalculateLineageNodes(request, timeout=self.timeout)


class LineageEdgeCalculationExplainLineageEdgeCalculation0Adapter:
    def __init__(
        self,
        client: prescriptions_v1_prescription_calculation_service_pb2_grpc.PrescriptionCalculationServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def __call__(
        self,
        request: prescriptions_v1_prescription_calculation_service_pb2.EstimatePrescriptionRequest
    ) -> prescriptions_v1_prescription_calculation_service_pb2.EstimatePrescriptionResponse:
        return await self.client.EstimatePrescription(request, timeout=self.timeout)


async def lineage_edge_import_import_lineage_edges2(
    client: customers_v1_preference_validation_service_pb2_grpc.PreferenceValidationServiceStub,
    request: customers_v1_preference_validation_service_pb2.NormalizePreferenceRequest,
    timeout: float
) -> customers_v1_preference_validation_service_pb2.NormalizePreferenceResponse:
    return await client.NormalizePreference(request, timeout=timeout)


class LineageEdgeImportMapLineageEdgeImportColumns0Port(Protocol):
    async def execute(
        self,
        request: lineage_v1_impact_calculation_service_pb2.SimulateImpactRequest
    ) -> lineage_v1_impact_calculation_service_pb2.SimulateImpactResponse: ...


class LineageEdgeImportMapLineageEdgeImportColumns0Adapter:
    def __init__(
        self,
        client: lineage_v1_impact_calculation_service_pb2_grpc.ImpactCalculationServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def execute(
        self,
        request: lineage_v1_impact_calculation_service_pb2.SimulateImpactRequest
    ) -> lineage_v1_impact_calculation_service_pb2.SimulateImpactResponse:
        return await self.client.SimulateImpact(request, timeout=self.timeout)


class LineageEdgeImportMapLineageEdgeImportColumns2Adapter:
    def __init__(
        self,
        client: customers_v1_consent_record_calculation_service_pb2_grpc.ConsentRecordCalculationServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def __call__(
        self,
        request: customers_v1_consent_record_calculation_service_pb2.CompareConsentRecordOptionsRequest
    ) -> customers_v1_consent_record_calculation_service_pb2.CompareConsentRecordOptionsResponse:
        return await self.client.CompareConsentRecordOptions(request, timeout=self.timeout)


async def lineage_edge_lifecycle_reinstate_lineage_edge0(
    client: lineage_v1_lineage_node_sync_service_pb2_grpc.LineageNodeSyncServiceStub,
    request: lineage_v1_lineage_node_sync_service_pb2.PullLineageNodesRequest,
    timeout: float
) -> lineage_v1_lineage_node_sync_service_pb2.PullLineageNodesResponse:
    return await client.PullLineageNodes(request, timeout=timeout)


class LineageEdgeLifecycleScheduleLineageEdgeExpiry0Adapter:
    def __init__(
        self,
        client: analytics_v1_funnel_validation_service_pb2_grpc.FunnelValidationServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def __call__(
        self,
        request: analytics_v1_funnel_validation_service_pb2.ScoreFunnelRequest
    ) -> analytics_v1_funnel_validation_service_pb2.ScoreFunnelResponse:
        return await self.client.ScoreFunnel(request, timeout=self.timeout)


class LineageEdgeQuerySummarizeLineageEdges2Adapter:
    def __init__(
        self,
        client: metrics_v1_dashboard_sync_service_pb2_grpc.DashboardSyncServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def __call__(
        self,
        request: metrics_v1_dashboard_sync_service_pb2.ListDashboardConflictsRequest
    ) -> metrics_v1_dashboard_sync_service_pb2.ListDashboardConflictsResponse:
        return await self.client.ListDashboardConflicts(request, timeout=self.timeout)


async def lineage_edge_reporting_stream_lineage_edge_metrics0(
    client: lineage_v1_lineage_edge_import_service_pb2_grpc.LineageEdgeImportServiceStub,
    request: lineage_v1_lineage_edge_import_service_pb2.RetryLineageEdgeImportRequest,
    timeout: float
) -> lineage_v1_lineage_edge_import_service_pb2.RetryLineageEdgeImportResponse:
    return await client.RetryLineageEdgeImport(request, timeout=timeout)


class LineageEdgeSyncPushLineageEdge1Port(Protocol):
    async def execute(
        self,
        request: lineage_v1_lineage_edge_import_service_pb2.CancelLineageEdgeImportRequest
    ) -> lineage_v1_lineage_edge_import_service_pb2.CancelLineageEdgeImportResponse: ...


class LineageEdgeSyncPushLineageEdge1Adapter:
    def __init__(
        self,
        client: lineage_v1_lineage_edge_import_service_pb2_grpc.LineageEdgeImportServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def execute(
        self,
        request: lineage_v1_lineage_edge_import_service_pb2.CancelLineageEdgeImportRequest
    ) -> lineage_v1_lineage_edge_import_service_pb2.CancelLineageEdgeImportResponse:
        return await self.client.CancelLineageEdgeImport(request, timeout=self.timeout)


async def lineage_edge_validation_normalize_lineage_edge1(
    client: lineage_v1_impact_calculation_service_pb2_grpc.ImpactCalculationServiceStub,
    request: lineage_v1_impact_calculation_service_pb2.ExplainImpactCalculationRequest,
    timeout: float
) -> lineage_v1_impact_calculation_service_pb2.ExplainImpactCalculationResponse:
    return await client.ExplainImpactCalculation(request, timeout=timeout)


class LineageEdgeValidationPreviewLineageEdge3Adapter:
    def __init__(
        self,
        client: performers_v1_performer_query_service_pb2_grpc.PerformerQueryServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def __call__(
        self,
        request: performers_v1_performer_query_service_pb2.SuggestPerformersRequest
    ) -> performers_v1_performer_query_service_pb2.SuggestPerformersResponse:
        return await self.client.SuggestPerformers(request, timeout=self.timeout)


class LineageEdgeWorkflowPauseLineageEdgeWorkflow0Port(Protocol):
    async def execute(
        self,
        request: lineage_v1_lineage_edge_approval_service_pb2.SubmitLineageEdgeRequest
    ) -> lineage_v1_lineage_edge_approval_service_pb2.SubmitLineageEdgeResponse: ...


class LineageEdgeWorkflowPauseLineageEdgeWorkflow0Adapter:
    def __init__(
        self,
        client: lineage_v1_lineage_edge_approval_service_pb2_grpc.LineageEdgeApprovalServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def execute(
        self,
        request: lineage_v1_lineage_edge_approval_service_pb2.SubmitLineageEdgeRequest
    ) -> lineage_v1_lineage_edge_approval_service_pb2.SubmitLineageEdgeResponse:
        return await self.client.SubmitLineageEdge(request, timeout=self.timeout)


async def lineage_node_approval_comment_lineage_node_approval3(
    client: lineage_v1_lineage_node_lifecycle_service_pb2_grpc.LineageNodeLifecycleServiceStub,
    request: lineage_v1_lineage_node_lifecycle_service_pb2.ExpireLineageNodeRequest,
    timeout: float
) -> lineage_v1_lineage_node_lifecycle_service_pb2.ExpireLineageNodeResponse:
    return await client.ExpireLineageNode(request, timeout=timeout)


async def lineage_node_calculation_calculate_lineage_node0(
    client: dispatch_v1_dispatch_order_query_service_pb2_grpc.DispatchOrderQueryServiceStub,
    request: dispatch_v1_dispatch_order_query_service_pb2.SuggestDispatchOrdersRequest,
    timeout: float
) -> dispatch_v1_dispatch_order_query_service_pb2.SuggestDispatchOrdersResponse:
    return await client.SuggestDispatchOrders(request, timeout=timeout)


class LineageNodeCalculationCalculateLineageNode2Port(Protocol):
    async def execute(
        self,
        request: search_v1_search_index_validation_service_pb2.NormalizeSearchIndexRequest
    ) -> search_v1_search_index_validation_service_pb2.NormalizeSearchIndexResponse: ...


class LineageNodeCalculationCalculateLineageNode2Adapter:
    def __init__(
        self,
        client: search_v1_search_index_validation_service_pb2_grpc.SearchIndexValidationServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def execute(
        self,
        request: search_v1_search_index_validation_service_pb2.NormalizeSearchIndexRequest
    ) -> search_v1_search_index_validation_service_pb2.NormalizeSearchIndexResponse:
        return await self.client.NormalizeSearchIndex(request, timeout=self.timeout)


async def lineage_node_lifecycle_activate_lineage_node0(
    client: metrics_v1_dashboard_validation_service_pb2_grpc.DashboardValidationServiceStub,
    request: metrics_v1_dashboard_validation_service_pb2.ExplainDashboardDecisionRequest,
    timeout: float
) -> metrics_v1_dashboard_validation_service_pb2.ExplainDashboardDecisionResponse:
    return await client.ExplainDashboardDecision(request, timeout=timeout)


class LineageNodeLifecycleExpireLineageNode0Port(Protocol):
    async def execute(
        self,
        request: performers_v1_performer_query_service_pb2.SuggestPerformersRequest
    ) -> performers_v1_performer_query_service_pb2.SuggestPerformersResponse: ...


class LineageNodeLifecycleExpireLineageNode0Adapter:
    def __init__(
        self,
        client: performers_v1_performer_query_service_pb2_grpc.PerformerQueryServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def execute(
        self,
        request: performers_v1_performer_query_service_pb2.SuggestPerformersRequest
    ) -> performers_v1_performer_query_service_pb2.SuggestPerformersResponse:
        return await self.client.SuggestPerformers(request, timeout=self.timeout)


async def lineage_node_query_export_lineage_nodes2(
    client: lineage_v1_lineage_edge_validation_service_pb2_grpc.LineageEdgeValidationServiceStub,
    request: lineage_v1_lineage_edge_validation_service_pb2.CheckLineageEdgeEligibilityRequest,
    timeout: float
) -> lineage_v1_lineage_edge_validation_service_pb2.CheckLineageEdgeEligibilityResponse:
    return await client.CheckLineageEdgeEligibility(request, timeout=timeout)


class LineageNodeQueryPeekLineageNode1Adapter:
    def __init__(
        self,
        client: lineage_v1_lineage_edge_validation_service_pb2_grpc.LineageEdgeValidationServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def __call__(
        self,
        request: lineage_v1_lineage_edge_validation_service_pb2.NormalizeLineageEdgeRequest
    ) -> lineage_v1_lineage_edge_validation_service_pb2.NormalizeLineageEdgeResponse:
        return await self.client.NormalizeLineageEdge(request, timeout=self.timeout)


class LineageNodeBatchGetLineageNodes1Adapter:
    def __init__(
        self,
        client: lineage_v1_lineage_edge_validation_service_pb2_grpc.LineageEdgeValidationServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def __call__(
        self,
        request: lineage_v1_lineage_edge_validation_service_pb2.ScoreLineageEdgeRequest
    ) -> lineage_v1_lineage_edge_validation_service_pb2.ScoreLineageEdgeResponse:
        return await self.client.ScoreLineageEdge(request, timeout=self.timeout)


class LineageNodeValidationCheckLineageNodeEligibility0Port(Protocol):
    async def execute(
        self,
        request: lineage_v1_lineage_node_calculation_service_pb2.ExplainLineageNodeCalculationRequest
    ) -> lineage_v1_lineage_node_calculation_service_pb2.ExplainLineageNodeCalculationResponse: ...


class LineageNodeValidationCheckLineageNodeEligibility0Adapter:
    def __init__(
        self,
        client: lineage_v1_lineage_node_calculation_service_pb2_grpc.LineageNodeCalculationServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def execute(
        self,
        request: lineage_v1_lineage_node_calculation_service_pb2.ExplainLineageNodeCalculationRequest
    ) -> lineage_v1_lineage_node_calculation_service_pb2.ExplainLineageNodeCalculationResponse:
        return await self.client.ExplainLineageNodeCalculation(request, timeout=self.timeout)


class LineageNodeValidationCheckLineageNodeEligibility2Adapter:
    def __init__(
        self,
        client: lineage_v1_lineage_edge_calculation_service_pb2_grpc.LineageEdgeCalculationServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def __call__(
        self,
        request: lineage_v1_lineage_edge_calculation_service_pb2.CompareLineageEdgeOptionsRequest
    ) -> lineage_v1_lineage_edge_calculation_service_pb2.CompareLineageEdgeOptionsResponse:
        return await self.client.CompareLineageEdgeOptions(request, timeout=self.timeout)


async def lineage_node_workflow_advance_lineage_node_workflow1(
    client: customers_v1_household_calculation_service_pb2_grpc.HouseholdCalculationServiceStub,
    request: customers_v1_household_calculation_service_pb2.EstimateHouseholdRequest,
    timeout: float
) -> customers_v1_household_calculation_service_pb2.EstimateHouseholdResponse:
    return await client.EstimateHousehold(request, timeout=timeout)
