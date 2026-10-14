"""Register and compose every service of the metrics domain."""

from __future__ import annotations

import grpc

from acme.featureflags.v1 import feature_flag_service_pb2_grpc as featureflags_v1_feature_flag_service_pb2_grpc
from acme.metrics.v1 import dashboard_admin_service_pb2_grpc as metrics_v1_dashboard_admin_service_pb2_grpc
from acme.metrics.v1 import dashboard_export_service_pb2_grpc as metrics_v1_dashboard_export_service_pb2_grpc
from acme.metrics.v1 import dashboard_history_service_pb2_grpc as metrics_v1_dashboard_history_service_pb2_grpc
from acme.metrics.v1 import (
    dashboard_notification_service_pb2_grpc as metrics_v1_dashboard_notification_service_pb2_grpc,
)
from acme.metrics.v1 import dashboard_sync_service_pb2_grpc as metrics_v1_dashboard_sync_service_pb2_grpc
from acme.metrics.v1 import dashboard_validation_service_pb2_grpc as metrics_v1_dashboard_validation_service_pb2_grpc
from acme.metrics.v1 import metric_alert_admin_service_pb2_grpc as metrics_v1_metric_alert_admin_service_pb2_grpc
from acme.metrics.v1 import metric_alert_export_service_pb2_grpc as metrics_v1_metric_alert_export_service_pb2_grpc
from acme.metrics.v1 import metric_alert_history_service_pb2_grpc as metrics_v1_metric_alert_history_service_pb2_grpc
from acme.metrics.v1 import (
    metric_alert_notification_service_pb2_grpc as metrics_v1_metric_alert_notification_service_pb2_grpc,
)
from acme.metrics.v1 import metric_alert_query_service_pb2_grpc as metrics_v1_metric_alert_query_service_pb2_grpc
from acme.metrics.v1 import (
    metric_alert_validation_service_pb2_grpc as metrics_v1_metric_alert_validation_service_pb2_grpc,
)
from acme.metrics.v1 import metric_series_admin_service_pb2_grpc as metrics_v1_metric_series_admin_service_pb2_grpc
from acme.metrics.v1 import metric_series_export_service_pb2_grpc as metrics_v1_metric_series_export_service_pb2_grpc
from acme.metrics.v1 import metric_series_history_service_pb2_grpc as metrics_v1_metric_series_history_service_pb2_grpc
from acme.metrics.v1 import (
    metric_series_notification_service_pb2_grpc as metrics_v1_metric_series_notification_service_pb2_grpc,
)
from acme.metrics.v1 import metric_series_query_service_pb2_grpc as metrics_v1_metric_series_query_service_pb2_grpc
from acme.metrics.v1 import metric_series_service_pb2_grpc as metrics_v1_metric_series_service_pb2_grpc
from acme.metrics.v1 import (
    metric_series_validation_service_pb2_grpc as metrics_v1_metric_series_validation_service_pb2_grpc,
)
from acme.venues.v1 import venue_query_service_pb2_grpc as venues_v1_venue_query_service_pb2_grpc
from acme.venues.v1 import venue_service_pb2_grpc as venues_v1_venue_service_pb2_grpc
from acme.venues.v1 import venue_validation_service_pb2_grpc as venues_v1_venue_validation_service_pb2_grpc

from acme_data.domains.metrics.dashboard_admin_service import DashboardAdminServicer
from acme_data.domains.metrics.dashboard_export_service import DashboardExportServicer
from acme_data.domains.metrics.dashboard_history_service import DashboardHistoryServicer
from acme_data.domains.metrics.dashboard_notification_service import DashboardNotificationServicer
from acme_data.domains.metrics.dashboard_sync_service import DashboardSyncServicer
from acme_data.domains.metrics.dashboard_validation_service import DashboardValidationServicer
from acme_data.domains.metrics.dependencies import Clients
from acme_data.domains.metrics.dependencies import Dependencies
from acme_data.domains.metrics.events import subscribe
from acme_data.domains.metrics.metric_alert_admin_service import MetricAlertAdminServicer
from acme_data.domains.metrics.metric_alert_export_service import MetricAlertExportServicer
from acme_data.domains.metrics.metric_alert_history_service import MetricAlertHistoryServicer
from acme_data.domains.metrics.metric_alert_notification_service import MetricAlertNotificationServicer
from acme_data.domains.metrics.metric_alert_query_service import MetricAlertQueryServicer
from acme_data.domains.metrics.metric_alert_validation_service import MetricAlertValidationServicer
from acme_data.domains.metrics.metric_series_admin_service import MetricSeriesAdminServicer
from acme_data.domains.metrics.metric_series_export_service import MetricSeriesExportServicer
from acme_data.domains.metrics.metric_series_history_service import MetricSeriesHistoryServicer
from acme_data.domains.metrics.metric_series_notification_service import MetricSeriesNotificationServicer
from acme_data.domains.metrics.metric_series_query_service import MetricSeriesQueryServicer
from acme_data.domains.metrics.metric_series_service import MetricSeriesServicer
from acme_data.domains.metrics.metric_series_validation_service import MetricSeriesValidationServicer
from acme_data.domains.metrics.repository import DomainRepository
from acme_data.platform.container import Container
from acme_data.platform.container import Factory


def dependencies(container: Container) -> Dependencies:
    featureflags_feature_flag = container.singleton(
        featureflags_v1_feature_flag_service_pb2_grpc.FeatureFlagServiceStub,
        lambda: featureflags_v1_feature_flag_service_pb2_grpc.FeatureFlagServiceStub(container.channel)
    )
    metrics_dashboard_admin = container.singleton(
        metrics_v1_dashboard_admin_service_pb2_grpc.DashboardAdminServiceStub,
        lambda: metrics_v1_dashboard_admin_service_pb2_grpc.DashboardAdminServiceStub(container.channel)
    )
    metrics_dashboard_export = container.singleton(
        metrics_v1_dashboard_export_service_pb2_grpc.DashboardExportServiceStub,
        lambda: metrics_v1_dashboard_export_service_pb2_grpc.DashboardExportServiceStub(container.channel)
    )
    metrics_dashboard_history = container.singleton(
        metrics_v1_dashboard_history_service_pb2_grpc.DashboardHistoryServiceStub,
        lambda: metrics_v1_dashboard_history_service_pb2_grpc.DashboardHistoryServiceStub(container.channel)
    )
    metrics_dashboard_sync = container.singleton(
        metrics_v1_dashboard_sync_service_pb2_grpc.DashboardSyncServiceStub,
        lambda: metrics_v1_dashboard_sync_service_pb2_grpc.DashboardSyncServiceStub(container.channel)
    )
    metrics_metric_alert_export = container.singleton(
        metrics_v1_metric_alert_export_service_pb2_grpc.MetricAlertExportServiceStub,
        lambda: metrics_v1_metric_alert_export_service_pb2_grpc.MetricAlertExportServiceStub(container.channel)
    )
    metrics_metric_series_admin = container.singleton(
        metrics_v1_metric_series_admin_service_pb2_grpc.MetricSeriesAdminServiceStub,
        lambda: metrics_v1_metric_series_admin_service_pb2_grpc.MetricSeriesAdminServiceStub(container.channel)
    )
    metrics_metric_series_export = container.singleton(
        metrics_v1_metric_series_export_service_pb2_grpc.MetricSeriesExportServiceStub,
        lambda: metrics_v1_metric_series_export_service_pb2_grpc.MetricSeriesExportServiceStub(container.channel)
    )
    metrics_metric_series_history = container.singleton(
        metrics_v1_metric_series_history_service_pb2_grpc.MetricSeriesHistoryServiceStub,
        lambda: metrics_v1_metric_series_history_service_pb2_grpc.MetricSeriesHistoryServiceStub(container.channel)
    )
    metrics_metric_series_notification = container.singleton(
        metrics_v1_metric_series_notification_service_pb2_grpc.MetricSeriesNotificationServiceStub,
        lambda: metrics_v1_metric_series_notification_service_pb2_grpc.MetricSeriesNotificationServiceStub(
            container.channel
        )
    )
    venues_venue_query = container.singleton(
        venues_v1_venue_query_service_pb2_grpc.VenueQueryServiceStub,
        lambda: venues_v1_venue_query_service_pb2_grpc.VenueQueryServiceStub(container.channel)
    )
    venues_venue = container.singleton(
        venues_v1_venue_service_pb2_grpc.VenueServiceStub,
        lambda: venues_v1_venue_service_pb2_grpc.VenueServiceStub(container.channel)
    )
    venues_venue_validation = container.singleton(
        venues_v1_venue_validation_service_pb2_grpc.VenueValidationServiceStub,
        lambda: venues_v1_venue_validation_service_pb2_grpc.VenueValidationServiceStub(container.channel)
    )
    clients = Clients(
        featureflags_feature_flag=featureflags_feature_flag,
        metrics_dashboard_admin=metrics_dashboard_admin,
        metrics_dashboard_export=metrics_dashboard_export,
        metrics_dashboard_history=metrics_dashboard_history,
        metrics_dashboard_sync=metrics_dashboard_sync,
        metrics_metric_alert_export=metrics_metric_alert_export,
        metrics_metric_series_admin=metrics_metric_series_admin,
        metrics_metric_series_export=metrics_metric_series_export,
        metrics_metric_series_history=metrics_metric_series_history,
        metrics_metric_series_notification=metrics_metric_series_notification,
        venues_venue_query=venues_venue_query,
        venues_venue=venues_venue,
        venues_venue_validation=venues_venue_validation,
        registry={
            'acme.featureflags.v1.FeatureFlagService': featureflags_feature_flag,
            'acme.metrics.v1.DashboardAdminService': metrics_dashboard_admin,
            'acme.metrics.v1.DashboardExportService': metrics_dashboard_export,
            'acme.metrics.v1.DashboardHistoryService': metrics_dashboard_history,
            'acme.metrics.v1.DashboardSyncService': metrics_dashboard_sync,
            'acme.metrics.v1.MetricAlertExportService': metrics_metric_alert_export,
            'acme.metrics.v1.MetricSeriesAdminService': metrics_metric_series_admin,
            'acme.metrics.v1.MetricSeriesExportService': metrics_metric_series_export,
            'acme.metrics.v1.MetricSeriesHistoryService': metrics_metric_series_history,
            'acme.metrics.v1.MetricSeriesNotificationService': metrics_metric_series_notification,
            'acme.venues.v1.VenueQueryService': venues_venue_query,
            'acme.venues.v1.VenueService': venues_venue,
            'acme.venues.v1.VenueValidationService': venues_venue_validation,
        },
    )
    return Dependencies(clients, DomainRepository(container.sessions),
                        container.settings, container.bus)


def register(server: grpc.aio.Server, container: Container) -> dict[str, object]:
    deps = dependencies(container)
    registered: dict[str, object] = {}
    dashboard_admin_servicer = Factory(lambda: DashboardAdminServicer(deps))()
    metrics_v1_dashboard_admin_service_pb2_grpc.add_DashboardAdminServiceServicer_to_server(
        dashboard_admin_servicer,
        server
    )
    registered['acme.metrics.v1.DashboardAdminService'] = dashboard_admin_servicer
    dashboard_export_servicer = Factory(lambda: DashboardExportServicer(deps))()
    metrics_v1_dashboard_export_service_pb2_grpc.add_DashboardExportServiceServicer_to_server(
        dashboard_export_servicer,
        server
    )
    registered['acme.metrics.v1.DashboardExportService'] = dashboard_export_servicer
    dashboard_history_servicer = Factory(lambda: DashboardHistoryServicer(deps))()
    metrics_v1_dashboard_history_service_pb2_grpc.add_DashboardHistoryServiceServicer_to_server(
        dashboard_history_servicer,
        server
    )
    registered['acme.metrics.v1.DashboardHistoryService'] = dashboard_history_servicer
    dashboard_notification_servicer = Factory(lambda: DashboardNotificationServicer(deps))()
    metrics_v1_dashboard_notification_service_pb2_grpc.add_DashboardNotificationServiceServicer_to_server(
        dashboard_notification_servicer,
        server
    )
    registered['acme.metrics.v1.DashboardNotificationService'] = dashboard_notification_servicer
    dashboard_sync_servicer = Factory(lambda: DashboardSyncServicer(deps))()
    metrics_v1_dashboard_sync_service_pb2_grpc.add_DashboardSyncServiceServicer_to_server(
        dashboard_sync_servicer,
        server
    )
    registered['acme.metrics.v1.DashboardSyncService'] = dashboard_sync_servicer
    dashboard_validation_servicer = Factory(lambda: DashboardValidationServicer(deps))()
    metrics_v1_dashboard_validation_service_pb2_grpc.add_DashboardValidationServiceServicer_to_server(
        dashboard_validation_servicer,
        server
    )
    registered['acme.metrics.v1.DashboardValidationService'] = dashboard_validation_servicer
    metric_alert_admin_servicer = Factory(lambda: MetricAlertAdminServicer(deps))()
    metrics_v1_metric_alert_admin_service_pb2_grpc.add_MetricAlertAdminServiceServicer_to_server(
        metric_alert_admin_servicer,
        server
    )
    registered['acme.metrics.v1.MetricAlertAdminService'] = metric_alert_admin_servicer
    metric_alert_export_servicer = Factory(lambda: MetricAlertExportServicer(deps))()
    metrics_v1_metric_alert_export_service_pb2_grpc.add_MetricAlertExportServiceServicer_to_server(
        metric_alert_export_servicer,
        server
    )
    registered['acme.metrics.v1.MetricAlertExportService'] = metric_alert_export_servicer
    metric_alert_history_servicer = Factory(lambda: MetricAlertHistoryServicer(deps))()
    metrics_v1_metric_alert_history_service_pb2_grpc.add_MetricAlertHistoryServiceServicer_to_server(
        metric_alert_history_servicer,
        server
    )
    registered['acme.metrics.v1.MetricAlertHistoryService'] = metric_alert_history_servicer
    metric_alert_notification_servicer = Factory(lambda: MetricAlertNotificationServicer(deps))()
    metrics_v1_metric_alert_notification_service_pb2_grpc.add_MetricAlertNotificationServiceServicer_to_server(
        metric_alert_notification_servicer,
        server
    )
    registered['acme.metrics.v1.MetricAlertNotificationService'] = metric_alert_notification_servicer
    metric_alert_query_servicer = Factory(lambda: MetricAlertQueryServicer(deps))()
    metrics_v1_metric_alert_query_service_pb2_grpc.add_MetricAlertQueryServiceServicer_to_server(
        metric_alert_query_servicer,
        server
    )
    registered['acme.metrics.v1.MetricAlertQueryService'] = metric_alert_query_servicer
    metric_alert_validation_servicer = Factory(lambda: MetricAlertValidationServicer(deps))()
    metrics_v1_metric_alert_validation_service_pb2_grpc.add_MetricAlertValidationServiceServicer_to_server(
        metric_alert_validation_servicer,
        server
    )
    registered['acme.metrics.v1.MetricAlertValidationService'] = metric_alert_validation_servicer
    metric_series_admin_servicer = Factory(lambda: MetricSeriesAdminServicer(deps))()
    metrics_v1_metric_series_admin_service_pb2_grpc.add_MetricSeriesAdminServiceServicer_to_server(
        metric_series_admin_servicer,
        server
    )
    registered['acme.metrics.v1.MetricSeriesAdminService'] = metric_series_admin_servicer
    metric_series_export_servicer = Factory(lambda: MetricSeriesExportServicer(deps))()
    metrics_v1_metric_series_export_service_pb2_grpc.add_MetricSeriesExportServiceServicer_to_server(
        metric_series_export_servicer,
        server
    )
    registered['acme.metrics.v1.MetricSeriesExportService'] = metric_series_export_servicer
    metric_series_history_servicer = Factory(lambda: MetricSeriesHistoryServicer(deps))()
    metrics_v1_metric_series_history_service_pb2_grpc.add_MetricSeriesHistoryServiceServicer_to_server(
        metric_series_history_servicer,
        server
    )
    registered['acme.metrics.v1.MetricSeriesHistoryService'] = metric_series_history_servicer
    metric_series_notification_servicer = Factory(lambda: MetricSeriesNotificationServicer(deps))()
    metrics_v1_metric_series_notification_service_pb2_grpc.add_MetricSeriesNotificationServiceServicer_to_server(
        metric_series_notification_servicer,
        server
    )
    registered['acme.metrics.v1.MetricSeriesNotificationService'] = metric_series_notification_servicer
    metric_series_query_servicer = Factory(lambda: MetricSeriesQueryServicer(deps))()
    metrics_v1_metric_series_query_service_pb2_grpc.add_MetricSeriesQueryServiceServicer_to_server(
        metric_series_query_servicer,
        server
    )
    registered['acme.metrics.v1.MetricSeriesQueryService'] = metric_series_query_servicer
    metric_series_servicer = Factory(lambda: MetricSeriesServicer(deps))()
    metrics_v1_metric_series_service_pb2_grpc.add_MetricSeriesServiceServicer_to_server(metric_series_servicer, server)
    registered['acme.metrics.v1.MetricSeriesService'] = metric_series_servicer
    metric_series_validation_servicer = Factory(lambda: MetricSeriesValidationServicer(deps))()
    metrics_v1_metric_series_validation_service_pb2_grpc.add_MetricSeriesValidationServiceServicer_to_server(
        metric_series_validation_servicer,
        server
    )
    registered['acme.metrics.v1.MetricSeriesValidationService'] = metric_series_validation_servicer
    subscribe(deps)
    return registered
