"""Functional operations behind EntityImportService."""

from __future__ import annotations

import logging

from google.protobuf.json_format import MessageToDict
from google.protobuf.json_format import ParseDict

from acme.catalog.v1 import product_query_service_pb2 as catalog_v1_product_query_service_pb2
from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.datasets.v1 import data_schema_calculation_service_pb2 as datasets_v1_data_schema_calculation_service_pb2
from acme.datasets.v1 import datasets_pb2 as datasets_v1_datasets_pb2
from acme.featurestore.v1 import entity_import_service_pb2 as featurestore_v1_entity_import_service_pb2
from acme.featurestore.v1 import (
    feature_value_calculation_service_pb2 as featurestore_v1_feature_value_calculation_service_pb2,
)
from acme.featurestore.v1 import feature_value_import_service_pb2 as featurestore_v1_feature_value_import_service_pb2
from acme.featurestore.v1 import (
    feature_value_validation_service_pb2 as featurestore_v1_feature_value_validation_service_pb2,
)
from acme.featurestore.v1 import feature_view_service_pb2 as featurestore_v1_feature_view_service_pb2
from acme.featurestore.v1 import (
    feature_view_validation_service_pb2 as featurestore_v1_feature_view_validation_service_pb2,
)
from acme.featurestore.v1 import featurestore_pb2 as featurestore_v1_featurestore_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.lineage.v1 import impact_workflow_service_pb2 as lineage_v1_impact_workflow_service_pb2
from acme.lineage.v1 import lineage_pb2 as lineage_v1_lineage_pb2
from acme.metrics.v1 import dashboard_validation_service_pb2 as metrics_v1_dashboard_validation_service_pb2
from acme.notifications.v1 import (
    notification_validation_service_pb2 as notifications_v1_notification_validation_service_pb2,
)
from acme.notifications.v1 import notifications_pb2 as notifications_v1_notifications_pb2

from acme_data.domains.featurestore import hooks
from acme_data.domains.featurestore.dependencies import Dependencies
from acme_data.domains.featurestore.models import EntityImportRetryEntityImport1Command
from acme_data.domains.featurestore.models import to_entity_import_retry_entity_import1_command
from acme_data.platform.rpc import async_messages
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


async def handle_cancel_entity_import(
    deps: Dependencies,
    request: featurestore_v1_entity_import_service_pb2.CancelEntityImportRequest
) -> featurestore_v1_entity_import_service_pb2.CancelEntityImportResponse:
    """Cancels an entity."""
    response = featurestore_v1_entity_import_service_pb2.CancelEntityImportResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('CancelEntityImport', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'CancelEntityImport', {'reason': request.reason})
        response_0 = featurestore_v1_feature_view_service_pb2.BatchGetFeatureViewsResponse()
        response_1 = featurestore_v1_feature_view_service_pb2.BatchCreateFeatureViewsResponse()
        outgoing_0 = featurestore_v1_feature_view_service_pb2.BatchGetFeatureViewsRequest(context=request.context)
        response_0 = await deps.clients.featurestore_feature_view.BatchGetFeatureViews(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = featurestore_v1_feature_view_service_pb2.BatchCreateFeatureViewsRequest(
            context=request.context,
            record=featurestore_v1_featurestore_pb2.FeatureView(
                owner=identity_v1_refs_pb2.UserRef(
                    display_name=request.details.new_owner.display_name,
                    user_id=request.details.new_owner.user_id
                )
            )
        )
        response_1 = await deps.clients.featurestore_feature_view.BatchCreateFeatureViews(
            async_messages((outgoing_1,)),
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.result.details
        response.result.details.update(returned_0_0)
        echoed_0 = request.entity_id
        response.entity.entity_id = echoed_0
        echoed_1 = request.details.effective_at
        response.outcome.effective_at.CopyFrom(echoed_1)
        return response


async def handle_get_entity_import_status(
    deps: Dependencies,
    request: featurestore_v1_entity_import_service_pb2.GetEntityImportStatusRequest
) -> featurestore_v1_entity_import_service_pb2.GetEntityImportStatusResponse:
    """Returns an entity."""
    response = featurestore_v1_entity_import_service_pb2.GetEntityImportStatusResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('GetEntityImportStatus', extra={'fields': {'domain': 'featurestore'}})
        await deps.repository.audit(request.context.tenant_id, 'GetEntityImportStatus', {})
        response_0 = featurestore_v1_feature_value_calculation_service_pb2.SimulateFeatureValueResponse()
        response_1 = featurestore_v1_feature_value_import_service_pb2.ListFeatureValueImportsResponse()
        outgoing_0 = featurestore_v1_feature_value_calculation_service_pb2.SimulateFeatureValueRequest(
            context=request.context,
            feature_value=featurestore_v1_featurestore_pb2.FeatureValue(
                measurements=[
                    featurestore_v1_featurestore_pb2.FeatureValueMeasurement(observed_at=request.context.deadline)
                ],
                source=request.entity_id
            )
        )
        response_0 = await deps.clients.featurestore_feature_value_calculation.SimulateFeatureValue(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = featurestore_v1_feature_value_import_service_pb2.ListFeatureValueImportsRequest(
            context=request.context,
            filter=featurestore_v1_feature_value_import_service_pb2.ListFeatureValueImportsRequest.Filter(
                owner_id=response_0.feature_value.subject.dataset_id
            )
        )
        document_1 = MessageToDict(outgoing_1, preserving_proto_field_name=True)
        outgoing_1 = ParseDict(
            document_1,
            featurestore_v1_feature_value_import_service_pb2.ListFeatureValueImportsRequest()
        )
        response_1 = await deps.clients.featurestore_feature_value_import.ListFeatureValueImports(
            outgoing_1,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.feature_value.subject.display_name
        if returned_0_0:
            response.entity.relationship_manager.display_name = returned_0_0
        returned_1_0 = response_1.result.message
        if returned_1_0:
            response.result.message = returned_1_0
        returned_1_1 = response_1.result.status
        if returned_1_1:
            response.result.status = returned_1_1
        echoed_0 = request.entity_id
        response.entity.entity_id = echoed_0
        return response


async def handle_import_entities(
    deps: Dependencies,
    request: featurestore_v1_entity_import_service_pb2.ImportEntitiesRequest
) -> featurestore_v1_entity_import_service_pb2.ImportEntitiesResponse:
    """Takes a stream of entities and answers once at the end."""
    response = featurestore_v1_entity_import_service_pb2.ImportEntitiesResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('ImportEntities', extra={'fields': {'sequence': request.sequence}})
        await deps.repository.audit(request.context.tenant_id, 'ImportEntities', {'sequence': request.sequence})
        if request.WhichOneof('chunk') == 'record':
            await deps.repository.save_entity(request.context.tenant_id, request.record)
        response_0 = featurestore_v1_feature_view_validation_service_pb2.PreviewFeatureViewResponse()
        response_1 = metrics_v1_dashboard_validation_service_pb2.ExplainDashboardDecisionResponse()
        outgoing_0 = featurestore_v1_feature_view_validation_service_pb2.PreviewFeatureViewRequest()
        outgoing_0.context.CopyFrom(request.context)
        if request.WhichOneof('chunk') == 'record':
            outgoing_0.feature_view.address.country_code = request.record.primary_address.country_code
        if request.WhichOneof('chunk') == 'record':
            outgoing_0.details.contact.email = request.record.contact.email
        if request.WhichOneof('chunk') == 'record':
            outgoing_0.feature_view.owner.email = request.record.relationship_manager.email
        response_0 = await deps.clients.featurestore_feature_view_validation.PreviewFeatureView(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = metrics_v1_dashboard_validation_service_pb2.ExplainDashboardDecisionRequest()
        outgoing_1.context.CopyFrom(request.context)
        outgoing_1.details.contact.email = request.record.contact.email
        outgoing_1.dashboard.audit.updated_by = request.record.audit.updated_by
        outgoing_1.dashboard.counterparty.display_name = response_0.feature_view.owner.display_name
        merged_1 = metrics_v1_dashboard_validation_service_pb2.ExplainDashboardDecisionRequest()
        merged_1.MergeFrom(outgoing_1)
        outgoing_1.CopyFrom(merged_1)
        response_1 = await deps.clients.metrics_dashboard_validation.ExplainDashboardDecision(
            outgoing_1,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.result.status
        if returned_0_0:
            response.result.status = returned_0_0
        returned_1_0 = response_1.result.reference_ids
        response.result.reference_ids.extend(returned_1_0)
        returned_1_1 = response_1.outcome.message
        if returned_1_1:
            response.result.message = returned_1_1
        return response


async def handle_list_entity_imports(
    deps: Dependencies,
    request: featurestore_v1_entity_import_service_pb2.ListEntityImportsRequest
) -> featurestore_v1_entity_import_service_pb2.ListEntityImportsResponse:
    """Lists entities a page at a time."""
    response = featurestore_v1_entity_import_service_pb2.ListEntityImportsResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('ListEntityImports', extra={'fields': {'order_by': request.order_by}})
        await deps.repository.audit(request.context.tenant_id, 'ListEntityImports', {'order_by': request.order_by})
        response_0 = featurestore_v1_feature_view_service_pb2.CloneFeatureViewResponse()
        outgoing_0 = featurestore_v1_feature_view_service_pb2.CloneFeatureViewRequest(
            context=request.context,
            feature_view=featurestore_v1_featurestore_pb2.FeatureView(
                address=common_v1_address_pb2.PostalAddress(region=request.filter.region),
                audit=common_v1_audit_pb2.AuditInfo(updated_at=request.filter.created_after),
                owner=identity_v1_refs_pb2.UserRef(email=request.context.actor.email)
            )
        )
        response_0 = await deps.clients.featurestore_feature_view.CloneFeatureView(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.result.message
        if returned_0_0:
            response.result.message = returned_0_0
        returned_0_1 = response_0.feature_view.address.locality
        returned_0_1_part_0 = response.entities.add()
        if returned_0_1:
            returned_0_1_part_0.primary_address.locality = returned_0_1
        return response


async def handle_map_entity_import_columns(
    deps: Dependencies,
    request: featurestore_v1_entity_import_service_pb2.MapEntityImportColumnsRequest
) -> featurestore_v1_entity_import_service_pb2.MapEntityImportColumnsResponse:
    """Maps an entity."""
    response = featurestore_v1_entity_import_service_pb2.MapEntityImportColumnsResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('MapEntityImportColumns', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'MapEntityImportColumns', {'reason': request.reason})
        await deps.repository.save_entity(request.context.tenant_id, request.entity)
        response_0 = datasets_v1_data_schema_calculation_service_pb2.EstimateDataSchemaResponse()
        outgoing_0 = datasets_v1_data_schema_calculation_service_pb2.EstimateDataSchemaRequest(
            context=request.context,
            data_schema=datasets_v1_datasets_pb2.DataSchema(
                children=[
                    datasets_v1_datasets_pb2.DataSchema(
                        children=[
                            datasets_v1_datasets_pb2.DataSchema(
                                audit=common_v1_audit_pb2.AuditInfo(updated_by=request.entity.audit.updated_by)
                            )
                        ]
                    )
                ]
            )
        )
        response_0 = await deps.clients.datasets_data_schema_calculation.EstimateDataSchema(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.result.correlation_id
        if returned_0_0:
            response.result.correlation_id = returned_0_0
        echoed_0 = request.entity_id
        response.entity.entity_id = echoed_0
        echoed_1 = request.entity.name
        response.entity.name.CopyFrom(echoed_1)
        return response


async def handle_retry_entity_import(
    deps: Dependencies,
    request: featurestore_v1_entity_import_service_pb2.RetryEntityImportRequest
) -> featurestore_v1_entity_import_service_pb2.RetryEntityImportResponse:
    """Retrys an entity."""
    response = featurestore_v1_entity_import_service_pb2.RetryEntityImportResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('RetryEntityImport', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'RetryEntityImport', {'reason': request.reason})
        await deps.repository.save_entity(request.context.tenant_id, request.entity)
        response_0 = lineage_v1_impact_workflow_service_pb2.CancelImpactWorkflowResponse()
        response_1 = catalog_v1_product_query_service_pb2.CountProductsResponse()
        outgoing_0 = lineage_v1_impact_workflow_service_pb2.CancelImpactWorkflowRequest(
            context=request.context,
            impact=lineage_v1_lineage_pb2.Impact(
                assignee=identity_v1_refs_pb2.UserRef(display_name=request.entity.relationship_manager.display_name)
            )
        )
        response_0 = await deps.clients.lineage_impact_workflow.CancelImpactWorkflow(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        command_1 = EntityImportRetryEntityImport1Command.model_validate(
            {'context': request.context, 'filter_region': request.entity.primary_address.region}
        )
        outgoing_1 = to_entity_import_retry_entity_import1_command(command_1)
        response_1 = await deps.clients.catalog_product_query.CountProducts(outgoing_1, timeout=deps.settings.timeout)
        returned_0_0 = response_0.impact.assignee.email
        if returned_0_0:
            response.entity.contact.email = returned_0_0
        returned_0_1 = response_0.outcome.reference_id
        if returned_0_1:
            response.outcome.reference_id = returned_0_1
        returned_1_0 = response_1.result.message
        if returned_1_0:
            response.outcome.message = returned_1_0
        returned_1_1 = response_1.result.status
        if returned_1_1:
            response.outcome.status = returned_1_1
        echoed_0 = request.entity_id
        response.entity.entity_id = echoed_0
        echoed_1 = request.entity.attributes
        response.entity.attributes.update(echoed_1)
        return response


async def handle_validate_entity_import(
    deps: Dependencies,
    request: featurestore_v1_entity_import_service_pb2.ValidateEntityImportRequest
) -> featurestore_v1_entity_import_service_pb2.ValidateEntityImportResponse:
    """Validates an entity."""
    response = featurestore_v1_entity_import_service_pb2.ValidateEntityImportResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('ValidateEntityImport', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'ValidateEntityImport', {'reason': request.reason})
        await deps.repository.save_entity(request.context.tenant_id, request.entity)
        response_0 = featurestore_v1_feature_value_validation_service_pb2.ScoreFeatureValueResponse()
        response_1 = notifications_v1_notification_validation_service_pb2.ScoreNotificationResponse()
        outgoing_0 = featurestore_v1_feature_value_validation_service_pb2.ScoreFeatureValueRequest(
            context=request.context,
            details=featurestore_v1_feature_value_validation_service_pb2.ScoreFeatureValueRequest.Details(
                destination=common_v1_address_pb2.PostalAddress(
                    country_code=request.entity.primary_address.country_code,
                    postal_code=request.entity.primary_address.postal_code
                )
            )
        )
        response_0 = await deps.clients.featurestore_feature_value_validation.ScoreFeatureValue(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = notifications_v1_notification_validation_service_pb2.ScoreNotificationRequest(
            context=request.context,
            details=notifications_v1_notification_validation_service_pb2.ScoreNotificationRequest.Details(
                destination=common_v1_address_pb2.PostalAddress(region=request.entity.primary_address.region)
            ),
            notification=notifications_v1_notifications_pb2.Notification(
                assignee=identity_v1_refs_pb2.UserRef(email=request.entity.contact.email)
            )
        )
        response_1 = await hooks.entity_import_validate_entity_import1(
            deps.clients.notifications_notification_validation,
            outgoing_1,
            deps.settings.timeout
        )
        returned_0_0 = response_0.result.message
        if returned_0_0:
            response.outcome.message = returned_0_0
        returned_0_1 = response_0.feature_value.subject.display_name
        if returned_0_1:
            response.entity.relationship_manager.display_name = returned_0_1
        returned_1_0 = response_1.result.message
        if returned_1_0:
            response.result.message = returned_1_0
        echoed_0 = request.entity_id
        response.entity.entity_id = echoed_0
        echoed_1 = request.entity.name
        response.entity.contact.name.CopyFrom(echoed_1)
        return response
