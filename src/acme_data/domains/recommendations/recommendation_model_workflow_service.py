"""Runs the long-lived workflow that takes a recommendation model from start to finish."""

from __future__ import annotations

from collections.abc import AsyncIterator
from dataclasses import dataclass
from functools import partial
from typing import cast
import asyncio
import logging

from google.protobuf.any_pb2 import Any as AnyMessage
from google.protobuf.json_format import MessageToDict
from google.protobuf.json_format import ParseDict
import grpc

from acme.anomalies.v1 import anomalies_pb2 as anomalies_v1_anomalies_pb2
from acme.anomalies.v1 import (
    anomaly_feedback_approval_service_pb2 as anomalies_v1_anomaly_feedback_approval_service_pb2,
)
from acme.anomalies.v1 import (
    anomaly_feedback_approval_service_pb2_grpc as anomalies_v1_anomaly_feedback_approval_service_pb2_grpc,
)
from acme.anomalies.v1 import (
    anomaly_feedback_workflow_service_pb2 as anomalies_v1_anomaly_feedback_workflow_service_pb2,
)
from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.contracts.v1 import contract_service_pb2 as contracts_v1_contract_service_pb2
from acme.customers.v1 import customer_calculation_service_pb2 as customers_v1_customer_calculation_service_pb2
from acme.customers.v1 import (
    customer_segment_validation_service_pb2 as customers_v1_customer_segment_validation_service_pb2,
)
from acme.customers.v1 import customers_pb2 as customers_v1_customers_pb2
from acme.customers.v1 import preference_calculation_service_pb2 as customers_v1_preference_calculation_service_pb2
from acme.customers.v1 import refs_pb2 as customers_v1_refs_pb2
from acme.datasets.v1 import refs_pb2 as datasets_v1_refs_pb2
from acme.featurestore.v1 import entity_reporting_service_pb2 as featurestore_v1_entity_reporting_service_pb2
from acme.fuel.v1 import fuel_card_query_service_pb2 as fuel_v1_fuel_card_query_service_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.identity.v1 import user_query_service_pb2 as identity_v1_user_query_service_pb2
from acme.metrics.v1 import metric_alert_validation_service_pb2 as metrics_v1_metric_alert_validation_service_pb2
from acme.metrics.v1 import metrics_pb2 as metrics_v1_metrics_pb2
from acme.modelregistry.v1 import deployment_import_service_pb2 as modelregistry_v1_deployment_import_service_pb2
from acme.modelregistry.v1 import modelregistry_pb2 as modelregistry_v1_modelregistry_pb2
from acme.modelregistry.v1 import (
    registered_model_reporting_service_pb2 as modelregistry_v1_registered_model_reporting_service_pb2,
)
from acme.notifications.v1 import notification_query_service_pb2 as notifications_v1_notification_query_service_pb2
from acme.pipelines.v1 import pipeline_approval_service_pb2 as pipelines_v1_pipeline_approval_service_pb2
from acme.recommendations.v1 import (
    interaction_validation_service_pb2 as recommendations_v1_interaction_validation_service_pb2,
)
from acme.recommendations.v1 import (
    recommendation_model_workflow_service_pb2 as recommendations_v1_recommendation_model_workflow_service_pb2,
)
from acme.recommendations.v1 import (
    recommendation_model_workflow_service_pb2_grpc as recommendations_v1_recommendation_model_workflow_service_pb2_grpc,
)
from acme.recommendations.v1 import (
    recommendation_set_approval_service_pb2 as recommendations_v1_recommendation_set_approval_service_pb2,
)
from acme.recommendations.v1 import (
    recommendation_set_query_service_pb2 as recommendations_v1_recommendation_set_query_service_pb2,
)
from acme.recommendations.v1 import recommendation_set_service_pb2 as recommendations_v1_recommendation_set_service_pb2
from acme.recommendations.v1 import (
    recommendation_set_validation_service_pb2 as recommendations_v1_recommendation_set_validation_service_pb2,
)
from acme.recommendations.v1 import (
    recommendation_set_workflow_service_pb2 as recommendations_v1_recommendation_set_workflow_service_pb2,
)
from acme.recommendations.v1 import recommendations_pb2 as recommendations_v1_recommendations_pb2

from acme_data.domains.recommendations import hooks
from acme_data.domains.recommendations.adapters import (
    RecommendationModelWorkflowCancelRecommendationModelWorkflow0Adapter,
)
from acme_data.domains.recommendations.adapters import (
    RecommendationModelWorkflowSignalRecommendationModelWorkflow1Adapter,
)
from acme_data.domains.recommendations.adapters import RecommendationModelWorkflowSignalRecommendationModelWorkflow1Port
from acme_data.domains.recommendations.dependencies import Dependencies
from acme_data.domains.recommendations.models import (
    RecommendationModelWorkflowResumeRecommendationModelWorkflow1Command,
)
from acme_data.domains.recommendations.models import RecommendationModelWorkflowRetryRecommendationModelWorkflow0Command
from acme_data.domains.recommendations.models import (
    to_recommendation_model_workflow_resume_recommendation_model_workflow1_command,
)
from acme_data.domains.recommendations.models import (
    to_recommendation_model_workflow_retry_recommendation_model_workflow0_command,
)
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import run_steps
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


@dataclass(slots=True)
class RecommendationModelWorkflowServicer(
    recommendations_v1_recommendation_model_workflow_service_pb2_grpc.RecommendationModelWorkflowServiceServicer
):
    deps: Dependencies

    @rpc_errors
    async def AdvanceRecommendationModelWorkflow(
        self, request: recommendations_v1_recommendation_model_workflow_service_pb2.AdvanceRecommendationModelWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> recommendations_v1_recommendation_model_workflow_service_pb2.AdvanceRecommendationModelWorkflowResponse:
        """Advances a recommendation model."""
        return await self.handle_advance_recommendation_model_workflow(request)

    @rpc_errors
    async def CancelRecommendationModelWorkflow(
        self, request: recommendations_v1_recommendation_model_workflow_service_pb2.CancelRecommendationModelWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> recommendations_v1_recommendation_model_workflow_service_pb2.CancelRecommendationModelWorkflowResponse:
        """Cancels a recommendation model."""
        return await self.handle_cancel_recommendation_model_workflow(request)

    @rpc_errors
    @retry_transient
    async def InspectRecommendationModelWorkflow(
        self, request: recommendations_v1_recommendation_model_workflow_service_pb2.InspectRecommendationModelWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> recommendations_v1_recommendation_model_workflow_service_pb2.InspectRecommendationModelWorkflowResponse:
        """Returns a recommendation model."""
        return await self.handle_inspect_recommendation_model_workflow(request)

    @rpc_errors
    @retry_transient
    async def ListRecommendationModelWorkflows(
        self, request: recommendations_v1_recommendation_model_workflow_service_pb2.ListRecommendationModelWorkflowsRequest, context: grpc.aio.ServicerContext,
    ) -> recommendations_v1_recommendation_model_workflow_service_pb2.ListRecommendationModelWorkflowsResponse:
        """Lists recommendation models a page at a time."""
        return await self.handle_list_recommendation_model_workflows(request)

    @rpc_errors
    async def PauseRecommendationModelWorkflow(
        self, request: recommendations_v1_recommendation_model_workflow_service_pb2.PauseRecommendationModelWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> recommendations_v1_recommendation_model_workflow_service_pb2.PauseRecommendationModelWorkflowResponse:
        """Pauses a recommendation model."""
        return await self.handle_pause_recommendation_model_workflow(request)

    @rpc_errors
    async def ResumeRecommendationModelWorkflow(
        self, request: recommendations_v1_recommendation_model_workflow_service_pb2.ResumeRecommendationModelWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> recommendations_v1_recommendation_model_workflow_service_pb2.ResumeRecommendationModelWorkflowResponse:
        """Resumes a recommendation model."""
        return await self.handle_resume_recommendation_model_workflow(request)

    @rpc_errors
    async def RetryRecommendationModelWorkflow(
        self, request: recommendations_v1_recommendation_model_workflow_service_pb2.RetryRecommendationModelWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> recommendations_v1_recommendation_model_workflow_service_pb2.RetryRecommendationModelWorkflowResponse:
        """Retrys a recommendation model."""
        return await self.handle_retry_recommendation_model_workflow(request)

    @rpc_errors
    async def SignalRecommendationModelWorkflow(
        self, request: recommendations_v1_recommendation_model_workflow_service_pb2.SignalRecommendationModelWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> recommendations_v1_recommendation_model_workflow_service_pb2.SignalRecommendationModelWorkflowResponse:
        """Signals a recommendation model."""
        return await self.handle_signal_recommendation_model_workflow(request)

    @rpc_errors
    async def StartRecommendationModelWorkflow(
        self, request: recommendations_v1_recommendation_model_workflow_service_pb2.StartRecommendationModelWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> recommendations_v1_recommendation_model_workflow_service_pb2.StartRecommendationModelWorkflowResponse:
        """Starts a recommendation model."""
        return await self.handle_start_recommendation_model_workflow(request)

    async def handle_advance_recommendation_model_workflow(
        self,
        request: recommendations_v1_recommendation_model_workflow_service_pb2.AdvanceRecommendationModelWorkflowRequest
    ) -> recommendations_v1_recommendation_model_workflow_service_pb2.AdvanceRecommendationModelWorkflowResponse:
        """Advances a recommendation model."""
        deps = self.deps
        response = recommendations_v1_recommendation_model_workflow_service_pb2.AdvanceRecommendationModelWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('AdvanceRecommendationModelWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'AdvanceRecommendationModelWorkflow',
                {'reason': request.reason}
            )
            await deps.repository.save_recommendation_model(request.context.tenant_id, request.recommendation_model)
            response_0 = modelregistry_v1_deployment_import_service_pb2.ValidateDeploymentImportResponse()
            response_1 = modelregistry_v1_registered_model_reporting_service_pb2.CountRegisteredModelTotalsResponse()
            outgoing_0 = modelregistry_v1_deployment_import_service_pb2.ValidateDeploymentImportRequest(
                context=request.context,
                deployment=modelregistry_v1_modelregistry_pb2.Deployment(
                    participants=[
                        modelregistry_v1_modelregistry_pb2.DeploymentParticipant(
                            contact=common_v1_contact_pb2.ContactInfo(name=request.details.notify.name)
                        )
                    ]
                )
            )
            outgoing_1 = modelregistry_v1_registered_model_reporting_service_pb2.CountRegisteredModelTotalsRequest(
                context=request.context,
                filter=modelregistry_v1_registered_model_reporting_service_pb2.CountRegisteredModelTotalsRequest.Filter(
                    region=request.recommendation_model.address.region
                )
            )
            response_0, response_1 = await asyncio.gather(
                deps.clients.modelregistry_deployment_import.ValidateDeploymentImport(
                    outgoing_0,
                    timeout=deps.settings.timeout
                ),
                deps.clients.modelregistry_registered_model_reporting.CountRegisteredModelTotals(
                    outgoing_1,
                    timeout=deps.settings.timeout
                ),
            )
            returned_0_0 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_0)
            returned_1_0 = response_1.result.status
            if returned_1_0:
                response.result.status = returned_1_0
            echoed_0 = request.recommendation_model_id
            response.recommendation_model.recommendation_model_id = echoed_0
            echoed_1 = request.recommendation_model.owner
            response.recommendation_model.owner.CopyFrom(echoed_1)
            return response

    async def handle_cancel_recommendation_model_workflow(
        self,
        request: recommendations_v1_recommendation_model_workflow_service_pb2.CancelRecommendationModelWorkflowRequest
    ) -> recommendations_v1_recommendation_model_workflow_service_pb2.CancelRecommendationModelWorkflowResponse:
        """Cancels a recommendation model."""
        deps = self.deps
        response = recommendations_v1_recommendation_model_workflow_service_pb2.CancelRecommendationModelWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CancelRecommendationModelWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'CancelRecommendationModelWorkflow',
                {'reason': request.reason}
            )
            await deps.repository.save_recommendation_model(request.context.tenant_id, request.recommendation_model)
            response_0 = notifications_v1_notification_query_service_pb2.CountNotificationsResponse()
            response_1 = recommendations_v1_recommendation_set_approval_service_pb2.ListPendingRecommendationSetsResponse()
            response_2 = metrics_v1_metric_alert_validation_service_pb2.PreviewMetricAlertResponse()
            response_3 = recommendations_v1_recommendation_set_approval_service_pb2.SubmitRecommendationSetResponse()
            outgoing_0 = notifications_v1_notification_query_service_pb2.CountNotificationsRequest(
                context=request.context,
                filter=notifications_v1_notification_query_service_pb2.CountNotificationsRequest.Filter(
                    created_after=request.recommendation_model.audit.created_at,
                    labels=dict(request.recommendation_model.specs),
                    owner_id=request.recommendation_model_id,
                    region=request.recommendation_model.address.region
                )
            )
            response_0 = await RecommendationModelWorkflowCancelRecommendationModelWorkflow0Adapter(
                deps.clients.notifications_notification_query,
                deps.settings.timeout
            )(outgoing_0)
            outgoing_1 = recommendations_v1_recommendation_set_approval_service_pb2.ListPendingRecommendationSetsRequest(
                context=request.context,
                filter=recommendations_v1_recommendation_set_approval_service_pb2.ListPendingRecommendationSetsRequest.Filter(
                    created_after=request.recommendation_model.audit.created_at,
                    labels=dict(request.details.parameters),
                    region=request.recommendation_model.address.region
                )
            )
            response_1 = cast(recommendations_v1_recommendation_set_approval_service_pb2.ListPendingRecommendationSetsResponse, await deps.bus.request(
                'acme.recommendations.v1.RecommendationModelWorkflowService/CancelRecommendationModelWorkflow/1', outgoing_1, deps.settings.timeout,
            ))
            outgoing_2 = metrics_v1_metric_alert_validation_service_pb2.PreviewMetricAlertRequest(
                context=request.context,
                metric_alert=metrics_v1_metrics_pb2.MetricAlert(
                    owner=identity_v1_refs_pb2.UserRef(display_name=request.recommendation_model.owner.display_name)
                )
            )
            response_2 = await deps.clients.metrics_metric_alert_validation.PreviewMetricAlert(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            outgoing_3 = recommendations_v1_recommendation_set_approval_service_pb2.SubmitRecommendationSetRequest(
                context=request.context,
                recommendation_set=recommendations_v1_recommendations_pb2.RecommendationSet(
                    billing_address=common_v1_address_pb2.PostalAddress(
                        country_code=request.recommendation_model.address.country_code,
                        lines=list(request.recommendation_model.address.lines)
                    ),
                    lines=[
                        recommendations_v1_recommendations_pb2.RecommendationSetLine(
                            tax=recommendations_v1_recommendations_pb2.RecommendationSetLineTax(
                                amount=response_2.metric_alert.discount.amount
                            )
                        )
                    ]
                )
            )
            method_name_3 = 'SubmitRecommendationSet'
            response_3 = await getattr(
                deps.clients.recommendations_recommendation_set_approval,
                method_name_3
            )(outgoing_3, timeout=deps.settings.timeout)
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.result.message = returned_0_0
            returned_1_0 = response_1.result.correlation_id
            if returned_1_0:
                response.result.correlation_id = returned_1_0
            returned_2_0 = response_2.result.message
            if returned_2_0:
                response.result.message = returned_2_0
            returned_2_1 = response_2.result.reference_ids
            response.result.reference_ids.extend(returned_2_1)
            returned_3_0 = response_3.result.status
            if returned_3_0:
                response.result.status = returned_3_0
            returned_3_1 = response_3.recommendation_set.audit.updated_at
            if returned_3_1.ListFields():
                response.recommendation_model.audit.updated_at.MergeFrom(returned_3_1)
            echoed_0 = request.recommendation_model_id
            response.recommendation_model.recommendation_model_id = echoed_0
            echoed_1 = request.recommendation_model.code
            response.recommendation_model.code = echoed_1
            return response

    async def handle_inspect_recommendation_model_workflow(
        self,
        request: recommendations_v1_recommendation_model_workflow_service_pb2.InspectRecommendationModelWorkflowRequest
    ) -> recommendations_v1_recommendation_model_workflow_service_pb2.InspectRecommendationModelWorkflowResponse:
        """Returns a recommendation model."""
        deps = self.deps
        response = recommendations_v1_recommendation_model_workflow_service_pb2.InspectRecommendationModelWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('InspectRecommendationModelWorkflow', extra={'fields': {'domain': 'recommendations'}})
            await deps.repository.audit(request.context.tenant_id, 'InspectRecommendationModelWorkflow', {})
            response_0 = featurestore_v1_entity_reporting_service_pb2.StreamEntityMetricsResponse()
            response_1 = identity_v1_user_query_service_pb2.FindUsersResponse()
            outgoing_0 = featurestore_v1_entity_reporting_service_pb2.StreamEntityMetricsRequest(
                context=request.context,
                filter=featurestore_v1_entity_reporting_service_pb2.StreamEntityMetricsRequest.Filter(
                    created_after=request.context.deadline,
                    labels=dict(request.context.baggage),
                    owner_id=request.recommendation_model_id
                ),
                subscriber=common_v1_contact_pb2.ContactInfo(email=request.context.actor.email)
            )
            async for chunk_0 in deps.clients.featurestore_entity_reporting.StreamEntityMetrics(
                outgoing_0,
                timeout=deps.settings.timeout
            ):
                response_0 = chunk_0
            outgoing_1 = identity_v1_user_query_service_pb2.FindUsersRequest(
                context=request.context,
                filter=identity_v1_user_query_service_pb2.FindUsersRequest.Filter(
                    owner_id=request.recommendation_model_id
                )
            )
            document_1 = MessageToDict(outgoing_1, preserving_proto_field_name=True)
            outgoing_1 = ParseDict(document_1, identity_v1_user_query_service_pb2.FindUsersRequest())
            response_1 = await deps.clients.identity_user_query.FindUsers(outgoing_1, timeout=deps.settings.timeout)
            returned_1_0 = response_1.result.details
            response.result.details.update(returned_1_0)
            returned_1_1 = response_1.result.status
            if returned_1_1:
                response.result.status = returned_1_1
            echoed_0 = request.recommendation_model_id
            response.recommendation_model.recommendation_model_id = echoed_0
            return response

    async def handle_list_recommendation_model_workflows(
        self,
        request: recommendations_v1_recommendation_model_workflow_service_pb2.ListRecommendationModelWorkflowsRequest
    ) -> recommendations_v1_recommendation_model_workflow_service_pb2.ListRecommendationModelWorkflowsResponse:
        """Lists recommendation models a page at a time."""
        deps = self.deps
        response = recommendations_v1_recommendation_model_workflow_service_pb2.ListRecommendationModelWorkflowsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ListRecommendationModelWorkflows', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ListRecommendationModelWorkflows',
                {'order_by': request.order_by}
            )
            response_0 = recommendations_v1_recommendation_set_validation_service_pb2.ValidateRecommendationSetResponse()
            outgoing_0 = recommendations_v1_recommendation_set_validation_service_pb2.ValidateRecommendationSetRequest(
                context=request.context,
                recommendation_set=recommendations_v1_recommendations_pb2.RecommendationSet(
                    billing_address=common_v1_address_pb2.PostalAddress(region=request.filter.region)
                )
            )
            response_0 = await deps.clients.recommendations_recommendation_set_validation.ValidateRecommendationSet(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_0)
            returned_0_1 = response_0.result.details
            response.result.details.update(returned_0_1)
            return response

    async def handle_pause_recommendation_model_workflow(
        self,
        request: recommendations_v1_recommendation_model_workflow_service_pb2.PauseRecommendationModelWorkflowRequest
    ) -> recommendations_v1_recommendation_model_workflow_service_pb2.PauseRecommendationModelWorkflowResponse:
        """Pauses a recommendation model."""
        deps = self.deps
        response = recommendations_v1_recommendation_model_workflow_service_pb2.PauseRecommendationModelWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('PauseRecommendationModelWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'PauseRecommendationModelWorkflow',
                {'reason': request.reason}
            )
            await deps.repository.save_recommendation_model(request.context.tenant_id, request.recommendation_model)
            response_0 = contracts_v1_contract_service_pb2.BatchGetContractsResponse()
            response_1 = customers_v1_customer_segment_validation_service_pb2.ExplainCustomerSegmentDecisionResponse()
            outgoing_0 = contracts_v1_contract_service_pb2.BatchGetContractsRequest()
            outgoing_0.context.CopyFrom(request.context)
            merged_0 = contracts_v1_contract_service_pb2.BatchGetContractsRequest()
            merged_0.MergeFrom(outgoing_0)
            outgoing_0.CopyFrom(merged_0)
            response_0 = await deps.clients.contracts_contract.BatchGetContracts(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = customers_v1_customer_segment_validation_service_pb2.ExplainCustomerSegmentDecisionRequest(
                context=request.context,
                customer_segment=customers_v1_customers_pb2.CustomerSegment(
                    audit=common_v1_audit_pb2.AuditInfo(created_at=request.recommendation_model.audit.created_at),
                    owner=identity_v1_refs_pb2.UserRef(email=request.details.notify.email)
                )
            )
            envelope_1 = AnyMessage()
            envelope_1.Pack(outgoing_1)
            outgoing_1 = customers_v1_customer_segment_validation_service_pb2.ExplainCustomerSegmentDecisionRequest()
            if not envelope_1.Unpack(outgoing_1):
                raise ValueError("partner envelope contains the wrong request type")
            response_1 = await deps.clients.customers_customer_segment_validation.ExplainCustomerSegmentDecision(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.status
            if returned_0_0:
                response.result.status = returned_0_0
            returned_1_0 = response_1.outcome.reference_id
            if returned_1_0:
                response.outcome.reference_id = returned_1_0
            returned_1_1 = response_1.customer_segment.owner.display_name
            if returned_1_1:
                response.recommendation_model.owner.display_name = returned_1_1
            echoed_0 = request.recommendation_model_id
            response.recommendation_model.recommendation_model_id = echoed_0
            echoed_1 = request.recommendation_model.specs
            response.recommendation_model.specs.update(echoed_1)
            return response

    async def handle_resume_recommendation_model_workflow(
        self,
        request: recommendations_v1_recommendation_model_workflow_service_pb2.ResumeRecommendationModelWorkflowRequest
    ) -> recommendations_v1_recommendation_model_workflow_service_pb2.ResumeRecommendationModelWorkflowResponse:
        """Resumes a recommendation model."""
        deps = self.deps
        response = recommendations_v1_recommendation_model_workflow_service_pb2.ResumeRecommendationModelWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ResumeRecommendationModelWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ResumeRecommendationModelWorkflow',
                {'reason': request.reason}
            )
            await deps.repository.save_recommendation_model(request.context.tenant_id, request.recommendation_model)
            response_0 = anomalies_v1_anomaly_feedback_approval_service_pb2.DelegateAnomalyFeedbackApprovalResponse()
            response_1 = anomalies_v1_anomaly_feedback_workflow_service_pb2.RetryAnomalyFeedbackWorkflowResponse()
            outgoing_0 = anomalies_v1_anomaly_feedback_approval_service_pb2.DelegateAnomalyFeedbackApprovalRequest(
                anomaly_feedback=anomalies_v1_anomalies_pb2.AnomalyFeedback(
                    measurements=[
                        anomalies_v1_anomalies_pb2.AnomalyFeedbackMeasurement(
                            unit=request.recommendation_model.dimensions.unit
                        )
                    ],
                    subject=datasets_v1_refs_pb2.DatasetRef(
                        display_name=request.recommendation_model.owner.display_name
                    )
                ),
                context=request.context,
                details=anomalies_v1_anomaly_feedback_approval_service_pb2.DelegateAnomalyFeedbackApprovalRequest.Details(
                    approver=identity_v1_refs_pb2.UserRef(
                        email=request.recommendation_model.owner.email,
                        user_id=request.recommendation_model.owner.user_id
                    )
                )
            )
            registered_0 = cast(
                anomalies_v1_anomaly_feedback_approval_service_pb2_grpc.AnomalyFeedbackApprovalServiceStub,
                deps.clients.registry['acme.anomalies.v1.AnomalyFeedbackApprovalService']
            )
            response_0 = await registered_0.DelegateAnomalyFeedbackApproval(outgoing_0, timeout=deps.settings.timeout)
            command_1 = RecommendationModelWorkflowResumeRecommendationModelWorkflow1Command(
                context=request.context,
                details_notify_email=request.details.notify.email,
                anomaly_feedback_subject_code=request.recommendation_model.code,
                anomaly_feedback_subject_display_name=request.recommendation_model.owner.display_name
            )
            outgoing_1 = to_recommendation_model_workflow_resume_recommendation_model_workflow1_command(command_1)
            response_1 = await deps.clients.anomalies_anomaly_feedback_workflow.RetryAnomalyFeedbackWorkflow(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.outcome.status
            if returned_0_0:
                response.outcome.status = returned_0_0
            returned_1_0 = response_1.outcome.next_steps
            response.outcome.next_steps.extend(returned_1_0)
            returned_1_1 = response_1.outcome.status
            if returned_1_1:
                response.result.status = returned_1_1
            echoed_0 = request.recommendation_model_id
            response.recommendation_model.recommendation_model_id = echoed_0
            echoed_1 = request.recommendation_model.capacity
            response.recommendation_model.capacity = echoed_1
            return response

    async def handle_retry_recommendation_model_workflow(
        self,
        request: recommendations_v1_recommendation_model_workflow_service_pb2.RetryRecommendationModelWorkflowRequest
    ) -> recommendations_v1_recommendation_model_workflow_service_pb2.RetryRecommendationModelWorkflowResponse:
        """Retrys a recommendation model."""
        deps = self.deps
        response = recommendations_v1_recommendation_model_workflow_service_pb2.RetryRecommendationModelWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('RetryRecommendationModelWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'RetryRecommendationModelWorkflow',
                {'reason': request.reason}
            )
            await deps.repository.save_recommendation_model(request.context.tenant_id, request.recommendation_model)
            response_0 = recommendations_v1_interaction_validation_service_pb2.ValidateInteractionResponse()
            response_1 = anomalies_v1_anomaly_feedback_workflow_service_pb2.ListAnomalyFeedbackWorkflowsResponse()
            response_2 = recommendations_v1_recommendation_set_service_pb2.UpdateRecommendationSetResponse()
            command_0 = RecommendationModelWorkflowRetryRecommendationModelWorkflow0Command.model_validate(
                {
                    'context': request.context,
                    'interaction_subject_display_name': request.recommendation_model.owner.display_name,
                    'details_contact_email': request.details.notify.email,
                    'interaction_measurements_unit': request.recommendation_model.dimensions.unit,
                    'details_contact_phone': request.details.notify.phone
                }
            )
            outgoing_0 = to_recommendation_model_workflow_retry_recommendation_model_workflow0_command(command_0)
            response_0 = await deps.clients.recommendations_interaction_validation.ValidateInteraction(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = anomalies_v1_anomaly_feedback_workflow_service_pb2.ListAnomalyFeedbackWorkflowsRequest(
                context=request.context,
                filter=anomalies_v1_anomaly_feedback_workflow_service_pb2.ListAnomalyFeedbackWorkflowsRequest.Filter(
                    created_after=request.recommendation_model.audit.created_at,
                    labels=dict(response_0.result.details),
                    owner_id=response_0.interaction.correlation_id,
                    region=request.recommendation_model.address.region
                )
            )
            send_1 = partial(
                deps.clients.anomalies_anomaly_feedback_workflow.ListAnomalyFeedbackWorkflows,
                timeout=deps.settings.timeout
            )
            response_1 = await send_1(outgoing_1)
            outgoing_2 = recommendations_v1_recommendation_set_service_pb2.UpdateRecommendationSetRequest(
                context=request.context,
                recommendation_set=recommendations_v1_recommendations_pb2.RecommendationSet(
                    audit=common_v1_audit_pb2.AuditInfo(
                        created_at=request.recommendation_model.audit.created_at,
                        etag=request.recommendation_model.audit.etag
                    ),
                    counterparty=customers_v1_refs_pb2.CustomerRef(
                        display_name=request.recommendation_model.owner.display_name
                    ),
                    lines=[
                        recommendations_v1_recommendations_pb2.RecommendationSetLine(
                            attributes=dict(response_0.interaction.attributes)
                        )
                    ]
                )
            )
            response_2 = await hooks.recommendation_model_workflow_retry_recommendation_model_workflow2(
                deps.clients.recommendations_recommendation_set,
                outgoing_2,
                deps.settings.timeout
            )
            returned_0_0 = response_0.outcome.status
            if returned_0_0:
                response.result.status = returned_0_0
            returned_0_1 = response_0.outcome.message
            if returned_0_1:
                response.outcome.message = returned_0_1
            returned_1_0 = response_1.result.correlation_id
            if returned_1_0:
                response.result.correlation_id = returned_1_0
            returned_1_1 = response_1.result.message
            if returned_1_1:
                response.outcome.message = returned_1_1
            returned_2_0 = response_2.recommendation_set.audit.created_at
            if returned_2_0.ListFields():
                response.recommendation_model.audit.created_at.MergeFrom(returned_2_0)
            echoed_0 = request.recommendation_model_id
            response.recommendation_model.recommendation_model_id = echoed_0
            echoed_1 = request.recommendation_model.specs
            response.recommendation_model.specs.update(echoed_1)
            return response

    async def handle_signal_recommendation_model_workflow(
        self,
        request: recommendations_v1_recommendation_model_workflow_service_pb2.SignalRecommendationModelWorkflowRequest
    ) -> recommendations_v1_recommendation_model_workflow_service_pb2.SignalRecommendationModelWorkflowResponse:
        """Signals a recommendation model."""
        deps = self.deps
        response = recommendations_v1_recommendation_model_workflow_service_pb2.SignalRecommendationModelWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SignalRecommendationModelWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'SignalRecommendationModelWorkflow',
                {'reason': request.reason}
            )
            await deps.repository.save_recommendation_model(request.context.tenant_id, request.recommendation_model)
            response_0 = pipelines_v1_pipeline_approval_service_pb2.DelegatePipelineApprovalResponse()
            response_1 = recommendations_v1_recommendation_set_query_service_pb2.FindRecommendationSetsResponse()
            response_2 = recommendations_v1_recommendation_set_workflow_service_pb2.SignalRecommendationSetWorkflowResponse()
            outgoing_0 = pipelines_v1_pipeline_approval_service_pb2.DelegatePipelineApprovalRequest()
            outgoing_0.context.CopyFrom(request.context)
            outgoing_0.pipeline.organizer.email = request.recommendation_model.owner.email
            if request.recommendation_model.WhichOneof('locator') == 'address':
                outgoing_0.pipeline.location.region = request.recommendation_model.address.region
            response_0 = await deps.clients.pipelines_pipeline_approval.DelegatePipelineApproval(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = recommendations_v1_recommendation_set_query_service_pb2.FindRecommendationSetsRequest(
                context=request.context,
                filter=recommendations_v1_recommendation_set_query_service_pb2.FindRecommendationSetsRequest.Filter(
                    created_after=request.recommendation_model.audit.updated_at,
                    region=response_0.pipeline.location.region
                )
            )
            port_1: RecommendationModelWorkflowSignalRecommendationModelWorkflow1Port = RecommendationModelWorkflowSignalRecommendationModelWorkflow1Adapter(
                deps.clients.recommendations_recommendation_set_query,
                deps.settings.timeout
            )
            response_1 = await port_1.execute(outgoing_1)
            outgoing_2 = recommendations_v1_recommendation_set_workflow_service_pb2.SignalRecommendationSetWorkflowRequest(
                context=request.context,
                recommendation_set=recommendations_v1_recommendations_pb2.RecommendationSet(
                    billing_address=common_v1_address_pb2.PostalAddress(
                        lines=list(response_0.pipeline.location.lines),
                        postal_code=response_0.pipeline.location.postal_code
                    )
                )
            )
            steps_2 = [
                partial(
                    deps.clients.recommendations_recommendation_set_workflow.SignalRecommendationSetWorkflow,
                    outgoing_2,
                    timeout=deps.settings.timeout
                )
            ]
            results_2 = await run_steps(steps_2)
            response_2 = results_2[-1]
            returned_0_0 = response_0.pipeline.audit.etag
            if returned_0_0:
                response.recommendation_model.audit.etag = returned_0_0
            returned_1_0 = response_1.result.status
            if returned_1_0:
                response.outcome.status = returned_1_0
            returned_1_1 = response_1.result.status
            if returned_1_1:
                response.result.status = returned_1_1
            returned_2_0 = response_2.recommendation_set.audit.created_by
            if returned_2_0:
                response.recommendation_model.audit.created_by = returned_2_0
            returned_2_1 = response_2.recommendation_set.audit.updated_at
            if returned_2_1.ListFields():
                response.recommendation_model.audit.updated_at.MergeFrom(returned_2_1)
            echoed_0 = request.recommendation_model_id
            response.recommendation_model.recommendation_model_id = echoed_0
            echoed_1 = request.recommendation_model.capacity
            response.recommendation_model.capacity = echoed_1
            return response

    async def handle_start_recommendation_model_workflow(
        self,
        request: recommendations_v1_recommendation_model_workflow_service_pb2.StartRecommendationModelWorkflowRequest
    ) -> recommendations_v1_recommendation_model_workflow_service_pb2.StartRecommendationModelWorkflowResponse:
        """Starts a recommendation model."""
        deps = self.deps
        response = recommendations_v1_recommendation_model_workflow_service_pb2.StartRecommendationModelWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('StartRecommendationModelWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'StartRecommendationModelWorkflow',
                {'reason': request.reason}
            )
            await deps.repository.save_recommendation_model(request.context.tenant_id, request.recommendation_model)
            response_0 = fuel_v1_fuel_card_query_service_pb2.SuggestFuelCardsResponse()
            response_1 = recommendations_v1_interaction_validation_service_pb2.ValidateInteractionResponse()
            response_2 = customers_v1_preference_calculation_service_pb2.EstimatePreferenceResponse()
            response_3 = customers_v1_customer_calculation_service_pb2.EstimateCustomerResponse()
            outgoing_0 = fuel_v1_fuel_card_query_service_pb2.SuggestFuelCardsRequest()
            outgoing_0.context.CopyFrom(request.context)
            if request.recommendation_model.WhichOneof('locator') == 'address':
                outgoing_0.filter.region = request.recommendation_model.address.region
            outgoing_0.filter.created_after.CopyFrom(request.recommendation_model.audit.updated_at)
            response_0 = await deps.clients.fuel_fuel_card_query.SuggestFuelCards(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = recommendations_v1_interaction_validation_service_pb2.ValidateInteractionRequest(
                context=request.context,
                interaction=recommendations_v1_recommendations_pb2.Interaction(
                    measurements=[
                        recommendations_v1_recommendations_pb2.InteractionMeasurement(
                            unit=request.recommendation_model.dimensions.unit
                        )
                    ],
                    subject=customers_v1_refs_pb2.CustomerRef(email=request.recommendation_model.owner.email)
                )
            )
            response_1 = cast(recommendations_v1_interaction_validation_service_pb2.ValidateInteractionResponse, await deps.bus.request(
                'acme.recommendations.v1.RecommendationModelWorkflowService/StartRecommendationModelWorkflow/1', outgoing_1, deps.settings.timeout,
            ))
            outgoing_2 = customers_v1_preference_calculation_service_pb2.EstimatePreferenceRequest(
                context=request.context,
                details=customers_v1_preference_calculation_service_pb2.EstimatePreferenceRequest.Details(
                    destination=common_v1_address_pb2.PostalAddress(
                        recipient=request.recommendation_model.address.recipient
                    )
                ),
                preference=customers_v1_customers_pb2.Preference(
                    audit=common_v1_audit_pb2.AuditInfo(created_by=request.recommendation_model.audit.created_by),
                    owner=identity_v1_refs_pb2.UserRef(email=request.details.notify.email)
                )
            )
            response_2 = await deps.clients.customers_preference_calculation.EstimatePreference(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            outgoing_3 = customers_v1_customer_calculation_service_pb2.EstimateCustomerRequest(
                context=request.context,
                customer=customers_v1_customers_pb2.Customer(
                    relationship_manager=identity_v1_refs_pb2.UserRef(
                        display_name=response_2.preference.owner.display_name
                    )
                )
            )
            method_name_3 = 'EstimateCustomer'
            response_3 = await getattr(
                deps.clients.customers_customer_calculation,
                method_name_3
            )(outgoing_3, timeout=deps.settings.timeout)
            returned_0_0 = response_0.result.correlation_id
            if returned_0_0:
                response.result.correlation_id = returned_0_0
            returned_0_1 = response_0.result.details
            response.result.details.update(returned_0_1)
            returned_1_0 = response_1.result.message
            if returned_1_0:
                response.result.message = returned_1_0
            returned_2_0 = response_2.preference.owner.user_id
            if returned_2_0:
                response.recommendation_model.owner.user_id = returned_2_0
            returned_2_1 = response_2.preference.description
            if returned_2_1:
                response.recommendation_model.components['primary'].description = returned_2_1
            returned_3_0 = response_3.customer.relationship_manager.display_name
            if returned_3_0:
                response.recommendation_model.owner.display_name = returned_3_0
            returned_3_1 = response_3.result.message
            if returned_3_1:
                response.result.message = returned_3_1
            echoed_0 = request.recommendation_model_id
            response.recommendation_model.recommendation_model_id = echoed_0
            echoed_1 = request.recommendation_model.name
            response.recommendation_model.name = echoed_1
            return response
