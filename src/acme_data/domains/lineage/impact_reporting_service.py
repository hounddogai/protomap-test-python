"""Builds and schedules reports about impacts."""

from __future__ import annotations

from collections.abc import AsyncIterator
from dataclasses import dataclass
from functools import partial
from typing import cast
import logging

from google.protobuf.json_format import MessageToDict
from google.protobuf.json_format import MessageToJson
from google.protobuf.json_format import Parse
from google.protobuf.json_format import ParseDict
import grpc

from acme.assets.v1 import fixed_asset_service_pb2 as assets_v1_fixed_asset_service_pb2
from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.customers.v1 import (
    consent_record_validation_service_pb2 as customers_v1_consent_record_validation_service_pb2,
)
from acme.customers.v1 import customer_validation_service_pb2 as customers_v1_customer_validation_service_pb2
from acme.customers.v1 import customers_pb2 as customers_v1_customers_pb2
from acme.customers.v1 import preference_validation_service_pb2 as customers_v1_preference_validation_service_pb2
from acme.customers.v1 import refs_pb2 as customers_v1_refs_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.lending.v1 import lending_pb2 as lending_v1_lending_pb2
from acme.lending.v1 import loan_application_service_pb2 as lending_v1_loan_application_service_pb2
from acme.lineage.v1 import impact_import_service_pb2 as lineage_v1_impact_import_service_pb2
from acme.lineage.v1 import impact_reporting_service_pb2 as lineage_v1_impact_reporting_service_pb2
from acme.lineage.v1 import impact_reporting_service_pb2_grpc as lineage_v1_impact_reporting_service_pb2_grpc
from acme.lineage.v1 import lineage_node_service_pb2 as lineage_v1_lineage_node_service_pb2
from acme.lineage.v1 import lineage_node_sync_service_pb2 as lineage_v1_lineage_node_sync_service_pb2
from acme.lineage.v1 import lineage_node_sync_service_pb2_grpc as lineage_v1_lineage_node_sync_service_pb2_grpc
from acme.lineage.v1 import lineage_pb2 as lineage_v1_lineage_pb2
from acme.metrics.v1 import dashboard_export_service_pb2 as metrics_v1_dashboard_export_service_pb2
from acme.metrics.v1 import dashboard_sync_service_pb2 as metrics_v1_dashboard_sync_service_pb2
from acme.metrics.v1 import metrics_pb2 as metrics_v1_metrics_pb2
from acme.pipelines.v1 import (
    pipeline_step_calculation_service_pb2 as pipelines_v1_pipeline_step_calculation_service_pb2,
)
from acme.recommendations.v1 import (
    interaction_validation_service_pb2 as recommendations_v1_interaction_validation_service_pb2,
)
from acme.recommendations.v1 import recommendations_pb2 as recommendations_v1_recommendations_pb2
from acme.reviews.v1 import product_review_service_pb2 as reviews_v1_product_review_service_pb2
from acme.venues.v1 import venue_validation_service_pb2 as venues_v1_venue_validation_service_pb2
from acme.venues.v1 import venues_pb2 as venues_v1_venues_pb2

from acme_data.domains.lineage import hooks
from acme_data.domains.lineage.adapters import ImpactReportingStreamImpactMetrics0Adapter
from acme_data.domains.lineage.adapters import ImpactReportingStreamImpactMetrics0Port
from acme_data.domains.lineage.dependencies import Dependencies
from acme_data.domains.lineage.models import ImpactReportingScheduleImpactReport1Command
from acme_data.domains.lineage.models import ImpactReportingScheduleImpactReport2Command
from acme_data.domains.lineage.models import to_impact_reporting_schedule_impact_report1_command
from acme_data.domains.lineage.models import to_impact_reporting_schedule_impact_report2_command
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


@dataclass(slots=True)
class ImpactReportingServicer(lineage_v1_impact_reporting_service_pb2_grpc.ImpactReportingServiceServicer):
    deps: Dependencies

    @rpc_errors
    @retry_transient
    async def CountImpactTotals(
        self, request: lineage_v1_impact_reporting_service_pb2.CountImpactTotalsRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_impact_reporting_service_pb2.CountImpactTotalsResponse:
        """Counts impacts by status."""
        return await self.handle_count_impact_totals(request)

    @rpc_errors
    async def DeleteImpactReport(
        self, request: lineage_v1_impact_reporting_service_pb2.DeleteImpactReportRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_impact_reporting_service_pb2.DeleteImpactReportResponse:
        """Deletes an impact."""
        return await self.handle_delete_impact_report(request)

    @rpc_errors
    @retry_transient
    async def FetchImpactReport(
        self, request: lineage_v1_impact_reporting_service_pb2.FetchImpactReportRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_impact_reporting_service_pb2.FetchImpactReportResponse:
        """Returns an impact."""
        return await self.handle_fetch_impact_report(request)

    @rpc_errors
    async def GenerateImpactReport(
        self, request: lineage_v1_impact_reporting_service_pb2.GenerateImpactReportRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_impact_reporting_service_pb2.GenerateImpactReportResponse:
        """Generates an impact."""
        return await self.handle_generate_impact_report(request)

    @rpc_errors
    @retry_transient
    async def ListImpactReports(
        self, request: lineage_v1_impact_reporting_service_pb2.ListImpactReportsRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_impact_reporting_service_pb2.ListImpactReportsResponse:
        """Lists impacts a page at a time."""
        return await self.handle_list_impact_reports(request)

    @rpc_errors
    async def ScheduleImpactReport(
        self, request: lineage_v1_impact_reporting_service_pb2.ScheduleImpactReportRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_impact_reporting_service_pb2.ScheduleImpactReportResponse:
        """Schedules an impact."""
        return await self.handle_schedule_impact_report(request)

    @rpc_errors
    async def ShareImpactReport(
        self, request: lineage_v1_impact_reporting_service_pb2.ShareImpactReportRequest, context: grpc.aio.ServicerContext,
    ) -> lineage_v1_impact_reporting_service_pb2.ShareImpactReportResponse:
        """Shares an impact."""
        return await self.handle_share_impact_report(request)

    @stream_errors
    async def StreamImpactMetrics(
        self, request: lineage_v1_impact_reporting_service_pb2.StreamImpactMetricsRequest, context: grpc.aio.ServicerContext,
    ) -> AsyncIterator[lineage_v1_impact_reporting_service_pb2.StreamImpactMetricsResponse]:
        """Streams the changes of impacts as they happen."""
        response = await self.handle_stream_impact_metrics(request)
        for item in messages((response,)):
            yield item

    async def handle_count_impact_totals(
        self,
        request: lineage_v1_impact_reporting_service_pb2.CountImpactTotalsRequest
    ) -> lineage_v1_impact_reporting_service_pb2.CountImpactTotalsResponse:
        """Counts impacts by status."""
        deps = self.deps
        response = lineage_v1_impact_reporting_service_pb2.CountImpactTotalsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CountImpactTotals', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(request.context.tenant_id, 'CountImpactTotals', {'order_by': request.order_by})
            response_0 = customers_v1_preference_validation_service_pb2.NormalizePreferenceResponse()
            outgoing_0 = customers_v1_preference_validation_service_pb2.NormalizePreferenceRequest(
                context=request.context,
                details=customers_v1_preference_validation_service_pb2.NormalizePreferenceRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(email=request.context.actor.email)
                ),
                preference=customers_v1_customers_pb2.Preference(
                    owner=identity_v1_refs_pb2.UserRef(user_id=request.context.actor.user_id)
                )
            )
            response_0 = await deps.clients.customers_preference_validation.NormalizePreference(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.details
            response.result.details.update(returned_0_0)
            return response

    async def handle_delete_impact_report(
        self,
        request: lineage_v1_impact_reporting_service_pb2.DeleteImpactReportRequest
    ) -> lineage_v1_impact_reporting_service_pb2.DeleteImpactReportResponse:
        """Deletes an impact."""
        deps = self.deps
        response = lineage_v1_impact_reporting_service_pb2.DeleteImpactReportResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('DeleteImpactReport', extra={'fields': {'etag': request.etag}})
            await deps.repository.audit(request.context.tenant_id, 'DeleteImpactReport', {'etag': request.etag})
            response_0 = customers_v1_consent_record_validation_service_pb2.NormalizeConsentRecordResponse()
            response_1 = recommendations_v1_interaction_validation_service_pb2.NormalizeInteractionResponse()
            outgoing_0 = customers_v1_consent_record_validation_service_pb2.NormalizeConsentRecordRequest(
                context=request.context,
                reason=request.reason
            )
            response_0 = await deps.clients.customers_consent_record_validation.NormalizeConsentRecord(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = recommendations_v1_interaction_validation_service_pb2.NormalizeInteractionRequest(
                context=request.context,
                interaction=recommendations_v1_recommendations_pb2.Interaction(
                    correlation_id=response_0.result.correlation_id,
                    kind=response_0.consent_record.kind
                )
            )
            method_name_1 = 'NormalizeInteraction'
            response_1 = await getattr(
                deps.clients.recommendations_interaction_validation,
                method_name_1
            )(outgoing_1, timeout=deps.settings.timeout)
            returned_0_0 = response_0.consent_record.correlation_id
            if returned_0_0:
                response.result.correlation_id = returned_0_0
            returned_1_0 = response_1.result.correlation_id
            if returned_1_0:
                response.result.correlation_id = returned_1_0
            returned_1_1 = response_1.outcome.message
            if returned_1_1:
                response.result.message = returned_1_1
            return response

    async def handle_fetch_impact_report(
        self,
        request: lineage_v1_impact_reporting_service_pb2.FetchImpactReportRequest
    ) -> lineage_v1_impact_reporting_service_pb2.FetchImpactReportResponse:
        """Returns an impact."""
        deps = self.deps
        response = lineage_v1_impact_reporting_service_pb2.FetchImpactReportResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('FetchImpactReport', extra={'fields': {'domain': 'lineage'}})
            await deps.repository.audit(request.context.tenant_id, 'FetchImpactReport', {})
            response_0 = metrics_v1_dashboard_sync_service_pb2.SyncDashboardsResponse()
            response_1 = venues_v1_venue_validation_service_pb2.ScoreVenueResponse()
            outgoing_0 = metrics_v1_dashboard_sync_service_pb2.SyncDashboardsRequest(
                context=request.context,
                dashboard=metrics_v1_metrics_pb2.Dashboard(
                    audit=common_v1_audit_pb2.AuditInfo(updated_at=request.context.deadline),
                    lines=[metrics_v1_metrics_pb2.DashboardLine(attributes=dict(request.context.baggage))]
                )
            )
            response_0 = await deps.clients.metrics_dashboard_sync.SyncDashboards(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = venues_v1_venue_validation_service_pb2.ScoreVenueRequest(
                context=request.context,
                details=venues_v1_venue_validation_service_pb2.ScoreVenueRequest.Details(
                    destination=common_v1_address_pb2.PostalAddress(
                        lines=list(response_0.dashboard.billing_address.lines)
                    )
                ),
                venue=venues_v1_venues_pb2.Venue(
                    address=common_v1_address_pb2.PostalAddress(
                        postal_code=response_0.dashboard.billing_address.postal_code
                    )
                )
            )
            document_1 = MessageToDict(outgoing_1, preserving_proto_field_name=True)
            outgoing_1 = ParseDict(document_1, venues_v1_venue_validation_service_pb2.ScoreVenueRequest())
            response_1 = await deps.clients.venues_venue_validation.ScoreVenue(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.dashboard.audit.created_at
            returned_0_0_part_1 = response.impact.comments.add()
            if returned_0_0.ListFields():
                returned_0_0_part_1.created_at.MergeFrom(returned_0_0)
            returned_0_1 = response_0.dashboard.audit.etag
            if returned_0_1:
                response.impact.audit.etag = returned_0_1
            returned_1_0 = response_1.result.reference_ids
            response.result.reference_ids.extend(returned_1_0)
            returned_1_1 = response_1.result.details
            response.result.details.update(returned_1_1)
            echoed_0 = request.impact_id
            response.impact.impact_id = echoed_0
            return response

    async def handle_generate_impact_report(
        self,
        request: lineage_v1_impact_reporting_service_pb2.GenerateImpactReportRequest
    ) -> lineage_v1_impact_reporting_service_pb2.GenerateImpactReportResponse:
        """Generates an impact."""
        deps = self.deps
        response = lineage_v1_impact_reporting_service_pb2.GenerateImpactReportResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('GenerateImpactReport', extra={'fields': {'cron': request.details.cron}})
            await deps.repository.audit(
                request.context.tenant_id,
                'GenerateImpactReport',
                {'cron': request.details.cron}
            )
            response_0 = assets_v1_fixed_asset_service_pb2.ListFixedAssetsResponse()
            response_1 = venues_v1_venue_validation_service_pb2.CheckVenueEligibilityResponse()
            outgoing_0 = assets_v1_fixed_asset_service_pb2.ListFixedAssetsRequest(
                context=request.context,
                filter=assets_v1_fixed_asset_service_pb2.ListFixedAssetsRequest.Filter(
                    created_after=request.context.deadline,
                    labels=dict(request.details.filters),
                    owner_id=request.impact_id
                )
            )
            document_0 = MessageToJson(outgoing_0, preserving_proto_field_name=True)
            outgoing_0 = Parse(document_0, assets_v1_fixed_asset_service_pb2.ListFixedAssetsRequest())
            response_0 = await deps.clients.assets_fixed_asset.ListFixedAssets(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = venues_v1_venue_validation_service_pb2.CheckVenueEligibilityRequest()
            outgoing_1.context.CopyFrom(request.context)
            outgoing_1.annotations.update(dict(request.annotations))
            outgoing_1.details.contact.email = request.context.actor.email
            outgoing_1.reason = request.reason
            merged_1 = venues_v1_venue_validation_service_pb2.CheckVenueEligibilityRequest()
            merged_1.MergeFrom(outgoing_1)
            outgoing_1.CopyFrom(merged_1)
            response_1 = await deps.clients.venues_venue_validation.CheckVenueEligibility(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.status
            if returned_0_0:
                response.result.status = returned_0_0
            returned_1_0 = response_1.result.correlation_id
            if returned_1_0:
                response.result.correlation_id = returned_1_0
            returned_1_1 = response_1.result.status
            if returned_1_1:
                response.result.status = returned_1_1
            echoed_0 = request.details.period
            response.period.CopyFrom(echoed_0)
            return response

    async def handle_list_impact_reports(
        self,
        request: lineage_v1_impact_reporting_service_pb2.ListImpactReportsRequest
    ) -> lineage_v1_impact_reporting_service_pb2.ListImpactReportsResponse:
        """Lists impacts a page at a time."""
        deps = self.deps
        response = lineage_v1_impact_reporting_service_pb2.ListImpactReportsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ListImpactReports', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(request.context.tenant_id, 'ListImpactReports', {'order_by': request.order_by})
            response_0 = lineage_v1_impact_import_service_pb2.ValidateImpactImportResponse()
            outgoing_0 = lineage_v1_impact_import_service_pb2.ValidateImpactImportRequest(
                context=request.context,
                details=lineage_v1_impact_import_service_pb2.ValidateImpactImportRequest.Details(
                    locale=request.context.locale
                ),
                impact=lineage_v1_lineage_pb2.Impact(
                    assignee=identity_v1_refs_pb2.UserRef(user_id=request.context.actor.user_id),
                    audit=common_v1_audit_pb2.AuditInfo(updated_at=request.filter.created_after),
                    customer=customers_v1_refs_pb2.CustomerRef(email=request.context.actor.email)
                )
            )
            response_0 = await deps.clients.lineage_impact_import.ValidateImpactImport(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.impact.audit.updated_by
            returned_0_0_part_0 = response.impacts.add()
            if returned_0_0:
                returned_0_0_part_0.audit.updated_by = returned_0_0
            return response

    async def handle_schedule_impact_report(
        self,
        request: lineage_v1_impact_reporting_service_pb2.ScheduleImpactReportRequest
    ) -> lineage_v1_impact_reporting_service_pb2.ScheduleImpactReportResponse:
        """Schedules an impact."""
        deps = self.deps
        response = lineage_v1_impact_reporting_service_pb2.ScheduleImpactReportResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ScheduleImpactReport', extra={'fields': {'impact_id': request.impact_id}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ScheduleImpactReport',
                {'impact_id': request.impact_id}
            )
            response_0 = lineage_v1_lineage_node_sync_service_pb2.PushLineageNodeResponse()
            response_1 = pipelines_v1_pipeline_step_calculation_service_pb2.EstimatePipelineStepResponse()
            response_2 = reviews_v1_product_review_service_pb2.ListProductReviewsResponse()
            response_3 = metrics_v1_dashboard_export_service_pb2.ScheduleDashboardExportResponse()
            outgoing_0 = lineage_v1_lineage_node_sync_service_pb2.PushLineageNodeRequest(
                context=request.context,
                lineage_node=lineage_v1_lineage_pb2.LineageNode(
                    children=[
                        lineage_v1_lineage_pb2.LineageNode(
                            children=[
                                lineage_v1_lineage_pb2.LineageNode(
                                    manager=identity_v1_refs_pb2.UserRef(email=request.context.actor.email)
                                )
                            ]
                        )
                    ]
                )
            )
            registered_0 = cast(
                lineage_v1_lineage_node_sync_service_pb2_grpc.LineageNodeSyncServiceStub,
                deps.clients.registry['acme.lineage.v1.LineageNodeSyncService']
            )
            response_0 = await registered_0.PushLineageNode(outgoing_0, timeout=deps.settings.timeout)
            command_1 = ImpactReportingScheduleImpactReport1Command(
                context=request.context,
                details_destination_country_code=response_0.lineage_node.location.country_code,
                pipeline_step_owner_display_name=response_0.lineage_node.manager.display_name,
                details_destination_region=response_0.lineage_node.location.region,
                details_destination_recipient=response_0.lineage_node.location.recipient
            )
            outgoing_1 = to_impact_reporting_schedule_impact_report1_command(command_1)
            response_1 = await deps.clients.pipelines_pipeline_step_calculation.EstimatePipelineStep(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            command_2 = ImpactReportingScheduleImpactReport2Command.model_validate(
                {
                    'context': request.context,
                    'filter_region': response_0.lineage_node.location.region,
                    'filter_created_after': response_1.pipeline_step.audit.created_at,
                    'filter_owner_id': response_1.pipeline_step.pipeline_step_id,
                    'filter_labels': dict(response_1.result.details)
                }
            )
            outgoing_2 = to_impact_reporting_schedule_impact_report2_command(command_2)
            response_2 = await deps.clients.reviews_product_review.ListProductReviews(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            outgoing_3 = metrics_v1_dashboard_export_service_pb2.ScheduleDashboardExportRequest(
                context=request.context,
                details=metrics_v1_dashboard_export_service_pb2.ScheduleDashboardExportRequest.Details(
                    filters=dict(request.details.filters),
                    period=request.details.period,
                    recipient_emails=list(request.details.recipient_emails)
                ),
                reason=response_1.pipeline_step.block.reason
            )
            send_3 = partial(
                deps.clients.metrics_dashboard_export.ScheduleDashboardExport,
                timeout=deps.settings.timeout
            )
            response_3 = await send_3(outgoing_3)
            returned_0_0 = response_0.result.correlation_id
            if returned_0_0:
                response.result.correlation_id = returned_0_0
            returned_1_0 = response_1.result.correlation_id
            if returned_1_0:
                response.result.correlation_id = returned_1_0
            returned_1_1 = response_1.result.details
            response.result.details.update(returned_1_1)
            returned_2_0 = response_2.result.reference_ids
            response.result.reference_ids.extend(returned_2_0)
            returned_2_1 = response_2.result.message
            if returned_2_1:
                response.result.message = returned_2_1
            returned_3_0 = response_3.result.details
            response.result.details.update(returned_3_0)
            echoed_0 = request.details.period
            response.period.CopyFrom(echoed_0)
            return response

    async def handle_share_impact_report(
        self,
        request: lineage_v1_impact_reporting_service_pb2.ShareImpactReportRequest
    ) -> lineage_v1_impact_reporting_service_pb2.ShareImpactReportResponse:
        """Shares an impact."""
        deps = self.deps
        response = lineage_v1_impact_reporting_service_pb2.ShareImpactReportResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ShareImpactReport', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'ShareImpactReport', {'reason': request.reason})
            response_0 = lending_v1_loan_application_service_pb2.CloneLoanApplicationResponse()
            response_1 = lineage_v1_lineage_node_service_pb2.WatchLineageNodesResponse()
            outgoing_0 = lending_v1_loan_application_service_pb2.CloneLoanApplicationRequest(
                context=request.context,
                loan_application=lending_v1_lending_pb2.LoanApplication(
                    audit=common_v1_audit_pb2.AuditInfo(updated_at=request.context.deadline),
                    counterparty=customers_v1_refs_pb2.CustomerRef(email=request.details.recipient.email),
                    lines=[lending_v1_lending_pb2.LoanApplicationLine(attributes=dict(request.details.variables))]
                )
            )
            response_0 = await hooks.impact_reporting_share_impact_report0(
                deps.clients.lending_loan_application,
                outgoing_0,
                deps.settings.timeout
            )
            outgoing_1 = lineage_v1_lineage_node_service_pb2.WatchLineageNodesRequest(
                context=request.context,
                subscriber=common_v1_contact_pb2.ContactInfo(
                    email=request.details.recipient.email,
                    name=request.details.recipient.name
                )
            )
            async for chunk_1 in deps.clients.lineage_lineage_node.WatchLineageNodes(
                outgoing_1,
                timeout=deps.settings.timeout
            ):
                response_1 = chunk_1
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.result.message = returned_0_0
            echoed_0 = request.impact_id
            response.impact.impact_id = echoed_0
            echoed_1 = request.details.recipient.email
            response.impact.assignee.email = echoed_1
            return response

    async def handle_stream_impact_metrics(
        self,
        request: lineage_v1_impact_reporting_service_pb2.StreamImpactMetricsRequest
    ) -> lineage_v1_impact_reporting_service_pb2.StreamImpactMetricsResponse:
        """Streams the changes of impacts as they happen."""
        deps = self.deps
        response = lineage_v1_impact_reporting_service_pb2.StreamImpactMetricsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('StreamImpactMetrics', extra={'fields': {'max_events': request.max_events}})
            await deps.repository.audit(
                request.context.tenant_id,
                'StreamImpactMetrics',
                {'max_events': request.max_events}
            )
            response_0 = customers_v1_customer_validation_service_pb2.ExplainCustomerDecisionResponse()
            outgoing_0 = customers_v1_customer_validation_service_pb2.ExplainCustomerDecisionRequest(
                context=request.context,
                customer=customers_v1_customers_pb2.Customer(
                    primary_address=common_v1_address_pb2.PostalAddress(region=request.filter.region)
                ),
                details=customers_v1_customer_validation_service_pb2.ExplainCustomerDecisionRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(
                        email=request.subscriber.email,
                        preferred_channel=request.subscriber.preferred_channel
                    )
                )
            )
            port_0: ImpactReportingStreamImpactMetrics0Port = ImpactReportingStreamImpactMetrics0Adapter(
                deps.clients.customers_customer_validation,
                deps.settings.timeout
            )
            response_0 = await port_0.execute(outgoing_0)
            returned_0_0 = response_0.customer.audit.created_by
            if returned_0_0:
                response.impact.audit.created_by = returned_0_0
            returned_0_1 = response_0.result.status
            if returned_0_1:
                response.result.status = returned_0_1
            echoed_0 = request.subscriber.email
            response.impact.requester.email = echoed_0
            echoed_1 = request.subscriber.preferred_channel
            response.impact.requester.preferred_channel = echoed_1
            return response
