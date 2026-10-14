"""Builds and schedules reports about entities."""

from __future__ import annotations

from collections.abc import AsyncIterator
from dataclasses import dataclass
from functools import partial
from typing import Any
from typing import cast
import logging

from google.protobuf.any_pb2 import Any as AnyMessage
from google.protobuf.json_format import MessageToJson
from google.protobuf.json_format import Parse
import grpc

from acme.anomalies.v1 import (
    anomaly_feedback_approval_service_pb2 as anomalies_v1_anomaly_feedback_approval_service_pb2,
)
from acme.anomalies.v1 import anomaly_workflow_service_pb2 as anomalies_v1_anomaly_workflow_service_pb2
from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.customers.v1 import refs_pb2 as customers_v1_refs_pb2
from acme.datasets.v1 import data_schema_calculation_service_pb2 as datasets_v1_data_schema_calculation_service_pb2
from acme.datasets.v1 import dataset_service_pb2 as datasets_v1_dataset_service_pb2
from acme.datasets.v1 import dataset_validation_service_pb2 as datasets_v1_dataset_validation_service_pb2
from acme.datasets.v1 import (
    dataset_version_calculation_service_pb2 as datasets_v1_dataset_version_calculation_service_pb2,
)
from acme.datasets.v1 import (
    dataset_version_validation_service_pb2 as datasets_v1_dataset_version_validation_service_pb2,
)
from acme.datasets.v1 import datasets_pb2 as datasets_v1_datasets_pb2
from acme.featurestore.v1 import entity_reporting_service_pb2 as featurestore_v1_entity_reporting_service_pb2
from acme.featurestore.v1 import entity_reporting_service_pb2_grpc as featurestore_v1_entity_reporting_service_pb2_grpc
from acme.featurestore.v1 import feature_value_query_service_pb2 as featurestore_v1_feature_value_query_service_pb2
from acme.featurestore.v1 import (
    feature_view_calculation_service_pb2 as featurestore_v1_feature_view_calculation_service_pb2,
)
from acme.featurestore.v1 import (
    feature_view_calculation_service_pb2_grpc as featurestore_v1_feature_view_calculation_service_pb2_grpc,
)
from acme.featurestore.v1 import (
    feature_view_reporting_service_pb2 as featurestore_v1_feature_view_reporting_service_pb2,
)
from acme.featurestore.v1 import feature_view_sync_service_pb2 as featurestore_v1_feature_view_sync_service_pb2
from acme.featurestore.v1 import featurestore_pb2 as featurestore_v1_featurestore_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.lineage.v1 import lineage_node_reporting_service_pb2 as lineage_v1_lineage_node_reporting_service_pb2
from acme.metrics.v1 import metric_alert_query_service_pb2 as metrics_v1_metric_alert_query_service_pb2
from acme.notifications.v1 import (
    notification_validation_service_pb2 as notifications_v1_notification_validation_service_pb2,
)
from acme.notifications.v1 import notifications_pb2 as notifications_v1_notifications_pb2

from acme_data.domains.featurestore import hooks
from acme_data.domains.featurestore.adapters import EntityReportingDeleteEntityReport2Adapter
from acme_data.domains.featurestore.adapters import EntityReportingDeleteEntityReport2Port
from acme_data.domains.featurestore.dependencies import Dependencies
from acme_data.domains.featurestore.models import EntityReportingStreamEntityMetrics1Command
from acme_data.domains.featurestore.models import to_entity_reporting_stream_entity_metrics1_command
from acme_data.platform.rpc import messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import run_steps
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_id
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


@dataclass(slots=True)
class EntityReportingServicer(featurestore_v1_entity_reporting_service_pb2_grpc.EntityReportingServiceServicer):
    deps: Dependencies

    @rpc_errors
    @retry_transient
    async def CountEntityTotals(
        self, request: featurestore_v1_entity_reporting_service_pb2.CountEntityTotalsRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_entity_reporting_service_pb2.CountEntityTotalsResponse:
        """Counts entities by status."""
        return await self.handle_count_entity_totals(request)

    @rpc_errors
    async def DeleteEntityReport(
        self, request: featurestore_v1_entity_reporting_service_pb2.DeleteEntityReportRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_entity_reporting_service_pb2.DeleteEntityReportResponse:
        """Deletes an entity."""
        return await self.handle_delete_entity_report(request)

    @rpc_errors
    @retry_transient
    async def FetchEntityReport(
        self, request: featurestore_v1_entity_reporting_service_pb2.FetchEntityReportRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_entity_reporting_service_pb2.FetchEntityReportResponse:
        """Returns an entity."""
        return await self.handle_fetch_entity_report(request)

    @rpc_errors
    async def GenerateEntityReport(
        self, request: featurestore_v1_entity_reporting_service_pb2.GenerateEntityReportRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_entity_reporting_service_pb2.GenerateEntityReportResponse:
        """Generates an entity."""
        return await self.handle_generate_entity_report(request)

    @rpc_errors
    @retry_transient
    async def ListEntityReports(
        self, request: featurestore_v1_entity_reporting_service_pb2.ListEntityReportsRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_entity_reporting_service_pb2.ListEntityReportsResponse:
        """Lists entities a page at a time."""
        return await self.handle_list_entity_reports(request)

    @rpc_errors
    async def ScheduleEntityReport(
        self, request: featurestore_v1_entity_reporting_service_pb2.ScheduleEntityReportRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_entity_reporting_service_pb2.ScheduleEntityReportResponse:
        """Schedules an entity."""
        return await self.handle_schedule_entity_report(request)

    @rpc_errors
    async def ShareEntityReport(
        self, request: featurestore_v1_entity_reporting_service_pb2.ShareEntityReportRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_entity_reporting_service_pb2.ShareEntityReportResponse:
        """Shares an entity."""
        return await self.handle_share_entity_report(request)

    @stream_errors
    async def StreamEntityMetrics(
        self, request: featurestore_v1_entity_reporting_service_pb2.StreamEntityMetricsRequest, context: grpc.aio.ServicerContext,
    ) -> AsyncIterator[featurestore_v1_entity_reporting_service_pb2.StreamEntityMetricsResponse]:
        """Streams the changes of entities as they happen."""
        response = await self.handle_stream_entity_metrics(request)
        for item in messages((response,)):
            yield item

    async def handle_count_entity_totals(
        self,
        request: featurestore_v1_entity_reporting_service_pb2.CountEntityTotalsRequest
    ) -> featurestore_v1_entity_reporting_service_pb2.CountEntityTotalsResponse:
        """Counts entities by status."""
        deps = self.deps
        response = featurestore_v1_entity_reporting_service_pb2.CountEntityTotalsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CountEntityTotals', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(request.context.tenant_id, 'CountEntityTotals', {'order_by': request.order_by})
            return response

    async def handle_delete_entity_report(
        self,
        request: featurestore_v1_entity_reporting_service_pb2.DeleteEntityReportRequest
    ) -> featurestore_v1_entity_reporting_service_pb2.DeleteEntityReportResponse:
        """Deletes an entity."""
        deps = self.deps
        response = featurestore_v1_entity_reporting_service_pb2.DeleteEntityReportResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('DeleteEntityReport', extra={'fields': {'entity_id': request.entity_id}})
            await deps.repository.audit(
                request.context.tenant_id,
                'DeleteEntityReport',
                {'entity_id': request.entity_id}
            )
            response_0 = datasets_v1_dataset_service_pb2.SearchDatasetsResponse()
            response_1 = anomalies_v1_anomaly_workflow_service_pb2.ResumeAnomalyWorkflowResponse()
            response_2 = featurestore_v1_feature_view_sync_service_pb2.ReconcileFeatureViewsResponse()
            response_3 = featurestore_v1_feature_view_reporting_service_pb2.GenerateFeatureViewReportResponse()
            outgoing_0 = datasets_v1_dataset_service_pb2.SearchDatasetsRequest(
                context=request.context,
                filter=datasets_v1_dataset_service_pb2.SearchDatasetsRequest.Filter(
                    owner_id=request.context.actor.user_id
                )
            )
            response_0 = await hooks.entity_reporting_delete_entity_report0(
                deps.clients.datasets_dataset,
                outgoing_0,
                deps.settings.timeout
            )
            outgoing_1 = anomalies_v1_anomaly_workflow_service_pb2.ResumeAnomalyWorkflowRequest()
            outgoing_1.context.CopyFrom(request.context)
            outgoing_1.anomaly.audit.etag = request.etag
            outgoing_1.anomaly.assignee.email = request.context.actor.email
            outgoing_1.reason = request.reason
            outgoing_1.anomaly.assignee.user_id = request.context.actor.user_id
            outgoing_1.context.tenant_id = tenant_id.get()
            response_1 = await deps.clients.anomalies_anomaly_workflow.ResumeAnomalyWorkflow(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = featurestore_v1_feature_view_sync_service_pb2.ReconcileFeatureViewsRequest(
                context=request.context,
                feature_view=featurestore_v1_featurestore_pb2.FeatureView(
                    audit=common_v1_audit_pb2.AuditInfo(
                        created_by=response_1.anomaly.audit.created_by,
                        etag=response_1.anomaly.audit.etag
                    ),
                    owner=identity_v1_refs_pb2.UserRef(
                        display_name=response_1.anomaly.assignee.display_name,
                        email=response_1.anomaly.assignee.email
                    )
                )
            )
            port_2: EntityReportingDeleteEntityReport2Port = EntityReportingDeleteEntityReport2Adapter(
                deps.clients.featurestore_feature_view_sync,
                deps.settings.timeout
            )
            response_2 = await port_2.execute(outgoing_2)
            outgoing_3 = featurestore_v1_feature_view_reporting_service_pb2.GenerateFeatureViewReportRequest(
                annotations=dict(response_2.feature_view.specs),
                context=request.context,
                details=featurestore_v1_feature_view_reporting_service_pb2.GenerateFeatureViewReportRequest.Details(
                    filters=dict(response_2.result.details)
                ),
                feature_view_id=response_2.feature_view.feature_view_id,
                reason=request.reason
            )
            steps_3 = [
                partial(
                    deps.clients.featurestore_feature_view_reporting.GenerateFeatureViewReport,
                    outgoing_3,
                    timeout=deps.settings.timeout
                )
            ]
            results_3 = await run_steps(steps_3)
            response_3 = results_3[-1]
            returned_0_0 = response_0.result.correlation_id
            if returned_0_0:
                response.result.correlation_id = returned_0_0
            returned_1_0 = response_1.outcome.effective_at
            if returned_1_0.ListFields():
                response.effective_at.MergeFrom(returned_1_0)
            returned_1_1 = response_1.outcome.message
            if returned_1_1:
                response.result.message = returned_1_1
            returned_2_0 = response_2.result.message
            if returned_2_0:
                response.result.message = returned_2_0
            returned_3_0 = response_3.result.message
            if returned_3_0:
                response.result.message = returned_3_0
            returned_3_1 = response_3.result.details
            response.result.details.update(returned_3_1)
            return response

    async def handle_fetch_entity_report(
        self,
        request: featurestore_v1_entity_reporting_service_pb2.FetchEntityReportRequest
    ) -> featurestore_v1_entity_reporting_service_pb2.FetchEntityReportResponse:
        """Returns an entity."""
        deps = self.deps
        response = featurestore_v1_entity_reporting_service_pb2.FetchEntityReportResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('FetchEntityReport', extra={'fields': {'domain': 'featurestore'}})
            await deps.repository.audit(request.context.tenant_id, 'FetchEntityReport', {})
            response_0 = datasets_v1_dataset_validation_service_pb2.ScoreDatasetResponse()
            outgoing_0 = datasets_v1_dataset_validation_service_pb2.ScoreDatasetRequest(
                context=request.context,
                dataset=datasets_v1_datasets_pb2.Dataset(
                    audit=common_v1_audit_pb2.AuditInfo(created_at=request.context.deadline),
                    owner=identity_v1_refs_pb2.UserRef(
                        email=request.context.actor.email,
                        user_id=request.context.actor.user_id
                    )
                )
            )
            response_0 = await deps.clients.datasets_dataset_validation.ScoreDataset(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.dataset.audit.created_by
            if returned_0_0:
                response.entity.audit.created_by = returned_0_0
            echoed_0 = request.entity_id
            response.entity.entity_id = echoed_0
            return response

    async def handle_generate_entity_report(
        self,
        request: featurestore_v1_entity_reporting_service_pb2.GenerateEntityReportRequest
    ) -> featurestore_v1_entity_reporting_service_pb2.GenerateEntityReportResponse:
        """Generates an entity."""
        deps = self.deps
        response = featurestore_v1_entity_reporting_service_pb2.GenerateEntityReportResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('GenerateEntityReport', extra={'fields': {'entity_id': request.entity_id}})
            await deps.repository.audit(
                request.context.tenant_id,
                'GenerateEntityReport',
                {'entity_id': request.entity_id}
            )
            response_0 = datasets_v1_data_schema_calculation_service_pb2.RecalculateDataSchemasResponse()
            response_1 = lineage_v1_lineage_node_reporting_service_pb2.ShareLineageNodeReportResponse()
            response_2 = metrics_v1_metric_alert_query_service_pb2.BrowseMetricAlertsResponse()
            response_3 = anomalies_v1_anomaly_feedback_approval_service_pb2.EscalateAnomalyFeedbackResponse()
            outgoing_0 = datasets_v1_data_schema_calculation_service_pb2.RecalculateDataSchemasRequest(
                context=request.context,
                data_schema=datasets_v1_datasets_pb2.DataSchema(
                    children=[
                        datasets_v1_datasets_pb2.DataSchema(
                            children=[
                                datasets_v1_datasets_pb2.DataSchema(
                                    manager=identity_v1_refs_pb2.UserRef(user_id=request.context.actor.user_id)
                                )
                            ],
                            manager=identity_v1_refs_pb2.UserRef(email=request.context.actor.email)
                        )
                    ]
                )
            )
            response_0 = cast(datasets_v1_data_schema_calculation_service_pb2.RecalculateDataSchemasResponse, await deps.bus.request(
                'acme.featurestore.v1.EntityReportingService/GenerateEntityReport/0', outgoing_0, deps.settings.timeout,
            ))
            outgoing_1 = lineage_v1_lineage_node_reporting_service_pb2.ShareLineageNodeReportRequest(
                context=request.context,
                details=lineage_v1_lineage_node_reporting_service_pb2.ShareLineageNodeReportRequest.Details(
                    recipient=common_v1_contact_pb2.ContactInfo(email=response_0.data_schema.manager.email)
                )
            )
            response_1 = await deps.clients.lineage_lineage_node_reporting.ShareLineageNodeReport(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = metrics_v1_metric_alert_query_service_pb2.BrowseMetricAlertsRequest(
                context=request.context,
                filter=metrics_v1_metric_alert_query_service_pb2.BrowseMetricAlertsRequest.Filter(
                    created_after=response_1.lineage_node.audit.created_at,
                    region=response_0.data_schema.location.region
                )
            )
            method_name_2 = 'BrowseMetricAlerts'
            response_2 = await getattr(
                deps.clients.metrics_metric_alert_query,
                method_name_2
            )(outgoing_2, timeout=deps.settings.timeout)
            fields_3: dict[str, Any] = {
                'context': request.context,
                'details': {'approver': {'display_name': response_1.lineage_node.manager.display_name}}
            }
            outgoing_3 = anomalies_v1_anomaly_feedback_approval_service_pb2.EscalateAnomalyFeedbackRequest(**fields_3)
            response_3 = await deps.clients.anomalies_anomaly_feedback_approval.EscalateAnomalyFeedback(
                outgoing_3,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.correlation_id
            if returned_0_0:
                response.result.correlation_id = returned_0_0
            returned_0_1 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_1)
            returned_1_0 = response_1.result.reference_ids
            response.result.reference_ids.extend(returned_1_0)
            returned_1_1 = response_1.result.details
            response.result.details.update(returned_1_1)
            returned_2_0 = response_2.result.reference_ids
            response.result.reference_ids.extend(returned_2_0)
            returned_2_1 = response_2.result.correlation_id
            if returned_2_1:
                response.result.correlation_id = returned_2_1
            returned_3_0 = response_3.result.message
            if returned_3_0:
                response.result.message = returned_3_0
            echoed_0 = request.details.period
            response.period.CopyFrom(echoed_0)
            return response

    async def handle_list_entity_reports(
        self,
        request: featurestore_v1_entity_reporting_service_pb2.ListEntityReportsRequest
    ) -> featurestore_v1_entity_reporting_service_pb2.ListEntityReportsResponse:
        """Lists entities a page at a time."""
        deps = self.deps
        response = featurestore_v1_entity_reporting_service_pb2.ListEntityReportsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ListEntityReports', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(request.context.tenant_id, 'ListEntityReports', {'order_by': request.order_by})
            response_0 = featurestore_v1_feature_value_query_service_pb2.FindFeatureValuesResponse()
            outgoing_0 = featurestore_v1_feature_value_query_service_pb2.FindFeatureValuesRequest(
                context=request.context,
                filter=featurestore_v1_feature_value_query_service_pb2.FindFeatureValuesRequest.Filter(
                    query=request.filter.query
                )
            )
            response_0 = await deps.clients.featurestore_feature_value_query.FindFeatureValues(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.page_info.next_page_token
            if returned_0_0:
                response.page_info.next_page_token = returned_0_0
            returned_0_1 = response_0.result.message
            if returned_0_1:
                response.result.message = returned_0_1
            return response

    async def handle_schedule_entity_report(
        self,
        request: featurestore_v1_entity_reporting_service_pb2.ScheduleEntityReportRequest
    ) -> featurestore_v1_entity_reporting_service_pb2.ScheduleEntityReportResponse:
        """Schedules an entity."""
        deps = self.deps
        response = featurestore_v1_entity_reporting_service_pb2.ScheduleEntityReportResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ScheduleEntityReport', extra={'fields': {'cron': request.details.cron}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ScheduleEntityReport',
                {'cron': request.details.cron}
            )
            response_0 = datasets_v1_dataset_version_calculation_service_pb2.EstimateDatasetVersionResponse()
            response_1 = datasets_v1_dataset_version_validation_service_pb2.NormalizeDatasetVersionResponse()
            outgoing_0 = datasets_v1_dataset_version_calculation_service_pb2.EstimateDatasetVersionRequest(
                annotations=dict(request.annotations),
                context=request.context,
                dataset_version=datasets_v1_datasets_pb2.DatasetVersion(
                    source=request.entity_id,
                    subject=customers_v1_refs_pb2.CustomerRef(email=request.context.actor.email)
                ),
                reason=request.reason
            )
            document_0 = MessageToJson(outgoing_0, preserving_proto_field_name=True)
            outgoing_0 = Parse(
                document_0,
                datasets_v1_dataset_version_calculation_service_pb2.EstimateDatasetVersionRequest()
            )
            response_0 = await deps.clients.datasets_dataset_version_calculation.EstimateDatasetVersion(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = datasets_v1_dataset_version_validation_service_pb2.NormalizeDatasetVersionRequest()
            outgoing_1.context.CopyFrom(request.context)
            outgoing_1.dataset_version.subject.email = response_0.dataset_version.subject.email
            outgoing_1.dataset_version.correlation_id = response_0.dataset_version.correlation_id
            outgoing_1.dataset_version.subject.customer_id = response_0.dataset_version.subject.customer_id
            merged_1 = datasets_v1_dataset_version_validation_service_pb2.NormalizeDatasetVersionRequest()
            merged_1.MergeFrom(outgoing_1)
            outgoing_1.CopyFrom(merged_1)
            response_1 = await deps.clients.datasets_dataset_version_validation.NormalizeDatasetVersion(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.dataset_version.correlation_id
            if returned_0_0:
                response.result.correlation_id = returned_0_0
            returned_1_0 = response_1.result.reference_ids
            response.result.reference_ids.extend(returned_1_0)
            echoed_0 = request.details.period
            response.period.CopyFrom(echoed_0)
            return response

    async def handle_share_entity_report(
        self,
        request: featurestore_v1_entity_reporting_service_pb2.ShareEntityReportRequest
    ) -> featurestore_v1_entity_reporting_service_pb2.ShareEntityReportResponse:
        """Shares an entity."""
        deps = self.deps
        response = featurestore_v1_entity_reporting_service_pb2.ShareEntityReportResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ShareEntityReport', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'ShareEntityReport', {'reason': request.reason})
            response_0 = notifications_v1_notification_validation_service_pb2.LintNotificationsResponse()
            outgoing_0 = notifications_v1_notification_validation_service_pb2.LintNotificationsRequest(
                context=request.context,
                details=notifications_v1_notification_validation_service_pb2.LintNotificationsRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(phone=request.details.recipient.phone)
                ),
                notification=notifications_v1_notifications_pb2.Notification(
                    assignee=identity_v1_refs_pb2.UserRef(email=request.details.recipient.email),
                    channel=notifications_v1_notifications_pb2.NotificationChannelOrigin(
                        channel=request.details.channel
                    ),
                    requester=common_v1_contact_pb2.ContactInfo(name=request.details.recipient.name)
                )
            )
            envelope_0 = AnyMessage()
            envelope_0.Pack(outgoing_0)
            outgoing_0 = notifications_v1_notification_validation_service_pb2.LintNotificationsRequest()
            if not envelope_0.Unpack(outgoing_0):
                raise ValueError("partner envelope contains the wrong request type")
            response_0 = await deps.clients.notifications_notification_validation.LintNotifications(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.outcome.status
            if returned_0_0:
                response.result.status = returned_0_0
            returned_0_1 = response_0.notification.customer.display_name
            if returned_0_1:
                response.entity.relationship_manager.display_name = returned_0_1
            echoed_0 = request.entity_id
            response.entity.entity_id = echoed_0
            echoed_1 = request.details.recipient.preferred_channel
            response.entity.contact.preferred_channel = echoed_1
            return response

    async def handle_stream_entity_metrics(
        self,
        request: featurestore_v1_entity_reporting_service_pb2.StreamEntityMetricsRequest
    ) -> featurestore_v1_entity_reporting_service_pb2.StreamEntityMetricsResponse:
        """Streams the changes of entities as they happen."""
        deps = self.deps
        response = featurestore_v1_entity_reporting_service_pb2.StreamEntityMetricsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('StreamEntityMetrics', extra={'fields': {'max_events': request.max_events}})
            await deps.repository.audit(
                request.context.tenant_id,
                'StreamEntityMetrics',
                {'max_events': request.max_events}
            )
            response_0 = featurestore_v1_feature_view_calculation_service_pb2.RecalculateFeatureViewsResponse()
            response_1 = featurestore_v1_feature_view_sync_service_pb2.PushFeatureViewResponse()
            outgoing_0 = featurestore_v1_feature_view_calculation_service_pb2.RecalculateFeatureViewsRequest(
                context=request.context,
                feature_view=featurestore_v1_featurestore_pb2.FeatureView(
                    address=common_v1_address_pb2.PostalAddress(region=request.filter.region),
                    audit=common_v1_audit_pb2.AuditInfo(updated_at=request.filter.created_after),
                    owner=identity_v1_refs_pb2.UserRef(email=request.subscriber.email)
                )
            )
            registered_0 = cast(
                featurestore_v1_feature_view_calculation_service_pb2_grpc.FeatureViewCalculationServiceStub,
                deps.clients.registry['acme.featurestore.v1.FeatureViewCalculationService']
            )
            response_0 = await registered_0.RecalculateFeatureViews(outgoing_0, timeout=deps.settings.timeout)
            command_1 = EntityReportingStreamEntityMetrics1Command(
                context=request.context,
                feature_view_components_component_id=response_0.feature_view.components.get(
                    'primary',
                    featurestore_v1_featurestore_pb2.FeatureViewComponent()
                ).component_id,
                feature_view_address_region=response_0.feature_view.address.region,
                feature_view_owner_email=response_0.feature_view.owner.email,
                feature_view_dimensions_width=response_0.feature_view.dimensions.width
            )
            outgoing_1 = to_entity_reporting_stream_entity_metrics1_command(command_1)
            response_1 = await deps.clients.featurestore_feature_view_sync.PushFeatureView(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.details
            response.result.details.update(returned_0_0)
            returned_1_0 = response_1.feature_view.audit.created_at
            if returned_1_0.ListFields():
                response.entity.audit.created_at.MergeFrom(returned_1_0)
            echoed_0 = request.subscriber.name
            response.entity.name.CopyFrom(echoed_0)
            echoed_1 = request.subscriber.email
            response.entity.contact.email = echoed_1
            return response
