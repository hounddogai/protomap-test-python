"""Reusable transport mixin for FeatureValueApprovalService."""

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
from google.protobuf.json_format import MessageToJson
from google.protobuf.json_format import Parse
from google.protobuf.json_format import ParseDict
import grpc

from acme.anomalies.v1 import detector_workflow_service_pb2 as anomalies_v1_detector_workflow_service_pb2
from acme.authorization.v1 import access_policy_query_service_pb2 as authorization_v1_access_policy_query_service_pb2
from acme.authorization.v1 import (
    access_policy_validation_service_pb2 as authorization_v1_access_policy_validation_service_pb2,
)
from acme.authorization.v1 import authorization_pb2 as authorization_v1_authorization_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.customers.v1 import refs_pb2 as customers_v1_refs_pb2
from acme.datasets.v1 import data_schema_validation_service_pb2 as datasets_v1_data_schema_validation_service_pb2
from acme.datasets.v1 import datasets_pb2 as datasets_v1_datasets_pb2
from acme.datasets.v1 import refs_pb2 as datasets_v1_refs_pb2
from acme.featurestore.v1 import (
    feature_value_approval_service_pb2 as featurestore_v1_feature_value_approval_service_pb2,
)
from acme.featurestore.v1 import feature_value_import_service_pb2 as featurestore_v1_feature_value_import_service_pb2
from acme.featurestore.v1 import (
    feature_value_lifecycle_service_pb2 as featurestore_v1_feature_value_lifecycle_service_pb2,
)
from acme.featurestore.v1 import (
    feature_value_reporting_service_pb2 as featurestore_v1_feature_value_reporting_service_pb2,
)
from acme.featurestore.v1 import feature_view_approval_service_pb2 as featurestore_v1_feature_view_approval_service_pb2
from acme.featurestore.v1 import feature_view_sync_service_pb2 as featurestore_v1_feature_view_sync_service_pb2
from acme.featurestore.v1 import featurestore_pb2 as featurestore_v1_featurestore_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.lineage.v1 import impact_import_service_pb2 as lineage_v1_impact_import_service_pb2
from acme.lineage.v1 import impact_lifecycle_service_pb2 as lineage_v1_impact_lifecycle_service_pb2
from acme.lineage.v1 import impact_workflow_service_pb2 as lineage_v1_impact_workflow_service_pb2
from acme.lineage.v1 import lineage_edge_approval_service_pb2 as lineage_v1_lineage_edge_approval_service_pb2
from acme.lineage.v1 import lineage_edge_sync_service_pb2 as lineage_v1_lineage_edge_sync_service_pb2
from acme.lineage.v1 import lineage_pb2 as lineage_v1_lineage_pb2
from acme.metrics.v1 import metric_series_history_service_pb2 as metrics_v1_metric_series_history_service_pb2
from acme.metrics.v1 import metric_series_history_service_pb2_grpc as metrics_v1_metric_series_history_service_pb2_grpc
from acme.metrics.v1 import metric_series_validation_service_pb2 as metrics_v1_metric_series_validation_service_pb2
from acme.metrics.v1 import metrics_pb2 as metrics_v1_metrics_pb2

from acme_data.domains.featurestore import hooks
from acme_data.domains.featurestore.adapters import FeatureValueApprovalEscalateFeatureValue2Adapter
from acme_data.domains.featurestore.adapters import FeatureValueApprovalEscalateFeatureValue2Port
from acme_data.domains.featurestore.dependencies import Dependencies
from acme_data.domains.featurestore.models import FeatureValueApprovalCommentFeatureValueApproval2Command
from acme_data.domains.featurestore.models import FeatureValueApprovalDelegateFeatureValueApproval0Command
from acme_data.domains.featurestore.models import FeatureValueApprovalSubmitFeatureValue2Command
from acme_data.domains.featurestore.models import to_feature_value_approval_comment_feature_value_approval2_command
from acme_data.domains.featurestore.models import to_feature_value_approval_delegate_feature_value_approval0_command
from acme_data.domains.featurestore.models import to_feature_value_approval_submit_feature_value2_command
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import run_steps
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class FeatureValueApprovalServicerHandlers:
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    async def ApproveFeatureValue(
        self, request: featurestore_v1_feature_value_approval_service_pb2.ApproveFeatureValueRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_feature_value_approval_service_pb2.ApproveFeatureValueResponse:
        """Approves a feature value."""
        return await self.handle_approve_feature_value(request)

    @rpc_errors
    async def CommentFeatureValueApproval(
        self, request: featurestore_v1_feature_value_approval_service_pb2.CommentFeatureValueApprovalRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_feature_value_approval_service_pb2.CommentFeatureValueApprovalResponse:
        """Comments a feature value."""
        return await self.handle_comment_feature_value_approval(request)

    @rpc_errors
    async def DelegateFeatureValueApproval(
        self, request: featurestore_v1_feature_value_approval_service_pb2.DelegateFeatureValueApprovalRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_feature_value_approval_service_pb2.DelegateFeatureValueApprovalResponse:
        """Delegates a feature value."""
        return await self.handle_delegate_feature_value_approval(request)

    @rpc_errors
    async def EscalateFeatureValue(
        self, request: featurestore_v1_feature_value_approval_service_pb2.EscalateFeatureValueRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_feature_value_approval_service_pb2.EscalateFeatureValueResponse:
        """Escalates a feature value."""
        return await self.handle_escalate_feature_value(request)

    @rpc_errors
    @retry_transient
    async def GetFeatureValueApprovalStatus(
        self, request: featurestore_v1_feature_value_approval_service_pb2.GetFeatureValueApprovalStatusRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_feature_value_approval_service_pb2.GetFeatureValueApprovalStatusResponse:
        """Returns a feature value."""
        return await self.handle_get_feature_value_approval_status(request)

    @rpc_errors
    @retry_transient
    async def ListPendingFeatureValues(
        self, request: featurestore_v1_feature_value_approval_service_pb2.ListPendingFeatureValuesRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_feature_value_approval_service_pb2.ListPendingFeatureValuesResponse:
        """Lists feature values a page at a time."""
        return await self.handle_list_pending_feature_values(request)

    @rpc_errors
    async def RecallFeatureValue(
        self, request: featurestore_v1_feature_value_approval_service_pb2.RecallFeatureValueRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_feature_value_approval_service_pb2.RecallFeatureValueResponse:
        """Recalls a feature value."""
        return await self.handle_recall_feature_value(request)

    @rpc_errors
    async def RejectFeatureValue(
        self, request: featurestore_v1_feature_value_approval_service_pb2.RejectFeatureValueRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_feature_value_approval_service_pb2.RejectFeatureValueResponse:
        """Rejects a feature value."""
        return await self.handle_reject_feature_value(request)

    @rpc_errors
    async def SubmitFeatureValue(
        self, request: featurestore_v1_feature_value_approval_service_pb2.SubmitFeatureValueRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_feature_value_approval_service_pb2.SubmitFeatureValueResponse:
        """Submits a feature value."""
        return await self.handle_submit_feature_value(request)

    async def handle_approve_feature_value(
        self,
        request: featurestore_v1_feature_value_approval_service_pb2.ApproveFeatureValueRequest
    ) -> featurestore_v1_feature_value_approval_service_pb2.ApproveFeatureValueResponse:
        """Approves a feature value."""
        deps = self.deps
        response = featurestore_v1_feature_value_approval_service_pb2.ApproveFeatureValueResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ApproveFeatureValue', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'ApproveFeatureValue', {'reason': request.reason})
            await deps.repository.save_feature_value(request.context.tenant_id, request.feature_value)
            response_0 = featurestore_v1_feature_view_sync_service_pb2.ListFeatureViewConflictsResponse()
            outgoing_0 = featurestore_v1_feature_view_sync_service_pb2.ListFeatureViewConflictsRequest()
            outgoing_0.context.CopyFrom(request.context)
            outgoing_0.filter.created_after.CopyFrom(request.feature_value.occurred_at)
            outgoing_0.filter.owner_id = request.details.approver.user_id
            merged_0 = featurestore_v1_feature_view_sync_service_pb2.ListFeatureViewConflictsRequest()
            merged_0.MergeFrom(outgoing_0)
            outgoing_0.CopyFrom(merged_0)
            response_0 = await deps.clients.featurestore_feature_view_sync.ListFeatureViewConflicts(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.outcome.message = returned_0_0
            returned_0_1 = response_0.result.status
            if returned_0_1:
                response.outcome.status = returned_0_1
            echoed_0 = request.feature_value_id
            response.feature_value.feature_value_id = echoed_0
            echoed_1 = request.feature_value.subject
            response.feature_value.subject.CopyFrom(echoed_1)
            return response

    async def handle_comment_feature_value_approval(
        self,
        request: featurestore_v1_feature_value_approval_service_pb2.CommentFeatureValueApprovalRequest
    ) -> featurestore_v1_feature_value_approval_service_pb2.CommentFeatureValueApprovalResponse:
        """Comments a feature value."""
        deps = self.deps
        response = featurestore_v1_feature_value_approval_service_pb2.CommentFeatureValueApprovalResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CommentFeatureValueApproval', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'CommentFeatureValueApproval',
                {'reason': request.reason}
            )
            await deps.repository.save_feature_value(request.context.tenant_id, request.feature_value)
            response_0 = featurestore_v1_feature_value_import_service_pb2.ValidateFeatureValueImportResponse()
            response_1 = metrics_v1_metric_series_validation_service_pb2.LintMetricSeriesesResponse()
            response_2 = featurestore_v1_feature_value_import_service_pb2.RetryFeatureValueImportResponse()
            outgoing_0 = featurestore_v1_feature_value_import_service_pb2.ValidateFeatureValueImportRequest(
                context=request.context,
                details=featurestore_v1_feature_value_import_service_pb2.ValidateFeatureValueImportRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(email=request.details.approver.email)
                ),
                feature_value=featurestore_v1_featurestore_pb2.FeatureValue(
                    subject=datasets_v1_refs_pb2.DatasetRef(
                        code=request.feature_value.subject.code,
                        dataset_id=request.feature_value.subject.dataset_id,
                        display_name=request.feature_value.subject.display_name
                    )
                )
            )
            outgoing_1 = metrics_v1_metric_series_validation_service_pb2.LintMetricSeriesesRequest(
                context=request.context,
                details=metrics_v1_metric_series_validation_service_pb2.LintMetricSeriesesRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(email=request.details.approver_email)
                ),
                metric_series=metrics_v1_metrics_pb2.MetricSeries(
                    owner=identity_v1_refs_pb2.UserRef(
                        display_name=request.details.approver.display_name,
                        email=request.details.approver.email
                    )
                )
            )
            response_0, response_1 = await asyncio.gather(
                deps.clients.featurestore_feature_value_import.ValidateFeatureValueImport(
                    outgoing_0,
                    timeout=deps.settings.timeout
                ),
                deps.clients.metrics_metric_series_validation.LintMetricSerieses(
                    outgoing_1,
                    timeout=deps.settings.timeout
                ),
            )
            command_2 = FeatureValueApprovalCommentFeatureValueApproval2Command(
                context=request.context,
                feature_value_subject_dataset_id=request.feature_value.subject.dataset_id,
                feature_value_subject_display_name=request.feature_value.subject.display_name,
                feature_value_subject_code=response_0.feature_value.subject.code
            )
            outgoing_2 = to_feature_value_approval_comment_feature_value_approval2_command(command_2)
            response_2 = await deps.clients.featurestore_feature_value_import.RetryFeatureValueImport(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.outcome.status
            if returned_0_0:
                response.outcome.status = returned_0_0
            returned_0_1 = response_0.feature_value.kind
            if returned_0_1:
                response.feature_value.kind = returned_0_1
            returned_1_0 = response_1.result.correlation_id
            if returned_1_0:
                response.result.correlation_id = returned_1_0
            returned_2_0 = response_2.outcome.next_steps
            response.outcome.next_steps.extend(returned_2_0)
            returned_2_1 = response_2.result.reference_ids
            response.result.reference_ids.extend(returned_2_1)
            echoed_0 = request.feature_value_id
            response.feature_value.feature_value_id = echoed_0
            echoed_1 = request.feature_value.sequence
            response.feature_value.sequence = echoed_1
            return response

    async def handle_delegate_feature_value_approval(
        self,
        request: featurestore_v1_feature_value_approval_service_pb2.DelegateFeatureValueApprovalRequest
    ) -> featurestore_v1_feature_value_approval_service_pb2.DelegateFeatureValueApprovalResponse:
        """Delegates a feature value."""
        deps = self.deps
        response = featurestore_v1_feature_value_approval_service_pb2.DelegateFeatureValueApprovalResponse()
        with tenant_scope(request.context.tenant_id):
            log.info(
                'DelegateFeatureValueApproval',
                extra={'fields': {'approver_email': request.details.approver_email}}
            )
            await deps.repository.audit(
                request.context.tenant_id,
                'DelegateFeatureValueApproval',
                {'approver_email': request.details.approver_email}
            )
            await deps.repository.save_feature_value(request.context.tenant_id, request.feature_value)
            response_0 = featurestore_v1_feature_view_sync_service_pb2.SyncFeatureViewsResponse()
            response_1 = authorization_v1_access_policy_query_service_pb2.SummarizeAccessPoliciesResponse()
            command_0 = FeatureValueApprovalDelegateFeatureValueApproval0Command.model_validate(
                {'context': request.context, 'feature_view_owner_email': request.details.approver.email}
            )
            outgoing_0 = to_feature_value_approval_delegate_feature_value_approval0_command(command_0)
            response_0 = await deps.clients.featurestore_feature_view_sync.SyncFeatureViews(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = authorization_v1_access_policy_query_service_pb2.SummarizeAccessPoliciesRequest(
                context=request.context,
                reason=request.reason
            )
            send_1 = partial(
                deps.clients.authorization_access_policy_query.SummarizeAccessPolicies,
                timeout=deps.settings.timeout
            )
            response_1 = await send_1(outgoing_1)
            returned_0_0 = response_0.outcome.reference_id
            if returned_0_0:
                response.outcome.reference_id = returned_0_0
            returned_0_1 = response_0.result.status
            if returned_0_1:
                response.outcome.status = returned_0_1
            returned_1_0 = response_1.result.message
            if returned_1_0:
                response.outcome.message = returned_1_0
            returned_1_1 = response_1.result.reference_ids
            response.result.reference_ids.extend(returned_1_1)
            echoed_0 = request.feature_value_id
            response.feature_value.feature_value_id = echoed_0
            echoed_1 = request.feature_value.subject
            response.feature_value.subject.CopyFrom(echoed_1)
            return response

    async def handle_escalate_feature_value(
        self,
        request: featurestore_v1_feature_value_approval_service_pb2.EscalateFeatureValueRequest
    ) -> featurestore_v1_feature_value_approval_service_pb2.EscalateFeatureValueResponse:
        """Escalates a feature value."""
        deps = self.deps
        response = featurestore_v1_feature_value_approval_service_pb2.EscalateFeatureValueResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('EscalateFeatureValue', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'EscalateFeatureValue', {'reason': request.reason})
            await deps.repository.save_feature_value(request.context.tenant_id, request.feature_value)
            response_0 = featurestore_v1_feature_view_sync_service_pb2.ReconcileFeatureViewsResponse()
            response_1 = featurestore_v1_feature_view_approval_service_pb2.RecallFeatureViewResponse()
            response_2 = authorization_v1_access_policy_validation_service_pb2.ExplainAccessPolicyDecisionResponse()
            response_3 = featurestore_v1_feature_value_reporting_service_pb2.GenerateFeatureValueReportResponse()
            outgoing_0 = featurestore_v1_feature_view_sync_service_pb2.ReconcileFeatureViewsRequest(
                context=request.context,
                feature_view=featurestore_v1_featurestore_pb2.FeatureView(
                    code=request.feature_value.subject.code,
                    owner=identity_v1_refs_pb2.UserRef(
                        display_name=request.details.approver.display_name,
                        email=request.details.approver.email,
                        user_id=request.details.approver.user_id
                    )
                )
            )
            response_0 = await hooks.feature_value_approval_escalate_feature_value0(
                deps.clients.featurestore_feature_view_sync,
                outgoing_0,
                deps.settings.timeout
            )
            outgoing_1 = featurestore_v1_feature_view_approval_service_pb2.RecallFeatureViewRequest()
            outgoing_1.context.CopyFrom(request.context)
            outgoing_1.details.approver.user_id = request.details.approver.user_id
            if response_0.feature_view.WhichOneof('locator') == 'address':
                outgoing_1.feature_view.address.postal_code = response_0.feature_view.address.postal_code
            response_1 = await deps.clients.featurestore_feature_view_approval.RecallFeatureView(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = authorization_v1_access_policy_validation_service_pb2.ExplainAccessPolicyDecisionRequest(
                access_policy=authorization_v1_authorization_pb2.AccessPolicy(
                    audit=common_v1_audit_pb2.AuditInfo(created_at=response_1.feature_view.audit.created_at),
                    description=response_1.feature_view.components.get(
                        'primary',
                        featurestore_v1_featurestore_pb2.FeatureViewComponent()
                    ).description,
                    owner=identity_v1_refs_pb2.UserRef(user_id=response_1.feature_view.owner.user_id)
                ),
                context=request.context
            )
            port_2: FeatureValueApprovalEscalateFeatureValue2Port = FeatureValueApprovalEscalateFeatureValue2Adapter(
                deps.clients.authorization_access_policy_validation,
                deps.settings.timeout
            )
            response_2 = await port_2.execute(outgoing_2)
            outgoing_3 = featurestore_v1_feature_value_reporting_service_pb2.GenerateFeatureValueReportRequest(
                annotations=dict(request.annotations),
                context=request.context,
                reason=response_2.access_policy.block.reason
            )
            steps_3 = [
                partial(
                    deps.clients.featurestore_feature_value_reporting.GenerateFeatureValueReport,
                    outgoing_3,
                    timeout=deps.settings.timeout
                )
            ]
            results_3 = await run_steps(steps_3)
            response_3 = results_3[-1]
            returned_0_0 = response_0.outcome.message
            if returned_0_0:
                response.outcome.message = returned_0_0
            returned_0_1 = response_0.result.correlation_id
            if returned_0_1:
                response.result.correlation_id = returned_0_1
            returned_1_0 = response_1.outcome.status
            if returned_1_0:
                response.result.status = returned_1_0
            returned_1_1 = response_1.result.message
            if returned_1_1:
                response.result.message = returned_1_1
            returned_2_0 = response_2.outcome.effective_at
            if returned_2_0.ListFields():
                response.outcome.effective_at.MergeFrom(returned_2_0)
            returned_3_0 = response_3.result.status
            if returned_3_0:
                response.outcome.status = returned_3_0
            returned_3_1 = response_3.result.details
            response.result.details.update(returned_3_1)
            echoed_0 = request.feature_value_id
            response.feature_value.feature_value_id = echoed_0
            echoed_1 = request.feature_value.sequence
            response.feature_value.sequence = echoed_1
            return response

    async def handle_get_feature_value_approval_status(
        self,
        request: featurestore_v1_feature_value_approval_service_pb2.GetFeatureValueApprovalStatusRequest
    ) -> featurestore_v1_feature_value_approval_service_pb2.GetFeatureValueApprovalStatusResponse:
        """Returns a feature value."""
        deps = self.deps
        response = featurestore_v1_feature_value_approval_service_pb2.GetFeatureValueApprovalStatusResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('GetFeatureValueApprovalStatus', extra={'fields': {'domain': 'featurestore'}})
            await deps.repository.audit(request.context.tenant_id, 'GetFeatureValueApprovalStatus', {})
            response_0 = featurestore_v1_feature_view_approval_service_pb2.RecallFeatureViewResponse()
            response_1 = anomalies_v1_detector_workflow_service_pb2.ListDetectorWorkflowsResponse()
            outgoing_0 = featurestore_v1_feature_view_approval_service_pb2.RecallFeatureViewRequest(
                context=request.context,
                details=featurestore_v1_feature_view_approval_service_pb2.RecallFeatureViewRequest.Details(
                    approver=identity_v1_refs_pb2.UserRef(email=request.context.actor.email)
                ),
                feature_view=featurestore_v1_featurestore_pb2.FeatureView(
                    owner=identity_v1_refs_pb2.UserRef(user_id=request.context.actor.user_id)
                )
            )
            response_0 = await deps.clients.featurestore_feature_view_approval.RecallFeatureView(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = anomalies_v1_detector_workflow_service_pb2.ListDetectorWorkflowsRequest(
                context=request.context,
                filter=anomalies_v1_detector_workflow_service_pb2.ListDetectorWorkflowsRequest.Filter(
                    created_after=response_0.feature_view.audit.updated_at,
                    labels=dict(response_0.feature_view.specs),
                    owner_id=response_0.result.correlation_id,
                    region=response_0.feature_view.address.region
                )
            )
            response_1 = cast(anomalies_v1_detector_workflow_service_pb2.ListDetectorWorkflowsResponse, await deps.bus.request(
                'acme.featurestore.v1.FeatureValueApprovalService/GetFeatureValueApprovalStatus/1', outgoing_1, deps.settings.timeout,
            ))
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.result.message = returned_0_0
            returned_1_0 = response_1.result.message
            if returned_1_0:
                response.result.message = returned_1_0
            returned_1_1 = response_1.result.reference_ids
            response.result.reference_ids.extend(returned_1_1)
            echoed_0 = request.feature_value_id
            response.feature_value.feature_value_id = echoed_0
            return response

    async def handle_list_pending_feature_values(
        self,
        request: featurestore_v1_feature_value_approval_service_pb2.ListPendingFeatureValuesRequest
    ) -> featurestore_v1_feature_value_approval_service_pb2.ListPendingFeatureValuesResponse:
        """Lists feature values a page at a time."""
        deps = self.deps
        response = featurestore_v1_feature_value_approval_service_pb2.ListPendingFeatureValuesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ListPendingFeatureValues', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ListPendingFeatureValues',
                {'order_by': request.order_by}
            )
            response_0 = lineage_v1_lineage_edge_sync_service_pb2.ResolveLineageEdgeConflictResponse()
            response_1 = featurestore_v1_feature_value_reporting_service_pb2.ShareFeatureValueReportResponse()
            outgoing_0 = lineage_v1_lineage_edge_sync_service_pb2.ResolveLineageEdgeConflictRequest(
                context=request.context,
                lineage_edge=lineage_v1_lineage_pb2.LineageEdge(
                    attributes=dict(request.filter.labels),
                    measurements=[
                        lineage_v1_lineage_pb2.LineageEdgeMeasurement(observed_at=request.filter.created_after)
                    ]
                )
            )
            response_0 = await deps.clients.lineage_lineage_edge_sync.ResolveLineageEdgeConflict(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = featurestore_v1_feature_value_reporting_service_pb2.ShareFeatureValueReportRequest(
                context=request.context,
                details=featurestore_v1_feature_value_reporting_service_pb2.ShareFeatureValueReportRequest.Details(
                    recipient=common_v1_contact_pb2.ContactInfo(email=request.context.actor.email)
                )
            )
            method_name_1 = 'ShareFeatureValueReport'
            response_1 = await getattr(
                deps.clients.featurestore_feature_value_reporting,
                method_name_1
            )(outgoing_1, timeout=deps.settings.timeout)
            returned_0_0 = response_0.lineage_edge.occurred_at
            returned_0_0_part_0 = response.feature_values.add()
            if returned_0_0.ListFields():
                returned_0_0_part_0.occurred_at.MergeFrom(returned_0_0)
            returned_0_1 = response_0.result.correlation_id
            returned_0_1_part_0 = response.feature_values.add()
            if returned_0_1:
                returned_0_1_part_0.correlation_id = returned_0_1
            returned_1_0 = response_1.feature_value.feature_value_id
            returned_1_0_part_0 = response.feature_values.add()
            if returned_1_0:
                returned_1_0_part_0.feature_value_id = returned_1_0
            returned_1_1 = response_1.feature_value.subject
            returned_1_1_part_0 = response.feature_values.add()
            if returned_1_1.ListFields():
                returned_1_1_part_0.subject.MergeFrom(returned_1_1)
            return response

    async def handle_recall_feature_value(
        self,
        request: featurestore_v1_feature_value_approval_service_pb2.RecallFeatureValueRequest
    ) -> featurestore_v1_feature_value_approval_service_pb2.RecallFeatureValueResponse:
        """Recalls a feature value."""
        deps = self.deps
        response = featurestore_v1_feature_value_approval_service_pb2.RecallFeatureValueResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('RecallFeatureValue', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'RecallFeatureValue', {'reason': request.reason})
            await deps.repository.save_feature_value(request.context.tenant_id, request.feature_value)
            response_0 = lineage_v1_impact_import_service_pb2.MapImpactImportColumnsResponse()
            response_1 = lineage_v1_impact_lifecycle_service_pb2.ScheduleImpactExpiryResponse()
            fields_0: dict[str, Any] = {
                'context': request.context,
                'impact': {
                    'assignee': {'email': request.details.approver.email, 'user_id': request.details.approver.user_id},
                    'comments': [{'author_email': request.details.approver_email}],
                    'customer': {'display_name': request.feature_value.subject.display_name}
                }
            }
            outgoing_0 = lineage_v1_impact_import_service_pb2.MapImpactImportColumnsRequest(**fields_0)
            response_0 = await deps.clients.lineage_impact_import.MapImpactImportColumns(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = lineage_v1_impact_lifecycle_service_pb2.ScheduleImpactExpiryRequest(
                context=request.context,
                details=lineage_v1_impact_lifecycle_service_pb2.ScheduleImpactExpiryRequest.Details(
                    notify=common_v1_contact_pb2.ContactInfo(phone=response_0.impact.requester.phone)
                ),
                impact=lineage_v1_lineage_pb2.Impact(
                    assignee=identity_v1_refs_pb2.UserRef(user_id=response_0.impact.assignee.user_id),
                    customer=customers_v1_refs_pb2.CustomerRef(email=response_0.impact.assignee.email)
                )
            )
            document_1 = MessageToDict(outgoing_1, preserving_proto_field_name=True)
            outgoing_1 = ParseDict(document_1, lineage_v1_impact_lifecycle_service_pb2.ScheduleImpactExpiryRequest())
            response_1 = await deps.clients.lineage_impact_lifecycle.ScheduleImpactExpiry(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.details
            response.result.details.update(returned_0_0)
            returned_1_0 = response_1.impact.customer.display_name
            if returned_1_0:
                response.feature_value.subject.display_name = returned_1_0
            returned_1_1 = response_1.outcome.message
            if returned_1_1:
                response.outcome.message = returned_1_1
            echoed_0 = request.feature_value_id
            response.feature_value.feature_value_id = echoed_0
            echoed_1 = request.feature_value.correlation_id
            response.feature_value.correlation_id = echoed_1
            return response

    async def handle_reject_feature_value(
        self,
        request: featurestore_v1_feature_value_approval_service_pb2.RejectFeatureValueRequest
    ) -> featurestore_v1_feature_value_approval_service_pb2.RejectFeatureValueResponse:
        """Rejects a feature value."""
        deps = self.deps
        response = featurestore_v1_feature_value_approval_service_pb2.RejectFeatureValueResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('RejectFeatureValue', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'RejectFeatureValue', {'reason': request.reason})
            await deps.repository.save_feature_value(request.context.tenant_id, request.feature_value)
            response_0 = datasets_v1_data_schema_validation_service_pb2.ExplainDataSchemaDecisionResponse()
            response_1 = lineage_v1_impact_workflow_service_pb2.AdvanceImpactWorkflowResponse()
            outgoing_0 = datasets_v1_data_schema_validation_service_pb2.ExplainDataSchemaDecisionRequest(
                context=request.context,
                data_schema=datasets_v1_datasets_pb2.DataSchema(
                    children=[
                        datasets_v1_datasets_pb2.DataSchema(
                            children=[
                                datasets_v1_datasets_pb2.DataSchema(
                                    attributes=dict(request.feature_value.attributes),
                                    manager=identity_v1_refs_pb2.UserRef(email=request.details.approver.email)
                                )
                            ],
                            manager=identity_v1_refs_pb2.UserRef(
                                display_name=request.feature_value.subject.display_name
                            )
                        )
                    ]
                )
            )
            document_0 = MessageToJson(outgoing_0, preserving_proto_field_name=True)
            outgoing_0 = Parse(
                document_0,
                datasets_v1_data_schema_validation_service_pb2.ExplainDataSchemaDecisionRequest()
            )
            response_0 = await deps.clients.datasets_data_schema_validation.ExplainDataSchemaDecision(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = lineage_v1_impact_workflow_service_pb2.AdvanceImpactWorkflowRequest()
            outgoing_1.context.CopyFrom(request.context)
            outgoing_1.impact.audit.created_by = response_0.data_schema.audit.created_by
            outgoing_1.impact.assignee.email = response_0.data_schema.manager.email
            outgoing_1.impact.assignee.user_id = request.details.approver.user_id
            merged_1 = lineage_v1_impact_workflow_service_pb2.AdvanceImpactWorkflowRequest()
            merged_1.MergeFrom(outgoing_1)
            outgoing_1.CopyFrom(merged_1)
            response_1 = await deps.clients.lineage_impact_workflow.AdvanceImpactWorkflow(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.outcome.message = returned_0_0
            returned_1_0 = response_1.result.reference_ids
            response.result.reference_ids.extend(returned_1_0)
            returned_1_1 = response_1.result.status
            if returned_1_1:
                response.outcome.status = returned_1_1
            echoed_0 = request.feature_value_id
            response.feature_value.feature_value_id = echoed_0
            echoed_1 = request.feature_value.source
            response.feature_value.source = echoed_1
            return response

    async def handle_submit_feature_value(
        self,
        request: featurestore_v1_feature_value_approval_service_pb2.SubmitFeatureValueRequest
    ) -> featurestore_v1_feature_value_approval_service_pb2.SubmitFeatureValueResponse:
        """Submits a feature value."""
        deps = self.deps
        response = featurestore_v1_feature_value_approval_service_pb2.SubmitFeatureValueResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SubmitFeatureValue', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'SubmitFeatureValue', {'reason': request.reason})
            await deps.repository.save_feature_value(request.context.tenant_id, request.feature_value)
            response_0 = lineage_v1_lineage_edge_approval_service_pb2.ListPendingLineageEdgesResponse()
            response_1 = metrics_v1_metric_series_history_service_pb2.RecordMetricSeriesVersionResponse()
            response_2 = featurestore_v1_feature_value_lifecycle_service_pb2.ScheduleFeatureValueExpiryResponse()
            callbacks_0: list[
                Callable[[], Awaitable[lineage_v1_lineage_edge_approval_service_pb2.ListPendingLineageEdgesResponse]]
            ] = []
            for item_0 in request.feature_value.measurements:
                outgoing_0 = lineage_v1_lineage_edge_approval_service_pb2.ListPendingLineageEdgesRequest(
                    context=request.context,
                    filter=lineage_v1_lineage_edge_approval_service_pb2.ListPendingLineageEdgesRequest.Filter(
                        created_after=item_0.observed_at,
                        owner_id=request.feature_value.subject.dataset_id
                    )
                )
                async def send_0(
                    payload: lineage_v1_lineage_edge_approval_service_pb2.ListPendingLineageEdgesRequest = outgoing_0
                ) -> lineage_v1_lineage_edge_approval_service_pb2.ListPendingLineageEdgesResponse:
                    return await deps.clients.lineage_lineage_edge_approval.ListPendingLineageEdges(
                        payload,
                        timeout=deps.settings.timeout
                    )
                callbacks_0.append(send_0)
            for callback_0 in callbacks_0:
                response_0 = await callback_0()
            outgoing_1 = metrics_v1_metric_series_history_service_pb2.RecordMetricSeriesVersionRequest(
                context=request.context,
                metric_series=metrics_v1_metrics_pb2.MetricSeries(
                    owner=identity_v1_refs_pb2.UserRef(user_id=request.details.approver.user_id)
                )
            )
            registered_1 = cast(
                metrics_v1_metric_series_history_service_pb2_grpc.MetricSeriesHistoryServiceStub,
                deps.clients.registry['acme.metrics.v1.MetricSeriesHistoryService']
            )
            response_1 = await registered_1.RecordMetricSeriesVersion(outgoing_1, timeout=deps.settings.timeout)
            command_2 = FeatureValueApprovalSubmitFeatureValue2Command(
                context=request.context,
                feature_value_subject_display_name=request.feature_value.subject.display_name
            )
            outgoing_2 = to_feature_value_approval_submit_feature_value2_command(command_2)
            response_2 = await deps.clients.featurestore_feature_value_lifecycle.ScheduleFeatureValueExpiry(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            returned_1_0 = response_1.outcome.message
            if returned_1_0:
                response.result.message = returned_1_0
            returned_2_0 = response_2.outcome.effective_at
            if returned_2_0.ListFields():
                response.outcome.effective_at.MergeFrom(returned_2_0)
            returned_2_1 = response_2.feature_value.kind
            if returned_2_1:
                response.feature_value.kind = returned_2_1
            echoed_0 = request.feature_value_id
            response.feature_value.feature_value_id = echoed_0
            echoed_1 = request.feature_value.attributes
            response.feature_value.attributes.update(echoed_1)
            return response
