"""Functional operations behind ModelVersionReportingService."""

from __future__ import annotations

from functools import partial
from typing import cast
import logging

from google.protobuf.json_format import MessageToJson
from google.protobuf.json_format import Parse

from acme.audit.v1 import audit_event_query_service_pb2 as audit_v1_audit_event_query_service_pb2
from acme.authorization.v1 import access_policy_service_pb2 as authorization_v1_access_policy_service_pb2
from acme.authorization.v1 import (
    access_policy_validation_service_pb2 as authorization_v1_access_policy_validation_service_pb2,
)
from acme.authorization.v1 import authorization_pb2 as authorization_v1_authorization_pb2
from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.customers.v1 import customer_query_service_pb2 as customers_v1_customer_query_service_pb2
from acme.customers.v1 import refs_pb2 as customers_v1_refs_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.modelregistry.v1 import deployment_import_service_pb2 as modelregistry_v1_deployment_import_service_pb2
from acme.modelregistry.v1 import deployment_sync_service_pb2 as modelregistry_v1_deployment_sync_service_pb2
from acme.modelregistry.v1 import (
    deployment_validation_service_pb2 as modelregistry_v1_deployment_validation_service_pb2,
)
from acme.modelregistry.v1 import (
    deployment_validation_service_pb2_grpc as modelregistry_v1_deployment_validation_service_pb2_grpc,
)
from acme.modelregistry.v1 import (
    model_version_calculation_service_pb2 as modelregistry_v1_model_version_calculation_service_pb2,
)
from acme.modelregistry.v1 import (
    model_version_reporting_service_pb2 as modelregistry_v1_model_version_reporting_service_pb2,
)
from acme.modelregistry.v1 import model_version_sync_service_pb2 as modelregistry_v1_model_version_sync_service_pb2
from acme.modelregistry.v1 import modelregistry_pb2 as modelregistry_v1_modelregistry_pb2
from acme.modelregistry.v1 import (
    registered_model_reporting_service_pb2 as modelregistry_v1_registered_model_reporting_service_pb2,
)
from acme.modelregistry.v1 import (
    registered_model_validation_service_pb2 as modelregistry_v1_registered_model_validation_service_pb2,
)

from acme_data.domains.modelregistry import hooks
from acme_data.domains.modelregistry.dependencies import Dependencies
from acme_data.domains.modelregistry.models import ModelVersionReportingShareModelVersionReport2Command
from acme_data.domains.modelregistry.models import to_model_version_reporting_share_model_version_report2_command
from acme_data.platform.rpc import async_messages
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


async def handle_count_model_version_totals(
    deps: Dependencies,
    request: modelregistry_v1_model_version_reporting_service_pb2.CountModelVersionTotalsRequest
) -> modelregistry_v1_model_version_reporting_service_pb2.CountModelVersionTotalsResponse:
    """Counts model versions by status."""
    response = modelregistry_v1_model_version_reporting_service_pb2.CountModelVersionTotalsResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('CountModelVersionTotals', extra={'fields': {'order_by': request.order_by}})
        await deps.repository.audit(
            request.context.tenant_id,
            'CountModelVersionTotals',
            {'order_by': request.order_by}
        )
        return response


async def handle_fetch_model_version_report(
    deps: Dependencies,
    request: modelregistry_v1_model_version_reporting_service_pb2.FetchModelVersionReportRequest
) -> modelregistry_v1_model_version_reporting_service_pb2.FetchModelVersionReportResponse:
    """Returns a model version."""
    response = modelregistry_v1_model_version_reporting_service_pb2.FetchModelVersionReportResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('FetchModelVersionReport', extra={'fields': {'domain': 'modelregistry'}})
        await deps.repository.audit(request.context.tenant_id, 'FetchModelVersionReport', {})
        response_0 = modelregistry_v1_registered_model_reporting_service_pb2.GenerateRegisteredModelReportResponse()
        outgoing_0 = modelregistry_v1_registered_model_reporting_service_pb2.GenerateRegisteredModelReportRequest(
            context=request.context,
            details=modelregistry_v1_registered_model_reporting_service_pb2.GenerateRegisteredModelReportRequest.Details(
                filters=dict(request.context.baggage)
            )
        )
        response_0 = await deps.clients.modelregistry_registered_model_reporting.GenerateRegisteredModelReport(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.result.details
        response.result.details.update(returned_0_0)
        echoed_0 = request.model_version_id
        response.model_version.model_version_id = echoed_0
        return response


async def handle_generate_model_version_report(
    deps: Dependencies,
    request: modelregistry_v1_model_version_reporting_service_pb2.GenerateModelVersionReportRequest
) -> modelregistry_v1_model_version_reporting_service_pb2.GenerateModelVersionReportResponse:
    """Generates a model version."""
    response = modelregistry_v1_model_version_reporting_service_pb2.GenerateModelVersionReportResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('GenerateModelVersionReport', extra={'fields': {'cron': request.details.cron}})
        await deps.repository.audit(
            request.context.tenant_id,
            'GenerateModelVersionReport',
            {'cron': request.details.cron}
        )
        response_0 = modelregistry_v1_model_version_sync_service_pb2.ReconcileModelVersionsResponse()
        response_1 = modelregistry_v1_deployment_sync_service_pb2.ListDeploymentConflictsResponse()
        response_2 = customers_v1_customer_query_service_pb2.ExportCustomersResponse()
        outgoing_0 = modelregistry_v1_model_version_sync_service_pb2.ReconcileModelVersionsRequest(
            annotations=dict(request.annotations),
            context=request.context,
            model_version=modelregistry_v1_modelregistry_pb2.ModelVersion(
                model_version_id=request.model_version_id,
                subject=customers_v1_refs_pb2.CustomerRef(email=request.context.actor.email)
            ),
            reason=request.reason
        )
        response_0 = await deps.clients.modelregistry_model_version_sync.ReconcileModelVersions(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = modelregistry_v1_deployment_sync_service_pb2.ListDeploymentConflictsRequest(
            context=request.context,
            filter=modelregistry_v1_deployment_sync_service_pb2.ListDeploymentConflictsRequest.Filter(
                created_after=response_0.outcome.effective_at,
                labels=dict(request.details.filters),
                owner_id=response_0.outcome.reference_id
            )
        )
        method_name_1 = 'ListDeploymentConflicts'
        response_1 = await getattr(
            deps.clients.modelregistry_deployment_sync,
            method_name_1
        )(outgoing_1, timeout=deps.settings.timeout)
        outgoing_2 = customers_v1_customer_query_service_pb2.ExportCustomersRequest(
            context=request.context,
            filter=customers_v1_customer_query_service_pb2.ExportCustomersRequest.Filter(
                created_after=response_0.outcome.effective_at
            ),
            format=request.details.format
        )
        async for chunk_2 in deps.clients.customers_customer_query.ExportCustomers(
            outgoing_2,
            timeout=deps.settings.timeout
        ):
            response_2 = chunk_2
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


async def handle_list_model_version_reports(
    deps: Dependencies,
    request: modelregistry_v1_model_version_reporting_service_pb2.ListModelVersionReportsRequest
) -> modelregistry_v1_model_version_reporting_service_pb2.ListModelVersionReportsResponse:
    """Lists model versions a page at a time."""
    response = modelregistry_v1_model_version_reporting_service_pb2.ListModelVersionReportsResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('ListModelVersionReports', extra={'fields': {'page_size': request.page.page_size}})
        await deps.repository.audit(
            request.context.tenant_id,
            'ListModelVersionReports',
            {'page_size': request.page.page_size}
        )
        response_0 = audit_v1_audit_event_query_service_pb2.BrowseAuditEventsResponse()
        response_1 = authorization_v1_access_policy_service_pb2.ListAccessPoliciesResponse()
        outgoing_0 = audit_v1_audit_event_query_service_pb2.BrowseAuditEventsRequest(
            context=request.context,
            filter=audit_v1_audit_event_query_service_pb2.BrowseAuditEventsRequest.Filter(
                labels=dict(request.filter.labels),
                owner_id=request.filter.owner_id,
                query=request.filter.query,
                region=request.filter.region
            )
        )
        response_0 = await deps.clients.audit_audit_event_query.BrowseAuditEvents(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = authorization_v1_access_policy_service_pb2.ListAccessPoliciesRequest(
            context=request.context,
            filter=authorization_v1_access_policy_service_pb2.ListAccessPoliciesRequest.Filter(
                owner_id=request.filter.owner_id,
                region=request.filter.region
            ),
            order_by=request.order_by
        )
        document_1 = MessageToJson(outgoing_1, preserving_proto_field_name=True)
        outgoing_1 = Parse(document_1, authorization_v1_access_policy_service_pb2.ListAccessPoliciesRequest())
        response_1 = await deps.clients.authorization_access_policy.ListAccessPolicies(
            outgoing_1,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.page_info.next_page_token
        if returned_0_0:
            response.page_info.next_page_token = returned_0_0
        returned_1_0 = response_1.result.reference_ids
        response.result.reference_ids.extend(returned_1_0)
        returned_1_1 = response_1.result.message
        if returned_1_1:
            response.result.message = returned_1_1
        return response


async def handle_schedule_model_version_report(
    deps: Dependencies,
    request: modelregistry_v1_model_version_reporting_service_pb2.ScheduleModelVersionReportRequest
) -> modelregistry_v1_model_version_reporting_service_pb2.ScheduleModelVersionReportResponse:
    """Schedules a model version."""
    response = modelregistry_v1_model_version_reporting_service_pb2.ScheduleModelVersionReportResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('ScheduleModelVersionReport', extra={'fields': {'model_version_id': request.model_version_id}})
        await deps.repository.audit(
            request.context.tenant_id,
            'ScheduleModelVersionReport',
            {'model_version_id': request.model_version_id}
        )
        response_0 = authorization_v1_access_policy_validation_service_pb2.ScoreAccessPolicyResponse()
        outgoing_0 = authorization_v1_access_policy_validation_service_pb2.ScoreAccessPolicyRequest(
            access_policy=authorization_v1_authorization_pb2.AccessPolicy(
                owner=identity_v1_refs_pb2.UserRef(user_id=request.context.actor.user_id)
            ),
            annotations=dict(request.annotations),
            context=request.context,
            reason=request.reason
        )
        response_0 = await deps.clients.authorization_access_policy_validation.ScoreAccessPolicy(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.result.correlation_id
        if returned_0_0:
            response.result.correlation_id = returned_0_0
        echoed_0 = request.details.period
        response.period.CopyFrom(echoed_0)
        return response


async def handle_share_model_version_report(
    deps: Dependencies,
    request: modelregistry_v1_model_version_reporting_service_pb2.ShareModelVersionReportRequest
) -> modelregistry_v1_model_version_reporting_service_pb2.ShareModelVersionReportResponse:
    """Shares a model version."""
    response = modelregistry_v1_model_version_reporting_service_pb2.ShareModelVersionReportResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('ShareModelVersionReport', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'ShareModelVersionReport', {'reason': request.reason})
        response_0 = modelregistry_v1_deployment_import_service_pb2.ListDeploymentImportsResponse()
        response_1 = modelregistry_v1_deployment_validation_service_pb2.NormalizeDeploymentResponse()
        response_2 = modelregistry_v1_registered_model_validation_service_pb2.ValidateRegisteredModelResponse()
        outgoing_0 = modelregistry_v1_deployment_import_service_pb2.ListDeploymentImportsRequest(
            context=request.context,
            filter=modelregistry_v1_deployment_import_service_pb2.ListDeploymentImportsRequest.Filter(
                labels=dict(request.annotations),
                owner_id=request.model_version_id
            )
        )
        response_0 = await deps.clients.modelregistry_deployment_import.ListDeploymentImports(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = modelregistry_v1_deployment_validation_service_pb2.NormalizeDeploymentRequest(
            context=request.context,
            deployment=modelregistry_v1_modelregistry_pb2.Deployment(
                participants=[
                    modelregistry_v1_modelregistry_pb2.DeploymentParticipant(
                        contact=common_v1_contact_pb2.ContactInfo(
                            name=request.details.recipient.name,
                            phone=request.details.recipient.phone,
                            preferred_channel=request.details.recipient.preferred_channel
                        )
                    )
                ]
            )
        )
        registered_1 = cast(
            modelregistry_v1_deployment_validation_service_pb2_grpc.DeploymentValidationServiceStub,
            deps.clients.registry['acme.modelregistry.v1.DeploymentValidationService']
        )
        response_1 = await registered_1.NormalizeDeployment(outgoing_1, timeout=deps.settings.timeout)
        command_2 = ModelVersionReportingShareModelVersionReport2Command(
            context=request.context,
            registered_model_address_postal_code=response_1.deployment.location.postal_code,
            registered_model_audit_created_at=response_1.deployment.audit.created_at,
            details_contact_name=request.details.recipient.name,
            registered_model_audit_updated_at=response_1.deployment.audit.updated_at
        )
        outgoing_2 = to_model_version_reporting_share_model_version_report2_command(command_2)
        response_2 = await deps.clients.modelregistry_registered_model_validation.ValidateRegisteredModel(
            outgoing_2,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.result.message
        if returned_0_0:
            response.outcome.message = returned_0_0
        returned_1_0 = response_1.result.message
        if returned_1_0:
            response.outcome.message = returned_1_0
        returned_1_1 = response_1.outcome.effective_at
        if returned_1_1.ListFields():
            response.outcome.effective_at.MergeFrom(returned_1_1)
        returned_2_0 = response_2.result.message
        if returned_2_0:
            response.outcome.message = returned_2_0
        returned_2_1 = response_2.registered_model.owner.email
        if returned_2_1:
            response.model_version.subject.email = returned_2_1
        echoed_0 = request.model_version_id
        response.model_version.model_version_id = echoed_0
        return response


async def handle_stream_model_version_metrics(
    deps: Dependencies,
    request: modelregistry_v1_model_version_reporting_service_pb2.StreamModelVersionMetricsRequest
) -> modelregistry_v1_model_version_reporting_service_pb2.StreamModelVersionMetricsResponse:
    """Streams the changes of model versions as they happen."""
    response = modelregistry_v1_model_version_reporting_service_pb2.StreamModelVersionMetricsResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('StreamModelVersionMetrics', extra={'fields': {'max_events': request.max_events}})
        await deps.repository.audit(
            request.context.tenant_id,
            'StreamModelVersionMetrics',
            {'max_events': request.max_events}
        )
        response_0 = modelregistry_v1_model_version_calculation_service_pb2.EstimateModelVersionResponse()
        response_1 = modelregistry_v1_registered_model_reporting_service_pb2.CountRegisteredModelTotalsResponse()
        response_2 = modelregistry_v1_model_version_sync_service_pb2.ReconcileModelVersionsResponse()
        outgoing_0 = modelregistry_v1_model_version_calculation_service_pb2.EstimateModelVersionRequest(
            context=request.context,
            details=modelregistry_v1_model_version_calculation_service_pb2.EstimateModelVersionRequest.Details(
                destination=common_v1_address_pb2.PostalAddress(region=request.filter.region)
            ),
            model_version=modelregistry_v1_modelregistry_pb2.ModelVersion(
                correlation_id=request.filter.owner_id,
                measurements=[
                    modelregistry_v1_modelregistry_pb2.ModelVersionMeasurement(observed_at=request.filter.created_after)
                ],
                subject=customers_v1_refs_pb2.CustomerRef(email=request.subscriber.email)
            )
        )
        response_0 = await deps.clients.modelregistry_model_version_calculation.EstimateModelVersion(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = modelregistry_v1_registered_model_reporting_service_pb2.CountRegisteredModelTotalsRequest(
            context=request.context,
            filter=modelregistry_v1_registered_model_reporting_service_pb2.CountRegisteredModelTotalsRequest.Filter(
                owner_id=request.filter.owner_id,
                region=request.filter.region
            )
        )
        send_1 = partial(
            deps.clients.modelregistry_registered_model_reporting.CountRegisteredModelTotals,
            timeout=deps.settings.timeout
        )
        response_1 = await send_1(outgoing_1)
        outgoing_2 = modelregistry_v1_model_version_sync_service_pb2.ReconcileModelVersionsRequest(
            context=request.context,
            model_version=modelregistry_v1_modelregistry_pb2.ModelVersion(
                kind=response_0.model_version.kind,
                occurred_at=response_0.model_version.occurred_at,
                subject=customers_v1_refs_pb2.CustomerRef(display_name=response_0.model_version.subject.display_name)
            )
        )
        response_2 = await hooks.model_version_reporting_stream_model_version_metrics2(
            deps.clients.modelregistry_model_version_sync,
            outgoing_2,
            deps.settings.timeout
        )
        returned_0_0 = response_0.model_version.correlation_id
        if returned_0_0:
            response.result.correlation_id = returned_0_0
        returned_1_0 = response_1.result.status
        if returned_1_0:
            response.result.status = returned_1_0
        returned_1_1 = response_1.result.reference_ids
        response.result.reference_ids.extend(returned_1_1)
        returned_2_0 = response_2.model_version.subject.display_name
        if returned_2_0:
            response.model_version.subject.display_name = returned_2_0
        returned_2_1 = response_2.model_version.subject.customer_id
        if returned_2_1:
            response.model_version.subject.customer_id = returned_2_1
        echoed_0 = request.subscriber.email
        response.model_version.subject.email = echoed_0
        return response
