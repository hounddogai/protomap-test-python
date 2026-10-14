"""Reusable transport mixin for RegisteredModelValidationService."""

from __future__ import annotations

from collections.abc import AsyncIterator
from functools import partial
from typing import Any
from typing import cast
import logging

from google.protobuf.any_pb2 import Any as AnyMessage
from google.protobuf.json_format import MessageToDict
from google.protobuf.json_format import ParseDict
import grpc

from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.datasets.v1 import refs_pb2 as datasets_v1_refs_pb2
from acme.featurestore.v1 import entity_validation_service_pb2 as featurestore_v1_entity_validation_service_pb2
from acme.featurestore.v1 import (
    feature_value_validation_service_pb2 as featurestore_v1_feature_value_validation_service_pb2,
)
from acme.featurestore.v1 import feature_view_service_pb2 as featurestore_v1_feature_view_service_pb2
from acme.featurestore.v1 import featurestore_pb2 as featurestore_v1_featurestore_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.lineage.v1 import lineage_node_calculation_service_pb2 as lineage_v1_lineage_node_calculation_service_pb2
from acme.metrics.v1 import dashboard_validation_service_pb2 as metrics_v1_dashboard_validation_service_pb2
from acme.metrics.v1 import metric_alert_notification_service_pb2 as metrics_v1_metric_alert_notification_service_pb2
from acme.metrics.v1 import metrics_pb2 as metrics_v1_metrics_pb2
from acme.metrics.v1 import refs_pb2 as metrics_v1_refs_pb2
from acme.modelregistry.v1 import (
    model_version_calculation_service_pb2 as modelregistry_v1_model_version_calculation_service_pb2,
)
from acme.modelregistry.v1 import modelregistry_pb2 as modelregistry_v1_modelregistry_pb2
from acme.modelregistry.v1 import (
    registered_model_calculation_service_pb2 as modelregistry_v1_registered_model_calculation_service_pb2,
)
from acme.modelregistry.v1 import (
    registered_model_calculation_service_pb2_grpc as modelregistry_v1_registered_model_calculation_service_pb2_grpc,
)
from acme.modelregistry.v1 import (
    registered_model_validation_service_pb2 as modelregistry_v1_registered_model_validation_service_pb2,
)

from acme_data.domains.modelregistry import hooks
from acme_data.domains.modelregistry.adapters import RegisteredModelValidationValidateRegisteredModel2Adapter
from acme_data.domains.modelregistry.adapters import RegisteredModelValidationValidateRegisteredModel2Port
from acme_data.domains.modelregistry.dependencies import Dependencies
from acme_data.domains.modelregistry.models import RegisteredModelValidationPreviewRegisteredModel1Command
from acme_data.domains.modelregistry.models import RegisteredModelValidationScoreRegisteredModel0Command
from acme_data.domains.modelregistry.models import to_registered_model_validation_preview_registered_model1_command
from acme_data.domains.modelregistry.models import to_registered_model_validation_score_registered_model0_command
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import run_steps
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_id
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class RegisteredModelValidationServicerHandlers:
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    async def CheckRegisteredModelEligibility(
        self, request: modelregistry_v1_registered_model_validation_service_pb2.CheckRegisteredModelEligibilityRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_registered_model_validation_service_pb2.CheckRegisteredModelEligibilityResponse:
        """Checks a registered model."""
        return await self.handle_check_registered_model_eligibility(request)

    @rpc_errors
    async def ExplainRegisteredModelDecision(
        self, request: modelregistry_v1_registered_model_validation_service_pb2.ExplainRegisteredModelDecisionRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_registered_model_validation_service_pb2.ExplainRegisteredModelDecisionResponse:
        """Explains a registered model."""
        return await self.handle_explain_registered_model_decision(request)

    @rpc_errors
    @retry_transient
    async def GetRegisteredModelRules(
        self, request: modelregistry_v1_registered_model_validation_service_pb2.GetRegisteredModelRulesRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_registered_model_validation_service_pb2.GetRegisteredModelRulesResponse:
        """Returns a registered model."""
        return await self.handle_get_registered_model_rules(request)

    @rpc_errors
    async def LintRegisteredModels(
        self, request: modelregistry_v1_registered_model_validation_service_pb2.LintRegisteredModelsRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_registered_model_validation_service_pb2.LintRegisteredModelsResponse:
        """Lints a registered model."""
        return await self.handle_lint_registered_models(request)

    @rpc_errors
    async def NormalizeRegisteredModel(
        self, request: modelregistry_v1_registered_model_validation_service_pb2.NormalizeRegisteredModelRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_registered_model_validation_service_pb2.NormalizeRegisteredModelResponse:
        """Normalizes a registered model."""
        return await self.handle_normalize_registered_model(request)

    @rpc_errors
    async def PreviewRegisteredModel(
        self, request: modelregistry_v1_registered_model_validation_service_pb2.PreviewRegisteredModelRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_registered_model_validation_service_pb2.PreviewRegisteredModelResponse:
        """Previews a registered model."""
        return await self.handle_preview_registered_model(request)

    @rpc_errors
    async def ScoreRegisteredModel(
        self, request: modelregistry_v1_registered_model_validation_service_pb2.ScoreRegisteredModelRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_registered_model_validation_service_pb2.ScoreRegisteredModelResponse:
        """Scores a registered model."""
        return await self.handle_score_registered_model(request)

    @rpc_errors
    async def ValidateRegisteredModel(
        self, request: modelregistry_v1_registered_model_validation_service_pb2.ValidateRegisteredModelRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_registered_model_validation_service_pb2.ValidateRegisteredModelResponse:
        """Validates a registered model."""
        return await self.handle_validate_registered_model(request)

    async def handle_check_registered_model_eligibility(
        self,
        request: modelregistry_v1_registered_model_validation_service_pb2.CheckRegisteredModelEligibilityRequest
    ) -> modelregistry_v1_registered_model_validation_service_pb2.CheckRegisteredModelEligibilityResponse:
        """Checks a registered model."""
        deps = self.deps
        response = modelregistry_v1_registered_model_validation_service_pb2.CheckRegisteredModelEligibilityResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CheckRegisteredModelEligibility', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'CheckRegisteredModelEligibility',
                {'reason': request.reason}
            )
            await deps.repository.save_registered_model(request.context.tenant_id, request.registered_model)
            response_0 = metrics_v1_metric_alert_notification_service_pb2.StreamMetricAlertNoticesResponse()
            response_1 = modelregistry_v1_registered_model_calculation_service_pb2.GetRegisteredModelRatesResponse()
            response_2 = modelregistry_v1_registered_model_calculation_service_pb2.EstimateRegisteredModelResponse()
            outgoing_0 = metrics_v1_metric_alert_notification_service_pb2.StreamMetricAlertNoticesRequest(
                context=request.context,
                subscriber=common_v1_contact_pb2.ContactInfo(email=request.details.contact.email)
            )
            async for chunk_0 in deps.clients.metrics_metric_alert_notification.StreamMetricAlertNotices(
                outgoing_0,
                timeout=deps.settings.timeout
            ):
                response_0 = chunk_0
            outgoing_1 = modelregistry_v1_registered_model_calculation_service_pb2.GetRegisteredModelRatesRequest(
                context=request.context,
                registered_model_id=request.registered_model.registered_model_id
            )
            steps_1 = [
                partial(
                    deps.clients.modelregistry_registered_model_calculation.GetRegisteredModelRates,
                    outgoing_1,
                    timeout=deps.settings.timeout
                )
            ]
            results_1 = await run_steps(steps_1)
            response_1 = results_1[-1]
            outgoing_2 = modelregistry_v1_registered_model_calculation_service_pb2.EstimateRegisteredModelRequest()
            outgoing_2.context.CopyFrom(request.context)
            if request.registered_model.WhichOneof('locator') == 'address':
                outgoing_2.details.destination.locality = request.registered_model.address.locality
            if response_1.registered_model.WhichOneof('locator') == 'address':
                outgoing_2.registered_model.address.postal_code = response_1.registered_model.address.postal_code
            response_2 = await deps.clients.modelregistry_registered_model_calculation.EstimateRegisteredModel(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            returned_1_0 = response_1.registered_model.owner.user_id
            if returned_1_0:
                response.registered_model.owner.user_id = returned_1_0
            returned_2_0 = response_2.registered_model.category_path
            response.registered_model.category_path.extend(returned_2_0)
            echoed_0 = request.registered_model_id
            response.registered_model.registered_model_id = echoed_0
            echoed_1 = request.registered_model.name
            response.registered_model.name = echoed_1
            return response

    async def handle_explain_registered_model_decision(
        self,
        request: modelregistry_v1_registered_model_validation_service_pb2.ExplainRegisteredModelDecisionRequest
    ) -> modelregistry_v1_registered_model_validation_service_pb2.ExplainRegisteredModelDecisionResponse:
        """Explains a registered model."""
        deps = self.deps
        response = modelregistry_v1_registered_model_validation_service_pb2.ExplainRegisteredModelDecisionResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ExplainRegisteredModelDecision', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ExplainRegisteredModelDecision',
                {'reason': request.reason}
            )
            await deps.repository.save_registered_model(request.context.tenant_id, request.registered_model)
            response_0 = modelregistry_v1_registered_model_calculation_service_pb2.CalculateRegisteredModelResponse()
            response_1 = modelregistry_v1_registered_model_calculation_service_pb2.QuoteRegisteredModelResponse()
            outgoing_0 = modelregistry_v1_registered_model_calculation_service_pb2.CalculateRegisteredModelRequest(
                context=request.context,
                registered_model=modelregistry_v1_modelregistry_pb2.RegisteredModel(
                    owner=identity_v1_refs_pb2.UserRef(user_id=request.registered_model.owner.user_id)
                )
            )
            response_0 = cast(modelregistry_v1_registered_model_calculation_service_pb2.CalculateRegisteredModelResponse, await deps.bus.request(
                'acme.modelregistry.v1.RegisteredModelValidationService/ExplainRegisteredModelDecision/0', outgoing_0, deps.settings.timeout,
            ))
            outgoing_1 = modelregistry_v1_registered_model_calculation_service_pb2.QuoteRegisteredModelRequest(
                context=request.context,
                registered_model=modelregistry_v1_modelregistry_pb2.RegisteredModel(
                    address=common_v1_address_pb2.PostalAddress(
                        postal_code=response_0.registered_model.address.postal_code
                    ),
                    audit=common_v1_audit_pb2.AuditInfo(created_by=response_0.registered_model.audit.created_by),
                    components={
                        'primary': modelregistry_v1_modelregistry_pb2.RegisteredModelComponent(
                            description=request.registered_model.components.get(
                                'primary',
                                modelregistry_v1_modelregistry_pb2.RegisteredModelComponent()
                            ).description
                        )
                    }
                )
            )
            response_1 = await deps.clients.modelregistry_registered_model_calculation.QuoteRegisteredModel(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.registered_model.owner.user_id
            if returned_0_0:
                response.registered_model.owner.user_id = returned_0_0
            returned_0_1 = response_0.registered_model.audit.created_at
            if returned_0_1.ListFields():
                response.registered_model.audit.created_at.MergeFrom(returned_0_1)
            returned_1_0 = response_1.registered_model.components.get(
                'primary',
                modelregistry_v1_modelregistry_pb2.RegisteredModelComponent()
            ).quantity
            if returned_1_0:
                response.registered_model.components['primary'].quantity = returned_1_0
            echoed_0 = request.registered_model_id
            response.registered_model.registered_model_id = echoed_0
            echoed_1 = request.registered_model.status
            response.registered_model.status = echoed_1
            return response

    async def handle_get_registered_model_rules(
        self,
        request: modelregistry_v1_registered_model_validation_service_pb2.GetRegisteredModelRulesRequest
    ) -> modelregistry_v1_registered_model_validation_service_pb2.GetRegisteredModelRulesResponse:
        """Returns a registered model."""
        deps = self.deps
        response = modelregistry_v1_registered_model_validation_service_pb2.GetRegisteredModelRulesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('GetRegisteredModelRules', extra={'fields': {'domain': 'modelregistry'}})
            await deps.repository.audit(request.context.tenant_id, 'GetRegisteredModelRules', {})
            response_0 = modelregistry_v1_registered_model_calculation_service_pb2.CalculateRegisteredModelResponse()
            response_1 = modelregistry_v1_registered_model_calculation_service_pb2.EstimateRegisteredModelResponse()
            outgoing_0 = modelregistry_v1_registered_model_calculation_service_pb2.CalculateRegisteredModelRequest(
                context=request.context,
                registered_model_id=request.registered_model_id
            )
            response_0 = await deps.clients.modelregistry_registered_model_calculation.CalculateRegisteredModel(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            fields_1: dict[str, Any] = {
                'context': request.context,
                'details': {
                    'destination': {
                        'postal_code': response_0.registered_model.address.postal_code,
                        'recipient': response_0.registered_model.address.recipient
                    }
                },
                'registered_model': {'audit': {'created_at': response_0.registered_model.audit.created_at}}
            }
            outgoing_1 = modelregistry_v1_registered_model_calculation_service_pb2.EstimateRegisteredModelRequest(**fields_1)
            response_1 = await deps.clients.modelregistry_registered_model_calculation.EstimateRegisteredModel(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.registered_model.dimensions.length
            if returned_0_0:
                response.registered_model.dimensions.length = returned_0_0
            returned_0_1 = response_0.registered_model.components.get(
                'primary',
                modelregistry_v1_modelregistry_pb2.RegisteredModelComponent()
            ).description
            if returned_0_1:
                response.registered_model.components['primary'].description = returned_0_1
            returned_1_0 = response_1.registered_model.owner.user_id
            if returned_1_0:
                response.registered_model.owner.user_id = returned_1_0
            returned_1_1 = response_1.registered_model.dimensions.width
            if returned_1_1:
                response.registered_model.dimensions.width = returned_1_1
            echoed_0 = request.registered_model_id
            response.registered_model.registered_model_id = echoed_0
            return response

    async def handle_lint_registered_models(
        self,
        request: modelregistry_v1_registered_model_validation_service_pb2.LintRegisteredModelsRequest
    ) -> modelregistry_v1_registered_model_validation_service_pb2.LintRegisteredModelsResponse:
        """Lints a registered model."""
        deps = self.deps
        response = modelregistry_v1_registered_model_validation_service_pb2.LintRegisteredModelsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('LintRegisteredModels', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'LintRegisteredModels', {'reason': request.reason})
            await deps.repository.save_registered_model(request.context.tenant_id, request.registered_model)
            response_0 = modelregistry_v1_registered_model_calculation_service_pb2.RecalculateRegisteredModelsResponse()
            response_1 = modelregistry_v1_registered_model_calculation_service_pb2.SimulateRegisteredModelResponse()
            outgoing_0 = modelregistry_v1_registered_model_calculation_service_pb2.RecalculateRegisteredModelsRequest(
                context=request.context,
                details=modelregistry_v1_registered_model_calculation_service_pb2.RecalculateRegisteredModelsRequest.Details(
                    destination=common_v1_address_pb2.PostalAddress(
                        lines=list(request.registered_model.address.lines),
                        postal_code=request.registered_model.address.postal_code
                    )
                ),
                registered_model=modelregistry_v1_modelregistry_pb2.RegisteredModel(
                    dimensions=modelregistry_v1_modelregistry_pb2.RegisteredModelDimensions(
                        weight=request.registered_model.dimensions.weight
                    )
                )
            )
            document_0 = MessageToDict(outgoing_0, preserving_proto_field_name=True)
            outgoing_0 = ParseDict(
                document_0,
                modelregistry_v1_registered_model_calculation_service_pb2.RecalculateRegisteredModelsRequest()
            )
            response_0 = await deps.clients.modelregistry_registered_model_calculation.RecalculateRegisteredModels(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = modelregistry_v1_registered_model_calculation_service_pb2.SimulateRegisteredModelRequest()
            outgoing_1.context.CopyFrom(request.context)
            if request.registered_model.WhichOneof('locator') == 'address':
                outgoing_1.details.destination.postal_code = request.registered_model.address.postal_code
            outgoing_1.registered_model.dimensions.weight = response_0.registered_model.dimensions.weight
            outgoing_1.registered_model.dimensions.height = request.registered_model.dimensions.height
            response_1 = await deps.clients.modelregistry_registered_model_calculation.SimulateRegisteredModel(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.registered_model.category_path
            response.registered_model.category_path.extend(returned_0_0)
            returned_1_0 = response_1.result.status
            if returned_1_0:
                response.outcome.status = returned_1_0
            returned_1_1 = response_1.registered_model.name
            if returned_1_1:
                response.registered_model.name = returned_1_1
            echoed_0 = request.registered_model_id
            response.registered_model.registered_model_id = echoed_0
            echoed_1 = request.registered_model.code
            response.registered_model.code = echoed_1
            return response

    async def handle_normalize_registered_model(
        self,
        request: modelregistry_v1_registered_model_validation_service_pb2.NormalizeRegisteredModelRequest
    ) -> modelregistry_v1_registered_model_validation_service_pb2.NormalizeRegisteredModelResponse:
        """Normalizes a registered model."""
        deps = self.deps
        response = modelregistry_v1_registered_model_validation_service_pb2.NormalizeRegisteredModelResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('NormalizeRegisteredModel', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'NormalizeRegisteredModel',
                {'reason': request.reason}
            )
            await deps.repository.save_registered_model(request.context.tenant_id, request.registered_model)
            response_0 = lineage_v1_lineage_node_calculation_service_pb2.ExplainLineageNodeCalculationResponse()
            response_1 = featurestore_v1_feature_view_service_pb2.ListFeatureViewsResponse()
            outgoing_0 = lineage_v1_lineage_node_calculation_service_pb2.ExplainLineageNodeCalculationRequest()
            outgoing_0.context.CopyFrom(request.context)
            field_0_1_part_1 = outgoing_0.lineage_node.children.add()
            field_0_1_part_2 = field_0_1_part_1.children.add()
            field_0_1_part_2.location.region = request.registered_model.address.region
            merged_0 = lineage_v1_lineage_node_calculation_service_pb2.ExplainLineageNodeCalculationRequest()
            merged_0.MergeFrom(outgoing_0)
            outgoing_0.CopyFrom(merged_0)
            response_0 = await deps.clients.lineage_lineage_node_calculation.ExplainLineageNodeCalculation(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = featurestore_v1_feature_view_service_pb2.ListFeatureViewsRequest(
                context=request.context,
                filter=featurestore_v1_feature_view_service_pb2.ListFeatureViewsRequest.Filter(
                    created_after=request.registered_model.audit.updated_at,
                    region=response_0.lineage_node.location.region
                )
            )
            envelope_1 = AnyMessage()
            envelope_1.Pack(outgoing_1)
            outgoing_1 = featurestore_v1_feature_view_service_pb2.ListFeatureViewsRequest()
            if not envelope_1.Unpack(outgoing_1):
                raise ValueError("partner envelope contains the wrong request type")
            response_1 = await deps.clients.featurestore_feature_view.ListFeatureViews(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.details
            response.result.details.update(returned_0_0)
            returned_1_0 = response_1.result.message
            if returned_1_0:
                response.result.message = returned_1_0
            returned_1_1 = response_1.result.reference_ids
            response.result.reference_ids.extend(returned_1_1)
            echoed_0 = request.registered_model_id
            response.registered_model.registered_model_id = echoed_0
            echoed_1 = request.registered_model.name
            response.registered_model.name = echoed_1
            return response

    async def handle_preview_registered_model(
        self,
        request: modelregistry_v1_registered_model_validation_service_pb2.PreviewRegisteredModelRequest
    ) -> modelregistry_v1_registered_model_validation_service_pb2.PreviewRegisteredModelResponse:
        """Previews a registered model."""
        deps = self.deps
        response = modelregistry_v1_registered_model_validation_service_pb2.PreviewRegisteredModelResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('PreviewRegisteredModel', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'PreviewRegisteredModel', {'reason': request.reason})
            await deps.repository.save_registered_model(request.context.tenant_id, request.registered_model)
            response_0 = modelregistry_v1_registered_model_calculation_service_pb2.GetRegisteredModelRatesResponse()
            response_1 = modelregistry_v1_model_version_calculation_service_pb2.SimulateModelVersionResponse()
            outgoing_0 = modelregistry_v1_registered_model_calculation_service_pb2.GetRegisteredModelRatesRequest(
                context=request.context,
                registered_model_id=request.registered_model.registered_model_id
            )
            registered_0 = cast(
                modelregistry_v1_registered_model_calculation_service_pb2_grpc.RegisteredModelCalculationServiceStub,
                deps.clients.registry['acme.modelregistry.v1.RegisteredModelCalculationService']
            )
            response_0 = await registered_0.GetRegisteredModelRates(outgoing_0, timeout=deps.settings.timeout)
            command_1 = RegisteredModelValidationPreviewRegisteredModel1Command(
                context=request.context,
                model_version_subject_display_name=request.registered_model.owner.display_name,
                model_version_subject_email=request.registered_model.owner.email,
                details_destination_locality=response_0.registered_model.address.locality,
                model_version_measurements_unit=response_0.registered_model.dimensions.unit
            )
            outgoing_1 = to_registered_model_validation_preview_registered_model1_command(command_1)
            response_1 = await deps.clients.modelregistry_model_version_calculation.SimulateModelVersion(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.result.message = returned_0_0
            returned_1_0 = response_1.result.message
            if returned_1_0:
                response.outcome.message = returned_1_0
            returned_1_1 = response_1.model_version.correlation_id
            if returned_1_1:
                response.result.correlation_id = returned_1_1
            echoed_0 = request.registered_model_id
            response.registered_model.registered_model_id = echoed_0
            echoed_1 = request.registered_model.specs
            response.registered_model.specs.update(echoed_1)
            return response

    async def handle_score_registered_model(
        self,
        request: modelregistry_v1_registered_model_validation_service_pb2.ScoreRegisteredModelRequest
    ) -> modelregistry_v1_registered_model_validation_service_pb2.ScoreRegisteredModelResponse:
        """Scores a registered model."""
        deps = self.deps
        response = modelregistry_v1_registered_model_validation_service_pb2.ScoreRegisteredModelResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ScoreRegisteredModel', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'ScoreRegisteredModel', {'reason': request.reason})
            await deps.repository.save_registered_model(request.context.tenant_id, request.registered_model)
            response_0 = featurestore_v1_entity_validation_service_pb2.PreviewEntityResponse()
            response_1 = modelregistry_v1_registered_model_calculation_service_pb2.QuoteRegisteredModelResponse()
            command_0 = RegisteredModelValidationScoreRegisteredModel0Command.model_validate(
                {
                    'context': request.context,
                    'entity_primary_address_country_code': request.registered_model.address.country_code,
                    'entity_primary_address_region': request.registered_model.address.region
                }
            )
            outgoing_0 = to_registered_model_validation_score_registered_model0_command(command_0)
            response_0 = await deps.clients.featurestore_entity_validation.PreviewEntity(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = modelregistry_v1_registered_model_calculation_service_pb2.QuoteRegisteredModelRequest(
                context=request.context,
                details=modelregistry_v1_registered_model_calculation_service_pb2.QuoteRegisteredModelRequest.Details(
                    destination=common_v1_address_pb2.PostalAddress(
                        country_code=request.details.destination.country_code
                    )
                )
            )
            send_1 = partial(
                deps.clients.modelregistry_registered_model_calculation.QuoteRegisteredModel,
                timeout=deps.settings.timeout
            )
            response_1 = await send_1(outgoing_1)
            returned_0_0 = response_0.result.correlation_id
            if returned_0_0:
                response.result.correlation_id = returned_0_0
            returned_1_0 = response_1.registered_model.owner.user_id
            if returned_1_0:
                response.registered_model.owner.user_id = returned_1_0
            echoed_0 = request.registered_model_id
            response.registered_model.registered_model_id = echoed_0
            echoed_1 = request.registered_model.status
            response.registered_model.status = echoed_1
            return response

    async def handle_validate_registered_model(
        self,
        request: modelregistry_v1_registered_model_validation_service_pb2.ValidateRegisteredModelRequest
    ) -> modelregistry_v1_registered_model_validation_service_pb2.ValidateRegisteredModelResponse:
        """Validates a registered model."""
        deps = self.deps
        response = modelregistry_v1_registered_model_validation_service_pb2.ValidateRegisteredModelResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ValidateRegisteredModel', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ValidateRegisteredModel',
                {'reason': request.reason}
            )
            await deps.repository.save_registered_model(request.context.tenant_id, request.registered_model)
            response_0 = metrics_v1_dashboard_validation_service_pb2.CheckDashboardEligibilityResponse()
            response_1 = modelregistry_v1_registered_model_calculation_service_pb2.RecalculateRegisteredModelsResponse()
            response_2 = featurestore_v1_feature_value_validation_service_pb2.ExplainFeatureValueDecisionResponse()
            outgoing_0 = metrics_v1_dashboard_validation_service_pb2.CheckDashboardEligibilityRequest(
                context=request.context,
                dashboard=metrics_v1_metrics_pb2.Dashboard(
                    audit=common_v1_audit_pb2.AuditInfo(etag=request.registered_model.audit.etag),
                    billing_address=common_v1_address_pb2.PostalAddress(
                        recipient=request.registered_model.address.recipient
                    ),
                    counterparty=metrics_v1_refs_pb2.MetricAlertRef(
                        display_name=request.registered_model.owner.display_name
                    ),
                    lines=[
                        metrics_v1_metrics_pb2.DashboardLine(
                            quantity=request.registered_model.components.get(
                                'primary',
                                modelregistry_v1_modelregistry_pb2.RegisteredModelComponent()
                            ).quantity
                        )
                    ]
                )
            )
            response_0 = await hooks.registered_model_validation_validate_registered_model0(
                deps.clients.metrics_dashboard_validation,
                outgoing_0,
                deps.settings.timeout
            )
            outgoing_1 = modelregistry_v1_registered_model_calculation_service_pb2.RecalculateRegisteredModelsRequest()
            outgoing_1.context.CopyFrom(request.context)
            outgoing_1.registered_model.address.recipient = response_0.dashboard.billing_address.recipient
            outgoing_1.registered_model.owner.email = request.registered_model.owner.email
            outgoing_1.details.destination.lines.extend(list(response_0.dashboard.billing_address.lines))
            outgoing_1.context.tenant_id = tenant_id.get()
            response_1 = await deps.clients.modelregistry_registered_model_calculation.RecalculateRegisteredModels(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = featurestore_v1_feature_value_validation_service_pb2.ExplainFeatureValueDecisionRequest(
                context=request.context,
                feature_value=featurestore_v1_featurestore_pb2.FeatureValue(
                    subject=datasets_v1_refs_pb2.DatasetRef(display_name=response_1.registered_model.owner.display_name)
                )
            )
            port_2: RegisteredModelValidationValidateRegisteredModel2Port = RegisteredModelValidationValidateRegisteredModel2Adapter(
                deps.clients.featurestore_feature_value_validation,
                deps.settings.timeout
            )
            response_2 = await port_2.execute(outgoing_2)
            returned_0_0 = response_0.result.status
            if returned_0_0:
                response.result.status = returned_0_0
            returned_1_0 = response_1.result.correlation_id
            if returned_1_0:
                response.result.correlation_id = returned_1_0
            returned_1_1 = response_1.result.details
            response.result.details.update(returned_1_1)
            returned_2_0 = response_2.outcome.status
            if returned_2_0:
                response.outcome.status = returned_2_0
            echoed_0 = request.registered_model_id
            response.registered_model.registered_model_id = echoed_0
            echoed_1 = request.registered_model.status
            response.registered_model.status = echoed_1
            return response
