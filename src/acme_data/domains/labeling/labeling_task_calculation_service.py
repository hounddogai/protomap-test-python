"""Computes the figures of a labeling task, such as totals, taxes, and estimates."""

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
from google.protobuf.json_format import MessageToJson
from google.protobuf.json_format import Parse
from google.protobuf.json_format import ParseDict
import grpc

from acme.anomalies.v1 import (
    anomaly_feedback_calculation_service_pb2 as anomalies_v1_anomaly_feedback_calculation_service_pb2,
)
from acme.audit.v1 import audit_event_service_pb2 as audit_v1_audit_event_service_pb2
from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.configuration.v1 import config_set_query_service_pb2 as configuration_v1_config_set_query_service_pb2
from acme.featureflags.v1 import feature_flag_query_service_pb2 as featureflags_v1_feature_flag_query_service_pb2
from acme.featurestore.v1 import (
    feature_value_calculation_service_pb2 as featurestore_v1_feature_value_calculation_service_pb2,
)
from acme.featurestore.v1 import (
    feature_view_calculation_service_pb2 as featurestore_v1_feature_view_calculation_service_pb2,
)
from acme.featurestore.v1 import featurestore_pb2 as featurestore_v1_featurestore_pb2
from acme.identity.v1 import identity_pb2 as identity_v1_identity_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.identity.v1 import user_validation_service_pb2 as identity_v1_user_validation_service_pb2
from acme.labeling.v1 import labeling_task_calculation_service_pb2 as labeling_v1_labeling_task_calculation_service_pb2
from acme.labeling.v1 import (
    labeling_task_calculation_service_pb2_grpc as labeling_v1_labeling_task_calculation_service_pb2_grpc,
)
from acme.lineage.v1 import impact_validation_service_pb2 as lineage_v1_impact_validation_service_pb2
from acme.lineage.v1 import lineage_pb2 as lineage_v1_lineage_pb2
from acme.metrics.v1 import dashboard_sync_service_pb2 as metrics_v1_dashboard_sync_service_pb2
from acme.metrics.v1 import metric_series_history_service_pb2 as metrics_v1_metric_series_history_service_pb2
from acme.metrics.v1 import metric_series_query_service_pb2 as metrics_v1_metric_series_query_service_pb2
from acme.metrics.v1 import metrics_pb2 as metrics_v1_metrics_pb2
from acme.metrics.v1 import refs_pb2 as metrics_v1_refs_pb2
from acme.modelregistry.v1 import (
    deployment_calculation_service_pb2 as modelregistry_v1_deployment_calculation_service_pb2,
)
from acme.modelregistry.v1 import (
    deployment_validation_service_pb2 as modelregistry_v1_deployment_validation_service_pb2,
)
from acme.modelregistry.v1 import model_version_query_service_pb2 as modelregistry_v1_model_version_query_service_pb2
from acme.modelregistry.v1 import (
    model_version_query_service_pb2_grpc as modelregistry_v1_model_version_query_service_pb2_grpc,
)
from acme.modelregistry.v1 import modelregistry_pb2 as modelregistry_v1_modelregistry_pb2
from acme.modelregistry.v1 import registered_model_service_pb2 as modelregistry_v1_registered_model_service_pb2
from acme.modelregistry.v1 import (
    registered_model_validation_service_pb2 as modelregistry_v1_registered_model_validation_service_pb2,
)

from acme_data.domains.labeling import hooks
from acme_data.domains.labeling.dependencies import Dependencies
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import run_steps
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class LabelingTaskCalculationServicer(
    labeling_v1_labeling_task_calculation_service_pb2_grpc.LabelingTaskCalculationServiceServicer
):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    async def CalculateLabelingTask(
        self, request: labeling_v1_labeling_task_calculation_service_pb2.CalculateLabelingTaskRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_labeling_task_calculation_service_pb2.CalculateLabelingTaskResponse:
        """Calculates a labeling task."""
        return await self.handle_calculate_labeling_task(request)

    @rpc_errors
    async def CompareLabelingTaskOptions(
        self, request: labeling_v1_labeling_task_calculation_service_pb2.CompareLabelingTaskOptionsRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_labeling_task_calculation_service_pb2.CompareLabelingTaskOptionsResponse:
        """Compares a labeling task."""
        return await self.handle_compare_labeling_task_options(request)

    @rpc_errors
    async def EstimateLabelingTask(
        self, request: labeling_v1_labeling_task_calculation_service_pb2.EstimateLabelingTaskRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_labeling_task_calculation_service_pb2.EstimateLabelingTaskResponse:
        """Estimates a labeling task."""
        return await self.handle_estimate_labeling_task(request)

    @rpc_errors
    async def ExplainLabelingTaskCalculation(
        self, request: labeling_v1_labeling_task_calculation_service_pb2.ExplainLabelingTaskCalculationRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_labeling_task_calculation_service_pb2.ExplainLabelingTaskCalculationResponse:
        """Explains a labeling task."""
        return await self.handle_explain_labeling_task_calculation(request)

    @rpc_errors
    @retry_transient
    async def GetLabelingTaskRates(
        self, request: labeling_v1_labeling_task_calculation_service_pb2.GetLabelingTaskRatesRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_labeling_task_calculation_service_pb2.GetLabelingTaskRatesResponse:
        """Returns a labeling task."""
        return await self.handle_get_labeling_task_rates(request)

    @rpc_errors
    async def QuoteLabelingTask(
        self, request: labeling_v1_labeling_task_calculation_service_pb2.QuoteLabelingTaskRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_labeling_task_calculation_service_pb2.QuoteLabelingTaskResponse:
        """Quotes a labeling task."""
        return await self.handle_quote_labeling_task(request)

    @rpc_errors
    async def RecalculateLabelingTasks(
        self, request: labeling_v1_labeling_task_calculation_service_pb2.RecalculateLabelingTasksRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_labeling_task_calculation_service_pb2.RecalculateLabelingTasksResponse:
        """Recalculates a labeling task."""
        return await self.handle_recalculate_labeling_tasks(request)

    @rpc_errors
    async def SimulateLabelingTask(
        self, request: labeling_v1_labeling_task_calculation_service_pb2.SimulateLabelingTaskRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_labeling_task_calculation_service_pb2.SimulateLabelingTaskResponse:
        """Simulates a labeling task."""
        return await self.handle_simulate_labeling_task(request)

    async def handle_calculate_labeling_task(
        self,
        request: labeling_v1_labeling_task_calculation_service_pb2.CalculateLabelingTaskRequest
    ) -> labeling_v1_labeling_task_calculation_service_pb2.CalculateLabelingTaskResponse:
        """Calculates a labeling task."""
        deps = self.deps
        response = labeling_v1_labeling_task_calculation_service_pb2.CalculateLabelingTaskResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CalculateLabelingTask', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'CalculateLabelingTask', {'reason': request.reason})
            await deps.repository.save_labeling_task(request.context.tenant_id, request.labeling_task)
            response_0 = modelregistry_v1_deployment_calculation_service_pb2.RecalculateDeploymentsResponse()
            response_1 = identity_v1_user_validation_service_pb2.ExplainUserDecisionResponse()
            response_2 = modelregistry_v1_registered_model_service_pb2.CloneRegisteredModelResponse()
            outgoing_0 = modelregistry_v1_deployment_calculation_service_pb2.RecalculateDeploymentsRequest(
                context=request.context,
                deployment=modelregistry_v1_modelregistry_pb2.Deployment(
                    participants=[
                        modelregistry_v1_modelregistry_pb2.DeploymentParticipant(
                            contact=common_v1_contact_pb2.ContactInfo(
                                preferred_channel=request.labeling_task.requester.preferred_channel
                            )
                        )
                    ]
                ),
                details=modelregistry_v1_deployment_calculation_service_pb2.RecalculateDeploymentsRequest.Details(
                    destination=common_v1_address_pb2.PostalAddress(locality=request.details.destination.locality)
                )
            )
            document_0 = MessageToDict(outgoing_0, preserving_proto_field_name=True)
            outgoing_0 = ParseDict(
                document_0,
                modelregistry_v1_deployment_calculation_service_pb2.RecalculateDeploymentsRequest()
            )
            response_0 = await deps.clients.modelregistry_deployment_calculation.RecalculateDeployments(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = identity_v1_user_validation_service_pb2.ExplainUserDecisionRequest(
                context=request.context,
                details=identity_v1_user_validation_service_pb2.ExplainUserDecisionRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(email=response_0.deployment.organizer.email)
                ),
                user=identity_v1_identity_pb2.User(
                    relationship_manager=identity_v1_refs_pb2.UserRef(
                        display_name=request.labeling_task.assignee.display_name
                    )
                )
            )
            document_1 = MessageToJson(outgoing_1, preserving_proto_field_name=True)
            outgoing_1 = Parse(document_1, identity_v1_user_validation_service_pb2.ExplainUserDecisionRequest())
            response_1 = await deps.clients.identity_user_validation.ExplainUserDecision(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            requests_2: list[modelregistry_v1_registered_model_service_pb2.CloneRegisteredModelRequest] = []
            for item_2 in request.labeling_task.comments:
                outgoing_2 = modelregistry_v1_registered_model_service_pb2.CloneRegisteredModelRequest(
                    context=request.context,
                    registered_model=modelregistry_v1_modelregistry_pb2.RegisteredModel(
                        audit=common_v1_audit_pb2.AuditInfo(created_at=item_2.created_at)
                    )
                )
                requests_2.append(outgoing_2)
            replies_2 = await asyncio.gather(*(
                deps.clients.modelregistry_registered_model.CloneRegisteredModel(
                    entry,
                    timeout=deps.settings.timeout
                ) for entry in requests_2
            ))
            if replies_2:
                response_2 = replies_2[-1]
            returned_0_0 = response_0.breakdown.currency_code
            if returned_0_0:
                response.breakdown.currency_code = returned_0_0
            returned_1_0 = response_1.user.audit.created_by
            if returned_1_0:
                response.labeling_task.audit.created_by = returned_1_0
            returned_1_1 = response_1.user.relationship_manager.email
            if returned_1_1:
                response.labeling_task.assignee.email = returned_1_1
            echoed_0 = request.labeling_task_id
            response.labeling_task.labeling_task_id = echoed_0
            echoed_1 = request.labeling_task.priority
            response.labeling_task.priority = echoed_1
            return response

    async def handle_compare_labeling_task_options(
        self,
        request: labeling_v1_labeling_task_calculation_service_pb2.CompareLabelingTaskOptionsRequest
    ) -> labeling_v1_labeling_task_calculation_service_pb2.CompareLabelingTaskOptionsResponse:
        """Compares a labeling task."""
        deps = self.deps
        response = labeling_v1_labeling_task_calculation_service_pb2.CompareLabelingTaskOptionsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CompareLabelingTaskOptions', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'CompareLabelingTaskOptions',
                {'reason': request.reason}
            )
            await deps.repository.save_labeling_task(request.context.tenant_id, request.labeling_task)
            response_0 = featurestore_v1_feature_view_calculation_service_pb2.CompareFeatureViewOptionsResponse()
            response_1 = modelregistry_v1_model_version_query_service_pb2.SuggestModelVersionsResponse()
            response_2 = metrics_v1_metric_series_query_service_pb2.SuggestMetricSeriesesResponse()
            outgoing_0 = featurestore_v1_feature_view_calculation_service_pb2.CompareFeatureViewOptionsRequest(
                context=request.context,
                details=featurestore_v1_feature_view_calculation_service_pb2.CompareFeatureViewOptionsRequest.Details(
                    destination=common_v1_address_pb2.PostalAddress(
                        country_code=request.details.destination.country_code
                    )
                ),
                feature_view=featurestore_v1_featurestore_pb2.FeatureView(
                    address=common_v1_address_pb2.PostalAddress(locality=request.details.destination.locality),
                    audit=common_v1_audit_pb2.AuditInfo(created_by=request.labeling_task.audit.created_by)
                )
            )
            envelope_0 = AnyMessage()
            envelope_0.Pack(outgoing_0)
            outgoing_0 = featurestore_v1_feature_view_calculation_service_pb2.CompareFeatureViewOptionsRequest()
            if not envelope_0.Unpack(outgoing_0):
                raise ValueError("partner envelope contains the wrong request type")
            response_0 = await deps.clients.featurestore_feature_view_calculation.CompareFeatureViewOptions(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = modelregistry_v1_model_version_query_service_pb2.SuggestModelVersionsRequest(
                context=request.context,
                filter=modelregistry_v1_model_version_query_service_pb2.SuggestModelVersionsRequest.Filter(
                    created_after=request.labeling_task.audit.created_at,
                    region=request.details.destination.region
                )
            )
            registered_1 = cast(
                modelregistry_v1_model_version_query_service_pb2_grpc.ModelVersionQueryServiceStub,
                deps.clients.registry['acme.modelregistry.v1.ModelVersionQueryService']
            )
            response_1 = await registered_1.SuggestModelVersions(outgoing_1, timeout=deps.settings.timeout)
            callbacks_2: list[
                Callable[[], Awaitable[metrics_v1_metric_series_query_service_pb2.SuggestMetricSeriesesResponse]]
            ] = []
            for item_2 in request.labeling_task.history:
                outgoing_2 = metrics_v1_metric_series_query_service_pb2.SuggestMetricSeriesesRequest(
                    context=request.context,
                    filter=metrics_v1_metric_series_query_service_pb2.SuggestMetricSeriesesRequest.Filter(
                        created_after=item_2.changed_at,
                        owner_id=request.labeling_task.sla.policy_id,
                        region=response_0.feature_view.address.region
                    )
                )
                async def send_2(
                    payload: metrics_v1_metric_series_query_service_pb2.SuggestMetricSeriesesRequest = outgoing_2
                ) -> metrics_v1_metric_series_query_service_pb2.SuggestMetricSeriesesResponse:
                    return await deps.clients.metrics_metric_series_query.SuggestMetricSerieses(
                        payload,
                        timeout=deps.settings.timeout
                    )
                callbacks_2.append(send_2)
            for callback_2 in callbacks_2:
                response_2 = await callback_2()
            returned_0_0 = response_0.feature_view.audit.updated_at
            if returned_0_0.ListFields():
                response.labeling_task.audit.updated_at.MergeFrom(returned_0_0)
            returned_0_1 = response_0.feature_view.audit.etag
            if returned_0_1:
                response.labeling_task.audit.etag = returned_0_1
            returned_1_0 = response_1.result.correlation_id
            if returned_1_0:
                response.result.correlation_id = returned_1_0
            returned_1_1 = response_1.result.status
            if returned_1_1:
                response.result.status = returned_1_1
            echoed_0 = request.labeling_task_id
            response.labeling_task.labeling_task_id = echoed_0
            echoed_1 = request.labeling_task.status
            response.labeling_task.status = echoed_1
            return response

    async def handle_estimate_labeling_task(
        self,
        request: labeling_v1_labeling_task_calculation_service_pb2.EstimateLabelingTaskRequest
    ) -> labeling_v1_labeling_task_calculation_service_pb2.EstimateLabelingTaskResponse:
        """Estimates a labeling task."""
        deps = self.deps
        response = labeling_v1_labeling_task_calculation_service_pb2.EstimateLabelingTaskResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('EstimateLabelingTask', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'EstimateLabelingTask', {'reason': request.reason})
            await deps.repository.save_labeling_task(request.context.tenant_id, request.labeling_task)
            response_0 = lineage_v1_impact_validation_service_pb2.NormalizeImpactResponse()
            response_1 = anomalies_v1_anomaly_feedback_calculation_service_pb2.RecalculateAnomalyFeedbacksResponse()
            async for item_0 in async_messages(request.labeling_task.history):
                outgoing_0 = lineage_v1_impact_validation_service_pb2.NormalizeImpactRequest(
                    context=request.context,
                    impact=lineage_v1_lineage_pb2.Impact(
                        history=[lineage_v1_lineage_pb2.ImpactStatusChange(changed_at=item_0.changed_at)]
                    )
                )
                response_0 = await deps.clients.lineage_impact_validation.NormalizeImpact(
                    outgoing_0,
                    timeout=deps.settings.timeout
                )
            outgoing_1 = anomalies_v1_anomaly_feedback_calculation_service_pb2.RecalculateAnomalyFeedbacksRequest(
                context=request.context,
                details=anomalies_v1_anomaly_feedback_calculation_service_pb2.RecalculateAnomalyFeedbacksRequest.Details(
                    destination=common_v1_address_pb2.PostalAddress(
                        lines=list(request.details.destination.lines),
                        region=request.details.destination.region
                    )
                )
            )
            send_1 = partial(
                deps.clients.anomalies_anomaly_feedback_calculation.RecalculateAnomalyFeedbacks,
                timeout=deps.settings.timeout
            )
            response_1 = await send_1(outgoing_1)
            returned_1_0 = response_1.result.details
            response.result.details.update(returned_1_0)
            returned_1_1 = response_1.result.reference_ids
            response.result.reference_ids.extend(returned_1_1)
            echoed_0 = request.labeling_task_id
            response.labeling_task.labeling_task_id = echoed_0
            echoed_1 = request.labeling_task.subject
            response.labeling_task.subject = echoed_1
            return response

    async def handle_explain_labeling_task_calculation(
        self,
        request: labeling_v1_labeling_task_calculation_service_pb2.ExplainLabelingTaskCalculationRequest
    ) -> labeling_v1_labeling_task_calculation_service_pb2.ExplainLabelingTaskCalculationResponse:
        """Explains a labeling task."""
        deps = self.deps
        response = labeling_v1_labeling_task_calculation_service_pb2.ExplainLabelingTaskCalculationResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ExplainLabelingTaskCalculation', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ExplainLabelingTaskCalculation',
                {'reason': request.reason}
            )
            await deps.repository.save_labeling_task(request.context.tenant_id, request.labeling_task)
            response_0 = metrics_v1_dashboard_sync_service_pb2.ResolveDashboardConflictResponse()
            response_1 = audit_v1_audit_event_service_pb2.WatchAuditEventsResponse()
            outgoing_0 = metrics_v1_dashboard_sync_service_pb2.ResolveDashboardConflictRequest(
                context=request.context,
                dashboard=metrics_v1_metrics_pb2.Dashboard(
                    audit=common_v1_audit_pb2.AuditInfo(
                        created_at=request.labeling_task.audit.created_at,
                        created_by=request.labeling_task.audit.created_by,
                        updated_at=request.labeling_task.audit.updated_at
                    ),
                    counterparty=metrics_v1_refs_pb2.MetricAlertRef(
                        display_name=request.labeling_task.assignee.display_name
                    )
                )
            )
            response_0 = await hooks.labeling_task_calculation_explain_labeling_task_calculation0(
                deps.clients.metrics_dashboard_sync,
                outgoing_0,
                deps.settings.timeout
            )
            for item_1 in request.labeling_task.history:
                outgoing_1 = audit_v1_audit_event_service_pb2.WatchAuditEventsRequest(
                    context=request.context,
                    filter=audit_v1_audit_event_service_pb2.WatchAuditEventsRequest.Filter(
                        created_after=item_1.changed_at,
                        region=response_0.dashboard.billing_address.region
                    ),
                    subscriber=common_v1_contact_pb2.ContactInfo(
                        email=request.labeling_task.assignee.email,
                        phone=request.details.contact.phone
                    )
                )
                async for result_1 in deps.clients.audit_audit_event.WatchAuditEvents(
                    outgoing_1,
                    timeout=deps.settings.timeout
                ):
                    response_1 = result_1
            returned_0_0 = response_0.result.status
            if returned_0_0:
                response.result.status = returned_0_0
            returned_0_1 = response_0.result.status
            if returned_0_1:
                response.outcome.status = returned_0_1
            echoed_0 = request.labeling_task_id
            response.labeling_task.labeling_task_id = echoed_0
            echoed_1 = request.labeling_task.assignee
            response.labeling_task.assignee.CopyFrom(echoed_1)
            return response

    async def handle_get_labeling_task_rates(
        self,
        request: labeling_v1_labeling_task_calculation_service_pb2.GetLabelingTaskRatesRequest
    ) -> labeling_v1_labeling_task_calculation_service_pb2.GetLabelingTaskRatesResponse:
        """Returns a labeling task."""
        deps = self.deps
        response = labeling_v1_labeling_task_calculation_service_pb2.GetLabelingTaskRatesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('GetLabelingTaskRates', extra={'fields': {'domain': 'labeling'}})
            await deps.repository.audit(request.context.tenant_id, 'GetLabelingTaskRates', {})
            response_0 = modelregistry_v1_registered_model_validation_service_pb2.LintRegisteredModelsResponse()
            response_1 = featurestore_v1_feature_value_calculation_service_pb2.QuoteFeatureValueResponse()
            outgoing_0 = modelregistry_v1_registered_model_validation_service_pb2.LintRegisteredModelsRequest(
                context=request.context,
                details=modelregistry_v1_registered_model_validation_service_pb2.LintRegisteredModelsRequest.Details(
                    locale=request.context.locale
                ),
                registered_model=modelregistry_v1_modelregistry_pb2.RegisteredModel(
                    audit=common_v1_audit_pb2.AuditInfo(updated_at=request.context.deadline),
                    owner=identity_v1_refs_pb2.UserRef(
                        email=request.context.actor.email,
                        user_id=request.context.actor.user_id
                    )
                )
            )
            response_0 = await deps.clients.modelregistry_registered_model_validation.LintRegisteredModels(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = featurestore_v1_feature_value_calculation_service_pb2.QuoteFeatureValueRequest(
                context=request.context,
                details=featurestore_v1_feature_value_calculation_service_pb2.QuoteFeatureValueRequest.Details(
                    destination=common_v1_address_pb2.PostalAddress(
                        country_code=response_0.registered_model.address.country_code,
                        lines=list(response_0.registered_model.address.lines),
                        locality=response_0.registered_model.address.locality
                    )
                ),
                feature_value=featurestore_v1_featurestore_pb2.FeatureValue(
                    measurements=[
                        featurestore_v1_featurestore_pb2.FeatureValueMeasurement(
                            unit=response_0.registered_model.dimensions.unit
                        )
                    ]
                )
            )
            steps_1 = [
                partial(
                    deps.clients.featurestore_feature_value_calculation.QuoteFeatureValue,
                    outgoing_1,
                    timeout=deps.settings.timeout
                )
            ]
            results_1 = await run_steps(steps_1)
            response_1 = results_1[-1]
            returned_0_0 = response_0.registered_model.audit.etag
            if returned_0_0:
                response.labeling_task.audit.etag = returned_0_0
            returned_1_0 = response_1.result.correlation_id
            if returned_1_0:
                response.result.correlation_id = returned_1_0
            returned_1_1 = response_1.feature_value.subject.display_name
            if returned_1_1:
                response.labeling_task.assignee.display_name = returned_1_1
            echoed_0 = request.labeling_task_id
            response.labeling_task.labeling_task_id = echoed_0
            return response

    async def handle_quote_labeling_task(
        self,
        request: labeling_v1_labeling_task_calculation_service_pb2.QuoteLabelingTaskRequest
    ) -> labeling_v1_labeling_task_calculation_service_pb2.QuoteLabelingTaskResponse:
        """Quotes a labeling task."""
        deps = self.deps
        response = labeling_v1_labeling_task_calculation_service_pb2.QuoteLabelingTaskResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('QuoteLabelingTask', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'QuoteLabelingTask', {'reason': request.reason})
            await deps.repository.save_labeling_task(request.context.tenant_id, request.labeling_task)
            response_0 = configuration_v1_config_set_query_service_pb2.ExportConfigSetsResponse()
            response_1 = featureflags_v1_feature_flag_query_service_pb2.CountFeatureFlagsResponse()
            outgoing_0 = configuration_v1_config_set_query_service_pb2.ExportConfigSetsRequest(
                context=request.context,
                filter=configuration_v1_config_set_query_service_pb2.ExportConfigSetsRequest.Filter(
                    region=request.details.destination.region
                )
            )
            async for chunk_0 in deps.clients.configuration_config_set_query.ExportConfigSets(
                outgoing_0,
                timeout=deps.settings.timeout
            ):
                response_0 = chunk_0
            outgoing_1 = featureflags_v1_feature_flag_query_service_pb2.CountFeatureFlagsRequest(
                context=request.context,
                filter=featureflags_v1_feature_flag_query_service_pb2.CountFeatureFlagsRequest.Filter(
                    region=request.details.destination.region
                )
            )
            response_1 = cast(featureflags_v1_feature_flag_query_service_pb2.CountFeatureFlagsResponse, await deps.bus.request(
                'acme.labeling.v1.LabelingTaskCalculationService/QuoteLabelingTask/1', outgoing_1, deps.settings.timeout,
            ))
            returned_1_0 = response_1.result.status
            if returned_1_0:
                response.result.status = returned_1_0
            echoed_0 = request.labeling_task_id
            response.labeling_task.labeling_task_id = echoed_0
            echoed_1 = request.details.currency_code
            response.breakdown.currency_code = echoed_1
            return response

    async def handle_recalculate_labeling_tasks(
        self,
        request: labeling_v1_labeling_task_calculation_service_pb2.RecalculateLabelingTasksRequest
    ) -> labeling_v1_labeling_task_calculation_service_pb2.RecalculateLabelingTasksResponse:
        """Recalculates a labeling task."""
        deps = self.deps
        response = labeling_v1_labeling_task_calculation_service_pb2.RecalculateLabelingTasksResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('RecalculateLabelingTasks', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'RecalculateLabelingTasks',
                {'reason': request.reason}
            )
            await deps.repository.save_labeling_task(request.context.tenant_id, request.labeling_task)
            response_0 = metrics_v1_metric_series_history_service_pb2.CompareMetricSeriesVersionsResponse()
            outgoing_0 = metrics_v1_metric_series_history_service_pb2.CompareMetricSeriesVersionsRequest(
                context=request.context,
                metric_series=metrics_v1_metrics_pb2.MetricSeries(
                    audit=common_v1_audit_pb2.AuditInfo(
                        created_at=request.labeling_task.audit.created_at,
                        etag=request.labeling_task.audit.etag,
                        updated_by=request.labeling_task.audit.updated_by
                    ),
                    owner=identity_v1_refs_pb2.UserRef(display_name=request.labeling_task.assignee.display_name)
                )
            )
            response_0 = await deps.clients.metrics_metric_series_history.CompareMetricSeriesVersions(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.metric_series.audit.created_at
            returned_0_0_part_1 = response.labeling_task.comments.add()
            if returned_0_0.ListFields():
                returned_0_0_part_1.created_at.MergeFrom(returned_0_0)
            echoed_0 = request.labeling_task_id
            response.labeling_task.labeling_task_id = echoed_0
            echoed_1 = request.labeling_task.subject
            response.labeling_task.subject = echoed_1
            return response

    async def handle_simulate_labeling_task(
        self,
        request: labeling_v1_labeling_task_calculation_service_pb2.SimulateLabelingTaskRequest
    ) -> labeling_v1_labeling_task_calculation_service_pb2.SimulateLabelingTaskResponse:
        """Simulates a labeling task."""
        deps = self.deps
        response = labeling_v1_labeling_task_calculation_service_pb2.SimulateLabelingTaskResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SimulateLabelingTask', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'SimulateLabelingTask', {'reason': request.reason})
            await deps.repository.save_labeling_task(request.context.tenant_id, request.labeling_task)
            response_0 = metrics_v1_metric_series_history_service_pb2.AnnotateMetricSeriesVersionResponse()
            response_1 = metrics_v1_metric_series_history_service_pb2.RecordMetricSeriesVersionResponse()
            response_2 = modelregistry_v1_deployment_validation_service_pb2.ExplainDeploymentDecisionResponse()
            response_3 = featurestore_v1_feature_view_calculation_service_pb2.CalculateFeatureViewResponse()
            outgoing_0 = metrics_v1_metric_series_history_service_pb2.AnnotateMetricSeriesVersionRequest()
            outgoing_0.context.CopyFrom(request.context)
            outgoing_0.metric_series.address.country_code = request.details.destination.country_code
            outgoing_0.metric_series.audit.created_by = request.labeling_task.audit.created_by
            if request.labeling_task.WhichOneof('origin') == 'customer':
                outgoing_0.metric_series.owner.display_name = request.labeling_task.customer.display_name
            outgoing_0.metric_series.address.postal_code = request.details.destination.postal_code
            response_0 = await deps.clients.metrics_metric_series_history.AnnotateMetricSeriesVersion(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            for item_1 in request.labeling_task.comments:
                outgoing_1 = metrics_v1_metric_series_history_service_pb2.RecordMetricSeriesVersionRequest(
                    context=request.context,
                    details=metrics_v1_metric_series_history_service_pb2.RecordMetricSeriesVersionRequest.Details(
                        author_email=item_1.author_email
                    ),
                    metric_series=metrics_v1_metrics_pb2.MetricSeries(
                        audit=common_v1_audit_pb2.AuditInfo(created_at=item_1.created_at)
                    )
                )
                response_1 = await deps.clients.metrics_metric_series_history.RecordMetricSeriesVersion(
                    outgoing_1,
                    timeout=deps.settings.timeout
                )
            outgoing_2 = modelregistry_v1_deployment_validation_service_pb2.ExplainDeploymentDecisionRequest(
                context=request.context,
                deployment=modelregistry_v1_modelregistry_pb2.Deployment(
                    participants=[
                        modelregistry_v1_modelregistry_pb2.DeploymentParticipant(
                            contact=common_v1_contact_pb2.ContactInfo(name=request.labeling_task.requester.name)
                        )
                    ]
                )
            )
            document_2 = MessageToDict(outgoing_2, preserving_proto_field_name=True)
            outgoing_2 = ParseDict(
                document_2,
                modelregistry_v1_deployment_validation_service_pb2.ExplainDeploymentDecisionRequest()
            )
            response_2 = await deps.clients.modelregistry_deployment_validation.ExplainDeploymentDecision(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            outgoing_3 = featurestore_v1_feature_view_calculation_service_pb2.CalculateFeatureViewRequest(
                context=request.context,
                feature_view=featurestore_v1_featurestore_pb2.FeatureView(
                    address=common_v1_address_pb2.PostalAddress(
                        locality=request.details.destination.locality,
                        recipient=response_2.deployment.location.recipient
                    ),
                    components={
                        'primary': featurestore_v1_featurestore_pb2.FeatureViewComponent(
                            component_id=response_1.metric_series.components.get(
                                'primary',
                                metrics_v1_metrics_pb2.MetricSeriesComponent()
                            ).component_id
                        )
                    },
                    owner=identity_v1_refs_pb2.UserRef(display_name=response_1.metric_series.owner.display_name)
                )
            )
            document_3 = MessageToJson(outgoing_3, preserving_proto_field_name=True)
            outgoing_3 = Parse(
                document_3,
                featurestore_v1_feature_view_calculation_service_pb2.CalculateFeatureViewRequest()
            )
            response_3 = await deps.clients.featurestore_feature_view_calculation.CalculateFeatureView(
                outgoing_3,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.status
            if returned_0_0:
                response.result.status = returned_0_0
            returned_2_0 = response_2.deployment.organizer.display_name
            if returned_2_0:
                response.labeling_task.assignee.display_name = returned_2_0
            returned_2_1 = response_2.result.status
            if returned_2_1:
                response.result.status = returned_2_1
            returned_3_0 = response_3.result.status
            if returned_3_0:
                response.result.status = returned_3_0
            echoed_0 = request.labeling_task_id
            response.labeling_task.labeling_task_id = echoed_0
            echoed_1 = request.labeling_task.priority
            response.labeling_task.priority = echoed_1
            return response
