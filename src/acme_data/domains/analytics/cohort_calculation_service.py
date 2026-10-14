"""Computes the figures of a cohort, such as totals, taxes, and estimates."""

from __future__ import annotations

from collections.abc import AsyncIterator
from collections.abc import Awaitable
from collections.abc import Callable
from functools import partial
from typing import Any
from typing import cast
import asyncio
import logging

from google.protobuf.json_format import MessageToDict
from google.protobuf.json_format import ParseDict
import grpc

from acme.analytics.v1 import (
    analytics_event_validation_service_pb2 as analytics_v1_analytics_event_validation_service_pb2,
)
from acme.analytics.v1 import (
    analytics_event_validation_service_pb2_grpc as analytics_v1_analytics_event_validation_service_pb2_grpc,
)
from acme.analytics.v1 import analytics_pb2 as analytics_v1_analytics_pb2
from acme.analytics.v1 import cohort_calculation_service_pb2 as analytics_v1_cohort_calculation_service_pb2
from acme.analytics.v1 import cohort_calculation_service_pb2_grpc as analytics_v1_cohort_calculation_service_pb2_grpc
from acme.analytics.v1 import funnel_calculation_service_pb2 as analytics_v1_funnel_calculation_service_pb2
from acme.analytics.v1 import refs_pb2 as analytics_v1_refs_pb2
from acme.anomalies.v1 import anomalies_pb2 as anomalies_v1_anomalies_pb2
from acme.anomalies.v1 import detector_validation_service_pb2 as anomalies_v1_detector_validation_service_pb2
from acme.authorization.v1 import access_policy_query_service_pb2 as authorization_v1_access_policy_query_service_pb2
from acme.authorization.v1 import access_policy_service_pb2 as authorization_v1_access_policy_service_pb2
from acme.authorization.v1 import authorization_pb2 as authorization_v1_authorization_pb2
from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.configuration.v1 import (
    config_set_calculation_service_pb2 as configuration_v1_config_set_calculation_service_pb2,
)
from acme.configuration.v1 import configuration_pb2 as configuration_v1_configuration_pb2
from acme.datasets.v1 import data_schema_calculation_service_pb2 as datasets_v1_data_schema_calculation_service_pb2
from acme.datasets.v1 import datasets_pb2 as datasets_v1_datasets_pb2
from acme.featureflags.v1 import (
    feature_flag_validation_service_pb2 as featureflags_v1_feature_flag_validation_service_pb2,
)
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.metrics.v1 import metric_alert_notification_service_pb2 as metrics_v1_metric_alert_notification_service_pb2

from acme_data.domains.analytics.adapters import CohortCalculationExplainCohortCalculation1Adapter
from acme_data.domains.analytics.adapters import CohortCalculationExplainCohortCalculation1Port
from acme_data.domains.analytics.adapters import CohortCalculationQuoteCohort0Adapter
from acme_data.domains.analytics.dependencies import Dependencies
from acme_data.domains.analytics.models import CohortCalculationCompareCohortOptions0Command
from acme_data.domains.analytics.models import to_cohort_calculation_compare_cohort_options0_command
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_id
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class CohortCalculationServicer(analytics_v1_cohort_calculation_service_pb2_grpc.CohortCalculationServiceServicer):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    async def CalculateCohort(
        self, request: analytics_v1_cohort_calculation_service_pb2.CalculateCohortRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_cohort_calculation_service_pb2.CalculateCohortResponse:
        """Calculates a cohort."""
        return await self.handle_calculate_cohort(request)

    @rpc_errors
    async def CompareCohortOptions(
        self, request: analytics_v1_cohort_calculation_service_pb2.CompareCohortOptionsRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_cohort_calculation_service_pb2.CompareCohortOptionsResponse:
        """Compares a cohort."""
        return await self.handle_compare_cohort_options(request)

    @rpc_errors
    async def EstimateCohort(
        self, request: analytics_v1_cohort_calculation_service_pb2.EstimateCohortRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_cohort_calculation_service_pb2.EstimateCohortResponse:
        """Estimates a cohort."""
        return await self.handle_estimate_cohort(request)

    @rpc_errors
    async def ExplainCohortCalculation(
        self, request: analytics_v1_cohort_calculation_service_pb2.ExplainCohortCalculationRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_cohort_calculation_service_pb2.ExplainCohortCalculationResponse:
        """Explains a cohort."""
        return await self.handle_explain_cohort_calculation(request)

    @rpc_errors
    @retry_transient
    async def GetCohortRates(
        self, request: analytics_v1_cohort_calculation_service_pb2.GetCohortRatesRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_cohort_calculation_service_pb2.GetCohortRatesResponse:
        """Returns a cohort."""
        return await self.handle_get_cohort_rates(request)

    @rpc_errors
    async def QuoteCohort(
        self, request: analytics_v1_cohort_calculation_service_pb2.QuoteCohortRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_cohort_calculation_service_pb2.QuoteCohortResponse:
        """Quotes a cohort."""
        return await self.handle_quote_cohort(request)

    @rpc_errors
    async def RecalculateCohorts(
        self, request: analytics_v1_cohort_calculation_service_pb2.RecalculateCohortsRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_cohort_calculation_service_pb2.RecalculateCohortsResponse:
        """Recalculates a cohort."""
        return await self.handle_recalculate_cohorts(request)

    @rpc_errors
    async def SimulateCohort(
        self, request: analytics_v1_cohort_calculation_service_pb2.SimulateCohortRequest, context: grpc.aio.ServicerContext,
    ) -> analytics_v1_cohort_calculation_service_pb2.SimulateCohortResponse:
        """Simulates a cohort."""
        return await self.handle_simulate_cohort(request)

    async def handle_calculate_cohort(
        self,
        request: analytics_v1_cohort_calculation_service_pb2.CalculateCohortRequest
    ) -> analytics_v1_cohort_calculation_service_pb2.CalculateCohortResponse:
        """Calculates a cohort."""
        deps = self.deps
        response = analytics_v1_cohort_calculation_service_pb2.CalculateCohortResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CalculateCohort', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'CalculateCohort', {'reason': request.reason})
            await deps.repository.save_cohort(request.context.tenant_id, request.cohort)
            response_0 = analytics_v1_analytics_event_validation_service_pb2.PreviewAnalyticsEventResponse()
            response_1 = analytics_v1_funnel_calculation_service_pb2.CalculateFunnelResponse()
            outgoing_0 = analytics_v1_analytics_event_validation_service_pb2.PreviewAnalyticsEventRequest(
                analytics_event=analytics_v1_analytics_pb2.AnalyticsEvent(
                    subject=analytics_v1_refs_pb2.FunnelRef(version=request.cohort.version)
                ),
                context=request.context,
                details=analytics_v1_analytics_event_validation_service_pb2.PreviewAnalyticsEventRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(email=request.cohort.owner.email)
                ),
                reason=request.cohort.block.reason
            )
            registered_0 = cast(
                analytics_v1_analytics_event_validation_service_pb2_grpc.AnalyticsEventValidationServiceStub,
                deps.clients.registry['acme.analytics.v1.AnalyticsEventValidationService']
            )
            response_0 = await registered_0.PreviewAnalyticsEvent(outgoing_0, timeout=deps.settings.timeout)
            outgoing_1 = analytics_v1_funnel_calculation_service_pb2.CalculateFunnelRequest()
            outgoing_1.context.CopyFrom(request.context)
            outgoing_1.details.destination.lines.extend(list(request.details.destination.lines))
            outgoing_1.funnel.owner.display_name = request.cohort.owner.display_name
            if request.cohort.WhichOneof('action') == 'discount':
                outgoing_1.funnel.discount.percent = request.cohort.discount.percent
            outgoing_1.funnel.audit.created_at.CopyFrom(request.cohort.audit.created_at)
            response_1 = await deps.clients.analytics_funnel_calculation.CalculateFunnel(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.outcome.message
            if returned_0_0:
                response.result.message = returned_0_0
            returned_0_1 = response_0.analytics_event.correlation_id
            if returned_0_1:
                response.result.correlation_id = returned_0_1
            returned_1_0 = response_1.funnel.description
            if returned_1_0:
                response.cohort.description = returned_1_0
            returned_1_1 = response_1.result.status
            if returned_1_1:
                response.result.status = returned_1_1
            echoed_0 = request.cohort_id
            response.cohort.cohort_id = echoed_0
            echoed_1 = request.cohort.parameters
            response.cohort.parameters.update(echoed_1)
            return response

    async def handle_compare_cohort_options(
        self,
        request: analytics_v1_cohort_calculation_service_pb2.CompareCohortOptionsRequest
    ) -> analytics_v1_cohort_calculation_service_pb2.CompareCohortOptionsResponse:
        """Compares a cohort."""
        deps = self.deps
        response = analytics_v1_cohort_calculation_service_pb2.CompareCohortOptionsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CompareCohortOptions', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'CompareCohortOptions', {'reason': request.reason})
            await deps.repository.save_cohort(request.context.tenant_id, request.cohort)
            response_0 = featureflags_v1_feature_flag_validation_service_pb2.CheckFeatureFlagEligibilityResponse()
            response_1 = configuration_v1_config_set_calculation_service_pb2.EstimateConfigSetResponse()
            command_0 = CohortCalculationCompareCohortOptions0Command.model_validate(
                {'context': request.context, 'feature_flag_audit_created_by': request.cohort.audit.created_by}
            )
            outgoing_0 = to_cohort_calculation_compare_cohort_options0_command(command_0)
            response_0 = await deps.clients.featureflags_feature_flag_validation.CheckFeatureFlagEligibility(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = configuration_v1_config_set_calculation_service_pb2.EstimateConfigSetRequest(
                config_set=configuration_v1_configuration_pb2.ConfigSet(
                    children=[
                        configuration_v1_configuration_pb2.ConfigSet(
                            children=[
                                configuration_v1_configuration_pb2.ConfigSet(
                                    audit=common_v1_audit_pb2.AuditInfo(
                                        updated_by=response_0.feature_flag.audit.updated_by
                                    ),
                                    location=common_v1_address_pb2.PostalAddress(
                                        region=request.details.destination.region
                                    )
                                )
                            ]
                        )
                    ]
                ),
                context=request.context
            )
            send_1 = partial(
                deps.clients.configuration_config_set_calculation.EstimateConfigSet,
                timeout=deps.settings.timeout
            )
            response_1 = await send_1(outgoing_1)
            returned_0_0 = response_0.feature_flag.audit.created_at
            if returned_0_0.ListFields():
                response.cohort.audit.created_at.MergeFrom(returned_0_0)
            returned_0_1 = response_0.feature_flag.owner.user_id
            if returned_0_1:
                response.cohort.owner.user_id = returned_0_1
            returned_1_0 = response_1.result.status
            if returned_1_0:
                response.result.status = returned_1_0
            returned_1_1 = response_1.result.reference_ids
            response.result.reference_ids.extend(returned_1_1)
            echoed_0 = request.cohort_id
            response.cohort.cohort_id = echoed_0
            echoed_1 = request.cohort.description
            response.cohort.description = echoed_1
            return response

    async def handle_estimate_cohort(
        self,
        request: analytics_v1_cohort_calculation_service_pb2.EstimateCohortRequest
    ) -> analytics_v1_cohort_calculation_service_pb2.EstimateCohortResponse:
        """Estimates a cohort."""
        deps = self.deps
        response = analytics_v1_cohort_calculation_service_pb2.EstimateCohortResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('EstimateCohort', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'EstimateCohort', {'reason': request.reason})
            await deps.repository.save_cohort(request.context.tenant_id, request.cohort)
            response_0 = analytics_v1_funnel_calculation_service_pb2.SimulateFunnelResponse()
            callbacks_0: list[
                Callable[[], Awaitable[analytics_v1_funnel_calculation_service_pb2.SimulateFunnelResponse]]
            ] = []
            for item_0 in request.cohort.conditions:
                outgoing_0 = analytics_v1_funnel_calculation_service_pb2.SimulateFunnelRequest(
                    context=request.context,
                    funnel=analytics_v1_analytics_pb2.Funnel(
                        conditions=[analytics_v1_analytics_pb2.FunnelCondition(attribute=item_0.attribute)]
                    )
                )
                async def send_0(
                    payload: analytics_v1_funnel_calculation_service_pb2.SimulateFunnelRequest = outgoing_0
                ) -> analytics_v1_funnel_calculation_service_pb2.SimulateFunnelResponse:
                    return await deps.clients.analytics_funnel_calculation.SimulateFunnel(
                        payload,
                        timeout=deps.settings.timeout
                    )
                callbacks_0.append(send_0)
            for callback_0 in callbacks_0:
                response_0 = await callback_0()
            echoed_0 = request.cohort_id
            response.cohort.cohort_id = echoed_0
            echoed_1 = request.cohort.version
            response.cohort.version = echoed_1
            return response

    async def handle_explain_cohort_calculation(
        self,
        request: analytics_v1_cohort_calculation_service_pb2.ExplainCohortCalculationRequest
    ) -> analytics_v1_cohort_calculation_service_pb2.ExplainCohortCalculationResponse:
        """Explains a cohort."""
        deps = self.deps
        response = analytics_v1_cohort_calculation_service_pb2.ExplainCohortCalculationResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ExplainCohortCalculation', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ExplainCohortCalculation',
                {'reason': request.reason}
            )
            await deps.repository.save_cohort(request.context.tenant_id, request.cohort)
            response_0 = authorization_v1_access_policy_query_service_pb2.ResolveAccessPoliciesResponse()
            response_1 = datasets_v1_data_schema_calculation_service_pb2.RecalculateDataSchemasResponse()
            outgoing_0 = authorization_v1_access_policy_query_service_pb2.ResolveAccessPoliciesRequest()
            outgoing_0.context.CopyFrom(request.context)
            outgoing_0.context.tenant_id = tenant_id.get()
            response_0 = await deps.clients.authorization_access_policy_query.ResolveAccessPolicies(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = datasets_v1_data_schema_calculation_service_pb2.RecalculateDataSchemasRequest(
                context=request.context,
                data_schema=datasets_v1_datasets_pb2.DataSchema(
                    children=[
                        datasets_v1_datasets_pb2.DataSchema(
                            audit=common_v1_audit_pb2.AuditInfo(updated_at=request.cohort.audit.updated_at),
                            children=[
                                datasets_v1_datasets_pb2.DataSchema(
                                    audit=common_v1_audit_pb2.AuditInfo(
                                        created_at=request.cohort.audit.created_at,
                                        etag=request.cohort.audit.etag
                                    ),
                                    manager=identity_v1_refs_pb2.UserRef(email=request.details.contact.email)
                                )
                            ]
                        )
                    ]
                )
            )
            port_1: CohortCalculationExplainCohortCalculation1Port = CohortCalculationExplainCohortCalculation1Adapter(
                deps.clients.datasets_data_schema_calculation,
                deps.settings.timeout
            )
            response_1 = await port_1.execute(outgoing_1)
            returned_0_0 = response_0.result.correlation_id
            if returned_0_0:
                response.result.correlation_id = returned_0_0
            returned_0_1 = response_0.result.status
            if returned_0_1:
                response.outcome.status = returned_0_1
            returned_1_0 = response_1.result.reference_ids
            response.result.reference_ids.extend(returned_1_0)
            returned_1_1 = response_1.result.correlation_id
            if returned_1_1:
                response.result.correlation_id = returned_1_1
            echoed_0 = request.cohort_id
            response.cohort.cohort_id = echoed_0
            echoed_1 = request.cohort.effective
            response.cohort.effective.CopyFrom(echoed_1)
            return response

    async def handle_get_cohort_rates(
        self,
        request: analytics_v1_cohort_calculation_service_pb2.GetCohortRatesRequest
    ) -> analytics_v1_cohort_calculation_service_pb2.GetCohortRatesResponse:
        """Returns a cohort."""
        deps = self.deps
        response = analytics_v1_cohort_calculation_service_pb2.GetCohortRatesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('GetCohortRates', extra={'fields': {'domain': 'analytics'}})
            await deps.repository.audit(request.context.tenant_id, 'GetCohortRates', {})
            response_0 = anomalies_v1_detector_validation_service_pb2.ValidateDetectorResponse()
            outgoing_0 = anomalies_v1_detector_validation_service_pb2.ValidateDetectorRequest(
                context=request.context,
                details=anomalies_v1_detector_validation_service_pb2.ValidateDetectorRequest.Details(
                    locale=request.context.locale
                ),
                detector=anomalies_v1_anomalies_pb2.Detector(
                    owner=identity_v1_refs_pb2.UserRef(
                        email=request.context.actor.email,
                        user_id=request.context.actor.user_id
                    )
                )
            )
            response_0 = await deps.clients.anomalies_detector_validation.ValidateDetector(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.detector.audit.etag
            if returned_0_0:
                response.cohort.audit.etag = returned_0_0
            echoed_0 = request.cohort_id
            response.cohort.cohort_id = echoed_0
            return response

    async def handle_quote_cohort(
        self,
        request: analytics_v1_cohort_calculation_service_pb2.QuoteCohortRequest
    ) -> analytics_v1_cohort_calculation_service_pb2.QuoteCohortResponse:
        """Quotes a cohort."""
        deps = self.deps
        response = analytics_v1_cohort_calculation_service_pb2.QuoteCohortResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('QuoteCohort', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'QuoteCohort', {'reason': request.reason})
            await deps.repository.save_cohort(request.context.tenant_id, request.cohort)
            response_0 = analytics_v1_analytics_event_validation_service_pb2.LintAnalyticsEventsResponse()
            response_1 = datasets_v1_data_schema_calculation_service_pb2.CompareDataSchemaOptionsResponse()
            response_2 = analytics_v1_analytics_event_validation_service_pb2.ExplainAnalyticsEventDecisionResponse()
            response_3 = authorization_v1_access_policy_service_pb2.CloneAccessPolicyResponse()
            outgoing_0 = analytics_v1_analytics_event_validation_service_pb2.LintAnalyticsEventsRequest(
                analytics_event=analytics_v1_analytics_pb2.AnalyticsEvent(
                    subject=analytics_v1_refs_pb2.FunnelRef(display_name=request.cohort.owner.display_name)
                ),
                context=request.context,
                details=analytics_v1_analytics_event_validation_service_pb2.LintAnalyticsEventsRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(email=request.cohort.owner.email)
                )
            )
            response_0 = await CohortCalculationQuoteCohort0Adapter(
                deps.clients.analytics_analytics_event_validation,
                deps.settings.timeout
            )(outgoing_0)
            outgoing_1 = datasets_v1_data_schema_calculation_service_pb2.CompareDataSchemaOptionsRequest(
                context=request.context,
                data_schema=datasets_v1_datasets_pb2.DataSchema(
                    children=[
                        datasets_v1_datasets_pb2.DataSchema(
                            children=[
                                datasets_v1_datasets_pb2.DataSchema(
                                    location=common_v1_address_pb2.PostalAddress(
                                        country_code=request.details.destination.country_code
                                    ),
                                    manager=identity_v1_refs_pb2.UserRef(display_name=request.cohort.owner.display_name)
                                )
                            ]
                        )
                    ]
                )
            )
            response_1 = cast(datasets_v1_data_schema_calculation_service_pb2.CompareDataSchemaOptionsResponse, await deps.bus.request(
                'acme.analytics.v1.CohortCalculationService/QuoteCohort/1', outgoing_1, deps.settings.timeout,
            ))
            outgoing_2 = analytics_v1_analytics_event_validation_service_pb2.ExplainAnalyticsEventDecisionRequest(
                context=request.context,
                details=analytics_v1_analytics_event_validation_service_pb2.ExplainAnalyticsEventDecisionRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(email=request.cohort.owner.email)
                )
            )
            response_2 = await deps.clients.analytics_analytics_event_validation.ExplainAnalyticsEventDecision(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            outgoing_3 = authorization_v1_access_policy_service_pb2.CloneAccessPolicyRequest(
                access_policy=authorization_v1_authorization_pb2.AccessPolicy(
                    audit=common_v1_audit_pb2.AuditInfo(created_at=response_1.data_schema.audit.created_at),
                    owner=identity_v1_refs_pb2.UserRef(
                        display_name=response_2.analytics_event.subject.display_name,
                        email=response_1.data_schema.manager.email,
                        user_id=response_1.data_schema.manager.user_id
                    )
                ),
                context=request.context
            )
            method_name_3 = 'CloneAccessPolicy'
            response_3 = await getattr(
                deps.clients.authorization_access_policy,
                method_name_3
            )(outgoing_3, timeout=deps.settings.timeout)
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.result.message = returned_0_0
            returned_1_0 = response_1.data_schema.name
            if returned_1_0:
                response.cohort.name = returned_1_0
            returned_2_0 = response_2.result.details
            response.result.details.update(returned_2_0)
            returned_3_0 = response_3.access_policy.name
            if returned_3_0:
                response.cohort.name = returned_3_0
            returned_3_1 = response_3.access_policy.audit.created_at
            if returned_3_1.ListFields():
                response.cohort.audit.created_at.MergeFrom(returned_3_1)
            echoed_0 = request.cohort_id
            response.cohort.cohort_id = echoed_0
            echoed_1 = request.cohort.version
            response.cohort.version = echoed_1
            return response

    async def handle_recalculate_cohorts(
        self,
        request: analytics_v1_cohort_calculation_service_pb2.RecalculateCohortsRequest
    ) -> analytics_v1_cohort_calculation_service_pb2.RecalculateCohortsResponse:
        """Recalculates a cohort."""
        deps = self.deps
        response = analytics_v1_cohort_calculation_service_pb2.RecalculateCohortsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('RecalculateCohorts', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'RecalculateCohorts', {'reason': request.reason})
            await deps.repository.save_cohort(request.context.tenant_id, request.cohort)
            response_0 = analytics_v1_funnel_calculation_service_pb2.SimulateFunnelResponse()
            fields_0: dict[str, Any] = {
                'context': request.context,
                'funnel': {
                    'audit': {'updated_at': request.cohort.audit.updated_at},
                    'route': {'weight': request.cohort.route.weight}
                }
            }
            outgoing_0 = analytics_v1_funnel_calculation_service_pb2.SimulateFunnelRequest(**fields_0)
            response_0 = await deps.clients.analytics_funnel_calculation.SimulateFunnel(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.funnel.audit.created_at
            if returned_0_0.ListFields():
                response.cohort.audit.created_at.MergeFrom(returned_0_0)
            echoed_0 = request.cohort_id
            response.cohort.cohort_id = echoed_0
            echoed_1 = request.details.currency_code
            response.breakdown.currency_code = echoed_1
            return response

    async def handle_simulate_cohort(
        self,
        request: analytics_v1_cohort_calculation_service_pb2.SimulateCohortRequest
    ) -> analytics_v1_cohort_calculation_service_pb2.SimulateCohortResponse:
        """Simulates a cohort."""
        deps = self.deps
        response = analytics_v1_cohort_calculation_service_pb2.SimulateCohortResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SimulateCohort', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'SimulateCohort', {'reason': request.reason})
            await deps.repository.save_cohort(request.context.tenant_id, request.cohort)
            response_0 = metrics_v1_metric_alert_notification_service_pb2.SubscribeMetricAlertUpdatesResponse()
            outgoing_0 = metrics_v1_metric_alert_notification_service_pb2.SubscribeMetricAlertUpdatesRequest(
                context=request.context,
                details=metrics_v1_metric_alert_notification_service_pb2.SubscribeMetricAlertUpdatesRequest.Details(
                    recipient=common_v1_contact_pb2.ContactInfo(email=request.cohort.owner.email)
                )
            )
            document_0 = MessageToDict(outgoing_0, preserving_proto_field_name=True)
            outgoing_0 = ParseDict(
                document_0,
                metrics_v1_metric_alert_notification_service_pb2.SubscribeMetricAlertUpdatesRequest()
            )
            response_0 = await deps.clients.metrics_metric_alert_notification.SubscribeMetricAlertUpdates(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.metric_alert.owner
            if returned_0_0.ListFields():
                response.cohort.owner.MergeFrom(returned_0_0)
            echoed_0 = request.cohort_id
            response.cohort.cohort_id = echoed_0
            echoed_1 = request.cohort.name
            response.cohort.name = echoed_1
            return response
