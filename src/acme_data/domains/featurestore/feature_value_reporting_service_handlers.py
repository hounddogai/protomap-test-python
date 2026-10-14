"""Reusable transport mixin for FeatureValueReportingService."""

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

from acme.anomalies.v1 import (
    anomaly_feedback_workflow_service_pb2 as anomalies_v1_anomaly_feedback_workflow_service_pb2,
)
from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.customers.v1 import refs_pb2 as customers_v1_refs_pb2
from acme.datasets.v1 import (
    dataset_version_validation_service_pb2 as datasets_v1_dataset_version_validation_service_pb2,
)
from acme.datasets.v1 import datasets_pb2 as datasets_v1_datasets_pb2
from acme.documents.v1 import document_query_service_pb2 as documents_v1_document_query_service_pb2
from acme.featurestore.v1 import entity_sync_service_pb2 as featurestore_v1_entity_sync_service_pb2
from acme.featurestore.v1 import (
    feature_value_calculation_service_pb2 as featurestore_v1_feature_value_calculation_service_pb2,
)
from acme.featurestore.v1 import feature_value_import_service_pb2 as featurestore_v1_feature_value_import_service_pb2
from acme.featurestore.v1 import (
    feature_value_reporting_service_pb2 as featurestore_v1_feature_value_reporting_service_pb2,
)
from acme.featurestore.v1 import feature_view_query_service_pb2 as featurestore_v1_feature_view_query_service_pb2
from acme.featurestore.v1 import (
    feature_view_reporting_service_pb2 as featurestore_v1_feature_view_reporting_service_pb2,
)
from acme.featurestore.v1 import feature_view_service_pb2 as featurestore_v1_feature_view_service_pb2
from acme.featurestore.v1 import feature_view_sync_service_pb2 as featurestore_v1_feature_view_sync_service_pb2
from acme.featurestore.v1 import featurestore_pb2 as featurestore_v1_featurestore_pb2
from acme.helpdesk.v1 import helpdesk_pb2 as helpdesk_v1_helpdesk_pb2
from acme.helpdesk.v1 import ticket_calculation_service_pb2 as helpdesk_v1_ticket_calculation_service_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.insurance.v1 import policy_query_service_pb2 as insurance_v1_policy_query_service_pb2

from acme_data.domains.featurestore.adapters import FeatureValueReportingGenerateFeatureValueReport1Adapter
from acme_data.domains.featurestore.dependencies import Dependencies
from acme_data.domains.featurestore.models import FeatureValueReportingStreamFeatureValueMetrics2Command
from acme_data.domains.featurestore.models import to_feature_value_reporting_stream_feature_value_metrics2_command
from acme_data.platform.rpc import messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import run_steps
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class FeatureValueReportingServicerHandlers:
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    @retry_transient
    async def CountFeatureValueTotals(
        self, request: featurestore_v1_feature_value_reporting_service_pb2.CountFeatureValueTotalsRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_feature_value_reporting_service_pb2.CountFeatureValueTotalsResponse:
        """Counts feature values by status."""
        return await self.handle_count_feature_value_totals(request)

    @rpc_errors
    @retry_transient
    async def FetchFeatureValueReport(
        self, request: featurestore_v1_feature_value_reporting_service_pb2.FetchFeatureValueReportRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_feature_value_reporting_service_pb2.FetchFeatureValueReportResponse:
        """Returns a feature value."""
        return await self.handle_fetch_feature_value_report(request)

    @rpc_errors
    async def GenerateFeatureValueReport(
        self, request: featurestore_v1_feature_value_reporting_service_pb2.GenerateFeatureValueReportRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_feature_value_reporting_service_pb2.GenerateFeatureValueReportResponse:
        """Generates a feature value."""
        return await self.handle_generate_feature_value_report(request)

    @rpc_errors
    @retry_transient
    async def ListFeatureValueReports(
        self, request: featurestore_v1_feature_value_reporting_service_pb2.ListFeatureValueReportsRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_feature_value_reporting_service_pb2.ListFeatureValueReportsResponse:
        """Lists feature values a page at a time."""
        return await self.handle_list_feature_value_reports(request)

    @rpc_errors
    async def ScheduleFeatureValueReport(
        self, request: featurestore_v1_feature_value_reporting_service_pb2.ScheduleFeatureValueReportRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_feature_value_reporting_service_pb2.ScheduleFeatureValueReportResponse:
        """Schedules a feature value."""
        return await self.handle_schedule_feature_value_report(request)

    @rpc_errors
    async def ShareFeatureValueReport(
        self, request: featurestore_v1_feature_value_reporting_service_pb2.ShareFeatureValueReportRequest, context: grpc.aio.ServicerContext,
    ) -> featurestore_v1_feature_value_reporting_service_pb2.ShareFeatureValueReportResponse:
        """Shares a feature value."""
        return await self.handle_share_feature_value_report(request)

    @stream_errors
    async def StreamFeatureValueMetrics(
        self, request: featurestore_v1_feature_value_reporting_service_pb2.StreamFeatureValueMetricsRequest, context: grpc.aio.ServicerContext,
    ) -> AsyncIterator[featurestore_v1_feature_value_reporting_service_pb2.StreamFeatureValueMetricsResponse]:
        """Streams the changes of feature values as they happen."""
        response = await self.handle_stream_feature_value_metrics(request)
        for item in messages((response,)):
            yield item

    async def handle_count_feature_value_totals(
        self,
        request: featurestore_v1_feature_value_reporting_service_pb2.CountFeatureValueTotalsRequest
    ) -> featurestore_v1_feature_value_reporting_service_pb2.CountFeatureValueTotalsResponse:
        """Counts feature values by status."""
        deps = self.deps
        response = featurestore_v1_feature_value_reporting_service_pb2.CountFeatureValueTotalsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CountFeatureValueTotals', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'CountFeatureValueTotals',
                {'order_by': request.order_by}
            )
            response_0 = featurestore_v1_feature_value_calculation_service_pb2.RecalculateFeatureValuesResponse()
            outgoing_0 = featurestore_v1_feature_value_calculation_service_pb2.RecalculateFeatureValuesRequest(
                context=request.context,
                details=featurestore_v1_feature_value_calculation_service_pb2.RecalculateFeatureValuesRequest.Details(
                    destination=common_v1_address_pb2.PostalAddress(region=request.filter.region)
                ),
                feature_value=featurestore_v1_featurestore_pb2.FeatureValue(
                    measurements=[
                        featurestore_v1_featurestore_pb2.FeatureValueMeasurement(
                            observed_at=request.filter.created_after
                        )
                    ]
                )
            )
            response_0 = await deps.clients.featurestore_feature_value_calculation.RecalculateFeatureValues(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.result.message = returned_0_0
            return response

    async def handle_fetch_feature_value_report(
        self,
        request: featurestore_v1_feature_value_reporting_service_pb2.FetchFeatureValueReportRequest
    ) -> featurestore_v1_feature_value_reporting_service_pb2.FetchFeatureValueReportResponse:
        """Returns a feature value."""
        deps = self.deps
        response = featurestore_v1_feature_value_reporting_service_pb2.FetchFeatureValueReportResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('FetchFeatureValueReport', extra={'fields': {'locale': request.context.locale}})
            await deps.repository.audit(
                request.context.tenant_id,
                'FetchFeatureValueReport',
                {'locale': request.context.locale}
            )
            echoed_0 = request.feature_value_id
            response.feature_value.feature_value_id = echoed_0
            return response

    async def handle_generate_feature_value_report(
        self,
        request: featurestore_v1_feature_value_reporting_service_pb2.GenerateFeatureValueReportRequest
    ) -> featurestore_v1_feature_value_reporting_service_pb2.GenerateFeatureValueReportResponse:
        """Generates a feature value."""
        deps = self.deps
        response = featurestore_v1_feature_value_reporting_service_pb2.GenerateFeatureValueReportResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('GenerateFeatureValueReport', extra={'fields': {'feature_value_id': request.feature_value_id}})
            await deps.repository.audit(
                request.context.tenant_id,
                'GenerateFeatureValueReport',
                {'feature_value_id': request.feature_value_id}
            )
            response_0 = helpdesk_v1_ticket_calculation_service_pb2.ExplainTicketCalculationResponse()
            response_1 = featurestore_v1_feature_view_query_service_pb2.SummarizeFeatureViewsResponse()
            response_2 = featurestore_v1_entity_sync_service_pb2.ReconcileEntitiesResponse()
            response_3 = datasets_v1_dataset_version_validation_service_pb2.ValidateDatasetVersionResponse()
            outgoing_0 = helpdesk_v1_ticket_calculation_service_pb2.ExplainTicketCalculationRequest(
                annotations=dict(request.annotations),
                context=request.context,
                reason=request.reason,
                ticket=helpdesk_v1_helpdesk_pb2.Ticket(
                    assignee=identity_v1_refs_pb2.UserRef(email=request.context.actor.email)
                )
            )
            steps_0 = [
                partial(
                    deps.clients.helpdesk_ticket_calculation.ExplainTicketCalculation,
                    outgoing_0,
                    timeout=deps.settings.timeout
                )
            ]
            results_0 = await run_steps(steps_0)
            response_0 = results_0[-1]
            outgoing_1 = featurestore_v1_feature_view_query_service_pb2.SummarizeFeatureViewsRequest(
                context=request.context,
                details=featurestore_v1_feature_view_query_service_pb2.SummarizeFeatureViewsRequest.Details(
                    cron=request.details.cron
                )
            )
            response_1 = await FeatureValueReportingGenerateFeatureValueReport1Adapter(
                deps.clients.featurestore_feature_view_query,
                deps.settings.timeout
            )(outgoing_1)
            outgoing_2 = featurestore_v1_entity_sync_service_pb2.ReconcileEntitiesRequest(
                context=request.context,
                entity=featurestore_v1_featurestore_pb2.Entity(
                    audit=common_v1_audit_pb2.AuditInfo(created_at=response_0.ticket.audit.created_at),
                    contact=common_v1_contact_pb2.ContactInfo(
                        preferred_channel=response_0.ticket.requester.preferred_channel
                    )
                )
            )
            response_2 = cast(featurestore_v1_entity_sync_service_pb2.ReconcileEntitiesResponse, await deps.bus.request(
                'acme.featurestore.v1.FeatureValueReportingService/GenerateFeatureValueReport/2', outgoing_2, deps.settings.timeout,
            ))
            outgoing_3 = datasets_v1_dataset_version_validation_service_pb2.ValidateDatasetVersionRequest(
                context=request.context,
                dataset_version=datasets_v1_datasets_pb2.DatasetVersion(
                    subject=customers_v1_refs_pb2.CustomerRef(email=response_2.entity.contact.email)
                ),
                details=datasets_v1_dataset_version_validation_service_pb2.ValidateDatasetVersionRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(name=response_2.entity.contact.name)
                )
            )
            response_3 = await deps.clients.datasets_dataset_version_validation.ValidateDatasetVersion(
                outgoing_3,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.status
            if returned_0_0:
                response.result.status = returned_0_0
            returned_0_1 = response_0.result.correlation_id
            if returned_0_1:
                response.result.correlation_id = returned_0_1
            returned_1_0 = response_1.result.status
            if returned_1_0:
                response.result.status = returned_1_0
            returned_2_0 = response_2.result.message
            if returned_2_0:
                response.result.message = returned_2_0
            returned_2_1 = response_2.result.status
            if returned_2_1:
                response.result.status = returned_2_1
            returned_3_0 = response_3.result.status
            if returned_3_0:
                response.result.status = returned_3_0
            returned_3_1 = response_3.result.details
            response.result.details.update(returned_3_1)
            echoed_0 = request.details.period
            response.period.CopyFrom(echoed_0)
            return response

    async def handle_list_feature_value_reports(
        self,
        request: featurestore_v1_feature_value_reporting_service_pb2.ListFeatureValueReportsRequest
    ) -> featurestore_v1_feature_value_reporting_service_pb2.ListFeatureValueReportsResponse:
        """Lists feature values a page at a time."""
        deps = self.deps
        response = featurestore_v1_feature_value_reporting_service_pb2.ListFeatureValueReportsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ListFeatureValueReports', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ListFeatureValueReports',
                {'order_by': request.order_by}
            )
            response_0 = insurance_v1_policy_query_service_pb2.BrowsePoliciesResponse()
            response_1 = featurestore_v1_feature_view_service_pb2.UpdateFeatureViewResponse()
            outgoing_0 = insurance_v1_policy_query_service_pb2.BrowsePoliciesRequest(
                context=request.context,
                filter=insurance_v1_policy_query_service_pb2.BrowsePoliciesRequest.Filter(
                    labels=dict(request.filter.labels),
                    region=request.filter.region
                )
            )
            response_0 = await deps.clients.insurance_policy_query.BrowsePolicies(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            fields_1: dict[str, Any] = {
                'context': request.context,
                'feature_view': {
                    'address': {'region': request.filter.region},
                    'owner': {'email': request.context.actor.email, 'user_id': request.context.actor.user_id}
                }
            }
            outgoing_1 = featurestore_v1_feature_view_service_pb2.UpdateFeatureViewRequest(**fields_1)
            response_1 = await deps.clients.featurestore_feature_view.UpdateFeatureView(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.result.message = returned_0_0
            returned_1_0 = response_1.feature_view.dimensions.unit
            returned_1_0_part_0 = response.feature_values.add()
            returned_1_0_part_1 = returned_1_0_part_0.measurements.add()
            if returned_1_0:
                returned_1_0_part_1.unit = returned_1_0
            returned_1_1 = response_1.result.details
            response.result.details.update(returned_1_1)
            return response

    async def handle_schedule_feature_value_report(
        self,
        request: featurestore_v1_feature_value_reporting_service_pb2.ScheduleFeatureValueReportRequest
    ) -> featurestore_v1_feature_value_reporting_service_pb2.ScheduleFeatureValueReportResponse:
        """Schedules a feature value."""
        deps = self.deps
        response = featurestore_v1_feature_value_reporting_service_pb2.ScheduleFeatureValueReportResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ScheduleFeatureValueReport', extra={'fields': {'cron': request.details.cron}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ScheduleFeatureValueReport',
                {'cron': request.details.cron}
            )
            response_0 = documents_v1_document_query_service_pb2.CountDocumentsResponse()
            response_1 = anomalies_v1_anomaly_feedback_workflow_service_pb2.StartAnomalyFeedbackWorkflowResponse()
            outgoing_0 = documents_v1_document_query_service_pb2.CountDocumentsRequest(
                context=request.context,
                filter=documents_v1_document_query_service_pb2.CountDocumentsRequest.Filter(
                    created_after=request.context.deadline,
                    labels=dict(request.details.filters),
                    owner_id=request.feature_value_id
                )
            )
            document_0 = MessageToDict(outgoing_0, preserving_proto_field_name=True)
            outgoing_0 = ParseDict(document_0, documents_v1_document_query_service_pb2.CountDocumentsRequest())
            response_0 = await deps.clients.documents_document_query.CountDocuments(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = anomalies_v1_anomaly_feedback_workflow_service_pb2.StartAnomalyFeedbackWorkflowRequest(
                context=request.context,
                reason=request.reason
            )
            document_1 = MessageToJson(outgoing_1, preserving_proto_field_name=True)
            outgoing_1 = Parse(
                document_1,
                anomalies_v1_anomaly_feedback_workflow_service_pb2.StartAnomalyFeedbackWorkflowRequest()
            )
            response_1 = await deps.clients.anomalies_anomaly_feedback_workflow.StartAnomalyFeedbackWorkflow(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.result.message = returned_0_0
            returned_0_1 = response_0.result.details
            response.result.details.update(returned_0_1)
            returned_1_0 = response_1.result.details
            response.result.details.update(returned_1_0)
            returned_1_1 = response_1.result.reference_ids
            response.result.reference_ids.extend(returned_1_1)
            echoed_0 = request.details.period
            response.period.CopyFrom(echoed_0)
            return response

    async def handle_share_feature_value_report(
        self,
        request: featurestore_v1_feature_value_reporting_service_pb2.ShareFeatureValueReportRequest
    ) -> featurestore_v1_feature_value_reporting_service_pb2.ShareFeatureValueReportResponse:
        """Shares a feature value."""
        deps = self.deps
        response = featurestore_v1_feature_value_reporting_service_pb2.ShareFeatureValueReportResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ShareFeatureValueReport', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ShareFeatureValueReport',
                {'reason': request.reason}
            )
            response_0 = featurestore_v1_feature_view_reporting_service_pb2.ListFeatureViewReportsResponse()
            outgoing_0 = featurestore_v1_feature_view_reporting_service_pb2.ListFeatureViewReportsRequest()
            outgoing_0.context.CopyFrom(request.context)
            outgoing_0.filter.owner_id = request.feature_value_id
            outgoing_0.filter.labels.update(dict(request.details.variables))
            outgoing_0.filter.created_after.CopyFrom(request.context.deadline)
            merged_0 = featurestore_v1_feature_view_reporting_service_pb2.ListFeatureViewReportsRequest()
            merged_0.MergeFrom(outgoing_0)
            outgoing_0.CopyFrom(merged_0)
            response_0 = await deps.clients.featurestore_feature_view_reporting.ListFeatureViewReports(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.outcome.message = returned_0_0
            returned_0_1 = response_0.result.correlation_id
            if returned_0_1:
                response.result.correlation_id = returned_0_1
            echoed_0 = request.feature_value_id
            response.feature_value.feature_value_id = echoed_0
            return response

    async def handle_stream_feature_value_metrics(
        self,
        request: featurestore_v1_feature_value_reporting_service_pb2.StreamFeatureValueMetricsRequest
    ) -> featurestore_v1_feature_value_reporting_service_pb2.StreamFeatureValueMetricsResponse:
        """Streams the changes of feature values as they happen."""
        deps = self.deps
        response = featurestore_v1_feature_value_reporting_service_pb2.StreamFeatureValueMetricsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('StreamFeatureValueMetrics', extra={'fields': {'max_events': request.max_events}})
            await deps.repository.audit(
                request.context.tenant_id,
                'StreamFeatureValueMetrics',
                {'max_events': request.max_events}
            )
            response_0 = featurestore_v1_feature_value_import_service_pb2.ListFeatureValueImportsResponse()
            response_1 = featurestore_v1_feature_view_sync_service_pb2.PushFeatureViewResponse()
            response_2 = datasets_v1_dataset_version_validation_service_pb2.LintDatasetVersionsResponse()
            outgoing_0 = featurestore_v1_feature_value_import_service_pb2.ListFeatureValueImportsRequest(
                context=request.context,
                filter=featurestore_v1_feature_value_import_service_pb2.ListFeatureValueImportsRequest.Filter(
                    created_after=request.filter.created_after,
                    query=request.filter.query,
                    statuses=list(request.filter.statuses)
                )
            )
            outgoing_1 = featurestore_v1_feature_view_sync_service_pb2.PushFeatureViewRequest(
                context=request.context,
                feature_view=featurestore_v1_featurestore_pb2.FeatureView(
                    address=common_v1_address_pb2.PostalAddress(region=request.filter.region),
                    owner=identity_v1_refs_pb2.UserRef(email=request.subscriber.email)
                )
            )
            response_0, response_1 = await asyncio.gather(
                deps.clients.featurestore_feature_value_import.ListFeatureValueImports(
                    outgoing_0,
                    timeout=deps.settings.timeout
                ),
                deps.clients.featurestore_feature_view_sync.PushFeatureView(outgoing_1, timeout=deps.settings.timeout),
            )
            command_2 = FeatureValueReportingStreamFeatureValueMetrics2Command(
                context=request.context,
                dataset_version_subject_email=response_1.feature_view.owner.email,
                dataset_version_subject_display_name=response_1.feature_view.owner.display_name,
                details_contact_name=request.subscriber.name
            )
            outgoing_2 = to_feature_value_reporting_stream_feature_value_metrics2_command(command_2)
            response_2 = await deps.clients.datasets_dataset_version_validation.LintDatasetVersions(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.details
            response.result.details.update(returned_0_0)
            returned_1_0 = response_1.feature_view.code
            if returned_1_0:
                response.feature_value.subject.code = returned_1_0
            returned_1_1 = response_1.result.correlation_id
            if returned_1_1:
                response.feature_value.correlation_id = returned_1_1
            returned_2_0 = response_2.result.status
            if returned_2_0:
                response.result.status = returned_2_0
            returned_2_1 = response_2.dataset_version.source
            if returned_2_1:
                response.feature_value.source = returned_2_1
            return response
