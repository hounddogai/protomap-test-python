"""Reusable transport mixin for AnalyticsEventValidationService."""

from __future__ import annotations

from collections.abc import AsyncIterator
from functools import partial
from typing import Any
from typing import cast
import logging

from google.protobuf.json_format import MessageToDict
from google.protobuf.json_format import ParseDict
import grpc

from acme.analytics.v1 import (
    analytics_event_validation_service_pb2 as analytics_v1_analytics_event_validation_service_pb2,
)
from acme.analytics.v1 import funnel_calculation_service_pb2 as analytics_v1_funnel_calculation_service_pb2
from acme.anomalies.v1 import detector_query_service_pb2 as anomalies_v1_detector_query_service_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.labeling.v1 import annotation_validation_service_pb2 as labeling_v1_annotation_validation_service_pb2
from acme.labeling.v1 import labeling_pb2 as labeling_v1_labeling_pb2
from acme.labeling.v1 import refs_pb2 as labeling_v1_refs_pb2
from acme.metrics.v1 import metric_alert_notification_service_pb2 as metrics_v1_metric_alert_notification_service_pb2
from acme.metrics.v1 import metric_series_service_pb2 as metrics_v1_metric_series_service_pb2
from acme.modelregistry.v1 import modelregistry_pb2 as modelregistry_v1_modelregistry_pb2
from acme.modelregistry.v1 import registered_model_service_pb2 as modelregistry_v1_registered_model_service_pb2

from acme_data.domains.analytics.dependencies import Dependencies
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import run_steps
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_id
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class AnalyticsEventValidationServicerHandlers:
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    async def ExplainAnalyticsEventDecision(
        self, request: analytics_v1_analytics_event_validation_service_pb2.ExplainAnalyticsEventDecisionRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_analytics_event_validation_service_pb2.ExplainAnalyticsEventDecisionResponse:
        """Explains an analytics event."""
        return await self.handle_explain_analytics_event_decision(request)

    @rpc_errors
    @retry_transient
    async def GetAnalyticsEventRules(
        self, request: analytics_v1_analytics_event_validation_service_pb2.GetAnalyticsEventRulesRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_analytics_event_validation_service_pb2.GetAnalyticsEventRulesResponse:
        """Returns an analytics event."""
        return await self.handle_get_analytics_event_rules(request)

    @rpc_errors
    async def LintAnalyticsEvents(
        self, request: analytics_v1_analytics_event_validation_service_pb2.LintAnalyticsEventsRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_analytics_event_validation_service_pb2.LintAnalyticsEventsResponse:
        """Lints an analytics event."""
        return await self.handle_lint_analytics_events(request)

    @rpc_errors
    async def NormalizeAnalyticsEvent(
        self, request: analytics_v1_analytics_event_validation_service_pb2.NormalizeAnalyticsEventRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_analytics_event_validation_service_pb2.NormalizeAnalyticsEventResponse:
        """Normalizes an analytics event."""
        return await self.handle_normalize_analytics_event(request)

    @rpc_errors
    async def PreviewAnalyticsEvent(
        self, request: analytics_v1_analytics_event_validation_service_pb2.PreviewAnalyticsEventRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_analytics_event_validation_service_pb2.PreviewAnalyticsEventResponse:
        """Previews an analytics event."""
        return await self.handle_preview_analytics_event(request)

    @rpc_errors
    async def ValidateAnalyticsEvent(
        self, request: analytics_v1_analytics_event_validation_service_pb2.ValidateAnalyticsEventRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_analytics_event_validation_service_pb2.ValidateAnalyticsEventResponse:
        """Validates an analytics event."""
        return await self.handle_validate_analytics_event(request)

    async def handle_explain_analytics_event_decision(
        self,
        request: analytics_v1_analytics_event_validation_service_pb2.ExplainAnalyticsEventDecisionRequest
    ) -> analytics_v1_analytics_event_validation_service_pb2.ExplainAnalyticsEventDecisionResponse:
        """Explains an analytics event."""
        deps = self.deps
        response = analytics_v1_analytics_event_validation_service_pb2.ExplainAnalyticsEventDecisionResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ExplainAnalyticsEventDecision', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ExplainAnalyticsEventDecision',
                {'reason': request.reason}
            )
            await deps.repository.save_analytics_event(request.context.tenant_id, request.analytics_event)
            response_0 = metrics_v1_metric_alert_notification_service_pb2.SubscribeMetricAlertUpdatesResponse()
            response_1 = analytics_v1_funnel_calculation_service_pb2.SimulateFunnelResponse()
            outgoing_0 = metrics_v1_metric_alert_notification_service_pb2.SubscribeMetricAlertUpdatesRequest()
            outgoing_0.context.CopyFrom(request.context)
            outgoing_0.details.recipient.phone = request.details.contact.phone
            outgoing_0.details.recipient.name.CopyFrom(request.details.contact.name)
            outgoing_0.details.recipient.preferred_channel = request.details.contact.preferred_channel
            outgoing_0.details.recipient.email = request.details.contact.email
            outgoing_0.context.tenant_id = tenant_id.get()
            response_0 = await deps.clients.metrics_metric_alert_notification.SubscribeMetricAlertUpdates(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = analytics_v1_funnel_calculation_service_pb2.SimulateFunnelRequest()
            outgoing_1.context.CopyFrom(request.context)
            if response_0.metric_alert.WhichOneof('action') == 'discount':
                outgoing_1.funnel.discount.percent = response_0.metric_alert.discount.percent
            outgoing_1.funnel.owner.display_name = request.analytics_event.subject.display_name
            outgoing_1.funnel.audit.created_by = response_0.metric_alert.audit.created_by
            outgoing_1.funnel.scopes.extend(list(response_0.metric_alert.scopes))
            response_1 = await deps.clients.analytics_funnel_calculation.SimulateFunnel(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.outcome.message
            if returned_0_0:
                response.result.message = returned_0_0
            returned_1_0 = response_1.funnel.version
            if returned_1_0:
                response.analytics_event.subject.version = returned_1_0
            returned_1_1 = response_1.result.status
            if returned_1_1:
                response.outcome.status = returned_1_1
            echoed_0 = request.analytics_event_id
            response.analytics_event.analytics_event_id = echoed_0
            echoed_1 = request.analytics_event.attributes
            response.analytics_event.attributes.update(echoed_1)
            return response

    async def handle_get_analytics_event_rules(
        self,
        request: analytics_v1_analytics_event_validation_service_pb2.GetAnalyticsEventRulesRequest
    ) -> analytics_v1_analytics_event_validation_service_pb2.GetAnalyticsEventRulesResponse:
        """Returns an analytics event."""
        deps = self.deps
        response = analytics_v1_analytics_event_validation_service_pb2.GetAnalyticsEventRulesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('GetAnalyticsEventRules', extra={'fields': {'locale': request.context.locale}})
            await deps.repository.audit(
                request.context.tenant_id,
                'GetAnalyticsEventRules',
                {'locale': request.context.locale}
            )
            echoed_0 = request.analytics_event_id
            response.analytics_event.analytics_event_id = echoed_0
            return response

    async def handle_lint_analytics_events(
        self,
        request: analytics_v1_analytics_event_validation_service_pb2.LintAnalyticsEventsRequest
    ) -> analytics_v1_analytics_event_validation_service_pb2.LintAnalyticsEventsResponse:
        """Lints an analytics event."""
        deps = self.deps
        response = analytics_v1_analytics_event_validation_service_pb2.LintAnalyticsEventsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('LintAnalyticsEvents', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'LintAnalyticsEvents', {'reason': request.reason})
            await deps.repository.save_analytics_event(request.context.tenant_id, request.analytics_event)
            response_0 = labeling_v1_annotation_validation_service_pb2.NormalizeAnnotationResponse()
            response_1 = metrics_v1_metric_series_service_pb2.WatchMetricSeriesesResponse()
            response_2 = anomalies_v1_detector_query_service_pb2.FindDetectorsResponse()
            response_3 = modelregistry_v1_registered_model_service_pb2.UpdateRegisteredModelResponse()
            outgoing_0 = labeling_v1_annotation_validation_service_pb2.NormalizeAnnotationRequest(
                annotation=labeling_v1_labeling_pb2.Annotation(
                    subject=labeling_v1_refs_pb2.LabelingTaskRef(
                        display_name=request.analytics_event.subject.display_name
                    )
                ),
                context=request.context,
                details=labeling_v1_annotation_validation_service_pb2.NormalizeAnnotationRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(
                        email=request.details.contact.email,
                        preferred_channel=request.details.contact.preferred_channel
                    )
                )
            )
            steps_0 = [
                partial(
                    deps.clients.labeling_annotation_validation.NormalizeAnnotation,
                    outgoing_0,
                    timeout=deps.settings.timeout
                )
            ]
            results_0 = await run_steps(steps_0)
            response_0 = results_0[-1]
            outgoing_1 = metrics_v1_metric_series_service_pb2.WatchMetricSeriesesRequest(
                context=request.context,
                subscriber=common_v1_contact_pb2.ContactInfo(
                    preferred_channel=request.details.contact.preferred_channel
                )
            )
            async for chunk_1 in deps.clients.metrics_metric_series.WatchMetricSerieses(
                outgoing_1,
                timeout=deps.settings.timeout
            ):
                response_1 = chunk_1
            outgoing_2 = anomalies_v1_detector_query_service_pb2.FindDetectorsRequest(
                context=request.context,
                filter=anomalies_v1_detector_query_service_pb2.FindDetectorsRequest.Filter(
                    created_after=request.analytics_event.occurred_at
                )
            )
            response_2 = cast(anomalies_v1_detector_query_service_pb2.FindDetectorsResponse, await deps.bus.request(
                'acme.analytics.v1.AnalyticsEventValidationService/LintAnalyticsEvents/2', outgoing_2, deps.settings.timeout,
            ))
            outgoing_3 = modelregistry_v1_registered_model_service_pb2.UpdateRegisteredModelRequest(
                context=request.context,
                registered_model=modelregistry_v1_modelregistry_pb2.RegisteredModel(
                    audit=common_v1_audit_pb2.AuditInfo(created_at=response_0.outcome.effective_at),
                    owner=identity_v1_refs_pb2.UserRef(
                        display_name=request.analytics_event.subject.display_name,
                        email=request.details.contact.email,
                        user_id=request.context.actor.user_id
                    )
                )
            )
            response_3 = await deps.clients.modelregistry_registered_model.UpdateRegisteredModel(
                outgoing_3,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.outcome.status
            if returned_0_0:
                response.outcome.status = returned_0_0
            returned_0_1 = response_0.result.message
            if returned_0_1:
                response.outcome.message = returned_0_1
            returned_2_0 = response_2.result.correlation_id
            if returned_2_0:
                response.result.correlation_id = returned_2_0
            returned_2_1 = response_2.result.status
            if returned_2_1:
                response.outcome.status = returned_2_1
            returned_3_0 = response_3.result.correlation_id
            if returned_3_0:
                response.analytics_event.correlation_id = returned_3_0
            returned_3_1 = response_3.result.message
            if returned_3_1:
                response.result.message = returned_3_1
            echoed_0 = request.analytics_event_id
            response.analytics_event.analytics_event_id = echoed_0
            echoed_1 = request.analytics_event.attributes
            response.analytics_event.attributes.update(echoed_1)
            return response

    async def handle_normalize_analytics_event(
        self,
        request: analytics_v1_analytics_event_validation_service_pb2.NormalizeAnalyticsEventRequest
    ) -> analytics_v1_analytics_event_validation_service_pb2.NormalizeAnalyticsEventResponse:
        """Normalizes an analytics event."""
        deps = self.deps
        response = analytics_v1_analytics_event_validation_service_pb2.NormalizeAnalyticsEventResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('NormalizeAnalyticsEvent', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'NormalizeAnalyticsEvent',
                {'reason': request.reason}
            )
            await deps.repository.save_analytics_event(request.context.tenant_id, request.analytics_event)
            response_0 = modelregistry_v1_registered_model_service_pb2.CloneRegisteredModelResponse()
            outgoing_0 = modelregistry_v1_registered_model_service_pb2.CloneRegisteredModelRequest(
                context=request.context,
                registered_model=modelregistry_v1_modelregistry_pb2.RegisteredModel(
                    owner=identity_v1_refs_pb2.UserRef(email=request.details.contact.email)
                )
            )
            method_name_0 = 'CloneRegisteredModel'
            response_0 = await getattr(
                deps.clients.modelregistry_registered_model,
                method_name_0
            )(outgoing_0, timeout=deps.settings.timeout)
            returned_0_0 = response_0.result.correlation_id
            if returned_0_0:
                response.analytics_event.correlation_id = returned_0_0
            returned_0_1 = response_0.result.details
            response.result.details.update(returned_0_1)
            echoed_0 = request.analytics_event_id
            response.analytics_event.analytics_event_id = echoed_0
            echoed_1 = request.analytics_event.attributes
            response.analytics_event.attributes.update(echoed_1)
            return response

    async def handle_preview_analytics_event(
        self,
        request: analytics_v1_analytics_event_validation_service_pb2.PreviewAnalyticsEventRequest
    ) -> analytics_v1_analytics_event_validation_service_pb2.PreviewAnalyticsEventResponse:
        """Previews an analytics event."""
        deps = self.deps
        response = analytics_v1_analytics_event_validation_service_pb2.PreviewAnalyticsEventResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('PreviewAnalyticsEvent', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'PreviewAnalyticsEvent', {'reason': request.reason})
            await deps.repository.save_analytics_event(request.context.tenant_id, request.analytics_event)
            response_0 = analytics_v1_funnel_calculation_service_pb2.GetFunnelRatesResponse()
            fields_0: dict[str, Any] = {
                'context': request.context,
                'funnel_id': request.analytics_event.subject.funnel_id
            }
            outgoing_0 = analytics_v1_funnel_calculation_service_pb2.GetFunnelRatesRequest(**fields_0)
            response_0 = await deps.clients.analytics_funnel_calculation.GetFunnelRates(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.correlation_id
            if returned_0_0:
                response.analytics_event.correlation_id = returned_0_0
            returned_0_1 = response_0.result.message
            if returned_0_1:
                response.outcome.message = returned_0_1
            echoed_0 = request.analytics_event_id
            response.analytics_event.analytics_event_id = echoed_0
            echoed_1 = request.analytics_event.attributes
            response.analytics_event.attributes.update(echoed_1)
            return response

    async def handle_validate_analytics_event(
        self,
        request: analytics_v1_analytics_event_validation_service_pb2.ValidateAnalyticsEventRequest
    ) -> analytics_v1_analytics_event_validation_service_pb2.ValidateAnalyticsEventResponse:
        """Validates an analytics event."""
        deps = self.deps
        response = analytics_v1_analytics_event_validation_service_pb2.ValidateAnalyticsEventResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ValidateAnalyticsEvent', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'ValidateAnalyticsEvent', {'reason': request.reason})
            await deps.repository.save_analytics_event(request.context.tenant_id, request.analytics_event)
            response_0 = analytics_v1_funnel_calculation_service_pb2.GetFunnelRatesResponse()
            outgoing_0 = analytics_v1_funnel_calculation_service_pb2.GetFunnelRatesRequest(
                context=request.context,
                funnel_id=request.analytics_event.subject.funnel_id
            )
            document_0 = MessageToDict(outgoing_0, preserving_proto_field_name=True)
            outgoing_0 = ParseDict(document_0, analytics_v1_funnel_calculation_service_pb2.GetFunnelRatesRequest())
            response_0 = await deps.clients.analytics_funnel_calculation.GetFunnelRates(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.status
            if returned_0_0:
                response.outcome.status = returned_0_0
            echoed_0 = request.analytics_event_id
            response.analytics_event.analytics_event_id = echoed_0
            echoed_1 = request.analytics_event.occurred_at
            response.analytics_event.occurred_at.CopyFrom(echoed_1)
            return response
