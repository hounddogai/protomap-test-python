"""Reusable transport mixin for DataSchemaWorkflowService."""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any
from typing import cast
import asyncio
import logging

from google.protobuf.json_format import MessageToDict
from google.protobuf.json_format import ParseDict
import grpc

from acme.anomalies.v1 import (
    anomaly_feedback_workflow_service_pb2 as anomalies_v1_anomaly_feedback_workflow_service_pb2,
)
from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.customers.v1 import refs_pb2 as customers_v1_refs_pb2
from acme.datasets.v1 import data_schema_approval_service_pb2 as datasets_v1_data_schema_approval_service_pb2
from acme.datasets.v1 import data_schema_calculation_service_pb2 as datasets_v1_data_schema_calculation_service_pb2
from acme.datasets.v1 import data_schema_workflow_service_pb2 as datasets_v1_data_schema_workflow_service_pb2
from acme.datasets.v1 import dataset_approval_service_pb2 as datasets_v1_dataset_approval_service_pb2
from acme.datasets.v1 import (
    dataset_version_calculation_service_pb2 as datasets_v1_dataset_version_calculation_service_pb2,
)
from acme.datasets.v1 import dataset_version_workflow_service_pb2 as datasets_v1_dataset_version_workflow_service_pb2
from acme.datasets.v1 import dataset_workflow_service_pb2 as datasets_v1_dataset_workflow_service_pb2
from acme.datasets.v1 import datasets_pb2 as datasets_v1_datasets_pb2
from acme.featurestore.v1 import (
    feature_value_lifecycle_service_pb2 as featurestore_v1_feature_value_lifecycle_service_pb2,
)
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.lineage.v1 import lineage_edge_approval_service_pb2 as lineage_v1_lineage_edge_approval_service_pb2
from acme.lineage.v1 import lineage_edge_approval_service_pb2_grpc as lineage_v1_lineage_edge_approval_service_pb2_grpc
from acme.lineage.v1 import lineage_pb2 as lineage_v1_lineage_pb2
from acme.lineage.v1 import refs_pb2 as lineage_v1_refs_pb2
from acme.loyalty.v1 import loyalty_member_query_service_pb2 as loyalty_v1_loyalty_member_query_service_pb2
from acme.metrics.v1 import dashboard_sync_service_pb2 as metrics_v1_dashboard_sync_service_pb2
from acme.metrics.v1 import metric_series_history_service_pb2 as metrics_v1_metric_series_history_service_pb2
from acme.metrics.v1 import metrics_pb2 as metrics_v1_metrics_pb2

from acme_data.domains.datasets import hooks
from acme_data.domains.datasets.adapters import DataSchemaWorkflowStartDataSchemaWorkflow2Adapter
from acme_data.domains.datasets.adapters import DataSchemaWorkflowStartDataSchemaWorkflow2Port
from acme_data.domains.datasets.dependencies import Dependencies
from acme_data.domains.datasets.models import DataSchemaWorkflowRetryDataSchemaWorkflow0Command
from acme_data.domains.datasets.models import DataSchemaWorkflowRetryDataSchemaWorkflow1Command
from acme_data.domains.datasets.models import to_data_schema_workflow_retry_data_schema_workflow0_command
from acme_data.domains.datasets.models import to_data_schema_workflow_retry_data_schema_workflow1_command
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_id
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class DataSchemaWorkflowServicerHandlers:
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    async def AdvanceDataSchemaWorkflow(
        self, request: datasets_v1_data_schema_workflow_service_pb2.AdvanceDataSchemaWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> datasets_v1_data_schema_workflow_service_pb2.AdvanceDataSchemaWorkflowResponse:
        """Advances a data schema."""
        return await self.handle_advance_data_schema_workflow(request)

    @rpc_errors
    async def CancelDataSchemaWorkflow(
        self, request: datasets_v1_data_schema_workflow_service_pb2.CancelDataSchemaWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> datasets_v1_data_schema_workflow_service_pb2.CancelDataSchemaWorkflowResponse:
        """Cancels a data schema."""
        return await self.handle_cancel_data_schema_workflow(request)

    @rpc_errors
    @retry_transient
    async def InspectDataSchemaWorkflow(
        self, request: datasets_v1_data_schema_workflow_service_pb2.InspectDataSchemaWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> datasets_v1_data_schema_workflow_service_pb2.InspectDataSchemaWorkflowResponse:
        """Returns a data schema."""
        return await self.handle_inspect_data_schema_workflow(request)

    @rpc_errors
    async def ResumeDataSchemaWorkflow(
        self, request: datasets_v1_data_schema_workflow_service_pb2.ResumeDataSchemaWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> datasets_v1_data_schema_workflow_service_pb2.ResumeDataSchemaWorkflowResponse:
        """Resumes a data schema."""
        return await self.handle_resume_data_schema_workflow(request)

    @rpc_errors
    async def RetryDataSchemaWorkflow(
        self, request: datasets_v1_data_schema_workflow_service_pb2.RetryDataSchemaWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> datasets_v1_data_schema_workflow_service_pb2.RetryDataSchemaWorkflowResponse:
        """Retrys a data schema."""
        return await self.handle_retry_data_schema_workflow(request)

    @rpc_errors
    async def StartDataSchemaWorkflow(
        self, request: datasets_v1_data_schema_workflow_service_pb2.StartDataSchemaWorkflowRequest, context: grpc.aio.ServicerContext,
    ) -> datasets_v1_data_schema_workflow_service_pb2.StartDataSchemaWorkflowResponse:
        """Starts a data schema."""
        return await self.handle_start_data_schema_workflow(request)

    async def handle_advance_data_schema_workflow(
        self,
        request: datasets_v1_data_schema_workflow_service_pb2.AdvanceDataSchemaWorkflowRequest
    ) -> datasets_v1_data_schema_workflow_service_pb2.AdvanceDataSchemaWorkflowResponse:
        """Advances a data schema."""
        deps = self.deps
        response = datasets_v1_data_schema_workflow_service_pb2.AdvanceDataSchemaWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('AdvanceDataSchemaWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'AdvanceDataSchemaWorkflow',
                {'reason': request.reason}
            )
            await deps.repository.save_data_schema(request.context.tenant_id, request.data_schema)
            response_0 = datasets_v1_dataset_version_workflow_service_pb2.RetryDatasetVersionWorkflowResponse()
            response_1 = datasets_v1_dataset_version_calculation_service_pb2.CompareDatasetVersionOptionsResponse()
            outgoing_0 = datasets_v1_dataset_version_workflow_service_pb2.RetryDatasetVersionWorkflowRequest(
                context=request.context,
                dataset_version=datasets_v1_datasets_pb2.DatasetVersion(
                    attributes=dict(request.data_schema.attributes)
                ),
                details=datasets_v1_dataset_version_workflow_service_pb2.RetryDatasetVersionWorkflowRequest.Details(
                    notify=common_v1_contact_pb2.ContactInfo(
                        email=request.data_schema.manager.email,
                        name=request.details.notify.name,
                        preferred_channel=request.details.notify.preferred_channel
                    )
                )
            )
            response_0 = cast(datasets_v1_dataset_version_workflow_service_pb2.RetryDatasetVersionWorkflowResponse, await deps.bus.request(
                'acme.datasets.v1.DataSchemaWorkflowService/AdvanceDataSchemaWorkflow/0', outgoing_0, deps.settings.timeout,
            ))
            outgoing_1 = datasets_v1_dataset_version_calculation_service_pb2.CompareDatasetVersionOptionsRequest(
                context=request.context,
                details=datasets_v1_dataset_version_calculation_service_pb2.CompareDatasetVersionOptionsRequest.Details(
                    destination=common_v1_address_pb2.PostalAddress(
                        country_code=request.data_schema.location.country_code
                    )
                )
            )
            response_1 = await deps.clients.datasets_dataset_version_calculation.CompareDatasetVersionOptions(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.dataset_version.attributes
            returned_0_0_part_1 = response.data_schema.children.add()
            returned_0_0_part_2 = returned_0_0_part_1.children.add()
            returned_0_0_part_2.attributes.update(returned_0_0)
            returned_0_1 = response_0.result.status
            if returned_0_1:
                response.outcome.status = returned_0_1
            returned_1_0 = response_1.result.status
            if returned_1_0:
                response.result.status = returned_1_0
            echoed_0 = request.data_schema_id
            response.data_schema.data_schema_id = echoed_0
            echoed_1 = request.data_schema.manager
            response.data_schema.manager.CopyFrom(echoed_1)
            return response

    async def handle_cancel_data_schema_workflow(
        self,
        request: datasets_v1_data_schema_workflow_service_pb2.CancelDataSchemaWorkflowRequest
    ) -> datasets_v1_data_schema_workflow_service_pb2.CancelDataSchemaWorkflowResponse:
        """Cancels a data schema."""
        deps = self.deps
        response = datasets_v1_data_schema_workflow_service_pb2.CancelDataSchemaWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CancelDataSchemaWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'CancelDataSchemaWorkflow',
                {'reason': request.reason}
            )
            await deps.repository.save_data_schema(request.context.tenant_id, request.data_schema)
            response_0 = datasets_v1_dataset_version_workflow_service_pb2.AdvanceDatasetVersionWorkflowResponse()
            response_1 = loyalty_v1_loyalty_member_query_service_pb2.FindLoyaltyMembersResponse()
            response_2 = metrics_v1_dashboard_sync_service_pb2.PullDashboardsResponse()
            outgoing_0 = datasets_v1_dataset_version_workflow_service_pb2.AdvanceDatasetVersionWorkflowRequest(
                context=request.context,
                dataset_version=datasets_v1_datasets_pb2.DatasetVersion(
                    subject=customers_v1_refs_pb2.CustomerRef(email=request.details.notify.email)
                )
            )
            method_name_0 = 'AdvanceDatasetVersionWorkflow'
            response_0 = await getattr(
                deps.clients.datasets_dataset_version_workflow,
                method_name_0
            )(outgoing_0, timeout=deps.settings.timeout)
            fields_1: dict[str, Any] = {
                'context': request.context,
                'filter': {
                    'created_after': response_0.dataset_version.occurred_at,
                    'owner_id': request.data_schema.manager.user_id,
                    'region': request.data_schema.location.region
                }
            }
            outgoing_1 = loyalty_v1_loyalty_member_query_service_pb2.FindLoyaltyMembersRequest(**fields_1)
            response_1 = await deps.clients.loyalty_loyalty_member_query.FindLoyaltyMembers(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = metrics_v1_dashboard_sync_service_pb2.PullDashboardsRequest(
                context=request.context,
                dashboard=metrics_v1_metrics_pb2.Dashboard(
                    audit=common_v1_audit_pb2.AuditInfo(
                        updated_at=request.data_schema.audit.updated_at,
                        updated_by=request.data_schema.audit.updated_by
                    )
                )
            )
            document_2 = MessageToDict(outgoing_2, preserving_proto_field_name=True)
            outgoing_2 = ParseDict(document_2, metrics_v1_dashboard_sync_service_pb2.PullDashboardsRequest())
            response_2 = await deps.clients.metrics_dashboard_sync.PullDashboards(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.outcome.status
            if returned_0_0:
                response.outcome.status = returned_0_0
            returned_0_1 = response_0.outcome.effective_at
            if returned_0_1.ListFields():
                response.outcome.effective_at.MergeFrom(returned_0_1)
            returned_1_0 = response_1.result.message
            if returned_1_0:
                response.result.message = returned_1_0
            returned_2_0 = response_2.dashboard.billing_address.recipient
            if returned_2_0:
                response.data_schema.location.recipient = returned_2_0
            echoed_0 = request.data_schema_id
            response.data_schema.data_schema_id = echoed_0
            echoed_1 = request.data_schema.depth
            response.data_schema.depth = echoed_1
            return response

    async def handle_inspect_data_schema_workflow(
        self,
        request: datasets_v1_data_schema_workflow_service_pb2.InspectDataSchemaWorkflowRequest
    ) -> datasets_v1_data_schema_workflow_service_pb2.InspectDataSchemaWorkflowResponse:
        """Returns a data schema."""
        deps = self.deps
        response = datasets_v1_data_schema_workflow_service_pb2.InspectDataSchemaWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('InspectDataSchemaWorkflow', extra={'fields': {'locale': request.context.locale}})
            await deps.repository.audit(
                request.context.tenant_id,
                'InspectDataSchemaWorkflow',
                {'locale': request.context.locale}
            )
            echoed_0 = request.data_schema_id
            response.data_schema.data_schema_id = echoed_0
            return response

    async def handle_resume_data_schema_workflow(
        self,
        request: datasets_v1_data_schema_workflow_service_pb2.ResumeDataSchemaWorkflowRequest
    ) -> datasets_v1_data_schema_workflow_service_pb2.ResumeDataSchemaWorkflowResponse:
        """Resumes a data schema."""
        deps = self.deps
        response = datasets_v1_data_schema_workflow_service_pb2.ResumeDataSchemaWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ResumeDataSchemaWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ResumeDataSchemaWorkflow',
                {'reason': request.reason}
            )
            await deps.repository.save_data_schema(request.context.tenant_id, request.data_schema)
            response_0 = featurestore_v1_feature_value_lifecycle_service_pb2.ScheduleFeatureValueExpiryResponse()
            response_1 = datasets_v1_dataset_workflow_service_pb2.StartDatasetWorkflowResponse()
            response_2 = metrics_v1_metric_series_history_service_pb2.CompareMetricSeriesVersionsResponse()
            response_3 = lineage_v1_lineage_edge_approval_service_pb2.DelegateLineageEdgeApprovalResponse()
            outgoing_0 = featurestore_v1_feature_value_lifecycle_service_pb2.ScheduleFeatureValueExpiryRequest(
                context=request.context,
                details=featurestore_v1_feature_value_lifecycle_service_pb2.ScheduleFeatureValueExpiryRequest.Details(
                    notify=common_v1_contact_pb2.ContactInfo(phone=request.details.notify.phone)
                )
            )
            outgoing_1 = datasets_v1_dataset_workflow_service_pb2.StartDatasetWorkflowRequest(
                context=request.context,
                dataset=datasets_v1_datasets_pb2.Dataset(
                    address=common_v1_address_pb2.PostalAddress(locality=request.data_schema.location.locality)
                )
            )
            outgoing_2 = metrics_v1_metric_series_history_service_pb2.CompareMetricSeriesVersionsRequest(
                context=request.context,
                metric_series=metrics_v1_metrics_pb2.MetricSeries(
                    address=common_v1_address_pb2.PostalAddress(recipient=request.data_schema.location.recipient),
                    audit=common_v1_audit_pb2.AuditInfo(created_by=request.data_schema.audit.created_by)
                )
            )
            response_0, response_1, response_2 = await asyncio.gather(
                deps.clients.featurestore_feature_value_lifecycle.ScheduleFeatureValueExpiry(
                    outgoing_0,
                    timeout=deps.settings.timeout
                ),
                deps.clients.datasets_dataset_workflow.StartDatasetWorkflow(outgoing_1, timeout=deps.settings.timeout),
                deps.clients.metrics_metric_series_history.CompareMetricSeriesVersions(
                    outgoing_2,
                    timeout=deps.settings.timeout
                ),
            )
            outgoing_3 = lineage_v1_lineage_edge_approval_service_pb2.DelegateLineageEdgeApprovalRequest(
                context=request.context,
                details=lineage_v1_lineage_edge_approval_service_pb2.DelegateLineageEdgeApprovalRequest.Details(
                    approver=identity_v1_refs_pb2.UserRef(
                        display_name=response_1.dataset.owner.display_name,
                        email=response_2.metric_series.owner.email,
                        user_id=request.data_schema.manager.user_id
                    )
                ),
                lineage_edge=lineage_v1_lineage_pb2.LineageEdge(
                    subject=lineage_v1_refs_pb2.ImpactRef(display_name=request.data_schema.manager.display_name)
                )
            )
            registered_3 = cast(
                lineage_v1_lineage_edge_approval_service_pb2_grpc.LineageEdgeApprovalServiceStub,
                deps.clients.registry['acme.lineage.v1.LineageEdgeApprovalService']
            )
            response_3 = await registered_3.DelegateLineageEdgeApproval(outgoing_3, timeout=deps.settings.timeout)
            returned_0_0 = response_0.outcome.message
            if returned_0_0:
                response.outcome.message = returned_0_0
            returned_1_0 = response_1.dataset.name
            returned_1_0_part_1 = response.data_schema.children.add()
            if returned_1_0:
                returned_1_0_part_1.name = returned_1_0
            returned_1_1 = response_1.dataset.address.region
            returned_1_1_part_1 = response.data_schema.children.add()
            if returned_1_1:
                returned_1_1_part_1.location.region = returned_1_1
            returned_2_0 = response_2.metric_series.name
            returned_2_0_part_1 = response.data_schema.children.add()
            returned_2_0_part_2 = returned_2_0_part_1.children.add()
            returned_2_0_part_3 = returned_2_0_part_2.children.add()
            if returned_2_0:
                returned_2_0_part_3.name = returned_2_0
            returned_3_0 = response_3.result.message
            if returned_3_0:
                response.outcome.message = returned_3_0
            echoed_0 = request.data_schema_id
            response.data_schema.data_schema_id = echoed_0
            echoed_1 = request.data_schema.attributes
            response.data_schema.attributes.update(echoed_1)
            return response

    async def handle_retry_data_schema_workflow(
        self,
        request: datasets_v1_data_schema_workflow_service_pb2.RetryDataSchemaWorkflowRequest
    ) -> datasets_v1_data_schema_workflow_service_pb2.RetryDataSchemaWorkflowResponse:
        """Retrys a data schema."""
        deps = self.deps
        response = datasets_v1_data_schema_workflow_service_pb2.RetryDataSchemaWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('RetryDataSchemaWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'RetryDataSchemaWorkflow',
                {'reason': request.reason}
            )
            await deps.repository.save_data_schema(request.context.tenant_id, request.data_schema)
            response_0 = datasets_v1_dataset_approval_service_pb2.SubmitDatasetResponse()
            response_1 = datasets_v1_dataset_workflow_service_pb2.CancelDatasetWorkflowResponse()
            response_2 = datasets_v1_dataset_approval_service_pb2.ListPendingDatasetsResponse()
            command_0 = DataSchemaWorkflowRetryDataSchemaWorkflow0Command(
                context=request.context,
                details_approver_display_name=request.data_schema.manager.display_name,
                dataset_audit_updated_by=request.data_schema.audit.updated_by,
                dataset_audit_created_at=request.data_schema.audit.created_at,
                dataset_owner_email=request.data_schema.manager.email
            )
            outgoing_0 = to_data_schema_workflow_retry_data_schema_workflow0_command(command_0)
            response_0 = await deps.clients.datasets_dataset_approval.SubmitDataset(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            command_1 = DataSchemaWorkflowRetryDataSchemaWorkflow1Command.model_validate(
                {
                    'context': request.context,
                    'dataset_audit_created_at': response_0.dataset.audit.created_at,
                    'dataset_components_quantity': response_0.dataset.components.get(
                        'primary',
                        datasets_v1_datasets_pb2.DatasetComponent()
                    ).quantity,
                    'dataset_audit_updated_at': request.data_schema.audit.updated_at
                }
            )
            outgoing_1 = to_data_schema_workflow_retry_data_schema_workflow1_command(command_1)
            response_1 = await deps.clients.datasets_dataset_workflow.CancelDatasetWorkflow(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = datasets_v1_dataset_approval_service_pb2.ListPendingDatasetsRequest()
            outgoing_2.context.CopyFrom(request.context)
            if response_0.dataset.WhichOneof('locator') == 'address':
                outgoing_2.filter.region = response_0.dataset.address.region
            outgoing_2.filter.created_after.CopyFrom(request.data_schema.audit.created_at)
            outgoing_2.filter.owner_id = response_1.dataset.components.get(
                'primary',
                datasets_v1_datasets_pb2.DatasetComponent()
            ).component_id
            outgoing_2.filter.labels.update(dict(response_1.dataset.specs))
            response_2 = await deps.clients.datasets_dataset_approval.ListPendingDatasets(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_0)
            returned_1_0 = response_1.dataset.address.recipient
            returned_1_0_part_1 = response.data_schema.children.add()
            if returned_1_0:
                returned_1_0_part_1.location.recipient = returned_1_0
            returned_2_0 = response_2.result.details
            response.result.details.update(returned_2_0)
            returned_2_1 = response_2.result.reference_ids
            response.result.reference_ids.extend(returned_2_1)
            echoed_0 = request.data_schema_id
            response.data_schema.data_schema_id = echoed_0
            echoed_1 = request.data_schema.location
            response.data_schema.location.CopyFrom(echoed_1)
            return response

    async def handle_start_data_schema_workflow(
        self,
        request: datasets_v1_data_schema_workflow_service_pb2.StartDataSchemaWorkflowRequest
    ) -> datasets_v1_data_schema_workflow_service_pb2.StartDataSchemaWorkflowResponse:
        """Starts a data schema."""
        deps = self.deps
        response = datasets_v1_data_schema_workflow_service_pb2.StartDataSchemaWorkflowResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('StartDataSchemaWorkflow', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'StartDataSchemaWorkflow',
                {'reason': request.reason}
            )
            await deps.repository.save_data_schema(request.context.tenant_id, request.data_schema)
            response_0 = anomalies_v1_anomaly_feedback_workflow_service_pb2.AdvanceAnomalyFeedbackWorkflowResponse()
            response_1 = datasets_v1_data_schema_calculation_service_pb2.RecalculateDataSchemasResponse()
            response_2 = datasets_v1_data_schema_approval_service_pb2.RecallDataSchemaResponse()
            outgoing_0 = anomalies_v1_anomaly_feedback_workflow_service_pb2.AdvanceAnomalyFeedbackWorkflowRequest(
                context=request.context,
                details=anomalies_v1_anomaly_feedback_workflow_service_pb2.AdvanceAnomalyFeedbackWorkflowRequest.Details(
                    notify=common_v1_contact_pb2.ContactInfo(email=request.data_schema.manager.email)
                )
            )
            response_0 = await hooks.data_schema_workflow_start_data_schema_workflow0(
                deps.clients.anomalies_anomaly_feedback_workflow,
                outgoing_0,
                deps.settings.timeout
            )
            outgoing_1 = datasets_v1_data_schema_calculation_service_pb2.RecalculateDataSchemasRequest()
            outgoing_1.context.CopyFrom(request.context)
            field_1_1_part_1 = outgoing_1.data_schema.children.add()
            field_1_1_part_2 = field_1_1_part_1.children.add()
            field_1_1_part_2.audit.created_at.CopyFrom(request.data_schema.audit.created_at)
            field_1_2_part_1 = outgoing_1.data_schema.children.add()
            field_1_2_part_2 = field_1_2_part_1.children.add()
            field_1_2_part_2.audit.etag = request.data_schema.audit.etag
            outgoing_1.context.tenant_id = tenant_id.get()
            response_1 = await deps.clients.datasets_data_schema_calculation.RecalculateDataSchemas(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = datasets_v1_data_schema_approval_service_pb2.RecallDataSchemaRequest(
                context=request.context,
                data_schema=datasets_v1_datasets_pb2.DataSchema(
                    children=[
                        datasets_v1_datasets_pb2.DataSchema(
                            children=[
                                datasets_v1_datasets_pb2.DataSchema(
                                    location=common_v1_address_pb2.PostalAddress(
                                        recipient=request.data_schema.location.recipient
                                    ),
                                    manager=identity_v1_refs_pb2.UserRef(email=response_1.data_schema.manager.email)
                                )
                            ]
                        )
                    ]
                )
            )
            port_2: DataSchemaWorkflowStartDataSchemaWorkflow2Port = DataSchemaWorkflowStartDataSchemaWorkflow2Adapter(
                deps.clients.datasets_data_schema_approval,
                deps.settings.timeout
            )
            response_2 = await port_2.execute(outgoing_2)
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.outcome.message = returned_0_0
            returned_1_0 = response_1.data_schema.location.lines
            response.data_schema.location.lines.extend(returned_1_0)
            returned_2_0 = response_2.data_schema.manager
            returned_2_0_part_1 = response.data_schema.children.add()
            returned_2_0_part_2 = returned_2_0_part_1.children.add()
            if returned_2_0.ListFields():
                returned_2_0_part_2.manager.MergeFrom(returned_2_0)
            echoed_0 = request.data_schema_id
            response.data_schema.data_schema_id = echoed_0
            echoed_1 = request.data_schema.parent_id
            response.data_schema.parent_id = echoed_1
            return response
