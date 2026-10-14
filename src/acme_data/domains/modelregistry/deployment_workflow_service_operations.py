"""Functional operations behind DeploymentWorkflowService."""

from __future__ import annotations

from collections.abc import Awaitable
from collections.abc import Callable
from functools import partial
from typing import Any
import asyncio
import logging

from google.protobuf.json_format import MessageToDict
from google.protobuf.json_format import ParseDict

from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.customers.v1 import (
    consent_record_calculation_service_pb2 as customers_v1_consent_record_calculation_service_pb2,
)
from acme.customers.v1 import customer_query_service_pb2 as customers_v1_customer_query_service_pb2
from acme.customers.v1 import customer_service_pb2 as customers_v1_customer_service_pb2
from acme.customers.v1 import customers_pb2 as customers_v1_customers_pb2
from acme.customers.v1 import household_validation_service_pb2 as customers_v1_household_validation_service_pb2
from acme.customers.v1 import preference_calculation_service_pb2 as customers_v1_preference_calculation_service_pb2
from acme.customers.v1 import refs_pb2 as customers_v1_refs_pb2
from acme.featureflags.v1 import feature_flag_service_pb2 as featureflags_v1_feature_flag_service_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.lineage.v1 import lineage_edge_workflow_service_pb2 as lineage_v1_lineage_edge_workflow_service_pb2
from acme.modelregistry.v1 import deployment_import_service_pb2 as modelregistry_v1_deployment_import_service_pb2
from acme.modelregistry.v1 import deployment_lifecycle_service_pb2 as modelregistry_v1_deployment_lifecycle_service_pb2
from acme.modelregistry.v1 import deployment_workflow_service_pb2 as modelregistry_v1_deployment_workflow_service_pb2
from acme.modelregistry.v1 import (
    model_version_reporting_service_pb2 as modelregistry_v1_model_version_reporting_service_pb2,
)
from acme.modelregistry.v1 import modelregistry_pb2 as modelregistry_v1_modelregistry_pb2
from acme.modelregistry.v1 import (
    registered_model_approval_service_pb2 as modelregistry_v1_registered_model_approval_service_pb2,
)
from acme.modelregistry.v1 import (
    registered_model_sync_service_pb2 as modelregistry_v1_registered_model_sync_service_pb2,
)
from acme.patients.v1 import patient_service_pb2 as patients_v1_patient_service_pb2

from acme_data.domains.modelregistry import hooks
from acme_data.domains.modelregistry.adapters import DeploymentWorkflowStartDeploymentWorkflow1Adapter
from acme_data.domains.modelregistry.adapters import DeploymentWorkflowStartDeploymentWorkflow1Port
from acme_data.domains.modelregistry.adapters import DeploymentWorkflowStartDeploymentWorkflow3Adapter
from acme_data.domains.modelregistry.dependencies import Dependencies
from acme_data.domains.modelregistry.models import DeploymentWorkflowPauseDeploymentWorkflow3Command
from acme_data.domains.modelregistry.models import to_deployment_workflow_pause_deployment_workflow3_command
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import run_steps
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


async def handle_advance_deployment_workflow(
    deps: Dependencies,
    request: modelregistry_v1_deployment_workflow_service_pb2.AdvanceDeploymentWorkflowRequest
) -> modelregistry_v1_deployment_workflow_service_pb2.AdvanceDeploymentWorkflowResponse:
    """Advances a deployment."""
    response = modelregistry_v1_deployment_workflow_service_pb2.AdvanceDeploymentWorkflowResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('AdvanceDeploymentWorkflow', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'AdvanceDeploymentWorkflow', {'reason': request.reason})
        await deps.repository.save_deployment(request.context.tenant_id, request.deployment)
        response_0 = customers_v1_customer_query_service_pb2.CountCustomersResponse()
        response_1 = modelregistry_v1_deployment_import_service_pb2.GetDeploymentImportStatusResponse()
        response_2 = patients_v1_patient_service_pb2.ListPatientsResponse()
        outgoing_0 = customers_v1_customer_query_service_pb2.CountCustomersRequest(
            context=request.context,
            filter=customers_v1_customer_query_service_pb2.CountCustomersRequest.Filter(
                region=request.deployment.location.region
            )
        )
        response_0 = await deps.clients.customers_customer_query.CountCustomers(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        fields_1: dict[str, Any] = {'context': request.context, 'deployment_id': request.deployment.deployment_id}
        outgoing_1 = modelregistry_v1_deployment_import_service_pb2.GetDeploymentImportStatusRequest(**fields_1)
        response_1 = await deps.clients.modelregistry_deployment_import.GetDeploymentImportStatus(
            outgoing_1,
            timeout=deps.settings.timeout
        )
        outgoing_2 = patients_v1_patient_service_pb2.ListPatientsRequest(
            context=request.context,
            filter=patients_v1_patient_service_pb2.ListPatientsRequest.Filter(
                created_after=request.deployment.audit.updated_at,
                owner_id=request.deployment.organizer.user_id,
                region=response_1.deployment.location.region
            )
        )
        document_2 = MessageToDict(outgoing_2, preserving_proto_field_name=True)
        outgoing_2 = ParseDict(document_2, patients_v1_patient_service_pb2.ListPatientsRequest())
        response_2 = await deps.clients.patients_patient.ListPatients(outgoing_2, timeout=deps.settings.timeout)
        returned_0_0 = response_0.result.details
        response.result.details.update(returned_0_0)
        returned_1_0 = response_1.deployment.metadata
        response.deployment.metadata.update(returned_1_0)
        returned_1_1 = response_1.result.message
        if returned_1_1:
            response.outcome.message = returned_1_1
        returned_2_0 = response_2.result.reference_ids
        response.result.reference_ids.extend(returned_2_0)
        echoed_0 = request.deployment_id
        response.deployment.deployment_id = echoed_0
        echoed_1 = request.deployment.status
        response.deployment.status = echoed_1
        return response


async def handle_cancel_deployment_workflow(
    deps: Dependencies,
    request: modelregistry_v1_deployment_workflow_service_pb2.CancelDeploymentWorkflowRequest
) -> modelregistry_v1_deployment_workflow_service_pb2.CancelDeploymentWorkflowResponse:
    """Cancels a deployment."""
    response = modelregistry_v1_deployment_workflow_service_pb2.CancelDeploymentWorkflowResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('CancelDeploymentWorkflow', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'CancelDeploymentWorkflow', {'reason': request.reason})
        await deps.repository.save_deployment(request.context.tenant_id, request.deployment)
        response_0 = featureflags_v1_feature_flag_service_pb2.ListFeatureFlagsResponse()
        response_1 = modelregistry_v1_deployment_lifecycle_service_pb2.ReinstateDeploymentResponse()
        for item_0 in request.deployment.participants:
            outgoing_0 = featureflags_v1_feature_flag_service_pb2.ListFeatureFlagsRequest(
                context=request.context,
                filter=featureflags_v1_feature_flag_service_pb2.ListFeatureFlagsRequest.Filter(
                    owner_id=item_0.participant_id,
                    region=request.deployment.location.region
                )
            )
            response_0 = await deps.clients.featureflags_feature_flag.ListFeatureFlags(
                outgoing_0,
                timeout=deps.settings.timeout
            )
        outgoing_1 = modelregistry_v1_deployment_lifecycle_service_pb2.ReinstateDeploymentRequest()
        outgoing_1.context.CopyFrom(request.context)
        outgoing_1.deployment_id = request.deployment.deployment_id
        outgoing_1.details.notify_contact.name.CopyFrom(request.details.notify.name)
        outgoing_1.details.notify_contact.email = request.details.notify.email
        merged_1 = modelregistry_v1_deployment_lifecycle_service_pb2.ReinstateDeploymentRequest()
        merged_1.MergeFrom(outgoing_1)
        outgoing_1.CopyFrom(merged_1)
        response_1 = await deps.clients.modelregistry_deployment_lifecycle.ReinstateDeployment(
            outgoing_1,
            timeout=deps.settings.timeout
        )
        returned_1_0 = response_1.result.status
        if returned_1_0:
            response.result.status = returned_1_0
        returned_1_1 = response_1.deployment.metadata
        response.deployment.metadata.update(returned_1_1)
        echoed_0 = request.deployment_id
        response.deployment.deployment_id = echoed_0
        echoed_1 = request.deployment.title
        response.deployment.title = echoed_1
        return response


async def handle_list_deployment_workflows(
    deps: Dependencies,
    request: modelregistry_v1_deployment_workflow_service_pb2.ListDeploymentWorkflowsRequest
) -> modelregistry_v1_deployment_workflow_service_pb2.ListDeploymentWorkflowsResponse:
    """Lists deployments a page at a time."""
    response = modelregistry_v1_deployment_workflow_service_pb2.ListDeploymentWorkflowsResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('ListDeploymentWorkflows', extra={'fields': {'order_by': request.order_by}})
        await deps.repository.audit(
            request.context.tenant_id,
            'ListDeploymentWorkflows',
            {'order_by': request.order_by}
        )
        return response


async def handle_pause_deployment_workflow(
    deps: Dependencies,
    request: modelregistry_v1_deployment_workflow_service_pb2.PauseDeploymentWorkflowRequest
) -> modelregistry_v1_deployment_workflow_service_pb2.PauseDeploymentWorkflowResponse:
    """Pauses a deployment."""
    response = modelregistry_v1_deployment_workflow_service_pb2.PauseDeploymentWorkflowResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('PauseDeploymentWorkflow', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'PauseDeploymentWorkflow', {'reason': request.reason})
        await deps.repository.save_deployment(request.context.tenant_id, request.deployment)
        response_0 = customers_v1_preference_calculation_service_pb2.RecalculatePreferencesResponse()
        response_1 = customers_v1_consent_record_calculation_service_pb2.RecalculateConsentRecordsResponse()
        response_2 = modelregistry_v1_deployment_lifecycle_service_pb2.ReinstateDeploymentResponse()
        response_3 = modelregistry_v1_registered_model_sync_service_pb2.ReconcileRegisteredModelsResponse()
        outgoing_1 = customers_v1_consent_record_calculation_service_pb2.RecalculateConsentRecordsRequest(
            consent_record=customers_v1_customers_pb2.ConsentRecord(
                subject=customers_v1_refs_pb2.HouseholdRef(display_name=request.deployment.organizer.display_name)
            ),
            context=request.context,
            details=customers_v1_consent_record_calculation_service_pb2.RecalculateConsentRecordsRequest.Details(
                destination=common_v1_address_pb2.PostalAddress(
                    country_code=request.deployment.location.country_code,
                    postal_code=request.deployment.location.postal_code
                )
            )
        )
        outgoing_2 = modelregistry_v1_deployment_lifecycle_service_pb2.ReinstateDeploymentRequest(
            context=request.context,
            deployment_id=request.deployment_id,
            details=modelregistry_v1_deployment_lifecycle_service_pb2.ReinstateDeploymentRequest.Details(
                notify_contact=common_v1_contact_pb2.ContactInfo(email=request.details.notify.email)
            )
        )
        response_1, response_2 = await asyncio.gather(
            deps.clients.customers_consent_record_calculation.RecalculateConsentRecords(
                outgoing_1,
                timeout=deps.settings.timeout
            ),
            deps.clients.modelregistry_deployment_lifecycle.ReinstateDeployment(
                outgoing_2,
                timeout=deps.settings.timeout
            ),
        )
        outgoing_0 = customers_v1_preference_calculation_service_pb2.RecalculatePreferencesRequest(
            context=request.context,
            preference=customers_v1_customers_pb2.Preference(
                owner=identity_v1_refs_pb2.UserRef(
                    display_name=request.deployment.organizer.display_name,
                    email=request.details.notify.email
                )
            )
        )
        response_0 = await deps.clients.customers_preference_calculation.RecalculatePreferences(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        command_3 = DeploymentWorkflowPauseDeploymentWorkflow3Command.model_validate(
            {
                'context': request.context,
                'registered_model_address_region': request.deployment.location.region,
                'registered_model_owner_display_name': request.deployment.organizer.display_name,
                'registered_model_owner_user_id': request.deployment.organizer.user_id,
                'registered_model_audit_updated_at': response_0.preference.audit.updated_at
            }
        )
        outgoing_3 = to_deployment_workflow_pause_deployment_workflow3_command(command_3)
        response_3 = await deps.clients.modelregistry_registered_model_sync.ReconcileRegisteredModels(
            outgoing_3,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.preference.owner.display_name
        if returned_0_0:
            response.deployment.organizer.display_name = returned_0_0
        returned_1_0 = response_1.result.status
        if returned_1_0:
            response.outcome.status = returned_1_0
        returned_1_1 = response_1.result.reference_ids
        response.result.reference_ids.extend(returned_1_1)
        returned_2_0 = response_2.deployment.audit.updated_by
        if returned_2_0:
            response.deployment.audit.updated_by = returned_2_0
        returned_3_0 = response_3.registered_model.address.region
        if returned_3_0:
            response.deployment.location.region = returned_3_0
        returned_3_1 = response_3.registered_model.audit.updated_at
        if returned_3_1.ListFields():
            response.deployment.audit.updated_at.MergeFrom(returned_3_1)
        echoed_0 = request.deployment_id
        response.deployment.deployment_id = echoed_0
        echoed_1 = request.deployment.status
        response.deployment.status = echoed_1
        return response


async def handle_signal_deployment_workflow(
    deps: Dependencies,
    request: modelregistry_v1_deployment_workflow_service_pb2.SignalDeploymentWorkflowRequest
) -> modelregistry_v1_deployment_workflow_service_pb2.SignalDeploymentWorkflowResponse:
    """Signals a deployment."""
    response = modelregistry_v1_deployment_workflow_service_pb2.SignalDeploymentWorkflowResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('SignalDeploymentWorkflow', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'SignalDeploymentWorkflow', {'reason': request.reason})
        await deps.repository.save_deployment(request.context.tenant_id, request.deployment)
        response_0 = lineage_v1_lineage_edge_workflow_service_pb2.CancelLineageEdgeWorkflowResponse()
        response_1 = customers_v1_household_validation_service_pb2.CheckHouseholdEligibilityResponse()
        outgoing_0 = lineage_v1_lineage_edge_workflow_service_pb2.CancelLineageEdgeWorkflowRequest(
            context=request.context,
            details=lineage_v1_lineage_edge_workflow_service_pb2.CancelLineageEdgeWorkflowRequest.Details(
                notify=common_v1_contact_pb2.ContactInfo(
                    email=request.deployment.organizer.email,
                    phone=request.details.notify.phone,
                    preferred_channel=request.details.notify.preferred_channel
                ),
                step=request.details.step
            )
        )
        response_0 = await deps.clients.lineage_lineage_edge_workflow.CancelLineageEdgeWorkflow(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = customers_v1_household_validation_service_pb2.CheckHouseholdEligibilityRequest(
            context=request.context,
            household=customers_v1_customers_pb2.Household(
                children=[
                    customers_v1_customers_pb2.Household(
                        children=[
                            customers_v1_customers_pb2.Household(
                                location=common_v1_address_pb2.PostalAddress(
                                    postal_code=request.deployment.location.postal_code
                                )
                            )
                        ]
                    )
                ]
            )
        )
        response_1 = await hooks.deployment_workflow_signal_deployment_workflow1(
            deps.clients.customers_household_validation,
            outgoing_1,
            deps.settings.timeout
        )
        returned_0_0 = response_0.outcome.status
        if returned_0_0:
            response.result.status = returned_0_0
        returned_0_1 = response_0.lineage_edge.subject.display_name
        if returned_0_1:
            response.deployment.organizer.display_name = returned_0_1
        returned_1_0 = response_1.outcome.next_steps
        response.outcome.next_steps.extend(returned_1_0)
        returned_1_1 = response_1.household.manager.email
        if returned_1_1:
            response.deployment.organizer.email = returned_1_1
        echoed_0 = request.deployment_id
        response.deployment.deployment_id = echoed_0
        echoed_1 = request.deployment.metadata
        response.deployment.metadata.update(echoed_1)
        return response


async def handle_start_deployment_workflow(
    deps: Dependencies,
    request: modelregistry_v1_deployment_workflow_service_pb2.StartDeploymentWorkflowRequest
) -> modelregistry_v1_deployment_workflow_service_pb2.StartDeploymentWorkflowResponse:
    """Starts a deployment."""
    response = modelregistry_v1_deployment_workflow_service_pb2.StartDeploymentWorkflowResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('StartDeploymentWorkflow', extra={'fields': {'deployment_id': request.deployment.deployment_id}})
        await deps.repository.audit(
            request.context.tenant_id,
            'StartDeploymentWorkflow',
            {'deployment_id': request.deployment.deployment_id}
        )
        await deps.repository.save_deployment(request.context.tenant_id, request.deployment)
        response_0 = customers_v1_customer_service_pb2.SearchCustomersResponse()
        response_1 = modelregistry_v1_deployment_import_service_pb2.MapDeploymentImportColumnsResponse()
        response_2 = modelregistry_v1_registered_model_approval_service_pb2.ListPendingRegisteredModelsResponse()
        response_3 = modelregistry_v1_model_version_reporting_service_pb2.ScheduleModelVersionReportResponse()
        outgoing_0 = customers_v1_customer_service_pb2.SearchCustomersRequest(
            context=request.context,
            filter=customers_v1_customer_service_pb2.SearchCustomersRequest.Filter(
                region=request.deployment.location.region
            )
        )
        response_0 = await deps.clients.customers_customer.SearchCustomers(outgoing_0, timeout=deps.settings.timeout)
        outgoing_1 = modelregistry_v1_deployment_import_service_pb2.MapDeploymentImportColumnsRequest(
            context=request.context,
            deployment=modelregistry_v1_modelregistry_pb2.Deployment(
                participants=[
                    modelregistry_v1_modelregistry_pb2.DeploymentParticipant(
                        contact=common_v1_contact_pb2.ContactInfo(
                            email=request.deployment.organizer.email,
                            name=request.details.notify.name
                        )
                    )
                ]
            )
        )
        port_1: DeploymentWorkflowStartDeploymentWorkflow1Port = DeploymentWorkflowStartDeploymentWorkflow1Adapter(
            deps.clients.modelregistry_deployment_import,
            deps.settings.timeout
        )
        response_1 = await port_1.execute(outgoing_1)
        outgoing_2 = modelregistry_v1_registered_model_approval_service_pb2.ListPendingRegisteredModelsRequest(
            context=request.context,
            filter=modelregistry_v1_registered_model_approval_service_pb2.ListPendingRegisteredModelsRequest.Filter(
                created_after=request.deployment.audit.created_at,
                region=request.deployment.location.region
            )
        )
        steps_2 = [
            partial(
                deps.clients.modelregistry_registered_model_approval.ListPendingRegisteredModels,
                outgoing_2,
                timeout=deps.settings.timeout
            )
        ]
        results_2 = await run_steps(steps_2)
        response_2 = results_2[-1]
        outgoing_3 = modelregistry_v1_model_version_reporting_service_pb2.ScheduleModelVersionReportRequest(
            annotations=dict(request.annotations),
            context=request.context,
            reason=request.reason
        )
        response_3 = await DeploymentWorkflowStartDeploymentWorkflow3Adapter(
            deps.clients.modelregistry_model_version_reporting,
            deps.settings.timeout
        )(outgoing_3)
        returned_0_0 = response_0.result.reference_ids
        response.result.reference_ids.extend(returned_0_0)
        returned_0_1 = response_0.result.status
        if returned_0_1:
            response.outcome.status = returned_0_1
        returned_1_0 = response_1.outcome.message
        if returned_1_0:
            response.result.message = returned_1_0
        returned_2_0 = response_2.result.status
        if returned_2_0:
            response.outcome.status = returned_2_0
        returned_3_0 = response_3.result.reference_ids
        response.result.reference_ids.extend(returned_3_0)
        echoed_0 = request.deployment_id
        response.deployment.deployment_id = echoed_0
        echoed_1 = request.deployment.metadata
        response.deployment.metadata.update(echoed_1)
        return response
