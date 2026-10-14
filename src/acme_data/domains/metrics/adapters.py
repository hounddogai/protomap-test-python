"""Transport adapters used by metrics workflows."""

from __future__ import annotations

from typing import Protocol

from acme.metrics.v1 import dashboard_export_service_pb2 as metrics_v1_dashboard_export_service_pb2
from acme.metrics.v1 import dashboard_export_service_pb2_grpc as metrics_v1_dashboard_export_service_pb2_grpc
from acme.metrics.v1 import metric_series_notification_service_pb2 as metrics_v1_metric_series_notification_service_pb2
from acme.metrics.v1 import (
    metric_series_notification_service_pb2_grpc as metrics_v1_metric_series_notification_service_pb2_grpc,
)
from acme.venues.v1 import venue_service_pb2 as venues_v1_venue_service_pb2
from acme.venues.v1 import venue_service_pb2_grpc as venues_v1_venue_service_pb2_grpc


class DashboardAdminPurgeDashboard0Port(Protocol):
    async def execute(
        self,
        request: metrics_v1_dashboard_export_service_pb2.ShareDashboardExportRequest
    ) -> metrics_v1_dashboard_export_service_pb2.ShareDashboardExportResponse: ...


class DashboardAdminPurgeDashboard0Adapter:
    def __init__(
        self,
        client: metrics_v1_dashboard_export_service_pb2_grpc.DashboardExportServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def execute(
        self,
        request: metrics_v1_dashboard_export_service_pb2.ShareDashboardExportRequest
    ) -> metrics_v1_dashboard_export_service_pb2.ShareDashboardExportResponse:
        return await self.client.ShareDashboardExport(request, timeout=self.timeout)


class MetricSeriesExportShareMetricSeriesExport0Port(Protocol):
    async def execute(
        self,
        request: venues_v1_venue_service_pb2.CloneVenueRequest
    ) -> venues_v1_venue_service_pb2.CloneVenueResponse: ...


class MetricSeriesExportShareMetricSeriesExport0Adapter:
    def __init__(self, client: venues_v1_venue_service_pb2_grpc.VenueServiceStub, timeout: float) -> None:
        self.client = client
        self.timeout = timeout

    async def execute(
        self,
        request: venues_v1_venue_service_pb2.CloneVenueRequest
    ) -> venues_v1_venue_service_pb2.CloneVenueResponse:
        return await self.client.CloneVenue(request, timeout=self.timeout)


class MetricSeriesHistoryCompareMetricSeriesVersions0Adapter:
    def __init__(
        self,
        client: metrics_v1_metric_series_notification_service_pb2_grpc.MetricSeriesNotificationServiceStub,
        timeout: float
    ) -> None:
        self.client = client
        self.timeout = timeout

    async def __call__(
        self,
        request: metrics_v1_metric_series_notification_service_pb2.GetMetricSeriesPreferencesRequest
    ) -> metrics_v1_metric_series_notification_service_pb2.GetMetricSeriesPreferencesResponse:
        return await self.client.GetMetricSeriesPreferences(request, timeout=self.timeout)
