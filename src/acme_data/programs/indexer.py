"""Consume changes and refresh the search projection."""

from __future__ import annotations

import argparse
import asyncio
import logging
import os

import grpc

from acme.analytics.v1 import analytics_event_service_pb2 as analytics_v1_analytics_event_service_pb2
from acme.analytics.v1 import analytics_event_service_pb2_grpc as analytics_v1_analytics_event_service_pb2_grpc
from acme.analytics.v1 import (
    analytics_event_validation_service_pb2 as analytics_v1_analytics_event_validation_service_pb2,
)
from acme.analytics.v1 import (
    analytics_event_validation_service_pb2_grpc as analytics_v1_analytics_event_validation_service_pb2_grpc,
)
from acme.analytics.v1 import analytics_pb2 as analytics_v1_analytics_pb2
from acme.common.v1 import context_pb2 as common_v1_context_pb2
from acme.datahub.v1 import data_share_reporting_service_pb2 as datahub_v1_data_share_reporting_service_pb2
from acme.datahub.v1 import data_share_reporting_service_pb2_grpc as datahub_v1_data_share_reporting_service_pb2_grpc
from acme.datahub.v1 import data_share_validation_service_pb2 as datahub_v1_data_share_validation_service_pb2
from acme.datahub.v1 import data_share_validation_service_pb2_grpc as datahub_v1_data_share_validation_service_pb2_grpc
from acme.datahub.v1 import datahub_pb2 as datahub_v1_datahub_pb2
from acme.datasets.v1 import dataset_service_pb2 as datasets_v1_dataset_service_pb2
from acme.datasets.v1 import dataset_service_pb2_grpc as datasets_v1_dataset_service_pb2_grpc
from acme.datasets.v1 import dataset_validation_service_pb2 as datasets_v1_dataset_validation_service_pb2
from acme.datasets.v1 import dataset_validation_service_pb2_grpc as datasets_v1_dataset_validation_service_pb2_grpc
from acme.datasets.v1 import datasets_pb2 as datasets_v1_datasets_pb2
from acme.featurestore.v1 import entity_calculation_service_pb2 as featurestore_v1_entity_calculation_service_pb2
from acme.featurestore.v1 import (
    entity_calculation_service_pb2_grpc as featurestore_v1_entity_calculation_service_pb2_grpc,
)
from acme.featurestore.v1 import entity_reporting_service_pb2 as featurestore_v1_entity_reporting_service_pb2
from acme.featurestore.v1 import entity_reporting_service_pb2_grpc as featurestore_v1_entity_reporting_service_pb2_grpc
from acme.featurestore.v1 import featurestore_pb2 as featurestore_v1_featurestore_pb2
from acme.labeling.v1 import annotation_calculation_service_pb2 as labeling_v1_annotation_calculation_service_pb2
from acme.labeling.v1 import (
    annotation_calculation_service_pb2_grpc as labeling_v1_annotation_calculation_service_pb2_grpc,
)
from acme.labeling.v1 import annotation_reporting_service_pb2 as labeling_v1_annotation_reporting_service_pb2
from acme.labeling.v1 import annotation_reporting_service_pb2_grpc as labeling_v1_annotation_reporting_service_pb2_grpc
from acme.labeling.v1 import labeling_pb2 as labeling_v1_labeling_pb2
from acme.lineage.v1 import impact_calculation_service_pb2 as lineage_v1_impact_calculation_service_pb2
from acme.lineage.v1 import impact_calculation_service_pb2_grpc as lineage_v1_impact_calculation_service_pb2_grpc
from acme.lineage.v1 import impact_reporting_service_pb2 as lineage_v1_impact_reporting_service_pb2
from acme.lineage.v1 import impact_reporting_service_pb2_grpc as lineage_v1_impact_reporting_service_pb2_grpc
from acme.lineage.v1 import lineage_pb2 as lineage_v1_lineage_pb2
from acme.metrics.v1 import dashboard_notification_service_pb2 as metrics_v1_dashboard_notification_service_pb2
from acme.metrics.v1 import (
    dashboard_notification_service_pb2_grpc as metrics_v1_dashboard_notification_service_pb2_grpc,
)
from acme.metrics.v1 import dashboard_validation_service_pb2 as metrics_v1_dashboard_validation_service_pb2
from acme.metrics.v1 import dashboard_validation_service_pb2_grpc as metrics_v1_dashboard_validation_service_pb2_grpc
from acme.metrics.v1 import metrics_pb2 as metrics_v1_metrics_pb2
from acme.modelregistry.v1 import (
    deployment_calculation_service_pb2 as modelregistry_v1_deployment_calculation_service_pb2,
)
from acme.modelregistry.v1 import (
    deployment_calculation_service_pb2_grpc as modelregistry_v1_deployment_calculation_service_pb2_grpc,
)
from acme.modelregistry.v1 import deployment_reporting_service_pb2 as modelregistry_v1_deployment_reporting_service_pb2
from acme.modelregistry.v1 import (
    deployment_reporting_service_pb2_grpc as modelregistry_v1_deployment_reporting_service_pb2_grpc,
)
from acme.modelregistry.v1 import modelregistry_pb2 as modelregistry_v1_modelregistry_pb2
from acme.pipelines.v1 import pipeline_calculation_service_pb2 as pipelines_v1_pipeline_calculation_service_pb2
from acme.pipelines.v1 import (
    pipeline_calculation_service_pb2_grpc as pipelines_v1_pipeline_calculation_service_pb2_grpc,
)
from acme.pipelines.v1 import pipeline_reporting_service_pb2 as pipelines_v1_pipeline_reporting_service_pb2
from acme.pipelines.v1 import pipeline_reporting_service_pb2_grpc as pipelines_v1_pipeline_reporting_service_pb2_grpc
from acme.pipelines.v1 import pipelines_pb2 as pipelines_v1_pipelines_pb2


async def refresh_analytics(
    channel: grpc.aio.Channel, context: common_v1_context_pb2.RequestContext,
    metadata: tuple[tuple[str, str], ...],
) -> None:
    source = analytics_v1_analytics_event_service_pb2_grpc.AnalyticsEventServiceStub(channel)
    target = analytics_v1_analytics_event_validation_service_pb2_grpc.AnalyticsEventValidationServiceStub(channel)
    request = analytics_v1_analytics_event_service_pb2.WatchAnalyticsEventsRequest(context=context)
    stream = source.WatchAnalyticsEvents(request, timeout=30, metadata=metadata)
    async for change in stream:
        record = change.analytics_event
        outgoing = analytics_v1_analytics_event_validation_service_pb2.ExplainAnalyticsEventDecisionRequest(
            analytics_event=analytics_v1_analytics_pb2.AnalyticsEvent(
                analytics_event_id=record.analytics_event_id,
                kind=record.kind
            ),
            analytics_event_id=record.analytics_event_id,
            context=context
        )
        await target.ExplainAnalyticsEventDecision(outgoing, timeout=5, metadata=metadata)


async def refresh_datahub(
    channel: grpc.aio.Channel, context: common_v1_context_pb2.RequestContext,
    metadata: tuple[tuple[str, str], ...],
) -> None:
    source = datahub_v1_data_share_reporting_service_pb2_grpc.DataShareReportingServiceStub(channel)
    target = datahub_v1_data_share_validation_service_pb2_grpc.DataShareValidationServiceStub(channel)
    request = datahub_v1_data_share_reporting_service_pb2.StreamDataShareMetricsRequest(context=context)
    stream = source.StreamDataShareMetrics(request, timeout=30, metadata=metadata)
    async for change in stream:
        record = change.data_share
        outgoing = datahub_v1_data_share_validation_service_pb2.CheckDataShareEligibilityRequest(
            context=context,
            data_share=datahub_v1_datahub_pb2.DataShare(
                data_share_id=record.data_share_id,
                number=record.counterparty.number
            ),
            data_share_id=record.data_share_id
        )
        await target.CheckDataShareEligibility(outgoing, timeout=5, metadata=metadata)


async def refresh_datasets(
    channel: grpc.aio.Channel, context: common_v1_context_pb2.RequestContext,
    metadata: tuple[tuple[str, str], ...],
) -> None:
    source = datasets_v1_dataset_service_pb2_grpc.DatasetServiceStub(channel)
    target = datasets_v1_dataset_validation_service_pb2_grpc.DatasetValidationServiceStub(channel)
    request = datasets_v1_dataset_service_pb2.WatchDatasetsRequest(context=context)
    stream = source.WatchDatasets(request, timeout=30, metadata=metadata)
    async for change in stream:
        record = change.dataset
        outgoing = datasets_v1_dataset_validation_service_pb2.CheckDatasetEligibilityRequest(
            context=context,
            dataset=datasets_v1_datasets_pb2.Dataset(code=record.code, dataset_id=record.dataset_id),
            dataset_id=record.dataset_id
        )
        await target.CheckDatasetEligibility(outgoing, timeout=5, metadata=metadata)


async def refresh_featurestore(
    channel: grpc.aio.Channel, context: common_v1_context_pb2.RequestContext,
    metadata: tuple[tuple[str, str], ...],
) -> None:
    source = featurestore_v1_entity_reporting_service_pb2_grpc.EntityReportingServiceStub(channel)
    target = featurestore_v1_entity_calculation_service_pb2_grpc.EntityCalculationServiceStub(channel)
    request = featurestore_v1_entity_reporting_service_pb2.StreamEntityMetricsRequest(context=context)
    stream = source.StreamEntityMetrics(request, timeout=30, metadata=metadata)
    async for change in stream:
        record = change.entity
        outgoing = featurestore_v1_entity_calculation_service_pb2.CalculateEntityRequest(
            context=context,
            entity=featurestore_v1_featurestore_pb2.Entity(entity_id=record.entity_id, name=record.contact.name),
            entity_id=record.entity_id
        )
        await target.CalculateEntity(outgoing, timeout=5, metadata=metadata)


async def refresh_labeling(
    channel: grpc.aio.Channel, context: common_v1_context_pb2.RequestContext,
    metadata: tuple[tuple[str, str], ...],
) -> None:
    source = labeling_v1_annotation_reporting_service_pb2_grpc.AnnotationReportingServiceStub(channel)
    target = labeling_v1_annotation_calculation_service_pb2_grpc.AnnotationCalculationServiceStub(channel)
    request = labeling_v1_annotation_reporting_service_pb2.StreamAnnotationMetricsRequest(context=context)
    stream = source.StreamAnnotationMetrics(request, timeout=30, metadata=metadata)
    async for change in stream:
        record = change.annotation
        outgoing = labeling_v1_annotation_calculation_service_pb2.CalculateAnnotationRequest(
            annotation=labeling_v1_labeling_pb2.Annotation(annotation_id=record.annotation_id, kind=record.kind),
            annotation_id=record.annotation_id,
            context=context
        )
        await target.CalculateAnnotation(outgoing, timeout=5, metadata=metadata)


async def refresh_lineage(
    channel: grpc.aio.Channel, context: common_v1_context_pb2.RequestContext,
    metadata: tuple[tuple[str, str], ...],
) -> None:
    source = lineage_v1_impact_reporting_service_pb2_grpc.ImpactReportingServiceStub(channel)
    target = lineage_v1_impact_calculation_service_pb2_grpc.ImpactCalculationServiceStub(channel)
    request = lineage_v1_impact_reporting_service_pb2.StreamImpactMetricsRequest(context=context)
    stream = source.StreamImpactMetrics(request, timeout=30, metadata=metadata)
    async for change in stream:
        record = change.impact
        outgoing = lineage_v1_impact_calculation_service_pb2.CalculateImpactRequest(
            context=context,
            impact=lineage_v1_lineage_pb2.Impact(impact_id=record.impact_id, subject=record.subject),
            impact_id=record.impact_id
        )
        await target.CalculateImpact(outgoing, timeout=5, metadata=metadata)


async def refresh_metrics(
    channel: grpc.aio.Channel, context: common_v1_context_pb2.RequestContext,
    metadata: tuple[tuple[str, str], ...],
) -> None:
    source = metrics_v1_dashboard_notification_service_pb2_grpc.DashboardNotificationServiceStub(channel)
    target = metrics_v1_dashboard_validation_service_pb2_grpc.DashboardValidationServiceStub(channel)
    request = metrics_v1_dashboard_notification_service_pb2.StreamDashboardNoticesRequest(context=context)
    stream = source.StreamDashboardNotices(request, timeout=30, metadata=metadata)
    async for change in stream:
        record = change.dashboard
        outgoing = metrics_v1_dashboard_validation_service_pb2.CheckDashboardEligibilityRequest(
            context=context,
            dashboard=metrics_v1_metrics_pb2.Dashboard(dashboard_id=record.dashboard_id, number=record.number),
            dashboard_id=record.dashboard_id
        )
        await target.CheckDashboardEligibility(outgoing, timeout=5, metadata=metadata)


async def refresh_modelregistry(
    channel: grpc.aio.Channel, context: common_v1_context_pb2.RequestContext,
    metadata: tuple[tuple[str, str], ...],
) -> None:
    source = modelregistry_v1_deployment_reporting_service_pb2_grpc.DeploymentReportingServiceStub(channel)
    target = modelregistry_v1_deployment_calculation_service_pb2_grpc.DeploymentCalculationServiceStub(channel)
    request = modelregistry_v1_deployment_reporting_service_pb2.StreamDeploymentMetricsRequest(context=context)
    stream = source.StreamDeploymentMetrics(request, timeout=30, metadata=metadata)
    async for change in stream:
        record = change.deployment
        outgoing = modelregistry_v1_deployment_calculation_service_pb2.CalculateDeploymentRequest(
            context=context,
            deployment=modelregistry_v1_modelregistry_pb2.Deployment(
                deployment_id=record.deployment_id,
                title=record.title
            ),
            deployment_id=record.deployment_id
        )
        await target.CalculateDeployment(outgoing, timeout=5, metadata=metadata)


async def refresh_pipelines(
    channel: grpc.aio.Channel, context: common_v1_context_pb2.RequestContext,
    metadata: tuple[tuple[str, str], ...],
) -> None:
    source = pipelines_v1_pipeline_reporting_service_pb2_grpc.PipelineReportingServiceStub(channel)
    target = pipelines_v1_pipeline_calculation_service_pb2_grpc.PipelineCalculationServiceStub(channel)
    request = pipelines_v1_pipeline_reporting_service_pb2.StreamPipelineMetricsRequest(context=context)
    stream = source.StreamPipelineMetrics(request, timeout=30, metadata=metadata)
    async for change in stream:
        record = change.pipeline
        outgoing = pipelines_v1_pipeline_calculation_service_pb2.CalculatePipelineRequest(
            context=context,
            pipeline=pipelines_v1_pipelines_pb2.Pipeline(pipeline_id=record.pipeline_id, title=record.title),
            pipeline_id=record.pipeline_id
        )
        await target.CalculatePipeline(outgoing, timeout=5, metadata=metadata)


async def run(mesh: str, tenant: str) -> None:
    context = common_v1_context_pb2.RequestContext(tenant_id=tenant)
    # The operator the job runs for acts in every call, as the servers downstream require.
    context.actor.user_id = os.environ['ACME_USER']
    metadata = (('authorization', 'Bearer ' + os.environ['ACME_TOKEN']),
                ('x-user-id', os.environ['ACME_USER']), ('x-tenant-id', tenant))
    async with grpc.aio.insecure_channel(mesh) as channel:
        await asyncio.gather(
            refresh_analytics(channel, context, metadata),
            refresh_datahub(channel, context, metadata),
            refresh_datasets(channel, context, metadata),
            refresh_featurestore(channel, context, metadata),
            refresh_labeling(channel, context, metadata),
            refresh_lineage(channel, context, metadata),
            refresh_metrics(channel, context, metadata),
            refresh_modelregistry(channel, context, metadata),
            refresh_pipelines(channel, context, metadata),
        )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mesh', default=os.environ.get('ACME_MESH', '127.0.0.1:15001'))
    parser.add_argument('--tenant', required=True)
    args = parser.parse_args()
    asyncio.run(run(args.mesh, args.tenant))


if __name__ == '__main__':
    main()
