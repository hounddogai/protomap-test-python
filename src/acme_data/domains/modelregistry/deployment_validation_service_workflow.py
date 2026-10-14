"""Application workflow for Deployment Validation."""

from __future__ import annotations

from collections.abc import Awaitable
from collections.abc import Callable
from functools import partial
from typing import cast
import asyncio
import logging

from google.protobuf.json_format import MessageToJson
from google.protobuf.json_format import Parse

from acme.anomalies.v1 import detector_query_service_pb2 as anomalies_v1_detector_query_service_pb2
from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.customers.v1 import refs_pb2 as customers_v1_refs_pb2
from acme.featureflags.v1 import (
    feature_flag_validation_service_pb2 as featureflags_v1_feature_flag_validation_service_pb2,
)
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.ledger.v1 import ledger_account_service_pb2 as ledger_v1_ledger_account_service_pb2
from acme.modelregistry.v1 import (
    deployment_calculation_service_pb2 as modelregistry_v1_deployment_calculation_service_pb2,
)
from acme.modelregistry.v1 import (
    deployment_validation_service_pb2 as modelregistry_v1_deployment_validation_service_pb2,
)
from acme.modelregistry.v1 import (
    model_version_calculation_service_pb2 as modelregistry_v1_model_version_calculation_service_pb2,
)
from acme.modelregistry.v1 import (
    model_version_validation_service_pb2 as modelregistry_v1_model_version_validation_service_pb2,
)
from acme.modelregistry.v1 import (
    model_version_validation_service_pb2_grpc as modelregistry_v1_model_version_validation_service_pb2_grpc,
)
from acme.modelregistry.v1 import modelregistry_pb2 as modelregistry_v1_modelregistry_pb2
from acme.modelregistry.v1 import (
    registered_model_validation_service_pb2 as modelregistry_v1_registered_model_validation_service_pb2,
)
from acme.search.v1 import search_index_validation_service_pb2 as search_v1_search_index_validation_service_pb2
from acme.search.v1 import search_pb2 as search_v1_search_pb2
from acme.venues.v1 import venue_validation_service_pb2 as venues_v1_venue_validation_service_pb2

from acme_data.domains.modelregistry import hooks
from acme_data.domains.modelregistry.adapters import DeploymentValidationScoreDeployment0Adapter
from acme_data.domains.modelregistry.dependencies import Dependencies
from acme_data.domains.modelregistry.models import DeploymentValidationExplainDeploymentDecision1Command
from acme_data.domains.modelregistry.models import to_deployment_validation_explain_deployment_decision1_command
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import run_steps
from acme_data.platform.tenancy import tenant_id
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class DeploymentValidationServicerWorkflow:
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    async def handle_check_deployment_eligibility(
        self,
        request: modelregistry_v1_deployment_validation_service_pb2.CheckDeploymentEligibilityRequest
    ) -> modelregistry_v1_deployment_validation_service_pb2.CheckDeploymentEligibilityResponse:
        """Checks a deployment."""
        deps = self.deps
        response = modelregistry_v1_deployment_validation_service_pb2.CheckDeploymentEligibilityResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CheckDeploymentEligibility', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'CheckDeploymentEligibility',
                {'reason': request.reason}
            )
            await deps.repository.save_deployment(request.context.tenant_id, request.deployment)
            response_0 = modelregistry_v1_model_version_validation_service_pb2.ScoreModelVersionResponse()
            response_1 = modelregistry_v1_model_version_calculation_service_pb2.CompareModelVersionOptionsResponse()
            response_2 = featureflags_v1_feature_flag_validation_service_pb2.NormalizeFeatureFlagResponse()
            outgoing_0 = modelregistry_v1_model_version_validation_service_pb2.ScoreModelVersionRequest(
                context=request.context,
                details=modelregistry_v1_model_version_validation_service_pb2.ScoreModelVersionRequest.Details(
                    destination=common_v1_address_pb2.PostalAddress(
                        lines=list(request.deployment.location.lines),
                        locality=request.deployment.location.locality,
                        recipient=request.deployment.location.recipient
                    )
                )
            )
            document_0 = MessageToJson(outgoing_0, preserving_proto_field_name=True)
            outgoing_0 = Parse(
                document_0,
                modelregistry_v1_model_version_validation_service_pb2.ScoreModelVersionRequest()
            )
            response_0 = await deps.clients.modelregistry_model_version_validation.ScoreModelVersion(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = modelregistry_v1_model_version_calculation_service_pb2.CompareModelVersionOptionsRequest()
            outgoing_1.context.CopyFrom(request.context)
            outgoing_1.details.destination.lines.extend(list(request.deployment.location.lines))
            outgoing_1.details.destination.country_code = request.deployment.location.country_code
            outgoing_1.details.destination.locality = request.deployment.location.locality
            outgoing_1.model_version.subject.display_name = response_0.model_version.subject.display_name
            merged_1 = modelregistry_v1_model_version_calculation_service_pb2.CompareModelVersionOptionsRequest()
            merged_1.MergeFrom(outgoing_1)
            outgoing_1.CopyFrom(merged_1)
            response_1 = await deps.clients.modelregistry_model_version_calculation.CompareModelVersionOptions(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            requests_2: list[featureflags_v1_feature_flag_validation_service_pb2.NormalizeFeatureFlagRequest] = []
            for item_2 in request.deployment.participants:
                outgoing_2 = featureflags_v1_feature_flag_validation_service_pb2.NormalizeFeatureFlagRequest(
                    context=request.context,
                    details=featureflags_v1_feature_flag_validation_service_pb2.NormalizeFeatureFlagRequest.Details(
                        contact=common_v1_contact_pb2.ContactInfo(
                            email=item_2.contact.email,
                            preferred_channel=item_2.contact.preferred_channel
                        )
                    )
                )
                requests_2.append(outgoing_2)
            replies_2 = await asyncio.gather(*(
                deps.clients.featureflags_feature_flag_validation.NormalizeFeatureFlag(
                    entry,
                    timeout=deps.settings.timeout
                ) for entry in requests_2
            ))
            if replies_2:
                response_2 = replies_2[-1]
            returned_0_0 = response_0.model_version.subject.email
            returned_0_0_part_1 = response.deployment.participants.add()
            if returned_0_0:
                returned_0_0_part_1.contact.email = returned_0_0
            returned_0_1 = response_0.result.details
            response.result.details.update(returned_0_1)
            returned_1_0 = response_1.result.details
            response.result.details.update(returned_1_0)
            returned_1_1 = response_1.model_version.subject.email
            returned_1_1_part_1 = response.deployment.participants.add()
            if returned_1_1:
                returned_1_1_part_1.contact.email = returned_1_1
            echoed_0 = request.deployment_id
            response.deployment.deployment_id = echoed_0
            echoed_1 = request.deployment.status
            response.deployment.status = echoed_1
            return response

    async def handle_explain_deployment_decision(
        self,
        request: modelregistry_v1_deployment_validation_service_pb2.ExplainDeploymentDecisionRequest
    ) -> modelregistry_v1_deployment_validation_service_pb2.ExplainDeploymentDecisionResponse:
        """Explains a deployment."""
        deps = self.deps
        response = modelregistry_v1_deployment_validation_service_pb2.ExplainDeploymentDecisionResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ExplainDeploymentDecision', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ExplainDeploymentDecision',
                {'reason': request.reason}
            )
            await deps.repository.save_deployment(request.context.tenant_id, request.deployment)
            response_0 = modelregistry_v1_model_version_validation_service_pb2.PreviewModelVersionResponse()
            response_1 = venues_v1_venue_validation_service_pb2.LintVenuesResponse()
            outgoing_0 = modelregistry_v1_model_version_validation_service_pb2.PreviewModelVersionRequest(
                context=request.context,
                details=modelregistry_v1_model_version_validation_service_pb2.PreviewModelVersionRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(
                        email=request.details.contact.email,
                        preferred_channel=request.details.contact.preferred_channel
                    )
                ),
                model_version=modelregistry_v1_modelregistry_pb2.ModelVersion(
                    subject=customers_v1_refs_pb2.CustomerRef(email=request.deployment.organizer.email)
                )
            )
            registered_0 = cast(
                modelregistry_v1_model_version_validation_service_pb2_grpc.ModelVersionValidationServiceStub,
                deps.clients.registry['acme.modelregistry.v1.ModelVersionValidationService']
            )
            response_0 = await registered_0.PreviewModelVersion(outgoing_0, timeout=deps.settings.timeout)
            command_1 = DeploymentValidationExplainDeploymentDecision1Command(
                context=request.context,
                details_contact_email=request.details.contact.email,
                venue_address_locality=request.deployment.location.locality
            )
            outgoing_1 = to_deployment_validation_explain_deployment_decision1_command(command_1)
            response_1 = await deps.clients.venues_venue_validation.LintVenues(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.model_version.subject.email
            returned_0_0_part_1 = response.deployment.participants.add()
            if returned_0_0:
                returned_0_0_part_1.contact.email = returned_0_0
            returned_0_1 = response_0.outcome.status
            if returned_0_1:
                response.outcome.status = returned_0_1
            returned_1_0 = response_1.venue.address.recipient
            if returned_1_0:
                response.deployment.location.recipient = returned_1_0
            echoed_0 = request.deployment_id
            response.deployment.deployment_id = echoed_0
            echoed_1 = request.deployment.organizer
            response.deployment.organizer.CopyFrom(echoed_1)
            return response

    async def handle_get_deployment_rules(
        self,
        request: modelregistry_v1_deployment_validation_service_pb2.GetDeploymentRulesRequest
    ) -> modelregistry_v1_deployment_validation_service_pb2.GetDeploymentRulesResponse:
        """Returns a deployment."""
        deps = self.deps
        response = modelregistry_v1_deployment_validation_service_pb2.GetDeploymentRulesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('GetDeploymentRules', extra={'fields': {'domain': 'modelregistry'}})
            await deps.repository.audit(request.context.tenant_id, 'GetDeploymentRules', {})
            response_0 = modelregistry_v1_model_version_validation_service_pb2.CheckModelVersionEligibilityResponse()
            outgoing_0 = modelregistry_v1_model_version_validation_service_pb2.CheckModelVersionEligibilityRequest(
                context=request.context,
                details=modelregistry_v1_model_version_validation_service_pb2.CheckModelVersionEligibilityRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(email=request.context.actor.email),
                    locale=request.context.locale
                ),
                model_version=modelregistry_v1_modelregistry_pb2.ModelVersion(correlation_id=request.deployment_id)
            )
            response_0 = await deps.clients.modelregistry_model_version_validation.CheckModelVersionEligibility(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.details
            response.result.details.update(returned_0_0)
            echoed_0 = request.deployment_id
            response.deployment.deployment_id = echoed_0
            return response

    async def handle_lint_deployments(
        self,
        request: modelregistry_v1_deployment_validation_service_pb2.LintDeploymentsRequest
    ) -> modelregistry_v1_deployment_validation_service_pb2.LintDeploymentsResponse:
        """Lints a deployment."""
        deps = self.deps
        response = modelregistry_v1_deployment_validation_service_pb2.LintDeploymentsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('LintDeployments', extra={'fields': {'deployment_id': request.deployment_id}})
            await deps.repository.audit(
                request.context.tenant_id,
                'LintDeployments',
                {'deployment_id': request.deployment_id}
            )
            await deps.repository.save_deployment(request.context.tenant_id, request.deployment)
            response_0 = modelregistry_v1_deployment_calculation_service_pb2.QuoteDeploymentResponse()
            outgoing_0 = modelregistry_v1_deployment_calculation_service_pb2.QuoteDeploymentRequest()
            outgoing_0.context.CopyFrom(request.context)
            if request.deployment.WhichOneof('recurrence') == 'daily':
                outgoing_0.deployment.daily.interval = request.deployment.daily.interval
            outgoing_0.deployment.location.postal_code = request.deployment.location.postal_code
            outgoing_0.deployment.organizer.user_id = request.deployment.organizer.user_id
            outgoing_0.details.destination.recipient = request.deployment.location.recipient
            response_0 = await deps.clients.modelregistry_deployment_calculation.QuoteDeployment(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.deployment.deployment_id
            if returned_0_0:
                response.deployment.deployment_id = returned_0_0
            echoed_0 = request.deployment.organizer
            response.deployment.organizer.CopyFrom(echoed_0)
            echoed_1 = request.deployment.title
            response.deployment.title = echoed_1
            return response

    async def handle_normalize_deployment(
        self,
        request: modelregistry_v1_deployment_validation_service_pb2.NormalizeDeploymentRequest
    ) -> modelregistry_v1_deployment_validation_service_pb2.NormalizeDeploymentResponse:
        """Normalizes a deployment."""
        deps = self.deps
        response = modelregistry_v1_deployment_validation_service_pb2.NormalizeDeploymentResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('NormalizeDeployment', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'NormalizeDeployment', {'reason': request.reason})
            await deps.repository.save_deployment(request.context.tenant_id, request.deployment)
            response_0 = modelregistry_v1_model_version_validation_service_pb2.ExplainModelVersionDecisionResponse()
            outgoing_0 = modelregistry_v1_model_version_validation_service_pb2.ExplainModelVersionDecisionRequest(
                context=request.context,
                details=modelregistry_v1_model_version_validation_service_pb2.ExplainModelVersionDecisionRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(
                        preferred_channel=request.details.contact.preferred_channel
                    )
                ),
                model_version=modelregistry_v1_modelregistry_pb2.ModelVersion(
                    subject=customers_v1_refs_pb2.CustomerRef(email=request.details.contact.email)
                )
            )
            response_0 = await hooks.deployment_validation_normalize_deployment0(
                deps.clients.modelregistry_model_version_validation,
                outgoing_0,
                deps.settings.timeout
            )
            returned_0_0 = response_0.result.details
            response.result.details.update(returned_0_0)
            returned_0_1 = response_0.outcome.reference_id
            if returned_0_1:
                response.outcome.reference_id = returned_0_1
            echoed_0 = request.deployment_id
            response.deployment.deployment_id = echoed_0
            echoed_1 = request.deployment.window
            response.deployment.window.CopyFrom(echoed_1)
            return response

    async def handle_preview_deployment(
        self,
        request: modelregistry_v1_deployment_validation_service_pb2.PreviewDeploymentRequest
    ) -> modelregistry_v1_deployment_validation_service_pb2.PreviewDeploymentResponse:
        """Previews a deployment."""
        deps = self.deps
        response = modelregistry_v1_deployment_validation_service_pb2.PreviewDeploymentResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('PreviewDeployment', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'PreviewDeployment', {'reason': request.reason})
            await deps.repository.save_deployment(request.context.tenant_id, request.deployment)
            response_0 = modelregistry_v1_registered_model_validation_service_pb2.ValidateRegisteredModelResponse()
            response_1 = anomalies_v1_detector_query_service_pb2.FindDetectorsResponse()
            response_2 = modelregistry_v1_model_version_validation_service_pb2.ValidateModelVersionResponse()
            outgoing_0 = modelregistry_v1_registered_model_validation_service_pb2.ValidateRegisteredModelRequest()
            outgoing_0.context.CopyFrom(request.context)
            outgoing_0.registered_model.audit.etag = request.deployment.audit.etag
            outgoing_0.registered_model.address.lines.extend(list(request.deployment.location.lines))
            outgoing_0.context.tenant_id = tenant_id.get()
            response_0 = await deps.clients.modelregistry_registered_model_validation.ValidateRegisteredModel(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            callbacks_1: list[
                Callable[[], Awaitable[anomalies_v1_detector_query_service_pb2.FindDetectorsResponse]]
            ] = []
            for item_1 in request.deployment.participants:
                outgoing_1 = anomalies_v1_detector_query_service_pb2.FindDetectorsRequest(
                    context=request.context,
                    filter=anomalies_v1_detector_query_service_pb2.FindDetectorsRequest.Filter(
                        created_after=response_0.registered_model.audit.updated_at,
                        labels=dict(response_0.registered_model.specs),
                        owner_id=item_1.participant_id,
                        region=request.deployment.location.region
                    )
                )
                async def send_1(
                    payload: anomalies_v1_detector_query_service_pb2.FindDetectorsRequest = outgoing_1
                ) -> anomalies_v1_detector_query_service_pb2.FindDetectorsResponse:
                    return await deps.clients.anomalies_detector_query.FindDetectors(
                        payload,
                        timeout=deps.settings.timeout
                    )
                callbacks_1.append(send_1)
            for callback_1 in callbacks_1:
                response_1 = await callback_1()
            outgoing_2 = modelregistry_v1_model_version_validation_service_pb2.ValidateModelVersionRequest(
                context=request.context,
                model_version=modelregistry_v1_modelregistry_pb2.ModelVersion(
                    measurements=[
                        modelregistry_v1_modelregistry_pb2.ModelVersionMeasurement(
                            unit=response_0.registered_model.dimensions.unit
                        )
                    ]
                )
            )
            steps_2 = [
                partial(
                    deps.clients.modelregistry_model_version_validation.ValidateModelVersion,
                    outgoing_2,
                    timeout=deps.settings.timeout
                )
            ]
            results_2 = await run_steps(steps_2)
            response_2 = results_2[-1]
            returned_0_0 = response_0.result.details
            response.result.details.update(returned_0_0)
            returned_0_1 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_1)
            returned_2_0 = response_2.outcome.next_steps
            response.outcome.next_steps.extend(returned_2_0)
            echoed_0 = request.deployment_id
            response.deployment.deployment_id = echoed_0
            echoed_1 = request.deployment.window
            response.deployment.window.CopyFrom(echoed_1)
            return response

    async def handle_score_deployment(
        self,
        request: modelregistry_v1_deployment_validation_service_pb2.ScoreDeploymentRequest
    ) -> modelregistry_v1_deployment_validation_service_pb2.ScoreDeploymentResponse:
        """Scores a deployment."""
        deps = self.deps
        response = modelregistry_v1_deployment_validation_service_pb2.ScoreDeploymentResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ScoreDeployment', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'ScoreDeployment', {'reason': request.reason})
            await deps.repository.save_deployment(request.context.tenant_id, request.deployment)
            response_0 = search_v1_search_index_validation_service_pb2.ScoreSearchIndexResponse()
            response_1 = ledger_v1_ledger_account_service_pb2.SearchLedgerAccountsResponse()
            outgoing_0 = search_v1_search_index_validation_service_pb2.ScoreSearchIndexRequest(
                context=request.context,
                search_index=search_v1_search_pb2.SearchIndex(
                    address=common_v1_address_pb2.PostalAddress(lines=list(request.details.destination.lines)),
                    audit=common_v1_audit_pb2.AuditInfo(etag=request.deployment.audit.etag),
                    owner=identity_v1_refs_pb2.UserRef(display_name=request.deployment.organizer.display_name)
                )
            )
            response_0 = await DeploymentValidationScoreDeployment0Adapter(
                deps.clients.search_search_index_validation,
                deps.settings.timeout
            )(outgoing_0)
            outgoing_1 = ledger_v1_ledger_account_service_pb2.SearchLedgerAccountsRequest(
                context=request.context,
                filter=ledger_v1_ledger_account_service_pb2.SearchLedgerAccountsRequest.Filter(
                    region=request.details.destination.region
                )
            )
            response_1 = cast(ledger_v1_ledger_account_service_pb2.SearchLedgerAccountsResponse, await deps.bus.request(
                'acme.modelregistry.v1.DeploymentValidationService/ScoreDeployment/1', outgoing_1, deps.settings.timeout,
            ))
            returned_0_0 = response_0.result.details
            response.result.details.update(returned_0_0)
            returned_0_1 = response_0.result.message
            if returned_0_1:
                response.result.message = returned_0_1
            returned_1_0 = response_1.result.correlation_id
            if returned_1_0:
                response.result.correlation_id = returned_1_0
            echoed_0 = request.deployment_id
            response.deployment.deployment_id = echoed_0
            echoed_1 = request.deployment.status
            response.deployment.status = echoed_1
            return response

    async def handle_validate_deployment(
        self,
        request: modelregistry_v1_deployment_validation_service_pb2.ValidateDeploymentRequest
    ) -> modelregistry_v1_deployment_validation_service_pb2.ValidateDeploymentResponse:
        """Validates a deployment."""
        deps = self.deps
        response = modelregistry_v1_deployment_validation_service_pb2.ValidateDeploymentResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ValidateDeployment', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'ValidateDeployment', {'reason': request.reason})
            await deps.repository.save_deployment(request.context.tenant_id, request.deployment)
            response_0 = modelregistry_v1_model_version_validation_service_pb2.ValidateModelVersionResponse()
            async for item_0 in async_messages(request.deployment.participants):
                outgoing_0 = modelregistry_v1_model_version_validation_service_pb2.ValidateModelVersionRequest(
                    context=request.context,
                    details=modelregistry_v1_model_version_validation_service_pb2.ValidateModelVersionRequest.Details(
                        contact=common_v1_contact_pb2.ContactInfo(name=item_0.contact.name, phone=item_0.contact.phone)
                    )
                )
                response_0 = await deps.clients.modelregistry_model_version_validation.ValidateModelVersion(
                    outgoing_0,
                    timeout=deps.settings.timeout
                )
            echoed_0 = request.deployment_id
            response.deployment.deployment_id = echoed_0
            echoed_1 = request.deployment.window
            response.deployment.window.CopyFrom(echoed_1)
            return response
