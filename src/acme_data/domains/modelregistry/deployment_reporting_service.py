"""Builds and schedules reports about deployments."""

from __future__ import annotations

from collections.abc import AsyncIterator
from dataclasses import dataclass
from functools import partial
from typing import cast
import logging

from google.protobuf.any_pb2 import Any as AnyMessage
from google.protobuf.json_format import MessageToJson
from google.protobuf.json_format import Parse
import grpc

from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.common.v1 import paging_pb2 as common_v1_paging_pb2
from acme.customers.v1 import (
    consent_record_validation_service_pb2 as customers_v1_consent_record_validation_service_pb2,
)
from acme.customers.v1 import (
    customer_segment_calculation_service_pb2 as customers_v1_customer_segment_calculation_service_pb2,
)
from acme.customers.v1 import customer_service_pb2 as customers_v1_customer_service_pb2
from acme.customers.v1 import customer_validation_service_pb2 as customers_v1_customer_validation_service_pb2
from acme.customers.v1 import customers_pb2 as customers_v1_customers_pb2
from acme.customers.v1 import refs_pb2 as customers_v1_refs_pb2
from acme.featurestore.v1 import feature_view_workflow_service_pb2 as featurestore_v1_feature_view_workflow_service_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.ledger.v1 import ledger_account_service_pb2 as ledger_v1_ledger_account_service_pb2
from acme.lineage.v1 import lineage_edge_workflow_service_pb2 as lineage_v1_lineage_edge_workflow_service_pb2
from acme.metrics.v1 import metric_series_query_service_pb2 as metrics_v1_metric_series_query_service_pb2
from acme.metrics.v1 import metric_series_validation_service_pb2 as metrics_v1_metric_series_validation_service_pb2
from acme.modelregistry.v1 import deployment_reporting_service_pb2 as modelregistry_v1_deployment_reporting_service_pb2
from acme.modelregistry.v1 import (
    deployment_reporting_service_pb2_grpc as modelregistry_v1_deployment_reporting_service_pb2_grpc,
)
from acme.modelregistry.v1 import deployment_sync_service_pb2 as modelregistry_v1_deployment_sync_service_pb2
from acme.modelregistry.v1 import (
    model_version_reporting_service_pb2 as modelregistry_v1_model_version_reporting_service_pb2,
)
from acme.modelregistry.v1 import modelregistry_pb2 as modelregistry_v1_modelregistry_pb2
from acme.modelregistry.v1 import registered_model_service_pb2 as modelregistry_v1_registered_model_service_pb2
from acme.modelregistry.v1 import (
    registered_model_validation_service_pb2 as modelregistry_v1_registered_model_validation_service_pb2,
)

from acme_data.domains.modelregistry.adapters import DeploymentReportingScheduleDeploymentReport0Adapter
from acme_data.domains.modelregistry.adapters import DeploymentReportingScheduleDeploymentReport0Port
from acme_data.domains.modelregistry.adapters import DeploymentReportingScheduleDeploymentReport2Adapter
from acme_data.domains.modelregistry.dependencies import Dependencies
from acme_data.domains.modelregistry.models import DeploymentReportingGenerateDeploymentReport0Command
from acme_data.domains.modelregistry.models import DeploymentReportingGenerateDeploymentReport1Command
from acme_data.domains.modelregistry.models import to_deployment_reporting_generate_deployment_report0_command
from acme_data.domains.modelregistry.models import to_deployment_reporting_generate_deployment_report1_command
from acme_data.platform.rpc import messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_id
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


@dataclass(slots=True)
class DeploymentReportingServicer(
    modelregistry_v1_deployment_reporting_service_pb2_grpc.DeploymentReportingServiceServicer
):
    deps: Dependencies

    @rpc_errors
    @retry_transient
    async def CountDeploymentTotals(
        self, request: modelregistry_v1_deployment_reporting_service_pb2.CountDeploymentTotalsRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_deployment_reporting_service_pb2.CountDeploymentTotalsResponse:
        """Counts deployments by status."""
        return await self.handle_count_deployment_totals(request)

    @rpc_errors
    async def DeleteDeploymentReport(
        self, request: modelregistry_v1_deployment_reporting_service_pb2.DeleteDeploymentReportRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_deployment_reporting_service_pb2.DeleteDeploymentReportResponse:
        """Deletes a deployment."""
        return await self.handle_delete_deployment_report(request)

    @rpc_errors
    @retry_transient
    async def FetchDeploymentReport(
        self, request: modelregistry_v1_deployment_reporting_service_pb2.FetchDeploymentReportRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_deployment_reporting_service_pb2.FetchDeploymentReportResponse:
        """Returns a deployment."""
        return await self.handle_fetch_deployment_report(request)

    @rpc_errors
    async def GenerateDeploymentReport(
        self, request: modelregistry_v1_deployment_reporting_service_pb2.GenerateDeploymentReportRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_deployment_reporting_service_pb2.GenerateDeploymentReportResponse:
        """Generates a deployment."""
        return await self.handle_generate_deployment_report(request)

    @rpc_errors
    @retry_transient
    async def ListDeploymentReports(
        self, request: modelregistry_v1_deployment_reporting_service_pb2.ListDeploymentReportsRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_deployment_reporting_service_pb2.ListDeploymentReportsResponse:
        """Lists deployments a page at a time."""
        return await self.handle_list_deployment_reports(request)

    @rpc_errors
    async def ScheduleDeploymentReport(
        self, request: modelregistry_v1_deployment_reporting_service_pb2.ScheduleDeploymentReportRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_deployment_reporting_service_pb2.ScheduleDeploymentReportResponse:
        """Schedules a deployment."""
        return await self.handle_schedule_deployment_report(request)

    @rpc_errors
    async def ShareDeploymentReport(
        self, request: modelregistry_v1_deployment_reporting_service_pb2.ShareDeploymentReportRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_deployment_reporting_service_pb2.ShareDeploymentReportResponse:
        """Shares a deployment."""
        return await self.handle_share_deployment_report(request)

    @stream_errors
    async def StreamDeploymentMetrics(
        self, request: modelregistry_v1_deployment_reporting_service_pb2.StreamDeploymentMetricsRequest, context: grpc.aio.ServicerContext,
    ) -> AsyncIterator[modelregistry_v1_deployment_reporting_service_pb2.StreamDeploymentMetricsResponse]:
        """Streams the changes of deployments as they happen."""
        response = await self.handle_stream_deployment_metrics(request)
        for item in messages((response,)):
            yield item

    async def handle_count_deployment_totals(
        self,
        request: modelregistry_v1_deployment_reporting_service_pb2.CountDeploymentTotalsRequest
    ) -> modelregistry_v1_deployment_reporting_service_pb2.CountDeploymentTotalsResponse:
        """Counts deployments by status."""
        deps = self.deps
        response = modelregistry_v1_deployment_reporting_service_pb2.CountDeploymentTotalsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CountDeploymentTotals', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'CountDeploymentTotals',
                {'order_by': request.order_by}
            )
            response_0 = metrics_v1_metric_series_query_service_pb2.SummarizeMetricSeriesesResponse()
            outgoing_0 = metrics_v1_metric_series_query_service_pb2.SummarizeMetricSeriesesRequest(
                annotations=dict(request.context.baggage),
                context=request.context,
                details=metrics_v1_metric_series_query_service_pb2.SummarizeMetricSeriesesRequest.Details(
                    filters=dict(request.filter.labels)
                )
            )
            response_0 = await deps.clients.metrics_metric_series_query.SummarizeMetricSerieses(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.result.message = returned_0_0
            return response

    async def handle_delete_deployment_report(
        self,
        request: modelregistry_v1_deployment_reporting_service_pb2.DeleteDeploymentReportRequest
    ) -> modelregistry_v1_deployment_reporting_service_pb2.DeleteDeploymentReportResponse:
        """Deletes a deployment."""
        deps = self.deps
        response = modelregistry_v1_deployment_reporting_service_pb2.DeleteDeploymentReportResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('DeleteDeploymentReport', extra={'fields': {'etag': request.etag}})
            await deps.repository.audit(request.context.tenant_id, 'DeleteDeploymentReport', {'etag': request.etag})
            response_0 = modelregistry_v1_deployment_sync_service_pb2.ListDeploymentConflictsResponse()
            response_1 = metrics_v1_metric_series_query_service_pb2.CountMetricSeriesesResponse()
            response_2 = ledger_v1_ledger_account_service_pb2.ListLedgerAccountsResponse()
            outgoing_0 = modelregistry_v1_deployment_sync_service_pb2.ListDeploymentConflictsRequest(
                context=request.context,
                filter=modelregistry_v1_deployment_sync_service_pb2.ListDeploymentConflictsRequest.Filter(
                    created_after=request.context.deadline,
                    labels=dict(request.context.baggage),
                    owner_id=request.deployment_id
                )
            )
            document_0 = MessageToJson(outgoing_0, preserving_proto_field_name=True)
            outgoing_0 = Parse(
                document_0,
                modelregistry_v1_deployment_sync_service_pb2.ListDeploymentConflictsRequest()
            )
            response_0 = await deps.clients.modelregistry_deployment_sync.ListDeploymentConflicts(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = metrics_v1_metric_series_query_service_pb2.CountMetricSeriesesRequest()
            outgoing_1.context.CopyFrom(request.context)
            outgoing_1.filter.labels.update(dict(response_0.result.details))
            merged_1 = metrics_v1_metric_series_query_service_pb2.CountMetricSeriesesRequest()
            merged_1.MergeFrom(outgoing_1)
            outgoing_1.CopyFrom(merged_1)
            response_1 = await deps.clients.metrics_metric_series_query.CountMetricSerieses(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = ledger_v1_ledger_account_service_pb2.ListLedgerAccountsRequest(
                context=request.context,
                filter=ledger_v1_ledger_account_service_pb2.ListLedgerAccountsRequest.Filter(
                    labels=dict(response_1.result.details)
                )
            )
            envelope_2 = AnyMessage()
            envelope_2.Pack(outgoing_2)
            outgoing_2 = ledger_v1_ledger_account_service_pb2.ListLedgerAccountsRequest()
            if not envelope_2.Unpack(outgoing_2):
                raise ValueError("partner envelope contains the wrong request type")
            response_2 = await deps.clients.ledger_ledger_account.ListLedgerAccounts(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_0)
            returned_1_0 = response_1.result.correlation_id
            if returned_1_0:
                response.result.correlation_id = returned_1_0
            returned_2_0 = response_2.result.reference_ids
            response.result.reference_ids.extend(returned_2_0)
            return response

    async def handle_fetch_deployment_report(
        self,
        request: modelregistry_v1_deployment_reporting_service_pb2.FetchDeploymentReportRequest
    ) -> modelregistry_v1_deployment_reporting_service_pb2.FetchDeploymentReportResponse:
        """Returns a deployment."""
        deps = self.deps
        response = modelregistry_v1_deployment_reporting_service_pb2.FetchDeploymentReportResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('FetchDeploymentReport', extra={'fields': {'domain': 'modelregistry'}})
            await deps.repository.audit(request.context.tenant_id, 'FetchDeploymentReport', {})
            response_0 = customers_v1_customer_segment_calculation_service_pb2.RecalculateCustomerSegmentsResponse()
            outgoing_0 = customers_v1_customer_segment_calculation_service_pb2.RecalculateCustomerSegmentsRequest(
                context=request.context,
                customer_segment=customers_v1_customers_pb2.CustomerSegment(
                    owner=identity_v1_refs_pb2.UserRef(
                        email=request.context.actor.email,
                        user_id=request.context.actor.user_id
                    )
                )
            )
            response_0 = await deps.clients.customers_customer_segment_calculation.RecalculateCustomerSegments(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.status
            if returned_0_0:
                response.result.status = returned_0_0
            echoed_0 = request.deployment_id
            response.deployment.deployment_id = echoed_0
            return response

    async def handle_generate_deployment_report(
        self,
        request: modelregistry_v1_deployment_reporting_service_pb2.GenerateDeploymentReportRequest
    ) -> modelregistry_v1_deployment_reporting_service_pb2.GenerateDeploymentReportResponse:
        """Generates a deployment."""
        deps = self.deps
        response = modelregistry_v1_deployment_reporting_service_pb2.GenerateDeploymentReportResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('GenerateDeploymentReport', extra={'fields': {'deployment_id': request.deployment_id}})
            await deps.repository.audit(
                request.context.tenant_id,
                'GenerateDeploymentReport',
                {'deployment_id': request.deployment_id}
            )
            response_0 = modelregistry_v1_deployment_sync_service_pb2.SyncDeploymentsResponse()
            response_1 = customers_v1_customer_validation_service_pb2.PreviewCustomerResponse()
            response_2 = customers_v1_consent_record_validation_service_pb2.ScoreConsentRecordResponse()
            command_0 = DeploymentReportingGenerateDeploymentReport0Command(
                context=request.context,
                deployment_participants_contact_email=request.context.actor.email
            )
            outgoing_0 = to_deployment_reporting_generate_deployment_report0_command(command_0)
            response_0 = await deps.clients.modelregistry_deployment_sync.SyncDeployments(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            command_1 = DeploymentReportingGenerateDeploymentReport1Command.model_validate(
                {
                    'context': request.context,
                    'customer_audit_etag': response_0.deployment.audit.etag,
                    'customer_relationship_manager_display_name': response_0.deployment.organizer.display_name,
                    'customer_audit_updated_by': response_0.deployment.audit.updated_by
                }
            )
            outgoing_1 = to_deployment_reporting_generate_deployment_report1_command(command_1)
            response_1 = await deps.clients.customers_customer_validation.PreviewCustomer(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = customers_v1_consent_record_validation_service_pb2.ScoreConsentRecordRequest(
                consent_record=customers_v1_customers_pb2.ConsentRecord(
                    subject=customers_v1_refs_pb2.HouseholdRef(
                        display_name=response_1.customer.relationship_manager.display_name
                    )
                ),
                context=request.context,
                details=customers_v1_consent_record_validation_service_pb2.ScoreConsentRecordRequest.Details(
                    destination=common_v1_address_pb2.PostalAddress(
                        country_code=response_1.customer.primary_address.country_code,
                        locality=response_1.customer.primary_address.locality,
                        region=response_1.customer.primary_address.region
                    )
                )
            )
            send_2 = partial(
                deps.clients.customers_consent_record_validation.ScoreConsentRecord,
                timeout=deps.settings.timeout
            )
            response_2 = await send_2(outgoing_2)
            returned_0_0 = response_0.result.details
            response.result.details.update(returned_0_0)
            returned_0_1 = response_0.outcome.message
            if returned_0_1:
                response.result.message = returned_0_1
            returned_1_0 = response_1.result.details
            response.result.details.update(returned_1_0)
            returned_1_1 = response_1.result.status
            if returned_1_1:
                response.result.status = returned_1_1
            returned_2_0 = response_2.result.message
            if returned_2_0:
                response.result.message = returned_2_0
            echoed_0 = request.details.period
            response.period.CopyFrom(echoed_0)
            return response

    async def handle_list_deployment_reports(
        self,
        request: modelregistry_v1_deployment_reporting_service_pb2.ListDeploymentReportsRequest
    ) -> modelregistry_v1_deployment_reporting_service_pb2.ListDeploymentReportsResponse:
        """Lists deployments a page at a time."""
        deps = self.deps
        response = modelregistry_v1_deployment_reporting_service_pb2.ListDeploymentReportsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ListDeploymentReports', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ListDeploymentReports',
                {'order_by': request.order_by}
            )
            response_0 = customers_v1_customer_service_pb2.SearchCustomersResponse()
            response_1 = modelregistry_v1_model_version_reporting_service_pb2.ShareModelVersionReportResponse()
            outgoing_0 = customers_v1_customer_service_pb2.SearchCustomersRequest(
                context=request.context,
                filter=customers_v1_customer_service_pb2.SearchCustomersRequest.Filter(
                    created_after=request.filter.created_after,
                    labels=dict(request.filter.labels)
                ),
                page=common_v1_paging_pb2.PageRequest(page_size=request.page.page_size)
            )
            response_0 = await deps.clients.customers_customer.SearchCustomers(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = modelregistry_v1_model_version_reporting_service_pb2.ShareModelVersionReportRequest()
            outgoing_1.context.CopyFrom(request.context)
            outgoing_1.details.recipient.email = request.context.actor.email
            outgoing_1.details.variables.update(dict(response_0.result.details))
            outgoing_1.annotations.update(dict(request.filter.labels))
            outgoing_1.context.tenant_id = tenant_id.get()
            response_1 = await deps.clients.modelregistry_model_version_reporting.ShareModelVersionReport(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_0)
            returned_0_1 = response_0.page_info.next_page_token
            if returned_0_1:
                response.page_info.next_page_token = returned_0_1
            returned_1_0 = response_1.result.reference_ids
            response.result.reference_ids.extend(returned_1_0)
            return response

    async def handle_schedule_deployment_report(
        self,
        request: modelregistry_v1_deployment_reporting_service_pb2.ScheduleDeploymentReportRequest
    ) -> modelregistry_v1_deployment_reporting_service_pb2.ScheduleDeploymentReportResponse:
        """Schedules a deployment."""
        deps = self.deps
        response = modelregistry_v1_deployment_reporting_service_pb2.ScheduleDeploymentReportResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ScheduleDeploymentReport', extra={'fields': {'deployment_id': request.deployment_id}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ScheduleDeploymentReport',
                {'deployment_id': request.deployment_id}
            )
            response_0 = modelregistry_v1_registered_model_service_pb2.CreateRegisteredModelResponse()
            response_1 = featurestore_v1_feature_view_workflow_service_pb2.PauseFeatureViewWorkflowResponse()
            response_2 = modelregistry_v1_registered_model_validation_service_pb2.LintRegisteredModelsResponse()
            outgoing_0 = modelregistry_v1_registered_model_service_pb2.CreateRegisteredModelRequest(
                context=request.context,
                registered_model=modelregistry_v1_modelregistry_pb2.RegisteredModel(
                    owner=identity_v1_refs_pb2.UserRef(email=request.context.actor.email)
                )
            )
            port_0: DeploymentReportingScheduleDeploymentReport0Port = DeploymentReportingScheduleDeploymentReport0Adapter(
                deps.clients.modelregistry_registered_model,
                deps.settings.timeout
            )
            response_0 = await port_0.execute(outgoing_0)
            outgoing_1 = featurestore_v1_feature_view_workflow_service_pb2.PauseFeatureViewWorkflowRequest()
            outgoing_1.context.CopyFrom(request.context)
            outgoing_1.feature_view.dimensions.length = response_0.registered_model.dimensions.length
            if response_0.registered_model.WhichOneof('locator') == 'address':
                outgoing_1.feature_view.address.region = response_0.registered_model.address.region
            response_1 = await deps.clients.featurestore_feature_view_workflow.PauseFeatureViewWorkflow(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = modelregistry_v1_registered_model_validation_service_pb2.LintRegisteredModelsRequest(
                context=request.context,
                registered_model=modelregistry_v1_modelregistry_pb2.RegisteredModel(
                    audit=common_v1_audit_pb2.AuditInfo(updated_by=response_1.feature_view.audit.updated_by)
                )
            )
            response_2 = await DeploymentReportingScheduleDeploymentReport2Adapter(
                deps.clients.modelregistry_registered_model_validation,
                deps.settings.timeout
            )(outgoing_2)
            returned_0_0 = response_0.result.status
            if returned_0_0:
                response.result.status = returned_0_0
            returned_1_0 = response_1.result.correlation_id
            if returned_1_0:
                response.result.correlation_id = returned_1_0
            returned_1_1 = response_1.result.reference_ids
            response.result.reference_ids.extend(returned_1_1)
            returned_2_0 = response_2.result.reference_ids
            response.result.reference_ids.extend(returned_2_0)
            returned_2_1 = response_2.outcome.status
            if returned_2_1:
                response.result.status = returned_2_1
            echoed_0 = request.details.period
            response.period.CopyFrom(echoed_0)
            return response

    async def handle_share_deployment_report(
        self,
        request: modelregistry_v1_deployment_reporting_service_pb2.ShareDeploymentReportRequest
    ) -> modelregistry_v1_deployment_reporting_service_pb2.ShareDeploymentReportResponse:
        """Shares a deployment."""
        deps = self.deps
        response = modelregistry_v1_deployment_reporting_service_pb2.ShareDeploymentReportResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ShareDeploymentReport', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'ShareDeploymentReport', {'reason': request.reason})
            response_0 = metrics_v1_metric_series_validation_service_pb2.CheckMetricSeriesEligibilityResponse()
            outgoing_0 = metrics_v1_metric_series_validation_service_pb2.CheckMetricSeriesEligibilityRequest(
                context=request.context,
                details=metrics_v1_metric_series_validation_service_pb2.CheckMetricSeriesEligibilityRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(
                        email=request.details.recipient.email,
                        name=request.details.recipient.name,
                        phone=request.details.recipient.phone
                    )
                )
            )
            response_0 = cast(metrics_v1_metric_series_validation_service_pb2.CheckMetricSeriesEligibilityResponse, await deps.bus.request(
                'acme.modelregistry.v1.DeploymentReportingService/ShareDeploymentReport/0', outgoing_0, deps.settings.timeout,
            ))
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.result.message = returned_0_0
            returned_0_1 = response_0.result.correlation_id
            if returned_0_1:
                response.result.correlation_id = returned_0_1
            echoed_0 = request.deployment_id
            response.deployment.deployment_id = echoed_0
            echoed_1 = request.details.recipient.email
            response.deployment.organizer.email = echoed_1
            return response

    async def handle_stream_deployment_metrics(
        self,
        request: modelregistry_v1_deployment_reporting_service_pb2.StreamDeploymentMetricsRequest
    ) -> modelregistry_v1_deployment_reporting_service_pb2.StreamDeploymentMetricsResponse:
        """Streams the changes of deployments as they happen."""
        deps = self.deps
        response = modelregistry_v1_deployment_reporting_service_pb2.StreamDeploymentMetricsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('StreamDeploymentMetrics', extra={'fields': {'max_events': request.max_events}})
            await deps.repository.audit(
                request.context.tenant_id,
                'StreamDeploymentMetrics',
                {'max_events': request.max_events}
            )
            response_0 = lineage_v1_lineage_edge_workflow_service_pb2.ListLineageEdgeWorkflowsResponse()
            response_1 = modelregistry_v1_model_version_reporting_service_pb2.GenerateModelVersionReportResponse()
            outgoing_0 = lineage_v1_lineage_edge_workflow_service_pb2.ListLineageEdgeWorkflowsRequest(
                context=request.context,
                filter=lineage_v1_lineage_edge_workflow_service_pb2.ListLineageEdgeWorkflowsRequest.Filter(
                    region=request.filter.region
                )
            )
            response_0 = await deps.clients.lineage_lineage_edge_workflow.ListLineageEdgeWorkflows(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = modelregistry_v1_model_version_reporting_service_pb2.GenerateModelVersionReportRequest(
                annotations=dict(request.filter.labels),
                context=request.context,
                details=modelregistry_v1_model_version_reporting_service_pb2.GenerateModelVersionReportRequest.Details(
                    filters=dict(response_0.result.details)
                )
            )
            method_name_1 = 'GenerateModelVersionReport'
            response_1 = await getattr(
                deps.clients.modelregistry_model_version_reporting,
                method_name_1
            )(outgoing_1, timeout=deps.settings.timeout)
            returned_0_0 = response_0.result.correlation_id
            if returned_0_0:
                response.result.correlation_id = returned_0_0
            returned_0_1 = response_0.result.details
            response.result.details.update(returned_0_1)
            returned_1_0 = response_1.result.reference_ids
            response.result.reference_ids.extend(returned_1_0)
            echoed_0 = request.filter.region
            response.deployment.location.region = echoed_0
            echoed_1 = request.subscriber.email
            response.deployment.organizer.email = echoed_1
            return response
