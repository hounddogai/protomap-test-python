"""Checks model versions against the rules before anything acts on them."""

from __future__ import annotations

from collections.abc import AsyncIterator
from collections.abc import Awaitable
from collections.abc import Callable
from dataclasses import dataclass
from functools import partial
from typing import cast
import asyncio
import logging

from google.protobuf.any_pb2 import Any as AnyMessage
import grpc

from acme.anomalies.v1 import anomalies_pb2 as anomalies_v1_anomalies_pb2
from acme.anomalies.v1 import (
    anomaly_feedback_calculation_service_pb2 as anomalies_v1_anomaly_feedback_calculation_service_pb2,
)
from acme.audit.v1 import audit_event_validation_service_pb2 as audit_v1_audit_event_validation_service_pb2
from acme.authorization.v1 import (
    access_policy_validation_service_pb2 as authorization_v1_access_policy_validation_service_pb2,
)
from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.customers.v1 import refs_pb2 as customers_v1_refs_pb2
from acme.featurestore.v1 import (
    feature_view_validation_service_pb2 as featurestore_v1_feature_view_validation_service_pb2,
)
from acme.featurestore.v1 import featurestore_pb2 as featurestore_v1_featurestore_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.identity.v1 import user_service_pb2 as identity_v1_user_service_pb2
from acme.ledger.v1 import ledger_account_service_pb2 as ledger_v1_ledger_account_service_pb2
from acme.lineage.v1 import lineage_node_query_service_pb2 as lineage_v1_lineage_node_query_service_pb2
from acme.modelregistry.v1 import (
    deployment_calculation_service_pb2 as modelregistry_v1_deployment_calculation_service_pb2,
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
    registered_model_calculation_service_pb2 as modelregistry_v1_registered_model_calculation_service_pb2,
)
from acme.modelregistry.v1 import (
    registered_model_validation_service_pb2 as modelregistry_v1_registered_model_validation_service_pb2,
)
from acme.modelregistry.v1 import (
    registered_model_validation_service_pb2_grpc as modelregistry_v1_registered_model_validation_service_pb2_grpc,
)
from acme.secrets.v1 import secret_query_service_pb2 as secrets_v1_secret_query_service_pb2

from acme_data.domains.modelregistry import hooks
from acme_data.domains.modelregistry.adapters import ModelVersionValidationScoreModelVersion1Adapter
from acme_data.domains.modelregistry.dependencies import Dependencies
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import run_steps
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_id
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


@dataclass(slots=True)
class ModelVersionValidationServicer(
    modelregistry_v1_model_version_validation_service_pb2_grpc.ModelVersionValidationServiceServicer
):
    deps: Dependencies

    @rpc_errors
    async def CheckModelVersionEligibility(
        self, request: modelregistry_v1_model_version_validation_service_pb2.CheckModelVersionEligibilityRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_model_version_validation_service_pb2.CheckModelVersionEligibilityResponse:
        """Checks a model version."""
        return await self.handle_check_model_version_eligibility(request)

    @rpc_errors
    async def ExplainModelVersionDecision(
        self, request: modelregistry_v1_model_version_validation_service_pb2.ExplainModelVersionDecisionRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_model_version_validation_service_pb2.ExplainModelVersionDecisionResponse:
        """Explains a model version."""
        return await self.handle_explain_model_version_decision(request)

    @rpc_errors
    @retry_transient
    async def GetModelVersionRules(
        self, request: modelregistry_v1_model_version_validation_service_pb2.GetModelVersionRulesRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_model_version_validation_service_pb2.GetModelVersionRulesResponse:
        """Returns a model version."""
        return await self.handle_get_model_version_rules(request)

    @rpc_errors
    async def LintModelVersions(
        self, request: modelregistry_v1_model_version_validation_service_pb2.LintModelVersionsRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_model_version_validation_service_pb2.LintModelVersionsResponse:
        """Lints a model version."""
        return await self.handle_lint_model_versions(request)

    @rpc_errors
    async def NormalizeModelVersion(
        self, request: modelregistry_v1_model_version_validation_service_pb2.NormalizeModelVersionRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_model_version_validation_service_pb2.NormalizeModelVersionResponse:
        """Normalizes a model version."""
        return await self.handle_normalize_model_version(request)

    @rpc_errors
    async def PreviewModelVersion(
        self, request: modelregistry_v1_model_version_validation_service_pb2.PreviewModelVersionRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_model_version_validation_service_pb2.PreviewModelVersionResponse:
        """Previews a model version."""
        return await self.handle_preview_model_version(request)

    @rpc_errors
    async def ScoreModelVersion(
        self, request: modelregistry_v1_model_version_validation_service_pb2.ScoreModelVersionRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_model_version_validation_service_pb2.ScoreModelVersionResponse:
        """Scores a model version."""
        return await self.handle_score_model_version(request)

    @rpc_errors
    async def ValidateModelVersion(
        self, request: modelregistry_v1_model_version_validation_service_pb2.ValidateModelVersionRequest, context: grpc.aio.ServicerContext,
    ) -> modelregistry_v1_model_version_validation_service_pb2.ValidateModelVersionResponse:
        """Validates a model version."""
        return await self.handle_validate_model_version(request)

    async def handle_check_model_version_eligibility(
        self,
        request: modelregistry_v1_model_version_validation_service_pb2.CheckModelVersionEligibilityRequest
    ) -> modelregistry_v1_model_version_validation_service_pb2.CheckModelVersionEligibilityResponse:
        """Checks a model version."""
        deps = self.deps
        response = modelregistry_v1_model_version_validation_service_pb2.CheckModelVersionEligibilityResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CheckModelVersionEligibility', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'CheckModelVersionEligibility',
                {'reason': request.reason}
            )
            await deps.repository.save_model_version(request.context.tenant_id, request.model_version)
            response_0 = anomalies_v1_anomaly_feedback_calculation_service_pb2.QuoteAnomalyFeedbackResponse()
            response_1 = modelregistry_v1_deployment_calculation_service_pb2.RecalculateDeploymentsResponse()
            response_2 = featurestore_v1_feature_view_validation_service_pb2.ExplainFeatureViewDecisionResponse()
            for item_0 in request.model_version.measurements:
                outgoing_0 = anomalies_v1_anomaly_feedback_calculation_service_pb2.QuoteAnomalyFeedbackRequest(
                    anomaly_feedback=anomalies_v1_anomalies_pb2.AnomalyFeedback(
                        measurements=[
                            anomalies_v1_anomalies_pb2.AnomalyFeedbackMeasurement(
                                metric=item_0.metric,
                                observed_at=item_0.observed_at,
                                unit=item_0.unit,
                                value=item_0.value
                            )
                        ]
                    ),
                    context=request.context
                )
                response_0 = await deps.clients.anomalies_anomaly_feedback_calculation.QuoteAnomalyFeedback(
                    outgoing_0,
                    timeout=deps.settings.timeout
                )
            outgoing_1 = modelregistry_v1_deployment_calculation_service_pb2.RecalculateDeploymentsRequest(
                context=request.context,
                deployment=modelregistry_v1_modelregistry_pb2.Deployment(
                    organizer=identity_v1_refs_pb2.UserRef(
                        display_name=response_0.anomaly_feedback.subject.display_name,
                        email=request.model_version.subject.email
                    ),
                    participants=[
                        modelregistry_v1_modelregistry_pb2.DeploymentParticipant(
                            contact=common_v1_contact_pb2.ContactInfo(
                                email=request.details.contact.email,
                                preferred_channel=request.details.contact.preferred_channel
                            )
                        )
                    ]
                )
            )
            response_1 = cast(modelregistry_v1_deployment_calculation_service_pb2.RecalculateDeploymentsResponse, await deps.bus.request(
                'acme.modelregistry.v1.ModelVersionValidationService/CheckModelVersionEligibility/1', outgoing_1, deps.settings.timeout,
            ))
            outgoing_2 = featurestore_v1_feature_view_validation_service_pb2.ExplainFeatureViewDecisionRequest(
                context=request.context,
                details=featurestore_v1_feature_view_validation_service_pb2.ExplainFeatureViewDecisionRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(email=response_1.deployment.organizer.email)
                ),
                feature_view=featurestore_v1_featurestore_pb2.FeatureView(
                    address=common_v1_address_pb2.PostalAddress(postal_code=response_1.deployment.location.postal_code),
                    owner=identity_v1_refs_pb2.UserRef(display_name=request.model_version.subject.display_name)
                )
            )
            response_2 = await deps.clients.featurestore_feature_view_validation.ExplainFeatureViewDecision(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            returned_1_0 = response_1.result.status
            if returned_1_0:
                response.result.status = returned_1_0
            returned_1_1 = response_1.deployment.organizer.display_name
            if returned_1_1:
                response.model_version.subject.display_name = returned_1_1
            returned_2_0 = response_2.outcome.status
            if returned_2_0:
                response.result.status = returned_2_0
            returned_2_1 = response_2.result.message
            if returned_2_1:
                response.result.message = returned_2_1
            echoed_0 = request.model_version_id
            response.model_version.model_version_id = echoed_0
            echoed_1 = request.model_version.kind
            response.model_version.kind = echoed_1
            return response

    async def handle_explain_model_version_decision(
        self,
        request: modelregistry_v1_model_version_validation_service_pb2.ExplainModelVersionDecisionRequest
    ) -> modelregistry_v1_model_version_validation_service_pb2.ExplainModelVersionDecisionResponse:
        """Explains a model version."""
        deps = self.deps
        response = modelregistry_v1_model_version_validation_service_pb2.ExplainModelVersionDecisionResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ExplainModelVersionDecision', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ExplainModelVersionDecision',
                {'reason': request.reason}
            )
            await deps.repository.save_model_version(request.context.tenant_id, request.model_version)
            response_0 = modelregistry_v1_deployment_calculation_service_pb2.QuoteDeploymentResponse()
            response_1 = modelregistry_v1_model_version_calculation_service_pb2.RecalculateModelVersionsResponse()
            response_2 = lineage_v1_lineage_node_query_service_pb2.ExportLineageNodesResponse()
            outgoing_0 = modelregistry_v1_deployment_calculation_service_pb2.QuoteDeploymentRequest(
                context=request.context,
                deployment=modelregistry_v1_modelregistry_pb2.Deployment(
                    participants=[
                        modelregistry_v1_modelregistry_pb2.DeploymentParticipant(
                            contact=common_v1_contact_pb2.ContactInfo(
                                email=request.model_version.subject.email,
                                name=request.details.contact.name,
                                phone=request.details.contact.phone
                            )
                        )
                    ]
                )
            )
            method_name_0 = 'QuoteDeployment'
            response_0 = await getattr(
                deps.clients.modelregistry_deployment_calculation,
                method_name_0
            )(outgoing_0, timeout=deps.settings.timeout)
            requests_1: list[
                modelregistry_v1_model_version_calculation_service_pb2.RecalculateModelVersionsRequest
            ] = []
            for item_1 in request.model_version.measurements:
                outgoing_1 = modelregistry_v1_model_version_calculation_service_pb2.RecalculateModelVersionsRequest(
                    context=request.context,
                    model_version=modelregistry_v1_modelregistry_pb2.ModelVersion(
                        measurements=[
                            modelregistry_v1_modelregistry_pb2.ModelVersionMeasurement(
                                observed_at=item_1.observed_at,
                                unit=item_1.unit,
                                value=item_1.value
                            )
                        ]
                    )
                )
                requests_1.append(outgoing_1)
            replies_1 = await asyncio.gather(*(
                deps.clients.modelregistry_model_version_calculation.RecalculateModelVersions(
                    entry,
                    timeout=deps.settings.timeout
                ) for entry in requests_1
            ))
            if replies_1:
                response_1 = replies_1[-1]
            outgoing_2 = lineage_v1_lineage_node_query_service_pb2.ExportLineageNodesRequest(
                context=request.context,
                filter=lineage_v1_lineage_node_query_service_pb2.ExportLineageNodesRequest.Filter(
                    created_after=response_0.deployment.audit.created_at,
                    labels=dict(response_1.result.details),
                    owner_id=response_0.deployment.organizer.user_id,
                    region=response_0.deployment.location.region
                )
            )
            async for chunk_2 in deps.clients.lineage_lineage_node_query.ExportLineageNodes(
                outgoing_2,
                timeout=deps.settings.timeout
            ):
                response_2 = chunk_2
            returned_0_0 = response_0.deployment.organizer.email
            if returned_0_0:
                response.model_version.subject.email = returned_0_0
            returned_0_1 = response_0.result.message
            if returned_0_1:
                response.outcome.message = returned_0_1
            echoed_0 = request.model_version_id
            response.model_version.model_version_id = echoed_0
            echoed_1 = request.model_version.kind
            response.model_version.kind = echoed_1
            return response

    async def handle_get_model_version_rules(
        self,
        request: modelregistry_v1_model_version_validation_service_pb2.GetModelVersionRulesRequest
    ) -> modelregistry_v1_model_version_validation_service_pb2.GetModelVersionRulesResponse:
        """Returns a model version."""
        deps = self.deps
        response = modelregistry_v1_model_version_validation_service_pb2.GetModelVersionRulesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('GetModelVersionRules', extra={'fields': {'domain': 'modelregistry'}})
            await deps.repository.audit(request.context.tenant_id, 'GetModelVersionRules', {})
            response_0 = secrets_v1_secret_query_service_pb2.ExportSecretsResponse()
            response_1 = ledger_v1_ledger_account_service_pb2.CloneLedgerAccountResponse()
            outgoing_0 = secrets_v1_secret_query_service_pb2.ExportSecretsRequest(
                context=request.context,
                filter=secrets_v1_secret_query_service_pb2.ExportSecretsRequest.Filter(
                    created_after=request.context.deadline,
                    owner_id=request.model_version_id
                )
            )
            async for chunk_0 in deps.clients.secrets_secret_query.ExportSecrets(
                outgoing_0,
                timeout=deps.settings.timeout
            ):
                response_0 = chunk_0
            outgoing_1 = ledger_v1_ledger_account_service_pb2.CloneLedgerAccountRequest()
            outgoing_1.context.CopyFrom(request.context)
            outgoing_1.ledger_account.contact.email = request.context.actor.email
            outgoing_1.ledger_account.audit.created_at.CopyFrom(request.context.deadline)
            outgoing_1.ledger_account.external_account_id = request.model_version_id
            merged_1 = ledger_v1_ledger_account_service_pb2.CloneLedgerAccountRequest()
            merged_1.MergeFrom(outgoing_1)
            outgoing_1.CopyFrom(merged_1)
            response_1 = await deps.clients.ledger_ledger_account.CloneLedgerAccount(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_1_0 = response_1.ledger_account.contact.email
            if returned_1_0:
                response.model_version.subject.email = returned_1_0
            echoed_0 = request.model_version_id
            response.model_version.model_version_id = echoed_0
            return response

    async def handle_lint_model_versions(
        self,
        request: modelregistry_v1_model_version_validation_service_pb2.LintModelVersionsRequest
    ) -> modelregistry_v1_model_version_validation_service_pb2.LintModelVersionsResponse:
        """Lints a model version."""
        deps = self.deps
        response = modelregistry_v1_model_version_validation_service_pb2.LintModelVersionsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('LintModelVersions', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'LintModelVersions', {'reason': request.reason})
            await deps.repository.save_model_version(request.context.tenant_id, request.model_version)
            response_0 = modelregistry_v1_model_version_calculation_service_pb2.EstimateModelVersionResponse()
            response_1 = modelregistry_v1_registered_model_validation_service_pb2.PreviewRegisteredModelResponse()
            outgoing_0 = modelregistry_v1_model_version_calculation_service_pb2.EstimateModelVersionRequest(
                context=request.context,
                model_version=modelregistry_v1_modelregistry_pb2.ModelVersion(
                    correlation_id=request.model_version.correlation_id,
                    sequence=request.model_version.sequence,
                    subject=customers_v1_refs_pb2.CustomerRef(
                        customer_id=request.model_version.subject.customer_id,
                        email=request.details.contact.email
                    )
                )
            )
            envelope_0 = AnyMessage()
            envelope_0.Pack(outgoing_0)
            outgoing_0 = modelregistry_v1_model_version_calculation_service_pb2.EstimateModelVersionRequest()
            if not envelope_0.Unpack(outgoing_0):
                raise ValueError("partner envelope contains the wrong request type")
            response_0 = await deps.clients.modelregistry_model_version_calculation.EstimateModelVersion(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = modelregistry_v1_registered_model_validation_service_pb2.PreviewRegisteredModelRequest(
                context=request.context,
                registered_model=modelregistry_v1_modelregistry_pb2.RegisteredModel(
                    owner=identity_v1_refs_pb2.UserRef(email=request.details.contact.email)
                )
            )
            registered_1 = cast(
                modelregistry_v1_registered_model_validation_service_pb2_grpc.RegisteredModelValidationServiceStub,
                deps.clients.registry['acme.modelregistry.v1.RegisteredModelValidationService']
            )
            response_1 = await registered_1.PreviewRegisteredModel(outgoing_1, timeout=deps.settings.timeout)
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.outcome.message = returned_0_0
            returned_0_1 = response_0.result.message
            if returned_0_1:
                response.result.message = returned_0_1
            returned_1_0 = response_1.outcome.reference_id
            if returned_1_0:
                response.outcome.reference_id = returned_1_0
            echoed_0 = request.model_version_id
            response.model_version.model_version_id = echoed_0
            echoed_1 = request.model_version.subject
            response.model_version.subject.CopyFrom(echoed_1)
            return response

    async def handle_normalize_model_version(
        self,
        request: modelregistry_v1_model_version_validation_service_pb2.NormalizeModelVersionRequest
    ) -> modelregistry_v1_model_version_validation_service_pb2.NormalizeModelVersionResponse:
        """Normalizes a model version."""
        deps = self.deps
        response = modelregistry_v1_model_version_validation_service_pb2.NormalizeModelVersionResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('NormalizeModelVersion', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'NormalizeModelVersion', {'reason': request.reason})
            await deps.repository.save_model_version(request.context.tenant_id, request.model_version)
            response_0 = modelregistry_v1_deployment_calculation_service_pb2.RecalculateDeploymentsResponse()
            response_1 = modelregistry_v1_deployment_calculation_service_pb2.QuoteDeploymentResponse()
            outgoing_0 = modelregistry_v1_deployment_calculation_service_pb2.RecalculateDeploymentsRequest(
                context=request.context,
                deployment=modelregistry_v1_modelregistry_pb2.Deployment(
                    participants=[
                        modelregistry_v1_modelregistry_pb2.DeploymentParticipant(
                            contact=common_v1_contact_pb2.ContactInfo(
                                email=request.details.contact.email,
                                preferred_channel=request.details.contact.preferred_channel
                            )
                        )
                    ]
                )
            )
            outgoing_1 = modelregistry_v1_deployment_calculation_service_pb2.QuoteDeploymentRequest(
                context=request.context,
                deployment=modelregistry_v1_modelregistry_pb2.Deployment(
                    participants=[
                        modelregistry_v1_modelregistry_pb2.DeploymentParticipant(
                            contact=common_v1_contact_pb2.ContactInfo(email=request.model_version.subject.email)
                        )
                    ]
                )
            )
            response_0, response_1 = await asyncio.gather(
                deps.clients.modelregistry_deployment_calculation.RecalculateDeployments(
                    outgoing_0,
                    timeout=deps.settings.timeout
                ),
                deps.clients.modelregistry_deployment_calculation.QuoteDeployment(
                    outgoing_1,
                    timeout=deps.settings.timeout
                ),
            )
            returned_0_0 = response_0.result.status
            if returned_0_0:
                response.outcome.status = returned_0_0
            returned_0_1 = response_0.deployment.organizer.email
            if returned_0_1:
                response.model_version.subject.email = returned_0_1
            returned_1_0 = response_1.result.status
            if returned_1_0:
                response.result.status = returned_1_0
            returned_1_1 = response_1.deployment.organizer.email
            if returned_1_1:
                response.model_version.subject.email = returned_1_1
            echoed_0 = request.model_version_id
            response.model_version.model_version_id = echoed_0
            echoed_1 = request.model_version.attributes
            response.model_version.attributes.update(echoed_1)
            return response

    async def handle_preview_model_version(
        self,
        request: modelregistry_v1_model_version_validation_service_pb2.PreviewModelVersionRequest
    ) -> modelregistry_v1_model_version_validation_service_pb2.PreviewModelVersionResponse:
        """Previews a model version."""
        deps = self.deps
        response = modelregistry_v1_model_version_validation_service_pb2.PreviewModelVersionResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('PreviewModelVersion', extra={'fields': {'locale': request.details.locale}})
            await deps.repository.audit(
                request.context.tenant_id,
                'PreviewModelVersion',
                {'locale': request.details.locale}
            )
            await deps.repository.save_model_version(request.context.tenant_id, request.model_version)
            response_0 = audit_v1_audit_event_validation_service_pb2.PreviewAuditEventResponse()
            response_1 = identity_v1_user_service_pb2.SearchUsersResponse()
            response_2 = authorization_v1_access_policy_validation_service_pb2.ScoreAccessPolicyResponse()
            response_3 = modelregistry_v1_model_version_calculation_service_pb2.EstimateModelVersionResponse()
            outgoing_0 = audit_v1_audit_event_validation_service_pb2.PreviewAuditEventRequest(
                context=request.context,
                details=audit_v1_audit_event_validation_service_pb2.PreviewAuditEventRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(
                        email=request.details.contact.email,
                        preferred_channel=request.details.contact.preferred_channel
                    )
                )
            )
            send_0 = partial(deps.clients.audit_audit_event_validation.PreviewAuditEvent, timeout=deps.settings.timeout)
            response_0 = await send_0(outgoing_0)
            outgoing_1 = identity_v1_user_service_pb2.SearchUsersRequest(
                context=request.context,
                filter=identity_v1_user_service_pb2.SearchUsersRequest.Filter(
                    created_after=request.model_version.occurred_at
                )
            )
            response_1 = await hooks.model_version_validation_preview_model_version1(
                deps.clients.identity_user,
                outgoing_1,
                deps.settings.timeout
            )
            outgoing_2 = authorization_v1_access_policy_validation_service_pb2.ScoreAccessPolicyRequest()
            outgoing_2.context.CopyFrom(request.context)
            outgoing_2.access_policy.owner.email = request.details.contact.email
            outgoing_2.access_policy.owner.display_name = request.model_version.subject.display_name
            outgoing_2.access_policy.block.notify_email = request.model_version.subject.email
            outgoing_2.reason = request.reason
            outgoing_2.context.tenant_id = tenant_id.get()
            response_2 = await deps.clients.authorization_access_policy_validation.ScoreAccessPolicy(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            callbacks_3: list[
                Callable[
                    [],
                    Awaitable[modelregistry_v1_model_version_calculation_service_pb2.EstimateModelVersionResponse]
                ]
            ] = []
            for item_3 in request.model_version.measurements:
                outgoing_3 = modelregistry_v1_model_version_calculation_service_pb2.EstimateModelVersionRequest(
                    context=request.context,
                    model_version=modelregistry_v1_modelregistry_pb2.ModelVersion(
                        measurements=[modelregistry_v1_modelregistry_pb2.ModelVersionMeasurement(unit=item_3.unit)]
                    )
                )
                async def send_3(
                    payload: modelregistry_v1_model_version_calculation_service_pb2.EstimateModelVersionRequest = outgoing_3
                ) -> modelregistry_v1_model_version_calculation_service_pb2.EstimateModelVersionResponse:
                    return await deps.clients.modelregistry_model_version_calculation.EstimateModelVersion(
                        payload,
                        timeout=deps.settings.timeout
                    )
                callbacks_3.append(send_3)
            for callback_3 in callbacks_3:
                response_3 = await callback_3()
            returned_0_0 = response_0.outcome.message
            if returned_0_0:
                response.result.message = returned_0_0
            returned_1_0 = response_1.result.status
            if returned_1_0:
                response.outcome.status = returned_1_0
            returned_2_0 = response_2.result.status
            if returned_2_0:
                response.result.status = returned_2_0
            returned_2_1 = response_2.result.reference_ids
            response.result.reference_ids.extend(returned_2_1)
            echoed_0 = request.model_version_id
            response.model_version.model_version_id = echoed_0
            echoed_1 = request.model_version.correlation_id
            response.model_version.correlation_id = echoed_1
            return response

    async def handle_score_model_version(
        self,
        request: modelregistry_v1_model_version_validation_service_pb2.ScoreModelVersionRequest
    ) -> modelregistry_v1_model_version_validation_service_pb2.ScoreModelVersionResponse:
        """Scores a model version."""
        deps = self.deps
        response = modelregistry_v1_model_version_validation_service_pb2.ScoreModelVersionResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ScoreModelVersion', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'ScoreModelVersion', {'reason': request.reason})
            await deps.repository.save_model_version(request.context.tenant_id, request.model_version)
            response_0 = modelregistry_v1_registered_model_calculation_service_pb2.ExplainRegisteredModelCalculationResponse()
            response_1 = modelregistry_v1_model_version_calculation_service_pb2.CalculateModelVersionResponse()
            response_2 = modelregistry_v1_model_version_calculation_service_pb2.ExplainModelVersionCalculationResponse()
            outgoing_0 = modelregistry_v1_registered_model_calculation_service_pb2.ExplainRegisteredModelCalculationRequest(
                context=request.context,
                registered_model=modelregistry_v1_modelregistry_pb2.RegisteredModel(
                    address=common_v1_address_pb2.PostalAddress(
                        country_code=request.details.destination.country_code,
                        lines=list(request.details.destination.lines),
                        locality=request.details.destination.locality
                    )
                )
            )
            steps_0 = [
                partial(
                    deps.clients.modelregistry_registered_model_calculation.ExplainRegisteredModelCalculation,
                    outgoing_0,
                    timeout=deps.settings.timeout
                )
            ]
            results_0 = await run_steps(steps_0)
            response_0 = results_0[-1]
            outgoing_1 = modelregistry_v1_model_version_calculation_service_pb2.CalculateModelVersionRequest(
                context=request.context,
                details=modelregistry_v1_model_version_calculation_service_pb2.CalculateModelVersionRequest.Details(
                    destination=common_v1_address_pb2.PostalAddress(
                        recipient=response_0.registered_model.address.recipient
                    )
                )
            )
            response_1 = await ModelVersionValidationScoreModelVersion1Adapter(
                deps.clients.modelregistry_model_version_calculation,
                deps.settings.timeout
            )(outgoing_1)
            outgoing_2 = modelregistry_v1_model_version_calculation_service_pb2.ExplainModelVersionCalculationRequest(
                context=request.context,
                details=modelregistry_v1_model_version_calculation_service_pb2.ExplainModelVersionCalculationRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(email=request.model_version.subject.email)
                ),
                model_version=modelregistry_v1_modelregistry_pb2.ModelVersion(
                    subject=customers_v1_refs_pb2.CustomerRef(customer_id=response_1.model_version.subject.customer_id)
                )
            )
            response_2 = cast(modelregistry_v1_model_version_calculation_service_pb2.ExplainModelVersionCalculationResponse, await deps.bus.request(
                'acme.modelregistry.v1.ModelVersionValidationService/ScoreModelVersion/2', outgoing_2, deps.settings.timeout,
            ))
            returned_0_0 = response_0.registered_model.owner.email
            if returned_0_0:
                response.model_version.subject.email = returned_0_0
            returned_1_0 = response_1.result.correlation_id
            if returned_1_0:
                response.result.correlation_id = returned_1_0
            returned_1_1 = response_1.model_version.attributes
            response.model_version.attributes.update(returned_1_1)
            returned_2_0 = response_2.model_version.correlation_id
            if returned_2_0:
                response.result.correlation_id = returned_2_0
            returned_2_1 = response_2.result.message
            if returned_2_1:
                response.result.message = returned_2_1
            echoed_0 = request.model_version_id
            response.model_version.model_version_id = echoed_0
            echoed_1 = request.model_version.occurred_at
            response.model_version.occurred_at.CopyFrom(echoed_1)
            return response

    async def handle_validate_model_version(
        self,
        request: modelregistry_v1_model_version_validation_service_pb2.ValidateModelVersionRequest
    ) -> modelregistry_v1_model_version_validation_service_pb2.ValidateModelVersionResponse:
        """Validates a model version."""
        deps = self.deps
        response = modelregistry_v1_model_version_validation_service_pb2.ValidateModelVersionResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ValidateModelVersion', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'ValidateModelVersion', {'reason': request.reason})
            await deps.repository.save_model_version(request.context.tenant_id, request.model_version)
            response_0 = modelregistry_v1_registered_model_validation_service_pb2.ExplainRegisteredModelDecisionResponse()
            response_1 = modelregistry_v1_registered_model_validation_service_pb2.LintRegisteredModelsResponse()
            outgoing_0 = modelregistry_v1_registered_model_validation_service_pb2.ExplainRegisteredModelDecisionRequest(
                context=request.context,
                registered_model=modelregistry_v1_modelregistry_pb2.RegisteredModel(
                    owner=identity_v1_refs_pb2.UserRef(email=request.details.contact.email)
                )
            )
            response_0 = await deps.clients.modelregistry_registered_model_validation.ExplainRegisteredModelDecision(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = modelregistry_v1_registered_model_validation_service_pb2.LintRegisteredModelsRequest(
                context=request.context,
                details=modelregistry_v1_registered_model_validation_service_pb2.LintRegisteredModelsRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(email=response_0.registered_model.owner.email)
                ),
                registered_model=modelregistry_v1_modelregistry_pb2.RegisteredModel(
                    address=common_v1_address_pb2.PostalAddress(
                        postal_code=response_0.registered_model.address.postal_code
                    ),
                    components={
                        'primary': modelregistry_v1_modelregistry_pb2.RegisteredModelComponent(
                            quantity=response_0.registered_model.components.get(
                                'primary',
                                modelregistry_v1_modelregistry_pb2.RegisteredModelComponent()
                            ).quantity
                        )
                    },
                    dimensions=modelregistry_v1_modelregistry_pb2.RegisteredModelDimensions(
                        height=response_0.registered_model.dimensions.height
                    )
                )
            )
            method_name_1 = 'LintRegisteredModels'
            response_1 = await getattr(
                deps.clients.modelregistry_registered_model_validation,
                method_name_1
            )(outgoing_1, timeout=deps.settings.timeout)
            returned_0_0 = response_0.registered_model.owner.display_name
            if returned_0_0:
                response.model_version.subject.display_name = returned_0_0
            returned_0_1 = response_0.result.details
            response.result.details.update(returned_0_1)
            returned_1_0 = response_1.result.reference_ids
            response.result.reference_ids.extend(returned_1_0)
            returned_1_1 = response_1.result.message
            if returned_1_1:
                response.outcome.message = returned_1_1
            echoed_0 = request.model_version_id
            response.model_version.model_version_id = echoed_0
            echoed_1 = request.model_version.correlation_id
            response.result.correlation_id = echoed_1
            return response
