"""Background event handlers owned by the metrics team."""

from __future__ import annotations

from functools import partial
from typing import cast

from google.protobuf.message import Message

from acme.metrics.v1 import dashboard_admin_service_pb2 as metrics_v1_dashboard_admin_service_pb2
from acme.metrics.v1 import metric_series_admin_service_pb2 as metrics_v1_metric_series_admin_service_pb2

from acme_data.domains.metrics.dependencies import Dependencies


async def on_dashboard_notification_service_notify_dashboard_watchers_0(
    deps: Dependencies,
    payload: Message
) -> Message:
    request = cast(metrics_v1_dashboard_admin_service_pb2.ReassignDashboardRequest, payload)
    return await deps.clients.metrics_dashboard_admin.ReassignDashboard(request, timeout=deps.settings.timeout)


async def on_metric_series_history_service_prune_metric_series_versions_0(
    deps: Dependencies,
    payload: Message
) -> Message:
    request = cast(metrics_v1_metric_series_admin_service_pb2.ArchiveMetricSeriesRequest, payload)
    return await deps.clients.metrics_metric_series_admin.ArchiveMetricSeries(request, timeout=deps.settings.timeout)


def subscribe(deps: Dependencies) -> None:
    deps.bus.subscribe(
        'acme.metrics.v1.DashboardNotificationService/NotifyDashboardWatchers/0',
        partial(on_dashboard_notification_service_notify_dashboard_watchers_0, deps)
    )
    deps.bus.subscribe(
        'acme.metrics.v1.MetricSeriesHistoryService/PruneMetricSeriesVersions/0',
        partial(on_metric_series_history_service_prune_metric_series_versions_0, deps)
    )
