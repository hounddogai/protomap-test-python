"""Routes pipeline steps through approval, with escalation and delegation."""

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

from acme.admissions.v1 import admission_query_service_pb2 as admissions_v1_admission_query_service_pb2
from acme.authorization.v1 import access_policy_service_pb2 as authorization_v1_access_policy_service_pb2
from acme.authorization.v1 import (
    access_policy_validation_service_pb2 as authorization_v1_access_policy_validation_service_pb2,
)
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.featurestore.v1 import entity_sync_service_pb2 as featurestore_v1_entity_sync_service_pb2
from acme.featurestore.v1 import feature_value_import_service_pb2 as featurestore_v1_feature_value_import_service_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.ledger.v1 import ledger_account_service_pb2 as ledger_v1_ledger_account_service_pb2
from acme.ledger.v1 import ledger_account_service_pb2_grpc as ledger_v1_ledger_account_service_pb2_grpc
from acme.metrics.v1 import metric_alert_history_service_pb2 as metrics_v1_metric_alert_history_service_pb2
from acme.metrics.v1 import metrics_pb2 as metrics_v1_metrics_pb2
from acme.modelregistry.v1 import (
    model_version_reporting_service_pb2 as modelregistry_v1_model_version_reporting_service_pb2,
)
from acme.pipelines.v1 import pipeline_calculation_service_pb2 as pipelines_v1_pipeline_calculation_service_pb2
from acme.pipelines.v1 import pipeline_run_import_service_pb2 as pipelines_v1_pipeline_run_import_service_pb2
from acme.pipelines.v1 import pipeline_run_sync_service_pb2 as pipelines_v1_pipeline_run_sync_service_pb2
from acme.pipelines.v1 import pipeline_step_approval_service_pb2 as pipelines_v1_pipeline_step_approval_service_pb2
from acme.pipelines.v1 import (
    pipeline_step_approval_service_pb2_grpc as pipelines_v1_pipeline_step_approval_service_pb2_grpc,
)
from acme.pipelines.v1 import (
    pipeline_step_calculation_service_pb2 as pipelines_v1_pipeline_step_calculation_service_pb2,
)
from acme.pipelines.v1 import pipeline_step_lifecycle_service_pb2 as pipelines_v1_pipeline_step_lifecycle_service_pb2
from acme.pipelines.v1 import pipelines_pb2 as pipelines_v1_pipelines_pb2
from acme.pricing.v1 import price_list_service_pb2 as pricing_v1_price_list_service_pb2
from acme.venues.v1 import venue_service_pb2 as venues_v1_venue_service_pb2

from acme_data.domains.pipelines import hooks
from acme_data.domains.pipelines.dependencies import Dependencies
from acme_data.domains.pipelines.models import PipelineStepApprovalEscalatePipelineStep2Command
from acme_data.domains.pipelines.models import PipelineStepApprovalEscalatePipelineStep3Command
from acme_data.domains.pipelines.models import to_pipeline_step_approval_escalate_pipeline_step2_command
from acme_data.domains.pipelines.models import to_pipeline_step_approval_escalate_pipeline_step3_command
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_id
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class PipelineStepApprovalServicer(
    pipelines_v1_pipeline_step_approval_service_pb2_grpc.PipelineStepApprovalServiceServicer
):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    async def ApprovePipelineStep(
        self, request: pipelines_v1_pipeline_step_approval_service_pb2.ApprovePipelineStepRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_step_approval_service_pb2.ApprovePipelineStepResponse:
        """Approves a pipeline step."""
        return await self.handle_approve_pipeline_step(request)

    @rpc_errors
    async def CommentPipelineStepApproval(
        self, request: pipelines_v1_pipeline_step_approval_service_pb2.CommentPipelineStepApprovalRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_step_approval_service_pb2.CommentPipelineStepApprovalResponse:
        """Comments a pipeline step."""
        return await self.handle_comment_pipeline_step_approval(request)

    @rpc_errors
    async def DelegatePipelineStepApproval(
        self, request: pipelines_v1_pipeline_step_approval_service_pb2.DelegatePipelineStepApprovalRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_step_approval_service_pb2.DelegatePipelineStepApprovalResponse:
        """Delegates a pipeline step."""
        return await self.handle_delegate_pipeline_step_approval(request)

    @rpc_errors
    async def EscalatePipelineStep(
        self, request: pipelines_v1_pipeline_step_approval_service_pb2.EscalatePipelineStepRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_step_approval_service_pb2.EscalatePipelineStepResponse:
        """Escalates a pipeline step."""
        return await self.handle_escalate_pipeline_step(request)

    @rpc_errors
    async def RejectPipelineStep(
        self, request: pipelines_v1_pipeline_step_approval_service_pb2.RejectPipelineStepRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_step_approval_service_pb2.RejectPipelineStepResponse:
        """Rejects a pipeline step."""
        return await self.handle_reject_pipeline_step(request)

    @rpc_errors
    async def SubmitPipelineStep(
        self, request: pipelines_v1_pipeline_step_approval_service_pb2.SubmitPipelineStepRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_step_approval_service_pb2.SubmitPipelineStepResponse:
        """Submits a pipeline step."""
        return await self.handle_submit_pipeline_step(request)

    async def handle_approve_pipeline_step(
        self,
        request: pipelines_v1_pipeline_step_approval_service_pb2.ApprovePipelineStepRequest
    ) -> pipelines_v1_pipeline_step_approval_service_pb2.ApprovePipelineStepResponse:
        """Approves a pipeline step."""
        deps = self.deps
        response = pipelines_v1_pipeline_step_approval_service_pb2.ApprovePipelineStepResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ApprovePipelineStep', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'ApprovePipelineStep', {'reason': request.reason})
            await deps.repository.save_pipeline_step(request.context.tenant_id, request.pipeline_step)
            response_0 = metrics_v1_metric_alert_history_service_pb2.AnnotateMetricAlertVersionResponse()
            response_1 = pipelines_v1_pipeline_step_calculation_service_pb2.ComparePipelineStepOptionsResponse()
            response_2 = admissions_v1_admission_query_service_pb2.CountAdmissionsResponse()
            requests_0: list[metrics_v1_metric_alert_history_service_pb2.AnnotateMetricAlertVersionRequest] = []
            for item_0 in request.pipeline_step.conditions:
                outgoing_0 = metrics_v1_metric_alert_history_service_pb2.AnnotateMetricAlertVersionRequest(
                    context=request.context,
                    metric_alert=metrics_v1_metrics_pb2.MetricAlert(
                        conditions=[
                            metrics_v1_metrics_pb2.MetricAlertCondition(
                                attribute=item_0.attribute,
                                negate=item_0.negate,
                                operator=item_0.operator,
                                value=item_0.value
                            )
                        ]
                    )
                )
                requests_0.append(outgoing_0)
            replies_0 = await asyncio.gather(*(
                deps.clients.metrics_metric_alert_history.AnnotateMetricAlertVersion(
                    entry,
                    timeout=deps.settings.timeout
                ) for entry in requests_0
            ))
            if replies_0:
                response_0 = replies_0[-1]
            callbacks_1: list[
                Callable[
                    [],
                    Awaitable[pipelines_v1_pipeline_step_calculation_service_pb2.ComparePipelineStepOptionsResponse]
                ]
            ] = []
            for item_1 in request.pipeline_step.conditions:
                outgoing_1 = pipelines_v1_pipeline_step_calculation_service_pb2.ComparePipelineStepOptionsRequest(
                    context=request.context,
                    pipeline_step=pipelines_v1_pipelines_pb2.PipelineStep(
                        conditions=[
                            pipelines_v1_pipelines_pb2.PipelineStepCondition(
                                operator=item_1.operator,
                                value=item_1.value
                            )
                        ]
                    )
                )
                async def send_1(
                    payload: pipelines_v1_pipeline_step_calculation_service_pb2.ComparePipelineStepOptionsRequest = outgoing_1
                ) -> pipelines_v1_pipeline_step_calculation_service_pb2.ComparePipelineStepOptionsResponse:
                    return await deps.clients.pipelines_pipeline_step_calculation.ComparePipelineStepOptions(
                        payload,
                        timeout=deps.settings.timeout
                    )
                callbacks_1.append(send_1)
            for callback_1 in callbacks_1:
                response_1 = await callback_1()
            outgoing_2 = admissions_v1_admission_query_service_pb2.CountAdmissionsRequest(
                context=request.context,
                filter=admissions_v1_admission_query_service_pb2.CountAdmissionsRequest.Filter(
                    created_after=request.pipeline_step.audit.updated_at,
                    labels=dict(response_0.result.details),
                    owner_id=response_0.metric_alert.owner.user_id
                )
            )
            response_2 = await deps.clients.admissions_admission_query.CountAdmissions(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            returned_2_0 = response_2.result.message
            if returned_2_0:
                response.outcome.message = returned_2_0
            returned_2_1 = response_2.result.correlation_id
            if returned_2_1:
                response.result.correlation_id = returned_2_1
            echoed_0 = request.pipeline_step_id
            response.pipeline_step.pipeline_step_id = echoed_0
            echoed_1 = request.pipeline_step.priority
            response.pipeline_step.priority = echoed_1
            return response

    async def handle_comment_pipeline_step_approval(
        self,
        request: pipelines_v1_pipeline_step_approval_service_pb2.CommentPipelineStepApprovalRequest
    ) -> pipelines_v1_pipeline_step_approval_service_pb2.CommentPipelineStepApprovalResponse:
        """Comments a pipeline step."""
        deps = self.deps
        response = pipelines_v1_pipeline_step_approval_service_pb2.CommentPipelineStepApprovalResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CommentPipelineStepApproval', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'CommentPipelineStepApproval',
                {'reason': request.reason}
            )
            await deps.repository.save_pipeline_step(request.context.tenant_id, request.pipeline_step)
            response_0 = authorization_v1_access_policy_service_pb2.CreateAccessPolicyResponse()
            response_1 = pricing_v1_price_list_service_pb2.ListPriceListsResponse()
            outgoing_0 = authorization_v1_access_policy_service_pb2.CreateAccessPolicyRequest()
            outgoing_0.context.CopyFrom(request.context)
            outgoing_0.access_policy.owner.display_name = request.pipeline_step.owner.display_name
            outgoing_0.access_policy.audit.created_at.CopyFrom(request.pipeline_step.audit.created_at)
            if request.pipeline_step.WhichOneof('action') == 'block':
                outgoing_0.access_policy.block.notify_email = request.pipeline_step.block.notify_email
            outgoing_0.access_policy.owner.user_id = request.details.approver.user_id
            response_0 = await deps.clients.authorization_access_policy.CreateAccessPolicy(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            fields_1: dict[str, Any] = {
                'context': request.context,
                'filter': {
                    'created_after': response_0.access_policy.audit.created_at,
                    'labels': dict(response_0.result.details),
                    'owner_id': response_0.access_policy.access_policy_id
                }
            }
            outgoing_1 = pricing_v1_price_list_service_pb2.ListPriceListsRequest(**fields_1)
            response_1 = await deps.clients.pricing_price_list.ListPriceLists(outgoing_1, timeout=deps.settings.timeout)
            returned_0_0 = response_0.access_policy.audit.updated_at
            if returned_0_0.ListFields():
                response.pipeline_step.audit.updated_at.MergeFrom(returned_0_0)
            returned_0_1 = response_0.result.correlation_id
            if returned_0_1:
                response.result.correlation_id = returned_0_1
            returned_1_0 = response_1.result.message
            if returned_1_0:
                response.outcome.message = returned_1_0
            echoed_0 = request.pipeline_step_id
            response.pipeline_step.pipeline_step_id = echoed_0
            echoed_1 = request.pipeline_step.status
            response.pipeline_step.status = echoed_1
            return response

    async def handle_delegate_pipeline_step_approval(
        self,
        request: pipelines_v1_pipeline_step_approval_service_pb2.DelegatePipelineStepApprovalRequest
    ) -> pipelines_v1_pipeline_step_approval_service_pb2.DelegatePipelineStepApprovalResponse:
        """Delegates a pipeline step."""
        deps = self.deps
        response = pipelines_v1_pipeline_step_approval_service_pb2.DelegatePipelineStepApprovalResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('DelegatePipelineStepApproval', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'DelegatePipelineStepApproval',
                {'reason': request.reason}
            )
            await deps.repository.save_pipeline_step(request.context.tenant_id, request.pipeline_step)
            response_0 = pipelines_v1_pipeline_run_import_service_pb2.ListPipelineRunImportsResponse()
            response_1 = authorization_v1_access_policy_validation_service_pb2.PreviewAccessPolicyResponse()
            response_2 = pipelines_v1_pipeline_step_lifecycle_service_pb2.SchedulePipelineStepExpiryResponse()
            outgoing_0 = pipelines_v1_pipeline_run_import_service_pb2.ListPipelineRunImportsRequest(
                context=request.context,
                filter=pipelines_v1_pipeline_run_import_service_pb2.ListPipelineRunImportsRequest.Filter(
                    created_after=request.pipeline_step.audit.created_at,
                    owner_id=request.details.approver.user_id
                )
            )
            document_0 = MessageToDict(outgoing_0, preserving_proto_field_name=True)
            outgoing_0 = ParseDict(
                document_0,
                pipelines_v1_pipeline_run_import_service_pb2.ListPipelineRunImportsRequest()
            )
            response_0 = await deps.clients.pipelines_pipeline_run_import.ListPipelineRunImports(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = authorization_v1_access_policy_validation_service_pb2.PreviewAccessPolicyRequest()
            outgoing_1.context.CopyFrom(request.context)
            if request.pipeline_step.WhichOneof('action') == 'route':
                outgoing_1.access_policy.route.weight = request.pipeline_step.route.weight
            outgoing_1.access_policy.audit.created_at.CopyFrom(request.pipeline_step.audit.created_at)
            outgoing_1.access_policy.owner.email = request.details.approver.email
            response_1 = await deps.clients.authorization_access_policy_validation.PreviewAccessPolicy(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = pipelines_v1_pipeline_step_lifecycle_service_pb2.SchedulePipelineStepExpiryRequest()
            outgoing_2.context.CopyFrom(request.context)
            outgoing_2.pipeline_step.route.target = request.pipeline_step.route.target
            merged_2 = pipelines_v1_pipeline_step_lifecycle_service_pb2.SchedulePipelineStepExpiryRequest()
            merged_2.MergeFrom(outgoing_2)
            outgoing_2.CopyFrom(merged_2)
            response_2 = await deps.clients.pipelines_pipeline_step_lifecycle.SchedulePipelineStepExpiry(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.correlation_id
            if returned_0_0:
                response.result.correlation_id = returned_0_0
            returned_0_1 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_1)
            returned_1_0 = response_1.access_policy.audit.updated_at
            if returned_1_0.ListFields():
                response.pipeline_step.audit.updated_at.MergeFrom(returned_1_0)
            returned_1_1 = response_1.access_policy.effective
            if returned_1_1.ListFields():
                response.pipeline_step.effective.MergeFrom(returned_1_1)
            returned_2_0 = response_2.pipeline_step.parameters
            response.pipeline_step.parameters.update(returned_2_0)
            returned_2_1 = response_2.pipeline_step.description
            if returned_2_1:
                response.pipeline_step.description = returned_2_1
            echoed_0 = request.pipeline_step_id
            response.pipeline_step.pipeline_step_id = echoed_0
            echoed_1 = request.pipeline_step.owner
            response.pipeline_step.owner.CopyFrom(echoed_1)
            return response

    async def handle_escalate_pipeline_step(
        self,
        request: pipelines_v1_pipeline_step_approval_service_pb2.EscalatePipelineStepRequest
    ) -> pipelines_v1_pipeline_step_approval_service_pb2.EscalatePipelineStepResponse:
        """Escalates a pipeline step."""
        deps = self.deps
        response = pipelines_v1_pipeline_step_approval_service_pb2.EscalatePipelineStepResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('EscalatePipelineStep', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'EscalatePipelineStep', {'reason': request.reason})
            await deps.repository.save_pipeline_step(request.context.tenant_id, request.pipeline_step)
            response_0 = pipelines_v1_pipeline_run_sync_service_pb2.PushPipelineRunResponse()
            response_1 = ledger_v1_ledger_account_service_pb2.ListLedgerAccountsResponse()
            response_2 = pipelines_v1_pipeline_run_import_service_pb2.RetryPipelineRunImportResponse()
            response_3 = featurestore_v1_entity_sync_service_pb2.ListEntityConflictsResponse()
            outgoing_0 = pipelines_v1_pipeline_run_sync_service_pb2.PushPipelineRunRequest(
                context=request.context,
                pipeline_run=pipelines_v1_pipelines_pb2.PipelineRun(
                    assignee=identity_v1_refs_pb2.UserRef(user_id=request.details.approver.user_id),
                    audit=common_v1_audit_pb2.AuditInfo(etag=request.pipeline_step.audit.etag)
                )
            )
            envelope_0 = AnyMessage()
            envelope_0.Pack(outgoing_0)
            outgoing_0 = pipelines_v1_pipeline_run_sync_service_pb2.PushPipelineRunRequest()
            if not envelope_0.Unpack(outgoing_0):
                raise ValueError("partner envelope contains the wrong request type")
            response_0 = await deps.clients.pipelines_pipeline_run_sync.PushPipelineRun(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = ledger_v1_ledger_account_service_pb2.ListLedgerAccountsRequest(
                context=request.context,
                filter=ledger_v1_ledger_account_service_pb2.ListLedgerAccountsRequest.Filter(
                    created_after=response_0.pipeline_run.audit.created_at,
                    labels=dict(response_0.result.details),
                    owner_id=response_0.pipeline_run.sla.policy_id
                )
            )
            registered_1 = cast(
                ledger_v1_ledger_account_service_pb2_grpc.LedgerAccountServiceStub,
                deps.clients.registry['acme.ledger.v1.LedgerAccountService']
            )
            response_1 = await registered_1.ListLedgerAccounts(outgoing_1, timeout=deps.settings.timeout)
            command_2 = PipelineStepApprovalEscalatePipelineStep2Command(
                context=request.context,
                pipeline_run_sla_breached=response_0.pipeline_run.sla.breached
            )
            outgoing_2 = to_pipeline_step_approval_escalate_pipeline_step2_command(command_2)
            response_2 = await deps.clients.pipelines_pipeline_run_import.RetryPipelineRunImport(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            command_3 = PipelineStepApprovalEscalatePipelineStep3Command.model_validate(
                {
                    'context': request.context,
                    'filter_created_after': response_2.pipeline_run.customer.starts_at,
                    'filter_owner_id': response_0.pipeline_run.assignee.user_id,
                    'filter_labels': dict(response_0.pipeline_run.custom_fields)
                }
            )
            outgoing_3 = to_pipeline_step_approval_escalate_pipeline_step3_command(command_3)
            response_3 = await deps.clients.featurestore_entity_sync.ListEntityConflicts(
                outgoing_3,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.pipeline_run.audit.created_at
            if returned_0_0.ListFields():
                response.pipeline_step.audit.created_at.MergeFrom(returned_0_0)
            returned_1_0 = response_1.result.status
            if returned_1_0:
                response.outcome.status = returned_1_0
            returned_2_0 = response_2.result.status
            if returned_2_0:
                response.outcome.status = returned_2_0
            returned_3_0 = response_3.result.status
            if returned_3_0:
                response.outcome.status = returned_3_0
            echoed_0 = request.pipeline_step_id
            response.pipeline_step.pipeline_step_id = echoed_0
            echoed_1 = request.pipeline_step.effective
            response.pipeline_step.effective.CopyFrom(echoed_1)
            return response

    async def handle_reject_pipeline_step(
        self,
        request: pipelines_v1_pipeline_step_approval_service_pb2.RejectPipelineStepRequest
    ) -> pipelines_v1_pipeline_step_approval_service_pb2.RejectPipelineStepResponse:
        """Rejects a pipeline step."""
        deps = self.deps
        response = pipelines_v1_pipeline_step_approval_service_pb2.RejectPipelineStepResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('RejectPipelineStep', extra={'fields': {'approver_email': request.details.approver_email}})
            await deps.repository.audit(
                request.context.tenant_id,
                'RejectPipelineStep',
                {'approver_email': request.details.approver_email}
            )
            await deps.repository.save_pipeline_step(request.context.tenant_id, request.pipeline_step)
            response_0 = venues_v1_venue_service_pb2.SearchVenuesResponse()
            response_1 = modelregistry_v1_model_version_reporting_service_pb2.GenerateModelVersionReportResponse()
            outgoing_0 = venues_v1_venue_service_pb2.SearchVenuesRequest(
                context=request.context,
                filter=venues_v1_venue_service_pb2.SearchVenuesRequest.Filter(
                    created_after=request.pipeline_step.audit.updated_at,
                    labels=dict(request.pipeline_step.parameters),
                    owner_id=request.details.approver.user_id
                )
            )
            send_0 = partial(deps.clients.venues_venue.SearchVenues, timeout=deps.settings.timeout)
            response_0 = await send_0(outgoing_0)
            outgoing_1 = modelregistry_v1_model_version_reporting_service_pb2.GenerateModelVersionReportRequest(
                annotations=dict(request.annotations),
                context=request.context,
                details=modelregistry_v1_model_version_reporting_service_pb2.GenerateModelVersionReportRequest.Details(
                    filters=dict(response_0.result.details),
                    period=request.pipeline_step.effective
                ),
                reason=request.reason
            )
            response_1 = await hooks.pipeline_step_approval_reject_pipeline_step1(
                deps.clients.modelregistry_model_version_reporting,
                outgoing_1,
                deps.settings.timeout
            )
            returned_0_0 = response_0.result.status
            if returned_0_0:
                response.outcome.status = returned_0_0
            returned_1_0 = response_1.result.correlation_id
            if returned_1_0:
                response.result.correlation_id = returned_1_0
            echoed_0 = request.pipeline_step_id
            response.pipeline_step.pipeline_step_id = echoed_0
            echoed_1 = request.pipeline_step.description
            response.pipeline_step.description = echoed_1
            return response

    async def handle_submit_pipeline_step(
        self,
        request: pipelines_v1_pipeline_step_approval_service_pb2.SubmitPipelineStepRequest
    ) -> pipelines_v1_pipeline_step_approval_service_pb2.SubmitPipelineStepResponse:
        """Submits a pipeline step."""
        deps = self.deps
        response = pipelines_v1_pipeline_step_approval_service_pb2.SubmitPipelineStepResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SubmitPipelineStep', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'SubmitPipelineStep', {'reason': request.reason})
            await deps.repository.save_pipeline_step(request.context.tenant_id, request.pipeline_step)
            response_0 = pipelines_v1_pipeline_calculation_service_pb2.ComparePipelineOptionsResponse()
            response_1 = featurestore_v1_feature_value_import_service_pb2.ImportFeatureValuesResponse()
            outgoing_0 = pipelines_v1_pipeline_calculation_service_pb2.ComparePipelineOptionsRequest()
            outgoing_0.context.CopyFrom(request.context)
            outgoing_0.pipeline.audit.etag = request.pipeline_step.audit.etag
            outgoing_0.pipeline.organizer.user_id = request.pipeline_step.owner.user_id
            field_0_3_part_1 = outgoing_0.pipeline.participants.add()
            field_0_3_part_1.contact.email = request.details.approver.email
            outgoing_0.context.tenant_id = tenant_id.get()
            response_0 = await deps.clients.pipelines_pipeline_calculation.ComparePipelineOptions(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = featurestore_v1_feature_value_import_service_pb2.ImportFeatureValuesRequest(
                context=request.context,
                header=featurestore_v1_feature_value_import_service_pb2.ImportFeatureValuesRequest.StreamHeader(
                    source=response_0.pipeline.pipeline_id,
                    submitted_by=common_v1_contact_pb2.ContactInfo(email=response_0.pipeline.organizer.email)
                )
            )
            response_1 = await deps.clients.featurestore_feature_value_import.ImportFeatureValues(
                async_messages((outgoing_1,)),
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.correlation_id
            if returned_0_0:
                response.result.correlation_id = returned_0_0
            echoed_0 = request.pipeline_step_id
            response.pipeline_step.pipeline_step_id = echoed_0
            echoed_1 = request.pipeline_step.version
            response.pipeline_step.version = echoed_1
            return response
