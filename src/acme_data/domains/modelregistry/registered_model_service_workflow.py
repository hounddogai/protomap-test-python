"""Application workflow for RegisteredModel ."""

from __future__ import annotations

from functools import partial
from typing import cast
import asyncio
import logging

from acme.audit.v1 import audit_event_service_pb2 as audit_v1_audit_event_service_pb2
from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.documents.v1 import document_service_pb2 as documents_v1_document_service_pb2
from acme.featureflags.v1 import (
    feature_flag_validation_service_pb2 as featureflags_v1_feature_flag_validation_service_pb2,
)
from acme.featureflags.v1 import (
    feature_flag_validation_service_pb2_grpc as featureflags_v1_feature_flag_validation_service_pb2_grpc,
)
from acme.featureflags.v1 import featureflags_pb2 as featureflags_v1_featureflags_pb2
from acme.featurestore.v1 import entity_validation_service_pb2 as featurestore_v1_entity_validation_service_pb2
from acme.featurestore.v1 import feature_value_query_service_pb2 as featurestore_v1_feature_value_query_service_pb2
from acme.featurestore.v1 import (
    feature_view_calculation_service_pb2 as featurestore_v1_feature_view_calculation_service_pb2,
)
from acme.featurestore.v1 import featurestore_pb2 as featurestore_v1_featurestore_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.modelregistry.v1 import (
    deployment_calculation_service_pb2 as modelregistry_v1_deployment_calculation_service_pb2,
)
from acme.modelregistry.v1 import (
    deployment_validation_service_pb2 as modelregistry_v1_deployment_validation_service_pb2,
)
from acme.modelregistry.v1 import modelregistry_pb2 as modelregistry_v1_modelregistry_pb2
from acme.modelregistry.v1 import (
    registered_model_calculation_service_pb2 as modelregistry_v1_registered_model_calculation_service_pb2,
)
from acme.modelregistry.v1 import (
    registered_model_query_service_pb2 as modelregistry_v1_registered_model_query_service_pb2,
)
from acme.modelregistry.v1 import registered_model_service_pb2 as modelregistry_v1_registered_model_service_pb2
from acme.sponsorships.v1 import sponsor_query_service_pb2 as sponsorships_v1_sponsor_query_service_pb2

from acme_data.domains.modelregistry import hooks
from acme_data.domains.modelregistry.adapters import RegisteredModelUpdateRegisteredModel0Adapter
from acme_data.domains.modelregistry.dependencies import Dependencies
from acme_data.domains.modelregistry.models import RegisteredModelCloneRegisteredModel1Command
from acme_data.domains.modelregistry.models import to_registered_model_clone_registered_model1_command
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import run_steps
from acme_data.platform.tenancy import tenant_id
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class RegisteredModelServicerWorkflow:
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    async def handle_batch_create_registered_models(
        self,
        request: modelregistry_v1_registered_model_service_pb2.BatchCreateRegisteredModelsRequest
    ) -> modelregistry_v1_registered_model_service_pb2.BatchCreateRegisteredModelsResponse:
        """Takes a stream of registered models and answers once at the end."""
        deps = self.deps
        response = modelregistry_v1_registered_model_service_pb2.BatchCreateRegisteredModelsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('BatchCreateRegisteredModels', extra={'fields': {'sequence': request.sequence}})
            await deps.repository.audit(
                request.context.tenant_id,
                'BatchCreateRegisteredModels',
                {'sequence': request.sequence}
            )
            if request.WhichOneof('chunk') == 'record':
                await deps.repository.save_registered_model(request.context.tenant_id, request.record)
            response_0 = documents_v1_document_service_pb2.BatchGetDocumentsResponse()
            response_1 = sponsorships_v1_sponsor_query_service_pb2.ResolveSponsorsResponse()
            response_2 = modelregistry_v1_registered_model_query_service_pb2.ResolveRegisteredModelsResponse()
            outgoing_0 = documents_v1_document_service_pb2.BatchGetDocumentsRequest(context=request.context)
            outgoing_1 = sponsorships_v1_sponsor_query_service_pb2.ResolveSponsorsRequest(context=request.context)
            outgoing_2 = modelregistry_v1_registered_model_query_service_pb2.ResolveRegisteredModelsRequest(
                context=request.context
            )
            response_0, response_1, response_2 = await asyncio.gather(
                deps.clients.documents_document.BatchGetDocuments(outgoing_0, timeout=deps.settings.timeout),
                deps.clients.sponsorships_sponsor_query.ResolveSponsors(outgoing_1, timeout=deps.settings.timeout),
                deps.clients.modelregistry_registered_model_query.ResolveRegisteredModels(
                    outgoing_2,
                    timeout=deps.settings.timeout
                ),
            )
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.result.message = returned_0_0
            returned_0_1 = response_0.result.status
            if returned_0_1:
                response.result.status = returned_0_1
            returned_1_0 = response_1.result.status
            if returned_1_0:
                response.result.status = returned_1_0
            returned_1_1 = response_1.result.details
            response.result.details.update(returned_1_1)
            returned_2_0 = response_2.result.correlation_id
            if returned_2_0:
                response.result.correlation_id = returned_2_0
            returned_2_1 = response_2.result.details
            response.result.details.update(returned_2_1)
            return response

    async def handle_batch_get_registered_models(
        self,
        request: modelregistry_v1_registered_model_service_pb2.BatchGetRegisteredModelsRequest
    ) -> modelregistry_v1_registered_model_service_pb2.BatchGetRegisteredModelsResponse:
        """Returns several registered models at once."""
        deps = self.deps
        response = modelregistry_v1_registered_model_service_pb2.BatchGetRegisteredModelsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('BatchGetRegisteredModels', extra={'fields': {'locale': request.context.locale}})
            await deps.repository.audit(
                request.context.tenant_id,
                'BatchGetRegisteredModels',
                {'locale': request.context.locale}
            )
            return response

    async def handle_clone_registered_model(
        self,
        request: modelregistry_v1_registered_model_service_pb2.CloneRegisteredModelRequest
    ) -> modelregistry_v1_registered_model_service_pb2.CloneRegisteredModelResponse:
        """Creates a registered model."""
        deps = self.deps
        response = modelregistry_v1_registered_model_service_pb2.CloneRegisteredModelResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CloneRegisteredModel', extra={'fields': {'request_id': request.request_id}})
            await deps.repository.audit(
                request.context.tenant_id,
                'CloneRegisteredModel',
                {'request_id': request.request_id}
            )
            await deps.repository.save_registered_model(request.context.tenant_id, request.registered_model)
            response_0 = featureflags_v1_feature_flag_validation_service_pb2.ScoreFeatureFlagResponse()
            response_1 = featurestore_v1_feature_view_calculation_service_pb2.EstimateFeatureViewResponse()
            outgoing_0 = featureflags_v1_feature_flag_validation_service_pb2.ScoreFeatureFlagRequest(
                context=request.context,
                details=featureflags_v1_feature_flag_validation_service_pb2.ScoreFeatureFlagRequest.Details(
                    destination=common_v1_address_pb2.PostalAddress(
                        country_code=request.registered_model.address.country_code,
                        postal_code=request.registered_model.address.postal_code
                    )
                ),
                feature_flag=featureflags_v1_featureflags_pb2.FeatureFlag(
                    audit=common_v1_audit_pb2.AuditInfo(updated_at=request.registered_model.audit.updated_at)
                )
            )
            registered_0 = cast(
                featureflags_v1_feature_flag_validation_service_pb2_grpc.FeatureFlagValidationServiceStub,
                deps.clients.registry['acme.featureflags.v1.FeatureFlagValidationService']
            )
            response_0 = await registered_0.ScoreFeatureFlag(outgoing_0, timeout=deps.settings.timeout)
            command_1 = RegisteredModelCloneRegisteredModel1Command(
                context=request.context,
                feature_view_dimensions_unit=request.registered_model.dimensions.unit,
                feature_view_audit_created_by=request.registered_model.audit.created_by
            )
            outgoing_1 = to_registered_model_clone_registered_model1_command(command_1)
            response_1 = await deps.clients.featurestore_feature_view_calculation.EstimateFeatureView(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.feature_flag.owner.display_name
            if returned_0_0:
                response.registered_model.owner.display_name = returned_0_0
            returned_0_1 = response_0.feature_flag.description
            if returned_0_1:
                response.registered_model.components['primary'].description = returned_0_1
            returned_1_0 = response_1.feature_view.dimensions.height
            if returned_1_0:
                response.registered_model.dimensions.height = returned_1_0
            returned_1_1 = response_1.feature_view.category_path
            response.registered_model.category_path.extend(returned_1_1)
            echoed_0 = request.registered_model.specs
            response.registered_model.specs.update(echoed_0)
            echoed_1 = request.registered_model.name
            response.registered_model.name = echoed_1
            return response

    async def handle_create_registered_model(
        self,
        request: modelregistry_v1_registered_model_service_pb2.CreateRegisteredModelRequest
    ) -> modelregistry_v1_registered_model_service_pb2.CreateRegisteredModelResponse:
        """Creates a registered model."""
        deps = self.deps
        response = modelregistry_v1_registered_model_service_pb2.CreateRegisteredModelResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CreateRegisteredModel', extra={'fields': {'request_id': request.request_id}})
            await deps.repository.audit(
                request.context.tenant_id,
                'CreateRegisteredModel',
                {'request_id': request.request_id}
            )
            await deps.repository.save_registered_model(request.context.tenant_id, request.registered_model)
            response_0 = featurestore_v1_feature_value_query_service_pb2.ExportFeatureValuesResponse()
            response_1 = featurestore_v1_entity_validation_service_pb2.LintEntitiesResponse()
            outgoing_0 = featurestore_v1_feature_value_query_service_pb2.ExportFeatureValuesRequest(
                context=request.context,
                filter=featurestore_v1_feature_value_query_service_pb2.ExportFeatureValuesRequest.Filter(
                    created_after=request.registered_model.audit.created_at,
                    region=request.registered_model.address.region
                )
            )
            async for chunk_0 in deps.clients.featurestore_feature_value_query.ExportFeatureValues(
                outgoing_0,
                timeout=deps.settings.timeout
            ):
                response_0 = chunk_0
            outgoing_1 = featurestore_v1_entity_validation_service_pb2.LintEntitiesRequest(
                context=request.context,
                entity=featurestore_v1_featurestore_pb2.Entity(
                    primary_address=common_v1_address_pb2.PostalAddress(
                        locality=request.registered_model.address.locality,
                        recipient=request.registered_model.address.recipient
                    )
                )
            )
            send_1 = partial(deps.clients.featurestore_entity_validation.LintEntities, timeout=deps.settings.timeout)
            response_1 = await send_1(outgoing_1)
            returned_1_0 = response_1.entity.contact.email
            if returned_1_0:
                response.registered_model.owner.email = returned_1_0
            echoed_0 = request.registered_model.status
            response.registered_model.status = echoed_0
            echoed_1 = request.registered_model.capacity
            response.registered_model.capacity = echoed_1
            return response

    async def handle_delete_registered_model(
        self,
        request: modelregistry_v1_registered_model_service_pb2.DeleteRegisteredModelRequest
    ) -> modelregistry_v1_registered_model_service_pb2.DeleteRegisteredModelResponse:
        """Deletes a registered model."""
        deps = self.deps
        response = modelregistry_v1_registered_model_service_pb2.DeleteRegisteredModelResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('DeleteRegisteredModel', extra={'fields': {'force': request.force}})
            await deps.repository.audit(request.context.tenant_id, 'DeleteRegisteredModel', {'force': request.force})
            response_0 = featureflags_v1_feature_flag_validation_service_pb2.LintFeatureFlagsResponse()
            response_1 = modelregistry_v1_deployment_validation_service_pb2.ScoreDeploymentResponse()
            outgoing_0 = featureflags_v1_feature_flag_validation_service_pb2.LintFeatureFlagsRequest(
                context=request.context,
                feature_flag=featureflags_v1_featureflags_pb2.FeatureFlag(
                    audit=common_v1_audit_pb2.AuditInfo(etag=request.etag),
                    block=featureflags_v1_featureflags_pb2.FeatureFlagBlockAction(
                        notify_email=request.context.actor.email,
                        reason=request.reason
                    )
                )
            )
            response_0 = await hooks.registered_model_delete_registered_model0(
                deps.clients.featureflags_feature_flag_validation,
                outgoing_0,
                deps.settings.timeout
            )
            outgoing_1 = modelregistry_v1_deployment_validation_service_pb2.ScoreDeploymentRequest()
            outgoing_1.context.CopyFrom(request.context)
            field_1_1_part_1 = outgoing_1.deployment.participants.add()
            field_1_1_part_1.contact.email = response_0.feature_flag.owner.email
            outgoing_1.deployment.audit.updated_at.CopyFrom(response_0.feature_flag.audit.updated_at)
            outgoing_1.deployment.organizer.display_name = response_0.feature_flag.owner.display_name
            outgoing_1.deployment.organizer.user_id = response_0.feature_flag.owner.user_id
            outgoing_1.context.tenant_id = tenant_id.get()
            response_1 = await deps.clients.modelregistry_deployment_validation.ScoreDeployment(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.outcome.message
            if returned_0_0:
                response.result.message = returned_0_0
            returned_1_0 = response_1.result.message
            if returned_1_0:
                response.result.message = returned_1_0
            return response

    async def handle_get_registered_model(
        self,
        request: modelregistry_v1_registered_model_service_pb2.GetRegisteredModelRequest
    ) -> modelregistry_v1_registered_model_service_pb2.GetRegisteredModelResponse:
        """Returns a registered model."""
        deps = self.deps
        response = modelregistry_v1_registered_model_service_pb2.GetRegisteredModelResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('GetRegisteredModel', extra={'fields': {'domain': 'modelregistry'}})
            await deps.repository.audit(request.context.tenant_id, 'GetRegisteredModel', {})
            response_0 = modelregistry_v1_deployment_validation_service_pb2.PreviewDeploymentResponse()
            response_1 = audit_v1_audit_event_service_pb2.ListAuditEventsResponse()
            outgoing_0 = modelregistry_v1_deployment_validation_service_pb2.PreviewDeploymentRequest(
                context=request.context,
                deployment=modelregistry_v1_modelregistry_pb2.Deployment(
                    organizer=identity_v1_refs_pb2.UserRef(user_id=request.context.actor.user_id),
                    participants=[
                        modelregistry_v1_modelregistry_pb2.DeploymentParticipant(
                            contact=common_v1_contact_pb2.ContactInfo(email=request.context.actor.email)
                        )
                    ]
                ),
                details=modelregistry_v1_deployment_validation_service_pb2.PreviewDeploymentRequest.Details(
                    locale=request.context.locale
                )
            )
            response_0 = await deps.clients.modelregistry_deployment_validation.PreviewDeployment(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = audit_v1_audit_event_service_pb2.ListAuditEventsRequest(
                context=request.context,
                filter=audit_v1_audit_event_service_pb2.ListAuditEventsRequest.Filter(
                    created_after=response_0.deployment.audit.updated_at,
                    region=response_0.deployment.location.region
                )
            )
            steps_1 = [
                partial(deps.clients.audit_audit_event.ListAuditEvents, outgoing_1, timeout=deps.settings.timeout)
            ]
            results_1 = await run_steps(steps_1)
            response_1 = results_1[-1]
            returned_0_0 = response_0.result.correlation_id
            if returned_0_0:
                response.result.correlation_id = returned_0_0
            returned_1_0 = response_1.result.details
            response.result.details.update(returned_1_0)
            returned_1_1 = response_1.result.status
            if returned_1_1:
                response.result.status = returned_1_1
            echoed_0 = request.registered_model_id
            response.registered_model.registered_model_id = echoed_0
            return response

    async def handle_update_registered_model(
        self,
        request: modelregistry_v1_registered_model_service_pb2.UpdateRegisteredModelRequest
    ) -> modelregistry_v1_registered_model_service_pb2.UpdateRegisteredModelResponse:
        """Changes a registered model."""
        deps = self.deps
        response = modelregistry_v1_registered_model_service_pb2.UpdateRegisteredModelResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('UpdateRegisteredModel', extra={'fields': {'allow_missing': request.allow_missing}})
            await deps.repository.audit(
                request.context.tenant_id,
                'UpdateRegisteredModel',
                {'allow_missing': request.allow_missing}
            )
            await deps.repository.save_registered_model(request.context.tenant_id, request.registered_model)
            response_0 = modelregistry_v1_registered_model_calculation_service_pb2.RecalculateRegisteredModelsResponse()
            response_1 = modelregistry_v1_deployment_calculation_service_pb2.CalculateDeploymentResponse()
            response_2 = featurestore_v1_feature_view_calculation_service_pb2.EstimateFeatureViewResponse()
            response_3 = modelregistry_v1_registered_model_calculation_service_pb2.QuoteRegisteredModelResponse()
            outgoing_0 = modelregistry_v1_registered_model_calculation_service_pb2.RecalculateRegisteredModelsRequest(
                context=request.context,
                details=modelregistry_v1_registered_model_calculation_service_pb2.RecalculateRegisteredModelsRequest.Details(
                    destination=common_v1_address_pb2.PostalAddress(region=request.registered_model.address.region)
                )
            )
            response_0 = await RegisteredModelUpdateRegisteredModel0Adapter(
                deps.clients.modelregistry_registered_model_calculation,
                deps.settings.timeout
            )(outgoing_0)
            outgoing_1 = modelregistry_v1_deployment_calculation_service_pb2.CalculateDeploymentRequest(
                context=request.context,
                deployment=modelregistry_v1_modelregistry_pb2.Deployment(
                    audit=common_v1_audit_pb2.AuditInfo(etag=request.registered_model.audit.etag)
                ),
                details=modelregistry_v1_deployment_calculation_service_pb2.CalculateDeploymentRequest.Details(
                    destination=common_v1_address_pb2.PostalAddress(
                        locality=response_0.registered_model.address.locality
                    )
                )
            )
            response_1 = cast(modelregistry_v1_deployment_calculation_service_pb2.CalculateDeploymentResponse, await deps.bus.request(
                'acme.modelregistry.v1.RegisteredModelService/UpdateRegisteredModel/1', outgoing_1, deps.settings.timeout,
            ))
            outgoing_2 = featurestore_v1_feature_view_calculation_service_pb2.EstimateFeatureViewRequest(
                context=request.context,
                feature_view=featurestore_v1_featurestore_pb2.FeatureView(
                    audit=common_v1_audit_pb2.AuditInfo(updated_at=response_0.registered_model.audit.updated_at),
                    dimensions=featurestore_v1_featurestore_pb2.FeatureViewDimensions(
                        unit=request.registered_model.dimensions.unit,
                        width=response_0.registered_model.dimensions.width
                    )
                )
            )
            response_2 = await deps.clients.featurestore_feature_view_calculation.EstimateFeatureView(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            outgoing_3 = modelregistry_v1_registered_model_calculation_service_pb2.QuoteRegisteredModelRequest(
                context=request.context,
                registered_model=modelregistry_v1_modelregistry_pb2.RegisteredModel(
                    address=common_v1_address_pb2.PostalAddress(
                        postal_code=response_0.registered_model.address.postal_code,
                        recipient=response_0.registered_model.address.recipient
                    ),
                    owner=identity_v1_refs_pb2.UserRef(email=response_1.deployment.organizer.email)
                )
            )
            method_name_3 = 'QuoteRegisteredModel'
            response_3 = await getattr(
                deps.clients.modelregistry_registered_model_calculation,
                method_name_3
            )(outgoing_3, timeout=deps.settings.timeout)
            returned_0_0 = response_0.registered_model.audit.updated_by
            if returned_0_0:
                response.registered_model.audit.updated_by = returned_0_0
            returned_0_1 = response_0.registered_model.dimensions.height
            if returned_0_1:
                response.registered_model.dimensions.height = returned_0_1
            returned_1_0 = response_1.deployment.audit.updated_at
            if returned_1_0.ListFields():
                response.registered_model.audit.updated_at.MergeFrom(returned_1_0)
            returned_2_0 = response_2.result.details
            response.result.details.update(returned_2_0)
            returned_2_1 = response_2.result.message
            if returned_2_1:
                response.result.message = returned_2_1
            returned_3_0 = response_3.registered_model.dimensions.length
            if returned_3_0:
                response.registered_model.dimensions.length = returned_3_0
            echoed_0 = request.registered_model.code
            response.registered_model.code = echoed_0
            echoed_1 = request.registered_model.status
            response.registered_model.status = echoed_1
            return response
