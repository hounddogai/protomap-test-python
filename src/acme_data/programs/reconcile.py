"""Reconcile each domain's records against its validation API."""

from __future__ import annotations

import argparse
import asyncio
import logging
import os

import grpc

from acme.analytics.v1 import analytics_event_approval_service_pb2 as analytics_v1_analytics_event_approval_service_pb2
from acme.analytics.v1 import (
    analytics_event_approval_service_pb2_grpc as analytics_v1_analytics_event_approval_service_pb2_grpc,
)
from acme.analytics.v1 import (
    analytics_event_validation_service_pb2 as analytics_v1_analytics_event_validation_service_pb2,
)
from acme.analytics.v1 import (
    analytics_event_validation_service_pb2_grpc as analytics_v1_analytics_event_validation_service_pb2_grpc,
)
from acme.analytics.v1 import analytics_pb2 as analytics_v1_analytics_pb2
from acme.anomalies.v1 import anomalies_pb2 as anomalies_v1_anomalies_pb2
from acme.anomalies.v1 import anomaly_approval_service_pb2 as anomalies_v1_anomaly_approval_service_pb2
from acme.anomalies.v1 import anomaly_approval_service_pb2_grpc as anomalies_v1_anomaly_approval_service_pb2_grpc
from acme.anomalies.v1 import anomaly_validation_service_pb2 as anomalies_v1_anomaly_validation_service_pb2
from acme.anomalies.v1 import anomaly_validation_service_pb2_grpc as anomalies_v1_anomaly_validation_service_pb2_grpc
from acme.common.v1 import context_pb2 as common_v1_context_pb2
from acme.datahub.v1 import data_share_approval_service_pb2 as datahub_v1_data_share_approval_service_pb2
from acme.datahub.v1 import data_share_approval_service_pb2_grpc as datahub_v1_data_share_approval_service_pb2_grpc
from acme.datahub.v1 import data_share_validation_service_pb2 as datahub_v1_data_share_validation_service_pb2
from acme.datahub.v1 import data_share_validation_service_pb2_grpc as datahub_v1_data_share_validation_service_pb2_grpc
from acme.datahub.v1 import datahub_pb2 as datahub_v1_datahub_pb2
from acme.datasets.v1 import data_schema_approval_service_pb2 as datasets_v1_data_schema_approval_service_pb2
from acme.datasets.v1 import data_schema_approval_service_pb2_grpc as datasets_v1_data_schema_approval_service_pb2_grpc
from acme.datasets.v1 import data_schema_calculation_service_pb2 as datasets_v1_data_schema_calculation_service_pb2
from acme.datasets.v1 import (
    data_schema_calculation_service_pb2_grpc as datasets_v1_data_schema_calculation_service_pb2_grpc,
)
from acme.datasets.v1 import datasets_pb2 as datasets_v1_datasets_pb2
from acme.featurestore.v1 import entity_approval_service_pb2 as featurestore_v1_entity_approval_service_pb2
from acme.featurestore.v1 import entity_approval_service_pb2_grpc as featurestore_v1_entity_approval_service_pb2_grpc
from acme.featurestore.v1 import entity_calculation_service_pb2 as featurestore_v1_entity_calculation_service_pb2
from acme.featurestore.v1 import (
    entity_calculation_service_pb2_grpc as featurestore_v1_entity_calculation_service_pb2_grpc,
)
from acme.featurestore.v1 import featurestore_pb2 as featurestore_v1_featurestore_pb2
from acme.forecasting.v1 import (
    demand_forecast_approval_service_pb2 as forecasting_v1_demand_forecast_approval_service_pb2,
)
from acme.forecasting.v1 import (
    demand_forecast_approval_service_pb2_grpc as forecasting_v1_demand_forecast_approval_service_pb2_grpc,
)
from acme.forecasting.v1 import (
    demand_forecast_validation_service_pb2 as forecasting_v1_demand_forecast_validation_service_pb2,
)
from acme.forecasting.v1 import (
    demand_forecast_validation_service_pb2_grpc as forecasting_v1_demand_forecast_validation_service_pb2_grpc,
)
from acme.forecasting.v1 import forecasting_pb2 as forecasting_v1_forecasting_pb2
from acme.labeling.v1 import annotation_approval_service_pb2 as labeling_v1_annotation_approval_service_pb2
from acme.labeling.v1 import annotation_approval_service_pb2_grpc as labeling_v1_annotation_approval_service_pb2_grpc
from acme.labeling.v1 import annotation_calculation_service_pb2 as labeling_v1_annotation_calculation_service_pb2
from acme.labeling.v1 import (
    annotation_calculation_service_pb2_grpc as labeling_v1_annotation_calculation_service_pb2_grpc,
)
from acme.labeling.v1 import labeling_pb2 as labeling_v1_labeling_pb2
from acme.lineage.v1 import impact_approval_service_pb2 as lineage_v1_impact_approval_service_pb2
from acme.lineage.v1 import impact_approval_service_pb2_grpc as lineage_v1_impact_approval_service_pb2_grpc
from acme.lineage.v1 import impact_calculation_service_pb2 as lineage_v1_impact_calculation_service_pb2
from acme.lineage.v1 import impact_calculation_service_pb2_grpc as lineage_v1_impact_calculation_service_pb2_grpc
from acme.lineage.v1 import lineage_pb2 as lineage_v1_lineage_pb2
from acme.metrics.v1 import dashboard_history_service_pb2 as metrics_v1_dashboard_history_service_pb2
from acme.metrics.v1 import dashboard_history_service_pb2_grpc as metrics_v1_dashboard_history_service_pb2_grpc
from acme.metrics.v1 import dashboard_validation_service_pb2 as metrics_v1_dashboard_validation_service_pb2
from acme.metrics.v1 import dashboard_validation_service_pb2_grpc as metrics_v1_dashboard_validation_service_pb2_grpc
from acme.metrics.v1 import metrics_pb2 as metrics_v1_metrics_pb2
from acme.modelregistry.v1 import deployment_approval_service_pb2 as modelregistry_v1_deployment_approval_service_pb2
from acme.modelregistry.v1 import (
    deployment_approval_service_pb2_grpc as modelregistry_v1_deployment_approval_service_pb2_grpc,
)
from acme.modelregistry.v1 import (
    deployment_calculation_service_pb2 as modelregistry_v1_deployment_calculation_service_pb2,
)
from acme.modelregistry.v1 import (
    deployment_calculation_service_pb2_grpc as modelregistry_v1_deployment_calculation_service_pb2_grpc,
)
from acme.modelregistry.v1 import modelregistry_pb2 as modelregistry_v1_modelregistry_pb2
from acme.pipelines.v1 import pipeline_approval_service_pb2 as pipelines_v1_pipeline_approval_service_pb2
from acme.pipelines.v1 import pipeline_approval_service_pb2_grpc as pipelines_v1_pipeline_approval_service_pb2_grpc
from acme.pipelines.v1 import pipeline_calculation_service_pb2 as pipelines_v1_pipeline_calculation_service_pb2
from acme.pipelines.v1 import (
    pipeline_calculation_service_pb2_grpc as pipelines_v1_pipeline_calculation_service_pb2_grpc,
)
from acme.pipelines.v1 import pipelines_pb2 as pipelines_v1_pipelines_pb2
from acme.recommendations.v1 import (
    interaction_approval_service_pb2 as recommendations_v1_interaction_approval_service_pb2,
)
from acme.recommendations.v1 import (
    interaction_approval_service_pb2_grpc as recommendations_v1_interaction_approval_service_pb2_grpc,
)
from acme.recommendations.v1 import (
    interaction_calculation_service_pb2 as recommendations_v1_interaction_calculation_service_pb2,
)
from acme.recommendations.v1 import (
    interaction_calculation_service_pb2_grpc as recommendations_v1_interaction_calculation_service_pb2_grpc,
)
from acme.recommendations.v1 import recommendations_pb2 as recommendations_v1_recommendations_pb2


async def refresh_analytics(
    channel: grpc.aio.Channel, context: common_v1_context_pb2.RequestContext,
    metadata: tuple[tuple[str, str], ...],
) -> None:
    source = analytics_v1_analytics_event_approval_service_pb2_grpc.AnalyticsEventApprovalServiceStub(channel)
    target = analytics_v1_analytics_event_validation_service_pb2_grpc.AnalyticsEventValidationServiceStub(channel)
    request = analytics_v1_analytics_event_approval_service_pb2.ListPendingAnalyticsEventsRequest(context=context)
    while True:
        page = await source.ListPendingAnalyticsEvents(request, timeout=30, metadata=metadata)
        for record in page.analytics_events:
            outgoing = analytics_v1_analytics_event_validation_service_pb2.ExplainAnalyticsEventDecisionRequest(
                analytics_event=analytics_v1_analytics_pb2.AnalyticsEvent(
                    analytics_event_id=record.analytics_event_id,
                    kind=record.kind
                ),
                analytics_event_id=record.analytics_event_id,
                context=context
            )
            await target.ExplainAnalyticsEventDecision(outgoing, timeout=5, metadata=metadata)
        token = page.page_info.next_page_token
        if not token:
            break
        request.page.page_token = token


async def refresh_anomalies(
    channel: grpc.aio.Channel, context: common_v1_context_pb2.RequestContext,
    metadata: tuple[tuple[str, str], ...],
) -> None:
    source = anomalies_v1_anomaly_approval_service_pb2_grpc.AnomalyApprovalServiceStub(channel)
    target = anomalies_v1_anomaly_validation_service_pb2_grpc.AnomalyValidationServiceStub(channel)
    request = anomalies_v1_anomaly_approval_service_pb2.ListPendingAnomaliesRequest(context=context)
    while True:
        page = await source.ListPendingAnomalies(request, timeout=30, metadata=metadata)
        for record in page.anomalies:
            outgoing = anomalies_v1_anomaly_validation_service_pb2.CheckAnomalyEligibilityRequest(
                anomaly=anomalies_v1_anomalies_pb2.Anomaly(anomaly_id=record.anomaly_id, subject=record.subject),
                anomaly_id=record.anomaly_id,
                context=context
            )
            await target.CheckAnomalyEligibility(outgoing, timeout=5, metadata=metadata)
        token = page.page_info.next_page_token
        if not token:
            break
        request.page.page_token = token


async def refresh_datahub(
    channel: grpc.aio.Channel, context: common_v1_context_pb2.RequestContext,
    metadata: tuple[tuple[str, str], ...],
) -> None:
    source = datahub_v1_data_share_approval_service_pb2_grpc.DataShareApprovalServiceStub(channel)
    target = datahub_v1_data_share_validation_service_pb2_grpc.DataShareValidationServiceStub(channel)
    request = datahub_v1_data_share_approval_service_pb2.ListPendingDataSharesRequest(context=context)
    while True:
        page = await source.ListPendingDataShares(request, timeout=30, metadata=metadata)
        for record in page.data_shares:
            outgoing = datahub_v1_data_share_validation_service_pb2.CheckDataShareEligibilityRequest(
                context=context,
                data_share=datahub_v1_datahub_pb2.DataShare(
                    data_share_id=record.data_share_id,
                    number=record.counterparty.number
                ),
                data_share_id=record.data_share_id
            )
            await target.CheckDataShareEligibility(outgoing, timeout=5, metadata=metadata)
        token = page.page_info.next_page_token
        if not token:
            break
        request.page.page_token = token


async def refresh_datasets(
    channel: grpc.aio.Channel, context: common_v1_context_pb2.RequestContext,
    metadata: tuple[tuple[str, str], ...],
) -> None:
    source = datasets_v1_data_schema_approval_service_pb2_grpc.DataSchemaApprovalServiceStub(channel)
    target = datasets_v1_data_schema_calculation_service_pb2_grpc.DataSchemaCalculationServiceStub(channel)
    request = datasets_v1_data_schema_approval_service_pb2.ListPendingDataSchemasRequest(context=context)
    while True:
        page = await source.ListPendingDataSchemas(request, timeout=30, metadata=metadata)
        for record in page.data_schemas:
            outgoing = datasets_v1_data_schema_calculation_service_pb2.CalculateDataSchemaRequest(
                context=context,
                data_schema=datasets_v1_datasets_pb2.DataSchema(data_schema_id=record.data_schema_id, name=record.name),
                data_schema_id=record.data_schema_id
            )
            await target.CalculateDataSchema(outgoing, timeout=5, metadata=metadata)
        token = page.page_info.next_page_token
        if not token:
            break
        request.page.page_token = token


async def refresh_featurestore(
    channel: grpc.aio.Channel, context: common_v1_context_pb2.RequestContext,
    metadata: tuple[tuple[str, str], ...],
) -> None:
    source = featurestore_v1_entity_approval_service_pb2_grpc.EntityApprovalServiceStub(channel)
    target = featurestore_v1_entity_calculation_service_pb2_grpc.EntityCalculationServiceStub(channel)
    request = featurestore_v1_entity_approval_service_pb2.ListPendingEntitiesRequest(context=context)
    while True:
        page = await source.ListPendingEntities(request, timeout=30, metadata=metadata)
        for record in page.entities:
            outgoing = featurestore_v1_entity_calculation_service_pb2.CalculateEntityRequest(
                context=context,
                entity=featurestore_v1_featurestore_pb2.Entity(entity_id=record.entity_id, name=record.contact.name),
                entity_id=record.entity_id
            )
            await target.CalculateEntity(outgoing, timeout=5, metadata=metadata)
        token = page.page_info.next_page_token
        if not token:
            break
        request.page.page_token = token


async def refresh_forecasting(
    channel: grpc.aio.Channel, context: common_v1_context_pb2.RequestContext,
    metadata: tuple[tuple[str, str], ...],
) -> None:
    source = forecasting_v1_demand_forecast_approval_service_pb2_grpc.DemandForecastApprovalServiceStub(channel)
    target = forecasting_v1_demand_forecast_validation_service_pb2_grpc.DemandForecastValidationServiceStub(channel)
    request = forecasting_v1_demand_forecast_approval_service_pb2.ListPendingDemandForecastsRequest(context=context)
    while True:
        page = await source.ListPendingDemandForecasts(request, timeout=30, metadata=metadata)
        for record in page.demand_forecasts:
            outgoing = forecasting_v1_demand_forecast_validation_service_pb2.CheckDemandForecastEligibilityRequest(
                context=context,
                demand_forecast=forecasting_v1_forecasting_pb2.DemandForecast(
                    demand_forecast_id=record.demand_forecast_id,
                    number=record.number
                ),
                demand_forecast_id=record.demand_forecast_id
            )
            await target.CheckDemandForecastEligibility(outgoing, timeout=5, metadata=metadata)
        token = page.page_info.next_page_token
        if not token:
            break
        request.page.page_token = token


async def refresh_labeling(
    channel: grpc.aio.Channel, context: common_v1_context_pb2.RequestContext,
    metadata: tuple[tuple[str, str], ...],
) -> None:
    source = labeling_v1_annotation_approval_service_pb2_grpc.AnnotationApprovalServiceStub(channel)
    target = labeling_v1_annotation_calculation_service_pb2_grpc.AnnotationCalculationServiceStub(channel)
    request = labeling_v1_annotation_approval_service_pb2.ListPendingAnnotationsRequest(context=context)
    while True:
        page = await source.ListPendingAnnotations(request, timeout=30, metadata=metadata)
        for record in page.annotations:
            outgoing = labeling_v1_annotation_calculation_service_pb2.CalculateAnnotationRequest(
                annotation=labeling_v1_labeling_pb2.Annotation(annotation_id=record.annotation_id, kind=record.kind),
                annotation_id=record.annotation_id,
                context=context
            )
            await target.CalculateAnnotation(outgoing, timeout=5, metadata=metadata)
        token = page.page_info.next_page_token
        if not token:
            break
        request.page.page_token = token


async def refresh_lineage(
    channel: grpc.aio.Channel, context: common_v1_context_pb2.RequestContext,
    metadata: tuple[tuple[str, str], ...],
) -> None:
    source = lineage_v1_impact_approval_service_pb2_grpc.ImpactApprovalServiceStub(channel)
    target = lineage_v1_impact_calculation_service_pb2_grpc.ImpactCalculationServiceStub(channel)
    request = lineage_v1_impact_approval_service_pb2.ListPendingImpactsRequest(context=context)
    while True:
        page = await source.ListPendingImpacts(request, timeout=30, metadata=metadata)
        for record in page.impacts:
            outgoing = lineage_v1_impact_calculation_service_pb2.CalculateImpactRequest(
                context=context,
                impact=lineage_v1_lineage_pb2.Impact(impact_id=record.impact_id, subject=record.subject),
                impact_id=record.impact_id
            )
            await target.CalculateImpact(outgoing, timeout=5, metadata=metadata)
        token = page.page_info.next_page_token
        if not token:
            break
        request.page.page_token = token


async def refresh_metrics(
    channel: grpc.aio.Channel, context: common_v1_context_pb2.RequestContext,
    metadata: tuple[tuple[str, str], ...],
) -> None:
    source = metrics_v1_dashboard_history_service_pb2_grpc.DashboardHistoryServiceStub(channel)
    target = metrics_v1_dashboard_validation_service_pb2_grpc.DashboardValidationServiceStub(channel)
    request = metrics_v1_dashboard_history_service_pb2.ListDashboardVersionsRequest(context=context)
    while True:
        page = await source.ListDashboardVersions(request, timeout=30, metadata=metadata)
        for record in page.dashboards:
            outgoing = metrics_v1_dashboard_validation_service_pb2.CheckDashboardEligibilityRequest(
                context=context,
                dashboard=metrics_v1_metrics_pb2.Dashboard(dashboard_id=record.dashboard_id, number=record.number),
                dashboard_id=record.dashboard_id
            )
            await target.CheckDashboardEligibility(outgoing, timeout=5, metadata=metadata)
        token = page.page_info.next_page_token
        if not token:
            break
        request.page.page_token = token


async def refresh_modelregistry(
    channel: grpc.aio.Channel, context: common_v1_context_pb2.RequestContext,
    metadata: tuple[tuple[str, str], ...],
) -> None:
    source = modelregistry_v1_deployment_approval_service_pb2_grpc.DeploymentApprovalServiceStub(channel)
    target = modelregistry_v1_deployment_calculation_service_pb2_grpc.DeploymentCalculationServiceStub(channel)
    request = modelregistry_v1_deployment_approval_service_pb2.ListPendingDeploymentsRequest(context=context)
    while True:
        page = await source.ListPendingDeployments(request, timeout=30, metadata=metadata)
        for record in page.deployments:
            outgoing = modelregistry_v1_deployment_calculation_service_pb2.CalculateDeploymentRequest(
                context=context,
                deployment=modelregistry_v1_modelregistry_pb2.Deployment(
                    deployment_id=record.deployment_id,
                    title=record.title
                ),
                deployment_id=record.deployment_id
            )
            await target.CalculateDeployment(outgoing, timeout=5, metadata=metadata)
        token = page.page_info.next_page_token
        if not token:
            break
        request.page.page_token = token


async def refresh_pipelines(
    channel: grpc.aio.Channel, context: common_v1_context_pb2.RequestContext,
    metadata: tuple[tuple[str, str], ...],
) -> None:
    source = pipelines_v1_pipeline_approval_service_pb2_grpc.PipelineApprovalServiceStub(channel)
    target = pipelines_v1_pipeline_calculation_service_pb2_grpc.PipelineCalculationServiceStub(channel)
    request = pipelines_v1_pipeline_approval_service_pb2.ListPendingPipelinesRequest(context=context)
    while True:
        page = await source.ListPendingPipelines(request, timeout=30, metadata=metadata)
        for record in page.pipelines:
            outgoing = pipelines_v1_pipeline_calculation_service_pb2.CalculatePipelineRequest(
                context=context,
                pipeline=pipelines_v1_pipelines_pb2.Pipeline(pipeline_id=record.pipeline_id, title=record.title),
                pipeline_id=record.pipeline_id
            )
            await target.CalculatePipeline(outgoing, timeout=5, metadata=metadata)
        token = page.page_info.next_page_token
        if not token:
            break
        request.page.page_token = token


async def refresh_recommendations(
    channel: grpc.aio.Channel, context: common_v1_context_pb2.RequestContext,
    metadata: tuple[tuple[str, str], ...],
) -> None:
    source = recommendations_v1_interaction_approval_service_pb2_grpc.InteractionApprovalServiceStub(channel)
    target = recommendations_v1_interaction_calculation_service_pb2_grpc.InteractionCalculationServiceStub(channel)
    request = recommendations_v1_interaction_approval_service_pb2.ListPendingInteractionsRequest(context=context)
    while True:
        page = await source.ListPendingInteractions(request, timeout=30, metadata=metadata)
        for record in page.interactions:
            outgoing = recommendations_v1_interaction_calculation_service_pb2.CalculateInteractionRequest(
                context=context,
                interaction=recommendations_v1_recommendations_pb2.Interaction(
                    interaction_id=record.interaction_id,
                    kind=record.kind
                ),
                interaction_id=record.interaction_id
            )
            await target.CalculateInteraction(outgoing, timeout=5, metadata=metadata)
        token = page.page_info.next_page_token
        if not token:
            break
        request.page.page_token = token


async def run(mesh: str, tenant: str) -> None:
    context = common_v1_context_pb2.RequestContext(tenant_id=tenant)
    # The operator the job runs for acts in every call, as the servers downstream require.
    context.actor.user_id = os.environ['ACME_USER']
    metadata = (('authorization', 'Bearer ' + os.environ['ACME_TOKEN']),
                ('x-user-id', os.environ['ACME_USER']), ('x-tenant-id', tenant))
    async with grpc.aio.insecure_channel(mesh) as channel:
        await asyncio.gather(
            refresh_analytics(channel, context, metadata),
            refresh_anomalies(channel, context, metadata),
            refresh_datahub(channel, context, metadata),
            refresh_datasets(channel, context, metadata),
            refresh_featurestore(channel, context, metadata),
            refresh_forecasting(channel, context, metadata),
            refresh_labeling(channel, context, metadata),
            refresh_lineage(channel, context, metadata),
            refresh_metrics(channel, context, metadata),
            refresh_modelregistry(channel, context, metadata),
            refresh_pipelines(channel, context, metadata),
            refresh_recommendations(channel, context, metadata),
        )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mesh', default=os.environ.get('ACME_MESH', '127.0.0.1:15001'))
    parser.add_argument('--tenant', required=True)
    args = parser.parse_args()
    asyncio.run(run(args.mesh, args.tenant))


if __name__ == '__main__':
    main()
