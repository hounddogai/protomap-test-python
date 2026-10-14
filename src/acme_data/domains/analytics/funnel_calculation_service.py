"""Computes the figures of a funnel, such as totals, taxes, and estimates."""

from __future__ import annotations

from collections.abc import AsyncIterator
from collections.abc import Awaitable
from collections.abc import Callable
from functools import partial
from typing import cast
import asyncio
import logging

from google.protobuf.any_pb2 import Any as AnyMessage
from google.protobuf.json_format import MessageToDict
from google.protobuf.json_format import ParseDict
import grpc

from acme.admissions.v1 import admission_calculation_service_pb2 as admissions_v1_admission_calculation_service_pb2
from acme.admissions.v1 import admissions_pb2 as admissions_v1_admissions_pb2
from acme.admissions.v1 import refs_pb2 as admissions_v1_refs_pb2
from acme.analytics.v1 import funnel_calculation_service_pb2 as analytics_v1_funnel_calculation_service_pb2
from acme.analytics.v1 import funnel_calculation_service_pb2_grpc as analytics_v1_funnel_calculation_service_pb2_grpc
from acme.anomalies.v1 import anomalies_pb2 as anomalies_v1_anomalies_pb2
from acme.anomalies.v1 import anomaly_query_service_pb2 as anomalies_v1_anomaly_query_service_pb2
from acme.anomalies.v1 import detector_validation_service_pb2 as anomalies_v1_detector_validation_service_pb2
from acme.appointments.v1 import appointment_service_pb2 as appointments_v1_appointment_service_pb2
from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.configuration.v1 import config_set_service_pb2 as configuration_v1_config_set_service_pb2
from acme.documents.v1 import document_query_service_pb2 as documents_v1_document_query_service_pb2
from acme.forecasting.v1 import forecasting_pb2 as forecasting_v1_forecasting_pb2
from acme.forecasting.v1 import scenario_validation_service_pb2 as forecasting_v1_scenario_validation_service_pb2
from acme.forecasting.v1 import (
    scenario_validation_service_pb2_grpc as forecasting_v1_scenario_validation_service_pb2_grpc,
)
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.labeling.v1 import annotation_query_service_pb2 as labeling_v1_annotation_query_service_pb2
from acme.metrics.v1 import dashboard_sync_service_pb2 as metrics_v1_dashboard_sync_service_pb2
from acme.metrics.v1 import metric_alert_query_service_pb2 as metrics_v1_metric_alert_query_service_pb2
from acme.metrics.v1 import metric_series_validation_service_pb2 as metrics_v1_metric_series_validation_service_pb2
from acme.metrics.v1 import metrics_pb2 as metrics_v1_metrics_pb2
from acme.notifications.v1 import notification_query_service_pb2 as notifications_v1_notification_query_service_pb2
from acme.notifications.v1 import (
    notification_validation_service_pb2 as notifications_v1_notification_validation_service_pb2,
)
from acme.notifications.v1 import notifications_pb2 as notifications_v1_notifications_pb2
from acme.notifications.v1 import refs_pb2 as notifications_v1_refs_pb2
from acme.prescriptions.v1 import prescription_service_pb2 as prescriptions_v1_prescription_service_pb2
from acme.ratelimiting.v1 import rate_limit_service_pb2 as ratelimiting_v1_rate_limit_service_pb2
from acme.ratelimiting.v1 import ratelimiting_pb2 as ratelimiting_v1_ratelimiting_pb2

from acme_data.domains.analytics import hooks
from acme_data.domains.analytics.adapters import FunnelCalculationCalculateFunnel0Adapter
from acme_data.domains.analytics.adapters import FunnelCalculationCalculateFunnel0Port
from acme_data.domains.analytics.adapters import FunnelCalculationCompareFunnelOptions0Adapter
from acme_data.domains.analytics.dependencies import Dependencies
from acme_data.domains.analytics.models import FunnelCalculationQuoteFunnel1Command
from acme_data.domains.analytics.models import to_funnel_calculation_quote_funnel1_command
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import run_steps
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_id
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class FunnelCalculationServicer(analytics_v1_funnel_calculation_service_pb2_grpc.FunnelCalculationServiceServicer):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    async def CalculateFunnel(
        self, request: analytics_v1_funnel_calculation_service_pb2.CalculateFunnelRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_funnel_calculation_service_pb2.CalculateFunnelResponse:
        """Calculates a funnel."""
        return await self.handle_calculate_funnel(request)

    @rpc_errors
    async def CompareFunnelOptions(
        self, request: analytics_v1_funnel_calculation_service_pb2.CompareFunnelOptionsRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_funnel_calculation_service_pb2.CompareFunnelOptionsResponse:
        """Compares a funnel."""
        return await self.handle_compare_funnel_options(request)

    @rpc_errors
    async def EstimateFunnel(
        self, request: analytics_v1_funnel_calculation_service_pb2.EstimateFunnelRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_funnel_calculation_service_pb2.EstimateFunnelResponse:
        """Estimates a funnel."""
        return await self.handle_estimate_funnel(request)

    @rpc_errors
    async def ExplainFunnelCalculation(
        self, request: analytics_v1_funnel_calculation_service_pb2.ExplainFunnelCalculationRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_funnel_calculation_service_pb2.ExplainFunnelCalculationResponse:
        """Explains a funnel."""
        return await self.handle_explain_funnel_calculation(request)

    @rpc_errors
    @retry_transient
    async def GetFunnelRates(
        self, request: analytics_v1_funnel_calculation_service_pb2.GetFunnelRatesRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_funnel_calculation_service_pb2.GetFunnelRatesResponse:
        """Returns a funnel."""
        return await self.handle_get_funnel_rates(request)

    @rpc_errors
    async def QuoteFunnel(
        self, request: analytics_v1_funnel_calculation_service_pb2.QuoteFunnelRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_funnel_calculation_service_pb2.QuoteFunnelResponse:
        """Quotes a funnel."""
        return await self.handle_quote_funnel(request)

    @rpc_errors
    async def SimulateFunnel(
        self, request: analytics_v1_funnel_calculation_service_pb2.SimulateFunnelRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_funnel_calculation_service_pb2.SimulateFunnelResponse:
        """Simulates a funnel."""
        return await self.handle_simulate_funnel(request)

    async def handle_calculate_funnel(
        self,
        request: analytics_v1_funnel_calculation_service_pb2.CalculateFunnelRequest
    ) -> analytics_v1_funnel_calculation_service_pb2.CalculateFunnelResponse:
        """Calculates a funnel."""
        deps = self.deps
        response = analytics_v1_funnel_calculation_service_pb2.CalculateFunnelResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CalculateFunnel', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'CalculateFunnel', {'reason': request.reason})
            await deps.repository.save_funnel(request.context.tenant_id, request.funnel)
            response_0 = metrics_v1_metric_alert_query_service_pb2.BrowseMetricAlertsResponse()
            response_1 = anomalies_v1_anomaly_query_service_pb2.BrowseAnomaliesResponse()
            outgoing_0 = metrics_v1_metric_alert_query_service_pb2.BrowseMetricAlertsRequest(
                context=request.context,
                filter=metrics_v1_metric_alert_query_service_pb2.BrowseMetricAlertsRequest.Filter(
                    region=request.details.destination.region
                )
            )
            port_0: FunnelCalculationCalculateFunnel0Port = FunnelCalculationCalculateFunnel0Adapter(
                deps.clients.metrics_metric_alert_query,
                deps.settings.timeout
            )
            response_0 = await port_0.execute(outgoing_0)
            outgoing_1 = anomalies_v1_anomaly_query_service_pb2.BrowseAnomaliesRequest(
                context=request.context,
                filter=anomalies_v1_anomaly_query_service_pb2.BrowseAnomaliesRequest.Filter(
                    owner_id=request.funnel.owner.user_id,
                    region=request.details.destination.region
                )
            )
            steps_1 = [
                partial(deps.clients.anomalies_anomaly_query.BrowseAnomalies, outgoing_1, timeout=deps.settings.timeout)
            ]
            results_1 = await run_steps(steps_1)
            response_1 = results_1[-1]
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.result.message = returned_0_0
            returned_0_1 = response_0.result.details
            response.result.details.update(returned_0_1)
            returned_1_0 = response_1.result.message
            if returned_1_0:
                response.result.message = returned_1_0
            returned_1_1 = response_1.result.status
            if returned_1_1:
                response.result.status = returned_1_1
            echoed_0 = request.funnel_id
            response.funnel.funnel_id = echoed_0
            echoed_1 = request.funnel.priority
            response.funnel.priority = echoed_1
            return response

    async def handle_compare_funnel_options(
        self,
        request: analytics_v1_funnel_calculation_service_pb2.CompareFunnelOptionsRequest
    ) -> analytics_v1_funnel_calculation_service_pb2.CompareFunnelOptionsResponse:
        """Compares a funnel."""
        deps = self.deps
        response = analytics_v1_funnel_calculation_service_pb2.CompareFunnelOptionsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CompareFunnelOptions', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'CompareFunnelOptions', {'reason': request.reason})
            await deps.repository.save_funnel(request.context.tenant_id, request.funnel)
            response_0 = appointments_v1_appointment_service_pb2.ListAppointmentsResponse()
            response_1 = anomalies_v1_detector_validation_service_pb2.PreviewDetectorResponse()
            response_2 = notifications_v1_notification_validation_service_pb2.ExplainNotificationDecisionResponse()
            outgoing_0 = appointments_v1_appointment_service_pb2.ListAppointmentsRequest(
                context=request.context,
                filter=appointments_v1_appointment_service_pb2.ListAppointmentsRequest.Filter(
                    region=request.details.destination.region
                )
            )
            response_0 = await FunnelCalculationCompareFunnelOptions0Adapter(
                deps.clients.appointments_appointment,
                deps.settings.timeout
            )(outgoing_0)
            callbacks_1: list[
                Callable[[], Awaitable[anomalies_v1_detector_validation_service_pb2.PreviewDetectorResponse]]
            ] = []
            for item_1 in request.funnel.conditions:
                outgoing_1 = anomalies_v1_detector_validation_service_pb2.PreviewDetectorRequest(
                    context=request.context,
                    detector=anomalies_v1_anomalies_pb2.Detector(
                        conditions=[
                            anomalies_v1_anomalies_pb2.DetectorCondition(
                                attribute=item_1.attribute,
                                operator=item_1.operator
                            )
                        ]
                    )
                )
                async def send_1(
                    payload: anomalies_v1_detector_validation_service_pb2.PreviewDetectorRequest = outgoing_1
                ) -> anomalies_v1_detector_validation_service_pb2.PreviewDetectorResponse:
                    return await deps.clients.anomalies_detector_validation.PreviewDetector(
                        payload,
                        timeout=deps.settings.timeout
                    )
                callbacks_1.append(send_1)
            for callback_1 in callbacks_1:
                response_1 = await callback_1()
            outgoing_2 = notifications_v1_notification_validation_service_pb2.ExplainNotificationDecisionRequest(
                context=request.context,
                notification=notifications_v1_notifications_pb2.Notification(
                    assignee=identity_v1_refs_pb2.UserRef(email=request.funnel.owner.email),
                    customer=notifications_v1_refs_pb2.NotificationTemplateRef(
                        display_name=request.funnel.owner.display_name
                    )
                )
            )
            response_2 = await deps.clients.notifications_notification_validation.ExplainNotificationDecision(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_0)
            returned_2_0 = response_2.notification.priority
            if returned_2_0:
                response.funnel.priority = returned_2_0
            echoed_0 = request.funnel_id
            response.funnel.funnel_id = echoed_0
            echoed_1 = request.funnel.status
            response.funnel.status = echoed_1
            return response

    async def handle_estimate_funnel(
        self,
        request: analytics_v1_funnel_calculation_service_pb2.EstimateFunnelRequest
    ) -> analytics_v1_funnel_calculation_service_pb2.EstimateFunnelResponse:
        """Estimates a funnel."""
        deps = self.deps
        response = analytics_v1_funnel_calculation_service_pb2.EstimateFunnelResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('EstimateFunnel', extra={'fields': {'currency_code': request.details.currency_code}})
            await deps.repository.audit(
                request.context.tenant_id,
                'EstimateFunnel',
                {'currency_code': request.details.currency_code}
            )
            await deps.repository.save_funnel(request.context.tenant_id, request.funnel)
            response_0 = admissions_v1_admission_calculation_service_pb2.ExplainAdmissionCalculationResponse()
            response_1 = documents_v1_document_query_service_pb2.ResolveDocumentsResponse()
            outgoing_0 = admissions_v1_admission_calculation_service_pb2.ExplainAdmissionCalculationRequest(
                admission=admissions_v1_admissions_pb2.Admission(
                    subject=admissions_v1_refs_pb2.GateScanRef(display_name=request.funnel.owner.display_name)
                ),
                annotations=dict(request.annotations),
                context=request.context,
                details=admissions_v1_admission_calculation_service_pb2.ExplainAdmissionCalculationRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(email=request.funnel.block.notify_email)
                ),
                reason=request.reason
            )
            outgoing_1 = documents_v1_document_query_service_pb2.ResolveDocumentsRequest(context=request.context)
            response_0, response_1 = await asyncio.gather(
                deps.clients.admissions_admission_calculation.ExplainAdmissionCalculation(
                    outgoing_0,
                    timeout=deps.settings.timeout
                ),
                deps.clients.documents_document_query.ResolveDocuments(outgoing_1, timeout=deps.settings.timeout),
            )
            returned_0_0 = response_0.outcome.message
            if returned_0_0:
                response.result.message = returned_0_0
            returned_1_0 = response_1.result.status
            if returned_1_0:
                response.result.status = returned_1_0
            returned_1_1 = response_1.result.reference_ids
            response.result.reference_ids.extend(returned_1_1)
            echoed_0 = request.funnel_id
            response.funnel.funnel_id = echoed_0
            echoed_1 = request.funnel.effective
            response.funnel.effective.CopyFrom(echoed_1)
            return response

    async def handle_explain_funnel_calculation(
        self,
        request: analytics_v1_funnel_calculation_service_pb2.ExplainFunnelCalculationRequest
    ) -> analytics_v1_funnel_calculation_service_pb2.ExplainFunnelCalculationResponse:
        """Explains a funnel."""
        deps = self.deps
        response = analytics_v1_funnel_calculation_service_pb2.ExplainFunnelCalculationResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ExplainFunnelCalculation', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ExplainFunnelCalculation',
                {'reason': request.reason}
            )
            await deps.repository.save_funnel(request.context.tenant_id, request.funnel)
            response_0 = configuration_v1_config_set_service_pb2.BatchGetConfigSetsResponse()
            response_1 = prescriptions_v1_prescription_service_pb2.UpdatePrescriptionResponse()
            outgoing_0 = configuration_v1_config_set_service_pb2.BatchGetConfigSetsRequest(context=request.context)
            document_0 = MessageToDict(outgoing_0, preserving_proto_field_name=True)
            outgoing_0 = ParseDict(document_0, configuration_v1_config_set_service_pb2.BatchGetConfigSetsRequest())
            response_0 = await deps.clients.configuration_config_set.BatchGetConfigSets(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = prescriptions_v1_prescription_service_pb2.UpdatePrescriptionRequest()
            outgoing_1.context.CopyFrom(request.context)
            if request.funnel.WhichOneof('action') == 'discount':
                field_1_1_part_1 = outgoing_1.prescription.lines.add()
                field_1_1_part_1.tax.amount.CopyFrom(request.funnel.discount.amount)
            response_1 = await deps.clients.prescriptions_prescription.UpdatePrescription(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.result.message = returned_0_0
            returned_1_0 = response_1.prescription.audit.updated_by
            if returned_1_0:
                response.funnel.audit.updated_by = returned_1_0
            returned_1_1 = response_1.prescription.counterparty.display_name
            if returned_1_1:
                response.funnel.owner.display_name = returned_1_1
            echoed_0 = request.funnel_id
            response.funnel.funnel_id = echoed_0
            echoed_1 = request.funnel.version
            response.funnel.version = echoed_1
            return response

    async def handle_get_funnel_rates(
        self,
        request: analytics_v1_funnel_calculation_service_pb2.GetFunnelRatesRequest
    ) -> analytics_v1_funnel_calculation_service_pb2.GetFunnelRatesResponse:
        """Returns a funnel."""
        deps = self.deps
        response = analytics_v1_funnel_calculation_service_pb2.GetFunnelRatesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('GetFunnelRates', extra={'fields': {'domain': 'analytics'}})
            await deps.repository.audit(request.context.tenant_id, 'GetFunnelRates', {})
            response_0 = ratelimiting_v1_rate_limit_service_pb2.CreateRateLimitResponse()
            response_1 = notifications_v1_notification_query_service_pb2.ResolveNotificationsResponse()
            outgoing_0 = ratelimiting_v1_rate_limit_service_pb2.CreateRateLimitRequest(
                context=request.context,
                rate_limit=ratelimiting_v1_ratelimiting_pb2.RateLimit(
                    owner=identity_v1_refs_pb2.UserRef(
                        email=request.context.actor.email,
                        user_id=request.context.actor.user_id
                    )
                )
            )
            response_0 = await deps.clients.ratelimiting_rate_limit.CreateRateLimit(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = notifications_v1_notification_query_service_pb2.ResolveNotificationsRequest(
                context=request.context
            )
            envelope_1 = AnyMessage()
            envelope_1.Pack(outgoing_1)
            outgoing_1 = notifications_v1_notification_query_service_pb2.ResolveNotificationsRequest()
            if not envelope_1.Unpack(outgoing_1):
                raise ValueError("partner envelope contains the wrong request type")
            response_1 = await deps.clients.notifications_notification_query.ResolveNotifications(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.result.message = returned_0_0
            returned_1_0 = response_1.result.reference_ids
            response.result.reference_ids.extend(returned_1_0)
            echoed_0 = request.funnel_id
            response.funnel.funnel_id = echoed_0
            return response

    async def handle_quote_funnel(
        self,
        request: analytics_v1_funnel_calculation_service_pb2.QuoteFunnelRequest
    ) -> analytics_v1_funnel_calculation_service_pb2.QuoteFunnelResponse:
        """Quotes a funnel."""
        deps = self.deps
        response = analytics_v1_funnel_calculation_service_pb2.QuoteFunnelResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('QuoteFunnel', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'QuoteFunnel', {'reason': request.reason})
            await deps.repository.save_funnel(request.context.tenant_id, request.funnel)
            response_0 = forecasting_v1_scenario_validation_service_pb2.LintScenariosResponse()
            response_1 = metrics_v1_metric_alert_query_service_pb2.FindMetricAlertsResponse()
            outgoing_0 = forecasting_v1_scenario_validation_service_pb2.LintScenariosRequest(
                context=request.context,
                details=forecasting_v1_scenario_validation_service_pb2.LintScenariosRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(email=request.funnel.owner.email)
                ),
                scenario=forecasting_v1_forecasting_pb2.Scenario(
                    audit=common_v1_audit_pb2.AuditInfo(
                        updated_at=request.funnel.audit.updated_at,
                        updated_by=request.funnel.audit.updated_by
                    )
                )
            )
            registered_0 = cast(
                forecasting_v1_scenario_validation_service_pb2_grpc.ScenarioValidationServiceStub,
                deps.clients.registry['acme.forecasting.v1.ScenarioValidationService']
            )
            response_0 = await registered_0.LintScenarios(outgoing_0, timeout=deps.settings.timeout)
            command_1 = FunnelCalculationQuoteFunnel1Command(
                context=request.context,
                filter_region=request.details.destination.region,
                filter_created_after=response_0.scenario.audit.created_at,
                filter_owner_id=response_0.scenario.scenario_id,
                filter_labels=dict(response_0.scenario.custom_fields)
            )
            outgoing_1 = to_funnel_calculation_quote_funnel1_command(command_1)
            response_1 = await deps.clients.metrics_metric_alert_query.FindMetricAlerts(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.scenario.assignee.user_id
            if returned_0_0:
                response.funnel.owner.user_id = returned_0_0
            returned_1_0 = response_1.result.correlation_id
            if returned_1_0:
                response.result.correlation_id = returned_1_0
            returned_1_1 = response_1.result.details
            response.result.details.update(returned_1_1)
            echoed_0 = request.funnel_id
            response.funnel.funnel_id = echoed_0
            echoed_1 = request.funnel.parameters
            response.funnel.parameters.update(echoed_1)
            return response

    async def handle_simulate_funnel(
        self,
        request: analytics_v1_funnel_calculation_service_pb2.SimulateFunnelRequest
    ) -> analytics_v1_funnel_calculation_service_pb2.SimulateFunnelResponse:
        """Simulates a funnel."""
        deps = self.deps
        response = analytics_v1_funnel_calculation_service_pb2.SimulateFunnelResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SimulateFunnel', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'SimulateFunnel', {'reason': request.reason})
            await deps.repository.save_funnel(request.context.tenant_id, request.funnel)
            response_0 = labeling_v1_annotation_query_service_pb2.ExportAnnotationsResponse()
            response_1 = metrics_v1_metric_series_validation_service_pb2.CheckMetricSeriesEligibilityResponse()
            response_2 = metrics_v1_metric_alert_query_service_pb2.FindMetricAlertsResponse()
            response_3 = metrics_v1_dashboard_sync_service_pb2.ResolveDashboardConflictResponse()
            outgoing_0 = labeling_v1_annotation_query_service_pb2.ExportAnnotationsRequest(
                context=request.context,
                filter=labeling_v1_annotation_query_service_pb2.ExportAnnotationsRequest.Filter(
                    created_after=request.funnel.audit.updated_at,
                    region=request.details.destination.region
                )
            )
            async for chunk_0 in deps.clients.labeling_annotation_query.ExportAnnotations(
                outgoing_0,
                timeout=deps.settings.timeout
            ):
                response_0 = chunk_0
            outgoing_1 = metrics_v1_metric_series_validation_service_pb2.CheckMetricSeriesEligibilityRequest(
                context=request.context,
                metric_series=metrics_v1_metrics_pb2.MetricSeries(
                    address=common_v1_address_pb2.PostalAddress(lines=list(request.details.destination.lines)),
                    owner=identity_v1_refs_pb2.UserRef(email=request.funnel.owner.email)
                )
            )
            send_1 = partial(
                deps.clients.metrics_metric_series_validation.CheckMetricSeriesEligibility,
                timeout=deps.settings.timeout
            )
            response_1 = await send_1(outgoing_1)
            outgoing_2 = metrics_v1_metric_alert_query_service_pb2.FindMetricAlertsRequest(
                context=request.context,
                filter=metrics_v1_metric_alert_query_service_pb2.FindMetricAlertsRequest.Filter(
                    created_after=response_1.metric_series.audit.updated_at,
                    labels=dict(response_1.result.details),
                    owner_id=request.funnel.owner.user_id,
                    region=response_1.metric_series.address.region
                )
            )
            response_2 = await hooks.funnel_calculation_simulate_funnel2(
                deps.clients.metrics_metric_alert_query,
                outgoing_2,
                deps.settings.timeout
            )
            outgoing_3 = metrics_v1_dashboard_sync_service_pb2.ResolveDashboardConflictRequest()
            outgoing_3.context.CopyFrom(request.context)
            outgoing_3.dashboard.billing_address.lines.extend(list(response_1.metric_series.address.lines))
            outgoing_3.dashboard.audit.updated_by = response_1.metric_series.audit.updated_by
            outgoing_3.context.tenant_id = tenant_id.get()
            response_3 = await deps.clients.metrics_dashboard_sync.ResolveDashboardConflict(
                outgoing_3,
                timeout=deps.settings.timeout
            )
            returned_1_0 = response_1.result.correlation_id
            if returned_1_0:
                response.result.correlation_id = returned_1_0
            returned_2_0 = response_2.result.correlation_id
            if returned_2_0:
                response.result.correlation_id = returned_2_0
            returned_3_0 = response_3.dashboard.audit.etag
            if returned_3_0:
                response.funnel.audit.etag = returned_3_0
            returned_3_1 = response_3.result.details
            response.result.details.update(returned_3_1)
            echoed_0 = request.funnel_id
            response.funnel.funnel_id = echoed_0
            echoed_1 = request.funnel.description
            response.funnel.description = echoed_1
            return response
