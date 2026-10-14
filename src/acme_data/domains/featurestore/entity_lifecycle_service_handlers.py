"""Reusable transport mixin for EntityLifecycleService."""

from __future__ import annotations

from collections.abc import AsyncIterator
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

from acme.audit.v1 import audit_event_query_service_pb2 as audit_v1_audit_event_query_service_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.datasets.v1 import data_schema_calculation_service_pb2 as datasets_v1_data_schema_calculation_service_pb2
from acme.datasets.v1 import data_schema_validation_service_pb2 as datasets_v1_data_schema_validation_service_pb2
from acme.datasets.v1 import dataset_query_service_pb2 as datasets_v1_dataset_query_service_pb2
from acme.datasets.v1 import dataset_service_pb2 as datasets_v1_dataset_service_pb2
from acme.datasets.v1 import dataset_validation_service_pb2 as datasets_v1_dataset_validation_service_pb2
from acme.datasets.v1 import datasets_pb2 as datasets_v1_datasets_pb2
from acme.featurestore.v1 import entity_calculation_service_pb2 as featurestore_v1_entity_calculation_service_pb2
from acme.featurestore.v1 import entity_import_service_pb2 as featurestore_v1_entity_import_service_pb2
from acme.featurestore.v1 import entity_lifecycle_service_pb2 as featurestore_v1_entity_lifecycle_service_pb2
from acme.featurestore.v1 import (
    feature_value_reporting_service_pb2 as featurestore_v1_feature_value_reporting_service_pb2,
)
from acme.featurestore.v1 import (
    feature_value_reporting_service_pb2_grpc as featurestore_v1_feature_value_reporting_service_pb2_grpc,
)
from acme.featurestore.v1 import feature_value_sync_service_pb2 as featurestore_v1_feature_value_sync_service_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.lineage.v1 import impact_workflow_service_pb2 as lineage_v1_impact_workflow_service_pb2
from acme.lineage.v1 import lineage_pb2 as lineage_v1_lineage_pb2
from acme.metrics.v1 import metric_alert_export_service_pb2 as metrics_v1_metric_alert_export_service_pb2
from acme.notifications.v1 import (
    notification_validation_service_pb2 as notifications_v1_notification_validation_service_pb2,
)
from acme.notifications.v1 import notifications_pb2 as notifications_v1_notifications_pb2
from acme.search.v1 import search_index_query_service_pb2 as search_v1_search_index_query_service_pb2

from acme_data.domains.featurestore.adapters import EntityLifecycleExpireEntity0Adapter
from acme_data.domains.featurestore.dependencies import Dependencies
from acme_data.domains.featurestore.models import EntityLifecycleSuspendEntity3Command
from acme_data.domains.featurestore.models import to_entity_lifecycle_suspend_entity3_command
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import run_steps
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_id
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class EntityLifecycleServicerHandlers:
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    async def ActivateEntity(
        self, request: featurestore_v1_entity_lifecycle_service_pb2.ActivateEntityRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_entity_lifecycle_service_pb2.ActivateEntityResponse:
        """Activates an entity."""
        return await self.handle_activate_entity(request)

    @rpc_errors
    async def ExpireEntity(
        self, request: featurestore_v1_entity_lifecycle_service_pb2.ExpireEntityRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_entity_lifecycle_service_pb2.ExpireEntityResponse:
        """Expires an entity."""
        return await self.handle_expire_entity(request)

    @rpc_errors
    @retry_transient
    async def GetEntityLifecycle(
        self, request: featurestore_v1_entity_lifecycle_service_pb2.GetEntityLifecycleRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_entity_lifecycle_service_pb2.GetEntityLifecycleResponse:
        """Returns an entity."""
        return await self.handle_get_entity_lifecycle(request)

    @rpc_errors
    async def ReinstateEntity(
        self, request: featurestore_v1_entity_lifecycle_service_pb2.ReinstateEntityRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_entity_lifecycle_service_pb2.ReinstateEntityResponse:
        """Reinstates an entity."""
        return await self.handle_reinstate_entity(request)

    @rpc_errors
    async def RenewEntity(
        self, request: featurestore_v1_entity_lifecycle_service_pb2.RenewEntityRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_entity_lifecycle_service_pb2.RenewEntityResponse:
        """Renews an entity."""
        return await self.handle_renew_entity(request)

    @rpc_errors
    async def ScheduleEntityExpiry(
        self, request: featurestore_v1_entity_lifecycle_service_pb2.ScheduleEntityExpiryRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_entity_lifecycle_service_pb2.ScheduleEntityExpiryResponse:
        """Schedules an entity."""
        return await self.handle_schedule_entity_expiry(request)

    @rpc_errors
    async def SuspendEntity(
        self, request: featurestore_v1_entity_lifecycle_service_pb2.SuspendEntityRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_entity_lifecycle_service_pb2.SuspendEntityResponse:
        """Suspends an entity."""
        return await self.handle_suspend_entity(request)

    @rpc_errors
    async def TerminateEntity(
        self, request: featurestore_v1_entity_lifecycle_service_pb2.TerminateEntityRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_entity_lifecycle_service_pb2.TerminateEntityResponse:
        """Terminates an entity."""
        return await self.handle_terminate_entity(request)

    async def handle_activate_entity(
        self,
        request: featurestore_v1_entity_lifecycle_service_pb2.ActivateEntityRequest
    ) -> featurestore_v1_entity_lifecycle_service_pb2.ActivateEntityResponse:
        """Activates an entity."""
        deps = self.deps
        response = featurestore_v1_entity_lifecycle_service_pb2.ActivateEntityResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ActivateEntity', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'ActivateEntity', {'reason': request.reason})
            response_0 = audit_v1_audit_event_query_service_pb2.BrowseAuditEventsResponse()
            response_1 = datasets_v1_dataset_service_pb2.WatchDatasetsResponse()
            response_2 = datasets_v1_dataset_validation_service_pb2.CheckDatasetEligibilityResponse()
            outgoing_0 = audit_v1_audit_event_query_service_pb2.BrowseAuditEventsRequest()
            outgoing_0.context.CopyFrom(request.context)
            outgoing_0.filter.created_after.CopyFrom(request.details.effective_at)
            outgoing_0.filter.labels.update(dict(request.annotations))
            outgoing_0.filter.owner_id = request.details.new_owner.user_id
            outgoing_0.context.tenant_id = tenant_id.get()
            response_0 = await deps.clients.audit_audit_event_query.BrowseAuditEvents(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = datasets_v1_dataset_service_pb2.WatchDatasetsRequest(
                context=request.context,
                subscriber=common_v1_contact_pb2.ContactInfo(
                    email=request.details.notify_contact.email,
                    name=request.details.notify_contact.name,
                    phone=request.details.notify_contact.phone,
                    preferred_channel=request.details.notify_contact.preferred_channel
                )
            )
            async for chunk_1 in deps.clients.datasets_dataset.WatchDatasets(outgoing_1, timeout=deps.settings.timeout):
                response_1 = chunk_1
            outgoing_2 = datasets_v1_dataset_validation_service_pb2.CheckDatasetEligibilityRequest(
                context=request.context,
                dataset=datasets_v1_datasets_pb2.Dataset(
                    owner=identity_v1_refs_pb2.UserRef(
                        display_name=request.details.new_owner.display_name,
                        email=request.details.new_owner.email,
                        user_id=request.details.new_owner.user_id
                    )
                ),
                details=datasets_v1_dataset_validation_service_pb2.CheckDatasetEligibilityRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(email=request.details.notify_contact.email)
                )
            )
            steps_2 = [
                partial(
                    deps.clients.datasets_dataset_validation.CheckDatasetEligibility,
                    outgoing_2,
                    timeout=deps.settings.timeout
                )
            ]
            results_2 = await run_steps(steps_2)
            response_2 = results_2[-1]
            returned_0_0 = response_0.result.correlation_id
            if returned_0_0:
                response.result.correlation_id = returned_0_0
            returned_0_1 = response_0.result.details
            response.result.details.update(returned_0_1)
            returned_2_0 = response_2.dataset.audit.updated_at
            if returned_2_0.ListFields():
                response.entity.audit.updated_at.MergeFrom(returned_2_0)
            returned_2_1 = response_2.dataset.audit.updated_by
            if returned_2_1:
                response.entity.audit.updated_by = returned_2_1
            echoed_0 = request.entity_id
            response.entity.entity_id = echoed_0
            echoed_1 = request.details.effective_at
            response.outcome.effective_at.CopyFrom(echoed_1)
            return response

    async def handle_expire_entity(
        self,
        request: featurestore_v1_entity_lifecycle_service_pb2.ExpireEntityRequest
    ) -> featurestore_v1_entity_lifecycle_service_pb2.ExpireEntityResponse:
        """Expires an entity."""
        deps = self.deps
        response = featurestore_v1_entity_lifecycle_service_pb2.ExpireEntityResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ExpireEntity', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'ExpireEntity', {'reason': request.reason})
            response_0 = featurestore_v1_feature_value_sync_service_pb2.ListFeatureValueConflictsResponse()
            outgoing_0 = featurestore_v1_feature_value_sync_service_pb2.ListFeatureValueConflictsRequest(
                context=request.context,
                filter=featurestore_v1_feature_value_sync_service_pb2.ListFeatureValueConflictsRequest.Filter(
                    created_after=request.details.effective_at,
                    owner_id=request.details.new_owner.user_id
                )
            )
            response_0 = await EntityLifecycleExpireEntity0Adapter(
                deps.clients.featurestore_feature_value_sync,
                deps.settings.timeout
            )(outgoing_0)
            returned_0_0 = response_0.result.details
            response.result.details.update(returned_0_0)
            echoed_0 = request.entity_id
            response.entity.entity_id = echoed_0
            echoed_1 = request.details.effective_at
            response.outcome.effective_at.CopyFrom(echoed_1)
            return response

    async def handle_get_entity_lifecycle(
        self,
        request: featurestore_v1_entity_lifecycle_service_pb2.GetEntityLifecycleRequest
    ) -> featurestore_v1_entity_lifecycle_service_pb2.GetEntityLifecycleResponse:
        """Returns an entity."""
        deps = self.deps
        response = featurestore_v1_entity_lifecycle_service_pb2.GetEntityLifecycleResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('GetEntityLifecycle', extra={'fields': {'domain': 'featurestore'}})
            await deps.repository.audit(request.context.tenant_id, 'GetEntityLifecycle', {})
            response_0 = notifications_v1_notification_validation_service_pb2.CheckNotificationEligibilityResponse()
            outgoing_0 = notifications_v1_notification_validation_service_pb2.CheckNotificationEligibilityRequest(
                context=request.context,
                details=notifications_v1_notification_validation_service_pb2.CheckNotificationEligibilityRequest.Details(
                    locale=request.context.locale
                ),
                notification=notifications_v1_notifications_pb2.Notification(
                    assignee=identity_v1_refs_pb2.UserRef(email=request.context.actor.email)
                )
            )
            response_0 = await deps.clients.notifications_notification_validation.CheckNotificationEligibility(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.notification.audit.updated_by
            if returned_0_0:
                response.entity.audit.updated_by = returned_0_0
            returned_0_1 = response_0.notification.assignee.email
            if returned_0_1:
                response.entity.contact.email = returned_0_1
            echoed_0 = request.entity_id
            response.entity.entity_id = echoed_0
            return response

    async def handle_reinstate_entity(
        self,
        request: featurestore_v1_entity_lifecycle_service_pb2.ReinstateEntityRequest
    ) -> featurestore_v1_entity_lifecycle_service_pb2.ReinstateEntityResponse:
        """Reinstates an entity."""
        deps = self.deps
        response = featurestore_v1_entity_lifecycle_service_pb2.ReinstateEntityResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ReinstateEntity', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'ReinstateEntity', {'reason': request.reason})
            response_0 = lineage_v1_impact_workflow_service_pb2.PauseImpactWorkflowResponse()
            outgoing_0 = lineage_v1_impact_workflow_service_pb2.PauseImpactWorkflowRequest(
                context=request.context,
                details=lineage_v1_impact_workflow_service_pb2.PauseImpactWorkflowRequest.Details(
                    notify=common_v1_contact_pb2.ContactInfo(email=request.details.new_owner.email)
                ),
                impact=lineage_v1_lineage_pb2.Impact(
                    requester=common_v1_contact_pb2.ContactInfo(phone=request.details.notify_contact.phone)
                )
            )
            response_0 = await deps.clients.lineage_impact_workflow.PauseImpactWorkflow(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.impact.audit.etag
            if returned_0_0:
                response.entity.audit.etag = returned_0_0
            returned_0_1 = response_0.impact.requester.preferred_channel
            if returned_0_1:
                response.entity.contact.preferred_channel = returned_0_1
            echoed_0 = request.entity_id
            response.entity.entity_id = echoed_0
            echoed_1 = request.details.effective_at
            response.outcome.effective_at.CopyFrom(echoed_1)
            return response

    async def handle_renew_entity(
        self,
        request: featurestore_v1_entity_lifecycle_service_pb2.RenewEntityRequest
    ) -> featurestore_v1_entity_lifecycle_service_pb2.RenewEntityResponse:
        """Renews an entity."""
        deps = self.deps
        response = featurestore_v1_entity_lifecycle_service_pb2.RenewEntityResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('RenewEntity', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'RenewEntity', {'reason': request.reason})
            response_0 = featurestore_v1_entity_calculation_service_pb2.GetEntityRatesResponse()
            response_1 = metrics_v1_metric_alert_export_service_pb2.RetryMetricAlertExportResponse()
            outgoing_0 = featurestore_v1_entity_calculation_service_pb2.GetEntityRatesRequest(
                context=request.context,
                entity_id=request.entity_id
            )
            method_name_0 = 'GetEntityRates'
            response_0 = await getattr(
                deps.clients.featurestore_entity_calculation,
                method_name_0
            )(outgoing_0, timeout=deps.settings.timeout)
            fields_1: dict[str, Any] = {
                'context': request.context,
                'details': {'notify': {'phone': response_0.entity.contact.phone}}
            }
            outgoing_1 = metrics_v1_metric_alert_export_service_pb2.RetryMetricAlertExportRequest(**fields_1)
            response_1 = await deps.clients.metrics_metric_alert_export.RetryMetricAlertExport(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.entity.relationship_manager.email
            if returned_0_0:
                response.entity.contact.email = returned_0_0
            returned_0_1 = response_0.entity.preferences.quiet_hours
            if returned_0_1.ListFields():
                response.entity.preferences.quiet_hours.MergeFrom(returned_0_1)
            returned_1_0 = response_1.result.message
            if returned_1_0:
                response.outcome.message = returned_1_0
            echoed_0 = request.entity_id
            response.entity.entity_id = echoed_0
            echoed_1 = request.details.effective_at
            response.outcome.effective_at.CopyFrom(echoed_1)
            return response

    async def handle_schedule_entity_expiry(
        self,
        request: featurestore_v1_entity_lifecycle_service_pb2.ScheduleEntityExpiryRequest
    ) -> featurestore_v1_entity_lifecycle_service_pb2.ScheduleEntityExpiryResponse:
        """Schedules an entity."""
        deps = self.deps
        response = featurestore_v1_entity_lifecycle_service_pb2.ScheduleEntityExpiryResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ScheduleEntityExpiry', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'ScheduleEntityExpiry', {'reason': request.reason})
            await deps.repository.save_entity(request.context.tenant_id, request.entity)
            response_0 = featurestore_v1_entity_import_service_pb2.GetEntityImportStatusResponse()
            response_1 = search_v1_search_index_query_service_pb2.BrowseSearchIndexesResponse()
            outgoing_0 = featurestore_v1_entity_import_service_pb2.GetEntityImportStatusRequest(
                context=request.context,
                entity_id=request.entity.entity_id
            )
            document_0 = MessageToDict(outgoing_0, preserving_proto_field_name=True)
            outgoing_0 = ParseDict(document_0, featurestore_v1_entity_import_service_pb2.GetEntityImportStatusRequest())
            response_0 = await deps.clients.featurestore_entity_import.GetEntityImportStatus(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = search_v1_search_index_query_service_pb2.BrowseSearchIndexesRequest(
                context=request.context,
                filter=search_v1_search_index_query_service_pb2.BrowseSearchIndexesRequest.Filter(
                    region=request.entity.primary_address.region
                )
            )
            document_1 = MessageToJson(outgoing_1, preserving_proto_field_name=True)
            outgoing_1 = Parse(document_1, search_v1_search_index_query_service_pb2.BrowseSearchIndexesRequest())
            response_1 = await deps.clients.search_search_index_query.BrowseSearchIndexes(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.entity.relationship_manager.user_id
            if returned_0_0:
                response.entity.relationship_manager.user_id = returned_0_0
            returned_1_0 = response_1.result.status
            if returned_1_0:
                response.result.status = returned_1_0
            echoed_0 = request.entity_id
            response.entity.entity_id = echoed_0
            echoed_1 = request.entity.name
            response.entity.contact.name.CopyFrom(echoed_1)
            return response

    async def handle_suspend_entity(
        self,
        request: featurestore_v1_entity_lifecycle_service_pb2.SuspendEntityRequest
    ) -> featurestore_v1_entity_lifecycle_service_pb2.SuspendEntityResponse:
        """Suspends an entity."""
        deps = self.deps
        response = featurestore_v1_entity_lifecycle_service_pb2.SuspendEntityResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SuspendEntity', extra={'fields': {'reason_code': request.details.reason_code}})
            await deps.repository.audit(
                request.context.tenant_id,
                'SuspendEntity',
                {'reason_code': request.details.reason_code}
            )
            response_0 = datasets_v1_data_schema_validation_service_pb2.ScoreDataSchemaResponse()
            response_1 = featurestore_v1_feature_value_reporting_service_pb2.StreamFeatureValueMetricsResponse()
            response_2 = featurestore_v1_feature_value_reporting_service_pb2.ScheduleFeatureValueReportResponse()
            response_3 = datasets_v1_dataset_query_service_pb2.SummarizeDatasetsResponse()
            outgoing_0 = datasets_v1_data_schema_validation_service_pb2.ScoreDataSchemaRequest()
            outgoing_0.context.CopyFrom(request.context)
            field_0_1_part_1 = outgoing_0.data_schema.children.add()
            field_0_1_part_2 = field_0_1_part_1.children.add()
            field_0_1_part_2.manager.display_name = request.details.new_owner.display_name
            merged_0 = datasets_v1_data_schema_validation_service_pb2.ScoreDataSchemaRequest()
            merged_0.MergeFrom(outgoing_0)
            outgoing_0.CopyFrom(merged_0)
            response_0 = await deps.clients.datasets_data_schema_validation.ScoreDataSchema(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = featurestore_v1_feature_value_reporting_service_pb2.StreamFeatureValueMetricsRequest(
                context=request.context,
                subscriber=common_v1_contact_pb2.ContactInfo(email=response_0.data_schema.manager.email)
            )
            async for chunk_1 in deps.clients.featurestore_feature_value_reporting.StreamFeatureValueMetrics(
                outgoing_1,
                timeout=deps.settings.timeout
            ):
                response_1 = chunk_1
            outgoing_2 = featurestore_v1_feature_value_reporting_service_pb2.ScheduleFeatureValueReportRequest(
                annotations=dict(request.annotations),
                context=request.context,
                reason=request.reason
            )
            registered_2 = cast(
                featurestore_v1_feature_value_reporting_service_pb2_grpc.FeatureValueReportingServiceStub,
                deps.clients.registry['acme.featurestore.v1.FeatureValueReportingService']
            )
            response_2 = await registered_2.ScheduleFeatureValueReport(outgoing_2, timeout=deps.settings.timeout)
            command_3 = EntityLifecycleSuspendEntity3Command(
                context=request.context,
                annotations=dict(request.annotations),
                details_period=response_2.period
            )
            outgoing_3 = to_entity_lifecycle_suspend_entity3_command(command_3)
            response_3 = await deps.clients.datasets_dataset_query.SummarizeDatasets(
                outgoing_3,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_0)
            returned_0_1 = response_0.data_schema.location.region
            if returned_0_1:
                response.entity.primary_address.region = returned_0_1
            returned_2_0 = response_2.result.status
            if returned_2_0:
                response.result.status = returned_2_0
            returned_3_0 = response_3.result.message
            if returned_3_0:
                response.result.message = returned_3_0
            returned_3_1 = response_3.result.reference_ids
            response.result.reference_ids.extend(returned_3_1)
            echoed_0 = request.entity_id
            response.entity.entity_id = echoed_0
            echoed_1 = request.details.effective_at
            response.outcome.effective_at.CopyFrom(echoed_1)
            return response

    async def handle_terminate_entity(
        self,
        request: featurestore_v1_entity_lifecycle_service_pb2.TerminateEntityRequest
    ) -> featurestore_v1_entity_lifecycle_service_pb2.TerminateEntityResponse:
        """Terminates an entity."""
        deps = self.deps
        response = featurestore_v1_entity_lifecycle_service_pb2.TerminateEntityResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('TerminateEntity', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'TerminateEntity', {'reason': request.reason})
            response_0 = datasets_v1_data_schema_calculation_service_pb2.RecalculateDataSchemasResponse()
            response_1 = datasets_v1_dataset_query_service_pb2.SummarizeDatasetsResponse()
            outgoing_0 = datasets_v1_data_schema_calculation_service_pb2.RecalculateDataSchemasRequest(
                context=request.context,
                data_schema=datasets_v1_datasets_pb2.DataSchema(
                    children=[
                        datasets_v1_datasets_pb2.DataSchema(
                            children=[
                                datasets_v1_datasets_pb2.DataSchema(
                                    manager=identity_v1_refs_pb2.UserRef(
                                        display_name=request.details.new_owner.display_name,
                                        email=request.details.new_owner.email,
                                        user_id=request.details.new_owner.user_id
                                    )
                                )
                            ],
                            manager=identity_v1_refs_pb2.UserRef(email=request.details.notify_contact.email)
                        )
                    ]
                )
            )
            outgoing_1 = datasets_v1_dataset_query_service_pb2.SummarizeDatasetsRequest(
                annotations=dict(request.annotations),
                context=request.context
            )
            response_0, response_1 = await asyncio.gather(
                deps.clients.datasets_data_schema_calculation.RecalculateDataSchemas(
                    outgoing_0,
                    timeout=deps.settings.timeout
                ),
                deps.clients.datasets_dataset_query.SummarizeDatasets(outgoing_1, timeout=deps.settings.timeout),
            )
            returned_0_0 = response_0.result.correlation_id
            if returned_0_0:
                response.result.correlation_id = returned_0_0
            returned_0_1 = response_0.data_schema.audit.updated_by
            if returned_0_1:
                response.entity.audit.updated_by = returned_0_1
            returned_1_0 = response_1.result.message
            if returned_1_0:
                response.outcome.message = returned_1_0
            returned_1_1 = response_1.result.details
            response.result.details.update(returned_1_1)
            echoed_0 = request.entity_id
            response.entity.entity_id = echoed_0
            echoed_1 = request.details.effective_at
            response.outcome.effective_at.CopyFrom(echoed_1)
            return response
