"""Functional operations behind DataSchemaValidationService."""

from __future__ import annotations

from functools import partial
from typing import cast
import logging

from google.protobuf.any_pb2 import Any as AnyMessage
from google.protobuf.json_format import MessageToDict
from google.protobuf.json_format import MessageToJson
from google.protobuf.json_format import Parse
from google.protobuf.json_format import ParseDict

from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.customers.v1 import refs_pb2 as customers_v1_refs_pb2
from acme.datasets.v1 import data_schema_calculation_service_pb2 as datasets_v1_data_schema_calculation_service_pb2
from acme.datasets.v1 import data_schema_validation_service_pb2 as datasets_v1_data_schema_validation_service_pb2
from acme.datasets.v1 import dataset_validation_service_pb2 as datasets_v1_dataset_validation_service_pb2
from acme.datasets.v1 import (
    dataset_version_calculation_service_pb2 as datasets_v1_dataset_version_calculation_service_pb2,
)
from acme.datasets.v1 import datasets_pb2 as datasets_v1_datasets_pb2
from acme.featureflags.v1 import feature_flag_query_service_pb2 as featureflags_v1_feature_flag_query_service_pb2
from acme.fuel.v1 import fuel_card_service_pb2 as fuel_v1_fuel_card_service_pb2
from acme.identity.v1 import identity_pb2 as identity_v1_identity_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.identity.v1 import user_validation_service_pb2 as identity_v1_user_validation_service_pb2
from acme.lineage.v1 import lineage_edge_calculation_service_pb2 as lineage_v1_lineage_edge_calculation_service_pb2
from acme.lineage.v1 import lineage_pb2 as lineage_v1_lineage_pb2
from acme.lineage.v1 import refs_pb2 as lineage_v1_refs_pb2
from acme.modelregistry.v1 import modelregistry_pb2 as modelregistry_v1_modelregistry_pb2
from acme.modelregistry.v1 import (
    registered_model_calculation_service_pb2 as modelregistry_v1_registered_model_calculation_service_pb2,
)
from acme.pipelines.v1 import pipeline_run_calculation_service_pb2 as pipelines_v1_pipeline_run_calculation_service_pb2
from acme.pipelines.v1 import pipeline_service_pb2 as pipelines_v1_pipeline_service_pb2
from acme.pipelines.v1 import pipelines_pb2 as pipelines_v1_pipelines_pb2

from acme_data.domains.datasets.adapters import DataSchemaValidationScoreDataSchema2Adapter
from acme_data.domains.datasets.adapters import DataSchemaValidationScoreDataSchema2Port
from acme_data.domains.datasets.dependencies import Dependencies
from acme_data.domains.datasets.models import DataSchemaValidationPreviewDataSchema1Command
from acme_data.domains.datasets.models import DataSchemaValidationPreviewDataSchema2Command
from acme_data.domains.datasets.models import to_data_schema_validation_preview_data_schema1_command
from acme_data.domains.datasets.models import to_data_schema_validation_preview_data_schema2_command
from acme_data.platform.rpc import async_messages
from acme_data.platform.rpc import run_steps
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


async def handle_check_data_schema_eligibility(
    deps: Dependencies,
    request: datasets_v1_data_schema_validation_service_pb2.CheckDataSchemaEligibilityRequest
) -> datasets_v1_data_schema_validation_service_pb2.CheckDataSchemaEligibilityResponse:
    """Checks a data schema."""
    response = datasets_v1_data_schema_validation_service_pb2.CheckDataSchemaEligibilityResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('CheckDataSchemaEligibility', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'CheckDataSchemaEligibility', {'reason': request.reason})
        await deps.repository.save_data_schema(request.context.tenant_id, request.data_schema)
        response_0 = datasets_v1_dataset_version_calculation_service_pb2.CompareDatasetVersionOptionsResponse()
        response_1 = datasets_v1_dataset_validation_service_pb2.ScoreDatasetResponse()
        response_2 = datasets_v1_data_schema_calculation_service_pb2.QuoteDataSchemaResponse()
        response_3 = pipelines_v1_pipeline_run_calculation_service_pb2.EstimatePipelineRunResponse()
        outgoing_0 = datasets_v1_dataset_version_calculation_service_pb2.CompareDatasetVersionOptionsRequest(
            context=request.context,
            details=datasets_v1_dataset_version_calculation_service_pb2.CompareDatasetVersionOptionsRequest.Details(
                destination=common_v1_address_pb2.PostalAddress(
                    lines=list(request.data_schema.location.lines),
                    postal_code=request.data_schema.location.postal_code,
                    recipient=request.data_schema.location.recipient,
                    region=request.data_schema.location.region
                )
            )
        )
        response_0 = await deps.clients.datasets_dataset_version_calculation.CompareDatasetVersionOptions(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = datasets_v1_dataset_validation_service_pb2.ScoreDatasetRequest(
            context=request.context,
            dataset=datasets_v1_datasets_pb2.Dataset(
                owner=identity_v1_refs_pb2.UserRef(
                    email=response_0.dataset_version.subject.email,
                    user_id=request.data_schema.manager.user_id
                )
            ),
            details=datasets_v1_dataset_validation_service_pb2.ScoreDatasetRequest.Details(
                destination=common_v1_address_pb2.PostalAddress(country_code=request.data_schema.location.country_code)
            )
        )
        response_1 = cast(datasets_v1_dataset_validation_service_pb2.ScoreDatasetResponse, await deps.bus.request(
            'acme.datasets.v1.DataSchemaValidationService/CheckDataSchemaEligibility/1', outgoing_1, deps.settings.timeout,
        ))
        outgoing_2 = datasets_v1_data_schema_calculation_service_pb2.QuoteDataSchemaRequest(
            context=request.context,
            data_schema=datasets_v1_datasets_pb2.DataSchema(
                children=[
                    datasets_v1_datasets_pb2.DataSchema(
                        children=[
                            datasets_v1_datasets_pb2.DataSchema(
                                audit=common_v1_audit_pb2.AuditInfo(etag=response_1.dataset.audit.etag)
                            )
                        ]
                    )
                ]
            )
        )
        response_2 = await deps.clients.datasets_data_schema_calculation.QuoteDataSchema(
            outgoing_2,
            timeout=deps.settings.timeout
        )
        outgoing_3 = pipelines_v1_pipeline_run_calculation_service_pb2.EstimatePipelineRunRequest(
            context=request.context,
            pipeline_run=pipelines_v1_pipelines_pb2.PipelineRun(
                audit=common_v1_audit_pb2.AuditInfo(created_by=response_2.data_schema.audit.created_by)
            )
        )
        method_name_3 = 'EstimatePipelineRun'
        response_3 = await getattr(
            deps.clients.pipelines_pipeline_run_calculation,
            method_name_3
        )(outgoing_3, timeout=deps.settings.timeout)
        returned_0_0 = response_0.result.correlation_id
        if returned_0_0:
            response.result.correlation_id = returned_0_0
        returned_1_0 = response_1.dataset.owner.user_id
        returned_1_0_part_1 = response.data_schema.children.add()
        if returned_1_0:
            returned_1_0_part_1.manager.user_id = returned_1_0
        returned_1_1 = response_1.dataset.owner.email
        if returned_1_1:
            response.data_schema.manager.email = returned_1_1
        returned_2_0 = response_2.result.reference_ids
        response.result.reference_ids.extend(returned_2_0)
        returned_3_0 = response_3.pipeline_run.customer.display_name
        if returned_3_0:
            response.data_schema.manager.display_name = returned_3_0
        echoed_0 = request.data_schema_id
        response.data_schema.data_schema_id = echoed_0
        echoed_1 = request.data_schema.attributes
        response.data_schema.attributes.update(echoed_1)
        return response


async def handle_explain_data_schema_decision(
    deps: Dependencies,
    request: datasets_v1_data_schema_validation_service_pb2.ExplainDataSchemaDecisionRequest
) -> datasets_v1_data_schema_validation_service_pb2.ExplainDataSchemaDecisionResponse:
    """Explains a data schema."""
    response = datasets_v1_data_schema_validation_service_pb2.ExplainDataSchemaDecisionResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('ExplainDataSchemaDecision', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'ExplainDataSchemaDecision', {'reason': request.reason})
        await deps.repository.save_data_schema(request.context.tenant_id, request.data_schema)
        response_0 = pipelines_v1_pipeline_service_pb2.ClonePipelineResponse()
        response_1 = datasets_v1_dataset_version_calculation_service_pb2.ExplainDatasetVersionCalculationResponse()
        response_2 = datasets_v1_dataset_validation_service_pb2.NormalizeDatasetResponse()
        outgoing_0 = pipelines_v1_pipeline_service_pb2.ClonePipelineRequest(
            context=request.context,
            pipeline=pipelines_v1_pipelines_pb2.Pipeline(
                location=common_v1_address_pb2.PostalAddress(country_code=request.data_schema.location.country_code),
                organizer=identity_v1_refs_pb2.UserRef(email=request.data_schema.manager.email),
                participants=[
                    pipelines_v1_pipelines_pb2.PipelineParticipant(
                        contact=common_v1_contact_pb2.ContactInfo(phone=request.details.contact.phone)
                    )
                ]
            )
        )
        response_0 = await deps.clients.pipelines_pipeline.ClonePipeline(outgoing_0, timeout=deps.settings.timeout)
        outgoing_1 = datasets_v1_dataset_version_calculation_service_pb2.ExplainDatasetVersionCalculationRequest(
            context=request.context,
            dataset_version=datasets_v1_datasets_pb2.DatasetVersion(
                attributes=dict(request.data_schema.attributes),
                subject=customers_v1_refs_pb2.CustomerRef(
                    display_name=response_0.pipeline.organizer.display_name,
                    email=request.details.contact.email
                )
            ),
            details=datasets_v1_dataset_version_calculation_service_pb2.ExplainDatasetVersionCalculationRequest.Details(
                contact=common_v1_contact_pb2.ContactInfo(preferred_channel=request.details.contact.preferred_channel)
            )
        )
        document_1 = MessageToDict(outgoing_1, preserving_proto_field_name=True)
        outgoing_1 = ParseDict(
            document_1,
            datasets_v1_dataset_version_calculation_service_pb2.ExplainDatasetVersionCalculationRequest()
        )
        response_1 = await deps.clients.datasets_dataset_version_calculation.ExplainDatasetVersionCalculation(
            outgoing_1,
            timeout=deps.settings.timeout
        )
        outgoing_2 = datasets_v1_dataset_validation_service_pb2.NormalizeDatasetRequest(
            context=request.context,
            details=datasets_v1_dataset_validation_service_pb2.NormalizeDatasetRequest.Details(
                contact=common_v1_contact_pb2.ContactInfo(email=request.details.contact.email)
            )
        )
        document_2 = MessageToJson(outgoing_2, preserving_proto_field_name=True)
        outgoing_2 = Parse(document_2, datasets_v1_dataset_validation_service_pb2.NormalizeDatasetRequest())
        response_2 = await deps.clients.datasets_dataset_validation.NormalizeDataset(
            outgoing_2,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.pipeline.organizer.display_name
        if returned_0_0:
            response.data_schema.manager.display_name = returned_0_0
        returned_1_0 = response_1.result.status
        if returned_1_0:
            response.result.status = returned_1_0
        returned_2_0 = response_2.outcome.message
        if returned_2_0:
            response.outcome.message = returned_2_0
        echoed_0 = request.data_schema_id
        response.data_schema.data_schema_id = echoed_0
        echoed_1 = request.data_schema.location
        response.data_schema.location.CopyFrom(echoed_1)
        return response


async def handle_get_data_schema_rules(
    deps: Dependencies,
    request: datasets_v1_data_schema_validation_service_pb2.GetDataSchemaRulesRequest
) -> datasets_v1_data_schema_validation_service_pb2.GetDataSchemaRulesResponse:
    """Returns a data schema."""
    response = datasets_v1_data_schema_validation_service_pb2.GetDataSchemaRulesResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('GetDataSchemaRules', extra={'fields': {'domain': 'datasets'}})
        await deps.repository.audit(request.context.tenant_id, 'GetDataSchemaRules', {})
        response_0 = datasets_v1_dataset_validation_service_pb2.NormalizeDatasetResponse()
        response_1 = datasets_v1_dataset_validation_service_pb2.ValidateDatasetResponse()
        outgoing_0 = datasets_v1_dataset_validation_service_pb2.NormalizeDatasetRequest(
            context=request.context,
            dataset=datasets_v1_datasets_pb2.Dataset(
                owner=identity_v1_refs_pb2.UserRef(
                    email=request.context.actor.email,
                    user_id=request.context.actor.user_id
                )
            ),
            details=datasets_v1_dataset_validation_service_pb2.NormalizeDatasetRequest.Details(
                locale=request.context.locale
            )
        )
        response_0 = await deps.clients.datasets_dataset_validation.NormalizeDataset(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = datasets_v1_dataset_validation_service_pb2.ValidateDatasetRequest(
            context=request.context,
            dataset=datasets_v1_datasets_pb2.Dataset(
                dimensions=datasets_v1_datasets_pb2.DatasetDimensions(
                    length=response_0.dataset.dimensions.length,
                    width=response_0.dataset.dimensions.width
                )
            )
        )
        envelope_1 = AnyMessage()
        envelope_1.Pack(outgoing_1)
        outgoing_1 = datasets_v1_dataset_validation_service_pb2.ValidateDatasetRequest()
        if not envelope_1.Unpack(outgoing_1):
            raise ValueError("partner envelope contains the wrong request type")
        response_1 = await deps.clients.datasets_dataset_validation.ValidateDataset(
            outgoing_1,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.dataset.audit.created_by
        returned_0_0_part_1 = response.data_schema.children.add()
        if returned_0_0:
            returned_0_0_part_1.audit.created_by = returned_0_0
        returned_1_0 = response_1.dataset.owner.user_id
        returned_1_0_part_1 = response.data_schema.children.add()
        returned_1_0_part_2 = returned_1_0_part_1.children.add()
        if returned_1_0:
            returned_1_0_part_2.manager.user_id = returned_1_0
        echoed_0 = request.data_schema_id
        response.data_schema.data_schema_id = echoed_0
        return response


async def handle_preview_data_schema(
    deps: Dependencies,
    request: datasets_v1_data_schema_validation_service_pb2.PreviewDataSchemaRequest
) -> datasets_v1_data_schema_validation_service_pb2.PreviewDataSchemaResponse:
    """Previews a data schema."""
    response = datasets_v1_data_schema_validation_service_pb2.PreviewDataSchemaResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('PreviewDataSchema', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'PreviewDataSchema', {'reason': request.reason})
        await deps.repository.save_data_schema(request.context.tenant_id, request.data_schema)
        response_0 = identity_v1_user_validation_service_pb2.NormalizeUserResponse()
        response_1 = featureflags_v1_feature_flag_query_service_pb2.CountFeatureFlagsResponse()
        response_2 = datasets_v1_dataset_version_calculation_service_pb2.CalculateDatasetVersionResponse()
        response_3 = datasets_v1_dataset_validation_service_pb2.NormalizeDatasetResponse()
        outgoing_0 = identity_v1_user_validation_service_pb2.NormalizeUserRequest(
            context=request.context,
            user=identity_v1_identity_pb2.User(
                audit=common_v1_audit_pb2.AuditInfo(updated_at=request.data_schema.audit.updated_at)
            )
        )
        response_0 = await deps.clients.identity_user_validation.NormalizeUser(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        command_1 = DataSchemaValidationPreviewDataSchema1Command(
            context=request.context,
            filter_region=request.data_schema.location.region,
            filter_created_after=response_0.user.audit.created_at,
            filter_owner_id=request.data_schema.manager.user_id,
            filter_labels=dict(response_0.user.attributes)
        )
        outgoing_1 = to_data_schema_validation_preview_data_schema1_command(command_1)
        response_1 = await deps.clients.featureflags_feature_flag_query.CountFeatureFlags(
            outgoing_1,
            timeout=deps.settings.timeout
        )
        command_2 = DataSchemaValidationPreviewDataSchema2Command.model_validate(
            {
                'context': request.context,
                'details_destination_lines': list(request.data_schema.location.lines),
                'details_destination_locality': response_0.user.primary_address.locality,
                'details_destination_postal_code': response_0.user.primary_address.postal_code
            }
        )
        outgoing_2 = to_data_schema_validation_preview_data_schema2_command(command_2)
        response_2 = await deps.clients.datasets_dataset_version_calculation.CalculateDatasetVersion(
            outgoing_2,
            timeout=deps.settings.timeout
        )
        outgoing_3 = datasets_v1_dataset_validation_service_pb2.NormalizeDatasetRequest(
            context=request.context,
            dataset=datasets_v1_datasets_pb2.Dataset(
                address=common_v1_address_pb2.PostalAddress(lines=list(request.data_schema.location.lines)),
                audit=common_v1_audit_pb2.AuditInfo(updated_at=response_0.user.audit.updated_at),
                owner=identity_v1_refs_pb2.UserRef(display_name=response_0.user.relationship_manager.display_name)
            )
        )
        send_3 = partial(deps.clients.datasets_dataset_validation.NormalizeDataset, timeout=deps.settings.timeout)
        response_3 = await send_3(outgoing_3)
        returned_0_0 = response_0.user.contact.email
        if returned_0_0:
            response.data_schema.manager.email = returned_0_0
        returned_0_1 = response_0.user.relationship_manager.email
        returned_0_1_part_1 = response.data_schema.children.add()
        if returned_0_1:
            returned_0_1_part_1.manager.email = returned_0_1
        returned_1_0 = response_1.result.details
        response.result.details.update(returned_1_0)
        returned_2_0 = response_2.dataset_version.attributes
        response.data_schema.attributes.update(returned_2_0)
        returned_3_0 = response_3.outcome.reference_id
        if returned_3_0:
            response.outcome.reference_id = returned_3_0
        returned_3_1 = response_3.dataset.address.lines
        response.data_schema.location.lines.extend(returned_3_1)
        echoed_0 = request.data_schema_id
        response.data_schema.data_schema_id = echoed_0
        echoed_1 = request.data_schema.name
        response.data_schema.name = echoed_1
        return response


async def handle_score_data_schema(
    deps: Dependencies,
    request: datasets_v1_data_schema_validation_service_pb2.ScoreDataSchemaRequest
) -> datasets_v1_data_schema_validation_service_pb2.ScoreDataSchemaResponse:
    """Scores a data schema."""
    response = datasets_v1_data_schema_validation_service_pb2.ScoreDataSchemaResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('ScoreDataSchema', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'ScoreDataSchema', {'reason': request.reason})
        await deps.repository.save_data_schema(request.context.tenant_id, request.data_schema)
        response_0 = datasets_v1_dataset_validation_service_pb2.ExplainDatasetDecisionResponse()
        response_1 = fuel_v1_fuel_card_service_pb2.WatchFuelCardsResponse()
        response_2 = lineage_v1_lineage_edge_calculation_service_pb2.EstimateLineageEdgeResponse()
        response_3 = datasets_v1_dataset_validation_service_pb2.CheckDatasetEligibilityResponse()
        outgoing_0 = datasets_v1_dataset_validation_service_pb2.ExplainDatasetDecisionRequest(
            context=request.context,
            dataset=datasets_v1_datasets_pb2.Dataset(
                address=common_v1_address_pb2.PostalAddress(region=request.details.destination.region),
                owner=identity_v1_refs_pb2.UserRef(user_id=request.data_schema.manager.user_id)
            )
        )
        response_0 = await deps.clients.datasets_dataset_validation.ExplainDatasetDecision(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        outgoing_1 = fuel_v1_fuel_card_service_pb2.WatchFuelCardsRequest(
            context=request.context,
            subscriber=common_v1_contact_pb2.ContactInfo(email=request.data_schema.manager.email)
        )
        async for chunk_1 in deps.clients.fuel_fuel_card.WatchFuelCards(outgoing_1, timeout=deps.settings.timeout):
            response_1 = chunk_1
        outgoing_2 = lineage_v1_lineage_edge_calculation_service_pb2.EstimateLineageEdgeRequest(
            context=request.context,
            lineage_edge=lineage_v1_lineage_pb2.LineageEdge(
                subject=lineage_v1_refs_pb2.ImpactRef(display_name=request.data_schema.manager.display_name)
            )
        )
        port_2: DataSchemaValidationScoreDataSchema2Port = DataSchemaValidationScoreDataSchema2Adapter(
            deps.clients.lineage_lineage_edge_calculation,
            deps.settings.timeout
        )
        response_2 = await port_2.execute(outgoing_2)
        outgoing_3 = datasets_v1_dataset_validation_service_pb2.CheckDatasetEligibilityRequest(
            context=request.context,
            dataset=datasets_v1_datasets_pb2.Dataset(
                address=common_v1_address_pb2.PostalAddress(region=response_0.dataset.address.region),
                components={
                    'primary': datasets_v1_datasets_pb2.DatasetComponent(
                        quantity=response_0.dataset.components.get(
                            'primary',
                            datasets_v1_datasets_pb2.DatasetComponent()
                        ).quantity
                    )
                }
            )
        )
        steps_3 = [
            partial(
                deps.clients.datasets_dataset_validation.CheckDatasetEligibility,
                outgoing_3,
                timeout=deps.settings.timeout
            )
        ]
        results_3 = await run_steps(steps_3)
        response_3 = results_3[-1]
        returned_0_0 = response_0.dataset.audit.etag
        returned_0_0_part_1 = response.data_schema.children.add()
        if returned_0_0:
            returned_0_0_part_1.audit.etag = returned_0_0
        returned_0_1 = response_0.dataset.audit.etag
        if returned_0_1:
            response.data_schema.audit.etag = returned_0_1
        returned_2_0 = response_2.lineage_edge.subject.display_name
        if returned_2_0:
            response.data_schema.manager.display_name = returned_2_0
        returned_2_1 = response_2.lineage_edge.attributes
        response.data_schema.attributes.update(returned_2_1)
        returned_3_0 = response_3.dataset.owner.display_name
        returned_3_0_part_1 = response.data_schema.children.add()
        if returned_3_0:
            returned_3_0_part_1.manager.display_name = returned_3_0
        returned_3_1 = response_3.dataset.address.lines
        returned_3_1_part_1 = response.data_schema.children.add()
        returned_3_1_part_1.location.lines.extend(returned_3_1)
        echoed_0 = request.data_schema_id
        response.data_schema.data_schema_id = echoed_0
        echoed_1 = request.data_schema.name
        response.data_schema.name = echoed_1
        return response


async def handle_validate_data_schema(
    deps: Dependencies,
    request: datasets_v1_data_schema_validation_service_pb2.ValidateDataSchemaRequest
) -> datasets_v1_data_schema_validation_service_pb2.ValidateDataSchemaResponse:
    """Validates a data schema."""
    response = datasets_v1_data_schema_validation_service_pb2.ValidateDataSchemaResponse()
    with tenant_scope(request.context.tenant_id):
        log.info('ValidateDataSchema', extra={'fields': {'reason': request.reason}})
        await deps.repository.audit(request.context.tenant_id, 'ValidateDataSchema', {'reason': request.reason})
        await deps.repository.save_data_schema(request.context.tenant_id, request.data_schema)
        response_0 = modelregistry_v1_registered_model_calculation_service_pb2.SimulateRegisteredModelResponse()
        outgoing_0 = modelregistry_v1_registered_model_calculation_service_pb2.SimulateRegisteredModelRequest(
            context=request.context,
            details=modelregistry_v1_registered_model_calculation_service_pb2.SimulateRegisteredModelRequest.Details(
                destination=common_v1_address_pb2.PostalAddress(
                    country_code=request.data_schema.location.country_code,
                    region=request.data_schema.location.region
                )
            ),
            registered_model=modelregistry_v1_modelregistry_pb2.RegisteredModel(
                audit=common_v1_audit_pb2.AuditInfo(etag=request.data_schema.audit.etag)
            )
        )
        response_0 = await deps.clients.modelregistry_registered_model_calculation.SimulateRegisteredModel(
            outgoing_0,
            timeout=deps.settings.timeout
        )
        returned_0_0 = response_0.registered_model.address.recipient
        returned_0_0_part_1 = response.data_schema.children.add()
        if returned_0_0:
            returned_0_0_part_1.location.recipient = returned_0_0
        echoed_0 = request.data_schema_id
        response.data_schema.data_schema_id = echoed_0
        echoed_1 = request.data_schema.parent_id
        response.data_schema.parent_id = echoed_1
        return response
