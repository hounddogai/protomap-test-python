"""Application workflow for DataSchema Calculation."""

from __future__ import annotations

from functools import partial
from typing import Any
from typing import cast
import logging

from google.protobuf.any_pb2 import Any as AnyMessage
from google.protobuf.json_format import MessageToDict
from google.protobuf.json_format import MessageToJson
from google.protobuf.json_format import Parse
from google.protobuf.json_format import ParseDict

from acme.anomalies.v1 import anomalies_pb2 as anomalies_v1_anomalies_pb2
from acme.anomalies.v1 import anomaly_validation_service_pb2 as anomalies_v1_anomaly_validation_service_pb2
from acme.anomalies.v1 import refs_pb2 as anomalies_v1_refs_pb2
from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.customers.v1 import refs_pb2 as customers_v1_refs_pb2
from acme.datasets.v1 import data_schema_calculation_service_pb2 as datasets_v1_data_schema_calculation_service_pb2
from acme.datasets.v1 import dataset_validation_service_pb2 as datasets_v1_dataset_validation_service_pb2
from acme.datasets.v1 import (
    dataset_version_calculation_service_pb2 as datasets_v1_dataset_version_calculation_service_pb2,
)
from acme.datasets.v1 import (
    dataset_version_calculation_service_pb2_grpc as datasets_v1_dataset_version_calculation_service_pb2_grpc,
)
from acme.datasets.v1 import datasets_pb2 as datasets_v1_datasets_pb2
from acme.featurestore.v1 import (
    feature_value_validation_service_pb2 as featurestore_v1_feature_value_validation_service_pb2,
)
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.lineage.v1 import lineage_node_calculation_service_pb2 as lineage_v1_lineage_node_calculation_service_pb2
from acme.lineage.v1 import lineage_node_validation_service_pb2 as lineage_v1_lineage_node_validation_service_pb2
from acme.lineage.v1 import lineage_pb2 as lineage_v1_lineage_pb2
from acme.metrics.v1 import dashboard_export_service_pb2 as metrics_v1_dashboard_export_service_pb2
from acme.notifications.v1 import notification_service_pb2 as notifications_v1_notification_service_pb2
from acme.notifications.v1 import notifications_pb2 as notifications_v1_notifications_pb2
from acme.pipelines.v1 import pipeline_run_query_service_pb2 as pipelines_v1_pipeline_run_query_service_pb2
from acme.seating.v1 import seat_map_service_pb2 as seating_v1_seat_map_service_pb2
from acme.seating.v1 import seating_pb2 as seating_v1_seating_pb2
from acme.sponsorships.v1 import sponsor_service_pb2 as sponsorships_v1_sponsor_service_pb2

from acme_data.domains.datasets import hooks
from acme_data.domains.datasets.adapters import DataSchemaCalculationRecalculateDataSchemas0Adapter
from acme_data.domains.datasets.adapters import DataSchemaCalculationRecalculateDataSchemas0Port
from acme_data.domains.datasets.dependencies import Dependencies
from acme_data.domains.datasets.models import DataSchemaCalculationExplainDataSchemaCalculation2Command
from acme_data.domains.datasets.models import to_data_schema_calculation_explain_data_schema_calculation2_command
from acme_data.platform.rpc import run_steps
from acme_data.platform.tenancy import tenant_id
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class DataSchemaCalculationServicerWorkflow:
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    async def handle_calculate_data_schema(
        self,
        request: datasets_v1_data_schema_calculation_service_pb2.CalculateDataSchemaRequest
    ) -> datasets_v1_data_schema_calculation_service_pb2.CalculateDataSchemaResponse:
        """Calculates a data schema."""
        deps = self.deps
        response = datasets_v1_data_schema_calculation_service_pb2.CalculateDataSchemaResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CalculateDataSchema', extra={'fields': {'data_schema_id': request.data_schema.data_schema_id}})
            await deps.repository.audit(
                request.context.tenant_id,
                'CalculateDataSchema',
                {'data_schema_id': request.data_schema.data_schema_id}
            )
            await deps.repository.save_data_schema(request.context.tenant_id, request.data_schema)
            response_0 = seating_v1_seat_map_service_pb2.BatchGetSeatMapsResponse()
            response_1 = featurestore_v1_feature_value_validation_service_pb2.ValidateFeatureValueResponse()
            response_2 = metrics_v1_dashboard_export_service_pb2.ShareDashboardExportResponse()
            response_3 = sponsorships_v1_sponsor_service_pb2.CreateSponsorResponse()
            outgoing_0 = seating_v1_seat_map_service_pb2.BatchGetSeatMapsRequest(context=request.context)
            response_0 = cast(seating_v1_seat_map_service_pb2.BatchGetSeatMapsResponse, await deps.bus.request(
                'acme.datasets.v1.DataSchemaCalculationService/CalculateDataSchema/0', outgoing_0, deps.settings.timeout,
            ))
            outgoing_1 = featurestore_v1_feature_value_validation_service_pb2.ValidateFeatureValueRequest(
                context=request.context,
                details=featurestore_v1_feature_value_validation_service_pb2.ValidateFeatureValueRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(email=request.data_schema.manager.email)
                )
            )
            response_1 = await deps.clients.featurestore_feature_value_validation.ValidateFeatureValue(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = metrics_v1_dashboard_export_service_pb2.ShareDashboardExportRequest(
                context=request.context,
                details=metrics_v1_dashboard_export_service_pb2.ShareDashboardExportRequest.Details(
                    recipient=common_v1_contact_pb2.ContactInfo(email=request.data_schema.manager.email)
                ),
                reason=request.reason
            )
            method_name_2 = 'ShareDashboardExport'
            response_2 = await getattr(
                deps.clients.metrics_dashboard_export,
                method_name_2
            )(outgoing_2, timeout=deps.settings.timeout)
            fields_3: dict[str, Any] = {
                'context': request.context,
                'sponsor': {
                    'audit': {'updated_at': request.data_schema.audit.updated_at},
                    'relationship_manager': {'display_name': request.data_schema.manager.display_name}
                }
            }
            outgoing_3 = sponsorships_v1_sponsor_service_pb2.CreateSponsorRequest(**fields_3)
            response_3 = await deps.clients.sponsorships_sponsor.CreateSponsor(
                outgoing_3,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_0)
            returned_0_1 = response_0.result.details
            response.result.details.update(returned_0_1)
            returned_1_0 = response_1.feature_value.correlation_id
            if returned_1_0:
                response.result.correlation_id = returned_1_0
            returned_1_1 = response_1.outcome.status
            if returned_1_1:
                response.result.status = returned_1_1
            returned_2_0 = response_2.dashboard.total
            if returned_2_0.ListFields():
                response.breakdown.total.MergeFrom(returned_2_0)
            returned_3_0 = response_3.sponsor.primary_address.lines
            returned_3_0_part_1 = response.data_schema.children.add()
            returned_3_0_part_1.location.lines.extend(returned_3_0)
            returned_3_1 = response_3.result.status
            if returned_3_1:
                response.result.status = returned_3_1
            echoed_0 = request.data_schema_id
            response.data_schema.data_schema_id = echoed_0
            echoed_1 = request.data_schema.location
            response.data_schema.location.CopyFrom(echoed_1)
            return response

    async def handle_compare_data_schema_options(
        self,
        request: datasets_v1_data_schema_calculation_service_pb2.CompareDataSchemaOptionsRequest
    ) -> datasets_v1_data_schema_calculation_service_pb2.CompareDataSchemaOptionsResponse:
        """Compares a data schema."""
        deps = self.deps
        response = datasets_v1_data_schema_calculation_service_pb2.CompareDataSchemaOptionsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CompareDataSchemaOptions', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'CompareDataSchemaOptions',
                {'reason': request.reason}
            )
            await deps.repository.save_data_schema(request.context.tenant_id, request.data_schema)
            response_0 = datasets_v1_dataset_version_calculation_service_pb2.CalculateDatasetVersionResponse()
            outgoing_0 = datasets_v1_dataset_version_calculation_service_pb2.CalculateDatasetVersionRequest(
                context=request.context,
                dataset_version=datasets_v1_datasets_pb2.DatasetVersion(
                    subject=customers_v1_refs_pb2.CustomerRef(email=request.data_schema.manager.email)
                ),
                details=datasets_v1_dataset_version_calculation_service_pb2.CalculateDatasetVersionRequest.Details(
                    destination=common_v1_address_pb2.PostalAddress(
                        country_code=request.data_schema.location.country_code,
                        postal_code=request.details.destination.postal_code,
                        recipient=request.data_schema.location.recipient
                    )
                )
            )
            document_0 = MessageToDict(outgoing_0, preserving_proto_field_name=True)
            outgoing_0 = ParseDict(
                document_0,
                datasets_v1_dataset_version_calculation_service_pb2.CalculateDatasetVersionRequest()
            )
            response_0 = await deps.clients.datasets_dataset_version_calculation.CalculateDatasetVersion(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.dataset_version.subject.email
            returned_0_0_part_1 = response.data_schema.children.add()
            returned_0_0_part_2 = returned_0_0_part_1.children.add()
            if returned_0_0:
                returned_0_0_part_2.manager.email = returned_0_0
            echoed_0 = request.data_schema_id
            response.data_schema.data_schema_id = echoed_0
            echoed_1 = request.data_schema.manager
            response.data_schema.manager.CopyFrom(echoed_1)
            return response

    async def handle_estimate_data_schema(
        self,
        request: datasets_v1_data_schema_calculation_service_pb2.EstimateDataSchemaRequest
    ) -> datasets_v1_data_schema_calculation_service_pb2.EstimateDataSchemaResponse:
        """Estimates a data schema."""
        deps = self.deps
        response = datasets_v1_data_schema_calculation_service_pb2.EstimateDataSchemaResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('EstimateDataSchema', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'EstimateDataSchema', {'reason': request.reason})
            await deps.repository.save_data_schema(request.context.tenant_id, request.data_schema)
            response_0 = lineage_v1_lineage_node_calculation_service_pb2.RecalculateLineageNodesResponse()
            response_1 = datasets_v1_dataset_validation_service_pb2.CheckDatasetEligibilityResponse()
            outgoing_0 = lineage_v1_lineage_node_calculation_service_pb2.RecalculateLineageNodesRequest(
                context=request.context,
                lineage_node=lineage_v1_lineage_pb2.LineageNode(
                    children=[
                        lineage_v1_lineage_pb2.LineageNode(
                            children=[
                                lineage_v1_lineage_pb2.LineageNode(
                                    location=common_v1_address_pb2.PostalAddress(
                                        country_code=request.details.destination.country_code
                                    )
                                )
                            ]
                        )
                    ]
                )
            )
            document_0 = MessageToJson(outgoing_0, preserving_proto_field_name=True)
            outgoing_0 = Parse(
                document_0,
                lineage_v1_lineage_node_calculation_service_pb2.RecalculateLineageNodesRequest()
            )
            response_0 = await deps.clients.lineage_lineage_node_calculation.RecalculateLineageNodes(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = datasets_v1_dataset_validation_service_pb2.CheckDatasetEligibilityRequest()
            outgoing_1.context.CopyFrom(request.context)
            outgoing_1.dataset.address.postal_code = request.details.destination.postal_code
            outgoing_1.dataset.audit.created_at.CopyFrom(request.data_schema.audit.created_at)
            outgoing_1.dataset.address.locality = request.details.destination.locality
            outgoing_1.dataset.address.lines.extend(list(response_0.lineage_node.location.lines))
            merged_1 = datasets_v1_dataset_validation_service_pb2.CheckDatasetEligibilityRequest()
            merged_1.MergeFrom(outgoing_1)
            outgoing_1.CopyFrom(merged_1)
            response_1 = await deps.clients.datasets_dataset_validation.CheckDatasetEligibility(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.lineage_node.audit.created_by
            if returned_0_0:
                response.data_schema.audit.created_by = returned_0_0
            returned_0_1 = response_0.lineage_node.parent_id
            returned_0_1_part_1 = response.data_schema.children.add()
            returned_0_1_part_2 = returned_0_1_part_1.children.add()
            if returned_0_1:
                returned_0_1_part_2.parent_id = returned_0_1
            returned_1_0 = response_1.dataset.name
            returned_1_0_part_1 = response.data_schema.children.add()
            if returned_1_0:
                returned_1_0_part_1.name = returned_1_0
            returned_1_1 = response_1.dataset.audit.updated_by
            returned_1_1_part_1 = response.data_schema.children.add()
            if returned_1_1:
                returned_1_1_part_1.audit.updated_by = returned_1_1
            echoed_0 = request.data_schema_id
            response.data_schema.data_schema_id = echoed_0
            echoed_1 = request.data_schema.manager
            response.data_schema.manager.CopyFrom(echoed_1)
            return response

    async def handle_explain_data_schema_calculation(
        self,
        request: datasets_v1_data_schema_calculation_service_pb2.ExplainDataSchemaCalculationRequest
    ) -> datasets_v1_data_schema_calculation_service_pb2.ExplainDataSchemaCalculationResponse:
        """Explains a data schema."""
        deps = self.deps
        response = datasets_v1_data_schema_calculation_service_pb2.ExplainDataSchemaCalculationResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ExplainDataSchemaCalculation', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ExplainDataSchemaCalculation',
                {'reason': request.reason}
            )
            await deps.repository.save_data_schema(request.context.tenant_id, request.data_schema)
            response_0 = notifications_v1_notification_service_pb2.CreateNotificationResponse()
            response_1 = datasets_v1_dataset_version_calculation_service_pb2.EstimateDatasetVersionResponse()
            response_2 = lineage_v1_lineage_node_validation_service_pb2.ValidateLineageNodeResponse()
            outgoing_0 = notifications_v1_notification_service_pb2.CreateNotificationRequest(
                context=request.context,
                notification=notifications_v1_notifications_pb2.Notification(
                    assignee=identity_v1_refs_pb2.UserRef(email=request.details.contact.email),
                    audit=common_v1_audit_pb2.AuditInfo(updated_by=request.data_schema.audit.updated_by),
                    comments=[
                        notifications_v1_notifications_pb2.NotificationComment(
                            created_at=request.data_schema.audit.created_at
                        )
                    ]
                )
            )
            envelope_0 = AnyMessage()
            envelope_0.Pack(outgoing_0)
            outgoing_0 = notifications_v1_notification_service_pb2.CreateNotificationRequest()
            if not envelope_0.Unpack(outgoing_0):
                raise ValueError("partner envelope contains the wrong request type")
            response_0 = await deps.clients.notifications_notification.CreateNotification(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = datasets_v1_dataset_version_calculation_service_pb2.EstimateDatasetVersionRequest(
                context=request.context,
                dataset_version=datasets_v1_datasets_pb2.DatasetVersion(
                    subject=customers_v1_refs_pb2.CustomerRef(
                        display_name=response_0.notification.assignee.display_name,
                        email=request.details.contact.email
                    )
                ),
                details=datasets_v1_dataset_version_calculation_service_pb2.EstimateDatasetVersionRequest.Details(
                    destination=common_v1_address_pb2.PostalAddress(
                        lines=list(request.data_schema.location.lines),
                        region=request.data_schema.location.region
                    )
                )
            )
            registered_1 = cast(
                datasets_v1_dataset_version_calculation_service_pb2_grpc.DatasetVersionCalculationServiceStub,
                deps.clients.registry['acme.datasets.v1.DatasetVersionCalculationService']
            )
            response_1 = await registered_1.EstimateDatasetVersion(outgoing_1, timeout=deps.settings.timeout)
            command_2 = DataSchemaCalculationExplainDataSchemaCalculation2Command(
                context=request.context,
                lineage_node_children_children_manager_display_name=response_1.dataset_version.subject.display_name,
                lineage_node_children_children_location_postal_code=request.data_schema.location.postal_code
            )
            outgoing_2 = to_data_schema_calculation_explain_data_schema_calculation2_command(command_2)
            response_2 = await deps.clients.lineage_lineage_node_validation.ValidateLineageNode(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.notification.assignee.email
            if returned_0_0:
                response.data_schema.manager.email = returned_0_0
            returned_1_0 = response_1.dataset_version.subject.display_name
            if returned_1_0:
                response.data_schema.manager.display_name = returned_1_0
            returned_1_1 = response_1.dataset_version.attributes
            returned_1_1_part_1 = response.data_schema.children.add()
            returned_1_1_part_2 = returned_1_1_part_1.children.add()
            returned_1_1_part_2.attributes.update(returned_1_1)
            returned_2_0 = response_2.lineage_node.name
            returned_2_0_part_1 = response.data_schema.children.add()
            if returned_2_0:
                returned_2_0_part_1.name = returned_2_0
            returned_2_1 = response_2.lineage_node.location.lines
            returned_2_1_part_1 = response.data_schema.children.add()
            returned_2_1_part_1.location.lines.extend(returned_2_1)
            echoed_0 = request.data_schema_id
            response.data_schema.data_schema_id = echoed_0
            echoed_1 = request.data_schema.status
            response.data_schema.status = echoed_1
            return response

    async def handle_get_data_schema_rates(
        self,
        request: datasets_v1_data_schema_calculation_service_pb2.GetDataSchemaRatesRequest
    ) -> datasets_v1_data_schema_calculation_service_pb2.GetDataSchemaRatesResponse:
        """Returns a data schema."""
        deps = self.deps
        response = datasets_v1_data_schema_calculation_service_pb2.GetDataSchemaRatesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('GetDataSchemaRates', extra={'fields': {'domain': 'datasets'}})
            await deps.repository.audit(request.context.tenant_id, 'GetDataSchemaRates', {})
            response_0 = datasets_v1_dataset_version_calculation_service_pb2.CalculateDatasetVersionResponse()
            outgoing_0 = datasets_v1_dataset_version_calculation_service_pb2.CalculateDatasetVersionRequest(
                context=request.context,
                dataset_version=datasets_v1_datasets_pb2.DatasetVersion(
                    subject=customers_v1_refs_pb2.CustomerRef(email=request.context.actor.email)
                )
            )
            response_0 = await deps.clients.datasets_dataset_version_calculation.CalculateDatasetVersion(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.dataset_version.subject.email
            if returned_0_0:
                response.data_schema.manager.email = returned_0_0
            echoed_0 = request.data_schema_id
            response.data_schema.data_schema_id = echoed_0
            return response

    async def handle_quote_data_schema(
        self,
        request: datasets_v1_data_schema_calculation_service_pb2.QuoteDataSchemaRequest
    ) -> datasets_v1_data_schema_calculation_service_pb2.QuoteDataSchemaResponse:
        """Quotes a data schema."""
        deps = self.deps
        response = datasets_v1_data_schema_calculation_service_pb2.QuoteDataSchemaResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('QuoteDataSchema', extra={'fields': {'data_schema_id': request.data_schema.data_schema_id}})
            await deps.repository.audit(
                request.context.tenant_id,
                'QuoteDataSchema',
                {'data_schema_id': request.data_schema.data_schema_id}
            )
            await deps.repository.save_data_schema(request.context.tenant_id, request.data_schema)
            response_0 = seating_v1_seat_map_service_pb2.CloneSeatMapResponse()
            response_1 = anomalies_v1_anomaly_validation_service_pb2.CheckAnomalyEligibilityResponse()
            response_2 = pipelines_v1_pipeline_run_query_service_pb2.SummarizePipelineRunsResponse()
            outgoing_0 = seating_v1_seat_map_service_pb2.CloneSeatMapRequest(
                context=request.context,
                seat_map=seating_v1_seating_pb2.SeatMap(
                    children=[
                        seating_v1_seating_pb2.SeatMap(
                            children=[
                                seating_v1_seating_pb2.SeatMap(
                                    manager=identity_v1_refs_pb2.UserRef(
                                        display_name=request.data_schema.manager.display_name,
                                        email=request.data_schema.manager.email
                                    )
                                )
                            ]
                        )
                    ]
                )
            )
            send_0 = partial(deps.clients.seating_seat_map.CloneSeatMap, timeout=deps.settings.timeout)
            response_0 = await send_0(outgoing_0)
            outgoing_1 = anomalies_v1_anomaly_validation_service_pb2.CheckAnomalyEligibilityRequest(
                anomaly=anomalies_v1_anomalies_pb2.Anomaly(
                    assignee=identity_v1_refs_pb2.UserRef(email=request.data_schema.manager.email),
                    audit=common_v1_audit_pb2.AuditInfo(created_at=request.data_schema.audit.created_at),
                    customer=anomalies_v1_refs_pb2.DetectorRef(display_name=response_0.seat_map.manager.display_name)
                ),
                context=request.context
            )
            response_1 = await hooks.data_schema_calculation_quote_data_schema1(
                deps.clients.anomalies_anomaly_validation,
                outgoing_1,
                deps.settings.timeout
            )
            outgoing_2 = pipelines_v1_pipeline_run_query_service_pb2.SummarizePipelineRunsRequest()
            outgoing_2.context.CopyFrom(request.context)
            outgoing_2.annotations.update(dict(request.annotations))
            outgoing_2.reason = request.reason
            outgoing_2.context.tenant_id = tenant_id.get()
            response_2 = await deps.clients.pipelines_pipeline_run_query.SummarizePipelineRuns(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.seat_map.manager.display_name
            returned_0_0_part_1 = response.data_schema.children.add()
            returned_0_0_part_2 = returned_0_0_part_1.children.add()
            if returned_0_0:
                returned_0_0_part_2.manager.display_name = returned_0_0
            returned_1_0 = response_1.anomaly.audit.created_at
            returned_1_0_part_1 = response.data_schema.children.add()
            returned_1_0_part_2 = returned_1_0_part_1.children.add()
            if returned_1_0.ListFields():
                returned_1_0_part_2.audit.created_at.MergeFrom(returned_1_0)
            returned_1_1 = response_1.anomaly.assignee.display_name
            if returned_1_1:
                response.data_schema.manager.display_name = returned_1_1
            returned_2_0 = response_2.result.details
            response.result.details.update(returned_2_0)
            returned_2_1 = response_2.result.reference_ids
            response.result.reference_ids.extend(returned_2_1)
            echoed_0 = request.data_schema_id
            response.data_schema.data_schema_id = echoed_0
            echoed_1 = request.data_schema.name
            response.data_schema.name = echoed_1
            return response

    async def handle_recalculate_data_schemas(
        self,
        request: datasets_v1_data_schema_calculation_service_pb2.RecalculateDataSchemasRequest
    ) -> datasets_v1_data_schema_calculation_service_pb2.RecalculateDataSchemasResponse:
        """Recalculates a data schema."""
        deps = self.deps
        response = datasets_v1_data_schema_calculation_service_pb2.RecalculateDataSchemasResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('RecalculateDataSchemas', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'RecalculateDataSchemas', {'reason': request.reason})
            await deps.repository.save_data_schema(request.context.tenant_id, request.data_schema)
            response_0 = datasets_v1_dataset_version_calculation_service_pb2.QuoteDatasetVersionResponse()
            response_1 = datasets_v1_dataset_version_calculation_service_pb2.CalculateDatasetVersionResponse()
            outgoing_0 = datasets_v1_dataset_version_calculation_service_pb2.QuoteDatasetVersionRequest(
                context=request.context,
                dataset_version=datasets_v1_datasets_pb2.DatasetVersion(
                    subject=customers_v1_refs_pb2.CustomerRef(email=request.data_schema.manager.email)
                ),
                details=datasets_v1_dataset_version_calculation_service_pb2.QuoteDatasetVersionRequest.Details(
                    destination=common_v1_address_pb2.PostalAddress(
                        country_code=request.data_schema.location.country_code,
                        locality=request.details.destination.locality,
                        postal_code=request.data_schema.location.postal_code
                    )
                )
            )
            port_0: DataSchemaCalculationRecalculateDataSchemas0Port = DataSchemaCalculationRecalculateDataSchemas0Adapter(
                deps.clients.datasets_dataset_version_calculation,
                deps.settings.timeout
            )
            response_0 = await port_0.execute(outgoing_0)
            outgoing_1 = datasets_v1_dataset_version_calculation_service_pb2.CalculateDatasetVersionRequest(
                context=request.context,
                dataset_version=datasets_v1_datasets_pb2.DatasetVersion(
                    subject=customers_v1_refs_pb2.CustomerRef(email=response_0.dataset_version.subject.email)
                ),
                details=datasets_v1_dataset_version_calculation_service_pb2.CalculateDatasetVersionRequest.Details(
                    destination=common_v1_address_pb2.PostalAddress(
                        country_code=request.details.destination.country_code,
                        postal_code=request.data_schema.location.postal_code
                    )
                )
            )
            steps_1 = [
                partial(
                    deps.clients.datasets_dataset_version_calculation.CalculateDatasetVersion,
                    outgoing_1,
                    timeout=deps.settings.timeout
                )
            ]
            results_1 = await run_steps(steps_1)
            response_1 = results_1[-1]
            returned_0_0 = response_0.dataset_version.subject.email
            if returned_0_0:
                response.data_schema.manager.email = returned_0_0
            returned_0_1 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_1)
            returned_1_0 = response_1.dataset_version.attributes
            response.data_schema.attributes.update(returned_1_0)
            returned_1_1 = response_1.result.reference_ids
            response.result.reference_ids.extend(returned_1_1)
            echoed_0 = request.data_schema_id
            response.data_schema.data_schema_id = echoed_0
            echoed_1 = request.details.currency_code
            response.breakdown.currency_code = echoed_1
            return response
