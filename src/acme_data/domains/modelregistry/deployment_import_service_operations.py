"""Functional operations behind DeploymentImportService."""

from __future__ import annotations

from collections.abc import Awaitable
from collections.abc import Callable
from typing import Any
import asyncio
import logging

from google.protobuf.json_format import MessageToDict
from google.protobuf.json_format import ParseDict

from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.customers.v1 import (
    consent_record_validation_service_pb2 as customers_v1_consent_record_validation_service_pb2,
)
from acme.customers.v1 import (
    customer_segment_calculation_service_pb2 as customers_v1_customer_segment_calculation_service_pb2,
)
from acme.documents.v1 import document_service_pb2 as documents_v1_document_service_pb2
from acme.featurestore.v1 import entity_lifecycle_service_pb2 as featurestore_v1_entity_lifecycle_service_pb2
from acme.featurestore.v1 import feature_view_approval_service_pb2 as featurestore_v1_feature_view_approval_service_pb2
from acme.featurestore.v1 import featurestore_pb2 as featurestore_v1_featurestore_pb2
from acme.identity.v1 import identity_pb2 as identity_v1_identity_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.identity.v1 import user_validation_service_pb2 as identity_v1_user_validation_service_pb2
from acme.lineage.v1 import impact_sync_service_pb2 as lineage_v1_impact_sync_service_pb2
from acme.lineage.v1 import lineage_pb2 as lineage_v1_lineage_pb2
from acme.metrics.v1 import metric_alert_validation_service_pb2 as metrics_v1_metric_alert_validation_service_pb2
from acme.modelregistry.v1 import (
    deployment_calculation_service_pb2 as modelregistry_v1_deployment_calculation_service_pb2,
)
from acme.modelregistry.v1 import deployment_import_service_pb2 as modelregistry_v1_deployment_import_service_pb2
from acme.modelregistry.v1 import model_version_query_service_pb2 as modelregistry_v1_model_version_query_service_pb2
from acme.modelregistry.v1 import (
    model_version_validation_service_pb2 as modelregistry_v1_model_version_validation_service_pb2,
)
from acme.modelregistry.v1 import modelregistry_pb2 as modelregistry_v1_modelregistry_pb2
from acme.modelregistry.v1 import (
    registered_model_calculation_service_pb2 as modelregistry_v1_registered_model_calculation_service_pb2,
)
from acme.modelregistry.v1 import (
    registered_model_query_service_pb2 as modelregistry_v1_registered_model_query_service_pb2,
)
from acme.search.v1 import search_index_service_pb2 as search_v1_search_index_service_pb2

from acme_data.domains.modelregistry import hooks
from acme_data.domains.modelregistry.dependencies import Dependencies
from acme_data.domains.modelregistry.models import DeploymentImportImportDeployments3Command
from acme_data.domains.modelregistry.models import to_deployment_import_import_deployments3_command
from acme_data.platform.rpc import async_messages
from acme_data.platform.tenancy import tenant_id
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


async def handle_cancel_deployment_import(
    deps: Dependencies,
    request: modelregistry_v1_deployment_import_service_pb2.CancelDeploymentImportRequest
) -> modelregistry_v1_deployment_import_service_pb2.CancelDeploymentImportResponse:
    """Cancels a deployment."""
    response = modelregistry_v1_deployment_import_service_pb2.CancelDeploymentImportResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('CancelDeploymentImport', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'CancelDeploymentImport', {'reason': request.reason})
        response_0 = documents_v1_document_service_pb2.ListDocumentsResponse()
        response_1 = featurestore_v1_entity_lifecycle_service_pb2.ScheduleEntityExpiryResponse()
        outgoing_0 = documents_v1_document_service_pb2.ListDocumentsRequest(
            context=request.context,
            filter=documents_v1_document_service_pb2.ListDocumentsRequest.Filter(
                created_after=request.details.effective_at,
                labels=dict(request.annotations),
                owner_id=request.details.new_owner.user_id
            )
        )
        response_0 = await deps.clients.documents_document.ListDocuments(outgoing_0, timeout=deps.settings.timeout)
        outgoing_1 = featurestore_v1_entity_lifecycle_service_pb2.ScheduleEntityExpiryRequest(
            context=request.context,
            details=featurestore_v1_entity_lifecycle_service_pb2.ScheduleEntityExpiryRequest.Details(
                notify=common_v1_contact_pb2.ContactInfo(name=request.details.notify_contact.name)
            ),
            entity=featurestore_v1_featurestore_pb2.Entity(
                contact=common_v1_contact_pb2.ContactInfo(
                    email=request.details.new_owner.email,
                    phone=request.details.notify_contact.phone
                ),
                relationship_manager=identity_v1_refs_pb2.UserRef(user_id=request.details.new_owner.user_id)
            )
        )
        document_1 = MessageToDict(outgoing_1, preserving_proto_field_name=True)
        outgoing_1 = ParseDict(document_1, featurestore_v1_entity_lifecycle_service_pb2.ScheduleEntityExpiryRequest())
        response_1 = await deps.clients.featurestore_entity_lifecycle.ScheduleEntityExpiry(
            outgoing_1,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.result.reference_ids
        response.result.reference_ids.extend(returned_0_0)
        returned_0_1 = response_0.result.message
        if returned_0_1:
            response.result.message = returned_0_1
        returned_1_0 = response_1.outcome.status
        if returned_1_0:
            response.outcome.status = returned_1_0
        echoed_0 = request.deployment_id
        response.deployment.deployment_id = echoed_0
        echoed_1 = request.details.effective_at
        response.outcome.effective_at.CopyFrom(echoed_1)
        return response


async def handle_get_deployment_import_status(
    deps: Dependencies,
    request: modelregistry_v1_deployment_import_service_pb2.GetDeploymentImportStatusRequest
) -> modelregistry_v1_deployment_import_service_pb2.GetDeploymentImportStatusResponse:
    """Returns a deployment."""
    response = modelregistry_v1_deployment_import_service_pb2.GetDeploymentImportStatusResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('GetDeploymentImportStatus', extra={'fields': {'domain': 'modelregistry'}})
        await deps.repository.audit(request.context.tenant_id, 'GetDeploymentImportStatus', {})
        response_0 = modelregistry_v1_model_version_validation_service_pb2.CheckModelVersionEligibilityResponse()
        outgoing_0 = modelregistry_v1_model_version_validation_service_pb2.CheckModelVersionEligibilityRequest(
            context=request.context,
            details=modelregistry_v1_model_version_validation_service_pb2.CheckModelVersionEligibilityRequest.Details(
                contact=common_v1_contact_pb2.ContactInfo(email=request.context.actor.email)
            )
        )
        response_0 = await deps.clients.modelregistry_model_version_validation.CheckModelVersionEligibility(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.result.reference_ids
        response.result.reference_ids.extend(returned_0_0)
        returned_0_1 = response_0.model_version.subject.display_name
        if returned_0_1:
            response.deployment.organizer.display_name = returned_0_1
        echoed_0 = request.deployment_id
        response.deployment.deployment_id = echoed_0
        return response


async def handle_import_deployments(
    deps: Dependencies,
    request: modelregistry_v1_deployment_import_service_pb2.ImportDeploymentsRequest
) -> modelregistry_v1_deployment_import_service_pb2.ImportDeploymentsResponse:
    """Takes a stream of deployments and answers once at the end."""
    response = modelregistry_v1_deployment_import_service_pb2.ImportDeploymentsResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('ImportDeployments', extra={'fields': {'sequence': request.sequence}})
        await deps.repository.audit(request.context.tenant_id, 'ImportDeployments', {'sequence': request.sequence})
        if request.WhichOneof('chunk') == 'record':
            await deps.repository.save_deployment(request.context.tenant_id, request.record)
        response_0 = metrics_v1_metric_alert_validation_service_pb2.LintMetricAlertsResponse()
        response_1 = featurestore_v1_feature_view_approval_service_pb2.DelegateFeatureViewApprovalResponse()
        response_2 = modelregistry_v1_model_version_validation_service_pb2.LintModelVersionsResponse()
        response_3 = modelregistry_v1_registered_model_query_service_pb2.CountRegisteredModelsResponse()
        outgoing_0 = metrics_v1_metric_alert_validation_service_pb2.LintMetricAlertsRequest(
            context=request.context,
            details=metrics_v1_metric_alert_validation_service_pb2.LintMetricAlertsRequest.Details(
                contact=common_v1_contact_pb2.ContactInfo(email=request.header.submitted_by.email)
            )
        )
        response_0 = await deps.clients.metrics_metric_alert_validation.LintMetricAlerts(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = featurestore_v1_feature_view_approval_service_pb2.DelegateFeatureViewApprovalRequest()
        outgoing_1.context.CopyFrom(request.context)
        if request.WhichOneof('chunk') == 'record':
            outgoing_1.feature_view.audit.created_at.CopyFrom(request.record.audit.created_at)
        if request.WhichOneof('chunk') == 'record':
            outgoing_1.feature_view.address.region = request.record.location.region
        outgoing_1.feature_view.audit.etag = response_0.metric_alert.audit.etag
        response_1 = await deps.clients.featurestore_feature_view_approval.DelegateFeatureViewApproval(
            outgoing_1,
            timeout=deps.settings.timeout
        )
        async for item_2 in async_messages(request.record.participants):
            outgoing_2 = modelregistry_v1_model_version_validation_service_pb2.LintModelVersionsRequest(
                context=request.context,
                details=modelregistry_v1_model_version_validation_service_pb2.LintModelVersionsRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(phone=item_2.contact.phone)
                )
            )
            response_2 = await deps.clients.modelregistry_model_version_validation.LintModelVersions(
                outgoing_2,
                timeout=deps.settings.timeout
            )
        command_3 = DeploymentImportImportDeployments3Command(
            context=request.context,
            filter_region=response_1.feature_view.address.region,
            filter_owner_id=response_1.feature_view.components.get(
                'primary',
                featurestore_v1_featurestore_pb2.FeatureViewComponent()
            ).component_id,
            filter_created_after=response_0.metric_alert.audit.updated_at,
            filter_labels=dict(response_2.result.details)
        )
        outgoing_3 = to_deployment_import_import_deployments3_command(command_3)
        response_3 = await deps.clients.modelregistry_registered_model_query.CountRegisteredModels(
            outgoing_3,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.result.message
        if returned_0_0:
            response.result.message = returned_0_0
        returned_0_1 = response_0.result.reference_ids
        response.result.reference_ids.extend(returned_0_1)
        returned_1_0 = response_1.result.message
        if returned_1_0:
            response.result.message = returned_1_0
        returned_1_1 = response_1.result.status
        if returned_1_1:
            response.result.status = returned_1_1
        returned_3_0 = response_3.result.message
        if returned_3_0:
            response.result.message = returned_3_0
        return response


async def handle_list_deployment_imports(
    deps: Dependencies,
    request: modelregistry_v1_deployment_import_service_pb2.ListDeploymentImportsRequest
) -> modelregistry_v1_deployment_import_service_pb2.ListDeploymentImportsResponse:
    """Lists deployments a page at a time."""
    response = modelregistry_v1_deployment_import_service_pb2.ListDeploymentImportsResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('ListDeploymentImports', extra={'fields': {'order_by': request.order_by}})
        await deps.repository.audit(request.context.tenant_id, 'ListDeploymentImports', {'order_by': request.order_by})
        response_0 = identity_v1_user_validation_service_pb2.ScoreUserResponse()
        outgoing_0 = identity_v1_user_validation_service_pb2.ScoreUserRequest(
            context=request.context,
            user=identity_v1_identity_pb2.User(
                primary_address=common_v1_address_pb2.PostalAddress(region=request.filter.region)
            )
        )
        response_0 = await deps.clients.identity_user_validation.ScoreUser(outgoing_0, timeout=deps.settings.timeout)
        returned_0_0 = response_0.user.primary_address.country_code
        returned_0_0_part_0 = response.deployments.add()
        if returned_0_0:
            returned_0_0_part_0.location.country_code = returned_0_0
        returned_0_1 = response_0.user.audit.created_at
        returned_0_1_part_0 = response.deployments.add()
        if returned_0_1.ListFields():
            returned_0_1_part_0.audit.created_at.MergeFrom(returned_0_1)
        return response


async def handle_map_deployment_import_columns(
    deps: Dependencies,
    request: modelregistry_v1_deployment_import_service_pb2.MapDeploymentImportColumnsRequest
) -> modelregistry_v1_deployment_import_service_pb2.MapDeploymentImportColumnsResponse:
    """Maps a deployment."""
    response = modelregistry_v1_deployment_import_service_pb2.MapDeploymentImportColumnsResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('MapDeploymentImportColumns', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'MapDeploymentImportColumns', {'reason': request.reason})
        await deps.repository.save_deployment(request.context.tenant_id, request.deployment)
        response_0 = lineage_v1_impact_sync_service_pb2.ReconcileImpactsResponse()
        response_1 = modelregistry_v1_registered_model_calculation_service_pb2.QuoteRegisteredModelResponse()
        response_2 = customers_v1_customer_segment_calculation_service_pb2.ExplainCustomerSegmentCalculationResponse()
        response_3 = modelregistry_v1_model_version_query_service_pb2.ExportModelVersionsResponse()
        outgoing_0 = lineage_v1_impact_sync_service_pb2.ReconcileImpactsRequest(
            context=request.context,
            impact=lineage_v1_lineage_pb2.Impact(
                audit=common_v1_audit_pb2.AuditInfo(etag=request.deployment.audit.etag),
                requester=common_v1_contact_pb2.ContactInfo(email=request.deployment.organizer.email)
            )
        )
        response_0 = await deps.clients.lineage_impact_sync.ReconcileImpacts(outgoing_0, timeout=deps.settings.timeout)
        outgoing_1 = modelregistry_v1_registered_model_calculation_service_pb2.QuoteRegisteredModelRequest(
            context=request.context,
            details=modelregistry_v1_registered_model_calculation_service_pb2.QuoteRegisteredModelRequest.Details(
                destination=common_v1_address_pb2.PostalAddress(
                    lines=list(request.deployment.location.lines),
                    region=request.deployment.location.region
                )
            ),
            registered_model=modelregistry_v1_modelregistry_pb2.RegisteredModel(
                address=common_v1_address_pb2.PostalAddress(country_code=request.deployment.location.country_code),
                owner=identity_v1_refs_pb2.UserRef(user_id=request.deployment.organizer.user_id)
            )
        )
        response_1 = await hooks.deployment_import_map_deployment_import_columns1(
            deps.clients.modelregistry_registered_model_calculation,
            outgoing_1,
            deps.settings.timeout
        )
        outgoing_2 = customers_v1_customer_segment_calculation_service_pb2.ExplainCustomerSegmentCalculationRequest()
        outgoing_2.context.CopyFrom(request.context)
        outgoing_2.details.contact.email = request.deployment.organizer.email
        outgoing_2.details.contact.phone = response_0.impact.requester.phone
        outgoing_2.customer_segment.owner.user_id = request.deployment.organizer.user_id
        outgoing_2.context.tenant_id = tenant_id.get()
        response_2 = await deps.clients.customers_customer_segment_calculation.ExplainCustomerSegmentCalculation(
            outgoing_2,
            timeout=deps.settings.timeout
        )
        outgoing_3 = modelregistry_v1_model_version_query_service_pb2.ExportModelVersionsRequest(
            context=request.context,
            filter=modelregistry_v1_model_version_query_service_pb2.ExportModelVersionsRequest.Filter(
                created_after=response_0.impact.sla.due_at,
                region=request.deployment.location.region
            )
        )
        async for chunk_3 in deps.clients.modelregistry_model_version_query.ExportModelVersions(
            outgoing_3,
            timeout=deps.settings.timeout
        ):
            response_3 = chunk_3
        returned_0_0 = response_0.impact.assignee.display_name
        if returned_0_0:
            response.deployment.organizer.display_name = returned_0_0
        returned_1_0 = response_1.registered_model.address.region
        if returned_1_0:
            response.deployment.location.region = returned_1_0
        returned_1_1 = response_1.result.reference_ids
        response.result.reference_ids.extend(returned_1_1)
        returned_2_0 = response_2.result.message
        if returned_2_0:
            response.outcome.message = returned_2_0
        returned_2_1 = response_2.customer_segment.audit.created_at
        if returned_2_1.ListFields():
            response.deployment.audit.created_at.MergeFrom(returned_2_1)
        echoed_0 = request.deployment_id
        response.deployment.deployment_id = echoed_0
        echoed_1 = request.deployment.title
        response.deployment.title = echoed_1
        return response


async def handle_retry_deployment_import(
    deps: Dependencies,
    request: modelregistry_v1_deployment_import_service_pb2.RetryDeploymentImportRequest
) -> modelregistry_v1_deployment_import_service_pb2.RetryDeploymentImportResponse:
    """Retrys a deployment."""
    response = modelregistry_v1_deployment_import_service_pb2.RetryDeploymentImportResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('RetryDeploymentImport', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'RetryDeploymentImport', {'reason': request.reason})
        await deps.repository.save_deployment(request.context.tenant_id, request.deployment)
        response_0 = featurestore_v1_feature_view_approval_service_pb2.CommentFeatureViewApprovalResponse()
        response_1 = search_v1_search_index_service_pb2.SearchSearchIndexesResponse()
        outgoing_0 = featurestore_v1_feature_view_approval_service_pb2.CommentFeatureViewApprovalRequest(
            context=request.context,
            details=featurestore_v1_feature_view_approval_service_pb2.CommentFeatureViewApprovalRequest.Details(
                approver=identity_v1_refs_pb2.UserRef(display_name=request.deployment.organizer.display_name)
            ),
            feature_view=featurestore_v1_featurestore_pb2.FeatureView(
                audit=common_v1_audit_pb2.AuditInfo(created_by=request.deployment.audit.created_by)
            )
        )
        response_0 = await deps.clients.featurestore_feature_view_approval.CommentFeatureViewApproval(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = search_v1_search_index_service_pb2.SearchSearchIndexesRequest()
        outgoing_1.context.CopyFrom(request.context)
        if response_0.feature_view.WhichOneof('locator') == 'address':
            outgoing_1.filter.region = response_0.feature_view.address.region
        response_1 = await deps.clients.search_search_index.SearchSearchIndexes(
            outgoing_1,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.result.status
        if returned_0_0:
            response.outcome.status = returned_0_0
        returned_1_0 = response_1.result.reference_ids
        response.result.reference_ids.extend(returned_1_0)
        echoed_0 = request.deployment_id
        response.deployment.deployment_id = echoed_0
        echoed_1 = request.deployment.location
        response.deployment.location.CopyFrom(echoed_1)
        return response


async def handle_validate_deployment_import(
    deps: Dependencies,
    request: modelregistry_v1_deployment_import_service_pb2.ValidateDeploymentImportRequest
) -> modelregistry_v1_deployment_import_service_pb2.ValidateDeploymentImportResponse:
    """Validates a deployment."""
    response = modelregistry_v1_deployment_import_service_pb2.ValidateDeploymentImportResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('ValidateDeploymentImport', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'ValidateDeploymentImport', {'reason': request.reason})
        await deps.repository.save_deployment(request.context.tenant_id, request.deployment)
        response_0 = modelregistry_v1_model_version_validation_service_pb2.LintModelVersionsResponse()
        response_1 = modelregistry_v1_deployment_calculation_service_pb2.EstimateDeploymentResponse()
        response_2 = modelregistry_v1_model_version_query_service_pb2.SuggestModelVersionsResponse()
        response_3 = customers_v1_consent_record_validation_service_pb2.ScoreConsentRecordResponse()
        for item_0 in request.deployment.participants:
            outgoing_0 = modelregistry_v1_model_version_validation_service_pb2.LintModelVersionsRequest(
                context=request.context,
                details=modelregistry_v1_model_version_validation_service_pb2.LintModelVersionsRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(
                        email=item_0.contact.email,
                        name=item_0.contact.name,
                        phone=item_0.contact.phone,
                        preferred_channel=item_0.contact.preferred_channel
                    )
                )
            )
            response_0 = await deps.clients.modelregistry_model_version_validation.LintModelVersions(
                outgoing_0,
                timeout=deps.settings.timeout
            )
        outgoing_1 = modelregistry_v1_deployment_calculation_service_pb2.EstimateDeploymentRequest(
            context=request.context,
            deployment=modelregistry_v1_modelregistry_pb2.Deployment(
                daily=modelregistry_v1_modelregistry_pb2.DeploymentDailyRule(
                    interval=request.deployment.weekly.interval
                ),
                participants=[
                    modelregistry_v1_modelregistry_pb2.DeploymentParticipant(
                        contact=common_v1_contact_pb2.ContactInfo(
                            email=request.deployment.organizer.email,
                            phone=request.details.contact.phone
                        )
                    )
                ]
            )
        )
        response_1 = await deps.clients.modelregistry_deployment_calculation.EstimateDeployment(
            outgoing_1,
            timeout=deps.settings.timeout
        )
        outgoing_2 = modelregistry_v1_model_version_query_service_pb2.SuggestModelVersionsRequest(
            context=request.context,
            filter=modelregistry_v1_model_version_query_service_pb2.SuggestModelVersionsRequest.Filter(
                created_after=response_1.deployment.audit.created_at,
                region=request.deployment.location.region
            )
        )
        method_name_2 = 'SuggestModelVersions'
        response_2 = await getattr(
            deps.clients.modelregistry_model_version_query,
            method_name_2
        )(outgoing_2, timeout=deps.settings.timeout)
        fields_3: dict[str, Any] = {
            'consent_record': {'subject': {'display_name': request.deployment.organizer.display_name}},
            'context': request.context
        }
        outgoing_3 = customers_v1_consent_record_validation_service_pb2.ScoreConsentRecordRequest(**fields_3)
        response_3 = await deps.clients.customers_consent_record_validation.ScoreConsentRecord(
            outgoing_3,
            timeout=deps.settings.timeout
        )
        returned_1_0 = response_1.deployment.window
        if returned_1_0.ListFields():
            response.deployment.window.MergeFrom(returned_1_0)
        returned_2_0 = response_2.result.details
        response.result.details.update(returned_2_0)
        returned_2_1 = response_2.result.status
        if returned_2_1:
            response.result.status = returned_2_1
        returned_3_0 = response_3.result.correlation_id
        if returned_3_0:
            response.result.correlation_id = returned_3_0
        echoed_0 = request.deployment_id
        response.deployment.deployment_id = echoed_0
        echoed_1 = request.deployment.title
        response.deployment.title = echoed_1
        return response
