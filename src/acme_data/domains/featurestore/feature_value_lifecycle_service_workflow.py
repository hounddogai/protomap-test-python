"""Application workflow for FeatureValue Lifecycle."""

from __future__ import annotations

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

from acme.anomalies.v1 import anomalies_pb2 as anomalies_v1_anomalies_pb2
from acme.anomalies.v1 import anomaly_workflow_service_pb2 as anomalies_v1_anomaly_workflow_service_pb2
from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.customers.v1 import refs_pb2 as customers_v1_refs_pb2
from acme.datasets.v1 import data_schema_validation_service_pb2 as datasets_v1_data_schema_validation_service_pb2
from acme.datasets.v1 import (
    dataset_version_calculation_service_pb2 as datasets_v1_dataset_version_calculation_service_pb2,
)
from acme.datasets.v1 import (
    dataset_version_calculation_service_pb2_grpc as datasets_v1_dataset_version_calculation_service_pb2_grpc,
)
from acme.datasets.v1 import (
    dataset_version_validation_service_pb2 as datasets_v1_dataset_version_validation_service_pb2,
)
from acme.datasets.v1 import datasets_pb2 as datasets_v1_datasets_pb2
from acme.featurestore.v1 import entity_reporting_service_pb2 as featurestore_v1_entity_reporting_service_pb2
from acme.featurestore.v1 import entity_sync_service_pb2 as featurestore_v1_entity_sync_service_pb2
from acme.featurestore.v1 import feature_value_import_service_pb2 as featurestore_v1_feature_value_import_service_pb2
from acme.featurestore.v1 import (
    feature_value_lifecycle_service_pb2 as featurestore_v1_feature_value_lifecycle_service_pb2,
)
from acme.featurestore.v1 import feature_value_query_service_pb2 as featurestore_v1_feature_value_query_service_pb2
from acme.featurestore.v1 import feature_value_sync_service_pb2 as featurestore_v1_feature_value_sync_service_pb2
from acme.featurestore.v1 import feature_view_sync_service_pb2 as featurestore_v1_feature_view_sync_service_pb2
from acme.featurestore.v1 import featurestore_pb2 as featurestore_v1_featurestore_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.lineage.v1 import lineage_edge_sync_service_pb2 as lineage_v1_lineage_edge_sync_service_pb2
from acme.lineage.v1 import lineage_edge_workflow_service_pb2 as lineage_v1_lineage_edge_workflow_service_pb2
from acme.lineage.v1 import lineage_node_workflow_service_pb2 as lineage_v1_lineage_node_workflow_service_pb2
from acme.lineage.v1 import lineage_pb2 as lineage_v1_lineage_pb2
from acme.lineage.v1 import refs_pb2 as lineage_v1_refs_pb2
from acme.metrics.v1 import dashboard_notification_service_pb2 as metrics_v1_dashboard_notification_service_pb2

from acme_data.domains.featurestore import hooks
from acme_data.domains.featurestore.dependencies import Dependencies
from acme_data.domains.featurestore.models import FeatureValueLifecycleReinstateFeatureValue0Command
from acme_data.domains.featurestore.models import to_feature_value_lifecycle_reinstate_feature_value0_command
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import run_steps
from acme_data.platform.tenancy import tenant_id
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class FeatureValueLifecycleServicerWorkflow:
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    async def handle_activate_feature_value(
        self,
        request: featurestore_v1_feature_value_lifecycle_service_pb2.ActivateFeatureValueRequest
    ) -> featurestore_v1_feature_value_lifecycle_service_pb2.ActivateFeatureValueResponse:
        """Activates a feature value."""
        deps = self.deps
        response = featurestore_v1_feature_value_lifecycle_service_pb2.ActivateFeatureValueResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ActivateFeatureValue', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'ActivateFeatureValue', {'reason': request.reason})
            response_0 = featurestore_v1_feature_value_sync_service_pb2.ListFeatureValueConflictsResponse()
            response_1 = anomalies_v1_anomaly_workflow_service_pb2.SignalAnomalyWorkflowResponse()
            outgoing_0 = featurestore_v1_feature_value_sync_service_pb2.ListFeatureValueConflictsRequest(
                context=request.context,
                filter=featurestore_v1_feature_value_sync_service_pb2.ListFeatureValueConflictsRequest.Filter(
                    created_after=request.details.effective_at,
                    labels=dict(request.annotations),
                    owner_id=request.details.new_owner.user_id
                )
            )
            document_0 = MessageToDict(outgoing_0, preserving_proto_field_name=True)
            outgoing_0 = ParseDict(
                document_0,
                featurestore_v1_feature_value_sync_service_pb2.ListFeatureValueConflictsRequest()
            )
            response_0 = await deps.clients.featurestore_feature_value_sync.ListFeatureValueConflicts(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = anomalies_v1_anomaly_workflow_service_pb2.SignalAnomalyWorkflowRequest(
                anomaly=anomalies_v1_anomalies_pb2.Anomaly(
                    assignee=identity_v1_refs_pb2.UserRef(email=request.details.new_owner.email)
                ),
                context=request.context,
                details=anomalies_v1_anomaly_workflow_service_pb2.SignalAnomalyWorkflowRequest.Details(
                    notify=common_v1_contact_pb2.ContactInfo(
                        email=request.details.notify_contact.email,
                        name=request.details.notify_contact.name
                    )
                )
            )
            document_1 = MessageToJson(outgoing_1, preserving_proto_field_name=True)
            outgoing_1 = Parse(document_1, anomalies_v1_anomaly_workflow_service_pb2.SignalAnomalyWorkflowRequest())
            response_1 = await deps.clients.anomalies_anomaly_workflow.SignalAnomalyWorkflow(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.correlation_id
            if returned_0_0:
                response.feature_value.correlation_id = returned_0_0
            returned_1_0 = response_1.result.message
            if returned_1_0:
                response.result.message = returned_1_0
            echoed_0 = request.feature_value_id
            response.feature_value.feature_value_id = echoed_0
            echoed_1 = request.details.effective_at
            response.outcome.effective_at.CopyFrom(echoed_1)
            return response

    async def handle_expire_feature_value(
        self,
        request: featurestore_v1_feature_value_lifecycle_service_pb2.ExpireFeatureValueRequest
    ) -> featurestore_v1_feature_value_lifecycle_service_pb2.ExpireFeatureValueResponse:
        """Expires a feature value."""
        deps = self.deps
        response = featurestore_v1_feature_value_lifecycle_service_pb2.ExpireFeatureValueResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ExpireFeatureValue', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'ExpireFeatureValue', {'reason': request.reason})
            response_0 = datasets_v1_dataset_version_validation_service_pb2.ValidateDatasetVersionResponse()
            outgoing_0 = datasets_v1_dataset_version_validation_service_pb2.ValidateDatasetVersionRequest()
            outgoing_0.context.CopyFrom(request.context)
            outgoing_0.details.contact.email = request.details.notify_contact.email
            merged_0 = datasets_v1_dataset_version_validation_service_pb2.ValidateDatasetVersionRequest()
            merged_0.MergeFrom(outgoing_0)
            outgoing_0.CopyFrom(merged_0)
            response_0 = await deps.clients.datasets_dataset_version_validation.ValidateDatasetVersion(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.outcome.next_steps
            response.outcome.next_steps.extend(returned_0_0)
            echoed_0 = request.feature_value_id
            response.feature_value.feature_value_id = echoed_0
            echoed_1 = request.details.effective_at
            response.outcome.effective_at.CopyFrom(echoed_1)
            return response

    async def handle_get_feature_value_lifecycle(
        self,
        request: featurestore_v1_feature_value_lifecycle_service_pb2.GetFeatureValueLifecycleRequest
    ) -> featurestore_v1_feature_value_lifecycle_service_pb2.GetFeatureValueLifecycleResponse:
        """Returns a feature value."""
        deps = self.deps
        response = featurestore_v1_feature_value_lifecycle_service_pb2.GetFeatureValueLifecycleResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('GetFeatureValueLifecycle', extra={'fields': {'domain': 'featurestore'}})
            await deps.repository.audit(request.context.tenant_id, 'GetFeatureValueLifecycle', {})
            response_0 = lineage_v1_lineage_node_workflow_service_pb2.StartLineageNodeWorkflowResponse()
            response_1 = datasets_v1_dataset_version_calculation_service_pb2.SimulateDatasetVersionResponse()
            outgoing_0 = lineage_v1_lineage_node_workflow_service_pb2.StartLineageNodeWorkflowRequest(
                context=request.context,
                lineage_node=lineage_v1_lineage_pb2.LineageNode(
                    children=[
                        lineage_v1_lineage_pb2.LineageNode(
                            children=[
                                lineage_v1_lineage_pb2.LineageNode(
                                    audit=common_v1_audit_pb2.AuditInfo(created_at=request.context.deadline),
                                    children=[lineage_v1_lineage_pb2.LineageNode(parent_id=request.feature_value_id)],
                                    manager=identity_v1_refs_pb2.UserRef(user_id=request.context.actor.user_id)
                                )
                            ],
                            manager=identity_v1_refs_pb2.UserRef(email=request.context.actor.email)
                        )
                    ]
                )
            )
            response_0 = await deps.clients.lineage_lineage_node_workflow.StartLineageNodeWorkflow(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = datasets_v1_dataset_version_calculation_service_pb2.SimulateDatasetVersionRequest(
                context=request.context,
                dataset_version=datasets_v1_datasets_pb2.DatasetVersion(
                    subject=customers_v1_refs_pb2.CustomerRef(display_name=response_0.lineage_node.manager.display_name)
                ),
                details=datasets_v1_dataset_version_calculation_service_pb2.SimulateDatasetVersionRequest.Details(
                    destination=common_v1_address_pb2.PostalAddress(
                        lines=list(response_0.lineage_node.location.lines),
                        locality=response_0.lineage_node.location.locality,
                        recipient=response_0.lineage_node.location.recipient
                    )
                )
            )
            registered_1 = cast(
                datasets_v1_dataset_version_calculation_service_pb2_grpc.DatasetVersionCalculationServiceStub,
                deps.clients.registry['acme.datasets.v1.DatasetVersionCalculationService']
            )
            response_1 = await registered_1.SimulateDatasetVersion(outgoing_1, timeout=deps.settings.timeout)
            returned_0_0 = response_0.result.correlation_id
            if returned_0_0:
                response.feature_value.correlation_id = returned_0_0
            returned_0_1 = response_0.outcome.status
            if returned_0_1:
                response.result.status = returned_0_1
            returned_1_0 = response_1.dataset_version.sequence
            if returned_1_0:
                response.feature_value.sequence = returned_1_0
            echoed_0 = request.feature_value_id
            response.feature_value.feature_value_id = echoed_0
            return response

    async def handle_reinstate_feature_value(
        self,
        request: featurestore_v1_feature_value_lifecycle_service_pb2.ReinstateFeatureValueRequest
    ) -> featurestore_v1_feature_value_lifecycle_service_pb2.ReinstateFeatureValueResponse:
        """Reinstates a feature value."""
        deps = self.deps
        response = featurestore_v1_feature_value_lifecycle_service_pb2.ReinstateFeatureValueResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ReinstateFeatureValue', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'ReinstateFeatureValue', {'reason': request.reason})
            response_0 = featurestore_v1_feature_value_import_service_pb2.ListFeatureValueImportsResponse()
            response_1 = featurestore_v1_feature_value_query_service_pb2.ExportFeatureValuesResponse()
            command_0 = FeatureValueLifecycleReinstateFeatureValue0Command(
                context=request.context,
                filter_created_after=request.details.effective_at,
                filter_owner_id=request.details.new_owner.user_id,
                filter_labels=dict(request.annotations)
            )
            outgoing_0 = to_feature_value_lifecycle_reinstate_feature_value0_command(command_0)
            response_0 = await deps.clients.featurestore_feature_value_import.ListFeatureValueImports(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = featurestore_v1_feature_value_query_service_pb2.ExportFeatureValuesRequest(
                context=request.context,
                filter=featurestore_v1_feature_value_query_service_pb2.ExportFeatureValuesRequest.Filter(
                    created_after=request.details.effective_at,
                    labels=dict(response_0.result.details),
                    owner_id=request.details.new_owner.user_id
                )
            )
            async for chunk_1 in deps.clients.featurestore_feature_value_query.ExportFeatureValues(
                outgoing_1,
                timeout=deps.settings.timeout
            ):
                response_1 = chunk_1
            returned_0_0 = response_0.result.details
            response.result.details.update(returned_0_0)
            returned_0_1 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_1)
            echoed_0 = request.feature_value_id
            response.feature_value.feature_value_id = echoed_0
            echoed_1 = request.details.effective_at
            response.outcome.effective_at.CopyFrom(echoed_1)
            return response

    async def handle_renew_feature_value(
        self,
        request: featurestore_v1_feature_value_lifecycle_service_pb2.RenewFeatureValueRequest
    ) -> featurestore_v1_feature_value_lifecycle_service_pb2.RenewFeatureValueResponse:
        """Renews a feature value."""
        deps = self.deps
        response = featurestore_v1_feature_value_lifecycle_service_pb2.RenewFeatureValueResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('RenewFeatureValue', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'RenewFeatureValue', {'reason': request.reason})
            response_0 = featurestore_v1_feature_view_sync_service_pb2.SyncFeatureViewsResponse()
            response_1 = lineage_v1_lineage_edge_sync_service_pb2.ResolveLineageEdgeConflictResponse()
            response_2 = datasets_v1_data_schema_validation_service_pb2.ExplainDataSchemaDecisionResponse()
            outgoing_0 = featurestore_v1_feature_view_sync_service_pb2.SyncFeatureViewsRequest(
                context=request.context,
                feature_view=featurestore_v1_featurestore_pb2.FeatureView(
                    owner=identity_v1_refs_pb2.UserRef(
                        email=request.details.new_owner.email,
                        user_id=request.details.new_owner.user_id
                    )
                )
            )
            send_0 = partial(
                deps.clients.featurestore_feature_view_sync.SyncFeatureViews,
                timeout=deps.settings.timeout
            )
            response_0 = await send_0(outgoing_0)
            outgoing_1 = lineage_v1_lineage_edge_sync_service_pb2.ResolveLineageEdgeConflictRequest(
                annotations=dict(request.annotations),
                context=request.context,
                lineage_edge=lineage_v1_lineage_pb2.LineageEdge(
                    correlation_id=response_0.result.correlation_id,
                    measurements=[
                        lineage_v1_lineage_pb2.LineageEdgeMeasurement(unit=response_0.feature_view.dimensions.unit)
                    ],
                    subject=lineage_v1_refs_pb2.ImpactRef(display_name=response_0.feature_view.owner.display_name)
                )
            )
            response_1 = await hooks.feature_value_lifecycle_renew_feature_value1(
                deps.clients.lineage_lineage_edge_sync,
                outgoing_1,
                deps.settings.timeout
            )
            outgoing_2 = datasets_v1_data_schema_validation_service_pb2.ExplainDataSchemaDecisionRequest()
            outgoing_2.context.CopyFrom(request.context)
            field_2_1_part_1 = outgoing_2.data_schema.children.add()
            field_2_1_part_2 = field_2_1_part_1.children.add()
            field_2_1_part_2.manager.display_name = request.details.new_owner.display_name
            field_2_2_part_1 = outgoing_2.data_schema.children.add()
            field_2_2_part_2 = field_2_2_part_1.children.add()
            field_2_2_part_2.manager.email = response_0.feature_view.owner.email
            field_2_3_part_1 = outgoing_2.data_schema.children.add()
            field_2_3_part_2 = field_2_3_part_1.children.add()
            field_2_3_part_3 = field_2_3_part_2.children.add()
            field_2_3_part_3.attributes.update(dict(response_1.lineage_edge.attributes))
            outgoing_2.context.tenant_id = tenant_id.get()
            response_2 = await deps.clients.datasets_data_schema_validation.ExplainDataSchemaDecision(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.outcome.reference_id
            if returned_0_0:
                response.outcome.reference_id = returned_0_0
            returned_1_0 = response_1.lineage_edge.sequence
            if returned_1_0:
                response.feature_value.sequence = returned_1_0
            returned_1_1 = response_1.result.message
            if returned_1_1:
                response.result.message = returned_1_1
            returned_2_0 = response_2.data_schema.manager.display_name
            if returned_2_0:
                response.feature_value.subject.display_name = returned_2_0
            echoed_0 = request.feature_value_id
            response.feature_value.feature_value_id = echoed_0
            echoed_1 = request.details.effective_at
            response.outcome.effective_at.CopyFrom(echoed_1)
            return response

    async def handle_schedule_feature_value_expiry(
        self,
        request: featurestore_v1_feature_value_lifecycle_service_pb2.ScheduleFeatureValueExpiryRequest
    ) -> featurestore_v1_feature_value_lifecycle_service_pb2.ScheduleFeatureValueExpiryResponse:
        """Schedules a feature value."""
        deps = self.deps
        response = featurestore_v1_feature_value_lifecycle_service_pb2.ScheduleFeatureValueExpiryResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ScheduleFeatureValueExpiry', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ScheduleFeatureValueExpiry',
                {'reason': request.reason}
            )
            await deps.repository.save_feature_value(request.context.tenant_id, request.feature_value)
            response_0 = featurestore_v1_entity_sync_service_pb2.SyncEntitiesResponse()
            for item_0 in request.feature_value.measurements:
                outgoing_0 = featurestore_v1_entity_sync_service_pb2.SyncEntitiesRequest(
                    context=request.context,
                    entity=featurestore_v1_featurestore_pb2.Entity(
                        audit=common_v1_audit_pb2.AuditInfo(updated_at=item_0.observed_at),
                        name=request.details.notify.name
                    )
                )
                response_0 = await deps.clients.featurestore_entity_sync.SyncEntities(
                    outgoing_0,
                    timeout=deps.settings.timeout
                )
            echoed_0 = request.feature_value_id
            response.feature_value.feature_value_id = echoed_0
            echoed_1 = request.feature_value.source
            response.feature_value.source = echoed_1
            return response

    async def handle_suspend_feature_value(
        self,
        request: featurestore_v1_feature_value_lifecycle_service_pb2.SuspendFeatureValueRequest
    ) -> featurestore_v1_feature_value_lifecycle_service_pb2.SuspendFeatureValueResponse:
        """Suspends a feature value."""
        deps = self.deps
        response = featurestore_v1_feature_value_lifecycle_service_pb2.SuspendFeatureValueResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SuspendFeatureValue', extra={'fields': {'reason_code': request.details.reason_code}})
            await deps.repository.audit(
                request.context.tenant_id,
                'SuspendFeatureValue',
                {'reason_code': request.details.reason_code}
            )
            response_0 = featurestore_v1_entity_reporting_service_pb2.GenerateEntityReportResponse()
            outgoing_0 = featurestore_v1_entity_reporting_service_pb2.GenerateEntityReportRequest(
                context=request.context,
                reason=request.reason
            )
            steps_0 = [
                partial(
                    deps.clients.featurestore_entity_reporting.GenerateEntityReport,
                    outgoing_0,
                    timeout=deps.settings.timeout
                )
            ]
            results_0 = await run_steps(steps_0)
            response_0 = results_0[-1]
            returned_0_0 = response_0.result.correlation_id
            if returned_0_0:
                response.result.correlation_id = returned_0_0
            echoed_0 = request.feature_value_id
            response.feature_value.feature_value_id = echoed_0
            echoed_1 = request.details.effective_at
            response.outcome.effective_at.CopyFrom(echoed_1)
            return response

    async def handle_terminate_feature_value(
        self,
        request: featurestore_v1_feature_value_lifecycle_service_pb2.TerminateFeatureValueRequest
    ) -> featurestore_v1_feature_value_lifecycle_service_pb2.TerminateFeatureValueResponse:
        """Terminates a feature value."""
        deps = self.deps
        response = featurestore_v1_feature_value_lifecycle_service_pb2.TerminateFeatureValueResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('TerminateFeatureValue', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'TerminateFeatureValue', {'reason': request.reason})
            response_0 = metrics_v1_dashboard_notification_service_pb2.StreamDashboardNoticesResponse()
            response_1 = lineage_v1_lineage_edge_workflow_service_pb2.StartLineageEdgeWorkflowResponse()
            outgoing_0 = metrics_v1_dashboard_notification_service_pb2.StreamDashboardNoticesRequest(
                context=request.context,
                subscriber=common_v1_contact_pb2.ContactInfo(
                    preferred_channel=request.details.notify_contact.preferred_channel
                )
            )
            async for chunk_0 in deps.clients.metrics_dashboard_notification.StreamDashboardNotices(
                outgoing_0,
                timeout=deps.settings.timeout
            ):
                response_0 = chunk_0
            outgoing_1 = lineage_v1_lineage_edge_workflow_service_pb2.StartLineageEdgeWorkflowRequest(
                context=request.context,
                details=lineage_v1_lineage_edge_workflow_service_pb2.StartLineageEdgeWorkflowRequest.Details(
                    notify=common_v1_contact_pb2.ContactInfo(
                        email=request.details.new_owner.email,
                        name=request.details.notify_contact.name,
                        preferred_channel=request.details.notify_contact.preferred_channel
                    )
                ),
                lineage_edge=lineage_v1_lineage_pb2.LineageEdge(
                    subject=lineage_v1_refs_pb2.ImpactRef(display_name=request.details.new_owner.display_name)
                )
            )
            response_1 = cast(lineage_v1_lineage_edge_workflow_service_pb2.StartLineageEdgeWorkflowResponse, await deps.bus.request(
                'acme.featurestore.v1.FeatureValueLifecycleService/TerminateFeatureValue/1', outgoing_1, deps.settings.timeout,
            ))
            returned_1_0 = response_1.outcome.message
            if returned_1_0:
                response.result.message = returned_1_0
            returned_1_1 = response_1.result.correlation_id
            if returned_1_1:
                response.feature_value.correlation_id = returned_1_1
            echoed_0 = request.feature_value_id
            response.feature_value.feature_value_id = echoed_0
            echoed_1 = request.details.effective_at
            response.outcome.effective_at.CopyFrom(echoed_1)
            return response
