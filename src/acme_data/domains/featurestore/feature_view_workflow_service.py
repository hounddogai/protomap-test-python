"""Runs the long-lived workflow that takes a feature view from start to finish."""

from __future__ import annotations

from collections.abc import AsyncIterator
from functools import partial
from typing import cast
import asyncio
import logging

from google.protobuf.any_pb2 import Any as AnyMessage
from google.protobuf.json_format import MessageToDict
from google.protobuf.json_format import ParseDict
import grpc

from acme.authorization.v1 import access_policy_service_pb2 as authorization_v1_access_policy_service_pb2
from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.customers.v1 import refs_pb2 as customers_v1_refs_pb2
from acme.datasets.v1 import data_schema_validation_service_pb2 as datasets_v1_data_schema_validation_service_pb2
from acme.datasets.v1 import (
    data_schema_validation_service_pb2_grpc as datasets_v1_data_schema_validation_service_pb2_grpc,
)
from acme.datasets.v1 import (
    dataset_version_calculation_service_pb2 as datasets_v1_dataset_version_calculation_service_pb2,
)
from acme.datasets.v1 import datasets_pb2 as datasets_v1_datasets_pb2
from acme.datasets.v1 import refs_pb2 as datasets_v1_refs_pb2
from acme.featurestore.v1 import entity_lifecycle_service_pb2 as featurestore_v1_entity_lifecycle_service_pb2
from acme.featurestore.v1 import entity_sync_service_pb2 as featurestore_v1_entity_sync_service_pb2
from acme.featurestore.v1 import (
    feature_value_approval_service_pb2 as featurestore_v1_feature_value_approval_service_pb2,
)
from acme.featurestore.v1 import feature_value_import_service_pb2 as featurestore_v1_feature_value_import_service_pb2
from acme.featurestore.v1 import (
    feature_value_reporting_service_pb2 as featurestore_v1_feature_value_reporting_service_pb2,
)
from acme.featurestore.v1 import feature_view_approval_service_pb2 as featurestore_v1_feature_view_approval_service_pb2
from acme.featurestore.v1 import (
    feature_view_lifecycle_service_pb2 as featurestore_v1_feature_view_lifecycle_service_pb2,
)
from acme.featurestore.v1 import feature_view_workflow_service_pb2 as featurestore_v1_feature_view_workflow_service_pb2
from acme.featurestore.v1 import (
    feature_view_workflow_service_pb2_grpc as featurestore_v1_feature_view_workflow_service_pb2_grpc,
)
from acme.featurestore.v1 import featurestore_pb2 as featurestore_v1_featurestore_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.lineage.v1 import impact_workflow_service_pb2 as lineage_v1_impact_workflow_service_pb2
from acme.lineage.v1 import lineage_edge_import_service_pb2 as lineage_v1_lineage_edge_import_service_pb2
from acme.lineage.v1 import lineage_node_sync_service_pb2 as lineage_v1_lineage_node_sync_service_pb2
from acme.lineage.v1 import lineage_pb2 as lineage_v1_lineage_pb2
from acme.metrics.v1 import dashboard_validation_service_pb2 as metrics_v1_dashboard_validation_service_pb2
from acme.metrics.v1 import metrics_pb2 as metrics_v1_metrics_pb2
from acme.search.v1 import search_index_query_service_pb2 as search_v1_search_index_query_service_pb2
from acme.webhooks.v1 import webhook_endpoint_query_service_pb2 as webhooks_v1_webhook_endpoint_query_service_pb2

from acme_data.domains.featurestore.adapters import FeatureViewWorkflowStartFeatureViewWorkflow1Adapter
from acme_data.domains.featurestore.adapters import FeatureViewWorkflowStartFeatureViewWorkflow1Port
from acme_data.domains.featurestore.adapters import FeatureViewWorkflowStartFeatureViewWorkflow3Adapter
from acme_data.domains.featurestore.dependencies import Dependencies
from acme_data.domains.featurestore.models import FeatureViewWorkflowRetryFeatureViewWorkflow0Command
from acme_data.domains.featurestore.models import FeatureViewWorkflowRetryFeatureViewWorkflow1Command
from acme_data.domains.featurestore.models import to_feature_view_workflow_retry_feature_view_workflow0_command
from acme_data.domains.featurestore.models import to_feature_view_workflow_retry_feature_view_workflow1_command
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import run_steps
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_id
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class FeatureViewWorkflowServicer(
    featurestore_v1_feature_view_workflow_service_pb2_grpc.FeatureViewWorkflowServiceServicer
):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    async def AdvanceFeatureViewWorkflow(
        self, request: featurestore_v1_feature_view_workflow_service_pb2.AdvanceFeatureViewWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_feature_view_workflow_service_pb2.AdvanceFeatureViewWorkflowResponse:
        """Advances a feature view."""
        return await self.handle_advance_feature_view_workflow(request)

    @rpc_errors
    async def CancelFeatureViewWorkflow(
        self, request: featurestore_v1_feature_view_workflow_service_pb2.CancelFeatureViewWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_feature_view_workflow_service_pb2.CancelFeatureViewWorkflowResponse:
        """Cancels a feature view."""
        return await self.handle_cancel_feature_view_workflow(request)

    @rpc_errors
    @retry_transient
    async def ListFeatureViewWorkflows(
        self, request: featurestore_v1_feature_view_workflow_service_pb2.ListFeatureViewWorkflowsRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_feature_view_workflow_service_pb2.ListFeatureViewWorkflowsResponse:
        """Lists feature views a page at a time."""
        return await self.handle_list_feature_view_workflows(request)

    @rpc_errors
    async def PauseFeatureViewWorkflow(
        self, request: featurestore_v1_feature_view_workflow_service_pb2.PauseFeatureViewWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_feature_view_workflow_service_pb2.PauseFeatureViewWorkflowResponse:
        """Pauses a feature view."""
        return await self.handle_pause_feature_view_workflow(request)

    @rpc_errors
    async def ResumeFeatureViewWorkflow(
        self, request: featurestore_v1_feature_view_workflow_service_pb2.ResumeFeatureViewWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_feature_view_workflow_service_pb2.ResumeFeatureViewWorkflowResponse:
        """Resumes a feature view."""
        return await self.handle_resume_feature_view_workflow(request)

    @rpc_errors
    async def RetryFeatureViewWorkflow(
        self, request: featurestore_v1_feature_view_workflow_service_pb2.RetryFeatureViewWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_feature_view_workflow_service_pb2.RetryFeatureViewWorkflowResponse:
        """Retrys a feature view."""
        return await self.handle_retry_feature_view_workflow(request)

    @rpc_errors
    async def SignalFeatureViewWorkflow(
        self, request: featurestore_v1_feature_view_workflow_service_pb2.SignalFeatureViewWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_feature_view_workflow_service_pb2.SignalFeatureViewWorkflowResponse:
        """Signals a feature view."""
        return await self.handle_signal_feature_view_workflow(request)

    @rpc_errors
    async def StartFeatureViewWorkflow(
        self, request: featurestore_v1_feature_view_workflow_service_pb2.StartFeatureViewWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_feature_view_workflow_service_pb2.StartFeatureViewWorkflowResponse:
        """Starts a feature view."""
        return await self.handle_start_feature_view_workflow(request)

    async def handle_advance_feature_view_workflow(
        self,
        request: featurestore_v1_feature_view_workflow_service_pb2.AdvanceFeatureViewWorkflowRequest
    ) -> featurestore_v1_feature_view_workflow_service_pb2.AdvanceFeatureViewWorkflowResponse:
        """Advances a feature view."""
        deps = self.deps
        response = featurestore_v1_feature_view_workflow_service_pb2.AdvanceFeatureViewWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('AdvanceFeatureViewWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'AdvanceFeatureViewWorkflow',
                {'reason': request.reason}
            )
            await deps.repository.save_feature_view(request.context.tenant_id, request.feature_view)
            response_0 = webhooks_v1_webhook_endpoint_query_service_pb2.FindWebhookEndpointsResponse()
            response_1 = featurestore_v1_feature_view_approval_service_pb2.DelegateFeatureViewApprovalResponse()
            outgoing_0 = webhooks_v1_webhook_endpoint_query_service_pb2.FindWebhookEndpointsRequest(
                context=request.context,
                filter=webhooks_v1_webhook_endpoint_query_service_pb2.FindWebhookEndpointsRequest.Filter(
                    region=request.feature_view.address.region
                )
            )
            outgoing_1 = featurestore_v1_feature_view_approval_service_pb2.DelegateFeatureViewApprovalRequest(
                context=request.context,
                feature_view=featurestore_v1_featurestore_pb2.FeatureView(
                    components={
                        'primary': featurestore_v1_featurestore_pb2.FeatureViewComponent(
                            component_id=request.feature_view.components.get(
                                'primary',
                                featurestore_v1_featurestore_pb2.FeatureViewComponent()
                            ).component_id
                        )
                    },
                    owner=identity_v1_refs_pb2.UserRef(display_name=request.feature_view.owner.display_name)
                )
            )
            response_0, response_1 = await asyncio.gather(
                deps.clients.webhooks_webhook_endpoint_query.FindWebhookEndpoints(
                    outgoing_0,
                    timeout=deps.settings.timeout
                ),
                deps.clients.featurestore_feature_view_approval.DelegateFeatureViewApproval(
                    outgoing_1,
                    timeout=deps.settings.timeout
                ),
            )
            returned_0_0 = response_0.result.status
            if returned_0_0:
                response.outcome.status = returned_0_0
            returned_0_1 = response_0.result.correlation_id
            if returned_0_1:
                response.result.correlation_id = returned_0_1
            returned_1_0 = response_1.feature_view.audit.created_by
            if returned_1_0:
                response.feature_view.audit.created_by = returned_1_0
            returned_1_1 = response_1.result.status
            if returned_1_1:
                response.outcome.status = returned_1_1
            echoed_0 = request.feature_view_id
            response.feature_view.feature_view_id = echoed_0
            echoed_1 = request.feature_view.capacity
            response.feature_view.capacity = echoed_1
            return response

    async def handle_cancel_feature_view_workflow(
        self,
        request: featurestore_v1_feature_view_workflow_service_pb2.CancelFeatureViewWorkflowRequest
    ) -> featurestore_v1_feature_view_workflow_service_pb2.CancelFeatureViewWorkflowResponse:
        """Cancels a feature view."""
        deps = self.deps
        response = featurestore_v1_feature_view_workflow_service_pb2.CancelFeatureViewWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CancelFeatureViewWorkflow', extra={'fields': {'feature_view_id': request.feature_view_id}})
            await deps.repository.audit(
                request.context.tenant_id,
                'CancelFeatureViewWorkflow',
                {'feature_view_id': request.feature_view_id}
            )
            await deps.repository.save_feature_view(request.context.tenant_id, request.feature_view)
            response_0 = metrics_v1_dashboard_validation_service_pb2.ScoreDashboardResponse()
            response_1 = featurestore_v1_feature_view_approval_service_pb2.DelegateFeatureViewApprovalResponse()
            response_2 = lineage_v1_lineage_edge_import_service_pb2.ListLineageEdgeImportsResponse()
            outgoing_0 = metrics_v1_dashboard_validation_service_pb2.ScoreDashboardRequest(
                context=request.context,
                dashboard=metrics_v1_metrics_pb2.Dashboard(
                    audit=common_v1_audit_pb2.AuditInfo(
                        created_by=request.feature_view.audit.created_by,
                        updated_at=request.feature_view.audit.updated_at
                    ),
                    lines=[
                        metrics_v1_metrics_pb2.DashboardLine(
                            description=request.feature_view.components.get(
                                'primary',
                                featurestore_v1_featurestore_pb2.FeatureViewComponent()
                            ).description
                        )
                    ]
                ),
                details=metrics_v1_dashboard_validation_service_pb2.ScoreDashboardRequest.Details(
                    destination=common_v1_address_pb2.PostalAddress(region=request.feature_view.address.region)
                )
            )
            response_0 = cast(metrics_v1_dashboard_validation_service_pb2.ScoreDashboardResponse, await deps.bus.request(
                'acme.featurestore.v1.FeatureViewWorkflowService/CancelFeatureViewWorkflow/0', outgoing_0, deps.settings.timeout,
            ))
            outgoing_1 = featurestore_v1_feature_view_approval_service_pb2.DelegateFeatureViewApprovalRequest(
                context=request.context,
                details=featurestore_v1_feature_view_approval_service_pb2.DelegateFeatureViewApprovalRequest.Details(
                    approver=identity_v1_refs_pb2.UserRef(email=request.feature_view.owner.email)
                ),
                feature_view=featurestore_v1_featurestore_pb2.FeatureView(
                    audit=common_v1_audit_pb2.AuditInfo(created_at=request.feature_view.audit.created_at)
                )
            )
            response_1 = await deps.clients.featurestore_feature_view_approval.DelegateFeatureViewApproval(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = lineage_v1_lineage_edge_import_service_pb2.ListLineageEdgeImportsRequest(
                context=request.context,
                filter=lineage_v1_lineage_edge_import_service_pb2.ListLineageEdgeImportsRequest.Filter(
                    region=response_0.dashboard.billing_address.region
                )
            )
            method_name_2 = 'ListLineageEdgeImports'
            response_2 = await getattr(
                deps.clients.lineage_lineage_edge_import,
                method_name_2
            )(outgoing_2, timeout=deps.settings.timeout)
            returned_0_0 = response_0.result.correlation_id
            if returned_0_0:
                response.result.correlation_id = returned_0_0
            returned_1_0 = response_1.feature_view.feature_view_id
            if returned_1_0:
                response.feature_view.feature_view_id = returned_1_0
            returned_2_0 = response_2.result.message
            if returned_2_0:
                response.result.message = returned_2_0
            echoed_0 = request.feature_view.capacity
            response.feature_view.capacity = echoed_0
            echoed_1 = request.feature_view.status
            response.feature_view.status = echoed_1
            return response

    async def handle_list_feature_view_workflows(
        self,
        request: featurestore_v1_feature_view_workflow_service_pb2.ListFeatureViewWorkflowsRequest
    ) -> featurestore_v1_feature_view_workflow_service_pb2.ListFeatureViewWorkflowsResponse:
        """Lists feature views a page at a time."""
        deps = self.deps
        response = featurestore_v1_feature_view_workflow_service_pb2.ListFeatureViewWorkflowsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ListFeatureViewWorkflows', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ListFeatureViewWorkflows',
                {'order_by': request.order_by}
            )
            response_0 = lineage_v1_impact_workflow_service_pb2.PauseImpactWorkflowResponse()
            response_1 = featurestore_v1_feature_value_import_service_pb2.RetryFeatureValueImportResponse()
            outgoing_0 = lineage_v1_impact_workflow_service_pb2.PauseImpactWorkflowRequest(
                context=request.context,
                details=lineage_v1_impact_workflow_service_pb2.PauseImpactWorkflowRequest.Details(
                    notify=common_v1_contact_pb2.ContactInfo(email=request.context.actor.email)
                ),
                impact=lineage_v1_lineage_pb2.Impact(
                    assignee=identity_v1_refs_pb2.UserRef(user_id=request.context.actor.user_id)
                )
            )
            response_0 = await deps.clients.lineage_impact_workflow.PauseImpactWorkflow(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = featurestore_v1_feature_value_import_service_pb2.RetryFeatureValueImportRequest(
                context=request.context,
                details=featurestore_v1_feature_value_import_service_pb2.RetryFeatureValueImportRequest.Details(
                    notify=common_v1_contact_pb2.ContactInfo(
                        email=response_0.impact.assignee.email,
                        name=response_0.impact.requester.name,
                        preferred_channel=response_0.impact.requester.preferred_channel
                    )
                ),
                feature_value=featurestore_v1_featurestore_pb2.FeatureValue(
                    subject=datasets_v1_refs_pb2.DatasetRef(display_name=response_0.impact.customer.display_name)
                )
            )
            document_1 = MessageToDict(outgoing_1, preserving_proto_field_name=True)
            outgoing_1 = ParseDict(
                document_1,
                featurestore_v1_feature_value_import_service_pb2.RetryFeatureValueImportRequest()
            )
            response_1 = await deps.clients.featurestore_feature_value_import.RetryFeatureValueImport(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.result.message = returned_0_0
            returned_1_0 = response_1.outcome.status
            if returned_1_0:
                response.result.status = returned_1_0
            return response

    async def handle_pause_feature_view_workflow(
        self,
        request: featurestore_v1_feature_view_workflow_service_pb2.PauseFeatureViewWorkflowRequest
    ) -> featurestore_v1_feature_view_workflow_service_pb2.PauseFeatureViewWorkflowResponse:
        """Pauses a feature view."""
        deps = self.deps
        response = featurestore_v1_feature_view_workflow_service_pb2.PauseFeatureViewWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('PauseFeatureViewWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'PauseFeatureViewWorkflow',
                {'reason': request.reason}
            )
            await deps.repository.save_feature_view(request.context.tenant_id, request.feature_view)
            response_0 = featurestore_v1_feature_value_reporting_service_pb2.StreamFeatureValueMetricsResponse()
            response_1 = lineage_v1_lineage_node_sync_service_pb2.SyncLineageNodesResponse()
            outgoing_0 = featurestore_v1_feature_value_reporting_service_pb2.StreamFeatureValueMetricsRequest(
                context=request.context,
                filter=featurestore_v1_feature_value_reporting_service_pb2.StreamFeatureValueMetricsRequest.Filter(
                    region=request.feature_view.address.region
                ),
                subscriber=common_v1_contact_pb2.ContactInfo(
                    email=request.feature_view.owner.email,
                    phone=request.details.notify.phone,
                    preferred_channel=request.details.notify.preferred_channel
                )
            )
            async for chunk_0 in deps.clients.featurestore_feature_value_reporting.StreamFeatureValueMetrics(
                outgoing_0,
                timeout=deps.settings.timeout
            ):
                response_0 = chunk_0
            outgoing_1 = lineage_v1_lineage_node_sync_service_pb2.SyncLineageNodesRequest()
            outgoing_1.context.CopyFrom(request.context)
            field_1_1_part_1 = outgoing_1.lineage_node.children.add()
            field_1_1_part_2 = field_1_1_part_1.children.add()
            field_1_1_part_2.audit.etag = request.feature_view.audit.etag
            field_1_2_part_1 = outgoing_1.lineage_node.children.add()
            field_1_2_part_2 = field_1_2_part_1.children.add()
            field_1_2_part_2.audit.updated_at.CopyFrom(request.feature_view.audit.updated_at)
            merged_1 = lineage_v1_lineage_node_sync_service_pb2.SyncLineageNodesRequest()
            merged_1.MergeFrom(outgoing_1)
            outgoing_1.CopyFrom(merged_1)
            response_1 = await deps.clients.lineage_lineage_node_sync.SyncLineageNodes(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_1_0 = response_1.outcome.reference_id
            if returned_1_0:
                response.outcome.reference_id = returned_1_0
            echoed_0 = request.feature_view_id
            response.feature_view.feature_view_id = echoed_0
            echoed_1 = request.feature_view.capacity
            response.feature_view.capacity = echoed_1
            return response

    async def handle_resume_feature_view_workflow(
        self,
        request: featurestore_v1_feature_view_workflow_service_pb2.ResumeFeatureViewWorkflowRequest
    ) -> featurestore_v1_feature_view_workflow_service_pb2.ResumeFeatureViewWorkflowResponse:
        """Resumes a feature view."""
        deps = self.deps
        response = featurestore_v1_feature_view_workflow_service_pb2.ResumeFeatureViewWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ResumeFeatureViewWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ResumeFeatureViewWorkflow',
                {'reason': request.reason}
            )
            await deps.repository.save_feature_view(request.context.tenant_id, request.feature_view)
            response_0 = datasets_v1_dataset_version_calculation_service_pb2.ExplainDatasetVersionCalculationResponse()
            response_1 = datasets_v1_data_schema_validation_service_pb2.PreviewDataSchemaResponse()
            outgoing_0 = datasets_v1_dataset_version_calculation_service_pb2.ExplainDatasetVersionCalculationRequest(
                context=request.context,
                dataset_version=datasets_v1_datasets_pb2.DatasetVersion(
                    subject=customers_v1_refs_pb2.CustomerRef(email=request.details.notify.email)
                ),
                details=datasets_v1_dataset_version_calculation_service_pb2.ExplainDatasetVersionCalculationRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(
                        name=request.details.notify.name,
                        phone=request.details.notify.phone
                    )
                )
            )
            envelope_0 = AnyMessage()
            envelope_0.Pack(outgoing_0)
            outgoing_0 = datasets_v1_dataset_version_calculation_service_pb2.ExplainDatasetVersionCalculationRequest()
            if not envelope_0.Unpack(outgoing_0):
                raise ValueError("partner envelope contains the wrong request type")
            response_0 = await deps.clients.datasets_dataset_version_calculation.ExplainDatasetVersionCalculation(
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
                                    manager=identity_v1_refs_pb2.UserRef(
                                        display_name=response_0.dataset_version.subject.display_name,
                                        email=request.feature_view.owner.email
                                    )
                                )
                            ]
                        )
                    ]
                )
            )
            registered_1 = cast(
                datasets_v1_data_schema_validation_service_pb2_grpc.DataSchemaValidationServiceStub,
                deps.clients.registry['acme.datasets.v1.DataSchemaValidationService']
            )
            response_1 = await registered_1.PreviewDataSchema(outgoing_1, timeout=deps.settings.timeout)
            returned_0_0 = response_0.dataset_version.subject.email
            if returned_0_0:
                response.feature_view.owner.email = returned_0_0
            returned_1_0 = response_1.data_schema.audit.etag
            if returned_1_0:
                response.feature_view.audit.etag = returned_1_0
            returned_1_1 = response_1.result.reference_ids
            response.result.reference_ids.extend(returned_1_1)
            echoed_0 = request.feature_view_id
            response.feature_view.feature_view_id = echoed_0
            echoed_1 = request.feature_view.status
            response.feature_view.status = echoed_1
            return response

    async def handle_retry_feature_view_workflow(
        self,
        request: featurestore_v1_feature_view_workflow_service_pb2.RetryFeatureViewWorkflowRequest
    ) -> featurestore_v1_feature_view_workflow_service_pb2.RetryFeatureViewWorkflowResponse:
        """Retrys a feature view."""
        deps = self.deps
        response = featurestore_v1_feature_view_workflow_service_pb2.RetryFeatureViewWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('RetryFeatureViewWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'RetryFeatureViewWorkflow',
                {'reason': request.reason}
            )
            await deps.repository.save_feature_view(request.context.tenant_id, request.feature_view)
            response_0 = featurestore_v1_feature_view_lifecycle_service_pb2.GetFeatureViewLifecycleResponse()
            response_1 = featurestore_v1_feature_value_reporting_service_pb2.CountFeatureValueTotalsResponse()
            command_0 = FeatureViewWorkflowRetryFeatureViewWorkflow0Command(
                context=request.context,
                feature_view_id=request.feature_view_id
            )
            outgoing_0 = to_feature_view_workflow_retry_feature_view_workflow0_command(command_0)
            response_0 = await deps.clients.featurestore_feature_view_lifecycle.GetFeatureViewLifecycle(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            command_1 = FeatureViewWorkflowRetryFeatureViewWorkflow1Command.model_validate(
                {
                    'context': request.context,
                    'filter_region': response_0.feature_view.address.region,
                    'filter_created_after': response_0.feature_view.audit.created_at,
                    'filter_owner_id': request.feature_view.components.get(
                        'primary',
                        featurestore_v1_featurestore_pb2.FeatureViewComponent()
                    ).component_id
                }
            )
            outgoing_1 = to_feature_view_workflow_retry_feature_view_workflow1_command(command_1)
            response_1 = await deps.clients.featurestore_feature_value_reporting.CountFeatureValueTotals(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.feature_view.audit.updated_at
            if returned_0_0.ListFields():
                response.feature_view.audit.updated_at.MergeFrom(returned_0_0)
            returned_0_1 = response_0.result.message
            if returned_0_1:
                response.outcome.message = returned_0_1
            returned_1_0 = response_1.result.message
            if returned_1_0:
                response.outcome.message = returned_1_0
            echoed_0 = request.feature_view_id
            response.feature_view.feature_view_id = echoed_0
            echoed_1 = request.feature_view.name
            response.feature_view.name = echoed_1
            return response

    async def handle_signal_feature_view_workflow(
        self,
        request: featurestore_v1_feature_view_workflow_service_pb2.SignalFeatureViewWorkflowRequest
    ) -> featurestore_v1_feature_view_workflow_service_pb2.SignalFeatureViewWorkflowResponse:
        """Signals a feature view."""
        deps = self.deps
        response = featurestore_v1_feature_view_workflow_service_pb2.SignalFeatureViewWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SignalFeatureViewWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'SignalFeatureViewWorkflow',
                {'reason': request.reason}
            )
            await deps.repository.save_feature_view(request.context.tenant_id, request.feature_view)
            response_0 = featurestore_v1_entity_lifecycle_service_pb2.ScheduleEntityExpiryResponse()
            response_1 = featurestore_v1_feature_value_import_service_pb2.ValidateFeatureValueImportResponse()
            outgoing_0 = featurestore_v1_entity_lifecycle_service_pb2.ScheduleEntityExpiryRequest(
                context=request.context,
                entity=featurestore_v1_featurestore_pb2.Entity(
                    audit=common_v1_audit_pb2.AuditInfo(updated_by=request.feature_view.audit.updated_by),
                    contact=common_v1_contact_pb2.ContactInfo(
                        preferred_channel=request.details.notify.preferred_channel
                    ),
                    relationship_manager=identity_v1_refs_pb2.UserRef(user_id=request.feature_view.owner.user_id)
                )
            )
            outgoing_1 = featurestore_v1_feature_value_import_service_pb2.ValidateFeatureValueImportRequest(
                context=request.context,
                details=featurestore_v1_feature_value_import_service_pb2.ValidateFeatureValueImportRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(email=request.feature_view.owner.email)
                )
            )
            response_0, response_1 = await asyncio.gather(
                deps.clients.featurestore_entity_lifecycle.ScheduleEntityExpiry(
                    outgoing_0,
                    timeout=deps.settings.timeout
                ),
                deps.clients.featurestore_feature_value_import.ValidateFeatureValueImport(
                    outgoing_1,
                    timeout=deps.settings.timeout
                ),
            )
            returned_0_0 = response_0.outcome.status
            if returned_0_0:
                response.outcome.status = returned_0_0
            returned_0_1 = response_0.result.correlation_id
            if returned_0_1:
                response.result.correlation_id = returned_0_1
            returned_1_0 = response_1.outcome.message
            if returned_1_0:
                response.outcome.message = returned_1_0
            echoed_0 = request.feature_view_id
            response.feature_view.feature_view_id = echoed_0
            echoed_1 = request.feature_view.specs
            response.feature_view.specs.update(echoed_1)
            return response

    async def handle_start_feature_view_workflow(
        self,
        request: featurestore_v1_feature_view_workflow_service_pb2.StartFeatureViewWorkflowRequest
    ) -> featurestore_v1_feature_view_workflow_service_pb2.StartFeatureViewWorkflowResponse:
        """Starts a feature view."""
        deps = self.deps
        response = featurestore_v1_feature_view_workflow_service_pb2.StartFeatureViewWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('StartFeatureViewWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'StartFeatureViewWorkflow',
                {'reason': request.reason}
            )
            await deps.repository.save_feature_view(request.context.tenant_id, request.feature_view)
            response_0 = authorization_v1_access_policy_service_pb2.CreateAccessPolicyResponse()
            response_1 = featurestore_v1_feature_value_approval_service_pb2.RejectFeatureValueResponse()
            response_2 = search_v1_search_index_query_service_pb2.BrowseSearchIndexesResponse()
            response_3 = featurestore_v1_entity_sync_service_pb2.PushEntityResponse()
            outgoing_0 = authorization_v1_access_policy_service_pb2.CreateAccessPolicyRequest()
            outgoing_0.context.CopyFrom(request.context)
            outgoing_0.access_policy.audit.updated_at.CopyFrom(request.feature_view.audit.updated_at)
            outgoing_0.context.tenant_id = tenant_id.get()
            response_0 = await deps.clients.authorization_access_policy.CreateAccessPolicy(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = featurestore_v1_feature_value_approval_service_pb2.RejectFeatureValueRequest(
                context=request.context,
                details=featurestore_v1_feature_value_approval_service_pb2.RejectFeatureValueRequest.Details(
                    approver=identity_v1_refs_pb2.UserRef(display_name=request.feature_view.owner.display_name)
                ),
                feature_value=featurestore_v1_featurestore_pb2.FeatureValue(
                    measurements=[
                        featurestore_v1_featurestore_pb2.FeatureValueMeasurement(
                            unit=request.feature_view.dimensions.unit
                        )
                    ]
                )
            )
            port_1: FeatureViewWorkflowStartFeatureViewWorkflow1Port = FeatureViewWorkflowStartFeatureViewWorkflow1Adapter(
                deps.clients.featurestore_feature_value_approval,
                deps.settings.timeout
            )
            response_1 = await port_1.execute(outgoing_1)
            outgoing_2 = search_v1_search_index_query_service_pb2.BrowseSearchIndexesRequest(
                context=request.context,
                filter=search_v1_search_index_query_service_pb2.BrowseSearchIndexesRequest.Filter(
                    created_after=request.feature_view.audit.created_at,
                    labels=dict(response_1.feature_value.attributes),
                    owner_id=response_1.feature_value.subject.dataset_id,
                    region=request.feature_view.address.region
                )
            )
            steps_2 = [
                partial(
                    deps.clients.search_search_index_query.BrowseSearchIndexes,
                    outgoing_2,
                    timeout=deps.settings.timeout
                )
            ]
            results_2 = await run_steps(steps_2)
            response_2 = results_2[-1]
            outgoing_3 = featurestore_v1_entity_sync_service_pb2.PushEntityRequest(
                context=request.context,
                entity=featurestore_v1_featurestore_pb2.Entity(
                    primary_address=common_v1_address_pb2.PostalAddress(lines=list(request.feature_view.address.lines))
                )
            )
            response_3 = await FeatureViewWorkflowStartFeatureViewWorkflow3Adapter(
                deps.clients.featurestore_entity_sync,
                deps.settings.timeout
            )(outgoing_3)
            returned_0_0 = response_0.access_policy.audit.created_at
            if returned_0_0.ListFields():
                response.feature_view.audit.created_at.MergeFrom(returned_0_0)
            returned_1_0 = response_1.result.details
            response.result.details.update(returned_1_0)
            returned_2_0 = response_2.result.message
            if returned_2_0:
                response.outcome.message = returned_2_0
            returned_3_0 = response_3.result.message
            if returned_3_0:
                response.outcome.message = returned_3_0
            echoed_0 = request.feature_view_id
            response.feature_view.feature_view_id = echoed_0
            echoed_1 = request.feature_view.status
            response.feature_view.status = echoed_1
            return response
