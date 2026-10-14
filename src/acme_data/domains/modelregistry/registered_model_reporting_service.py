"""Builds and schedules reports about registered models."""

from __future__ import annotations

from collections.abc import AsyncIterator
from functools import partial
from typing import Any
from typing import cast
import asyncio
import logging

from google.protobuf.json_format import MessageToDict
from google.protobuf.json_format import ParseDict
import grpc

from acme.audit.v1 import audit_event_service_pb2 as audit_v1_audit_event_service_pb2
from acme.audit.v1 import audit_event_service_pb2_grpc as audit_v1_audit_event_service_pb2_grpc
from acme.audit.v1 import audit_pb2 as audit_v1_audit_pb2
from acme.authorization.v1 import access_policy_service_pb2 as authorization_v1_access_policy_service_pb2
from acme.budgeting.v1 import budget_query_service_pb2 as budgeting_v1_budget_query_service_pb2
from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.customers.v1 import (
    consent_record_calculation_service_pb2 as customers_v1_consent_record_calculation_service_pb2,
)
from acme.customers.v1 import (
    customer_segment_calculation_service_pb2 as customers_v1_customer_segment_calculation_service_pb2,
)
from acme.customers.v1 import customers_pb2 as customers_v1_customers_pb2
from acme.customers.v1 import refs_pb2 as customers_v1_refs_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.identity.v1 import user_service_pb2 as identity_v1_user_service_pb2
from acme.lineage.v1 import impact_sync_service_pb2 as lineage_v1_impact_sync_service_pb2
from acme.lineage.v1 import lineage_node_sync_service_pb2 as lineage_v1_lineage_node_sync_service_pb2
from acme.lineage.v1 import lineage_pb2 as lineage_v1_lineage_pb2
from acme.modelregistry.v1 import deployment_import_service_pb2 as modelregistry_v1_deployment_import_service_pb2
from acme.modelregistry.v1 import (
    model_version_calculation_service_pb2 as modelregistry_v1_model_version_calculation_service_pb2,
)
from acme.modelregistry.v1 import model_version_sync_service_pb2 as modelregistry_v1_model_version_sync_service_pb2
from acme.modelregistry.v1 import modelregistry_pb2 as modelregistry_v1_modelregistry_pb2
from acme.modelregistry.v1 import (
    registered_model_reporting_service_pb2 as modelregistry_v1_registered_model_reporting_service_pb2,
)
from acme.modelregistry.v1 import (
    registered_model_reporting_service_pb2_grpc as modelregistry_v1_registered_model_reporting_service_pb2_grpc,
)
from acme.modelregistry.v1 import (
    registered_model_sync_service_pb2 as modelregistry_v1_registered_model_sync_service_pb2,
)

from acme_data.domains.modelregistry import hooks
from acme_data.domains.modelregistry.adapters import RegisteredModelReportingGenerateRegisteredModelReport1Adapter
from acme_data.domains.modelregistry.adapters import RegisteredModelReportingGenerateRegisteredModelReport1Port
from acme_data.domains.modelregistry.dependencies import Dependencies
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import run_steps
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_id
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class RegisteredModelReportingServicer(
    modelregistry_v1_registered_model_reporting_service_pb2_grpc.RegisteredModelReportingServiceServicer
):
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    @retry_transient
    async def CountRegisteredModelTotals(
        self, request: modelregistry_v1_registered_model_reporting_service_pb2.CountRegisteredModelTotalsRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_registered_model_reporting_service_pb2.CountRegisteredModelTotalsResponse:
        """Counts registered models by status."""
        return await self.handle_count_registered_model_totals(request)

    @rpc_errors
    async def DeleteRegisteredModelReport(
        self, request: modelregistry_v1_registered_model_reporting_service_pb2.DeleteRegisteredModelReportRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_registered_model_reporting_service_pb2.DeleteRegisteredModelReportResponse:
        """Deletes a registered model."""
        return await self.handle_delete_registered_model_report(request)

    @rpc_errors
    @retry_transient
    async def FetchRegisteredModelReport(
        self, request: modelregistry_v1_registered_model_reporting_service_pb2.FetchRegisteredModelReportRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_registered_model_reporting_service_pb2.FetchRegisteredModelReportResponse:
        """Returns a registered model."""
        return await self.handle_fetch_registered_model_report(request)

    @rpc_errors
    async def GenerateRegisteredModelReport(
        self, request: modelregistry_v1_registered_model_reporting_service_pb2.GenerateRegisteredModelReportRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_registered_model_reporting_service_pb2.GenerateRegisteredModelReportResponse:
        """Generates a registered model."""
        return await self.handle_generate_registered_model_report(request)

    @rpc_errors
    @retry_transient
    async def ListRegisteredModelReports(
        self, request: modelregistry_v1_registered_model_reporting_service_pb2.ListRegisteredModelReportsRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_registered_model_reporting_service_pb2.ListRegisteredModelReportsResponse:
        """Lists registered models a page at a time."""
        return await self.handle_list_registered_model_reports(request)

    @rpc_errors
    async def ScheduleRegisteredModelReport(
        self, request: modelregistry_v1_registered_model_reporting_service_pb2.ScheduleRegisteredModelReportRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_registered_model_reporting_service_pb2.ScheduleRegisteredModelReportResponse:
        """Schedules a registered model."""
        return await self.handle_schedule_registered_model_report(request)

    @stream_errors
    async def StreamRegisteredModelMetrics(
        self, request: modelregistry_v1_registered_model_reporting_service_pb2.StreamRegisteredModelMetricsRequest, context: grpc.aio.ServicerContext,
    ) -> AsyncIterator[modelregistry_v1_registered_model_reporting_service_pb2.StreamRegisteredModelMetricsResponse]:
        """Streams the changes of registered models as they happen."""
        response = await self.handle_stream_registered_model_metrics(request)
        for item in messages((response,)):
            yield item

    async def handle_count_registered_model_totals(
        self,
        request: modelregistry_v1_registered_model_reporting_service_pb2.CountRegisteredModelTotalsRequest
    ) -> modelregistry_v1_registered_model_reporting_service_pb2.CountRegisteredModelTotalsResponse:
        """Counts registered models by status."""
        deps = self.deps
        response = modelregistry_v1_registered_model_reporting_service_pb2.CountRegisteredModelTotalsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CountRegisteredModelTotals', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'CountRegisteredModelTotals',
                {'order_by': request.order_by}
            )
            response_0 = modelregistry_v1_registered_model_sync_service_pb2.ListRegisteredModelConflictsResponse()
            response_1 = audit_v1_audit_event_service_pb2.CloneAuditEventResponse()
            outgoing_0 = modelregistry_v1_registered_model_sync_service_pb2.ListRegisteredModelConflictsRequest(
                context=request.context,
                filter=modelregistry_v1_registered_model_sync_service_pb2.ListRegisteredModelConflictsRequest.Filter(
                    labels=dict(request.filter.labels),
                    owner_id=request.filter.owner_id
                )
            )
            response_0 = await deps.clients.modelregistry_registered_model_sync.ListRegisteredModelConflicts(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = audit_v1_audit_event_service_pb2.CloneAuditEventRequest(
                audit_event=audit_v1_audit_pb2.AuditEvent(
                    correlation_id=response_0.result.correlation_id,
                    measurements=[audit_v1_audit_pb2.AuditEventMeasurement(observed_at=request.filter.created_after)]
                ),
                context=request.context
            )
            registered_1 = cast(
                audit_v1_audit_event_service_pb2_grpc.AuditEventServiceStub,
                deps.clients.registry['acme.audit.v1.AuditEventService']
            )
            response_1 = await registered_1.CloneAuditEvent(outgoing_1, timeout=deps.settings.timeout)
            returned_0_0 = response_0.result.status
            if returned_0_0:
                response.result.status = returned_0_0
            returned_0_1 = response_0.result.details
            response.result.details.update(returned_0_1)
            returned_1_0 = response_1.result.status
            if returned_1_0:
                response.result.status = returned_1_0
            returned_1_1 = response_1.result.correlation_id
            if returned_1_1:
                response.result.correlation_id = returned_1_1
            return response

    async def handle_delete_registered_model_report(
        self,
        request: modelregistry_v1_registered_model_reporting_service_pb2.DeleteRegisteredModelReportRequest
    ) -> modelregistry_v1_registered_model_reporting_service_pb2.DeleteRegisteredModelReportResponse:
        """Deletes a registered model."""
        deps = self.deps
        response = modelregistry_v1_registered_model_reporting_service_pb2.DeleteRegisteredModelReportResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('DeleteRegisteredModelReport', extra={'fields': {'force': request.force}})
            await deps.repository.audit(
                request.context.tenant_id,
                'DeleteRegisteredModelReport',
                {'force': request.force}
            )
            response_0 = lineage_v1_lineage_node_sync_service_pb2.ListLineageNodeConflictsResponse()
            response_1 = authorization_v1_access_policy_service_pb2.WatchAccessPoliciesResponse()
            response_2 = lineage_v1_impact_sync_service_pb2.PullImpactsResponse()
            response_3 = modelregistry_v1_model_version_calculation_service_pb2.RecalculateModelVersionsResponse()
            outgoing_0 = lineage_v1_lineage_node_sync_service_pb2.ListLineageNodeConflictsRequest(
                context=request.context,
                filter=lineage_v1_lineage_node_sync_service_pb2.ListLineageNodeConflictsRequest.Filter(
                    created_after=request.context.deadline,
                    labels=dict(request.context.baggage),
                    owner_id=request.registered_model_id
                )
            )
            outgoing_2 = lineage_v1_impact_sync_service_pb2.PullImpactsRequest(
                context=request.context,
                impact=lineage_v1_lineage_pb2.Impact(
                    assignee=identity_v1_refs_pb2.UserRef(
                        email=request.context.actor.email,
                        user_id=request.context.actor.user_id
                    ),
                    audit=common_v1_audit_pb2.AuditInfo(etag=request.etag)
                )
            )
            response_0, response_2 = await asyncio.gather(
                deps.clients.lineage_lineage_node_sync.ListLineageNodeConflicts(
                    outgoing_0,
                    timeout=deps.settings.timeout
                ),
                deps.clients.lineage_impact_sync.PullImpacts(outgoing_2, timeout=deps.settings.timeout),
            )
            outgoing_1 = authorization_v1_access_policy_service_pb2.WatchAccessPoliciesRequest(
                context=request.context,
                filter=authorization_v1_access_policy_service_pb2.WatchAccessPoliciesRequest.Filter(
                    labels=dict(response_0.result.details)
                ),
                subscriber=common_v1_contact_pb2.ContactInfo(email=request.context.actor.email)
            )
            async for chunk_1 in deps.clients.authorization_access_policy.WatchAccessPolicies(
                outgoing_1,
                timeout=deps.settings.timeout
            ):
                response_1 = chunk_1
            outgoing_3 = modelregistry_v1_model_version_calculation_service_pb2.RecalculateModelVersionsRequest(
                context=request.context,
                model_version=modelregistry_v1_modelregistry_pb2.ModelVersion(
                    correlation_id=response_2.result.correlation_id,
                    subject=customers_v1_refs_pb2.CustomerRef(
                        customer_id=response_2.impact.customer.customer_id,
                        display_name=response_2.impact.customer.display_name,
                        email=response_2.impact.customer.email
                    )
                )
            )
            response_3 = await hooks.registered_model_reporting_delete_registered_model_report3(
                deps.clients.modelregistry_model_version_calculation,
                outgoing_3,
                deps.settings.timeout
            )
            returned_0_0 = response_0.result.details
            response.result.details.update(returned_0_0)
            returned_0_1 = response_0.result.message
            if returned_0_1:
                response.result.message = returned_0_1
            returned_2_0 = response_2.outcome.status
            if returned_2_0:
                response.result.status = returned_2_0
            returned_2_1 = response_2.outcome.effective_at
            if returned_2_1.ListFields():
                response.effective_at.MergeFrom(returned_2_1)
            returned_3_0 = response_3.result.status
            if returned_3_0:
                response.result.status = returned_3_0
            return response

    async def handle_fetch_registered_model_report(
        self,
        request: modelregistry_v1_registered_model_reporting_service_pb2.FetchRegisteredModelReportRequest
    ) -> modelregistry_v1_registered_model_reporting_service_pb2.FetchRegisteredModelReportResponse:
        """Returns a registered model."""
        deps = self.deps
        response = modelregistry_v1_registered_model_reporting_service_pb2.FetchRegisteredModelReportResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('FetchRegisteredModelReport', extra={'fields': {'locale': request.context.locale}})
            await deps.repository.audit(
                request.context.tenant_id,
                'FetchRegisteredModelReport',
                {'locale': request.context.locale}
            )
            echoed_0 = request.registered_model_id
            response.registered_model.registered_model_id = echoed_0
            return response

    async def handle_generate_registered_model_report(
        self,
        request: modelregistry_v1_registered_model_reporting_service_pb2.GenerateRegisteredModelReportRequest
    ) -> modelregistry_v1_registered_model_reporting_service_pb2.GenerateRegisteredModelReportResponse:
        """Generates a registered model."""
        deps = self.deps
        response = modelregistry_v1_registered_model_reporting_service_pb2.GenerateRegisteredModelReportResponse()
        with tenant_scope(request.context.tenant_id):
            log.info(
                'GenerateRegisteredModelReport',
                extra={'fields': {'registered_model_id': request.registered_model_id}}
            )
            await deps.repository.audit(
                request.context.tenant_id,
                'GenerateRegisteredModelReport',
                {'registered_model_id': request.registered_model_id}
            )
            response_0 = modelregistry_v1_deployment_import_service_pb2.RetryDeploymentImportResponse()
            response_1 = modelregistry_v1_registered_model_sync_service_pb2.ReconcileRegisteredModelsResponse()
            response_2 = customers_v1_consent_record_calculation_service_pb2.CompareConsentRecordOptionsResponse()
            outgoing_0 = modelregistry_v1_deployment_import_service_pb2.RetryDeploymentImportRequest()
            outgoing_0.context.CopyFrom(request.context)
            outgoing_0.reason = request.reason
            outgoing_0.deployment.organizer.user_id = request.context.actor.user_id
            outgoing_0.context.tenant_id = tenant_id.get()
            response_0 = await deps.clients.modelregistry_deployment_import.RetryDeploymentImport(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = modelregistry_v1_registered_model_sync_service_pb2.ReconcileRegisteredModelsRequest(
                context=request.context,
                registered_model=modelregistry_v1_modelregistry_pb2.RegisteredModel(
                    address=common_v1_address_pb2.PostalAddress(
                        country_code=response_0.deployment.location.country_code
                    ),
                    audit=common_v1_audit_pb2.AuditInfo(updated_at=response_0.deployment.audit.updated_at)
                )
            )
            port_1: RegisteredModelReportingGenerateRegisteredModelReport1Port = RegisteredModelReportingGenerateRegisteredModelReport1Adapter(
                deps.clients.modelregistry_registered_model_sync,
                deps.settings.timeout
            )
            response_1 = await port_1.execute(outgoing_1)
            outgoing_2 = customers_v1_consent_record_calculation_service_pb2.CompareConsentRecordOptionsRequest(
                consent_record=customers_v1_customers_pb2.ConsentRecord(
                    measurements=[
                        customers_v1_customers_pb2.ConsentRecordMeasurement(
                            unit=response_1.registered_model.dimensions.unit
                        )
                    ]
                ),
                context=request.context,
                details=customers_v1_consent_record_calculation_service_pb2.CompareConsentRecordOptionsRequest.Details(
                    destination=common_v1_address_pb2.PostalAddress(
                        country_code=response_1.registered_model.address.country_code,
                        region=response_0.deployment.location.region
                    )
                )
            )
            steps_2 = [
                partial(
                    deps.clients.customers_consent_record_calculation.CompareConsentRecordOptions,
                    outgoing_2,
                    timeout=deps.settings.timeout
                )
            ]
            results_2 = await run_steps(steps_2)
            response_2 = results_2[-1]
            returned_0_0 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_0)
            returned_1_0 = response_1.outcome.message
            if returned_1_0:
                response.result.message = returned_1_0
            returned_2_0 = response_2.result.message
            if returned_2_0:
                response.result.message = returned_2_0
            echoed_0 = request.details.period
            response.period.CopyFrom(echoed_0)
            return response

    async def handle_list_registered_model_reports(
        self,
        request: modelregistry_v1_registered_model_reporting_service_pb2.ListRegisteredModelReportsRequest
    ) -> modelregistry_v1_registered_model_reporting_service_pb2.ListRegisteredModelReportsResponse:
        """Lists registered models a page at a time."""
        deps = self.deps
        response = modelregistry_v1_registered_model_reporting_service_pb2.ListRegisteredModelReportsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ListRegisteredModelReports', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ListRegisteredModelReports',
                {'order_by': request.order_by}
            )
            response_0 = budgeting_v1_budget_query_service_pb2.SummarizeBudgetsResponse()
            outgoing_0 = budgeting_v1_budget_query_service_pb2.SummarizeBudgetsRequest(
                annotations=dict(request.filter.labels),
                context=request.context,
                details=budgeting_v1_budget_query_service_pb2.SummarizeBudgetsRequest.Details(
                    filters=dict(request.context.baggage)
                )
            )
            response_0 = await deps.clients.budgeting_budget_query.SummarizeBudgets(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_0)
            returned_0_1 = response_0.result.correlation_id
            if returned_0_1:
                response.result.correlation_id = returned_0_1
            return response

    async def handle_schedule_registered_model_report(
        self,
        request: modelregistry_v1_registered_model_reporting_service_pb2.ScheduleRegisteredModelReportRequest
    ) -> modelregistry_v1_registered_model_reporting_service_pb2.ScheduleRegisteredModelReportResponse:
        """Schedules a registered model."""
        deps = self.deps
        response = modelregistry_v1_registered_model_reporting_service_pb2.ScheduleRegisteredModelReportResponse()
        with tenant_scope(request.context.tenant_id):
            log.info(
                'ScheduleRegisteredModelReport',
                extra={'fields': {'registered_model_id': request.registered_model_id}}
            )
            await deps.repository.audit(
                request.context.tenant_id,
                'ScheduleRegisteredModelReport',
                {'registered_model_id': request.registered_model_id}
            )
            response_0 = modelregistry_v1_registered_model_sync_service_pb2.SyncRegisteredModelsResponse()
            response_1 = identity_v1_user_service_pb2.BatchGetUsersResponse()
            outgoing_0 = modelregistry_v1_registered_model_sync_service_pb2.SyncRegisteredModelsRequest(
                annotations=dict(request.annotations),
                context=request.context,
                reason=request.reason,
                registered_model=modelregistry_v1_modelregistry_pb2.RegisteredModel(
                    owner=identity_v1_refs_pb2.UserRef(email=request.context.actor.email)
                )
            )
            response_0 = cast(modelregistry_v1_registered_model_sync_service_pb2.SyncRegisteredModelsResponse, await deps.bus.request(
                'acme.modelregistry.v1.RegisteredModelReportingService/ScheduleRegisteredModelReport/0', outgoing_0, deps.settings.timeout,
            ))
            outgoing_1 = identity_v1_user_service_pb2.BatchGetUsersRequest(context=request.context)
            response_1 = await deps.clients.identity_user.BatchGetUsers(outgoing_1, timeout=deps.settings.timeout)
            returned_0_0 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_0)
            returned_1_0 = response_1.result.message
            if returned_1_0:
                response.result.message = returned_1_0
            echoed_0 = request.details.period
            response.period.CopyFrom(echoed_0)
            return response

    async def handle_stream_registered_model_metrics(
        self,
        request: modelregistry_v1_registered_model_reporting_service_pb2.StreamRegisteredModelMetricsRequest
    ) -> modelregistry_v1_registered_model_reporting_service_pb2.StreamRegisteredModelMetricsResponse:
        """Streams the changes of registered models as they happen."""
        deps = self.deps
        response = modelregistry_v1_registered_model_reporting_service_pb2.StreamRegisteredModelMetricsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('StreamRegisteredModelMetrics', extra={'fields': {'max_events': request.max_events}})
            await deps.repository.audit(
                request.context.tenant_id,
                'StreamRegisteredModelMetrics',
                {'max_events': request.max_events}
            )
            response_0 = modelregistry_v1_model_version_sync_service_pb2.PullModelVersionsResponse()
            response_1 = customers_v1_customer_segment_calculation_service_pb2.CompareCustomerSegmentOptionsResponse()
            response_2 = modelregistry_v1_registered_model_sync_service_pb2.PushRegisteredModelResponse()
            outgoing_0 = modelregistry_v1_model_version_sync_service_pb2.PullModelVersionsRequest(
                context=request.context,
                model_version=modelregistry_v1_modelregistry_pb2.ModelVersion(
                    measurements=[
                        modelregistry_v1_modelregistry_pb2.ModelVersionMeasurement(
                            observed_at=request.filter.created_after
                        )
                    ],
                    subject=customers_v1_refs_pb2.CustomerRef(email=request.subscriber.email)
                )
            )
            method_name_0 = 'PullModelVersions'
            response_0 = await getattr(
                deps.clients.modelregistry_model_version_sync,
                method_name_0
            )(outgoing_0, timeout=deps.settings.timeout)
            fields_1: dict[str, Any] = {
                'context': request.context,
                'customer_segment': {
                    'owner': {
                        'display_name': response_0.model_version.subject.display_name,
                        'email': response_0.model_version.subject.email
                    }
                }
            }
            outgoing_1 = customers_v1_customer_segment_calculation_service_pb2.CompareCustomerSegmentOptionsRequest(**fields_1)
            response_1 = await deps.clients.customers_customer_segment_calculation.CompareCustomerSegmentOptions(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = modelregistry_v1_registered_model_sync_service_pb2.PushRegisteredModelRequest(
                context=request.context,
                reason=response_1.customer_segment.block.reason,
                registered_model=modelregistry_v1_modelregistry_pb2.RegisteredModel(
                    audit=common_v1_audit_pb2.AuditInfo(updated_at=response_1.customer_segment.audit.updated_at),
                    components={
                        'primary': modelregistry_v1_modelregistry_pb2.RegisteredModelComponent(
                            description=response_1.customer_segment.description
                        )
                    },
                    owner=identity_v1_refs_pb2.UserRef(email=response_1.customer_segment.owner.email)
                )
            )
            document_2 = MessageToDict(outgoing_2, preserving_proto_field_name=True)
            outgoing_2 = ParseDict(
                document_2,
                modelregistry_v1_registered_model_sync_service_pb2.PushRegisteredModelRequest()
            )
            response_2 = await deps.clients.modelregistry_registered_model_sync.PushRegisteredModel(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_0)
            returned_0_1 = response_0.model_version.correlation_id
            if returned_0_1:
                response.result.correlation_id = returned_0_1
            returned_1_0 = response_1.result.details
            response.result.details.update(returned_1_0)
            returned_1_1 = response_1.result.correlation_id
            if returned_1_1:
                response.result.correlation_id = returned_1_1
            returned_2_0 = response_2.registered_model.dimensions.length
            if returned_2_0:
                response.registered_model.dimensions.length = returned_2_0
            returned_2_1 = response_2.registered_model.code
            if returned_2_1:
                response.registered_model.code = returned_2_1
            echoed_0 = request.subscriber.email
            response.registered_model.owner.email = echoed_0
            return response
