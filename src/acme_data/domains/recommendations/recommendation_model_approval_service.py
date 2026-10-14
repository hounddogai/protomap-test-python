"""Routes recommendation models through approval, with escalation and delegation."""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any
from typing import cast
import asyncio
import logging

from google.protobuf.any_pb2 import Any as AnyMessage
from google.protobuf.json_format import MessageToDict
from google.protobuf.json_format import MessageToJson
from google.protobuf.json_format import Parse
from google.protobuf.json_format import ParseDict
import grpc

from acme.audit.v1 import audit_event_validation_service_pb2 as audit_v1_audit_event_validation_service_pb2
from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.customers.v1 import (
    consent_record_calculation_service_pb2 as customers_v1_consent_record_calculation_service_pb2,
)
from acme.customers.v1 import customers_pb2 as customers_v1_customers_pb2
from acme.customers.v1 import household_query_service_pb2 as customers_v1_household_query_service_pb2
from acme.customers.v1 import household_validation_service_pb2 as customers_v1_household_validation_service_pb2
from acme.customers.v1 import refs_pb2 as customers_v1_refs_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.labeling.v1 import label_set_workflow_service_pb2 as labeling_v1_label_set_workflow_service_pb2
from acme.labeling.v1 import labeling_pb2 as labeling_v1_labeling_pb2
from acme.labeling.v1 import labeling_task_approval_service_pb2 as labeling_v1_labeling_task_approval_service_pb2
from acme.labeling.v1 import refs_pb2 as labeling_v1_refs_pb2
from acme.ledger.v1 import ledger_account_query_service_pb2 as ledger_v1_ledger_account_query_service_pb2
from acme.ledger.v1 import ledger_account_validation_service_pb2 as ledger_v1_ledger_account_validation_service_pb2
from acme.ledger.v1 import ledger_pb2 as ledger_v1_ledger_pb2
from acme.metrics.v1 import metric_alert_notification_service_pb2 as metrics_v1_metric_alert_notification_service_pb2
from acme.pipelines.v1 import pipeline_step_export_service_pb2 as pipelines_v1_pipeline_step_export_service_pb2
from acme.pipelines.v1 import pipelines_pb2 as pipelines_v1_pipelines_pb2
from acme.pricing.v1 import price_list_service_pb2 as pricing_v1_price_list_service_pb2
from acme.pricing.v1 import price_list_service_pb2_grpc as pricing_v1_price_list_service_pb2_grpc
from acme.recommendations.v1 import (
    interaction_calculation_service_pb2 as recommendations_v1_interaction_calculation_service_pb2,
)
from acme.recommendations.v1 import (
    interaction_validation_service_pb2 as recommendations_v1_interaction_validation_service_pb2,
)
from acme.recommendations.v1 import (
    recommendation_model_approval_service_pb2 as recommendations_v1_recommendation_model_approval_service_pb2,
)
from acme.recommendations.v1 import (
    recommendation_model_approval_service_pb2_grpc as recommendations_v1_recommendation_model_approval_service_pb2_grpc,
)
from acme.recommendations.v1 import (
    recommendation_model_calculation_service_pb2 as recommendations_v1_recommendation_model_calculation_service_pb2,
)
from acme.recommendations.v1 import (
    recommendation_set_approval_service_pb2 as recommendations_v1_recommendation_set_approval_service_pb2,
)
from acme.recommendations.v1 import recommendation_set_service_pb2 as recommendations_v1_recommendation_set_service_pb2
from acme.recommendations.v1 import (
    recommendation_set_validation_service_pb2 as recommendations_v1_recommendation_set_validation_service_pb2,
)
from acme.recommendations.v1 import recommendations_pb2 as recommendations_v1_recommendations_pb2

from acme_data.domains.recommendations import hooks
from acme_data.domains.recommendations.adapters import RecommendationModelApprovalEscalateRecommendationModel0Adapter
from acme_data.domains.recommendations.adapters import RecommendationModelApprovalEscalateRecommendationModel0Port
from acme_data.domains.recommendations.adapters import (
    RecommendationModelApprovalGetRecommendationModelApprovalStatus1Adapter,
)
from acme_data.domains.recommendations.dependencies import Dependencies
from acme_data.domains.recommendations.models import (
    RecommendationModelApprovalCommentRecommendationModelApproval3Command,
)
from acme_data.domains.recommendations.models import (
    to_recommendation_model_approval_comment_recommendation_model_approval3_command,
)
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class RecommendationModelApprovalServicer(
    recommendations_v1_recommendation_model_approval_service_pb2_grpc.RecommendationModelApprovalServiceServicer
):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    async def ApproveRecommendationModel(
        self, request: recommendations_v1_recommendation_model_approval_service_pb2.ApproveRecommendationModelRequest, context: grpc.aio.ServicerContext,
    ) -> recommendations_v1_recommendation_model_approval_service_pb2.ApproveRecommendationModelResponse:
        """Approves a recommendation model."""
        return await self.handle_approve_recommendation_model(request)

    @rpc_errors
    async def CommentRecommendationModelApproval(
        self, request: recommendations_v1_recommendation_model_approval_service_pb2.CommentRecommendationModelApprovalRequest, context: grpc.aio.ServicerContext,
    ) -> recommendations_v1_recommendation_model_approval_service_pb2.CommentRecommendationModelApprovalResponse:
        """Comments a recommendation model."""
        return await self.handle_comment_recommendation_model_approval(request)

    @rpc_errors
    async def DelegateRecommendationModelApproval(
        self, request: recommendations_v1_recommendation_model_approval_service_pb2.DelegateRecommendationModelApprovalRequest, context: grpc.aio.ServicerContext,
    ) -> recommendations_v1_recommendation_model_approval_service_pb2.DelegateRecommendationModelApprovalResponse:
        """Delegates a recommendation model."""
        return await self.handle_delegate_recommendation_model_approval(request)

    @rpc_errors
    async def EscalateRecommendationModel(
        self, request: recommendations_v1_recommendation_model_approval_service_pb2.EscalateRecommendationModelRequest, context: grpc.aio.ServicerContext,
    ) -> recommendations_v1_recommendation_model_approval_service_pb2.EscalateRecommendationModelResponse:
        """Escalates a recommendation model."""
        return await self.handle_escalate_recommendation_model(request)

    @rpc_errors
    @retry_transient
    async def GetRecommendationModelApprovalStatus(
        self, request: recommendations_v1_recommendation_model_approval_service_pb2.GetRecommendationModelApprovalStatusRequest, context: grpc.aio.ServicerContext,
    ) -> recommendations_v1_recommendation_model_approval_service_pb2.GetRecommendationModelApprovalStatusResponse:
        """Returns a recommendation model."""
        return await self.handle_get_recommendation_model_approval_status(request)

    @rpc_errors
    @retry_transient
    async def ListPendingRecommendationModels(
        self, request: recommendations_v1_recommendation_model_approval_service_pb2.ListPendingRecommendationModelsRequest, context: grpc.aio.ServicerContext,
    ) -> recommendations_v1_recommendation_model_approval_service_pb2.ListPendingRecommendationModelsResponse:
        """Lists recommendation models a page at a time."""
        return await self.handle_list_pending_recommendation_models(request)

    @rpc_errors
    async def RecallRecommendationModel(
        self, request: recommendations_v1_recommendation_model_approval_service_pb2.RecallRecommendationModelRequest, context: grpc.aio.ServicerContext,
    ) -> recommendations_v1_recommendation_model_approval_service_pb2.RecallRecommendationModelResponse:
        """Recalls a recommendation model."""
        return await self.handle_recall_recommendation_model(request)

    @rpc_errors
    async def RejectRecommendationModel(
        self, request: recommendations_v1_recommendation_model_approval_service_pb2.RejectRecommendationModelRequest, context: grpc.aio.ServicerContext,
    ) -> recommendations_v1_recommendation_model_approval_service_pb2.RejectRecommendationModelResponse:
        """Rejects a recommendation model."""
        return await self.handle_reject_recommendation_model(request)

    @rpc_errors
    async def SubmitRecommendationModel(
        self, request: recommendations_v1_recommendation_model_approval_service_pb2.SubmitRecommendationModelRequest, context: grpc.aio.ServicerContext,
    ) -> recommendations_v1_recommendation_model_approval_service_pb2.SubmitRecommendationModelResponse:
        """Submits a recommendation model."""
        return await self.handle_submit_recommendation_model(request)

    async def handle_approve_recommendation_model(
        self,
        request: recommendations_v1_recommendation_model_approval_service_pb2.ApproveRecommendationModelRequest
    ) -> recommendations_v1_recommendation_model_approval_service_pb2.ApproveRecommendationModelResponse:
        """Approves a recommendation model."""
        deps = self.deps
        response = recommendations_v1_recommendation_model_approval_service_pb2.ApproveRecommendationModelResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ApproveRecommendationModel', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ApproveRecommendationModel',
                {'reason': request.reason}
            )
            await deps.repository.save_recommendation_model(request.context.tenant_id, request.recommendation_model)
            response_0 = recommendations_v1_recommendation_set_service_pb2.ListRecommendationSetsResponse()
            response_1 = ledger_v1_ledger_account_validation_service_pb2.PreviewLedgerAccountResponse()
            outgoing_0 = recommendations_v1_recommendation_set_service_pb2.ListRecommendationSetsRequest(
                context=request.context,
                filter=recommendations_v1_recommendation_set_service_pb2.ListRecommendationSetsRequest.Filter(
                    created_after=request.details.effective_at,
                    owner_id=request.recommendation_model.components.get(
                        'primary',
                        recommendations_v1_recommendations_pb2.RecommendationModelComponent()
                    ).component_id,
                    region=request.recommendation_model.address.region
                )
            )
            document_0 = MessageToDict(outgoing_0, preserving_proto_field_name=True)
            outgoing_0 = ParseDict(
                document_0,
                recommendations_v1_recommendation_set_service_pb2.ListRecommendationSetsRequest()
            )
            response_0 = await deps.clients.recommendations_recommendation_set.ListRecommendationSets(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = ledger_v1_ledger_account_validation_service_pb2.PreviewLedgerAccountRequest(
                context=request.context,
                ledger_account=ledger_v1_ledger_pb2.LedgerAccount(
                    audit=common_v1_audit_pb2.AuditInfo(
                        created_by=request.recommendation_model.audit.created_by,
                        etag=request.recommendation_model.audit.etag
                    ),
                    contact=common_v1_contact_pb2.ContactInfo(email=request.recommendation_model.owner.email)
                )
            )
            document_1 = MessageToJson(outgoing_1, preserving_proto_field_name=True)
            outgoing_1 = Parse(
                document_1,
                ledger_v1_ledger_account_validation_service_pb2.PreviewLedgerAccountRequest()
            )
            response_1 = await deps.clients.ledger_ledger_account_validation.PreviewLedgerAccount(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_0)
            returned_0_1 = response_0.result.details
            response.result.details.update(returned_0_1)
            returned_1_0 = response_1.ledger_account.audit.updated_by
            if returned_1_0:
                response.recommendation_model.audit.updated_by = returned_1_0
            returned_1_1 = response_1.outcome.effective_at
            if returned_1_1.ListFields():
                response.outcome.effective_at.MergeFrom(returned_1_1)
            echoed_0 = request.recommendation_model_id
            response.recommendation_model.recommendation_model_id = echoed_0
            echoed_1 = request.recommendation_model.status
            response.recommendation_model.status = echoed_1
            return response

    async def handle_comment_recommendation_model_approval(
        self,
        request: recommendations_v1_recommendation_model_approval_service_pb2.CommentRecommendationModelApprovalRequest
    ) -> recommendations_v1_recommendation_model_approval_service_pb2.CommentRecommendationModelApprovalResponse:
        """Comments a recommendation model."""
        deps = self.deps
        response = recommendations_v1_recommendation_model_approval_service_pb2.CommentRecommendationModelApprovalResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CommentRecommendationModelApproval', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'CommentRecommendationModelApproval',
                {'reason': request.reason}
            )
            await deps.repository.save_recommendation_model(request.context.tenant_id, request.recommendation_model)
            response_0 = recommendations_v1_recommendation_set_validation_service_pb2.LintRecommendationSetsResponse()
            response_1 = recommendations_v1_interaction_calculation_service_pb2.ExplainInteractionCalculationResponse()
            response_2 = pricing_v1_price_list_service_pb2.BatchGetPriceListsResponse()
            response_3 = recommendations_v1_recommendation_model_calculation_service_pb2.QuoteRecommendationModelResponse()
            outgoing_0 = recommendations_v1_recommendation_set_validation_service_pb2.LintRecommendationSetsRequest()
            outgoing_0.context.CopyFrom(request.context)
            outgoing_0.recommendation_set.counterparty.display_name = request.details.approver.display_name
            outgoing_0.recommendation_set.audit.updated_by = request.recommendation_model.audit.updated_by
            merged_0 = recommendations_v1_recommendation_set_validation_service_pb2.LintRecommendationSetsRequest()
            merged_0.MergeFrom(outgoing_0)
            outgoing_0.CopyFrom(merged_0)
            response_0 = await deps.clients.recommendations_recommendation_set_validation.LintRecommendationSets(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = recommendations_v1_interaction_calculation_service_pb2.ExplainInteractionCalculationRequest(
                context=request.context,
                details=recommendations_v1_interaction_calculation_service_pb2.ExplainInteractionCalculationRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(email=request.details.approver.email)
                ),
                interaction=recommendations_v1_recommendations_pb2.Interaction(
                    measurements=[
                        recommendations_v1_recommendations_pb2.InteractionMeasurement(
                            unit=request.recommendation_model.dimensions.unit
                        )
                    ],
                    subject=customers_v1_refs_pb2.CustomerRef(
                        display_name=response_0.recommendation_set.counterparty.display_name,
                        email=request.recommendation_model.owner.email
                    )
                )
            )
            envelope_1 = AnyMessage()
            envelope_1.Pack(outgoing_1)
            outgoing_1 = recommendations_v1_interaction_calculation_service_pb2.ExplainInteractionCalculationRequest()
            if not envelope_1.Unpack(outgoing_1):
                raise ValueError("partner envelope contains the wrong request type")
            response_1 = await deps.clients.recommendations_interaction_calculation.ExplainInteractionCalculation(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = pricing_v1_price_list_service_pb2.BatchGetPriceListsRequest(context=request.context)
            registered_2 = cast(
                pricing_v1_price_list_service_pb2_grpc.PriceListServiceStub,
                deps.clients.registry['acme.pricing.v1.PriceListService']
            )
            response_2 = await registered_2.BatchGetPriceLists(outgoing_2, timeout=deps.settings.timeout)
            command_3 = RecommendationModelApprovalCommentRecommendationModelApproval3Command(
                context=request.context,
                recommendation_model_owner_display_name=response_0.recommendation_set.counterparty.display_name
            )
            outgoing_3 = to_recommendation_model_approval_comment_recommendation_model_approval3_command(command_3)
            response_3 = await deps.clients.recommendations_recommendation_model_calculation.QuoteRecommendationModel(
                outgoing_3,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.recommendation_set.counterparty.display_name
            if returned_0_0:
                response.recommendation_model.owner.display_name = returned_0_0
            returned_1_0 = response_1.outcome.status
            if returned_1_0:
                response.result.status = returned_1_0
            returned_2_0 = response_2.result.reference_ids
            response.result.reference_ids.extend(returned_2_0)
            returned_3_0 = response_3.recommendation_model.owner
            if returned_3_0.ListFields():
                response.recommendation_model.owner.MergeFrom(returned_3_0)
            echoed_0 = request.recommendation_model_id
            response.recommendation_model.recommendation_model_id = echoed_0
            echoed_1 = request.recommendation_model.specs
            response.recommendation_model.specs.update(echoed_1)
            return response

    async def handle_delegate_recommendation_model_approval(
        self,
        request: recommendations_v1_recommendation_model_approval_service_pb2.DelegateRecommendationModelApprovalRequest
    ) -> recommendations_v1_recommendation_model_approval_service_pb2.DelegateRecommendationModelApprovalResponse:
        """Delegates a recommendation model."""
        deps = self.deps
        response = recommendations_v1_recommendation_model_approval_service_pb2.DelegateRecommendationModelApprovalResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('DelegateRecommendationModelApproval', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'DelegateRecommendationModelApproval',
                {'reason': request.reason}
            )
            await deps.repository.save_recommendation_model(request.context.tenant_id, request.recommendation_model)
            response_0 = pipelines_v1_pipeline_step_export_service_pb2.RetryPipelineStepExportResponse()
            response_1 = recommendations_v1_interaction_calculation_service_pb2.SimulateInteractionResponse()
            response_2 = recommendations_v1_interaction_validation_service_pb2.ExplainInteractionDecisionResponse()
            response_3 = labeling_v1_labeling_task_approval_service_pb2.RecallLabelingTaskResponse()
            outgoing_0 = pipelines_v1_pipeline_step_export_service_pb2.RetryPipelineStepExportRequest(
                context=request.context,
                details=pipelines_v1_pipeline_step_export_service_pb2.RetryPipelineStepExportRequest.Details(
                    notify=common_v1_contact_pb2.ContactInfo(email=request.details.approver.email)
                ),
                pipeline_step=pipelines_v1_pipelines_pb2.PipelineStep(
                    audit=common_v1_audit_pb2.AuditInfo(
                        created_at=request.recommendation_model.audit.created_at,
                        created_by=request.recommendation_model.audit.created_by
                    )
                )
            )
            outgoing_1 = recommendations_v1_interaction_calculation_service_pb2.SimulateInteractionRequest(
                context=request.context,
                interaction=recommendations_v1_recommendations_pb2.Interaction(
                    subject=customers_v1_refs_pb2.CustomerRef(email=request.recommendation_model.owner.email)
                )
            )
            outgoing_3 = labeling_v1_labeling_task_approval_service_pb2.RecallLabelingTaskRequest(
                context=request.context,
                labeling_task=labeling_v1_labeling_pb2.LabelingTask(
                    assignee=identity_v1_refs_pb2.UserRef(email=request.details.approver.email),
                    customer=labeling_v1_refs_pb2.LabelSetRef(
                        display_name=request.recommendation_model.owner.display_name
                    )
                )
            )
            response_0, response_1, response_3 = await asyncio.gather(
                deps.clients.pipelines_pipeline_step_export.RetryPipelineStepExport(
                    outgoing_0,
                    timeout=deps.settings.timeout
                ),
                deps.clients.recommendations_interaction_calculation.SimulateInteraction(
                    outgoing_1,
                    timeout=deps.settings.timeout
                ),
                deps.clients.labeling_labeling_task_approval.RecallLabelingTask(
                    outgoing_3,
                    timeout=deps.settings.timeout
                ),
            )
            outgoing_2 = recommendations_v1_interaction_validation_service_pb2.ExplainInteractionDecisionRequest(
                context=request.context,
                details=recommendations_v1_interaction_validation_service_pb2.ExplainInteractionDecisionRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(email=request.recommendation_model.owner.email)
                ),
                interaction=recommendations_v1_recommendations_pb2.Interaction(
                    measurements=[
                        recommendations_v1_recommendations_pb2.InteractionMeasurement(
                            unit=request.recommendation_model.dimensions.unit
                        )
                    ],
                    subject=customers_v1_refs_pb2.CustomerRef(
                        display_name=request.recommendation_model.owner.display_name,
                        email=response_1.interaction.subject.email
                    )
                )
            )
            response_2 = await hooks.recommendation_model_approval_delegate_recommendation_model_approval2(
                deps.clients.recommendations_interaction_validation,
                outgoing_2,
                deps.settings.timeout
            )
            returned_0_0 = response_0.pipeline_step.audit.updated_at
            if returned_0_0.ListFields():
                response.recommendation_model.audit.updated_at.MergeFrom(returned_0_0)
            returned_1_0 = response_1.result.message
            if returned_1_0:
                response.result.message = returned_1_0
            returned_1_1 = response_1.result.correlation_id
            if returned_1_1:
                response.result.correlation_id = returned_1_1
            returned_2_0 = response_2.outcome.message
            if returned_2_0:
                response.outcome.message = returned_2_0
            returned_2_1 = response_2.outcome.next_steps
            response.outcome.next_steps.extend(returned_2_1)
            returned_3_0 = response_3.result.reference_ids
            response.result.reference_ids.extend(returned_3_0)
            returned_3_1 = response_3.result.status
            if returned_3_1:
                response.outcome.status = returned_3_1
            echoed_0 = request.recommendation_model_id
            response.recommendation_model.recommendation_model_id = echoed_0
            echoed_1 = request.recommendation_model.specs
            response.recommendation_model.specs.update(echoed_1)
            return response

    async def handle_escalate_recommendation_model(
        self,
        request: recommendations_v1_recommendation_model_approval_service_pb2.EscalateRecommendationModelRequest
    ) -> recommendations_v1_recommendation_model_approval_service_pb2.EscalateRecommendationModelResponse:
        """Escalates a recommendation model."""
        deps = self.deps
        response = recommendations_v1_recommendation_model_approval_service_pb2.EscalateRecommendationModelResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('EscalateRecommendationModel', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'EscalateRecommendationModel',
                {'reason': request.reason}
            )
            await deps.repository.save_recommendation_model(request.context.tenant_id, request.recommendation_model)
            response_0 = customers_v1_household_validation_service_pb2.ScoreHouseholdResponse()
            outgoing_0 = customers_v1_household_validation_service_pb2.ScoreHouseholdRequest(
                context=request.context,
                household=customers_v1_customers_pb2.Household(
                    children=[
                        customers_v1_customers_pb2.Household(
                            children=[
                                customers_v1_customers_pb2.Household(
                                    location=common_v1_address_pb2.PostalAddress(
                                        region=request.recommendation_model.address.region
                                    ),
                                    manager=identity_v1_refs_pb2.UserRef(
                                        display_name=request.details.approver.display_name
                                    )
                                )
                            ]
                        )
                    ]
                )
            )
            port_0: RecommendationModelApprovalEscalateRecommendationModel0Port = RecommendationModelApprovalEscalateRecommendationModel0Adapter(
                deps.clients.customers_household_validation,
                deps.settings.timeout
            )
            response_0 = await port_0.execute(outgoing_0)
            returned_0_0 = response_0.household.audit.updated_by
            if returned_0_0:
                response.recommendation_model.audit.updated_by = returned_0_0
            echoed_0 = request.recommendation_model_id
            response.recommendation_model.recommendation_model_id = echoed_0
            echoed_1 = request.recommendation_model.name
            response.recommendation_model.name = echoed_1
            return response

    async def handle_get_recommendation_model_approval_status(
        self,
        request: recommendations_v1_recommendation_model_approval_service_pb2.GetRecommendationModelApprovalStatusRequest
    ) -> recommendations_v1_recommendation_model_approval_service_pb2.GetRecommendationModelApprovalStatusResponse:
        """Returns a recommendation model."""
        deps = self.deps
        response = recommendations_v1_recommendation_model_approval_service_pb2.GetRecommendationModelApprovalStatusResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('GetRecommendationModelApprovalStatus', extra={'fields': {'domain': 'recommendations'}})
            await deps.repository.audit(request.context.tenant_id, 'GetRecommendationModelApprovalStatus', {})
            response_0 = recommendations_v1_recommendation_set_approval_service_pb2.EscalateRecommendationSetResponse()
            response_1 = metrics_v1_metric_alert_notification_service_pb2.SubscribeMetricAlertUpdatesResponse()
            outgoing_0 = recommendations_v1_recommendation_set_approval_service_pb2.EscalateRecommendationSetRequest(
                context=request.context,
                details=recommendations_v1_recommendation_set_approval_service_pb2.EscalateRecommendationSetRequest.Details(
                    approver=identity_v1_refs_pb2.UserRef(user_id=request.context.actor.user_id)
                ),
                recommendation_set=recommendations_v1_recommendations_pb2.RecommendationSet(
                    counterparty=customers_v1_refs_pb2.CustomerRef(email=request.context.actor.email)
                )
            )
            response_0 = await deps.clients.recommendations_recommendation_set_approval.EscalateRecommendationSet(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = metrics_v1_metric_alert_notification_service_pb2.SubscribeMetricAlertUpdatesRequest(
                context=request.context,
                details=metrics_v1_metric_alert_notification_service_pb2.SubscribeMetricAlertUpdatesRequest.Details(
                    recipient=common_v1_contact_pb2.ContactInfo(email=response_0.recommendation_set.counterparty.email)
                )
            )
            response_1 = await RecommendationModelApprovalGetRecommendationModelApprovalStatus1Adapter(
                deps.clients.metrics_metric_alert_notification,
                deps.settings.timeout
            )(outgoing_1)
            returned_0_0 = response_0.recommendation_set.audit.etag
            if returned_0_0:
                response.recommendation_model.audit.etag = returned_0_0
            returned_0_1 = response_0.recommendation_set.audit.created_at
            if returned_0_1.ListFields():
                response.recommendation_model.audit.created_at.MergeFrom(returned_0_1)
            returned_1_0 = response_1.metric_alert.description
            if returned_1_0:
                response.recommendation_model.components['primary'].description = returned_1_0
            echoed_0 = request.recommendation_model_id
            response.recommendation_model.recommendation_model_id = echoed_0
            return response

    async def handle_list_pending_recommendation_models(
        self,
        request: recommendations_v1_recommendation_model_approval_service_pb2.ListPendingRecommendationModelsRequest
    ) -> recommendations_v1_recommendation_model_approval_service_pb2.ListPendingRecommendationModelsResponse:
        """Lists recommendation models a page at a time."""
        deps = self.deps
        response = recommendations_v1_recommendation_model_approval_service_pb2.ListPendingRecommendationModelsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ListPendingRecommendationModels', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ListPendingRecommendationModels',
                {'order_by': request.order_by}
            )
            response_0 = customers_v1_household_query_service_pb2.BrowseHouseholdsResponse()
            outgoing_0 = customers_v1_household_query_service_pb2.BrowseHouseholdsRequest(
                context=request.context,
                filter=customers_v1_household_query_service_pb2.BrowseHouseholdsRequest.Filter(
                    owner_id=request.filter.owner_id
                )
            )
            response_0 = await deps.clients.customers_household_query.BrowseHouseholds(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.correlation_id
            if returned_0_0:
                response.result.correlation_id = returned_0_0
            return response

    async def handle_recall_recommendation_model(
        self,
        request: recommendations_v1_recommendation_model_approval_service_pb2.RecallRecommendationModelRequest
    ) -> recommendations_v1_recommendation_model_approval_service_pb2.RecallRecommendationModelResponse:
        """Recalls a recommendation model."""
        deps = self.deps
        response = recommendations_v1_recommendation_model_approval_service_pb2.RecallRecommendationModelResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('RecallRecommendationModel', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'RecallRecommendationModel',
                {'reason': request.reason}
            )
            await deps.repository.save_recommendation_model(request.context.tenant_id, request.recommendation_model)
            response_0 = labeling_v1_label_set_workflow_service_pb2.ResumeLabelSetWorkflowResponse()
            outgoing_0 = labeling_v1_label_set_workflow_service_pb2.ResumeLabelSetWorkflowRequest(
                context=request.context,
                label_set=labeling_v1_labeling_pb2.LabelSet(
                    children=[
                        labeling_v1_labeling_pb2.LabelSet(
                            children=[
                                labeling_v1_labeling_pb2.LabelSet(
                                    manager=identity_v1_refs_pb2.UserRef(
                                        display_name=request.details.approver.display_name
                                    )
                                )
                            ]
                        )
                    ]
                )
            )
            response_0 = await deps.clients.labeling_label_set_workflow.ResumeLabelSetWorkflow(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.label_set.audit.created_at
            if returned_0_0.ListFields():
                response.recommendation_model.audit.created_at.MergeFrom(returned_0_0)
            echoed_0 = request.recommendation_model_id
            response.recommendation_model.recommendation_model_id = echoed_0
            echoed_1 = request.recommendation_model.name
            response.recommendation_model.name = echoed_1
            return response

    async def handle_reject_recommendation_model(
        self,
        request: recommendations_v1_recommendation_model_approval_service_pb2.RejectRecommendationModelRequest
    ) -> recommendations_v1_recommendation_model_approval_service_pb2.RejectRecommendationModelResponse:
        """Rejects a recommendation model."""
        deps = self.deps
        response = recommendations_v1_recommendation_model_approval_service_pb2.RejectRecommendationModelResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('RejectRecommendationModel', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'RejectRecommendationModel',
                {'reason': request.reason}
            )
            await deps.repository.save_recommendation_model(request.context.tenant_id, request.recommendation_model)
            response_0 = customers_v1_consent_record_calculation_service_pb2.CompareConsentRecordOptionsResponse()
            response_1 = recommendations_v1_recommendation_set_approval_service_pb2.SubmitRecommendationSetResponse()
            response_2 = ledger_v1_ledger_account_query_service_pb2.FindLedgerAccountsResponse()
            response_3 = recommendations_v1_recommendation_set_approval_service_pb2.EscalateRecommendationSetResponse()
            outgoing_0 = customers_v1_consent_record_calculation_service_pb2.CompareConsentRecordOptionsRequest(
                consent_record=customers_v1_customers_pb2.ConsentRecord(
                    subject=customers_v1_refs_pb2.HouseholdRef(display_name=request.details.approver.display_name)
                ),
                context=request.context,
                details=customers_v1_consent_record_calculation_service_pb2.CompareConsentRecordOptionsRequest.Details(
                    destination=common_v1_address_pb2.PostalAddress(
                        postal_code=request.recommendation_model.address.postal_code
                    )
                )
            )
            method_name_0 = 'CompareConsentRecordOptions'
            response_0 = await getattr(
                deps.clients.customers_consent_record_calculation,
                method_name_0
            )(outgoing_0, timeout=deps.settings.timeout)
            fields_1: dict[str, Any] = {
                'context': request.context,
                'recommendation_set': {
                    'billing_address': {'recipient': request.recommendation_model.address.recipient},
                    'counterparty': {'display_name': request.recommendation_model.owner.display_name}
                }
            }
            outgoing_1 = recommendations_v1_recommendation_set_approval_service_pb2.SubmitRecommendationSetRequest(**fields_1)
            response_1 = await deps.clients.recommendations_recommendation_set_approval.SubmitRecommendationSet(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = ledger_v1_ledger_account_query_service_pb2.FindLedgerAccountsRequest()
            outgoing_2.context.CopyFrom(request.context)
            if request.recommendation_model.WhichOneof('locator') == 'address':
                outgoing_2.filter.region = request.recommendation_model.address.region
            outgoing_2.filter.created_after.CopyFrom(request.recommendation_model.audit.created_at)
            outgoing_2.filter.owner_id = request.recommendation_model.owner.user_id
            outgoing_2.filter.labels.update(dict(request.annotations))
            response_2 = await deps.clients.ledger_ledger_account_query.FindLedgerAccounts(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            outgoing_3 = recommendations_v1_recommendation_set_approval_service_pb2.EscalateRecommendationSetRequest(
                context=request.context,
                details=recommendations_v1_recommendation_set_approval_service_pb2.EscalateRecommendationSetRequest.Details(
                    approver=identity_v1_refs_pb2.UserRef(display_name=response_0.consent_record.subject.display_name)
                ),
                recommendation_set=recommendations_v1_recommendations_pb2.RecommendationSet(
                    card=recommendations_v1_recommendations_pb2.RecommendationSetCardSettlement(
                        network=response_1.recommendation_set.card.network
                    )
                )
            )
            document_3 = MessageToJson(outgoing_3, preserving_proto_field_name=True)
            outgoing_3 = Parse(
                document_3,
                recommendations_v1_recommendation_set_approval_service_pb2.EscalateRecommendationSetRequest()
            )
            response_3 = await deps.clients.recommendations_recommendation_set_approval.EscalateRecommendationSet(
                outgoing_3,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.result.message = returned_0_0
            returned_1_0 = response_1.outcome.status
            if returned_1_0:
                response.outcome.status = returned_1_0
            returned_1_1 = response_1.result.message
            if returned_1_1:
                response.result.message = returned_1_1
            returned_2_0 = response_2.result.status
            if returned_2_0:
                response.outcome.status = returned_2_0
            returned_2_1 = response_2.result.details
            response.result.details.update(returned_2_1)
            returned_3_0 = response_3.outcome.status
            if returned_3_0:
                response.outcome.status = returned_3_0
            returned_3_1 = response_3.recommendation_set.counterparty.display_name
            if returned_3_1:
                response.recommendation_model.owner.display_name = returned_3_1
            echoed_0 = request.recommendation_model_id
            response.recommendation_model.recommendation_model_id = echoed_0
            echoed_1 = request.recommendation_model.capacity
            response.recommendation_model.capacity = echoed_1
            return response

    async def handle_submit_recommendation_model(
        self,
        request: recommendations_v1_recommendation_model_approval_service_pb2.SubmitRecommendationModelRequest
    ) -> recommendations_v1_recommendation_model_approval_service_pb2.SubmitRecommendationModelResponse:
        """Submits a recommendation model."""
        deps = self.deps
        response = recommendations_v1_recommendation_model_approval_service_pb2.SubmitRecommendationModelResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SubmitRecommendationModel', extra={'fields': {'approver_email': request.details.approver_email}})
            await deps.repository.audit(
                request.context.tenant_id,
                'SubmitRecommendationModel',
                {'approver_email': request.details.approver_email}
            )
            await deps.repository.save_recommendation_model(request.context.tenant_id, request.recommendation_model)
            response_0 = audit_v1_audit_event_validation_service_pb2.NormalizeAuditEventResponse()
            outgoing_0 = audit_v1_audit_event_validation_service_pb2.NormalizeAuditEventRequest()
            outgoing_0.context.CopyFrom(request.context)
            outgoing_0.details.contact.email = request.recommendation_model.owner.email
            field_0_2_part_1 = outgoing_0.audit_event.measurements.add()
            field_0_2_part_1.unit = request.recommendation_model.dimensions.unit
            outgoing_0.audit_event.subject.display_name = request.recommendation_model.owner.display_name
            outgoing_0.reason = request.reason
            merged_0 = audit_v1_audit_event_validation_service_pb2.NormalizeAuditEventRequest()
            merged_0.MergeFrom(outgoing_0)
            outgoing_0.CopyFrom(merged_0)
            response_0 = await deps.clients.audit_audit_event_validation.NormalizeAuditEvent(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.outcome.status
            if returned_0_0:
                response.outcome.status = returned_0_0
            returned_0_1 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_1)
            echoed_0 = request.recommendation_model_id
            response.recommendation_model.recommendation_model_id = echoed_0
            echoed_1 = request.recommendation_model.owner
            response.recommendation_model.owner.CopyFrom(echoed_1)
            return response
