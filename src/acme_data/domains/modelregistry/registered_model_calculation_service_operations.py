"""Functional operations behind RegisteredModelCalculationService."""

from __future__ import annotations

from typing import cast
import logging

from google.protobuf.any_pb2 import Any as AnyMessage
from google.protobuf.json_format import MessageToDict
from google.protobuf.json_format import ParseDict

from acme.anomalies.v1 import anomalies_pb2 as anomalies_v1_anomalies_pb2
from acme.anomalies.v1 import anomaly_validation_service_pb2 as anomalies_v1_anomaly_validation_service_pb2
from acme.authorization.v1 import access_policy_service_pb2 as authorization_v1_access_policy_service_pb2
from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.featurestore.v1 import entity_calculation_service_pb2 as featurestore_v1_entity_calculation_service_pb2
from acme.featurestore.v1 import (
    feature_value_calculation_service_pb2 as featurestore_v1_feature_value_calculation_service_pb2,
)
from acme.featurestore.v1 import feature_view_query_service_pb2 as featurestore_v1_feature_view_query_service_pb2
from acme.featurestore.v1 import featurestore_pb2 as featurestore_v1_featurestore_pb2
from acme.identity.v1 import identity_pb2 as identity_v1_identity_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.identity.v1 import user_validation_service_pb2 as identity_v1_user_validation_service_pb2
from acme.maintenance.v1 import work_order_query_service_pb2 as maintenance_v1_work_order_query_service_pb2
from acme.metrics.v1 import dashboard_export_service_pb2 as metrics_v1_dashboard_export_service_pb2
from acme.metrics.v1 import dashboard_export_service_pb2_grpc as metrics_v1_dashboard_export_service_pb2_grpc
from acme.metrics.v1 import metrics_pb2 as metrics_v1_metrics_pb2
from acme.metrics.v1 import refs_pb2 as metrics_v1_refs_pb2
from acme.modelregistry.v1 import modelregistry_pb2 as modelregistry_v1_modelregistry_pb2
from acme.modelregistry.v1 import (
    registered_model_calculation_service_pb2 as modelregistry_v1_registered_model_calculation_service_pb2,
)
from acme.seating.v1 import seat_map_service_pb2 as seating_v1_seat_map_service_pb2

from acme_data.domains.modelregistry.adapters import RegisteredModelCalculationRecalculateRegisteredModels1Adapter
from acme_data.domains.modelregistry.adapters import RegisteredModelCalculationRecalculateRegisteredModels1Port
from acme_data.domains.modelregistry.dependencies import Dependencies
from acme_data.domains.modelregistry.models import RegisteredModelCalculationExplainRegisteredModelCalculation3Command
from acme_data.domains.modelregistry.models import (
    to_registered_model_calculation_explain_registered_model_calculation3_command,
)
from acme_data.platform.rpc import async_messages
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


async def handle_calculate_registered_model(
    deps: Dependencies,
    request: modelregistry_v1_registered_model_calculation_service_pb2.CalculateRegisteredModelRequest
) -> modelregistry_v1_registered_model_calculation_service_pb2.CalculateRegisteredModelResponse:
    """Calculates a registered model."""
    response = modelregistry_v1_registered_model_calculation_service_pb2.CalculateRegisteredModelResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('CalculateRegisteredModel', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'CalculateRegisteredModel', {'reason': request.reason})
        await deps.repository.save_registered_model(request.context.tenant_id, request.registered_model)
        response_0 = maintenance_v1_work_order_query_service_pb2.FindWorkOrdersResponse()
        response_1 = featurestore_v1_feature_value_calculation_service_pb2.CalculateFeatureValueResponse()
        outgoing_0 = maintenance_v1_work_order_query_service_pb2.FindWorkOrdersRequest(
            context=request.context,
            filter=maintenance_v1_work_order_query_service_pb2.FindWorkOrdersRequest.Filter(
                created_after=request.registered_model.audit.created_at,
                labels=dict(request.registered_model.specs),
                owner_id=request.registered_model.components.get(
                    'primary',
                    modelregistry_v1_modelregistry_pb2.RegisteredModelComponent()
                ).component_id,
                region=request.details.destination.region
            )
        )
        response_0 = await deps.clients.maintenance_work_order_query.FindWorkOrders(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = featurestore_v1_feature_value_calculation_service_pb2.CalculateFeatureValueRequest(
            context=request.context,
            details=featurestore_v1_feature_value_calculation_service_pb2.CalculateFeatureValueRequest.Details(
                destination=common_v1_address_pb2.PostalAddress(recipient=request.details.destination.recipient)
            )
        )
        document_1 = MessageToDict(outgoing_1, preserving_proto_field_name=True)
        outgoing_1 = ParseDict(
            document_1,
            featurestore_v1_feature_value_calculation_service_pb2.CalculateFeatureValueRequest()
        )
        response_1 = await deps.clients.featurestore_feature_value_calculation.CalculateFeatureValue(
            outgoing_1,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.result.status
        if returned_0_0:
            response.result.status = returned_0_0
        returned_0_1 = response_0.result.message
        if returned_0_1:
            response.result.message = returned_0_1
        returned_1_0 = response_1.feature_value.correlation_id
        if returned_1_0:
            response.result.correlation_id = returned_1_0
        echoed_0 = request.registered_model_id
        response.registered_model.registered_model_id = echoed_0
        echoed_1 = request.registered_model.code
        response.registered_model.code = echoed_1
        return response


async def handle_estimate_registered_model(
    deps: Dependencies,
    request: modelregistry_v1_registered_model_calculation_service_pb2.EstimateRegisteredModelRequest
) -> modelregistry_v1_registered_model_calculation_service_pb2.EstimateRegisteredModelResponse:
    """Estimates a registered model."""
    response = modelregistry_v1_registered_model_calculation_service_pb2.EstimateRegisteredModelResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('EstimateRegisteredModel', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'EstimateRegisteredModel', {'reason': request.reason})
        await deps.repository.save_registered_model(request.context.tenant_id, request.registered_model)
        response_0 = featurestore_v1_feature_view_query_service_pb2.ResolveFeatureViewsResponse()
        outgoing_0 = featurestore_v1_feature_view_query_service_pb2.ResolveFeatureViewsRequest(context=request.context)
        response_0 = await deps.clients.featurestore_feature_view_query.ResolveFeatureViews(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.result.reference_ids
        response.result.reference_ids.extend(returned_0_0)
        echoed_0 = request.registered_model_id
        response.registered_model.registered_model_id = echoed_0
        echoed_1 = request.registered_model.capacity
        response.registered_model.capacity = echoed_1
        return response


async def handle_explain_registered_model_calculation(
    deps: Dependencies,
    request: modelregistry_v1_registered_model_calculation_service_pb2.ExplainRegisteredModelCalculationRequest
) -> modelregistry_v1_registered_model_calculation_service_pb2.ExplainRegisteredModelCalculationResponse:
    """Explains a registered model."""
    response = modelregistry_v1_registered_model_calculation_service_pb2.ExplainRegisteredModelCalculationResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('ExplainRegisteredModelCalculation', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(
            request.context.tenant_id,
            'ExplainRegisteredModelCalculation',
            {'reason': request.reason}
        )
        await deps.repository.save_registered_model(request.context.tenant_id, request.registered_model)
        response_0 = metrics_v1_dashboard_export_service_pb2.ShareDashboardExportResponse()
        response_1 = featurestore_v1_entity_calculation_service_pb2.CalculateEntityResponse()
        response_2 = metrics_v1_dashboard_export_service_pb2.RetryDashboardExportResponse()
        response_3 = featurestore_v1_feature_value_calculation_service_pb2.SimulateFeatureValueResponse()
        outgoing_0 = metrics_v1_dashboard_export_service_pb2.ShareDashboardExportRequest(
            context=request.context,
            details=metrics_v1_dashboard_export_service_pb2.ShareDashboardExportRequest.Details(
                recipient=common_v1_contact_pb2.ContactInfo(
                    email=request.registered_model.owner.email,
                    name=request.details.contact.name,
                    phone=request.details.contact.phone,
                    preferred_channel=request.details.contact.preferred_channel
                )
            )
        )
        response_0 = await deps.clients.metrics_dashboard_export.ShareDashboardExport(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = featurestore_v1_entity_calculation_service_pb2.CalculateEntityRequest(
            context=request.context,
            entity=featurestore_v1_featurestore_pb2.Entity(
                audit=common_v1_audit_pb2.AuditInfo(created_by=response_0.dashboard.audit.created_by),
                primary_address=common_v1_address_pb2.PostalAddress(
                    lines=list(request.registered_model.address.lines),
                    recipient=request.registered_model.address.recipient
                )
            )
        )
        envelope_1 = AnyMessage()
        envelope_1.Pack(outgoing_1)
        outgoing_1 = featurestore_v1_entity_calculation_service_pb2.CalculateEntityRequest()
        if not envelope_1.Unpack(outgoing_1):
            raise ValueError("partner envelope contains the wrong request type")
        response_1 = await deps.clients.featurestore_entity_calculation.CalculateEntity(
            outgoing_1,
            timeout=deps.settings.timeout
        )
        outgoing_2 = metrics_v1_dashboard_export_service_pb2.RetryDashboardExportRequest(
            context=request.context,
            dashboard=metrics_v1_metrics_pb2.Dashboard(
                card=metrics_v1_metrics_pb2.DashboardCardSettlement(last4=response_0.dashboard.card.last4),
                counterparty=metrics_v1_refs_pb2.MetricAlertRef(
                    display_name=request.registered_model.owner.display_name
                )
            )
        )
        registered_2 = cast(
            metrics_v1_dashboard_export_service_pb2_grpc.DashboardExportServiceStub,
            deps.clients.registry['acme.metrics.v1.DashboardExportService']
        )
        response_2 = await registered_2.RetryDashboardExport(outgoing_2, timeout=deps.settings.timeout)
        command_3 = RegisteredModelCalculationExplainRegisteredModelCalculation3Command(
            context=request.context,
            details_destination_recipient=response_0.dashboard.billing_address.recipient,
            feature_value_measurements_unit=request.registered_model.dimensions.unit
        )
        outgoing_3 = to_registered_model_calculation_explain_registered_model_calculation3_command(command_3)
        response_3 = await deps.clients.featurestore_feature_value_calculation.SimulateFeatureValue(
            outgoing_3,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.dashboard.audit.updated_at
        if returned_0_0.ListFields():
            response.registered_model.audit.updated_at.MergeFrom(returned_0_0)
        returned_0_1 = response_0.result.correlation_id
        if returned_0_1:
            response.result.correlation_id = returned_0_1
        returned_1_0 = response_1.result.reference_ids
        response.result.reference_ids.extend(returned_1_0)
        returned_2_0 = response_2.outcome.message
        if returned_2_0:
            response.result.message = returned_2_0
        returned_3_0 = response_3.result.details
        response.result.details.update(returned_3_0)
        echoed_0 = request.registered_model_id
        response.registered_model.registered_model_id = echoed_0
        echoed_1 = request.registered_model.owner
        response.registered_model.owner.CopyFrom(echoed_1)
        return response


async def handle_get_registered_model_rates(
    deps: Dependencies,
    request: modelregistry_v1_registered_model_calculation_service_pb2.GetRegisteredModelRatesRequest
) -> modelregistry_v1_registered_model_calculation_service_pb2.GetRegisteredModelRatesResponse:
    """Returns a registered model."""
    response = modelregistry_v1_registered_model_calculation_service_pb2.GetRegisteredModelRatesResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('GetRegisteredModelRates', extra={'fields': {'domain': 'modelregistry'}})
        await deps.repository.audit(request.context.tenant_id, 'GetRegisteredModelRates', {})
        response_0 = anomalies_v1_anomaly_validation_service_pb2.PreviewAnomalyResponse()
        outgoing_0 = anomalies_v1_anomaly_validation_service_pb2.PreviewAnomalyRequest(
            anomaly=anomalies_v1_anomalies_pb2.Anomaly(
                assignee=identity_v1_refs_pb2.UserRef(user_id=request.context.actor.user_id),
                requester=common_v1_contact_pb2.ContactInfo(email=request.context.actor.email)
            ),
            context=request.context
        )
        response_0 = await deps.clients.anomalies_anomaly_validation.PreviewAnomaly(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.result.reference_ids
        response.result.reference_ids.extend(returned_0_0)
        echoed_0 = request.registered_model_id
        response.registered_model.registered_model_id = echoed_0
        return response


async def handle_quote_registered_model(
    deps: Dependencies,
    request: modelregistry_v1_registered_model_calculation_service_pb2.QuoteRegisteredModelRequest
) -> modelregistry_v1_registered_model_calculation_service_pb2.QuoteRegisteredModelResponse:
    """Quotes a registered model."""
    response = modelregistry_v1_registered_model_calculation_service_pb2.QuoteRegisteredModelResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('QuoteRegisteredModel', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'QuoteRegisteredModel', {'reason': request.reason})
        await deps.repository.save_registered_model(request.context.tenant_id, request.registered_model)
        response_0 = featurestore_v1_feature_view_query_service_pb2.BrowseFeatureViewsResponse()
        response_1 = featurestore_v1_feature_value_calculation_service_pb2.RecalculateFeatureValuesResponse()
        outgoing_0 = featurestore_v1_feature_view_query_service_pb2.BrowseFeatureViewsRequest(
            context=request.context,
            filter=featurestore_v1_feature_view_query_service_pb2.BrowseFeatureViewsRequest.Filter(
                created_after=request.registered_model.audit.updated_at,
                region=request.details.destination.region
            )
        )
        response_0 = await deps.clients.featurestore_feature_view_query.BrowseFeatureViews(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = featurestore_v1_feature_value_calculation_service_pb2.RecalculateFeatureValuesRequest()
        outgoing_1.context.CopyFrom(request.context)
        field_1_1_part_1 = outgoing_1.feature_value.measurements.add()
        field_1_1_part_1.unit = request.registered_model.dimensions.unit
        outgoing_1.details.destination.lines.extend(list(request.details.destination.lines))
        if request.registered_model.WhichOneof('locator') == 'address':
            outgoing_1.details.destination.locality = request.registered_model.address.locality
        outgoing_1.details.destination.region = request.details.destination.region
        response_1 = await deps.clients.featurestore_feature_value_calculation.RecalculateFeatureValues(
            outgoing_1,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.result.message
        if returned_0_0:
            response.result.message = returned_0_0
        returned_1_0 = response_1.result.status
        if returned_1_0:
            response.result.status = returned_1_0
        returned_1_1 = response_1.breakdown.total
        if returned_1_1.ListFields():
            response.breakdown.total.MergeFrom(returned_1_1)
        echoed_0 = request.registered_model_id
        response.registered_model.registered_model_id = echoed_0
        echoed_1 = request.registered_model.owner
        response.registered_model.owner.CopyFrom(echoed_1)
        return response


async def handle_recalculate_registered_models(
    deps: Dependencies,
    request: modelregistry_v1_registered_model_calculation_service_pb2.RecalculateRegisteredModelsRequest
) -> modelregistry_v1_registered_model_calculation_service_pb2.RecalculateRegisteredModelsResponse:
    """Recalculates a registered model."""
    response = modelregistry_v1_registered_model_calculation_service_pb2.RecalculateRegisteredModelsResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('RecalculateRegisteredModels', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(
            request.context.tenant_id,
            'RecalculateRegisteredModels',
            {'reason': request.reason}
        )
        await deps.repository.save_registered_model(request.context.tenant_id, request.registered_model)
        response_0 = authorization_v1_access_policy_service_pb2.WatchAccessPoliciesResponse()
        response_1 = identity_v1_user_validation_service_pb2.ScoreUserResponse()
        outgoing_0 = authorization_v1_access_policy_service_pb2.WatchAccessPoliciesRequest(
            context=request.context,
            filter=authorization_v1_access_policy_service_pb2.WatchAccessPoliciesRequest.Filter(
                created_after=request.registered_model.audit.created_at,
                region=request.details.destination.region
            ),
            subscriber=common_v1_contact_pb2.ContactInfo(email=request.registered_model.owner.email)
        )
        async for chunk_0 in deps.clients.authorization_access_policy.WatchAccessPolicies(
            outgoing_0,
            timeout=deps.settings.timeout
        ):
            response_0 = chunk_0
        outgoing_1 = identity_v1_user_validation_service_pb2.ScoreUserRequest(
            context=request.context,
            user=identity_v1_identity_pb2.User(
                audit=common_v1_audit_pb2.AuditInfo(
                    created_at=request.registered_model.audit.created_at,
                    etag=request.registered_model.audit.etag
                ),
                primary_address=common_v1_address_pb2.PostalAddress(
                    lines=list(request.details.destination.lines),
                    recipient=request.details.destination.recipient
                )
            )
        )
        port_1: RegisteredModelCalculationRecalculateRegisteredModels1Port = RegisteredModelCalculationRecalculateRegisteredModels1Adapter(
            deps.clients.identity_user_validation,
            deps.settings.timeout
        )
        response_1 = await port_1.execute(outgoing_1)
        returned_1_0 = response_1.user.audit.created_at
        if returned_1_0.ListFields():
            response.registered_model.audit.created_at.MergeFrom(returned_1_0)
        echoed_0 = request.registered_model_id
        response.registered_model.registered_model_id = echoed_0
        echoed_1 = request.details.currency_code
        response.breakdown.currency_code = echoed_1
        return response


async def handle_simulate_registered_model(
    deps: Dependencies,
    request: modelregistry_v1_registered_model_calculation_service_pb2.SimulateRegisteredModelRequest
) -> modelregistry_v1_registered_model_calculation_service_pb2.SimulateRegisteredModelResponse:
    """Simulates a registered model."""
    response = modelregistry_v1_registered_model_calculation_service_pb2.SimulateRegisteredModelResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('SimulateRegisteredModel', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'SimulateRegisteredModel', {'reason': request.reason})
        await deps.repository.save_registered_model(request.context.tenant_id, request.registered_model)
        response_0 = seating_v1_seat_map_service_pb2.WatchSeatMapsResponse()
        response_1 = authorization_v1_access_policy_service_pb2.WatchAccessPoliciesResponse()
        outgoing_0 = seating_v1_seat_map_service_pb2.WatchSeatMapsRequest(
            context=request.context,
            filter=seating_v1_seat_map_service_pb2.WatchSeatMapsRequest.Filter(
                created_after=request.registered_model.audit.updated_at,
                region=request.details.destination.region
            ),
            subscriber=common_v1_contact_pb2.ContactInfo(email=request.registered_model.owner.email)
        )
        async for chunk_0 in deps.clients.seating_seat_map.WatchSeatMaps(outgoing_0, timeout=deps.settings.timeout):
            response_0 = chunk_0
        outgoing_1 = authorization_v1_access_policy_service_pb2.WatchAccessPoliciesRequest(
            context=request.context,
            filter=authorization_v1_access_policy_service_pb2.WatchAccessPoliciesRequest.Filter(
                region=request.registered_model.address.region
            )
        )
        async for chunk_1 in deps.clients.authorization_access_policy.WatchAccessPolicies(
            outgoing_1,
            timeout=deps.settings.timeout
        ):
            response_1 = chunk_1
        echoed_0 = request.registered_model_id
        response.registered_model.registered_model_id = echoed_0
        echoed_1 = request.registered_model.code
        response.registered_model.code = echoed_1
        return response
