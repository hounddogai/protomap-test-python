"""Runs the long-lived workflow that takes an anomaly feedback from start to finish."""

from __future__ import annotations

from collections.abc import AsyncIterator
from collections.abc import Awaitable
from collections.abc import Callable
from dataclasses import dataclass
from functools import partial
from typing import Any
from typing import cast
import asyncio
import logging

from google.protobuf.any_pb2 import Any as AnyMessage
from google.protobuf.json_format import MessageToJson
from google.protobuf.json_format import Parse
import grpc

from acme.anomalies.v1 import anomalies_pb2 as anomalies_v1_anomalies_pb2
from acme.anomalies.v1 import anomaly_approval_service_pb2 as anomalies_v1_anomaly_approval_service_pb2
from acme.anomalies.v1 import (
    anomaly_feedback_calculation_service_pb2 as anomalies_v1_anomaly_feedback_calculation_service_pb2,
)
from acme.anomalies.v1 import (
    anomaly_feedback_workflow_service_pb2 as anomalies_v1_anomaly_feedback_workflow_service_pb2,
)
from acme.anomalies.v1 import (
    anomaly_feedback_workflow_service_pb2_grpc as anomalies_v1_anomaly_feedback_workflow_service_pb2_grpc,
)
from acme.anomalies.v1 import anomaly_query_service_pb2 as anomalies_v1_anomaly_query_service_pb2
from acme.anomalies.v1 import detector_approval_service_pb2 as anomalies_v1_detector_approval_service_pb2
from acme.anomalies.v1 import detector_query_service_pb2 as anomalies_v1_detector_query_service_pb2
from acme.anomalies.v1 import detector_query_service_pb2_grpc as anomalies_v1_detector_query_service_pb2_grpc
from acme.anomalies.v1 import detector_validation_service_pb2 as anomalies_v1_detector_validation_service_pb2
from acme.anomalies.v1 import refs_pb2 as anomalies_v1_refs_pb2
from acme.authorization.v1 import access_policy_service_pb2 as authorization_v1_access_policy_service_pb2
from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.datasets.v1 import data_schema_calculation_service_pb2 as datasets_v1_data_schema_calculation_service_pb2
from acme.datasets.v1 import data_schema_validation_service_pb2 as datasets_v1_data_schema_validation_service_pb2
from acme.datasets.v1 import (
    dataset_version_validation_service_pb2 as datasets_v1_dataset_version_validation_service_pb2,
)
from acme.datasets.v1 import datasets_pb2 as datasets_v1_datasets_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.lineage.v1 import lineage_node_workflow_service_pb2 as lineage_v1_lineage_node_workflow_service_pb2
from acme.lineage.v1 import lineage_pb2 as lineage_v1_lineage_pb2
from acme.metrics.v1 import metric_series_service_pb2 as metrics_v1_metric_series_service_pb2
from acme.metrics.v1 import metrics_pb2 as metrics_v1_metrics_pb2
from acme.notifications.v1 import notification_query_service_pb2 as notifications_v1_notification_query_service_pb2

from acme_data.domains.anomalies import hooks
from acme_data.domains.anomalies.adapters import AnomalyFeedbackWorkflowRetryAnomalyFeedbackWorkflow3Adapter
from acme_data.domains.anomalies.adapters import AnomalyFeedbackWorkflowRetryAnomalyFeedbackWorkflow3Port
from acme_data.domains.anomalies.adapters import AnomalyFeedbackWorkflowSignalAnomalyFeedbackWorkflow1Adapter
from acme_data.domains.anomalies.dependencies import Dependencies
from acme_data.domains.anomalies.models import AnomalyFeedbackWorkflowResumeAnomalyFeedbackWorkflow1Command
from acme_data.domains.anomalies.models import to_anomaly_feedback_workflow_resume_anomaly_feedback_workflow1_command
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import run_steps
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_id
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


@dataclass(slots=True)
class AnomalyFeedbackWorkflowServicer(
    anomalies_v1_anomaly_feedback_workflow_service_pb2_grpc.AnomalyFeedbackWorkflowServiceServicer
):
    deps: Dependencies

    @rpc_errors
    async def AdvanceAnomalyFeedbackWorkflow(
        self, request: anomalies_v1_anomaly_feedback_workflow_service_pb2.AdvanceAnomalyFeedbackWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> anomalies_v1_anomaly_feedback_workflow_service_pb2.AdvanceAnomalyFeedbackWorkflowResponse:
        """Advances an anomaly feedback."""
        return await self.handle_advance_anomaly_feedback_workflow(request)

    @rpc_errors
    async def CancelAnomalyFeedbackWorkflow(
        self, request: anomalies_v1_anomaly_feedback_workflow_service_pb2.CancelAnomalyFeedbackWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> anomalies_v1_anomaly_feedback_workflow_service_pb2.CancelAnomalyFeedbackWorkflowResponse:
        """Cancels an anomaly feedback."""
        return await self.handle_cancel_anomaly_feedback_workflow(request)

    @rpc_errors
    @retry_transient
    async def InspectAnomalyFeedbackWorkflow(
        self, request: anomalies_v1_anomaly_feedback_workflow_service_pb2.InspectAnomalyFeedbackWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> anomalies_v1_anomaly_feedback_workflow_service_pb2.InspectAnomalyFeedbackWorkflowResponse:
        """Returns an anomaly feedback."""
        return await self.handle_inspect_anomaly_feedback_workflow(request)

    @rpc_errors
    @retry_transient
    async def ListAnomalyFeedbackWorkflows(
        self, request: anomalies_v1_anomaly_feedback_workflow_service_pb2.ListAnomalyFeedbackWorkflowsRequest, context: grpc.aio.ServicerContext,
    ) -> anomalies_v1_anomaly_feedback_workflow_service_pb2.ListAnomalyFeedbackWorkflowsResponse:
        """Lists anomaly feedbacks a page at a time."""
        return await self.handle_list_anomaly_feedback_workflows(request)

    @rpc_errors
    async def PauseAnomalyFeedbackWorkflow(
        self, request: anomalies_v1_anomaly_feedback_workflow_service_pb2.PauseAnomalyFeedbackWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> anomalies_v1_anomaly_feedback_workflow_service_pb2.PauseAnomalyFeedbackWorkflowResponse:
        """Pauses an anomaly feedback."""
        return await self.handle_pause_anomaly_feedback_workflow(request)

    @rpc_errors
    async def ResumeAnomalyFeedbackWorkflow(
        self, request: anomalies_v1_anomaly_feedback_workflow_service_pb2.ResumeAnomalyFeedbackWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> anomalies_v1_anomaly_feedback_workflow_service_pb2.ResumeAnomalyFeedbackWorkflowResponse:
        """Resumes an anomaly feedback."""
        return await self.handle_resume_anomaly_feedback_workflow(request)

    @rpc_errors
    async def RetryAnomalyFeedbackWorkflow(
        self, request: anomalies_v1_anomaly_feedback_workflow_service_pb2.RetryAnomalyFeedbackWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> anomalies_v1_anomaly_feedback_workflow_service_pb2.RetryAnomalyFeedbackWorkflowResponse:
        """Retrys an anomaly feedback."""
        return await self.handle_retry_anomaly_feedback_workflow(request)

    @rpc_errors
    async def SignalAnomalyFeedbackWorkflow(
        self, request: anomalies_v1_anomaly_feedback_workflow_service_pb2.SignalAnomalyFeedbackWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> anomalies_v1_anomaly_feedback_workflow_service_pb2.SignalAnomalyFeedbackWorkflowResponse:
        """Signals an anomaly feedback."""
        return await self.handle_signal_anomaly_feedback_workflow(request)

    @rpc_errors
    async def StartAnomalyFeedbackWorkflow(
        self, request: anomalies_v1_anomaly_feedback_workflow_service_pb2.StartAnomalyFeedbackWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> anomalies_v1_anomaly_feedback_workflow_service_pb2.StartAnomalyFeedbackWorkflowResponse:
        """Starts an anomaly feedback."""
        return await self.handle_start_anomaly_feedback_workflow(request)

    async def handle_advance_anomaly_feedback_workflow(
        self,
        request: anomalies_v1_anomaly_feedback_workflow_service_pb2.AdvanceAnomalyFeedbackWorkflowRequest
    ) -> anomalies_v1_anomaly_feedback_workflow_service_pb2.AdvanceAnomalyFeedbackWorkflowResponse:
        """Advances an anomaly feedback."""
        deps = self.deps
        response = anomalies_v1_anomaly_feedback_workflow_service_pb2.AdvanceAnomalyFeedbackWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('AdvanceAnomalyFeedbackWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'AdvanceAnomalyFeedbackWorkflow',
                {'reason': request.reason}
            )
            await deps.repository.save_anomaly_feedback(request.context.tenant_id, request.anomaly_feedback)
            response_0 = metrics_v1_metric_series_service_pb2.CreateMetricSeriesResponse()
            response_1 = lineage_v1_lineage_node_workflow_service_pb2.AdvanceLineageNodeWorkflowResponse()
            outgoing_0 = metrics_v1_metric_series_service_pb2.CreateMetricSeriesRequest(
                context=request.context,
                metric_series=metrics_v1_metrics_pb2.MetricSeries(
                    code=request.anomaly_feedback.subject.code,
                    owner=identity_v1_refs_pb2.UserRef(
                        display_name=request.anomaly_feedback.subject.display_name,
                        email=request.details.notify.email,
                        user_id=request.context.actor.user_id
                    )
                )
            )
            method_name_0 = 'CreateMetricSeries'
            response_0 = await getattr(
                deps.clients.metrics_metric_series,
                method_name_0
            )(outgoing_0, timeout=deps.settings.timeout)
            fields_1: dict[str, Any] = {
                'context': request.context,
                'lineage_node': {
                    'children': [{'children': [{'audit': {'updated_at': response_0.metric_series.audit.updated_at}}]}]
                }
            }
            outgoing_1 = lineage_v1_lineage_node_workflow_service_pb2.AdvanceLineageNodeWorkflowRequest(**fields_1)
            response_1 = await deps.clients.lineage_lineage_node_workflow.AdvanceLineageNodeWorkflow(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.result.message = returned_0_0
            returned_0_1 = response_0.result.details
            response.result.details.update(returned_0_1)
            returned_1_0 = response_1.result.correlation_id
            if returned_1_0:
                response.result.correlation_id = returned_1_0
            returned_1_1 = response_1.result.message
            if returned_1_1:
                response.result.message = returned_1_1
            echoed_0 = request.anomaly_feedback_id
            response.anomaly_feedback.anomaly_feedback_id = echoed_0
            echoed_1 = request.anomaly_feedback.attributes
            response.anomaly_feedback.attributes.update(echoed_1)
            return response

    async def handle_cancel_anomaly_feedback_workflow(
        self,
        request: anomalies_v1_anomaly_feedback_workflow_service_pb2.CancelAnomalyFeedbackWorkflowRequest
    ) -> anomalies_v1_anomaly_feedback_workflow_service_pb2.CancelAnomalyFeedbackWorkflowResponse:
        """Cancels an anomaly feedback."""
        deps = self.deps
        response = anomalies_v1_anomaly_feedback_workflow_service_pb2.CancelAnomalyFeedbackWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CancelAnomalyFeedbackWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'CancelAnomalyFeedbackWorkflow',
                {'reason': request.reason}
            )
            await deps.repository.save_anomaly_feedback(request.context.tenant_id, request.anomaly_feedback)
            response_0 = anomalies_v1_detector_approval_service_pb2.CommentDetectorApprovalResponse()
            response_1 = datasets_v1_dataset_version_validation_service_pb2.PreviewDatasetVersionResponse()
            requests_0: list[anomalies_v1_detector_approval_service_pb2.CommentDetectorApprovalRequest] = []
            for item_0 in request.anomaly_feedback.measurements:
                outgoing_0 = anomalies_v1_detector_approval_service_pb2.CommentDetectorApprovalRequest(
                    context=request.context,
                    detector=anomalies_v1_anomalies_pb2.Detector(
                        audit=common_v1_audit_pb2.AuditInfo(created_at=item_0.observed_at)
                    )
                )
                requests_0.append(outgoing_0)
            replies_0 = await asyncio.gather(*(
                deps.clients.anomalies_detector_approval.CommentDetectorApproval(
                    entry,
                    timeout=deps.settings.timeout
                ) for entry in requests_0
            ))
            if replies_0:
                response_0 = replies_0[-1]
            outgoing_1 = datasets_v1_dataset_version_validation_service_pb2.PreviewDatasetVersionRequest(
                context=request.context,
                details=datasets_v1_dataset_version_validation_service_pb2.PreviewDatasetVersionRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(email=request.details.notify.email)
                )
            )
            document_1 = MessageToJson(outgoing_1, preserving_proto_field_name=True)
            outgoing_1 = Parse(
                document_1,
                datasets_v1_dataset_version_validation_service_pb2.PreviewDatasetVersionRequest()
            )
            response_1 = await deps.clients.datasets_dataset_version_validation.PreviewDatasetVersion(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_1_0 = response_1.dataset_version.source
            if returned_1_0:
                response.anomaly_feedback.source = returned_1_0
            returned_1_1 = response_1.result.reference_ids
            response.result.reference_ids.extend(returned_1_1)
            echoed_0 = request.anomaly_feedback_id
            response.anomaly_feedback.anomaly_feedback_id = echoed_0
            echoed_1 = request.anomaly_feedback.correlation_id
            response.anomaly_feedback.correlation_id = echoed_1
            return response

    async def handle_inspect_anomaly_feedback_workflow(
        self,
        request: anomalies_v1_anomaly_feedback_workflow_service_pb2.InspectAnomalyFeedbackWorkflowRequest
    ) -> anomalies_v1_anomaly_feedback_workflow_service_pb2.InspectAnomalyFeedbackWorkflowResponse:
        """Returns an anomaly feedback."""
        deps = self.deps
        response = anomalies_v1_anomaly_feedback_workflow_service_pb2.InspectAnomalyFeedbackWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('InspectAnomalyFeedbackWorkflow', extra={'fields': {'locale': request.context.locale}})
            await deps.repository.audit(
                request.context.tenant_id,
                'InspectAnomalyFeedbackWorkflow',
                {'locale': request.context.locale}
            )
            echoed_0 = request.anomaly_feedback_id
            response.anomaly_feedback.anomaly_feedback_id = echoed_0
            return response

    async def handle_list_anomaly_feedback_workflows(
        self,
        request: anomalies_v1_anomaly_feedback_workflow_service_pb2.ListAnomalyFeedbackWorkflowsRequest
    ) -> anomalies_v1_anomaly_feedback_workflow_service_pb2.ListAnomalyFeedbackWorkflowsResponse:
        """Lists anomaly feedbacks a page at a time."""
        deps = self.deps
        response = anomalies_v1_anomaly_feedback_workflow_service_pb2.ListAnomalyFeedbackWorkflowsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ListAnomalyFeedbackWorkflows', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ListAnomalyFeedbackWorkflows',
                {'order_by': request.order_by}
            )
            response_0 = authorization_v1_access_policy_service_pb2.ListAccessPoliciesResponse()
            response_1 = datasets_v1_data_schema_validation_service_pb2.PreviewDataSchemaResponse()
            outgoing_0 = authorization_v1_access_policy_service_pb2.ListAccessPoliciesRequest(
                context=request.context,
                filter=authorization_v1_access_policy_service_pb2.ListAccessPoliciesRequest.Filter(
                    owner_id=request.filter.owner_id
                )
            )
            response_0 = await deps.clients.authorization_access_policy.ListAccessPolicies(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = datasets_v1_data_schema_validation_service_pb2.PreviewDataSchemaRequest(
                context=request.context,
                data_schema=datasets_v1_datasets_pb2.DataSchema(
                    children=[
                        datasets_v1_datasets_pb2.DataSchema(
                            children=[
                                datasets_v1_datasets_pb2.DataSchema(
                                    location=common_v1_address_pb2.PostalAddress(region=request.filter.region)
                                )
                            ]
                        )
                    ]
                )
            )
            envelope_1 = AnyMessage()
            envelope_1.Pack(outgoing_1)
            outgoing_1 = datasets_v1_data_schema_validation_service_pb2.PreviewDataSchemaRequest()
            if not envelope_1.Unpack(outgoing_1):
                raise ValueError("partner envelope contains the wrong request type")
            response_1 = await deps.clients.datasets_data_schema_validation.PreviewDataSchema(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.page_info.total_size
            if returned_0_0:
                response.page_info.total_size = returned_0_0
            returned_1_0 = response_1.result.correlation_id
            returned_1_0_part_0 = response.anomaly_feedbacks.add()
            if returned_1_0:
                returned_1_0_part_0.correlation_id = returned_1_0
            returned_1_1 = response_1.result.correlation_id
            if returned_1_1:
                response.result.correlation_id = returned_1_1
            return response

    async def handle_pause_anomaly_feedback_workflow(
        self,
        request: anomalies_v1_anomaly_feedback_workflow_service_pb2.PauseAnomalyFeedbackWorkflowRequest
    ) -> anomalies_v1_anomaly_feedback_workflow_service_pb2.PauseAnomalyFeedbackWorkflowResponse:
        """Pauses an anomaly feedback."""
        deps = self.deps
        response = anomalies_v1_anomaly_feedback_workflow_service_pb2.PauseAnomalyFeedbackWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('PauseAnomalyFeedbackWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'PauseAnomalyFeedbackWorkflow',
                {'reason': request.reason}
            )
            await deps.repository.save_anomaly_feedback(request.context.tenant_id, request.anomaly_feedback)
            response_0 = anomalies_v1_detector_query_service_pb2.BrowseDetectorsResponse()
            outgoing_0 = anomalies_v1_detector_query_service_pb2.BrowseDetectorsRequest(
                context=request.context,
                filter=anomalies_v1_detector_query_service_pb2.BrowseDetectorsRequest.Filter(
                    labels=dict(request.details.parameters)
                )
            )
            registered_0 = cast(
                anomalies_v1_detector_query_service_pb2_grpc.DetectorQueryServiceStub,
                deps.clients.registry['acme.anomalies.v1.DetectorQueryService']
            )
            response_0 = await registered_0.BrowseDetectors(outgoing_0, timeout=deps.settings.timeout)
            returned_0_0 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_0)
            echoed_0 = request.anomaly_feedback_id
            response.anomaly_feedback.anomaly_feedback_id = echoed_0
            echoed_1 = request.anomaly_feedback.kind
            response.anomaly_feedback.kind = echoed_1
            return response

    async def handle_resume_anomaly_feedback_workflow(
        self,
        request: anomalies_v1_anomaly_feedback_workflow_service_pb2.ResumeAnomalyFeedbackWorkflowRequest
    ) -> anomalies_v1_anomaly_feedback_workflow_service_pb2.ResumeAnomalyFeedbackWorkflowResponse:
        """Resumes an anomaly feedback."""
        deps = self.deps
        response = anomalies_v1_anomaly_feedback_workflow_service_pb2.ResumeAnomalyFeedbackWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ResumeAnomalyFeedbackWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ResumeAnomalyFeedbackWorkflow',
                {'reason': request.reason}
            )
            await deps.repository.save_anomaly_feedback(request.context.tenant_id, request.anomaly_feedback)
            response_0 = lineage_v1_lineage_node_workflow_service_pb2.StartLineageNodeWorkflowResponse()
            response_1 = datasets_v1_data_schema_validation_service_pb2.PreviewDataSchemaResponse()
            callbacks_0: list[
                Callable[[], Awaitable[lineage_v1_lineage_node_workflow_service_pb2.StartLineageNodeWorkflowResponse]]
            ] = []
            for item_0 in request.anomaly_feedback.measurements:
                outgoing_0 = lineage_v1_lineage_node_workflow_service_pb2.StartLineageNodeWorkflowRequest(
                    context=request.context,
                    lineage_node=lineage_v1_lineage_pb2.LineageNode(
                        children=[
                            lineage_v1_lineage_pb2.LineageNode(
                                children=[
                                    lineage_v1_lineage_pb2.LineageNode(
                                        audit=common_v1_audit_pb2.AuditInfo(updated_at=item_0.observed_at)
                                    )
                                ]
                            )
                        ]
                    )
                )
                async def send_0(
                    payload: lineage_v1_lineage_node_workflow_service_pb2.StartLineageNodeWorkflowRequest = outgoing_0
                ) -> lineage_v1_lineage_node_workflow_service_pb2.StartLineageNodeWorkflowResponse:
                    return await deps.clients.lineage_lineage_node_workflow.StartLineageNodeWorkflow(
                        payload,
                        timeout=deps.settings.timeout
                    )
                callbacks_0.append(send_0)
            for callback_0 in callbacks_0:
                response_0 = await callback_0()
            command_1 = AnomalyFeedbackWorkflowResumeAnomalyFeedbackWorkflow1Command.model_validate(
                {
                    'context': request.context,
                    'data_schema_children_children_audit_updated_at': response_0.lineage_node.audit.updated_at
                }
            )
            outgoing_1 = to_anomaly_feedback_workflow_resume_anomaly_feedback_workflow1_command(command_1)
            response_1 = await deps.clients.datasets_data_schema_validation.PreviewDataSchema(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_1_0 = response_1.outcome.status
            if returned_1_0:
                response.outcome.status = returned_1_0
            echoed_0 = request.anomaly_feedback_id
            response.anomaly_feedback.anomaly_feedback_id = echoed_0
            echoed_1 = request.anomaly_feedback.occurred_at
            response.anomaly_feedback.occurred_at.CopyFrom(echoed_1)
            return response

    async def handle_retry_anomaly_feedback_workflow(
        self,
        request: anomalies_v1_anomaly_feedback_workflow_service_pb2.RetryAnomalyFeedbackWorkflowRequest
    ) -> anomalies_v1_anomaly_feedback_workflow_service_pb2.RetryAnomalyFeedbackWorkflowResponse:
        """Retrys an anomaly feedback."""
        deps = self.deps
        response = anomalies_v1_anomaly_feedback_workflow_service_pb2.RetryAnomalyFeedbackWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('RetryAnomalyFeedbackWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'RetryAnomalyFeedbackWorkflow',
                {'reason': request.reason}
            )
            await deps.repository.save_anomaly_feedback(request.context.tenant_id, request.anomaly_feedback)
            response_0 = anomalies_v1_anomaly_approval_service_pb2.EscalateAnomalyResponse()
            response_1 = datasets_v1_data_schema_calculation_service_pb2.EstimateDataSchemaResponse()
            response_2 = anomalies_v1_anomaly_feedback_calculation_service_pb2.QuoteAnomalyFeedbackResponse()
            response_3 = anomalies_v1_detector_validation_service_pb2.ValidateDetectorResponse()
            outgoing_0 = anomalies_v1_anomaly_approval_service_pb2.EscalateAnomalyRequest(
                anomaly=anomalies_v1_anomalies_pb2.Anomaly(
                    customer=anomalies_v1_refs_pb2.DetectorRef(
                        display_name=request.anomaly_feedback.subject.display_name
                    ),
                    requester=common_v1_contact_pb2.ContactInfo(phone=request.details.notify.phone)
                ),
                context=request.context,
                details=anomalies_v1_anomaly_approval_service_pb2.EscalateAnomalyRequest.Details(
                    approver=identity_v1_refs_pb2.UserRef(email=request.details.notify.email)
                )
            )
            send_0 = partial(deps.clients.anomalies_anomaly_approval.EscalateAnomaly, timeout=deps.settings.timeout)
            response_0 = await send_0(outgoing_0)
            outgoing_1 = datasets_v1_data_schema_calculation_service_pb2.EstimateDataSchemaRequest(
                context=request.context,
                data_schema=datasets_v1_datasets_pb2.DataSchema(
                    children=[
                        datasets_v1_datasets_pb2.DataSchema(
                            children=[
                                datasets_v1_datasets_pb2.DataSchema(
                                    audit=common_v1_audit_pb2.AuditInfo(
                                        created_by=response_0.anomaly.audit.created_by,
                                        updated_by=response_0.anomaly.audit.updated_by
                                    )
                                )
                            ],
                            manager=identity_v1_refs_pb2.UserRef(
                                display_name=response_0.anomaly.assignee.display_name,
                                email=response_0.anomaly.requester.email
                            )
                        )
                    ]
                )
            )
            response_1 = await hooks.anomaly_feedback_workflow_retry_anomaly_feedback_workflow1(
                deps.clients.datasets_data_schema_calculation,
                outgoing_1,
                deps.settings.timeout
            )
            outgoing_2 = anomalies_v1_anomaly_feedback_calculation_service_pb2.QuoteAnomalyFeedbackRequest()
            outgoing_2.context.CopyFrom(request.context)
            outgoing_2.details.destination.postal_code = response_1.data_schema.location.postal_code
            outgoing_2.details.destination.country_code = response_1.data_schema.location.country_code
            outgoing_2.details.destination.lines.extend(list(response_1.data_schema.location.lines))
            outgoing_2.context.tenant_id = tenant_id.get()
            response_2 = await deps.clients.anomalies_anomaly_feedback_calculation.QuoteAnomalyFeedback(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            outgoing_3 = anomalies_v1_detector_validation_service_pb2.ValidateDetectorRequest(
                context=request.context,
                details=anomalies_v1_detector_validation_service_pb2.ValidateDetectorRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(
                        email=response_1.data_schema.manager.email,
                        name=response_0.anomaly.requester.name
                    )
                )
            )
            port_3: AnomalyFeedbackWorkflowRetryAnomalyFeedbackWorkflow3Port = AnomalyFeedbackWorkflowRetryAnomalyFeedbackWorkflow3Adapter(
                deps.clients.anomalies_detector_validation,
                deps.settings.timeout
            )
            response_3 = await port_3.execute(outgoing_3)
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.outcome.message = returned_0_0
            returned_0_1 = response_0.anomaly.customer.display_name
            if returned_0_1:
                response.anomaly_feedback.subject.display_name = returned_0_1
            returned_1_0 = response_1.data_schema.manager.display_name
            if returned_1_0:
                response.anomaly_feedback.subject.display_name = returned_1_0
            returned_2_0 = response_2.anomaly_feedback.subject
            if returned_2_0.ListFields():
                response.anomaly_feedback.subject.MergeFrom(returned_2_0)
            returned_2_1 = response_2.anomaly_feedback.correlation_id
            if returned_2_1:
                response.result.correlation_id = returned_2_1
            returned_3_0 = response_3.result.status
            if returned_3_0:
                response.result.status = returned_3_0
            returned_3_1 = response_3.result.correlation_id
            if returned_3_1:
                response.anomaly_feedback.correlation_id = returned_3_1
            echoed_0 = request.anomaly_feedback_id
            response.anomaly_feedback.anomaly_feedback_id = echoed_0
            echoed_1 = request.anomaly_feedback.sequence
            response.anomaly_feedback.sequence = echoed_1
            return response

    async def handle_signal_anomaly_feedback_workflow(
        self,
        request: anomalies_v1_anomaly_feedback_workflow_service_pb2.SignalAnomalyFeedbackWorkflowRequest
    ) -> anomalies_v1_anomaly_feedback_workflow_service_pb2.SignalAnomalyFeedbackWorkflowResponse:
        """Signals an anomaly feedback."""
        deps = self.deps
        response = anomalies_v1_anomaly_feedback_workflow_service_pb2.SignalAnomalyFeedbackWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SignalAnomalyFeedbackWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'SignalAnomalyFeedbackWorkflow',
                {'reason': request.reason}
            )
            await deps.repository.save_anomaly_feedback(request.context.tenant_id, request.anomaly_feedback)
            response_0 = anomalies_v1_anomaly_query_service_pb2.BrowseAnomaliesResponse()
            response_1 = anomalies_v1_detector_query_service_pb2.BrowseDetectorsResponse()
            response_2 = notifications_v1_notification_query_service_pb2.ResolveNotificationsResponse()
            response_3 = anomalies_v1_detector_approval_service_pb2.RecallDetectorResponse()
            outgoing_0 = anomalies_v1_anomaly_query_service_pb2.BrowseAnomaliesRequest(
                context=request.context,
                filter=anomalies_v1_anomaly_query_service_pb2.BrowseAnomaliesRequest.Filter(
                    created_after=request.anomaly_feedback.occurred_at,
                    owner_id=request.anomaly_feedback.correlation_id
                )
            )
            steps_0 = [
                partial(deps.clients.anomalies_anomaly_query.BrowseAnomalies, outgoing_0, timeout=deps.settings.timeout)
            ]
            results_0 = await run_steps(steps_0)
            response_0 = results_0[-1]
            outgoing_1 = anomalies_v1_detector_query_service_pb2.BrowseDetectorsRequest(
                context=request.context,
                filter=anomalies_v1_detector_query_service_pb2.BrowseDetectorsRequest.Filter(
                    created_after=request.anomaly_feedback.occurred_at,
                    labels=dict(request.annotations),
                    owner_id=request.anomaly_feedback.subject.dataset_id
                )
            )
            response_1 = await AnomalyFeedbackWorkflowSignalAnomalyFeedbackWorkflow1Adapter(
                deps.clients.anomalies_detector_query,
                deps.settings.timeout
            )(outgoing_1)
            outgoing_2 = notifications_v1_notification_query_service_pb2.ResolveNotificationsRequest(
                context=request.context
            )
            response_2 = cast(notifications_v1_notification_query_service_pb2.ResolveNotificationsResponse, await deps.bus.request(
                'acme.anomalies.v1.AnomalyFeedbackWorkflowService/SignalAnomalyFeedbackWorkflow/2', outgoing_2, deps.settings.timeout,
            ))
            outgoing_3 = anomalies_v1_detector_approval_service_pb2.RecallDetectorRequest(
                context=request.context,
                details=anomalies_v1_detector_approval_service_pb2.RecallDetectorRequest.Details(
                    approver=identity_v1_refs_pb2.UserRef(email=request.details.notify.email)
                ),
                detector=anomalies_v1_anomalies_pb2.Detector(
                    owner=identity_v1_refs_pb2.UserRef(display_name=request.anomaly_feedback.subject.display_name)
                )
            )
            response_3 = await deps.clients.anomalies_detector_approval.RecallDetector(
                outgoing_3,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.correlation_id
            if returned_0_0:
                response.result.correlation_id = returned_0_0
            returned_0_1 = response_0.result.message
            if returned_0_1:
                response.result.message = returned_0_1
            returned_1_0 = response_1.result.reference_ids
            response.result.reference_ids.extend(returned_1_0)
            returned_2_0 = response_2.result.status
            if returned_2_0:
                response.result.status = returned_2_0
            returned_3_0 = response_3.result.details
            response.result.details.update(returned_3_0)
            echoed_0 = request.anomaly_feedback_id
            response.anomaly_feedback.anomaly_feedback_id = echoed_0
            echoed_1 = request.anomaly_feedback.correlation_id
            response.anomaly_feedback.correlation_id = echoed_1
            return response

    async def handle_start_anomaly_feedback_workflow(
        self,
        request: anomalies_v1_anomaly_feedback_workflow_service_pb2.StartAnomalyFeedbackWorkflowRequest
    ) -> anomalies_v1_anomaly_feedback_workflow_service_pb2.StartAnomalyFeedbackWorkflowResponse:
        """Starts an anomaly feedback."""
        deps = self.deps
        response = anomalies_v1_anomaly_feedback_workflow_service_pb2.StartAnomalyFeedbackWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('StartAnomalyFeedbackWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'StartAnomalyFeedbackWorkflow',
                {'reason': request.reason}
            )
            await deps.repository.save_anomaly_feedback(request.context.tenant_id, request.anomaly_feedback)
            response_0 = anomalies_v1_detector_query_service_pb2.BrowseDetectorsResponse()
            response_1 = datasets_v1_dataset_version_validation_service_pb2.LintDatasetVersionsResponse()
            outgoing_0 = anomalies_v1_detector_query_service_pb2.BrowseDetectorsRequest(
                context=request.context,
                filter=anomalies_v1_detector_query_service_pb2.BrowseDetectorsRequest.Filter(
                    created_after=request.anomaly_feedback.occurred_at,
                    labels=dict(request.anomaly_feedback.attributes),
                    owner_id=request.anomaly_feedback.anomaly_feedback_id
                )
            )
            outgoing_1 = datasets_v1_dataset_version_validation_service_pb2.LintDatasetVersionsRequest(
                context=request.context,
                dataset_version=datasets_v1_datasets_pb2.DatasetVersion(source=request.anomaly_feedback.source),
                details=datasets_v1_dataset_version_validation_service_pb2.LintDatasetVersionsRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(phone=request.details.notify.phone)
                )
            )
            response_0, response_1 = await asyncio.gather(
                deps.clients.anomalies_detector_query.BrowseDetectors(outgoing_0, timeout=deps.settings.timeout),
                deps.clients.datasets_dataset_version_validation.LintDatasetVersions(
                    outgoing_1,
                    timeout=deps.settings.timeout
                ),
            )
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.result.message = returned_0_0
            returned_1_0 = response_1.result.message
            if returned_1_0:
                response.result.message = returned_1_0
            returned_1_1 = response_1.result.correlation_id
            if returned_1_1:
                response.anomaly_feedback.correlation_id = returned_1_1
            echoed_0 = request.anomaly_feedback_id
            response.anomaly_feedback.anomaly_feedback_id = echoed_0
            echoed_1 = request.anomaly_feedback.attributes
            response.anomaly_feedback.attributes.update(echoed_1)
            return response
