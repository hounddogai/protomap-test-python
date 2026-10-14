"""Application workflow for Deployment Calculation."""

from __future__ import annotations

from collections.abc import Awaitable
from collections.abc import Callable
from functools import partial
from typing import cast
import asyncio
import logging

from acme.admissions.v1 import admission_query_service_pb2 as admissions_v1_admission_query_service_pb2
from acme.anomalies.v1 import anomalies_pb2 as anomalies_v1_anomalies_pb2
from acme.anomalies.v1 import anomaly_validation_service_pb2 as anomalies_v1_anomaly_validation_service_pb2
from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.customers.v1 import refs_pb2 as customers_v1_refs_pb2
from acme.featurestore.v1 import (
    feature_value_validation_service_pb2 as featurestore_v1_feature_value_validation_service_pb2,
)
from acme.featurestore.v1 import feature_view_query_service_pb2 as featurestore_v1_feature_view_query_service_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.metrics.v1 import metric_alert_notification_service_pb2 as metrics_v1_metric_alert_notification_service_pb2
from acme.modelregistry.v1 import (
    deployment_calculation_service_pb2 as modelregistry_v1_deployment_calculation_service_pb2,
)
from acme.modelregistry.v1 import (
    model_version_calculation_service_pb2 as modelregistry_v1_model_version_calculation_service_pb2,
)
from acme.modelregistry.v1 import modelregistry_pb2 as modelregistry_v1_modelregistry_pb2
from acme.modelregistry.v1 import (
    registered_model_calculation_service_pb2 as modelregistry_v1_registered_model_calculation_service_pb2,
)

from acme_data.domains.modelregistry import hooks
from acme_data.domains.modelregistry.dependencies import Dependencies
from acme_data.domains.modelregistry.models import DeploymentCalculationCalculateDeployment0Command
from acme_data.domains.modelregistry.models import DeploymentCalculationCompareDeploymentOptions0Command
from acme_data.domains.modelregistry.models import to_deployment_calculation_calculate_deployment0_command
from acme_data.domains.modelregistry.models import to_deployment_calculation_compare_deployment_options0_command
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import run_steps
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class DeploymentCalculationServicerWorkflow:
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    async def handle_calculate_deployment(
        self,
        request: modelregistry_v1_deployment_calculation_service_pb2.CalculateDeploymentRequest
    ) -> modelregistry_v1_deployment_calculation_service_pb2.CalculateDeploymentResponse:
        """Calculates a deployment."""
        deps = self.deps
        response = modelregistry_v1_deployment_calculation_service_pb2.CalculateDeploymentResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CalculateDeployment', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'CalculateDeployment', {'reason': request.reason})
            await deps.repository.save_deployment(request.context.tenant_id, request.deployment)
            response_0 = featurestore_v1_feature_view_query_service_pb2.BrowseFeatureViewsResponse()
            command_0 = DeploymentCalculationCalculateDeployment0Command(
                context=request.context,
                filter_region=request.deployment.location.region,
                filter_created_after=request.deployment.audit.updated_at,
                filter_labels=dict(request.deployment.metadata),
                filter_owner_id=request.deployment.deployment_id
            )
            outgoing_0 = to_deployment_calculation_calculate_deployment0_command(command_0)
            response_0 = await deps.clients.featurestore_feature_view_query.BrowseFeatureViews(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.details
            response.result.details.update(returned_0_0)
            echoed_0 = request.deployment_id
            response.deployment.deployment_id = echoed_0
            echoed_1 = request.deployment.metadata
            response.deployment.metadata.update(echoed_1)
            return response

    async def handle_compare_deployment_options(
        self,
        request: modelregistry_v1_deployment_calculation_service_pb2.CompareDeploymentOptionsRequest
    ) -> modelregistry_v1_deployment_calculation_service_pb2.CompareDeploymentOptionsResponse:
        """Compares a deployment."""
        deps = self.deps
        response = modelregistry_v1_deployment_calculation_service_pb2.CompareDeploymentOptionsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CompareDeploymentOptions', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'CompareDeploymentOptions',
                {'reason': request.reason}
            )
            await deps.repository.save_deployment(request.context.tenant_id, request.deployment)
            response_0 = modelregistry_v1_registered_model_calculation_service_pb2.QuoteRegisteredModelResponse()
            response_1 = admissions_v1_admission_query_service_pb2.BrowseAdmissionsResponse()
            response_2 = anomalies_v1_anomaly_validation_service_pb2.ScoreAnomalyResponse()
            command_0 = DeploymentCalculationCompareDeploymentOptions0Command.model_validate(
                {
                    'context': request.context,
                    'registered_model_address_region': request.deployment.location.region,
                    'details_destination_locality': request.deployment.location.locality
                }
            )
            outgoing_0 = to_deployment_calculation_compare_deployment_options0_command(command_0)
            response_0 = await deps.clients.modelregistry_registered_model_calculation.QuoteRegisteredModel(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = admissions_v1_admission_query_service_pb2.BrowseAdmissionsRequest(
                context=request.context,
                filter=admissions_v1_admission_query_service_pb2.BrowseAdmissionsRequest.Filter(
                    region=request.deployment.location.region
                )
            )
            send_1 = partial(deps.clients.admissions_admission_query.BrowseAdmissions, timeout=deps.settings.timeout)
            response_1 = await send_1(outgoing_1)
            outgoing_2 = anomalies_v1_anomaly_validation_service_pb2.ScoreAnomalyRequest(
                anomaly=anomalies_v1_anomalies_pb2.Anomaly(
                    assignee=identity_v1_refs_pb2.UserRef(user_id=response_0.registered_model.owner.user_id)
                ),
                context=request.context,
                details=anomalies_v1_anomaly_validation_service_pb2.ScoreAnomalyRequest.Details(
                    destination=common_v1_address_pb2.PostalAddress(locality=request.deployment.location.locality)
                )
            )
            response_2 = await hooks.deployment_calculation_compare_deployment_options2(
                deps.clients.anomalies_anomaly_validation,
                outgoing_2,
                deps.settings.timeout
            )
            returned_0_0 = response_0.result.reference_ids
            response.result.reference_ids.extend(returned_0_0)
            returned_0_1 = response_0.registered_model.owner.display_name
            if returned_0_1:
                response.deployment.organizer.display_name = returned_0_1
            returned_1_0 = response_1.result.status
            if returned_1_0:
                response.result.status = returned_1_0
            returned_2_0 = response_2.anomaly.audit.updated_at
            if returned_2_0.ListFields():
                response.deployment.audit.updated_at.MergeFrom(returned_2_0)
            returned_2_1 = response_2.anomaly.audit.created_at
            if returned_2_1.ListFields():
                response.deployment.audit.created_at.MergeFrom(returned_2_1)
            echoed_0 = request.deployment_id
            response.deployment.deployment_id = echoed_0
            echoed_1 = request.details.currency_code
            response.breakdown.currency_code = echoed_1
            return response

    async def handle_estimate_deployment(
        self,
        request: modelregistry_v1_deployment_calculation_service_pb2.EstimateDeploymentRequest
    ) -> modelregistry_v1_deployment_calculation_service_pb2.EstimateDeploymentResponse:
        """Estimates a deployment."""
        deps = self.deps
        response = modelregistry_v1_deployment_calculation_service_pb2.EstimateDeploymentResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('EstimateDeployment', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'EstimateDeployment', {'reason': request.reason})
            await deps.repository.save_deployment(request.context.tenant_id, request.deployment)
            response_0 = featurestore_v1_feature_value_validation_service_pb2.ValidateFeatureValueResponse()
            response_1 = modelregistry_v1_registered_model_calculation_service_pb2.ExplainRegisteredModelCalculationResponse()
            for item_0 in request.deployment.participants:
                outgoing_0 = featurestore_v1_feature_value_validation_service_pb2.ValidateFeatureValueRequest(
                    context=request.context,
                    details=featurestore_v1_feature_value_validation_service_pb2.ValidateFeatureValueRequest.Details(
                        contact=common_v1_contact_pb2.ContactInfo(
                            name=item_0.contact.name,
                            phone=item_0.contact.phone,
                            preferred_channel=item_0.contact.preferred_channel
                        )
                    )
                )
                response_0 = await deps.clients.featurestore_feature_value_validation.ValidateFeatureValue(
                    outgoing_0,
                    timeout=deps.settings.timeout
                )
            requests_1: list[
                modelregistry_v1_registered_model_calculation_service_pb2.ExplainRegisteredModelCalculationRequest
            ] = []
            for item_1 in request.deployment.participants:
                outgoing_1 = modelregistry_v1_registered_model_calculation_service_pb2.ExplainRegisteredModelCalculationRequest(
                    context=request.context,
                    details=modelregistry_v1_registered_model_calculation_service_pb2.ExplainRegisteredModelCalculationRequest.Details(
                        contact=common_v1_contact_pb2.ContactInfo(email=item_1.contact.email, name=item_1.contact.name)
                    )
                )
                requests_1.append(outgoing_1)
            replies_1 = await asyncio.gather(*(
                deps.clients.modelregistry_registered_model_calculation.ExplainRegisteredModelCalculation(
                    entry,
                    timeout=deps.settings.timeout
                ) for entry in requests_1
            ))
            if replies_1:
                response_1 = replies_1[-1]
            echoed_0 = request.deployment_id
            response.deployment.deployment_id = echoed_0
            echoed_1 = request.deployment.title
            response.deployment.title = echoed_1
            return response

    async def handle_get_deployment_rates(
        self,
        request: modelregistry_v1_deployment_calculation_service_pb2.GetDeploymentRatesRequest
    ) -> modelregistry_v1_deployment_calculation_service_pb2.GetDeploymentRatesResponse:
        """Returns a deployment."""
        deps = self.deps
        response = modelregistry_v1_deployment_calculation_service_pb2.GetDeploymentRatesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('GetDeploymentRates', extra={'fields': {'locale': request.context.locale}})
            await deps.repository.audit(
                request.context.tenant_id,
                'GetDeploymentRates',
                {'locale': request.context.locale}
            )
            echoed_0 = request.deployment_id
            response.deployment.deployment_id = echoed_0
            return response

    async def handle_quote_deployment(
        self,
        request: modelregistry_v1_deployment_calculation_service_pb2.QuoteDeploymentRequest
    ) -> modelregistry_v1_deployment_calculation_service_pb2.QuoteDeploymentResponse:
        """Quotes a deployment."""
        deps = self.deps
        response = modelregistry_v1_deployment_calculation_service_pb2.QuoteDeploymentResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('QuoteDeployment', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'QuoteDeployment', {'reason': request.reason})
            await deps.repository.save_deployment(request.context.tenant_id, request.deployment)
            response_0 = modelregistry_v1_model_version_calculation_service_pb2.ExplainModelVersionCalculationResponse()
            response_1 = metrics_v1_metric_alert_notification_service_pb2.SubscribeMetricAlertUpdatesResponse()
            response_2 = modelregistry_v1_registered_model_calculation_service_pb2.RecalculateRegisteredModelsResponse()
            outgoing_0 = modelregistry_v1_model_version_calculation_service_pb2.ExplainModelVersionCalculationRequest(
                context=request.context,
                model_version=modelregistry_v1_modelregistry_pb2.ModelVersion(
                    subject=customers_v1_refs_pb2.CustomerRef(
                        display_name=request.deployment.organizer.display_name,
                        email=request.deployment.organizer.email
                    )
                )
            )
            steps_0 = [
                partial(
                    deps.clients.modelregistry_model_version_calculation.ExplainModelVersionCalculation,
                    outgoing_0,
                    timeout=deps.settings.timeout
                )
            ]
            results_0 = await run_steps(steps_0)
            response_0 = results_0[-1]
            callbacks_1: list[
                Callable[
                    [],
                    Awaitable[metrics_v1_metric_alert_notification_service_pb2.SubscribeMetricAlertUpdatesResponse]
                ]
            ] = []
            for item_1 in request.deployment.participants:
                outgoing_1 = metrics_v1_metric_alert_notification_service_pb2.SubscribeMetricAlertUpdatesRequest(
                    context=request.context,
                    details=metrics_v1_metric_alert_notification_service_pb2.SubscribeMetricAlertUpdatesRequest.Details(
                        recipient=common_v1_contact_pb2.ContactInfo(
                            email=item_1.contact.email,
                            name=item_1.contact.name,
                            phone=item_1.contact.phone,
                            preferred_channel=item_1.contact.preferred_channel
                        )
                    )
                )
                async def send_1(
                    payload: metrics_v1_metric_alert_notification_service_pb2.SubscribeMetricAlertUpdatesRequest = outgoing_1
                ) -> metrics_v1_metric_alert_notification_service_pb2.SubscribeMetricAlertUpdatesResponse:
                    return await deps.clients.metrics_metric_alert_notification.SubscribeMetricAlertUpdates(
                        payload,
                        timeout=deps.settings.timeout
                    )
                callbacks_1.append(send_1)
            for callback_1 in callbacks_1:
                response_1 = await callback_1()
            outgoing_2 = modelregistry_v1_registered_model_calculation_service_pb2.RecalculateRegisteredModelsRequest(
                context=request.context,
                registered_model=modelregistry_v1_modelregistry_pb2.RegisteredModel(
                    address=common_v1_address_pb2.PostalAddress(locality=request.deployment.location.locality),
                    audit=common_v1_audit_pb2.AuditInfo(created_at=response_1.metric_alert.audit.created_at),
                    owner=identity_v1_refs_pb2.UserRef(
                        display_name=response_0.model_version.subject.display_name,
                        email=request.deployment.organizer.email
                    )
                )
            )
            response_2 = cast(modelregistry_v1_registered_model_calculation_service_pb2.RecalculateRegisteredModelsResponse, await deps.bus.request(
                'acme.modelregistry.v1.DeploymentCalculationService/QuoteDeployment/2', outgoing_2, deps.settings.timeout,
            ))
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.result.message = returned_0_0
            returned_2_0 = response_2.registered_model.owner.user_id
            if returned_2_0:
                response.deployment.organizer.user_id = returned_2_0
            returned_2_1 = response_2.registered_model.owner.email
            returned_2_1_part_1 = response.deployment.participants.add()
            if returned_2_1:
                returned_2_1_part_1.contact.email = returned_2_1
            echoed_0 = request.deployment_id
            response.deployment.deployment_id = echoed_0
            echoed_1 = request.deployment.location
            response.deployment.location.CopyFrom(echoed_1)
            return response

    async def handle_recalculate_deployments(
        self,
        request: modelregistry_v1_deployment_calculation_service_pb2.RecalculateDeploymentsRequest
    ) -> modelregistry_v1_deployment_calculation_service_pb2.RecalculateDeploymentsResponse:
        """Recalculates a deployment."""
        deps = self.deps
        response = modelregistry_v1_deployment_calculation_service_pb2.RecalculateDeploymentsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('RecalculateDeployments', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'RecalculateDeployments', {'reason': request.reason})
            await deps.repository.save_deployment(request.context.tenant_id, request.deployment)
            response_0 = modelregistry_v1_registered_model_calculation_service_pb2.RecalculateRegisteredModelsResponse()
            response_1 = modelregistry_v1_registered_model_calculation_service_pb2.ExplainRegisteredModelCalculationResponse()
            outgoing_0 = modelregistry_v1_registered_model_calculation_service_pb2.RecalculateRegisteredModelsRequest(
                context=request.context,
                details=modelregistry_v1_registered_model_calculation_service_pb2.RecalculateRegisteredModelsRequest.Details(
                    destination=common_v1_address_pb2.PostalAddress(region=request.deployment.location.region)
                ),
                registered_model=modelregistry_v1_modelregistry_pb2.RegisteredModel(
                    address=common_v1_address_pb2.PostalAddress(locality=request.deployment.location.locality),
                    owner=identity_v1_refs_pb2.UserRef(user_id=request.deployment.organizer.user_id)
                )
            )
            response_0 = await deps.clients.modelregistry_registered_model_calculation.RecalculateRegisteredModels(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = modelregistry_v1_registered_model_calculation_service_pb2.ExplainRegisteredModelCalculationRequest(
                context=request.context,
                registered_model=modelregistry_v1_modelregistry_pb2.RegisteredModel(
                    address=common_v1_address_pb2.PostalAddress(
                        lines=list(response_0.registered_model.address.lines),
                        postal_code=request.deployment.location.postal_code,
                        region=request.deployment.location.region
                    ),
                    components={
                        'primary': modelregistry_v1_modelregistry_pb2.RegisteredModelComponent(
                            component_id=response_0.registered_model.components.get(
                                'primary',
                                modelregistry_v1_modelregistry_pb2.RegisteredModelComponent()
                            ).component_id
                        )
                    }
                )
            )
            method_name_1 = 'ExplainRegisteredModelCalculation'
            response_1 = await getattr(
                deps.clients.modelregistry_registered_model_calculation,
                method_name_1
            )(outgoing_1, timeout=deps.settings.timeout)
            returned_0_0 = response_0.registered_model.address.lines
            response.deployment.location.lines.extend(returned_0_0)
            returned_1_0 = response_1.registered_model.address.region
            if returned_1_0:
                response.deployment.location.region = returned_1_0
            returned_1_1 = response_1.registered_model.address.locality
            if returned_1_1:
                response.deployment.location.locality = returned_1_1
            echoed_0 = request.deployment_id
            response.deployment.deployment_id = echoed_0
            echoed_1 = request.deployment.organizer
            response.deployment.organizer.CopyFrom(echoed_1)
            return response
