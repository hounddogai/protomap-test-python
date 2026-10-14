"""Builds and schedules reports about label sets."""

from __future__ import annotations

from collections.abc import AsyncIterator
from functools import partial
from typing import Any
from typing import cast
import asyncio
import logging

from google.protobuf.any_pb2 import Any as AnyMessage
from google.protobuf.json_format import MessageToDict
from google.protobuf.json_format import ParseDict
import grpc

from acme.audit.v1 import audit_event_service_pb2 as audit_v1_audit_event_service_pb2
from acme.audit.v1 import audit_pb2 as audit_v1_audit_pb2
from acme.audit.v1 import refs_pb2 as audit_v1_refs_pb2
from acme.billing.v1 import billing_account_service_pb2 as billing_v1_billing_account_service_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.experiments.v1 import experiment_query_service_pb2 as experiments_v1_experiment_query_service_pb2
from acme.labeling.v1 import annotation_calculation_service_pb2 as labeling_v1_annotation_calculation_service_pb2
from acme.labeling.v1 import annotation_reporting_service_pb2 as labeling_v1_annotation_reporting_service_pb2
from acme.labeling.v1 import annotation_validation_service_pb2 as labeling_v1_annotation_validation_service_pb2
from acme.labeling.v1 import label_set_reporting_service_pb2 as labeling_v1_label_set_reporting_service_pb2
from acme.labeling.v1 import label_set_reporting_service_pb2_grpc as labeling_v1_label_set_reporting_service_pb2_grpc
from acme.labeling.v1 import label_set_validation_service_pb2 as labeling_v1_label_set_validation_service_pb2
from acme.labeling.v1 import labeling_pb2 as labeling_v1_labeling_pb2
from acme.lineage.v1 import lineage_node_approval_service_pb2 as lineage_v1_lineage_node_approval_service_pb2
from acme.metrics.v1 import metric_alert_validation_service_pb2 as metrics_v1_metric_alert_validation_service_pb2
from acme.notifications.v1 import notification_service_pb2 as notifications_v1_notification_service_pb2
from acme.performers.v1 import performer_query_service_pb2 as performers_v1_performer_query_service_pb2
from acme.search.v1 import search_index_query_service_pb2 as search_v1_search_index_query_service_pb2
from acme.search.v1 import search_index_query_service_pb2_grpc as search_v1_search_index_query_service_pb2_grpc
from acme.search.v1 import search_index_validation_service_pb2 as search_v1_search_index_validation_service_pb2

from acme_data.domains.labeling.dependencies import Dependencies
from acme_data.domains.labeling.models import LabelSetReportingShareLabelSetReport0Command
from acme_data.domains.labeling.models import to_label_set_reporting_share_label_set_report0_command
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class LabelSetReportingServicer(labeling_v1_label_set_reporting_service_pb2_grpc.LabelSetReportingServiceServicer):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    @retry_transient
    async def CountLabelSetTotals(
        self, request: labeling_v1_label_set_reporting_service_pb2.CountLabelSetTotalsRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_label_set_reporting_service_pb2.CountLabelSetTotalsResponse:
        """Counts label sets by status."""
        return await self.handle_count_label_set_totals(request)

    @rpc_errors
    async def DeleteLabelSetReport(
        self, request: labeling_v1_label_set_reporting_service_pb2.DeleteLabelSetReportRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_label_set_reporting_service_pb2.DeleteLabelSetReportResponse:
        """Deletes a label set."""
        return await self.handle_delete_label_set_report(request)

    @rpc_errors
    @retry_transient
    async def FetchLabelSetReport(
        self, request: labeling_v1_label_set_reporting_service_pb2.FetchLabelSetReportRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_label_set_reporting_service_pb2.FetchLabelSetReportResponse:
        """Returns a label set."""
        return await self.handle_fetch_label_set_report(request)

    @rpc_errors
    async def GenerateLabelSetReport(
        self, request: labeling_v1_label_set_reporting_service_pb2.GenerateLabelSetReportRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_label_set_reporting_service_pb2.GenerateLabelSetReportResponse:
        """Generates a label set."""
        return await self.handle_generate_label_set_report(request)

    @rpc_errors
    @retry_transient
    async def ListLabelSetReports(
        self, request: labeling_v1_label_set_reporting_service_pb2.ListLabelSetReportsRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_label_set_reporting_service_pb2.ListLabelSetReportsResponse:
        """Lists label sets a page at a time."""
        return await self.handle_list_label_set_reports(request)

    @rpc_errors
    async def ScheduleLabelSetReport(
        self, request: labeling_v1_label_set_reporting_service_pb2.ScheduleLabelSetReportRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_label_set_reporting_service_pb2.ScheduleLabelSetReportResponse:
        """Schedules a label set."""
        return await self.handle_schedule_label_set_report(request)

    @rpc_errors
    async def ShareLabelSetReport(
        self, request: labeling_v1_label_set_reporting_service_pb2.ShareLabelSetReportRequest, context: grpc.aio.ServicerContext,
    ) -> labeling_v1_label_set_reporting_service_pb2.ShareLabelSetReportResponse:
        """Shares a label set."""
        return await self.handle_share_label_set_report(request)

    @stream_errors
    async def StreamLabelSetMetrics(
        self, request: labeling_v1_label_set_reporting_service_pb2.StreamLabelSetMetricsRequest, context: grpc.aio.ServicerContext,
    ) -> AsyncIterator[labeling_v1_label_set_reporting_service_pb2.StreamLabelSetMetricsResponse]:
        """Streams the changes of label sets as they happen."""
        response = await self.handle_stream_label_set_metrics(request)
        for item in messages((response,)):
            yield item

    async def handle_count_label_set_totals(
        self,
        request: labeling_v1_label_set_reporting_service_pb2.CountLabelSetTotalsRequest
    ) -> labeling_v1_label_set_reporting_service_pb2.CountLabelSetTotalsResponse:
        """Counts label sets by status."""
        deps = self.deps
        response = labeling_v1_label_set_reporting_service_pb2.CountLabelSetTotalsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CountLabelSetTotals', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'CountLabelSetTotals',
                {'order_by': request.order_by}
            )
            response_0 = performers_v1_performer_query_service_pb2.SummarizePerformersResponse()
            response_1 = experiments_v1_experiment_query_service_pb2.SummarizeExperimentsResponse()
            outgoing_0 = performers_v1_performer_query_service_pb2.SummarizePerformersRequest(
                annotations=dict(request.context.baggage),
                context=request.context,
                details=performers_v1_performer_query_service_pb2.SummarizePerformersRequest.Details(
                    filters=dict(request.filter.labels)
                )
            )
            response_0 = await deps.clients.performers_performer_query.SummarizePerformers(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = experiments_v1_experiment_query_service_pb2.SummarizeExperimentsRequest(
                context=request.context,
                details=experiments_v1_experiment_query_service_pb2.SummarizeExperimentsRequest.Details(
                    filters=dict(response_0.summary),
                    period=response_0.period
                )
            )
            response_1 = cast(experiments_v1_experiment_query_service_pb2.SummarizeExperimentsResponse, await deps.bus.request(
                'acme.labeling.v1.LabelSetReportingService/CountLabelSetTotals/1', outgoing_1, deps.settings.timeout,
            ))
            returned_0_0 = response_0.result.status
            if returned_0_0:
                response.result.status = returned_0_0
            returned_0_1 = response_0.result.message
            if returned_0_1:
                response.result.message = returned_0_1
            returned_1_0 = response_1.result.correlation_id
            if returned_1_0:
                response.result.correlation_id = returned_1_0
            return response

    async def handle_delete_label_set_report(
        self,
        request: labeling_v1_label_set_reporting_service_pb2.DeleteLabelSetReportRequest
    ) -> labeling_v1_label_set_reporting_service_pb2.DeleteLabelSetReportResponse:
        """Deletes a label set."""
        deps = self.deps
        response = labeling_v1_label_set_reporting_service_pb2.DeleteLabelSetReportResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('DeleteLabelSetReport', extra={'fields': {'etag': request.etag}})
            await deps.repository.audit(request.context.tenant_id, 'DeleteLabelSetReport', {'etag': request.etag})
            response_0 = labeling_v1_annotation_calculation_service_pb2.CalculateAnnotationResponse()
            response_1 = labeling_v1_annotation_reporting_service_pb2.StreamAnnotationMetricsResponse()
            outgoing_0 = labeling_v1_annotation_calculation_service_pb2.CalculateAnnotationRequest(
                annotation=labeling_v1_labeling_pb2.Annotation(
                    correlation_id=request.label_set_id,
                    measurements=[labeling_v1_labeling_pb2.AnnotationMeasurement(observed_at=request.context.deadline)],
                    source=request.context.actor.user_id
                ),
                context=request.context,
                reason=request.reason
            )
            response_0 = await deps.clients.labeling_annotation_calculation.CalculateAnnotation(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = labeling_v1_annotation_reporting_service_pb2.StreamAnnotationMetricsRequest(
                context=request.context,
                filter=labeling_v1_annotation_reporting_service_pb2.StreamAnnotationMetricsRequest.Filter(
                    created_after=response_0.annotation.occurred_at
                ),
                subscriber=common_v1_contact_pb2.ContactInfo(email=request.context.actor.email)
            )
            async for chunk_1 in deps.clients.labeling_annotation_reporting.StreamAnnotationMetrics(
                outgoing_1,
                timeout=deps.settings.timeout
            ):
                response_1 = chunk_1
            returned_0_0 = response_0.result.correlation_id
            if returned_0_0:
                response.result.correlation_id = returned_0_0
            return response

    async def handle_fetch_label_set_report(
        self,
        request: labeling_v1_label_set_reporting_service_pb2.FetchLabelSetReportRequest
    ) -> labeling_v1_label_set_reporting_service_pb2.FetchLabelSetReportResponse:
        """Returns a label set."""
        deps = self.deps
        response = labeling_v1_label_set_reporting_service_pb2.FetchLabelSetReportResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('FetchLabelSetReport', extra={'fields': {'locale': request.context.locale}})
            await deps.repository.audit(
                request.context.tenant_id,
                'FetchLabelSetReport',
                {'locale': request.context.locale}
            )
            echoed_0 = request.label_set_id
            response.label_set.label_set_id = echoed_0
            return response

    async def handle_generate_label_set_report(
        self,
        request: labeling_v1_label_set_reporting_service_pb2.GenerateLabelSetReportRequest
    ) -> labeling_v1_label_set_reporting_service_pb2.GenerateLabelSetReportResponse:
        """Generates a label set."""
        deps = self.deps
        response = labeling_v1_label_set_reporting_service_pb2.GenerateLabelSetReportResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('GenerateLabelSetReport', extra={'fields': {'label_set_id': request.label_set_id}})
            await deps.repository.audit(
                request.context.tenant_id,
                'GenerateLabelSetReport',
                {'label_set_id': request.label_set_id}
            )
            response_0 = search_v1_search_index_validation_service_pb2.ScoreSearchIndexResponse()
            response_1 = labeling_v1_label_set_validation_service_pb2.ValidateLabelSetResponse()
            fields_0: dict[str, Any] = {
                'annotations': dict(request.annotations),
                'context': request.context,
                'reason': request.reason,
                'search_index': {'owner': {'user_id': request.context.actor.user_id}}
            }
            outgoing_0 = search_v1_search_index_validation_service_pb2.ScoreSearchIndexRequest(**fields_0)
            response_0 = await deps.clients.search_search_index_validation.ScoreSearchIndex(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = labeling_v1_label_set_validation_service_pb2.ValidateLabelSetRequest(
                context=request.context,
                label_set=labeling_v1_labeling_pb2.LabelSet(
                    children=[
                        labeling_v1_labeling_pb2.LabelSet(
                            children=[
                                labeling_v1_labeling_pb2.LabelSet(
                                    audit=common_v1_audit_pb2.AuditInfo(
                                        created_by=response_0.search_index.audit.created_by
                                    )
                                )
                            ]
                        )
                    ]
                )
            )
            document_1 = MessageToDict(outgoing_1, preserving_proto_field_name=True)
            outgoing_1 = ParseDict(document_1, labeling_v1_label_set_validation_service_pb2.ValidateLabelSetRequest())
            response_1 = await deps.clients.labeling_label_set_validation.ValidateLabelSet(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.correlation_id
            if returned_0_0:
                response.result.correlation_id = returned_0_0
            returned_1_0 = response_1.outcome.status
            if returned_1_0:
                response.result.status = returned_1_0
            echoed_0 = request.details.period
            response.period.CopyFrom(echoed_0)
            return response

    async def handle_list_label_set_reports(
        self,
        request: labeling_v1_label_set_reporting_service_pb2.ListLabelSetReportsRequest
    ) -> labeling_v1_label_set_reporting_service_pb2.ListLabelSetReportsResponse:
        """Lists label sets a page at a time."""
        deps = self.deps
        response = labeling_v1_label_set_reporting_service_pb2.ListLabelSetReportsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ListLabelSetReports', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ListLabelSetReports',
                {'order_by': request.order_by}
            )
            response_0 = labeling_v1_annotation_validation_service_pb2.CheckAnnotationEligibilityResponse()
            response_1 = metrics_v1_metric_alert_validation_service_pb2.NormalizeMetricAlertResponse()
            outgoing_0 = labeling_v1_annotation_validation_service_pb2.CheckAnnotationEligibilityRequest(
                annotation=labeling_v1_labeling_pb2.Annotation(
                    measurements=[
                        labeling_v1_labeling_pb2.AnnotationMeasurement(observed_at=request.filter.created_after)
                    ]
                ),
                context=request.context,
                details=labeling_v1_annotation_validation_service_pb2.CheckAnnotationEligibilityRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(email=request.context.actor.email)
                )
            )
            response_0 = await deps.clients.labeling_annotation_validation.CheckAnnotationEligibility(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = metrics_v1_metric_alert_validation_service_pb2.NormalizeMetricAlertRequest()
            outgoing_1.context.CopyFrom(request.context)
            outgoing_1.metric_alert.priority = response_0.annotation.subject.priority
            outgoing_1.metric_alert.owner.display_name = response_0.annotation.subject.display_name
            outgoing_1.metric_alert.owner.user_id = request.context.actor.user_id
            merged_1 = metrics_v1_metric_alert_validation_service_pb2.NormalizeMetricAlertRequest()
            merged_1.MergeFrom(outgoing_1)
            outgoing_1.CopyFrom(merged_1)
            response_1 = await deps.clients.metrics_metric_alert_validation.NormalizeMetricAlert(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.details
            response.result.details.update(returned_0_0)
            returned_1_0 = response_1.metric_alert.owner.user_id
            returned_1_0_part_0 = response.label_sets.add()
            if returned_1_0:
                returned_1_0_part_0.manager.user_id = returned_1_0
            returned_1_1 = response_1.metric_alert.audit.etag
            returned_1_1_part_0 = response.label_sets.add()
            returned_1_1_part_1 = returned_1_1_part_0.children.add()
            returned_1_1_part_2 = returned_1_1_part_1.children.add()
            if returned_1_1:
                returned_1_1_part_2.audit.etag = returned_1_1
            return response

    async def handle_schedule_label_set_report(
        self,
        request: labeling_v1_label_set_reporting_service_pb2.ScheduleLabelSetReportRequest
    ) -> labeling_v1_label_set_reporting_service_pb2.ScheduleLabelSetReportResponse:
        """Schedules a label set."""
        deps = self.deps
        response = labeling_v1_label_set_reporting_service_pb2.ScheduleLabelSetReportResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ScheduleLabelSetReport', extra={'fields': {'domain': 'labeling'}})
            await deps.repository.audit(request.context.tenant_id, 'ScheduleLabelSetReport', {})
            response_0 = notifications_v1_notification_service_pb2.SearchNotificationsResponse()
            response_1 = search_v1_search_index_query_service_pb2.SummarizeSearchIndexesResponse()
            outgoing_0 = notifications_v1_notification_service_pb2.SearchNotificationsRequest(
                context=request.context,
                filter=notifications_v1_notification_service_pb2.SearchNotificationsRequest.Filter(
                    labels=dict(request.details.filters),
                    owner_id=request.label_set_id
                )
            )
            envelope_0 = AnyMessage()
            envelope_0.Pack(outgoing_0)
            outgoing_0 = notifications_v1_notification_service_pb2.SearchNotificationsRequest()
            if not envelope_0.Unpack(outgoing_0):
                raise ValueError("partner envelope contains the wrong request type")
            response_0 = await deps.clients.notifications_notification.SearchNotifications(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = search_v1_search_index_query_service_pb2.SummarizeSearchIndexesRequest(
                context=request.context,
                details=search_v1_search_index_query_service_pb2.SummarizeSearchIndexesRequest.Details(
                    cron=request.details.cron,
                    filters=dict(request.details.filters),
                    format=request.details.format
                ),
                reason=request.reason
            )
            registered_1 = cast(
                search_v1_search_index_query_service_pb2_grpc.SearchIndexQueryServiceStub,
                deps.clients.registry['acme.search.v1.SearchIndexQueryService']
            )
            response_1 = await registered_1.SummarizeSearchIndexes(outgoing_1, timeout=deps.settings.timeout)
            returned_0_0 = response_0.result.status
            if returned_0_0:
                response.result.status = returned_0_0
            returned_1_0 = response_1.download_uri
            if returned_1_0:
                response.download_uri = returned_1_0
            echoed_0 = request.details.period
            response.period.CopyFrom(echoed_0)
            return response

    async def handle_share_label_set_report(
        self,
        request: labeling_v1_label_set_reporting_service_pb2.ShareLabelSetReportRequest
    ) -> labeling_v1_label_set_reporting_service_pb2.ShareLabelSetReportResponse:
        """Shares a label set."""
        deps = self.deps
        response = labeling_v1_label_set_reporting_service_pb2.ShareLabelSetReportResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ShareLabelSetReport', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'ShareLabelSetReport', {'reason': request.reason})
            response_0 = lineage_v1_lineage_node_approval_service_pb2.SubmitLineageNodeResponse()
            command_0 = LabelSetReportingShareLabelSetReport0Command(
                context=request.context,
                lineage_node_manager_email=request.details.recipient.email,
                lineage_node_children_children_manager_email=request.context.actor.email
            )
            outgoing_0 = to_label_set_reporting_share_label_set_report0_command(command_0)
            response_0 = await deps.clients.lineage_lineage_node_approval.SubmitLineageNode(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.lineage_node.location
            returned_0_0_part_1 = response.label_set.children.add()
            returned_0_0_part_2 = returned_0_0_part_1.children.add()
            if returned_0_0.ListFields():
                returned_0_0_part_2.location.MergeFrom(returned_0_0)
            returned_0_1 = response_0.lineage_node.depth
            returned_0_1_part_1 = response.label_set.children.add()
            returned_0_1_part_2 = returned_0_1_part_1.children.add()
            if returned_0_1:
                returned_0_1_part_2.depth = returned_0_1
            echoed_0 = request.label_set_id
            response.label_set.label_set_id = echoed_0
            echoed_1 = request.details.recipient.email
            response.label_set.manager.email = echoed_1
            return response

    async def handle_stream_label_set_metrics(
        self,
        request: labeling_v1_label_set_reporting_service_pb2.StreamLabelSetMetricsRequest
    ) -> labeling_v1_label_set_reporting_service_pb2.StreamLabelSetMetricsResponse:
        """Streams the changes of label sets as they happen."""
        deps = self.deps
        response = labeling_v1_label_set_reporting_service_pb2.StreamLabelSetMetricsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('StreamLabelSetMetrics', extra={'fields': {'max_events': request.max_events}})
            await deps.repository.audit(
                request.context.tenant_id,
                'StreamLabelSetMetrics',
                {'max_events': request.max_events}
            )
            response_0 = labeling_v1_annotation_validation_service_pb2.ValidateAnnotationResponse()
            response_1 = audit_v1_audit_event_service_pb2.CreateAuditEventResponse()
            response_2 = billing_v1_billing_account_service_pb2.BatchGetBillingAccountsResponse()
            outgoing_0 = labeling_v1_annotation_validation_service_pb2.ValidateAnnotationRequest(
                context=request.context,
                details=labeling_v1_annotation_validation_service_pb2.ValidateAnnotationRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(
                        email=request.subscriber.email,
                        name=request.subscriber.name,
                        phone=request.subscriber.phone,
                        preferred_channel=request.subscriber.preferred_channel
                    )
                )
            )
            outgoing_2 = billing_v1_billing_account_service_pb2.BatchGetBillingAccountsRequest(context=request.context)
            response_0, response_2 = await asyncio.gather(
                deps.clients.labeling_annotation_validation.ValidateAnnotation(
                    outgoing_0,
                    timeout=deps.settings.timeout
                ),
                deps.clients.billing_billing_account.BatchGetBillingAccounts(outgoing_2, timeout=deps.settings.timeout),
            )
            outgoing_1 = audit_v1_audit_event_service_pb2.CreateAuditEventRequest(
                audit_event=audit_v1_audit_pb2.AuditEvent(
                    correlation_id=response_0.result.correlation_id,
                    source=response_0.annotation.source,
                    subject=audit_v1_refs_pb2.AuditTrailRef(display_name=response_0.annotation.subject.display_name)
                ),
                context=request.context
            )
            send_1 = partial(deps.clients.audit_audit_event.CreateAuditEvent, timeout=deps.settings.timeout)
            response_1 = await send_1(outgoing_1)
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.result.message = returned_0_0
            returned_0_1 = response_0.result.correlation_id
            if returned_0_1:
                response.result.correlation_id = returned_0_1
            returned_1_0 = response_1.result.correlation_id
            if returned_1_0:
                response.result.correlation_id = returned_1_0
            returned_1_1 = response_1.audit_event.subject.display_name
            if returned_1_1:
                response.label_set.manager.display_name = returned_1_1
            returned_2_0 = response_2.result.details
            response.result.details.update(returned_2_0)
            returned_2_1 = response_2.result.status
            if returned_2_1:
                response.result.status = returned_2_1
            echoed_0 = request.subscriber.email
            response.label_set.manager.email = echoed_0
            echoed_1 = request.filter.region
            response.label_set.location.region = echoed_1
            return response
