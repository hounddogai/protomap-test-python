"""Application workflow for Pipeline Calculation."""

from __future__ import annotations

from collections.abc import Awaitable
from collections.abc import Callable
from typing import cast
import asyncio
import logging

from acme.appointments.v1 import appointment_service_pb2 as appointments_v1_appointment_service_pb2
from acme.broadcasts.v1 import broadcast_service_pb2 as broadcasts_v1_broadcast_service_pb2
from acme.broadcasts.v1 import broadcast_service_pb2_grpc as broadcasts_v1_broadcast_service_pb2_grpc
from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.concessions.v1 import concession_stand_service_pb2 as concessions_v1_concession_stand_service_pb2
from acme.concessions.v1 import concessions_pb2 as concessions_v1_concessions_pb2
from acme.customers.v1 import refs_pb2 as customers_v1_refs_pb2
from acme.featurestore.v1 import (
    feature_view_calculation_service_pb2 as featurestore_v1_feature_view_calculation_service_pb2,
)
from acme.featurestore.v1 import (
    feature_view_validation_service_pb2 as featurestore_v1_feature_view_validation_service_pb2,
)
from acme.featurestore.v1 import featurestore_pb2 as featurestore_v1_featurestore_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.labeling.v1 import label_set_calculation_service_pb2 as labeling_v1_label_set_calculation_service_pb2
from acme.labeling.v1 import labeling_pb2 as labeling_v1_labeling_pb2
from acme.lineage.v1 import impact_validation_service_pb2 as lineage_v1_impact_validation_service_pb2
from acme.lineage.v1 import lineage_pb2 as lineage_v1_lineage_pb2
from acme.maintenance.v1 import maintenance_pb2 as maintenance_v1_maintenance_pb2
from acme.maintenance.v1 import work_order_calculation_service_pb2 as maintenance_v1_work_order_calculation_service_pb2
from acme.metrics.v1 import metric_alert_history_service_pb2 as metrics_v1_metric_alert_history_service_pb2
from acme.metrics.v1 import metric_alert_query_service_pb2 as metrics_v1_metric_alert_query_service_pb2
from acme.metrics.v1 import metric_series_export_service_pb2 as metrics_v1_metric_series_export_service_pb2
from acme.metrics.v1 import metric_series_service_pb2 as metrics_v1_metric_series_service_pb2
from acme.metrics.v1 import metrics_pb2 as metrics_v1_metrics_pb2
from acme.pipelines.v1 import pipeline_calculation_service_pb2 as pipelines_v1_pipeline_calculation_service_pb2
from acme.telematics.v1 import telemetry_reading_query_service_pb2 as telematics_v1_telemetry_reading_query_service_pb2
from acme.venues.v1 import venue_validation_service_pb2 as venues_v1_venue_validation_service_pb2
from acme.yards.v1 import yard_query_service_pb2 as yards_v1_yard_query_service_pb2

from acme_data.domains.pipelines import hooks
from acme_data.domains.pipelines.adapters import PipelineCalculationCalculatePipeline2Adapter
from acme_data.domains.pipelines.adapters import PipelineCalculationCalculatePipeline2Port
from acme_data.domains.pipelines.adapters import PipelineCalculationComparePipelineOptions0Adapter
from acme_data.domains.pipelines.dependencies import Dependencies
from acme_data.domains.pipelines.models import PipelineCalculationSimulatePipeline0Command
from acme_data.domains.pipelines.models import PipelineCalculationSimulatePipeline1Command
from acme_data.domains.pipelines.models import to_pipeline_calculation_simulate_pipeline0_command
from acme_data.domains.pipelines.models import to_pipeline_calculation_simulate_pipeline1_command
from acme_data.platform.rpc import async_messages
from acme_data.platform.tenancy import tenant_id
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class PipelineCalculationServicerWorkflow:
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    async def handle_calculate_pipeline(
        self,
        request: pipelines_v1_pipeline_calculation_service_pb2.CalculatePipelineRequest
    ) -> pipelines_v1_pipeline_calculation_service_pb2.CalculatePipelineResponse:
        """Calculates a pipeline."""
        deps = self.deps
        response = pipelines_v1_pipeline_calculation_service_pb2.CalculatePipelineResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CalculatePipeline', extra={'fields': {'currency_code': request.details.currency_code}})
            await deps.repository.audit(
                request.context.tenant_id,
                'CalculatePipeline',
                {'currency_code': request.details.currency_code}
            )
            await deps.repository.save_pipeline(request.context.tenant_id, request.pipeline)
            response_0 = concessions_v1_concession_stand_service_pb2.CreateConcessionStandResponse()
            response_1 = metrics_v1_metric_series_export_service_pb2.ScheduleMetricSeriesExportResponse()
            response_2 = telematics_v1_telemetry_reading_query_service_pb2.FindTelemetryReadingsResponse()
            response_3 = featurestore_v1_feature_view_calculation_service_pb2.RecalculateFeatureViewsResponse()
            outgoing_0 = concessions_v1_concession_stand_service_pb2.CreateConcessionStandRequest(
                concession_stand=concessions_v1_concessions_pb2.ConcessionStand(
                    address=common_v1_address_pb2.PostalAddress(
                        locality=request.pipeline.location.locality,
                        recipient=request.details.destination.recipient,
                        region=request.details.destination.region
                    ),
                    audit=common_v1_audit_pb2.AuditInfo(etag=request.pipeline.audit.etag)
                ),
                context=request.context
            )
            response_0 = await hooks.pipeline_calculation_calculate_pipeline0(
                deps.clients.concessions_concession_stand,
                outgoing_0,
                deps.settings.timeout
            )
            outgoing_1 = metrics_v1_metric_series_export_service_pb2.ScheduleMetricSeriesExportRequest()
            outgoing_1.context.CopyFrom(request.context)
            outgoing_1.reason = request.reason
            outgoing_1.context.tenant_id = tenant_id.get()
            response_1 = await deps.clients.metrics_metric_series_export.ScheduleMetricSeriesExport(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = telematics_v1_telemetry_reading_query_service_pb2.FindTelemetryReadingsRequest(
                context=request.context,
                filter=telematics_v1_telemetry_reading_query_service_pb2.FindTelemetryReadingsRequest.Filter(
                    created_after=request.pipeline.audit.updated_at,
                    region=request.pipeline.location.region
                )
            )
            port_2: PipelineCalculationCalculatePipeline2Port = PipelineCalculationCalculatePipeline2Adapter(
                deps.clients.telematics_telemetry_reading_query,
                deps.settings.timeout
            )
            response_2 = await port_2.execute(outgoing_2)
            requests_3: list[featurestore_v1_feature_view_calculation_service_pb2.RecalculateFeatureViewsRequest] = []
            for item_3 in request.pipeline.participants:
                outgoing_3 = featurestore_v1_feature_view_calculation_service_pb2.RecalculateFeatureViewsRequest(
                    context=request.context,
                    feature_view=featurestore_v1_featurestore_pb2.FeatureView(
                        owner=identity_v1_refs_pb2.UserRef(email=item_3.contact.email)
                    )
                )
                requests_3.append(outgoing_3)
            replies_3 = await asyncio.gather(*(
                deps.clients.featurestore_feature_view_calculation.RecalculateFeatureViews(
                    entry,
                    timeout=deps.settings.timeout
                ) for entry in requests_3
            ))
            if replies_3:
                response_3 = replies_3[-1]
            returned_0_0 = response_0.concession_stand.address.region
            if returned_0_0:
                response.pipeline.location.region = returned_0_0
            returned_1_0 = response_1.result.reference_ids
            response.result.reference_ids.extend(returned_1_0)
            returned_2_0 = response_2.result.details
            response.result.details.update(returned_2_0)
            echoed_0 = request.pipeline_id
            response.pipeline.pipeline_id = echoed_0
            echoed_1 = request.pipeline.metadata
            response.pipeline.metadata.update(echoed_1)
            return response

    async def handle_compare_pipeline_options(
        self,
        request: pipelines_v1_pipeline_calculation_service_pb2.ComparePipelineOptionsRequest
    ) -> pipelines_v1_pipeline_calculation_service_pb2.ComparePipelineOptionsResponse:
        """Compares a pipeline."""
        deps = self.deps
        response = pipelines_v1_pipeline_calculation_service_pb2.ComparePipelineOptionsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ComparePipelineOptions', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'ComparePipelineOptions', {'reason': request.reason})
            await deps.repository.save_pipeline(request.context.tenant_id, request.pipeline)
            response_0 = metrics_v1_metric_alert_query_service_pb2.ResolveMetricAlertsResponse()
            response_1 = metrics_v1_metric_series_service_pb2.CloneMetricSeriesResponse()
            outgoing_0 = metrics_v1_metric_alert_query_service_pb2.ResolveMetricAlertsRequest(context=request.context)
            response_0 = await PipelineCalculationComparePipelineOptions0Adapter(
                deps.clients.metrics_metric_alert_query,
                deps.settings.timeout
            )(outgoing_0)
            outgoing_1 = metrics_v1_metric_series_service_pb2.CloneMetricSeriesRequest(
                context=request.context,
                metric_series=metrics_v1_metrics_pb2.MetricSeries(
                    address=common_v1_address_pb2.PostalAddress(
                        lines=list(request.details.destination.lines),
                        recipient=request.pipeline.location.recipient
                    ),
                    owner=identity_v1_refs_pb2.UserRef(email=request.pipeline.organizer.email)
                )
            )
            response_1 = cast(metrics_v1_metric_series_service_pb2.CloneMetricSeriesResponse, await deps.bus.request(
                'acme.pipelines.v1.PipelineCalculationService/ComparePipelineOptions/1', outgoing_1, deps.settings.timeout,
            ))
            returned_0_0 = response_0.result.details
            response.result.details.update(returned_0_0)
            returned_1_0 = response_1.metric_series.audit.etag
            if returned_1_0:
                response.pipeline.audit.etag = returned_1_0
            echoed_0 = request.pipeline_id
            response.pipeline.pipeline_id = echoed_0
            echoed_1 = request.pipeline.status
            response.pipeline.status = echoed_1
            return response

    async def handle_estimate_pipeline(
        self,
        request: pipelines_v1_pipeline_calculation_service_pb2.EstimatePipelineRequest
    ) -> pipelines_v1_pipeline_calculation_service_pb2.EstimatePipelineResponse:
        """Estimates a pipeline."""
        deps = self.deps
        response = pipelines_v1_pipeline_calculation_service_pb2.EstimatePipelineResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('EstimatePipeline', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'EstimatePipeline', {'reason': request.reason})
            await deps.repository.save_pipeline(request.context.tenant_id, request.pipeline)
            response_0 = labeling_v1_label_set_calculation_service_pb2.CalculateLabelSetResponse()
            response_1 = lineage_v1_impact_validation_service_pb2.PreviewImpactResponse()
            response_2 = maintenance_v1_work_order_calculation_service_pb2.QuoteWorkOrderResponse()
            outgoing_0 = labeling_v1_label_set_calculation_service_pb2.CalculateLabelSetRequest(
                context=request.context,
                label_set=labeling_v1_labeling_pb2.LabelSet(
                    children=[
                        labeling_v1_labeling_pb2.LabelSet(
                            audit=common_v1_audit_pb2.AuditInfo(updated_at=request.pipeline.audit.updated_at),
                            children=[
                                labeling_v1_labeling_pb2.LabelSet(
                                    location=common_v1_address_pb2.PostalAddress(
                                        country_code=request.details.destination.country_code,
                                        postal_code=request.details.destination.postal_code
                                    ),
                                    manager=identity_v1_refs_pb2.UserRef(email=request.pipeline.organizer.email)
                                )
                            ]
                        )
                    ]
                )
            )
            response_0 = await deps.clients.labeling_label_set_calculation.CalculateLabelSet(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            callbacks_1: list[
                Callable[[], Awaitable[lineage_v1_impact_validation_service_pb2.PreviewImpactResponse]]
            ] = []
            for item_1 in request.pipeline.participants:
                outgoing_1 = lineage_v1_impact_validation_service_pb2.PreviewImpactRequest(
                    context=request.context,
                    details=lineage_v1_impact_validation_service_pb2.PreviewImpactRequest.Details(
                        contact=common_v1_contact_pb2.ContactInfo(name=item_1.contact.name)
                    ),
                    impact=lineage_v1_lineage_pb2.Impact(
                        customer=customers_v1_refs_pb2.CustomerRef(email=item_1.contact.email)
                    )
                )
                async def send_1(
                    payload: lineage_v1_impact_validation_service_pb2.PreviewImpactRequest = outgoing_1
                ) -> lineage_v1_impact_validation_service_pb2.PreviewImpactResponse:
                    return await deps.clients.lineage_impact_validation.PreviewImpact(
                        payload,
                        timeout=deps.settings.timeout
                    )
                callbacks_1.append(send_1)
            for callback_1 in callbacks_1:
                response_1 = await callback_1()
            async for item_2 in async_messages(request.pipeline.participants):
                outgoing_2 = maintenance_v1_work_order_calculation_service_pb2.QuoteWorkOrderRequest(
                    context=request.context,
                    work_order=maintenance_v1_maintenance_pb2.WorkOrder(
                        assignee=identity_v1_refs_pb2.UserRef(email=item_2.contact.email),
                        requester=common_v1_contact_pb2.ContactInfo(
                            name=item_2.contact.name,
                            phone=item_2.contact.phone,
                            preferred_channel=item_2.contact.preferred_channel
                        )
                    )
                )
                response_2 = await deps.clients.maintenance_work_order_calculation.QuoteWorkOrder(
                    outgoing_2,
                    timeout=deps.settings.timeout
                )
            returned_0_0 = response_0.label_set.manager.display_name
            if returned_0_0:
                response.pipeline.organizer.display_name = returned_0_0
            echoed_0 = request.pipeline_id
            response.pipeline.pipeline_id = echoed_0
            echoed_1 = request.details.currency_code
            response.breakdown.currency_code = echoed_1
            return response

    async def handle_explain_pipeline_calculation(
        self,
        request: pipelines_v1_pipeline_calculation_service_pb2.ExplainPipelineCalculationRequest
    ) -> pipelines_v1_pipeline_calculation_service_pb2.ExplainPipelineCalculationResponse:
        """Explains a pipeline."""
        deps = self.deps
        response = pipelines_v1_pipeline_calculation_service_pb2.ExplainPipelineCalculationResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ExplainPipelineCalculation', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ExplainPipelineCalculation',
                {'reason': request.reason}
            )
            await deps.repository.save_pipeline(request.context.tenant_id, request.pipeline)
            response_0 = yards_v1_yard_query_service_pb2.ExportYardsResponse()
            response_1 = metrics_v1_metric_alert_history_service_pb2.ListMetricAlertVersionsResponse()
            response_2 = featurestore_v1_feature_view_validation_service_pb2.ExplainFeatureViewDecisionResponse()
            outgoing_0 = yards_v1_yard_query_service_pb2.ExportYardsRequest(
                context=request.context,
                filter=yards_v1_yard_query_service_pb2.ExportYardsRequest.Filter(
                    created_after=request.pipeline.audit.created_at,
                    owner_id=request.pipeline.organizer.user_id,
                    region=request.pipeline.location.region
                )
            )
            async for chunk_0 in deps.clients.yards_yard_query.ExportYards(outgoing_0, timeout=deps.settings.timeout):
                response_0 = chunk_0
            for item_1 in request.pipeline.participants:
                outgoing_1 = metrics_v1_metric_alert_history_service_pb2.ListMetricAlertVersionsRequest(
                    context=request.context,
                    filter=metrics_v1_metric_alert_history_service_pb2.ListMetricAlertVersionsRequest.Filter(
                        owner_id=item_1.participant_id
                    )
                )
                response_1 = await deps.clients.metrics_metric_alert_history.ListMetricAlertVersions(
                    outgoing_1,
                    timeout=deps.settings.timeout
                )
            outgoing_2 = featurestore_v1_feature_view_validation_service_pb2.ExplainFeatureViewDecisionRequest()
            outgoing_2.context.CopyFrom(request.context)
            outgoing_2.details.contact.email = request.details.contact.email
            outgoing_2.feature_view.audit.updated_by = request.pipeline.audit.updated_by
            outgoing_2.feature_view.audit.created_at.CopyFrom(request.pipeline.audit.created_at)
            merged_2 = featurestore_v1_feature_view_validation_service_pb2.ExplainFeatureViewDecisionRequest()
            merged_2.MergeFrom(outgoing_2)
            outgoing_2.CopyFrom(merged_2)
            response_2 = await deps.clients.featurestore_feature_view_validation.ExplainFeatureViewDecision(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            returned_2_0 = response_2.result.status
            if returned_2_0:
                response.outcome.status = returned_2_0
            echoed_0 = request.pipeline_id
            response.pipeline.pipeline_id = echoed_0
            echoed_1 = request.pipeline.organizer
            response.pipeline.organizer.CopyFrom(echoed_1)
            return response

    async def handle_get_pipeline_rates(
        self,
        request: pipelines_v1_pipeline_calculation_service_pb2.GetPipelineRatesRequest
    ) -> pipelines_v1_pipeline_calculation_service_pb2.GetPipelineRatesResponse:
        """Returns a pipeline."""
        deps = self.deps
        response = pipelines_v1_pipeline_calculation_service_pb2.GetPipelineRatesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('GetPipelineRates', extra={'fields': {'domain': 'pipelines'}})
            await deps.repository.audit(request.context.tenant_id, 'GetPipelineRates', {})
            response_0 = featurestore_v1_feature_view_calculation_service_pb2.ExplainFeatureViewCalculationResponse()
            outgoing_0 = featurestore_v1_feature_view_calculation_service_pb2.ExplainFeatureViewCalculationRequest(
                context=request.context,
                details=featurestore_v1_feature_view_calculation_service_pb2.ExplainFeatureViewCalculationRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(email=request.context.actor.email)
                )
            )
            response_0 = await deps.clients.featurestore_feature_view_calculation.ExplainFeatureViewCalculation(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.outcome.message
            if returned_0_0:
                response.result.message = returned_0_0
            echoed_0 = request.pipeline_id
            response.pipeline.pipeline_id = echoed_0
            return response

    async def handle_recalculate_pipelines(
        self,
        request: pipelines_v1_pipeline_calculation_service_pb2.RecalculatePipelinesRequest
    ) -> pipelines_v1_pipeline_calculation_service_pb2.RecalculatePipelinesResponse:
        """Recalculates a pipeline."""
        deps = self.deps
        response = pipelines_v1_pipeline_calculation_service_pb2.RecalculatePipelinesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('RecalculatePipelines', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'RecalculatePipelines', {'reason': request.reason})
            await deps.repository.save_pipeline(request.context.tenant_id, request.pipeline)
            response_0 = broadcasts_v1_broadcast_service_pb2.SearchBroadcastsResponse()
            outgoing_0 = broadcasts_v1_broadcast_service_pb2.SearchBroadcastsRequest(
                context=request.context,
                filter=broadcasts_v1_broadcast_service_pb2.SearchBroadcastsRequest.Filter(
                    created_after=request.pipeline.audit.created_at,
                    labels=dict(request.pipeline.metadata),
                    owner_id=request.pipeline.organizer.user_id,
                    region=request.pipeline.location.region
                )
            )
            registered_0 = cast(
                broadcasts_v1_broadcast_service_pb2_grpc.BroadcastServiceStub,
                deps.clients.registry['acme.broadcasts.v1.BroadcastService']
            )
            response_0 = await registered_0.SearchBroadcasts(outgoing_0, timeout=deps.settings.timeout)
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.result.message = returned_0_0
            echoed_0 = request.pipeline_id
            response.pipeline.pipeline_id = echoed_0
            echoed_1 = request.pipeline.location
            response.pipeline.location.CopyFrom(echoed_1)
            return response

    async def handle_simulate_pipeline(
        self,
        request: pipelines_v1_pipeline_calculation_service_pb2.SimulatePipelineRequest
    ) -> pipelines_v1_pipeline_calculation_service_pb2.SimulatePipelineResponse:
        """Simulates a pipeline."""
        deps = self.deps
        response = pipelines_v1_pipeline_calculation_service_pb2.SimulatePipelineResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SimulatePipeline', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'SimulatePipeline', {'reason': request.reason})
            await deps.repository.save_pipeline(request.context.tenant_id, request.pipeline)
            response_0 = venues_v1_venue_validation_service_pb2.PreviewVenueResponse()
            response_1 = appointments_v1_appointment_service_pb2.BatchGetAppointmentsResponse()
            response_2 = labeling_v1_label_set_calculation_service_pb2.QuoteLabelSetResponse()
            response_3 = metrics_v1_metric_alert_history_service_pb2.AnnotateMetricAlertVersionResponse()
            command_0 = PipelineCalculationSimulatePipeline0Command(
                context=request.context,
                venue_owner_email=request.pipeline.organizer.email
            )
            outgoing_0 = to_pipeline_calculation_simulate_pipeline0_command(command_0)
            response_0 = await deps.clients.venues_venue_validation.PreviewVenue(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            command_1 = PipelineCalculationSimulatePipeline1Command.model_validate({'context': request.context})
            outgoing_1 = to_pipeline_calculation_simulate_pipeline1_command(command_1)
            response_1 = await deps.clients.appointments_appointment.BatchGetAppointments(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = labeling_v1_label_set_calculation_service_pb2.QuoteLabelSetRequest()
            outgoing_2.context.CopyFrom(request.context)
            field_2_1_part_1 = outgoing_2.label_set.children.add()
            field_2_1_part_2 = field_2_1_part_1.children.add()
            field_2_1_part_2.manager.user_id = response_0.venue.owner.user_id
            if response_0.venue.WhichOneof('locator') == 'address':
                field_2_2_part_1 = outgoing_2.label_set.children.add()
                field_2_2_part_2 = field_2_2_part_1.children.add()
                field_2_2_part_2.location.region = response_0.venue.address.region
            field_2_3_part_1 = outgoing_2.label_set.children.add()
            field_2_3_part_2 = field_2_3_part_1.children.add()
            field_2_3_part_2.location.postal_code = request.pipeline.location.postal_code
            field_2_4_part_1 = outgoing_2.label_set.children.add()
            field_2_4_part_2 = field_2_4_part_1.children.add()
            field_2_4_part_2.location.lines.extend(list(request.pipeline.location.lines))
            response_2 = await deps.clients.labeling_label_set_calculation.QuoteLabelSet(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            requests_3: list[metrics_v1_metric_alert_history_service_pb2.AnnotateMetricAlertVersionRequest] = []
            for item_3 in request.pipeline.participants:
                outgoing_3 = metrics_v1_metric_alert_history_service_pb2.AnnotateMetricAlertVersionRequest(
                    context=request.context,
                    metric_alert=metrics_v1_metrics_pb2.MetricAlert(
                        audit=common_v1_audit_pb2.AuditInfo(updated_by=response_0.venue.audit.updated_by),
                        owner=identity_v1_refs_pb2.UserRef(
                            display_name=response_0.venue.owner.display_name,
                            email=item_3.contact.email,
                            user_id=response_0.venue.owner.user_id
                        )
                    )
                )
                requests_3.append(outgoing_3)
            replies_3 = await asyncio.gather(*(
                deps.clients.metrics_metric_alert_history.AnnotateMetricAlertVersion(
                    entry,
                    timeout=deps.settings.timeout
                ) for entry in requests_3
            ))
            if replies_3:
                response_3 = replies_3[-1]
            returned_0_0 = response_0.result.correlation_id
            if returned_0_0:
                response.result.correlation_id = returned_0_0
            returned_0_1 = response_0.outcome.message
            if returned_0_1:
                response.result.message = returned_0_1
            returned_1_0 = response_1.result.details
            response.result.details.update(returned_1_0)
            returned_2_0 = response_2.label_set.audit.updated_by
            if returned_2_0:
                response.pipeline.audit.updated_by = returned_2_0
            returned_2_1 = response_2.label_set.location
            if returned_2_1.ListFields():
                response.pipeline.location.MergeFrom(returned_2_1)
            echoed_0 = request.pipeline_id
            response.pipeline.pipeline_id = echoed_0
            echoed_1 = request.pipeline.organizer
            response.pipeline.organizer.CopyFrom(echoed_1)
            return response
