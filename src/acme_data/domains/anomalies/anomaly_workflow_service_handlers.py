"""Reusable transport mixin for AnomalyWorkflowService."""

from __future__ import annotations

from collections.abc import AsyncIterator
from collections.abc import Awaitable
from collections.abc import Callable
from functools import partial
from typing import cast
import asyncio
import logging

from google.protobuf.json_format import MessageToDict
from google.protobuf.json_format import MessageToJson
from google.protobuf.json_format import Parse
from google.protobuf.json_format import ParseDict
import grpc

from acme.anomalies.v1 import anomalies_pb2 as anomalies_v1_anomalies_pb2
from acme.anomalies.v1 import anomaly_approval_service_pb2 as anomalies_v1_anomaly_approval_service_pb2
from acme.anomalies.v1 import (
    anomaly_feedback_calculation_service_pb2 as anomalies_v1_anomaly_feedback_calculation_service_pb2,
)
from acme.anomalies.v1 import anomaly_query_service_pb2 as anomalies_v1_anomaly_query_service_pb2
from acme.anomalies.v1 import anomaly_service_pb2 as anomalies_v1_anomaly_service_pb2
from acme.anomalies.v1 import anomaly_service_pb2_grpc as anomalies_v1_anomaly_service_pb2_grpc
from acme.anomalies.v1 import anomaly_workflow_service_pb2 as anomalies_v1_anomaly_workflow_service_pb2
from acme.anomalies.v1 import detector_validation_service_pb2 as anomalies_v1_detector_validation_service_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.datasets.v1 import dataset_query_service_pb2 as datasets_v1_dataset_query_service_pb2
from acme.datasets.v1 import dataset_service_pb2 as datasets_v1_dataset_service_pb2
from acme.datasets.v1 import dataset_validation_service_pb2 as datasets_v1_dataset_validation_service_pb2
from acme.datasets.v1 import dataset_version_query_service_pb2 as datasets_v1_dataset_version_query_service_pb2
from acme.datasets.v1 import datasets_pb2 as datasets_v1_datasets_pb2
from acme.datasets.v1 import refs_pb2 as datasets_v1_refs_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.metrics.v1 import dashboard_export_service_pb2 as metrics_v1_dashboard_export_service_pb2
from acme.surveys.v1 import refs_pb2 as surveys_v1_refs_pb2
from acme.surveys.v1 import survey_service_pb2 as surveys_v1_survey_service_pb2
from acme.surveys.v1 import survey_service_pb2_grpc as surveys_v1_survey_service_pb2_grpc
from acme.surveys.v1 import surveys_pb2 as surveys_v1_surveys_pb2

from acme_data.domains.anomalies.adapters import AnomalyWorkflowPauseAnomalyWorkflow1Adapter
from acme_data.domains.anomalies.dependencies import Dependencies
from acme_data.domains.anomalies.models import AnomalyWorkflowAdvanceAnomalyWorkflow1Command
from acme_data.domains.anomalies.models import AnomalyWorkflowCancelAnomalyWorkflow0Command
from acme_data.domains.anomalies.models import to_anomaly_workflow_advance_anomaly_workflow1_command
from acme_data.domains.anomalies.models import to_anomaly_workflow_cancel_anomaly_workflow0_command
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class AnomalyWorkflowServicerHandlers:
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    async def AdvanceAnomalyWorkflow(
        self, request: anomalies_v1_anomaly_workflow_service_pb2.AdvanceAnomalyWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> anomalies_v1_anomaly_workflow_service_pb2.AdvanceAnomalyWorkflowResponse:
        """Advances an anomaly."""
        return await self.handle_advance_anomaly_workflow(request)

    @rpc_errors
    async def CancelAnomalyWorkflow(
        self, request: anomalies_v1_anomaly_workflow_service_pb2.CancelAnomalyWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> anomalies_v1_anomaly_workflow_service_pb2.CancelAnomalyWorkflowResponse:
        """Cancels an anomaly."""
        return await self.handle_cancel_anomaly_workflow(request)

    @rpc_errors
    @retry_transient
    async def ListAnomalyWorkflows(
        self, request: anomalies_v1_anomaly_workflow_service_pb2.ListAnomalyWorkflowsRequest, context: grpc.aio.ServicerContext,
    ) -> anomalies_v1_anomaly_workflow_service_pb2.ListAnomalyWorkflowsResponse:
        """Lists anomalies a page at a time."""
        return await self.handle_list_anomaly_workflows(request)

    @rpc_errors
    async def PauseAnomalyWorkflow(
        self, request: anomalies_v1_anomaly_workflow_service_pb2.PauseAnomalyWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> anomalies_v1_anomaly_workflow_service_pb2.PauseAnomalyWorkflowResponse:
        """Pauses an anomaly."""
        return await self.handle_pause_anomaly_workflow(request)

    @rpc_errors
    async def ResumeAnomalyWorkflow(
        self, request: anomalies_v1_anomaly_workflow_service_pb2.ResumeAnomalyWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> anomalies_v1_anomaly_workflow_service_pb2.ResumeAnomalyWorkflowResponse:
        """Resumes an anomaly."""
        return await self.handle_resume_anomaly_workflow(request)

    @rpc_errors
    async def RetryAnomalyWorkflow(
        self, request: anomalies_v1_anomaly_workflow_service_pb2.RetryAnomalyWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> anomalies_v1_anomaly_workflow_service_pb2.RetryAnomalyWorkflowResponse:
        """Retrys an anomaly."""
        return await self.handle_retry_anomaly_workflow(request)

    @rpc_errors
    async def SignalAnomalyWorkflow(
        self, request: anomalies_v1_anomaly_workflow_service_pb2.SignalAnomalyWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> anomalies_v1_anomaly_workflow_service_pb2.SignalAnomalyWorkflowResponse:
        """Signals an anomaly."""
        return await self.handle_signal_anomaly_workflow(request)

    @rpc_errors
    async def StartAnomalyWorkflow(
        self, request: anomalies_v1_anomaly_workflow_service_pb2.StartAnomalyWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> anomalies_v1_anomaly_workflow_service_pb2.StartAnomalyWorkflowResponse:
        """Starts an anomaly."""
        return await self.handle_start_anomaly_workflow(request)

    async def handle_advance_anomaly_workflow(
        self,
        request: anomalies_v1_anomaly_workflow_service_pb2.AdvanceAnomalyWorkflowRequest
    ) -> anomalies_v1_anomaly_workflow_service_pb2.AdvanceAnomalyWorkflowResponse:
        """Advances an anomaly."""
        deps = self.deps
        response = anomalies_v1_anomaly_workflow_service_pb2.AdvanceAnomalyWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('AdvanceAnomalyWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'AdvanceAnomalyWorkflow', {'reason': request.reason})
            await deps.repository.save_anomaly(request.context.tenant_id, request.anomaly)
            response_0 = anomalies_v1_anomaly_service_pb2.UpdateAnomalyResponse()
            response_1 = anomalies_v1_anomaly_service_pb2.GetAnomalyResponse()
            outgoing_0 = anomalies_v1_anomaly_service_pb2.UpdateAnomalyRequest(
                anomaly=anomalies_v1_anomalies_pb2.Anomaly(
                    audit=common_v1_audit_pb2.AuditInfo(updated_by=request.anomaly.audit.updated_by)
                ),
                context=request.context
            )
            registered_0 = cast(
                anomalies_v1_anomaly_service_pb2_grpc.AnomalyServiceStub,
                deps.clients.registry['acme.anomalies.v1.AnomalyService']
            )
            response_0 = await registered_0.UpdateAnomaly(outgoing_0, timeout=deps.settings.timeout)
            command_1 = AnomalyWorkflowAdvanceAnomalyWorkflow1Command(
                context=request.context,
                anomaly_id=request.anomaly_id
            )
            outgoing_1 = to_anomaly_workflow_advance_anomaly_workflow1_command(command_1)
            response_1 = await deps.clients.anomalies_anomaly.GetAnomaly(outgoing_1, timeout=deps.settings.timeout)
            returned_0_0 = response_0.anomaly.sla.paused_for
            if returned_0_0.ListFields():
                response.anomaly.sla.paused_for.MergeFrom(returned_0_0)
            returned_0_1 = response_0.anomaly.sla.policy_id
            if returned_0_1:
                response.anomaly.sla.policy_id = returned_0_1
            returned_1_0 = response_1.anomaly.requester.preferred_channel
            if returned_1_0:
                response.anomaly.requester.preferred_channel = returned_1_0
            echoed_0 = request.anomaly_id
            response.anomaly.anomaly_id = echoed_0
            echoed_1 = request.anomaly.priority
            response.anomaly.priority = echoed_1
            return response

    async def handle_cancel_anomaly_workflow(
        self,
        request: anomalies_v1_anomaly_workflow_service_pb2.CancelAnomalyWorkflowRequest
    ) -> anomalies_v1_anomaly_workflow_service_pb2.CancelAnomalyWorkflowResponse:
        """Cancels an anomaly."""
        deps = self.deps
        response = anomalies_v1_anomaly_workflow_service_pb2.CancelAnomalyWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CancelAnomalyWorkflow', extra={'fields': {'anomaly_id': request.anomaly.anomaly_id}})
            await deps.repository.audit(
                request.context.tenant_id,
                'CancelAnomalyWorkflow',
                {'anomaly_id': request.anomaly.anomaly_id}
            )
            await deps.repository.save_anomaly(request.context.tenant_id, request.anomaly)
            response_0 = datasets_v1_dataset_query_service_pb2.ResolveDatasetsResponse()
            response_1 = anomalies_v1_anomaly_feedback_calculation_service_pb2.CompareAnomalyFeedbackOptionsResponse()
            response_2 = datasets_v1_dataset_version_query_service_pb2.SuggestDatasetVersionsResponse()
            command_0 = AnomalyWorkflowCancelAnomalyWorkflow0Command.model_validate({'context': request.context})
            outgoing_0 = to_anomaly_workflow_cancel_anomaly_workflow0_command(command_0)
            response_0 = await deps.clients.datasets_dataset_query.ResolveDatasets(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = anomalies_v1_anomaly_feedback_calculation_service_pb2.CompareAnomalyFeedbackOptionsRequest(
                annotations=dict(request.annotations),
                anomaly_feedback=anomalies_v1_anomalies_pb2.AnomalyFeedback(
                    correlation_id=response_0.result.correlation_id,
                    subject=datasets_v1_refs_pb2.DatasetRef(display_name=request.anomaly.assignee.display_name)
                ),
                context=request.context,
                reason=request.reason
            )
            send_1 = partial(
                deps.clients.anomalies_anomaly_feedback_calculation.CompareAnomalyFeedbackOptions,
                timeout=deps.settings.timeout
            )
            response_1 = await send_1(outgoing_1)
            requests_2: list[datasets_v1_dataset_version_query_service_pb2.SuggestDatasetVersionsRequest] = []
            for item_2 in request.anomaly.history:
                outgoing_2 = datasets_v1_dataset_version_query_service_pb2.SuggestDatasetVersionsRequest(
                    context=request.context,
                    filter=datasets_v1_dataset_version_query_service_pb2.SuggestDatasetVersionsRequest.Filter(
                        created_after=item_2.changed_at,
                        labels=dict(response_0.result.details),
                        owner_id=request.anomaly.sla.policy_id
                    )
                )
                requests_2.append(outgoing_2)
            replies_2 = await asyncio.gather(*(
                deps.clients.datasets_dataset_version_query.SuggestDatasetVersions(
                    entry,
                    timeout=deps.settings.timeout
                ) for entry in requests_2
            ))
            if replies_2:
                response_2 = replies_2[-1]
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.outcome.message = returned_0_0
            returned_1_0 = response_1.result.reference_ids
            response.result.reference_ids.extend(returned_1_0)
            returned_1_1 = response_1.result.correlation_id
            if returned_1_1:
                response.result.correlation_id = returned_1_1
            echoed_0 = request.anomaly_id
            response.anomaly.anomaly_id = echoed_0
            echoed_1 = request.anomaly.priority
            response.anomaly.priority = echoed_1
            return response

    async def handle_list_anomaly_workflows(
        self,
        request: anomalies_v1_anomaly_workflow_service_pb2.ListAnomalyWorkflowsRequest
    ) -> anomalies_v1_anomaly_workflow_service_pb2.ListAnomalyWorkflowsResponse:
        """Lists anomalies a page at a time."""
        deps = self.deps
        response = anomalies_v1_anomaly_workflow_service_pb2.ListAnomalyWorkflowsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ListAnomalyWorkflows', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ListAnomalyWorkflows',
                {'order_by': request.order_by}
            )
            response_0 = anomalies_v1_detector_validation_service_pb2.CheckDetectorEligibilityResponse()
            response_1 = metrics_v1_dashboard_export_service_pb2.StreamDashboardExportResponse()
            outgoing_0 = anomalies_v1_detector_validation_service_pb2.CheckDetectorEligibilityRequest(
                context=request.context,
                details=anomalies_v1_detector_validation_service_pb2.CheckDetectorEligibilityRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(email=request.context.actor.email),
                    locale=request.context.locale
                ),
                detector=anomalies_v1_anomalies_pb2.Detector(
                    audit=common_v1_audit_pb2.AuditInfo(updated_at=request.filter.created_after),
                    owner=identity_v1_refs_pb2.UserRef(user_id=request.context.actor.user_id)
                )
            )
            response_0 = await deps.clients.anomalies_detector_validation.CheckDetectorEligibility(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = metrics_v1_dashboard_export_service_pb2.StreamDashboardExportRequest(
                context=request.context,
                filter=metrics_v1_dashboard_export_service_pb2.StreamDashboardExportRequest.Filter(
                    query=request.filter.query,
                    region=request.filter.region
                )
            )
            async for chunk_1 in deps.clients.metrics_dashboard_export.StreamDashboardExport(
                outgoing_1,
                timeout=deps.settings.timeout
            ):
                response_1 = chunk_1
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.result.message = returned_0_0
            returned_0_1 = response_0.detector.audit.updated_by
            returned_0_1_part_0 = response.anomalies.add()
            if returned_0_1:
                returned_0_1_part_0.audit.updated_by = returned_0_1
            return response

    async def handle_pause_anomaly_workflow(
        self,
        request: anomalies_v1_anomaly_workflow_service_pb2.PauseAnomalyWorkflowRequest
    ) -> anomalies_v1_anomaly_workflow_service_pb2.PauseAnomalyWorkflowResponse:
        """Pauses an anomaly."""
        deps = self.deps
        response = anomalies_v1_anomaly_workflow_service_pb2.PauseAnomalyWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('PauseAnomalyWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'PauseAnomalyWorkflow', {'reason': request.reason})
            await deps.repository.save_anomaly(request.context.tenant_id, request.anomaly)
            response_0 = anomalies_v1_anomaly_approval_service_pb2.ListPendingAnomaliesResponse()
            response_1 = datasets_v1_dataset_service_pb2.UpdateDatasetResponse()
            callbacks_0: list[
                Callable[[], Awaitable[anomalies_v1_anomaly_approval_service_pb2.ListPendingAnomaliesResponse]]
            ] = []
            for item_0 in request.anomaly.history:
                outgoing_0 = anomalies_v1_anomaly_approval_service_pb2.ListPendingAnomaliesRequest(
                    context=request.context,
                    filter=anomalies_v1_anomaly_approval_service_pb2.ListPendingAnomaliesRequest.Filter(
                        created_after=item_0.changed_at,
                        labels=dict(request.anomaly.custom_fields),
                        owner_id=request.anomaly.anomaly_id
                    )
                )
                async def send_0(
                    payload: anomalies_v1_anomaly_approval_service_pb2.ListPendingAnomaliesRequest = outgoing_0
                ) -> anomalies_v1_anomaly_approval_service_pb2.ListPendingAnomaliesResponse:
                    return await deps.clients.anomalies_anomaly_approval.ListPendingAnomalies(
                        payload,
                        timeout=deps.settings.timeout
                    )
                callbacks_0.append(send_0)
            for callback_0 in callbacks_0:
                response_0 = await callback_0()
            outgoing_1 = datasets_v1_dataset_service_pb2.UpdateDatasetRequest(
                context=request.context,
                dataset=datasets_v1_datasets_pb2.Dataset(
                    audit=common_v1_audit_pb2.AuditInfo(updated_by=request.anomaly.audit.updated_by),
                    owner=identity_v1_refs_pb2.UserRef(
                        display_name=request.anomaly.assignee.display_name,
                        email=request.anomaly.assignee.email,
                        user_id=request.anomaly.assignee.user_id
                    )
                )
            )
            response_1 = await AnomalyWorkflowPauseAnomalyWorkflow1Adapter(
                deps.clients.datasets_dataset,
                deps.settings.timeout
            )(outgoing_1)
            returned_1_0 = response_1.dataset.audit.updated_by
            if returned_1_0:
                response.anomaly.audit.updated_by = returned_1_0
            returned_1_1 = response_1.dataset.owner.display_name
            if returned_1_1:
                response.anomaly.assignee.display_name = returned_1_1
            echoed_0 = request.anomaly_id
            response.anomaly.anomaly_id = echoed_0
            echoed_1 = request.anomaly.priority
            response.anomaly.priority = echoed_1
            return response

    async def handle_resume_anomaly_workflow(
        self,
        request: anomalies_v1_anomaly_workflow_service_pb2.ResumeAnomalyWorkflowRequest
    ) -> anomalies_v1_anomaly_workflow_service_pb2.ResumeAnomalyWorkflowResponse:
        """Resumes an anomaly."""
        deps = self.deps
        response = anomalies_v1_anomaly_workflow_service_pb2.ResumeAnomalyWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ResumeAnomalyWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'ResumeAnomalyWorkflow', {'reason': request.reason})
            await deps.repository.save_anomaly(request.context.tenant_id, request.anomaly)
            response_0 = anomalies_v1_anomaly_query_service_pb2.PeekAnomalyResponse()
            outgoing_0 = anomalies_v1_anomaly_query_service_pb2.PeekAnomalyRequest(
                anomaly_id=request.anomaly.anomaly_id,
                context=request.context
            )
            response_0 = cast(anomalies_v1_anomaly_query_service_pb2.PeekAnomalyResponse, await deps.bus.request(
                'acme.anomalies.v1.AnomalyWorkflowService/ResumeAnomalyWorkflow/0', outgoing_0, deps.settings.timeout,
            ))
            returned_0_0 = response_0.anomaly.audit.etag
            if returned_0_0:
                response.anomaly.audit.etag = returned_0_0
            returned_0_1 = response_0.result.status
            if returned_0_1:
                response.outcome.status = returned_0_1
            echoed_0 = request.anomaly_id
            response.anomaly.anomaly_id = echoed_0
            echoed_1 = request.anomaly.assignee
            response.anomaly.assignee.CopyFrom(echoed_1)
            return response

    async def handle_retry_anomaly_workflow(
        self,
        request: anomalies_v1_anomaly_workflow_service_pb2.RetryAnomalyWorkflowRequest
    ) -> anomalies_v1_anomaly_workflow_service_pb2.RetryAnomalyWorkflowResponse:
        """Retrys an anomaly."""
        deps = self.deps
        response = anomalies_v1_anomaly_workflow_service_pb2.RetryAnomalyWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('RetryAnomalyWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'RetryAnomalyWorkflow', {'reason': request.reason})
            await deps.repository.save_anomaly(request.context.tenant_id, request.anomaly)
            response_0 = datasets_v1_dataset_validation_service_pb2.ScoreDatasetResponse()
            response_1 = datasets_v1_dataset_version_query_service_pb2.ResolveDatasetVersionsResponse()
            response_2 = anomalies_v1_detector_validation_service_pb2.LintDetectorsResponse()
            outgoing_0 = datasets_v1_dataset_validation_service_pb2.ScoreDatasetRequest(
                context=request.context,
                dataset=datasets_v1_datasets_pb2.Dataset(
                    audit=common_v1_audit_pb2.AuditInfo(created_by=request.anomaly.audit.created_by),
                    owner=identity_v1_refs_pb2.UserRef(
                        display_name=request.anomaly.assignee.display_name,
                        email=request.anomaly.requester.email
                    )
                )
            )
            outgoing_1 = datasets_v1_dataset_version_query_service_pb2.ResolveDatasetVersionsRequest(
                context=request.context
            )
            outgoing_2 = anomalies_v1_detector_validation_service_pb2.LintDetectorsRequest(
                context=request.context,
                details=anomalies_v1_detector_validation_service_pb2.LintDetectorsRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(
                        name=request.anomaly.requester.name,
                        phone=request.details.notify.phone
                    )
                ),
                detector=anomalies_v1_anomalies_pb2.Detector(
                    audit=common_v1_audit_pb2.AuditInfo(etag=request.anomaly.audit.etag)
                )
            )
            response_0, response_1, response_2 = await asyncio.gather(
                deps.clients.datasets_dataset_validation.ScoreDataset(outgoing_0, timeout=deps.settings.timeout),
                deps.clients.datasets_dataset_version_query.ResolveDatasetVersions(
                    outgoing_1,
                    timeout=deps.settings.timeout
                ),
                deps.clients.anomalies_detector_validation.LintDetectors(outgoing_2, timeout=deps.settings.timeout),
            )
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.outcome.message = returned_0_0
            returned_1_0 = response_1.result.reference_ids
            response.result.reference_ids.extend(returned_1_0)
            returned_2_0 = response_2.outcome.status
            if returned_2_0:
                response.result.status = returned_2_0
            returned_2_1 = response_2.outcome.effective_at
            if returned_2_1.ListFields():
                response.outcome.effective_at.MergeFrom(returned_2_1)
            echoed_0 = request.anomaly_id
            response.anomaly.anomaly_id = echoed_0
            echoed_1 = request.anomaly.assignee
            response.anomaly.assignee.CopyFrom(echoed_1)
            return response

    async def handle_signal_anomaly_workflow(
        self,
        request: anomalies_v1_anomaly_workflow_service_pb2.SignalAnomalyWorkflowRequest
    ) -> anomalies_v1_anomaly_workflow_service_pb2.SignalAnomalyWorkflowResponse:
        """Signals an anomaly."""
        deps = self.deps
        response = anomalies_v1_anomaly_workflow_service_pb2.SignalAnomalyWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SignalAnomalyWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'SignalAnomalyWorkflow', {'reason': request.reason})
            await deps.repository.save_anomaly(request.context.tenant_id, request.anomaly)
            response_0 = datasets_v1_dataset_version_query_service_pb2.SuggestDatasetVersionsResponse()
            response_1 = datasets_v1_dataset_service_pb2.BatchGetDatasetsResponse()
            outgoing_0 = datasets_v1_dataset_version_query_service_pb2.SuggestDatasetVersionsRequest(
                context=request.context,
                filter=datasets_v1_dataset_version_query_service_pb2.SuggestDatasetVersionsRequest.Filter(
                    created_after=request.anomaly.sla.due_at
                )
            )
            document_0 = MessageToDict(outgoing_0, preserving_proto_field_name=True)
            outgoing_0 = ParseDict(
                document_0,
                datasets_v1_dataset_version_query_service_pb2.SuggestDatasetVersionsRequest()
            )
            response_0 = await deps.clients.datasets_dataset_version_query.SuggestDatasetVersions(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = datasets_v1_dataset_service_pb2.BatchGetDatasetsRequest(context=request.context)
            document_1 = MessageToJson(outgoing_1, preserving_proto_field_name=True)
            outgoing_1 = Parse(document_1, datasets_v1_dataset_service_pb2.BatchGetDatasetsRequest())
            response_1 = await deps.clients.datasets_dataset.BatchGetDatasets(outgoing_1, timeout=deps.settings.timeout)
            returned_0_0 = response_0.result.correlation_id
            if returned_0_0:
                response.result.correlation_id = returned_0_0
            returned_1_0 = response_1.result.status
            if returned_1_0:
                response.result.status = returned_1_0
            returned_1_1 = response_1.result.message
            if returned_1_1:
                response.result.message = returned_1_1
            echoed_0 = request.anomaly_id
            response.anomaly.anomaly_id = echoed_0
            echoed_1 = request.anomaly.assignee
            response.anomaly.assignee.CopyFrom(echoed_1)
            return response

    async def handle_start_anomaly_workflow(
        self,
        request: anomalies_v1_anomaly_workflow_service_pb2.StartAnomalyWorkflowRequest
    ) -> anomalies_v1_anomaly_workflow_service_pb2.StartAnomalyWorkflowResponse:
        """Starts an anomaly."""
        deps = self.deps
        response = anomalies_v1_anomaly_workflow_service_pb2.StartAnomalyWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('StartAnomalyWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'StartAnomalyWorkflow', {'reason': request.reason})
            await deps.repository.save_anomaly(request.context.tenant_id, request.anomaly)
            response_0 = anomalies_v1_anomaly_service_pb2.SearchAnomaliesResponse()
            response_1 = anomalies_v1_anomaly_approval_service_pb2.CommentAnomalyApprovalResponse()
            response_2 = surveys_v1_survey_service_pb2.UpdateSurveyResponse()
            outgoing_0 = anomalies_v1_anomaly_service_pb2.SearchAnomaliesRequest()
            outgoing_0.context.CopyFrom(request.context)
            outgoing_0.filter.created_after.CopyFrom(request.anomaly.sla.due_at)
            outgoing_0.filter.owner_id = request.anomaly.customer.detector_id
            merged_0 = anomalies_v1_anomaly_service_pb2.SearchAnomaliesRequest()
            merged_0.MergeFrom(outgoing_0)
            outgoing_0.CopyFrom(merged_0)
            response_0 = await deps.clients.anomalies_anomaly.SearchAnomalies(outgoing_0, timeout=deps.settings.timeout)
            outgoing_1 = anomalies_v1_anomaly_approval_service_pb2.CommentAnomalyApprovalRequest()
            outgoing_1.context.CopyFrom(request.context)
            outgoing_1.anomaly.assignee.email = request.details.notify.email
            if request.anomaly.WhichOneof('origin') == 'channel':
                outgoing_1.anomaly.channel.address = request.anomaly.channel.address
            response_1 = await deps.clients.anomalies_anomaly_approval.CommentAnomalyApproval(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = surveys_v1_survey_service_pb2.UpdateSurveyRequest(
                context=request.context,
                survey=surveys_v1_surveys_pb2.Survey(
                    counterparty=surveys_v1_refs_pb2.QuestionRef(display_name=request.anomaly.customer.display_name)
                )
            )
            registered_2 = cast(
                surveys_v1_survey_service_pb2_grpc.SurveyServiceStub,
                deps.clients.registry['acme.surveys.v1.SurveyService']
            )
            response_2 = await registered_2.UpdateSurvey(outgoing_2, timeout=deps.settings.timeout)
            returned_0_0 = response_0.result.details
            response.result.details.update(returned_0_0)
            returned_0_1 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_1)
            returned_1_0 = response_1.anomaly.audit.created_at
            returned_1_0_part_1 = response.anomaly.comments.add()
            if returned_1_0.ListFields():
                returned_1_0_part_1.created_at.MergeFrom(returned_1_0)
            returned_2_0 = response_2.result.status
            if returned_2_0:
                response.outcome.status = returned_2_0
            echoed_0 = request.anomaly_id
            response.anomaly.anomaly_id = echoed_0
            echoed_1 = request.anomaly.custom_fields
            response.anomaly.custom_fields.update(echoed_1)
            return response
