"""Inspect domain records or invoke an operator-supplied protobuf method path."""

from __future__ import annotations

import argparse
import asyncio
import os

from google.protobuf.json_format import MessageToJson
import grpc

from acme.analytics.v1 import analytics_event_query_service_pb2 as analytics_v1_analytics_event_query_service_pb2
from acme.analytics.v1 import (
    analytics_event_query_service_pb2_grpc as analytics_v1_analytics_event_query_service_pb2_grpc,
)
from acme.anomalies.v1 import anomaly_approval_service_pb2 as anomalies_v1_anomaly_approval_service_pb2
from acme.anomalies.v1 import anomaly_approval_service_pb2_grpc as anomalies_v1_anomaly_approval_service_pb2_grpc
from acme.common.v1 import context_pb2 as common_v1_context_pb2
from acme.datahub.v1 import data_share_notification_service_pb2 as datahub_v1_data_share_notification_service_pb2
from acme.datahub.v1 import (
    data_share_notification_service_pb2_grpc as datahub_v1_data_share_notification_service_pb2_grpc,
)
from acme.datasets.v1 import data_schema_approval_service_pb2 as datasets_v1_data_schema_approval_service_pb2
from acme.datasets.v1 import data_schema_approval_service_pb2_grpc as datasets_v1_data_schema_approval_service_pb2_grpc
from acme.featurestore.v1 import entity_calculation_service_pb2 as featurestore_v1_entity_calculation_service_pb2
from acme.featurestore.v1 import (
    entity_calculation_service_pb2_grpc as featurestore_v1_entity_calculation_service_pb2_grpc,
)
from acme.forecasting.v1 import demand_forecast_query_service_pb2 as forecasting_v1_demand_forecast_query_service_pb2
from acme.forecasting.v1 import (
    demand_forecast_query_service_pb2_grpc as forecasting_v1_demand_forecast_query_service_pb2_grpc,
)
from acme.labeling.v1 import annotation_approval_service_pb2 as labeling_v1_annotation_approval_service_pb2
from acme.labeling.v1 import annotation_approval_service_pb2_grpc as labeling_v1_annotation_approval_service_pb2_grpc
from acme.lineage.v1 import impact_approval_service_pb2 as lineage_v1_impact_approval_service_pb2
from acme.lineage.v1 import impact_approval_service_pb2_grpc as lineage_v1_impact_approval_service_pb2_grpc
from acme.metrics.v1 import dashboard_admin_service_pb2 as metrics_v1_dashboard_admin_service_pb2
from acme.metrics.v1 import dashboard_admin_service_pb2_grpc as metrics_v1_dashboard_admin_service_pb2_grpc
from acme.modelregistry.v1 import deployment_approval_service_pb2 as modelregistry_v1_deployment_approval_service_pb2
from acme.modelregistry.v1 import (
    deployment_approval_service_pb2_grpc as modelregistry_v1_deployment_approval_service_pb2_grpc,
)
from acme.pipelines.v1 import pipeline_approval_service_pb2 as pipelines_v1_pipeline_approval_service_pb2
from acme.pipelines.v1 import pipeline_approval_service_pb2_grpc as pipelines_v1_pipeline_approval_service_pb2_grpc
from acme.recommendations.v1 import (
    interaction_approval_service_pb2 as recommendations_v1_interaction_approval_service_pb2,
)
from acme.recommendations.v1 import (
    interaction_approval_service_pb2_grpc as recommendations_v1_interaction_approval_service_pb2_grpc,
)


async def run(mesh: str, tenant: str, command: str, record_id: str, method_path: str, body: str) -> None:
    context = common_v1_context_pb2.RequestContext(tenant_id=tenant)
    context.actor.user_id = os.environ['ACME_USER']
    metadata = (('authorization', 'Bearer ' + os.environ['ACME_TOKEN']),
                ('x-user-id', os.environ['ACME_USER']), ('x-tenant-id', tenant))
    async with grpc.aio.insecure_channel(mesh) as channel:
        match command:
            case 'get-analytics':
                client = analytics_v1_analytics_event_query_service_pb2_grpc.AnalyticsEventQueryServiceStub(channel)
                request = analytics_v1_analytics_event_query_service_pb2.LookupAnalyticsEventRequest(
                    context=context,
                    analytics_event_id=record_id
                )
                response = await client.LookupAnalyticsEvent(request, timeout=10, metadata=metadata)
                print(MessageToJson(response, preserving_proto_field_name=True))
            case 'get-anomalies':
                client = anomalies_v1_anomaly_approval_service_pb2_grpc.AnomalyApprovalServiceStub(channel)
                request = anomalies_v1_anomaly_approval_service_pb2.GetAnomalyApprovalStatusRequest(
                    context=context,
                    anomaly_id=record_id
                )
                response = await client.GetAnomalyApprovalStatus(request, timeout=10, metadata=metadata)
                print(MessageToJson(response, preserving_proto_field_name=True))
            case 'get-datahub':
                client = datahub_v1_data_share_notification_service_pb2_grpc.DataShareNotificationServiceStub(channel)
                request = datahub_v1_data_share_notification_service_pb2.GetDataSharePreferencesRequest(
                    context=context,
                    data_share_id=record_id
                )
                response = await client.GetDataSharePreferences(request, timeout=10, metadata=metadata)
                print(MessageToJson(response, preserving_proto_field_name=True))
            case 'get-datasets':
                client = datasets_v1_data_schema_approval_service_pb2_grpc.DataSchemaApprovalServiceStub(channel)
                request = datasets_v1_data_schema_approval_service_pb2.GetDataSchemaApprovalStatusRequest(
                    context=context,
                    data_schema_id=record_id
                )
                response = await client.GetDataSchemaApprovalStatus(request, timeout=10, metadata=metadata)
                print(MessageToJson(response, preserving_proto_field_name=True))
            case 'get-featurestore':
                client = featurestore_v1_entity_calculation_service_pb2_grpc.EntityCalculationServiceStub(channel)
                request = featurestore_v1_entity_calculation_service_pb2.GetEntityRatesRequest(
                    context=context,
                    entity_id=record_id
                )
                response = await client.GetEntityRates(request, timeout=10, metadata=metadata)
                print(MessageToJson(response, preserving_proto_field_name=True))
            case 'get-forecasting':
                client = forecasting_v1_demand_forecast_query_service_pb2_grpc.DemandForecastQueryServiceStub(channel)
                request = forecasting_v1_demand_forecast_query_service_pb2.LookupDemandForecastRequest(
                    context=context,
                    demand_forecast_id=record_id
                )
                response = await client.LookupDemandForecast(request, timeout=10, metadata=metadata)
                print(MessageToJson(response, preserving_proto_field_name=True))
            case 'get-labeling':
                client = labeling_v1_annotation_approval_service_pb2_grpc.AnnotationApprovalServiceStub(channel)
                request = labeling_v1_annotation_approval_service_pb2.GetAnnotationApprovalStatusRequest(
                    context=context,
                    annotation_id=record_id
                )
                response = await client.GetAnnotationApprovalStatus(request, timeout=10, metadata=metadata)
                print(MessageToJson(response, preserving_proto_field_name=True))
            case 'get-lineage':
                client = lineage_v1_impact_approval_service_pb2_grpc.ImpactApprovalServiceStub(channel)
                request = lineage_v1_impact_approval_service_pb2.GetImpactApprovalStatusRequest(
                    context=context,
                    impact_id=record_id
                )
                response = await client.GetImpactApprovalStatus(request, timeout=10, metadata=metadata)
                print(MessageToJson(response, preserving_proto_field_name=True))
            case 'get-metrics':
                client = metrics_v1_dashboard_admin_service_pb2_grpc.DashboardAdminServiceStub(channel)
                request = metrics_v1_dashboard_admin_service_pb2.InspectDashboardRequest(
                    context=context,
                    dashboard_id=record_id
                )
                response = await client.InspectDashboard(request, timeout=10, metadata=metadata)
                print(MessageToJson(response, preserving_proto_field_name=True))
            case 'get-modelregistry':
                client = modelregistry_v1_deployment_approval_service_pb2_grpc.DeploymentApprovalServiceStub(channel)
                request = modelregistry_v1_deployment_approval_service_pb2.GetDeploymentApprovalStatusRequest(
                    context=context,
                    deployment_id=record_id
                )
                response = await client.GetDeploymentApprovalStatus(request, timeout=10, metadata=metadata)
                print(MessageToJson(response, preserving_proto_field_name=True))
            case 'get-pipelines':
                client = pipelines_v1_pipeline_approval_service_pb2_grpc.PipelineApprovalServiceStub(channel)
                request = pipelines_v1_pipeline_approval_service_pb2.GetPipelineApprovalStatusRequest(
                    context=context,
                    pipeline_id=record_id
                )
                response = await client.GetPipelineApprovalStatus(request, timeout=10, metadata=metadata)
                print(MessageToJson(response, preserving_proto_field_name=True))
            case 'get-recommendations':
                client = recommendations_v1_interaction_approval_service_pb2_grpc.InteractionApprovalServiceStub(channel)
                request = recommendations_v1_interaction_approval_service_pb2.GetInteractionApprovalStatusRequest(
                    context=context,
                    interaction_id=record_id
                )
                response = await client.GetInteractionApprovalStatus(request, timeout=10, metadata=metadata)
                print(MessageToJson(response, preserving_proto_field_name=True))
            case 'invoke':
                # The operator supplies a method path and a protobuf body encoded as hexadecimal bytes.
                if not method_path.startswith('/acme.') or method_path.count('/') != 2:
                    raise ValueError('invoke requires a fully qualified /acme.package.Service/Method path')
                invoke = channel.unary_unary(method_path)
                payload = await invoke(bytes.fromhex(body), timeout=10, metadata=metadata)
                print(payload.hex())
            case _:
                raise ValueError(f'unknown command: {command}')


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mesh', default=os.environ.get('ACME_MESH', '127.0.0.1:15001'))
    parser.add_argument('--tenant', required=True)
    parser.add_argument('command')
    parser.add_argument('record_id', nargs='?', default='')
    parser.add_argument('--method', default='')
    parser.add_argument('--body', default='')
    args = parser.parse_args()
    asyncio.run(run(args.mesh, args.tenant, args.command, args.record_id, args.method, args.body))


if __name__ == '__main__':
    main()
