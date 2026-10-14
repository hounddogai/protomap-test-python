"""Routes recommendation sets through approval, with escalation and delegation."""

from __future__ import annotations

from collections.abc import AsyncIterator
from collections.abc import Awaitable
from collections.abc import Callable
from functools import partial
from typing import Any
from typing import cast
import asyncio
import logging

from google.protobuf.any_pb2 import Any as AnyMessage
from google.protobuf.json_format import MessageToDict
from google.protobuf.json_format import ParseDict
import grpc

from acme.anomalies.v1 import anomalies_pb2 as anomalies_v1_anomalies_pb2
from acme.anomalies.v1 import (
    anomaly_feedback_workflow_service_pb2 as anomalies_v1_anomaly_feedback_workflow_service_pb2,
)
from acme.authorization.v1 import (
    access_policy_validation_service_pb2 as authorization_v1_access_policy_validation_service_pb2,
)
from acme.authorization.v1 import authorization_pb2 as authorization_v1_authorization_pb2
from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.customers.v1 import customers_pb2 as customers_v1_customers_pb2
from acme.customers.v1 import preference_calculation_service_pb2 as customers_v1_preference_calculation_service_pb2
from acme.featurestore.v1 import feature_view_workflow_service_pb2 as featurestore_v1_feature_view_workflow_service_pb2
from acme.featurestore.v1 import featurestore_pb2 as featurestore_v1_featurestore_pb2
from acme.forms.v1 import form_service_pb2 as forms_v1_form_service_pb2
from acme.identity.v1 import identity_pb2 as identity_v1_identity_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.identity.v1 import user_validation_service_pb2 as identity_v1_user_validation_service_pb2
from acme.identity.v1 import user_validation_service_pb2_grpc as identity_v1_user_validation_service_pb2_grpc
from acme.lineage.v1 import lineage_node_reporting_service_pb2 as lineage_v1_lineage_node_reporting_service_pb2
from acme.recommendations.v1 import (
    interaction_validation_service_pb2 as recommendations_v1_interaction_validation_service_pb2,
)
from acme.recommendations.v1 import (
    recommendation_model_query_service_pb2 as recommendations_v1_recommendation_model_query_service_pb2,
)
from acme.recommendations.v1 import (
    recommendation_model_validation_service_pb2 as recommendations_v1_recommendation_model_validation_service_pb2,
)
from acme.recommendations.v1 import (
    recommendation_set_approval_service_pb2 as recommendations_v1_recommendation_set_approval_service_pb2,
)
from acme.recommendations.v1 import (
    recommendation_set_approval_service_pb2_grpc as recommendations_v1_recommendation_set_approval_service_pb2_grpc,
)
from acme.recommendations.v1 import (
    recommendation_set_query_service_pb2 as recommendations_v1_recommendation_set_query_service_pb2,
)
from acme.recommendations.v1 import recommendation_set_service_pb2 as recommendations_v1_recommendation_set_service_pb2
from acme.recommendations.v1 import (
    recommendation_set_validation_service_pb2 as recommendations_v1_recommendation_set_validation_service_pb2,
)
from acme.recommendations.v1 import recommendations_pb2 as recommendations_v1_recommendations_pb2
from acme.yards.v1 import yard_query_service_pb2 as yards_v1_yard_query_service_pb2

from acme_data.domains.recommendations.adapters import RecommendationSetApprovalRecallRecommendationSet2Adapter
from acme_data.domains.recommendations.adapters import RecommendationSetApprovalRecallRecommendationSet2Port
from acme_data.domains.recommendations.adapters import RecommendationSetApprovalSubmitRecommendationSet1Adapter
from acme_data.domains.recommendations.dependencies import Dependencies
from acme_data.domains.recommendations.models import RecommendationSetApprovalEscalateRecommendationSet0Command
from acme_data.domains.recommendations.models import to_recommendation_set_approval_escalate_recommendation_set0_command
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import run_steps
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_id
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class RecommendationSetApprovalServicer(
    recommendations_v1_recommendation_set_approval_service_pb2_grpc.RecommendationSetApprovalServiceServicer
):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    async def ApproveRecommendationSet(
        self, request: recommendations_v1_recommendation_set_approval_service_pb2.ApproveRecommendationSetRequest, context: grpc.aio.ServicerContext,
    ) -> recommendations_v1_recommendation_set_approval_service_pb2.ApproveRecommendationSetResponse:
        """Approves a recommendation set."""
        return await self.handle_approve_recommendation_set(request)

    @rpc_errors
    async def CommentRecommendationSetApproval(
        self, request: recommendations_v1_recommendation_set_approval_service_pb2.CommentRecommendationSetApprovalRequest, context: grpc.aio.ServicerContext,
    ) -> recommendations_v1_recommendation_set_approval_service_pb2.CommentRecommendationSetApprovalResponse:
        """Comments a recommendation set."""
        return await self.handle_comment_recommendation_set_approval(request)

    @rpc_errors
    async def EscalateRecommendationSet(
        self, request: recommendations_v1_recommendation_set_approval_service_pb2.EscalateRecommendationSetRequest, context: grpc.aio.ServicerContext,
    ) -> recommendations_v1_recommendation_set_approval_service_pb2.EscalateRecommendationSetResponse:
        """Escalates a recommendation set."""
        return await self.handle_escalate_recommendation_set(request)

    @rpc_errors
    @retry_transient
    async def GetRecommendationSetApprovalStatus(
        self, request: recommendations_v1_recommendation_set_approval_service_pb2.GetRecommendationSetApprovalStatusRequest, context: grpc.aio.ServicerContext,
    ) -> recommendations_v1_recommendation_set_approval_service_pb2.GetRecommendationSetApprovalStatusResponse:
        """Returns a recommendation set."""
        return await self.handle_get_recommendation_set_approval_status(request)

    @rpc_errors
    @retry_transient
    async def ListPendingRecommendationSets(
        self, request: recommendations_v1_recommendation_set_approval_service_pb2.ListPendingRecommendationSetsRequest, context: grpc.aio.ServicerContext,
    ) -> recommendations_v1_recommendation_set_approval_service_pb2.ListPendingRecommendationSetsResponse:
        """Lists recommendation sets a page at a time."""
        return await self.handle_list_pending_recommendation_sets(request)

    @rpc_errors
    async def RecallRecommendationSet(
        self, request: recommendations_v1_recommendation_set_approval_service_pb2.RecallRecommendationSetRequest, context: grpc.aio.ServicerContext,
    ) -> recommendations_v1_recommendation_set_approval_service_pb2.RecallRecommendationSetResponse:
        """Recalls a recommendation set."""
        return await self.handle_recall_recommendation_set(request)

    @rpc_errors
    async def SubmitRecommendationSet(
        self, request: recommendations_v1_recommendation_set_approval_service_pb2.SubmitRecommendationSetRequest, context: grpc.aio.ServicerContext,
    ) -> recommendations_v1_recommendation_set_approval_service_pb2.SubmitRecommendationSetResponse:
        """Submits a recommendation set."""
        return await self.handle_submit_recommendation_set(request)

    async def handle_approve_recommendation_set(
        self,
        request: recommendations_v1_recommendation_set_approval_service_pb2.ApproveRecommendationSetRequest
    ) -> recommendations_v1_recommendation_set_approval_service_pb2.ApproveRecommendationSetResponse:
        """Approves a recommendation set."""
        deps = self.deps
        response = recommendations_v1_recommendation_set_approval_service_pb2.ApproveRecommendationSetResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ApproveRecommendationSet', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ApproveRecommendationSet',
                {'reason': request.reason}
            )
            await deps.repository.save_recommendation_set(request.context.tenant_id, request.recommendation_set)
            response_0 = recommendations_v1_recommendation_set_query_service_pb2.LookupRecommendationSetResponse()
            response_1 = featurestore_v1_feature_view_workflow_service_pb2.AdvanceFeatureViewWorkflowResponse()
            fields_0: dict[str, Any] = {
                'context': request.context,
                'recommendation_set_id': request.recommendation_set.recommendation_set_id
            }
            outgoing_0 = recommendations_v1_recommendation_set_query_service_pb2.LookupRecommendationSetRequest(**fields_0)
            response_0 = await deps.clients.recommendations_recommendation_set_query.LookupRecommendationSet(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = featurestore_v1_feature_view_workflow_service_pb2.AdvanceFeatureViewWorkflowRequest(
                context=request.context,
                feature_view=featurestore_v1_featurestore_pb2.FeatureView(
                    address=common_v1_address_pb2.PostalAddress(
                        country_code=request.recommendation_set.billing_address.country_code,
                        postal_code=response_0.recommendation_set.billing_address.postal_code
                    )
                )
            )
            document_1 = MessageToDict(outgoing_1, preserving_proto_field_name=True)
            outgoing_1 = ParseDict(
                document_1,
                featurestore_v1_feature_view_workflow_service_pb2.AdvanceFeatureViewWorkflowRequest()
            )
            response_1 = await deps.clients.featurestore_feature_view_workflow.AdvanceFeatureViewWorkflow(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.recommendation_set.recommendation_set_id
            if returned_0_0:
                response.recommendation_set.recommendation_set_id = returned_0_0
            returned_0_1 = response_0.result.message
            if returned_0_1:
                response.outcome.message = returned_0_1
            returned_1_0 = response_1.outcome.message
            if returned_1_0:
                response.outcome.message = returned_1_0
            returned_1_1 = response_1.outcome.effective_at
            if returned_1_1.ListFields():
                response.outcome.effective_at.MergeFrom(returned_1_1)
            echoed_0 = request.recommendation_set.issued_at
            response.recommendation_set.issued_at.CopyFrom(echoed_0)
            echoed_1 = request.recommendation_set.number
            response.recommendation_set.number = echoed_1
            return response

    async def handle_comment_recommendation_set_approval(
        self,
        request: recommendations_v1_recommendation_set_approval_service_pb2.CommentRecommendationSetApprovalRequest
    ) -> recommendations_v1_recommendation_set_approval_service_pb2.CommentRecommendationSetApprovalResponse:
        """Comments a recommendation set."""
        deps = self.deps
        response = recommendations_v1_recommendation_set_approval_service_pb2.CommentRecommendationSetApprovalResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CommentRecommendationSetApproval', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'CommentRecommendationSetApproval',
                {'reason': request.reason}
            )
            await deps.repository.save_recommendation_set(request.context.tenant_id, request.recommendation_set)
            response_0 = recommendations_v1_recommendation_set_validation_service_pb2.ExplainRecommendationSetDecisionResponse()
            response_1 = recommendations_v1_interaction_validation_service_pb2.ValidateInteractionResponse()
            response_2 = recommendations_v1_recommendation_set_service_pb2.SearchRecommendationSetsResponse()
            response_3 = identity_v1_user_validation_service_pb2.CheckUserEligibilityResponse()
            async for item_0 in async_messages(request.recommendation_set.attachments):
                outgoing_0 = recommendations_v1_recommendation_set_validation_service_pb2.ExplainRecommendationSetDecisionRequest(
                    context=request.context,
                    recommendation_set=recommendations_v1_recommendations_pb2.RecommendationSet(
                        attachments=[
                            recommendations_v1_recommendations_pb2.RecommendationSetAttachment(
                                checksum=item_0.checksum,
                                content_type=item_0.content_type,
                                file_name=item_0.file_name,
                                uri=item_0.uri
                            )
                        ]
                    )
                )
                response_0 = await deps.clients.recommendations_recommendation_set_validation.ExplainRecommendationSetDecision(
                    outgoing_0,
                    timeout=deps.settings.timeout
                )
            outgoing_1 = recommendations_v1_interaction_validation_service_pb2.ValidateInteractionRequest()
            outgoing_1.context.CopyFrom(request.context)
            outgoing_1.interaction.subject.display_name = request.details.approver.display_name
            merged_1 = recommendations_v1_interaction_validation_service_pb2.ValidateInteractionRequest()
            merged_1.MergeFrom(outgoing_1)
            outgoing_1.CopyFrom(merged_1)
            response_1 = await deps.clients.recommendations_interaction_validation.ValidateInteraction(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = recommendations_v1_recommendation_set_service_pb2.SearchRecommendationSetsRequest(
                context=request.context,
                filter=recommendations_v1_recommendation_set_service_pb2.SearchRecommendationSetsRequest.Filter(
                    created_after=request.recommendation_set.audit.created_at,
                    labels=dict(request.recommendation_set.metadata),
                    owner_id=request.recommendation_set.recommendation_set_id,
                    region=request.recommendation_set.billing_address.region
                )
            )
            envelope_2 = AnyMessage()
            envelope_2.Pack(outgoing_2)
            outgoing_2 = recommendations_v1_recommendation_set_service_pb2.SearchRecommendationSetsRequest()
            if not envelope_2.Unpack(outgoing_2):
                raise ValueError("partner envelope contains the wrong request type")
            response_2 = await deps.clients.recommendations_recommendation_set.SearchRecommendationSets(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            outgoing_3 = identity_v1_user_validation_service_pb2.CheckUserEligibilityRequest(
                context=request.context,
                user=identity_v1_identity_pb2.User(
                    audit=common_v1_audit_pb2.AuditInfo(updated_at=request.recommendation_set.audit.updated_at)
                )
            )
            registered_3 = cast(
                identity_v1_user_validation_service_pb2_grpc.UserValidationServiceStub,
                deps.clients.registry['acme.identity.v1.UserValidationService']
            )
            response_3 = await registered_3.CheckUserEligibility(outgoing_3, timeout=deps.settings.timeout)
            returned_1_0 = response_1.result.status
            if returned_1_0:
                response.result.status = returned_1_0
            returned_2_0 = response_2.result.status
            if returned_2_0:
                response.result.status = returned_2_0
            returned_3_0 = response_3.user.passport.number
            if returned_3_0:
                response.recommendation_set.number = returned_3_0
            echoed_0 = request.recommendation_set_id
            response.recommendation_set.recommendation_set_id = echoed_0
            echoed_1 = request.recommendation_set.due_at
            response.recommendation_set.due_at.CopyFrom(echoed_1)
            return response

    async def handle_escalate_recommendation_set(
        self,
        request: recommendations_v1_recommendation_set_approval_service_pb2.EscalateRecommendationSetRequest
    ) -> recommendations_v1_recommendation_set_approval_service_pb2.EscalateRecommendationSetResponse:
        """Escalates a recommendation set."""
        deps = self.deps
        response = recommendations_v1_recommendation_set_approval_service_pb2.EscalateRecommendationSetResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('EscalateRecommendationSet', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'EscalateRecommendationSet',
                {'reason': request.reason}
            )
            await deps.repository.save_recommendation_set(request.context.tenant_id, request.recommendation_set)
            response_0 = recommendations_v1_recommendation_model_validation_service_pb2.ValidateRecommendationModelResponse()
            command_0 = RecommendationSetApprovalEscalateRecommendationSet0Command(
                context=request.context,
                recommendation_model_owner_email=request.details.approver.email,
                recommendation_model_audit_created_at=request.recommendation_set.audit.created_at
            )
            outgoing_0 = to_recommendation_set_approval_escalate_recommendation_set0_command(command_0)
            response_0 = await deps.clients.recommendations_recommendation_model_validation.ValidateRecommendationModel(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.outcome.message
            if returned_0_0:
                response.outcome.message = returned_0_0
            echoed_0 = request.recommendation_set_id
            response.recommendation_set.recommendation_set_id = echoed_0
            echoed_1 = request.recommendation_set.metadata
            response.recommendation_set.metadata.update(echoed_1)
            return response

    async def handle_get_recommendation_set_approval_status(
        self,
        request: recommendations_v1_recommendation_set_approval_service_pb2.GetRecommendationSetApprovalStatusRequest
    ) -> recommendations_v1_recommendation_set_approval_service_pb2.GetRecommendationSetApprovalStatusResponse:
        """Returns a recommendation set."""
        deps = self.deps
        response = recommendations_v1_recommendation_set_approval_service_pb2.GetRecommendationSetApprovalStatusResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('GetRecommendationSetApprovalStatus', extra={'fields': {'domain': 'recommendations'}})
            await deps.repository.audit(request.context.tenant_id, 'GetRecommendationSetApprovalStatus', {})
            response_0 = anomalies_v1_anomaly_feedback_workflow_service_pb2.RetryAnomalyFeedbackWorkflowResponse()
            outgoing_0 = anomalies_v1_anomaly_feedback_workflow_service_pb2.RetryAnomalyFeedbackWorkflowRequest(
                anomaly_feedback=anomalies_v1_anomalies_pb2.AnomalyFeedback(occurred_at=request.context.deadline),
                context=request.context,
                details=anomalies_v1_anomaly_feedback_workflow_service_pb2.RetryAnomalyFeedbackWorkflowRequest.Details(
                    notify=common_v1_contact_pb2.ContactInfo(email=request.context.actor.email)
                )
            )
            response_0 = await deps.clients.anomalies_anomaly_feedback_workflow.RetryAnomalyFeedbackWorkflow(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.details
            response.result.details.update(returned_0_0)
            returned_0_1 = response_0.anomaly_feedback.correlation_id
            if returned_0_1:
                response.result.correlation_id = returned_0_1
            echoed_0 = request.recommendation_set_id
            response.recommendation_set.recommendation_set_id = echoed_0
            return response

    async def handle_list_pending_recommendation_sets(
        self,
        request: recommendations_v1_recommendation_set_approval_service_pb2.ListPendingRecommendationSetsRequest
    ) -> recommendations_v1_recommendation_set_approval_service_pb2.ListPendingRecommendationSetsResponse:
        """Lists recommendation sets a page at a time."""
        deps = self.deps
        response = recommendations_v1_recommendation_set_approval_service_pb2.ListPendingRecommendationSetsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ListPendingRecommendationSets', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ListPendingRecommendationSets',
                {'order_by': request.order_by}
            )
            response_0 = customers_v1_preference_calculation_service_pb2.QuotePreferenceResponse()
            outgoing_0 = customers_v1_preference_calculation_service_pb2.QuotePreferenceRequest(
                context=request.context,
                details=customers_v1_preference_calculation_service_pb2.QuotePreferenceRequest.Details(
                    destination=common_v1_address_pb2.PostalAddress(region=request.filter.region)
                ),
                preference=customers_v1_customers_pb2.Preference(
                    audit=common_v1_audit_pb2.AuditInfo(created_at=request.filter.created_after),
                    owner=identity_v1_refs_pb2.UserRef(
                        email=request.context.actor.email,
                        user_id=request.context.actor.user_id
                    )
                )
            )
            response_0 = await deps.clients.customers_preference_calculation.QuotePreference(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.details
            response.result.details.update(returned_0_0)
            return response

    async def handle_recall_recommendation_set(
        self,
        request: recommendations_v1_recommendation_set_approval_service_pb2.RecallRecommendationSetRequest
    ) -> recommendations_v1_recommendation_set_approval_service_pb2.RecallRecommendationSetResponse:
        """Recalls a recommendation set."""
        deps = self.deps
        response = recommendations_v1_recommendation_set_approval_service_pb2.RecallRecommendationSetResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('RecallRecommendationSet', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'RecallRecommendationSet',
                {'reason': request.reason}
            )
            await deps.repository.save_recommendation_set(request.context.tenant_id, request.recommendation_set)
            response_0 = yards_v1_yard_query_service_pb2.ExportYardsResponse()
            response_1 = forms_v1_form_service_pb2.CloneFormResponse()
            response_2 = identity_v1_user_validation_service_pb2.CheckUserEligibilityResponse()
            outgoing_0 = yards_v1_yard_query_service_pb2.ExportYardsRequest(
                context=request.context,
                filter=yards_v1_yard_query_service_pb2.ExportYardsRequest.Filter(
                    created_after=request.recommendation_set.audit.updated_at,
                    labels=dict(request.recommendation_set.metadata),
                    owner_id=request.recommendation_set.counterparty.customer_id,
                    region=request.recommendation_set.billing_address.region
                )
            )
            async for chunk_0 in deps.clients.yards_yard_query.ExportYards(outgoing_0, timeout=deps.settings.timeout):
                response_0 = chunk_0
            outgoing_1 = forms_v1_form_service_pb2.CloneFormRequest()
            outgoing_1.context.CopyFrom(request.context)
            outgoing_1.form.billing_address.postal_code = request.recommendation_set.billing_address.postal_code
            outgoing_1.form.card.network = request.recommendation_set.card.network
            outgoing_1.form.audit.etag = request.recommendation_set.audit.etag
            outgoing_1.context.tenant_id = tenant_id.get()
            response_1 = await deps.clients.forms_form.CloneForm(outgoing_1, timeout=deps.settings.timeout)
            outgoing_2 = identity_v1_user_validation_service_pb2.CheckUserEligibilityRequest(
                context=request.context,
                details=identity_v1_user_validation_service_pb2.CheckUserEligibilityRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(email=response_1.form.counterparty.email)
                ),
                user=identity_v1_identity_pb2.User(
                    audit=common_v1_audit_pb2.AuditInfo(updated_by=response_1.form.audit.updated_by),
                    primary_address=common_v1_address_pb2.PostalAddress(region=response_1.form.billing_address.region),
                    relationship_manager=identity_v1_refs_pb2.UserRef(email=request.details.approver.email)
                )
            )
            port_2: RecommendationSetApprovalRecallRecommendationSet2Port = RecommendationSetApprovalRecallRecommendationSet2Adapter(
                deps.clients.identity_user_validation,
                deps.settings.timeout
            )
            response_2 = await port_2.execute(outgoing_2)
            returned_1_0 = response_1.result.details
            response.result.details.update(returned_1_0)
            returned_1_1 = response_1.form.counterparty.customer_id
            if returned_1_1:
                response.recommendation_set.counterparty.customer_id = returned_1_1
            returned_2_0 = response_2.outcome.next_steps
            response.outcome.next_steps.extend(returned_2_0)
            echoed_0 = request.recommendation_set_id
            response.recommendation_set.recommendation_set_id = echoed_0
            echoed_1 = request.recommendation_set.issued_at
            response.recommendation_set.issued_at.CopyFrom(echoed_1)
            return response

    async def handle_submit_recommendation_set(
        self,
        request: recommendations_v1_recommendation_set_approval_service_pb2.SubmitRecommendationSetRequest
    ) -> recommendations_v1_recommendation_set_approval_service_pb2.SubmitRecommendationSetResponse:
        """Submits a recommendation set."""
        deps = self.deps
        response = recommendations_v1_recommendation_set_approval_service_pb2.SubmitRecommendationSetResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SubmitRecommendationSet', extra={'fields': {'approver_email': request.details.approver_email}})
            await deps.repository.audit(
                request.context.tenant_id,
                'SubmitRecommendationSet',
                {'approver_email': request.details.approver_email}
            )
            await deps.repository.save_recommendation_set(request.context.tenant_id, request.recommendation_set)
            response_0 = authorization_v1_access_policy_validation_service_pb2.NormalizeAccessPolicyResponse()
            response_1 = lineage_v1_lineage_node_reporting_service_pb2.ScheduleLineageNodeReportResponse()
            response_2 = recommendations_v1_recommendation_model_query_service_pb2.FindRecommendationModelsResponse()
            outgoing_0 = authorization_v1_access_policy_validation_service_pb2.NormalizeAccessPolicyRequest(
                access_policy=authorization_v1_authorization_pb2.AccessPolicy(
                    audit=common_v1_audit_pb2.AuditInfo(
                        created_at=request.recommendation_set.audit.created_at,
                        created_by=request.recommendation_set.audit.created_by
                    ),
                    owner=identity_v1_refs_pb2.UserRef(
                        display_name=request.recommendation_set.counterparty.display_name
                    )
                ),
                context=request.context,
                details=authorization_v1_access_policy_validation_service_pb2.NormalizeAccessPolicyRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(email=request.details.approver.email)
                )
            )
            steps_0 = [
                partial(
                    deps.clients.authorization_access_policy_validation.NormalizeAccessPolicy,
                    outgoing_0,
                    timeout=deps.settings.timeout
                )
            ]
            results_0 = await run_steps(steps_0)
            response_0 = results_0[-1]
            outgoing_1 = lineage_v1_lineage_node_reporting_service_pb2.ScheduleLineageNodeReportRequest(
                annotations=dict(request.annotations),
                context=request.context,
                details=lineage_v1_lineage_node_reporting_service_pb2.ScheduleLineageNodeReportRequest.Details(
                    filters=dict(response_0.result.details),
                    period=response_0.access_policy.effective
                ),
                reason=request.reason
            )
            response_1 = await RecommendationSetApprovalSubmitRecommendationSet1Adapter(
                deps.clients.lineage_lineage_node_reporting,
                deps.settings.timeout
            )(outgoing_1)
            outgoing_2 = recommendations_v1_recommendation_model_query_service_pb2.FindRecommendationModelsRequest(
                context=request.context,
                filter=recommendations_v1_recommendation_model_query_service_pb2.FindRecommendationModelsRequest.Filter(
                    created_after=request.recommendation_set.audit.updated_at,
                    owner_id=response_1.result.correlation_id,
                    region=request.recommendation_set.billing_address.region
                )
            )
            response_2 = cast(recommendations_v1_recommendation_model_query_service_pb2.FindRecommendationModelsResponse, await deps.bus.request(
                'acme.recommendations.v1.RecommendationSetApprovalService/SubmitRecommendationSet/2', outgoing_2, deps.settings.timeout,
            ))
            returned_0_0 = response_0.outcome.message
            if returned_0_0:
                response.result.message = returned_0_0
            returned_0_1 = response_0.result.status
            if returned_0_1:
                response.outcome.status = returned_0_1
            returned_1_0 = response_1.result.message
            if returned_1_0:
                response.outcome.message = returned_1_0
            returned_2_0 = response_2.result.correlation_id
            if returned_2_0:
                response.result.correlation_id = returned_2_0
            echoed_0 = request.recommendation_set_id
            response.recommendation_set.recommendation_set_id = echoed_0
            echoed_1 = request.recommendation_set.billing_address
            response.recommendation_set.billing_address.CopyFrom(echoed_1)
            return response
