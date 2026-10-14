"""Application workflow for PipelineStep Calculation."""

from __future__ import annotations

from functools import partial
from typing import cast
import logging

from google.protobuf.json_format import MessageToDict
from google.protobuf.json_format import MessageToJson
from google.protobuf.json_format import Parse
from google.protobuf.json_format import ParseDict

from acme.anomalies.v1 import (
    anomaly_feedback_calculation_service_pb2 as anomalies_v1_anomaly_feedback_calculation_service_pb2,
)
from acme.audit.v1 import audit_event_query_service_pb2 as audit_v1_audit_event_query_service_pb2
from acme.audit.v1 import audit_event_query_service_pb2_grpc as audit_v1_audit_event_query_service_pb2_grpc
from acme.authorization.v1 import access_policy_service_pb2 as authorization_v1_access_policy_service_pb2
from acme.authorization.v1 import authorization_pb2 as authorization_v1_authorization_pb2
from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.featureflags.v1 import (
    feature_flag_validation_service_pb2 as featureflags_v1_feature_flag_validation_service_pb2,
)
from acme.featureflags.v1 import featureflags_pb2 as featureflags_v1_featureflags_pb2
from acme.featurestore.v1 import feature_view_query_service_pb2 as featurestore_v1_feature_view_query_service_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.labeling.v1 import label_set_validation_service_pb2 as labeling_v1_label_set_validation_service_pb2
from acme.labeling.v1 import labeling_pb2 as labeling_v1_labeling_pb2
from acme.labeling.v1 import labeling_task_service_pb2 as labeling_v1_labeling_task_service_pb2
from acme.lineage.v1 import impact_validation_service_pb2 as lineage_v1_impact_validation_service_pb2
from acme.lineage.v1 import lineage_edge_calculation_service_pb2 as lineage_v1_lineage_edge_calculation_service_pb2
from acme.modelregistry.v1 import (
    registered_model_validation_service_pb2 as modelregistry_v1_registered_model_validation_service_pb2,
)
from acme.pipelines.v1 import pipeline_calculation_service_pb2 as pipelines_v1_pipeline_calculation_service_pb2
from acme.pipelines.v1 import pipeline_run_calculation_service_pb2 as pipelines_v1_pipeline_run_calculation_service_pb2
from acme.pipelines.v1 import (
    pipeline_step_calculation_service_pb2 as pipelines_v1_pipeline_step_calculation_service_pb2,
)
from acme.pipelines.v1 import pipelines_pb2 as pipelines_v1_pipelines_pb2
from acme.yards.v1 import yard_calculation_service_pb2 as yards_v1_yard_calculation_service_pb2
from acme.yards.v1 import yards_pb2 as yards_v1_yards_pb2

from acme_data.domains.pipelines import hooks
from acme_data.domains.pipelines.adapters import PipelineStepCalculationCalculatePipelineStep1Adapter
from acme_data.domains.pipelines.adapters import PipelineStepCalculationSimulatePipelineStep2Adapter
from acme_data.domains.pipelines.adapters import PipelineStepCalculationSimulatePipelineStep2Port
from acme_data.domains.pipelines.dependencies import Dependencies
from acme_data.domains.pipelines.models import PipelineStepCalculationQuotePipelineStep0Command
from acme_data.domains.pipelines.models import PipelineStepCalculationQuotePipelineStep1Command
from acme_data.domains.pipelines.models import to_pipeline_step_calculation_quote_pipeline_step0_command
from acme_data.domains.pipelines.models import to_pipeline_step_calculation_quote_pipeline_step1_command
from acme_data.platform.rpc import run_steps
from acme_data.platform.tenancy import tenant_id
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class PipelineStepCalculationServicerWorkflow:
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    async def handle_calculate_pipeline_step(
        self,
        request: pipelines_v1_pipeline_step_calculation_service_pb2.CalculatePipelineStepRequest
    ) -> pipelines_v1_pipeline_step_calculation_service_pb2.CalculatePipelineStepResponse:
        """Calculates a pipeline step."""
        deps = self.deps
        response = pipelines_v1_pipeline_step_calculation_service_pb2.CalculatePipelineStepResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CalculatePipelineStep', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'CalculatePipelineStep', {'reason': request.reason})
            await deps.repository.save_pipeline_step(request.context.tenant_id, request.pipeline_step)
            response_0 = pipelines_v1_pipeline_calculation_service_pb2.ComparePipelineOptionsResponse()
            response_1 = lineage_v1_lineage_edge_calculation_service_pb2.QuoteLineageEdgeResponse()
            outgoing_0 = pipelines_v1_pipeline_calculation_service_pb2.ComparePipelineOptionsRequest(
                context=request.context,
                details=pipelines_v1_pipeline_calculation_service_pb2.ComparePipelineOptionsRequest.Details(
                    destination=common_v1_address_pb2.PostalAddress(locality=request.details.destination.locality)
                )
            )
            steps_0 = [
                partial(
                    deps.clients.pipelines_pipeline_calculation.ComparePipelineOptions,
                    outgoing_0,
                    timeout=deps.settings.timeout
                )
            ]
            results_0 = await run_steps(steps_0)
            response_0 = results_0[-1]
            outgoing_1 = lineage_v1_lineage_edge_calculation_service_pb2.QuoteLineageEdgeRequest(
                context=request.context,
                details=lineage_v1_lineage_edge_calculation_service_pb2.QuoteLineageEdgeRequest.Details(
                    destination=common_v1_address_pb2.PostalAddress(
                        country_code=response_0.pipeline.location.country_code,
                        recipient=request.details.destination.recipient,
                        region=request.details.destination.region
                    )
                )
            )
            response_1 = await PipelineStepCalculationCalculatePipelineStep1Adapter(
                deps.clients.lineage_lineage_edge_calculation,
                deps.settings.timeout
            )(outgoing_1)
            returned_0_0 = response_0.breakdown.currency_code
            if returned_0_0:
                response.breakdown.currency_code = returned_0_0
            returned_0_1 = response_0.pipeline.audit.created_by
            if returned_0_1:
                response.pipeline_step.audit.created_by = returned_0_1
            returned_1_0 = response_1.result.correlation_id
            if returned_1_0:
                response.result.correlation_id = returned_1_0
            echoed_0 = request.pipeline_step_id
            response.pipeline_step.pipeline_step_id = echoed_0
            echoed_1 = request.pipeline_step.priority
            response.pipeline_step.priority = echoed_1
            return response

    async def handle_compare_pipeline_step_options(
        self,
        request: pipelines_v1_pipeline_step_calculation_service_pb2.ComparePipelineStepOptionsRequest
    ) -> pipelines_v1_pipeline_step_calculation_service_pb2.ComparePipelineStepOptionsResponse:
        """Compares a pipeline step."""
        deps = self.deps
        response = pipelines_v1_pipeline_step_calculation_service_pb2.ComparePipelineStepOptionsResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ComparePipelineStepOptions', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ComparePipelineStepOptions',
                {'reason': request.reason}
            )
            await deps.repository.save_pipeline_step(request.context.tenant_id, request.pipeline_step)
            response_0 = pipelines_v1_pipeline_calculation_service_pb2.ComparePipelineOptionsResponse()
            response_1 = pipelines_v1_pipeline_calculation_service_pb2.CalculatePipelineResponse()
            response_2 = pipelines_v1_pipeline_run_calculation_service_pb2.EstimatePipelineRunResponse()
            response_3 = pipelines_v1_pipeline_run_calculation_service_pb2.CalculatePipelineRunResponse()
            outgoing_0 = pipelines_v1_pipeline_calculation_service_pb2.ComparePipelineOptionsRequest(
                context=request.context,
                details=pipelines_v1_pipeline_calculation_service_pb2.ComparePipelineOptionsRequest.Details(
                    destination=common_v1_address_pb2.PostalAddress(locality=request.details.destination.locality)
                ),
                pipeline=pipelines_v1_pipelines_pb2.Pipeline(
                    location=common_v1_address_pb2.PostalAddress(recipient=request.details.destination.recipient),
                    participants=[
                        pipelines_v1_pipelines_pb2.PipelineParticipant(
                            contact=common_v1_contact_pb2.ContactInfo(email=request.pipeline_step.owner.email)
                        )
                    ]
                )
            )
            response_0 = cast(pipelines_v1_pipeline_calculation_service_pb2.ComparePipelineOptionsResponse, await deps.bus.request(
                'acme.pipelines.v1.PipelineStepCalculationService/ComparePipelineStepOptions/0', outgoing_0, deps.settings.timeout,
            ))
            outgoing_1 = pipelines_v1_pipeline_calculation_service_pb2.CalculatePipelineRequest(
                context=request.context,
                pipeline=pipelines_v1_pipelines_pb2.Pipeline(
                    audit=common_v1_audit_pb2.AuditInfo(updated_at=request.pipeline_step.audit.updated_at),
                    location=common_v1_address_pb2.PostalAddress(
                        country_code=response_0.pipeline.location.country_code,
                        locality=request.details.destination.locality
                    ),
                    participants=[
                        pipelines_v1_pipelines_pb2.PipelineParticipant(
                            contact=common_v1_contact_pb2.ContactInfo(email=request.pipeline_step.owner.email)
                        )
                    ]
                )
            )
            response_1 = await deps.clients.pipelines_pipeline_calculation.CalculatePipeline(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = pipelines_v1_pipeline_run_calculation_service_pb2.EstimatePipelineRunRequest(
                context=request.context,
                details=pipelines_v1_pipeline_run_calculation_service_pb2.EstimatePipelineRunRequest.Details(
                    destination=common_v1_address_pb2.PostalAddress(
                        country_code=request.details.destination.country_code,
                        lines=list(request.details.destination.lines)
                    )
                ),
                pipeline_run=pipelines_v1_pipelines_pb2.PipelineRun(
                    requester=common_v1_contact_pb2.ContactInfo(email=response_1.pipeline.organizer.email)
                )
            )
            method_name_2 = 'EstimatePipelineRun'
            response_2 = await getattr(
                deps.clients.pipelines_pipeline_run_calculation,
                method_name_2
            )(outgoing_2, timeout=deps.settings.timeout)
            outgoing_3 = pipelines_v1_pipeline_run_calculation_service_pb2.CalculatePipelineRunRequest()
            outgoing_3.context.CopyFrom(request.context)
            if response_2.pipeline_run.WhichOneof('origin') == 'customer':
                outgoing_3.pipeline_run.customer.starts_at.CopyFrom(response_2.pipeline_run.customer.starts_at)
            field_3_2_part_1 = outgoing_3.pipeline_run.comments.add()
            field_3_2_part_1.created_at.CopyFrom(request.pipeline_step.audit.created_at)
            response_3 = await deps.clients.pipelines_pipeline_run_calculation.CalculatePipelineRun(
                outgoing_3,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.status
            if returned_0_0:
                response.result.status = returned_0_0
            returned_0_1 = response_0.result.correlation_id
            if returned_0_1:
                response.result.correlation_id = returned_0_1
            returned_1_0 = response_1.pipeline.audit.etag
            if returned_1_0:
                response.pipeline_step.audit.etag = returned_1_0
            returned_2_0 = response_2.result.details
            response.result.details.update(returned_2_0)
            returned_3_0 = response_3.pipeline_run.customer.display_name
            if returned_3_0:
                response.pipeline_step.owner.display_name = returned_3_0
            returned_3_1 = response_3.pipeline_run.audit.updated_at
            if returned_3_1.ListFields():
                response.pipeline_step.audit.updated_at.MergeFrom(returned_3_1)
            echoed_0 = request.pipeline_step_id
            response.pipeline_step.pipeline_step_id = echoed_0
            echoed_1 = request.pipeline_step.effective
            response.pipeline_step.effective.CopyFrom(echoed_1)
            return response

    async def handle_estimate_pipeline_step(
        self,
        request: pipelines_v1_pipeline_step_calculation_service_pb2.EstimatePipelineStepRequest
    ) -> pipelines_v1_pipeline_step_calculation_service_pb2.EstimatePipelineStepResponse:
        """Estimates a pipeline step."""
        deps = self.deps
        response = pipelines_v1_pipeline_step_calculation_service_pb2.EstimatePipelineStepResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('EstimatePipelineStep', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'EstimatePipelineStep', {'reason': request.reason})
            await deps.repository.save_pipeline_step(request.context.tenant_id, request.pipeline_step)
            response_0 = featureflags_v1_feature_flag_validation_service_pb2.CheckFeatureFlagEligibilityResponse()
            response_1 = authorization_v1_access_policy_service_pb2.UpdateAccessPolicyResponse()
            response_2 = lineage_v1_impact_validation_service_pb2.PreviewImpactResponse()
            outgoing_0 = featureflags_v1_feature_flag_validation_service_pb2.CheckFeatureFlagEligibilityRequest(
                context=request.context,
                feature_flag=featureflags_v1_featureflags_pb2.FeatureFlag(
                    audit=common_v1_audit_pb2.AuditInfo(updated_at=request.pipeline_step.audit.updated_at)
                )
            )
            document_0 = MessageToDict(outgoing_0, preserving_proto_field_name=True)
            outgoing_0 = ParseDict(
                document_0,
                featureflags_v1_feature_flag_validation_service_pb2.CheckFeatureFlagEligibilityRequest()
            )
            response_0 = await deps.clients.featureflags_feature_flag_validation.CheckFeatureFlagEligibility(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = authorization_v1_access_policy_service_pb2.UpdateAccessPolicyRequest(
                access_policy=authorization_v1_authorization_pb2.AccessPolicy(
                    audit=common_v1_audit_pb2.AuditInfo(
                        etag=response_0.feature_flag.audit.etag,
                        updated_at=response_0.feature_flag.audit.updated_at
                    ),
                    route=authorization_v1_authorization_pb2.AccessPolicyRouteAction(
                        target=request.pipeline_step.route.target,
                        weight=request.pipeline_step.route.weight
                    )
                ),
                context=request.context
            )
            document_1 = MessageToJson(outgoing_1, preserving_proto_field_name=True)
            outgoing_1 = Parse(document_1, authorization_v1_access_policy_service_pb2.UpdateAccessPolicyRequest())
            response_1 = await deps.clients.authorization_access_policy.UpdateAccessPolicy(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = lineage_v1_impact_validation_service_pb2.PreviewImpactRequest()
            outgoing_2.context.CopyFrom(request.context)
            outgoing_2.impact.assignee.user_id = response_0.feature_flag.owner.user_id
            merged_2 = lineage_v1_impact_validation_service_pb2.PreviewImpactRequest()
            merged_2.MergeFrom(outgoing_2)
            outgoing_2.CopyFrom(merged_2)
            response_2 = await deps.clients.lineage_impact_validation.PreviewImpact(
                outgoing_2,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.feature_flag.name
            if returned_0_0:
                response.pipeline_step.name = returned_0_0
            returned_0_1 = response_0.feature_flag.scopes
            response.pipeline_step.scopes.extend(returned_0_1)
            returned_1_0 = response_1.access_policy.priority
            if returned_1_0:
                response.pipeline_step.priority = returned_1_0
            returned_2_0 = response_2.result.reference_ids
            response.result.reference_ids.extend(returned_2_0)
            returned_2_1 = response_2.outcome.message
            if returned_2_1:
                response.result.message = returned_2_1
            echoed_0 = request.pipeline_step_id
            response.pipeline_step.pipeline_step_id = echoed_0
            echoed_1 = request.pipeline_step.version
            response.pipeline_step.version = echoed_1
            return response

    async def handle_get_pipeline_step_rates(
        self,
        request: pipelines_v1_pipeline_step_calculation_service_pb2.GetPipelineStepRatesRequest
    ) -> pipelines_v1_pipeline_step_calculation_service_pb2.GetPipelineStepRatesResponse:
        """Returns a pipeline step."""
        deps = self.deps
        response = pipelines_v1_pipeline_step_calculation_service_pb2.GetPipelineStepRatesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('GetPipelineStepRates', extra={'fields': {'domain': 'pipelines'}})
            await deps.repository.audit(request.context.tenant_id, 'GetPipelineStepRates', {})
            response_0 = yards_v1_yard_calculation_service_pb2.SimulateYardResponse()
            response_1 = audit_v1_audit_event_query_service_pb2.SuggestAuditEventsResponse()
            outgoing_0 = yards_v1_yard_calculation_service_pb2.SimulateYardRequest(
                context=request.context,
                yard=yards_v1_yards_pb2.Yard(
                    owner=identity_v1_refs_pb2.UserRef(
                        email=request.context.actor.email,
                        user_id=request.context.actor.user_id
                    )
                )
            )
            response_0 = await deps.clients.yards_yard_calculation.SimulateYard(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = audit_v1_audit_event_query_service_pb2.SuggestAuditEventsRequest(
                context=request.context,
                filter=audit_v1_audit_event_query_service_pb2.SuggestAuditEventsRequest.Filter(
                    created_after=response_0.yard.audit.updated_at,
                    owner_id=response_0.yard.components.get('primary', yards_v1_yards_pb2.YardComponent()).component_id,
                    region=response_0.yard.address.region
                )
            )
            registered_1 = cast(
                audit_v1_audit_event_query_service_pb2_grpc.AuditEventQueryServiceStub,
                deps.clients.registry['acme.audit.v1.AuditEventQueryService']
            )
            response_1 = await registered_1.SuggestAuditEvents(outgoing_1, timeout=deps.settings.timeout)
            returned_0_0 = response_0.result.details
            response.result.details.update(returned_0_0)
            returned_1_0 = response_1.result.correlation_id
            if returned_1_0:
                response.result.correlation_id = returned_1_0
            echoed_0 = request.pipeline_step_id
            response.pipeline_step.pipeline_step_id = echoed_0
            return response

    async def handle_quote_pipeline_step(
        self,
        request: pipelines_v1_pipeline_step_calculation_service_pb2.QuotePipelineStepRequest
    ) -> pipelines_v1_pipeline_step_calculation_service_pb2.QuotePipelineStepResponse:
        """Quotes a pipeline step."""
        deps = self.deps
        response = pipelines_v1_pipeline_step_calculation_service_pb2.QuotePipelineStepResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('QuotePipelineStep', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'QuotePipelineStep', {'reason': request.reason})
            await deps.repository.save_pipeline_step(request.context.tenant_id, request.pipeline_step)
            response_0 = modelregistry_v1_registered_model_validation_service_pb2.ScoreRegisteredModelResponse()
            response_1 = anomalies_v1_anomaly_feedback_calculation_service_pb2.RecalculateAnomalyFeedbacksResponse()
            response_2 = featurestore_v1_feature_view_query_service_pb2.BrowseFeatureViewsResponse()
            command_0 = PipelineStepCalculationQuotePipelineStep0Command(
                context=request.context,
                registered_model_address_region=request.details.destination.region,
                registered_model_audit_updated_at=request.pipeline_step.audit.updated_at,
                registered_model_owner_email=request.pipeline_step.owner.email
            )
            outgoing_0 = to_pipeline_step_calculation_quote_pipeline_step0_command(command_0)
            response_0 = await deps.clients.modelregistry_registered_model_validation.ScoreRegisteredModel(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            command_1 = PipelineStepCalculationQuotePipelineStep1Command.model_validate(
                {
                    'context': request.context,
                    'details_destination_postal_code': response_0.registered_model.address.postal_code
                }
            )
            outgoing_1 = to_pipeline_step_calculation_quote_pipeline_step1_command(command_1)
            response_1 = await deps.clients.anomalies_anomaly_feedback_calculation.RecalculateAnomalyFeedbacks(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = featurestore_v1_feature_view_query_service_pb2.BrowseFeatureViewsRequest(
                context=request.context,
                filter=featurestore_v1_feature_view_query_service_pb2.BrowseFeatureViewsRequest.Filter(
                    created_after=request.pipeline_step.audit.created_at,
                    owner_id=response_1.anomaly_feedback.subject.dataset_id,
                    region=response_0.registered_model.address.region
                )
            )
            send_2 = partial(
                deps.clients.featurestore_feature_view_query.BrowseFeatureViews,
                timeout=deps.settings.timeout
            )
            response_2 = await send_2(outgoing_2)
            returned_0_0 = response_0.registered_model.audit.etag
            if returned_0_0:
                response.pipeline_step.audit.etag = returned_0_0
            returned_1_0 = response_1.breakdown.currency_code
            if returned_1_0:
                response.breakdown.currency_code = returned_1_0
            returned_1_1 = response_1.anomaly_feedback.subject.display_name
            if returned_1_1:
                response.pipeline_step.owner.display_name = returned_1_1
            returned_2_0 = response_2.result.status
            if returned_2_0:
                response.result.status = returned_2_0
            returned_2_1 = response_2.result.reference_ids
            response.result.reference_ids.extend(returned_2_1)
            echoed_0 = request.pipeline_step_id
            response.pipeline_step.pipeline_step_id = echoed_0
            echoed_1 = request.pipeline_step.parameters
            response.pipeline_step.parameters.update(echoed_1)
            return response

    async def handle_simulate_pipeline_step(
        self,
        request: pipelines_v1_pipeline_step_calculation_service_pb2.SimulatePipelineStepRequest
    ) -> pipelines_v1_pipeline_step_calculation_service_pb2.SimulatePipelineStepResponse:
        """Simulates a pipeline step."""
        deps = self.deps
        response = pipelines_v1_pipeline_step_calculation_service_pb2.SimulatePipelineStepResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SimulatePipelineStep', extra={'fields': {'reason': request.reason}})
            await deps.repository.audit(request.context.tenant_id, 'SimulatePipelineStep', {'reason': request.reason})
            await deps.repository.save_pipeline_step(request.context.tenant_id, request.pipeline_step)
            response_0 = pipelines_v1_pipeline_run_calculation_service_pb2.CalculatePipelineRunResponse()
            response_1 = pipelines_v1_pipeline_calculation_service_pb2.CalculatePipelineResponse()
            response_2 = labeling_v1_label_set_validation_service_pb2.NormalizeLabelSetResponse()
            response_3 = labeling_v1_labeling_task_service_pb2.UpdateLabelingTaskResponse()
            outgoing_0 = pipelines_v1_pipeline_run_calculation_service_pb2.CalculatePipelineRunRequest(
                context=request.context,
                details=pipelines_v1_pipeline_run_calculation_service_pb2.CalculatePipelineRunRequest.Details(
                    destination=common_v1_address_pb2.PostalAddress(recipient=request.details.destination.recipient)
                ),
                pipeline_run=pipelines_v1_pipelines_pb2.PipelineRun(
                    audit=common_v1_audit_pb2.AuditInfo(
                        etag=request.pipeline_step.audit.etag,
                        updated_at=request.pipeline_step.audit.updated_at,
                        updated_by=request.pipeline_step.audit.updated_by
                    )
                )
            )
            response_0 = await hooks.pipeline_step_calculation_simulate_pipeline_step0(
                deps.clients.pipelines_pipeline_run_calculation,
                outgoing_0,
                deps.settings.timeout
            )
            outgoing_1 = pipelines_v1_pipeline_calculation_service_pb2.CalculatePipelineRequest()
            outgoing_1.context.CopyFrom(request.context)
            field_1_1_part_1 = outgoing_1.pipeline.participants.add()
            field_1_1_part_1.contact.preferred_channel = response_0.pipeline_run.requester.preferred_channel
            field_1_2_part_1 = outgoing_1.pipeline.participants.add()
            field_1_2_part_1.contact.email = response_0.pipeline_run.assignee.email
            outgoing_1.context.tenant_id = tenant_id.get()
            response_1 = await deps.clients.pipelines_pipeline_calculation.CalculatePipeline(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            outgoing_2 = labeling_v1_label_set_validation_service_pb2.NormalizeLabelSetRequest(
                context=request.context,
                label_set=labeling_v1_labeling_pb2.LabelSet(
                    children=[
                        labeling_v1_labeling_pb2.LabelSet(
                            children=[
                                labeling_v1_labeling_pb2.LabelSet(
                                    location=common_v1_address_pb2.PostalAddress(
                                        locality=request.details.destination.locality,
                                        postal_code=response_1.pipeline.location.postal_code
                                    ),
                                    manager=identity_v1_refs_pb2.UserRef(
                                        display_name=response_0.pipeline_run.assignee.display_name,
                                        email=response_0.pipeline_run.assignee.email
                                    )
                                )
                            ]
                        )
                    ]
                )
            )
            port_2: PipelineStepCalculationSimulatePipelineStep2Port = PipelineStepCalculationSimulatePipelineStep2Adapter(
                deps.clients.labeling_label_set_validation,
                deps.settings.timeout
            )
            response_2 = await port_2.execute(outgoing_2)
            outgoing_3 = labeling_v1_labeling_task_service_pb2.UpdateLabelingTaskRequest(
                context=request.context,
                labeling_task=labeling_v1_labeling_pb2.LabelingTask(
                    assignee=identity_v1_refs_pb2.UserRef(user_id=response_0.pipeline_run.assignee.user_id),
                    audit=common_v1_audit_pb2.AuditInfo(
                        etag=response_1.pipeline.audit.etag,
                        updated_at=request.pipeline_step.audit.updated_at
                    ),
                    requester=common_v1_contact_pb2.ContactInfo(email=response_0.pipeline_run.requester.email)
                )
            )
            steps_3 = [
                partial(
                    deps.clients.labeling_labeling_task.UpdateLabelingTask,
                    outgoing_3,
                    timeout=deps.settings.timeout
                )
            ]
            results_3 = await run_steps(steps_3)
            response_3 = results_3[-1]
            returned_0_0 = response_0.result.details
            response.result.details.update(returned_0_0)
            returned_0_1 = response_0.pipeline_run.assignee.display_name
            if returned_0_1:
                response.pipeline_step.owner.display_name = returned_0_1
            returned_1_0 = response_1.breakdown.total
            if returned_1_0.ListFields():
                response.breakdown.total.MergeFrom(returned_1_0)
            returned_2_0 = response_2.label_set.manager.user_id
            if returned_2_0:
                response.pipeline_step.owner.user_id = returned_2_0
            returned_3_0 = response_3.labeling_task.customer.display_name
            if returned_3_0:
                response.pipeline_step.owner.display_name = returned_3_0
            returned_3_1 = response_3.result.correlation_id
            if returned_3_1:
                response.result.correlation_id = returned_3_1
            echoed_0 = request.pipeline_step_id
            response.pipeline_step.pipeline_step_id = echoed_0
            echoed_1 = request.pipeline_step.version
            response.pipeline_step.version = echoed_1
            return response
