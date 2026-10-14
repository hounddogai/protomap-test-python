"""Reusable transport mixin for PipelineQueryService."""

from __future__ import annotations

from collections.abc import AsyncIterator
from functools import partial
from typing import cast
import logging

from google.protobuf.json_format import MessageToDict
from google.protobuf.json_format import ParseDict
import grpc

from acme.anomalies.v1 import detector_query_service_pb2 as anomalies_v1_detector_query_service_pb2
from acme.authorization.v1 import (
    access_policy_validation_service_pb2 as authorization_v1_access_policy_validation_service_pb2,
)
from acme.authorization.v1 import authorization_pb2 as authorization_v1_authorization_pb2
from acme.common.v1 import address_pb2 as common_v1_address_pb2
from acme.common.v1 import audit_pb2 as common_v1_audit_pb2
from acme.common.v1 import contact_pb2 as common_v1_contact_pb2
from acme.featurestore.v1 import entity_validation_service_pb2 as featurestore_v1_entity_validation_service_pb2
from acme.identity.v1 import refs_pb2 as identity_v1_refs_pb2
from acme.pipelines.v1 import pipeline_query_service_pb2 as pipelines_v1_pipeline_query_service_pb2
from acme.pipelines.v1 import pipeline_run_validation_service_pb2 as pipelines_v1_pipeline_run_validation_service_pb2
from acme.pipelines.v1 import pipeline_step_validation_service_pb2 as pipelines_v1_pipeline_step_validation_service_pb2
from acme.pipelines.v1 import pipeline_validation_service_pb2 as pipelines_v1_pipeline_validation_service_pb2
from acme.pipelines.v1 import pipelines_pb2 as pipelines_v1_pipelines_pb2
from acme.search.v1 import search_index_service_pb2 as search_v1_search_index_service_pb2

from acme_data.domains.pipelines.adapters import PipelineQueryExportPipelines0Adapter
from acme_data.domains.pipelines.adapters import PipelineQueryExportPipelines0Port
from acme_data.domains.pipelines.dependencies import Dependencies
from acme_data.platform.rpc import messages
from acme_data.platform.rpc import retry_transient
from acme_data.platform.rpc import rpc_errors
from acme_data.platform.rpc import run_steps
from acme_data.platform.rpc import stream_errors
from acme_data.platform.tenancy import tenant_id
from acme_data.platform.tenancy import tenant_scope


log = logging.getLogger(__name__)


class PipelineQueryServicerHandlers:
    def __init__(self, deps: Dependencies) -> None:
        self.deps = deps

    @rpc_errors
    @retry_transient
    async def BrowsePipelines(
        self, request: pipelines_v1_pipeline_query_service_pb2.BrowsePipelinesRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_query_service_pb2.BrowsePipelinesResponse:
        """Lists pipelines a page at a time."""
        return await self.handle_browse_pipelines(request)

    @rpc_errors
    @retry_transient
    async def CountPipelines(
        self, request: pipelines_v1_pipeline_query_service_pb2.CountPipelinesRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_query_service_pb2.CountPipelinesResponse:
        """Counts pipelines by status."""
        return await self.handle_count_pipelines(request)

    @stream_errors
    async def ExportPipelines(
        self, request: pipelines_v1_pipeline_query_service_pb2.ExportPipelinesRequest, context: grpc.aio.ServicerContext,
    ) -> AsyncIterator[pipelines_v1_pipeline_query_service_pb2.ExportPipelinesResponse]:
        """Streams every matching pipeline."""
        response = await self.handle_export_pipelines(request)
        for item in messages((response,)):
            yield item

    @rpc_errors
    @retry_transient
    async def FindPipelines(
        self, request: pipelines_v1_pipeline_query_service_pb2.FindPipelinesRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_query_service_pb2.FindPipelinesResponse:
        """Lists pipelines a page at a time."""
        return await self.handle_find_pipelines(request)

    @rpc_errors
    @retry_transient
    async def LookupPipeline(
        self, request: pipelines_v1_pipeline_query_service_pb2.LookupPipelineRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_query_service_pb2.LookupPipelineResponse:
        """Returns a pipeline."""
        return await self.handle_lookup_pipeline(request)

    @rpc_errors
    @retry_transient
    async def PeekPipeline(
        self, request: pipelines_v1_pipeline_query_service_pb2.PeekPipelineRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_query_service_pb2.PeekPipelineResponse:
        """Returns a pipeline."""
        return await self.handle_peek_pipeline(request)

    @rpc_errors
    @retry_transient
    async def ResolvePipelines(
        self, request: pipelines_v1_pipeline_query_service_pb2.ResolvePipelinesRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_query_service_pb2.ResolvePipelinesResponse:
        """Returns several pipelines at once."""
        return await self.handle_resolve_pipelines(request)

    @rpc_errors
    @retry_transient
    async def SuggestPipelines(
        self, request: pipelines_v1_pipeline_query_service_pb2.SuggestPipelinesRequest, context: grpc.aio.ServicerContext,
    ) -> pipelines_v1_pipeline_query_service_pb2.SuggestPipelinesResponse:
        """Lists pipelines a page at a time."""
        return await self.handle_suggest_pipelines(request)

    async def handle_browse_pipelines(
        self,
        request: pipelines_v1_pipeline_query_service_pb2.BrowsePipelinesRequest
    ) -> pipelines_v1_pipeline_query_service_pb2.BrowsePipelinesResponse:
        """Lists pipelines a page at a time."""
        deps = self.deps
        response = pipelines_v1_pipeline_query_service_pb2.BrowsePipelinesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('BrowsePipelines', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(request.context.tenant_id, 'BrowsePipelines', {'order_by': request.order_by})
            response_0 = pipelines_v1_pipeline_run_validation_service_pb2.PreviewPipelineRunResponse()
            outgoing_0 = pipelines_v1_pipeline_run_validation_service_pb2.PreviewPipelineRunRequest(
                context=request.context,
                details=pipelines_v1_pipeline_run_validation_service_pb2.PreviewPipelineRunRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(email=request.context.actor.email),
                    locale=request.context.locale
                ),
                pipeline_run=pipelines_v1_pipelines_pb2.PipelineRun(
                    assignee=identity_v1_refs_pb2.UserRef(user_id=request.context.actor.user_id),
                    history=[
                        pipelines_v1_pipelines_pb2.PipelineRunStatusChange(changed_at=request.filter.created_after)
                    ]
                )
            )
            response_0 = await deps.clients.pipelines_pipeline_run_validation.PreviewPipelineRun(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.pipeline_run.audit.etag
            returned_0_0_part_0 = response.pipelines.add()
            if returned_0_0:
                returned_0_0_part_0.audit.etag = returned_0_0
            return response

    async def handle_count_pipelines(
        self,
        request: pipelines_v1_pipeline_query_service_pb2.CountPipelinesRequest
    ) -> pipelines_v1_pipeline_query_service_pb2.CountPipelinesResponse:
        """Counts pipelines by status."""
        deps = self.deps
        response = pipelines_v1_pipeline_query_service_pb2.CountPipelinesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('CountPipelines', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(request.context.tenant_id, 'CountPipelines', {'order_by': request.order_by})
            response_0 = pipelines_v1_pipeline_validation_service_pb2.ScorePipelineResponse()
            response_1 = pipelines_v1_pipeline_step_validation_service_pb2.ScorePipelineStepResponse()
            outgoing_0 = pipelines_v1_pipeline_validation_service_pb2.ScorePipelineRequest(
                context=request.context,
                pipeline=pipelines_v1_pipelines_pb2.Pipeline(
                    location=common_v1_address_pb2.PostalAddress(region=request.filter.region)
                )
            )
            response_0 = await deps.clients.pipelines_pipeline_validation.ScorePipeline(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = pipelines_v1_pipeline_step_validation_service_pb2.ScorePipelineStepRequest()
            outgoing_1.context.CopyFrom(request.context)
            outgoing_1.pipeline_step.audit.updated_at.CopyFrom(response_0.pipeline.audit.updated_at)
            outgoing_1.pipeline_step.audit.created_by = response_0.pipeline.audit.created_by
            outgoing_1.details.destination.region = request.filter.region
            outgoing_1.pipeline_step.owner.user_id = response_0.pipeline.organizer.user_id
            outgoing_1.context.tenant_id = tenant_id.get()
            response_1 = await deps.clients.pipelines_pipeline_step_validation.ScorePipelineStep(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.correlation_id
            if returned_0_0:
                response.result.correlation_id = returned_0_0
            returned_1_0 = response_1.result.status
            if returned_1_0:
                response.result.status = returned_1_0
            return response

    async def handle_export_pipelines(
        self,
        request: pipelines_v1_pipeline_query_service_pb2.ExportPipelinesRequest
    ) -> pipelines_v1_pipeline_query_service_pb2.ExportPipelinesResponse:
        """Streams every matching pipeline."""
        deps = self.deps
        response = pipelines_v1_pipeline_query_service_pb2.ExportPipelinesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ExportPipelines', extra={'fields': {'destination_uri': request.destination_uri}})
            await deps.repository.audit(
                request.context.tenant_id,
                'ExportPipelines',
                {'destination_uri': request.destination_uri}
            )
            response_0 = authorization_v1_access_policy_validation_service_pb2.NormalizeAccessPolicyResponse()
            response_1 = pipelines_v1_pipeline_step_validation_service_pb2.NormalizePipelineStepResponse()
            outgoing_0 = authorization_v1_access_policy_validation_service_pb2.NormalizeAccessPolicyRequest(
                access_policy=authorization_v1_authorization_pb2.AccessPolicy(
                    owner=identity_v1_refs_pb2.UserRef(user_id=request.context.actor.user_id)
                ),
                context=request.context
            )
            port_0: PipelineQueryExportPipelines0Port = PipelineQueryExportPipelines0Adapter(
                deps.clients.authorization_access_policy_validation,
                deps.settings.timeout
            )
            response_0 = await port_0.execute(outgoing_0)
            outgoing_1 = pipelines_v1_pipeline_step_validation_service_pb2.NormalizePipelineStepRequest(
                context=request.context,
                pipeline_step=pipelines_v1_pipelines_pb2.PipelineStep(
                    audit=common_v1_audit_pb2.AuditInfo(
                        created_at=response_0.access_policy.audit.created_at,
                        updated_at=response_0.access_policy.audit.updated_at
                    )
                )
            )
            steps_1 = [
                partial(
                    deps.clients.pipelines_pipeline_step_validation.NormalizePipelineStep,
                    outgoing_1,
                    timeout=deps.settings.timeout
                )
            ]
            results_1 = await run_steps(steps_1)
            response_1 = results_1[-1]
            returned_0_0 = response_0.access_policy.audit.created_at
            if returned_0_0.ListFields():
                response.pipeline.audit.created_at.MergeFrom(returned_0_0)
            returned_1_0 = response_1.outcome.message
            if returned_1_0:
                response.result.message = returned_1_0
            echoed_0 = request.filter.region
            response.pipeline.location.region = echoed_0
            return response

    async def handle_find_pipelines(
        self,
        request: pipelines_v1_pipeline_query_service_pb2.FindPipelinesRequest
    ) -> pipelines_v1_pipeline_query_service_pb2.FindPipelinesResponse:
        """Lists pipelines a page at a time."""
        deps = self.deps
        response = pipelines_v1_pipeline_query_service_pb2.FindPipelinesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('FindPipelines', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(request.context.tenant_id, 'FindPipelines', {'order_by': request.order_by})
            response_0 = pipelines_v1_pipeline_validation_service_pb2.CheckPipelineEligibilityResponse()
            response_1 = pipelines_v1_pipeline_validation_service_pb2.ValidatePipelineResponse()
            outgoing_0 = pipelines_v1_pipeline_validation_service_pb2.CheckPipelineEligibilityRequest(
                context=request.context,
                pipeline=pipelines_v1_pipelines_pb2.Pipeline(
                    location=common_v1_address_pb2.PostalAddress(region=request.filter.region)
                )
            )
            response_0 = await deps.clients.pipelines_pipeline_validation.CheckPipelineEligibility(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = pipelines_v1_pipeline_validation_service_pb2.ValidatePipelineRequest(
                context=request.context,
                pipeline=pipelines_v1_pipelines_pb2.Pipeline(
                    audit=common_v1_audit_pb2.AuditInfo(updated_at=response_0.pipeline.audit.updated_at)
                )
            )
            response_1 = cast(pipelines_v1_pipeline_validation_service_pb2.ValidatePipelineResponse, await deps.bus.request(
                'acme.pipelines.v1.PipelineQueryService/FindPipelines/1', outgoing_1, deps.settings.timeout,
            ))
            returned_0_0 = response_0.pipeline.location.region
            returned_0_0_part_0 = response.pipelines.add()
            if returned_0_0:
                returned_0_0_part_0.location.region = returned_0_0
            returned_1_0 = response_1.pipeline.audit.created_by
            returned_1_0_part_0 = response.pipelines.add()
            if returned_1_0:
                returned_1_0_part_0.audit.created_by = returned_1_0
            return response

    async def handle_lookup_pipeline(
        self,
        request: pipelines_v1_pipeline_query_service_pb2.LookupPipelineRequest
    ) -> pipelines_v1_pipeline_query_service_pb2.LookupPipelineResponse:
        """Returns a pipeline."""
        deps = self.deps
        response = pipelines_v1_pipeline_query_service_pb2.LookupPipelineResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('LookupPipeline', extra={'fields': {'domain': 'pipelines'}})
            await deps.repository.audit(request.context.tenant_id, 'LookupPipeline', {})
            response_0 = authorization_v1_access_policy_validation_service_pb2.ExplainAccessPolicyDecisionResponse()
            response_1 = anomalies_v1_detector_query_service_pb2.FindDetectorsResponse()
            outgoing_0 = authorization_v1_access_policy_validation_service_pb2.ExplainAccessPolicyDecisionRequest(
                access_policy=authorization_v1_authorization_pb2.AccessPolicy(
                    owner=identity_v1_refs_pb2.UserRef(email=request.context.actor.email)
                ),
                context=request.context
            )
            response_0 = await deps.clients.authorization_access_policy_validation.ExplainAccessPolicyDecision(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = anomalies_v1_detector_query_service_pb2.FindDetectorsRequest(
                context=request.context,
                filter=anomalies_v1_detector_query_service_pb2.FindDetectorsRequest.Filter(
                    created_after=response_0.access_policy.audit.updated_at
                )
            )
            method_name_1 = 'FindDetectors'
            response_1 = await getattr(
                deps.clients.anomalies_detector_query,
                method_name_1
            )(outgoing_1, timeout=deps.settings.timeout)
            returned_0_0 = response_0.result.message
            if returned_0_0:
                response.result.message = returned_0_0
            returned_1_0 = response_1.result.reference_ids
            response.result.reference_ids.extend(returned_1_0)
            echoed_0 = request.pipeline_id
            response.pipeline.pipeline_id = echoed_0
            return response

    async def handle_peek_pipeline(
        self,
        request: pipelines_v1_pipeline_query_service_pb2.PeekPipelineRequest
    ) -> pipelines_v1_pipeline_query_service_pb2.PeekPipelineResponse:
        """Returns a pipeline."""
        deps = self.deps
        response = pipelines_v1_pipeline_query_service_pb2.PeekPipelineResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('PeekPipeline', extra={'fields': {'locale': request.context.locale}})
            await deps.repository.audit(request.context.tenant_id, 'PeekPipeline', {'locale': request.context.locale})
            echoed_0 = request.pipeline_id
            response.pipeline.pipeline_id = echoed_0
            return response

    async def handle_resolve_pipelines(
        self,
        request: pipelines_v1_pipeline_query_service_pb2.ResolvePipelinesRequest
    ) -> pipelines_v1_pipeline_query_service_pb2.ResolvePipelinesResponse:
        """Returns several pipelines at once."""
        deps = self.deps
        response = pipelines_v1_pipeline_query_service_pb2.ResolvePipelinesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('ResolvePipelines', extra={'fields': {'domain': 'pipelines'}})
            await deps.repository.audit(request.context.tenant_id, 'ResolvePipelines', {})
            response_0 = pipelines_v1_pipeline_step_validation_service_pb2.ExplainPipelineStepDecisionResponse()
            response_1 = search_v1_search_index_service_pb2.BatchGetSearchIndexesResponse()
            outgoing_0 = pipelines_v1_pipeline_step_validation_service_pb2.ExplainPipelineStepDecisionRequest(
                context=request.context,
                details=pipelines_v1_pipeline_step_validation_service_pb2.ExplainPipelineStepDecisionRequest.Details(
                    locale=request.context.locale
                )
            )
            response_0 = await deps.clients.pipelines_pipeline_step_validation.ExplainPipelineStepDecision(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = search_v1_search_index_service_pb2.BatchGetSearchIndexesRequest(context=request.context)
            document_1 = MessageToDict(outgoing_1, preserving_proto_field_name=True)
            outgoing_1 = ParseDict(document_1, search_v1_search_index_service_pb2.BatchGetSearchIndexesRequest())
            response_1 = await deps.clients.search_search_index.BatchGetSearchIndexes(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.pipeline_step.owner.email
            returned_0_0_part_0 = response.pipelines.add()
            returned_0_0_part_1 = returned_0_0_part_0.participants.add()
            if returned_0_0:
                returned_0_0_part_1.contact.email = returned_0_0
            returned_0_1 = response_0.outcome.status
            if returned_0_1:
                response.result.status = returned_0_1
            returned_1_0 = response_1.result.reference_ids
            response.result.reference_ids.extend(returned_1_0)
            returned_1_1 = response_1.result.details
            response.result.details.update(returned_1_1)
            return response

    async def handle_suggest_pipelines(
        self,
        request: pipelines_v1_pipeline_query_service_pb2.SuggestPipelinesRequest
    ) -> pipelines_v1_pipeline_query_service_pb2.SuggestPipelinesResponse:
        """Lists pipelines a page at a time."""
        deps = self.deps
        response = pipelines_v1_pipeline_query_service_pb2.SuggestPipelinesResponse()
        with tenant_scope(request.context.tenant_id):
            log.info('SuggestPipelines', extra={'fields': {'order_by': request.order_by}})
            await deps.repository.audit(request.context.tenant_id, 'SuggestPipelines', {'order_by': request.order_by})
            response_0 = pipelines_v1_pipeline_validation_service_pb2.NormalizePipelineResponse()
            response_1 = featurestore_v1_entity_validation_service_pb2.NormalizeEntityResponse()
            outgoing_0 = pipelines_v1_pipeline_validation_service_pb2.NormalizePipelineRequest(
                context=request.context,
                details=pipelines_v1_pipeline_validation_service_pb2.NormalizePipelineRequest.Details(
                    contact=common_v1_contact_pb2.ContactInfo(email=request.context.actor.email)
                ),
                pipeline=pipelines_v1_pipelines_pb2.Pipeline(
                    location=common_v1_address_pb2.PostalAddress(region=request.filter.region),
                    organizer=identity_v1_refs_pb2.UserRef(user_id=request.context.actor.user_id)
                )
            )
            response_0 = await deps.clients.pipelines_pipeline_validation.NormalizePipeline(
                outgoing_0,
                timeout=deps.settings.timeout
            )
            outgoing_1 = featurestore_v1_entity_validation_service_pb2.NormalizeEntityRequest()
            outgoing_1.context.CopyFrom(request.context)
            outgoing_1.entity.primary_address.lines.extend(list(response_0.pipeline.location.lines))
            outgoing_1.entity.primary_address.recipient = response_0.pipeline.location.recipient
            merged_1 = featurestore_v1_entity_validation_service_pb2.NormalizeEntityRequest()
            merged_1.MergeFrom(outgoing_1)
            outgoing_1.CopyFrom(merged_1)
            response_1 = await deps.clients.featurestore_entity_validation.NormalizeEntity(
                outgoing_1,
                timeout=deps.settings.timeout
            )
            returned_0_0 = response_0.result.status
            if returned_0_0:
                response.result.status = returned_0_0
            returned_1_0 = response_1.entity.audit.updated_by
            returned_1_0_part_0 = response.pipelines.add()
            if returned_1_0:
                returned_1_0_part_0.audit.updated_by = returned_1_0
            return response
