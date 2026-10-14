"""Functional operations behind InteractionLifecycleService."""

from __future__ import annotations

from collections.abc import Awaitable
from collections.abc import Callable
from functools import partial
from typing import cast
import asyncio
import logging

from google.protobuf.any_pb2 import Any as AnyMessage

from acme.audit.v1 import audit_event_service_pb2 as audit_v1_audit_event_service_pb2
from acme.audit.v1 import audit_pb2 as audit_v1_audit_pb2
from acme.audit.v1 import refs_pb2 as audit_v1_refs_pb2
from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.customers.v1 import (
    consent_record_calculation_service_pb2 as customers_v1_consent_record_calculation_service_pb2,
)
from acme.customers.v1 import customer_query_service_pb2 as customers_v1_customer_query_service_pb2
from acme.customers.v1 import (
    customer_segment_validation_service_pb2 as customers_v1_customer_segment_validation_service_pb2,
)
from acme.customers.v1 import customer_validation_service_pb2 as customers_v1_customer_validation_service_pb2
from acme.customers.v1 import customers_pb2 as customers_v1_customers_pb2
from acme.customers.v1 import household_calculation_service_pb2 as customers_v1_household_calculation_service_pb2
from acme.customers.v1 import refs_pb2 as customers_v1_refs_pb2
from acme.featurestore.v1 import (
    feature_value_workflow_service_pb2 as featurestore_v1_feature_value_workflow_service_pb2,
)
from acme.featurestore.v1 import (
    feature_value_workflow_service_pb2_grpc as featurestore_v1_feature_value_workflow_service_pb2_grpc,
)
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.media.v1 import media_asset_calculation_service_pb2 as media_v1_media_asset_calculation_service_pb2
from acme.metrics.v1 import dashboard_history_service_pb2 as metrics_v1_dashboard_history_service_pb2
from acme.metrics.v1 import dashboard_history_service_pb2_grpc as metrics_v1_dashboard_history_service_pb2_grpc
from acme.metrics.v1 import metric_series_export_service_pb2 as metrics_v1_metric_series_export_service_pb2
from acme.metrics.v1 import metric_series_service_pb2 as metrics_v1_metric_series_service_pb2
from acme.metrics.v1 import metrics_pb2 as metrics_v1_metrics_pb2
from acme.pipelines.v1 import pipeline_run_sync_service_pb2 as pipelines_v1_pipeline_run_sync_service_pb2
from acme.recommendations.v1 import (
    interaction_lifecycle_service_pb2 as recommendations_v1_interaction_lifecycle_service_pb2,
)
from acme.recommendations.v1 import (
    interaction_validation_service_pb2 as recommendations_v1_interaction_validation_service_pb2,
)
from acme.recommendations.v1 import (
    recommendation_model_query_service_pb2 as recommendations_v1_recommendation_model_query_service_pb2,
)
from acme.recommendations.v1 import (
    recommendation_model_validation_service_pb2 as recommendations_v1_recommendation_model_validation_service_pb2,
)
from acme.recommendations.v1 import (
    recommendation_set_query_service_pb2 as recommendations_v1_recommendation_set_query_service_pb2,
)
from acme.recommendations.v1 import recommendation_set_service_pb2 as recommendations_v1_recommendation_set_service_pb2
from acme.recommendations.v1 import recommendations_pb2 as recommendations_v1_recommendations_pb2

from acme_data.domains.recommendations import hooks
from acme_data.domains.recommendations.adapters import InteractionLifecycleGetInteractionLifecycle1Adapter
from acme_data.domains.recommendations.adapters import InteractionLifecycleGetInteractionLifecycle1Port
from acme_data.domains.recommendations.adapters import InteractionLifecycleReinstateInteraction1Adapter
from acme_data.domains.recommendations.dependencies import Dependencies
from acme_data.domains.recommendations.models import InteractionLifecycleActivateInteraction3Command
from acme_data.domains.recommendations.models import InteractionLifecycleTerminateInteraction2Command
from acme_data.domains.recommendations.models import to_interaction_lifecycle_activate_interaction3_command
from acme_data.domains.recommendations.models import to_interaction_lifecycle_terminate_interaction2_command
from acme_data.platform.rpc import async_messages
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


async def handle_activate_interaction(
    deps: Dependencies,
    request: recommendations_v1_interaction_lifecycle_service_pb2.ActivateInteractionRequest
) -> recommendations_v1_interaction_lifecycle_service_pb2.ActivateInteractionResponse:
    """Activates an interaction."""
    response = recommendations_v1_interaction_lifecycle_service_pb2.ActivateInteractionResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('ActivateInteraction', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'ActivateInteraction', {'reason': request.reason})
        response_0 = recommendations_v1_interaction_validation_service_pb2.LintInteractionsResponse()
        response_1 = customers_v1_customer_validation_service_pb2.PreviewCustomerResponse()
        response_2 = featurestore_v1_feature_value_workflow_service_pb2.StartFeatureValueWorkflowResponse()
        response_3 = pipelines_v1_pipeline_run_sync_service_pb2.ResolvePipelineRunConflictResponse()
        outgoing_0 = recommendations_v1_interaction_validation_service_pb2.LintInteractionsRequest(
            context=request.context,
            details=recommendations_v1_interaction_validation_service_pb2.LintInteractionsRequest.Details(
                contact=common_v1_contact_pb2.ContactInfo(
                    phone=request.details.notify_contact.phone,
                    preferred_channel=request.details.notify_contact.preferred_channel
                )
            ),
            interaction=recommendations_v1_recommendations_pb2.Interaction(
                subject=customers_v1_refs_pb2.CustomerRef(display_name=request.details.new_owner.display_name)
            )
        )
        response_0 = await deps.clients.recommendations_interaction_validation.LintInteractions(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = customers_v1_customer_validation_service_pb2.PreviewCustomerRequest(
            context=request.context,
            customer=customers_v1_customers_pb2.Customer(
                contact=common_v1_contact_pb2.ContactInfo(
                    email=request.details.notify_contact.email,
                    name=request.details.notify_contact.name
                ),
                relationship_manager=identity_v1_refs_pb2.UserRef(
                    display_name=response_0.interaction.subject.display_name
                )
            ),
            details=customers_v1_customer_validation_service_pb2.PreviewCustomerRequest.Details(
                contact=common_v1_contact_pb2.ContactInfo(email=response_0.interaction.subject.email)
            )
        )
        envelope_1 = AnyMessage()
        envelope_1.Pack(outgoing_1)
        outgoing_1 = customers_v1_customer_validation_service_pb2.PreviewCustomerRequest()
        if not envelope_1.Unpack(outgoing_1):
            raise ValueError("partner envelope contains the wrong request type")
        response_1 = await deps.clients.customers_customer_validation.PreviewCustomer(
            outgoing_1,
            timeout=deps.settings.timeout
        )
        outgoing_2 = featurestore_v1_feature_value_workflow_service_pb2.StartFeatureValueWorkflowRequest(
            context=request.context,
            details=featurestore_v1_feature_value_workflow_service_pb2.StartFeatureValueWorkflowRequest.Details(
                notify=common_v1_contact_pb2.ContactInfo(
                    preferred_channel=request.details.notify_contact.preferred_channel
                )
            )
        )
        registered_2 = cast(
            featurestore_v1_feature_value_workflow_service_pb2_grpc.FeatureValueWorkflowServiceStub,
            deps.clients.registry['acme.featurestore.v1.FeatureValueWorkflowService']
        )
        response_2 = await registered_2.StartFeatureValueWorkflow(outgoing_2, timeout=deps.settings.timeout)
        command_3 = InteractionLifecycleActivateInteraction3Command(
            context=request.context,
            pipeline_run_assignee_email=request.details.new_owner.email
        )
        outgoing_3 = to_interaction_lifecycle_activate_interaction3_command(command_3)
        response_3 = await deps.clients.pipelines_pipeline_run_sync.ResolvePipelineRunConflict(
            outgoing_3,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.interaction.subject.email
        if returned_0_0:
            response.interaction.subject.email = returned_0_0
        returned_0_1 = response_0.outcome.status
        if returned_0_1:
            response.outcome.status = returned_0_1
        returned_1_0 = response_1.result.correlation_id
        if returned_1_0:
            response.interaction.correlation_id = returned_1_0
        returned_1_1 = response_1.outcome.next_steps
        response.outcome.next_steps.extend(returned_1_1)
        returned_2_0 = response_2.result.details
        response.result.details.update(returned_2_0)
        returned_2_1 = response_2.feature_value.correlation_id
        if returned_2_1:
            response.result.correlation_id = returned_2_1
        returned_3_0 = response_3.outcome.status
        if returned_3_0:
            response.outcome.status = returned_3_0
        echoed_0 = request.interaction_id
        response.interaction.interaction_id = echoed_0
        echoed_1 = request.details.effective_at
        response.outcome.effective_at.CopyFrom(echoed_1)
        return response


async def handle_expire_interaction(
    deps: Dependencies,
    request: recommendations_v1_interaction_lifecycle_service_pb2.ExpireInteractionRequest
) -> recommendations_v1_interaction_lifecycle_service_pb2.ExpireInteractionResponse:
    """Expires an interaction."""
    response = recommendations_v1_interaction_lifecycle_service_pb2.ExpireInteractionResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('ExpireInteraction', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'ExpireInteraction', {'reason': request.reason})
        response_0 = pipelines_v1_pipeline_run_sync_service_pb2.ListPipelineRunConflictsResponse()
        response_1 = audit_v1_audit_event_service_pb2.CreateAuditEventResponse()
        response_2 = recommendations_v1_recommendation_model_query_service_pb2.CountRecommendationModelsResponse()
        outgoing_0 = pipelines_v1_pipeline_run_sync_service_pb2.ListPipelineRunConflictsRequest(
            context=request.context,
            filter=pipelines_v1_pipeline_run_sync_service_pb2.ListPipelineRunConflictsRequest.Filter(
                created_after=request.details.effective_at,
                labels=dict(request.annotations)
            )
        )
        response_0 = await deps.clients.pipelines_pipeline_run_sync.ListPipelineRunConflicts(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = audit_v1_audit_event_service_pb2.CreateAuditEventRequest(
            audit_event=audit_v1_audit_pb2.AuditEvent(
                correlation_id=response_0.result.correlation_id,
                measurements=[audit_v1_audit_pb2.AuditEventMeasurement(observed_at=request.details.effective_at)],
                subject=audit_v1_refs_pb2.AuditTrailRef(display_name=request.details.new_owner.display_name)
            ),
            context=request.context
        )
        send_1 = partial(deps.clients.audit_audit_event.CreateAuditEvent, timeout=deps.settings.timeout)
        response_1 = await send_1(outgoing_1)
        outgoing_2 = recommendations_v1_recommendation_model_query_service_pb2.CountRecommendationModelsRequest(
            context=request.context,
            filter=recommendations_v1_recommendation_model_query_service_pb2.CountRecommendationModelsRequest.Filter(
                created_after=response_1.audit_event.occurred_at,
                labels=dict(response_1.audit_event.attributes),
                owner_id=response_1.audit_event.subject.audit_trail_id
            )
        )
        response_2 = await hooks.interaction_lifecycle_expire_interaction2(
            deps.clients.recommendations_recommendation_model_query,
            outgoing_2,
            deps.settings.timeout
        )
        returned_0_0 = response_0.result.status
        if returned_0_0:
            response.result.status = returned_0_0
        returned_1_0 = response_1.result.correlation_id
        if returned_1_0:
            response.interaction.correlation_id = returned_1_0
        returned_1_1 = response_1.audit_event.correlation_id
        if returned_1_1:
            response.result.correlation_id = returned_1_1
        returned_2_0 = response_2.result.status
        if returned_2_0:
            response.outcome.status = returned_2_0
        returned_2_1 = response_2.result.message
        if returned_2_1:
            response.outcome.message = returned_2_1
        echoed_0 = request.interaction_id
        response.interaction.interaction_id = echoed_0
        echoed_1 = request.details.effective_at
        response.outcome.effective_at.CopyFrom(echoed_1)
        return response


async def handle_get_interaction_lifecycle(
    deps: Dependencies,
    request: recommendations_v1_interaction_lifecycle_service_pb2.GetInteractionLifecycleRequest
) -> recommendations_v1_interaction_lifecycle_service_pb2.GetInteractionLifecycleResponse:
    """Returns an interaction."""
    response = recommendations_v1_interaction_lifecycle_service_pb2.GetInteractionLifecycleResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('GetInteractionLifecycle', extra={'fields': {'domain': 'recommendations'}})
        await deps.repository.audit(request.context.tenant_id, 'GetInteractionLifecycle', {})
        response_0 = recommendations_v1_recommendation_set_query_service_pb2.ExportRecommendationSetsResponse()
        response_1 = customers_v1_consent_record_calculation_service_pb2.EstimateConsentRecordResponse()
        outgoing_0 = recommendations_v1_recommendation_set_query_service_pb2.ExportRecommendationSetsRequest(
            context=request.context,
            filter=recommendations_v1_recommendation_set_query_service_pb2.ExportRecommendationSetsRequest.Filter(
                created_after=request.context.deadline,
                labels=dict(request.context.baggage),
                owner_id=request.interaction_id
            )
        )
        async for chunk_0 in deps.clients.recommendations_recommendation_set_query.ExportRecommendationSets(
            outgoing_0,
            timeout=deps.settings.timeout
        ):
            response_0 = chunk_0
        outgoing_1 = customers_v1_consent_record_calculation_service_pb2.EstimateConsentRecordRequest(
            consent_record=customers_v1_customers_pb2.ConsentRecord(
                attributes=dict(request.context.baggage),
                correlation_id=request.interaction_id,
                occurred_at=request.context.deadline,
                source=request.context.actor.user_id
            ),
            context=request.context
        )
        port_1: InteractionLifecycleGetInteractionLifecycle1Port = InteractionLifecycleGetInteractionLifecycle1Adapter(
            deps.clients.customers_consent_record_calculation,
            deps.settings.timeout
        )
        response_1 = await port_1.execute(outgoing_1)
        returned_1_0 = response_1.consent_record.sequence
        if returned_1_0:
            response.interaction.sequence = returned_1_0
        echoed_0 = request.interaction_id
        response.interaction.interaction_id = echoed_0
        return response


async def handle_reinstate_interaction(
    deps: Dependencies,
    request: recommendations_v1_interaction_lifecycle_service_pb2.ReinstateInteractionRequest
) -> recommendations_v1_interaction_lifecycle_service_pb2.ReinstateInteractionResponse:
    """Reinstates an interaction."""
    response = recommendations_v1_interaction_lifecycle_service_pb2.ReinstateInteractionResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('ReinstateInteraction', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'ReinstateInteraction', {'reason': request.reason})
        response_0 = audit_v1_audit_event_service_pb2.SearchAuditEventsResponse()
        response_1 = recommendations_v1_recommendation_set_service_pb2.CloneRecommendationSetResponse()
        response_2 = customers_v1_household_calculation_service_pb2.SimulateHouseholdResponse()
        outgoing_0 = audit_v1_audit_event_service_pb2.SearchAuditEventsRequest(
            context=request.context,
            filter=audit_v1_audit_event_service_pb2.SearchAuditEventsRequest.Filter(
                created_after=request.details.effective_at
            )
        )
        response_0 = await deps.clients.audit_audit_event.SearchAuditEvents(outgoing_0, timeout=deps.settings.timeout)
        outgoing_1 = recommendations_v1_recommendation_set_service_pb2.CloneRecommendationSetRequest(
            context=request.context,
            recommendation_set=recommendations_v1_recommendations_pb2.RecommendationSet(
                audit=common_v1_audit_pb2.AuditInfo(updated_at=request.details.effective_at),
                counterparty=customers_v1_refs_pb2.CustomerRef(
                    display_name=request.details.new_owner.display_name,
                    email=request.details.new_owner.email
                )
            )
        )
        response_1 = await InteractionLifecycleReinstateInteraction1Adapter(
            deps.clients.recommendations_recommendation_set,
            deps.settings.timeout
        )(outgoing_1)
        outgoing_2 = customers_v1_household_calculation_service_pb2.SimulateHouseholdRequest(
            context=request.context,
            household=customers_v1_customers_pb2.Household(
                children=[
                    customers_v1_customers_pb2.Household(
                        children=[
                            customers_v1_customers_pb2.Household(
                                audit=common_v1_audit_pb2.AuditInfo(
                                    created_at=response_1.recommendation_set.audit.created_at,
                                    etag=response_1.recommendation_set.audit.etag
                                ),
                                manager=identity_v1_refs_pb2.UserRef(email=request.details.new_owner.email)
                            )
                        ]
                    )
                ]
            )
        )
        response_2 = cast(customers_v1_household_calculation_service_pb2.SimulateHouseholdResponse, await deps.bus.request(
            'acme.recommendations.v1.InteractionLifecycleService/ReinstateInteraction/2', outgoing_2, deps.settings.timeout,
        ))
        returned_0_0 = response_0.result.status
        if returned_0_0:
            response.outcome.status = returned_0_0
        returned_1_0 = response_1.recommendation_set.counterparty.email
        if returned_1_0:
            response.interaction.subject.email = returned_1_0
        returned_2_0 = response_2.result.status
        if returned_2_0:
            response.outcome.status = returned_2_0
        echoed_0 = request.interaction_id
        response.interaction.interaction_id = echoed_0
        echoed_1 = request.details.effective_at
        response.outcome.effective_at.CopyFrom(echoed_1)
        return response


async def handle_renew_interaction(
    deps: Dependencies,
    request: recommendations_v1_interaction_lifecycle_service_pb2.RenewInteractionRequest
) -> recommendations_v1_interaction_lifecycle_service_pb2.RenewInteractionResponse:
    """Renews an interaction."""
    response = recommendations_v1_interaction_lifecycle_service_pb2.RenewInteractionResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('RenewInteraction', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'RenewInteraction', {'reason': request.reason})
        response_0 = recommendations_v1_recommendation_model_validation_service_pb2.NormalizeRecommendationModelResponse()
        response_1 = customers_v1_consent_record_calculation_service_pb2.EstimateConsentRecordResponse()
        outgoing_0 = recommendations_v1_recommendation_model_validation_service_pb2.NormalizeRecommendationModelRequest(
            context=request.context,
            details=recommendations_v1_recommendation_model_validation_service_pb2.NormalizeRecommendationModelRequest.Details(
                contact=common_v1_contact_pb2.ContactInfo(
                    email=request.details.new_owner.email,
                    phone=request.details.notify_contact.phone
                )
            ),
            recommendation_model=recommendations_v1_recommendations_pb2.RecommendationModel(
                owner=identity_v1_refs_pb2.UserRef(email=request.details.notify_contact.email)
            )
        )
        response_0 = await deps.clients.recommendations_recommendation_model_validation.NormalizeRecommendationModel(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = customers_v1_consent_record_calculation_service_pb2.EstimateConsentRecordRequest(
            context=request.context,
            details=customers_v1_consent_record_calculation_service_pb2.EstimateConsentRecordRequest.Details(
                destination=common_v1_address_pb2.PostalAddress(
                    locality=response_0.recommendation_model.address.locality,
                    recipient=response_0.recommendation_model.address.recipient,
                    region=response_0.recommendation_model.address.region
                )
            )
        )
        method_name_1 = 'EstimateConsentRecord'
        response_1 = await getattr(
            deps.clients.customers_consent_record_calculation,
            method_name_1
        )(outgoing_1, timeout=deps.settings.timeout)
        returned_0_0 = response_0.result.correlation_id
        if returned_0_0:
            response.interaction.correlation_id = returned_0_0
        returned_0_1 = response_0.recommendation_model.dimensions.unit
        returned_0_1_part_1 = response.interaction.measurements.add()
        if returned_0_1:
            returned_0_1_part_1.unit = returned_0_1
        returned_1_0 = response_1.consent_record.attributes
        response.interaction.attributes.update(returned_1_0)
        returned_1_1 = response_1.consent_record.kind
        if returned_1_1:
            response.interaction.kind = returned_1_1
        echoed_0 = request.interaction_id
        response.interaction.interaction_id = echoed_0
        echoed_1 = request.details.effective_at
        response.outcome.effective_at.CopyFrom(echoed_1)
        return response


async def handle_schedule_interaction_expiry(
    deps: Dependencies,
    request: recommendations_v1_interaction_lifecycle_service_pb2.ScheduleInteractionExpiryRequest
) -> recommendations_v1_interaction_lifecycle_service_pb2.ScheduleInteractionExpiryResponse:
    """Schedules an interaction."""
    response = recommendations_v1_interaction_lifecycle_service_pb2.ScheduleInteractionExpiryResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('ScheduleInteractionExpiry', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'ScheduleInteractionExpiry', {'reason': request.reason})
        await deps.repository.save_interaction(request.context.tenant_id, request.interaction)
        response_0 = customers_v1_customer_query_service_pb2.BrowseCustomersResponse()
        response_1 = recommendations_v1_recommendation_model_validation_service_pb2.ScoreRecommendationModelResponse()
        outgoing_0 = customers_v1_customer_query_service_pb2.BrowseCustomersRequest(
            context=request.context,
            filter=customers_v1_customer_query_service_pb2.BrowseCustomersRequest.Filter(
                created_after=request.interaction.occurred_at,
                labels=dict(request.details.parameters)
            )
        )
        response_0 = await deps.clients.customers_customer_query.BrowseCustomers(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        requests_1: list[
            recommendations_v1_recommendation_model_validation_service_pb2.ScoreRecommendationModelRequest
        ] = []
        for item_1 in request.interaction.measurements:
            outgoing_1 = recommendations_v1_recommendation_model_validation_service_pb2.ScoreRecommendationModelRequest(
                context=request.context,
                recommendation_model=recommendations_v1_recommendations_pb2.RecommendationModel(
                    audit=common_v1_audit_pb2.AuditInfo(created_at=item_1.observed_at),
                    dimensions=recommendations_v1_recommendations_pb2.RecommendationModelDimensions(unit=item_1.unit),
                    owner=identity_v1_refs_pb2.UserRef(email=request.interaction.subject.email)
                )
            )
            requests_1.append(outgoing_1)
        replies_1 = await asyncio.gather(*(
            deps.clients.recommendations_recommendation_model_validation.ScoreRecommendationModel(
                entry,
                timeout=deps.settings.timeout
            ) for entry in requests_1
        ))
        if replies_1:
            response_1 = replies_1[-1]
        returned_0_0 = response_0.result.message
        if returned_0_0:
            response.outcome.message = returned_0_0
        returned_0_1 = response_0.result.status
        if returned_0_1:
            response.outcome.status = returned_0_1
        echoed_0 = request.interaction_id
        response.interaction.interaction_id = echoed_0
        echoed_1 = request.interaction.sequence
        response.interaction.sequence = echoed_1
        return response


async def handle_suspend_interaction(
    deps: Dependencies,
    request: recommendations_v1_interaction_lifecycle_service_pb2.SuspendInteractionRequest
) -> recommendations_v1_interaction_lifecycle_service_pb2.SuspendInteractionResponse:
    """Suspends an interaction."""
    response = recommendations_v1_interaction_lifecycle_service_pb2.SuspendInteractionResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('SuspendInteraction', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'SuspendInteraction', {'reason': request.reason})
        response_0 = metrics_v1_metric_series_export_service_pb2.ScheduleMetricSeriesExportResponse()
        response_1 = metrics_v1_metric_series_service_pb2.UpdateMetricSeriesResponse()
        outgoing_0 = metrics_v1_metric_series_export_service_pb2.ScheduleMetricSeriesExportRequest(
            annotations=dict(request.annotations),
            context=request.context
        )
        response_0 = await deps.clients.metrics_metric_series_export.ScheduleMetricSeriesExport(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = metrics_v1_metric_series_service_pb2.UpdateMetricSeriesRequest()
        outgoing_1.context.CopyFrom(request.context)
        outgoing_1.metric_series.owner.display_name = request.details.new_owner.display_name
        outgoing_1.metric_series.owner.email = request.details.notify_contact.email
        outgoing_1.metric_series.owner.user_id = request.details.new_owner.user_id
        outgoing_1.metric_series.audit.created_at.CopyFrom(request.details.effective_at)
        merged_1 = metrics_v1_metric_series_service_pb2.UpdateMetricSeriesRequest()
        merged_1.MergeFrom(outgoing_1)
        outgoing_1.CopyFrom(merged_1)
        response_1 = await deps.clients.metrics_metric_series.UpdateMetricSeries(
            outgoing_1,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.result.reference_ids
        response.result.reference_ids.extend(returned_0_0)
        returned_0_1 = response_0.result.message
        if returned_0_1:
            response.result.message = returned_0_1
        returned_1_0 = response_1.result.status
        if returned_1_0:
            response.result.status = returned_1_0
        echoed_0 = request.interaction_id
        response.interaction.interaction_id = echoed_0
        echoed_1 = request.details.effective_at
        response.outcome.effective_at.CopyFrom(echoed_1)
        return response


async def handle_terminate_interaction(
    deps: Dependencies,
    request: recommendations_v1_interaction_lifecycle_service_pb2.TerminateInteractionRequest
) -> recommendations_v1_interaction_lifecycle_service_pb2.TerminateInteractionResponse:
    """Terminates an interaction."""
    response = recommendations_v1_interaction_lifecycle_service_pb2.TerminateInteractionResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('TerminateInteraction', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'TerminateInteraction', {'reason': request.reason})
        response_0 = customers_v1_customer_segment_validation_service_pb2.CheckCustomerSegmentEligibilityResponse()
        response_1 = metrics_v1_dashboard_history_service_pb2.AnnotateDashboardVersionResponse()
        response_2 = media_v1_media_asset_calculation_service_pb2.ExplainMediaAssetCalculationResponse()
        outgoing_0 = customers_v1_customer_segment_validation_service_pb2.CheckCustomerSegmentEligibilityRequest(
            context=request.context,
            customer_segment=customers_v1_customers_pb2.CustomerSegment(
                owner=identity_v1_refs_pb2.UserRef(user_id=request.details.new_owner.user_id)
            ),
            details=customers_v1_customer_segment_validation_service_pb2.CheckCustomerSegmentEligibilityRequest.Details(
                contact=common_v1_contact_pb2.ContactInfo(email=request.details.notify_contact.email)
            )
        )
        response_0 = await deps.clients.customers_customer_segment_validation.CheckCustomerSegmentEligibility(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = metrics_v1_dashboard_history_service_pb2.AnnotateDashboardVersionRequest(
            context=request.context,
            dashboard=metrics_v1_metrics_pb2.Dashboard(
                audit=common_v1_audit_pb2.AuditInfo(created_by=response_0.customer_segment.audit.created_by)
            )
        )
        registered_1 = cast(
            metrics_v1_dashboard_history_service_pb2_grpc.DashboardHistoryServiceStub,
            deps.clients.registry['acme.metrics.v1.DashboardHistoryService']
        )
        response_1 = await registered_1.AnnotateDashboardVersion(outgoing_1, timeout=deps.settings.timeout)
        command_2 = InteractionLifecycleTerminateInteraction2Command(
            context=request.context,
            media_asset_owner_email=request.details.new_owner.email,
            details_contact_email=response_0.customer_segment.owner.email
        )
        outgoing_2 = to_interaction_lifecycle_terminate_interaction2_command(command_2)
        response_2 = await deps.clients.media_media_asset_calculation.ExplainMediaAssetCalculation(
            outgoing_2,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.customer_segment.owner.display_name
        if returned_0_0:
            response.interaction.subject.display_name = returned_0_0
        returned_1_0 = response_1.result.status
        if returned_1_0:
            response.outcome.status = returned_1_0
        returned_1_1 = response_1.outcome.next_steps
        response.outcome.next_steps.extend(returned_1_1)
        returned_2_0 = response_2.result.correlation_id
        if returned_2_0:
            response.interaction.correlation_id = returned_2_0
        returned_2_1 = response_2.outcome.message
        if returned_2_1:
            response.result.message = returned_2_1
        echoed_0 = request.interaction_id
        response.interaction.interaction_id = echoed_0
        echoed_1 = request.details.effective_at
        response.outcome.effective_at.CopyFrom(echoed_1)
        return response
