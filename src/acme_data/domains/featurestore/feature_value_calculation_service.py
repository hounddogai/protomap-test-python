"""Computes the figures of a feature value, such as totals, taxes, and estimates."""

from __future__ import annotations

from collections.abc import AsyncIterator
from collections.abc import Awaitable
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any
import asyncio
import logging

from google.protobuf.json_format import MessageToDict
from google.protobuf.json_format import MessageToJson
from google.protobuf.json_format import Parse
from google.protobuf.json_format import ParseDict
import grpc

from acme.anomalies.v1 import anomalies_pb2 as anomalies_v1_anomalies_pb2
from acme.anomalies.v1 import (
    anomaly_feedback_validation_service_pb2 as anomalies_v1_anomaly_feedback_validation_service_pb2,
)
from acme.anomalies.v1 import anomaly_query_service_pb2 as anomalies_v1_anomaly_query_service_pb2
from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.featurestore.v1 import (
    feature_value_calculation_service_pb2 as featurestore_v1_feature_value_calculation_service_pb2,
)
from acme.featurestore.v1 import (
    feature_value_calculation_service_pb2_grpc as featurestore_v1_feature_value_calculation_service_pb2_grpc,
)
from acme.featurestore.v1 import (
    feature_view_calculation_service_pb2 as featurestore_v1_feature_view_calculation_service_pb2,
)
from acme.featurestore.v1 import featurestore_pb2 as featurestore_v1_featurestore_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.lineage.v1 import lineage_node_validation_service_pb2 as lineage_v1_lineage_node_validation_service_pb2
from acme.metrics.v1 import metric_alert_history_service_pb2 as metrics_v1_metric_alert_history_service_pb2
from acme.metrics.v1 import metric_series_history_service_pb2 as metrics_v1_metric_series_history_service_pb2
from acme.metrics.v1 import metrics_pb2 as metrics_v1_metrics_pb2
from acme.prescriptions.v1 import prescription_service_pb2 as prescriptions_v1_prescription_service_pb2
from acme.prescriptions.v1 import prescriptions_pb2 as prescriptions_v1_prescriptions_pb2

from acme_data.domains.featurestore import hooks
from acme_data.domains.featurestore.adapters import FeatureValueCalculationQuoteFeatureValue0Adapter
from acme_data.domains.featurestore.dependencies import Dependencies
from acme_data.domains.featurestore.models import FeatureValueCalculationCalculateFeatureValue0Command
from acme_data.domains.featurestore.models import to_feature_value_calculation_calculate_feature_value0_command
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_id
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


@dataclass(slots=True)
class FeatureValueCalculationServicer(
    featurestore_v1_feature_value_calculation_service_pb2_grpc.FeatureValueCalculationServiceServicer
):
    deps: Dependencies

    @rpc_errors
    async def CalculateFeatureValue(
        self, request: featurestore_v1_feature_value_calculation_service_pb2.CalculateFeatureValueRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_feature_value_calculation_service_pb2.CalculateFeatureValueResponse:
        """Calculates a feature value."""
        return await self.handle_calculate_feature_value(request)

    @rpc_errors
    async def EstimateFeatureValue(
        self, request: featurestore_v1_feature_value_calculation_service_pb2.EstimateFeatureValueRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_feature_value_calculation_service_pb2.EstimateFeatureValueResponse:
        """Estimates a feature value."""
        return await self.handle_estimate_feature_value(request)

    @rpc_errors
    async def ExplainFeatureValueCalculation(
        self, request: featurestore_v1_feature_value_calculation_service_pb2.ExplainFeatureValueCalculationRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_feature_value_calculation_service_pb2.ExplainFeatureValueCalculationResponse:
        """Explains a feature value."""
        return await self.handle_explain_feature_value_calculation(request)

    @rpc_errors
    @retry_transient
    async def GetFeatureValueRates(
        self, request: featurestore_v1_feature_value_calculation_service_pb2.GetFeatureValueRatesRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_feature_value_calculation_service_pb2.GetFeatureValueRatesResponse:
        """Returns a feature value."""
        return await self.handle_get_feature_value_rates(request)

    @rpc_errors
    async def QuoteFeatureValue(
        self, request: featurestore_v1_feature_value_calculation_service_pb2.QuoteFeatureValueRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_feature_value_calculation_service_pb2.QuoteFeatureValueResponse:
        """Quotes a feature value."""
        return await self.handle_quote_feature_value(request)

    @rpc_errors
    async def RecalculateFeatureValues(
        self, request: featurestore_v1_feature_value_calculation_service_pb2.RecalculateFeatureValuesRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_feature_value_calculation_service_pb2.RecalculateFeatureValuesResponse:
        """Recalculates a feature value."""
        return await self.handle_recalculate_feature_values(request)

    @rpc_errors
    async def SimulateFeatureValue(
        self, request: featurestore_v1_feature_value_calculation_service_pb2.SimulateFeatureValueRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_feature_value_calculation_service_pb2.SimulateFeatureValueResponse:
        """Simulates a feature value."""
        return await self.handle_simulate_feature_value(request)

    async def handle_calculate_feature_value(
        self,
        request: featurestore_v1_feature_value_calculation_service_pb2.CalculateFeatureValueRequest
    ) -> featurestore_v1_feature_value_calculation_service_pb2.CalculateFeatureValueResponse:
        """Calculates a feature value."""
        deps = self.deps
        response = featurestore_v1_feature_value_calculation_service_pb2.CalculateFeatureValueResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CalculateFeatureValue', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'CalculateFeatureValue', {'reason': request.reason})
            await deps.repository.save_feature_value(request.context.tenant_id, request.feature_value)
            response_0 = metrics_v1_metric_series_history_service_pb2.CompareMetricSeriesVersionsResponse()
            command_0 = FeatureValueCalculationCalculateFeatureValue0Command.model_validate(
                {'context': request.context, 'metric_series_address_locality': request.details.destination.locality}
            )
            outgoing_0 = to_feature_value_calculation_calculate_feature_value0_command(command_0)
            response_0 = await deps.clients.metrics_metric_series_history.CompareMetricSeriesVersions(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.result.message = returned_0_0
            returned_0_1 = response_0.metric_series.dimensions.unit
            returned_0_1_part_1 = response.feature_value.measurements.add()
            if returned_0_1:
                returned_0_1_part_1.unit = returned_0_1
            echoed_0 = request.feature_value_id
            response.feature_value.feature_value_id = echoed_0
            echoed_1 = request.feature_value.subject
            response.feature_value.subject.CopyFrom(echoed_1)
            return response

    async def handle_estimate_feature_value(
        self,
        request: featurestore_v1_feature_value_calculation_service_pb2.EstimateFeatureValueRequest
    ) -> featurestore_v1_feature_value_calculation_service_pb2.EstimateFeatureValueResponse:
        """Estimates a feature value."""
        deps = self.deps
        response = featurestore_v1_feature_value_calculation_service_pb2.EstimateFeatureValueResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('EstimateFeatureValue', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'EstimateFeatureValue', {'reason': request.reason})
            await deps.repository.save_feature_value(request.context.tenant_id, request.feature_value)
            response_0 = featurestore_v1_feature_view_calculation_service_pb2.EstimateFeatureViewResponse()
            response_1 = metrics_v1_metric_series_history_service_pb2.ListMetricSeriesVersionsResponse()
            async for item_0 in async_messages(request.feature_value.measurements):
                outgoing_0 = featurestore_v1_feature_view_calculation_service_pb2.EstimateFeatureViewRequest(
                    context=request.context,
                    feature_view=featurestore_v1_featurestore_pb2.FeatureView(
                        audit=common_v1_audit_pb2.AuditInfo(created_at=item_0.observed_at),
                        dimensions=featurestore_v1_featurestore_pb2.FeatureViewDimensions(unit=item_0.unit)
                    )
                )
                response_0 = await deps.clients.featurestore_feature_view_calculation.EstimateFeatureView(
                    outgoing_0,
                    timeout=deps.settings.timeout
                )
            outgoing_1 = metrics_v1_metric_series_history_service_pb2.ListMetricSeriesVersionsRequest(
                context=request.context,
                filter=metrics_v1_metric_series_history_service_pb2.ListMetricSeriesVersionsRequest.Filter(
                    created_after=response_0.feature_view.audit.created_at,
                    labels=dict(response_0.result.details),
                    owner_id=response_0.feature_view.owner.user_id,
                    region=response_0.feature_view.address.region
                )
            )
            response_1 = await hooks.feature_value_calculation_estimate_feature_value1(
                deps.clients.metrics_metric_series_history,
                outgoing_1,
                deps.settings.timeout
            )
            returned_1_0 = response_1.result.message
            if returned_1_0:
                response.result.message = returned_1_0
            returned_1_1 = response_1.result.details
            response.result.details.update(returned_1_1)
            echoed_0 = request.feature_value_id
            response.feature_value.feature_value_id = echoed_0
            echoed_1 = request.feature_value.kind
            response.feature_value.kind = echoed_1
            return response

    async def handle_explain_feature_value_calculation(
        self,
        request: featurestore_v1_feature_value_calculation_service_pb2.ExplainFeatureValueCalculationRequest
    ) -> featurestore_v1_feature_value_calculation_service_pb2.ExplainFeatureValueCalculationResponse:
        """Explains a feature value."""
        deps = self.deps
        response = featurestore_v1_feature_value_calculation_service_pb2.ExplainFeatureValueCalculationResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ExplainFeatureValueCalculation', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ExplainFeatureValueCalculation',
                {'reason': request.reason}
            )
            await deps.repository.save_feature_value(request.context.tenant_id, request.feature_value)
            response_0 = featurestore_v1_feature_view_calculation_service_pb2.SimulateFeatureViewResponse()
            response_1 = anomalies_v1_anomaly_feedback_validation_service_pb2.PreviewAnomalyFeedbackResponse()
            outgoing_0 = featurestore_v1_feature_view_calculation_service_pb2.SimulateFeatureViewRequest()
            outgoing_0.context.CopyFrom(request.context)
            outgoing_0.feature_view.owner.email = request.details.contact.email
            outgoing_0.feature_view.owner.display_name = request.feature_value.subject.display_name
            outgoing_0.feature_view.code = request.feature_value.subject.code
            outgoing_0.annotations.update(dict(request.annotations))
            outgoing_0.context.tenant_id = tenant_id.get()
            response_0 = await deps.clients.featurestore_feature_view_calculation.SimulateFeatureView(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            for item_1 in request.feature_value.measurements:
                outgoing_1 = anomalies_v1_anomaly_feedback_validation_service_pb2.PreviewAnomalyFeedbackRequest(
                    anomaly_feedback=anomalies_v1_anomalies_pb2.AnomalyFeedback(
                        measurements=[
                            anomalies_v1_anomalies_pb2.AnomalyFeedbackMeasurement(
                                metric=item_1.metric,
                                observed_at=item_1.observed_at,
                                value=item_1.value
                            )
                        ]
                    ),
                    context=request.context
                )
                response_1 = await deps.clients.anomalies_anomaly_feedback_validation.PreviewAnomalyFeedback(
                    outgoing_1,
                    timeout=deps.settings.timeout
                )
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.result.message = returned_0_0
            echoed_0 = request.feature_value_id
            response.feature_value.feature_value_id = echoed_0
            echoed_1 = request.feature_value.subject
            response.feature_value.subject.CopyFrom(echoed_1)
            return response

    async def handle_get_feature_value_rates(
        self,
        request: featurestore_v1_feature_value_calculation_service_pb2.GetFeatureValueRatesRequest
    ) -> featurestore_v1_feature_value_calculation_service_pb2.GetFeatureValueRatesResponse:
        """Returns a feature value."""
        deps = self.deps
        response = featurestore_v1_feature_value_calculation_service_pb2.GetFeatureValueRatesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('GetFeatureValueRates', extra={'fields': {'domain': 'featurestore'}})
            await deps.repository.audit(request.context.tenant_id, 'GetFeatureValueRates', {})
            response_0 = featurestore_v1_feature_view_calculation_service_pb2.QuoteFeatureViewResponse()
            outgoing_0 = featurestore_v1_feature_view_calculation_service_pb2.QuoteFeatureViewRequest(
                context=request.context,
                feature_view=featurestore_v1_featurestore_pb2.FeatureView(
                    owner=identity_v1_refs_pb2.UserRef(
                        email=request.context.actor.email,
                        user_id=request.context.actor.user_id
                    )
                )
            )
            response_0 = await deps.clients.featurestore_feature_view_calculation.QuoteFeatureView(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_0)
            echoed_0 = request.feature_value_id
            response.feature_value.feature_value_id = echoed_0
            return response

    async def handle_quote_feature_value(
        self,
        request: featurestore_v1_feature_value_calculation_service_pb2.QuoteFeatureValueRequest
    ) -> featurestore_v1_feature_value_calculation_service_pb2.QuoteFeatureValueResponse:
        """Quotes a feature value."""
        deps = self.deps
        response = featurestore_v1_feature_value_calculation_service_pb2.QuoteFeatureValueResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('QuoteFeatureValue', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'QuoteFeatureValue', {'reason': request.reason})
            await deps.repository.save_feature_value(request.context.tenant_id, request.feature_value)
            response_0 = featurestore_v1_feature_view_calculation_service_pb2.EstimateFeatureViewResponse()
            response_1 = featurestore_v1_feature_view_calculation_service_pb2.ExplainFeatureViewCalculationResponse()
            outgoing_0 = featurestore_v1_feature_view_calculation_service_pb2.EstimateFeatureViewRequest(
                context=request.context,
                details=featurestore_v1_feature_view_calculation_service_pb2.EstimateFeatureViewRequest.Details(
                    destination=common_v1_address_pb2.PostalAddress(locality=request.details.destination.locality)
                ),
                feature_view=featurestore_v1_featurestore_pb2.FeatureView(
                    address=common_v1_address_pb2.PostalAddress(
                        country_code=request.details.destination.country_code,
                        recipient=request.details.destination.recipient
                    ),
                    owner=identity_v1_refs_pb2.UserRef(display_name=request.feature_value.subject.display_name)
                )
            )
            response_0 = await FeatureValueCalculationQuoteFeatureValue0Adapter(
                deps.clients.featurestore_feature_view_calculation,
                deps.settings.timeout
            )(outgoing_0)
            requests_1: list[
                featurestore_v1_feature_view_calculation_service_pb2.ExplainFeatureViewCalculationRequest
            ] = []
            for item_1 in request.feature_value.measurements:
                outgoing_1 = featurestore_v1_feature_view_calculation_service_pb2.ExplainFeatureViewCalculationRequest(
                    context=request.context,
                    feature_view=featurestore_v1_featurestore_pb2.FeatureView(
                        address=common_v1_address_pb2.PostalAddress(lines=list(response_0.feature_view.address.lines)),
                        dimensions=featurestore_v1_featurestore_pb2.FeatureViewDimensions(
                            unit=item_1.unit,
                            width=response_0.feature_view.dimensions.width
                        ),
                        owner=identity_v1_refs_pb2.UserRef(email=response_0.feature_view.owner.email)
                    )
                )
                requests_1.append(outgoing_1)
            replies_1 = await asyncio.gather(*(
                deps.clients.featurestore_feature_view_calculation.ExplainFeatureViewCalculation(
                    entry,
                    timeout=deps.settings.timeout
                ) for entry in requests_1
            ))
            if replies_1:
                response_1 = replies_1[-1]
            returned_0_0 = response_0.breakdown.total
            if returned_0_0.ListFields():
                response.breakdown.total.MergeFrom(returned_0_0)
            returned_0_1 = response_0.breakdown.currency_code
            if returned_0_1:
                response.breakdown.currency_code = returned_0_1
            echoed_0 = request.feature_value_id
            response.feature_value.feature_value_id = echoed_0
            echoed_1 = request.feature_value.attributes
            response.feature_value.attributes.update(echoed_1)
            return response

    async def handle_recalculate_feature_values(
        self,
        request: featurestore_v1_feature_value_calculation_service_pb2.RecalculateFeatureValuesRequest
    ) -> featurestore_v1_feature_value_calculation_service_pb2.RecalculateFeatureValuesResponse:
        """Recalculates a feature value."""
        deps = self.deps
        response = featurestore_v1_feature_value_calculation_service_pb2.RecalculateFeatureValuesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('RecalculateFeatureValues', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'RecalculateFeatureValues',
                {'reason': request.reason}
            )
            await deps.repository.save_feature_value(request.context.tenant_id, request.feature_value)
            response_0 = prescriptions_v1_prescription_service_pb2.CreatePrescriptionResponse()
            response_1 = anomalies_v1_anomaly_query_service_pb2.ExportAnomaliesResponse()
            outgoing_0 = prescriptions_v1_prescription_service_pb2.CreatePrescriptionRequest(
                context=request.context,
                prescription=prescriptions_v1_prescriptions_pb2.Prescription(
                    billing_address=common_v1_address_pb2.PostalAddress(
                        country_code=request.details.destination.country_code,
                        locality=request.details.destination.locality,
                        postal_code=request.details.destination.postal_code
                    )
                )
            )
            response_0 = await deps.clients.prescriptions_prescription.CreatePrescription(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = anomalies_v1_anomaly_query_service_pb2.ExportAnomaliesRequest(
                context=request.context,
                filter=anomalies_v1_anomaly_query_service_pb2.ExportAnomaliesRequest.Filter(
                    created_after=response_0.prescription.issued_at,
                    region=response_0.prescription.billing_address.region
                )
            )
            async for chunk_1 in deps.clients.anomalies_anomaly_query.ExportAnomalies(
                outgoing_1,
                timeout=deps.settings.timeout
            ):
                response_1 = chunk_1
            returned_0_0 = response_0.prescription.counterparty.display_name
            if returned_0_0:
                response.feature_value.subject.display_name = returned_0_0
            echoed_0 = request.feature_value_id
            response.feature_value.feature_value_id = echoed_0
            echoed_1 = request.feature_value.occurred_at
            response.feature_value.occurred_at.CopyFrom(echoed_1)
            return response

    async def handle_simulate_feature_value(
        self,
        request: featurestore_v1_feature_value_calculation_service_pb2.SimulateFeatureValueRequest
    ) -> featurestore_v1_feature_value_calculation_service_pb2.SimulateFeatureValueResponse:
        """Simulates a feature value."""
        deps = self.deps
        response = featurestore_v1_feature_value_calculation_service_pb2.SimulateFeatureValueResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SimulateFeatureValue', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'SimulateFeatureValue', {'reason': request.reason})
            await deps.repository.save_feature_value(request.context.tenant_id, request.feature_value)
            response_0 = featurestore_v1_feature_view_calculation_service_pb2.SimulateFeatureViewResponse()
            response_1 = featurestore_v1_feature_view_calculation_service_pb2.ExplainFeatureViewCalculationResponse()
            response_2 = metrics_v1_metric_alert_history_service_pb2.RecordMetricAlertVersionResponse()
            response_3 = lineage_v1_lineage_node_validation_service_pb2.NormalizeLineageNodeResponse()
            fields_0: dict[str, Any] = {
                'context': request.context,
                'details': {
                    'destination': {
                        'lines': list(request.details.destination.lines),
                        'locality': request.details.destination.locality
                    }
                },
                'feature_view': {
                    'address': {
                        'country_code': request.details.destination.country_code,
                        'postal_code': request.details.destination.postal_code
                    }
                }
            }
            outgoing_0 = featurestore_v1_feature_view_calculation_service_pb2.SimulateFeatureViewRequest(**fields_0)
            response_0 = await deps.clients.featurestore_feature_view_calculation.SimulateFeatureView(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = featurestore_v1_feature_view_calculation_service_pb2.ExplainFeatureViewCalculationRequest(
                context=request.context,
                feature_view=featurestore_v1_featurestore_pb2.FeatureView(
                    address=common_v1_address_pb2.PostalAddress(
                        recipient=response_0.feature_view.address.recipient,
                        region=request.details.destination.region
                    ),
                    audit=common_v1_audit_pb2.AuditInfo(updated_at=response_0.feature_view.audit.updated_at)
                )
            )
            document_1 = MessageToDict(outgoing_1, preserving_proto_field_name=True)
            outgoing_1 = ParseDict(
                document_1,
                featurestore_v1_feature_view_calculation_service_pb2.ExplainFeatureViewCalculationRequest()
            )
            response_1 = await deps.clients.featurestore_feature_view_calculation.ExplainFeatureViewCalculation(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = metrics_v1_metric_alert_history_service_pb2.RecordMetricAlertVersionRequest(
                context=request.context,
                metric_alert=metrics_v1_metrics_pb2.MetricAlert(
                    audit=common_v1_audit_pb2.AuditInfo(
                        etag=response_0.feature_view.audit.etag,
                        updated_at=response_1.feature_view.audit.updated_at
                    ),
                    owner=identity_v1_refs_pb2.UserRef(
                        display_name=response_1.feature_view.owner.display_name,
                        email=response_0.feature_view.owner.email
                    )
                )
            )
            document_2 = MessageToJson(outgoing_2, preserving_proto_field_name=True)
            outgoing_2 = Parse(
                document_2,
                metrics_v1_metric_alert_history_service_pb2.RecordMetricAlertVersionRequest()
            )
            response_2 = await deps.clients.metrics_metric_alert_history.RecordMetricAlertVersion(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            outgoing_3 = lineage_v1_lineage_node_validation_service_pb2.NormalizeLineageNodeRequest()
            outgoing_3.context.CopyFrom(request.context)
            field_3_1_part_1 = outgoing_3.lineage_node.children.add()
            field_3_1_part_2 = field_3_1_part_1.children.add()
            field_3_1_part_2.location.locality = request.details.destination.locality
            if response_1.feature_view.WhichOneof('locator') == 'address':
                field_3_2_part_1 = outgoing_3.lineage_node.children.add()
                field_3_2_part_2 = field_3_2_part_1.children.add()
                field_3_2_part_2.location.postal_code = response_1.feature_view.address.postal_code
            response_3 = await deps.clients.lineage_lineage_node_validation.NormalizeLineageNode(
                outgoing_3,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.feature_view.dimensions.unit
            returned_0_0_part_1 = response.feature_value.measurements.add()
            if returned_0_0:
                returned_0_0_part_1.unit = returned_0_0
            returned_0_1 = response_0.result.message
            if returned_0_1:
                response.result.message = returned_0_1
            returned_1_0 = response_1.result.message
            if returned_1_0:
                response.result.message = returned_1_0
            returned_2_0 = response_2.result.correlation_id
            if returned_2_0:
                response.feature_value.correlation_id = returned_2_0
            returned_2_1 = response_2.outcome.status
            if returned_2_1:
                response.result.status = returned_2_1
            returned_3_0 = response_3.result.reference_ids
            response.result.reference_ids.extend(returned_3_0)
            returned_3_1 = response_3.lineage_node.manager.display_name
            if returned_3_1:
                response.feature_value.subject.display_name = returned_3_1
            echoed_0 = request.feature_value_id
            response.feature_value.feature_value_id = echoed_0
            echoed_1 = request.feature_value.occurred_at
            response.feature_value.occurred_at.CopyFrom(echoed_1)
            return response
